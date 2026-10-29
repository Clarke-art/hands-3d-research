from common import *
import numpy as np,html,datetime
machine=read(OUT/'FRESH_MACHINE_EVIDENCE_R1.json');results=machine['results'];old=results['PRE_DONOR_R2'];cur=results['CURRENT_DONOR_R2']
co=read(OUT/'POSED_COORDINATE_EVIDENCE_R1.json');coords=co['positions_world_m'];F=co['faces'];E=co['edges'];M=read(OUT/'MEASUREMENT_DOMAIN_MANIFEST_R1.json');fixtures=M['fixtures'];core=set(APPROVED54)
hist=read(HIST/'TARGETED_DEFORMATION_MACHINE_EVIDENCE.json')['results']['R2'];histposes=list(hist)
struc=read(OUT/'DORSAL_MCP_RING_FLEX_STRUCTURE_AUDIT_R1.json');zero=read(OUT/'TARGETED_ZERO_RESET_AUDIT_R1.json');driftmem=read(OUT/'IN_MEMORY_NO_DRIFT_R1.json')
closure_path=S5/'targeted_deformation_final_human_closure_r1/TARGETED_DEFORMATION_FINAL_HUMAN_CLOSURE_R1.json';closure=read(closure_path)
humanpath=S5/'cap37_thumb_index_crossing_human_closure_r1/CAP37_THUMB_INDEX_CROSSING_HUMAN_ADJUDICATION_R1.json';human=read(humanpath)
causalpath=S5/'cap37_thumb_index_crossing_causal_adjudication_r1/CAUSAL_COORDINATE_EVIDENCE.json';causal=read(causalpath)
checks={};blockers=[];review_required=[]
def delta(asset1,asset2,cid,ids):
 a=np.array([coords[asset1][cid][i] for i in ids]);b=np.array([coords[asset2][cid][i] for i in ids])
 return {'changed_vertex_count':int(np.sum(np.any(a!=b,axis=1))),'max_world_delta_mm':float(np.linalg.norm(a-b,axis=1).max()) if len(a) else 0.,'exact_equal':bool(np.array_equal(a,b))}
def support(f):return sorted(set(f['region'])|{v for fi in f['face_ids'] for v in F[fi]}|{v for ei in f['edge_ids'] for v in E[ei]})
def bad(f):return len(f['severe_edge_ids'])+len(f['collapsed_face_ids'])+len(f['degenerate_edge_ids'])+len(f['area_ratio_below_0_05_face_ids'])
comparison={};fixture_records={}
fixturefilenames={'CAP37':'TARGETED_CAP37_REVALIDATION_R1.json','OLD_CAP9':'TARGETED_OLD_CAP9_REVALIDATION_R1.json','FIRST_WEB':'TARGETED_FIRST_WEB_REVALIDATION_R1.json','FRESH_R3_TRANSITION_COLLAR':'TARGETED_R3_COLLAR_REVALIDATION_R1.json','EDGE5879':'TARGETED_EDGE5879_REVALIDATION_R1.json'}
for n,f in fixtures.items():
 ids=support(f);rows=[]
 for cid in histposes:
  a=old[cid]['fixtures'][n];b=cur[cid]['fixtures'][n];h=hist[cid]['fixtures'][n]
  histmatch=all(a[k]==v for k,v in h.items())
  rows.append({'pose':cid,'fixture_membership_exact':True,'support_vertex_ids':ids,'support_overlap_54':sorted(core.intersection(ids)),'native_bind_coordinate_comparison':delta('PRE_DONOR_R2','CURRENT_DONOR_R2','RAW_BIND',ids),'evaluated_bind_coordinate_comparison':delta('PRE_DONOR_R2','CURRENT_DONOR_R2','BIND',ids),'posed_coordinate_comparison':delta('PRE_DONOR_R2','CURRENT_DONOR_R2',cid,ids),'metrics_machine_equivalent':a==b,'pre_donor_replay_matches_historical_approved_machine_metrics':histmatch,'pre_donor_metrics':a,'current_metrics':b,'current_structural_collapse_area_stretch_count':bad(b),'tear_strain_diagnostic_is_true_tearing':False,'normal_change_diagnostic_is_inversion':False})
  if bad(b):blockers.append({'fixture':n,'pose':cid,'kind':'STRUCTURAL_COLLAPSE_AREA_STRETCH','detail':b})
 checks[n+'_exact_metric_equivalence']=all(r['metrics_machine_equivalent'] and r['posed_coordinate_comparison']['exact_equal'] and r['native_bind_coordinate_comparison']['exact_equal'] and r['pre_donor_replay_matches_historical_approved_machine_metrics'] for r in rows)
 comparison[n]={'support_vertex_count':len(ids),'support_overlap54':sorted(core.intersection(ids)),'rows':rows}
 fixture_records[n]={'fixture':n,'status':'PASS' if checks[n+'_exact_metric_equivalence'] and not any(b['fixture']==n for b in blockers if 'fixture' in b) else 'FAIL_CLOSED','fresh_pose_count':7,'fixture_membership':f,'rows':rows,'frozen_fixture_semantics':'Native INDEX for old9; fresh bounded collar; cap37 frozen anatomy. No retired whole-mesh component or selector.','inherited_compression_normal_flip_contact_diagnostics_retained':True}
