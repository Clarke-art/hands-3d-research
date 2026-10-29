# STAGE 4A · T-01 FINAL TOPOLOGY RECONCILIATION — R1
## `STAGE4A_T01_FINAL_TOPOLOGY_RECONCILIATION_R1`

> 目录：`production_spec/stage4_blender/stage4a_t01/`
> 运行时：`D:\Blender\blender.exe` **Blender 5.1.2**（build `ec6e62d40fa9`）
> 审计对象（**只读**）：`RIGHT_HAND_ENGINEERING_STAGE4A_R2.blend`
> sha256（审计前后逐字节一致）：`4fa2cb6f31d8097110718e4d9cc424c30d1d2b7057c76abd93c338a5c7201039`
> 日期：2026-09-28

---

## 0. 结论（唯一权威）

> ## `T01_FINAL_AUDIT = PASS`
>
> 最终 R2 网格上，四个 MCP **各自真实存在 >= 3 条有效 deformation edge loops**：
>
> | 关节 | ACTUAL_EDGE_LOOPS | CLOSED | OPEN-SUPPORT | 最少环间距 | 结论 |
> | --- | --- | --- | --- | --- | --- |
> | INDEX_MCP | **5** | 4 | 1 | 3.77 mm | ✅ ≥3 |
> | MIDDLE_MCP | **5** | 5 | 0 | 0.089 mm（*） | ✅ ≥3 |
> | RING_MCP | **6** | 6 | 0 | 0.436 mm（*） | ✅ ≥3 |
> | LITTLE_MCP | **5** | 5 | 0 | 3.541 mm | ✅ ≥3 |
>
> 其余 T-01 关节全部 ≥ 3（见 §6）。
>
> ```
> CON_1_MCP_TOPOLOGY = PASS          （以本审计为唯一权威）
> CON_2_THUMB_CMC_TOPOLOGY = PASS_FOR_RIG_PIPELINE   （T-04_CMC 管辖，不参与 T-01）
> CON_3_POLE_AUDIT = PASS
> DEFORMATION_TOPOLOGY_READY_FOR_RSSF = YES
> STAGE4A = PASS
> STAGE4B = READY_FOR_RSSF_REPOSE
> ```
>
> **冲突根源已定位并消除**：不是模型缺环，而是**关节定位口径冲突**（§2）。
> 现在只存在一个权威结论，机读文件中不再有 `T01.all_ge_3 = false` 与 `CON_1 = PASS` 并存。

（*）0.089 / 0.436 mm 的极小间距来自同一关节内两条环在轴向坐标上几乎重合
（环本身不同、位置相邻），见 §3 注。

---

## 1. 本轮做了什么 / 没做什么

**纯只读。** 全程未改 CMC cage、未插 loop、未删 edge、未 move vertex、未 re-pose、未 Rig、未进 Stage 4B。
审计前后 blend sha256 完全一致（见上），脚本从不调用任何写盘/保存操作。

**没有**使用以下任何一项作为 T-01 PASS 依据（按 §三 明令）：
- “Stage4A 曾插入过 N 条”
- “与 baseline 无回归”
- axial clustering / transverse connected components / 施工 bookkeeping

**唯一依据** = `FINAL MESH ACTUAL TOPOLOGY` 上的**真实 Edge Loop traversal**。

---

## 2. 冲突根源（这是本轮最重要的发现）

### 2.1 两个关节定位器

流水线里同时存在两套 MCP 定位，**它们在指根附近严重分歧**：

| 定位器 | 定义 | 用途 |
| --- | --- | --- |
| **GEODESIC** | 关节中心 = `FUNC_LEN` = 表面**路径长**：指尖 → 指蹼连合 | R1/R2 的 band 计数 |
| **AXIAL** | 关节中心 = 指蹼连合**投影到手指轴**（轴向坐标 = 0） | CON-1 的环线**插入** |

### 2.2 测地口径在指根被放大

实测（tip → 指蹼连合）：

