# v1 build notes: print, assemble, wire, configure

## 0. Saturday plan (2 days)
Printing is the long pole: ~830 g, roughly 35-45 h on one printer at standard 0.2 mm settings (estimate, not sliced).
Split it over three printers at the Invention Studio:
| Printer | Parts, in order | est. |
|---|---|---|
| A (your X1E) | coupon-fits + coupon-yaw (first, ~1 h), then upper-arm, turret-hub | ~14 h |
| B | base-shell, base-deck (0.24-0.28 mm layers, 3 walls, 15 % infill are fine for these two) | ~12 h |
| C | forearm, shoulder-tower, pack-cover, pack-carriage, shoulder-pulley-80t, forearm-cover, gripper-base, both fingers, small rings | ~14 h |
Material for the deadline: everything in PLA is acceptable if you set the A4988s to **0.6 A** (Vref 0.48 V with R100)
and check after 10 minutes of holding that no motor case is too hot to keep a finger on (~45 °C). Reprint
base-deck, upper-arm, pack-cover, pack-carriage and forearm in PETG later if they soften.
Order the Amazon list (parts/components.yaml) today and pick listings that say "arrives Friday/Saturday"; fallbacks
the same day: 608 bearings at a skate shop, 6806 at a bike shop, fuse holder at an auto-parts store.
Before you print: measure one motor's body length (CAD assumes 40 mm) and shaft length from the face (24 mm).
If either differs, tell Mechy first: the pack depth, J1 pulley seat and wrist coupling depend on them.

## 1. Print order
1. **Fit coupons first**: `design/v1/printed/coupon-fits.stl` and `coupon-yaw.stl` (rows 1-2 of print_list.csv),
   in the material of the real parts (PLA for Saturday; print them again in PETG before the PETG reprints of
   base-deck, upper-arm, pack-carriage and forearm, whose bearing pockets depend on the material). Four columns each = design value −0.1 / 0 / +0.1 / +0.2 (notches on the
   front edge count the column). Report which column fits:
   608 / 625 / 6806 pockets press in firmly by hand or with a vise; the 8 mm rod pushes through snugly; an M3
   insert melts in square; the spigot peg slides into a 6806 inner ring without play; a GT2 belt seats on the
   40T stub. Every part follows those sizes through `design/v1/printed/layout.py`.
2. Then the parts in `design/v1/print_list.csv` (about 830 g, est). Each STL is already in its print orientation,
   no supports. 0.2 mm layers, 4 walls, 20-25 % gyroid; pulleys and gears at 0.12-0.16 mm for cleaner teeth.
   Brim on base-shell, base-deck and upper-arm.
3. Material: PLA, except **base-deck, upper-arm, pack-cover, pack-carriage, forearm in PETG** (at a motor body).

| Part | Qty | Inserts (M3 x 5.7) |
|---|---|---|
| base-shell | 1 | 10 (6 deck, 4 Uno) |
| base-deck (PETG) | 1 | 3 (bearing cap) |
| bearing-cap, yaw-spacer-outer, yaw-spacer-inner, turret-clamp | 1 each | |
| turret-hub | 1 | 7 (3 spigot end, 4 tower foot) |
| shoulder-tower | 1 | 1 (shaft lock, top) |
| shoulder-pulley-80t | 1 | 4 (spacer face) |
| bearing-shim | 3 | |
| upper-arm (PETG) | 1 | 5 (pack cover) |
| pack-cover (PETG), pack-carriage (PETG) | 1 each | |
| forearm (PETG) | 1 | 4 (cover) |
| forearm-cover | 1 | |
| gripper-base, gripper-finger-left, gripper-finger-right | 1 each | 1 (idler axle) |
Total 35 inserts (buy 50).

## 2. Screws (all M3 socket head cap screws, one 2.5 mm key; M2 only on the servo)
| Joint | Screw | Qty | Engagement |
|---|---|---|---|
| Deck → shell bosses | M3 × 10 | 6 | 5 in the insert |
| Uno → standoffs | M3 × 8 | 4 | 6.4 |
| J1 motor → deck (5 mm) | M3 × 10 + 1 or 2 M3 washers (0.5 each) | 4 | 4.5 (1 washer) / 4.0 (2) in the motor thread |
| J2, J3, J4 motors → 4 mm plates | M3 × 8 | 12 | 4.0 in the motor thread |

**Measure the motor threads first:** screw an M3 into one motor hole by hand until it stops and measure how far it
went. The design assumes 4.5 mm. Motor end caps are aluminium, where 4.5 mm (1.5 d) is the target engagement.
- 6 mm or more: use M3 × 10 for J2-J4 (6.0 engaged) and 1 washer on J1.
- 5 to 6 mm: keep M3 × 8 for J2-J4 and 1 washer on J1.
- under 5 mm: keep M3 × 8 and use 2 washers on J1 so the screw cannot bottom. Add a drop of medium threadlocker
  (metal-to-metal joint, safe here) since engagement is then 4.0 mm.
| Bearing cap, turret clamp | M3 × 8 | 6 | 5 / 4.5 |
| Tower foot → turret | M3 × 12 | 4 | 6 |
| Tower shaft lock | M3 × 30 + M3 jam nut | 1 | runs onto the rod, ~4 mm shows; lock with the nut |
| Fixed 80T → tower | M3 × 12 (counterbored 5.5 from the outer face) | 4 | 5.5 |
| Carriage clamp | M3 × 12 + M3 nut held in the 5.8 slot on the wall's outer face | 2 | full nut + 0.6 |
| Pack cover | M3 × 10 | 5 | 6 |
| Forearm cover | M3 × 8 | 4 | 5 |
| Gripper base → flange coupling | M3 × 8 from behind the flange into nuts in the plate's front pockets | 4 | full nut + 1 |
| Idler finger axle | M3 × 6 + M3 × 12 mm OD fender washer | 1 | 5.2 |
| Servo tabs | M2 × 8 + M2 nut | 2 | |
| Base → table | M5 wood screws (or 2 C-clamps on the base rim) | 4 | |

