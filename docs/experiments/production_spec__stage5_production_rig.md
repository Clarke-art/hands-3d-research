# production_spec/stage5_production_rig

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> **任务**：Stage5A R1 Human Review（`REQUEST_CHANGES`）后的窄修订 —— 只重新资格确认 5 个关节位置

出处：[STAGE5A_R2_REPORT.md](../research/production_spec/stage5_production_rig/stage5a_r2/STAGE5A_R2_REPORT.md)

> **Sanity check（不作为目标）**：`wrist → mean MCP = 120.0 mm`；项目此前引用的解剖参考 65–90 mm。

出处：[STAGE5A_R2_REPORT.md](../research/production_spec/stage5_production_rig/stage5a_r2/STAGE5A_R2_REPORT.md)

## 技术路线

> **PRODUCTION_WRIST_CENTER_METHOD（可复现，无手工点选）**

出处：[STAGE5A_R2_REPORT.md](../research/production_spec/stage5_production_rig/stage5a_r2/STAGE5A_R2_REPORT.md)

> 方法：在笼锚点所在轴向平面内、以锚点为心的批准区域内求最大间隙点（1.15×R_env(thumb) = 12.81 mm 搜索球）。

出处：[STAGE5A_R2_REPORT.md](../research/production_spec/stage5_production_rig/stage5a_r2/STAGE5A_R2_REPORT.md)

## 测试结论

> PRODUCTION_RIG_SKELETON   = PASS_PENDING_HUMAN_REVIEW

出处：[STAGE5A_R2_REPORT.md](../research/production_spec/stage5_production_rig/stage5a_r2/STAGE5A_R2_REPORT.md)

> ASSET_OBJECT_ORIGIN            = [1.408704638, 0.022395039, 0.335847497]   （未修改，Stage4C 继续 PASS）

出处：[STAGE5A_R2_REPORT.md](../research/production_spec/stage5_production_rig/stage5a_r2/STAGE5A_R2_REPORT.md)

## 失败原因与证据边界

> **原因归类**：`region mask 太宽` + `thumb distal ownership guard 太强` 的组合——真正的单一触发点是**判据符号反向**，且**没有 else 兜底**把 THUMB_IP 限制在远端指骨。`lam = exp(-((xi-mj)/κ)²)` 与 `mu = exp(-(d/L0)²)` 都被该守卫覆盖，`normalize → prune → normalize` 顺序正常（最坏归一化误差 4.4e-08），**不是**成因。

出处：[STAGE5B_R1A_REPORT.md](../research/production_spec/stage5_production_rig/stage5b_r1a/STAGE5B_R1A_REPORT.md)

> R1 mask（`到两条链距离 ≤ 2×中位边长`，阈值 7.7764 mm）命中 45 顶点，但其**拇指弧长区间为 83.0–93.9 mm**（= 拇指**远端指骨**，IP 关节在 71.88 mm），并**吞入 5 个拇指指甲顶点**。原因是本姿态下拇指被内收：

出处：[STAGE5B_R1A_REPORT.md](../research/production_spec/stage5_production_rig/stage5b_r1a/STAGE5B_R1A_REPORT.md)

## 后续建议

> - 后续路径（例如 distal phalanx 辅助表示、或 THUMB_IP_R.head 的重新授权）须由 Human Review 另行授权。

出处：[STAGE5A_R2B_REPORT.md](../research/production_spec/stage5_production_rig/stage5a_r2b/STAGE5A_R2B_REPORT.md)

## 原报告与关键代码

