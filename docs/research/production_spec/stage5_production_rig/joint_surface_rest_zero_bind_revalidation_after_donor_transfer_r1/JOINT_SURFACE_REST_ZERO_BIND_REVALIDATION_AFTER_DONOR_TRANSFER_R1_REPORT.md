# JOINT_SURFACE_REST_ZERO_BIND_REVALIDATION_AFTER_DONOR_TRANSFER_R1

PASS_JOINT_REST_ZERO_BIND_REQUALIFIED

本轮为只读重新资格验证。三个新 geometry 输入、旧 corrected rig、旧 R2 均先校验实际 SHA256，再 factory-startup clean reopen。两个 Stage5 derivative 的完整 raw geometry 与 bone payload 一致，且相对于各自正式来源非几何数据精确继承。没有任何 blend 保存或 authority 写入。

当前语义恢复使用 R2/R2A 与正式 freeze/errata，加上随后 Human-approved thumb correction：16 deform heads 必须 ray-parity inside；wrist 使用 R2 冻结 transition band；CMC 使用 R2 locality sphere；MCP/PIP/DIP 使用既有冻结 T-01 axial frame/zone；四指 helper 使用已接受 own-digit surface/apex 规则；THUMB TIP 使用 corrected native terminal v284 与 non-deform helper convention，旧 cap REP 和旧 apex 阈值不再是它的权威。没有重新研究 anatomy、region、ownership、cap 或 locator。

对全部 21 heads，在实际旧 corrected raw geometry、新 Stage5A raw 和新 Stage5B raw 三条路径重新测量。R2 closest / 64-ray parity 函数仅通过 AST 复用；没有执行旧 builder 或旧 audit 顶层。16 deform heads 均 64/64 inside。所有 region 与 5 TIP helper 均 PASS。Signed distance 同时单列 nearest-normal projection 和 parity-signed distance，inside 不从法线方向推断。Native face/vertex/edge feature、old/new/delta 在逐 joint 表中完整记录。

最大 joint surface distance delta = RING_MCP_R +0.424279381116 mm（5.162971280100 → 5.587250661216 mm），其 ray parity 64/64，冻结 T-01 margin 8.875 mm。其余 head 的 surface distance delta = 0；全部 head/tail 排序及上一轮 fan diagnostic 的最大变化也单独保留。CMC 当前 clearance = 12.000322775338 mm，与旧 corrected baseline 一致；approved cage locality margin = 1.020410072993 mm。早期 R1 的小 clearance 不是当前 corrected rig 数值，也没有新增 deep-joint 条件。

Rest 骨架 21 bones 的名字/order、hierarchy、head/tail、actual EditBone.roll、rest matrices/local frames、deform/inheritance/connect flags、object/armature transforms 与各自正式来源逐值匹配；corrected thumb 六槽保持 native stored authority，未重算。独立读取 roll 只在临时会话最后进入 EDIT，无 setter、退出或保存。

Zero 使用当前正式 s6a_common.reset_pose（仅 AST 函数）：21 quaternion identity / location zero / scale one。所有 matrix_basis exact identity，pose-rest matrix max entry delta = 0；NaN/Inf、missing bone/group/modifier reference 与 residue 均 0。操作只在内存，不保存。

Actual R2 Armature modifier ON + ZERO 下 full 3416-point raw→evaluated：max 0.0000596700924622 mm；mean 0.00000602722814390 mm；RMS 0.0000104473156449 mm。当前 R2 FullStage6A 原 consumer 明确对 raw_RSSF_noise 采用 <= 0.0001 mm，Stage5B R1/R1B 也采用同一级原门槛；本轮只恢复该 zero/raw bind 语义，不运行任何 deformation 函数或 case。超出原数值残差门槛的点为 0。

Modifier order/target/settings、mesh/rig object transforms、group names/order、deform mapping 和每个权重 scalar（含零）与旧 R2 一致；完整 3416 weight vector hash 保持 authority。实际 Blender Armature modifier 不持有独立用户 bind matrix：其内部使用 object frame 与 bone rest inverse。报告实际 object matrix_parent_inverse，不创造字段、reparent、rebind 或计算新 inverse bind。

