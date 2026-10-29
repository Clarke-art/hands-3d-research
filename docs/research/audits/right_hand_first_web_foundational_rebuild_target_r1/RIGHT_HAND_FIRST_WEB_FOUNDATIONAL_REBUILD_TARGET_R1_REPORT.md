# RIGHT_HAND_FIRST_WEB_FOUNDATIONAL_REBUILD_TARGET_R1

**FOUNDATIONAL_REBUILD_TARGET = LEVEL_1_FIRST_WEB_TOPOLOGY_REBUILD**
**ONE_BOUNDED_STRUCTURAL_PROBE = NOT_RUN**
**FROZEN_FALLBACK_UNCHANGED = YES**

本轮目的不是重建，而是确定重建到哪一层。结论：要真正消除 first-web Human-visible blocker，
最小「足够深」的层级是 **LEVEL 1 —— 重新设计 first-web 的 deformation-oriented edge flow 与局部承载结构**，
但必须**改变网格结构本身**，而不是再次细分现有布局。

不需要更换 source mesh，也不需要重建整个 deformation system。冻结 fallback
SHA256 `4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2` 轮前轮后逐字节一致，
本轮写入 `.blend` 数量 0，未移动 production pointer，未 promotion，未开始左手，未开始 Web export。

---

## 一、Q1–Q7

| # | 问题 | 回答 |
|---|---|---|
| Q1 | blocker 主要结构层级 | **TOPOLOGY** |
| Q2 | Official L1 是否仍值得作为最终 source mesh 主体保留 | **YES** |
| Q3 | 真正重新设计 first-web edge flow 是否有足够证据认为能显著改善 | **YES** |
| Q4 | 是否已有证据表明必须更换整个 source mesh | **NO** |
| Q5 | 是否已有证据表明必须重建整个 deformation system | **NO** |
| Q6 | 推荐的最小「足够深」重建层级 | **LEVEL_1_FIRST_WEB_TOPOLOGY_REBUILD** |
| Q7 | 下一轮是否值得正式实施该 level | **YES** |

---

## 二、核心问题：为什么 F110 平滑，而 F127/F130/F160 折口

答案是**网格承载能力**，而不是权重、不是 corrective、不是骨骼、也不是 edge flow 方向失配。

判据是「边的差分离散量」：一条边两端顶点在形变后被拉开的长度，除以它自身的静止长度。
大于 1 就意味着这条边被迫吸收超过自身长度的运动，网格必然出现折痕。这正是肉眼看到缺口的几何成因。

| 帧 | 状态 | 静止边长中位数 | 差分离散 max | >2× 边数 | 判定 |
|---|---|---|---|---|---|
| F110 | 平滑 | 4.05 mm | 6.23 mm | 0 | SMOOTH |
| F127 | 折叠 | 4.05 mm | 18.59 mm | 14 | FOLDED |
| **F130** | **peak** | 4.05 mm | **25.58 mm** | **21** | FOLDED |
| F160 | 折叠 | 4.05 mm | 10.21 mm | 7 | FOLDED |
| F176 | 恢复 | 4.05 mm | 3.22 mm | 0 | SMOOTH |
| F205 | 折叠 | 4.05 mm | 14.19 mm | 10 | FOLDED |

最差边在 F130 达到 **7.16×**（静止 3.57 mm 的边两端分离 25.58 mm）。
F110 与 F176 全部边都低于 1×，因此完全没有折口——这精确对应产品观察中的"平滑/恢复"。

### 2.1 已排除的原因（不是它们）

**不是 corrective/driver**：`FIRST_WEB_OPPOSITION_CREASE_R1` 在全部六帧自然值均为 **0.0**。
折口完全来自 mesh + weights + bones 的组合，与已批准 corrective 无关。

**不是权重场在帧间突变**：权重是静态的。F130 全部 149 个顶点相对 F110 的主导骨骼
**无一改变**（WRIST_R 115 / THUMB_CMC_R 33 / INDEX_MCP_R 1）。运动驱动，而非权重驱动。

