"""RIGHT_HAND_FIRST_WEB_TOPOLOGY_CAUSAL_PROBE_R1 — step 1: read-only patch inspection.

Answers, before any topology is designed:
  - is the 149-vertex first-web patch a topological disk with ONE clean boundary loop?
  - what is the existing loop / ring structure (so the candidate can be genuinely different)?
  - what is the per-vertex weight field over the patch?
  - which shape keys carry deltas inside the patch (they must be transferred, not sculpted)?
No .blend is written and nothing is modified.
"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import *

PATCH = PATCH_IDS
PSET = set(PATCH)


def main():
    before = protected_inputs()
    verify_inputs(before)
    ob, rig = open_frozen()

    faces = [tuple(p.vertices) for p in ob.data.polygons]
    edges = [tuple(e.vertices) for e in ob.data.edges]
    V = len(ob.data.vertices)
    F = len(faces)
    poly_sizes = sorted({len(f) for f in faces})

    ifl = [i for i, f in enumerate(faces) if all(v in PSET for v in f)]
    utilde = [(min(a, b), max(a, b)) for f in faces for a, b in zip(f, f[1:] + f[:1])]
    # boundary of the fully-contained face set = directed edges whose reverse does not appear
    dirs = {}
    for fi in ifl:
        f = faces[fi]
        for a, b in zip(f, f[1:] + f[:1]):
            dirs.setdefault(a, []).append(b)
    bnd_edges = [(a, b) for a in dirs for b in dirs[a] if a not in dirs.get(b, [])]
    # order into loops
    nxt = {a: b for a, b in bnd_edges}
    seen = set()
    loops = []
    for a, b in bnd_edges:
        if a in seen:
            continue
        loop = [a]
        seen.add(a)
        cur = b
        while cur != a:
            loop.append(cur)
            seen.add(cur)
            cur = nxt[cur]
        loops.append(loop)
    loops.sort(key=len, reverse=True)

    # local graph stats
    local_edges = [(a, b) for a, b in edges if a in PSET and b in PSET]
    val = {}
    for a, b in local_edges:
        val[a] = val.get(a, 0) + 1
        val[b] = val.get(b, 0) + 1
    valhist = {}
    for v, d in val.items():
        valhist[d] = valhist.get(d, 0) + 1

    # ring layers from the boundary loop (layer 0 = boundary)
    adj = {}
    for a, b in local_edges:
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, []).append(a)
    layer = {v: 0 for v in loops[0]}
    frontier = list(loops[0])
    nxtlayer = 1
    while frontier:
        nf = []
        for v in frontier:
            for w in adj[v]:
                if w not in layer:
                    layer[w] = nxtlayer
                    nf.append(w)
        frontier = nf
        nxtlayer += 1
    layerhist = {}
    for v, L in layer.items():
        layerhist[L] = layerhist.get(L, 0) + 1

    rest = coords(ob)
    PL = np.array([rest[v] for v in PATCH])

    # weight field
    wmap = {}
    for vid in PATCH:
        wmap[vid] = {ob.vertex_groups[g.group].name: round(float(g.weight), 6) for g in ob.data.vertices[vid].groups}

    # shape keys touching the patch
    keys = []
    if ob.data.shape_keys:
        for kb in ob.data.shape_keys.key_blocks:
            d = np.array([tuple(kb.data[i].co) for i in range(len(ob.data.vertices))], dtype=float)
            restv = np.array([tuple(ob.data.vertices[i].co) for i in range(len(ob.data.vertices))], dtype=float)
            delta = np.linalg.norm(d - restv, axis=1)
            inside = [v for v in PATCH if delta[v] > 1e-9]
            keys.append({'name': kb.name, 'value': float(kb.value), 'slider_min': float(kb.slider_min),
                         'slider_max': float(kb.slider_max), 'relative_to': kb.relative_key.name if kb.relative_key else None,
                         'changed_vertices_in_patch': len(inside),
                         'max_delta_in_patch_mm': float(delta[PATCH].max() * 1000) if inside else 0.0,
                         'total_changed_vertices': int((delta > 1e-9).sum())})

    out = {
        'phase': PHASE,
        'mode': 'READ_ONLY_PATCH_INSPECTION',
        'blend_files_written': 0,
        'mesh_name': m.MESH_NAME,
        'mesh_vertices': V, 'mesh_faces': F, 'mesh_polygon_sizes': poly_sizes,
        'patch_vertices': len(PATCH),
        'patch_fully_contained_faces': len(ifl),
        'patch_local_edges': len(local_edges),
        'patch_euler_V_minus_E_plus_F': len(PATCH) - len(local_edges) + len(ifl),
        'boundary_loops': [{'length': len(L), 'vertices': L} for L in loops],
        'local_valence_histogram': valhist,
        'ring_layer_histogram': layerhist,
        'patch_rest_bbox_min_mm': (PL.min(0) * 1000).tolist(),
        'patch_rest_bbox_max_mm': (PL.max(0) * 1000).tolist(),
        'patch_rest_extent_mm': ((PL.max(0) - PL.min(0)) * 1000).tolist(),
        'patch_surface_area_mm2': None,
        'shape_keys': keys,
        'vertex_group_names': [g.name for g in ob.vertex_groups],
        'patch_weight_pattern_counts': {},
        'modifiers': [{'name': mo.name, 'type': mo.type,
                       'object': mo.object.name if getattr(mo, 'object', None) else None} for mo in ob.modifiers],
        'subdivision_modifier_count': sum(1 for mo in ob.modifiers if mo.type == 'SUBSURF'),
    }
    pats = {}
    for vid, w in wmap.items():
        k = json.dumps(w, sort_keys=True)
        pats[k] = pats.get(k, 0) + 1
    out['patch_weight_pattern_counts'] = sorted(pats.items(), key=lambda kv: -kv[1])
    out['patch_distinct_weight_patterns'] = len(pats)

    # surface area of the fully-contained faces
    a = 0.0
    for fi in ifl:
        f = faces[fi]
        pts = [np.array(ob.data.vertices[v].co) for v in f]
        for j in range(1, len(f) - 1):
            a += float(np.linalg.norm(np.cross(pts[j] - pts[0], pts[j + 1] - pts[0])) * 0.5)
    out['patch_surface_area_mm2'] = a * 1e6

    neutral(rig)
    restore = float(np.linalg.norm(coords(ob) - rest, axis=1).max() * 1000)
    verify_inputs(before)
    out['ZERO_restore_max_mm'] = restore
    out['frozen_baseline_sha256'] = sha(BASE)
    assert out['frozen_baseline_sha256'] == FROZEN_SHA
    dump('PATCH_INSPECTION_R1.json', out)
    print('LOOPS', [(l['length']) for l in out['boundary_loops']])
    print('EULER', out['patch_euler_V_minus_E_plus_F'])
    print('VALHIST', out['local_valence_histogram'])
    print('LAYERS', out['ring_layer_histogram'])
    print('AREA_MM2', round(out['patch_surface_area_mm2'], 3))
    for k in keys:
        print('KEY', k['name'], 'changedInPatch', k['changed_vertices_in_patch'], 'maxDeltaMm', round(k['max_delta_in_patch_mm'], 5))
    print('INSPECTION_READY')


main()
