"""Yaw-bearing fit coupon: 6806 pockets 42.0 / 42.1 / 42.2 / 42.3 (7 deep, design 42.1) and
turret-spigot pegs 29.75 / 29.85 / 29.95 / 30.05 (design 29.85, slides into the 30 mm inner ring):
design value - 0.1 .. + 0.2 (rules §9). Notches on the front edge = column 1..4, smallest first.
Print before base-deck and turret-hub."""
from pathlib import Path

from build123d import *

from features import export_printed
from layout import *

HERE = Path(__file__).parent
T = 9.0
P = 52.0
N = 4
W, H = N * P + 4, 2 * P

with BuildPart() as c:
    with Locations((W / 2, H / 2, 0)):
        Box(W, H, T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for i, d in enumerate([42.0, 42.1, 42.2, 42.3]):
        with Locations((2 + P * i + P / 2, P * 1.5, T)):
            Hole(d / 2, 7.0)
    for i, d in enumerate([29.75, 29.85, 29.95, 30.05]):
        with Locations((2 + P * i + P / 2, P / 2, T)):
            Cylinder(d / 2, 7.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for i in range(N):
        for k in range(i + 1):
            with Locations((2 + P * i + P / 2 + (k - i / 2) * 3.0, 0, T / 2)):
                Box(1.2, 2.0, T + 1, mode=Mode.SUBTRACT)

export_printed(c.part, "coupon-yaw", here=HERE)
