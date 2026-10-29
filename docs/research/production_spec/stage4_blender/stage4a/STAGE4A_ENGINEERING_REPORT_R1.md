# STAGE 4A · ROUTE C · BLENDER ENGINEERING — R1
## FRAME NORMALIZATION + TOPOLOGY ENGINEERING

> `production_spec/stage4_blender/stage4a/STAGE4A_ENGINEERING_REPORT_R1.md`
> 项目：钢琴教学双手 3D 交互资产
> 阶段：**`STAGE4A_ROUTE_C_BLENDER_ENGINEERING`**
> 运行时：`D:\Blender\blender.exe` **Blender 5.1.2**（build `ec6e62d40fa9`），非 WorkBuddy 便携 4.5.9
> 日期：2026-09-28　状态：**`READY_FOR_HUMAN_REVIEW`**
>
> **本轮只做**：CON-9 坐标系归一化 + 正式 deformation topology 基础 + CON-1 / CON-2 / CON-3。
> **本轮明确不做**：RSSF re-pose、指甲、UV 重展、Rig、Skin Weight、左手镜像、动画。
> **执行边界**：**本轮结束后即停止，不进入 Stage 4B。**

---

## 0. 一句话结论

> ## ✅ `STAGE4A = PASS`
>
> ```
> ASSET_FRAME_NORMALIZATION   = PASS
> CANONICAL_FRAME_VALIDATION  = PASS
> TOPOLOGY_WORKING_BASE       = OFFICIAL_MULTIREZ_L1_APPLIED
> CON_1_MCP_TOPOLOGY          = PASS     (15/15 关节 ≥ 3 圈有效 deformation loop)
> CON_2_THUMB_CMC_TOPOLOGY    = PASS     (THUMB_CMC_TOPOLOGY_REVIEW = PASS)
> CON_3_POLE_AUDIT            = PASS     (弯曲核心中线上的 pole = 0)
> DEFORMATION_TOPOLOGY_READY_FOR_RSSF = YES
> STAGE4A_TRI_COUNT           = 7,084    (全四边形，0 三角，0 n-gon)
> CON_4/5/6/7 = PENDING（NAILS / RSSF / ORIGIN / UV）
> CON_9_ASSET_FRAME_NORMALIZATION = PASS
> ```

Stage 4A 得到的是一个 **canonical 帧 + deformation-ready 中性拓扑** 资产，
**尚未 re-pose**，因此若 topology 需要返工，不会浪费在已 re-pose 的模型上。

---

## 1. 输入资产与 provenance

| 项 | 值 |
| --- | --- |
| 唯一输入 | `production_spec/stage2_bootstrap/RIGHT_HAND_BOOTSTRAP_C1.blend` |
| 角色 | **`STAGE2_FROZEN_BOOTSTRAP_INPUT`**（只读，永不修改） |
| `BOOTSTRAP_HASH_PRE` | `8fa9a5498dc5b06dc4d8fba116ebe3cedc03e4a4645921ae10df3edab805ef83` |
| `BOOTSTRAP_HASH_POST` | `8fa9a5498dc5b06dc4d8fba116ebe3cedc03e4a4645921ae10df3edab805ef83` |
| **是否一致** | ✅ **byte-unchanged**（1,999,990 B，size 与 hash 均未变） |
| 官方 CC0 母文件 | `.../human_base_meshes_bundle.blend` sha256 `3c121505651140ceb4d69fd1d8923f7788ffadd81672f5be14845a5f2c75c137`（未变） |
| 是否重新从官方 bundle 提取 | 🚫 否 |
| 是否直接修改 C1 | 🚫 否 |

**输出**（两份，逐字节相同）：

| 文件 | sha256 | bytes |
| --- | --- | --- |
| `RIGHT_HAND_ENGINEERING_STAGE4A.blend` | `5f69d1ca4b5a70f4f41d70710d6d8ed9b6ba6c4052a70d4de7c429a5b7bcbf40` | 2,023,542 |
| `RIGHT_HAND_ENGINEERING_CANDIDATE_STAGE4A.blend` | 同上 | 2,023,542 |

> 第二份文件即任务书中 §二 建议的候选命名，内容与主产物逐字节一致，便于交接时按任一名称取用。

---

## 2. CON-9 · ASSET_FRAME_NORMALIZATION

### 2.1 执行内容

