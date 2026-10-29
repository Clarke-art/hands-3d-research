# STAGE4A experiment -- loop insertion along a HARMONIC level set.
#
# Raw Dijkstra geodesics are noisy on a discrete mesh, so their level sets break
# into open fragments (mixing n-gons into the result). Replacing the distance by a
# HARMONIC scalar field (Laplace solve with Dirichlet ends: 0 at the digit tip,
# 1 on the distal-wrist band) makes the level sets smooth, so the crossing-edge
# chain closes and the subdivision stays all-quad.
#
# usage: blender -b RIGHT_HAND_BOOTSTRAP_C1.blend --python exp_cut2.py -- <tip x,y,z> <frac 0..1>
import bpy, bmesh, sys, heapq, math
from collections import Counter
from mathutils import Vector

TARGET = "Hand  - Realistic"
argv = sys.argv[sys.argv.index("--") + 1:]
TIP = Vector([float(x) for x in argv[0].split(",")])
FRAC = float(argv[1])

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
nv = len(bm.verts)
print("=" * 74, "\nV=%d E=%d F=%d" % (nv, len(bm.edges), len(bm.faces)))


def report(tag):
    quads = sum(1 for f in bm.faces if len(f.verts) == 4)
    tris = sum(1 for f in bm.faces if len(f.verts) == 3)
    ng = sum(1 for f in bm.faces if len(f.verts) > 4)
    nm = sum(1 for e in bm.edges if not e.is_manifold)
    bd = sum(1 for e in bm.edges if e.is_boundary)
    tris_tot = tris + 2 * quads + sum(len(f.verts) - 2 for f in bm.faces if len(f.verts) > 4)
    print(f"  [{tag}] V={len(bm.verts)} F={len(bm.faces)} quad={quads} tri={tris} "
          f"ngon={ng} nonmanifold={nm} boundary={bd} TRIS={tris_tot}")
    return quads, tris, ng, nm, bd, tris_tot


report("before")

# ---- seed + raw geodesic (used only to build the Dirichlet ends)
bv, bd = None, 1e18
for v in bm.verts:
    d = ((mw @ v.co) - TIP).length_squared
    if d < bd:
        bd, bv = d, v
dist = [1e18] * nv
dist[bv.index] = 0.0
pq = [(0.0, bv.index)]
while pq:
    d, i = heapq.heappop(pq)
    u = bm.verts[i]
    if d > dist[i] + 1e-15:
        continue
    for e in u.link_edges:
        w = e.other_vert(u)
        nd = d + e.calc_length()
        if nd < dist[w.index] - 1e-16:
            dist[w.index] = nd
            heapq.heappush(pq, (nd, w.index))

gmax = max(dist)
print("  geodesic max = %.1f mm" % (gmax * 1000))

# ---- harmonic field: 0 at tip, 1 on the far band
nb = [[] for _ in range(nv)]
for e in bm.edges:
    a, b = e.verts[0].index, e.verts[1].index
    nb[a].append(b)
    nb[b].append(a)

FIXED = {}
FIXED[bv.index] = 0.0
far = [i for i in range(nv) if dist[i] > 0.95 * gmax]
for i in far:
    FIXED[i] = 1.0
print("  Dirichlet: tip=1 vert, far band=%d verts" % len(far))

phi = [dist[i] / gmax for i in range(nv)]
for i, val in FIXED.items():
    phi[i] = val
for it in range(600):
    new = phi[:]
    for i in range(nv):
        if i in FIXED or not nb[i]:
            continue
        s = 0.0
        for j in nb[i]:
            s += phi[j]
        new[i] = s / len(nb[i])
    phi = new
print("  harmonic solved; phi range %.4f .. %.4f" % (min(phi), max(phi)))

CUT = FRAC
cross = [e for e in bm.edges
         if (phi[e.verts[0].index] - CUT) * (phi[e.verts[1].index] - CUT) < 0]
deg = Counter()
for e in cross:
    for v in e.verts:
        deg[v.index] += 1
print("  crossing edges: %d  degree hist: %s" % (len(cross), dict(Counter(deg.values()))))

if cross:
    bmesh.ops.subdivide_edges(bm, edges=cross, cuts=1, use_grid_fill=True,
                              use_only_quads=False, smooth=0.0)
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    report("after")
    bad = [f for f in bm.faces if len(f.verts) != 4]
    print("  non-quad faces:", len(bad))
    for f in bad[:12]:
        c = sum((mw @ v.co for v in f.verts), Vector()) / len(f.verts)
        print("    n=%d centre" % len(f.verts), [round(x, 4) for x in c])
bm.free()
