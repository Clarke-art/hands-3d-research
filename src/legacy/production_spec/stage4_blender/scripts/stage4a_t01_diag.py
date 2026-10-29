# diagnostic: dump every maximal edge loop near each MCP with all metrics + rejection reason
import bpy, bmesh, sys, os, json, math, heapq
from mathutils import Vector, Matrix

OUT = sys.argv[sys.argv.index("--") + 1]
TARGET = "Hand  - Realistic"
M_NORM = Matrix(((1.0, 0.0, 0.0), (0.0, -1.0, 0.0), (0.0, 0.0, -1.0)))
TIP_SEEDS = {
    "little": Vector((1.3515, 0.0319, 0.1879)), "ring": Vector((1.3933, 0.0320, 0.1599)),
    "middle": Vector((1.4231, 0.0251, 0.1490)), "index": Vector((1.4586, 0.0239, 0.1643)),
    "thumb": Vector((1.4977, 0.0358, 0.2421)),
}
THUMB_ROOT_SEED = Vector((1.4489, 0.0115, 0.3134))
FOREARM_SEED = Vector((1.4048, 0.0113, 0.4316)); WRIST_SEED = Vector((1.4048, 0.0113, 0.3430))
FINGER_ORDER = ["little", "ring", "middle", "index"]
ob = bpy.data.objects[TARGET]; MW = ob.matrix_world; LOC0 = MW.translation
canon = lambda p: (M_NORM @ p) + (LOC0 - (M_NORM @ LOC0))
bm = bmesh.new(); bm.from_mesh(ob.data)
bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()
W = [(MW @ v.co).copy() for v in bm.verts]; NV = len(W)
ADJ = [[] for _ in range(NV)]
for e in bm.edges:
    a, b = e.verts[0].index, e.verts[1].index; L = (W[a] - W[b]).length
    ADJ[a].append((b, L)); ADJ[b].append((a, L))
nearest = lambda p: min(range(NV), key=lambda i: (W[i] - p).length_squared)
def dij(src):
    d = [float("inf")] * NV; d[src] = 0.0; pq = [(0.0, src)]
    while pq:
        du, u = heapq.heappop(pq)
        if du > d[u] + 1e-15: continue
        for v, w in ADJ[u]:
            if du + w < d[v] - 1e-16: d[v] = du + w; heapq.heappush(pq, (d[v], v))
    return d
TIPV = {n: nearest(canon(s)) for n, s in TIP_SEEDS.items()}
G = {n: dij(TIPV[n]) for n in TIPV}
WRIST_V = nearest(canon(WRIST_SEED)); FOREARM = W[nearest(canon(FOREARM_SEED))]
lab = [None] * NV; dd = [float("inf")] * NV
srcs = [("wrist", WRIST_V)] + [(n, TIPV[n]) for n in TIPV]
for nm, s in srcs: dd[s] = 0.0; lab[s] = nm
pq = [(0.0, s) for _n, s in srcs]; heapq.heapify(pq)
while pq:
    du, u = heapq.heappop(pq)
    if du > dd[u] + 1e-15: continue
    for v, w in ADJ[u]:
        if du + w < dd[v] - 1e-16: dd[v] = du + w; lab[v] = lab[u]; heapq.heappush(pq, (dd[v], v))
DIGIT_V = {n: [] for n in TIPV}
for i, l in enumerate(lab):
    if l in DIGIT_V: DIGIT_V[l].append(i)
CLEFTS = [("index","middle"),("middle","ring"),("ring","little"),("index","thumb")]
FC = {"index":["index-middle"],"middle":["index-middle","middle-ring"],
      "ring":["middle-ring","ring-little"],"little":["ring-little"]}
NOTCH = {}
for a, b in CLEFTS:
    ridge = {u for u in range(NV) if lab[u] in (a,b) and any(lab[v] in (a,b) and lab[v]!=lab[u] for v,_w in ADJ[u])}
    if ridge: NOTCH["%s-%s"%(a,b)] = max(ridge, key=lambda u: (W[u]-FOREARM).dot((W[TIPV["middle"]]-FOREARM).normalized()))
FL = {}
for nm in FINGER_ORDER:
    vals = [G[nm][NOTCH[c]] for c in FC[nm] if c in NOTCH]
    if vals: FL[nm] = sum(vals)/len(vals)
FL["thumb"] = G["thumb"][nearest(canon(THUMB_ROOT_SEED))]
def joint_centers(nm):
    L = FL[nm]; h = max(0.007, 0.10*L)
    return {"%s_MCP"%nm.upper(): (L, h), "%s_PIP"%nm.upper(): (0.54*L, h),
            "%s_DIP"%nm.upper(): (0.23*L, max(0.006, 0.09*L))} if nm != "thumb" else {
            "THUMB_CMC":(L,max(0.007,0.10*L)),"THUMB_MCP":(0.56*L,max(0.007,0.10*L)),"THUMB_IP":(0.25*L,max(0.006,0.09*L))}
def finger_axis(nm):
    tip = W[TIPV[nm]]; L = FL[nm]; ids = DIGIT_V.get(nm, [])
    band = [i for i in ids if 0.25*L <= G[nm][i] <= 0.55*L]
    c = (sum((W[i] for i in band), Vector())/len(band)) if band else tip
    axis = (tip-c).normalized()
    ref = W[nearest(canon(THUMB_ROOT_SEED))] if nm=="thumb" else W[NOTCH[FC[nm][0]]]
    return axis, tip + axis*((ref-tip).dot(axis))
incident = {v.index: [] for v in bm.verts}
for e in bm.edges:
    incident[e.verts[0].index].append(e.index); incident[e.verts[1].index].append(e.index)
