import sys
sys.dont_write_bytecode=True
from common import *
import shutil
A=read(OUT/'RUN_A/STATIC_PATH_PAYLOAD.json');B=read(OUT/'RUN_B/STATIC_PATH_PAYLOAD.json')
PA=read(OUT/'RUN_A/POSED_BOUND_PAYLOAD.json');PB=read(OUT/'RUN_B/POSED_BOUND_PAYLOAD.json')
VA=read(OUT/'RUN_A/COMPUTATION_VERIFICATION.json');VB=read(OUT/'RUN_B/COMPUTATION_VERIFICATION.json')
assert A==B and PA==PB
assert VA['static_path_payload_hash']==VB['static_path_payload_hash']==digest(A)
assert VA['bound_payload_hash']==VB['bound_payload_hash']==digest(PA)
assert all(VA['live_prerequisite_checks'].values()) and all(VB['live_prerequisite_checks'].values())
for src,dst in [('STATIC_PATH_PAYLOAD.json','TRUE_CAP_STATIC_PATH_ENSEMBLE_R1.json'),('POSED_BOUND_PAYLOAD.json','TRUE_CAP_POSED_BOUND_RECOMPUTATION_R1.json')]:
 shutil.copyfile(OUT/'RUN_A'/src,OUT/dst)
dump('TRUE_CAP_BOUND_DETERMINISM_VERIFICATION.json',{'status':'PASS_EXACT_VALUE_AND_PAYLOAD_HASH_MATCH','independent_complete_Blender_process_runs':2,'comparison':'Recursive exact equality of every path vertex/edge sequence, endpoint coordinates, edge lengths, bound value and all 120 virtual recipe results. No rounding and no tolerance in A/B comparison.','path_family_equal':A==B,'bound_payload_equal':PA==PB,'path_family_payload_hash':digest(A),'bound_payload_hash':digest(PA),'geometry_context_hash_equal':sha(OUT/'RUN_A/BOUND_GEOMETRY_CONTEXT.json')==sha(OUT/'RUN_B/BOUND_GEOMETRY_CONTEXT.json'),'run_A':ref(OUT/'RUN_A/COMPUTATION_VERIFICATION.json'),'run_B':ref(OUT/'RUN_B/COMPUTATION_VERIFICATION.json'),'input_authority_hashes':VA['input_authority_hashes'],'source_set_hash':VA['source_set_hash'],'target_set_hash':VA['target_set_hash'],'graph_metric_hash':VA['graph_metric_hash'],'tie_rule':A['path_tie_rule'],'path_selection_rounded':False,'max_path_sum_vs_Dijkstra_accumulation_residual_mm':max(abs(p['path_sum_minus_Dijkstra_mm']) for p in A['all_exact_boundary_context_paths']),'residual_interpretation':'Binary64 summation order only; every full path is preserved and denominators are sums of recorded edge lengths. This residual is not an A/B difference.'})
gate=read(OUT/'PREREQUISITE_GATE_R1.json')
gate['status']='PASS'
gate['live_reopen_in_both_independent_runs']='PASS'
gate['live_reopen_checks']=VA['live_prerequisite_checks']
gate['live_reopen_timing']='Performed and asserted before path or pose-bound numeric evaluation in each run.'
dump('PREREQUISITE_GATE_R1.json',gate)
oldpath=read(FEAS/'R1E_CAP_TO_COLLAR_SHORTEST_PATH_AUDIT.json')
oldbounds=read(FEAS/'R1E_STRICT_GEOMETRIC_BOUND_AUDIT.json')
oldsens=read(SENS/'R1E_ENDPOINT_SENSITIVITY_AUDIT.json')
comparison={'historical_numeric_role':'HISTORICAL_VALUE_ONLY; no seed, threshold, expected-answer or acceptance-target use. Fixed-ID old arithmetic remains historical.','historical_shortest_path':{'source_vertex':oldpath['shortest']['cap_vertex'],'target_vertex':oldpath['shortest']['collar_vertex'],'vertex_sequence':oldpath['shortest']['path']['vertex_sequence'],'edge_id_sequence':oldpath['shortest']['path']['edge_id_sequence'],'length_mm':oldpath['shortest']['path']['total_bind_polyline_mm'],'source_authority':'SUPERSEDED_CONTAMINATED_OLD_CAP9','target_authority':'OLD_R3_EXACT_INDEX_COLLAR','current_anatomical_interpretation':'INVALIDATED'},'corrected_shortest_path':A['global_shortest_path'],'historical_pair_count':len(oldpath['all_144_pairs']),'corrected_primary_pair_count':len(A['paths']),'corrected_all_exact_boundary_context_pair_count':len(A['all_exact_boundary_context_paths']),'pose_comparison':{},'downstream_recommendations':{'mesh_limit':'HISTORICAL_ONLY_REQUIRES_SEPARATE_DOWNSTREAM_RECONCILIATION','retopo':'HISTORICAL_ONLY_REQUIRES_SEPARATE_DOWNSTREAM_RECONCILIATION','no_legal_weights':'HISTORICAL_ONLY_REQUIRES_SEPARATE_DOWNSTREAM_RECONCILIATION','cap_constrained_feasibility':'HISTORICAL_ONLY_REQUIRES_SEPARATE_DOWNSTREAM_RECONCILIATION','recommendations_automatically_promoted':False}}
for pose,x in PA['per_pose'].items():
 comparison['pose_comparison'][pose]={'historical_top10_max':oldbounds['per_pose'][pose]['max_STRICT_LOWER_BOUND'],'corrected_top10_max':x['max_over_historical_semantic_top10_current_shortest_pairs']['strict_lower_bound'],'corrected_full703_max':x['max_over_complete_703_pairs']['strict_lower_bound'],'interpretation':'Input-authority replacement comparison, not acceptance testing.'}
