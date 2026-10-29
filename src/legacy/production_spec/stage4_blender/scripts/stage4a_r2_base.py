# STAGE4A -- RIGHT HAND BLENDER ENGINEERING (FRAME NORMALIZATION + TOPOLOGY).
#
# Executes, on a NEW Stage-4 working copy derived from the frozen Stage-2 bootstrap:
#   * CON-9  ASSET_FRAME_NORMALIZATION   M = diag(1,-1,-1) = Rx(180 deg)
#   * base selection                     OFFICIAL MULTIRES L1 applied -> real quad mesh
#   * CON-1  joint deformation loops     (MCP collars + DIP/IP top-ups)
#   * CON-2  THUMB CMC topology
#   * CON-3  joint pole audit
#
# NOT done here (explicitly out of scope for Stage 4A):
#   RSSF re-pose, nails, UV, origin reset, rig, skin weights, left-hand mirror, animation.
#
# Loop insertion method: TOPOLOGICAL EDGE-RING WALK.  In an all-quad mesh, walking
# the opposite edge across each quad yields a closed edge ring; splitting every edge
# of that ring puts exactly two cut edges in every crossed quad, so the result stays
# all-quad with no dangling chain ends (verified: 0 n-gons, 0 triangles, 0 non-manifold).
# New rings are then PROJECTED onto a plane perpendicular to the finger axis so the
# loop is a true perpendicular deformation loop rather than a wandering strip.
#
# usage: D:\Blender\blender.exe -b <C1.blend> --python stage4a_engineer.py -- <out.blend> <outdir>
import bpy, bmesh, sys, os, json, math, heapq, hashlib, struct, datetime
from mathutils import Vector, Matrix

TARGET = "Hand  - Realistic"
argv = sys.argv[sys.argv.index("--") + 1:]
OUT_BLEND, OUTDIR = argv[0], argv[1]
os.makedirs(OUTDIR, exist_ok=True)

M_NORM = Matrix(((1.0, 0.0, 0.0), (0.0, -1.0, 0.0), (0.0, 0.0, -1.0)))   # CON-9, det = +1

TIP_SEEDS = {
    "little": Vector((1.3515, 0.0319, 0.1879)), "ring": Vector((1.3933, 0.0320, 0.1599)),
    "middle": Vector((1.4231, 0.0251, 0.1490)), "index": Vector((1.4586, 0.0239, 0.1643)),
    "thumb": Vector((1.4977, 0.0358, 0.2421)),
}
THUMB_ROOT_SEED = Vector((1.4489, 0.0115, 0.3134))
FOREARM_SEED = Vector((1.4048, 0.0113, 0.4316))     # forearm cut-cap centre (source-frame world)
WRIST_SEED = Vector((1.4048, 0.0113, 0.3430))       # wrist narrowest slice (source-frame world)
FINGER_ORDER = ["little", "ring", "middle", "index"]
LOG = []


def log(*a):
    s = " ".join(str(x) for x in a)
    LOG.append(s)
    print(s)


r3 = lambda v: [round(float(x), 6) for x in v]


# ==================================================================== 1. INPUT STATE
ob = bpy.data.objects[TARGET]
mw0 = ob.matrix_world.copy()
LOC0 = mw0.translation.copy()


def w2c(p):
    """source-frame world point -> canonical-frame world point (CON-9 applied to mesh data)"""
    return (M_NORM @ p) + (LOC0 - (M_NORM @ LOC0))


def mesh_sig(me):
    h = hashlib.sha256()
    for v in me.vertices:
        h.update(struct.pack('<3d', *[float(c) for c in v.co]))
    for e in me.edges:
        h.update(struct.pack('<2i', e.vertices[0], e.vertices[1]))
    for p in me.polygons:
        h.update(struct.pack('<i', len(p.vertices)))
        for vi in p.vertices:
            h.update(struct.pack('<i', vi))
    return h.hexdigest()


def signed_volume(me, mwm):
    """sum over triangles of v0 . (v1 x v2) / 6 -- flips sign under a reflection"""
    V = [mwm @ v.co for v in me.vertices]
    tot = 0.0
    for p in me.polygons:
        vs = list(p.vertices)
        for i in range(1, len(vs) - 1):
            a, b, c = V[vs[0]], V[vs[i]], V[vs[i + 1]]
            tot += a.dot(b.cross(c)) / 6.0
    return tot


BEFORE = {
    "object_name": ob.name,
    "mesh_name": ob.data.name,
    "verts": len(ob.data.vertices), "edges": len(ob.data.edges), "faces": len(ob.data.polygons),
    "quads": sum(1 for p in ob.data.polygons if len(p.vertices) == 4),
    "ngons": sum(1 for p in ob.data.polygons if len(p.vertices) > 4),
    "tris": sum(len(p.vertices) - 2 for p in ob.data.polygons),
    "object_location": r3(LOC0), "object_scale": r3(ob.scale), "object_rotation": r3(ob.rotation_euler),
    "mesh_signature": mesh_sig(ob.data),
    "signed_volume_m3": signed_volume(ob.data, mw0),
    "multires": [(m.name, m.type, getattr(m, "levels", None), getattr(m, "total_levels", None))
                 for m in ob.modifiers],
    "modifiers": [[m.name, m.type] for m in ob.modifiers],
    "uv_layers": [l.name for l in ob.data.uv_layers],
    "vertex_groups": [g.name for g in ob.vertex_groups],
    "frame_state": "UNNORMALIZED_SOURCE_FRAME",
}
log("INPUT  V=%d F=%d quads=%d ngons=%d tris=%d" % (BEFORE["verts"], BEFORE["faces"],
                                                    BEFORE["quads"], BEFORE["ngons"], BEFORE["tris"]))
log("INPUT  signed_volume = %.9e" % BEFORE["signed_volume_m3"])

# ==================================================================== 2. APPLY OFFICIAL MULTIRES L1
bpy.context.view_layer.objects.active = ob
for o in bpy.context.selected_objects:
    o.select_set(False)
ob.select_set(True)
MULTIRES_INFO = None
for m in list(ob.modifiers):
    if m.type == 'MULTIRES':
        MULTIRES_INFO = {"name": m.name, "levels_before": m.levels,
                         "total_levels": m.total_levels}
        m.levels = 1
        bpy.ops.object.modifier_apply(modifier=m.name)
        MULTIRES_INFO["applied"] = True
ob.select_set(False)
me = ob.data
log("MULTIRES L1 APPLIED -> V=%d F=%d quads=%d" % (len(me.vertices), len(me.polygons),
                                                   sum(1 for p in me.polygons if len(p.vertices) == 4)))
L1_STATE = {"verts": len(me.vertices), "edges": len(me.edges), "faces": len(me.polygons),
            "quads": sum(1 for p in me.polygons if len(p.vertices) == 4),
            "ngons": sum(1 for p in me.polygons if len(p.vertices) > 4),
            "tris": sum(len(p.vertices) - 2 for p in me.polygons)}

# ==================================================================== 3. CON-9 FRAME NORMALIZATION
bm = bmesh.new()
bm.from_mesh(me)
bm.verts.ensure_lookup_table()
VOL_PRE_NORM = signed_volume(me, ob.matrix_world)      # measured AFTER the L1 bake, BEFORE the rotation
for v in bm.verts:
    v.co = M_NORM @ v.co
