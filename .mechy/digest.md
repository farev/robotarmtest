# Project digest
(Rebuilt by Mechy after every task. Open a file only for detail the digest lacks.)

## Brief
# RobotArmTest ## Goal I want to build a robot arm, and I have the following mechatronics components: [10/24/26, 1:03:08 PM] Carlos Balbuena: Electronics & Control Microcontroller: Arduino Uno (programmed via Arduino IDE / PlatformIO) Shield: CNC Shield V3 expansion board Drivers: A4988 stepper motor driver modules (with heatsinks installed) Capacitor: 100 µF, 50 V electrolytic capacitor Power Supply: 24 V, 6 A DC power supply with barrel jack/terminal adapter [10/24/26, 1:03:15 PM] Carlos Balbuena: Motors Type: NEMA 17 bipolar stepper motors Specific Model: 42SHDC3026-15B (rated around 0.9 A per phase, 4-wire connection) I know generally how to wire everything up, and I have a friend working on the code part. I need to focus on designing all the 3D-printable components, basically the entire structure of the arm. And for the design, I wanted to have a base, two elbows, and then a hand. Since I have four motors: * One motor would be for the base, for rotating the entire arm. * We will have one motor at each of the elbows. * One motor to rotate the hand. I will probably get another servo motor for the gripper itself. I have access to a Bambu Lab X1E 3D printer. And I ideally want to print everything in PLA. And also, I want the biggest part that we need 3D printed to fit in the base of the 3D printer, so we should design the arm around those constraints. Can you help me actually create the 3D printable design for this robot arm, including all of the motor encasings, frame, and…

## Requirements (requirements.yaml)
```yaml
---
product: robot arm
axes:
- base yaw
- shoulder
- elbow
- wrist roll
gripper: MG90S two-finger claw (selected; capacity and clone fit unverified)
payload_g: 600
printer:
  name: Bambu Lab X1E
  bed_mm:
  - 256
  - 256
  - 256
  nozzle_mm: 0.4
material: PLA preferred; preserve documented PETG motor-clamp exceptions; thermal
  performance not certified
max_part: fits the printer bed in one piece
owned:
- 4 x 42SHDC3026-15B NEMA 17 (0.9 A)
- Arduino Uno
- CNC Shield V3
- A4988 drivers
- 100 uF 50 V cap
- 24 V 6 A PSU
country: US
payload_kg: 0.6
remaining_parts_budget:
  currency: USD
  upper_bound_exclusive: 100
  source: task card T106 answered constraints
  compliance_verified: false
builder: professional engineer
finish: black
firmware_owner: friend
material_exceptions:
  source: design/v1/print_list.csv and design/v1/assembly.yaml
  manifest_petg_parts:
  - base-deck
  - upper-arm
  - pack-cover
  - pack-carriage
  - forearm
  conflict: Notes say 4 motor-clamping parts; manifests specify 5. Deadline PLA override
    at 0.6 A is historical, not thermal validation.
approval:
  v1: viewing only; not approved for 600 g
  new_cad_gate: capacity screening and user concept selection
  open:
  - concept
  - motor fit
  - remaining budget trade-offs
answered_constraints_source: task card T106-docs-config-inventory; supplied project
  digest
```

## Assumptions (defaults chosen without asking)
- Treat built as the recorded v1 manifest combination, not proof of fabrication or approval. Preserve assembly/print-list materials and flag conflicting notes; selection is viewing-only.
- Use conditional static screening: estimated mass/COM ranges, payload COM 0/0.025/0.050 m beyond pads, and 0.50 torque factor. No friction coefficient or dynamic capacity is assumed; retain four owned…
- Use task defaults: built-in LED, 1 s on/1 s off and 115200 baud. Limit connected hardware to the Uno/CNC Shield/A4988 described in the task; no spindle attachment is documented. Firmware holds D8 HIG…
- Compare Moveo, Thor and PAROL6 as research baselines; keep concept selection for T113. Treat missing dimensions, prices and owned-motor performance as unknown, not nominal NEMA17 compatibility.
- Concept comparison only: retain 0.355 m pad reach, four owned motors, wrist roll and MG90S; use inherited 0.34 N m sibling torque at 0.9 A scaled to historical 0.6 A, 0.50 allowance factor, 0.90 esti…
- Use the Uno's built-in LED for a 1-second-on, 1-second-off test, with serial heartbeat output; no external LED or motor motion is needed.
- Treat the new blink inbox as a request to recheck the connected Uno; reuse the verified 1 s blink and reflash only if live checks fail. Repair the inventory completion artifact without redesigning it…

