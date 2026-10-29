import os, sys, json, math
import bpy
from mathutils import Vector, Quaternion
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.append(HERE)
sys.path.append(os.path.join(HERE,"..","..","..","stage6_deformation","stage6b_r1b","scripts"))
import s6br1b_common as K
ctx=K.B.build_context(); ref=ctx["ref"]; V0=ref["V0"]; NV=ref["NV"]; EDGES=ref["EDGES"]
probe=K.load_probe_sets(); PART=K.r2_partition(ctx,ref)
CC=K.build_corrected_ownership(ctx,ref,PART["partition"],probe)
CORR=CC["corrected"]; DOM=set(CC["domain"]); bnd=CC["r2_boundary_edges"]
print("R2 corrected THUMB|INDEX boundary edges:",len(bnd))
rows=[]
for k in bnd:
    a,b=EDGES[k]
    rows.append((round((V0[a]-V0[b]).length*1000,3),k,a,b,CORR[a],CORR[b]))
rows.sort()
for r in rows:
    print("   bind %7.3f mm  e%-5d  v%-5d(%s) - v%-5d(%s)"%(r[0],r[1],r[2],r[4],r[3],r[5]))
CM=dict((c["case_id"],c) for c in json.load(open(os.path.join(HERE,"..","..","..","stage6_deformation","stage6b","STAGE6B_CASE_MATRIX.json"),encoding="utf-8"))["cases"])
FILES=[("R1B",K.R1B_MASTER),("R1C",K.R1C_MASTER),("R1D",os.path.join(HERE,"..","RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1D.blend"))]
print("\nedge 498 (v160-v1080) posed length mm:")
for lbl,p in FILES:
    bpy.ops.wm.open_mainfile(filepath=p)
    ob=bpy.data.objects[K.MESH_OBJ]; rig=bpy.data.objects[K.RIG_OBJ]; MW=ob.matrix_world.copy()
    W=K.read_weights(ob,NV)
    res={}
    K.B.S6.reset_pose(rig); K.B.S6.set_joint_rotation(rig,"THUMB_IP_R",-45.0); K.B.update()
    V=K.RB.evaluate(ob,MW)[0]; res["TH_IP_45"]=round((V[160]-V[1080]).length*1000,2)
    for cid in ("CMC_OPP_30","FULL_OPP_L3"):
        c=CM[cid]; q=c["cmc_quaternion_local"]; K.B.reset_pose(rig)
        pb=rig.pose.bones["THUMB_CMC_R"]; pb.rotation_mode='QUATERNION'
        pb.rotation_quaternion=Quaternion((q[0],q[1],q[2],q[3]))
        for bn,dg in (("THUMB_MCP_R",c["mcp_deg"]),("THUMB_IP_R",c["ip_deg"])):
            if dg:
                pp=rig.pose.bones[bn]; pp.rotation_mode='QUATERNION'
                pp.rotation_quaternion=Quaternion(Vector((1,0,0)),math.radians(-dg))
        K.B.update(); V=K.RB.evaluate(ob,MW)[0]
        res[cid]=round((V[160]-V[1080]).length*1000,2)
    print("  %s %s | W160=%s W1080=%s"%(lbl,res,
        {g:round(v,3) for g,v in sorted(W[160].items())},{g:round(v,3) for g,v in sorted(W[1080].items())}))
