"""Independent shortest-path replay, arithmetic/coverage and immutable-history verification."""
import sys
sys.dont_write_bytecode=True
from common import *
import heapq
required=[PHASE+'_REPORT.md',PHASE+'_STATUS.json','POST_DONOR_SOURCE_TARGET_VERIFICATION_R1.json','POST_DONOR_GRAPH_METRIC_AUDIT_R1.json',
 'APPROVED54_GRAPH_METRIC_IMPACT_R1.json','POST_DONOR_PRIMARY_703_PATHS_R1.json','OLD_VS_NEW_703_PATH_COMPARISON_R1.json',
 'POST_DONOR_1406_CONTEXT_PATHS_R1.json','POST_DONOR_POSED_BOUND_RECOMPUTATION_R1.json','POST_DONOR_VIRTUAL_120_RECIPE_RECOMPUTATION_R1.json',
 'POST_DONOR_TRUE_CAP_DETERMINISM_R1.json','POST_DONOR_TRUE_CAP_AUTHORITY_MANIFEST_R1.json','PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json']
checks={'all13_required_deliverables_exist':all((OUT/f).is_file() for f in required)}
static=read(OUT/'RUN_A/STATIC_PATH_PAYLOAD.json');graph=read(OUT/'RUN_A/GRAPH_METRIC_PAYLOAD.json')
auth=read(OUT/'CORRECTED_TRUE_CAP_SOURCE_TARGET_AUTHORITY.json');poses=read(OUT/'RUN_A/POSED_BOUND_PAYLOAD.json')
adj=[[] for _ in graph['vertices_world_m']]
for eid,((a,b),length) in enumerate(zip(graph['edges'],graph['edge_lengths_mm'])):adj[a].append((b,length,eid));adj[b].append((a,length,eid))
for row in adj:row.sort()
by_source={}
for p in static['all_exact_boundary_context_paths']:by_source.setdefault(p['source_vertex'],[]).append(p)
matched=0
for source,paths in sorted(by_source.items()):
 dist={source:0.};pred={source:None};queue=[(0.,source)]
 while queue:
  du,u=heapq.heappop(queue)
  if du>dist.get(u,1e18)+1e-15:continue
  for v,w,eid in adj[u]:
   if du+w<dist.get(v,1e18)-1e-16:
    dist[v]=du+w;pred[v]=u;heapq.heappush(queue,(du+w,v))
 for p in paths:
  sequence=[p['target_vertex']]
  while sequence[-1]!=source:sequence.append(pred[sequence[-1]])
  sequence.reverse()
  if sequence==p['vertex_sequence'] and dist[p['target_vertex']]==p['Dijkstra_accumulated_distance_mm'] and sum(graph['edge_lengths_mm'][e] for e in p['edge_id_sequence'])==p['total_path_length_mm']:matched+=1
checks['independent37_source_Dijkstra_all1406_paths_exact']=matched==1406
checks['path_pair_sets_complete']=set((p['source_vertex'],p['target_vertex']) for p in static['paths'])=={(a,b) for a in auth['source']['vertex_ids'] for b in auth['target']['vertex_ids']}
checks['context_pair_sets_complete']=set((p['source_vertex'],p['target_vertex']) for p in static['all_exact_boundary_context_paths'])=={(a,b) for a in auth['source']['vertex_ids'] for b in auth['target']['all_exact_boundary_endpoints']}
pathlength={(p['source_vertex'],p['target_vertex']):p['total_path_length_mm'] for p in static['all_exact_boundary_context_paths']}
bound_rows=0
for case in poses['per_pose'].values():
 rows=case['all_primary_pair_bounds']
 for r in rows:
  assert r['bind_path_length_mm']==pathlength[(r['source_vertex'],r['target_vertex'])]
  assert r['strict_lower_bound']==r['posed_endpoint_separation_mm']/r['bind_path_length_mm'];bound_rows+=1
 assert max(r['strict_lower_bound'] for r in rows)==case['max_over_complete_703_pairs']['strict_lower_bound']
