from common import *
dump('PROTECTED_HISTORY_HASHES_BEFORE.json',inventory())
cap=read(CAP_PATH);r3=read(R3_PATH)
checks={'current_derivative':sha(CAND)==EXPECTED_CAND,'old_R2':sha(OLD_CAND)==EXPECTED_OLD,'corrected_rig':sha(CORRECTED)==EXPECTED_RIG,
 'cap_frozen':cap['status']=='HUMAN_APPROVED_FROZEN' and cap['combined_authority_hash']==digest(read(CAP_PATH.parent/'CAP_AUTHORITY_CANONICAL_PAYLOAD.json'))==EXPECTED_CAP,
 'R3_frozen':r3['status']=='HUMAN_APPROVED_FROZEN' and digest(r3)==EXPECTED_R3 and r3['membership']['membership_hash']==EXPECTED_MEMBER}
for directory,phase,verdict in [('static_skin_compatibility_revalidation_after_donor_transfer_r1','STATIC_SKIN_COMPATIBILITY_REVALIDATION_AFTER_DONOR_TRANSFER_R1','PASS_STATIC_SKIN_COMPATIBILITY_REQUALIFIED'),('joint_surface_rest_zero_bind_revalidation_after_donor_transfer_r1','JOINT_SURFACE_REST_ZERO_BIND_REVALIDATION_AFTER_DONOR_TRANSFER_R1','PASS_JOINT_REST_ZERO_BIND_REQUALIFIED'),('true_cap_bound_revalidation_after_donor_transfer_r1','TRUE_CAP_BOUND_REVALIDATION_AFTER_DONOR_TRANSFER_R1','PASS_CURRENT_GEOMETRY_BOUND_AUTHORITY_ESTABLISHED')]:
 p=S5/directory/(phase+'_STATUS.json');d=read(p);checks[directory]=d['VERDICT']==verdict
 if 'R2_WEIGHT_HASH' in d:checks[directory+'_weights']=d['R2_WEIGHT_HASH']==EXPECTED_WEIGHTS
sources=read(S5/'targeted_rig_and_skin_data_rebuild_r2/HUMAN_AMENDMENT_AND_INPUT_VERIFICATION_R2.json')
dump('FROZEN_INPUT_RECEIPT_REOPEN.json',sources)
closure=read(S5/'targeted_deformation_final_human_closure_r1/TARGETED_DEFORMATION_FINAL_HUMAN_CLOSURE_R1.json')
checks['targeted_human_closure']=closure['active_recovery_status']=='PASS_WITH_HUMAN_REVIEW_COMPLETE'
for k,v in closure['sources'].items():
 if isinstance(v,dict) and 'path' in v and 'sha256' in v:checks['human_source_'+k]=sha(ROOT/v['path'])==v['sha256']
for k,v in closure['closure_basis'].items():checks['closure_basis_'+k]=sha(ROOT/v['path'])==v['sha256']
# Hashes frozen at the old R2 input receipt, including FIRST_WEB and old9.
def scan(x):
 if isinstance(x,dict):
  if 'path' in x and 'sha256' in x and (ROOT/x['path']).is_file():checks['R2_receipt_'+x['path']]=sha(ROOT/x['path'])==x['sha256']
  for v in x.values():scan(v)
 elif isinstance(x,list):
  for v in x:scan(v)
scan(sources)
for n,h in sources['authority_component_hashes'].items():checks['frozen_component_'+n]=sha(AUTH/n)==h
matrix=read(HIST/'TARGETED_FIXTURE_MATRIX.json')
assert len(matrix['poses'])==7 and set(matrix['fixtures'])=={'CAP37','OLD_CAP9','FIRST_WEB','FRESH_R3_TRANSITION_COLLAR','EDGE5879'}
checks['cap_membership']=matrix['fixtures']['CAP37']['core']==cap['vertex_ids']
checks['FIRST_WEB_membership']=matrix['fixtures']['FIRST_WEB']['core']==r3['FIRST_WEB21']['membership_vertex_ids']
checks['old9_membership']=matrix['fixtures']['OLD_CAP9']['core']==r3['old_cap9']['vertex_ids']
dump('PREREQUISITE_GATE_R1.json',{'checks':checks,'status':'PASS' if all(checks.values()) else 'FAIL_CLOSED','sources':{'current':ref(CAND),'old_R2':ref(OLD_CAND),'rig':ref(CORRECTED),'cap':ref(CAP_PATH),'R3':ref(R3_PATH)},'live_weight_check':'REQUIRED_BEFORE_POSES'})
assert all(checks.values()),checks
dump('TARGETED_FIXTURE_MATRIX_R1.json',matrix)
print('READONLY PREFLIGHT PASS; native weight and rig check precedes pose execution',flush=True)
