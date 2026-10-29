# experiments/hands_local_skin_asset_repair_poc_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 阶段1停止：本轮明确要求先核对Human原始红箭头，并规定“如果不能准确对应，输出一张可供Human定位的标注图并停止，不得自行猜测要修的面片”。当前可访问的本会话5个任务回合均为文字请求，没有Human图像内容；已知上一轮及前轮文本附件目录也只有已粘贴的文本。未找到可核对的原始红箭头截图，不能确认截图视角、指向表面或编辑边界。本次没有对整个文件系统或其他会话开展无目标扫描。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_local_skin_asset_repair_poc_r1/TECHNICAL_REPORT.md)

> 已重新读取hands/AGENTS.md。用户本轮授权隔离资产实验，未授予对冻结资产的修改权；同时编辑前的目标确认门槛尚未满足。没有把历史ROI-A背侧拱形或边629—2018自动当成本轮编辑目标。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_local_skin_asset_repair_poc_r1/TECHNICAL_REPORT.md)

## 技术路线

> 这不是任何方法的实验性失败，也不是已证明资产不可修。当前缺少的是准确编辑目标，而不是隔离实验的授权。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_local_skin_asset_repair_poc_r1/TECHNICAL_REPORT.md)

> 2. 虎口更适合权重还是corrective？**未验证**，没有B1/B2修改或方法比较结果；不根据旧折面夹角选择方法。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_local_skin_asset_repair_poc_r1/TECHNICAL_REPORT.md)

## 测试结论

> 结果：**INSUFFICIENT_EVIDENCE**。最终状态：**STOP — HUMAN REVIEW**。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_local_skin_asset_repair_poc_r1/TECHNICAL_REPORT.md)

> - 图上上排是原C1，下排是上轮固定几何PASS姿态；后者仍为Human自然性否决状态，不能作为正确解剖模板。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_local_skin_asset_repair_poc_r1/TECHNICAL_REPORT.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

> 5. 两处是否需分别修？**尚未证明**；现有证据不支持合并为同一缺陷。后续按授权使用独立A/B副本做单因素验证。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_local_skin_asset_repair_poc_r1/TECHNICAL_REPORT.md)

## 原报告与关键代码

