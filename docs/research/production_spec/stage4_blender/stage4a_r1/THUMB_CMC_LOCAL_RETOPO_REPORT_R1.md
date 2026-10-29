# STAGE 4A · THUMB CMC LOCAL RETOPO — R1
## `STAGE4A_THUMB_CMC_LOCAL_RETOPO_R1`

> 目录：`production_spec/stage4_blender/stage4a_r1/`
> 运行时：`D:\Blender\blender.exe` **Blender 5.1.2**（build `ec6e62d40fa9`）
> 输入：`RIGHT_HAND_ENGINEERING_STAGE4A.blend`（冻结为 `STAGE4A_PRE_CMC_RETOPO_BASELINE`）
> 本轮范围：**只做 THUMB CMC / THENAR 局部拓扑**。未 re-pose，未 Rig，未 Skin Weight，未改 origin，未重展 UV，未加指甲，未镜像左手，未进入 Stage 4B。
> 日期：2026-09-28

---

## 0. 结论

> ## `CON_2_THUMB_CMC_TOPOLOGY = NEEDS_MAJOR_RETOPO`
>
> ```
> CON_2_THUMB_CMC_TOPOLOGY   = NEEDS_MAJOR_RETOPO   ← 触发 §14 条件 1
> CON_1_MCP_TOPOLOGY         = PASS_NO_REGRESSION
> CON_3_POLE_AUDIT           = PROVISIONAL_PASS
> ASSET_FRAME_NORMALIZATION  = PASS
> CANONICAL_FRAME_VALIDATION = PASS
> DEFORMATION_TOPOLOGY_READY_FOR_RSSF = NO
> STAGE4A                    = REVISION_REQUIRED
> STAGE4B_RSSF_REPOSE        = BLOCKED
> ```
>
> **本轮没有对网格做任何改动**，因为本轮证明了：**在当前资产上，"环绕第一掌骨的闭合支撑环"在几何上不可能保持局部**。这不是插线方法的问题，也不是前一轮没找对算法——是 thenar 与掌骨在 CMC 高度**根本不构成一根管子**。
>
> 基础文件与工作副本**逐字节未变**：`5f69d1ca…cbf40`（= 评审前基线）。

---

## 1. 输入保护（§3）

| 项 | 值 |
| --- | --- |
| 冻结基线 | `RIGHT_HAND_ENGINEERING_STAGE4A.blend` → `STAGE4A_PRE_CMC_RETOPO_BASELINE` |
| sha256 **pre** | `5f69d1ca4b5a70f4f41d70710d6d8ed9b6ba6c4052a70d4de7c429a5b7bcbf40` |
| sha256 **post** | `5f69d1ca4b5a70f4f41d70710d6d8ed9b6ba6c4052a70d4de7c429a5b7bcbf40` |
| bytes | 2,023,542 |
| `modified` | **false** |
| 工作副本 | `RIGHT_HAND_ENGINEERING_STAGE4A_CMC_R1.blend`（sha256 与基线相同） |
| `STAGE2_FROZEN_BOOTSTRAP_INPUT` | `8fa9a549…05ef83`，未触碰 |

网格完整性复核（§8）：**V=3544 / E=7084 / F=3542；100% quad；0 三角；0 n-gon；0 非流形边；0 边界边；0 松散几何；0 内部面。**

---

## 2. 现有 3 条支撑环的实测（§13 要求字段）

以第一掌骨轴为基准（`CMC = [1.448897, 0.011107, 0.393934]`，`AXIS = [0.617098, −0.075968, 0.783210]`）：

