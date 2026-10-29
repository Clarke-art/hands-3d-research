# STAGE4A_R2 -- full topology audit of a Stage-4A hand mesh.
#
# Runs the SAME band/loop audit that produced stage4a/JOINT_LOOP_AUDIT.json, so the R2
# result and the pre-cage baseline can be compared like for like, plus:
#   * mesh integrity (all-quad / manifold / loose / orientation)
#   * pole audit (whole mesh + the three CMC-specific categories of R1)
#   * per-ring locality of the CMC cage (to prove there is no 40-60 mm helical pseudo-loop)
#
# usage: blender -b <blend> --python stage4a_r2_audit.py -- <out.json> [cage.json] [base.json]
import bpy, bmesh, sys, os, json, math, heapq
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:]
OUT_JSON = argv[0]
CAGE_JSON = argv[1] if len(argv) > 1 else None
BASE_JSON = argv[2] if len(argv) > 2 else None
TARGET = "Hand  - Realistic"
M_NORM = Matrix(((1.0, 0.0, 0.0), (0.0, -1.0, 0.0), (0.0, 0.0, -1.0)))
TIP_SEEDS = {
    "little": Vector((1.3515, 0.0319, 0.1879)), "ring": Vector((1.3933, 0.0320, 0.1599)),
    "middle": Vector((1.4231, 0.0251, 0.1490)), "index": Vector((1.4586, 0.0239, 0.1643)),
    "thumb": Vector((1.4977, 0.0358, 0.2421)),
}
THUMB_ROOT_SEED = Vector((1.4489, 0.0115, 0.3134))
FOREARM_SEED = Vector((1.4048, 0.0113, 0.4316))
WRIST_SEED = Vector((1.4048, 0.0113, 0.3430))
FINGER_ORDER = ["little", "ring", "middle", "index"]
LOG = []


def log(*a):
    s = " ".join(str(x) for x in a)
    LOG.append(s); print(s)


ob = bpy.data.objects[TARGET]
MW = ob.matrix_world
me = ob.data
LOC0 = MW.translation


def w2c(p):
    return (M_NORM @ p) + (LOC0 - (M_NORM @ LOC0))


bm = bmesh.new()
bm.from_mesh(me)
bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()


def adjacency(bm):
    adj = [[] for _ in range(len(bm.verts))]
    for e in bm.edges:
        a, b = e.verts[0].index, e.verts[1].index
        L = e.calc_length()
        adj[a].append((b, L)); adj[b].append((a, L))
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
                dist[v] = nd; heapq.heappush(pq, (nd, v))
    return dist


def nearest_vertex(p, coords):
    best, bi = 1e18, 0
    for i, q in enumerate(coords):
        d = (q - p).length_squared
        if d < best:
            best, bi = d, i
    return bi


ADJ = adjacency(bm)
CO = [MW @ v.co for v in bm.verts]
TIPV = {n: nearest_vertex(w2c(s), CO) for n, s in TIP_SEEDS.items()}
TIPV_ALL = dict(TIPV)
FOREARM = CO[nearest_vertex(w2c(FOREARM_SEED), CO)]
D_DIST = (CO[TIPV["middle"]] - FOREARM).normalized()
R_RAD = (CO[TIPV["index"]] - CO[TIPV["little"]]).normalized()
R_RAD = (R_RAD - D_DIST * R_RAD.dot(D_DIST)).normalized()
DORSAL = D_DIST.cross(R_RAD).normalized()
PALMAR = -DORSAL
TIPV = TIPV_ALL


def label_partition(adj, nverts, srcs):
    lab = [None] * nverts
    dd = [float("inf")] * nverts
    for name, s in srcs:
        dd[s] = 0.0; lab[s] = name
    pq = [(0.0, s) for _, s in srcs]
    heapq.heapify(pq)
    while pq:
        d, u = heapq.heappop(pq)
        if d > dd[u] + 1e-15:
            continue
        for v, w in adj[u]:
            nd = d + w
            if nd < dd[v] - 1e-16:
                dd[v] = nd; lab[v] = lab[u]; heapq.heappush(pq, (nd, v))
    return lab, dd


