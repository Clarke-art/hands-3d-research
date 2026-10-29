# STAGE5B R1B · HUMAN APPROVAL FREEZE R1

- **round**：`STAGE5B_R1B_STAGE6A_R1A_HUMAN_APPROVAL_FREEZE_R1`
- **generated**：2026-09-30
- **mode**：DOCUMENTATION + PROVENANCE + HUMAN APPROVAL FREEZE（**非**生产修改轮）
- **声明**：本轮**未**修改任何 Blender geometry / topology / skin weight / rig。
  所有核验均为只读；唯一写入发生在 `_tmp/` 与两个 freeze 目录。

---

## 一、Human Review 裁决

```
STAGE5B_R1B_HUMAN_REVIEW = APPROVED
STAGE6A_R1A_HUMAN_REVIEW = APPROVED
```

正式接受：

| 项 | 状态 |
|---|---|
| `THUMB_IP_TRANSITION` | **PASS** |
| `THUMB_MCP_TRANSITION` | **PASS_WITH_ACCEPTED_DOCUMENTED_RESIDUAL** |
| `TH_MCP_45_MIN_EDGE_RESIDUAL` | **ACCEPTED_NON_BLOCKING_FOR_STAGE6A** |
| `FOUR_FINGER_REGRESSION` | PASS |
| `ZERO_RESTORE` | PASS |
| `NAIL_DEFORMATION` | PASS |
| `DISTAL_CAP` | PASS |
| `FIRST_WEB` | PASS |

> 本轮仅批准 **STAGE6A_ISOLATED_FLEX_DEFORMATION**。
> **不得**写 `DEFORMATION_FINAL = PASS` —— 因为 Stage6B CMC opposition /
> combined opposition 尚未执行。`DEFORMATION_FINAL = PENDING_STAGE6B`。

---

## 二、冻结状态（本轮生效）

```
STAGE5B_R1B                    = FINAL_APPROVED
PRODUCTION_BINDING             = FINAL_APPROVED
PRODUCTION_SKIN_WEIGHT_STATIC  = FINAL_APPROVED
STAGE5B_MASTER                 = RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend
STAGE5B_FREEZE_R1B             = PASS
STAGE5B_R1A                    = SUPERSEDED_BY_R1B_FOR_THUMB_WEIGHTING
                                 （历史文件与报告全部保留，未覆盖/删除/回改）
```

---

## 三、唯一有效 Stage5B master

| 角色 | 文件 | SHA-256 |
|---|---|---|
| **APPROVED_STAGE5B_STATIC_SKIN_MASTER** | `stage5b_r1b/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend` | `cec5804f1319bf2408fded21a3d0cf8c9f01bf778ae0659c18cf17950b117d10` |

---

## 四、只读完整性复核（写 freeze 收据之前执行）

核验脚本：`stage5b_freeze_r1b/scripts/s5b_r1b_freeze_verify.py`（只读）
结果文件：`stage5b_freeze_r1b/STAGE5B_R1B_FREEZE_VERIFICATION_R1.json`

### 4.1 五个关键 blend：before / after 哈希

| blend | sha256（before） | after | 一致 |
|---|---|---|---|
| Stage5A skeleton master | `c4fafc56c591411bb5ddf07bde44b5fcd6e6a9aa5e0d43b22f9734c0884c2845` | 同 | ✅ |
| Stage5B R1A master | `c68e415aff80b56911cfe5646e47dff9100d7b54b8bf7aa8ba068bb3948c0ea6` | 同 | ✅ |
| **Stage5B R1B master** | `cec5804f1319bf2408fded21a3d0cf8c9f01bf778ae0659c18cf17950b117d10` | 同 | ✅ |
| Stage6A R1 harness | `8f223c979362a8c3414b58e2467c7cda2da60f993245cc95b2a38d76c718d3ef` | 同 | ✅ |
| Stage6A R1A harness | `c4bb74ea116e7352064c26977a509ed1248aacbe734118e5f9c240fa24b1157b` | 同 | ✅ |