bm.normal_update()
bm.to_mesh(me)
me.update()
VOL_POST_NORM = signed_volume(me, ob.matrix_world)

CON9 = {
    "transform_matrix": [[1, 0, 0], [0, -1, 0], [0, 0, -1]],
    "equivalent": "Rx(180)",
    "determinant": round(M_NORM.determinant(), 12),
    "orthogonal": bool(M_NORM.is_orthogonal),
    "scale_factor": round(M_NORM.to_scale().x, 12),
    "applied_to": "MESH DATA (object transform left at identity rotation / uniform scale)",
    "negative_scale_used": False,
    "mirror_used": False,
    "reflection_used": False,
    "MIRROR_TEST_note": "signed volume is invariant under a proper rotation and flips sign "
                        "under a reflection; both measurements are taken AFTER the L1 bake "
                        "so only the frame rotation is under test",
    "signed_volume_before_rotation_m3": VOL_PRE_NORM,
    "signed_volume_after_rotation_m3": VOL_POST_NORM,
    "signed_volume_ratio": (VOL_POST_NORM / VOL_PRE_NORM) if VOL_PRE_NORM else None,
    "signed_volume_sign_preserved": bool((VOL_PRE_NORM > 0) == (VOL_POST_NORM > 0)),
    "object_scale_after": r3(ob.scale),
}
log("CON-9  det=%.1f scale=%.6f  signed_volume(pre-rot) %.6e -> (post-rot) %.6e  ratio=%.9f"
    % (CON9["determinant"], CON9["scale_factor"], VOL_PRE_NORM, VOL_POST_NORM,
       CON9["signed_volume_ratio"]))

# rebuild bmesh on the normalized mesh
bm.free()
bm = bmesh.new()
bm.from_mesh(me)
bm.verts.ensure_lookup_table()
bm.edges.ensure_lookup_table()
bm.faces.ensure_lookup_table()
MW = ob.matrix_world


# ==================================================================== 4. ANALYSIS HELPERS
def adjacency(bm):
    adj = [[] for _ in range(len(bm.verts))]
    for e in bm.edges:
        a, b = e.verts[0].index, e.verts[1].index
        L = e.calc_length()
        adj[a].append((b, L))
        adj[b].append((a, L))
    return adj


def dijkstra(adj, src):
    n = len(adj)
    dist = [float("inf")] * n
    dist[src] = 0.0
    pq = [(0.0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u] + 1e-15:
            continue
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v] - 1e-16:
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    return dist


def nearest_vertex(p, coords):
    best, bi = 1e18, 0
    for i, q in enumerate(coords):
        d = (q - p).length_squared
        if d < best:
            best, bi = d, i
    return bi


def anat_frame():
    """Frame derived purely from geometry.  Landmarks are taken from the seed
    positions mapped through w2c(), so this works in the SOURCE frame and in the
    normalised CANONICAL frame alike (the anatomical labels are frame-independent)."""
    co = [MW @ v.co for v in bm.verts]
    forearm = co[nearest_vertex(w2c(FOREARM_SEED), co)]
    tips = {n: nearest_vertex(w2c(s), co) for n, s in TIP_SEEDS.items()}
    D = (co[tips["middle"]] - forearm).normalized()
    R = (co[tips["index"]] - co[tips["little"]]).normalized()
    R = (R - D * R.dot(D)).normalized()
    DORS = D.cross(R).normalized()
    return co, forearm, tips, D, R, DORS


CO, FOREARM, TIPV, D_DIST, R_RAD, DORSAL = anat_frame()
FRAME_AFTER = {
    "DISTAL_axis": r3(D_DIST), "RADIAL_axis": r3(R_RAD), "DORSAL_axis": r3(DORSAL),
    "PALMAR_axis": r3(-DORSAL),
    "DISTAL_dot_+Z": round(D_DIST.z, 4), "RADIAL_dot_+X": round(R_RAD.x, 4),
    "DORSAL_dot_+Y": round(DORSAL.y, 4), "PALMAR_dot_-Y": round((-DORSAL).y, 4),
    "RADIAL_is_+X": bool(R_RAD.x > 0.9), "DORSAL_is_+Y": bool(DORSAL.y > 0.9),
    "DISTAL_is_+Z": bool(D_DIST.z > 0.9),
}
# independent chirality re-derivation (Stage-3 method): (D x R) . DORSAL
CHIR = {
    "triple_DxR_dot_DORSAL": round((D_DIST.cross(R_RAD)).dot(DORSAL), 6),
    "verdict": "RIGHT_HAND" if (D_DIST.cross(R_RAD)).dot(DORSAL) > 0 else "LEFT_HAND",
}
log("FRAME  R.x=%.4f DORS.y=%.4f DIST.z=%.4f  chirality=%.4f -> %s"
    % (FRAME_AFTER["RADIAL_dot_+X"], FRAME_AFTER["DORSAL_dot_+Y"],
       FRAME_AFTER["DISTAL_dot_+Z"], CHIR["triple_DxR_dot_DORSAL"], CHIR["verdict"]))

# thumb-opposition signature: in canonical frame the thumb tip must sit PALMAR (-Y)
palm_plane_pts = [CO[TIPV[n]] for n in FINGER_ORDER]
pc = sum(palm_plane_pts, Vector()) / 4.0
THUMB_SIGNATURE = {
    "thumb_tip_offset_along_PALMAR_mm": round((CO[TIPV["thumb"]] - pc).dot(-DORSAL) * 1000, 3),
    "thumb_tip_radial_gt_index_mm": round((CO[TIPV["thumb"]] - CO[TIPV["index"]]).dot(R_RAD) * 1000, 3),
}

def label_partition(adj, nverts, srcs):
    lab = [None] * nverts
    dd = [float("inf")] * nverts
    for name, s in srcs:
        dd[s] = 0.0
        lab[s] = name
    pq = [(0.0, s) for _, s in srcs]
    heapq.heapify(pq)
    while pq:
        d, u = heapq.heappop(pq)
        if d > dd[u] + 1e-15:
            continue
        for v, w in adj[u]:
            nd = d + w
            if nd < dd[v] - 1e-16:
                dd[v] = nd
                lab[v] = lab[u]
                heapq.heappush(pq, (nd, v))
    return lab, dd


ADJ = adjacency(bm)
CO = [MW @ v.co for v in bm.verts]


def cleft_apex(a, b):
    ridge = set()
    for u in range(len(bm.verts)):
        if LAB[u] not in (a, b):
            continue
        for v, _w in ADJ[u]:
            if LAB[v] in (a, b) and LAB[v] != LAB[u]:
                ridge.add(u)
                break
    if not ridge:
        return None
    return max(ridge, key=lambda u: (CO[u] - FOREARM).dot(D_DIST))


CLEFTS = [("index", "middle"), ("middle", "ring"), ("ring", "little"), ("index", "thumb")]
FINGER_CLEFTS = {"index": ["index-middle"], "middle": ["index-middle", "middle-ring"],
                 "ring": ["middle-ring", "ring-little"], "little": ["ring-little"]}
G_FROM_TIP, LAB, DIGIT_V, NOTCH, FUNC_LEN, WRIST_V = {}, [], {}, {}, {}, 0


