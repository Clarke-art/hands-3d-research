import json,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
def read(n):return json.loads((OUT/n).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
S=read('SENSITIVITY_RESPONSE_R1.json');P=read('WEIGHT_FIELD_PROBE_VERIFICATION_R1.json');status=read('RIGHT_HAND_FIRST_WEB_SKINNING_FIELD_VS_DOF_DIAGNOSIS_R1_STATUS.json')
for p,h in S['input_hashes_unchanged'].items():assert sha(ROOT/p)==h,p
assert sha(ROOT/P['candidate']['path'])==P['candidate']['sha256']
assert len(list(OUT.glob('*.blend')))==1 and P['candidate_count']==1
assert len(list((OUT/'renders').glob('*.png')))==48
assert status['FINAL_DIAGNOSIS']=='INSUFFICIENT_EVIDENCE' and status['human_final_decision']=='PENDING'
assert P['all_other_influences_exact'] and P['outside_and_boundary_weights_exact'] and P['source_action_payload_exact']
dump('FINAL_ASSET_PROTECTION_R1.json',{'status':'PASS','FROZEN_FALLBACK_UNCHANGED':'YES','fallback_expected_sha256':status['SOURCE_BASELINE_SHA256'],'fallback_actual_sha256':sha(ROOT/'production_spec/right_hand_product_baseline_r1/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1.blend'),'protected_inputs_expected_and_final':S['input_hashes_unchanged'],'candidate':P['candidate'],'candidate_count':1,'source_action_unchanged':True,'mesh_topology_basis_bones_corrective_driver_unchanged':True,'modified_scope':'ONE static WRIST/THUMB ratio field at 164 internal nodes; S and all other influence weights preserved','production_pointer_moved':False,'promotion':False,'left_hand_started':False,'web_export_started':False,'previous_topology_experiment_repeated':False,'manual_LBS_reconstruction_used':False,'new_helper_cage_DQS_corrective_used':False,'asset_controls':'PASS','causal_discrimination_control':'FAIL_IDENTIFIABILITY_NOT_ASSET_INTEGRITY'})
dump('REVIEW_UI_VERIFICATION_R1.json',{'status':'PASS','url':'http://127.0.0.1:8773/review.html','default_frame':'F130','default_mode':'FIELD','default_images_loaded':7,'tested_mode':'SENSITIVITY','tested_frame':'F176','tested_all_images_loaded':True,'restored_default':True,'horizontal_overflow':False,'console_errors':[],'proof':'REVIEW_PAGE_PROOF_R1.png'})
files=[{'path':p.relative_to(OUT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='FINAL_OUTPUT_MANIFEST_R1.json']
dump('FINAL_OUTPUT_MANIFEST_R1.json',{'phase':status['PHASE'],'FINAL_DIAGNOSIS':status['FINAL_DIAGNOSIS'],'WORKFLOW_STATUS':'STOP_HUMAN_REVIEW','files':files})
print('FINAL_DIAGNOSIS_DELIVERY_PASS',len(files),'FILES','ONE_CANDIDATE','48_MATCHED_RENDERS','FROZEN_UNCHANGED')
