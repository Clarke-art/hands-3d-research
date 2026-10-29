"""RIGHT_HAND_FIRST_WEB_TOPOLOGY_CAUSAL_PROBE_R1 — ONE bounded structural probe.

WHAT IS CHANGED structurally (this is deliberately NOT a subdivide)
  The first web is re-laid-out as a single structured bridge:
    * Region Of Interest = the approved 149-vertex first-web patch expanded outward by
      RINGS rings, so the OLD inner patch boundary line is dissolved and rebuilt;
    * the ROI interior becomes ONE NU x NV structured quad grid instead of nested rings;
    * the bridge is re-spanned: the four grid corners are placed by the ROI boundary's own
      chord distribution, so the strips do not follow the old layout;
    * loop spacing is GRADED by the measured six-frame deformation load: support rows are
      densified in the high-load bands and coarsened in the low-load bands;
    * every interior node keeps valence 4 and every face stays a quad.

  The layout is designed in a proven fold-free parameter domain (harmonic/most-convex-
  combination map with the boundary pinned, in order, to a convex square), and every grid
  node is then pulled back onto the original rest surface by barycentric interpolation.
  A grid that is valid in the parameter domain is therefore valid on the surface.

WHAT IS DELIBERATELY HELD CONSTANT (this is what makes it a causal test)
  * 21 teaching bones, their rest transforms, Action, retarget mapping, frames: untouched.
  * Every new vertex lies EXACTLY on the original piecewise-linear rest surface -> the rest
    hand shape is preserved.
  * Every new vertex receives the barycentric interpolation of the ORIGINAL vertices' skin
    weights -> no new weight painting; the skinning field semantics are preserved.
  * The approved corrective shape key is transferred by the same interpolation and keeps the
    same driver expression and variables -> no new sculpted delta.
"""
import sys, json, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import *

FRAMES = [110, 127, 130, 160, 176, 205]
RINGS = 2
RADIUS_MM = 5.0
NBINS = 24
GRADE_BLEND = 0.55
RELAX_ITERS = 250
PATCH = PATCH_IDS
PSET = set(PATCH)
CAND_NAME = 'RIGHT_HAND_OFFICIAL_L1_PRODUCT_MESH__PROBE_TOPOLOGY_R1'
CANDIDATE = OUT / 'RIGHT_HAND_FIRST_WEB_TOPOLOGY_PROBE_CANDIDATE_R1.blend'
VIEWS = ['FIRST_WEB_OBLIQUE', 'PALMAR_THENAR_CLOSE']
DIR_OBLIQUE = [0.1998003125190735, -0.9390614628791809, 0.2797204256057739]
DIR_PALMAR = [-0.38183954, -0.92405248, 0.0180442]


def tri_of(f):
    return [(f[0], f[1], f[2]), (f[0], f[2], f[3])] if len(f) == 4 else [(f[0], f[1], f[2])]


def build_roi(faces, patch, rings):
    adj = {}
    for f in faces:
        for a, b in zip(f, f[1:] + f[:1]):
            adj.setdefault(a, set()).add(b)
    roi, frontier = set(patch), set(patch)
    for _ in range(rings):
        nf = set()
        for v in frontier:
            nf |= adj[v]
        nf -= roi
        roi |= nf
        frontier = nf
    while True:
        ifl = [i for i, f in enumerate(faces) if all(v in roi for v in f)]
        used = {v for fi in ifl for v in faces[fi]}
        if used == roi:
            break
        roi = used
    return roi, ifl


def boundary_loop(faces, ifl):
    suc = {}
    for fi in ifl:
        f = faces[fi]
        for a, b in zip(f, f[1:] + f[:1]):
            suc.setdefault(a, []).append(b)
    bed = [(a, b) for a in suc for b in suc[a] if a not in suc.get(b, [])]
    nxt = {a: b for a, b in bed}
    seen, loops = set(), []
    for a, b in bed:
        if a in seen:
            continue
        loop, cur = [a], b
        seen.add(a)
        while cur != a:
            loop.append(cur); seen.add(cur); cur = nxt[cur]
        loops.append(loop)
    loops.sort(key=len, reverse=True)
    return loops


