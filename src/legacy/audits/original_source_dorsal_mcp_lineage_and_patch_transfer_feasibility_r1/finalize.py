import sys,ast,html
sys.dont_write_bytecode=True
from common import *
S=read(OUT/'RAW_SOURCE_GEOMETRY.json')['stages'];T=read(OUT/'HISTORICAL_OPERATION_RAM_REPLAY.json');P=read(OUT/'TEMP_DONOR_TRANSFER_DESIGN_ONLY.json');gate=read(OUT/'PROBE_TRUE3D_STRUCTURAL_GATE.json');vis=read(OUT/'PROBE_VISUAL_GEOMETRY_DIAGNOSTICS.json');ops=read(OUT/'OPERATION_SEQUENCE_METRICS.json');G=read(OUT/'REVIEW_GEOMETRY.json')
assert gate['status']=='PASS'
builder=ROOT/'production_spec/stage4_blender/scripts/stage4a_r2_base.py';engineer=ROOT/'production_spec/stage4_blender/scripts/stage4a_engineer.py'
def funhash(p,name):
 node=next(n for n in ast.parse(p.read_text(encoding='utf-8-sig')).body if isinstance(n,ast.FunctionDef) and n.name==name)
 return hashlib.sha256(ast.dump(node).encode()).hexdigest()
event=T['events'][0];after=T['snapshots'][1];before=T['snapshots'][0]
changes=[]
for v in event['new_vertices']:
 i=v['vertex_id'];changes.append({**v,'post_plane_projection_local_m':after['local_m'][i],'before_subdivision_element':'Actual L1 parent edge / interpolation weights','affected_after_faces':[fi for fi,p in enumerate(after['faces']) if i in p]})