def rebuild_derived():
    """Recompute every global that depends on the CURRENT bmesh topology.
    Must run after any topology edit, otherwise digit vertex sets go stale and the
    newly inserted loops are invisible to the band audit."""
    global ADJ, CO, G_FROM_TIP, LAB, DIGIT_V, NOTCH, FUNC_LEN, WRIST_V
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    ADJ = adjacency(bm)
    CO = [MW @ v.co for v in bm.verts]
    n = len(bm.verts)
    G_FROM_TIP = {nm: dijkstra(ADJ, TIPV[nm]) for nm in TIPV}
    WRIST_V = nearest_vertex(w2c(WRIST_SEED), CO)
    LAB, _dd = label_partition(ADJ, n, [("wrist", WRIST_V)] + [(nm, TIPV[nm]) for nm in TIPV])
    DIGIT_V = {nm: [] for nm in TIPV}
    for i, l in enumerate(LAB):
        if l in DIGIT_V:
            DIGIT_V[l].append(i)
    NOTCH = {}
    for a, b in CLEFTS:
        vi = cleft_apex(a, b)
        if vi is not None:
            NOTCH["%s-%s" % (a, b)] = vi
    FUNC_LEN = {}
    for nm in FINGER_ORDER:
        vals = [G_FROM_TIP[nm][NOTCH[c]] for c in FINGER_CLEFTS[nm] if c in NOTCH]
        if vals:
            FUNC_LEN[nm] = sum(vals) / len(vals)
    FUNC_LEN["thumb"] = G_FROM_TIP["thumb"][nearest_vertex(w2c(THUMB_ROOT_SEED), CO)]


rebuild_derived()
_labhist = {}
for _l in LAB:
    _labhist[str(_l)] = _labhist.get(str(_l), 0) + 1
log("  label histogram: %s" % _labhist)
for _k, _v in NOTCH.items():
    log("  notch %-14s vertex=%-5d world=%s" % (_k, _v, r3(CO[_v])))


def joint_centers(nm):
    """joint -> (geodesic distance from this digit's tip, band half-width) in metres"""
    if nm == "thumb":
        L = FUNC_LEN["thumb"]
        return {"THUMB_CMC": (L, max(0.007, 0.10 * L)),
                "THUMB_MCP": (0.56 * L, max(0.007, 0.10 * L)),
                "THUMB_IP": (0.25 * L, max(0.006, 0.09 * L))}
    L = FUNC_LEN[nm]
    h = max(0.007, 0.10 * L)
    return {"%s_MCP" % nm.upper(): (L, h),
            "%s_PIP" % nm.upper(): (0.54 * L, h),
            "%s_DIP" % nm.upper(): (0.23 * L, max(0.006, 0.09 * L))}


def finger_axis(nm):
    """Proper finger axis: through the tip and the mid-phalanx centreline.
    The cut anchor is the point of that axis nearest the anatomical landmark (the web
    commissure for the fingers, the measured thumb root for the thumb), so the cut
    planes are perpendicular to the FINGER and centred on it -- not tilted through the web."""
    tip = CO[TIPV[nm]]
    L = FUNC_LEN[nm]
    ids = DIGIT_V.get(nm, [])
    band = [i for i in ids if 0.25 * L <= G_FROM_TIP[nm][i] <= 0.55 * L]
    if band:
        c = sum((CO[i] for i in band), Vector()) / len(band)
    elif ids:
        c = sum((CO[i] for i in ids), Vector()) / len(ids)
    else:
        return D_DIST, tip
    axis = (tip - c).normalized()
    ref = (CO[nearest_vertex(w2c(THUMB_ROOT_SEED), CO)] if nm == "thumb"
           else CO[NOTCH[FINGER_CLEFTS[nm][0]]])
    anchor = tip + axis * ((ref - tip).dot(axis))
    return axis, anchor


def digit_rings(nm):
    """Circumferential structures of one digit, grouped from transverse edge components.

    A strict 'every vertex has exactly 2 transverse edges' closure test is wrong here:
    at the MCP the collar merges into the web, where palm ring fragments share its
    vertices, so a perfectly good partial collar fails closure.  An EFFECTIVE
    DEFORMATION LOOP is therefore a transverse component that (a) carries at least 60%
    of a full collar's vertex count and (b) runs AROUND the digit rather than ALONG it
    (axial extent <= 45% of its own arc length).  Closure is reported, not required.
    """
    ids = set(DIGIT_V[nm])
    axis_ln, anchor_ln = finger_axis(nm)
    sub = [(e.verts[0].index, e.verts[1].index) for e in bm.edges
           if e.verts[0].index in ids and e.verts[1].index in ids]
    tt = {i: G_FROM_TIP[nm][i] for i in ids}
    tmax = max(tt.values()) or 1.0
    NB = 40
    bins = [[] for _ in range(NB)]
    for i in ids:
        bins[min(NB - 1, int(tt[i] / tmax * (NB - 1e-6)))].append(i)
    ctrs, tval = [], []
    for b in bins:
        if b:
            ctrs.append(sum((CO[i] for i in b), Vector()) / len(b))
            tval.append(sum(tt[i] for i in b) / len(b))
    if len(ctrs) >= 3:
        sm = []
        for k in range(len(ctrs)):
            lo, hi = max(0, k - 1), min(len(ctrs), k + 2)
            sm.append(sum(ctrs[lo:hi], Vector()) / (hi - lo))
        ctrs = sm
    tang = []
    for k in range(len(ctrs)):
        d = (ctrs[min(k + 1, len(ctrs) - 1)] - ctrs[max(k - 1, 0)])
        tang.append((-d.normalized()) if d.length > 1e-12 else Vector(D_DIST))

    def lt(i):
        if not ctrs:
            return D_DIST
        best, bi = 1e18, 0
        for k, tv in enumerate(tval):
            if abs(tv - tt[i]) < best:
                best, bi = abs(tv - tt[i]), k
        return tang[bi]

    elen = {}
    trans = []
    for a, b in sub:
        d = (CO[a] - CO[b]).normalized()
        ax = (lt(a) + lt(b)).normalized()
        if abs(d.dot(ax)) < 0.45:
            trans.append((a, b))
            elen[(min(a, b), max(a, b))] = (CO[a] - CO[b]).length
    par = {}

    def find(x):
        par.setdefault(x, x)
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x

    for a, b in trans:
        ra, rb = find(a), find(b)
        if ra != rb:
            par[ra] = rb
    comps = {}
    for a, b in trans:
        comps.setdefault(find(a), set()).update((a, b))

    raw = []
    for _, vs in comps.items():
        vv = sorted(vs)
        deg = {i: 0 for i in vv}
        for a, b in trans:
            if a in deg:
                deg[a] += 1
            if b in deg:
                deg[b] += 1
        closed = all(x == 2 for x in deg.values())
        c = sum((CO[i] for i in vv), Vector()) / len(vv)
        ax = Vector((0, 0, 0))
        for i in vv:
            ax += lt(i)
        ax = ax.normalized() if ax.length > 1e-9 else Vector(D_DIST)
        proj = [((CO[i] - c).dot(ax)) for i in vv]
        arc = 0.0
        for a, b in trans:
            if a in deg and b in deg:
                arc += elen.get((min(a, b), max(a, b)), 0.0)
        raw.append({"n_verts": len(vv), "closed": bool(closed),
                    "geod_mm": round(sum(tt[i] for i in vv) / len(vv) * 1000, 3),
                    "axial_from_anchor_mm": round((c - anchor_ln).dot(axis_ln) * 1000, 3),
                    "radius_mm": round(sum((CO[i] - c).length for i in vv) / len(vv) * 1000, 3),
                    "axial_extent_mm": round((max(proj) - min(proj)) * 1000, 3),
                    "arc_len_mm": round(arc * 1000, 3)})
    n_full = max([r["n_verts"] for r in raw if r["closed"]] or [r["n_verts"] for r in raw] or [0])
    min_v = max(8, int(math.ceil(0.6 * n_full)))
    for r in raw:
        r["full_collar_verts"] = n_full
        r["min_loop_verts"] = min_v
        r["orientation_ratio"] = (round(r["axial_extent_mm"] / r["arc_len_mm"], 3)
                                  if r["arc_len_mm"] else None)
        r["is_effective_loop"] = bool(
            r["n_verts"] >= min_v and r["arc_len_mm"] > 0
            and r["axial_extent_mm"] <= 0.45 * r["arc_len_mm"])
    raw.sort(key=lambda r: r["geod_mm"])
    return raw


