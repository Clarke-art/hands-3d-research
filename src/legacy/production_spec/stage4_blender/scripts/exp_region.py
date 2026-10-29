# STAGE4A experiment -- CON-1 loop insertion restricted to a finger by a cylinder.
#
# Cuts with a plane perpendicular to the finger axis, but only keeps the crossing
# edges whose BOTH endpoints lie inside a cylinder around the finger axis.
# Larger radius = longer chain (more of the collar) but more risk of grazing other
# fingers. The test reports exactly how many non-quad faces the subdivision leaves
# and where they land, so the radius can be chosen empirically.
#
# usage: blender -b C1.blend --python exp_region.py -- <axis_pt x,y,z> <axis_dir x,y,z> <R_mm>
import bpy, bmesh, sys
from mathutils import Vector

TARGET = "Hand  - Realistic"
argv = sys.argv[sys.argv.index("--") + 1:]
PT = Vector([float(x) for x in argv[0].split(",")])
AX = Vector([float(x) for x in argv[1].split(",")]).normalized()
R = float(argv[2]) / 1000.0

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


def rep(tag):
    q = sum(1 for f in bm.faces if len(f.verts) == 4)
    t = sum(1 for f in bm.faces if len(f.verts) == 3)
    n = sum(1 for f in bm.faces if len(f.verts) > 4)
    nm = sum(1 for e in bm.edges if not e.is_manifold)
    bd = sum(1 for e in bm.edges if e.is_boundary)
    tot = t + 2 * q + sum(len(f.verts) - 2 for f in bm.faces if len(f.verts) > 4)
    print(f"  [{tag}] V={len(bm.verts)} F={len(bm.faces)} quad={q} tri={t} ngon={n} "
          f"nonmanifold={nm} boundary={bd} TRIS={tot}")
    return t, n, tot


print("=" * 74)
print("axis_pt", list(PT), "axis_dir", [round(x, 4) for x in AX], "R_mm", R * 1000)
rep("before")

PTL = mw.inverted() @ PT
d = [(v.co - PTL).dot(AX) for v in bm.verts]
rad = []
for v in bm.verts:
    w = v.co - PTL
    radial = (w - AX * w.dot(AX)).length
    rad.append(radial)

inside = [r <= R for r in rad]
cross = []
for e in bm.edges:
    a, b = e.verts[0].index, e.verts[1].index
    if not (inside[a] and inside[b]):
        continue
    if (d[a] > 1e-9 and d[b] < -1e-9) or (d[a] < -1e-9 and d[b] > 1e-9):
        cross.append(e)
print("  verts inside cylinder: %d / %d" % (sum(inside), len(inside)))
print("  crossing edges inside cylinder: %d" % len(cross))

bmesh.ops.subdivide_edges(bm, edges=cross, cuts=1, use_grid_fill=True,
                          use_only_quads=False, smooth=0.0)
bm.verts.ensure_lookup_table()
bm.faces.ensure_lookup_table()
t, n, tot = rep("after")
bad = [f for f in bm.faces if len(f.verts) != 4]
print("  non-quad faces:", len(bad))
for f in bad[:14]:
    c = sum((v.co for v in f.verts), Vector()) / len(f.verts)
    w = mw @ c
    ww = w - PT
    rr = (ww - AX * ww.dot(AX)).length
    print("    n=%d at" % len(f.verts), [round(x, 4) for x in w], "r_mm=%.1f axial_mm=%.1f" % (rr * 1000, ww.dot(AX) * 1000))
bm.free()