- [production_spec/stage5_production_rig/stage5a_r2/STAGE5A_R2_REPORT.md](../research/production_spec/stage5_production_rig/stage5a_r2/STAGE5A_R2_REPORT.md)
- [production_spec/stage5_production_rig/stage5b_r1/STAGE5B_R1_REPORT.md](../research/production_spec/stage5_production_rig/stage5b_r1/STAGE5B_R1_REPORT.md)
- [production_spec/stage5_production_rig/stage5a_r2b/STAGE5A_R2B_REPORT.md](../research/production_spec/stage5_production_rig/stage5a_r2b/STAGE5A_R2B_REPORT.md)
- [production_spec/stage5_production_rig/stage5b_r1a/STAGE5B_R1A_REPORT.md](../research/production_spec/stage5_production_rig/stage5b_r1a/STAGE5B_R1A_REPORT.md)
- [production_spec/stage5_production_rig/stage5b_r1b/STAGE5B_R1B_REPORT.md](../research/production_spec/stage5_production_rig/stage5b_r1b/STAGE5B_R1B_REPORT.md)
- [production_spec/stage5_production_rig/stage5b_r1c/STAGE5B_R1C_REPORT.md](../research/production_spec/stage5_production_rig/stage5b_r1c/STAGE5B_R1C_REPORT.md)
- [production_spec/stage5_production_rig/stage5b_r1d/STAGE5B_R1D_REPORT.md](../research/production_spec/stage5_production_rig/stage5b_r1d/STAGE5B_R1D_REPORT.md)
- [production_spec/stage5_production_rig/stage5b_r1e/STAGE5B_R1E_REPORT.md](../research/production_spec/stage5_production_rig/stage5b_r1e/STAGE5B_R1E_REPORT.md)
- [production_spec/stage5_production_rig/stage5a/STAGE5A_PRODUCTION_RIG_REPORT_R1.md](../research/production_spec/stage5_production_rig/stage5a/STAGE5A_PRODUCTION_RIG_REPORT_R1.md)
- [production_spec/stage5_production_rig/stage5a_r2a/STAGE5A_R2A_AUTHORITY_RECONCILIATION_REPORT.md](../research/production_spec/stage5_production_rig/stage5a_r2a/STAGE5A_R2A_AUTHORITY_RECONCILIATION_REPORT.md)
- [production_spec/stage5_production_rig/cap37_thumb_index_crossing_causal_adjudication_r1/build_adjudication.py](../../src/legacy/production_spec/stage5_production_rig/cap37_thumb_index_crossing_causal_adjudication_r1/build_adjudication.py)
- [production_spec/stage5_production_rig/cap37_thumb_index_crossing_causal_adjudication_r1/causal_common.py](../../src/legacy/production_spec/stage5_production_rig/cap37_thumb_index_crossing_causal_adjudication_r1/causal_common.py)
- [production_spec/stage5_production_rig/cap37_thumb_index_crossing_causal_adjudication_r1/local_analysis_and_visual_samples.py](../../src/legacy/production_spec/stage5_production_rig/cap37_thumb_index_crossing_causal_adjudication_r1/local_analysis_and_visual_samples.py)
- [production_spec/stage5_production_rig/cap37_thumb_index_crossing_causal_adjudication_r1/prepare.py](../../src/legacy/production_spec/stage5_production_rig/cap37_thumb_index_crossing_causal_adjudication_r1/prepare.py)
- [production_spec/stage5_production_rig/cap37_thumb_index_crossing_causal_adjudication_r1/render_matched.py](../../src/legacy/production_spec/stage5_production_rig/cap37_thumb_index_crossing_causal_adjudication_r1/render_matched.py)
- [production_spec/stage5_production_rig/cap37_thumb_index_crossing_causal_adjudication_r1/run_causal.py](../../src/legacy/production_spec/stage5_production_rig/cap37_thumb_index_crossing_causal_adjudication_r1/run_causal.py)
- [production_spec/stage5_production_rig/cap37_thumb_index_crossing_causal_adjudication_r1/verify_artifacts.py](../../src/legacy/production_spec/stage5_production_rig/cap37_thumb_index_crossing_causal_adjudication_r1/verify_artifacts.py)
- [production_spec/stage5_production_rig/cap37_thumb_index_crossing_causal_adjudication_r1/verify_frozen.py](../../src/legacy/production_spec/stage5_production_rig/cap37_thumb_index_crossing_causal_adjudication_r1/verify_frozen.py)
- [production_spec/stage5_production_rig/cap37_thumb_index_crossing_human_closure_r1/record_human_closure.py](../../src/legacy/production_spec/stage5_production_rig/cap37_thumb_index_crossing_human_closure_r1/record_human_closure.py)
- [production_spec/stage5_production_rig/cap_derived_r2_r3_input_reconciliation_r1/scripts/complete_records.py](../../src/legacy/production_spec/stage5_production_rig/cap_derived_r2_r3_input_reconciliation_r1/scripts/complete_records.py)
- [production_spec/stage5_production_rig/cap_derived_r2_r3_input_reconciliation_r1/scripts/extract_live.py](../../src/legacy/production_spec/stage5_production_rig/cap_derived_r2_r3_input_reconciliation_r1/scripts/extract_live.py)
- [production_spec/stage5_production_rig/cap_derived_r2_r3_input_reconciliation_r1/scripts/intake.py](../../src/legacy/production_spec/stage5_production_rig/cap_derived_r2_r3_input_reconciliation_r1/scripts/intake.py)

## 输入、输出与大型证据

