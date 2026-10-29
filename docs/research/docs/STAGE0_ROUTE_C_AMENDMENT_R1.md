# STAGE 0 · ROUTE C AMENDMENT · R1

> `docs/STAGE0_ROUTE_C_AMENDMENT_R1.md`
> 项目：钢琴教学双手 3D 交互资产
> 性质：**极窄 Stage 0 架构修订**（`STAGE0_ROUTE_C_AMENDMENT`）
> 日期：2026-09-27　状态：**`READY_FOR_HUMAN_REVIEW`**
>
> **本轮不是**：重新研究 / 重新选型 / 生产模型 / Stage 4 / Retopo / re-pose / Rig。
> **本轮是**：修改"几何从哪里来"以及"哪些 Gate 阻塞哪条路线"，并完成当前权威文件的一致性更新。
>
> **停止条件**：权威文件修订 + 一致性扫描 + 本文件。之后停止，等待 Human Review。**不自动开始模型工程。**

---

## 0. 一句话结论

> ## ✅ `STAGE0_ROUTE_C_AMENDMENT = PASS`
>
> 项目主几何来源正式由：
> **真人 8 视图 → Hunyuan3D Multi-view → Geometry Candidate**
> 改为：
> **CC0 Authoritative Base Mesh → Geometry Bootstrap → Geometry Review → Blender Engineering**
>
> 正式主母体 = **Blender Human Base Meshes v1.4.1 · `Hand  - Realistic`**（CC0）。
> `ROUTE_C_SOURCE_GATE = PASS`（允许创建工程工作副本）。
> `REFERENCE_ACQUISITION_GATE` 由**全局阻塞门禁**降为**分支门禁**（仅 Hunyuan Multi-view）。
> **Stage 4 之后的核心生产结构原则上保持不变。**

---

## 1. 为什么需要本次 amendment

三条已完成的 Human Review 事实，共同把"几何来源"从"AI 重建"推向"CC0 作者化基础网格"：

| # | 事实 | 后果 |
| --- | --- | --- |
| 1 | **Stage 1A 路线 FAIL**（2D Anchor + 图像编辑无法锁定共享几何 / 相机外参 / 世界光照 / 姿态） | 2D 派生路线被永久否决，需要一个新的"统一 3D 母体"来源 |
| 2 | **Stage 1B 路线选择**：`ROUTE C` 在项目优先级第 1–5 项全面领先；且**它不依赖被阻塞的 `REFERENCE_ACQUISITION_GATE`** | 主路线改为 CC0 作者化基础网格 |
| 3 | **Stage 1C C-1 资格审查 = `CONDITIONAL_PASS`**：官方 CC0 hand 资产真实存在、解剖可用、四边面、含短前臂 | 母体来源已落实，且条件项均可明确修复 |
| 4 | **Blender 5.1.2 runtime parity = PASS** | 可以使用用户正式安装的 `D:\Blender\blender.exe` 做后续工程，技术结论不被 runtime 改变 |

因此需要一次**极窄的 Stage 0 修订**，把"几何来源权威"与"门禁作用域"正式改写，避免后续 Stage 2 继续按已失效的旧语义执行。

---

## 2. Stage 1A（承接，不重开）

| 项 | 值 |
| --- | --- |
| `AI_MULTIVIEW_FEASIBILITY` | **`FAIL`** |
| 失败路线 | 2D Anchor → AI 图像编辑 → 派生 DORSAL / PALMAR / RADIAL / ULNAR |
| `2D_IMAGEGEN_MULTIVIEW_ROUTE` | **`REJECTED_BASELINE`** |
| 是否重开 | 🚫 **不得重开** |

**失败机制（结构性，非提示词问题）**：2D Anchor + image editing 无法锁定
**shared geometry / camera extrinsics / world lighting / pose** 四项。
只要中间表示是 2D 位图，这四项在原理上都不可能被满足。

> 来源：`docs/STAGE1_AI_MULTIVIEW_RESULT_R1.md`（**本轮未修改，历史语义保留**）。

---

## 3. Stage 1B（路线选择）

| 项 | 值 |
| --- | --- |
| 推荐 | `ROUTE_C_PRIMARY`（CC0 AUTHORED BASE MESH）+ `ROUTE_B_PARALLEL_BOUNDED_EXPERIMENT` |
| 优先级 | 结构正确 > 可 Rig > 变形稳定 > 授权安全 > 可复用 > Web 性能 > 生产成本 |
| 关键优势 | ① 结构由人工作者保证；② 四边面为后续处理而设计；③ **CC0 授权与 Web 分发零冲突**；④ 母体为静态文件，可版本化可审计；⑤ **不依赖被阻塞的 `REFERENCE_ACQUISITION_GATE`** |
| 关键认知 | **AI 可近似继承姿态，但无法可靠、可审计地保证符合冻结的 RSSF 技术范围**（`HR-06b` / `HR-06c`）→ 最终 RSSF 必须人工验证，必要时 Blender 重摆 |

> 来源：`docs/STAGE1B_SHARED_3D_BOOTSTRAP_ROUTE_SELECTION_R1.md`（**本轮未再改写**）。

---

## 4. Stage 1C（C-1 资格审查）

| 字段 | 值 |
| --- | --- |
| 资产包 | **Human Base Meshes v1.4.1** |
| 实际对象名 | **`Hand  - Realistic`**（`Hand` 与 `-` 之间**两个空格**，无尾随空格） |
| 来源 | Blender 官方资产包（仅 `blender.org` / `mirror.blender.org`） |
| 授权 | **CC0** |
| 母文件 | `human_base_meshes_bundle.blend` |
| SHA-256 | **`3c121505651140ceb4d69fd1d8923f7788ffadd81672f5be14845a5f2c75c137`** |
| `C1_SOURCE_VERIFIED` | **YES** |
| `C1_LICENSE` | **CC0** |
| `C1_HAND_ASSET_FOUND` | **YES** |
| `C1_GEOMETRY` | **PASS**（附 `G-07` 指甲 = `CONDITIONAL_PASS`；`THUMB_CMC = NEEDS_MINOR_RETOPO`） |
| `C1_TOPOLOGY` | **`CONDITIONAL_PASS`** |
| `C1_RSSF_REPOSE` | **MODERATE**（临时骨架可完成，无需雕刻） |
| `C1_FOREARM` | **PASS**（已含 ≈9.2 cm 短前臂） |
| `C1_ASSET_QUALIFICATION` | **`CONDITIONAL_PASS`** |

