import sys
sys.dont_write_bytecode=True
from common import *
import re
required=[PHASE+'_REPORT.md',PHASE+'_STATUS.json','PALMAR_STATIC_SKIN_INPUT_HASH_AUDIT_R1.json','PALMAR_STATIC_SKIN_WEIGHT_PAYLOAD_AUDIT_R1.json','PALMAR_STATIC_SKIN_FULL_MESH_MATH_AUDIT_R1.json','PALMAR_STATIC_SKIN_CONTINUITY_EDGE_REVALIDATION_R1.json','PALMAR_STATIC_SKIN_PRE_POST_METRIC_EQUIVALENCE_R1.json','PALMAR_STATIC_SKIN_CAP37_R1.json','PALMAR_STATIC_SKIN_OLDCAP9_R1.json','PALMAR_STATIC_SKIN_FIRSTWEB_R1.json','PALMAR_STATIC_SKIN_R3_GUARD_R1.json','PALMAR_STATIC_SKIN_EDGE5879_R1.json','PALMAR_STATIC_SKIN_INHERITED16_R1.json','PALMAR16_AUTHORITY_INTERSECTION_R1.json','PALMAR16_STATIC_EDGE_COMPATIBILITY_R1.json','PALMAR16_GEOMETRY_DRIVER_DIAGNOSTIC_R1.json','NORMAL69_STATIC_SKIN_PROTECTION_R1.json','DORSAL54_STATIC_SKIN_REGRESSION_R1.json','CURRENT9_HOLD_RECHECK_R1.json','PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json','review.html']
assert all((OUT/n).is_file() for n in required)
status=read(OUT/(PHASE+'_STATUS.json'));assert status['VERDICT']=='PASS_STATIC_SKIN_COMPATIBILITY_REQUALIFIED' and status['STOP'] and not status['NEXT_EXECUTED']
assert all(sha(p)==EXPECTED[k] for k,p in FILES.items())
N=read(OUT/'CURRENT_CLEAN_REOPEN_NATIVE_PAYLOAD_R1.json');O=read(OUT/'OLD_R2_CLEAN_REOPEN_NATIVE_PAYLOAD_R1.json')
assert len(N['positive_weight_vectors'])==len(N['dense_float32_rows'])==3416
assert digest(N['positive_weight_vectors'])==digest(O['positive_weight_vectors'])==WEIGHT_HASH
assert N['protected']==O['protected'] and N['group_order']==O['group_order'] and N['dense_float32_rows']==O['dense_float32_rows']
math_audit=read(OUT/'PALMAR_STATIC_SKIN_FULL_MESH_MATH_AUDIT_R1.json');assert len(math_audit['per_vertex'])==3416 and not any(math_audit['violation_counts'].values())
assert math_audit['canonical_zero_epsilon']==0 and len(math_audit['cleanup55'])==55 and all(r['all_exact_zero'] and r['payload_exact_old_R2'] for r in math_audit['cleanup55'])
cont=read(OUT/'PALMAR_STATIC_SKIN_CONTINUITY_EDGE_REVALIDATION_R1.json');pre=read(PRE/'STATIC_SKIN_CONTINUITY_EDGE_REVALIDATION_R1.json');eq=read(OUT/'PALMAR_STATIC_SKIN_PRE_POST_METRIC_EQUIVALENCE_R1.json')
assert cont['all_checked_edges']==pre['all_checked_edges'] and len(cont['all_checked_edges'])==2127
assert cont['all_exceedances']==pre['all_exceedances'] and len(cont['all_exceedances'])==16
assert eq['EDGE_METRIC_EXACT_MATCH_COUNT']==2127 and all(r['metric_exact_old_R2'] and r['endpoints_exact_old_R2'] for r in eq['per_edge'])
assert eq['MAX_LINF_DELTA_VS_OLD_R2']==eq['MAX_L1_DELTA_VS_OLD_R2']==0
assert [r['edge_id'] for r in cont['all_exceedances']]==[1130,1137,1171,1172,1174,1176,1555,4417,4421,4425,4427,4428,4431,4474,4881,5474]
assert all(r['classification']=='INHERITED_COPY_ONLY_STATIC_QUALIFICATION_DEBT' and not r['resolved'] for r in cont['all_exceedances'])
contract=read(OUT/'PALMAR_STATIC_SKIN_CONTRACT_RECOVERY_R1.json');assert all(contract['checks'].values()) and contract['normalization_tolerance']==1e-5 and contract['canonical_zero_epsilon']==0
assert cont['limits']=={'L_inf':.5,'L1':1} and cont['semantics']=='SCOPED_ABSOLUTE_SCREEN_PLUS_NO_REGRESSION_WITH_EXPLICIT_QUALIFICATION'
for r in contract['sources']:assert sha(r['path'])==r['sha256']
for name,count in [('PALMAR_STATIC_SKIN_CAP37_R1.json',37),('PALMAR_STATIC_SKIN_OLDCAP9_R1.json',9),('PALMAR_STATIC_SKIN_FIRSTWEB_R1.json',21)]:
 r=read(OUT/name);assert r['status']=='PASS' and len(r['per_vertex'])==count and r['vectors_exact_old_R2']
