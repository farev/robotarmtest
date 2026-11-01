| What | Where |
|---|---|
| Concept comparison and verification | [note.md](note.md) |
| Original concept sketches | [options.svg](options.svg) |
| Interactive choice | [arm-600g-concept.yaml](../../options/arm-600g-concept.yaml) |
| Matching unselected presets | [configs.yaml](../../design/configs.yaml) |
| Planner handoff | [summary.md](summary.md) |

**Decision: present A first; nominate A and B for subsequent CAD/simulation, with C available if counterbalancing is preferred. No concept is selected. All new CAD, variants and simulation are gated on the user's pick.** Selection authorizes development, not fabrication or a 600 g rating. Neither grip nor the strictly under-$100 remaining budget is established for any option.

## Constraints and evidence

All options retain **0.600 kg**, **four owned 42SHDC3026-15B motors**, base yaw / shoulder / elbow / **wrist roll**, selected **Miuzei MG90S**, black finish, X1E **0.256 m cube**, PLA preference and the documented PETG exceptions. The hand points along the forearm; no independent wrist pitch is added. Owned electronics remain Uno, CNC Shield V3, A4988, 100 µF/50 V capacitor and **24 V/6 A** supply. No firmware, current setting or power wiring is changed.

Sources are the supplied digest, [T112 prior art](../arm-baseline/note.md), [T107 screening](../payload-600g/note.md) and the engineering library. No new external research or vendor downloads. **Configured** means requirement; **computed** means the equations below; all concept masses, COMs, efficiency, cost, effort and packaging are **estimates**. No new measurement is claimed.

T112 reports `hw/motors.yaml` and `hw/drivers.yaml` empty. They are outside this card's inputs and were not reread. Exact motor torque/speed, step angle and **max_step_rate_hz are unavailable**. The inherited **0.34 N·m at 0.9 A** is an unverified sibling scenario, not a lower bound on the owned motors. The historical **0.6 A** setting is a comparison input, not thermal approval.

## Option table — A first

| Item | A — conventional articulated belt arm | B — base-driven parallelogram | C — dead-load counterbalanced arm |
|---|---|---|---|
| Option / registry id | `arm-600g-A` | `arm-600g-B` | `arm-600g-C` |
| One-line idea | Adapt Moveo's supported serial joints and accessible belts, adding reduction for the owned motors. | Drive forearm absolute elevation through a four-bar from the yaw platform. | Balance the serial arm's own weight at both pitch joints using rear ballast. |
| Source / licence | BCN3D Technologies **Moveo, MIT**; preserve notice when copying assets. | Original linkage adaptation of Moveo support details, **MIT**; library §13.4 mechanism reference. Not an existing verified Moveo configuration. | Original counterweight adaptation of Moveo, **MIT**. Not an upstream rated design. |
| Layout | J1 motor fixed in base; J2/J3 on yaw platform, J3 belt routed along upper arm; J4 local on forearm, direct roll. | J1 fixed; J2/J3 on yaw platform; 0.135 m parallel rods and 0.060 m equal cranks transfer forearm angle; J4 local direct roll. | A's layout plus independent rear tails on upper arm and forearm, each with 0.200 m effective ballast lever. |
| Ratios J1/J2/J3/J4 | **6 / 80 / 48 / 1** | **6 / 36 / 36 / 1** | **6 / 48 / 32 / 1** |
| Pitch-moving mass, excluding payload | **0.7828 kg estimate** | **0.8428 kg estimate** | **1.6127 kg estimate**, including **0.8299 kg** effective ballast assemblies |
| Reach / zone | 0.135 m upper + 0.220 m elbow-to-pad = **0.355 m** nominal reach | Same links; estimated transmission-angle restriction gives radial annulus **0.145–0.335 m** before collisions/height limits | **0.355 m** nominal reach; rear tails need additional clearance |
| J2/J3 static gravity demand | **3.412 / 1.746 N·m**, conservative serial-load envelope | **1.712 / 1.746 N·m** in independent shoulder / absolute-forearm coordinates; not a claim about individual link bearing moments | **2.089 / 1.294 N·m** with ideal dead-load balance, payload at pads |
| J2/J3 allowance, 0.50 factor | **6.610 / 3.569 N·m** conditional | **2.974 / 2.974 N·m** conditional | **3.966 / 2.379 N·m** conditional |
| Current-convention sensitivity | **4.674 / 2.524 N·m** | **2.103 / 2.103 N·m** | **2.804 / 1.683 N·m** |
| J4 distal motor cost | All options retain estimated **0.280 kg** J4; gravity cost **0.645 N·m shoulder / 0.275 N·m elbow** in serial coordinates, equivalent **0.185 / 0.127 kg** payload. | In B's independent coordinates J4 adds **0.371 N·m J2 / 0.275 N·m J3**. Extra linkage mass means B is not the lightest. | Same motor mass; balancing removes its ideal static demand but increases inertia and support load. |
| Estimated printed / purchased physical pieces | **26–34 / 110–150** | **30–40 / 125–175** | **30–40 / 120–165** |
| Estimated new spend, all missing mechanical parts | **$82–127** | **$91–141** | **$90–140** |
| Estimated hands-on / print-machine time | **12–18 / 30–45 h** | **18–28 / 35–55 h** | **16–24 / 35–50 h** |
| Main risk | Multiple belt stages: compliance, belt pull, unknown running torque and cost. | Toggle singularities, linkage interference and coupled control; smaller usable zone. | Ballast/guard mass, rear collision and inertia; balancing depends on actual mass moments. |

