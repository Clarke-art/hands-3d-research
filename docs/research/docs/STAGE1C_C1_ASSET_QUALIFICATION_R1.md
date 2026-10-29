# Stage 1C · C-1 资产资格审查（真实文件级）· R1

> `docs/STAGE1C_C1_ASSET_QUALIFICATION_R1.md`
> 项目：钢琴教学双手 3D 交互资产
> 阶段：**`STAGE1C_C1_ASSET_QUALIFICATION`**
> 日期：2026-09-27　状态：**`READY_FOR_HUMAN_REVIEW`**
>
> **本轮只做：文档事实性更正 / 获取官方资产 / 真实文件级资格审查 / 证据渲染 / 判定。**
> **本轮不做：正式 re-pose、Retopo、Rig、权重、动画、Hunyuan3D 调用、Three.js、Stage 0 修改。**
>
> **执行依据（人工审核结论）**：`HQ-1 = CONDITIONAL_APPROVE`（批准进入实际资产资格审查，未批准成为正式母版来源）；
> `HQ-2 / HQ-3 / HQ-4 = DEFER`；`HQ-5`：真人 8 视图不再预设为未来强制条件。
> 配套证据目录：`production_spec/stage1c_c1_qualification/`、`references/licenses/blender_human_base_meshes/`

---

## 0. 本轮一句话结论

> ## `C1_ASSET_QUALIFICATION = CONDITIONAL_PASS`
>
> Blender 官方 Human Base Meshes v1.4.1 中**确实存在**独立的 realistic hand 资产（实际名称 **`Hand  - Realistic`**，831 顶点 / 819 四边面 / 封闭流形 / CC0），
> **解剖结构无关键错误**（五指、比例、拇指列、掌心弓、指蹼、指尖、右手手性、成人中性 全部通过），
> **已含腕 + 9.2 cm 短前臂**（无需延长）；
> 但**存在三项可明确修复的问题**，因此**不能判 PASS**：
> ① **关节环线密度不足**（base 层每关节仅 0–2 圈；应用资产自带的 1 级细分后 PIP/DIP 达标，**MCP 区与拇指 CMC 仍需局部补线**）；
> ② **拇指 CMC 放射状拓扑未获证实**（该区 0 条拇指轴环线，极点集中在过渡区）；
> ③ **无指甲几何**（需 Stage 4 补浅甲面）。
> 姿态方面：当前为"近完全伸展"姿态 → RSSF 需 **MODERATE** 旋转量（**纯临时骨架可完成，无需雕刻**）。

---

## 1. 第一部分：Stage 1B 文档事实性更正（只改两份指定文档）

**仅修改**（未触碰任何 Stage 0 冻结文档）：
- `docs/STAGE1B_SHARED_3D_BOOTSTRAP_ROUTE_SELECTION_R1.md`
- `docs/STAGE1B_HUNYUAN_SINGLE_IMAGE_TEST_CONTRACT_R1.md`

两份文档均已加入 **修订记录** 段落（状态仍为 `READY_FOR_HUMAN_REVIEW`，未改结论）。

### 1.1 更正 ①：姿态表述

| 项 | 内容 |
| --- | --- |
| **删除/改写** | 原句"任何路线的姿态都必须人工做，AI 给不了"（选路文档 §0 关键认知） |
| **改为** | **"AI 可以从输入图近似继承姿态，但无法可靠、可审计地保证符合冻结的 RSSF 技术范围（`HR-06b`/`HR-06c`）。因此最终 RSSF 必须人工验证，必要时在 Blender 中重新摆姿。"** |
| 连带修正 | 合同文档 §0 排除项表中原"母版姿态（RSSF）必须由人工完成，任何 AI 输出都做不到"→ 同步改为"最终 RSSF 必须人工验证，必要时在 Blender 中重新摆姿；AI 无法可靠、可审计地保证符合 RSSF 技术范围" |

### 1.2 更正 ②：Hunyuan3D 3.1 `FaceCount`

| 项 | 内容 |
| --- | --- |
| **官方实测值（腾讯云文档）** | `FaceCount` 取值范围 **3000–1500000**（官方参考值），默认 **500000** |
| **删除** | "约 40k 是最低面数"（选路文档 §5.3 参数表行） |
| **改为** | "官方 `FaceCount` 范围为 **3000–1500000**（默认 500000）；本实验固定 **100000 = `PROJECT TEST VALUE`**，**不是接口最低值**" |
| 合同同步 | `FaceCount = 100000` 一格明确标注 **`PROJECT TEST VALUE`（非接口最低值）**；继续作为本实验固定目标值 |

### 1.3 更正 ③：`GenerateType`

