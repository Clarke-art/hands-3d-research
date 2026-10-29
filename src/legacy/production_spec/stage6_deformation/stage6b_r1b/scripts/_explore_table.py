# =====================================================================================
# STAGE6B_R1B -- EXPLORATORY 7 (read-only): full table for the 84 flagged endpoints
# =====================================================================================
import os
import sys
import json
import heapq

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
PROD = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
S6D = os.path.join(PROD, "stage6_deformation")
for _p in (os.path.join(S6D, "stage6b", "scripts"),
           os.path.join(PROD, "stage5_production_rig", "stage5b_r1b", "scripts"),
           os.path.join(PROD, "stage5_production_rig", "stage5b_r1a", "scripts")):
    if _p not in sys.path:
        sys.path.append(_p)
import s6b_common as B                                              # noqa: E402
import r1a_common as RC                                             # noqa: E402

MM = 1000.0
OUT = os.path.join(S6D, "stage6b_r1b", "_tmp")
LOG = []


def log(s):
    LOG.append(s)
    print("[EX7] " + s)


ctx = B.build_context()
ref = ctx["ref"]
NV = ctx["NV"]
V0 = ref["V0"]
EDGES = ref["EDGES"]
own = ctx["own_r1a"]
AC = ref["AC"]

eadj = {}
for a, b in EDGES:
    w = (V0[a] - V0[b]).length
    eadj.setdefault(a, []).append((b, w))
    eadj.setdefault(b, []).append((a, w))


def dij(s):
    d = {s: 0.0}
    pq = [(0.0, s)]
    while pq:
        du, u = heapq.heappop(pq)
        if du > d.get(u, 1e18) + 1e-15:
            continue
        for v, w in eadj.get(u, ()):
            if du + w < d.get(v, 1e18) - 1e-16:
                d[v] = du + w
                heapq.heappush(pq, (du + w, v))
    return d


# weights from the ACTIVE R1B master (read-only)
bpy.ops.wm.open_mainfile(filepath=B.R1B_MASTER)
ob = bpy.data.objects["Hand  - Realistic"]
W = [dict() for _ in range(NV)]
for g in ob.vertex_groups:
    for i in range(NV):
        try:
            w = g.weight(i)
        except RuntimeError:
            continue
        if w > 0.0:
            W[i][g.name] = w


def dom(i):
    it = sorted(W[i].items(), key=lambda kv: -kv[1])
    return it[0][0] if it else None


# live seeds
bpy.ops.wm.open_mainfile(filepath=B.R1B_MASTER)
rig = bpy.data.objects["RIGHT_HAND_PRODUCTION_RIG"]
MWr = rig.matrix_world.copy()
live_tip_thumb = (MWr @ rig.data.bones["THUMB_TIP_R"].head_local).copy()
live_tip_index = (MWr @ rig.data.bones["INDEX_TIP_R"].head_local).copy()
nvT = min(range(NV), key=lambda i: (V0[i] - live_tip_thumb).length)
nvI = min(range(NV), key=lambda i: (V0[i] - live_tip_index).length)
log("live THUMB_TIP_R head -> v%d ; live INDEX_TIP_R head -> v%d" % (nvT, nvI))

P = os.path.join(S6D, "stage6b_r1a_seam_provenance")
CB = json.load(open(os.path.join(P, "STAGE6B_R1A_CLASS_B_OWNERSHIP_MISCLASSIFICATION.json"),
                    encoding="utf-8"))
CA = json.load(open(os.path.join(P, "STAGE6B_R1A_CLASS_A_VALID_WEB_EDGES.json"), encoding="utf-8"))
verts = sorted(set([e["endpoints"]["v0"] for e in CB["edges"]] +
                   [e["endpoints"]["v1"] for e in CB["edges"]] +
                   [e["endpoints"]["v0"] for e in CA["edges"]] +
                   [e["endpoints"]["v1"] for e in CA["edges"]]))

gOld = dij(284)
gLive = dij(nvT)
gIdx = dij(nvI)
ptsT, ptsI = AC["THUMB"], AC["INDEX"]
log("%-7s %-6s %-8s %7s %7s %7s %7s %7s %7s %8s %-8s %-9s %-9s" %
    ("vert", "own", "dombone", "dT", "dI", "arcT", "arcI", "gOld", "gLive", "gIdx",
     "R2old", "R2live", "cap/nail"))
rows = []
for v in verts:
    aT = RC.arc_of(ptsT, V0[v])[0]
    aI = RC.arc_of(ptsI, V0[v])[0]
    lab_old = "THUMB" if gOld[v] < gIdx[v] else "INDEX"
    lab_live = "THUMB" if gLive[v] < gIdx[v] else "INDEX"
    tags = []
    if v in ctx["nail"]:
        tags.append("nail")
    if v in ctx["cap"]:
        tags.append("cap")
    if v in ctx["first_web"]:
        tags.append("web")
    log("v%-6d %-6s %-8s %7.2f %7.2f %7.2f %7.2f %7.2f %7.2f %8.2f %-8s %-9s %-9s" %
        (v, own[v], dom(v), ref["dchain"][v]["THUMB"], ref["dchain"][v]["INDEX"], aT, aI,
         gOld[v] * MM, gLive[v] * MM, gIdx[v] * MM, lab_old, lab_live, ",".join(tags)))
    rows.append({"v": v, "own": own[v], "dom": dom(v), "dT": ref["dchain"][v]["THUMB"],
                 "dI": ref["dchain"][v]["INDEX"], "arcT": aT, "arcI": aI,
                 "gOld": gOld[v] * MM, "gLive": gLive[v] * MM, "gIdx": gIdx[v] * MM,
                 "R2_old_seed": lab_old, "R2_live_seed": lab_live, "tags": tags})
json.dump({"log": LOG, "live_thumb_seed": nvT, "live_index_seed": nvI, "rows": rows},
          open(os.path.join(OUT, "EXPLORE_TABLE.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print("EXPLORE7_DONE")
