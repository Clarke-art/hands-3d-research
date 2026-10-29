import sys,json,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;PREV=O.parent/'hands_c01_whole_hand_motion_feasibility_r1';ROOT=O.parent/'hands'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
I=read(PREV/'INPUT_BINDINGS.json');M=read(PREV/'SCENE_MANIFEST.json')
files=[PREV/n for n in ['MOTION_FEASIBILITY_METRICS.json','SCENE_MANIFEST.json','motion.npz','blender_utils.py','blender_preflight.py','INPUT_BINDINGS.json','RIG_PREFLIGHT.json']]+[Path(M['path']),Path(I['candidate_source'])]
files+=[Path(p) for p in read(PREV/'PROTECTED_FILES_BEFORE.json')]
files=list(dict.fromkeys(files));assert sha(Path(M['path']))==M['sha256']
policy=dict(task='PIANO_HAND_SKIN_COLLISION_STATIC_FEASIBILITY_R1',authority='DESIGN_PROVISIONAL',max_numerical_wall_seconds=570,hard_wall_budget_seconds=600,max_initializations_per_test=2,max_test_seconds=112,max_nfev_per_initialization=28,random_search=False,contact=dict(pad_horizontal_inside_required=True,pad_vertical_max_mm=3.,true_skin_contact_band_mm=.05,no_hover_pass=True,target_key_max_depth_mm=.25,contact_area_label='Geometric near-contact slab area, not soft-tissue load area'),collision=dict(non_target_key_max_depth_mm=.25,numerical_epsilon_m=1e-7,self_positive_depth_mm=.1,bvh_epsilon=0.,full_88_keys=True,connected_mesh_exclusion='Only triangles sharing a vertex or immediately topology-neighboring around continuous root/web; excluded counts reported separately',no_historical_3mm_deep_only_pass=True),solver=dict(root_z='Fixed per initialization at its recorded C01 or approved static value; no upward escape variable',translation_x_y_bounds_mm=[[-150,-30],[60,35]],extra_rotation_bounds_deg=[[-8,-8,-12],[8,8,12]],joint_increment_bounds='Use original static R2 approved planning domain, unchanged',weights_fixed_before_solve=True),source_input=I,source_action_scene=M)
(O/'POLICY_LOCK.json').write_text(json.dumps(policy,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(O/'PROTECTED_INPUTS_BEFORE.json').write_text(json.dumps({str(p):sha(p) for p in files},indent=2)+'\n',encoding='utf8')
print('POLICY_LOCKED',sha(O/'POLICY_LOCK.json'),len(files))
