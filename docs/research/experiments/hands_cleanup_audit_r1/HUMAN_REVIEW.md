# Human 审核：Hands 大规模瘦身 R1

实测 **23.012 GiB（24.709 GB）**。audits占 20.547 GiB，production_spec占 2.350 GiB。主因是PNG逐帧渲染，不是视频或Blend。

推荐批准深度清理中明确的DELETE_CANDIDATE：预计释放 **12.618 GiB（13.549 GB，54.8%）**，剩余 **10.394 GiB（11.160 GB）**。先批准保守方案则释放 6.039 GiB，剩余 16.973 GiB。深度包含保守，两者不能相加。

## 可以整目录删除的历史包

B2连续伴奏、旧target-key规划等大任务的_frames，历史PianoVAM/琴键空间/低DOF/双手实动的_render_frames和已编码motion序列，以及C2的before_frames。深度追加A2/B3 recovery/C2的非必要_frames及C1除两张审核poster以外的帧。保留任务根目录内代码、数值、Blend、视频、报告，可继续研发，不把曾参与研发的整个目录永久保护。

没有完整任务根目录能在现有证据下直接整包删除。多个FAIL_CLOSED任务仍是有效后续代码/对照输入；TASK_ASSESSMENTS.json逐个给出具体阻碍。

## 必须保护

RIGHT HAND R2和LEFT HAND R1正式冻结，右手R1永久回退，四个Human-approved静态场景，A2/B3 Human视觉批准源，全部Blend、NPZ、有效代码及_deps、MIDI/琴键/音频/双手核心程序、Human记录和必要审核依据。六个重点批准资产容器实测SHA匹配；未启动Blender，未重写任何资产。

## 不计入两档释放量的待决问题（4.551 GiB）

1. **动态逐帧审核是否必须继续可用？** lightweight与pedagogical两套_frames共约2.267 GiB，两个Human页面动态读取这些PNG。需要Human明确允许用现有视频/对照图取代无损滑块，或者另轮先改页面并验证。未决定前不可删除；此项若未来单独批准可再减至约 8.127 GiB，但不属于本次深度方案。

2. **历史验证是否必须逐路径完整复跑？** RUN_A/B大量逐顶点JSON经SHA确认相同，约0.18 GiB的双次复跑包仍被比较脚本读取。需要明确只保留规范结果/数值对照报告是否足够；原验证脚本要求两个路径存在，不能直接删除一个路径。

3. **大型before-save和原生JSON是否允许仅保留结果/报告？** 缺少旧状态独立资产或输入闭合证明；LINEAGE_RAW_READONLY_EXTRACTION和POSED_COORDINATES已有后续源码引用。需要逐项证实旧状态可恢复、实际路径不被读取、汇总报告能替代原始证据，而不是泛称“人工审核”。具体文件见下表。

4. **旧全目录哈希验证如何处理已批准删缓存？** 后续任务常校验PROTECTED_INPUTS_BEFORE中的所有历史文件。清理必然使这些历史全清单核验出现预期缺失；必须保留原清单并建立独立的审批例外账本，不能改旧记录，也不能让验证程序把任意新增缺失自动放行。核心数值/功能依赖不受候选删除影响，但全文件旧审核命令不会未经适配继续PASS。

## HUMAN_REVIEW精确列表（按空间排序）

