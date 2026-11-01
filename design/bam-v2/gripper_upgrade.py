"""Build the gripper cartridge, its solid manifest, views, and viewer mesh records."""
from pathlib import Path
import json, sys, math, os
os.environ.setdefault("MPLCONFIGDIR","/private/tmp/bam-v2-matplotlib")
import numpy as np
import yaml
from build123d import *
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE/'printed'))
import gripper_geometry as gg
import gripper_servo as gs
import hardware as hw
from mechy.cad.render import render_parts_png

def build():
    meshes,records,details=gs.build()
    gdir=HERE/'gripper';gdir.mkdir(exist_ok=True)
    left=np.array(gg.SOURCE_DATUM)+[gs.SHIFT_X,0,0]-gs.HAND
    center=np.array([gs.CX,gs.CY,0])-np.array([gs.HAND[0],gs.HAND[1],0])
    right=np.array([2*center[0]-left[0],2*center[1]-left[1],left[2]])
    allow=[];reasons=[]
    def add(name,part,kind,color,material=None,printed_ref=None):
        file=HERE/'gripper-models'/f'{name}.step';export_step(part,str(file))
        v,t=gs.mesh(part);rgba=tuple(int(color[i:i+2],16)/255 for i in (1,3,5))+(1,)
        meshes.append(dict(name=name,node='hand',v=v/1000,t=t,rgba=rgba,kind=kind,printed_ref=printed_ref))
        row=dict(id=name,model=str(file.relative_to(ROOT)),kind=kind,position=[0,0,0],rotation=[0,0,0],color=color,joint_node='hand')
        if material:row['material']=material
        if printed_ref:row['print_model']=f'design/bam-v2/printed/{printed_ref}.step'
        records.append(row)
    for side,pos,angle in [('left',left,0),('right',right,180)]:
        tf=Pos(*pos)*Rot(0,0,angle)
        add(f'gripper-finger-{side}',tf*gg.finger_work(),'printed','#465466','PLA','gripper-finger')
        add(f'gripper-pad-{side}',tf*gg.pad_work(),'printed','#4fd1c5','TPU 95A','gripper-pad')
        for i,(x,z) in enumerate(gg.SCREWS,1):
            # SHCS head outside jaw. Local +Z -> -Y, shank toward object (+Y).
            screw=Pos(x,-gg.PAD_T-gg.JAW_T,z)*Rot(90,0,0)*hw.shcs(3,10)
            # Nut's +Z -> -Y; outside nut face at Y=-1.1, back face=-3.5.
            nut=Pos(x,-1.1,z)*Rot(90,0,0)*hw.nut(3)
            sn=f'gripper-pad-{side}-m3x10-{i}';nn=f'gripper-pad-{side}-nut-{i}'
            add(sn,tf*screw,'bought','#b4b8be');add(nn,tf*nut,'bought','#b4b8be')
            allow.append([sn,nn]);reasons.append('Nominal M3 threads; 2.4 mm nut engagement, screw ends 0.5 mm below contact lands.')
    for i in range(1,4):
        allow.append([f'gripper-mount-m3x16-{i}',f'gripper-mount-m3-nut-{i}']);reasons.append('M3 threads in captive wrist attachment nut.')
    for i in range(1,3):
        allow.append([f'gripper-servo-m2x12-{i}','gripper-servo-carrier']);reasons.append('M2 screw forms thread in the carrier 1.7 mm pilot; 5.1 mm engagement estimate.')
    allow.append(['gripper-oem-retaining-screw','gripper-mg90s']);reasons.append('OEM retention screw into servo output thread; screw geometry provisional.')
    allow.append(['gripper-oem-horn','gripper-mg90s']);reasons.append('OEM horn spline engages servo spline; exact clone horn unverified.')
    # Original retainers deliberately thread into the finger; never hide rail interference.
    for side in ['left','right']:
        for r in records:
            if 'retainer' in r['id'] and side in r['id'] and ('m3' in r['id'] or 'screw' in r['id']):
                allow.append([r['id'],f'gripper-finger-{side}']);reasons.append('M3 retainer screw into original finger pilot.')
    # Wrist solid is included as a physical mating reference, not a new print export.
    manip=Pos(*(-gs.HAND))*gs.model_sources()['source-manipulator']
    add('gripper-wrist-reference',manip,'bought','#9971b2')
    doc=dict(scope='Gripper cartridge in hand-local frame; wrist BRep included. No whole-arm capacity claim.',
             min_clearance_mm=0.1,parts=records,allow_contact=allow,allow_contact_reasons=reasons)
    (gdir/'assembly.yaml').write_text(yaml.safe_dump(doc,sort_keys=False))
    # Save reusable hand-local manifest for the full-arm generator.
    (HERE/'gripper_assembly.yaml').write_text(yaml.safe_dump(doc,sort_keys=False))
    # Render physical cartridge without keepouts, from four sides.
    shown=[(m['v'],m['t'],m['rgba']) for m in meshes]
    for view in ['iso','front','side','top']:
        render_parts_png(shown,HERE/'views'/f'gripper-{view}.png',view,size_px=1000)
    details.update(finger_left_datum_hand_mm=left.tolist(),finger_right_datum_hand_mm=right.tolist(),
        opening_at_display_pose_mm=round(2*(center[1]-left[1]),4),
        pad_mm=[gg.PAD_WIDTH,gg.PAD_HEIGHT,gg.PAD_T],jaw_tip_extension_mm=8.8,
        printcheck_slicer='BambuStudio crashed signal6; geometric checks do not certify slicing')
    (gdir/'design.json').write_text(json.dumps(details,indent=2))
    # Wrist reference is already present in full arm; do not duplicate that mesh.
    return [m for m in meshes if m['name']!='gripper-wrist-reference'],records,details

if __name__=='__main__':
    m,r,d=build();print(json.dumps({'parts':len(m),'opening_mm':d['opening_at_display_pose_mm']}))
