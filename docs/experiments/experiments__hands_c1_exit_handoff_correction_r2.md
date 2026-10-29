# experiments/hands_c1_exit_handoff_correction_r2

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 保留R1进入/保持段，只对2.68–3.12s退出进行两种局部修正。最佳为候选2；目标窗结果与上下文结果分别记账，不把局部成功当成整段合格。没有第三候选、重新烘焙、IK、参数扫描、资产修改或正式C1合并。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_c1_exit_handoff_correction_r2/TECHNICAL_REPORT.md)

> 穿入列是**2.45–2.92s全目标窗口最大内部深度mm**，不是单帧；225个目标样本，2.10–3.35s上下文501样本。上下文回退列沿用R1的相对原C1加深>0.02mm统计口径（只作三方比较，不改变零非法碰撞要求）。本轮另以0.0001mm数值分辨率列出更严格的加深清单。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_c1_exit_handoff_correction_r2/TECHNICAL_REPORT.md)

## 技术路线

原报告未单独概述路线；以下实现文件与原报告共同界定方法，不能由文件名推断算法成功：

- [diagnose.py](../../src/legacy/experiments/hands_c1_exit_handoff_correction_r2/diagnose.py)
- [edit_exit.py](../../src/legacy/experiments/hands_c1_exit_handoff_correction_r2/edit_exit.py)
- [finalize.py](../../src/legacy/experiments/hands_c1_exit_handoff_correction_r2/finalize.py)
- [make_media.py](../../src/legacy/experiments/hands_c1_exit_handoff_correction_r2/make_media.py)
- [render_delivery.py](../../src/legacy/experiments/hands_c1_exit_handoff_correction_r2/render_delivery.py)

## 测试结论

> **PARTIAL — STOP — HUMAN REVIEW**。2026-10-17T13:35:12.337688+08:00。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_c1_exit_handoff_correction_r2/TECHNICAL_REPORT.md)

> **PARTIAL — STOP — HUMAN REVIEW**。本轮两次局部尝试已停止，未合并正式C1。

出处：[HUMAN_REVIEW.md](../research/experiments/hands_c1_exit_handoff_correction_r2/HUMAN_REVIEW.md)

## 失败原因与证据边界

> **A4是拇指侧面**：2.92s见证三角形2787/1381/342，93–98%属于THUMB_IP_R，其余THUMB_MCP_R；原R1深0.577845mm。发生在回腕、G4尚未结束而E5正在准备时。没有编辑拇指骨，只通过共享腕位做毫米级避让。真实三角面/键体证据、权重和曲线handle原始值见 `EXIT_DIAGNOSIS.json`，原因计划见 `DIAGNOSIS_AND_LOCAL_PLAN.md`。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_c1_exit_handoff_correction_r2/TECHNICAL_REPORT.md)

> 机器目标非法0/225，关节越界0.000000°，48触点48/48；上下文>0.02mm加深仍22个样本。若上下文非零，本轮只供审看改进和失败原因，**不能进入最终合格动作批准**。详见 `TECHNICAL_REPORT.md`（链接见原报告） 与 `R2_REGRESSION_DETAILS.json`（链接见原报告）。

出处：[HUMAN_REVIEW.md](../research/experiments/hands_c1_exit_handoff_correction_r2/HUMAN_REVIEW.md)

## 后续建议

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 原报告与关键代码

