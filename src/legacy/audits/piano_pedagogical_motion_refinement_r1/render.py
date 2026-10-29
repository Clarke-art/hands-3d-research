import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'audits/minuet_stage_c_r2_local_finger_overlap_refinement'))
from blender_local import *
from bpy_extras.object_utils import world_to_camera_view
report=read(OUT/'ACTUAL_VALIDATION.json');assert read(OUT/'DIAGNOSTIC_RENDER_AUTHORITY.json')['final_status']=='FAIL_CLOSED'
man=read(OUT/'SCENE_MANIFEST.json');src=read(ROOT/'audits/minuet_stage_c_lightweight_animation_poc_r1/SCENE_MANIFEST.json')
assert sha(man['path'])==man['sha256']
bpy.ops.wm.open_mainfile(filepath=man['path'],load_ui=False,use_scripts=False)
sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc
rig=bpy.data.objects[man['mapping']['R']['rig']];mesh=bpy.data.objects[man['mapping']['R']['mesh']]
new=rig.animation_data.action;slot=rig.animation_data.action_slot.identifier
with bpy.data.libraries.load(src['path'],link=False) as (a,b):b.actions=['DESIGN_ONLY_LIGHTWEIGHT_R1_RIGHT_JOINTS_NOT_APPROVED']
source=bpy.data.actions['DESIGN_ONLY_LIGHTWEIGHT_R1_RIGHT_JOINTS_NOT_APPROVED']
def bind(a):rig.animation_data.action=a;rig.animation_data.action_slot=a.slots[slot]
sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.use_persistent_data=True
probes=[('B01',1.133333333),('B02',3.825),('B03_INDEX',2.6),('B03_MIDDLE',4.05),('B03_RING',4.916666667)]
rois=read(ROOT/'audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/LOCAL_SKIN_ROI.json')
ids=sorted(set(v for d in ['INDEX','MIDDLE','RING'] for v in rois[d]['vertices']))
stills=[]
for label,t in probes:
 for view,cam in man['cameras'].items():
  sc.camera=bpy.data.objects[cam];screen=[];files={}
  for state,action in [('SOURCE',source),('NEW',new)]:
   bind(action);settime(sc,t);V=mesh_pose(mesh)[0]
   for v in V[ids]:
    p=world_to_camera_view(sc,sc.camera,Vector(v));screen.append([p.x*1280,(1-p.y)*720])
   folder=OUT/'stills';folder.mkdir(exist_ok=True);file=folder/f'{label}_{state}_{view}.png'
   sc.render.filepath=str(file);bpy.ops.render.render(write_still=True);files[state]=file.name
  points=np.array(screen);low=np.maximum(np.floor(points.min(0)-35),[0,0]);high=np.minimum(np.ceil(points.max(0)+35),[1280,720])
  stills.append(dict(label=label,time=float(t),view=view,files=files,crop=[int(low[0]),int(low[1]),int(high[0]),int(high[1])],camera=cam))
(OUT/'STILL_MANIFEST.json').write_text(json.dumps(stills,indent=2),encoding='utf8')
bind(new)
for f in range(1,358):
 sc.frame_set(f)
 for view,cam in man['cameras'].items():
  folder=OUT/'_frames'/view;folder.mkdir(parents=True,exist_ok=True);file=folder/f'{f-1:04d}.png'
  if file.exists():continue
  sc.camera=bpy.data.objects[cam];sc.render.filepath=str(file);bpy.ops.render.render(write_still=True)
 if f%30==0:print('NEW_CANDIDATE_RENDER',f,357,flush=True)
(OUT/'RENDER_MANIFEST.json').write_text(json.dumps(dict(candidate_sha256=man['sha256'],frames_each=357,fps=60,dimensions=[1280,720],cameras=man['cameras'],original_cameras_unchanged=True,source_action_was_only_loaded_readonly=True),indent=2),encoding='utf8')
