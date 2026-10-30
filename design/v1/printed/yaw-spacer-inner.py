"""Spacer between the two 6806 inner rings, on the turret spigot (slip fit, rules §1 +0.3).
OD 33 stays on the inner ring land (6806 inner ring OD ~33.5 [est]). Printed flat."""
from pathlib import Path

from build123d import *

from features import export_printed
from layout import *

HERE = Path(__file__).parent
Z0 = Z_B_LO_BOT + W6806

with BuildPart() as p:
    with Locations((0, 0, Z0)):
        Cylinder(33.0 / 2, SPACER_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    Cylinder((d6806 + 0.3) / 2, 500, mode=Mode.SUBTRACT)
export_printed(p.part, "yaw-spacer-inner", here=HERE)