- [experiments/hands_local_skin_asset_repair_poc_r1/TECHNICAL_REPORT.md](../research/experiments/hands_local_skin_asset_repair_poc_r1/TECHNICAL_REPORT.md)
- [experiments/hands_local_skin_asset_repair_poc_r1/roi_approved_asset_trials_r1/TECHNICAL_REPORT.md](../research/experiments/hands_local_skin_asset_repair_poc_r1/roi_approved_asset_trials_r1/TECHNICAL_REPORT.md)
- [experiments/hands_local_skin_asset_repair_poc_r1/HUMAN_REVIEW.md](../research/experiments/hands_local_skin_asset_repair_poc_r1/HUMAN_REVIEW.md)
- [experiments/hands_local_skin_asset_repair_poc_r1/ROI_HUMAN_REVIEW.md](../research/experiments/hands_local_skin_asset_repair_poc_r1/ROI_HUMAN_REVIEW.md)
- [experiments/hands_local_skin_asset_repair_poc_r1/roi_approved_asset_trials_r1/HUMAN_REVIEW.md](../research/experiments/hands_local_skin_asset_repair_poc_r1/roi_approved_asset_trials_r1/HUMAN_REVIEW.md)
- [experiments/hands_local_skin_asset_repair_poc_r1/roi_approved_asset_trials_r1/MULTIPOSE_COMPARISON.md](../research/experiments/hands_local_skin_asset_repair_poc_r1/roi_approved_asset_trials_r1/MULTIPOSE_COMPARISON.md)
- [experiments/hands_local_skin_asset_repair_poc_r1/finalize_roi_review.py](../../src/legacy/experiments/hands_local_skin_asset_repair_poc_r1/finalize_roi_review.py)
- [experiments/hands_local_skin_asset_repair_poc_r1/make_localization_delivery.py](../../src/legacy/experiments/hands_local_skin_asset_repair_poc_r1/make_localization_delivery.py)
- [experiments/hands_local_skin_asset_repair_poc_r1/propose_roi.py](../../src/legacy/experiments/hands_local_skin_asset_repair_poc_r1/propose_roi.py)
- [experiments/hands_local_skin_asset_repair_poc_r1/roi_localization_tools.py](../../src/legacy/experiments/hands_local_skin_asset_repair_poc_r1/roi_localization_tools.py)
- [experiments/hands_local_skin_asset_repair_poc_r1/roi_approved_asset_trials_r1/build_trials.py](../../src/legacy/experiments/hands_local_skin_asset_repair_poc_r1/roi_approved_asset_trials_r1/build_trials.py)
- [experiments/hands_local_skin_asset_repair_poc_r1/roi_approved_asset_trials_r1/finalize_trials.py](../../src/legacy/experiments/hands_local_skin_asset_repair_poc_r1/roi_approved_asset_trials_r1/finalize_trials.py)
- [experiments/hands_local_skin_asset_repair_poc_r1/roi_approved_asset_trials_r1/package_trials.py](../../src/legacy/experiments/hands_local_skin_asset_repair_poc_r1/roi_approved_asset_trials_r1/package_trials.py)
- [experiments/hands_local_skin_asset_repair_poc_r1/roi_approved_asset_trials_r1/render_active.py](../../src/legacy/experiments/hands_local_skin_asset_repair_poc_r1/roi_approved_asset_trials_r1/render_active.py)
- [experiments/hands_local_skin_asset_repair_poc_r1/roi_approved_asset_trials_r1/render_trials.py](../../src/legacy/experiments/hands_local_skin_asset_repair_poc_r1/roi_approved_asset_trials_r1/render_trials.py)
- [experiments/hands_local_skin_asset_repair_poc_r1/roi_approved_asset_trials_r1/render_true_side_near.py](../../src/legacy/experiments/hands_local_skin_asset_repair_poc_r1/roi_approved_asset_trials_r1/render_true_side_near.py)
- [experiments/hands_local_skin_asset_repair_poc_r1/roi_approved_asset_trials_r1/run_stage.py](../../src/legacy/experiments/hands_local_skin_asset_repair_poc_r1/roi_approved_asset_trials_r1/run_stage.py)
- [experiments/hands_local_skin_asset_repair_poc_r1/roi_approved_asset_trials_r1/trial_common.py](../../src/legacy/experiments/hands_local_skin_asset_repair_poc_r1/roi_approved_asset_trials_r1/trial_common.py)

## 输入、输出与大型证据

该目录原始成员 244 项；拟公开身份记录 226 项。
- `experiments/hands_local_skin_asset_repair_poc_r1/roi_approved_asset_trials_r1/A_BASIS_CANDIDATE_1_NOT_APPROVED.blend` → `hands-research-r1-selected-014.zip` / `payload/experiments/hands_local_skin_asset_repair_poc_r1/roi_approved_asset_trials_r1/A_BASIS_CANDIDATE_1_NOT_APPROVED.blend`
- `experiments/hands_local_skin_asset_repair_poc_r1/roi_approved_asset_trials_r1/A_BASIS_CANDIDATE_2_NOT_APPROVED.blend` → `hands-research-r1-selected-014.zip` / `payload/experiments/hands_local_skin_asset_repair_poc_r1/roi_approved_asset_trials_r1/A_BASIS_CANDIDATE_2_NOT_APPROVED.blend`
- `experiments/hands_local_skin_asset_repair_poc_r1/roi_approved_asset_trials_r1/B1_WEIGHTS_NOT_APPROVED.blend` → `hands-research-r1-selected-014.zip` / `payload/experiments/hands_local_skin_asset_repair_poc_r1/roi_approved_asset_trials_r1/B1_WEIGHTS_NOT_APPROVED.blend`
- `experiments/hands_local_skin_asset_repair_poc_r1/roi_approved_asset_trials_r1/B2_CORRECTIVE_NOT_APPROVED.blend` → `hands-research-r1-selected-014.zip` / `payload/experiments/hands_local_skin_asset_repair_poc_r1/roi_approved_asset_trials_r1/B2_CORRECTIVE_NOT_APPROVED.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
