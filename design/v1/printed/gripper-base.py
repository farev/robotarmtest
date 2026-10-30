"""Gripper base: bolts to the J4 5 mm rigid flange coupling with 4 x M3 x 8 put in from behind the flange
(round heads clear the coupling hub) into nuts captured in hex pockets on the plate's front face; join the two
on the bench before the coupling goes on the motor shaft and before the servo goes in), holds the MG90S through a deck cut-out
(2 x M2 x 8 + nuts through the tabs) and carries the idler-gear post.
G frame (see gripper_layout.py). Printed deck down, as assembled."""
import math
from pathlib import Path

from build123d import *

from features import export_printed
from gripper_layout import *
from layout import M3_CLEAR, M3_INSERT, M3_NUT
from style import *

HERE = Path(__file__).parent
PLATE_T = 5.0                                        # 2.3 mm left behind the 2.7 deep nut pockets
PLATE_Y, PLATE_Z1 = 20.0, 20.0
Z_DECK_BOT = Z_DECK_TOP - DECK_T
DECK_X1 = SERVO_TAB_HOLES_X[1] + 5.0
DECK_Y = 26.0
FLANGE_R, FLANGE_ANG = 8.0, [45, 135, 225, 315]     # generic 5 mm flange coupling: 4 holes on a 16 circle;
                                                     # at 45 deg the heads (z >= -8.4) clear the deck top (-11)
CUT = 0.3                                            # rules §1: pocket for a bought body, +0.3 per side
M2_CLEAR = 2.6
POST_D = 10.0
AXLE_D = 8.0                                         # idler axle boss; gear bore 8.4 (printed-on-printed +0.4)

with BuildPart() as gb:
    # mount plate (YZ) against the coupling flange
    with BuildSketch(Plane.YZ.offset(0)) as pl:
        with Locations((0, (Z_DECK_BOT + PLATE_Z1) / 2)):
            RectangleRounded(2 * PLATE_Y, PLATE_Z1 - Z_DECK_BOT, R_SMALL)
    extrude(pl.sketch, amount=PLATE_T)
    # deck
    with Locations(((PLATE_T + DECK_X1) / 2 - 0.01, 0, (Z_DECK_BOT + Z_DECK_TOP) / 2)):
        Box(DECK_X1 - PLATE_T + 0.02, 2 * DECK_Y, DECK_T)
    # gussets between plate and deck
    for gy in (-DECK_Y + 2, DECK_Y - 2):
        with BuildSketch(Plane.XZ.offset(-gy)) as gs:
            Polygon((PLATE_T, Z_DECK_TOP), (PLATE_T + 10, Z_DECK_TOP), (PLATE_T, Z_DECK_TOP + 10))
        extrude(gs.sketch, amount=2.0, both=True)
    # idler post + axle boss
    with Locations((X_S, -PIVOT_Y, Z_DECK_TOP)):
        Cylinder(POST_D / 2, Z_GEAR - Z_DECK_TOP, align=(Align.CENTER, Align.CENTER, Align.MIN))
    with Locations((X_S, -PIVOT_Y, Z_GEAR)):
        Cylinder(AXLE_D / 2, GEAR_T + 0.2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # ---- cuts
    # coupling screws and shaft-tip clearance (horizontal holes, < 8 mm: bridge as printed)
    for a in FLANGE_ANG:
        y, z = FLANGE_R * math.cos(math.radians(a)), FLANGE_R * math.sin(math.radians(a))
        add(Solid.make_cylinder(M3_CLEAR / 2, 3 * PLATE_T, Plane(origin=(-PLATE_T, y, z), z_dir=(1, 0, 0))), mode=Mode.SUBTRACT)
        # hex nut pocket on the front face (rules §2: AF + 0.25, depth nut + 0.3), flats up: the roof is a
        # 3.3 mm bridge as printed (summary.md)
        with BuildSketch(Plane(origin=(PLATE_T, y, z), x_dir=(0, 1, 0), z_dir=(-1, 0, 0))) as nut:
            RegularPolygon((M3_NUT[0]) / math.sqrt(3), 6, rotation=0)
        extrude(nut.sketch, amount=M3_NUT[1], mode=Mode.SUBTRACT)
    # no centre hole: the shaft tip stops 1 mm short of the plate (hub face 1 mm proud)
    # servo body cut-out (servo rotated 180 deg: body forward of the shaft)
    with Locations(((SERVO_BODY_X[0] + SERVO_BODY_X[1]) / 2, PIVOT_Y, Z_DECK_BOT)):
        Box(SERVO_BODY_X[1] - SERVO_BODY_X[0] + 2 * CUT, S["body width"] + 2 * CUT, 3 * DECK_T, mode=Mode.SUBTRACT)
    with Locations(*[(x, PIVOT_Y, Z_DECK_TOP) for x in SERVO_TAB_HOLES_X]):
        Hole(M2_CLEAR / 2)
    # idler axle insert (M3 x 6 + M3 x 12 mm OD fender washer retains the gear, 1.8 mm overlap on its 8.4 bore)
    with Locations((X_S, -PIVOT_Y, Z_GEAR + GEAR_T + 0.2)):
        Hole(M3_INSERT[0] / 2, M3_INSERT[1])

part = gb.part
export_printed(part, "gripper-base", here=HERE)
