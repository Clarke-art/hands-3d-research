# audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 数学变量为冻结 S4 的111个顶点、333维，仅位置方向；不构成应用授权。核心深度使用冻结 surrounding 二次曲面诊断，active core vertex=3025；连续性使用已经缓存的 R3 B-S4-V3 healthy reference 和位移/梯度/弯曲 metric，不重做健康参照选择。三个目标梯度 rank=3。线性方向锥解的最大约束欠量均小于4e-10；梯度与中心差分最大相对误差约 2.03e-05。

出处：[DORSAL_MCP_POSITION_ONLY_FORMULATION_AND_GEOMETRIC_GATE_RECONCILIATION_R1_REPORT.md](../research/audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/DORSAL_MCP_POSITION_ONLY_FORMULATION_AND_GEOMETRIC_GATE_RECONCILIATION_R1_REPORT.md)

> 完整R3几何资格的 NO **不是** iterative tangent cone 空集，也不是对所有位置修改的不可行证明。修复最终深度/折角阈值是完成目标，不能作为 infinitesimal feasibility 的立即达标要求。R3原构造/投影/步长策略停滞，而代表方向还降低其自身 soft-target MSE，故局部 solver formulation gap 同时得到确认。

出处：[DORSAL_MCP_POSITION_ONLY_FORMULATION_AND_GEOMETRIC_GATE_RECONCILIATION_R1_REPORT.md](../research/audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/DORSAL_MCP_POSITION_ONLY_FORMULATION_AND_GEOMETRIC_GATE_RECONCILIATION_R1_REPORT.md)

## 技术路线

> 结果：**PASS_POSITION_ONLY_FEASIBILITY_REOPENED**。Position-only 路线保持 OPEN；同时确认局部 solver formulation gap。两项结论属于不同 gate 层次，不能合并为“真实3D约束已不可行”。

出处：[DORSAL_MCP_POSITION_ONLY_FORMULATION_AND_GEOMETRIC_GATE_RECONCILIATION_R1_REPORT.md](../research/audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/DORSAL_MCP_POSITION_ONLY_FORMULATION_AND_GEOMETRIC_GATE_RECONCILIATION_R1_REPORT.md)

> 完整R3几何资格的 NO **不是** iterative tangent cone 空集，也不是对所有位置修改的不可行证明。修复最终深度/折角阈值是完成目标，不能作为 infinitesimal feasibility 的立即达标要求。R3原构造/投影/步长策略停滞，而代表方向还降低其自身 soft-target MSE，故局部 solver formulation gap 同时得到确认。

出处：[DORSAL_MCP_POSITION_ONLY_FORMULATION_AND_GEOMETRIC_GATE_RECONCILIATION_R1_REPORT.md](../research/audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/DORSAL_MCP_POSITION_ONLY_FORMULATION_AND_GEOMETRIC_GATE_RECONCILIATION_R1_REPORT.md)

## 测试结论

> 结果：**PASS_POSITION_ONLY_FEASIBILITY_REOPENED**。Position-only 路线保持 OPEN；同时确认局部 solver formulation gap。两项结论属于不同 gate 层次，不能合并为“真实3D约束已不可行”。

出处：[DORSAL_MCP_POSITION_ONLY_FORMULATION_AND_GEOMETRIC_GATE_RECONCILIATION_R1_REPORT.md](../research/audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/DORSAL_MCP_POSITION_ONLY_FORMULATION_AND_GEOMETRIC_GATE_RECONCILIATION_R1_REPORT.md)

> 但当前对边角点3025、3340的垂直于公共边的射线几乎同向：基线 cosine≈0.9999995233，失败点≈1。失败点角点到对面三角形平面的保留侧高度约 **7.06432814799e-08 mm**。若该折叠穿过同侧共面极限，会形成真实正面积重叠。因此 **2182/3330 当前有限 feature 的屏障必须保留**；自然共边零距离不证明这条具体 side row 是错误约束。实际 feature 的共面同侧/异侧对照分别 HARD FAIL/LEGAL，均验证通过。

出处：[DORSAL_MCP_POSITION_ONLY_FORMULATION_AND_GEOMETRIC_GATE_RECONCILIATION_R1_REPORT.md](../research/audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/DORSAL_MCP_POSITION_ONLY_FORMULATION_AND_GEOMETRIC_GATE_RECONCILIATION_R1_REPORT.md)

## 失败原因与证据边界

> 负对照 **16/16 PASS**：真实 nonadjacent crossing、历史R2-S5 204/207、true3D coplanar bow、shared-edge off-edge overlap、face material-path reversal/collapse、degenerate face、persistent tunnel均阻断；合法点/边/非共面折叠、合法persistent shared edge、三例intrinsic projection fans均通过；另加入当前2182/3330同侧非法与异侧合法共面feature对照。实际 crossing 不能因释放共享feature active-set而获豁免。

出处：[DORSAL_MCP_POSITION_ONLY_FORMULATION_AND_GEOMETRIC_GATE_RECONCILIATION_R1_REPORT.md](../research/audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/DORSAL_MCP_POSITION_ONLY_FORMULATION_AND_GEOMETRIC_GATE_RECONCILIATION_R1_REPORT.md)

## 后续建议

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 原报告与关键代码

- [audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/DORSAL_MCP_POSITION_ONLY_FORMULATION_AND_GEOMETRIC_GATE_RECONCILIATION_R1_REPORT.md](../research/audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/DORSAL_MCP_POSITION_ONLY_FORMULATION_AND_GEOMETRIC_GATE_RECONCILIATION_R1_REPORT.md)
- [audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/collision_engine.py](../../src/legacy/audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/collision_engine.py)
- [audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/common.py](../../src/legacy/audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/common.py)
- [audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/contact_geometry.py](../../src/legacy/audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/contact_geometry.py)
- [audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/continuous_witness.py](../../src/legacy/audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/continuous_witness.py)
- [audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/delivery_verification.py](../../src/legacy/audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/delivery_verification.py)
- [audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/finalize_semantics.py](../../src/legacy/audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/finalize_semantics.py)
- [audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/forensic_figures.py](../../src/legacy/audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/forensic_figures.py)
- [audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/geometry.py](../../src/legacy/audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/geometry.py)
- [audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/local_analysis.py](../../src/legacy/audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/local_analysis.py)
- [audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/negative_controls.py](../../src/legacy/audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/negative_controls.py)
- [audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/persistent_coplanar.py](../../src/legacy/audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/persistent_coplanar.py)
- [audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/robust_geometry.py](../../src/legacy/audits/dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1/robust_geometry.py)

## 输入、输出与大型证据

该目录原始成员 45 项；拟公开身份记录 45 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
