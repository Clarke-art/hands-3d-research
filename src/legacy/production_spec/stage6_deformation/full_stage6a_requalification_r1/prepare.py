import sys
sys.dont_write_bytecode=True
from common import *
import re
checks={}
cap=read(CAP_PATH);r3=read(R3_PATH);human=read(HUMAN)
cap_payload=read(CAP_PATH.parent/'CAP_AUTHORITY_CANONICAL_PAYLOAD.json')
checks['cap_frozen37_faces25_hash']=(cap['status']=='HUMAN_APPROVED_FROZEN' and len(cap['vertex_ids'])==37 and len(cap['face_ids'])==25 and cap['combined_authority_hash']==digest(cap_payload)==EXPECTED_CAP)
checks['cap_payload_matches_authority']=cap_payload=={k:v for k,v in cap.items() if k!='combined_authority_hash'}
checks['fresh_R3_frozen_combined']=(r3['status']=='HUMAN_APPROVED_FROZEN' and digest(r3)==sha(R3_PATH.parent/'FRESH_R3_OWNERSHIP_AUTHORITY_R1_CANONICAL.json')==EXPECTED_R3)
checks['fresh_R3_membership']=(r3['membership']['membership_hash']==sha(R3_PATH.parent/'R3_OWNERSHIP_MEMBERSHIP_CANONICAL.json')==EXPECTED_MEMBER)
old=r3['old_cap9']
checks['old9_superseded_native_index']=(old['historical_anatomical_status']=='SUPERSEDED_CONTAMINATED' and old['hard_role_count']==0 and len(old['vertex_ids'])==9 and set(old['fresh_labels'].values())=={'INDEX'})
native=read(S5/'stage5b_r1e_thumb_distal_cap_native_branch_identity_audit_r1/CURRENT_CAP9_NATIVE_BRANCH_CLASSIFICATION.json')
checks['native_old9_9_of_9_INDEX_SURFACE']=native['counts']['INDEX_SURFACE']==9 and native['counts']['UNRESOLVED']==0 and native['current_cap9_vertex_ids']==old['vertex_ids']
checks['corrected_kinematics_applied']=(read(CORRECTED.parent/'THUMB_KINEMATIC_CORRECTION_APPLICATION_RECORD_R1.json')['status']=='HUMAN_APPROVED_APPLIED_VERIFIED' and sha(CORRECTED)==EXPECTED_RIG)
checks['candidate_byte_hash']=sha(CAND)==EXPECTED_CAND
saved=read(CAND.parent/'R2_CANDIDATE_CLEAN_REOPEN_PAYLOAD.json')
checks['saved_weight_vector_hash']=digest(saved['weights'])==EXPECTED_WEIGHTS
checks['human_closure_complete']=(human['active_recovery_status']=='PASS_WITH_HUMAN_REVIEW_COMPLETE' and human['ADDITIONAL_REMEDIATION_REQUIRED']=='NO' and human['ADDITIONAL_SCOPE_EXPANSION_REQUIRED']=='NO' and human['PRODUCTION_DRIFT']==0)
checks['human_closure_sources_unchanged']=all(sha(ROOT/v['path'])==v['sha256'] for v in human['closure_basis'].values())
checks['cap37_preserved_all_THUMB']=cap['vertex_ids']==r3['cap37_preservation']['vertex_ids'] and all(r3['membership']['vertex_labels'][str(v)]=='THUMB' for v in cap['vertex_ids'])
checks['fresh_boundary_authoritative']=r3['boundary']['status']=='DERIVED_FROM_HUMAN_FROZEN_OWNERSHIP_FIELD' and r3['boundary']['edge_count']==20
checks['FIRST_WEB_membership_preserved']=r3['FIRST_WEB21']['membership_vertex_ids']==read(ROOT/r3['FIRST_WEB21']['original_anatomical_membership_reference']['path'])['vertex_ids'] if 'vertex_ids' in read(ROOT/r3['FIRST_WEB21']['original_anatomical_membership_reference']['path']) else sha(ROOT/r3['FIRST_WEB21']['original_anatomical_membership_reference']['path'])==r3['FIRST_WEB21']['original_anatomical_membership_reference']['sha256']
bound_path=S5/'true_cap_bound_recompute_after_dependency_reconciliation_r1/TRUE_CAP_BOUND_RECOMPUTE_AFTER_DEPENDENCY_RECONCILIATION_R1_STATUS.json'
bound=read(bound_path)
checks['corrected_true_cap_numeric_authority']=bound['TRUE_CAP_BOUND_VERDICT']=='PASS_CORRECTED_BOUND_AUTHORITY_ESTABLISHED' and bound['PRODUCTION_DRIFT']==0
dump('PREREQUISITE_GATE_R1.json',{'status':'PASS_STATIC_PREREQUISITES_LIVE_REOPEN_PENDING' if all(checks.values()) else 'FAIL_CLOSED_PREREQUISITE_MISMATCH','checks':checks,'input_authorities':{'cap37':ref(CAP_PATH),'fresh_R3':ref(R3_PATH),'corrected_rig':ref(CORRECTED),'R2_candidate':ref(CAND),'targeted_human_closure':ref(HUMAN)},'native_old9_classification_source':ref(S5/'stage5b_r1e_thumb_distal_cap_native_branch_identity_audit_r1/CURRENT_CAP9_NATIVE_BRANCH_CLASSIFICATION.json'),'no_bound_numbers_computed':True})
assert all(checks.values()),checks