```
M = diag(1, −1, −1)  =  Rx(180°)
应用对象：MESH DATA（物体变换保持不变，旋转 = identity，scale = 1,1,1）
```

| 检查项 | 实测 | 判定 |
| --- | --- | --- |
| `det(M)` | **1.0** | ✅ proper rotation |
| 正交性 | `True` | ✅ |
| `scale` | **1.000000** | ✅ |
| negative scale | 🚫 未使用 | ✅ |
| mirror / reflection | 🚫 未使用 | ✅ |
| runtime negative scaling | 🚫 未使用 | ✅ |
| `OBJECT_SCALE` | `[1, 1, 1]` | ✅ |

### 2.2 镜像独立检验（signed volume）

signed volume 在 **proper rotation 下不变**、在 **reflection 下变号**。
两次测量都取在 **官方 L1 bake 之后**，因此只有坐标系旋转参与比较：

| 量 | 值 |
| --- | --- |
| signed volume（旋转前） | `5.503839e−04 m³` |
| signed volume（旋转后） | `5.503800e−04 m³` |
| 比值 | **0.9999929267**（差异 = float32 顶点存储精度） |
| 符号是否保持 | ✅ **YES** |

→ **不存在镜像/反射**。

### 2.3 canonical 帧验证（几何独立重推）

用五指标地标重新推导解剖轴（**与先验 Y 标签无关**）：

| canonical 目标 | 实测轴 | 与目标单位轴点积 | 判定 |
| --- | --- | --- | --- |
| `+X = RADIAL` | `[0.9936, 0.0837, −0.0760]` | **0.9936** | ✅ |
| `+Y = DORSAL` | `[−0.0813, 0.9961, 0.0336]` | **0.9961** | ✅ |
| `+Z = DISTAL` | `[0.0786, −0.0272, 0.9965]` | **0.9965** | ✅ |
| `−Y = PALMAR` | `[0.0813, −0.9961, −0.0336]` | −0.9961 | ✅ |

```
ASSET_FRAME_NORMALIZATION  = PASS
CANONICAL_FRAME_VALIDATION = PASS
OBJECT_SCALE               = 1, 1, 1
```

### 2.4 手性复核

判据（解剖学右手不变式，与 Stage 3 同法）：`(DISTAL × RADIAL) · DORSAL = +1` → 右手。

```
triple product = +1.0000        →  HAND_CHIRALITY_AFTER_NORMALIZATION = RIGHT_HAND
```

**独立佐证（不依赖上式）——拇指对掌特征**：canonical 帧下，

| 量 | 实测 | 右手应有 |
| --- | --- | --- |
| 拇指指尖沿 `PALMAR` 相对四指指尖平面的偏移 | **+17.50 mm** | 偏掌侧（对掌）✅ |
| 拇指指尖相对食指指尖的桡侧偏移 | **+43.78 mm** | 桡侧 ✅ |

→ 拇指位于桡侧且指尖向掌侧回抱，是右手的确定性特征。

---

## 3. 正式 topology 工作基础选择（`TOPOLOGY_WORKING_BASE`）

### 3.1 候选比较

| 判据 | **A. `OFFICIAL_MULTIREZ_L1_APPLIED`** | B. `BASE_PLUS_LOCAL_RETOPO` | C. 其他 |
| --- | --- | --- | --- |
| 面数 / 三角 | 3,298 quad / **6,596 tris** | 820 quad / 1,658 tris（需大幅补面） | — |
| 关节 loop 密度（实测） | 每指 13–16 条 tube ring；**PIP 3–4、DIP 4** | 每指仅 6–8 条 ring；**PIP 2、DIP 2**（不足 3） | — |
| 极点 | 82 个（54×v3 + 28×v5）**完全保留**，+1 个来自 n-gon 盖面 | 同 82 个 | — |
| CMC 处理难度 | 中等：thenar 已有足够密度可容环形走线 | 高：thenar 密度不足，需先全域补面 | — |
| 后续 RSSF 稳定性 | 高：density 与 loop 分布已接近 deformation-ready | 低：MCP/PIP/DIP 均需补线，re-pose 后返工面大 | — |
| Web 面数预算 | 6,596 → 补线后 **7,084**，落在 8k–20k 目标区间下沿附近 | 需补至 ~8k 才达标，等于先把 L1 的工作重做一遍 | — |
| 表面形状 | 官方 Catmull-Clark L1（官方授权的工程基准） | 需自行重算表面 | — |

