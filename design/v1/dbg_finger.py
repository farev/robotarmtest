"""Debug: print-check pieces of the finger to find the thin wall."""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "printed"))
from build123d import *
from features import involute_gear, hull_sketch, circle_pts
from gripper_layout import *

out = Path("/tmp/fdbg"); out.mkdir(exist_ok=True)
pieces = {
    "gear": involute_gear(GEAR_M, GEAR_Z, GEAR_T, addendum=GEAR_ADD),
    "gear_full": involute_gear(GEAR_M, GEAR_Z, GEAR_T),
}
with BuildPart() as pad:
    Box(8, 6, 32)
    for z in range(-13, 15, 3):
        with Locations((0, -2.8, z)):
            Box(8.2, 2.0, 1.0, mode=Mode.SUBTRACT)
pieces["pad"] = pad.part
for n, p in pieces.items():
    f = out / f"{n}.step"
    export_step(p, str(f))
    r = subprocess.run([sys.executable, "-m", "mechy.design_tools", "printcheck", str(f)], capture_output=True, text=True)
    d = json.loads(r.stdout)
    print(n, d["min_wall_mm"], d["thin_walls"])
