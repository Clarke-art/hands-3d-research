# STAGE5B_R1 — 生产蒙皮初始绑定与静态审计 · 阶段报告

- **阶段**：STAGE5B_R1_PRODUCTION_SKIN_WEIGHT_INITIAL_BINDING_AND_STATIC_AUDIT
- **日期**：2026-09-29（GMT+8）
- **运行环境**：Blender 5.1.2 (`D:\Blender\blender.exe`)，纯本地 EEVEE 渲染，无外部服务调用
- **输入 master**：`stage5a_r2a/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend`（唯一 active master）
- **输出 candidate**：`stage5b_r1/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1.blend`
- **状态结论**：**STAGE5B_R1 = READY_FOR_HUMAN_REVIEW**；`PRODUCTION_SKIN_WEIGHT_FINAL = NOT_YET_APPROVED`；`STAGE6 = NOT_STARTED`

---

## 一、阶段定位与输入门（PASS）

| 项 | 值 | 判定 |
|---|---|---|
| 上游 Stage5A_R2A | FINAL_APPROVED（stage5a_freeze 已签发） | PASS |
| R2A master 拓扑签名 | V=3416 / E=6828 / F=3414 / TRIS=6828 | PASS |
| R2A master 哈希 | `c4fafc56…c2845` | PASS（见 §六复核，未改动） |
| 骨骼总数 | 21（16 deform + 5 TIP helper `use_deform=false`） | PASS |
| 不进入 Stage6 | 仅 REST/ZERO-POSE 绑定与静态审计，不做 deform 测试 | PASS |

---

## 二、绑定动作（动作清单）

1. mesh `Hand  - Realistic` parent → `RIGHT_HAND_PRODUCTION_RIG`（matrix_parent_inverse 已写入，object transform 零漂移）。
2. 挂载 `PRODUCTION_ARMATURE` 修改器（ARMATURE 类型，指向 production rig）。
3. 建立 **16 个 deform 顶点组**（禁止为 5 个 TIP helper 建权重组）：
   `WRIST_R, THUMB_CMC_R, THUMB_MCP_R, THUMB_IP_R, INDEX_MCP_R, INDEX_PIP_R, INDEX_DIP_R, MIDDLE_MCP_R, MIDDLE_PIP_R, MIDDLE_DIP_R, RING_MCP_R, RING_PIP_R, RING_DIP_R, LITTLE_MCP_R, LITTLE_PIP_R, LITTLE_DIP_R`。
4. 写入**确定性初始权重**（非自动求解器、非手绘）：SEMANTIC REGION + BONE LOCAL DISTANCE + JOINT TRANSITION BLEND + GEODESIC/OWNERSHIP GUARD。
5. 权重剪枝（`MAX_NONZERO_INFLUENCES = 4`）→ 重归一化。
6. 零姿态校验 + 权重热图渲染（12 张）。

---

## 三、权重方法要点

- **链式骨权 bump**：每指沿弧长 `XIJ[D]` 布置高斯 bump `lam = exp(-((xi-mj)/κ)²)`，`κ = 0.5·Lj + 0.5·(τ_h+τ_t)`（τ 取自 T-01 joint region）。
- **WRIST 直线轴主导**：前臂侧 `lam=1` 绝对主导，作为掌/前臂背景权重。
- **守卫（4 项）**：
  - FOREARM GUARD：近端 `(v-wH)·wU < 0` → 仅 `WRIST_R`；
  - THUMB DISTAL OWNERSHIP GUARD：弧长 ≤ THUMB_IP 关节+τ 时 `THUMB_IP_R ≥ 2×others`，服从真实远端网格而非直线弦；
  - NAIL_THUMB_V 守卫：拇指甲床顶点（`material_index==1` 且 owner=THUMB）→ `THUMB_IP_R` 主导；
  - 首蹼 FIRST_WEB 白名单：仅 `WRIST_R/THUMB_CMC_R/THUMB_MCP_R/INDEX_MCP_R`，显式禁止 `THUMB_IP_R/INDEX_PIP_R/INDEX_DIP_R`。
