| What | Where |
|---|---|
| Completion summary | [summary.md](summary.md) |
| Registry checked; unchanged | [configs.yaml](../../design/configs.yaml) |
| Selection checked; unchanged | [selection.yaml](../../design/selection.yaml) |

Decision: retain v1 for viewing only, never capacity approval. No demonstrated registry/reference errors; no corrections. T106 card/state untouched.

Constraints retained: 0.6 kg (600 g), remaining budget strictly below USD 100, black finish, MG90S claw, four owned steppers, PLA preference. New CAD requires capacity screening and user concept selection ([requirements, supplied digest](../../.mechy/digest.md)).

Computed YAML checks against [registry](../../design/configs.yaml) and [selection](../../design/selection.yaml):

| Check | Expected | Got | PASS/FAIL |
|---|---|---|---|
| Slots/built/selection counts | 137 each (T106) | 137 each | PASS |
| Valid non-null references | 131 (T106) | 131 | PASS |
| Missing slots/duplicate keys | 0 | 0 | PASS |
| Selection equals built.v1 | Equal | Equal | PASS |
| Approval/capacity verified | False | False | PASS |

[T106 handoff](../../tasks/summaries/T106-docs-config-inventory.md) supplies expected counts. Six null picks remain: component.21 (rejected panel jack), component.26 (optional caliper), addon.cable-wrap, addon.insert-tool, addon.hex-keys, addon.rod-cutting.

Registry retains five PETG assignments: base-deck, upper-arm, pack-cover, pack-carriage, forearm; notes claim four. Historical 0.6/0.7 A settings are not thermal validation. Historical USD 83.10 + 5.50 subtotals exclude unresolved costs (registry unresolved_mappings).

No registry-validation tool exposed; checked YAML locally. doc.build omitted: generated build artifacts exceed this inventory-only card. No new design or licence claims.

Not verified
- Capacity, motor/servo fit, thermal behavior, protection, prices, quantities, licences, viewer integration; external source/model existence was not checked.
- Registry unresolved_mappings retained: composite electronics, pulley-kit/belt allocation, elbow rod mapping, screw/washer counts, homing mounts/sourcing, fuse rating, geometry-dependent belt fallback; stale payload calculations remain historical.

Open decisions
- Concept, motor fit, budget trade-offs; resolve optional caliper, cable routing and tool availability.
- Reconcile material/current conflicts and hardware mappings; rejected panel jack remains unselected.
