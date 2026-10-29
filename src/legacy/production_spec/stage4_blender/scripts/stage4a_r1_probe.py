# STAGE4A_THUMB_CMC_LOCAL_RETOPO_R1 -- topology probe of the thenar / first metacarpal base.
#
# Read-only reconnaissance: nothing is written back to the .blend.
#   * mesh integrity (boundary edges / non-manifold)
#   * CMC frame (rotation centre + first metacarpal axis), identical derivation to the
#     engineering pipeline (stage4a_cmc_locality.py)
#   * geodesic ball around the CMC centre: region sizes, boundary-loop decomposition
#   * valve/valence histogram and local quad-flow classification inside the thenar
#
# usage: blender -b <blend> --python stage4a_r1_probe.py -- <out.json>
import bpy, sys, json, math, heapq, statistics
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:]
OUT_JSON = argv[0]

TIP_SEED = Vector((1.4977, 0.0358, 0.2421))          # thumb tip, SOURCE frame
ROOT_SEED = Vector((1.4489, 0.0115, 0.3134))         # thumb root = CMC centre, SOURCE frame
M_NORM = Matrix(((1.0, 0.0, 0.0), (0.0, -1.0, 0.0), (0.0, 0.0, -1.0)))
TARGET = "Hand  - Realistic"

ob = bpy.data.objects[TARGET]
mw = ob.matrix_world
me = ob.data
CO = [mw @ v.co for v in me.vertices]
N = len(CO)
NR = len(me.polygons)
NE = len(me.edges)


def nearest(p):
    best, bi = 1e18, 0
    for i, q in enumerate(CO):
        d = (q - p).length_squared
        if d < best:
            best, bi = d, i
    return bi


loc = mw.translation


def canon(p):
    return (M_NORM @ p) + (loc - (M_NORM @ loc))


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


# radial basis around the metacarpal axis
ref = Vector((0.0, 0.0, 1.0)) if abs(AXIS.z) < 0.9 else Vector((1.0, 0.0, 0.0))
U1 = (ref - AXIS * ref.dot(AXIS)).normalized()
U2 = AXIS.cross(U1)


def polar(p):
    v = p - ANCHOR
    v = v - AXIS * v.dot(AXIS)
    return v.length, math.degrees(math.atan2(v.dot(U2), v.dot(U1)))


# ---------------- integrity
edge_faces = {}
for p in me.polygons:
    vs = list(p.vertices)
    for k in range(len(vs)):
        key = tuple(sorted((vs[k], vs[(k + 1) % len(vs)])))
        edge_faces[key] = edge_faces.get(key, 0) + 1
boundary_edges = [k for k, c in edge_faces.items() if c == 1]
nonmanifold_edges = [k for k, c in edge_faces.items() if c > 2]
face_sizes = {}
for p in me.polygons:
    face_sizes[len(p.vertices)] = face_sizes.get(len(p.vertices), 0) + 1

