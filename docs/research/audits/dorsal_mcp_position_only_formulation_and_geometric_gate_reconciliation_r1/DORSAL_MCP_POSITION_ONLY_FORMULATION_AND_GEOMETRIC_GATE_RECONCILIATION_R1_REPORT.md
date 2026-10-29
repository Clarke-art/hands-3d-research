# DORSAL_MCP_POSITION_ONLY_FORMULATION_AND_GEOMETRIC_GATE_RECONCILIATION_R1

结果：**PASS_POSITION_ONLY_FEASIBILITY_REOPENED**。Position-only 路线保持 OPEN；同时确认局部 solver formulation gap。两项结论属于不同 gate 层次，不能合并为“真实3D约束已不可行”。

本轮仅做冻结数据读取、语义裁决、局部 Jacobian/方向锥、微步和负对照。未重跑 R3 搜索，未生成修复候选，未保存 blend 或修改生产 geometry、历史 validator。**STOP — HUMAN REVIEW。NEXT 未执行。**

## 三个投影标记

| Native face | Native cycle | 向量和面积 mm² | 实际对边最小间距 mm | 裁决 |
|---|---|---:|---:|---|
| 2771 | [3348, 3357, 1019, 119] | 1.626121473 | 0.108425363 | PROJECTION_ONLY_DIAGNOSTIC |
| 3332 | [80, 956, 3341, 3339] | 3.347375006 | 0.343273164 | PROJECTION_ONLY_DIAGNOSTIC |
| 3351 | [123, 3351, 3361, 1023] | 0.165734394 | 0.045424101 | PROJECTION_ONLY_DIAGNOSTIC |

每个面的两片原生扇三角面积均为正，内部只在合法对角线上相交；无该面的真实3D自交。边的 manifold incidence 均为2。JSON保留逐扇面积、法线、相对冻结ROI法线的 signed area、严格投影交点参数及 exact rational 接触证据。负法线点积或相对某个视图的负 signed area 是折叠/朝向诊断，不能单独当 intrinsic face inversion。

**3351 另有既有真实接触：2784/3351、2787/3351，交段约0.539691、0.541564 mm。**“投影标记是诊断”只裁决3351自身的 fan 与投影谓词，不把这两个真实 off-shared-feature 接触降级。2771、3332 的该项外部上下文检查未发现接触。所有 source-existing 实际接触独立保留，不能宣称全网格无交叉；历史 Stage6A old9 判级未重跑、未覆盖。

[三个原生面与投影](../../../artifacts/9b4e051943661c00ef06.md)

## 共边与具体 active barrier

2182=[3025,955,79,2327]；3330=[79,955,3340,3332]；共享 native edge79/955。基线与 R3 A-S4-V2 失败点的全部4个 fan-pair exact predicates均无边外交叉，只存在公共边/顶点接触。该天然零距离应从 pair-wide collision barrier 释放，不能人为增加 gap。

但当前对边角点3025、3340的垂直于公共边的射线几乎同向：基线 cosine≈0.9999995233，失败点≈1。失败点角点到对面三角形平面的保留侧高度约 **7.06432814799e-08 mm**。若该折叠穿过同侧共面极限，会形成真实正面积重叠。因此 **2182/3330 当前有限 feature 的屏障必须保留**；自然共边零距离不证明这条具体 side row 是错误约束。实际 feature 的共面同侧/异侧对照分别 HARD FAIL/LEGAL，均验证通过。

沿选定联合方向，此侧高度导数约 +0.665406020 mm/mm-peak，移动远离真实穿越边界。共享顶点只能豁免同一点，共边只能豁免实际闭线段，内部对角线只能豁免同一 native fan 的对角线；不豁免面、邻近条带或正面积重叠。

[共享边有限feature](../../../artifacts/7518b7f518256b3764f6.md)

## 局部下降及三个 gate 集合

数学变量为冻结 S4 的111个顶点、333维，仅位置方向；不构成应用授权。核心深度使用冻结 surrounding 二次曲面诊断，active core vertex=3025；连续性使用已经缓存的 R3 B-S4-V3 healthy reference 和位移/梯度/弯曲 metric，不重做健康参照选择。三个目标梯度 rank=3。线性方向锥解的最大约束欠量均小于4e-10；梯度与中心差分最大相对误差约 2.03e-05。

