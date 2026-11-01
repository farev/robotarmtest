#!/usr/bin/env python3
"""T107 static screening, SI units. Python stdlib only; no CAD/simulation.
Run: python3 research/payload-600g/check.py
Writes only envelope.csv and envelope.svg beside this script; prints audit tables.
Frozen input transcription and all estimates are documented in note.md.
The Mechy tool catalog has no custom mass/COM free-body sensitivity interface.
"""
from pathlib import Path
import csv, math, random
G = 9.80665
L, D, H, R = .135, .220, .187, .115  # configured geometry; R assumed contact radius
PAYLOAD = .600
# name, kg, local axial x, local vertical z, lateral y, attachment frame
# Frames: S = fixed in yaw frame, U = upper arm, F = forearm from elbow.
# Print masses: design/v1/print_list.csv estimates. All COMs estimates unless stated.
# Hardware allowances explicitly include bearings, shafts, collars, pulleys, belts,
# screws/nuts/inserts, wiring and pads. They are NOT measured BOM masses.
def bodies(case='central'):
    scale, mm, ux, fx, wx = {'light':(.8,.22,0.,.055,.090),
        'central':(1.,.28,.035,.075,.100),
        'heavy':(1.2,.35,.0675,.095,.110)}[case]
    out=[]
    def add(n,m,x,z=0,y=0,f='U',uncertain=True):
        out.append((n,m*scale if uncertain else m,x,z,y,f))
    # All stationary prints except coupons. No motor payload cost assigned to J1.
    add('stationary prints incl tower and fixed shoulder pulley',.5380,0,y=-.025,f='S')
    add('J1 motor',mm,0,y=.0730665,f='S',uncertain=False)
    add('stationary electronics, bearings, fasteners, shoulder shaft',.280,0,y=-.010,f='S')
    add('upper-arm print',.171,ux,y=-.0567)
    add('pack cover and carriage prints',.0348,-.046,y=-.0567)
    # Inverse of home q2=45deg mounting positions (assembly.yaml).
    add('J2 moving motor',mm,-.01673,-.05076,-.0572,uncertain=False)
    add('J3 moving motor',mm,-.04870,.03653,-.0562,uncertain=False)
    add('intermediate rod,625 bearings,60T/20T pulleys',.065,-.046,y=-.075)
    add('three moving belts,other pulleys,fasteners,wiring',.065,.020,y=-.05)
    add('elbow rod,collars,608 bearings',.090,L,y=-.030)
    add('forearm and cover prints',.095,fx,y=0,f='F')
    add('J4 motor',mm,wx,f='F',uncertain=False)
    add('flange coupling,forearm screws,inserts,wiring',.025,.130,f='F')
    add('gripper base and fingers prints',.0174,.180,z=-.014,f='F')
    add('MG90S servo',.0134,.165,z=-.010,y=.015,f='F',uncertain=False)
    add('gripper screws,nuts,horn,pads,wire',.012,.185,z=-.014,f='F')
    return out

def rot(x,z,a): return x*math.cos(a)-z*math.sin(a), x*math.sin(a)+z*math.cos(a)

def positions(q2,q3,delta=0,case='central',payload=PAYLOAD):
    ex,ez=rot(L,0,q2)
    result=[]
    for name,m,x,z,y,f in bodies(case)+[('payload',payload,D+delta,0,0,'F')]:
        if f=='U': x,z=rot(x,z,q2)
        if f=='F':
            x,z=rot(x,z,q2+q3); x+=ex; z+=ez
        result.append((name,m,x,y,z+(0 if f=='S' else H),f))
    return result

def loads(q2,q3,delta=0,case='central',payload=PAYLOAD):
    p=positions(q2,q3,delta,case,payload)
    ex=L*math.cos(q2)
    t2=G*sum(m*x for _,m,x,y,z,f in p if f!='S')
    t3=G*sum(m*(x-ex) for _,m,x,y,z,f in p if f=='F')
    mass=sum(b[1] for b in p)
    sx=sum(m*x for _,m,x,y,z,f in p); sy=sum(m*y for _,m,x,y,z,f in p)
    # Circular contact support: worst-edge overturning, invariant under yaw of whole arm.
    # J1's offset is fixed to the base, so sweep yaw to rotate all other bodies relative to it.
    j1=next(b for b in p if b[0]=='J1 motor'); sy_fixed=j1[1]*j1[3]
    # Other S offsets are treated as yaw-following estimates; worst-yaw extension covers uncertainty.
    radius_moment=math.hypot(sx,sy-sy_fixed)+abs(sy_fixed)
    edge=G*(radius_moment-mass*R) # positive means tips under assumed support
    return t2,t3,edge,mass,radius_moment/mass

