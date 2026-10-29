# STAGE4A experiment -- CON-1 loop insertion by TOPOLOGICAL EDGE-RING WALK.
#
# In an all-quad mesh, walking the "opposite edge" of each quad gives an edge ring
# that always CLOSES. Splitting every edge of a closed ring puts exactly two cut
# edges in every crossed quad, so the subdivision yields an all-quad result with
# no dangling chain ends and no n-gons.
#
# usage: blender -b C1.blend --python exp_ring.py -- <axis_pt x,y,z> <axis_dir x,y,z> <dorsal x,y,z> <axial_off_mm>
import bpy, bmesh, sys
from mathutils import Vector

TARGET = "Hand  - Realistic"
argv = sys.argv[sys.argv.index("--") + 1:]
PT = Vector([float(x) for x in argv[0].split(",")])
AX = Vector([float(x) for x in argv[1].split(",")]).normalized()
DORS = Vector([float(x) for x in argv[2].split(",")]).normalized()
OFF = float(argv[3]) / 1000.0

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
bm.faces.ensure_lookup_table()


def rep(tag):
    q = sum(1 for f in bm.faces if len(f.verts) == 4)
    t = sum(1 for f in bm.faces if len(f.verts) == 3)
    n = sum(1 for f in bm.faces if len(f.verts) > 4)
    nm = sum(1 for e in bm.edges if not e.is_manifold)
    bd = sum(1 for e in bm.edges if e.is_boundary)
    tot = t + 2 * q + sum(len(f.verts) - 2 for f in bm.faces if len(f.verts) > 4)
    print(f"  [{tag}] V={len(bm.verts)} F={len(bm.faces)} quad={q} tri={t} ngon={n} "
          f"nonmanifold={nm} boundary={bd} TRIS={tot}")


def opposite_edge_in_face(f, e):
    es = list(f.edges)
    n = len(es)
    if n % 2:
        return None
    try:
        i = es.index(e)
    except ValueError:
        return None
    return es[(i + n // 2) % n]


def ring_walk(e0):
    ring = set()
    stack = [e0]
    closed = True
    while stack:
        e = stack.pop()
        if e in ring:
            continue
        ring.add(e)
        nxt = 0
        for f in e.link_faces:
            o = opposite_edge_in_face(f, e)
            if o is None:
                closed = False
                continue
            nxt += 1
            if o not in ring:
                stack.append(o)
        if len(e.link_faces) < 2:
            closed = False
    # closure test: every vertex must carry exactly 2 ring edges
    deg = {}
    for e in ring:
        for v in e.verts:
            deg[v] = deg.get(v, 0) + 1
    return ring, closed, sorted(set(deg.values()))


print("=" * 74)
print("axial offset %+.1f mm" % (OFF * 1000))
rep("before")

PTL = mw.inverted() @ PT
d = [(v.co - PTL).dot(AX) for v in bm.verts]

# seed: crossing edge nearest the DORSAL midline of the finger
best, bestscore = None, -1e18
for e in bm.edges:
    a, b = e.verts[0].index, e.verts[1].index
    da, db = d[a], d[b]
    if not ((da > OFF + 1e-9 and db < OFF - 1e-9) or (da < OFF - 1e-9 and db > OFF + 1e-9)):
        continue
    mid = (e.verts[0].co + e.verts[1].co) / 2 - PTL
    rad = (mid - AX * mid.dot(AX)).length
    if rad > 0.016:
        continue
    sc = mid.dot(DORS) - 8.0 * rad
    if sc > bestscore:
        bestscore, best = sc, e
print("  seed edge:", best.index if best else None,
      "mid world", [round(x, 4) for x in (mw @ ((best.verts[0].co + best.verts[1].co) / 2))] if best else None)

ring, closed, degset = ring_walk(best)
print("  ring size: %d edges, closed=%s, vertex-degrees=%s" % (len(ring), closed, degset))
lens = [e.calc_length() for e in ring]
print("  ring edge length mm: min %.2f mean %.2f max %.2f" % (min(lens) * 1000, sum(lens) / len(lens) * 1000, max(lens) * 1000))
# where does the ring sit?
own = []
for e in ring:
    for v in e.verts:
        w = mw @ v.co - PT
        own.append((w.dot(AX) * 1000, (w - AX * w.dot(AX)).length * 1000))
print("  ring axial_mm range %.1f .. %.1f ; radial_mm range %.1f .. %.1f"
      % (min(o[0] for o in own), max(o[0] for o in own), min(o[1] for o in own), max(o[1] for o in own)))

bmesh.ops.subdivide_edges(bm, edges=list(ring), cuts=1, use_grid_fill=True,
                          use_only_quads=False, smooth=0.0)
bm.verts.ensure_lookup_table()
bm.faces.ensure_lookup_table()
rep("after")
bad = [f for f in bm.faces if len(f.verts) != 4]
print("  non-quad faces:", len(bad))
for f in bad[:8]:
    c = sum((v.co for v in f.verts), Vector()) / len(f.verts)
    print("    n=%d at" % len(f.verts), [round(x, 4) for x in (mw @ c)])
bm.free()