在基线与 R3 最佳失败点均找到了非零 normal+tangent 联合方向。失败点代表方向 JOINT_METRIC_GRADIENT 的导数为：

| 量 | 导数（每1 mm最大顶点方向幅度） |
|---|---:|
| dent-depth mm | -0.493610262 |
| edge6676 degree | -18.072920551 |
| reference/surrounding loss mm² | -2.007386362 |
| R3 A4自身缓存 soft-target MSE mm² | -0.004450760 |
| 非共享新接触最小间距 mm（204/207） | -0.263700878 |
| 共边有限feature安全侧高度 mm | 0.665406020 |
| boundary progression loss degree² | 0.001528095 |

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

代表联合方向在1e-5mm整个路径额外通过 **exact rational Bernstein / complete oriented-matroid sign certificate**：覆盖2309个 swept 或 intrinsic fan pair，含144个同一native face的fan pair；失败点检查6105个不同有理数三次谓词。完整4点谓词包含合法shared simplex端点，所有符号保持，故有限凸单形交叉及共享feature归属的组合关系不变。未用“既有整对face豁免”；未决pair=0。所有受影响 native fan 基线本征非法交叉=0，微步全路径最小fan面积约0.170385mm²，未发生翻转/退化。

这证明 **局部 no-new-structural-defect 下降仍存在**，不证明源网格既有缺陷消失、全局最优、完整 dent 修复或所有姿态安全。一般微步JSON的端点统计采用face-family差集；只有代表连续证书额外消除了整对face豁免的证明漏洞。未来正式候选必须升级到component/feature non-regression，不能把family差集当最终安全标准。

[下降与gate对照](../../../artifacts/e76382139beb49a8d7ba.md)

[固定源投影微步核验](../../../../examples/historical/audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/FIXED_SOURCE_PROJECTION_MICRO_NO_REGRESSION_R1.json)另对三个标记使用同一个冻结source chart，记录前后交点参数与实际3D对边间距；代表微步无新增flag、无增加crossing count，实际边间距保持为正。参数位置不是解剖严重度评分，外观变化保留Human review。

## 全 trace pair inventory

读取全部12个已有R3 trace（含superseded，明确保留最终6个的身份），加 mandatory pairs，得到13个面pair；基线分类计数：{'NEAR_CONTACT_WARNING': 1, 'SHARED_LEGAL': 11, 'NONADJACENT_TRUE_COLLISION': 1}。分类不凭 unsigned distance=0，也不凭四点无限平面符号。

| Faces | 基线精确分类 | Active row出现次数 |
|---|---|---:|
| 204/207 | NEAR_CONTACT_WARNING | 12 |
| 204/3313 | SHARED_LEGAL | 0 |
| 204/3314 | SHARED_LEGAL | 0 |
| 204/3329 | SHARED_LEGAL | 0 |
| 516/3315 | SHARED_LEGAL | 0 |
| 517/3314 | SHARED_LEGAL | 0 |
| 517/3315 | SHARED_LEGAL | 0 |
| 517/3329 | SHARED_LEGAL | 0 |
| 2181/3329 | NONADJACENT_TRUE_COLLISION | 182 |
| 2182/3330 | SHARED_LEGAL | 498 |
| 2424/2425 | SHARED_LEGAL | 0 |
| 3312/3313 | SHARED_LEGAL | 306 |
| 3329/3331 | SHARED_LEGAL | 1328 |

2181/3329 是既有非邻接真实接触，不能变为合法共享关系。局部全网格检查还独立记录10个已有真实接触family；它们不是 Stage6A old9 的替代判级。204/207 的历史相对切向运动因果保留，未被解释成单一坏点或大法线旋转。

## Persistent coplanar 与负对照

所有3D四点volume polynomial恒零时，仍需 common-plane chart中的连续2D边/顶点事件分区与 finite polygon overlap。固定共同平面上的有理数事件处理器检测到“两端不交、中途重叠”的 tunnel，同时通过始终只共边的合法路径。非有理事件根若未认证则 FAIL CLOSED；旋转共面路径需 chart atlas/root isolation，未来正式solver必须补齐，不能从本轮特定证书推定通用CCD已完成。

负对照 **16/16 PASS**：真实 nonadjacent crossing、历史R2-S5 204/207、true3D coplanar bow、shared-edge off-edge overlap、face material-path reversal/collapse、degenerate face、persistent tunnel均阻断；合法点/边/非共面折叠、合法persistent shared edge、三例intrinsic projection fans均通过；另加入当前2182/3330同侧非法与异侧合法共面feature对照。实际 crossing 不能因释放共享feature active-set而获豁免。

