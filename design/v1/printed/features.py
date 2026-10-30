"""Shared printed features: GT2 toothed bands, involute spur gears, 2D hulls, teardrops."""
from __future__ import annotations

import math

import numpy as np
from build123d import *
from scipy.spatial import ConvexHull

from layout import FLANGE_T, TEETH_W, od, pd

# GT2 groove approximation (Gates 2MGT: tooth height 0.75, tip radius 0.555) [typ];
# printed teeth are checked with the coupon pulley before the big parts.
GT2_GROOVE_R = 0.555
GT2_GROOVE_DEPTH = 0.76


def gt2_profile(teeth: int) -> Sketch:
    """Top-view sketch of a GT2 pulley of `teeth` teeth (centred, XY)."""
    R = od(teeth) / 2
    rc = R - GT2_GROOVE_DEPTH + GT2_GROOVE_R
    with BuildSketch(mode=Mode.PRIVATE) as s:      # PRIVATE: never leaks into a caller's builder
        Circle(R)
        with PolarLocations(rc, teeth):
            Circle(GT2_GROOVE_R, mode=Mode.SUBTRACT)
        with PolarLocations((rc + R + 1) / 2, teeth):
            Rectangle(R + 1 - rc, 2 * GT2_GROOVE_R, mode=Mode.SUBTRACT)
    return s.sketch


