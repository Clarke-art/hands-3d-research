# STAGE6B 报告 · THUMB OPPOSITION + COMBINED DEFORMATION VALIDATION R1

- **round**：`STAGE6B_THUMB_OPPOSITION_AND_COMBINED_DEFORMATION_VALIDATION_R1`
- **generated**：2026-09-30T20:40:42.027829+08:00
- **性质**：TECHNICAL OPPOSITION DEFORMATION QUALIFICATION（**非**权重优化 / 非骨架设计 / 非教学标准姿态定义 / 非钢琴按键 / 非动画生产）
- **harnes**：`<HANDS_ROOT>/production_spec/stage6_deformation/stage6b/RIGHT_HAND_STAGE6B_OPPOSITION_HARNESS_R1.blend`
  SHA-256 `4b6200899fe4d2f5a67e3254aec2a5cb17b734b14acefe381a2ac9c1241f549d`（TEST HARNESS COPY，非 Production Master，保存态 ZERO / RSSF）
- **最终状态**：`FAIL_CLOSED_FOR_HUMAN_REVIEW`
- **DEFORMATION_FINAL**：`PENDING_HUMAN_REVIEW`

---

## 一、本轮关闭的历史 pending 项

Stage4 起一直保留的 `CMC_DEFORMATION_FINAL = PENDING_STAGE6` 就是本轮的对象。
本轮执行了 THUMB_CMC isolated opposition、CMC+MCP coordinated、CMC+MCP+IP full chain、
thenar、first web、thumb-index contact progression 六项。
**结论：CMC cage 本身通过，但因拇指-食指缝合面撕裂 blocker，本轮不能把 `CMC_DEFORMATION_FINAL` 置为 PASS。**

---

## 二、CMC 轴向探测（§九）

六向 ±5° 小角度 probe（其它骨全部锁定），指尖 landmark 世界位移：

| local axis | tip 位移 (mm @5°) | 投影到 T_OPPOSE (mm) |
|---|---|---|
| X +5° | 8.783313 | -8.392046 |
| X −5° | 8.783299 | +8.573903 |
| Y +5° | 2.150455 | +2.105630 |
| Y −5° | 2.150416 | -2.096945 |
| Z +5° | 9.032086 | -1.199480 |
| Z −5° | 9.032031 | +1.337243 |

Jacobian（mm / rad）:

- **local_X** = [58.624885559, 78.847618103, -21.381736755]
- **local_Y** = [-17.131481171, -16.921344757, 5.124691486]
- **local_Z** = [82.657592773, -62.102909088, 1.665200114]

---

## 三、CMC opposition 单位旋转（§十 / §十二）

```
CMC_OPPOSITION_UNIT_ROTATION (local X,Y,Z) = [-0.868788302, -0.25, -0.427442193]
unit quaternion (local)                        = [0.877582609653, -0.416519254446, -0.119856372476, -0.204926684499]
X/Z share of magnitude                         = 0.9682
local-Y (axial twist) share of magnitude       = 0.2500
achieved direction cos with T_OPPOSE          = 0.922510 (tilt 22.704 deg)
achieved distal component                      = +0.1807
```

- 方向来自 **X/Z 受限的 regularized least-squares 解**（§十 要求 local X/Z 为主）；
  无 hand-tuned 角度。
- 无约束解被 local Y 主导（`solved_uncapped_y_ratio = 3.625`），但其达到的 T_OPPOSE alignment 与 X/Z 解几乎相同（0.922510 vs 0.929185），故限制到 X/Z **零代价**。
- 组合旋转用 **exponential map → 单个 quaternion**，非 Euler 叠加，**无 order dependence**。

### CMC axial twist（§十一）
```
CMC_AXIAL_TWIST_SIGN = -1   (跨 ±3/±5/±7° 稳定 = True)
```
判据 = approved thumb nail normal → pad proxy normal 与 T_OPPOSE 的 alignment 变化。

---

## 四、9 个正式 case（§十三 / §十四 / §十五 / §三十七）

