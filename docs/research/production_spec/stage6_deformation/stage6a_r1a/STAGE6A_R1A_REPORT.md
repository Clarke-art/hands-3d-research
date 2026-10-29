# STAGE6A R1A 报告 · 隔离屈曲全量复检（含四指回归）

- **round**：`STAGE6A_R1A_ISOLATED_FLEX_REQUALIFICATION`
- **generated**：2026-09-30
- **status**：`READY_FOR_HUMAN_REVIEW`
- **输入 master**：Stage5B **R1B candidate**（`CANDIDATE_FOR_HUMAN_REVIEW`）
- **测试工装**：`stage6a_r1a/RIGHT_HAND_STAGE6A_DEFORMATION_HARNESS_R1A.blend`
  SHA-256 `c4bb74ea116e7352064c26977a509ed1248aacbe734118e5f9c240fa24b1157b`
- **DEFORMATION_FINAL**：`NOT_SET_PENDING_HUMAN_REVIEW`（**未**写 PASS）
- **stage6b**：`NOT_STARTED`

---

## 一、复检规模（不是只重跑拇指）

```
14 joints  x  15 / 30 / 45 deg  =  42 formal cases
THUMB_CMC_R 与 WRIST_R  =  LOCKED_AT_BIND_POSE
FLEXION_AXIS = bone LOCAL X（Stage5A 冻结）;  FLEXION_SIGN = -1（五指一致）
```

- 度量口径、patch 定义、κ 取值、自交判定**逐行沿用** Stage6A R1 运行器
  （`stage6a/scripts/s6a_run_cases.py`，SHA-256
  `33710e8f3b1d551401d0f30dee04052cd84a0f07d91a119e1a2f33854521fb67`），
  R1A 版本仅替换输入 master / 工装路径 / 输出文件命名并追加回归对比段。
- **引擎自校验**：以 `form=onesided` 复算 R1A 权重 → **float32 精确一致（0 处差异）**，
  且六 thumb case 的 min face-area / p05 / max stretch / min edge / intra 与 Stage6A R1
  实测 **全等**。

---

## 二、门（全部 PASS）

| gate | 结果 |
|---|---|
| `FLEXION_AXIS_SIGN_QUALIFIED` | PASS |
| `FORMAL_CASE_COUNT` | **42** |
| `ZERO_RESTORE_AFTER_EACH_CASE` | **PASS** |
| `ZERO_RESTORE`（汇总） | **PASS** |
| `NAN_INF_DEFORM` | 0 |
| `COLLAPSED_FACES` | 0 |
| `FOUR_FINGER_REGRESSION` | **PASS** |
| `FOREARM_STABILITY` | PASS |
| `NON_TARGET_DIGIT_SHAFT_CONTAMINATION` | PASS |
| `TIP_TRAJECTORY_MONOTONIC` | PASS |
| `TOPOLOGY_UNCHANGED_ALL_CASES` | true |
| `MAX_INFLUENCES` | 4 |
| `NAIL_DEFORMATION` | **PASS（无回归）** |
| `DISTAL_CAP` | **PASS（无回归）** |
| `FIRST_WEB` | **PASS（无回归）** |
| `HARNESS_FINAL_POSE_ZERO` | 5.967e-05 mm |
| `MASTER_HASH_UNCHANGED` / `HARNESS_HASH_UNCHANGED` | true |
| `THUMB_MCP_TRANSITION` | **IMPROVED_PENDING_HUMAN_REVIEW** |
| `THUMB_IP_TRANSITION` | **IMPROVED_PENDING_HUMAN_REVIEW** |
| `NEW_SEVERE_SELF_INTERSECTION` | `PASS_WITH_HUMAN_REVIEW` |

**blockers = 0**。`all_gates_pass = True`（但**不含** `DEFORMATION_FINAL`，该项由 HR 裁定）。

---

## 三、拇指三 case 数值（R1 → R1A）

| metric | TH_IP_30 R1 → R1A | TH_IP_45 R1 → R1A | TH_MCP_45 R1 → R1A |
|---|---|---|---|
| min face-area ratio | 0.054027 → **0.416085** (×7.70) | 0.019443 → **0.181324** (×9.33) | 0.193672 → **0.297893** (×1.54) |
| face-area p05 | 0.322227 → **0.714432** | 0.436325 → **0.619005** | 0.523736 → **0.580019** |
| max edge stretch | 2.287108 → **2.034480** | 3.127780 → **2.733736** | 3.016385 → **3.016385**（持平） |
| min edge ratio | 0.075150 → **0.244620** | 0.286202 → **0.445217** | 0.421283 → **0.219223** ⚠ |
| intra-thumb 自交对 | 35 → **30** | 51 → **42** | 79 → **74** |
| local surface-area ratio | 1.008559 → 0.981885 | 1.071838 → 0.983090 | 1.078911 → 1.049894 |

放宽到全部 6 个 thumb case（含 15°/30°）：

