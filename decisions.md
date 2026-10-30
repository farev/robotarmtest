# Decisions

## 2026-10-29 (evening): Invention Studio Store catalog (user capture, research/gt-invention-studio-store.md)
- From the store: MG90S servo (Miuzei, $3.50) and the J1 300 mm closed belt ($2). Everything else stays on Amazon.
- Not redesigned around the store's 6 mm-bore 20T/80T kit and 606 bearings: they fit only the J2 intermediate
  shaft (motor shafts are 5 mm), the store's 6 mm shaft is out of stock, and the Amazon order is needed anyway for
  the 608/6806 bearings, 5 mm-bore pulleys, rods, collars, belts 200/520 and electronics. Saving ~$20 of
  pulleys/bearings is not worth a J2 re-layout, new pose checks and a new review two days before the deadline.

## 2026-10-29 (later): Saturday deadline
- Parts from Amazon (fast delivery) or the GT Invention Studio store; screws, nuts, washers and heat-set inserts
  from the Invention Studio. The store catalog could not be read (JavaScript page), so the list is Amazon.
- Wrist coupling: generic Amazon 5 mm rigid flange coupling instead of the Pololu hub (gripper deck 3.5 mm lower so
  the M3 heads at r 8 clear it).
- PLA everywhere is accepted for the deadline at 0.6 A driver current; PETG reprints of the motor parts later.

## 2026-10-29: v1 architecture
- **Wrist = roll** ("one motor to rotate the hand"), not pitch. The gripper always points along the forearm;
  approach angle = J2 + J3. Assumed; changing to wrist pitch means a new forearm/wrist module.
- **Belts, not printed gearboxes**: printed PLA planetaries backlash 0.5-2° per stage (≈ 10 mm at full reach);
  GT2 belts with metal motor pulleys keep torque off printed bores on the stepper shaft (rules §1).
- **J2 12:1 in two belt stages, motor climbs a fixed pulley**: J2 and the elbow motor ride on the upper arm behind
  the shoulder as counterweights. Single-stage options (≤ 7.5:1) left < 1.5 safety on 0.34 N·m motors.
  Result: J2 motor at 29 % of holding torque, J3 at 30 % (CAD masses, 100 g payload).
- **Elbow motor in the pack, belt along the upper arm** instead of a motor at the elbow: saves ~0.45 N·m at the
  shoulder. Joints stay relative (no J2/J3 coupling in firmware).
- **J4 direct drive** (first the Pololu 1998 hub, since the Saturday change a generic 5 mm flange coupling): roll
  torque is tiny; the motor's own bearings carry the ~0.17 kg gripper + payload at 40 mm.
- **Gripper gears m2 z15** (shortened addendum 0.85) instead of m1.5 z20: same 30 mm centres, 1.5 mm tip land prints.
- **E-stop 22 mm mushroom** (22.3 hole) instead of a 16 mm latching button: no 16 mm button found rated for 6 A DC.
- **Design review 2026-10-29 fixes**: tower foot screws moved off the wall/gussets (foot extended both sides); shaft lock
  M3 x 30 + jam nut; J2 motor straight below the intermediate shaft (J2_ANGLE 270) so its screws clear the 60T; carriage
  clamps from inside the pack into captive nuts; then (after the service-pose check showed the key grazing the
  stage-1 belt) stage 1 moved to a 200 mm loop with the J2 motor at 300°: one belt size for both stages, shoulder
  axis down to 187 mm; 2 mm spacer under the fixed 80T; forearm cover inserts with 2 mm walls;
  panel holes as teardrops; no web/floor holes beside belts (finger traps); all M3 SHCS (one key).
- **Tool plane on the yaw axis** (upper arm offset to −Y): planar IK without a lateral offset.
- **Electronics inside the base** (Ø230, fits the X1E bed): USB-B, 24 V jack and motor-power switch on the rear.
- **PETG for the 4 motor-clamping parts**, PLA elsewhere (PLA softens at 55-60 °C).
- **Elbow belt 520 mm** (Amazon 2-pack listing; stock unverified). Fallback: 500 mm loop with L2 = 125 mm.
- Shoulder height (now 187 mm) is set by the motor pack's swing at J2 = 90°.
- Review 2 fixes: carriage nut slots 5.8 wide (nut can't turn) and the screw 0.6 past the nut; J1 motor turned 45°
  so its screws are reachable with the belt on; tower window closed (finger trap); key keep-outs at Ø6.5;
  gripper flange screws from behind into captive nuts; soft-limit pose J2 -30 / J3 -45 checked.