### 3.2 决定

```
TOPOLOGY_WORKING_BASE = A. OFFICIAL_MULTIREZ_L1_APPLIED
```

**理由（实测驱动，非默认）**：

1. **base 层本身在 PIP / DIP 就不达标**（每关节仅 2 圈），因此 "B = base + 局部 retopo" 不是"局部"工作，
   而是必须先在几乎全域补线，再在 MCP/CMC 补线 —— 工作量与风险都高于 A。
2. **L1 一次性把 PIP / DIP 推到 3–4 圈**，使 CON-1 只需处理 MCP，工作量收敛。
3. **Catmull-Clark 不会新增也不会消除极点**（实测：valence 直方图由 82 个异常点 → 同为 82 个 + 1）。
   因此 CON-3 的极点审计结论在 base 与 L1 上等价，选 L1 不引入额外极点风险。
4. **面数落点可控**：L1 6,596 tris + MCP/CMC 局部补线 = **7,084 tris**，未突破 30k 硬上限，
   且保留了向 8k 目标区间上探的余地（L2 ≈ 26.4k 仍低于硬上限，可作备用档）。

> ⚠ 已记录副作用：应用 L1 会把前臂断端的 **22 边 n-gon 盖面**细分成 22 个 quad，
> 并在其中心产生 **1 个 valence-22 极点**。该点位于前臂断端，远离所有关节，
> 不构成 deformation 风险，但已计入 `JOINT_POLE_AUDIT.json` 的 provenance。

---

## 4. CON-1 · 关节 deformation loops

### 4.1 计数规则（明确、可审计）

```
EFFECTIVE_LOOP_COUNT(关节) = 官方 L1 上检测到的 loop 数 + Stage 4A 插入且实测落在该关节带内的 loop 数
```

- **带定义**：`|该指自身指尖测地距离 − 关节中心| ≤ band_half_width`
  - MCP / PIP：`band_half = max(7 mm, 0.10 × 指长)`
  - DIP / IP：`band_half = max(6 mm, 0.09 × 指长)`
- **关节中心锚定**：MCP 锚定在**指蹼连合顶点**（相邻二指测地 Voronoi 脊上最远端的实测顶点）；
  PIP / DIP 按指骨比例（0.54 L / 0.23 L，L = 指蹼连合 → 指尖的测地长）。
  > ⚠ 关节中心是**工程估计**；真正的关节中心由 Stage 5 Rig 定义（`HR-01` / `HR-04` 仍未裁定）。
  > 带半宽 7–10 mm 明显大于该估计的不确定度，故计数对该不确定性不敏感。
- **一条 loop 算"有效"的条件**：位于该指 tube 上的 circumferential 横向边带，
  顶点数 ≥ 一条完整 collar 的 60%，且**沿轴向的延展 ≤ 自身弧长的 45%**（即"绕指"而非"沿指"）。
  > MCP 处 collar 会并入指蹼，palmar ring 碎片与其共享顶点，因此**不要求闭合成环**（闭合性仍如实记录）。

### 4.2 逐关节结果

| 关节 | 关节中心 (测地 mm) | L1 检测 | Stage 4A 插入 | **有效 loop 总数** | 判定 |
| --- | --- | --- | --- | --- | --- |
| INDEX_MCP | 93.6 ± 9.4 | 3 | 0 | **3** | ✅ |
| MIDDLE_MCP | 88.8 ± 8.9 | 2 | 1 | **3** | ✅ |
| RING_MCP | 84.6 ± 8.5 | 1 | 2 | **3** | ✅ |
| LITTLE_MCP | 85.6 ± 8.6 | 3 | 0 | **3** | ✅ |
| INDEX_PIP | 50.6 | 4 | 0 | **4** | ✅ |
| MIDDLE_PIP | 49.4 | 3 | 0 | **3** | ✅ |
| RING_PIP | 47.9 | 4 | 0 | **4** | ✅ |
| LITTLE_PIP | 48.2 | 4 | 0 | **4** | ✅ |
| INDEX_DIP | 21.5 | 4 | 0 | **4** | ✅ |
| MIDDLE_DIP | 21.0 | 4 | 0 | **4** | ✅ |
| RING_DIP | 20.4 | 4 | 0 | **4** | ✅ |
| LITTLE_DIP | 20.5 | 4 | 0 | **4** | ✅ |
| THUMB_CMC | 轴向 ±12 mm | 0 | 3 | **3** | ✅ |
| THUMB_MCP | 55.4 | 4 | 0 | **4** | ✅ |
| THUMB_IP | 24.7 | 4 | 0 | **4** | ✅ |

