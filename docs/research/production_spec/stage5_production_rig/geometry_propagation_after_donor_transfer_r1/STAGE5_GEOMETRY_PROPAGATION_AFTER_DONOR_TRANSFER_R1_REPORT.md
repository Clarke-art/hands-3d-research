# STAGE5_GEOMETRY_PROPAGATION_AFTER_DONOR_TRANSFER_R1

PASS_GEOMETRY_PROPAGATED_WITH_RIG_AND_WEIGHTS_FROZEN

仅从三个已校验输入传播完整 3416 点的 native stored geometry。Corrected rig 从工作区全部 36 个 `.blend` 的实际 SHA256 唯一恢复；没有回退到 historical rig。两个新资产分别由各自正式 Stage5 来源打开、赋值全部坐标后独立保存，原资产未覆盖。

两个资产的 3416 / 3416 local 与 world 坐标均精确匹配实际新 Stage4C；相对各自旧资产恰好改变同一 approved54，outside54 为 0。V/E/F、native IDs、edge endpoints、face cycles 和 loops 完全相同。

各自完整非几何快照逐值相等：21 bones、原 hierarchy、head/tail、matrix/rest frame、inherit flags、实际 EditBone.roll、pose channels、object/armature transforms、原 custom properties、约束、groups/order、所有含零 weight entries、UV、材料 slots/assignments/node settings/links、modifier settings/bindings、smooth/sharp 与 custom-normal state。R2 的 16 groups、3416 weight vectors 的 authority hash 在保存重开后不变。历史 R2 rig provenance 与 corrected 源的差异按各自来源保留。

实际 roll 只在输入提取与重开检查的最后一步进入 EDIT 读取；无 edit setter、无 roll 计算、无退出 EDIT 或保存该临时会话。传播保存过程从不进入 armature EDIT。两个资产分别通过独立 factory-startup 进程重开，完整快照 serialization drift = 0。

JOINT_SURFACE_DELTA_DIAGNOSTIC 记录每个固定 joint head/tail 到旧、新 raw mesh 同一 native-index fan triangulation 的最近距离，仅为 DIAGNOSTIC_ONLY，没有门槛、正式资格 verdict 或移动 joint。Zero evaluation 仅在临时内存清零 pose channels 并检查有限值、已有 modifier/group/bone references；不保存，不做 rest/zero/bind 资格判定。未运行任何 Stage6 pose。

cap37 / old cap9 / FIRST_WEB21 / fresh R3 962 / historical317 仅检查 frozen ID membership。9 个 Stage6A blockers 保留原 FAIL_CLOSED；没有重跑、修复、裁决或分类。全工作区 3909 个先前文件 SHA256 保持原样，新文件仅在本目录。

## 完整字段