**五个文件在执行前后均未变化。**

### 4.2 五个 blend 的结构一致性（对照冻结 Stage5A R2A 参考）

全部 blend 一致且与参考相同：

| 检查 | 五个 blend 结果 |
|---|---|
| vertex count | 3416 |
| edge count | 6828 |
| face count | 3414 |
| tri count | 6828 |
| UV unchanged | true |
| material unchanged | true |
| nail face assignment unchanged（124 面，集合哈希一致） | true |
| bone count = 21 | true |
| deform bones = 16 | true |
| TIP helper = 5（`{THUMB,INDEX,MIDDLE,RING,LITTLE}_TIP_R`） | true |
| hierarchy unchanged | true |
| bone head / tail / roll（`matrix_local` 全量） unchanged | true |
| object origin unchanged | true |
| object matrix（含 scale） unchanged | true |
| RSSF bind pose（zero-pose 评测残差） | R1A/R1B/R1/R1A-harness = 5.967e-05 mm；R2A = 0.000000000 mm |

### 4.3 R1B 权重再核验

由冻结 R1A master + 已记录参数**独立重新推导**候选权重场，再与**已签发 R1B** 逐组逐顶点比较：

| 项 | 值 |
|---|---|
| authorised region | **323** |
| changed vertices | **319** |
| authorised-but-unchanged | 4 |
| 实际被改动的组 | `WRIST_R`、`THUMB_CMC_R`、`THUMB_MCP_R`、`THUMB_IP_R`（**仅此 4 组**） |
| `FOUR_FINGER_GROUP_DRIFT` | **0.0** |
| `FIRST_WEB_DRIFT` | **0.0** |
| `NAIL_DRIFT` | **0.0** |
| `DISTAL_CAP_DRIFT` | **0.0** |
| `OUTSIDE_AUTHORISED_DRIFT` | **0.0** |
| 候选场 vs 落盘 R1B（float32）不一致数 | **0** |
| `MAX_INFLUENCES` | 4（≤ 4 ✅） |
| `NORMALIZATION` | **PASS** |
| `ZERO_POSE_BIND` | **PASS** |
| 权重是否被重新调整 | **否** |

---

## 五、拇指权重 authority（冻结，不需重新研究）

```
GLOBAL_LONGITUDINAL_COORDINATE = APPROVED_JOINT_POLYLINE_ARC_LENGTH
transition form                = JOINT_CENTERED
profile                        = QUINTIC
W_IP  = 5.0 * MED      (half width 19.441 mm, full span 38.882 mm)
W_MCP = 1.0 * MED
W_BASE = 3.0 * MED
MED   = 3.888205 mm

GLOBAL_SURFACE_GEODESIC_FROM_DISTAL_TIP = FORBIDDEN_FOR_LONGITUDINAL_WEIGHT_COORDINATE
```

该方案用于解决：**R1A 的单侧（one-sided）过渡把主要权重梯度压缩到约一条 mesh edge**
（实测 full-MCP→full-IP 跨度 3.886 mm），导致 30°/45° 下 IP 关节过渡带塌陷。

---

## 六、`TH_MCP_45` min-edge 残余 —— 正式冻结

```
TH_MCP_45_MIN_EDGE_RESIDUAL = ACCEPTED_NON_BLOCKING_FOR_STAGE6A
```

| 指标（`TH_MCP_45`） | Stage6A R1 | Stage6A R1A |
|---|---|---|
| **min edge ratio** | **0.421283** | **0.219223** |
| min face-area ratio | 0.193672 | 0.297893 |
| face-area p05 | 0.523736 | 0.580019 |
| max edge stretch | 3.016385 | 3.016385 |
| intra-thumb pairs | 79 | 74 |

**理由（如实记录）**：

