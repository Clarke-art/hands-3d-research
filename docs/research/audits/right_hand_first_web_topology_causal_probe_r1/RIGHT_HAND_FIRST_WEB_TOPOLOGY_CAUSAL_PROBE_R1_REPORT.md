# RIGHT_HAND_FIRST_WEB_TOPOLOGY_CAUSAL_PROBE_R1

**FINAL_CAUSAL_RESULT = LEVEL_1_NOT_SUPPORTED**
**F130_HUMAN_VISIBLE_IMPROVEMENT = NO**
**WEIGHT_FIELD_SEMANTICS_PRESERVED = YES**
**FROZEN_FALLBACK_UNCHANGED = YES**

本轮只做一件事：用一个真正改变 first-web 局部承载结构（不是细分）的 DESIGN_ONLY 候选，
在保持骨骼 / Action / retarget / motion sample / weight 语义 / corrective 逻辑不变的条件下，
检查 first-web 的 Human-visible fold 是否出现明显的结构性改善。

答案是不出现。而且本轮给出了比"试了一次没变好"更强的证据：**在保持静态外形与 weight 语义的
前提下，任何 topology 都不可能改变这块区域的形变场**，因此 LEVEL 1 不可能单独解决这个 blocker。

---

## 一、Q1–Q7

| # | 问题 | 回答 |
|---|---|---|
| Q1 | candidate 是否真正改变了局部 topology / load path，而不是简单 subdivide？ | **YES** |
| Q2 | WEIGHT_FIELD_SEMANTICS_PRESERVED？ | **YES** |
| Q3 | F130 Human-visible main fold 是否明显改善？ | **NO** |
| Q4 | F127 / F160 / F205 是否表现出一致改善？ | **NO** |
| Q5 | F110 / F176 是否保持平滑，且无明显新 defect？ | **YES** |
| Q6 | 改善是否来自 topology 本身，而非新 weights / corrective / helper / cage / DQS？ | **YES**（本轮没有用它们中的任何一个；但并没有产生实质改善，见 Q3/Q4） |
| Q7 | 最终结论 | **LEVEL_1_NOT_SUPPORTED** |

---

## 二、candidate 到底改了什么（Q1 的证据）

`DR-1 FIRST_WEB_GRADED_STRUCTURED_BRIDGE_R1`，候选文件
`RIGHT_HAND_FIRST_WEB_TOPOLOGY_PROBE_CANDIDATE_R1.blend`
SHA256 `373b8516fe45d8f9f83e752eeb3607e7bfd7e3135ed8467ad22272a99ac355bb`。

- ROI = 批准的 149 顶点 first-web patch 向外扩 2 圈 → **234 顶点 / 198 面 / 边界环 70**（欧拉数 1，单环圆盘）。
  即**原有的 patch 内边界线被整体溶解后重建**，不是把旧布局再切细。
- ROI 内部重建为**一个 17 × 18 的结构化四边形网格**（272 个新内部节点），内部节点 valence 全为 4。
- 四个网格角点由 ROI 边界自身的弦长分布决定，**条带走向不复刻旧布局**。
- 采样间距按**六帧实测形变载荷分级**（`GRADE_BLEND=0.55`）：高载荷带获得更多支撑行，低载荷带更少。

**决定性事实：新 ROI 边集与旧 ROI 边集的交集 = 0 条边**（旧 431 条 / 新 647 条，共享 0 条）。
这不是"看起来更密"，是局部承载结构被换掉了。

---

## 三、实验控制（Q2 / Q6 的证据）

| 控制项 | 状态 |
|---|---|
| 21 教学骨骼 / rest transforms / Action / retarget mapping / motion sample | 未改动，Action payload SHA 与本轮批准值一致 |
| motion | 仍为 `PIANOVAM_PHYSICAL_RIGHT_AXIS_CORRECTED_R1`，11.5–18.5 s，六决策帧 |
| 新顶点的静止位置 | 在原始 PL 曲面上做重心插值 → **保留顶点最大偏移 0.0 mm**；整体静止偏差 2.6 × 10⁻⁴ mm |
| 新顶点的 skin weights | 原始权重场的重心插值（mean-value 参数域内定位），**未做任何美术刷权重**；权重和 ∈ [0.99999992, 1.00000007]，无零权重顶点 |
| corrective | 唯一 approved corrective `FIRST_WEB_OPPOSITION_CREASE_R1` 按同一重心插值迁移，driver 表达式与变量逐字复制；**六决策帧自然值 baseline 与 probe 均为 0.0** |
| helper bone / cage / DQS / 新 corrective | 全部未使用；保持 LBS |
| 参数域有效性 | 顶点域 0 个翻转三角形（11 个零面积退化三角形为原网格既有），2D 网格 306 个单元全部正面积 → 候选不会自交 |

