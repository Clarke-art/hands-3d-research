# =====================================================================================
# STAGE5B R1E -- READ-ONLY PROBE 2 : the operative R3-vs-R1B-weight defects
# =====================================================================================
import os
import sys
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
MESH_OBJ = "Hand  - Realistic"
RIG_OBJ = "RIGHT_HAND_PRODUCTION_RIG"
R1B_MASTER = os.path.join(S5, "stage5b_r1b", "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend")
R2A = os.path.join(S5, "stage5a_r2a", "RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend")

lab = json.load(open(os.path.join(R3D, "R3_OWNERSHIP_LABELS.json"), encoding="utf-8"))
R3, R2 = lab["R3"], lab["R2"]
BND_R3 = list(lab["boundary_edges_R3"])
CAP = set(lab["CAP"]); NAIL_T = set(lab["NAIL_THUMB"]); NAIL_I = set(lab["NAIL_INDEX"]); WEB = set(lab["WEB"])

bpy.ops.wm.open_mainfile(filepath=R1B_MASTER)
ob = bpy.data.objects[MESH_OBJ]
me = ob.data
MW = ob.matrix_world.copy()
NV = len(me.vertices)
V0 = [(MW @ v.co).copy() for v in me.vertices]
EDGES = [(e.vertices[0], e.vertices[1]) for e in me.edges]
WOLD = [dict() for _ in range(NV)]
for g in ob.vertex_groups:
    for i in range(NV):
        try:
            w = g.weight(i)
        except RuntimeError:
            continue
        if w > 0.0:
            WOLD[i][g.name] = w

adj = {}
for a, b in EDGES:
    adj.setdefault(a, set()).add(b)
    adj.setdefault(b, set()).add(a)
adj = dict((k, sorted(v)) for k, v in adj.items())

bpy.ops.wm.open_mainfile(filepath=R2A)
ob2 = bpy.data.objects[MESH_OBJ]; rig2 = bpy.data.objects[RIG_OBJ]; MW2 = ob2.matrix_world.copy()
CH = {"THUMB": ("THUMB_CMC_R", "THUMB_MCP_R", "THUMB_IP_R"),
      "INDEX": ("INDEX_MCP_R", "INDEX_PIP_R", "INDEX_DIP_R")}


def live_poly(chain):
    p = [MW2 @ Vector(rig2.data.bones[chain[0]].head_local)]
    for nm in chain:
        p.append(MW2 @ Vector(rig2.data.bones[nm].tail_local))
    return p


def arc_of(pts, v):
    bd, bs, acc = 1e18, 0.0, 0.0
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        ab = b - a
        t = max(0.0, min(1.0, (v - a).dot(ab) / max(ab.length_squared, 1e-18)))
        d = (v - (a + ab * t)).length
        if d < bd:
            bd, bs = d, (acc + t * ab.length) * MM
        acc += ab.length
    return bs, bd * MM


LT = live_poly(CH["THUMB"]); LI = live_poly(CH["INDEX"])
sT = [0.0] * NV; dT = [0.0] * NV; sI = [0.0] * NV; dI = [0.0] * NV
for i in range(NV):
    sT[i], dT[i] = arc_of(LT, V0[i])
    sI[i], dI[i] = arc_of(LI, V0[i])

GD = {"WRIST_R": "wrist"}
for D in ("THUMB", "INDEX", "MIDDLE", "RING", "LITTLE"):
    for st in ("MCP", "PIP", "DIP", "CMC", "IP"):
        GD["%s_%s_R" % (D, st)] = D
dom = [GD.get(max(WOLD[i].items(), key=lambda kv: kv[1])[0], "wrist") if WOLD[i] else None
       for i in range(NV)]

O = {}
TH = [i for i in range(NV) if R3[i] == "THUMB"]
IX = [i for i in range(NV) if R3[i] == "INDEX"]
O["r3_thumb"] = len(TH)
O["r3_index"] = len(IX)
O["r3_thumb_dominant"] = dict(Counter(dom[i] for i in TH))
O["r3_index_dominant"] = dict(Counter(dom[i] for i in IX))

FORBID_THUMB = ["INDEX_PIP_R", "INDEX_DIP_R"]
FORBID_INDEX = ["THUMB_IP_R", "THUMB_MCP_R", "THUMB_CMC_R"]
th_ip_pip = [i for i in TH if any(g in WOLD[i] for g in FORBID_THUMB)]
th_idx_mcp = [i for i in TH if "INDEX_MCP_R" in WOLD[i]]
ix_th = [i for i in IX if any(g in WOLD[i] for g in FORBID_INDEX)]
O["r3_thumb_carrying_index_pip_or_dip"] = len(th_ip_pip)
O["r3_thumb_carrying_index_pip_or_dip_list"] = th_ip_pip
O["r3_thumb_carrying_index_mcp"] = len(th_idx_mcp)
O["r3_thumb_carrying_index_mcp_list"] = th_idx_mcp
O["r3_thumb_carrying_index_mcp_in_web"] = len([i for i in th_idx_mcp if i in WEB])
O["r3_index_carrying_thumb_groups"] = len(ix_th)
O["r3_index_carrying_thumb_groups_list"] = ix_th
O["r3_index_carrying_thumb_groups_dominant"] = dict(Counter(dom[i] for i in ix_th))
O["r3_thumb_dominant_index_vertices"] = len([i for i in TH if dom[i] == "INDEX"])