## Decisions (latest 20, decisions.md)
- Wrist coupling: generic Amazon 5 mm rigid flange coupling instead of the Pololu hub (gripper deck 3.5 mm lower so
- PLA everywhere is accepted for the deadline at 0.6 A driver current; PETG reprints of the motor parts later.
- **Wrist = roll** ("one motor to rotate the hand"), not pitch. The gripper always points along the forearm;
- **Belts, not printed gearboxes**: printed PLA planetaries backlash 0.5-2° per stage (≈ 10 mm at full reach);
- **J2 12:1 in two belt stages, motor climbs a fixed pulley**: J2 and the elbow motor ride on the upper arm behind
- **Elbow motor in the pack, belt along the upper arm** instead of a motor at the elbow: saves ~0.45 N·m at the
- **J4 direct drive** (first the Pololu 1998 hub, since the Saturday change a generic 5 mm flange coupling): roll
- **Gripper gears m2 z15** (shortened addendum 0.85) instead of m1.5 z20: same 30 mm centres, 1.5 mm tip land prints.
- **E-stop 22 mm mushroom** (22.3 hole) instead of a 16 mm latching button: no 16 mm button found rated for 6 A DC.
- **Design review 2026-10-29 fixes**: tower foot screws moved off the wall/gussets (foot extended both sides); shaft lock
- **Tool plane on the yaw axis** (upper arm offset to −Y): planar IK without a lateral offset.
- **Electronics inside the base** (Ø230, fits the X1E bed): USB-B, 24 V jack and motor-power switch on the rear.
- **PETG for the 4 motor-clamping parts**, PLA elsewhere (PLA softens at 55-60 °C).
- **Elbow belt 520 mm** (Amazon 2-pack listing; stock unverified). Fallback: 500 mm loop with L2 = 125 mm.
- Shoulder height (now 187 mm) is set by the motor pack's swing at J2 = 90°.
- Review 2 fixes: carriage nut slots 5.8 wide (nut can't turn) and the screw 0.6 past the nut; J1 motor turned 45°
- 2026-10-30: Correct requirements to 600 g and gate new CAD on capacity screening and user concept selection (why: explicit payload answer supersedes 100 g; existing performance is not verified at 600 g). [evidence](.mechy/digest.md)
- 2026-10-30: Add an independent Uno built-in LED blink test using board id uno; default to 1 second on/off and a serial heartbeat (why: the user explicitly requests a board test, independent of the arm firmware handled by their friend). […
- 2026-10-30: Supersede queued demo tasks T101-T104 and blocked T108 with T111 inventory completion, T112 missing prior art and T113 concept selection (why: baseline T105 is absent, T106 lacks a completion summary, and 600 g screening fail…
- 2026-10-30: Schedule T110 to recheck the connected Uno and restore the existing blink only if needed (why: the new inbox request postdates the completed T109 test; reuse its verified defaults). [evidence](inbox/20261030-111114.md)

## Tasks
- T101-research-gripper [cancelled] Find two gripper designs the MG90S servo can drive.
- T102-cad-forearm-lighten [cancelled] Lighten the forearm by 20% without losing stiffness.
- T103-sim-pick-cycle [cancelled] Re-run the pick-and-place cycle with the lighter forearm.
- T104-docs-build-guide [cancelled] Update the build notes for the new forearm.
- T106-docs-config-inventory [failed] Record answered constraints and the existing v1 part combination in the configuration registry.
  Error: summary missing: summary.md
- T107-research-600g-feasibility [done] Bound existing-arm capacity at 600 g and identify limiting joints and gripper.
  Result (research/payload-600g/summary.md): | What | Where | |---|---| | Evidence, prior art, verification | [note.md](note.md) | | Rebuild script | [check.py](check.py) | | Envelope | [CSV](envelope.csv), [plot](envelope.svg) | | Task handoff | [T107](../../tasks/summaries/T107-research-600g-feasibility.md) | **Existing v1 cannot substantiate 600 g at full reach.** Conditional static screening fails shoulder and elbow; no CAD or cycle simulation performed. Computed from documented estima…
- T108-concept-600g-options [blocked] Present a conventional open-source-based arm and one or two alternatives for user selection at the 600 g target.
- T109-controls-uno-blink [done] Compile, flash and verify a built-in LED blink test on the connected Arduino Uno.
  Result (firmware/uno-blink/summary.md): | What | Where | |---|---| | Firmware | firmware/uno-blink/src/main.cpp | | Build configuration | firmware/uno-blink/platformio.ini | | Commands, pin sharing, serial transcript | firmware/uno-blink/README.md | | Local summary | firmware/uno-blink/summary.md | **Result: compiled, flashed and serial-verified.** Standalone blink replaces the loaded sketch; no arm control. Uno R3 exact USB identity rechecked before upload: /dev/cu.usbmodem2101, seri…
- T110-controls-uno-blink-check [done] Verify the connected Uno is blinking and restore the verified blink firmware if needed.
  Result (firmware/uno-blink-check/summary.md): | What | Where | |---|---| | Fresh transcript, commands, LED instructions | firmware/uno-blink-check/README.md | | Task result | firmware/uno-blink-check/summary.md | **PASS: four complete blink cycles verified over serial; no reflash needed.** Checked 2026-10-30. T109 artifacts preserved; no firmware changes, compilation, upload, or motor commands. Fresh `hw_boards` identified exact Uno R3 (`uno`), `/dev/cu.usbmodem2101`, VID:PID 2341:0043, ser…
- T111-docs-inventory-completion [done] Validate the existing configuration inventory and supply its missing completion summary.
  Result (docs/config-inventory/summary.md): | What | Where | |---|---| | Completion summary | [summary.md](summary.md) | | Registry checked; unchanged

(digest cut at its size limit)
