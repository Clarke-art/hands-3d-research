import sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));from blender_utils import *
A=np.load(O/'STATIC_REACH_STATES.npz')
bpy.ops.wm.open_mainfile(filepath=man['path'],load_ui=False,use_scripts=False);sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc;rig=bpy.data.objects[man['mapping']['R']['rig']];mesh=bpy.data.objects[man['mapping']['R']['mesh']];rt=bpy.data.objects[man['mapping']['R']['root']]
rig.animation_data_clear();rt.animation_data_clear();sc.render.engine='BLENDER_WORKBENCH';sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.display.shading.light='STUDIO';sc.display.shading.color_type='MATERIAL';sc.display.shading.show_shadows=True;sc.display.shading.show_cavity=True;sc.display.shading.cavity_type='BOTH';sc.display.shading.background_type='WORLD';sc.world.color=(.08,.08,.08)
# Only diagnostic stills; no frame sequence, no video production on a failed preflight.
folder=O/'stills';folder.mkdir(exist_ok=True);manifest=[]
for idx,label,views in [(2,'R08_E5_MIDDLE', ['OVERHEAD']),(5,'R11_B02_E5_MIDDLE',['OVERHEAD','SIDE_OBLIQUE']),(6,'R12_FSHARP_RING',['OVERHEAD','SIDE_OBLIQUE']),(8,'R14_G4_THUMB',['OVERHEAD'])]:
 t=float(A['times'][idx]);settime(sc,t);apply(A['states'][idx],rt,rig);n=I['notes'][idx]
 for view in views:
  sc.camera=bpy.data.objects[man['cameras'][view]];sc.camera.data.ortho_scale=.34
  target=Vector((c.KEYS[n['key_index']]['key_center'][0],-.035,.015));sc.camera.location=target+Vector((0,0,.8) if view=='OVERHEAD' else (.11,-.48,.22));sc.camera.rotation_euler=(target-sc.camera.location).to_track_quat('-Z','Y').to_euler()
  file=folder/f'STATIC_ONLY_{label}_{view}.png';sc.render.filepath=str(file);start=time.perf_counter();bpy.ops.render.render(write_still=True);seconds=time.perf_counter()-start
  manifest.append(dict(file=str(file),label=label,time=t,view=view,static_only=True,continuous_action_generated=False,render_seconds=seconds))
  print('DIAGNOSTIC_STILL',file.name,round(seconds,3),flush=True)
out('STILL_MANIFEST.json',manifest)