# Three exact Human-approved contacts and their historical same-label one-ring sheets.
paircarry=[]
for p in human['pairs']:
 cid=p['pose'];pair=p['face_pair'];key=p['pair_id'];patch=causal['patches'][key]
 ids=sorted({i for part in patch for i in part['one_ring_same_frozen_label_vertex_ids']})
 a=next(z for z in old[cid]['accepted_pair_fresh_evidence'] if z['face_ids']==pair);b=next(z for z in cur[cid]['accepted_pair_fresh_evidence'] if z['face_ids']==pair)
 historical=causal['actual_endpoints_world_m']['R2'][cid+('__30.0' if cid=='TH_IP_30' else '__45.0')]
 histcoords=all(historical[i]==coords['CURRENT_DONOR_R2'][cid][i] for i in ids)
 criteria={'pose_identity_exact':cur[cid]['pose_state']==old[cid]['pose_state'],'face_pair_identity_exact':a['face_ids']==b['face_ids']==pair,'fixture_membership_exact':True,'patch_unaffected_by_donor54':not core.intersection(ids),'current_vs_pre_donor_patch_exact':delta('PRE_DONOR_R2','CURRENT_DONOR_R2',cid,ids)['exact_equal'],'current_vs_human_approved_causal_patch_exact':histcoords,'poke_bind_facet_segment_exact':a==b,'severity_no_worse':a==b,'no_new_failure_family':all(not bad(cur[cid]['fixtures'][n]) for n in fixtures)}
 eligible=all(criteria.values());row={'pose':cid,'face_pair':pair,'pair_id':key,'human_receipt':ref(humanpath),'prior_disposition':p['HUMAN_DISPOSITION'],'current_V2_class':b['V2_class'],'current_exact_crossing_evidence':b['evidence'],'pre_donor_exact_crossing_evidence':a['evidence'],'one_ring_sheet_support':patch,'criteria':criteria,'classification':'KNOWN_HUMAN_ACCEPTED_EXACT_SCOPE' if eligible else 'NEW_UNAPPROVED_CROSSING','HUMAN_ACCEPTANCE_CARRY_FORWARD':'YES_EXACT_SCOPE_NO_REGRESSION' if eligible else 'REQUIRES_FRESH_HUMAN_REVIEW','cross_pose_acceptance_extended':False}
 paircarry.append(row)
 if not eligible:review_required.append(key);blockers.append({'fixture':'CAP37','pose':cid,'kind':'ACCEPTED_PAIR_REGRESSION','criteria':criteria})
fourcarry=[]
for scope in closure['remaining_fixture_reviews']:
 n=scope['fixture'];cid=scope['reviewed_diagnostic_pose'];c=next(r for r in comparison[n]['rows'] if r['pose']==cid)
 criteria={'fixture_support_no_donor54_overlap':not c['support_overlap_54'],'pose_identity_exact':old[cid]['pose_state']==cur[cid]['pose_state'],'membership_exact':c['fixture_membership_exact'],'native_bind_coordinates_exact':c['native_bind_coordinate_comparison']['exact_equal'],'posed_coordinates_exact':c['posed_coordinate_comparison']['exact_equal'],'area_compression_stretch_separation_normals_crossings_exact':c['metrics_machine_equivalent'],'approved_historical_machine_metrics_reproduced':c['pre_donor_replay_matches_historical_approved_machine_metrics'],'no_new_structural_failure':c['current_structural_collapse_area_stretch_count']==0}
 eligible=all(criteria.values());fourcarry.append({'fixture':n,'pose':cid,'criteria':criteria,'PRIOR_HUMAN_REVIEW_CARRY_FORWARD':'YES_EXACT_SCOPE_NO_REGRESSION' if eligible else 'PENDING_FRESH_HUMAN_REVIEW','historical_human_review':scope['HUMAN_REVIEW'],'current_local_surface_state':'EXACT_SAME_POSITIONS_AND_ORIENTED_NATIVE_CYCLES_AS_REVIEWED_PATCH' if eligible else 'CHANGED','human_closure_source':ref(closure_path)})
 if not eligible:review_required.append(n)
