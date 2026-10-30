"""Standard bought parts for the arm, built from the engineering data tables.

Writes one STEP per part next to this file. Frames:
  bearings     axis Z, centred (z = -B/2 .. +B/2), origin on the axis
  pulleys      axis Z, z = 0 at the hub end face, hub toward -Z... (hub z 0..HUB_L, teeth above)
  rods         axis Z, z = 0 at one end
  collar       axis Z, centred
  hub          axis Z, z = 0 at the mounting face, body toward -Z (Pololu 1998)
Sources: bearings_deep_groove.csv (608, 625, 6806), timing_pulleys.csv (GT2 pitch and outside
diameters); hub/flange envelopes of the pulleys, coupling and collar are typical store-listing
values [est], recorded in each <slug>.yaml.
"""
from pathlib import Path

from build123d import *

HERE = Path(__file__).parent


def ring(od, idia, h, z0=0.0):
    with BuildPart() as p:
        with Locations((0, 0, z0)):
            Cylinder(od / 2, h, align=(Align.CENTER, Align.CENTER, Align.MIN))
            Cylinder(idia / 2, h, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
    return p.part


def bearing(d, D, B):
    return ring(D, d, B, -B / 2)


# bearings_deep_groove.csv: d x D x B
BEARINGS = {"bearing-608": (8, 22, 7), "bearing-625": (5, 16, 5), "bearing-6806": (30, 42, 7)}
for slug, (d, D, B) in BEARINGS.items():
    export_step(bearing(d, D, B), str(HERE / f"{slug}.step"))

# GT2 pulleys, 6 mm belt. timing_pulleys.csv: 20T OD 12.224, 60T OD 37.689.
# Envelope [est]: hub 7, flange 1, toothed band 7, flange 1 = 16 long; belt centre 11.5 above the hub end.
PULLEYS = {
    "gt2-20t-5mm": dict(od=12.224, flange=16.0, hub_d=16.0, bore=5.0),
    "gt2-60t-5mm": dict(od=37.689, flange=42.0, hub_d=20.0, bore=5.0),
}
HUB_L, FL, TEETH_W = 7.0, 1.0, 7.0
for slug, p in PULLEYS.items():
    with BuildPart() as pul:
        Cylinder(p["hub_d"] / 2, HUB_L, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations((0, 0, HUB_L)):
            Cylinder(p["flange"] / 2, FL, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations((0, 0, HUB_L + FL)):
            Cylinder(p["od"] / 2, TEETH_W, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations((0, 0, HUB_L + FL + TEETH_W)):
            Cylinder(p["flange"] / 2, FL, align=(Align.CENTER, Align.CENTER, Align.MIN))
        Cylinder(p["bore"] / 2, 2 * (HUB_L + 2 * FL + TEETH_W), mode=Mode.SUBTRACT)
    export_step(pul.part, str(HERE / f"{slug}.step"))

# Ground steel rods (cut to length): 8 mm shoulder/elbow shafts, 5 mm intermediate shaft
RODS = {"rod-8x100": (8.0, 100.0), "rod-8x113": (8.0, 113.0), "rod-5x52": (5.0, 52.0)}
for slug, (d, L) in RODS.items():
    with BuildPart() as r:
        Cylinder(d / 2, L, align=(Align.CENTER, Align.CENTER, Align.MIN))
    export_step(r.part, str(HERE / f"{slug}.step"))

# 8 mm set-screw shaft collar [est 16 OD x 8 wide]
export_step(ring(16.0, 8.0, 8.0, -4.0), str(HERE / "collar-8mm.step"))

# Generic 5 mm rigid flange coupling (Amazon "5mm rigid flange coupling", WHEELTEC/uxcell type) [est]:
# flange 22 x 2, hub 10 x 10, 4 x 3.2 holes on a 16 mm circle. z = 0 on the flange face, hub toward -Z.
with BuildPart() as fc:
    with Locations((0, 0, -2.0)):
        Cylinder(11.0, 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    with Locations((0, 0, -12.0)):
        Cylinder(5.0, 10.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    Cylinder(2.5, 40, mode=Mode.SUBTRACT)
    with PolarLocations(8.0, 4, start_angle=45):
        Cylinder(1.6, 10, mode=Mode.SUBTRACT)
export_step(fc.part, str(HERE / "flange-coupling-5mm.step"))

print("ok")