| loop | n | closed | ACTUAL_AXIAL_MIN | ACTUAL_AXIAL_MAX | **SPAN** | MEDIAN | STDDEV | IN ±12 mm | IN ±18 mm | MAX_OUTLIER |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `CON2_CMC@−1mm` | 60 | ✅ | −48.81 | +17.83 | **66.64** | −1.01 | 20.33 | 0.42 | 0.55 | 48.81 |
| `CON2_CMC@+1mm` | 60 | ✅ | −49.77 | +17.28 | **67.06** | +0.99 | 20.49 | 0.47 | 0.53 | 49.77 |
| `CON2_CMC@+3mm` | 60 | ✅ | −47.85 | +18.42 | **66.28** | +2.99 | 20.18 | 0.48 | 0.52 | 47.85 |

表面偏差（对官方 L1 表面，canonical 帧，V=3300 / F=3298）：

**MAX = 5.286 mm · P95 = 3.789 mm · MEAN = 0.779 mm**

> 这三条环的确是**闭合拓扑环、all-quad**，但轴线跨度 66–67 mm，`stddev ≈ 20 mm`。
> `THUMB_CMC_LOCALITY_SIDE.png` 直接显示：它们**在 CMC 处折过窗口后一路下行并绕住手腕**。

---

## 3. 决定性新证据（本轮核心）

### 3.1 轴向等值线：CMC 高度的截面不属于"拇指管"

把表面与垂直于掌骨轴的平面求交，逐 2 mm 输出闭合轮廓：

| axial | 轮廓数 | 轮廓（边数 / 距轴半径 mm） |
| --- | --- | --- |
| −12 mm | 1 | n=89 **r = 13.7 … 94.0** |
| −8 mm | 1 | n=99 **r = 14.1 … 98.6** |
| **0 mm** | **1** | **n=165 r = 13.4 … 110.0** |
| +8 mm | 1 | n=128 r = 13.0 … 121.7 |
| +12 mm | 1 | n=128 r = 12.9 … 126.4 |
| +28 mm | 2 | n=95 r = 7.5 … 102.3 ｜ n=24 r = 122.9 … 142.9 |
| **+30 mm** | **3** | n=77 r = 17.7 … 104.8 ｜ n=25 r = 125.3 … 144.6 ｜ **n=22 r = 7.5 … 15.5 ← 拇指独立管** |

**读法**：从 −30 mm 一直到 +12 mm，截面**只有一条轮廓**，半径跨到 100 mm 以上——它把**整只手切穿**。
拇指**直到 axial ≈ +30 mm** 才与手掌分离成独立管。CMC 在 0 mm，二者相差 30 mm。

> **⇒ 在 CMC 高度不存在"只绕拇指"的水平环。** 任何在该高度的 circumferential 环必然绕整只手。

### 3.2 CMC 邻域是拓扑圆盘

以 CMC 表面点为源，做测地球：

| 球半径 R | 球内顶点 | 边界环数 | 边界环长（边） | 拓扑圆盘 |
| --- | --- | --- | --- | --- |
| 8 mm | 10 | 1 | 8 | ✅ |
| 12 mm | 19 | 1 | 16 | ✅ |
| 20 mm | 41 | 1 | 24 | ✅ |
| 30 mm | 88 | 1 | 44 | ✅ |
| **45 mm** | **210** | **1** | **78** | ✅ |

**⇒ 直到 R = 45 mm，CMC 邻域仍是单边界拓扑圆盘。**

### 3.3 所有 CMC 同心环的绕轴圈数 = 0

以 CMC 为中心、沿表面等测地距离的闭合环族，实测绕第一掌骨轴的**绕数（winding）**：

| R | n | closed | SPAN | IN ±12 | **WINDING** | 是否环绕掌骨 | 距轴半径 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 8 mm | 8 | ✅ | **2.85 mm** | **1.00** | **+0.000** | ❌ | 17.5–19.7 |
| 12 mm | 16 | ✅ | **11.09 mm** | **1.00** | **+0.000** | ❌ | 16.4–21.9 |
| 16 mm | 22 | ✅ | **17.89 mm** | **1.00** | **+0.000** | ❌ | 15.5–25.0 |
| 20 mm | 24 | ✅ | 21.44 mm | 0.92 | +0.000 | ❌ | 15.5–25.4 |
| 25 mm | 34 | ✅ | 35.48 mm | 0.74 | +0.000 | ❌ | 14.8–31.8 |
| 40 mm | 62 | ✅ | 66.08 mm | 0.29 | +0.000 | ❌ | 11.0–38.7 |