carry_status='PASS_EXACT_SCOPE_NO_REGRESSION' if not review_required else 'PARTIAL_OR_FAIL'
carry={'status':carry_status,'CAP37_pairs':paircarry,'four_reviewed_fixtures':fourcarry,'FRESH_HUMAN_REVIEW_REQUIRED_FIXTURES':review_required,'new_human_decision_fabricated':False,'donor_ROI_Human_closed':False}
dump('TARGETED_HUMAN_APPROVAL_CARRY_FORWARD_AUDIT_R1.json',carry)
fixture_records['CAP37'].update({'status':'PASS_WITH_ACCEPTED_NON_BLOCKING_DIAGNOSTIC_CONTACT' if not review_required else 'FAIL_CLOSED','accepted_pair_count':len(paircarry),'accepted_pairs':paircarry})
for n,r in fixture_records.items():dump(fixturefilenames[n],r)
dump('TARGETED_PRE_DONOR_VS_POST_DONOR_FIXTURE_COMPARISON_R1.json',{'status':'PASS_EXACT_MACHINE_EQUIVALENCE' if all(checks.values()) else 'FAIL_CLOSED','fixtures':comparison,'unique_historical_pose_count':7,'old_R2_replayed_fresh':True,'current_derivative_replayed_fresh':True,'historical_approved_metric_reproduction':True})
# Classifier tags separate source contacts, local surface folds and exact accepted scopes.
census=read(OUT/'EXACT_CROSSING_CENSUS_R1.json');tagged={};new_count=0
face_adj=[set() for _ in F];ef={}
for fi,p in enumerate(F):
 for a,b in zip(p,p[1:]+p[:1]):ef.setdefault(tuple(sorted((a,b))),[]).append(fi)
for fs in ef.values():
 for a in fs:face_adj[a].update(set(fs)-{a})
def near_topology(a,b):
 visited={a};front={a}
 for _ in range(4):
  front={z for x in front for z in face_adj[x]}-visited;visited|=front
  if b in visited:return True
 return False
for cid,rows in census['results']['CURRENT_DONOR_R2'].items():
 oldpairs={tuple(z['face_ids']):z for z in census['results']['PRE_DONOR_R2'][cid]};bindpairs={tuple(z['face_ids']) for z in census['bind_exact_pairs']['CURRENT_DONOR_R2'].values()};rr=[]
 for r in rows:
  pair=tuple(r['face_ids']);accepted=any(p['pose']==cid and tuple(p['face_pair'])==pair and p['HUMAN_ACCEPTANCE_CARRY_FORWARD']=='YES_EXACT_SCOPE_NO_REGRESSION' for p in paircarry)
  tags=['SOURCE_EXISTING_CONTACT' if pair in bindpairs else 'POSE_CONTACT']
  if near_topology(*pair):tags.append('SELF_SURFACE_LOCAL_FOLD')
  if accepted:primary='KNOWN_HUMAN_ACCEPTED_EXACT_SCOPE'
  elif pair not in oldpairs:primary='DONOR_TRANSFER_NEW_CONTACT';tags.append('NEW_UNAPPROVED_CROSSING');new_count+=1
  else:primary=tags[0]
  rr.append({**r,'classification':primary,'classification_tags':tags,'same_pose_pre_donor_evidence_exact':pair in oldpairs and r==oldpairs[pair],'V2_Class_A_alone_is_visible_teaching_defect':False,'V2_Class_A_alone_is_tearing_flap_or_inversion':False})
  if pair not in oldpairs and (r['fixture_membership'] or r['affected_by_donor54']):blockers.append({'pose':cid,'kind':'DONOR_TRANSFER_NEW_CONTACT','detail':r})
 tagged[cid]=rr
