# STAGE5A_HUMAN_APPROVAL_FREEZE_R1

**Human Review 裁决** `ACCEPT_STRUCTURAL_NO_SOLUTION`
**本轮性质**：READ-ONLY 收口。未创建任何新 blend、未创建 R2B blend、未做任何几何或骨架修改。

---

## 零、最终状态

```
STAGE5A                             = FINAL_APPROVED
STAGE5A_PRODUCTION_RIG_SKELETON     = FINAL_APPROVED
STAGE5A_MASTER                      = RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend
STAGE5A_FREEZE                      = PASS
STAGE5B                             = READY_TO_BEGIN
```

> 只能写 `STAGE5B = READY_TO_BEGIN`，**不得**写 `STARTED`。

## 一、Active Production Rig Master（冻结）

| 项 | 值 |
| --- | --- |
| 路径 | `production_spec/stage5_production_rig/stage5a_r2a/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend` |
| **SHA-256** | **`c4fafc56c591411bb5ddf07bde44b5fcd6e6a9aa5e0d43b22f9734c0884c2845`** |
| Production Rig 对象 | `RIGHT_HAND_PRODUCTION_RIG` |
| **PRODUCTION_BONE_COUNT** | **21** |
| TIP helper（`use_deform = false`） | 5 → `INDEX_TIP_R / MIDDLE_TIP_R / RING_TIP_R / LITTLE_TIP_R / THUMB_TIP_R` |
| deform bones（`use_deform = true`） | 16 |
| Production Skin Weight | **NOT_STARTED** |
| 新增 helper deform bone | **无**（严格 21 bone 抽象） |

## 二、关键位置（冻结，实测 delta = 0.0 mm）

| Joint / landmark | Status | World position |
| --- | --- | --- |
| **PRODUCTION_WRIST_R**（= 骨骼 `WRIST_R`，与 asset origin 解耦） | **APPROVED** | `[1.406007767, 0.016420959, 0.358511657]` |
| **THUMB_CMC_R** | **APPROVED** | `[1.440895081, 0.001219887, 0.3918145]` |
| **THUMB_MCP_R** | **APPROVED** | `[1.454060912, 0.001536574, 0.436873049]` |
| **THUMB_IP_R** | **APPROVED** | `[1.450860858, 0.006127121, 0.464001149]` |
| **THUMB_TIP_R** | **APPROVED_AS_STABLE_DISTAL_CAP_SURFACE_LANDMARK** | `[1.45281744, 0.019802358, 0.493028343]` |
| **INDEX_MCP_R** | **APPROVED** | `[1.442374706, 0.017366245, 0.483602315]` |
| 其余全部 joint | **CARRY_FORWARD_APPROVED** | 0 drift |

`PRODUCTION_WRIST_R` 是与 ASSET object origin **解耦**的腕关节中心（分离 23.593 mm）；
rig 中实际骨骼名为 `WRIST_R`。

## 三、科学语义（binding）

```
SCIENTIFIC_JOINT_PLACEMENT
  !=
STRAIGHT_BONE_DISPLAY_GEOMETRY_FULLY_INSIDE_SOFT_TISSUE
```

Production bone 是 **KINEMATIC CONTROL AXIS**，不是实体骨骼体积 / 软组织中心线实体 /
必须完整包含在 skin volume 中的刚性圆柱。
因此：只要 IP joint authority、TIP distal-cap authority、chain hierarchy、local frame/roll、
以及**后续实际 deformation（Stage6）** 全部 PASS，
则 straight chord 在高度弯曲 RSSF soft-tissue mesh 中局部穿出，**不自动等于 joint placement FAIL**。

## 四、THUMB distal exception 最终状态

```
THUMB_DISTAL_STRAIGHT_CHORD_EXCEPTION_ONLY

THUMB_IP_TO_TIP_STRAIGHT_CHORD_CONTAINMENT =
  STRUCTURALLY_INCOMPATIBLE_WITH_CURRENT_MESH_AND_21_BONE_ABSTRACTION
GATE_CLASSIFICATION =
  DIAGNOSTIC_ONLY_AFTER_R2B_FEASIBILITY_PROOF
```

**不是 PASS，不是 WAIVED。** 保留实测数据：

| 对象 | MCP→IP (strict) | IP→TIP (strict) |
| --- | --- | --- |
| R2A 当前 IP（KEEP） | 40/40 | **31/40** |
| zone 内 best | 40/40 | 36/40 |
| IP→TIP 单项 40/40 candidate | 20/40 | 40/40 |
| **full simultaneous 40/40** | — | **NONE** |

**适用范围**：仅 `THUMB_IP_R → THUMB_TIP_R`。
INDEX / MIDDLE / RING / LITTLE 的 distal containment Gate **继续有效**（四指 20/20、40/40）。
详见 `STAGE5A_THUMB_DISTAL_CHORD_GATE_AMENDMENT_R1.md`。