Matched 三列 Stage4C raw / R2 raw / R2 evaluated ZERO 的 close flat/native、grazing、side 视图已由 Codex直接图像检查，批准 donor contour 保留，未观察到 dent 回返或新 ridge/notch/local collapse。局部 native triangle area 非零、方向未反转；0/60/120° 的真实 native sections 作为补充证据。该判断只覆盖 zero/bind contour preservation，不授予新的 Human rig approval、static skin 或 posed deformation PASS。没有出现新增 borderline joint relation，故无新 Human gate。

已有 3950 个工作区文件 SHA256 全部保持原样，新文件仅在本轮目录。旧 Full42 仍 FAIL_CLOSED，9 blockers 原样保留。

## 最终字段

| 字段 | 结果 |
|---|---|
| phase | JOINT_SURFACE_REST_ZERO_BIND_REVALIDATION_AFTER_DONOR_TRANSFER_R1 |
| recorded_at_utc | 2026-10-05T13:17:15.931013+00:00 |
| inputs | {"STAGE4": {"path": "<HANDS_ROOT>\\production_spec\\stage4_blender\\stage4c_donor_transfer_r1\\RIGHT_HAND_ENGINEERING_STAGE4C_DONOR_TRANSFER_R1.blend", "sha256": "5f48ffa5ac6ff6d10b5d3bde1348571437b3a4fdf5c3ecfb97922e7dc0acd4d1"}, "CORRECTED": {"path": "<HANDS_ROOT>\\production_spec\\stage5_production_rig\\geometry_propagation_after_donor_transfer_r1\\RIGHT_HAND_STAGE5A_CORRECTED_RIG_DONOR_TRANSFER_R1.blend", "sha256": "513323c98a0d2a1c3b45f5543c6738476af7090447e84a0cc510d6e9606adc62"}, "R2": {"path": "<HANDS_ROOT>\\production_spec\\stage5_production_rig\\geometry_propagation_after_donor_transfer_r1\\RIGHT_HAND_STAGE5B_R2_DONOR_TRANSFER_GEOMETRY_R1.blend", "sha256": "d8ea48d5d09635a46aebabb7a6e516f2a2a8599c92f2ca68489cdbeb0ec6866d"}, "OLD_CORRECTED": {"path": "<HANDS_ROOT>\\production_spec\\stage5_production_rig\\human_thumb_kinematic_authority_correction_r1\\RIGHT_HAND_STAGE5A_PRODUCTION_RIG_THUMB_KINEMATIC_CORRECTED_R1.blend", "sha256": "5d5f86bb59135715a77515468c2b76fe81e2a44e2e8c5d6c17fcc3d56d2147fe"}, "OLD_R2": {"path": "<HANDS_ROOT>\\production_spec\\stage5_production_rig\\targeted_rig_and_skin_data_rebuild_r2\\RIGHT_HAND_STAGE5B_TARGETED_SKIN_REBUILD_R2.blend", "sha256": "adf757aeace8a0d69070b94f102b9bef9eb99da9847dd7a5639c4c2c3799dde9"}} |
| FORMAL_JOINT_COUNT | 21 |
| FORMAL_JOINTS_PASS | 21 |
| DEFORM_JOINT_INSIDE_FAILURE_COUNT | 0 |
| TIP_HELPER_FAILURE_COUNT | 0 |
| JOINT_REGION_FAILURE_COUNT | 0 |
| deform_inside_failures | [] |
| TIP_failures | [] |
| region_failures | [] |
| MAX_JOINT_SURFACE_DISTANCE_DELTA_MM | 0.42427938111618513 |
| MAX_JOINT_SURFACE_DISTANCE_DELTA_JOINT | RING_MCP_R |
| RING_MCP_SURFACE_DELTA_MM | 0.42427938111618513 |
| RING_MCP_OLD_SURFACE_DISTANCE_MM | 5.162971280100306 |
| RING_MCP_NEW_SURFACE_DISTANCE_MM | 5.587250661216491 |
| RING_MCP_INSIDE_VOTES | 64/64 |
| RING_MCP_T01_REGION_MARGIN_MM | 8.875 |
| THUMB_CMC_SURFACE_CLEARANCE_MM | 12.000322775338363 |
| THUMB_CMC_REGION_MARGIN_MM | 1.0204100729928527 |
| CORRECTED_THUMB_CHAIN_PRESERVED | PASS |
| BONE_PAYLOAD_DELTA | 0 |
| JOINT_PAYLOAD_DELTA | 0 |
| JOINT_HEAD_DELTA_MM | 0.0 |
| JOINT_TAIL_DELTA_MM | 0.0 |
| ROLL_DELTA | 0.0 |
| REST_MATRIX_DELTA | 0 |
| REST_RIG_PAYLOAD_MATCH | PASS |
| ZERO_POSE | PASS |
| NaN_INF_COUNT | 0 |
| BONE_MISSING_COUNT | 0 |
| GROUP_MISSING_COUNT | 0 |
| MODIFIER_REFERENCE_MISSING_COUNT | 0 |
| POSE_RESIDUE_COUNT | 0 |
| POSE_REST_MATRIX_MAX_ENTRY_DELTA | 0.0 |
| RAW_TO_BIND_MAX_DELTA_MM | 5.9670092462157264e-05 |
| RAW_TO_BIND_MEAN_DELTA_MM | 6.02722814390494e-06 |
| RAW_TO_BIND_RMS_DELTA_MM | 1.0447315644879861e-05 |
| RAW_TO_BIND_POINT_COUNT | 3416 |
| EXISTING_ZERO_BIND_GATE_MM | 0.0001 |
| OUTSIDE_EXPECTED_NUMERICAL_RESIDUE_COUNT | 0 |
| BIND_ZERO | PASS |
| DORSAL_MCP_DENT_REAPPEARED_AT_BIND_ZERO | NO |
| NEW_BIND_ZERO_RIDGE_NOTCH_COLLAPSE | NONE_OBSERVED |
| MODIFIER_BINDING | PASS |
| R2_WEIGHT_HASH | 1d9437a10354cdd98a2b5cb5e43be8cfabc519e232235483a615e76898129f55 |
| R2_WEIGHT_HASH_MATCH | PASS |
| JOINT_RELOCATION_REQUIRED | NO |
| RIG_REBUILD_REQUIRED | NO |
| WEIGHT_CHANGE_REQUIRED | NO |
| STATIC_SKIN_REQUALIFICATION | NOT_RUN |
| TRUE_CAP_RECOMPUTATION | NOT_RUN |
| TARGETED_DEFORMATION | NOT_RUN |
| STAGE6_POSE_COUNT | 0 |
| FULL42_RERUN | NOT_RUN |
| STAGE6B_STARTED | False |
| PRODUCTION_PROMOTION | NO |
| CLEAN_REOPEN | PASS |
| SERIALIZATION_DRIFT | 0 |
| BLEND_FILES_SAVED_THIS_PHASE | 0 |
| PROTECTED_HISTORY_DRIFT | 0 |
| PROTECTED_PREEXISTING_FILE_COUNT | 3950 |
| FULL_STAGE6A_STATUS_RETAINED | FAIL_CLOSED_FULL_STAGE6A_REQUALIFICATION |
| MACHINE_HARD_BLOCKER_COUNT_RETAINED | 9 |
| old_full42_status_source | {"path": "<HANDS_ROOT>\\production_spec\\stage6_deformation\\full_stage6a_requalification_r1\\FULL_STAGE6A_REQUALIFICATION_R1_STATUS.json", "sha256": "d2c3bb13a77dd123e278d21e98ebdb724706dd8c789f91f0d2ac9e4d2f03d0a6"} |
| old9_repaired_adjudicated_or_reclassified | False |
| VERDICT | PASS_JOINT_REST_ZERO_BIND_REQUALIFIED |
| NEXT | STATIC_SKIN_COMPATIBILITY_REVALIDATION_AFTER_DONOR_TRANSFER_R1 |
| NEXT_EXECUTED | False |
| STOP | True |

