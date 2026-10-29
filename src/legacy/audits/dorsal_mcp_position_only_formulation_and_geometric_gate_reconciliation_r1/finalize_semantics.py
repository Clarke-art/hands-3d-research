import sys
sys.dont_write_bytecode=True
from semantic_audit import *
from collections import Counter
from html import escape

STATUS='PASS_POSITION_ONLY_FEASIBILITY_REOPENED'
NEXT='MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R4_WITH_RECONCILED_GATES'

def contract():
 return {
  'phase':'PROPOSED_POSITION_ONLY_GEOMETRY_GATE_CONTRACT_R1','status':'PROPOSAL_ONLY_NOT_APPLIED','next_phase':NEXT,'execution_authority_granted':False,
  'scope':'Position-only local geometry design against immutable native mesh and frozen source. Mathematical feasibility diagnostics do not authorize production edits or validate Full42/Stage6.',
  'immutable':['Native V/E/F, vertex identities, face cycles and winding, edge incidence, triangulation convention','UV, material assignments, smooth/sharp attributes, custom-normal state','Weights, bones, joints, RSSF and every protected authority membership','Historical validators and all frozen historical/source assets'],
  'hard_fail':[
   {'id':'NATIVE_TOPOLOGY_CHANGE','predicate':'Any change to native identities, cycles, winding, counts, incidence or frozen triangulation.'},
   {'id':'DEGENERATE_FACE','predicate':'Zero-area native fan triangle or collapse anywhere on the proposed continuous path. Also audit vector-sum quad area; cancellation with positive fan areas must be separately classified, never hidden by a single quad-area scalar.'},
   {'id':'FACE_REVERSAL','predicate':'Certified material orientation reversal under a declared material-chart/path convention, including a zero signed material Jacobian. A chart-outward normal dot or normal rotation alone is not intrinsic 3D inversion. Require both explicit orientation convention and continuous area checks; absent convention fails certification.'},
   {'id':'NEW_NONADJACENT_EXACT_INTERSECTION','predicate':'New finite point/segment/area contact between nonadjacent native fan triangles, with exact feature membership, across the entire path.'},
   {'id':'NEW_OFF_SHARED_FEATURE_CROSSING','predicate':'Any new contact outside the exact native common vertex/segment or legal same-face diagonal. Sharing a vertex/edge is never a whole-pair exemption.'},
   {'id':'NEW_TRUE3D_SELF_INTERSECTION','predicate':'New intrinsic fan overlap or new extrinsic surface crossing. Positive-area coplanar overlap remains illegal even when the faces share a native edge.'},
   {'id':'UNRESOLVED_CONTINUOUS_PREDICATE','predicate':'An uncertified root, chart singularity, coplanar interval or degeneracy interval cannot be promoted to PASS from endpoint tests or a few samples.'}
  ],
  'conditional_no_regression':[
   {'id':'BASELINE_PROJECTED_BOWTIE','faces':[2771,3332,3351],'classification':'PROJECTION_ONLY_DIAGNOSTIC_INTRINSIC_FAN','rule':'Do not require absolute flag count zero. Freeze chart, camera, native cycle and sampling convention; require no new true3D defect and disclose fixed-view crossing parameters and sharpness. New flag/severity worsening triggers review unless independently ruled structural. An updated SVD chart may be reported separately, never substituted to hide regression.'},
   {'id':'BASELINE_SHARED_FEATURE_CONTACT','rule':'Remove only the actual shared simplex from collision barrier and active set. Continue finite off-simplex checks. There is no positive pair-wide adjacency distance or clearance floor.'},
   {'id':'BASELINE_COPLANAR_DIAGNOSTIC','rule':'A certified coplanar disjoint pair or exact shared-simplex-only contact is legal. Positive-area overlap is a real defect even if baseline-existing, never a projection-only exemption.'},
   {'id':'BASELINE_TRUE_CONTACT_COMPONENTS','rule':'Track native triangle IDs, finite features, connected intersection components and contact extents. No wholesale face-family whitelist. New components or penetration/extent worsening cannot inherit a baseline exemption. Existing true contacts remain independently recorded defects; a local no-new-defect result is not global production safety approval.'}
  ],
  'warning_human':['Local sharpness and crease appearance','Valley depth and contour naturalness','Reference/surrounding continuity and boundary normal progression','Projection-only artifact in declared views','AABB proximity, unsigned distance and plane-extension volume sign used only to activate finite-feature checks'],
  'feature_model':{'shared_vertex':'Exclude only the identical native point.','shared_edge':'Exclude only the actual closed segment, with exact on-segment predicate; no expanded strip.','native_fan_diagonal':'Same-face diagonal is legal; coplanar fan area overlap remains illegal.','2182_3330_specific':'Current edge79/955 contact is legal, but same-side coplanar fold limit has positive-area overlap. Retain this finite corner/edge barrier; the active row is not automatically spurious.','204_207':'Nonadjacent, source gap0.024319952mm; preserve finite vertex/triangle nonpenetration and relative tangent-motion causality.'},
  'continuous_collision':{'broadphase':'Swept whole-mesh AABBs for every changed-incident fan, plus explicit same-native-face fan pairs. Unchanged static pairs retain independently recorded source status.','noncoplanar':'Isolate coplanarity roots with certified intervals; verify finite barycentric/edge membership at events. Exact Bernstein sign certificates for complete pair oriented-matroid predicates can instead certify event-free subintervals.','persistent_coplanar':'Certify common plane, use a nonsingular chart, partition all continuous 2D orientation/edge events, clip finite polygons and subtract shared simplex at events and sign-invariant intervals. All-zero 3D volume polynomials do not imply safety.','rotating_common_plane':'Certify a projection-chart atlas and singularity events, or complete rank-3 chirotope sign preservation within a certified chart; require certified algebraic-root isolation on intervals with events.','implemented_here':'Fixed-plane rational-event controls and exact sign-preserving continuous micro certificates. No general-purpose rotating-plane CCD implementation or candidate production validator is claimed.','unresolved_policy':'FAIL_CLOSED_FOR_THE_TRIAL, refine predicate/interval/chart; never endpoint-only PASS.'},
  'tolerances':{'classification':'COMPUTATIONAL_GEOMETRY_TOLERANCE','anatomy_clearance_mm':0,'shared_edge_separation_floor_mm':0,'exact_narrowphase':'Rational predicates on stored binary64 inputs; no barycentric extension epsilon.','broadphase_padding_mm':1e-8,'micro_numeric_fan_area_screen_mm2':1e-10,'old_R3_tolerances':'Historical values are reproduced only for comparator results; not silently elevated into anatomy rules.','uncertain_float_result':'Refine to exact/certified predicates; fail closed if undecidable.'},
  'solver_formulation_proposal':{'objective':'Simultaneous dent diagnostic, native hinge progression and frozen reference/surrounding continuity descent; shape completion is a goal, not an impossible infinitesimal terminal threshold.','variables':'Coupled normal plus both tangents within a separately reviewed local position pool, smooth displacement/gradient/bending metric and immutable outer boundary. Mathematical111-vertex probe support grants no application authority.','strategy':'Feature-aware nonlinear SQP/trust-region or constrained descent, re-identify closest finite features and contact components after every trial. Keep genuine active off-edge rows, remove pure shared-simplex zero-distance rows.','acceptance':'Certified continuous true3D nonpenetration/orientation/area; projection-specific no-regression; meaningful objective decrease and boundary checks. A small-step progress heuristic alone cannot establish infeasibility.','next_validation':'Implement rotating-plane/event root certification and baseline component tracking before candidate safety certification; retain the full negative-control suite and source no-drift check.','not_proved':'Local micro descent does not prove a complete repair, all-pose nonintersection or natural valley appearance.'},
  'negative_control_requirement':{'required':'Every true crossing, same-side shared-edge overlap, intrinsic coplanar bow, material reversal/collapse, degeneracy and persistent-coplanar tunnel must block. Legal shared vertices/edges and the three intrinsic projection-only fans must pass their geometric test.','this_round_result':'16/16 PASS','evidence':'GEOMETRIC_GATE_NEGATIVE_CONTROLS_R1.json'},
  'historical_validator_modified':False,'clearance_increased':False,'production_promotion':False
 }