**人工判定**：该资产**不是** Final Production Master，而是
**`APPROVED_ENGINEERING_BASE_MESH`** —— 已批准作为 Route C 的正式工程母体起点。

**资产客观事实（影响 Stage 4）**：831 顶点 / 820 面（819 quad + 1 ngon）/ 封闭流形 / 1 层 UV /
自带 **Multires 仅 1 级**（L1 = 3,298 面 / 3,300 顶点）/ 无 armature / 无 shape keys / materials = 0 /
origin 位于前臂中段（不在腕关节旋转中心）。

> 来源：`docs/STAGE1C_C1_ASSET_QUALIFICATION_R1.md`（**本轮未修改**）。

---

## 5. Blender Runtime Parity

| 项 | 值 |
| --- | --- |
| `PROJECT_BLENDER_RUNTIME` | **`D:\Blender\blender.exe`** |
| `PROJECT_BLENDER_VERSION` | **5.1.2** |
| `PROJECT_BLENDER_BUILD` | **`ec6e62d40fa9`** |
| `BLENDER_5_1_2_RUNTIME_PARITY` | **PASS** |
| `BASE_GEOMETRY_PARITY` | **PASS**（EXACT_MATCH，26/26 字段零差异） |
| `MULTIRES_PARITY` | **PASS** |
| `TOPOLOGY_PARITY` | **EXACT**（base + L1 逐字段 0 差异） |
| `RENDER_RUNTIME` | **FUNCTIONAL** |
| `USER_CONFIG_DIFF` | **EMPTY** |
| `C1_QUALIFICATION_REPRO_RUNTIME` | **`BLENDER_4_5_9_LTS`**（历史复现，**保留未动**） |

> **正式规则**：`PROJECT_BLENDER_RUNTIME = D:\Blender\blender.exe`。
> **但历史 C1 Qualification provenance 保持不变**：`C1_QUALIFICATION_REPRO_RUNTIME = WorkBuddy Portable Blender 4.5.9 LTS`。
> **不得修改历史记录。** portable 4.5.9 不删除，仅作为历史复现 runtime 保留。
> 两者**永久区分**（对应风险 `RC-R6`）。

> 来源：`docs/BLENDER_RUNTIME_DISCOVERY_AUDIT_R1.md`、`docs/BLENDER_5_1_2_RUNTIME_PARITY_CHECK_R1.md`（**本轮未修改**）。

---

## 6. 旧主线（修订前）

```
  STAGE 0  Research & Spec
      ↓  🚦 GATE 1
  STAGE 1  真人右手 8 视图采集（强制前置）
      ↓  🔒 REFERENCE_ACQUISITION_GATE（12 项全局阻塞）
  STAGE 2  Hunyuan3D Multi-view Generation（首轮即 8 视图）
      ↓  🚦 GATE 2
  STAGE 3  Geometry Review
      ↓
  STAGE 4  Blender Engineering（清理 / Retopo / UV / 形态修正）
      ↓  5 Rig → 6 Deformation → 7 Mirror → 8 Animation → 9 Review → 10 GLB → 11 Three.js
```

**旧主线的结构性问题**：Stage 2 的几何来源被 `REFERENCE_ACQUISITION_GATE` **全局阻塞**；
而真人 8 视图尚未采集 → Stage 2 无法启动。

---

## 7. 新主线（修订后）

```
  STAGE 0   Research & Spec（COMPLETE / REFROZEN）
      ↓  🔑 ROUTE_C_SOURCE_GATE  ✅ PASS
  STAGE 2   GEOMETRY BOOTSTRAP
            PRIMARY: CC0 《Hand  - Realistic》(Human Base Meshes v1.4.1)
            输出：RIGHT_HAND_BOOTSTRAP_C1 工程工作副本
      ↓  🚦 GATE 2
  STAGE 3   GEOMETRY REVIEW（接纳为 RIGHT_HAND_ENGINEERING_CANDIDATE）
      ↓
  STAGE 4   BLENDER ENGINEERING
            Topology Patch / RSSF Re-pose / Nails / Origin / UV
      ↓
  STAGE 5   RIG
      ↓  🚦 GATE 3
  STAGE 6   DEFORMATION TEST
      ↓  🚦 GATE 4
  STAGE 7   LEFT HAND MIRROR
      ↓
  STAGE 8   ANIMATION
      ↓  🚦 GATE 5
  STAGE 9   HUMAN REVIEW
      ↓
  STAGE 10  GLB
      ↓
  STAGE 11  THREE.JS

  ── 旁支 A · OPTIONAL REFERENCES ───────────────────────────────
     真人 8 Views  →  Validation / Texture Reference（非阻塞）

  ── 旁支 B · OPTIONAL FALLBACK ─────────────────────────────────
     Hunyuan3D  →  Human-trigger only
     若 fallback 使用 Multi-view：REFERENCE_ACQUISITION_GATE 重新生效
```

---

## 8. 受影响文件的 semantic diff

> **只修改真正受到 Route C 影响的当前权威文件。**
> 历史审计链**一律不改**（见 §15）。

### 8.1 `docs/PIANO_HAND_PRODUCTION_PIPELINE_R1.md`

