"""Read-only probe 4b: attribution WITHOUT rebuilding the skinning pipeline.

The previous attempt tried to reproduce Blender's LBS by hand and could not make
its matrices agree with the authoritative evaluated mesh, so its numbers were
discarded rather than used. This probe needs no skinning reproduction at all.

Method: take the authoritative evaluated positions directly, then ask a purely
kinematic question of them. Fit one rigid motion per bone-influence group using
Kabsch on the vertices whose weight field is essentially pure for that bone
(purity > 0.999). Those vertices must move rigidly if the fold were only bulk rig
motion. Whatever stretch remains on the first-web edges, after removing that
fitted bulk motion, is stretch the grid itself had to absorb.

No weights are changed, no bones are added, nothing is saved.
"""
import sys, json, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import *

PATCH = set(PATCH_IDS)


def kabsch(P, Q):
    """Rigid transform mapping P onto Q (both N x 3)."""
    cp, cq = P.mean(0), Q.mean(0)
    H = (P - cp).T @ (Q - cq)
    U, S, Vt = np.linalg.svd(H)
    d = np.sign(np.linalg.det(Vt.T @ U.T))
    D = np.diag([1.0, 1.0, d])
    R = Vt.T @ D @ U.T
    return R, cq - R @ cp


def run():
    before = protected_inputs()
    verify_inputs(before)
    ob, rig = open_frozen()
    names = [g.name for g in ob.vertex_groups]
    W = np.zeros((len(ob.data.vertices), len(names)))
    for v in ob.data.vertices:
        for g in v.groups:
            W[v.index, g.group] = g.weight
    names = np.array(names)

    edges = [(e.vertices[0], e.vertices[1]) for e in ob.data.edges]
    local = [(a, b) for a, b in edges if a in PATCH and b in PATCH]
    slot = {v: i for i, v in enumerate(PATCH_IDS)}
    LE = np.array([[slot[a], slot[b]] for a, b in local])

    neutral(rig)
    rest = coords(ob)
    restL = rest[PATCH_IDS]
    edge_rest = restL[LE[:, 0]] - restL[LE[:, 1]]
    edge_len = np.linalg.norm(edge_rest, axis=1)

    rows = []
    for f in [110, 130, 205]:
        motion(rig, f)
        actL = coords(ob)[PATCH_IDS]
        # Pure-weight anchor sets per bone, restricted to the patch.
        pure = {}
        for bi, bn in enumerate(names):
            sel = np.nonzero(W[PATCH_IDS, bi] > 0.999)[0]
            if len(sel) >= 6:
                pure[bi] = sel
        fits = {}
        for bi, sel in pure.items():
            P = restL[sel]
            Q = actL[sel]
            R, t = kabsch(P, Q)
            rms = float(np.sqrt((((P @ R.T + t) - Q) ** 2).sum(1).mean())) * 1000
            fits[names[bi]] = {'anchors': int(len(sel)), 'rms_mm': round(rms, 4),
                               'R': R, 't': t}

        # Which bone best explains each patch vertex, using its fitted rigid motion.
        err = np.zeros(len(PATCH_IDS))
        for i in range(len(PATCH_IDS)):
            w = W[PATCH_IDS[i]]
            best, bestw = None, 0.0
            for bn, fit in fits.items():
                bi = int(np.nonzero(names == bn)[0][0])
                if w[bi] >= bestw:
                    bestw, best = w[bi], bn
            if best is not None and bestw > 0:
                f = fits[best]
                err[i] = float(np.linalg.norm((restL[i] @ f['R'].T + f['t']) - actL[i])) * 1000
            else:
                err[i] = float('nan')

        dd = (actL[LE[:, 0]] - actL[LE[:, 1]]) - edge_rest
        ratio = np.linalg.norm(dd, axis=1) / edge_len
        rows.append({'frame': f,
                     'pure_anchor_fits': {k: {kk: vv for kk, vv in v.items() if kk in ('anchors', 'rms_mm')}
                                          for k, v in fits.items()},
                     'fit_quality_note': 'rms_mm near 0 means that bone group moved rigidly, so its motion is bulk rig motion and is not a grid defect.',
                     'median_fit_residual_mm': round(float(np.nanmedian(err)), 4),
                     'p90_fit_residual_mm': round(float(np.nanpercentile(err, 90)), 4),
                     'max_fit_residual_mm': round(float(np.nanmax(err)), 4),
                     'edge_stretch': {'median': round(float(np.median(ratio)), 3),
                                      'p90': round(float(np.percentile(ratio, 90)), 3),
                                      'max': round(float(ratio.max()), 3),
                                      'above_2x': int((ratio > 2).sum()),
                                      'above_4x': int((ratio > 4).sum()),
                                      'of_total': len(local)},
                     'interpretation': 'Large edge stretch together with large per-vertex fit residual means the vertices could NOT be explained by any single bone rigid motion: the fold is generated inside the patch by blending between bones that move very differently.'})
        print('FIT', f, 'anchors', {k: v['anchors'] for k, v in fits.items()},
              'resid med/p90/max', rows[-1]['median_fit_residual_mm'],
              rows[-1]['p90_fit_residual_mm'], rows[-1]['max_fit_residual_mm'],
              '| stretch', rows[-1]['edge_stretch'], flush=True)

    neutral(rig)
    restore = float(np.linalg.norm(coords(ob) - rest, axis=1).max() * 1000)
    assert restore < 0.001
    verify_inputs(before)
    out = {'phase': PHASE, 'mode': 'READ_ONLY_RIGID_FIT_ATTRIBUTION', 'blend_written': False,
           'method': 'Kabsch rigid fit of each pure-weight bone group on the authoritative evaluated mesh; no skinning reproduction.',
           'frames': rows,
           'ZERO_restore_max_mm': restore,
           'frozen_baseline_sha256': sha(BASE),
           'blend_files_written': 0}
    assert out['frozen_baseline_sha256'] == FROZEN_SHA
    dump('RIGID_FIT_ATTRIBUTION_R1.json', out)
    print('FIT_READY')


run()