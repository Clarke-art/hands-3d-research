from common import *
from datetime import datetime,timezone
frozen=read(OUT/'FROZEN_INPUT_NATIVE_PAYLOADS_R1.json')
reopened={k:read(OUT/(k+'_REOPENED_NATIVE_PAYLOAD_R1.json')) for k in ASSETS}
prop=read(OUT/'STAGE5_BEFORE_SAVE_PROPAGATION_PAYLOADS_R1.json')
recovery=read(OUT/'STAGE5_CURRENT_LINEAGE_INPUT_RECOVERY_R1.json')
assert recovery['status']=='PASS'
for k,p in inputs().items():assert sha(p)==EXPECTED[k]
assert read(OUT/'STAGE5_INPUT_PAYLOAD_PREFLIGHT_R1.json')['status']=='PASS'
geometry={k:read(OUT/('STAGE5A_GEOMETRY_PROPAGATION_AUDIT_R1.json' if k=='CORRECTED' else 'STAGE5B_R2_GEOMETRY_PROPAGATION_AUDIT_R1.json')) for k in ASSETS}
save={k:read(OUT/(k+'_SAVE_REOPEN_RESULT_R1.json')) for k in ASSETS}
smoke={k:read(OUT/(k+'_ZERO_EVAL_SMOKE_RESULT_R1.json')) for k in ASSETS}
roll={k:read(OUT/(k+'_NATIVE_ROLL_EQUIVALENCE_R1.json')) for k in ASSETS}
rig={};weights={}
for k,s in reopened.items():
 assert s['protected']==frozen[k]['protected']
 assert s['coordinates_local_m']==frozen['STAGE4']['coordinates_local_m']
 assert save[k]['status']==geometry[k]['status']==roll[k]['status']=='PASS'
 assert smoke[k]['ZERO_EVAL_SMOKE']=='PASS'
 assert ref(ASSETS[k])==prop[k]['asset']
 bones=next(iter(s['protected']['rigs'].values()))['bones']
 rig[k]={'status':'PASS','bone_count':len(bones),'native_bone_names_order_hierarchy_head_tail_matrices_frames_flags_exact':True,
 'object_and_armature_transforms_exact':True,'all_original_custom_properties_and_constraints_exact':True,
 'BONE_PAYLOAD_DELTA':0,'JOINT_PAYLOAD_DELTA':0,'ROLL_PAYLOAD_DELTA':0,
 'source_rig_payload_sha256':digest(frozen[k]['protected']['rigs']),'derived_rig_payload_sha256':digest(s['protected']['rigs']),
 'explicit_native_roll_equivalence':roll[k],
 'corrected_thumb_unchanged':{name:{'head_local_m':bones[name]['head_local_m'],'tail_local_m':bones[name]['tail_local_m'],'matrix_local':bones[name]['matrix_local'],'native_roll_rad':next(iter(roll[k]['reopened_native_rolls'].values()))[name]} for name in ('THUMB_IP_R','THUMB_TIP_R')}}
 assert len(bones)==21
 scalars=sum(len(v) for v in s['protected']['weights_exact_including_zero'])
 zeros=sum(g[1]==0 for v in s['protected']['weights_exact_including_zero'] for g in v)
 weights[k]={'status':'PASS','vertex_vector_count':3416,'exact_including_zero_entry_count':scalars,'explicit_zero_entry_count':zeros,
 'weight_scalar_drift':0,'GROUP_SET_ORDER_UNCHANGED':'PASS','group_count':len(s['protected']['groups']),'group_order':[g[1] for g in s['protected']['groups']],
 'source_exact_weight_payload_sha256':digest(frozen[k]['protected']['weights_exact_including_zero']),
 'derived_exact_weight_payload_sha256':digest(s['protected']['weights_exact_including_zero']),
 'positive_weight_vector_sha256':digest(s['positive_weight_vectors']),
 'edge5879_native_endpoints':s['protected']['mesh']['edges'][5879][1],
 'edge5879_weights_unchanged':{str(i):s['positive_weight_vectors'][i] for i in s['protected']['mesh']['edges'][5879][1]},
 'qualification':'Payload inheritance only; cap37/old_cap9/FIRST_WEB/317 and 16 inherited static debts not requalified'}
