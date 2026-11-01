| What | Where |
|---|---|
| Baselines, evidence and concept handoff | [note.md](note.md) |
| Mechanism comparison (schematic, not CAD) | [comparison.svg](comparison.svg) |
| Owned-motor measurement sheet | [motor-datum.svg](motor-datum.svg) |
| Planner handoff | [summary.md](summary.md) |

**Recommendation for T113: present a conventional Moveo-derived articulated belt arm first, with remote-drive linkage and counterbalanced variants as alternatives. No concept is selected and none is verified for 0.600 kg.** Moveo supplies permissively licensed construction references; Thor supplies the closest author-reported horizontal lift; PAROL6 supplies the clearest workspace-dependent rating. None is a drop-in design for four owned motors or a demonstrated under-$100 build.

## Evidence and scope

Research date: 2026-10-30. `intake_pending` returned **0**; authorized `inspiration/links.yaml` is empty, and the supplied digest records no inspiration notes. No inspiration TODOs were available. Only authorized project inputs and the engineering library were read. No vendor assets were downloaded to disk or modified. The SVGs are original explanatory drawings, not vendor geometry. No capacity sweep, CAD build or new mechanical simulation was run.

**Configured** means supplied requirement, **published** means primary-source specification, **author measured** means the author's report (not independent replication), **computed from estimates** means inherited T107 results, and **unknown** means no substantiated value. The library labels all three `reference_designs/designs.csv` rows `value_type=datasheet`, checked 2026-10-23; this labels provenance, not measured performance. Library root: `/Users/Carlo/Empire/mechy/engine/mechy/data/`.

## Prior art

