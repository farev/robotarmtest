"""Screen the added upper-arm hardware against every other mesh in arm.glb at sampled poses.

Vertices and triangle centres of each added part are tested for containment in the other
meshes (ray-parity, two ray directions must agree). This finds penetrations at the sampled
poses; it is not a boolean volume check and does not prove clearance between samples.
"""
from pathlib import Path
import os,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PY=Path('/Users/Carlo/Empire/mechy/engine/.venv/bin/python')
if Path(sys.prefix)!=PY.parent.parent:
    os.execv(str(PY),[str(PY),str(Path(__file__).resolve())])
import json
import numpy as np
import yaml
from build_direct_drive import read_meshes,dump
from mechy.cad.glb import node_world

def inside(points,v,t,direction):
    """Ray-parity containment of points in the closed mesh (v,t) along one direction."""
    a,b,c=v[t[:,0]],v[t[:,1]],v[t[:,2]]
    e1,e2=b-a,c-a
    p=np.cross(direction,e2);det=np.einsum('ij,ij->i',e1,p)
    ok=np.abs(det)>1e-12;a,e1,e2,p,det=a[ok],e1[ok],e2[ok],p[ok],det[ok]
    inv=1/det
    hits=np.zeros(len(points),int);step=max(1,int(2e6//max(len(a),1)))
    for i0 in range(0,len(points),step):
        P=points[i0:i0+step]
        s=P[:,None,:]-a[None,:,:]
        u=np.einsum('nij,ij->ni',s,p)*inv
        q=np.cross(s,e1[None,:,:])
        w=np.einsum('j,nij->ni',direction,q)*inv
        tt=np.einsum('nij,ij->ni',q,e2)*inv
        hits[i0:i0+len(P)]=np.sum((u>=0)&(w>=0)&(u+w<=1)&(tt>1e-9),axis=1)
    return hits%2==1

def surface_distance(points,v,t):
    """Distance from each point to the nearest triangle of (v,t) (Ericson, closest point)."""
    a,b,c=v[t[:,0]],v[t[:,1]],v[t[:,2]]
    best=np.full(len(points),np.inf)
    for k,P in enumerate(points):
        ab,ac,ap=b-a,c-a,P-a
        d1=np.einsum('ij,ij->i',ab,ap);d2=np.einsum('ij,ij->i',ac,ap)
        bp=P-b;d3=np.einsum('ij,ij->i',ab,bp);d4=np.einsum('ij,ij->i',ac,bp)
        cp=P-c;d5=np.einsum('ij,ij->i',ab,cp);d6=np.einsum('ij,ij->i',ac,cp)
        va=d3*d6-d5*d4;vb=d5*d2-d1*d6;vc=d1*d4-d3*d2
        den=np.where(np.abs(va+vb+vc)>1e-18,va+vb+vc,1e-18)
        q=a+ab*(vb/den)[:,None]+ac*(vc/den)[:,None]                      # face region
        e=lambda cond,pt:np.where(cond[:,None],pt,q)
        q=e((vc<=0)&(d1>=0)&(d3<=0),a+ab*(d1/np.where(d1-d3!=0,d1-d3,1))[:,None])
        q=e((vb<=0)&(d2>=0)&(d6<=0),a+ac*(d2/np.where(d2-d6!=0,d2-d6,1))[:,None])
        w=(d4-d3)/np.where((d4-d3)+(d5-d6)!=0,(d4-d3)+(d5-d6),1)
        q=e((va<=0)&((d4-d3)>=0)&((d5-d6)>=0),b+(c-b)*w[:,None])
        q=e((d1<=0)&(d2<=0),a);q=e((d3>=0)&(d4<=d3),b);q=e((d6>=0)&(d5<=d6),c)
        best[k]=np.sqrt(((q-P)**2).sum(1)).min()
    return best

def world(part,g,q):
    T=node_world(g,part['node'],q)
    return (part['v']@T[:3,:3].T+T[:3,3])*1000

g,parts,_=read_meshes(HERE/'arm.glb')
doc=yaml.safe_load((HERE/'upper_hardware.yaml').read_text())
added={r['id'] for r in doc['parts']}
D1=np.array([0.5773503,0.5773503,0.5773503]);D2=np.array([-0.267261,0.534522,0.801784])
poses={'ready':[0,90,-90,0],'rest-like':[0,137.4,-111.4,-26.0],'reach':[0,40,-60,20],'folded':[0,150,-140,-10]}
results={}
for pname,qd in poses.items():
    q=np.radians(qd)
    W=[world(p,g,q) for p in parts]
    issues=[]
    for i,p in enumerate(parts):
        if p['name'] not in added:continue
        tri=W[i][p['t']].mean(axis=1)
        pts=np.vstack([W[i],tri])
        lo,hi=pts.min(0)-0.01,pts.max(0)+0.01
        for j,o in enumerate(parts):
            if j==i or o['node']=='base':continue
            olo,ohi=W[j].min(0),W[j].max(0)
            if np.any(olo>hi) or np.any(ohi<lo):continue
            cand=pts[np.all(pts>olo,axis=1)&np.all(pts<ohi,axis=1)]
            if not len(cand):continue
            hit=inside(cand,W[j],o['t'],D1)&inside(cand,W[j],o['t'],D2)
            if hit.any():
                inner=cand[hit]
                if len(inner)>150:inner=inner[np.random.default_rng(0).choice(len(inner),150,replace=False)]
                depth=float(surface_distance(inner,W[j],o['t']).max())
                issues.append(dict(part=p['name'],other=o['name'],points_inside=int(hit.sum()),
                                   points_tested=int(len(pts)),max_depth_mm=round(depth,3)))
    results[pname]=dict(q_deg=qd,issues=issues)
    print(pname,len(issues),flush=True)
# Classify by depth and by the intended joint the pair represents.
THREAD={('pleuel-pin-m4x16','upper_shank_140'):'M4 thread-formed into 3.76 mm hole',
        ('bend-lower-pin-m4x10','main_body'):'M4 thread-formed into 3.86 mm hole',
        ('triplate-lower-pin-nut','triplate'):'M4 nut corners (8.08 mm) pressed into 8.0 mm pocket',
        ('triplate-upper-pin-nut','triplate'):'M4 nut corners (8.08 mm) pressed into 8.0 mm pocket'}
def classify(x):
    a,b=x['part'],x['other']
    if (a,b) in THREAD:return 'intended: '+THREAD[(a,b)]
    if b.startswith('NEMA_17') and 'motor-' in a:return 'intended: screw in motor tapped hole (vendor motor solid has no holes)'
    if 'toolhead' in a and (b.startswith('gripper_motor') or b=='gripper-base'):return 'intended: M3 thread-formed into 2.4 mm gripper-base hole (mesh is the gripper base)'
    if ('nut' in a or 'nut' in b) and a.rsplit('-',1)[0]==b.rsplit('-',1)[0]:
        return 'intended: screw in its own nut (nut bore modelled at thread minor diameter)'
    if x['max_depth_mm']<=0.05:return 'contact (zero-gap seat or face, within 0.05 mm)'
    if x['max_depth_mm']<=0.2:return 'review: shallow overlap <= 0.2 mm (mesh tolerance or press fit)'
    return 'INTERFERENCE'
summary={}
for r in results.values():
    for x in r['issues']:
        x['class']=classify(x);k=(x['part'],x['other'])
        if k not in summary or x['max_depth_mm']>summary[k]['max_depth_mm']:summary[k]=x
interference=[x for x in summary.values() if x['class']=='INTERFERENCE']
review=[x for x in summary.values() if x['class'].startswith('review')]
out=dict(scope=__doc__.strip(),added_parts=len(added),poses=results,worst_by_pair=list(summary.values()),
         interference_count=len(interference),review_count=len(review),ok=not interference)
dump(HERE/'checks/upper_hardware_screen.json',out)
for x in sorted(summary.values(),key=lambda x:-x['max_depth_mm']):
    print(f"{x['part']:38s} {x['other']:42s} depth {x['max_depth_mm']:.3f}  {x['class']}")
print(json.dumps(dict(interference=len(interference),review=len(review),ok=not interference)))
