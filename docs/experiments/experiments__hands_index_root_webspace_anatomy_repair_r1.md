# experiments/hands_index_root_webspace_anatomy_repair_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 任务提供的历史数据：原C1 A#4穿入5.637124mm；上轮候选为0mm、净空0.282075mm，并保持当时活动接触。这些是已知历史机器结果，不是本轮重新计算结果。Human本次已否决该候选自然性，应视为GEOMETRY_PASS_NATURALITY_FAIL。

出处：[STATIC_GEOMETRY_REPORT.md](../research/experiments/hands_index_root_webspace_anatomy_repair_r1/STATIC_GEOMETRY_REPORT.md)

> **UNKNOWN**：Human所指“缺少体积感”的具体目标曲面，以及当前凹面中哪些属于正常第一指蹼、哪些属于不合理局部塌陷。没有独立解剖目标或Human对具体边面的定位，不能唯一归因为错误权重、缺失corrective或Basis不足。没有证据证明两处异常来自同一个错误机制。

出处：[ANATOMICAL_CAUSE_REPORT.md](../research/experiments/hands_index_root_webspace_anatomy_repair_r1/ANATOMICAL_CAUSE_REPORT.md)

## 技术路线

原报告未单独概述路线；以下实现文件与原报告共同界定方法，不能由文件名推断算法成功：

- [analyze_rois.py](../../src/legacy/experiments/hands_index_root_webspace_anatomy_repair_r1/analyze_rois.py)
- [diagnostic_session.py](../../src/legacy/experiments/hands_index_root_webspace_anatomy_repair_r1/diagnostic_session.py)
- [finalize.py](../../src/legacy/experiments/hands_index_root_webspace_anatomy_repair_r1/finalize.py)
- [package_evidence.py](../../src/legacy/experiments/hands_index_root_webspace_anatomy_repair_r1/package_evidence.py)
- [render_diagnostics.py](../../src/legacy/experiments/hands_index_root_webspace_anatomy_repair_r1/render_diagnostics.py)

## 测试结论

> 本轮未创建需要验收的新动作或资产，因此没有重新进行全右手键面/自交/跨手候选验收，也不填造“新增碰撞=0”或“最小正净空”的候选数字。几何检查工具代码为隔离复用准备，未通过优化或放宽容差制作新PASS。

出处：[STATIC_GEOMETRY_REPORT.md](../research/experiments/hands_index_root_webspace_anatomy_repair_r1/STATIC_GEOMETRY_REPORT.md)

> 任务提供的历史数据：原C1 A#4穿入5.637124mm；上轮候选为0mm、净空0.282075mm，并保持当时活动接触。这些是已知历史机器结果，不是本轮重新计算结果。Human本次已否决该候选自然性，应视为GEOMETRY_PASS_NATURALITY_FAIL。

出处：[STATIC_GEOMETRY_REPORT.md](../research/experiments/hands_index_root_webspace_anatomy_repair_r1/STATIC_GEOMETRY_REPORT.md)

## 失败原因与证据边界

> 仅研究原C1的2.600000秒。已完成原C1与上轮第二静态候选的实际Blender网格、骨轴、权重、corrective及因素隔离检查，并做一次收窄虎口ROI的额外只读检查。没有执行阶段2，没有编辑Pose Bone，没有本轮修复候选，没有连续动画。有限诊断取得部分因果证据，但未充分证明解剖缺陷的唯一根因或合法姿态修复的可行性；不把普通曲率、正常虎口凹面或混合变形本身认定为错误资产。

出处：[ANATOMICAL_CAUSE_REPORT.md](../research/experiments/hands_index_root_webspace_anatomy_repair_r1/ANATOMICAL_CAUSE_REPORT.md)

> **CONFIRMED**：同机位侧向、真侧向、反向及线框显示根部曲面并非光滑解析面，存在真实折面。**SUPPORTED_BUT_UNPROVEN**：flat shading和低面数让折面更醒目，混合变形可增强局部法线差。**UNKNOWN**：Human所指“侧视凹陷”与上述虎口观测边是否为同一片皮肤，还是更靠掌指连接处的另一个问题。因此不合并根因，也不宣称这个问题已解决。

出处：[ANATOMICAL_CAUSE_REPORT.md](../research/experiments/hands_index_root_webspace_anatomy_repair_r1/ANATOMICAL_CAUSE_REPORT.md)

## 后续建议

> 若后续Human将已否决的具体拱起/折陷定位到本图网格片，建议单独授权一个最小局部资产诊断/修订实验：只涉及食指近节Basis轮廓与第一指蹼—根部过渡的目标面片；先确定自然形态目标，再在Basis、局部4骨权重过渡、corrective覆盖三者中逐项选一项验证。不能同时修改多项、不能整体鼓起虎口、不能改Rig/rest/琴键/MIDI。本轮没有实施这些资产修订，也没有证明其中某一项必须更改。

