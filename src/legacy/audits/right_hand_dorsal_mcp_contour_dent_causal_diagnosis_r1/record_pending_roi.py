"""Preserve independent findings while waiting for the required exact ROI location.
Never manufacture a dent membership or causal conclusion from an ambiguous label.
"""
import sys
sys.dont_write_bytecode=True
from common import *
I=read(OUT/'LINEAGE_INPUT_STATE_VERIFICATION_R1.json')
status={'phase':PHASE,'RIGHT_HAND_DORSAL_MCP_CONTOUR_DENT':'PRODUCTION_BLOCKER_PENDING_CAUSAL_DIAGNOSIS','CAUSAL_DIAGNOSIS_STATUS':'FAIL_CLOSED_DENT_CAUSE_UNRESOLVED','continuation_state':'WAITING_FOR_HUMAN_ROI_LOCATION_CONFIRMATION','DENT_VISIBLE_IN_STAGE4C_RAW':'UNRESOLVED_PENDING_CONFIRMED_ROI','DENT_VISIBLE_IN_RSSF':'HUMAN_CONFIRMED_REGION_NOT_YET_LOCALIZED','DENT_VISIBLE_IN_R2_BIND':'HUMAN_CONFIRMED_REGION_NOT_YET_LOCALIZED','DENT_VISIBLE_IN_IDX_MCP_15':'HUMAN_CONFIRMED_REGION_NOT_YET_LOCALIZED','EARLIEST_CONFIRMED_DENT_STAGE':'NOT_SET_PENDING_CONFIRMED_ROI','RAW_TO_BIND_GEOMETRY_DELTA':{'scope':'FULL_MESH_UPPER_BOUND_NOT_ROI_SPECIFIC','max_mm':I['stages']['R2_PRODUCTION']['max_raw_to_evaluated_on_mm']},'SHADING_CAUSAL':'UNRESOLVED_PENDING_CONFIRMED_ROI','ARMATURE_ZERO_POSE_CAUSAL':'NO_MEANINGFUL_ZERO_GEOMETRY_CHANGE_BEYOND_PREVIOUSLY_ESTABLISHED_FLOAT_NOISE','SKIN_CAUSAL':'UNRESOLVED_PENDING_CONFIRMED_ROI','POSE_AMPLIFICATION':'NOT_MEASURED_PENDING_CONFIRMED_ROI','ROOT_CAUSE_CLASS':'UNRESOLVED','TOPOLOGY_CHANGE_REQUIRED':'UNRESOLVED','RET0PO_REQUIRED':'UNRESOLVED','MINIMAL_REPAIR_LAYER':'NOT_SET_PENDING_CONFIRMED_ROI','PRODUCTION_DRIFT':0,'FULL_STAGE6A_REQUALIFICATION_R1':'FAIL_CLOSED_FULL_STAGE6A_REQUALIFICATION','severe_crossing_evidence_reclassified_or_modified_count':0,'Stage6A_rerun_count':0,'Stage6B_started':False,'repair_count':0,'NEXT':'HUMAN_CONFIRM_DENT_ROI_LOCATION_ONLY','minimum_unresolved_evidence':['Confirm the intended visible dent in the source IDX_MCP_15 FULL_SOLID bind panel: A=[410,159], B=[390,240], C=[345,257], or an exact textual image location. The instruction references a Human-marked region, but its attached text contains no mark.'],'final_causal_review_ready':False}
dump(PHASE+'_STATUS.json',status)
dump('DORSAL_MCP_DENT_ROI_R1.json',{'status':'NOT_ESTABLISHED_PENDING_HUMAN_LOCATION','anatomy_authority':False,'vertices':None,'faces':None,'edges':None,'1_ring':None,'2_ring':None,'source_image':ref(S6/'full_stage6a_requalification_r1/renders/IDX_MCP_15_FULL_SOLID.png'),'clarification_figure':ref(OUT/'ROI_LOCATION_CLARIFICATION.png'),'screen_points_draft_only':{'A':[410,159],'B':[390,240],'C':[345,257]},'vertices_guessed_from_text':False})
dump('DENT_STAGE_LINEAGE_COMPARISON_R1.json',{'status':'INPUT_LINEAGE_VERIFIED_ROI_COMPARISON_PENDING','input_checks':I,'frozen_Stage4A_R2_added_only_to_locate_introduction':True,'earliest_confirmed_dent_stage':None})
dump('DENT_GEOMETRY_VS_SHADING_R1.json',{'status':'NOT_RUN_PENDING_CONFIRMED_ROI','root_cause_class':'UNRESOLVED','source_custom_normals':{k:v['custom_normals'] for k,v in I['stages'].items()},'flat_normal_or_best_fit_counterfactual_applied':False})
dump('DENT_ARMATURE_ZERO_POSE_AUDIT_R1.json',{'status':'GLOBAL_INDEPENDENT_INPUT_CHECK_COMPLETE_ROI_DETAIL_PENDING','R2_full_mesh_max_off_to_on_mm':I['stages']['R2_PRODUCTION']['max_off_to_on_mm'],'R2_full_mesh_max_raw_to_bind_mm':I['stages']['R2_PRODUCTION']['max_raw_to_evaluated_on_mm'],'prior_Stage6A_float_noise_mm':5.9670092462157264e-05,'formal_gate_created':False,'Stage4C_and_current_R2_raw_coordinates_max_delta_mm':0,'meaningful_zero_pose_geometry_change_detected':False})
dump('DENT_POSE_AMPLIFICATION_R1.json',{'status':'NOT_MEASURED_PENDING_CONFIRMED_ROI','pose_ids_available':['BIND','IDX_MCP_15','IDX_MCP_30','IDX_MCP_45'],'source':'Frozen existing Stage6A coordinate artifact','new_pose_applications':0,'new_stage6_gates':0})
report='''# RIGHT_HAND_DORSAL_MCP_CONTOUR_DENT_CAUSAL_DIAGNOSIS_R1

FAIL_CLOSED_DENT_CAUSE_UNRESOLVED — exact visible ROI location confirmation pending.

The Human product requirement is recorded as PRODUCTION_BLOCKER_PENDING_CAUSAL_DIAGNOSIS. No new anatomy authority or repair authorization is inferred.

The source full solid image contains several distinct concavities. The instruction refers to a Human-marked region, but the supplied text contains no visual mark. A/B/C are screen-space clarification marks only, not anatomical or vertex memberships. In accordance with “不要根据文字猜具体 vertex”, no ROI vertices are guessed and no causal classification is manufactured.

## Completed independent work

- Identical 3416-vertex/6828-edge/3414-face topology identity verified from frozen Stage4A_R2, through Stage4B_RSSF_R2 and Stage4C_R2, to corrected Stage5A and current R2.
- Stage4C raw stored geometry is already RSSF. A “raw Stage4C” view is not a native pre-RSSF pose.
- Stage4C world coordinates and corrected Stage5A/current R2 raw world coordinates are exactly identical. Stage4B_RSSF differs only by 0.000003725290298 mm world-coordinate float noise.
- R2 Armature OFF/ON zero maximum difference is 0.000059670092462 mm, matching the previously established float noise. No meaningful zero-pose geometry change was detected globally.
- Existing BIND / IDX_MCP_15 /30 /45 coordinate evidence was read. No Stage6A cases were rerun.
- Earlier Stage4A_R2_BASE has3364 vertices and was excluded from identity tracing; no mapping across its changed topology is guessed.

## Remaining evidence

Human must confirm whether the intended dent is A, B, C in ROI_LOCATION_CLARIFICATION.png, or describe another exact image location. Then screen-to-surface selection, 1/2-ring membership, matched stage/shading renders, three surface sections, ROI metrics, pose-amplification comparison and minimum downstream amendment scope can be completed.

The existing 9 severe crossing records and Stage6A FAIL CLOSED remain unchanged. No geometry, normals, material, weights, rest bones, memberships, RSSF, bound authority or receipt was edited. No repair candidate was created or saved. No Stage6B or production promotion occurred.

STOP — HUMAN ROI LOCATION CONFIRMATION. This is an incomplete causal diagnosis, not READY_FOR_HUMAN_DENT_CAUSAL_REVIEW.
'''
(OUT/(PHASE+'_REPORT.md')).write_text(report,encoding='utf-8')
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Dent ROI location confirmation</title><style>body{max-width:1100px;margin:30px auto;font:17px/1.6 system-ui;color:#243142}img{width:100%;height:auto}a{color:#285d92}</style><h1>凹陷位置确认：诊断尚未完成</h1><p>请确认 A/B/C 中的目标。标注仅为屏幕位置，不是 anatomy authority。没有从文字猜测顶点，也没有生成修复。</p><p>A：上方锐利凹口。B：右侧指根间沟谷。C：左侧指根过渡凹处。</p><img src="ROI_LOCATION_CLARIFICATION.png" alt="BIND RSSF 左侧三个候选观察位置 A/B/C"><p>Stage4C、corrected Stage5A、R2 原始几何坐标完全一致。R2 zero Armature OFF/ON 的全网格最大差异仅0.00005967 mm，与既有浮点噪声一致。</p><p>确认后再建立 ROI、三个截面和 matched stage/shading evidence。9 对 crossing 保持原样。</p><p><a href="RIGHT_HAND_DORSAL_MCP_CONTOUR_DENT_CAUSAL_DIAGNOSIS_R1_REPORT.md">当前调查记录</a> · <a href="RIGHT_HAND_DORSAL_MCP_CONTOUR_DENT_CAUSAL_DIAGNOSIS_R1_STATUS.json">未完成状态</a></p></html>'''
(OUT/'review.html').write_text(page,encoding='utf-8')
baseline=read(OUT/'HISTORICAL_HASHES_BEFORE.json');now=inventory()
changed=[p for p,h in baseline.items() if now.get(p)!=h];unexpected=sorted(set(now)-set(baseline))
assert not changed and not unexpected,(changed,unexpected)
dump('PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json',{'status':'PASS','protected_preexisting_file_count':len(baseline),'changed_or_deleted_preexisting_files':changed,'new_files_outside_this_round':unexpected,'PRODUCTION_DRIFT':0,'Stage6A_crossing_evidence_unchanged':True,'repair_count':0})
dump('ROUND_ARTIFACT_MANIFEST.json',{'artifacts':{p.relative_to(OUT).as_posix():sha(p) for p in OUT.rglob('*') if p.is_file() and p.name!='ROUND_ARTIFACT_MANIFEST.json'},'purpose':'Incomplete causal diagnosis, independent read-only inputs preserved pending exact Human ROI location.'})
print('PENDING ROI; protected files unchanged',len(baseline))
