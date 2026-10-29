"""Read-only probe 3: is the fold caused by insufficient grid resolution, or by the
skin weight field splitting neighbouring vertices apart?

Both produce the same visible notch, but they need different rebuild levels:
  - resolution-limited  -> LEVEL 1 (deformation-oriented edge flow / density)
  - weight-field-limited-> weight authority problem (different fix)
  - single-bone-limited -> LEVEL 3 territory

For the worst F130 edges, reads the actual skin weights of both endpoints and asks
whether the two endpoints are driven by different bones with near-binary weights.
No painting, no tuning, no saving.
"""
import sys, json, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import *

PATCH = set(PATCH_IDS)


def run():
    before = protected_inputs()
    verify_inputs(before)
    ob, rig = open_frozen()
    edges = [(e.vertices[0], e.vertices[1]) for e in ob.data.edges]
    local = [(a, b) for a, b in edges if a in PATCH and b in PATCH]
    slot = {v: i for i, v in enumerate(PATCH_IDS)}
    LE = np.array([[slot[a], slot[b]] for a, b in local])

    neutral(rig)
    rest = coords(ob)
    restL = rest[PATCH_IDS]
    edge_rest = restL[LE[:, 0]] - restL[LE[:, 1]]
    edge_len = np.linalg.norm(edge_rest, axis=1)

    W = np.zeros((len(ob.data.vertices), len(ob.vertex_groups)))
    names = [g.name for g in ob.vertex_groups]
    for v in ob.data.vertices:
        for g in v.groups:
            W[v.index, g.group] = g.weight

    motion(rig, 130)
    P = coords(ob)
    PL = P[PATCH_IDS]
    dd = (PL[LE[:, 0]] - PL[LE[:, 1]]) - edge_rest
    ratio = np.linalg.norm(dd, axis=1) / edge_len
    order = np.argsort(ratio)[::-1]

    # Per-bone rigid motion, to separate "grid cannot carry it" from "weights differ".
    def bone_matrix(name):
        b = rig.pose.bones[name]
        M = rig.matrix_world @ b.matrix @ ob.matrix_world.inverted()
        return np.array(M)

    bones = sorted({names[i] for i in np.nonzero(W[PATCH_IDS].max(0))[0]})
    M = {b: bone_matrix(b) for b in bones}

    rows = []
    for i in order[:20]:
        a, b = int(local[i][0]), int(local[i][1])
        wa = {names[k]: round(float(W[a, k]), 4) for k in np.nonzero(W[a])[0] if W[a, k] > 1e-4}
        wb = {names[k]: round(float(W[b, k]), 4) for k in np.nonzero(W[b])[0] if W[b, k] > 1e-4}
        # dominant bone and whether the two ends disagree dominantly
        da = max(wa, key=wa.get) if wa else None
        db = max(wb, key=wb.get) if wb else None
        # weight-space distance
        wd = float(np.abs(W[a] - W[b]).sum())
        # If both endpoints were rigidly transformed by their own single dominant bone,
        # would the edge still stretch this much?
        pred_a = (M[da] @ np.append(rest[a], 1))[:3] if da else rest[a]
        pred_b = (M[db] @ np.append(rest[b], 1))[:3] if db else rest[b]
        pred_ratio = float(np.linalg.norm(pred_a - pred_b) / edge_len[i])
        rows.append({
            'edge': [a, b], 'rest_mm': round(float(edge_len[i]) * 1000, 3),
            'actual_differential_mm': round(float(np.linalg.norm(dd[i])) * 1000, 3),
            'actual_ratio': round(float(ratio[i]), 3),
            'weights_a': wa, 'weights_b': wb,
            'dominant_a': da, 'dominant_b': db,
            'same_dominant_bone': da == db,
            'weight_l1_distance': round(wd, 4),
            'ratio_if_each_end_followed_its_own_dominant_bone': round(pred_ratio, 3),
            'note': 'If the dominant-bone-only prediction already stretches this edge, the stretch comes from the rig driving the two ends apart. If it does not, blending and corrective contribute it.'})

    out = {'phase': PHASE, 'mode': 'READ_ONLY_WEIGHT_FIELD_DIAGNOSIS', 'blend_written': False,
           'frame': 130, 'time_seconds': 11.5 + 129 / 30.0,
           'patch_local_edges': len(local),
           'bones_driving_patch': bones,
           'worst_edges': rows,
           'aggregate': {
               'edges_above_2x': int((ratio > 2).sum()),
               'edges_above_4x': int((ratio > 4).sum()),
               'of_total': len(local),
               'worst20_same_dominant_bone': sum(1 for r in rows if r['same_dominant_bone']),
               'worst20_dominant_bone_only_also_stretches_gt_2x': sum(1 for r in rows if r['ratio_if_each_end_followed_its_own_dominant_bone'] > 2),
               'worst20_median_weight_l1': round(float(np.median([r['weight_l1_distance'] for r in rows])), 4)},
           'frozen_baseline_sha256': sha(BASE),
           'blend_files_written': 0}
    neutral(rig)
    restore = float(np.linalg.norm(coords(ob) - rest, axis=1).max() * 1000)
    assert restore < 0.001
    out['ZERO_restore_max_mm'] = restore
    verify_inputs(before)
    assert out['frozen_baseline_sha256'] == FROZEN_SHA
    dump('WEIGHT_FIELD_DIAGNOSIS_R1.json', out)
    for r in rows[:10]:
        print('W', r['edge'], 'ratio', r['actual_ratio'], '| dom', r['dominant_a'], '/', r['dominant_b'],
              '| same', r['same_dominant_bone'], '| wL1', r['weight_l1_distance'],
              '| dominant-only ratio', r['ratio_if_each_end_followed_its_own_dominant_bone'], flush=True)
    print('WEIGHT_FIELD_READY')


run()