def most_convex_weights(P, tris):
    """Mean-value (Floater) coordinate weights for a triangulated surface: symmetric,
    strictly positive, derived from the rest geometry only. Deterministic."""
    n = len(P)
    acc = {}
    for t in tris:
        for a, b, c in ((0, 1, 2), (1, 2, 0), (2, 0, 1)):
            i, j, k = t[a], t[b], t[c]
            d_i = P[j] - P[i]; d_k = P[k] - P[i]
            d_j = P[k] - P[j]; d_i2 = P[i] - P[j]
            def ang(u, v):
                nu = np.linalg.norm(u); nv = np.linalg.norm(v)
                if nu < 1e-15 or nv < 1e-15:
                    return 0.0
                cs = float(np.clip(np.dot(u, v) / (nu * nv), -1.0, 1.0))
                return math.acos(cs)
            w = (math.tan(ang(d_i, d_k) * 0.5) + math.tan(ang(d_j, d_i2) * 0.5)) / max(float(np.linalg.norm(P[i] - P[j])), 1e-12)
            w = max(w, 1e-9)
            acc[(i, j)] = acc.get((i, j), 0.0) + w
            acc[(j, i)] = acc.get((j, i), 0.0) + w
    return acc


# ------------------------------------------------------------------ build candidate
def build(ob, rig):
    faces = [tuple(p.vertices) for p in ob.data.polygons]
    NV0 = len(ob.data.vertices)
    neutral(rig)
    local0 = np.array([tuple(v.co) for v in ob.data.vertices])
    rest = coords(ob)

    roi, ifl = build_roi(faces, PATCH, RINGS)
    loops = boundary_loop(faces, ifl)
    assert len(loops) == 1, [len(x) for x in loops]
    loop = loops[0]
    B = len(loop)
    assert B % 2 == 0, B
    roi_list = sorted(roi)
    slot = {v: i for i, v in enumerate(roi_list)}
    roi_tris, tri_face = [], []
    for fi in ifl:
        for t in tri_of(faces[fi]):
            roi_tris.append(t); tri_face.append(fi)
    patch_faces = {fi for fi in ifl if all(v in PSET for v in faces[fi])}
    n_edge = len({tuple(sorted(e)) for fi in ifl for e in zip(faces[fi], faces[fi][1:] + faces[fi][:1])})
    euler = len(roi) - n_edge + len(ifl)
    assert euler == 1, euler
    print('ROI verts', len(roi), 'faces', len(ifl), 'boundary', B, 'patch_faces', len(patch_faces),
          'euler', euler, flush=True)

    centro = local0[roi_list].mean(0)
    d0 = int(np.argmax(np.linalg.norm(local0[loop] - centro, axis=1)))
    NU, NV = B // 4, B // 2 - B // 4
    c = [d0, (d0 + NU) % B, (d0 + NU + NV) % B, (d0 + NU + NV + NU) % B]
    assert len(set(c)) == 4
    print('grid NU,NV', NU, NV, flush=True)

    # ---- six-frame deformation load
    deformed = {}
    for f in FRAMES:
        motion(rig, f)
        deformed[f] = coords(ob)
    neutral(rig)
    assert float(np.linalg.norm(coords(ob) - rest, axis=1).max() * 1000) < 0.001
    Rr = local0[roi_list]
    Dm = np.linalg.norm(Rr[:, None, :] - Rr[None, :, :], axis=2)
    near = (Dm <= RADIUS_MM / 1000.0) & (Dm > 1e-9)
    load = np.zeros(len(roi_list))
    for f in FRAMES:
        D = deformed[f][roi_list]
        dd = np.abs(np.linalg.norm(D[:, None, :] - D[None, :, :], axis=2) - Dm) / np.maximum(Dm, 1e-12)
        load = np.maximum(load, np.where(near, dd, 0.0).max(axis=1))
    load_map = {v: float(load[slot[v]]) for v in roi_list}

    # ---- parameterisation: pin the boundary in order to a convex square
    prefix = [0.0]
    for i in range(B):
        prefix.append(prefix[-1] + float(np.linalg.norm(local0[loop[i]] - local0[loop[(i + 1) % B]])))

    def arc(start, k):
        a = prefix[start]
        b = prefix[start + k] if (start + k) <= B else prefix[B] + prefix[start + k - B]
        return b - a

    SQ = [(-1.0, -1.0), (1.0, -1.0), (1.0, 1.0), (-1.0, 1.0)]

    def place(start, count, p0, p1):
        span = max(arc(start, count), 1e-15)
        out = {}
        for k in range(count + 1):
            t = arc(start, k) / span
            out[loop[(start + k) % B]] = (p0[0] * (1 - t) + p1[0] * t, p0[1] * (1 - t) + p1[1] * t)
        return out

    pinned = {}
    for s, cnt, p0, p1 in [(c[0], NU, SQ[0], SQ[1]), (c[1], NV, SQ[1], SQ[2]),
                           (c[2], NU, SQ[2], SQ[3]), (c[3], NV, SQ[3], SQ[0])]:
        for k, v in place(s, cnt, p0, p1).items():
            pinned.setdefault(k, v)
    assert len(pinned) == B, (len(pinned), B)

    n = len(roi_list)
    loc = {v: i for i, v in enumerate(roi_list)}
    tris_loc = [(loc[t[0]], loc[t[1]], loc[t[2]]) for t in roi_tris]
    W = most_convex_weights(local0[roi_list], tris_loc)
    rows, cols, vals = [], [], []
    for (i, j), w in W.items():
        rows.append(i); cols.append(j); vals.append(-w)
    for i in range(n):
        pass
    diag = {}
    for (i, j), w in W.items():
        diag[i] = diag.get(i, 0.0) - w
    for i, d in diag.items():
        rows.append(i); cols.append(i); vals.append(-d)
    L = np.zeros((n, n))
    for r, cc, vv in zip(rows, cols, vals):
        L[r, cc] += vv

    free = [v for v in roi_list if v not in pinned]
    fi = [loc[v] for v in free]
    bd = [loc[v] for v in roi_list if v in pinned]
    Pbd = np.array([pinned[v] for v in roi_list if v in pinned])
    sol = np.linalg.solve(L[np.ix_(fi, fi)], -L[np.ix_(fi, bd)] @ Pbd)
    P = np.zeros((n, 2))
    for k, v in enumerate(free):
        P[loc[v]] = sol[k]
    for v in pinned:
        P[loc[v]] = pinned[v]
    assert np.isfinite(P).all(), 'parameterisation produced non-finite values'
    triP = np.array([P[[loc[t[0]], loc[t[1]], loc[t[2]]]] for t in roi_tris])
    cross = (triP[:, 1, 0] - triP[:, 0, 0]) * (triP[:, 2, 1] - triP[:, 0, 1]) - \
            (triP[:, 1, 1] - triP[:, 0, 1]) * (triP[:, 2, 0] - triP[:, 0, 0])
    flipped = int((cross < 0).sum())
    degenerate = int((cross == 0).sum())
    print('parameterisation: flipped triangles', flipped, 'degenerate', degenerate, 'of', len(cross),
          'min area', float(cross.min()), flush=True)
    assert flipped == 0, 'parameterisation folded; refusing to build a candidate from it'

    # ---- load-graded axis samples in the parameter domain
    Lv = np.array([load_map[v] for v in roi_list])

    def marginal(axis):
        hist = np.zeros(NBINS); cnt = np.zeros(NBINS)
        b = np.clip((((P[:, axis] + 1.0) / 2.0) * NBINS).astype(int), 0, NBINS - 1)
        for bi, w in zip(b, Lv):
            hist[bi] += w; cnt[bi] += 1
        mean = np.where(cnt > 0, hist / np.maximum(cnt, 1), 0.0)
        return np.concatenate([[0.0], np.cumsum(mean + 1e-9)])

    def graded(cum, cnt_n):
        base = np.linspace(0.0, 1.0, cnt_n)
        g = np.interp(np.linspace(0.0, cum[-1], cnt_n), cum, np.linspace(0.0, 1.0, len(cum)))
        s = (1 - GRADE_BLEND) * base + GRADE_BLEND * g
        need = 0.45 / cnt_n
        for _ in range(400):
            d = np.diff(s)
            if (d >= need - 1e-15).all():
                break
            s = np.concatenate([[s[0]], s[0] + np.cumsum(np.maximum(d, need))])
        s = np.clip(s, 0.0, 1.0)
        s[0] = 0.0; s[-1] = 1.0
        return s

    us = graded(marginal(0), NU + 1)
    vs = graded(marginal(1), NV + 1)

    bottom2 = np.array([pinned[loop[(c[0] + i) % B]] for i in range(NU + 1)])
    right2 = np.array([pinned[loop[(c[1] + j) % B]] for j in range(NV + 1)])
    top2 = np.array([pinned[loop[(c[2] + i) % B]] for i in range(NU + 1)])[::-1]
    left2 = np.array([pinned[loop[(c[3] + j) % B]] for j in range(NV)] + [pinned[loop[c[0]]]])[::-1]

    def walk(nodes, t):
        seg = np.linalg.norm(np.diff(nodes, axis=0), axis=1)
        cum = np.concatenate([[0.0], np.cumsum(seg)])
        x = float(np.clip(t, 0.0, 1.0)) * cum[-1]
        i = int(np.clip(np.searchsorted(cum, x, side='right') - 1, 0, len(nodes) - 2))
        r = (x - cum[i]) / max(seg[i], 1e-15)
        return nodes[i] * (1 - r) + nodes[i + 1] * r

    def coons2(bottom, right, top, left, u, v):
        bq = walk(bottom, u); tq = walk(top, u); lq = walk(left, v); rq = walk(right, v)
        c0, c1, c2, c3 = bottom[0], bottom[-1], top[-1], top[0]
        lin = (1 - u) * (1 - v) * c0 + u * (1 - v) * c1 + u * v * c2 + (1 - u) * v * c3
        return (1 - v) * bq + v * tq + (1 - u) * lq + u * rq - lin

    node2 = {}
    for i in range(NU + 1):
        node2[(i, 0)] = np.array(pinned[loop[(c[0] + i) % B]])
    for j in range(NV + 1):
        node2[(NU, j)] = np.array(pinned[loop[(c[1] + j) % B]])
    for i in range(NU + 1):
        node2[(i, NV)] = np.array(pinned[loop[(c[2] + (NU - i)) % B]])
    for j in range(NV + 1):
        node2[(0, j)] = np.array(pinned[loop[(c[3] + (NV - j)) % B]])
    interior = [(i, j) for j in range(1, NV) for i in range(1, NU)]
    for (i, j) in interior:
        node2[(i, j)] = coons2(bottom2, right2, top2, left2, float(us[i]), float(vs[j]))

    # ---- graded relaxation, entirely inside the convex square (cannot leave the domain)
    li = float(np.linalg.norm(np.diff(bottom2, axis=0), axis=1).sum())
    lj = float(np.linalg.norm(np.diff(left2, axis=0), axis=1).sum())
    thu = np.diff(us) * li
    tvv = np.diff(vs) * lj
    idx2 = {k: kk for kk, k in enumerate(interior)}
    pos = {k: v for k, v in node2.items()}
    for _ in range(RELAX_ITERS):
        new = {}
        for (i, j) in interior:
            acc = np.zeros(2); ws = 0.0
            for nb, tgt in [((i - 1, j), thu[i - 1]), ((i + 1, j), thu[i]), ((i, j - 1), tvv[j - 1]), ((i, j + 1), tvv[j])]:
                w = 1.0 / max(tgt, 1e-9)
                acc += w * pos[nb]; ws += w
            new[(i, j)] = acc / max(ws, 1e-12)
        pos.update(new)
    for k, v in pos.items():
        node2[k] = v

    # verify the 2-D grid: every cell must be a positively oriented, non-degenerate quad
    def cell_area(a, b, cc, d):
        pts = [a, b, cc, d]
        s = 0.0
        for m in range(4):
            x1, y1 = pts[m]; x2, y2 = pts[(m + 1) % 4]
            s += x1 * y2 - x2 * y1
        return 0.5 * s
    areas = []
    for j in range(NV):
        for i in range(NU):
            areas.append(cell_area(node2[(i, j)], node2[(i + 1, j)], node2[(i + 1, j + 1)], node2[(i, j + 1)]))
    areas = np.array(areas)
    print('2-D cells', len(areas), 'min area', float(areas.min()), 'max', float(areas.max()),
          'negative', int((areas <= 0).sum()), flush=True)
    assert (areas > 0).all(), 'candidate grid is not valid in the parameter domain'

    # ---- pull every new node back onto the original rest surface
    tri_mean = triP.mean(axis=1)
    tri_rad = np.linalg.norm(triP - tri_mean[:, None, :], axis=2).max(axis=1)

    def locate(q):
        cand = np.where(np.linalg.norm(tri_mean - q[None, :], axis=1) <= tri_rad + 1e-12)[0]
        for ti in cand:
            a, b, cc = triP[ti]
            v0 = cc - a; v1 = b - a; v2 = q - a
            d00 = v0 @ v0; d01 = v0 @ v1; d11 = v1 @ v1
            d20 = v2 @ v0; d21 = v2 @ v1
            den = d00 * d11 - d01 * d01
            if abs(den) < 1e-18:
                continue
            w = (d11 * d20 - d01 * d21) / den
            v = (d00 * d21 - d01 * d20) / den
            u = 1.0 - v - w
            if u >= -1e-9 and v >= -1e-9 and w >= -1e-9:
                return int(ti), np.array([u, v, w])
        return None, None

    group_names = [g.name for g in ob.vertex_groups]
    gidx = {g.index: g.name for g in ob.vertex_groups}
    Wsrc = np.zeros((NV0, len(group_names)))
    for v in range(NV0):
        for g in ob.data.vertices[v].groups:
            Wsrc[v, group_names.index(gidx[g.group])] = float(g.weight)
    keyblocks = [(kb.name, np.array([tuple(kb.data[i].co) for i in range(NV0)], float) - local0)
                 for kb in ob.data.shape_keys.key_blocks]
    uv_names = [u.name for u in ob.data.uv_layers]
    UVsrc = {u.name: np.array([tuple(u.data[i].uv) for i in range(len(u.data))]) for u in ob.data.uv_layers}

    def interp(ti, bw):
        t0, t1, t2 = roi_tris[ti]
        xyz = bw[0] * local0[t0] + bw[1] * local0[t1] + bw[2] * local0[t2]
        wts = bw[0] * Wsrc[t0] + bw[1] * Wsrc[t1] + bw[2] * Wsrc[t2]
        kd = {nm: bw[0] * d[t0] + bw[1] * d[t1] + bw[2] * d[t2] for nm, d in keyblocks}
        uvs = {nm: bw[0] * U[t0] + bw[1] * U[t1] + bw[2] * U[t2] for nm, U in UVsrc.items()}
        return xyz, wts, kd, uvs, tri_face[ti]

    # ---- assemble
    outside = [i for i in range(NV0) if i not in roi]
    index_old = {v: k for k, v in enumerate(outside)}
    bstart = len(outside)
    bmap = {v: bstart + k for k, v in enumerate(loop)}
    index_old.update(bmap)
    new_start = bstart + len(loop)
    node_index = {}
    for i in range(NU + 1):
        node_index[(i, 0)] = bmap[loop[(c[0] + i) % B]]
    for j in range(NV + 1):
        node_index[(NU, j)] = bmap[loop[(c[1] + j) % B]]
    for i in range(NU + 1):
        node_index[(i, NV)] = bmap[loop[(c[2] + (NU - i)) % B]]
    for j in range(NV + 1):
        node_index[(0, j)] = bmap[loop[(c[3] + (NV - j)) % B]]
    assert len([k for k in node_index]) == (NU + 1) * (NV + 1) - len(interior), 'boundary node bookkeeping'

    Vlocal, Wall, Kall, Uall = [], [], [], []
    for old in outside:
        Vlocal.append(local0[old]); Wall.append(Wsrc[old])
        Kall.append({nm: d[old] for nm, d in keyblocks})
        Uall.append({nm: U[old] for nm, U in UVsrc.items()})
    for v in loop:
        Vlocal.append(local0[v]); Wall.append(Wsrc[v])
        Kall.append({nm: d[v] for nm, d in keyblocks})
        Uall.append({nm: U[v] for nm, U in UVsrc.items()})
    SRC_FACE = {}
    placed = 0
    for kk, (i, j) in enumerate(interior):
        ti, bw = locate(node2[(i, j)])
        assert ti is not None, (i, j, node2[(i, j)])
        xyz, wts, kd, uvs, sf = interp(ti, bw)
        k = new_start + kk
        Vlocal.append(xyz); Wall.append(wts); Kall.append(kd); Uall.append(uvs)
        SRC_FACE[k] = sf
        node_index[(i, j)] = k
        placed += 1
    assert placed == len(interior)

    new_faces = [(node_index[(i, j)], node_index[(i + 1, j)], node_index[(i + 1, j + 1)], node_index[(i, j + 1)])
                 for j in range(NV) for i in range(NU)]
    keepout = set(ifl)
    FACES_NEW = [tuple(index_old[v] for v in faces[fi]) for fi in range(len(faces)) if fi not in keepout]
    FACES_NEW.extend(new_faces)
    assert len(Vlocal) == len(Wall) == new_start + len(interior)
    assert all(len(set(f)) == 4 for f in new_faces)

    old_edges = {tuple(sorted(e)) for fi in ifl for e in zip(faces[fi], faces[fi][1:] + faces[fi][:1])}
    new_edges = {tuple(sorted((a, b))) for f in new_faces for a, b in zip(f, f[1:] + f[:1])}
    max_kept_mm = max(float(np.linalg.norm(Vlocal[index_old[v]] - local0[v]) * 1000) for v in outside + list(loop))

    cmesh = bpy.data.meshes.new('PROBE_TOPOLOGY_GRID')
    cmesh.from_pydata([tuple(x) for x in Vlocal], [], [tuple(f) for f in FACES_NEW])
    cob = ob.copy()
    cob.name = CAND_NAME
    cob.data = cmesh
    bpy.context.scene.collection.objects.link(cob)
    bpy.context.view_layer.update()
    for vg in list(cob.vertex_groups):
        cob.vertex_groups.remove(vg)
    for gn in group_names:
        cob.vertex_groups.new(name=gn)
    for vid in range(len(Vlocal)):
        for gi, w in enumerate(Wall[vid]):
            if abs(w) > 1e-12:
                cob.vertex_groups[gi].add([vid], float(w), 'REPLACE')
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = cob
    cob.select_set(True)
    bpy.ops.object.shape_key_add(from_mix=False)
    for nm, _ in keyblocks:
        if nm == 'Basis':
            continue
        bpy.ops.object.shape_key_add(from_mix=False)
        cmesh.shape_keys.key_blocks[-1].name = nm
    for nm, _ in keyblocks:
        kb = cmesh.shape_keys.key_blocks[nm]
        for vid in range(len(Vlocal)):
            kb.data[vid].co = tuple(np.asarray(Vlocal[vid], float) + Kall[vid][nm])
        kb.slider_min = float(ob.data.shape_keys.key_blocks[nm].slider_min)
        kb.slider_max = float(ob.data.shape_keys.key_blocks[nm].slider_max)
    if ob.data.shape_keys.animation_data:
        cmesh.shape_keys.animation_data_create()
        for src in ob.data.shape_keys.animation_data.drivers:
            dst = cmesh.shape_keys.animation_data.drivers.new(src.data_path)
            dst.driver.expression = src.driver.expression
            for v in src.driver.variables:
                nv = dst.driver.variables.new()
                nv.name = v.name; nv.type = v.type
                t = v.targets[0]; nt = nv.targets[0]
                nt.id = t.id; nt.bone_target = t.bone_target
                nt.transform_type = t.transform_type; nt.rotation_mode = t.rotation_mode
                nt.transform_space = t.transform_space
    for uname in uv_names:
        lyr = cmesh.uv_layers.new(name=uname)
        for vid in range(len(Vlocal)):
            lyr.data[vid].uv = tuple(Uall[vid][uname])
    for mat in ob.data.materials:
        cmesh.materials.append(mat)
    cmesh.update()
    bpy.context.view_layer.update()
    probe_rest = coords(cob)

    return dict(faces=faces, ifl=ifl, loop=loop, c=c, NU=NU, NV=NV, B=B,
                node_index=node_index, bmap=bmap, outside=outside, SRC_FACE=SRC_FACE,
                patch_faces=patch_faces, roi=roi, roi_list=roi_list, load_map=load_map,
                local0=local0, rest=rest, probe_rest=probe_rest, keyblocks=keyblocks,
                group_names=group_names, new_start=new_start, nc=len(interior),
                max_kept_mm=max_kept_mm, FACES_NEW=FACES_NEW, Vlocal=Vlocal,
                us=us, vs=vs, load_max=float(load.max()), flipped=flipped,
                old_edges=old_edges, new_edges=new_edges, cell_min_area=float(areas.min()))


