# =====================================================================================
# STAGE5B R1E -- READ-ONLY PROBE 3 : spatial identity of the collar / sheet
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

bpy.ops.wm.open_mainfile(filepath=R2A)
ob2 = bpy.data.objects[MESH_OBJ]; rig2 = bpy.data.objects[RIG_OBJ]; MW2 = ob2.matrix_world.copy()


def bone(nm, head=True):
    b = rig2.data.bones[nm]
    return MW2 @ (b.head_local if head else b.tail_local)


O = {}
O["bone_heads_mm"] = {nm: [round(c * MM, 3) for c in bone(nm)] for nm in
                      ("INDEX_MCP_R", "INDEX_PIP_R", "INDEX_DIP_R", "THUMB_MCP_R",
                       "THUMB_IP_R", "THUMB_CMC_R", "WRIST_R")}
O["index_tip_bone_tail_mm"] = [round(c * MM, 3) for c in bone("INDEX_DIP_R", False)]
O["thumb_tip_bone_tail_mm"] = [round(c * MM, 3) for c in bone("THUMB_IP_R", False)]

names = [1228, 1076, 693, 2153, 702, 2155, 689, 2157, 2156, 3196, 2160, 3197, 2189, 1061, 284, 695, 2178,
         2166, 692, 2169, 704, 3199, 2176, 3203, 149, 1053]
O["vertex_positions_mm"] = dict((str(v), {"R3": R3[v], "pos": [round(c * MM, 3) for c in V0[v]],
                                          "in_cap": v in CAP, "in_nailT": v in NAIL_T,
                                          "in_nailI": v in NAIL_I, "in_web": v in WEB})
                                for v in names)

# which component
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
O["comp_of"] = dict((str(v), ("body" if v in set(comps[0]) else "sheet")) for v in names)
BODY = set(comps[0]); SHEET = set(comps[1])

O["sheet_bbox_mm"] = [[round(min(V0[i][k] for i in SHEET) * MM, 2) for k in range(3)],
                      [round(max(V0[i][k] for i in SHEET) * MM, 2) for k in range(3)]]
O["body_bbox_mm"] = [[round(min(V0[i][k] for i in BODY) * MM, 2) for k in range(3)],
                     [round(max(V0[i][k] for i in BODY) * MM, 2) for k in range(3)]]
O["sheet_pts_mm"] = [[round(c * MM, 3) for c in V0[i]] for i in sorted(SHEET)][:0]
cs = sum((V0[i] for i in SHEET), Vector()) / len(SHEET)
O["sheet_centroid_mm"] = [round(c * MM, 3) for c in cs]
# index nail centroid (in sheet)
cn = sum((V0[i] for i in NAIL_I), Vector()) / len(NAIL_I)
O["index_nail_centroid_mm"] = [round(c * MM, 3) for c in cn]
ct = sum((V0[i] for i in CAP), Vector()) / len(CAP)
O["thumb_cap_centroid_mm"] = [round(c * MM, 3) for c in ct]
cw = sum((V0[i] for i in WEB), Vector()) / len(WEB)
O["first_web_centroid_mm"] = [round(c * MM, 3) for c in cw]

# distances of the collar rings to the index / thumb axes
POLY_I = [bone("INDEX_MCP_R"), bone("INDEX_MCP_R", False), bone("INDEX_PIP_R", False), bone("INDEX_DIP_R", False)]
POLY_T = [bone("THUMB_CMC_R"), bone("THUMB_CMC_R", False), bone("THUMB_MCP_R", False), bone("THUMB_IP_R", False)]


def dseg(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-18)))
    return (p - (a + ab * t)).length


def dpoly(p, poly):
    return min(dseg(p, poly[i], poly[i + 1]) for i in range(len(poly) - 1)) * MM


ringT = [2153, 2155, 2157, 2159, 2161, 2163, 2166, 2169, 3196, 3197, 3198, 3199, 3200, 3201, 3202, 3203]
ringI = [693, 702, 689, 696, 699, 698, 692, 704, 2156, 2160, 2164, 2167, 2170, 2172, 2174, 2176]
O["ring_THUMBside_geometry"] = [{"v": v, "dI_mm": round(dpoly(V0[v], POLY_I), 3),
                                 "dT_mm": round(dpoly(V0[v], POLY_T), 3), "R3": R3[v]}
                                for v in ringT]
O["ring_INDEXside_geometry"] = [{"v": v, "dI_mm": round(dpoly(V0[v], POLY_I), 3),
                                 "dT_mm": round(dpoly(V0[v], POLY_T), 3), "R3": R3[v]}
                                for v in ringI]

# global: dI / dT for R3 THUMB and R3 INDEX and all
for tag, S in (("R3_THUMB", [i for i in range(NV) if R3[i] == "THUMB"]),
               ("R3_INDEX", sorted(SHEET))):
    dd = sorted((dpoly(V0[i], POLY_I), i) for i in S)
    O["%s_dI_p05_p50_p95" % tag] = [round(dd[int(0.05 * (len(dd) - 1))][0], 3),
                                    round(dd[len(dd) // 2][0], 3),
                                    round(dd[int(0.95 * (len(dd) - 1))][0], 3)]
    ddt = sorted((dpoly(V0[i], POLY_T), i) for i in S)
    O["%s_dT_p05_p50_p95" % tag] = [round(ddt[int(0.05 * (len(ddt) - 1))][0], 3),
                                    round(ddt[len(ddt) // 2][0], 3),
                                    round(ddt[int(0.95 * (len(ddt) - 1))][0], 3)]

# the 173 defective THUMB vertices: nearest region identity by proximity to polylines
defc = [i for i in range(NV) if R3[i] == "THUMB"
        and any(g not in ("WRIST_R", "THUMB_CMC_R", "THUMB_MCP_R", "THUMB_IP_R") for g in [k for k in range(0)] )]
json.dump(O, open(os.path.join(R1E, "_tmp", "r1e_probe3.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)

# weights histogram of the 173 foreign THUMB vertices
_w = {}
for i in range(NV):
    pass
print("PROBE3_DONE")
