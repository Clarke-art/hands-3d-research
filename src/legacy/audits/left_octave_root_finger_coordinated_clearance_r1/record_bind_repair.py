import json,hashlib,shutil
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent;LAST=P.parent/'left_little_finger_moving_key_reachability_r1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
a=np.load(P/'coordinated_motion.npz');b=np.load(LAST/'probe_motion.npz')
assert np.array_equal(a['root_matrices'][0],np.eye(4))
delta=float(np.max(abs(a['root_matrices'][0]-b['root_matrices'][0])));assert delta>1
repair=json.loads((P/'IMPLEMENTATION_REPAIR_R1.json').read_text(encoding='utf8'));lock=json.loads((P/'PRE_SOLVE_LOCK_R1.json').read_text(encoding='utf8'))
repair['second_confirmed_implementation_bug']={'type':'UNEVALUATED_OTHER_SCENE_ROOT_RETURNS_IDENTITY','invalid_first_root_matrix':a['root_matrices'][0].tolist(),'expected_source_first_root_matrix':b['root_matrices'][0].tolist(),'max_matrix_error':delta,'repair':'Use evaluated source dynamic scene frame1 root, then assert equality against inherited source motion. Never read uninitialized other-scene matrix_world.','wrong_coordinate_attempt_cost':json.loads((P/'ROOT_FINGER_COORDINATION_R1.json').read_text(encoding='utf8'))['cost'],'invalid_output_not_a_product_motion_candidate':True,'output_path_reused_after_implementation_repair':True}
repair['bind_initialization_bug_confirmed']=True;repair['invalid_coordinate_result_sha256']=sha(P/'ROOT_FINGER_COORDINATION_R1.json');repair['invalid_coordinate_blend_sha256']=sha(P/'LEFT_OCTAVE_COORDINATED_CLEARANCE_CANDIDATE_R1.blend');repair['previous_repaired_script_sha256']=repair['repaired_script_sha256'];repair['repaired_script_sha256']=sha(P/'01_coordinate.py');repair['policy_sha256_unchanged']=sha(P/'COORDINATED_CLEARANCE_POLICY_R1.json')==lock['policy_sha256'];repair['implementation_invalid_attempts']=2
for name in ['ROOT_FINGER_COORDINATION_R1.json','coordinated_motion.npz','solve.log','SAVE_REOPEN_VERIFICATION_R1.json']:
 if (P/name).exists():shutil.copyfile(P/name,P/('invalid_bind_'+name))
(P/'IMPLEMENTATION_REPAIR_R1.json').write_text(json.dumps(repair,indent=2),encoding='utf8');print('BIND_INITIALIZATION_IMPLEMENTATION_BUG_RECORDED',delta)
