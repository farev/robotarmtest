"""Shared layout of the v1 arm: every dimension two parts agree on lives here.

World frame: table at z = 0, yaw axis = Z, arm points along +X at home, Y to the left.
The gripper/forearm plane is y = 0 (on the yaw axis), so planar IK needs no lateral offset;
the upper arm, its motor pack and the shoulder tower sit at -Y (offsets along the joint axes
do not change the planar kinematics).

Joints (all relative):
  J1 yaw about +Z (base)             GT2 20T -> printed 120T, 6:1
  J2 shoulder about -Y (up = +)       GT2 20T -> 60T, 20T -> printed 80T fixed on tower, 12:1
                                      (motor rides on the upper arm and climbs the fixed pulley)
  J3 elbow about -Y (relative)        GT2 20T -> printed 120T on the forearm, 6:1
  J4 wrist roll about forearm +X      direct drive, 5 mm rigid flange coupling
"""
from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
DATA = Path("/Users/fabianarevalo/Documents/Mechy/engine/mechy/data/standard_parts")


def _dims(slug):
    y = yaml.safe_load((ROOT / f"parts/models/{slug}.yaml").read_text())
    return {d["name"]: d["value_mm"] for d in y["critical_dims"]}


def _csv(name, key, val):
    rows = list(csv.DictReader(open(DATA / name)))
    return next(r for r in rows if r[key] == val)


# ---------------------------------------------------------------- bought parts
M = _dims("nema17-42shdc")                 # stepper, read by name
NEMA_FACE = M["face square"]
NEMA_PITCH = M["hole pitch"]
NEMA_PILOT = M["pilot diameter"]
NEMA_PILOT_H = M["pilot height"]
NEMA_LEN = M["body length"]                # ASSUMED 40 until measured
NEMA_SHAFT_L = M["shaft length"]           # ASSUMED 24 until measured

B608 = _csv("bearings_deep_groove.csv", "designation", "608")
B625 = _csv("bearings_deep_groove.csv", "designation", "625")
B6806 = _csv("bearings_deep_groove.csv", "designation", "6806")
D608, W608 = float(B608["D_mm"]), float(B608["B_mm"])        # 22 x 7
D625, W625 = float(B625["D_mm"]), float(B625["B_mm"])        # 16 x 5
D6806, d6806, W6806 = float(B6806["D_mm"]), float(B6806["d_mm"]), float(B6806["B_mm"])  # 42/30 x 7

GT2_P = 2.0


def pd(teeth):                              # GT2 pitch diameter (timing_pulleys.csv formula)
    return GT2_P * teeth / math.pi


def od(teeth):                              # GT2 outside diameter = PD - 0.508 (2 x pitch line offset)
    return pd(teeth) - 0.508


LOOPS = [int(float(r["pitch_length_mm"])) for r in csv.DictReader(open(DATA / "timing_belt_closed_loops.csv"))
         if r["profile"] == "GT2"]


def centre_for_loop(L, D, d):
    """Centre distance for a closed loop of pitch length L over pulleys of pitch diameters D, d."""
    b = 2 * L - math.pi * (D + d)
    return (b + math.sqrt(b * b - 8 * (D - d) ** 2)) / 8


def pick_loop(D, d, c_min):
    """Smallest stock loop whose centre distance is at least c_min."""
    for L in sorted(LOOPS):
        try:
            c = centre_for_loop(L, D, d)
        except ValueError:
            continue
        if c >= c_min:
            return L, c
    raise ValueError("no loop")


def wrap_small(D, d, c):
    return 180 - 2 * math.degrees(math.asin((D - d) / (2 * c)))


# bought pulley envelope (parts/models/std_parts.py): hub 7, flange 1, teeth 7, flange 1; belt centre 11.5
PUL_HUB, PUL_LEN, PUL_BELT = 7.0, 16.0, 11.5
PUL20_FL, PUL60_FL = 16.0, 42.0            # flange diameters
BELT_W, BELT_T = 6.0, 1.4

