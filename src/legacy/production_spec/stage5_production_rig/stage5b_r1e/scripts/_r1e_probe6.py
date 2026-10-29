# =====================================================================================
# STAGE5B R1E -- READ-ONLY PROBE 6 : measured differential motion across the fold
# =====================================================================================
import os
import sys
import json
import math
import bpy
from mathutils import Vector, Quaternion

HERE = os.path.dirname(os.path.abspath(__file__))
PROD = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
R1E = os.path.abspath(os.path.join(HERE, ".."))
S5 = os.path.join(PROD, "stage5_production_rig")
S6D = os.path.join(PROD, "stage6_deformation")
sys.path.append(os.path.join(S6D, "stage6a", "scripts"))
import s6a_common as S6                                          # noqa: E402
MM = 1000.0
MESH_OBJ = "Hand  - Realistic"; RIG_OBJ = "RIGHT_HAND_PRODUCTION_RIG"
R1B = os.path.join(S5, "stage5b_r1b", "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend")
CM = dict((c["case_id"], c) for c in json.load(
    open(os.path.join(S6D, "stage6b", "STAGE6B_CASE_MATRIX.json"), encoding="utf-8"))["cases"])

bpy.ops.wm.open_mainfile(filepath=R1B)
ob = bpy.data.objects[MESH_OBJ]; rig = bpy.data.objects[RIG_OBJ]; MW = ob.matrix_world.copy()
NV = len(ob.data.vertices)
V0 = [(MW @ v.co).copy() for v in ob.data.vertices]
EDGES = [(e.vertices[0], e.vertices[1]) for e in ob.data.edges]
W = [dict() for _ in range(NV)]
for g in ob.vertex_groups:
    for i in range(NV):
        try:
            w = g.weight(i)
        except RuntimeError:
            continue
        if w > 0.0:
            W[i][g.name] = w


def pose(cid):
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
    return [(MW @ v.co).copy() for v in ob.evaluated_get(dg_).data.vertices]


def pose_s6a(bone, ang):
    S6.reset_pose(rig)
    S6.set_joint_rotation(rig, bone, -ang)
    bpy.context.view_layer.update()
    dg_ = bpy.context.evaluated_depsgraph_get()
    return [(MW @ v.co).copy() for v in ob.evaluated_get(dg_).data.vertices]


watch = [2189, 2192, 2569, 694, 695, 701, 703, 690, 2153, 2155, 2157, 2159, 693, 702, 689, 696,
         151, 1076, 1061, 1228, 228, 230, 2179, 2180, 2181, 2185, 296, 346]
O = {"watch": {}, "pairs": {}}
for v in watch:
    O["watch"][v] = {"W": dict((g, round(x, 4)) for g, x in sorted(W[v].items())),
                     "pos": [round(c * MM, 2) for c in V0[v]]}

POSES = [("FULL_OPP_L3", "s6b", "FULL_OPP_L3"), ("CMC_OPP_30", "s6b", "CMC_OPP_30"),
         ("TH_IP_45", "s6a", ("THUMB_IP_R", 45.0)), ("TH_MCP_45", "s6a", ("THUMB_MCP_R", 45.0)),
         ("CMC_MCP_L3", "s6b", "CMC_MCP_L3"), ("TH_IP_30", "s6a", ("THUMB_IP_R", 30.0))]
for name, kind, arg in POSES:
    V = pose(arg) if kind == "s6b" else pose_s6a(arg[0], arg[1])
    d = {}
    for v in watch:
        d[v] = round((V[v] - V0[v]).length * MM, 2)
    O["disp_mm_" + name] = d

# bind lengths along the fold path  cap -> d1 -> ringT -> ringI -> sheet
def bl(a, b):
    return round((V0[a] - V0[b]).length * MM, 3)


O["fold_path_bind_mm"] = {
    "2189-694": bl(2189, 694), "694-2153": bl(694, 2153), "2153-693": bl(2153, 693),
    "2192-703": bl(2192, 703), "703-2169": bl(703, 2169), "2169-704": bl(2169, 704),
    "2569-695": bl(2569, 695), "695-2159": bl(695, 2159), "2159-696": bl(2159, 696),
}
json.dump(O, open(os.path.join(R1E, "_tmp", "r1e_probe6.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)

print("--- displacement (mm) ---")
for k, v in O.items():
    if k.startswith("disp_mm_"):
        print(k, json.dumps(v))
print("--- fold bind ---")
print(json.dumps(O["fold_path_bind_mm"], ensure_ascii=False, indent=1))
print("PROBE6_DONE")