| 项 | 内容 |
| --- | --- |
| **事实** | **Model 3.1 下 `LowPoly` 不可用**；**官方参数枚举中仍然列有 `Sketch`** |
| **删除** | "3.1 已移除 `LowPoly` / `Sketch`"（选路文档 §5.1）与"不要使用 `Sketch`（3.1 已不支持…）"（合同 §2） |
| **改为** | Model 3.1 下 `LowPoly` 不可用；`Sketch` **在本项目本轮实验中禁止使用**，禁止名称为 **`PROHIBIT_SKETCH_FOR_THIS_EXPERIMENT`**，理由是**它不符合本轮单图 Geometry-only 实验设计**（且会丢失解剖依据） |
| **明确不写** | 文档中**不再出现**"3.1 已移除 Sketch"这类表述 |

### 1.4 更正 ④：Seed 表述

| 项 | 内容 |
| --- | --- |
| **绑定接口（写入合同）** | 腾讯云混元生 3D 专业版 **`SubmitHunyuanTo3DProJob`**（Version `2023-09-01`，`Model = 3.1`） |
| **事实** | 该接口**当前不暴露 Seed 参数**，不存在"固定/改变随机种子"这一操作 |
| **删除** | "只允许随机种子/重复次数这一个变量变化"、"只改变随机 seed" |
| **改为** | **"第 1 轮 4 个 Candidate = 相同输入 + 相同参数 + 独立重复请求"**；允许变化的只有"独立重复请求次数"这一个变量 |
| **未来约束** | **若改用另一个明确支持 Seed 的腾讯接口，必须另起实验合同，不得与当前批次混合**（已写入合同 §2） |
| 连带修正 | 合同 §5.2 中"靠换 seed 解决属于纯运气"→"靠独立重复请求碰运气属于纯运气" |

> 📌 **本轮未修改的**：`PIANO_HAND_PRODUCTION_PIPELINE_R1.md`、`REFERENCE_ACQUISITION_GATE`、Stage 2 定义、
> `PIANO_HAND_MASTER_ASSET_SPEC_R1.md`、`CANONICAL_HAND_POSE_SPEC_R1.md` 等**全部 Stage 0 冻结文档**。

---

## 2. 第二部分：权威资产获取

| 项 | 记录 |
| --- | --- |
| 资产包 | **Human Base Meshes v1.4.1** |
| 官方页面 URL | `https://www.blender.org/download/demo-files/`（Asset Bundles 区） |
| 官方页面原始授权标记 | **"49 MB – CC0"**；署名 **"by Blender Studio and community contributions."**；**"Updated: Jan 20, 2025"** |
| 页面下载入口 | `https://www.blender.org/download/demo/asset-bundles/human-base-meshes/human-base-meshes-bundle-v1.4.1.zip` |
| **实际下载 URL（官方 mirror）** | `https://mirror.blender.org/demo/asset-bundles/human-base-meshes/human-base-meshes-bundle-v1.4.1.zip` |
| 版本号 | **v1.4.1** |
| 下载日期 | **2026-09-27** |
| 最低 Blender 版本要求 | **Blender 4.2 LTS 或更新**（实际使用 **4.5.9 LTS** 打开检查） |
| 来源合规性 | 仅使用 Blender 官方域（`blender.org` / `mirror.blender.org`），**未从任何第三方转载站下载母文件** |
| 保存位置 | `references/licenses/blender_human_base_meshes/human-base-meshes-bundle-v1.4.1.zip` |
| 授权证据文件 | `references/licenses/blender_human_base_meshes/LICENSE_EVIDENCE.md`　（摘要：`production_spec/stage1c_c1_qualification/license/C1_LICENSE_RECORD.md`） |

### 2.1 文件哈希（SHA-256）

| 文件 | 大小（bytes） | SHA-256 |
| --- | --- | --- |
| `human-base-meshes-bundle-v1.4.1.zip` | **50,643,039** | `811f43accbb31a88266d932f8f5563b2d13586fca0ba2693aad1f5fe582b3515` |
| `human_base_meshes_bundle.blend`（解压后） | **49,420,489** | `3c121505651140ceb4d69fd1d8923f7788ffadd81672f5be14845a5f2c75c137` |

### 2.2 授权判定

```
C1_LICENSE = CC0
C1_SOURCE_VERIFIED = YES
```
- CC0 = 可修改 / 可商用 / 可再发布 / **无需署名**；**不含**"禁止再分发模型文件"条款 → **与 Web 交付场景不冲突**；
- ⚠ 诚实记录：**该授权声明不在 `.blend` 文件内部**（文件内 author/license 元数据为空、包内无 LICENSE 文件），只存在于官方页面。
  故证据链 = 官方页面原文 + 官方 URL + 文件哈希 + Wikimedia Commons 权威交叉印证（`Hand realistic by Dan Ulrich (CC0)`，贡献者含 Blender Studio / Dan Ulrich / Paul Kotelevets / Tonatiuh de San Julián / Julien Kaspar）。

---

## 3. 第三部分：真实 hand asset 定位（文件级，不依赖网页简介）

### 3.1 实际存在的相关资产（从包内 407 个对象中枚举）