def closest_on_surface(P, V, Tr):
    A = V[Tr[:, 0]]; Bd = V[Tr[:, 1]]; C = V[Tr[:, 2]]
    best = np.full(len(P), 1e18)
    CH = 128
    for s in range(0, len(P), CH):
        p = P[s:s + CH]
        for start in range(0, len(Tr), 256):
            a = A[start:start + 256]; b = Bd[start:start + 256]; cc = C[start:start + 256]
            ab = b - a; ac = cc - a; ap = p[:, None, :] - a[None, :, :]
            d1 = np.einsum('ptc,tc->pt', ap, ab); d2 = np.einsum('ptc,tc->pt', ap, ac)
            e11 = np.einsum('tc,tc->t', ab, ab); e12 = np.einsum('tc,tc->t', ab, ac)
            e22 = np.einsum('tc,tc->t', ac, ac)
            den = e11 * e22 - e12 * e12
            den = np.where(np.abs(den) < 1e-30, 1e-30, den)
            u = np.clip((d1 * e22 - d2 * e12) / den, 0.0, 1.0)
            v = np.clip((d2 * e11 - d1 * e12) / den, 0.0, 1.0)
            ov = (u + v > 1.0)
            u = np.where(ov, 1.0 - v, u)
            cp = a[None, :, :] + u[:, :, None] * ab[None, :, :] + v[:, :, None] * ac[None, :, :]
            d = np.linalg.norm(p[:, None, :] - cp, axis=2)
            best[s:s + CH] = np.minimum(best[s:s + CH], d.min(axis=1))
    return best


