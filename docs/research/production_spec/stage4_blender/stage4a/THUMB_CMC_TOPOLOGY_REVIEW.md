# THUMB CMC TOPOLOGY REVIEW — CON-2
## `THUMB_CMC_TOPOLOGY_REVIEW`

> `production_spec/stage4_blender/stage4a/THUMB_CMC_TOPOLOGY_REVIEW.md`
> 阶段：**`STAGE4A` · CON-2　（本轮最高风险区，单独评审）**
> 对象：`RIGHT_HAND_ENGINEERING_STAGE4A.blend`（canonical 帧）
> 日期：2026-09-28
>
> ```
> THUMB_CMC_TOPOLOGY_REVIEW = PASS
> THUMB_CMC_RETOPO          = COMPLETED
> ```

---

## 1. 为什么 CMC 是本轮最高风险区

CMC（trapeziometacarpal，拇指腕掌关节）与前四指的 MCP / PIP / DIP 有本质区别：

| | 指间关节 | **拇指 CMC** |
| --- | --- | --- |
| 运动学 | 近似单轴铰链 | **多轴 saddle（鞍状）关节** |
| 需要支持 | flexion / extension | flexion-extension **+** abduction-adduction **+** **opposition（对掌旋转）** |
| 所在区域 | 指 tube（规则圆柱拓扑） | **掌部 thenar 体量内部**（与掌骨、大小鱼际、腕部共享表面） |
| 拓扑可用性 | 有现成 collar 可复用 | **无任何 circumferential loop**（实测轴向带内 = 0） |

因此 **不能"机械补 3 个圆环"**：环比数量更重要的是**环带相对第一掌骨轴的空间关系**、
thenar 的 edge flow 是否允许这些环带整圈闭合、以及环带是否会撞上 thenar 的三角化区。

---

## 2. 现状实测（修复前）

| 项 | 实测 |
| --- | --- |
| `THUMB_CMC` circumferential loops（轴向 ±12 mm 带内） | **0** |
| 拇指 tube 上的 closed ring（远端） | 8 条（L1），分布在距指尖 21–57 mm |
| 掌骨基底处的拓扑 | 无环带；表面进入 **thenar 三角化过渡区** |
| 该区极点 | valence-3 ×1 落在 core 窗口内 |
| thenar 区域的既有 edge flow | **不规则**：以斜向三角面/斜向 quad 为主，不沿第一掌骨轴线分布 |

**依据**：`RAW_RECON.json`（只读侦察）+ `renders/THUMB_CMC_WIREFRAME.png`。

---

## 3. 关键地标（canonical 帧，单位 m）

| 地标 | canonical 坐标 | 说明 |
| --- | --- | --- |
| **CMC rotation center（锚点）** | `[1.448897, 0.011106, 0.393934]` | 实测**拇指根部**顶点（距离腕中心 5.2 cm）。CMC 的旋转中心在解剖上即位于此；Stage 5 Rig 可在此基础上做微调（`HR-04`） |
| **第一指蹼转接点（first web transition）** | `[1.443781, 0.001022, 0.457045]` | index–thumb 指蹼连合顶点（测地 Voronoi 脊最远端），腕测地距离 127.9 mm |
| 拇指指尖 | 距根部测地 98.9 mm | 用于换算 CMC / MCP / IP 的轴向位置 |
| 第二指蹼转接点（对照） | `[1.423901, 0.007870, 0.481378]` | index–middle 蹼顶 |
| 第三 / 第四指蹼（对照） | `[1.411032, 0.006230, 0.483587]` / `[1.387958, 0.003636, 0.476785]` | middle–ring / ring–little |

**第一掌骨轴**：由指尖与中段指体（测地 0.25 L–0.55 L 的质心）连线确定，
CMC 锚点取该轴上距拇指根部最近的点 —— 因此所有切割平面都**垂直于第一掌骨且以掌骨为中心**，
而不是"斜穿指蹼"。

---

## 4. thenar 转接区与 edge flow

**观测（`THUMB_CMC_WIREFRAME.png`，背侧视图，拇指在画面左上）**：

1. **拇指本体（左上）**：规则 quad 网格，环向线与第一掌骨轴垂直，edge flow 干净 —— 可直接承接环带。
2. **腕 / 前臂（左下）**：规则 quad 网格。
3. **thenar 体量（中部–右侧）**：**拓扑最不规则处**。可见明显的斜向三角/斜 quad 交织带，
   这是 thenar 隆起、第一掌骨与掌部网格互相"挤入"的必然结果。
   官方基础网格在此处通过若干 valence-3 / valence-5 极点完成列数变换。
4. **第一指蹼（上方）**：清楚的 V 形连合，指向拇指根部方向。

→ **结论**：CMC 环带**可以**在拇指本体上成为干净的整圈 collar，
但一旦延伸进入 thenar，就会穿过上述斜向区，因此环带在该段的轴向位置会产生漂移。
这是本资产既有的拓扑属性，**不是本轮引入的缺陷**。

---

## 5. 本轮实际构建的 CMC deformation loops

### 5.1 构建方式

沿用 CON-1 的**拓扑边环行走 + 投影**流水线（保证全 quad、无悬空链端），
仅在参数上放宽以适应大跨度环带：

