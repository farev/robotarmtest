"""The ftobler servo gripper of the 20sffactory Community Robot Arm (CC BY 4.0), MG90S version.

Five printed parts and one servo: base, two sliding fingers, the drive disc that moves them and
the screw retainer. The vendor STEP assembly carries the 28BYJ version of this gripper (same
fingers, a stepper base and a deeper drive disc), so: keep its two fingers where they are, put
the servo print files (servo_gripperBase.stl, servo_gripper_shaft.stl) in the place of the
stepper base and disc, each turned to the axis-aligned orientation that overlaps the old part
best, and drop an MG90S through the base's servo slot (tabs on the top face, output down, coaxial
with the drive disc). The base keeps the vendor's three M3 holes into the manipulator.

All meshes are hand-local, metres in and out (like the arm.glb node meshes)."""
from pathlib import Path
import math
import numpy as np
from scipy import ndimage
from mechy.cad import ref_arm as RA
from mechy.sim import voxel

HERE = Path(__file__).resolve().parent
STL = RA.DATA_DIR / 'stl'
PRINT = {'gripper-base': 'servo_gripperBase.stl', 'gripper-finger': 'gripperFinger_by_ftobler.stl',
         'gripper-drive-disc': 'servo_gripper_shaft.stl', 'gripper-screw-retainer': 'gripper_screw_secure.stl'}
MG90S = {'body': (22.8, 12.2, 22.7), 'tabs': (32.2, 12.2, 2.5), 'tab_from_output': 4.3,
         'gear_d': 11.8, 'gear_h': 4.0, 'shaft_from_end': 5.9}            # mm, TowerPro datasheet
PRINTED, SERVO = '#9971b2', '#1c1c1e'


def _rgba(h):
    return tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)) + (1.0,)


def _yaw(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])


def _fit(src_v, src_t, tgt_v, tgt_t, h=1.0):
    """src turned (8 axis-aligned orientations keeping its thin side vertical) and centred on tgt's
    box; the orientation with the best voxel overlap. Returns (v, IoU)."""
    tgt = voxel.voxelize(tgt_v[tgt_t], h, keep_largest=False)
    c = (tgt_v.min(0) + tgt_v.max(0)) / 2
    best = None
    for k in range(4):
        for flip in (False, True):
            R = _yaw(k * math.pi / 2) @ (np.diag([1.0, -1.0, -1.0]) if flip else np.eye(3))
            v = src_v @ R.T
            v = v - (v.min(0) + v.max(0)) / 2 + c
            votes = sum(voxel._parity_axis(v[src_t], tgt.origin, h, tgt.shape, a).astype(np.int8) for a in range(3))
            m = votes >= 2
            iou = (m & tgt.solid).sum() / max((m | tgt.solid).sum(), 1)
            if best is None or iou > best[1]:
                best = (v, float(iou))
    return best