出处：[ANATOMICAL_CAUSE_REPORT.md](../research/experiments/hands_index_root_webspace_anatomy_repair_r1/ANATOMICAL_CAUSE_REPORT.md)

> 5. **是否充分支持独立资产修订实验？** 足够支持经单独授权的局部定位及单因素资产试验建议；不足以确证必须改权重、corrective或网格，更不能据此直接实施。

出处：[ANATOMICAL_CAUSE_REPORT.md](../research/experiments/hands_index_root_webspace_anatomy_repair_r1/ANATOMICAL_CAUSE_REPORT.md)

## 原报告与关键代码

- [experiments/hands_index_root_webspace_anatomy_repair_r1/STATIC_GEOMETRY_REPORT.md](../research/experiments/hands_index_root_webspace_anatomy_repair_r1/STATIC_GEOMETRY_REPORT.md)
- [experiments/hands_index_root_webspace_anatomy_repair_r1/ANATOMICAL_CAUSE_REPORT.md](../research/experiments/hands_index_root_webspace_anatomy_repair_r1/ANATOMICAL_CAUSE_REPORT.md)
- [experiments/hands_index_root_webspace_anatomy_repair_r1/HUMAN_REVIEW.md](../research/experiments/hands_index_root_webspace_anatomy_repair_r1/HUMAN_REVIEW.md)
- [experiments/hands_index_root_webspace_anatomy_repair_r1/TOOLING_BOUNDARY_NOTES.md](../research/experiments/hands_index_root_webspace_anatomy_repair_r1/TOOLING_BOUNDARY_NOTES.md)
- [experiments/hands_index_root_webspace_anatomy_repair_r1/analyze_rois.py](../../src/legacy/experiments/hands_index_root_webspace_anatomy_repair_r1/analyze_rois.py)
- [experiments/hands_index_root_webspace_anatomy_repair_r1/diagnostic_session.py](../../src/legacy/experiments/hands_index_root_webspace_anatomy_repair_r1/diagnostic_session.py)
- [experiments/hands_index_root_webspace_anatomy_repair_r1/finalize.py](../../src/legacy/experiments/hands_index_root_webspace_anatomy_repair_r1/finalize.py)
- [experiments/hands_index_root_webspace_anatomy_repair_r1/package_evidence.py](../../src/legacy/experiments/hands_index_root_webspace_anatomy_repair_r1/package_evidence.py)
- [experiments/hands_index_root_webspace_anatomy_repair_r1/render_diagnostics.py](../../src/legacy/experiments/hands_index_root_webspace_anatomy_repair_r1/render_diagnostics.py)
- [experiments/hands_index_root_webspace_anatomy_repair_r1/render_evidence_plots.py](../../src/legacy/experiments/hands_index_root_webspace_anatomy_repair_r1/render_evidence_plots.py)
- [experiments/hands_index_root_webspace_anatomy_repair_r1/render_true_side.py](../../src/legacy/experiments/hands_index_root_webspace_anatomy_repair_r1/render_true_side.py)
- [experiments/hands_index_root_webspace_anatomy_repair_r1/verify_saved_diagnostic.py](../../src/legacy/experiments/hands_index_root_webspace_anatomy_repair_r1/verify_saved_diagnostic.py)

## 输入、输出与大型证据

该目录原始成员 124 项；拟公开身份记录 108 项。
- `experiments/hands_index_root_webspace_anatomy_repair_r1/ANATOMICAL_DIAGNOSTIC_ONLY.blend` → `hands-research-r1-selected-014.zip` / `payload/experiments/hands_index_root_webspace_anatomy_repair_r1/ANATOMICAL_DIAGNOSTIC_ONLY.blend`
- `experiments/hands_index_root_webspace_anatomy_repair_r1/ANATOMICAL_DIAGNOSTIC_WITH_TRUE_SIDE.blend` → `hands-research-r1-selected-014.zip` / `payload/experiments/hands_index_root_webspace_anatomy_repair_r1/ANATOMICAL_DIAGNOSTIC_WITH_TRUE_SIDE.blend`
- `experiments/hands_index_root_webspace_anatomy_repair_r1/ORIGINAL_C1_DIAGNOSTIC_ONLY.blend` → `hands-research-r1-selected-014.zip` / `payload/experiments/hands_index_root_webspace_anatomy_repair_r1/ORIGINAL_C1_DIAGNOSTIC_ONLY.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
