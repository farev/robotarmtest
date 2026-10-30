"""Fixed GT2 80T shoulder pulley: bolted to the tower's +Y face (4 x M3 x 12 from the tower's
outer face into inserts in the spacer disc face; 6.5 mm of tower clamped, 5.5 engaged), coaxial with the dead shoulder shaft. The J2 motor pack's stage-2
20T pulley walks around it. The boss on its +Y face is the axial stop for the shaft collar.
Printed mating face down; as assembled in the turret frame."""
import math
from pathlib import Path

from build123d import *

from features import export_printed, gt2_band
from layout import *
from style import *

HERE = Path(__file__).parent
PUL_SCREW_R = 18.0                 # matches shoulder-tower
PUL_SCREW_ANG = [45, 135, 225, 315]
BOSS_D = 14.0
COLLAR_W = 8.0
SHIM_T = 1.2
Y_COLLAR_OUT = Y_PACK_OUT - SHIM_T - COLLAR_W     # collar outer face (toward the tower)
BOSS_L = Y_COLLAR_OUT - Y_FIX_PUL[1]

SPACER_D = 2 * (od(T_S2_BIG) / 2 + 0.9 * FLANGE_T)   # as wide as the band's flange (no overhang on the bed side);
                                                      # r 26.4, inside the stage-2 20T's orbit (r >= 38)

with BuildPart(mode=Mode.PRIVATE) as local:          # local frame: axis Z, z = 0 on the tower face
    Cylinder(SPACER_D / 2, FIX_PUL_SPACER, align=(Align.CENTER, Align.CENTER, Align.MIN))   # spacer disc
    add(gt2_band(T_S2_BIG).moved(Location((0, 0, FIX_PUL_SPACER))))
    with Locations((0, 0, FIX_PUL_SPACER + BAND_W)):
        Cylinder(BOSS_D / 2, BOSS_L, align=(Align.CENTER, Align.CENTER, Align.MIN))
    Cylinder(ROD8_CLAMP / 2, 200, mode=Mode.SUBTRACT)
    with Locations(*[(PUL_SCREW_R * math.cos(math.radians(a)), PUL_SCREW_R * math.sin(math.radians(a)), 0) for a in PUL_SCREW_ANG]):
        Cylinder(M3_INSERT[0] / 2, M3_INSERT[1], align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

part = local.part.rotate(Axis.X, -90).moved(Location((0, Y_TOWER[1], Z_SH)))   # local +Z -> +Y, on the tower face
export_printed(part, "shoulder-pulley-80t", rot=(90, 0, 0), here=HERE)
print("boss length", round(BOSS_L, 2))