[共面负对照](../../../artifacts/c2ce373c2cede2cb21a3.md)

## 下一轮契约与停止点

[Proposed gate contract](../../../../examples/historical/audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/PROPOSED_POSITION_ONLY_GEOMETRY_GATE_CONTRACT_R1.json)仅为草案：真实新非邻接交叉、边外穿越、native topology改变、材料方向翻转/连续退化及真实self-intersection仍hard fail；baseline projected/shared/coplanar diagnostics采用feature-aware conditional/no-regression；sharpness、crease、depth、naturalness及投影外观进入明确Human review。所有tolerance标记COMPUTATIONAL_GEOMETRY_TOLERANCE；新增anatomy clearance=0；未改历史validator。

未来方向：耦合法线/两切向、非线性feature-aware约束、每步有限feature重识别，持续保留2182/3330同侧穿越屏障，避免绝对baseline projected归零；把目标完成与迭代合法性分开。事件产生的旋转共面CCD、既有contact component不恶化、完整修复外观评估仍须在未来完成。

POSITION_ONLY_ROUTE=OPEN；POSITION_ONLY_INSUFFICIENT=NOT_PROVED_GLOBALLY；TOPOLOGY_EXPRESSIVITY_LIMIT_EVIDENCE=NOT_FOUND；TOPOLOGY_CHANGE_REQUIRED=NOT_PROVED；RET0PO_REQUIRED=NO。

NEXT=MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R4_WITH_RECONCILED_GATES。**本轮不执行NEXT；无候选、无生产修改。STOP — HUMAN REVIEW。**

## 只读核验与证据索引

全部3281个既有文件SHA256一致，changed/missing/unexpected outside addition均为0，覆盖生产、冻结authority、全部历史R3及既有临时资产。生产R2 blend SHA256=adf757aeace8a0d69070b94f102b9bef9eb99da9847dd7a5639c4c2c3799dde9。PRODUCTION_DRIFT=0；blend save=0。未运行Full42、Stage6A/6B、ownership R3、skin rebuild或promotion。

- [Status](../../../../examples/historical/audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/DORSAL_MCP_POSITION_ONLY_FORMULATION_AND_GEOMETRIC_GATE_RECONCILIATION_R1_STATUS.json)
- [Gate classification](../../../../examples/historical/audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/GEOMETRIC_GATE_SEMANTIC_CLASSIFICATION_R1.json)
- [Projected audit](../../../../examples/historical/audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/PROJECTED_BOWTIE_SEMANTICS_AUDIT_R1.json)
- [Shared feature audit](../../../../examples/historical/audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/SHARED_EDGE_CONTACT_SEMANTICS_R1.json)
- [Pair inventory](../../../../examples/historical/audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/ACTIVE_SET_PAIR_INVENTORY_R1.json)
- [Local descent](../../../../examples/historical/audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/LOCAL_FEASIBLE_DESCENT_ANALYSIS_R1.json)
- [Normal/tangent directions](../../../../examples/historical/audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/NORMAL_TANGENT_COUPLED_DIRECTION_AUDIT_R1.json)
- [Continuous witness](../../../../examples/historical/audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/CONTINUOUS_MICRO_WITNESS_CERTIFICATE_R1.json)
- [Jacobian validation](../../../../examples/historical/audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/OBJECTIVE_JACOBIAN_VALIDATION_R1.json)
- [Negative controls](../../../../examples/historical/audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/GEOMETRIC_GATE_NEGATIVE_CONTROLS_R1.json)
- [Persistent feature policy](../../../../examples/historical/audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/PERSISTENT_COPLANAR_FEATURE_POLICY_R1.json)
- [No drift](../../../../examples/historical/audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json)
- [Visual review](../../../../examples/historical/audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/review.html)

可复现脚本顺序：semantic_audit.py → local_analysis.py → negative_controls.py → continuous_witness.py → supplemental_diagnostics.py → forensic_figures.py → delivery_verification.py --fixed-projection → finalize_semantics.py → delivery_verification.py。OPENBLAS_NUM_THREADS=1；全部python用-B。仅复用历史纯函数AST，绝不执行历史solve/search入口；只在本轮新目录写文件。
