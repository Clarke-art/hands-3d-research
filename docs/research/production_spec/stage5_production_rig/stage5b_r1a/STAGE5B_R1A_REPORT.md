# STAGE5B_R1A — Thumb Chain Weight Rebalance（拇指链权重职责重建）· 阶段报告

- **阶段**：`STAGE5B_R1A_THUMB_CHAIN_WEIGHT_REBALANCE`（Stage5B R1 Human Review 后的**窄范围**权重修订）
- **日期**：2026-09-30（GMT+8）
- **运行环境**：Blender 5.1.2（`D:\Blender\blender.exe`），纯本地 EEVEE 渲染，无外部服务调用
- **输入 R1 candidate（冻结）**：`stage5b_r1/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1.blend` → `8f4c6901…c308d`（执行前后未变 ✅）
- **输入 Stage5A master（冻结）**：`stage5a_r2a/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend` → `c4fafc56…c2845`（执行前后未变 ✅）
- **输出 R1A candidate（新建）**：`stage5b_r1a/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1A.blend` → `c68e415a…8c0ea6`（2,293,759 B）
- **状态结论**：`STAGE5B_R1A = READY_FOR_HUMAN_REVIEW`；`PRODUCTION_BINDING = CARRY_FORWARD_PASS`；`INITIAL_PRODUCTION_SKIN_WEIGHT = PASS_PENDING_HUMAN_REVIEW`；`PRODUCTION_SKIN_WEIGHT_FINAL = NOT_YET_APPROVED`；`STAGE6 = NOT_STARTED`

---

## 一、Human Review 裁决的处置

| HR 判定项 | R1A 处置 |
|---|---|
| PRODUCTION_BINDING = PASS | 保留（parent/rig transform/修改器结构未动，world_delta = 0） |
| ZERO_POSE_BIND = PASS | 重新验证通过（max delta 5.967e-05 mm） |
| FOUR_FINGER_INITIAL_WEIGHT = PASS | 四指全部 11 组权重**位级不变**（frozen drift = 0） |
| WRIST_WEIGHT = PASS_FOR_INITIAL_BIND | 仅授权区域内重分配 |
| GLOBAL_CROSS_DIGIT_GUARD = PASS | 重新审计（1 项 R1 遗留 residue，已记录） |
| TOPOLOGY / UV / MATERIAL = PASS | delta 全 0 |
| MAX_INFLUENCES ≤ 4 = PASS | 保持 ≤ 4 |
| **THUMB_CHAIN_WEIGHTING = FAIL/REVISE** | 本轮重建（见 §三–§五） |
| **FIRST_WEB_WEIGHTING = FAIL/REVISE** | mask 重新资格确认 + 权重归零（见 §六） |

---

## 二、只读根因审计（先测量，后修改）

产物：`STAGE5B_R1A_THUMB_WEIGHT_ROOT_CAUSE_AUDIT.json`（在改动任何权重**之前**产出）

### 根因 1（主因）· THUMB DISTAL OWNERSHIP GUARD 判据反向

R1 守卫写作：

```
if (v in NAIL_THUMB_V) or (arc_of("THUMB", v) <= XIJ["THUMB"][2] + tau):   # ← 反向
        raw["THUMB_IP_R"] = max(raw["THUMB_IP_R"], 2.0 * sum(others))
```

`XIJ["THUMB"][2]` = 从 CMC head 起算的 **IP 关节弧长**（= MCP 段的**远端端点**）。所有拇指自有顶点都满足 `arc ≤ IP关节弧长`，于是该守卫在**整根拇指**上无条件成立：

| 指标 | 值 |
|---|---|
| 拇指自有顶点 | 620 |
| R1 判据成立数 | **620 / 620（100 %）** |
| 修正判据（`arc ≥ IP弧长 − τ`）成立数 | 161（= 远端指骨，正确） |
| 观测到 `W_IP ≥ 2×others` 的顶点 | 601 |
| THUMB_IP_R 非零顶点 | **604**（>0.25：604；>0.50：601） |
| W_IP 直方图（拇指自有顶点） | 0.0:16 ｜ (0,0.25]:0 ｜ (0.25,0.5]:9 ｜ (0.5,0.75]:3 ｜ (0.75,1.0]:**592** |