def cleft_apex(a, b):
    ridge = set()
    for u in range(len(bm.verts)):
        if LAB[u] not in (a, b):
            continue
        for v, _w in ADJ[u]:
            if LAB[v] in (a, b) and LAB[v] != LAB[u]:
                ridge.add(u); break
    if not ridge:
        return None
    return max(ridge, key=lambda u: (CO[u] - FOREARM).dot(D_DIST))


CLEFTS = [("index", "middle"), ("middle", "ring"), ("ring", "little"), ("index", "thumb")]
FINGER_CLEFTS = {"index": ["index-middle"], "middle": ["index-middle", "middle-ring"],
                 "ring": ["middle-ring", "ring-little"], "little": ["ring-little"]}
G_FROM_TIP = {nm: dijkstra(ADJ, TIPV[nm]) for nm in TIPV}
WRIST_V = nearest_vertex(w2c(WRIST_SEED), CO)
LAB, _dd = label_partition(ADJ, len(bm.verts),
                           [("wrist", WRIST_V)] + [(nm, TIPV[nm]) for nm in TIPV])
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


def joint_centers(nm):
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
    tip = CO[TIPV[nm]]
    L = FUNC_LEN[nm]
    ids = DIGIT_V.get(nm, [])
    band = [i for i in ids if 0.25 * L <= G_FROM_TIP[nm][i] <= 0.55 * L]
    c = (sum((CO[i] for i in band), Vector()) / len(band)) if band else \
        ((sum((CO[i] for i in ids), Vector()) / len(ids)) if ids else tip)
    axis = (tip - c).normalized()
    ref = (CO[nearest_vertex(w2c(THUMB_ROOT_SEED), CO)] if nm == "thumb"
           else CO[NOTCH[FINGER_CLEFTS[nm][0]]])
    anchor = tip + axis * ((ref - tip).dot(axis))
    return axis, anchor


def digit_rings(nm):
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
    for _r, vs in comps.items():
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
        out[jn] = {
            "joint_center_geod_mm": round(c * 1000, 3),
            "band_half_width_mm": round(h * 1000, 3),
            "effective_loop_count": len(sel),
            "loops_geod_mm": [r["geod_mm"] for r in sel],
            "loops_verts": [r["n_verts"] for r in sel],
            "loops_closed": [r["closed"] for r in sel],
        }
    return out


# ============================================================ integrity
quads = sum(1 for p in me.polygons if len(p.vertices) == 4)
tris = sum(1 for p in me.polygons if len(p.vertices) == 3)
ngons = sum(1 for p in me.polygons if len(p.vertices) > 4)
bm.edges.ensure_lookup_table(); bm.verts.ensure_lookup_table()
bnd = [e.index for e in bm.edges if len(e.link_faces) == 1]
over = [e.index for e in bm.edges if len(e.link_faces) > 2]
loosev = [v.index for v in bm.verts if len(v.link_edges) == 0]
loosee = [e.index for e in bm.edges if len(e.link_faces) == 0]
val = {v.index: len(v.link_edges) for v in bm.verts}
log("INTEGRITY  V=%d E=%d F=%d  quads=%d tris=%d ngons=%d | boundary=%d >2face=%d "
    "loose_v=%d loose_e=%d"
    % (len(me.vertices), len(me.edges), len(me.polygons), quads, tris, ngons,
       len(bnd), len(over), len(loosev), len(loosee)))

# ============================================================ CON-1 loop audit
BANDS = {nm: band_audit(nm) for nm in TIPV}
for nm in sorted(BANDS):
    log("  %-7s %s" % (nm, ", ".join("%s=%d" % (k, v["effective_loop_count"])
                                     for k, v in BANDS[nm].items())))
T01_JOINTS = ["%s_%s" % (d.upper(), j) for d in FINGER_ORDER for j in ("MCP", "PIP", "DIP")] \
             + ["THUMB_MCP", "THUMB_IP"]