| case | minAR | p05 | max stretch | min edge | intra |
|---|---|---|---|---|---|
| TH_MCP_15 | 0.492276 → 0.695244 | 0.706566 → 0.832893 | 1.551121 → 1.408898 | 0.465582 → 0.711945 | 33 → 33 |
| TH_MCP_30 | 0.324811 → 0.456639 | 0.481305 → 0.712787 | 2.078012 → 2.004247 | 0.356231 → 0.427973 | 49 → 49 |
| TH_MCP_45 | 0.193672 → 0.297893 | 0.523736 → 0.580019 | 3.016385 → 3.016385 | 0.421283 → **0.219223** ⚠ | 79 → 74 |
| TH_IP_15 | 0.441064 → 0.599756 | 0.634885 → 0.827962 | 1.552091 → 1.446986 | 0.435307 → 0.551881 | 13 → 12 |
| TH_IP_30 | 0.054027 → 0.416085 | 0.322227 → 0.714432 | 2.287108 → 2.034480 | 0.075150 → 0.244620 | 35 → 30 |
| TH_IP_45 | 0.019443 → 0.181324 | 0.436325 → 0.619005 | 3.127780 → 2.733736 | 0.286202 → 0.445217 | 51 → 42 |

**35 项指标中 34 项不劣化或改善；唯一劣化项 = `TH_MCP_45 min_edge_ratio`**（见 §七）。

---

## 四、四指回归 = 严格 0 漂移

`STAGE6A_R1A_FOUR_FINGER_REGRESSION.json`：

| 项 | 值 |
|---|---|
| 对比 case 数 | **36**（12 关节 × 15/30/45°） |
| target patch 位移最大差 | **0.000e+00 mm** |
| non-target clean 位移最大差 | **0.000e+00 mm** |
| hard blocker 不一致数 | 0 |
| 判定 | **PASS** |

根本保证：`INDEX_*` / `MIDDLE_*` / `RING_*` / `LITTLE_*` 四组在 R1B 中**逐顶点逐字节未变**
（`STAGE5B_R1B_POSTSAVE_SELF_PROOF.json`：`frozen_four_finger_groups = 0.0`），
因此四指形变在数值上是**恒等**，与实测 0.000e+00 mm 一致。

`sanctioned FIRST_WEB cross blend` 同样逐顶点未变（漂移 0.0），
故 first-web 位移在 42 case 上与 R1 完全一致（`FIRST_WEB = PASS`）。

---

## 五、nail / distal cap / zero restore

| 项 | 结果 |
|---|---|
| nail area ratio 与 R1 最大差 | **0.000e+00**（`NAIL_DEFORMATION = PASS`） |
| distal cap area ratio 与 R1 最大差 | **0.000e+00**（`DISTAL_CAP = PASS`） |
| `ZERO_RESTORE` | PASS，max 恢复残差 **5.967e-05 mm**（硬门 1e-4 mm） |
| forearm 最大位移 | ≤ 1e-3 mm 门内，`FOREARM_STABILITY = PASS` |
| non-target clean 顶点最大位移 | 5.967e-05 mm（float32 噪声底） |

---

## 六、自交（措辞按本轮勘误）

```
total_new_pairs          : R1 909  -> R1A 909 - ... 见下表
intra_target_digit_pairs : R1 279  -> R1A 259
target_vs_other_digit    : R1 404  -> R1A 400
pairs deeper than 0.5 mm : R1 454  -> R1A 450
```

拇指数值（intra-thumb）：35→30、51→42、79→74、13→12、33→33、49→49。
THUMB↔INDEX 跨指碰撞继续按 `POSE_CONSTRAINT_DIAGNOSTIC` 记录，**本轮不作为权重优化目标**，
也**未**因权重改动而增加。

叙述采用 `STAGE6A_R1_SELF_INTERSECTION_WORDING_ERRATA.md` 的更正版本：
非零 case **绝大多数**集中在 THUMB / INDEX_MCP，另有 MIDDLE_MCP、RING_MCP 少量浅层 pair
（每 case ≤3、最大 penetration ≤0.383 mm、无一对深于 0.5 mm），**不构成 blocker**。

---

## 七、残余项（交 Human Review）

```
TH_MCP_45 min_edge_ratio :  R1 = 0.421283  ->  R1A = 0.219223
```

- 六 thumb case × 5 类指标（30 项）中**唯一**劣于 Stage6A R1 的指标；
- 375 个候选中**无一个**能在全部受限 case 上同时不退化 `min_edge_ratio`；
- 同 case 的 **max edge stretch 完全持平**、**face-area ratio / p05 改善**、
  **intra-thumb 自交减少**；
- 语义：45° 单纯 MCP 屈曲下**掌侧内表面**的局部压缩，与已修复的 face-area 塌陷同源但更轻；
- **是否可接受归 Human Review**，本轮不自行判 PASS。

---

## 八、方法学勘误（本轮发布，历史文件不回改）

1. `STAGE6A_R1_THICKNESS_PROXY_AUTHORITY_ERRATA.md`
   —— `LOCAL_THICKNESS_PROXY = DIAGNOSTIC_ONLY`；不得再单独以
   `IDX_MCP thickness ≈ 0` 作为真实 collapse 的硬证据。给出新权威优先级
   （目视 > face-area strain > edge strain > 自交 > 局部面积/轮廓 > thickness proxy）。
   证据：该量在 42 case 中跨 5 个数量级（0.000549 – 16.078711 mm），
   且对角**非单调**（LTL_MCP_15 = 1.6e-05 而 LTL_MCP_45 = 0.1095）。