**原因归类**：`region mask 太宽` + `thumb distal ownership guard 太强` 的组合——真正的单一触发点是**判据符号反向**，且**没有 else 兜底**把 THUMB_IP 限制在远端指骨。`lam = exp(-((xi-mj)/κ)²)` 与 `mu = exp(-(d/L0)²)` 都被该守卫覆盖，`normalize → prune → normalize` 顺序正常（最坏归一化误差 4.4e-08），**不是**成因。

### 根因 2 · CMC / MCP 偏弱是上一条的**症状**

守卫强制 `W_IP ≥ 2×others` ⇒ `sum(others) ≤ 1/3`；CMC 与 MCP 再对分这 1/3 ⇒ 解析上界 0.3333。实测 CMC max 0.3618、MCP max 0.2955、IP max 0.9982，与解析上界吻合。

### 根因 3 · FIRST_WEB 审计逻辑与权重语义双重矛盾

- **构建侧**：`allowed -= {"THUMB_IP_R", …}` 只在 `i not in NAIL_THUMB_V` 时执行 ⇒ 落在 web 带内的**拇指指甲顶点保留 THUMB_IP 并被守卫强制抬高**。
- **审计侧**：违例循环写成 `if b not in WEB_OK and b not in ("THUMB_IP_R","INDEX_PIP_R","INDEX_DIP_R")` ⇒ **THUMB_IP 结构上永远无法被报为违例**，却同时声明 whitelist = `WEB_OK`。
- 实测（按严格 whitelist 重算）：R1 web 内有 5 条违例（均为 THUMB_IP_R），合计 2.666676 —— 与 R1 报告的 `violations = []` 直接冲突。

### 根因 4 · R1 的 “FIRST WEB” mask 根本不是 first web

R1 mask（`到两条链距离 ≤ 2×中位边长`，阈值 7.7764 mm）命中 45 顶点，但其**拇指弧长区间为 83.0–93.9 mm**（= 拇指**远端指骨**，IP 关节在 71.88 mm），并**吞入 5 个拇指指甲顶点**。原因是本姿态下拇指被内收：

| 拇指链段 | 到食指链最小距离 |
|---|---|
| CMC 段 | 44.29 mm |
| MCP 段 | 18.11 mm |
| IP 段 | **3.28 mm** |

即：拇指与食指**只在该指远端相接**，MCP 层级相距 18.11 mm，**不存在**可跨越两条链的 web 皮面。因此 R1 在“first web”里测到的 THUMB_IP **不是泄漏，而是被错误命名的拇指远端**。

### 根因 5 · 语义归属（ownership）判据缺陷

`OWN_V` 用**二维折线最近距离**作顶点归属权威。在本姿态下，拇指远端指骨贴着食指 MCP，于是：

- **v1383 / v2740**（拇指指甲近端 border 顶点）被判为 `INDEX`（dThumb 8.29/6.44 vs dIndex 7.68/5.72）；
- **v1061 / v2189**（R2A 已批准的拇指远端 cap patch 顶点）同样被判为 `INDEX`。

这直接决定了 v1383/v2740 在 R1 的权重归属（见 §四）。

### 根因 6（方法学，记录在案）· 测地坐标在本网格上不可用

`geodesic distance from the thumb distal-most vertex` 在本网格上**非单调**：拇指**指甲板及其相邻背侧片层**到 D*=v2189 的**表面测地距离为 148–180 mm**，而空间欧氏距离仅 8–30 mm（该处存在表面折痕/片层结构；`v1076` 测地 8.94 mm 而 `v284` 达 174.70 mm）。R1 定义了 `gval()` 但守卫从未调用它，故未造成损害；R1A **显式弃用**该坐标，改用**已批准关节折线的弧长坐标**（沿 CMC head → MCP → IP → TIP，单调、贴合已批准运动学轴，且天然复现 R2A 批准的 IP→TIP 远端范围 71.88→93.95 mm）。

