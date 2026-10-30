"""Write design/v1/assembly.yaml (home pose) and design/v1/poses/<name>/assembly.yaml from the
shared layout, the printed parts' place.json files and the bought-part frames.

python design/v1/make_assembly.py

Frames: world (base) -> turret Rz(q1) -> UA: T(0,0,Z_SH) Ry(-q2) -> FA: T(L2,0,0) Ry(-q3)
-> G: T(COUPLING_FACE,0,0) Rx(q4). Every part is placed in one frame; joint origins are on the
joint axes so a pose only changes rotations.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
import yaml
from scipy.spatial.transform import Rotation as Rot

HERE = Path(__file__).parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE / "printed"))
from layout import *            # noqa: E402
import gripper_layout as G      # noqa: E402
from style import *             # noqa: E402
HERE = Path(__file__).parent    # re-set: layout's star import also exports a HERE
ROOT = HERE.parents[1]

# ---------------------------------------------------------------- transforms
def T(x=0.0, y=0.0, z=0.0):
    m = np.eye(4); m[:3, 3] = (x, y, z); return m


def R(axis, deg):
    m = np.eye(4); m[:3, :3] = Rot.from_euler(axis, deg, degrees=True).as_matrix(); return m


def frames(q):
    q1, q2, q3, q4 = q
    W = np.eye(4)
    TU = R("z", q1)
    UA = TU @ T(0, 0, Z_SH) @ R("y", -q2)
    FA = UA @ T(L2, 0, 0) @ R("y", -q3)
    GR = FA @ T(COUPLING_FACE, 0, 0) @ R("x", q4)
    return {"base": W, "turret": TU, "ua": UA, "fa": FA, "g": GR}


def placed(M):
    pos = [round(float(v), 4) for v in M[:3, 3]]
    rot = [round(float(v), 4) for v in Rot.from_matrix(M[:3, :3]).as_euler("xyz", degrees=True)]
    return pos, rot


def printed_local(name):
    """Inverse of the print transform: printed STEP coords -> as-assembled frame coords."""
    d = json.loads((HERE / "printed" / f"{name}.place.json").read_text())
    Rm = np.array(d["R"]); t = np.array(d["t"])
    m = np.eye(4); m[:3, :3] = Rm.T; m[:3, 3] = -Rm.T @ t
    return m


# rotations that map a bought part's +Z (shaft/axis) onto a direction
Z_TO_PY = R("x", -90)    # +Z -> +Y
Z_TO_NY = R("x", 90)     # +Z -> -Y
Z_TO_PX = R("y", 90)     # +Z -> +X
Z_TO_NZ = R("x", 180)

# ---------------------------------------------------------------- belts
def belt_step(name, c1, r1, c2, r2):
    """Closed belt (BELT_T thick, BELT_W wide) on the tooth tips of two pulleys, in the XY plane of
    its own frame (z = belt centre plane); written to parts/models/<name>.step."""
    from build123d import BuildPart, BuildSketch, Mode, Plane, add, export_step, extrude, offset
    from features import hull_sketch, circle_pts
    path = ROOT / "parts/models" / f"{name}.step"
    with BuildPart() as b:
        with BuildSketch(Plane.XY.offset(-BELT_W / 2)) as s:
            add(hull_sketch(circle_pts(*c1, r1 + BELT_T, 96) + circle_pts(*c2, r2 + BELT_T, 96)))
            add(hull_sketch(circle_pts(*c1, r1, 96) + circle_pts(*c2, r2, 96)), mode=Mode.SUBTRACT)
        extrude(s.sketch, amount=BELT_W)
    export_step(b.part, str(path))
    return f"parts/models/{name}.step"


PART_COLORS = {"printed": COLOR_MAIN, "accent": COLOR_ACCENT}
ACCENT = {"turret-hub", "shoulder-pulley-80t", "gripper-finger-left", "gripper-finger-right"}
PETG = {"base-deck", "upper-arm", "pack-cover", "forearm", "pack-carriage"}   # parts at a stepper body


def build(q, service=None):
    """service: None (normal pose), "j2" (belt-tensioning pose: J2 motor-screw key keep-outs) or
    "tower" (tower bolted to the turret before the arm goes on: no arm parts, foot-screw keep-outs)."""
    F = frames(q)
    parts = []

    def add_printed(pid, frame, name=None):
        name = name or pid
        M = F[frame] @ printed_local(name)
        pos, rot = placed(M)
        e = {"id": pid, "model": f"design/v1/printed/{name}.step", "kind": "printed", "position": pos,
             "rotation": rot, "color": COLOR_ACCENT if name in ACCENT else COLOR_MAIN, "_frame": frame}
        if name in PETG:
            e["material"] = "PETG"
        parts.append(e)

    def add_bought(pid, model, frame, local, color=COLOR_METAL):
        pos, rot = placed(F[frame] @ local)
        parts.append({"id": pid, "model": model, "kind": "bought", "position": pos, "rotation": rot, "color": color,
                      "_frame": frame})
        if model.endswith("nema17-42shdc.step"):          # every motor gets its plug + cable-bend keep-out
            parts.append({"id": f"plug-{pid}-keepout", "model": "parts/models/nema17-plug-keepout.step",
                          "kind": "bought", "position": pos, "rotation": rot, "color": "#ff00ff", "_frame": frame})

    # ---- table the base stands on (keep-out: nothing may go below z = 0)
    parts.append({"id": "table-keepout", "model": "parts/models/table-keepout.step", "kind": "bought",
                  "position": [0, 0, 0], "rotation": [0, 0, 0], "color": "#ff00ff", "_frame": "base"})
    # ---- base (world frame)
    for n in ("base-shell", "base-deck", "bearing-cap", "yaw-spacer-outer"):
        add_printed(n, "base")
    mx, my = J1_MOTOR_XY
    add_bought("motor-j1", "parts/models/nema17-42shdc.step", "base", T(mx, my, Z_DECK_BOT) @ R("z", J1_MOTOR_ROT))
    add_bought("bearing-6806-upper", "parts/models/bearing-6806.step", "base", T(0, 0, Z_B_UP_TOP - W6806 / 2))
    add_bought("bearing-6806-lower", "parts/models/bearing-6806.step", "base", T(0, 0, Z_B_LO_BOT + W6806 / 2))
    add_bought("uno-cnc-shield", "parts/models/uno-cnc-shield.step", "base", T(-107.0, -53.34 / 2, BASE_FLOOR + 6.0), COLOR_BOARD)
    # ---- turret
    for n in ("turret-hub", "yaw-spacer-inner", "turret-clamp", "shoulder-tower", "shoulder-pulley-80t"):
        add_printed(n, "turret")
    add_bought("pulley-j1-20t", "parts/models/gt2-20t-5mm.step", "base", T(mx, my, Z_J1_PUL_TOP) @ Z_TO_NZ)
    j1b = belt_step("belt-j1-gt2-300", (0, 0), od(T_YAW_BIG) / 2, (mx, my), od(T_YAW_SMALL) / 2)
    add_bought("belt-j1", j1b, "base", T(0, 0, Z_B1), COLOR_BELT)      # both pulley axes fixed in the base
    add_bought("rod-shoulder", "parts/models/rod-8x100.step", "turret", T(0, Y_TOWER[0] - 0.5, Z_SH) @ Z_TO_PY, COLOR_STEEL)
    SH = 1.2; CW = 8.0
    # shims and collars on the dead shoulder shaft (turret frame; y as in the UA frame)
    def on_shoulder(pid, model, y0, color=COLOR_STEEL, printed=False):
        M = T(0, y0, Z_SH) @ Z_TO_PY
        if printed:
            pos, rot = placed(F["turret"] @ M @ printed_local("bearing-shim"))
            parts.append({"id": pid, "model": "design/v1/printed/bearing-shim.step", "kind": "printed",
                          "position": pos, "rotation": rot, "color": COLOR_MAIN})
        else:
            pos, rot = placed(F["turret"] @ M)
            parts.append({"id": pid, "model": model, "kind": "bought", "position": pos, "rotation": rot, "color": color})
    on_shoulder("bearing-shim", None, Y_PACK_OUT - SH, printed=True)
    on_shoulder("collar-shoulder-in", "parts/models/collar-8mm.step", Y_PACK_OUT - SH - CW / 2)
    on_shoulder("bearing-shim-2", None, Y_UA_HUB[1], printed=True)
    on_shoulder("collar-shoulder-out", "parts/models/collar-8mm.step", Y_UA_HUB[1] + SH + CW / 2)
    # ---- upper arm (UA frame)
    for n in ("upper-arm", "pack-cover", "pack-carriage"):
        add_printed(n, "ua")
    add_bought("bearing-608-sh-1", "parts/models/bearing-608.step", "ua", T(0, Y_PACK_OUT + W608 / 2, 0) @ Z_TO_PY)
    add_bought("bearing-608-sh-2", "parts/models/bearing-608.step", "ua", T(0, Y_UA_HUB[1] - W608 / 2, 0) @ Z_TO_PY)
    add_bought("motor-j2", "parts/models/nema17-42shdc.step", "ua", T(J2_XZ[0], Y_PACK_IN, J2_XZ[1]) @ Z_TO_NY @ R("z", -90))
    add_bought("pulley-j2-20t", "parts/models/gt2-20t-5mm.step", "ua", T(J2_XZ[0], Y_PACK_OUT - PUL_WALL_GAP, J2_XZ[1]) @ Z_TO_NY)
    ix, iz = INT_XZ
    add_bought("rod-intermediate", "parts/models/rod-5x52.step", "ua", T(ix, Y_PACK_IN + 15.5, iz) @ Z_TO_NY, COLOR_STEEL)
    add_bought("bearing-625-1", "parts/models/bearing-625.step", "ua", T(ix, Y_PACK_IN + W625 / 2, iz) @ Z_TO_PY)
    add_bought("bearing-625-2", "parts/models/bearing-625.step", "ua", T(ix, Y_PACK_IN + 16 - W625 / 2, iz) @ Z_TO_PY)
    add_bought("pulley-s1-60t", "parts/models/gt2-60t-5mm.step", "ua", T(ix, Y_PACK_OUT - PUL_WALL_GAP, iz) @ Z_TO_NY)
    add_bought("pulley-s2-20t", "parts/models/gt2-20t-5mm.step", "ua",
               T(ix, Y_PACK_OUT - PUL_WALL_GAP - PUL_LEN - PUL_STACK_GAP, iz) @ Z_TO_NY)
    ex, ez = ELB_MOTOR_XZ
    add_bought("motor-j3", "parts/models/nema17-42shdc.step", "ua", T(ex, Y_ELB_MOTOR_FACE, ez) @ Z_TO_PY @ R("z", -90))
    add_bought("pulley-j3-20t", "parts/models/gt2-20t-5mm.step", "ua", T(ex, Y_COVER_OUT + 0.5, ez) @ Z_TO_PY)
    # belts in the UA frame: belt sketch (u, v, w) -> UA (u, -w, v) via Rx(90), so pass (x, z) centres
    BXZ = R("x", 90)
    s1 = belt_step(f"belt-s1-gt2-{S1_LOOP}", (ix, iz), od(60) / 2, J2_XZ, od(20) / 2)
    add_bought("belt-s1", s1, "ua", T(0, Y_S1, 0) @ BXZ, COLOR_BELT)
    s2 = belt_step("belt-s2-gt2-200", (0, 0), od(T_S2_BIG) / 2, (ix, iz), od(20) / 2)
    add_bought("belt-s2", s2, "ua", T(0, Y_S2, 0) @ BXZ, COLOR_BELT)
    e3 = belt_step("belt-j3-gt2-520", (L2, 0), od(T_E_BIG) / 2, (ex, ez), od(20) / 2)
    add_bought("belt-j3", e3, "ua", T(0, Y_E, 0) @ BXZ, COLOR_BELT)
    # elbow shaft, collars, shim (UA frame)
    add_bought("rod-elbow", "parts/models/rod-8x113.step", "ua", T(L2, Y_PACK_OUT - CW, 0) @ Z_TO_PY, COLOR_STEEL)
    add_bought("collar-elbow-in", "parts/models/collar-8mm.step", "ua", T(L2, Y_PACK_OUT - CW / 2, 0) @ Z_TO_PY, COLOR_STEEL)
    pos, rot = placed(F["ua"] @ T(L2, FA_HUB_HALF, 0) @ Z_TO_PY @ printed_local("bearing-shim"))
    parts.append({"id": "bearing-shim-3", "model": "design/v1/printed/bearing-shim.step", "kind": "printed",
                  "position": pos, "rotation": rot, "color": COLOR_MAIN})
    add_bought("collar-elbow-out", "parts/models/collar-8mm.step", "ua", T(L2, FA_HUB_HALF + SH + CW / 2, 0) @ Z_TO_PY, COLOR_STEEL)
    # ---- forearm (FA frame)
    for n in ("forearm", "forearm-cover"):
        add_printed(n, "fa")
    add_bought("bearing-608-el-1", "parts/models/bearing-608.step", "fa", T(0, FA_Y[0] + W608 / 2, 0) @ Z_TO_PY)
    add_bought("bearing-608-el-2", "parts/models/bearing-608.step", "fa", T(0, FA_HUB_HALF - W608 / 2, 0) @ Z_TO_PY)
    add_bought("motor-j4", "parts/models/nema17-42shdc.step", "fa", T(X_J4_FACE, 0, 0) @ Z_TO_PX @ R("z", 90))
    add_bought("hub-j4", "parts/models/flange-coupling-5mm.step", "fa", T(COUPLING_FACE, 0, 0) @ Z_TO_PX)
    # ---- screws at the joints the design review flagged, with hex-key keep-outs where tightened in place
    def screw(pid, L, frame, local, key=True, key_offset=0.0):
        """key_offset: start the key keep-out this far above the head top (screws sunk in a counterbore of the
        keep-out's own diameter start it at the counterbore mouth)."""
        add_bought(pid, f"parts/models/m3x{L}-shcs.step", frame, local, COLOR_STEEL)
        if key:
            add_bought(f"{pid}-key-keepout", "parts/models/m3-key-keepout.step", frame, local @ T(0, 0, key_offset), "#ff00ff")
    for i, (sx, sz) in enumerate([(-1, -1), (-1, 1), (1, -1), (1, 1)]):      # J2 motor: heads on the -Y face,
        screw(f"screw-j2-{i + 1}", 8, "ua",                                   # tightened in the service-j2 pose
              T(J2_XZ[0] + sx * NEMA_PITCH / 2, Y_PACK_OUT, J2_XZ[1] + sz * NEMA_PITCH / 2) @ Z_TO_NY,
              key=service == "j2")
    for i, sx in enumerate((-1, 1)):                                          # carriage clamps: heads inside the pack,
        y_head = Y_PACK_IN + 16.0 - (16.0 + WALL_T + 0.3 - 12.0)              # tightened with the pack cover off
        cx = INT_XZ[0] + sx * CARR_SCREW_DX * CARR_DIR[0]
        cz = INT_XZ[1] + sx * CARR_SCREW_DX * CARR_DIR[1]
        screw(f"screw-carriage-{i + 1}", 12, "ua", T(cx, y_head, cz) @ Z_TO_PY, key=service == "j2",
              key_offset=(Y_PACK_IN + 16.0) - (y_head + 3.0))                  # from the counterbore mouth
    for i, (fx, fy) in enumerate(TOWER_FOOT_INSERTS):                         # tower foot into turret inserts,
        screw(f"screw-tower-foot-{i + 1}", 12, "turret", T(fx, fy, Z_TUR_TOP + 6.0),   # before the arm goes on
              key=service == "tower")
    for i, (sx_, sy_) in enumerate(J1_SCREWS_XY):                             # J1 motor: M3 x 10 + 0.5 washer on the
        screw(f"screw-j1-{i + 1}", 10, "base", T(sx_, sy_, Z_DECK + 0.5),         # deck top, tightened with the belt on
              key=service == "tower")                                         # and the turret arm turned away
    screw("screw-shaft-lock", 30, "turret", T(0, (Y_TOWER[0] + Y_TOWER[1]) / 2, Z_SH + 4.0 + 30.0))   # tip on the rod top
    # ---- gripper (G frame)
    for n in ("gripper-base", "gripper-finger-left", "gripper-finger-right"):
        add_printed(n, "g")
    add_bought("servo-gripper", "parts/models/mg90s.step", "g", T(G.X_S, G.PIVOT_Y, G.Z_TAB) @ R("z", 180), "#2B2B2B")
    add_bought("servo-cable-keepout", "parts/models/mg90s-keepout.step", "g", T(G.X_S, G.PIVOT_Y, G.Z_TAB) @ R("z", 180), "#ff00ff")

    allow = [
        ["bearing-6806-upper", "base-deck"], ["bearing-6806-lower", "base-deck"],      # press fit +0.1
        ["bearing-6806-upper", "turret-hub"], ["bearing-6806-lower", "turret-hub"],    # spigot slip in the inner rings
        ["yaw-spacer-inner", "turret-hub"], ["yaw-spacer-outer", "base-deck"],         # spacer slips on spigot / in pocket
        ["pulley-j1-20t", "motor-j1"], ["pulley-j2-20t", "motor-j2"], ["pulley-j3-20t", "motor-j3"],  # pulley on shaft
        ["hub-j4", "motor-j4"],                                                         # hub on the shaft
        ["belt-j1", "pulley-j1-20t"], ["belt-j1", "turret-hub"],                        # belt wraps its pulleys
        ["belt-s1", "pulley-j2-20t"], ["belt-s1", "pulley-s1-60t"],
        ["belt-s2", "pulley-s2-20t"], ["belt-s2", "shoulder-pulley-80t"],
        ["belt-j3", "pulley-j3-20t"], ["belt-j3", "forearm"],
        ["rod-shoulder", "shoulder-tower"], ["rod-shoulder", "shoulder-pulley-80t"],    # snug 8.2 bores
        ["rod-shoulder", "bearing-608-sh-1"], ["rod-shoulder", "bearing-608-sh-2"],     # bearing on shaft
        ["rod-shoulder", "collar-shoulder-in"], ["rod-shoulder", "collar-shoulder-out"],
        ["rod-shoulder", "upper-arm"], ["rod-shoulder", "bearing-shim"], ["rod-shoulder", "bearing-shim-2"],
        ["bearing-608-sh-1", "upper-arm"], ["bearing-608-sh-2", "upper-arm"],          # press fit
        ["rod-intermediate", "bearing-625-1"], ["rod-intermediate", "bearing-625-2"],
        ["rod-intermediate", "pulley-s1-60t"], ["rod-intermediate", "pulley-s2-20t"],
        ["rod-intermediate", "upper-arm"], ["rod-intermediate", "pack-carriage"],      # passes the wall slot
        ["bearing-625-1", "pack-carriage"], ["bearing-625-2", "pack-carriage"],        # press fit
        ["rod-elbow", "upper-arm"], ["rod-elbow", "forearm"], ["rod-elbow", "collar-elbow-in"],
        ["rod-elbow", "collar-elbow-out"], ["rod-elbow", "bearing-608-el-1"], ["rod-elbow", "bearing-608-el-2"],
        ["rod-elbow", "bearing-shim-3"],
        ["bearing-608-el-1", "forearm"], ["bearing-608-el-2", "forearm"],              # press fit
        ["servo-gripper", "gripper-base"],                                              # body in the 0.3 cut-out
        ["servo-cable-keepout", "servo-gripper"],
        ["gripper-finger-left", "gripper-finger-right"],                                # gear mesh (0.1 backlash)
        ["gripper-finger-right", "gripper-base"],                                       # idler on its axle boss
        ["hub-j4", "gripper-base"],                                                     # hub face bolted to the base plate
    ]
    allow += [[f"plug-{m}-keepout", m] for m in ("motor-j1", "motor-j2", "motor-j3", "motor-j4")]  # plug on its motor
    allow += [[f"screw-j2-{i}", "motor-j2"] for i in range(1, 5)]          # screw threads into the motor's M3 hole
    allow += [[f"screw-j1-{i}", "motor-j1"] for i in range(1, 5)]
    allow += [["table-keepout", "base-shell"]]                              # the base stands on the table
    # face-clamped bolted joints (0 gap by design) show 0.03-0.06 mm3 of boolean noise in rotated poses.
    # The J4 motor's side clearance in the channel is 0.7 mm by construction (forearm.py ZW_IN).
    allow += [["shoulder-tower", "shoulder-pulley-80t"], ["forearm", "motor-j4"]]
    if service == "tower":                      # tower bolted down before the arm goes on
        parts = [p for p in parts if p.get("_frame", "ua") in ("base", "turret") and not p["id"].startswith(
            ("bearing-shim", "collar-shoulder", "rod-shoulder", "screw-shaft-lock"))]
    if service == "j2":                         # upper arm on the bench, pack cover off: stage 1 tensioned, J2 and
        parts = [p for p in parts if p.get("_frame") == "ua" and p["id"] not in (   # carriage screws reachable
            "belt-s2", "belt-j3", "pack-cover", "motor-j3", "pulley-j3-20t", "plug-motor-j3-keepout")
                 and not p["id"].startswith(("rod-elbow", "collar-elbow", "bearing-shim"))]
    ids = {p["id"] for p in parts}
    allow = [a for a in allow if a[0] in ids and a[1] in ids]
    for p in parts:
        p.pop("_frame", None)
    return {"min_clearance_mm": 0.5, "parts": parts, "allow_contact": allow}


POSES = {
    "home": ((0, 45, -90, 0), None),
    "stretched": ((0, 0, 0, 0), None),
    "up": ((0, 90, 0, 0), None),
    "folded": ((0, 90, -135, 0), None),
    "reach-table": ((0, 0, -43, 0), None),        # table limit at J2 = 0: pad centre 37 mm up, lowest pad edge ~12
    "shoulder-down": ((90, -30, 8, 0), None),     # shoulder at its lower limit, table limit (pad centre 36 up)
    "elbow-up": ((0, 30, 120, 0), None),
    "yaw-150": ((150, 45, -90, 180), None),
    "service-j2": ((0, 0, 0, 0), "j2"),           # upper arm on the bench: stage-1 tension, J2 screws from -Y
    "service-tower": ((0, 0, 0, 0), "tower"),     # tower on the turret, foot + J1 screws reachable from above
    "soft-limit": ((0, 20, -84, 0), None),        # steep reach-down at the table limit: pad centre 35.5 up, r ~ 223
}

if __name__ == "__main__":
    for name, (q, service) in POSES.items():
        asm = build(q, service)
        out = HERE / "assembly.yaml" if name == "home" else HERE / "poses" / name / "assembly.yaml"
        out.parent.mkdir(parents=True, exist_ok=True)
        hdr = f"# generated by design/v1/make_assembly.py, pose {name} q = {q}\n"
        out.write_text(hdr + yaml.safe_dump(asm, sort_keys=False, width=140))
        print("wrote", out.relative_to(ROOT), len(asm["parts"]), "parts")
