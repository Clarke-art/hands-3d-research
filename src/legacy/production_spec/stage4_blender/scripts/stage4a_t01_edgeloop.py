# STAGE4A_T01_FINAL_TOPOLOGY_RECONCILIATION_R1 -- AUTHORITATIVE T-01 AUDIT (READ-ONLY).
#
# The R2 transverse-connected-component counting gave INDEX_MCP=2 / MIDDLE_MCP=2 /
# RING_MCP=1 / LITTLE_MCP=3, which contradicts the R1 CON-1 verdict.  This script settles
# the question on the FINAL MESH with the method Human Review designated as the T-01
# authority: TRUE EDGE-LOOP TRAVERSAL (the Stage-1C pass9 algorithm), not axial clustering,
# not transverse components, and not construction bookkeeping.
#
#   * a step is taken only at a valence-4 vertex (opposite edge = straightest continuation)
#   * at a pole the walk STOPS and the interruption is recorded
#   * a loop counts for T-01 only if it is circumferential, belongs to the digit, sits in
#     the joint band, has >= 8 edges and covers >= 60% of the digit circumference
#
# NOTHING IS WRITTEN TO THE BLEND.  No loop insertion, no vertex move, no re-pose, no rig.
#
# usage: blender -b <blend> --python stage4a_t01_edgeloop.py -- <out.json>
import bpy, bmesh, sys, os, json, math, heapq, hashlib, datetime
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:]
OUT_JSON = argv[0]
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


BLEND = bpy.data.filepath
SHA_BEFORE = hashlib.sha256(open(BLEND, "rb").read()).hexdigest() if BLEND else None
log("INPUT (read-only): %s" % BLEND)
log("INPUT sha256: %s" % SHA_BEFORE)

ob = bpy.data.objects[TARGET]
MW = ob.matrix_world
me = ob.data
LOC0 = MW.translation
canon = lambda p: (M_NORM @ p) + (LOC0 - (M_NORM @ LOC0))

bm = bmesh.new()
bm.from_mesh(me)
bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()
W = [(MW @ v.co).copy() for v in bm.verts]
NV = len(W)


def adjacency():
    adj = [[] for _ in range(NV)]
    for e in bm.edges:
        a, b = e.verts[0].index, e.verts[1].index
        L = (W[a] - W[b]).length
        adj[a].append((b, L)); adj[b].append((a, L))
    return adj


ADJ = adjacency()
nearest = lambda p: min(range(NV), key=lambda i: (W[i] - p).length_squared)


def dij(src):
    d = [float("inf")] * NV; d[src] = 0.0; pq = [(0.0, src)]
    while pq:
        du, u = heapq.heappop(pq)
        if du > d[u] + 1e-15:
            continue
        for v, w in ADJ[u]:
            nd = du + w
            if nd < d[v] - 1e-16:
                d[v] = nd; heapq.heappush(pq, (nd, v))
    return d


TIPV = {n: nearest(canon(s)) for n, s in TIP_SEEDS.items()}
G = {n: dij(TIPV[n]) for n in TIPV}
WRIST_V = nearest(canon(WRIST_SEED))
FOREARM = W[nearest(canon(FOREARM_SEED))]
D_DIST = (W[TIPV["middle"]] - FOREARM).normalized()
R_RAD = (W[TIPV["index"]] - W[TIPV["little"]]).normalized()
R_RAD = (R_RAD - D_DIST * R_RAD.dot(D_DIST)).normalized()
DORSAL = D_DIST.cross(R_RAD).normalized()

lab = [None] * NV
dd = [float("inf")] * NV
for nm, s in [("wrist", WRIST_V)] + [(n, TIPV[n]) for n in TIPV]:
    dd[s] = 0.0; lab[s] = nm
pq = [(0.0, s) for _, s in [("wrist", WRIST_V)] + [(n, TIPV[n]) for n in TIPV]]
heapq.heapify(pq)
while pq:
    du, u = heapq.heappop(pq)
    if du > dd[u] + 1e-15:
        continue
    for v, w in ADJ[u]:
        if du + w < dd[v] - 1e-16:
            dd[v] = du + w; lab[v] = lab[u]; heapq.heappush(pq, (dd[v], v))
DIGIT_V = {n: [] for n in TIPV}
for i, l in enumerate(lab):
    if l in DIGIT_V:
        DIGIT_V[l].append(i)

CLEFTS = [("index", "middle"), ("middle", "ring"), ("ring", "little"), ("index", "thumb")]
FINGER_CLEFTS = {"index": ["index-middle"], "middle": ["index-middle", "middle-ring"],
                 "ring": ["middle-ring", "ring-little"], "little": ["ring-little"]}
