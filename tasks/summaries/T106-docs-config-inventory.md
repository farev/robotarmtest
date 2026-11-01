| What | Where |
|---|---|
| Answered constraints | requirements.yaml |
| Evidenced slots and built v1 picks | design/configs.yaml |
| Viewing-only selection | design/selection.yaml |
| Task handoff | tasks/summaries/T106-docs-config-inventory.md |
| Summary | tasks/summaries/summary.md |

Decision: preserve existing v1 as a viewing-only combination, not fabricated inventory or approval at 600 g. No geometry, purchases or firmware changes.

Recorded user answers: 0.6 kg payload, remaining parts budget strictly below USD 100, professional-engineer builder, black finish, MG90S two-finger claw, friend handling firmware (task card). PLA preference remains.

Computed inventory counts from assembly.yaml, print_list.csv and components.yaml: 66 physical assembly instances (keepouts excluded), 20 print rows including coupons, 26 component records; 137 slots, 131 non-null picks, 6 unresolved/unselected entries. Choices cite sources. Fasteners and unmodelled add-ons are included; incomplete quantities remain unresolved.

| Check | Expected | Got | PASS/FAIL |
|---|---|---|---|
| Physical-instance coverage | 66 | 66 | PASS |
| Built entries | 137 | 137 | PASS |
| Selection matches built | Equal | Equal | PASS |
| Capacity approval | False | False | PASS |

Material conflict: manifests specify 5 PETG parts; notes say 4. Preserve manifest assignments, with historical PLA deadline exception documented. Historical current settings conflict: 0.6 A versus 0.7 A. Historical order subtotals USD 83.10 + 5.50 exclude unresolved items (components.yaml); budget compliance is unknown.

No configuration tool/schema was exposed; YAML inventory integration remains unverified. doc.build was omitted because its PDFs and supporting files fall outside this card’s output scope. Default logged with assumption_log.

Not verified
- Capacity, thermal performance, motor/servo fit, electrical protection, sourcing, licences, viewer integration.
- Full screw quantities; homing mounts; kit/model mappings; stale 100 g torque results.

Open decisions
- Concept, motor-fit and budget trade-offs.
- Reconcile material/current conflicts, unresolved add-ons and hardware mappings.
