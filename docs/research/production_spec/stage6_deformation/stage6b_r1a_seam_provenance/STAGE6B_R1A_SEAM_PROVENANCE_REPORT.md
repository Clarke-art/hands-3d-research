# STAGE6B_R1A · THUMB|INDEX SEAM TOPOLOGY PROVENANCE AUDIT — REPORT

**轮次**：`STAGE6B_R1A_THUMB_INDEX_SEAM_TOPOLOGY_PROVENANCE_AUDIT`
**性质**：READ-ONLY / FORENSIC / TOPOLOGY PROVENANCE / SEMANTIC CLASSIFICATION（**非修复轮**）
**生成时间**：2026-09-30
**工作区**：`<HANDS_ROOT>`

---

## 0. 一句话结论

> **Stage6B 的 67 条 “THUMB|INDEX seam edges” 不是一条拓扑缝。**
> 其中 **0 条**是真正的拇指/食指跨指边界；**67 / 67** 的两个端点用真实网格测地线判定都落在
> **同一根手指**的表面上（39 条双侧 INDEX，28 条双侧 THUMB）。
> 这 67 条边是 **CC0 手部表面的普通内部边**，被一个**纯空间最近链归属测试**
> 在 **RSSF 绑定姿态把拇指末节与食指 MCP 面片压到 0.25 mm** 的接触带里**贴错了标签**。

`CLASS_C（ANATOMICALLY INVALID CROSS LINK）= 0`
→ **既不是 `SOURCE_ASSET_TOPOLOGY_LIMITATION`，也不是 `STAGE4_TOPOLOGY_INTRODUCED_DEFECT`。**

---

## 1. 冻结输入与无漂移

| 对象 | SHA-256（执行前 = 执行后） |
|---|---|
| Stage5A R2A master | `c4fafc56c591411bb5ddf07bde44b5fcd6e6a9aa5e0d43b22f9734c0884c2845` |
| Stage5B R1B master（ACTIVE production skin master） | `cec5804f1319bf2408fded21a3d0cf8c9f01bf778ae0659c18cf17950b117d10` |
| Stage6A R1A harness | `c4bb74ea116e7352064c26977a509ed1248aacbe734118e5f9c240fa24b1157b` |
| Stage6B R1 harness | `4b6200899fe4d2f5a67e3254aec2a5cb17b734b14acefe381a2ac9c1241f549d` |

全部历史 Stage2 / Stage3 / Stage4 冻结 blend 只读加载，**未修改任何文件**。
本轮只允许：读取 / 分析 / 标记 / 导出 audit / 渲染 diagnostic evidence —— 已严格遵守。

---

## 2. 逐条审计的基础事实（§7 / §8 / §20）

| 事实 | 值 |
|---|---|
| THUMB\|INDEX 归属边界边总数 | **67** |
| 其中是**真实 mesh edge** | **67 / 67** |
| 流形（incident face = 2） | **67 / 67** |
| boundary edge / non-manifold | 0 / 0 |
| bridge-like（边长 > 邻域中位 3×） | **0** |
| near-coincident（非相邻顶点 ≤0.02 mm） | **0** |
| 二面角范围 | 0.68° – 39.22°（全部为光滑同片连接） |
| bind 边长 | min 1.0586 / median 3.8912 / max 9.0456 mm |
| 端点 1-ring 标签 | **全部为混合标签**（典型 2 THUMB + 2 INDEX） |

> **关键**：没有任何一条边是“把两个不该相连的解剖面片直接连起来”的桥。
> 若 67 条边里存在真实跨指连接，其两端测地距必须 ≤ 该边长（≤9 mm）；
> 而**拇指尖到食指尖的网格测地距离 = 201.70 mm** —— 这是正常手部的解剖分离。

### 2.1 为什么是 25 个碎片而不是一条连续边界线

| 指标 | 值 |
|---|---|
| 边界图连通分量 | **25** |
| 顶点数 | 92 |
| 度直方图 | `{1: 54, 2: 34, 3: 4}` |
| 整个 1-ring 都是反标签的端点 | **0 / 134** |
| 不同 1-ring 标签模式数 | 13（主模式 n=21：两侧 1-ring 均为 2+2） |

**解释**：接触带内 THUMB / INDEX 标签是一个**细粒度交错混合场**——
每个端点都有同标签邻居和反标签邻居。这正是“两条候选链距离几乎相等、
最近链测试在整片区域里随机翻面”的特征；因此得到的不是一条 contour，
而是 25 段互不相连的碎片。

---

## 3. 三类（含第四类）判定 —— 决定性判据

**判据 = 真实网格测地线归属**（只用边连通性，与姿态无关）：
以拇指尖 / 食指尖 landmark 顶点为种子，取测地更近者为该顶点的手指归属。

