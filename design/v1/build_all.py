"""Build every printed part of v1 (or the ones named on the command line) and print-check it.

python design/v1/build_all.py [part ...]
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
PRINTED = HERE / "printed"
ROOT = HERE.parents[1]
SKIP = {"layout", "style", "features", "gripper_layout"}

names = sys.argv[1:] or sorted(p.stem for p in PRINTED.glob("*.py") if p.stem not in SKIP)
results = {}
for n in names:
    r = subprocess.run([sys.executable, str(PRINTED / f"{n}.py")], cwd=PRINTED, capture_output=True, text=True)
    out = "\n".join(l for l in (r.stdout + r.stderr).splitlines() if "Deprecat" not in l and "add(" not in l)
    if r.returncode:
        print(f"== {n}: BUILD FAILED\n{out[-3000:]}")
        results[n] = "failed"
        continue
    pc = subprocess.run([sys.executable, "-m", "mechy.design_tools", "printcheck", str(PRINTED / f"{n}.step")],
                        cwd=ROOT, capture_output=True, text=True)
    try:
        d = json.loads(pc.stdout)
        axes = [o["axes"] for o in d["fitting_orientations"]]
        info = {k: d[k] for k in ("min_wall_mm", "thin_walls", "overhang_area_mm2", "small_holes")}
        info["xyz_fits"] = "xyz" in axes
    except Exception:
        info = pc.stdout[-500:] + pc.stderr[-500:]
    results[n] = info
    print(f"== {n}: {out.strip()}\n   {info}")
