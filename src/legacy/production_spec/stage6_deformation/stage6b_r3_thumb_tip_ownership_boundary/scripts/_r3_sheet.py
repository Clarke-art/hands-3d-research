import os, sys, json
from collections import Counter, deque
import bpy
from mathutils import Vector
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.append(HERE)
sys.path.append(os.path.join(HERE,"..","..","stage6b_r1b","scripts"))
import s6br1b_common as K
ctx=K.B.build_context(); ref=ctx["ref"]; V0=ref["V0"]; NV=ref["NV"]; EDGES=ref["EDGES"]; POLY=ref["TOPO0"]; MAT0=ref["MAT0"]
PROD=os.path.abspath(os.path.join(HERE,"..","..",".."))
R2A=os.path.join(PROD,"stage5_production_rig","stage5a_r2a","RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend")
bpy.ops.wm.open_mainfile(filepath=R2A)
ob=bpy.data.objects[K.MESH_OBJ]; rig=bpy.data.objects[K.RIG_OBJ]; MWo=ob.matrix_world.copy()
def tl(n): return MWo @ Vector(rig.data.bones[n].tail_local)
def hd(n): return MWo @ Vector(rig.data.bones[n].head_local)
TIPV={}
for D in ("THUMB","INDEX","MIDDLE","RING","LITTLE"):
    p=tl("THUMB_IP_R" if D=="THUMB" else "%s_DIP_R"%D)
    TIPV[D]=min(range(NV),key=lambda i:(V0[i]-p).length)
    print("live %s tip landmark vertex v%-5d  dist %.3f mm  pos(%.1f,%.1f,%.1f)"%(
        D,TIPV[D],(V0[TIPV[D]]-p).length*1000,V0[TIPV[D]].x*1000,V0[TIPV[D]].y*1000,V0[TIPV[D]].z*1000))
Z=json.load(open(os.path.join(HERE,"..","R3_BOUNDARY_CONNECTEDNESS_AUDIT.json"),encoding="utf-8"))
ZSET=set(tuple(sorted(EDGES[e["edge"]])) for e in Z["R3_boundary_edges"])
ADJ={}
for a,b in EDGES:
    if tuple(sorted((a,b))) in ZSET: continue
    ADJ.setdefault(a,[]).append(b); ADJ.setdefault(b,[]).append(a)
seen=set(); comps=[]
for v in range(NV):
    if v in seen: continue
    c=[]; dq=deque([v]); seen.add(v)
    while dq:
        x=dq.popleft(); c.append(x)
        for y in ADJ.get(x,()):
            if y not in seen: seen.add(y); dq.append(y)
    comps.append(c)
comps.sort(key=len,reverse=True)
lab={}
for i,c in enumerate(comps):
    for v in c: lab[v]=i
print("\ncomponents:",[len(c) for c in comps])
for D,v in TIPV.items():
    print("   %-7s tip vertex v%-5d -> component %s"%(D,v,lab.get(v)))
CAP=set(ref["cap"]["thumb_cap_vertex_ids"]); NAILT=set(ctx["nail"]); WEB=set(ctx["first_web"])
NAILF=[fi for fi in range(len(POLY)) if MAT0[fi]==1]
byn={}
for fi in NAILF:
    c=sum((V0[v] for v in POLY[fi]),Vector())/len(POLY[fi])
    d=min(("THUMB","INDEX","MIDDLE","RING","LITTLE"),key=lambda D:(V0[TIPV[D]]-c).length)
    byn.setdefault(d,set()).update(POLY[fi])
print("\nnail faces grouped by NEAREST TIP LANDMARK:")
for D,s in sorted(byn.items()):
    print("   %-7s %d vertices ; in comp0=%d comp1=%d"%(D,len(s),
        len(s & set(comps[0])), len(s & set(comps[1])) if len(comps)>1 else 0))
print("\nCAP in comp0=%d comp1=%d ; thumb nail in comp0=%d comp1=%d ; web in comp0=%d comp1=%d"%(
    len(CAP&set(comps[0])),len(CAP&set(comps[1])),len(NAILT&set(comps[0])),len(NAILT&set(comps[1])),
    len(WEB&set(comps[0])),len(WEB&set(comps[1]))))
c1=comps[1]
print("\ncomponent1 (n=%d) bbox mm: x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f"%(
    len(c1),min(V0[v].x for v in c1)*1000,max(V0[v].x for v in c1)*1000,
    min(V0[v].y for v in c1)*1000,max(V0[v].y for v in c1)*1000,
    min(V0[v].z for v in c1)*1000,max(V0[v].z for v in c1)*1000))
print("component1 distance to live index tip v%d: min %.2f max %.2f mm"%(
    TIPV["INDEX"],min((V0[v]-V0[TIPV["INDEX"]]).length for v in c1)*1000,
    max((V0[v]-V0[TIPV["INDEX"]]).length for v in c1)*1000))
print("component1 distance to live thumb tip v%d: min %.2f max %.2f mm"%(
    TIPV["THUMB"],min((V0[v]-V0[TIPV["THUMB"]]).length for v in c1)*1000,
    max((V0[v]-V0[TIPV["THUMB"]]).length for v in c1)*1000))
