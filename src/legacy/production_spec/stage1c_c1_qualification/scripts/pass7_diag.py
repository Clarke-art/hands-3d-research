# STAGE1C - Pass 7: diagnostics on the opposite-edge component structure
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
def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb: parent[rb] = ra
for f in bm.faces:
    if len(f.edges) != 4: continue
    es = list(f.edges); vs = [set(v.index for v in e.verts) for e in es]
    for i in range(4):
        for j in range(4):
            if i != j and not (vs[i] & vs[j]):
                union(es[i].index, es[j].index); break
comps = {}
for ei in range(nE):
    comps.setdefault(find(ei), []).append(ei)
print("components:", len(comps))
rows = []
for root, eids in comps.items():
    pts = []
    for ei in eids:
        e = bm.edges[ei]
        pts.append(W[e.verts[0].index]); pts.append(W[e.verts[1].index])
    xs = [p.x for p in pts]; ys = [p.y for p in pts]; zs = [p.z for p in pts]
    rows.append((len(eids), round(min(xs),3), round(max(xs),3), round(min(zs),3), round(max(zs),3), round(min(ys),3), round(max(ys),3)))
rows.sort(key=lambda r: -r[0])
for r in rows[:45]:
    print(f"n={r[0]:>4} x[{r[1]},{r[2]}] z[{r[3]},{r[4]}] y[{r[5]},{r[6]}]")
print("PASS7_DONE")
