import os, sys, json, math
import numpy as np
import bpy
from mathutils import Vector, Quaternion
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.append(HERE)
import r1c_pen_common as R
ctx=R.B.build_context(); ref=ctx["ref"]; V0=ref["V0"]; POLY=ctx["poly"]; NV=ref["NV"]
TRIS=R.tris_of(POLY,V0); FACE_TRIS={}
for fi,t in TRIS: FACE_TRIS.setdefault(fi,[]).append(t)
CM=dict((c["case_id"],c) for c in json.load(open(R.K.PROVENANCE["stage6b_case_matrix"],encoding="utf-8"))["cases"])
bpy.ops.wm.open_mainfile(filepath=R.K.S6B_R1B_HARNESS)
ob=bpy.data.objects[R.MESH_OBJ]; rig=bpy.data.objects[R.RIG_OBJ]; MW=ob.matrix_world.copy()
def pose(cid):
    c=CM[cid]; q=c["cmc_quaternion_local"]; R.B.reset_pose(rig)
    pb=rig.pose.bones["THUMB_CMC_R"]; pb.rotation_mode='QUATERNION'
    pb.rotation_quaternion=Quaternion((q[0],q[1],q[2],q[3]))
    if c["mcp_deg"]:
        p=rig.pose.bones["THUMB_MCP_R"]; p.rotation_mode='QUATERNION'
        p.rotation_quaternion=Quaternion(Vector((1,0,0)),math.radians(-c["mcp_deg"]))
    if c["ip_deg"]:
        p=rig.pose.bones["THUMB_IP_R"]; p.rotation_mode='QUATERNION'
        p.rotation_quaternion=Quaternion(Vector((1,0,0)),math.radians(-c["ip_deg"]))
    R.B.update(); return R.B.evaluate(ob,MW)[0]
# bind quad edge stats
BE=[]
for p in POLY:
    for i in range(len(p)):
        BE.append((V0[p[i]]-V0[p[(i+1)%len(p)]]).length*1000)
BE=np.array(BE)
print("BIND quad edge mm: p50 %.4f p99 %.4f max %.4f ; n=%d"%(np.percentile(BE,50),np.percentile(BE,99),BE.max(),len(BE)))
for cid in ("CMC_OPP_30","CMC_MCP_L3","FULL_OPP_L3"):
    V=pose(cid)
    PE=[]
    worst=(0,None)
    for fi,t in TRIS:
        a,b,c=V[t[0]],V[t[1]],V[t[2]]
        m=((a-b).length+(b-c).length+(c-a).length)/3.0*1000
        mx=max((a-b).length,(b-c).length,(c-a).length)*1000
        PE.append(m)
        if mx>worst[0]: worst=(mx,(fi,t))
    PE=np.array(PE)
    print("%-12s POSED tri mean edge: p50 %.4f p99 %.4f max %.4f | worst tri face %d verts %s maxedge %.4f mm"%
          (cid,np.percentile(PE,50),np.percentile(PE,99),PE.max(),worst[1][0],worst[1][1],worst[0]))
    # ratio posed/bind per quad
    ratios=[]
    for fi,p in enumerate(POLY):
        for i in range(len(p)):
            u,v=p[i],p[(i+1)%len(p)]
            b=(V0[u]-V0[v]).length; q=(V[u]-V[v]).length
            if b>1e-9: ratios.append(q/b)
    ratios=np.array(ratios)
    print("            posed/bind edge ratio: p99 %.3f max %.3f  (over 1.5x: %d, over 2x: %d)"%
          (np.percentile(ratios,99),ratios.max(),int((ratios>1.5).sum()),int((ratios>2).sum())))
    # the deepest poke pair from the adjudication JSON
    d=json.load(open("../STAGE6B_R1C_PENETRATION_ADJUDICATION.json",encoding="utf-8"))["cases"][cid]
    for lbl,pair in (("MAX",d["max_pair"]),("FOCUS",d["adjudication_focus"])):
        fa,fb=(pair["face_a"],pair["face_b"]) if lbl=="MAX" else (pair["face_a"],pair["face_b"])
        for ta in FACE_TRIS[fa]:
            for tb in FACE_TRIS[fb]:
                A=(V[ta[0]],V[ta[1]],V[ta[2]]); B3=(V[tb[0]],V[tb[1]],V[tb[2]])
                pA=R.poke_depth(A,B3)*1000; pB=R.poke_depth(B3,A)*1000
                ea=max((A[0]-A[1]).length,(A[1]-A[2]).length,(A[2]-A[0]).length)*1000
                eb=max((B3[0]-B3[1]).length,(B3[1]-B3[2]).length,(B3[2]-B3[0]).length)*1000
                if max(pA,pB)>0.05:
                    print("   %-5s faces %d/%d tri %s/%s : pokeA %.4f pokeB %.4f | maxedgeA %.4f maxedgeB %.4f"%
                          (lbl,fa,fb,ta,tb,pA,pB,ea,eb))
