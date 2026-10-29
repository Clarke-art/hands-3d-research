# STAGE 4A · CMC LOCALITY REFINEMENT — R1
## `STAGE4A_CMC_LOCALITY_REFINEMENT_R1`

> `production_spec/stage4_blender/stage4a/THUMB_CMC_LOCALITY_REFINEMENT_REPORT_R1.md`
> 运行时：`D:\Blender\blender.exe` **Blender 5.1.2**（build `ec6e62d40fa9`）
> 输入评审结论：`STAGE4A = REVISION_REQUIRED`；`CON_2_THUMB_CMC_TOPOLOGY = NEEDS_REVISION`
> 本轮范围：**只修 THUMB CMC**。未重做其他指 topology，未 re-pose，未 Rig，未进入 Stage 4B。
> 日期：2026-09-28

---

## 0. 结论（先说结果）

> ## ❌ `STAGE4A_CMC_LOCALITY_REFINEMENT = FAILED`
>
> ```
> CON_2_THUMB_CMC_TOPOLOGY = NEEDS_REVISION       （未能通过）
> CON_1_MCP_TOPOLOGY       = PASS                 （保持不变）
> ASSET_FRAME_NORMALIZATION= PASS                 （保持不变）
> CON_3_POLE_AUDIT         = PROVISIONAL_PASS     （CMC 侧复核见 §7）
> STAGE4A                  = REVISION_REQUIRED
> ```

**评审意见被完整证实，并且找到了根因**：不是插入方法的问题，而是**该资产的 thenar 拓扑中根本不存在位于 CMC 处的局部环状边环**。
本轮穷举了 CMC 邻域内**全部 19 条拓扑边环**，其中真正的近圆环只出现在 **轴向 +24 … +48 mm**（掌骨中段/拇指 MCP 处），
**±12 mm CMC 窗口内一条都没有**。

**因此我没有交出一个"看起来通过"的模型。** `RIGHT_HAND_ENGINEERING_STAGE4A.blend` **原样未改**（sha256 与评审前一致），
all-quad 状态未被破坏。下面是完整证据与所需手术的精确规格。

---

## 1. 输入与"保持不变"的部分

| 项 | 值 |
| --- | --- |
| 基准 | `RIGHT_HAND_ENGINEERING_STAGE4A.blend` |
| sha256（本轮前后） | `5f69d1ca4b5a70f4f41d70710d6d8ed9b6ba6c4052a70d4de7c429a5b7bcbf40` **未变** |
| `STAGE2_FROZEN_BOOTSTRAP_INPUT` | 仍 `8fa9a549…05ef83`，byte-unchanged |
| 流水线可复现性 | `scripts/stage4a_engineer.py` 重跑 = **逐字节复现**同一 sha256 ✅ |

保留（未触碰）：canonical frame normalization、MCP/PIP/DIP topology、100% quad、
其他指拓扑、已完成的轻微 pole lateralisation（`max_displacement_mm = 0.166`）。

---

## 2. 问题确认：实际轴向审计

轴 = 第一掌骨轴（过拇指指尖与中段指体质心，锚定在实测拇指根部 = CMC 旋转中心）。
**TARGET_OFFSET 与 ACTUAL_VERTEX_AXIAL_POSITIONS 明确区分**（下表右列全是实测顶点位置）。

| loop | TARGET_OFFSET | ACTUAL_MIN | ACTUAL_MAX | **ACTUAL_SPAN** | MEDIAN | STDDEV | ±12mm 内 | ±18mm 内 | 最大离群 | closed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | −1 mm | −48.81 | +17.83 | **66.64 mm** | −1.01 | 20.33 | 42 % | 55 % | 48.81 | ✅ |
| 2 | +1 mm | −49.77 | +17.28 | **67.06 mm** | +0.99 | 20.49 | 47 % | 53 % | 49.77 | ✅ |
| 3 | +3 mm | −47.85 | +18.42 | **66.27 mm** | +2.99 | 20.18 | 48 % | 52 % | 47.85 | ✅ |

```
worst span = 67.06 mm     mean span = 66.66 mm
AXIAL_STDDEV ≈ 20 mm      最大离群 ≈ 50 mm
```

**结论**：三条 loop **确实是闭合的拓扑环、确实 all-quad**，但**每条的轴向跨度 66–67 mm**，
远超评审设定的 40 mm 上限；`stddev ≈ 20 mm` 说明它们不是"围着一个水平的环"，
而是沿掌骨轴铺开的一条螺旋带。**337–338° 的角度覆盖率确实是假阳性**——它只说明"绕了一圈"，
完全不能说明"局部"。

---

## 3. 根因（本轮最关键的技术发现）

穷举法：以 CMC 邻域内 **1130 条候选种子边**各自做一次确定性拓扑边环行走，
去重后得到 **19 条不同的环**：

