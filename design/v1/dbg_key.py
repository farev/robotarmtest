"""Debug: where does the J2 key keep-out touch the stage-1 belt in the service-j2 pose?"""
from pathlib import Path

import numpy as np
import yaml
from build123d import Extrinsic, Location, Rotation, import_step

ROOT = Path(__file__).parents[2]
asm = yaml.safe_load((Path(__file__).parent / "poses/service-j2/assembly.yaml").read_text())
P = {p["id"]: p for p in asm["parts"]}


def load(pid):
    p = P[pid]
    return import_step(str(ROOT / p["model"])).moved(Location(tuple(p["position"])) * Rotation(*p["rotation"], ordering=Extrinsic.XYZ))


belt, key, mot, pul = load("belt-s1"), load("screw-j2-2-key-keepout"), load("motor-j2"), load("pulley-s1-60t")
i = belt.intersect(key)
i = list(i) if isinstance(i, list) or hasattr(i, "__iter__") else [i]
for s in i:
    print("overlap piece", round(s.volume, 3), "bbox", s.bounding_box())
print("belt bbox", belt.bounding_box())
print("key bbox", key.bounding_box())
print("motor centre", mot.bounding_box().center(), "60T centre", pul.bounding_box().center())
