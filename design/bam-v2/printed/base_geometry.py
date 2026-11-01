"""Direct-drive base dimensions in mm. Source geometry is built in assembly coordinates.

The main-body mating plane is measured from the original GLB. Motor/coupling
dimensions are read from the existing model records, whose uncertainties remain.
The 51105 dimensions are handbook-typical, not a certificate for a purchased bearing.
"""
from pathlib import Path
import math
import yaml
from build123d import *
from style import *

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
def dims(name):
    return {d['name']: d['value_mm'] for d in yaml.safe_load(
        (ROOT / 'parts/models' / (name + '.yaml')).read_text())['critical_dims']}
MOTOR = dims('nema17-42shdc')
COUPLER = dims('flange-coupling-5mm')
# Set from the original main_body mesh, not from the rounded vendor drawing.
TOP = 25.697
ADAPTER_BOTTOM = TOP - 4.5
BEARING_TOP = TOP - 12
BEARING_BOTTOM = BEARING_TOP - 11
MOTOR_FACE = BEARING_BOTTOM - 10
FLOOR = MOTOR_FACE - MOTOR['body length'] - 5
COUPLER_TOP = ADAPTER_BOTTOM
JOURNAL_BOTTOM = BEARING_BOTTOM - 5
PITCH = MOTOR['hole pitch']
BODY_PITCH = 27.0  # original main_body cylindrical feature axes, +/-13.5
M3_CLEAR = 3.6
M4_CLEAR = 4.8
JOURNAL_OD = 24.9  # 0.1 diametral clearance to nominal 25 mm bearing bore; coupon required
JOURNAL_ID = 14.0  # clearance for 10 mm coupling barrel and shaft
JOURNAL_BORE = 25.3  # 0.4 diametral running clearance; coupon/wear check required
BEARING_OD = 42.0
COUPLER_XY = [(COUPLER['hole circle radius'] * math.cos(math.radians(a)),
               COUPLER['hole circle radius'] * math.sin(math.radians(a)))
              for a in (45, 135, 225, 315)]
# Enclosed drum housing: motor bay walls, 40-degree skirt and an anchor foot ring.
SKIRT_TAN = math.tan(math.radians(40))   # all skirts 40 deg from vertical: no supports
HOUSING_R = 48.0
HOUSING_WALL = 3.0
FOOT_R = 58.0
FOOT_H = 4.0
SKIRT_TOP = FLOOR + FOOT_H + (FOOT_R - HOUSING_R) / SKIRT_TAN
ANCHOR_R = 52.5   # 3.25 mm of foot outside the 4.8 mm hole
ANCHOR_ANGLES = (45, 135, 225, 315)
PORT_W = 22.0          # motor cable port on -X; the motor plug is turned to face it
PORT_TOP = FLOOR + 24.0
VENT_W = 3.2
VENT_LO = SKIRT_TOP + 4
VENT_HI = MOTOR_FACE - 4
VENT_ANGLES = [a for a in range(0, 360, 20) if abs(a - 180) > 30]
# Bearing cover: a closed collar over the thrust bearing whose lip catches the spindle flange.
# At the shoulder 15 / elbow -132..-142 deg corner the forearm sweeps down to z~9.6 at r~41 mm
# and z~3.6 at r~49 mm, so nothing of the cover may sit outside r~39: the screws run down
# through bosses inside the collar into heat-set inserts in the deck.
COVER_R = 38.5
COVER_WALL = 2.4
LIP_Z = ADAPTER_BOTTOM + 0.5     # 0.5 mm rotor axial float
LIP_T = 2.4
LIP_TOP = LIP_Z + LIP_T          # 1.6 mm below the unchanged main-body underside
LIP_IR = 25.3        # 2.3 mm radial gap to the 46 mm adapter; 2.7 mm overlap on the spindle flange
COVER_SCREW_R = 33.8             # boss inner edge 1.4 mm outside the r28 spindle flange
COVER_BOSS_R = 4.4
COVER_HOLES = [(COVER_SCREW_R * math.cos(math.radians(a)), COVER_SCREW_R * math.sin(math.radians(a)))
               for a in (0, 90, 180, 270)]
COVER_SEAT = LIP_TOP - 3.3       # screw-head seat in the lip counterbore
INSERT_D = 4.0       # M3 x 5.7 heat-set insert hole in the deck top
INSERT_DEPTH = 6.0
BRIDGE = 0.25   # one sacrificial bridge layer per step above a counterbore floor

def cyl(r, height, z=0, x=0, y=0):
    return Pos(x, y, z) * Cylinder(r, height, align=(Align.CENTER, Align.CENTER, Align.MIN))

