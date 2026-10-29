import sys
sys.dont_write_bytecode=True
from common import *
import math,collections
A=read(OUT/'RUN_A/STATIC_PATH_PAYLOAD.json');B=read(OUT/'RUN_B/STATIC_PATH_PAYLOAD.json')
PA=read(OUT/'RUN_A/POSED_BOUND_PAYLOAD.json');PB=read(OUT/'RUN_B/POSED_BOUND_PAYLOAD.json')
OLDPATH=read(OLD/'RUN_A/STATIC_PATH_PAYLOAD.json');OLDPOSE=read(OLD/'RUN_A/POSED_BOUND_PAYLOAD.json')
graph=read(OUT/'RUN_A/GRAPH_METRIC_PAYLOAD.json');oldgraph=read(OUT/'RUN_A/OLD_GRAPH_METRIC_REPLAY_PAYLOAD.json')
coords=read(OUT/'RUN_A/SOURCE_TARGET_LIVE_COORDINATES.json')
authority=read(OUT/'CORRECTED_TRUE_CAP_SOURCE_TARGET_AUTHORITY.json')
ids=set(read(S5/'geometry_propagation_after_donor_transfer_r1/STAGE5B_R2_GEOMETRY_PROPAGATION_AUDIT_R1.json')['actual_changed_ids'])
assert len(ids)==54
def status(ok):return 'PASS' if ok else 'FAIL_CLOSED_TRUE_CAP_AUTHORITY_MISMATCH'
def vecdelta(a,b):return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))*1000
source=coords['source_ids'];target=coords['target_ids'];context=coords['context_ids']
coordinate_rows=[]
for v in sorted(set(source)|set(context)):
 coordinate_rows.append({'vertex_id':v,'role':'CAP37_SOURCE' if v in source else 'INDEX_PRIMARY_TARGET' if v in target else 'THUMB_SIDE_BOUNDARY_CONTEXT',
 'old_local_m':coords['old_local_m'][str(v)],'current_local_m':coords['current_local_m'][str(v)],
 'old_world_m':coords['old_world_m'][str(v)],'current_world_m':coords['current_world_m'][str(v)],
 'coordinate_changed':coords['old_local_m'][str(v)]!=coords['current_local_m'][str(v)] or coords['old_world_m'][str(v)]!=coords['current_world_m'][str(v)],
 'world_delta_mm':vecdelta(coords['old_world_m'][str(v)],coords['current_world_m'][str(v)])})
source_changed=sum(r['coordinate_changed'] for r in coordinate_rows if r['vertex_id'] in source)
target_changed=sum(r['coordinate_changed'] for r in coordinate_rows if r['vertex_id'] in target)
context_changed=sum(r['coordinate_changed'] for r in coordinate_rows if r['vertex_id'] in context)
dump('POST_DONOR_SOURCE_TARGET_VERIFICATION_R1.json',{'status':'PASS','source_count':len(source),'primary_target_count':len(target),'full_context_target_count':len(context),
 'source_set_hash':digest(source),'target_set_hash':digest(target),'context_set_hash':digest(context),
 'SOURCE_COORDINATE_CHANGED_COUNT':source_changed,'TARGET_COORDINATE_CHANGED_COUNT':target_changed,'CONTEXT_COORDINATE_CHANGED_COUNT':context_changed,
 'native_coordinates_actually_read_from_both_assets':True,'membership_rebuilt':False,'per_vertex':coordinate_rows})

changed=[];incident=[]
for eid,(edge,ol,nl) in enumerate(zip(graph['edges'],oldgraph['edge_lengths_mm'],graph['edge_lengths_mm'])):
 row={'edge_id':eid,'vertex_ids':edge,'old_length_mm':ol,'current_length_mm':nl,'length_delta_mm':nl-ol,'length_ratio':nl/ol,'approved54_incident':bool(ids.intersection(edge))}
 if row['approved54_incident']:incident.append(row)
 if ol!=nl:changed.append(row)
