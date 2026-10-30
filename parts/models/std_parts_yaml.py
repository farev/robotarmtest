"""Write <slug>.yaml provenance for the standard-part models built by std_parts.py and for the
generated belts and keep-outs."""
from pathlib import Path

import yaml

HERE = Path(__file__).parent
TABLE = "/Users/fabianarevalo/Documents/Mechy/engine/mechy/data/standard_parts"
D = "2026-10-29"


def w(slug, part, frame, dims, source, note=""):
    y = {"part": part, "model_source": "datasheet", "source_url": source, "datasheet": source, "retrieved": D,
         "generator": "parts/models/std_parts.py" if not slug.startswith(("belt", "nema17-plug")) else
         ("design/v1/make_assembly.py" if slug.startswith("belt") else "parts/models/nema17-plug-keepout.py"),
         "frame": frame,
         "critical_dims": [{"name": n, "value_mm": v, "tol_mm": t, "source": s, "model_mm": v} for n, v, t, s in dims],
         "checked": f"{D}: modelled from the listed values; inspect bbox matches", "note": note}
    (HERE / f"{slug}.yaml").write_text(yaml.safe_dump(y, sort_keys=False, width=120))


for slug, (d, Dd, B) in {"bearing-608": (8, 22, 7), "bearing-625": (5, 16, 5), "bearing-6806": (30, 42, 7)}.items():
    w(slug, f"{slug.split('-')[1]}-2RS deep groove ball bearing", "axis Z, centred (z = -B/2..B/2)",
      [("bore", d, 0.01, "standard"), ("outer diameter", Dd, 0.01, "standard"), ("width", B, 0.1, "standard")],
      f"{TABLE}/bearings_deep_groove.csv")
for slug, (t, odia, fl, hub) in {"gt2-20t-5mm": (20, 12.224, 16, 16), "gt2-60t-5mm": (60, 37.689, 42, 20)}.items():
    w(slug, f"GT2 {t}T pulley, 5 mm bore, 6 mm belt", "axis Z, hub end face at z = 0, hub 0..7, teeth 8..15, belt centre z = 11.5",
      [("outside diameter", odia, 0.1, "standard (timing_pulleys.csv)"), ("bore", 5.0, 0.05, "store listing [est]"),
       ("flange diameter", fl, 1.0, "estimate"), ("hub diameter", hub, 1.0, "estimate"), ("total length", 16.0, 1.0, "estimate")],
      f"{TABLE}/timing_pulleys.csv", "Envelope (hub, flanges, length) is an estimate until the scouted listing is read.")
for slug, (dd, L) in {"rod-8x100": (8, 100), "rod-8x113": (8, 113), "rod-5x52": (5, 52)}.items():
    w(slug, f"{dd} mm ground steel rod, cut to {L} mm", "axis Z from z = 0", [("diameter", dd, 0.01, "h6 ground rod"),
      ("length", L, 0.5, "cut length from the CAD")], "design/v1/printed/layout.py")
w("collar-8mm", "8 mm set-screw shaft collar", "axis Z, centred", [("bore", 8, 0.05, "listing"), ("outer diameter", 16, 1, "estimate"),
  ("width", 8, 0.5, "estimate")], f"{TABLE}/couplings.csv")
w("flange-coupling-5mm", "5 mm rigid flange coupling (generic, Amazon)", "axis Z, flange face at z = 0, hub toward -Z, holes at 45/135/225/315 deg",
  [("bore", 5.0, 0.05, "listing"), ("flange diameter", 22.0, 0.5, "VXB / Handsontec listings"),
   ("flange thickness", 2.0, 0.5, "VXB sister listing"), ("hole circle radius", 8.0, 0.3, "WHEELTEC listing (16 mm PCD)"),
   ("hub diameter", 10.0, 1.0, "VXB listing"), ("hub length", 10.0, 1.0, "VXB listing")],
  "https://vxb.com/products/4-pack-5mm-rigid-flange-shaft-couplings-with-8-scr",
  "Generic part: measure the flange hole circle when it arrives; gripper-base holes are 3.6 so +-0.3 is tolerated.")
for slug, L in {"belt-j1-gt2-300": 300, "belt-s1-gt2-200": 200, "belt-s2-gt2-200": 200, "belt-j3-gt2-520": 520}.items():
    w(slug, f"GT2 6 mm closed belt {L} mm", "belt centre plane at z = 0 of its frame; sketched around the pulley tooth tips",
      [("pitch length", L, 0.5, "stock closed loop (timing_belt_closed_loops.csv)"), ("width", 6, 0.2, "standard"),
       ("thickness", 1.4, 0.1, "estimate")], f"{TABLE}/timing_belt_closed_loops.csv")
w("nema17-plug-keepout", "keep-out: 42SHDC plug and cable bend", "motor frame of nema17-42shdc.step",
  [("plug width", 18, 1, "estimate"), ("cable straight length", 18, 2, "estimate")], "estimate")
for L in (8, 10, 12, 30):
    w(f"m3x{L}-shcs", f"M3 x {L} ISO 4762 socket head cap screw", "head underside at z = 0, head +Z, shank -Z",
      [("head diameter", 5.5, 0.1, "standard"), ("head height", 3.0, 0.1, "standard"), ("length", L, 0.2, "standard"),
       ("shank (minor) diameter", 2.46, 0.05, "ISO 724 d1")], f"{TABLE}/fasteners_iso4762_shcs.csv")
w("m3-key-keepout", "keep-out: 2.5 mm hex key access", "screw frame; from the head top, 60 mm",
  [("diameter", 6.5, 0.5, "assembly skill (head 5.5 + 1)"), ("length", 60.0, 1, "assembly skill")], "estimate")
w("table-keepout", "keep-out: table top under the base", "z = 0 is the table surface, slab z -20..0, axis on the yaw axis",
  [("radius", 400.0, 1, "chosen > arm reach"), ("thickness", 20.0, 1, "chosen")], "estimate")
w("mg90s-keepout", "keep-out: MG90S cable exit", "mg90s.step frame (see mg90s.yaml)",
  [("length", 10.0, 1, "estimate"), ("width", 6.0, 1, "estimate"), ("height", 4.0, 1, "estimate")], "estimate")
print("ok")
