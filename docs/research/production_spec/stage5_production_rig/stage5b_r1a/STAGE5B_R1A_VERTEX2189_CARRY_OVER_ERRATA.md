# STAGE5B_R1A_VERTEX2189_CARRY_OVER_ERRATA

**性质**：ERRATA sidecar（provenance 登记）。**不回改**任何历史文件。
**本轮**：纯只读提取 + 文档。未修改任何 blend、未修改任何权重。
**数据来源**：冻结 blend `stage5b_r1a/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1A.blend`
（SHA-256 `c68e415aff80b56911cfe5646e47dff9100d7b54b8bf7aa8ba068bb3948c0ea6`）
与对照 `stage5b_r1/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1.blend`
（SHA-256 `8f4c6901fdae417e3855d388f9739ebea10863f0ebdbfedf0df8d79a751c308d`）
**证据 JSON**：`stage5b_r1a/_tmp/R1A_V2189_PROVENANCE.json`
（同时内嵌于 `stage5b_freeze/STAGE5B_FREEZE_VERIFICATION_R1.json` → `vertex_2189`）

---

## 零、正式状态

```
VERTEX_2189_CARRY_OVER_RESIDUE   = ACCEPTED_NON_BLOCKING_PROVENANCE
DO_NOT_PROPAGATE_AS_GENERAL_EXCEPTION
IF_THE_WHOLE_WEIGHT_SET_IS_EVER_REGENERATED = SHOULD_BE_CLEANED
```

**不是** PASS AS DESIGNED；**不是** GENERAL EXCEPTION。
这是一个**点状、历史继承、非阻断性 provenance 记录**，只对 vertex 2189 生效，
不得推广到其它顶点、其它骨组或其它阶段。

---

## 一、Vertex 身份

| 项 | 值 |
|---|---|
| **vertex ID** | **2189** |
| world coordinate（mm） | `[1450.257778, 18.083785, 498.667270]` |
| 该顶点在网格中的角色 | **thumb distal-most vertex = D\***（拇指最远端顶点；R2A 远端 cap 定义的种子点） |
| 拇指链弧长 | **93.9454 mm** = 拇指链全长（CMC head → … → TIP 端点） |
| 是否在 R2A 已批准 thumb distal-cap patch | **是**（`cap_vertex_ids` 成员；R2A：`distal_most_vertex_inside_cap = true`） |
| 是否拇指指甲顶点 | 否 |
| R1A 语义归属 | **THUMB** |
| R1 二维最近链归属（历史） | **INDEX** ← R1 归属缺陷的直接体现 |
| R1A 语义区域 | **THUMB_DISTAL** |
| 当前 dominant | `THUMB_IP_R` |
| R1 dominant | `INDEX_MCP_R` |

---

## 二、当前完整 weight vector（冻结 R1A，16 组全列）

| group | weight |
|---|---|
| **THUMB_IP_R** | **0.999755191122** |
| INDEX_PIP_R | 0.000244808878 ← **residue** |
| INDEX_DIP_R | 0.0 |
| WRIST_R | 0.0 |
| THUMB_CMC_R | 0.0 |
| THUMB_MCP_R | 0.0 |
| INDEX_MCP_R | 0.0 |
| MIDDLE_MCP_R / MIDDLE_PIP_R / MIDDLE_DIP_R | 0.0 |
| RING_MCP_R / RING_PIP_R / RING_DIP_R | 0.0 |
| LITTLE_MCP_R / LITTLE_PIP_R / LITTLE_DIP_R | 0.0 |

非零组 = `{THUMB_IP_R, INDEX_PIP_R}`（2 组，≤ 4，PASS）。

**residual：`INDEX_PIP_R = 0.000244808878` ≈ 2.4507e-04 ≈ 0.0245 %**

---

## 三、before / after 对照

| group | R1（before） | R1A（after） | delta |
|---|---|---|---|
| INDEX_MCP_R | 0.999073 | 0.0 | −0.999073 |
| THUMB_IP_R | 0.0 | 0.999755 | +0.999755 |
| WRIST_R | 0.000683 | 0.0 | −0.000683 |
| **INDEX_PIP_R** | **0.000245** | **0.000245** | **0.0（逐位相同）** |
| INDEX_DIP_R | 0.0 | 0.0 | 0.0 |

```
before_equals_after (INDEX_PIP_R) = TRUE
R1A 改动的组 = {INDEX_MCP_R, THUMB_IP_R, WRIST_R}
R1A 未改动的组 = {INDEX_PIP_R, INDEX_DIP_R, 其余 FROZEN 四指组}
```

R1 完整向量：`{WRIST_R 0.000683, INDEX_MCP_R 0.999073, INDEX_PIP_R 0.000245, INDEX_DIP_R 0.0}`
R1A 完整向量：`{THUMB_IP_R 0.999755, INDEX_PIP_R 0.000245, INDEX_DIP_R 0.0}`

---

## 四、R1 来源

