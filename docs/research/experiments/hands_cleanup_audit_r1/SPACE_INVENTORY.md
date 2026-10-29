# Hands 工作区空间清单 R1

任务 `HANDS_WORKSPACE_DEEP_CLEANUP_AUDIT_R1`。审计日期：2026-10-11（Asia/Shanghai）。Hands 只读，未删除、移动、压缩、保存 Blend、修改配置或运行求解/渲染。报告只写在工作区外。

## 总量与扫描完整性

实测 **24,709,011,213 bytes = 23.012 GiB = 24.709 GB**；38,188 个普通文件，1,239 个目录（含根目录）。用户所称约23GB对应约23 GiB。以下排名均为实际已枚举文件的逻辑长度求和。

本轮发现目录/文件 reparse 链接0、硬链接0；按卷ID+文件ID去重后体积与逻辑体积相同。Windows GetCompressedFileSizeW 返回总量同为 24,709,011,213 bytes；这不是精确的磁盘空闲空间承诺，目录/MFT、allocation unit 与文件系统开销未计。未跟随任何 reparse 目录；若存在链接，其目标只记录不进入，故不可能误入外部工作区。

枚举/stat/分配大小错误0，扫描内 file size/mtime/fileID 变化0，目录mtime变化0。纠正了 Windows DirEntry.stat 的 fileID=0问题：正式库存使用 os.stat(...,follow_symlinks=False)，不以 DirEntry 的缺省ID去重。正式数据以 inventory.json / files.jsonl 为准。文本索引5778份、读取错误0；40份大于12MB的数值 JSON 未全文做路径索引，逐份列于 reference_index.json，不能宣称完整运行时依赖已经证明。

## 一级目录

| 目录 | GiB | 文件数 |
| --- | --- | --- |
| audits | 20.547 | 34273 |
| production_spec | 2.350 | 3834 |
| references | 0.114 | 43 |
| docs | 0.000 | 21 |
| .workbuddy | 0.000 | 8 |
| reference_manifest | 0.000 | 1 |
| canonical_upright_action_key043_front_stop_compatibility_r1 | 0.000 | 7 |
| (root files) | 0.000 | 1 |

## 二级目录完整排名