Purchased counts include the four owned motors, electronics, bearings, shafts and individual fasteners; they are assembly estimates, not shopping quantities. Moving masses count everything above J2 including allowances for prints, supports, belts and wire; J2/J3 motors yaw with the platform but do not pitch. Yaw-platform hardware is not yet mass-modelled. No cycle time or catching capability is claimed.

**B is better on shoulder actuator gravity torque: 1.712 versus A's conservative 3.412 N·m (about 50% lower).** It sacrifices about 0.020 m outer reach and adds assembly complexity. A remains the conventional first option; no numerical score overrides a failed requirement. C reduces gravity by a different method but adds approximately 0.830 kg, so is a reserve option rather than a presumed improvement.

## Sketch transmissions and real-part candidates

All pulley ratios mean motor revolutions / output revolution. GT2 pitch is **0.002 m**. Use purchased 20T motor pulleys with bore verified against the actual shafts; printed larger pulleys have steel shafts and spaced bearings. The numbers below are **provisional combinations**, not completed belt routing.

| Drive | Candidate pulley stages | Candidate closed loops |
|---|---|---|
| Common yaw, 6:1 | 20T→120T | 0.300 m × 0.010 m width |
| A shoulder, 80:1 | 20→40, 20→100, 20→160 | 0.200, 0.300, 0.400 m; 0.012 m width on loaded stages |
| A elbow, 48:1 | 20→60, 20→80, 20→80; then equal 65T transfer along upper link | 0.200, 0.200, 0.200 m; transfer **0.400 m**, 0.012 m width |
| B shoulder and absolute forearm, each 36:1 | 20→60, 20→60, 20→80 at platform; forearm output through equal-crank linkage | Three 0.200 m loops per drive, 0.012 m width on loaded stages |
| C shoulder, 48:1 | 20→40, 20→80, 20→120 | 0.200, 0.200, 0.300 m |
| C elbow, 32:1 | 20→40, 20→80, 20→80; equal 65T transfer | Three 0.200 m loops plus 0.400 m transfer; loaded stages 0.012 m width |
| Common wrist | Direct 1:1, 0.005 m nominal rigid flange coupling; separately supported roll shaft | No belt; shaft fit and coupling holes require measurements |

The equal-65T transfer has exact nominal loop length `2×0.135 + 65×0.002 = 0.400 m`. Tension adjustment and concentric transfer bearings are still needed. Large 120T/160T and transfer 65T pulleys are computed geometry, not verified purchasable products. Largest listed pitch diameter is **0.1019 m** for 160T. Use the library belt-length/wrap equations to set centres during CAD; all other loop lengths are candidate stock lengths, not confirmed fits. Do not inherit the v1 520/500 mm fallback.