# ---------------------------------------------------------------- fits (fdm_pla_rules.md)
FIT_608 = D608 + 0.10       # bearing outer ring press, §1 (+0.05..0.15); retained by a lip/cap
FIT_625 = D625 + 0.10
FIT_6806 = D6806 + 0.10
ROD8_CLAMP = 8.2            # snug locating on a dead 8 mm rod, vertical holes (§1 snug +0.2)
ROD8_CLAMP_H = 8.3          # same fit in a horizontal (teardrop) hole: §1 adds +0.1
ROD8_CLEAR = 8.6            # clearance where the rod only passes (§1 running +0.4, +0.2 margin)
SPIGOT = d6806 - 0.15       # printed spigot into the 6806 inner ring (§1 outer feature -0.1..-0.2)
M3_CLEAR = 3.6              # §2
M3_CBORE = (6.5, 3.3)       # §2 counterbore dia x depth
M3_NUT = (5.75, 2.7)        # §2 hex trap across flats x depth
M3_INSERT = (4.0, 6.7)      # §3 insert hole dia x depth (M3 x 5.7 insert)
M3_BOSS = 8.0               # §3 boss OD around an M3 insert
BEARING_WALL_608 = 0.4 * FIT_608   # §4 wall around a bearing pocket: 0.4 x bore (8.8)
PRINT_GAP = 0.4             # §1 printed-on-printed sliding / running gap (total)
PILOT_CLEAR = NEMA_PILOT + 1.4   # motor pilot in a slotted (non-locating) mount: 0.7 radial, above the 0.5 check gap

# ---------------------------------------------------------------- base and J1
BASE_D = 230.0              # base shell outside diameter (fits the 256 bed with brim margin)
BASE_WALL = 3.0
BASE_FLOOR = 3.0
Z_DECK_BOT = 55.0           # deck underside = J1 motor mounting face
DECK_T = 5.0
Z_DECK = Z_DECK_BOT + DECK_T          # deck top, 60

T_YAW_SMALL, T_YAW_BIG = 20, 120
YAW_LOOP, YAW_C = pick_loop(pd(T_YAW_BIG), pd(T_YAW_SMALL), 68.0)
J1_RATIO = T_YAW_BIG / T_YAW_SMALL
J1_MOTOR_XY = (0.0, YAW_C)            # J1 motor at +Y, hanging under the deck
J1_MOTOR_ROT = -45.0                  # about Z: screw holes on the belt centreline / beside it, plug toward +X-Y
J1_SCREWS_XY = [(J1_MOTOR_XY[0] + NEMA_PITCH / 2 * math.sqrt(2) * math.cos(math.radians(a)),
                 J1_MOTOR_XY[1] + NEMA_PITCH / 2 * math.sqrt(2) * math.sin(math.radians(a))) for a in (0, 90, 180, 270)]

# base bearing stack (2 x 6806-2RS), pocket from below in a tube hanging under the deck
LIP_T = 2.0                 # deck lip over the upper outer ring
LIP_ID = 38.0               # clears the inner ring (d1 ~ 33) and stops on the outer ring
SPACER_H = 4.0              # outer and inner spacer rings between the bearings
Z_B_UP_TOP = Z_DECK - LIP_T                    # top face of the upper 6806
Z_B_LO_BOT = Z_B_UP_TOP - 2 * W6806 - SPACER_H  # bottom face of the lower 6806 (40)
TUBE_OD = FIT_6806 + 2 * 0.4 * FIT_6806        # §4 0.4 x bore wall -> ~76
CAP_T = 3.0                 # bearing cap under the tube (retains the lower outer ring)

# turret (rotating): steps on the upper inner ring, 120T band above the deck, plate above the J1 pulley
TURRET_GAP = 1.5            # turret underside above the deck
Z_TUR_BOT = Z_DECK + TURRET_GAP
FLANGE_T = 1.2
TEETH_W = 8.0               # printed toothed band for a 6 mm belt
Z_B1 = Z_TUR_BOT + FLANGE_T + TEETH_W / 2      # J1 belt plane (66.7)
# J1 motor pulley teeth on the plane, mounted hub up (needs >= 23 mm of shaft above the face):
# the hub end face is the pulley top, PUL_BELT above the belt centre
Z_J1_PUL_TOP = Z_B1 + PUL_BELT                  # 78.2
Z_TUR_PLATE = Z_J1_PUL_TOP + 2.0                # turret plate underside clears the J1 pulley (80.2)
TUR_PLATE_T = 6.0
Z_TUR_TOP = Z_TUR_PLATE + TUR_PLATE_T

