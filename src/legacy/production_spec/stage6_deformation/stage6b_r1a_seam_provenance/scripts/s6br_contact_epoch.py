# =====================================================================================
# STAGE6B_R1A -- contact-epoch experiment: did the RSSF re-pose create the near-contact?
# =====================================================================================
# Vertex indices are stable for every 3416-vertex stage, so the SAME seed vertices can be
# used everywhere.  The digit basins are computed from REAL mesh geodesics (topology only),
# so they are pose-independent; what we then measure is the SPATIAL gap between the thumb
# sheet and the index sheet, which IS pose dependent.
# =====================================================================================
import os
import sys
import json
import heapq

import bpy
from mathutils import Vector
from mathutils.kdtree import KDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import s6br_common as F                                              # noqa: E402

OUT = os.path.join(F.S6B_R1A, "_tmp")
MM = F.MM
LOG = []
RES = {}


def log(s):
    LOG.append(s)
    print("[S6BR-CONTACT] " + s)


# ---------------------------------------------------------------- reference + seeds
ctx = F.B.build_context()
NV = ctx["NV"]
ref = ctx["ref"]
V0 = ref["V0"]
EDGES = ref["EDGES"]
ARC = ctx["ARC"]
thumb_pts = ref["AC"]["THUMB"]
index_pts = ref["AC"]["INDEX"]


def nearest_vert(P):
    return min(range(NV), key=lambda i: (V0[i] - P).length)


TIP_SEEDS = {
    "THUMB": nearest_vert(thumb_pts[-1]),
    "INDEX": nearest_vert(index_pts[-1]),
}
log("seed vertices (production): %s" % TIP_SEEDS)

# ---------------------------------------------------------------- geodesic utilities
def build_adj(V, EDGES):
    eadj = {}
    for a, b in EDGES:
        w = (V[a] - V[b]).length
        eadj.setdefault(a, []).append((b, w))
        eadj.setdefault(b, []).append((a, w))
    return eadj


def dij(eadj, src):
    d = {src: 0.0}
    pq = [(0.0, src)]
    while pq:
        du, u = heapq.heappop(pq)
        if du > d.get(u, 1e18) + 1e-15:
            continue
        for v, w in eadj.get(u, ()):
            if du + w < d.get(v, 1e18) - 1e-16:
                d[v] = du + w
                heapq.heappush(pq, (du + w, v))
    return d


def min_sheet_gap(V, setA, setB, exclude_edge_adjacent=True):
    """min spatial distance between vertex set A and set B, optionally ignoring pairs that
    are directly edge-adjacent (those are legitimate same-sheet links)."""
    Eset = set()
    if exclude_edge_adjacent:
        for a, b in EDGES:
            Eset.add((a, b))
            Eset.add((b, a))
    kt = KDTree(len(setB))
    listB = sorted(setB)
    for n, i in enumerate(listB):
        kt.insert(V[i], n)
    kt.balance()
    best = 1e18
    pair = None
    for i in setA:
        cos, n, d = kt.find(V[i])
        j = listB[n]
        if exclude_edge_adjacent and ((i, j) in Eset):
            continue
        if d < best:
            best, pair = d, (i, j)
    return best * MM, pair


def load_stage_geo(path, prefer_nv=None):
    bpy.ops.wm.open_mainfile(filepath=path)
    ob = None
    for c in bpy.data.objects:
        if c.type == 'MESH' and "Hand" in c.name:
            if prefer_nv is not None and abs(len(c.data.vertices) - prefer_nv) > max(4, 0.02 * prefer_nv):
                continue
            if ob is None or len(c.data.vertices) > len(ob.data.vertices):
                ob = c
    if ob is None:
        return None
    MW = ob.matrix_world.copy()
    V = [(MW @ v.co).copy() for v in ob.data.vertices]
    E = [(e.vertices[0], e.vertices[1]) for e in ob.data.edges]
    return V, E, ob.name


