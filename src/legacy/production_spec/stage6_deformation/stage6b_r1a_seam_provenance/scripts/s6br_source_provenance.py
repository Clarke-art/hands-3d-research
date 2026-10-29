# =====================================================================================
# STAGE6B_R1A -- SOURCE ASSET provenance probe (read-only)
# =====================================================================================
# (a) geodesic thumb-tip <-> index-tip on the PRE-RSSF Stage4A surface (indices stable)
# (b) the CC0 bootstrap C1 mesh: geodesic-farthest pair (double sweep) -> intrinsic scale
# (c) does the CC0 mesh coincide with the Stage4A R2 surface (multirez L1 of the same
#     surface)?  measured as nearest-SURFACE distance after the global translation.
# =====================================================================================
import os
import sys
import json
import heapq

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import s6br_common as F                                              # noqa: E402

OUT = os.path.join(F.S6B_R1A, "_tmp")
MM = F.MM
LOG = []
RES = {}


def log(s):
    LOG.append(s)
    print("[S6BR-SRC] " + s)


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
ref = ctx["ref"]
V0 = ref["V0"]
EDGES = ref["EDGES"]


def nearest_vert(V, P):
    return min(range(len(V)), key=lambda i: (V[i] - P).length)


TIP_T = nearest_vert(V0, ctx["ref"]["AC"]["THUMB"][-1])
TIP_I = nearest_vert(V0, ctx["ref"]["AC"]["INDEX"][-1])

# ---------------- (a) Stage4A R2 (pre-RSSF, same surface & indices as production)
bpy.ops.wm.open_mainfile(filepath=os.path.join(F.S4, "stage4a_r2",
                                               "RIGHT_HAND_ENGINEERING_STAGE4A_R2.blend"))
ob = bpy.data.objects[F.MESH_OBJ]
MW = ob.matrix_world.copy()
V4 = [(MW @ v.co).copy() for v in ob.data.vertices]
E4 = [(e.vertices[0], e.vertices[1]) for e in ob.data.edges]
a4 = adj_of(V4, E4)
gT4 = dij(a4, TIP_T)
gI4 = dij(a4, TIP_I)
log("S4A_R2 (pre-RSSF, same surface as the CC0 source): geodesic thumb_tip->index_tip = "
    "%.4f mm ; thumb_tip->wrist-side eccentricity = %.4f mm"
    % (gI4[TIP_T] * MM, max(gT4.values()) * MM))
RES["S4A_R2_pre_rssf"] = {
    "geodesic_thumb_tip_to_index_tip_mm": F.rr(gI4[TIP_T] * MM, 4),
    "thumb_tip_eccentricity_mm": F.rr(max(gT4.values()) * MM, 4),
    "NV": len(V4), "NE": len(E4)}
S4A_FACES = [tuple(p.vertices) for p in ob.data.polygons]

# ---------------- (b)(c) CC0 bootstrap C1
bpy.ops.wm.open_mainfile(filepath=os.path.join(F.S2, "RIGHT_HAND_BOOTSTRAP_C1.blend"))
ob = bpy.data.objects[F.MESH_OBJ]
MW = ob.matrix_world.copy()
Vc = [(MW @ v.co).copy() for v in ob.data.vertices]
Ec = [(e.vertices[0], e.vertices[1]) for e in ob.data.edges]
ac = adj_of(Vc, Ec)
nvc = len(Vc)
s0 = 0
g0 = dij(ac, s0)
A = max(g0, key=lambda k: g0[k])
gA = dij(ac, A)
B = max(gA, key=lambda k: gA[k])
log("C1 CC0 bootstrap: NV=%d NE=%d NF=%d | geodesic-farthest pair A=v%d B=v%d = %.4f mm"
    % (nvc, len(Ec), len(ob.data.polygons), A, B, gA[B] * MM))
# the 5 mutually-separated points furthest from A (fingertip candidates)
order = sorted(gA, key=lambda k: -gA[k])
tips = []
for v in order:
    if all((Vc[v] - Vc[t]).length * MM >= 18.0 for t in tips):
        tips.append(v)
    if len(tips) >= 5:
        break
log("C1 fingertip candidates (furthest from A, spatially separated): %s  arcs from A: %s"
    % (tips, [F.rr(gA[t] * MM, 2) for t in tips]))
RES["C1_cc0_bootstrap"] = {
    "NV": nvc, "NE": len(Ec), "NF": len(ob.data.polygons),
    "geodesic_farthest_pair_mm": F.rr(gA[B] * MM, 4),
    "farthest_pair": [A, B],
    "fingertip_candidates": tips,
    "fingertip_arc_from_A_mm": [F.rr(gA[t] * MM, 2) for t in tips]}

# (c) does C1 coincide with the Stage4A surface?
zoff = min(v.z for v in V4) - min(v.z for v in Vc)
Vs = [v + Vector((0.0, 0.0, zoff)) for v in Vc]
tree = BVHTree.FromPolygons([tuple(v) for v in V4], [tuple(p) for p in S4A_FACES],
                            all_triangles=False, epsilon=0.0)
ds = []
for v in Vs:
    loc, nrm, idx, d = tree.find_nearest(v)
    ds.append(d * MM if d is not None else 1e9)
ds.sort()
log("C1 (Z-shifted %.3f mm) -> Stage4A R2 nearest-SURFACE distance: median %.4f mm ; "
    "p95 %.4f mm ; max %.4f mm  (sub-division smoothing only)"
    % (zoff * MM, ds[len(ds) // 2], ds[int(0.95 * (len(ds) - 1))], ds[-1]))
RES["C1_vs_S4A_surface"] = {"z_offset_mm": F.rr(zoff * MM, 4),
                            "median_dist_mm": F.rr(ds[len(ds) // 2], 4),
                            "p95_dist_mm": F.rr(ds[int(0.95 * (len(ds) - 1))], 4),
                            "max_dist_mm": F.rr(ds[-1], 4)}

json.dump({"result": RES, "log": LOG},
          open(os.path.join(OUT, "S6BR_SOURCE_PROVENANCE.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print("S6BR_SRC_DONE")
