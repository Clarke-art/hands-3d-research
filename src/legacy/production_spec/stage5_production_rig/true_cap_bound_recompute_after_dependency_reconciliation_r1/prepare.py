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
dump('PREREQUISITE_GATE_R1.json',{'status':'PASS_STATIC_PREREQUISITES_LIVE_REOPEN_PENDING' if all(checks.values()) else 'FAIL_CLOSED_PREREQUISITE_MISMATCH','checks':checks,'input_authorities':{'cap37':ref(CAP_PATH),'fresh_R3':ref(R3_PATH),'corrected_rig':ref(CORRECTED),'R2_candidate':ref(CAND),'targeted_human_closure':ref(HUMAN)},'native_old9_classification_source':ref(S5/'stage5b_r1e_thumb_distal_cap_native_branch_identity_audit_r1/CURRENT_CAP9_NATIVE_BRANCH_CLASSIFICATION.json'),'no_bound_numbers_computed':True})
assert all(checks.values()),checks
labels=r3['membership']['vertex_labels']
c0=sorted({v for edge in r3['boundary']['edge_records'] for v in edge['vertex_ids']})
index=sorted(v for v in c0 if labels[str(v)]=='INDEX')
thumb=sorted(v for v in c0 if labels[str(v)]=='THUMB')
assert len(index)>0 and not(set(cap['vertex_ids'])&set(c0))
dump('CORRECTED_TRUE_CAP_SOURCE_TARGET_AUTHORITY.json',{
 'source':{'authority':'THUMB_DISTAL_CAP_CANONICAL_AUTHORITY_R1','classification':'DERIVED_FROM_FROZEN_CAP37','vertex_ids':cap['vertex_ids'],'face_ids':cap['face_ids'],'source_count':len(cap['vertex_ids']),'source_set_hash':digest(cap['vertex_ids']),'mathematical_object':'Complete frozen cap surface vertex endpoint set, not representative/centroid/extreme vertex.','old_cap9_source_authority_count':0,'legacy_REP_source_authority_count':0},
 'target':{'authority':'FRESH_R3_OWNERSHIP_AUTHORITY_R1','historical_role':'INDEX side endpoints of exact ownership boundary edges','vertex_ids':index,'target_count':len(index),'target_set_hash':digest(index),'classification':'DERIVED_FROM_FROZEN_EXACT_BOUNDARY','exact_boundary_edge_ids':r3['boundary']['edge_ids'],'exact_boundary_edge_records':r3['boundary']['edge_records'],'all_exact_boundary_endpoints':c0,'thumb_side_exact_endpoints':thumb,'all_collar_context_set_hash':digest(c0)},
 'semantic_role_separation':{'exact_boundary':'20 frozen crossing edges; targets are only their INDEX endpoints.','collar_transition_band':'Existing targeted fixture neighborhood is descriptive continuity context only; not added to primary target set.','proximal_semantic_stop':r3['proximal_boundary_authority'],'proximal_stop_is_target_anatomy_map':False,'first_web':r3['FIRST_WEB21']['membership_vertex_ids'],'first_web_is_extra_target_set':False,'full_collar_sensitivity_context':'Historical sensitivity method also covers both sides of exact boundary; kept as a separate context family.'},
 'authority_hashes':{'cap37_combined':EXPECTED_CAP,'R3_membership':EXPECTED_MEMBER,'R3_combined':EXPECTED_R3,'corrected_rig':EXPECTED_RIG,'R2_candidate':EXPECTED_CAND,'weight_vector':EXPECTED_WEIGHTS},
 'R3_solver_runs':0,'R3_Dijkstra_runs':0,'R3_mincut_runs':0,'R3_closure_runs':0,'new_anatomical_authority':False})
dependency=read(DEP/'STRICT_BOUND_DEPENDENCY_INVALIDATION_AUDIT.json')
paths={ROOT/x['path'] for x in dependency['references']}
paths.update([FEAS/'scripts/feas_audit.py',FEAS/'scripts/feas_render.py',SENS/'scripts/review_analyze.py',S5/'stage5b_r1e/scripts/s5b_r1e_prequal.py',S5/'stage5b_r1e/scripts/s5b_r1e_common.py',S6/'stage6b/STAGE6B_CASE_MATRIX.json'])
# Read all workspace implementations/reports directly mentioning these methods;
# hash inventories and coordinate dumps are not method implementations.
pattern=re.compile(r'strict[_ -]?(?:lower[_ -]?)?bound|true[_ -]?cap.{0,30}bound|cap[_ -]?(?:to|→)[_ -]?collar|no[_ -]?legal[_ -]?weight|13\.1646|5\.9643|6\.5160',re.I)
for folder in [ROOT/'production_spec',ROOT/'audits',ROOT/'docs']:
 for p in folder.rglob('*'):
  if not p.is_file() or OUT in p.parents or p.suffix.lower() not in ['.py','.md','.json']:continue
  if any(t in p.name.upper() for t in ['HASH','PROTECTED_STATE','COORDINATE','_RAW','_PAYLOAD']):continue
  text=p.read_text(encoding='utf-8-sig')
  if pattern.search(text):paths.add(p)
