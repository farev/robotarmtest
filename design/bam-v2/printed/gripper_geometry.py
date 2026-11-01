"""BAM gripper fingers: original measured dovetail, reinforced jaw, replaceable TPU pad.

Original Florin Tobler / 20sffactory geometry, CC BY 4.0. Only the guide and wire-link
interface are retained. Work frame: X across finger, Y toward object, Z up; guide
top is Z=0, pad contact plane Y=0. Parts are transformed to their print orientations.
"""
from pathlib import Path
import math
from build123d import *
from style import *

HERE = Path(__file__).resolve().parent
VARIANT = HERE.parent
SOURCE = VARIANT/'gripper-models/reference-finger.step'
# Measured STEP solid 4, robot_arm.step. Preserve these mating surfaces exactly.
SOURCE_DATUM = (172.333408616, -54.410922315, 199.548278346)
PAD_T = 6.5
JAW_T = 4.0
JAW_WIDTH = 28.0
PAD_WIDTH = 26.0
PAD_HEIGHT = 22.0
TIP_Z = -33.5
SCREWS = [(-7.0, -22.5), (7.0, -22.5)] # (x,z), M3x10, ISO data / owned studio stock
M3_CLEAR = 3.6
NUT_AF = 5.75
NUT_DEPTH = 3.5

def _plate_polygon(points, thickness):
    return extrude(Plane.XZ * Polygon(*points, align=None), amount=thickness)

def finger_work():
    original = Pos(*[-v for v in SOURCE_DATUM])*import_step(str(SOURCE))
    # Preserve dovetail and wire linkage down to Z=-13.5; replace old slender tips.
    guide = original & (Pos(0,-15,-13.5)*Box(100,100,40,align=(Align.CENTER,Align.CENTER,Align.MIN)))
    # Rounded 4 mm jaw web. Extrusion on XZ goes toward -Y.
    plate = Pos(0,-PAD_T,TIP_Z+12)*extrude(Plane.XZ*RectangleRounded(JAW_WIDTH,24,GRIP_CORNER), amount=JAW_T)
    # Two ribs transfer jaw bending into the old guide root. Flat side on the bed.
    rib_outline = [(-23,-5),(-10.5,-5),(-10.5,-30),(-14,-24),(-23,-13)] # (y,z)
    ribs=[]
    for x in (-13.3,10.3):
        ribs.append(Pos(x,0,0)*extrude(Plane.YZ*Polygon(*rib_outline,align=None),amount=3,dir=(1,0,0)))
    part=guide.fuse(plate,*ribs)
    # Recess the retained root where the detachable pad replaces the old curved tip.
    part -= Pos(0,-1.5,-23)*Box(26.5,10,23.5)
    # Open the original 0.2 / 1.2 mm sacrificial hole caps: no unprintable membrane.
    for y,r,z in [(-19.23876193,1.4,-0.2),(-14.73876193,0.9,-1.2)]:
        part -= Pos(-2,y,z-0.01)*Cylinder(r,3,align=(Align.CENTER,Align.CENTER,Align.MIN))
    for x,z in SCREWS:
        part -= Pos(x,5,z)*Rot(90,0,0)*Cylinder(M3_CLEAR/2,25,align=(Align.CENTER,Align.CENTER,Align.MIN))
    # Original assembly had 0.2 mm crown penetration into the guide roof.
    # Remove 0.4 mm from the crown for 0.2 mm running clearance, preserving link axes.
    part -= Pos(0,-15,4.6)*Box(100,100,10)
    return part

def pad_work():
    # Rigid fasteners terminate 0.5 mm below the flat lands. TPU compliance is untested.
    part=Pos(0,0,TIP_Z+PAD_HEIGHT/2)*extrude(Plane.XZ*RectangleRounded(PAD_WIDTH,PAD_HEIGHT,GRIP_CORNER),amount=PAD_T)
    # Broad shallow V groove locates round objects; flat lands still grip boxes.
    # 2 mm relief, 12 mm mouth; printable without thin decorative ribs.
    groove=Pos(0,0,TIP_Z-1)*extrude(Polygon((-6,0.1),(6,0.1),(0,-2),align=None),amount=PAD_HEIGHT+2)
    part -= groove
    for x,z in SCREWS:
        part -= Pos(x,2,z)*Rot(90,0,0)*Cylinder(M3_CLEAR/2,12,align=(Align.CENTER,Align.CENTER,Align.MIN))
        pocket=Pos(x,0.1,z)*Rot(90,0,0)*extrude(RegularPolygon(NUT_AF/math.sqrt(3),6),amount=NUT_DEPTH+0.1)
        part -= pocket
    return part

def finger_print():
    # Guide face down: retained dovetail bridges stay short; four walls/ribs resist jaw bending.
    return Pos(0,0,-0.4)*Rot(180,0,0)*finger_work()

def pad_print():
    # Back face down, contact lands face up; nut traps open upward.
    return Pos(0,-11.5,PAD_T)*Rot(90,0,0)*pad_work()

def export_one(name, fn):
    part=fn()
    if len(part.solids()) != 1 or not part.is_valid:
        raise RuntimeError(f'{name}: {len(part.solids())} solids, valid {part.is_valid}')
    export_step(part,str(HERE/f'{name}.step'))
    export_stl(part,str(HERE/f'{name}.stl'),tolerance=0.05,angular_tolerance=0.1)
    return part

if __name__=='__main__':
    for name,fn in [('gripper-finger',finger_print),('gripper-pad',pad_print)]:
        part=export_one(name,fn)
        print(name,part.volume,part.bounding_box())