| case | CMC/MCP/IP (deg) | tip 沿 T_OPPOSE (mm) | pad align | thumb-index pairs | seam 最大拉伸 | seam 撕裂边 |
|---|---|---|---|---|---|---|
| CMC_OPP_10 | 10 / 0 / 0 | +14.77 | 0.9904 | 119 | 12.6 x | 48/67 |
| CMC_OPP_20 | 20 / 0 / 0 | +29.18 | 0.9699 | 110 | 25.5 x | 64/67 |
| CMC_OPP_30 | 30 / 0 / 0 | +42.80 | 0.9257 | 100 | 38.2 x | 67/67 |
| CMC_MCP_L1 | 10 / 10 / 0 | +25.06 | 0.9545 | 108 | 19.5 x | 63/67 |
| CMC_MCP_L2 | 20 / 20 / 0 | +49.10 | 0.8294 | 95 | 39.0 x | 67/67 |
| CMC_MCP_L3 | 30 / 30 / 0 | +70.05 | 0.6290 | 85 | 57.5 x | 67/67 |
| FULL_OPP_L1 | 10 / 10 / 5 | +27.86 | 0.9240 | 116 | 21.0 x | 63/67 |
| FULL_OPP_L2 | 20 / 20 / 10 | +54.37 | 0.7171 | 93 | 41.8 x | 67/67 |
| FULL_OPP_L3 | 30 / 30 / 15 | +76.47 | 0.4085 | 83 | 61.3 x | 67/67 |

tip 沿 T_OPPOSE 进展（§二十四，要求整体单调）：
- **CMC_ISOLATED** [14.765373431, 29.178448021, 42.801328003] → monotonic = **True**
- **CMC_MCP** [25.057640858, 49.101563171, 70.047382265] → monotonic = **True**
- **FULL_CHAIN** [27.861936018, 54.365923628, 76.465653256] → monotonic = **True**

---

## 五、各功能区域结论

| 区域 | 关键量 | 判定 |
|---|---|---|
| CMC cage (T-04_CMC) | min face-area ratio 0.6247–0.8494；fold-over 0；cage 内新增自交 0 | **PASS** |
| thenar | PCA bbox volume ratio 0.9359–0.9920；无 catastrophic collapse | **PASS** |
| first web | opening area ratio [0.992316, 1.091327, 1.147129]；degenerate face 0；web 内自交 0 | **PASS（progression 连续）** |
| nail | area ratio 0.99976–1.03821；rigid-fit rel residual ≤ 0.13409；inverted 0 | **PASS（无脱离）** |
| distal cap | area ratio 0.99982–1.00059；rigid-fit rel residual ≤ 0.00378 | **PASS** |
| 四指（clean shaft） | max 0.000059670 mm（噪声底） | **PASS** |
| palm / forearm | forearm max 7.451e-06 mm；palm mean ≤ 0.162726 mm | **PASS** |
| zero restore | max 0.000059670 mm（gate 1e-4），9/9 | **PASS** |
| **thumb ↔ index 缝合面** | **67 条 seam 边，最大拉伸 12.6–61.3×，撕裂 48–67/67** | **FAIL（hard blocker）** |
| CMC cage 自交 | cage 内 new pair = 0（全部 9 case） | **PASS** |
| intra-thumb 自交 | 48–64 pairs/case（与 Stage6A 已接受包络同量级） | 诊断 |
| thumb-index 深穿透 | 83–119 pairs，max proxy 2.42–4.18 mm，>0.5 mm 118–167 pairs | **交 HR 裁定** |

---

## 六、BLOCKER：THUMB_INDEX_SEAM_TEAR（§四十一 / §四十八）

```
blocker_classification.primary   = F_POSE_CONTACT_CONSTRAINT_FAILURE
blocker_classification.sub     = THUMB_INDEX_SEAM_TEAR
```
**机制（证据链）**：
1. RSSF 绑定位姿下拇指远端指骨（含指甲板）与食指 MCP 段**直接相贴**（最近顶点距 1.0586 mm）；
2. 该处有 **67 条 THUMB|INDEX 归属 seam 边**直接连接两侧表面（bind 长度 1.0586–9.0456 mm，中位 3.8912 mm），且跨该边的权重近似**硬跳变**（一侧 `THUMB_IP_R = 1.0`，另一侧 `INDEX_MCP_R ≈ 0.66` + `WRIST_R`）；
3. 因此**任何**拇指链相对食指的相对运动都会把这些边拉开：
   - `CMC_OPP_10`：最大 12.6×，48/67 撕裂
   - `CMC_OPP_30`：最大 38.2×，**67/67 撕裂**
   - `FULL_OPP_L3`：最大 **61.3×**（1.059 → 64.903 mm），**67/67 撕裂**

**这不是本轮引入的**（`STAGE6B_SEAM_CONTEXT.json`）：在**已冻结且已批准的** Stage6A R1A harness 上测同 67 条边——

| pose | 最大拉伸 | 撕裂边 |
|---|---|---|
| TH_MCP_45（Stage6A 已批准包络） | 31.940× | 64/67 |
| TH_IP_45（Stage6A 已批准包络） | 12.916× | 43/67 |
| CMC_OPP_30（Stage6A 已批准包络） | 38.247× | 67/67 |
| FULL_OPP_L3（Stage6A 已批准包络） | 61.312× | 67/67 |

