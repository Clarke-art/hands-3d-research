import os, sys, json, math
import bpy
from mathutils import Quaternion, Vector
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.append(HERE)
import s6br1b_common as K
ctx = K.B.build_context(); ref = ctx["ref"]; V0 = ref["V0"]; EDGES = ref["EDGES"]; NV = ref["NV"]
own = ctx["own_r1a"]; probe = K.load_probe_sets()
EDGE_LEN0 = [(V0[a]-V0[b]).length for a,b in EDGES]
cap = set(ref["cap"]["thumb_cap_vertex_ids"]); nail = set(ctx["nail"])
CM = json.load(open(K.PROVENANCE["stage6b_case_matrix"], encoding="utf-8"))
CASES = dict((c["case_id"], c) for c in CM["cases"])
bpy.ops.wm.open_mainfile(filepath=K.R1B_MASTER)
ob = bpy.data.objects[K.MESH_OBJ]; rig = bpy.data.objects[K.RIG_OBJ]; MW = ob.matrix_world.copy()
W0 = K.read_weights(ob, NV)
for mode in ("approved_chain_tip", "approved_distal_cap"):
    P = K.r2_partition(ctx, ref, thumb_seed_mode=mode)["partition"]
    C = K.build_corrected_ownership(ctx, ref, P, probe); corr = C["corrected"]
    mixedB = sum(1 for _k,a,b in probe["CLASS_B"] if corr[a]!=corr[b])
    bnd = [k for k,(a,b) in enumerate(EDGES) if corr[a]!=corr[b] and {corr[a],corr[b]}=={"THUMB","INDEX"}]
    changed = sum(1 for i in range(NV) if own[i]!=corr[i])
    print("=== mode=%s : changed=%d mixedB=%d R2bnd=%d cap_labels=%s nail_labels=%s" % (
        mode, changed, mixedB, len(bnd),
        sorted(set(corr[i] for i in cap)), sorted(set(corr[i] for i in nail))))
    if not bnd and mixedB==0:
        print("   (no boundary edges to test)")
        continue
    bep = set(v for k in bnd for v in EDGES[k])
    web = set(ctx["first_web"])
    VER,_ = K.weight_consistency(corr, W0)
    prim = set(i for i in C["domain"] if VER[i]=="WEIGHT_RECONCILIATION_REQUIRED" and i not in web)
    prim |= bep
    Wn,_ = K.trusted_interpolation(ref, W0, corr, set(prim))
    W2 = [dict(W0[i]) for i in range(NV)]
    for i in prim:
        nv = Wn[i]
        if not nv: continue
        it = sorted(nv.items(), key=lambda kv:(-kv[1],kv[0]))[:4]; s=sum(v for _g,v in it)
        if s<=0: continue
        W2[i] = dict((g,v/s) for g,v in it)
    K.push_weights(ob, NV, W2)
    for cid in ("CMC_OPP_30","CMC_MCP_L3","FULL_OPP_L3"):
        c = CASES[cid]; q = c["cmc_quaternion_local"]
        K.B.reset_pose(rig)
        pb = rig.pose.bones["THUMB_CMC_R"]; pb.rotation_mode='QUATERNION'
        pb.rotation_quaternion = Quaternion((q[0],q[1],q[2],q[3]))
        if c["mcp_deg"]:
            pbm=rig.pose.bones["THUMB_MCP_R"]; pbm.rotation_mode='QUATERNION'
            pbm.rotation_quaternion=Quaternion(Vector((1,0,0)), math.radians(-c["mcp_deg"]))
        if c["ip_deg"]:
            pbi=rig.pose.bones["THUMB_IP_R"]; pbi.rotation_mode='QUATERNION'
            pbi.rotation_quaternion=Quaternion(Vector((1,0,0)), math.radians(-c["ip_deg"]))
        K.B.update(); V = K.B.evaluate(ob, MW)[0]
        hm = max(((V[EDGES[k][0]]-V[EDGES[k][1]]).length/max(1e-18,EDGE_LEN0[k])) for k,_,_ in probe["CLASS_B"])
        ht = sum(1 for k,_,_ in probe["CLASS_B"] if ((V[EDGES[k][0]]-V[EDGES[k][1]]).length/max(1e-18,EDGE_LEN0[k]))>3.0)
        bm = max(((V[EDGES[k][0]]-V[EDGES[k][1]]).length/max(1e-18,EDGE_LEN0[k])) for k in bnd)
        bt = sum(1 for k in bnd if ((V[EDGES[k][0]]-V[EDGES[k][1]]).length/max(1e-18,EDGE_LEN0[k]))>3.0 and ((V[EDGES[k][0]]-V[EDGES[k][1]]).length*1000>5.0))
        capd = max((V[i]-V0[i]).length*1000 for i in cap)
        print("   %-12s hist_max=%.3f hist_torn=%d | bnd_max=%.3f bnd_torn=%d | cap_disp_max=%.4f mm" % (cid, hm, ht, bm, bt, capd))
    K.push_weights(ob, NV, W0)
