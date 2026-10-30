"""Fit-test coupon (rules §9): print first, in the same material and orientation as the parts.
Rows, left to right = smallest to largest; the number of notches on the front edge = column 1..4.
  row A: 608 pocket 22.0 / 22.1 / 22.2 / 22.3 (7 deep)  -> FIT_608 (design uses 22.1)
  row B: 625 pocket 16.0 / 16.1 / 16.2 / 16.3 (5 deep)  -> FIT_625 (16.1)
  row C: M3 insert hole 3.9 / 4.0 / 4.1 / 4.2          -> M3_INSERT (4.0)
  row D: 8 mm rod 8.1 / 8.2 / 8.3 / 8.4 through         -> ROD8_CLAMP (8.2, snug, vertical holes)
  plus a GT2 40T printed tooth stub (belt test) at the right.
Tell me which size fitted and I will update layout.py; every part follows."""
from pathlib import Path

from build123d import *

from features import export_printed, gt2_band
from layout import *

HERE = Path(__file__).parent
T = 10.0
ROWS = [("A", [22.0, 22.1, 22.2, 22.3], 7.0, 32.0), ("B", [16.0, 16.1, 16.2, 16.3], 5.0, 24.0),
        ("C", [3.9, 4.0, 4.1, 4.2], 6.7, 12.0), ("D", [8.1, 8.2, 8.3, 8.4], 100.0, 16.0)]   # design value - 0.1 .. + 0.2 (§9)
NCOL = 4
W = NCOL * 32.0 + 8
H = sum(r[3] for r in ROWS) + 8

with BuildPart() as c:
    with Locations((W / 2, H / 2, 0)):
        Box(W, H, T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    y = 4.0
    for name, sizes, depth, pitch in ROWS:
        yc = y + pitch / 2
        for i, d in enumerate(sizes):
            with Locations((4 + 32.0 * i + 16.0, yc, T)):
                Hole(d / 2, min(depth, 100))
        y += pitch
    for i in range(NCOL):                                # column notches on the front edge
        for k in range(i + 1):
            with Locations((4 + 32.0 * i + 16.0 + (k - i / 2) * 3.0, 0, T / 2)):
                Box(1.2, 2.0, T + 1, mode=Mode.SUBTRACT)
    add(gt2_band(40).moved(Location((W + 11.5, H / 2, 0))))   # overlaps the plate edge: one solid

export_printed(c.part, "coupon-fits", here=HERE)
