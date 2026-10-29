from common import *
from html import escape
from datetime import datetime,timezone,timedelta
import ast
J=read(OUT/'JOINT_SURFACE_REQUALIFICATION_AFTER_PALMAR_R1.json');M=read(OUT/'MIDDLE_MCP_R_SURFACE_RELATION_REVALIDATION_R1.json');R=read(OUT/'JOINT_SURFACE_DELTA_RANKING_AFTER_PALMAR_R1.json');B=read(OUT/'BIND_ZERO_GEOMETRY_REVALIDATION_AFTER_PALMAR_R1.json');Z=read(OUT/'ZERO_POSE_REVALIDATION_AFTER_PALMAR_R1.json');D=read(OUT/'CLEAN_REOPEN_NATIVE_PAYLOADS_R1.json');S=read(OUT/'ZERO_BIND_PROTECTED_SURFACE_NUMERICAL_SUPPORT_R1.json');C=read(OUT/'CURRENT9_HOLD_AND_OVERLAP_RECHECK_R1.json');W=read(OUT/'WEIGHT_HASH_READONLY_AFTER_PALMAR_R1.json');P=read(OUT/'MATCHED_RENDER_PIXEL_SUPPORT_R1.json');E=read(OUT/'EVALUATED_ZERO_JOINT_SURFACE_CROSSCHECK_R1.json')
assert J['summary']['FORMAL_JOINTS_PASS']==21 and J['status']==E['status']=='PASS'
assert Z['ZERO_POSE']==B['BIND_ZERO']=='PASS' and B['RAW_TO_BIND_OUT_OF_TOLERANCE_COUNT']==0
assert all(r['Stage4C_vs_Stage5B_raw_pixel_exact'] for r in P['rows'])
assert W['actual_hashes']['R2']==WEIGHT_HASH
rest=read(OUT/'REST_RIG_PAYLOAD_AFTER_PALMAR_R1.json');rest['actual21_native_rest_payloads']={k:D[k]['protected']['rigs'] for k in ('CORRECTED','R2','OLD_CORRECTED','OLD_R2')};dump('REST_RIG_PAYLOAD_AFTER_PALMAR_R1.json',rest)
Z['ZERO_POSE_REVALIDATION']=Z['ZERO_POSE'];dump('ZERO_POSE_REVALIDATION_AFTER_PALMAR_R1.json',Z)
visual={'status':'PASS','PALMAR_ROOT_DENT_REAPPEARED_AT_BIND_ZERO':'NO','PALMAR_ROOT_DENT_REAPPEARED':'NO','HARD_SHELF_REAPPEARED':'NO','PALMAR_ROOT_NATURAL_CREASE_BIND_ZERO':'PRESERVED','NATURAL_CREASE_BIND_ZERO':'PRESERVED','PALMAR_ROOT_NEW_BIND_VISIBLE_DEFECT':'NONE','PALMAR_ROOT_NEW_VISIBLE_DEFECT':'NONE','new_ridge':'NONE_OBSERVED','new_notch':'NONE_OBSERVED','new_collapse':'NONE_OBSERVED','new_boundary_discontinuity':'NONE_OBSERVED','reviewer':'Codex direct inspection of generated matched three-column images','inspection_scope':'Preservation at bind-zero of existing Human-approved surface; no new Human acceptance or posed qualification','inspected_images':[ref(OUT/p) for p in ('PALMAR_SOLID_INSPECTION_R1.png','PALMAR_DETAIL_INSPECTION_R1.png')],'camera_authority':ref(ROOT/'audits/palmar_digit_root_local_donor_shape_restoration_design_r1/PALMAR_ROOT_HUMAN_TARGET_LOCK_R1.json'),'matched_render_manifest':ref(OUT/'PALMAR_BIND_ZERO_MATCHED_RENDER_MANIFEST_R1.json'),'views':['Human confirmed camera solid','close solid','alternate solid','close grazing','close flat/source-native','close wire'],'columns':['Latest Stage4C RAW','New Stage5B RAW','Actual new Stage5B evaluated ZERO'],'numerical_support':S['palmar16'],'normal69':S['normal69'],'pixel_support':[r for r in P['rows'] if not r['view'].startswith('DORSAL')],'native_asset_saves':0,'new_human_approval_claimed':False}
dump('PALMAR_ROOT_BIND_ZERO_VISUAL_R1.json',visual)
dump('DORSAL54_BIND_ZERO_REGRESSION_R1.json',{'status':'PASS','DORSAL54_BIND_ZERO_REGRESSION':'PASS','scope':'Regression sentinel only; no full dorsal Human review','reviewer':'Codex direct image inspection','inspection':ref(OUT/'DORSAL_SENTINEL_INSPECTION_R1.png'),'numerical_support':S['dorsal54'],'matched_render_manifest':ref(OUT/'DORSAL_BIND_ZERO_MATCHED_RENDER_MANIFEST_R1.json'),'pixel_support':[r for r in P['rows'] if r['view'].startswith('DORSAL')],'new_visible_bind_regression':'NONE_OBSERVED'})
dump('NORMAL69_BIND_ZERO_REVALIDATION_R1.json',S['normal69'])
dump('NUMERICAL_METHOD_RECONCILIATION_R1.json',{'status':'PASS','raw_exact_vs_evaluated_zero':'Corrected THUMB_TIP native v284 exact equality applies to stored raw authority. Evaluated terminal displacement 0.000003725290298461914mm uses the recovered full3416 <=0.0001mm raw-to-bind gate. Supplement implementation initially applied raw exact equality to evaluated data and was corrected before qualification delivery; no geometry, rig or threshold change.','corrected_native_terminal_in_evaluated_zero':E['all21_rows']['THUMB_TIP_R']['region'],'surface_methods':M['methods'],'fan_computation_reproduced_user_old_new_delta':M['head']['prior_diagnostic_method_fresh_recomputed'],'formal_native_polygon_head':M['head']['formal_Blender_native_polygon_method'],'new_thresholds':0})
# Verify executable scope: display-only mesh creation and formal ZERO reuse are permitted.
scope=[]
for p in OUT.glob('*.py'):
 tree=ast.parse(p.read_text(encoding='utf-8-sig'))
 forbidden=[ast.unparse(n) for n in ast.walk(tree) if isinstance(n,ast.Call) and any(x in ast.unparse(n.func) for x in ('save_as_mainfile','save_mainfile','modifier_apply','armature_apply','transform_apply'))]
 assert not forbidden,(p,forbidden)
 scope.append({'script':ref(p),'forbidden_save_apply_calls':forbidden})
