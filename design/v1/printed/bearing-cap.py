"""Retains the lower 6806's outer ring under the deck tube. 3 x M3 x 8 into the tube's inserts.
Printed flat; as assembled its top face is at Z_B_LO_BOT."""
import math
from pathlib import Path

from build123d import *

from features import export_printed
from layout import *

HERE = Path(__file__).parent
R = (FIT_6806 / 2 + TUBE_OD / 2) / 2      # same screw circle as base-deck

with BuildPart() as p:
    with Locations((0, 0, Z_B_LO_BOT - CAP_T)):
        Cylinder(TUBE_OD / 2, CAP_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    Cylinder(LIP_ID / 2, 500, mode=Mode.SUBTRACT)      # clears the inner ring and the turret clamp
    with Locations(*[(R * math.cos(math.radians(a)), R * math.sin(math.radians(a)), Z_B_LO_BOT) for a in (90, 210, 330)]):
        Hole(M3_CLEAR / 2)
export_printed(p.part, "bearing-cap", here=HERE)
