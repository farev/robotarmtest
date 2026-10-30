"""The two fingers are allowed to touch in the assembly check (gear mesh), so check them here:
overlap volume outside the gear band, and the closed-pad gap. G frame, closed pose."""
import sys
from pathlib import Path

import numpy as np
from build123d import Box, Location, Matrix, import_step

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE / "printed")); sys.path.insert(0, str(HERE))
import gripper_layout as G
from make_assembly import printed_local


def load(n):
    s = import_step(str(HERE / "printed" / f"{n}.step"))
    return s.transform_geometry(Matrix(printed_local(n).tolist())) if hasattr(s, "transform_geometry") else s.moved(Location(Matrix(printed_local(n).tolist())))


L, R = load("gripper-finger-left"), load("gripper-finger-right")
inter = L.intersect(R)
v = inter.volume if inter else 0.0
print("total overlap mm3:", round(v, 3))
# overlap outside the mesh zone (|y| < 3 around the pitch point at x = X_S, gear band z)
mesh = Box(20, 8, 40).moved(Location((G.X_S, 0, G.Z_GEAR)))
outside = inter.cut(mesh) if inter and v > 0 else None
print("overlap outside the gear mesh zone mm3:", round(outside.volume, 3) if outside else 0.0)
bl, br = L.bounding_box(), R.bounding_box()
print("left min y", round(bl.min.Y, 2), "right max y", round(br.max.Y, 2))
