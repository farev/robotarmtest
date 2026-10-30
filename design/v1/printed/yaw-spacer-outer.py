"""Spacer between the two 6806 outer rings: slides in the 42.1 pocket, clears the inner ring.
Printed flat; as assembled it sits on top of the lower bearing."""
from pathlib import Path

from build123d import *

from features import export_printed
from layout import *

HERE = Path(__file__).parent
Z0 = Z_B_LO_BOT + W6806

with BuildPart() as p:
    with Locations((0, 0, Z0)):
        Cylinder((FIT_6806 - PRINT_GAP) / 2, SPACER_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    Cylinder(LIP_ID / 2, 500, mode=Mode.SUBTRACT)
export_printed(p.part, "yaw-spacer-outer", here=HERE)
