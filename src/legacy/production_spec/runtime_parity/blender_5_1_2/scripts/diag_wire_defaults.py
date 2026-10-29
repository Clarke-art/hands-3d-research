import bpy, sys
ob = bpy.data.objects["Hand  - Realistic"]
m = ob.modifiers.new("wf", 'WIREFRAME')
print("DIAG use_replace        =", getattr(m, "use_replace", "MISSING"))
print("DIAG use_boundary       =", m.use_boundary)
print("DIAG use_even_offset    =", m.use_even_offset)
print("DIAG thickness          =", m.thickness)
sh = bpy.context.scene.display.shading
print("DIAG shading.light        =", sh.light)
print("DIAG shading.background_type =", sh.background_type)
print("DIAG shading.color_type   =", sh.color_type)
print("DIAG shading.show_cavity  =", sh.show_cavity)
print("DIAG shading.single_color =", tuple(sh.single_color))
w = bpy.context.scene.world
bg = w.node_tree.nodes.get('Background') if w and w.use_nodes else None
print("DIAG world background color =", tuple(bg.inputs[0].default_value) if bg else None)
print("DIAG world use_nodes =", w.use_nodes if w else None)
print("RUNTIME", bpy.app.version_string)
