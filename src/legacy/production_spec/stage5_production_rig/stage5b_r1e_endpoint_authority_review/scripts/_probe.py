# =====================================================================================
# R1E_ENDPOINT_WEIGHT_AUTHORITY_REVIEW -- reconnaissance probe (READ ONLY)
# =====================================================================================
import os
import sys
import json
from collections import Counter, deque

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
AUD = os.path.abspath(os.path.join(HERE, ".."))
PROD = os.path.abspath(os.path.join(AUD, "..", ".."))
R1E_DIR = os.path.join(PROD, "stage5_production_rig", "stage5b_r1e")
sys.path.append(os.path.join(R1E_DIR, "scripts"))
import s5b_r1e_common as C                                          # noqa: E402

MM = C.MM
CAND_R1E = os.path.join(R1E_DIR, "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1E.blend")
TMP = os.path.join(AUD, "_tmp")
os.makedirs(TMP, exist_ok=True)

LAB = json.load(open(C.R3_FILES["r3_ownership_labels"], encoding="utf-8"))
R3 = list(LAB["R3"])
BND_IDS = list(LAB["boundary_edges_R3"])
CAP = sorted(LAB["CAP"]); NAIL_T = set(LAB["NAIL_THUMB"]); NAIL_I = set(LAB["NAIL_INDEX"])
WEB = set(LAB["WEB"])

bpy.ops.wm.open_mainfile(filepath=C.R1B_MASTER)
ob = bpy.data.objects[C.MESH_OBJ]; rig = bpy.data.objects[C.RIG_OBJ]
MW = ob.matrix_world.copy()
NV = len(ob.data.vertices)
V0 = [(MW @ v.co).copy() for v in ob.data.vertices]
EDGES = [(e.vertices[0], e.vertices[1]) for e in ob.data.edges]
POLY = [tuple(p.vertices) for p in ob.data.polygons]
BIND = [(V0[a] - V0[b]).length * MM for a, b in EDGES]
W_R1B = C.read_weights(ob, NV)
ADJ = {}
for a, b in EDGES:
    ADJ.setdefault(a, set()).add(b); ADJ.setdefault(b, set()).add(a)
ADJ = dict((k, sorted(v)) for k, v in ADJ.items())
JOINT = {}
for bn in ("INDEX_MCP_R", "INDEX_PIP_R", "THUMB_CMC_R", "THUMB_MCP_R", "THUMB_IP_R", "WRIST_R"):
    JOINT[bn] = MW @ Vector(rig.data.bones[bn].head_local)

bpy.ops.wm.open_mainfile(filepath=C.R2A)
_o2 = bpy.data.objects[C.MESH_OBJ]; _r2 = bpy.data.objects[C.RIG_OBJ]
_mw2 = _o2.matrix_world.copy()
LIVE = {}
for _d, _ch in C.BONE_CHAIN.items():
    _p = [_mw2 @ Vector(_r2.data.bones[_ch[0]].head_local)]
    for _nm in _ch:
        _p.append(_mw2 @ Vector(_r2.data.bones[_nm].tail_local))
    LIVE[_d] = _p
XIJ = {}
for _d, _p in LIVE.items():
    _acc, _a = 0.0, [0.0]
    for _k in range(len(_p) - 1):
        _acc += (_p[_k + 1] - _p[_k]).length; _a.append(_acc * MM)
    XIJ[_d] = _a
LIVEJ = {}
for nm in ("INDEX_MCP_R", "INDEX_PIP_R", "INDEX_DIP_R", "THUMB_CMC_R", "THUMB_MCP_R", "THUMB_IP_R"):
    LIVEJ[nm] = _mw2 @ Vector(_r2.data.bones[nm].head_local)