| 环边数 | 轴向跨度 | 轴向范围 (mm) | 环绕最大角隙 | 判读 |
| --- | --- | --- | --- | --- |
| 16 | **6.01 mm** | +33.5 … +39.5 | 31.3° | ✅ 真正近圆局部环 |
| 16 | **6.50 mm** | +37.3 … +43.8 | 29.2° | ✅ |
| 16 | **7.00 mm** | +29.4 … +36.4 | 33.8° | ✅ |
| 16 | **7.22 mm** | +41.2 … +48.4 | 26.5° | ✅ |
| 16 | **9.18 mm** | +24.6 … +33.8 | 35.9° | ✅ |
| 44 | 44.60 mm | −81.4 … −36.8 | 26.1° | ❌ 远离 CMC |
| 52 ×6 | 65.5–69.9 mm | 跨掌部 | 300–312° | ❌ 即当前三条 loop 的家族 |
| 60 | 69.47 mm | −46.9 … +22.6 | 22.5° | ❌ |

**读法**：能"围住一根管子"的近圆环（16 边、跨度 6–9 mm）**只存在于轴向 +24 … +48 mm**，
即掌骨中段到拇指 MCP 之间；**+24 mm 以近（含整个 ±12 mm 的 CMC 窗口）不存在任何近圆环**。
CMC 处唯一能"绕一圈"的拓扑边环就是那条跨度 66 mm 的螺旋带。

**物理原因**：拇指掌骨自 thenar 体量内长出，thenar 的 quad 流向**绕掌骨基底呈螺旋**，
所以沿既有流向走出来的边环必然一边绕行一边沿轴漂移。这不是插入方法选错，
而是**既有拓扑不具备承载局部 CMC collar 的结构**。

---

## 4. 本轮尝试过的五条路（全部有实测记录）

| # | 方法 | 结果 | 实测 |
| --- | --- | --- | --- |
| 1 | 局部 thenar 带 re-grid（删面带 + 重建） | ❌ 不可行 | 该带是**矩形（带缝）而非环带**：边界只有 1 条闭合环（52–92 边，D/P 各 23 边 + 两条缝 2/4 边）。缝合后端墙需要 D/P 链等长且缝内顶点数匹配；最佳参数 S=11 mm / R=26 mm 下缝内顶点为 1 与 3（非 0 与 2），三条中间环时两端墙均为**奇数环**，无法全 quad 闭合 |
| 2 | 圆柱限定的平面切割 | ❌ 破 all-quad | 轴向跨度 **0.00 mm（完全共面，方向完美）**，曲面闭合、无非流形、无边界；但**扭曲四边形被平面切角**产生 **26–32 个三角 + 26–34 个五边形**；角切修复（dissolve+connect）无效，因为三角与五边形**并不共享边** |
| 3 | **测地环带（围绕 CMC 的等测地环）** | ⚠ 部分成功 | 这是唯一能得到**真环带**的结构（g∈[8,22] mm 有 2 条闭合边界环）。沿其等值线插环 → **新环是闭合的**（每个新顶点恰好 2 条环内邻边），轴向跨度 **26.0 mm**（比 66 mm 改善 60%）——**但同样残留约 20 三角 + 20 五边形**，破 all-quad |
| 4 | 把 loop 顶点直接迭代投影到目标平面 + 邻域松弛 | ❌ 有损 | 漂移部分需要最大 ~48 mm 位移，会明显改变 thenar 体积，违反形状保护 |
| 5 | 沿指轴把核心极点拖出（CON-3 遗留实验） | ❌ 已否决并回滚 | 见 `JOINT_POLE_AUDIT.json`，累积 ~17 mm 畸变且分类不消 |

**方法 3 是本轮最有价值的中间成果**：它证明"局部闭合环"在**几何上**可造（26 mm 跨度、闭合），
代价是 40 个非四边形面。

---

## 5. 形状保护（评审 §7）

以**官方 L1（canonical 帧）表面**为基准，用 BVH 量测三条 loop 顶点对基准面的距离：

| 量 | 值 |
| --- | --- |
| `MAX_SURFACE_DEVIATION_MM` | **5.286 mm** |
| `P95_SURFACE_DEVIATION_MM` | **3.789 mm** |

`RIGHT_HAND_ENGINEERING_STAGE4A.blend` 的既有顶点**本轮一个都没有移动**（该文件未改），
上表量的是当初插入 loop 时投影造成的偏差。thenar 体积未被改变。

---

## 6. CMC 极点审计（评审 §8）

按评审要求的三个类别重新输出（`CMC_POLE_AUDIT.json`）：

| 类别 | 数量 | 判读 |
| --- | --- | --- |
| **`CMC_CORE_POLES`**（弯曲核心内，±6 mm） | **0** | ✅ 无 |
| **`CMC_FLEXION_MIDLINE_POLES`**（屈曲中线上） | **4** | ⚠ 全部位于轴向 +7.8 … +15.4 mm，**在核心窗口之外** |
| **`CMC_OPPOSITION_PATH_POLES`**（对掌主路径：掌侧 62° 且桡侧 75° 内） | **0** | ✅ 无 |

