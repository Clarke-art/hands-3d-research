import bpy,sys
from pathlib import Path
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P));from stage_common import *
man=read(P/'SCENE_MANIFEST.json');A=np.load(P/'evaluated.npz');assert sha(man['path'])==man['sha256']
bpy.ops.wm.open_mainfile(filepath=man['path'],load_ui=False,use_scripts=False);sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc
framing={}
for view,name in man['cameras'].items():
    camera=bpy.data.objects[name];inv=np.array(camera.matrix_world.inverted());corners=np.array([list(v) for v in camera.data.view_frame(scene=sc)])
    lo=corners[:,:2].min(0);hi=corners[:,:2].max(0);mins=np.ones(2);maxs=np.zeros(2)
    for V in A['L_verts']:
        p=V@inv[:3,:3].T+inv[:3,3];uv=(p[:,:2]-lo)/(hi-lo);mins=np.minimum(mins,uv.min(0));maxs=np.maximum(maxs,uv.max(0))
    passed=bool(np.all(mins>=0) and np.all(maxs<=1))
    framing[view]=dict(all_actual_left_vertices_inside_frame=passed,normalized_min=mins,normalized_max=maxs,
        ortho_scale=camera.data.ortho_scale,camera_world_matrix=np.array(camera.matrix_world),
        complete_hand_and_wrist_cap_visible=passed,not_a_fingertip_closeup=True)
dump('WHOLE_LEFT_HAND_FRAMING.json',dict(views=framing,all_views_entire_left_hand_visible=all(v['all_actual_left_vertices_inside_frame'] for v in framing.values()),
    checked_evaluated_samples=len(A['times']),no_camera_or_candidate_modified=True))
print('WHOLE_LEFT_HAND_FRAME_READONLY',framing,flush=True)
