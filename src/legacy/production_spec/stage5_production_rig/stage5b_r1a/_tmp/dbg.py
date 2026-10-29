import bpy, sys, os, json, math
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(r"<HANDS_ROOT>/production_spec/stage5_production_rig/stage5b_r1a/scripts")
import r1a_common as C
from mathutils import Vector
TOP = r"<HANDS_ROOT>/production_spec/stage5_production_rig"
ref = C.load_reference(TOP)
NV=ref["NV"]; V0=ref["V0"]
print("BBOX world:", [[round(min(v[k] for v in V0)*1000,2), round(max(v[k] for v in V0)*1000,2)] for k in range(3)])
print("MW0 row:", [[round(x,6) for x in r] for r in ref["MW0"]])
dstar=int(ref["cap"]["thumb"]["distal_most_vertex"])
GEO=ref["dij"](dstar)
print("reached verts:", len(GEO), "/", NV)
jf=ref["jf"]
for name in ("THUMB_IP_R","THUMB_MCP_R","THUMB_CMC_R","WRIST_R","THUMB_TIP_R","INDEX_MCP_R"):
    P=Vector(jf[name]["head"])
    i=min(range(NV), key=lambda k:(V0[k]-P).length)
    print(name, "nearest v%d"%i, "euclid=%.3f mm"%((V0[i]-P).length*1000), "geo=%.3f mm"%(GEO[i]*1000))
print("geo at 2189=%.3f  1076=%.3f  1075=%.3f"%(GEO[2189]*1000, GEO[1076]*1000, GEO[1075]*1000))
print("cap json keys:", list(ref["cap"].keys()))
print("cap thumb keys:", list(ref["cap"]["thumb"].keys()))
# components
import collections
adj=ref["eadj"]
seen=set(); comps=[]
for s in range(NV):
    if s in seen: continue
    st=[s]; seen.add(s); n=0
    while st:
        u=st.pop(); n+=1
        for v,_w in adj.get(u,()):
            if v not in seen: seen.add(v); st.append(v)
    comps.append(n)
print("mesh components:", sorted(comps, reverse=True)[:10], "count=",len(comps))