t01 = {j: BANDS[j.split("_")[0].lower()][j]["effective_loop_count"] for j in T01_JOINTS}
log("T-01 (finger MCP/PIP/DIP + THUMB MCP/IP) all >= 3 : %s" % all(v >= 3 for v in t01.values()))
log("T-01 detail: %s" % t01)

# ============================================================ CMC / pole audit
ROOT_V = nearest_vertex(w2c(THUMB_ROOT_SEED), CO)
gd = dijkstra(ADJ, ROOT_V)
gdt = G_FROM_TIP["thumb"]
L_THUMB = gdt[ROOT_V]
bndv = [i for i in range(len(CO)) if 0.25 * L_THUMB <= gdt[i] <= 0.55 * L_THUMB]
c_mid = sum((CO[i] for i in bndv), Vector()) / len(bndv)
AXIS = (CO[TIPV["thumb"]] - c_mid).normalized()
ANCHOR = CO[TIPV["thumb"]] + AXIS * ((CO[ROOT_V] - CO[TIPV["thumb"]]).dot(AXIS))
CMC = CO[ROOT_V]

rows = []
for i, k in val.items():
    if k == 4:
        continue
    p = CO[i]
    ax = (p - ANCHOR).dot(AXIS)
    if abs(ax) > 0.025:
        continue
    ring = [CO[j] for j, _w in ADJ[i]]
    if not ring:
        continue
    c = sum(ring, Vector()) / len(ring)
    nrm = (p - c)
    if nrm.length < 1e-9:
        continue
    nrm.normalize()
    a_dor = math.degrees(math.acos(max(-1.0, min(1.0, nrm.dot(DORSAL)))))
    a_pal = math.degrees(math.acos(max(-1.0, min(1.0, nrm.dot(PALMAR)))))
    a_rad = math.degrees(math.acos(max(-1.0, min(1.0, nrm.dot(R_RAD)))))
    rows.append({"vertex": i, "valence": k, "axial_from_cmc_mm": round(ax * 1000, 2),
                 "euclid_from_cmc_mm": round((p - CMC).length * 1000, 2),
                 "world": [round(float(x), 6) for x in p],
                 "in_cmc_core": bool(abs(ax) <= 0.006),
                 "on_flexion_midline": bool(min(a_dor, a_pal) <= 45.0),
                 "on_opposition_path": bool(a_pal <= 62.0 and a_rad <= 75.0),
                 "angle_dorsal_deg": round(a_dor, 1), "angle_palmar_deg": round(a_pal, 1),
                 "angle_radial_deg": round(a_rad, 1)})
CORE = [r for r in rows if r["in_cmc_core"]]
FLEX = [r for r in rows if r["on_flexion_midline"]]
OPPO = [r for r in rows if r["on_opposition_path"]]
log("POLES  total=%d (v3=%d v5=%d other=%d)"
    % (len([1 for k in val.values() if k != 4]),
       sum(1 for k in val.values() if k == 3), sum(1 for k in val.values() if k == 5),
       sum(1 for k in val.values() if k not in (3, 4, 5))))
log("CMC pole audit (thumb poles within 25 mm of the CMC along the metacarpal axis):")
log("  poles near CMC        : %d" % len(rows))
log("  CMC_CORE_POLES        : %d" % len(CORE))
log("  CMC_FLEXION_MIDLINE   : %d" % len(FLEX))
log("  CMC_OPPOSITION_PATH   : %d" % len(OPPO))
for r in sorted(rows, key=lambda r: abs(r["axial_from_cmc_mm"]))[:14]:
    log("    v%-5d val=%d axial=%7.2f  dor=%5.1f pal=%5.1f rad=%5.1f  core=%s flex=%s oppo=%s"
        % (r["vertex"], r["valence"], r["axial_from_cmc_mm"], r["angle_dorsal_deg"],
           r["angle_palmar_deg"], r["angle_radial_deg"], r["in_cmc_core"],
           r["on_flexion_midline"], r["on_opposition_path"]))