operation={'FIRST_DEFECT_ADJUDICATION':'DEFECT_INTRODUCED_DURING_STAGE4A_CON1_ENGINEERING','FIRST_CONFIRMED_CLEAN_STAGE':'OFFICIAL_BASE','LAST_CONFIRMED_CLEAN_STATE':'STAGE4A_L1_NORMALIZED_BEFORE_CON1','FIRST_CONFIRMED_DEFECT_STATE':'CON1_RING_MCP@-1mm','FIRST_CONFIRMED_FROZEN_DEFECT_STAGE':'STAGE4A_R2_BASE','TRANSITION_STEP':'Historical CON1 ring-edge subdivision followed by perpendicular finger-axis plane projection','operation_name':'CON1_RING_MCP@-1mm / insert_loop plane projection','script':str(builder.relative_to(ROOT)),'script_sha256':sha(builder),'function':'insert_loop','subdivide_lines':'612-613','projection_lines':'621-623','input_topology':{'V':3300,'E':6596,'F':3298},'output_topology':{'V':3316,'E':6628,'F':3314},'affected_new_vertices':changes,'sequence_metrics':ops,'first_step_max_projection_mm':event['receipt']['max_projection_mm'],'first_step_max_mapped_dihedral_deg':ops[1]['max_mapped_patch_dihedral_deg'],'before_max_mapped_dihedral_deg':ops[0]['max_mapped_patch_dihedral_deg'],'surface_preservation_semantics':'New edge points begin on actual donor edges. They are then moved along finger axis to a common deformation-loop plane. This is not donor surface projection/reprojection; it can leave the original surface and fold native fans. No donor surface preservation constraint follows.','donor_reprojection_present':False,'source_shape_preservation_bug':'Missing surface-preservation constraint in plane-projected loop design, rather than shading or an incorrect Stage2 layer selection. This trace demonstrates a geometry defect; it does not infer intent.','CON3_secondary_effect':'Pole738 is later lateralized twice; its 1-ring is smoothed factor0.5. It changes nearby donor positions by up to0.456mm, but first visible fold is already in the first CON1 snapshot.','stage4a_engineer_audit':{'path':str(engineer.relative_to(ROOT)),'sha256':sha(engineer),'insert_loop_AST_hash':funhash(engineer,'insert_loop'),'same_insert_loop_as_r2_base':funhash(engineer,'insert_loop')==funhash(builder,'insert_loop'),'role':'Earlier historical script, not the executed frozen R2_BASE producer. R2_BASE exact replay establishes the operative transition.'},'replay_semantics':'Only original historical operations executed in RAM, historical save section removed; exact final local coordinates and native cycles equal frozen R2_BASE. No alternative operation rebuild performed.','visual_before_after':['renders/TRACE_0_CLOSE_FLAT.png','renders/TRACE_1_CLOSE_FLAT.png']}
dump('DENT_FIRST_INTRODUCTION_OPERATION_AUDIT_R1.json',operation)
donor={'DONOR_SOURCE_AVAILABLE':'YES','RECOMMENDED_DONOR_SOURCE':'OFFICIAL_MULTIRES_L1','equivalent_donor':'STAGE2 enabled/evaluated L1; independently exact geometry and UV parity','selection_reasons':['Nearest actual unengineered geometric ancestor of Stage4A','Matched visible source has natural valley but no Human-target sharp fold','Exact L1 subdivision graph ancestry and actual historical split-parent weights recovered','Official stored Multires result is deterministic; no new sculpt or optimizer','Base cage is coarser and was not the real baked engineering input'],'OFFICIAL_BASE_TARGET_DENT_VISIBLE':'NO','OFFICIAL_L1_TARGET_DENT_VISIBLE':'NO','STAGE2_TARGET_DENT_VISIBLE':'NO','natural_source_valley_present':True,'distinction':'The inherited broad interdigit concavity exists; the Human-target sharp local shelf/fold does not. Do not equate a positive valley-depth proxy with the production blocker.','Human_approval':'PENDING_HUMAN_REVIEW','correspondence':'Validated entire official L1 oriented subdivision graph; historical edge-split barycentric weights; current ROI native identity; recovered frozen RSSF per-vertex transform.'}
dump('DONOR_SOURCE_SELECTION_R1.json',donor)
feas={'status':'PASS_LOCAL_DONOR_SHAPE_TRANSFER_FEASIBLE','NOT_PRODUCTION':True,'NOT_APPROVED':True,'probe':'TEMP_DONOR_TRANSFER_DESIGN_ONLY.blend','probe_sha256':P['blend_sha256'],'moved_vertex_count':len(P['moved_vertex_ids']),'max_displacement_mm':vis['max_displacement_mm'],'DONOR_RESTORE_CORE':P['DONOR_RESTORE_CORE'],'DONOR_TRANSITION_RING':P['DONOR_TRANSITION_RING'],'UNCHANGED_BOUNDARY':P['UNCHANGED_BOUNDARY'],'scope_method':P['scope_method'],'per_vertex_explanation_file':'TEMP_DONOR_TRANSFER_DESIGN_ONLY.json write_set','current_topology_preserved':True,'protected_payloads':'PROBE_PROTECTED_PAYLOAD_VERIFICATION.json, reopened saved file exact comparison','transfer_structural_gate':gate['status'],'contact_no_regression':gate['contact_no_regression'],'new_true3D_defect_counts':{k:gate[k] for k in ['new_nonadjacent_exact_intersection','new_off_shared_crossing','new_illegal_coplanar_overlap','new_face_reversal','new_degenerate','new_structural_bowtie','new_self_intersection']},'local_existing_contact_components_before':gate['baseline_counts']['component_count'],'local_existing_contact_components_after':gate['probe_counts']['component_count'],'remote_baseline_contacts':'All untouched coordinates/fans remain identical; no remote family is reclassified or claimed absent','visible_assessment':'Human-target angular shelf/fold absent in inspected matched close/grazing/side views; natural source valley retained. No new bulge or boundary crease visible in rendered views. Human acceptance pending.','max_ROI_dihedral_before_deg':vis['mapped_ROI_max_dihedral_before_deg'],'max_ROI_dihedral_after_deg':vis['mapped_ROI_max_dihedral_probe_deg'],'new_obtuse_boundary_edges':vis['new_obtuse_boundary_edges'],'initial_scope_diagnostic':{'files':['INITIAL_INCOMPLETE_SCOPE_38_PROBE.json','INITIAL_INCOMPLETE_SCOPE_38_GATE.json'],'result':'FAIL: omitted first cut ring sharing the same L1 parent edges; existing205/207 contact extent increased0.002749mm. Scope corrected by actual parent-edge ancestry closure, not fairing/optimization.'},'boundary_blending':'NONE','generic_geometry_optimizer_used':False,'Stage5_propagation':False,'true_cap_recompute':False,'targeted_deformation':False,'Full42_Stage6A':False,'Stage6B':False,'static_bind_preview':'NOT_RUN; static geometry gate/review suffices for this design-only feasibility round','INCIDENTAL_STAGE6A_CROSSING_EFFECT':'NOT_EVALUATED; all9 frozen severe crossings remain independent blockers','NEXT_EXECUTED':False}
dump('DONOR_PATCH_TRANSFER_FEASIBILITY_R1.json',feas)
lost=['MCP engineering loops/vertex IDs','CMC engineered cage','frozen RSSF geometry/frame','nail face/material semantic membership','current UV connectivity and mesh identity','production weight vector indexing','production bone/joint coordinate compatibility','fresh R3 membership authority','cap37 membership authority','true-cap derived authority','Stage6 evidence applicability']
comparison={'OPTION_A_FULL_ORIGINAL_MODEL_REPLACEMENT':{'feasible_as_independent_new_asset':True,'feasible_as_drop_in_production_replacement':False,'cost':'Would reset the production asset to831 cage vertices plus modifier, or3300 baked L1 vertices. Requires reengineering, rebinding/reweighting, semantic mapping, authority recovery and downstream requalification.','lost_or_invalidated':lost,'bone_note':'Old bone datablocks could be kept physically, but their asset compatibility and binding evidence do not survive wholesale replacement.','recommended':False},'OPTION_B_LOCAL_DONOR_SHAPE_TRANSFER':{'feasible':True,'preserved_exactly':['3416/6828/3414 topology','vertex IDs/native face cycles','current MCP/CMC edge connectivity','UV connectivity','material assignments/nail semantics','production weights','production bones/joints','authority files and memberships'],'still_requires_future_revalidation':['Production promotion approval','geometry-dependent true-cap/downstream evidence after any future formal amendment','targeted deformation and Stage6 qualifications under separately authorized task'],'existing_Stage6_pass_implied':False,'recommended':True},'FULL_REPLACEMENT_RECOMMENDED':'NO','LOCAL_DONOR_TRANSFER_RECOMMENDED':'YES','STAGE4_OPERATION_REBUILD_FEASIBLE':'YES_IN_PRINCIPLE_NOT_EXECUTED','rebuild_tradeoff':'An ancestry-preserving cut without plane projection can be designed; demonstrated donor-derived54-vertex probe supports that design. Whole Stage4A rerun could alter geometry-dependent seed selection/order and downstream IDs, so local fixed-topology restoration is the cleaner scoped amendment. No surface-preserving rebuild was executed.'}
dump('FULL_REPLACEMENT_VS_LOCAL_TRANSFER_R1.json',comparison)
status={PHASE:'PASS_LOCAL_DONOR_SHAPE_TRANSFER_FEASIBLE','OFFICIAL_BASE_DENT_VISIBLE':'NO_TARGET_SHARP_FOLD_NATURAL_VALLEY_PRESENT','OFFICIAL_L1_DENT_VISIBLE':'NO_TARGET_SHARP_FOLD_NATURAL_VALLEY_PRESENT','STAGE2_BOOTSTRAP_DENT_VISIBLE':'NO_TARGET_SHARP_FOLD_NATURAL_VALLEY_PRESENT','STAGE4A_R2_BASE_DENT_VISIBLE':'YES','FIRST_CONFIRMED_CLEAN_STAGE':'OFFICIAL_BASE','LAST_CONFIRMED_CLEAN_STAGE':'STAGE4A_L1_NORMALIZED_BEFORE_CON1','FIRST_CONFIRMED_DEFECT_STAGE':'CON1_RING_MCP@-1mm_RAM_TRACE / STAGE4A_R2_BASE_FIRST_FROZEN_FILE','FIRST_DEFECT_TRANSITION':'STAGE4A_CON1_RING_MCP@-1mm_EDGE_SUBDIVISION_THEN_PLANE_PROJECTION','FIRST_DEFECT_OPERATION_IDENTIFIED':'YES','FIRST_DEFECT_OPERATION':'stage4a_r2_base.py::insert_loop / CON1_RING_MCP@-1mm plane projection','DONOR_SOURCE_AVAILABLE':'YES','RECOMMENDED_DONOR_SOURCE':'OFFICIAL_MULTIRES_L1_EQUIVALENT_TO_STAGE2_EVALUATED_L1','DONOR_CORRESPONDENCE_METHOD':'EXACT_SUBDIVISION_GRAPH_ANCESTRY + HISTORICAL_SPLIT_EDGE_WEIGHTS + FROZEN_RSSF_LINEAR_TRANSFORM','CURRENT_TOPOLOGY_PRESERVED_IN_TRANSFER':'YES','TRANSFER_PROBE_CREATED':'YES_NOT_PRODUCTION_NOT_APPROVED','TRANSFER_STRUCTURAL_GATE':'PASS','TRANSFER_VISIBLE_DENT_STATUS':'TARGET_SHARP_FOLD_ABSENT_IN_INSPECTED_MATCHED_VIEWS_HUMAN_REVIEW_PENDING','TRANSFER_NEW_VISIBLE_DEFECT':'NONE_OBSERVED_HUMAN_REVIEW_PENDING','FULL_ORIGINAL_MODEL_REPLACEMENT_FEASIBLE':'NEW_ASSET_YES_DROP_IN_NO','FULL_REPLACEMENT_RECOMMENDED':'NO','LOCAL_DONOR_SHAPE_TRANSFER_FEASIBLE':'YES_DESIGN_ONLY_STATIC','LOCAL_DONOR_TRANSFER_RECOMMENDED':'YES','STAGE4_OPERATION_REBUILD_FEASIBLE':'YES_IN_PRINCIPLE_NOT_EXECUTED','TOPOLOGY_CHANGE_REQUIRED':'NO_FOR_THIS_PROBE','RET0PO_REQUIRED':'NO_NOT_PROVED_REQUIRED','PRODUCTION_DRIFT':0,'FULL_STAGE6A_REQUALIFICATION_R1':'FAIL_CLOSED_FULL_STAGE6A_REQUALIFICATION','UNAPPROVED_SEVERE_CROSSINGS':9,'NEXT':'LOCAL_DONOR_SHAPE_TRANSFER_AMENDMENT_DESIGN_R1','NEXT_EXECUTED':False,'STOP':'STOP — HUMAN REVIEW','human_approval':'NOT_APPROVED'}
status['RET0PO_REQUIRED']='NO'
dump(PHASE+'_STATUS.json',status)
report=f'''# 原始 source dorsal MCP lineage 与局部形状转移可行性 R1

**PASS_LOCAL_DONOR_SHAPE_TRANSFER_FEASIBLE — STOP — HUMAN REVIEW。**

官方 base / L1 与 Stage2 在同一物理区域有自然的指间谷，但没有 Human 指出的尖锐 shelf / 折叠。第一处明确缺陷出现在 Stage4A `CON1_RING_MCP@-1mm` 的 `insert_loop` 平面投影。官方 L1 可作为 shape donor。保存并独立重读的临时探针保留当前拓扑及保护数据，结构可行性通过；尚未获得 Human 视觉批准，未应用生产。

## Q1–Q3

| 问题 | 证据结论 |
|---|---|
| 官方原模型已有这个坑吗？ | 没有同样的尖锐折叠；原本的自然谷仍存在。请查看同机位 source-native / flat 五阶段图及原始 section。 |
| 首次在哪里引入？ | 官方 base → 官方 L1 → Stage2 均未出现该折叠。Stage4A 烘焙 L1、CON9 旋转后仍干净；首个 ring MCP 切环的平面投影立即出现锐折。 |
| 可保留当前工程 topology 只恢复 source shape 吗？ | 可行。54 个顶点根据 donor 父边 ancestry 恢复，经原有 frozen RSSF 坐标变换转入当前表面；临时文件的3416/6828/3414、native face cycles、UV、材质、weights、bones/joints 完全保留。 |

## 真实 lineage

Stage2 不是已应用 base 或 L1 的猜测选择：它保留官方831/1649/820 cage 与启用但未应用的官方 Multires L1。实测 source/Stage2 的 cage 坐标、边、faces、UV 完全相等；其真实 evaluated L1（3300/6596/3298）也完全相等。receipt 两个源文件 SHA256 均重新验证。

Stage4A 将真实官方 L1 烘焙，执行 mesh-data Rx180°，四次 CON1 边环 subdivision + plane projection，再作 CON3 pole 邻域处理，得到3364/6724/3362 R2_BASE。R2 CMC 工程后3416/6828/3414，Human ROI 的52顶点与36 native faces 精确保持；Stage4B RSSF 烘焙后交给 Stage4C / 当前 R2。`SOURCE_GEOMETRY_LINEAGE_R1.json` 提供实际 modifiers、counts、hashes 与构建脚本证据。

## 物理 ROI 与首次 operation

没有跨阶段套用 vertex ID。官方 L1 的每个 oriented 子 face cycle 都与 cage face/corner subdivision graph 核对。当前955追到官方 base79–80边的 L1 子顶点；新增工程点由历史实际 split 父边及 interpolation 权重追溯。R2_BASE 回放仅在 RAM 中执行原操作，剔除历史 SAVE 段；最终 local coordinates 与 native face cycles 和 frozen 文件精确相同。

首步 `CON1_RING_MCP@-1mm` 从3300/6596/3298变到3316/6628/3314，新增16顶点。新点原先在 donor 边上，随后沿 finger axis 投影到 deformation-loop plane，最大4.520mm。该操作没有 donor surface reprojection / preservation constraint。matched patch 最大二面角由60.157°变为169.833°；`-7mm`后177.904°。这是 comparative diagnostic，不是 anatomy threshold。`TRACE_0/TRACE_1`图可直接检查第一步前后。

CON3 后续 pole738两次位移及 smooth factor0.5 另改变邻域，但第一折叠在它之前已存在。`stage4a_engineer.py`的 `insert_loop` AST 与实际 R2_BASE producer相同；审计没有只凭文件名归因。

## Donor、scope 与临时探针

选择 actual official L1：它是 Stage4A 真实最近未工程化祖先，视觉表面正常，correspondence 确定。Stage2 evaluated L1 是精确等价 donor；coarse base 并非真实烘焙输入。仅恢复 shape，不剪 faces、不删除 loops、不换 topology。

scope 由实际 donor/current deviation、Human core 连通域和共享 L1 父边 ancestry 闭合得到54顶点，非15/52/111预设。每顶点理由、父权重和前后坐标在临时 JSON 的 `write_set`。最大位移{vis['max_displacement_mm']:.6f}mm；无需 boundary fairing。未连接的 DIP / CMC 操作保持不动。

初始38点 scope 漏掉共享相同 donor edges 的第一圈，205/207已有 contact 增长0.002749mm，严格 FAIL。其失败证据保留。依据真实 ancestry 补齐第一圈后得到54点探针，没有调整目标曲面或运行 optimizer。

冻结 RSSF 的历史 mathutils forward reconstruction 与保存 Stage4B local coordinates 精确相等。只是恢复已有坐标 correspondence，不修改 RSSF authority。double线性公式与原float32逐步累积存在0.000318mm最大数值差，实际探针 anchoring当前点并保存后重读；结构 gate 检查重读后的真实存储坐标。

## 结构与视觉可行性

| Gate | 结果 |
|---|---|
| native V/E/F / cycles / incidence | 完全相同 |
| UV / materials / smoothing / weights / bones / joints | 保存重读后与来源 payload 完全相同 |
| 新非邻接 exact intersection / off-shared crossing / 非法 coplanar overlap | 0 / 0 / 0 |
| 新 structural bow-tie / self-intersection / degenerate / face reversal | 0 / 0 / 0 / 0 |
| 新 true contact component / 既有恶化 / feature expansion | 0 / 0 / 0 |
| scope 内 source-existing true contact components | 12 → 0；远端未改变，不宣称全手无 contact |
| declared linear path 最小 native fan area | 0.021731568mm² > numerical area tolerance；该检查不等于完整 continuous collision certificate |
| ROI 最大局部二面角 | {vis['mapped_ROI_max_dihedral_before_deg']:.3f}° → {vis['mapped_ROI_max_dihedral_probe_deg']:.3f}° |
| 新 obtuse boundary edges | 0 |

gate 使用已 reconciliation 的 exact rational finite-feature predicates，并扣除真实共享 simplex。没有恢复 absolute projected bowtie zero。旧 contact 可以消失，不允许新增、扩张或恶化；完整 changed fan scope 对全手 unchanged mesh 检查。所有未移动 coordinates 精确相等。

已检查 matched close / grazing / side：原尖锐折叠不再出现，自然 source 谷保留；未观察到新鼓包或边界锐折。整体 arch 除54点外逐坐标相同。原始 Human camera 640×800、full dorsal、wire、silhouette、0/60/120实际三角面切线均在 review。视觉结论仍待 Human；metrics绝不代替 anatomy批准。

## 整手替换 vs 局部恢复

**不推荐整手替换；推荐局部 donor shape transfer amendment design。** 原模型可作为另一个新资产，不能直接作为当前 production replacement。替换会重置 MCP/CMC、mesh IDs/UV/nail semantics，要求重新 binding/weights、bone compatibility、fresh R3、cap37、true-cap及 Stage6证据。局部探针保留这些数据和authority文件；未来正式 shape amendment 仍需重新验证 geometry-dependent derived authority 与下游资格，不能沿用旧通过结论。

surface-preserving Stage4 operation rebuild 原理上可设计，但未执行；重跑可能改变 geometry-dependent seed selection、顺序和 downstream IDs。当前 fixed-topology 局部恢复是更明确的范围。

## 保护与停止

官方、Stage2、所有 historical/frozen assets 与 production文件按全项目SHA256前后核验；新输出只在本轮audit目录。详见 `PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json`。未执行 formal amendment、Stage5 propagation、true-cap recompute、targeted deformation、Full42、Stage6B、retopo或正式promotion。

Stage6A继续 `FAIL_CLOSED_FULL_STAGE6A_REQUALIFICATION`，9个unapproved severe crossings独立存在；未运行也未裁决 incidental crossing effect。探针明确 **NOT_PRODUCTION / NOT_APPROVED**。

NEXT只记录 `LOCAL_DONOR_SHAPE_TRANSFER_AMENDMENT_DESIGN_R1`，未执行。**STOP — HUMAN REVIEW**。

## 最终字段

| 字段 | 结果 |
|---|---|
'''+''.join(f'| `{k}` | {v} |\n' for k,v in status.items())
(OUT/(PHASE+'_REPORT.md')).write_text(report,encoding='utf-8')
def section_svg(label,ang,labels):
 segs=G['stages'][label]['sections'][str(ang)];parts=[]
 for s in segs:
  p=s['profile_mm'];points=' '.join(f'{300+a*22:.3f},{120-b*15:.3f}' for a,b in p)
  parts.append(f'<polyline points="{points}" fill="none" stroke="#244b69" stroke-width="2"/>')
 return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 240"><rect width="600" height="240" fill="#f3f6f8"/><path d="M20 120H580 M300 15V225" stroke="#b7c6cf"/><text x="12" y="20" font-size="13">shared physical scale • tangent mm / outward mm</text><text x="300" y="236" font-size="13">0</text><text x="520" y="236" font-size="13">10 mm</text>'+''.join(parts)+'</svg>'
