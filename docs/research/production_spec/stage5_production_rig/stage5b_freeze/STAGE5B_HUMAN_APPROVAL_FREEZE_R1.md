# STAGE5B_HUMAN_APPROVAL_FREEZE_R1

**Human Review 裁决** `APPROVED`
**本轮性质**：**纯文档 / provenance / freeze**。未创建任何新 blend、未创建 R1B / R1C / R2、
未修改任何权重、未修改 vertex group / parent / Armature modifier / bone / joint / roll /
mesh / topology / UV / material / nail face。未做 pose / animation / GLB / Three.js / Stage6。

---

## 零、最终状态

```
STAGE5B                          = FINAL_APPROVED
STAGE5B_R1A                      = APPROVED_STAGE5B_STATIC_SKIN_MASTER
PRODUCTION_BINDING               = FINAL_APPROVED
PRODUCTION_SKIN_WEIGHT_STATIC    = FINAL_APPROVED
STAGE5B_FREEZE                   = PASS
STAGE6                           = READY_TO_BEGIN
```

> 只能写 `STAGE6 = READY_TO_BEGIN`，**不得**写 `STARTED`。

---

## 一、唯一 Active Stage5B Master（冻结）

| 项 | 值 |
| --- | --- |
| 路径 | `production_spec/stage5_production_rig/stage5b_r1a/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1A.blend` |
| **SHA-256** | **`c68e415aff80b56911cfe5646e47dff9100d7b54b8bf7aa8ba068bb3948c0ea6`** |
| bytes | 2,293,759 |
| mesh 对象 | `Hand  - Realistic`（两个空格） |
| rig 对象 | `RIGHT_HAND_PRODUCTION_RIG` |
| parent | `RIGHT_HAND_PRODUCTION_RIG` |
| Armature modifier | `PRODUCTION_ARMATURE` → `RIGHT_HAND_PRODUCTION_RIG` |
| deform vertex groups | **16** |
| TIP helper（`use_deform = false`） | **5**，且**无任何 deform 权重** |
| PRODUCTION_BONE_COUNT | **21** |

---

## 二、Human Review 正式通过项

| Gate | 裁决 |
| --- | --- |
| PRODUCTION_BINDING | **APPROVED** |
| FOUR_FINGER_SKIN_WEIGHT | **APPROVED** |
| WRIST_WEIGHT | **APPROVED** |
| THUMB_CHAIN_WEIGHTING | **APPROVED** |
| THUMB_CMC_THENAR_LOCALITY | **APPROVED** |
| THUMB_MCP_LOCALITY | **APPROVED** |
| THUMB_IP_DISTAL_LOCALITY | **APPROVED** |
| FIRST_WEB_WEIGHTING | **APPROVED** |
| NAIL_WEIGHT_OWNERSHIP | **APPROVED** |
| **PRODUCTION_SKIN_WEIGHT_STATIC** | **APPROVED** |

`STAGE5B_R1A_HUMAN_REVIEW = APPROVED`；`Stage6 dynamic deformation` **尚未开始**。

---

## 三、冻结的 weighting method

### 3.1 Thumb 纵向权威

```
GLOBAL_THUMB_LONGITUDINAL_COORDINATE = APPROVED_JOINT_POLYLINE_ARC_LENGTH
joint chain                          = CMC → MCP → IP → TIP
XIJ (mm) = [0.0(CMC head), 42.6796(MCP joint), 71.8815(IP joint), 93.9454(TIP landmark)]
FORBIDDEN = GLOBAL_SURFACE_GEODESIC_FROM_DISTAL_TIP
（详见 STAGE5B_R1A_GEODESIC_LONGITUDINAL_METHOD_ERRATA.md）
```

判据与派生常量（全部由网格/已批准数据导出，无手选常数）：

```
τ            = 1 × 网格中位边长 = 3.8882 mm      （joint-local transition 半宽）
R_TT         = 9.44 mm                            （近节指骨带内到拇指链横向距离 p25 ⇒ 管半径）
R_MAX        = 29.87 mm                           （掌骨/根部带 p95）
R_TUBE       = R_TT + τ = 13.33 mm
单位分解（沿弧长，Σ = 1 且各项 ≥ 0）：
  W_IP   = 1 − t_IP
  W_MCP  = t_IP − t_MCP
  W_CMC  = (1 − t_MCP) · f_tube(d)
  W_WRIST= (1 − t_MCP) · (1 − f_tube(d))
  f_tube(d) = 1 − S((d − R_TT)/(R_MAX − R_TT))     （仅作径向分工，非纵向依据）
```

### 3.2 Thumb 语义区域（7 区域，全部冻结）

