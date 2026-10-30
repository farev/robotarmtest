"""Forearm cover: closes the forearm channel over the J4 motor. 4 x M3 x 8 socket heads into the
forearm's inserts. Printed outer face down; FA frame as assembled."""
import json
from pathlib import Path

from build123d import *

from features import export_printed
from layout import *
from style import *

HERE = Path(__file__).parent
INSERTS = json.loads((HERE / "forearm.inserts.json").read_text())
T = 3.0
X0 = 24.0                          # starts behind the elbow collar (r 8) with clearance
X1 = X_J4_FACE + FACE_PLATE_T
ZW = NEMA_FACE / 2 + 0.7 + WALL          # matches forearm ZW_OUT
Y0 = FA_Y[1]

with BuildPart() as cv:
    with Locations(((X0 + X1) / 2, Y0 + T / 2, 0)):
        Box(X1 - X0, T, 2 * ZW)
    with Locations(*[Location((x, Y0 + T, z), (90, 0, 0)) for x, z in INSERTS]):
        Cylinder(M3_CLEAR / 2, 3 * T, mode=Mode.SUBTRACT)
    # window over the J4 motor plug (plug 32.5 behind the motor face, 16 wide along z): cable exits up
    with Locations((X_J4_FACE - 32.5, Y0 + T / 2, 0)):
        Box(14.0, 3 * T, 20.0, mode=Mode.SUBTRACT)

part = cv.part
part = try_fillet(part, part.edges().filter_by(Axis.Y), R_OUTER)
export_printed(part, "forearm-cover", rot=(-90, 0, 0), here=HERE)
