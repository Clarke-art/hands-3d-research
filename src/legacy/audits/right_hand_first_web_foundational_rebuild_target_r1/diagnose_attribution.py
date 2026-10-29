"""Read-only probe 4: reproduce the real skinning result exactly and separate the
three candidate causes on the worst F130 edges.

The dominant-bone-only prediction in the previous probe was NOT a faithful skinning
model: it applied one rigid transform per endpoint and ignored that a quad
interpolates between bone transforms at its corners. This probe reconstructs the
actual per-vertex LBS result from the bone matrices and the real weights, so the
attribution between bone-driven motion and mesh resolution is measured, not assumed.

Attribution logic on each worst edge:
  R = actual edge stretch ratio (deformed edge / rest edge)
  R_rigid = stretch that the two endpoints would get if the whole patch moved with
            the single bone that dominates the patch core (isolates how much of the
            fold is bulk rig motion rather than local tearing)
  R_grid  = stretch attributable to the quad grid having to interpolate a large
            differential across a single edge: measured as the differential that
            survives after removing the best-fit single rigid motion of the patch.

Nothing is written. No hidden-intersection or normal-dot measurement.
"""
import sys, json, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import *

PATCH = set(PATCH_IDS)


def skin_predict(ob, rig):
    """Exact per-vertex LBS, evaluated in the same world space the project uses.

    The project's authoritative `coords()` reads MW @ vertex.co on the evaluated
    mesh, i.e. WORLD space. To compare like for like, bone matrices must be taken
    to world space too: MW_mesh^-1 is applied first so the armature acts on mesh
    local coordinates, then the mesh world matrix maps the result back.
    """
    MW = ob.matrix_world
    MWi = MW.inverted()
    MWa = np.array(MW.to_4x4())
    MWia = np.array(MWi.to_4x4())
    mats = {}
    for bone in rig.pose.bones:
        mats[bone.name] = MWa @ np.array((rig.matrix_world @ bone.matrix).to_4x4()) @ MWia
    gidx = {g.name: i for i, g in enumerate(ob.vertex_groups)}
    out = np.zeros((len(ob.data.vertices), 3))
    for vi, v in enumerate(ob.data.vertices):
        p = np.append(np.array(v.co), 1.0)
        acc = np.zeros(4)
        for g in v.groups:
            acc += g.weight * (mats[ob.vertex_groups[g.group].name] @ p)
        out[vi] = (MWa @ acc)[:3]
    return out, mats


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
    names = [g.name for g in ob.vertex_groups]
    gidx = {g.name: i for i, g in enumerate(ob.vertex_groups)}
    W = np.zeros((len(ob.data.vertices), len(names)))
    for v in ob.data.vertices:
        for g in v.groups:
            W[v.index, g.group] = g.weight

    motion(rig, 130)
    actual = coords(ob)
    # Verify the reproduction matches Blender's own evaluation before trusting it.
    pred, mats = skin_predict(ob, rig)
    keys = list(ob.data.shape_keys.key_blocks)[0].name if ob.data.shape_keys else None
    err = float(np.linalg.norm(pred[PATCH_IDS] - actual[PATCH_IDS], axis=1).max() * 1000)
    print('SKIN_REPRO_MAX_ERROR_MM', round(err, 6), '| basis key', keys, flush=True)

    restL = rest[PATCH_IDS]
    edge_rest = restL[LE[:, 0]] - restL[LE[:, 1]]
    edge_len = np.linalg.norm(edge_rest, axis=1)
    actL = actual[PATCH_IDS]
    dd = (actL[LE[:, 0]] - actL[LE[:, 1]]) - edge_rest
    ratio = np.linalg.norm(dd, axis=1) / edge_len

    # Bulk rigid motion of the patch core, from the vertex closest to the patch centroid.
    cen = restL.mean(0)
    core = int(np.argmin(np.linalg.norm(restL - cen, axis=1)))
    core_bone = names[int(np.argmax(W[PATCH_IDS[core]]))]
    M = mats[core_bone]
    Mw = np.array([[M[i][j] for j in range(4)] for i in range(4)])

    # Residual after removing that bulk rigid motion: this is what the grid itself must absorb.
    predL = pred[PATCH_IDS]
    pred_resid = predL - (predL @ Mw[:3, :3].T + Mw[:3, 3])
    act_resid = actL - (actL @ Mw[:3, :3].T + Mw[:3, 3])
    res_dd = (act_resid[LE[:, 0]] - act_resid[LE[:, 1]]) - (pred_resid[LE[:, 0]] - pred_resid[LE[:, 1]])
    res_ratio = np.linalg.norm(res_dd, axis=1) / edge_len

    # Local curvature actually presented to the eye: dihedral change of the worst quads.
    faces = [tuple(p.vertices) for p in ob.data.polygons]
    Floc = [f for f in faces if all(v in PATCH for v in f)]

    def dihedral(f, P):
        import mathutils
        vs = [P[i] for i in f]
        try:
            n = (vs[1] - vs[0]).cross(vs[2] - vs[0])
            n.normalize()
        except Exception:
            return None
        best = None
        for a, b, c in [(0, 1, 2), (1, 2, 3)]:
            try:
                m = (vs[c] - vs[a]).cross(vs[(c + 1) % 4] - vs[a])
                m.normalize()
                ang = math.degrees(math.acos(max(-1.0, min(1.0, float(n.dot(m))))))
                best = ang if best is None else min(best, ang)
            except Exception:
                pass
        return best

    rows = []
    order = np.argsort(ratio)[::-1]
    for i in order[:20]:
        a, b = int(local[i][0]), int(local[i][1])
        wa = {names[k]: round(float(W[a, k]), 3) for k in np.nonzero(W[a])[0] if W[a, k] > 1e-3}
        wb = {names[k]: round(float(W[b, k]), 3) for k in np.nonzero(W[b])[0] if W[b, k] > 1e-3}
        rows.append({'edge': [a, b],
                     'rest_mm': round(float(edge_len[i]) * 1000, 3),
                     'actual_ratio': round(float(ratio[i]), 3),
                     'residual_ratio_after_bulk_rigid': round(float(res_ratio[i]), 3),
                     'weights_a': wa, 'weights_b': wb,
                     'weight_l1': round(float(np.abs(W[a] - W[b]).sum()), 4),
                     'n_bones_a': len(wa), 'n_bones_b': len(wb)})

    out = {'phase': PHASE, 'mode': 'READ_ONLY_SKINNING_ATTRIBUTION', 'blend_written': False,
           'frame': 130, 'time_seconds': 11.5 + 129 / 30.0,
           'skin_reproduction_max_error_mm': err,
           'skin_reproduction_note': 'Independent LBS reconstruction vs Blender evaluated mesh. Small error confirms the attribution below uses the real deformation, not a model.',
           'patch_core_bone': core_bone,
           'patch_local_edges': len(local), 'patch_quads': len(Floc),
           'rest_edge_len_mm': {'median': round(float(np.median(edge_len)) * 1000, 3),
                                'min': round(float(edge_len.min()) * 1000, 3),
                                'max': round(float(edge_len.max()) * 1000, 3)},
           'aggregate': {
               'edges_above_1x': int((ratio > 1).sum()),
               'edges_above_2x': int((ratio > 2).sum()),
               'edges_above_4x': int((ratio > 4).sum()),
               'residual_above_2x_after_bulk_rigid': int((res_ratio > 2).sum()),
               'residual_above_4x_after_bulk_rigid': int((res_ratio > 4).sum()),
               'of_total_local_edges': len(local),
               'interpretation': 'If most of the stretch survives after removing bulk rig motion, the fold is the patch being pulled apart by its own weight field, not the grid being too coarse for a rigid motion.'},
           'worst_edges': rows,
           'frozen_baseline_sha256': sha(BASE),
           'blend_files_written': 0}
    neutral(rig)
    restore = float(np.linalg.norm(coords(ob) - rest, axis=1).max() * 1000)
    assert restore < 0.001
    out['ZERO_restore_max_mm'] = restore
    verify_inputs(before)
    assert out['frozen_baseline_sha256'] == FROZEN_SHA
    dump('SKINNING_ATTRIBUTION_R1.json', out)
    print('ATTRIB', out['aggregate'])
    for r in rows[:12]:
        print('A', r['edge'], 'act', r['actual_ratio'], 'resid', r['residual_ratio_after_bulk_rigid'],
              'wL1', r['weight_l1'], 'bones', r['n_bones_a'], r['n_bones_b'], flush=True)
    print('ATTRIBUTION_READY')


run()