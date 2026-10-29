# STAGE6A R1A · HUMAN APPROVAL FREEZE R1

- **round**：`STAGE5B_R1B_STAGE6A_R1A_HUMAN_APPROVAL_FREEZE_R1`
- **generated**：2026-09-30
- **mode**：DOCUMENTATION + PROVENANCE + HUMAN APPROVAL FREEZE（**非**生产修改轮）
- **声明**：本轮**未**修改任何 Blender geometry / topology / skin weight / rig。

---

## 一、Human Review 裁决

```
STAGE6A_R1A_HUMAN_REVIEW = APPROVED
```

冻结后正式状态：

```
STAGE6A_R1A                        = FINAL_APPROVED
STAGE6A_ISOLATED_FLEX_DEFORMATION  = FINAL_APPROVED
THUMB_IP_TRANSITION                = PASS
THUMB_MCP_TRANSITION               = PASS_WITH_ACCEPTED_DOCUMENTED_RESIDUAL
FOUR_FINGER_ISOLATED_FLEX          = FINAL_APPROVED
ZERO_RESTORE                       = PASS
FOREARM_STABILITY                  = PASS
NON_TARGET_DIGIT_SHAFT_CONTAMINATION = PASS
TIP_TRAJECTORY_MONOTONIC           = PASS
NAIL_DEFORMATION                   = PASS
DISTAL_CAP                         = PASS
FIRST_WEB                          = PASS
```

必须继续写：

```
DEFORMATION_FINAL        = PENDING_STAGE6B
CMC_OPPOSITION           = NOT_STARTED
COMBINED_THUMB_OPPOSITION= NOT_STARTED
STAGE6B                  = READY_TO_BEGIN      （禁止写 STARTED）
```

> **不能写** `DEFORMATION_FINAL = PASS`：Stage6B CMC opposition / combined opposition
> 尚未执行。Stage6A R1A 只批准 **isolated flex** 这一层的形变资格。

---

## 二、已批准测试工装

| 项 | 值 |
|---|---|
| 文件 | `stage6_deformation/stage6a_r1a/RIGHT_HAND_STAGE6A_DEFORMATION_HARNESS_R1A.blend` |
| SHA-256 | `c4bb74ea116e7352064c26977a509ed1248aacbe734118e5f9c240fa24b1157b` |
| 角色 | **APPROVED_STAGE6A_ISOLATED_FLEX_TEST_HARNESS** |
| 性质 | **TEST HARNESS，不是 Production Master** |
| 输入 master | `stage5b_r1b/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend`（`cec5804f…`） |
| 保存态 | ZERO / RSSF |

只读复核（`stage6a_freeze_r1a/STAGE6A_R1A_FREEZE_VERIFICATION_R1.json`）确认：
R1A 工装与历史 R1 工装的 mesh topology / UV / material / nail 归属 / 骨骼表 /
诊断相机与灯光集合**完全一致**，差异仅在于 thumb 授权区内的权重。

---

## 三、已批准数字基线（冻结）

### `TH_IP_30`

| 指标 | R1 | R1A |
|---|---|---|
| min face-area ratio | 0.054027 | **0.416085** |
| face-area p05 | 0.322227 | **0.714432** |
| min edge ratio | 0.075150 | **0.244620** |
| max edge stretch | 2.287108 | **2.034480** |
| intra-thumb pairs | 35 | **30** |

### `TH_IP_45`

| 指标 | R1 | R1A |
|---|---|---|
| min face-area ratio | 0.019443 | **0.181324** |
| face-area p05 | 0.436325 | **0.619005** |
| min edge ratio | 0.286202 | **0.445217** |
| max edge stretch | 3.127780 | **2.733736** |
| intra-thumb pairs | 51 | **42** |

### `TH_MCP_45`

| 指标 | R1 | R1A |
|---|---|---|
| min face-area ratio | 0.193672 | **0.297893** |
| face-area p05 | 0.523736 | **0.580019** |
| min edge ratio | 0.421283 | **0.219223** ⚠ |
| max edge stretch | 3.016385 | **3.016385** |
| intra-thumb pairs | 79 | **74** |

其余门：42/42 formal case、blockers **0**、
`FOUR_FINGER_REGRESSION = PASS`（36 case，位移差 **0.000e+00 mm**）、
`ZERO_RESTORE = PASS`（max 5.967e-05 mm）、
nail / distal cap area ratio 与 R1 差 **0.000e+00**、first-web drift **0.000e+00 mm**。