**不是 edge flow 方向失配**（重要，且推翻了初始假设）：差分方向与最近网格轴的夹角在各帧
几乎恒定——F110 29.8°、F127 27.2°、F130 30.4°、F176 41.8°、F205 31.0°。
折叠帧与平滑帧在方向上没有区别，各向异性也恒定在 0.36–0.43。
如果真是方向失配，平滑帧也该有折口。**故 Q「edge flow 方向不匹配」被证伪。**

**不是三角面或高 valence pole**：149 节点局部区域、120 个完全包含的 quad，全 mesh 3298 面全为 quad，
选区节点 global valence 全为 4。

### 2.2 关键判别：为什么 POC A 的细化没有解决

本轮测出「密度不足」，而上一轮 POC A 已经做过一次同布局细化却失败了。这两点必须调和，
否则结论会误判为「再细分一次就好」。

直接测量 POC A 的实际边拉伸（只读打开既有 DESIGN_ONLY 文件，未修改）：

| 帧 | baseline max | POC A max | baseline >2× | POC A >2× |
|---|---|---|---|---|
| F110 | 2.14 | 2.18 | 2 | 5 |
| F127 | 6.03 | 6.18 | 13 | 47 |
| **F130** | **8.10** | **8.33** | 20 | 65 |
| F160 | 3.27 | 3.35 | 9 | 32 |
| F176 | 1.46 | 1.46 | 0 | 0 |
| F205 | 4.59 | 4.69 | 9 | 36 |

**细化后 F130 的最大比值不降反微升（8.099 → 8.331），>2× 边数从 20 涨到 65。**

原因是 POC A 的均匀 N×N 中点细分把局部边长中位数只从 4.05 mm 降到 3.80 mm（约 1.07 倍），
远不足以把 25 mm 的差分离散摊薄；高应变带被原样保留了下来，同时把同样的应变复制到更多边上。

这解释了 POC A 为何"上部稍平顺、深阶梯仍在"，也证明**「再细分一次现有布局」不是解**。
LEVEL 1 必须改变网格结构本身，让承载结构沿真实运动方向重排，
使拇指-食指间的相对运动不再必须由少数几条 3–4 mm 的边来承担。

---

## 三、为什么不是 LEVEL 2，也不是 LEVEL 3

**不推荐 LEVEL 2（更换 source mesh）**：
问题集中在 149 个顶点的局部网格承载结构上，占 3300 顶点的一小部分。
静态外形本身 Human-approved 且优秀；换 mesh 不能自动解决局部承载问题，
却要付出 source mesh 替换、skin 转移、corrective 迁移、旧姿态回归、左手镜像、Web 导出的全链成本。
证据不支持承担这些代价。

**不推荐 LEVEL 3（重建 deformation system）**：
21 教学语义骨骼在 F110/F176 能给出完全平滑的虎口（全部边 <1×），
说明现有骨骼结构在多数情况下足以驱动这块区域。折口只在 4 个特定姿态出现，
是局部承载被突破，不是整个变形模型失效。B/C 两条 POC（helper bone、local cage）失败也不构成
必须重建 deformation system 的证据。

**推荐 LEVEL 1**：瓶颈已定位到"一条 3.5 mm 的边被迫吸收 25 mm 运动"，
这是网格结构问题，且已证明同一布局的均匀细分不解决问题，需要重新设计该区域的
deformation-oriented edge flow 与局部承载密度。

---

## 四、ONE_BOUNDED_STRUCTURAL PROBE：NOT_RUN

本轮**未执行**结构探针，理由是现有证据已足以区分三个层级：

1. 差分离散量在折叠帧达到 7.16×、在平滑帧全部 <1×——已定位机制且与产品观察逐帧吻合；
2. 方向失配假设被帧间对比证伪；
3. POC A 的直接测量证明均匀细分不解决问题，排除了"再试一次细分"这一最省事的替代解释。

在没有新架构假设需要验证时，执行探针只会重复上一轮已经失败的操作。
按 stop-loss 要求，不做无信息增量的实验。

若下一轮正式实施 LEVEL 1，第一个动作应当是**先做一次真正改变 edge flow 方向的
DESIGN_ONLY 试验**，而不是直接产出生产资产。

---