| 对象名（原文，含空格） | 类型 | 是否 asset | Catalog | 顶点 / 面 |
| --- | --- | --- | --- | --- |
| **`Hand  - Realistic`** | MESH | ✅ 是 | `Human Base Meshes/Realistic` | **831 / 820** |
| `Hand - Stylized `（尾随空格） | MESH | ✅ 是 | `Human Base Meshes/Stylized` | 871 / 880 |
| `GEO-hand_*_primitive_*`（`.L` / `.R`，多组） | MESH | ❌ | — | 各 113 / 111（属 primitive 人体拼装件，非独立母体候选） |

> **重要更正**：网页研究中曾以 **`Hand realistic`** 指称该资产。**文件内实际名称为 `Hand  - Realistic`**
> （`Hand` 与 `-` 之间为**两个空格**，无尾随空格；而 stylized 版本为 `Hand - Stylized `，**有尾随空格**）。
> 此类差异必须按实际文件记录，否则后续脚本按键名查找会失败。

### 3.2 15 项"是否真的存在"核验（全部来自实际文件）

| # | 核验项 | 实测答案 |
| --- | --- | --- |
| 1 | 是否真的存在独立 realistic hand asset | ✅ **存在**（`Hand  - Realistic`，独立 mesh 对象，asset 标记为真） |
| 2 | 精确资产名称 | **`Hand  - Realistic`** |
| 3 | 右手 / 左手 / 双手 | **仅一只，解剖学右手**（手性检验见 §5 G-12）；**包内无左手** |
| 4 | 是否独立 hand mesh | ✅ 独立（非从人体切分，无 parent） |
| 5 | 是否包含 wrist | ✅ 包含（腕部最窄截面 z ≈ 0.335–0.345） |
| 6 | 是否包含 forearm | ✅ 包含（断端 z = 0.4316） |
| 7 | 前臂长度 | **≈ 0.092 m（9.2 cm）**；与手长（≈0.191 m）比值 ≈ **0.48** |
| 8 | 是否为封闭网格 | ✅ **封闭流形**（boundary edges = 0、non-manifold = 0、signed volume = +5.369e-4 m³） |
| 9 | 是否为 quad-dominant | ✅ **819 quad / 0 tri / 1 ngon**（ngon 位于前臂平端盖面） |
| 10 | 是否已有 UV | ✅ **1 层**（`UVMap`）；**仅单块 UV，不是 UDIM**（更正网页"UV/UDIM"的笼统印象） |
| 11 | 是否已有 multires | ✅ 有 **Multires 修饰器，但只有 1 级**（`total_levels = 1`；L1 = 3,298 面） |
| 12 | 是否已有 armature | ❌ **无**（无 armature modifier、无 vertex groups） |
| 13 | 是否已有 shape keys | ❌ **无** |
| 14 | 是否左右对称 | ❌ 不自对称（跨 X/Y/Z 镜像匹配率 0.0 / 0.0024 / 0.0）；这是**单只手的正常状态** |
| 15 | 初始 pose 是什么 | **五指接近完全伸展（extended）+ 五指已有扇形张开 3.6–9.6° + 拇指虎口约 33.6° + 腕近中立**（详见 §7） |

### 3.3 其他文件级事实（影响后续处理）

- **materials = 0**（资产无材质、无贴图；包内 `images` 仅 1 项且与本资产无关）；
- **包内整个文件无任何 armature**（`bpy.data.armatures` 为空）；
- 前臂断端由**唯一那个 ngon 平盖封闭** → 若日后需延长前臂，须先处理该盖面；
- object origin 位于前臂中段 `(1.4048, 0.0113, 0.3536)`，**不在腕关节旋转中心**（Stage 4 需按规范重设）。

---

## 4. 第四部分：ASSET_GEOMETRY_STATS（base 层摘要）

| 指标 | 值 | 指标 | 值 |
| --- | --- | --- | --- |
| objects | 1 | UV layers | 1（`UVMap`） |
| vertices | **831** | materials | 0 |
| edges | 1,649 | shape keys | 0 |
| faces | **820** | modifiers | Multires（1 级） |
| triangles | **0** | armature | 无 |
| quads | **819** | dimensions | **0.1512 × 0.0651 × 0.2829 m** |
| ngons | **1**（前臂盖面） | bounding box | `(1.3484,−0.0191,0.1490)`→`(1.4986,0.0456,0.4316)` |
| non-manifold edges | **0** | scale | 1.0（米制，未缩放） |
| loose verts / edges | **0 / 0** | origin | `(1.4048, 0.0113, 0.3536)`（前臂中段） |
| boundary edges | **0**（封闭） | symmetry | 无（单只手正常） |

**multires 逐级**：base = **820 面 / 831 顶点** → level 1（最高现有）= **3,298 面 / 3,300 顶点**。

> ⚠ **与网页描述的差异（以文件为准）**：该 hand 资产的 multires **只有 1 级**，
> 不能假设"高模细节已存在"；但这一级对**环线密度**有实质意义（见 §6 T-01）。

**完整数据**：`production_spec/stage1c_c1_qualification/stats/ASSET_GEOMETRY_STATS.md`

---