assert weights['R2']['positive_weight_vector_sha256']==WEIGHT_HASH
dump('STAGE5_RIG_PAYLOAD_EQUIVALENCE_R1.json',{'status':'PASS','paths':rig,'rig_rebuild_joint_locator_roll_recalculation_or_slot_application_run':False})
dump('STAGE5_WEIGHT_PAYLOAD_EQUIVALENCE_R1.json',{'status':'PASS','paths':weights,'R2_authority_positive_vector_sha256':WEIGHT_HASH,'any_weight_group_creation_normalization_smoothing_solver_or_rebinding_run':False})

authority=read(APP/'APPLICATION_AUTHORITY_INTERSECTION_AUDIT_R1.json')
counts={'cap37':37,'old_cap9':9,'FIRST_WEB21':21,'fresh_R3_protected_domain':962,'historical317_weight_universe':317}
sets={}
for name,n in counts.items():
 s=authority['sets'][name];ids=s['frozen_vertex_ids'];p=ROOT/s['source']['path']
 assert sha(p)==s['source']['sha256']
 assert len(ids)==len(set(ids))==s['membership_count']==n
 assert digest(ids)==s['membership_sha256']
 assert all(all(s2['protected']['mesh']['vertex_ids'][i]==i for i in ids) for s2 in reopened.values())
 sets[name]={'membership_count':n,'frozen_native_vertex_ids':ids,'membership_sha256':digest(ids),'authority':ref(p),'each_derived_mapping_count':{k:n for k in ASSETS},'ID_set_or_membership_drift':0,'only_ID_consistency_checked':True}
dump('STAGE5_AUTHORITY_ID_MEMBERSHIP_AUDIT_R1.json',{'status':'PASS','receipt':ref(APP/'APPLICATION_AUTHORITY_INTERSECTION_AUDIT_R1.json'),'sets':sets,'authority_research_or_solve_run':False})
dump('STAGE5_SAVE_REOPEN_AUDIT_R1.json',{'status':'PASS','separate_factory_startup_processes':True,'paths':save,'serialization_drift':0,'R2_reopened_all3416_positive_weight_vector_sha256':weights['R2']['positive_weight_vector_sha256']})
dump('STAGE5_ZERO_EVAL_SMOKE_R1.json',{'ZERO_EVAL_SMOKE':'PASS','paths':smoke,'NOT_REST_ZERO_BIND_REQUALIFICATION':True,'posed_Stage6_tests_run':[]})
dump('JOINT_SURFACE_DELTA_DIAGNOSTIC_R1.json',{'classification':'DIAGNOSTIC_ONLY','paths':{k:read(OUT/(k+'_JOINT_SURFACE_DELTA_DIAGNOSTIC_R1.json')) for k in ASSETS},'formal_joint_surface_rest_zero_bind_qualification':'NOT_RUN','joints_or_rolls_changed':False})