Common bearing candidates: two **6806-2RS** yaw bearings, paired **608-2RS** pitch bearings on **0.008 m** steel shafts, paired **625-2RS** intermediate bearings on **0.005 m** shafts. B adds four-bar pivots with 608-2RS supports; C retains paired supports and adds captive ballast fastenings. Do not use motor bearings to carry arm bending. Candidate fasteners: **M3x8/M3x10/M3x12/M3x30**, M3 nuts/washers for covers and motor mounts; **M4x20** through bolts/nuts for link laminations and **M6x40** through bolts with large washers for table attachment (actual lengths depend on stack and table thickness). No extrusion is needed in these concepts.

Common homing proposal: three **ZW12-3 lever microswitches** for J1/J2/J3 and a manually indexed wrist mark. Electrical compatibility, mounts and repeatability are unverified. Retain the selected MG90S; propose a separately regulated **4.8 V** servo rail for the screening case, using an LM2596 module only after clone-voltage/current checks. Servo current demand is unknown; do not power it from the Uno regulator or 24 V directly. Supply capacity and E-stop/fuse integration require the controls handoff.

## Reproducible static screen and source labels

Use `g=9.80665 m/s²` (standard), lengths in metres, angles in radians. Library references: `knowledge/motors_actuators.md` §§2.4, 8 steps 2–5; `physics_fundamentals.md` §10.1; `machine_elements.md` §§5.2–5.4 and 13.3–13.4. The task's **0.50 multiplier** takes precedence over the library's alternative 1.5 load-factor convention. These are hand-evaluated closed-form calculations, not a motion simulation.

Estimated forearm inventory, adapted from T107: frame **0.095 kg at 0.075 m**, J4 **0.280 at 0.100**, coupling/wire **0.025 at 0.130**, combined gripper **0.0428 at 0.180**. Thus forearm mass `mF=0.4428 kg`, first moment `hF=0.046079 kg·m`. A/C upper frame/hardware **0.250 kg at 0.0675 m**, elbow support **0.090 kg at 0.135 m**. B allows **0.300 kg at 0.0675 m** plus **0.100 kg at the elbow** for the added linkage. These are new concept allowances, not inherited measured mass. If CAD exceeds them, recalculate.

For serial angles θ (upper) and φ (relative elbow), potential energy is:

`U = g{[0.250×0.0675 + (0.090+mF+0.600)×0.135] sin θ + [hF+0.600×0.220] sin(θ+φ)}`.

Then `τ2=∂U/∂θ`, `τ3=∂U/∂φ`. At horizontal, both cosines equal one, giving **3.411557 / 1.746358 N·m**. Since coefficients are positive and `|cos|≤1`, these also bound the ideal serial gravity terms over all poses. Remote belt coordinates can redistribute motor loads; A conservatively retains this serial J2 bound until routing is derived.

For B, independent α is forearm absolute elevation; replace upper quantities with B's and `sin(θ+φ)` with `sin α`. Thus `τθ=g[0.300×0.0675+(0.100+mF+0.600)×0.135]cos θ` and `τα=g[hF+0.600×0.220]cos α`. The amplitude bounds are **1.711535 / 1.746358 N·m**, although both-horizontal is excluded by the proposed linkage operating range. A true parallelogram has unity angular transfer away from toggles; use relative angle **40°–140°** as a preliminary exclusion, not a verified motion limit. `r²=L1²+L2²+2L1L2 cos φ` gives the displayed annulus. The linkage must turn the forearm itself, not keep the tool level.

For C, ideal forearm balance first moment is **0.046079 kg·m**: effective assembly **0.230395 kg at −0.200 m**. Shoulder balance is `[0.250×0.0675+(0.090+mF+0.230395)×0.135] = 0.119906325 kg·m`: **0.599531625 kg at −0.200 m**. These include equivalent carrier/tail moments; actual ballast must be trimmed after weighing, not simply add these masses to an unaccounted tail. Dead-load sin terms cancel at every pose in the ideal model, leaving payload-only torques **2.088816 / 1.294478 N·m**. Empty-arm gravity is ideally zero, so there is no payload-tuned reversal. A 10% imbalance of the compensated moment gives approximately **0.118 / 0.045 N·m** residual in the corresponding balance coordinates; serial coupling must be included in detailed checks.

