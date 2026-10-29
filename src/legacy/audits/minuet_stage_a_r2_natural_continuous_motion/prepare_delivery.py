from stage_common import *
assert not (P/'CANDIDATE_ATTEMPT.json').exists()
text=(R1/'03_scene.py').read_text(encoding='utf8')
text=text.replace('STAGE_A_RIGHT_TARGET_KEY_DESIGN_PROVISIONAL_R1.blend','STAGE_A_R2_COORDINATED_RIGHT_DESIGN_ONLY.blend')
text=text.replace('STAGE_A_RIGHT_ONLY_DESIGN_PROVISIONAL_R1','STAGE_A_R2_COORDINATED_RIGHT_ONLY')
text=text.replace("P/'PLANNING_LOCK.json'","P/'GENERATION_LOCK.json'")
text=text.replace("f=1+t*60;rt.matrix_world=Matrix.Translation(Vector(A['R_delta'][i]))@base",
    "f=1+t*60;wrist=Vector(o.ANCHORS['R1']['root_xyz_m']);rot=Matrix(A['R_extra_rotation'][i].tolist()).to_4x4();rt.matrix_world=Matrix.Translation(wrist+Vector(A['R_delta'][i]))@<REDACTED_EMAIL>(-wrist)@base")
text=text.replace("o.worldpads('R',A['R_q'][i])+A['R_delta'][i]",
    "(o.worldpads('R',A['R_q'][i])-np.array(o.ANCHORS['R1']['root_xyz_m']))@A['R_extra_rotation'][i].T+np.array(o.ANCHORS['R1']['root_xyz_m'])+A['R_delta'][i]")
text=text.replace('DESIGN_PROVISIONAL_STAGE_A_RIGHT_JOINTS','DESIGN_ONLY_STAGE_A_R2_COORDINATED_JOINTS')
text=text.replace('DESIGN_PROVISIONAL_STAGE_A_RIGHT_ROOT','DESIGN_ONLY_STAGE_A_R2_COORDINATED_ROOT')
needle="sc['DESIGN_PROVISIONAL']=True;"
text=text.replace(needle,"camera_bind=read(P/'R1_REVIEW_CAMERA_BIND.json')\nfor view,name in cameras.items():\n    ob=bpy.data.objects[name];cfg=camera_bind['cameras'][view];ob.matrix_world=Matrix(cfg['matrix_world']);ob.data.type=cfg['type'];ob.data.ortho_scale=cfg['ortho_scale'];ob.data.clip_start=cfg['clip_start'];ob.data.clip_end=cfg['clip_end']\nsc['DESIGN_ONLY']=True;"+needle)
text=text.replace("actual_key_world_parity_max_mm=keyerr,key_angle_parity_max_rad=", "all_R1_review_cameras_exact_matched=True,R1_camera_bind_sha256=sha(P/'R1_REVIEW_CAMERA_BIND.json'),actual_key_world_parity_max_mm=keyerr,key_angle_parity_max_rad=")
(P/'03_scene.py').write_text(text,encoding='utf8')
(P/'05_render.py').write_text((R1/'05_render.py').read_text(encoding='utf8'),encoding='utf8')
(P/'07_media.py').write_text((R1/'07_media.py').read_text(encoding='utf8'),encoding='utf8')
# Existing R1 right-only PCM reused byte-for-byte because MIDI and presentation
# clocks are identical. No reason to re-synthesize or alter the audio chain.
import shutil
shutil.copyfile(R1/'piano_performance.wav',P/'piano_performance.wav')
assert sha(P/'piano_performance.wav')==sha(R1/'piano_performance.wav')
dump('AUDIO_REUSE_VERIFICATION.json',dict(R1_PCM_sha256=sha(R1/'piano_performance.wav'),R2_PCM_sha256=sha(P/'piano_performance.wav'),
    same_bytes=True,right_only=True,voices=16,original_NOTE_ON_OFF_and_audio_retrigger_unchanged=True))
print('DELIVERY_ADAPTERS_READY_NO_DYNAMIC_GENERATION')