old=read(OUT/'PROTECTED_HISTORY_HASHES_BEFORE.json');after=inventory()
changed=[p for p,h in old.items() if after.get(p)!=h]
added=sorted(set(after)-set(old));removed=sorted(set(old)-set(after))
history={'status':'PASS' if not changed and not added and not removed else 'FAIL_CLOSED_STAGE5_GEOMETRY_PROPAGATION','protected_file_count':len(old),'all_workspace_files_hashed':True,'sole_exclusion':str(OUT),'changed_paths':changed,'new_files_outside_phase_directory':added,'removed_paths':removed,'PROTECTED_HISTORY_DRIFT':len(changed),'before_manifest_sha256':sha(OUT/'PROTECTED_HISTORY_HASHES_BEFORE.json'),'source_assets_receipts_authorities_and_all_deformation_artifacts_byte_identical':not changed}
dump('PROTECTED_HISTORY_HASHES_AFTER.json',after)
dump('PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json',history)
assert history['status']=='PASS',history
fullp=ROOT/'production_spec/stage6_deformation/full_stage6a_requalification_r1/FULL_STAGE6A_REQUALIFICATION_R1_STATUS.json'
full=read(fullp)
assert full['FULL_STAGE6A_REQUALIFICATION_R1']=='FAIL_CLOSED_FULL_STAGE6A_REQUALIFICATION' and full['MACHINE_HARD_BLOCKER_COUNT']==9
status={'phase':PHASE,'recorded_at_utc':datetime.now(timezone.utc).isoformat(),
 'NEW_STAGE4C_SOURCE':str(STAGE4),'NEW_STAGE4C_SOURCE_SHA256':sha(STAGE4),
 'CORRECTED_RIG_SOURCE_PATH':str(inputs()['CORRECTED']),'CORRECTED_RIG_SOURCE_SHA256':sha(inputs()['CORRECTED']),
 'R2_SOURCE_PATH':str(R2),'R2_SOURCE_SHA256':sha(R2),'R2_SOURCE_WEIGHT_HASH':WEIGHT_HASH,
 'NEW_STAGE5A_DERIVED_PATH':str(ASSETS['CORRECTED']),'NEW_STAGE5A_DERIVED_SHA256':sha(ASSETS['CORRECTED']),
 'NEW_STAGE5B_R2_DERIVED_PATH':str(ASSETS['R2']),'NEW_STAGE5B_R2_DERIVED_SHA256':sha(ASSETS['R2']),
 'NEW_STAGE4C_SOURCE_HASH_VERIFIED':'PASS','CORRECTED_RIG_INPUT_HASH_VERIFIED':'PASS','R2_INPUT_HASH_VERIFIED':'PASS',
 'STAGE5A_GEOMETRY_EQUALS_NEW_STAGE4C':'PASS','STAGE5B_R2_GEOMETRY_EQUALS_NEW_STAGE4C':'PASS',
 'STAGE4C_TO_STAGE5A_VERTEX_MAX_DELTA_MM':0.0,'STAGE4C_TO_STAGE5B_R2_VERTEX_MAX_DELTA_MM':0.0,
 'OLD_TO_NEW_STAGE5A_CHANGED_VERTEX_COUNT':54,'OLD_TO_NEW_R2_CHANGED_VERTEX_COUNT':54,
 'OUTSIDE54_STAGE5A_GEOMETRY_DRIFT':0,'OUTSIDE54_R2_GEOMETRY_DRIFT':0,
 'FULL_NATIVE_COORDINATE_MATCH_COUNT_EACH':3416,'NATIVE_V_E_F_EACH':[3416,6828,3414],
 'BONE_PAYLOAD_DELTA':0,'JOINT_PAYLOAD_DELTA':0,'NATIVE_ROLL_PAYLOAD_DELTA':0,
 'R2_WEIGHT_VECTOR_HASH_AFTER_PROPAGATION':weights['R2']['positive_weight_vector_sha256'],'R2_WEIGHT_VECTOR_HASH_MATCH':'PASS',
 'GROUP_SET_ORDER_UNCHANGED':'PASS','WEIGHT_SCALAR_DRIFT_INCLUDING_ZERO':0,
 'TOPOLOGY_DRIFT':0,'UV_DRIFT':0,'MATERIAL_DRIFT':0,'SMOOTH_SHARP_CUSTOM_NORMAL_STATE_DRIFT':0,
 'MODIFIER_BINDING_UNCHANGED':'PASS','AUTHORITY_ID_MEMBERSHIP_UNCHANGED':'PASS','ZERO_EVAL_SMOKE':'PASS','SAVE_REOPEN':'PASS','SERIALIZATION_DRIFT':0,'PROTECTED_HISTORY_DRIFT':0,
 'PROTECTED_PREEXISTING_FILE_COUNT':len(old),'NEW_FILES_OUTSIDE_PHASE_DIRECTORY':0,
 'FULL_STAGE6A_STATUS_RETAINED':full['FULL_STAGE6A_REQUALIFICATION_R1'],'MACHINE_HARD_BLOCKER_COUNT_RETAINED':full['MACHINE_HARD_BLOCKER_COUNT'],'full_stage6a_retained_evidence':ref(fullp),
 'STAGE5_GEOMETRY_PROPAGATION_VERDICT':'PASS_GEOMETRY_PROPAGATED_WITH_RIG_AND_WEIGHTS_FROZEN',
 'JOINT_SURFACE_DELTA_DIAGNOSTIC':'DIAGNOSTIC_ONLY','JOINT_TO_SURFACE_REQUALIFICATION':'NOT_RUN','REST_ZERO_BIND_REQUALIFICATION':'NOT_RUN','STATIC_SKIN_REQUALIFICATION':'NOT_RUN','TRUE_CAP_REQUALIFICATION':'NOT_RUN','TARGETED_DEFORMATION':'NOT_RUN','FULL42_RERUN':'NOT_RUN','STAGE6B_STARTED':False,'PRODUCTION_PROMOTION':'NO',
 'NEXT':'JOINT_SURFACE_REST_ZERO_BIND_REVALIDATION_AFTER_DONOR_TRANSFER_R1','NEXT_EXECUTED':False,'STOP':True}
