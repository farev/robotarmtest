"""Belts are allowed to touch the printed part carrying their toothed band (allow_contact), which would also hide a
clash with the rest of that part. The belt models sit exactly on the tooth tips (inner face = pulley OD) and are
6 mm wide inside an 8 mm toothed band, so a correct belt overlaps its part by ~0 mm3. Anything more is a clash.

python design/v1/check_belts.py      (every pose file; prints the overlap volume per belt/part pair)
"""
from pathlib import Path

import yaml
from build123d import Extrinsic, Location, Rotation, import_step

HERE = Path(__file__).parent
ROOT = HERE.parents[1]
PAIRS = [("belt-j1", "turret-hub"), ("belt-s2", "shoulder-pulley-80t"), ("belt-j3", "elbow-pulley-120t")]
LIMIT = 0.5   # mm3: tessellation / boolean noise


def load(p):
    s = import_step(str(ROOT / p["model"]))
    return s.moved(Location(tuple(p["position"])) * Rotation(*p["rotation"], ordering=Extrinsic.XYZ))


def vol(shape):
    if shape is None:
        return 0.0
    if isinstance(shape, list) or type(shape).__name__ == "ShapeList":
        return sum(s.volume for s in shape)
    return shape.volume


bad = 0
for f in [HERE / "assembly.yaml"] + sorted((HERE / "poses").glob("*/assembly.yaml")):
    P = {p["id"]: p for p in yaml.safe_load(f.read_text())["parts"]}
    name = "home" if f.parent == HERE else f.parent.name
    for b, part in PAIRS:
        if b in P and part in P:
            v = vol(load(P[b]).intersect(load(P[part])))
            flag = "CLASH" if v > LIMIT else "ok"
            bad += v > LIMIT
            print(f"{name:14s} {b:8s} x {part:20s} {v:9.3f} mm3  {flag}")
print("belt clashes:", bad)