- **掌根掌扇 PALM_FAN_OK**：允许 5 个 MCP 的 metacarpal fan（归入 sanctioned 跨指权重，不记为泄漏）。

---

## 四、静态审计结果（全部 PASS）

| # | Gate | 指标 | 结果 |
|---|---|---|---|
| G1 | 未权重顶点 | unweighted = 0 / 3416 | **PASS** |
| G2 | 负权 / NaN / Inf | neg = 0，nan_inf = 0 | **PASS** |
| G3 | 最大影响数 | max = 4（分布：1-inf 552，4-inf 2864，其余 0） | **PASS** |
| G4 | 归一化误差 | worst = 4.4005e-08 | **PASS** |
| G5 | 跨指泄漏 | 非授权泄漏 = 0 项 / 0 权重 | **PASS** |
| G5a | 授权掌扇 | 1193 项 / 39.2967 权重 | 合规 |
| G5b | 授权首蹼根混合 | 62 项 / 13.1760 权重 | 合规 |
| G6 | 指→前臂泄漏 | 0 项 | **PASS** |
| G7 | PIP/DIP→掌泄漏 | 0 项 | **PASS** |
| G8 | 零姿态绑定 | max delta = 5.967e-05 mm，mean 5.893e-06 mm，bbox 漂移 ≤ 7.451e-06 mm | **PASS** |
| G9 | 父级绑定 | world_delta = 0.0；修改器 `PRODUCTION_ARMATURE` 存在 | **PASS** |
| G10 | 首蹼审计 | 45 顶点；白名单干净；violations = [] | **PASS** |
| G11 | 指甲审计 | 189 顶点；index/middle/ring/little = 100%；thumb 20/22（2 个 web 边界例外，已记录） | **PASS（附记录）** |
| G12 | 权重剪枝 | 6→4；1690 顶点被剪；丢弃权重 0.2986；最坏单点丢弃 0.0954 | **PASS** |
| G13 | 拓扑漂移 | V/E/F/TRIS 全 0 漂移；UV/材质/指甲面 0 漂移 | **PASS** |

### 指甲审计说明（G11）
- thumb 2 个例外顶点（#1383 主权 WRIST_R、#2740 主权重 INDEX_MCP_R）均位于**拇指–食指 web 边界**，该处 WRIST_R/INDEX_MCP_R 主导属几何合理，非错误，记录于 `NAIL_WEIGHT_AUDIT.json`。
- 四指指甲 100% 由对应 DIP 骨主导，符合预期。

---

## 五、关键权重统计（节选）

| 骨组 | 非零顶点 | 权重和 | max | 说明 |
|---|---|---|---|---|
| WRIST_R | 3416 | 1561.41 | 1.000 | 全网格背景权重 |
| THUMB_CMC_R | 1244 | 81.54 | 0.362 | CMC/thenar 与腕共享，max 受控 |
| THUMB_MCP_R | 645 | 44.84 | 0.296 | 同上 |
| THUMB_IP_R | 604 | 411.81 | 0.998 | 远端所有权守卫生效，mean 0.682 |
| INDEX_MCP_R | 524 | 153.78 | 0.999 | — |
| INDEX_PIP_R | 344 | 65.32 | 0.852 | — |
| INDEX_DIP_R | 344 | 112.96 | 0.996 | — |
| MIDDLE_MCP_R | 906 | 129.90 | 0.998 | 掌扇最大承载 |
| RING_MCP_R | 785 | 148.71 | 0.994 | — |
| LITTLE_MCP_R | 898 | 166.07 | 0.974 | — |

（其余 MCP/PIP/DIP 组详见 `STAGE5B_R1_WEIGHT_STATS.json`）

---

## 六、哈希复核（执行前后）

| 文件 | SHA-256 | 判定 |
|---|---|---|
| R2A master（输入，未改动） | `c4fafc56c591411bb5ddf07bde44b5fcd6e6a9aa5e0d43b22f9734c0884c2845` | 与冻结台账一致 ✅ |
| Stage5B candidate（输出） | `8f4c6901fdae417e3855d388f9739ebea10863f0ebdbfedf0df8d79a751c308d` | 新产物，已记录 ✅ |

