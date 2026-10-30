"""Base deck: lid of the base shell. Carries the J1 motor (hanging below, slotted for belt
tension) and the 2 x 6806-2RS yaw bearing tube (hanging below, pocket open downward).
Printed top face down (rotated 180 deg about X); as-assembled frame = world at q1 = 0."""
import math
from pathlib import Path

from build123d import *

from features import export_printed
from layout import *
from style import *

HERE = Path(__file__).parent
R_OUT = BASE_D / 2
DECK_BOSS_R = R_OUT - BASE_WALL - 3.5        # matches base-shell bosses
DECK_BOSS_ANG = [30 + 60 * k for k in range(6)]
CAP_SCREW_R = (FIT_6806 / 2 + TUBE_OD / 2) / 2   # cap screws midway through the tube wall
MX, MY = J1_MOTOR_XY

with BuildPart() as deck:
    # deck plate z = Z_DECK_BOT .. Z_DECK
    with Locations((0, 0, Z_DECK_BOT)):
        Cylinder(R_OUT, DECK_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # bearing tube hanging down to the lower bearing's bottom face
    with Locations((0, 0, Z_B_LO_BOT)):
        Cylinder(TUBE_OD / 2, Z_DECK_BOT - Z_B_LO_BOT, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # pocket: 6806 press fit (rules §1 +0.1) from below up to the lip; lip hole above
    with Locations((0, 0, Z_B_LO_BOT)):
        Cylinder(FIT_6806 / 2, Z_B_UP_TOP - Z_B_LO_BOT, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
    Cylinder(LIP_ID / 2, 200, mode=Mode.SUBTRACT)
    # bearing-cap screws: M3 inserts into the tube's bottom face
    with Locations(*[(CAP_SCREW_R * math.cos(math.radians(a)), CAP_SCREW_R * math.sin(math.radians(a)), Z_B_LO_BOT)
                     for a in (90, 210, 330)]):
        Cylinder(M3_INSERT[0] / 2, M3_INSERT[1], align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
    # J1 motor: pilot slot and 4 x M3 slots along Y (belt tension, +-SLOT)
    with BuildSketch(Plane.XY.offset(Z_DECK_BOT)) as sk:
        with Locations((MX, MY)):
            SlotCenterToCenter(2 * SLOT, PILOT_CLEAR, rotation=90)
        # motor turned 45 deg (layout J1_MOTOR_ROT): its holes sit on the belt centreline and beside the pulley, so
        # a key reaches all four with the belt on (review 2, blocking 2)
        with Locations(*J1_SCREWS_XY):
            SlotCenterToCenter(2 * SLOT, M3_CLEAR, rotation=90)
    extrude(amount=DECK_T, mode=Mode.SUBTRACT)
    # deck screws into the shell bosses: M3 clearance, M3 x 10 socket heads on top (no counterbore:
    # a counterbore on the bed face would print as an unsupported ceiling)
    with Locations(*[(DECK_BOSS_R * math.cos(math.radians(a)), DECK_BOSS_R * math.sin(math.radians(a)), Z_DECK)
                     for a in DECK_BOSS_ANG]):
        Hole(M3_CLEAR / 2)

part = deck.part
export_printed(part, "base-deck", rot=(180, 0, 0), here=HERE)
