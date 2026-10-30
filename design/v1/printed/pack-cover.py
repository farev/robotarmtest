"""Pack cover: closes the upper arm's motor pack on the +Y side and carries the elbow motor
(slotted along the elbow belt for tension). 5 x M3 x 10 socket heads into the pack's inserts.
Printed outer face down (the visible face gets the bed finish); UA frame as assembled."""
import json
import math
from pathlib import Path

from build123d import *

from features import export_printed, hull_sketch
from layout import *
from style import *

HERE = Path(__file__).parent
BOSSES = json.loads((HERE / "upper-arm.bosses.json").read_text())     # written by upper-arm.py
DE = ((L2 - ELB_MOTOR_XZ[0]) / E_C, (0 - ELB_MOTOR_XZ[1]) / E_C)     # toward the elbow pulley
COLLAR_CLEAR = D608 + 1.0          # clears the shoulder 608's face and the 8 mm collar


def PXZ(y):
    return Plane(origin=(0, y, 0), x_dir=(1, 0, 0), z_dir=(0, -1, 0))


def slot(cx, cz, d, length, width):
    with BuildSketch(mode=Mode.PRIVATE) as s:
        with Locations(Location((cx, cz), math.degrees(math.atan2(d[1], d[0])))):
            SlotCenterToCenter(length, width)
    return s.sketch


with BuildPart() as cover:
    with BuildSketch(PXZ(Y_COVER_OUT)) as sk:
        add(hull_sketch(pack_points()))
    extrude(sk.sketch, amount=COVER_T)
    with BuildSketch(PXZ(Y_COVER_OUT)) as holes:
        # elbow motor: pilot and screw slots along the belt line (pull away from the elbow to tension)
        add(slot(ELB_MOTOR_XZ[0], ELB_MOTOR_XZ[1], DE, 2 * SLOT, PILOT_CLEAR))
        for sx in (-1, 1):
            for sz in (-1, 1):
                add(slot(ELB_MOTOR_XZ[0] + sx * NEMA_PITCH / 2, ELB_MOTOR_XZ[1] + sz * NEMA_PITCH / 2, DE, 2 * SLOT, M3_CLEAR))
        with Locations((0, 0)):
            Circle(COLLAR_CLEAR / 2)
        with Locations(*[(x, z) for x, z in BOSSES]):
            Circle(M3_CLEAR / 2)
    extrude(holes.sketch, amount=COVER_T, mode=Mode.SUBTRACT)

part = cover.part
part = try_fillet(part, part.edges().filter_by(Axis.Y).filter_by(lambda e: e.length > COVER_T - 0.1), R_EDGE)
export_printed(part, "pack-cover", rot=(-90, 0, 0), here=HERE)
