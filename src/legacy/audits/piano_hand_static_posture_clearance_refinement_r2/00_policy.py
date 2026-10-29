from pathlib import Path
import json,hashlib,copy
P=Path(__file__).resolve().parent;R1=P.parent/'piano_hand_four_pose_static_feasibility_r1'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
assert not (P/'SOLVED_STATIC_POSES_R2.json').exists(),'Never overwrite a completed single candidate with a new policy.'
before=read(R1/'PROTECTED_INPUTS_BEFORE_R1.json')
for p in R1.rglob('*'):
 if p.is_file() and '__pycache__' not in p.parts:before[str(p.resolve())]=sha(p)
assert all(Path(p).is_file() and sha(Path(p))==v for p,v in before.items())
dump('PROTECTED_INPUTS_BEFORE_R2.json',before)
base=read(R1/'STATIC_POSTURE_POLICY_R1.json');policy=copy.deepcopy(base)
policy.update({'phase':'PIANO_HAND_STATIC_POSTURE_CLEARANCE_REFINEMENT_R2','client_date':'2026-10-09','candidate_count':1,'pose_count':4,'source_candidate_sha256':sha(R1/'STATIC_POSTURE_CANDIDATE_R1.blend'),'source_policy_sha256':sha(R1/'STATIC_POSTURE_POLICY_R1.json'),'human_feedback_authority':{'LEFT_STATIC_CONTACT':'PASS_CANDIDATE','LEFT_NATURALNESS':'NOT_APPROVED: idle three too straight/splayed, tense, bounds saturated','RIGHT_FSHARP_CONTACT':'PASS','RIGHT_NEIGHBOR_CLEARANCE':'FAIL D#5 / G#5','FOUR_POSE_HUMAN_APPROVAL':'NOT_GRANTED'},'reference_search':'NO_NEW_SEARCH','scope':'One coordinated shared-root static refinement; never alter mesh/rest/weights/drivers/key geometry/material.'})
policy['constraints']['NATURAL_IDLE_FINGERS']['ENGINEERING_ASSUMPTION']='Nonuniform positive RSSF-relative curvature with inward index/ring base spread, bounded moderate increments; no fake home-key targets for left idle three. Human explicitly rejected the R1 straight/splayed result.'
policy['constraints']['NEIGHBOR_KEY_CLEARANCE']['ENGINEERING_ASSUMPTION']='Use complete unchanged 3300-vertex linear-blend skin prediction in a signed key-piece-box distance penalty, including the previously missed side vertices. Full saved/reopened screen and normal views remain final checks.'
policy['constraints']['PALM_CLEARANCE']['ENGINEERING_ASSUMPTION']='5mm palm/wrist planning volume distance; cap wrist-root z to68mm left/65mm right; no lifting both hands arbitrarily to escape neighbors.'
policy['constraints']['WRIST_ORIENTATION']['ENGINEERING_ASSUMPTION']='Yaw ±12°, pitch -6°..10°, roll ±6°, before result inspection. Paired scenes share exact root. These are a priori engineering policy, not physiology.'
policy['root_bounds']={'L':{'xyz_mm':[[-248,-125,42],[-208,-70,68]],'seed_xyz_mm':[-221.4,-95,60]},'R':{'xyz_mm':[[222,-145,42],[264,-95,65]],'seed_xyz_mm':[236,-135,48]},'yaw_pitch_roll_deg':[[-12,-6,-6],[12,10,6]],'seed_yaw_pitch_roll_deg':{'L':[5,0,0],'R':[-2,1,2]},'pair_root_difference_mm':0,'pair_orientation_difference_deg':0,'interpretation':'Common root can differ from R1. Left maximum root height reduced70→68mm; right65mm cap. Root bounds decided before solve.'}
policy['joint_increment_bounds_deg']['LEFT_IDLE_INDEX']=[[3,5,2,0],[18,24,14,10]]
policy['joint_increment_bounds_deg']['LEFT_IDLE_MIDDLE']=[[3,5,2,-4],[18,24,14,4]]
policy['joint_increment_bounds_deg']['LEFT_IDLE_RING']=[[3,5,2,-10],[18,24,14,0]]
policy['joint_increment_bounds_deg'].pop('LEFT_IDLE_INDEX_MIDDLE_RING',None)
policy['priors_deg']={'L1':[[4,3,2,0],[8,11,5,6],[10,14,7,0],[9,12,6,-6],[22,12,6,10]],'L2':[[8,5,3,0],[8,11,5,6],[10,14,7,0],[9,12,6,-6],[16,8,4,10]],'R1':[[2,2,1,-22],[12,11,5,-14],[1,2,1,-7],[8,9,5,8],[14,7,3,18]],'R2':[[2,2,1,-22],[12,11,5,-14],[4,6,3,-7],[8,9,5,8],[14,7,3,18]]}
policy['contact_regions']['white_preferred_y_mm']={'THUMB':20,'INDEX':35,'RING':34,'LITTLE':28}
policy['contact_regions']['black_preferred_y_mm']=60
policy['contact_regions']['right_index_ring_preparation']='Actual WHITE front piece only, y in7..45mm; full skin distance to black sides also penalized. No isolated lifting of index/ring, root and all digits solved jointly.'
policy['contact_regions']['left_idle_targets']='NONE; no home keys for index/middle/ring'
policy['solver'].update({'max_nfev_per_pair':150,'skin_proxy':'Full 3300-vertex linear-blend prediction from unchanged R1 extracted mesh/weights; no generated deformation or modified weights. Blender preserved drivers evaluated after save/reopen.','proxy_sampling':'ALL3300 vertices. R1 key-boundary misses are included, not just8 low sample vertices.','initialization':'One deterministic RSSF-prior initialization per hand-pair with declared root seeds; no alternate candidate seeds.','full_vertex_penalty':'SDF of union of inherited frozen rectangular key pieces;2mm neighboring-key skin margin;5mm palm/wrist margin. Target-key distal active patch permits0mm distance. Distal patch rest radius18mm from fixed mesh pad, selected before solve.','planned_key_bands':{'L':[21,61],'R':[58,101]},'planned_key_band_reason':'Broad fixed geometric bands around complete allowed root/hand extent; final screen independently checks all88 keys.','joint_boundary_relief':'Penalty within final10% of active/endpoint flex bounds; cannot change hard limits. Does not certify low muscular load.','priority':'Hard no-reverse bounded joint domain and paired common root, nonuniform idle curvature/spacing, whole-skin neighbors and palm clearances, active fixed/skin contact, natural preparation. Conflicts remain failure; never relax after inspecting.'})
policy['solver']['residual_weights']={'active_contact_mm':6,'active_skin_contact_mm':4,'prepared_region_mm':2,'prepared_gap_interval_mm':2,'preferred_xy_mm':0.12,'prepared_preferred_height_mm':0.25,'left_idle_joint_rad':30,'other_joint_rad':7,'active_joint_rad':5,'paired_joint_difference_rad':4,'root_prior_mm':0.10,'root_rotation_rad':10,'full_skin_clearance_mm':3,'joint_limit_relief_rad':12,'idle_pad_clearance_mm':3}
dump('STATIC_REFINEMENT_POLICY_R2.json',policy)
dump('PRE_SOLVE_LOCK_R2.json',{'policy_sha256':sha(P/'STATIC_REFINEMENT_POLICY_R2.json'),'solver_script_sha256':sha(P/'01_solve.py'),'created_before_result_inspection':True,'one_candidate':True,'Human_feedback_source':'Current pasted request','protected_files':len(before)})
dump('INHERITED_INPUTS_R2.json',{'R1_files':{n:sha(R1/n) for n in ['PIANO_HAND_FOUR_POSE_STATIC_FEASIBILITY_R1_REPORT.md','STATIC_POSTURE_CANDIDATE_R1.blend','STATIC_POSTURE_POLICY_R1.json','STATIC_POSTURE_RESULTS_R1.json','HAND_KEYBOARD_CLEARANCE_R1.json','EVIDENCE_LEFT_L1_L2_R1.png','EVIDENCE_RIGHT_R1_R2_R1.png','EVIDENCE_SIDE_CLEARANCE_R1.png','FORMAL_INPUT_EXTRACTION_R1.json']},'R1_not_rerun':True,'new_material_changes':False,'new_reference_search':False})
print('R2_POLICY_LOCKED',sha(P/'STATIC_REFINEMENT_POLICY_R2.json'),len(before),'protected')
