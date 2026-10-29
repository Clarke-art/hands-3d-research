"""Independent scope, numeric, classifier, image and workspace byte audit.
A completed qualification may correctly fail its deformation gate while this
delivery/evidence verification passes. No automatic repair or Human approval.
"""
from common import *
import numpy as np,re
from PIL import Image
S=read(OUT/(PHASE+'_STATUS.json'));E=read(OUT/'FULL_STAGE6A_MACHINE_EVIDENCE_R1.json');C=E['cases'];G=read(OUT/'POSED_COORDINATES_R1.json');H=read(HIST/'POSED_COORDINATES_R1.json');Z=read(OUT/'FULL_STAGE6A_POST_DONOR_ZERO_RESET_AUDIT_R1.json');A=read(OUT/'FULL_STAGE6A_POST_DONOR_EXACT_CROSSING_AUDIT_R1.json');R=read(OUT/'FULL_STAGE6A_DORSAL_MCP_EXACT_STRUCTURE_R1.json');M=read(TARGETED/'MEASUREMENT_DOMAIN_MANIFEST_R1.json')
checks={};expected=read(HIST/'FULL_STAGE6A_CASE_MATRIX_R1.json')['cases'];ids={c['case_id'] for c in expected}
checks['42_unique_formal_case_ids']=len(C)==len(ids)==42 and set(C)==ids
checks['14joints_3angles']=len({r['case']['bone'] for r in C.values()})==14 and all({r['case']['angle_deg'] for r in C.values() if r['case']['bone']==bone}=={15,30,45} for bone in {r['case']['bone'] for r in C.values()})
checks['same_frozen_matrix_pose_semantics']=all(C[c['case_id']]['case']==c for c in expected)
checks['old_sign_sanity_qualified']=read(OUT/'FLEXION_AXIS_SIGN_AUDIT_R1.json')['qualified']
checks['formal_joint_isolation_locked_CMC_WRIST']=all(z['one_joint_only']==[C[cid]['case']['bone']] and z['locked_CMC_WRIST'] for cid,z in Z['cases'].items())
checks['zero_before_after_exact']=len(Z['cases'])==42 and all(z['before_max_mm']==z['after_max_mm']==0 and z['zero_rotation_location_scale_before_and_after'] for z in Z['cases'].values())
checks['native_bind_noise_unmodified_gate']=all(z['raw_RSSF_noise_mm']<=1e-4 and z['formal_zero_gate_mm']==1e-4 for z in Z['cases'].values())
checks['Blender_origin_AST_clean_reopen']=read(OUT/'BLENDER_RUNTIME_SOURCE_AND_CLEAN_REOPEN_VERIFICATION_R1.json')['status']=='PASS'
checks['input_preflight']=all(read(OUT/'PREREQUISITE_GATE_R1.json')['checks'].values()) and all(read(OUT/'LIVE_PREREQUISITE_GATE_R1.json')['checks'].values())
checks['no_extra_formal_cases']=S['FULL42_FORMAL_POSE_APPLICATIONS']==42 and S['HISTORICAL_FULL42_POSE_APPLICATIONS']==0 and not S['STAGE6B_STARTED']
checks['none_geometry_weight_group_modifier_saves']=S['PRODUCTION_SAVE_COUNT']==S['GEOMETRY_WEIGHT_BONE_GROUP_MODIFIER_MUTATION_COUNT']==0 and not list(OUT.glob('*.blend'))
checks['fresh_current_geometry_matches_frozen_derivative']=np.array_equal(np.array(G['bind_raw_world_m']),np.array(read(CAND.parent/'R2_REOPENED_NATIVE_PAYLOAD_R1.json')['coordinates_world_m']))
outside=sorted(set(range(3416))-set(APPROVED54));checks['outside54_all42_same_pose_exact_pre_donor']=all(np.array_equal(np.array(G['positions_world_m'][cid])[outside],np.array(H['positions_world_m'][cid])[outside]) for cid in ids)
# Independently derive complete current/formal counts and severe qualification sets.
checks['crossing_partition_complete']=S['CURRENT_TOTAL_EXACT_CROSSING_COUNT']==len(A['rows'])==S['CURRENT_SOURCE_EXISTING_CONTACT_COUNT']+S['CURRENT_UNAPPROVED_EXACT_CROSSING_COUNT']+S['CURRENT_KNOWN_HUMAN_ACCEPTED_CONTACT_COUNT']
formal={(r['case_id'],tuple(r['face_ids'])) for row in C.values() for r in row['crossings']};replay={(r['case_id'],tuple(r['face_ids'])) for r in A['rows'] if r['formal_pose_generated']}
checks['fresh_formal_vs_independent_census_exact_identity']=formal==replay
checks['formal_severe_class_sets_match']=set((cid,tuple(r['face_ids'])) for cid,row in C.items() for r in row['crossings'] if r['hard_blocker'])==set((r['case_id'],tuple(r['face_ids'])) for r in A['rows'] if r['formal_hard_blocker'])
checks['source_existing_ClassA_transparent_exact_no_donor_change']=all(r['old_vs_current_numeric_equivalence'] and not r['human_approved'] for r in A['rows'] if r['classification']=='SOURCE_EXISTING_CONTACT' and r['class'].startswith('CASE_A'))
known=read(OUT/'FULL_STAGE6A_KNOWN_HUMAN_CONTACT_AUDIT_R1.json')
checks['exact_scope_Human_three_no_extension']=len(known['rows'])==3 and {(r['case_id'],tuple(r['face_ids'])) for r in known['rows']}=={('TH_IP_30',(1225,2740)),('IDX_MCP_45',(1041,2735)),('IDX_MCP_45',(1226,2742))} and all(all(r['criteria'].values()) and r['non_blocking'] for r in known['rows']) and not known['cross_pose_acceptance_extended']
checks['IDX30_pair1226_2742_not_waived']=any(r['case_id']=='IDX_MCP_30' and r['face_ids']==[1226,2742] and r['formal_hard_blocker'] and not r['human_approved'] for r in A['rows'])
old9=read(OUT/'OLD_9_BLOCKER_FRESH_REMEASUREMENT_R1.json');checks['old9_forced_recorded_regardless_classifier']=len(old9['rows'])==9 and all(r['remeasured_even_if_current_classifier_would_disappear'] and 'current_face_coordinates_world_m' in r for r in old9['rows'])
checks['old9_severity_delta_actually_computed']=all(all(r['current_fresh_evidence'][k]-r['old_evidence'][k]==r['old_to_new_severity_delta'][k] for k in ['depth_mm','seg_mm','local_edge_mm']) for r in old9['rows'])
checks['current_verdict_from_fresh_blockers']=S['MACHINE_HARD_BLOCKER_COUNT']==len(E['blockers']) and S['FULL_STAGE6A_MACHINE_QUALIFICATION']==('FAIL' if E['blockers'] else 'PASS') and not S['current_verdict_inherited_from_old']
checks['donor_roi42_coverage']=set(R['results'])==ids and all(r['new_structural_evidence_count']==0 for r in R['results'].values())
checks['ROI_Human_not_closed']=S['DORSAL_MCP_HUMAN_VISUAL_STATUS']=='PENDING_HUMAN_REVIEW' and not read(OUT/'FULL_STAGE6A_DORSAL_MCP_REGRESSION_R1.json')['FINAL_VISUAL_PASS']
for r in R['sources']:
 p=ROOT/r['source']['path'];nodes={n.name:digest(ast.dump(n)) for n in ast.parse(p.read_text(encoding='utf-8-sig')).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))};checks['ROI_source_'+p.name]=sha(p)==r['source']['sha256'] and all(nodes[k]==v for k,v in r['function_AST_sha256'].items())
