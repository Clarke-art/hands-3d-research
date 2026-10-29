# STAGE4A experiment -- CON-1 loop insertion by PLANE cross-section.
#
# A plane intersects a CLOSED surface in a set of closed curves, so the
# crossing-edge chain always closes and the subdivision stays all-quad
# (restricting the cut to a sub-region would break the chain and mix in n-gons).
#
# usage: blender -b RIGHT_HAND_BOOTSTRAP_C1.blend --python exp_plane.py -- <co x,y,z> <no x,y,z>
import bpy, bmesh, sys
from collections import Counter
from mathutils import Vector

TARGET = "Hand  - Realistic"
argv = sys.argv[sys.argv.index("--") + 1:]
CO = Vector([float(x) for x in argv[0].split(",")])
NO = Vector([float(x) for x in argv[1].split(",")]).normalized()

ob = bpy.data.objects[TARGET]
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


def report(tag, bm):
    q = sum(1 for f in bm.faces if len(f.verts) == 4)
    t = sum(1 for f in bm.faces if len(f.verts) == 3)
    n = sum(1 for f in bm.faces if len(f.verts) > 4)
    nm = sum(1 for e in bm.edges if not e.is_manifold)
    bd = sum(1 for e in bm.edges if e.is_boundary)
    tot = t + 2 * q + sum(len(f.verts) - 2 for f in bm.faces if len(f.verts) > 4)
    print(f"  [{tag}] V={len(bm.verts)} F={len(bm.faces)} quad={q} tri={t} ngon={n} "
          f"nonmanifold={nm} boundary={bd} TRIS={tot}")
    return q, t, n, nm, bd, tot


print("=" * 74)
print("plane_co", list(CO), "plane_no", [round(x, 4) for x in NO])
report("before", bm)

CO_L = ob.matrix_world.inverted() @ CO      # bmesh coordinates are LOCAL

res = bmesh.ops.bisect_plane(
    bm,
    geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
    dist=1e-6,
    plane_co=CO_L,
    plane_no=NO,
    use_snap_center=False,
    clear_outer=False,
    clear_inner=False,
)
cut_edges = [g for g in res["geom_cut"] if isinstance(g, bmesh.types.BMEdge)]
print("  bisect_plane created %d cut edges" % len(cut_edges))

bm.verts.ensure_lookup_table()
bm.faces.ensure_lookup_table()
q, t, n, nm, bd, tot = report("after", bm)

if t or n:
    bad = [f for f in bm.faces if len(f.verts) != 4]
    print("  non-quad faces:", len(bad))
    for f in bad[:10]:
        c = sum((v.co for v in f.verts), Vector()) / len(f.verts)
        print("    n=%d at" % len(f.verts), [round(x, 4) for x in (ob.matrix_world @ c)])
bm.free()
