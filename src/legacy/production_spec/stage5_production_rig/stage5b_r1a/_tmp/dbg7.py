import bpy, sys, os
sys.path.append(r"<HANDS_ROOT>/production_spec/stage5_production_rig/stage5b_r1a/scripts")
import r1a_common as C
from mathutils import Vector
TOP = r"<HANDS_ROOT>/production_spec/stage5_production_rig"
ref = C.load_reference(TOP); NV=ref["NV"]; V0=ref["V0"]; TOPO=ref["TOPO0"]; MAT=ref["MAT0"]
GEO=ref["dij"](2189)
near=set(i for i in range(NV) if GEO[i]*1000<=100)
nearT=set(i for i in range(NV) if GEO[i]*1000<=100 and ref["dchain"][i]["THUMB"]<20)
print("near<=100mm: %d ; of those within 20mm of thumb chain: %d"%(len(near),len(nearT)))
# boundary edges between nearT and its complement
be=[]
for a,b in ref["EDGES"]:
    if (a in nearT) != (b in nearT):
        be.append((a,b,round(GEO[a]*1000,1),round(GEO[b]*1000,1),round(ref["dchain"][a]["THUMB"],2),round(ref["dchain"][b]["THUMB"],2)))
print("boundary edges nearT|rest:", len(be))
for e in be[:40]: print("   ",e)
print("--- thumb nail verts neighbours ---")
for i in sorted(ref["NAIL_BY_DIGIT"]["THUMB"]):
    nb=[b if a==i else a for a,b in ref["EDGES"] if a==i or b==i]
    print("nail v%-5d geo=%7.2f nbrs=%s"%(i,GEO[i]*1000,[(v,round(GEO[v]*1000,1)) for v in nb]))