edge_v = {e.index: (e.verts[0].index, e.verts[1].index) for e in bm.edges}
edge_key = {}
for e in bm.edges:
    edge_key[(e.verts[0].index, e.verts[1].index)] = e.index
    edge_key[(e.verts[1].index, e.verts[0].index)] = e.index
link = {}
for f in bm.faces:
    vs = [v.index for v in f.verts]; n = len(vs)
    for i in range(n):
        v = vs[i]
        ep = edge_key[(vs[(i-1)%n], v)]; en = edge_key[(v, vs[(i+1)%n])]
        link.setdefault((v, ep), set()).add(en); link.setdefault((v, en), set()).add(ep)
VCYC = {}
def vcycle(v):
    if v in VCYC: return VCYC[v]
    k = len(incident[v]); order = None
    if k >= 3:
        e0 = incident[v][0]
        for second in sorted(link.get((v, e0), ())):
            seq = [e0, second]; prev, cur = e0, second; ok = True
            while len(seq) < k:
                cands = [e for e in link.get((v, cur), ()) if e != prev]
                if len(cands) != 1: ok = False; break
                nx = cands[0]
                if nx == e0: break
                if nx in seq: ok = False; break
                seq.append(nx); prev, cur = cur, nx
            if ok and len(seq) == k and e0 in link.get((v, seq[-1]), ()):
                order = seq; break
    VCYC[v] = order; return order
def opp_at(v, e):
    c = vcycle(v)
    if not c or len(c) != 4 or e not in c: return None
    return c[(c.index(e)+2) % 4]
def walk(se, sv):
    loop=[se]; cur_e, cur_v = se, sv
    while True:
        a,b = edge_v[cur_e]; nx = b if cur_v==a else a
        op = opp_at(nx, cur_e)
        if op is None: return loop, ("pole" if len(incident[nx])!=4 else "nocycle"), nx, len(incident[nx])
        if op == se: return loop,"closed",nx,len(incident[nx])
        if op in loop: return loop,"self",nx,len(incident[nx])
        loop.append(op); cur_v,cur_e=nx,op
        if len(loop)>400: return loop,"self",nx,len(incident[nx])
LOOPS=[]; covered=set()
for e in bm.edges:
    if e.index in covered: continue
    a,b = edge_v[e.index]
    f,sf,vf,kf = walk(e.index,a); bk,sb,vb,kb = walk(e.index,b)
    full = (list(reversed(bk[1:]))+f) if len(bk)>1 else f
    for ei in full: covered.add(ei)
    if len(full)<3: continue
    LOOPS.append((full, sf=="closed" and sb=="closed", sf, sb))
print("maximal loops:", len(LOOPS))
def lverts(lg):
    out=[]
    for ei in lg:
        a,b=edge_v[ei]
        if not out: out=[a,b]; continue
        out.append(b if out[-1]==a else a)
    return out
res={}
for nm in ("index","middle","ring","little"):
    axis, anchor = finger_axis(nm); c,h = joint_centers(nm)["%s_MCP"%nm.upper()]
    rows=[]
    for lg, closed, sf, sb in LOOPS:
        vs = lverts(lg)
        geod=[G[nm][v] for v in vs]
        g=sum(geod)/len(geod)
        if abs(g-c) > h+0.012: continue
        perp=[((W[v]-anchor)-axis*((W[v]-anchor).dot(axis))).length for v in vs]
        df=sum(1 for v in vs if lab[v]==nm)/len(vs)
        al=[]
        for ei in lg:
            a,b=edge_v[ei]; d=W[b]-W[a]
            if d.length>1e-9: al.append(abs((d/d.length).dot(axis)))
        align=sum(al)/max(1,len(al))
        ref = Vector((0,0,1)) if abs(axis.z)<0.9 else Vector((1,0,0))
        u1=(ref-axis*ref.dot(axis)).normalized(); u2=axis.cross(u1)
        ang=sorted(math.atan2((W[v]-anchor).dot(u2),(W[v]-anchor).dot(u1)) for v in vs)
        gaps=[ang[i+1]-ang[i] for i in range(len(ang)-1)]+[ang[0]+2*math.pi-ang[-1]]
        cov=1.0-max(gaps)/(2*math.pi)
        rej=[]
        if len(lg)<8: rej.append("n_edges<8")
        if align>=0.45: rej.append("not_circumferential")
        if df<0.55: rej.append("digit_frac<0.55")
        if max(perp)>0.022: rej.append("perp>22mm")
        if cov<0.60: rej.append("coverage<0.60")
        rows.append({"n":len(lg),"closed":closed,"sf":sf,"sb":sb,"geod_mm":round(g*1000,2),
                     "align":round(align,3),"digit_frac":round(df,3),"perp_mm":round(max(perp)*1000,1),
                     "cov":round(cov,3),"reject":rej})
    rows.sort(key=lambda r:r["geod_mm"])
    res[nm]={"band_mm":[round((c-h)*1000,2),round((c+h)*1000,2)],"candidates":rows}
    print("="*100)
    print("%s MCP band %.2f..%.2f mm  candidates=%d"%(nm,(c-h)*1000,(c+h)*1000,len(rows)))
    for r in rows:
        print("  n=%3d closed=%-5s geod=%7.2f align=%.3f dfrac=%.3f perp=%5.1f cov=%.3f %s %s/%s"%(
            r["n"],r["closed"],r["geod_mm"],r["align"],r["digit_frac"],r["perp_mm"],r["cov"],
            "REJECT:"+",".join(r["reject"]) if r["reject"] else "ACCEPT", r["sf"], r["sb"]))
json.dump(res, open(OUT,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("WROTE", OUT)
