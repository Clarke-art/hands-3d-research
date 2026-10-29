# STAGE4A -- wireframe evidence renders.
#
# Renders a WIREFRAME-only view of the hand (or of one joint region) using a real
# Wireframe modifier on a copy of the evaluated mesh (headless-safe; the viewport
# wireframe overlay is not available in background mode).
#
# The camera is placed using an anatomical frame DERIVED FROM THE GEOMETRY
# (tip positions + cross products), so the same script gives anatomically
# correct views both before and after CON-9 frame normalization.
#
# usage: blender -b <file.blend> --python stage4a_wire.py -- --out <png> --view <v> [--l1] [--zoom <m>]
#   view: dorsal | palmar | radial | region
#   --region-name <name> --region-center x,y,z   (for --view region)
import bpy, sys, math, json, os
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
opt = {}
i = 0
while i < len(argv):
    k = argv[i].lstrip("-")
    if k in ("l1",):
        opt[k] = True
        i += 1
    else:
        opt[k] = argv[i + 1]
        i += 2

TARGET = "Hand  - Realistic"
ob = bpy.data.objects[TARGET]

if opt.get("l1"):
    bpy.context.view_layer.objects.active = ob
    for o in bpy.context.selected_objects:
        o.select_set(False)
    ob.select_set(True)
    for m in list(ob.modifiers):
        if m.type == 'MULTIRES':
            m.levels = 1
            bpy.ops.object.modifier_apply(modifier=m.name)
    ob.select_set(False)
else:
    for m in ob.modifiers:
        if m.type == 'MULTIRES':
            m.show_viewport = False      # render the REAL base cage, not the evaluated L1

mw = ob.matrix_world
V = [mw @ v.co for v in ob.data.vertices]


def nearest(p):
    best, bi = 1e18, 0
    for i2, q in enumerate(V):
        d = (q - p).length_squared
        if d < best:
            best, bi = d, i2
    return bi


TIP = {
    "little": Vector((1.3515, 0.0319, 0.1879)), "ring": Vector((1.3933, 0.0320, 0.1599)),
    "middle": Vector((1.4231, 0.0251, 0.1490)), "index": Vector((1.4586, 0.0239, 0.1643)),
    "thumb": Vector((1.4977, 0.0358, 0.2421)),
}
# forearm cap = extreme +Z plateau; seed frame from Stage-3 geometry, then re-derive
if opt.get("dorsal"):
    # explicit anatomical frame (canonical, post CON-9) -- preferred
    DORSAL = Vector([float(x) for x in opt["dorsal"].split(",")]).normalized()
    r = Vector([float(x) for x in opt.get("radial", "1,0,0").split(",")]).normalized()
    u = Vector([float(x) for x in opt.get("distal", "0,0,1").split(",")]).normalized()
    PALMAR = -DORSAL
else:
    # geometric fallback: the forearm cut cap is the extreme end along the DISTAL axis,
    # so try both ends and keep the one that puts the thumb on the +radial side.
    zs = [p.z for p in V]
    best = None
    for sign in (1.0, -1.0):
        cap = [p for p in V if sign * p.z > sign * max(sign * z for z in zs) - 0.0025]
        fc = sum(cap, Vector()) / len(cap)
        u = (V[nearest(TIP["middle"])] - fc).normalized()
        rr = (V[nearest(TIP["index"])] - V[nearest(TIP["little"])]).normalized()
        rr = (rr - u * rr.dot(u)).normalized()
        dd = u.cross(rr).normalized()
        # thumb must sit on the RADIAL side of the middle finger axis for a right hand
        score = (V[nearest(TIP["thumb"])] - V[nearest(TIP["middle"])]).dot(rr)
        if best is None or score > best[0]:
            best = (score, u, rr, dd)
    _sc, u, r, DORSAL = best
    PALMAR = -DORSAL

centre = sum(V, Vector()) / len(V)
bb_min = Vector((min(p.x for p in V), min(p.y for p in V), min(p.z for p in V)))
bb_max = Vector((max(p.x for p in V), max(p.y for p in V), max(p.z for p in V)))
bb_c = (bb_min + bb_max) / 2

# ---------------- wireframe copy ----------------
dg = bpy.context.evaluated_depsgraph_get()
me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
ob_w = bpy.data.objects.new("wire", me)
ob_w.matrix_world = mw.copy()          # mesh data is in LOCAL space -- carry the object transform
bpy.context.scene.collection.objects.link(ob_w)
wf = ob_w.modifiers.new("wf", 'WIREFRAME')
wf.thickness = float(opt.get("thickness", 0.00055))
wf.use_replace = True
wf.use_boundary = True
wf.use_even_offset = False
ob.hide_render = True

# ---------------- camera ----------------
VIEWS = {
    "dorsal": (DORSAL, 0.33),
    "palmar": (PALMAR, 0.33),
    "radial": (r, 0.33),
}
view = opt["view"]
if view == "region":
    c = Vector([float(x) for x in opt["region-center"].split(",")])
    d = Vector([float(x) for x in opt.get("region-dir", "0,-1,0").split(",")]).normalized()
    scale = float(opt.get("zoom", 0.055))
    target = c
else:
    d, scale = VIEWS[view]
    target = bb_c
cam_pos = target + d * 1.0

scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'FLAT'
scene.display.shading.color_type = 'SINGLE'
scene.display.shading.single_color = (0.09, 0.10, 0.13)
scene.display.shading.background_type = 'VIEWPORT'
scene.display.shading.background_color = (1.0, 1.0, 1.0)
scene.display.render_aa = '8'
world = bpy.data.worlds[0] if bpy.data.worlds else bpy.data.worlds.new("W")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get('Background')
if bg:
    bg.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
scene.render.film_transparent = False
scene.render.resolution_x = int(opt.get("rx", 1100))
scene.render.resolution_y = int(opt.get("ry", 1400))
scene.render.filepath = os.path.abspath(opt["out"])

cd = bpy.data.cameras.new("c")
cd.type = 'ORTHO'
cd.ortho_scale = scale
cd.clip_start = 0.001
cam = bpy.data.objects.new("c", cd)
bpy.context.scene.collection.objects.link(cam)
scene.camera = cam
cam.location = cam_pos
cam.rotation_euler = (target - cam_pos).to_track_quat('-Z', 'Y').to_euler()

bpy.ops.render.render(write_still=True)
_p = os.path.abspath(opt["out"])
print("WIRE_DONE", view, _p, "exists=", os.path.exists(_p),
      "size=", (os.path.getsize(_p) if os.path.exists(_p) else -1),
      "tris=", sum(len(p.vertices) - 2 for p in me.polygons),
      "DORSAL=", [round(x, 3) for x in DORSAL])