virtual_rows=0
for recipe in poses['historical_endpoint_sensitivity_recomputed']:
 assert len(recipe['all_primary_pair_bounds'])==703 and len(recipe['all_exact_boundary_context_pair_bounds'])==1406
 for field in ['all_primary_pair_bounds','all_exact_boundary_context_pair_bounds']:
  for a,b,d,ratio in recipe[field]:assert ratio==d/pathlength[(a,b)];virtual_rows+=1
 assert max(r[3] for r in recipe['all_primary_pair_bounds'])==recipe['max_primary_bound_row'][3]
 assert max(r[3] for r in recipe['all_exact_boundary_context_pair_bounds'])==recipe['max_all_exact_boundary_context_bound_row'][3]
checks['all4218_actual_bound_ratios_and_maxima_verified']=bound_rows==6*703
checks['all253080_virtual_ratios_and_maxima_verified']=virtual_rows==120*(703+1406)
checks['all_six_actual_poses_complete']=set(poses['per_pose'])=={'TH_IP_30','TH_IP_45','TH_MCP_45','CMC_OPP_30','CMC_MCP_L3','FULL_OPP_L3'}
checks['all120_recipes_complete']=len(poses['historical_endpoint_sensitivity_recomputed'])==120
checks['final_current_intake_hash']=auth['authority_hashes']['R2_candidate']==EXPECTED_CAND and auth['pre_donor_authority_hashes']['R2_candidate']==EXPECTED_OLD
authority=read(OUT/'POST_DONOR_TRUE_CAP_AUTHORITY_MANIFEST_R1.json');combined=authority.pop('combined_numeric_authority_hash')
checks['numeric_authority_combined_hash_exact']=combined==digest(authority)
checks['numeric_payload_hashes_exact']=authority['graph_metric_hash_current']==digest(graph) and authority['path_family_payload_hash_current']==digest(static) and authority['bound_payload_hash_current']==digest(poses)
checks['all_current_authority_references_exact']=all(sha(ROOT/r['path'])==r['sha256'] for r in authority['current_numeric_references'].values())
checks['A_B_exact']=static==read(OUT/'RUN_B/STATIC_PATH_PAYLOAD.json') and poses==read(OUT/'RUN_B/POSED_BOUND_PAYLOAD.json')
before=read(OUT/'PROTECTED_HISTORY_HASHES_BEFORE.json');after=inventory()
checks['all_preexisting_files_immutable']=before==after
checks['input_blend_hashes_retained']=sha(CAND)==EXPECTED_CAND and sha(OLD_CAND)==EXPECTED_OLD and sha(CORRECTED)==EXPECTED_RIG
s=read(OUT/(PHASE+'_STATUS.json'))
checks['PASS_and_STOP_current_authority_only']=s['VERDICT']=='PASS_CURRENT_GEOMETRY_BOUND_AUTHORITY_ESTABLISHED' and s['STOP'] and not s['NEXT_EXECUTED']
checks['no_deformation_qualification_or_Stage6_runs']=all(s[k]==0 for k in ['TARGETED_DEFORMATION_RUNS','FULL_STAGE6A_RUNS','STAGE6B_RUNS','R3_SOLVER_RUNS','R3_DIJKSTRA_RUNS','BLEND_SAVES','WEIGHT_MUTATIONS','GEOMETRY_MUTATIONS','REST_RIG_MUTATIONS'])
checks['required_JSON_audits_PASS']=all(read(OUT/f).get('status','').startswith('PASS') for f in required if f.endswith('.json') and f!=PHASE+'_STATUS.json')
manifest=read(OUT/'OUTPUT_EVIDENCE_HASH_MANIFEST_R1.json')
checks['delivery_manifest_exact_and_complete']=digest(manifest['files'])==manifest['canonical_files_hash'] and all(sha(OUT/f)==h for f,h in manifest['files'].items()) and set(manifest['files'])=={p.relative_to(OUT).as_posix() for p in OUT.rglob('*') if p.is_file() and p.name not in manifest['excludes']}
output={'status':'PASS' if all(checks.values()) else 'FAIL_CLOSED_DELIVERY_VALIDATION','checks':checks,'required_deliverables':required,
 'independently_replayed_shortest_paths':matched,'actual_bound_ratios_checked':bound_rows,'virtual_bound_ratios_checked':virtual_rows,'protected_preexisting_file_count':len(before),'STOP':True}
dump('FINAL_DELIVERY_VALIDATION_R1.json',output)
print(json.dumps(output,ensure_ascii=False,indent=2),flush=True)
assert all(checks.values()),output
