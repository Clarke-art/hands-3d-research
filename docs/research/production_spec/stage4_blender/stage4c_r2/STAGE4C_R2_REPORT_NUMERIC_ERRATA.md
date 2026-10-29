# STAGE4C_R2_REPORT_NUMERIC_ERRATA

**任务**：`STAGE4C_R2_HUMAN_APPROVAL_FREEZE_R1` — 数字勘误（documentation-only）
**类型**：文档同步勘误。**不**回改原报告、**不**改模型、**不**改审计 JSON、**不**创建 R3。
**生成时间**：2026-09-29T08:28:01+08:00
**冻结 master（本轮未改动）**：`stage4c_r2/RIGHT_HAND_ENGINEERING_STAGE4C_R2.blend`
`sha256 fde620b2cebd2b4cd894e32b58d7b59ba7fac9b00d3d2dfa5193cefb32513ab7`

---

## 0. 正式声明

```
NAIL_AUDIT_R2.json = AUTHORITATIVE_FINAL_NAIL_GEOMETRY_STATISTICS
```

```
权威文件   stage4c_r2/NAIL_AUDIT_R2.json
           sha256 0a8388c44792b432512818ea0f8450af8961981df1d487d0ecd5008abc5bcddc
勘误对象   stage4c_r2/STAGE4C_R2_FINALIZATION_REPORT.md  Section 4
           sha256 cc6a47b55578c7732c0e2370a8c79565eb2e15f8996772c2cb20c4f227f86c49
           （**原报告保持逐字节不变，未回改**）
```

本 errata 仅关闭**文档同步**问题（report 的几何统计表中残留了 selector 收口前的数值）。
它**不**改变任何 gate 判定、**不**改变模型数据、**不**改变任何已批准的验收结论。

---

## 1. 根因（已定位到具体来源文件）

`STAGE4C_R2_FINALIZATION_REPORT.md` Section 4 的表格是一张**混合表**：

| 表列 | 实际来源 | 状态 |
| --- | --- | --- |
| `faces`、合计 124 | 最终运行（= `NAIL_AUDIT_R2.json`） | 正确 |
| `distal bone` | 最终运行 | 正确 |
| `axial 归一化`、`bbox extent`、`到自身骨距离`、`到竞争指距离` | **收口前探针** `stage4c_r2/_tmp/R2_SELECTOR_PROBE.json` | **stale** |

**探针与最终 selector 的参数差异**（探针 JSON 的 `parameters` 字段 vs `STAGE4C_R2_RUN.json.selector_parameters`）：

| 参数 | 探针（写表时） | 最终（收口后） |
| --- | --- | --- |
| `CONE_MIN` | 0.66 | **0.60** |
| `RADIAL_FRAC_MIN` | 0.35 | **0.25** |
| `AX_LO / AX_HI` | 0.18 / 0.80 | 0.18 / 0.80（未变） |
| `OWN_MARGIN / COMP_MIN_M / SPECK_FRAC` | 0.85 / 0.004 / 0.15 | 同（未变） |

**方向自洽**：`RADIAL_FRAC_MIN` 由 0.35 放宽到 0.25，甲片沿背侧外壳向下延伸更多，
因此最终 face 数上升（10/21/30/22/19 → **12/29/35/25/23**），
bbox extent 与"到竞争指距离"随之小幅变化。数值变化**方向一致**，说明这不是两次独立测量冲突，
而是**同一次收紧-复跑之后，报告表格未从最终产物重新取值**。

**证据**：逐单元格比对结果表明，报告 Section 4 中的每一个 stale 值都可与
`_tmp/R2_SELECTOR_PROBE.json` 的同名字段**精确对上**（见第 2 节"探针值"列）。

---

## 2. 已确认 stale 项目（Section 4 全量清点）

`Δ = 最终权威值 − 报告值`（正 = 报告偏低）。全部单位 mm（轴向为无量纲归一化系数）。

