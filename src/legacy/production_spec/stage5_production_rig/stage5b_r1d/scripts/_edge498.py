import os, sys, json, math
import bpy
from mathutils import Vector, Quaternion
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.append(HERE)
sys.path.append(os.path.join(HERE,"..","..","..","stage6_deformation","stage6b_r1b","scripts"))
import s6br1b_common as K
ctx=K.B.build_context(); ref=ctx["ref"]; V0=ref["V0"]; NV=ref["NV"]; POLY=ref["TOPO0"]; EDGES=ref["EDGES"]
probe=K.load_probe_sets(); PART=K.r2_partition(ctx,ref)
CC=K.build_corrected_ownership(ctx,ref,PART["partition"],probe)
CORR=CC["corrected"]; DOM=set(CC["domain"]); P2=CC["r2"]; O1=CC["own_r1a"]
cap=set(ctx["cap"]); web=set(ctx["first_web"])
print("v160 : own_r1a=%s r2=%s corrected=%s inDomain=%s inCap=%s inWeb=%s"%(O1[160],P2[160],CORR[160],160 in DOM,160 in cap,160 in web))
print("v1080: own_r1a=%s r2=%s corrected=%s inDomain=%s inCap=%s inWeb=%s"%(O1[1080],P2[1080],CORR[1080],1080 in DOM,1080 in cap,1080 in web))
print("bind |v160-v1080| = %.4f mm"%((V0[160]-V0[1080]).length*1000))
from collections import Counter
grp={}
for i in (160,1080):
    nb=[v for a,b in EDGES for v in ((b,) if a==i else ((a,) if b==i else ()))]
    grp[i]=Counter(CORR[v] for v in nb)
    print("v%-5d neighbours=%d  corrected labels=%s"%(i,len(nb),dict(grp[i])))
CM=dict((c["case_id"],c) for c in json.load(open(os.path.join(HERE,"..","..","..","stage6_deformation","stage6b","STAGE6B_CASE_MATRIX.json"),encoding="utf-8"))["cases"])
def apply(rig,cid,mode):
    c=CM[cid]
    if mode=="s6a":
        K.B.S6.reset_pose(rig); K.B.S6.set_joint_rotation(rig,"THUMB_IP_R",-45.0); return
    q=c["cmc_quaternion_local"]; K.B.reset_pose(rig)
    pb=rig.pose.bones["THUMB_CMC_R"]; pb.rotation_mode='QUATERNION'
    pb.rotation_quaternion=Quaternion((q[0],q[1],q[2],q[3]))
    for bn,dg in (("THUMB_MCP_R",c["mcp_deg"]),("THUMB_IP_R",c["ip_deg"])):
        if dg:
            p=rig.pose.bones[bn]; p.rotation_mode='QUATERNION'
            p.rotation_quaternion=Quaternion(Vector((1,0,0)),math.radians(-dg))
    K.B.update()
FILES=[("R1B",K.R1B_MASTER),("R1C",K.R1C_MASTER),("R1D",os.path.join(HERE,"..","RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1D.blend"))]
for lbl,p in FILES:
    bpy.ops.wm.open_mainfile(filepath=p)
    ob=bpy.data.objects[K.MESH_OBJ]; rig=bpy.data.objects[K.RIG_OBJ]; MW=ob.matrix_world.copy()
    W=K.read_weights(ob,NV)
    out={}
    for cid,mode in (("TH_IP_45","s6a"),("FULL_OPP_L3","s6b"),("CMC_OPP_30","s6b")):
        apply(rig,cid,mode); K.B.update()
        V=K.RB.evaluate(ob,MW)[0]
        out[cid]=round((V[160]-V[1080]).length*1000,2)
    print("%s edge498 posed mm: %s | W160=%s W1080=%s"%(lbl,out,
        {g:round(v,3) for g,v in sorted(W[160].items())},{g:round(v,3) for g,v in sorted(W[1080].items())}))
