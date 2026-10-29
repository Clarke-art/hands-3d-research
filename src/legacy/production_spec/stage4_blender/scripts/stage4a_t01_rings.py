import bpy, bmesh, sys, math, heapq
from mathutils import Vector, Matrix
TARGET="Hand  - Realistic"
M=Matrix(((1,0,0),(0,-1,0),(0,0,-1)))
TS={"little":Vector((1.3515,0.0319,0.1879)),"ring":Vector((1.3933,0.0320,0.1599)),
    "middle":Vector((1.4231,0.0251,0.1490)),"index":Vector((1.4586,0.0239,0.1643)),
    "thumb":Vector((1.4977,0.0358,0.2421))}
TR=Vector((1.4489,0.0115,0.3134)); FO=Vector((1.4048,0.0113,0.4316)); WS=Vector((1.4048,0.0113,0.3430))
ob=bpy.data.objects[TARGET]; MW=ob.matrix_world; L0=MW.translation
canon=lambda p:(M@p)+(L0-(M@L0))
bm=bmesh.new(); bm.from_mesh(ob.data)
bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()
W=[(<REDACTED_EMAIL>).copy() for v in bm.verts]; NV=len(W)
ADJ=[[] for _ in range(NV)]
for e in bm.edges:
    a,b=e.verts[0].index,e.verts[1].index; L=(W[a]-W[b]).length
    ADJ[a].append((b,L)); ADJ[b].append((a,L))
nr=lambda p: min(range(NV), key=lambda i:(W[i]-p).length_squared)
def dij(s):
    d=[float('inf')]*NV; d[s]=0.0; pq=[(0.0,s)]
    while pq:
        du,u=heapq.heappop(pq)
        if du>d[u]+1e-15: continue
        for v,w in ADJ[u]:
            if du+w<d[v]-1e-16: d[v]=du+w; heapq.heappush(pq,(d[v],v))
    return d
TV={n:nr(canon(s)) for n,s in TS.items()}
G={n:dij(TV[n]) for n in TV}
lab=[None]*NV; dd=[float('inf')]*NV
srcs=[("wrist",nr(canon(WS)))]+[(n,TV[n]) for n in TV]
for nm,s in srcs: dd[s]=0.0; lab[s]=nm
pq=[(0.0,s) for _n,s in srcs]; heapq.heapify(pq)
while pq:
    du,u=heapq.heappop(pq)
    if du>dd[u]+1e-15: continue
    for v,w in ADJ[u]:
        if du+w<dd[v]-1e-16: dd[v]=du+w; lab[v]=lab[u]; heapq.heappush(pq,(dd[v],v))
DV={n:[] for n in TV}
for i,l in enumerate(lab):
    if l in DV: DV[l].append(i)
FOV=W[nr(canon(FO))]
CL=[("index","middle"),("middle","ring"),("ring","little"),("index","thumb")]
FC={"index":["index-middle"],"middle":["index-middle","middle-ring"],"ring":["middle-ring","ring-little"],"little":["ring-little"]}
Ddist=(W[TV["middle"]]-FOV).normalized()
NT={}
for a,b in CL:
    rg={u for u in range(NV) if lab[u] in (a,b) and any(lab[v] in (a,b) and lab[v]!=lab[u] for v,_w in ADJ[u])}
    if rg: NT["%s-%s"%(a,b)]=max(rg,key=lambda u:(W[u]-FOV).dot(Ddist))
FL={}
for nm in ("little","ring","middle","index"):
    vals=[G[nm][NT[c]] for c in FC[nm] if c in NT]
    FL[nm]=sum(vals)/len(vals)
FL["thumb"]=G["thumb"][nr(canon(TR))]
print("--- FUNC_LEN vs euclidean tip->web ---")
for nm in ("index","middle","ring","little"):
    tip=W[TV[nm]]
    for c in FC[nm]:
        nw=W[NT[c]]
        print("  %-7s %-14s geod=%7.2f mm  euclid=%7.2f mm  ratio=%.2f"%(nm,c,G[nm][NT[c]]*1000,(tip-nw).length*1000,G[nm][NT[c]]/(tip-nw).length))
    print("  %-7s FUNC_LEN=%.2f mm"%(nm,FL[nm]*1000))
