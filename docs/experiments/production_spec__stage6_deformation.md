# production_spec/stage6_deformation

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 每个 case 严格按：`RESET ALL POSE BONES → 验证 zero state → 只应用目标关节 rotation → depsgraph evaluate →

出处：[STAGE6A_REPORT_R1.md](../research/production_spec/stage6_deformation/stage6a/STAGE6A_REPORT_R1.md)

> - **四指（36 case）**：NaN/折叠 = 0；topology 不变；前臂不动；非目标指 clean 顶点不动；

出处：[STAGE6A_REPORT_R1.md](../research/production_spec/stage6_deformation/stage6a/STAGE6A_REPORT_R1.md)

## 技术路线

原报告未单独概述路线；以下实现文件与原报告共同界定方法，不能由文件名推断算法成功：

- [build_package.py](../../src/legacy/production_spec/stage6_deformation/current_full_stage6a_crossing_human_adjudication_prep_r1/build_package.py)
- [common.py](../../src/legacy/production_spec/stage6_deformation/current_full_stage6a_crossing_human_adjudication_prep_r1/common.py)
- [prepare.py](../../src/legacy/production_spec/stage6_deformation/current_full_stage6a_crossing_human_adjudication_prep_r1/prepare.py)
- [render_location_only.py](../../src/legacy/production_spec/stage6_deformation/current_full_stage6a_crossing_human_adjudication_prep_r1/render_location_only.py)
- [render_only.py](../../src/legacy/production_spec/stage6_deformation/current_full_stage6a_crossing_human_adjudication_prep_r1/render_only.py)

## 测试结论

> - **状态结论**：`STAGE6A = READY_FOR_HUMAN_REVIEW`；`ISOLATED_FLEX_DEFORMATION = PASS_PENDING_HUMAN_REVIEW`；`STAGE6B = NOT_STARTED`

出处：[STAGE6A_REPORT_R1.md](../research/production_spec/stage6_deformation/stage6a/STAGE6A_REPORT_R1.md)

> | Stage5B freeze receipt | `STAGE5B = FINAL_APPROVED` ／ `PRODUCTION_SKIN_WEIGHT_STATIC = FINAL_APPROVED` ／ `STAGE5B_FREEZE = PASS` ／ `STAGE6 = READY_TO_BEGIN` ✅ |

出处：[STAGE6A_REPORT_R1.md](../research/production_spec/stage6_deformation/stage6a/STAGE6A_REPORT_R1.md)

## 失败原因与证据边界

> 两根手指**。原因是几何性的：冻结姿态里拇指远端指骨与食指 MCP 段最小链距仅 **3.28 mm**，

出处：[STAGE6A_REPORT_R1.md](../research/production_spec/stage6_deformation/stage6a/STAGE6A_REPORT_R1.md)

> **无 FAIL case。** 无 blocker。以下为需 HR 关注的**非阻断**诊断项及其归因：

出处：[STAGE6A_REPORT_R1.md](../research/production_spec/stage6_deformation/stage6a/STAGE6A_REPORT_R1.md)

## 后续建议

> **本轮不覆盖**（留给 Stage6B / 后续）：`THUMB_CMC_R` opposition、完整 thumb opposition、

出处：[STAGE6A_REPORT_R1.md](../research/production_spec/stage6_deformation/stage6a/STAGE6A_REPORT_R1.md)

## 原报告与关键代码

- [production_spec/stage6_deformation/stage6a/STAGE6A_REPORT_R1.md](../research/production_spec/stage6_deformation/stage6a/STAGE6A_REPORT_R1.md)
- [production_spec/stage6_deformation/stage6b/STAGE6B_REPORT_R1.md](../research/production_spec/stage6_deformation/stage6b/STAGE6B_REPORT_R1.md)
- [production_spec/stage6_deformation/stage6a_r1a/STAGE6A_R1A_REPORT.md](../research/production_spec/stage6_deformation/stage6a_r1a/STAGE6A_R1A_REPORT.md)
- [production_spec/stage6_deformation/stage6a_r1b/STAGE6A_R1B_REPORT.md](../research/production_spec/stage6_deformation/stage6a_r1b/STAGE6A_R1B_REPORT.md)
- [production_spec/stage6_deformation/stage6b_r1b/STAGE6B_R1B_REPORT.md](../research/production_spec/stage6_deformation/stage6b_r1b/STAGE6B_R1B_REPORT.md)
- [production_spec/stage6_deformation/stage6b_r1c/STAGE6B_R1C_PENETRATION_ADJUDICATION_REPORT.md](../research/production_spec/stage6_deformation/stage6b_r1c/STAGE6B_R1C_PENETRATION_ADJUDICATION_REPORT.md)
- [production_spec/stage6_deformation/stage6b_r1a_seam_provenance/STAGE6B_R1A_SEAM_PROVENANCE_REPORT.md](../research/production_spec/stage6_deformation/stage6b_r1a_seam_provenance/STAGE6B_R1A_SEAM_PROVENANCE_REPORT.md)
- [production_spec/stage6_deformation/full_stage6a_requalification_r1/FULL_STAGE6A_REQUALIFICATION_R1_REPORT.md](../research/production_spec/stage6_deformation/full_stage6a_requalification_r1/FULL_STAGE6A_REQUALIFICATION_R1_REPORT.md)
- [production_spec/stage6_deformation/stage6b_r3_thumb_tip_ownership_boundary/THUMB_TIP_OWNERSHIP_BOUNDARY_R3_REPORT.md](../research/production_spec/stage6_deformation/stage6b_r3_thumb_tip_ownership_boundary/THUMB_TIP_OWNERSHIP_BOUNDARY_R3_REPORT.md)
- [production_spec/stage6_deformation/stage6b_opposition_requalification_r1/STAGE6B_OPPOSITION_REQUALIFICATION_R1_REPORT.md](../research/production_spec/stage6_deformation/stage6b_opposition_requalification_r1/STAGE6B_OPPOSITION_REQUALIFICATION_R1_REPORT.md)
- [production_spec/stage6_deformation/current_full_stage6a_crossing_human_adjudication_prep_r1/build_package.py](../../src/legacy/production_spec/stage6_deformation/current_full_stage6a_crossing_human_adjudication_prep_r1/build_package.py)
- [production_spec/stage6_deformation/current_full_stage6a_crossing_human_adjudication_prep_r1/common.py](../../src/legacy/production_spec/stage6_deformation/current_full_stage6a_crossing_human_adjudication_prep_r1/common.py)
- [production_spec/stage6_deformation/current_full_stage6a_crossing_human_adjudication_prep_r1/prepare.py](../../src/legacy/production_spec/stage6_deformation/current_full_stage6a_crossing_human_adjudication_prep_r1/prepare.py)
- [production_spec/stage6_deformation/current_full_stage6a_crossing_human_adjudication_prep_r1/render_location_only.py](../../src/legacy/production_spec/stage6_deformation/current_full_stage6a_crossing_human_adjudication_prep_r1/render_location_only.py)
- [production_spec/stage6_deformation/current_full_stage6a_crossing_human_adjudication_prep_r1/render_only.py](../../src/legacy/production_spec/stage6_deformation/current_full_stage6a_crossing_human_adjudication_prep_r1/render_only.py)
- [production_spec/stage6_deformation/current_full_stage6a_crossing_human_adjudication_prep_r1/response-validator.js](../../src/legacy/production_spec/stage6_deformation/current_full_stage6a_crossing_human_adjudication_prep_r1/response-validator.js)
- [production_spec/stage6_deformation/current_full_stage6a_crossing_human_adjudication_prep_r1/response_validator.py](../../src/legacy/production_spec/stage6_deformation/current_full_stage6a_crossing_human_adjudication_prep_r1/response_validator.py)
- [production_spec/stage6_deformation/current_full_stage6a_crossing_human_adjudication_prep_r1/verify_and_deliver.py](../../src/legacy/production_spec/stage6_deformation/current_full_stage6a_crossing_human_adjudication_prep_r1/verify_and_deliver.py)
- [production_spec/stage6_deformation/full_stage6a_requalification_after_donor_transfer_r1/common.py](../../src/legacy/production_spec/stage6_deformation/full_stage6a_requalification_after_donor_transfer_r1/common.py)
- [production_spec/stage6_deformation/full_stage6a_requalification_after_donor_transfer_r1/crossing_census.py](../../src/legacy/production_spec/stage6_deformation/full_stage6a_requalification_after_donor_transfer_r1/crossing_census.py)
- [production_spec/stage6_deformation/full_stage6a_requalification_after_donor_transfer_r1/debt_coordinate_audit.py](../../src/legacy/production_spec/stage6_deformation/full_stage6a_requalification_after_donor_transfer_r1/debt_coordinate_audit.py)
- [production_spec/stage6_deformation/full_stage6a_requalification_after_donor_transfer_r1/deliver.py](../../src/legacy/production_spec/stage6_deformation/full_stage6a_requalification_after_donor_transfer_r1/deliver.py)

## 输入、输出与大型证据

该目录原始成员 1558 项；拟公开身份记录 1450 项。
- `production_spec/stage6_deformation/full_stage6a_requalification_r1/RIGHT_HAND_FULL_STAGE6A_QUALIFICATION_HARNESS_R1.blend` → `hands-research-r1-selected-017.zip` / `payload/production_spec/stage6_deformation/full_stage6a_requalification_r1/RIGHT_HAND_FULL_STAGE6A_QUALIFICATION_HARNESS_R1.blend`
- `production_spec/stage6_deformation/stage6a/RIGHT_HAND_STAGE6A_DEFORMATION_HARNESS_R1.blend` → `hands-research-r1-selected-018.zip` / `payload/production_spec/stage6_deformation/stage6a/RIGHT_HAND_STAGE6A_DEFORMATION_HARNESS_R1.blend`
- `production_spec/stage6_deformation/stage6a_r1a/RIGHT_HAND_STAGE6A_DEFORMATION_HARNESS_R1A.blend` → `hands-research-r1-selected-018.zip` / `payload/production_spec/stage6_deformation/stage6a_r1a/RIGHT_HAND_STAGE6A_DEFORMATION_HARNESS_R1A.blend`
- `production_spec/stage6_deformation/stage6a_r1b/RIGHT_HAND_STAGE6A_DEFORMATION_HARNESS_R1B.blend` → `hands-research-r1-selected-018.zip` / `payload/production_spec/stage6_deformation/stage6a_r1b/RIGHT_HAND_STAGE6A_DEFORMATION_HARNESS_R1B.blend`
- `production_spec/stage6_deformation/stage6b/RIGHT_HAND_STAGE6B_OPPOSITION_HARNESS_R1.blend` → `hands-research-r1-selected-018.zip` / `payload/production_spec/stage6_deformation/stage6b/RIGHT_HAND_STAGE6B_OPPOSITION_HARNESS_R1.blend`
- `production_spec/stage6_deformation/stage6b_r1b/RIGHT_HAND_STAGE6B_OPPOSITION_HARNESS_R1B.blend` → `hands-research-r1-selected-018.zip` / `payload/production_spec/stage6_deformation/stage6b_r1b/RIGHT_HAND_STAGE6B_OPPOSITION_HARNESS_R1B.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