| 字段 | 结果 |
|---|---|
| phase | STAGE5_GEOMETRY_PROPAGATION_AFTER_DONOR_TRANSFER_R1 |
| recorded_at_utc | 2026-10-05T12:44:24.427426+00:00 |
| NEW_STAGE4C_SOURCE | <HANDS_ROOT>\production_spec\stage4_blender\stage4c_donor_transfer_r1\RIGHT_HAND_ENGINEERING_STAGE4C_DONOR_TRANSFER_R1.blend |
| NEW_STAGE4C_SOURCE_SHA256 | 5f48ffa5ac6ff6d10b5d3bde1348571437b3a4fdf5c3ecfb97922e7dc0acd4d1 |
| CORRECTED_RIG_SOURCE_PATH | <HANDS_ROOT>\production_spec\stage5_production_rig\human_thumb_kinematic_authority_correction_r1\RIGHT_HAND_STAGE5A_PRODUCTION_RIG_THUMB_KINEMATIC_CORRECTED_R1.blend |
| CORRECTED_RIG_SOURCE_SHA256 | 5d5f86bb59135715a77515468c2b76fe81e2a44e2e8c5d6c17fcc3d56d2147fe |
| R2_SOURCE_PATH | <HANDS_ROOT>\production_spec\stage5_production_rig\targeted_rig_and_skin_data_rebuild_r2\RIGHT_HAND_STAGE5B_TARGETED_SKIN_REBUILD_R2.blend |
| R2_SOURCE_SHA256 | adf757aeace8a0d69070b94f102b9bef9eb99da9847dd7a5639c4c2c3799dde9 |
| R2_SOURCE_WEIGHT_HASH | 1d9437a10354cdd98a2b5cb5e43be8cfabc519e232235483a615e76898129f55 |
| NEW_STAGE5A_DERIVED_PATH | <HANDS_ROOT>\production_spec\stage5_production_rig\geometry_propagation_after_donor_transfer_r1\RIGHT_HAND_STAGE5A_CORRECTED_RIG_DONOR_TRANSFER_R1.blend |
| NEW_STAGE5A_DERIVED_SHA256 | 513323c98a0d2a1c3b45f5543c6738476af7090447e84a0cc510d6e9606adc62 |
| NEW_STAGE5B_R2_DERIVED_PATH | <HANDS_ROOT>\production_spec\stage5_production_rig\geometry_propagation_after_donor_transfer_r1\RIGHT_HAND_STAGE5B_R2_DONOR_TRANSFER_GEOMETRY_R1.blend |
| NEW_STAGE5B_R2_DERIVED_SHA256 | d8ea48d5d09635a46aebabb7a6e516f2a2a8599c92f2ca68489cdbeb0ec6866d |
| NEW_STAGE4C_SOURCE_HASH_VERIFIED | PASS |
| CORRECTED_RIG_INPUT_HASH_VERIFIED | PASS |
| R2_INPUT_HASH_VERIFIED | PASS |
| STAGE5A_GEOMETRY_EQUALS_NEW_STAGE4C | PASS |
| STAGE5B_R2_GEOMETRY_EQUALS_NEW_STAGE4C | PASS |
| STAGE4C_TO_STAGE5A_VERTEX_MAX_DELTA_MM | 0.0 |
| STAGE4C_TO_STAGE5B_R2_VERTEX_MAX_DELTA_MM | 0.0 |
| OLD_TO_NEW_STAGE5A_CHANGED_VERTEX_COUNT | 54 |
| OLD_TO_NEW_R2_CHANGED_VERTEX_COUNT | 54 |
| OUTSIDE54_STAGE5A_GEOMETRY_DRIFT | 0 |
| OUTSIDE54_R2_GEOMETRY_DRIFT | 0 |
| FULL_NATIVE_COORDINATE_MATCH_COUNT_EACH | 3416 |
| NATIVE_V_E_F_EACH | [3416, 6828, 3414] |
| BONE_PAYLOAD_DELTA | 0 |
| JOINT_PAYLOAD_DELTA | 0 |
| NATIVE_ROLL_PAYLOAD_DELTA | 0 |
| R2_WEIGHT_VECTOR_HASH_AFTER_PROPAGATION | 1d9437a10354cdd98a2b5cb5e43be8cfabc519e232235483a615e76898129f55 |
| R2_WEIGHT_VECTOR_HASH_MATCH | PASS |
| GROUP_SET_ORDER_UNCHANGED | PASS |
| WEIGHT_SCALAR_DRIFT_INCLUDING_ZERO | 0 |
| TOPOLOGY_DRIFT | 0 |
| UV_DRIFT | 0 |
| MATERIAL_DRIFT | 0 |
| SMOOTH_SHARP_CUSTOM_NORMAL_STATE_DRIFT | 0 |
| MODIFIER_BINDING_UNCHANGED | PASS |
| AUTHORITY_ID_MEMBERSHIP_UNCHANGED | PASS |
| ZERO_EVAL_SMOKE | PASS |
| SAVE_REOPEN | PASS |
| SERIALIZATION_DRIFT | 0 |
| PROTECTED_HISTORY_DRIFT | 0 |
| PROTECTED_PREEXISTING_FILE_COUNT | 3909 |
| NEW_FILES_OUTSIDE_PHASE_DIRECTORY | 0 |
| FULL_STAGE6A_STATUS_RETAINED | FAIL_CLOSED_FULL_STAGE6A_REQUALIFICATION |
| MACHINE_HARD_BLOCKER_COUNT_RETAINED | 9 |
| full_stage6a_retained_evidence | {"path": "<HANDS_ROOT>\\production_spec\\stage6_deformation\\full_stage6a_requalification_r1\\FULL_STAGE6A_REQUALIFICATION_R1_STATUS.json", "sha256": "d2c3bb13a77dd123e278d21e98ebdb724706dd8c789f91f0d2ac9e4d2f03d0a6"} |
| STAGE5_GEOMETRY_PROPAGATION_VERDICT | PASS_GEOMETRY_PROPAGATED_WITH_RIG_AND_WEIGHTS_FROZEN |
| JOINT_SURFACE_DELTA_DIAGNOSTIC | DIAGNOSTIC_ONLY |
| JOINT_TO_SURFACE_REQUALIFICATION | NOT_RUN |
| REST_ZERO_BIND_REQUALIFICATION | NOT_RUN |
| STATIC_SKIN_REQUALIFICATION | NOT_RUN |
| TRUE_CAP_REQUALIFICATION | NOT_RUN |
| TARGETED_DEFORMATION | NOT_RUN |
| FULL42_RERUN | NOT_RUN |
| STAGE6B_STARTED | False |
| PRODUCTION_PROMOTION | NO |
| NEXT | JOINT_SURFACE_REST_ZERO_BIND_REVALIDATION_AFTER_DONOR_TRANSFER_R1 |
| NEXT_EXECUTED | False |
| STOP | True |

## 证据

- [STAGE5_CURRENT_LINEAGE_INPUT_RECOVERY_R1.json](../../../../artifacts/f35be29aa9869e978076.md)
- [STAGE5_INPUT_PAYLOAD_PREFLIGHT_R1.json](../../../../artifacts/da91cd73c26f97aa56ff.md)
- [STAGE5A_GEOMETRY_PROPAGATION_AUDIT_R1.json](../../../../artifacts/0ee38be3806805e34011.md)
- [STAGE5B_R2_GEOMETRY_PROPAGATION_AUDIT_R1.json](../../../../artifacts/763fe7cdfb2e66a61ac6.md)
- [STAGE5_RIG_PAYLOAD_EQUIVALENCE_R1.json](../../../../artifacts/04ebffc7c0ee616ffbe6.md)
- [STAGE5_WEIGHT_PAYLOAD_EQUIVALENCE_R1.json](../../../../artifacts/c5355fe579c5497a9cf4.md)
- [STAGE5_AUTHORITY_ID_MEMBERSHIP_AUDIT_R1.json](../../../../artifacts/1bb89f4999a61e15e249.md)
- [STAGE5_ZERO_EVAL_SMOKE_R1.json](../../../../artifacts/a3ee7993832e6d022ae4.md)
- [STAGE5_SAVE_REOPEN_AUDIT_R1.json](../../../../artifacts/4bbdfcc9f122e8331670.md)
- [JOINT_SURFACE_DELTA_DIAGNOSTIC_R1.json](../../../../artifacts/3479b3e67f79feb39478.md)
- [PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json](../../../../artifacts/8346705fd73035746cb7.md)

NEXT = JOINT_SURFACE_REST_ZERO_BIND_REVALIDATION_AFTER_DONOR_TRANSFER_R1，只记录，不执行。PRODUCTION_PROMOTION = NO。STOP。