说明一处过程细节：在构建会话中，新建 probe shape key 的 driver 值在 F205 曾瞬时读到 0.0913；
**重新只读打开已保存的候选文件后，baseline 与 probe 在六帧上均读到 0.0**（见
`CANDIDATE_VERIFICATION_R1.json`）。该帧 corrective 不参与，结论不受影响。

---

## 四、结果（Q3 / Q4 / Q5）

同相机 / 同姿态 / 同帧 / 中性 Workbench 实体着色，baseline 左、probe 右。

### 4.1 Human-visible（主判据）

- **F130 PEAK：主缺口没有改善。** baseline 是一道粗阶梯状缺口，probe 把同一道缺口解析成一条
  更细、更锐的折线（局部还出现分叉）。两者都明显不自然，probe 说不上更自然。
- F127 / F160 / F205：同样没有出现一致的结构性改善，缺口位置不变。
- F110 / F176：两侧都保持平滑，probe 未引入新的折痕 / bulge / flap。

证据图：`EVIDENCE_F130_BASELINE_VS_PROBE.png`、`EVIDENCE_SIX_FRAMES_BASELINE_VS_PROBE.png`
（均含 x6 放大像素差，可直接看出差异集中在折痕处的法线/着色，而不是整体形状）。

### 4.2 决定性几何证据

在同一个物理区域（原始 149 顶点 first-web，面积 2104.95 mm²）上直接比较两套**形变后曲面**：

| 帧 | probe 顶点到 baseline 曲面最大距离 | 该帧最大差分 strain |
|---|---|---|
| F110 | 0.046 mm | 1.74 |
| F127 | 0.100 mm | 5.20 |
| **F130** | **0.152 mm** | **7.16** |
| F160 | 0.064 mm | 2.86 |
| F176 | 0.038 mm | 0.87 |
| F205 | 0.106 mm | 3.97 |

**F130 的差分约 25.6 mm，而两套曲面相差不到 0.152 mm（0.6%）。**
也就是说：换掉局部承载结构之后，**形变后的曲面几乎就是同一张曲面**。
fold 长在这张曲面上，不长在网格上。渲染上的差别来自法线场离散方式，不是形状被修正。

### 4.3 次级数字（SECONDARY EVIDENCE，不作为 PASS 条件）

| 帧 | baseline max 边长比 | probe max 边长比 | 变化 |
|---|---|---|---|
| F110 | 2.138 | 2.063 | −3.5% |
| F127 | 6.031 | 5.531 | −8.3% |
| **F130** | **8.099** | **7.312** | **−9.7%** |
| F160 | 3.268 | 3.060 | −6.4% |
| F176 | 1.407 | 1.411 | +0.3% |
| F205 | 4.585 | 4.168 | −9.1% |

原始 ">2× 边数" 会随顶点预算变化而失去可比性（probe 在 ROI 内顶点更多），
采样无关的写法（每个采样点 5 mm 半径内最大边长比 > 2× 的采样占比）见
`SAMPLING_ROBUST_METRIC_R1.json`：F130 baseline 15.4% vs probe 29.3% ——
**更细的网格把同一条高应变带解析得更清楚，反而暴露出更多 >2× 采样，而不是更少。**

---

## 五、为什么 LEVEL 1 不可能单独解决（本轮的核心论证）

设点 p 的权重向量为 w(p)，骨骼 b 在该帧的变换为 T_b，则 LBS 形变场为
`X(p) = Σ_b w_b(p) · T_b · p`。

在候选构造中，每个新顶点都取原三角内重心坐标 (λ_i) 的插值：
`p = Σ λ_i p_i`，`w(p) = Σ λ_i w_i`。代入得
`X(p) = Σ_b (Σ_i λ_i w_i,b) T_b (Σ_j λ_j p_j)`
即在**同一 weight 场**下，细分只把同一条形变路径采样得更密。

因此：

- 若 p_A、p_B 之间权重由 w_A 硬变到 w_B，插入中间点只会造出**共线的中间点**，
  把 25 mm 的位移差均摊到更多边上 —— **每条边的比值不变**（这就是 POC A 均匀细分
  F130 max 8.099 → 8.331 不降反升的原因）。
- 本轮不是均匀细分，而是换了条带走向与间距，结果 F130 max 8.099 → 7.312，只降 9.7%，
  仍远离 1×，且形变后曲面与 baseline 相差 0.152 mm。
- 唯一能真正压低这条比值的量是 **∂w/∂p**（权重场的空间梯度）或 **T_b 之间的差异**，
  两者都不属于 topology。

`07_attribution.py` 独立确认了成因：F130 最坏的 8 条边，静止长度 3.4–3.9 mm、形变后 20–29 mm，
两端权重向量 L1 差 0.39–0.57，两端主导骨骼都是 **WRIST_R 与 THUMB_CMC_R 的比例互换**
（例：`WRIST_R 0.45 / THUMB_CMC_R 0.27` 对 `WRIST_R 0.41 / THUMB_CMC_R 0.39`）。
局部差分 strain 与权重 L1 差的相关系数在六帧为 0.53–0.71。