views=[('CLOSE','近景 solid'),('HUMAN','Human 原始640×800机位'),('FULL_DORSAL','整体手背'),('GRAZING','掠射光'),('WIRE','实际 wire'),('SIDE','侧面'),('SILHOUETTE','Silhouette')]
def panel(labels,title):
 body=f'<section><h2>{title}</h2><p class="labels">'+''.join(f'<span>{html.escape(l)}</span>' for l in labels)+'</p>'
 for view,name in views:
  for shade in ['FLAT','SOURCE_NATIVE']:
   body+=f'<h3>{name} · {shade}</h3><div class="grid" style="--n:{len(labels)}">'
   for l in labels:
    fn=f'renders/{l}_{view}_{shade}.png';body+=f'<a href="{fn}" target="_blank"><img loading="lazy" src="{fn}" alt="{l} {view} {shade}"><span>{l}</span></a>'
   body+='</div>'
 for angle in [0,60,120]:
  body+=f'<h3>{angle}° actual mesh cross-section · 共用坐标尺度</h3><div class="grid" style="--n:{len(labels)}">'
  for l in labels:
   fn=f'figures/{l}_SECTION_{angle}.svg';(OUT/'figures').mkdir(exist_ok=True);(OUT/fn).write_text(section_svg(l,angle,labels),encoding='utf-8');body+=f'<a href="{fn}" target="_blank"><img src="{fn}" alt="{l} section {angle}"><span>{l}</span></a>'
  body+='</div>'
 return body+'</section>'
