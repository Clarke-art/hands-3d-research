# STAGE6A_R1_SELF_INTERSECTION_WORDING_ERRATA

- **stage**: STAGE6A_FORMAL_ERRATA
- **issued under**: STAGE5B_R1B_THUMB_MCP_IP_NARROW_WEIGHT_REPAIR + STAGE6A_R1A_ISOLATED_FLEX_REQUALIFICATION
- **issued at**: 2026-09-30
- **corrects**: a wording statement in `stage6_deformation/stage6a/STAGE6A_REPORT_R1.md`
- **historical files**: **NOT edited** (see §五)

---

## 一、被勘误的原句

`STAGE6A_REPORT_R1.md`（§十二 自交小节，第 168 行）原文：

> 非零 case 全部集中在 **THUMB（MCP / IP）与 INDEX_MCP** —— 即 **在 RSSF 绑定姿态下本就相互接触的两根手指**。

**该句不严格成立。** 正式 audit 数据中还存在少量 **MIDDLE_MCP** 与 **RING_MCP** 的非零 pair。

---

## 二、反证（来自现有 `STAGE6A_SELF_INTERSECTION_AUDIT.json`，未回改）

全 42 case 中，"新增相交 = 0" 的为 **27 / 42**；其余 15 个非零 case 的完整体分布如下。

| case | new_pairs | intra_target | target_vs_other | other_vs_other | max penetration (mm) | >0.5 mm | >0.2 mm |
|---|---|---|---|---|---|---|---|
| TH_MCP_45 | 222 | 79 | 84 | 59 | — | — | — |
| TH_MCP_30 | 171 | 49 | 67 | 55 | — | — | — |
| TH_IP_45 | 159 | 51 | 71 | 37 | — | — | — |
| TH_MCP_15 | 119 | 33 | 58 | 28 | — | — | — |
| TH_IP_30 | 113 | 35 | 52 | 26 | — | — | — |
| IDX_MCP_45 | 46 | 5 | 32 | 9 | — | — | — |
| IDX_MCP_30 | 38 | 6 | 27 | 5 | — | — | — |
| TH_IP_15 | 18 | 13 | 5 | 0 | — | — | — |
| IDX_MCP_15 | 13 | 1 | 8 | 4 | — | — | — |
| **MID_MCP_45** | **3** | **3** | 0 | 0 | **0.266653** | **0** | 1 |
| **MID_MCP_30** | **3** | **3** | 0 | 0 | **0.194841** | **0** | 0 |
| **RNG_MCP_45** | **1** | 0 | 0 | **1** | **0.334782** | **0** | 1 |
| **RNG_MCP_30** | **1** | 0 | 0 | **1** | **0.369994** | **0** | 1 |
| **RNG_MCP_15** | **1** | 0 | 0 | **1** | **0.382824** | **0** | 1 |
| **MID_MCP_15** | **1** | **1** | 0 | 0 | **0.090015** | **0** | 0 |

（`TH_*` / `IDX_*` 行的 penetration 列从略，其值与本勘误结论无关；
完整数值见 audit JSON 的 `cases[*].max_penetration_depth_mm`。）

**pair 样本 id**：

```
MID_MCP_15 : [[2421, 2783]]
MID_MCP_30 : [[1596, 2776], [2421, 2776], [2421, 2783]]
MID_MCP_45 : [[1596, 2776], [2421, 2776], [2421, 2783]]
RNG_MCP_15/30/45 : [[2185, 3358]]
```

---

## 三、更正后的表述（binding 措辞）

> 非零 case **绝大多数**集中在 **THUMB（MCP / IP）与 INDEX_MCP**；
> 此外 **MIDDLE_MCP 与 RING_MCP 还存在少量浅层非零 pair**
> （每个 case ≤ 3 对，最大 penetration proxy ≤ 0.3828 mm，**没有任何一对深于 0.5 mm**），
> 其形态与"每指 MCP 在 45° 全屈下的内侧褶皱压缩"一致，
> **不是** thumb↔index 那种姿态级接触。

---

## 四、分类与是否 blocker

```
MIDDLE_MCP / RING_MCP 浅层 pair:
  CLASSIFICATION = SHALLOW_INTRA_DIGIT_CREASE (diagnostic)
  BLOCKER        = NO
  依据           : 每 case ≤ 3 对；最大 penetration proxy 0.090–0.383 mm；
                   深度 > 0.5 mm 的 pair 数 = 0；
                   与 THUMB / INDEX_MCP 的 404 对跨指姿态接触在数量级上不可比。
```

- 这**不改变** Stage6A R1 的整体裁决与 gate 状态（`NEW_SEVERE_SELF_INTERSECTION =
  PASS_WITH_HUMAN_REVIEW` 不变）。
- 这**不改变** "THUMB ↔ INDEX 跨指接触 = POSE_CONSTRAINT_DIAGNOSTIC" 的既有分类。
- 这**只**修正"全部集中"这一绝对化措辞。

---

## 五、历史文件处理

以下文件**保持原样，不回改**（provenance）：

```
stage6_deformation/stage6a/STAGE6A_REPORT_R1.md          （§十二 原句保留）
stage6_deformation/stage6a/STAGE6A_SELF_INTERSECTION_AUDIT.json
stage6_deformation/stage6a/STAGE6A_STATUS.json
```

后续任何引用 Stage6A R1 自交分布的文档，必须同时引用本勘误，或直接采用 §三 的更正表述。

---

## 六、对本轮（STAGE6A_R1A）的影响

- 本轮回归的 `intra-thumb` 计数口径**不变**，仍逐 case 与 R1 的实测值对比：
  `TH_MCP_15=33, TH_MCP_30=49, TH_MCP_45=79, TH_IP_15=13, TH_IP_30=35, TH_IP_45=51`。
- 本轮**不**把 MIDDLE_MCP / RING_MCP 浅层 pair 纳入修复目标（四指权重为 frozen）。
- 本轮报告中的自交叙述一律采用 §三 的更正表述。

---

## 七、状态

```
STAGE6A_R1_SELF_INTERSECTION_WORDING = CORRECTED (见 §三)
MIDDLE_MCP / RING_MCP SHALLOW PAIRS  = ACCEPTED_NON_BLOCKING_DIAGNOSTIC
HISTORICAL_R1_FILES                  = UNCHANGED
```
