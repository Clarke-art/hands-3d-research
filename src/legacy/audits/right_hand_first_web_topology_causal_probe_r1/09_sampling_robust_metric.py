"""Sampling-robust restatement of the secondary metric (read-only).

The raw ">2x pair count per 100 mm2" grows when a region is sampled more finely, so it is
not comparable across different vertex budgets. This script recomputes the same measurement
as a per-sample fraction, which is.

Opens the saved DESIGN_ONLY candidate read-only.
"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import *

FRAMES = [110, 127, 130, 160, 176, 205]
RADIUS_MM = 5.0
PATCH = PATCH_IDS
CAND = OUT / 'RIGHT_HAND_FIRST_WEB_TOPOLOGY_PROBE_CANDIDATE_R1.blend'
CAND_NAME = 'RIGHT_HAND_OFFICIAL_L1_PRODUCT_MESH__PROBE_TOPOLOGY_R1'


def tri_of(f):
    return [(f[0], f[1], f[2]), (f[0], f[2], f[3])] if len(f) == 4 else [(f[0], f[1], f[2])]


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.open_mainfile(filepath=str(CAND), load_ui=False, use_scripts=False)
    ob = bpy.data.objects[m.MESH_NAME]
    cob = bpy.data.objects[CAND_NAME]
    rig = bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG']
    faces = [tuple(p.vertices) for p in ob.data.polygons]
    cfaces = [tuple(p.vertices) for p in cob.data.polygons]
    pf = set()
    for i, f in enumerate(faces):
        if all(v in set(PATCH) for v in f):
            pf.add(i)
    # probe vertices that were interpolated from a triangle of a first-web patch face
    probe_rest_local = np.array([tuple(v.co) for v in cob.data.vertices])
    baseline_rest_local = np.array([tuple(v.co) for v in ob.data.vertices])
    # identify probe vertices inside the original patch region by distance to its PL surface
    Tr = np.array([t for i in pf for t in tri_of(faces[i])])
    A = baseline_rest_local[Tr[:, 0]]; B = baseline_rest_local[Tr[:, 1]]; C = baseline_rest_local[Tr[:, 2]]
    sel = []
    for vid in range(len(probe_rest_local)):
        p = probe_rest_local[vid]
        best = 1e9
        for s in range(0, len(Tr), 400):
            a = A[s:s + 400]; b = B[s:s + 400]; c = C[s:s + 400]
            ab = b - a; ac = c - a; ap = p[None, :] - a
            d1 = np.einsum('tc,tc->t', ap, ab); d2 = np.einsum('tc,tc->t', ap, ac)
            e11 = np.einsum('tc,tc->t', ab, ab); e12 = np.einsum('tc,tc->t', ab, ac); e22 = np.einsum('tc,tc->t', ac, ac)
            den = np.where(np.abs(e11 * e22 - e12 * e12) < 1e-30, 1e-30, e11 * e22 - e12 * e12)
            u = np.clip((d1 * e22 - d2 * e12) / den, 0, 1); v = np.clip((d2 * e11 - d1 * e12) / den, 0, 1)
            ov = u + v > 1.0
            u = np.where(ov, 1 - v, u)
            cp = a + u[:, None] * ab + v[:, None] * ac
            best = min(best, float(np.linalg.norm(p[None, :] - cp, axis=1).min()))
        if best < 2e-5:
            sel.append(vid)
    sel = np.array(sel)
    print('probe samples inside the original first-web region:', len(sel), flush=True)

    def coords(obj):
        return np.array([list(v) for v in m.evaluate(obj, obj.matrix_world)[0]])

    rows = []
    for f in FRAMES:
        rig.animation_data.action = bpy.data.actions['PIANOVAM_PHYSICAL_RIGHT_AXIS_CORRECTED_R1']
        for t in rig.animation_data.nla_tracks:
            t.mute = False
        bpy.context.scene.frame_set(f)
        bpy.context.view_layer.update()
        Vb = coords(ob); Vc = coords(cob)
        out = {'frame': f}
        for label, V, ids, R0 in [('baseline', Vb, np.array(PATCH), baseline_rest_local),
                                  ('probe', Vc, sel, probe_rest_local)]:
            Vv = V[ids]; Vrest = R0[ids]
            Dm = np.linalg.norm(Vv[:, None, :] - Vv[None, :, :], axis=2)
            Rm = np.linalg.norm(Vrest[:, None, :] - Vrest[None, :, :], axis=2)
            mask = (Rm <= RADIUS_MM / 1000.0) & (Rm > 1e-9)
            ratio = np.where(mask, Dm / np.maximum(Rm, 1e-12), 0.0)
            per = ratio.max(axis=1)
            out[label] = {'samples': int(len(ids)),
                          'fraction_of_samples_with_local_ratio_above_2x': round(float((per > 2.0).mean()), 4),
                          'fraction_of_samples_with_local_ratio_above_4x': round(float((per > 4.0).mean()), 4),
                          'median_local_max_ratio': round(float(np.median(per)), 4)}
        rows.append(out)
        print('ROBUST', f, out['baseline'], out['probe'], flush=True)

    dump('SAMPLING_ROBUST_METRIC_R1.json', {'phase': PHASE,
                                            'mode': 'READ_ONLY_SAMPLING_ROBUST_RESTATEMENT',
                                            'candidate_blend_sha256': sha(CAND),
                                            'note': 'per-sample fractions of the same 5 mm radius measurement; '
                                                    'unlike a raw count they are comparable across vertex budgets.',
                                            'rows': rows})
    print('ROBUST_READY')


main()