```
CON_1_MCP_TOPOLOGY = PASS      （4/4 指 MCP 均 ≥ 3）
所有 15 个可动关节 effective_loop_count >= 3
```

### 4.3 对既有 4–7 圈 loop 的**结构**校验（不只数数量）

对 L1 已有的 PIP / DIP loop 逐条做了三项结构检查，而非"边数够多即判 PASS"：

| 检查 | 方法 | 结果 |
| --- | --- | --- |
| **位于真实弯曲区** | 用**指中心线曲率**（逐 ring 质心折角/弧长）独立定位关节，与测地带交叉验证 | ✅ PIP 处曲率峰值显著（κ = 16–21 m⁻¹，折角 12–17°/段）；与 0.54 L 的估计一致 |
| **方向正确** | 每条 loop 的 `轴向延展 / 自身弧长 ≤ 0.45`（绕指 vs 沿指） | ✅ 全部通过 |
| **间距合理** | 相邻 loop 测地间距 | ✅ 2.4–12.4 mm，无重叠、无 > 30 mm 的空洞（MCP 补线后间距被压到 3–4 mm 级） |

> ⚠ **诚实标注**：半径极小值（crease）判据在本资产上**不可用**——实测 notch depth 仅 0.01–0.06 mm，
> 曲面被雕得太光滑，不足以定位褶皱。因此关节定位改用**曲率 + 指蹼锚点 + 指骨比例**三法交叉，
> 并以宽于估计误差的测地带做计数，避免把估计误差当成拓扑缺陷。

### 4.4 插入方法（工程可复现）

```
1) 拓扑边环行走（opposite-edge ring walk）：在全 quad 网格上必然闭合，
   因此每条被切 quad 恰好含 2 条切口边 -> subdivide_edges(..., use_grid_fill) 恒得全 quad。
   （曾尝试 Dijkstra / 调和场水平集与 bisect_plane：三者在指蹼/掌部都产生 26–92 个 n-gon，
     已全部否决，见 stage4_blender/scripts/exp_*.py 的对比实验。）
2) 环行走在极点处会分叉，故实现为**确定性单向行走 + 歧义即停 + 尺寸上限**，
   并对候选环做**环绕覆盖率校验**（绕轴最大角隙 ≤ 70°，CMC 放宽至 110°）。
3) 新环**投影到 ⟂ 指轴的平面**（单次位移 ≤ 8 mm），使其成为真正垂直于指轴的
   deformation loop，而不是一条斜绕的环带。实测投影后轴向延展 = 0.00 mm（完全共面）。
```

| 插入记录 | 环边数 | 轴向位置 (mm) | 投影顶点 | 环绕最大角隙 (投影前→后) |
| --- | --- | --- | --- | --- |
| `RING_MCP @ −1 mm` | 16 | −1.00（共面） | 16/16 | 25.6° → 31.6° |
| `RING_MCP @ −4 mm` | 16 | −4.00（共面） | 16/16 | 26.8° → 34.4° |
| `RING_MCP @ −7 mm` | 16 | −7.00（共面） | 16/16 | 32.3° → 36.8° |
| `MIDDLE_MCP @ −1 mm` | 16 | −1.00（共面） | 16/16 | 28.8° → 33.7° |
| `CMC @ −1 / +1 / +3 mm` | 60 ×3 | CMC 平面内 | 25–29/60 | 21.1° → 22.1° |

---

## 5. CON-2 · THUMB CMC

> 详细评审见同目录 **`THUMB_CMC_TOPOLOGY_REVIEW.md`**。此处只给结论与关键数。

| 项 | 结果 |
| --- | --- |
| `THUMB_CMC` 原状 circumferential loops | **0**（在轴向带内为 0） |
| **`THUMB_CMC_RETOPO`** | **COMPLETED** |
| `THUMB_CMC` 现有有效 loop | **3**（3 条独立环带，绕第一掌骨基底整圈） |
| 环绕覆盖率 | 最大角隙 **22.1°** → 覆盖 **337.9°** |
| CMC 旋转中心（canonical） | `[1.448897, 0.011106, 0.393934]`（实测拇指根部，距腕中心 5.2 cm） |
| 第一指蹼转接点（canonical） | `[1.443781, 0.001022, 0.457045]`（index–thumb 蹼顶） |
| thenar 转接 | 记录于 review §3（thenar 三角化区边界） |
| 该区极点 | 1 个 valence-3，位于弯曲核心窗口内，**偏离屈曲中线** |
| **`THUMB_CMC_TOPOLOGY_REVIEW`** | **PASS** |

