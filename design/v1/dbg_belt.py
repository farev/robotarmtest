"""Debug: probe the stage-1 belt model in its own frame (u = UA x, v = UA z)."""
from build123d import Box, Location, import_step

b = import_step("/Users/fabianarevalo/Mechy Projects/robotarmtest/parts/models/belt-s1-gt2-158.step")
print(b.bounding_box())
for x in (-64, -62, -60, -58, -57, -56, -54):
    p = Box(0.1, 0.1, 0.1).moved(Location((x, -20.71, 0)))
    r = b.intersect(p)
    v = sum(s.volume for s in r) if r else 0
    print(x, "inside belt" if v > 0 else "-")
