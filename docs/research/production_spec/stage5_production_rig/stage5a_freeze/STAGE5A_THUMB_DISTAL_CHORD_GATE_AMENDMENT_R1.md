# STAGE5A_THUMB_DISTAL_CHORD_GATE_AMENDMENT_R1

**性质**：正式 Gate 修订（amendment）。**不修改任何 blend、几何、骨骼、roll。**
**依据**：`STAGE5A_R2B_HUMAN_REVIEW = ACCEPT_STRUCTURAL_NO_SOLUTION`。

---

## 一、修订对象

```
旧 Gate
  THUMB_IP_TO_TIP_INTERIOR =
    straight segment must remain 20/20 AND 40/40 inside mesh
    （硬性 Production Rig Gate）

新 Gate
  THUMB_IP_TO_TIP_STRAIGHT_CHORD_CONTAINMENT =
    DIAGNOSTIC_ONLY
```

**适用范围严格限定为 THUMB distal segment：**

```
THUMB_IP_R  →  THUMB_TIP_R
```

## 二、修订原因

R2B 已证明：在批准 THUMB_IP T-01 joint region
（axial centre **65.986 mm**、zone **±8.653 mm** = **[57.333, 74.639] mm**）内，
不存在能同时令 MCP→IP 与 IP→TIP 两段 straight chord 都达到严格 full-containment 的
Production THUMB_IP joint centre：

| 项 | 值 |
| --- | --- |
| inside + THUMB-owned candidates | 501 |
| clearance ≥ 3 mm | 259 |
| **strict feasible（20 与 40 sample 全内部）** | **0** |
| 扩展诊断带 axial 35–100 mm 内同时 40/40 的位置 | **NONE** |

继续移动 `THUMB_IP_R` 会破坏：已批准 T-01 joint authority、joint scientific semantics、
以及当前已通过的 MCP→IP chain。故 `THUMB_IP_R = KEEP`。

## 三、本 Amendment 不得扩大

```
正确写法：THUMB_DISTAL_STRAIGHT_CHORD_EXCEPTION_ONLY
禁止写法：ALL_BONES_FULL_CONTAINMENT = DIAGNOSTIC_ONLY
```

**不修改** INDEX / MIDDLE / RING / LITTLE 的 distal segment containment Gate。
四指当前可以达到 full containment，其原 Gate **继续有效**（四指 DIP→TIP 均为 20/20、40/40）。

## 四、科学语义正式区分（binding）

```
SCIENTIFIC_JOINT_PLACEMENT
  !=
STRAIGHT_BONE_DISPLAY_GEOMETRY_FULLY_INSIDE_SOFT_TISSUE
```

Production bone 是 **KINEMATIC CONTROL AXIS**，不是：
实体骨骼体积 / 软组织中心线实体 / 必须完整包含在 skin volume 中的刚性圆柱。

因此，只要下列全部 PASS：

- `THUMB_IP` joint authority（T-01 zone）= PASS
- `THUMB_TIP` distal-cap authority = PASS
- thumb chain hierarchy = PASS
- local frame / roll = PASS
- **后续实际 deformation（Stage6）= PASS**

则 straight chord 在高度弯曲的 RSSF soft-tissue mesh 中局部穿出，
**不自动等于 joint placement FAIL**。

## 五、Final Gate 状态措辞（禁止 PASS / WAIVED）

```
THUMB_IP_TO_TIP_STRAIGHT_CHORD_CONTAINMENT =
  STRUCTURALLY_INCOMPATIBLE_WITH_CURRENT_MESH_AND_21_BONE_ABSTRACTION

GATE_CLASSIFICATION =
  DIAGNOSTIC_ONLY_AFTER_R2B_FEASIBILITY_PROOF
```

**保留实际数据（不得删除）：**

| 对象 | MCP→IP (strict) | IP→TIP (strict) |
| --- | --- | --- |
| **R2A 当前 IP**（KEEP） | **40/40** | **31/40** |
| zone 内 best | 40/40 | 36/40 |
| IP→TIP 单项 40/40 candidate | 20/40 | 40/40 |
| **full simultaneous 40/40** | — | **NONE** |

## 六、Stage6 成为最终功能权威

Thumb distal 的最终功能验收转移到：

```
STAGE6_DEFORM_TEST_THUMB_FLEX
STAGE6_DEFORM_TEST_THUMB_OPPOSE
```

Stage6 **至少**必须检查：

- THUMB_IP flexion deformation
- distal phalanx volume preservation
- fingertip positional stability
- nail / distal-cap distortion
- pinching
- collapse
- candy-wrapper distortion
- abnormal skin inversion
- web-space contamination
- thenar contamination
- CMC / MCP / IP combined opposition deformation

> **如果 Stage6 FAIL，不得引用本 Amendment 掩盖变形问题。**
> 必须回到 Skin Weight / Rig mechanics / 或必要时 topology 重新诊断。

## 七、未变更项（本 Amendment 之外）

- 21 bones per hand（不变）；5 个 TIP helper `use_deform = false`（不变）
- 不增加新的 deform helper bone
- `THUMB_CMC_R` / `THUMB_MCP_R` / `THUMB_IP_R` / `THUMB_TIP_R` / `WRIST_R` / `INDEX_MCP_R` 全部 KEEP
- Mesh / topology / CMC cage / RSSF / nails / UV / roll 均未改动

---

**关联文件**
- 依据：`stage5a_r2b/STAGE5A_R2B_REPORT.md`、`stage5a_r2b/THUMB_STRAIGHT_BONE_COMPATIBILITY_DIAGNOSIS.json`
- 措辞勘误：`stage5a_r2b/STAGE5A_R2B_STRUCTURAL_DIAGNOSIS_WORDING_ERRATA.md`
- 口径勘误：`stage5a_r2b/STAGE5A_R2B_FEASIBILITY_ZONE_CLASSIFICATION_ERRATA.md`
- 冻结回执：`stage5a_freeze/STAGE5A_HUMAN_APPROVAL_FREEZE_R1.md` / `.json`
