"""Static gravity torque per joint from the CAD (worst case: arm stretched horizontally).

Masses: printed parts = solid volume x density x FILL (4 walls + 20 % infill [est]); bought parts
from catalogue values (layout notes). Payload 100 g at the pad centre [assumed].
python design/v1/torque_check.py
"""
import sys
from pathlib import Path

import numpy as np
import yaml
from build123d import import_step

HERE = Path(__file__).parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE / "printed"))
sys.path.insert(0, str(HERE))
from layout import *                 # noqa: E402
import gripper_layout as G           # noqa: E402
from make_assembly import build, frames   # noqa: E402

HERE = Path(__file__).parent
FILL = 0.45                          # [est] solid fraction of a 4-wall, 20 % gyroid print
DENS = {"PLA": 1.24e-3, "PETG": 1.27e-3}      # g/mm^3
BOUGHT_G = {"nema17": 280, "608": 12, "625": 5, "6806": 26, "gt2-20t": 8, "gt2-60t": 25, "rod-8x100": 39,
            "rod-8x113": 45, "rod-5x52": 8, "collar": 10, "coupling": 12, "mg90s": 13.4, "belt": 3}
PAYLOAD_G = 100.0
TORQUE_HOLD = 0.34                   # N m, lower sibling value (unverified for 42SHDC3026-15B)
USABLE = 0.5                         # size steppers at <= 50 % of holding torque (controls ref. rule 8)
ETA = {"J2": 0.95 * 0.95, "J3": 0.95}

q = (0, 0, 0, 0)                     # stretched horizontally: worst gravity case for J2 and J3
asm = build(q)
asm["parts"] = [p for p in asm["parts"] if not p["id"].startswith("screw")]   # screws: < 30 g, not weighed
F = frames(q)
items = []
for p in asm["parts"]:
    if p["id"].endswith("keepout"):
        continue
    model = p["model"]
    s = import_step(str(ROOT / model))
    from build123d import Location, Rotation, Extrinsic
    loc = Location(tuple(p["position"])) * Rotation(*p["rotation"], ordering=Extrinsic.XYZ)
    s = s.moved(loc)
    com = s.center()
    if p["kind"] == "printed":
        g = s.volume * DENS.get(p.get("material", "PLA"), 1.24e-3) * FILL
    else:
        key = next((k for k in BOUGHT_G if k in model), None)
        g = BOUGHT_G.get(key, 0.0) if key else 0.0
    items.append((p["id"], g, np.array([com.X, com.Y, com.Z])))

pad = F["g"] @ np.array([G.X_TIP, 0, 0, 1])
items.append(("payload", PAYLOAD_G, pad[:3]))

UA_IDS = {"upper-arm", "pack-cover", "pack-carriage", "bearing-608-sh-1", "bearing-608-sh-2", "motor-j2", "pulley-j2-20t",
          "rod-intermediate", "bearing-625-1", "bearing-625-2", "pulley-s1-60t", "pulley-s2-20t", "motor-j3", "pulley-j3-20t",
          "belt-s1", "belt-j3", "rod-elbow", "collar-elbow-in", "collar-elbow-out", "bearing-shim-3"}
FA_IDS = {"forearm", "forearm-cover", "bearing-608-el-1", "bearing-608-el-2", "motor-j4", "coupling-j4",
          "gripper-base", "gripper-finger-left", "gripper-finger-right", "servo-gripper", "payload"}
sh = np.array([0, 0, Z_SH]); el = np.array([L2, 0, Z_SH])
t2 = sum(g * (c[0] - sh[0]) for i, g, c in items if i in UA_IDS | FA_IDS) * 9.81e-6   # N m (g*mm -> kg*m)
t3 = sum(g * (c[0] - el[0]) for i, g, c in items if i in FA_IDS) * 9.81e-6
m_arm = sum(g for i, g, c in items if i in UA_IDS | FA_IDS)
m_tot = sum(g for i, g, c in items)
res = {}
for j, t, ratio, eta in (("J2", t2, J2_RATIO, ETA["J2"]), ("J3", t3, J3_RATIO, ETA["J3"])):
    t = float(t)
    motor = t / (ratio * eta)
    res[j] = {"joint_torque_Nm": round(t, 3), "ratio": ratio, "motor_torque_Nm": round(motor, 3),
              "share_of_holding": round(motor / TORQUE_HOLD, 2),
              "safety_factor_vs_50pct_rule": round(USABLE * TORQUE_HOLD / motor, 2)}
res["moving_mass_g"] = round(float(m_arm), 0)
res["total_mass_g"] = round(float(m_tot), 0)
res["assumptions"] = {"fill": FILL, "payload_g": PAYLOAD_G, "holding_Nm": TORQUE_HOLD, "pose": "stretched horizontal"}
print(yaml.safe_dump(res, sort_keys=False))
(HERE / "torque_check.yaml").write_text(yaml.safe_dump(res, sort_keys=False))
