import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
import blender_support as s
from blender_support import *
begin=time.perf_counter();edit=read(OUT/'EDIT_RECEIPT.json');lock=read(OUT/'STRATEGY_LOCK.json');base=read(OUT/'BASELINE_B01_ACTUAL.json')
sc,rig,mesh,left,lrig=s.open_scene(edit['candidate_path']);assert sha(edit['candidate_path'])==edit['candidate_sha256']
new=rig.animation_data.action;source=bpy.data.actions[edit['source_action']]
assert c.digest(s.payload(source))==base['actions'][rig.name]['payload']
paths={f'pose.bones["{n}"].rotation_quaternion' for n in edit['bones']}
assert s.payload(new,paths)==s.payload(source,paths)
fa,fb=1+60*lock['support'][0],1+60*lock['support'][1]
def outside(action):return {(f.data_path,f.array_index):[(list(k.co),k.interpolation) for k in f.keyframe_points if k.co.x<fa-1e-5 or k.co.x>fb+1e-5] for f in s.curves(action) if f.data_path in paths}
assert outside(new)==outside(source)
assert s.protected_state(exclude_rig=True)==edit['protected_actions']
assert all(c.digest(c.native(ob,rg))==base['native_structure'][side] for side,ob,rg in [('R',mesh,rig),('L',left,lrig)])
cam=bpy.data.objects[MAN['cameras']['OVERHEAD']];R=np.array(cam.matrix_world)[:3,:3];axis=-R[:,2]/np.linalg.norm(R[:,2]);assert np.max(abs(axis-[0,0,-1]))<1e-10 and cam.data.type=='ORTHO'
save('CANDIDATE_READBACK.json',dict(pass_=True,seconds=time.perf_counter()-begin,original_source_Action_payload_matches_C1=True,other_curves_exact=True,
 outside_edit_key_values_and_interpolation_exact=True,other_actions_exact=True,rig_skin_rest_corrective_exact=True,
 B02_B03_action_channels_outside_support_unchanged=True,camera=cam.name,optical_axis=axis,projection='ORTHO',ortho_scale=cam.data.ortho_scale,
 candidate_sha256=sha(edit['candidate_path']),no_new_action_or_blend_saved=True))
protection('READBACK_PROTECTION.json');print('SAME_CANDIDATE_READBACK_PASS',flush=True)