dump('READONLY_EXECUTION_SCOPE_VERIFICATION_R1.json',{'status':'PASS','scripts':scope,'actual_blend_saves':0,'actual_nonzero_pose_evaluations':0,'formal_unsaved_ZERO_evaluations':1,'no_static_skin_true_cap_R3_Stage6_Full42_runs':True,'display_only_meshes_created_for_queries_and_renders':True})
before=read(OUT/'PROTECTED_HISTORY_HASHES_BEFORE.json');after=inventory();changed=[p for p,h in before.items() if after.get(p)!=h];added=sorted(set(after)-set(before));removed=sorted(set(before)-set(after))
assert not changed and not added and not removed,(changed,added,removed)
assert all(sha(p)==EXPECTED[k] for k,p in FILES.items())
external=C['external_response'];assert external is None or sha(external['path'])==external['sha256']
dump('PROTECTED_HISTORY_HASHES_AFTER.json',after)
dump('PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json',{'status':'PASS','PROTECTED_HISTORY_DRIFT':0,'before_protected_file_count':len(before),'after_protected_file_count':len(after),'changed_paths':changed,'added_paths_outside_phase':added,'removed_paths':removed,'all_input_hashes_after':{k:ref(p) for k,p in FILES.items()},'scope_exclusion':str(OUT),'blend_files_saved':0,'geometry_joint_bone_roll_rest_weight_group_modifier_edits':0,'external_current9_response_byte_unchanged_if_available':external})
fan=M['head']['prior_diagnostic_method_fresh_recomputed'];formal=M['head']['formal_Blender_native_polygon_method']
status={'phase':PHASE,'recorded_at_Asia_Shanghai':datetime.now(timezone(timedelta(hours=8))).isoformat(),'STAGE5A_INPUT_HASH_VERIFIED':'PASS','STAGE5B_INPUT_HASH_VERIFIED':'PASS','FORMAL_JOINT_HELPER_COUNT':21,'FORMAL_JOINT_HELPER_PASS_COUNT':21,'ALL_REQUIRED_INSIDE_JOINTS':'PASS','REQUIRED_INSIDE_JOINT_FAILURE_COUNT':0,'TIP_HELPER_FAILURE_COUNT':0,'JOINT_REGION_FAILURE_COUNT':0,
 'MAX_JOINT_SURFACE_DISTANCE_DELTA_MM':R['MAX_JOINT_SURFACE_DISTANCE_DELTA_MM'],'MAX_JOINT_SURFACE_DISTANCE_DELTA_JOINT':R['MAX_JOINT_SURFACE_DISTANCE_DELTA_JOINT'],'MAX_JOINT_SURFACE_DISTANCE_DELTA_METHOD':'Formal current frozen Blender native polygon closest, paired old/new','MIDDLE_MCP_R_HEAD_OLD_SURFACE_MM':fan['old_distance_mm'],'MIDDLE_MCP_R_HEAD_NEW_SURFACE_MM':fan['new_distance_mm'],'MIDDLE_MCP_R_HEAD_DELTA_MM':fan['delta_mm'],'MIDDLE_MCP_R_HEAD_REPORTED_DISTANCE_METHOD':'Historical diagnostic native fan BVH, independently fresh reproduced; do not mix with formal polygon method','MIDDLE_MCP_R_HEAD_FORMAL_OLD_SURFACE_MM':formal['old']['surface_distance_mm'],'MIDDLE_MCP_R_HEAD_FORMAL_NEW_SURFACE_MM':formal['new']['surface_distance_mm'],'MIDDLE_MCP_R_HEAD_FORMAL_DELTA_MM':formal['delta_mm'],'MIDDLE_MCP_R_HEAD_NEAREST_FACE_BEFORE':formal['old']['nearest_native_feature']['native_polygon'],'MIDDLE_MCP_R_HEAD_NEAREST_FACE_AFTER':formal['new']['nearest_native_feature']['native_polygon'],'MIDDLE_MCP_R_INSIDE_STATUS':'PASS','MIDDLE_MCP_R_INSIDE_VOTES':'64/64','MIDDLE_MCP_R_REGION_STATUS':'PASS','MIDDLE_MCP_R_T01_MARGIN_MM':M['head']['formal_region']['qualification_margin_mm'],
 'CORRECTED_THUMB_CHAIN_PRESERVED':'PASS','BONE_PAYLOAD_DELTA':0,'JOINT_PAYLOAD_DELTA':0,'JOINT_HEAD_DELTA_MM':0,'JOINT_TAIL_DELTA_MM':0,'ROLL_DELTA':0,'REST_MATRIX_DELTA':0,'BONE_HIERARCHY_DELTA':0,'OBJECT_ARMATURE_TRANSFORM_DELTA':0,'REST_RIG_PAYLOAD_MATCH':'PASS','ZERO_POSE_REVALIDATION':'PASS','RAW_TO_BIND_MAX_DELTA_MM':B['RAW_TO_BIND_MAX_DELTA_MM'],'RAW_TO_BIND_MEAN_DELTA_MM':B['RAW_TO_BIND_MEAN_DELTA_MM'],'RAW_TO_BIND_RMS_DELTA_MM':B['RAW_TO_BIND_RMS_DELTA_MM'],'RAW_TO_BIND_P95_DELTA_MM':B['RAW_TO_BIND_P95_DELTA_MM'],'RAW_TO_BIND_OUT_OF_TOLERANCE_COUNT':B['RAW_TO_BIND_OUT_OF_TOLERANCE_COUNT'],'MAX_DELTA_VERTEX_ID':B['MAX_DELTA_VERTEX_ID'],'RAW_TO_BIND_POINT_COUNT':3416,'RECOVERED_FORMAL_ZERO_GATE_MM':B['recovered_existing_tolerance_mm'],'BIND_ZERO':'PASS','PALMAR_ROOT_DENT_REAPPEARED_AT_BIND_ZERO':'NO','PALMAR_ROOT_NATURAL_CREASE_BIND_ZERO':'PRESERVED','PALMAR_ROOT_NEW_BIND_VISIBLE_DEFECT':'NONE','DORSAL54_BIND_ZERO_REGRESSION':'PASS','NORMAL69_RAW_COORD_MATCH':'PASS','NORMAL69_ZERO_WITHIN_FORMAL_GATE':'PASS','MODIFIER_BINDING':'PASS','R2_WEIGHT_HASH':W['actual_hashes']['R2'],'R2_WEIGHT_HASH_MATCH':'PASS','CURRENT9_DIRECT_OVERLAP':0,'CURRENT9_1RING_OVERLAP':0,'CURRENT9_2RING_OVERLAP':0,'CURRENT9_HUMAN_RESPONSE':'HOLD_NOT_CLOSED','JOINT_RELOCATION_REQUIRED':'NO','RIG_REBUILD_REQUIRED':'NO','WEIGHT_CHANGE_REQUIRED':'NO','STATIC_SKIN_REQUALIFICATION':'NOT_RUN','MID_MCP_45_MANDATORY_REVALIDATION':'YES','WHOLE_HAND_SURFACE_INTEGRITY_BASELINE_REQUIRED':'YES','TRUE_CAP_RECOMPUTATION':'NOT_RUN','R3_RERUN':'NOT_RUN','NONZERO_POSE_EVALUATIONS':0,'FULL42':'NOT_RUN','STAGE6B':'NOT_RUN','PRODUCTION_PROMOTION':'NO','PROTECTED_HISTORY_DRIFT':0,'PROTECTED_FILE_COUNT':len(before),'BLEND_SAVES':0,'VERDICT':'PASS_JOINT_REST_ZERO_BIND_REQUALIFIED','NEXT':'STATIC_SKIN_COMPATIBILITY_REVALIDATION_AFTER_PALMAR_DONOR_RESTORATION_R1','NEXT_EXECUTED':False,'STOP':True}