| 目录 | GiB | 文件数 |
| --- | --- | --- |
| audits\minuet_stage_c_r2_local_finger_overlap_refinement | 2.154 | 2818 |
| audits\minuet_stage_b_r2_left_hand_continuous_accompaniment | 1.479 | 1514 |
| audits\minuet_stage_c_r1_dual_hand_synchronized_performance | 1.281 | 1149 |
| production_spec\stage5_production_rig | 1.223 | 1539 |
| audits\minuet_stage_c_lightweight_animation_poc_r1 | 1.195 | 1184 |
| audits\piano_pedagogical_motion_refinement_r1 | 1.194 | 1185 |
| audits\minuet_stage_b_r3_budget_policy_candidate_recovery_r1 | 1.120 | 1155 |
| audits\minuet_stage_a_r2_natural_continuous_motion | 1.115 | 1110 |
| audits\minuet_target_key_hand_position_planning_r1 | 1.101 | 1087 |
| audits\first_web_real_motion_deformation_fix_r1 | 0.870 | 1910 |
| production_spec\stage6_deformation | 0.788 | 1563 |
| audits\piano_keyboard_low_dof_root_pose_validation_r1 | 0.624 | 908 |
| audits\pianovam_retarget_local_axis_mapping_correction_r1 | 0.555 | 1415 |
| audits\right_hand_first_web_product_impact_go_no_go_r1 | 0.537 | 695 |
| audits\piano_keyboard_spatial_anchor_and_contact_validation_r1 | 0.534 | 693 |
| audits\right_hand_articulation_contact_short_phrase_r1 | 0.511 | 543 |
| audits\piano_hand_visual_first_short_phrase_validation_r1 | 0.509 | 535 |
| audits\midi_driven_dual_hand_piano_performance_poc_r1 | 0.508 | 4427 |
| audits\right_hand_lbs_vs_dqs_real_motion_ab_r1 | 0.445 | 980 |
| audits\pianovam_single_sample_right_hand_retarget_r1 | 0.425 | 1348 |
| audits\dual_hand_synchronized_real_motion_validation_r1 | 0.356 | 660 |
| audits\official_l1_product_rebase_feasibility_r1 | 0.316 | 285 |
| audits\minuet_stage_b_r1_left_hand_triad_coordination | 0.315 | 380 |
| production_spec\stage4_blender | 0.295 | 585 |
| audits\left_little_finger_moving_key_reachability_r1 | 0.289 | 2827 |
| audits\midi_driven_hand_posture_and_contact_refinement_r1 | 0.282 | 271 |
| audits\palmar_digit_root_local_donor_shape_restoration_design_r1 | 0.262 | 217 |
| audits\left_hand_real_motion_retarget_validation_r1 | 0.254 | 670 |
| audits\piano_hand_static_to_dynamic_transition_r1 | 0.242 | 453 |
| audits\left_octave_root_finger_coordinated_clearance_r1 | 0.178 | 320 |
| audits\palmar_macro_proportion_restoration_from_official_source_r1 | 0.156 | 157 |
| audits\palmar_digit_root_surface_irregularity_causal_diagnosis_r1 | 0.151 | 114 |
| audits\official_l1_first_web_targeted_deformation_fix_r1 | 0.113 | 126 |
| audits\right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1 | 0.112 | 106 |
| audits\palmar_thenar_source_shape_restoration_r1 | 0.102 | 113 |
| audits\palmar_digit_root_local_donor_shape_restoration_feasibility_r1 | 0.098 | 94 |
| references\licenses | 0.094 | 29 |
| audits\targeted_thenar_opposition_weight_tuning_r1 | 0.082 | 89 |
| audits\original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1 | 0.080 | 166 |
| audits\minuet_stage_c_r6_whole_phrase_spatial_planning | 0.076 | 72 |
| audits\minuet_stage_c_r3_right_hand_local_spatial_clearance | 0.072 | 188 |
| audits\proximal_exclusive_shared_extent_authority_r1 | 0.071 | 48 |
| audits\first_web_deformation_architecture_rebuild_assessment_r1 | 0.071 | 119 |
| audits\minuet_stage_c_r4_multi_finger_coordinated_clearance | 0.059 | 93 |
| audits\local_donor_shape_transfer_amendment_design_r1 | 0.058 | 147 |
| audits\minimal_local_geometry_amendment_design_r1 | 0.051 | 113 |
| audits\right_hand_first_web_production_weight_qualification_r1 | 0.050 | 66 |
| audits\right_hand_first_web_skinning_field_vs_dof_diagnosis_r1 | 0.044 | 76 |
| audits\pianovam_first_web_joint_contribution_isolation_r1 | 0.042 | 74 |
| audits\pianovam_first_web_corrective_ab_isolation_r1 | 0.033 | 59 |
| audits\minimal_local_geometry_amendment_design_r3 | 0.031 | 90 |
| audits\cap_skin_driver_and_weight_authority_reconciliation_r1 | 0.031 | 45 |
| production_spec\stage1c_c1_qualification | 0.029 | 65 |
| audits\piano_hand_four_pose_static_feasibility_r1 | 0.027 | 51 |
| audits\minimal_local_geometry_amendment_design_r2 | 0.026 | 62 |
| audits\right_hand_first_web_full_static_weight_field_causal_probe_r1 | 0.026 | 49 |
| audits\piano_hand_static_posture_clearance_refinement_r2 | 0.026 | 51 |
| audits\minuet_stage_c_root_finger_spatial_feasibility_r1 | 0.026 | 63 |
| audits\left_octave_neighbor_key_clearance_conflict_isolation_r1 | 0.024 | 46 |
| audits\left_hand_canonical_mirror_baseline_r1 | 0.024 | 71 |
| audits\minimal_local_geometry_amendment_design_r4 | 0.023 | 176 |
| audits\right_hand_first_web_topology_causal_probe_r1 | 0.022 | 48 |
| audits\proximal_partial_circumference_semantic_boundary_authority_r1 | 0.016 | 41 |
| audits\r3_recovery_input_contract_finalization_r1 | 0.011 | 44 |
| references\piano_motion | 0.010 | 7 |
| references\hand_r_canonical_ai | 0.010 | 7 |
| audits\right_hand_product_baseline_r2_promotion_r1 | 0.007 | 28 |
| audits\minuet_stage_b_r3_guard_fix_contact_validation_r1 | 0.005 | 34 |
| production_spec\right_hand_product_baseline_r1 | 0.005 | 16 |
| audits\thumb_frozen_web_partial_circumference_frontier_authority_r1 | 0.005 | 36 |
| audits\narrow_proximal_web_to_palm_transition_authority_r1 | 0.005 | 32 |
| audits\piano_pedagogical_demonstration_audit_r1 | 0.005 | 25 |
| audits\r3_full_recompute_and_authority_revalidation_r1 | 0.004 | 41 |
| production_spec\runtime_parity | 0.003 | 31 |
| audits\r3_sheet_identity_validator_reconciliation_r1 | 0.003 | 31 |
| audits\piano_hand_posture_reference_and_static_feasibility_r1 | 0.003 | 29 |
| audits\minuet_stage_b_r3_left_hand_global_contact_placement | 0.003 | 42 |
| audits\thumb_shared_strip_longitudinal_stop_rule_authority_r1 | 0.003 | 32 |
| audits\dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1 | 0.003 | 45 |
| audits\real_piano_reference_gap_closure_and_static_posture_probe_r2 | 0.003 | 36 |
| production_spec\stage2_bootstrap | 0.002 | 8 |
| audits\minuet_stage_b_r3_dynamic_failure_isolation_r1 | 0.002 | 21 |
| production_spec\stage3_geometry_review | 0.002 | 8 |
| audits\skin_static_gate_semantics_and_scope_reconciliation_r1 | 0.001 | 15 |
| audits\right_hand_first_web_foundational_rebuild_target_r1 | 0.001 | 30 |
| audits\minuet_stage_c_r5_phase_aware_spatial_window_implementation | 0.001 | 23 |
| audits\minuet_stage_c_motion_planning_architecture_reassessment_r1 | 0.001 | 11 |
| production_spec\right_hand_product_baseline_r2 | 0.001 | 2 |
| production_spec\left_hand_product_baseline_r1 | 0.001 | 2 |
| audits\narrow_proximal_domain_wrappers_and_unary_units_authority_review_r1 | 0.001 | 28 |
| audits\minuet_in_g_longer_phrase_validation_r1 | 0.001 | 25 |
| audits\human_r3_fresh_result_authority_freeze_r1 | 0.001 | 17 |
| audits\piano_hand_motion_technology_research_r1 | 0.001 | 55 |
| audits\human_proximal_partial_circumference_boundary_authority_freeze_r1 | 0.001 | 14 |
| .workbuddy\memory | 0.000 | 8 |
| audits\left_octave_coordinated_motion_architecture_reassessment_r1 | 0.000 | 11 |
| audits\left_hand_product_baseline_r1_promotion_r1 | 0.000 | 16 |
| production_spec\stage0_r1_3_1_frame_audit | 0.000 | 13 |

