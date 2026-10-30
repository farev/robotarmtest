"""Intermediate-shaft carriage: holds the J2 drive's 5 mm intermediate shaft on 2 x 625 inside the motor
pack. It slides perpendicular to the stage-1 belt (CARR_DIR, rear-down) so moving it tensions stage 2 only.
Clamped to the pack's -Y wall by 2 x M3 x 12 put in from inside the pack (heads in counterbores on its +Y
face) into captive nuts in slots on the wall's outer face: no key reaches under the 60T.
Print in PETG (it sits beside both motor bodies). Printed -Y face down; UA frame as assembled."""
import math
from pathlib import Path

from build123d import *

from features import export_printed, bed_bearing_pocket
from layout import *
from style import *

HERE = Path(__file__).parent
CL, CH, CT = 35.0, 25.0, 16.0          # length (x), height (z), thickness (y); CH gives 4.45 walls round the 625s
CARR_CBORE = CT + WALL_T + 0.3 - 12.0  # head seat so the M3 x 12 tip stands 0.3 past the wall face, 0.6 past the
                                       # nut (rules §2: >= 1 pitch), still 0.7 short of the 60T hub (8.3 deep)
X0, Z0 = INT_XZ
Y0 = Y_PACK_IN
SCREWS = [(X0 + s * CARR_SCREW_DX * CARR_DIR[0], Z0 + s * CARR_SCREW_DX * CARR_DIR[1]) for s in (-1, 1)]
CORNER_CHAMFER = 3.0                   # rear-bottom corner clears the sloping rear wall; 2.3 wall to the screw counterbore

with BuildSketch(mode=Mode.PRIVATE) as outline:          # XZ outline in sketch coordinates (u = x, v = z)
    with Locations((X0, Z0)):
        Rectangle(CL, CH)
    chamfer(outline.vertices().sort_by(Axis.X)[:2].sort_by(Axis.Y)[:1], CORNER_CHAMFER)

with BuildPart() as carr:
    with BuildSketch(Plane(origin=(0, Y0 + CT, 0), x_dir=(1, 0, 0), z_dir=(0, -1, 0))) as sk:   # u -> x, v -> z
        add(outline.sketch)
    extrude(sk.sketch, amount=CT)                         # toward -Y, down to the wall face
    # 625 press pockets at both faces (rules §1 +0.1); bed-side one with ledge + cone
    add(bed_bearing_pocket(FIT_625, W625, 13.0, 5.6).rotate(Axis.X, -90).moved(Location((X0, Y0, Z0))), mode=Mode.SUBTRACT)
    with Locations(Location((X0, Y0 + CT - W625, Z0), (-90, 0, 0))):
        Cylinder(FIT_625 / 2, W625 + 1, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
    # clamp screws: clearance through, counterbore on the +Y face (opens upward as printed, rules §2)
    with Locations(*[Location((x, Y0 + CT, z), (-90, 0, 0)) for x, z in SCREWS]):   # hole runs -Y
        CounterBoreHole(M3_CLEAR / 2, M3_CBORE[0] / 2, CARR_CBORE)

part = carr.part
part = try_fillet(part, part.edges().filter_by(Axis.Y).filter_by(lambda e: e.length > CT - 0.1), R_INNER - 1.0)
export_printed(part, "pack-carriage", rot=(90, 0, 0), here=HERE)