**判读**：CMC 弯曲/对掌的高应变主路径上**没有危险 pole**；4 个中线 pole 都在核心窗口外，
不参与 CMC 的屈曲/对掌加载。因此 CMC 侧的极点风险**不是**本轮未通过的原因。

---

## 7. 评审 §9 的 JSON 文案修正（已完成）

| 项 | 内容 |
| --- | --- |
| 文件 | `JOINT_POLE_AUDIT.json` |
| 原错误表述 | "the maximum displacement was 5 mm" |
| **更正后表述** | "ACTUAL maximum displacement = **0.166 mm**. The 5 mm figure is the ALLOWED CAP (the per-move limit), **NOT** the achieved displacement" |
| 机器字段 | `max_displacement_mm = 0.166`（实际值，未改）+ 新增 `cap_displacement_mm = 5.0` |
| 留痕 | 新增 `wording_correction` 块，记录更正时间、原句、新句与问题定性 |

Stage 4A 尚未冻结，故按评审授权在此阶段数据文件内直接修正。

---

## 8. 证据清单（新增）

| 文件 | 内容 |
| --- | --- |
| `THUMB_CMC_LOCALITY_REFINEMENT_REPORT_R1.md` | 本报告 |
| **`renders/THUMB_CMC_LOCALITY_REVIEW.png`** | **专为人审做的 CMC 局部图**：只显示 CMC/thenar，三条 loop 分别高亮（红/蓝/绿），橙球 = CMC 旋转中心，黑线 = 第一掌骨轴，两条紫线 = ±12 mm 形变窗口边界。**可一眼看出三条 loop 在 CMC 处折过窗口后沿掌骨方向长距离延伸** |
| **`renders/THUMB_CMC_LOCALITY_SIDE.png`** | 侧向视图，直接读出三条 loop 沿掌骨轴的实际位置（大幅越过 ±12 mm 窗口，一直延伸到腕部附近） |
| `renders/THUMB_CMC_LOCALITY_REVIEW_loops_only.png` | 同上但隐藏手体，只留三条 loop + 轴 + 窗口 |
| `CMC_AXIAL_LOCALITY_AUDIT.json` | §2 全部轴向实测（含 `ACTUAL_*`、median、stddev、±12/±18 比例、离群、表面偏差） |
| `CMC_POLE_AUDIT.json` | §6 三类极点逐点数据 |
| `scripts/stage4a_cmc_locality.py` · `stage4a_cmc_locality_render.py` · `stage4a_cmc_pole_audit.py` | 本轮新增脚本，可复现 |

---

## 9. 通过 CON-2 所需的精确手术规格（交给人工/CAD 环节）

自动化操作无法完成，但问题已被完全定位。需要的是一次**人工 thenar 局部重布线**：

1. **手术区域**：围绕第一掌骨轴、轴向 −15 … +20 mm、半径 ≤ 27 mm 的 thenar 带
   （该带当前是"矩形+缝"结构，缝位于深掌侧 r > 26 mm 处，缝两侧各 2 / 4 个顶点）。
2. **目标**：把该带的 quad 流向从"绕掌骨螺旋"改为"沿掌骨轴向 + 环向正交"，
   使带宽内出现 **3 条与掌骨轴垂直、闭合、彼此间距 6–8 mm 的环**。
3. **缝处理**：必须把缝闭合（把两侧顶点按环向一一对应缝合），
   或改用跨越深掌侧的环向桥接，使环能整圈闭合。
4. **必须保持**：全 quad、无新增 "dangerous pole"（CMC 核心 / 对掌主路径）、
   第一指蹼转接（`[1.443781, 0.001022, 0.457045]`）、thenar 体积、
   表面偏差尽量小（建议 < 1 mm）。
5. **验收**：按 §2 的审计重测，要求 `ACTUAL_AXIAL_SPAN ≤ 20 mm`，
   `±12 mm 内顶点比例 ≥ 0.8`，且 all-quad。

> 已证明的可用起点：**测地环带法**（方法 3）已能给出 26 mm 跨度的闭合环，
> 只是残留 20 三角 + 20 五边形。人工/半自动环节若从该结果出发做局部清理，代价最小。

---

## 10. 最终状态

```
STAGE4A_CMC_LOCALITY_REFINEMENT = FAILED

CON_2_THUMB_CMC_TOPOLOGY   = NEEDS_REVISION
CON_1_MCP_TOPOLOGY         = PASS
ASSET_FRAME_NORMALIZATION  = PASS
CANONICAL_FRAME_VALIDATION = PASS
CON_3_POLE_AUDIT           = PROVISIONAL_PASS

DEFORMATION_TOPOLOGY_READY_FOR_RSSF = NO

STAGE4A = REVISION_REQUIRED
RIGHT_HAND_ENGINEERING_STAGE4A = READY_FOR_HUMAN_REVIEW
```

**未开始 RSSF re-pose，未进入 Stage 4B。等待 Human Review。**

**文档状态：`READY_FOR_HUMAN_REVIEW`**
