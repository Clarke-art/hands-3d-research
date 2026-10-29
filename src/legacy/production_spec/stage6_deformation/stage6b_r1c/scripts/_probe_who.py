import os, sys, json, math
import bpy
from mathutils import Vector, Quaternion
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.append(HERE)
import r1c_pen_common as R
ctx=R.B.build_context(); ref=ctx["ref"]; V0=ref["V0"]; POLY=ctx["poly"]; NV=ref["NV"]
CM=dict((c["case_id"],c) for c in json.load(open(R.K.PROVENANCE["stage6b_case_matrix"],encoding="utf-8"))["cases"])
bpy.ops.wm.open_mainfile(filepath=R.K.S6B_R1B_HARNESS)
ob=bpy.data.objects[R.MESH_OBJ]; rig=bpy.data.objects[R.RIG_OBJ]; MW=ob.matrix_world.copy()
G=[g.name for g in ob.vertex_groups]
def W(i):
    return dict((G[g.group],round(g.weight,4)) for g in ob.data.vertices[i].groups if g.weight>1e-4)
c=CM["FULL_OPP_L3"]; q=c["cmc_quaternion_local"]; R.B.reset_pose(rig)
pb=rig.pose.bones["THUMB_CMC_R"]; pb.rotation_mode='QUATERNION'
pb.rotation_quaternion=Quaternion((q[0],q[1],q[2],q[3]))
for bn,dg in (("THUMB_MCP_R",c["mcp_deg"]),("THUMB_IP_R",c["ip_deg"])):
    if dg:
        p=rig.pose.bones[bn]; p.rotation_mode='QUATERNION'
        p.rotation_quaternion=Quaternion(Vector((1,0,0)),math.radians(-dg))
R.B.update(); V=R.B.evaluate(ob,MW)[0]
# bone heads
def head(name):
    b=rig.data.bones[name]
    return ob.matrix_world.inverted() @ (rig.matrix_world @ b.head_local)
hc=R.B.evaluate(ob,MW)
for v in (693,2156,2172,3201,689,2160,697,2162,2191,2584,2176,704,2190,1062,2578,2071,651,154,1066,1067,2580,2058,2583,2066,649):
    disp=(V[v]-V0[v]).length*1000
    print("v%-5d bind=(%7.2f,%7.2f,%7.2f) posed=(%7.2f,%7.2f,%7.2f) disp=%7.2f mm distCMC=%6.2f  W=%s"%(
        v, V0[v].x*1000,V0[v].y*1000,V0[v].z*1000, V[v].x*1000,V[v].y*1000,V[v].z*1000, disp,
        (V0[v]-hc).length*1000 if False else (V0[v]-Vector((0,0,0))).length*1000, W(v)))
# thumb CMC joint position (bind, world)
hb=rig.data.bones["THUMB_CMC_R"]
cmc_world = MW @ rig.matrix_world.inverted() @ hb.head_local if False else None
print("\nTHUMB_CMC head (armature space) mm:", [round(x*1000,2) for x in hb.head_local])
for v in (693,2156,2172,3201,689,2160,2191,2584):
    d=(V0[v]-hb.head_local).length*1000
    print("   v%-5d dist to THUMB_CMC head = %.2f mm   disp=%.2f mm"%(v,d,(V[v]-V0[v]).length*1000))
