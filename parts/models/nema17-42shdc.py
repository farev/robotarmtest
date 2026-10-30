"""42SHDC3026-15B NEMA 17 stepper, built from NEMA 17 / 42SHDC30xx family drawing values.

Frame: origin at the centre of the mounting face (the face the pilot boss stands on),
body toward -Z, shaft along +Z, D-flat facing +X. Connector on the +X side face, near the back.

Face square 42.3, hole pitch 31.0, M3 x 4.5 deep, pilot 22 x 2 and the 5 mm D-shaft are NEMA 17
values shared by the 42SHDC3025-24B (Anet A8) sibling. Body length 40 mm and shaft length 24 mm
are ASSUMED until the user measures them (see nema17-42shdc.yaml).
"""
from pathlib import Path

from build123d import *

HERE = Path(__file__).parent

FACE = 42.3          # face square (NEMA 17)
CORNER_C = 5.0       # 45 deg corner chamfer on the body's long edges [est]
BODY_L = 40.0        # body length, ASSUMED (sibling 42SHDC3025-24B: 42 x 42 x 40)
PITCH = 31.0         # M3 hole pitch
HOLE_D = 2.5         # M3 tap drill, modelled as the hole
HOLE_DEPTH = 4.5     # typical NEMA 17 thread depth
PILOT_D = 22.0       # pilot boss
PILOT_H = 2.0
SHAFT_D = 5.0
SHAFT_FLAT = 4.5     # across the D-flat
SHAFT_L = 24.0       # from the mounting face, ASSUMED
FLAT_L = 15.0        # flat length from the shaft tip
CONN = (16.0, 7.0, 5.0)   # connector housing: width (Y) x height (Z) x protrusion (X) [est]

with BuildPart() as body:
    Box(FACE, FACE, BODY_L, align=(Align.CENTER, Align.CENTER, Align.MAX))
    chamfer(body.edges().filter_by(Axis.Z), length=CORNER_C)
    with Locations(Location((0, 0, 0))):
        with GridLocations(PITCH, PITCH, 2, 2):
            Hole(HOLE_D / 2, depth=HOLE_DEPTH)
    Cylinder(PILOT_D / 2, PILOT_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    with Locations((FACE / 2 + CONN[2] / 2 - 0.5, 0, -BODY_L + 4 + CONN[1] / 2)):
        Box(CONN[2] + 1, CONN[0], CONN[1])
    # shaft with the D-flat on +X over the last FLAT_L
    with Locations((0, 0, PILOT_H)):
        Cylinder(SHAFT_D / 2, SHAFT_L - PILOT_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    with Locations((SHAFT_FLAT - SHAFT_D / 2 + 2.5, 0, SHAFT_L - FLAT_L / 2)):
        Box(5, 6, FLAT_L, mode=Mode.SUBTRACT)

export_step(body.part, str(HERE / "nema17-42shdc.step"))
