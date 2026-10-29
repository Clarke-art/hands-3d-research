import sys,shutil
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
from support import *
R1=ROOT/'experiments/hands_c1_dynamic_artist_correction_poc_r1'
candidate=OUT/'EXIT_CANDIDATE_2_NOT_APPROVED.blend';final=OUT/'EXIT_CORRECTED_NOT_APPROVED.blend'
assert not final.exists();shutil.copyfile(candidate,final)
previous=read(R1/'RENDER_DELIVERY_MANIFEST.json');records=[]
sc,rig,mesh,left,lrig=open_scene(final)
sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
cameras={}
for kind in ['OVERHEAD','SIDE_OBLIQUE']:
 folder=OUT/('candidate_'+kind.lower()+'_frames');folder.mkdir()
 cam=bpy.data.objects[MAN['cameras'][kind]];sc.camera=cam
 cameras[kind]=dict(name=cam.name,matrix=np.array(cam.matrix_world).tolist(),type=cam.data.type,scale=cam.data.ortho_scale,lens=cam.data.lens)
 for ix,frame in enumerate(range(127,203)):
  c.settime(sc,(frame-1)/60);sc.render.filepath=str(folder/f'{ix:04d}.png');bpy.ops.render.render(write_still=True)
 for t,label in [(2.6,'HOLD_UNCHANGED'),(2.90,'EXIT'),(2.92,'TARGET_END'),(2.9214260000000003,'E5_ON'),(3.066666666666667,'HANDOFF'),(3.12,'RESTORED')]:
  c.settime(sc,t);sc.render.filepath=str(OUT/f'R2_{label}_{kind}.png');bpy.ops.render.render(write_still=True)
assert cameras==previous['records'][0]['cameras']
# Same-time R1 evidence, rendered from its isolated copy, never written to R1.
sc,rig,mesh,left,lrig=open_scene(OUT/'R1_START_ISOLATED_NOT_APPROVED.blend')
sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
for kind in ['OVERHEAD','SIDE_OBLIQUE']:
 sc.camera=bpy.data.objects[MAN['cameras'][kind]]
 for t,label in [(2.92,'TARGET_END'),(3.066666666666667,'HANDOFF')]:
  c.settime(sc,t);sc.render.filepath=str(OUT/f'R1_{label}_{kind}.png');bpy.ops.render.render(write_still=True)
save('RENDER_MANIFEST.json',dict(final=str(final),sha256=sha(final),exact_candidate_copy=sha(final)==sha(candidate),cameras=cameras,original_C1_frames_reused_from=str(R1),original_source_sha256=previous['records'][0]['sha256'],original_C1_frozen_sha_matches=previous['records'][0]['sha256']==sha(SOURCE),camera_exact_match=True,frames=76,source_frame_range=[127,202],first_time=2.1,last_time=3.35,fps=60,engine=sc.render.engine,visibility='Original objects and visibility retained; no image geometry edits'))
protection('RENDER_INPUT_RECEIPT.json')
print('R2_RENDER_COMPLETE',flush=True)
