# STAGE6A_R1A_METRIC_COUNT_WORDING_ERRATA

- **stage**: STAGE6A_R1A_FORMAL_ERRATA
- **issued under**: STAGE5B_R1B_STAGE6A_R1A_HUMAN_APPROVAL_FREEZE_R1
- **issued at**: 2026-09-30
- **type**: **WORDING / COUNT ERRATA ONLY**
- **historical files**: **NOT edited** — `stage6a_r1a/STAGE6A_R1A_REPORT.md` is left as written

---

## 一、被勘误的原文

`stage6a_r1a/STAGE6A_R1A_REPORT.md`（§三 拇指三 case 数值小节末）写有：

> **35 项指标中 34 项不劣化或改善；唯一劣化项 = `TH_MCP_45 min_edge_ratio`**（见 §七）。

该计数**不正确**。

---

## 二、正确的计数

正式定义为：

```
6 thumb cases
  x
5 recorded metric families
  ( min face-area ratio
    face-area p05
    max edge stretch
    min edge ratio
    intra-thumb pairs )
  =
30 items
```

因此正确表述为：

> **30 项指标中 29 项不劣化或改善；唯一劣化项 = `TH_MCP_45 min_edge_ratio`**

（原句中的 "35 / 34" 既非 30 也非任何等价口径；`5 x 6 = 30`，其中 1 项劣化 ⇒ 29 项非劣化。）

---

## 三、影响范围（明确不变项）

| 项 | 是否受影响 |
|---|---|
| 任何 case 的 min face-area ratio / p05 / max edge stretch / min edge ratio / intra-thumb 数值 | **不受影响**（数值全部未变） |
| `TH_MCP_45 min_edge_ratio = 0.219223`（vs R1 `0.421283`） | **不受影响** |
| `TH_MCP_45_MIN_EDGE_RESIDUAL = ACCEPTED_NON_BLOCKING_FOR_STAGE6A` | **不受影响** |
| 42/42 case、blockers 0、各 PASS 门 | **不受影响** |
| Human Review 的批准结论 | **不受影响** |
| 9 张同机位 before/after 渲染 | **不受影响** |

即：**纯计数措辞错误，不影响任何测量值、门、结论或批准。**

---

## 四、历史文件处理

```
stage6a_r1a/STAGE6A_R1A_REPORT.md        不回改（原 35/34 句保留）
stage6a_r1a/STAGE6A_R1A_CONSOLIDATED_SUMMARY.json   不回改
stage6a_r1a/STAGE6A_R1A_STATUS.json      不回改
```

后续任何引用「不劣化项数」的文档，必须采用本勘误的 **30 / 29** 口径。

---

## 五、状态

```
STAGE6A_R1A_METRIC_COUNT = 30  (6 cases x 5 metric families)
NON_REGRESSED_ITEMS       = 29
REGRESSED_ITEMS           = 1   (TH_MCP_45 min_edge_ratio, ACCEPTED_NON_BLOCKING_FOR_STAGE6A)
ERRATA_TYPE               = WORDING_AND_COUNT_ONLY
IMPACT_ON_RESULTS         = NONE
```
