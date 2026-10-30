"""ISO 4762 M3 socket head cap screws and hex-key access keep-outs (fasteners_iso4762_shcs.csv:
head 5.5 x 3). Frame: origin at the underside of the head on the axis, head toward +Z, shank toward
-Z. The shank is modelled at the thread minor diameter (2.46) so a screw centred in a 3.6
clearance hole clears it by 0.57 and the check only flags a misplaced screw.
Key keep-out: head-diameter cylinder from the head top, 60 mm long (assembly skill step 5)."""
from pathlib import Path

from build123d import *

HERE = Path(__file__).parent
HEAD_D, HEAD_K, MINOR = 5.5, 3.0, 2.46
for L in (8, 10, 12, 30):
    with BuildPart() as s:
        Cylinder(HEAD_D / 2, HEAD_K, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations((0, 0, -L)):
            Cylinder(MINOR / 2, L, align=(Align.CENTER, Align.CENTER, Align.MIN))
    export_step(s.part, str(HERE / f"m3x{L}-shcs.step"))
with BuildPart() as k:            # assembly skill: head diameter + 1 = 6.5, 60 mm from the head top
    with Locations((0, 0, HEAD_K)):
        Cylinder(6.5 / 2, 60.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
export_step(k.part, str(HERE / "m3-key-keepout.step"))
with BuildPart() as kn:           # straight / ball-end 2.5 key only, 0.5 margin: for screws next to a belt strand
    with Locations((0, 0, HEAD_K)):
        Cylinder(3.5 / 2, 60.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
export_step(kn.part, str(HERE / "m3-key-keepout-narrow.step"))
print("ok")
