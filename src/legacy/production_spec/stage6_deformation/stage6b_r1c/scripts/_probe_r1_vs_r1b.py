import os, sys, json, math
import numpy as np
import bpy
from mathutils import Vector, Quaternion
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.append(HERE)
import r1c_pen_common as R
ctx=R.B.build_context(); ref=ctx["ref"]; V0=ref["V0"]; POLY=ctx["poly"]; NV=ref["NV"]
probe=R.K.load_probe_sets()
PART=R.K.r2_partition(ctx,ref)
OWN=R.K.build_corrected_ownership(ctx,ref,PART["partition"],probe)["corrected"]
from collections import Counter
FOWN=[]
for p in POLY:
    c=Counter(OWN[v] for v in p); m=c.most_common(); top=[k for k,v in m if v==m[0][1]]
    FOWN.append(top[0] if len(top)==1 else sorted(top)[0])
CM=dict((c["case_id"],c) for c in json.load(open(R.K.PROVENANCE["stage6b_case_matrix"],encoding="utf-8"))["cases"])
HARN={"R1(Stage6B, master S5B-R1B)": os.path.join(R.S6D,"stage6b","RIGHT_HAND_STAGE6B_OPPOSITION_HARNESS_R1.blend"),
      "R1B(Stage5B-R1C)":            R.K.S6B_R1B_HARNESS}
def census(path,cids):
    bpy.ops.wm.open_mainfile(filepath=path)
    ob=bpy.data.objects[R.MESH_OBJ]; rig=bpy.data.objects[R.RIG_OBJ]; MW=ob.matrix_world.copy()
    out={}
    for cid in cids:
        c=CM[cid]; q=c["cmc_quaternion_local"]; R.B.reset_pose(rig)
        pb=rig.pose.bones["THUMB_CMC_R"]; pb.rotation_mode='QUATERNION'
        pb.rotation_quaternion=Quaternion((q[0],q[1],q[2],q[3]))
        if c["mcp_deg"]:
            p=rig.pose.bones["THUMB_MCP_R"]; p.rotation_mode='QUATERNION'
            p.rotation_quaternion=Quaternion(Vector((1,0,0)),math.radians(-c["mcp_deg"]))
        if c["ip_deg"]:
            p=rig.pose.bones["THUMB_IP_R"]; p.rotation_mode='QUATERNION'
            p.rotation_quaternion=Quaternion(Vector((1,0,0)),math.radians(-c["ip_deg"]))
        R.B.update(); V=R.B.evaluate(ob,MW)[0]
        n_over2=0; n_over5=0; mx=0.0; mxinfo=None; faces=set()
        for fi,p in enumerate(POLY):
            for i in range(len(p)):
                u,v=p[i],p[(i+1)%len(p)]
                b=(V0[u]-V0[v]).length*1000; qq=(V[u]-V[v]).length*1000
                if b>3.0:
                    r=qq/b
                    if r>2.0: n_over2+=1; faces.add(fi)
                    if r>5.0: n_over5+=1
                    if r>mx: mx=r; mxinfo=(fi,u,v,round(b,2),round(qq,2))
        out[cid]={"edges_bind_gt3_and_over_2x":n_over2,"over_5x":n_over5,
                  "max_ratio":round(mx,2),"max_info":mxinfo,
                  "faces_affected":len(faces),
                  "faces_by_own":dict(Counter(FOWN[f] for f in faces))}
    return out
for lbl,path in HARN.items():
    print("=== %s ==="%lbl); print("   ",os.path.basename(path))
    r=census(path,["CMC_OPP_30","CMC_MCP_L3","FULL_OPP_L3"])
    for cid,v in r.items():
        print("   %-12s over2x=%4d over5x=%4d max_ratio=%6.2f faces=%3d own=%s  worst=%s"%(
            cid,v["edges_bind_gt3_and_over_2x"],v["over_5x"],v["max_ratio"],v["faces_affected"],
            v["faces_by_own"],v["max_info"]))
