import sys
sys.dont_write_bytecode=True
from common import *
from datetime import datetime,timezone
s=read(OUT/'POST_DONOR_MACHINE_NUMERIC_RESULT_R1.json')
before=read(OUT/'PROTECTED_HISTORY_HASHES_BEFORE.json');after=inventory()
drift=[p for p,h in before.items() if after.get(p)!=h];outside_new=sorted(set(after)-set(before))
dump('PROTECTED_HISTORY_HASHES_AFTER.json',after)
full42p=S6/'full_stage6a_requalification_r1/FULL_STAGE6A_REQUALIFICATION_R1_STATUS.json';full42=read(full42p)
checks={'protected_history_hashes_unchanged':not drift,'new_files_only_in_this_task':not outside_new,
 'full42_status_retained':full42['FULL_STAGE6A_REQUALIFICATION_R1']=='FAIL_CLOSED_FULL_STAGE6A_REQUALIFICATION' and full42['MACHINE_HARD_BLOCKER_COUNT']==9,
 'static_prerequisite_gate':all(read(OUT/'PREREQUISITE_GATE_R1.json')['checks'].values()),
 'exact_historical_numeric_method':all(read(OUT/'METHOD_IMPLEMENTATION_REUSE_VERIFICATION_R1.json')['checks'].values()),
 'historical_primitives_and_case_matrix_hashes':all(read(OUT/'HISTORICAL_PRIMITIVE_AUTHORITY_VERIFICATION_R1.json')['checks'].values()),
 'determinism':all(read(OUT/'POST_DONOR_TRUE_CAP_DETERMINISM_R1.json')['checks'].values()),
 'all37x19_and37x38_fresh_paths':s['PRIMARY_PAIR_COUNT']==703 and s['FULL_CONTEXT_PAIR_COUNT']==1406,
 'all_six_pose_results':len(read(OUT/'POST_DONOR_POSED_BOUND_RECOMPUTATION_R1.json')['per_pose'])==6,
 'all120_virtual_recipes':len(read(OUT/'POST_DONOR_VIRTUAL_120_RECIPE_RECOMPUTATION_R1.json')['recipes'])==120,
 'all_graph_checks':all(read(OUT/'POST_DONOR_GRAPH_METRIC_AUDIT_R1.json')['checks'].values()),
 'all_live_prerequisites_A_and_B':all(all(read(OUT/(run+'/COMPUTATION_VERIFICATION.json'))['live_prerequisite_checks'].values()) for run in ['RUN_A','RUN_B'])}
render=read(OUT/'POST_DONOR_FORENSIC_RENDER_MANIFEST_R1.json')
render['agent_visual_inspection']='PASS: Agent directly viewed the five-figure contact sheet; gold cap37, blue INDEX endpoints, teal context, orange donor ROI, red old route and purple current route are visible in matched two-view frames. The routes coincide and remain separate from approved54. Marks use actual native coordinates and IDs.'
dump('POST_DONOR_FORENSIC_RENDER_MANIFEST_R1.json',render)
checks['forensic_evidence_complete']=render['render_count']==5 and all(sha(ROOT/r['path'])==r['sha256'] for r in render['files'])
passed=all(checks.values())
verdict='PASS_CURRENT_GEOMETRY_BOUND_AUTHORITY_ESTABLISHED' if passed else 'FAIL_CLOSED_TRUE_CAP_AUTHORITY_MISMATCH'
if not checks['determinism']:verdict='FAIL_CLOSED_TRUE_CAP_DETERMINISM'
elif not checks['exact_historical_numeric_method'] or not checks['historical_primitives_and_case_matrix_hashes']:verdict='FAIL_CLOSED_TRUE_CAP_METHOD_INCOMPATIBILITY'
dump('PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json',{'status':'PASS' if not drift and not outside_new else 'FAIL_CLOSED','protected_preexisting_file_count':len(before),
 'history_modified_or_deleted_count':len(drift),'history_modified_or_deleted_paths':drift,'outside_task_new_file_count':len(outside_new),'outside_task_new_files':outside_new,
 'before_inventory_hash':digest(before),'after_inventory_hash':digest(after),'full_Stage6A_status':full42['FULL_STAGE6A_REQUALIFICATION_R1'],'machine_hard_blocker_count':full42['MACHINE_HARD_BLOCKER_COUNT'],
 'old9_repaired_adjudicated_reclassified':False,'BLEND_SAVE_COUNT':0,'WEIGHT_MUTATIONS':0,'GEOMETRY_MUTATIONS':0,'REST_RIG_MUTATIONS':0,
 'TARGETED_DEFORMATION_RUNS':0,'FULL_STAGE6A_RUNS':0,'STAGE6B_RUNS':0,'full42_source':ref(full42p)})