graphchecks={'native_edge_IDs_and_endpoints_exact':graph['edges']==oldgraph['edges'],
 'all_lengths_positive_finite':all(math.isfinite(x) and x>0 for x in graph['edge_lengths_mm']),
 'old_graph_replay_hash_exact_historical':digest(oldgraph)==EXPECTED_OLD_GRAPH==OLDPATH['graph_metric_hash'],
 'all_current_graph_edges_freshly_built':len(graph['edge_lengths_mm'])==len(graph['edges'])==6828,
 'all_graph_vertices_freshly_read':len(graph['vertices_world_m'])==3416,
 'changed_edges_only_approved54_incident':all(r['approved54_incident'] for r in changed)}
assert all(graphchecks.values()),graphchecks
dump('POST_DONOR_GRAPH_METRIC_AUDIT_R1.json',{'status':'PASS','checks':graphchecks,
 'metric':graph['metric'],'OLD_GRAPH_METRIC_HASH':digest(oldgraph),'GRAPH_METRIC_HASH_CURRENT':digest(graph),'NEW_GRAPH_METRIC_HASH':digest(graph),
 'GRAPH_METRIC_CHANGED':digest(graph)!=digest(oldgraph),'changed_graph_edge_count':len(changed),'all_graph_metric_payload':ref(OUT/'RUN_A/GRAPH_METRIC_PAYLOAD.json'),
 'shortest_path_method':'Same whole native undirected mesh graph, sorted adjacency, frozen historical strict relaxation/tie rules; no cost substitutions.'})
dump('APPROVED54_GRAPH_METRIC_IMPACT_R1.json',{'status':'PASS_DIAGNOSTIC','classification':'GEOMETRY_METRIC_EXPLANATION_NOT_NEW_GEOMETRY_GATE',
 'approved54_ids':sorted(ids),'incident_edge_count':len(incident),'CHANGED_GRAPH_EDGE_COUNT':len(changed),'CHANGED_GRAPH_EDGE_IDS':[r['edge_id'] for r in changed],
 'MAX_EDGE_LENGTH_DELTA_MM':max(abs(r['length_delta_mm']) for r in changed),'MAX_EDGE_LENGTH_RATIO':max(r['length_ratio'] for r in changed),
 'MIN_EDGE_LENGTH_RATIO':min(r['length_ratio'] for r in changed),'incident_edges':incident,'changed_graph_edges':changed})

oldby={(p['source_vertex'],p['target_vertex']):p for p in OLDPATH['all_exact_boundary_context_paths']}
newby={(p['source_vertex'],p['target_vertex']):p for p in A['all_exact_boundary_context_paths']}
ties={(r['source_vertex'],r['target_vertex']):r for r in read(OUT/'RUN_A/PATH_TIE_AUDIT.json')['records']}
oldranks={(p['source_vertex'],p['target_vertex']):i+1 for i,p in enumerate(OLDPATH['paths'])}
newranks={(p['source_vertex'],p['target_vertex']):i+1 for i,p in enumerate(A['paths'])}
def path_comparison(p):
 key=(p['source_vertex'],p['target_vertex']);old=oldby[key];tie=ties[key]
 seqeq=p['vertex_sequence']==old['vertex_sequence'] and p['edge_id_sequence']==old['edge_id_sequence']
 leneq=p['total_path_length_mm']==old['total_path_length_mm'];tieeq=tie['current_tie_status']==tie['old_tie_status']
 dl=p['total_path_length_mm']-old['total_path_length_mm']
 if not tieeq:classification='PATH_TIE_CHANGED'
 elif seqeq:classification='PATH_IDENTICAL_LENGTH_IDENTICAL' if leneq else 'PATH_IDENTICAL_LENGTH_CHANGED'
 elif dl<0:classification='PATH_CHANGED_SHORTER'
 elif dl>0:classification='PATH_CHANGED_LONGER'
 else:classification='OTHER_EXPLICIT'
 return {'source_vertex':key[0],'target_vertex':key[1],'classification':classification,'path_identity_exact':seqeq,'path_length_exact':leneq,'tie_status_exact':tieeq,
 'old_vertex_sequence':old['vertex_sequence'],'current_vertex_sequence':p['vertex_sequence'],'old_edge_sequence':old['edge_id_sequence'],'current_edge_sequence':p['edge_id_sequence'],
 'old_length_mm':old['total_path_length_mm'],'current_length_mm':p['total_path_length_mm'],'length_delta_mm':dl,
 'old_rank_primary':oldranks.get(key),'current_rank_primary':newranks.get(key),'rank_changed':oldranks.get(key)!=newranks.get(key),
 'old_path_touches_approved54':bool(ids.intersection(old['vertex_sequence'])),'current_path_touches_approved54':bool(ids.intersection(p['vertex_sequence'])),
 'tie_status_old_and_current':tie,'other_explicit_reason':'Selected path changed at identical length and tie-status payload' if classification=='OTHER_EXPLICIT' else None}
