# =====================================================================================
# STAGE5B R1E -- READ-ONLY PROBE 5 : the thumb-tip / index-base FOLD topology
# =====================================================================================
import os
import json
from collections import Counter, deque
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
PROD = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
R1E = os.path.abspath(os.path.join(HERE, ".."))
R3D = os.path.join(PROD, "stage6_deformation", "stage6b_r3_thumb_tip_ownership_boundary")
S5 = os.path.join(PROD, "stage5_production_rig")
MM = 1000.0
MESH_OBJ = "Hand  - Realistic"; RIG_OBJ = "RIGHT_HAND_PRODUCTION_RIG"
R1B = os.path.join(S5, "stage5b_r1b", "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend")
R2A = os.path.join(S5, "stage5a_r2a", "RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend")

lab = json.load(open(os.path.join(R3D, "R3_OWNERSHIP_LABELS.json"), encoding="utf-8"))
R3 = lab["R3"]; BND = list(lab["boundary_edges_R3"])
CAP = set(lab["CAP"]); NAIL_T = set(lab["NAIL_THUMB"]); NAIL_I = set(lab["NAIL_INDEX"]); WEB = set(lab["WEB"])

bpy.ops.wm.open_mainfile(filepath=R1B)
ob = bpy.data.objects[MESH_OBJ]; me = ob.data; MW = ob.matrix_world.copy()
NV = len(me.vertices)
V0 = [(MW @ v.co).copy() for v in me.vertices]
EDGES = [(e.vertices[0], e.vertices[1]) for e in me.edges]
W = [dict() for _ in range(NV)]
for g in ob.vertex_groups:
    for i in range(NV):
        try:
            w = g.weight(i)
        except RuntimeError:
            continue
        if w > 0.0:
            W[i][g.name] = w
bpy.ops.wm.open_mainfile(filepath=R2A)
ob2 = bpy.data.objects[MESH_OBJ]; rig2 = bpy.data.objects[RIG_OBJ]; MW2 = ob2.matrix_world.copy()
CH = {"THUMB": ("THUMB_CMC_R", "THUMB_MCP_R", "THUMB_IP_R"),
      "INDEX": ("INDEX_MCP_R", "INDEX_PIP_R", "INDEX_DIP_R")}


def lp(c):
    p = [MW2 @ Vector(rig2.data.bones[c[0]].head_local)]
    for nm in c:
        p.append(MW2 @ Vector(rig2.data.bones[nm].tail_local))
    return p


def arc_of(pts, v):
    bd, bs, acc = 1e18, 0.0, 0.0
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]; ab = b - a
        t = max(0.0, min(1.0, (v - a).dot(ab) / max(ab.length_squared, 1e-18)))
        d = (v - (a + ab * t)).length
        if d < bd:
            bd, bs = d, (acc + t * ab.length) * MM
        acc += ab.length
    return bs, bd * MM


LT = lp(CH["THUMB"]); LI = lp(CH["INDEX"])
sT = [0.0] * NV; dT = [0.0] * NV; sI = [0.0] * NV; dI = [0.0] * NV
for i in range(NV):
    sT[i], dT[i] = arc_of(LT, V0[i])
    sI[i], dI[i] = arc_of(LI, V0[i])

adj = {}
for a, b in EDGES:
    adj.setdefault(a, set()).add(b); adj.setdefault(b, set()).add(a)
adj = dict((k, sorted(v)) for k, v in adj.items())
cut = set(tuple(sorted(EDGES[k])) for k in BND)
seen = set(); comps = []
for v in range(NV):
    if v in seen:
        continue
    dq = deque([v]); seen.add(v); c = []
    while dq:
        x = dq.popleft(); c.append(x)
        for u in adj[x]:
            if u in seen or tuple(sorted((x, u))) in cut:
                continue
            seen.add(u); dq.append(u)
    comps.append(c)
comps.sort(key=len, reverse=True)
BODY = set(comps[0]); SHEET = set(comps[1])


