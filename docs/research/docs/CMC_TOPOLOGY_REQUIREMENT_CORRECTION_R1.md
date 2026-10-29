# CMC TOPOLOGY REQUIREMENT CORRECTION — R1

> **文档类型**：规范修正（narrow-scope amendment）
> **授权**：Human Review R2 裁定 — **OPT-A = APPROVED**，**OPT-B = DEFERRED_UNLESS_STAGE6_CMC_DEFORMATION_FAILS**
> **修正范围**：仅 `T-01` / `T-04` / `CON-2` 中关于 **THUMB CMC** 的适用语义。
> **明确不做**：不重开 Stage 0 研究；不改动 T-01 对其余关节的适用；不触碰任何已冻结文件。
> **日期**：2026-09-28
> **执行轮次**：`STAGE4A_CMC_TOPOLOGY_REQUIREMENT_CORRECTION_AND_LOCAL_RETOPO_R2`

---

## 0. 一句话结论

```
THUMB CMC 不再适用 "必须存在 >=3 圈绕第一掌骨轴的闭合环" 这一判据。
THUMB CMC 改由 T-04_CMC 单独约束：
    LOCAL MULTI-AXIS DEFORMATION SUPPORT TOPOLOGY
最终功能验收权移交给 Stage 6：FINAL_CMC_DEFORMATION_AUTHORITY = STAGE6_DEFORM_TEST_THUMB_OPPOSE
```

---

## 1. 新规则（正式）

### 1.1 T-01 — `>= 3 circumferential deformation loops`

继续**严格**适用于：

| 手指 | 关节 |
| --- | --- |
| INDEX / MIDDLE / RING / LITTLE | MCP / PIP / DIP |
| THUMB | MCP / IP |

### 1.2 THUMB CMC — 从 T-01 的 "绕骨 collar" 要求中排除

`T-01` 对 THUMB CMC 的 **tubular circumferential collar** 要求 **不再适用**：

```
T01_CMC_TUBULAR_COLLAR_REQUIREMENT = NOT_APPLICABLE
```

不得再以"是否绕第一掌骨一圈"作为 CMC topology PASS 的必要条件，
也不得再使用 winding number = 1 作为 PASS 判据。

### 1.3 T-04_CMC — THUMB CMC 的唯一拓扑判据（正式定义）

```
THUMB CMC 必须具有
    LOCAL MULTI-AXIS DEFORMATION SUPPORT TOPOLOGY
```

必须能够支持未来的：

* flexion / extension
* abduction / adduction
* opposition

但**不要求**任何 closed loop 具有绕第一掌骨轴的 linking number = 1。

### 1.4 CON-2 的验收语义

```
CON_2_THUMB_CMC_TOPOLOGY = PASS_FOR_RIG_PIPELINE   ← 静态验收（Stage 4A）
```

Stage 4A 只判定静态拓扑是否可进入 Rig 流水线；**最终功能验收在 Stage 6**。

---

## 2. 修正依据（本轮已证事实，R1 轮实测）

以下事实已在 `stage4a_r1/THUMB_CMC_LOCAL_RETOPO_REPORT_R1.md` 中量化证明，
它们共同说明：**该 CC0 母资产在 CMC 高度根本不存在"拇指独立管"结构**。

| # | 实测事实 | 数值 |
| --- | --- | --- |
| F1 | 轴向等值线：CMC 高度的横截面把整只手切穿 | axial −30 … +12 mm 恒为 1 条轮廓，半径跨 13.4 … 110 mm |
| F2 | 拇指独立管形成位置 | axial ≈ **+30 mm** 才出现 r = 7.5…15.5 mm 的独立拇指管轮廓（CMC 在 0 mm，相差 30 mm） |
| F3 | CMC 测地邻域拓扑 | R ≤ 45 mm 恒为**拓扑圆盘**（单边界环） |
| F4 | CMC 同心环绕轴圈数 | 全部 = **0.000**（不环绕第一掌骨） |
| F5 | 现有 3 条 "collar" | 轴向跨度 **66.3 / 66.6 / 67.1 mm**，stddev ≈ 20 mm，绕住手腕 ⇒ non-local helical band |

### 2.1 不可能性证明（R1 已证明，勿再尝试）

> P = CMC 测地邻域（R ≤ 45 mm）是拓扑圆盘，且不与掌骨轴相交（最近 13.4 mm）。
> P 内任意闭合环在 P 内张成子圆盘 Σ ⊂ P，Σ 不交掌骨轴 ⇒ linking number = 0。
> ⇒ 任何"环绕掌骨"的环必须离开 P，即至少离 CMC 测地 45 mm 之外。
> ⇒ "局部环绕环"在本资产上几何上不可能。

```
SOURCE_TOPOLOGY_LACKS_LOCAL_TUBULAR_CMC_STRUCTURE
```

因此：**CMC 不应使用 tube-joint collar criterion** —— 这是对 T-01 的过度泛化，予以修正。

---

## 3. 既有 3 条错误 CMC loops 的处置

R1 轮插入的 3 条 66–67 mm helical pseudo-collars **不得作为最终 CON-2 topology**。

* 处置方式：**不修补**，而是回到"CON-1 已完成 / CON-2 未施加"的可精确复现状态，
  在其上重建 CMC 局部拓扑。
* 复现基线：`RIGHT_HAND_ENGINEERING_STAGE4A_R2_BASE.blend`
  （由 `scripts/stage4a_r2_base.py` 从 Stage-2 冻结 bootstrap 重建，
  仅禁用 legacy CMC helical 插入，其余流水线逐字相同）
  sha256 `afbae673ac3e1a520c5a2d6b4e56c6cdc373394876569fb36510865bef7e54a4`
