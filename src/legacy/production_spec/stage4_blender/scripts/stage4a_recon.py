# STAGE4A -- read-only topology reconnaissance.
#
# Purpose: establish the objective facts needed to decide TOPOLOGY_WORKING_BASE,
#          and to locate joint deformation bands for CON-1 / CON-2 / CON-3.
#
# READ ONLY. Nothing is saved. The L1 level is obtained through the evaluated
# depsgraph (non-destructive), so the source file is never touched.
#
# Anatomical frame used (R1.3.1 correctness, see STAGE1C ... _ERRATA.md):
#   RADIAL = +X   DORSAL = -Y   PALMAR = +Y   DISTAL = -Z   (SOURCE frame, unnormalized)
#
# usage: blender -b RIGHT_HAND_BOOTSTRAP_C1.blend --python stage4a_recon.py -- <out.json>
import bpy, json, sys, math, heapq
from mathutils import Vector, Matrix

TARGET = "Hand  - Realistic"
argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]

ob = bpy.data.objects[TARGET]
mw = ob.matrix_world
LOCAL_OBJ = ob

# Stage-3 measured tip locations (world space) -- used only as SEEDS, the actual
# extremal vertex of each digit is re-derived here.
TIP_SEEDS = {
    "little": Vector((1.3515, 0.0319, 0.1879)),
    "ring":   Vector((1.3933, 0.0320, 0.1599)),
    "middle": Vector((1.4231, 0.0251, 0.1490)),
    "index":  Vector((1.4586, 0.0239, 0.1643)),
    "thumb":  Vector((1.4977, 0.0358, 0.2421)),
}
FINGER_ORDER = ["little", "ring", "middle", "index"]

r3 = lambda v: [round(float(x), 6) for x in v]


# ------------------------------------------------------------------ mesh source
def mesh_arrays(me, mwm):
    """(world verts, edges as index pairs, faces as index tuples)"""
    V = [mwm @ v.co for v in me.vertices]
    E = [tuple(e.vertices) for e in me.edges]
    F = [tuple(p.vertices) for p in me.polygons]
    return V, E, F


BASE_V, BASE_E, BASE_F = mesh_arrays(ob.data, mw)

# evaluated (L1) mesh -- non destructive
dg = bpy.context.evaluated_depsgraph_get()
ob_eval = ob.evaluated_get(dg)
me_l1 = bpy.data.meshes.new_from_object(ob_eval)
L1_V, L1_E, L1_F = mesh_arrays(me_l1, mw)
L1_MODIFIER_LEVEL_USED = 1
L1_INFO = {
    "vertices": len(L1_V), "edges": len(L1_E), "faces": len(L1_F),
    "quads": sum(1 for f in L1_F if len(f) == 4),
    "ngons": sum(1 for f in L1_F if len(f) > 4),
    "tris": sum(len(f) - 2 for f in L1_F),
}

# ------------------------------------------------------------------ anatomical frame
zs = [p.z for p in BASE_V]
# forearm cap = the extreme +Z plateau (the single ngon cap)
zmax = max(zs)
cap_ids = [i for i, p in enumerate(BASE_V) if p.z > zmax - 0.0025]
forearm_center = sum((BASE_V[i] for i in cap_ids), Vector()) / len(cap_ids)
# wrist narrowest slice (Stage-3 value, re-derived here from the vertex plateaus)
wrist_z0 = 0.343
wrist_ids = [i for i, p in enumerate(BASE_V) if abs(p.z - wrist_z0) < 0.0035]
wrist_center = sum((BASE_V[i] for i in wrist_ids), Vector()) / len(wrist_ids)

def nearest_vertex(p, V):
    best, bi = 1e9, -1
    for i, q in enumerate(V):
        d = (q - p).length_squared
        if d < best:
            best, bi = d, i
    return bi, math.sqrt(best)

TIP_V = {}
for name, seed in TIP_SEEDS.items():
    bi, dist = nearest_vertex(seed, BASE_V)
    TIP_V[name] = bi

D_DISTAL = (BASE_V[TIP_V["middle"]] - forearm_center).normalized()
R_RAW = (BASE_V[TIP_V["index"]] - BASE_V[TIP_V["little"]]).normalized()
R_RADIAL = (R_RAW - D_DISTAL * R_RAW.dot(D_DISTAL)).normalized()
DORSAL = D_DISTAL.cross(R_RADIAL).normalized()
PALMAR = -DORSAL

