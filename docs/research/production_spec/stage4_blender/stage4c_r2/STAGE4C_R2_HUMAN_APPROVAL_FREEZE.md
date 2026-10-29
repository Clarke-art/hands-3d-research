# STAGE4C_R2_HUMAN_APPROVAL_FREEZE

**Receipt revision**：R1
**签发任务**：`STAGE4C_R2_HUMAN_APPROVAL_FREEZE_R1`
**签发时间**：2026-09-29T08:28:01+08:00
**性质**：记录 Human Review 裁决的冻结回执。本轮**不**创建、**不**修改任何资产。

---

## 1. Human Review 结论

```
STAGE4C_R2_HUMAN_REVIEW = APPROVED
```

---

## 2. 批准 master（不可变）

```
APPROVED_MASTER        = stage4c_r2/RIGHT_HAND_ENGINEERING_STAGE4C_R2.blend
APPROVED_MASTER_SHA256 = fde620b2cebd2b4cd894e32b58d7b59ba7fac9b00d3d2dfa5193cefb32513ab7
APPROVED_MASTER_BYTES  = 2,009,735
MUTABLE                = false
```

> 该 blend 不得修改。

---

## 3. 条件项

```
CON_4_NAILS        = PASS   （per-face MATERIAL，slot 1 = NAIL_BED，124 面；零几何、零 tri）
CON_5_RSSF_REPOSE  = PASS   （carry-forward，Stage-4B R2 语义修正版；顶点 delta = 0）
CON_6_ORIGIN       = PASS
CON_7_UV           = PASS   （carry-forward；uv_max_delta = 0）

CANONICAL_HAND_POSE   = RSSF
HAND_BASE_TOPOLOGY    = UNCHANGED
TOPOLOGY_SIGNATURE    = 5a396684…90c1d（PRE = POST）
CMC_DEFORMATION_FINAL = PENDING_STAGE6
```

---

## 4. 版本沿革

```
Stage4C R1 = SUPERSEDED_FOR_CON_4（保留 provenance，未删除、未覆盖、未回写）
Stage4C R2 = APPROVED_STAGE4C_MASTER
```

- R1 blend `66fa45325273f38f597f6af78bec603c471a697d6f1798b96eecc231e64bcdb6` 保持逐字节不变。
- R2 相对 R1 的**变更面**仅限 face material assignment（`NAIL_BED` 155 → 124 面）。

---

## 5. 冻结验证

```
执行前 sha256 = fde620b2cebd2b4cd894e32b58d7b59ba7fac9b00d3d2dfa5193cefb32513ab7
执行后 sha256 = fde620b2cebd2b4cd894e32b58d7b59ba7fac9b00d3d2dfa5193cefb32513ab7
SHA256_UNCHANGED = true          （hash 变化时：FAIL CLOSED）

V = 3416    E = 6828    F = 3414    TRIS = 6828
QUADS = 3414    NGONS = 0    100% quad
```

**独立只读复核**（`D:\Blender\blender.exe --background`，Blender 5.1.2，未保存）：

| 项 | 实测 |
| --- | --- |
| objects | `Hand  - Realistic`（唯一） |
| armatures / vertex groups / modifiers / constraints / actions | 全部为空 |
| material slots | `HAND_SKIN` 3290 面 / `NAIL_BED` 124 面 |
| UV layers | `UVMap` |
| object origin | `[1.408704638, 0.022395039, 0.335847497]` |
| object scale / rotation | `[1,1,1]` / `[0,0,0]` |
| 打开后 `is_dirty` | `false` |
| 打开后 blend sha256 | 不变 |

```
PRODUCTION_RIG          = NOT_STARTED
PRODUCTION_SKIN_WEIGHT  = NOT_STARTED
LEFT_HAND               = NOT_STARTED
ANIMATION               = NOT_STARTED
GLB                     = NOT_STARTED
THREE_JS                = NOT_STARTED
```

---

## 6. 必须冻结的 Stage 5 约束（binding）

```
STAGE4B_WRIST_R_LOCATOR_DEFECT = ACKNOWLEDGED_AND_BINDING_ON_STAGE5
```

Stage-4B TEMP rig 的 `WRIST_R` 头位于**前臂截断面**处
（head z = 0.277348846 m；前臂端盖 = mesh bbox z-min = 0.276016384 m；
Stage-4B 自身日志即写 "narrowest cross-section at −1.9 mm from the forearm cap"），
导致其"腕→掌心"骨长 **201 mm**（解剖上应为 ~65–90 mm）。

**Stage 5 必须**：

```
DO_NOT_INHERIT_STAGE4B_WRIST_R_POSITION
```

禁止作为输入：`WRIST_R` head `[1.395632625, 0.015556923, 0.277348846]`

**Stage4C R2 当前批准的 wrist / origin**：

```
WRIST_ORIGIN = [1.408704638, 0.022395039, 0.335847497]
```

**Stage 5 可以**：

- **方案 A** — 直接以该批准 wrist/origin 作为 wrist reference；**或**
- **方案 B** — 使用已经记录的 `radius-limited interior-minimum locator`
  （见 `ORIGIN_AUDIT_R2.json.locator`）重新验证。

> **如果重新验证结果发生明显漂移，必须 FAIL CLOSED 并回到 Human Review，不得自行改腕位。**

该 defect **不**影响 Stage-4B 的 RSSF 关节角验收（全部在手指上测量）。

---

## 7. 本轮新增文件

```
stage4c_r2/STAGE4C_R2_REPORT_NUMERIC_ERRATA.md        数字勘误（documentation-only）
stage4c_r2/STAGE4C_R2_HUMAN_APPROVAL_FREEZE.json      本回执（机读）
stage4c_r2/STAGE4C_R2_HUMAN_APPROVAL_FREEZE.md        本回执（人读）
```

数字勘误要点：`STAGE4C_R2_FINALIZATION_REPORT.md` Section 4 中 13 个几何统计单元格
取自 selector 收口前的探针 `_tmp/R2_SELECTOR_PROBE.json`，为 stale 值。

```
NAIL_AUDIT_R2.json = AUTHORITATIVE_FINAL_NAIL_GEOMETRY_STATISTICS
```

**原报告未回改、模型数据未改、审计 JSON 未改。**

---

## 8. 遗留项

| ID | 状态 |
| --- | --- |
| `STAGE4B_WRIST_R_LOCATOR_DEFECT` | **OPEN** — 对 Stage 5 有约束力 |
| `STAGE4C_R1_ORIGIN_STAGE3_DELTA_WORDING` | CLOSED_BY_ERRATA |
| `STAGE4C_R2_REPORT_NUMERIC_ERRATA` | CLOSED_BY_ERRATA（仅文档同步） |
| `STAGE4C_R2_ORIGIN_AUDIT_WRIST_R_ZMIN_WORDING` | REPORTED_NOT_CLOSED（仅措辞；见 errata §6，请 Human 决定是否再出勘误） |

---

## 9. 最终状态

```
STAGE4C        = FINAL_APPROVED
STAGE4C_R2     = APPROVED_STAGE4C_MASTER
STAGE4C_FREEZE = PASS
STAGE5         = READY_TO_BEGIN
```

**不得写** `STAGE5 = STARTED`。

**已停止。未创建 Production Rig，未进入 Stage 5。**
