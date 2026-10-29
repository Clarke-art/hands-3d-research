# =====================================================================================
# STAGE6B_R1A -- resolve the CC0 bootstrap -> Stage4A rigid transform, then measure the
# thumb|index sheet gap in the SOURCE pose (read-only).
# =====================================================================================
import os
import sys
import json
import heapq

import bpy
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import s6br_common as F                                              # noqa: E402

OUT = os.path.join(F.S6B_R1A, "_tmp")
MM = F.MM
LOG = []


def log(s):
    LOG.append(s)
    print("[S6BR-SRC2] " + s)


def adj_of(V, E):
    a = {}
    for x, y in E:
        w = (V[x] - V[y]).length
        a.setdefault(x, []).append((y, w))
        a.setdefault(y, []).append((x, w))
    return a


def dij(a, src):
    d = {src: 0.0}
    pq = [(0.0, src)]
    while pq:
        du, u = heapq.heappop(pq)
        if du > d.get(u, 1e18) + 1e-15:
            continue
        for v, w in a.get(u, ()):
            if du + w < d.get(v, 1e18) - 1e-16:
                d[v] = du + w
                heapq.heappush(pq, (du + w, v))
    return d


ctx = F.B.build_context()
NV = ctx["NV"]
V0 = ctx["ref"]["V0"]
EDGES = ctx["edges"]
TIP_T = min(range(NV), key=lambda i: (V0[i] - ctx["ref"]["AC"]["THUMB"][-1]).length)
TIP_I = min(range(NV), key=lambda i: (V0[i] - ctx["ref"]["AC"]["INDEX"][-1]).length)

# Stage4A R2 (target frame)
bpy.ops.wm.open_mainfile(filepath=os.path.join(F.S4, "stage4a_r2",
                                               "RIGHT_HAND_ENGINEERING_STAGE4A_R2.blend"))
ob = bpy.data.objects[F.MESH_OBJ]
MW = ob.matrix_world.copy()
V4 = [(MW @ v.co).copy() for v in ob.data.vertices]
F4 = [tuple(p.vertices) for p in ob.data.polygons]
TREE = BVHTree.FromPolygons([tuple(v) for v in V4], F4, all_triangles=False, epsilon=0.0)
V4_T = V4[TIP_T]
V4_I = V4[TIP_I]

# CC0 bootstrap
bpy.ops.wm.open_mainfile(filepath=os.path.join(F.S2, "RIGHT_HAND_BOOTSTRAP_C1.blend"))
ob = bpy.data.objects[F.MESH_OBJ]
MWc = ob.matrix_world.copy()
Vc = [(MWc @ v.co).copy() for v in ob.data.vertices]
Ec = [(e.vertices[0], e.vertices[1]) for e in ob.data.edges]
nvc = len(Vc)