review='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>原始 source lineage / donor transfer R1</title><style>body{font-family:system-ui,sans-serif;background:#e8edf0;color:#172e40;margin:0;padding:24px}header,section{max-width:1600px;margin:auto auto 28px;padding:24px;background:white;border-radius:12px}h1{font-size:26px}h2{font-size:22px}.badge{display:inline-block;background:#dceee6;padding:8px 14px;border-radius:7px;font-weight:700}.note{background:#fff1cd;padding:16px;border-radius:7px}a{color:#285d82}.grid{display:grid;grid-template-columns:repeat(var(--n),minmax(0,1fr));gap:10px}.grid a{text-decoration:none;text-align:center;background:#eef2f5;border-radius:6px;overflow:hidden}.grid img{width:100%;display:block}.grid span{display:block;padding:8px;font-size:12px}.labels{display:flex;justify-content:space-around;font-size:12px}h3{margin:24px 0 10px;font-size:17px}.fields{overflow:auto}table{border-collapse:collapse;font-size:13px}td{border-bottom:1px solid #ddd;padding:8px}nav{display:flex;gap:16px;flex-wrap:wrap}p{line-height:1.7}</style><header><h1>原始 source lineage 与局部 shape transfer R1</h1><p class="badge">PASS_LOCAL_DONOR_SHAPE_TRANSFER_FEASIBLE</p><p class="note">NOT_PRODUCTION · NOT_APPROVED · STOP — HUMAN REVIEW<br>官方 L1 未见同样的尖锐折叠。首次在 Stage4A CON1_RING_MCP@-1mm 平面投影出现。临时54点 donor恢复结构通过；尚未批准生产。</p><p>请检查：原模型是否有同样的坑、probe是否消除尖锐折叠、有无新鼓包或边界锐折、整体 arch是否自然。自然指间谷保留。点击图像可打开全尺寸。</p><nav>'''
review+=f'<a href="{PHASE}_REPORT.md">完整报告</a><a href="{PHASE}_STATUS.json">最终状态</a><a href="DENT_FIRST_INTRODUCTION_OPERATION_AUDIT_R1.json">首次 operation 证据</a><a href="PROBE_TRUE3D_STRUCTURAL_GATE.json">true3D gate</a><a href="TEMP_DONOR_TRANSFER_DESIGN_ONLY.blend">临时 Blender 探针</a></nav><p>54点；V/E/F3416/6828/3414；新 contact / worsening / expansion =0/0/0。原 Stage6A的9个 severe crossings独立保留，未重跑。</p></header>'
review+=panel(['STAGE4C_R2','OFFICIAL_L1','TRANSFER_PROBE'],'CURRENT / DONOR SOURCE / TRANSFER PROBE · 三列 Human review')
review+=panel(['OFFICIAL_BASE','OFFICIAL_L1','STAGE2_L1','STAGE4A_R2_BASE','STAGE4C_R2'],'真实 source lineage · 五列同机位')
review+='<section><h2>First defect operation · before / after</h2><p>同一物理 source frame：L1归一化后 → CON1_RING_MCP@-1mm。初步169.833°锐折已出现，CON3尚未执行。</p><div class="grid" style="--n:2">'+''.join(f'<a href="renders/TRACE_{i}_CLOSE_FLAT.png" target="_blank"><img src="renders/TRACE_{i}_CLOSE_FLAT.png" alt="operation {i}"><span>{T["snapshots"][i]["name"]}</span></a>' for i in [0,1])+'</div></section>'
review+='<section class="fields"><h2>最终裁决字段</h2><table>'+''.join(f'<tr><td>{html.escape(k)}</td><td>{html.escape(str(v))}</td></tr>' for k,v in status.items())+'</table></section></html>'
(OUT/'review.html').write_text(review,encoding='utf-8')
print('Required adjudication/report/review artifacts written',flush=True)
