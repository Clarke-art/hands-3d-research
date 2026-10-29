from common import *
assert not CANDIDATE.exists(),'FAIL_CLOSED: candidate already exists; never overwrite'
assert not (OUT/'FROZEN_HASHES_BEFORE.json').exists(),'Refuse to replace protected baseline'
B=read(PROPOSAL/'SKIN_AUTHORITY_PROPOSAL_BUNDLE_R1.json');A=read(RESPONSE)
expected={'review_id':'SKIN_AUTHORITY_RECONCILIATION_HUMAN_REVIEW_R1','phase':'HUMAN_SKIN_AUTHORITY_RECONCILIATION_APPROVAL',
 'proposal_bundle_hash':'a0a3811f00984edce73db6ff4171d72aeaec07e27dbe17936266dec6d9da1340',
 'R3_authority_hash':'361f4f25201f5810830dc1bfc4bd2cf19db908aef8945801a63bfd2829197ff0',
 'R3_membership_hash':'f57483723e90cc34e0551bf70fac00c7c8cb789dbad5d0e248018fdaddd3741d',
 'corrected_rig_sha256':'5d5f86bb59135715a77515468c2b76fe81e2a44e2e8c5d6c17fcc3d56d2147fe',
 'technical_verdict':'DETERMINISTIC_PROPOSAL_READY_FOR_HUMAN_REVIEW',
 'accepted_as_skin_authority_rebuild_plan':True,'skin_rebuild_candidate_approved':True,
 'authorized_next_phase':PHASE,'authority_scope':'DETERMINISTIC_SKIN_DRIVER_AND_WEIGHT_REBUILD_PLAN_ONLY',
 'candidate_static_pass':False,'candidate_deformation_pass':False,'Stage6_approved':False,'production_promotion_approved':False,
 'validation_mode':False,'automatic_apply':False,'all_questions_answered':True,
 'response_kind':'HUMAN_SKIN_AUTHORITY_RECONCILIATION_RESPONSE','automatic_solver_execution':False,'applies_production_changes':False}
for q in ['Q1_cap37_driver_semantics','Q2_old_cap9_INDEX_reconstruction','Q3_FIRST_WEB_shared_wrapper',
 'Q4_safe_reuse_and_rebuild_envelope','Q5_edge5879_targeted_scope','Q6_ownership_as_side_guard','Q7_approve_targeted_candidate_rebuild']:expected[q]='YES'
for k,v in expected.items():assert type(A.get(k)) is type(v) and A[k]==v,('FAIL_CLOSED Human response',k)
assert digest(B)==expected['proposal_bundle_hash']==sha(PROPOSAL/'SKIN_AUTHORITY_PROPOSAL_BUNDLE_R1_CANONICAL.json')
assert B['R3_authority_hash']==expected['R3_authority_hash'] and B['corrected_rig_sha256']==expected['corrected_rig_sha256']
for f,h in B['proposal_files'].items():assert sha(PROPOSAL/f)==h,('FAIL_CLOSED proposal file drift',f)
R3=read(ROOT/'audits/human_r3_fresh_result_authority_freeze_r1/FRESH_R3_OWNERSHIP_AUTHORITY_R1.json')
assert digest(R3)==expected['R3_authority_hash'] and R3['status']=='HUMAN_APPROVED_FROZEN'
assert sha(ROOT/'audits/human_r3_fresh_result_authority_freeze_r1/R3_OWNERSHIP_MEMBERSHIP_CANONICAL.json')==expected['R3_membership_hash']
assert sha(CORRECTED)==expected['corrected_rig_sha256']
stage4=read(ROOT/'production_spec/stage4_blender/stage4c_r2/STAGE4C_R2_HUMAN_APPROVAL_FREEZE.json')
assert sha(STAGE4)==stage4['approved_master']['APPROVED_MASTER_SHA256']
reuse=read(PROPOSAL/'R1B_SAFE_WEIGHT_REUSE_SET_R1.json');assert sha(DONOR)==reuse['baseline_source']['sha256']
sets=[set(reuse[k]) for k in ['SAFE_REUSE','TARGETED_REVALIDATION','REBUILD_REQUIRED']]
assert list(map(len,sets))==[2401,771,244] and set.union(*sets)==set(range(3416))
assert sum(map(len,sets))==len(set.union(*sets))
cap=read(PROPOSAL/'CAP37_SKIN_DRIVER_AUTHORITY_R1.json');web=read(PROPOSAL/'FIRST_WEB_SKIN_WEIGHT_WRAPPER_R2.json')
old=read(PROPOSAL/'OLD_CAP9_SKIN_CORRECTION_AUTHORITY_R1.json');edge=read(PROPOSAL/'EDGE5879_REBUILD_SCOPE_R1.json')
assert set(r['vertex_id'] for r in cap['per_vertex_surface_evidence'])<=sets[2]
assert set(old['vertex_ids'])<=sets[2] and set(edge['endpoints'])<=sets[2]
assert len(set(web['membership']['vertex_ids'])&sets[2])==1
dump('FROZEN_HASHES_BEFORE.json',inventory())
(OUT/'HUMAN_APPROVAL_RESPONSE_SOURCE_COPY.json').write_bytes(RESPONSE.read_bytes())
dump('APPROVAL_AND_INPUT_HASH_VERIFICATION_R1.json',{'status':'PASS','phase':PHASE,
 'Human_response_verified':True,'response_source':str(RESPONSE),'response_sha256':sha(RESPONSE),
 'notes':A['notes'],'proposal_bundle_hash_verified':True,'proposal_bundle_hash':digest(B),
 'R3_authority_hash_verified':True,'R3_authority_hash':digest(R3),'R3_membership_hash_verified':True,
 'corrected_rig_hash_verified':True,'corrected_rig_sha256':sha(CORRECTED),'Stage4C_geometry_source_sha256':sha(STAGE4),
 'R1B_donor_sha256':sha(DONOR),'proposal_component_hashes':B['proposal_files'],
 'approval_scope':'New targeted candidate only; historical files immutable; no Stage6, no pose tuning, no production promotion'})
dump('AUTHORIZED_WEIGHT_WRITE_SET_R1.json',{'phase':PHASE,'source':str(PROPOSAL/'R1B_SAFE_WEIGHT_REUSE_SET_R1.json'),
 'source_sha256':sha(PROPOSAL/'R1B_SAFE_WEIGHT_REUSE_SET_R1.json'),'approval_response_sha256':sha(RESPONSE),
 'SAFE_REUSE':sorted(sets[0]),'TARGETED_REVALIDATION':sorted(sets[1]),'REBUILD_REQUIRED':sorted(sets[2]),
 'expected_counts':[2401,771,244],'WEIGHT_WRITE_ALLOWED_ONLY':sorted(sets[2]),
 'complete_and_disjoint':True,'FIRST_WEB_write_ids':sorted(set(web['membership']['vertex_ids'])&sets[2]),
 'EDGE5879_write_ids':sorted(set(edge['neighborhood_ids'])&sets[2]),
 'EDGE5879_copy_only_ids':sorted(set(edge['neighborhood_ids'])-sets[2]),
 'constraint_resolution':'Hash-bound 244 set controls write permission. Remaining approved transition-neighborhood vertices are copied exactly and tested/flagged only.'})
print('APPROVAL / ALL BOUND INPUTS PASS; partitions 2401 + 771 + 244 = 3416')