formal=[]
for p in sorted(paths):
 text=p.read_text(encoding='utf-8-sig')
 hits=[{'line':i,'text':line[:800]} for i,line in enumerate(text.splitlines(),1) if pattern.search(line)]
 role='METHOD_REUSABLE' if p in [FEAS/'scripts/feas_audit.py',SENS/'scripts/review_analyze.py'] else 'HISTORICAL_VALUE_ONLY'
 formal.append({**ref(p),'classification':role,'direct_relevant_excerpts':hits,'entire_content_read':True})
strict=read(FEAS/'R1E_STRICT_GEOMETRIC_BOUND_AUDIT.json')
poses=list(strict['per_pose'])
assert set(poses)=={'TH_IP_30','TH_IP_45','TH_MCP_45','CMC_OPP_30','CMC_MCP_L3','FULL_OPP_L3'}
samples=read(SENS/'R1E_ENDPOINT_SENSITIVITY_AUDIT.json')['samples']
recipes=[{k:x[k] for k in ['family','base_group','added_group','parameter_fraction','pose']} for x in samples]
dump('HISTORICAL_TRUE_CAP_BOUND_METHOD_RECOVERY.json',{
 'HISTORICAL_METHOD_RECOVERED':True,'recovery_complete_before_numeric_computation':True,
 'mathematical_definition':'max_i(posed_edge_length_i / bind_edge_length_i) >= norm(B_pose-A_pose) / sum(bind_edge_lengths_on_fixed_path)',
 'source_object':'Every frozen cap vertex individually; no REP/centroid construction needed.',
 'target_object':'INDEX-owned endpoints of exact boundary edges; additional all-boundary endpoints only for separately labeled historical sensitivity context.',
 'mesh_graph':'All saved mesh vertices and native undirected mesh edges, no ownership-cut graph restriction.',
 'edge_metric':'Euclidean length of each actual bind-space mesh edge in world mm; not endpoint chord distance.',
 'path_space':'BIND mesh; paths retained for posed endpoint ratios; no posed shortest-path recomputation.',
 'pose_evaluation':'Existing exact pose primitives and case matrix on current corrected R2; both posed endpoint positions used.',
 'primary_bound_aggregation':'Historical feasibility used max over the 10 shortest distinct pairs. Preserve that summary and also report full current ensemble maximum separately.',
 'statistics_rule':'Historical order statistics: p05 index floor(.05*(n-1)); median index floor(n/2); p95 floor(.95*(n-1)); no interpolated percentiles.',
 'classifications':[
 {'component':'Triangle inequality and fixed path denominator','classification':'METHOD_REUSABLE'},
 {'component':'Actual mesh-edge bind metric and complete source x target enumeration','classification':'METHOD_REUSABLE'},
 {'component':'Historical cap9/old REP/legacy proxy source authority','classification':'INPUT_INVALIDATED_RECOMPUTE','replacement':'Complete frozen cap37 vertex set'},
 {'component':'Old R3 exact boundary endpoints and side labels','classification':'INPUT_INVALIDATED_RECOMPUTE','replacement':'Frozen fresh20 exact boundary endpoint labels; preserve INDEX-side role'},
 {'component':'Old R2A/REP-derived rig transforms and R1E endpoint vectors','classification':'INPUT_INVALIDATED_RECOMPUTE','replacement':'Current corrected rig and actual R2 evaluated endpoints'},
 {'component':'Old global ownership labels, cut-sheet and thumb-arc tissue interpretation','classification':'SEMANTIC_INVALIDATED_RECOMPUTE','replacement':'Bounded fresh labels with UNASSIGNED outside; corrected chain proxies are descriptive only, no new tissue authority'},
 {'component':'(|uA|+Lbind)/Lbind expression','classification':'SEMANTIC_INVALIDATED_RECOMPUTE','replacement':'Rejected as lower bound; not used for current numeric authority'},
 {'component':'13.1646 mm / 5.9643 / 6.5160 and old numeric payloads','classification':'HISTORICAL_VALUE_ONLY'},
 {'component':'mesh-limit / retopo / no-legal-weight recommendations','classification':'HISTORICAL_VALUE_ONLY','automatic_revival':False},
 {'component':'Historical algebraic sensitivity families','classification':'METHOD_REUSABLE','role':'Virtual endpoint LBS probes only; not weight assignments or authority'}
 ],
 'unresolved':[],'formal_files_read':formal,
 'dependency_recompute_required_references':[x for x in dependency['references'] if 'RECOMPUTE_REQUIRED' in x['scope_classifications']],
 'bound_pose_ids':poses,'additional_numeric_families':{'six_pose_motion_decomposition':'Recompute cap37 mean displacement and top10/full endpoint bounds; deformation counts/recommendations remain historical.','endpoint_sensitivity':{'sample_count':len(recipes),'recipes':recipes,'full_index_and_all_exact_boundary_pair_sets':True,'virtual_weight_mutation':False}},
 'historical_values_not_used_as_seed_threshold_target_or_expected_answer':True,
 'R3_solver_rerun_forbidden':True,'mesh_path_Dijkstra_is_only_bound_computation':True})
print('PREREQUISITES STATIC PASS; METHOD RECOVERED; source',len(cap['vertex_ids']),'index target',len(index),'all exact endpoints',len(c0),'formal files read',len(formal),'pose cases',len(poses),'virtual recipes',len(recipes),flush=True)
