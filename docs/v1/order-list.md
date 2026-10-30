# v1 order list — updated 2026-10-29 (after the pre-order review)

Dates are from Amazon product pages fetched today for Atlanta (30324). **Prime dates only apply with Prime**; without it,
the earliest free delivery is **Tuesday Nov 3**. Set ZIP 30332 at checkout and re-read each date.

## A. Order now — Prime arrives Saturday Oct 31
| ✓ | Part | Qty | Price | Link |
|---|---|---|---|---|
| ☐ | 608-2RS bearings, 10 pcs (shoulder + elbow, need 4) | 1 | $4.99 | [B0CX8JPXDW](https://www.amazon.com/dp/B0CX8JPXDW) |
| ☐ | 8 mm × 150 mm chrome rod, 2 pcs (cut 100 + 113) | 1 | $6.49 | [B0D7M8XBG4](https://www.amazon.com/dp/B0D7M8XBG4) |
| ☐ | 5 mm rigid flange coupling, 2 pcs (wrist) | 1 | $8.09 | [B07PLB2P4W](https://www.amazon.com/dp/B07PLB2P4W) |
| ☐ | 22 mm E-stop, 1 NC latching | 1 | $9.99 | [B07MJPRMRL](https://www.amazon.com/dp/B07MJPRMRL) |
| ☐ | Inline ATO fuse holder 16 AWG (10-pack) | 1 | $7.49 | [B0DG97B5HL](https://www.amazon.com/dp/B0DG97B5HL) |
| ☐ | LM2596 buck converter, 4 pcs (servo 6 V) | 1 | $6.99 | [B08L5VRBZS](https://www.amazon.com/dp/B08L5VRBZS) |
| ☐ | Stepper cables 1 m XH2.54 → PH2.0 6-pin, 6 pcs | 1 | $7.99 | [B0D57RRQVP](https://www.amazon.com/dp/B0D57RRQVP) — only if your motors have a 6-pin socket |

## B. Order now — Prime arrives Sunday Nov 1 (one day late)
| ✓ | Part | Qty | Price | Link |
|---|---|---|---|---|
| ☐ | GT2 kit: 2×60T + 2×20T + 2×200 mm belt, 5 mm bore | **2** | $11.89 each | [B09V5C1F7C](https://www.amazon.com/dp/B09V5C1F7C) |
| ☐ | Shaft collars, **metric 8 mm** bore, 10 pcs | 1 | $7.29 | [B0CQ2S44S4](https://www.amazon.com/dp/B0CQ2S44S4) |

No faster 5 mm-bore 20T/60T pulley listing turned up. Without the kit no joint can be driven, so **realistically the arm moves on Sunday at
the earliest**. The collars are optional for first assembly: the tower's shaft-lock screw already holds the shoulder rod.

## C. Not available in time from Amazon — get these locally
| ✓ | Part | Need | Amazon (too slow) | Local option today/tomorrow |
|---|---|---|---|---|
| ☐ | 6806-2RS bearing 30×42×7 (base yaw) | 2 | [B0G8ZDSXGP](https://www.amazon.com/dp/B0G8ZDSXGP) $5.03, date not shown; 10-pack Nov 10–19 | **Bike shop**: "two BB30 bottom-bracket bearings, 6806-2RS" |
| ☐ | 625-2RS bearing 5×16×5 (shoulder carriage) | 2 | Nov 10–20 ($29+) | 3D-printer / RC hobby shop (Voron/Prusa part), or Micro Center |
| ☐ | GT2 closed belt 520 mm, 6 mm (elbow) | 1 | Nov 4–6 at best ([B018528Z38](https://www.amazon.com/dp/B018528Z38)) | Micro Center 3D-printer parts aisle; check the store's stock page first |
| ☐ | 5 mm ground rod, ≥ 52 mm (shoulder intermediate shaft) | 1 | only a $77 listing, Nov 10–20 — don't buy | Invention Studio metal shop (5 mm rod / drill rod), or a 5 mm steel dowel pin ≥ 55 mm |

If these arrive late, the base, turret, tower and upper arm can still be assembled and tested on Saturday. The shoulder needs the 625s +
5 mm rod, and the elbow needs the 520 belt.

## D. Invention Studio Store (free pickup)
| ✓ | Part | Price | Link |
|---|---|---|---|
| ☐ | Miuzei MG90S servo — check the label says 180° (not 360°) | $3.50 | [product 6265](https://epay.gatech.edu/C20793_ustores/web/product_detail.jsp?PRODUCTID=6265&SINGLESTORE=true) |
| ☐ | 2GT closed belt 6 × 300 mm (base) | $2.00 | [product 6296](https://epay.gatech.edu/C20793_ustores/web/product_detail.jsp?PRODUCTID=6296&SINGLESTORE=true) |
| ☐ | WEN caliper (only if you have none) | $11.00 | [product 6316](https://epay.gatech.edu/C20793_ustores/web/product_detail.jsp?PRODUCTID=6316&SINGLESTORE=true) |

## E. From the studio bins / around the shop (no purchase)
- Heat-set inserts M3 × 5.7 (50), M3 socket heads (57: 15 × 10, 30 × 8, 10 × 12, 1 × 30, 1 × 6), 7 M3 nuts, 8 M3 washers,
  1 M3 fender washer, 2 × M2 × 8 + nuts, 4 × M5 wood screws (per-joint list: `build-notes.md` §2).
- **Servo extension:** ~1 m of 3-core wire, soldered and heat-shrunk onto the MG90S lead. The other end goes to the LM2596
  output and Uno pin A3.
- Hookup wire (18–20 AWG for 24 V: PSU adapter → fuse → E-stop → shield), heat-shrink, zip ties (the store's are out of stock).
- **7.5 A or 5 A ATO blade fuse** from an auto-parts store. The holders come with 10 A and 15 A fuses only.
- Filament: about 830 g PLA (+ PETG later for the 5 motor parts).

## Dropped
- **Panel DC jack:** it would arrive Nov 17–27, and that type is rated only 0.5–3 A. Use the **barrel-jack/terminal adapter that came with
  your 24 V supply** inside the base: run the PSU plug through the 11.3 mm rear hole and tie the cable as strain relief.

## Check before ordering (your parts)
1. **Motor connector:** do your motors have a 6-pin socket (PH2.0, like Anet printer motors)? If they have fixed wires, skip the
   stepper cables.
2. **Motor shaft:** 5 mm diameter? (the pulleys and coupling are 5 mm bore)

Total for A + B: **$83.10** before tax (A $52.03 + B $31.07, prices shown today). Section C items are extra (local prices).
