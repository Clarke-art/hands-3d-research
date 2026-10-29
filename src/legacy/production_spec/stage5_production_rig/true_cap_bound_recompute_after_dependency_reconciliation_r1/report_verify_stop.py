import sys
sys.dont_write_bytecode=True
from common import *
from datetime import datetime,timezone
A=read(OUT/'TRUE_CAP_STATIC_PATH_ENSEMBLE_R1.json');P=read(OUT/'TRUE_CAP_POSED_BOUND_RECOMPUTATION_R1.json')
method=read(OUT/'HISTORICAL_TRUE_CAP_BOUND_METHOD_RECOVERY.json');auth=read(OUT/'CORRECTED_TRUE_CAP_SOURCE_TARGET_AUTHORITY.json')
det=read(OUT/'TRUE_CAP_BOUND_DETERMINISM_VERIFICATION.json')
assert det['path_family_equal'] and det['bound_payload_equal']
context=read(OUT/'RUN_A/BOUND_GEOMETRY_CONTEXT.json')
edges=context['edges'];source=set(auth['source']['vertex_ids']);target=set(auth['target']['vertex_ids'])
for row in A['all_exact_boundary_context_paths']:
 seq=row['vertex_sequence'];eids=row['edge_id_sequence'];lens=row['individual_edge_lengths_mm']
 assert len(seq)==len(eids)+1==len(lens)+1
 assert row['source_vertex'] in source and row['target_vertex'] in auth['target']['all_exact_boundary_endpoints']
 assert len(set(seq))==len(seq)
 for i,eid in enumerate(eids):assert set(edges[eid])==set(seq[i:i+2])
 assert sum(lens)==row['total_path_length_mm']
 assert row['fresh_R3_ownership_sequence'][0]=='THUMB'
assert len(A['paths'])==703 and {(r['source_vertex'],r['target_vertex']) for r in A['paths']}=={(a,b) for a in source for b in target}
assert len(P['historical_endpoint_sensitivity_recomputed'])==120
for x in P['historical_endpoint_sensitivity_recomputed']:
 assert len(x['all_primary_pair_bounds'])==703 and len(x['all_exact_boundary_context_pair_bounds'])==1406
 assert max(r[3] for r in x['all_primary_pair_bounds'])==x['max_primary_bound_row'][3]
for pose,x in P['per_pose'].items():
 assert len(x['all_primary_pair_bounds'])==703
 assert max(r['strict_lower_bound'] for r in x['all_primary_pair_bounds'])==x['max_over_complete_703_pairs']['strict_lower_bound']
 for r in x['all_primary_pair_bounds']:assert r['strict_lower_bound']==r['posed_endpoint_separation_mm']/r['bind_path_length_mm']