| 区域 | 顶点数 | 允许骨 | 期望主导 |
| --- | --- | --- | --- |
| `THUMB_DISTAL` | 161 | IP / MCP | **THUMB_IP_R** |
| `THUMB_PROXIMAL` | 107 | MCP / IP / CMC | **THUMB_MCP_R** |
| `THUMB_FIRST_METACARPAL` | 153 | CMC / MCP / WRIST | **THUMB_CMC_R** |
| `THUMB_BASE_FOLD` | 37 | WRIST / CMC / MCP / INDEX_MCP | MCP（近节层面折返带） |
| `THENAR_BASE` | 287 | WRIST / CMC / MCP | **WRIST_R + THUMB_CMC_R** |
| `FIRST_WEB` | 21 | WRIST / CMC / MCP / INDEX_MCP | 四者，**THUMB_IP_R ≡ 0** |
| `CENTRAL_PALM` | 1199 | WRIST | WRIST（**不修改**） |

区域顶点集合权威：`stage5b_r1a/THUMB_SEMANTIC_REGION_AUDIT.json`
（本轮已独立重算比对，7/7 区域顶点集合完全相同）。

`AUTHORISED_MODIFICATION_SET = 703`；`CHANGED_VERTICES = 696`。

### 3.3 冻结的关键 gate 值

```
FIRST_WEB_THUMB_IP_WEIGHT        = 0                 （精确 0.000000；R1 为 14.000000）
THUMB_NAIL                       = 22 / 22 THUMB_IP dominant
FOUR_FINGER_NAIL                 = 100 % corresponding DIP dominant
UNAUTHORIZED_CHANGED_VERTICES    = 0
FROZEN_FOUR_FINGER_GROUP_DRIFT   = 0                 （11 组 × 3416 顶点逐位相同）
CROSS_DIGIT_LEAKAGE              = PASS_WITH_DOCUMENTED_CARRY_OVER_RESIDUE
THUMB_CHAIN_DOMINANCE_BY_REGION  = PASS              （全部区域 unexpected dominant = 0）
```

---

## 四、R1A static integrity freeze（本轮只读复核）

| 项 | 值 | 判定 |
| --- | --- | --- |
| V / E / F / TRIS | **3416 / 6828 / 3414 / 6828** | PASS |
| Topology delta vs master | **0** | PASS |
| UV delta | **0** | PASS |
| Material assignment delta | **0** | PASS |
| Nail-face assignment delta | **0** | PASS |
| deform vertex groups | **16** | PASS |
| TIP helpers（`use_deform = false`） | **5**，deform 权重 = **0** | PASS |
| MAX_INFLUENCES | **4**（分布 1:951 ｜ 2:244 ｜ 3:51 ｜ 4:2170 ｜ >4:0） | PASS |
| UNWEIGHTED_VERTICES | **0** | PASS |
| WEIGHT_NORMALIZATION | **PASS**（最坏误差 4.4005e-08） | PASS |
| ZERO_POSE_BIND | **PASS** | PASS |
| world transform delta vs master | **0.0 mm** | PASS |
| parent / modifier 结构 | `RIGHT_HAND_PRODUCTION_RIG` / `PRODUCTION_ARMATURE`（ARMATURE） | PASS |

---

## 五、Zero-pose frozen values

```
max evaluated vertex delta  = 5.967e-05 mm
mean evaluated vertex delta = 5.893e-06 mm
bbox delta                  <= 7.451e-06 mm
base mesh vertex delta      = 0
parent world delta          = 0
```

以上统一定义为 **FLOAT_EQUIVALENT_ZERO**（分类冻结）。

> 复核备注：本轮只读重算复现 **max = 5.967e-05 mm** 与 **bbox = [0, 7.451e-06, 0, 0, 0, 0] mm**、
> base mesh delta = 0、parent world delta = 0（完全一致）；mean 在同一量级复现为 5.649e-06 mm
> （与 R1A 审计值 5.893e-06 mm 的差异来自 depsgraph 求值次序，二者同属 float32 噪声级）。
> **R1A 审计值（mean 5.893e-06 mm）保持为冻结权威值**，本备注不改变分类。

---

## 六、Stage5B provenance chain

```
Stage5B R1  = SUPERSEDED_FOR_THUMB_WEIGHTING        （保留 provenance，不删除）
  RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1.blend
  8f4c6901fdae417e3855d388f9739ebea10863f0ebdbfedf0df8d79a751c308d
  HR 裁决 REQUEST_CHANGES_NARROW → THUMB_CHAIN_WEIGHTING / FIRST_WEB_WEIGHTING = FAIL
  R1 仍为 PRODUCTION_BINDING / ZERO_POSE_BIND / FOUR_FINGER_INITIAL_WEIGHT 的历史证据

Stage5B R1A = APPROVED_STAGE5B_STATIC_SKIN_MASTER   （唯一 Active Stage5B Master）
  RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1A.blend
  c68e415aff80b56911cfe5646e47dff9100d7b54b8bf7aa8ba068bb3948c0ea6
```

**本轮未创建 R1B / R1C / R2，未另存任何新的模型 revision。**

---

## 七、Stage5B approval 的语义边界

```
STAGE5B_APPROVAL = STATIC_SKIN_WEIGHT_APPROVAL
                 ≠ FINAL_DEFORMATION_APPROVAL
```

本冻结只声明**静态蒙皮权重**通过。**动态形变质量尚未验证**，
全部动态判定权在 Stage6。任何“权重已批准”的表述**不得**被解释为
“形变已批准”或“可直接上线”。