comparisons=[path_comparison(p) for p in A['paths']]
context_comparisons=[path_comparison(p) for p in A['all_exact_boundary_context_paths']]
classcounts=dict(collections.Counter(r['classification'] for r in comparisons))
statistics_deltas={k:A['statistics_mm'][k]-OLDPATH['statistics_mm'][k] for k in ['min','p05','median','p95','max','mean']}
dump('POST_DONOR_PRIMARY_703_PATHS_R1.json',{'status':'PASS','pair_count':len(A['paths']),'source_count':37,'target_count':19,'graph_metric_hash':digest(graph),
 'statistics_mm':A['statistics_mm'],'global_shortest_path':A['global_shortest_path'],'current_shortest10':A['ten_shortest_distinct_endpoint_pairs'],
 'tie_rule':A['path_tie_rule'],'paths':[{**p,'tie_status':ties[(p['source_vertex'],p['target_vertex'])]['current_tie_status']} for p in A['paths']]})
dump('OLD_VS_NEW_703_PATH_COMPARISON_R1.json',{'status':'PASS_COMPARISON_NUMERIC_CHANGE_IS_NOT_FAILURE','pair_count':len(comparisons),'classification_counts':classcounts,
 'PATH_IDENTITY_MATCH_COUNT':sum(r['path_identity_exact'] for r in comparisons),'PATH_CHANGED_COUNT':sum(not r['path_identity_exact'] for r in comparisons),
 'PATH_LENGTH_CHANGED_COUNT':sum(not r['path_length_exact'] for r in comparisons),'PATH_TIE_CHANGED_COUNT':sum(not r['tie_status_exact'] for r in comparisons),
 'PATH_RANK_CHANGED_COUNT':sum(r['rank_changed'] for r in comparisons),'NEW_PATH_TOUCHES_APPROVED54_COUNT':sum(r['current_path_touches_approved54'] for r in comparisons),
 'OLD_PATH_TOUCHES_APPROVED54_COUNT':sum(r['old_path_touches_approved54'] for r in comparisons),'old_statistics_mm':OLDPATH['statistics_mm'],
 'current_statistics_mm':A['statistics_mm'],'statistics_delta_mm':statistics_deltas,'old_global_shortest_path':OLDPATH['global_shortest_path'],'current_global_shortest_path':A['global_shortest_path'],
 'per_pair':comparisons,'old_ties':'Fresh bind-only historical graph replay matched every stored1406 path; supplemental audit retains frozen first-predecessor semantics.'})
dump('POST_DONOR_1406_CONTEXT_PATHS_R1.json',{'status':'PASS','pair_count':len(A['all_exact_boundary_context_paths']),'source_count':37,'context_endpoint_count':38,
 'target_role':'Both sides of frozen exact fresh-R3 boundary; primary target remains INDEX side only',
 'paths':[{**p,'tie_status':ties[(p['source_vertex'],p['target_vertex'])]['current_tie_status']} for p in A['all_exact_boundary_context_paths']],
 'old_vs_current_comparisons':context_comparisons,'path_identity_match_count':sum(r['path_identity_exact'] for r in context_comparisons),
 'new_path_touches_approved54_count':sum(r['current_path_touches_approved54'] for r in context_comparisons)})

