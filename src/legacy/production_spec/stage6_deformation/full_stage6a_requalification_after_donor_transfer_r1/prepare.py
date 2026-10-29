from common import *
dump('PROTECTED_HISTORY_HASHES_BEFORE.json',inventory())
cap=read(CAP_PATH);r3=read(R3_PATH)
checks={'current_derivative_hash':sha(CAND)==EXPECTED_CAND,'corrected_rig_hash':sha(CORRECTED)==EXPECTED_RIG,'cap37_frozen':cap['status']=='HUMAN_APPROVED_FROZEN' and cap['combined_authority_hash']==digest(read(CAP_PATH.parent/'CAP_AUTHORITY_CANONICAL_PAYLOAD.json'))==EXPECTED_CAP,'cap37_count':len(cap['vertex_ids'])==37 and len(cap['face_ids'])==25,'fresh_R3_frozen':r3['status']=='HUMAN_APPROVED_FROZEN' and digest(r3)==EXPECTED_R3,'fresh_R3_membership_hash':r3['membership']['membership_hash']==sha(R3_PATH.parent/'R3_OWNERSHIP_MEMBERSHIP_CANONICAL.json')==EXPECTED_MEMBER}
prerequisites={}
for directory,phase,verdict in [('joint_surface_rest_zero_bind_revalidation_after_donor_transfer_r1','JOINT_SURFACE_REST_ZERO_BIND_REVALIDATION_AFTER_DONOR_TRANSFER_R1','PASS_JOINT_REST_ZERO_BIND_REQUALIFIED'),('static_skin_compatibility_revalidation_after_donor_transfer_r1','STATIC_SKIN_COMPATIBILITY_REVALIDATION_AFTER_DONOR_TRANSFER_R1','PASS_STATIC_SKIN_COMPATIBILITY_REQUALIFIED'),('true_cap_bound_revalidation_after_donor_transfer_r1','TRUE_CAP_BOUND_REVALIDATION_AFTER_DONOR_TRANSFER_R1','PASS_CURRENT_GEOMETRY_BOUND_AUTHORITY_ESTABLISHED'),('targeted_deformation_revalidation_after_donor_transfer_r1','TARGETED_DEFORMATION_REVALIDATION_AFTER_DONOR_TRANSFER_R1','PASS_TARGETED_DEFORMATION_REQUALIFIED')]:
 p=S5/directory/(phase+'_STATUS.json');d=read(p);checks[phase]=d['VERDICT']==verdict;prerequisites[phase]=ref(p)
 if 'R2_WEIGHT_HASH' in d:checks[phase+'_weight_hash']=d['R2_WEIGHT_HASH']==EXPECTED_WEIGHTS
 checks[phase+'_asset_dependency']=d.get('current_asset',d.get('production_input',{})).get('sha256',EXPECTED_CAND)==EXPECTED_CAND
authorityhashes=read(S5/'targeted_rig_and_skin_data_rebuild_r2/HUMAN_AMENDMENT_AND_INPUT_VERIFICATION_R2.json')['authority_component_hashes']
for n,h in authorityhashes.items():checks['frozen_'+n]=sha(ROOT/'audits/cap_skin_driver_and_weight_authority_reconciliation_r1'/n)==h
fixtures=read(S5/'cap_fixture_static_validation_and_targeted_deformation_r1/TARGETED_FIXTURE_MATRIX.json')['fixtures']
checks['FIRST_WEB21_exact_membership']=fixtures['FIRST_WEB']['core']==r3['FIRST_WEB21']['membership_vertex_ids'] and len(fixtures['FIRST_WEB']['core'])==21
checks['cap37_membership']=fixtures['CAP37']['core']==cap['vertex_ids']
checks['targeted_exact_Human_carry_forward']=read(TARGETED/'TARGETED_HUMAN_APPROVAL_CARRY_FORWARD_AUDIT_R1.json')['status']=='PASS_EXACT_SCOPE_NO_REGRESSION'
oldmatrix=read(HIST/'FULL_STAGE6A_CASE_MATRIX_R1.json')
checks['formal42_14joints']=oldmatrix['formal_count']==42 and len(oldmatrix['cases'])==42 and len({c['bone'] for c in oldmatrix['cases']})==14
checks['historical_axis_sign_angles']=all(c['axis']=='bone_local_X' and c['sign']==-1 and c['angle_deg'] in [15,30,45] and c['applied_rotation_deg']==-c['angle_deg'] for c in oldmatrix['cases'])
current_native=read(CAND.parent/'R2_REOPENED_NATIVE_PAYLOAD_R1.json');checks['frozen_native_weight_hash']=digest(current_native['positive_weight_vectors'])==EXPECTED_WEIGHTS
checks['old9_history_comparator_only']=len(read(HIST/'FULL_STAGE6A_MACHINE_EVIDENCE_R1.json')['blockers'])==9
dump('PREREQUISITE_GATE_R1.json',{'status':'PASS_STATIC_PREREQUISITES_LIVE_REOPEN_PENDING' if all(checks.values()) else 'FAIL_CLOSED','checks':checks,'sources':{'current':ref(CAND),'old_comparator':ref(OLD_CAND),'corrected_rig':ref(CORRECTED),'cap37':ref(CAP_PATH),'fresh_R3':ref(R3_PATH),'matrix':ref(HIST/'FULL_STAGE6A_CASE_MATRIX_R1.json')},'prerequisites':prerequisites,'old_status_role':'HISTORICAL_PRE_DONOR_RESULT_ONLY','current_verdict_basis':'ALL42_FRESH_CURRENT_ASSET_EVALUATIONS','live_weight_and_payload_preflight_required_before_poses':True})
dump('FULL_STAGE6A_POST_DONOR_CASE_MATRIX_R1.json',{**oldmatrix,'scope':'FRESH_FULL42_CURRENT_DERIVATIVE','source':ref(HIST/'FULL_STAGE6A_CASE_MATRIX_R1.json'),'case_id_aliases':{f'RING_MCP_{a}':f'RNG_MCP_{a}' for a in [15,30,45]},'alias_note':'Legacy RNG case IDs preserved exactly. User-facing RING names are aliases, not additional cases.','WRIST_R':'LOCKED_AT_BIND_ZERO','THUMB_CMC_R':'LOCKED_AT_BIND_ZERO'})
assert all(checks.values()),checks
print('FULL42 FROZEN PREREQUISITES PASS; live native check precedes all poses',flush=True)
