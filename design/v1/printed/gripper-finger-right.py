"""Idler gripper finger (-Y side): mirror of the driven finger, gear turns on the base's 8 mm
printed axle boss (bore 8.4, printed-on-printed running +0.4) under an M3 x 12 mm OD fender washer.
G frame, closed pose. Printed upside down."""
import importlib.util
from pathlib import Path

from build123d import *

from features import export_printed
from gripper_layout import *

HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location("fl", HERE / "gripper-finger-left.py")
src = (HERE / "gripper-finger-left.py").read_text().split("part = finger(SIDE)")[0]   # reuse finger()
ns = {"__file__": str(HERE / "gripper-finger-left.py")}
exec(compile(src, "gripper-finger-left.py", "exec"), ns)
AXLE_BORE = 8.4

with BuildPart() as fr:
    add(ns["finger"](-1))
    with Locations((X_S, -PIVOT_Y, Z_GEAR)):
        Cylinder(AXLE_BORE / 2, 3 * GEAR_T, mode=Mode.SUBTRACT)

export_printed(fr.part, "gripper-finger-right", rot=(180, 0, 0), here=HERE)