- [experiments/hands_c1_exit_handoff_correction_r2/TECHNICAL_REPORT.md](../research/experiments/hands_c1_exit_handoff_correction_r2/TECHNICAL_REPORT.md)
- [experiments/hands_c1_exit_handoff_correction_r2/HUMAN_REVIEW.md](../research/experiments/hands_c1_exit_handoff_correction_r2/HUMAN_REVIEW.md)
- [experiments/hands_c1_exit_handoff_correction_r2/DIAGNOSIS_AND_LOCAL_PLAN.md](../research/experiments/hands_c1_exit_handoff_correction_r2/DIAGNOSIS_AND_LOCAL_PLAN.md)
- [experiments/hands_c1_exit_handoff_correction_r2/diagnose.py](../../src/legacy/experiments/hands_c1_exit_handoff_correction_r2/diagnose.py)
- [experiments/hands_c1_exit_handoff_correction_r2/edit_exit.py](../../src/legacy/experiments/hands_c1_exit_handoff_correction_r2/edit_exit.py)
- [experiments/hands_c1_exit_handoff_correction_r2/finalize.py](../../src/legacy/experiments/hands_c1_exit_handoff_correction_r2/finalize.py)
- [experiments/hands_c1_exit_handoff_correction_r2/make_media.py](../../src/legacy/experiments/hands_c1_exit_handoff_correction_r2/make_media.py)
- [experiments/hands_c1_exit_handoff_correction_r2/render_delivery.py](../../src/legacy/experiments/hands_c1_exit_handoff_correction_r2/render_delivery.py)
- [experiments/hands_c1_exit_handoff_correction_r2/restore_metadata.py](../../src/legacy/experiments/hands_c1_exit_handoff_correction_r2/restore_metadata.py)
- [experiments/hands_c1_exit_handoff_correction_r2/review_existing.py](../../src/legacy/experiments/hands_c1_exit_handoff_correction_r2/review_existing.py)
- [experiments/hands_c1_exit_handoff_correction_r2/start_mcp.py](../../src/legacy/experiments/hands_c1_exit_handoff_correction_r2/start_mcp.py)
- [experiments/hands_c1_exit_handoff_correction_r2/validate_candidates.py](../../src/legacy/experiments/hands_c1_exit_handoff_correction_r2/validate_candidates.py)
- [experiments/hands_c1_exit_handoff_correction_r2/verify_reopened.py](../../src/legacy/experiments/hands_c1_exit_handoff_correction_r2/verify_reopened.py)

## 输入、输出与大型证据

该目录原始成员 556 项；拟公开身份记录 534 项。
- `experiments/hands_c1_exit_handoff_correction_r2/CANDIDATE_1_DENSE.npz` → `hands-research-r1-selected-010.zip` / `payload/experiments/hands_c1_exit_handoff_correction_r2/CANDIDATE_1_DENSE.npz`
- `experiments/hands_c1_exit_handoff_correction_r2/CANDIDATE_2_DENSE.npz` → `hands-research-r1-selected-010.zip` / `payload/experiments/hands_c1_exit_handoff_correction_r2/CANDIDATE_2_DENSE.npz`
- `experiments/hands_c1_exit_handoff_correction_r2/EXIT_CANDIDATE_1_METADATA_RESTORED_NOT_APPROVED.blend` → `hands-research-r1-selected-010.zip` / `payload/experiments/hands_c1_exit_handoff_correction_r2/EXIT_CANDIDATE_1_METADATA_RESTORED_NOT_APPROVED.blend`
- `experiments/hands_c1_exit_handoff_correction_r2/EXIT_CANDIDATE_1_NOT_APPROVED.blend` → `hands-research-r1-selected-010.zip` / `payload/experiments/hands_c1_exit_handoff_correction_r2/EXIT_CANDIDATE_1_NOT_APPROVED.blend`
- `experiments/hands_c1_exit_handoff_correction_r2/EXIT_CANDIDATE_2_METADATA_RESTORED_NOT_APPROVED.blend` → `hands-research-r1-selected-010.zip` / `payload/experiments/hands_c1_exit_handoff_correction_r2/EXIT_CANDIDATE_2_METADATA_RESTORED_NOT_APPROVED.blend`
- `experiments/hands_c1_exit_handoff_correction_r2/EXIT_CANDIDATE_2_NOT_APPROVED.blend` → `hands-research-r1-selected-010.zip` / `payload/experiments/hands_c1_exit_handoff_correction_r2/EXIT_CANDIDATE_2_NOT_APPROVED.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