---

## 三、R1A 语义区域（§十）

产物：`THUMB_SEMANTIC_REGION_AUDIT.json`

全部常量均由数据导出，无手选常数：`τ = 1×网格中位边长 = 3.8882 mm`；`R_TT = 9.44 mm`（近节指骨带内到拇指链的 p25 横向距离 = 管半径）；`R_MAX = 29.87 mm`（掌骨/根部带 p95）；`R_TUBE = R_TT + τ = 13.33 mm`。

| 区域 | 顶点数 | 允许骨 | 期望主导 | 派生依据 |
|---|---|---|---|---|
| THUMB_DISTAL | 161 | IP / MCP | **THUMB_IP_R** | 弧长 ≥ IP 关节 − τ，∪ 拇指指甲面顶点 ∪ R2A 远端 cap |
| THUMB_PROXIMAL | 107 | MCP / IP / CMC | **THUMB_MCP_R** | MCP−τ ≤ 弧长 < IP−τ 且横向 ≤ R_TUBE |
| THUMB_FIRST_METACARPAL | 153 | CMC / MCP / WRIST | **THUMB_CMC_R** | 弧长 < MCP−τ 且横向 ≤ R_TUBE |
| THUMB_BASE_FOLD | 37 | WRIST / CMC / MCP / INDEX_MCP | MCP（近节层面折返带） | 横向 > R_TUBE 且 MCP+τ < 弧长 < IP−τ |
| THENAR_BASE | 287 | WRIST / CMC / MCP | **WRIST + THUMB_CMC** | 根部隆起（横向 > R_TT，弧长 ≤ MCP+τ）∪ 拇指自有顶点 2 环内的腕侧掌带 |
| FIRST_WEB | 21 | WRIST / CMC / MCP / INDEX_MCP | 四者（IP 恒为 0） | 拇指↔食指**拓扑归属边界** 2 环带 ∩ 弧长 ≤ IP−τ ∩ 索引弧长 ≤ PIP+τ ∩ 非指甲/非 cap |
| CENTRAL_PALM | 1199 | WRIST | WRIST | 掌/前臂非拇指根部 —— **不修改** |

**授权修改集 AUTH = 703 顶点（20.58 %）**；覆盖全部 604 个 THUMB_IP 非零顶点（**区域外 THUMB_IP 非零 = 0**，构建期硬断言）。

区域重叠矩阵（显式 transition 语义）见 `THUMB_SEMANTIC_REGION_AUDIT.json`：CHAIN 段之间零重叠；THENAR_BASE 与 PROXIMAL/METACARPAL/FIRST_WEB 有 15/27/4 个过渡共享顶点；CENTRAL_PALM 与其他区域完全不相交。

---

## 四、v1383 / v2740 独立空间语义核查（§六）

产物：`THUMB_NAIL_BOUNDARY_VERTEX_AUDIT.json` + `STAGE5B_R1A_NAIL_VERTEX_1383_2740.png`

