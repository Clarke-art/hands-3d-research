# STAGE4A_THUMB_CMC_LOCAL_RETOPO_R1 -- axial level-set diagnosis.
#
# Decisive question: at a given axial height (measured along the first metacarpal axis
# from the CMC rotation centre), what does the surface level-set look like near the
# thumb base?  If the level set has a small separate contour that wraps ONLY the thumb,
# a local circumferential support ring can be inserted at that height without touching
# the rest of the hand.  If instead there is a single large contour that wraps the whole
# hand/wrist, a "circumferential" ring at that height is necessarily non-local.
#
# Also re-runs the corrected quad-flow classification (opposite-neighbour pairing).
#
# usage: blender -b <blend> --python stage4a_r1_levelset.py -- <out.json>
import bpy, sys, json, math, heapq
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:]
OUT_JSON = argv[0]

TIP_SEED = Vector((1.4977, 0.0358, 0.2421))
ROOT_SEED = Vector((1.4489, 0.0115, 0.3134))
M_NORM = Matrix(((1.0, 0.0, 0.0), (0.0, -1.0, 0.0), (0.0, 0.0, -1.0)))
TARGET = "Hand  - Realistic"

ob = bpy.data.objects[TARGET]
mw = ob.matrix_world
me = ob.data
CO = [mw @ v.co for v in me.vertices]
N = len(CO)
loc = mw.translation


def canon(p):
    return (M_NORM @ p) + (loc - (M_NORM @ loc))


def nearest(p):
    best, bi = 1e18, 0
    for i, q in enumerate(CO):
        d = (q - p).length_squared
        if d < best:
            best, bi = d, i
    return bi


TIP_V = nearest(canon(TIP_SEED))
ROOT_V = nearest(canon(ROOT_SEED))

adj = [[] for _ in range(N)]
for e in me.edges:
    a, b = e.vertices[0], e.vertices[1]
    L = (CO[a] - CO[b]).length
    adj[a].append((b, L))
    adj[b].append((a, L))


def dijkstra(src):
    d = [float("inf")] * N
    d[src] = 0.0
    pq = [(0.0, src)]
    while pq:
        du, u = heapq.heappop(pq)
        if du > d[u] + 1e-15:
            continue
        for v, w in adj[u]:
            nd = du + w
            if nd < d[v] - 1e-16:
                d[v] = nd
                heapq.heappush(pq, (nd, v))
    return d


gd_tip = dijkstra(TIP_V)
L_THUMB = gd_tip[ROOT_V]
band = [i for i in range(N) if 0.25 * L_THUMB <= gd_tip[i] <= 0.55 * L_THUMB]
c_mid = sum((CO[i] for i in band), Vector()) / len(band)
AXIS = (CO[TIP_V] - c_mid).normalized()
ANCHOR = CO[TIP_V] + AXIS * ((CO[ROOT_V] - CO[TIP_V]).dot(AXIS))
CMC = CO[ROOT_V]
gd_cmc = dijkstra(ROOT_V)


def axial(p):
    return (p - ANCHOR).dot(AXIS)


def radius(p):
    v = p - ANCHOR
    return (v - AXIS * v.dot(AXIS)).length


# ---------------- axial level-set contours
face_cross = {}


