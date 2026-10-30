"""Debug: list downward-facing faces (overhangs) of a printed STEP, grouped by height."""
import sys
from collections import defaultdict

from build123d import import_step

s = import_step(sys.argv[1])
zmin = s.bounding_box().min.Z
groups = defaultdict(float)
for f in s.faces():
    try:
        n = f.normal_at(f.center())
    except Exception:
        continue
    c = f.center()
    if n.Z < -0.72 and c.Z > zmin + 0.05:
        groups[(round(c.Z, 1), f.geom_type.name, round(c.X), round(c.Y))] += f.area
for k, a in sorted(groups.items(), key=lambda kv: -kv[1])[:25]:
    print(k, round(a, 1))
