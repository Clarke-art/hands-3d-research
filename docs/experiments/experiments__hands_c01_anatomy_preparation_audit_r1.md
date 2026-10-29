# experiments/hands_c01_anatomy_preparation_audit_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 只恢复MCP spread时旧E5越界变为17.96mm，而G4接触/零交叉保持，证明当前掌位与旧精确提前目标不协调。0.393571s的准备窗口不能推导必须提前精确悬停。共同骨架/皮肤已能在保守参考族内求得安全S1，没有直接证据支持现在修改冻结Rig。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_c01_anatomy_preparation_audit_r1/FINAL_RECOMMENDATION.md)

> - G4真实指腹接触距离0mm，目标侵入0.00327214mm。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_c01_anatomy_preparation_audit_r1/FINAL_RECOMMENDATION.md)

## 技术路线

> **C — 解剖/手型约束与E5准备策略都存在问题，需要联合改进。** 直接证据支持ANATOMY_CAUSE_IDENTIFIED；在不改冻结Rig下已得到满足真实几何及明确参考关节约束的B2静态候选，Human自然度仍待审。全部DESIGN_PROVISIONAL。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_c01_anatomy_preparation_audit_r1/FINAL_RECOMMENDATION.md)

> 将全部非拇指恢复批准参考而不调整掌位，会出现约3.353881mm非目标侵入。故不能仅手工“摆正手指”就判合格，需要接触、避障与手型联合求解。原raw布尔/数值都保留在READONLY_PREPARATION_PERTURBATIONS.json，没有把这些诊断当PASS。

出处：[S1_UNNATURAL_POSE_ROOT_CAUSE.md](../research/experiments/hands_c01_anatomy_preparation_audit_r1/S1_UNNATURAL_POSE_ROOT_CAUSE.md)

## 测试结论

> - S1_NUMERICAL_GEOMETRY = PASS

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_c01_anatomy_preparation_audit_r1/FINAL_RECOMMENDATION.md)

> - S1_HUMAN_ANATOMICAL_VISUAL = FAIL

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_c01_anatomy_preparation_audit_r1/FINAL_RECOMMENDATION.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

> B2旧E5精确悬停合同仍FAIL（越界19.96865mm）；通过的是本轮分阶段早期准备定义。不能把它追认为原静态合同PASS，也不能证明下一音能及时触键。整体自然度、拇指形态和教学习惯由Human审查，不能以数值替代。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_c01_anatomy_preparation_audit_r1/FINAL_RECOMMENDATION.md)

> 前臂/腕绝对解剖角、全域手型族和连续可达性尚未验证；即使B视觉获认可，也仍需单独的动态授权。本轮不自动执行任何后续运动实验。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_c01_anatomy_preparation_audit_r1/FINAL_RECOMMENDATION.md)

## 原报告与关键代码

- [experiments/hands_c01_anatomy_preparation_audit_r1/FINAL_RECOMMENDATION.md](../research/experiments/hands_c01_anatomy_preparation_audit_r1/FINAL_RECOMMENDATION.md)
- [experiments/hands_c01_anatomy_preparation_audit_r1/S1_UNNATURAL_POSE_ROOT_CAUSE.md](../research/experiments/hands_c01_anatomy_preparation_audit_r1/S1_UNNATURAL_POSE_ROOT_CAUSE.md)
- [experiments/hands_c01_anatomy_preparation_audit_r1/HUMAN_VISUAL_REVIEW.md](../research/experiments/hands_c01_anatomy_preparation_audit_r1/HUMAN_VISUAL_REVIEW.md)
- [experiments/hands_c01_anatomy_preparation_audit_r1/STATIC_AB_COMPARISON.md](../research/experiments/hands_c01_anatomy_preparation_audit_r1/STATIC_AB_COMPARISON.md)
- [experiments/hands_c01_anatomy_preparation_audit_r1/RIG_JOINT_ANATOMY_AUDIT.md](../research/experiments/hands_c01_anatomy_preparation_audit_r1/RIG_JOINT_ANATOMY_AUDIT.md)
- [experiments/hands_c01_anatomy_preparation_audit_r1/E5_PREPARATION_CONSTRAINT_REVIEW.md](../research/experiments/hands_c01_anatomy_preparation_audit_r1/E5_PREPARATION_CONSTRAINT_REVIEW.md)
- [experiments/hands_c01_anatomy_preparation_audit_r1/design_constraints.py](../../src/legacy/experiments/hands_c01_anatomy_preparation_audit_r1/design_constraints.py)
- [experiments/hands_c01_anatomy_preparation_audit_r1/diagnose_preparation.py](../../src/legacy/experiments/hands_c01_anatomy_preparation_audit_r1/diagnose_preparation.py)
- [experiments/hands_c01_anatomy_preparation_audit_r1/freeze_diagnostic.py](../../src/legacy/experiments/hands_c01_anatomy_preparation_audit_r1/freeze_diagnostic.py)
- [experiments/hands_c01_anatomy_preparation_audit_r1/prepare.py](../../src/legacy/experiments/hands_c01_anatomy_preparation_audit_r1/prepare.py)
- [experiments/hands_c01_anatomy_preparation_audit_r1/prepare_second_solve.py](../../src/legacy/experiments/hands_c01_anatomy_preparation_audit_r1/prepare_second_solve.py)
- [experiments/hands_c01_anatomy_preparation_audit_r1/render_ab.py](../../src/legacy/experiments/hands_c01_anatomy_preparation_audit_r1/render_ab.py)
- [experiments/hands_c01_anatomy_preparation_audit_r1/solve_b.py](../../src/legacy/experiments/hands_c01_anatomy_preparation_audit_r1/solve_b.py)
- [experiments/hands_c01_anatomy_preparation_audit_r1/solve_b_attempt1.py](../../src/legacy/experiments/hands_c01_anatomy_preparation_audit_r1/solve_b_attempt1.py)
- [experiments/hands_c01_anatomy_preparation_audit_r1/supplement_angles.py](../../src/legacy/experiments/hands_c01_anatomy_preparation_audit_r1/supplement_angles.py)
- [experiments/hands_c01_anatomy_preparation_audit_r1/verify_b.py](../../src/legacy/experiments/hands_c01_anatomy_preparation_audit_r1/verify_b.py)
- [experiments/hands_c01_anatomy_preparation_audit_r1/verify_delivery.py](../../src/legacy/experiments/hands_c01_anatomy_preparation_audit_r1/verify_delivery.py)
- [experiments/hands_c01_anatomy_preparation_audit_r1/write_reports.py](../../src/legacy/experiments/hands_c01_anatomy_preparation_audit_r1/write_reports.py)

## 输入、输出与大型证据

该目录原始成员 84 项；拟公开身份记录 60 项。
- `experiments/hands_c01_anatomy_preparation_audit_r1/S1_ANATOMY_PREPARATION_DIAGNOSTIC_R1.blend` → `hands-research-r1-selected-008.zip` / `payload/experiments/hands_c01_anatomy_preparation_audit_r1/S1_ANATOMY_PREPARATION_DIAGNOSTIC_R1.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
