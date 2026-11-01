"""Rebuild ONLY bam-v2, preserving the imported GLB's upper mesh and rig contract.

Run: python3 design/bam-v2/build_direct_drive.py
Uses the installed Mechy Python environment; does not patch the shared engine.
The generic `mechy cad build` does not implement this variant's direct-drive base.
"""
from pathlib import Path
import sys, os
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/bam-v2-matplotlib')
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ENGINE_PY = Path('/Users/Carlo/Empire/mechy/engine/.venv/bin/python')
if Path(sys.prefix) != ENGINE_PY.parent.parent:
    os.execv(str(ENGINE_PY), [str(ENGINE_PY), str(Path(__file__).resolve()), *sys.argv[1:]])
sys.path.insert(0, str(HERE/'printed'))
import copy, csv, hashlib, json, math, struct
import numpy as np
import yaml
from build123d import *
from base_geometry import *
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
import hardware as hw
from mechy.arm_model import ArmModel
from mechy.cad import ref_arm as RA
from mechy.cad.ref_arm import build_design, RefPart, params_hash, mesh_metrics, write_stl
from mechy.cad.glb import write_glb, read_glb, node_world
from mechy.cad.mjcf import build_mjcf
from mechy.cad.outputs import loads
from mechy.cad.render import render_parts_png

REF = HERE/'reference/belt-drive'
# Same per-node link stretch and shift the engine applies to the vendor solids (ref_arm.build_design).
STRETCH = {'upper_arm':(RA.S_ST,RA.U1),'pleuel':(RA.L_ST,RA.U1),'bend_lower':(RA.B0_ST,RA.U1),
           'forearm':(RA.E_ST,RA.U2),'bend_upper':(RA.T2_ST,RA.U2)}