> 渲染脚本仅 `write_still` 输出 PNG，未回存 .blend，故 candidate 磁盘哈希与绑定产物一致。

---

## 七、渲染证据（12 张权重热图）

- 路径：`stage5b_r1/renders/`
- 数量：12 张 PNG，总占用 **9,285,581 字节（≈ 8.85 MB）**
- 清单：
  `STAGE5B_R1_WEIGHT_WRIST` / `THUMB_CMC` / `THUMB_MCP` / `THUMB_IP` / `INDEX_MCP` / `INDEX_PIP` / `INDEX_DIP` / `FIRST_WEB` / `PALM_FAN` / `CROSS_DIGIT_LEAK` / `BIND_OVERVIEW_DORSAL` / `BIND_OVERVIEW_PALMAR`

> 过程记录：首跑因 `make_legend` 中 `el = list(cr.color_ramp.elements)` 为静态快照、`while len(el) < 5` 永不更新导致死循环直至色带 32 元素上限抛 `RuntimeError`；已改为按差值 `need = 5 - len(el)` 增量添加并修正 `s5b_r1_render.py`（第 152–158 行），重跑全 12 张成功。该改动仅影响图例材质构造，不影响权重数据。

---

## 八、结论与状态

- **STAGE5B_R1 = READY_FOR_HUMAN_REVIEW**：绑定、16 组确定性权重、静态审计（G1–G13 全 PASS）、零姿态校验、12 张热图证据均已齐备。
- **PRODUCTION_SKIN_WEIGHT_FINAL = NOT_YET_APPROVED**：待人工评审（HR）确认后转 `APPROVED`，方可进入 Stage6 deform 测试。
- **STAGE6 = NOT_STARTED**：本阶段不进入 GATE3 deform 测试。
- 拇指远端所有权按 Stage5A_R2B 勘误后的 canonical 语义（`THUMB_IP_TO_TIP_STRAIGHT_CHORD_CONTAINMENT = DIAGNOSTIC_ONLY`）处理；本阶段骨架绑定与权重分配均遵循该约束，权重层面拇指远端跟随 `THUMB_IP_R` 已验证（G11 thumb 20/22，2 例 web 边界例外已记录）。

---

## 九、动作清单（allow / disallow）

**ALLOW（本次已执行）**
- 以副本形式新建 `RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1.blend`，parent + Armature 修改器 + 16 顶点组 + 确定性权重。
- 生成全套静态审计 JSON 与 12 张权重热图。
- 修正渲染脚本图例构造 bug（仅脚本，不动权重/几何）。
- 复核 R2A master 哈希未变。

**DISALLOW（本阶段禁止 / 待 HR）**
- 不得修改 R2A master 任何内容（哈希已锁定）。
- 不得为 5 个 TIP helper 建立 deform 权重组。
- 不得进入 Stage6 deform 测试，直至 `PRODUCTION_SKIN_WEIGHT_FINAL = APPROVED`。
- 不得因 THUMB distal chord 例外而放宽四指原 containment Gate。

---

## 十、产物清单

```
stage5b_r1/
├── RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1.blend        (2,307,647 B, sha 8f4c6901…)
├── STAGE5B_R1_REPORT.md                            (本报告)
├── STAGE5B_R1_STATUS.json                          (机器可读状态)
├── STAGE5B_R1_WEIGHT_STATS.json
├── STAGE5B_R1_VERTEX_INFLUENCE_AUDIT.json
├── JOINT_WEIGHT_TRANSITION_TABLE.json
├── FIRST_WEB_WEIGHT_AUDIT.json
├── CROSS_DIGIT_WEIGHT_LEAK_AUDIT.json
├── NAIL_WEIGHT_AUDIT.json
├── WEIGHT_PRUNE_AUDIT.json
├── ZERO_POSE_BIND_AUDIT.json
├── PARENT_BIND_AUDIT.json
├── renders/  (12 × PNG, 9,285,581 B 合计)
├── scripts/  (s5b_r1_bind.py / s5b_r1_audit.py / s5b_r1_render.py)
└── _tmp/     (S5B_R1_AUDIT_LOG / BUILD_LOG / TOPOLOGY_DRIFT.json)
```
