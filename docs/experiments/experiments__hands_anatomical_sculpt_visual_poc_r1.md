# experiments/hands_anatomical_sculpt_visual_poc_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 二者是各自第2轮真实文件的同目录字节相同副本，不是空壳。最终文件重开后，2.6秒evaluated mesh与建模记录逐点误差0。原Basis、原shape key绝对坐标和相对差分、权重、UV、3300顶点／3298原生面、rest骨数据、驱动表达式／目标与全部Action摘要均与原C1一致。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_anatomical_sculpt_visual_poc_r1/TECHNICAL_REPORT.md)

> A意图是减少近节靠虎口侧的非关节突起，保留背侧软组织圆度及MCP—PIP骨段关系；B意图是形成连续的下部第一指蹼组织扇面，保留自然虎口凹面。照片只提供定性形态依据，不提供唯一三维目标。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_anatomical_sculpt_visual_poc_r1/TECHNICAL_REPORT.md)

## 技术路线

> 做法是有限的局部grab／支撑笔触：给定空间中心、半径、方向，以局部比例衰减直接拖动顶点，再观察真实皮肤渲染并修正。现有Armature的3×3线性变换只用于将世界空间笔触换算到mesh局部坐标，没有建立新蒙皮算法、曲面优化器、随机搜索器或自动纠错Agent。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_anatomical_sculpt_visual_poc_r1/TECHNICAL_REPORT.md)

## 测试结论

> 对原C1 2.600秒、历史固定几何PASS姿态分别实际重算evaluated mesh、实际三角化、全右手与实际键体相交／内部深度、非邻接自交、跨手碰撞、局部翻面、面积／边长与法向射线厚度代理、皮肤触点及接触邻域。不是沿用旧PASS。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_anatomical_sculpt_visual_poc_r1/TECHNICAL_REPORT.md)

> 原C1已有非目标穿键仍保留，不宣称原C1全手PASS。完整六态回归、右手16音48活动触点复验、整曲高频几何验收、动画及自动激活机制均为**NOT_RUN**；按本轮要求未在Human视觉确认前展开。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_anatomical_sculpt_visual_poc_r1/TECHNICAL_REPORT.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 原报告与关键代码

- [experiments/hands_anatomical_sculpt_visual_poc_r1/TECHNICAL_REPORT.md](../research/experiments/hands_anatomical_sculpt_visual_poc_r1/TECHNICAL_REPORT.md)
- [experiments/hands_anatomical_sculpt_visual_poc_r1/HUMAN_REVIEW.md](../research/experiments/hands_anatomical_sculpt_visual_poc_r1/HUMAN_REVIEW.md)
- [experiments/hands_anatomical_sculpt_visual_poc_r1/finalize_reports.py](../../src/legacy/experiments/hands_anatomical_sculpt_visual_poc_r1/finalize_reports.py)
- [experiments/hands_anatomical_sculpt_visual_poc_r1/finalize_visual_delivery.py](../../src/legacy/experiments/hands_anatomical_sculpt_visual_poc_r1/finalize_visual_delivery.py)
- [experiments/hands_anatomical_sculpt_visual_poc_r1/limited_checks.py](../../src/legacy/experiments/hands_anatomical_sculpt_visual_poc_r1/limited_checks.py)
- [experiments/hands_anatomical_sculpt_visual_poc_r1/make_review_panels.py](../../src/legacy/experiments/hands_anatomical_sculpt_visual_poc_r1/make_review_panels.py)
- [experiments/hands_anatomical_sculpt_visual_poc_r1/prepare_sculpt_runtime.py](../../src/legacy/experiments/hands_anatomical_sculpt_visual_poc_r1/prepare_sculpt_runtime.py)
- [experiments/hands_anatomical_sculpt_visual_poc_r1/record_scope.py](../../src/legacy/experiments/hands_anatomical_sculpt_visual_poc_r1/record_scope.py)
- [experiments/hands_anatomical_sculpt_visual_poc_r1/render_round.py](../../src/legacy/experiments/hands_anatomical_sculpt_visual_poc_r1/render_round.py)
- [experiments/hands_anatomical_sculpt_visual_poc_r1/render_round_2.py](../../src/legacy/experiments/hands_anatomical_sculpt_visual_poc_r1/render_round_2.py)
- [experiments/hands_anatomical_sculpt_visual_poc_r1/run_stage.py](../../src/legacy/experiments/hands_anatomical_sculpt_visual_poc_r1/run_stage.py)
- [experiments/hands_anatomical_sculpt_visual_poc_r1/sculpt_common.py](../../src/legacy/experiments/hands_anatomical_sculpt_visual_poc_r1/sculpt_common.py)
- [experiments/hands_anatomical_sculpt_visual_poc_r1/sculpt_geometry.py](../../src/legacy/experiments/hands_anatomical_sculpt_visual_poc_r1/sculpt_geometry.py)
- [experiments/hands_anatomical_sculpt_visual_poc_r1/sculpt_round_1.py](../../src/legacy/experiments/hands_anatomical_sculpt_visual_poc_r1/sculpt_round_1.py)

## 输入、输出与大型证据

该目录原始成员 126 项；拟公开身份记录 113 项。
- `experiments/hands_anatomical_sculpt_visual_poc_r1/A_SCULPT_NOT_APPROVED.blend` → `hands-research-r1-selected-008.zip` / `payload/experiments/hands_anatomical_sculpt_visual_poc_r1/A_SCULPT_NOT_APPROVED.blend`
- `experiments/hands_anatomical_sculpt_visual_poc_r1/A_SCULPT_ROUND_1_NOT_APPROVED.blend` → `hands-research-r1-selected-008.zip` / `payload/experiments/hands_anatomical_sculpt_visual_poc_r1/A_SCULPT_ROUND_1_NOT_APPROVED.blend`
- `experiments/hands_anatomical_sculpt_visual_poc_r1/B_SCULPT_NOT_APPROVED.blend` → `hands-research-r1-selected-008.zip` / `payload/experiments/hands_anatomical_sculpt_visual_poc_r1/B_SCULPT_NOT_APPROVED.blend`
- `experiments/hands_anatomical_sculpt_visual_poc_r1/B_SCULPT_ROUND_1_NOT_APPROVED.blend` → `hands-research-r1-selected-008.zip` / `payload/experiments/hands_anatomical_sculpt_visual_poc_r1/B_SCULPT_ROUND_1_NOT_APPROVED.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