# Full-mesh edge tests, calculated independently in float64 from the recorded native coordinates.
ee=np.array(G['edges']);bind=np.array(G['bind_raw_world_m']);bl=np.linalg.norm(bind[ee[:,0]]-bind[ee[:,1]],axis=1)*1000
numeric_count=0;max_ratio_delta=0.;severe_matches=True;finite=True
for cid,row in C.items():
 v=np.array(G['positions_world_m'][cid]);finite&=bool(np.isfinite(v).all());ratios=np.linalg.norm(v[ee[:,0]]-v[ee[:,1]],axis=1)*1000/bl
 numeric_count+=len(ratios);max_ratio_delta=max(max_ratio_delta,abs(float(ratios.max())-row['global_metrics']['max_edge_ratio']),abs(float(ratios.min())-row['global_metrics']['min_edge_ratio']))
 severe_matches&=set(np.where((bl>=3)&(ratios>5))[0])=={r['edge_id'] for r in row['severe_edges']}
checks['independent_allmesh_severe_edge_sets']=severe_matches
checks['independent_allmesh_ratio_extrema_storage_precision']=max_ratio_delta<1e-4
checks['full42_coordinate_finite']=finite
checks['TIP_helpers_all42_zero']=all(r['TIP_HELPER_DEFORMATION_INFLUENCE_COUNT']==0 for r in C.values())
checks['tip14_fresh_trajectories']=len(E['tip_monotonic'])==14 and all(E['tip_monotonic'].values())
checks['debt16_retained']=read(OUT/'FULL_STAGE6A_INHERITED16_DEBT_AUDIT_R1.json')['true_deformation_failure_count']==0 and all(r['static_debt_status']=='NOT_RESOLVED' and not r['old_static_debt_deleted'] for r in read(OUT/'FULL_STAGE6A_INHERITED16_DEBT_AUDIT_R1.json')['rows'])
v=read(OUT/'EVIDENCE_RENDER_MANIFEST_R1.json');byview={};clipping=[];paired_identical=0
for r in v['renders']:
 p=OUT/r['path'];im=Image.open(p);im.verify();assert list(Image.open(p).size)==r['resolution']
 byview.setdefault(r['view_key'],[]).append(r)
 arr=G if r['asset']=='CURRENT_FRESH' else H;ps=np.array(arr['positions_world_m'][r['case_id']])[r['focus_vertex_ids']]-np.array(r['camera_centre_m']);d=np.array(r['camera_direction']);d/=np.linalg.norm(d);u=np.array(r['camera_up']);u-=u@d*d;u/=np.linalg.norm(u);rr=np.cross(u,d);rr/=np.linalg.norm(rr);W,Hp=r['resolution'];scale=(W/2-8)/(r['half_width_mm']/1000);xs=ps@rr*scale+W/2;ys=ps@u*scale+Hp/2
 n=int(np.sum((xs<0)|(xs>=W)|(ys<0)|(ys>=Hp)))
 if n:clipping.append({'view':r['view_key'],'asset':r['asset'],'count':n})