| 类别 | 定义 | 数量 |
|---|---|---|
| **CLASS_A** | ANATOMIC_FIRST_WEB_TRANSITION | **6** |
| **CLASS_B** | SEMANTIC_OWNERSHIP_MISCLASSIFICATION | **61** |
| **CLASS_C** | ANATOMICALLY_INVALID_CROSS_LINK | **0** |
| **CLASS_D** | AMBIGUOUS_REQUIRES_HUMAN_REVIEW | **0** |
| **合计** | | **67** ✅ |

### 3.1 交叉表（决定性）

| 拇指端测地归属 × 食指端测地归属 | 边数 |
|---|---|
| INDEX × INDEX | **39** |
| THUMB × THUMB | **28** |
| THUMB × INDEX（真正跨指） | **0** |

**没有任何一条边跨越两根手指。**

### 3.2 CLASS_A（6 条，`DO_NOT_CUT_CLASS_A`）

全部位于 **`THUMB_BASE_FOLD`**（拇指基底褶皱带）：拇指弧长 55.69 – 67.49 mm
（≤ `S_IP − τ` = 67.99），横向半径 17.3 – 33.8 mm（远大于拇指管半径 `r_tt` ≈ 9.44 mm）。
即**解剖学意义上的拇指基底 ↔ 第一指蹼 ↔ 食指根部连续皮肤带**。

| edge | bind mm | 拇指弧长 mm | 横向 mm | 二面角° |
|---|---|---|---|---|
| 1417 | 9.039 | 55.686 | 33.788 | 23.29 |
| 4963 | 9.046 | 57.828 | 31.459 | 26.67 |
| 1441 | 8.705 | 58.648 | 28.925 | 22.62 |
| 2346 | 3.591 | 66.937 | 25.198 | 15.51 |
| 5753 | 5.168 | 66.937 | 25.198 | 19.37 |
| 1699 | 3.749 | 67.493 | 17.342 | 6.21 |

剪断它们会破坏真实手部表面连续性 → **不得剪**。

### 3.3 CLASS_B（61 条）—— 代表边

位于 **RSSF 拇指末节 ↔ 食指 MCP/近节接触带**（拇指弧长 75.5 – 93.95 mm）。

| edge | bind mm | 拇指端（标签 → 真实手指，驱动骨） | 食指端（标签 → 真实手指，驱动骨） |
|---|---|---|---|
| **1019** | **1.059** | v37 `THUMB` → **THUMB** `THUMB_IP_R` 1.000 | v1340 `INDEX` → **THUMB** `INDEX_MCP_R` 0.661 |
| 4339 | 1.134 | v2740 `THUMB` → **THUMB** `THUMB_IP_R` 1.000 | v1339 `INDEX` → **THUMB** `INDEX_MCP_R` 0.542 |
| 4344 | 1.937 | v2741 `THUMB` → **THUMB** `THUMB_IP_R` 1.000 | v1338 `INDEX` → **THUMB** `INDEX_MCP_R` 0.840 |
| 1104 | 3.051 | v1383 `THUMB` → **THUMB** `THUMB_IP_R` 1.000 | v299 `INDEX` → **THUMB** `INDEX_MCP_R` 0.502 |
| 445 | 4.138 | v149 `THUMB` → **INDEX** `THUMB_IP_R` 0.890 | v1053 `INDEX` → **INDEX** `WRIST_R` 0.628 |

**注意机理**：错标**两个方向都发生**——
61 条中 **33 条**是“拇指端标签被贴在食指面片顶点上”，**28 条**是“食指端标签被贴在拇指面片顶点上”。
因此当拇指运动时，相邻顶点由不同骨骼驱动（`THUMB_IP_R` vs `INDEX_MCP_R` vs `WRIST_R`），
它们之间的边被拉开 —— 这就是 Stage6B 观测到的撕裂。

---

## 4. 指甲 / 远端帽专项（§12 / §13）

| 项 | 值 |
|---|---|
| 涉及 **NAIL** 的 seam edge | **8** |
| 涉及 **DISTAL_CAP** 的 seam edge | **9** |
| 涉及 **THUMB_IP 区** 的 seam edge | **61** |
| **v1383** 参与 | e1104、e4520 |
| **v2740** 参与 | e4339、e4340 |

**为什么指甲/远端帽会“碰到” seam？**
因为这些顶点就在**拇指自己的末节表面**上，而该表面在 RSSF 绑定姿态里正好从食指近端面片
旁边 **1–9 mm** 处经过。最近链测试由此把**同样属于拇指**的邻近顶点判成 INDEX，
画出一条**网格里并不存在**的边界。

**v1383 / v2740 的解释力**：它们的 raw 最近链归属是 INDEX，R1A 通过 nail authority
把它们**提升回 THUMB**；Stage6B 的 seam 恰好是这条“提升带”的边沿。
因此这两点**解释了一部分**（4 条边），但**不是全部根因** —— 不得据此假设根因只有两点。