## 5. 第五部分：Geometry（解剖）检查

> 逐项依据**实际渲染证据 + 实测数值**；视角约定：手指 −Z、**背侧 +Y**、**掌侧 −Y**、拇指侧 +X。
> 掌/背侧判定依据：掌区截面在 −Y 侧呈"两侧隆起 + 中央凹陷"（大鱼际/掌心凹/小鱼际），+Y 侧平缓外凸（手背）。

| ID | 判定项 | 结论 | 依据 |
| --- | --- | --- | --- |
| G-01 | 五指数量 | **PASS** | 5 条独立指截面轨迹；渲染目视 5 指，无融合/多指/少指 |
| G-02 | 手指比例 | **PASS** | 指尖 z：中指 0.149（最长）< 无名指 0.160 < 食指 0.164 < 小指 0.188；拇指最短 |
| G-03 | 拇指结构（非猿手） | **PASS(with note)** | 拇指为独立指列、根部位于腕附近（距腕 4.8 cm、远离四指 MCP 连线）、拇指平面与四指不共面、虎口张开；⚠ 基网格无骨骼，"仅 2 节指骨"由关节外形推定 |
| G-04 | 指间分离 | **PASS** | `EVIDENCE_DISTAL` 可见真实空隙；`WIREFRAME_WEBS.png` 显示四指独立拓扑 + 膜状指蹼 |
| G-05 | 掌结构 | **PASS** | 掌区 −Y 侧截面呈两侧高、中央凹（掌纵弓 + 大鱼际 + 小鱼际）；非平板、非背面镜像 |
| G-06 | 指尖 | **PASS** | 五指均为圆润锥状末端，有明确最前端触键点 |
| G-07 | 指甲 | **CONDITIONAL_PASS** | **资产内不存在任何指甲几何** → Stage 4 需补浅甲面；不影响指尖触键点定位 |
| G-08/G-09/G-10/G-11/G-13 | 细节/风格/禁卡通/禁解剖风/表面干净 | **PASS** | 无毛孔细节、无卡通化、无肌肉骨骼暴露、无疤痕纹身饰物 |
| G-12 | 解剖学右手 | **PASS** | 手性检验 `D × T = N`：`D=(0,0,−1)`、`T=(+1,0,0)`、`N=(0,−1,0)` → 右手成立；`EVIDENCE_PALMAR` 中拇指位于画面右侧（相机 −Y） |
| G-14 | 几何连续 | **PASS** | 0 非流形 / 0 边界边 / 封闭流形 / 正体积 |
| G-15 | `ADULT_NEUTRAL` | **PASS** | 腕→中指尖 **18.6 cm**（成人区间）；无性别强化特征；**包内 realistic 系列仅此一只 hand**（设计上即中性） |

### 5.1 专项：THUMB CMC（Rig 最高风险区，单独审查）

| 检查项 | 实测 | 判定 |
| --- | --- | --- |
| 沿拇指轴的环向环线数（CMC 窗口内） | **0** | ⚠ 该区不是"以拇指轴为中心的管状环结构"，而是过渡区 |
| 连续性 | 0 非流形 / 0 破面 | ✅ |
| 极点分布 | 该区 valence3 = 6、valence5 = 5（全网格 54 / 28） | ⚠ 需人工确认不与 CMC 旋转中心冲突 |
| 第一指蹼 | 张开可辨 | ✅ |
| `T-04`"放射状拓扑" | **NOT_CONFIRMED** | ⚠ **`NEEDS_MINOR_RET0PO`（未确认前不得判 PASS）** |

```
C1_GEOMETRY = PASS
（附：G-07 = CONDITIONAL_PASS；THUMB_CMC = NEEDS_MINOR_RET0PO）
```

**完整依据**：`production_spec/stage1c_c1_qualification/stats/GEOMETRY_ANATOMY_CHECK.md`

---

## 6. 第六部分：Topology 检查（T-01 逐指逐关节）

**方法**：真实 **Edge Loop** 遍历（非 Edge Ring），按 `align = mean|edge_dir·finger_axis| < 0.45` 分类环向环线。
脚本：`scripts/pass9_edge_loops.py`（base）、`scripts/pass10_multires_loops.py`（multires L1）。

### 6.1 base 层（asset 原始状态）

| 指 | MCP | PIP | DIP | CMC/MCP_T | 环线总数 / 中位间距 |
| --- | :-: | :-: | :-: | :-: | --- |
| **THUMB** | MCP_T = **2** | IP = **2** | — | **CMC = 0** | 7 / 8.33 mm |
| **INDEX** | **1** | **2** | **2** | — | 9 / 8.08 mm |
| **MIDDLE** | **1** | **2** | **2** | — | 8 / 9.80 mm |
| **RING** | **1** | **2** | **2** | — | 8 / 8.63 mm |
| **LITTLE** | **0** | **2** | **2** | — | 8 / 7.53 mm |

