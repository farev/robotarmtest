"""Keep-out for the 42SHDC stepper's 6-pin plug and cable bend, in the motor frame of
nema17-42shdc.step (connector on the +X face near the back). Plug 16 x 7 [est] plus 18 mm of
straight cable before it may bend."""
from pathlib import Path

from build123d import *

HERE = Path(__file__).parent
FACE, BODY_L, CONN_OUT = 42.3, 40.0, 5.0
X0 = FACE / 2 + CONN_OUT
with BuildPart() as k:
    with Locations((X0 + 9.0, 0, -BODY_L + 4 + 3.5)):
        Box(18.0, 18.0, 10.0)
export_step(k.part, str(HERE / "nema17-plug-keepout.step"))
