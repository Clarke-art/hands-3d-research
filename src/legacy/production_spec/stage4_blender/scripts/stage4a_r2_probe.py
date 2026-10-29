# STAGE4A_R2 -- CMC CAGE FEASIBILITY PROBE.
#
# For a range of geodesic radii R around the CMC surface vertex, measure:
#   * the disk of faces whose every vertex has gd <= R
#   * whether that face set is a topological disk with ONE boundary loop
#   * the boundary loop length N  (the cage will need N % 8 == 0 for a symmetric
#     all-quad core cap: N = 2*(P+Q) with P = Q = N/4 and P, Q even)
#   * leftover vertices: gd <= R but belonging to no disk face (must be 0)
#
# usage: blender -b <blend> --python stage4a_r2_probe.py -- <out.json>
import bpy, bmesh, sys, json, math, heapq
from mathutils import Vector, Matrix

OUT = sys.argv[sys.argv.index("--") + 1]
TARGET = "Hand  - Realistic"
M_NORM = Matrix(((1.0, 0.0, 0.0), (0.0, -1.0, 0.0), (0.0, 0.0, -1.0)))
THUMB_TIP_SEED = Vector((1.4977, 0.0358, 0.2421))
THUMB_ROOT_SEED = Vector((1.4489, 0.0115, 0.3134))

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


TIP_V = nearest(canon(THUMB_TIP_SEED))
ROOT_V = nearest(canon(THUMB_ROOT_SEED))
adj = [[] for _ in range(N)]
for e in me.edges:
    a, b = e.vertices[0], e.vertices[1]
    L = (CO[a] - CO[b]).length
    adj[a].append((b, L)); adj[b].append((a, L))


def dij(src, want_pred=False):
    d = [float("inf")] * N
    pred = [-1] * N
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
                pred[v] = u
                heapq.heappush(pq, (nd, v))
    return (d, pred) if want_pred else d


gd, pred = dij(ROOT_V, True)
# first metacarpal axis + CMC anchor (same construction as the R1 winding script)
gdt = dij(TIP_V)
L_THUMB = gdt[ROOT_V]
band = [i for i in range(N) if 0.25 * L_THUMB <= gdt[i] <= 0.55 * L_THUMB]
c_mid = sum((CO[i] for i in band), Vector()) / len(band)
AXIS = (CO[TIP_V] - c_mid).normalized()
ANCHOR = CO[TIP_V] + AXIS * ((CO[ROOT_V] - CO[TIP_V]).dot(AXIS))
CMC = CO[ROOT_V]

bf = []
for p in me.polygons:
    vs = [v for v in p.vertices]
    E = [(vs[i], vs[(i + 1) % len(vs)]) for i in range(len(vs))]
    bf.append((vs, E))


def disk_of(R):
    S = set(i for i in range(N) if gd[i] <= R)
    faces = [pi for pi, (vs, E) in enumerate(bf) if all(v in S for v in vs)]
    fset = set(faces)
    cnt = {}
    for pi in faces:
        for (a, b) in bf[pi][1]:
            k = tuple(sorted((a, b)))
            cnt[k] = cnt.get(k, 0) + 1
    bnd = [k for k, c in cnt.items() if c == 1]
    # Euler characteristic of the disk
    vs_in = set()
    for pi in faces:
        vs_in.update(bf[pi][0])
    e_in = set(cnt.keys())
    euler = len(vs_in) - len(e_in) + len(faces)
    # single boundary loop?
    cn = {}
    for a, b in bnd:
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
    ok_deg = all(len(v) == 2 for v in cn.values())
    # leftover: gd <= R but in no disk face
    inface = set()
    for pi in faces:
        inface.update(bf[pi][0])
    leftover = [i for i in S if i not in inface]
    return {"R_mm": round(R * 1000, 2), "faces": len(faces), "verts": len(vs_in),
            "boundary_edges": len(bnd), "boundary_verts": len(cn),
            "euler": euler, "is_disk": (euler == 1 and len(comps) == 1 and ok_deg),
            "components": len(comps), "leftover_verts": len(leftover),
            "N_mod8": len(bnd) % 8}


rows = []
for Rmm in range(10, 31):
    rows.append(disk_of(Rmm / 1000.0))

print("=" * 96)
print("CMC vertex=%d  world=%s" % (ROOT_V, [round(float(x), 5) for x in CMC]))
print("first metacarpal axis=%s" % [round(float(x), 4) for x in AXIS])
print("=" * 96)
print("%6s %6s %6s %8s %8s %6s %6s %6s %6s" %
      ("R_mm", "faces", "verts", "bnd_edge", "bnd_vtx", "euler", "disk", "leftov", "N%8"))
for r in rows:
    print("%6.1f %6d %6d %8d %8d %6d %6s %6d %6d" %
          (r["R_mm"], r["faces"], r["verts"], r["boundary_edges"], r["boundary_verts"],
           r["euler"], r["is_disk"], r["leftover_verts"], r["N_mod8"]))
cand = [r for r in rows if r["is_disk"] and r["leftover_verts"] == 0 and r["N_mod8"] == 0]
print("-" * 96)
print("VIABLE (disk, no leftover, N%8==0):", [(r["R_mm"], r["boundary_edges"]) for r in cand])
json.dump({"cmc_vertex": ROOT_V, "cmc_world": [float(x) for x in CMC],
           "axis": [float(x) for x in AXIS], "anchor": [float(x) for x in ANCHOR],
           "rows": rows, "viable": cand},
          open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("WROTE", OUT)
