# =====================================================================================
# STAGE5B R1E -- READ-ONLY PROBE 4 : where the severe stretch actually lives
# =====================================================================================
import os
import sys
import json
import math
from collections import Counter, deque

import bpy
from mathutils import Vector, Quaternion

HERE = os.path.dirname(os.path.abspath(__file__))
PROD = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
R1E = os.path.abspath(os.path.join(HERE, ".."))
R3D = os.path.join(PROD, "stage6_deformation", "stage6b_r3_thumb_tip_ownership_boundary")
S5 = os.path.join(PROD, "stage5_production_rig")
S6D = os.path.join(PROD, "stage6_deformation")
for _p in (os.path.join(S6D, "stage6a", "scripts"),):
    if _p not in sys.path:
        sys.path.append(_p)
import s6a_common as S6                                          # noqa: E402

MM = 1000.0
MESH_OBJ = "Hand  - Realistic"; RIG_OBJ = "RIGHT_HAND_PRODUCTION_RIG"
R1B = os.path.join(S5, "stage5b_r1b", "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend")
R1C = os.path.join(S5, "stage5b_r1c", "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1C.blend")
R1D = os.path.join(S5, "stage5b_r1d", "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1D.blend")
R2A = os.path.join(S5, "stage5a_r2a", "RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend")
CM = dict((c["case_id"], c) for c in json.load(
    open(os.path.join(S6D, "stage6b", "STAGE6B_CASE_MATRIX.json"), encoding="utf-8"))["cases"])

lab = json.load(open(os.path.join(R3D, "R3_OWNERSHIP_LABELS.json"), encoding="utf-8"))
R3 = lab["R3"]; BND = list(lab["boundary_edges_R3"])
CAP = set(lab["CAP"]); NAIL_T = set(lab["NAIL_THUMB"]); NAIL_I = set(lab["NAIL_INDEX"]); WEB = set(lab["WEB"])
PA = os.path.join(S6D, "stage6b_r1a_seam_provenance")
CLASS_A = [(e["edge_id"], e["endpoints"]["v0"], e["endpoints"]["v1"]) for e in json.load(
    open(os.path.join(PA, "STAGE6B_R1A_CLASS_A_VALID_WEB_EDGES.json"), encoding="utf-8"))["edges"]]
CLASS_B = [(e["edge_id"], e["endpoints"]["v0"], e["endpoints"]["v1"]) for e in json.load(
    open(os.path.join(PA, "STAGE6B_R1A_CLASS_B_OWNERSHIP_MISCLASSIFICATION.json"), encoding="utf-8"))["edges"]]

bpy.ops.wm.open_mainfile(filepath=R1B)
ob0 = bpy.data.objects[MESH_OBJ]; me0 = ob0.data; MW = ob0.matrix_world.copy()
NV = len(me0.vertices)
V0 = [(MW @ v.co).copy() for v in me0.vertices]
EDGES = [(e.vertices[0], e.vertices[1]) for e in me0.edges]
POLY0 = [tuple(p.vertices) for p in me0.polygons]
BL = [(V0[a] - V0[b]).length * MM for a, b in EDGES]

bpy.ops.wm.open_mainfile(filepath=R2A)
ob2 = bpy.data.objects[MESH_OBJ]; rig2 = bpy.data.objects[RIG_OBJ]; MW2 = ob2.matrix_world.copy()
CH = {"THUMB": ("THUMB_CMC_R", "THUMB_MCP_R", "THUMB_IP_R"),
      "INDEX": ("INDEX_MCP_R", "INDEX_PIP_R", "INDEX_DIP_R")}


def live_poly(c):
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


LT = live_poly(CH["THUMB"]); LI = live_poly(CH["INDEX"])
sT = [0.0] * NV; sI = [0.0] * NV
for i in range(NV):
    sT[i] = arc_of(LT, V0[i])[0]
    sI[i] = arc_of(LI, V0[i])[0]

O = {}
O["boundary_edge_midpoints_mm"] = [
    {"edge": k, "mid": [round(c * MM, 2) for c in (V0[EDGES[k][0]] + V0[EDGES[k][1]]) * 0.5],
     "a": EDGES[k][0], "b": EDGES[k][1], "aR3": R3[EDGES[k][0]], "bR3": R3[EDGES[k][1]],
     "bind_mm": round(BL[k], 3)} for k in BND]

# are the THUMB-side collar vertices adjacent to each other / to CAP / NAIL?
adj = {}
for a, b in EDGES:
    adj.setdefault(a, set()).add(b); adj.setdefault(b, set()).add(a)