def bdist(seeds, targets, maxd=8):
    seen = dict((v, 0) for v in seeds); front = set(seeds); d = 0
    while front and d < maxd:
        nxt = set()
        for u in front:
            for v in adj[u]:
                if v not in seen:
                    seen[v] = d + 1; nxt.add(v)
        front = nxt; d += 1
        if front & targets:
            return d, sorted(front & targets)
    return None, []


O = {}
ringT = [2153, 2155, 2157, 2159, 2161, 2163, 2166, 2169, 3196, 3197, 3198, 3199, 3200, 3201, 3202, 3203]
ringI = [693, 702, 689, 696, 699, 698, 692, 704, 2156, 2160, 2164, 2167, 2170, 2172, 2174, 2176]
dCAP, hCAP = bdist(ringT, CAP | NAIL_T)
O["ringT_to_cap_or_nail"] = [dCAP, hCAP]
O["ringT_to_cap_only"] = bdist(ringT, CAP)
O["ringT_to_nail_thumb"] = bdist(ringT, NAIL_T)
O["ringI_to_index_nail"] = bdist(ringI, NAIL_I)
O["ringI_to_cap"] = bdist(ringI, CAP)

# local neighbourhood of the whole collar ring set (ringT+ringI) at depth 1 and 2
ring = set(ringT) | set(ringI)
d1 = set()
for v in ring:
    d1.update(adj[v])
d1 -= ring
d2 = set()
for v in d1:
    d2.update(adj[v])
d2 -= ring | d1
O["collar_ring"] = sorted(ring)
O["collar_d1"] = sorted(d1)
O["collar_d2"] = sorted(d2)
O["collar_d1_label"] = dict(Counter(R3[v] for v in d1))
O["collar_d2_label"] = dict(Counter(R3[v] for v in d2))
O["collar_d1_in_sheet"] = len([v for v in d1 if v in SHEET])
O["collar_d2_in_sheet"] = len([v for v in d2 if v in SHEET])


def info(v):
    return {"v": v, "R3": R3[v], "comp": "sheet" if v in SHEET else "body",
            "isCap": v in CAP, "isNailT": v in NAIL_T, "isNailI": v in NAIL_I, "isWeb": v in WEB,
            "sT": round(sT[v], 2), "dT": round(dT[v], 2), "sI": round(sI[v], 2), "dI": round(dI[v], 2),
            "pos": [round(c * MM, 1) for c in V0[v]],
            "W": dict((g, round(x, 4)) for g, x in sorted(W[v].items())),
            "ring_nbrs": len([u for u in adj[v] if u in ring]),
            "nbrs": sorted(adj[v])}


O["ringT_detail"] = [info(v) for v in ringT]
O["ringI_detail"] = [info(v) for v in ringI]
O["collar_d1_detail"] = [info(v) for v in sorted(d1)][:120]
O["collar_d2_detail"] = [info(v) for v in sorted(d2)][:120]

# how many R3-THUMB vertices have dT > R_TT and sT in the distal band?
R_TT = 10.4735
dist_th = [i for i in range(NV) if R3[i] == "THUMB" and sT[i] >= 90.0]
O["r3_thumb_sT_ge_90"] = len(dist_th)
O["r3_thumb_sT_ge_90_dT_hist"] = dict(Counter(int(dT[i] // 5) * 5 for i in dist_th))
O["r3_thumb_sT_ge_90_dT_gt_RTT"] = len([i for i in dist_th if dT[i] > R_TT])
O["r3_thumb_sT_ge_90_bind_dom"] = dict(Counter(
    (max(W[i].items(), key=lambda kv: kv[1])[0] if W[i] else None) for i in dist_th))
O["r3_thumb_sT_ge_90_foreign"] = len([i for i in dist_th
                                      if any(g not in ("WRIST_R", "THUMB_CMC_R", "THUMB_MCP_R", "THUMB_IP_R")
                                             for g in W[i])])

json.dump(O, open(os.path.join(R1E, "_tmp", "r1e_probe5.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("PROBE5_DONE")