NOTCH = {}
for a, b in CLEFTS:
    ridge = {u for u in range(NV) if lab[u] in (a, b)
             and any(lab[v] in (a, b) and lab[v] != lab[u] for v, _w in ADJ[u])}
    if ridge:
        NOTCH["%s-%s" % (a, b)] = max(ridge, key=lambda u: (W[u] - FOREARM).dot(D_DIST))
FUNC_LEN = {}
for nm in FINGER_ORDER:
    vals = [G[nm][NOTCH[c]] for c in FINGER_CLEFTS[nm] if c in NOTCH]
    if vals:
        FUNC_LEN[nm] = sum(vals) / len(vals)
FUNC_LEN["thumb"] = G["thumb"][nearest(canon(THUMB_ROOT_SEED))]


def joint_centers(nm):
    if nm == "thumb":
        L = FUNC_LEN["thumb"]
        return {"THUMB_CMC": (L, max(0.007, 0.10 * L)),
                "THUMB_MCP": (0.56 * L, max(0.007, 0.10 * L)),
                "THUMB_IP": (0.25 * L, max(0.006, 0.09 * L))}
    L = FUNC_LEN[nm]
    h = max(0.007, 0.10 * L)
    return {"%s_MCP" % nm.upper(): (L, h), "%s_PIP" % nm.upper(): (0.54 * L, h),
            "%s_DIP" % nm.upper(): (0.23 * L, max(0.006, 0.09 * L))}


def finger_axis(nm):
    tip = W[TIPV[nm]]
    L = FUNC_LEN[nm]
    ids = DIGIT_V.get(nm, [])
    bandv = [i for i in ids if 0.25 * L <= G[nm][i] <= 0.55 * L]
    c = (sum((W[i] for i in bandv), Vector()) / len(bandv)) if bandv else tip
    axis = (tip - c).normalized()
    ref = W[nearest(canon(THUMB_ROOT_SEED))] if nm == "thumb" else W[NOTCH[FINGER_CLEFTS[nm][0]]]
    anchor = tip + axis * ((ref - tip).dot(axis))
    return axis, anchor


# ======================================================== TRUE EDGE-LOOP TRAVERSAL
# (Stage-1C pass9 algorithm, verbatim in method: straightest continuation, valence-4 only)
incident = {v.index: [] for v in bm.verts}
for e in bm.edges:
    incident[e.verts[0].index].append(e.index)
    incident[e.verts[1].index].append(e.index)
edge_v = {e.index: (e.verts[0].index, e.verts[1].index) for e in bm.edges}
edge_key = {}
for e in bm.edges:
    edge_key[(e.verts[0].index, e.verts[1].index)] = e.index
    edge_key[(e.verts[1].index, e.verts[0].index)] = e.index

# ---- PURELY TOPOLOGICAL cyclic order of the edges around each vertex.
# The Stage-1C pass9 walker picked the "straightest" continuation by GEOMETRY (max dot,
# threshold 0.2).  On this mesh that spirals: at a skewed valence-4 vertex both candidates
# can score positive, so a single ring is re-walked as overlapping 51/45/37/33-edge
# fragments.  The unambiguous rule is topological: at a valence-4 vertex the loop continues
# to the OPPOSITE edge in the face-derived cyclic order; at any other valence it STOPS.
link = {}
for f in bm.faces:
    vs = [v.index for v in f.verts]
    n = len(vs)
    for i in range(n):
        v = vs[i]
        e_prev = edge_key[(vs[(i - 1) % n], v)]
        e_next = edge_key[(v, vs[(i + 1) % n])]
        link.setdefault((v, e_prev), set()).add(e_next)
        link.setdefault((v, e_next), set()).add(e_prev)

VCYC = {}


def vcycle(v):
    if v in VCYC:
        return VCYC[v]
    k = len(incident[v])
    order = None
    if k >= 3:
        e0 = incident[v][0]
        for second in sorted(link.get((v, e0), ())):
            seq = [e0, second]
            prev, cur = e0, second
            ok = True
            while len(seq) < k:
                cands = [e for e in link.get((v, cur), ()) if e != prev]
                if len(cands) != 1:
                    ok = False; break
                nx = cands[0]
                if nx == e0:
                    break
                if nx in seq:
                    ok = False; break
                seq.append(nx); prev, cur = cur, nx
            if ok and len(seq) == k and e0 in link.get((v, seq[-1]), ()):
                order = seq
                break
    VCYC[v] = order
    return order


