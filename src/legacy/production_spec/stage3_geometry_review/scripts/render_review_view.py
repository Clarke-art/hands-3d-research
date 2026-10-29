# STAGE3 -- minimal review renders of the working copy. One view per process
# (Stage 1C hit a headless multi-render black-frame bug, so keep to one render per run).
#
# Camera placement uses the R1.3.1-CORRECTED frame:
#   DORSAL (back of hand) = -Y  -> camera sits on -Y
#   PALMAR (palm)         = +Y  -> camera sits on +Y
#   RADIAL (thumb side)   = +X
# up = +Z so the forearm (+Z) is at the top of the frame and the fingertips (-Z) at the bottom.
#
# usage: blender -b RIGHT_HAND_BOOTSTRAP_C1.blend --python render_review_view.py -- --out P --view dorsal|palmar|radial_oblique
import bpy, sys, math
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
opt = {}
i = 0
while i < len(argv):
    opt[argv[i].lstrip("-")] = argv[i+1]; i += 2

TARGET = "Hand  - Realistic"
ob = bpy.data.objects[TARGET]
mw = ob.matrix_world
V = [mw @ v.co for v in ob.data.vertices]
centre = Vector(((min(p.x for p in V)+max(p.x for p in V))/2,
                 (min(p.y for p in V)+max(p.y for p in V))/2,
                 (min(p.z for p in V)+max(p.z for p in V))/2))
D = 1.0
VIEWS = {
    "dorsal":         Vector((0.0, -1.0, 0.0)),      # looking at the BACK of the hand
    "palmar":         Vector((0.0,  1.0, 0.0)),      # looking at the PALM
    "radial_oblique": Vector((0.7071, -0.7071, 0.0)) # between RADIAL(+X) and DORSAL(-Y)
}
dirv = VIEWS[opt["view"]]
cam_pos = centre + dirv * D

scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'SINGLE'
scene.display.shading.single_color = (0.72, 0.72, 0.74)
scene.display.shading.show_cavity = True
scene.display.shading.cavity_type = 'BOTH'
scene.display.shading.background_type = 'WORLD'
scene.display.render_aa = '8'
world = bpy.data.worlds[0] if bpy.data.worlds else bpy.data.worlds.new("W")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get('Background')
if bg:
    bg.inputs[0].default_value = (0.97, 0.97, 0.97, 1.0)
scene.render.resolution_x = 900
scene.render.resolution_y = 1200
scene.render.filepath = opt["out"]

cam_data = bpy.data.cameras.new("c")
cam_data.type = 'ORTHO'
cam_data.ortho_scale = 0.34
cam_data.clip_start = 0.001
cam = bpy.data.objects.new("c", cam_data)
bpy.context.collection.objects.link(cam)
scene.camera = cam
cam.location = cam_pos
cam.rotation_euler = (centre - cam_pos).to_track_quat('-Z', 'Y').to_euler()
bpy.ops.render.render(write_still=True)
print("RENDER_DONE", opt["view"], opt["out"], "cam=", [round(c,4) for c in cam_pos])
