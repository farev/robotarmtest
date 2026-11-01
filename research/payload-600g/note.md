| What | Where |
|---|---|
| Static load-envelope plot | [envelope.svg](envelope.svg) |
| Reproducible calculation and verification | [check.py](check.py) |
| Full pose/mass/offset results | [envelope.csv](envelope.csv) |
| Planner summary | [summary.md](summary.md) |
| Task handoff | [T107 summary](../../tasks/summaries/T107-research-600g-feasibility.md) |

**Decision: existing v1 does not support a 0.600 kg full-reach claim on the available evidence.** Both shoulder and elbow fail the conditional static screen at horizontal extension. Elbow payload torque alone exceeds even the optimistic current-scaled allowance. Wrist capacity depends on object imbalance; friction-only gripping and unanchored stability are unresolved. Do not promote the 104 g forearm or 4.6 s cycle claims to verified results. This is a bounded screening calculation, not a redesign or capacity certification.

## Evidence and scope

Evidence labels: **configured** = project input, not measured; **datasheet** = manufacturer publication, not a test of owned hardware; **estimate** = assumed scenario; **computed** = equations below using those inputs. No masses, torques or cycle times were measured here. Date: 2026-10-30.

- **Configured:** four owned 42SHDC3026-15B motors; 0.9 A/phase user rating; deadline driver target 0.6 A; 24 V, 6 A supply; ratios J1/J2/J3/J4 = 6/12/6/1. Source: supplied digest, `parts/models/nema17-42shdc.yaml`, `control/joint_limits.yaml`. `hw/motors.yaml` and `hw/drivers.yaml` contain empty lists, so there is no populated exact-motor performance model.
- **Configured:** shoulder-to-elbow 0.135 m; elbow-to-pad 0.220 m; shoulder height 0.187 m; shoulder −30°…90°, relative elbow −135°…120°; pad height at least 0.035 m. Source: `control/joint_limits.yaml`. Horizontal pad reach = **computed 0.355 m**. Wrist is roll, not pitch.
- **Estimate:** owned-motor holding torque 0.34–0.40 N·m at 0.9 A, copied as an explicitly unverified scenario from `parts/models/nema17-42shdc.yaml`; that input relies on a sibling, not an exact-part datasheet. Exact-part manufacturer torque/current and torque/speed evidence was not found. Neither endpoint is an established bound on the owned motor.
- **Library:** `actuators_electronics/stepper_motors.csv`, row `Pololu 2267`, `value_type=datasheet`, `verification=fetched`: a different, similarly sized motor has mass 0.285 kg and torque 0.363 N·m at 1.7 A. [Pololu primary specifications](https://www.pololu.com/product/2267) confirm the size class; they do **not** establish owned-motor torque or mass. Central mass 0.280 kg/motor and sensitivity 0.220–0.350 kg are estimates.
- **Library:** `actuators_electronics/servos.csv`, MG90S rows at 4.8/6.0 V, `value_type=datasheet`, `verification=recalled`. The 6.0 V torque entry is contradicted by the current [TowerPro specification](https://towerpro.com.tw/product/mg90s-3/): 1.8 kgf·cm at 4.8 V = **computed 0.176520 N·m**, and 2.2 kgf·cm at **6.6 V** = **0.215746 N·m**. Published mass is **0.0134 kg**. The selected Miuzei servo is not established as equivalent to TowerPro. Use neither the recalled 6 V rating nor recalled stall currents as verified data for it.
- **Library:** `actuators_electronics/motor_drivers.csv`, A4988, `value_type=datasheet`, `verification=recalled`. [Allegro A4988 datasheet, rev. 8, p. 9](https://www.allegromicro.com/-/media/files/datasheets/a4988-datasheet.pdf) gives `ItripMAX=Vref/(8 Rs)`. **Computed:** 0.480 V at 0.6 A only if Rs = 0.100 Ω. [Pololu's carrier documentation](https://www.pololu.com/product/1182) explains the approximately 0.707 full-step coil-current factor. Verify clone resistors and whether the motor's torque rating uses two energized phases before comparing currents.

Library paths are relative to `/Users/Carlo/Empire/mechy/engine/mechy/data/`. Read method references: `knowledge/references_and_sources.md` §12.3 and `knowledge/machine_elements.md` §5. The task's explicit **0.50 multiplier** takes precedence over the library's different 1/1.5 margin convention.

## Mass and COM accounting

All following positions are **estimated COMs**, metres in the attached link frame: x along link, z perpendicular in its pitch plane, y lateral. Mounting origins are not COMs. Motor J2/J3 x,z are computed from the home mounting positions in `design/v1/assembly.yaml`; their transverse body centres are estimated. J4's mounting face is 0.120 m from elbow; its estimated body COM is 0.100 m. Prints use `design/v1/print_list.csv` estimated mass, not the unverified 104 g claim. Forearm plus cover = **0.0950 kg**; forearm alone = **0.0864 kg**. Material labels in the print list differ from the deadline PLA decision; no stiffness or thermal credit is taken from them.

| Item | Central mass, kg | Frame; x, z, y, m | Evidence |
|---|---:|---|---|
| All fixed-pitch prints, including tower and fixed shoulder pulley | 0.5380 | S; 0, 0, −0.025 | Print-list estimate; lumped COM estimate |
| J1 motor | 0.2800 | S; 0, 0, +0.07307 | Mass estimate; assembly mounting x,y |
| Stationary electronics, bearings, screws/inserts and shoulder shaft | 0.2800 | S; 0, 0, −0.010 | Hardware allowance estimate |
| Upper-arm print | 0.1710 | U; +0.035, 0, −0.0567 | Print estimate; unknown COM |
| Pack cover/carriage | 0.0348 | U; −0.046, 0, −0.0567 | Print estimate; COM estimate |
| Moving J2 motor | 0.2800 | U; −0.01673, −0.05076, −0.0572 | Mass estimate; mount-derived x,z |
| Moving J3 motor | 0.2800 | U; −0.04870, +0.03653, −0.0562 | Mass estimate; mount-derived x,z |
| Intermediate shaft, 625 bearings, 60T/20T pulleys | 0.0650 | U; −0.046, 0, −0.075 | Hardware allowance estimate |
| Moving belts, other pulleys, screws/inserts/wire | 0.0650 | U; +0.020, 0, −0.050 | Hardware allowance estimate |
| Elbow shaft, collars, 608 bearings | 0.0900 | U; +0.135, 0, −0.030 | Hardware allowance estimate; on elbow axis |
| Forearm and cover | 0.0950 | F; +0.075, 0, 0 | Print estimate; COM estimate |
| Moving J4 motor | 0.2800 | F; +0.100, 0, 0 | Mass/body-COM estimate |
| Flange coupling, forearm screws/inserts/wire | 0.0250 | F; +0.130, 0, 0 | Hardware allowance estimate |
| Gripper base and fingers | 0.0174 | F; +0.180, −0.014, 0 | Print estimate; COM estimate |
| MG90S | 0.0134 | F; +0.165, −0.010, +0.015 | TowerPro datasheet mass; clone/COM estimate |
| Gripper screws/nuts/horn/pads/wire | 0.0120 | F; +0.185, −0.014, 0 | Hardware allowance estimate |
| Payload | 0.6000 | F; +0.220 + δ, 0, 0 | Required mass; COM sensitivity |

S does not pitch; U rotates with shoulder; F rotates with shoulder plus elbow. Coupons and keepout solids have no operating mass. Bought items named in `parts/components.yaml` include 608-2RS, 625-2RS, 6806-2RS, 8 mm shafts, GT2 6 mm belts, pulleys, coupling and fasteners; the table explicitly allows for their mass without claiming weighed values. No external PSU mass is credited to the base.

**Sensitivity, not statistical confidence bounds:** light/heavy multiply every non-motor/non-servo mass by 0.8/1.2; each stepper becomes 0.220/0.350 kg; upper-arm x COM becomes 0/0.0675 m; forearm x COM 0.055/0.095 m; J4 x COM 0.090/0.110 m. These correlated scenarios do not bound every possible error or pose. Payload axial offsets δ = 0/0.025/0.050 m are chosen scenarios; actual object dimensions remain unknown.

## Reproducible free-body calculation

`python3 research/payload-600g/check.py` rebuilds the CSV and SVG and prints the verification/numeric tables, using only Python's standard library. Constants are a frozen transcription of authorized inputs; update them explicitly if geometry changes. No CAD, catching simulation, or trajectory model is used. Mechy's tool catalog was checked: `motor_check` accepts a variant/trajectory, but offers no interface for this missing-mass/COM, gripper-leverage and tipping sensitivity model. No suitable tool exposes this calculation; the task-requested script fills that gap without generating or reading a different variant.

For angle θ, each local COM has horizontal projection `x cos θ − z sin θ`. With g = **standard 9.80665 m/s²**:

- Shoulder gravity demand: `τ2 = g Σ(m x)` over U and F bodies.
- Elbow gravity demand: `τ3 = g Σ[m(x − x_elbow)]` over F bodies. Include all three moving steppers; J1 contributes only to base stability, not pitch torque.
- **Conditional allowance:** `Tmotor(0.9 A) × (I/0.9) × ratio × efficiency × 0.50`. Current scaling is an **estimate**. Central per-belt-stage efficiency 0.90 is an **estimate**, giving shoulder 0.81 and elbow 0.90. Direct wrist efficiency is taken as ideal 1.0, with friction unmodelled.
- The A4988 current-vector convention can reduce the simple current-scaled comparison by another factor approximately **0.707** if the sibling torque is rated at full current in both phases. This produces central allowances **0.779/0.433/0.0801 N·m** instead of **1.102/0.612/0.1133 N·m**. No extra current or PETG upgrade is authorized by this calculation.

Sweep: **1,075 pad-height-compliant poses** per case on a 5° grid, including exact horizontal extension; three mass cases × three offsets = **9,675 rows**. The unrestricted joint grid has 1,300 poses. This is the configured angular workspace with the existing pad-only height filter, **not** collision-checked usable workspace. Object clearance and other link collisions remain unknown. CSV angles are radians; plot labels convert to degrees.

## Torque results

Everything in this table is **computed from estimates** at horizontal extension, payload centred on pads. Maxima of the sampled central sweep coincide with that pose.

| Joint | Light / central / heavy demand, N·m | Central allowance at 0.6 A, N·m | Optimistic 0.40 N·m motor, ideal transmission, 0.6 A allowance | Screen |
|---|---:|---:|---:|---|
| Shoulder | 2.809 / 3.091 / 3.429 | 1.102 | 1.600 | FAIL for these scenarios |
| Elbow | 1.619 / 1.745 / 1.901 | 0.612 | 0.800 | FAIL for these scenarios |
| Wrist roll | See imbalance below | 0.1133 | 0.1333 | Conditional on object COM |
| Base yaw | Zero gravity torque about vertical axis | Not sized dynamically | Not applicable | No dynamic conclusion |

At the nominal **0.9 A** sibling scenario and central efficiencies, allowances would be **1.652/0.918 N·m**; these are still below central loads and are not deadline settings. Even at 0.9 A, 0.40 N·m and ideal transmission, elbow allowance is **1.200 N·m**, below **1.294 N·m payload-only** demand. No plausible forearm lightening alone closes that particular gap under the stated motor scenario.

| Axial payload offset, m | Central shoulder, N·m | Central elbow, N·m |
|---:|---:|---:|
| 0 | 3.091 | 1.745 |
| 0.025 | 3.239 | 1.892 |
| 0.050 | 3.386 | 2.039 |

Each additional **0.010 m** of payload extension adds **0.05884 N·m** to both joints horizontally. Conditional central full-extension payload ceilings are only **0.0284 kg shoulder / 0.0749 kg elbow**; these must **not** be advertised as measured capacity. Their strong dependence on unknown dead load makes the threshold-torque table more useful than a single capacity number.

The J4 motor alone adds **0.645 N·m shoulder / 0.275 N·m elbow**, equivalent to **0.185/0.127 kg** of pad-centred payload at horizontal extension. The rear J2/J3 motors are included with their signed lever arms; their central horizontal shoulder counterweight contribution is **−0.180 N·m**. Omitting moving motors is therefore wrong even when two provide some counterbalance.

## Wrist imbalance and gripping

For perpendicular payload COM eccentricity e about the forearm roll axis, the worst-roll gravitational demand is `g (m_payload e + Σm_tool e_tool) |cos(forearm elevation)|`. At horizontal forearm, estimated rotating gripper mass **0.0428 kg** at representative eccentricity **0.020 m** contributes **0.00839 N·m**. Payload e = 0/0.025/0.050 m gives total **0.00839/0.15549/0.30259 N·m**. Central conditional J4 allowance is crossed at **e ≈ 0.0178 m**. This is roll imbalance, separate from axial payload offset. The pitch sweep holds the estimated gripper orientation fixed and places payload COM on the roll axis; a transverse payload offset adds at most `0.600 g e` to either pitch torque (up to 0.2942 N·m for e = 0.050 m). Thus it cannot improve the claimed full-workspace capacity; full object/roll-dependent geometry remains unverified. Axial extension on the wrist axis causes pitch/bending demand but no roll gravity torque. Shaft bending/bearing ratings and asymmetric object contact are not checked.

The configured two finger gears are equal, module 2, 15 teeth, so **1:1** synchronisation; their **0.015 m pitch radius** is not the jaw-contact moment arm. Actual pivot/contact geometry is missing from allowed inputs. For symmetric jaws with effective moment arm ℓ, virtual work gives `N_total = η Tservo / ℓ`, and each jaw carries half. For friction-only vertical holding, require `μ N_total ≥ 0.600 g`; **μ is left unknown**, not assigned from a generic material table.

Using **0.50 × 4.8 V TowerPro stall torque** and estimated jaw efficiency **0.80**:

| Effective ℓ, m (estimate) | Total normal force, N (computed) | Required μ (computed, not assumed) | Ideal full-stall required μ |
|---:|---:|---:|---:|
| 0.030 | 2.354 | 2.500 | 1.000 |
| 0.050 | 1.412 | 4.167 | 1.667 |
| 0.070 | 1.009 | 5.833 | 2.333 |

Even substituting the **6.6 V** stall claim at ℓ = 0.050 m gives only **1.726 N** at the same derating/efficiency and requires **μ ≥ 3.409**. It is not a verified 6 V result. Shape capture or supporting the object from underneath changes the force model; no such object/geometry is established. Stall torque and no-load servo speed do not establish continuous holding force or dynamic lifting capacity.

## Base tipping

Use a conditional circular contact radius **R = 0.115 m**, inferred from the digest's 0.230 m base diameter. Actual foot/contact polygon and table attachment are unknown. `M_edge = g(Σm r_projected − R Σm)`; positive means tipping in that direction. For a yaw sensitivity bound, the script aligns the fixed J1 lateral mass moment with the resultant of other masses, giving `g(hypot(Sx, Sy_without_J1)+|Sy_J1|−M R)`. It conservatively allows all yaw orientations, beyond the configured 300° yaw range. Aggregated stationary COMs and which stationary masses follow yaw are estimates; this is not a verified support-polygon result.

Central total mass with payload is **3.1266 kg**. Horizontal worst-yaw edge moments at δ = 0/0.025/0.050 m are **−0.158/−0.014/+0.130 N·m**: the last tips under these assumptions; the middle has negligible static margin. At zero offset, light/heavy cases give **+0.078/−0.374 N·m**: adding mass can help tipping while worsening motor demand. If contact radius is only **0.090/0.100 m**, central zero-offset edge moments become **+0.608/+0.302 N·m**. At 0.115 m, central +0.050 m offset requires **0.115 kg** ideal central ballast merely to reach zero static margin; this is not an anchoring recommendation or a dynamic safety margin. Table anchors, if present, need a separate fastener/table check.

## Independent verification

PASS means the calculation agrees with the stated equation, **not** that the hardware passes. The closed-form horizontal FBD is explicitly expanded independently of the transformed point inventory; 500 seeded random poses also compare moments against central finite differences of gravitational potential energy.

| Check | Expected | Got | PASS/FAIL |
|---|---:|---:|---|
| Payload-only horizontal shoulder | 0.600 × 9.80665 × 0.355 = 2.08881645 N·m | 2.08881645 | PASS |
| Payload-only horizontal elbow | 0.600 × 9.80665 × 0.220 = 1.29447780 N·m | 1.29447780 | PASS |
| Expanded whole-arm horizontal shoulder FBD | 3.091446385 N·m | 3.091446385 | PASS |
| Expanded whole-arm horizontal elbow FBD | 1.744975688 N·m | 1.744975688 | PASS |
| 500 random poses: moment versus dU/dq, maximum error | < 1e−7 N·m | 1.21e−9 N·m or less | PASS |
| Axial offset +0.050 m, elbow increment | 0.29419950 N·m | 0.29419950 | PASS |
| Wrist payload eccentricity 0.025 m | 0.14709975 N·m | 0.14709975 | PASS |
| Base forward edge, sum individual moments versus total COM | −0.434622883 N·m | −0.434622883 | PASS |
| Two-jaw virtual work, 2 N_jaw ℓ | 0.07060788 N·m | 0.07060788 | PASS |
| A4988 Vref at Rs=0.100 Ω, 0.6 A | 0.480 V | 0.480 V | PASS |
| Central horizontal J2 / J3 demand ≤ conditional allowance | ≤ 1.102 / 0.612 N·m | 3.091 / 1.745 N·m | FAIL / FAIL |

## Prior art

No inspiration sources are named in this task's inputs; none were opened. No vendor files were copied. These are reference architectures, not proposals selected for this project. Library rows in `reference_designs/designs.csv` are `value_type=datasheet`; their measured and claimed fields must remain distinct.

| Open design / licence | Published evidence | What it gets right; copy / avoid |
|---|---|---|
| [BCN3D Moveo](https://github.com/BCN3D/BCN3D-Moveo), BCN3D, MIT (`bcn3d_moveo`) | No official measured payload/reach found in allowed library evidence; 5 axes per library BOM | Conventional articulated educational base; copy documented bearings, belt layouts and assembly access. Avoid inferring payload from appearance or substituting four small motors for its mixed geared/larger actuators. |
| [Thor](https://github.com/AngelLM/Thor), Ángel LM, CC BY-SA 4.0 (`thor`) | [Author's FAQ](https://github.com/AngelLM/Thor/wiki/FAQ): 0.750 kg **including tool**, lifted horizontally on author's prototype; maximum speed untested | Best nearby published horizontal-load demonstration; copy explicit test pose, tool-mass accounting and reduced pitch drives. Avoid equating author-measured lift with repeatable dynamic rating or importing its complete higher-motor-count architecture. |
| [PAROL6](https://github.com/Source-Robotics/PAROL6-Desktop-robot-arm), Source Robotics, GPL-3.0 (`parol6`) | [Manufacturer specs](https://docs.source-robotics.com/PAROL-docs/page2_2/): 0.400 m reach, 1.0 kg near base, 0.5 kg full workspace, 5.5 kg robot; **claims, no independent measurements located** | Copy workspace-dependent ratings and reduced, supported joints. Avoid treating near-base capacity as full-reach capacity; its hardware is not a demonstrated fit for the remaining budget. |

## Upgrade implications, without selecting a concept

Retain **four owned motors** and **under-$100 remaining budget**. No new purchases or prices are proposed. At central estimated efficiency and 0.6 A current scaling, horizontal demand would require approximately **33.7:1 shoulder / 17.1:1 elbow** versus configured 12:1/6:1. These are minimum **static algebraic ratios**, not buildable gearbox specifications; extra stages alter efficiency, motor speed and cycle time. Equivalent motor-side thresholds with existing ratios are **0.636/0.646 N·m at the actual drive current**. Returning to 0.9 A is not a supported remedy. Remote wrist actuation, shorter reach, counterbalance, different grip/contact support, or added reduction each changes packaging, cost and performance and belongs in T108's user-selected comparison. No option is selected here.

A 4.6 s cycle requires trajectory acceleration, moving inertia, pull-out torque versus speed at the actual drive voltage/current, grip force, thermal behaviour and repeatability data. None follows from holding torque. A lighter forearm cannot by itself establish it.

## Not verified

- Exact owned-motor torque/current/speed curve and mass; clone A4988 current calibration; belt efficiency, preload and tooth capacity.
- Actual print/hardware masses and COMs; 104 g claim; collision-free object workspace; link strength, deflection, shaft bending and thermal creep.
- Miuzei MG90S torque, current, voltage rating, continuous duty, jaw geometry, friction, object fragility/COM and form closure.
- Base contact polygon, anchoring and dynamic tipping; 600 g operation and 4.6 s cycle time.
- Tool gap: no Mechy endpoint for this supplied-mass/COM static and gripping sensitivity sweep. SVG structure was checked; visual browser inspection was unavailable in this session.

## Open decisions

- T108/user: mechanism or upgrades within four-motor and remaining-budget constraints; no purchase/concept commitment made here.
- Object dimensions, axial/transverse COM, contact surfaces and required motion/duty cycle.
- Bench evidence needed before design approval: weigh subassemblies; measure current/torque and jaw force; establish support/anchoring.
