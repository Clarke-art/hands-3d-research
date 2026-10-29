# RUNTIME_PARITY (5.1.2) - TEST 5 render smoke.
# Compatibility-guarded equivalent of stage1c render_one.py (identical view framing semantics:
# same camera positions / look-at / ortho scale / resolution / wireframe modifier thickness rules).
# Guards added ONLY so that any Workbench shading attribute renamed between 4.5 and 5.1 cannot
# break the render; the guards record which attributes were applied vs unavailable.
import bpy, sys, math
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
opt = {}
i = 0
while i < len(argv):
    opt[argv[i].lstrip("-")] = argv[i + 1]
    i += 2

out = opt["out"]
mode = opt.get("mode", "solid")
cam_pos = Vector([float(x) for x in opt["cam"].split(",")])
look = Vector([float(x) for x in opt["look"].split(",")])
ortho = float(opt.get("ortho", 0.30))
rx, ry = [int(v) for v in opt.get("res", "1000x1300").split("x")]
TARGET = "Hand  - Realistic"

applied, unavailable = [], []
def set_attr(obj, name, value):
    if hasattr(obj, name):
        try:
            setattr(obj, name, value); applied.append(name)
        except Exception as e:
            unavailable.append(name + ":" + str(e))
    else:
        unavailable.append(name + ":MISSING")

scene = bpy.context.scene
set_attr(scene.render, "engine", 'BLENDER_WORKBENCH')
sh = scene.display.shading
set_attr(sh, "light", 'STUDIO' if mode == "solid" else 'FLAT')
set_attr(sh, "color_type", 'SINGLE')
set_attr(sh, "single_color", (0.65, 0.45, 0.85) if mode == "solid" else (0.12, 0.12, 0.15))
set_attr(sh, "show_cavity", (mode == "solid"))
set_attr(sh, "background_type", 'WORLD')
set_attr(scene.display, "render_aa", '8')
world = bpy.data.worlds[0] if bpy.data.worlds else bpy.data.worlds.new("W")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get('Background')
if bg:
    bg.inputs[0].default_value = (0.95, 0.95, 0.95, 1.0)
scene.render.resolution_x = rx
scene.render.resolution_y = ry
scene.render.filepath = out
for o in bpy.context.view_layer.objects:
    o.hide_render = (o.name != TARGET)
ob = bpy.data.objects[TARGET]
if mode == "wire":
    wfm = ob.modifiers.new("wf_tmp", 'WIREFRAME')
    wfm.thickness = 0.0009 if ortho < 0.12 else 0.0013
    set_attr(wfm, "use_boundary", True)
    set_attr(wfm, "use_even_offset", True)
cam_data = bpy.data.cameras.new("c")
cam_data.type = 'ORTHO'
cam_data.ortho_scale = ortho
cam_data.clip_start = 0.001
cam_data.clip_end = 1000.0
cam = bpy.data.objects.new("c", cam_data)
bpy.context.collection.objects.link(cam)
scene.camera = cam
cam.location = cam_pos
cam.rotation_euler = (look - cam_pos).to_track_quat('-Z', 'Y').to_euler()
bpy.ops.render.render(write_still=True)
print("RENDER_DONE", out)
print("SHADING_APPLIED", applied)
print("SHADING_UNAVAILABLE", unavailable)
print("RUNTIME", bpy.app.version_string)
