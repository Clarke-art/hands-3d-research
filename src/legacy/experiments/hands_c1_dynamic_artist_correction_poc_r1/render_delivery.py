import sys,shutil
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
from support import *
candidate=OUT/'CANDIDATE_2_IMPLEMENTATION_FIXED_NOT_APPROVED.blend'
final=OUT/'DYNAMIC_CANDIDATE_NOT_APPROVED.blend'
if not final.exists():shutil.copyfile(candidate,final)
else:assert sha(final)==sha(candidate)
records=[]
for tag,path in [('original',SOURCE),('candidate',final)]:
 sc,rig,mesh,left,lrig=open_scene(path)
 sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
 cameras={}
 for kind in ['OVERHEAD','SIDE_OBLIQUE']:
  folder=OUT/(tag+'_'+kind.lower()+'_frames');folder.mkdir(exist_ok=True)
  cam=bpy.data.objects[MAN['cameras'][kind]];sc.camera=cam
  cameras[kind]=dict(name=cam.name,matrix=np.array(cam.matrix_world).tolist(),type=cam.data.type,scale=cam.data.ortho_scale,lens=cam.data.lens)
  for ix,frame in enumerate(range(127,203)):
   t=(frame-1)/60;c.settime(sc,t);dest=folder/f'{ix:04d}.png'
   if not dest.exists():sc.render.filepath=str(dest);bpy.ops.render.render(write_still=True)
  c.settime(sc,2.6);sc.render.filepath=str(OUT/(tag.upper()+'_EXACT_2_600_'+kind+'.png'))
  if not Path(sc.render.filepath).exists():bpy.ops.render.render(write_still=True)
 # Identical auxiliary local side, no material/object visibility changes.
 cam=bpy.data.objects.get('DYNAMIC_AUX_INDEX_SIDE')
 if not cam:
  cd=bpy.data.cameras.new('DYNAMIC_AUX_INDEX_SIDE');cam=bpy.data.objects.new(cd.name,cd);sc.collection.objects.link(cam)
  cam.location=(.015,-.035,.085);cam.rotation_euler=(Vector((.13,.045,.017))-cam.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=.145
 sc.camera=cam
 for t,label in [(2.2,'ENTRY_START'),(2.45,'TARGET_START'),(2.6,'HOLD'),(2.90,'EXIT'),(2.921426,'E5_ON'),(3.12,'RESTORED')]:
  c.settime(sc,t);sc.render.filepath=str(OUT/f'{tag.upper()}_AUX_{label}.png')
  if not Path(sc.render.filepath).exists():bpy.ops.render.render(write_still=True)
 records.append(dict(tag=tag,blend=str(path),sha256=sha(path),cameras=cameras,frames=76,source_frames=[127,202],source_first_time=2.1,source_last_time=3.35,render_engine=sc.render.engine,visibility='all original scene visibility preserved'))
assert records[0]['cameras']==records[1]['cameras']
save('RENDER_DELIVERY_MANIFEST.json',dict(records=records,cameras_identical=True,final_copy_exact=sha(final)==sha(candidate),fps=60))
protection('RENDER_DELIVERY_INPUT_RECEIPT.json')
print('RENDER_DELIVERY_COMPLETE',flush=True)