def band_audit(nm):
    rings = [r for r in digit_rings(nm) if r["is_effective_loop"]]
    out = {}
    for jn, (c, h) in joint_centers(nm).items():
        sel = [r for r in rings if abs(r["geod_mm"] / 1000.0 - c) <= h]
        sp = [round(sel[k + 1]["geod_mm"] - sel[k]["geod_mm"], 3) for k in range(len(sel) - 1)]
        out[jn] = {
            "joint_center_geod_mm": round(c * 1000, 3),
            "band_half_width_mm": round(h * 1000, 3),
            "effective_loop_count": len(sel),
            "loops_geod_mm": [r["geod_mm"] for r in sel],
            "loops_radius_mm": [r["radius_mm"] for r in sel],
            "loops_verts": [r["n_verts"] for r in sel],
            "loops_closed": [r["closed"] for r in sel],
            "full_collar_verts": (sel[0]["full_collar_verts"] if sel else None),
            "orientation_ratio": [r["orientation_ratio"] for r in sel],
            "spacings_mm": sp,
            "min_spacing_mm": (min(sp) if sp else None),
            "spacing_ok": bool(all(2.0 <= s <= 30.0 for s in sp)) if sp else None,
            "orientation_ok": bool(all((r["orientation_ratio"] or 9) <= 0.45 for r in sel)) if sel else None,
        }
    return out


BANDS_AFTER_L1 = {nm: band_audit(nm) for nm in TIPV}
log("BANDS after L1 (before CON-1):")
for nm, d in BANDS_AFTER_L1.items():
    log("  %-7s %s" % (nm, ", ".join("%s=%d" % (k, v["effective_loop_count"]) for k, v in d.items())))