def fax(nm):
    tip=W[TV[nm]]; L=FL[nm]; ids=DV.get(nm,[])
    bd=[i for i in ids if 0.25*L<=G[nm][i]<=0.55*L]
    c=(sum((W[i] for i in bd),Vector())/len(bd)) if bd else tip
    ax=(tip-c).normalized(); ref=W[NT[FC[nm][0]]]
    return ax, tip+ax*((ref-tip).dot(ax))
inc={v.index:[] for v in bm.verts}
for e in bm.edges: inc[e.verts[0].index].append(e.index); inc[e.verts[1].index].append(e.index)
ev={e.index:(e.verts[0].index,e.verts[1].index) for e in bm.edges}
ek={}
for e in bm.edges:
    ek[(e.verts[0].index,e.verts[1].index)]=e.index; ek[(e.verts[1].index,e.verts[0].index)]=e.index
link={}
for f in bm.faces:
    vs=[v.index for v in f.verts]; n=len(vs)
    for i in range(n):
        v=vs[i]; ep=ek[(vs[(i-1)%n],v)]; en=ek[(v,vs[(i+1)%n])]
        link.setdefault((v,ep),set()).add(en); link.setdefault((v,en),set()).add(ep)
VC={}
def vc(v):
    if v in VC: return VC[v]
    k=len(inc[v]); o=None
    if k>=3:
        e0=inc[v][0]
        for s2 in sorted(link.get((v,e0),())):
            seq=[e0,s2]; pr,cu=e0,s2; ok=True
            while len(seq)<k:
                cd=[e for e in link.get((v,cu),()) if e!=pr]
                if len(cd)!=1: ok=False; break
                nx=cd[0]
                if nx==e0: break
                if nx in seq: ok=False; break
                seq.append(nx); pr,cu=cu,nx
            if ok and len(seq)==k and e0 in link.get((v,seq[-1]),()): o=seq; break
    VC[v]=o; return o
def opp(v,e):
    c=vc(v)
    return None if (not c or len(c)!=4 or e not in c) else c[(c.index(e)+2)%4]
def walk(se,sv):
    lp=[se]; ce,cv=se,sv
    while True:
        a,b=ev[ce]; nx=b if cv==a else a
        o=opp(nx,ce)
        if o is None: return lp,("pole" if len(inc[nx])!=4 else "nocycle")
        if o==se: return lp,"closed"
        if o in lp: return lp,"self"
        lp.append(o); cv,ce=nx,o
        if len(lp)>400: return lp,"self"
LO=[]; cov=set()
for e in bm.edges:
    if e.index in cov: continue
    a,b=ev[e.index]
    f,sf=walk(e.index,a); bk,sb=walk(e.index,b)
    full=(list(reversed(bk[1:]))+f) if len(bk)>1 else f
    for x in full: cov.add(x)
    if len(full)<3: continue
    LO.append((full, sf=="closed" and sb=="closed"))
def lv(lg):
    o=[]
    for ei in lg:
        a,b=ev[ei]
        if not o: o=[a,b]; continue
        o.append(b if o[-1]==a else a)
    return o
print("--- all circumferential loops per finger (no band filter) ---")
for nm in ("index","middle","ring","little"):
    ax,an=fax(nm); rows=[]
    for lg,closed in LO:
        vs=lv(lg)
        if len(lg)<8: continue
        df=sum(1 for v in vs if lab[v]==nm)/len(vs)
        if df<0.55: continue
        al=[]
        for ei in lg:
            a,b=ev[ei]; d=W[b]-W[a]
            if d.length>1e-9: al.append(abs((d/d.length).dot(ax)))
        A=sum(al)/len(al)
        if A>=0.45: continue
        pp=[((W[v]-an)-ax*((W[v]-an).dot(ax))).length for v in vs]
        gd=[G[nm][v] for v in vs]
        axv=[(W[v]-an).dot(ax) for v in vs]
        rows.append((sum(axv)/len(axv)*1000,sum(gd)/len(gd)*1000,len(lg),closed,max(pp)*1000,A))
    rows.sort()
    ax,an=fax(nm)
    print("  %s: %d circumferential loops | tip axial=%.1f mm, web axial=0, axislen=%.1f mm"%(nm,len(rows),(W[TV[nm]]-an).dot(ax)*1000,(W[TV[nm]]-an).dot(ax)*1000))
    for r in rows: print("     axial=%7.2f  geod=%7.2f n=%3d closed=%-5s perp=%5.1f align=%.3f"%r)