## audits 每个任务目录实际体积

| 任务 | GiB | 文件数 |
| --- | --- | --- |
| minuet_stage_c_r2_local_finger_overlap_refinement | 2.154 | 2818 |
| minuet_stage_b_r2_left_hand_continuous_accompaniment | 1.479 | 1514 |
| minuet_stage_c_r1_dual_hand_synchronized_performance | 1.281 | 1149 |
| minuet_stage_c_lightweight_animation_poc_r1 | 1.195 | 1184 |
| piano_pedagogical_motion_refinement_r1 | 1.194 | 1185 |
| minuet_stage_b_r3_budget_policy_candidate_recovery_r1 | 1.120 | 1155 |
| minuet_stage_a_r2_natural_continuous_motion | 1.115 | 1110 |
| minuet_target_key_hand_position_planning_r1 | 1.101 | 1087 |
| first_web_real_motion_deformation_fix_r1 | 0.870 | 1910 |
| piano_keyboard_low_dof_root_pose_validation_r1 | 0.624 | 908 |
| pianovam_retarget_local_axis_mapping_correction_r1 | 0.555 | 1415 |
| right_hand_first_web_product_impact_go_no_go_r1 | 0.537 | 695 |
| piano_keyboard_spatial_anchor_and_contact_validation_r1 | 0.534 | 693 |
| right_hand_articulation_contact_short_phrase_r1 | 0.511 | 543 |
| piano_hand_visual_first_short_phrase_validation_r1 | 0.509 | 535 |
| midi_driven_dual_hand_piano_performance_poc_r1 | 0.508 | 4427 |
| right_hand_lbs_vs_dqs_real_motion_ab_r1 | 0.445 | 980 |
| pianovam_single_sample_right_hand_retarget_r1 | 0.425 | 1348 |
| dual_hand_synchronized_real_motion_validation_r1 | 0.356 | 660 |
| official_l1_product_rebase_feasibility_r1 | 0.316 | 285 |
| minuet_stage_b_r1_left_hand_triad_coordination | 0.315 | 380 |
| left_little_finger_moving_key_reachability_r1 | 0.289 | 2827 |
| midi_driven_hand_posture_and_contact_refinement_r1 | 0.282 | 271 |
| palmar_digit_root_local_donor_shape_restoration_design_r1 | 0.262 | 217 |
| left_hand_real_motion_retarget_validation_r1 | 0.254 | 670 |
| piano_hand_static_to_dynamic_transition_r1 | 0.242 | 453 |
| left_octave_root_finger_coordinated_clearance_r1 | 0.178 | 320 |
| palmar_macro_proportion_restoration_from_official_source_r1 | 0.156 | 157 |
| palmar_digit_root_surface_irregularity_causal_diagnosis_r1 | 0.151 | 114 |
| official_l1_first_web_targeted_deformation_fix_r1 | 0.113 | 126 |
| right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1 | 0.112 | 106 |
| palmar_thenar_source_shape_restoration_r1 | 0.102 | 113 |
| palmar_digit_root_local_donor_shape_restoration_feasibility_r1 | 0.098 | 94 |
| targeted_thenar_opposition_weight_tuning_r1 | 0.082 | 89 |
| original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1 | 0.080 | 166 |
| minuet_stage_c_r6_whole_phrase_spatial_planning | 0.076 | 72 |
| minuet_stage_c_r3_right_hand_local_spatial_clearance | 0.072 | 188 |
| proximal_exclusive_shared_extent_authority_r1 | 0.071 | 48 |
| first_web_deformation_architecture_rebuild_assessment_r1 | 0.071 | 119 |
| minuet_stage_c_r4_multi_finger_coordinated_clearance | 0.059 | 93 |
| local_donor_shape_transfer_amendment_design_r1 | 0.058 | 147 |
| minimal_local_geometry_amendment_design_r1 | 0.051 | 113 |
| right_hand_first_web_production_weight_qualification_r1 | 0.050 | 66 |
| right_hand_first_web_skinning_field_vs_dof_diagnosis_r1 | 0.044 | 76 |
| pianovam_first_web_joint_contribution_isolation_r1 | 0.042 | 74 |
| pianovam_first_web_corrective_ab_isolation_r1 | 0.033 | 59 |
| minimal_local_geometry_amendment_design_r3 | 0.031 | 90 |
| cap_skin_driver_and_weight_authority_reconciliation_r1 | 0.031 | 45 |
| piano_hand_four_pose_static_feasibility_r1 | 0.027 | 51 |
| minimal_local_geometry_amendment_design_r2 | 0.026 | 62 |
| right_hand_first_web_full_static_weight_field_causal_probe_r1 | 0.026 | 49 |
| piano_hand_static_posture_clearance_refinement_r2 | 0.026 | 51 |
| minuet_stage_c_root_finger_spatial_feasibility_r1 | 0.026 | 63 |
| left_octave_neighbor_key_clearance_conflict_isolation_r1 | 0.024 | 46 |
| left_hand_canonical_mirror_baseline_r1 | 0.024 | 71 |
| minimal_local_geometry_amendment_design_r4 | 0.023 | 176 |
| right_hand_first_web_topology_causal_probe_r1 | 0.022 | 48 |
| proximal_partial_circumference_semantic_boundary_authority_r1 | 0.016 | 41 |
| r3_recovery_input_contract_finalization_r1 | 0.011 | 44 |
| right_hand_product_baseline_r2_promotion_r1 | 0.007 | 28 |
| minuet_stage_b_r3_guard_fix_contact_validation_r1 | 0.005 | 34 |
| thumb_frozen_web_partial_circumference_frontier_authority_r1 | 0.005 | 36 |
| narrow_proximal_web_to_palm_transition_authority_r1 | 0.005 | 32 |
| piano_pedagogical_demonstration_audit_r1 | 0.005 | 25 |
| r3_full_recompute_and_authority_revalidation_r1 | 0.004 | 41 |
| r3_sheet_identity_validator_reconciliation_r1 | 0.003 | 31 |
| piano_hand_posture_reference_and_static_feasibility_r1 | 0.003 | 29 |
| minuet_stage_b_r3_left_hand_global_contact_placement | 0.003 | 42 |
| thumb_shared_strip_longitudinal_stop_rule_authority_r1 | 0.003 | 32 |
| dorsal_mcp_position_only_formulation_and_geometric_gate_reconciliation_r1 | 0.003 | 45 |
| real_piano_reference_gap_closure_and_static_posture_probe_r2 | 0.003 | 36 |
| minuet_stage_b_r3_dynamic_failure_isolation_r1 | 0.002 | 21 |
| skin_static_gate_semantics_and_scope_reconciliation_r1 | 0.001 | 15 |
| right_hand_first_web_foundational_rebuild_target_r1 | 0.001 | 30 |
| minuet_stage_c_r5_phase_aware_spatial_window_implementation | 0.001 | 23 |
| minuet_stage_c_motion_planning_architecture_reassessment_r1 | 0.001 | 11 |
| narrow_proximal_domain_wrappers_and_unary_units_authority_review_r1 | 0.001 | 28 |
| minuet_in_g_longer_phrase_validation_r1 | 0.001 | 25 |
| human_r3_fresh_result_authority_freeze_r1 | 0.001 | 17 |
| piano_hand_motion_technology_research_r1 | 0.001 | 55 |
| human_proximal_partial_circumference_boundary_authority_freeze_r1 | 0.001 | 14 |
| left_octave_coordinated_motion_architecture_reassessment_r1 | 0.000 | 11 |
| left_hand_product_baseline_r1_promotion_r1 | 0.000 | 16 |