| # | 位置 | 旧语义 | 新语义 |
| --- | --- | --- | --- |
| 1 | 头部 | 版本 R1.2 | 版本 R1.2 **+ R1.3 Route C Amendment 横幅** |
| 2 | §0 流水线总览图 | Stage 1 → `REFERENCE_ACQUISITION_GATE` → Stage 2 Hunyuan3D | Stage 0 → `ROUTE_C_SOURCE_GATE` → Stage 2 **GEOMETRY BOOTSTRAP**；新增旁支 A / B |
| 3 | Stage 0 | `COMPLETE / FROZEN` | `COMPLETE / **REFROZEN_AFTER_ROUTE_C_AMENDMENT**` |
| 4 | Stage 1 | `Reference（参考图采集）READY_TO_START`，**关键路径**，出口受阻于门禁 | **`REFERENCE / VALIDATION SOURCES`**，**非关键路径**，`OPTIONAL_NON_BLOCKING_FOR_ROUTE_C` |
| 5 | `REFERENCE_ACQUISITION_GATE` | 全局阻塞门禁（Stage 1 → Stage 2） | **`CONDITIONAL_BRANCH_GATE`**（仅 Hunyuan Multi-view）；Route C 下 = `NOT_APPLICABLE_TO_ROUTE_C`；**12 项条件完整保留** |
| 6 | — | （无） | **新增 `ROUTE_C_SOURCE_GATE`**（9 项 PASS 条件 → PASS） |
| 7 | Stage 2 | `Hunyuan3D（多视角生成）` | **`GEOMETRY BOOTSTRAP`**（`ROUTE C PRIMARY` → `RIGHT_HAND_BOOTSTRAP_C1`）；Hunyuan 降为 `HUMAN_TRIGGER_REQUIRED = YES` 的 fallback |
| 8 | Stage 3 | 消费 Stage 2 生成模型 | 消费 `RIGHT_HAND_BOOTSTRAP_C1` + 直接复用 `STAGE1C_C1_ASSET_QUALIFICATION_R1`；**不要求 CON-1~CON-7 已修完** |
| 9 | Stage 4 | 清理 → Retopo → UV → 形态修正 | 新增 **Route C 专项合同**（11 条，含 `THUMB_CMC_TOPOLOGY_REVIEW = REQUIRED`、官方母文件 byte-frozen） |
| 10 | §2 门禁汇总 | GATE 1 → `REFERENCE_ACQUISITION_GATE` | 新增 `ROUTE_C_SOURCE_GATE = PASS`；`REFERENCE_ACQUISITION_GATE` 标注分支作用域 |
| 11 | §3.2 / §3.3 | 生产路线 = `Reference → Hunyuan3D → Blender Engineering` | 生产路线 = **`CC0 Authoritative Base Mesh → Geometry Bootstrap → ...`**；旁支 A / B 单独列出 |
| 12 | §4 风险登记册 | 无分支作用域 | 新增 **branch-scoped** 标签；`RK-01` / `RK-02` → `HUNYUAN_BRANCH_ONLY`；新增 **`RC-R1`~`RC-R6`** |
| 13 | §5 目录结构 | 含 `stage2_hunyuan/`，与实际不符 | 对齐实际（`stage1c_c1_qualification/`、`runtime_parity/`、`licenses/`）；`stage2_bootstrap/` 标为目标目录 |
| 14 | §6 产出清单 | 8 行 | 补 9–14 行（Stage 1A/1B/1C、runtime parity、本修订文档） |
| 15 | §7 禁止事项 | Stage 0 禁止清单 | 新增 **§7.1 本轮禁止**（C1 working mesh / 母文件 / Multires / topology / re-pose / 指甲 / UV / origin / Rig / 镜像 / 动画 / Hunyuan3D / Three.js / 删 4.5.9 / 改 5.1 配置 / 自动进 Stage 2） |
| 16 | §8 当前状态 | `STAGE0 = FROZEN` / `STAGE2 = BLOCKED` | `STAGE0 = REFROZEN` / `ROUTE_C_SOURCE_GATE = PASS` / `STAGE2 = READY_TO_START_ROUTE_C_BOOTSTRAP`；附当前权威字段表 |

### 8.2 `docs/PIANO_HAND_MASTER_ASSET_SPEC_R1.md`

| # | 位置 | 旧语义 | 新语义 |
| --- | --- | --- | --- |
| 1 | 头部 | 版本 R1.2 | + **R1.3 横幅**（几何来源权威变更 / `CON-1`~`CON-7` 绑定 / `OFFICIAL_MULTIREZ_L1`） |
| 2 | §0 摘要 | 仅左右手生产策略 | 新增 **几何来源权威字段表**（`GEOMETRY_SOURCE_PRIMARY` 等） |
| 3 | `T-06` | "AI 生成 mesh ... 必须 Retopo" | 路线中立化：**不论几何来源（AI 或 CC0 基础网格）都不自动满足动画拓扑要求** |
| 4 | — | （无） | **新增 §2.4 Route C 拓扑工程输入**：`OFFICIAL_MULTIREZ_L1 = PERMITTED_ENGINEERING_BASE`；base vs L1 环线实测对照；**`CON-1`~`CON-8` Stage 绑定表** |
| 5 | §5.1 生产策略图 | `Reference Pack → Hunyuan3D 生成 → ...` | **Route C 主链**（CC0 资产 → Bootstrap → Review → Engineering → Rig）；旁支 A / B |
| 6 | §11 前序门禁 | `REFERENCE_ACQUISITION_GATE`（Stage 1 → Stage 2） | **§11.1 `ROUTE_C_SOURCE_GATE`** + **§11.2 `REFERENCE_ACQUISITION_GATE = CONDITIONAL_BRANCH_GATE`**；附 `HR-09` 澄清 |
| 7 | §10 `HR-09` 行 | 原裁定 | 增加 **R1.3 语义澄清**（限制的是渲染图作为 Hunyuan input，不是 CC0 资产本身） |
| 8 | §12 禁止事项 | 原清单 | 增加 R1.3 附加禁止 |
| 9 | §13 权威状态表 | R1.2.1 表 | **R1.3 表**（20 行，含几何来源 / runtime / Gate / 分支字段） |

### 8.3 `docs/MULTIVIEW_REFERENCE_PACK_SPEC_R1.md`