# ---------------------------------------------------------------- Y stack (see module doc)
FA_HUB_HALF = 15.0                       # forearm hub y in [-15, 15], 608 pockets at both ends
BAND_W = 2 * FLANGE_T + TEETH_W          # 10.4 printed pulley band
Y_E = -FA_HUB_HALF - BAND_W / 2          # elbow belt plane (-20.2)
Y_ELB_MOTOR_FACE = Y_E - PUL_BELT - 0.5 - 4.0  # elbow motor mounting face (cover plate inner face)
COVER_T = 4.0
Y_COVER_OUT = Y_ELB_MOTOR_FACE + COVER_T  # cover outer face (elbow pulley hub 0.5 beyond)
PACK_AXIAL_GAP = 1.0                      # motor back to the opposite wall (body length tolerance)
Y_PACK_IN = Y_ELB_MOTOR_FACE - NEMA_LEN - PACK_AXIAL_GAP   # J2 motor mounting face = -y wall inner face
WALL_T = 4.0
Y_PACK_OUT = Y_PACK_IN - WALL_T           # -y wall outer face = bed face of the upper arm print
PUL_WALL_GAP = 1.0                        # pulley hub ends off the pack's -Y wall
Y_S1 = Y_PACK_OUT - PUL_WALL_GAP - PUL_BELT   # stage-1 belt plane (J2 20T -> 60T)
PUL_STACK_GAP = 1.0                       # between the 60T and the stage-2 20T on the intermediate shaft
Y_S2 = Y_PACK_OUT - PUL_WALL_GAP - PUL_LEN - PUL_STACK_GAP - PUL_BELT   # stage-2 plane (20T -> fixed 80T)
Y_FIX_PUL = (Y_S2 - BAND_W / 2, Y_S2 + BAND_W / 2)    # fixed 80T band on the tower
FIX_PUL_SPACER = 2.0                      # disc under the fixed band: stage-2 20T flange clears the tower face by 2.7
TOWER_T = 12.0
Y_TOWER = (Y_FIX_PUL[0] - FIX_PUL_SPACER - TOWER_T, Y_FIX_PUL[0] - FIX_PUL_SPACER)
# tower foot (shared by shoulder-tower and turret-hub): extends both sides of the wall so the screws
# sit clear of the wall and the +Y gussets (design review 2026-10-29, blocking 1)
TOWER_FOOT_X = (-45.0, 45.0)
TOWER_FOOT_Y = (Y_TOWER[0] - 13.0, -100.0)
TOWER_FOOT_INSERTS = [(x, y) for x in (-30.0, 30.0) for y in (Y_TOWER[0] - 6.5, Y_TOWER[1] + 7.5)]

# ---------------------------------------------------------------- J2 shoulder
T_S1_SMALL, T_S1_BIG = 20, 60
T_S2_SMALL, T_S2_BIG = 20, 80
J2_RATIO = (T_S1_BIG / T_S1_SMALL) * (T_S2_BIG / T_S2_SMALL)
S2_LOOP, S2_C = pick_loop(pd(T_S2_BIG), pd(T_S2_SMALL), (od(T_S2_BIG) + 2.4) / 2 + PUL20_FL / 2 + 6)
# stage 1 on a 200 mm loop (same belt as stage 2): the longer centre distance lets a hex key reach every J2
# motor screw clear of the stage-1 belt and the 60T (design/v1/scan_j2.py: >= 4 mm at J2_ANGLE 300)
S1_LOOP = 200
S1_C = centre_for_loop(S1_LOOP, pd(T_S1_BIG), pd(T_S1_SMALL))

L2 = 135.0                  # shoulder axis -> elbow axis
L3 = 120.0                  # elbow axis -> J4 motor mounting face
# upper-arm frame (UA): origin on the shoulder axis, x along the arm, z up at q2 = 0
INT_ANGLE = 180.0           # intermediate shaft straight behind the shoulder
INT_XZ = (S2_C * math.cos(math.radians(INT_ANGLE)), S2_C * math.sin(math.radians(INT_ANGLE)))
J2_ANGLE = 300.0            # J2 motor below and forward of the intermediate shaft: every J2 screw's key path
                            # clears the 60T flange and the stage-1 belt (review blocking 3, scan_j2.py)
J2_XZ = (INT_XZ[0] + S1_C * math.cos(math.radians(J2_ANGLE)), INT_XZ[1] + S1_C * math.sin(math.radians(J2_ANGLE)))
# The carriage slides perpendicular to the stage-1 line (rear-down): sliding it tensions stage 2 (C2 grows by
# 0.87 x the travel) without changing the stage-1 centre distance, so stage 1 is tensioned once on the bench
# (J2 motor slots) and stage 2 afterwards on the tower (carriage, from inside the pack).
CARR_ANGLE = J2_ANGLE - 90.0
CARR_DIR = (math.cos(math.radians(CARR_ANGLE)), math.sin(math.radians(CARR_ANGLE)))
CARR_SCREW_DX = 14.0                 # carriage clamp screws on the slide line, either side of the shaft
ELB_MOTOR_XZ_NOM = (INT_XZ[0], 36.0)      # elbow motor above the intermediate shaft
T_E_SMALL, T_E_BIG = 20, 120
J3_RATIO = T_E_BIG / T_E_SMALL
_c_nom = math.hypot(L2 - ELB_MOTOR_XZ_NOM[0], ELB_MOTOR_XZ_NOM[1])
E_LOOP, E_C = pick_loop(pd(T_E_BIG), pd(T_E_SMALL), _c_nom)
_u = ((ELB_MOTOR_XZ_NOM[0] - L2) / _c_nom, ELB_MOTOR_XZ_NOM[1] / _c_nom)
ELB_MOTOR_XZ = (L2 + _u[0] * E_C, _u[1] * E_C)   # slid back along the belt line to the loop's centre distance
SLOT = 3.0                  # +- tension travel on slotted mounts

