import bpy, sys, os, math, json
sys.path.append(r"<HANDS_ROOT>/production_spec/stage5_production_rig/stage5b_r1a/scripts")
import r1a_common as C
from mathutils import Vector
TOP = r"<HANDS_ROOT>/production_spec/stage5_production_rig"
ref = C.load_reference(TOP); NV=ref["NV"]; V0=ref["V0"]; TOPO=ref["TOPO0"]; MAT=ref["MAT0"]
GEO=ref["dij"](2189)
nailT=set(ref["NAIL_BY_DIGIT"]["THUMB"])
CAP=set(ref["cap"]["thumb_cap_vertex_ids"])
print("thumb nail verts:", sorted(nailT))
print("cap patch verts :", sorted(CAP))
print("%-6s %-32s %8s %8s %8s %8s %8s %s"%("v","world(mm)","geo","dThumb","dIndex","dCapRep","arc","own/nail"))
def row(i):
    p=V0[i]*1000
    own=ref["OWN_V"][i]
    return "%-6d (%7.1f,%6.1f,%6.1f)  %8.2f %8.2f %8.2f %8.2f %8.2f %s%s"%(
      i,p.x,p.y,p.z, GEO[i]*1000, ref["dchain"][i]["THUMB"], ref["dchain"][i]["INDEX"],
      (V0[i]-Vector(ref["cap"]["cap_representative_world"])).length*1000,
      C.arc_of(C.chp(ref["jf"],"THUMB"),V0[i])[0],
      own, "/NAIL" if i in nailT else "")
for i in sorted(nailT):
    print(row(i))
print("--- cap patch / suspicious ---")
for i in sorted(CAP)+[284,1076,1752,1341,2746,2764,3411,2439]:
    print(row(i))
print("--- thumb nail FACE material/ownership ---")
fo=ref["FO"]
for fi in sorted(f for f in range(len(TOPO)) if MAT[f]==1):
    vs=TOPO[fi]
    if any(v in nailT for v in vs):
        print(" face %d mat=%d owner=%s verts=%s"%(fi,MAT[fi],fo[fi],list(vs)))
