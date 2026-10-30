"""Driven gripper finger (+Y side): m2 z15 gear screwed to the MG90S single-arm horn, arm, and a
pad that hangs down so the grip centre sits on the roll axis. Closed pose as modelled.
G frame. Printed upside down (arm on the bed, pad up)."""
from pathlib import Path

from build123d import *

from features import export_printed, involute_gear, hull_sketch, circle_pts
from gripper_layout import *
from style import *

HERE = Path(__file__).parent
SIDE = +1
PAD_GAP = 0.2                    # each pad stops 0.2 short of y = 0 when closed
HORN_SLOT = (5.3, 15.0, 1.8)     # single-arm horn pocket: width, reach from centre, depth [est]
HORN_HUB_D = 7.5                 # horn hub + screw access [est]
HORN_PILOT = 1.5                 # pilots for the horn's self-tapping screws [est]
HORN_SCREW_R = (8.0, 11.5)       # radii of the horn's outer holes [est]


def finger(side):
    cy = side * PIVOT_Y
    pad_y = side * (PAD_GAP + PAD[1] / 2)
    with BuildPart(mode=Mode.PRIVATE) as f:
        g = involute_gear(GEAR_M, GEAR_Z, GEAR_T, addendum=GEAR_ADD)
        if side < 0:
            g = g.rotate(Axis.Z, 180 / GEAR_Z)        # half a tooth: meshes with the driven gear
        add(g.moved(Location((X_S, cy, Z_GEAR))))
        with BuildSketch(Plane.XY.offset(Z_GEAR)) as arm:
            # tip circle no wider than the pad, so the arm never crosses the pad's grip face
            add(hull_sketch(circle_pts(X_S, cy, 7.0) + circle_pts(X_TIP - 1.0, pad_y, PAD[1] / 2)))
        extrude(arm.sketch, amount=GEAR_T)
        with Locations((X_TIP, pad_y, (PAD_Z[0] + PAD_Z[1]) / 2)):
            Box(PAD[0] + 2, PAD[1], PAD_Z[1] - PAD_Z[0])
        # grip ridges on the inner face (1 mm deep, every 3 mm)
        for z in range(int(PAD_Z[0]) + 3, int(Z_GEAR) - 1, 3):     # below the arm: no 0.5 mm slivers
            with Locations((X_TIP, side * PAD_GAP, z)):
                Box(PAD[0] + 2.2, 1.0 * 2, 1.0, mode=Mode.SUBTRACT)
    return f.part


part = finger(SIDE)
with BuildPart() as fl:
    add(part)
    # horn pocket in the gear underside, hub hole through, two pilots
    with Locations((X_S, PIVOT_Y, Z_GEAR)):
        Cylinder(HORN_HUB_D / 2, 3 * GEAR_T, mode=Mode.SUBTRACT)
    with Locations((X_S + HORN_SLOT[1] / 2, PIVOT_Y, Z_GEAR)):
        Box(HORN_SLOT[1], HORN_SLOT[0], 2 * HORN_SLOT[2], mode=Mode.SUBTRACT)
    with Locations(*[(X_S + r, PIVOT_Y, Z_GEAR + GEAR_T) for r in HORN_SCREW_R]):
        Hole(HORN_PILOT / 2)

export_printed(fl.part, "gripper-finger-left", rot=(180, 0, 0), here=HERE)