# ============================================================ cage ring locality
cage = json.load(open(CAGE_JSON, encoding="utf-8")) if CAGE_JSON else None
ring_loc = []
if cage:
    for k, rw in enumerate(cage["ring_world"]):
        if k == 0:
            continue                                  # k=0 is the untouched boundary loop
        pts = [Vector(p) for p in rw]
        axv = [(p - ANCHOR).dot(AXIS) for p in pts]
        rad = [(p - CMC).length for p in pts]
        arc = sum((pts[j] - pts[(j + 1) % len(pts)]).length for j in range(len(pts)))
        ring_loc.append({"ring": k, "n_verts": len(pts),
                         "axial_span_mm": round((max(axv) - min(axv)) * 1000, 2),
                         "radius_min_mm": round(min(rad) * 1000, 2),
                         "radius_max_mm": round(max(rad) * 1000, 2),
                         "arc_len_mm": round(arc * 1000, 2)})
    for r in ring_loc:
        log("  cage ring %d: %2d verts  axial span %5.2f mm  radius %.2f..%.2f mm  arc %.2f mm"
            % (r["ring"], r["n_verts"], r["axial_span_mm"], r["radius_min_mm"],
               r["radius_max_mm"], r["arc_len_mm"]))
    worst = max(r["axial_span_mm"] for r in ring_loc)
    log("  worst cage-ring axial span = %.2f mm  (helical pseudo-loop threshold 40 mm) -> %s"
        % (worst, "PASS" if worst < 40.0 else "FAIL"))

out = {
    "stage": "STAGE4A_R2_AUDIT", "blend": bpy.data.filepath,
    "integrity": {"verts": len(me.vertices), "edges": len(me.edges), "faces": len(me.polygons),
                  "quads": quads, "tris": tris, "ngons": ngons, "boundary_edges": len(bnd),
                  "over_2face_edges": len(over), "loose_verts": len(loosev),
                  "loose_edges": len(loosee),
                  "valence_histogram": {str(k): sum(1 for v in val.values() if v == k)
                                        for k in sorted(set(val.values()))}},
    "frame": {"DISTAL_dot_+Z": round(D_DIST.z, 4), "RADIAL_dot_+X": round(R_RAD.x, 4),
              "DORSAL_dot_+Y": round(DORSAL.y, 4),
              "chirality": "RIGHT_HAND" if (D_DIST.cross(R_RAD)).dot(DORSAL) > 0 else "LEFT_HAND"},
    "bands": BANDS,
    "T01": {"joints": t01, "all_ge_3": all(v >= 3 for v in t01.values()),
            "scope": "INDEX/MIDDLE/RING/LITTLE MCP,PIP,DIP + THUMB MCP,IP -- THUMB CMC "
                     "excluded by the R2 correction (governed by T-04_CMC)"},
    "cmc": {"vertex": ROOT_V, "world": [float(x) for x in CMC],
            "axis": [float(x) for x in AXIS],
            "poles_near_cmc": len(rows),
            "CMC_CORE_POLES": len(CORE), "CMC_FLEXION_MIDLINE_POLES": len(FLEX),
            "CMC_OPPOSITION_PATH_POLES": len(OPPO), "rows": rows},
    "cage_rings": ring_loc,
    "log": LOG,
}
if BASE_JSON:
    base = json.load(open(BASE_JSON, encoding="utf-8"))
    diff = {}
    for nm in BANDS:
        for jn in BANDS[nm]:
            a = BANDS[nm][jn]["effective_loop_count"]
            b = base["bands"].get(nm, {}).get(jn, {}).get("effective_loop_count")
            if a != b:
                diff["%s" % jn] = {"before": b, "after": a}
    out["regression_vs_baseline"] = {"changed": diff, "changed_count": len(diff)}
    log("REGRESSION vs baseline: %d joint(s) changed -> %s" % (len(diff), diff))
json.dump(out, open(OUT_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
log("WROTE %s" % OUT_JSON)
POS = [tuple(round(float(x), 7) for x in (MW @ v.co)) for v in me.vertices]
json.dump({"verts": len(POS), "pos": POS}, open(OUT_JSON + ".pos.json", "w", encoding="utf-8"))
log("WROTE %s.pos.json (%d positions)" % (OUT_JSON, len(POS)))