| # | 位置 | 旧语义 | 新语义 |
| --- | --- | --- | --- |
| 1 | 头部 | 版本 R1.2 | + **R1.3 横幅**（作用域收窄，内容不变） |
| 2 | §1 视角清单 | 无适用范围声明 | 新增**适用范围块**：本规范 = Hunyuan fallback 分支的输入规范 |
| 3 | §5.5 `HR-09` | 原裁定 | 增加 **R1.3 语义澄清表** |
| 4 | §5.6 备用降级路径 | 路径 2 = 备选 | **路径 2 升级为现有主路线**（历史内容保留为记录） |
| 5 | §6 `REFERENCE_GAP-02` | 阻塞 `Stage 1 → Stage 2` | 作用域收窄至 **Hunyuan Multi-view 分支**；新增 **R1.3 更新**段 |
| 6 | §7 Pre-flight Checklist | 即 Gate 第 12 项条件 | 增加**作用域声明**：仅约束 Hunyuan fallback；Route C 下**不适用** |
| 7 | §9 禁止事项 / 文档状态 | 原状态 | 增加 R1.3 附加禁止；状态改为 PASS（R1.3） |

### 8.4 `docs/CANONICAL_HAND_POSE_SPEC_R1.md`（**最小修正**）

| # | 位置 | 旧语义 | 新语义 |
| --- | --- | --- | --- |
| 1 | 头部 | 版本 R1.2 | + **R1.3 最小修正横幅**（明确"结构不动"） |
| 2 | §3.1 用途句 | "`CANONICAL_HAND_POSE` / **Hunyuan3D 多视角重建** / Rig neutral pose" | 扩写为 "RSSF 母版生成 / 工程 re-pose / Rig neutral pose"（Hunyuan 仅为**分支场景之一**） |
| 3 | §3.2 用途清单 | 含 "**Hunyuan3D 母版生成**" | 增加 **RSSF 母版生成 / 工程 re-pose**；Hunyuan 标为 fallback 分支 |
| 4 | §4 参考角度 | **"必须提供完整 8 视图，全部为强制"**（无范围限定） | 增加**适用范围块**：仅 Hunyuan fallback；**不得**再把真人 8 视图定义为 Route C 的必要条件 |
| 5 | §9 权威状态表 | R1.2.1 表 | **R1.3 表** |

> ⚠ `RSSF` 姿态定义、`HR-06b` / `HR-06c` 技术范围、`§2.1` 姿态总表**均未改动**。

### 8.5 历史文件中保留的旧状态块（**故意不改**）

以下文件仍含 `STAGE0 = FROZEN` / `STAGE1 = READY_TO_START` / `STAGE2 = BLOCKED` 等**旧状态块**。
**这些是历史语义，本轮不得修改**；它们的"当前性"已由本文件 §16 取代：

| 文件 | 保留内容 |
| --- | --- |
| `docs/PHASE1_R1_2_FINAL_CLOSURE.md` | R1.2 收口时的状态块 |
| `docs/PHASE1_R1_2_1_CONSISTENCY_PATCH.md` | R1.2.1 状态块 |
| `docs/BLENDER_5_1_2_RUNTIME_PARITY_CHECK_R1.md` | 该轮结束时的 `STAGE0 = FROZEN` / `STAGE2 = BLOCKED` |
| `docs/STAGE1C_C1_ASSET_QUALIFICATION_R1.md` | 该轮结束时的 `STAGE0 = FROZEN` / `STAGE2 = BLOCKED` |
| `docs/STAGE1B_SHARED_3D_BOOTSTRAP_ROUTE_SELECTION_R1.md` | `REFERENCE_ACQUISITION_GATE = STILL_BLOCKED` / `STAGE2 = BLOCKED` |
| `docs/STAGE1B_HUNYUAN_SINGLE_IMAGE_TEST_CONTRACT_R1.md` | 合同内的 `STAGE2 = BLOCKED`（该合同本身仍保留，当前 `DEFERRED`） |

> **一致性判据**：**当前权威状态以本文件 §16 与 `REFERENCE_MANIFEST_R1.json` 为准。**
> 上表文件的状态块只反映**各自完成时点**的事实，不构成当前状态声明。

### 8.6 `reference_manifest/REFERENCE_MANIFEST_R1.json`

| # | 位置 | 旧语义 | 新语义 |
| --- | --- | --- | --- |
| 1 | `revision` | `R1.2.1_CONSISTENCY_PATCH` | **`R1.3_ROUTE_C_AMENDMENT`**；新增 `route_c_amended_at` / `route_c_amendment_report` |
| 2 | — | （无） | **新增 `r1_3_scope`（11 条）/ `r1_3_unchanged`（9 条）** |
| 3 | `final_rules` | 8 键 | 加 **SCOPE 标注**；新增 `ROUTE_C_SOURCE_GATE` / `REFERENCE_ACQUISITION_GATE_ON_ROUTE_C` 等 |
| 4 | — | （无） | **新增 `geometry_source_authority`**（13 键） |
| 5 | — | （无） | **新增 `blender_runtime_authority`**（12 键） |
| 6 | — | （无） | **新增 `c1_conditional_items_binding`**（`CON-1`~`CON-8`，含所属 Stage） |
| 7 | — | （无） | **新增 `route_c_risks`（`RC-R1`~`RC-R6`）/ `branch_scoped_risks`（8 条）** |
| 8 | `REFERENCE_GAP-02` | 阻塞 `Stage 1 → Stage 2` | `does_not_block` / `must_block` / `blocks` / `severity` / `current_state` 全部收窄；新增 `r1_3_update` |
| 9 | `reference_acquisition_gate` | 全局门禁 | 新增 `gate_type_r1_3` / `applies_to_r1_3` / `on_route_c_r1_3` / `historical_conditions_preserved` |
| 10 | — | （无） | **新增 `route_c_source_gate`**（9 项条件 + 证据 + `does_not_mean`） |
| 11 | `HR-09` 条目 | 原裁定 | 新增 `r1_3_clarification` |
| 12 | `review_status` | `revision = R1.2`，`STAGE2 = BLOCKED` | `revision = R1.3`；`stage_status` 改为 `REFROZEN` / `OPTIONAL_NON_BLOCKING` / `READY_TO_START_ROUTE_C_BOOTSTRAP` |
| 13 | `phase1_prohibitions_observed` | 9 项 | **补充 12 项 R1.3 禁止观测记录** |

