# STAGE4A experiment -- geodesic level-set loop insertion.
#
# Inserts an edge loop along a geodesic level set {g = g_cut} measured from a
# digit tip. On a closed simply-connected surface a level set is a CLOSED curve,
# so the crossing-edge chain closes and subdividing it yields an all-quad result
# (no dangling chain ends).
#
# usage: blender -b RIGHT_HAND_BOOTSTRAP_C1.blend --python exp_cut.py -- <tip x,y,z> <g_cut_mm> <out.png>
import bpy, bmesh, sys, heapq, os, math
from mathutils import Vector

TARGET = "Hand  - Realistic"
argv = sys.argv[sys.argv.index("--") + 1:]
TIP = Vector([float(x) for x in argv[0].split(",")])
G_CUT = float(argv[1]) / 1000.0
OUT = argv[2] if len(argv) > 2 else None

ob = bpy.data.objects[TARGET]
mw = ob.matrix_world
bpy.context.view_layer.objects.active = ob
for o in bpy.context.selected_objects:
    o.select_set(False)
ob.select_set(True)
for m in list(ob.modifiers):
    if m.type == 'MULTIRES':
        m.levels = 1
        bpy.ops.object.modifier_apply(modifier=m.name)
ob.select_set(False)

bm = bmesh.new()
bm.from_mesh(ob.data)
bm.verts.ensure_lookup_table()
bm.edges.ensure_lookup_table()

def stats(tag):
    ng = sum(1 for f in bm.faces if len(f.verts) > 4)
    tri = sum(1 for f in bm.faces if len(f.verts) == 3)
    quad = sum(1 for f in bm.faces if len(f.verts) == 4)
    nonman = sum(1 for e in bm.edges if not e.is_manifold)
    bnd = sum(1 for e in bm.edges if e.is_boundary)
    print(f"  [{tag}] V={len(bm.verts)} E={len(bm.edges)} F={len(bm.faces)} "
          f"quad={quad} tri={tri} ngon={ng} nonmanifold={nonman} boundary={bnd} "
          f"tris={tri + 2 * quad + sum(len(f.verts) - 2 for f in bm.faces if len(f.verts) > 4)}")
    return tri, ng, nonman


print("=" * 70)
print("TIP", list(TIP), "G_CUT(by tip) =", G_CUT * 1000, "mm")
stats("before")

# nearest vertex to the tip
bv, bd = None, 1e18
for v in bm.verts:
    d = ((mw @ v.co) - TIP).length_squared
    if d < bd:
        bd, bv = d, v
print("  seed vertex", bv.index, "world", [round(c, 5) for c in (mw @ bv.co)], "dist_mm", round(math.sqrt(bd) * 1000, 2))

# geodesic from the seed
dist = {v: 1e18 for v in bm.verts}
dist[bv] = 0.0
pq = [(0.0, bv.index)]
vlist = list(bm.verts)
while pq:
    d, vi = heapq.heappop(pq)
    u = vlist[vi]
    if d > dist[u] + 1e-15:
        continue
    for e in u.link_edges:
        w = e.other_vert(u)
        nd = d + e.calc_length()
        if nd < dist[w] - 1e-16:
            dist[w] = nd
            heapq.heappush(pq, (nd, w.index))

# crossing edges
cross = [e for e in bm.edges
         if (dist[e.verts[0]] - G_CUT) * (dist[e.verts[1]] - G_CUT) < 0]
print("  crossing edges:", len(cross))
# chain closure check: every vertex touched should carry exactly 2 crossing edges
deg = {}
for e in cross:
    for v in e.verts:
        deg[v] = deg.get(v, 0) + 1
from collections import Counter
hist = Counter(deg.values())
print("  chain vertex degree histogram:", dict(hist), " (expect all == 2 for a closed chain)")

res = bmesh.ops.subdivide_edges(bm, edges=cross, cuts=1, use_grid_fill=True,
                                use_only_quads=False, smooth=0.0)
bm.verts.ensure_lookup_table()
bm.faces.ensure_lookup_table()
tri, ng, nonman = stats("after")

# where are the new n-gons / tris?
bad = [f for f in bm.faces if len(f.verts) != 4]
print("  non-quad faces:", len(bad))
for f in bad[:20]:
    c = sum((mw @ v.co for v in f.verts), Vector()) / len(f.verts)
    print("    n=", len(f.verts), "centre", [round(x, 4) for x in c])
print("RESULT", {"crossing_edges": len(cross), "deg_hist": dict(hist),
                 "ngon": ng, "tri": tri, "nonmanifold": nonman,
                 "verts_added": len(bm.verts) - (3300)})

bm.free()