---

## 5. 祖先溯源（§14 / §15 / §16 / §17）

### 5.1 匹配方法

**绝不单凭 edge index 相同**判定同一条边。使用：
① **相同 vertex-index 对**（分辨率一致时，精确）；
② **点落在边上**（point-on-segment，跨分辨率时）。

### 5.2 逐阶段结果

| 阶段 | NV / NE / NF | 67 条边（同 index 对） |
|---|---|---|
| S0 CC0 source bundle | 831 / 1649 / 820 | 不适用（分辨率不同） |
| S2 BOOTSTRAP C1 | 831 / 1649 / 820 | 不适用（分辨率不同） |
| **S4A_CANDIDATE** | 3544 / 7084 / 3542 | **67 / 67 ✅ 首次全部出现** |
| S4A_RAW / S4A_CMC_R1 | 3544 / 7084 / 3542 | 67 / 67 |
| S4A_R2_BASE | 3364 / 6724 / 3362 | 67 / 67 |
| S4A_R2 | 3416 / 6828 / 3414 | 67 / 67 |
| S4B_RSSF_R1 | 3416 / 6828 / 3414 | 67 / 67 |
| S4B_RSSF_R2 → S5B_R1B | 3416 / 6828 / 3414 | 67 / 67 |

**S4A_R2 起边集与生产完全逐字节同构**（`edge_set_equal_to_production = True`）；
`S4B_RSSF_R2 → S5B_R1B` 顶点位置 **3416/3416 完全一致（max delta 0.0000 mm）**。
`S4A_R2 → S4B_RSSF_R2` 位置变化 max 56.71 mm → **RSSF 只重摆姿态，不改拓扑**。

### 5.3 源资产同一性（决定性）

| 检验 | 结果 |
|---|---|
| CC0 bootstrap → Stage4A R2 最优刚体（含 **180° about X** 符号翻转） | **median 0.0006 mm / max 0.1334 mm** |
| 结论 | **工程网格就是 CC0 表面本身**（`TOPOLOGY_WORKING_BASE = OFFICIAL_MULTIREZ_L1_APPLIED`，仅 +244 个 MCP/CMC 关节环 quad），**未经 re-pose、未重建** |
| 源位姿拇指片 ↔ 食指片最小间距 | **10.86 mm**（831 点稀疏采样） |
| Stage4A R2（RSSF 前）同度量 | **5.05 mm** |
| Stage4B **RSSF R2**（生产绑定） | **0.2465 mm** ← **缩小约 20×** |

### 5.4 归属权威对比

| 权威 | THUMB\|INDEX 边界 | 弧长位置 |
|---|---|---|
| **测地（网格真实）** | 56 条 | **42.68 – 58.65 mm**（拇指基底 = 真实第一指蹼） |
| **最近链（Stage5B 实际使用）** | 67 条 | 55.69 – **93.95 mm**（一路延伸到指尖） |

测地边界**从不**出现在弧长 > 71.88 mm（IP 关节）处；
最近链权威在拇指末节上**多造了 61 条边界**。

### 5.5 Stage4 CMC surgery 影响面（§16）

| 项 | 值 |
|---|---|
| CMC R2 手术约束半径 | **25.08 mm**（中心世界坐标 `[1448.8973, 11.1066, 393.9344]` mm） |
| 半径内的 seam edge | **0 / 67** |
| 触及 CMC cage patch 的 seam edge | **0 / 67** |
| R2 手术拓扑增量 | 3364 → 3416（**+52 顶点**，局限于 CMC） |

**结论：`CMC_SURGERY_INTRODUCED_SEAM = FALSE`。**
67 条边在 R2 手术**之前**（S4A_CANDIDATE）就已作为同 index 对存在。

### 5.6 §17 判定

`CLASS_C = 0` ⇒ **§17 的两个分支都不成立**：
- `SOURCE_ASSET_TOPOLOGY_LIMITATION` = **NOT_APPLICABLE**
- `STAGE4_TOPOLOGY_INTRODUCED_DEFECT` = **NOT_APPLICABLE**

正式归类：**`ORDINARY_INTERIOR_EDGES_OF_THE_CC0_HAND_SURFACE`**。

---

## 6. 动态应变仅作分类辅助（§19）

复算 5 个诊断姿态，**与 Stage6B 记录逐位吻合**（独立验证姿态重建正确）：

| pose | max seam stretch | 撕裂(>3×) |
|---|---|---|
| TH_MCP_45 | 31.9401× | 64 / 67 |
| TH_IP_45 | 12.9165× | 43 / 67 |
| CMC_OPP_10 | 12.5977× | 48 / 67 |
| CMC_OPP_30 | 38.2469× | 67 / 67 |
| FULL_OPP_L3 | 61.3116× | 67 / 67 |