### 8.6 未修改（受影响面扫描结论）

| 文件 | 判定 | 理由 |
| --- | --- | --- |
| `docs/PIANO_HAND_PEDAGOGY_RESEARCH_R1.md` | 🚫 禁止修改 | 教学研究，与几何来源无关 |
| `docs/PHASE1_R1_1_AMENDMENT_REPORT.md` | 不修改 | 历史审计链 |
| `docs/PHASE1_R1_2_FINAL_CLOSURE.md` | 不修改 | 历史审计链 |
| `docs/PHASE1_R1_2_1_CONSISTENCY_PATCH.md` | 不修改 | 历史审计链 |
| `docs/STAGE1_AI_MULTIVIEW_RESULT_R1.md` | 不修改 | 历史审计链（Stage 1A FAIL 证据） |
| `docs/STAGE1B_SHARED_3D_BOOTSTRAP_ROUTE_SELECTION_R1.md` | 不修改 | 事实性修正已完成，**不再重写历史** |
| `docs/STAGE1C_C1_ASSET_QUALIFICATION_R1.md` | 不修改 | 历史审计链 |
| `docs/BLENDER_RUNTIME_DISCOVERY_AUDIT_R1.md` | 不修改 | 历史审计链 |
| `docs/BLENDER_5_1_2_RUNTIME_PARITY_CHECK_R1.md` | 不修改 | 历史审计链 |
| `docs/STAGE1B_HUNYUAN_SINGLE_IMAGE_TEST_CONTRACT_R1.md` | 不修改 | **保留**；当前 `ROUTE_B_EXECUTION = DEFERRED` |
| `docs/STAGE1_AI_MULTIVIEW_FEASIBILITY_PLAN_R1.md` / `_QC_SPEC_R1.md` | 不修改 | Stage 1A 历史附件 |

---

## 9. Gate 重定义汇总

| 门禁 | 修订前 | 修订后 |
| --- | --- | --- |
| **GATE 1** | Stage 0 → Stage 1 的放行 | ✅ **保留为历史判定**；现行含义 = `STAGE0 = COMPLETE` |
| **`ROUTE_C_SOURCE_GATE`** | （不存在） | 🔑 **新增**，Stage 0 → Stage 2（Route C）→ ✅ **PASS** |
| **`REFERENCE_ACQUISITION_GATE`** | 🔒 全局阻塞门禁（Stage 1 → Stage 2，12 项） | 🔒 **`CONDITIONAL_BRANCH_GATE`**，仅 `HUNYUAN3D_MULTIVIEW_FALLBACK`；Route C 下 = **`NOT_APPLICABLE_TO_ROUTE_C`** |
| **GATE 2** | Stage 3 后，打回 Stage 2 重生成 | **保留**；打回 Stage 2 重新输出工作副本，或否决母体 |
| **GATE 3 / 4 / 5** | — | **完全不变** |

> 🚫 **关键纪律**：`REFERENCE_ACQUISITION_GATE` 在 Route C 下**不得写成 `PASS`**。
> **它没有被绕过，而是不适用**——因为 Route C 不使用真人 8 视图做几何重建输入。
> **历史 12 项 Gate 条件保留，不得删除**，只改变 scope / applicability。

---

## 10. Hunyuan 分支的新角色

| 字段 | 值 |
| --- | --- |
| `HUNYUAN3D_ROLE` | **`OPTIONAL_FALLBACK_EXPERIMENT`** |
| `HUMAN_TRIGGER_REQUIRED` | **`YES`**（🚫 不得自动执行） |
| `ROUTE_B_EXECUTION` | **`DEFERRED`** |
| 接口版本 | `HY-3D-3.1`（`REFERENCE_GAP-01` = CLOSED；八视图全支持） |
| 配套合同 | `docs/STAGE1B_HUNYUAN_SINGLE_IMAGE_TEST_CONTRACT_R1.md`（**保留**） |
| Multi-view fallback 约束 | **必须重新受 `REFERENCE_ACQUISITION_GATE` 约束**（12 项逐条恢复强制力） |

**不得把 Hunyuan3D 删除出项目历史。** 它从 `PRIMARY_GEOMETRY_SOURCE` 降级为 `OPTIONAL_FALLBACK_GEOMETRY_SOURCE`。

**`ROUTE_B_EXECUTION = DEFERRED` 的原因**：已经获得可加工、CC0、解剖可用、四边面、含短前臂的 Route C 母体。
当前没有足够收益去消耗额度做 A02 单图 AI 重建。

**未来只有以下情况允许重新触发**：
1. Route C Stage 4 出现**结构性失败**；
2. Human Review **明确要求** AI 对照实验；
3. 未来研究**新的手资产生产策略**。

---

## 11. 真人 8 视图的新角色

| 字段 | 值 |
| --- | --- |
| `REAL_HUMAN_8VIEW_REFERENCE` | **`OPTIONAL_NON_BLOCKING_FOR_ROUTE_C`** |

**在 `ROUTE C PRIMARY` 主路线下**：真人 8 视图**不再是 geometry bootstrap 的强制条件**。

**允许用途**：
- 解剖比例人工校验；
- RSSF 造型辅助；
- 半真实皮肤 / 材质参考；
- 教学观察参考；
- 未来如确有需要的独立验证。

**不得再定义为**：Route C 进入后续阶段的**必要条件**。

