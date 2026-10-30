# Build plan: 4-axis desktop arm (v1)

Axes: J1 base yaw, J2 shoulder, J3 elbow, J4 wrist roll ("rotate the hand"), plus a servo gripper.
Printer: Bambu Lab X1E (256 mm cube), PLA with PETG for the 4 parts that touch a motor body.
Payload target: 100 g (assumed). Ship-to: US (assumed).

| Function | Status | Part or target |
|---|---|---|
| Joint motors | owned ×4 | 42SHDC3026-15B, 0.9 A; J1 base, J2 shoulder, J3 elbow, J4 wrist roll |
| Controller | owned | Arduino Uno R3 |
| Driver board + drivers | owned | CNC Shield V3 + 4 × A4988 (4 sockets = 4 motors, A axis via jumpers) |
| Motor supply | owned | 24 V 6 A PSU; 100 µF cap owned |
| J1 reduction | buy + print | GT2 20T 5 mm pulley → printed 120T on the turret, GT2-300 closed belt, 6:1 |
| J2 reduction | buy + print | 20T → 60T (bought) then 20T → printed 80T fixed on the tower, 2 × GT2-200 belts, 12:1 |
| J3 reduction | buy + print | 20T → printed 120T on the forearm, GT2-520 belt, 6:1 |
| J4 drive | buy | 5 mm rigid flange coupling, direct drive (roll needs < 0.05 N·m) |
| Yaw bearing | buy | 2 × 6806-2RS (30 × 42 × 7) in the base tube |
| Joint bearings | buy | 4 × 608-2RS (shoulder, elbow), 2 × 625 (J2 intermediate shaft) |
| Shafts | buy | 8 mm ground rod cut 100 + 113 mm, 5 mm rod cut 52 mm, 4 × 8 mm shaft collars |
| Gripper actuator | buy | MG90S metal-gear servo (design is built around it) |
| Servo power | buy | 24 V → 6 V buck, ≥ 2 A (never the Uno 5 V pin) |
| Power entry, switch, fuse | buy | 5.5 × 2.1 panel jack (12 mm hole), 16 mm latching switch on motor power, 7.5 A inline fuse |
| Emergency stop | buy | the 16 mm latching switch cuts 24 V to the shield (a separate mushroom E-stop is better: optional) |
| End-stops (homing) | buy | 3 × lever micro switches (J1, J2, J3); mounts are not in the v1 CAD yet |
| Fasteners | owned (Invention Studio) | 35 M3 × 5.7 heat-set inserts, M3 SHCS 6-30, 7 M3 nuts, 4 M3 washers, M3 × 12 mm OD fender washer, M2 × 8 + nuts |
| Cable routing | buy | 4-wire motor extension cables ~1 m (J2, J3, J4), servo extension ~1 m, spiral wrap / zip ties |
| Programming cable | owned? | USB-A to USB-B for the Uno (usually comes with it) |
| Base fixing | buy | 4 × M5 wood screws or 2 C-clamps (the base is screwed down from inside) |
| Consumables | buy | heat-shrink, zip ties, threadlocker safe for plastic (only on metal-to-metal set screws) |
| Base, turret, tower, links, motor housings, covers, gripper | print | 18 printed parts + 2 fit coupons, design/v1/printed/ |

Tools the user may lack: soldering iron with an insert tip (heat-set inserts), 1.5/2/2.5 mm hex keys,
hacksaw or rotary tool to cut the steel rods, calipers.
