"""Summarize saved bam-v2 check results; no CAD or shared project changes."""
from pathlib import Path
import os,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PY=Path('/Users/Carlo/Empire/mechy/engine/.venv/bin/python')
if Path(sys.prefix)!=PY.parent.parent:
    os.execv(str(PY),[str(PY),str(Path(__file__).resolve())])
import csv,json,yaml
def read(name):return json.loads((HERE/name).read_text())
reg=read('checks/regression.json');asm=read('checks/assembly.json')
prints=read('checks/print_checks.json');motion=read('checks/motion_screen.json')
motor=read('checks/motor_check.json');mass=read('mass_props.json');loads=read('loads.json')
hws=read('checks/upper_hardware_screen.json')
rows=list(csv.DictReader((HERE/'print_list.csv').open()))
parts=HERE/'parts';parts.mkdir(exist_ok=True)
components=[
 {'name':'42SHDC3026-15B NEMA 17 stepper','status':'owned','qty':1,'function':'Yaw drive',
  'model':'../../parts/models/nema17-42shdc.step','datasheet':'unverified',
  'compat':'unverified','compat_note':'Exact shaft length, pilot, thread depth and torque curve not measured.'},
 {'name':'5 mm flange coupling','status':'candidate','qty':1,'function':'Direct yaw torque coupling',
  'url':'https://vxb.com/products/4-pack-5mm-rigid-flange-shaft-couplings-with-8-scr',
  'datasheet':'https://vxb.com/products/4-pack-5mm-rigid-flange-shaft-couplings-with-8-scr',
  'stock_checked':'unverified','compat':'unverified','compat_note':'16 mm PCD and 2 mm flange thickness not stated on exact listing.',
  'note':'Page opened 2026-10-30: 4-pack $39.99, US shipping advertised; explicit available quantity not verified. No purchase selected.'},
 {'name':'51105 thrust bearing','status':'candidate','qty':1,'function':'Yaw axial support',
  'stock_checked':'unverified','datasheet':'unverified','compat':'unverified',
  'specs':['25 x 42 x 11 mm handbook-typical envelope','axial load only'],
  'note':'Retained from original bam-v2 BOM; ownership and exact bearing supplier not verified.'},
 {'name':'Direct-drive base fasteners','status':'candidate','qty':1,'function':'Fasteners',
  'stock_checked':'unverified','datasheet':'unverified','compat':'unverified',
  'specs':['4 M3x10 SHCS','4 M3x10 countersunk','4 M3x12 SHCS','4 M3x8 SHCS','4 M3 heat-set inserts','8 M3 nuts','4 bench anchors, support-dependent'],
  'note':'Variant delta; upper hardware quantities and what the CAD shows are in bom.csv (modeled_in_cad). Nominal ISO screw/nut solids checked, purchased tolerances unverified.'}]
(parts/'components.yaml').write_text(yaml.safe_dump({'scope':'bam-v2 delta only; shared v1 gallery is unchanged',
    'components':components,'orders':[]},sort_keys=False))
