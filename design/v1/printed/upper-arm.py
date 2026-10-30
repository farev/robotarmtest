"""Upper arm (link 2): shoulder hub on 2 x 608, C-channel beam to the elbow boss that clamps the
dead 8 mm elbow shaft, and the rear motor pack that carries the J2 motor (on the -Y wall) and the
elbow motor (on the separate pack-cover) as counterweights behind the shoulder.
UA frame: origin on the shoulder axis, x along the arm, y = world y, z up at q2 = 0.
Printed with the -Y wall on the bed (rotated +90 deg about X)."""
import math
from pathlib import Path

import numpy as np
from build123d import *

from features import export_printed, hull_sketch, circle_pts, bed_bearing_pocket
from layout import *
from style import *

HERE = Path(__file__).parent
HUB_R = HUB_OD / 2
BEAM_X0 = 28.0                       # beam flanges start in front of the pack-cover
FLANGE = 3.0                         # beam flange thickness (z) and web = the -Y wall
RIB_X = [62.0, 100.0]
WEB_HOLES = []                       # no web holes: 10-36 mm holes beside a running belt are finger traps
STOP_BOSS_D = 12.0                   # fixed stop on the forearm's left 608 inner ring
# carriage clamp screws: CARR_SCREW_DX along CARR_DIR (layout.py, matches pack-carriage); heads inside the
# pack, nuts in slots on the -Y face, so no key is needed under the 60T
CARR_SCREWS = [(INT_XZ[0] + s * CARR_SCREW_DX * CARR_DIR[0], INT_XZ[1] + s * CARR_SCREW_DX * CARR_DIR[1]) for s in (-1, 1)]
D1 = (math.cos(math.radians(J2_ANGLE)), math.sin(math.radians(J2_ANGLE)))   # stage-1 tension direction


def PXZ(y):
    """Sketch plane at world-y = y: local u -> +x, v -> +z, normal -> -y."""
    return Plane(origin=(0, y, 0), x_dir=(1, 0, 0), z_dir=(0, -1, 0))


def slab(sk, y0, y1, mode=Mode.ADD):
    """Extrude sketch `sk` (XZ coordinates) between world y0 < y1."""
    with BuildSketch(PXZ(y1)) as s:
        add(sk)
    extrude(s.sketch, amount=y1 - y0, mode=mode)


def slot_sketch(cx, cz, direction, length, width):
    ang = math.degrees(math.atan2(direction[1], direction[0]))
    with BuildSketch(mode=Mode.PRIVATE) as s:
        with Locations(Location((cx, cz), ang)):
            SlotCenterToCenter(length, width)
    return s.sketch


pack = hull_sketch(pack_points())
beam = hull_sketch(circle_pts(0, 0, HUB_R) + circle_pts(L2, 0, HUB_R))