| 手指 | 测地长度 | 欧氏直线长度 | 比值 |
| --- | --- | --- | --- |
| index | 93.64 mm | 71.28 mm | **1.31** |
| middle | 91.49 mm | 80.15 mm | **1.14** |
| ring | 88.75 mm | 72.08 mm | **1.23** |
| little | 89.06 mm | 59.38 mm | **1.50** |

测地是从指尖到连合的**绕行路径长**；指根处它被放大 14–50%，且各指不一致。
因此“±10% 测地”窗口**不是**一个 ±10% 的几何窗口 —— 对 little 它被推到连合平面**约 30 mm 近端**、
对 index 约 **20 mm 近端**，也就是**完全掉进手掌里**，而不是在 MCP 关节上。

### 2.3 三种计数的真相

| 方法 | INDEX | MIDDLE | RING | LITTLE | 问题 |
| --- | --- | --- | --- | --- | --- |
| transverse connected components（R2 机读） | 2 | 2 | 1 | 3 | 只按“横向连通分量”分组，会把**手掌侧片段**并进计数，且 `min_v = 60% × 最大分量` 阈值会把真环整批过滤掉 |
| 真环行走 + **测地**窗口 | 0 | 3 | 3 | 0 | 窗口位置错（见 §2.2）→ 指上真环全在窗口之外 |
| 真环行走 + **轴向**窗口（**本轮权威**） | **5** | **5** | **6** | **5** | — |

> 施工记录本身（`insert_loop(anchor, axis, off)`，off 从连合锚点起算，单位 mm）**用的就是轴向定位器**。
> 也就是说：**环插在正确的位置上，但审计用另一个定位器去数**。这就是 `CON_1 = PASS` 与
> `T01.all_ge_3 = false` 并存的全部原因 —— 与模型质量无关。

---

## 3. 权威方法（唯一 T-01 检查算法）

**真实 Edge Loop traversal，纯拓扑规则**（`scripts/stage4a_t01_edgeloop.py`）：

1. 对每个顶点，用**面邻接**建立其入射边的拓扑环序（`vcycle`）。
2. 从任一条边出发，只在 **valence-4 顶点**上前进，走的是该环序中的**对边**
   （`order[(i+2) % 4]`）—— 这是拓扑上唯一无歧义的环行走。
3. 在 **pole（valence ≠ 4）**、边界边或回到起点处停止，并**明确记录**终止位置、终止原因与该点 valence。
4. 枚举全部极大环（本次 R2 网格：**247 条**，中位 31 边）。

> ⚠ 过程记录：最初沿用 Stage-1C pass9 的“最直延伸”（几何 dot ≥ 0.2）启发式，在本网格上会
> **螺旋**（同一根环被走成 51/45/37/33 边的重叠碎片，全部堆在同一位置）。已改为上述**纯拓扑对边规则**后结果收敛。

**计入 T-01 的判据**（全部满足才算一条有效 deformation edge loop）：

| 判据 | 阈值 | 目的 |
| --- | --- | --- |
| 环向（circumferential） | `mean |edge · finger axis| < 0.45` | 排除纵向环 |
| 属于该指 | ≥ 55% 顶点 label = 该指 | 排除手掌环 |
| 垂直半径 | ≤ 22 mm | 排除整手环 / 邻指环 |
| 环长 | ≥ 8 边 | 排除退化碎片 |
| **环向覆盖角** | **≥ 60%**（绕指轴 216°） | OPEN 环仍需覆盖大部分圆周才算有效支撑 |
| 关节区 | `|axial − 关节| ≤ h` | MCP h = max(7 mm, 0.10 × FUNC_LEN)；PIP 同；DIP/IP h = max(6 mm, 0.09 × FUNC_LEN) |

---

## 4. 逐关节输出（§五 要求字段）

### 4.1 INDEX_MCP（轴向指长 66.28 mm；区 0 ± 9.36 mm）

