"""Debug: list solids of a STEP with their bounding boxes."""
import sys

from build123d import import_step

s = import_step(sys.argv[1])
for i, so in enumerate(s.solids()):
    b = so.bounding_box()
    print(i, [round(v, 1) for v in (b.min.X, b.min.Y, b.min.Z, b.max.X, b.max.Y, b.max.Z)], round(so.volume))
