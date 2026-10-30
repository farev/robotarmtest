import sys
sys.path.insert(0, "/Users/fabianarevalo/Mechy Projects/robotarmtest/design/v1/printed")
from build123d import *
from features import export_printed, hull_sketch, circle_pts
from layout import *
from style import *

print("extrude is", extrude.__module__, "add is", add.__module__, "Plane", Plane)
pack = hull_sketch(pack_points())


def PXZ(y):
    return Plane(origin=(0, y, 0), x_dir=(1, 0, 0), z_dir=(0, -1, 0))


with BuildPart() as p:
    with BuildSketch(PXZ(Y_PACK_IN)) as s:
        add(pack)
    print("pending", len(p.pending_faces))
    extrude(amount=4)
print(p.part.bounding_box())