Available torque is `0.34×(0.6/0.9)×N×η×0.50`. Efficiencies are **estimates**: yaw 0.90; pitch reduction 0.90³=0.729; A/C elbow includes one additional transfer, 0.90⁴=0.6561; direct wrist ideal 1.0. Every option has conditional J1/J4 allowances **0.612 / 0.1133 N·m**; with the inherited possible current-vector factor **1/√2**, these become **0.4327 / 0.0801 N·m**. J1 gravity torque is zero about a vertical axis; inertia, friction and acceleration are unsized. None of the static allowances is verified pull-out torque at speed.

## Step rates, contact, anchoring and budget

Assume **200 full steps/rev**, **1/8 microsteps**, individual joint speed **0.0872665 rad/s (5°/s)** for comparison, not a selected motion profile. `f=200×8×N×ω/(2π)`.

| Required pulse rate, Hz | A | B | C |
|---|---:|---:|---:|
| J1 | 133 | 133 | 133 |
| J2 | 1,778 | 800 | 1,067 |
| J3 independent coordinate at 5°/s | 1,067 | 800 | 711 |
| Conservative J3 with shoulder/relative-elbow compensation, 10°/s | **2,133** | **1,600** | **1,422** |
| J4 | 22 | 22 | 22 |
| Sum of conservative simultaneous channel rates | **4,067** | **2,556** | **2,644** |
| Compare with `hw/drivers.yaml.max_step_rate_hz` | **UNKNOWN** | **UNKNOWN** | **UNKNOWN** |

The highest A motor speed is **80 rpm** at compensated J3; A shoulder is **66.7 rpm**. Rates double at 1/16 microsteps or double joint speed. Firmware must support four independent axes plus servo/homing and the actual compensation Jacobian; CNC Shield V3's usual A-axis cloning cannot be assumed to supply independent wrist control. No generic A4988 chip pulse limit is substituted for missing firmware rate. Validate both per-channel and simultaneous generation limits.

**Contact is the common hard limit.** T107's TowerPro **4.8 V stall torque 0.176520 N·m** is datasheet evidence for a different unit, not the Miuzei clone. With the 0.50 multiplier, estimated efficiency 0.80 and 0.050 m jaw lever: `Ntotal=0.5×0.176520×0.8/0.050=1.412 N`; required friction **μ≥4.167** for 5.884 N weight. No friction-only 600 g approval. Offer object-specific under-support or form closure as the next grip study; it is not silently included as an established solution. Object shape/contact area, COM and roll orientation must be obtained before grip CAD or lifting tests.

Direct roll worst-case demand at 0.025 m transverse payload eccentricity is **0.1555 N·m**, exceeding even the central allowance. Conditional eccentricity ceilings are **0.0178 m**, or **0.0122 m** with the current-vector sensitivity, using T107's tool moment **0.00839 N·m**. Axial payload offset **+0.050 m** adds **0.2942 N·m** to serial pitch demands; transverse offset can add further demand. Neither a supported object nor a higher pitch ratio solves roll imbalance.

**Anchoring is required for development; unanchored operation is not approved.** Candidate: four M6 through bolts, washers/backing plate, approximately **0.160 m** front/rear span on a structurally suitable bench. A's nominal 3.412 N·m forward moment alone implies approximately **21.3 N** total tensile-row force at that span, or **42.6 N** with a 2× screening multiplier, before base eccentricity, belt, dynamic and user loads. This is not a fastener/table strength check. B's physical moment can approach **3.458 N·m**, despite lower actuator torque; C's nominal balanced moment is **2.089 N·m** but adds dead weight and rear swept volume. Clamps are an alternative only after verifying their load path. Do not reuse T107's near-tipping unanchored base claim.

