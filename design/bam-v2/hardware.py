"""Purchased hardware solids and their placements for bam-v2 (mm).

Screws, nuts and bearings use nominal ISO 4762 / ISO 4032 / catalogue dimensions; threads are
plain cylinders. Each local frame puts the bearing face at z=0 and the body along +Z (screws:
head on +Z, shank toward -Z). Upper-arm placements are in the vendor STEP frame of the
20sffactory arm, measured from the cylindrical bores of its printed parts (see probe notes in
summary.md); they are moved into the GLB node frames with the same pipeline as the vendor meshes.
"""
import math
import numpy as np
from build123d import *

SHCS = {3: (5.5, 3.0, 2.5), 4: (7.0, 4.0, 3.0), 6: (10.0, 6.0, 5.0)}   # head d, head h, hex key
NUT = {3: (5.5, 2.4), 4: (7.0, 3.2), 6: (10.0, 5.0)}                   # across flats, height
FLANGED = {'F624ZZ': (4, 13, 5, 15, 1.0), 'F686ZZ': (6, 13, 5, 15, 1.1)}  # d, D, B, flange D, flange B

def _cyl(r, h, z=0):
    return Pos(0, 0, z) * Cylinder(r, h, align=(Align.CENTER, Align.CENTER, Align.MIN))

def shcs(d, length):
    dk, k, s = SHCS[d]
    head = _cyl(dk/2, k) - Pos(0, 0, k - 0.6*k) * extrude(RegularPolygon(s/math.sqrt(3), 6), amount=0.6*k + 0.1)
    head = chamfer(head.edges().filter_by(GeomType.CIRCLE).sort_by(Axis.Z)[-1], 0.08*dk)
    return head + _cyl(d/2, length, -length)

def csk(d, length, head_d=5.7, head_h=1.35):
    """Countersunk screw with its flat head top at z=0, shank toward -Z (overall length)."""
    return _cyl(d/2, length - head_h, -length) + Pos(0, 0, -head_h) * Cone(
        d/2, head_d/2, head_h, align=(Align.CENTER, Align.CENTER, Align.MIN))

def nut(d, height=None):
    af, m = NUT[d]
    m = height or m
    # Bore at the thread minor diameter, so screw-in-nut overlap stands for thread engagement.
    return extrude(RegularPolygon(af/math.sqrt(3), 6), amount=m) - _cyl(0.4*d, m + 0.2, -0.1)

def heatset_m3(od=4.6, length=5.7):
    """M3 brass heat-set insert, top face at z=0, body toward +Z (flip to sink it into a part)."""
    s = _cyl(od/2, length) - _cyl(1.2, length + 0.2, -0.1)
    for z in (1.2, 3.4):
        s -= _cyl(od/2 + 0.1, 0.8, z) - _cyl(od/2 - 0.3, 1.0, z - 0.1)
    return s

def washer(d, od, t):
    return _cyl(od/2, t) - _cyl(d/2 + 0.2, t + 0.2, -0.1)

def flanged_bearing(kind):
    """Flanged ball bearing: flange face at z=0, ring along +Z; shield grooves on both faces."""
    d, D, B, Df, Bf = FLANGED[kind]
    s = _cyl(D/2, B) + _cyl(Df/2, Bf) - _cyl(d/2, B + 0.2, -0.1)
    ri, ro = d/2 + 1.2, D/2 - 1.0
    for z in (-0.1, B - 0.3):
        s -= _cyl(ro, 0.4, z) - _cyl(ri, 0.6, z - 0.1)
    return s

def thrust_51105():
    """51105 thrust ball bearing, 25 x 42 x 11, bottom (housing washer) face at z=0."""
    housing = _cyl(21.0, 3.5) - _cyl(13.25, 3.7, -0.1)
    shaft = _cyl(20.5, 3.5, 7.5) - _cyl(12.5, 3.7, 7.4)
    cage = _cyl(19.2, 3.0, 4.0) - _cyl(14.4, 3.2, 3.9)
    s = housing + shaft + cage
    for i in range(12):
        a = math.radians(i * 30)
        s += Pos(16.8*math.cos(a), 16.8*math.sin(a), 5.5) * Sphere(2.2)
    return s