这些环**躺在 thenar 表面上**，是围绕 CMC 点的环，**不环绕第一掌骨**。

---

## 4. 不可能性证明（本轮的关键结论）

**命题**：在该资产上，不存在既"环绕第一掌骨"又"C MC 局部"的闭合支撑环。

**证明**
1. 设 P = 以 CMC 为源、测地半径 R 的邻域。实测 P 在 R ≤ 45 mm 内恒为**拓扑圆盘**（单一边界环，§3.2）。
2. P 是表面上的圆盘，且**不与第一掌骨轴相交**（P 上离轴最近距离 13.4 mm > 0）。
3. 落在 P 内的任意闭合环 λ，在 P 内张成子圆盘 Σ；Σ ⊂ P，故 Σ 与掌骨轴不交。
4. 因此 λ 与掌骨轴的**环绕数（linking number）= 0**，即 λ **不环绕第一掌骨**。
5. 反之，任何环绕掌骨轴的环必须有 linking number = ±1，故**必须离开 P**——即必须至少离 CMC **测地 45 mm** 之外。
6. §6 的工程目标是轴向跨度 ≤ 20 mm。一个必须跨越 ≥45 mm 才能闭合的环，要同时把轴向跨度压到 ≤20 mm，只能横向铺开到手掌/手背的整个宽度（§3.1 的实测正是如此：半径一路到 110 mm）。

**∎**
**结论**：`§5-B / §6` 要求的"局部 circumferential support"，在本资产上**无法通过任何局部手术实现**。

---

## 5. 局部可达的最优结构（供 §8 复核，非本轮交付的 PASS 依据）

唯一能在窗口内闭合、且各项指标达标的结构，是 **以 CMC 为中心的同心环族**：

| R | 闭合 | 轴向跨度 | IN ±12 | 表面偏差 max / p95 / mean |
| --- | --- | --- | --- | --- |
| 8 mm | ✅ | **2.85 mm** | **1.00** | 0.391 / 0.163 / 0.089 mm |
| 12 mm | ✅ | **11.09 mm** | **1.00** | 0.391 / 0.315 / 0.090 mm |
| 16 mm | ✅ | **17.89 mm** | **1.00** | 0.826 / 0.384 / 0.120 mm |

**数值上完全满足 §6**（span ≤ 20 mm，比例 ≥ 0.80），形状偏差近 0（顶点都在原表面上）。
**但它绕轴圈数为 0**——它环绕的是 CMC 关节中心，不是掌骨。这是一个**定义变更**，必须由 Human Review 明确授权，不能由执行方自行认定为 PASS。

---

## 6. 人审证据（§12）

`stage4a_r1/renders/`

| 文件 | 内容 |
| --- | --- |
| **`CMC_RETOPO_BEFORE_AFTER.png`** | 左＝BEFORE（3 条基线环：橙球=CMC 旋转中心，黑线=掌骨轴，紫线=±12 mm 窗口，红/蓝/绿=三条支撑环，可见其绕过手掌并**绕住手腕**）；右＝AFTER候选（品红/青/黄绿=CMC 同心环族，完全局部）。**同一相机。** |
| `CMC_RETOPO_DORSAL.png` | 背侧视图，高亮三条基线支撑环 + 旋转中心 + 掌骨轴 + ±12 mm 窗口 |
| `CMC_RETOPO_PALMAR.png` | 掌侧视图，同上 |
| `CMC_RETOPO_SIDE.png` | 侧视图，直接读出三条环大幅越过 ±12 mm 窗口并绕腕 |
| `R1_BASE_WIRE_{dorsal,palmar,radial,thumbaxis}.png` | thenar 局部线框（非全手密集线框），用于观察 quad 流向 |
| `R1_GEORING_{DORSAL,SIDE,LOOPS_ONLY}.png` | CMC 测地同心环族专项图 |