def med_surface_dist(Vs):
    ds = []
    for v in Vs:
        loc, nrm, idx, d = TREE.find_nearest(v)
        ds.append((d * MM) if d is not None else 1e9)
    ds.sort()
    return ds[len(ds) // 2], ds[-1]


best = None
C4 = Vector(((min(v.x for v in V4) + max(v.x for v in V4)) * 0.5,
             (min(v.y for v in V4) + max(v.y for v in V4)) * 0.5,
             (min(v.z for v in V4) + max(v.z for v in V4)) * 0.5))
Cc = Vector(((min(v.x for v in Vc) + max(v.x for v in Vc)) * 0.5,
             (min(v.y for v in Vc) + max(v.y for v in Vc)) * 0.5,
             (min(v.z for v in Vc) + max(v.z for v in Vc)) * 0.5))
for sx in (1.0, -1.0):
    for sy in (1.0, -1.0):
        for sz in (1.0, -1.0):
            S = Matrix.Diagonal((sx, sy, sz)).to_4x4()
            Vs = [C4 + S @ (v - Cc) for v in Vc]
            med, mx = med_surface_dist(Vs)
            if best is None or med < best[0]:
                best = (med, mx, (sx, sy, sz), Vs)
log("best axis-sign alignment C1 -> Stage4A R2: signs=%s median=%.4f mm max=%.4f mm"
    % (str(best[2]), best[0], best[1]))
Vs = best[3]

# refine with Kabsch on nearest-vertex correspondences (2 iterations)
acc = V4
for it in range(2):
    # nearest V4 vertex for each source vertex (coarse but enough to refine)
    pairs = []
    for i, v in enumerate(Vs):
        j = min(range(len(V4)), key=lambda k: (V4[k] - v).length_squared)
        pairs.append((v, V4[j]))
    A = [p[0] for p in pairs]
    B = [p[1] for p in pairs]
    ca = sum(A, Vector()) / len(A)
    cb = sum(B, Vector()) / len(B)
    H = Matrix(((0, 0, 0), (0, 0, 0), (0, 0, 0)))
    for a, b in pairs:
        d = a - ca
        e = b - cb
        for r in range(3):
            for c in range(3):
                H[r][c] += d[r] * e[c]
    import numpy as np
    Hn = np.array([[H[r][c] for c in range(3)] for r in range(3)])
    Uu, Ss, Vv = np.linalg.svd(Hn)
    D = np.diag([1.0, 1.0, float(np.sign(np.linalg.det(Vv.T @ Uu.T)))])
    R = Vv.T @ D @ Uu.T
    Rm = Matrix([[R[r][c] for c in range(3)] for r in range(3)])
    Vs = [cb + Rm @ (v - ca) for v in Vs]
    med, mx = med_surface_dist(Vs)
    log("  refine %d: median=%.4f mm max=%.4f mm" % (it + 1, med, mx))

med, mx = med_surface_dist(Vs)
log("final C1 -> Stage4A R2 surface distance: median %.4f mm ; max %.4f mm" % (med, mx))

# ---------------------------------------------------------------- source-pose contact gap
aces = adj_of(Vc, Ec)
sT = min(range(nvc), key=lambda i: (Vs[i] - V4_T).length)
sI = min(range(nvc), key=lambda i: (Vs[i] - V4_I).length)
dT = (Vs[sT] - V4_T).length * MM
dI = (Vs[sI] - V4_I).length * MM
gT = dij(aces, sT)
gI = dij(aces, sI)
S_T = set(i for i in range(nvc) if gT[i] < gI[i])
S_I = set(i for i in range(nvc) if gI[i] < gT[i])
from mathutils.kdtree import KDTree
listI = sorted(S_I)
kt = KDTree(len(listI))
for n, i in enumerate(listI):
    kt.insert(Vc[i], n)
kt.balance()
Eset = set()
for a, b in Ec:
    Eset.add((a, b))
    Eset.add((b, a))
bg, bp = 1e18, None
for i in S_T:
    cos, n, d = kt.find(Vc[i])
    j = listI[n]
    if (i, j) in Eset:
        continue
    if d < bg:
        bg, bp = d, (i, j)
log("SOURCE pose: seed err (%.3f, %.3f) mm ; thumb basin %d / index basin %d ; "
    "min sheet gap %.4f mm ; geodesic thumb_tip->index_tip %.4f mm"
    % (dT, dI, len(S_T), len(S_I), bg * MM, gI[sT] * MM))

json.dump({"alignment": {"signs": list(best[2]), "median_mm": F.rr(med, 4), "max_mm": F.rr(mx, 4)},
           "source_pose": {"seed_error_mm": [F.rr(dT, 4), F.rr(dI, 4)],
                           "thumb_basin": len(S_T), "index_basin": len(S_I),
                           "min_sheet_gap_mm": F.rr(bg * MM, 4),
                           "geodesic_thumb_tip_to_index_tip_mm": F.rr(gI[sT] * MM, 4)},
           "log": LOG},
          open(os.path.join(OUT, "S6BR_SOURCE_ALIGN.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print("S6BR_SRC2_DONE")
