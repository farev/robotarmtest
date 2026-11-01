# bam-v2 direct-drive delta

Only the yaw transmission and support change. The shared v1 manifests are not edited.

| Function | Status | Target / retained item |
|---|---|---|
| Yaw actuation | owned | One 42SHDC3026-15B, coaxial, 1:1 |
| Shoulder / elbow / passive wrist / gripper | retained | Original bam-v2 upper assembly and hardware |
| Yaw belt and pulleys | removed | One motor pulley, one 200 mm belt, printed rotategear |
| Yaw torque coupling | buy, candidate | Metal 5 mm flange coupling; exact dimensions unresolved |
| Axial support | retained BOM candidate | 51105 thrust bearing; ownership unresolved |
| Radial guidance / uplift restraint | print | PETG spindle/journal and bearing cover; load/wear not certified |
| Motor mounting / base fixing | print + hardware | Enclosed PETG housing; M3 screws and inserts; support-specific M4 anchors |
| Fasteners | buy or existing stock, unverified | Explicit new-base counts in bom.csv |
| Homing | retained switch, bracket unresolved | New yaw bracket/cam and steps calibration required |
| Drivers and cooling | owned / retained | CNC shield, A4988, heatsinks; current/thermal checks unchanged |
| PSU, controller, capacitor | owned / retained | Existing 24 V supply, Uno and bulk capacitor |
| Switch, fuse, emergency stop | retained open audit | Not redesigned by this geometry change |
| Wire, connectors, motor extensions, USB | retained | Yaw motor plug faces a 22 mm cable port in the housing |
| Consumables, tools and spares | retained open audit | No new tools assumed owned; fit coupon added |

This is a design delta, not an orderable full-build cart. No part was promoted to preferred/selected.
