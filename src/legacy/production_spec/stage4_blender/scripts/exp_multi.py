# STAGE4A experiment -- insert several rings around one joint and save for visual check.
#
# usage: blender -b C1.blend --python exp_multi.py -- <axis_pt> <axis_dir> <dorsal> <off1,off2,...> <out.blend>
import bpy, bmesh, sys, os
from mathutils import Vector

TARGET = "Hand  - Realistic"
argv = sys.argv[sys.argv.index("--") + 1:]
PT = Vector([float(x) for x in argv[0].split(",")])
AX = Vector([float(x) for x in argv[1].split(",")]).normalized()
DORS = Vector([float(x) for x in argv[2].split(",")]).normalized()
OFFS = [float(x) / 1000.0 for x in argv[3].split(",")]
OUT = argv[4]

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


def opposite(f, e):
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
    ring, stack = set(), [e0]
    while stack:
        e = stack.pop()
        if e in ring:
            continue
        ring.add(e)
        for f in e.link_faces:
            o = opposite(f, e)
            if o is not None and o not in ring:
                stack.append(o)
    return ring


def insert_ring(off):
    PTL = mw.inverted() @ PT
    d = [(v.co - PTL).dot(AX) for v in bm.verts]
    best, bs = None, -1e18
    for e in bm.edges:
        da, db = d[e.verts[0].index], d[e.verts[1].index]
        if not ((da > off + 1e-9 and db < off - 1e-9) or (da < off - 1e-9 and db > off + 1e-9)):
            continue
        mid = (e.verts[0].co + e.verts[1].co) / 2 - PTL
        rad = (mid - AX * mid.dot(AX)).length
        if rad > 0.016:
            continue
        sc = mid.dot(DORS) - 8.0 * rad
        if sc > bs:
            bs, best = sc, e
    if best is None:
        print("  !! no seed edge at offset %.1f mm" % (off * 1000))
        return None
    ring = ring_walk(best)
    before = len(bm.verts)
    bmesh.ops.subdivide_edges(bm, edges=list(ring), cuts=1, use_grid_fill=True,
                              use_only_quads=False, smooth=0.0)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    own = []
    for e in ring:
        for v in e.verts:
            w = mw @ v.co - PT
            own.append((w.dot(AX) * 1000, (w - AX * w.dot(AX)).length * 1000))
    print("  off %+.1f mm -> ring %d edges, +%d verts, axial %.1f..%.1f, radial %.1f..%.1f"
          % (off * 1000, len(ring), len(bm.verts) - before,
             min(o[0] for o in own), max(o[0] for o in own),
             min(o[1] for o in own), max(o[1] for o in own)))
    return len(ring)


for off in OFFS:
    insert_ring(off)

q = sum(1 for f in bm.faces if len(f.verts) == 4)
t = sum(1 for f in bm.faces if len(f.verts) == 3)
n = sum(1 for f in bm.faces if len(f.verts) > 4)
print("  FINAL V=%d F=%d quad=%d tri=%d ngon=%d TRIS=%d nonmanifold=%d"
      % (len(bm.verts), len(bm.faces), q, t, n,
         t + 2 * q + sum(len(f.verts) - 2 for f in bm.faces if len(f.verts) > 4),
         sum(1 for e in bm.edges if not e.is_manifold)))

bm.to_mesh(ob.data)
bm.free()
ob.data.update()
os.makedirs(os.path.dirname(OUT), exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=OUT, copy=True, compress=False)
print("  SAVED", OUT)
