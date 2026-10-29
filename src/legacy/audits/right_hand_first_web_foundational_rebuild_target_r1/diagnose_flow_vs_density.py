"""Read-only probe 5: the decisive structural question.

Two candidate causes remain, and they need different rebuild levels:

  (H-DENSITY)  The first-web quad grid is simply too coarse: a single ~3.5 mm edge
               must absorb a differential of ~25 mm (measured 7.16x at F130).
               Fix level: LEVEL 1, re-design edge flow / density.

  (H-FLOW)     Density is adequate, but the existing grid's edge lines do not run
               along the direction the tissue actually stretches, so the quad has
               to carry the motion across its own bands and buckles into a stair.
               Fix level: LEVEL 1 as well, but a re-design of DIRECTION rather than
               a refinement of the same layout -- and critically, refinement alone
               (what route A already tried) cannot fix it.

Discriminator: if (H-DENSITY) were the whole story, subdividing the same layout
into N x N smaller quads would reduce the per-edge differential by roughly N.
Route A already performed a refinement of the same layout and did NOT clear the
blocker. Therefore test whether the measured differential is isotropic (a pure
resolution problem) or strongly directional (a flow problem).

Measures, per local edge at each frame:
  - differential magnitude and its direction in the local tangent plane
  - the angle between the differential direction and the nearest existing grid axis
  - isotropy of the differential field across the patch
  - how many local quads the motion has to cross

Then compares F110/F176 (smooth) against F127/F130/F160/F205 (folded).
Nothing is written; no weights, bones, topology or poses are touched.
"""
import sys, json, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import *

FRAMES = [110, 127, 130, 160, 176, 205]
PATCH = set(PATCH_IDS)


def run():
    before = protected_inputs()
    verify_inputs(before)
    ob, rig = open_frozen()
    diag = json.loads((OUT / 'STRUCTURAL_DIAGNOSIS_R1.json').read_text(encoding='utf-8-sig'))
    e0 = np.array(diag['grid_axes']['e0'])
    e1 = np.array(diag['grid_axes']['e1'])

    edges = [(e.vertices[0], e.vertices[1]) for e in ob.data.edges]
    local = [(a, b) for a, b in edges if a in PATCH and b in PATCH]
    slot = {v: i for i, v in enumerate(PATCH_IDS)}
    LE = np.array([[slot[a], slot[b]] for a, b in local])
    faces = [tuple(p.vertices) for p in ob.data.polygons]
    Floc = [f for f in faces if all(v in PATCH for v in f)]

    neutral(rig)
    rest = coords(ob)
    restL = rest[PATCH_IDS]
    edge_rest = restL[LE[:, 0]] - restL[LE[:, 1]]
    edge_len = np.linalg.norm(edge_rest, axis=1)
    ed = edge_rest / edge_len[:, None]
    a0 = np.abs(ed @ e0)
    a1 = np.abs(ed @ e1)
    axis_of = np.where(a0 >= a1, 0, 1)

    out = {'phase': PHASE, 'mode': 'READ_ONLY_FLOW_VS_DENSITY', 'blend_written': False,
           'grid_axes': {'e0': e0.tolist(), 'e1': e1.tolist()},
           'patch': {'vertices': len(PATCH_IDS), 'quads': len(Floc), 'local_edges': len(local),
                     'rest_edge_median_mm': round(float(np.median(edge_len)) * 1000, 3)},
           'frames': []}

    for f in FRAMES:
        motion(rig, f)
        actL = coords(ob)[PATCH_IDS]
        dd = (actL[LE[:, 0]] - actL[LE[:, 1]]) - edge_rest
        dl = np.linalg.norm(dd, axis=1)
        ratio = dl / edge_len

        # Tangent-plane basis at each edge midpoint, built from the two grid axes.
        mid = (restL[LE[:, 0]] + restL[LE[:, 1]]) / 2
        # project the differential onto each grid axis
        c0 = np.abs(dd @ e0)
        c1 = np.abs(dd @ e1)
        # anisotropy of the differential field: high when motion is confined to one axis
        tot = c0 + c1 + 1e-12
        aniso = np.abs(c0 - c1) / tot

        # Angle between the differential and the nearest existing grid axis.
        best_ang = []
        for v in dd:
            nv = np.linalg.norm(v)
            if nv < 1e-12:
                best_ang.append(0.0)
                continue
            v = v / nv
            b0 = math.degrees(math.acos(min(1.0, abs(float(v @ e0)))))
            b1 = math.degrees(math.acos(min(1.0, abs(float(v @ e1)))))
            best_ang.append(min(b0, b1))
        best_ang = np.array(best_ang)

        hi = ratio > 2.0
        out['frames'].append({
            'frame': f, 'source_frame': 690 + 2 * (f - 1), 'time_seconds': 11.5 + (f - 1) / 30.0,
            'differential_mm': {'median': round(float(np.median(dl)) * 1000, 3),
                                'p90': round(float(np.percentile(dl, 90)) * 1000, 3),
                                'max': round(float(dl.max()) * 1000, 3)},
            'stretch_ratio': {'median': round(float(np.median(ratio)), 3),
                              'p90': round(float(np.percentile(ratio, 90)), 3),
                              'max': round(float(ratio.max()), 3),
                              'above_2x': int(hi.sum()), 'of_total': len(local)},
            'direction_vs_grid': {
                'median_angle_to_nearest_grid_axis_deg': round(float(np.median(best_ang)), 2),
                'p90_angle_to_nearest_grid_axis_deg': round(float(np.percentile(best_ang, 90)), 2),
                'mean_anisotropy_0_uniform_1_axis_confined': round(float(np.mean(aniso)), 4),
                'median_abs_component_axis0_mm': round(float(np.median(c0)) * 1000, 3),
                'median_abs_component_axis1_mm': round(float(np.median(c1)) * 1000, 3),
                'note': 'If the differential ran along an existing grid line, the angle would be near 0 and no stair could form. A large angle means the quad must carry motion across its own bands.'},
            'verdict_signal': ('SMOOTH_NO_EDGE_ABOVE_2X' if hi.sum() == 0 else 'FOLDED'),
        })
        r = out['frames'][-1]
        print('FLOW', f, r['verdict_signal'], '| max', r['differential_mm']['max'],
              'mm | medAngle', r['direction_vs_grid']['median_angle_to_nearest_grid_axis_deg'],
              'deg | aniso', r['direction_vs_grid']['mean_anisotropy_0_uniform_1_axis_confined'],
              '| >2x', r['stretch_ratio']['above_2x'], flush=True)

    neutral(rig)
    restore = float(np.linalg.norm(coords(ob) - rest, axis=1).max() * 1000)
    assert restore < 0.001
    verify_inputs(before)
    out['ZERO_restore_max_mm'] = restore
    out['frozen_baseline_sha256'] = sha(BASE)
    out['blend_files_written'] = 0
    assert out['frozen_baseline_sha256'] == FROZEN_SHA
    dump('FLOW_VS_DENSITY_R1.json', out)
    print('FLOW_READY')


run()