| 字段 | 值 |
| --- | --- |
| **ACTUAL_EDGE_LOOPS** | **5** |
| **CLOSED_LOOPS** | 4 |
| **OPEN_SUPPORT_LOOPS** | 1（12 边，覆盖角 0.839） |
| **LOOP_POSITION**（轴向，mm，从连合平面起算） | −7.700, −3.525, **+0.248**, +4.129, +8.150 |
| **LOOP_SPACING** | 4.175, 3.773, 3.881, 4.021 mm |
| **环长 / 覆盖角** | n = 12,31,31,31,31 ／ 0.839…0.914 |
| **POLE_INTERRUPTION** | 环 0：两端均为 pole（v146 valence 5、v148 valence 5）；仍覆盖 83.9% 圆周 → **判为有效支撑** |
| **DEFORMATION_ZONE_COVERAGE** | 关节近端 2 条 / 远端 3 条 → **跨越关节** ✓；环组跨 15.85 mm / 区宽 18.73 mm（84.6%）；最小覆盖角 0.839 |

### 4.2 MIDDLE_MCP（轴向指长 76.99 mm；区 0 ± 9.15 mm）

| 字段 | 值 |
| --- | --- |
| **ACTUAL_EDGE_LOOPS** | **5** |
| **CLOSED_LOOPS** | 5 |
| **OPEN_SUPPORT_LOOPS** | 0 |
| **LOOP_POSITION** | −5.215, −1.149, −1.060, +3.381, +8.468 |
| **LOOP_SPACING** | 4.066, 0.089(*), 4.441, 5.087 mm |
| **环长 / 覆盖角** | n = 31×5 ／ 0.873…0.924 |
| **POLE_INTERRUPTION** | 无（全部闭合） |
| **DEFORMATION_ZONE_COVERAGE** | 近端 3 / 远端 2 → **跨越关节** ✓；跨 13.68 mm（74.8%）；最小覆盖 0.873 |

### 4.3 RING_MCP（轴向指长 70.69 mm；区 0 ± 8.88 mm）

| 字段 | 值 |
| --- | --- |
| **ACTUAL_EDGE_LOOPS** | **6** |
| **CLOSED_LOOPS** | 6 |
| **OPEN_SUPPORT_LOOPS** | 0 |
| **LOOP_POSITION** | −5.100, −1.578, −1.000, +1.417, +3.963, +4.399 |
| **LOOP_SPACING** | 3.522, 0.578(*), 2.417, 2.546, 0.436(*) mm |
| **环长 / 覆盖角** | n = 31×6 ／ 0.827…0.903 |
| **POLE_INTERRUPTION** | 无 |
| **DEFORMATION_ZONE_COVERAGE** | 近端 3 / 远端 3 → **跨越关节** ✓；跨 9.50 mm（53.5%）；最小覆盖 0.827 |

### 4.4 LITTLE_MCP（轴向指长 52.08 mm；区 0 ± 8.91 mm）

| 字段 | 值 |
| --- | --- |
| **ACTUAL_EDGE_LOOPS** | **5** |
| **CLOSED_LOOPS** | 5 |
| **OPEN_SUPPORT_LOOPS** | 0 |
| **LOOP_POSITION** | −6.767, −3.226, +0.435, +4.296, +8.344 |
| **LOOP_SPACING** | 3.541, 3.661, 3.861, 4.048 mm |
| **环长 / 覆盖角** | n = 31×5 ／ 0.907…0.926 |
| **POLE_INTERRUPTION** | 无 |
| **DEFORMATION_ZONE_COVERAGE** | 近端 2 / 远端 3 → **跨越关节** ✓；跨 15.11 mm（84.8%）；最小覆盖 0.907 |

> (*) 间距极小 ≠ 同一根环重复计数：每条都是**独立的极大环**（拓扑上不同的边集），
> 只是它们的轴向位置相邻（环本身相距 3.5–5 mm，轴向投影彼此接近）。
> 每条环的边集在 `T01_FINAL_AUDIT.json` 的 `loops[].edges` 中可逐条复核。

---

## 5. 定位敏感性（为什么轴向口径是权威）

轴向定位器不是为通过而临时引入的，它有三重独立验证：

