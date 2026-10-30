"""Turret hub (rotates with J1): spigot through the two 6806 inner rings, the printed GT2 120T
J1 pulley, and the turret plate that carries the shoulder tower.
Printed upside down (plate top on the bed, spigot up); as-assembled frame = turret frame
(world at q1 = 0)."""
import math
from pathlib import Path

from build123d import *

from features import export_printed, gt2_band, hull_sketch, circle_pts, rect_pts
from layout import *
from style import *

HERE = Path(__file__).parent
STEP_D = 33.0                         # bears on the upper 6806 inner ring only (inner ring OD ~33.5 [est])
SPIGOT_BOT = Z_B_LO_BOT + 0.5         # 0.5 short of the lower ring face so the clamp washer bites
SPIGOT_SCREW_R = 10.5                 # 3 x M3 inserts in the spigot end (walls 2.4 / 2.5, rules §3)
CABLE_D = 12.0
NECK_D = od(T_YAW_BIG) + 2 * FLANGE_T  # neck as wide as the flange: no overhang when printed inverted
FOOT_X, FOOT_Y, FOOT_INSERTS = TOWER_FOOT_X, TOWER_FOOT_Y, TOWER_FOOT_INSERTS   # layout.py, shared with the tower

with BuildPart() as hub:
    # spigot + step
    with Locations((0, 0, SPIGOT_BOT)):
        Cylinder(SPIGOT / 2, Z_B_UP_TOP - SPIGOT_BOT, align=(Align.CENTER, Align.CENTER, Align.MIN))
    with Locations((0, 0, Z_B_UP_TOP)):
        Cylinder(STEP_D / 2, Z_TUR_BOT - Z_B_UP_TOP, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # J1 120T band; its bottom flange is above the teeth in the print, so it is a cone
    add(gt2_band(T_YAW_BIG, bottom_cone=True).moved(Location((0, 0, Z_TUR_BOT))))
    z_band_top = Z_TUR_BOT + TEETH_W + 2 * FLANGE_T
    with Locations((0, 0, z_band_top)):
        Cylinder(NECK_D / 2, Z_TUR_PLATE - z_band_top, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # plate: round centre + arm out to the tower foot
    pts = circle_pts(0, 0, NECK_D / 2 + 4) + rect_pts(0, (FOOT_Y[0] + FOOT_Y[1]) / 2, 50, (FOOT_Y[1] - FOOT_Y[0]) / 2 + 5)
    with BuildSketch(Plane.XY.offset(Z_TUR_PLATE)):
        add(hull_sketch(pts))
    extrude(amount=TUR_PLATE_T)
    # cable bore through everything
    Cylinder(CABLE_D / 2, 500, mode=Mode.SUBTRACT)
    # spigot inserts (opening down)
    with Locations(*[(SPIGOT_SCREW_R * math.cos(math.radians(a)), SPIGOT_SCREW_R * math.sin(math.radians(a)), SPIGOT_BOT)
                     for a in (90, 210, 330)]):
        Cylinder(M3_INSERT[0] / 2, M3_INSERT[1], align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
    # tower-foot inserts from the plate top
    with Locations(*[(x, y, Z_TUR_TOP) for x, y in FOOT_INSERTS]):
        Hole(M3_INSERT[0] / 2, M3_INSERT[1])

part = hub.part
part = try_fillet(part, part.edges().filter_by(Axis.Z).filter_by(lambda e: e.center().Z > Z_TUR_PLATE), R_OUTER)
export_printed(part, "turret-hub", rot=(180, 0, 0), here=HERE)