| Conventional baseline; author and licence | Reach and payload evidence | Transmission / real hardware | Printable envelope, material, copy / avoid |
|---|---|---|---|
| **1. [BCN3D Moveo](https://github.com/BCN3D/BCN3D-Moveo)** — BCN3D Technologies with Generalitat education department; acknowledges Andreas Hölldorfer. [MIT licence](https://raw.githubusercontent.com/BCN3D/BCN3D-Moveo/master/LICENSE); retain notice. Library row `bcn3d_moveo`, `datasheet`. | **5 axes** plus servo claw (library BOM). Reach and measured payload **unknown** in reviewed official evidence; do not substitute community claims. | Articulated belt arm, T5 pulleys **10T/14T**, printed large pulleys and **5:1** geared motor. Mixed NEMA17/23/14 motors, not four identical motors. Named **608ZZ, 625ZZ, 624ZZ, 623ZZ** bearings. [Official BOM](https://github.com/BCN3D/BCN3D-Moveo/blob/master/BOM/BCN3D%20Moveo%20BOM.pdf), library row. | PLA structure; largest STL envelope **unknown**, so X1E fit unverified. BOM's **0.550 × 0.550 × 0.016 m** wood base is purchased structure, not a print envelope. Copy supported shafts, belt access and editable CAD. Avoid carrying over motor substitutions or the original footprint without checking. |
| **2. [Thor](https://github.com/AngelLM/Thor)** — Ángel Larrañaga / AngelLM. [CC BY-SA 4.0](https://raw.githubusercontent.com/AngelLM/Thor/master/LICENSE); credit, describe changes and preserve share-alike. Library row `thor`, `datasheet`. | **6 axes**; author reports **0.750 kg including tool** at horizontal extension. Reach **unknown**; **0.62415 m** is vertical height without tool, not reach. [FAQ](https://github.com/AngelLM/Thor/wiki/FAQ). This is a prototype lift, not a dynamic rating. | Printed gears, GT2 belts, **7 steppers**: **3** with **5:1** reduction for pitch joints; thus no direct four-motor transplant. [Component list](https://github.com/AngelLM/Thor/wiki/Component-list). | FAQ specifies **0.200 × 0.200 m** bed using split parts, **0.200 × 0.300 m** for unsplit Art2Body; Z envelope unknown. X1E cannot be declared a fit for unsplit parts. PLA/PETG plus ABS in library materials; preserve exceptions. Copy editable FreeCAD and explicit load-test pose. Avoid printed-gear backlash and extra distal motors. |
| **3. [PAROL6](https://github.com/Source-Robotics/PAROL6-Desktop-robot-arm)** — Petar Crnjak / Source Robotics. [GPL-3.0](https://raw.githubusercontent.com/Source-Robotics/PAROL6-Desktop-robot-arm/main/LICENSE); retain licence and corresponding source for distributed derivatives. Library row `parol6`, `datasheet`. | Published **0.400 m** reach with standard gripper; **1.0 kg** near base, **0.5 kg** across workspace; robot **5.5 kg**. No independent measured payload found. [Specifications](https://docs.source-robotics.com/PAROL-docs/page2_2/). | **6** steppers; planetary/belt reductions J1–J6 **6.4, 20, 18.0952381, 4, 4, 10:1**. Two EG17-G20 and one EG17-G10; purchased precision gearing, not equivalent to bare motors. [BOM](https://raw.githubusercontent.com/Source-Robotics/PAROL6-Desktop-robot-arm/main/BOM/BOM.md). | PETG specified. [Small-bed note](https://raw.githubusercontent.com/Source-Robotics/PAROL6-Desktop-robot-arm/main/STL/SMALL_PRINT_BED/README.md) reports minimum enclosing cubes **0.1605 m** upper arm, **0.1541 m** turret blocker, with split alternatives. These two parts are below **0.256 m**, but complete oriented STL/brim fit remains unknown. Copy bearing support, homing and workspace-specific limits; avoid assuming its near-base rating or expensive gear train transfers. |

Thor's historical FAQ estimate is **€350** components; it is not a current quote or this project's remaining cost. Current US delivered prices for all three adaptations are **unknown**. PAROL6's original claw is pneumatic; replacing it with MG90S invalidates any assumed grip equivalence.

### Parts worth carrying into a selected concept

These are **source examples, not a purchase BOM or approved sizing**:

- Thor component list: **625ZZ**, **MF84ZZ**, **16014ZZ** bearings; GT2 **0.002 m pitch**, **0.006 m width**, **0.208 m closed loops / 104 teeth**, **20T/40T** pulleys; **0.005 m** rods; **M3x8, M3x10, M3x12** screws. Author table lists distal motor torque **0.2157 N·m**, differing from library's **0.26 N·m**; use the current source and neither for owned motors.
- PAROL6 BOM: **AXK3552** with thrust washers, **NSK HR32906J / HR32907J**, HTD3M **0.396/0.342/0.201/0.246 m** belts, **0.006 m** wide; **15T** J1 and **12T** J4/J5 purchased pulleys. **ZW12-3** mechanical switches and **GX-F8A** sensor are homing examples, not validated Uno wiring. Original supply is **24 V, 5 A**; owned supply is configured **24 V, 6 A**.
- Existing v1 parts in T107 include **608-2RS / 625-2RS / 6806-2RS**, **0.008 m** shafts, GT2 belts and **0.005 m** flange coupling. Ownership/usable quantities are not established by the authorized inputs. T5, GT2 and HTD profiles are not interchangeable (`knowledge/machine_elements.md` §5.1).

## Carry-forward failures — T107, not rerun

All values below are **computed from estimates**, copied from [T107 summary](../payload-600g/summary.md) and [note](../payload-600g/note.md):

| Quantity | Existing v1 screening result | Consequence for every option |
|---|---|---|
| Horizontal pad reach | **0.355 m** | Shorter reach is a trade-off, not already authorized |
| Shoulder / elbow demand | **3.091 / 1.745 N·m** | Fails conditional **1.102 / 0.612 N·m** allowances |
| Optimistic shoulder / elbow allowance | **1.600 / 0.800 N·m** | Still fails; elbow payload alone **1.294 N·m** |
| Static implied reductions | **33.7:1 / 17.1:1** | Screening thresholds only; not selected gearboxes or dynamic performance |
| Distal J4 motor penalty | **0.645 / 0.275 N·m**, equivalent **0.185 / 0.127 kg** payload at shoulder/elbow | Remote wrist drive may recover some of this; added belts/bearings subtract savings |
| MG90S at estimated **0.050 m** jaw lever | **1.412 N** normal force, required **μ ≥ 4.167** | Friction-only **0.600 kg** grip unsupported; investigate object support/form closure |
| Wrist payload eccentricity | Conditional limit **0.0178 m** | Keep roll; remote actuation does not remove object imbalance |
| Verification already performed | **500** random-pose energy checks, error **<1.3e−9 N·m** | Checks arithmetic of T107 model, not hardware |

T107 used unverified sibling torque **0.34 N·m**, current scaling **0.6/0.9 A**, estimated efficiency and the required **0.50** torque multiplier. The library Pololu 2267 row (`stepper_motors.csv`, `datasheet`, `fetched`) is **0.363 N·m at 1.7 A**, **0.285 kg**; it is a different motor. `hw/motors.yaml` and `hw/drivers.yaml` are empty. Exact 42SHDC3026-15B torque, mass, current convention, shaft and mounting geometry remain unknown. No replacement torque is inferred here.

## Concept trade-offs for T113

The conventional option is first. All retain configured **4 steppers**, **wrist roll**, MG90S claw and target **0.600 kg**. These are adaptation proposals, not claims that upstream designs already implement them.

| Option | Construction and base-mounted drives | Numbers that matter | Fit / material / remaining-spend trade-off |
|---|---|---|---|
| **A — Moveo-derived articulated belt arm** | Keep serial shoulder/elbow geometry and bearing-supported links; mount pitch motors on yaw platform and route elbow drive remotely. Retain a local wrist motor initially for comparison. | Must close T107 **3.091/1.745 N·m** load gap; reference static ratios **33.7/17.1** cannot simply be installed without new mass and speed checks. | Editable MIT base, simpler reuse of stock bearings. New motor mounts and **0.256 m** part-envelope review mandatory. Budget fit **unknown**. |
| **B — Remote-drive parallel linkage** | Adapt conventional supported joints into a base-driven elbow linkage; remote wrist roll transmission. This is a new derivative, not an existing verified Moveo configuration. Preserve hand direction along forearm; do not silently substitute a level-platform palletizer. | Removing local J4 offers gross T107 penalty **0.185/0.127 kg** before replacement mass. Actual linkage torque advantage/workspace **unknown**. | More pivots, belts and alignment work; loop closure, singularities and wrist coupling require verification. Budget fit **unknown**. |
| **C — Counterbalanced articulated arm** | Same conventional serial chain with shoulder spring/counterweight; relocate drives where possible. Counterbalance is unselected and unsized. | Shoulder-only assistance cannot fix elbow **1.745 > 0.612 N·m** or MG90S grip. Net assistance over workspace **unknown**. | Extra anchors, adjustment and stored energy; counterweight raises base loads. Budget fit **unknown**, as are acceptable workspace and setup effort. |

Reference method: `knowledge/machine_elements.md` §§13.3–13.4 describes base-driven linkage benefits and singularity checks; §1.4 describes spaced bearing moment support. These support topology choices, not a capacity number. No new analysis is being used to select a winner.

**Budget handoff:** strictly **<$100 remaining** (configured). A provisional planning envelope is **$30** belts/pulleys, **$25** bearings/shafts, **$15** fasteners, **$15** grip/power/homing, **$10** shipping/contingency = **$95**. These are allocation targets, **not current prices, quotes or a cost estimate**; tax, filament and all missing items must fit the cap. Get a delivered, quantity-specific BOM after selection; if it fails, return the cost/reach/drive trade-off to the user. Do not buy PAROL6 gearboxes on the assumption they fit this allocation.

**Materials:** prefer PLA only where subsequently justified; preserve configured PETG exceptions for base-deck, upper-arm, pack-cover, pack-carriage and forearm. The digest's “4 clamps” versus **5** manifest parts is unresolved. Historical **0.6 A** PLA override is not a thermal test. PAROL6's PETG specification reinforces this gap, but does not certify local PLA/PETG parts. Every future printed part needs material, orientation and oriented bounding-box checks; these research diagrams are not printable parts.

## Motor-fit handoff

Use [motor-datum.svg](motor-datum.svg) for **each of the four motors**, identified individually. Do not enter catalogue NEMA17 values as measurements.

1. Set datum **A** to front mounting face, **B** to shaft axis, **C** to connector side. Record body width/height/length, bolt-pattern X/Y, thread and usable depth, pilot diameter/height, shaft diameter, shaft projection from A, D-flat length/depth and rear-shaft projection. Measure connector and cable-bend keepout; weigh each motor. Record instruments and uncertainty; store dimensions in metres.
2. Identify phase pairs with an unpowered resistance check; record label, winding resistance and A4988 sense-resistor markings. Do not set Vref from an assumed clone resistor. T107 references `ItripMAX = Vref/(8 Rs)`; calibration is a controls handoff, not performed here.
3. Check the selected pulley bore, shaft engagement and setscrew position against these measurements, then print a fit coupon only after concept approval. Never infer shaft fit from the model prefix.
4. Obtain exact torque/current data or a restrained bench measurement at actual current and voltage, then torque-speed/thermal evidence. Use `Tavailable = Tmotor × ratio × efficiency × 0.50`; holding torque alone cannot establish motion capacity. Record MG90S body, ears, spline/horn, actual jaw lever and object geometry separately.

## Verification table

PASS means the stated evidence check passed; FAIL means a claim is contradicted or lacks evidence, not necessarily that a new physical design failed.

| Check | Expected | Got | PASS/FAIL |
|---|---|---|---|
| Licensed reusable baselines | At least 3 actual licences | Moveo MIT; Thor CC BY-SA 4.0; PAROL6 GPL-3.0, primary files opened | PASS |
| Load-rating semantics | Compare horizontal tool-inclusive load to full-workspace claim | Thor **0.750 kg tool-inclusive**; PAROL6 **0.5 kg** full workspace; no transfer to owned motors | PASS |
| Thor envelope interpretation | Do not equate height with reach | **0.62415 m** labelled height; reach unknown | PASS |
| Thor split XY envelope vs configured bed | **0.200 ≤ 0.256 m** on each bed axis | Published split-part XY fits; Z and unsplit orientation unverified | PASS (XY only) |
| GT2 length/tooth consistency | pitch × teeth = loop length | **0.002 m × 104 = 0.208 m**, matching Thor BOM | PASS |
| PAROL6 elbow reduction | **20 × 38/42** | **18.0952381:1**, matches published specs | PASS |
| Owned-motor substitution | Exact fit and torque evidence | Empty hardware records; no exact datasheet | FAIL |
| Existing 600 g screen (inherited) | Allowance ≥ demand | Shoulder **1.102 < 3.091**, elbow **0.612 < 1.745 N·m** | FAIL |
| MG90S holding approval (inherited) | Verified force/contact supports payload | **μ ≥ 4.167** required in T107 scenario; actual μ unknown | FAIL |
| Complete one-piece X1E fit and delivered budget | All parts fit **0.256 m** cube; total **<$100** | Complete mesh envelopes and quotes absent | FAIL (not established) |

No engineering tool exposes this source-research/SVG-datum task. Mechy intake, assumptions, progress and workspace tools were used; original SVG markup supplies the requested visuals. No ad hoc capacity script replaces a Mechy tool. The SVG files are their own editable source: open them in an SVG viewer to reproduce the visuals; no CAD rebuild command applies.

## Not verified

- Both SVGs passed XML parsing. Visual browser inspection could not run because the in-app browser is unavailable.

- Exact motor fit, torque-speed/current, mass, A4988 calibration and servo-clone ratings; current prices and delivered BOM.
- Moveo reach/payload/envelope; Thor horizontal reach and full Z fit; complete PAROL6 print envelope and independent load performance.
- All adaptation capacity, stiffness, belt loads, collision workspace, homing integration, temperatures, grip, anchoring and dynamic cycle time.

## Open decisions

- T113/user chooses A/B/C or revised trade-offs before heavy CAD; this research does not select a concept.
- Object/contact geometry, allowable reach/duty, support/anchoring and spending trade-offs remain unresolved; no previously answered question was repeated.