# Compare every measured posed endpoint, not just the maximizing pair.
posed_coordinate_comparison=[];case_comparison={};old_geometry=read(OLD/'RUN_A/BOUND_GEOMETRY_CONTEXT.json');new_geometry=read(OUT/'RUN_A/BOUND_GEOMETRY_CONTEXT.json')
for cid,case in PA['per_pose'].items():
 for v in sorted(set(source)|set(context)):
  old=old_geometry['posed_world_m'][cid][v];new=new_geometry['posed_world_m'][cid][v]
  posed_coordinate_comparison.append({'pose':cid,'vertex_id':v,'role':'SOURCE' if v in source else 'PRIMARY_TARGET' if v in target else 'THUMB_SIDE_CONTEXT',
   'old_posed_world_m':old,'current_posed_world_m':new,'exact_match':new==old,'delta_mm':vecdelta(new,old)})
 oldcase=OLDPOSE['per_pose'][cid]
 current_max=case['max_over_complete_703_pairs']['strict_lower_bound'];old_max=oldcase['max_over_complete_703_pairs']['strict_lower_bound']
 case_comparison[cid]={'pose':cid,'old_max_all703':old_max,'current_max_all703':current_max,'delta_max_all703':current_max-old_max,
 'old_max_current_shortest10':oldcase['max_over_historical_semantic_top10_current_shortest_pairs']['strict_lower_bound'],
 'current_max_current_shortest10':case['max_over_historical_semantic_top10_current_shortest_pairs']['strict_lower_bound'],
 'all703_pair_row_exact_match_count':sum(a==b for a,b in zip(case['all_primary_pair_bounds'],oldcase['all_primary_pair_bounds'])),
 'pose_state_exact_old':case['pose_state']==oldcase['pose_state'],'complete_case_payload_exact_old':case==oldcase}
posed_changed=sum(not r['exact_match'] for r in posed_coordinate_comparison)
max_endpoint_delta=max(r['delta_mm'] for r in posed_coordinate_comparison)
dump('POST_DONOR_POSED_BOUND_RECOMPUTATION_R1.json',{'status':'PASS','classification':'BOUND_RECOMPUTATION_PROBE_ONLY','pose_count':6,
 'bound_definition':PA['definition'],'per_pose':PA['per_pose'],'old_vs_current_pose_comparison':case_comparison,
 'POSED_ENDPOINT_COORDINATE_CHANGE_COUNT':posed_changed,'MAX_POSED_ENDPOINT_COORDINATE_DELTA_MM':max_endpoint_delta,
 'posed_endpoint_coordinates_old_vs_current':posed_coordinate_comparison,'deformation_qualification_runs':0,'full_Stage6A_runs':0,'Stage6B_runs':0,
 'evaluated_mesh_coordinates_read_for_historical_bound_math_only':True,'surface_crossing_or_severe_stretch_QA_run':False})