def measure(ob, rig, cob, info):
    faces = info['faces']; patch_faces = info['patch_faces']
    Tr_b = np.array([t for fi in sorted(patch_faces) for t in tri_of(faces[fi])])
    ids_b = np.array(PATCH)
    ids_c = np.array(sorted([k for k, sf in info['SRC_FACE'].items() if sf in patch_faces]))
    print('comparison samples: baseline', len(ids_b), 'probe', len(ids_c), flush=True)
    a = info['local0'][Tr_b[:, 0]]; b = info['local0'][Tr_b[:, 1]]; cc = info['local0'][Tr_b[:, 2]]
    area_ref_mm2 = float(np.linalg.norm(np.cross(b - a, cc - a), axis=1).sum() * 0.5) * 1e6

    node_index = info['node_index']; NU, NV = info['NU'], info['NV']
    tris_c = []
    for j in range(NV):
        for i in range(NU):
            q = (node_index[(i, j)], node_index[(i + 1, j)], node_index[(i + 1, j + 1)], node_index[(i, j + 1)])
            if any(info['SRC_FACE'].get(v) in patch_faces for v in q):
                tris_c.extend([(q[0], q[1], q[2]), (q[0], q[2], q[3])])
    Tr_c = np.array(tris_c)
    print('comparison triangles: baseline', len(Tr_b), 'probe', len(Tr_c), flush=True)

    rows = []
    for f in FRAMES:
        motion(rig, f)
        Vb = coords(ob)
        Vc = coords(cob)
        rb = {'frame': f}

        def radius_metrics(V, ids, R0):
            Vv = V[ids]; Vrest = R0[ids]
            Dm = np.linalg.norm(Vv[:, None, :] - Vv[None, :, :], axis=2)
            Rm = np.linalg.norm(Vrest[:, None, :] - Vrest[None, :, :], axis=2)
            mask = (Rm <= RADIUS_MM / 1000.0) & (Rm > 1e-9)
            diff = np.where(mask, np.abs(Dm - Rm) / np.maximum(Rm, 1e-12), 0.0)
            ratio = np.where(mask, Dm / np.maximum(Rm, 1e-12), 0.0)
            pd = diff.max(axis=1); pr = ratio.max(axis=1)
            return {'max_differential_strain': round(float(pd.max()), 4),
                    'p99_differential_strain': round(float(np.percentile(pd, 99)), 4),
                    'max_length_ratio': round(float(pr.max()), 4),
                    'count_length_ratio_above_2x': int((pr > 2.0).sum()),
                    'samples': int(len(ids))}
        rb['baseline'] = radius_metrics(Vb, ids_b, info['rest'])
        rb['probe'] = radius_metrics(Vc, ids_c, info['probe_rest'])
        for side in ('baseline', 'probe'):
            rb[side]['count_above_2x_per_100mm2'] = round(
                rb[side]['count_length_ratio_above_2x'] / area_ref_mm2 * 100.0, 3)
        d_cb = closest_on_surface(Vc[ids_c], Vb, Tr_b)
        d_bc = closest_on_surface(Vb[ids_b], Vc, Tr_c)
        rb['surface_divergence_mm'] = {
            'probe_to_baseline_max': round(float(d_cb.max()) * 1000, 4),
            'probe_to_baseline_mean': round(float(d_cb.mean()) * 1000, 4),
            'baseline_to_probe_max': round(float(d_bc.max()) * 1000, 4),
            'baseline_to_probe_mean': round(float(d_bc.mean()) * 1000, 4),
            'comparison_area_mm2': round(area_ref_mm2, 3)}
        rb['rest_divergence_mm'] = round(float(closest_on_surface(info['probe_rest'][ids_c], info['rest'], Tr_b).max()) * 1000, 6)
        rb['baseline_corrective_value'] = {k.name: float(k.value) for k in ob.data.shape_keys.key_blocks[1:]}
        rb['probe_corrective_value'] = {k.name: float(k.value) for k in cob.data.shape_keys.key_blocks[1:]}
        rows.append(rb)
        print('MEASURE', f, '| base', rb['baseline']['max_length_ratio'], rb['baseline']['count_length_ratio_above_2x'],
              '| probe', rb['probe']['max_length_ratio'], rb['probe']['count_length_ratio_above_2x'],
              '| surfdiv', rb['surface_divergence_mm']['probe_to_baseline_max'],
              '| corr', rb['probe_corrective_value'], flush=True)

    cams = {}
    for f in FRAMES:
        motion(rig, f)
        Vb = coords(ob)
        center = np.mean(Vb[PATCH], axis=0)
        wrist = np.array(rig.matrix_world @ rig.pose.bones['WRIST_R'].head)
        down = (wrist - center) / np.linalg.norm(wrist - center)
        cams[f] = {
            'PALMAR_THENAR_CLOSE': {'center': [float(x) for x in center + down * 0.014],
                                    'direction': DIR_PALMAR, 'ortho_scale_m': 0.110, 'resolution': [960, 880]},
            'FIRST_WEB_OBLIQUE': {'center': [float(x) for x in center],
                                  'direction': DIR_OBLIQUE, 'ortho_scale_m': 0.072, 'resolution': [960, 880]}}
    neutral(rig)
    return rows, cams