FRAME_CHECK = {
    "D_distal": r3(D_DISTAL), "R_radial": r3(R_RADIAL),
    "DORSAL": r3(DORSAL), "PALMAR": r3(PALMAR),
    "D_distal_dot_-Z": round(D_DISTAL.z, 4),
    "R_radial_dot_+X": round(R_RADIAL.x, 4),
    "DORSAL_dot_-Y": round(DORSAL.y, 4),
    "PALMAR_dot_+Y": round(PALMAR.y, 4),
    "frame_matches_expected_source": bool(D_DISTAL.z < -0.8 and R_RADIAL.x > 0.8 and DORSAL.y < -0.8),
}

ORIGIN_REF = forearm_center  # reference point for the anatomical coordinate readout


def anat(p):
    d = p - ORIGIN_REF
    return {"t": round(d.dot(D_DISTAL), 6), "r": round(d.dot(R_RADIAL), 6), "n": round(d.dot(DORSAL), 6)}


# ------------------------------------------------------------------ graph helpers
def adjacency(V, E):
    adj = [[] for _ in V]
    for a, b in E:
        L = (V[a] - V[b]).length
        adj[a].append((b, L))
        adj[b].append((a, L))
    return adj


def multi_source_dijkstra(V, E, sources):
    """sources: list of (name, vertex_index). Returns (label per vertex, dist)."""
    adj = adjacency(V, E)
    dist = [float("inf")] * len(V)
    lab = [None] * len(V)
    pq = []
    for name, i in sources:
        dist[i] = 0.0
        lab[i] = name
        heapq.heappush(pq, (0.0, i))
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u] + 1e-12:
            continue
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v] - 1e-15:
                dist[v] = nd
                lab[v] = lab[u]
                heapq.heappush(pq, (nd, v))
    return lab, dist


def valence(V, E):
    val = [0] * len(V)
    for a, b in E:
        val[a] += 1
        val[b] += 1
    return val


def edge_face_degrees(F, nv):
    """number of faces touching each edge (manifold test)"""
    key = {}
    for fi, f in enumerate(F):
        n = len(f)
        for i in range(n):
            a, b = f[i], f[(i + 1) % n]
            k = (a, b) if a < b else (b, a)
            key[k] = key.get(k, 0) + 1
    return key


# ------------------------------------------------------------------ digit segmentation
SOURCES = [("wrist", wrist_ids[0])] + [(n, TIP_V[n]) for n in TIP_V]
LABEL, GEOD = multi_source_dijkstra(BASE_V, BASE_E, SOURCES)


def digit_vertices(lab, name):
    return [i for i, l in enumerate(lab) if l == name]