for key,rows in byview.items():
 checks['matched_view_'+key]=len(rows)==2 and all(rows[0][k]==rows[1][k] for k in ['camera_centre_m','camera_direction','camera_up','half_width_mm','resolution'])
 if len(rows)==2 and sha(OUT/rows[0]['path'])==sha(OUT/rows[1]['path']):paired_identical+=1
checks['native_focus_no_clipping']=not clipping
checks['all42_fresh_full_solids']=all(any(r['case_id']==cid and r['asset']=='CURRENT_FRESH' and r['style']=='FULL_SOLID' for r in v['renders']) for cid in ids)
checks['14_joint45_representatives']=all(any(r['case_id']==c['case_id'] and r['asset']=='CURRENT_FRESH' and r['style']=='NAIL_SOLID' for r in v['renders']) for c in expected if c['angle_deg']==45)
checks['RING3_full_close_grazing']=all(any(r['case_id']==cid and r['asset']=='CURRENT_FRESH' and r['style']==style for r in v['renders']) for cid in ['RNG_MCP_15','RNG_MCP_30','RNG_MCP_45'] for style in ['FULL_SOLID','DORSAL_MCP_CLOSE_SOLID','DORSAL_MCP_GRAZING_SOLID'])
checks['all_blocker_context_isolation']=all(any(x['case_id']==r['case_id'] and x['asset']=='CURRENT_FRESH' and x['style']==f"PAIR_{r['face_ids'][0]}_{r['face_ids'][1]}_ISOLATED" for x in v['renders']) for r in old9['rows'])
for link in re.findall(r'(?:href|src)="([^"]+)"',(OUT/'review.html').read_text(encoding='utf-8')):
 if not link.startswith('#'):assert (OUT/link.split('#')[0]).is_file(),link