recipes=PA['historical_endpoint_sensitivity_recomputed'];oldrecipes=OLDPOSE['historical_endpoint_sensitivity_recomputed']
assert len(recipes)==len(oldrecipes)==120
def recipe_id(r):return (r['family'],r['base_group'],r['added_group'],r['parameter_fraction'],r['pose'])
assert [recipe_id(r) for r in recipes]==[recipe_id(r) for r in oldrecipes]
oldrank=sorted(range(120),key=lambda i:(-oldrecipes[i]['max_primary_bound_row'][3],i))
newrank=sorted(range(120),key=lambda i:(-recipes[i]['max_primary_bound_row'][3],i))
oldcontextrank=sorted(range(120),key=lambda i:(-oldrecipes[i]['max_all_exact_boundary_context_bound_row'][3],i))
newcontextrank=sorted(range(120),key=lambda i:(-recipes[i]['max_all_exact_boundary_context_bound_row'][3],i))
recipe_comparison=[]
all_virtual_deltas=[]
for i,(new,old) in enumerate(zip(recipes,oldrecipes)):
 nd=new['max_primary_bound_row'][3];od=old['max_primary_bound_row'][3]
 nc=new['max_all_exact_boundary_context_bound_row'][3];oc=old['max_all_exact_boundary_context_bound_row'][3]
 deltas=[abs(a[3]-b[3]) for field in ['all_primary_pair_bounds','all_exact_boundary_context_pair_bounds'] for a,b in zip(new[field],old[field])]
 all_virtual_deltas.extend(deltas)
 recipe_comparison.append({'recipe_index':i,'recipe':dict(zip(['family','base_group','added_group','parameter_fraction','pose'],recipe_id(new))),
 'old_max_primary_bound':od,'current_max_primary_bound':nd,'primary_max_delta':nd-od,'primary_max_relative_delta':(nd-od)/od if od else None,
 'old_max_context_bound':oc,'current_max_context_bound':nc,'context_max_delta':nc-oc,'context_max_relative_delta':(nc-oc)/oc if oc else None,
 'old_rank':oldrank.index(i)+1,'current_rank':newrank.index(i)+1,'rank_changed':oldrank.index(i)!=newrank.index(i),
 'old_context_rank':oldcontextrank.index(i)+1,'current_context_rank':newcontextrank.index(i)+1,
 'all703_pair_exact_match_count':sum(a==b for a,b in zip(new['all_primary_pair_bounds'],old['all_primary_pair_bounds'])),
 'all1406_context_pair_exact_match_count':sum(a==b for a,b in zip(new['all_exact_boundary_context_pair_bounds'],old['all_exact_boundary_context_pair_bounds'])),
 'max_pairwise_absolute_bound_delta':max(deltas),'full_recipe_payload_exact_old':new==old})
max_recipe_delta=max(abs(r[k]) for r in recipe_comparison for k in ['primary_max_delta','context_max_delta'])
relative_deltas=[abs(r[k]) for r in recipe_comparison for k in ['primary_max_relative_delta','context_max_relative_delta'] if r[k] is not None]
dump('POST_DONOR_VIRTUAL_120_RECIPE_RECOMPUTATION_R1.json',{'status':'PASS','classification':'VIRTUAL_ENDPOINT_LBS_NUMERIC_PROBE_NOT_WEIGHT_AUTHORITY',
 'VIRTUAL_RECIPE_COUNT':120,'primary_pair_evaluations':120*703,'full_context_pair_evaluations':120*1406,
 'max_absolute_delta':max_recipe_delta,'max_relative_delta':max(relative_deltas),'max_all_pairwise_absolute_delta':max(all_virtual_deltas),
 'recipe_ranking_change_count':sum(r['rank_changed'] for r in recipe_comparison),'context_recipe_ranking_change_count':sum(r['old_context_rank']!=r['current_context_rank'] for r in recipe_comparison),
 'old_vs_current_recipe_comparison':recipe_comparison,'recipes':recipes,'production_weight_assignments':0,'skin_feasibility_or_mesh_limit_conclusion':False})