# ------------------------------------------------------------------ per-digit ring analysis
def analyse_digit(V, E, ids, tip_idx, name):
    idset = set(ids)
    sub_edges = [(a, b) for a, b in E if a in idset and b in idset]
    sub_faces = [f for f in [] ]  # not needed
    tip = V[tip_idx]
    cen = sum((V[i] for i in ids), Vector()) / len(ids)
    # PCA major axis, oriented distally (toward the tip)
    pts = [V[i] - cen for i in ids]
    M = Matrix(((0, 0, 0), (0, 0, 0), (0, 0, 0)))
    for p in pts:
        for r in range(3):
            for c in range(3):
                M[r][c] += p[r] * p[c]
    # power iteration for the dominant eigenvector
    a = Vector((0.3, 0.5, 0.81)).normalized()
    for _ in range(60):
        a = Vector((sum(M[r][c] * a[c] for c in range(3)) for r in range(3)))
        if a.length < 1e-14:
            break
        a.normalize()
    if a.dot(tip - cen) < 0:
        a = -a
    axis = a

    t_tip = {i: (tip - V[i]).dot(axis) for i in ids}   # 0 at tip, grows proximally
    tmax = max(t_tip.values())

    # centreline by axial binning -> locally varying tangent (handles finger curvature)
    NB = 48
    bins = [[] for _ in range(NB)]
    for i in ids:
        b = min(NB - 1, max(0, int(t_tip[i] / max(tmax, 1e-9) * (NB - 1e-6))))
        bins[b].append(i)
    centers, tval = [], []
    for b in range(NB):
        if bins[b]:
            centers.append(sum((V[i] for i in bins[b]), Vector()) / len(bins[b]))
            tval.append(sum(t_tip[i] for i in bins[b]) / len(bins[b]))
    # smooth
    def smooth(seq, k=2):
        out = []
        for i in range(len(seq)):
            lo, hi = max(0, i - k), min(len(seq), i + k + 1)
            out.append(sum(seq[lo:hi], Vector()) / (hi - lo))
        return out
    if len(centers) >= 3:
        centers = smooth(centers)
    tang = []
    for i in range(len(centers)):
        if i == 0:
            d = centers[min(1, len(centers) - 1)] - centers[0]
        elif i == len(centers) - 1:
            d = centers[-1] - centers[-2]
        else:
            d = centers[i + 1] - centers[i - 1]
        d = -d.normalized()  # tangent pointing PROXIMALLY (direction of increasing t)
        tang.append(d)

    def local_tangent(i):
        if not centers:
            return axis
        t = t_tip[i]
        # nearest bin
        best, bi = 1e9, 0
        for k, tv in enumerate(tval):
            if abs(tv - t) < best:
                best, bi = abs(tv - t), k
        return tang[bi]

    # ring detection: transverse edges = components of edges running around the axis
    THRESH = 0.45  # |cos| < 0.45  ->  > 63 deg from the local axis = circumferential
    trans = []
    for a, b in sub_edges:
        d = (V[a] - V[b]).normalized()
        ax = (local_tangent(a) + local_tangent(b)).normalized()
        if abs(d.dot(ax)) < THRESH:
            trans.append((a, b))
    # union-find over the transverse edges
    parent = {}
    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(x, y):
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[rx] = ry
    for a, b in trans:
        union(a, b)
    comps = {}
    for a, b in trans:
        comps.setdefault(find(a), set()).update((a, b))

    rings = []
    for _, vs in comps.items():
        vs = sorted(vs)
        tt = [t_tip[i] for i in vs]
        c = sum((V[i] for i in vs), Vector()) / len(vs)
        rad = sum((V[i] - c).length for i in vs) / len(vs)
        # closedness: every vertex should carry exactly 2 transverse edges
        deg = {i: 0 for i in vs}
        for a, b in trans:
            if a in deg:
                deg[a] += 1
            if b in deg:
                deg[b] += 1
        closed = all(v == 2 for v in deg.values())
        rings.append({
            "t_from_tip_mm": round(sum(tt) / len(tt) * 1000, 3),
            "t_span_mm": round((max(tt) - min(tt)) * 1000, 3),
            "n_verts": len(vs),
            "mean_radius_mm": round(rad * 1000, 3),
            "closed_loop": bool(closed),
            "centroid": r3(c),
            "verts": vs,
        })
    rings.sort(key=lambda r: r["t_from_tip_mm"])

    # --- geodesic distance from the tip, restricted to this digit's sub-mesh
    gadj = {}
    for a, b in sub_edges:
        gadj.setdefault(a, []).append(b)
        gadj.setdefault(b, []).append(a)
    gd = {tip_idx: 0.0}
    pq = [(0.0, tip_idx)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > gd.get(u, 1e18) + 1e-12:
            continue
        for v in gadj.get(u, ()):
            nd = d + (V[u] - V[v]).length
            if nd < gd.get(v, 1e18) - 1e-15:
                gd[v] = nd
                heapq.heappush(pq, (nd, v))
    for rr in rings:
        gg = [gd[i] for i in rr["verts"] if i in gd]
        rr["geod_from_tip_mm"] = round(sum(gg) / len(gg) * 1000, 3) if gg else None

    # spacing
    for k in range(1, len(rings)):
        rr = rings[k]
        rr["gap_from_prev_mm"] = round(rr["t_from_tip_mm"] - rings[k - 1]["t_from_tip_mm"], 3)
        a0, a1 = rings[k - 1].get("geod_from_tip_mm"), rr.get("geod_from_tip_mm")
        rr["geod_gap_mm"] = round(a1 - a0, 3) if (a0 is not None and a1 is not None) else None
    if rings:
        rings[0]["gap_from_prev_mm"] = None
        rings[0]["geod_gap_mm"] = None

    # --- centreline curvature along the digit: the REAL bending zones
    closed = [r for r in rings if r["closed_loop"] and r["n_verts"] >= 8
              and r.get("geod_from_tip_mm") is not None]
    closed.sort(key=lambda r: r["geod_from_tip_mm"])
    cen = [Vector(r["centroid"]) for r in closed]
    # light smoothing (centroid of a low-poly ring is noisy)
    if len(cen) >= 5:
        sm = []
        for k in range(len(cen)):
            lo, hi = max(0, k - 1), min(len(cen), k + 2)
            sm.append(sum(cen[lo:hi], Vector()) / (hi - lo))
        cen = sm
    curvature = []
    for k in range(1, len(cen) - 1):
        v1, v2 = cen[k] - cen[k - 1], cen[k + 1] - cen[k]
        if v1.length < 1e-9 or v2.length < 1e-9:
            continue
        ang = v1.angle(v2)
        ds = (v1.length + v2.length) / 2
        curvature.append({
            "ring_geod_mm": closed[k]["geod_from_tip_mm"],
            "turn_deg": round(math.degrees(ang), 4),
            "seg_len_mm": round(ds * 1000, 3),
            "kappa_1_per_m": round(ang / ds, 2),
        })
    joint_candidates = []
    for k in range(1, len(curvature) - 1):
        a, b, c = (curvature[k - 1]["kappa_1_per_m"], curvature[k]["kappa_1_per_m"],
                   curvature[k + 1]["kappa_1_per_m"])
        if b > a and b > c:
            joint_candidates.append({
                "geod_from_tip_mm": curvature[k]["ring_geod_mm"],
                "kappa_1_per_m": b,
                "prominence_1_per_m": round(b - max(a, c), 2),
                "local_turn_deg": round(sum(x["turn_deg"] for x in curvature[max(0, k - 1):k + 2]), 4),
            })

    # crease detection on the closed-ring radius profile
    minima = []
    for k in range(1, len(closed) - 1):
        a, b, c = (closed[k - 1]["mean_radius_mm"], closed[k]["mean_radius_mm"],
                   closed[k + 1]["mean_radius_mm"])
        if b < a and b < c:
            minima.append({"geod_from_tip_mm": closed[k]["geod_from_tip_mm"],
                           "radius_mm": b,
                           "notch_depth_mm": round(min(a, c) - b, 3)})

    return {
        "digit": name,
        "vertex_count": len(ids),
        "tip_vertex": tip_idx,
        "tip_world": r3(tip),
        "axis": r3(axis),
        "axial_extent_mm": round(tmax * 1000, 3),
        "closed_ring_count": len(closed),
        "ring_geod_span_mm": ([closed[0]["geod_from_tip_mm"], closed[-1]["geod_from_tip_mm"]] if closed else None),
        "ring_geod_spacing_mm": (None if len(closed) < 2 else
                                 [round(closed[k]["geod_from_tip_mm"] - closed[k - 1]["geod_from_tip_mm"], 3)
                                  for k in range(1, len(closed))]),
        "joint_candidates": joint_candidates,
        "radius_minima": minima,
        "curvature_profile": curvature,
        "ring_count": len(rings),
        "rings": rings,
    }


# ------------------------------------------------------------------ poles
def pole_census(V, E, label, name):
    val = valence(V, E)
    ef = edge_face_degrees([], len(V))
    out = []
    counts = {}
    for i, k in enumerate(val):
        counts[k] = counts.get(k, 0) + 1
        if k != 4:
            out.append({
                "vertex": i,
                "valence": k,
                "digit": label[i],
                "world": r3(V[i]),
                "anat": anat(V[i]),
            })
    return {"mesh": name, "valence_histogram": {str(k): v for k, v in sorted(counts.items())},
            "extraordinary_count": len(out), "extraordinary": out}


def topology_integrity(V, E, F, name):
    ef = {}
    for f in F:
        n = len(f)
        for i in range(n):
            a, b = f[i], f[(i + 1) % n]
            k = (a, b) if a < b else (b, a)
            ef[k] = ef.get(k, 0) + 1
    nonman = sum(1 for k, v in ef.items() if v > 2)
    bound = sum(1 for k, v in ef.items() if v == 1)
    val = valence(V, E)
    return {"mesh": name, "verts": len(V), "edges": len(E), "faces": len(F),
            "nonmanifold_edges": nonman, "boundary_edges": bound,
            "loose_verts": sum(1 for k in val if k == 0),
            "tris": sum(len(f) - 2 for f in F)}


# ------------------------------------------------------------------ run
BL1, GL1 = multi_source_dijkstra(L1_V, L1_E, [("wrist", wrist_ids[0])] +
                                 [(n, nearest_vertex(TIP_SEEDS[n], L1_V)[0]) for n in TIP_SEEDS])

RESULT = {
    "stage": "STAGE4A_RECON",
    "asset": TARGET,
    "runtime": {"blender": bpy.app.version_string,
                "build_hash": (bpy.app.build_hash.decode() if isinstance(bpy.app.build_hash, bytes) else str(bpy.app.build_hash))},
    "frame": FRAME_CHECK,
    "forearm_center_world": r3(forearm_center),
    "wrist_center_world": r3(wrist_center),
    "tip_vertices": {n: {"vertex": TIP_V[n], "world": r3(BASE_V[TIP_V[n]])} for n in TIP_V},
    "integrity": {
        "base": topology_integrity(BASE_V, BASE_E, BASE_F, "BASE"),
        "L1": topology_integrity(L1_V, L1_E, L1_F, "L1"),
    },
    "L1_derived": L1_INFO,
    "poles": {
        "base": pole_census(BASE_V, BASE_E, LABEL, "BASE"),
        "L1": pole_census(L1_V, L1_E, BL1, "L1"),
    },
    "digits_base": {},
    "digits_L1": {},
}

# ------------------------------------------------------------------ web notches & joint bands
def geo_from(V, E, src):
    adj = adjacency(V, E)
    dist = [float("inf")] * len(V)
    dist[src] = 0.0
    pq = [(0.0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u] + 1e-12:
            continue
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v] - 1e-15:
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    return dist


WRIST_V = wrist_ids[0]
GW_BASE = geo_from(BASE_V, BASE_E, WRIST_V)
GW_L1 = geo_from(L1_V, L1_E, nearest_vertex(BASE_V[WRIST_V], L1_V)[0])

THUMB_ROOT_SEED = Vector((1.4489, 0.0115, 0.3134))   # Stage-3 measured thumb root
CLEFTS = [("index", "middle"), ("middle", "ring"), ("ring", "little"), ("index", "thumb")]


def cleft_apex(V, E, lab, a, b, gw):
    """Most DISTAL vertex on the Voronoi ridge between two digit labels
    = the web commissure apex (anatomical MCP level).
    'Distal' is measured on the anatomical distal axis (not on wrist geodesics),
    because the ridge also runs proximally into the palm/forearm."""
    adj = adjacency(V, E)
    ridge = []
    for u in range(len(V)):
        if lab[u] not in (a, b):
            continue
        for v, _w in adj[u]:
            if lab[v] in (a, b) and lab[v] != lab[u]:
                ridge.append(u)
                break
    ridge = sorted(set(ridge))
    if not ridge:
        return None, []
    scored = sorted((( (V[u] - ORIGIN_REF).dot(D_DISTAL), u) for u in ridge), reverse=True)
    top = [{"vertex": u, "distal_mm": round(d * 1000, 3), "world": r3(V[u]),
            "wrist_geod_mm": round(gw[u] * 1000, 3)} for d, u in scored[:5]]
    return scored[0][1], top


NOTCHES = {}
for a, b in CLEFTS:
    vi, top = cleft_apex(BASE_V, BASE_E, LABEL, a, b, GW_BASE)
    NOTCHES[f"{a}-{b}"] = {"vertex": vi, "world": r3(BASE_V[vi]),
                           "wrist_geod_mm": round(GW_BASE[vi] * 1000, 3),
                           "ridge_vertex_count": None, "top5_most_distal": top}

FINGER_CLEFTS = {
    "index": ["index-middle"],
    "middle": ["index-middle", "middle-ring"],
    "ring": ["middle-ring", "ring-little"],
    "little": ["ring-little"],
}

GT_BASE = {nm: geo_from(BASE_V, BASE_E, TIP_V[nm]) for nm in TIP_V}
GT_L1 = {}
for nm in TIP_V:
    tv = nearest_vertex(TIP_SEEDS[nm], L1_V)[0]
    GT_L1[nm] = geo_from(L1_V, L1_E, tv)

# thumb CMC anchor = thumb root vertex
_thr_b, _ = nearest_vertex(THUMB_ROOT_SEED, BASE_V)
_thr_l1, _ = nearest_vertex(BASE_V[_thr_b], L1_V)


def anchors_for(nm, gt, is_l1):
    """joint -> (geodesic distance from own tip, band half width) in mm"""
    if nm == "thumb":
        cv = _thr_l1 if is_l1 else _thr_b
        Lc = gt[cv] * 1000.0
        return {
            "THUMB_CMC": (Lc, max(7.0, 0.10 * Lc)),
            "THUMB_MCP": (0.56 * Lc, max(7.0, 0.10 * Lc)),
            "THUMB_IP": (0.25 * Lc, max(6.0, 0.09 * Lc)),
        }, Lc
    clefts = FINGER_CLEFTS[nm]
    vals = []
    for c in clefts:
        nv = NOTCHES[c]["vertex"]
        if is_l1:
            nv = nearest_vertex(BASE_V[nv], L1_V)[0]
        vals.append(gt[nv] * 1000.0)
    L = sum(vals) / len(vals)
    h = max(7.0, 0.10 * L)
    return {
        f"{nm.upper()}_MCP": (L, h),
        f"{nm.upper()}_PIP": (0.54 * L, h),
        f"{nm.upper()}_DIP": (0.23 * L, max(6.0, 0.09 * L)),
    }, L


def bands_for(dd, anchors):
    rings = [r for r in dd["rings"]
             if r["closed_loop"] and r["n_verts"] >= 8 and r.get("geod_from_tip_mm") is not None]
    out = {}
    for jn, (c, h) in anchors.items():
        sel = [r for r in rings if abs(r["geod_from_tip_mm"] - c) <= h]
        sel.sort(key=lambda r: r["geod_from_tip_mm"])
        out[jn] = {
            "joint_center_geod_mm": round(c, 3),
            "band_half_width_mm": round(h, 3),
            "effective_loop_count": len(sel),
            "loops": [{"geod_from_tip_mm": r["geod_from_tip_mm"], "n_verts": r["n_verts"],
                       "radius_mm": r["mean_radius_mm"]} for r in sel],
        }
    return out


DIG_BASE, DIG_L1 = {}, {}
for nm in FINGER_ORDER + ["thumb"]:
    ids = digit_vertices(LABEL, nm)
    if ids:
        DIG_BASE[nm] = analyse_digit(BASE_V, BASE_E, ids, TIP_V[nm], nm)
    ids1 = [i for i, l in enumerate(BL1) if l == nm]
    if ids1:
        t1 = nearest_vertex(TIP_SEEDS[nm], L1_V)[0]
        DIG_L1[nm] = analyse_digit(L1_V, L1_E, ids1, t1, nm)

ANCH_BASE, ANCH_L1, LEN_BASE, LEN_L1 = {}, {}, {}, {}
for nm in DIG_BASE:
    if nm in DIG_L1:
        ab, Lb = anchors_for(nm, GT_BASE[nm], False)
        al, Ll = anchors_for(nm, GT_L1[nm], True)
        ANCH_BASE[nm], LEN_BASE[nm] = ab, Lb
        ANCH_L1[nm], LEN_L1[nm] = al, Ll
        DIG_BASE[nm]["joint_bands"] = bands_for(DIG_BASE[nm], ab)
        DIG_BASE[nm]["functional_length_mm"] = round(Lb, 3)
        DIG_L1[nm]["joint_bands"] = bands_for(DIG_L1[nm], al)
        DIG_L1[nm]["functional_length_mm"] = round(Ll, 3)

RESULT["digits_base"] = DIG_BASE
RESULT["digits_L1"] = DIG_L1
RESULT["web_notches"] = NOTCHES
RESULT["thumb_root_seed"] = r3(THUMB_ROOT_SEED)
RESULT["thumb_root_vertex"] = {"base": _thr_b, "world": r3(BASE_V[_thr_b])}

# strip giant vert lists from the persisted rings (keep counts only)
for grp in ("digits_base", "digits_L1"):
    for nm, d in RESULT[grp].items():
        for rr in d["rings"]:
            rr.pop("verts", None)

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(RESULT, f, ensure_ascii=False, indent=1)

# ------------------------------------------------------------------ console summary
print("=" * 78)
print("FRAME OK  :", FRAME_CHECK["frame_matches_expected_source"], FRAME_CHECK["D_distal"], FRAME_CHECK["DORSAL"])
print("INTEGRITY :", json.dumps(RESULT["integrity"]))
print("L1 DERIVED:", json.dumps(L1_INFO))
for grp in ("base", "L1"):
    p = RESULT["poles"][grp]
    print(f"POLES {grp:5s}: extraordinary={p['extraordinary_count']}  hist={p['valence_histogram']}")
for grp in ("digits_base", "digits_L1"):
    print("-" * 78)
    print(grp)
    for nm, d in RESULT[grp].items():
        rs = d["rings"]
        print(f"  {nm:7s} verts={d['vertex_count']:5d} extent={d['axial_extent_mm']:7.1f}mm rings={d['ring_count']}")
        row = []
        for rr in rs:
            row.append(f"{rr['t_from_tip_mm']:.0f}({rr['n_verts']}{'c' if rr['closed_loop'] else '!'})")
        print("     ", " ".join(row))
print("WROTE", OUT)
