import os, sys, json, math
import bpy
from mathutils import Vector
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.append(HERE)
import r1c_pen_common as R
ctx=R.B.build_context(); ref=ctx["ref"]; V0=ref["V0"]; POLY=ctx["poly"]
cap=sorted(ref["cap"]["thumb_cap_vertex_ids"])
print("thumb_cap_vertex_ids:",cap[:12],"... n=",len(cap))
bpy.ops.wm.open_mainfile(filepath=R.K.S6B_R1B_HARNESS)
ob=bpy.data.objects[R.MESH_OBJ]; rig=bpy.data.objects[R.RIG_OBJ]
JOINTS={}
for n in ("THUMB_CMC_R","THUMB_MCP_R","THUMB_IP_R","THUMB_TIP_R","INDEX_MCP_R","INDEX_PIP_R","INDEX_DIP_R"):
    if n in rig.data.bones:
        JOINTS[n]=Vector(rig.data.bones[n].head_local)
def d3(v,p): return (V0[v]-p).length*1000
IDS=[693,2156,2172,3201,689,2160,697,2162,2191,2584,2176,704,2190,1062,2578,2071,651,154,1066,1067,2580,2058,2583,2066,649]
hdr="v      "+"".join("%11s"%k.replace("_R","") for k in ("THUMB_CMC_R","THUMB_MCP_R","THUMB_IP_R","THUMB_TIP_R"))+"   nearestJoint"
print(hdr)
for v in IDS:
    ds={k:d3(v,p) for k,p in JOINTS.items() if k.startswith("THUMB")}
    nj=min(ds.items(),key=lambda kv:kv[1])
    print("v%-5d"%v+"".join("%11.2f"%ds[k] for k in ("THUMB_CMC_R","THUMB_MCP_R","THUMB_IP_R","THUMB_TIP_R"))+"   %s %.1f"%nj)
capc=sum((V0[i] for i in cap),Vector())/len(cap)
print("\ncap centroid:"+"".join(" %s %.1f"%(k,d3(0,0) if False else (capc-p).length*1000) for k,p in JOINTS.items() if k.startswith("THUMB")))
