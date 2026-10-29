import bpy
sc = bpy.context.scene
print("DIAG film_transparent =", sc.render.film_transparent)
print("DIAG world            =", sc.world.name if sc.world else None)
print("DIAG render.engine    =", sc.render.engine)
print("DIAG image_settings   =", sc.render.image_settings.file_format, sc.render.image_settings.color_mode)
print("RUNTIME", bpy.app.version_string)