SHIFT = {'triplate':RA._D1,'forearm':RA._D1,'bend_upper':RA._D1,'hand':RA._add(RA._D1,RA._D2)}
def dump(path, data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2)+'\n')
def write_csv(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def mesh(s):
    v,t=s.tessellate(0.08,0.15)
    return np.array([[p.X,p.Y,p.Z] for p in v]), np.asarray(t,np.uint32)
def rgba(h):
    return tuple(int(h[i:i+2],16)/255 for i in (1,3,5))+(1.0,)
def read_meshes(path):
    raw=path.read_bytes();g=read_glb(path)
    jslen=struct.unpack_from('<I',raw,12)[0]
    blob=raw[28+jslen:]
    def acc(idx):
        a=g['accessors'][idx];b=g['bufferViews'][a['bufferView']]
        dtype={5126:'<f4',5125:'<u4',5123:'<u2'}[a['componentType']]
        n={'VEC3':3,'SCALAR':1}[a['type']]
        return np.frombuffer(blob,dtype=dtype,count=a['count']*n,
            offset=b.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,n).copy()
    parent={c:i for i,n in enumerate(g['nodes']) for c in n.get('children',[])}
    parts=[]
    for i,n in enumerate(g['nodes']):
        if 'mesh' not in n:continue
        m=g['meshes'][n['mesh']];pr=m['primitives'][0]
        parts.append(dict(name=n['name'],node=g['nodes'][parent[i]]['name'],
            v=acc(pr['attributes']['POSITION']),t=acc(pr['indices']).reshape(-1,3),
            rgba=g['materials'][pr['material']]['pbrMetallicRoughness']['baseColorFactor']))
    tree=[]
    for i,n in enumerate(g['nodes']):
        if 'mesh' in n or n['name']=='arm':continue
        tree.append(dict(name=n['name'],parent=g['nodes'][parent[i]]['name'],
            translation=n.get('translation'),rotation=n.get('rotation'),extras=n.get('extras')))
    return g,parts,tree

def build():
    p=yaml.safe_load((REF/'params.yaml').read_text())
    p['name']='bam-v2'
    p['joints'][0].update(gear_ratio=1,drive_type='direct',transmission_efficiency_estimate=0.98)
    p['ref_arm']['base_drive']='direct'
    p['ref_arm']['base_motor_pulley_teeth']=None
    p['ref_arm']['base_belt']=None
    p['direct_drive']={
        'generator':'design/bam-v2/build_direct_drive.py',
        'motor_axis_xyz_mm':[0,0,MOTOR_FACE], 'motor_shaft_axis':[0,0,1],
        'turntable_mating_z_mm':TOP,'upper_geometry':'preserved from reference/belt-drive/arm.glb',
        'coupling':'5 mm metal flange, 22 mm OD, 16 mm PCD (PCD unverified)',
        'support':'51105 axial bearing plus printed running journal; load/wear unverified',
        'scope':'bam-v2 only', 'floor_z_mm':FLOOR,
        'motor_dimensions_verified':False,'print_release':False}
    (HERE/'params.yaml').write_text(yaml.safe_dump(p,sort_keys=False))
    old_mp=json.loads((REF/'mass_props.json').read_text())
    micro=old_mp['motor_map']['microsteps']
    arm=ArmModel(p,drivers_hw=[{'microsteps':micro}])
    d=build_design(arm)
    original,old_parts,tree=read_meshes(REF/'arm.glb')
    assert len(old_parts)==len(d.parts), 'Reference engine changed: map imported meshes explicitly.'
    keep=[];parts=[];removed=[];renamed=[];legacy_gripper=[]
    for op,dp in zip(old_parts,d.parts):
        assert op['node']==dp.node and op['name']==dp.name
        if op['node']=='base' or op['name']=='yaw_90T_gear':
            removed.append(op['name']);continue
        # The engine's classifier labels the four shoulder bearings F624ZZ and the wrist bearing
        # "gripper"; their solids have 6 mm bores (13 x 15 flange x 5), i.e. F686ZZ on the M6 axles.
        new=None;ext=np.sort(np.ptp(op['v'],axis=0)*1000)
        if op['node']=='turntable' and op['name'].startswith('bearing_F624ZZ'):
            new=f"bearing_F686ZZ_shoulder_{sum(r['new'].startswith('bearing_F686ZZ_shoulder') for r in renamed)+1}"
        elif op['node']=='hand' and op['name'].startswith('gripper') and np.allclose(ext,[5,15,15],atol=0.3):
            new='bearing_F686ZZ_wrist_1'
        if new:
            renamed.append(dict(index=len(parts),old=op['name'],new=new,recolored=True))
            op=dict(op,name=new,rgba=list(rgba(BEARING_COLOR)))
            dp.name=dp.label=new;dp.kind='bearing';dp.mass_kg=RA.CATALOG_MASS['f686']
            dp.color=rgba(BEARING_COLOR);dp.bom_item='F686ZZ flanged bearing';dp.printed_ref=None
        if op['node']=='hand' and op['name'].startswith('gripper'):
            removed.append(op['name']);legacy_gripper.append(op);continue
        parts.append(op)
        dp.v=op['v'].astype(float)*1000;dp.t=op['t'];keep.append(dp)
    preserved_count=len(keep)
    d.parts=keep.copy()
    assembly=[]
    def add_part(name,shape,node,kind,color,model,pos=(0,0,0),rot=(0,0,0),mass=None,printed_ref=None):
        v,t=mesh(shape)
        parts.append(dict(name=name,node=node,v=v/1000,t=t,rgba=rgba(color)))
        d.parts.append(RefPart(name=name,ref=printed_ref or name,kind=kind,node=node,
            v=v,t=t,color=rgba(color),label=name,step='base',mass_kg=mass,printed_ref=printed_ref))
        rec=dict(id=name,model=str(model.relative_to(ROOT)),kind='printed' if printed_ref else 'bought',joint_node=node,
                 position=list(pos),rotation=list(rot),color=color)
        if printed_ref:rec['material']='PETG'
        assembly.append(rec)
    for name,(fn,top,color) in PARTS.items():
        export_part(name)
        add_part(name,fn(),'base' if name in ('yaw-base-housing','yaw-bearing-cover') else 'turntable',
            'printed',color,HERE/'printed'/f'{name}.step',(0,0,top),(180,0,0),printed_ref=name)
    # Motor turned 180 deg so its plug faces the -X cable port; the bolt pattern is symmetric.
    motor=import_step(str(ROOT/'parts/models/nema17-42shdc.step'))
    add_part('yaw-motor-direct',Pos(0,0,MOTOR_FACE)*Rot(0,0,180)*motor,'base','motor','#2e3036',
             ROOT/'parts/models/nema17-42shdc.step',(0,0,MOTOR_FACE),(0,0,180),mass=0.28)
    # Plug and cable-bend keep-out: checked in assembly.yaml only, not drawn in the viewer.
    assembly.append(dict(id='yaw-motor-plug-keepout',model='parts/models/nema17-plug-keepout.step',
        kind='bought',joint_node='base',position=[0,0,MOTOR_FACE],rotation=[0,0,180],color='#ff5a5a',
        note='keep-out volume for the motor plug and cable bend, not a purchased part'))
    coupling=import_step(str(ROOT/'parts/models/flange-coupling-5mm.step'))
    add_part('yaw-flange-coupling',Pos(0,0,COUPLER_TOP)*coupling,'turntable','pulley',METAL_COLOR,
             ROOT/'parts/models/flange-coupling-5mm.step',(0,0,COUPLER_TOP),mass=0.012)
    models=HERE/'models';models.mkdir(exist_ok=True)
    for old in models.glob('*.step'):old.unlink()
    bearing=hw.thrust_51105()
    export_step(bearing,str(models/'bearing-51105.step'))
    add_part('yaw-thrust-bearing',Pos(0,0,BEARING_BOTTOM)*bearing,'base','bearing',METAL_COLOR,
             models/'bearing-51105.step',(0,0,BEARING_BOTTOM),mass=0.056)
    # Fasteners are explicit solids. Thread cylinders are nominal envelopes, not helical threads.
    cache={}
    def stock(key,fn):
        if key not in cache:
            f=models/f'{key}.step';s=fn();export_step(s,str(f));cache[key]=(s,f)
        return cache[key]
    def fastener(name,key,fn,node,pos,flip=False,mass=0.0015):
        s,f=stock(key,fn);rot=(180,0,0) if flip else (0,0,0)
        add_part(name,Pos(*pos)*Rot(*rot)*s,node,'fastener',METAL_COLOR,f,pos,rot,mass=mass)
    allow=[];reasons=[]
    for i,(x,y) in enumerate(( (x,y) for x in (-PITCH/2,PITCH/2) for y in (-PITCH/2,PITCH/2) )):
        name=f'motor-m3x10-{i+1}'
        fastener(name,'m3x10-shcs',lambda:hw.shcs(3,10),'base',(x,y,BEARING_BOTTOM-4.5))
        allow.append([name,'yaw-motor-direct']);reasons.append('M3 screw into the motor tapped hole; 4.5 mm nominal engagement, actual thread depth unverified.')
    for i,(x,y) in enumerate(COVER_HOLES):
        name=f'cover-m3x25-{i+1}'
        fastener(name,'m3x25-shcs',lambda:hw.shcs(3,25),'base',(x,y,COVER_SEAT))
        # Heat-set insert flush with the deck top; the screw passes its full 5.7 mm length.
        fastener(f'cover-m3-insert-{i+1}','m3-heatset-insert',hw.heatset_m3,'base',(x,y,BEARING_BOTTOM),flip=True,mass=0.0004)
        allow.append([name,f'cover-m3-insert-{i+1}']);reasons.append('M3 thread in the heat-set insert.')
        allow.append([f'cover-m3-insert-{i+1}','yaw-base-housing']);reasons.append('Heat-set insert knurl (4.6 mm) melted into its 4.0 mm hole by design.')
    for i,a in enumerate(ANCHOR_ANGLES):
        x,y=ANCHOR_R*math.cos(math.radians(a)),ANCHOR_R*math.sin(math.radians(a))
        # Shown as M4x12 seated on the foot; the length and anchor type depend on the bench.
        fastener(f'anchor-m4x12-{i+1}','m4x12-shcs',lambda:hw.shcs(4,12),'base',(x,y,FLOOR+FOOT_H))
    for i,(x,y) in enumerate(COUPLER_XY):
        name=f'coupling-m3x10-csk-{i+1}'
        fastener(name,'m3x10-csk',lambda:hw.csk(3,10),'turntable',(x,y,TOP-0.15))
        # Nut against the coupling flange underside (flange 2 mm thick below COUPLER_TOP).
        fastener(f'coupling-m3-nut-{i+1}','m3-nut',lambda:hw.nut(3),'turntable',(x,y,COUPLER_TOP-2),flip=True,mass=0.0005)
        allow.append([name,f'coupling-m3-nut-{i+1}']);reasons.append('Nominal thread engagement.')
    for i,(x,y) in enumerate(((x,y) for x in (-BODY_PITCH/2,BODY_PITCH/2) for y in (-BODY_PITCH/2,BODY_PITCH/2))):
        name=f'body-m3x12-{i+1}'
        # Original main-body mesh: floor=25.697, counterbore seat=28.197, top=31.697 mm.
        fastener(name,'m3x12-shcs',lambda:hw.shcs(3,12),'turntable',(x,y,28.197))
        fastener(f'body-m3-nut-{i+1}','m3-nut',lambda:hw.nut(3),'turntable',(x,y,BEARING_TOP+5.4),flip=True,mass=0.0005)
        allow.append([name,f'body-m3-nut-{i+1}']);reasons.append('Nominal M3 thread; 0.5 mm beyond the captive nut.')
    # The upper body and its existing hardware remain imported meshes. Their attachment
    # holes are checked numerically; the STEP check deliberately covers only this new base.
    doc={'scope':'New base solids only. Full upper geometry and rig are in arm.glb; upper hardware is in upper_hardware.yaml.',
         'min_clearance_mm':0.1,'parts':assembly,'allow_contact':allow,
         'allow_contact_reasons':reasons,
         'unverified':['motor and coupling dimensions','printed journal wear and cover lip strength',
                       'yaw endstop mount/cam must be redesigned; old socket mount removed',
                       'upper vendor meshes have no STEP solids; not covered by this boolean check']}
    (HERE/'assembly.yaml').write_text(yaml.safe_dump(doc,sort_keys=False))
    # ---- upper-arm hardware: belts, missing bearings, pivot axles, screws and nuts
    upper_records=[]
    def to_node(v,center,g):
        off=np.zeros(3);c=np.asarray(center,float)
        if g in STRETCH:off+=RA._stretch(c[None],*STRETCH[g])[0]-c
        if g in SHIFT:off+=np.array([SHIFT[g][0],0.0,SHIFT[g][1]])
        vw=v+off-np.array([RA.YAW_ST[0],RA.YAW_ST[1],RA.SOCKET_BOTTOM_ST])
        spec=RA.NODE_SPEC[g];piv=RA.PIVOTS.get(spec['pivot'],(0.0,0.0)) if spec['pivot'] else (0.0,0.0)
        return (RA._ry(RA.ABS_REST[g])@(vw-np.array([piv[0],0.0,piv[1]])).T).T
    def add_upper(name,solid,f,node,origin,Rm,kind,color,mass,bom,note):
        v,t=mesh(solid)
        vl=to_node(v@Rm.T+np.asarray(origin,float),origin,node)
        parts.append(dict(name=name,node=node,v=vl/1000,t=t,rgba=rgba(color)))
        d.parts.append(RefPart(name=name,ref=name,kind=kind,node=node,v=vl,t=t,color=rgba(color),
            label=name,step='arm',mass_kg=mass,bom_item=bom))
        upper_records.append(dict(id=name,model=str(f.relative_to(ROOT)),kind=kind,joint_node=node,
            frame='vendor STEP frame, before link stretch/shift',origin_mm=[round(float(a),3) for a in origin],
            axes=Rm.round(6).T.tolist(),bom=bom,note=note))
    for name,key,node,origin,zdir,bom,note in hw.UPPER:
        s,f=stock(hw.model_name(key),lambda:hw.model(key))
        kind={'shcs':'fastener','nut':'fastener','bearing':'bearing','washer':'fastener'}[key[0]]
        if key[0]=='bearing':mass=RA.CATALOG_MASS['f624' if key[1]=='F624ZZ' else 'f686']
        elif key[0]=='washer':mass=0.0003
        else:mass={'shcs':0.0015,'nut':0.0008}[key[0]] if key[1]<6 else {'shcs':0.012,'nut':0.0025}[key[0]]
        add_upper(name,s,f,node,origin,hw.frame(zdir),kind,BEARING_COLOR if kind=='bearing' else METAL_COLOR,mass,bom,note)
    belt=hw.belt(6.11,28.42,hw.BELT_CENTRE)
    bf=models/'belt-gt2-6mm-20t-90t-c39.step';export_step(belt,str(bf))
    for name,y_edge in hw.BELTS:
        Rm=np.column_stack([[1,0,0],[0,0,1],[0,-1,0]])   # local x->X, y->Z, extrusion z->-Y
        add_upper(name,belt,bf,'turntable',(100.0,y_edge,23.5),Rm,'belt',BELT_COLOR,0.003,
            'GT2 closed belt 200 mm',f'20T motor pulley to printed 90T pulley, centres {hw.BELT_CENTRE:.1f} mm; pitch length {hw.gt2_length(20,90,hw.BELT_CENTRE):.1f} mm')
    (HERE/'upper_hardware.yaml').write_text(yaml.safe_dump({'scope':'Hardware added to the preserved upper arm. Origins are in the vendor STEP frame; '
        'axes columns are the local x/y/z of each model. Screw frames: head bearing face at z=0, shank toward -z. '
        'Bearing frames: flange face at z=0, ring toward +z. Nut frames: bearing face at z=0.',
        'renamed_vendor_meshes':renamed,'parts':upper_records},sort_keys=False))
    # The 20sffactory arm's own servo gripper (ftobler): vendor fingers kept, servo base/disc + MG90S.
    import gripper_ftobler
    gm,gd=gripper_ftobler.build(legacy_gripper)
    for item in gm:
        parts.append(item)
        d.parts.append(RefPart(name=item['name'],ref=item['name'],kind=item.get('kind','bought'),node='hand',
            v=item['v']*1000,t=item['t'],color=item['rgba'],label=item['name'],step='toolhead',
            mass_kg=item.get('mass_kg'),printed_ref=item.get('printed_ref')))
    p['ref_arm']['gripper_servo']='mg90s'
    p.pop('gripper_upgrade',None)
    p['gripper']={'generator':'design/bam-v2/gripper_ftobler.py',**gd}
    (HERE/'params.yaml').write_text(yaml.safe_dump(p,sort_keys=False))
    d.info['homing'][0].update(mount='new pedestal: bracket unresolved',trigger='new cam unresolved',
                             homes='Do not home yaw until bracket, cam and steps are calibrated')
    mp=d.mass_props()
    for b in ('upper_arm','forearm'):mp['bodies'][b]=old_mp['bodies'][b]
    mp['motor_map']=arm.motor_map()
    mp['motor_map_note']='a=(q0,q1,q1+q2,q123); ratios [1,5.625,5.625,4.5]; wrist passive'
    mp['estimate_note']='Catalog motor masses and shell/infill estimates; new base hardware envelopes.'
    mp['params_hash']=params_hash(p)
    dump(HERE/'mass_props.json',mp);arm.mass_props=mp
    meta=copy.deepcopy(original['scenes'][original.get('scene',0)].get('extras',{}))
    meta.update(variant='bam-v2',base_drive='direct',base_gear_ratio=1)
    result=write_glb(HERE/'arm.glb',parts,d.origins,meta['rest_q_rad'],meta=meta,tree=tree)
    posed=[];g=read_glb(HERE/'arm.glb')
    q=arm.ready_pose()
    for part in parts:
        T=node_world(g,part['node'],q)
        posed.append((part['v']@T[:3,:3].T+T[:3,3],part['t'],part['rgba']))
    va=[];ta=[];off=0
    for v,t,_ in posed:va.append(v*1000);ta.append(t+off);off+=len(v)
    write_stl(HERE/'arm.stl',np.vstack(va),np.vstack(ta))
    xml=build_mjcf(arm)
    xml=xml.replace('name="floor" type="plane"','name="floor" pos="0 0 '+str(FLOOR/1000)+'" type="plane"')
    (HERE/'arm.xml').write_text(xml)
    import mujoco
    mj=mujoco.MjModel.from_xml_path(str(HERE/'arm.xml'))
    ld=loads(arm)
    base=ld['joints'][0];base['drive_type']='direct';base['transmission_efficiency_estimate']=0.98
    base['joint_torque_available_nm']=round(base['holding_torque_nm']*0.98,4)
    ld['note']='Estimate using inherited generic motor curve, not measured 42SHDC3026-15B performance. 57 g legacy ball scenario; not a 600 g payload certification.'
    ld['belt_efficiency_applies_to']=['shoulder','elbow'];dump(HERE/'loads.json',ld)
    # Keep the original upper print files and their rows unchanged; move active prints into printed/.
    old_rows=list(csv.DictReader((REF/'print_list.csv').open()))
    rows=[]
    import shutil
    archived_stls=REF/'stl';archived_stls.mkdir(exist_ok=True)
    for old in (HERE/'stl').glob('*.stl'):
        if not (archived_stls/old.name).exists():shutil.copy2(old,archived_stls/old.name)
    for row in old_rows:
        if row['part'] in ('arm_socket','arm_rotategear') or row['part'].startswith('grip_'):continue
        src=REF/row['stl'];target=HERE/'printed'/src.name
        shutil.copy2(src,target);row['stl']='printed/'+target.name;rows.append(row)
    for name,(fn,_,_) in PARTS.items():
        volume=fn().volume/1000;grams=volume*1.27*0.6
        rows.append(dict(part=name,qty=1,material='PETG',orientation='as modeled; top mating face on bed',
            est_grams=round(grams,1),est_grams_total=round(grams,1),infill='40%; 5 walls (estimate)',
            volume_cm3=round(volume,2),stl='printed/'+name+'.stl',source='bam-v2 direct-drive generator; fit unverified'))
    import runpy
    runpy.run_path(str(HERE/'printed/yaw-fits-coupon.py'))
    coupon=import_step(str(HERE/'printed/yaw-fits-coupon.step'))
    volume=coupon.volume/1000;grams=volume*1.27*0.6
    rows.append(dict(part='yaw-fits-coupon',qty=2,material='PETG',orientation='as modeled; flat base on bed; two copies mate for running-fit test',
        est_grams=round(grams,1),est_grams_total=round(round(grams,1)*2,1),infill='40%; same settings as base',
        volume_cm3=round(volume,2),stl='printed/yaw-fits-coupon.stl',source='fit-test coupon, not an assembly part'))
    import shutil
    for name,src in gripper_ftobler.PRINT.items():
        qty=2 if name=='gripper-finger' else 1
        shutil.copyfile(gripper_ftobler.STL/src,HERE/'printed'/f'{name}.stl')
        vv,tt=RA.read_stl(gripper_ftobler.STL/src);volume,_,_,area=RA.mesh_metrics(vv,tt);grams=RA.print_mass_g(volume,area)
        rows.append(dict(part=name,qty=qty,material='PLA',orientation='flat on the bed (vendor file orientation)',
             est_grams=round(grams,1),est_grams_total=round(grams*qty,1),infill='25%',
             volume_cm3=round(volume/1000,2),stl='printed/'+name+'.stl',source=f'20sffactory Community Robot Arm (CC BY 4.0): {src}'))
    for f in (HERE/'printed').glob('grip_*.stl'):f.unlink()
    write_csv(HERE/'print_list.csv',rows)
    bom=list(csv.DictReader((REF/'bom.csv').open()))
    # How many of each vendor item the CAD now shows (vendor quantities are kept as bought).
    def count(prefix):return sum(1 for r in upper_records if r['bom']==prefix)
    modeled={'GT2 pulley 20T':'2 (vendor solids)','GT2 closed belt 200 mm':f"{count('GT2 closed belt 200 mm')}",
        'F624ZZ flanged bearing':f"{count('F624ZZ flanged bearing')}",
        'F686ZZ flanged bearing':f"{count('F686ZZ flanged bearing')+sum(1 for r in renamed)+2}: shoulder 5, elbow 3, wrist 2",
        'M3x6 screw':f"{count('M3x6 socket head screw')+8}: 8 motor, 4 stabilizer, 4 endstop bracket, 8 pulley-to-link (vendor solids)",
        'M4x10 screw':f"{count('M4x10 socket head screw')}",'M4x16 screw':f"{count('M4x16 socket head screw')}",
        'M4x20 screw':f"{count('M4x20 socket head screw')}",'M4 nut':f"{count('M4 nut')}",
        'M6x40 screw':f"{count('M6x40 socket head screw')}",'M6x50 screw':f"{count('M6x50 socket head screw')}",
        'M6 nut':f"{count('M6 nut')}",'51105 thrust bearing':'1'}
    for row in bom:
        row['modeled_in_cad']=modeled.get(row['item'],'')
        if row['item'].startswith('GT2 '):row['qty']='2';row['used_for']='shoulder and elbow only; yaw is direct drive'
        if row['item']=='51105 thrust bearing':row['used_for']='direct-drive housing deck to spindle axial support'
        if row['item']=='Endstop microswitch':row['used_for']='X/Y homing retained; yaw needs a new bracket/cam and calibration'
        if row['item']=='F624ZZ flanged bearing':row['used_for']='M4 link pivots: pleuel x2, lower levelling link x2, upper levelling link x2'
        if row['item']=='F686ZZ flanged bearing':row['used_for']='M6 axles: shoulder 5, elbow 3, wrist 2 seats modeled; 2 extra in vendor count'
        if row['item']=='M6x20 screw':row['used_for']='belt-drive yaw socket axle; not used by the direct-drive base';row['modeled_in_cad']='0 (not needed)'
    def bom_add(item,qty,spec,used,source,price=''):
        bom.append(dict(item=item,qty=qty,spec=spec,used_for=used,source=source,est_unit_usd=price,modeled_in_cad=str(qty)))
    bom_add('5 mm flange coupling',1,'22 mm flange; 16 mm PCD and 2 mm flange thickness UNVERIFIED',
        'direct yaw shaft to turntable','existing parts/models/flange-coupling-5mm.yaml; VXB page checked 2026-10-30')
    bom_add('M3x10 socket head screw',4,'4.5 mm nominal motor thread engagement; verify actual thread depth','yaw motor to housing deck','design quantity')
    bom_add('M3x10 countersunk screw',4,'90 degree flat head','flange coupling to adapter','design quantity')
    bom_add('M3x12 socket head screw',4,'28.197 mm original counterbore seat; 0.5 mm thread beyond nut','main body through adapter/spindle','replaces original yaw attachment screws')
    bom_add('M3x25 socket head screw',4,'heads in the cover lip counterbores; full insert engagement, tip 1.2 mm past it','bearing cover to housing deck','design quantity')
    bom_add('M3 heat-set insert, 5.7 mm long',4,'about 4.6 mm knurl OD into 4.0 mm deck holes; check the insert maker\'s hole size','housing deck top','design quantity; exact insert not selected')
    bom_add('M3 nut (direct-drive base)',8,'4 coupling + 4 upper attachment; 5.5 AF x 2.4','direct-drive fasteners','design quantity')
    bom_add('M3x12 socket head screw (toolhead)',3,'from under the manipulator into the gripper base 2.4 mm holes','gripper base to manipulator','vendor holes')
    bom_add('M2x8 screw (gripper servo)',2,'MG90S tabs to the gripper base','gripper','owned studio stock')
    bom_add('Shim ring DIN 988 6x12x0.5',count('Shim ring DIN 988 6x12x0.5'),'steel; buy a 10-pack for spares',
        'shoulder axle x3, wrist axle x2: take up axial slack at the bearing inner rings','design quantity')
    bom_add('M4 base anchor screw',4,'4.8 mm holes through the housing foot ring; shown as M4x12, length and type depend on the support','base restraint','unresolved bench attachment; no purchase selected')
    write_csv(HERE/'bom.csv',bom)
    # Archived original files are under reference/. There is one active print directory.
    for f in (HERE/'stl').glob('*.stl'):f.unlink()
    if (HERE/'stl').exists() and not any((HERE/'stl').iterdir()):(HERE/'stl').rmdir()
    views=HERE/'views';views.mkdir(exist_ok=True)
    for view in ('iso','front','side','top'):
        render_parts_png(posed,views/(view+'.png'),view,size_px=1000)
    render_parts_png(posed,HERE/'thumb.png','hero',size_px=900)
    dump(HERE/'build_result.json',dict(glb=result,removed_base_meshes=removed,
        upper_meshes_preserved=preserved_count,mjcf_valid=True,variant='bam-v2'))
    print(json.dumps({'built':'design/bam-v2/arm.glb','upper_meshes_preserved':preserved_count,'mjcf_valid':True}))
if __name__=='__main__':build()
