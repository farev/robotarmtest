| What | Where |
|---|---|
| Evidence, equations, verification | [note.md](note.md) |
| Concept sketches | [options.svg](options.svg) |
| Presented choices | [arm-600g-concept.yaml](../../options/arm-600g-concept.yaml) |
| Matching presets | [configs.yaml](../../design/configs.yaml) |

**Three concepts presented through options_present; awaiting selection before any CAD.** Nominate A+B; C optional. Moveo/BCN3D MIT credited. No CAD/simulation; built/selection unchanged.

All retain **0.600 kg**, four owned motors, wrist roll, MG90S, black finish, **0.256 m** X1E cube and five PETG exceptions.

| Computed from estimates | A serial | B parallelogram | C counterbalanced |
|---|---:|---:|---:|
| Reach/radial zone, m | 0.355 | 0.145–0.335 | 0.355 |
| Pitch-moving mass excluding payload, kg | 0.783 | 0.843 | 1.613 |
| J1/J2/J3/J4 ratios | 6/80/48/1 | 6/36/36/1 | 6/48/32/1 |
| J2/J3 demand, N·m | 3.412/1.746 | 1.712/1.746 | 2.089/1.294 |
| Conditional allowance, N·m | 6.610/3.569 | 2.974/2.974 | 3.966/2.379 |
| Peak required channel rate, Hz | 2133 | 1600 | 1422 |
| Estimated USD | 82–127 | 91–141 | 90–140 |

Torque uses sibling **0.34 N·m**, **0.6/0.9 A** scaling, estimated belt losses and **0.50** factor; current-convention sensitivity reduces allowances **29.3%**. Rates assume **200 steps/rev, 1/8 microsteps, 5°/s** with compensation. C adds **0.830 kg** effective ballast. Local wrist motor costs **0.645/0.275 N·m** in serial coordinates.

MG90S friction screen needs **μ≥4.167**; roll demand **0.1555 > 0.1133 N·m** at **0.025 m** eccentricity. Anchoring required. No option establishes compliance below **$100**.

Verification: closed-form equations checked; **145 slots, 3 presets, 51/51 valid references**; SVG XML valid. Unbuilt-concept tool unavailable.

Not verified
- Motor/driver rate data, grip, dynamics, temperatures, belt strength, prices, printable envelopes; browser visual inspection unavailable.

Open decisions
- User pick; object/contact/COM before dependent CAD; anchoring and delivered BOM. Handoff: next-free vN, review, per-part STLs, print/BOM lists, assembly and rebuild commands.
