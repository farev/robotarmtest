"""Arduino Uno R3 + CNC Shield V3 (Protoneer style) + 4x A4988 with stick-on heatsinks.

Frame: origin at the Uno PCB lower-left corner on the BOTTOM face of the Uno PCB
(z = 0 is the PCB underside, components toward +Z). X along the 68.58 mm edge,
Y along the 53.34 mm edge. The USB-B jack and DC barrel jack sit on the x = 0 edge
and overhang to negative x. Coordinates are the Arduino Eagle board coordinates
(UNO-TH_Rev3e.brd, official A000066 CAD zip), same origin and orientation.

Sources
  Uno PCB outline, 4 mounting holes (3.2 dia), header positions, USB-B and DC jack
  footprint positions: official Arduino UNO-TH_Rev3e.brd.
  Connector heights, header height, shield stack heights, shield driver / terminal
  positions, heatsink size: ESTIMATES (see uno-cnc-shield.yaml). Driver and terminal
  positions come from the open-source StaticBoards CNC shield KiCad layout (same
  Protoneer-derived arrangement, same Uno outline), not from a Protoneer drawing.
"""
from pathlib import Path

from build123d import *

HERE = Path(__file__).parent

# ---------------- Uno R3 (Eagle coordinates, mm) ----------------
UNO_L, UNO_W, UNO_T = 68.58, 53.34, 1.6
UNO_OUTLINE = [(0, 0), (66.04, 0), (66.04, 2.54), (68.58, 5.08), (68.58, 37.846),
               (66.04, 40.386), (66.04, 51.816), (64.516, 53.34), (0, 53.34)]
UNO_HOLES = [(13.97, 2.54), (15.24, 50.8), (66.04, 7.62), (66.04, 35.56)]
HOLE_D = 3.2

# female headers (centre x, y, number of pins)
HEADER_H = 8.5            # standard 2.54 mm female header height [est]
UNO_HEADERS = [(54.61, 50.8, 8), (30.226, 50.8, 10), (57.15, 2.54, 6), (36.83, 2.54, 8)]

# USB-B (X2, PN61729 footprint): outline x -6.34..9.41, y 32.2..44.0, centre y 38.1
USB_Y, USB_W, USB_H = 38.1, 12.0, 10.9       # width/height: USB-B receptacle standard [est]
USB_X0, USB_X1 = -6.34, 9.41                 # footprint outline
# DC barrel jack (X1, POWERSUPPLY_DC-21MM footprint): outline x -1.80..11.68, y 3.30..12.30
DC_Y, DC_W, DC_H = 7.798, 9.0, 11.0          # height: typical PJ-002A [est]
DC_X0, DC_X1 = -1.803, 11.684

# ---------------- CNC shield V3 + drivers ----------------
SHIELD_T = 1.6
SHIELD_Z0 = 12.6          # shield PCB underside above Uno PCB underside [est]:
                          # 1.6 (Uno PCB) + 8.5 (Uno socket) + 2.5 (shield male header plastic)
SOCKET_H = 8.5            # driver female socket [est]
DRV_PLASTIC = 2.5         # A4988 male header plastic [est]
DRV_W, DRV_L, DRV_T = 15.24, 20.32, 1.6     # Pololu A4988 module 0.6" x 0.8"
CHIP_H = 1.0
SINK = (9.0, 9.0, 5.0)    # common stick-on A4988 heatsink [est]
# driver module centres (x, y), long axis (20.32) along Y; from StaticBoards layout
DRIVERS = [(23.495, 36.195), (23.495, 15.875), (45.593, 36.195), (45.593, 15.875)]
# power terminal (VMOT, 2-pin 5.08 mm): pin centres at x = 7.366 and 12.446, y = 3.937
TERM_X, TERM_Y = 9.906, 3.937
TERM_W, TERM_D, TERM_H = 10.2, 7.6, 10.0    # wire entry faces -Y (the y = 0 edge)
TERM_YFRONT = 0.15

parts = []


def box(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, z0) * Box(x1 - x0, y1 - y0, z1 - z0,
                                                        align=(Align.CENTER, Align.CENTER, Align.MIN))


# Uno PCB
with BuildPart() as uno:
    with BuildSketch():
        Polygon(*UNO_OUTLINE, align=None)
    extrude(amount=UNO_T)
    fillet([e for e in uno.edges().filter_by(Axis.Z)
            if any(abs(e.center().X - x) < 1e-3 and abs(e.center().Y - y) < 1e-3
                   for x, y in [(0, 0), (0, UNO_W), (66.04, 0)])], radius=1.0)
    with Locations(*UNO_HOLES):
        Hole(HOLE_D / 2)
parts.append(uno.part)

# Uno female headers
for cx, cy, n in UNO_HEADERS:
    half = n * 2.54 / 2
    parts.append(box(cx - half, cx + half, cy - 1.27, cy + 1.27, UNO_T, UNO_T + HEADER_H))

# USB-B and DC jack (overhang beyond x = 0)
parts.append(box(USB_X0, USB_X1, USB_Y - USB_W / 2, USB_Y + USB_W / 2, UNO_T, UNO_T + USB_H))
parts.append(box(DC_X0, DC_X1, DC_Y - DC_W / 2, DC_Y + DC_W / 2, UNO_T, UNO_T + DC_H))

# shield male-header plastic between Uno sockets and shield PCB
for cx, cy, n in UNO_HEADERS:
    half = n * 2.54 / 2
    parts.append(box(cx - half, cx + half, cy - 1.27, cy + 1.27, UNO_T + HEADER_H, SHIELD_Z0))

# shield PCB (same outline as the Uno, no mounting holes of its own modelled)
with BuildPart() as shield:
    with BuildSketch(Plane.XY.offset(SHIELD_Z0)):
        Polygon(*UNO_OUTLINE, align=None)
    extrude(amount=SHIELD_T)
parts.append(shield.part)
SHIELD_TOP = SHIELD_Z0 + SHIELD_T

# power terminal block
parts.append(box(TERM_X - TERM_W / 2, TERM_X + TERM_W / 2, TERM_YFRONT, TERM_YFRONT + TERM_D,
                 SHIELD_TOP, SHIELD_TOP + TERM_H))

# 4 drivers: sockets, module PCB, chip, heatsink
mod_z0 = SHIELD_TOP + SOCKET_H + DRV_PLASTIC
for cx, cy in DRIVERS:
    for dx in (-6.35, 6.35):
        parts.append(box(cx + dx - 1.27, cx + dx + 1.27, cy - DRV_L / 2, cy + DRV_L / 2,
                         SHIELD_TOP, mod_z0))
    parts.append(box(cx - DRV_W / 2, cx + DRV_W / 2, cy - DRV_L / 2, cy + DRV_L / 2,
                     mod_z0, mod_z0 + DRV_T))
    top = mod_z0 + DRV_T
    parts.append(box(cx - 2.5, cx + 2.5, cy - 2.5, cy + 2.5, top, top + CHIP_H))
    top += CHIP_H
    parts.append(box(cx - SINK[0] / 2, cx + SINK[0] / 2, cy - SINK[1] / 2, cy + SINK[1] / 2,
                     top, top + SINK[2]))

assembly = Compound(children=parts, label="uno-cnc-shield")
export_step(assembly, str(HERE / "uno-cnc-shield.step"))
bb = assembly.bounding_box()
print("bbox", bb.min, bb.max)