| ID | 完整路径 | GiB | 缺少的明确证据/决定 |
| --- | --- | --- | --- |
| HUMAN_REVIEW-0326 | <HANDS_ROOT>\audits\piano_pedagogical_motion_refinement_r1\_frames | 1.134 | Human 是否允许废弃逐帧无损审核，改以完整视频和现有对照图为唯一入口；若保留网页功能，须另轮先改页并验证后再删除 |
| HUMAN_REVIEW-0327 | <HANDS_ROOT>\audits\minuet_stage_c_lightweight_animation_poc_r1\_frames | 1.134 | Human 是否允许废弃逐帧无损审核，改以完整视频和现有对照图为唯一入口；若保留网页功能，须另轮先改页并验证后再删除 |
| HUMAN_REVIEW-0347 | <HANDS_ROOT>\audits\first_web_real_motion_deformation_fix_r1\weight_1_motion | 0.165 | 补齐逐视角视频覆盖与序列生产链，确认非唯一对照资料 |
| HUMAN_REVIEW-0348 | <HANDS_ROOT>\audits\first_web_real_motion_deformation_fix_r1\weight_2_motion | 0.165 | 补齐逐视角视频覆盖与序列生产链，确认非唯一对照资料 |
| HUMAN_REVIEW-0349 | <HANDS_ROOT>\audits\right_hand_lbs_vs_dqs_real_motion_ab_r1\dqs_motion | 0.165 | 补齐逐视角视频覆盖与序列生产链，确认非唯一对照资料 |
| HUMAN_REVIEW-0352 | <HANDS_ROOT>\audits\right_hand_lbs_vs_dqs_real_motion_ab_r1\lbs_motion | 0.165 | 补齐逐视角视频覆盖与序列生产链，确认非唯一对照资料 |
| HUMAN_REVIEW-0353 | <HANDS_ROOT>\audits\pianovam_single_sample_right_hand_retarget_r1\raw_motion_frames | 0.162 | 补齐逐视角视频覆盖与序列生产链，确认非唯一对照资料 |
| HUMAN_REVIEW-0354 | <HANDS_ROOT>\audits\pianovam_single_sample_right_hand_retarget_r1\smoothed_motion_frames | 0.162 | 补齐逐视角视频覆盖与序列生产链，确认非唯一对照资料 |
| HUMAN_REVIEW-0357 | <HANDS_ROOT>\audits\pianovam_single_sample_right_hand_retarget_r1\review_frames | 0.074 | 补齐逐视角视频覆盖与序列生产链，确认非唯一对照资料 |
| HUMAN_REVIEW-0360 | <HANDS_ROOT>\production_spec\stage5_production_rig\joint_surface_rest_zero_bind_revalidation_after_palmar_donor_restoration_r1\CLEAN_REOPEN_NATIVE_PAYLOADS_R1.json | 0.071 | 核对实际 read/load 调用的完整路径而非同名命中；确认历史 before-save 状态有独立资产或等价快照；证明汇总报告足以替代稠密逐顶点证据，且原验证脚本允许已批准缺失 |
| HUMAN_REVIEW-0361 | <HANDS_ROOT>\production_spec\stage5_production_rig\joint_surface_rest_zero_bind_revalidation_after_donor_transfer_r1\CLEAN_REOPEN_NATIVE_PAYLOADS_R1.json | 0.071 | 核对实际 read/load 调用的完整路径而非同名命中；确认历史 before-save 状态有独立资产或等价快照；证明汇总报告足以替代稠密逐顶点证据，且原验证脚本允许已批准缺失 |
| HUMAN_REVIEW-0358 | <HANDS_ROOT>\audits\pianovam_retarget_local_axis_mapping_correction_r1\comparison_palmar_full | 0.069 | 补齐逐视角视频覆盖与序列生产链，确认非唯一对照资料 |
| HUMAN_REVIEW-0359 | <HANDS_ROOT>\audits\pianovam_retarget_local_axis_mapping_correction_r1\comparison_dorsal_full | 0.069 | 补齐逐视角视频覆盖与序列生产链，确认非唯一对照资料 |
| HUMAN_REVIEW-0362 | <HANDS_ROOT>\production_spec\stage5_production_rig\geometry_propagation_after_palmar_donor_restoration_r1\PALMAR_STAGE5_BEFORE_SAVE_PAYLOADS_R1.json | 0.062 | 核对实际 read/load 调用的完整路径而非同名命中；确认历史 before-save 状态有独立资产或等价快照；证明汇总报告足以替代稠密逐顶点证据，且原验证脚本允许已批准缺失 |
| HUMAN_REVIEW-0363 | <HANDS_ROOT>\production_spec\stage5_production_rig\geometry_propagation_after_donor_transfer_r1\STAGE5_BEFORE_SAVE_PROPAGATION_PAYLOADS_R1.json | 0.062 | 核对实际 read/load 调用的完整路径而非同名命中；确认历史 before-save 状态有独立资产或等价快照；证明汇总报告足以替代稠密逐顶点证据，且原验证脚本允许已批准缺失 |
| HUMAN_REVIEW-0401 | <HANDS_ROOT>\production_spec\stage4_blender\stage4b_rssf\_tmp | 0.060 | Human 是否仍要求 RUN_A/RUN_B 双次独立复跑记录；明确保留唯一脚本和事故/修复证据，并重新核对绝对路径引用 |
| HUMAN_REVIEW-0364 | <HANDS_ROOT>\production_spec\stage5_production_rig\geometry_propagation_after_palmar_donor_restoration_r1\FROZEN_INPUT_NATIVE_PAYLOADS_R1.json | 0.056 | 核对实际 read/load 调用的完整路径而非同名命中；确认历史 before-save 状态有独立资产或等价快照；证明汇总报告足以替代稠密逐顶点证据，且原验证脚本允许已批准缺失 |
| HUMAN_REVIEW-0365 | <HANDS_ROOT>\audits\proximal_exclusive_shared_extent_authority_r1\INDEX_BRANCH_CONTINUITY_AUDIT.json | 0.051 | 核对实际 read/load 调用的完整路径而非同名命中；确认历史 before-save 状态有独立资产或等价快照；证明汇总报告足以替代稠密逐顶点证据，且原验证脚本允许已批准缺失 |
| HUMAN_REVIEW-0366 | <HANDS_ROOT>\audits\right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1\LINEAGE_RAW_READONLY_EXTRACTION.json | 0.047 | 核对实际 read/load 调用的完整路径而非同名命中；确认历史 before-save 状态有独立资产或等价快照；证明汇总报告足以替代稠密逐顶点证据，且原验证脚本允许已批准缺失 |
| HUMAN_REVIEW-0387 | <HANDS_ROOT>\production_spec\stage6_deformation\stage6b\_tmp | 0.043 | Human 是否仍要求 RUN_A/RUN_B 双次独立复跑记录；明确保留唯一脚本和事故/修复证据，并重新核对绝对路径引用 |
| HUMAN_REVIEW-0367 | <HANDS_ROOT>\production_spec\stage5_production_rig\geometry_propagation_after_donor_transfer_r1\FROZEN_INPUT_NATIVE_PAYLOADS_R1.json | 0.042 | 核对实际 read/load 调用的完整路径而非同名命中；确认历史 before-save 状态有独立资产或等价快照；证明汇总报告足以替代稠密逐顶点证据，且原验证脚本允许已批准缺失 |
| HUMAN_REVIEW-0388 | <HANDS_ROOT>\production_spec\stage6_deformation\stage6a_r1a\_tmp | 0.036 | Human 是否仍要求 RUN_A/RUN_B 双次独立复跑记录；明确保留唯一脚本和事故/修复证据，并重新核对绝对路径引用 |
| HUMAN_REVIEW-0368 | <HANDS_ROOT>\production_spec\stage5_production_rig\true_cap_bound_revalidation_after_donor_transfer_r1\RUN_B\POSED_BOUND_PAYLOAD.json | 0.033 | 核对实际 read/load 调用的完整路径而非同名命中；确认历史 before-save 状态有独立资产或等价快照；证明汇总报告足以替代稠密逐顶点证据，且原验证脚本允许已批准缺失 |
| HUMAN_REVIEW-0369 | <HANDS_ROOT>\production_spec\stage5_production_rig\true_cap_bound_revalidation_after_donor_transfer_r1\RUN_A\POSED_BOUND_PAYLOAD.json | 0.033 | 核对实际 read/load 调用的完整路径而非同名命中；确认历史 before-save 状态有独立资产或等价快照；证明汇总报告足以替代稠密逐顶点证据，且原验证脚本允许已批准缺失 |
| HUMAN_REVIEW-0370 | <HANDS_ROOT>\production_spec\stage5_production_rig\true_cap_bound_recompute_after_dependency_reconciliation_r1\TRUE_CAP_POSED_BOUND_RECOMPUTATION_R1.json | 0.033 | 核对实际 read/load 调用的完整路径而非同名命中；确认历史 before-save 状态有独立资产或等价快照；证明汇总报告足以替代稠密逐顶点证据，且原验证脚本允许已批准缺失 |
| HUMAN_REVIEW-0371 | <HANDS_ROOT>\production_spec\stage5_production_rig\true_cap_bound_recompute_after_dependency_reconciliation_r1\RUN_B\POSED_BOUND_PAYLOAD.json | 0.033 | 核对实际 read/load 调用的完整路径而非同名命中；确认历史 before-save 状态有独立资产或等价快照；证明汇总报告足以替代稠密逐顶点证据，且原验证脚本允许已批准缺失 |
| HUMAN_REVIEW-0372 | <HANDS_ROOT>\production_spec\stage5_production_rig\true_cap_bound_recompute_after_dependency_reconciliation_r1\RUN_A\POSED_BOUND_PAYLOAD.json | 0.033 | 核对实际 read/load 调用的完整路径而非同名命中；确认历史 before-save 状态有独立资产或等价快照；证明汇总报告足以替代稠密逐顶点证据，且原验证脚本允许已批准缺失 |
| HUMAN_REVIEW-0373 | <HANDS_ROOT>\production_spec\stage5_production_rig\true_cap_bound_revalidation_after_donor_transfer_r1\POST_DONOR_VIRTUAL_120_RECIPE_RECOMPUTATION_R1.json | 0.029 | 核对实际 read/load 调用的完整路径而非同名命中；确认历史 before-save 状态有独立资产或等价快照；证明汇总报告足以替代稠密逐顶点证据，且原验证脚本允许已批准缺失 |
| HUMAN_REVIEW-0374 | <HANDS_ROOT>\production_spec\stage4_blender\stage4c_donor_transfer_palmar_root_r1\PALMAR_APPLICATION_BEFORE_SAVE_SNAPSHOT_R1.json | 0.027 | 核对实际 read/load 调用的完整路径而非同名命中；确认历史 before-save 状态有独立资产或等价快照；证明汇总报告足以替代稠密逐顶点证据，且原验证脚本允许已批准缺失 |
| HUMAN_REVIEW-0375 | <HANDS_ROOT>\production_spec\stage6_deformation\full_stage6a_requalification_after_donor_transfer_r1\FULL_STAGE6A_DORSAL_MCP_REGRESSION_R1.json | 0.023 | 核对实际 read/load 调用的完整路径而非同名命中；确认历史 before-save 状态有独立资产或等价快照；证明汇总报告足以替代稠密逐顶点证据，且原验证脚本允许已批准缺失 |
| HUMAN_REVIEW-0376 | <HANDS_ROOT>\production_spec\stage6_deformation\full_stage6a_requalification_after_donor_transfer_r1\FULL_STAGE6A_DORSAL_MCP_EXACT_STRUCTURE_R1.json | 0.021 | 核对实际 read/load 调用的完整路径而非同名命中；确认历史 before-save 状态有独立资产或等价快照；证明汇总报告足以替代稠密逐顶点证据，且原验证脚本允许已批准缺失 |
| HUMAN_REVIEW-0377 | <HANDS_ROOT>\audits\original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1\RAW_SOURCE_GEOMETRY.json | 0.020 | 核对实际 read/load 调用的完整路径而非同名命中；确认历史 before-save 状态有独立资产或等价快照；证明汇总报告足以替代稠密逐顶点证据，且原验证脚本允许已批准缺失 |
| HUMAN_REVIEW-0378 | <HANDS_ROOT>\audits\cap_skin_driver_and_weight_authority_reconciliation_r1\SAVED_RIG_AND_SKIN_EVIDENCE_R1.json | 0.016 | 核对实际 read/load 调用的完整路径而非同名命中；确认历史 before-save 状态有独立资产或等价快照；证明汇总报告足以替代稠密逐顶点证据，且原验证脚本允许已批准缺失 |
| HUMAN_REVIEW-0379 | <HANDS_ROOT>\production_spec\stage6_deformation\full_stage6a_requalification_after_donor_transfer_r1\POSED_COORDINATES_R1.json | 0.015 | 核对实际 read/load 调用的完整路径而非同名命中；确认历史 before-save 状态有独立资产或等价快照；证明汇总报告足以替代稠密逐顶点证据，且原验证脚本允许已批准缺失 |
| HUMAN_REVIEW-0380 | <HANDS_ROOT>\production_spec\stage6_deformation\full_stage6a_requalification_r1\POSED_COORDINATES_R1.json | 0.015 | 核对实际 read/load 调用的完整路径而非同名命中；确认历史 before-save 状态有独立资产或等价快照；证明汇总报告足以替代稠密逐顶点证据，且原验证脚本允许已批准缺失 |
| HUMAN_REVIEW-0381 | <HANDS_ROOT>\production_spec\stage5_production_rig\cap37_thumb_index_crossing_causal_adjudication_r1\CAUSAL_COORDINATE_EVIDENCE.json | 0.015 | 核对实际 read/load 调用的完整路径而非同名命中；确认历史 before-save 状态有独立资产或等价快照；证明汇总报告足以替代稠密逐顶点证据，且原验证脚本允许已批准缺失 |
| HUMAN_REVIEW-0382 | <HANDS_ROOT>\production_spec\stage5_production_rig\static_skin_compatibility_revalidation_after_palmar_donor_restoration_r1\CURRENT_CLEAN_REOPEN_NATIVE_PAYLOAD_R1.json | 0.014 | 核对实际 read/load 调用的完整路径而非同名命中；确认历史 before-save 状态有独立资产或等价快照；证明汇总报告足以替代稠密逐顶点证据，且原验证脚本允许已批准缺失 |
| HUMAN_REVIEW-0383 | <HANDS_ROOT>\production_spec\stage5_production_rig\static_skin_compatibility_revalidation_after_palmar_donor_restoration_r1\OLD_R2_CLEAN_REOPEN_NATIVE_PAYLOAD_R1.json | 0.014 | 核对实际 read/load 调用的完整路径而非同名命中；确认历史 before-save 状态有独立资产或等价快照；证明汇总报告足以替代稠密逐顶点证据，且原验证脚本允许已批准缺失 |
| HUMAN_REVIEW-0384 | <HANDS_ROOT>\production_spec\stage5_production_rig\static_skin_compatibility_revalidation_after_donor_transfer_r1\CURRENT_CLEAN_REOPEN_NATIVE_PAYLOAD_R1.json | 0.014 | 核对实际 read/load 调用的完整路径而非同名命中；确认历史 before-save 状态有独立资产或等价快照；证明汇总报告足以替代稠密逐顶点证据，且原验证脚本允许已批准缺失 |
| HUMAN_REVIEW-0385 | <HANDS_ROOT>\production_spec\stage5_production_rig\static_skin_compatibility_revalidation_after_donor_transfer_r1\OLD_R2_CLEAN_REOPEN_NATIVE_PAYLOAD_R1.json | 0.014 | 核对实际 read/load 调用的完整路径而非同名命中；确认历史 before-save 状态有独立资产或等价快照；证明汇总报告足以替代稠密逐顶点证据，且原验证脚本允许已批准缺失 |
| HUMAN_REVIEW-0389 | <HANDS_ROOT>\production_spec\stage5_production_rig\true_cap_bound_revalidation_after_donor_transfer_r1\RUN_B | 0.014 | Human 是否仍要求 RUN_A/RUN_B 双次独立复跑记录；明确保留唯一脚本和事故/修复证据，并重新核对绝对路径引用 |
| HUMAN_REVIEW-0390 | <HANDS_ROOT>\production_spec\stage5_production_rig\true_cap_bound_revalidation_after_donor_transfer_r1\RUN_A | 0.014 | Human 是否仍要求 RUN_A/RUN_B 双次独立复跑记录；明确保留唯一脚本和事故/修复证据，并重新核对绝对路径引用 |
| HUMAN_REVIEW-0391 | <HANDS_ROOT>\production_spec\stage5_production_rig\true_cap_bound_recompute_after_dependency_reconciliation_r1\RUN_B | 0.012 | Human 是否仍要求 RUN_A/RUN_B 双次独立复跑记录；明确保留唯一脚本和事故/修复证据，并重新核对绝对路径引用 |
| HUMAN_REVIEW-0392 | <HANDS_ROOT>\production_spec\stage5_production_rig\true_cap_bound_recompute_after_dependency_reconciliation_r1\RUN_A | 0.012 | Human 是否仍要求 RUN_A/RUN_B 双次独立复跑记录；明确保留唯一脚本和事故/修复证据，并重新核对绝对路径引用 |
| HUMAN_REVIEW-0395 | <HANDS_ROOT>\production_spec\stage5_production_rig\stage5b_r1e_endpoint_authority_review\_tmp | 0.006 | Human 是否仍要求 RUN_A/RUN_B 双次独立复跑记录；明确保留唯一脚本和事故/修复证据，并重新核对绝对路径引用 |
| HUMAN_REVIEW-0397 | <HANDS_ROOT>\production_spec\stage5_production_rig\stage5b_r1a\_tmp | 0.006 | Human 是否仍要求 RUN_A/RUN_B 双次独立复跑记录；明确保留唯一脚本和事故/修复证据，并重新核对绝对路径引用 |
| HUMAN_REVIEW-0396 | <HANDS_ROOT>\production_spec\stage5_production_rig\stage5b_r1b\_tmp | 0.004 | Human 是否仍要求 RUN_A/RUN_B 双次独立复跑记录；明确保留唯一脚本和事故/修复证据，并重新核对绝对路径引用 |
| HUMAN_REVIEW-0394 | <HANDS_ROOT>\production_spec\stage5_production_rig\stage5b_r1e_narrow_anatomical_review\_tmp | 0.003 | Human 是否仍要求 RUN_A/RUN_B 双次独立复跑记录；明确保留唯一脚本和事故/修复证据，并重新核对绝对路径引用 |
| HUMAN_REVIEW-0399 | <HANDS_ROOT>\production_spec\stage5_production_rig\stage5a\_tmp | 0.003 | Human 是否仍要求 RUN_A/RUN_B 双次独立复跑记录；明确保留唯一脚本和事故/修复证据，并重新核对绝对路径引用 |
| HUMAN_REVIEW-0322 | <HANDS_ROOT>\audits\pianovam_single_sample_right_hand_retarget_r1\RIGHT_HAND_PIANO_MOTION_TEST_R1.blend1 | 0.003 | 确认此备份是否是唯一的修改前状态；需要其正式等价副本或可接受丢失的决定 |
| HUMAN_REVIEW-0400 | <HANDS_ROOT>\production_spec\stage4_blender\stage4c\_tmp | 0.003 | Human 是否仍要求 RUN_A/RUN_B 双次独立复跑记录；明确保留唯一脚本和事故/修复证据，并重新核对绝对路径引用 |
| HUMAN_REVIEW-0393 | <HANDS_ROOT>\production_spec\stage5_production_rig\stage5b_r1e_thumb_distal_cap_native_branch_identity_audit_r1\_tmp | 0.002 | Human 是否仍要求 RUN_A/RUN_B 双次独立复跑记录；明确保留唯一脚本和事故/修复证据，并重新核对绝对路径引用 |
| HUMAN_REVIEW-0402 | <HANDS_ROOT>\audits\right_hand_first_web_topology_causal_probe_r1\_tmp | 0.001 | Human 是否仍要求 RUN_A/RUN_B 双次独立复跑记录；明确保留唯一脚本和事故/修复证据，并重新核对绝对路径引用 |
| HUMAN_REVIEW-0398 | <HANDS_ROOT>\production_spec\stage5_production_rig\stage5a_r2a\_tmp | 0.001 | Human 是否仍要求 RUN_A/RUN_B 双次独立复跑记录；明确保留唯一脚本和事故/修复证据，并重新核对绝对路径引用 |
| HUMAN_REVIEW-0386 | <HANDS_ROOT>\production_spec\stage6_deformation\stage6b_r1b\_tmp | 0.001 | Human 是否仍要求 RUN_A/RUN_B 双次独立复跑记录；明确保留唯一脚本和事故/修复证据，并重新核对绝对路径引用 |

## 执行前约束

只审批具体entry ID或方案中已有的精确成员列表；原文件状态变化、新增文件、引用变化或reparse/hardlink变化均需重审。preflight_readonly.py只有扫描/哈希/输出报告，无删除能力。当前没有实际删除批准，没有进入执行阶段。

**STOP — HUMAN REVIEW。等待Human审核具体删除清单。**