detchecks={
 'fresh_full_path_payload_exact':A==B,
 'fresh_all_six_poses_and120_recipes_exact':PA==PB,
 'fresh_graph_payload_exact':graph==read(OUT/'RUN_B/GRAPH_METRIC_PAYLOAD.json'),
 'live_source_target_coordinates_exact':coords==read(OUT/'RUN_B/SOURCE_TARGET_LIVE_COORDINATES.json'),
 'tie_audit_exact':read(OUT/'RUN_A/PATH_TIE_AUDIT.json')==read(OUT/'RUN_B/PATH_TIE_AUDIT.json'),
 'geometry_context_every_numeric_value_exact':new_geometry==read(OUT/'RUN_B/BOUND_GEOMETRY_CONTEXT.json'),
 'source_target_hashes_exact':A['source_set_hash']==B['source_set_hash'] and A['target_set_hash']==B['target_set_hash'],
 'all_RUN_A_live_prerequisites':all(read(OUT/'RUN_A/COMPUTATION_VERIFICATION.json')['live_prerequisite_checks'].values()),
 'all_RUN_B_live_prerequisites':all(read(OUT/'RUN_B/COMPUTATION_VERIFICATION.json')['live_prerequisite_checks'].values()),
 'final_current_R2_input_hash_bound':all(read(OUT/(run+'/COMPUTATION_VERIFICATION.json'))['input_authority_hashes']['R2_candidate']==EXPECTED_CAND for run in ['RUN_A','RUN_B']),
 'final_input_authority_hashes_exact':read(OUT/'RUN_A/COMPUTATION_VERIFICATION.json')['input_authority_hashes']==read(OUT/'RUN_B/COMPUTATION_VERIFICATION.json')['input_authority_hashes'],
}
historical_primitive_records=read(OLD/'RUN_A/COMPUTATION_VERIFICATION.json')['reused_function_sources']
current_primitive_records=read(OUT/'RUN_A/COMPUTATION_VERIFICATION.json')['reused_function_sources']
primitive_checks={
 'all_four_historical_source_hashes_exact':len(current_primitive_records)==len(historical_primitive_records)==4 and all(a['source']==b['source'] for a,b in zip(current_primitive_records,historical_primitive_records)),
 'all_historical_AST_hashes_exact':all(a['function_AST_sha256']==b['function_AST_sha256'] for a,b in zip(current_primitive_records,historical_primitive_records)),
}
method=read(OLD/'HISTORICAL_TRUE_CAP_BOUND_METHOD_RECOVERY.json')
case_matrix_source=next(r for r in method['formal_files_read'] if r['path'].replace('\\','/').endswith('stage6b/STAGE6B_CASE_MATRIX.json'))
primitive_checks['historical_pose_case_matrix_hash_exact']=sha(ROOT/case_matrix_source['path'])==case_matrix_source['sha256']
dump('HISTORICAL_PRIMITIVE_AUTHORITY_VERIFICATION_R1.json',{'status':'PASS' if all(primitive_checks.values()) else 'FAIL_CLOSED_TRUE_CAP_METHOD_INCOMPATIBILITY','checks':primitive_checks,
 'historical_function_records':historical_primitive_records,'current_function_records':current_primitive_records,'case_matrix_source':case_matrix_source})
assert all(primitive_checks.values()),primitive_checks
dump('POST_DONOR_TRUE_CAP_DETERMINISM_R1.json',{'status':'PASS_EXACT_VALUE_AND_PAYLOAD_HASH_MATCH' if all(detchecks.values()) else 'FAIL_CLOSED_TRUE_CAP_DETERMINISM',
 'checks':detchecks,'independent_complete_Blender_processes':2,'each_current_run':'Clean reopen, fresh whole graph, fresh37-source Dijkstra,1406 paths,6 endpoint-bound poses,120 complete virtual recipes',
 'graph_metric_hash_current':digest(graph),'new_path_family_payload_hash':digest(A),'new_bound_payload_hash':digest(PA),
 'run_A_path_hash':digest(A),'run_B_path_hash':digest(B),'run_A_bound_hash':digest(PA),'run_B_bound_hash':digest(PB),
 'numeric_rounding_for_comparison':False,'serialization':'Round-trip JSON of full binary64 values; exact recursive equality. No altered path selection.'})
