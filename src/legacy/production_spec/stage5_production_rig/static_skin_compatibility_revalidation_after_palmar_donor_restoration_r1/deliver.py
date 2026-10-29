import sys
sys.dont_write_bytecode=True
from common import *
from datetime import datetime,timezone,timedelta
from html import escape
result=read(OUT/'STATIC_SKIN_MACHINE_RESULT_R1.json');assert result['preliminary_static_checks_pass'] and not result['minimal_blockers']
cont=read(OUT/'PALMAR_STATIC_SKIN_CONTINUITY_EDGE_REVALIDATION_R1.json');pre=read(PRE/'STATIC_SKIN_CONTINUITY_EDGE_REVALIDATION_R1.json');math_audit=read(OUT/'PALMAR_STATIC_SKIN_FULL_MESH_MATH_AUDIT_R1.json');payload=read(OUT/'PALMAR_STATIC_SKIN_WEIGHT_PAYLOAD_AUDIT_R1.json');diag=read(OUT/'PALMAR16_GEOMETRY_DRIVER_DIAGNOSTIC_R1.json');local=read(OUT/'PALMAR16_STATIC_EDGE_COMPATIBILITY_R1.json');debts=read(OUT/'PALMAR_STATIC_SKIN_INHERITED16_R1.json');intersection=read(OUT/'PALMAR16_AUTHORITY_INTERSECTION_R1.json');current9=read(OUT/'CURRENT9_HOLD_RECHECK_R1.json')
assert cont['all_checked_edges']==pre['all_checked_edges'] and cont['all_exceedances']==pre['all_exceedances'] and cont['subthreshold_historical_increases_preserved']==pre['subthreshold_historical_increases_preserved']
dump('PRE_PALMAR_FULL_STATIC_RECORD_EQUIVALENCE_R1.json',{'status':'PASS','all2127_complete_edge_records_exact':True,'all16_debt_classifications_endpoints_and_metrics_exact':True,'all_subthreshold_increase_records_exact':True,'pre_palmar_reference':ref(PRE/'STATIC_SKIN_CONTINUITY_EDGE_REVALIDATION_R1.json'),'current_reference':ref(OUT/'PALMAR_STATIC_SKIN_CONTINUITY_EDGE_REVALIDATION_R1.json'),'inherited_debt_resolution_count':0})
sourcefiles={str(p.resolve()):sha(p) for p in [PRE/'revalidate.py',R2DIR/'common.py',R2DIR/'audit_and_report.py',AUTH/'SKIN_WEIGHT_CONTINUITY_CONTRACT_R1.json']}
scope=[]
for p in OUT.glob('*.py'):
 tree=ast.parse(p.read_text(encoding='utf-8-sig'))
 forbidden=[]
 for n in ast.walk(tree):
  if isinstance(n,ast.Call):
   fn=ast.unparse(n.func)
   if fn.split('.')[-1] in ('save_as_mainfile','save_mainfile','reset_pose','evaluated_get','evaluated_depsgraph_get','to_mesh','mode_set','normalize','smooth','harmonic','dykstra','solve','set_pose'):forbidden.append(fn)
 assert not forbidden,(p,forbidden)
 scope.append({'script':ref(p),'forbidden_runtime_mutation_solver_pose_calls':forbidden})
