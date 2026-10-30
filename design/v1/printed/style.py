"""Design language for v1. Every printed part imports these; no local radii.

Soft, white body with orange drive parts: a friendly desktop tool where the moving drive
(printed pulleys, gripper fingers) reads at a glance against the structure.
"""
EDGE = "soft"          # fillets on vertical visible edges; bed edges get 45 deg chamfers
WALL = 3.0             # structural wall (load-bearing, rules §4 >= 2.0; 7-8 perimeters)
R_OUTER = 6.0          # main vertical corner radius of plates and housings (>= 1.5 x WALL)
R_INNER = R_OUTER - WALL
R_EDGE = 1.0           # touched edges
R_SMALL = 4.0          # small plates (gripper mount plate)
C_BED = 0.4            # elephant-foot chamfer on bed edges (rules §5)
REVEAL = 0.8           # gap between neighbouring prints (motor cover, pack cover)
STEP_MIN = 1.5
GRID = 0.5
DRIVE = "M3 hex"       # one drive: M3 socket head cap screws (2.5 mm key) throughout; M2 only on the servo tabs

COLOR_MAIN = "#E8E4DA"     # Bambu PLA Basic Jade White (approx.)
COLOR_ACCENT = "#F26B21"   # Bambu PLA Basic Orange (approx.)
COLOR_METAL = "#8C9096"
COLOR_STEEL = "#B8BCC2"
COLOR_BELT = "#222222"
COLOR_BOARD = "#1E5B3A"


def try_fillet(part, edges, r):
    """Fillet if OCC can, else return the part unchanged (looks never block a build)."""
    from build123d import fillet
    try:
        out = fillet(edges, r)
        return out if out.is_valid() else part
    except Exception:
        return part


def try_chamfer(part, edges, c):
    from build123d import chamfer
    try:
        out = chamfer(edges, c)
        return out if out.is_valid() else part
    except Exception:
        return part