| ID | digit | 报告字段 | 报告值（stale） | 探针值（来源） | **最终权威值** `NAIL_AUDIT_R2` | Δ |
| --- | --- | --- | --- | --- | --- | --- |
| E-01 | THUMB | bbox extent (mm) | 5.6 × 3.6 × 12.1 | 5.6 × 3.58 × 12.05 | **6.35 × 4.32 × 12.05** | +0.75 / +0.72 / −0.05 |
| E-02 | INDEX | bbox extent (mm) | 10.2 × 9.2 × 3.1 | 10.17 × 9.23 × 3.11 | **12.19 × 9.23 × 4.51** | +1.99 / +0.03 / +1.41 |
| E-03 | MIDDLE | bbox extent (mm) | 12.6 × 10.0 × 3.4 | 12.58 × 10.01 × 3.38 | **14.26 × 10.64 × 3.78** | +1.66 / +0.64 / +0.38 |
| E-04 | RING | bbox extent (mm) | 12.2 × 8.6 × 3.3 | 12.15 × 8.6 × 3.26 | **12.15 × 8.6 × 3.44** | −0.05 / 0 / +0.14 |
| E-05 | LITTLE | bbox extent (mm) | 7.9 × 6.8 × 3.7 | 7.91 × 6.81 × 3.72 | **9.82 × 6.81 × 4.46** | +1.92 / +0.01 / +0.76 |
| E-06 | INDEX | 到自身骨距离 max | 6.84 | 6.84 | **7.80** | +0.96 |
| E-07 | MIDDLE | 到自身骨距离 min–max | 5.73 – 8.32 | 5.73 – 8.32 | **5.72 – 8.35** | −0.01 / +0.03 |
| E-08 | LITTLE | 到自身骨距离 min–max | 3.32 – 6.18 | 3.32 – 6.18 | **3.25 – 6.79** | −0.07 / +0.61 |
| E-09 | INDEX | 到竞争指距离 min | ≥ 32.21 | 32.21 | **≥ 31.41** | −0.80 |
| E-10 | MIDDLE | 到竞争指距离 min | ≥ 26.67 | 26.67 | **≥ 25.65** | −1.02 |
| E-11 | LITTLE | 到竞争指距离 min | ≥ 32.55 | 32.55 | **≥ 31.84** | −0.71 |
| E-12 | MIDDLE | axial 归一化 min | 0.20 | 0.200 | **0.194** | −0.006（末位舍入级） |
| E-13 | LITTLE | axial 归一化 min | 0.20 | 0.205 | **0.193** | −0.007（末位舍入级） |

> E-12 / E-13 属**显示位级**差异（第 2 位小数），不影响任何判据；为完整清点一并列出。

**未在报告中打印、故不构成 errata 项的 stale 字段**（仅备查）：
`nearest_owning_bone_distance_mm.mean`（thumb 6.55→6.37 / index 4.81→5.12 / middle 6.42→6.47 /
ring 6.18→6.17 / little 4.57→4.55）与 `nearest_competing_digit_distance_mm.mean`
（thumb 54.34→54.41 / index 37.43→37.84 / middle 31.36→30.77 / ring 29.82→29.66 / little 36.31→36.74）。
报告未引用这些字段，故无需勘误。

---

## 3. Section 4 中经逐项核对**一致**的项目

| digit | 字段 | 报告值 | 最终权威值 | 判定 |
| --- | --- | --- | --- | --- |
| 全部 | `faces` | 12 / 29 / 35 / 25 / 23，合计 124 | 同 | CONSISTENT |
| 全部 | `distal bone` | THUMB_IP_R / INDEX_DIP_R / MIDDLE_DIP_R / RING_DIP_R / LITTLE_DIP_R | 同 | CONSISTENT |
| THUMB | 到自身骨距离 | 4.81 – 9.45 | 4.81 – 9.45 | CONSISTENT |
| THUMB | 到竞争指距离 min | 48.84（报告写作 "48.84–…"，未给上界） | 48.84 | CONSISTENT |
| RING | 到自身骨距离 | 5.65 – 6.96 | 5.65 – 6.96 | CONSISTENT |
| RING | 到竞争指距离 min | ≥ 24.13 | 24.13 | CONSISTENT |
| THUMB | axial 归一化 | 0.20 – 0.73 | 0.199 – 0.728 | CONSISTENT（舍入） |
| INDEX | axial 归一化 | 0.18 – 0.79 | 0.182 – 0.789 | CONSISTENT（舍入） |
| RING | axial 归一化 | 0.29 – 0.80 | 0.288 – 0.798 | CONSISTENT（舍入） |

**报告 Section 4 之外**亦已顺带交叉核对，**未发现** stale numeric value：
§2（selector 闸门参数、`R_env` 11.14 / 7.64 / 7.80 / 7.15 / 6.75）、
§3（R1 204/155/49/6-of-10/46，保留 70 / 丢弃 85 / 新增 54）、
§5（10 组 pairwise 交集全 0）、§6（全部 gate）、
§7（`WRIST_ORIGIN` 与 `ORIGIN_BEFORE`）、§8（V/E/F/TRIS、topology signature、`NAIL_BED` 155→124）、
§11（状态串）均与最终权威文件一致。

