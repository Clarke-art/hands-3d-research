import bpy, sys, os, math, heapq
sys.path.append(r"<HANDS_ROOT>/production_spec/stage5_production_rig/stage5b_r1a/scripts")
import r1a_common as C
from mathutils import Vector
TOP = r"<HANDS_ROOT>/production_spec/stage5_production_rig"
ref = C.load_reference(TOP); NV=ref["NV"]; V0=ref["V0"]; TOPO=ref["TOPO0"]; MAT=ref["MAT0"]
eadj=ref["eadj"]
def dij_path(src):
    d={src:0.0}; prev={src:None}; pq=[(0.0,src)]
    while pq:
        du,u=heapq.heappop(pq)
        if du>d.get(u,1e18)+1e-15: continue
        for v,w in eadj.get(u,()):
            if du+w<d.get(v,1e18)-1e-16:
                d[v]=du+w; prev[v]=u; heapq.heappush(pq,(du+w,v))
    return d,prev
d,prev=dij_path(2189)
for tgt in (1383,2740,284,2746):
    path=[]; cur=tgt
    while cur is not None: path.append(cur); cur=prev[cur]
    path=path[::-1]
    print("=== path 2189 -> v%d   len=%d verts  geo=%.2f mm"%(tgt,len(path),d[tgt]*1000))
    for k in range(0,len(path),max(1,len(path)//22)):
        i=path[k]; p=V0[i]*1000
        fs=[fi for fi,vs in enumerate(TOPO) if i in vs]
        mats=sorted(set(MAT[fi] for fi in fs))
        print("   step%3d v%-5d (%7.1f,%6.1f,%6.1f) dThumb=%5.2f mats=%s"%(k,i,p.x,p.y,p.z,ref["dchain"][i]["THUMB"],mats))
    i=path[-1]; p=V0[i]*1000
    print("   final v%-5d (%7.1f,%6.1f,%6.1f) dThumb=%5.2f"%(i,p.x,p.y,p.z,ref["dchain"][i]["THUMB"]))