1. 这是六个 thumb case 中的**主要残余单项**；
2. 同 case 的 max stretch **未变**、face-area 统计与自交**均改善**；
3. Human Review 观察 before/after 渲染，**未见新增不可接受尖刺、塌陷或明显教学形态破坏**；
4. 375 个受限权重候选中，**没有一个**能够让所有 restricted case 的 min-edge 都完全 non-regressed；
5. 因此**不继续为单一 min-edge 数值开启 R1C**。

> 这是 `ACCEPTED_DOCUMENTED_RESIDUAL`。
> **不是** `METRIC_INVALID`，**也不是** `GENERAL_EXCEPTION`。
> **不得**传播成其他关节的通用豁免。

---

## 七、自交 authority（冻结）

| 项 | Stage6A R1 | Stage6A R1A |
|---|---|---|
| `INTRA_TARGET_DIGIT_PAIRS` | 279 | **259** |
| `TARGET_VS_OTHER_DIGIT` | 404 | **400** |
| pairs > 0.5 mm | 454 | **450** |

```
THUMB <-> INDEX = POSE_CONSTRAINT_DIAGNOSTIC
```

**不得**把 isolated RSSF 下的 thumb-index contact 重新归因为 skin-weight blocker。
但 **Stage6B combined opposition 时必须重新测试真实联动姿态**。

---

## 八、`.blend` 可重复性勘误（本轮关闭）

完整勘误：`stage5b_r1b/STAGE5B_R1B_BLEND_REPRODUCIBILITY_ERRATA.md`
证据：`stage5b_r1b/_tmp/R1B_BLEND_REPRODUCIBILITY_CHECK.json`

```
BLEND_CONTAINER_BYTE_REPRODUCIBILITY = NOT_GUARANTEED
REPRODUCIBLE_UNDER_FIXED_OUTPUT_PATH  = TRUE
SEMANTIC_PAYLOAD_REPRODUCIBILITY      = PASS
```

- 同路径连续两次重建 → **字节完全相同**（`8cb6bd46…5c9c`）；
- 换路径重建 → 2 296 143 B 中仅 **36 B** 不同，且 **36 B 全部落在 8 字节内部指针槽位**；
- 语义载荷逐字段比较（含 **3416 顶点 × 16 组权重**）**全部 IDENTICAL**；
- **approved R1B master 未被覆盖**（核验后哈希仍为 `cec5804f…`）。

---

## 九、Stage6B binding obligations（仅记录，不执行）

Freeze 收据已写入以下约束；Stage6B 必须至少覆盖：

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

Stage6B 功能 authority = **真正的 thumb opposition / teaching hand function**，
**不得**由 Stage6A isolated flex 自动替代。

---

## 十、停止点

```
STAGE6B = READY_TO_BEGIN      （禁止写 STARTED）
```

本轮以下动作**未执行且禁止执行**：修改 R1B 权重、创建 R1C、改 mesh / retopo、
改 CMC cage、改 joint、改 bone roll、改 bone count、改 rig hierarchy、改 RSSF、
改 nail / distal cap / first-web、Stage6B 形变、CMC opposition、combined opposition、
钢琴按键、演奏动画、MediaPipe retarget、左手、GLB、Three.js。

---

## 十一、状态汇总

```
STAGE5B_R1B                       = FINAL_APPROVED
STAGE5B_MASTER                    = RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend
STAGE5B_FREEZE_R1B                = PASS
STAGE5B_R1A                       = SUPERSEDED_BY_R1B_FOR_THUMB_WEIGHTING（保留 provenance）
STAGE6A_R1A                       = FINAL_APPROVED
STAGE6A_ISOLATED_FLEX_DEFORMATION = FINAL_APPROVED
THUMB_IP_TRANSITION               = PASS
THUMB_MCP_TRANSITION              = PASS_WITH_ACCEPTED_DOCUMENTED_RESIDUAL
DEFORMATION_FINAL                 = PENDING_STAGE6B
STAGE6B                           = READY_TO_BEGIN
PRODUCTION_MASTER_GEOMETRY        = UNCHANGED
PRODUCTION_RIG_SKELETON           = UNCHANGED
```
