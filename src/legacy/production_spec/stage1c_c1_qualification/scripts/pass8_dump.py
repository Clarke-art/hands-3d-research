# STAGE1C - Pass 8: dump every opposite-edge component intersecting each finger zone, with classification data
import bpy, bmesh, json, math
from mathutils import Vector
TARGET = "Hand  - Realistic"
ob = bpy.data.objects[TARGET]
mw = ob.matrix_world
bm = bmesh.new(); bm.from_mesh(ob.data)
bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()
W = [(mw @ v.co).copy() for v in bm.verts]
nE = len(bm.edges)
parent = list(range(nE))
def find(a):
    while parent[a] != a:
        parent[a] = parent[parent[a]]; a = parent[a]
    return a
def union(a,b):
    ra, rb = find(a), find(b)
    if ra != rb: parent[rb] = ra
for f in bm.faces:
    if len(f.edges) != 4: continue
    es = list(f.edges); vs=[set(v.index for v in e.verts) for e in es]
    for i in range(4):
        for j in range(4):
            if i!=j and not (vs[i]&vs[j]):
                union(es[i].index, es[j].index); break
comps = {}
for ei in range(nE):
    comps.setdefault(find(ei), []).append(ei)

SEG = {
    "THUMB":  ((1.492, 0.036, 0.243), (1.443, 0.012, 0.298), 0.014),
    "INDEX":  ((1.458, 0.023, 0.163), (1.446, 0.011, 0.245), 0.0115),
    "MIDDLE": ((1.422, 0.023, 0.149), (1.424, 0.010, 0.235), 0.0115),
    "RING":   ((1.3925, 0.029, 0.160), (1.399, 0.014, 0.235), 0.0115),
    "LITTLE": ((1.3545, 0.031, 0.187), (1.372, 0.019, 0.262), 0.0110),
}
def seg_geom(p0s,p1s):
    p0,p1 = Vector(p0s), Vector(p1s)
    ax = p1-p0; L = ax.length
    return p0, ax/L, L

for name,(p0s,p1s,rad) in SEG.items():
    p0, ax, L = seg_geom(p0s,p1s)
    print(f"===== {name}  L={L:.4f} rad={rad} =====")
    rows=[]
    for root,eids in comps.items():
        ts=[]; aligns=[]; pts=[]
        for ei in eids:
            e=bm.edges[ei]
            mid=(W[e.verts[0].index]+W[e.verts[1].index])*0.5
            d=mid-p0; t=d.dot(ax)
            perp=(d-ax*t).length
            if t< -0.006 or t> L+0.006 or perp> rad+0.006:
                continue
            ts.append(t)
            dd=W[e.verts[1].index]-W[e.verts[0].index]
            if dd.length>1e-9: aligns.append(abs(dd.normalized().dot(ax)))
            pts.append(W[e.verts[0].index]); pts.append(W[e.verts[1].index])
        if len(ts)<3: continue
        zs=[p.z for p in pts]; xs=[p.x for p in pts]
        rows.append((len(ts), round(sum(ts)/len(ts),4), round(max(ts)-min(ts),4),
                     round(sum(aligns)/len(aligns),3), len(eids),
                     round(min(xs),3), round(max(xs),3), round(min(zs),3), round(max(zs),3)))
    rows.sort(key=lambda r: r[1])
    for r in rows:
        print(f"  n_in={r[0]:>3} t={r[1]:<7} tspan={r[2]:<7} align={r[3]:<6} strand={r[4]:<4} x[{r[5]},{r[6]}] z[{r[7]},{r[8]}]")
print("PASS8_DONE")
