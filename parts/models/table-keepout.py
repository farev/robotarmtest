"""Keep-out: the table top the base stands on (z <= 0), r 400 around the yaw axis, 20 mm thick."""
from pathlib import Path

from build123d import *

HERE = Path(__file__).parent
with BuildPart() as t:
    with Locations((0, 0, -20.0)):
        Cylinder(400.0, 20.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
export_step(t.part, str(HERE / "table-keepout.step"))