| 项 | v1383 | v2740 |
|---|---|---|
| world（mm） | (1448.9, 16.1, 472.9) | (1450.4, 15.2, 476.4) |
| incident faces | `1217(0) 1218(**NAIL**) 1222(0) 1223(0)` | `1040(**NAIL**) 1041(0) 1042(0) 1043(0)` |
| NAIL_BED / 非 NAIL 面数 | 1 / 3 | 1 / 3 |
| 分类 | **SHARED_SEMANTIC_BOUNDARY_VERTEX** | **SHARED_SEMANTIC_BOUNDARY_VERTEX** |
| 拇指链弧长 | 82.58 mm | 85.78 mm |
| 投影所在拇指骨段 | **远端指骨**（IP 关节 = 71.88 mm） | **远端指骨**（IP 关节 = 71.88 mm） |
| dThumb / dIndex | 8.29 / 7.68 mm | 6.44 / 5.72 mm |
| 到 cap 代表点 | 20.81 mm | 17.48 mm |
| 是否在 distal-cap patch | 否 | 否 |
| **R1 归属（二维最近链）** | INDEX | INDEX |
| R1 dominant | WRIST_R 0.5038 + INDEX_MCP_R 0.4962 | INDEX_MCP_R 0.5354 + WRIST_R 0.4167 + THUMB_MCP_R 0.0479 |
| R1 为何无拇指骨 | dThumb 8.29 mm **> R1 web 阈值 7.7764 mm** ⇒ web 分支未触发、`allowed` 内不含任何拇指骨（`own = INDEX`） | 落在 R1 web 带内 ⇒ 只加根级 `THUMB_CMC/MCP`；因 `own = INDEX` 而 `THUMB_IP_R` **永无资格** |
| **分支判定** | **C → A 合并**：共享指甲/皮肤边界顶点，位于**拇指远端指骨** ⇒ 远端权威 = `THUMB_IP_R`（以 incident-face 证据记录为 SHARED_BOUNDARY_EXCEPTION） | 同左 |
| R1A dominant | **THUMB_IP_R = 1.0** | **THUMB_IP_R = 1.0** |

拇指指甲 22 个顶点中 **18 个**为 nail/skin 共享边界顶点（全部列出 incident-face 证据），R1A 后 **18/18 dominant = THUMB_IP_R**；拇指指甲整体 **22/22 正确**（R1：20/22）。

---

## 五、Thumb chain 权重职责重建（§七 / §十一 / §十四）

### 方法

对每个授权顶点，沿**拇指链弧长** `s` 建立**单位分解**（joint-local transition，`τ = 1 网格边`）：

```
t_IP  = S((s − s_IP )/τ)          s_IP  = 71.8815 mm
t_MCP = S((s − s_MCP)/τ)          s_MCP = 42.6796 mm
A_IP   = t_IP            W_IP  = A_IP
A_MCP  = t_MCP − t_IP    W_MCP = A_MCP
A_BASE = 1 − t_MCP       W_CMC = A_BASE · f_tube(d)
                         W_WRIST = A_BASE · (1 − f_tube(d))
f_tube(d) = 1 − S((d − R_TT)/(R_MAX − R_TT))          # 管内外径向分工
Σ W = 1 且各项 ≥ 0（t_MCP ≥ t_IP ⇒ 单调嵌套）
```

- **FIRST_WEB** 内：`W_IP ≡ 0`；令 `share_idx = S((dThumb − dIndex + τ)/(2τ))`，其余 `(1 − share_idx)` 按 `W_MCP : W_CMC : W_WRIST` 比例分配 ⇒ 参与组恒为 `{WRIST, CMC, MCP, INDEX_MCP}` 子集。
- **不使用**单骨骼欧氏距离作纵向依据；`f_tube` 只作**径向**分工（区分“管”和“根部/隆起”）。
- 未授权顶点：**完整 16 组权重向量与 R1 完全相同**。
- FROZEN 组（`INDEX_PIP/DIP`、`MIDDLE_*`、`RING_*`、`LITTLE_*`）：**任何顶点、任何时刻都不参与缩放**，逐位不变。

### 结果（每骨组 before → after）

| 骨组 | 非零顶点 | >0.25 顶点 | max | 权重和 |
|---|---|---|---|---|
| THUMB_IP_R | 604 → **139** | 604 → **137** | 0.9982 → **1.0000** | 411.81 → **134.17** |
| THUMB_MCP_R | 645 → 195 | 54 → **150** | 0.2955 → **1.0000** | 44.84 → **147.88** |
| THUMB_CMC_R | 1244 → 907 | 86 → **276** | 0.3618 → **1.0000** | 81.54 → **243.40** |
| INDEX_MCP_R | 524 → 456 | 209 → 190 | 0.9991 → 0.9989 | 153.78 → 138.25 |
| WRIST_R | 3416 → 3000 | 1726 → 1782 | 1.0000 | 1561.41 → 1589.68 |
| INDEX_PIP_R / INDEX_DIP_R / MIDDLE_* / RING_* / LITTLE_*（11 组） | **完全不变** | 完全不变 | 完全不变 | **完全不变** |