def revolved(points):
    """Solid of revolution about Z from (radius, z) profile points."""
    return revolve(Plane.XZ * Polygon(*points, align=None), Axis.Z)

def cbore(x, y, z_top, hole_d, cb_d, depth, z_through):
    """Counterbore opening at z_top over a through hole down to z_through. The counterbore
    face prints on (or toward) the bed, so its floor is a ceiling: a slot layer then a square
    layer let the slicer bridge it without supports (sacrificial-bridge method)."""
    floor = z_top - depth
    s = cyl(hole_d/2, z_top - z_through + 0.1, z_through - 0.1, x, y)
    s += cyl(cb_d/2, depth + 0.1, floor, x, y)
    slot = Pos(x, y, floor - BRIDGE) * Box(cb_d, hole_d, BRIDGE, align=(Align.CENTER, Align.CENTER, Align.MIN))
    s += slot & cyl(cb_d/2, BRIDGE, floor - BRIDGE, x, y)
    s += Pos(x, y, floor - 2*BRIDGE) * Box(hole_d, hole_d, BRIDGE, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return s

def radial_slot(angle, r, z_lo, z_hi, width, depth):
    """Vertical stadium slot through a cylindrical wall at radius r."""
    straight = z_hi - z_lo - width
    s = Pos(r, 0, z_lo + width/2) * Box(depth, width, straight, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for z in (z_lo + width/2, z_hi - width/2):
        s += Pos(r, 0, z) * Rot(0, 90, 0) * Cylinder(width/2, depth)
    return Rot(0, 0, angle) * s

def housing():
    # Printed deck-down (deck top on the bed), walls upward. Every feature is a vertical wall,
    # the 40-degree skirt or a short counterbore bridge, so it needs no supports.
    s = revolved([(HOUSING_R - HOUSING_WALL, FLOOR), (FOOT_R - 0.6, FLOOR), (FOOT_R, FLOOR + 0.6),
                  (FOOT_R, FLOOR + FOOT_H), (HOUSING_R, SKIRT_TOP), (HOUSING_R, BEARING_BOTTOM - 1.0),
                  (HOUSING_R - 0.6, BEARING_BOTTOM), (0, BEARING_BOTTOM), (0, MOTOR_FACE),
                  (HOUSING_R - HOUSING_WALL, MOTOR_FACE)])
    # Pilot clearance and the separate running journal. These do not load the motor shaft axially.
    s -= cyl((MOTOR['pilot diameter']+0.4)/2, 10.2, MOTOR_FACE-0.1)
    s -= cyl(JOURNAL_BORE/2, BEARING_BOTTOM-JOURNAL_BOTTOM+0.1,JOURNAL_BOTTOM)
    # Internal transition 35 deg from vertical: no unsupported annular bore shoulder.
    delta=(JOURNAL_BORE-(MOTOR['pilot diameter']+0.4))/2
    rise=delta/math.tan(math.radians(35))
    s -= Pos(0,0,JOURNAL_BOTTOM-rise)*Cone((MOTOR['pilot diameter']+0.4)/2,
        JOURNAL_BORE/2,rise,align=(Align.CENTER,Align.CENTER,Align.MIN))
    # Motor fasteners are installed before the bearing. M3x10 gives 4.5 mm nominal engagement.
    for x in (-PITCH/2,PITCH/2):
        for y in (-PITCH/2,PITCH/2):
            s -= cbore(x, y, BEARING_BOTTOM, M3_CLEAR, 6.5, 4.5, MOTOR_FACE)
    # Cover screws go into heat-set inserts; a 3.2 mm hole continues through for the screw tip.
    for x, y in COVER_HOLES:
        s -= cyl(INSERT_D/2, INSERT_DEPTH + 0.1, BEARING_BOTTOM - INSERT_DEPTH, x, y)
        s -= cyl(1.7, 10.2, MOTOR_FACE - 0.1, x, y)
    # Anchor screws through the foot ring; spot faces open through the skirt.
    for a in ANCHOR_ANGLES:
        x, y = ANCHOR_R*math.cos(math.radians(a)), ANCHOR_R*math.sin(math.radians(a))
        s -= cbore(x, y, SKIRT_TOP + 0.1, M4_CLEAR, 8.4, SKIRT_TOP + 0.1 - FLOOR - FOOT_H, FLOOR)
    # Cable port at the floor on -X, open at the floor so it prints as a plain notch.
    port = Pos(-50, 0, FLOOR - 1) * Box(20, PORT_W, PORT_TOP - PORT_W/2 - FLOOR + 1,
        align=(Align.CENTER, Align.CENTER, Align.MIN))
    port += Pos(-50, 0, PORT_TOP - PORT_W/2) * Rot(0, 90, 0) * Cylinder(PORT_W/2, 20)
    s -= port
    # Vertical vent slots for the motor bay (stadium ends print as short arches).
    for a in VENT_ANGLES:
        s -= radial_slot(a, HOUSING_R - HOUSING_WALL/2, VENT_LO, VENT_HI, VENT_W, HOUSING_WALL + 4)
    return s

def spindle():
    # The spindle supports the bearing; the metal flange coupling transmits motor torque.
    s = cyl(28,ADAPTER_BOTTOM-BEARING_TOP,BEARING_TOP) + cyl(JOURNAL_OD/2,BEARING_TOP-JOURNAL_BOTTOM,JOURNAL_BOTTOM)
    s -= cyl(JOURNAL_ID/2,40,JOURNAL_BOTTOM-1)
    # Coupling and its nuts install from above before the adapter plate is attached.
    cavity_r=(COUPLER['flange diameter']+0.4)/2
    # Keep the wide coupling recess above the load-bearing journal neck.
    cavity_bottom=BEARING_TOP+3.0
    s -= cyl(cavity_r,9,cavity_bottom)
    taper=cavity_r-JOURNAL_ID/2
    s -= Pos(0,0,cavity_bottom-taper)*Cone(JOURNAL_ID/2,cavity_r,taper,
        align=(Align.CENTER,Align.CENTER,Align.MIN))
    # Two open-bottom 8 mm bridges give radial hex-key access to coupling set screws.
    for sign in (-1,1):
        s -= Pos(sign*22,0,BEARING_TOP) * Box(22,8,5.5,
            align=(Align.CENTER,Align.CENTER,Align.MIN))
    for x in (-BODY_PITCH/2,BODY_PITCH/2):
        for y in (-BODY_PITCH/2,BODY_PITCH/2):
            s -= cyl(M3_CLEAR/2,9,BEARING_TOP,x,y)
            # M3 nut trap, 5.8 AF, inserted from the bearing side before installation.
            s -= Pos(x,y,BEARING_TOP) * extrude(RegularPolygon(5.8/math.sqrt(3),6),amount=5.4)
    return s

def adapter():
    s = cyl(23,TOP-ADAPTER_BOTTOM,ADAPTER_BOTTOM)  # 2.3 mm radial gap to retainer
    s -= cyl((MOTOR['shaft diameter']+0.4)/2,5,ADAPTER_BOTTOM)
    for x in (-BODY_PITCH/2,BODY_PITCH/2):
        for y in (-BODY_PITCH/2,BODY_PITCH/2):
            s -= cyl(M3_CLEAR/2,5,ADAPTER_BOTTOM,x,y)
    for x,y in COUPLER_XY:
        s -= cyl(M3_CLEAR/2,5,ADAPTER_BOTTOM,x,y)
        # M3 flat-head screws sit below the unchanged main-body mating plane.
        s -= Pos(x,y,TOP-1.5) * Cone(1.8,3.3,1.5,align=(Align.CENTER,Align.CENTER,Align.MIN))
    return s

def cover():
    # Closed collar over the thrust bearing; its lip captures the spindle flange with 0.5 mm
    # axial float. Printed lip-down: collar and bosses grow straight up, no supports.
    # Lip strength is unverified.
    s = revolved([(COVER_R - COVER_WALL, BEARING_BOTTOM), (COVER_R, BEARING_BOTTOM),
                  (COVER_R, LIP_TOP - 0.8), (COVER_R - 0.5, LIP_TOP), (LIP_IR, LIP_TOP),
                  (LIP_IR, LIP_Z), (COVER_R - COVER_WALL, LIP_Z)])
    for x, y in COVER_HOLES:
        s += cyl(COVER_BOSS_R, LIP_Z - BEARING_BOTTOM + 0.1, BEARING_BOTTOM, x, y)
    for x, y in COVER_HOLES:
        s -= cbore(x, y, LIP_TOP, M3_CLEAR, 6.0, LIP_TOP - COVER_SEAT, BEARING_BOTTOM)
    return s

PARTS = {
    'yaw-base-housing': (housing, BEARING_BOTTOM, BASE_COLOR),
    'yaw-bearing-spindle': (spindle, ADAPTER_BOTTOM, ROTOR_COLOR),
    'yaw-turntable-adapter': (adapter, TOP, ROTOR_COLOR),
    'yaw-bearing-cover': (cover, LIP_TOP, BASE_COLOR),
}

def export_part(name):
    fn,top,_ = PARTS[name]
    # Rotate into print orientation; the original top face becomes z=0 on the bed.
    s = Pos(0,0,top) * Rot(180,0,0) * fn()
    export_step(s, str(HERE / (name+'.step')))
    export_stl(s, str(HERE / (name+'.stl')), tolerance=0.08, angular_tolerance=0.15)
    return s