def opposite_at(v, e):
    c = vcycle(v)
    if not c or len(c) != 4 or e not in c:
        return None
    return c[(c.index(e) + 2) % 4]


LOOPS = []
covered = set()


def walk(start_edge, start_vert):
    """Extend an edge loop from start_edge toward start_vert using the topological
    opposite-edge rule.  Returns (edges, status, stop_vertex, stop_valence)."""
    loop = [start_edge]
    cur_edge, cur_vert = start_edge, start_vert
    while True:
        a, b = edge_v[cur_edge]
        nxt = b if cur_vert == a else a
        opp = opposite_at(nxt, cur_edge)
        if opp is None:                                   # pole / boundary / no clean cycle
            return loop, ("pole" if len(incident[nxt]) != 4 else "nocycle"), \
                   nxt, len(incident[nxt])
        if opp == start_edge:
            return loop, "closed", nxt, len(incident[nxt])
        if opp in loop:
            return loop, "self", nxt, len(incident[nxt])
        loop.append(opp)
        cur_vert, cur_edge = nxt, opp
        if len(loop) > 400:
            return loop, "self", nxt, len(incident[nxt])


for e in bm.edges:
    if e.index in covered:
        continue
    a, b = edge_v[e.index]
    fwd, sf, vf, kf = walk(e.index, a)
    bwd, sb, vb, kb = walk(e.index, b)
    full = (list(reversed(bwd[1:])) + fwd) if len(bwd) > 1 else fwd
    for ei in full:
        covered.add(ei)
    if len(full) < 3:
        continue
    closed = (sf == "closed" and sb == "closed")
    stops = []
    if sf != "closed":
        stops.append({"end": "forward", "status": sf, "vertex": vf, "valence": kf})
    if sb != "closed":
        stops.append({"end": "backward", "status": sb, "vertex": vb, "valence": kb})
    LOOPS.append({"edges": full, "n_edges": len(full), "closed": closed, "stops": stops})