HUB_OD = 2 * (FIT_608 / 2 + BEARING_WALL_608)      # 40: shoulder and elbow hubs
Y_UA_HUB = (Y_PACK_OUT, Y_ELB_MOTOR_FACE - 0.2)     # upper-arm shoulder hub span (just under the cover)
Y_UA_BEAM = (Y_PACK_OUT, Y_E - BELT_W / 2 - 4.0)     # beam stays 4 mm clear of the elbow belt
J2_LIMITS = (-30.0, 90.0)
J3_LIMITS = (-135.0, 120.0)

# motor pack outline (UA frame XZ): motor squares grown by slot travel, clearance and wall;
# the connector side (J2 down, elbow motor up) grows by the plug
CONN_OUT = 6.0
PACK_GROW = SLOT + 1.0 + 3.0


def pack_points():
    pts = []
    h = NEMA_FACE / 2 + PACK_GROW
    for (x, z), conn in ((J2_XZ, -1), (ELB_MOTOR_XZ, +1)):
        lo = -h - (CONN_OUT if conn < 0 else 0)
        hi = h + (CONN_OUT if conn > 0 else 0)
        pts += [(x - h, z + lo), (x + h, z + lo), (x + h, z + hi), (x - h, z + hi)]
    for i in range(36):                      # hub circle (+ wall)
        a = 2 * math.pi * i / 36
        pts.append(((HUB_OD / 2 + 3) * math.cos(a), (HUB_OD / 2 + 3) * math.sin(a)))
    return pts


# shoulder height: pack must clear the turret plate at every shoulder angle
def _pack_low(q2):
    a = math.radians(q2)
    return min(px * math.sin(a) + pz * math.cos(a) for px, pz in pack_points())


PACK_LOW = min(_pack_low(q) for q in range(int(J2_LIMITS[0]), int(J2_LIMITS[1]) + 1))
Z_SH = math.ceil(Z_TUR_TOP - PACK_LOW + 4.0)    # 4 mm clearance over the turret plate

# ---------------------------------------------------------------- forearm, wrist, gripper
FA_HALF = NEMA_FACE / 2 + 3.0         # forearm channel half-width around the J4 motor (z)
FA_Y = (-FA_HUB_HALF - BAND_W, NEMA_FACE / 2 + 3.0)   # forearm y span (bed face = band face)
X_J4_FACE = L3                         # J4 motor mounting face (forearm frame x)
FACE_PLATE_T = 4.0
COUPLING_FACE = X_J4_FACE + NEMA_SHAFT_L + 1.0   # coupling flange face 1 mm proud of the shaft tip


def summary():
    rows = {
        "J1 belt": f"GT2-{YAW_LOOP} loop, C = {YAW_C:.2f}, wrap {wrap_small(pd(120), pd(20), YAW_C):.0f} deg",
        "J2 stage 1": f"GT2-{S1_LOOP} loop, C = {S1_C:.2f}, wrap {wrap_small(pd(60), pd(20), S1_C):.0f} deg",
        "J2 stage 2": f"GT2-{S2_LOOP} loop, C = {S2_C:.2f}, wrap {wrap_small(pd(80), pd(20), S2_C):.0f} deg",
        "J3 belt": f"GT2-{E_LOOP} loop, C = {E_C:.2f}, wrap {wrap_small(pd(120), pd(20), E_C):.0f} deg",
        "ratios": f"J1 {J1_RATIO}, J2 {J2_RATIO}, J3 {J3_RATIO}, J4 1",
        "Z_SH": Z_SH, "Z_TUR_TOP": Z_TUR_TOP, "PACK_LOW": round(PACK_LOW, 1),
        "INT_XZ": tuple(round(v, 2) for v in INT_XZ), "J2_XZ": tuple(round(v, 2) for v in J2_XZ),
        "ELB_MOTOR_XZ": tuple(round(v, 2) for v in ELB_MOTOR_XZ),
        "Y": dict(E=Y_E, elb_face=Y_ELB_MOTOR_FACE, cover_out=Y_COVER_OUT, pack_in=Y_PACK_IN,
                  pack_out=Y_PACK_OUT, S1=Y_S1, S2=Y_S2, fix_pul=Y_FIX_PUL, tower=Y_TOWER),
    }
    return rows


if __name__ == "__main__":
    import pprint
    pprint.pprint(summary(), width=110)