sT = [C.arc_of(LIVE["THUMB"], V0[i])[0] for i in range(NV)]
dT = [C.arc_of(LIVE["THUMB"], V0[i])[1] for i in range(NV)]
sI = [C.arc_of(LIVE["INDEX"], V0[i])[0] for i in range(NV)]
dI = [C.arc_of(LIVE["INDEX"], V0[i])[1] for i in range(NV)]
s_MCP_T, s_IP_T = XIJ["THUMB"][1], XIJ["THUMB"][2]
s_PIP_I = XIJ["INDEX"][2]
MED = sorted(BIND)[len(BIND) // 2]
tubeT = sorted(dT[i] for i in range(NV) if R3[i] == "THUMB" and s_MCP_T <= sT[i] <= s_IP_T)
baseT = sorted(dT[i] for i in range(NV) if R3[i] == "THUMB" and sT[i] <= s_MCP_T)
R_TT_T = tubeT[len(tubeT) // 2] if tubeT else 8.0
R_MAX_T = max(baseT[int(0.95 * (len(baseT) - 1))] if baseT else 2.0 * R_TT_T, R_TT_T * 1.25)

bpy.ops.wm.open_mainfile(filepath=CAND_R1E)
oE = bpy.data.objects[C.MESH_OBJ]
W_R1E = C.read_weights(oE, NV)


def semantic(v):
    if v in CAP: return "DISTAL_CAP"
    if v in NAIL_T: return "THUMB_NAIL"
    if v in NAIL_I: return "INDEX_NAIL"
    if v in WEB: return "FIRST_WEB"
    d = R3[v]
    if d == "THUMB":
        if sT[v] >= s_IP_T - MED: return "THUMB_DISTAL"
        if sT[v] >= s_MCP_T - MED: return "THUMB_MCP_TRANSITION"
        if dT[v] <= R_MAX_T: return "THUMB_CMC_TRANSITION"
        return "THENAR"
    if d == "INDEX":
        if sI[v] <= s_PIP_I: return "INDEX_ROOT"
        return "INDEX_PHALANX"
    if d == "wrist":
        if dT[v] > R_TT_T and sT[v] <= s_MCP_T + MED: return "THENAR"
        return "PALM"
    return "OTHER_" + d


SEM = [semantic(v) for v in range(NV)]
COLLAR = set()
for k in BND_IDS:
    COLLAR.update(EDGES[k])
DIST_C0 = C.rings_from(ADJ, COLLAR, 64)
GD_CAP = C.rings_from(ADJ, set(CAP), 64)
GD_WEB = C.rings_from(ADJ, WEB, 64)
GD_PALM = C.rings_from(ADJ, set(v for v in range(NV) if SEM[v] in ("PALM", "THENAR")), 64)
INGI = sorted(i for i in COLLAR if R3[i] == "INDEX")
INGT = sorted(i for i in COLLAR if R3[i] == "THUMB")

OUT = {
    "collar": [], "crossregion": {}, "web_adj": {},
    "live_XIJ": XIJ, "R_TT_T": R_TT_T, "R_MAX_T": R_MAX_T,
    "joints_live_mm": dict((k, [round(c * MM, 4) for c in v]) for k, v in LIVEJ.items()),
    "n_collar": len(COLLAR), "n_index_side": len(INGI), "n_thumb_side": len(INGT),
}
for v in sorted(COLLAR):
    r1 = Counter(SEM[u] for u in ADJ[v])
    r2 = set()
    for u in ADJ[v]:
        r2.update(ADJ[u])
    r2.discard(v); r2 -= set(ADJ[v])
    r1sem = Counter(SEM[u] for u in ADJ[v])
    r2sem = Counter(SEM[u] for u in r2)
    faces = [fi for fi, p in enumerate(POLY) if v in p]
    OUT["collar"].append({
        "v": v, "R3": R3[v], "side": ("INDEX" if R3[v] == "INDEX" else
                                      "THUMB" if R3[v] == "THUMB" else R3[v]),
        "semantic": SEM[v],
        "sT": round(sT[v], 3), "dT": round(dT[v], 3),
        "sI": round(sI[v], 3), "dI": round(dI[v], 3),
        "dist_INDEX_MCP_mm": round((V0[v] - LIVEJ["INDEX_MCP_R"]).length * MM, 3),
        "dist_INDEX_PIP_mm": round((V0[v] - LIVEJ["INDEX_PIP_R"]).length * MM, 3),
        "dist_THUMB_CMC_mm": round((V0[v] - LIVEJ["THUMB_CMC_R"]).length * MM, 3),
        "dist_THUMB_MCP_mm": round((V0[v] - LIVEJ["THUMB_MCP_R"]).length * MM, 3),
        "dist_THUMB_IP_mm": round((V0[v] - LIVEJ["THUMB_IP_R"]).length * MM, 3),
        "g_to_first_web": GD_WEB.get(v, -1),
        "g_to_distal_cap": GD_CAP.get(v, -1),
        "g_to_palm_thenar": GD_PALM.get(v, -1),
        "in_first_web": v in WEB,
        "adj_first_web": sorted(u for u in ADJ[v] if u in WEB),
        "n_faces": len(faces),
        "ring1_sem": dict(r1sem.most_common()),
        "ring2_sem": dict(r2sem.most_common()),
        "W_R1B": dict((g, round(w, 5)) for g, w in sorted(W_R1B[v].items())),
        "W_R1E": dict((g, round(w, 5)) for g, w in sorted(W_R1E[v].items())),
        "dom_R1B": (max(W_R1B[v].items(), key=lambda kv: kv[1])[0] if W_R1B[v] else None),
        "dom_R1E": (max(W_R1E[v].items(), key=lambda kv: kv[1])[0] if W_R1E[v] else None),
    })

# ---- cross-region thumb influence census
def census(W, tag):
    res = {"thumb_weights_on_non_thumb": [], "index_mcp_on_thumb": [],
           "thumb_on_wrist_palm": [], "by_dom_semantic": {}}
    for v in range(NV):
        tc = W[v].get("THUMB_CMC_R", 0.0)
        tm = W[v].get("THUMB_MCP_R", 0.0)
        ti = W[v].get("THUMB_IP_R", 0.0)
        im = W[v].get("INDEX_MCP_R", 0.0)
        if R3[v] not in ("THUMB",) and (tc > 1e-6 or tm > 1e-6 or ti > 1e-6):
            res["thumb_weights_on_non_thumb"].append(
                {"v": v, "R3": R3[v], "sem": SEM[v], "THUMB_CMC_R": round(tc, 5),
                 "THUMB_MCP_R": round(tm, 5), "THUMB_IP_R": round(ti, 5)})
        if R3[v] == "THUMB" and im > 1e-6:
            res["index_mcp_on_thumb"].append({"v": v, "sem": SEM[v], "INDEX_MCP_R": round(im, 5),
                                              "in_web": v in WEB})
        if R3[v] == "wrist" and (tc > 1e-6 or tm > 1e-6):
            res["thumb_on_wrist_palm"].append({"v": v, "sem": SEM[v],
                                               "THUMB_CMC_R": round(tc, 5),
                                               "THUMB_MCP_R": round(tm, 5)})
    res["by_dom_semantic"] = dict(Counter(
        (d["R3"] + "|" + d["sem"]) for d in res["thumb_weights_on_non_thumb"]).most_common())
    hs = dict(Counter((d["sem"]) for d in res["thumb_weights_on_non_thumb"]).most_common())
    res["counts"] = {"thumb_weights_on_non_thumb": len(res["thumb_weights_on_non_thumb"]),
                     "index_mcp_on_thumb": len(res["index_mcp_on_thumb"]),
                     "thumb_on_wrist_palm": len(res["thumb_on_wrist_palm"]),
                     "semantic_hist": hs}
    res["tag"] = tag
    return res


OUT["crossregion"]["R1B"] = census(W_R1B, "R1B")
OUT["crossregion"]["R1E"] = census(W_R1E, "R1E")

# ---- wider: does THUMB_CMC / THUMB_MCP influence R3-INDEX at all?
for tag, W in (("R1B", W_R1B), ("R1E", W_R1E)):
    idx = [v for v in range(NV) if R3[v] == "INDEX"]
    with_t = [v for v in idx if W[v].get("THUMB_CMC_R", 0) > 1e-6 or W[v].get("THUMB_MCP_R", 0) > 1e-6]
    OUT["crossregion"]["%s_index_with_thumb" % tag] = {
        "n_index_total": len(idx), "n_index_with_thumb_weight": len(with_t),
        "examples": [{"v": v, "sem": SEM[v], "g_to_web": GD_WEB.get(v, -1),
                      "W": dict((g, round(w, 4)) for g, w in sorted(W[v].items()))}
                     for v in with_t[:20]],
        "g_to_web_hist": dict(Counter(GD_WEB.get(v, -1) for v in with_t).most_common(12)),
    }

with open(os.path.join(TMP, "probe.json"), "w", encoding="utf-8") as f:
    json.dump(OUT, f, indent=1, ensure_ascii=False)
print("PROBE DONE")