### THUMB_CHAIN_DOMINANCE_BY_REGION（before → after，unexpected dominant = 0）

| 区域 | R1 dominant 分布 | R1A dominant 分布 | R1 THUMB_IP 总量 | R1A THUMB_IP 总量 |
|---|---|---|---|---|
| THUMB_DISTAL (161) | IP 141 / INDEX_MCP 17 / WRIST 3 | **IP 136** / MCP 25 | 103.15（mean 0.732，median 0.697） | **134.17（mean 0.965，median 1.0，全部 THUMB_IP 质量都在此区）** |
| THUMB_PROXIMAL (107) | **IP 107**（错） | **MCP 81** / CMC 26 | 71.33 | **0.00** |
| THUMB_FIRST_METACARPAL (153) | **IP 153**（错） | **CMC 153** | 102.00 | **0.00** |
| THUMB_BASE_FOLD (37) | **IP 37**（错） | **MCP 37** | 24.67 | **0.00** |
| THENAR_BASE (287) | IP 208 / WRIST 79 | **WRIST 188 / CMC 95** / MCP 4 | 138.67 | **0.00** |
| FIRST_WEB (21) | **IP 21**（错） | MCP 18 / WRIST 3 | 14.00 | **0.00** |
| CENTRAL_PALM (1199) | WRIST 1199 | WRIST 1199 | 0.00 | 0.00 |

**THUMB_IP_PROXIMAL_LEAKAGE**：全局 THUMB_IP 总量 411.814073 → **134.166368**，且 R1A 后 THUMB_IP 质量 **100 %** 落在 THUMB_DISTAL 内（其余全部区域 = 0）；FIRST_WEB / CENTRAL_PALM / CMC_LOCALITY 三处 after = **0.000000**（精确 0）；THENAR_BASE / THUMB_FIRST_METACARPAL / THUMB_PROXIMAL after = **0.000000**。
**THUMB_CMC_THENAR_LOCALITY**：THUMB_CMC 权重 100 % 落在 FIRST_METACARPAL ∪ THENAR_BASE 内（占比 ≥ 0.9 gate，实测 1.0）。**未设任何“max > 0.5”人造门**。

---

## 六、FIRST WEB 重新资格确认（§八 / §九 / §十八）

产物：`FIRST_WEB_REGION_AUDIT_R1A.json`、`FIRST_WEB_WEIGHT_AUDIT_R1A.json`、`STAGE5B_R1A_FIRST_WEB_MASK.png`

- **新 mask 定义**（姿态感知 + 解剖窗）：拇指↔食指**拓扑归属边界** 2 环带 ∩ 拇指弧长 ≤ IP−τ ∩ 食指弧长 ≤ PIP+τ ∩ 排除指甲/cap ⇒ **21 顶点**（拇指侧），弧长区间 41.7–68.0 mm（拇指 MCP 层级的尺侧边界 = 解剖学 first web 位置）。
- 明确**排除**：拇指远端指骨、指甲、cap patch、large thenar（渲染内以粉/绿/黄分别标注）。
- **FIRST_WEB_THUMB_IP_TOTAL_WEIGHT**：R1 = **14.000000** → R1A = **0.000000**（精确 0，非 epsilon 依赖）
- **participating_groups = {INDEX_MCP_R, THUMB_CMC_R, THUMB_MCP_R, WRIST_R} ⊆ whitelist**，**violations = []**（严格 whitelist，不含任何豁免名单）
- before/after 证据：`STAGE5B_R1A_FIRST_WEB_BEFORE_AFTER.png`（同一帧内左右两态，相机/灯光/legend/量程完全一致）

---

