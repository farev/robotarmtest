| What | Where |
|---|---|
| Prior art, sources, verification, motor-fit handoff | [note.md](note.md) |
| Concept comparison | [comparison.svg](comparison.svg) |
| Motor measurement diagram | [motor-datum.svg](motor-datum.svg) |

**Recommendation:** T113 should present a conventional Moveo-derived belt arm first; compare remote-drive linkage and counterbalanced alternatives before selecting CAD. No 600 g compliance claimed. Intake recheck: **0 pending**; no inspiration notes supplied.

Three licensed baselines: [Moveo](https://github.com/BCN3D/BCN3D-Moveo) **MIT**, reach/payload/print envelope unknown; [Thor](https://github.com/AngelLM/Thor/wiki/FAQ) **CC BY-SA 4.0**, author-reported **0.750 kg including tool horizontally**, **0.200 m square** split-part bed, unsplit **0.200×0.300 m**, Z unknown; [PAROL6](https://docs.source-robotics.com/PAROL-docs/page2_2/) **GPL-3.0**, claimed **0.400 m reach**, **0.5 kg full workspace / 1 kg near base**. Library rows: `value_type=datasheet`; claims remain claims. Thor's **0.62415 m** height is not reach.

Inherited [T107](../payload-600g/summary.md) estimates, not rerun: **0.355 m** reach; shoulder/elbow demand **3.091/1.745 N·m** versus **1.102/0.612 N·m** allowance; static implied ratios **33.7/17.1:1**, unselected. Distal J4 penalty **0.645/0.275 N·m**, equivalent **0.185/0.127 kg** payload. MG90S scenario: **1.412 N**, required **μ≥4.167**. Grip failure persists for every option.

Preserve **four motors**, wrist roll, **0.256 m** printer cube, PLA preference/PETG exceptions and **<$100** remaining. The **$95** allocation in the note is a planning target, not prices or cost validation. Motor diagram specifies datums, shaft/pilot, holes, connector clearance and mass measurements.

**Not verified**
- Exact motor torque/fit/current; complete print envelopes, prices, grip, dynamics and thermal capacity.
- SVG XML passes; browser unavailable for visual inspection. No Mechy research-diagram endpoint; original SVG markup used.

**Open decisions**
- T113 concept selection; reach, object/contact, anchoring and budget trade-offs. No repeated questions asked.