## 最大50个文件

| 序号 | 完整相对路径（根目录见上） | MiB | 类型 |
| --- | --- | --- | --- |
| 1 | audits\minuet_stage_c_r2_local_finger_overlap_refinement\BASELINE_REFERENCE.npz | 93.24 | .npz |
| 2 | production_spec\stage5_production_rig\joint_surface_rest_zero_bind_revalidation_after_palmar_donor_restoration_r1\CLEAN_REOPEN_NATIVE_PAYLOADS_R1.json | 72.29 | .json |
| 3 | production_spec\stage5_production_rig\joint_surface_rest_zero_bind_revalidation_after_donor_transfer_r1\CLEAN_REOPEN_NATIVE_PAYLOADS_R1.json | 72.28 | .json |
| 4 | audits\dual_hand_synchronized_real_motion_validation_r1\evaluated_dual_motion.npz | 66.75 | .npz |
| 5 | production_spec\stage5_production_rig\geometry_propagation_after_palmar_donor_restoration_r1\PALMAR_STAGE5_BEFORE_SAVE_PAYLOADS_R1.json | 63.91 | .json |
| 6 | production_spec\stage5_production_rig\geometry_propagation_after_donor_transfer_r1\STAGE5_BEFORE_SAVE_PROPAGATION_PAYLOADS_R1.json | 63.89 | .json |
| 7 | audits\piano_keyboard_low_dof_root_pose_validation_r1\model_a_evaluations.npz | 60.77 | .npz |
| 8 | audits\piano_keyboard_spatial_anchor_and_contact_validation_r1\spatial_evaluations.npz | 60.68 | .npz |
| 9 | audits\piano_keyboard_spatial_anchor_and_contact_validation_r1\hand_motion_canonical.npz | 60.24 | .npz |
| 10 | production_spec\stage5_production_rig\geometry_propagation_after_palmar_donor_restoration_r1\FROZEN_INPUT_NATIVE_PAYLOADS_R1.json | 57.06 | .json |
| 11 | audits\proximal_exclusive_shared_extent_authority_r1\INDEX_BRANCH_CONTINUITY_AUDIT.json | 52.58 | .json |
| 12 | audits\minuet_stage_c_r1_dual_hand_synchronized_performance\APPROVED_ACTION_PAYLOADS.json | 51.82 | .json |
| 13 | references\licenses\blender_human_base_meshes\human-base-meshes-bundle-v1.4.1.zip | 48.30 | .zip |
| 14 | audits\right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1\LINEAGE_RAW_READONLY_EXTRACTION.json | 47.63 | .json |
| 15 | references\licenses\blender_human_base_meshes\extracted\human-base-meshes-bundle-v1.4.1\human_base_meshes_bundle.blend | 47.13 | .blend |
| 16 | production_spec\stage5_production_rig\geometry_propagation_after_donor_transfer_r1\FROZEN_INPUT_NATIVE_PAYLOADS_R1.json | 43.05 | .json |
| 17 | audits\minuet_stage_c_r1_dual_hand_synchronized_performance\R_approved_reference.npz | 38.35 | .npz |
| 18 | audits\minuet_stage_a_r2_natural_continuous_motion\evaluated.npz | 36.07 | .npz |
| 19 | audits\minuet_stage_c_r1_dual_hand_synchronized_performance\L_approved_reference.npz | 34.38 | .npz |
| 20 | audits\minuet_stage_b_r3_budget_policy_candidate_recovery_r1\evaluated.npz | 33.67 | .npz |
| 21 | audits\minuet_stage_b_r2_left_hand_continuous_accompaniment\evaluated.npz | 33.66 | .npz |
| 22 | production_spec\stage5_production_rig\true_cap_bound_revalidation_after_donor_transfer_r1\RUN_B\POSED_BOUND_PAYLOAD.json | 33.59 | .json |
| 23 | production_spec\stage5_production_rig\true_cap_bound_revalidation_after_donor_transfer_r1\RUN_A\POSED_BOUND_PAYLOAD.json | 33.59 | .json |
| 24 | production_spec\stage5_production_rig\true_cap_bound_recompute_after_dependency_reconciliation_r1\TRUE_CAP_POSED_BOUND_RECOMPUTATION_R1.json | 33.59 | .json |
| 25 | production_spec\stage5_production_rig\true_cap_bound_recompute_after_dependency_reconciliation_r1\RUN_B\POSED_BOUND_PAYLOAD.json | 33.59 | .json |
| 26 | production_spec\stage5_production_rig\true_cap_bound_recompute_after_dependency_reconciliation_r1\RUN_A\POSED_BOUND_PAYLOAD.json | 33.59 | .json |
| 27 | audits\midi_driven_hand_posture_and_contact_refinement_r1\evaluated_candidate.npz | 32.65 | .npz |
| 28 | audits\midi_driven_dual_hand_piano_performance_poc_r1\evaluated_candidate.npz | 32.54 | .npz |
| 29 | audits\minuet_stage_c_r6_whole_phrase_spatial_planning\ACTUAL_TERMINAL_SKIN.npz | 31.98 | .npz |
| 30 | audits\right_hand_articulation_contact_short_phrase_r1\evaluated.npz | 29.74 | .npz |
| 31 | audits\piano_hand_visual_first_short_phrase_validation_r1\evaluated.npz | 29.71 | .npz |
| 32 | audits\minuet_target_key_hand_position_planning_r1\evaluated.npz | 29.66 | .npz |
| 33 | production_spec\stage5_production_rig\true_cap_bound_revalidation_after_donor_transfer_r1\POST_DONOR_VIRTUAL_120_RECIPE_RECOMPUTATION_R1.json | 29.43 | .json |
| 34 | production_spec\stage4_blender\stage4c_donor_transfer_palmar_root_r1\PALMAR_APPLICATION_BEFORE_SAVE_SNAPSHOT_R1.json | 27.64 | .json |
| 35 | audits\minuet_stage_c_r6_whole_phrase_spatial_planning\SOURCE_MODEL.npz | 26.83 | .npz |
| 36 | audits\midi_driven_dual_hand_piano_performance_poc_r1\_deps\pymupdf\mupdfcpp64.dll | 25.08 | .dll |
| 37 | audits\left_octave_root_finger_coordinated_clearance_r1\evaluated_coordinated.npz | 24.03 | .npz |
| 38 | production_spec\stage6_deformation\full_stage6a_requalification_after_donor_transfer_r1\FULL_STAGE6A_DORSAL_MCP_REGRESSION_R1.json | 23.12 | .json |
| 39 | production_spec\stage6_deformation\full_stage6a_requalification_after_donor_transfer_r1\FULL_STAGE6A_DORSAL_MCP_EXACT_STRUCTURE_R1.json | 21.39 | .json |
| 40 | audits\original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1\RAW_SOURCE_GEOMETRY.json | 20.11 | .json |
| 41 | audits\midi_driven_dual_hand_piano_performance_poc_r1\_deps\numpy.libs\libscipy_openblas64_-ed4f167a5330424524f45258e7ca2c8d.dll | 19.64 | .dll |
| 42 | audits\midi_driven_dual_hand_piano_performance_poc_r1\_deps\scipy.libs\libscipy_openblas-197ee2fc9b4d071f7e048078cac74115.dll | 19.32 | .dll |
| 43 | audits\left_little_finger_moving_key_reachability_r1\_deps313\scipy.libs\libscipy_openblas-197ee2fc9b4d071f7e048078cac74115.dll | 19.32 | .dll |
| 44 | audits\left_hand_real_motion_retarget_validation_r1\evaluated_motion.npz | 16.57 | .npz |
| 45 | audits\cap_skin_driver_and_weight_authority_reconciliation_r1\SAVED_RIG_AND_SKIN_EVIDENCE_R1.json | 16.20 | .json |
| 46 | production_spec\stage6_deformation\full_stage6a_requalification_after_donor_transfer_r1\POSED_COORDINATES_R1.json | 15.80 | .json |
| 47 | production_spec\stage6_deformation\full_stage6a_requalification_r1\POSED_COORDINATES_R1.json | 15.80 | .json |
| 48 | production_spec\stage5_production_rig\cap37_thumb_index_crossing_causal_adjudication_r1\CAUSAL_COORDINATE_EVIDENCE.json | 15.24 | .json |
| 49 | production_spec\stage5_production_rig\static_skin_compatibility_revalidation_after_palmar_donor_restoration_r1\CURRENT_CLEAN_REOPEN_NATIVE_PAYLOAD_R1.json | 14.67 | .json |
| 50 | production_spec\stage5_production_rig\static_skin_compatibility_revalidation_after_palmar_donor_restoration_r1\OLD_R2_CLEAN_REOPEN_NATIVE_PAYLOAD_R1.json | 14.67 | .json |

