"""Attribution for RIGHT_HAND_FIRST_WEB_TOPOLOGY_CAUSAL_PROBE_R1 (read-only).

Two questions only:

  1. Where does the fold actually come from? For every first-web edge we compare the
     measured differential strain with the L1 distance between the two endpoint
     weight vectors. If the strain is produced by the weight field, the two must track
     each other.

  2. Reconcile the previous round's F110 disagreement (one report said "0 edges above 2x",
     another said "2"). We recompute F110 under both definitions side by side:
       * edge subset: first-web patch-local edges only  vs  the whole 6596-edge mesh
       * metric:      |D(deformed edge) - (rest edge)| / |rest edge|   (differential strain)
                      |deformed edge| / |rest edge|                    (length ratio)

No .blend is written, nothing is modified.
"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import *

FRAMES = [110, 127, 130, 160, 176, 205]
PATCH = PATCH_IDS
PSET = set(PATCH)


def main():
    before = protected_inputs()
    verify_inputs(before)
    ob, rig = open_frozen()

    faces = [tuple(p.vertices) for p in ob.data.polygons]
    all_edges = [(e.vertices[0], e.vertices[1]) for e in ob.data.edges]
    local_edges = [(a, b) for a, b in all_edges if a in PSET and b in PSET]
    groups = [g.name for g in ob.vertex_groups]
    gidx = {g.index: g.name for g in ob.vertex_groups}
    Wv = np.zeros((len(ob.data.vertices), len(groups)))
    for v in range(len(ob.data.vertices)):
        for g in ob.data.vertices[v].groups:
            Wv[v, groups.index(gidx[g.group])] = float(g.weight)

    neutral(rig)
    rest = coords(ob)

    LE = np.array(local_edges)
    wl1 = np.abs(Wv[LE[:, 0]] - Wv[LE[:, 1]]).sum(axis=1)

    def bone_pair(i, j):
        a = np.argsort(-Wv[i])[:2]
        b = np.argsort(-Wv[j])[:2]
        return (f'{groups[a[0]]}={Wv[i][a[0]]:.2f}/{groups[a[1]]}={Wv[i][a[1]]:.2f}',
                f'{groups[b[0]]}={Wv[j][b[0]]:.2f}/{groups[b[1]]}={Wv[j][b[1]]:.2f}')

    report = {'phase': PHASE, 'mode': 'READ_ONLY_ATTRIBUTION_AND_RECONCILIATION',
              'blend_files_written': 0, 'frames': [], 'f110_reconciliation': {}}

    for f in FRAMES:
        motion(rig, f)
        P = coords(ob)
        r = np.linalg.norm(rest[LE[:, 0]] - rest[LE[:, 1]], axis=1)
        d = np.linalg.norm(P[LE[:, 0]] - P[LE[:, 1]], axis=1)
        vrest = rest[LE[:, 0]] - rest[LE[:, 1]]
        vdef = P[LE[:, 0]] - P[LE[:, 1]]
        diff = np.linalg.norm(vdef - vrest, axis=1) / np.maximum(r, 1e-12)
        order = np.argsort(-diff)[:8]
        top = []
        for k in order:
            i, j = int(LE[k, 0]), int(LE[k, 1])
            ba, bb = bone_pair(i, j)
            top.append({'v_a': i, 'v_b': j, 'rest_mm': round(float(r[k]) * 1000, 4),
                        'deformed_mm': round(float(d[k]) * 1000, 4),
                        'length_ratio': round(float(d[k] / r[k]), 4),
                        'differential_strain': round(float(diff[k]), 4),
                        'weight_l1': round(float(wl1[k]), 4),
                        'dominant_a': ba, 'dominant_b': bb})
        ok = wl1 > 1e-9
        corr = float(np.corrcoef(diff[ok], wl1[ok])[0, 1]) if ok.sum() > 2 else 0.0
        report['frames'].append({
            'frame': f,
            'local_edges': len(local_edges),
            'max_differential_strain': round(float(diff.max()), 4),
            'max_length_ratio': round(float((d / r).max()), 4),
            'edges_above_2x_differential': int((diff > 2.0).sum()),
            'edges_above_2x_length_ratio': int((d / r > 2.0).sum()),
            'correlation_differential_strain_vs_weight_L1': round(corr, 4),
            'median_weight_L1_of_top8_edges': round(float(np.median(wl1[order])), 4),
            'median_weight_L1_all_edges': round(float(np.median(wl1)), 4),
            'top_edges': top})
        print('ATTR', f, 'corr', round(corr, 3), 'maxDiff', round(float(diff.max()), 3),
              'maxRatio', round(float((d / r).max()), 3), flush=True)

    # ---- F110 reconciliation, both definitions, both edge subsets
    rec = {}
    for f in [110]:
        motion(rig, f)
        P = coords(ob)
        def stats(edges, metric):
            E = np.array(edges)
            r = np.linalg.norm(rest[E[:, 0]] - rest[E[:, 1]], axis=1)
            vr = rest[E[:, 0]] - rest[E[:, 1]]
            vd = P[E[:, 0]] - P[E[:, 1]]
            d = np.linalg.norm(vd, axis=1)
            val = (np.linalg.norm(vd - vr, axis=1) / np.maximum(r, 1e-12)) if metric == 'differential_strain' \
                else (d / np.maximum(r, 1e-12))
            return {'edges': len(edges), 'metric': metric, 'max': round(float(val.max()), 4),
                    'above_2x': int((val > 2.0).sum()), 'above_4x': int((val > 4.0).sum())}
        rec = {
            'patch_local_edges_differential_strain': stats(local_edges, 'differential_strain'),
            'patch_local_edges_length_ratio': stats(local_edges, 'length_ratio'),
            'whole_mesh_differential_strain': stats(all_edges, 'differential_strain'),
            'whole_mesh_length_ratio': stats(all_edges, 'length_ratio')}
    report['f110_reconciliation'] = rec
    for k, v in rec.items():
        print('RECON F110', k, v, flush=True)

    neutral(rig)
    restore = float(np.linalg.norm(coords(ob) - rest, axis=1).max() * 1000)
    assert restore < 0.001
    verify_inputs(before)
    report['ZERO_restore_max_mm'] = restore
    report['frozen_baseline_sha256'] = sha(BASE)
    assert report['frozen_baseline_sha256'] == FROZEN_SHA
    dump('ATTRIBUTION_AND_RECONCILIATION_R1.json', report)
    print('ATTR_READY')


main()
