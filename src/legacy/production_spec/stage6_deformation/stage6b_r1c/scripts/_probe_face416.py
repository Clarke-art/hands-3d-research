import os, sys, json, math
import numpy as np
import bpy
from mathutils import Vector, Quaternion
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.append(HERE)
import r1c_pen_common as R
ctx=R.B.build_context(); ref=ctx["ref"]; V0=ref["V0"]; POLY=ctx["poly"]; NV=ref["NV"]
CM=dict((c["case_id"],c) for c in json.load(open(R.K.PROVENANCE["stage6b_case_matrix"],encoding="utf-8"))["cases"])
print("POLY[416]",POLY[416],"POLY[392]",POLY[392],"POLY[415]",POLY[415])
for f in (416,392,401,375,419,420,431):
    p=POLY[f]
    es=[(V0[p[i]]-V0[p[(i+1)%len(p)]]).length*1000 for i in range(len(p))]
    print("face %-4d verts %-22s BIND edges %s"%(f,p,[round(e,3) for e in es]))
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
# vertex order sanity: bind from base object
Vb=R.B.evaluate(ob,MW)[0]
d=[(Vb[i]-V0[i]).length*1000 for i in range(NV)]
print("bind evaluated vs ref V0 max diff mm = %.6f"%max(d))
# stretched edges with bind > 3mm
for cid in ("CMC_OPP_30","CMC_MCP_L3","FULL_OPP_L3"):
    V=pose(cid)
    bad=[]
    for fi,p in enumerate(POLY):
        for i in range(len(p)):
            u,v=p[i],p[(i+1)%len(p)]
            b=(V0[u]-V0[v]).length*1000; q=(V[u]-V[v]).length*1000
            if b>3.0 and q>2.0*b:
                bad.append((q/b,round(b,2),round(q,2),fi,u,v))
    bad.sort(reverse=True)
    print("\n%s : edges with bind>3mm AND posed>2x bind = %d"%(cid,len(bad)))
    for x in bad[:10]:
        print("    ratio %6.2f  bind %7.2f -> posed %8.2f mm  face %d (v%d-v%d)"%x)
    from collections import Counter
    cc=Counter(x[0] for x in bad)
    print("    faces involved:",sorted(set(x[0] for x in bad))[:20])
    # absolute
    ab=[]
    for fi,p in enumerate(POLY):
        for i in range(len(p)):
            u,v=p[i],p[(i+1)%len(p)]
            b=(V0[u]-V0[v]).length*1000; q=(V[u]-V[v]).length*1000
            if b>3.0 and q>15.0:
                ab.append((round(q,2),round(b,2),fi,u,v))
    ab.sort(reverse=True)
    print("    edges bind>3mm AND posed>15mm = %d ; top:"%len(ab),ab[:6])