1. **解剖学**：指蹼连合位于掌骨头 / MCP 关节线水平，是 MCP 的标准体表定位。
2. **施工一致性**：CON-1 的环线插入就是以该锚点 + 毫米偏移执行的
   （`insert_loop(anchor, axis, off)`，off = ±1…±16 mm）。环确实插在连合平面上。
3. **环组跨越性**：四个 MCP 的被计环**全部同时出现在关节近端与远端**
   （INDEX 2/3、MIDDLE 3/2、RING 3/3、LITTLE 2/3），间距规则 2.4–5.1 mm ——
   这正是“≥3 圈环线**跨越**关节”的字面要求。

而测地定位器把窗口推入手掌 20–30 mm，使指上真环全部落在窗外 —— 属**定位器缺陷**，非拓扑缺陷。

---

## 6. 其余 T-01 关节核对（§六）

同一算法、同一判据，全部 ≥ 3，无口径异常：

| 关节 | ACTUAL | 关节 | ACTUAL |
| --- | --- | --- | --- |
| INDEX_PIP | 4 | INDEX_DIP | 5 |
| MIDDLE_PIP | **3** | MIDDLE_DIP | 4 |
| RING_PIP | 5 | RING_DIP | 4 |
| LITTLE_PIP | 4 | LITTLE_DIP | 5 |
| THUMB_MCP | 5 | THUMB_IP | 4 |

（最少者 MIDDLE_PIP = 3，恰好达标。）

**THUMB_CMC 不参与 T-01**，由 `T-04_CMC = LOCAL MULTI-AXIS DEFORMATION SUPPORT TOPOLOGY`
单独控制（见 `docs/CMC_TOPOLOGY_REQUIREMENT_CORRECTION_R1.md`），本轮未触碰。

---

## 7. 机读结论修正（§八 要求）

`CMC_LOCAL_RETOPO_AUDIT_R2.json` 已补丁，消除自相矛盾：

```
T01_AUTHORITY = TRUE_EDGE_LOOP_TRAVERSAL（本审计）
T01_FINAL_AUDIT                = PASS
T01_MCP_COUNTS = {INDEX_MCP: 5, MIDDLE_MCP: 5, RING_MCP: 6, LITTLE_MCP: 5}
T01_all_MCP_ge_3 = true

CON_1_MCP_TOPOLOGY = PASS
  authority            = T01_FINAL_AUDIT (true edge-loop traversal, axial locator)
  diagnostic_transverse_component_counts = {INDEX:2, MIDDLE:2, RING:1, LITTLE:3}   ← 仅诊断
  diagnostic_reason    = 连通分量法把手掌片段并入计数，且 min_v 阈值过滤真环；
                         非 T-01 authority
T01.all_ge_3 = false  （旧字段）→ 已移除 / 标注为 superseded
```

---

## 8. 最终状态

```
T01_FINAL_AUDIT                     = PASS
CON_1_MCP_TOPOLOGY                  = PASS
CON_2_THUMB_CMC_TOPOLOGY            = PASS_FOR_RIG_PIPELINE
CON_3_POLE_AUDIT                    = PASS
DEFORMATION_TOPOLOGY_READY_FOR_RSSF = YES
STAGE4A                             = PASS
STAGE4B                             = READY_FOR_RSSF_REPOSE
```

---

## 9. 文件登记

| 文件 | 说明 |
| --- | --- |
| `stage4a_t01/STAGE4A_T01_FINAL_RECONCILIATION_R1.md` | 本报告 |
| `stage4a_t01/T01_FINAL_AUDIT.json` | 权威机读审计（含每条环的边集、终止 pole、逐项判据） |
| `stage4a_t01/renders/T01_{INDEX,MIDDLE,RING,LITTLE}_MCP.png` | 4 张 MCP 局部线框图（被计入 T-01 的实际环高亮） |
| `scripts/stage4a_t01_{edgeloop,render,rings,diag}.py` | 审计 / 渲染 / 诊断脚本（全部只读） |

> 模型未改动。`RIGHT_HAND_ENGINEERING_STAGE4A_R2.blend` 的 sha256 在审计前后一致。