dump('READONLY_STATIC_EXECUTION_SCOPE_VERIFICATION_R1.json',{'status':'PASS','scripts':scope,'pure_functions_AST_reused':['metric','support','fails','edge_record','plain','props','rna','object_payload','rig_payload','material_payload','snapshot','load'],'historical_constructor_solver_audit_top_level_executed':False,'no_weight_group_mesh_joint_modification_calls':True,'weights_written':0,'groups_written':0,'solver_runs':0,'all_pose_runs':0,'depsgraph_deformation_evaluations':0,'blend_saves':0})
before=read(OUT/'PROTECTED_HISTORY_HASHES_BEFORE.json');after=inventory();drift=[p for p,h in before.items() if after.get(p)!=h];added=sorted(set(after)-set(before));removed=sorted(set(before)-set(after))
assert not drift and not added and not removed,(drift,added,removed)
assert all(sha(p)==EXPECTED[k] for k,p in FILES.items())
external=current9['external_response'];assert external is None or sha(external['path'])==external['sha256']
dump('PROTECTED_HISTORY_HASHES_AFTER.json',after)
dump('PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json',{'status':'PASS','PROTECTED_HISTORY_DRIFT':0,'protected_file_count':len(before),'history_modified_or_deleted_paths':drift,'new_paths_outside_this_phase':added,'removed_paths':removed,'sole_phase_exclusion':str(OUT),'input_hashes_after':{k:ref(p) for k,p in FILES.items()},'canonical_acceptance_sources':sourcefiles,'external_current9_response_if_available_preserved':external,'weight_write_count':0,'group_write_count':0,'mesh_joint_rig_modifier_writes':0,'skin_solver_runs':0,'all_pose_runs':0,'Full42_runs':0,'Stage6B_runs':0,'blend_saves':0})
status={k:v for k,v in result.items() if k not in ('preliminary_static_checks_pass','minimal_blockers')}
status.update({'recorded_at_Asia_Shanghai':datetime.now(timezone(timedelta(hours=8))).isoformat(),'CURRENT_STAGE5B_R2_SHA256':sha(FILES['CURRENT']),'PRE_PALMAR_STAGE5B_R2_SHA256':sha(FILES['OLD_R2']),'INPUT_HASHES_VERIFIED':'PASS','WEIGHT_REBUILD_REQUIRED':'NO','WEIGHT_CHANGE_REQUIRED':'NO','SCOPE_EXPANSION_REQUIRED':'NO','PROTECTED_HISTORY_DRIFT':0,'PROTECTED_FILE_COUNT':len(before),'BLEND_SAVE_COUNT':0,'STATIC_SKIN_COMPATIBILITY_REVALIDATION_AFTER_PALMAR_DONOR_RESTORATION_R1':'PASS_STATIC_SKIN_COMPATIBILITY_REQUALIFIED','VERDICT':'PASS_STATIC_SKIN_COMPATIBILITY_REQUALIFIED','NEXT':'GEOMETRY_DEPENDENT_AUTHORITY_IMPACT_AUDIT_AFTER_PALMAR_DONOR_RESTORATION_R1','NEXT_EXECUTED':False,'TRUE_CAP_RECOMPUTATION':'NOT_RUN','R3_RERUN':'NOT_RUN','WHOLE_HAND_INTEGRITY_BASELINE':'NOT_RUN','CURRENT9_CLOSURE':'NOT_RUN','PRODUCTION_PROMOTION':'NO','STOP':True})
dump(PHASE+'_STATUS.json',status)
def mdtable(rows):return '\n'.join('| '+' | '.join(str(x).replace('|','/') for x in row)+' |' for row in rows)
fields=mdtable((k,json.dumps(v,ensure_ascii=False)) for k,v in status.items())
ids=mdtable((k,len(v['native_vertex_ids']),str(v['native_vertex_ids'])) for k,v in intersection['intersections'].items())
focus=mdtable((g,d['positive_vertex_count'],format(d['weight_min'],'.12g'),format(d['weight_max'],'.12g'),format(d['weight_mean'],'.12g')) for g,d in diag['focus_driver_distribution'].items())
debt_table=mdtable((r['edge_id'],r['vertex_ids'],format(r['R2_metrics']['L_inf'],'.12g'),format(r['R2_metrics']['L1'],'.12g'),r['classification']) for r in debts['edges'])
report=f'''# {PHASE}

**PASS_STATIC_SKIN_COMPATIBILITY_REQUALIFIED**。本轮只读 static skin compatibility requalification 完成，STOP。

完整 3416 frozen R2 vectors 在最新 dorsal54 + palmar16 geometry 下保持数学合法、authority-compatible、continuity-compatible 和既有 driver-compatible。没有任何 weight scalar、group、geometry 或 rig 写入，没有 solver、pose、deformation 或下游 gate 执行。

## 输入与 prerequisites

Latest Stage5B R2 SHA256：`{status['CURRENT_STAGE5B_R2_SHA256']}`。

Pre-palmar Stage5B R2 comparator SHA256：`{status['PRE_PALMAR_STAGE5B_R2_SHA256']}`。

另行核对最新 Stage4C、Stage5A、canonical corrected rig 的实际 SHA256。四个既有 prerequisite verdict（palmar application、propagation、joint/rest/zero/bind、新几何之前的 static skin）均已读取与确认。实际五份资产经 Blender 5.1.2 background / factory-startup / disable-autoexec，逐一 factory-reset clean reopen。

当前 weight authority：`{status['R2_WEIGHT_HASH']}`，MATCH PASS。3416 complete positive group-name vectors 的 canonical JSON digest 沿用原 R2 序列化；所有 sparse scalar entries 含零状态也另行读取，并构造 3416×16 dense float32 零补齐比较。实际 stored entries **{payload['stored_entry_count']}**，explicit stored zeros **{payload['explicit_stored_zero_count']}**，implicit dense zeros **{payload['implicit_dense_zero_count']}**。Dense payload **{payload['dense_byte_count']} bytes**，SHA256 `{payload['dense_float32_le_SHA256']}`，bit-exact pre-palmar comparator；不将该附加 digest 冒称历史 authority hash。

## 正式 acceptance semantics

恢复了 SKIN_STATIC_GATE_SEMANTICS_AND_SCOPE_RECONCILIATION_R1、Human-approved SKIN_STATIC_GATE_AND_SCOPE_AMENDMENT、TARGETED_RIG_AND_SKIN_DATA_REBUILD_R2，以及成功的 pre-palmar static requalification。实际核对原 R2 manifest、Human Q1–Q5 全部 YES、proposal / response hash、12 个 skin-authority 组件与冻结 membership / graph hash。

正式 continuity 继续 **SCOPED_ABSOLUTE_SCREEN_PLUS_NO_REGRESSION_WITH_EXPLICIT_QUALIFICATION**：L∞ ≤0.5、L1 ≤1.0；normalization absolute tolerance **{math_audit['normalization_tolerance']}**；max positive influences **4**；forbidden zero **exact mathematical zero，epsilon=0**。仅 AST 加载既有 metric/support/fails/edge_record acceptance 函数，没有旧 audit/builder 顶层、harmonic、edge-length solve、MED、geometry prior、Dykstra、317 optimization、smoothing、normalization 或 cleanup rewrite。

## Full3416 weight math 与冻结 authority

WEIGHT_SUM / NEGATIVE / NaN / Inf / MAX_INFLUENCE / TIP / FORBIDDEN_RESIDUE / ILLEGAL_CROSS_DIGIT / FIRST_WEB_THUMB_IP violations 均 **0**。Max sum error **{math_audit['max_sum_error']}**，实际 max influences **{math_audit['max_positive_influences']}**。Ownership/support 仍按 frozen962 和 cap37/oldcap9/FIRST_WEB wrappers；其余 mesh 沿用正式 deform-group contract与已接受的 exact frozen vector，没有新建全手 anatomy labels。

Cleanup55：55/55 原 forbidden entries **exact 0**，vector exact pre-palmar；未应用 cutoff、prune 或再归一化。

CAP37：37/37 canonical membership / complete vectors 精确一致，THUMB_IP dominant + THUMB_MCP historical continuity profile 保留。仅核对历史 frozen arc/quintic float32 profile，没有新 geometry projection、bone-distance solve 或 anatomy research。

Old cap9：9/9 INDEX_SURFACE，INDEX-compatible vectors 保留，THUMB distal override=0。

FIRST_WEB21：membership/vector exact，允许 WRIST_R / THUMB_CMC_R / THUMB_MCP_R / INDEX_MCP_R，THUMB_IP 和 TIP exact 0。

Fresh R3：962 frozen membership/graph endpoints/boundary identity 保留，仅作为 side/leakage guard。无 Dijkstra、min-cut、closure、ownership/sheet rerun 或 label→one-hot。

## 正式 2127 continuity edges

实际重建 pre-palmar 完全相同的 **2127 edges**，覆盖 historical317 incident/crossing、FIRST_WEB full 2-ring、fresh-R3 boundary、cap37 2-ring、oldcap9 patch、edge5879 neighborhood及原 validator 集合。

每条 current 与 fresh pre-palmar comparator 重新计算 L∞/L1，并分别核对成功 pre-palmar formal receipt 和原 R2 archived metrics。**2127/2127 exact match**；MAX_LINF_DELTA=0，MAX_L1_DELTA=0。进一步核对完整 edge records、全部 inherited-debt classifications 与原 subthreshold increases，均逐值精确一致。

Edge5879，v1551 / v3125：L∞ **{status['EDGE5879_LINF']}**，L1 **{status['EDGE5879_L1']}**，来自 fresh vectors；未硬编码 PASS。

Absolute screen exceedances **16**，全部仍是 **INHERITED_COPY_ONLY_STATIC_QUALIFICATION_DEBT**，identity / endpoint vectors / metrics 精确保留，resolved=0。不是 palmar-introduced blocker，也没有扩大 scope 或删除既有 qualification 义务。PALMAR_INTRODUCED=0、PALMAR_WORSENED=0、R2_INTRODUCED=0、R2_WORSENED=0、TRUE_SCOPE_CONFLICT=0。

| Debt edge | Endpoints | L∞ | L1 | Classification |
|---|---|---|---|---|
{debt_table}

## Palmar16 intersections 与局部 edge audit

实际 write IDs **3348–3363**，只有这16个 raw positions 相对 pre-palmar 变化；完整当前3416 geometry 与 latest Stage4C / Stage5A / Human-approved stored candidate/native application 精确匹配。全部非geometry payload与旧 R2 exact。21 bones/rest/flags/default channels 与 canonical corrected authority exact，仅仅读取，不设置 pose。

| Frozen authority | Intersection count | Native IDs |
|---|---|---|
{ids}

Palmar16 **48 incident edges**；inclusive 1-ring 与 first fixed outer boundary **112 context edges**。每个 endpoint 的 full vectors、driver families、pre/post L∞/L1 均列出。48 incident 与正式2127集合交集为 **{sum(r['in_formal2127'] for r in local['incident_edges'])}**；额外 context 是只读诊断，不扩展正式 gate 或317 write universe。112/112 weight metrics / sparse entries exact，delta=0；incident max L∞ **{diag['max_incident_Linf']}**、L1 **{diag['max_incident_L1']}**。

## Geometry-sensitive driver compatibility diagnostic

对全部16个 write vertices，分别测量到全部16个固定 deform-driver segments 的 pre/post distance，记录每个已有正分量含极小 residual；不根据 nearest bone 重分配 driver。逐条测量48 incident edge lengths、displacement gradient、L∞/L1 per-mm physical-gradient context，及全部 incident native polygon area/normals。

| Focus driver | Positive vertices /16 | Weight min | Weight max | Weight mean |
|---|---|---|---|---|
{focus}

最大 raw point displacement **{diag['max_displacement_mm']:.12f}mm**；已有 driver distance 最大绝对变化 **{diag['max_abs_existing_driver_distance_delta_mm']:.12f}mm**；edge length ratio **{diag['edge_length_ratio_range']}**。这些变化完整保留，没有发明 distance/gradient skin threshold 或将旧 solver geometry prior当 gate。

有 **{diag['negative_area_normal_dot_count']}** 个 native polygon 的 old→new area-normal 点积为负，minimum cosine **{diag['minimum_normal_cosine']}**，均明确记录。已批准 structure authority 的语义为：`{diag['face_normal_change_semantics']}`。实际 geometry 与该批准结果 exact，原 structure face reversal=0、new self-intersection=0、continuous native fan minimum area **{diag['approved_structure_context']['continuous_fan_area']['minimum_fan_triangle_area_mm2']}mm²**。仅绑定引用该已批准结果，没有 rerun structure/contact/pose；负投影法线变化不被改造为新的 skin failure rule。

已有 MIDDLE_MCP 结果继续 64/64 inside，T-01 PASS / margin 9.149mm / joint relocation NO。Natural crease 恢复后的 fixed joint + weight field 没有观察到明确 static authority incompatibility：family/support合法，complete vectors精确保留，全部 weight-space metrics不变，当前几何为批准stored authority。**GEOMETRY_DRIVER_COMPATIBILITY_DIAGNOSTIC=PASS**。这一静态诊断不授予非零 deformation PASS；MID45 mandatory 保持。

Normal69：69/69 coordinates、positive vectors、sparse entries 与 pre-palmar exact，全部 incident edge metrics exact，driver semantics 未改。

Dorsal54：只做 weight payload / incident-edge metric regression sentinel，PASS；未重开 dorsal research。

## Current9 / 历史保护 / STOP

Current9 **HOLD_NOT_CLOSED**；palmar16 direct / 1-ring / 2-ring overlap **0/0/0**。仅 native ID consistency，无 answers、Human closure 或 acceptance 扩展。

**{len(before)}** 个 pre-existing workspace files 前后 SHA256 全部保持原样，PROTECTED_HISTORY_DRIFT=0，新产物仅本目录。weight/group/geometry/rig/modifier writes=0、solver=0、scope expansion=0、所有 pose=0、deformation=0、Full42=0、Stage6B=0、blend save=0、promotion=NO。

WEIGHT_REBUILD_REQUIRED=NO、WEIGHT_CHANGE_REQUIRED=NO、SCOPE_EXPANSION_REQUIRED=NO。INHERITED_STATIC_DEBT_COUNT=16；MID_MCP_45_MANDATORY_REVALIDATION=YES；WHOLE_HAND_SURFACE_INTEGRITY_BASELINE_REQUIRED=YES。

NEXT=`{status['NEXT']}`，只记录，未执行。下一阶段才判断 RSSF/joint-derived/cap37/FIRST_WEB/freshR3/true-cap path metric/bind-deformation authorities 是否受影响，并决定 full true-cap recompute 或 narrow no-impact revalidation。随后才是 targeted MID15/30/45（45 mandatory）→ fresh Full42 → Human visual review → current9 closure resume → whole-hand surface integrity baseline → Stage6B consideration。本轮均未执行。

## 全部最终字段

| Field | Measured result |
|---|---|
{fields}

复现流程：prepare.py（实际哈希、prerequisites、历史快照）→ Blender extract_readonly.py（五份 actual clean reopen）→ Python revalidate.py（仅 acceptance blocks与diagnostics.py）→ deliver.py → validate_delivery.py。所有 solver和历史builder/audit顶层都未执行。完整 native data、math每点、正式2127 per-edge、局部112 edges与driver16×16关系均在本目录JSON。

[Evidence review](review.html)。STOP。
'''
(OUT/(PHASE+'_REPORT.md')).write_text(report,encoding='utf-8')
parts=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Palmar static skin compatibility R1</title><style>body{margin:0;background:#111923;color:#e1edf5;font:15px/1.65 system-ui}main{max-width:1450px;margin:auto;padding:28px}h1{font-size:27px}h2{margin-top:30px}a{color:#88ceff}table{border-collapse:collapse;width:100%;font-size:13px}td,th{padding:8px;border-bottom:1px solid #34485b;text-align:left;overflow-wrap:anywhere}.badge{display:inline-block;background:#235d43;border-radius:7px;padding:8px 14px}.notice{background:#34352c;padding:16px;border-radius:8px}code{overflow-wrap:anywhere}</style><main><h1>Palmar restoration · static skin compatibility</h1><p class="badge">PASS_STATIC_SKIN_COMPATIBILITY_REQUALIFIED · STOP</p><p>Fresh reopened 3416 vectors；2127/2127 formal edge records exact；all weight math violations 0。没有 weight / group 写入、solver 或 pose。</p><p class="notice">16 条 inherited copy-only debts 原样保留，未关闭 qualification 义务。Static compatibility PASS 的范围限于当前静态 contract；MID45 和 whole-hand baseline 继续 required。</p><h2>Palmar16 · actual driver weights</h2><table><tr><th>Vertex</th><th>MIDDLE_MCP</th><th>WRIST</th><th>RING_MCP</th><th>INDEX_MCP</th><th>Displacement mm</th></tr>']
for r in diag['per_vertex']:
 values=[str(r['vertex_id'])]+[format(r['focus_weight_contributions'][g],'.9f') for g in ('MIDDLE_MCP_R','WRIST_R','RING_MCP_R','INDEX_MCP_R')]+[format(r['displacement_mm'],'.9f')]
 parts.append('<tr>'+''.join('<td>'+escape(v)+'</td>' for v in values)+'</tr>')
parts.append('</table><h2>Geometry-sensitive context</h2><p>16×16 fixed deform-driver distance relations、48 incident edges、112 local-context edges。Weight-space metrics保持exact；physical gradient随边长变化单列。9个old/new法线负点积按照批准的native structure semantics保留为诊断，没有新增threshold。</p><h2>Inherited16 · preserved</h2><table><tr><th>Edge</th><th>Endpoints</th><th>L∞</th><th>L1</th><th>Classification</th></tr>')
for r in debts['edges']:parts.append('<tr>'+''.join('<td>'+escape(str(v))+'</td>' for v in [r['edge_id'],r['vertex_ids'],r['R2_metrics']['L_inf'],r['R2_metrics']['L1'],r['classification']])+'</tr>')
parts.append('</table><h2>Palmar16 frozen-authority intersections</h2><table>')
for k,v in intersection['intersections'].items():parts.append('<tr><td>'+escape(k)+'</td><td>'+str(v['count'])+'</td><td>'+escape(str(v['native_vertex_ids']))+'</td></tr>')
parts.append('</table><h2>全部最终字段</h2><table>')
for k,v in status.items():parts.append('<tr><td>'+escape(k)+'</td><td>'+escape(json.dumps(v,ensure_ascii=False))+'</td></tr>')
parts.append('</table><h2>Report / evidence</h2><ul>')
for p in sorted(OUT.glob('PALMAR*.json'))+sorted(OUT.glob('NORMAL69*.json'))+sorted(OUT.glob('DORSAL54*.json'))+sorted(OUT.glob('CURRENT9*.json'))+[OUT/(PHASE+'_REPORT.md'),OUT/(PHASE+'_STATUS.json'),OUT/'PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json']:parts.append('<li><a href="'+escape(p.name)+'">'+escape(p.name)+'</a></li>')
parts.append('</ul><p>NEXT geometry-dependent authority impact audit 仅记录。current9 HOLD_NOT_CLOSED。STOP。</p></main></html>')
(OUT/'review.html').write_text(''.join(parts),encoding='utf-8')
print('PASS_STATIC_SKIN_COMPATIBILITY_REQUALIFIED; protected files',len(before),'drift0; NEXT recorded only; STOP')