---

## 4. 影响评估

| 项 | 结论 |
| --- | --- |
| 模型数据 | **无影响**。本轮未打开写权限保存任何 blend；未重新运行 selector。 |
| 任何 gate 判据 | **无影响**。`gates_result` 中不存在以 `bbox_extent` 或"到竞争指距离区间"为判据的 gate。 |
| 最终集合上的 gate 结果 | 全部维持 PASS：`NAIL_FACE_SET_DISJOINT` / `NAIL_FACE_OWNER_DISTANCE_TEST` / `NAIL_DISTAL_DOMAIN_TEST` / `NAIL_PALMAR_LEAKAGE = 0` / `NAIL_WEBSPACE_LEAKAGE = 0` / `>12mm = 0` / 每指 1 连通分量 |
| `NAIL_BED` 面数 | 不变（**124**） |
| THUMB 甲片 46 → 12 的收缩结论 | 不变，仍成立 |
| CON_4_NAILS 判定 | 不变（**PASS**） |
| 本轮之前所有验收结论 | 不变 |

**观察（非判据）**：E-02/E-03/E-05 的 `bbox extent` 首轴在最终集合上比报告值大约 1.7–2.0 mm，
这是**甲片沿背侧外壳向下延伸更多**所致（`RADIAL_FRAC_MIN` 0.35→0.25），
属设计意图内的收紧-放宽结果，非几何缺陷；`axial_frac_max` 均仍 ≤ 0.80（闸门上限），五指甲片仍为单一连通片。

---

## 5. 本轮**未修改**清单

```
模型数据                          未修改（无任何 blend 被保存）
stage4c_r2/NAIL_AUDIT_R2.json     未修改  sha256 0a8388c4…5bcddc
stage4c_r2/STAGE4C_R2_FINALIZATION_REPORT.md  未修改  sha256 cc6a47b5…f86c49
stage4c/**（R1 全部产物）          未修改（逐个 sha256 见 freeze receipt 的 immutability ledger）
stage4c_r2/**（本轮新增文件之外）  未修改
```

---

## 6. 范围外但已观察到（**不计入本次勘误、不改任何文件**）

```
ERRATA_ID = STAGE4C_R2_ORIGIN_AUDIT_WRIST_R_ZMIN_WORDING
status    = REPORTED_NOT_CLOSED (documentation only, no verdict change)
file      = stage4c_r2/ORIGIN_AUDIT_R2.json
```

同文件内两处表述不一致：

- 字段 `stage4b_WRIST_R_z_equals_mesh_bbox_zmin` = **false**
- 同一文件的 `P0_STYLE_FINDING.what` 文字写作 "its z (0.277349 m) **equals** the mesh
  bounding-box minimum (0.276016 m)"

实际两者相差 **1.333 mm**（0.277348846 vs 0.276016384），字面 "equals" 不精确。

**结论不受影响**：`STAGE4B_WRIST_R_LOCATOR_DEFECT` 成立与否由另外两条独立证据支撑 ——
(a) Stage-4B 自身运行日志记载 "narrowest cross-section at −1.9 mm from the forearm cap"，
(b) 由此产生的"腕→掌心"骨长 201 mm（解剖上应为 ~65–90 mm）。
该 WRIST_R 距前臂截断面仅 1.33 mm，仍落在前臂截断区，**该 finding 及其对 Stage 5 的约束力不变**。

本轮**未修改** `ORIGIN_AUDIT_R2.json`；是否再出一份 wording errata 由 Human 决定。

---

## 7. 结论

```
STAGE4C_R2_REPORT_NUMERIC_ERRATA = CLOSED (documentation synchronization only)

AUTHORITATIVE_FINAL_NAIL_GEOMETRY_STATISTICS = stage4c_r2/NAIL_AUDIT_R2.json
STALE_ITEMS_TOTAL                            = 13 (E-01 … E-13)
REPORT_REWRITTEN                             = NO
MODEL_DATA_MODIFIED                          = NO
AUDIT_JSON_MODIFIED                          = NO
R1_FILES_MODIFIED                            = NO
R3_CREATED                                   = NO
```

**已停止。未进入 Stage 5。**