| Cost allowance, USD, all estimates (no quotes) | A |
|---|---:|
| Belts and purchased small pulleys | 30–40 |
| Bearings, shafts and coupling | 15–23 |
| Screws, nuts and washers | 8–12 |
| MG90S, regulation, homing and wiring/protection allowance | 12–18 |
| Black PLA/PETG consumed | 7–12 |
| Anchoring | 3–7 |
| Shipping and tax | 7–15 |
| **Total** | **82–127** |

B adds estimated **$9–14** in pivots, links and fasteners; C adds **$8–13** for ballast, retention and guards. No unconfirmed mechanical stock is credited. Four owned motors and supplied electronics cost zero additional here. Tools/bench modification, if needed, are extra and could invalidate the ranges. Even A's range crosses **$100**; all budget compliance flags remain false. Obtain quantity-specific delivered quotes before committing geometry; if total cannot be strictly below $100, return a concrete trade-off for approval, not an automatic budget increase.

## Print and handoff gates

Sketch packaging targets: largest individual print within **0.240×0.240×0.240 m**, leaving nominal room inside the 0.256 m cube; split rear tails and long guards where needed. This target is not mesh-envelope verification. Black PLA for non-clamping covers/pulleys where justified; keep PETG for **base-deck, upper-arm, pack-cover, pack-carriage, forearm** or their functional successors. Preserve all five manifest exceptions; the historical “four clamps” conflict is unresolved. No 0.6 A PLA thermal certification.

Orientation proposals: links and four-bar rods flat, long axis in XY; pulleys face down / shaft axis vertical; clamp rings axis vertical; base deck flat; motor cradles on their load-bearing side with bracket load path in XY; guards/covers broad face down. These are families, not an issued print list. Final per-part material/orientation depends on stress and thermal review.

After selection, the planner allocates **next-free vN** (not reserved here). Always include conventional A in any authorized comparative CAD/sim round; the present task does not build A without the pick. A/C likely need explicit remote-drive and counterweight geometry; B requires a custom `model.py` if the default generator cannot represent the closed loop. Check tool support before copying parameters. Use `cad_params_set`, `cad_build`, applicable static/kinematic/structural simulations and `motor_check` only on the approved variant; verify wrist roll rather than generator-assumed pitch. Deep review/fix loop must include ≥500 pose energy/Jacobian checks, link collisions/toggles, belt wrap/tension, motor-speed curves, anchoring, heat, grip and budget. No ball-catching simulation substitutes for a lift test.

Final build handoff must include **one STL per printed part**, `print_list.csv` (quantity/material/orientation/estimated grams), complete sourced `bom.csv` including screws, assembly order, and artifact-specific rebuild commands. These are gated future deliverables, not claimed outputs of this concept task. Current SVG is its own editable source: open `research/concepts-600g/options.svg` in an SVG viewer. The static screen is reproducible from the explicit equations and inventories above; no CAD rebuild command applies yet.

## Verification table

PASS checks an equation or record, not hardware compliance. All computed concept results use estimated inputs.

| Check | Expected | Got | PASS/FAIL |
|---|---|---|---|
| Static method against T107 verified payload result | 0.6g×0.355 / 0.6g×0.220 | 2.088816 / 1.294478 N·m | PASS |
| A sum of individual horizontal moments vs coefficients of dU/dθ,dU/dφ | Same independent expansion | 3.411557 / 1.746358 N·m | PASS |
| B virtual work with independent absolute forearm coordinate | J2 excludes forearm rotation term | 1.711535 / 1.746358 N·m amplitude bounds | PASS analytically; mechanism unverified |
| C cancellation of both dead-load first moments | Zero remaining dead-load sin coefficients | 0 at ideal target moments; payload 2.088816/1.294478 | PASS algebra only |
| A reductions from tooth ratios | 2×5×8; 3×4×4×1 | 80; 48 | PASS |
| Transfer belt p×teeth+2C | 0.002×65+2×0.135 | 0.400 m / 200 teeth | PASS nominal geometry |
| Step-rate check by motor rev/s | A shoulder 80×5/360×1600 | 1777.78 Hz | PASS arithmetic |
| 600 g grip and eccentric roll at 0.025 m | Verified support; demand ≤ allowance | μ requirement 4.167 unverified; 0.1555 > 0.1133 N·m | FAIL |
| A nominal pitch demand vs current-vector allowance | Demand ≤ allowance | 3.412≤4.674; 1.746≤2.524 | PASS conditional static only |
| B nominal pitch bounds vs current-vector allowance | Demand ≤ allowance | 1.712≤2.103; 1.746≤2.103 | PASS conditional static only |
| C ideal balanced demand vs current-vector allowance | Demand ≤ allowance | 2.089≤2.804; 1.294≤1.683 | PASS conditional static only |
| Delivered budget / speed / exact motors / full print fit | Evidence for every required threshold | Quotes, rate model, motor data and meshes absent | FAIL to establish compliance |

