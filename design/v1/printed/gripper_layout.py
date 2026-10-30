"""Shared gripper numbers (G frame: origin at the flange-coupling face centre on the roll axis,
x forward, y left, z up at q4 = 0). MG90S dims read from parts/models/mg90s.yaml."""
import math

import yaml

from layout import ROOT

S = {d["name"]: d["value_mm"] for d in yaml.safe_load((ROOT / "parts/models/mg90s.yaml").read_text())["critical_dims"]}

GEAR_M, GEAR_Z = 2.0, 15                 # module 2 (load-bearing printed gears, machine_elements §4.1), 15 teeth
GEAR_ADD = 0.85                          # shortened addendum: ~1.5 mm tip land, prints with >= 3 lines
GEAR_PD = GEAR_M * GEAR_Z                # 30
GEAR_OD = GEAR_PD + 2 * GEAR_ADD * GEAR_M   # 33.4
GEAR_T = 6.0
PIVOT_Y = GEAR_PD / 2                    # driven gear on the servo at +y, idler at -y
X_S = 24.0                               # servo output / pivot x
Z_TAB = -8.5                             # servo tab top face (deck 3.5 lower so the flange-coupling screw
                                         # heads at r 8 / 45 deg clear the deck top)
TAB_T = S["tab thickness"]
Z_DECK_TOP = Z_TAB - TAB_T               # deck top = tab underside
DECK_T = 3.0
HORN_H = 3.5                             # horn top above the spline top [est, single-arm MG90S horn]
Z_GEAR = Z_TAB + S["shaft top height"] + HORN_H     # gear bottom sits on the horn
X_TIP = 75.0                             # finger pad centre (closed)
PAD = (6.0, 6.0)                         # pad x, y size
PAD_Z = (-18.0, Z_GEAR + GEAR_T)         # pads hang down so the grip centre is ~3 mm below the roll axis
FINGER_W = 8.0
IDLER_BOSS_D = 6.0                       # printed axle boss for the idler gear (gear bore +0.4)
# servo rotated 180 deg about z: body extends forward of the shaft, cable exits rearward
SERVO_BODY_X = (X_S - S["shaft offset"], X_S - S["shaft offset"] + S["body length"])
SERVO_TAB_HOLES_X = (X_S - (S["tab hole pitch"] / 2 - (S["body length"] / 2 - S["shaft offset"])),
                     X_S + (S["tab hole pitch"] / 2 + (S["body length"] / 2 - S["shaft offset"])))
