"""MG90S conversion of the vendor sliding gripper; all returned positions are hand-local mm.
Keeps the original dovetail guide BRep. Source: 20sffactory community_robot_arm CC BY 4.0.
Run with the Mechy engine Python. build() returns (mesh_parts, assembly_records, details).
Mesh v arrays are metres; generated STEP files themselves are hand-local mm, position=[0,0,0].
Actuator/horn fit is provisional: MG90S clone dimensions and OEM horn must be measured.
"""
from pathlib import Path
import json, math, sys
import numpy as np
from build123d import *

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OUT=HERE/'gripper-models'
SOURCE=Path('/Users/Carlo/Empire/BAM/Models/vendor/20sffactory/CAD Files/robot_arm.step')
HAND=np.array([119.541,-49.005,196.348])
SHIFT_X=0.999
CX=172.540515397+SHIFT_X
CY=-49.500004703
Z0=195.348278346
DECK=205.348278346
TAB=207.748278346
SOURCE_URL='https://github.com/20sffactory/community_robot_arm'
REMOVE_GRIPPER_REFS=('gripperBase_by_ftobler.stl','gripper_shaft.stl')

def mesh(shape):
    vs,ts=shape.tessellate(0.08,0.15)
    return np.array([[p.X,p.Y,p.Z] for p in vs]),np.asarray(ts,np.uint32)

def box(x0,x1,y0,y1,z0,z1):
    return Pos((x0+x1)/2,(y0+y1)/2,(z0+z1)/2)*Box(x1-x0,y1-y0,z1-z0)

def cyl(x,y,r,z0,z1):
    return Pos(x,y,(z0+z1)/2)*Cylinder(r,z1-z0)

def model_sources():
    OUT.mkdir(exist_ok=True)
    names={42:'source-base',37:'source-link-left',44:'source-link-right',46:'source-manipulator'}
    if not all((OUT/(n+'.step')).exists() for n in names.values()):
        src=import_step(str(SOURCE)).solids()
        for i,n in names.items():export_step(src[i],str(OUT/(n+'.step')))
    return {n:import_step(str(OUT/(n+'.step'))) for n in names.values()}

def mounting_nut(x,y):
    with BuildPart() as p:
        with BuildSketch(Plane.XY.offset(DECK-2.7)):
            with Locations((x,y)):RegularPolygon(5.5/math.sqrt(3),6)
        extrude(amount=2.4)
    return p.part-cyl(x,y,1.5,DECK-3,DECK+1)

def screw(d,length,x,y,seat,up=False):
    head={2:(3.8,2),3:(5.5,3)}[d]
    s=cyl(0,0,d/2,-length,0)+cyl(0,0,head[0]/2,0,head[1])
    with BuildPart() as hexcut:
        with BuildSketch(Plane.XY.offset(head[1]-1)):
            RegularPolygon(({2:1.5,3:2.5}[d])/math.sqrt(3),6)
        extrude(amount=2)
    s=s-hexcut.part
    return Pos(x,y,seat)*(Rot(180,0,0)*s if up else s)