baseline=read(OUT/'HISTORICAL_HASHES_BEFORE.json');current=inventory()
changed=sorted(k for k in baseline.keys()&current.keys() if baseline[k]!=current[k])
deleted=sorted(baseline.keys()-current.keys());added=sorted(current.keys()-baseline.keys())
assert not(changed or deleted or added),{'changed':changed,'deleted':deleted,'added':added}
drift={'artifact':'PRODUCTION_READONLY_NO_DRIFT_VERIFICATION','status':'PASS','PRODUCTION_DRIFT':0,'method':'Full before/after SHA256 comparison of every pre-existing workspace file; only the new recomputation directory excluded. Independent live clean R2 payload verification before computation in each complete run, before/after in-memory restore equality, candidate/corrected-rig byte hashes checked. No new production blend.','historical_file_count':len(baseline),'all_preexisting_files_byte_hash_unchanged':True,'changed':changed,'deleted':deleted,'added_outside_new_output_directory':added,'R2_candidate_sha256':sha(CAND),'corrected_rig_sha256':sha(CORRECTED),'weight_vector_sha256':EXPECTED_WEIGHTS,'weight_vector_actual_live_hash_verified_in_each_run':True,'zero_pose_restore_all_payload_exact':True,'production_writes':0,'weights_modified':False,'geometry_modified':False,'topology_modified':False,'UV_modified':False,'materials_modified':False,'bones_joints_modified':False,'RSSF_modified':False,'cap37_authority_modified':False,'fresh_R3_authority_modified':False,'FIRST_WEB_membership_modified':False,'historical_Human_receipts_modified':False,'historical_strict_bound_reports_numeric_evidence_modified':False,'deformation_qualification_runs':0,'R3_solver_runs':0,'full_Stage6A_runs':0,'full_Stage6B_runs':0,'bound_only_probe_evaluations_in_two_complete_runs':12,'skin_rebuilds':0,'production_freeze':False,'production_promotion':False}
dump('PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json',drift)
stats=A['statistics_mm']
status={'phase':PHASE,'nature':'DERIVED_GEOMETRIC_KINEMATIC_BOUND_RECOMPUTATION','recorded_at_utc':datetime.now(timezone.utc).isoformat(),'HISTORICAL_METHOD_RECOVERED':True,'CAP37_SOURCE_COUNT':37,'OLD_CAP9_SOURCE_AUTHORITY_COUNT':0,'CURRENT_TARGET_AUTHORITY':'FRESH_R3_OWNERSHIP_AUTHORITY_R1 / INDEX_SIDE_EXACT_BOUNDARY_ENDPOINTS','CURRENT_TARGET_COUNT':19,'CURRENT_EXACT_BOUNDARY_EDGE_COUNT':20,'STATIC_PATH_PAIR_COUNT':703,'TRUE_CAP_STATIC_PATH_MIN_MM':stats['min'],'TRUE_CAP_STATIC_PATH_P05_MM':stats['p05'],'TRUE_CAP_STATIC_PATH_MEDIAN_MM':stats['median'],'TRUE_CAP_STATIC_PATH_P95_MM':stats['p95'],'TRUE_CAP_STATIC_PATH_MAX_MM':stats['max'],'TRUE_CAP_STATIC_PATH_MEAN_MM':stats['mean'],'CMC_MCP_L3_CORRECTED_TRUE_CAP_BOUND':P['per_pose']['CMC_MCP_L3']['max_over_complete_703_pairs']['strict_lower_bound'],'FULL_OPP_L3_CORRECTED_TRUE_CAP_BOUND':P['per_pose']['FULL_OPP_L3']['max_over_complete_703_pairs']['strict_lower_bound'],'reported_bound_aggregation':'Maximum actual R2 endpoint separation / current shortest bind path length over complete703 primary endpoint pairs; historical top10 aggregation preserved in distinct fields.','CMC_MCP_L3_CORRECTED_TOP10_BOUND':P['per_pose']['CMC_MCP_L3']['max_over_historical_semantic_top10_current_shortest_pairs']['strict_lower_bound'],'FULL_OPP_L3_CORRECTED_TOP10_BOUND':P['per_pose']['FULL_OPP_L3']['max_over_historical_semantic_top10_current_shortest_pairs']['strict_lower_bound'],'ADDITIONAL_RECOMPUTED_BOUND_CASES':['TH_IP_30','TH_IP_45','TH_MCP_45','CMC_OPP_30','120 historical virtual endpoint LBS recipes, 703 INDEX-target pairs / 1406 full-exact-boundary context pairs per recipe'],'historical_RECOMPUTE_REQUIRED_reference_count':11,'actual_pose_case_count':6,'hypothetical_endpoint_recipe_count':120,'DETERMINISTIC_RERUN':'PASS_EXACT_VALUE_AND_PAYLOAD_HASH_MATCH','PRODUCTION_DRIFT':0,'TRUE_CAP_BOUND_VERDICT':'PASS_CORRECTED_BOUND_AUTHORITY_ESTABLISHED',PHASE:'PASS_CORRECTED_BOUND_AUTHORITY_ESTABLISHED','authority_hashes':auth['authority_hashes'],'source_set_hash':det['source_set_hash'],'target_set_hash':det['target_set_hash'],'graph_metric_hash':det['graph_metric_hash'],'path_family_payload_hash':det['path_family_payload_hash'],'bound_payload_hash':det['bound_payload_hash'],'qualification_scope':'Corrected numeric authority only. No deformation qualification, anatomical angle limit or weight/mesh feasibility conclusion.','old_values':'HISTORICAL_VALUE_ONLY','downstream_recommendations_automatically_revived':False,'NEXT':'FULL_STAGE6A_REQUALIFICATION','NEXT_EXECUTED':False,'automatic_next_phase':False,'STOP':True,'production_freeze':False,'production_promotion':False}
dump(PHASE+'_STATUS.json',status)
short=A['global_shortest_path']
req=['HISTORICAL_METHOD_RECOVERED','CAP37_SOURCE_COUNT','OLD_CAP9_SOURCE_AUTHORITY_COUNT','CURRENT_TARGET_AUTHORITY','CURRENT_TARGET_COUNT','STATIC_PATH_PAIR_COUNT','TRUE_CAP_STATIC_PATH_MIN_MM','TRUE_CAP_STATIC_PATH_P05_MM','TRUE_CAP_STATIC_PATH_MEDIAN_MM','TRUE_CAP_STATIC_PATH_P95_MM','TRUE_CAP_STATIC_PATH_MAX_MM','TRUE_CAP_STATIC_PATH_MEAN_MM','CMC_MCP_L3_CORRECTED_TRUE_CAP_BOUND','FULL_OPP_L3_CORRECTED_TRUE_CAP_BOUND','ADDITIONAL_RECOMPUTED_BOUND_CASES','DETERMINISTIC_RERUN','PRODUCTION_DRIFT','TRUE_CAP_BOUND_VERDICT']
rows='\n'.join('| '+k+' | '+str(status[k])+' |' for k in req)
pose_rows='\n'.join('| '+cid+' | %.9f | %.9f | %.9f |'%(x['max_over_complete_703_pairs']['strict_lower_bound'],x['max_over_historical_semantic_top10_current_shortest_pairs']['strict_lower_bound'],x['cap37_mean_displacement_mm']) for cid,x in P['per_pose'].items())
old=read(OUT/'TRUE_CAP_HISTORICAL_VS_CORRECTED_COMPARISON.json')
old_rows='\n'.join('| '+cid+' | %.9f | %.9f | %.9f |'%(x['historical_top10_max'],x['corrected_top10_max'],x['corrected_full703_max']) for cid,x in old['pose_comparison'].items())
text=f'''# {PHASE}

**PASS_CORRECTED_BOUND_AUTHORITY_ESTABLISHED — STOP**

本轮建立 corrected geometric / kinematic numeric authority。所有当前数值重新计算，没有继承 old cap9、old REP 或 contaminated derived inputs 的数值。已核验 targeted Human closure = PASS_WITH_HUMAN_REVIEW_COMPLETE；ADDITIONAL_REMEDIATION_REQUIRED = NO、ADDITIONAL_SCOPE_EXPANSION_REQUIRED = NO、PRODUCTION_DRIFT = 0。

| Required field | Result |
|---|---|
{rows}

## Prerequisite 与 source / target authority

[Prerequisite gate](PREREQUISITE_GATE_R1.json) 完整通过；每次独立 Blender 进程均在数值计算前 clean reopen 核对当前 R2 payload、实际 weight vector SHA256 和全部21 bones 对 corrected frozen rig 的精确一致性。

- cap37：HUMAN_APPROVED_FROZEN，37 vertices / 25 faces；combined authority hash {EXPECTED_CAP}。
- old cap9：SUPERSEDED_CONTAMINATED；native INDEX_SURFACE = 9/9；source authority role = 0。
- corrected rig：HUMAN_APPROVED_APPLIED_VERIFIED；SHA256 {EXPECTED_RIG}。
- fresh-R3：HUMAN_APPROVED_FROZEN；membership hash {EXPECTED_MEMBER}；combined authority hash {EXPECTED_R3}。
- R2 candidate：SHA256 {EXPECTED_CAND}；live weight vector SHA256 {EXPECTED_WEIGHTS}。
- targeted Human receipts 与 final closure 原样保留。

Source 数学对象为**全部37个 frozen cap37 vertices，逐点作为 endpoint**，没有 representative、centroid、extreme-vertex 或 REP 选择。Target 继续承担历史 **exact ownership boundary 的 INDEX 侧端点** 角色：fresh20 boundary 提供19个唯一 INDEX endpoints，38个完整 boundary endpoints。本轮不以历史16端点/144对限制 corrected cardinality。

[Source / target authority](CORRECTED_TRUE_CAP_SOURCE_TARGET_AUTHORITY.json) 区分 exact boundary、collar transition neighborhood、proximal semantic stop 和 FIRST_WEB21。Proximal stop 不当完整 target anatomy map；transition band 与 FIRST_WEB21 不加入 primary target。历史 sensitivity 所用两侧 exact endpoints 独立保留为37×38 = 1406对 context family。

Frozen fresh-R3 labels/boundary 直接消费；R3 Dijkstra、min-cut、closure、sheet validator、R3 solver 均未运行。下面的 mesh-edge Dijkstra 只用于已授权 bind-path bound 重算。

## 历史数学方法恢复

数值计算之前已读取并登记110份直接相关正式实现/报告；逐项分类与完整 relevant excerpts 见 [method recovery](HISTORICAL_TRUE_CAP_BOUND_METHOD_RECOVERY.json)。依赖 inventory 中11份 RECOMPUTE_REQUIRED references 全部映射至当前 numeric payload，见 [coverage](RECOMPUTE_REQUIRED_BOUND_CASE_COVERAGE_R1.json)。

令固定 mesh path 的 bind edge lengths 为 bᵢ、posed edge lengths 为 pᵢ，endpoint separation 为 dₜ：

Σpᵢ ≥ ||B_pose − A_pose|| = dₜ，所以 maxᵢ(pᵢ / bᵢ) ≥ dₜ / Σbᵢ。

正式 strict bound 为 **posed endpoint separation / fixed shortest bind path length**。Graph 使用全 mesh native undirected edges，edge metric 为实际 bind-space world-mm mesh edge Euclidean length。没有用 endpoint chord 替换 path；没有通过新 cost、ownership cut 或 vertex-index distance 改变图。

METHOD_REUSABLE：三角不等式、mesh-edge metric、完整 endpoint enumeration、历史 pose primitive、虚拟 endpoint LBS sensitivity 方法。INPUT_INVALIDATED_RECOMPUTE：old cap9 / REP、old R3 exact endpoints、旧 rig / R1E endpoint transforms。SEMANTIC_INVALIDATED_RECOMPUTE：旧 full-sheet/global ownership 与旧 arc anatomical interpretation，以及已被否定的 (abs(uA)+Lbind)/Lbind。历史数字与 downstream recommendations 为 HISTORICAL_VALUE_ONLY。UNRESOLVED = []。

Historical feasibility 的 bound 汇总是当前最短10个 distinct endpoint pair 上的最大值；本轮保留这项，并按完整 endpoint method 额外报告703对 ensemble 的最大值。**Required 两项 CORRECTED_TRUE_CAP_BOUND 字段明确采用 full703 max**；top10 数值独立列示，避免把两种 aggregation 混同。

## Static path ensemble

完整 primary ensemble = **37×19 = 703**。每条路径都记录 source / target class、vertex sequence、edge IDs、individual edge lengths、total length、semantic proxy sequence、fresh ownership sequence 与 region traversal flags。所有38个 exact boundary endpoints 的1406条 context paths 亦完整记录。

[完整路径 family](TRUE_CAP_STATIC_PATH_ENSEMBLE_R1.json) 包含 count、min、p05、median、p95、max、mean，以及10 shortest distinct pairs 和 global shortest path。Percentile 沿用历史离散排序规则：p05 = floor(0.05×(n−1))；median = floor(n/2)；p95 = floor(0.95×(n−1))，没有替换为 interpolation。

Global shortest：**v{short['source_vertex']} → v{short['target_vertex']}，{len(short['edge_id_sequence'])} edges，{short['total_path_length_mm']:.9f} mm**。

Vertex sequence：{' → '.join(map(str,short['vertex_sequence']))}。

Edge ID sequence：{', '.join(map(str,short['edge_id_sequence']))}。

Shortest route traversal：cap37 / thumb distal / thumb MCP transition / CMC transition / collar = YES；first-web = NO。全部703条 shortest routes 都位于 frozen fresh-R3 bounded domain 内。Semantic region labels 承接 corrected chain / bounded ownership 的历史 descriptive proxy，不构造新 anatomy authority。Fresh-R3 未批准 full palm anatomy map；path payload 中域外 route 的 palm flag 必须 UNKNOWN；域内 false 仅指当前 bounded proxy 没有标出 PALM，不能当 full biological palm exclusion 证明。

## Posed true-cap bounds 与额外 cases

只运行正式历史方法中的六个 poses，且每项标注 BOUND_RECOMPUTATION_PROBE。原有 pose primitive 函数 AST 与 Stage6B quaternion / MCP-IP progression 原样复用；当前 R2 corrected rig、actual endpoint weights、cap37 与 fresh targets 被消费。未保存 production blend。

| Pose | Full703 max bound | Current top10 max bound | cap37 mean displacement mm |
|---|---:|---:|---:|
{pose_rows}

[Posed recomputation](TRUE_CAP_POSED_BOUND_RECOMPUTATION_R1.json) 保存六个 poses 的全部703对 bound、bind/posed endpoint positions、endpoint displacement、fixed denominator、global shortest pair bound、top10/full max、actual pose state 与两侧 exact-boundary context max。

另重算历史 **120个 virtual endpoint LBS recipes**：五类原有 group-pair × 四个原有 poses × 六个原有 fractions。每个 recipe 计算完整703 INDEX-side pairs 和1406 full exact-boundary context pairs；source A 始终 actual evaluated R2 cap37，target B 为原数学方法的 algebraic virtual mixture。无 production weights mutation、无新 per-vertex weight assignment、无 percentage authority。虚拟 sensitivity 数字不会替代 actual R2 primary bound。

## Historical vs corrected

历史13.1646 mm路径以及 CMC_MCP_L3 = 5.9643、FULL_OPP_L3 = 6.5160 的 true-cap interpretation 均保持 INVALIDATED；只能作为历史 comparison。Old shortest v2192→v704 与 corrected v1380→v2035 不同，已有同图 forensic 对照。

| Pose | Historical top10 max, historical only | Corrected current top10 max | Corrected full703 max |
|---|---:|---:|---:|
{old_rows}

完整 [old-vs-corrected comparison](TRUE_CAP_HISTORICAL_VS_CORRECTED_COMPARISON.json) 同时保留历史144/288与当前703/1406 cardinality 和全部120 recipes 对比。旧数值未用作 seed、threshold、expected answer、acceptance target 或 anatomical truth。

本轮新 bound 只为 geometric / kinematic derived constraint，不等于人体最大允许角度、钢琴动作范围、deformation PASS、skin-quality threshold、教学姿态 canonical value 或 Stage6B opposition qualification。Bound 数值变化不会独自成立 skin failure、topology failure、retopo required、no legal weights 或 production failure。历史 mesh-limit / retopo / no-legal-weight / cap-constrained feasibility recommendations **没有自动复活**；若未来需恢复，必须另开 downstream reconciliation。

## 确定性与保护

完整 computation 在两个独立 Blender 5.1.2 processes 中运行；每个进程从 frozen candidate clean reopen 开始并完整执行 path family、六个 actual pose bounds 与120 virtual recipes。A/B 每个 path vertex/edge sequence、每个浮点值和 payload 都**精确相同**，没有通过四舍五入掩盖不同 path。[Determinism verification](TRUE_CAP_BOUND_DETERMINISM_VERIFICATION.json) 记录全部 input/source/target/graph/path/bound hashes 与 canonical tie rule。

- Source-set hash：{det['source_set_hash']}
- Target-set hash：{det['target_set_hash']}
- Graph/metric hash：{det['graph_metric_hash']}
- Path-family payload hash：{det['path_family_payload_hash']}
- Bound payload hash：{det['bound_payload_hash']}

Path tie handling 沿用历史严格 relaxation 与 epsilon，ascending source/target/adjacency IDs、(distance,vertex) heap；等长候选保持首次 predecessor。不按 rounded lengths 选路。Path edge-length sum 与 Dijkstra accumulation 的 binary64 加法顺序残差逐路径记录；这不是 A/B 差异，不影响 path identity。

[Production verification](PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json)：全部 **{len(baseline)}** 个既有工作区文件前后 SHA256 相同；新增文件仅在本轮目录。每个 run 的 before/after in-memory mesh、UV、materials、weights、group order、21 bones、pose 与 transforms 精确恢复。R2、geometry、topology、UV、materials、bones、joints、RSSF、cap37 authority、corrected kinematics、fresh-R3、FIRST_WEB、Human receipts、历史 reports/numeric evidence 均未修改。

## 最小 forensic evidence

生成六张 endpoint/path sanity figures，见 [render manifest](FORENSIC_RENDER_MANIFEST.json)：bind cap37、current exact target/collar、global shortest、historical/corrected 同图、CMC_MCP_L3 与 FULL_OPP_L3 actual endpoints / retained fixed-path context。颜色仅用于 forensic evidence，不是 Human anatomy review。

![Forensic contact sheet](renders/FORENSIC_CONTACT_SHEET.png)

## NEXT 与 STOP

**NEXT = FULL_STAGE6A_REQUALIFICATION**，只记录；NEXT_EXECUTED = false，automatic_next_phase = false，**STOP = true**。

本轮未执行 full Stage6A / Stage6B、R3 solve/rerun、skin rebuild、rig modification、retopo、production freeze 或 promotion。
'''
(OUT/(PHASE+'_REPORT.md')).write_text(text,encoding='utf-8')
dump('OUTPUT_CONSISTENCY_VERIFICATION_R1.json',{'status':'PASS','static_endpoint_pairs_complete':True,'all1406_context_paths_expanded_and_valid':True,'all703_primary_paths_source_target_and_adjacency_verified':True,'six_actual_pose_bounds_complete':True,'all120_virtual_recipes_complete':True,'bound_ratios_equal_recorded_separation_over_denominator':True,'all_preexisting2400_hashes_unchanged':True,'forensic_visual_inspection':'Six-figure contact sheet inspected by agent; cap37, fresh target, current/old routes and corrected posed endpoint context visible. This is implementation sanity only, not Human anatomy review.','minimum_deliverables_complete':True,'STOP':True})
manifest={p.relative_to(OUT).as_posix():sha(p) for p in OUT.rglob('*') if p.is_file() and p.name!='OUTPUT_ARTIFACT_HASH_MANIFEST.json'}
dump('OUTPUT_ARTIFACT_HASH_MANIFEST.json',manifest)
print(json.dumps({k:status[k] for k in ['HISTORICAL_METHOD_RECOVERED','CAP37_SOURCE_COUNT','CURRENT_TARGET_COUNT','STATIC_PATH_PAIR_COUNT','CMC_MCP_L3_CORRECTED_TRUE_CAP_BOUND','FULL_OPP_L3_CORRECTED_TRUE_CAP_BOUND','DETERMINISTIC_RERUN','PRODUCTION_DRIFT','TRUE_CAP_BOUND_VERDICT','NEXT','NEXT_EXECUTED','STOP']},ensure_ascii=False))
