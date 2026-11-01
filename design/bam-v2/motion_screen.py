"""Screen retained moving mesh vertices against new base solids at joint-limit corners.

This detects penetrations at sampled poses. It is not continuous mesh collision certification.
"""
from pathlib import Path
import os,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PY=Path('/Users/Carlo/Empire/mechy/engine/.venv/bin/python')
if Path(sys.prefix)!=PY.parent.parent:
    os.execv(str(PY),[str(PY),str(Path(__file__).resolve())])
import json,itertools
import numpy as np
from build_direct_drive import read_meshes,dump
from mechy.cad.glb import node_world
from mechy.design_tools.assembly import load_assembly

g,parts,_=read_meshes(HERE/'arm.glb')
new_solid_ids={'yaw-base-housing','yaw-bearing-cover','yaw-motor-direct',
    'yaw-thrust-bearing','yaw-bearing-spindle','yaw-turntable-adapter','yaw-flange-coupling'}
poses=[];hits=[]
for yaw in (-150,0,150):
    variant='bam-v2' if yaw==0 else f'bam-v2/poses/yaw-{yaw}'
    solids=[p for p in load_assembly(ROOT,variant) if p.id in new_solid_ids]
    for shoulder,elbow in itertools.product((15,90,160),(-142.3,-90,-39.2)):
        q=np.radians([yaw,shoulder,elbow,-shoulder-elbow]);label=[yaw,shoulder,elbow,-shoulder-elbow]
        poses.append(label)
        for part in parts:
            if part['node'] in ('base','turntable'):continue
            T=node_world(g,part['node'],q)
            v=(part['v']@T[:3,:3].T+T[:3,3])*1000
            for solid in solids:
                bb=solid.shape.bounding_box()
                lo=np.array([bb.min.X,bb.min.Y,bb.min.Z])+0.01
                hi=np.array([bb.max.X,bb.max.Y,bb.max.Z])-0.01
                cand=v[np.all(v>lo,axis=1)&np.all(v<hi,axis=1)]
                for xyz in cand:
                    if solid.shape.is_inside(tuple(xyz),tolerance=1e-5):
                        hits.append({'q_deg':label,'mesh':part['name'],'base_solid':solid.id,
                                     'penetrating_vertex_mm':xyz.round(3).tolist()});break
out={'poses':poses,'pose_count':len(poses),'penetrations':hits,
     'scope':'Vertex containment at sampled poses, not continuous collision checking or all triangle intersections.',
     'no_sampled_penetrations':not hits}
dump(HERE/'checks/motion_screen.json',out)
print(json.dumps(out))