adj = dict((k, sorted(v)) for k, v in adj.items())
ringT = [2153, 2155, 2157, 2159, 2161, 2163, 2166, 2169, 3196, 3197, 3198, 3199, 3200, 3201, 3202, 3203]
ringI = [693, 702, 689, 696, 699, 698, 692, 704, 2156, 2160, 2164, 2167, 2170, 2172, 2174, 2176]
O["ringT_adj_ringT"] = dict((v, len([u for u in adj[v] if u in ringT])) for v in ringT)
O["ringI_adj_ringI"] = dict((v, len([u for u in adj[v] if u in ringI])) for v in ringI)
O["ringT_steps_to_cap_nail"] = {}
seen = dict((v, 0) for v in ringT)
front = set(ringT); d = 0
hit = None
while front and d < 12:
    nxt = set()
    for u in front:
        for v in adj[u]:
            if v not in seen:
                seen[v] = d + 1; nxt.add(v)
    front = nxt; d += 1
    if hit is None and (front & (CAP | NAIL_T)):
        hit = d
O["ringT_ring_to_cap_or_nail"] = hit
O["ringI_ring_to_nail_index"] = None
seen2 = dict((v, 0) for v in ringI); front = set(ringI); d = 0; hit2 = None
while front and d < 12:
    nxt = set()
    for u in front:
        for v in adj[u]:
            if v not in seen2:
                seen2[v] = d + 1; nxt.add(v)
    front = nxt; d += 1
    if hit2 is None and (front & NAIL_I):
        hit2 = d
O["ringI_ring_to_index_nail"] = hit2

SEV_X = 5.0; SEV_MIN = 3.0


def run(path, label, cidlist):
    bpy.ops.wm.open_mainfile(filepath=path)
    ob = bpy.data.objects[MESH_OBJ]; rig = bpy.data.objects[RIG_OBJ]; mw = ob.matrix_world.copy()
    W = [dict() for _ in range(NV)]
    for g in ob.vertex_groups:
        for i in range(NV):
            try:
                w = g.weight(i)
            except RuntimeError:
                continue
            if w > 0.0:
                W[i][g.name] = w
    res = {}
    for cid in cidlist:
        c = CM[cid]
        q = c["cmc_quaternion_local"]
        S6.reset_pose(rig)
        pb = rig.pose.bones["THUMB_CMC_R"]; pb.rotation_mode = 'QUATERNION'
        pb.rotation_quaternion = Quaternion((q[0], q[1], q[2], q[3]))
        for bn, dg in (("THUMB_MCP_R", c["mcp_deg"]), ("THUMB_IP_R", c["ip_deg"])):
            if dg:
                p = rig.pose.bones[bn]; p.rotation_mode = 'QUATERNION'
                p.rotation_quaternion = Quaternion(Vector((1, 0, 0)), math.radians(-dg))
        bpy.context.view_layer.update()
        dg_ = bpy.context.evaluated_depsgraph_get()
        V = [(mw @ v.co).copy() for v in ob.evaluated_get(dg_).data.vertices]
        sev = []
        for k, (a, b) in enumerate(EDGES):
            if BL[k] <= SEV_MIN:
                continue
            r = (V[a] - V[b]).length * MM / BL[k]
            if r > SEV_X:
                sev.append({"edge": k, "a": a, "b": b, "ratio": round(r, 3),
                            "bind_mm": round(BL[k], 3),
                            "posed_mm": round((V[a] - V[b]).length * MM, 3),
                            "aR3": R3[a], "bR3": R3[b], "a_sT": round(sT[a], 2), "b_sT": round(sT[b], 2),
                            "a_sI": round(sI[a], 2), "b_sI": round(sI[b], 2),
                            "a_W": dict((g, round(v, 4)) for g, v in sorted(W[a].items())),
                            "b_W": dict((g, round(v, 4)) for g, v in sorted(W[b].items())),
                            "a_comp": None, "b_comp": None,
                            "a_pos": [round(x * MM, 2) for x in V0[a]],
                            "b_pos": [round(x * MM, 2) for x in V0[b]],
                            "in_classB": k in set(x[0] for x in CLASS_B),
                            "a_onBnd": a in ringT or a in ringI, "b_onBnd": b in ringT or b in ringI})
        res[cid] = sev
    return res


R = {"R1B": run(R1B, "R1B", ["CMC_OPP_30", "FULL_OPP_L3"]),
     "R1C": run(R1C, "R1C", ["CMC_OPP_30", "FULL_OPP_L3"]),
     "R1D": run(R1D, "R1D", ["CMC_OPP_30", "FULL_OPP_L3"])}
O["severe"] = dict((L, dict((c, {"n": len(v), "list": v}) for c, v in d.items())) for L, d in R.items())
O["severe_summary"] = dict((L, dict((c, {"n": len(v),
                                        "classB": len([x for x in v if x["in_classB"]]),
                                        "on_collar_ring": len([x for x in v if x["a_onBnd"] or x["b_onBnd"]])})
                               for c, v in d.items())) for L, d in R.items())

json.dump(O, open(os.path.join(R1E, "_tmp", "r1e_probe4.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("PROBE4_DONE")