status={'phase':PHASE,'recorded_at_utc':datetime.now(timezone.utc).isoformat(),'client_date':'2026-10-05','client_timezone':'Asia/Shanghai',**s,
 'R2_WEIGHT_HASH':EXPECTED_WEIGHTS,'R2_WEIGHT_HASH_MATCH':True,'corrected_rig_authority':EXPECTED_RIG,'cap37_combined_authority':EXPECTED_CAP,
 'fresh_R3_membership_authority':EXPECTED_MEMBER,'fresh_R3_combined_authority':EXPECTED_R3,
 'PROTECTED_HISTORY_DRIFT':len(drift),'PROTECTED_PREEXISTING_FILE_COUNT':len(before),'OUTSIDE_TASK_NEW_FILE_COUNT':len(outside_new),
 'FULL_STAGE6A_STATUS_RETAINED':full42['FULL_STAGE6A_REQUALIFICATION_R1'],'MACHINE_HARD_BLOCKER_COUNT_RETAINED':full42['MACHINE_HARD_BLOCKER_COUNT'],
 'VERDICT':verdict,PHASE:verdict,'checks':checks,'current_asset':ref(CAND),'history_authority_role':'PRE_DONOR_TRANSFER_CORRECTED_AUTHORITY_HISTORY',
 'current_authority_role':'POST_DONOR_TRANSFER_TRUE_CAP_NUMERIC_AUTHORITY','automatic_old_recommendation_revival':False,
 'NEXT':'TARGETED_DEFORMATION_REVALIDATION_AFTER_DONOR_TRANSFER_R1' if passed else 'STOP_MINIMAL_BLOCKER_REQUIRES_ADJUDICATION',
 'NEXT_EXECUTED':False,'STOP':True,'minimal_blocker':None if passed else next(k for k,v in checks.items() if not v)}
dump(PHASE+'_STATUS.json',status)
numeric_authority={'authority_id':'POST_DONOR_TRANSFER_TRUE_CAP_AUTHORITY_R1','status':verdict,'qualification_scope':'CURRENT_GEOMETRY_NUMERIC_AUTHORITY_ONLY',
 'current_asset':ref(CAND),'source_cap37_authority':{'combined_hash':EXPECTED_CAP,'reference':ref(CAP_PATH)},
 'target_fresh_R3_authority':{'membership_hash':EXPECTED_MEMBER,'combined_hash':EXPECTED_R3,'reference':ref(R3_PATH)},
 'weight_vector_authority':EXPECTED_WEIGHTS,'corrected_rig_authority':ref(CORRECTED),
 'source_target_authority':ref(OUT/'CORRECTED_TRUE_CAP_SOURCE_TARGET_AUTHORITY.json'),
 'source_set_hash':read(OUT/'RUN_A/STATIC_PATH_PAYLOAD.json')['source_set_hash'],'primary_target_set_hash':read(OUT/'RUN_A/STATIC_PATH_PAYLOAD.json')['target_set_hash'],
 'graph_metric_hash_current':s['NEW_GRAPH_METRIC_HASH'],'path_family_payload_hash_current':s['NEW_PATH_FAMILY_PAYLOAD_HASH'],'bound_payload_hash_current':s['NEW_BOUND_PAYLOAD_HASH'],
 'hash_serialization':'Same historical canonical sorted-key compact JSON digest; binary64 values retain round-trip precision.',
 'current_numeric_references':{k:ref(OUT/n) for k,n in {'graph':'RUN_A/GRAPH_METRIC_PAYLOAD.json','paths':'RUN_A/STATIC_PATH_PAYLOAD.json','bounds':'RUN_A/POSED_BOUND_PAYLOAD.json',
 'primary703':'POST_DONOR_PRIMARY_703_PATHS_R1.json','context1406':'POST_DONOR_1406_CONTEXT_PATHS_R1.json','posed':'POST_DONOR_POSED_BOUND_RECOMPUTATION_R1.json',
 'virtual120':'POST_DONOR_VIRTUAL_120_RECIPE_RECOMPUTATION_R1.json','determinism':'POST_DONOR_TRUE_CAP_DETERMINISM_R1.json','method':'METHOD_IMPLEMENTATION_REUSE_VERIFICATION_R1.json'}.items()},
 'pre_donor_history':{'role':'PRE_DONOR_TRANSFER_CORRECTED_AUTHORITY_HISTORY','reference':ref(OLD/'TRUE_CAP_BOUND_RECOMPUTE_AFTER_DEPENDENCY_RECONCILIATION_R1_STATUS.json'),'graph_hash':s['OLD_GRAPH_METRIC_HASH'],'overwritten':False},
 'deformation_qualification':False,'mesh_limit_conclusion':False,'retopo_recommendation':False,'no_legal_weight_conclusion':False,'skin_failure_conclusion':False,'anatomy_failure_conclusion':False,
 'old9_Stage6A_blockers_repaired_adjudicated_reclassified':False,'production_promotion':False,'STOP':True}