def capacity(t=.34,current=.6,eta=.90,basis=1.):
    # linear current scaling is an unverified extrapolation, NOT exact motor evidence
    tm=t*current/.9*basis
    return tm*12*eta**2*.50,tm*6*eta*.50,tm*.50

def potential(q2,q3,delta=0,case='central'):
    return G*sum(m*z for _,m,x,y,z,f in positions(q2,q3,delta,case))

def verification():
    rows=[]
    def check(name,expected,got,tol=1e-7):
        ok=abs(got-expected)<=tol
        rows.append((name,expected,got,'PASS' if ok else 'FAIL')); assert ok,name
    check('payload-only shoulder horizontal',2.08881645,PAYLOAD*G*(L+D))
    check('payload-only elbow horizontal',1.2944778,PAYLOAD*G*D)
    # Independent lumped horizontal FBD, with terms explicitly transcribed from inventory.
    upper=.171*.035+.0348*(-.046)+.28*(-.01673-.04870)+.065*(-.046)+.065*.020+.090*L
    fore=.095*.075+.28*.100+.025*.130+.0174*.180+.0134*.165+.012*.185
    fm=.095+.28+.025+.0174+.0134+.012
    check('whole-arm shoulder horizontal FBD',G*(upper+fore+fm*L+.6*(L+D)),loads(0,0)[0])
    check('whole-arm elbow horizontal FBD',G*(fore+.6*D),loads(0,0)[1])
    rng=random.Random(107); err=0
    for _ in range(500):
        a,b=math.radians(rng.uniform(-30,90)),math.radians(rng.uniform(-135,120))
        d=rng.choice([0,.025,.05]); c=rng.choice(['light','central','heavy']); h=1e-6
        t=loads(a,b,d,c)
        for j in (0,1):
            e=((potential(a+h,b,d,c)-potential(a-h,b,d,c))/(2*h) if j==0 else
               (potential(a,b+h,d,c)-potential(a,b-h,d,c))/(2*h))
            err=max(err,abs(t[j]-e))
    check('500 random poses: max torque vs dU/dq error',0,err,1e-7)
    check('payload offset +0.050 m torque increment',.2941995,loads(0,0,.05)[1]-loads(0,0)[1])
    check('wrist offset 0.025 m payload only',.14709975,.6*G*.025)
    # Independent overturning edge check with all estimated lateral offsets set to zero.
    p=positions(0,0); edge_sum=G*sum(m*(x-R) for _,m,x,y,z,f in p)
    check('base forward-edge FBD',G*(sum(m*x for _,m,x,y,z,f in p)-R*sum(v[1] for v in p)),edge_sum)
    # Gripper virtual work: input torque pays for BOTH jaw contacts.
    ts=1.8*.0980665; eta=.8; lever=.05; N=ts*.5*eta/(2*lever)
    check('gripper two-jaw virtual work',ts*.5*eta,2*N*lever)
    check('A4988 Vref R100 at 0.6 A',.480,8*.6*.1)
    return rows

