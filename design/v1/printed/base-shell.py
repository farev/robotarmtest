"""Base shell: round tub that houses the J1 motor (hanging from the deck) and the Uno + CNC shield.
Printed floor down, as assembled (base frame = world at q1 = 0)."""
import math
from pathlib import Path

import yaml
from build123d import *

from features import export_printed, teardrop
from layout import *
from style import *

HERE = Path(__file__).parent
U = {d["name"]: d["value_mm"] for d in yaml.safe_load((ROOT / "parts/models/uno-cnc-shield.yaml").read_text())["critical_dims"]}

R_OUT = BASE_D / 2
R_IN = R_OUT - BASE_WALL
H = Z_DECK_BOT                       # shell top rim = deck underside
STANDOFF_H = 6.0                     # Uno PCB underside 6 mm above the floor
UNO_X0 = -107.0                      # Uno x = 0 edge (USB/jack edge) at the rear wall
UNO_Y0 = -U["uno pcb width"] / 2
Z_PCB = BASE_FLOOR + STANDOFF_H
DECK_BOSS_ANG = [30 + 60 * k for k in range(6)]
DECK_BOSS_R = R_IN - 3.5
MOUNT_R, MOUNT_ANG = 100.0, [45, 135, 225, 315]   # M5 screws or clamps into the table
M5_CLEAR = 5.8                       # rules §2


def uno_xy(name):
    return (UNO_X0 + U[f"{name} x"], UNO_Y0 + U[f"{name} y"])


def radial_hole(ang_deg, z, d):
    """Radial teardrop through the wall (45 deg roof up: holes > 8 mm print without support, rules §5)."""
    a = math.radians(ang_deg)
    c = R_OUT - BASE_WALL / 2
    pl = Plane(origin=(c * math.cos(a), c * math.sin(a), z), x_dir=(-math.sin(a), math.cos(a), 0),
               z_dir=(math.cos(a), math.sin(a), 0))
    return teardrop(d / 2, 6 * BASE_WALL, pl)


with BuildPart() as shell:
    Cylinder(R_OUT, H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    with Locations((0, 0, BASE_FLOOR)):
        Cylinder(R_IN, H, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
    # deck bosses: M3 inserts from the top rim (rules §3: boss >= 8, hole 4.0 x 6.7)
    with Locations(*[(DECK_BOSS_R * math.cos(math.radians(a)), DECK_BOSS_R * math.sin(math.radians(a)), 0)
                     for a in DECK_BOSS_ANG]):
        Cylinder(M3_BOSS / 2 + 1, H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    with Locations(*[(DECK_BOSS_R * math.cos(math.radians(a)), DECK_BOSS_R * math.sin(math.radians(a)), H)
                     for a in DECK_BOSS_ANG]):
        Hole(M3_INSERT[0] / 2, M3_INSERT[1])
    # Uno standoffs with M3 inserts
    holes = [uno_xy(f"mount hole {i}") for i in (1, 2, 3, 4)]
    with Locations(*[(x, y, BASE_FLOOR) for x, y in holes]):
        Cylinder(M3_BOSS / 2, STANDOFF_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    with Locations(*[(x, y, Z_PCB) for x, y in holes]):
        Hole(M3_INSERT[0] / 2, M3_INSERT[1])
    # table mounting: M5 clearance through the floor, screwed from inside before the deck goes on
    with Locations(*[(MOUNT_R * math.cos(math.radians(a)), MOUNT_R * math.sin(math.radians(a)), BASE_FLOOR)
                     for a in MOUNT_ANG]):
        Hole(M5_CLEAR / 2)
    # rear panel (-X): USB-B window on the Uno, 11.3 mm panel DC jack (Vetco 321B needs 11.1),
    # 22.3 mm mushroom E-stop cutting motor power (IDEC HW1B: 22.3 cut-out)
    usb_y = UNO_Y0 + U["usb-b center y"]
    usb_z = Z_PCB + U["uno pcb thickness"] + U["usb-b height"] / 2
    with Locations((-R_OUT, usb_y, usb_z)):
        Box(4 * BASE_WALL, U["usb-b width"] + 2.0, U["usb-b height"] + 2.0, mode=Mode.SUBTRACT)
    add(radial_hole(180 + math.degrees(math.asin(-40 / R_OUT)), 32, 11.3), mode=Mode.SUBTRACT)
    add(radial_hole(180 + math.degrees(math.asin(-72 / R_OUT)), 30, 22.3), mode=Mode.SUBTRACT)
    # side vents beside the drivers: radial slots 3 x 26
    for a in [125, 133, 141, 219, 227, 235]:
        r = math.radians(a)
        with Locations(Location((R_OUT * math.cos(r), R_OUT * math.sin(r), 14 + 13), (0, 0, a))):
            Box(4 * BASE_WALL, 3.0, 26.0, mode=Mode.SUBTRACT)
    # floor vents under the drivers
    with Locations(*[(x, 0, 0) for x in (-88, -80, -72, -64, -56)]):
        Box(3.0, 34.0, 2 * BASE_FLOOR + 0.1, mode=Mode.SUBTRACT)

part = shell.part
part = try_chamfer(part, part.edges().filter_by(Plane.XY).group_by(Axis.Z)[0].filter_by(GeomType.CIRCLE).sort_by(SortBy.RADIUS)[-1:], C_BED)
export_printed(part, "base-shell", here=HERE)