**结论：blocker 写在 skinning / deformation field 上，不写在网格上。**

---

## 六、上一轮 F110 "0 vs 2" 的口径核对（最小解释）

已按最小范围复算，不用展开大型 forensic audit（`ATTRIBUTION_AND_RECONCILIATION_R1.json`）：

F110 在两种 edge subset 下数值完全相同，差别只来自**两个不同的度量定义**：

| edge subset | 度量 | max | >2× |
|---|---|---|---|
| first-web patch 内部边（268） | `‖Δ(边向量) − 静止边向量‖ / ‖静止边向量‖` | 1.742 | **0** |
| first-web patch 内部边（268） | `‖形变后边向量‖ / ‖静止边向量‖` | 2.138 | **2** |
| 全网格边（6596） | 差分 strain | 1.742 | 0 |
| 全网格边（6596） | 边长比 | 2.138 | 2 |

一句话：**0 与 2 不是两套数据，而是同一批边的两种定义 —— "边向量的变化量 / 静止边长"（F110 无一条 >2×）
对比 "形变边长 / 静止边长"（F110 有 2 条 >2×）。** edge subset（local patch vs 全网格）在 F110 不影响结果，
因为极值边本来就落在 patch 内部。

---

## 七、设计层可复用结论（写入项目长期记忆）

1. 在「保持静止外形 + 保持 weight 语义 + 不加 helper/cage/corrective/DQS」的约束下，
   **topology 对 LBS 形变曲面没有自由度**：候选形变面与 baseline 相差 0.152 mm / 25.6 mm 差分。
2. 判"改善"必须用同一物理区域上的**形变后曲面距离**，不能只看 max edge ratio，
   更不能只看渲染像素差（后者主要反映法线场离散方式）。
3. `>2× 边数` 会随顶点预算漂移，跨资产比较必须换算成采样无关的占比或面积密度。
4. 本轮 ROI 内顶点预算 234 → 342（结构化网格的固有结果），不构成"更密所以更好"的解释：
   曲面没有变。

---

## 八、交付物

| 文件 | 内容 |
|---|---|
| `RIGHT_HAND_FIRST_WEB_TOPOLOGY_CAUSAL_PROBE_R1_REPORT.md` | 本报告 |
| `review.html` | Human Review 页面（六帧 × 两视角 A/B/差异） |
| `RIGHT_HAND_FIRST_WEB_TOPOLOGY_PROBE_CANDIDATE_R1.blend` | DESIGN_ONLY 候选（含 baseline 对象 + probe 对象 + Action），不 promotion |
| `EVIDENCE_F130_BASELINE_VS_PROBE.png` | F130 peak：两视角 baseline / probe / x6 差异 |
| `EVIDENCE_SIX_FRAMES_BASELINE_VS_PROBE.png` | 六决策帧 × 两产品视角 baseline 左 / probe 右 |
| `renders/` | 24 张同相机单帧原图（6 帧 × 2 视角 × 2 资产） |
| `CANDIDATE_DESIGN_R1.json` | 候选结构事实（网格、分级、边重叠 0、参数域有效性） |
| `PROBE_MEASUREMENTS_R1.json` | 六帧对照测量（strain、曲面距离、corrective 值、相机） |
| `SAMPLING_ROBUST_METRIC_R1.json` | 采样无关的次级指标复述 |
| `ATTRIBUTION_AND_RECONCILIATION_R1.json` | 成因归因 + F110 口径核对 |
| `CANDIDATE_VERIFICATION_R1.json` | 候选只读复核（驱动一致、权重和、全 quad） |
| `FINAL_ASSET_PROTECTION_R1.json` | 资产保护校验 |
| `01/02/03/06/07/08/09_*.py` | 可复现管线（inspect → build+measure+render → evidence → verify → attribute → protect → robust metric） |

---

## 九、资产保护（Q 的硬性要求）

- 冻结 fallback `production_spec/right_hand_product_baseline_r1/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1.blend`
  SHA256 轮前轮后均为 `4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2`
  → **FROZEN_FALLBACK_UNCHANGED = YES**
- 全部 protected inputs 逐一复算一致（含 approved Action payload 与 motion sample）
- 本轮写入的 `.blend` 只有 1 个，位于本轮 audit 目录内的 DESIGN_ONLY 候选；未写回冻结资产
- **未移动 production pointer、未 promotion、未开始左手、未开始 Web export、未开始正式 topology rebuild**
- 未执行 hidden crossing census / normal-dot / R3 / true-cap 等已停用诊断

---

**STOP — HUMAN REVIEW**

下一轮不应继续 topology iteration。按结论 B，应转入 **SKINNING / DEFORMATION FIELD**
分析，而不是跳 LEVEL 2 / LEVEL 3；直接线索是第五节给出的
F130 高应变带上 `WRIST_R ↔ THUMB_CMC_R` 的过渡带（两端权重 L1 差 0.39–0.57，边静止长度 3.4–3.9 mm）。