## 七、权重写入、剪枝与保护（§十五 / §十六）

产物：`STAGE5B_R1A_WEIGHT_DELTA_AUDIT.json`、`STAGE5B_R1A_PROTECTED_WEIGHT_DRIFT_AUDIT.json`

| 项 | 值 |
|---|---|
| 授权区域顶点数 | 703 |
| **实际改变顶点数** | **696** |
| 未改变顶点数 | 2720 |
| 最大单点权重变化 | 1.0（0 → 1 的极端过渡带顶点） |
| 每组新增权重 | WRIST +92.444 ｜ CMC +180.929 ｜ MCP +115.410 ｜ IP +47.265 ｜ INDEX_MCP +0.331 |
| 每组移除权重 | WRIST −64.173 ｜ CMC −19.068 ｜ MCP −12.368 ｜ IP −324.913 ｜ INDEX_MCP −15.858 |
| **UNAUTHORIZED_CHANGED_VERTICES** | **0** |
| **FROZEN 四指组改动** | **0**（11 组 × 3416 顶点逐位相同） |
| prune（仅对 changed 顶点） | vertices_pruned = **0**，discarded = 0.000000000（构造即 ≤ 4 影响数） |
| 影响数分布 | 1: 951 ｜ 2: 244 ｜ 3: 51 ｜ 4: 2170 ｜ >4: **0** |
| 未权重顶点 | **0** |
| 归一化最坏误差 | 4.400e-08 |

### Prune worst-case（§二十）

R1 报出的最坏单点丢弃权重 0.095368 定位为 **v778**（世界坐标见 `WEIGHT_PRUNE_WORST_CASE_AUDIT_R1A.json`），位于 **CENTRAL_PALM**，**不在授权区域** ⇒ R1A 后仍保持 R1 原值（before == after，1 项被弃影响，总权重 0.095368）；因其**不影响语义归属**且最终影响数 = 4，判定 **PASS（非 blocker）**。R1A 自身对全部 changed 顶点的 prune 丢弃量 = 0。

---

## 八、其余重新审计

| 审计 | 结果 |
|---|---|
| **ZERO_POSE_BIND_AUDIT_R1A** | max 5.967e-05 mm / mean 5.893e-06 mm / bbox ≤ 7.451e-06 mm；parent = `RIGHT_HAND_PRODUCTION_RIG`；修改器 `PRODUCTION_ARMATURE` 结构未变 ⇒ **PASS** |
| **TOPOLOGY / UV / MATERIAL** | V=3416 / E=6828 / F=3414 / TRIS=6828；topology_delta = 0、uv_delta = 0、material_delta = 0、**nail-face assignment delta = 0** ⇒ PASS |
| **NAIL_WEIGHT_AUDIT_R1A** | index/middle/ring/little = **100 % DIP 主导**；thumb = **22/22 THUMB_IP 主导**（R1：20/22）；拇指 18 个 nail/skin 共享边界顶点全部带 incident-face 证据记录；violations = [] |
| **CROSS_DIGIT_WEIGHT_LEAK_AUDIT_R1A** | 非授权泄漏 **1 项**，为 R1 遗留 residue（顶点 2189 的 `INDEX_PIP_R` = 2.4507e-04，before == after）；因该组属 FROZEN 四指组，本轮无权修改 ⇒ 记为 `KNOWN_CARRY_OVER_RESIDUE_FROM_R1`。**R1A 引入的跨指权重 = 0**；授权掌扇与授权首蹼根混合仍合法 |
| 归属权威修正 | R1A 采用证据型归属（拇指自有指甲面 / R2A 批准远端 cap ⇒ THUMB），修正 R1 二维最近链误判的 4 个顶点：`1061, 1383, 2189, 2740` |

---

## 九、输入冻结复核（§二十七）