def main():
    out=Path(__file__).resolve().parent
    checks=verification()
    print('Check | Expected | Got | PASS/FAIL')
    for row in checks: print(' | '.join(str(x) for x in row))
    c2,c3,c4=capacity(); rows=[]
    for case in ['light','central','heavy']:
      for delta in [0,.025,.050]:
       for a in range(-30,91,5):
        for b in range(-135,121,5):
         q2,q3=map(math.radians,(a,b)); height=H+L*math.sin(q2)+D*math.sin(q2+q3)
         if height<.035: continue # existing pad-only table constraint, not collision certification
         t2,t3,edge,mass,cg=loads(q2,q3,delta,case)
         rows.append(dict(evidence='computed_from_estimates',case=case,payload_kg=PAYLOAD,offset_m=delta,
          q2_rad=q2,q3_rad=q3,pad_x_m=L*math.cos(q2)+D*math.cos(q2+q3),pad_z_m=height,
          shoulder_Nm=t2,elbow_Nm=t3,cap_shoulder_est_Nm=c2,cap_elbow_est_Nm=c3,
          utilization_est=max(abs(t2)/c2,abs(t3)/c3),base_worst_yaw_edge_Nm=edge,
          total_mass_est_kg=mass,base_worst_yaw_COM_radius_m=cg))
    with (out/'envelope.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
    print('Rows',len(rows),'central cases at offset 0',sum(r['case']=='central' and r['offset_m']==0 for r in rows))
    print('Capacities J2/J3/J4:',capacity(),'optimistic .4Nm eta=1:',capacity(.4,.6,1))
    print('Horizontal: case offset J2 J3 edge mass radial-COM ballast-at-centre')
    for c in ['light','central','heavy']:
      for d in [0,.025,.05]:
        v=loads(0,0,d,c); print(c,d,*[round(x,6) for x in v],round(max(0,v[2]/(G*R)),6))
    for d in [0,.025,.05]:
        subset=[r for r in rows if r['case']=='central' and r['offset_m']==d]
        print('Central maxima',d,max(abs(r['shoulder_Nm']) for r in subset),max(abs(r['elbow_Nm']) for r in subset))
    own=loads(0,0,payload=0)
    print('Central horizontal payload limits J2/J3 kg',(c2-own[0])/(G*(L+D)),(c3-own[1])/(G*D))
    print('Base central horizontal contact radius sensitivity (R, edge N m):', [(r, loads(0,0)[2]+loads(0,0)[3]*G*(R-r)) for r in [.090,.100,.115]])
    print('Required ratios central horizontal at eta .81/.90',2*loads(0,0)[0]/(.34*.6/.9*.81),2*loads(0,0)[1]/(.34*.6/.9*.90))
    print('J4 moving motor payload-equivalent cost kg J2/J3',.28*(L+.1)/(L+D),.28*.1/D)
    print('Wrist rotating tool estimate kg',.0174+.0134+.012,'offset limit m',(c4-(.0174+.0134+.012)*G*.02)/(.6*G))
    print('Jaw lever, total N at half 4.8V stall & eta .8, required mu, ideal stall mu')
    for l in [.03,.05,.07]:
        n=1.8*.0980665*.5*.8/l
        print(l,n,.6*G/n,.6*G*l/(1.8*.0980665))
    # SVG: three full joint-grid heatmaps, use mask and explicit conditional labels.
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1240" height="740" viewBox="0 0 1240 740">',
         '<rect width="1240" height="740" fill="#f5f7fa"/>',
         '<style>text{font-family:Arial,sans-serif;fill:#172b44}.small{font-size:13px}.label{font-size:16px}</style>',
         '<text x="40" y="40" font-size="27" font-weight="bold">600 g static envelope — conditional screening</text>',
         '<text x="40" y="68" class="label">Estimated central masses; 0.6 A extrapolation; capacity J2 = %.3f / J3 = %.3f N·m</text>'%(c2,c3),
         '<text x="40" y="92" class="small">Colour = max(|shoulder torque| / capacity, |elbow torque| / capacity). No dynamic, grip or collision approval.</text>']
    colors=['#d8e9ec','#86b6c0','#ffda85','#ee986d','#cf5558','#94384d']
    for k,d in enumerate([0,.025,.05]):
        ox=65+k*400; oy=145; w=330; h=390
        svg.append(f'<text x="{ox}" y="125" class="label" font-weight="bold">Payload COM beyond pads: {d:.3f} m</text>')
        svg.append(f'<rect x="{ox}" y="{oy}" width="{w}" height="{h}" fill="#d7dbe1"/>')
        for r in rows:
            if r['case']!='central' or r['offset_m']!=d:continue
            a=round(math.degrees(r['q2_rad']));b=round(math.degrees(r['q3_rad']))
            x=ox+(a+30)/125*w;y=oy+(120-b)/260*h
            color=colors[min(5,int(r['utilization_est']))]
            svg.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w/25+.1:.2f}" height="{h/52+.1:.2f}" fill="{color}"><title>J2 {a}°, J3 {b}°; demand {r["shoulder_Nm"]:.3f}, {r["elbow_Nm"]:.3f} N m; utilization {r["utilization_est"]:.2f}</title></rect>')
        x=ox+30/125*w+w/50;y=oy+120/260*h+h/104
        svg.append(f'<circle cx="{x}" cy="{y}" r="5" fill="white" stroke="#172b44" stroke-width="2"/>')
        svg.append(f'<text x="{ox}" y="560" class="small">Shoulder angle: −30° … 90° (left to right)</text>')
        svg.append(f'<text x="{ox}" y="580" class="small">Elbow angle: 120° … −135° (top to bottom)</text>')
    for i,c in enumerate(colors):
        svg.append(f'<rect x="{65+i*175}" y="610" width="25" height="20" fill="{c}"/>')
        svg.append(f'<text x="{96+i*175}" y="626" class="small">{i}–{i+1} × capacity</text>')
    svg += ['<text x="65" y="660" class="label">White dot: horizontal extension (pad reach 0.355 m). Grey: rejected by existing pad-height limit.</text>',
            '<text x="65" y="688" class="small">Below 1× means static torque screen only. Actual motor torque, mass/COM, friction and base mounting remain unverified.</text>',
            '<text x="65" y="712" class="small">Rebuild: python3 research/payload-600g/check.py  |  Full mass/offset sweep: envelope.csv  |  Sources: note.md</text>','</svg>']
    (out/'envelope.svg').write_text('\n'.join(svg))
if __name__=='__main__': main()
