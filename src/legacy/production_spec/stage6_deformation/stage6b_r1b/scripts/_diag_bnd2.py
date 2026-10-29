import os, sys, json
import bpy
from mathutils import Quaternion
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.append(HERE)
import s6br1b_common as K
ctx = K.B.build_context(); ref = ctx["ref"]; V0 = ref["V0"]; EDGES = ref["EDGES"]
probe = K.load_probe_sets(); part = K.r2_partition(ctx, ref)["partition"]
C = K.build_corrected_ownership(ctx, ref, part, probe); corr = C["corrected"]
EDGE_LEN0 = [(V0[a]-V0[b]).length for a,b in EDGES]
bnd = [k for k,(a,b) in enumerate(EDGES) if corr[a]!=corr[b] and {corr[a],corr[b]}=={"THUMB","INDEX"}]
CM = json.load(open(K.PROVENANCE["stage6b_case_matrix"], encoding="utf-8"))
CASES = dict((c["case_id"], c) for c in CM["cases"])
res = {}
for label, path in (("R1B", K.R1B_MASTER), ("R1C", K.R1C_MASTER)):
    bpy.ops.wm.open_mainfile(filepath=path)
    ob = bpy.data.objects[K.MESH_OBJ]; rig = bpy.data.objects[K.RIG_OBJ]; MW = ob.matrix_world.copy()
    row = {}
    for cid in ("CMC_OPP_30", "FULL_OPP_L3"):
        c = CASES[cid]; q = c["cmc_quaternion_local"]
        K.B.reset_pose(rig)
        pb = rig.pose.bones["THUMB_CMC_R"]; pb.rotation_mode='QUATERNION'
        pb.rotation_quaternion = Quaternion((q[0],q[1],q[2],q[3]))
        if c["mcp_deg"]:
            pb2 = rig.pose.bones["THUMB_MCP_R"]; pb2.rotation_mode='QUATERNION'
            pb2.rotation_quaternion = Quaternion((1,0,0), 0.0)
            pb2.rotation_quaternion = Quaternion(__import__("mathutils").Vector((1,0,0)), __import__("math").radians(-c["mcp_deg"]))
        if c["ip_deg"]:
            pb3 = rig.pose.bones["THUMB_IP_R"]; pb3.rotation_mode='QUATERNION'
            pb3.rotation_quaternion = Quaternion(__import__("mathutils").Vector((1,0,0)), __import__("math").radians(-c["ip_deg"]))
        K.B.update(); V = K.B.evaluate(ob, MW)[0]
        row[cid] = dict((k, (V[EDGES[k][0]]-V[EDGES[k][1]]).length/max(1e-18, EDGE_LEN0[k])) for k in bnd)
    res[label] = row
print("edge   bind_mm  own            corr           CMC30_R1B CMC30_R1C  L3_R1B  L3_R1C")
for k in sorted(bnd):
    a,b = EDGES[k]
    print("e%-5d %7.3f  %-14s %-14s %8.3f %8.3f %8.3f %8.3f" % (
        k, EDGE_LEN0[k]*1000, str([ctx["own_r1a"][a],ctx["own_r1a"][b]]),
        str([corr[a],corr[b]]),
        res["R1B"]["CMC_OPP_30"][k], res["R1C"]["CMC_OPP_30"][k],
        res["R1B"]["FULL_OPP_L3"][k], res["R1C"]["FULL_OPP_L3"][k]))
