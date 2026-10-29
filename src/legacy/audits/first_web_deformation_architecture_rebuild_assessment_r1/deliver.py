import json,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1];PHASE='FIRST_WEB_DEFORMATION_ARCHITECTURE_REBUILD_ASSESSMENT_R1'
def read(n):return json.loads((OUT/n).read_text(encoding='utf-8'))
def dump(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
machine=read('KEY_SCREEN_MACHINE_R1.json');protected=read('POC_PROTECTED_CONTENT_VERIFICATION_R1.json');top=read('TOPOLOGY_INPUT_R1.json')
assert protected['status']=='PASS'
sources=[{'title':'Three.js SkinnedMesh','url':'https://threejs.org/docs/pages/SkinnedMesh.html','used_for':'Native bone/skin-index/skin-weight representation; architecture deployment inference, not a tested export.'},{'title':'Three.js Animation System','url':'https://threejs.org/manual/pages/animation-system.html','used_for':'Bone and morph animation support; helper/runtime or bake assessment.'},{'title':'Blender Lattice Modifier','url':'https://docs.blender.org/UATEST/manual/en/dev/modeling/modifiers/deform/lattice.html','used_for':'Lattice cage and vertex-group-local deformation mechanism.'}]
dump('WEB_DEPLOYMENT_PRIMARY_SOURCES_R1.json',{'sources':sources,'web_export_executed':False,'conclusions':'Engineering assessment; no Web POC or export validation in this phase'})
foldedges=[[416,2033],[2033,3145],[1565,3145],[1565,415],[415,1677],[1677,526]]
assert all(sorted(e) in [sorted(r['vertices']) for r in top['local_edges']] for e in foldedges)
audit={k:top[k] for k in ['source_baseline_sha256','vertex_count','bone_count','patch_ids','patch_vertex_count','patch_face_count','patch_polygon_sides','whole_mesh_polygon_sides','local_valence','local_edges','local_faces']}
audit.update({'CURRENT_FIRST_WEB_TOPOLOGY_ASSESSMENT':'REGULAR_QUAD_GRID_LOCAL_FOLD_BANDS_NO_TRIANGLE_OR_POLE_DEFECT','valence_summary':'All 149 selected vertices have global edge valence 4. All 120 fully contained faces are quads.','assessment':'Regular quad connectivity alone does not prove correct soft-tissue flow. F130 visible angular folding follows consecutive existing bridge edge bands, so one local spacing/refinement POC was justified. No claim that triangles or high-valence poles caused it.','visible_fold_edge_examples':foldedges,'fold_edge_authority':'Representative edge bands located from ordinary F130 surface view + local wire overlay; not a complete fold census or strain ranking.','wire_overlay':'CURRENT_F130_LOCAL_WIREFLOW.png','wire_overlay_note':'Projected whole selected patch edges include rear/occluded connections. Read together with ordinary solid view; no hidden crossing audit.','connectivity':'Local faces remain connected between index radial root and thumb-side/thenar bridge; the 149-node region is bounded rather than a whole digit/palm rebuild.','edge_directions':'Original ZERO and F130 edge vectors recorded only as read-only topology context. No mathematical strain score.','causal_confidence':'TOPOLOGY_AS_PRIMARY_CAUSE_NOT_ESTABLISHED','A_scope':'120 quads refined, 387 nodes added and 83 original interior nodes redistributed on original surface; perimeter ring transitions may be n-gons.','whole_hand_retopology':False})
audit['A_scope']=f"120 quads refined, {read('ROUTE_A_BUILD_R1.json')['added_vertex_count']} nodes added and {len(read('ROUTE_A_BUILD_R1.json')['relocated_old_vertex_ids'])} original interior nodes redistributed on original surface; perimeter ring transitions may be n-gons."
dump('CURRENT_FIRST_WEB_TOPOLOGY_AUDIT_R1.json',audit)
notes={
'A':{'130':'上部折边略顺，但下部阶梯深沟仍明显，斜视仍有角折。没有显著解决主要 blocker。','76':'上部过渡较顺，底部凹口保留；未达到自然连续桥面。','205':'中段稍平，upper-web 尖峰与深沟保留。','61':'出现比基线更明显的横向浅沟；低缺陷对照回退。','ZERO':'整体轮廓初判保持，原顶点最大差约 0.1694 mm。'},
'B':{'130':'桥面上缘轻微改变，主要阶梯深沟/凹口基本保留。','76':'主要凹口保留，upper-web 折边略尖。','205':'凹沟、上缘尖折基本保留。','61':'整体基本保持，轻微 crease 变化。','ZERO':'原网格不变，最大浮点差约 0.00012 mm。'},
'C':{'130':'没有有意义的深折改善；lattice 有实际求值但改变很小。','76':'凹口、深沟基本不变。','205':'小范围表面位移，主要角折/尖峰仍在。','61':'基本保持。','ZERO':'原外形完全保持，最大差 0 mm。'}}
names={'A':'A_LOCAL_RETOPOLOGY','B':'B_HELPER_BONE','C':'C_LOCAL_CAGE'}
routes={}
for label in 'ABC':
    build=read(f'ROUTE_{label}_BUILD_R1.json');rows=machine['conditions'][label]
    assert all(all(x==0 for x in r['minimum'].values()) and r['ZERO_restore']=='PASS' for r in rows)
    result={'route':names[label],'executed':True,'POC_count':1,'candidate':{'path':build['path'],'sha256':build['sha256']},'authority':'AGENT_PRELIMINARY_HUMAN_PENDING','F130_result':('PARTIAL_SURFACE_SMOOTHING_BLOCKER_REMAINS' if label=='A' else 'NO_MEANINGFUL_BLOCKER_REDUCTION'),'keyframe_notes':notes[label],'keyframe_clear_improvement_gate':'FAIL','route_stopped':True,'7S_result':'NOT_RUN_KEYFRAME_GATE_FAILED','representative_pose_regression':'NOT_RUN_KEYFRAME_GATE_FAILED','ZERO_regression':'PRELIM_ACCEPTABLE','NEW_VISIBLE_DEFECT_COUNT':1 if label=='A' else 0,'new_visible_defect_note':'F61 new/prominent shallow transverse first-web groove' if label=='A' else 'No distinct new defect category established in the screened frames; original blockers remain.','minimum_machine':{'NaN_Inf':0,'collapsed_face':0,'degenerate_edge':0,'ZERO_restore':'PASS','gross_visible_tearing':0,'gross_visible_penetration':0,'scope':'ZERO and four selected motion frames only; ordinary visible inspection, not hidden intersections.'},'build':build,'protected':protected['routes'][label],'formal_rebuild_started':False,'source_baseline_modified':False,'new_corrective_count':0}
    if label=='B':result['helper_bone_count']=1;result['second_helper_executed']=False;result['second_helper_reason']='F130 lacked a significant benefit; immediate route stop gate takes priority over optional second-helper allowance.'
    if label=='C':result['method']='LATTICE';result['other_cage_methods_executed']=False;result['implementation_limitations']='Coarse deterministic outward field, not a tissue solve. Activation uses differently rolled local quaternions, so it is a weak articulation proxy. POC physical cage covers a larger volume than the vertex mask; only the compact first-web mask affects the hand. No further tuning after failed key gate.'
    routes[label]=result;dump(f'ROUTE_{label}_RESULT_R1.json',result)
comparison={
'F130修复能力':{'A':'PARTIAL：上部平顺，深阶梯仍在','B':'FAIL：主要深折保留','C':'FAIL：无有意义改善'},
'F76/F205泛化':{'A':'PARTIAL：部分平顺，凹沟尖峰仍在','B':'FAIL：原 blocker 保留','C':'FAIL：原 blocker 保留'},
'完整7秒稳定性':{l:'NOT_TESTED：关键帧未过门槛' for l in 'ABC'},
'ZERO外形保持':{'A':'PRELIM_PASS：0.1694 mm 原顶点最大差','B':'PRELIM_PASS：0.00012 mm 浮点差','C':'PRELIM_PASS：0 mm'},
'六旧姿态regression':{l:'NOT_TESTED：关键帧未过门槛' for l in 'ABC'},
'新bulge/flap或可见回退':{'A':'F61 浅沟更明显；残留 flap','B':'残留 flap，upper fold略尖','C':'没有明显新 bulge；残留 flap'},
'维护复杂度':{'A':'MEDIUM：UV/旧 corrective 转移和边界整理','B':'LOW–MEDIUM：一个内部骨骼和固定矩阵混合','C':'HIGH：后置 cage 与 Web 表达一致性'},
'motion retarget兼容':{'A':'HIGH：21关节及原 Action不变','B':'HIGH：内部helper从原关节派生','C':'MEDIUM：需稳定的手部坐标/控制器定义'},
'左手镜像难度':{'A':'MEDIUM：局部流线、UV和形态审核','B':'LOW–MEDIUM：镜像锚点/rest矩阵','C':'MEDIUM–HIGH：cage坐标和位移方向重标定'},
'Three.js/Web实现难度':{'A':'LOW：仍为普通 bone+morph mesh','B':'LOW–MEDIUM：多一个骨骼，运行时矩阵派生或 helper 曲线烘焙','C':'HIGH：Blender lattice无法直接当标准bone+morph导入；需证明转换或额外后置deformation实现'},
'运行时性能':{'A':'LOW增量：387局部顶点；未benchmark','B':'LOW增量：1个骨骼和两个矩阵的简单混合；未benchmark','C':'MEDIUM–HIGH工程负担：局部cage插值或转译；未benchmark'},
'未来钢琴动作鲁棒性':{'A':'UNPROVEN：当前POC不足','B':'UNPROVEN：固定平均桥接不能保证更广动作','C':'UNPROVEN：当前场与激活代理不足'}}
reason='三份有界 POC 均未显著解决 F130 主 blocker，A 还让 F61 出现更明显浅沟；没有路线满足进入完整动作/旧姿态回归的前置门槛，因此当前不支持沿任一路线启动正式 rebuild。此选择限定于本轮证据，不宣称三类架构在所有设计下均不可能。'
dump('ARCHITECTURE_ROUTE_COMPARISON_R1.json',{'routes':routes,'comparison_dimensions':comparison,'RECOMMENDED_ROUTE':'NONE_OF_THREE','RECOMMENDATION_REASON':reason,'human_review_pending':True,'web_sources':sources,'web_export_performed':False,'performance_benchmark_performed':False})
status={'PHASE':PHASE,'SOURCE_BASELINE_SHA256':top['source_baseline_sha256'],'SOURCE_ACTION':'PIANOVAM_PHYSICAL_RIGHT_AXIS_CORRECTED_R1','SOURCE_MOTION_CHANGED':'NO','CURRENT_FIRST_WEB_TOPOLOGY_ASSESSMENT':audit['CURRENT_FIRST_WEB_TOPOLOGY_ASSESSMENT'],'SOURCE_WINDOW_SECONDS':[11.5,18.5],'SOURCE_OBSERVATIONS':421,'TESTED_MOTION_FRAMES':[130,76,205,61],'F31_STATUS':'NOT_RUN_ALL_ROUTES_STOPPED_AT_INITIAL_GATE','ZERO_REGRESSION':'PRELIM_ACCEPTABLE_ALL_THREE','REPRESENTATIVE_POSE_REGRESSION':'NOT_RUN_KEYFRAME_GATE_FAILED','NEW_VISIBLE_DEFECT_COUNT':1,'NEW_VISIBLE_DEFECT_COUNT_UNIT':'Distinct observed issue type, not frame census','RECOMMENDED_ROUTE':'NONE_OF_THREE','RECOMMENDATION_REASON':reason,'FORMAL_REBUILD_STARTED':'NO','FROZEN_BASELINE_MODIFIED':'NO','LEFT_HAND_STARTED':'NO','WEB_EXPORT_STARTED':'NO','PRODUCTION_PROMOTION':'NO','NEW_CORRECTIVE_COUNT':0,'FINGERTIP_ISSUE_STATUS':'DEFERRED','HUMAN_REVIEW':{'Q1':None,'Q2':None,'Q3':None,'Q4':None},'VERDICT':'NONE_OF_THREE_PROVEN_FOR_FORMAL_REBUILD','WORKFLOW_STATUS':'STOP_HUMAN_REVIEW'}
deploy={'A':'STANDARD_BONE_MORPH_COMPATIBLE_NOT_EXPORTED','B':'HELPER_BONE_RUNTIME_OR_BAKED_TRACK_COMPATIBLE_NOT_EXPORTED','C':'POST_SKIN_CAGE_TRANSLATION_OR_BAKE_REQUIRED_NOT_PROVEN'}
for l in 'ABC':
    for k,val in [('EXECUTED','YES'),('F130_RESULT',routes[l]['F130_result']),('7S_RESULT','NOT_RUN_KEYFRAME_GATE_FAILED'),('WEB_DEPLOYMENT',deploy[l])]:status[f'ROUTE_{l}_{k}']=val
status['ROUTE_B_HELPER_BONE_COUNT']=1;status['ROUTE_C_METHOD']='LATTICE'
dump(PHASE+'_STATUS.json',status)
report=f'''# {PHASE}

**RECOMMENDED_ROUTE = NONE_OF_THREE**。三条架构各做一份独立 DESIGN_ONLY POC，均未通过 F130 的显著改善门槛，因此按本轮指令停止各路线。完整 7 秒、F31 和六个旧姿态 regression 未执行，不把未知写成通过。四项 Human 审核均未填写。当前结论是没有路线已证明值得正式 rebuild，不是三类架构永远不可行。

{reason}

冻结基线 SHA256 `{top['source_baseline_sha256']}` 未改变。DQS route 根据本次 Human Q1=NO/Q2=NO/Q3=YES/Q4=NO 正式拒绝。没有复用失败 weight2 / real-motion corrective candidate。每份 POC 从 frozen baseline 独立加载，再追加原 `PIANOVAM_PHYSICAL_RIGHT_AXIS_CORRECTED_R1`，原 Action payload hash 均逐项相同。同一 sample、mapping iteration 2、smoothing、421 observations、11.5–18.5 秒保持不变。仅生成 ZERO/F130/F76/F205/F61 同视角 screen。

当前局部网格：149 节点、120 个完全位于区域中的 quad；整个 mesh 3298 面也是 quad，选区节点 global valence 全为 4。不能把这次失败归因为三角面或高 valence pole。F130 的多个可见角折沿相邻桥面网格带形成；读数与 wire overlay 仅作为布局背景，不做 strain/normal-dot/crossing census。代表折线附近边：416–2033、2033–3145、3145–1565、1565–415、415–1677、1677–526。投影线图会显示选区背面/遮挡连接，需和普通实体视图一起读；没有以它证明隐藏几何情况。原/变形 edge vectors、面连接、valence 保存在 CURRENT_FIRST_WEB_TOPOLOGY_AUDIT_R1.json。

|路线|本次 POC|F130|F76/F205|停止原因|
|---|---|---|---|---|
|A local retopology|120 quad 细化，增加387点；{len(read('ROUTE_A_BUILD_R1.json')['relocated_old_vertex_ids'])}个内部旧点做一次有界切向重新分布并投影回原表面；已有 weights 简单插值|上部稍顺，下部深阶梯仍在|部分顺滑，尖峰/凹沟保留|未显著解决主 blocker，F61新增/加重浅横沟|
|B helper bone|1个 INTERNAL_FIRST_WEB_BRIDGE_R1；两个既有 skin transforms 的中点锚点 + quaternion slerp，转入原 wrist parent；局部最大 helper weight {read('ROUTE_B_BUILD_R1.json')['helper_weight_max']:.4f}|主要深折基本不变|原凹口/尖折保留|主要 blocker 未改善；按立即停止门槛没有试第二个 helper|
|C local cage|一种方法：3×3×3 Lattice，位于原 LBS Armature 后；既有关节四元数差驱动有界2mm控制场，只影响局部mask|实际改变很小，深折不变|原 blocker 保留|没有有意义改善，不尝试其他 cage 或调整场|

A 是局部空间分布/细化的架构探针，不是完成的美术 retopo。已有相对 corrective delta 在旧节点保持，在新增节点按原场插值，driver 表达式和目标完全保留；没有 sculpt 新 corrective、没有修改源批准资产。由于新 topology，候选 Key 数组尺寸会改变，不能声称候选 corrective 的数组逐字节完全相同。A 的边界一圈相邻 faces 可能变为 n-gon，正式版本若获授权还需边界拓扑/UV整理；本轮不做。域外原节点坐标和实际非零 weights 完全一致；重建 datablock 省略部分零值 sparse memberships，不改变数值影响。

B 现有21教学骨骼 names/rest/parents/inherit及原动作完全保留。内部 helper 不需要 mocap channel，不作为教学关节。421 组 helper 变换由固定矩阵混合公式派生，存成单独 helper-only NLA Action；这只保证本段 clip 的 POC 可重放，未来一般动作需运行同一小公式，不能把 POC 烘焙当成泛化验证。保存后的四个 frame helper 矩阵与公式最大绝对差 {protected['routes']['B']['saved_helper_formula_matrix_max_abs_error']:.9g}。没有额外 helper tuning 或权重刷调。

C 保持原 mesh、原 bone weights、原 corrective/driver。只加一个 lattice modifier 和非骨骼 local mask group。选择 lattice 是因为局部有界体积位移、无绑定和仿真；没有再实现 Mesh Deform / Surface Deform。实际控制点 lattice 定义域与 object scale 使其空间覆盖大于局部mask；影响顶点范围仍仅限原 first-web 选区。激活量直接使用 index/thumb 不同 local frame 的四元数差，这是弱 articulation proxy，不把它当解剖测量或复杂 solver。F130 实际 mesh 最大变化 {protected['routes']['C']['lattice_actual_effect'][0]['max_mesh_displacement_mm']:.4f} mm，driver invalid=0，因此确有求值但未解决深折。此阴性结果仅针对该有界字段，不足以否定所有 cage 设计。

ZERO 四个普通视图：palmar full/thenar close/dorsal full/first-web close，三路线初判轮廓可接受。A 原节点最大变化 0.1694mm；B 0.00012mm 浮点量级；C 0mm。所有 screen NaN/Inf=0、collapsed face=0、degenerate edge=0、恢复各自ZERO=PASS；普通可见检查 gross tearing=0、gross penetration=0，残留虎口 fold 本身仍是 blocker。以上仅覆盖 ZERO 和四选中帧，不是完整421点安全验收，不证明 hidden intersections。未跑 Stage6/R3/true-cap/2127 edges/normal-dot 或其他复杂研究。

统一产品工程比较：

|维度|A|B|C|
|---|---|---|---|
'''+''.join('|'+dim+'|'+r['A']+'|'+r['B']+'|'+r['C']+'|\n' for dim,r in comparison.items())+'''
Web 结论为工程评估，未做导出或 benchmark。Three.js 原生 SkinnedMesh 支持 skeleton 与 skin indices/weights，Animation System 支持 bone/morph tracks，因此 A/B 可继续保留 bone+morph 形式；B 的 Blender 派生关系需要转成运行时小公式或仅helper烘焙曲线，不能假设 driver/constraint 会自动被 Web 导入。[SkinnedMesh 官方文档](https://threejs.org/docs/pages/SkinnedMesh.html)、[Animation System 官方文档](https://threejs.org/manual/pages/animation-system.html)。C 的后置 lattice 场超出这里使用的标准 bone+morph 表达，需证明离线转换后的语义等价或自定义后置层；不能仅因为 Blender 有效就认为产品可部署。Lattice 的 vertex group 限域机制参考 [Blender 官方文档](https://docs.blender.org/UATEST/manual/en/dev/modeling/modifiers/deform/lattice.html)。这是路线成本推断，未执行 Web 产品验证。

再打开保护验证已确认：所有原21骨骼 rest/inherit 与材料保持；B/C approved corrective 内容完全一致；A 保留并插值同一 approved 相对场、driver 完全一致；原 Action hash 一致；域外原 Basis/有效weights一致；源7个受保护文件哈希不变。保存 ZERO 时原 Action 被显式 retained（fake user）；序列化修正仅保留Action，没有改变 POC 设计。

交付 review.html、三份 POC blend、4条件×12=48张 matched renders、局部 topology/线图、各路线结果、12维成本比较和脚本。没有路线进入完整motion，所以不交付伪造或沿用旧clip的 POC视频；旧六姿态也明确 NOT_RUN_KEYFRAME_GATE_FAILED。被冻结的六姿态 Human批准仍属于原baseline，未重新授予POC。

Human 只需四题：

1. 三条路线中哪一条 first-web 外观最好？A / B / C / NONE
2. 该路线是否已经证明值得正式重建？YES / NO
3. 是否保持 Official L1 整体手型与旧姿态可接受？YES / NO（POC仅ZERO已检查，旧姿态未过门槛而未执行，不能视为已证明）
4. 是否同意下一阶段只沿推荐路线实施正式 rebuild？YES / NO

STOP — HUMAN REVIEW。正式 rebuild / production promotion / 左手 / Web export 均 NO。指尖继续 DEFERRED。不新增路线或继续局部patch。
'''
(OUT/(PHASE+'_REPORT.md')).write_text(report,encoding='utf-8')
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>First-web 架构评估 R1</title><style>body{margin:0;background:#101820;color:#e5edf5;font:16px/1.6 system-ui}main{max-width:1280px;margin:auto;padding:24px}h1{font-size:28px}h2{font-size:23px;margin-top:36px}.banner{padding:18px;background:#33271f;border:1px solid #cd976c;border-radius:10px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:10px}figure{margin:0}img{display:block;width:100%}figcaption{background:#24323e;padding:7px}.grid{display:grid;gap:18px}.hint{color:#b5c5d4}.sticky{position:sticky;top:0;background:#16232e;padding:12px;z-index:2;border:1px solid #425668;border-radius:7px;margin-top:20px}select{background:#293e4e;color:white;padding:8px;font-size:16px;border:1px solid #667d90;border-radius:6px}section{border-top:1px solid #394854;margin-top:24px}a{color:#92ccff}details{padding:12px;background:#1a2934}table{border-collapse:collapse;width:100%;font-size:14px}td,th{border:1px solid #435361;padding:7px;vertical-align:top}.tableScroll{overflow:auto}.links{display:flex;gap:20px;flex-wrap:wrap}</style><main>
<h1>First-web deformation architecture · R1</h1><p>冻结基线 → 三份独立 DESIGN_ONLY POC · 相同 Action / frame / camera / lighting</p><div class="banner"><b>推荐：NONE_OF_THREE · STOP — HUMAN REVIEW</b><br>没有 POC 显著解决 F130 主 blocker。A 上部稍平顺，但深折保留且 F61 多出浅沟；B/C 未见有意义改善。<br>按关键帧门槛，三路线均停止；完整7秒及六旧姿态 regression 未运行。</div>
<section><h2>1 · CURRENT BASELINE</h2><p class="hint">原批准 baseline 的真实动作缺陷。以下三个 reference frame 保持固定。</p><div id="baselineReferences" class="grid"></div><details><summary>局部拓扑审查 · 规则 quad / valence 4</summary><p>149节点、120个quad，没有triangle或高valence pole缺陷。绿色为整个选区投影线，会包含背面连接；只作为布局背景。</p><a href="CURRENT_F130_LOCAL_WIREFLOW.png" target="_blank"><img src="CURRENT_F130_LOCAL_WIREFLOW.png" alt="F130 local quad wireflow"></a></details></section>
<div class="sticky"><label for="caseSelect">同步比较帧 / 姿态 </label><select id="caseSelect"><option value="130">F130 · 主 blocker</option><option value="76">F76</option><option value="205">F205</option><option value="61">F61 · control</option><option value="ZERO">ZERO</option></select><span class="hint">　以下 A/B/C 同步切换；LEFT = BASELINE / RIGHT = POC</span></div>
<section><h2>2 · ROUTE A · Local first-web retopology</h2><p>一次局部网格细化/表面投影；原21骨骼和Action保留。旧corrective相对场转移，未新增corrective。</p><p id="noteA"></p><div id="routeA" class="grid"></div></section>
<section><h2>3 · ROUTE B · Hidden helper bone</h2><p>单个内部桥接骨骼；由INDEX_MCP/THUMB_CMC skin transforms中点和slerp派生。不作为教学关节。未试第二个helper。</p><p id="noteB"></p><div id="routeB" class="grid"></div></section>
<section><h2>4 · ROUTE C · Local lattice layer</h2><p>一种3×3×3 Lattice，原Armature之后，仅影响local mask。没有仿真，也没有试其它cage。</p><p id="noteC"></p><div id="routeC" class="grid"></div></section>
<section><h2>路线选择与产品成本</h2><div class="tableScroll"><table><thead><tr><th>维度</th><th>A</th><th>B</th><th>C</th></tr></thead><tbody>TABLE_ROWS</tbody></table></div><p>Web部署为工程评估，未导出或实测性能。普通bone/morph形式参考 <a href="https://threejs.org/docs/pages/SkinnedMesh.html">Three.js SkinnedMesh</a> 与 <a href="https://threejs.org/manual/pages/animation-system.html">Animation System</a> 官方文档。</p></section>
<section><h2>Human review · 四题</h2><ol><li>三条路线中，哪一条 first-web 外观最好？A / B / C / NONE</li><li>该路线是否已经证明值得正式重建？YES / NO</li><li>是否保持 Official L1 整体手型与旧姿态可接受？YES / NO</li><li>是否同意下一阶段只沿推荐路线实施正式 rebuild？YES / NO</li></ol><p class="hint">POC仅ZERO已检查；六旧姿态未执行，不能视为通过。本轮推荐NONE，不授权自动正式重建。</p><div class="links"><a href="FIRST_WEB_DEFORMATION_ARCHITECTURE_REBUILD_ASSESSMENT_R1_REPORT.md">完整报告</a><a href="FIRST_WEB_DEFORMATION_ARCHITECTURE_REBUILD_ASSESSMENT_R1_STATUS.json">状态</a><a href="ROUTE_A_LOCAL_RETOPOLOGY_POC_R1.blend">A POC</a><a href="ROUTE_B_HELPER_BONE_POC_R1.blend">B POC</a><a href="ROUTE_C_LOCAL_CAGE_POC_R1.blend">C POC</a></div></section>
<script>const notes=NOTES;function picture(l,p,v){let path=`${l.toLowerCase()}_selected/${l}__${p}__${v}.png`;return `<figure><figcaption>${l} · ${p}</figcaption><a href="${path}" target="_blank"><img src="${path}" alt="${l} ${p} ${v}"></a></figure>`}document.querySelector('#baselineReferences').innerHTML=[130,76,205].map(f=>`<div><h3>F${f}</h3><div class="pair">${['PALMAR_THENAR_CLOSE','FIRST_WEB_OBLIQUE'].map(v=>picture('BASELINE','F'+String(f).padStart(3,'0'),v)).join('')}</div></div>`).join('');function update(){let f=document.querySelector('#caseSelect').value;let pose=f==='ZERO'?'ZERO':'F'+f.padStart(3,'0');let views=f==='ZERO'?['PALMAR_FULL','THENAR_CLOSE','DORSAL_FULL','FIRST_WEB_CLOSE']:['PALMAR_THENAR_CLOSE','FIRST_WEB_OBLIQUE'];for(let l of ['A','B','C']){document.querySelector('#note'+l).textContent=notes[l][f];document.querySelector('#route'+l).innerHTML=views.map(v=>`<div><h3>${v}</h3><div class="pair">${picture('BASELINE',pose,v)}${picture(l,pose,v)}</div></div>`).join('')}}document.querySelector('#caseSelect').addEventListener('change',update);update();</script></main></html>'''
html=html.replace('NOTES',json.dumps(notes,ensure_ascii=False)).replace('TABLE_ROWS',''.join('<tr><td>'+dim+'</td>'+''.join('<td>'+r[l]+'</td>' for l in 'ABC')+'</tr>' for dim,r in comparison.items()))
(OUT/'review.html').write_text(html,encoding='utf-8')
for p,h in machine['inputs_unchanged'].items():assert sha(ROOT/p)==h
for r in routes.values():assert sha(ROOT/r['candidate']['path'])==r['candidate']['sha256']
print('ARCHITECTURE_REVIEW_READY_NONE_OF_THREE')
