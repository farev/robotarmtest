"""Shoulder tower: the one upright on the turret. Clamps the dead 8 mm shoulder shaft
(cantilevered toward +Y, the upper arm rides on it on 2 x 608) and carries the fixed 80T
pulley that the J2 motor pack climbs. Printed standing on its foot, as assembled
(turret frame)."""
import math
from pathlib import Path

from build123d import *

from features import export_printed, hull_sketch, circle_pts, rect_pts, teardrop
from layout import *
from style import *

HERE = Path(__file__).parent
Y0, Y1 = Y_TOWER                          # wall y span (12 thick)
FOOT_T = 6.0
FOOT_X, FOOT_Y, FOOT_INSERTS = TOWER_FOOT_X, TOWER_FOOT_Y, TOWER_FOOT_INSERTS   # layout.py, shared with turret-hub
Z_FOOT = Z_TUR_TOP
TOP_R = 30.0                              # round head around the shoulder axis
GUSSET_X = (-40.0, 40.0)
GUSSET_T = 5.0
GUSSET_TOP = 132.0                        # stays under the stage-2 pulley's lowest orbit (138)
PUL_SCREW_R = 18.0                        # fixed-pulley screws (match shoulder-pulley-80t)
PUL_SCREW_ANG = [45, 135, 225, 315]
PUL_CBORE_DEPTH = 5.5                     # M3 x 12 into the pulley inserts engages 5.5 (rules §2)

with BuildPart() as tower:
    # foot plate
    with BuildSketch(Plane.XY.offset(Z_FOOT)):
        with Locations(((FOOT_X[0] + FOOT_X[1]) / 2, (FOOT_Y[0] + FOOT_Y[1]) / 2)):
            RectangleRounded(FOOT_X[1] - FOOT_X[0], FOOT_Y[1] - FOOT_Y[0], R_OUTER)
    extrude(amount=FOOT_T)
    # wall: hull of the foot width and the round head, in the XZ plane, Y0..Y1
    pl = Plane(origin=(0, Y1, 0), x_dir=(1, 0, 0), z_dir=(0, -1, 0))      # sketch XZ, extrude toward -Y
    pts = rect_pts(0, Z_FOOT + FOOT_T / 2, (FOOT_X[1] - FOOT_X[0]) / 2, FOOT_T / 2) + circle_pts(0, Z_SH, TOP_R)
    with BuildSketch(pl):
        add(hull_sketch([(x, z) for x, z in pts]))
    extrude(amount=Y1 - Y0)
    # gussets on the +Y face, under the pack's orbit
    for gx in GUSSET_X:
        gpl = Plane(origin=(gx, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0))
        with BuildSketch(gpl):
            Polygon((Y1, Z_FOOT + FOOT_T), (FOOT_Y[1], Z_FOOT + FOOT_T), (Y1, GUSSET_TOP))
        extrude(amount=GUSSET_T / 2, both=True)
    # shoulder shaft: snug 8.2 teardrop bore (horizontal, roof up)
    add(teardrop(ROD8_CLAMP_H / 2, 3 * TOWER_T, Plane(origin=(0, (Y0 + Y1) / 2, Z_SH), x_dir=(-1, 0, 0), z_dir=(0, 1, 0))),
        mode=Mode.SUBTRACT)
    # shaft lock: M3 insert in the head top (vertical as printed); an M3 x 30 runs down a 3.6 clearance
    # passage onto the rod (it stops with ~4 mm showing; an M3 jam nut on top locks it)
    with Locations((0, (Y0 + Y1) / 2, Z_SH + TOP_R)):
        Hole(M3_INSERT[0] / 2, M3_INSERT[1])
        Hole(M3_CLEAR / 2, TOP_R)
    # fixed-pulley screws: through the wall, counterbored on the outer (-Y) face
    for a in PUL_SCREW_ANG:
        x = PUL_SCREW_R * math.cos(math.radians(a))
        z = Z_SH + PUL_SCREW_R * math.sin(math.radians(a))
        add(Solid.make_cylinder(M3_CLEAR / 2, 3 * TOWER_T, Plane(origin=(x, Y0 - TOWER_T, z), z_dir=(0, 1, 0))), mode=Mode.SUBTRACT)
        add(Solid.make_cylinder(M3_CBORE[0] / 2, PUL_CBORE_DEPTH + 5, Plane(origin=(x, Y0 - 5, z), z_dir=(0, 1, 0))), mode=Mode.SUBTRACT)
    # foot screws: M3 x 10 down into the turret inserts (foot 6 + 6.7 insert)
    with Locations(*[(x, y, Z_FOOT + FOOT_T) for x, y in FOOT_INSERTS]):
        Hole(M3_CLEAR / 2)
    # no lightening window: a 26 mm opening beside the orbiting stage-2 pulley is a finger trap (review 2)

part = tower.part
export_printed(part, "shoulder-tower", here=HERE)