def run():
 local=read(OUT/'LOCAL_FEASIBLE_DESCENT_ANALYSIS_R1.json');bow=read(OUT/'PROJECTED_BOWTIE_SEMANTICS_AUDIT_R1.json');inv=read(OUT/'ACTIVE_SET_PAIR_INVENTORY_R1.json');neg=read(OUT/'GEOMETRIC_GATE_NEGATIVE_CONTROLS_R1.json');continuous=read(OUT/'CONTINUOUS_MICRO_WITNESS_CERTIFICATE_R1.json');shared=read(OUT/'SHARED_EDGE_CONTACT_SEMANTICS_R1.json');deriv=read(OUT/'OBJECTIVE_JACOBIAN_VALIDATION_R1.json')
 assert all(z['classification']=='PROJECTION_ONLY_DIAGNOSTIC' for z in bow['flags'].values())
 assert neg['TRUE_3D_NEGATIVE_CONTROLS_PASS'] and len(neg['controls'])==16
 assert all(z['status']=='CERTIFIED_CONSTANT_INTERSECTION_COMBINATORICS' and not z['baseline_intrinsic_illegal_fans'] for z in continuous['points'].values())
 for pt in local['points'].values():
  r=pt['directions'][0];assert r['all_three_objective_components_descend'];assert all(s['CURRENT_R3_ITERATION_GATE_PASS'] and s['R3_final_differential_geometry_gate_pass'] and s['reconciled_gate_pass'] for s in r['micro_steps'])
 dump('PROPOSED_POSITION_ONLY_GEOMETRY_GATE_CONTRACT_R1.json',contract())
 before=read(OUT/'HISTORICAL_HASHES_BEFORE.json');after=inventory();missing=sorted(set(before)-set(after));changed=sorted(k for k in before.keys()&after.keys() if before[k]!=after[k]);added=sorted(set(after)-set(before));assert not missing and not changed and not added,(missing,changed,added)
 assert sha(CAND)==EXPECTED_CAND
 drift={'phase':PHASE,'status':'PASS_BYTE_IDENTICAL','preexisting_files_checked':len(before),'preexisting_files_byte_identical':len(before),'changed_files':changed,'missing_files':missing,'unexpected_additions_outside_new_phase':added,'PRODUCTION_DRIFT':0,'frozen_production_source':ref(CAND),'expected_production_source_sha256':EXPECTED_CAND,'all_historical_R3_files_and_prior_temporary_assets_included':True,'new_output_scope':OUT.relative_to(ROOT).as_posix(),'blend_save_count':0,'geometry_candidate_count':0,'historical_validator_edit_count':0,'production_edit_count':0,'Full42':'NOT_RUN','Stage6A':'NOT_RUN','Stage6B':'NOT_RUN','ownership_R3':'NOT_RUN','skin_rebuild':'NOT_RUN','production_promotion':'NOT_RUN','inventory_before_sha256':sha(OUT/'HISTORICAL_HASHES_BEFORE.json')}
 dump('PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json',drift)
 status={'phase':PHASE,'status':STATUS,PHASE:STATUS,'ROOT_CAUSE_CLASS':'BASE_GEOMETRY_CONTOUR_DEFECT','PROJECTED_BOWTIE_2771':'PROJECTION_ONLY_DIAGNOSTIC','PROJECTED_BOWTIE_3332':'PROJECTION_ONLY_DIAGNOSTIC','PROJECTED_BOWTIE_3351':'PROJECTION_ONLY_DIAGNOSTIC','projection_classification_scope':'Intrinsic native fan; face3351 also has independently recorded baseline true contacts with2784/2787, which are not released.','SHARED_EDGE_2182_3330_RELATION':'LEGAL_SHARED_EDGE_AND_VERTICES_WITH_NO_BASELINE_OFF_EDGE_INTERSECTION','SHARED_EDGE_2182_3330_COPLANAR_LIMIT':'SAME_SIDE_POSITIVE_AREA_OVERLAP_REMAINS_HARD_FAIL','CURRENT_R3_GATESET_FEASIBLE_DESCENT_EXISTS':'NO','CURRENT_R3_GATESET_SCOPE':'Full R3 GEOMETRIC eligibility including absolute existing projected-flag elimination. Baseline and failed points themselves violate that terminal diagnostic; flags persist in an open local neighborhood. This is NOT iterative tangent-cone infeasibility. Shape completion thresholds are objectives, not infinitesimal feasibility constraints.','CURRENT_R3_ITERATION_GATESET_FEASIBLE_DESCENT_EXISTS':'YES','TRUE_3D_ONLY_GATESET_FEASIBLE_DESCENT_EXISTS':'YES','RECONCILED_GATESET_FEASIBLE_DESCENT_EXISTS':'YES','GATE_OVERCONSTRAINT':'CONFIRMED','GATE_OVERCONSTRAINT_SCOPE':'Terminal absolute projected-flag eligibility; not a claim that2182/3330 real off-edge barrier is unnecessary or that the iteration cone is empty.','SOLVER_FORMULATION_GAP':'CONFIRMED','SOLVER_FORMULATION_GAP_SCOPE':'Nonzero simultaneous descent at the failed point passes faithful existing iteration guards and lowers the actual cached R3 A4 soft-target residual. Published strategy stalled despite that local opportunity; no global-convergence theorem is claimed.','secondary_finding':'PASS_SOLVER_FORMULATION_GAP_CONFIRMED','TRUE_3D_NEGATIVE_CONTROLS_PASS':True,'negative_control_count':16,'POSITION_ONLY_ROUTE':'OPEN','POSITION_ONLY_INSUFFICIENT':'NOT_PROVED_GLOBALLY','TOPOLOGY_EXPRESSIVITY_LIMIT_EVIDENCE':'NOT_FOUND','TOPOLOGY_CHANGE_REQUIRED':'NOT_PROVED','RET0PO_REQUIRED':'NO','PRODUCTION_DRIFT':0,'preexisting_files_byte_identical':len(before),'local_variable_vertex_count':len(IDS),'local_variable_dimension':len(IDS)*3,'maximum_diagnostic_micro_step_mm':1e-4,'continuous_certified_joint_micro_step_mm':1e-5,'geometry_candidate_count':0,'new_micro_mesh_state_coordinates_saved':False,'source_feature_coordinates_in_audits':True,'normalized_mathematical_direction_vectors_saved':True,'historical_validator_modified':False,'NEXT':NEXT,'NEXT_EXECUTED':False,'STOP':'HUMAN REVIEW','unresolved_core_semantic_items':[],'future_implementation_requirements':['General event-producing rotating-plane CCD with certified root intervals','Component-level source contact non-regression and complete candidate safety certification','Full repair and appearance validation remain future work, without topology conclusions.']}
 dump(PHASE+'_STATUS.json',status)
 stats=Counter(z['classification_at_baseline'] for z in inv['pairs']);r=local['points']['R3_BEST_FAILED_POINT']['directions'][0];rr=r['derivatives'];c=continuous['points']['R3_BEST_FAILED_POINT'];height=shared['finite_shared_edge_fold_limit']['R3_BEST_FAILED_POINT']['preserved_signed_corner_to_opposite_triangle_plane_height_mm']
 bowrows='\n'.join('| '+fid+' | '+str(z['native_cycle'])+' | '+f"{z['native_vector_sum_face_area_mm2']:.9f}"+' | '+f"{min(t['minimum_3D_distance_mm'] for t in z['opposite_boundary_edge_tests']):.9f}"+' | PROJECTION_ONLY_DIAGNOSTIC |' for fid,z in bow['flags'].items())
 pairrows='\n'.join('| '+ '/'.join(map(str,z['face_ids']))+' | '+z['classification_at_baseline']+' | '+str(z['trace_occurrences'].get('constraint_occurrences',0))+' |' for z in inv['pairs'])
 report=f'''# {PHASE}

结果：**{STATUS}**。Position-only 路线保持 OPEN；同时确认局部 solver formulation gap。两项结论属于不同 gate 层次，不能合并为“真实3D约束已不可行”。

本轮仅做冻结数据读取、语义裁决、局部 Jacobian/方向锥、微步和负对照。未重跑 R3 搜索，未生成修复候选，未保存 blend 或修改生产 geometry、历史 validator。**STOP — HUMAN REVIEW。NEXT 未执行。**

## 三个投影标记

| Native face | Native cycle | 向量和面积 mm² | 实际对边最小间距 mm | 裁决 |
|---|---|---:|---:|---|
{bowrows}

每个面的两片原生扇三角面积均为正，内部只在合法对角线上相交；无该面的真实3D自交。边的 manifold incidence 均为2。JSON保留逐扇面积、法线、相对冻结ROI法线的 signed area、严格投影交点参数及 exact rational 接触证据。负法线点积或相对某个视图的负 signed area 是折叠/朝向诊断，不能单独当 intrinsic face inversion。

**3351 另有既有真实接触：2784/3351、2787/3351，交段约0.539691、0.541564 mm。**“投影标记是诊断”只裁决3351自身的 fan 与投影谓词，不把这两个真实 off-shared-feature 接触降级。2771、3332 的该项外部上下文检查未发现接触。所有 source-existing 实际接触独立保留，不能宣称全网格无交叉；历史 Stage6A old9 判级未重跑、未覆盖。

![三个原生面与投影](figures/PROJECTED_BOWTIE_3D_VS_CHART.png)

## 共边与具体 active barrier

2182=[3025,955,79,2327]；3330=[79,955,3340,3332]；共享 native edge79/955。基线与 R3 A-S4-V2 失败点的全部4个 fan-pair exact predicates均无边外交叉，只存在公共边/顶点接触。该天然零距离应从 pair-wide collision barrier 释放，不能人为增加 gap。

但当前对边角点3025、3340的垂直于公共边的射线几乎同向：基线 cosine≈0.9999995233，失败点≈1。失败点角点到对面三角形平面的保留侧高度约 **{height:.12g} mm**。若该折叠穿过同侧共面极限，会形成真实正面积重叠。因此 **2182/3330 当前有限 feature 的屏障必须保留**；自然共边零距离不证明这条具体 side row 是错误约束。实际 feature 的共面同侧/异侧对照分别 HARD FAIL/LEGAL，均验证通过。

沿选定联合方向，此侧高度导数约 +{rr['shared_edge_2182_3330_off_edge_finite_feature_side_height_derivative_mm_per_mm_peak']:.9f} mm/mm-peak，移动远离真实穿越边界。共享顶点只能豁免同一点，共边只能豁免实际闭线段，内部对角线只能豁免同一 native fan 的对角线；不豁免面、邻近条带或正面积重叠。

![共享边有限feature](figures/SHARED_EDGE_FINITE_FEATURE_RELATION.png)

## 局部下降及三个 gate 集合

数学变量为冻结 S4 的111个顶点、333维，仅位置方向；不构成应用授权。核心深度使用冻结 surrounding 二次曲面诊断，active core vertex=3025；连续性使用已经缓存的 R3 B-S4-V3 healthy reference 和位移/梯度/弯曲 metric，不重做健康参照选择。三个目标梯度 rank=3。线性方向锥解的最大约束欠量均小于4e-10；梯度与中心差分最大相对误差约 {max(z['max_relative_error'] for z in deriv.values()):.3g}。

在基线与 R3 最佳失败点均找到了非零 normal+tangent 联合方向。失败点代表方向 JOINT_METRIC_GRADIENT 的导数为：

| 量 | 导数（每1 mm最大顶点方向幅度） |
|---|---:|
| dent-depth mm | {rr['dent_depth_derivative_mm_per_mm_peak']:.9f} |
| edge6676 degree | {rr['edge6676_derivative_deg_per_mm_peak']:.9f} |
| reference/surrounding loss mm² | {rr['reference_continuity_derivative_mm2_per_mm_peak']:.9f} |
| R3 A4自身缓存 soft-target MSE mm² | {rr['R3_A_S4_V2_actual_soft_target_MSE_derivative_mm2_per_mm_peak']:.9f} |
| 非共享新接触最小间距 mm（204/207） | {rr['minimum_new_nonshared_separation_derivative_mm_per_mm_peak']:.9f} |
| 共边有限feature安全侧高度 mm | {rr['shared_edge_2182_3330_off_edge_finite_feature_side_height_derivative_mm_per_mm_peak']:.9f} |
| boundary progression loss degree² | {rr['boundary_normal_progression_loss_derivative_deg2_per_mm_peak']:.9f} |

204/207 基线间距0.024319952mm，失败点0.021028827mm；间距导数略负，但微步保持正间距，无人为增大 clearance。Boundary loss导数略正，是完整边界表中的微小连续性变化；所有检测微步仍通过原R3 boundary/no-new-obtuse screen，不把“连续性改进”误写成所有边界导数必为负。

| Gate 集合 | 可行下降 | 精确含义 |
|---|---|---|
| CURRENT_R3_GATESET（完整几何资格，含绝对投影标记清零） | NO | 起点本身不满足该最终资格。严格投影自交参数位于开区间，连续性使标记在局部开邻域内保留。 |
| CURRENT_R3_ITERATION_GATESET | YES | 原orientation函数AST复用；端点及0.25/0.5/0.75检查、原exact/CCD comparator全部通过。 |
| TRUE_3D_ONLY_GATESET | YES | 精确有限feature接触、连续非退化和无新结构缺陷的局部证据。 |
| RECONCILED_GATESET | YES | 真实3D硬约束加固定投影 no-new/no-regression，并保留共享边真实边外约束。 |

完整R3几何资格的 NO **不是** iterative tangent cone 空集，也不是对所有位置修改的不可行证明。修复最终深度/折角阈值是完成目标，不能作为 infinitesimal feasibility 的立即达标要求。R3原构造/投影/步长策略停滞，而代表方向还降低其自身 soft-target MSE，故局部 solver formulation gap 同时得到确认。

## 微步与连续认证

方向包括 joint metric、true3D cone、原R3 side-row cone、valley-axis tangent、cross-valley tangent、surface normal、历史净位移方向和有限接触激活的 cone。诊断幅度仅1e-6/1e-5/1e-4 mm，不做目标延续。失败点 cross-valley 单分量虽改善目标，却在所有三个诊断幅度触发真实新接触；联合方向全部通过。法线单分量局部微步合法，不证明它能够完成 R3 尺度的整体修复，不改变此前 normal-only 不足的结论。

代表联合方向在1e-5mm整个路径额外通过 **exact rational Bernstein / complete oriented-matroid sign certificate**：覆盖{c['whole_swept_and_intrinsic_pairs']}个 swept 或 intrinsic fan pair，含{c['intrinsic_fan_pairs_added']}个同一native face的fan pair；失败点检查{c['distinct_exact_cubic_predicates']}个不同有理数三次谓词。完整4点谓词包含合法shared simplex端点，所有符号保持，故有限凸单形交叉及共享feature归属的组合关系不变。未用“既有整对face豁免”；未决pair=0。所有受影响 native fan 基线本征非法交叉=0，微步全路径最小fan面积约0.170385mm²，未发生翻转/退化。

这证明 **局部 no-new-structural-defect 下降仍存在**，不证明源网格既有缺陷消失、全局最优、完整 dent 修复或所有姿态安全。一般微步JSON的端点统计采用face-family差集；只有代表连续证书额外消除了整对face豁免的证明漏洞。未来正式候选必须升级到component/feature non-regression，不能把family差集当最终安全标准。

![下降与gate对照](figures/LOCAL_DESCENT_AND_GATE_COMPARISON.png)

[固定源投影微步核验](FIXED_SOURCE_PROJECTION_MICRO_NO_REGRESSION_R1.json)另对三个标记使用同一个冻结source chart，记录前后交点参数与实际3D对边间距；代表微步无新增flag、无增加crossing count，实际边间距保持为正。参数位置不是解剖严重度评分，外观变化保留Human review。

## 全 trace pair inventory

读取全部{len(inv['all_trace_solve_ids_including_superseded'])}个已有R3 trace（含superseded，明确保留最终6个的身份），加 mandatory pairs，得到{inv['pair_count']}个面pair；基线分类计数：{dict(stats)}。分类不凭 unsigned distance=0，也不凭四点无限平面符号。

| Faces | 基线精确分类 | Active row出现次数 |
|---|---|---:|
{pairrows}

2181/3329 是既有非邻接真实接触，不能变为合法共享关系。局部全网格检查还独立记录10个已有真实接触family；它们不是 Stage6A old9 的替代判级。204/207 的历史相对切向运动因果保留，未被解释成单一坏点或大法线旋转。

## Persistent coplanar 与负对照

所有3D四点volume polynomial恒零时，仍需 common-plane chart中的连续2D边/顶点事件分区与 finite polygon overlap。固定共同平面上的有理数事件处理器检测到“两端不交、中途重叠”的 tunnel，同时通过始终只共边的合法路径。非有理事件根若未认证则 FAIL CLOSED；旋转共面路径需 chart atlas/root isolation，未来正式solver必须补齐，不能从本轮特定证书推定通用CCD已完成。

负对照 **16/16 PASS**：真实 nonadjacent crossing、历史R2-S5 204/207、true3D coplanar bow、shared-edge off-edge overlap、face material-path reversal/collapse、degenerate face、persistent tunnel均阻断；合法点/边/非共面折叠、合法persistent shared edge、三例intrinsic projection fans均通过；另加入当前2182/3330同侧非法与异侧合法共面feature对照。实际 crossing 不能因释放共享feature active-set而获豁免。

![共面负对照](figures/PERSISTENT_COPLANAR_NEGATIVE_CONTROL.png)

## 下一轮契约与停止点

[Proposed gate contract](PROPOSED_POSITION_ONLY_GEOMETRY_GATE_CONTRACT_R1.json)仅为草案：真实新非邻接交叉、边外穿越、native topology改变、材料方向翻转/连续退化及真实self-intersection仍hard fail；baseline projected/shared/coplanar diagnostics采用feature-aware conditional/no-regression；sharpness、crease、depth、naturalness及投影外观进入明确Human review。所有tolerance标记COMPUTATIONAL_GEOMETRY_TOLERANCE；新增anatomy clearance=0；未改历史validator。

未来方向：耦合法线/两切向、非线性feature-aware约束、每步有限feature重识别，持续保留2182/3330同侧穿越屏障，避免绝对baseline projected归零；把目标完成与迭代合法性分开。事件产生的旋转共面CCD、既有contact component不恶化、完整修复外观评估仍须在未来完成。

POSITION_ONLY_ROUTE=OPEN；POSITION_ONLY_INSUFFICIENT=NOT_PROVED_GLOBALLY；TOPOLOGY_EXPRESSIVITY_LIMIT_EVIDENCE=NOT_FOUND；TOPOLOGY_CHANGE_REQUIRED=NOT_PROVED；RET0PO_REQUIRED=NO。

NEXT={NEXT}。**本轮不执行NEXT；无候选、无生产修改。STOP — HUMAN REVIEW。**

## 只读核验与证据索引

全部{len(before)}个既有文件SHA256一致，changed/missing/unexpected outside addition均为0，覆盖生产、冻结authority、全部历史R3及既有临时资产。生产R2 blend SHA256={EXPECTED_CAND}。PRODUCTION_DRIFT=0；blend save=0。未运行Full42、Stage6A/6B、ownership R3、skin rebuild或promotion。

- [Status]({PHASE}_STATUS.json)
- [Gate classification](GEOMETRIC_GATE_SEMANTIC_CLASSIFICATION_R1.json)
- [Projected audit](PROJECTED_BOWTIE_SEMANTICS_AUDIT_R1.json)
- [Shared feature audit](SHARED_EDGE_CONTACT_SEMANTICS_R1.json)
- [Pair inventory](ACTIVE_SET_PAIR_INVENTORY_R1.json)
- [Local descent](LOCAL_FEASIBLE_DESCENT_ANALYSIS_R1.json)
- [Normal/tangent directions](NORMAL_TANGENT_COUPLED_DIRECTION_AUDIT_R1.json)
- [Continuous witness](CONTINUOUS_MICRO_WITNESS_CERTIFICATE_R1.json)
- [Jacobian validation](OBJECTIVE_JACOBIAN_VALIDATION_R1.json)
- [Negative controls](GEOMETRIC_GATE_NEGATIVE_CONTROLS_R1.json)
- [Persistent feature policy](PERSISTENT_COPLANAR_FEATURE_POLICY_R1.json)
- [No drift](PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json)
- [Visual review](review.html)

可复现脚本顺序：semantic_audit.py → local_analysis.py → negative_controls.py → continuous_witness.py → supplemental_diagnostics.py → forensic_figures.py → delivery_verification.py --fixed-projection → finalize_semantics.py → delivery_verification.py。OPENBLAS_NUM_THREADS=1；全部python用-B。仅复用历史纯函数AST，绝不执行历史solve/search入口；只在本轮新目录写文件。
'''
 (OUT/(PHASE+'_REPORT.md')).write_text(report,encoding='utf-8')
 pairhtml=''.join('<tr><td>'+ '/'.join(map(str,z['face_ids']))+'</td><td>'+escape(z['classification_at_baseline'])+'</td><td>'+str(z['trace_occurrences'].get('constraint_occurrences',0))+'</td></tr>' for z in inv['pairs'])
 controlshtml=''.join('<tr><td>'+escape(z['name'])+'</td><td>'+escape(z['expected'])+'</td><td class="pass">PASS</td></tr>' for z in neg['controls'])
 links=''.join(f'<li><a href="{escape(p.name)}">{escape(p.name)}</a></li>' for p in sorted(OUT.glob('*.json')) if p.name!='HISTORICAL_HASHES_BEFORE.json')
 html=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>几何 gate 语义核对 R1</title><style>body{{margin:0;background:#f3f6f8;color:#213849;font:16px/1.7 system-ui,"Microsoft YaHei",sans-serif}}main{{max-width:1150px;margin:auto;padding:40px 26px}}header{{padding:30px;background:#173747;color:white;border-radius:14px}}h1{{font-size:30px;margin:0}}h2{{font-size:23px}}.tag{{display:inline-block;padding:4px 10px;background:#23664e;border-radius:6px;font-size:14px}}section{{background:white;margin:22px 0;padding:26px;border:1px solid #d7e1e8;border-radius:12px}}a{{color:#126486;overflow-wrap:anywhere}}code{{overflow-wrap:anywhere}}img{{width:100%;height:auto;background:#f5f7fa}}table{{border-collapse:collapse;width:100%;font-size:14px}}td,th{{text-align:left;border-bottom:1px solid #dce5eb;padding:10px;overflow-wrap:anywhere}}.pass{{color:#237255}}.note{{background:#fff4df;border-left:4px solid #da9634;padding:14px}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}@media(max-width:750px){{.grid{{display:block}}main{{padding:15px}}header,section{{padding:20px}}table{{font-size:12px}}}}li{{margin:6px 0}}</style><main>
<header><span class="tag">{STATUS}</span><h1>钢琴 3D 手 · 几何 gate 语义核对</h1><p>Position-only 路线仍 OPEN。局部下降存在；最终投影资格过约束与求解策略缺口同时成立。</p><p>数学诊断 · 候选 0 · 生产漂移 0 · STOP — HUMAN REVIEW</p></header>
<section><h2>两层结论必须分开</h2><div class="grid"><div><h3>最终几何资格：过约束</h3><p>2771 / 3332 / 3351 的本征 fan 均属 PROJECTION_ONLY_DIAGNOSTIC。绝对要求既有投影标记清零，在局部邻域阻止最终资格通过。</p></div><div><h3>实际迭代空间：仍有下降</h3><p>R3 失败点的联合方向降低深度、6676折角、参考误差及自身soft-target残差，并通过原迭代检查。迭代 tangent cone 并未被证明为空。</p></div></div><p class="note">3351 与2784、2787的既有真实边外接触独立保留；投影重分类不放行这些接触。本轮证明局部 no-new-defect，不宣称源网格全局无交叉。</p></section>
<section><h2>三个投影标记的 3D 裁决</h2><img src="figures/PROJECTED_BOWTIE_3D_VS_CHART.png" alt="3D原生fan与SVD投影比较"><p><a href="PROJECTED_BOWTIE_SEMANTICS_AUDIT_R1.json">完整逐面证据</a></p></section>
<section><h2>共边合法，但同侧共面重叠仍禁止</h2><p>2182/3330共享79/955。起点只有合法edge/vertex接触；当前角点射线几乎同向，共面极限会有真实正面积重叠，因此有限feature屏障继续保留。联合方向增大安全侧高度。</p><img src="figures/SHARED_EDGE_FINITE_FEATURE_RELATION.png" alt="公共边接触与边外重叠区别"><p><a href="SHARED_EDGE_CONTACT_SEMANTICS_R1.json">Shared feature audit</a></p></section>
<section><h2>联合微步与连续证书</h2><p>111个数学变量顶点；诊断最大幅度0.0001mm。代表0.00001mm路径通过{c['whole_swept_and_intrinsic_pairs']}个swept/intrinsic pair的exact-rational符号保持认证，未决0；不依赖既有整对面豁免。</p><img src="figures/LOCAL_DESCENT_AND_GATE_COMPARISON.png" alt="下降方向导数及gate比较"><p><a href="LOCAL_FEASIBLE_DESCENT_ANALYSIS_R1.json">局部分析</a> · <a href="CONTINUOUS_MICRO_WITNESS_CERTIFICATE_R1.json">连续微步证书</a></p></section>
<section><h2>Persistent coplanar 与16个负对照</h2><img src="figures/PERSISTENT_COPLANAR_NEGATIVE_CONTROL.png" alt="共面中途重叠负对照"><details><summary>展开全部16个对照（16/16 PASS）</summary><table><thead><tr><th>Control</th><th>Expected</th><th>Result</th></tr></thead><tbody>{controlshtml}</tbody></table></details><p>一般旋转共面路径仍需认证chart atlas和事件根；本轮不宣称通用CCD实现已完成。</p></section>
<section><h2>全部已有R3 trace pair inventory</h2><p>{len(inv['all_trace_solve_ids_including_superseded'])}个已有trace，{inv['pair_count']}个pair；superseded身份保留。</p><table><thead><tr><th>Faces</th><th>Exact baseline class</th><th>Active rows</th></tr></thead><tbody>{pairhtml}</tbody></table></section>
<section><h2>只提出未来 gate contract</h2><p>硬阻断真实交叉、边外重叠、退化、材料方向翻转及拓扑变更；投影诊断按声明的视图做no-regression；天然共有点/边不设surface gap。所有容差为计算几何容差，新增anatomy clearance=0。</p><p><a href="PROPOSED_POSITION_ONLY_GEOMETRY_GATE_CONTRACT_R1.json">查看完整契约草案</a></p><p>TOPOLOGY_EXPRESSIVITY_LIMIT_EVIDENCE=NOT_FOUND；TOPOLOGY_CHANGE_REQUIRED=NOT_PROVED；RET0PO_REQUIRED=NO。</p><p class="note">NEXT={NEXT}。NEXT 未执行。停止在Human review，无修复候选、无生产修改。</p></section>
<section><h2>只读核验与文件</h2><p>{len(before)}个既有文件SHA256完全一致。PRODUCTION_DRIFT=0；changed / missing / unexpected outside additions=0。</p><p><a href="{PHASE}_REPORT.md">完整中文报告</a> · <a href="{PHASE}_STATUS.json">状态JSON</a></p><details><summary>证据JSON索引</summary><ul>{links}</ul></details></section></main></html>'''
 (OUT/'review.html').write_text(html,encoding='utf-8')
 manifest={'phase':PHASE,'artifacts':[ref(p) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='ARTIFACT_MANIFEST_R1.json' and not p.name.endswith('_LOG.txt')],'source_provenance':ref(OUT/'SOURCE_MODULE_PROVENANCE.json'),'historical_validators_edited':False,'geometry_candidate_count':0,'diagnostic_logs_excluded_from_hash_manifest':True}
 dump('ARTIFACT_MANIFEST_R1.json',manifest)
 print('FINALIZED',STATUS,'FILES_UNCHANGED',len(before),'DRIFT',0,'STOP HUMAN REVIEW',flush=True)
if __name__=='__main__':run()