该目录原始成员 1523 项；拟公开身份记录 1416 项。
- `production_spec/stage5_production_rig/geometry_propagation_after_donor_transfer_r1/RIGHT_HAND_STAGE5A_CORRECTED_RIG_DONOR_TRANSFER_R1.blend` → `hands-research-r1-selected-015.zip` / `payload/production_spec/stage5_production_rig/geometry_propagation_after_donor_transfer_r1/RIGHT_HAND_STAGE5A_CORRECTED_RIG_DONOR_TRANSFER_R1.blend`
- `production_spec/stage5_production_rig/geometry_propagation_after_donor_transfer_r1/RIGHT_HAND_STAGE5B_R2_DONOR_TRANSFER_GEOMETRY_R1.blend` → `hands-research-r1-selected-015.zip` / `payload/production_spec/stage5_production_rig/geometry_propagation_after_donor_transfer_r1/RIGHT_HAND_STAGE5B_R2_DONOR_TRANSFER_GEOMETRY_R1.blend`
- `production_spec/stage5_production_rig/geometry_propagation_after_palmar_donor_restoration_r1/RIGHT_HAND_STAGE5A_CORRECTED_RIG_DONOR_TRANSFER_PALMAR_ROOT_R1.blend` → `hands-research-r1-selected-016.zip` / `payload/production_spec/stage5_production_rig/geometry_propagation_after_palmar_donor_restoration_r1/RIGHT_HAND_STAGE5A_CORRECTED_RIG_DONOR_TRANSFER_PALMAR_ROOT_R1.blend`
- `production_spec/stage5_production_rig/geometry_propagation_after_palmar_donor_restoration_r1/RIGHT_HAND_STAGE5B_R2_DONOR_TRANSFER_PALMAR_ROOT_GEOMETRY_R1.blend` → `hands-research-r1-selected-016.zip` / `payload/production_spec/stage5_production_rig/geometry_propagation_after_palmar_donor_restoration_r1/RIGHT_HAND_STAGE5B_R2_DONOR_TRANSFER_PALMAR_ROOT_GEOMETRY_R1.blend`
- `production_spec/stage5_production_rig/human_thumb_kinematic_authority_correction_r1/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_THUMB_KINEMATIC_CORRECTED_R1.blend` → `hands-research-r1-selected-016.zip` / `payload/production_spec/stage5_production_rig/human_thumb_kinematic_authority_correction_r1/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_THUMB_KINEMATIC_CORRECTED_R1.blend`
- `production_spec/stage5_production_rig/stage5a/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R1.blend` → `hands-research-r1-selected-016.zip` / `payload/production_spec/stage5_production_rig/stage5a/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R1.blend`
- `production_spec/stage5_production_rig/stage5a_r2/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2.blend` → `hands-research-r1-selected-016.zip` / `payload/production_spec/stage5_production_rig/stage5a_r2/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2.blend`
- `production_spec/stage5_production_rig/stage5a_r2a/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend` → `hands-research-r1-selected-016.zip` / `payload/production_spec/stage5_production_rig/stage5a_r2a/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend`
- `production_spec/stage5_production_rig/stage5b_r1/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1.blend` → `hands-research-r1-selected-016.zip` / `payload/production_spec/stage5_production_rig/stage5b_r1/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1.blend`
- `production_spec/stage5_production_rig/stage5b_r1a/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1A.blend` → `hands-research-r1-selected-016.zip` / `payload/production_spec/stage5_production_rig/stage5b_r1a/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1A.blend`
- `production_spec/stage5_production_rig/stage5b_r1b/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend` → `hands-research-r1-selected-016.zip` / `payload/production_spec/stage5_production_rig/stage5b_r1b/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend`
- `production_spec/stage5_production_rig/stage5b_r1b/_tmp/rebuild/first.blend` → `hands-research-r1-selected-016.zip` / `payload/production_spec/stage5_production_rig/stage5b_r1b/_tmp/rebuild/first.blend`
- `production_spec/stage5_production_rig/stage5b_r1c/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1C.blend` → `hands-research-r1-selected-016.zip` / `payload/production_spec/stage5_production_rig/stage5b_r1c/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1C.blend`
- `production_spec/stage5_production_rig/stage5b_r1d/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1D.blend` → `hands-research-r1-selected-016.zip` / `payload/production_spec/stage5_production_rig/stage5b_r1d/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1D.blend`
- `production_spec/stage5_production_rig/stage5b_r1e/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1E.blend` → `hands-research-r1-selected-016.zip` / `payload/production_spec/stage5_production_rig/stage5b_r1e/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1E.blend`
- `production_spec/stage5_production_rig/targeted_rig_and_skin_data_rebuild_after_approval_r1/RIGHT_HAND_STAGE5B_TARGETED_SKIN_REBUILD_R1.blend` → `hands-research-r1-selected-017.zip` / `payload/production_spec/stage5_production_rig/targeted_rig_and_skin_data_rebuild_after_approval_r1/RIGHT_HAND_STAGE5B_TARGETED_SKIN_REBUILD_R1.blend`
- `production_spec/stage5_production_rig/targeted_rig_and_skin_data_rebuild_r2/RIGHT_HAND_STAGE5B_TARGETED_SKIN_REBUILD_R2.blend` → `hands-research-r1-selected-017.zip` / `payload/production_spec/stage5_production_rig/targeted_rig_and_skin_data_rebuild_r2/RIGHT_HAND_STAGE5B_TARGETED_SKIN_REBUILD_R2.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