→ **base 层全部关节 < 3 圈 → `T-01` 不满足**（`NEEDS_MINOR_RET0PO`）。
> 关键认知（与选路文档 `SB-R1` 一致）：这是"**雕刻友好**"基网格的典型密度，**不自动等于动画变形友好**。

### 6.2 应用资产自带的 1 级 multires 之后

| 指 | MCP | PIP | DIP | 环线总数 / 中位间距 | 单项判定 |
| --- | :-: | :-: | :-: | --- | --- |
| **THUMB** | **2** | **4** ✅ | — | 19 / 3.50 mm | `NEEDS_MINOR_RET0PO`（CMC=0、MCP_T=2） |
| **INDEX** | **2** | **5** ✅ | **7** ✅ | 24 / 3.97 mm | `NEEDS_MINOR_RET0PO`（MCP 区） |
| **MIDDLE** | **5** ✅ | **4** ✅ | **5** ✅ | 24 / 4.22 mm | **`PASS`** |
| **RING** | **5** ✅ | **4** ✅ | **7** ✅ | 24 / 3.91 mm | **`PASS`** |
| **LITTLE** | **0** | **4** ✅ | **6** ✅ | 22 / 3.54 mm | `NEEDS_MINOR_RET0PO`（MCP 区） |

### 6.3 其余拓扑项

| 项 | 结论 | 依据 |
| --- | --- | --- |
| T-01 关节 ≥3 圈 | ⚠ **`NEEDS_MINOR_RET0PO`** | 见上；**细分一级即可覆盖 PIP/DIP**，MCP 区与拇指 CMC 需局部补线 |
| T-02 关节区不得有扇形极点 | ⚠ `NEEDS_MINOR_RET0PO` | 极点存在但**无三角面**；是否落在弯曲区**须人工 Retopo 时确认** |
| T-03 指缝不得粘连 | ✅ `PASS` | 指缝独立、膜状指蹼、无焊接顶点 |
| T-04 拇指根部放射状 | ⚠ `NEEDS_MINOR_RET0PO` | CMC 区 0 条拇指轴环线；**未证实** |
| T-05 quad-dominant | ✅ `PASS` | 819/820 为 quad |
| T-06 允许必要 Retopo | ✅ 成立 | 本判定即为其输入 |
| T-07 四指拓扑可复用 | ✅ `PASS` | 四指拓扑同构（8–9 圈、结构一致，仅缩放）→ 利于统一权重模板（`S-07`） |
| T-08 非流形/孤立/重叠/内部面 | ✅ `PASS` | 全 0 |
| T-09 UV 不重叠/无拉伸 | ⚠ **NOT_VERIFIED** | 仅确认 1 层 UV 存在 |
| T-10 法线朝外 | ✅ `PASS(with note)` | 封闭流形 + 正体积支持；未逐面遍历 |

```
C1_TOPOLOGY = CONDITIONAL_PASS
```

**完整依据**：`production_spec/stage1c_c1_qualification/stats/TOPOLOGY_CHECK.md`

---

## 7. 第七部分：RSSF Pose Delta

**当前姿态（实测）**：五指**近完全伸展**（各关节屈曲 ≈ 0–4°）；张开 INDEX–MIDDLE **9.6°** / MIDDLE–RING **3.6°** / RING–LITTLE **8.2°**；拇指虎口 **≈ 33.6°**；腕近中立（含约 4–7° 横向偏移）。

| 部位 | 当前 | RSSF 目标 | 需变更 | 量级 |
| --- | --- | --- | --- | --- |
| **wrist** | 近中立 + 4–7° 偏移 | 背伸/掌屈 0°、尺/桡偏 0° | 归正 4–7° | MINOR |
| **thumb** | CMC ≈0–5°；虎口 33.6° | CMC 20–30° 屈曲；MCP(T) 15–25°；IP 10–20°；虎口 35–45° | 旋转 +10~30°、虎口再张开 +2~11° | **MODERATE** |
| **index** | 屈曲 ≈0–3° | MCP 20–30° / PIP 25–35° / DIP 10–20° | 三关节 +10~35° | **MODERATE** |
| **middle** | 屈曲 ≈0–4° | 同上 | 三关节 +10~35° | **MODERATE** |
| **ring** | 屈曲 ≈0–4° | 同上 | 三关节 +10~35° | **MODERATE** |
| **little** | 屈曲 ≈0–4° | 同上 | 三关节 +10~35° | **MODERATE** |
| **finger spread** | 3.6–9.6° | 10–15° | 整体 +1~11° | MINOR |
| **MCP / PIP / DIP** | ≈0° | 20–30° / 25–35° / 10–20° | +20~35° | **MODERATE** |
| **forearm** | 已足够 | 保持 | 无 | NONE |

**是否可用临时骨架 / simple armature 完成 re-pose，而无需从零雕刻？**
> ## ✅ **可以。全部差异均为关节旋转（10–35°），无一处需要重塑形或改变结构。**