---

## 四、自交 authority（冻结）

| 项 | R1 | R1A |
|---|---|---|
| `INTRA_TARGET_DIGIT_PAIRS` | 279 | **259** |
| `TARGET_VS_OTHER_DIGIT` | 404 | **400** |
| pairs > 0.5 mm | 454 | **450** |

```
THUMB <-> INDEX = POSE_CONSTRAINT_DIAGNOSTIC
```

**不得**把 isolated RSSF 下的 thumb-index contact 重新归因为 skin-weight blocker；
但 Stage6B combined opposition 时**必须重新测试真实联动姿态**。

---

## 五、残余项

```
TH_MCP_45_MIN_EDGE_RESIDUAL = ACCEPTED_NON_BLOCKING_FOR_STAGE6A
min edge ratio 0.421283 -> 0.219223
```

这是在六个 thumb case 的全部记录指标中**唯一**劣于 Stage6A R1 的项。
理由与「不做 R1C」的决定见 `stage5b_freeze_r1b/STAGE5B_R1B_HUMAN_APPROVAL_FREEZE_R1.md` §六。
性质 = `ACCEPTED_DOCUMENTED_RESIDUAL`，**不是** `METRIC_INVALID`、**不是**
`GENERAL_EXCEPTION`，**不得**推广为其他关节的通用豁免。

---

## 六、方法学勘误（本轮关闭）

| 勘误 | 文件 | 要点 |
|---|---|---|
| 计数措辞 | `stage6a_r1a/STAGE6A_R1A_METRIC_COUNT_WORDING_ERRATA.md` | 正式口径 = **6 case × 5 metric families = 30 项**，其中 **29 项**非劣化、**1 项**劣化；不影响任何数值/门/结论/批准；历史 REPORT 不回改 |
| thickness proxy 权威 | `stage6a_r1a/STAGE6A_R1_THICKNESS_PROXY_AUTHORITY_ERRATA.md` | `LOCAL_THICKNESS_PROXY = DIAGNOSTIC_ONLY`；权威优先级：目视 > face-area strain > edge strain > 自交 > 局部面积/轮廓 > thickness proxy |
| 自交措辞 | `stage6a_r1a/STAGE6A_R1_SELF_INTERSECTION_WORDING_ERRATA.md` | 更正「非零 case 全部集中在 THUMB / INDEX_MCP」；MIDDLE_MCP / RING_MCP 有少量浅层 pair（非 blocker） |

---

## 七、Stage6B binding obligations（**已写入 freeze 收据，本轮不执行**）

`STAGE6A_R1A_HUMAN_APPROVAL_FREEZE_R1.json` →
`stage6b_binding_obligations.must_at_least_cover`：

```
 1 THUMB_CMC isolated opposition
 2 CMC + MCP combined opposition
 3 CMC + MCP + IP combined opposition
 4 first-web opening / closing deformation
 5 thenar volume preservation
 6 thumb distal-cap stability
 7 thumb nail deformation
 8 thumb-index contact progression
 9 pinching
10 collapse
11 candy-wrapper
12 skin inversion
13 cross-digit contamination
14 tip trajectory / target reach
15 restore-to-RSSF
```

Stage6B 功能 authority = **真正的 thumb opposition / teaching hand function**；
**不得**由 Stage6A isolated flex 自动替代。

---

## 八、停止点

```
STAGE6B = READY_TO_BEGIN      （禁止写 STARTED）
```

完成 freeze / errata / hash verification / provenance ledger / Stage6B binding obligations 后
**立即 STOP**，不开始 Stage6B，等待 Human Review / 下一步指令。

---

## 九、状态汇总

```
STAGE6A_R1A                       = FINAL_APPROVED
STAGE6A_ISOLATED_FLEX_DEFORMATION = FINAL_APPROVED
THUMB_IP_TRANSITION               = PASS
THUMB_MCP_TRANSITION              = PASS_WITH_ACCEPTED_DOCUMENTED_RESIDUAL
DEFORMATION_FINAL                 = PENDING_STAGE6B
STAGE6B                           = READY_TO_BEGIN
PRODUCTION_MASTER_GEOMETRY        = UNCHANGED
PRODUCTION_RIG_SKELETON           = UNCHANGED
```