def gt2_band(teeth: int, bore: float = 0.0, bottom_flange=True, top_flange=True, bottom_cone=False) -> Part:
    """Toothed band along +Z from z = 0: flange, TEETH_W of teeth, flange.
    The top flange is a 45 deg cone widening upward (prints without support when the band is
    printed this way up). bottom_cone=True makes the bottom flange a cone widening downward,
    for bands printed upside down."""
    R = od(teeth) / 2
    Rf = R + 0.9 * FLANGE_T    # cone a little steeper than 45 deg so it never counts as overhang
    z = 0.0
    with BuildPart(mode=Mode.PRIVATE) as p:
        if bottom_flange:
            if bottom_cone:
                Cone(Rf, R, FLANGE_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
            else:
                Cylinder(Rf, FLANGE_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
            z += FLANGE_T
        with BuildSketch(Plane.XY.offset(z)):
            add(gt2_profile(teeth))
        extrude(amount=TEETH_W)
        z += TEETH_W
        if top_flange:
            with Locations((0, 0, z)):
                Cone(R, Rf, FLANGE_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
        if bore:
            Cylinder(bore / 2, 100, mode=Mode.SUBTRACT)
    return p.part


def band_height(bottom_flange=True, top_flange=True):
    return TEETH_W + FLANGE_T * (int(bottom_flange) + int(top_flange))


def involute_gear(module: float, teeth: int, thickness: float, pressure_deg=20.0, backlash=0.1,
                  addendum=1.0) -> Part:
    """Spur gear along +Z from z = 0, involute flanks, `backlash` (mm on the pitch circle) removed
    from each tooth for printed-on-printed running (rules §1: 0.2 per side is for sliding; gears
    run on a backlash of 0.1-0.2 [typ])."""
    a = math.radians(pressure_deg)
    rp = module * teeth / 2
    rb = rp * math.cos(a)
    ra = rp + addendum * module          # addendum < 1 widens the printed tip land
    rf = rp - 1.25 * module
    # half tooth angle at the pitch circle, minus backlash
    half = math.pi / (2 * teeth) - (backlash / 2) / rp
    inv = lambda t: math.tan(t) - t
    phi_p = inv(a)
    pts = []
    n = 12
    r_start = max(rb, rf)
    flank = []
    for i in range(n + 1):
        r = r_start + (ra - r_start) * i / n
        t = math.acos(min(1.0, rb / r))
        ang = half + phi_p - inv(t)          # angle of the flank at radius r (right flank, +)
        flank.append((r, ang))
    a0 = flank[0][1]
    tooth = [(rf * math.cos(-a0), rf * math.sin(-a0))]                       # root, left side
    tooth += [(r * math.cos(-t), r * math.sin(-t)) for r, t in flank]         # left flank, up
    tooth += [(r * math.cos(t), r * math.sin(t)) for r, t in reversed(flank)] # right flank, down
    tooth += [(rf * math.cos(a0), rf * math.sin(a0))]                         # root, right side
    outline = []
    for k in range(teeth):
        th = 2 * math.pi * k / teeth
        c, s = math.cos(th), math.sin(th)
        outline += [(x * c - y * s, x * s + y * c) for x, y in tooth]
    with BuildPart(mode=Mode.PRIVATE) as g:
        with BuildSketch():
            Polygon(*outline)
        extrude(amount=thickness)
    return g.part


def hull_sketch(points, plane=Plane.XY) -> Sketch:
    """Convex hull polygon of 2D points on `plane`."""
    pts = np.array(points, dtype=float)
    h = ConvexHull(pts)
    poly = [tuple(pts[i]) for i in h.vertices]
    with BuildSketch(plane, mode=Mode.PRIVATE) as s:
        Polygon(*poly)
    return s.sketch


def circle_pts(cx, cy, r, n=48):
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def rect_pts(cx, cy, hx, hy):
    return [(cx - hx, cy - hy), (cx + hx, cy - hy), (cx + hx, cy + hy), (cx - hx, cy + hy)]


def bed_bearing_pocket(fit_d: float, depth: float, ledge_d: float, bore_d: float) -> Part:
    """Cutter for a bearing pocket that opens on the bed face (local +Z from z = 0): the press
    bore, then a narrow ledge (seats the outer ring; <= 2 mm overhang) and a 45 deg cone down to
    the shaft bore so the pocket ceiling prints without support."""
    h_cone = (ledge_d - bore_d) / 2
    with BuildPart(mode=Mode.PRIVATE) as c:
        Cylinder(fit_d / 2, depth, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations((0, 0, depth)):
            Cone(ledge_d / 2, bore_d / 2, h_cone, align=(Align.CENTER, Align.CENTER, Align.MIN))
        Cylinder(bore_d / 2, 1000)
    return c.part


def export_printed(part_asm: Part, name: str, rot=(0.0, 0.0, 0.0), here=None):
    """Rotate an as-assembled part into its print orientation (extrinsic XYZ degrees), drop it on
    the bed (min z = 0), export printed/<name>.step and printed/<name>.place.json with the
    transform back to the as-assembled frame (assembly builder inverts it)."""
    import json
    from pathlib import Path

    from scipy.spatial.transform import Rotation as R

    here = Path(here) if here else Path(__file__).parent
    Rm = R.from_euler("xyz", rot, degrees=True).as_matrix()
    p = part_asm.rotate(Axis.X, rot[0]).rotate(Axis.Y, rot[1]).rotate(Axis.Z, rot[2])
    bb = p.bounding_box()
    t = (0.0, 0.0, -bb.min.Z)
    p = p.moved(Location(t))
    export_step(p, str(here / f"{name}.step"))
    (here / f"{name}.place.json").write_text(json.dumps({"R": Rm.tolist(), "t": list(t)}, indent=1))
    bb = p.bounding_box()
    print(f"{name}: print bbox {bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f}, solids {len(p.solids())}")
    return p


def teardrop(r: float, length: float, axis_plane: Plane) -> Part:
    """Horizontal hole of radius r with a 45 deg roof (prints without support), extruded both ways
    `length`/2 along the plane normal; the roof points along the plane's +Y (set it to print +Z)."""
    with BuildPart(mode=Mode.PRIVATE) as t:
        with BuildSketch(axis_plane):
            Circle(r)
            with Locations((0, r * 0.7071 / 2)):
                Rectangle(r * 1.4142, r * 0.7071)
            pts = [(-r * 0.7071, r * 0.7071), (r * 0.7071, r * 0.7071), (0, r * 1.4142)]
            Polygon(*pts)
        extrude(amount=length / 2, both=True)
    return t.part