⚠ **但顺序有关**：base 层每关节仅 0–2 圈，**若直接在 base 层旋转 25–35°，关节会折面/丢体积**。
正确顺序应为：**先细分/局部补线 → 再用临时骨架 re-pose → 再进入 Retopo/Rig**。

```
POSE_DELTA = MODERATE
C1_RSSF_REPOSE = MODERATE      （非 MINOR：差量跨 5 指 × 3 关节；非 MAJOR/NOT_VIABLE：纯旋转即可）
```

**完整依据**：`production_spec/stage1c_c1_qualification/stats/RSSF_POSE_DELTA_AND_FOREARM.md`

---

## 8. 第八部分：Forearm 判定

| 项 | 实测 | 判定 |
| --- | --- | --- |
| 是否含腕 | 是（最窄处 z ≈ 0.335–0.345） | ✅ |
| 前臂长度 | **≈ 9.2 cm**（z 0.340 → 0.4316）；手长 ≈ 19.1 cm；比值 ≈ 0.48 | — |
| 是否过长（延伸到肘） | 否 | ✅ |
| 是否只有腕、无足够前臂 | 否（9.2 cm 远大于"仅腕"） | ✅ |
| 能否读出"前臂—腕—掌"柔和直线（`FR-02`） | 能（`EVIDENCE_RADIAL` / `EVIDENCE_PROXIMAL`） | ✅ |
| 能否支撑腕部三态（`FR-03`） | 能 | ✅ |

**对应选项 A（已包含足够前臂）**：
```
C1_FOREARM = PASS
FOREARM_EXTENSION_REQUIRED = 不触发（本轮亦未做任何手工延长）
```
（断端为平切 + 单一 ngon 盖面，已记录为后续若需延长的前置处理项。）

---

## 9. 第九部分：证据图清单

所有证据图**仅为资格审查证据**，均为本阶段在 Blender 4.5.9 中**只读打开官方母文件后临时渲染**（未保存任何修改）：
**未送入 Hunyuan3D，未用于训练，未进入 Three.js。**

### 9.1 8 个解剖视角（`production_spec/stage1c_c1_qualification/renders/`）

| 文件 | 视角 |
| --- | --- |
| `EVIDENCE_DORSAL.png` | 背侧（相机 +Y） |
| `EVIDENCE_PALMAR.png` | 掌侧（相机 −Y） |
| `EVIDENCE_RADIAL.png` | 桡侧（相机 +X，拇指侧） |
| `EVIDENCE_ULNAR.png` | 尺侧（相机 −X） |
| `EVIDENCE_DISTAL.png` | 远端（相机 −Z，指尖方向） |
| `EVIDENCE_PROXIMAL.png` | 近端（相机 +Z，前臂断端方向） |
| `EVIDENCE_DORSAL_OBLIQUE_RADIAL.png` | 背侧斜视（桡侧 45°） |
| `EVIDENCE_DORSAL_OBLIQUE_ULNAR.png` | 背侧斜视（尺侧 45°） |

### 9.2 线框证据（`production_spec/stage1c_c1_qualification/wireframes/`）

| 文件 | 内容 |
| --- | --- |
| `WIREFRAME_DORSAL.png` / `WIREFRAME_PALMAR.png` | 全线框（背/掌） |
| `WIREFRAME_THUMB_CMC.png` / `WIREFRAME_THUMB_CMC_WIDE.png` | **拇指 CMC 专项**（近景 + 全景） |
| `WIREFRAME_THUMB_MCP.png` / `WIREFRAME_THUMB_IP.png` | 拇指 MCP(T) / IP |
| `WIREFRAME_INDEX_MCP.png` / `_PIP.png` / `_DIP.png` | 食指 MCP / PIP / DIP |
| `WIREFRAME_MIDDLE_MCP.png` / `_PIP.png` / `_DIP.png` | 中指 MCP / PIP / DIP |
| `WIREFRAME_RING_MCP.png` / `_PIP.png` / `_DIP.png` | 无名指 MCP / PIP / DIP |
| `WIREFRAME_LITTLE_MCP.png` / `_PIP.png` / `_DIP.png` | 小指 MCP / PIP / DIP |
| `WIREFRAME_WEBS.png` | 指蹼专项（4 指 + 膜状过渡） |
| `WIREFRAME_PALM_ARCH.png` | 掌心弓专项 |

> ⚠ **线框图的诚实说明**：线框由 Blender **Wireframe 修饰器**临时生成（仅渲染用，未写回文件）。
> 该修饰器在四边形非共面/强透视缩短时会产生**对角视觉伪影**，因此
> **拓扑结论一律以拓扑枚举数据为准**（819 quad / 0 tri / 1 ngon / 0 非流形），线框图仅作**目视佐证**。

### 9.3 可复现性

