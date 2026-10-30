"""Find shoulder angles where every J2 motor-screw key path (Ø5, along -Y) misses the tower's XZ outline."""
import math
import sys
from pathlib import Path

import numpy as np
from scipy.spatial import ConvexHull

sys.path.insert(0, str(Path(__file__).parent / "printed"))
from layout import J2_XZ, NEMA_PITCH, Z_SH, Z_TUR_TOP, TOWER_FOOT_X

pts = [(x, z) for x in TOWER_FOOT_X for z in (Z_TUR_TOP, Z_TUR_TOP + 6)]
pts += [(30 * math.cos(a), Z_SH + 30 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 72)]
# gussets reach 132 at x +-40 (+-2.5) - inside the hull of the foot and head anyway
hull = np.array(pts)[ConvexHull(np.array(pts)).vertices]


def dist_out(p):
    """Signed distance from p to the convex outline (positive outside)."""
    d = -1e9
    for i in range(len(hull)):
        a, b = hull[i], hull[(i + 1) % len(hull)]
        e = b - a; n = np.array([e[1], -e[0]]) / np.linalg.norm(e)
        d = max(d, float(np.dot(p - a, n)))
    return d


for q in range(-30, 91, 5):
    c, s = math.cos(math.radians(q)), math.sin(math.radians(q))
    worst = 1e9
    for sx in (-1, 1):
        for sz in (-1, 1):
            x, z = J2_XZ[0] + sx * NEMA_PITCH / 2, J2_XZ[1] + sz * NEMA_PITCH / 2
            p = np.array([x * c - z * s, x * s + z * c + Z_SH])
            worst = min(worst, dist_out(p) - 2.5)
    print(q, round(worst, 1), "OK" if worst > 1 else "")