2. `STAGE6A_R1_SELF_INTERSECTION_WORDING_ERRATA.md`
   —— 更正 R1 报告中"非零 case 全部集中在 THUMB / INDEX_MCP"的绝对化措辞。

---

## 九、Human Review 同机位 before / after 图（9 张）

渲染约定：`before = Stage5B R1A + Stage6A R1 pose`；
`after = Stage5B R1B candidate + Stage6A R1A 同 pose`。
两台工装的诊断相机与灯光由**同一确定性配方**生成，渲染前后**逐一比对签名完全相同**
（`same camera / scale / lighting / material / angle`，未通过换机位掩盖问题）。
每格 900×630；上排 = BEFORE，下排 = AFTER。

| 文件 | 布局 |
|---|---|
| `STAGE6A_R1A_THUMB_IP_30_BEFORE_AFTER.png` | 4 列（背 / 掌 / 拇指特写 / 侧）× 2 排 |
| `STAGE6A_R1A_THUMB_IP_45_BEFORE_AFTER.png` | 同上 |
| `STAGE6A_R1A_THUMB_MCP_45_BEFORE_AFTER.png` | 同上 |
| `STAGE6A_R1A_THUMB_IP_30_STRAIN.png` | 3 列（特写 / 掌 / 背）× 2 排；面面积比着色 |
| `STAGE6A_R1A_THUMB_IP_45_STRAIN.png` | 同上 |
| `STAGE6A_R1A_THUMB_MCP_45_STRAIN.png` | 同上 |
| `STAGE6A_R1A_INTRA_THUMB_INTERSECTION_BEFORE_AFTER.png` | 6 列（3 case × 特写/掌）；**半透明蒙皮 + 不透明红 = 新增自交面** |
| `STAGE6A_R1A_FOUR_FINGER_REGRESSION.png` | 4 列（INDEX/MIDDLE/RING/LITTLE 于 MCP 45°）× 2 排 |
| `STAGE6A_R1A_BIND_RESTORE_PROOF.png` | 2 列（背 / 特写）× 2 排，bind rest pose |

STRAIN 配色：`log10(face-area ratio)`，红 ≤ −1（塌陷）、绿 0（静止）、蓝 ≥ +1（拉伸）；
**before / after 使用同一色标**，两排可直接目视比较。

---

## 十、状态

```
STAGE6A_R1A                  = READY_FOR_HUMAN_REVIEW
THUMB_IP_TRANSITION          = IMPROVED_PENDING_HUMAN_REVIEW
THUMB_MCP_TRANSITION         = IMPROVED_PENDING_HUMAN_REVIEW
FOUR_FINGER_REGRESSION       = PASS
ZERO_RESTORE                 = PASS
FOREARM_STABILITY            = PASS
NON_TARGET_DIGIT_SHAFT_CONTAMINATION = PASS
TIP_TRAJECTORY_MONOTONIC     = PASS
NAIL_DEFORMATION             = NO_REGRESSION
DISTAL_CAP                   = NO_REGRESSION
FIRST_WEB                    = NO_REGRESSION
DEFORMATION_FINAL            = NOT_SET_PENDING_HUMAN_REVIEW
STAGE6B                      = NOT_STARTED
```

**立即 STOP。**

## 十一、本轮产物

```
stage6a_r1a/RIGHT_HAND_STAGE6A_DEFORMATION_HARNESS_R1A.blend
stage6a_r1a/STAGE6A_R1A_STATUS.json
stage6a_r1a/STAGE6A_R1A_CONSOLIDATED_SUMMARY.json
stage6a_r1a/STAGE6A_R1A_THUMB_TRANSITION_ROOT_CAUSE.json
stage6a_r1a/STAGE6A_R1A_THUMB_WEIGHT_CANDIDATE_RANKING.json
stage6a_r1a/STAGE6A_R1A_VERSUS_STAGE6A_R1.json
stage6a_r1a/STAGE6A_R1A_FOUR_FINGER_REGRESSION.json
stage6a_r1a/STAGE6A_R1A_{FLEXION_AXIS_SIGN,CASE_MATRIX,ZERO_RESTORE,LOCAL_STRAIN,
             PINCH_COLLAPSE,SELF_INTERSECTION,CROSS_DIGIT_DEFORM,FOREARM,
             TIP_TRAJECTORY,NAIL_DEFORM,THUMB_DISTAL,DISPLACEMENT}_*.json
stage6a_r1a/STAGE6A_R1_THICKNESS_PROXY_AUTHORITY_ERRATA.md
stage6a_r1a/STAGE6A_R1_SELF_INTERSECTION_WORDING_ERRATA.md
stage6a_r1a/renders/  （9 张 Human Review 图）
stage6a_r1a/scripts/  （诊断 / 扫描 / 建模 / 复检 / 渲染 / 整合，共 8 个脚本）
```
