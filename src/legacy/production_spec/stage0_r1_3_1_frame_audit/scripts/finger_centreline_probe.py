# STAGE0 R1.3.1 -- finger centre-line probe.  READ-ONLY, no save, no mesh creation.
# Extracts the middle / index / ring fingers of `Hand  - Realistic` by mesh connectivity
# (Dijkstra over the edge graph from each fingertip) and reports the centre-line, so the
# direction in which the fingers leave the palm plane can be read off without any
# assumption about which side of the hand is the palm.
import bpy, bmesh, json, sys, heapq, math
from mathutils import Vector

OUT = sys.argv[-1]
TARGET = "Hand  - Realistic"
ob = bpy.data.objects[TARGET]
mw = ob.matrix_world
me = ob.data
n = len(me.vertices)
co = [mw @ v.co for v in me.vertices]

adj = [[] for _ in range(n)]
for e in me.edges:
    a, b = e.vertices
    d = (co[a] - co[b]).length
    adj[a].append((b, d)); adj[b].append((a, d))

def dijkstra(src):
    dist = [float('inf')] * n
    dist[src] = 0.0
    pq = [(0.0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    return dist

# fingertips: lowest-z vertex inside each x band
tips = {}
for name, (xlo, xhi) in {'index': (1.384, 1.402), 'middle': (1.408, 1.432), 'ring': (1.440, 1.456)}.items():
    cand = [i for i in range(n) if xlo <= co[i].x <= xhi and co[i].z < 0.20]
    if not cand:
        continue
    tips[name] = min(cand, key=lambda i: co[i].z)

rep = {"target": TARGET, "finger_centrelines": {}, "tips": {k: [round(c,4) for c in co[v]] for k, v in tips.items()}}

for name, src in tips.items():
    dist = dijkstra(src)
    bins = {}
    for i in range(n):
        if dist[i] <= 0.078:
            k = int(dist[i] / 0.006)
            bins.setdefault(k, []).append(i)
    rows = []
    for k in sorted(bins):
        idx = bins[k]
        c = sum((co[i] for i in idx), Vector((0,0,0))) / len(idx)
        ys = [co[i].y for i in idx]
        rows.append({
            "geodesic_mm": int(k*6),
            "n": len(idx),
            "cx": round(c.x,4), "cy": round(c.y,4), "cz": round(c.z,4),
            "y_spread_mm": round((max(ys)-min(ys))*1000, 1),
        })
    rep["finger_centrelines"][name] = rows

# ---- the audit quantities -------------------------------------------------
# D = distal direction (finger axis), R = radial (ulnar->radial, i.e. towards the thumb),
# N = D x R.  N is the palm-plane normal with a sign that depends on the hand's chirality:
# for a RIGHT hand D x R = dorsal, for a LEFT hand D x R = palmar.
# Independent anatomical invariants used to decide which side of the palm plane is
# palmar: (i) the fingers are displaced towards the palmar side along their length,
# (ii) the thumb lies on the palmar side of the palm plane.
V = co
fingertips = [co[i] for i in range(n) if co[i].z < 0.20 and 1.35 <= co[i].x <= 1.46]
thumb = [co[i] for i in range(n) if co[i].x > 1.458 and 0.23 <= co[i].z <= 0.29]
core = [co[i] for i in range(n) if 0.23 <= co[i].z <= 0.32 and 1.34 <= co[i].x <= 1.45]

def centroid(L):
    return sum(L, Vector((0,0,0))) / len(L)

c_fingertips = centroid(fingertips)
c_thumb = centroid(thumb)
c_core = centroid(core)
D = (c_fingertips - c_core).normalized()
tmp = c_thumb - c_core
R = (tmp - D * tmp.dot(D)).normalized()
N = D.cross(R)

rep["audit_quantities"] = {
    "fingertips_centroid": [round(x,4) for x in c_fingertips],
    "thumb_centroid": [round(x,4) for x in c_thumb],
    "core_centroid": [round(x,4) for x in c_core],
    "D_distal": [round(x,4) for x in D],
    "R_radial": [round(x,4) for x in R],
    "N_equals_DxR": [round(x,4) for x in N],
    "thumb_offset_from_core": [round(x,4) for x in (c_thumb - c_core)],
    "thumb_offset_dot_N": round((c_thumb - c_core).dot(N), 6),
    "core_y_mid": round((min(p.y for p in core) + max(p.y for p in core))/2, 4),
    "core_y_range": [round(min(p.y for p in core),4), round(max(p.y for p in core),4)],
    "thumb_y_range": [round(min(p.y for p in thumb),4), round(max(p.y for p in thumb),4)],
}
rep["PASS"] = "FINGER_CENTRELINE_DONE"
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(rep, f, ensure_ascii=False, indent=1)
print("WROTE", OUT)