# ---------------- region decomposition per geodesic radius
regions = {}
for R in (0.015, 0.020, 0.025, 0.030, 0.035, 0.040):
    rk = "%dmm" % int(R * 1000)
    S = set(i for i in range(N) if gd_cmc[i] <= R)
    # boundary of the vertex set: edges with exactly one endpoint outside
    bl = [(a, b) for (a, b) in edge_faces if (a in S) != (b in S)]
    # group the boundary edges into chordless chains (they do not form a clean loop
    # because the "boundary" of a vertex set is a zig-zag ribbon, not a quad loop)
    nb = {}
    for a, b in bl:
        nb.setdefault(a, []).append(b)
        nb.setdefault(b, []).append(a)
    # faces fully inside
    fin = [p.index for p in me.polygons if all(v in S for v in p.vertices)]
    # face-region boundary loops: edges used by exactly one interior face
    uf = {}
    for fi in fin:
        vs = list(me.polygons[fi].vertices)
        for k in range(len(vs)):
            key = tuple(sorted((vs[k], vs[(k + 1) % len(vs)])))
            uf.setdefault(key, []).append(fi)
    fb = [k for k, v in uf.items() if len(v) == 1]
    # chain the face-boundary into loops
    cn = {}
    for a, b in fb:
        cn.setdefault(a, []).append(b)
        cn.setdefault(b, []).append(a)
    seen = set()
    loops = []
    for s in cn:
        if s in seen:
            continue
        comp, stack = [], [s]
        seen.add(s)
        while stack:
            u = stack.pop()
            comp.append(u)
            for v in cn[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        # is it a simple cycle?
        degs = set(len(cn[u]) for u in comp)
        loops.append({"verts": len(comp), "edges": sum(len(cn[u]) for u in comp) // 2,
                      "simple_cycle": degs == {2},
                      "axial_min_mm": round(min(axial(CO[u]) for u in comp) * 1000, 2),
                      "axial_max_mm": round(max(axial(CO[u]) for u in comp) * 1000, 2)})
    loops.sort(key=lambda L: -L["verts"])
    val = {}
    for i in S:
        val[len(adj[i])] = val.get(len(adj[i]), 0) + 1
    regions[rk] = {
        "radius_mm": R * 1000,
        "verts_in_ball": len(S),
        "faces_fully_inside": len(fin),
        "face_boundary_loops": loops[:6],
        "face_boundary_loop_count": len(loops),
        "valence_hist": val,
    }

# ---------------- quad-flow classification inside a 30 mm ball
S30 = set(i for i in range(N) if gd_cmc[i] <= 0.030)
flow = []
for i in sorted(S30):
    nb = [v for v, _ in adj[i]]
    if len(nb) != 4:
        flow.append({"v": i, "valence": len(nb), "cls": "SINGULAR"})
        continue
    # cyclic order around the vertex from the face fan
    fan = []
    for p in me.polygons:
        vs = list(p.vertices)
        if i in vs:
            k = vs.index(i)
            fan.append((vs[(k + 1) % len(vs)], vs[(k - 1) % len(vs)]))
    # opposite pairing: in a quad fan, the two edges of a quad that are opposite across
    # the vertex are (k+1) and (k-1)
    pairs = []
    for a, b in fan:
        pairs.append(tuple(sorted((a, b))))
    uniq = sorted(set(pairs))
    if len(uniq) != 2:
        flow.append({"v": i, "valence": 4, "cls": "AMBIGUOUS", "pairs": len(uniq)})
        continue
    angs = []
    for a, b in uniq:
        da = (CO[a] - CO[i])
        db = (CO[b] - CO[i])
        # the "flow direction" through the vertex for this pair
        d = (da.normalized() + db.normalized())
        if d.length < 1e-9:
            d = da
        d = d.normalized()
        angs.append(abs(d.dot(AXIS)))
    flow.append({"v": i, "valence": 4, "cls": "OK",
                 "axial_pair": round(max(angs), 3), "circ_pair": round(min(angs), 3),
                 "axial_mm": round(axial(CO[i]) * 1000, 2)})

cls_hist = {}
for f in flow:
    cls_hist[f["cls"]] = cls_hist.get(f["cls"], 0) + 1

out = {
    "mesh": {"verts": N, "edges": NE, "faces": NR, "face_sizes": face_sizes,
             "boundary_edges": len(boundary_edges),
             "nonmanifold_edges": len(nonmanifold_edges),
             "is_closed_manifold": len(boundary_edges) == 0 and len(nonmanifold_edges) == 0},
    "cmc_center": [round(x, 6) for x in CMC],
    "first_metacarpal_axis": [round(x, 6) for x in AXIS],
    "cmc_root_vertex": ROOT_V,
    "thumb_tip_vertex": TIP_V,
    "thumb_geodesic_length_mm": round(L_THUMB * 1000, 2),
    "regions": regions,
    "flow_30mm": {"classes": cls_hist,
                  "clean_orthogonal": sum(1 for f in flow if f["cls"] == "OK" and f["axial_pair"] > 0.9),
                  "oblique": sum(1 for f in flow if f["cls"] == "OK" and 0.45 < f["axial_pair"] <= 0.9)},
}
json.dump(out, open(OUT_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("=" * 78)
print("MESH  V=%d E=%d F=%d  sizes=%s  boundary=%d nonmanifold=%d"
      % (N, NE, NR, face_sizes, len(boundary_edges), len(nonmanifold_edges)))
print("CMC   = [%.6f, %.6f, %.6f]" % tuple(CMC))
print("AXIS  = [%.4f, %.4f, %.4f]   L_thumb=%.2f mm" % (AXIS.x, AXIS.y, AXIS.z, L_THUMB * 1000))
for rk, R in regions.items():
    print("  ball %-5s verts=%4d  faces=%4d  fb_loops=%d  %s"
          % (rk, R["verts_in_ball"], R["faces_fully_inside"], R["face_boundary_loop_count"],
             [(L["verts"], L["edges"], L["simple_cycle"], L["axial_min_mm"], L["axial_max_mm"])
              for L in R["face_boundary_loops"][:4]]))
print("FLOW30", cls_hist, "clean_orthogonal=%d oblique=%d"
      % (out["flow_30mm"]["clean_orthogonal"], out["flow_30mm"]["oblique"]))
print("WROTE", OUT_JSON)