* 原 legacy 产物 `RIGHT_HAND_ENGINEERING_STAGE4A.blend`
  （sha256 `5f69d1ca…cbf40`）**保留不动**，作为 provenance 记录。

**不得破坏**已经 PASS 的：

* `CON_1_MCP_TOPOLOGY`（MCP/PIP/DIP/THUMB MCP/IP 环线）
* `CON_9` ASSET FRAME NORMALIZATION

---

## 4. 新的 CMC 工程目标：CMC LOCAL DEFORMATION CAGE

目标**不是** 3 个绕第一掌骨的圆环，而是：

| 项 | 要求 |
| --- | --- |
| **A** | CMC rotation center 周围有足够局部 quad density |
| **B** | edge flow 围绕 CMC 中心形成局部 radial / concentric support |
| **C** | 向 first metacarpal、thenar、first web 三个方向平顺分流 |
| **D** | 不得产生 40–60 mm helical pseudo-loop |
| **E** | 不得破坏 thenar volume / first web transition / palm arch |
| **F** | 主要 pole 不得位于 flexion strain path / opposition strain path |

### 4.1 工程起始目标（非解剖学硬标准）

R1 实测的 CMC-centered 局部轮廓族 R ≈ 8 / 12 / 16 mm
（axial span 2.85 / 11.09 / 17.89 mm，±12 mm locality ratio ≈ 1，surface deviation ≤ ~0.83 mm）
作为 **PROJECT ENGINEERING STARTING TARGET**。允许人工调整半径与 flow 以保持 thenar / web 形态。

### 4.2 允许的拓扑形式

允许：局部手工 quad re-grid、radial flow、concentric / semi-concentric support loops、
edge slide、dissolve / reconnect、少量 pole reposition。
**不要求**每条 support loop 完整绕第一掌骨轴一圈。

硬约束：**100% quad · 0 n-gon · 0 triangle · 0 non-manifold · 0 loose geometry**。

### 4.3 局部修改范围（STOP 条款）

只允许：CMC centre、first metacarpal base、thenar transition、first web transition 邻近必要范围。
若必须扩大到整个 palm 或大范围 thenar 才能成立：

```
STOP  →  输出 CMC_LOCAL_RET0PO_SCOPE = ESCALATES_TO_MACRO_RETOPO ，不得自行继续
```

本轮未触发该条款（修改范围 ≤ 25.1 mm 半径，见 R2 报告 §5）。

---

## 5. 验收职责划分

| 阶段 | 职责 | 结论 |
| --- | --- | --- |
| **Stage 4A（本轮）** | `CMC_STATIC_TOPOLOGY = PASS_FOR_RIG_PIPELINE`：locality 明确 / 形状保持 / all-quad / edge density 足够 / pole 路径合理 / first web + thenar 保持 / 无 helical pseudo-collar | 见 `CMC_LOCAL_RETOPO_REPORT_R2.md` |
| **Stage 6（唯一功能验收权）** | `FINAL_CMC_DEFORMATION_AUTHORITY = STAGE6_DEFORM_TEST_THUMB_OPPOSE`；THUMB_OPPOSE + flex/ext + ab/ad 全部无 collapse / tear / candy-wrapper twist / first-web distortion / thenar volume loss → `CMC_DEFORMATION_FINAL = PASS` | 待执行 |
| Stage 6 FAIL 时 | 触发 `OPT-B = THENAR_PALM_MACRO_RETOPO` | 现在不做 |

### 5.1 CON-3 重跑

CMC 局部拓扑完成后必须重跑 pole audit。只有最终 topology 上
`CMC_FLEXION_PATH_POLES` / `CMC_OPPOSITION_PATH_POLES` 无危险 pole，才 `CON_3_POLE_AUDIT = PASS`。

---

## 6. 成功状态（本轮已达成，见 R2 报告）

```
CMC_TOPOLOGY_REQUIREMENT_CORRECTION   = PASS
T01_CMC_TUBULAR_COLLAR_REQUIREMENT    = NOT_APPLICABLE
T04_CMC_LOCAL_MULTIAXIS_SUPPORT       = PASS
CON_2_THUMB_CMC_TOPOLOGY              = PASS_FOR_RIG_PIPELINE
CON_3_POLE_AUDIT                      = PASS
CON_1_MCP_TOPOLOGY                    = PASS_NO_REGRESSION
DEFORMATION_TOPOLOGY_READY_FOR_RSSF   = YES
OPT_B_MACRO_RETOPO                    = DEFERRED_UNLESS_STAGE6_FAILS
STAGE4A                               = PASS
```

**到此停止。不进入 Stage 4B，等待 Human Review。**

---

## 7. 文件登记

| 文件 | 说明 |
| --- | --- |
| `docs/CMC_TOPOLOGY_REQUIREMENT_CORRECTION_R1.md` | 本文件（规范修正） |
| `production_spec/stage4_blender/stage4a_r2/CMC_LOCAL_RETOPO_REPORT_R2.md` | R2 执行报告 |
| `production_spec/stage4_blender/stage4a_r2/CMC_LOCAL_RETOPO_AUDIT_R2.json` | R2 机读审计 |
| `production_spec/stage4_blender/RIGHT_HAND_ENGINEERING_STAGE4A_R2.blend` | R2 交付网格 |
| `production_spec/stage4_blender/stage4a_r2/renders/CMC_RETOPO_*.png` | 人审证据图 |

> 本文件为**新增**文件，不修改任何历史文件；历史审计链保持 byte-frozen。