checks=[
 {'between':['system'],'interface':'viewer rig and upper geometry','status':'verified',
  'claim':'39 upper mesh instances and 17 upper print STL files unchanged; joint hierarchy/extras unchanged; 103 pose transforms identical.',
  'evidence':'design/bam-v2/checks/regression.json'},
 {'between':['42SHDC3026-15B NEMA 17 stepper','5 mm flange coupling'],'interface':'shaft, bore and engagement','status':'unverified',
  'claim':'Models use 5 mm shaft/bore and 7.5 mm engagement. Motor shaft length 24 mm is an estimate; coupling PCD/thickness remain unverified.',
  'evidence':['parts/models/nema17-42shdc.yaml','parts/models/flange-coupling-5mm.yaml',components[1]['url']]},
 {'between':['42SHDC3026-15B NEMA 17 stepper','Direct-drive base fasteners'],'interface':'mounting pattern and threads','status':'unverified',
  'claim':'31 mm square model pattern; M3x10 engages 4.5 mm nominally. No margin if actual tapped depth is less than 4.5 mm.',
  'evidence':['parts/models/nema17-42shdc.yaml','design/bam-v2/printed/base_geometry.py']},
 {'between':['51105 thrust bearing','system'],'interface':'bearing support, running journal and uplift','status':'unverified',
  'claim':'Nominal 25/42/11 bearing envelope, 24.9 mm printed locating journal in 25.3 mm bore; thrust washer compression support and 0.5 mm uplift gap. Friction, radial-load wear, bearing retention tolerances and printed lip strength not load-tested.',
  'evidence':['design/bam-v2/assembly.yaml','design/bam-v2/checks/assembly.json',
              '/Users/Carlo/Empire/mechy/engine/mechy/data/standard_parts/bearings_thrust.csv']},
 {'between':['system'],'interface':'homing','status':'issue',
  'claim':'Original yaw switch/socket and gear trigger were removed with the belt base. A new switch bracket/cam and home calibration are required before yaw homing.',
  'evidence':['design/bam-v2/build_result.json','design/bam-v2/mass_props.json']},
 {'between':['system'],'interface':'torque, payload and drive calibration','status':'unverified',
  'claim':'Yaw ratio 1 is represented throughout. Motor check uses a generic curve; 600 g payload capacity and usable acceleration not verified. Existing control firmware is not changed.',
  'evidence':['design/bam-v2/checks/motor_check.json','design/bam-v2/loads.json','requirements.yaml']},
 {'between':['system'],'interface':'inherited shoulder/elbow pulley consistency','status':'unverified',
  'claim':'Upper geometry/BOM retain 20T motor pulleys while inherited params specify 16T and 5.625:1. This pre-existing discrepancy was preserved to honor the upper-assembly scope.',
  'evidence':['design/bam-v2/reference/belt-drive/params.yaml','design/bam-v2/bom.csv']},
 {'between':['system'],'interface':'new base clearance','status':'verified',
  'claim':f"No solid interference or unmeasurable contacts in {asm['parts']} base solids (motor plug keep-out included) at yaw 0, -150, 90, 150 deg. The home check flags {len(asm['clearance_issues'])} coupling screw clearances at 0.1 mm; nominal gap for all four is (3.2 - 3.0)/2, at the numerical threshold.",
  'evidence':['design/bam-v2/checks/assembly.json','design/bam-v2/checks/yaw_poses.json']},
 {'between':['system'],'interface':'upper-arm hardware placement','status':'verified' if hws['ok'] else 'issue',
  'claim':f"{hws['added_parts']} added belts, bearings, axles, screws and nuts screened against every arm mesh at 4 poses: {hws['interference_count']} interferences, {hws['review_count']} shallow overlaps <= 0.2 mm (polygon tessellation of round holes). Bearing seats measured from the vendor solids.",
  'evidence':['design/bam-v2/checks/upper_hardware_screen.json','design/bam-v2/upper_hardware.yaml']},
]
(parts/'compatibility.yaml').write_text(yaml.safe_dump({'checked':'2026-10-30','scope':'bam-v2; geometry verification is distinct from purchased-part compatibility','checks':checks},sort_keys=False))
(parts/'build_plan.md').write_text('''# bam-v2 direct-drive delta

Only the yaw transmission and support change. The shared v1 manifests are not edited.

| Function | Status | Target / retained item |
|---|---|---|
| Yaw actuation | owned | One 42SHDC3026-15B, coaxial, 1:1 |
| Shoulder / elbow / passive wrist / gripper | retained | Original bam-v2 upper assembly and hardware |
| Yaw belt and pulleys | removed | One motor pulley, one 200 mm belt, printed rotategear |
| Yaw torque coupling | buy, candidate | Metal 5 mm flange coupling; exact dimensions unresolved |
| Axial support | retained BOM candidate | 51105 thrust bearing; ownership unresolved |
| Radial guidance / uplift restraint | print | PETG spindle/journal and bearing cover; load/wear not certified |
| Motor mounting / base fixing | print + hardware | Enclosed PETG housing; M3 screws and inserts; support-specific M4 anchors |
| Fasteners | buy or existing stock, unverified | Explicit new-base counts in bom.csv |
| Homing | retained switch, bracket unresolved | New yaw bracket/cam and steps calibration required |
| Drivers and cooling | owned / retained | CNC shield, A4988, heatsinks; current/thermal checks unchanged |
| PSU, controller, capacitor | owned / retained | Existing 24 V supply, Uno and bulk capacitor |
| Switch, fuse, emergency stop | retained open audit | Not redesigned by this geometry change |
| Wire, connectors, motor extensions, USB | retained | Yaw motor plug faces a 22 mm cable port in the housing |
| Consumables, tools and spares | retained open audit | No new tools assumed owned; fit coupon added |

This is a design delta, not an orderable full-build cart. No part was promoted to preferred/selected.
''')
old_env=HERE/'models/bearing-51105-envelope.yaml'
if old_env.exists():old_env.unlink()
model_doc={'part':'51105 thrust bearing','model_source':'handbook dimensions, unverified supplier',
 'frame':'axis Z; housing-washer bottom face z=0; washers, cage and 12 balls (generator: design/bam-v2/hardware.py)',
 'source_url':'https://www.skf.com/group/products/rolling-bearings/ball-bearings/thrust-ball-bearings',
 'source_file':'/Users/Carlo/Empire/mechy/engine/mechy/data/standard_parts/bearings_thrust.csv',
 'critical_dims':[{'name':n,'value_mm':v,'model_mm':v,'source':'handbook_typical'} for n,v in [('bore',25),('outer diameter',42),('height',11)]],
 'note':'0.056 kg from same table. Exact supplier variant, race dimensions and load rating not verified.'}