| 文件 | SHA-256 | 判定 |
|---|---|---|
| Stage5A master（输入） | `c4fafc56c591411bb5ddf07bde44b5fcd6e6a9aa5e0d43b22f9734c0884c2845` | 执行前后一致 ✅ |
| Stage5B R1（输入） | `8f4c6901fdae417e3855d388f9739ebea10863f0ebdbfedf0df8d79a751c308d` | 执行前后一致 ✅ |
| Stage5B R1A（输出） | `c68e415aff80b56911cfe5646e47dff9100d7b54b8bf7aa8ba068bb3948c0ea6` | 新产物 ✅ |

> 渲染脚本仅 `write_still` 输出 PNG，未回存任何 `.blend`。

---

## 十、自动 Gate（§二十八）

```
FIRST_WEB_REGION_VALIDATED        = PASS
FIRST_WEB_THUMB_IP_WEIGHT         = PASS   (0.000000, 精确 0)
FIRST_WEB_WHITELIST               = PASS   (violations = [])
THUMB_IP_DISTAL_LOCALITY          = PASS
THUMB_IP_PROXIMAL_LEAKAGE         = PASS
THUMB_CMC_THENAR_LOCALITY         = PASS
THUMB_CHAIN_DOMINANCE_BY_REGION   = PASS   (全部区域 unexpected dominant = 0)
THUMB_NAIL_BOUNDARY_RESOLVED      = PASS
NAIL_WEIGHT_OWNERSHIP             = PASS   (四指 100%，拇指 22/22)
CROSS_DIGIT_LEAKAGE               = PASS_WITH_DOCUMENTED_CARRY_OVER_RESIDUE (1 项 R1 遗留，2.45e-4)
UNAUTHORIZED_WEIGHT_DRIFT         = 0
FROZEN_FOUR_FINGER_GROUP_DRIFT    = 0
UNWEIGHTED_VERTICES               = 0
MAX_INFLUENCES <= 4               = PASS
WEIGHT_NORMALIZATION              = PASS   (4.400e-08)
ZERO_POSE_BIND                    = PASS
TOPOLOGY_DELTA                    = 0
UV_DELTA                          = 0
MATERIAL_DELTA                    = 0
NAIL_FACE_ASSIGNMENT_DELTA        = 0
```

**FAIL CLOSED 触发项**：无（未移动任何骨骼、未改拓扑、未改指甲面归属、first web 已彻底去除 THUMB_IP、拇指远端/近端语义同时满足、四指权重未被破坏、无授权外漂移、零姿态无可见漂移）。

---

## 十一、渲染证据（16 张，15.6 MB）

路径：`stage5b_r1a/renders/`

- 单组权重图：`STAGE5B_R1A_WEIGHT_THUMB_CMC` / `_THUMB_MCP` / `_THUMB_IP` / `_FIRST_WEB` / `_THENAR` / `_CROSS_DIGIT_LEAK`
- 区域图：`STAGE5B_R1A_THUMB_REGION_DOMINANCE`
- first web 资格：`STAGE5B_R1A_FIRST_WEB_MASK`
- 指甲边界顶点：`STAGE5B_R1A_NAIL_VERTEX_1383_2740`（+ `_1383_2740_CONTEXT`，及单点 `_v1383` / `_v2740`）
- before / after：`STAGE5B_R1A_THUMB_IP_BEFORE_AFTER`、`STAGE5B_R1A_FIRST_WEB_BEFORE_AFTER`
- 绑定总览：`STAGE5B_R1A_BIND_OVERVIEW_DORSAL` / `_PALMAR`

**heatmap 规范（§二十四）**：全部图像共用同一 legend（0.0–1.0，dark-blue → green → yellow → red）、同一相机基准（由冻结 Stage4B 关节系 + S5A_R2 dorsal refs 推导）、同一灯光组、1500×1050 EEVEE / Standard view transform。before/after **在同一帧内渲染两个网格副本**（左 = R1，右 = R1A），因此相机、灯光、legend、色标量程可证明完全一致。

---

## 十二、结论与停止点

`STAGE5B_R1A = READY_FOR_HUMAN_REVIEW`。本轮为**静态权重修订**，未做任何动态形变（无 flex / oppose / key press / stress pose / animation），`STAGE6 = NOT_STARTED`。