## 逐 joint 资格

| Joint | Inside votes | Surface mm | Δ mm | Region/helper | Status |
|---|---:|---:|---:|---|---|
| WRIST_R | 64/64 | 18.901024822 | +0.000000000 | FROZEN_WRIST_PALM_TRANSITION | PASS |
| THUMB_CMC_R | 64/64 | 12.000322775 | +0.000000000 | FROZEN_CMC_LOCALITY_SPHERE | PASS |
| THUMB_MCP_R | 64/64 | 9.484081826 | +0.000000000 | FROZEN_T01_AXIAL_ZONE | PASS |
| THUMB_IP_R | 64/64 | 6.217311454 | +0.000000000 | FROZEN_T01_AXIAL_ZONE | PASS |
| THUMB_TIP_R | N/A (non-deform) | 0.000000000 | +0.000000000 | CORRECTED_NATIVE_TERMINAL_SURFACE_LANDMARK | PASS |
| INDEX_MCP_R | 64/64 | 5.866985153 | +0.000000000 | FROZEN_T01_AXIAL_ZONE | PASS |
| INDEX_PIP_R | 64/64 | 6.102529536 | +0.000000000 | FROZEN_T01_AXIAL_ZONE | PASS |
| INDEX_DIP_R | 64/64 | 5.067485656 | +0.000000000 | FROZEN_T01_AXIAL_ZONE | PASS |
| INDEX_TIP_R | N/A (non-deform) | 0.254003730 | +0.000000000 | CARRY_FORWARD_APPROVED_FOUR_FINGER_SURFACE_APEX | PASS |
| MIDDLE_MCP_R | 64/64 | 6.136752535 | +0.000000000 | FROZEN_T01_AXIAL_ZONE | PASS |
| MIDDLE_PIP_R | 64/64 | 6.624789636 | +0.000000000 | FROZEN_T01_AXIAL_ZONE | PASS |
| MIDDLE_DIP_R | 64/64 | 5.965571830 | +0.000000000 | FROZEN_T01_AXIAL_ZONE | PASS |
| MIDDLE_TIP_R | N/A (non-deform) | 0.241906763 | +0.000000000 | CARRY_FORWARD_APPROVED_FOUR_FINGER_SURFACE_APEX | PASS |
| RING_MCP_R | 64/64 | 5.587250661 | +0.424279381 | FROZEN_T01_AXIAL_ZONE | PASS |
| RING_PIP_R | 64/64 | 6.212428845 | +0.000000000 | FROZEN_T01_AXIAL_ZONE | PASS |
| RING_DIP_R | 64/64 | 5.085878235 | +0.000000000 | FROZEN_T01_AXIAL_ZONE | PASS |
| RING_TIP_R | N/A (non-deform) | 0.232069764 | +0.000000000 | CARRY_FORWARD_APPROVED_FOUR_FINGER_SURFACE_APEX | PASS |
| LITTLE_MCP_R | 64/64 | 4.749688023 | +0.000000000 | FROZEN_T01_AXIAL_ZONE | PASS |
| LITTLE_PIP_R | 64/64 | 5.132156843 | +0.000000000 | FROZEN_T01_AXIAL_ZONE | PASS |
| LITTLE_DIP_R | 64/64 | 4.001341480 | +0.000000000 | FROZEN_T01_AXIAL_ZONE | PASS |
| LITTLE_TIP_R | N/A (non-deform) | 0.213540844 | +0.000000000 | CARRY_FORWARD_APPROVED_FOUR_FINGER_SURFACE_APEX | PASS |

[review.html](../../../../artifacts/4fa4464ef5e8af375e60.md)

NEXT = STATIC_SKIN_COMPATIBILITY_REVALIDATION_AFTER_DONOR_TRANSFER_R1，仅记录，未执行。PRODUCTION_PROMOTION = NO。STOP。