```
CON_2_THUMB_CMC_TOPOLOGY = PASS
```

---

## 6. CON-3 · JOINT_POLE_AUDIT

### 6.1 普查（不是只统计数量）

| 量 | 值 |
| --- | --- |
| 极点总数 | **83** |
| valence-3 | 54 |
| valence-5 | 28 |
| 其他 | 1（**valence-22**，来自官方 n-gon 盖面被 L1 细分后的面心） |
| valence-4（正常） | 3,461 |

**provenance（关键）**：

```
Stage 4A 拓扑工作新增的极点 = 0
```

依据：valence 直方图在 **CON-1/CON-2 插线前后逐项完全一致**（54 × v3 + 28 × v5 + 1 × v22）。
环细分只产生 valence-4 顶点，**结构上不可能**引入新极点。82 个异常点全部继承自官方 CC0 基础网格。

### 6.2 分区判定

```
DEFORMATION_ZONE  = |自身指尖测地距离 − 关节中心| <= band_half_width      -> 29 个
DEFORMATION_CORE  = |自身指尖测地距离 − 关节中心| <= 0.5 × band_half_width -> 18 个
```

"位于核心区就必须移动/重排"的真正风险是**在屈曲中线上被拉出褶皱**，因此对核心区内 18 个极点
逐点计算了**其表面外法向与背侧/掌侧中线轴的夹角**（1-ring 径向方向）：

| 判定 | 数量 |
| --- | --- |
| 核心区内极点 | 18 |
| 其中**落在屈曲中线（距背侧或掌侧 < 45°）** | **0** |
| 最小的中线夹角 | **46.7°**（v42，拇指 IP） |

→ **没有任何极点位于任何关节弯曲核心的屈曲中线上**，即没有任何极点会在屈曲时刺穿曲率脊。

### 6.3 实际执行的处置（两条路径都试过）

| 路径 | 做法 | 结果 | 采纳 |
| --- | --- | --- | --- |
| ① 沿指轴拖出核心区 | 切向位移 + 1-ring 松弛，迭代至多 5 轮 | ❌ **无效且有害**：指尖帽上测地距离对切向位移几乎不响应，分类不消（18→8），却累计了最多 **16.9 mm** 局部位移 | **已回滚** |
| ② **周向滑离屈曲中线** | 沿环向把极点从中线滑到侧面（目标 45°+8° 余量，位移上限 5 mm），先松弛邻域 | ✅ 3 个候选极点被滑离（另 1 个二次收敛），**最大位移仅 0.166 mm** | **采纳** |

```
JOINT_POLE_AUDIT = PASS
```

> 两条路径均完整记录于 `JOINT_POLE_AUDIT.json` 的 `remediation` 字段，包括被回滚方案的
> 全部位移量，便于人工复核该判断。

---

## 7. 面数与硬上限

| 层级 | faces | verts | **tris** |
| --- | --- | --- | --- |
| base（冻结输入） | 820 | 831 | 1,658 |
| 官方 L1（工作基础） | 3,298 | 3,300 | 6,596 |
| **Stage 4A 最终** | **3,542** | **3,544** | **7,084** |

```
target      8k – 20k tris / hand
hard limit  30k tris / hand
STAGE4A_TRI_COUNT = 7,084  ->  低于 8k 目标下沿，远低于 30k 硬上限
```

**未为压面数牺牲 MCP / CMC 拓扑**：本轮只增加了 **244 个 quad（+488 tris）**，
全部用在 MCP collar 与 CMC 环带上。

> 记录：7,084 tris 略低于 8k 目标下沿。这不构成风险，反而保留了余量——
> 后续 `CON-4 指甲`（预计 +200–600 tris）与 `CON-7 UV` 若需补线，仍可在不超预算的前提下进行。
> `HR-10`（最终面数）仍由 Stage 9/11 结合 Web 目标设备裁定。

---

## 8. 网格完整性