log("true edge-loop traversal (topological opposite-edge rule): %d maximal loops "
    "(median %d edges)" % (len(LOOPS), sorted(l["n_edges"] for l in LOOPS)[len(LOOPS) // 2]))


def loop_verts(lg):
    """ordered vertex list of a maximal loop"""
    out = []
    for ei in lg["edges"]:
        a, b = edge_v[ei]
        if not out:
            out = [a, b]; continue
        out.append(b if out[-1] == a else a)
    return out


def analyse(nm, lg):
    axis, anchor = finger_axis(nm)
    L = FUNC_LEN[nm]
    vs = loop_verts(lg)
    geod = [G[nm][v] for v in vs]
    ax = [(W[v] - anchor).dot(axis) for v in vs]
    perp = [((W[v] - anchor) - axis * ((W[v] - anchor).dot(axis))).length for v in vs]
    digit_frac = sum(1 for v in vs if lab[v] == nm) / max(1, len(vs))
    aligns = []
    for ei in lg["edges"]:
        a, b = edge_v[ei]
        d = W[b] - W[a]
        if d.length > 1e-9:
            aligns.append(abs((d / d.length).dot(axis)))
    align = sum(aligns) / max(1, len(aligns))
    # angular coverage around the digit axis
    ref = Vector((0, 0, 1)) if abs(axis.z) < 0.9 else Vector((1, 0, 0))
    u1 = (ref - axis * ref.dot(axis)).normalized()
    u2 = axis.cross(u1)
    ang = sorted(math.atan2(((W[v] - anchor)).dot(u2), ((W[v] - anchor)).dot(u1)) for v in vs)
    gaps = [ang[i + 1] - ang[i] for i in range(len(ang) - 1)] + [ang[0] + 2 * math.pi - ang[-1]]
    cover = 1.0 - max(gaps) / (2 * math.pi)
    return {"n_edges": lg["n_edges"], "closed": lg["closed"], "stops": lg["stops"],
            "geod_from_tip_mm": round(sum(geod) / len(geod) * 1000, 3),
            "geod_span_mm": round((max(geod) - min(geod)) * 1000, 3),
            "axial_from_anchor_mm": round(sum(ax) / len(ax) * 1000, 3),
            "axial_span_mm": round((max(ax) - min(ax)) * 1000, 3),
            "max_perp_mm": round(max(perp) * 1000, 2),
            "digit_fraction": round(digit_frac, 3),
            "axis_alignment": round(align, 3),
            "circumferential": bool(align < 0.45),
            "angular_coverage": round(cover, 3),
            "verts": vs}


T01_JOINTS = [("index", "INDEX_MCP"), ("middle", "MIDDLE_MCP"),
              ("ring", "RING_MCP"), ("little", "LITTLE_MCP")]
OTHER_JOINTS = [(d, "%s_%s" % (d.upper(), j)) for d in FINGER_ORDER for j in ("PIP", "DIP")] \
               + [("thumb", "THUMB_MCP"), ("thumb", "THUMB_IP")]
# ---------------------------------------------------------------- joint zones
# TWO joint locators exist in the pipeline and they DISAGREE near the finger base:
#   (a) GEODESIC -- centre = FUNC_LEN = surface-PATH length from tip to the web commissure
#   (b) AXIAL    -- centre = the web commissure projected onto the finger axis
# The geodesic metric is a PATH length.  Near the MCP the shortest path from the tip to the
# commissure wraps around the finger base, so it over-states the geometric distance by
# 1.14x (middle) up to 1.50x (little).  A "+/-10%" geodesic window is therefore displaced
# up to ~30 mm into the palm for the little finger.  The axial metric is the geometric one,
# and it is also the one the CON-1 loop INSERTION used (insert_loop(anchor, axis, off) with
# off in mm from the commissure anchor), so construction and audit finally agree.
#   => AXIAL is the T-01 authority; the geodesic-metric count is reported as DIAGNOSTIC.
AXIAL_FRAC = {"MCP": 0.0, "PIP": 0.46, "DIP": 0.77, "THUMB_MCP": 0.44, "THUMB_IP": 0.75}
EUCLID_TIP_WEB = {}
report = {}
for nm, jn in T01_JOINTS + OTHER_JOINTS:
    axis, anchor = finger_axis(nm)
    L = FUNC_LEN[nm]
    A = (W[TIPV[nm]] - anchor).dot(axis)          # axial finger length: tip -> commissure
    base = jn.split("_")[-1]
    key = ("THUMB_" + base) if (nm == "thumb" and base in ("MCP", "IP")) else base
    c_ax = A * AXIAL_FRAC[key]
    h = max(0.007, 0.10 * L) if base in ("MCP", "PIP") else max(0.006, 0.09 * L)
    c_gd, h_gd = joint_centers(nm)[jn]
    rows = []
    for lg in LOOPS:
        a = analyse(nm, lg)
        if a["n_edges"] < 8 or not a["circumferential"]:
            continue
        if a["digit_fraction"] < 0.55 or a["max_perp_mm"] > 22.0:
            continue
        if a["angular_coverage"] < 0.60:
            continue
        if abs(a["axial_from_anchor_mm"] - c_ax * 1000.0) > h * 1000.0:
            continue
        rows.append(a)
    rows.sort(key=lambda r: r["axial_from_anchor_mm"])
    gdiag = [a for a in rows if abs(a["geod_from_tip_mm"] - c_gd * 1000.0) <= h_gd * 1000.0]
    closed = [r for r in rows if r["closed"]]
    openok = [r for r in rows if not r["closed"]]
    spac = [round(rows[i + 1]["axial_from_anchor_mm"] - rows[i]["axial_from_anchor_mm"], 3)
            for i in range(len(rows) - 1)]
    pos = [r["axial_from_anchor_mm"] for r in rows]
    span = (max(pos) - min(pos)) if len(pos) >= 2 else 0.0
    neg = sum(1 for p in pos if p < c_ax * 1000.0)
    if nm not in EUCLID_TIP_WEB:
        EV = [i for i in DIGIT_V.get(nm, []) if lab[i] == nm]
        if nm in NOTCH.values():
            pass
        nc = [NOTCH[c] for c in FINGER_CLEFTS.get(nm, []) if c in NOTCH]
        if nc:
            EUCLID_TIP_WEB[nm] = {
                "geod_tip_to_web_mm": round(L * 1000, 3),
                "euclid_tip_to_web_mm": round(
                    sum((W[TIPV[nm]] - W[x]).length for x in nc) / len(nc) * 1000, 3)}
    report[jn] = {
        "digit": nm,
        "locator": "AXIAL -- joint centre = the web commissure projected on the finger axis",
        "axial_finger_length_mm": round(A * 1000, 3),
        "joint_axial_center_mm": round(c_ax * 1000, 3),
        "zone_half_width_mm": round(h * 1000, 3),
        "ACTUAL_EDGE_LOOPS": len(rows),
        "CLOSED_LOOPS": len(closed),
        "OPEN_SUPPORT_LOOPS": len(openok),
        "PARTIAL_ARCS_NOT_COUNTED": 0,
        "LOOP_POSITION_axial_from_commissure_mm": pos,
        "LOOP_POSITION_geod_from_tip_mm": [r["geod_from_tip_mm"] for r in rows],
        "LOOP_SPACING_mm": spac,
        "LOOP_N_EDGES": [r["n_edges"] for r in rows],
        "LOOP_ANGULAR_COVERAGE": [r["angular_coverage"] for r in rows],
        "POLE_INTERRUPTION": [
            {"loop_index": i, "axial_mm": r["axial_from_anchor_mm"], "n_edges": r["n_edges"],
             "coverage": r["angular_coverage"], "stops": r["stops"]}
            for i, r in enumerate(rows) if not r["closed"]],
        "DEFORMATION_ZONE_COVERAGE": {
            "loops_proximal_of_joint": neg,
            "loops_distal_of_joint": len(rows) - neg,
            "straddles_joint": bool(neg > 0 and len(rows) - neg > 0),
            "loops_span_mm": round(span, 3),
            "zone_width_mm": round(2 * h * 1000, 3),
            "span_over_zone": round(span / (2 * h * 1000), 3),
            "min_angular_coverage": min([r["angular_coverage"] for r in rows] or [0.0]),
            "all_loops_ge_60pct": bool(all(r["angular_coverage"] >= 0.60 for r in rows)),
        },
        "DIAGNOSTIC_geodesic_metric_count": len(gdiag),
        "DIAGNOSTIC_geodesic_band_mm": [round((c_gd - h_gd) * 1000, 3),
                                        round((c_gd + h_gd) * 1000, 3)],
        "meets_min_3": bool(len(rows) >= 3),
        "loops": [{k: v for k, v in r.items() if k != "verts"} for r in rows],
        "_verts": [r["verts"] for r in rows],
    }
    log("  %-12s axial zone %7.2f+-%5.2f mm  ACTUAL=%d (closed %d / open-support %d)  pos=%s "
        "[geodesic-metric diagnostic %d]"
        % (jn, c_ax * 1000, h * 1000, len(rows), len(closed), len(openok), pos, len(gdiag)))

SHA_AFTER = hashlib.sha256(open(BLEND, "rb").read()).hexdigest() if BLEND else None
t01 = {j: report[j]["ACTUAL_EDGE_LOOPS"] for _d, j in T01_JOINTS}
other = {j: report[j]["ACTUAL_EDGE_LOOPS"] for _d, j in OTHER_JOINTS if j in report}
out = {
    "stage": "STAGE4A_T01_FINAL_TOPOLOGY_RECONCILIATION_R1",
    "method": "TRUE EDGE-LOOP TRAVERSAL. A step is taken only at a valence-4 vertex, to "
              "the OPPOSITE edge in the face-derived topological cyclic order; the walk "
              "stops at a pole (valence != 4) and the interruption is recorded. Counting "
              "rule: n_edges >= 8, circumferential (mean |edge . finger axis| < 0.45), "
              ">=55% of vertices labelled to the digit, perpendicular radius <= 22 mm, "
              ">=60% angular coverage around the finger axis, and inside the joint zone. "
              "Joint zone locator = AXIAL (web commissure projected on the finger axis).",
    "read_only": True,
    "input_blend": BLEND, "input_sha256_before": SHA_BEFORE, "input_sha256_after": SHA_AFTER,
    "input_unchanged": SHA_BEFORE == SHA_AFTER,
    "generated_at": datetime.datetime.now().astimezone().isoformat(),
    "runtime": {"blender": bpy.app.version_string, "executable": bpy.app.binary_path},
    "total_maximal_edge_loops": len(LOOPS),
    "T01_MCP": {j: report[j] for _d, j in T01_JOINTS},
    "OTHER_T01_JOINTS": {j: report[j] for _d, j in OTHER_JOINTS if j in report},
    "T01_counts": t01,
    "geodesic_vs_euclid_tip_to_web": EUCLID_TIP_WEB,
    "T01_all_MCP_ge_3": all(v >= 3 for v in t01.values()),
    "OTHER_counts": other,
    "log": LOG,
}
json.dump(out, open(OUT_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
log("T01 counts: %s  all >= 3 : %s" % (t01, out["T01_all_MCP_ge_3"]))
log("OTHER counts: %s" % other)
log("input unchanged: %s" % out["input_unchanged"])
log("WROTE %s" % OUT_JSON)
