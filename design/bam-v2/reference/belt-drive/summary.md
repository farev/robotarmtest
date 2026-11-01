# CAD v2 (ref_arm — 20sffactory Community Robot Arm)

| What | Where |
|---|---|
| Assembly | arm.glb, arm.stl (ready pose). No arm.step: the vendor parts are meshes, not STEP solids. |
| Printable parts | stl/*.stl (19 files, 21 pieces), print_list.csv |
| Purchased parts | bom.csv (28 lines, about $131, estimate) |
| Sim model | arm.xml (MuJoCo), mass_props.json |

Provenance: 20sffactory Community Robot Arm (CC BY 4.0, original design Florin Tobler, vendored at
commit 6c2f573, `mechy/data/reference_designs/cad/20sffactory/`); `arm_pleuel_bend_upper_140` is a
BAM-made 140 mm levelling link (the vendor kit has none). Vendor Arduino firmware is GPL-3.0 — the
generated firmware here is mechy's own, not a copy.

This is a parallel-linkage arm (Dobot-style, `kinematics: parallel_level`): the lower motor drives
the lower shank about S, the upper motor drives the lever + pleuel loop so the upper shank's pitch
is a2 = q1+q2, and the two levelling links plus the triplate keep the manipulator level —
q1+q2+q3 = 0, the wrist is passive (no wrist motor). The cup opens straight up at every pose.
Shanks are the vendor 140 mm parts (the 120 -> 140 stretch plus the BAM-made upper levelling link).

- Links 0.14/0.14 m between pivots, shoulder height 0.0897 m,
  reach 0.334 m; cup centre 0.054 m radial + 0.02 m above the wrist axis.
- Cup 95 mm x 70 mm (net_pocket, restitution
  0.15 estimate).
- Masses from the solids (computed: mesh volume x PLA x shell/infill; catalogue masses for motors
  and bearings): upper arm 0.055 kg, forearm 0.047 kg,
  hand 0.016 kg, cup 0.046 kg, turntable 0.636 kg,
  base 0.316 kg. Passive links are lumped into the nearest driven body
  (pleuel + lower levelling link -> lower shank; lever + upper levelling link -> forearm;
  triplate -> hand) — the same lumping MJCF uses, so model and sim agree by construction.
- Printed plastic about 206 g.

Motor mapping (`mass_props.json` -> `motor_map`): `motor_angle = 4.5 * (C @ q)` with C the
passthrough matrix — motor a2 holds the upper shank's ABSOLUTE pitch (a2 = q1+q2), a3 = q123 is
constant (no wrist motor). Vendor CNC-shield socket order: X = upper arm, Y = lower arm, Z = yaw,
A = spare (vendor rail module — open decision).

Gravity-torque verification (computed; `g` = 9.81). Model = lumped-body gradient, MuJoCo =
qfrc_bias through the wrist constraint, closed form = BAM `sizing.py`
(tau_lower = g cos th1 L1 (m_ls/2 + m_us + m_tip), tau_upper = g cos th2 L2 (m_us/2 + m_tip)):
the closed form omits the passive links' lever arms, so small differences are expected — the
mujoco column is the ground truth for the lumped model.

| Pose | Motor-side torque | Model N m | MuJoCo N m | Closed form N m | vs MJ % | vs CF % |
|---|---|---|---|---|---|---|
| stretched | base | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| stretched | shoulder | 0.2477 | 0.1694 | 0.1869 | 46.2 | 32.5 |
| stretched | elbow | 0.1508 | 0.0725 | 0.1169 | 107.9 | 29.0 |
| folded | base | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| folded | shoulder | 0.0012 | 0.0012 | 0.0 | 0.0 | 118136.9 |
| folded | elbow | 0.1508 | 0.0725 | 0.1169 | 107.9 | 29.0 |
| random | base | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| random | shoulder | 0.153 | 0.1044 | 0.1162 | 46.6 | 31.7 |
| random | elbow | 0.1446 | 0.0698 | 0.1117 | 107.1 | 29.5 |

Torque budget per motor (computed; arm stretched horizontally with the ball; budget = holding x
4.5 x 50 %):

| Motor | Ratio | Joint torque N m | Motor-side N m | Budget N m | Margin | Max speed deg/s |
|---|---|---|---|---|---|---|
| base | 5.625 | 0.0 | 0.0 | 1.125 | - | 320.0 |
| shoulder | 5.625 | 0.424 | 0.248 | 1.125 | 4.54 | 320.0 |
| elbow | 5.625 | 0.176 | 0.151 | 1.125 | 7.46 | 320.0 |
| wrist | 4.5 | 0.025 | 0.0 | 0.9 | - | 400.0 |

Homing (vendor 3-endstop scheme; sensor positions need calibration with tool_shank_calibrator_140
because the firmware constants below are estimates):

| Joint | Sensor | Homes | Coordinate |
|---|---|---|---|
| base | endstop microswitch (vendor, on the socket) | q0 at the Z endstop; calibrate with Z_HOME_STEPS | q0 |
| shoulder | endstop microswitch (vendor) | a1 = q1 at the Y endstop; recalibrate with tool_shank_calibrator_140 | a1 = q1 |
| elbow | endstop microswitch (vendor) | a2 = q1+q2 at the X endstop; recalibrate with the calibrator | a2 = q1+q2 |
| wrist | none (passive joint: the linkage holds q3 = -(q1+q2)) | not homed (no motor) | q3 |

Rebuild: `mechy cad build v2`.

Not verified: belt tensioning and tooth skipping, printed-surface quality, joint stiffness/backlash,
infill-based masses (estimate — weigh the parts), home sensor positions (estimates, calibrate).
Open decisions: the 4th motor/driver — vendor rail module or a wrist servo (spare).

Warnings / open decisions:
- none
