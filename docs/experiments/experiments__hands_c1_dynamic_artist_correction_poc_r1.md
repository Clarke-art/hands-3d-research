# experiments/hands_c1_dynamic_artist_correction_poc_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 本轮通过Blender MCP直接调整现有Pose Bone，做出了可重新打开的进入、保持、退出动画；但是目标窗口仍有非法几何关系，尚未完成合格的连续纠错。没有开发IK、运动规划器、参数扫描或自动纠错Agent。只制作两个有差异的动画设计；停止继续调参。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_c1_dynamic_artist_correction_poc_r1/TECHNICAL_REPORT.md)

> 候选1食指目标10/15/8/−12°，腕部较早回位；候选2为10/10/5/−12°，减小末两节钩曲并较晚回位。中指仅为退出协同，目标0/4/3°，展指约−5.802°。具体权重、动作路径和所有关键时刻见 `CANDIDATE_2_FIXED_EDIT_LEDGER.json`。Bezier插值可能在关键姿态间产生超调，因此以实际求值验收，不能把作者关键角代替实际全段合法性。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_c1_dynamic_artist_correction_poc_r1/TECHNICAL_REPORT.md)

## 技术路线

原报告未单独概述路线；以下实现文件与原报告共同界定方法，不能由文件名推断算法成功：

- [build_candidate.py](../../src/legacy/experiments/hands_c1_dynamic_artist_correction_poc_r1/build_candidate.py)
- [finalize.py](../../src/legacy/experiments/hands_c1_dynamic_artist_correction_poc_r1/finalize.py)
- [make_media.py](../../src/legacy/experiments/hands_c1_dynamic_artist_correction_poc_r1/make_media.py)
- [render_delivery.py](../../src/legacy/experiments/hands_c1_dynamic_artist_correction_poc_r1/render_delivery.py)
- [start_session.py](../../src/legacy/experiments/hands_c1_dynamic_artist_correction_poc_r1/start_session.py)

## 测试结论

> **PARTIAL — STOP — HUMAN REVIEW**。2026-10-17T09:15:11.389913+08:00。候选2是最终交付；不是正式教学片批准，未合并原C1。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_c1_dynamic_artist_correction_poc_r1/TECHNICAL_REPORT.md)

> | 动画设计 | 目标非法样本 | 48触点PASS | 新自交样本 | 最大关节越界° |

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_c1_dynamic_artist_correction_poc_r1/TECHNICAL_REPORT.md)

## 失败原因与证据边界

> 初次写入出现Blender RNA关键点数组引用失效，导致旧点残留/点列表错误；未使用这些结果验收。初次 `CANDIDATE_1_NOT_APPROVED.blend`、`CANDIDATE_2_NOT_APPROVED.blend` 与初始survey保留为**无效过程证据**。修正为逆序删除并在全部插入后重新获取点引用，再以同两个设计生成 `IMPLEMENTATION_FIXED` 文件。没有新增第三个动作设计。另一次渲染manifest的numpy数组比较报错发生在全部PNG已保存后；修复元数据比较并复用原PNG，未覆写画面。日志全部保留。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_c1_dynamic_artist_correction_poc_r1/TECHNICAL_REPORT.md)

## 后续建议

> - 源3.12s（片内1.02s）后：应回到原C1后续动作。0.5X中上述片内时间乘2。

出处：[HUMAN_REVIEW.md](../research/experiments/hands_c1_dynamic_artist_correction_poc_r1/HUMAN_REVIEW.md)

## 原报告与关键代码

