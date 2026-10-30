"""Forearm (link 3): elbow hub on 2 x 608 riding the dead elbow shaft and a U-channel that encloses the J4
wrist-roll motor (face plate at the tip, shaft forward along the forearm). Open on +Y, closed by forearm-cover.
The elbow 120T pulley is a separate part (elbow-pulley-120t) bolted under the hub with 4 x M3 into inserts here,
so the elbow belt runs below the channel floor, clear of the walls at every elbow angle.
FA frame: origin on the elbow axis, x along the forearm, y = world y (forearm centred on y = 0),
z up at q3 = 0. Printed with the floor underside (-Y) on the bed (rotated +90 deg about X)."""
import math
from pathlib import Path

from build123d import *

from features import export_printed, bed_bearing_pocket, teardrop
from layout import *
from style import *

HERE = Path(__file__).parent
HUB_R = HUB_OD / 2
Y_BED = FA_FLOOR_Y                    # -24.85: floor underside = bed face
Y_TOP = FA_Y[1]                       # channel top edge (cover sits on it)
ZW_IN = NEMA_FACE / 2 + 0.7           # channel inner half-width: 0.7 mm around the J4 motor
ZW_OUT = ZW_IN + WALL
FLOOR_T = 3.0
X_PLATE = X_J4_FACE
INS_Z = ZW_OUT - M3_INSERT[0] / 2 - 2.0     # 2.0 mm wall outside the insert hole (rules §3)
COVER_INSERTS = [(x, s * INS_Z) for x in (30.0, 70.0) for s in (-1, 1)]
EP_INSERTS = [(EP_SCREW_R * math.cos(math.radians(a)), EP_SCREW_R * math.sin(math.radians(a))) for a in (45, 135, 225, 315)]

with BuildPart() as fa:
    # elbow hub, floor underside to the top bearing
    with Locations(Location((0, Y_BED, 0), (-90, 0, 0))):
        Cylinder(HUB_R, FA_HUB_HALF - Y_BED, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # U-channel: floor + two side walls, from the hub to the motor face plate
    with Locations((X_PLATE / 2, Y_BED + FLOOR_T / 2, 0)):
        Box(X_PLATE, FLOOR_T, 2 * ZW_OUT)
    for s in (-1, 1):
        with Locations((X_PLATE / 2, (Y_BED + Y_TOP) / 2, s * (ZW_IN + WALL / 2))):
            Box(X_PLATE, Y_TOP - Y_BED, WALL)
    # motor face plate
    with Locations((X_PLATE + FACE_PLATE_T / 2, (Y_BED + Y_TOP) / 2, 0)):
        Box(FACE_PLATE_T, Y_TOP - Y_BED, 2 * ZW_OUT)
    # cover-insert bosses inside the side walls
    with Locations(*[(x, (Y_BED + Y_TOP) / 2, z - (1 if z > 0 else -1) * (M3_BOSS / 2 - (ZW_OUT - abs(z))))
                     for x, z in COVER_INSERTS]):     # full-height columns, outer face flush with the wall
        Box(M3_BOSS, Y_TOP - Y_BED, M3_BOSS)
    # ---- cuts
    # 608 pockets: bed-side one (ledge + cone so the ceiling prints), top one open upward; rod clearance between
    add(bed_bearing_pocket(FIT_608, W608, 19.0, ROD8_CLEAR).rotate(Axis.X, -90).moved(Location((0, Y_BED, 0))),
        mode=Mode.SUBTRACT)
    with Locations(Location((0, FA_HUB_HALF - W608, 0), (-90, 0, 0))):
        Cylinder(FIT_608 / 2, W608 + 1, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
    # elbow-pulley inserts, opening on the bed face (rules §3: wall to the 608 pocket 2.45, to the hub rim 2.5)
    with Locations(*[Location((x, Y_BED, z), (-90, 0, 0)) for x, z in EP_INSERTS]):
        Cylinder(M3_INSERT[0] / 2, M3_INSERT[1], align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
    # J4 motor pilot (teardrop, roof toward +Y = print up) and 4 x M3 clearance
    add(teardrop(PILOT_CLEAR / 2, 3 * FACE_PLATE_T,
                 Plane(origin=(X_PLATE + FACE_PLATE_T / 2, 0, 0), x_dir=(0, 0, -1), z_dir=(1, 0, 0))), mode=Mode.SUBTRACT)
    for sy in (-1, 1):
        for sz in (-1, 1):
            add(Solid.make_cylinder(M3_CLEAR / 2, 3 * FACE_PLATE_T,
                                    Plane(origin=(X_PLATE - FACE_PLATE_T, sy * NEMA_PITCH / 2, sz * NEMA_PITCH / 2), z_dir=(1, 0, 0))),
                mode=Mode.SUBTRACT)
    # cover inserts from the top edge
    with Locations(*[Location((x, Y_TOP, z), (90, 0, 0)) for x, z in COVER_INSERTS]):
        Cylinder(M3_INSERT[0] / 2, 2 * M3_INSERT[1], mode=Mode.SUBTRACT)

part = fa.part
export_printed(part, "forearm", rot=(90, 0, 0), here=HERE)
import json
(HERE / "forearm.inserts.json").write_text(json.dumps(COVER_INSERTS))
print("volume cm3", round(part.volume / 1000, 1))