---

## 7. §10 其他已通过区域无回归

**依据**：本轮工作副本与评审基线**逐字节相同**（sha256 一致），因此所有已通过的关节环线在数学上**不可能发生变化**。逐关节环数（沿用 `stage4a/JOINT_LOOP_AUDIT.json`）：

| 关节 | 环数 | ≥3 |
| --- | --- | --- |
| INDEX_MCP / PIP / DIP | 3 / 4 / 4 | ✅ |
| MIDDLE_MCP / PIP / DIP | 3 / 3 / 4 | ✅ |
| RING_MCP / PIP / DIP | 3 / 4 / 4 | ✅ |
| LITTLE_MCP / PIP / DIP | 3 / 4 / 4 | ✅ |
| THUMB_CMC / THUMB_MCP / THUMB_IP | 3 / 4 / 4 | ✅ |

`CON_1_MCP_TOPOLOGY = PASS_NO_REGRESSION`

**§11**：`CON_4_NAILS / CON_5_RSSF_REPOSE / CON_6_ORIGIN / CON_7_UV` 全部保持 `PENDING`，未执行任何 re-pose / Rig / Skin Weight / origin / UV / 指甲 / 左手镜像。

---

## 8. 触发的 §14 失败条件

| 条件 | 是否触发 |
| --- | --- |
| 只能通过大范围 thenar 重建才能解决 | **✅ 触发（第 1 条）** |
| local collar 仍然是 40–60 mm helical flow | 结构上必然（无法局部消除） |
| first web 被破坏 | ❌ 未发生（未改网格） |
| thenar 体积明显变形 | ❌ 未发生（未改网格） |
| 产生大量新 poles / n-gons | ❌ 未发生（未改网格） |
| 已通过 MCP topology 回归 | ❌ 未发生 |

⇒ 依 §14：**停止，不扩大修改范围**。`CON_2 = NEEDS_MAJOR_RETOPO`。

---

## 9. 供 Human Review 决策的两个选项

**OPT-A — 重新界定 CON-2（局部可达成）**
把 CON-2 从"环绕掌骨的闭合环"改为"以 CMC 旋转中心为心的同心环族（绕轴数 0）"。
数值：span 2.85 / 11.09 / 17.89 mm，IN ±12 = 1.00，形状偏差 ≤0.83 mm。
代价：需要 Human Review 明确授权这个定义变更。

**OPT-B — 授权 thenar + 手掌级 macro-retopo（本轮范围外）**
把 3 条环重新走成近似等轴向高度的环绕环。必须把允许修改区域从 thenar 扩大到相邻掌部与手背——**超出 §4 授权范围**，且属"大范围重建"。

---

## 10. 最终状态

```
STAGE4A_THUMB_CMC_LOCAL_RETOPO_R1 = NEEDS_MAJOR_RETOPO

CON_2_THUMB_CMC_TOPOLOGY   = NEEDS_MAJOR_RETOPO
CON_1_MCP_TOPOLOGY         = PASS_NO_REGRESSION
CON_3_POLE_AUDIT           = PROVISIONAL_PASS
ASSET_FRAME_NORMALIZATION  = PASS
CANONICAL_FRAME_VALIDATION = PASS

DEFORMATION_TOPOLOGY_READY_FOR_RSSF = NO
STAGE4A = REVISION_REQUIRED
STAGE4B_RSSF_REPOSE = BLOCKED

RIGHT_HAND_ENGINEERING_STAGE4A = READY_FOR_HUMAN_REVIEW
RIGHT_HAND_ENGINEERING_STAGE4A_CMC_R1.blend = byte-identical to baseline (no surgery applied)
```

**未开始 RSSF re-pose，未进入 Stage 4B。等待 Human Review。**

**文档状态：`READY_FOR_HUMAN_REVIEW`**