with BuildPart() as ua:
    # -Y wall: pack outline + beam web
    slab(pack, Y_PACK_OUT, Y_PACK_IN)
    slab(beam, Y_PACK_OUT, Y_PACK_IN)
    # pack side walls up to the cover
    with BuildSketch(PXZ(Y_ELB_MOTOR_FACE)) as ring:
        add(pack)
        offset(amount=-WALL, mode=Mode.SUBTRACT)
    extrude(ring.sketch, amount=Y_ELB_MOTOR_FACE - Y_PACK_IN)
    # shoulder hub
    with Locations(Location((0, Y_PACK_OUT, 0), (-90, 0, 0))):
        Cylinder(HUB_R, Y_UA_HUB[1] - Y_PACK_OUT, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # beam flanges (top and bottom of the C-channel) and transverse ribs
    for zc in (HUB_R - FLANGE / 2, -HUB_R + FLANGE / 2):
        with Locations(((BEAM_X0 + L2) / 2, (Y_PACK_OUT + Y_UA_BEAM[1]) / 2, zc)):
            Box(L2 - BEAM_X0, Y_UA_BEAM[1] - Y_PACK_OUT, FLANGE)
    for rx in RIB_X:
        with Locations((rx, (Y_PACK_OUT + Y_UA_BEAM[1]) / 2, 0)):
            Box(WALL, Y_UA_BEAM[1] - Y_PACK_OUT, 2 * HUB_R - 0.2)
    # elbow boss
    with Locations(Location((L2, Y_PACK_OUT, 0), (-90, 0, 0))):
        Cylinder(HUB_R, Y_UA_BEAM[1] - Y_PACK_OUT, align=(Align.CENTER, Align.CENTER, Align.MIN))
    with Locations(Location((L2, Y_UA_BEAM[1], 0), (-90, 0, 0))):
        Cylinder(STOP_BOSS_D / 2, FA_Y[0] - Y_UA_BEAM[1], align=(Align.CENTER, Align.CENTER, Align.MIN))
    # cover-insert bosses: vertices of the pack outline inset by e, kept where the whole boss (+0.5) clears both
    # motor bodies over their slot travel, the hub and the plug notches; at least 25 mm apart
    # four in the motor-square corners of the outline (the motors' 5 mm corner chamfers leave room), one on the
    # long rear-left edge between the motors, set in along that edge's inward normal
    h = NEMA_FACE / 2 + PACK_GROW
    e = WALL + M3_BOSS / 2 - 1.0
    BOSSES = [(J2_XZ[0] - h + e, J2_XZ[1] - h - CONN_OUT + e), (J2_XZ[0] + h - e, J2_XZ[1] - h - CONN_OUT + e),
              (ELB_MOTOR_XZ[0] - h + e, ELB_MOTOR_XZ[1] + h + CONN_OUT - e),
              (ELB_MOTOR_XZ[0] + h - e, ELB_MOTOR_XZ[1] + h + CONN_OUT - e)]
    a = (ELB_MOTOR_XZ[0] - h, ELB_MOTOR_XZ[1] - h)                 # rear-left edge: elbow motor corner ...
    b = (J2_XZ[0] - h, J2_XZ[1] - h - CONN_OUT)                    # ... to J2 motor corner
    zc = -24.0                                                     # below the carriage (|z| <= 11.5 + travel)
    t = (a[1] - zc) / (a[1] - b[1])
    px, pz = a[0] + t * (b[0] - a[0]), zc
    dx, dz = b[0] - a[0], b[1] - a[1]
    nx, nz = -dz / math.hypot(dx, dz), dx / math.hypot(dx, dz)      # left normal of a->b
    if nx < 0:
        nx, nz = -nx, -nz                                          # point into the pack (+x side)
    ee = WALL + M3_BOSS / 2 + 0.5
    BOSSES.append((px + ee * nx, pz + ee * nz))
    with Locations(*[(px, (Y_PACK_IN + Y_ELB_MOTOR_FACE) / 2, pz) for px, pz in BOSSES]):
        Box(M3_BOSS, Y_ELB_MOTOR_FACE - Y_PACK_IN, M3_BOSS)
    # ---- cuts
    # bearing pockets (608 press, rules §1) at both hub ends, rod clearance between
    # bed-side pocket: ledge (608 outer ring ID ~19 [est]) + 45 deg cone so the ceiling prints
    add(bed_bearing_pocket(FIT_608, W608, 19.0, ROD8_CLEAR).rotate(Axis.X, -90).moved(Location((0, Y_PACK_OUT, 0))),
        mode=Mode.SUBTRACT)
    with Locations(Location((0, Y_UA_HUB[1] - W608, 0), (-90, 0, 0))):
        Cylinder(FIT_608 / 2, W608, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
    with Locations(Location((0, 0, 0), (-90, 0, 0))):
        Cylinder(ROD8_CLEAR / 2, 400, mode=Mode.SUBTRACT)
    # elbow rod: snug 8.2 (rules §1), located by collars on both sides
    with Locations(Location((L2, 0, 0), (-90, 0, 0))):
        Cylinder(ROD8_CLAMP / 2, 400, mode=Mode.SUBTRACT)
    # web lightening holes
    for hx, hr in WEB_HOLES:
        with Locations(Location((hx, 0, 0), (-90, 0, 0))):
            Cylinder(hr, 400, mode=Mode.SUBTRACT)
    # J2 motor: pilot slot and M3 slots along the stage-1 line (tension away from the 60T)
    with BuildSketch(PXZ(Y_PACK_IN)) as cuts:
        add(slot_sketch(J2_XZ[0], J2_XZ[1], D1, 2 * SLOT, PILOT_CLEAR))
        for sx in (-1, 1):
            for sz in (-1, 1):
                add(slot_sketch(J2_XZ[0] + sx * NEMA_PITCH / 2, J2_XZ[1] + sz * NEMA_PITCH / 2, D1, 2 * SLOT, M3_CLEAR))
        # intermediate shaft slot and carriage clamp slots (carriage slides along CARR_DIR)
        add(slot_sketch(INT_XZ[0], INT_XZ[1], CARR_DIR, 2 * SLOT, 6.0))
        for cx, cz in CARR_SCREWS:
            add(slot_sketch(cx, cz, CARR_DIR, 2 * SLOT, M3_CLEAR))
    extrude(cuts.sketch, amount=WALL_T + 1, mode=Mode.SUBTRACT)
    # captive-nut slots on the -Y face for the carriage screws (nut slides with the carriage, rules §2:
    # across flats + 0.3, depth = nut height + 0.3); 6 mm bridge over each as printed (summary.md)
    # slot width = nut across flats + 0.3 (rules §2 side-entry slot): the flats bear on the slot sides so the
    # nut cannot turn while the screw is tightened from inside the pack (review 2, blocking 1)
    nut_w, nut_d = 5.5 + 0.3, M3_NUT[1]
    with BuildSketch(PXZ(Y_PACK_OUT + nut_d)) as nuts:
        for cx, cz in CARR_SCREWS:
            add(slot_sketch(cx, cz, CARR_DIR, 2 * SLOT, nut_w))
    extrude(nuts.sketch, amount=nut_d + 1, mode=Mode.SUBTRACT)
    # cover inserts from the top edge
    with Locations(*[Location((px, Y_ELB_MOTOR_FACE, pz), (90, 0, 0)) for px, pz in BOSSES]):
        Cylinder(M3_INSERT[0] / 2, 2 * M3_INSERT[1], mode=Mode.SUBTRACT)
    # cable notches in the top edge of the pack walls (closed by the cover): J2 plug (down), elbow plug (up)
    # plug sits 32.5 from each motor face: J2 face at Y_PACK_IN (body +Y), elbow face at Y_ELB_MOTOR_FACE (body -Y)
    for (cx, cz), sgn, y_plug in ((J2_XZ, -1, Y_PACK_IN + 32.5), (ELB_MOTOR_XZ, 1, Y_ELB_MOTOR_FACE - 32.5)):
        zc = cz + sgn * (NEMA_FACE / 2 + PACK_GROW + CONN_OUT)
        depth = Y_ELB_MOTOR_FACE - (y_plug - 6.0)
        with Locations((cx, Y_ELB_MOTOR_FACE - depth / 2, zc)):
            Box(20, depth, 4 * WALL, mode=Mode.SUBTRACT)

part = ua.part
p = export_printed(part, "upper-arm", rot=(90, 0, 0), here=HERE)
print("cover bosses (x, z):", [(round(a, 1), round(b, 1)) for a, b in BOSSES])
import json
(HERE / "upper-arm.bosses.json").write_text(json.dumps([[float(a), float(b)] for a, b in BOSSES]))
print("volume cm3", round(part.volume / 1000, 1))
