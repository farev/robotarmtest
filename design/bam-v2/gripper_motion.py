"""Analytic slider/crank poses from measured pin axes; geometry checks are separate."""
from pathlib import Path
import copy,math,json
import numpy as np
import yaml
HERE=Path(__file__).resolve().parent

def transforms(angle_deg):
    # Hand-local mm, measured original STEP solid44 and crank. 21 mm link centres.
    cx,cy=173.539515397-119.541,-49.500004703+49.005
    c=np.array([cx,cy,0.])
    a0=np.array([170.333408616+.999-119.541,-69.149684245+49.005,0.])
    b0=np.array([180.443293149+.999-119.541,-50.743428930+49.005,0.])
    t=math.radians(angle_deg)
    R=np.array([[math.cos(t),-math.sin(t),0],[math.sin(t),math.cos(t),0],[0,0,1.]])
    b=c+R@(b0-c)
    length=float(np.linalg.norm(b0-a0))
    a=np.array([a0[0],b[1]-math.sqrt(length**2-(b[0]-a0[0])**2),0.])
    dy=a[1]-a0[1]
    u0=b0-a0;u=b-a
    phi=math.atan2(u[1],u[0])-math.atan2(u0[1],u0[0])
    Q=np.array([[math.cos(phi),-math.sin(phi),0],[math.sin(phi),math.cos(phi),0],[0,0,1.]])
    out={}
    out['rotor']=(R,c-R@c)
    out['left']=(np.eye(3),np.array([0,dy,0]))
    out['right']=(np.eye(3),np.array([0,-dy,0]))
    out['link-left']=(Q,a-Q@a0)
    ar0=2*c-a0;ar=2*c-a
    out['link-right']=(Q,ar-Q@ar0)
    out['opening']=9.821835224-2*dy
    return out

def transform_for(name,xf):
    if name in ['gripper-servo-crank','gripper-oem-horn','gripper-crank-keeper','gripper-oem-retaining-screw']:
        return xf['rotor']
    if name=='gripper-link-left':return xf['link-left']
    if name=='gripper-link-right':return xf['link-right']
    if any(s in name for s in ['gripper-finger','gripper-pad','gripper-wire-retainer','gripper-retainer']):
        return xf['left' if 'left' in name else 'right']
    return np.eye(3),np.zeros(3)

def apply_meshes(meshes,angle_deg):
    xf=transforms(angle_deg);out=[]
    for m in meshes:
        R,t=transform_for(m['name'],xf)
        out.append(dict(m,v=m['v']@R.T+t/1000))
    return out

def pose_manifest(doc,angle):
    result=copy.deepcopy(doc);xf=transforms(angle)
    for r in result['parts']:
        R,t=transform_for(r['id'],xf)
        r['position']=t.tolist();r['rotation']=[0,0,math.degrees(math.atan2(R[1,0],R[0,0]))]
    result['gripper_pose']={'crank_angle_deg':angle,'pad_opening_mm':round(xf['opening'],4),
        'basis':'Measured 21 mm link centres; requires servo endpoint calibration and actual wire length confirmation'}
    return result

def write_poses():
    doc=yaml.safe_load((HERE/'gripper_assembly.yaml').read_text())
    out=[]
    for name,angle in [('open',-60),('mid',-30),('near-closed',30)]:
        p=HERE/'gripper/poses'/name;p.mkdir(parents=True,exist_ok=True)
        d=pose_manifest(doc,angle);(p/'assembly.yaml').write_text(yaml.safe_dump(d,sort_keys=False))
        out.append(d['gripper_pose'])
    (HERE/'gripper/motion.json').write_text(json.dumps(out,indent=2))
    print(json.dumps(out))

if __name__=='__main__':write_poses()
