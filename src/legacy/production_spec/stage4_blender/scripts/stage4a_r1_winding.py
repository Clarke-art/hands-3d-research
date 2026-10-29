# STAGE4A_THUMB_CMC_LOCAL_RETOPO_R1 -- do the concentric CMC rings actually encircle
# the first metacarpal AXIS (winding number 1), or are they flat on the thenar?
#
# winding is computed on the plane perpendicular to the axis, about the axis origin,
# as the signed total turning of the projected polyline.
#
# usage: blender -b <blend> --python stage4a_r1_winding.py -- <out.json>
import bpy, sys, json, math, heapq
from mathutils import Vector, Matrix

OUT = sys.argv[sys.argv.index("--") + 1]
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
        if (q - p).length_squared < best:
            best, bi = (q - p).length_squared, i
    return bi


TIP_V, ROOT_V = nearest(canon(TIP_SEED)), nearest(canon(ROOT_SEED))
adj = [[] for _ in range(N)]
for e in me.edges:
    a, b = e.vertices[0], e.vertices[1]
    L = (CO[a] - CO[b]).length
    adj[a].append((b, L)); adj[b].append((a, L))


def dij(src):
    d = [float("inf")] * N; d[src] = 0.0; pq = [(0.0, src)]
    while pq:
        du, u = heapq.heappop(pq)
        if du > d[u] + 1e-15:
            continue
        for v, w in adj[u]:
            nd = du + w
            if nd < d[v] - 1e-16:
                d[v] = nd; heapq.heappush(pq, (nd, v))
    return d


gd_tip = dij(TIP_V)
L_THUMB = gd_tip[ROOT_V]
band = [i for i in range(N) if 0.25 * L_THUMB <= gd_tip[i] <= 0.55 * L_THUMB]
c_mid = sum((CO[i] for i in band), Vector()) / len(band)
AXIS = (CO[TIP_V] - c_mid).normalized()
ANCHOR = CO[TIP_V] + AXIS * ((CO[ROOT_V] - CO[TIP_V]).dot(AXIS))
CMC = CO[ROOT_V]
gd = dij(ROOT_V)
ref = Vector((0, 0, 1)) if abs(AXIS.z) < 0.9 else Vector((1, 0, 0))
U1 = (ref - AXIS * ref.dot(AXIS)).normalized()
U2 = AXIS.cross(U1)


def polar(p):
    v = p - ANCHOR
    v = v - AXIS * v.dot(AXIS)
    return v.length, math.atan2(v.dot(U2), v.dot(U1))


def ring_of(R):
    S = set(i for i in range(N) if gd[i] <= R)
    uf = {}
    for p in me.polygons:
        vs = list(p.vertices)
        if not all(v in S for v in vs):
            continue
        for j in range(len(vs)):
            k = tuple(sorted((vs[j], vs[(j + 1) % len(vs)])))
            uf.setdefault(k, []).append(p.index)
    fb = [k for k, v in uf.items() if len(v) == 1]
    cn = {}
    for a, b in fb:
        cn.setdefault(a, []).append(b); cn.setdefault(b, []).append(a)
    comps, seen = [], set()
    for s in cn:
        if s in seen:
            continue
        comp, st, seen = [], [s], seen | {s}
        while st:
            u = st.pop(); comp.append(u)
            for v in cn[u]:
                if v not in seen:
                    seen.add(v); st.append(v)
        comps.append(comp)
    comps.sort(key=len, reverse=True)
    comp = comps[0]
    start = sorted(comp)[0]
    order, prev, cur = [start], None, start
    while True:
        o = [x for x in cn[cur] if x != prev]
        if not o:
            break
        prev, cur = cur, o[0]
        if cur == start:
            break
        order.append(cur)
        if len(order) > len(comp) + 2:
            break
    return order


report = []
for R in (0.008, 0.012, 0.016, 0.020, 0.025, 0.030):
    order = ring_of(R)
    pts = [CO[i] for i in order]
    rr, ang = [], []
    for p in pts:
        r, a = polar(p)
        rr.append(r); ang.append(a)
    turn = 0.0
    for k in range(len(ang)):
        d = ang[(k + 1) % len(ang)] - ang[k]
        while d > math.pi:
            d -= 2 * math.pi
        while d < -math.pi:
            d += 2 * math.pi
        turn += d
    wind = turn / (2 * math.pi)
    ax = [(p - ANCHOR).dot(AXIS) * 1000 for p in pts]
    report.append({"R_mm": R * 1000, "verts": len(pts), "winding_about_axis": round(wind, 3),
                   "encircles_metacarpal": abs(abs(wind) - 1.0) < 0.25,
                   "r_min_mm": round(min(rr) * 1000, 2), "r_max_mm": round(max(rr) * 1000, 2),
                   "axial_span_mm": round(max(ax) - min(ax), 2)})
    print("R=%5.1f mm  n=%3d  winding=%+.3f  encircles=%s  r=[%5.1f,%5.1f]  axial_span=%6.2f"
          % (R * 1000, len(pts), wind, abs(abs(wind) - 1.0) < 0.25,
             min(rr) * 1000, max(rr) * 1000, max(ax) - min(ax)))
json.dump({"rings": report}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("WROTE", OUT)