# ---------------------------------------------------------------- 3416-vertex stages
STAGES_3416 = [
    ("S4A_R2", os.path.join(F.S4, "stage4a_r2", "RIGHT_HAND_ENGINEERING_STAGE4A_R2.blend")),
    ("S4B_RSSF_R1", os.path.join(F.S4, "stage4b_rssf",
                                 "RIGHT_HAND_ENGINEERING_STAGE4B_RSSF_R1.blend")),
    ("S4B_RSSF_R2", os.path.join(F.S4, "stage4b_rssf",
                                 "RIGHT_HAND_ENGINEERING_STAGE4B_RSSF_R2.blend")),
    ("S5B_R1B", F.R1B_MASTER),
]
log("")
log("%-14s %-10s %-12s %-12s %-12s" % ("stage", "thumbN", "indexN", "gap_mm", "gap_pair"))
V_S4A = None
for label, path in STAGES_3416:
    got = load_stage_geo(path, prefer_nv=NV)
    if got is None:
        log("%-14s not found" % label)
        continue
    V, E, name = got
    if label == "S4A_R2":
        V_S4A = V
    eadj = build_adj(V, E)
    gT = dij(eadj, TIP_SEEDS["THUMB"])
    gI = dij(eadj, TIP_SEEDS["INDEX"])
    S_T = set(i for i in range(NV) if gT[i] < gI[i])
    S_I = set(i for i in range(NV) if gI[i] < gT[i])
    gap, pair = min_sheet_gap(V, S_T, S_I, exclude_edge_adjacent=True)
    log("%-14s %-10d %-12d %-12.4f %s" % (label, len(S_T), len(S_I), gap, pair))
    RES[label] = {"thumb_basin": len(S_T), "index_basin": len(S_I),
                  "min_sheet_gap_mm": F.rr(gap, 4),
                  "min_sheet_gap_pair": list(pair) if pair else None,
                  "edge_count": len(E)}

# ---------------------------------------------------------------- source asset (831)
src_path = F.LINEAGE[0][1]
if os.path.exists(src_path):
    bpy.ops.wm.open_mainfile(filepath=src_path)
    ob = None
    for c in bpy.data.objects:
        if c.type == 'MESH' and "Hand" in c.name and len(c.data.vertices) == 831:
            ob = c
            break
    if ob is not None:
        MW = ob.matrix_world.copy()
        V = [(MW @ v.co).copy() for v in ob.data.vertices]
        E = [(e.vertices[0], e.vertices[1]) for e in ob.data.edges]
        NV_s = len(V)
        # map the two tip seeds onto the source by position, after removing the global
        # Z offset measured between C1 and the Stage4A frame
        zoff = (min(v.z for v in V_S4A) - min(v.z for v in V))
        Vs = [v + Vector((0.0, 0.0, zoff)) for v in V]
        # map the tip seeds on the PRE-RSSF pose (the source shares the Stage4A pose, not the
        # compact RSSF pose), therefore map against the Stage4A R2 vertex positions
        sT = min(range(NV_s), key=lambda i: (Vs[i] - V_S4A[TIP_SEEDS["THUMB"]]).length)
        sI = min(range(NV_s), key=lambda i: (Vs[i] - V_S4A[TIP_SEEDS["INDEX"]]).length)
        dT = (Vs[sT] - V_S4A[TIP_SEEDS["THUMB"]]).length * MM
        dI = (Vs[sI] - V_S4A[TIP_SEEDS["INDEX"]]).length * MM
        eadj = build_adj(V, E)
        gT = dij(eadj, sT)
        gI = dij(eadj, sI)
        S_T = set(i for i in range(NV_s) if gT[i] < gI[i])
        S_I = set(i for i in range(NV_s) if gI[i] < gT[i])
        # source geodesic tip-to-tip
        gtt = gI[sT] * MM
        # min gap (edge-adjacency excluded using source edges)
        kt = KDTree(len(S_I))
        list_I = sorted(S_I)
        for n, i in enumerate(list_I):
            kt.insert(V[i], n)
        kt.balance()
        Eset = set()
        for a, b in E:
            Eset.add((a, b))
            Eset.add((b, a))
        best, pair = 1e18, None
        for i in S_T:
            cos, n, d = kt.find(V[i])
            j = list_I[n]
            if (i, j) in Eset:
                continue
            if d < best:
                best, pair = d, (i, j)
        log("%-14s NV=%-5d seeds=(%d,%d) seed_err=(%.3f,%.3f)mm thumbN=%d indexN=%d "
            "gap=%.4f mm  geodesic_tip_to_tip=%.3f mm"
            % ("S0_SOURCE", NV_s, sT, sI, dT, dI, len(S_T), len(S_I), best * MM, gtt))
        RES["S0_SOURCE"] = {"NV": NV_s, "seed_thumb": sT, "seed_index": sI,
                            "seed_position_error_mm": [F.rr(dT, 4), F.rr(dI, 4)],
                            "thumb_basin": len(S_T), "index_basin": len(S_I),
                            "min_sheet_gap_mm": F.rr(best * MM, 4),
                            "min_sheet_gap_pair": list(pair) if pair else None,
                            "geodesic_thumb_tip_to_index_tip_mm": F.rr(gtt, 4),
                            "z_offset_applied_mm": F.rr(zoff * MM, 4)}

json.dump({"tip_seed_vertices": TIP_SEEDS, "stages": RES, "log": LOG},
          open(os.path.join(OUT, "S6BR_CONTACT_EPOCH.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print("S6BR_CONTACT_DONE")
