import bpy, sys, os, math
sys.path.append(r"<HANDS_ROOT>/production_spec/stage5_production_rig/stage5b_r1a/scripts")
import r1a_common as C
from mathutils import Vector
TOP = r"<HANDS_ROOT>/production_spec/stage5_production_rig"
ref = C.load_reference(TOP); NV=ref["NV"]; V0=ref["V0"]; TOPO=ref["TOPO0"]; MAT=ref["MAT0"]
GEO=ref["dij"](2189)
near=[i for i in range(NV) if GEO[i]*1000<=40]
far =[i for i in range(NV) if GEO[i]*1000>120]
print("near(<=40mm) count=%d   far(>120mm) count=%d"%(len(near),len(far)))
print("near bbox mm:", [[round(min(V0[i][k] for i in near)*1000,1), round(max(V0[i][k] for i in near)*1000,1)] for k in range(3)])
print("far  bbox mm:", [[round(min(V0[i][k] for i in far)*1000,1), round(max(V0[i][k] for i in far)*1000,1)] for k in range(3)])
# nearest near-vertex distance for a sample of far vertices
import heapq
dists=[]
for i in far[:400]:
    d=min((V0[i]-V0[j]).length*1000 for j in near)
    dists.append(d)
dists.sort()
print("far->near nearest distance mm: min=%.3f p25=%.3f med=%.3f p75=%.3f max=%.3f"%(
  dists[0],dists[len(dists)//4],dists[len(dists)//2],dists[3*len(dists)//4],dists[-1]))
# face normal orientation check: are 'far' faces flipped?
import statistics
def face_normal(fi):
    vs=TOPO[fi]; p=[V0[v] for v in vs]
    n=Vector((0,0,0))
    for k in range(len(p)):
        a=p[k]; b=p[(k+1)%len(p)]
        n += a.cross(b)
    return n.normalized()
# outward test: is normal pointing away from the hand axis? approximate: compare to vector from mesh centroid
Ctr=sum(V0,Vector())/NV
for name,grp in (("near",near),("far",far)):
    fset=set()
    for fi,vs in enumerate(TOPO):
        if vs[0] in set(grp[:120]): fset.add(fi)
    dots=[face_normal(fi).dot((sum(V0[v] for v in TOPO[fi])/len(TOPO[fi])-Ctr).normalized()) for fi in list(fset)[:150]]
    print(name,"face normal . outward: mean=%.3f (pos=outward)"%(sum(dots)/len(dots)))
# does the thumb tip region 'far' set sit *inside* the near set? distance from a far vertex to the nearest near vertex along -normal
i=284
n=face_normal([fi for fi,vs in enumerate(TOPO) if i in vs and MAT[fi]==0][0])
print("v284 normal:", [round(x,4) for x in n], " pos:", [round(x*1000,2) for x in V0[284]])