1. R1 的顶点归属权威是**二维最近链折线距离**（`OWN_V`）。在本姿态下拇指远端指骨贴着食指 MCP
   （两指链最小距离：CMC 段 44.29 mm / MCP 段 18.11 mm / **IP 段 3.28 mm**），
   于是 D\*=2189 被判为 **INDEX**。
2. `own = INDEX` ⇒ R1 允许集 = `{WRIST_R, INDEX_MCP_R, INDEX_PIP_R, INDEX_DIP_R}`，
   权重由纵向 `lam` 与横向 `mu` 的乘积归一化得到，得到
   `INDEX_MCP_R 0.999073 + WRIST_R 0.000683 + INDEX_PIP_R 0.000245`。
   `INDEX_PIP_R` 的 2.45e-04 即由此产生（`lam` 的远端尾巴，非独立语义决定）。
3. 该顶点同时被 R2A 远端 cap 认定为拇指 tip 顶点——**两套语义在 R1 中未被调和**。

---

## 五、为什么 R1A 未修改

```
INDEX_PIP_R ∈ FROZEN_FOUR_FINGER_GROUP
STAGE5B_R1A 授权范围：仅允许修改 WRIST_R / THUMB_CMC_R / THUMB_MCP_R / THUMB_IP_R / INDEX_MCP_R
                     且仅限授权拇指区域内的顶点
```

- R1A 已按授权修改了该顶点的 `INDEX_MCP_R`（0.999073 → 0）与 `THUMB_IP_R`（0 → 0.999755），
  并把归属修正为 THUMB（证据型归属：R2A 已批准远端 cap 顶点 ⇒ THUMB）。
- 但 `INDEX_PIP_R` 属**四指已通过权重**，本轮**无修改授权**；
  R1A 的构建脚本对 FROZEN 组采取“逐位复制、绝不参与任何归一化缩放”的硬化策略，
  因此该 2.45e-04 被**原样继承**。
- 该策略同时保证了 `FROZEN_FOUR_FINGER_GROUP_DRIFT = 0`（11 组 × 3416 顶点逐位相同），
  这是 HR 已批准的约束；清除本 residue 与该约束**在字面上互斥**。

---

## 六、为什么当前不值得解冻四指重做

| 维度 | 评估 |
|---|---|
| 量级 | 2.4507e-04（0.0245 %）——低于 R1 剪枝最小保留影响数，低于任何可观测形变阈值 |
| 语义 | `INDEX_PIP_R` 的 lam 远端尾巴，**不构成**对该顶点的主导/语义归属；R1A 后 dominant = `THUMB_IP_R` 0.99976 |
| 影响面 | 单点、单组；该顶点位于拇指远端 cap 正中，属于拇指 IP 完全支配区 |
| 修正代价 | 必须重开 `INDEX_PIP_R`（FROZEN 四指组）⇒ 需要四指重审 ⇒ 与“四指已 APPROVED、不得重开”直接冲突 |
| 风险 | 重算四指会破坏 `FOUR_FINGER_SKIN_WEIGHT = APPROVED` 的 provenance 与哈希链 |
| 收益 | 清除 0.0245 % 的历史残留 |

**结论**：收益 < 风险，且会违反本轮 scope。登记为 provenance 即可。
`CROSS_DIGIT_LEAKAGE` gate 在 R1A 中的判定为
`PASS_WITH_DOCUMENTED_CARRY_OVER_RESIDUE`（R1A 引入的跨指权重 = 0）。

---

## 七、传播禁令与未来清理

```
DO_NOT_PROPAGATE_AS_GENERAL_EXCEPTION
```

- 不得用本记录为任何**其它**顶点的跨指残留开脱；
- 不得用本记录为**未来阶段**（Stage6 / 左手镜像 / 任何重绑）的跨指污染开脱；
- 不得写成 `PASS AS DESIGNED`（这确实是 residue，不是设计目标）；
- 不得据此放宽 `GLOBAL_CROSS_DIGIT_GUARD`。

```
IF_THE_WHOLE_WEIGHT_SET_IS_EVER_REGENERATED = SHOULD_BE_CLEANED
```

若未来在**新授权**下整体重生成权重（例如重新审定四指权重、或改用新的归属权威），
该顶点必须满足：

1. 归属为 **THUMB**（证据型：R2A 已批准 thumb distal-cap 顶点）；
2. 权重向量**不含**任何 `INDEX_*` 组（`INDEX_PIP_R` 必须为 0）；
3. 预期结果：`{THUMB_IP_R: 1.0}`（该顶点弧长 93.9454 mm = 链全长，处于 IP 完全支配区）。

---

## 八、产物

```
stage5b_r1a/STAGE5B_R1A_VERTEX2189_CARRY_OVER_ERRATA.md          （本文件）
stage5b_r1a/_tmp/R1A_V2189_PROVENANCE.json                       （只读提取证据）
stage5b_freeze/STAGE5B_FREEZE_VERIFICATION_R1.json → vertex_2189  （内嵌于冻结校验）
```