## 类型分布

| 后缀 | GiB | 文件数 | 占总量 |
| --- | --- | --- | --- |
| .png | 19.533 | 26121 | 84.88% |
| .json | 1.774 | 2769 | 7.71% |
| .npz | 0.800 | 98 | 3.48% |
| .blend | 0.242 | 90 | 1.05% |
| .mp4 | 0.133 | 121 | 0.58% |
| .pyd | 0.124 | 233 | 0.54% |
| .dll | 0.082 | 5 | 0.36% |
| .pyc | 0.067 | 2539 | 0.29% |
| .py | 0.062 | 3605 | 0.27% |
| .jpg | 0.062 | 164 | 0.27% |
| .zip | 0.047 | 1 | 0.20% |
| .html | 0.028 | 102 | 0.12% |
| .gif | 0.014 | 10 | 0.06% |
| .wav | 0.009 | 55 | 0.04% |
| .blend1 | 0.005 | 3 | 0.02% |
| .txt | 0.004 | 230 | 0.02% |
| .lib | 0.004 | 23 | 0.02% |
| .log | 0.004 | 247 | 0.02% |
| .dat | 0.003 | 52 | 0.01% |
| .h | 0.003 | 117 | 0.01% |
| .md | 0.002 | 354 | 0.01% |
| .pyi | 0.002 | 303 | 0.01% |
| .csv | 0.001 | 36 | 0.01% |
| .npy | 0.001 | 17 | 0.00% |
| (无后缀) | 0.001 | 45 | 0.00% |
| .exe | 0.001 | 7 | 0.00% |
| .js | 0.001 | 9 | 0.00% |
| .pxd | 0.001 | 31 | 0.00% |
| .bin | 0.000 | 2 | 0.00% |
| .sav | 0.000 | 96 | 0.00% |
| .arff | 0.000 | 32 | 0.00% |
| .a | 0.000 | 212 | 0.00% |
| .svg | 0.000 | 36 | 0.00% |
| .mat | 0.000 | 222 | 0.00% |
| .cjs | 0.000 | 37 | 0.00% |
| .c | 0.000 | 5 | 0.00% |
| .pdf | 0.000 | 1 | 0.00% |
| .f90 | 0.000 | 62 | 0.00% |
| .pyx | 0.000 | 10 | 0.00% |
| .mjs | 0.000 | 2 | 0.00% |
| .f | 0.000 | 25 | 0.00% |
| .build | 0.000 | 9 | 0.00% |
| .apache | 0.000 | 1 | 0.00% |
| .rst | 0.000 | 1 | 0.00% |
| .sh | 0.000 | 3 | 0.00% |
| .ani | 0.000 | 2 | 0.00% |
| .fits | 0.000 | 1 | 0.00% |
| .tsv | 0.000 | 1 | 0.00% |
| .nc | 0.000 | 6 | 0.00% |
| .ly | 0.000 | 2 | 0.00% |
| .r | 0.000 | 2 | 0.00% |
| .cpp | 0.000 | 1 | 0.00% |
| .mid | 0.000 | 3 | 0.00% |
| .pyf | 0.000 | 8 | 0.00% |
| .ps1 | 0.000 | 2 | 0.00% |
| .template | 0.000 | 1 | 0.00% |
| .css | 0.000 | 1 | 0.00% |
| .bsd | 0.000 | 1 | 0.00% |
| .pkl | 0.000 | 1 | 0.00% |
| .gz | 0.000 | 3 | 0.00% |
| .ini | 0.000 | 1 | 0.00% |
| .pc | 0.000 | 1 | 0.00% |
| .f95 | 0.000 | 1 | 0.00% |
| .cfg | 0.000 | 1 | 0.00% |
| .inc | 0.000 | 1 | 0.00% |
| .whl | 0.000 | 2 | 0.00% |
| .typed | 0.000 | 3 | 0.00% |