comparison['endpoint_sensitivity_comparison']=[{'recipe':{k:x[k] for k in ['family','base_group','added_group','parameter_fraction','pose']},'historical_max_144_index_pairs':old['max_strict_bound_144_index_pairs'],'historical_max_288_all_collar_pairs':old['max_strict_bound_288_all_collar_pairs'],'corrected_max703_index_pairs':x['max_primary_bound_row'][3],'corrected_max1406_all_exact_boundary_context_pairs':x['max_all_exact_boundary_context_bound_row'][3]} for old,x in zip(oldsens['samples'],PA['historical_endpoint_sensitivity_recomputed'])]
dump('TRUE_CAP_HISTORICAL_VS_CORRECTED_COMPARISON.json',comparison)
method=read(OUT/'HISTORICAL_TRUE_CAP_BOUND_METHOD_RECOVERY.json')
coverage=[]
for x in method['dependency_recompute_required_references']:
 name=Path(x['path']).name
 if 'SENSITIVITY' in name or 'ENDPOINT_WEIGHT' in name:
  numeric={'family':'120 historical algebraic endpoint recipes, each 703 primary and 1406 exact-boundary context pairs','output':'TRUE_CAP_POSED_BOUND_RECOMPUTATION_R1.json#historical_endpoint_sensitivity_recomputed'}
 elif 'PATH' in name:
  numeric={'family':'All 703 corrected static source x INDEX-exact-target pairs, all full path records, order statistics and current top10; 1406 full-exact-boundary context records','output':'TRUE_CAP_STATIC_PATH_ENSEMBLE_R1.json'}
 else:
  numeric={'family':'Six historical strict-bound poses, current top10 and all703 actual R2 endpoint bounds, cap37 mean motion and 120 endpoint recipe family where referenced','output':'TRUE_CAP_POSED_BOUND_RECOMPUTATION_R1.json#per_pose'}
 coverage.append({'historical_source':x['path'],'historical_dependency_status':'RECOMPUTE_REQUIRED','corrected_numeric_coverage':numeric,'deformation_counts_and_recommendations':'HISTORICAL_ONLY_NOT_REQUALIFIED_OR_REVIVED'})
assert len(coverage)==len(method['dependency_recompute_required_references'])
dump('RECOMPUTE_REQUIRED_BOUND_CASE_COVERAGE_R1.json',{'status':'ALL_HISTORICAL_NUMERIC_BOUND_FAMILIES_RECOMPUTED','historical_RECOMPUTE_REQUIRED_reference_count':len(coverage),'references':coverage,'actual_pose_case_count':6,'historical_endpoint_recipe_case_count':120,'primary_pair_count_per_case':703,'all_exact_boundary_sensitivity_context_pair_count_per_case':1406,'old_values_copied_into_current_numeric_authority':False,'invalid_OLD_CLAIM_formula':'FORMALLY_REJECTED_NOT_RECOMPUTED_AS_A_BOUND','historical_mesh_limit_no_legal_weights_recommendations':'NOT_AUTOMATICALLY_REVIVED'})
print('EXACT DETERMINISM PASS; method/input replacement coverage',len(coverage),'historical required references; current numeric payloads established.')
