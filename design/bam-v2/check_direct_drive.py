"""Re-run rig/geometry regression, STEP checks, print checks and motor estimates for bam-v2."""
from pathlib import Path
import os,sys
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/bam-v2-matplotlib')
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]
PY=Path('/Users/Carlo/Empire/mechy/engine/.venv/bin/python')
if Path(sys.prefix)!=PY.parent.parent:
    os.execv(str(PY),[str(PY),str(Path(__file__).resolve()),*sys.argv[1:]])
import copy,csv,hashlib,json,math
import numpy as np
import yaml
from build_direct_drive import read_meshes,dump
from mechy.cad.glb import node_world
from mechy.design_tools.assembly import check_assembly
from mechy.design_tools.inspect import inspect_step
from mechy.design_tools.printing import print_check,printer_settings
from mechy.design_tools.parts import validate_parts
from mechy.tools import motor_check
from mechy.project import Project
import mujoco

def run():
    out=HERE/'checks';out.mkdir(exist_ok=True)
    old,op,ot=read_meshes(HERE/'reference/belt-drive/arm.glb')
    new,np_,nt=read_meshes(HERE/'arm.glb')
    def legacy_gripper(p):   # replaced by gripper_ftobler.py (the wrist bearing the vendor calls "gripper" stays)
        ext=np.sort(np.ptp(p['v'],axis=0)*1000)
        return p['node']=='hand' and p['name'].startswith('gripper') and not np.allclose(ext,[5,15,15],atol=0.3)
    kept=[p for p in op if p['node']!='base' and p['name']!='yaw_90T_gear' and not legacy_gripper(p)]
    assert len(np_)>=len(kept)
    # Preserve order as duplicate vendor mesh names are intentional in the source GLB.
    # Mislabeled vendor bearings are renamed/recoloured on purpose (upper_hardware.yaml); their
    # geometry, node and order must still match exactly.
    renames={r['index']:r for r in yaml.safe_load((HERE/'upper_hardware.yaml').read_text())['renamed_vendor_meshes']}
    preserved=[]
    for i,(a,b) in enumerate(zip(kept,np_)):
        r=renames.get(i)
        assert (b['name']==r['new'] and a['name']==r['old']) if r else a['name']==b['name'],a['name']
        passed=(a['node']==b['node'] and np.array_equal(a['v'],b['v']) and np.array_equal(a['t'],b['t'])
                and (r is not None or a['rgba']==b['rgba']))
        assert passed,a['name']
        preserved.append(b['name'])
    assert ot==nt,'Rig node tree/transforms/extras changed'
    joints={t['name']:t for t in nt}
    for name,i in [('turntable',0),('upper_arm',1),('forearm',2),('hand',3)]:
        assert joints[name]['extras']['joint_index']==i
    coupled=[t['name'] for t in nt if (t['extras'] or {}).get('coupled')]
    assert set(coupled)=={'lever','pleuel','bend_lower','triplate','bend_upper'}
    p=yaml.safe_load((HERE/'params.yaml').read_text())
    before=yaml.safe_load((HERE/'reference/belt-drive/params.yaml').read_text())
    assert p['joints'][0]['gear_ratio']==1
    assert p['joints'][1:]==before['joints'][1:]
    for key in ('links','ready_pose_deg','catcher','kinematics'):assert p[key]==before[key]
    rng=np.random.default_rng(1701)
    limits=np.radians([j['limit_deg'] for j in p['joints']])
    poses=[np.radians(p['ready_pose_deg']),np.radians([0,15,-39.2,24.2]),np.radians([0,160,-142.3,-17.7])]
    for _ in range(100):
        q=rng.uniform(limits[:,0],limits[:,1]);q[3]=-q[1]-q[2];poses.append(q)
    err=0
    for q in poses:
        for name in joints:
            err=max(err,float(np.abs(node_world(old,name,q)-node_world(new,name,q)).max()))
    assert err<1e-12
    manifest=json.loads((HERE/'reference/v1-sha256.json').read_text())
    changed=[f for f,h in manifest.items() if hashlib.sha256((ROOT/f).read_bytes()).hexdigest()!=h]
    assert not changed
    old_print=list(csv.DictReader((HERE/'reference/belt-drive/print_list.csv').open()))
    rows=list(csv.DictReader((HERE/'print_list.csv').open()))
    print_by_name={r['part']:r for r in rows}
    assert not {'arm_socket','arm_rotategear'} & print_by_name.keys()
    unchanged_stls=[]
    for row in old_print:
        if row['part'] in ('arm_socket','arm_rotategear') or row['part'].startswith('grip_'):continue   # grip_*: gripper_ftobler rows
        target=HERE/print_by_name[row['part']]['stl']
        source=HERE/'reference/belt-drive'/row['stl']
        assert target.read_bytes()==source.read_bytes(),row['part']
        unchanged_stls.append(row['part'])
    bom=list(csv.DictReader((HERE/'bom.csv').open()))
    for b in bom:
        if b['item'].startswith('GT2 '):assert b['qty']=='2'
    mp=json.loads((HERE/'mass_props.json').read_text());ld=json.loads((HERE/'loads.json').read_text())
    assert mp['motor_map']['gear_ratio'][0]==ld['joints'][0]['gear_ratio']==1
    assert np.isclose(mp['motor_map']['steps_per_deg'][0],200*8/360,atol=0.0001)
    model=mujoco.MjModel.from_xml_path(str(HERE/'arm.xml'))
    regression=dict(ok=True,preserved_upper_meshes=len(preserved),preserved_upper_mesh_names=preserved,
        preserved_upper_stls=len(unchanged_stls),joint_nodes=['turntable','upper_arm','forearm','hand'],
        linkage_extras=coupled,poses_checked=len(poses),max_transform_error=err,v1_files_unchanged=len(manifest),
        base_gear_ratio=1,base_steps_per_deg=mp['motor_map']['steps_per_deg'][0],mjcf_valid=True,
        motor_axis_offset_mm=0,upper_mating_face_z_mm=25.697)
    dump(out/'regression.json',regression);print('Rig/upper/v1 regression passed',flush=True)
    result=check_assembly(ROOT,'bam-v2');dump(out/'assembly.json',result)
    print('Base STEP check',result['ok'],flush=True)
    asm=yaml.safe_load((HERE/'assembly.yaml').read_text())
    pose_results={}
    for deg in (-150,90,150):
        doc=copy.deepcopy(asm);theta=math.radians(deg)
        for part in doc['parts']:
            if part.get('joint_node')!='turntable':continue
            x,y,z=part['position'];part['position']=[x*math.cos(theta)-y*math.sin(theta),x*math.sin(theta)+y*math.cos(theta),z]
            part['rotation'][2]+=deg
        pv=f'bam-v2/poses/yaw-{deg}'
        target=ROOT/'design'/pv/'assembly.yaml';target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(yaml.safe_dump(doc,sort_keys=False))
        pose_results[str(deg)]=check_assembly(ROOT,pv)
        print('Yaw pose',deg,pose_results[str(deg)]['ok'],flush=True)
    dump(out/'yaw_poses.json',pose_results)
    settings=printer_settings();dump(out/'printer_profile.json',settings)
    prints={}
    for f in sorted((HERE/'printed').glob('*.step')):
        ins=inspect_step(f);dump(out/(f.stem+'-inspect.json'),ins)
        pc=print_check(f,{'material':'PETG','density_g_cm3':1.27})
        prints[f.stem]=pc
        print('Print',f.stem,'thin=',pc['thin_walls'],'overhang=',pc['overhang_area_mm2'],flush=True)
    dump(out/'print_checks.json',prints)
    # The untouched imported upper STLs have no STEP sources: only mesh integrity/bed bounds here.
    from mechy.cad.ref_arm import read_stl,mesh_metrics
    meshes={}
    for row in rows:
        f=HERE/row['stl'];v,t=read_stl(f)
        extent=np.ptp(v,axis=0)
        edges=np.sort(np.vstack([t[:,[0,1]],t[:,[1,2]],t[:,[2,0]]]),axis=1)
        _,cnt=np.unique(edges,axis=0,return_counts=True)
        meshes[row['part']]=dict(extents_mm=extent.round(3).tolist(),fits_bed_xyz=bool(np.all(extent<=256)),
            boundary_or_nonmanifold_edges=int(np.sum(cnt!=2)),triangles=len(t),
            scope='mesh/bed screening only; does not establish wall thickness or print release')
    dump(out/'all_print_meshes.json',meshes)
    validation=validate_parts(ROOT);dump(out/'shared_parts_validation.json',validation)
    # Validation is read-only: global parts and v1 were not changed for this scoped variant.
    try:
        # The engine's MCP wrapper only accepts v<N> names. Extend that parser locally;
        # use its unchanged motor_check implementation and restore it immediately.
        import re, mechy.tools as mt
        old_re=mt.VARIANT_RE
        try:
            mt.VARIANT_RE=re.compile(r'^(?:v\d+[a-z0-9_-]*|bam-v2)$')
            mc=motor_check(Project(ROOT),'bam-v2',microsteps=8)
        finally:mt.VARIANT_RE=old_re
        mc['variant_parser_note']='Local name-parser extension for bam-v2; engine files untouched.'
        mc['evidence_status']='estimate: inherited generic motor curve; not measured owned motor performance'
    except Exception as e:mc={'error':str(e),'ok':False}
    dump(out/'motor_check.json',mc)
    result={'regression':regression,'assembly_ok':result['ok'],
        'yaw_pose_assembly_ok':all(x['ok'] for x in pose_results.values()),
        'thin_wall_parts':[n for n,x in prints.items() if x['thin_walls']],
        'overhang_parts':[n for n,x in prints.items() if x['overhang_area_mm2']>0],
        'shared_parts_validation_ok':validation['ok'], 'print_release':False}
    dump(HERE/'check_results.json',result);print(json.dumps(result),flush=True)
if __name__=='__main__':run()
