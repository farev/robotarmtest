# Invention Studio Store (GT Marketplace, store 324): catalog vs the v1 arm

Source: full catalog capture by the user, 2026-10-29 20:59 ET (94 products, 17 categories; "no stock warning"
means the product page showed no out-of-stock notice; checkout inventory was not tested).
Store: https://epay.gatech.edu/C20793_ustores/web/store_main.jsp?STOREID=324&SINGLESTORE=true (free pickup,
Wepfer Design Commons).

## Usable as-is (moved to the store in parts/components.yaml)
| Need | Store product | Price | ID |
|---|---|---|---|
| Gripper servo MG90S | Miuzei MG90S 9G Metal Geared Micro Servo Motor | $3.50 | 6265 |
| J1 belt GT2 6 mm 300 mm closed | 2GT Timing Belt; Closed Loop, 6mm Width x 300mm Length | $2.00 | 6296 |
| M3 screws (backup to studio bins) | Machine Screw Assortment 440pcs M3 | $10.00 | 6313 |
| Calipers (to measure motors, coupling, coupons) | WEN 10761 Electronic 6.1-Inch Digital Caliper | $11.00 | 6316 |
| Consumables | Electrical tape $1.50 (6259), super glue $0.30 (6719); zip-tie bundle (6310) is **out of stock** | | |

## Close but not usable without a redesign
| Store product | Why not |
|---|---|
| 20 & 80 tooth GT2 1:4 reduction, **6 mm bore**, w/ belt ($8.50, 6295) | Bores are 6 mm; the motor shafts are 5 mm, so they cannot go on a motor. Only the J2 intermediate shaft could take them, and that needs a 6 mm shaft (store's 6 x 300 mm shaft, 6307, is **out of stock**; the 6 x 40 dowels, 6308, are too short for the 52 mm pulley stack). |
| 606-2RS bearing 6x17x6 ($9.99, 6727) | Would go with the 6 mm intermediate shaft above; the design uses 625 (5x16x5). |
| GT2 open-loop belt 2 m / 10 m (6299, 6298) | The design uses closed loops on fixed centres; splicing an open belt into a loop is weak and uneven. |
| GT2 idler pulley (6300) | Not needed. |
| 6 mm couplers (6305, 6306) | 6 mm, the J4 motor shaft is 5 mm. |
| 10 mm V-groove bearings (6294), drawer slides | Not used. |
| Nema 17 stepper ($14, 6266), TMC2208 driver ($4, 6271) | Already owned (4 x 42SHDC, A4988s). A TMC2208 would be a quieter optional swap; not needed. |

## Not in the store (Amazon or local shops)
608-2RS, 625-2RS and 6806-2RS bearings; GT2 20T and 60T pulleys with 5 mm bore; GT2 closed belts 200 mm (x2)
and 520 mm; 8 mm and 5 mm steel rod; 8 mm shaft collars; 5 mm flange coupling; LM2596 buck converter; 5.5 x 2.1
panel jack; 22 mm E-stop; inline fuse holder; stepper extension cables. Heat-set inserts are not listed either
(the user has access through the Invention Studio).
