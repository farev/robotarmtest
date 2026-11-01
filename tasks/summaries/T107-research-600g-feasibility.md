| What | Where |
|---|---|
| Evidence, prior art, verification | [note](../../research/payload-600g/note.md) |
| Rebuild script | [check.py](../../research/payload-600g/check.py) |
| Envelope | [CSV](../../research/payload-600g/envelope.csv), [plot](../../research/payload-600g/envelope.svg) |

**Existing v1 cannot substantiate 600 g at full reach.** Conditional static screening fails shoulder and elbow; no CAD or cycle simulation performed.

Computed from documented estimates: 0.355 m pad reach; horizontal shoulder/elbow demand **3.091/1.745 N·m**, versus **1.102/0.612 N·m** allowances (unverified 0.34 N·m sibling torque × 0.6/0.9 A × 12/6 ratio × 0.81/0.90 efficiency × 0.50). Optimistic allowances: **1.600/0.800 N·m**. Payload-only elbow demand: **1.294 N·m**. Actual motor torque remains unknown.

Light/heavy horizontal demands: **2.809–3.429 / 1.619–1.901 N·m**. Payload extension +0.050 m adds **0.2942 N·m** per joint. Estimated J4 motor payload penalty: **0.185/0.127 kg**. Print-list forearm/cover totals **0.095 kg**; 104 g claim unverified.

Wrist allowance **0.1133 N·m**; estimated tool imbalance leaves **0.0178 m** payload eccentricity. MG90S half-stall, 0.050 m jaw lever gives **1.412 N** total normal force, requiring **μ≥4.167**, not assumed. TowerPro's higher torque applies at **6.6 V**, not verified at configured 6 V/Miuzei.

Estimated base mass including payload **3.1266 kg**; 0.115 m support-radius edge margin changes **−0.158 to +0.130 N·m** with 0–0.050 m offset; positive tips.

**9,675 rows; 500 random-pose energy checks pass** (error <1.3e−9 N·m). Rebuild: `python3 research/payload-600g/check.py`. Static ratio implications: **33.7:1/17.1:1**, unselected. Preserve four motors and under-$100 remaining budget; no prices invented.

**Not verified**
- Exact torque/current, masses/COMs, grip, anchoring, structural/dynamic capacity, 4.6 s cycle.
- Mechy lacks this custom mass/COM/grip sweep; requested script supplied.

**Open decisions**
- T108 concept/upgrades; object/contact geometry; mounting and bench validation.