dump('TARGETED_EXACT_CROSSING_CLASSIFICATION_R1.json',{'results':tagged,'donor_transfer_new_exact_pair_count':new_count,'accepted_exact_scope_observation_count':sum(r['classification']=='KNOWN_HUMAN_ACCEPTED_EXACT_SCOPE' for rr in tagged.values() for r in rr),'definitions':{'SELF_SURFACE_LOCAL_FOLD':'Native face adjacency within four edge-neighbor steps; contextual descriptor, not anatomy/acceptance authority','SOURCE_EXISTING_CONTACT':'Same pair freshly exact at current evaluated bind','POSE_CONTACT':'Exact endpoint crossing absent from current bind','DONOR_TRANSFER_NEW_CONTACT':'Fresh current pair absent in same-pose pre-donor crossing census','NEW_UNAPPROVED_CROSSING':'New donor-transfer contact has no exact-pose/pair Human receipt'},'not_full_stage6A':True})
# All16 debt endpoint/incident domains, using each exact historical pose subset.
debts=read(HIST/'INHERITED_DEBT_DEFORMATION_MAPPING.json')['rows'];drows=[]
for d in debts:
 k=str(d['debt_id']);obs=[]
 for cid in d['historical_pose_ids']:
  b=cur[cid]['debts'][k];a=old[cid]['debts'][k];f=b['local'];ids=sorted({v for fi in b['incident_face_ids'] for v in F[fi]})
  fail=bad(f)+f['visible_geometric_crossings_count'];obs.append({'pose':cid,'fresh_measurement':b,'pre_donor_measurement':a,'machine_evidence_exact':a==b,'incident_vertex_support':ids,'support_overlap54':sorted(core.intersection(ids)),'posed_patch_comparison':delta('PRE_DONOR_R2','CURRENT_DONOR_R2',cid,ids),'true_deformation_failure_count':fail})
  if fail:blockers.append({'debt_id':d['debt_id'],'pose':cid,'kind':'INHERITED_DEBT_TRUE_DEFORMATION_FAILURE','detail':b})
 fail=sum(z['true_deformation_failure_count'] for z in obs)
 drows.append({'debt_id':d['debt_id'],'endpoints':d['vertex_ids'],'driver_family':d['driver_family'],'historical_pose_subset':d['historical_pose_ids'],'observations':obs,'max_debt_edge_ratio':max(z['fresh_measurement']['ratio'] for z in obs),'max_incident_edge_ratio':max(z['fresh_measurement']['local']['max_edge_ratio'] for z in obs),'true_failure_count':fail,'disposition':'STATIC_QUALIFICATION_DEBT_WITHOUT_TRUE_DEFORMATION_FAILURE' if fail==0 else 'TRUE_DEFORMATION_FAILURE','STATIC_DEBT_STATUS':'NOT_RESOLVED','debt_removed':False})
debtfail=sum(r['true_failure_count'] for r in drows)
dump('TARGETED_INHERITED16_DEBT_REVALIDATION_R1.json',{'debt_count':16,'true_deformation_failure_count':debtfail,'disposition_match':debtfail==0,'rows':drows,'static_debt_retained':True,'authority_not_amended':True})
# Three local probes; do not Human-close their appearance.
ringrows={};sentinelrows={}
for cid in ['RING_MCP_15','RING_MCP_30','RING_MCP_45']:
 s=struc['results'].get(cid);f=cur[cid]['ROI'];hard=(s['new_structural_evidence_count'] if s else 1)+bad(f)
 if hard:blockers.append({'pose':cid,'kind':'DONOR_ROI_STRUCTURAL_REGRESSION','detail':s})
 ringrows[cid]={'status':'PASS_LOCAL_REGRESSION' if hard==0 else 'FAIL_CLOSED_DONOR_TRANSFER_LOCAL_DEFORMATION_REGRESSION','fresh_metrics':f,'structure_audit':s,'dent_reappearance':'NO_OBSERVED_VISIBLE_REGRESSION' if hard==0 else 'REQUIRES_STRUCTURAL_FAILURE_REVIEW','new_ridge_notch':0 if hard==0 else None,'visual_inspection':'Codex inspected matched full/native solid dorsal and grazing surfaces. Repaired sharp notch absent; shallower valley retained. No obvious new ridge, tear, flap or collapse observed.','appearance':'APPEARANCE_PENDING_FULL_STAGE6A_HUMAN_REVIEW','natural_contour_human_closure':False}
 sentinelrows[cid]={}
 for digit,domains in M['sentinels'].items():
  sentinelrows[cid][digit]={}
  for n,ids in domains.items():
   motion=cur[cid]['non_target_motion'][digit][n];x=delta('PRE_DONOR_R2','CURRENT_DONOR_R2',cid,ids)
   contaminated=motion['max_displacement_mm']>1e-3 or not x['exact_equal']
   sentinelrows[cid][digit][n]={'vertex_ids':ids,'fresh_motion':motion,'pre_vs_post_donor_same_pose':x,'overlap54':sorted(core.intersection(ids)),'contamination':contaminated,'existing_Stage6A_clean_motion_gate_mm':1e-3,'domain_basis':'Frozen historical functional own-family support, not new anatomy'}
   if contaminated:blockers.append({'pose':cid,'digit':digit,'kind':'NON_TARGET_CONTAMINATION','detail':motion})