assert read(OUT/'PALMAR_STATIC_SKIN_R3_GUARD_R1.json')['status']=='PASS'
edge=read(OUT/'PALMAR_STATIC_SKIN_EDGE5879_R1.json');assert edge['status']=='PASS' and edge['exact_old_R2_metric']
assert status['EDGE5879_LINF']==.06026959419250488 and status['EDGE5879_L1']==.16152597963809967
local=read(OUT/'PALMAR16_STATIC_EDGE_COMPATIBILITY_R1.json');assert len(local['incident_edges'])==48 and len(local['all_context_edges'])==112
assert all(r['metric_exact_match'] and r['endpoint_sparse_entries_exact'] for r in local['all_context_edges'])
diag=read(OUT/'PALMAR16_GEOMETRY_DRIVER_DIAGNOSTIC_R1.json');assert len(diag['per_vertex'])==16 and all(len(r['all16_deform_driver_distance_relations'])==16 for r in diag['per_vertex'])
assert all(diag['geometry_context_checks'].values()) and all(diag['rig_checks'].values()) and not diag['explicit_static_incompatibilities'] and diag['new_thresholds']==0 and diag['pose_runs']==0
for name,count in [('NORMAL69_STATIC_SKIN_PROTECTION_R1.json',69),('DORSAL54_STATIC_SKIN_REGRESSION_R1.json',54)]:
 r=read(OUT/name);assert r['status']=='PASS' and r['native_vertex_count']==count and r['all_edge_metrics_exact']
assert status['CURRENT9_HUMAN_RESPONSE']=='HOLD_NOT_CLOSED'
assert status['MID_MCP_45_MANDATORY_REVALIDATION']==status['WHOLE_HAND_SURFACE_INTEGRITY_BASELINE_REQUIRED']=='YES'
assert all(status[k]==0 for k in ('WEIGHT_WRITE_COUNT','GROUP_WRITE_COUNT','SKIN_SOLVER_RUN_COUNT','SCOPE_EXPANSION_COUNT','ALL_POSE_RUNS','NONZERO_POSE_RUNS','TARGETED_DEFORMATION_RUNS','FULL42_RUNS','STAGE6B_RUNS'))
protected=read(OUT/'PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json');assert protected['status']=='PASS' and protected['PROTECTED_HISTORY_DRIFT']==0 and not protected['history_modified_or_deleted_paths'] and not protected['new_paths_outside_this_phase']
for r in read(OUT/'STATIC_VALIDATOR_FUNCTION_REUSE_R1.json')['records']:assert sha(r['source']['path'])==r['source']['sha256'] and not r['top_level_code_executed']
assert not list(OUT.glob('*.blend*'))
for target in re.findall(r'href="([^"]+)"',(OUT/'review.html').read_text(encoding='utf-8')):assert (OUT/target).is_file(),target
report=(OUT/(PHASE+'_REPORT.md')).read_text(encoding='utf-8');assert all(k in report for k in status)
dump('DELIVERY_VERIFICATION_R1.json',{'status':'PASS','required_outputs_count':20,'review_html_additional':True,'required_artifacts':{n:ref(OUT/n) for n in required},'all3416_vectors_checked':True,'all2127_edges_complete_record_exact':True,'all16_debts_preserved':True,'palmar_local48_and_context112_edges_exact':True,'no_solver_pose_or_weight_writes':True,'STOP':True,'NEXT_EXECUTED':False})
dump('OUTPUT_ARTIFACT_HASH_MANIFEST_R1.json',{p.relative_to(OUT).as_posix():sha(p) for p in OUT.rglob('*') if p.is_file() and p.name!='OUTPUT_ARTIFACT_HASH_MANIFEST_R1.json'})
print('DELIVERY PASS: required20 outputs + review;3416 weights /2127 edges /16 debts preserved;STOP')
