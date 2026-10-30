"""Clamp washer under the lower 6806 inner ring: 3 x M3 x 8 into the spigot's inserts pull the
inner stack (lower ring, inner spacer, upper ring) up against the turret step. Printed flat."""
import math
from pathlib import Path

from build123d import *

from features import export_printed
from layout import *

HERE = Path(__file__).parent
CLAMP_T = 3.0
SPIGOT_SCREW_R = 10.5         # matches turret-hub

with BuildPart() as p:
    with Locations((0, 0, Z_B_LO_BOT - CLAMP_T)):
        Cylinder(33.0 / 2, CLAMP_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    Cylinder(12.0 / 2, 500, mode=Mode.SUBTRACT)                 # cable pass, same as the spigot bore
    with Locations(*[(SPIGOT_SCREW_R * math.cos(math.radians(a)), SPIGOT_SCREW_R * math.sin(math.radians(a)), Z_B_LO_BOT)
                     for a in (90, 210, 330)]):
        Hole(M3_CLEAR / 2)
export_printed(p.part, "turret-clamp", here=HERE)