def belt_profile(ra, rb, centre, n=96):
    """Points of the hull of circle ra at (0,0) and circle rb at (0,centre), counter-clockwise."""
    al = math.asin((rb - ra) / centre)
    pts = [(rb*math.cos(t), centre + rb*math.sin(t)) for t in np.linspace(-al, math.pi + al, n)]
    pts += [(ra*math.cos(t), ra*math.sin(t)) for t in np.linspace(math.pi + al, 2*math.pi - al, n // 3)[1:-1]]
    return pts

def belt(r_small_tip, r_big_tip, centre, width=6.0, back=0.9, gap=0.1):
    """Closed GT2 belt band riding on the pulley tips (teeth not modelled), in local XY, along +Z."""
    inner = Polygon(*belt_profile(r_small_tip + gap, r_big_tip + gap, centre), align=None)
    outer = Polygon(*belt_profile(r_small_tip + gap + back, r_big_tip + gap + back, centre), align=None)
    return extrude(outer - inner, amount=width)

def gt2_length(z1, z2, centre):
    """Pitch length of a GT2 loop over two pulleys (mm)."""
    r1, r2 = z1*2/(2*math.pi), z2*2/(2*math.pi)
    return 2*centre + math.pi*(r1 + r2) + (r2 - r1)**2/centre

def frame(z_dir, x_hint=(1, 0, 0)):
    """Rotation matrix whose columns are the local x, y, z axes in the parent frame."""
    z = np.asarray(z_dir, float); z /= np.linalg.norm(z)
    x = np.asarray(x_hint, float)
    if abs(x @ z) > 0.9:
        x = np.array([0.0, 0.0, 1.0]) if abs(z[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
    x = x - (x @ z) * z; x /= np.linalg.norm(x)
    return np.column_stack([x, np.cross(z, x), z])

def euler_xyz(Rm):
    """Extrinsic X, Y, Z angles (deg) of a rotation matrix (assembly.yaml convention)."""
    sy = -Rm[2, 0]
    y = math.asin(max(-1.0, min(1.0, sy)))
    if abs(math.cos(y)) > 1e-9:
        x = math.atan2(Rm[2, 1], Rm[2, 2]); z = math.atan2(Rm[1, 0], Rm[0, 0])
    else:
        x = math.atan2(-Rm[1, 2], Rm[1, 1]); z = 0.0
    return [round(math.degrees(v), 6) for v in (x, y, z)]

# ------------------------------------------------------------------ upper-arm placements
# Vendor STEP frame pivots (x, z); every axle runs along Y.
PIV = {'S': (100.0, 62.5), 'E': (11.685, 143.744), 'W': (119.541, 196.348), 'L': (64.048, 44.965),
       'PU': (-24.381, 126.084), 'B0': (70.0, 74.5), 'TL': (-18.315, 155.744),
       'T2': (26.685, 163.744), 'T3': (134.53, 216.371)}
Y_POS, Y_NEG = (0, 1, 0), (0, -1, 0)

def _at(p, y):
    x, z = PIV[p]
    return (x, y, z)

# (id, model key, node group, origin, z_dir, BOM label, note)
UPPER = [
    # Pivot axles. Each is clamped to the part named in the note; bearings turn on it.
    ('shoulder-axle-m6x50', ('shcs', 6, 50), 'turntable', _at('S', -27.0), Y_POS, 'M6x50 socket head screw',
     'head in main-body counterbore; carries both 90T pulleys, lower shank and lever'),
    ('shoulder-axle-nut', ('nut', 6), 'turntable', _at('S', -71.0), Y_NEG, 'M6 nut', 'opposite main-body counterbore'),
    ('elbow-axle-m6x40', ('shcs', 6, 40), 'upper_arm', _at('E', -39.0), Y_POS, 'M6x40 socket head screw',
     'clamped in the lower-shank fork; upper shank and triplate turn on it'),
    ('elbow-axle-nut', ('nut', 6), 'upper_arm', _at('E', -71.6), Y_NEG, 'M6 nut', 'outside the triplate'),
    ('wrist-axle-m6x40', ('shcs', 6, 40), 'hand', _at('W', -66.0), Y_NEG, 'M6x40 socket head screw',
     'head in manipulator counterbore; upper shank turns on it'),
    ('wrist-axle-nut', ('nut', 6), 'hand', _at('W', -34.0), Y_POS, 'M6 nut', 'outside the manipulator cheek'),
    ('lever-pin-m4x20', ('shcs', 4, 20), 'lever', _at('L', -49.6), Y_NEG, 'M4x20 socket head screw',
     'lever to pleuel; clamps the pleuel bearing inner ring'),
    ('lever-pin-nut', ('nut', 4), 'lever', _at('L', -35.5), Y_POS, 'M4 nut', 'on the lever face'),
    ('pleuel-pin-m4x16', ('shcs', 4, 16), 'forearm', _at('PU', -43.4), Y_POS, 'M4x16 socket head screw',
     'pleuel to upper shank; threads into the 3.76 mm upper-shank hole'),
    ('bend-lower-pin-m4x10', ('shcs', 4, 10), 'turntable', _at('B0', -81.1), Y_NEG, 'M4x10 socket head screw',
     'lower levelling link to main body; threads into the 3.86 mm main-body hole'),
    ('triplate-lower-pin-m4x20', ('shcs', 4, 20), 'triplate', _at('TL', -81.1), Y_NEG, 'M4x20 socket head screw',
     'lower levelling link to triplate'),
    ('triplate-lower-pin-nut', ('nut', 4), 'triplate', _at('TL', -67.5), Y_POS, 'M4 nut',
     'in the triplate 8 mm pocket (nut corners 8.08 mm: light press)'),
    ('triplate-upper-pin-m4x16', ('shcs', 4, 16), 'triplate', _at('T2', -77.6), Y_NEG, 'M4x16 socket head screw',
     'upper levelling link to triplate'),
    ('triplate-upper-pin-nut', ('nut', 4), 'triplate', _at('T2', -67.5), Y_POS, 'M4 nut',
     'in the triplate 8 mm pocket (light press)'),
    ('manipulator-pin-m4x20', ('shcs', 4, 20), 'hand', _at('T3', -77.6), Y_NEG, 'M4x20 socket head screw',
     'upper levelling link to manipulator'),
    ('manipulator-pin-nut', ('nut', 4), 'hand', _at('T3', -62.0), Y_POS, 'M4 nut', 'in the manipulator pocket'),
    # Bearings without a vendor solid; flange face origin, ring into the part. Each flange sits on
    # its measured recess floor (seat depths from the vendor solids, see summary.md).
    ('bearing_F686ZZ_lever', ('bearing', 'F686ZZ'), 'lever', _at('S', -43.1), Y_POS, 'F686ZZ flanged bearing',
     'lever seat, shoulder axle'),
    ('bearing_F686ZZ_triplate', ('bearing', 'F686ZZ'), 'triplate', _at('E', -71.1), Y_POS, 'F686ZZ flanged bearing',
     'triplate seat, elbow axle'),
    ('bearing_F686ZZ_wrist_2', ('bearing', 'F686ZZ'), 'forearm', _at('W', -42.4), Y_NEG, 'F686ZZ flanged bearing',
     'upper-shank seat, wrist axle'),
    ('bearing_F624ZZ_pleuel_lever', ('bearing', 'F624ZZ'), 'pleuel', _at('L', -49.5), Y_POS, 'F624ZZ flanged bearing',
     'pleuel seat at the lever'),
    ('bearing_F624ZZ_pleuel_shank', ('bearing', 'F624ZZ'), 'pleuel', _at('PU', -43.5), Y_NEG, 'F624ZZ flanged bearing',
     'pleuel seat at the upper shank'),
    ('bearing_F624ZZ_bend_lower_body', ('bearing', 'F624ZZ'), 'bend_lower', _at('B0', -81.0), Y_POS,
     'F624ZZ flanged bearing', 'lower levelling link at the main body'),
    ('bearing_F624ZZ_bend_lower_triplate', ('bearing', 'F624ZZ'), 'bend_lower', _at('TL', -81.0), Y_POS,
     'F624ZZ flanged bearing', 'lower levelling link at the triplate'),
    ('bearing_F624ZZ_bend_upper_triplate', ('bearing', 'F624ZZ'), 'bend_upper', _at('T2', -77.5), Y_POS,
     'F624ZZ flanged bearing', 'upper levelling link at the triplate'),
    ('bearing_F624ZZ_bend_upper_manipulator', ('bearing', 'F624ZZ'), 'bend_upper', _at('T3', -77.5), Y_POS,
     'F624ZZ flanged bearing', 'upper levelling link at the manipulator'),
]
# Shim rings (DIN 988 6 x 12 x 0.5) where an axle has slack between a bearing inner ring and the
# next face: the axle bolt then clamps the inner-ring stack instead of leaving it to float or rub.
# Gaps measured along the axles (ray-cast at r 4 mm on the vendor solids + the bearings above):
# shoulder 0.5 / 0.9 / 0.5 mm, wrist 0.6 / 0.5 mm. The M4 link pivots and the elbow have no room
# (pocket floors and fork faces are flush or 0.1 mm), so they get none.
SHIM = ('washer', 6, 12, 0.5)
UPPER += [
    ('shim-shoulder-1', SHIM, 'turntable', _at('S', -69.0), Y_POS, 'Shim ring DIN 988 6x12x0.5',
     'main-body cheek to the lower 90T pulley bearing inner ring (0.5 mm gap)'),
    ('shim-shoulder-2', SHIM, 'turntable', _at('S', -44.0), Y_POS, 'Shim ring DIN 988 6x12x0.5',
     'lower-shank bearing to lever bearing inner rings (0.9 mm gap); they turn relative to each other'),
    ('shim-shoulder-3', SHIM, 'turntable', _at('S', -29.5), Y_POS, 'Shim ring DIN 988 6x12x0.5',
     'upper 90T pulley bearing inner ring to the main-body cheek (0.5 mm gap)'),
    ('shim-wrist-1', SHIM, 'hand', _at('W', -57.1), Y_POS, 'Shim ring DIN 988 6x12x0.5',
     'manipulator cheek to the upper-shank bearing inner ring (0.6 mm gap)'),
    ('shim-wrist-2', SHIM, 'hand', _at('W', -42.4), Y_POS, 'Shim ring DIN 988 6x12x0.5',
     'upper-shank bearing inner ring to the manipulator cheek (0.5 mm gap)'),
]

# Motor screws: heads in the main-body counterbores, 4 mm into each motor's tapped holes.
for side, y, zd in (('outer', -73.0, Y_POS), ('inner', -25.0, Y_NEG)):
    for i, (x, z) in enumerate(((84.5, 8.0), (84.5, 39.0), (115.5, 8.0), (115.5, 39.0))):
        UPPER.append((f'motor-{side}-m3x6-{i+1}', ('shcs', 3, 6), 'turntable', (x, y, z), zd,
                      'M3x6 socket head screw', f'{"lower" if side == "outer" else "upper"}-arm motor to main body'))
for i, (y, z) in enumerate(((-26.0, 23.0), (-26.0, 33.0), (-72.0, 23.0), (-72.0, 33.0))):
    UPPER.append((f'stabilizer-m3x6-{i+1}', ('shcs', 3, 6), 'turntable', (124.0, y, z), (1, 0, 0),
                  'M3x6 socket head screw', 'stabilizer to main body'))
for i, (y, z) in enumerate(((-72.0, 27.0), (-72.0, 37.0), (-26.0, 27.0), (-26.0, 37.0))):
    # M3x5: an M3x6 tip would hit the neighbouring motor-screw head (2 mm away in Z).
    UPPER.append((f'endstop-bracket-m3x5-{i+1}', ('shcs', 3, 5), 'turntable', (76.0, y, z), (-1, 0, 0),
                  'M3x5 socket head screw', 'endstop bracket to main body; 3.5 mm into the 3 mm pilot'))
for i, y in enumerate((-34.5, -49.5, -64.5)):
    UPPER.append((f'toolhead-m3x12-{i+1}', ('shcs', 3, 12), 'hand', (146.5, y, 190.3), (0, 0, -1),
                  'M3x12 socket head screw', 'gripper base to manipulator, from below'))

# Belts: GT2 6 mm loops from each 20T motor pulley (tip r 6.11) to its printed 90T pulley
# (tip r 28.42), centres 39 mm apart; teeth bands measured on the vendor solids.
BELT_CENTRE = 62.5 - 23.5
BELTS = [('belt-shoulder-gt2-200', -62.75), ('belt-elbow-gt2-200', -29.25)]   # +Y edge of each band

def model(key):
    if key[0] == 'shcs':
        return shcs(key[1], key[2])
    if key[0] == 'nut':
        return nut(key[1])
    if key[0] == 'bearing':
        return flanged_bearing(key[1])
    if key[0] == 'washer':
        return washer(key[1], key[2], key[3])
    raise KeyError(key)

def model_name(key):
    if key[0] == 'shcs':
        return f'm{key[1]}x{key[2]}-shcs'
    if key[0] == 'nut':
        return f'm{key[1]}-nut'
    if key[0] == 'washer':
        return f'shim-{key[1]}x{key[2]}x{key[3]}'
    return key[1].lower()