def build():
    src=model_sources()
    base=Pos(SHIFT_X,0,0)*src['source-base']
    # Close the old stepper holes with a 4 mm top web inside the unchanged perimeter.
    base=base+box(151.0,186.0,CY-25,CY+25,DECK-4,DECK)
    # 0.5 mm nominal per-side clearance around the modeled 22.8 x 12.4 servo case.
    bx=CX-5.2
    base=base-box(bx-11.9,bx+11.9,CY-6.7,CY+6.7,Z0-1,DECK+4)
    servo_holes=[CX-19.45,CX+9.05]
    for x in servo_holes:
        base=base-cyl(x,CY,0.85,DECK-5,DECK+1)
    # Full-depth mount clearances and captive M3 hex nuts accessible from above.
    mount_x=146.540515397
    for y in [CY-15,CY,CY+15]:
        base=base-cyl(mount_x,y,1.7,Z0-1,DECK+1)
        with BuildPart() as pocket:
            with BuildSketch(Plane.XY.offset(DECK-2.7)):
                with Locations((mount_x,y)):RegularPolygon(5.85/math.sqrt(3),6)
            extrude(amount=3)
        base=base-pocket.part
    # Cam sizes measured from servo_gripper_shaft.stl; wire holes retain STEP crank coordinates.
    cam=cyl(CX,CY,10,194.848278346,197.848278346)+cyl(CX,CY,6,197.848278346,199.848278346)
    cam=cam-cyl(CX,CY,2.75,194,201)-cyl(CX,CY,3.65,196.348278346,201)
    pin_xy=[(171.297091171+SHIFT_X,-57.402782455),(164.637737646+SHIFT_X,-48.256580477),
            (173.783939624+SHIFT_X,-41.597226951),(180.443293149+SHIFT_X,-50.743428930)]
    for x,y in pin_xy:cam=cam-cyl(x,y,0.9,194,199)
    # Captured trimmed OEM single-arm horn: open radial notch transmits torque through its arm.
    # The supplied horn must be measured before this pocket is released for print.
    cam=cam-box(CX-2.2,CX+2.2,CY,CY+9,198.048278346,201)
    horn=cyl(CX,CY,3.5,196.548278346,199.748278346)+box(CX-2,CX+2,CY,CY+8,198.248278346,199.648278346)
    horn=horn-cyl(CX,CY,2.4,195,201)
    servo=Pos(CX,CY,TAB)*Rot(180,0,0)*import_step(str(ROOT/'parts/models/mg90s.step'))
    # Protective collar mounts under the existing servo fasteners; top remains open
    # for cooling and direct driver access. Rounded walls hide the mounting tabs.
    cover_bottom=TAB+2.5
    cover_outer=Pos(bx,CY,cover_bottom)*extrude(RectangleRounded(39.3,19.2,4),amount=20)
    cover_inner=Pos(bx,CY,cover_bottom-1)*extrude(RectangleRounded(34.5,14.4,1.6),amount=23)
    cover=cover_outer-cover_inner
    for x in servo_holes:
        foot=box(CX-24.85,CX-17.1,CY-5,CY+5,cover_bottom,cover_bottom+2) if x<bx else box(CX+6.7,CX+14.45,CY-5,CY+5,cover_bottom,cover_bottom+2)
        cover=cover+foot
        cover=cover-cyl(x,CY,1.3,cover_bottom-1,cover_bottom+3)
    # Cable exits above the tabs on the +X end of this inverted servo.
    cover=cover-box(CX+6, CX+16, CY-3.5,CY+3.5,TAB+16.5,TAB+23)
    rows=[];solids={}
    def add(name,shape,kind,color,material=None,note='',mass=None):
        local=Pos(*(-HAND))*shape
        file=OUT/(name+'.step');export_step(local,str(file))
        if kind=='printed':
            export_stl(local,str(OUT/(name+'.stl')))
            bb=local.bounding_box();c=bb.center()
            flipped=name=='gripper-servo-carrier'
            zdatum=bb.max.Z if flipped else bb.min.Z
            pre=Pos(-c.X,-c.Y,-zdatum)*local
            pr=Rot(180,0,0)*pre if flipped else pre
            printstep=HERE/'printed'/(name+'.step');printstl=HERE/'printed'/(name+'.stl')
            export_step(pr,str(printstep));export_stl(pr,str(printstl))
            wrapper=HERE/'printed'/(name+'.py')
            wrapper.write_text('from pathlib import Path\nimport sys\nsys.path.insert(0,str(Path(__file__).resolve().parents[1]))\nfrom gripper_servo import build\nfrom style import *\nbuild()\n')
        v,t=mesh(local)
        rgba=tuple(int(color[i:i+2],16)/255 for i in (1,3,5))+(1.0,)
        rec=dict(id=name,model=str(file.relative_to(ROOT)),position=[0,0,0],rotation=[0,0,0],
                 joint_node='hand',kind=kind,color=color,frame='hand-local mm',note=note)
        if material:rec['material']=material
        if kind=='printed':
            rec.update(print_model=str(printstep.relative_to(ROOT)),print_stl=str(printstl.relative_to(ROOT)),
                       print_position=[c.X,c.Y,zdatum],print_rotation=[180,0,0] if flipped else [0,0,0],
                       print_orientation='top mounting face on bed; guide rails up' if flipped else 'flat flange face on bed')
        if mass is not None:rec['mass_kg_estimate']=mass
        rows.append((dict(name=name,node='hand',v=v/1000,t=t,rgba=rgba,kind=kind,printed_ref=name if kind=='printed' else None,mass_kg=mass),rec))
        solids[name]=dict(valid=bool(local.is_valid),solids=len(local.solids()),volume_mm3=round(local.volume,3),bbox_mm=[list(local.bounding_box().min),list(local.bounding_box().max)])
    add('gripper-servo-carrier',base,'printed','#64748b','PLA',
        'Original STEP dovetail rails retained; motor web, clearance pocket, separate 2.4 mm servo spacers and captive mount nuts revised.')
    add('gripper-servo-crank',cam,'printed','#fbbf24','PLA',
        '20 mm cam, 12 mm hub; measured servo STL sizes with original four wire-hole axes; OEM horn notch estimated.')
    add('gripper-servo-guard',cover,'printed','#303945','PLA',note='Open-top protective collar, cable notch, 2.4 mm walls; seats on servo tabs, two M2x12 screws.')
    add('gripper-mg90s',servo,'bought','#263445',note='Existing parts/models/mg90s.step; variant-specific measurements still required.',mass=0.0134)
    add('gripper-oem-horn',horn,'bought','#e2e8f0',note='Estimated trimmed OEM horn envelope, not a purchase or a printable spline.',mass=0.0005)
    left_link=Pos(SHIFT_X,0,0)*src['source-link-right']
    def mirror_tool(s):return Pos(CX,CY,0)*Rot(0,0,180)*Pos(-CX,-CY,0)*s
    for side,link in [('left',left_link),('right',mirror_tool(left_link))]:
        add('gripper-link-'+side,link,'bought','#cbd5e1',
            note='Original STEP solid44 bent steel link, mirrored for right. Diameter1.5 mm;21 mm end-axis spacing; source guide says approximately20 mm.',mass=0.0005)
    rx,ry=170.333408616+SHIFT_X,-73.649684245
    retainer=cyl(rx,ry,6,189.348278346,191.848278346)-cyl(rx,ry,1.7,188,193)-cyl(rx,ry,3.1,188,190.848278346)
    retainer_screw=screw(3,6,rx,ry,190.848278346,up=True)
    for side,ret,sc in [('left',retainer,retainer_screw),('right',mirror_tool(retainer),mirror_tool(retainer_screw))]:
        add('gripper-wire-retainer-'+side,ret,'printed','#64748b','PLA',note='12 mm washer captures bent-wire pin; M3 head access counterbore.')
        add('gripper-retainer-m3x6-'+side,sc,'bought','#cbd5e1',note='M3x6 into2.8 mm finger pilot;5 mm nominal polymer engagement.',mass=0.0012)
    # Captive retaining plate is larger than the crank bore. OEM screw size/depth
    # remains a measured-hardware release gate; shown as an M2x8 envelope only.
    keeper=cyl(CX,CY,4,193.148278346,194.848278346)-cyl(CX,CY,1.3,192,196)
    add('gripper-crank-keeper',keeper,'printed','#303945','PLA',note='1.7 mm retaining plate under crank; OEM horn screw clamps the stack. Check actual screw/head/thread before print.')
    add('gripper-oem-retaining-screw',screw(2,8,CX,CY,193.148278346,up=True),'bought','#303945',note='Envelope only for servo-supplied retaining screw; exact diameter and length unverified.',mass=.0005)
    for i,y in enumerate([CY-15,CY,CY+15],1):
        add('gripper-mount-m3x16-'+str(i),screw(3,16,mount_x,y,190.348278346,up=True),'bought','#cbd5e1',note='M3x16 from underside of manipulator; tip 1.3 mm past captive nut.',mass=0.0018)
        add('gripper-mount-m3-nut-'+str(i),mounting_nut(mount_x,y),'bought','#cbd5e1',note='M3 plain nut in accessible top hex pocket.',mass=0.0005)
    for i,x in enumerate(servo_holes,1):
        spacer=box(x-2.6,x+2.6,CY-5,CY+5,DECK,TAB)-cyl(x,CY,1.3,DECK-1,TAB+1)
        add('gripper-servo-spacer-'+str(i),spacer,'printed','#64748b','PLA',note='2.4 mm thick; separate flat print keeps the carrier supportless.')
        add('gripper-servo-m2x12-'+str(i),screw(2,12,x,CY,TAB+4.5),'bought','#cbd5e1',note='M2x12 through2 mm guard,2.5 mm tab and2.4 mm spacer;5.1 mm pilot engagement. Length availability unverified.',mass=0.0005)
    details=dict(source=SOURCE_URL,source_step=str(SOURCE),source_license='CC BY4.0; Florin Tobler /20sffactory',
        imported_brep_solids=[42,37,44],hand_origin_vendor_mm=HAND.tolist(),base_shift_x_mm=SHIFT_X,
        crank_center_vendor_mm=[CX,CY],servo_tab_top_vendor_mm=TAB,mount_hole_axes_vendor_mm=[[mount_x,y]for y in [CY-15,CY,CY+15]],
        old_node_removal='Remove hand parts whose name starts gripper; preserve renamed wrist bearing and manipulator. Skip upper-hardware toolhead-m3x12-*.',
        retained_finger_translation_vendor_mm=[SHIFT_X,0,0],minimum_boss_to_crank_axial_clearance_mm=0.5,
        unverified=['MG90S clone and horn actual dimensions','Horn notch geometry and torque transfer need fit coupon','M2 pilot strength and fastener availability','Sliding rail fit and bending-link endurance','Complete motion sweep and load test'],
        model_checks=solids)
    (OUT/'provenance.json').write_text(json.dumps(details,indent=2))
    (OUT/'assembly-records.json').write_text(json.dumps([r for _,r in rows],indent=2))
    return [m for m,_ in rows],[r for _,r in rows],details

if __name__=='__main__':
    m,r,d=build()
    print(json.dumps(dict(parts=len(m),models_valid=all(x['valid'] and x['solids']==1 for x in d['model_checks'].values()),outputs=str(OUT))))