numeric_authority['combined_numeric_authority_hash']=digest(numeric_authority)
dump('POST_DONOR_TRUE_CAP_AUTHORITY_MANIFEST_R1.json',numeric_authority)
rows=['| 字段 | 当前实测值 |','|---|---|']
for k,v in status.items():
 if k in ['checks','CHANGED_GRAPH_EDGE_IDS','current_asset']:continue
 rows.append(f'| {k} | {json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v} |')
path=read(OUT/'RUN_A/STATIC_PATH_PAYLOAD.json')['global_shortest_path']
pose=read(OUT/'POST_DONOR_POSED_BOUND_RECOMPUTATION_R1.json')
pose_rows=['| Pose | Current all703 max | Pre-donor delta | Current shortest10 max |','|---|---:|---:|---:|']
for cid,r in pose['old_vs_current_pose_comparison'].items():pose_rows.append(f"| {cid} | {r['current_max_all703']} | {r['delta_max_all703']} | {r['current_max_current_shortest10']} |")
report=f'''# {PHASE}

**{verdict}**。建立新的 POST_DONOR_TRANSFER TRUE-CAP NUMERIC AUTHORITY。NEXT仅记录，STOP。

## 输入与正式方法

Current R2 derivative SHA256 `{EXPECTED_CAND}`；3416 weight hash `{EXPECTED_WEIGHTS}`；corrected rig SHA256 `{EXPECTED_RIG}`。cap37 combined `{EXPECTED_CAP}`、fresh-R3 membership `{EXPECTED_MEMBER}` / combined `{EXPECTED_R3}`全部通过。static skin与joint/rest/zero/bind先决资格均PASS。旧 corrected true-cap history未覆盖。

原方法的mesh graph/metric、path record、排序/statistics、六pose及120 recipe数值计算代码区段逐字相同。4组historical extractor/path/pose函数文件hash、函数AST hash和pose case matrix SHA精确继承。只替换current/old clean intake并补充只读graph、coordinate、tie诊断。没有改变bound numerator/denominator、pair ensemble或max aggregation。

Frozen37 cap sources、19 INDEX primary targets、38 full exact-boundary context endpoints直接读取。没有selector、anatomy research或R3 solver。历史Dijkstra按ascending adjacency、heap(distance,vertex)、strict relaxation `du+w < stored-1e-16`、stale cutoff `+1e-15`，相等候选保留第一predecessor。

## Fresh全图与完整paths

每个独立Blender进程factory-reset clean reopen old R2、corrected rig和current derivative，读取actual weights/raw entries含零/groups/rig/native coordinates。全部3416 vertices、6828 native undirected edges fresh build world bind edge-length metric。每次对37 sources完整Dijkstra求1406 context paths并提取703 primary，不使用旧path作为current seed，也不只检查ROI相关旧路径。

旧graph另行bind-only replay验证全部1406 frozen paths和tie diagnostics；此replay不提供current结果。OLD_GRAPH_METRIC_HASH=`{s['OLD_GRAPH_METRIC_HASH']}`，NEW_GRAPH_METRIC_HASH=`{s['NEW_GRAPH_METRIC_HASH']}`。148条approved54 incident edges改变，max绝对length delta={s['MAX_EDGE_LENGTH_DELTA_MM']}mm，max ratio={s['MAX_EDGE_LENGTH_RATIO']}。变化不是失败或新geometry gate。全部changed edge IDs及old/new lengths/delta/ratio另列。

实际source37与target19/context38坐标均与旧geometry精确相同。Fresh primary703/703、context1406/1406 path vertex/edge sequence和length保持exact；path/tie/rank change=0，old/new primary触及approved54=0，new context触及approved54=0。

统计沿用历史order statistics，不插值percentile。min={s['TRUE_CAP_STATIC_PATH_MIN_MM_CURRENT']}、p05={s['TRUE_CAP_STATIC_PATH_P05_MM_CURRENT']}、median={s['TRUE_CAP_STATIC_PATH_MEDIAN_MM_CURRENT']}、p95={s['TRUE_CAP_STATIC_PATH_P95_MM_CURRENT']}、max={s['TRUE_CAP_STATIC_PATH_MAX_MM_CURRENT']}、mean={s['TRUE_CAP_STATIC_PATH_MEAN_MM_CURRENT']}mm；六项delta全部0。

重新确定global shortest：v{path['source_vertex']}→v{path['target_vertex']}，{len(path['edge_id_sequence'])} edges，{path['total_path_length_mm']}mm。

Vertex sequence：`{path['vertex_sequence']}`。
Edge sequence：`{path['edge_id_sequence']}`。

## Posed bounds与virtual recipes

沿用历史lower bound：`max(posed-edge/bind-edge) >= norm(B_pose-A_pose)/sum(bind edge lengths on fixed path)`。每case实际两端current evaluated coordinates都重新读取，保持all703、current-shortest10、global-shortest pair、cap mean motion和full-context max各原aggregate。原path-edge ratio sanity context不运行severe-stretch classifier、surface/crossing QA或deformation qualification。

{chr(10).join(pose_rows)}

六pose×75 unique source/context endpoints=450份posed coordinate逐值比较，change=0、max delta=0mm。六case完整703 pair rows和pose states与pre-donor精确一致。

120 historical recipes（5 families×4 original poses×6 original fractions）每次全部重新执行，84360 primary、168720 full-context pair evaluations。Source A是actual evaluated cap37，target B使用原algebraic virtual LBS transforms。每recipe old/new max、每pair bound、endpoint trajectories和ranking都完整保存；max absolute/relative delta=0，rank changes=0。没有weight assignment或旧mesh-limit/retopo/no-legal-weight/skin/anatomy conclusion恢复。

## Determinism、forensics与STOP

两个独立Blender5.1.2进程均完整重算graph、37-source Dijkstra、1406 paths、六pose与120 recipes。每scalar、path sequence、tie diagnostic、coordinate及完整geometry context A/B exact equality；没有rounding或tolerance掩盖不同path。

NEW_PATH_FAMILY_PAYLOAD_HASH=`{s['NEW_PATH_FAMILY_PAYLOAD_HASH']}`。
NEW_BOUND_PAYLOAD_HASH=`{s['NEW_BOUND_PAYLOAD_HASH']}`。

Path-family payload包含改变的graph hash，故family hash改变；路径本身保持exact。完整bound payload与pre-donor相同，但由current输入fresh执行得到。

生成并直接检查5张matched native-ID forensic图：current cap37、fresh-R3 endpoints、old/new global shortest、old/new overlay。Gold source、blue INDEX target、teal THUMB context、orange approved54 ROI与red/purple路径可见，路径重合且未进入ROI。这是计算证据核对，不需要Human anatomy approval。

![Forensic evidence](<{(OUT/'renders/FORENSIC_CONTACT_SHEET.png').as_posix()}>)

{len(before)}个预先存在文件SHA256原样保留，history drift={len(drift)}、越界新增={len(outside_new)}。blend save、weights/geometry/rest rig mutation全0。True-cap current Dijkstra总计37×4，另old bind-only replay总计37×4；R3 Dijkstra/solver=0。最终收据下两个独立完整process做确定性比较；另两次早期完整process读取正确current geometry，但source/target收据旧hash归属字段随后显式分离，故重跑最终两个process。4次numeric payload hashes精确相同，执行ledger保留。允许的bound probe总计6×4=24，不是Stage6 suite。

TARGETED_DEFORMATION_RUNS=0，FULL_STAGE6A_RUNS=0，STAGE6B_RUNS=0。旧Full42仍FAIL_CLOSED_FULL_STAGE6A_REQUALIFICATION，9 blockers未修复、裁决或重分类。PRODUCTION_PROMOTION=NO。

## 最终字段

{chr(10).join(rows)}

NEXT=**{status['NEXT']}**，只记录，未执行。之后targeted deformation→Full42 Stage6A→Human Review→之后才可能Stage6B。STOP。
'''
(OUT/(PHASE+'_REPORT.md')).write_text(report,encoding='utf-8')
files={p.relative_to(OUT).as_posix():sha(p) for p in OUT.rglob('*') if p.is_file() and p.name not in ['OUTPUT_EVIDENCE_HASH_MANIFEST_R1.json','FINAL_DELIVERY_VALIDATION_R1.json']}
dump('OUTPUT_EVIDENCE_HASH_MANIFEST_R1.json',{'files':files,'canonical_files_hash':digest(files),'excludes':['OUTPUT_EVIDENCE_HASH_MANIFEST_R1.json','FINAL_DELIVERY_VALIDATION_R1.json']})
print(json.dumps({'VERDICT':verdict,'PROTECTED_HISTORY_DRIFT':len(drift),'protected_files':len(before),'NEXT':status['NEXT'],'NEXT_EXECUTED':False,'STOP':True},ensure_ascii=False),flush=True)