**但是**：如果未来人工重新启用 `HUNYUAN3D_MULTIVIEW_FALLBACK`，
则原来的真人多视角要求**重新生效**。此时 `REFERENCE_ACQUISITION_GATE`
**只约束 `HUNYUAN_MULTIVIEW_BRANCH`**，不约束 `ROUTE_C_PRIMARY`。

### 11.1 `HR-09` 适用语义澄清（不删除 `HR-09`）

> **旧规则仍然成立**：CC0 模型图只可作 QC，不得作为 Hunyuan 正式输入。

**新增澄清**：`HR-09` 限制的是 **"CC0 MODEL RENDERED IMAGES 作为 Hunyuan input"**，
**不是** **"CC0 3D ASSET 本身不能作为母体"**。

| 情形 | 是否受 `HR-09` 限制 |
| --- | --- |
| CC0 模型的**渲染截图** → 送进 Hunyuan3D | 🚫 **受限制**（原始规则仍成立） |
| **CC0 3D geometry asset** 本身作为工程母体（Route C） | ✅ **不受限制**——这不是"图"，是资产本身 |

→ **`HR-09` 与 Route C 不存在逻辑冲突。**

---

## 12. `ROUTE_C_SOURCE_GATE`（新增）

> **它控制：Route C geometry bootstrap 是否可以启动。**

| # | PASS 条件 | 实际 |
| --- | --- | --- |
| 1 | 官方来源已验证 | ✅ `C1_SOURCE_VERIFIED = YES` |
| 2 | CC0 授权已验证 | ✅ `C1_LICENSE = CC0` |
| 3 | 文件 SHA-256 已锁定 | ✅ `3c121505…75c137` |
| 4 | 实际 hand asset 已定位 | ✅ `Hand  - Realistic` |
| 5 | `C1_GEOMETRY = PASS` | ✅ |
| 6 | `C1_TOPOLOGY = PASS` 或 `CONDITIONAL_PASS`，且 Conditional 项全部明确绑定后续处理阶段 | ✅ `CONDITIONAL_PASS`；`CON-1`~`CON-7` → Stage 4 |
| 7 | `C1_FOREARM = PASS` | ✅ |
| 8 | RSSF re-pose 可行 | ✅ `C1_RSSF_REPOSE = MODERATE` |
| 9 | Blender 5.1.2 runtime parity = PASS | ✅ |

```
ROUTE_C_SOURCE_GATE = PASS
```

> **只表示**：允许创建 Route C 工程工作副本。
> **不表示**：`RIGHT_HAND_MASTER` 已批准 / Topology 已完成 / Rig 可以开始。

---

## 13. `CON-1` ~ `CON-8`（完整继承）

> 全部为 `CONDITIONAL_PASS` 的附条件项。**`CON-1`~`CON-7` 必须作为 Stage 4 的绑定工程义务。**

| # | 条件项 | 定性 | 处理 | 量级 | 阻塞 Stage 2？ |
| --- | --- | --- | --- | --- | --- |
| **CON-1** | 关节环线密度（`T-01`）：base 层不足；资产自带 L1 后 **PIP / DIP 大部分满足**，**MCP 与 THUMB CMC 仍需局部补线** | 局部 topology | Stage 4 topology patch 至 ≥3 圈 | MINOR | 否 |
| **CON-2** | **THUMB CMC 放射状 topology** 必须专项检查并按需修正 | 局部 topology | `THUMB_CMC_TOPOLOGY_REVIEW = REQUIRED`<br>`THUMB_CMC_RETOPO_IF_NEEDED = REQUIRED` | MINOR | 否 |
| **CON-3** | Retopo 时检查极点是否落在关节弯曲区 | 人工确认 | Stage 4 确认 | MINOR | 否 |
| **CON-4** | 补轻度指甲 / 甲床表现（**semi-realistic，不得照片级**） | 表面细节 | Stage 4 | MINOR | 否 |
| **CON-5** | **RSSF re-pose**。正确顺序：**先建立足够的 deformation topology → 再临时骨架 re-pose → 再完成工程 topology / Rig** | 姿态 | Stage 4（`Spread 10–15° / MCP 20–30° / PIP 25–35° / DIP 10–20°`，技术范围） | MODERATE | 否 |
| **CON-6** | 把 origin 重设到**腕关节旋转中心** | 规范对齐 | Stage 4 | MINOR | 否 |
| **CON-7** | UV overlap / stretch 尚未正式验证 | 待验 | Stage 4 UV 检查 / 重展 | MINOR | 否 |
| **CON-8** | 左手继续执行冻结规则：`RIGHT_HAND_MASTER` → Human Approval → Blender mirror → `LEFT_HAND_MASTER`。**禁止独立 AI 生成左手** | 流程 | **Stage 7**（不在 Stage 4） | — | 否 |
| **CON-9** | **`ASSET_FRAME_NORMALIZATION`**（🔒 R1.3.1 新增）：source asset orientation 与 canonical target frame 必须明确记录；只允许使用已批准的 proper transform（`M = diag(1,−1,−1) = Rx(180°)`，`det = +1`）；🚫 禁止负缩放 / runtime mirror / reflection；normalize 后 `scale = 1`；hand chirality 必须保持 `RIGHT`；canonical frame validation 必须 `PASS` | 规范对齐 / frame | **Stage 4**（完成后才允许 Stage 5 Rig） | MINOR | 否 |

