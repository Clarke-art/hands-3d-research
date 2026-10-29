import bpy, sys, os, json, math
sys.path.append(r"<HANDS_ROOT>/production_spec/stage5_production_rig/stage5b_r1a/scripts")
import r1a_common as C
from mathutils import Vector
TOP = r"<HANDS_ROOT>/production_spec/stage5_production_rig"
ref = C.load_reference(TOP)
NV=ref["NV"]; V0=ref["V0"]; me_mat=ref["MAT0"]; TOPO=ref["TOPO0"]
# material index histogram
from collections import Counter
print("material indices:", dict(Counter(me_mat)))
print("nail faces (mat1) count:", sum(1 for m in me_mat if m==1))
# per-material vertex sets
vm={}
for fi,vs in enumerate(TOPO):
    m=me_mat[fi]
    for v in vs: vm.setdefault(m,set()).add(v)
print("verts per material:", {k:len(v) for k,v in sorted(vm.items())})
print("nail vert ids:", sorted(vm.get(1,set())))
# coincident vertex pairs (grid hash 0.3 mm)
cell={}
for i,v in enumerate(V0):
    k=(round(v.x*3000), round(v.y*3000), round(v.z*3000))
    cell.setdefault(k,[]).append(i)
pairs=[]
for k,ids in cell.items():
    if len(ids)>1:
        for a in range(len(ids)):
            for b in range(a+1,len(ids)):
                if (V0[ids[a]]-V0[ids[b]]).length*1000 < 0.3:
                    pairs.append((ids[a],ids[b],round((V0[ids[a]]-V0[ids[b]]).length*1000,4)))
print("coincident(<0.3mm) pairs:", len(pairs))
print("sample pairs:", pairs[:25])
dstar=2189; GEO=ref["dij"](dstar)
far=[i for i in range(NV) if GEO[i]*1000>120 and ref["dchain"][i]["THUMB"]<15]
print("verts with geo>120mm AND dist_to_thumb_chain<15mm:", len(far), sorted(far)[:40])
inv=sorted([i for i in range(NV) if GEO[i]*1000>120], key=lambda i:-GEO[i])
print("max geo:", [(i, round(GEO[i]*1000,3)) for i in inv[:10]])
# check mate of v284 and 1076
for target in (284,1076,2189,1383,2740,3411,2746,2764,2439):
    near=[(i,round((V0[i]-V0[target]).length*1000,4)) for i in range(NV) if i!=target and (V0[i]-V0[target]).length*1000<2.0]
    print("v%d mat=%s geo=%.3f mm  neighbours<2mm:"%(target, "NAIL" if target in vm.get(1,set()) else "-", GEO[target]*1000), sorted(near,key=lambda t:t[1])[:8])
# which material faces touch v284/1076
for target in (284,1076,1383,2740):
    fs=[fi for fi,vs in enumerate(TOPO) if target in vs]
    print("v%d incident faces:"%target, [(fi, me_mat[fi]) for fi in fs])