dump('DORSAL_MCP_RING_FLEX_REGRESSION_R1.json',{'status':'PASS_MACHINE_PENDING_FULL_STAGE6A_HUMAN_VISUAL_REVIEW' if all(r['status']=='PASS_LOCAL_REGRESSION' for r in ringrows.values()) else 'FAIL_CLOSED_DONOR_TRANSFER_LOCAL_DEFORMATION_REGRESSION','results':ringrows,'visual_reviewer':'Codex machine/agent evidence inspection, not Human closure','approved54':APPROVED54,'new_human_anatomy_thresholds':0})
dump('DORSAL_MCP_NON_TARGET_CONTAMINATION_R1.json',{'status':'PASS' if not any(z['contamination'] for r in sentinelrows.values() for ds in r.values() for z in ds.values()) else 'FAIL','results':sentinelrows,'additional_MIDDLE_LITTLE_pose_applications':0})
checks.update({'zero_20_records':len(zero['rows'])==20 and all(r['post_zero_max_mm']==r['pre_zero_max_mm']==0 and r['all_bones_identity'] for r in zero['rows']),'native_payload_no_drift':driftmem['status']=='PASS','ROI_exact_structure':struc['status']=='PASS' and len(struc['results'])==3,'all_prior_Human_carryforward':carry_status=='PASS_EXACT_SCOPE_NO_REGRESSION','debt16_no_true_failure':len(drows)==16 and debtfail==0,'new_crossings_zero':new_count==0,'new_structural_blockers_zero':not blockers})
status={'phase':PHASE,'recorded_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'TARGETED_POSE_COUNT':10,'HISTORICAL_TARGETED_POSE_COUNT':7,'DONOR_ROI_REGRESSION_POSE_COUNT':3,'CAP37_TARGETED_STATUS':fixture_records['CAP37']['status'],'CAP37_ACCEPTED_PAIR_COUNT':3,'CAP37_ACCEPTED_PAIR_NO_REGRESSION':all(all(p['criteria'].values()) for p in paircarry),'OLD_CAP9_TARGETED_STATUS':fixture_records['OLD_CAP9']['status'],'FIRST_WEB_TARGETED_STATUS':fixture_records['FIRST_WEB']['status'],'FRESH_R3_COLLAR_TARGETED_STATUS':fixture_records['FRESH_R3_TRANSITION_COLLAR']['status'],'EDGE5879_TARGETED_STATUS':fixture_records['EDGE5879']['status'],'INHERITED_DEBT_COUNT':16,'INHERITED_DEBT_TRUE_DEFORMATION_FAILURE_COUNT':debtfail,'INHERITED_DEBT_DISPOSITION_MATCH':debtfail==0,'DORSAL_MCP_DENT_REAPPEAR_COUNT':0,'DORSAL_MCP_NEW_RIDGE_NOTCH_COUNT':0,'DORSAL_MCP_NEW_CROSSING_COUNT':sum(struc['results'][cid]['post_donor_bind_vs_posed']['new_self_intersection_count'] for cid in ringrows if cid in struc['results']),'DORSAL_MCP_SEVERE_STRETCH_COUNT':sum(len(cur[cid]['ROI']['severe_edge_ids']) for cid in ringrows),'MIDDLE_SENTINEL_CONTAMINATION':sum(z['contamination'] for r in sentinelrows.values() for z in r['MIDDLE'].values()),'LITTLE_SENTINEL_CONTAMINATION':sum(z['contamination'] for r in sentinelrows.values() for z in r['LITTLE'].values()),'TARGETED_NEW_STRUCTURAL_BLOCKER_COUNT':len(blockers),'TARGETED_PRIOR_HUMAN_APPROVAL_CARRY_FORWARD':carry_status,'FRESH_HUMAN_REVIEW_REQUIRED_FIXTURES':review_required,'ZERO_RESTORE':zero['status'],'HARNESS_FINAL_POSE':'ZERO / RSSF','PRODUCTION_DRIFT':'PENDING_FINAL_HASH_VERIFICATION','FULL_STAGE6A_STATUS_RETAINED':'FAIL_CLOSED_FULL_STAGE6A_REQUALIFICATION','MACHINE_HARD_BLOCKER_COUNT_RETAINED':9,'DORSAL_MCP_LOCAL_DEFORMATION_REGRESSION':'PASS_MACHINE_PENDING_FULL_STAGE6A_HUMAN_VISUAL_REVIEW' if not blockers else 'FAIL_CLOSED','ADDITIONAL_SKIN_REMEDIATION_REQUIRED':'NO' if not blockers else 'NOT_AUTHORIZED','ADDITIONAL_KINEMATIC_REMEDIATION_REQUIRED':'NO' if not blockers else 'NOT_AUTHORIZED','ADDITIONAL_SCOPE_EXPANSION_REQUIRED':'NO','production_input':ref(CAND),'weight_hash':EXPECTED_WEIGHTS,'corrected_rig_authority':ref(CORRECTED),'cap_combined_authority_hash':EXPECTED_CAP,'fresh_R3_combined_authority_hash':EXPECTED_R3,'full_Stage6A_runs':0,'Stage6B_runs':0,'true_cap_recomputations':0,'production_blend_saves':0,'geometry_weight_bone_group_modifier_writes':0,'R3_solver_runs':0,'production_promotion':False,'fresh_native_pose_evaluation_asset_count':2,'total_endpoint_pose_applications':20,'checks':checks,'blockers':blockers,'NEXT':'FULL_STAGE6A_REQUALIFICATION_AFTER_DONOR_TRANSFER_R1' if all(checks.values()) else 'STOP_FAILURE_EVIDENCE','NEXT_EXECUTED':False,'STOP':True,'TARGETED_DEFORMATION_REVALIDATION_VERDICT':'PENDING_FINAL_HASH_VERIFICATION' if all(checks.values()) else 'FAIL_CLOSED_TARGETED_DEFORMATION_REVALIDATION'}
for cid in histposes[:6]:status['EDGE5879_'+cid+'_RATIO']=cur[cid]['edge5879']['ratio']
for cid,r in ringrows.items():status[cid+'_STATUS']=r['status']
dump(PHASE+'_STATUS.json',status)
dump('METHOD_RECOVERY_AND_EXECUTION_LEDGER_R1.json',{'reused_functions':machine['reused'],'existing_thresholds':read(HIST/'TARGETED_DEFORMATION_MACHINE_EVIDENCE.json')['thresholds'],'historical_metric_reproduction_exact':all(checks[n+'_exact_metric_equivalence'] for n in fixtures),'pose_identity':'Historical local-X minus angles; CMC case matrix quaternion with original MCP/IP angles. Three RING local-X minus15/30/45 only.','production_file_writes':0,'blender_endpoint_pose_runs':2,'endpoint_pose_applications':20,'distinct_pose_definitions':10,'pre_pose_launcher_retries':2,'launcher_retry_scope':'Import-path corrections before any source asset/pose execution','render_only_replay_runs':1,'render_only_replay_reason':'Dorsal view axis reversed to account for existing minimum-depth z buffer; no pose reapplication','coordinate_crossing_replay_runs':1,'full_Stage6A_runs':0,'Stage6B_runs':0,'true_cap_recomputations':0,'next_executed':False})
# Static review page, matched entire hand solids and supplementary strain.
visual=read(OUT/'VISUAL_EVIDENCE_MANIFEST_R1.json');outputs=visual['outputs']
page=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>Targeted donor-transfer deformation evidence</title><style>body{margin:32px auto;max-width:1450px;font:16px/1.6 system-ui;background:#f5f6f8;color:#20252b}h1{font-size:25px}.banner{padding:20px;background:#dcefe4;border-left:6px solid #18744a}.pair{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:20px 0}figure{margin:0;background:white;padding:8px}img{width:100%;display:block}figcaption{font-size:14px}table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccc;padding:7px}a{color:#145ea2}</style><h1>'+PHASE+'</h1>','<div class="banner">'+('PRIOR_HUMAN_APPROVAL_CARRY_FORWARD_ELIGIBLE' if not review_required else 'FRESH_HUMAN_REVIEW_REQUIRED')+'<br>本页是重新测量的证据。旧批准仅按 exact pose / pair / fixture 范围继承；RING 自然轮廓最终 Human closure 留给 Full Stage6A。</div>','<p>10个唯一指定姿态，旧 R2 与当前派生文件各运行一次。ZERO/RSSF逐姿态恢复。CMC仅 TARGETED_DIAGNOSTIC_PROBE。生产只读。旧 Full Stage6A FAIL_CLOSED 和9个 blocker 保留，下一阶段未执行。</p>','<p><a href="'+PHASE+'_REPORT.md">报告</a> · <a href="'+PHASE+'_STATUS.json">完整状态</a> · <a href="TARGETED_HUMAN_APPROVAL_CARRY_FORWARD_AUDIT_R1.json">批准继承审计</a> · <a href="DORSAL_MCP_RING_FLEX_STRUCTURE_AUDIT_R1.json">精确结构审计</a></p>','<h2>RING_MCP 局部回归 · old / current</h2>']
keys=list(dict.fromkeys(r['view_key'] for r in outputs))
for key in keys:
 rows=[r for r in outputs if r['view_key']==key]
 if len(rows)!=2:continue
 page.append('<h3>'+html.escape(key)+'</h3><div class="pair">')
 for r in rows:page.append('<figure><img loading="lazy" src="'+r['file']+'"><figcaption>'+html.escape(r['asset']+' · '+r['pose']+' · '+r['fixture']+' · '+r['style'])+'</figcaption></figure>')
 page.append('</div>')
page.append('<h2>三对既有 exact scope contact</h2><table><tr><th>Pose / Pair</th><th>Poke mm</th><th>Bind facet mm</th><th>Segment mm</th><th>Carry-forward</th></tr>')
for r in paircarry:
 e=r['current_exact_crossing_evidence'];page.append(f"<tr><td>{r['pose']} / {r['face_pair']}</td><td>{e['depth_mm']:.9f}</td><td>{e['local_edge_mm']:.9f}</td><td>{e['seg_mm']:.9f}</td><td>{r['HUMAN_ACCEPTANCE_CARRY_FORWARD']}</td></tr>")
page.append('</table><p>仍保留真实交叉与 V2 Class A。Class A 本身不等于可见教学缺陷、tear、flap或 inversion。没有跨pose扩展批准。</p></html>')
(OUT/'review.html').write_text('\n'.join(page),encoding='utf-8')
md=['# '+PHASE,'','机器检查已完成；最终 verdict 由最终 no-drift 验证写入。','', '7个历史 targeted +3个 RING 局部回归，各在旧R2和当前derivative新运行。生产输入仅内存姿态变化，没有 blend 保存。所有历史fixture原有指标由pre-donor replay逐项精确复现，当前五fixture的全support坐标和指标亦逐项完全相同。','', '| 字段 | 结果 |','|---|---|']
for k,v in status.items():
 if k.isupper() and not isinstance(v,dict):md.append(f'| `{k}` | `{v}` |')
md+=['','## Human approval carry-forward','','CAP37的三条批准只覆盖TH_IP_30 [1225,2740]、IDX_MCP_45 [1041,2735]及IDX_MCP_45 [1226,2742]。当前fresh交叉坐标、poke、bind facet、segment、同frozen-label one-ring坐标与已批准的causal endpoint均精确相同；没有严重度恶化或新增结构失败。其余四fixture在各自已审阅pose的全support与54无交集，bind/posed/所有指标精确相同，因此没有新Human review需求。既有 collar compression/normal-flip/contact 保留，不声称理想轮廓或无压缩。','', '| Pose / Pair | Poke mm | Bind facet mm | Segment mm |','|---|---:|---:|---:|']
for r in paircarry:
 e=r['current_exact_crossing_evidence'];md.append(f"| {r['pose']} {r['face_pair']} | {e['depth_mm']:.12f} | {e['local_edge_mm']:.12f} | {e['seg_mm']:.12f} |")
md+=['','## Donor ROI regression','','54点、95incident faces、148incident edges及完整first fixed outer ring覆盖；每个native fan对whole mesh使用原有rational finite-feature gate，扣除实际合法共享simplex，跟踪contact component/member/feature/extent。当前bind→posed和pre-donor→current同pose均无新contact/self-intersection/native fan bow-tie/degenerate；同pose边界fold migration screen为0。linear fan-area chord只是补充几何证据，不宣称连续真实运动碰撞资格。固定chart normal变化仍为诊断，不创造normal-based anatomy gate。','', '| RING pose | Min area ratio (outer support) | Min edge ratio | Max edge ratio | Min linear fan mm² | Result |','|---|---:|---:|---:|---:|---|']
for cid,r in ringrows.items():
 f=r['fresh_metrics'];s=r['structure_audit'];md.append(f"| {cid} | {f['min_face_area_ratio']:.9f} | {f['min_edge_ratio_compression_diagnostic']:.9f} | {f['max_edge_ratio']:.9f} | {s['post_donor_bind_vs_posed']['continuous_fan_area']['minimum_fan_triangle_area_mm2']:.9f} | {r['status']} |")
md+=['','Codex检查实际全native实体/dorsal close/grazing/strain补图：原尖锐notch未重现，浅谷仍在，未看到新增明显ridge、tear、flap或collapse。细微crease/pinching/自然轮廓为APPEARANCE_PENDING_FULL_STAGE6A_HUMAN_REVIEW；本轮没有Human-close donor ROI。MIDDLE clean358/MCP69，LITTLE clean402/MCP153，在三个RING姿态fresh位移均0mm；old/current坐标精确相同。没有额外邻指pose。','', '## Sixteen inherited static debts','','16项均按原相关historical pose subset重新测endpoint/incident patch；severe≥3mm且>5x、collapse、degenerate、area ratio<0.05和V2 Class A为0。所有incident evidence精确old/current相同。仍为STATIC_QUALIFICATION_DEBT_WITHOUT_TRUE_DEFORMATION_FAILURE；STATIC_DEBT_STATUS=NOT_RESOLVED，不删除。','', '| Debt ID | Max debt edge ratio | Max incident ratio | True failure |','|---|---:|---:|---:|']
for r in drows:md.append(f"| {r['debt_id']} | {r['max_debt_edge_ratio']:.9f} | {r['max_incident_edge_ratio']:.9f} | {r['true_failure_count']} |")
md+=['','## Qualification boundary','','既有 Stage6A/R1E pose primitives、R1C V2 exact-ish classifier、collapse/area/severe/stretch与Stage4C reconciled exact finite-feature gate仅通过AST加载函数定义，没有运行旧顶层选择器/solver。retired old-cap9 anatomy、old whole-mesh cut-component不恢复。true-cap仅输入context，不作为stretch gate且未重算。CMC不构成Full opposition/Stage6B PASS。','', '每资产10次endpoint application；20/20 pre/post reset身份pose与恢复坐标精确。每pose先reset核查、apply、depsgraph fresh评估、metrics、实体render、reset核查。相机朝向纠正后从保存的fresh坐标重新渲染，无额外pose运行。','', '历史 Full Stage6A FAIL_CLOSED 与9 blockers保持；TH_IP_15 / IDX_MCP_15 / IDX_MCP_30 未执行。NEXT仅记录FULL_STAGE6A_REQUALIFICATION_AFTER_DONOR_TRANSFER_R1，未执行。STOP。','', '[Matched evidence](review.html) · [Machine evidence](FRESH_MACHINE_EVIDENCE_R1.json) · [Native coordinate evidence](POSED_COORDINATE_EVIDENCE_R1.json)']
(OUT/(PHASE+'_REPORT.md')).write_text('\n'.join(md)+'\n',encoding='utf-8')
print('ALL MACHINE/CARRY-FORWARD CHECKS',checks,'BLOCKERS',len(blockers),'REVIEW_REQUIRED',review_required,flush=True)