# ---- boundary edge detail
bnd = []
for k in BND_R3:
    a, b = EDGES[k]
    bnd.append({"edge": k, "a": a, "b": b, "bind_mm": round((V0[a] - V0[b]).length * MM, 4),
                "a_lab": R3[a], "b_lab": R3[b], "a_R2": R2[a], "b_R2": R2[b],
                "a_sT": round(sT[a], 3), "b_sT": round(sT[b], 3),
                "a_sI": round(sI[a], 3), "b_sI": round(sI[b], 3),
                "a_dI": round(dI[a], 3), "b_dI": round(dI[b], 3),
                "a_dT": round(dT[a], 3), "b_dT": round(dT[b], 3),
                "a_W": dict((g, round(v, 4)) for g, v in sorted(WOLD[a].items())),
                "b_W": dict((g, round(v, 4)) for g, v in sorted(WOLD[b].items())),
                "a_dom": dom[a], "b_dom": dom[b]})
O["boundary_edge_detail"] = bnd

# ---- collar neighbourhood: 2 ring around boundary vertices, R3 label + s
bndv = set()
for k in BND_R3:
    bndv.update(EDGES[k])
ring1 = set()
for v in sorted(bndv):
    ring1.update(adj[v])
ring2 = set()
for v in sorted(ring1 - bndv):
    ring2.update(adj[v])
O["collar_bnd_verts"] = sorted(bndv)
O["collar_ring1_only"] = sorted(ring1 - bndv)
O["collar_ring2_only"] = sorted(ring2 - bndv - ring1)
O["collar_ring1_label_counts"] = dict(Counter(R3[v] for v in ring1))
O["collar_ring2_label_counts"] = dict(Counter(R3[v] for v in ring2))

# ---- sheet / body split again, with s ranges per label
cut = set(tuple(sorted(EDGES[k])) for k in BND_R3)
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
O["sheet_n"] = len(SHEET)
# where does the sheet sit in index arc? histogram
edges_bins = [0, 10, 20, 30, 40, 50, 60, 70]
h = Counter()
for i in SHEET:
    h[min(6, int(sI[i] // 10))] += 1
O["sheet_sI_hist"] = {("%d-%d" % (b * 10, b * 10 + 10)): h.get(b, 0) for b in range(7)}
O["sheet_thumb_vertices"] = len([i for i in SHEET if R3[i] == "THUMB"])
O["body_index_vertices"] = len([i for i in BODY if R3[i] == "INDEX"])
O["body_index_vertices_list"] = sorted(i for i in BODY if R3[i] == "INDEX")
O["body_index_sI_range"] = ([round(min(sI[i] for i in BODY if R3[i] == "INDEX"), 3),
                             round(max(sI[i] for i in BODY if R3[i] == "INDEX"), 3)]
                            if [i for i in BODY if R3[i] == "INDEX"] else None)
O["body_index_dominant"] = dict(Counter(dom[i] for i in BODY if R3[i] == "INDEX"))
O["body_index_carrying_thumb"] = len([i for i in BODY if R3[i] == "INDEX"
                                      and any(g in WOLD[i] for g in FORBID_INDEX)])

# ---- foreign influence census
TH_ALLOW = {"WRIST_R", "THUMB_CMC_R", "THUMB_MCP_R", "THUMB_IP_R"}
IX_ALLOW = {"WRIST_R", "INDEX_MCP_R", "INDEX_PIP_R", "INDEX_DIP_R"}
O["r3_thumb_weights_outside_allow_all"] = len([i for i in TH if any(g not in TH_ALLOW for g in WOLD[i])])
O["r3_index_weights_outside_allow_all"] = len([i for i in IX if any(g not in IX_ALLOW for g in WOLD[i])])
O["r3_index_weights_outside_allow_sample"] = [
    {"v": i, "lab": R3[i], "W": dict((g, round(v2, 4)) for g, v2 in sorted(WOLD[i].items())),
     "sI": round(sI[i], 3)} for i in sorted(IX)[:0]]
O["r3_index_outside_allow_list"] = sorted(i for i in IX if any(g not in IX_ALLOW for g in WOLD[i]))[:400]

# ---- cap / web weights
O["cap_detail"] = [{"v": i, "sT": round(sT[i], 3), "R3": R3[i],
                    "W": dict((g, round(v2, 4)) for g, v2 in sorted(WOLD[i].items()))} for i in sorted(CAP)]
O["web_detail"] = [{"v": i, "sT": round(sT[i], 3), "sI": round(sI[i], 3), "R3": R3[i],
                    "W": dict((g, round(v2, 4)) for g, v2 in sorted(WOLD[i].items()))} for i in sorted(WEB)]
O["web_with_ip"] = sorted(i for i in WEB if WOLD[i].get("THUMB_IP_R", 0.0) > 0.0)
O["nail_thumb_detail"] = [{"v": i, "sT": round(sT[i], 3), "R3": R3[i],
                           "W": dict((g, round(v2, 4)) for g, v2 in sorted(WOLD[i].items()))}
                          for i in sorted(NAIL_T)]

json.dump(O, open(os.path.join(R1E, "_tmp", "r1e_probe2.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print("PROBE2_DONE")
