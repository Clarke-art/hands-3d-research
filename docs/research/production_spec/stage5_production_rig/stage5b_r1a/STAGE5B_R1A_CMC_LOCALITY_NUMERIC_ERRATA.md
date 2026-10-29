# STAGE5B_R1A_CMC_LOCALITY_NUMERIC_ERRATA

**性质**：ERRATA sidecar（勘误附页）。**不回改** `STAGE5B_R1A_REPORT.md` / `STAGE5B_R1A_STATUS.json`，
历史文件继续保留 provenance。
**本轮**：纯只读重算 + 文档。未修改任何 blend、未修改任何权重。
**重算证据**：`stage5b_r1a/STAGE5B_R1A_CMC_LOCALITY_NUMERIC_RECOMPUTE.json`
**输入**：`stage5b_r1a/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1A.blend`
SHA-256 `c68e415aff80b56911cfe5646e47dff9100d7b54b8bf7aa8ba068bb3948c0ea6`
**区域权威**：`stage5b_r1a/THUMB_SEMANTIC_REGION_AUDIT.json`
（本轮已用独立重算逐区域比对，7/7 区域顶点集合**完全相同**）

---

## 零、正式声明

```
THUMB_CMC_THENAR_LOCALITY_HUMAN_REVIEW = APPROVED
REOPENED_BY_THIS_ERRATA                = NO
```

本勘误只解决**同一指标被两个不同数值表述**的记账问题；
**不构成** locality 判定重开，**不构成**权重缺陷，**不触发** FAIL CLOSED。

---

## 一、被质疑的两个原值

| 出处 | 原文 / 键 | 值 | 性质 |
|---|---|---|---|
| `STAGE5B_R1A_REPORT.md` §五 | 散文：“THUMB_CMC 权重 100 % 落在 FIRST_METACARPAL ∪ THENAR_BASE 内（占比 ≥ 0.9 gate，**实测 1.0**）” | **1.0** | ❌ **无任何机器可读产物支持** |
| `STAGE5B_R1A_STATUS.json` | `thumb_chain_locality.THUMB_CMC_share_inside_first_metacarpal_or_thenar` | **0.925204** | ✅ 度量 **B**（权重质量占比） |
| `STAGE5B_R1A_CMC_THENAR_LOCALITY.json` | 同上键名 | **0.925204** | ✅ 度量 **B** |

### 两个原值各自为何产生

- **0.925204 的来源（正确）**：`s5b_r1a_audit.py` 中
  `_cmc_in = Σ THUMB_CMC_R over (THUMB_FIRST_METACARPAL ∪ THENAR_BASE)`，
  `_cmc_tot = Σ THUMB_CMC_R over the entire mesh`，`share = _cmc_in / _cmc_tot`。
  即 **度量 B（权重质量占比）**，分母 243.399683、分子 225.194429。该值可由冻结 blend 完整复现。

- **1.0 的来源（错误）**：**不存在**。该数字在 R1A 全部输出中没有任何机器可读背书；
  同一 gate 在审计脚本中的判定式为 `share >= 0.9`，报告撰写时把
  “gate 通过”误写成了“实测值 = 1.0”。经本轮穷举检验（见 §三），
  **任何合理解释下的 region union 都无法得到 1.0**，所有 union 的上限为 **0.972791**。

### 判定

```
STAGE5B_R1A_REPORT.md 中的 "实测 1.0"
  = STALE / AMBIGUOUS WORDING（无背书散文声明，非另一口径的真实度量）
STAGE5B_R1A_STATUS.json 中的 0.925204
  = 唯一有机器可读背书的数值，但其键名省略了 metric 类型
    ⇒ 亦属 AMBIGUOUS NAMING（"share" 未说明是 vertex coverage 还是 weight mass）
```

---

## 二、Authoritative metric definitions（本勘误建立，binding）

`eps` 默认取 **1e-8**（项目标准）；同时给出 eps=0 / 1e-6 / 1e-3 供对照。
区域 union 固定为 **`THUMB_FIRST_METACARPAL ∪ THENAR_BASE`**（413 顶点；两集合交 27）。

### A. `THUMB_CMC_NONZERO_VERTEX_COVERAGE_IN_TARGET_REGIONS`

```
numerator   = #{ v : THUMB_CMC_R(v) > eps  AND  v ∈ (THUMB_FIRST_METACARPAL ∪ THENAR_BASE) }
denominator = #{ v : THUMB_CMC_R(v) > eps }
```

| eps | numerator | denominator | value |
|---|---|---|---|
| 0.0 | 339 | 907 | **0.373760** |
| 1e-8（默认） | 339 | 907 | **0.373760** |
| 1e-6 | 339 | 874 | 0.387872 |
| 1e-3 | 336 | 590 | 0.569492 |

### B. `THUMB_CMC_WEIGHT_MASS_SHARE_IN_TARGET_REGIONS`