## 3. Assembly order
1. **Base sub-assembly** (the turret clamp is only reachable from inside the base): press the upper 6806 into the
   deck tube from below until it stops on the lip, drop in yaw-spacer-outer, press the lower 6806, screw the bearing
   cap. J1 motor under the deck, turned 45° so its screws sit on the belt centreline and beside the pulley (plug
   toward the front-right), 20T pulley **hub up**, teeth level with the turret's 120T band (66.7 mm above the table).
   Loop the GT2-300 belt, slide the turret spigot through the bearings with yaw-spacer-inner between the inner
   rings, screw turret-clamp from below. Turn the turret so its tower arm points away from the motor, slide the J1
   motor outward to tension and tighten its 4 screws from above (checked as pose `service-tower`).
2. Base shell: inserts in, screw the shell to the table through the 4 floor holes (M5) **now**. Uno + shield on the
   standoffs (USB-B in the rear window). Panel jack (11.3 mm hole), 22 mm mushroom E-stop (22.3 mm hole) and the
   7.5 A inline fuse in the +24 V lead. Then lower the deck sub-assembly on and fit the 6 deck screws.
3. Tower: bolt the fixed 80T to the tower (4 × M3 × 12 from the outer face), then the tower to the turret
   (4 × M3 × 12, reached from above, **before the arm goes on**; checked as pose `service-tower`).
4. **Upper arm on the bench** (pose `service-j2`), pack cover off: press both shoulder 608s. Fit the carriage
   (2 × 625 + 5 × 52 rod) loosely with its two M3 × 12 from inside the pack into nuts in the wall's outer slots,
   centred in its slots. J2 motor on the −Y wall (plug down through the bottom notch). Outboard of the wall: J2 20T
   and 60T (hubs toward the wall, 1 mm off it), stage-2 20T 1 mm beyond the 60T. Fit the first GT2-200 (J2 → 60T),
   slide the J2 motor down-forward along its slots to tension it, and tighten the 4 J2 screws from the −Y side.
   (On the tower these screws are behind the tower wall, so stage 1 is set here.)
5. On the tower: loop the second GT2-200 around the fixed 80T and the stage-2 20T as the arm slides onto the shoulder
   rod: shim + collar on the tower side, shim + collar on the cover side. Lock the rod with the M3 × 30 and jam nut.
   **Tension stage 2 with the carriage**: from inside the pack, slide it rear-down along its slots and clamp it. Its
   slots run at right angles to the stage-1 belt, so this does not change the stage-1 tension.
6. Elbow motor on the pack cover (plug up through the top notch), 20T on its shaft (hub toward the cover), close the
   cover with 5 screws.
7. Forearm: press both elbow 608s, drop the J4 motor into the channel from the open top (plug up), face screws from
   the front. Elbow rod (8 × 113) through the upper-arm boss and the forearm hub: collar on the −Y end, shim + collar
   on the forearm side. Loop the GT2-520 belt, tension by sliding the elbow motor along its cover slots.
8. Gripper: on the bench, bolt the 5 mm flange coupling to gripper-base (4 × M3 × 8 put in from behind the flange,
   into nuts pressed into the plate's front pockets). Measure the coupling first: the holes must be on a 16 mm
   circle and the hub ≤ 10.5 mm across, or the round screw heads will not clear the hub. Then slide the coupling hub
   onto the J4 shaft until the flange face is 1 mm proud of the shaft tip and tighten its set screws on the flat. Servo through the deck cut-out,
   cable toward the forearm, M2 screws + nuts. Centre the servo (90°) with the fingers closed, then fix the left
   finger to the single-arm horn; the idler finger goes on its axle under the fender washer.
9. Cables: motor cables leave the pack through its notches and run down the outside of the tower, through the
   turret's Ø12 centre bore into the base (pass bare wires, crimp the shield end afterwards). J4 and servo cables run
   along the forearm, over the elbow (loop for ±135°) and down the upper arm with the pack cables (spiral wrap).
   Leave loops for ±150° of yaw and ±180° of roll.

### Re-tensioning (PLA creeps: check the belts after the first week)
- J1 and J3: slide the motor in its slots and re-tighten (both reachable assembled; J1 with the turret arm turned away).
- J2 stage 2: take off the pack cover (5 screws; lift the elbow motor and its belt off with it), loosen the two
  carriage screws, slide the carriage rear-down, clamp, refit the cover and re-tension J3.
- J2 stage 1: needs the upper arm off the tower (collars off, slide the arm off the rod), then as in step 4.

## 4. Electrical settings
See `control/joint_limits.yaml` for pins, steps per degree, limits and kinematics.
- A4988 current: **0.6 A** while the motor-mount parts are PLA (0.7 A once they are PETG). Vref = 8 × I × R_sense:
  **0.48 V** with R100 (0.1 Ω) sense resistors (read the resistor code first: R050 → 0.24 V, R200 → 0.96 V).
  Check the motor cases after 10 minutes of holding.
- 1/16 microstepping (all MS jumpers fitted). Stock GRBL on the Uno drives 3 axes: use AccelStepper on the shield
  pins, or a 4-axis fork.
- E-stop: NC contacts in series with +24 V to the shield (cuts motor power; the Uno stays on USB).
- Servo: 6 V from the LM2596 (set it with a meter **before** connecting the servo), never the Uno 5 V pin; signal on A3;
  common ground.
- End-stops: headers X−/Y−/Z− for J1-J3. **Mounts are not in v1**: home by eye or add switch brackets later.