**待 HR 裁决的开放项**（3 项，均已在对应审计 JSON 中留证）：

1. 顶点 **2189** 的 `INDEX_PIP_R = 2.4507e-04` 残留（R1 遗留；因属 FROZEN 四指组，本轮无权清除）。
2. 本姿态下**不存在开放的 first-web 折返**（MCP 层级两指相距 18.11 mm），first web 以“拇指↔食指归属边界 ∩ 解剖窗”定义，落在拇指侧 21 个顶点；如 HR 期望更大的 web 区域，需要新的 mask 定义输入。
3. `THUMB_IP_TO_TIP_STRAIGHT_CHORD_CONTAINMENT` 继续为 `DIAGNOSTIC_ONLY`（Stage5A R2B amendment 有效）；最终功能权威仍在 `STAGE6_DEFORM_TEST_THUMB_FLEX / _OPPOSE`。

---

## 十三、动作清单（allow / disallow）

**ALLOW（本次已执行）**
- 只读根因审计、v1383/v2740 独立空间核查、区域与 mask 资格确认（**均在改权重之前**）。
- 以副本形式新建 `RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1A.blend`；仅重写授权区域内 5 个自由组的权重。
- 全套重新审计 JSON + 16 张渲染。
- R2A master 与 R1 candidate 哈希复核（未变）。

**DISALLOW（本轮禁止）**
- 未移动骨骼、未改 bone roll、未增删 bone、未改 21-bone 层级。
- 未改 mesh geometry / topology / UV / material assignment / nail face assignment / RSSF / CMC cage / object origin。
- 未创建左手、未做 animation / GLB / Three.js。
- 未进入 Stage6；未将状态写为 `APPROVED` / `FINAL` / `STAGE6_STARTED`。
- 未修改任何四指已通过权重（frozen drift = 0）。

---

## 十四、产物清单

```
stage5b_r1a/
├── RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1A.blend        sha c68e415a…
├── STAGE5B_R1A_REPORT.md                            （本报告）
├── STAGE5B_R1A_STATUS.json
├── STAGE5B_R1A_THUMB_WEIGHT_ROOT_CAUSE_AUDIT.json
├── THUMB_NAIL_BOUNDARY_VERTEX_AUDIT.json
├── FIRST_WEB_REGION_AUDIT_R1A.json
├── THUMB_SEMANTIC_REGION_AUDIT.json
├── THUMB_CHAIN_DOMINANCE_AUDIT.json
├── THUMB_IP_PROXIMAL_LEAK_AUDIT.json
├── FIRST_WEB_WEIGHT_AUDIT_R1A.json
├── NAIL_WEIGHT_AUDIT_R1A.json
├── CROSS_DIGIT_WEIGHT_LEAK_AUDIT_R1A.json
├── STAGE5B_R1A_WEIGHT_DELTA_AUDIT.json
├── STAGE5B_R1A_PROTECTED_WEIGHT_DRIFT_AUDIT.json
├── STAGE5B_R1A_CMC_THENAR_LOCALITY.json
├── WEIGHT_PRUNE_WORST_CASE_AUDIT_R1A.json
├── ZERO_POSE_BIND_AUDIT_R1A.json
├── STAGE5B_R1A_VERTEX_INFLUENCE_AUDIT.json
├── STAGE5B_R1A_TOPOLOGY_DRIFT.json
├── STAGE5B_R1A_WEIGHT_STATS.json
├── renders/  (16 × PNG, 16,349,060 B)
├── scripts/  (r1a_common.py / s5b_r1a_survey.py / s5b_r1a_build.py /
│              s5b_r1a_audit.py / s5b_r1a_render.py)
└── _tmp/     (R1A_SURVEY.json / R1A_REGION_PROBE.json / R1A_REGIONS.json /
               R1A_RENDER_LOG.json)
```

> `_tmp/` 内为过程中间数据，非正式产物。