```
numerator   = Σ THUMB_CMC_R(v)  over  v ∈ (THUMB_FIRST_METACARPAL ∪ THENAR_BASE)
denominator = Σ THUMB_CMC_R(v)  over  the entire mesh
```

| numerator | denominator | value |
|---|---|---|
| **225.194429** | **243.399683** | **0.925204** |

### C. 其它 region union 的对照（用于排除“1.0 来自另一种口径”）

| 候选 union | union 顶点数 | 度量 B（weight mass share） | 度量 A（eps=0 vertex coverage） |
|---|---|---|---|
| C1 META ∪ THENAR（**权威**） | 413 | **0.925204** | 0.373760 |
| C2 + THUMB_PROXIMAL | 505 | 0.972791 | 0.388093 |
| C3 + THUMB_BASE_FOLD | 450 | 0.925204 | 0.373760 |
| C4 + PROXIMAL + BASE_FOLD | 542 | 0.972791 | 0.388093 |
| C5 + PROXIMAL + BASE_FOLD + DISTAL | 703 | 0.972791 | 0.388093 |
| C6 + FIRST_WEB | 430 | 0.925204 | 0.373760 |
| C7 全部 thumb 语义区域（除 CENTRAL_PALM） | 703 | 0.972791 | 0.388093 |
| C8 = AUTH（授权修改集） | 703 | 0.972791 | 0.388093 |
| C9 THUMB_FIRST_METACARPAL only | 153 | 0.622982 | 0.168688 |
| C10 THENAR_BASE only | 287 | 0.407537 | 0.234840 |
| C11 META ∪ THENAR ∪ AUTH | 703 | 0.972791 | 0.388093 |

> **结论**：不存在值为 1.0 的口径。报告中的 “1.0” 必须视为**无背书措辞**。

---

## 三、目标 union 之外的 THUMB_CMC 质量去向（0.074796 = 7.4796 %）

```
outside vertex count = 568 ； sum = 18.205254 ； share = 0.074796
max single outside weight = 1.000000 (v777)
```

| 所在区域 | 顶点数 | THUMB_CMC 质量和 | 说明 |
|---|---|---|---|
| THUMB_PROXIMAL | 13 | **11.582636** | MCP 关节层过渡环（例：v777 arc 41.44 mm ≈ MCP 关节弧 42.6796 mm，dThumb 11.28 mm）。`THUMB_CMC_R` 是 THUMB_PROXIMAL 的**允许骨**，此处主导属设计内行为。 |
| CENTRAL_PALM | 531 | **6.622561** | R1 继承的**授权掌扇**（palm metacarpal fan，max 0.222808，无 >0.5 顶点）。区域外，R1A 未触碰。 |
| 不属于任何 R1A 区域（24 个 `INDEX` 自有顶点） | 24 | **0.0000559** | 单点最大 1.48e-05，属 R1 继承的浮点级残留，无功能影响。 |

三项均为**正常设计后果**，无一为 R1A 引入：
PROXIMAL 项是 region 允许骨分工，PALM 项是授权掌扇，余项在浮点噪声量级。
**这正是度量 B 值为 0.925204 而非 1.0 的全部原因。**

---

## 四、Authoritative recomputed values（最终口径）

```
THUMB_CMC_NONZERO_VERTEX_COVERAGE_IN_TARGET_REGIONS (eps=1e-8) = 339 / 907 = 0.373760
THUMB_CMC_WEIGHT_MASS_SHARE_IN_TARGET_REGIONS                 = 225.194429 / 243.399683 = 0.925204
```

**统一措辞规范（后续所有文档必须遵守）**

- 不得再把任意一个数字单称 `THUMB_CMC_share`。
- 必须写全 `THUMB_CMC_NONZERO_VERTEX_COVERAGE_IN_TARGET_REGIONS`（度量 A）
  或 `THUMB_CMC_WEIGHT_MASS_SHARE_IN_TARGET_REGIONS`（度量 B）。
- `THUMB_CMC_THENAR_LOCALITY` gate 的判定口径固定为**度量 B ≥ 0.9**（实测 0.925204，PASS）。

---

## 五、残余表述归属

| 旧表述 | 归属 |
|---|---|
| `REPORT.md` “100 % 落在 … / 实测 1.0” | **STALE_WORDING（无背书）** — 历史文件保留，不再引用 |
| `STATUS.json` / `CMC_THENAR_LOCALITY.json` 键 `THUMB_CMC_share_inside_first_metacarpal_or_thenar` | **AMBIGUOUS_NAMING** — 数值正确（= 度量 B），键名未标 metric 类型；历史文件保留，后续以本勘误 §二 全名引用 |

---

## 六、产物

```
stage5b_r1a/STAGE5B_R1A_CMC_LOCALITY_NUMERIC_ERRATA.md              （本文件）
stage5b_r1a/STAGE5B_R1A_CMC_LOCALITY_NUMERIC_RECOMPUTE.json         （只读重算证据）
stage5b_r1a/scripts/s5b_r1a_freeze_verify.py                        （重算脚本，只读）
```
