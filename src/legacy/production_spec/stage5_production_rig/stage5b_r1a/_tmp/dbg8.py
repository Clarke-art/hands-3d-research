import bpy, sys, os, json
sys.path.append(r"<HANDS_ROOT>/production_spec/stage5_production_rig/stage5b_r1a/scripts")
import r1a_common as C
from mathutils import Vector
TOP = r"<HANDS_ROOT>/production_spec/stage5_production_rig"
ref = C.load_reference(TOP); NV=ref["NV"]; V0=ref["V0"]; TOPO=ref["TOPO0"]; MAT=ref["MAT0"]
def fn(fi):
    p=[V0[v] for v in TOPO[fi]]; n=Vector((0,0,0))
    for k in range(len(p)):
        n+=p[k].cross(p[(k+1)%len(p)])
    return n.normalized()
Ctr=sum(V0,Vector())/NV
# centroid-based outward is crude; better: use closest_point_on_mesh + normal for each vertex
ob=bpy.data.objects["Hand  - Realistic"]; MW=ref["MW0"]; MINV=MW.inverted(); M3=MW.to_3x3()
pos=0;neg=0
for i in range(0,NV,7):
    ok,loc,nor,idx=ob.closest_point_on_mesh(MINV@V0[i])
    if not ok: continue
    n=(M3@nor).normalized(); d=(V0[i]-(MW@loc))
    if d.length<1e-6: continue
    if n.dot(d.normalized())>0: neg+=1
    else: pos+=1
print("vertices whose surface normal points AWAY from the nearest surface (i.e. on an inner/back sheet): %d ; on the outer sheet: %d"%(neg,pos))
# duplicate-ish faces
key={}
dup=0; sheet=0
for fi,vs in enumerate(TOPO):
    k=tuple(sorted(vs))
    if k in key: dup+=1
    key[k]=fi
print("duplicate face keys:",dup)
# mesh volume
vol=0.0
for vs in TOPO:
    p=[V0[v] for v in vs]
    for k in range(1,len(p)-1):
        a,b,c=p[0],p[k],p[k+1]
        vol+=a.dot(b.cross(c))/6.0
print("signed volume (cm^3): %.2f"%(abs(vol)*1e6))
# count faces whose centroid is outside the 'convex-ish hull' - instead: check normal consistency between neighbours
inc={}
for fi,vs in enumerate(TOPO):
    for k in range(len(vs)):
        e=tuple(sorted((vs[k],vs[(k+1)%len(vs)])))
        inc.setdefault(e,[]).append(fi)
bad=0; tot=0
for e,fl in inc.items():
    if len(fl)!=2: continue
    n1=fn(fl[0]); n2=fn(fl[1])
    # for a consistently oriented manifold, adjacent face normals have positive dot for flat regions
    tot+=1
    if n1.dot(n2)<-0.5: bad+=1
print("adjacent face pairs with opposed normals: %d / %d"%(bad,tot))
print("dorsal_refs:", json.load(open(os.path.join(TOP,"stage5a_r2","_tmp","S5A_R2_CANDIDATES.json"),encoding="utf-8"))["dorsal_refs"])
