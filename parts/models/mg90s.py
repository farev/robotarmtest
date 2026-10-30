"""TowerPro MG90S micro servo (metal gear) - build123d generator.

Run: python parts/models/mg90s.py
Writes parts/models/mg90s.step (servo) and parts/models/mg90s-keepout.step (cable exit block).

Frame: origin on the output shaft axis at the TOP face of the mounting tabs.
  +Z = output shaft direction, long axis = X, shaft end of the body toward +X,
  body centre at negative X (x = -(body_length/2 - shaft_offset)), tabs along X.

Sources (see mg90s.yaml for details):
  TowerPro product page table (towerpro.com.tw/product/mg90s-3/): A 32.5 total height to spline top,
  B 22.8 body length, C 28.4 height to gear-boss top, D 12.4 width, E 32.1 tab span, F 18.5 tab underside.
  Tab hole pitch/diameter, tab thickness, case top, shaft offset: not on the TowerPro page; taken from
  the Hitec HS-5055MG drawing (same 9g footprint) and the Kuman MG90S OpenSCAD model (christophevg/3d-servo-model).
"""
import os

from build123d import Box, Cylinder, Pos, export_step

HERE = os.path.dirname(os.path.abspath(__file__))

# --- dimensions (mm) ---
BODY_L = 22.8          # B
BODY_W = 12.4          # D
TAB_SPAN = 32.5        # E = 32.1 on the TowerPro page; 32.2..32.7 in other sources -> modelled at the upper end
TAB_PITCH = 28.5       # hole centre to hole centre (Hitec drawing 28.5, Kuman model 28.6)
TAB_HOLE_D = 2.0
TAB_T = 2.5
TAB_UNDERSIDE = 18.5   # F: bottom of body to underside of tab
TAB_TOP = TAB_UNDERSIDE + TAB_T      # 21.0 above body bottom
CASE_TOP = 22.5        # body bottom to case top (Kuman model 22.5)
BUMP_TOP = 28.4        # C: bottom to top of gear boss
SPLINE_TOP = 32.5      # A: bottom to top of spline
SHAFT_OFFSET = 6.2     # shaft axis to near (+X) body end
SPLINE_D = 4.8
BOSS_D = 12.0          # round gear boss around the output
BOSS2_D = 6.0          # second (idler) boss
BOSS2_X = -6.4         # centre of second boss relative to the shaft axis

# --- frame: z = 0 at tab top face ---
z_bot = -TAB_TOP
z_case = CASE_TOP - TAB_TOP
z_bump = BUMP_TOP - TAB_TOP
z_spl = SPLINE_TOP - TAB_TOP
x_end = SHAFT_OFFSET                 # +X body end
x_far = SHAFT_OFFSET - BODY_L        # -X body end
x_c = (x_end + x_far) / 2            # body centre (negative)


def box(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


def cyl(x, r, z0, z1):
    return Pos(x, 0, (z0 + z1) / 2) * Cylinder(r, z1 - z0)


body = box(x_far, x_end, -BODY_W / 2, BODY_W / 2, z_bot, z_case)

tabs = box(x_c - TAB_SPAN / 2, x_c + TAB_SPAN / 2, -BODY_W / 2, BODY_W / 2, -TAB_T, 0)
servo = body + tabs
for sx in (-1, 1):
    servo = servo - cyl(x_c + sx * TAB_PITCH / 2, TAB_HOLE_D / 2, -TAB_T - 1, 1)

# gear-top bump: big round boss over the shaft + second boss + bridge between them
boss = cyl(0, BOSS_D / 2, z_case - 0.5, z_bump)
boss2 = cyl(BOSS2_X, BOSS2_D / 2, z_case - 0.5, z_bump)
bridge = box(BOSS2_X, 0, -BOSS2_D / 2, BOSS2_D / 2, z_case - 0.5, z_bump)
servo = servo + boss + boss2 + bridge

# output spline (outer diameter modelled as a plain cylinder)
servo = servo + cyl(0, SPLINE_D / 2, z_bump - 0.5, z_spl)

export_step(servo, os.path.join(HERE, "mg90s.step"))

# cable exit keep-out: leaves the +X (shaft) end face at the bottom, centred in Y (TowerPro drawing).
# Block = 6 wide, 4 tall, 10 long (flat 3-wire lead plus room for the first bend). Position is estimated.
cable = box(x_end, x_end + 10.0, -3.0, 3.0, z_bot, z_bot + 4.0)
export_step(cable, os.path.join(HERE, "mg90s-keepout.step"))

print("body x", x_far, x_end, "centre", x_c, "z", z_bot, z_case, z_bump, z_spl)
