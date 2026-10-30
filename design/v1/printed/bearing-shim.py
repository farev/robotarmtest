"""Inner-ring shim between a 608 and an 8 mm shaft collar: OD 11.5 touches only the inner ring
(608 inner ring OD ~12.1 [est]) so the fixed collar never rubs the seal. 3 needed. Printed flat.
Modelled at the origin, axis Z; the assembly places each copy."""
from pathlib import Path

from build123d import *

from features import export_printed
from layout import *

HERE = Path(__file__).parent
SHIM_T = 1.2               # 3 layers of 0.4 lines minimum (printer min wall 1.2)

with BuildPart() as p:
    Cylinder(11.5 / 2, SHIM_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    Cylinder(ROD8_CLEAR / 2, 10, mode=Mode.SUBTRACT)
export_printed(p.part, "bearing-shim", here=HERE)
