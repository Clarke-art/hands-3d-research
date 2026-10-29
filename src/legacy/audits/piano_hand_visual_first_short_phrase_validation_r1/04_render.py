import bpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P));from phrase_common import *
man=read(P/'SCENE_MANIFEST.json');assert sha(P/'SHORT_PHRASE_DESIGN_ONLY_R1.blend')==man['sha256'];bpy.ops.wm.open_mainfile(filepath=str(P/'SHORT_PHRASE_DESIGN_ONLY_R1.blend'),load_ui=False,use_scripts=False);sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc
sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.use_persistent_data=True
if sc.render.engine=='CYCLES':
 prefs=bpy.context.preferences.addons['cycles'].preferences
 try:
  prefs.compute_device_type='CUDA';prefs.get_devices();gpus=[v for v in prefs.devices if v.type!='CPU']
  for v in prefs.devices:v.use=v in gpus
  if gpus:sc.cycles.device='GPU'
 except Exception as e:print('CPU_FALLBACK',str(e),flush=True)
indices=[20,35,50,57,64,76,110,124,133] if '--precheck' in sys.argv else range(sc.frame_end)
for j in indices:
 sc.frame_set(j+1)
 for view,name in man['cameras'].items():
  folder=P/'_frames'/view;folder.mkdir(parents=True,exist_ok=True);dest=folder/f'{j:04}.png'
  if dest.exists():continue
  sc.camera=bpy.data.objects[name];sc.render.filepath=str(dest);bpy.ops.render.render(write_still=True)
 if j%10==0 or j==sc.frame_end-1:print('SAME_CANDIDATE_RENDER',j+1,'/',sc.frame_end,flush=True)
if '--precheck' not in sys.argv:dump('RENDER_MANIFEST.json',{'candidate_sha256':man['sha256'],'scene':sc.name,'frames_each':sc.frame_end,'fps':60,'views':man['cameras'],'dimensions':[1280,720],'engine':sc.render.engine,'normal_speed':True,'continuous_same_scene':True,'no_pose_stitching':True,'original_time_window':[START,END]})
