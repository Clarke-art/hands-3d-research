"""Read-only probe 2: why the notch is VISIBLE.

Large absolute displacement is not itself a defect — a rigid region can move far
without folding. What produces a visible crease is differential displacement
across a quad: neighbouring vertices separating by a large fraction of their own
edge length, while the quad grid has no line along which that motion can travel.

Measures, at the six product frames:
  - per-edge differential displacement vs that edge's own rest length
  - the same quantity resolved along each grid axis (shear vs stretch)
  - how the worst edges line up with the previously recorded visible fold bands
  - approved corrective value, to separate mesh-limited folding from driver action

No hidden-crossing census, no normal-dot, no intersection tests, no vertex census.
"""
import sys, json, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import *

FRAMES = [110, 127, 130, 160, 176, 205]
PATCH = set(PATCH_IDS)
# Fold bands already identified by ordinary visible F130 inspection in an earlier approved round.
FOLD_BANDS = json.loads((ROOT / 'audits/first_web_deformation_architecture_rebuild_assessment_r1/'
                         'CURRENT_FIRST_WEB_TOPOLOGY_AUDIT_R1.json').read_text(encoding='utf-8-sig'))['visible_fold_edge_examples']


def run():
    before = protected_inputs()
    verify_inputs(before)
    ob, rig = open_frozen()
    edges = [(e.vertices[0], e.vertices[1]) for e in ob.data.edges]
    slot = {v: i for i, v in enumerate(PATCH_IDS)}
    local = [(a, b) for a, b in edges if a in PATCH and b in PATCH]
    LE = np.array([[slot[a], slot[b]] for a, b in local])
    GV = np.array([[a, b] for a, b in local])
    F_local = [f for f in (tuple(p.vertices) for p in ob.data.polygons) if all(v in PATCH for v in f)]

    neutral(rig)
    rest = coords(ob)
    restL = rest[PATCH_IDS]
    edge_rest = restL[LE[:, 0]] - restL[LE[:, 1]]
    edge_rest_len = np.linalg.norm(edge_rest, axis=1)

    diag = json.loads((OUT / 'STRUCTURAL_DIAGNOSIS_R1.json').read_text(encoding='utf-8-sig'))
    e0 = np.array(diag['grid_axes']['e0'])
    e1 = np.array(diag['grid_axes']['e1'])
    # Which grid axis does each local edge belong to?
    ed = edge_rest / edge_rest_len[:, None]
    a0 = np.abs(ed @ e0)
    a1 = np.abs(ed @ e1)
    axis_of = np.where(a0 >= a1, 0, 1)

    out = {'phase': PHASE, 'mode': 'READ_ONLY_VISIBLE_CREASE_DIAGNOSIS', 'blend_written': False,
           'patch_local_edges': len(local), 'patch_quads': len(F_local),
           'rest_edge_len_mm': {'median': float(np.median(edge_rest_len) * 1000),
                                'min': float(edge_rest_len.min() * 1000),
                                'max': float(edge_rest_len.max() * 1000)},
           'axis_edge_counts': {'axis0': int((axis_of == 0).sum()), 'axis1': int((axis_of == 1).sum())},
           'frames': []}

    for f in FRAMES:
        motion(rig, f)
        P = coords(ob)
        PL = P[PATCH_IDS]
        # differential displacement across each edge
        dd = (PL[LE[:, 0]] - PL[LE[:, 1]]) - edge_rest
        dd_len = np.linalg.norm(dd, axis=1)
        ratio = dd_len / edge_rest_len
        # shear vs stretch: component of the differential across each grid axis
        comp0 = np.abs(dd @ e0)
        comp1 = np.abs(dd @ e1)
        # worst offenders
        order = np.argsort(ratio)[::-1][:14]
        worst = [{'edge': [int(GV[i][0]), int(GV[i][1])],
                  'grid_axis': 'axis0' if axis_of[i] == 0 else 'axis1',
                  'rest_mm': round(float(edge_rest_len[i]) * 1000, 3),
                  'differential_mm': round(float(dd_len[i]) * 1000, 3),
                  'ratio': round(float(ratio[i]), 3)} for i in order]
        fold_hit = sorted({int(e) for pair in FOLD_BANDS for e in pair})
        fold_rows = []
        for a, b in FOLD_BANDS:
            ia = [k for k, (x, y) in enumerate(local) if {x, y} == {a, b}]
            if ia:
                i = ia[0]
                fold_rows.append({'edge': [a, b], 'rest_mm': round(float(edge_rest_len[i]) * 1000, 3),
                                  'differential_mm': round(float(dd_len[i]) * 1000, 3),
                                  'ratio': round(float(ratio[i]), 3),
                                  'grid_axis': 'axis0' if axis_of[i] == 0 else 'axis1'})
        out['frames'].append({
            'frame': f, 'source_frame': 690 + 2 * (f - 1), 'time_seconds': 11.5 + (f - 1) / 30.0,
            'approved_corrective_natural_values': values(ob),
            'differential_vs_rest_length': {
                'median': round(float(np.median(ratio)), 3),
                'p75': round(float(np.percentile(ratio, 75)), 3),
                'p90': round(float(np.percentile(ratio, 90)), 3),
                'p95': round(float(np.percentile(ratio, 95)), 3),
                'max': round(float(ratio.max()), 3),
                'edges_above_1x': int((ratio > 1).sum()),
                'edges_above_2x': int((ratio > 2).sum()),
                'edges_above_4x': int((ratio > 4).sum()),
                'of_total_local_edges': len(local),
                'note': 'Differential displacement between the two endpoints of an edge, divided by that edge own rest length. Above 1 the edge endpoints have separated by more than the edge was long.'},
            'resolved_along_grid_axes': {
                'median_abs_differential_along_axis0_mm': round(float(np.median(comp0)) * 1000, 3),
                'median_abs_differential_along_axis1_mm': round(float(np.median(comp1)) * 1000, 3),
                'max_abs_differential_along_axis0_mm': round(float(comp0.max()) * 1000, 3),
                'max_abs_differential_along_axis1_mm': round(float(comp1.max()) * 1000, 3),
                'note': 'Which grid axis the differential motion runs along. Motion running across the grid lines has no edge to travel along.'},
            'known_visible_fold_bands': fold_rows,
            'worst_edges': worst,
        })
        print('VISDIAG', f, 'median', round(float(np.median(ratio)), 3),
              'p90', round(float(np.percentile(ratio, 90)), 3),
              'max', round(float(ratio.max()), 3),
              '>2x', int((ratio > 2).sum()), flush=True)

    neutral(rig)
    restore = float(np.linalg.norm(coords(ob) - rest, axis=1).max() * 1000)
    assert restore < 0.001
    verify_inputs(before)
    out['ZERO_restore_max_mm'] = restore
    out['frozen_baseline_sha256'] = sha(BASE)
    out['action_payload_sha256'] = digest(action_payload(bpy.data.actions[ACTION]))
    out['inputs_unchanged'] = before
    out['blend_files_written'] = 0
    assert out['frozen_baseline_sha256'] == FROZEN_SHA
    assert out['action_payload_sha256'] == APPROVED_ACTION_SHA
    dump('VISIBLE_CREASE_DIAGNOSIS_R1.json', out)
    print('VISDIAG_READY')


run()