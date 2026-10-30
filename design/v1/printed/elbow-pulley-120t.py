"""Elbow GT2 120T pulley: bolted under the forearm hub with 4 x M3 x 12 (heads in counterbores on the underside,
into the forearm's heat-set inserts), so the elbow belt runs below the forearm channel. Its 13 mm bore clears the
dead elbow rod, the 608's inner ring and the upper arm's stop boss; its top face retains the lower 608's outer ring.
FA frame as assembled. Printed bottom (flat flange) on the bed (local axis = +Y)."""
import math
from pathlib import Path

from build123d import *

from features import export_printed, gt2_band
from layout import *
from style import *

HERE = Path(__file__).parent

with BuildPart(mode=Mode.PRIVATE) as local:          # local frame: axis +Z, z = 0 on the bottom face
    add(gt2_band(T_E_BIG))
    Cylinder(EP_BORE / 2, 100, mode=Mode.SUBTRACT)
    with Locations(*[(EP_SCREW_R * math.cos(math.radians(a)), EP_SCREW_R * math.sin(math.radians(a)), 0)
                     for a in (45, 135, 225, 315)]):
        Cylinder(M3_CLEAR / 2, 100, mode=Mode.SUBTRACT)
        Cylinder(M3_CBORE[0] / 2, 2 * M3_CBORE[1], mode=Mode.SUBTRACT)   # counterbore 3.3 deep from the bottom

# local +Z -> FA +Y; local z = 0 -> y = EP_Y[0]. Local (x, y) -> FA (x, -z): screw angles mirror, which is symmetric.
part = local.part.rotate(Axis.X, -90).moved(Location((0, EP_Y[0], 0)))
export_printed(part, "elbow-pulley-120t", rot=(90, 0, 0), here=HERE)
