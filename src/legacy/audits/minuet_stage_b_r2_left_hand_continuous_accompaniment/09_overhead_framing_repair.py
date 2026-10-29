import bpy,sys
from pathlib import Path
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P));from stage_common import *
man=read(P/'SCENE_MANIFEST.json');before=read(P/'WHOLE_LEFT_HAND_FRAMING.json');motion_hash=sha(P/'motion.npz');candidate_hash=sha(man['path'])
assert before['views']['TEACHING']['all_actual_left_vertices_inside_frame'] and before['views']['SIDE_OBLIQUE']['all_actual_left_vertices_inside_frame']
bpy.ops.wm.open_mainfile(filepath=man['path'],load_ui=False,use_scripts=False);sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc
camera=bpy.data.objects[man['cameras']['OVERHEAD']];old=float(camera.data.ortho_scale);camera.data.ortho_scale=.60;sc.camera=camera
sc.render.image_settings.file_format='PNG';sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100
folder=P/'_frames/OVERHEAD_FULL_HAND';folder.mkdir(parents=True,exist_ok=True)
for f in range(1,sc.frame_end+1):
    dest=folder/f'{f-1:04d}.png'
    if dest.exists():continue
    sc.frame_set(f);sc.render.filepath=str(dest);bpy.ops.render.render(write_still=True)
V=np.load(P/'evaluated.npz')['L_verts'];inv=np.array(camera.matrix_world.inverted());corners=np.array([list(v) for v in camera.data.view_frame(scene=sc)]);lo=corners[:,:2].min(0);hi=corners[:,:2].max(0)
mins=np.ones(2);maxs=np.zeros(2)
for vertices in V:
    q=vertices@inv[:3,:3].T+inv[:3,3];uv=(q[:,:2]-lo)/(hi-lo);mins=np.minimum(mins,uv.min(0));maxs=np.maximum(maxs,uv.max(0))
assert np.all(mins>=0) and np.all(maxs<=1)
assert sha(P/'motion.npz')==motion_hash and sha(man['path'])==candidate_hash
dump('VIDEO_FRAMING_REPAIR.json',dict(reason='Only overhead wrist cap was cropped by about1.49% at the lowest sample; teaching/side entire hand already visible.',
    view='OVERHEAD',old_ortho_scale=old,new_ortho_scale=.60,orientation_location_unchanged=True,
    normalized_min=mins,normalized_max=maxs,all_delivered_views_entire_left_hand_visible=True,
    teaching_side_videos_unchanged=True,new_overhead_frame_folder='OVERHEAD_FULL_HAND',
    candidate_sha256=candidate_hash,motion_sha256=motion_hash,no_new_candidate=True,no_pose_or_solver_change=True,
    candidate_blend_not_resaved=True,display_reframe_only=True))
print('SAME_CANDIDATE_OVERHEAD_FULL_HAND_ONLY',flush=True)