- [experiments/hands_c1_dynamic_artist_correction_poc_r1/TECHNICAL_REPORT.md](../research/experiments/hands_c1_dynamic_artist_correction_poc_r1/TECHNICAL_REPORT.md)
- [experiments/hands_c1_dynamic_artist_correction_poc_r1/HUMAN_REVIEW.md](../research/experiments/hands_c1_dynamic_artist_correction_poc_r1/HUMAN_REVIEW.md)
- [experiments/hands_c1_dynamic_artist_correction_poc_r1/build_candidate.py](../../src/legacy/experiments/hands_c1_dynamic_artist_correction_poc_r1/build_candidate.py)
- [experiments/hands_c1_dynamic_artist_correction_poc_r1/finalize.py](../../src/legacy/experiments/hands_c1_dynamic_artist_correction_poc_r1/finalize.py)
- [experiments/hands_c1_dynamic_artist_correction_poc_r1/make_media.py](../../src/legacy/experiments/hands_c1_dynamic_artist_correction_poc_r1/make_media.py)
- [experiments/hands_c1_dynamic_artist_correction_poc_r1/render_delivery.py](../../src/legacy/experiments/hands_c1_dynamic_artist_correction_poc_r1/render_delivery.py)
- [experiments/hands_c1_dynamic_artist_correction_poc_r1/start_session.py](../../src/legacy/experiments/hands_c1_dynamic_artist_correction_poc_r1/start_session.py)
- [experiments/hands_c1_dynamic_artist_correction_poc_r1/static_tools.py](../../src/legacy/experiments/hands_c1_dynamic_artist_correction_poc_r1/static_tools.py)
- [experiments/hands_c1_dynamic_artist_correction_poc_r1/validate_full.py](../../src/legacy/experiments/hands_c1_dynamic_artist_correction_poc_r1/validate_full.py)
- [experiments/hands_c1_dynamic_artist_correction_poc_r1/verify_final.py](../../src/legacy/experiments/hands_c1_dynamic_artist_correction_poc_r1/verify_final.py)

## 输入、输出与大型证据

该目录原始成员 559 项；拟公开身份记录 542 项。
- `experiments/hands_c1_dynamic_artist_correction_poc_r1/BASELINE_DENSE.npz` → `hands-research-r1-selected-009.zip` / `payload/experiments/hands_c1_dynamic_artist_correction_poc_r1/BASELINE_DENSE.npz`
- `experiments/hands_c1_dynamic_artist_correction_poc_r1/C1_ISOLATED_WORKING_COPY.blend` → `hands-research-r1-selected-009.zip` / `payload/experiments/hands_c1_dynamic_artist_correction_poc_r1/C1_ISOLATED_WORKING_COPY.blend`
- `experiments/hands_c1_dynamic_artist_correction_poc_r1/CANDIDATE_1_FIXED_DENSE.npz` → `hands-research-r1-selected-009.zip` / `payload/experiments/hands_c1_dynamic_artist_correction_poc_r1/CANDIDATE_1_FIXED_DENSE.npz`
- `experiments/hands_c1_dynamic_artist_correction_poc_r1/CANDIDATE_1_IMPLEMENTATION_FIXED_NOT_APPROVED.blend` → `hands-research-r1-selected-009.zip` / `payload/experiments/hands_c1_dynamic_artist_correction_poc_r1/CANDIDATE_1_IMPLEMENTATION_FIXED_NOT_APPROVED.blend`
- `experiments/hands_c1_dynamic_artist_correction_poc_r1/CANDIDATE_1_NOT_APPROVED.blend` → `hands-research-r1-selected-009.zip` / `payload/experiments/hands_c1_dynamic_artist_correction_poc_r1/CANDIDATE_1_NOT_APPROVED.blend`
- `experiments/hands_c1_dynamic_artist_correction_poc_r1/CANDIDATE_2_FIXED_DENSE.npz` → `hands-research-r1-selected-009.zip` / `payload/experiments/hands_c1_dynamic_artist_correction_poc_r1/CANDIDATE_2_FIXED_DENSE.npz`
- `experiments/hands_c1_dynamic_artist_correction_poc_r1/CANDIDATE_2_IMPLEMENTATION_FIXED_NOT_APPROVED.blend` → `hands-research-r1-selected-009.zip` / `payload/experiments/hands_c1_dynamic_artist_correction_poc_r1/CANDIDATE_2_IMPLEMENTATION_FIXED_NOT_APPROVED.blend`
- `experiments/hands_c1_dynamic_artist_correction_poc_r1/CANDIDATE_2_NOT_APPROVED.blend` → `hands-research-r1-selected-009.zip` / `payload/experiments/hands_c1_dynamic_artist_correction_poc_r1/CANDIDATE_2_NOT_APPROVED.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