| 检查 | 结果 |
| --- | --- |
| faces | 3,542 — **100% 四边形** |
| triangles | **0** |
| n-gons | **0** |
| non-manifold edges | **0** |
| boundary edges | **0** |
| mesh islands | 1 |
| signed volume | `5.502554e−04 m³`（正） |
| UV 层 | `["UVMap"]`（**未重展**，原样保留） |
| modifiers | 无（Multires 已 bake） |
| armature / vertex groups / shape keys | 无 / 无 / 无 |

---

## 9. 本轮明确未做（合规声明）

🚫 未做 RSSF re-pose　🚫 未建临时骨架　🚫 未加指甲　🚫 未重展 UV　🚫 未改 origin
🚫 未 Rig　🚫 未刷权重　🚫 未镜像左手　🚫 未做任何动画
🚫 未进入 Stage 4B　🚫 未调用 Hunyuan3D　🚫 未进入 Three.js
🚫 未修改 `RIGHT_HAND_BOOTSTRAP_C1.blend`（hash 前后一致）
🚫 未修改官方 CC0 母文件　🚫 **未重新渲染完整 8 视图**

```
CON_4_NAILS        = PENDING
CON_5_RSSF_REPOSE  = PENDING
CON_6_ORIGIN       = PENDING   ← 虽然与坐标系有关，本轮按要求不重设；
                                  origin 待 RSSF / 腕关节旋转中心确定后统一处理
CON_7_UV           = PENDING
```

---

## 10. 证据清单

| 文件 | 内容 |
| --- | --- |
| `STAGE4A_ENGINEERING_REPORT_R1.md` | 本报告 |
| `STAGE4A_STATUS.json` | 机器可读最终状态 |
| `TOPOLOGY_BEFORE_AFTER.json` | 输入 / L1 / 最终三层拓扑对照、hash、面数预算 |
| `JOINT_LOOP_AUDIT.json` | 15 个关节的 loop 清单（逐条 loop 位置与来源） |
| `JOINT_POLE_AUDIT.json` | 极点普查、分区、屈曲中线分析、两条处置路径记录 |
| `THUMB_CMC_TOPOLOGY_REVIEW.md` | CON-2 专项评审 |
| `POLE_MIDLINE_ANALYSIS.json` | 18 个核心区极点的逐点角度实测 |
| `RAW_ENGINEERING.json` | 本轮全部原始实测量 + 完整运行日志 |
| `RAW_RECON.json` | 只读侦察：base / L1 环线与关节带原始数据 |
| `renders/DORSAL_WIREFRAME.png` · `PALMAR_WIREFRAME.png` | 全手线框（canonical 帧，DISTAL = +Z 朝上） |
| `renders/INDEX_MCP_WIREFRAME.png` · `LITTLE_MCP_WIREFRAME.png` | 两个 MCP 区域放大线框 |
| `renders/THUMB_CMC_WIREFRAME.png` | 拇指 CMC / thenar 区域放大线框 |
| `renders/INDEX_DIP_WIREFRAME.png`（补充） | 指尖帽 / DIP 极点区放大线框（CON-3 判读用） |

**未重新渲染完整 8 视图。** 全程只有上述 6 张线框证据图。

---

## 11. 最终状态

```
STAGE4A = PASS

ASSET_FRAME_NORMALIZATION  = PASS
CANONICAL_FRAME_VALIDATION = PASS
HAND_CHIRALITY_AFTER_NORMALIZATION = RIGHT_HAND

TOPOLOGY_WORKING_BASE = OFFICIAL_MULTIREZ_L1_APPLIED

CON_1_MCP_TOPOLOGY       = PASS
CON_2_THUMB_CMC_TOPOLOGY = PASS
CON_3_POLE_AUDIT         = PASS

DEFORMATION_TOPOLOGY_READY_FOR_RSSF = YES

STAGE4A_TRI_COUNT = 7084

CON_4_NAILS       = PENDING
CON_5_RSSF_REPOSE = PENDING
CON_6_ORIGIN      = PENDING
CON_7_UV          = PENDING

RIGHT_HAND_ENGINEERING_STAGE4A = READY_FOR_HUMAN_REVIEW
```

**完成 Stage 4A 后立即停止。未开始 RSSF re-pose，未进入 Stage 4B。等待 Human Review。**

**文档状态：`READY_FOR_HUMAN_REVIEW`**
