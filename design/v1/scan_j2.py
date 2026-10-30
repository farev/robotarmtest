"""Scan J2 motor placement (stage-1 loop, J2_ANGLE) for hex-key access: every J2 screw-key path (Ø5) must clear
the 60T flange (r 22, Olimex value) and the stage-1 belt band (outer surface) by >= 0.5 mm."""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "printed"))
from layout import pd, od, centre_for_loop, NEMA_PITCH

KEY_R, FL60 = 2.5, 22.0
r20o, r60o = od(20) / 2 + 1.4, od(60) / 2 + 1.4        # belt outer surface radii


def seg_dist(p, a, b):
    ax, ay = b[0] - a[0], b[1] - a[1]
    t = max(0, min(1, ((p[0] - a[0]) * ax + (p[1] - a[1]) * ay) / (ax * ax + ay * ay)))
    return math.hypot(p[0] - a[0] - t * ax, p[1] - a[1] - t * ay)


for L in (158, 160, 180, 200):
    C = centre_for_loop(L, pd(60), pd(20))
    for ang in range(200, 341, 5):
        a = math.radians(ang)
        m = (C * math.cos(a), C * math.sin(a))            # motor relative to the intermediate shaft
        # external tangent lines of the two belt-outer circles (belt band = hull of the circles)
        d = C; phi = math.atan2(m[1], m[0]); beta = math.asin((r60o - r20o) / d)
        worst = 99
        for s in (-1, 1):
            n = phi + s * (math.pi / 2 - beta)       # outward normal of the external tangent (n.(c2-c1) = r1 - r2)
            p1 = (r60o * math.cos(n), r60o * math.sin(n)); p2 = (m[0] + r20o * math.cos(n), m[1] + r20o * math.sin(n))
            for sx in (-1, 1):
                for sz in (-1, 1):
                    h = (m[0] + sx * NEMA_PITCH / 2, m[1] + sz * NEMA_PITCH / 2)
                    inside = (math.hypot(*h) < r60o) or (math.hypot(h[0] - m[0], h[1] - m[1]) < r20o)
                    gb = seg_dist(h, p1, p2) - KEY_R
                    g60 = math.hypot(*h) - FL60 - KEY_R
                    worst = min(worst, gb if not inside else -1, g60)
        if worst > 0.5:
            print(f"loop {L} C {C:.2f} angle {ang}: worst clearance {worst:.2f}")