动态拉伸只说明“两端 deformation authority 不兼容”，**已按规程仅作辅助**，
最终分类由 **拓扑 + 解剖位置 + 语义归属 + 溯源** 决定。

---

## 7. CMC cage 与深穿透的独立状态（§29 / §30）

| 项 | 状态 |
|---|---|
| `CMC_CAGE_DYNAMIC_QUALIFICATION` | **PASS** |
| `T04_CMC` | **PASS_FOR_CURRENT_STAGE6B_RANGE** |
| `CMC_DEFORMATION_FINAL` | **PENDING**（整体 thumb opposition 仍受 seam 阻断） |
| `THUMB_INDEX_DEEP_PENETRATION` | **SEPARATE_PENDING_STAGE6B_RETEST**（max penetration proxy **4.177 mm**） |

> **不得**声称“修好 seam = Stage6B 自动 PASS”。
> 未来 topology / ownership 修复后**必须重跑 Stage6B contact progression**。

---

## 8. 交付物

| 文件 | 内容 |
|---|---|
| `STAGE6B_R1A_SEAM_PROVENANCE_REPORT.md` | 本报告 |
| `STAGE6B_R1A_SEAM_REPAIR_DECISION_MATRIX.md` | HR 决策矩阵 |
| `STAGE6B_R1A_SEAM_PROVENANCE_STATUS.json` | 本轮状态 |
| `STAGE6B_R1A_SEAM_EDGE_TOPOLOGY_AUDIT.json` | 67 条边完整逐条取证 + 标签交错审计 |
| `STAGE6B_R1A_DISTAL_SEAM_FORENSIC_AUDIT.json` | 指甲 / 远端帽 / v1383 / v2740 专项 |
| `STAGE6B_R1A_SEAM_ANCESTRY_AUDIT.json` | 全血统溯源 + 接触纪元 |
| `CMC_SURGERY_SEAM_PROVENANCE.json` | CMC 手术影响面 |
| `STAGE6B_R1A_CLASS_A_VALID_WEB_EDGES.json` | 6 条，`DO_NOT_CUT_CLASS_A` |
| `STAGE6B_R1A_CLASS_B_OWNERSHIP_MISCLASSIFICATION.json` | 61 条 + ownership correction evidence |
| `STAGE6B_R1A_CLASS_C_INVALID_EDGE_TABLE.json` | **0 条** |
| `STAGE6B_R1A_CLASS_D_AMBIGUOUS_EDGES.json` | **0 条** |
| `renders/`（7 张） | 见 §9 |

### 9. 渲染

| 文件 | 说明 |
|---|---|
| `STAGE6B_R1A_THUMB_INDEX_SEAM_67_EDGE_ANATOMY_MAP.png` | 三联：dorsal / palmar / contact close-up |
| `STAGE6B_R1A_SEAM_MAP_DORSAL.png` | 背面视图 |
| `STAGE6B_R1A_SEAM_MAP_PALMAR.png` | 掌面视图 |
| `STAGE6B_R1A_SEAM_MAP_RADIAL.png` | 桡侧视图 |
| `STAGE6B_R1A_SEAM_MAP_ULNAR.png` | 尺侧视图 |
| `STAGE6B_R1A_SEAM_MAP_CLOSEUP.png` | 拇指末节 / 食指 MCP 接触带特写 |
| `STAGE6B_R1A_SEAM_MAP_EXPLODED.png` | **EXPLODED_DIAGNOSTIC_ONLY**（仅可视化副本，真实网格未改） |

配色：**CLASS_A 绿 / CLASS_B 橙 / CLASS_C 品红 / CLASS_D 蓝**；
灰 = 全部 6828 条网格边；红 = THUMB owned；蓝 = INDEX owned；青 = FIRST_WEB；黄 = NAIL；紫 = DISTAL_CAP。

---

## 10. 本轮未做（严格边界）

未修 seam、未 retopo、未改 ownership、未改权重、未改 joint / roll / CMC vector / RSSF /
nail / distal cap / first-web mask，未重跑 Stage6B，未进入 key press / 教学动作 / 左手 / Web export。

---

## 11. 状态

```
STAGE6B_R1A_SEAM_PROVENANCE = READY_FOR_HUMAN_REVIEW
STAGE6B                     = REMAINS_FAIL_CLOSED
CMC_CAGE_DYNAMIC_QUALIFICATION = PASS
T04_CMC                     = PASS_FOR_CURRENT_STAGE6B_RANGE
CMC_DEFORMATION_FINAL       = PENDING
DEFORMATION_FINAL           = PENDING
TOPOLOGY_REPAIR             = NOT_STARTED
OWNERSHIP_CORRECTION        = NOT_STARTED
STAGE6B_RETEST              = NOT_STARTED
```

**STOP —— 等待 Human Review。**