| 脚本 | 用途 |
| --- | --- |
| `scripts/pass1_inventory.py` | 包内对象与资产元数据清点 |
| `scripts/pass2_stats_probe.py` | 基础几何统计 + 6 方向探测渲染 |
| `scripts/pass4a_centers.py` | 截面中心提取（指轴标定数据） |
| `scripts/pass6_loops_unionfind.py` / `pass8_dump.py` | 对边图结构诊断（Edge Ring 家族） |
| `scripts/pass9_edge_loops.py` | **真实 Edge Loop 枚举（T-01 base）** |
| `scripts/pass10_multires_loops.py` | **Edge Loop 枚举（multires L1）** |
| `scripts/pass11_orientation.py` / `pass12_knuckles.py` | 掌/背侧与手别判定 |
| `scripts/render_one.py` + `render_all.sh` / `render_closeups.sh` / `render_extra.sh` | 证据渲染（**单视图单进程**，规避无头多帧渲染黑屏） |

---

## 10. 第十部分：C-2（MakeHuman / MPFB2）轻量备选核验

| 项 | 结果 |
| --- | --- |
| **当前官方许可** | MakeHuman 源码 **AGPL**、MPFB 源码 **GPL**；**核心资产 CC0**（官方原文："All core assets are shared under Creative Commons, CC0."） |
| **导出模型是否 CC0** | **是**（官方 FAQ："The exported models end up being licensed CC0"；"Can I sell models created with MakeHuman? **Yes**"；"Do I need a separate commercial license...? **No**"） |
| 是否能输出成人中性人体 | 可以（基于单一 androgynous 基础网格 + 滑杆）；**本轮未实测** |
| 是否有完整手指骨架 | **未本轮实测**（官方资料显示含通用骨架并专门展示过 hand topology 演进）→ 标记 `TO_BE_VERIFIED_IN_C2_STAGE` |
| hand topology 是否值得作 C-1 备选 | 方向可信，但**手部解剖精度是公认弱项**（`SB-R2`）；未实测 |

```
C2_LICENSE = CC0（已验证）  |  C2_HAND_TOPOLOGY = NOT_VERIFIED  |  C2_FORMAL_QUALIFICATION = NOT_TRIGGERED
```
> 依据本轮指令：**C-1 未 FAIL（= CONDITIONAL_PASS），故不需要继续深挖 C-2**。
> 仅当 C-1 最终被判 FAIL、或人工在 Amendment Review 中要求双来源对比时，才启动 C-2 正式资格审查。

**完整记录**：`production_spec/stage1c_c1_qualification/stats/C2_MAKEHUMAN_LIGHT_CHECK.md`

---

## 11. 第十一部分：C-1 总判定

### 11.1 判定依据对照

| `PASS` 条件（人工指令 §十一） | 实际 |
| --- | --- |
| 授权明确 CC0 | ✅ |
| 实际 hand geometry 存在 | ✅ |
| 解剖无关键错误 | ✅ |
| 掌心 / 拇指 / 指蹼可用 | ✅（CMC 放射状拓扑未证实 → 局部） |
| topology **至少可通过局部 Retopo** 达到动画要求 | ✅（范式正确、密度不足 → 局部补线/细分） |
| RSSF re-pose 工作量可控 | ✅（MODERATE，纯旋转） |
| 能形成 HAND + SHORT FOREARM | ✅（已含 9.2 cm 前臂） |

| `CONDITIONAL_PASS` 条件 | 实际 |
| --- | --- |
| 核心几何成立 | ✅ |
| 但存在**可明确修复**的局部 topology / forearm / pose / 中性化问题 | ✅ **① MCP 区与拇指 CMC 环线不足；② CMC 放射状未证实；③ 无指甲几何**（forearm 与中性化**无**问题） |

| `FAIL` 条件 | 实际 |
| --- | --- |
| hand asset 实际不存在 | ❌ 不存在（asset 存在） |
| 解剖明显错误 / 拇指不可用 / 掌心指蹼不可用 / 需接近重做 / 非成人中性基础手 | ❌ 全部不成立 |

### 11.2 判定

```
C1_ASSET_QUALIFICATION = CONDITIONAL_PASS
```
**一句话理由**：**核心几何、解剖、授权、前臂全部成立，且体量（831 顶点封闭流形）与四指同构拓扑使其成为高质量的"可加工母体"；
唯一不足是关节环线密度与拇指 CMC 布线（可由"1 级细分 + 局部补线"明确修复）以及缺失的指甲细节**。

### 11.3 CONDITIONAL 项与修复清单（作为 `STAGE0_ROUTE_C_AMENDMENT` 的输入）

