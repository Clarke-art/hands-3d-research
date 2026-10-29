import os, sys, json
from collections import Counter, deque
import bpy
from mathutils import Vector
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.append(HERE)
sys.path.append(os.path.join(HERE,"..","..","stage6b_r1b","scripts"))
import s6br1b_common as K
ctx=K.B.build_context(); ref=ctx["ref"]; V0=ref["V0"]; NV=ref["NV"]; EDGES=ref["EDGES"]; POLY=ref["TOPO0"]; MAT0=ref["MAT0"]
CAP=set(ref["cap"]["thumb_cap_vertex_ids"]); NAILT=set(ctx["nail"])
b=json.load(open(os.path.join(HERE,"..","R3_BOUNDARY_CONNECTEDNESS_AUDIT.json"),encoding="utf-8"))
ZIP=[e["edge"] for e in b["R3_boundary_edges"]]
ZSET=set(tuple(sorted(EDGES[k])) for k in ZIP)
print("zipper edges (R3 boundary): %d"%len(ZSET))
def components(skip):
    ADJ={}
    for a,bb in EDGES:
        if tuple(sorted((a,bb))) in skip: continue
        ADJ.setdefault(a,[]).append(bb); ADJ.setdefault(bb,[]).append(a)
    seen=set(); comps=[]
    for v in range(NV):
        if v in seen: continue
        c=[]; dq=deque([v]); seen.add(v)
        while dq:
            x=dq.popleft(); c.append(x)
            for y in ADJ.get(x,()):
                if y not in seen: seen.add(y); dq.append(y)
        comps.append(c)
    return sorted(comps,key=len,reverse=True)
base=components(set())
print("baseline components: %d (sizes %s)"%(len(base),[len(c) for c in base[:5]]))
cut=components(ZSET)
print("after cutting the R3 zipper: %d component(s), sizes %s"%(len(cut),[len(c) for c in cut[:6]]))
if len(cut)>1:
    for i,c in enumerate(cut[:4]):
        cs=set(c)
        print("  comp %d: n=%d  cap=%d nail_thumb=%d  cx=%.1f cy=%.1f cz=%.1f"%(
            i,len(c),len(cs&CAP),len(cs&NAILT),
            sum(V0[v].x for v in c)/len(c)*1000,sum(V0[v].y for v in c)/len(c)*1000,sum(V0[v].z for v in c)/len(c)*1000))
# also cut the R2 boundary set for comparison
b2=json.load(open(os.path.join(HERE,"..","R3_OWNERSHIP_LABELS.json"),encoding="utf-8"))
Z2=set(tuple(sorted(EDGES[k])) for k in b2["boundary_edges_R2"])
cut2=components(Z2)
print("after cutting the R2 boundary (%d edges): %d component(s), sizes %s"%(len(Z2),len(cut2),[len(c) for c in cut2[:6]]))
# which block is each disputed vertex in
if len(cut)>1:
    lab={}
    for i,c in enumerate(cut):
        for v in c: lab[v]=i
    for v in (693,689,699,698,692,704,2156,2160,2164,2172,2153,2155,2157,2159,2161,2163,2166,2169,3196,3203,160,1080):
        print("   v%-5d -> component %s"%(v,lab.get(v)))