(HERE/'models/bearing-51105.yaml').write_text(yaml.safe_dump(model_doc,sort_keys=False))
print_lines='\n'.join(f"| {n} | {v['min_wall_mm']} | {v['overhang_area_mm2']} | yes |" for n,v in prints.items())
total=sum(float(r['est_grams_total']) for r in rows)
newmass=sum(float(r['est_grams_total']) for r in rows if r['part'].startswith('yaw-') and 'coupon' not in r['part'])
import math
hws_belt=round(2*39+math.pi*(20/math.pi+90/math.pi)+((90/math.pi-20/math.pi)**2)/39,1)
summary=f'''# bam-v2 — direct-drive yaw, enclosed base, full hardware

The yaw motor is coaxial under the turntable, joined by a metal flange coupling. Base `gear_ratio: 1`.
It now sits inside an enclosed drum housing with vent slots, a 40° anchor skirt and a rear cable port;
a closed bearing cover replaces the four-post retainer. The upper arm now shows its belts, every
bearing, pivot axle, screw and nut. **Upper printed geometry and viewer linkage are preserved. v1 is unchanged.**

## Files and rebuild

- [Full articulated arm](arm.glb), [ready-pose mesh](arm.stl), [preview](views/iso.png),
  [base close-up](views/base_iso.png), [base exploded](views/base_exploded.png).
- [Parameters](params.yaml), [BOM with `modeled_in_cad`](bom.csv), [print list](print_list.csv),
  [base solid assembly](assembly.yaml), [upper hardware placements](upper_hardware.yaml).
- [Check results](check_results.json), [hardware screen](checks/upper_hardware_screen.json),
  [motor estimate](checks/motor_check.json), [compatibility](parts/compatibility.yaml).
- Previous open pedestal and four-post retainer: `reference/open-pedestal/`.

Run from the project folder:

```text
python3 design/bam-v2/build_direct_drive.py
python3 design/bam-v2/check_direct_drive.py
python3 design/bam-v2/motion_screen.py
python3 design/bam-v2/hardware_screen.py
python3 design/bam-v2/write_report.py
```

Use this variant generator: the shared generic `mechy cad build` still creates a belt base.
Hardware solids and placements are generated by `hardware.py`; base parts by `printed/base_geometry.py`.

## Base redesign

- **Housing** (`yaw-base-housing`): one PETG part, 96 mm drum on a 116 mm foot, printed deck-down.
  Walls enclose the motor on all sides; 15 vertical 3.2 mm vent slots; a 22 mm cable port on -X.
  The motor is turned 180° so its plug faces the port; its plug keep-out is in the clash check.
  Every feature is a vertical wall, a 40° skirt, a 35° bore transition or a counterbore bridge
  with sacrificial bridge layers, so the part needs **no supports**.
- **Bearing cover** (`yaw-bearing-cover`): closed 77 mm collar over the thrust bearing with a 2.4 mm
  lip over the spindle flange (0.5 mm float). Four M3x25 screws run down through bosses inside the
  collar into heat-set inserts in the deck. Printed lip-down, no supports. Nothing sits outside r38.5:
  at the shoulder 15° / elbow -132…-142° corner the forearm sweeps down to z≈9.6 at r≈41 mm.
- Spindle, adapter, coupling, motor screws and the main-body interface are unchanged.

## Upper-arm hardware added

- Two GT2 6 mm closed belts, 20T motor pulley to printed 90T pulley, 39 mm centres
  (pitch length {hws_belt} mm, so the 200 mm loop fits). Teeth are not modelled.
- Bearings at every seat: F686ZZ at shoulder 5, elbow 3, wrist 2; F624ZZ at the six M4 link pivots.
  Five vendor bearings were mislabeled (shoulder "F624ZZ", wrist "gripper"); their 6 mm bores make
  them F686ZZ, so they were renamed and recoloured. Flanges sit on recess floors measured from the vendor solids.
- Pivot axles: M6x50 shoulder, M6x40 elbow and wrist with nuts; M4x20/16/10 link pins with nuts where
  the parts have nut pockets. M3x6 motor and stabilizer screws, M3x5 endstop-bracket screws
  (M3x6 would hit the motor-screw heads), three M3x12 toolhead screws.
- The vendor counts 12 F686ZZ but the parts have 10 seats; 2 are spare or unaccounted for.

## Verified in this run

- {reg['preserved_upper_meshes']} retained mesh instances keep vertices, triangles and parents
  (5 renamed bearings recoloured); {reg['preserved_upper_stls']} upper STL files are byte-identical.
- Joint nodes and five coupled linkage extras intact; {reg['poses_checked']} poses give zero transform difference.
- All {reg['v1_files_unchanged']} files in `design/v1` match their starting SHA-256 hashes.
- Base STEP check: {asm['parts']} solids, {len(asm['interferences'])} interferences,
  {len(asm['unverified_contacts'])} unmeasurable contacts; same at yaw -150°, 90°, 150°.
  Raw `ok` is **false** only because {len(asm['clearance_issues'])} coupling screws sit at the 0.1 mm
  clearance threshold in their 3.2 mm holes; these are not hidden.
- Hardware screen: {hws['added_parts']} added parts against every arm mesh at 4 poses:
  {hws['interference_count']} interferences, {hws['review_count']} overlaps ≤ 0.2 mm from polygonal holes.
  The belts touch nothing. It is a vertex-containment screen, not a boolean volume check.
- Motion screen: {motion['pose_count']} sampled poses, {len(motion['penetrations'])} arm vertices inside the base.
- Every printed base part sliced successfully. `arm.xml` loads in MuJoCo.

`allow_contact` only exempts threads (motor screws, screws in nuts or inserts) and the heat-set
insert knurls in their holes.

## Print screening — not released

| New part | Minimum measured wall mm | Flagged overhang area mm² | Fits 256 mm bed as modeled |
|---|---:|---:|---|
{print_lines}

All flagged overhang on the housing and cover is counterbore ceilings that print as bridges using
the modelled sacrificial bridge layers. Print in PETG, broad top mating face on the bed. Calibrate
first-layer compensation with the two coupons before printing the stack. No parts have been printed or weighed.

Printed mass: **{total:.1f} g estimate including the coupon**, of which **{newmass:.1f} g** is the new base
(60% of solid PETG volume).

## Assembly sequence

1. Verify the owned motor's shaft, pilot, 31 mm pitch and tapped depth. Feed the motor up into the
   housing, plug toward the cable port, and fix it with four M3x10 screws from the deck top.
2. Press four M3 heat-set inserts into the deck top. Place the thrust bearing and spindle.
3. Bolt the coupling to the adapter (four M3x10 countersunk screws and nuts). Lower it onto the
   spindle and shaft; tighten the set screws through the spindle windows **before fitting the cover**.
4. Fit the bearing cover over the adapter; four M3x25 screws through the lip into the inserts.
5. Bolt the main body through the adapter/spindle with four M3x12 screws into the captive nuts.
6. Anchor the foot with four M4 screws suited to the bench (shown as M4x12).

## Open checks and estimates

- **Motor/coupling fit:** shaft length, tapped depth and the coupling's 16 mm PCD and flange
  thickness are unverified.
- **Yaw homing:** no yaw switch bracket or cam yet. Do not run the old yaw homing routine.
- **Torque/capacity:** 1:1 yaw estimate uses a generic torque curve; 600 g payload not verified.
- **Inherited pulley discrepancy:** CAD and BOM show 20T motor pulleys (90/20 = 4.5:1) while params use
  16T (5.625:1). Resolve before physical motion.
- **Upper hardware mass** (~45 g estimate) is drawn but not added to the upper bodies' mass properties.
- **Deck-edge sweep:** at that same corner the forearm passes ≈0.9 mm above the housing deck edge
  (r48–50 mm, sampled). Add a firmware soft limit there before running joint-limit moves.
- **Release:** journal wear, cover lip strength, insert hole size, anchors and an independent review
  remain release gates. No buyable-cart or print-ready claim.

## Provenance

Dark blue-gray static base, turquoise rotor, chrome bearings, black belts; upper colours unchanged.
Upper geometry: 20sffactory Community Robot Arm, CC BY 4.0, original design Florin Tobler; original
vendored commit 6c2f573. The BAM upper levelling link retains its existing attribution.
'''
(HERE/'summary.md').write_text(summary)
print('Wrote scoped compatibility/build-plan and summary.md')
