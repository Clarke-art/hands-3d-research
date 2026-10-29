"""Read-only structural diagnosis: why does the first web fold at F127/F130/F160
but stay smooth at F110?

Measures only quantities that can explain a Human-visible notch:
  - local grid edge-flow directions (two principal grid axes of the quad patch)
  - per-vertex deformation direction and magnitude at the six product frames
  - alignment between the deformation direction and the grid axes
  - grid edge length vs deformation amplitude (resolution adequacy)
  - existing skin influence distribution across the patch

No .blend is written. No hidden-crossing / normal-dot / census of any kind.
"""
import sys, json, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import *

FRAMES = [110, 127, 130, 160, 176, 205]
PATCH = set(PATCH_IDS)


def analyse():
    before = protected_inputs()
    verify_inputs(before)
    ob, rig = open_frozen()

    faces = [tuple(p.vertices) for p in ob.data.polygons]
    edges = [(e.vertices[0], e.vertices[1]) for e in ob.data.edges]
    E = np.array(edges)
    # Local grid = edges with both ends inside the first-web patch.
    mask = np.array([(a in PATCH and b in PATCH) for a, b in edges])
    localE = E[mask]
    F_local = [f for f in faces if all(v in PATCH for v in f)]

    neutral(rig)
    rest = coords(ob)
    # Local row index of every patch vertex, so patch-local arrays can be indexed by edge endpoints.
    slot = {v: i for i, v in enumerate(PATCH_IDS)}
    LE = np.array([[slot[a], slot[b]] for a, b in edges if a in PATCH and b in PATCH])
    rest_local = rest[PATCH_IDS]
    # Grid axes from local edge direction histogram (two peaks = quad grid axes).
    d = rest_local[LE[:, 0]] - rest_local[LE[:, 1]]
    L = np.linalg.norm(d, axis=1)
    u = d / L[:, None]
    ang = np.degrees(np.arctan2(u[:, 2], u[:, 0]))
    hist, edges_h = np.histogram(ang, bins=72, range=(-180, 180))
    centres = (edges_h[:-1] + edges_h[1:]) / 2
    order = np.argsort(hist)[::-1][:2]
    axes = sorted(centres[order].tolist())
    while axes[-1] - axes[0] > 180:
        axes = [a + 360 if a < 0 else a for a in axes]
    ax0, ax1 = axes

    def axis_frame():
        a0 = math.radians(ax0)
        e0 = np.array([math.cos(a0), 0.0, math.sin(a0)])
        e0 /= np.linalg.norm(e0)
        # Second axis = the one maximising orthogonality in the actual tangent spread.
        proj = u - np.outer(u @ e0, e0)
        w = np.linalg.norm(proj, axis=1)
        v = (proj * w[:, None]).sum(0)
        e1 = v / np.linalg.norm(v)
        return e0, e1

    e0, e1 = axis_frame()
    report = {
        'phase': PHASE,
        'mode': 'READ_ONLY_STRUCTURAL_DIAGNOSIS',
        'blend_written': False,
        'patch': {'vertices': len(PATCH_IDS), 'fully_contained_quads': len(F_local),
                  'local_edges': int(mask.sum()),
                  'local_edge_length_mm': {'min': float(L.min() * 1000), 'median': float(np.median(L) * 1000),
                                           'max': float(L.max() * 1000), 'mean': float(L.mean() * 1000)}},
        'grid_axes': {'axis0_xz_deg': ax0, 'axis1_xz_deg': ax1,
                      'e0': e0.tolist(), 'e1': e1.tolist(),
                      'note': 'Principal axes of the existing first-web quad grid, from the rest-pose local edge-direction histogram. Read as layout context only.'},
        'frames': [],
    }

    wmap = {}
    for v in ob.data.vertices:
        if v.index in PATCH:
            wmap[v.index] = {ob.vertex_groups[g.group].name: round(g.weight, 4) for g in v.groups}

    for f in FRAMES:
        motion(rig, f)
        P = coords(ob)
        disp = P[PATCH_IDS] - rest_local
        mag = np.linalg.norm(disp, axis=1)
        # Component of deformation along each grid axis vs across them.
        c0 = disp @ e0
        c1 = disp @ e1
        # Principal direction of the deformation field itself.
        if mag.max() > 1e-9:
            w = mag ** 2
            mean = (disp * w[:, None]).sum(0) / w.sum()
            cov = ((disp - mean).T * w) @ (disp - mean) / w.sum()
            ev, evec = np.linalg.eigh(cov)
            pdir = evec[:, int(np.argmax(ev))]
            pdir /= np.linalg.norm(pdir)
        else:
            pdir = np.array([1.0, 0.0, 0.0])
        def ang_to(v):
            c = abs(float(np.dot(v, pdir)))
            return math.degrees(math.acos(min(1.0, c)))
        report['frames'].append({
            'frame': f, 'source_frame': 690 + 2 * (f - 1), 'time_seconds': 11.5 + (f - 1) / 30.0,
            'displacement_mm': {'min': float(mag.min() * 1000), 'median': float(np.median(mag) * 1000),
                                'p90': float(np.percentile(mag, 90) * 1000), 'max': float(mag.max() * 1000)},
            'displacement_vs_grid': {
                'median_abs_along_axis0_mm': float(np.median(np.abs(c0)) * 1000),
                'median_abs_along_axis1_mm': float(np.median(np.abs(c1)) * 1000),
                'principal_deformation_direction': pdir.tolist(),
                'angle_to_grid_axis0_deg': round(ang_to(e0), 2),
                'angle_to_grid_axis1_deg': round(ang_to(e1), 2),
                'note': 'How the local deformation field is oriented relative to the existing quad-grid axes. Large off-axis angle means the grid does not carry the motion along its own lines.'},
            'resolution': {
                'median_edge_mm': float(np.median(L) * 1000),
                'max_displacement_mm': float(mag.max() * 1000),
                'max_displacement_over_median_edge': round(float(mag.max() * 1000) / float(np.median(L) * 1000), 3),
                'p90_displacement_over_median_edge': round(float(np.percentile(mag, 90) * 1000) / float(np.median(L) * 1000), 3),
                'note': 'Deformation amplitude expressed in grid cells. Values well above 1 mean a single quad must absorb motion larger than its own size.'},
            'skin_influence': {'distinct_patterns': len({json.dumps(v, sort_keys=True) for v in wmap.values()}),
                               'bones_present': sorted({b for v in wmap.values() for b in v})},
        })
        print('DIAG_FRAME', f, 'maxdisp_mm', round(mag.max() * 1000, 3),
              'axis0_deg', report['frames'][-1]['displacement_vs_grid']['angle_to_grid_axis0_deg'],
              'axis1_deg', report['frames'][-1]['displacement_vs_grid']['angle_to_grid_axis1_deg'], flush=True)

    # Per-vertex detail kept for the frames that decide the diagnosis.
    detail = {}
    for f in [110, 130, 205]:
        motion(rig, f)
        P = coords(ob)
        disp = (P - rest)
        rows = []
        for i, vid in enumerate(PATCH_IDS):
            rows.append({'v': vid, 'd': [round(x * 1000, 4) for x in disp[vid]],
                         'dm': round(float(np.linalg.norm(disp[vid])) * 1000, 4),
                         'w': wmap[vid]})
        detail[str(f)] = rows
    neutral(rig)
    report['per_vertex_detail'] = detail
    report['skin_pattern_counts'] = {}
    for vid, w in wmap.items():
        k = json.dumps(w, sort_keys=True)
        report['skin_pattern_counts'][k] = report['skin_pattern_counts'].get(k, 0) + 1
    report['distinct_skin_patterns'] = len(report['skin_pattern_counts'])
    report['skin_pattern_histogram'] = sorted(report['skin_pattern_counts'].items(), key=lambda kv: -kv[1])

    restore = float(np.linalg.norm(coords(ob) - rest, axis=1).max() * 1000)
    assert restore < 0.001
    verify_inputs(before)
    report['ZERO_restore_max_mm'] = restore
    report['frozen_baseline_sha256'] = sha(BASE)
    report['action_payload_sha256'] = digest(action_payload(bpy.data.actions[ACTION]))
    report['inputs_unchanged'] = before
    report['blend_files_written'] = 0
    assert report['frozen_baseline_sha256'] == FROZEN_SHA
    assert report['action_payload_sha256'] == APPROVED_ACTION_SHA
    dump('STRUCTURAL_DIAGNOSIS_R1.json', report)
    print('DIAGNOSIS_READY')


analyse()