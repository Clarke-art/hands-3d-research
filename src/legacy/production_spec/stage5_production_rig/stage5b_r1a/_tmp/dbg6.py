import bpy, sys, os
sys.path.append(r"<HANDS_ROOT>/production_spec/stage5_production_rig/stage5b_r1a/scripts")
import r1a_common as C
from mathutils import Vector
TOP = r"<HANDS_ROOT>/production_spec/stage5_production_rig"
ref = C.load_reference(TOP); NV=ref["NV"]; V0=ref["V0"]; TOPO=ref["TOPO0"]; MAT=ref["MAT0"]
from collections import Counter
deg=Counter()
for a,b in ref["EDGES"]:
    deg[a]+=1; deg[b]+=1
print("degree histogram:", dict(sorted(Counter(deg[i] for i in range(NV)).items())))
GEO=ref["dij"](2189)
for i in (284,1076,2189,1383,2740,2746,1752,1341,1074,2569,2192,158):
    nb=[v for a,b in ref["EDGES"] if a==i or b==i for v in ([b] if a==i else [a])]
    print("v%-5d deg=%d geo=%8.2f dThumb=%5.2f nbrs=%s"%(i,deg[i],GEO[i]*1000,ref["dchain"][i]["THUMB"],
        [(v,round((V0[i]-V0[v]).length*1000,2),round(GEO[v]*1000,1)) for v in nb]))
# is there any *non-manifold* edge / boundary edge?
fe=Counter()
for vs in TOPO:
    for k in range(len(vs)):
        e=tuple(sorted((vs[k],vs[(k+1)%len(vs)]))); fe[e]+=1
print("edge face-use histogram:", dict(Counter(fe.values())))