dump(PHASE+'_STATUS.json',status)
def table(rows):return '\n'.join('| '+ ' | '.join(str(x).replace('|','/') for x in row)+' |' for row in rows)
fields=table([(k,json.dumps(v,ensure_ascii=False)) for k,v in status.items()])
jointrows=table([(n,r['authority']['role'],str(r['surface']['ray_parity_votes'])+'/64' if r['authority']['inside_required'] else 'N/A',format(r['old_geometry']['surface_distance_mm'],'.12f'),format(r['surface']['surface_distance_mm'],'.12f'),format(r['distance_delta_mm'],'+.12f'),r['region']['status'],r['final_status']) for n,r in J['all21_current_rows'].items()])
report=f'''# {PHASE}

PASS_JOINT_REST_ZERO_BIND_REQUALIFIED。只读复核完成，STOP。

新 Stage5A、新 Stage5B R2 与最新 Human-approved dorsal54 + palmar16 Stage4C 的完整 3416 local/world raw coordinates 精确一致，两份 Stage5 bone payload 精确一致。实际输入哈希均与指定 authority 匹配。所有 21 joint/helper 都在当前新表面 fresh 测量；16 deform heads required-inside 全部 64/64 inside，5 non-deform TIP helpers 与全部区域规则通过。Actual evaluated ZERO surface 的 21 项交叉检查也通过。

## Authority 与语义

沿用此前成功 donor-transfer revalidation 的 R2/R2A / freeze / errata / Human corrected thumb 优先级，并 fresh 读取与核对其 source hashes。Wrist 使用冻结 transition band，THUMB_CMC 使用已批准 CMC locality sphere，MCP/PIP/DIP 使用 T-01 frozen axial frame/zone。四指 TIP 使用 accepted own-digit face/surface/apex 规则；corrected THUMB_TIP 使用 native terminal v284，旧 cap REP 规则已 superseded。TIP 不执行 deform-inside gate。没有 anatomy、locator、CMC cage、cap、ownership 或 joint fitting 重算。

正式 parity/closest、ZERO reset/evaluate 仅 AST 复用历史函数，无历史 audit/builder 顶层执行。ZERO procedure 为 21 quaternion identity / location zero / scale one，仅临时内存，不保存。源代码明确确认当前 R2 `raw_RSSF_noise_mm <= 1e-4 mm`，Stage5B R1/R1B 亦使用 0.0001mm 门槛；本轮未发明阈值。

## MIDDLE_MCP head / tail

历史 diagnostic fan-BVH 方法独立 fresh 重现：head old **{fan['old_distance_mm']:.15f} mm** → new **{fan['new_distance_mm']:.15f} mm**，delta **+{fan['delta_mm']:.17f} mm**。

正式 frozen Blender native polygon 方法独立成对计算：old **{formal['old']['surface_distance_mm']:.15f} mm** → new **{formal['new']['surface_distance_mm']:.15f} mm**，delta **+{formal['delta_mm']:.17f} mm**。两种方法的旧值差异来自 fan/native polygon tessellation 与数值空间；禁止把一套旧值与另一套新值相减。报告的正式 joint delta ranking 使用后一方法，最大变化 joint 仍为 MIDDLE_MCP_R；其余 20 head delta 均为 0。

Nearest native face **2783 → 2421**：旧 face 包含 palmar16 的 3360 / 3353，新 face 为 1024 / 125 / 1938 / 3085。Head 64/64 inside，negative signed relation；T-01 MCP axial projection 0mm，approved center 0mm，half-width / margin **9.149mm**，区域 PASS。局部 palmar16 proximity 与 native feature 详见专项 JSON。该距离增量不是 fail threshold，也不要求 joint relocation。

Tail 与 MIDDLE_PIP_R head 精确相同，两种方法的 old/new nearest distance delta 均为 0，64/64 inside，冻结 PIP region PASS。Tail 不被误套 MCP head zone；完整 head/tail 独立报告。全部 42 endpoints 排序与 palmar16 最近 joint/helper 排序已输出，INDEX_MCP / RING_MCP / WRIST 明确列入 focus。

## Rest / ZERO / bind

两份新 Stage5 对各自 propagation source：21 bones 的 names/order、parents/children、head/tail、actual native roll、rest/local matrices、use_deform / inherit / connect flags、完整 mesh/armature object transforms 精确一致。Corrected THUMB_IP / TIP chain frozen。Native EditBone.roll 在临时会话最后只读，无 setter、mode exit 或保存。REST_RIG_PAYLOAD_MATCH PASS。

Clean reopened actual Stage5B R2 Armature ON + formal ZERO：21 matrix_basis exact identity，pose-rest matrix residue 0，NaN/Inf、missing bones/groups/modifier target 和 pose residue 均 0。Full 3416-point raw→evaluated max **{B['RAW_TO_BIND_MAX_DELTA_MM']:.16g}mm**，mean **{B['RAW_TO_BIND_MEAN_DELTA_MM']:.16g}mm**，RMS **{B['RAW_TO_BIND_RMS_DELTA_MM']:.16g}mm**，P95 **{B['RAW_TO_BIND_P95_DELTA_MM']:.16g}mm**；超出 recovered 0.0001mm gate 的点 **0**；max vertex ID **{B['MAX_DELTA_VERTEX_ID']}**。

Corrected THUMB terminal 的 stored raw exact native-v284 authority PASS。其 evaluated ZERO native-terminal noise 为 0.000003725290298461914mm，按 recovered bind tolerance 处理。补充脚本初稿曾把 raw exact equality 用于 evaluated geometry，现已修正其实现适用范围；没有 joint、geometry 或阈值改动。该数值不得误判为 geometry write。所有 21 evaluated-zero surface/region cross-check PASS。

Modifier target/order/settings、groups/order、每个 weight scalar 含零、deform mapping、mesh/armature transforms 与旧 R2 精确一致。完整 3416 weight-vector hash **{WEIGHT_HASH}**。实际 Blender Armature modifier 无独立用户 bind matrix；沿用其 object/rest mapping，记录已有 matrix_parent_inverse，无 rebind / inverse-bind recompute。

## 掌侧与 dorsal / normal69

27 张实际 fresh matched renders：掌侧 6 rows × 3 columns，dorsal sentinel 3 rows × 3 columns。掌侧覆盖 Human confirmed camera solid、close solid、alternate solid、grazing、flat/source-native、wire。同一 row 三列 camera/light/material/scale 相同，坐标源为 latest Stage4C RAW / new Stage5B RAW / actual evaluated ZERO。已由 Codex 直接检查 contact sheets：hard shelf/dent 未回返，natural crease PRESERVED，未观察到新 ridge、notch、collapse 或 boundary discontinuity。这仅证明现有 Human-approved geometry 的 ZERO preservation，不生成新 Human closure 或 acceptance。

Dorsal54 regression sentinel PASS；normal69 raw coordinates exact Stage4C，evaluated ZERO 全部 within formal gate。三类区域 incident native triangles 零面积与方向反转数均 0，面积比仅记录为补充 contour 数值支持，无新增 skin gate。所有 rendered Stage4C→Stage5B RAW 像素精确一致；RAW→ZERO pixel difference 单列。

## Current9、历史与 NEXT

两份实际 Stage5 native ID/topology fresh recheck：palmar16/current9 direct / 1-ring / 2-ring **0 / 0 / 0**。Current9 **HOLD_NOT_CLOSED**，answer/closure/acceptance 无写入。已 hash 核对 **{len(before)}** 个受保护 pre-existing files，漂移 **0**。本轮新产物仅位于本目录，blend 保存 **0**。

JOINT_RELOCATION_REQUIRED=NO；RIG_REBUILD_REQUIRED=NO；WEIGHT_CHANGE_REQUIRED=NO。STATIC_SKIN_REQUALIFICATION=NOT_RUN；MID_MCP_45_MANDATORY_REVALIDATION=YES；WHOLE_HAND_SURFACE_INTEGRITY_BASELINE_REQUIRED=YES。

NEXT=`{status['NEXT']}`，只记录，未执行。后续顺序：static skin compatibility → geometry-dependent authority impact audit → palmar targeted MID15/30/45（45 mandatory）→ fresh FullStage6A42 → Human visual review → current9 closure resume → whole-hand surface integrity baseline → 之后才考虑 Stage6B。本轮未执行任何非零 pose、skin continuity、R3、true-cap、Full42、Stage6B 或 promotion。

## 全部最终字段

| Field | Value |
|---|---|
{fields}

## 逐项 fresh formal surface qualification

| Joint/helper | Type | Inside votes | Old mm | New mm | Delta mm | Region/helper | Final |
|---|---|---|---|---|---|---|---|
{jointrows}

复现顺序：prepare.py → recover_semantics.py → Blender revalidate.py → Blender supplement.py → build_visual_tools.py → Blender render_palmar.py / render_dorsal.py → prepare_evidence.py → direct image inspection → deliver.py → validate_delivery.py。只读 native 查询副本与 display meshes 在内存创建；唯一 pose 操作为 frozen ZERO procedure。

[Matched review](review.html)。STOP。
'''
(OUT/(PHASE+'_REPORT.md')).write_text(report,encoding='utf-8')
parts=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Palmar · Joint / Rest / ZERO / Bind R1</title><style>body{margin:0;background:#111923;color:#e2edf4;font:15px/1.65 system-ui}main{max-width:1500px;margin:auto;padding:28px}h1{font-size:28px}h2{margin-top:32px}a{color:#83cfff}table{border-collapse:collapse;width:100%;font-size:13px}td,th{border-bottom:1px solid #33465a;padding:8px;text-align:left;overflow-wrap:anywhere}img{display:block;width:100%;height:auto}.badge{display:inline-block;padding:8px 14px;background:#215c40;border-radius:7px}code{overflow-wrap:anywhere}</style><main><h1>Palmar restoration · joint / rest / ZERO / bind</h1><p class="badge">PASS_JOINT_REST_ZERO_BIND_REQUALIFIED · STOP</p><p>21/21 joints/helpers；16 deform heads inside PASS；5 non-deform TIP helpers PASS。完整 3416 点 evaluated ZERO within recovered ≤0.0001 mm。没有 blend 保存、rig / weight 修改或非零 pose。</p><h2>MIDDLE_MCP · 成对方法</h2><table><tr><th>Method</th><th>Old mm</th><th>New mm</th><th>Delta mm</th></tr>']
for label,a,z,d in [('Formal native polygon',formal['old']['surface_distance_mm'],formal['new']['surface_distance_mm'],formal['delta_mm']),('Diagnostic native fan BVH',fan['old_distance_mm'],fan['new_distance_mm'],fan['delta_mm'])]:parts.append(f'<tr><td>{label}</td><td>{a:.15f}</td><td>{z:.15f}</td><td>+{d:.15f}</td></tr>')
parts.append('</table><p>Nearest face 2783 → 2421；64/64 inside；MCP T-01 margin 9.149 mm。距离变化不是自动失败门槛。两种方法分别 paired，不混用。</p>')
for title,img in [('掌侧 · Human / close / alternate solid','PALMAR_SOLID_INSPECTION_R1.png'),('掌侧 · grazing / flat-source-native / wire','PALMAR_DETAIL_INSPECTION_R1.png'),('Dorsal54 · regression sentinel','DORSAL_SENTINEL_INSPECTION_R1.png')]:parts.append(f'<h2>{title}</h2><p>三列：latest Stage4C RAW ／ new Stage5B RAW ／ actual evaluated ZERO。</p><a href="{img}"><img src="{img}" alt="{title}"></a>')
parts.append('<h2>逐项 joint/helper</h2><table><tr><th>Name</th><th>Inside</th><th>Surface mm</th><th>Delta mm</th><th>Region</th><th>Status</th></tr>')
for n,r in J['all21_current_rows'].items():
 vals=[n,str(r['surface']['ray_parity_votes'])+'/64' if r['authority']['inside_required'] else 'N/A — non-deform',format(r['surface']['surface_distance_mm'],'.12f'),format(r['distance_delta_mm'],'+.12f'),r['region']['status'],r['final_status']];parts.append('<tr>'+''.join('<td>'+escape(v)+'</td>' for v in vals)+'</tr>')
parts.append('</table><h2>全部最终字段</h2><table>')
for k,v in status.items():parts.append('<tr><td>'+escape(k)+'</td><td>'+escape(json.dumps(v,ensure_ascii=False))+'</td></tr>')
parts.append('</table><h2>报告与只读证据</h2><ul>')
for p in sorted(OUT.glob('*.json'))+sorted(OUT.glob('*REPORT.md')):parts.append('<li><a href="'+escape(p.name)+'">'+escape(p.name)+'</a></li>')
parts.append('</ul><p>Current9 HOLD_NOT_CLOSED。MID45 mandatory 与 whole-hand baseline required 保持 YES。NEXT static skin 只记录，未执行。STOP。</p></main></html>')
(OUT/'review.html').write_text(''.join(parts),encoding='utf-8')
print('PASS_JOINT_REST_ZERO_BIND_REQUALIFIED; protected files',len(before),'drift0; STOP')