即 Stage6A 的 `TH_MCP_45` **已经**撕裂 64/67 条 seam 边（31.9×），而 Stage6A 未测量 seam 边。
**本轮的新增是「测量与量化」，不是「新损伤」**；但按 §四十一，实际撕裂必须 FAIL CLOSED。

**本轮不做任何修复**（§二十九 / §四十六）：不改权重、不移动 joint、不改 CMC vector、不改拓扑、**不自动启用 OPT-B THENAR/PALM MACRO RETOPO**。

---

## 七、自交与接触（§二十七 / §二十八 / §三十二）

分类计数（不相加为单一总数）：

| case | intra-thumb | thumb-index | thumb-palm | thumb-other | unrelated | max penetration |
|---|---|---|---|---|---|---|
| CMC_OPP_10 | 48 | 119 | 5 | 0 | 36 | 2.4151 mm |
| CMC_OPP_20 | 55 | 110 | 21 | 12 | 63 | 3.4701 mm |
| CMC_OPP_30 | 62 | 100 | 41 | 18 | 81 | 4.1770 mm |
| CMC_MCP_L1 | 53 | 108 | 8 | 3 | 65 | 2.9544 mm |
| CMC_MCP_L2 | 61 | 95 | 31 | 5 | 76 | 2.4347 mm |
| CMC_MCP_L3 | 64 | 85 | 48 | 3 | 96 | 2.5703 mm |
| FULL_OPP_L1 | 54 | 116 | 8 | 4 | 64 | 3.0753 mm |
| FULL_OPP_L2 | 61 | 93 | 31 | 2 | 72 | 2.5720 mm |
| FULL_OPP_L3 | 64 | 83 | 52 | 3 | 82 | 3.5676 mm |

`THUMB ↔ INDEX` 在 isolated RSSF 下继续归类 `POSE_CONSTRAINT_DIAGNOSTIC`；本轮已在真实 coordinated opposition 下复测（§二十七），结果为大量新接触对 + 上述 seam 撕裂。
**接触 vs 深穿透的最终裁定归 Human Review**（§二十八）。

---

## 八、Human Review 渲染（16 张）

- `renders/STAGE6B_BIND_RESTORE_PROOF.png`
- `renders/STAGE6B_CMC_CAGE_CLOSEUP_L3.png`
- `renders/STAGE6B_CMC_MCP_L3_BEFORE_AFTER.png`
- `renders/STAGE6B_CMC_OPP_30_BEFORE_AFTER.png`
- `renders/STAGE6B_CMC_OPP_30_CMC_CAGE_STRAIN.png`
- `renders/STAGE6B_CONTACT_PROGRESSION.png`
- `renders/STAGE6B_DISTAL_CAP_NAIL_L3.png`
- `renders/STAGE6B_FIRST_WEB_CLOSEUP_L3.png`
- `renders/STAGE6B_FIRST_WEB_L1_L2_L3.png`
- `renders/STAGE6B_FULL_OPP_L1.png`
- `renders/STAGE6B_FULL_OPP_L2.png`
- `renders/STAGE6B_FULL_OPP_L3.png`
- `renders/STAGE6B_THENAR_CLOSEUP_L3.png`
- `renders/STAGE6B_THENAR_L1_L2_L3.png`
- `renders/STAGE6B_THUMB_INDEX_CONTACT_CLOSEUP_L3.png`
- `renders/STAGE6B_TIP_TRAJECTORY.png`

约定：`before` = 冻结 Stage5B R1B @ RSSF bind；`after` = 目标 pose；**same camera / scale / lighting / material**；L1/L2/L3 一律同一 camera family。

---

## 九、状态

```
STAGE6B                          = FAIL_CLOSED_FOR_HUMAN_REVIEW
CMC_OPPOSITION_DEFORMATION       = FAIL_CLOSED_FOR_HUMAN_REVIEW
COMBINED_THUMB_OPPOSITION        = FAIL_CLOSED_FOR_HUMAN_REVIEW
CMC_DEFORMATION_FINAL            = PENDING_HUMAN_REVIEW
DEFORMATION_FINAL                = PENDING_HUMAN_REVIEW
PRODUCTION_MASTER_GEOMETRY       = UNCHANGED
PRODUCTION_RIG_SKELETON          = UNCHANGED
PRODUCTION_SKIN_WEIGHT           = UNCHANGED (Stage5B R1B)
```

**立即 STOP**：不进入 key press / teaching pose / left hand / Web export。