---

## 八、Stage6 binding obligations（15 项必测）

```
 1. THUMB CMC oppose
 2. THUMB MCP flex
 3. THUMB IP flex
 4. CMC + MCP + IP combined opposition
 5. first web deformation
 6. thenar volume preservation
 7. thumb distal volume preservation
 8. thumb fingertip stability
 9. nail / distal-cap distortion
10. pinching
11. collapse
12. candy-wrapper
13. skin inversion
14. cross-digit contamination
15. four-finger MCP / PIP / DIP flexion
```

### 8.1 Stage5A thumb distal exception 继续 binding

```
THUMB_IP_TO_TIP_STRAIGHT_CHORD_CONTAINMENT = DIAGNOSTIC_ONLY
```

Stage6 **不得**因为 debug bone chord 局部穿出 soft-tissue mesh 而自动判 deform FAIL；
Stage6 应判**实际 skin deformation quality**。
（适用范围仅 `THUMB_IP_R → THUMB_TIP_R`；四指 distal containment gate 继续有效。）

### 8.2 Stage6 若 FAIL 的诊断顺序（不得越级）

```
Stage6 若出现问题：
  不得直接移动 frozen bone。
  优先诊断顺序：
    1. skin weight
    2. weight transition
    3. first-web / thenar ownership
    4. CMC cage consumption
    5. rig local-axis mechanics
    6. 必要时 topology
  任何 joint position / bone count / rig architecture 重开都必须 Human Review。
```

---

## 九、登记在案的 provenance 记录（非阻断）

| 记录 | 状态 | 文档 |
| --- | --- | --- |
| `VERTEX_2189_CARRY_OVER_RESIDUE`（`INDEX_PIP_R = 2.4507e-04`，R1 继承，before == after） | `ACCEPTED_NON_BLOCKING_PROVENANCE`（**不是** PASS AS DESIGNED，**不是** GENERAL EXCEPTION；`DO_NOT_PROPAGATE_AS_GENERAL_EXCEPTION`；未来整套重生成时 `SHOULD_BE_CLEANED`） | `stage5b_r1a/STAGE5B_R1A_VERTEX2189_CARRY_OVER_ERRATA.md` |
| `THUMB_CMC locality` 数值口径矛盾（REPORT 散文 “1.0” vs STATUS `0.925204`） | 已关闭：权威度量为 **A = 339/907 = 0.373760**（eps=1e-8）、**B = 225.194429/243.399683 = 0.925204**；REPORT 的 “1.0” 判定为 **STALE_WORDING（无背书）** | `stage5b_r1a/STAGE5B_R1A_CMC_LOCALITY_NUMERIC_ERRATA.md` |
| 全局测地纵向坐标不可用 | 已关闭：`GLOBAL_THUMB_LONGITUDINAL_COORDINATE = APPROVED_JOINT_POLYLINE_ARC_LENGTH`；`LOCAL_DISTAL_CAP_GEODESIC_9MM = REMAINS_APPROVED` | `stage5b_r1a/STAGE5B_R1A_GEODESIC_LONGITUDINAL_METHOD_ERRATA.md` |

**上述记录均不重开任何已批准 gate，不构成 FAIL CLOSED。**

---

## 十、冻结 hash before / after

| 文件 | SHA-256 | before = after |
| --- | --- | --- |
| Stage5A master `RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend` | `c4fafc56c591411bb5ddf07bde44b5fcd6e6a9aa5e0d43b22f9734c0884c2845` | ✅ |
| Stage5B R1 `RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1.blend` | `8f4c6901fdae417e3855d388f9739ebea10863f0ebdbfedf0df8d79a751c308d` | ✅ |
| Stage5B R1A `RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1A.blend` | `c68e415aff80b56911cfe5646e47dff9100d7b54b8bf7aa8ba068bb3948c0ea6` | ✅ |

全部 **before = after**；本轮**未修改任何 blend**。
只读复核证据：`stage5b_freeze/STAGE5B_FREEZE_VERIFICATION_R1.json`。

---

## 十一、产物清单

```
stage5b_freeze/STAGE5B_HUMAN_APPROVAL_FREEZE_R1.md              （本文件）
stage5b_freeze/STAGE5B_HUMAN_APPROVAL_FREEZE_R1.json
stage5b_freeze/STAGE5B_FREEZE_VERIFICATION_R1.json              （只读复核证据）
stage5b_r1a/STAGE5B_R1A_CMC_LOCALITY_NUMERIC_ERRATA.md
stage5b_r1a/STAGE5B_R1A_CMC_LOCALITY_NUMERIC_RECOMPUTE.json
stage5b_r1a/STAGE5B_R1A_VERTEX2189_CARRY_OVER_ERRATA.md
stage5b_r1a/STAGE5B_R1A_GEODESIC_LONGITUDINAL_METHOD_ERRATA.md
```

---

## 十二、停止点

本轮**未开始 Stage6**，未创建任何新 blend revision，未修改任何权重。
`STAGE6 = READY_TO_BEGIN` 仅为就绪声明。等待下一步指令。