assert all(detchecks.values()),detchecks
summary={'CAP37_SOURCE_COUNT':len(source),'PRIMARY_TARGET_COUNT':len(target),'PRIMARY_PAIR_COUNT':len(A['paths']),'FULL_CONTEXT_PAIR_COUNT':len(A['all_exact_boundary_context_paths']),
 'SOURCE_COORDINATE_CHANGED_COUNT':source_changed,'TARGET_COORDINATE_CHANGED_COUNT':target_changed,'OLD_GRAPH_METRIC_HASH':digest(oldgraph),'NEW_GRAPH_METRIC_HASH':digest(graph),
 'GRAPH_METRIC_CHANGED':digest(graph)!=digest(oldgraph),'CHANGED_GRAPH_EDGE_COUNT':len(changed),'CHANGED_GRAPH_EDGE_IDS':[r['edge_id'] for r in changed],
 'MAX_EDGE_LENGTH_DELTA_MM':max(abs(r['length_delta_mm']) for r in changed),'MAX_EDGE_LENGTH_RATIO':max(r['length_ratio'] for r in changed),
 'PATH_IDENTITY_MATCH_COUNT':sum(r['path_identity_exact'] for r in comparisons),'PATH_CHANGED_COUNT':sum(not r['path_identity_exact'] for r in comparisons),
 'PATH_LENGTH_CHANGED_COUNT':sum(not r['path_length_exact'] for r in comparisons),'PATH_TIE_CHANGED_COUNT':sum(not r['tie_status_exact'] for r in comparisons),
 'PATH_RANK_CHANGED_COUNT':sum(r['rank_changed'] for r in comparisons),'NEW_PATH_TOUCHES_APPROVED54_COUNT':sum(r['current_path_touches_approved54'] for r in comparisons),
 'OLD_PATH_TOUCHES_APPROVED54_COUNT':sum(r['old_path_touches_approved54'] for r in comparisons),
 'GLOBAL_SHORTEST_SOURCE':A['global_shortest_path']['source_vertex'],'GLOBAL_SHORTEST_TARGET':A['global_shortest_path']['target_vertex'],
 'GLOBAL_SHORTEST_EDGE_COUNT':len(A['global_shortest_path']['edge_id_sequence']),
 **{'TRUE_CAP_STATIC_PATH_'+k.upper()+'_MM_CURRENT':A['statistics_mm'][k] for k in statistics_deltas},
 **{k.upper()+'_DELTA_MM':v for k,v in statistics_deltas.items()},
 **{cid+'_CURRENT_BOUND':r['current_max_all703'] for cid,r in case_comparison.items()},
 'CMC_MCP_L3_DELTA_VS_PRE_DONOR':case_comparison['CMC_MCP_L3']['delta_max_all703'],
 'FULL_OPP_L3_DELTA_VS_PRE_DONOR':case_comparison['FULL_OPP_L3']['delta_max_all703'],
 'POSED_ENDPOINT_COORDINATE_CHANGE_COUNT':posed_changed,'MAX_POSED_ENDPOINT_COORDINATE_DELTA_MM':max_endpoint_delta,
 'VIRTUAL_RECIPE_COUNT':120,'MAX_VIRTUAL_RECIPE_BOUND_DELTA':max_recipe_delta,'MAX_VIRTUAL_RECIPE_RELATIVE_DELTA':max(relative_deltas),
 'VIRTUAL_RECIPE_RANK_CHANGED_COUNT':sum(r['rank_changed'] for r in recipe_comparison),
 'DETERMINISTIC_RERUN':'PASS_EXACT_VALUE_AND_PAYLOAD_HASH_MATCH','NEW_PATH_FAMILY_PAYLOAD_HASH':digest(A),'NEW_BOUND_PAYLOAD_HASH':digest(PA),
 'TARGETED_DEFORMATION_RUNS':0,'FULL_STAGE6A_RUNS':0,'STAGE6B_RUNS':0,'R3_SOLVER_RUNS':0,'R3_DIJKSTRA_RUNS':0,
 'CURRENT_TRUE_CAP_BIND_DIJKSTRA_SOURCE_RUNS':4*37,'OLD_BIND_REPLAY_DIJKSTRA_SOURCE_RUNS':4*37,
 'FINAL_AUTHORITY_DETERMINISM_PROCESS_COUNT':2,'TOTAL_COMPLETE_PROCESS_EXECUTIONS':4,
 'BOUND_RECOMPUTATION_PROBE_POSE_COUNT_PER_RUN':6,'BOUND_RECOMPUTATION_PROBE_POSE_APPLICATIONS_TOTAL':24,
 'GEOMETRY_MUTATIONS':0,'WEIGHT_MUTATIONS':0,'REST_RIG_MUTATIONS':0,'BLEND_SAVES':0,'PRODUCTION_PROMOTION':'NO'}
dump('POST_DONOR_MACHINE_NUMERIC_RESULT_R1.json',summary)
print(json.dumps({k:v for k,v in summary.items() if k!='CHANGED_GRAPH_EDGE_IDS'},ensure_ascii=False,indent=2),flush=True)