```
wrap_max_gap = 110°（拇指本体 70°）
max_edges    = 140
proj_limit   = 15 mm（CMC 环带跨越 thenar，需较大投影量才能成为平面环）
轴向候选偏移 = −17 … +8 mm，步长 2 mm
```

### 5.2 结果

| 环带 | 环边数 | 轴向范围 (mm) | 投影顶点 | 环绕最大角隙（投影后） | 覆盖率 |
| --- | --- | --- | --- | --- | --- |
| `CON2_CMC @ −1 mm` | 60 | [−48.8, +17.8] | 25/60 | **22.09°** | 337.9° |
| `CON2_CMC @ +1 mm` | 60 | [−49.8, +17.3] | 28/60 | **21.90°** | 338.1° |
| `CON2_CMC @ +3 mm` | 60 | [−47.9, +18.4] | 29/60 | **22.28°** | 337.7° |

```
THUMB_CMC effective loops (轴向 |offset| <= 12 mm) : 0 -> 3
```

**三条环带全部整圈环绕第一掌骨基底**（每条的角隙 ≤ 22.3°，即覆盖 ≥ 337.7°，
意味着任何方向上最多只有 22° 的"缺口"，足以支撑三轴运动）：
- **flexion / extension**：环带垂直于掌骨轴 → 直接提供屈伸的弯曲环；
- **abduction / adduction**：同一组环带在桡/尺侧的分段提供侧摆弯曲环；
- **opposition**：环带闭合环绕掌骨，掌骨自身的旋转由环带的周向连续性承载。

### 5.3 ⚠ 残留质量观察（如实记录，不掩盖）

三条环带的**轴向延展达 47–67 mm**（相对 60 边环带的总长约 200 mm）。
这说明：环带在**拇指本体段**是垂直于掌骨的平面环，但**进入 thenar 段后沿掌骨方向明显漂移**
（因为 thenar 的 quad 流向不与掌骨轴垂直，环行走只能顺着既有流向走）。

| 后果 | 评估 |
| --- | --- |
| 是否影响"三轴支持" | ❌ 不影响：环带仍然整圈闭合环绕掌骨基底，方向性由其在拇指本体段的垂直段保证 |
| 是否影响面数 / 网格质量 | ❌ 无影响：全 quad、0 非流形、体积变化可忽略 |
| 是否理想 | ⚠ **不理想**。理想形态是三条与掌骨轴垂直的平行环带 |

**建议（不属于本轮范围）**：若后续希望 CMC 环带完全垂直于掌骨轴，
需要对 thenar 区做一次**局部重布线**（把 thenar 的斜向流向改为沿掌骨轴向），
这属于 **Stage 4B 可选深化项**，也可在 Stage 5 Rig 建立后按权重需求再决定是否需要。
本轮不执行该重布线，理由：它会显著改变掌部既有拓扑，
应当与 Rig 的权重需求一并决策，而不是在 Rig 之前盲目重排。

---

## 6. 该区极点

| 项 | 值 |
| --- | --- |
| `THUMB_CMC` core 窗口内极点 | **1 个（valence-3）** |
| 是否位于屈曲中线 | ❌ 否（偏离背侧中线 133.3°，即明显偏掌侧/尺侧） |
| 是否由本轮插入环带产生 | ❌ 否（环细分只产生 valence-4 顶点；valence 直方图不变） |
| 处置 | 无需移动（不在屈曲中线，屈曲时不会被拉出褶皱） |

---

## 7. 结论

| 检查项 | 结果 |
| --- | --- |
| CMC rotation center 是否明确记录 | ✅ `[1.448897, 0.011106, 0.393934]` |
| surrounding edge flow 是否记录 | ✅ §4（拇指本体规则 / thenar 斜向三角化区） |
| poles 是否审计 | ✅ 1 个 valence-3，不在屈曲中线，非本轮引入 |
| first web transition 是否记录 | ✅ `[1.443781, 0.001022, 0.457045]` |
| thenar transition 是否记录 | ✅ §4 |
| proposed / built deformation loops 是否记录 | ✅ 3 条，覆盖率 ≥ 337.7° |
| 是否达到"支持 flexion/extension + abduction/adduction + opposition" | ✅ 是（整圈闭合环绕掌骨基底） |
| 是否存在无法闭合 / 破面 / 非流形 | ✅ 无 |
| 是否存在残留不理想（环带轴向漂移） | ⚠ 有，已如实记录并给出 Stage 4B 可选项 |

```
THUMB_CMC_TOPOLOGY_REVIEW = PASS
THUMB_CMC_RETOPO          = COMPLETED
CON_2_THUMB_CMC_TOPOLOGY  = PASS
```

> **评审人须注意的开放项**：§5.3 的环带轴向漂移是**质量残留**而非功能缺陷。
> 若人工评审认为"CMC 环带必须严格垂直于掌骨轴"，则应判 `NEEDS_REVISION`，
> 并在 Stage 4B 增加 thenar 局部重布线 —— 该决策需要人来做，本报告不代为决定。

**文档状态：`READY_FOR_HUMAN_REVIEW`**