## 五、Distal-cap method authority（保持不变）

```
CANONICAL_DISTAL_CAP_METHOD =
  GEODESIC_CONNECTED_CAP_FROM_DISTAL_MOST_SURFACE_REGION
  D* → mesh geodesic → connected digit-owned cap → 9.0 mm calibrated radius
  → area-weighted centroid projected to surface → geodesic 1-median cross-check

早期 "fitted medial distal axis + 0.5 mm slab transition" =
  SUPERSEDED_DIAGNOSTIC_METHOD
```
勘误：`stage5a_r2a/../stage5a_r2b/STAGE5A_R2A_DISTAL_CAP_METHOD_ERRATA.md`（不再修改）。

## 六、Stage6 binding deformation tests

```
STAGE6_DEFORM_TEST_THUMB_FLEX
STAGE6_DEFORM_TEST_THUMB_OPPOSE
```
至少检查：THUMB_IP flexion deformation / distal phalanx volume preservation /
fingertip positional stability / nail & distal-cap distortion / pinching / collapse /
candy-wrapper distortion / abnormal skin inversion / web-space contamination /
thenar contamination / CMC·MCP·IP combined opposition deformation。

> **Stage6 若 FAIL，不得引用本次 exception 掩盖变形问题**；
> 必须回到 Skin Weight / Rig mechanics / 或必要时 topology 重新诊断。

```
CMC_DEFORMATION_FINAL = PENDING_STAGE6
```

## 七、历史 provenance

```
STAGE5A_R1  = FAIL_CLOSED_PROVENANCE_ONLY
STAGE5A_R1_OBJECT_FRAME_OFFSET = CLOSED_BY_R2_SUPERSESSION   （偏移 1448.359 mm）
  → R1 不得作为 executable rig
STAGE5A_R2  = SUPERSEDED_BY_R2A_FOR_THUMB_TIP
STAGE5A_R2A = APPROVED_PRODUCTION_RIG_SKELETON_MASTER
STAGE5A_R2B = READ_ONLY_FEASIBILITY_DIAGNOSIS / NO_NEW_BLEND
```

## 八、冻结完整性检查（before = after）

| 输入 | SHA-256 |
| --- | --- |
| Stage4C master | `fde620b2cebd2b4cd894e32b58d7b59ba7fac9b00d3d2dfa5193cefb32513ab7` |
| Stage5A R1 | `dd5f7265ea373579e9f77ecea2f74f0b2d0642a2bbb10795f1ddf5c17eb1486d` |
| Stage5A R2 | `615367d7fab3e75431fa7171e7e82f3a655c62e29ad7ddca5509b093e9f68c81` |
| Stage5A R2A | `c4fafc56c591411bb5ddf07bde44b5fcd6e6a9aa5e0d43b22f9734c0884c2845` |

全部 **before = after**（已逐项复核）。

**实测完整性**（read-only 校验，见 `STAGE5A_FREEZE_VERIFICATION_R1.json`）：

```
Mesh vertex delta vs Stage4C master = 9.31e-07 mm   (float32-equivalent 0)
Topology delta                      = 0
UV delta                            = 0
Material assignment delta           = 0
No new blend / No new bone / No joint move / No roll change
BONE_LOCAL_FRAME_ORTHONORMAL        = PASS   (max err 3.69e-07)
BONE_ROLL_180_FLIPS                 = 0
THUMB_CHAIN_ROLL_CONTINUITY         = PASS   (thumb: 47.21 / 7.55 / 18.44 / 0.01 deg)
Mesh parent = None ; modifiers = [] ; vertex groups = []
Rig object  = ASSET origin, identity rotation, scale 1
```

## 九、产物清单

```
stage5a_freeze/STAGE5A_HUMAN_APPROVAL_FREEZE_R1.md          （本文件）
stage5a_freeze/STAGE5A_HUMAN_APPROVAL_FREEZE_R1.json
stage5a_freeze/STAGE5A_THUMB_DISTAL_CHORD_GATE_AMENDMENT_R1.md
stage5a_freeze/STAGE5A_FREEZE_VERIFICATION_R1.json          （read-only 校验证据）
stage5a_r2b/STAGE5A_R2B_STRUCTURAL_DIAGNOSIS_WORDING_ERRATA.md
stage5a_r2b/STAGE5A_R2B_FEASIBILITY_ZONE_CLASSIFICATION_ERRATA.md
stage5a_r2b/STAGE5A_R2A_DISTAL_CAP_METHOD_ERRATA.md
```

## 十、停止点

本轮**未开始 Stage5B**。`STAGE5B = READY_TO_BEGIN` 仅为就绪声明。
等待下一步指令。
