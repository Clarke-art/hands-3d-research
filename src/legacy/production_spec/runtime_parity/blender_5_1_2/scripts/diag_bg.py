import bpy, sys
argv = sys.argv[sys.argv.index("--")+1:]
o = dict(zip([a.lstrip('-') for a in argv[0::2]], argv[1::2]))
scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
sh = scene.display.shading
sh.light = o.get("light", "FLAT")
sh.color_type = 'SINGLE'
sh.single_color = (0.12, 0.12, 0.15)
sh.background_type = o.get("bgtype", "WORLD")
sh.show_cavity = False
scene.display.render_aa = '8'
w = bpy.data.worlds[0]
scene.world = w; w.use_nodes = True
w.node_tree.nodes.get('Background').inputs[0].default_value = (0.95, 0.95, 0.95, 1.0)
scene.render.resolution_x = 480; scene.render.resolution_y = 480
scene.render.filepath = o["out"]
for ob in bpy.context.view_layer.objects:
    ob.hide_render = (ob.name != "Hand  - Realistic")
ob = bpy.data.objects["Hand  - Realistic"]
m = ob.modifiers.new("wf", 'WIREFRAME'); m.thickness = 0.0009; m.use_boundary = True; m.use_even_offset = True
cd = bpy.data.cameras.new("c"); cd.type='ORTHO'; cd.ortho_scale=0.055; cd.clip_start=0.001; cd.clip_end=1000
cam = bpy.data.objects.new("c", cd); bpy.context.collection.objects.link(cam); scene.camera = cam
from mathutils import Vector
cam.location = Vector((1.6079,0.1344,0.2925)); look = Vector((1.4479,0.0144,0.2925))
cam.rotation_euler = (look - cam.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.render.render(write_still=True)
print("DIAG_DONE", o.get("light"), o.get("bgtype"), o["out"])
