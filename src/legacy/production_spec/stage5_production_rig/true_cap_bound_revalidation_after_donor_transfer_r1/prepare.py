import sys
sys.dont_write_bytecode=True
from common import *
dump('PROTECTED_HISTORY_HASHES_BEFORE.json',inventory())
cap=read(CAP_PATH);r3=read(R3_PATH)
authority=read(OLD/'CORRECTED_TRUE_CAP_SOURCE_TARGET_AUTHORITY.json')
oldstatus=read(OLD/'TRUE_CAP_BOUND_RECOMPUTE_AFTER_DEPENDENCY_RECONCILIATION_R1_STATUS.json')
capcanon=read(CAP_PATH.parent/'CAP_AUTHORITY_CANONICAL_PAYLOAD.json')
skinpath=S5/'static_skin_compatibility_revalidation_after_donor_transfer_r1/STATIC_SKIN_COMPATIBILITY_REVALIDATION_AFTER_DONOR_TRANSFER_R1_STATUS.json'
jointpath=S5/'joint_surface_rest_zero_bind_revalidation_after_donor_transfer_r1/JOINT_SURFACE_REST_ZERO_BIND_REVALIDATION_AFTER_DONOR_TRANSFER_R1_STATUS.json'
oldmanifest=read(OLD/'OUTPUT_ARTIFACT_HASH_MANIFEST.json')
files=['compute_bound.py','common.py','HISTORICAL_TRUE_CAP_BOUND_METHOD_RECOVERY.json','CORRECTED_TRUE_CAP_SOURCE_TARGET_AUTHORITY.json','RUN_A/STATIC_PATH_PAYLOAD.json','RUN_A/POSED_BOUND_PAYLOAD.json','RUN_A/BOUND_GEOMETRY_CONTEXT.json','TRUE_CAP_BOUND_RECOMPUTE_AFTER_DEPENDENCY_RECONCILIATION_R1_STATUS.json']
hashchecks={f:sha(OLD/f)==oldmanifest[f] for f in files}
boundary=sorted({v for e in r3['boundary']['edge_records'] for v in e['vertex_ids']})
targets=sorted(v for v in boundary if r3['membership']['vertex_labels'][str(v)]=='INDEX')
checks={
 'current_derivative_SHA256':sha(CAND)==EXPECTED_CAND,
 'old_R2_SHA256':sha(OLD_CAND)==EXPECTED_OLD,
 'corrected_rig_SHA256':sha(CORRECTED)==EXPECTED_RIG,
 'cap37_HUMAN_APPROVED_FROZEN':cap['status']=='HUMAN_APPROVED_FROZEN' and len(cap['vertex_ids'])==37,
 'cap_combined_authority_hash':cap['combined_authority_hash']==digest(capcanon)==EXPECTED_CAP and capcanon=={k:v for k,v in cap.items() if k!='combined_authority_hash'},
 'R3_HUMAN_APPROVED_FROZEN':r3['status']=='HUMAN_APPROVED_FROZEN',
 'R3_combined_authority_hash':digest(r3)==sha(R3_PATH.parent/'FRESH_R3_OWNERSHIP_AUTHORITY_R1_CANONICAL.json')==EXPECTED_R3,
 'R3_membership_hash':r3['membership']['membership_hash']==sha(R3_PATH.parent/'R3_OWNERSHIP_MEMBERSHIP_CANONICAL.json')==EXPECTED_MEMBER,
 'static_skin_prerequisite':read(skinpath)['VERDICT']=='PASS_STATIC_SKIN_COMPATIBILITY_REQUALIFIED' and read(skinpath)['current_asset']['sha256']==EXPECTED_CAND and read(skinpath)['R2_WEIGHT_HASH']==EXPECTED_WEIGHTS,
 'joint_rest_zero_bind_prerequisite':read(jointpath)['VERDICT']=='PASS_JOINT_REST_ZERO_BIND_REQUALIFIED',
 'historical_corrected_authority_PASS':oldstatus['TRUE_CAP_BOUND_VERDICT']=='PASS_CORRECTED_BOUND_AUTHORITY_ESTABLISHED',
 'historical_graph_metric_hash':oldstatus['graph_metric_hash']==EXPECTED_OLD_GRAPH,
 'historical_files_hash_bound':all(hashchecks.values()),
 'frozen_sources_exact':authority['source']['vertex_ids']==cap['vertex_ids'],
 'primary19_targets_exact':targets==authority['target']['vertex_ids'] and len(targets)==19,
 'context38_targets_exact':boundary==authority['target']['all_exact_boundary_endpoints'] and len(boundary)==38,
 'saved_current_weight_hash':read(S5/'static_skin_compatibility_revalidation_after_donor_transfer_r1/STATIC_SKIN_WEIGHT_PAYLOAD_AUDIT_R1.json')['R2_WEIGHT_VECTOR_HASH']==EXPECTED_WEIGHTS,
}
dump('PREREQUISITE_GATE_R1.json',{'status':'PASS_STATIC_PREREQUISITES_LIVE_REOPEN_PENDING' if all(checks.values()) else 'FAIL_CLOSED_TRUE_CAP_AUTHORITY_MISMATCH','checks':checks,'historical_file_hash_checks':hashchecks,
 'inputs':{k:ref(p) for k,p in {'current':CAND,'old_R2':OLD_CAND,'rig':CORRECTED,'cap37':CAP_PATH,'fresh_R3':R3_PATH,'static_skin':skinpath,'joint_rest_zero_bind':jointpath}.items()}})
assert all(checks.values()),checks
method=read(OLD/'HISTORICAL_TRUE_CAP_BOUND_METHOD_RECOVERY.json')
assert method['HISTORICAL_METHOD_RECOVERED'] and not method['unresolved']
assert len(method['additional_numeric_families']['endpoint_sensitivity']['recipes'])==120
dump('HISTORICAL_TRUE_CAP_BOUND_METHOD_RECOVERY.json',method)
dump('CORRECTED_TRUE_CAP_SOURCE_TARGET_AUTHORITY.json',{**authority,'authority_hashes':{**authority['authority_hashes'],'R2_candidate':EXPECTED_CAND},
 'pre_donor_authority_hashes':authority['authority_hashes'],'current_geometry_asset':ref(CAND),'old_geometry_role':'PRE_DONOR_TRANSFER_CORRECTED_AUTHORITY_HISTORY','post_donor_source_target_membership_rebuilds':0})
request=Path('<USER_HOME>/.codex/attachments/4a5978b2-4d89-41b0-8a64-72397c137af9/已粘贴的文本.txt')
(OUT/'USER_PHASE_SCOPE_ORIGINAL.txt').write_bytes(request.read_bytes())
print('ALL INPUT PREREQUISITES PASS; FROZEN37 / 19 / 38 RESTORED',flush=True)