| # | 条件项 | 问题定性 | 拟修复（**本轮不执行**） | 量级 | 阻塞 Stage 2 否 |
| --- | --- | --- | --- | --- | --- |
| CON-1 | 关节环线密度（`T-01`） | 局部 topology | ① 应用/新增细分（资产自带 1 级，零成本）；② MCP 区每指 + 拇指 CMC 局部补线至 ≥3 圈 | **MINOR** | 否（属 Stage 4 工序） |
| CON-2 | 拇指 CMC 放射状拓扑（`T-04`） | 局部 topology | 人工放大审阅 → 按需重排 CMC 周围回路（保留既有走向） | **MINOR** | 否 |
| CON-3 | 极点位置确认（`T-02`） | 人工确认 | Retopo 时确认极点不在关节弯曲区 | **MINOR** | 否 |
| CON-4 | 指甲几何缺失（`G-07`） | 表面细节 | Stage 4 补浅甲面/甲床边界 | **MINOR** | 否 |
| CON-5 | RSSF 姿态差（`POSE_DELTA = MODERATE`） | 姿态 | **先细分/补线 → 临时骨架 re-pose → 再 Retopo/Rig** | **MODERATE** | 否 |
| CON-6 | object origin 不在腕关节中心 | 规范对齐 | Stage 4 重设 origin | **MINOR** | 否 |
| CON-7 | UV 重叠/拉伸未核验（`T-09`） | 待验 | Stage 4 UV 检查/重展 | **MINOR** | 否 |
| CON-8 | 左手需镜像得到 | 流程 | 按 `LR-01`~`LR-04` 在右手母版获批后镜像 | — | 否 |

> 📌 **上述全部为"可明确修复"，且全部落在既有 Stage 4 / Stage 5 工序范围内，不新增阶段、不新增技能需求。**

---

## 12. 第十二部分：本轮对 Stage 0 的处理（合规声明）

| 项 | 状态 |
| --- | --- |
| `PIANO_HAND_PRODUCTION_PIPELINE_R1.md` | **未修改** |
| `REFERENCE_ACQUISITION_GATE` | **未修改、仍为 `STILL_BLOCKED`** |
| Stage 2 定义 | **未修改、仍为 `BLOCKED`** |
| 任何其他 Stage 0 冻结文档 | **未修改** |
| 本轮是否提出 Stage 0 修订 | **否**。若 C-1 PASS/CONDITIONAL_PASS，**下一轮**才提出 `STAGE0_ROUTE_C_AMENDMENT` |

本轮的**唯一文档写入**为：两份 Stage 1B 文档的**事实性更正与修订记录**（人工已授权的 §一 范围），
以及本阶段新增的资格审查文档与证据（`docs/STAGE1C_C1_ASSET_QUALIFICATION_R1.md`、`production_spec/stage1c_c1_qualification/**`、`references/licenses/**`）。

---

## 13. 第十三部分：本轮未做（停止条件确认）

- 🚫 **未**对资产做任何正式 re-pose（未加骨架、未旋转骨骼、未 apply）
- 🚫 **未**做 Retopo / 补线 / 修改任何几何
- 🚫 **未** Rig / 未加骨骼 / 未刷权重 / 未做动画
- 🚫 **未**调用 Hunyuan3D（`HUNYUAN3D_CALLED = NO`）
- 🚫 **未**进入 Three.js
- 🚫 **未**修改任何 Stage 0 冻结文档
- 🚫 **未**修改母文件（`.blend` 全程只读打开；所有合成都只存在于内存、从未保存）
- 🚫 **未**把任何证据图送入 Hunyuan3D 或任何生成式管线
- ✅ 已完成：① 两份 Stage 1B 文档的 4 项事实性更正；② 官方资产获取 + CC0 授权证据链；③ 真实文件级 15 项资产核验；④ 完整几何统计；⑤ 解剖 15 项检查 + 拇指 CMC 专项；⑥ 拓扑逐指逐关节环线定量（base 与 multires L1）+ 极点普查；⑦ 8 视角 + 24 张线框/近景证据图；⑧ RSSF 姿态差量与前臂判定；⑨ C-2 轻量核验；⑩ C-1 总判定

---

## 14. 最终状态输出

```
C1_SOURCE_VERIFIED      = YES
C1_LICENSE              = CC0
C1_HAND_ASSET_FOUND     = YES        （实际名称：Hand  - Realistic）

C1_GEOMETRY             = PASS        （附：G-07 指甲 = CONDITIONAL_PASS；THUMB_CMC = NEEDS_MINOR_RET0PO）
C1_TOPOLOGY             = CONDITIONAL_PASS

C1_RSSF_REPOSE          = MODERATE    （临时骨架可完成，无需雕刻）
C1_FOREARM              = PASS        （已含 9.2 cm 短前臂，EXTENSION_REQUIRED 不触发）

C1_ASSET_QUALIFICATION  = CONDITIONAL_PASS

ROUTE_C_PRIMARY         = READY_FOR_AMENDMENT_REVIEW

STAGE0                  = FROZEN
STAGE2                  = BLOCKED
```

**下一步（不由本轮执行）**：
1. 人工审核本文件与证据目录；
2. 若认可 `CONDITIONAL_PASS`，由人工发起 **`STAGE0_ROUTE_C_AMENDMENT`**（拟修订 `AMEND-01`~`AMEND-05`，并纳入本文 §11.3 的 `CON-1`~`CON-8` 条件）；
3. `STAGE0_ROUTE_C_AMENDMENT` 通过后，方可进入 Stage 4 的 **re-pose + 局部补线**（届时才允许动模型）。

**文档状态：`READY_FOR_HUMAN_REVIEW`**