def contours_at(t):
    """Cross-cut the surface with the plane {axial == t}; return the closed contours."""
    face_cross.clear()
    edges_at = {}
    for p in me.polygons:
        vs = list(p.vertices)
        cr = []
        for k in range(len(vs)):
            a, b = vs[k], vs[(k + 1) % len(vs)]
            aa, ab = axial(CO[a]), axial(CO[b])
            if (aa - t) * (ab - t) < 0:
                f = (t - aa) / (ab - aa)
                key = (min(a, b), max(a, b))
                edges_at[key] = CO[a] + (CO[b] - CO[a]) * f
                cr.append(key)
        if len(cr) == 2:
            face_cross[p.index] = cr
    # link crossings that share a face
    link = {}
    for fi, (e1, e2) in face_cross.items():
        link.setdefault(e1, []).append(e2)
        link.setdefault(e2, []).append(e1)
    seen = set()
    out = []
    for s in list(link):
        if s in seen:
            continue
        comp, stack = [], [s]
        seen.add(s)
        while stack:
            u = stack.pop()
            comp.append(u)
            for v in link[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        degs = set(len(link[u]) for u in comp)
        rs = [radius(edges_at[e]) * 1000 for e in comp]
        out.append({"edges": len(comp), "simple_cycle": degs == {2},
                    "r_min_mm": round(min(rs), 2), "r_max_mm": round(max(rs), 2)})
    face_cross.clear()
    out.sort(key=lambda L: -L["edges"])
    return out


levels = []
for tmm in range(-30, 61, 2):
    t = tmm / 1000.0
    cs = contours_at(t)
    levels.append({"axial_mm": tmm, "n_contours": len(cs),
                   "contours": cs[:5]})

# ---------------- corrected quad-flow classification (30 mm ball)
S30 = [i for i in range(N) if gd_cmc[i] <= 0.030]
cls_hist = {}
flow_rows = []
for i in S30:
    nb = [v for v, _ in adj[i]]
    if len(nb) != 4:
        cls_hist["SINGULAR"] = cls_hist.get("SINGULAR", 0) + 1
        flow_rows.append({"v": i, "valence": len(nb), "cls": "SINGULAR"})
        continue
    # build the cyclic order from the quad fan
    consec = set()
    for p in me.polygons:
        vs = list(p.vertices)
        if i in vs:
            k = vs.index(i)
            a, b = vs[(k + 1) % len(vs)], vs[(k - 1) % len(vs)]
            consec.add(tuple(sorted((a, b))))
    nxt = {}
    for a, b in consec:
        nxt.setdefault(a, set()).add(b)
        nxt.setdefault(b, set()).add(a)
    if len(nxt) != 4 or any(len(v) != 2 for v in nxt.values()):
        cls_hist["AMBIGUOUS"] = cls_hist.get("AMBIGUOUS", 0) + 1
        flow_rows.append({"v": i, "valence": 4, "cls": "AMBIGUOUS"})
        continue
    # walk the cycle
    start = nb[0]
    order = [start]
    prev = None
    cur = start
    while True:
        opts = [x for x in nxt[cur] if x != prev]
        if not opts:
            break
        prev, cur = cur, opts[0]
        if cur == start:
            break
        order.append(cur)
    if len(order) != 4:
        cls_hist["AMBIGUOUS"] = cls_hist.get("AMBIGUOUS", 0) + 1
        flow_rows.append({"v": i, "valence": 4, "cls": "AMBIGUOUS"})
        continue
    # opposite neighbours = flow partners
    pair_a = (order[0], order[2])
    pair_b = (order[1], order[3])
    al = []
    for (a, b) in (pair_a, pair_b):
        da = (CO[a] - CO[i]).normalized()
        db = (CO[b] - CO[i]).normalized()
        d = (da + db)
        d = d.normalized() if d.length > 1e-9 else da
        al.append(abs(d.dot(AXIS)))
    ax_pair = max(al)
    if ax_pair > 0.9:
        c = "AXIAL_CLEAN"
    elif ax_pair > 0.6:
        c = "AXIAL_OBLIQUE"
    elif ax_pair > 0.35:
        c = "SKEW"
    else:
        c = "CIRCUMFERENTIAL_ONLY"
    cls_hist[c] = cls_hist.get(c, 0) + 1
    flow_rows.append({"v": i, "valence": 4, "cls": c,
                      "axial_pair": round(al[0], 3), "circ_pair": round(al[1], 3),
                      "axial_mm": round(axial(CO[i]) * 1000, 2),
                      "r_mm": round(radius(CO[i]) * 1000, 2)})

out = {
    "cmc_center": [round(x, 6) for x in CMC],
    "first_metacarpal_axis": [round(x, 6) for x in AXIS],
    "levels": levels,
    "flow_30mm_ball": {"classes": cls_hist, "verts": len(S30)},
    "flow_rows": flow_rows,
}
json.dump(out, open(OUT_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("=" * 100)
print("AXIAL LEVEL SETS  (contour edges / r_min..r_max mm from the metacarpal axis)")
for L in levels:
    desc = " | ".join("n=%d %s r=%.1f..%.1f" % (c["edges"], "CLOSED" if c["simple_cycle"] else "OPEN",
                                                 c["r_min_mm"], c["r_max_mm"])
                      for c in L["contours"])
    print("  axial %+4d mm : %d contour(s)  %s" % (L["axial_mm"], L["n_contours"], desc))
print("FLOW(30mm ball):", cls_hist)
print("WROTE", OUT_JSON)