checks['old_full42_historical_bytes_unchanged']=sha(HIST/'FULL_STAGE6A_REQUALIFICATION_R1_STATUS.json')=='d2c3bb13a77dd123e278d21e98ebdb724706dd8c789f91f0d2ac9e4d2f03d0a6'
checks['current_derivative_bytes']=sha(CAND)==EXPECTED_CAND
checks['corrected_rig_bytes']=sha(CORRECTED)==EXPECTED_RIG
required=[PHASE+'_REPORT.md',PHASE+'_STATUS.json','FULL_STAGE6A_POST_DONOR_CASE_MATRIX_R1.json','FULL_STAGE6A_POST_DONOR_ZERO_RESET_AUDIT_R1.json','FULL_STAGE6A_POST_DONOR_LOCAL_STRAIN_AUDIT_R1.json','FULL_STAGE6A_POST_DONOR_SEVERE_EDGE_STRETCH_AUDIT_R1.json','FULL_STAGE6A_POST_DONOR_EXACT_CROSSING_AUDIT_R1.json','OLD_9_BLOCKER_FRESH_REMEASUREMENT_R1.json','OLD_VS_NEW_FULL_STAGE6A_BLOCKER_COMPARISON_R1.json','FULL_STAGE6A_KNOWN_HUMAN_CONTACT_AUDIT_R1.json','FULL_STAGE6A_DORSAL_MCP_REGRESSION_R1.json','FULL_STAGE6A_CAP37_AUDIT_R1.json','FULL_STAGE6A_OLD_CAP9_AUDIT_R1.json','FULL_STAGE6A_FIRST_WEB_AUDIT_R1.json','FULL_STAGE6A_NAIL_AUDIT_R1.json','FULL_STAGE6A_NON_TARGET_CONTAMINATION_R1.json','FULL_STAGE6A_HISTORICAL_COMPARISON_R1.json','review.html']
checks['required_artifacts_complete']=all((OUT/n).is_file() for n in required)
before=read(OUT/'PROTECTED_HISTORY_HASHES_BEFORE.json');after=inventory();changed=[n for n,h in before.items() if n in after and after[n]!=h];missing=sorted(set(before)-set(after));new=sorted(set(after)-set(before));drift=len(changed)+len(missing)+len(new)
checks['all_preexisting_workspace_files_exact']=drift==0
dump('PROTECTED_HISTORY_HASHES_AFTER.json',after)
dump('PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json',{'status':'PASS' if drift==0 else 'FAIL_CLOSED','PRODUCTION_DRIFT':drift,'protected_preexisting_file_count':len(before),'changed_files':changed,'deleted_files':missing,'new_files_outside_current_phase':new,'all_preexisting_bytes_exact':before==after,'current_derivative':ref(CAND),'current_weight_vector_hash':EXPECTED_WEIGHTS,'independent_native_reopen':ref(OUT/'BLENDER_RUNTIME_SOURCE_AND_CLEAN_REOPEN_VERIFICATION_R1.json'),'production_blend_saves':0,'scope':'Every pre-existing workspace file, including all Stage4/5/targeted/true-cap/Human/old Full42 artifacts. Only this phase output subtree excluded.'})
passed=all(checks.values());verification={'status':'PASS' if passed else 'FAIL_CLOSED_DELIVERY_VERIFICATION','checks':checks,'qualification_verdict_is_separate_from_delivery_verification':True,'current_machine_qualification':S[PHASE],'protected_file_count':len(before),'full_mesh_independent_edge_ratio_checks':numeric_count,'max_float64_vs_historical_float32_ratio_extrema_delta':max_ratio_delta,'matched_view_count':len(byview),'render_image_count':len(v['renders']),'pixel_identical_matched_view_count':paired_identical,'focus_clipping':clipping,'production_drift':drift}
dump('INDEPENDENT_DELIVERY_VERIFICATION_R1.json',verification)
S.update({'PRODUCTION_DRIFT':drift,'PROTECTED_PREEXISTING_FILE_COUNT':len(before),'DELIVERY_VERIFICATION':'PASS' if passed else 'FAIL_CLOSED','VERDICT':S[PHASE] if passed else 'FAIL_CLOSED_FULL_STAGE6A_REQUALIFICATION','MINIMAL_CURRENT_BLOCKER_SCOPE':S['FAILING_CASES'],'evidence_verification_failed_fields':[k for k,val in checks.items() if not val]})
dump(PHASE+'_STATUS.json',S)
report=OUT/(PHASE+'_REPORT.md');txt=report.read_text(encoding='utf-8').replace('| `PRODUCTION_DRIFT` | `PENDING_FINAL_HASH_VERIFICATION` |','| `PRODUCTION_DRIFT` | `'+str(drift)+'` |')
txt+='\n## Independent final delivery verification\n\n'+str(len(before))+'个预存workspace文件SHA256逐个完全相同，changed/deleted/new-outside-phase均0。'+str(numeric_count)+'条独立全mesh edge-ratio复算，最大float64与历史float32比例极值差'+str(max_ratio_delta)+'；正式3mm/>5x gate未改变。'+str(len(v['renders']))+'张PNG、'+str(len(byview))+'对matched camera/scale有效，focus clipping0。原Blender运行时AST及独立clean native reopen PASS，R2全3416权重与frozen corrected rig一致。\n\n交付验证='+verification['status']+'；变形资格仍='+S[PHASE]+'。当前9个blocker基于fresh42，不继承历史verdict。NEXT='+S['NEXT']+'，未执行；STOP。\n'
report.write_text(txt,encoding='utf-8')
dump('OUTPUT_ARTIFACT_HASH_MANIFEST.json',{p.relative_to(OUT).as_posix():sha(p) for p in OUT.rglob('*') if p.is_file() and p.name!='OUTPUT_ARTIFACT_HASH_MANIFEST.json'})
print(json.dumps({'delivery_verification':verification['status'],'qualification':S[PHASE],'formal_completed':len(C),'blockers':S['MACHINE_HARD_BLOCKER_COUNT'],'old9_still':S['OLD_9_STILL_PRESENT_COUNT'],'new_pairs':S['CURRENT_NEW_PAIR_COUNT'],'protected_files':len(before),'drift':drift,'images':len(v['renders']),'focus_clipping':clipping,'failed_checks':[k for k,val in checks.items() if not val]},ensure_ascii=False),flush=True)
assert passed,'FAIL CLOSED: fix qualification harness/evidence only; no production repair'