def render(ob, rig, cob, cams):
    rr = m.Renderer(cams[FRAMES[0]], 'renders')
    rr.sc.display.shading.shadow_intensity = 0
    records = []
    for f in FRAMES:
        rr.cameras = cams[f]
        for asset, obj in [('BASELINE_FROZEN', ob), ('PROBE_TOPOLOGY', cob)]:
            motion(rig, f)
            V, F = m.evaluate(obj, obj.matrix_world)
            rr.draw(asset, f'F{f:03}', V, F, VIEWS)
            records.extend(rr.records[-2:])
    rr.dispose()
    return records


def main():
    before = protected_inputs()
    verify_inputs(before)
    ob, rig = open_frozen()
    initial_shape = shape_state(ob)
    info = build(ob, rig)
    cob = bpy.data.objects[CAND_NAME]

    design = {
        'phase': PHASE,
        'design_id': 'FIRST_WEB_GRADED_STRUCTURED_BRIDGE_R1',
        'roi': {'patch_vertices': len(PATCH), 'rings_added': RINGS,
                'roi_vertices': len(info['roi']), 'roi_faces': len(info['ifl']),
                'roi_boundary_loop': info['B'], 'roi_euler_characteristic': 1},
        'candidate_grid': {'NU': int(info['NU']), 'NV': int(info['NV']),
                           'new_interior_nodes': int(info['nc']),
                           'roi_nodes_after': int((info['NU'] + 1) * (info['NV'] + 1)),
                           'total_vertices': int(len(info['Vlocal'])),
                           'baseline_vertices': int(len(ob.data.vertices)),
                           'total_faces': int(len(info['FACES_NEW'])),
                           'baseline_faces': int(len(info['faces'])),
                           'all_quads': all(len(f) == 4 for f in info['FACES_NEW']),
                           'interior_valence_all_4': True},
        'structural_changes': [
            'ROI interior rebuilt as ONE NU x NV structured quad grid; the old inner patch boundary line is dissolved',
            'the four grid corners are placed by the ROI boundary chord distribution, so strips do not follow the old layout',
            f'loop spacing graded by the measured six-frame radius-normalised differential strain (GRADE_BLEND={GRADE_BLEND})',
            'interior nodes relaxed in the parameter domain with target spacings taken from the graded parameters'],
        'edge_layout_change': {'old_roi_edges': len(info['old_edges']), 'new_roi_edges': len(info['new_edges']),
                               'edges_shared_with_old_layout': len(info['old_edges'] & info['new_edges'])},
        'rest_surface_identity': {'max_kept_vertex_delta_mm': round(info['max_kept_mm'], 9)},
        'parameterisation': {'weights': 'mean-value (Floater) coordinates computed from the rest geometry only',
                             'boundary': 'ROI loop pinned in order to a convex unit square, chord-length proportional',
                             'flipped_triangles': int(info['flipped']),
                             'min_grid_cell_area_in_domain': round(info['cell_min_area'], 8)},
        'load_field': {'max_radius_normalised_strain': round(info['load_max'], 4),
                       'radius_mm': RADIUS_MM, 'frames_used': FRAMES},
        'grade_samples': {'u': [round(float(x), 5) for x in info['us']],
                          'v': [round(float(x), 5) for x in info['vs']]},
    }
    dump('CANDIDATE_DESIGN_R1.json', design)

    rows, cams = measure(ob, rig, cob, info)
    records = render(ob, rig, cob, cams)

    neutral(rig)
    restore = float(np.linalg.norm(coords(ob) - info['rest'], axis=1).max() * 1000)
    assert restore < 0.001, restore
    assert shape_state(ob) == initial_shape, 'BASELINE SHAPE PAYLOAD CHANGED'
    verify_inputs(before)
    assert sha(BASE) == FROZEN_SHA
    assert digest(action_payload(bpy.data.actions[ACTION])) == APPROVED_ACTION_SHA

    dump('PROBE_MEASUREMENTS_R1.json', {
        'phase': PHASE, 'mode': 'ONE_BOUNDED_STRUCTURAL_PROBE',
        'frozen_baseline_sha256': sha(BASE),
        'action_payload_sha256': digest(action_payload(bpy.data.actions[ACTION])),
        'candidate_object': CAND_NAME, 'baseline_object_untouched': True,
        'design_reference': 'CANDIDATE_DESIGN_R1.json',
        'radius_metric_note': 'pairs within 5 mm in REST space whose both ends lie over the ORIGINAL 149-vertex '
                              'first-web region; counts are also given per 100 mm2 of that same physical region so '
                              'they stay comparable across different vertex budgets.',
        'rows': rows, 'cameras': {str(k): v for k, v in cams.items()}, 'renders': records,
        'ZERO_restore_max_mm': restore})

    bpy.ops.wm.save_as_mainfile(filepath=str(CANDIDATE), compress=True, copy=False)
    print('CANDIDATE_WRITTEN', CANDIDATE.name, sha(CANDIDATE), flush=True)
    print('PROBE_READY')


main()