## 单文件≥10MB的类型分布

| 后缀 | GiB | 数量 |
| --- | --- | --- |
| .json | 1.108 | 43 |
| .npz | 0.776 | 21 |
| .dll | 0.081 | 4 |
| .zip | 0.047 | 1 |
| .blend | 0.046 | 1 |
| .pyd | 0.012 | 1 |
| .html | 0.010 | 1 |

## 主要占用解释

PNG 19.533 GiB（约84.88%）是主因，多为按视角保存的连续无损帧。JSON约1.774 GiB、NPZ约0.800 GiB是原生提取、Action、求解/实际skin记录；其中有后续真实依赖。Blend约0.242 GiB/90份，MP4约0.133 GiB/121份，blend1约0.005 GiB/3份，日志仅约0.004 GiB。因此只删视频或Blend备份无法显著瘦身。Action主要嵌在Blend和JSON中，没有独立Action后缀总量可诚实单列；90份Blend全部保留。

重复扫描确认 919 组 ≥1KiB 完全相同文件，理论额外副本 0.637 GiB。先按大小分桶，再读取头尾各64KiB预筛，最后完整SHA-256确认。采样读取 0.883 GB，完整哈希读取 1.246 GB；未对24.7GB全盘重复哈希。第三方_deps、pyc、小于1KiB及OUT_OF_SCOPE不做重复搜索；这些范围的重复情况为未核查，不能报为无重复。

重复不自动等于可删：独立复跑RUN_A/RUN_B、按路径引用的重复视频、冻结资产别名仍有审核或代码用途。duplicate总量与渲染候选大量重叠，不再加到预计释放量。

## 完整原始数据

`inventory.json`、`files.jsonl`、`directories.json`、`duplicates.json`、`reference_index.json`、`FILE_CLASSIFICATIONS.jsonl`。分类覆盖所有38188文件，未扫描的文本依赖范围有明确记录。