def _boxes(boxes):
    v, t = [], []
    for (x0, y0, z0), (x1, y1, z1) in boxes:
        i = len(v)
        v += [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
        t += [(i + a, i + b, i + c) for a, b, c in [(0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7), (0, 1, 5), (0, 5, 4),
                                                    (1, 2, 6), (1, 6, 5), (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)]]
    return np.array(v, float), np.array(t, np.int64)


def _cyl(cx, cy, z0, z1, r, n=32):
    a = np.linspace(0, 2 * math.pi, n, endpoint=False)
    ring = np.c_[cx + r * np.cos(a), cy + r * np.sin(a)]
    v = np.vstack([np.c_[ring, np.full(n, z0)], np.c_[ring, np.full(n, z1)], [[cx, cy, z0], [cx, cy, z1]]])
    t = []
    for i in range(n):
        j = (i + 1) % n
        t += [(i, j, n + j), (i, n + j, n + i), (2 * n, j, i), (2 * n + 1, n + i, n + j)]
    return v, np.array(t, np.int64)


def _which(m):
    """Role of a legacy hand mesh by its size (mm)."""
    ext = np.sort(np.ptp(m['v'] * 1000, axis=0))
    if np.allclose(ext, [24.6, 25.0, 30.0], atol=1.0):
        return 'finger'
    if np.allclose(ext, [10.0, 50.0, 60.0], atol=1.0):
        return 'base'
    if np.allclose(ext[1:], [20.0, 20.0], atol=1.0) and ext[0] < 9:
        return 'disc'
    if ext[2] > 28:
        return 'stepper'
    return 'other'


def build(legacy):
    """legacy: the vendor gripper meshes from the reference arm (dicts name, v m, t, hand-local).
    Returns (meshes, details); meshes carry name, node, v (m), t, rgba, kind, mass_kg, printed_ref."""
    roles = {}
    for m in legacy:
        roles.setdefault(_which(m), []).append(m)
    assert len(roles.get('finger', [])) == 2 and roles.get('base') and roles.get('disc'), \
        {k: [m['name'] for m in v] for k, v in roles.items()}
    base_o, disc_o = roles['base'][0], roles['disc'][0]
    out = []

    def add(name, v_mm, t, color, kind, mass=None, printed=None):
        out.append(dict(name=name, node='hand', v=np.asarray(v_mm, float) / 1000, t=np.asarray(t, np.int64),
                        rgba=_rgba(color), kind=kind, mass_kg=mass, printed_ref=printed))

    for side, f in zip(('left', 'right'), sorted(roles['finger'], key=lambda m: m['v'][:, 1].mean())):
        add(f'gripper-finger-{side}', f['v'] * 1000, f['t'], PRINTED, 'printed', printed='gripper-finger')
    bv, bt = RA.read_stl(STL / PRINT['gripper-base'])
    base_v, base_iou = _fit(bv, bt, base_o['v'] * 1000, base_o['t'])
    add('gripper-base', base_v, bt, PRINTED, 'printed', printed='gripper-base')
    dv, dt = RA.read_stl(STL / PRINT['gripper-drive-disc'])
    disc_v, disc_iou = _fit(dv, dt, disc_o['v'] * 1000, disc_o['t'], h=0.5)
    # the servo disc is thinner than the stepper one: keep its servo-side face where the old one was
    top_old = (disc_o['v'][:, 2] * 1000).max()
    disc_v[:, 2] += top_old - disc_v[:, 2].max()
    add('gripper-drive-disc', disc_v, dt, PRINTED, 'printed', printed='gripper-drive-disc')
    dc = (disc_v.min(0) + disc_v.max(0)) / 2
    sv, st = RA.read_stl(STL / PRINT['gripper-screw-retainer'])
    sv = sv - (sv.min(0) + sv.max(0)) / 2
    sv[:, :2] += dc[:2]
    sv[:, 2] += disc_v[:, 2].min() - sv[:, 2].max()              # under the disc, on the horn screw
    add('gripper-screw-retainer', sv, st, PRINTED, 'printed', printed='gripper-screw-retainer')

    # MG90S through the base's servo slot (the biggest enclosed hole seen from above)
    g = voxel.voxelize(base_v[bt], 0.5, keep_largest=False)
    foot = g.solid.any(axis=2)
    lab, n = ndimage.label(ndimage.binary_fill_holes(foot) & ~foot)
    k = np.bincount(lab.ravel())[1:].argmax() + 1
    ij = np.argwhere(lab == k)
    lo, hi = g.origin[:2] + ij.min(0) * 0.5, g.origin[:2] + (ij.max(0) + 1) * 0.5
    along_x = (hi - lo)[0] >= (hi - lo)[1]
    top = float(base_v[:, 2].max())
    L, W, H = MG90S['body']
    z0 = top - MG90S['tab_from_output']                    # output face, pointing down at the disc
    d = L / 2 - MG90S['shaft_from_end']
    # body placed so its output shaft is on the drive disc's axis, long side along the slot
    ux = np.array([1.0, 0.0]) if along_x else np.array([0.0, 1.0])
    slot_c = (lo + hi) / 2
    sgn = 1.0 if (dc[:2] - slot_c) @ ux >= 0 else -1.0
    bc = dc[:2] - sgn * d * ux
    hx, hy = (L / 2, W / 2) if along_x else (W / 2, L / 2)
    tx, ty = (MG90S['tabs'][0] / 2, W / 2) if along_x else (W / 2, MG90S['tabs'][0] / 2)
    v1, t1 = _boxes([((bc[0] - hx, bc[1] - hy, z0), (bc[0] + hx, bc[1] + hy, z0 + H)),
                     ((bc[0] - tx, bc[1] - ty, top), (bc[0] + tx, bc[1] + ty, top + MG90S['tabs'][2]))])
    v2, t2 = _cyl(dc[0], dc[1], z0 - MG90S['gear_h'], z0, MG90S['gear_d'] / 2)
    add('gripper-mg90s', np.vstack([v1, v2]), np.vstack([t1, t2 + len(v1)]), SERVO, 'motor',
        mass=RA.CATALOG_MASS['servo'])
    details = dict(design='ftobler servo gripper, 20sffactory Community Robot Arm (CC BY 4.0)',
                   printed=list(PRINT.values()), base_fit_iou=round(base_iou, 3), disc_fit_iou=round(disc_iou, 3),
                   servo_axis_offset_mm=round(float(np.linalg.norm(bc - slot_c)), 2),
                   replaced=[m['name'] for m in legacy if _which(m) in ('base', 'disc', 'stepper', 'other')],
                   note='servo body is a datasheet envelope; horn fit to the disc unverified')
    return out, details