> **注意**：`CON-1`~`CON-7` 已正式绑定为 **Stage 4 工程义务**（见 `PIANO_HAND_MASTER_ASSET_SPEC_R1.md` §2.4.2 与 `PIANO_HAND_PRODUCTION_PIPELINE_R1.md` §1 Stage 4）。
> **`CON-8` 仍属于后续 Left Hand Mirror 阶段。**
> **`CON-9`** 由 **R1.3.1 `ASSET_FRAME_COMPATIBILITY_AUDIT`** 引入（见 `docs/STAGE0_ROUTE_C_R1_3_1_FINAL_CLOSURE.md` 与 `CANONICAL_HAND_POSE_SPEC_R1.md` §1.2.1），绑定 **Stage 4**；**Stage 2 Bootstrap 仍只复制 source asset，不得修改 geometry**。
>
> ### 13.1 R1.3.1 追加记录：Asset Frame 闭合
>
> R1.3 通过 Human Review 后，R1.3.1 执行了一次**纯数学 / 只读**的 `ASSET_FRAME_COMPATIBILITY_AUDIT`：
>
> ```
> ASSET_FRAME_CONFLICT            = RESOLVED
>   └─ conflict_class             = SOURCE_ORIENTATION_LABEL_ERROR
>      └─ 错在哪一个标签           = DORSAL（连带 PALMAR）
>         └─ 原记录                = DORSAL = +Y
>         └─ 实测更正              = DORSAL = −Y ; PALMAR = +Y
>         └─ 未受影响              = DISTAL = −Z（正确）、RADIAL = +X（正确）、RIGHT_HAND（不变）
>
> SOURCE_TO_CANONICAL_TRANSFORM   = DEFINED
>   └─ result                     = ROTATION_ONLY_COMPATIBLE
>   └─ M                          = diag(1, −1, −1) = Rx(180°)
>   └─ det(M)                     = +1（proper rotation；无负缩放 / 无镜像 / 无反射）
>   └─ scale（归一化后）           = 1.0
>
> CON_9_ASSET_FRAME_NORMALIZATION = BOUND_TO_STAGE4
> ```
>
> canonical Asset Frame（`+X = RADIAL` / `+Y = DORSAL` / `+Z = DISTAL`）**本身正确、无需修正**；
> 冲突唯一来源是 **C1 记录对 Y 轴解剖学标签的记录反转**。资产本体未被修改，**官方母文件 byte-unchanged**。

---

## 14. 新增风险（Route C 专项）

> 原风险**不删除**，改为**按分支生效**。

### 14.1 分支作用域调整

| 风险 | 调整后 |
| --- | --- |
| `RK-01`（Hunyuan 猿手） | **`APPLIES_TO = HUNYUAN_BRANCH_ONLY`**；Route C 下 = **`NOT_ACTIVE_PRIMARY_ROUTE_RISK`** |
| `RK-02`（Hunyuan 指间粘连） | **`APPLIES_TO = HUNYUAN_BRANCH_ONLY`**；Route C 下 = **`NOT_ACTIVE_PRIMARY_ROUTE_RISK`** |
| `RK-09`（AI 生成面数噪声） | `APPLIES_TO = HUNYUAN_BRANCH_ONLY` |
| `RK-17`（绕过 `REFERENCE_ACQUISITION_GATE`） | `APPLIES_TO = HUNYUAN_BRANCH_ONLY`（该门禁现仅约束此分支） |
| `RK-04`（拇指 CMC 拓扑） | `APPLIES_TO = BOTH_ROUTES`（Route C 下具体化为 `RC-R1`） |
| `RK-10` / `RK-14` / `RK-15` | `APPLIES_TO = OPTIONAL_REFERENCE_BRANCH`（**不阻塞** Stage 2） |

### 14.2 Route C 新增风险

| ID | 风险 | 缓解 |
| --- | --- | --- |
| **RC-R1** | **THUMB CMC topology 不足**（C1 实测 CMC 区 0 条拇指轴环线） | Stage 4 topology patch + Human Review；Stage 6 `THUMB_OPPOSE` 专项 |
| **RC-R2** | **MCP deformation loops 不足**（base MCP 0–1 圈；L1 后部分指仍不足） | Stage 4 topology patch 至 ≥3 圈 + Human Review |
| **RC-R3** | **RSSF re-pose 后体积塌陷**（MODERATE 量级旋转 10–35°） | 先建 deformation topology → 再 re-pose；**Stage 6 deformation test** |
| **RC-R4** | **误把 subdivision density 当作 deformation-ready topology**（含误认 L1 已达标） | `T-01` / `T-02` / `T-04` + Stage 6；**不得因 L1 存在即判 PASS** |
| **RC-R5** | **修改官方原始 CC0 母文件，导致 provenance 丢失** | 官方母文件 **byte-frozen**；只在 **working copy** 生产；bootstrap receipt 记录来源 hash |
| **RC-R6** | **5.1.2 runtime 与历史 4.5.9 provenance 混淆** | `PROJECT_RUNTIME = 5.1.2`；`C1_REPRO_RUNTIME = 4.5.9`；**两者永久区分** |

---

## 15. 明确保持不变的内容

本次 amendment **不允许改变**以下内容（已逐项核对）：

| # | 冻结项 |
| --- | --- |
| 1 | **Finger ID**：1 = THUMB / 2 = INDEX / 3 = MIDDLE / 4 = RING / 5 = LITTLE |
| 2 | **21 bones / hand**（16 可动关节 + 5 TIP 辅助骨） |
| 3 | **`RIGHT_HAND_MASTER` → `LEFT_HAND_MASTER` 镜像策略**（`LR-01`~`LR-04`） |
| 4 | **`NORMAL_MODE` / `ERROR_DEMO_MODE`**；`DIP_ERROR_DEMO_CONFLICT = RESOLVED` |
| 5 | 教学研究结论；`HR-01` / `HR-02` / `HR-03` 未裁定状态 |
| 6 | `STANDARD_HAND` 尚未裁定的教学参数 |
| 7 | **Stage 5 Rig 规范** |
| 8 | **Stage 6 Deformation Test** |
| 9 | **Stage 7 Left Mirror** |
| 10 | **Stage 8 Animation** |
| 11 | **Stage 9 Human Review** |
| 12 | **Stage 10 GLB** |
| 13 | **Stage 11 Three.js** |
| 14 | WorkBuddy 职责边界；Human Gate 机制（GATE 1–5） |
| 15 | `RSSF` 姿态定义；`HR-06b` / `HR-06c` 技术范围 |
| 16 | `HR-06` / `HR-07` / `HR-08` / `REFERENCE_GAP-01` / `REFERENCE_GAP-05` 已裁定结论 |