dump(PHASE+'_STATUS.json',status)
lines=['# '+PHASE,'',status['STAGE5_GEOMETRY_PROPAGATION_VERDICT'],'',
 '仅从三个已校验输入传播完整 3416 点的 native stored geometry。Corrected rig 从工作区全部 36 个 `.blend` 的实际 SHA256 唯一恢复；没有回退到 historical rig。两个新资产分别由各自正式 Stage5 来源打开、赋值全部坐标后独立保存，原资产未覆盖。','',
 '两个资产的 3416 / 3416 local 与 world 坐标均精确匹配实际新 Stage4C；相对各自旧资产恰好改变同一 approved54，outside54 为 0。V/E/F、native IDs、edge endpoints、face cycles 和 loops 完全相同。','',
 '各自完整非几何快照逐值相等：21 bones、原 hierarchy、head/tail、matrix/rest frame、inherit flags、实际 EditBone.roll、pose channels、object/armature transforms、原 custom properties、约束、groups/order、所有含零 weight entries、UV、材料 slots/assignments/node settings/links、modifier settings/bindings、smooth/sharp 与 custom-normal state。R2 的 16 groups、3416 weight vectors 的 authority hash 在保存重开后不变。历史 R2 rig provenance 与 corrected 源的差异按各自来源保留。','',
 '实际 roll 只在输入提取与重开检查的最后一步进入 EDIT 读取；无 edit setter、无 roll 计算、无退出 EDIT 或保存该临时会话。传播保存过程从不进入 armature EDIT。两个资产分别通过独立 factory-startup 进程重开，完整快照 serialization drift = 0。','',
 'JOINT_SURFACE_DELTA_DIAGNOSTIC 记录每个固定 joint head/tail 到旧、新 raw mesh 同一 native-index fan triangulation 的最近距离，仅为 DIAGNOSTIC_ONLY，没有门槛、正式资格 verdict 或移动 joint。Zero evaluation 仅在临时内存清零 pose channels 并检查有限值、已有 modifier/group/bone references；不保存，不做 rest/zero/bind 资格判定。未运行任何 Stage6 pose。','',
 'cap37 / old cap9 / FIRST_WEB21 / fresh R3 962 / historical317 仅检查 frozen ID membership。9 个 Stage6A blockers 保留原 FAIL_CLOSED；没有重跑、修复、裁决或分类。全工作区 '+str(len(old))+' 个先前文件 SHA256 保持原样，新文件仅在本目录。','',
 '## 完整字段','', '| 字段 | 结果 |','|---|---|']
for k,v in status.items():
 if isinstance(v,dict):v=json.dumps(v,ensure_ascii=False)
 lines.append('| '+k+' | '+str(v).replace('|','\\|')+' |')
lines+=['','## 证据','']
for n in ['STAGE5_CURRENT_LINEAGE_INPUT_RECOVERY_R1.json','STAGE5_INPUT_PAYLOAD_PREFLIGHT_R1.json','STAGE5A_GEOMETRY_PROPAGATION_AUDIT_R1.json','STAGE5B_R2_GEOMETRY_PROPAGATION_AUDIT_R1.json','STAGE5_RIG_PAYLOAD_EQUIVALENCE_R1.json','STAGE5_WEIGHT_PAYLOAD_EQUIVALENCE_R1.json','STAGE5_AUTHORITY_ID_MEMBERSHIP_AUDIT_R1.json','STAGE5_ZERO_EVAL_SMOKE_R1.json','STAGE5_SAVE_REOPEN_AUDIT_R1.json','JOINT_SURFACE_DELTA_DIAGNOSTIC_R1.json','PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json']:
 lines.append('- ['+n+'](<'+str(OUT/n).replace('\\','/')+'>)')
lines+=['','NEXT = '+status['NEXT']+'，只记录，不执行。PRODUCTION_PROMOTION = NO。STOP。','']
(OUT/(PHASE+'_REPORT.md')).write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps({k:status[k] for k in ('STAGE5_GEOMETRY_PROPAGATION_VERDICT','NEW_STAGE5A_DERIVED_SHA256','NEW_STAGE5B_R2_DERIVED_SHA256','PROTECTED_PREEXISTING_FILE_COUNT','PROTECTED_HISTORY_DRIFT','STOP')}))