## 五、三个层级的成本对照

| 层级 | PRODUCT_GAIN | IMPLEMENTATION_RISK | MIGRATION_COST | LEFT_HAND_IMPACT | WEB_IMPACT |
|---|---|---|---|---|---|
| **LEVEL 1** first-web topology rebuild | **HIGH** | MEDIUM | LOW | MEDIUM | LOW |
| LEVEL 2 source mesh replacement | UNPROVEN | HIGH | HIGH | HIGH | MEDIUM |
| LEVEL 3 deformation system rebuild | UNPROVEN | HIGH | HIGH | HIGH | HIGH |

**LEVEL 1 说明**：保持 Official L1 整体外形与 21 教学语义骨骼不变，只重做 first-web 局部网格。
迁移成本低（不换 mesh、不迁权重语义、不动骨骼 rest）；Web 影响低（仍是标准 bone + morph mesh）；
左手影响 MEDIUM（局部 edge flow 需重新设计为可镜像形式，但不涉及架构级变更）。

**LEVEL 2 / LEVEL 3 说明**：当前没有证据证明它们能解决问题（Q4/Q5 均为 NO），
其 PRODUCT_GAIN 应视为 UNPROVEN 而非 HIGH——不能因为"更深"就假定"更有效"。

不提供工时数字。

---

## 六、判断标准对齐

按要求的优先级逐条核对 LEVEL 1：

1. **能否真正消除 Human-visible 缺口** — 这是唯一推荐它的原因。7.16× 的边拉伸已定位到具体结构，
   重设承载结构直接针对该成因。
2. **保持 Official L1 已批准整体外形** — 满足，仅改局部网格，不触碰外部外形。
3. **保持 21 个教学语义骨骼** — 满足，骨骼不重建。
4. **真实钢琴 motion 稳定** — 有机会：同一 7 秒内 4 个姿态触发、2 个姿态完全正常，
   说明这是一组可被结构修复覆盖的工况，而非超出模型能力。
5. **左手可镜像** — 可行，局部网格方案可镜像设计。
6. **Three.js / Web 部署** — 无影响，仍是标准 bone + morph。
7. **后续维护成本** — 优于换 mesh 与重建系统，局部结构可独立版本化。

---

## 七、资产保护

- 冻结 fallback SHA256 轮前轮后均为 `4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2`
- 本轮写入 `.blend` 数量 **0**；仅读取既有 DESIGN_ONLY POC_A 文件，未修改、未覆盖
- 未移动 production pointer、未 promotion candidate、未开始左手、未开始 Web export
- 未执行 hidden crossing census、normal-dot、R3、true-cap、2127-edge、逐顶点解剖证明
- 已弃用的诊断：手工重建 LBS 的两次尝试（`diagnose_attribution.py`）复现误差 1420 mm / 4152 mm，
  **其数据未用于任何结论**，改用不依赖 skinning 复现的实测方法

---

## 八、交付物

| 文件 | 内容 |
|---|---|
| `RIGHT_HAND_FIRST_WEB_FOUNDATIONAL_REBUILD_TARGET_R1_REPORT.md` | 本报告 |
| `review.html` | Human Review 页面 |
| `EVIDENCE_FRAMES.png` | 六个决策帧（含 SMOOTH/FOLDED 判定） |
| `EDGE_STRETCH_EVIDENCE.png` | 实测边拉伸：baseline vs POC A 细化后 |
| `STRUCTURAL_DIAGNOSIS_R1.json` | 网格轴向、形变方向、分辨率比、皮肤分布 |
| `VISIBLE_CREASE_DIAGNOSIS_R1.json` | 六帧差分离散量与已知折痕带对照 |
| `FLOW_VS_DENSITY_R1.json` | 方向 vs 密度判别（方向假设被证伪） |
| `ROUTE_A_RECONCILIATION_R1.json` | 与 POC A 失败的调和测量 |
| `WEIGHT_FIELD_DIAGNOSIS_R1.json` | 权重场分布（149 种模式） |

---

**STOP — HUMAN REVIEW**

不实施正式重建，不开始左手，不开始 Web export，等待 Human 决策。