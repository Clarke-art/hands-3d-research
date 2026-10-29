import bpy
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(OUT/'HAND_ASSET_BENCHMARK_STATIC.blend'),use_scripts=False,load_ui=False)
sc=bpy.context.scene
for ident in ['C1','MAKEHUMAN']:
 for o in sc.objects:
  if o.type=='MESH':o.hide_render=o.name!=ident+'__NEUTRAL'
 sc.camera.location=(0,0,-.5);sc.camera.rotation_euler=(Vector((0,0,0))-sc.camera.location).to_track_quat('-Z','Y').to_euler()
 sc.render.filepath=str(OUT/('PREVIEW_REVERSE_'+ident+'.png'));bpy.ops.render.render(write_still=True)