Library provenance: `data/standard_parts/bearings_deep_groove.csv` rows **608/625/6806**, `value_type=handbook_typical`, dimensions **0.008×0.022×0.007 / 0.005×0.016×0.005 / 0.030×0.042×0.007 m**; ratings not used as verified. `shafts_linear_precision.csv` **shaft-5/shaft-8**, `standard`; `fasteners_iso4762_shcs.csv` **M3/M4/M6**, `standard`. `timing_pulleys.csv` **GT2-20T/40T/60T/80T/100T**, `standard`; larger/custom counts use pz/π. `timing_belt_closed_loops.csv` **GT2-200/300/400**, `handbook_typical`; width/stock unverified. `timing_belt_profiles.csv` **GT2**, `estimate`: rough 8 N/mm working pull must not decide belt strength. A's 65T transfer needs about **84.4 N** effective pull at nominal J3, before preload/dynamics; 12 mm width's estimated 96 N is not approval. `actuators_electronics/stepper_motors.csv` **Pololu 2267**, `datasheet/fetched`, is a different motor; no owned-motor substitution. `motor_drivers.csv` **A4988**, `datasheet/recalled`, does not supply project firmware rate. `servos.csv` **MG90S**, `datasheet/recalled`; its 6 V torque conflict is superseded by T107's primary-source 4.8/6.6 V evidence.

Credit retained from T112: [BCN3D Moveo](https://github.com/BCN3D/BCN3D-Moveo), BCN3D Technologies, MIT. Comparison-only references: [Thor](https://github.com/AngelLM/Thor), Ángel Larrañaga, CC BY-SA 4.0, author-reported 0.750 kg including tool; [PAROL6](https://github.com/Source-Robotics/PAROL6-Desktop-robot-arm), Petar Crnjak/Source Robotics, GPL-3.0, published 0.5 kg full workspace / 1 kg near base. Neither establishes this arm's capacity. No vendor geometry was copied or edited; future copies require original licences and untouched vendor originals.

Registry QA: **145 slots**, **3 presets**, **51/51 valid preset references**, no duplicate YAML keys. `built` was compared by parsed-content SHA-256 and `design/selection.yaml` by file SHA-256: both unchanged; selection still equals built.v1. Presets are explicit concept groups, not incomplete copies of v1 geometry. SVG XML parses; visual browser inspection was unavailable because the in-app browser is not enabled.

## Not verified

- No Mechy tool accepts an unbuilt concept mass/COM/closed-loop/balance screen or emits concept SVGs. `motor_check` requires a variant; using it now would require unauthorized variant work. Hand closed-form screening and original SVG markup fill that gap; no ad hoc CAD/sim script was written.
- Exact motor fit/mass/torque-speed/current; firmware step limits and four independent axes; servo clone/contact; all dynamic, stiffness, thermal, belt, coupling, print-envelope and bench checks.
- Prices, complete part quantities, viewer preset integration, actual ballast moments, coupled transmission Jacobians and 500-pose checks for these new concepts. T107's 500 checks verify its prior model only.

## Open decisions

- User selects A/B/C for development; built and viewing selection stay unchanged. A and B are the proposed comparison pair; C is optional if balancing is preferred.
- Obtain object/contact geometry and COM before dependent gripper/roll CAD; verify anchoring method and quantities/cost before detailed commitment. No budget increase or topology change is preauthorized.
