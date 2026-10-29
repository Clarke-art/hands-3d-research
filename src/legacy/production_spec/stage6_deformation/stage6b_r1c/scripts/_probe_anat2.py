import os, sys, json
import bpy
from mathutils import Vector
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.append(HERE)
import r1c_pen_common as R
ctx=R.B.build_context(); ref=ctx["ref"]; V0=ref["V0"]
cap=sorted(ref["cap"]["thumb_cap_vertex_ids"])
bpy.ops.wm.open_mainfile(filepath=R.K.S6B_R1B_HARNESS)
ob=bpy.data.objects[R.MESH_OBJ]; rig=bpy.data.objects[R.RIG_OBJ]
MWo=ob.matrix_world.copy(); MWr=rig.matrix_world.copy()
def bh(n): return MWr @ Vector(rig.data.bones[n].head_local)
J={k:bh(k) for k in ("THUMB_CMC_R","THUMB_MCP_R","THUMB_IP_R","THUMB_TIP_R","WRIST_R")}
def w(v): return MWo @ V0[v]
def d(v,k): return (w(v)-J[k]).length*1000
capc=sum((w(i) for i in cap),Vector())/len(cap)
print("thumb_cap centroid -> CMC %.2f  MCP %.2f  IP %.2f  TIP %.2f  WRIST %.2f" % tuple(
    (capc-J[k]).length*1000 for k in ("THUMB_CMC_R","THUMB_MCP_R","THUMB_IP_R","THUMB_TIP_R","WRIST_R")))
print("THUMB chain segment lengths mm: CMC->MCP %.2f  MCP->IP %.2f  IP->TIP %.2f"%(
    (J["THUMB_CMC_R"]-J["THUMB_MCP_R"]).length*1000,(J["THUMB_MCP_R"]-J["THUMB_IP_R"]).length*1000,
    (J["THUMB_IP_R"]-J["THUMB_TIP_R"]).length*1000))
print("\nv       CMC     MCP      IP     TIP   WRIST   nearest")
for v in (693,2156,2191,2584,1062,154,651,2058,649):
    ds={k:d(v,k) for k in ("THUMB_CMC_R","THUMB_MCP_R","THUMB_IP_R","THUMB_TIP_R","WRIST_R")}
    nj=min(ds,key=ds.get)
    print("v%-5d"%v+"".join("%8.2f"%ds[k] for k in ("THUMB_CMC_R","THUMB_MCP_R","THUMB_IP_R","THUMB_TIP_R","WRIST_R"))+"   %s"%nj)