### 15.1 不修改历史报告

以下是历史审计链，**不得篡改**：

- `docs/PHASE1_R1_1_AMENDMENT_REPORT.md`
- `docs/PHASE1_R1_2_FINAL_CLOSURE.md`
- `docs/PHASE1_R1_2_1_CONSISTENCY_PATCH.md`
- `docs/STAGE1_AI_MULTIVIEW_RESULT_R1.md`
- `docs/STAGE1B_SHARED_3D_BOOTSTRAP_ROUTE_SELECTION_R1.md`（除已完成的事实性修正外不再重写）
- `docs/STAGE1C_C1_ASSET_QUALIFICATION_R1.md`
- `docs/BLENDER_RUNTIME_DISCOVERY_AUDIT_R1.md`
- `docs/BLENDER_5_1_2_RUNTIME_PARITY_CHECK_R1.md`

**它们全部保留历史语义。**

---

## 16. 当前 authority 状态

```
STAGE0_ROUTE_C_AMENDMENT        = PASS

GEOMETRY_SOURCE_PRIMARY         = CC0_AUTHORED_BASE_MESH
GEOMETRY_SOURCE_PRIMARY_ASSET   = BLENDER_HUMAN_BASE_MESHES_V1_4_1_HAND_REALISTIC
GEOMETRY_SOURCE_LICENSE         = CC0
GEOMETRY_SOURCE_QUALIFICATION   = CONDITIONAL_PASS_ACCEPTED_FOR_ENGINEERING

C1_ASSET_QUALIFICATION          = CONDITIONAL_PASS
ROUTE_C_SOURCE_GATE             = PASS

PROJECT_BLENDER_RUNTIME         = D:\Blender\blender.exe
PROJECT_BLENDER_VERSION         = 5.1.2
C1_QUALIFICATION_REPRO_RUNTIME  = BLENDER_4_5_9_LTS

REAL_HUMAN_8VIEW_REFERENCE      = OPTIONAL_NON_BLOCKING_FOR_ROUTE_C
REFERENCE_ACQUISITION_GATE      = CONDITIONAL_BRANCH_GATE_FOR_HUNYUAN_MULTIVIEW
HUNYUAN3D_ROLE                  = OPTIONAL_FALLBACK_EXPERIMENT
ROUTE_B_EXECUTION               = DEFERRED
2D_IMAGEGEN_MULTIVIEW_ROUTE     = REJECTED_BASELINE

ASSET_FRAME_AUTHORITY           = CONSISTENT
ASSET_FRAME_CONFLICT            = RESOLVED
SOURCE_TO_CANONICAL_TRANSFORM   = DEFINED      （ROTATION_ONLY_COMPATIBLE / M = diag(1,−1,−1) = Rx(180°) / det = +1）
CON_9_ASSET_FRAME_NORMALIZATION = BOUND_TO_STAGE4

STAGE0                          = REFROZEN_AFTER_ROUTE_C_AMENDMENT
STAGE2                          = READY_TO_START_ROUTE_C_BOOTSTRAP
```

> 📌 上述 4 个 `ASSET_FRAME_*` / `CON_9_*` 字段由 **R1.3.1** 追加（`ASSET_FRAME_COMPATIBILITY_AUDIT`）。
> 其余字段为 R1.3 原值，**未改动**。

```

### 16.1 权威流程（修订后）

```
STAGE 0  Research & Spec        COMPLETE / REFROZEN
   ↓
ROUTE_C_SOURCE_GATE             PASS
   ↓
STAGE 2  GEOMETRY BOOTSTRAP     PRIMARY: CC0 《Hand  - Realistic》
   ↓
STAGE 3  GEOMETRY REVIEW        🚦 GATE 2
   ↓
STAGE 4  BLENDER ENGINEERING    Topology Patch / RSSF Re-pose / Nails / Origin / UV
   ↓
STAGE 5  RIG
   ↓
STAGE 6  DEFORMATION TEST       🚦 GATE 3
   ↓
STAGE 7  LEFT HAND MIRROR       🚦 GATE 4
   ↓
STAGE 8  ANIMATION
   ↓
STAGE 9  HUMAN REVIEW           🚦 GATE 5
   ↓
STAGE 10 GLB
   ↓
STAGE 11 THREE.JS
```

**旁支**：

```
OPTIONAL REFERENCES   真人 8 Views  →  Validation / Texture Reference
OPTIONAL FALLBACK     Hunyuan3D     →  Human-trigger only
                                        （Multi-view 时 REFERENCE_ACQUISITION_GATE 重新生效）
```

---

## 17. 本轮未做（停止条件确认）

- 🚫 未创建 C1 working mesh
- 🚫 未修改官方母文件
- 🚫 未应用 Multires
- 🚫 未补 topology
- 🚫 未 re-pose
- 🚫 未加指甲
- 🚫 未改 UV
- 🚫 未改 origin
- 🚫 未 Rig / 未 Skin Weight
- 🚫 未镜像左手
- 🚫 未做动画
- 🚫 未调用 Hunyuan3D（`HUNYUAN3D_CALLED = NO`）
- 🚫 未进入 Three.js
- 🚫 未删除 portable Blender 4.5.9
- 🚫 未修改用户 Blender 5.1 配置
- 🚫 **未自动进入 Stage 2**
- ✅ 已完成：① 影响面扫描；② 4 份当前权威文件的 Route C 一致性更新（+ `REFERENCE_MANIFEST_R1.json`）；③ 一致性扫描；④ 本修订文档

---

## 18. 最终状态输出

```
STAGE0_ROUTE_C_AMENDMENT     = PASS
CURRENT_AUTHORITY_CONSISTENCY = PASS
ROUTE_C_SOURCE_GATE          = PASS
STAGE0                       = REFROZEN
STAGE2                       = READY_TO_START_ROUTE_C_BOOTSTRAP
```

**等待 Human Review。不自动开始模型工程。**

**文档状态：`READY_FOR_HUMAN_REVIEW`**