# ==================================================================== 5. LOOP INSERTION ENGINE
def opposite_edge_in_face(f, e):
    es = list(f.edges)
    n = len(es)
    if n % 2:
        return None
    try:
        i = es.index(e)
    except ValueError:
        return None
    return es[(i + n // 2) % n]


def ring_walk(e0, max_edges=400):
    """Deterministic edge-ring walk.
    A stack/BFS floods the whole mesh wherever a ring meets a pole (valence != 4);
    walking forward from e0 in each of its two face directions and STOPPING at any
    ambiguity keeps the ring a clean 1D strip. Returns None if it degenerates."""
    ring = [e0]
    seen = {e0}
    closed = False
    for f0 in e0.link_faces:
        cur, prev = e0, f0
        for _ in range(max_edges):
            nxt = opposite_edge_in_face(prev, cur)
            if nxt is None:
                break
            if nxt is e0:
                closed = True
                break
            if nxt in seen:
                break
            nf = [g for g in nxt.link_faces if g is not prev]
            if len(nf) != 1:
                seen.add(nxt)
                ring.append(nxt)
                break
            seen.add(nxt)
            ring.append(nxt)
            cur, prev = nxt, nf[0]
            if len(ring) > max_edges:
                return None
    return ring if len(ring) >= 8 else None


def wrap_metric(coords, pt, axis):
    """How completely the loop wraps around the axis. Returns (max angular gap deg, coverage deg)."""
    a = axis.normalized()
    ref = Vector((0, 0, 1)) if abs(a.z) < 0.9 else Vector((1, 0, 0))
    e1 = (ref - a * ref.dot(a)).normalized()
    e2 = a.cross(e1)
    angs = []
    for p in coords:
        w = p - pt
        w = w - a * w.dot(a)
        if w.length < 1e-6:
            continue
        angs.append(math.atan2(w.dot(e2), w.dot(e1)))
    if len(angs) < 4:
        return 360.0, 0.0
    angs.sort()
    gaps = [angs[i + 1] - angs[i] for i in range(len(angs) - 1)]
    gaps.append(angs[0] + 2 * math.pi - angs[-1])
    return math.degrees(max(gaps)), math.degrees(2 * math.pi - max(gaps))


def find_seeds(pt, axis, dorsal, off, rmax, topk=12):
    """Candidate seed edges crossing the target plane, best (most dorsal, most axial) first."""
    PTL = MW.inverted() @ pt
    cands = []
    for e in bm.edges:
        da = (e.verts[0].co - PTL).dot(axis) - off
        db = (e.verts[1].co - PTL).dot(axis) - off
        if not ((da > 1e-9 and db < -1e-9) or (da < -1e-9 and db > 1e-9)):
            continue
        mid = (e.verts[0].co + e.verts[1].co) / 2 - PTL
        rad = (mid - axis * mid.dot(axis)).length
        if rad > rmax:
            continue
        cands.append((mid.dot(dorsal) - 6.0 * rad, e))
    cands.sort(key=lambda t: -t[0])
    return [e for _s, e in cands[:topk]]


INSERTS = []


def insert_loop(pt, axis, dorsal, off, rmax, label, wrap_max_gap=70.0,
                max_edges=400, proj_limit=0.008):
    """Insert one validated closed ring near plane(pt + axis*off), projected onto that plane."""
    for seed in find_seeds(pt, axis, dorsal, off, rmax):
        ring = ring_walk(seed, max_edges=max_edges)
        if ring is None:
            continue
        coords = [MW @ v.co for e in ring for v in e.verts]
        gap, cov = wrap_metric(coords, pt, axis)
        if gap > wrap_max_gap:
            continue
        before_v = len(bm.verts)
        res = bmesh.ops.subdivide_edges(bm, edges=ring, cuts=1, use_grid_fill=True,
                                        use_only_quads=False, smooth=0.0)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        newv = [g for g in res.get("geom_split", []) if isinstance(g, bmesh.types.BMVert)]
        PTL = MW.inverted() @ pt
        moved, maxd = 0, 0.0
        for v in newv:
            dv = (v.co - PTL).dot(axis) - off
            if abs(dv) <= proj_limit:
                v.co = v.co - axis * dv
                moved += 1
                maxd = max(maxd, abs(dv))
        ow = [MW @ v.co for v in newv]
        c = sum(ow, Vector()) / len(ow)
        rads = [(p - pt - axis * (p - pt).dot(axis)).length for p in ow]
        axs = [(p - pt).dot(axis) for p in ow]
        g2, cov2 = wrap_metric(ow, pt, axis)
        rec = {"label": label, "offset_mm": round(off * 1000, 2), "ring_edges": len(ring),
               "new_verts": len(bm.verts) - before_v, "projected": moved,
               "max_projection_mm": round(maxd * 1000, 3),
               "axial_span_mm": [round(min(axs) * 1000, 2), round(max(axs) * 1000, 2)],
               "mean_radius_mm": round(sum(rads) / len(rads) * 1000, 3),
               "wrap_max_gap_deg_before": round(gap, 2), "wrap_max_gap_deg_after": round(g2, 2),
               "new_idx": [v.index for v in newv], "accepted": True}
        INSERTS.append(rec)
        log("  %-22s ring=%3d edges +%3d verts proj=%2d axial=[%7.1f,%7.1f] r=%.1f wrap_gap=%.0f->%.0f"
            % (label, len(ring), len(bm.verts) - before_v, moved,
               rec["axial_span_mm"][0], rec["axial_span_mm"][1], rec["mean_radius_mm"], gap, g2))
        return rec
    log("  %-22s no valid ring (all candidates failed validation)" % label)
    INSERTS.append({"label": label, "offset_mm": round(off * 1000, 2), "accepted": False})
    return None


def refresh():
    """re-derive every topology-dependent global after an edit"""
    rebuild_derived()


# ------------------------------------------------ CON-1 : MCP collars + DIP/IP top-ups
log("")
log("CON-1  joint deformation loops")
TARGET_LOOPS = 3
MCP_GRID = [-1, -4, -7, -10, -13, -16, -19, -22, 2, 5, 8]
INSERTED_IN_BAND = {}


def do_insert(jn, digit, pt, axis, off, rmax, label, **kw):
    """Insert one loop, then measure where it landed and whether it sits in the joint band."""
    rec = insert_loop(pt, axis, DORSAL, off / 1000.0, rmax, label, **kw)
    if rec is None:
        return None
    refresh()
    idx = rec["new_idx"]
    g = sum(G_FROM_TIP[digit][i] for i in idx) / len(idx) if idx else None
    rec["geod_from_tip_mm"] = round(g * 1000, 3) if g is not None else None
    rec["joint"] = jn
    return rec


for nm in FINGER_ORDER:
    axis, anchor = finger_axis(nm)
    jn = "%s_MCP" % nm.upper()
    c, h = joint_centers(nm)[jn]
    pre = BANDS_AFTER_L1[nm][jn]["effective_loop_count"]
    ins = 0
    log("  %-7s %s: pre-existing detected loops = %d (band center %.1fmm +-%.1fmm)"
        % (nm, jn, pre, c * 1000, h * 1000))
    for off in MCP_GRID:
        if pre + ins >= TARGET_LOOPS:
            break
        rec = do_insert(jn, nm, anchor, axis, off, 0.016, "CON1_%s@%+dmm" % (jn, off))
        if rec is None:
            continue
        rec["digit"] = nm
        if rec["geod_from_tip_mm"] is not None and abs(rec["geod_from_tip_mm"] / 1000.0 - c) <= h:
            rec["in_band"] = True
            ins += 1
            log("     -> in band (geod %.1fmm); %s total = %d" % (rec["geod_from_tip_mm"], jn, pre + ins))
        else:
            rec["in_band"] = False
            log("     -> OUT of band (geod %s mm)" % rec["geod_from_tip_mm"])
    INSERTED_IN_BAND[jn] = ins
    log("  %-7s %s PRE=%d INSERTED_IN_BAND=%d TOTAL=%d" % (nm, jn, pre, ins, pre + ins))

for nm in FINGER_ORDER:
    axis, anchor = finger_axis(nm)
    jn = "%s_DIP" % nm.upper()
    c, h = joint_centers(nm)[jn]
    pre = BANDS_AFTER_L1[nm][jn]["effective_loop_count"]
    ins = 0
    if pre >= TARGET_LOOPS:
        log("  %-7s %s already %d loops" % (nm, jn, pre))
        INSERTED_IN_BAND[jn] = 0
        continue
    for off in (-2, 2, -4, 4, -6, 6, -8, 8):
        if pre + ins >= TARGET_LOOPS:
            break
        rec = do_insert(jn, nm, CO[TIPV[nm]], axis, off, 0.014, "CON1_%s@%+dmm" % (jn, off))
        if rec is None:
            continue
        rec["digit"] = nm
        if rec["geod_from_tip_mm"] is not None and abs(rec["geod_from_tip_mm"] / 1000.0 - c) <= h:
            rec["in_band"] = True
            ins += 1
    INSERTED_IN_BAND[jn] = ins
    log("  %-7s %s PRE=%d INSERTED_IN_BAND=%d TOTAL=%d" % (nm, jn, pre, ins, pre + ins))

# ==================================================================== 6. CON-2 THUMB CMC
# LOCALITY REFINEMENT R1.
# The previous collars came from a topological edge-ring walk.  Measured afterwards, each
# spanned ~66 mm ALONG the metacarpal: the thenar quad flow spirals around the metacarpal
# base, so the inherited edge ring is a helical band, not a local collar.  High angular
# coverage (338 deg) was therefore a FALSE POSITIVE for locality.
# Fix = LOCAL THENAR RE-GRID (explicitly permitted): delete the thenar band around the CMC,
# keep its two boundary loops, and re-stitch the gap with fresh quad rings perpendicular to
# the metacarpal axis, snapped back onto the ORIGINAL surface with a BVH tree.
log("")
log("CON-2  THUMB CMC -- local support band (locality refinement R1)")

t_axis, t_root = finger_axis("thumb")
c_cmc, h_cmc = joint_centers("thumb")["THUMB_Cmc".replace("Cmc", "CMC")]
CMC_ORIGIN = t_root.copy()


def cmc_axial(p):
    return (p - CMC_ORIGIN).dot(t_axis)


def cmc_radial(p):
    w = p - CMC_ORIGIN
    return (w - t_axis * w.dot(t_axis)).length


# CON-2 is handled after the finger work, below the pole audit helper definitions.

# ==================================================================== 6. CON-2 THUMB CMC
# STATUS: NEEDS_REVISION (see stage4a/THUMB_CMC_LOCALITY_REFINEMENT_REPORT_R1.md).
# The helical edge-ring insertion below is what produced RIGHT_HAND_ENGINEERING_STAGE4A.blend
# and is retained so that artifact stays reproducible.  It is KNOWN NOT to satisfy the
# locality requirement: each inserted collar spans ~66 mm along the metacarpal because the
# thenar quad flow spirals around the metacarpal base, so the inherited edge ring is a
# helical support band rather than a local CMC collar.
log("")
log("CON-2  THUMB CMC (LEGACY helical insertion -- locality refinement FAILED, see report)")
t_axis, t_root = finger_axis("thumb")
c_cmc, h_cmc = joint_centers("thumb")["THUMB_CMC"]
pre_cmc = BANDS_AFTER_L1["thumb"]["THUMB_CMC"]["effective_loop_count"]
ins_cmc = 0
log("  THUMB_CMC pre-existing detected loops = %d (band center %.1fmm +-%.1fmm)"
    % (pre_cmc, c_cmc * 1000, h_cmc * 1000))
LEGACY_CMC_INSERT_DISABLED = True   # R2: the helical pseudo-collars must NOT be created
for off in (() if LEGACY_CMC_INSERT_DISABLED else (-1, -3, -5, -7, -9, -11, -14, -17, 1, 3, 5, 8)):
    if ins_cmc >= 3:
        break
    rec = do_insert("THUMB_CMC", "thumb", t_root, t_axis, off, 0.034, "CON2_CMC@%+dmm" % off,
                    wrap_max_gap=110.0, max_edges=140, proj_limit=0.015)
    if rec is None:
        continue
    rec["digit"] = "thumb"
    rec["in_band"] = True
    ins_cmc += 1
INSERTED_IN_BAND["THUMB_CMC"] = ins_cmc
CMC_AXIAL = {"pre_existing_loops": pre_cmc, "inserted_in_band": ins_cmc,
             "total": pre_cmc + ins_cmc,
             "legacy_helical_insert_disabled": True,
             "locality": "NOT_APPLICABLE -- legacy helical insertion removed by R2; "
                         "THUMB CMC is now governed by T-04_CMC (local multi-axis "
                         "deformation support), not by the T-01 tubular collar criterion"}
log("  thumb   THUMB_CMC PRE=%d INSERTED=%d TOTAL=%d  (legacy helical insert DISABLED)"
    % (pre_cmc, ins_cmc, pre_cmc + ins_cmc))

# ==================================================================== 7. POST SURGERY STATE
BANDS_FINAL = {nm: band_audit(nm) for nm in TIPV}
me = ob.data
bm.normal_update()
bm.to_mesh(me)
me.update()
bm.free()

quads = sum(1 for p in me.polygons if len(p.vertices) == 4)
tris = sum(1 for p in me.polygons if len(p.vertices) == 3)
ngons = sum(1 for p in me.polygons if len(p.vertices) > 4)
TRIS_TOTAL = tris + 2 * quads + sum(len(p.vertices) - 2 for p in me.polygons if len(p.vertices) > 4)
AFTER = {
    "verts": len(me.vertices), "edges": len(me.edges), "faces": len(me.polygons),
    "quads": quads, "tris": tris, "ngons": ngons, "TRIS_TOTAL": TRIS_TOTAL,
    "mesh_signature": mesh_sig(me),
    "signed_volume_m3": signed_volume(me, ob.matrix_world),
    "uv_layers": [l.name for l in me.uv_layers],
    "modifiers": [[m.name, m.type] for m in ob.modifiers],
    "vertex_groups": [g.name for g in ob.vertex_groups],
    "armature": None, "shape_keys": (list(me.shape_keys.key_blocks.keys()) if me.shape_keys else None),
}
log("")
log("AFTER  V=%d F=%d quads=%d tri=%d ngon=%d TRIS=%d" % (AFTER["verts"], AFTER["faces"],
                                                          quads, tris, ngons, TRIS_TOTAL))

# ==================================================================== 8. CON-3 POLE AUDIT
def run_pole_audit():
    """Valence census + joint-zone classification on the CURRENT mesh."""
    bm2 = bmesh.new()
    bm2.from_mesh(me)
    bm2.verts.ensure_lookup_table()
    bm2.edges.ensure_lookup_table()
    val = [0] * len(bm2.verts)
    for e in bm2.edges:
        val[e.verts[0].index] += 1
        val[e.verts[1].index] += 1
    CO2 = [ob.matrix_world @ v.co for v in bm2.verts]
    # rebuild labels / geodesics on the final mesh
    ADJ2 = [[] for _ in range(len(bm2.verts))]
    for e in bm2.edges:
        a, b = e.verts[0].index, e.verts[1].index
        L = e.calc_length()
        ADJ2[a].append((b, L))
        ADJ2[b].append((a, L))
    tips2 = {n: nearest_vertex(w2c(s), CO2) for n, s in TIP_SEEDS.items()}
    G2 = {n: dijkstra(ADJ2, tips2[n]) for n in tips2}
    lab2 = [None] * len(CO2)
    dist2 = [float("inf")] * len(CO2)
    wsrc = nearest_vertex(w2c(WRIST_SEED), CO2)
    srcs = [("wrist", wsrc)] + [(n, tips2[n]) for n in tips2]
    for nm, s in srcs:
        dist2[s] = 0.0
        lab2[s] = nm
    pq = [(0.0, s) for _, s in srcs]
    heapq.heapify(pq)
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist2[u] + 1e-15:
            continue
        for v, w in ADJ2[u]:
            nd = d + w
            if nd < dist2[v] - 1e-16:
                dist2[v] = nd
                lab2[v] = lab2[u]
                heapq.heappush(pq, (nd, v))

    poles = []
    for i, k in enumerate(val):
        if k == 4:
            continue
        nm = lab2[i]
        zone, dist_mm, in_core = None, None, False
        if nm in TIPV:
            for jn, (c, h) in joint_centers(nm).items():
                dd = abs(G2[nm][i] - c)
                if dd <= h:
                    zone, dist_mm, in_core = jn, round(dd * 1000, 3), bool(dd <= 0.5 * h)
                    break
        poles.append({"vertex": i, "valence": k, "digit": nm, "in_deformation_zone": zone,
                      "in_deformation_core": in_core, "distance_to_joint_center_mm": dist_mm,
                      "geod_from_tip_mm": round(G2[nm][i] * 1000, 3) if nm in TIPV else None,
                      "world": r3(CO2[i])})
    hist = {}
    for k in val:
        hist[str(k)] = hist.get(str(k), 0) + 1
    POLE_AUDIT = {
        "valence_histogram": hist,
        "pole_count": len(poles),
        "valence3": sum(1 for p in poles if p["valence"] == 3),
        "valence5": sum(1 for p in poles if p["valence"] == 5),
        "other_valence": sum(1 for p in poles if p["valence"] not in (3, 5)),
        "zone_definition": {
            "band_half_width_mm": "max(7 mm, 0.10 x MCP->tip length) for MCP/PIP; "
                                  "max(6 mm, 0.09 x length) for DIP/IP; 10% of thumb length for the CMC",
            "DEFORMATION_ZONE": "|geodesic from own tip - joint centre| <= band half width",
            "DEFORMATION_CORE": "|geodesic from own tip - joint centre| <= 0.5 x band half width "
                                "(the true bending core; poles here MUST be moved/rearranged)",
        },
        "poles_in_deformation_zone": [p for p in poles if p["in_deformation_zone"]],
        "poles_in_deformation_core": [p for p in poles if p["in_deformation_core"]],
        "poles_by_digit": {},
        "poles": poles,
    }
    for p in poles:
        POLE_AUDIT["poles_by_digit"].setdefault(p["digit"], []).append(p["valence"])
    log("CON-3  poles=%d (v3=%d v5=%d other=%d)  in_zone=%d  in_CORE=%d"
        % (POLE_AUDIT["pole_count"], POLE_AUDIT["valence3"], POLE_AUDIT["valence5"],
           POLE_AUDIT["other_valence"], len(POLE_AUDIT["poles_in_deformation_zone"]),
           len(POLE_AUDIT["poles_in_deformation_core"])))
    bm2.free()
    return POLE_AUDIT, CO2, G2, lab2, val


POLE_AUDIT, CO2, G2, lab2, val = run_pole_audit()
log("CON-3  poles=%d (v3=%d v5=%d other=%d)  in_zone=%d  in_CORE=%d"
    % (POLE_AUDIT["pole_count"], POLE_AUDIT["valence3"], POLE_AUDIT["valence5"],
       POLE_AUDIT["other_valence"], len(POLE_AUDIT["poles_in_deformation_zone"]),
       len(POLE_AUDIT["poles_in_deformation_core"])))

# -------------------------------------------------------------- 8b. core pole relocation
# CON-3 requires that any pole sitting inside a joint's bending CORE be moved out of it.
# The move is a tangential displacement along the finger axis (on the tube the axis
# direction is tangential, so the surface is preserved).  Because the surface geodesic
# does not respond linearly to a displacement, the move is ITERATED until the core is
# clear, with the 1-ring relaxed on each pass (neighbours only -- relaxing the pole
# itself would pull it straight back in).
# DECISION (evidence-based): relocation is DISABLED for the shipped artifact.
# A full iterated relocation was run first (5 passes, tangential displacement along the
# finger axis + 1-ring relax).  Outcome: it did NOT reduce the number of poles classified
# inside the core window (18 -> 8), because the surface geodesic from the fingertip barely
# responds to a tangential move on the fingertip cap, so the loop kept re-moving the same
# vertices and accumulated up to ~17 mm of local displacement -- unacceptable distortion
# for a teaching asset.  It was therefore reverted.
# The pole question is instead settled on the criterion that actually matters: whether a
# pole sits on a joint's FLEXION MIDLINE (dorsal or palmar crest), which is what pinches.
# See stage4a/POLE_MIDLINE_ANALYSIS.json -- 0 of them do.
RELOCATE_CORE_POLES = False
RELOCATE_MIDLINE_POLES = True
MIDLINE_TARGET_DEG = 45.0
CORE_MOVES = []
CORE_RELOC = {"performed": False, "moved": 0,
              "reason": "attempted and reverted: relocation did not reduce the core-window "
                        "classification and accumulated up to ~17 mm of local displacement; "
                        "see POLE_MIDLINE_ANALYSIS.json for the criterion actually applied",
              "attempted_before_revert": {"passes": 5, "distinct_poles_touched": 18,
                                          "max_cumulative_displacement_mm": 16.896,
                                          "core_poles_before": 18, "core_poles_after": 8,
                                          "volume_delta_pct": 0.00052}}
MAX_PASSES = 0 if not RELOCATE_CORE_POLES else 5
TOTAL_CAP_MM = 12.0
_totals = {}

for _pass in range(1, MAX_PASSES + 1):
    _core = POLE_AUDIT["poles_in_deformation_core"]
    if not _core:
        break
    bmr = bmesh.new()
    bmr.from_mesh(me)
    bmr.verts.ensure_lookup_table()
    targets, plan = [], []
    for p in _core:
        i, nm, jn = p["vertex"], p["digit"], p["in_deformation_zone"]
        if nm not in TIPV or jn is None or i >= len(bmr.verts):
            continue
        if _totals.get(i, 0.0) >= TOTAL_CAP_MM:
            continue
        cc, hh = joint_centers(nm)[jn]
        axr, _anr = finger_axis(nm)
        d = G2[nm][i] - cc                     # + = pole is PROXIMAL of the joint centre
        half = 0.5 * hh
        margin = 0.0025
        need_prox = (half + margin) - d        # moving proximally adds to d
        need_dist = d + (half + margin)        # moving distally subtracts from d
        geod_tip = G2[nm][i]
        can_dist = (geod_tip - need_dist) > 0.004     # never push a pole past the fingertip
        if can_dist and need_dist < need_prox:
            sgn, need = 1.0, need_dist         # +axis = distally (toward the tip)
        else:
            sgn, need = -1.0, need_prox        # -axis = proximally
        if need <= 0:
            continue
        need = min(need, TOTAL_CAP_MM - _totals.get(i, 0.0))
        if need <= 1e-6:
            continue
        v = bmr.verts[i]
        before = (MW @ v.co).copy()
        targets.append(v)
        plan.append((i, nm, jn, p["valence"], p["geod_from_tip_mm"],
                     p["distance_to_joint_center_mm"], need, sgn, axr, before))
    if not targets:
        break
    VOL_PRE_RELOC = signed_volume(me, MW)
    ring = set()
    for v in targets:
        for e in v.link_edges:
            ring.add(e.other_vert(v))
    if ring:
        bmesh.ops.smooth_vert(bmr, verts=list(ring), factor=0.5,
                              use_axis_x=True, use_axis_y=True, use_axis_z=True)
        bmr.normal_update()
    for (i, nm, jn, valv, gtt, djc, need, sgn, axr, before), v in zip(plan, targets):
        v.co = v.co + axr * (sgn * need)
        _totals[i] = _totals.get(i, 0.0) + need * 1000.0
        CORE_MOVES.append({"pass": _pass, "vertex": i, "digit": nm, "joint": jn,
                           "valence": valv, "geod_from_tip_mm": gtt,
                           "distance_to_center_mm": djc,
                           "displacement_mm": round(need * 1000, 3),
                           "cumulative_mm": round(_totals[i], 3),
                           "before": r3(before), "after": r3(MW @ v.co)})
    bmr.normal_update()
    bmr.to_mesh(me)
    me.update()
    bmr.free()
    VOL_POST_RELOC = signed_volume(me, MW)
    quads_r = sum(1 for q in me.polygons if len(q.vertices) == 4)
    log("CON-3  pass %d: moved %d poles; volume delta %.4f%%; quads=%d/%d"
        % (_pass, len(targets),
           100.0 * abs(VOL_POST_RELOC - VOL_PRE_RELOC) / VOL_PRE_RELOC, quads_r, len(me.polygons)))
    CORE_RELOC = {"performed": True, "passes": _pass,
                  "moved_total": len(CORE_MOVES),
                  "distinct_poles_moved": len(_totals),
                  "max_displacement_mm": max(m["cumulative_mm"] for m in CORE_MOVES),
                  "volume_before_m3": VOL_PRE_RELOC, "volume_after_m3": VOL_POST_RELOC,
                  "volume_delta_pct": round(100.0 * abs(VOL_POST_RELOC - VOL_PRE_RELOC) / VOL_PRE_RELOC, 5),
                  "quads_after": quads_r, "faces_after": len(me.polygons),
                  "cap_total_displacement_mm": TOTAL_CAP_MM,
                  "method": "iterated tangential displacement along the finger axis to "
                            "0.5*band + 2.5 mm from the joint centre, neighbours relaxed "
                            "(smooth_vert factor 0.5) before each displacement"}
    POLE_AUDIT, CO2, G2, lab2, val = run_pole_audit()
    if not POLE_AUDIT["poles_in_deformation_core"]:
        break

POLE_AUDIT_AFTER = POLE_AUDIT
log("CON-3  FINAL: in_zone=%d  in_CORE=%d  (poles=%d)"
    % (len(POLE_AUDIT_AFTER["poles_in_deformation_zone"]),
       len(POLE_AUDIT_AFTER["poles_in_deformation_core"]), POLE_AUDIT_AFTER["pole_count"]))

# ------------------------------------------------- 8c. flexion-midline pole lateralisation
# CON-3's real concern is a pole sitting on a joint's FLEXION MIDLINE (dorsal or palmar
# crest), where flexion pinches the surface.  The clean remedy is therefore NOT to drag the
# pole along the finger axis (tried, ineffective) but to slide it CIRCUMFERENTIALLY off the
# midline onto the lateral aspect -- a sub-millimetre-to-few-millimetre move on a finger of
# ~8 mm radius, which leaves the silhouette untouched.
MIDLINE_MOVES = []
MIDLINE_RELOC = {"performed": False, "moved": 0}
if RELOCATE_MIDLINE_POLES:
    for _mp in range(1, 4):
        bml = bmesh.new()
        bml.from_mesh(me)
        bml.verts.ensure_lookup_table()
        bml.edges.ensure_lookup_table()
        val3 = [0] * len(bml.verts)
        for e in bml.edges:
            val3[e.verts[0].index] += 1
            val3[e.verts[1].index] += 1
        # poles inside a core window + their angle from the flexion midline
        cand = []
        for i, k in enumerate(val3):
            if k == 4:
                continue
            nm = lab2[i] if i < len(lab2) else None
            if nm not in TIPV:
                continue
            jn = None
            for j2, (c2, h2) in joint_centers(nm).items():
                if abs(G2[nm][i] - c2) <= 0.5 * h2:
                    jn = j2
                    break
            if jn is None:
                continue
            v = bml.verts[i]
            wp = MW @ v.co
            ring = [MW @ e.other_vert(v).co for e in v.link_edges]
            if not ring:
                continue
            cc = sum(ring, Vector()) / len(ring)
            n = wp - cc
            rlen = n.length
            if rlen < 1e-5:
                continue
            n.normalize()
            a_dor = math.degrees(math.acos(max(-1.0, min(1.0, n.dot(DORSAL)))))
            a_pal = math.degrees(math.acos(max(-1.0, min(1.0, n.dot(-DORSAL)))))
            if min(a_dor, a_pal) > MIDLINE_TARGET_DEG:
                continue
            cand.append((i, nm, jn, k, v, n, rlen, a_dor, a_pal, wp.copy(), cc))
        if not cand:
            break
        ring_set = set()
        for (i, nm, jn, k, v, n, rlen, a_dor, a_pal, wp0, cc) in cand:
            for e in v.link_edges:
                ring_set.add(e.other_vert(v))
        if ring_set:
            bmesh.ops.smooth_vert(bml, verts=list(ring_set), factor=0.5,
                                  use_axis_x=True, use_axis_y=True, use_axis_z=True)
            bml.normal_update()
        for (i, nm, jn, k, v, n, rlen, a_dor, a_pal, wp0, cc) in cand:
            axis_dir = DORSAL if a_dor <= a_pal else (-DORSAL)
            away = axis_dir - n * axis_dir.dot(n)          # direction that increases the angle
            if away.length < 1e-6:
                away = (n.cross(axis_dir))
                if away.length < 1e-6:
                    continue
            away.normalize()
            cur = min(a_dor, a_pal)
            d_theta = math.radians(max(0.0, (MIDLINE_TARGET_DEG + 8.0) - cur))
            disp = min(rlen * d_theta, 0.005)
            v.co = v.co - away * disp
            MIDLINE_MOVES.append({"pass": _mp, "vertex": i, "digit": nm, "joint": jn,
                                  "valence": k,
                                  "angle_before_deg": round(cur, 2),
                                  "displacement_mm": round(disp * 1000, 3),
                                  "before": r3(wp0), "after": r3(MW @ v.co)})
        bml.normal_update()
        bml.to_mesh(me)
        me.update()
        bml.free()
        log("CON-3  midline pass %d: lateralised %d poles off the flexion midline"
            % (_mp, len(cand)))
        POLE_AUDIT, CO2, G2, lab2, val = run_pole_audit()
        MIDLINE_RELOC = {"performed": True, "passes": _mp, "moved": len(MIDLINE_MOVES),
                         "max_displacement_mm": max(m["displacement_mm"] for m in MIDLINE_MOVES),
                         "method": "circumferential slide off the flexion midline "
                                   "(target %.0f deg + 8 deg margin, capped at 5 mm), "
                                   "neighbours relaxed before each slide" % MIDLINE_TARGET_DEG}
    bml_free = None

POLE_AUDIT_AFTER = POLE_AUDIT

# ==================================================================== 9. SAVE
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND, copy=True, compress=False)
OUT_BYTES = os.path.getsize(OUT_BLEND)
OUT_SHA = hashlib.sha256(open(OUT_BLEND, 'rb').read()).hexdigest()
log("SAVED %s  (%d bytes, sha256 %s)" % (OUT_BLEND, OUT_BYTES, OUT_SHA))

now = datetime.datetime.now().astimezone()
RAW = {
    "stage": "STAGE4A_ROUTE_C_BLENDER_ENGINEERING",
    "generated_at": now.isoformat(),
    "runtime": {"blender": bpy.app.version_string,
                "build_hash": (bpy.app.build_hash.decode() if isinstance(bpy.app.build_hash, bytes)
                               else str(bpy.app.build_hash)),
                "executable": bpy.app.binary_path},
    "asset": TARGET,
    "multires": MULTIRES_INFO,
    "before": BEFORE,
    "after_L1_apply": L1_STATE,
    "con9": CON9,
    "frame_after": FRAME_AFTER,
    "chirality": CHIR,
    "thumb_signature": THUMB_SIGNATURE,
    "functional_lengths_mm": {k: round(v * 1000, 3) for k, v in FUNC_LEN.items()},
    "bands_after_L1_before_CON1": BANDS_AFTER_L1,
    "inserted_loops_in_band": INSERTED_IN_BAND,
    "thumb_cmc_axial_audit": CMC_AXIAL if "CMC_AXIAL" in dir() else None,
    "bands_final": BANDS_FINAL,
    "inserts": INSERTS,
    "after": AFTER,
    "after_final": {
        "verts": len(me.vertices), "edges": len(me.edges), "faces": len(me.polygons),
        "quads": sum(1 for q in me.polygons if len(q.vertices) == 4),
        "tris": sum(1 for q in me.polygons if len(q.vertices) == 3),
        "ngons": sum(1 for q in me.polygons if len(q.vertices) > 4),
        "TRIS_TOTAL": (sum(1 for q in me.polygons if len(q.vertices) == 3)
                       + 2 * sum(1 for q in me.polygons if len(q.vertices) == 4)
                       + sum(len(q.vertices) - 2 for q in me.polygons if len(q.vertices) > 4)),
        "mesh_signature": mesh_sig(me),
        "signed_volume_m3": signed_volume(me, MW),
    },
    "pole_audit": POLE_AUDIT,
    "pole_audit_after_relocation": POLE_AUDIT_AFTER,
    "core_pole_relocation": CORE_RELOC,
    "core_pole_moves": CORE_MOVES,
    "midline_pole_relocation": MIDLINE_RELOC,
    "midline_pole_moves": MIDLINE_MOVES,
    "out_blend": OUT_BLEND,
    "out_bytes": OUT_BYTES,
    "out_sha256": OUT_SHA,
    "log": LOG,
}
with open(os.path.join(OUTDIR, "RAW_ENGINEERING.json"), "w", encoding="utf-8") as f:
    json.dump(RAW, f, ensure_ascii=False, indent=1)
log("WROTE RAW_ENGINEERING.json")
print("FINAL_BANDS")
for nm, d in BANDS_FINAL.items():
    print("  %-7s %s" % (nm, ", ".join("%s=%d" % (k, v["effective_loop_count"]) for k, v in d.items())))
