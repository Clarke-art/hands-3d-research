# 钢琴手 3D 资产生产流水线 · R1

> `docs/PIANO_HAND_PRODUCTION_PIPELINE_R1.md`
> 项目：钢琴教学双手 3D 交互资产 · 第一阶段
> 版本：**R1.2（最终收口）** + **`STAGE0_ROUTE_C_AMENDMENT`（R1.3）**　基准版本：R1 / R1.1　日期：2026-09-27　状态：**PASS**
>
> **本阶段只定义流水线，不执行流水线。**
>
> ---
> ## 🔄 R1.3 · `STAGE0_ROUTE_C_AMENDMENT`（几何来源权威变更）
>
> 详见 `docs/STAGE0_ROUTE_C_AMENDMENT_R1.md`。
>
> **本次修订只改两件事：**
> 1. **"几何从哪里来"** —— 主母体来源由 `真人 8 视图 → Hunyuan3D Multi-view → Geometry Candidate`
>    改为 **`CC0 Authoritative Base Mesh → Geometry Bootstrap → Geometry Review → Blender Engineering`**。
> 2. **"哪些 Gate 阻塞哪条路线"** —— `REFERENCE_ACQUISITION_GATE` 由全局阻塞门禁降为**分支门禁**（仅约束 Hunyuan Multi-view 分支）。
>
> | 变更点 | 修订后 |
> | --- | --- |
> | `GEOMETRY_SOURCE_PRIMARY` | **`CC0_AUTHORED_BASE_MESH`** |
> | 主母体资产 | **Blender Human Base Meshes v1.4.1 · `Hand  - Realistic`**（CC0） |
> | `PROJECT_BLENDER_RUNTIME` | **`D:\Blender\blender.exe`（Blender 5.1.2）** |
> | `C1_QUALIFICATION_REPRO_RUNTIME` | **Blender 4.5.9 LTS**（历史复现，永久区分） |
> | `ROUTE_C_SOURCE_GATE` | ✅ **PASS** |
> | `REFERENCE_ACQUISITION_GATE` | = **`CONDITIONAL_BRANCH_GATE`**（仅 `HUNYUAN_MULTIVIEW_FALLBACK`） |
> | `REAL_HUMAN_8VIEW_REFERENCE` | = **`OPTIONAL_NON_BLOCKING_FOR_ROUTE_C`** |
> | `HUNYUAN3D_ROLE` | = **`OPTIONAL_FALLBACK_EXPERIMENT`**（人工明确触发才运行） |
> | `ROUTE_B_EXECUTION` | = **`DEFERRED`** |
> | `2D_IMAGEGEN_MULTIVIEW_ROUTE` | = **`REJECTED_BASELINE`**（不得重开） |
> | `STAGE0` | **`REFROZEN_AFTER_ROUTE_C_AMENDMENT`** |
> | `STAGE2` | **`READY_TO_START_ROUTE_C_BOOTSTRAP`** |
>
> **Stage 4 之后的核心生产结构（Rig / Deformation / Mirror / Animation / GLB / Three.js）原则上保持不变。**
>
> ---
>
> **R1.2 收口内容**（详见 `docs/PHASE1_R1_2_FINAL_CLOSURE.md`）：
> - **`STAGE2_FIRST_GENERATION_INPUT` = `8_VIEWS`** —— Stage 2 首轮即提交完整 8 视图
> - **图片总量规则修正**：`RAW_IMAGE_TOTAL_TARGET` ≈ ≤ 6 MB / `BASE64_ENCODED_TOTAL` ≤ 8 MB（官方硬约束）
> - **采集总原则 = `HAND_FIXED` / `LIGHT_FIXED` / `CAMERA_MOVES`**；废弃"光源随相机同步移动"
> - `HR-06b` / `HR-06c` = **`APPROVED_AS_TECHNICAL_RANGE`**；`HR-09` = **`OPTIONAL_NON_BLOCKING`**
> - `REFERENCE_GAP-02` 重新定义为 **`REFERENCE_SOURCE_TO_BE_ACQUIRED_IN_STAGE1`**
> - **新增 `REFERENCE_ACQUISITION_GATE`（Stage 1 → Stage 2）**
> - **`GATE 1` = `PASS`**
>
> **R1.1 修订内容**（详见 `docs/PHASE1_R1_1_AMENDMENT_REPORT.md`）：
> - `HR-06` = **APPROVED**（手 + 短前臂，删除固定 3–5 cm 规则）
> - `HR-08` = **APPROVED**（`ADULT_NEUTRAL`）
> - `REFERENCE_GAP-01` = **CLOSED**（统一 HY-3D-3.1，八视图；已删除旧版兼容降级路线）
> - `HR-07` = **RESOLVED**（`HAND = FIXED / CAMERA = MOVES`）
> - `DIP_ERROR_DEMO_CONFLICT` = **RESOLVED**（`NORMAL_MODE` / `ERROR_DEMO_MODE` 双模式）
>
> **主流水线结构、WorkBuddy 职责边界、Human Gate 机制均保持不变。**

---

## 0. 流水线总览

> **R1.3 修订后形式**：主路线 = `ROUTE C PRIMARY`（CC0 作者化基础网格）。
> Stage 1（真人 8 视图采集）已从**关键路径**移出，降为**旁支**（`OPTIONAL REFERENCES`）。

```
  ┌────────────────────────────────────────────────────────────────────┐
  │  ✅ STAGE 0   Research & Spec（COMPLETE / REFROZEN）                 │
  │     教学研究 · 母版姿态 · 多视角规范 · 资产规范 · 流水线             │
  └───────────────────────────────┬────────────────────────────────────┘
                                  │  ◀ ─ ─ 🚦 ROUTE_C_SOURCE_GATE  ✅ PASS
                                  │          （R1.3 新增；允许创建 Route C 工程工作副本）
  ┌───────────────────────────────▼────────────────────────────────────┐
  │  2  GEOMETRY BOOTSTRAP PRIMARY：CC0 《Hand  - Realistic》            │
  │     仅提取资产 / 建工作副本 / 固定 hash·版本·runtime·provenance       │
  └───────────────────────────────┬────────────────────────────────────┘
                                  │
  ┌───────────────────────────────▼────────────────────────────────────┐
  │  3  GEOMETRY REVIEW    几何人工评审            🚦 GATE 2            │
  │  4  BLENDER ENGINEERING 工作副本 / Topology Patch / RSSF Re-pose     │
  │                         指甲 / origin / UV 校验                      │
  │  5  RIG                骨骼绑定（16 关节 + 5 指尖骨）               │
  │  6  DEFORMATION TEST   变形测试（6 项）         🚦 GATE 3           │
  │  7  LEFT HAND MIRROR   镜像生成左手             🚦 GATE 4           │
  │  8  ANIMATION          9 个 Pose / Clip                             │
  │  9  HUMAN REVIEW       教学与资产终审           🚦 GATE 5           │
  │  10 GLB                导出与校验                                   │
  │  11 THREE.JS           Web 3D runtime 集成                          │
  └────────────────────────────────────────────────────────────────────┘

  ── 旁支 A · OPTIONAL REFERENCES（非阻塞）─────────────────────────────
     真人 8 Views  ──▶  Validation / Texture Reference
     （旧 Stage 1；Route C 主路线下不再是 geometry bootstrap 的强制条件）

  ── 旁支 B · OPTIONAL FALLBACK（仅人工触发）───────────────────────────
     Hunyuan3D  ──▶  Human-trigger only
     若 fallback 使用 Multi-view：REFERENCE_ACQUISITION_GATE 重新生效
```

---

## 1. Stage 明细

### Stage 0 — Research & Spec ✅ **COMPLETE / REFROZEN**

| 项 | 内容 |
| --- | --- |
| **输入** | 项目需求 |
| **输出** | 6 份文档 + 1 份参考清单（见 §6）+ Route C 修订文档 |
| **执行** | WorkBuddy（研究 + 规范撰写），人工审核 |
| **状态** | ✅ **`COMPLETE`** —— GATE 1 = **PASS**<br>🔒 **`REFROZEN_AFTER_ROUTE_C_AMENDMENT`**（R1.3 修订后重新冻结） |
| **已完成** | 教学研究 · 母版姿态 · 多视角规范 · 资产规范 · 流水线 · 参考清单 · R1.1 修订 · R1.2 收口 · Stage 1A/1B/1C · Blender runtime parity · **Route C Amendment（R1.3）** |
| **未做** | 未建 mesh、未生成、未绑定、未动画、未编码、未采集图片 |

> **📌 R1.3 判定说明**：`STAGE0 = REFROZEN`。几何来源权威已由本修订正式变更，
> Stage 2 的主输入不再是真人多视角参考图，而是 **CC0 作者化基础网格**。
> 真人 8 视图转为**非阻塞的可选校验 / 纹理参考**（旁支 A）。

---

### Stage 1 — REFERENCE / VALIDATION SOURCES（⚠ **非关键路径** · R1.3 重新定角色）

> **R1.3 重要变更**：在 `ROUTE C PRIMARY` 主路线下，**真人 8 视图不再是 geometry bootstrap 的强制前置**。
> 本 Stage 已从关键路径移出，成为**非阻塞旁支**。

| 项 | 内容 |
| --- | --- |
| **正式状态** | **`REAL_HUMAN_8VIEW_REFERENCE = OPTIONAL_NON_BLOCKING_FOR_ROUTE_C`** |
| **输入** | `CANONICAL_HAND_POSE_SPEC_R1.md`、`MULTIVIEW_REFERENCE_PACK_SPEC_R1.md` |
| **任务** | 采集（或授权获取）同一只 **`ADULT_NEUTRAL` 解剖学右手**、同一 `CANONICAL_HAND_POSE` 的 **完整 8 视图**参考图 —— **仅作为可选校验 / 参考素材** |
| **允许用途** | ① 解剖比例人工校验；② RSSF 造型辅助；③ 半真实皮肤 / 材质参考；④ 教学观察参考；⑤ 未来如确有需要的独立验证 |
| **采集原则** | 🔑 **`HAND = FIXED` / `LIGHT = FIXED` / `CAMERA = MOVES`**（若执行采集则仍须遵守） |
| **执行** | **人工**（拍摄 / 授权 / 采购）—— WorkBuddy 不拍摄、不下载、不拼凑 |
| **产出** | `references/hand_r_canonical/selected/*.png` **8 张** + `CONSISTENCY_REPORT.md` + **`LICENSES.md`** |
| **🚦 门禁** | ⚪ **无阻塞作用**（Route C 主路线下）。<br>该阶段自身不再阻塞 Stage 2。<br>⚠ **例外**：若人工重新启用 `HUNYUAN3D_MULTIVIEW_FALLBACK`，则本阶段的 12 项要求**重新生效**并约束该 fallback 分支 |
| **不得再定义为** | 🚫 **不得**把本阶段写成 Route C 进入后续阶段的**必要条件** |
| **禁止** | 🚫 拼凑不同来源/不同人/不同姿态的手冒充同一只手；🚫 用左手补右手；🚫 用 AI 图片补真人视角；🚫 缺视角强行提交（若用于 Hunyuan Multi-view fallback） |

> **📌 旧 GATE 1（Stage 0 → Stage 1）的现行语义**：`GATE_1 = PASS` 这一历史判定**保留**，
> 但其后置含义已改变——它不再指向"进入 Stage 1 采集"，而是指向"`STAGE0 = COMPLETE`"。
> Route C 主路线下真正控制进入 Stage 2 的门禁是 **`ROUTE_C_SOURCE_GATE`**。


---

### 🔒 `REFERENCE_ACQUISITION_GATE`（**R1.3 重定义为分支门禁**）

> ## ⚠ 作用域变更（R1.3 · `STAGE0_ROUTE_C_AMENDMENT`）
>
> | 项 | 旧定义（R1.2） | **新定义（R1.3）** |
> | --- | --- | --- |
> | **门禁类型** | 全局阻塞门禁 | **`CONDITIONAL_BRANCH_GATE`** |
> | **适用路线** | 所有路线 | **仅 `HUNYUAN3D_MULTIVIEW_FALLBACK`** |
> | **对 `ROUTE C PRIMARY`** | 强制前置 | **`REFERENCE_ACQUISITION_GATE = NOT_APPLICABLE_TO_ROUTE_C`** |
>
> **🚫 不得把它写成 `PASS`。** 本门禁**没有被"绕过"**，而是**不适用**——
> 因为 Route C **不使用真人 8 视图做几何重建输入**，该门禁的 12 项条件在 Route C 下**无从谈起**。
>
> **📌 历史 12 项条件必须完整保留，不得删除。** 只改变其 **scope / applicability**。
> 一旦人工重新启用 Hunyuan Multi-view fallback，下列 12 项**逐条恢复强制力**。
>
> **位置**：原为 Stage 1 → Stage 2 之间；现为 `OPTIONAL FALLBACK ⇒ Hunyuan Multi-view` 分支入口。

| # | 条件 |
| --- | --- |
| **1** | 已获得同一只 **`ADULT_NEUTRAL` 解剖学右手** |
| **2** | 全部 8 张来自**同一只手、同一次采集会话、同一个 `CANONICAL_HAND_POSE`** |
| **3** | 采集原则 **`HAND = FIXED` / `LIGHT = FIXED` / `CAMERA = MOVES`** 已实际遵守 |
| **4** | **完整 8 视图存在**：DORSAL / PALMAR / RADIAL / ULNAR / DISTAL / PROXIMAL / DORSAL_OBLIQUE_RADIAL / DORSAL_OBLIQUE_ULNAR |
| **5** | **手悬空** —— 掌部、手指、指尖没有：接触桌面 / 接触琴键 / 接触支架 / 被支撑压平掌弓 |
| **6** | **短前臂存在**，足以表达**前臂—手腕—手掌**方向与连续关系 |
| **7** | 8 张图完成**一致性 QC**：姿态一致 / 手指张开一致 / 掌宽比例一致 / 指长比例一致 / 拇指旋前一致 / 无明显时间漂移 |
| **8** | 若使用单相机环绕：**`DORSAL_PRE` / `DORSAL_POST` 漂移校验 PASS** |
| **9** | **授权完成**：至少存在 `LICENSES.md`，并明确——模特授权 / 图片使用权 / **商业数字教材使用范围** / **是否允许修改与 AI 3D 生成** |
| **10** | **图片技术参数 PASS**：`RAW_IMAGE_TOTAL_TARGET` ≤ **~6 MB**；`BASE64_ENCODED_TOTAL` ≤ **8 MB** |
| **11** | **Hunyuan3D 3.1 `ViewType` 映射检查 PASS** |
| **12** | **`MULTIVIEW_REFERENCE_PACK_SPEC` Pre-flight Checklist 全部 PASS** |

> 🚫 **在 Hunyuan Multi-view 分支上严禁为了赶进度**：
> - 拼不同人的手
> - 拼不同姿态
> - 用左手补右手
> - 用 AI 图片补真人视角
> - 用 CC0 模型图代替正式真人输入
> - 缺视角也强行提交

---

### 🔑 `ROUTE_C_SOURCE_GATE`（R1.3 新增 · Route C 工程引导入口）

> **位置：Stage 0 之后、Stage 2（Geometry Bootstrap）之前。**
> **它控制：Route C geometry bootstrap 是否可以启动。**
>
> ## ✅ `ROUTE_C_SOURCE_GATE = PASS`

| # | PASS 条件 | 实际 |
| --- | --- | --- |
| **1** | 官方来源已验证 | ✅ `C1_SOURCE_VERIFIED = YES`（Blender 官方域） |
| **2** | CC0 授权已验证 | ✅ `C1_LICENSE = CC0` |
| **3** | 文件 SHA-256 已锁定 | ✅ `3c121505651140ceb4d69fd1d8923f7788ffadd81672f5be14845a5f2c75c137` |
| **4** | 实际 hand asset 已定位 | ✅ `Hand  - Realistic`（`Hand` 与 `-` 之间**两个空格**） |
| **5** | `C1_GEOMETRY = PASS` | ✅ |
| **6** | `C1_TOPOLOGY = PASS` 或 `CONDITIONAL_PASS`，且 Conditional 项全部明确绑定后续处理阶段 | ✅ `CONDITIONAL_PASS`；`CON-1`~`CON-7` 已绑定 Stage 4（见 §1 Stage 4 与修订文档 §13） |
| **7** | `C1_FOREARM = PASS` | ✅（已含 ≈9.2 cm 短前臂） |
| **8** | RSSF re-pose 可行 | ✅ `C1_RSSF_REPOSE = MODERATE`（临时骨架可完成，无需雕刻） |
| **9** | Blender 5.1.2 runtime parity = PASS | ✅ `BLENDER_5_1_2_RUNTIME_PARITY = PASS` |

> ## ⚠ 上述条件全部成立 → `ROUTE_C_SOURCE_GATE = PASS`。
> **注意：`PASS` 只表示——允许创建 Route C 工程工作副本。**
>
> 🚫 **不表示**：
> - `RIGHT_HAND_MASTER` 已批准；
> - Topology 已完成；
> - Rig 可以开始。
>
> **依据**：`docs/STAGE1C_C1_ASSET_QUALIFICATION_R1.md`、`docs/BLENDER_5_1_2_RUNTIME_PARITY_CHECK_R1.md`、
> 以及 `docs/STAGE0_ROUTE_C_AMENDMENT_R1.md` §12 / §16。

---

### Stage 2 — GEOMETRY BOOTSTRAP（R1.3 重定义）

> **原 Stage 2**：`Hunyuan3D Multi-view Generation`。
> **R1.3 后**：`GEOMETRY BOOTSTRAP`，主路线 = `ROUTE C PRIMARY`。

| 项 | 内容 |
| --- | --- |
| **主路线** | **`ROUTE C PRIMARY`** |
| **输入** | **Blender Human Base Meshes v1.4.1 · `Hand  - Realistic`**（官方 CC0 母文件，**byte-frozen**） |
| **母文件路径** | `references/licenses/blender_human_base_meshes/extracted/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend` |
| **输出** | 一个项目工作副本：**`RIGHT_HAND_BOOTSTRAP_C1`**（或符合现有命名规范的等价名称） |
| **🔒 入口门禁** | **`ROUTE_C_SOURCE_GATE = PASS`** |
| **✅ Stage 2 Route C 只允许** | ① 从官方 CC0 母文件**提取目标 hand asset**；② 建立**项目工作副本**；③ 固定**来源 hash**；④ 固定**版本**；⑤ 固定 **runtime**；⑥ 固定 **provenance**；⑦ 建立 **bootstrap receipt** |
| **🚫 Stage 2 Route C 不允许** | 正式 re-pose；topology patch；Retopo；指甲制作；UV 修正；Rig；Skin Weight；Animation<br>**——这些仍属于 Stage 4。** |
| **执行** | **人工 / 3D 资产方**（WorkBuddy 不自行执行几何工程） |

#### Stage 2 · fallback branch（`HUMAN_TRIGGER_REQUIRED = YES`）

| 项 | 内容 |
| --- | --- |
| **保留分支** | `HUNYUAN3D_SINGLE_IMAGE_EXPERIMENT` / `HUNYUAN3D_MULTIVIEW_FALLBACK` |
| **接口版本** | **`HY-3D-3.1` / Hunyuan3D 3.1**（`REFERENCE_GAP-01` = CLOSED）。八视图全支持：`front` / `back` / `left` / `right` / `top` / `bottom` / `left_front` / `right_front`。参数见 `MULTIVIEW_REFERENCE_PACK_SPEC_R1.md` §4 |
| **触发方式** | 🔒 **`HUMAN_TRIGGER_REQUIRED = YES`** —— 🚫 **不得自动执行** |
| **Multi-view fallback 额外约束** | 必须**重新受 `REFERENCE_ACQUISITION_GATE` 约束**（12 项逐条恢复强制力） |
| **当前状态** | **`ROUTE_B_EXECUTION = DEFERRED`**（见 §4 与修订文档 §10） |
| **单图实验合同** | `docs/STAGE1B_HUNYUAN_SINGLE_IMAGE_TEST_CONTRACT_R1.md`（**保留**，当前不执行） |


---

### Stage 3 — GEOMETRY REVIEW（几何人工评审）🚦 **GATE 2**

> **Stage 3 不删除，章节名不变。** R1.3 下允许**直接消费** `STAGE1C_C1_ASSET_QUALIFICATION_R1` 及其证据，
> **不要重复进行整套 Stage 1C 研究。**

| 项 | 内容 |
| --- | --- |
| **输入** | `RIGHT_HAND_BOOTSTRAP_C1` 工程工作副本（+ `STAGE1C_C1_ASSET_QUALIFICATION_R1` 已有证据） |
| **目的（R1.3）** | 正式把项目 working copy **接纳**为 **`RIGHT_HAND_ENGINEERING_CANDIDATE`**，并确认 C1 Qualification 中的 **`CON-1` ~ `CON-7` 已正确绑定到 Stage 4** |
| **任务** | 按 `PIANO_HAND_MASTER_ASSET_SPEC_R1.md` §1 Geometry 逐项评审 |
| **执行** | **人工**（需钢琴教学方 + 3D 资产方**共同**评审） |
| **关键判定** | G-01~**G-15** 逐条；**尤其** G-03（拇指非猿手）、G-04（指间无粘连）、**G-15（`ADULT_NEUTRAL`）**、G-10/G-11（风格禁区） |
| **R1.1 保留判定任务** | ① **确定短前臂最终裁切长度**（`HR-06` FR-05）：按视觉效果裁定，判据为"足以表达前臂—手腕—手掌的方向与连续关系，且能支持腕部过高/中立/过低三态比较；不得延伸至肘部"<br>② **按最终裁切长度复核面数预算**（`HR-10`） |
| **🚫 Stage 3 不要求** | **不要求 `CON-1`~`CON-7` 已经修完。** 这些本来就是 **Stage 4 Engineering tasks** |
| **Stage 3 Gate 2 的核心问题** | **"这个母体是否值得进入工程化？"**<br>基于现有 Human Review：应为 **YES**（⚠ 但本轮 amendment **不自动执行 Stage 3**） |
| **产出** | `GEOMETRY_REVIEW_REPORT.md`（通过 / 打回 + 具体缺陷清单 + 前臂裁切长度与面数复核结论 + **`CON-1`~`CON-7` Stage 4 绑定确认**） |
| **🚦 门禁** | **未通过不得进入 Stage 4** |
| **说明** | 这是全流程**最重要的人工门禁**。几何/拓扑缺陷（尤其指间粘连、拇指方向、关节环线密度）若在此放过，会在 Rig / 蒙皮阶段放大，返工成本极高 |

---

### Stage 4 — BLENDER ENGINEERING（工程化）· **R1.3 Route C 专项合同**

| 项 | 内容 |
| --- | --- |
| **输入** | 通过 GATE 2 的 `RIGHT_HAND_ENGINEERING_CANDIDATE` |
| **执行** | **人工 / 3D 资产方**（WorkBuddy 不在 Blender 中从零雕刻手） |
| **产出** | `RIGHT_HAND_MASTER_retopo.blend` |
| **验收** | 资产规范 §2 Topology 全部条目 |

#### Stage 4 · Route C 专项合同（R1.3 新增，逐条强制）

| # | 要求 |
| --- | --- |
| **1** | 使用 **`D:\Blender\blender.exe`**（`PROJECT_BLENDER_RUNTIME`） |
| **2** | 🚫 **不得直接修改官方 CC0 原始母文件。** 必须建立 **`PROJECT WORKING COPY`**；官方原始资产保持 **`BYTE-UNCHANGED`** |
| **3** | **决定工作拓扑基础**：官方 base + 官方现有 L1 multires。**具体如何应用必须记录**。🚫 **不得因为 L1 存在，就自动认为动画 topology PASS** |
| **4** | 处理 **`CON-1`**：MCP / CMC deformation topology 补线 |
| **5** | 处理 **`CON-2`**：THUMB CMC 专项。必须建立独立检查：<br>**`THUMB_CMC_TOPOLOGY_REVIEW = REQUIRED`**<br>**`THUMB_CMC_RETOPO_IF_NEEDED = REQUIRED`** |
| **6** | 处理 **`CON-3`**：极点位置（确认极点不落在关节弯曲区） |
| **7** | 处理 **`CON-4`**：轻度指甲 / 甲床几何。保持 **`semi-realistic`**；🚫 **不得制作照片级指甲** |
| **8** | 处理 **`CON-5`**：RSSF re-pose。必须使用冻结技术范围：`Finger Spread ≈ 10–15°` / `MCP ≈ 20–30°` / `PIP ≈ 25–35°` / `DIP ≈ 10–20°`。<br>⚠ 这些仍是 **technical range**，**不是 `STANDARD_HAND` 教学参数** |
| **9** | 处理 **`CON-6`**：origin → **腕关节旋转中心（wrist joint rotation center）** |
| **10** | 处理 **`CON-7`**：UV overlap / stretch **validation** |
| **11** | 完成后**才允许**进入 **Stage 5 Rig** |
| **`CON-9`** | 处理 **`CON-9` = `ASSET_FRAME_NORMALIZATION`**（🔒 R1.3.1 新增；权威定义见 `CANONICAL_HAND_POSE_SPEC_R1.md` §1.2.1）：<br>① **source asset orientation 明确记录**（`DISTAL = −Z` / `RADIAL = +X` / **`DORSAL = −Y`** / `PALMAR = +Y`）；<br>② **canonical target frame 明确记录**（`+X = RADIAL` / `+Y = DORSAL` / `+Z = DISTAL`）；<br>③ 只使用**已批准的 proper transform**（`M = diag(1, −1, −1)` = `Rx(180°)`，`det = +1`）；<br>④ 🚫 **禁止负缩放**、🚫 runtime mirror、🚫 reflection；<br>⑤ normalize 后 **`scale = 1`**；<br>⑥ **hand chirality 必须保持 `RIGHT`**；<br>⑦ **canonical frame validation 必须 `PASS`**；<br>⑧ **完成以上之后，才允许进入 Stage 5 Rig**<br>⚠ 本项属 **Stage 4 Engineering**；**Stage 2 Bootstrap 仍只复制 source asset，不得修改 geometry** |
| **关键** | T-01 关节 3 圈环线、T-03 指缝独立、T-04 拇指根部放射状拓扑 |
| **禁止** | 🚫 跳过 Retopo 直接绑定（base 网格密度为"雕刻友好"，**不自动等于**动画变形友好） |


---

### Stage 5 — Rig（绑定）

| 项 | 内容 |
| --- | --- |
| **输入** | Retopo 后的右手模型 |
| **任务** | 按资产规范 §3 建立 21 骨骼（16 可动关节 + 5 指尖骨），设置层级、命名、轴向、关节限制 → 蒙皮权重 |
| **执行** | **人工 / 3D 资产方** |
| **关键** | 绑定中性姿态必须 = `CANONICAL_HAND_POSE`（R-09）；命名 100% 符合 §3.2（R-02） |
| **产出** | `RIGHT_HAND_MASTER_rig.blend` |
| **验收** | 资产规范 §3 Rig + Skin Weight 条目 |

---

### Stage 6 — Deformation Test（变形测试）🚦 **GATE 3**

| 项 | 内容 |
| --- | --- |
| **输入** | 绑定后的右手模型 |
| **任务** | 执行资产规范 §4.2 的 **6 项变形测试姿态** |
| **执行** | **人工 / 3D 资产方** |
| **必测（分模式）** | **`NORMAL_MODE` 量程内**：`DEFORM_TEST_FIST` / `EXTEND` / `SPREAD` / **`THUMB_OPPOSE`（最高风险）**<br>**`ERROR_DEMO_MODE` 下**：`DEFORM_TEST_ERR_COLLAPSED_MCP` / `DEFORM_TEST_ERR_COLLAPSED_DIP` |
| **判定** | 关节无塌陷、无"糖果纸"扭转、无撕裂、无穿模；相邻指无权重污染 |
| **R1.1 分模式判定** | ① `NORMAL_MODE` 前 4 项：验证正常教学动作的变形质量<br>② `ERROR_DEMO_MODE` 后 2 项：验证错误对比可做，且受控过伸下蒙皮不塌陷/不穿模（S-08）<br>③ **验证双模式机制本身**：`NORMAL_MODE` 下 DIP 过伸确实被 limit 阻止（DM-01）；`ERROR_DEMO_MODE` 只能由教学流程触发，退出后必定恢复（DM-02 / DM-03） |
| **产出** | `DEFORMATION_TEST_REPORT.md`（含各测试姿态截图 + **双模式验证结论**） |
| **🚦 门禁** | **未通过不得进入 Stage 7** |
| **说明** | 拇指 CMC 拓扑问题（T-04）**只在** `THUMB_OPPOSE` 测试中暴露，静态评审看不出来 |
| **📌 冲突已消解** | R1 中"DIP 禁止过伸（R-04）"与"DIP 必须能塌陷（R-05）"的表面冲突，已由资产规范 §3.5 的双模式机制消解。本阶段按模式分别测试即可 |

---

### Stage 7 — Left Hand Mirror（左手镜像）🚦 **GATE 4**

| 项 | 内容 |
| --- | --- |
| **输入** | 通过 GATE 3 的 `RIGHT_HAND_MASTER` |
| **前提** | **`RIGHT_HAND_MASTER` 已人工批准** |
| **任务** | Blender 中 X 轴镜像 → 应用变换 → 重算法线 → 校验权重镜像 → 校验动画曲线 X 旋转 |
| **执行** | **人工 / 3D 资产方** |
| **必检** | 资产规范 §5.4 的 **7 项镜像专项检查**；**首要项：两拇指相对朝向中央 C**（`C-ID-04`） |
| **产出** | `LEFT_HAND_MASTER.blend` |
| **🚦 门禁** | 7 项检查未全过不得进入 Stage 8 |
| **禁止** | 🚫 用 Three.js 运行时负缩放实现左手；🚫 AI 独立生成左手 |

---

### Stage 8 — Animation（动画制作）

| 项 | 内容 |
| --- | --- |
| **输入** | `RIGHT_HAND_MASTER` + `LEFT_HAND_MASTER` |
| **任务** | 制作资产规范 §4.1 的 **9 个 Pose / Clip**（双手各一套，同名） |
| **执行** | **人工 / 3D 资产方**（动作数值由教学方给出） |
| **关键** | `FINGER_n_PRESS` 须含手腕/掌部伴随调整（`C-SH-06`）；弹 1 指 vs 弹 5 指掌部位置有差异（`C-SH-07`） |
| **产出** | 带动画的 `.blend` |
| **🚦 前置门禁** | ⚠ **`HR-01` / `HR-02` / `HR-03` / `REFERENCE_GAP-04` 必须先裁定** —— `STANDARD_HAND` 的关节角度与 `FINGER_n_PRESS` 的抬指高度均依赖它们。**未裁定前不得臆测数值** |

---

### Stage 9 — Human Review（终审）🚦 **GATE 5**

| 项 | 内容 |
| --- | --- |
| **任务** | **教学终审 + 资产终审双签** |
| **教学终审** | 标准手型是否正确；1–5 指编号是否正确；错误对比是否恰当；**是否可能误导学生** |
| **资产终审** | 资产规范 §9 验收清单 A–F 全部通过 |
| **执行** | **人工**（钢琴教学方 + 3D 资产方） |
| **产出** | `FINAL_HUMAN_REVIEW_SIGN_OFF.md` |
| **🚦 门禁** | **未双签不得导出交付** |

---

### Stage 10 — GLB（导出与校验）

| 项 | 内容 |
| --- | --- |
| **任务** | 按资产规范 §8 导出 `hand_right_master.glb` / `hand_left_master.glb` |
| **校验** | glTF 2.0 Binary；单位米；Y-up；scale=1；骨骼与蒙皮已导出；**指尖辅助骨保留**；动画 clip 命名正确 |
| **运行时验证** | 在 Three.js / glTF Viewer 中播放全部动画 clip，确认骨骼层级与蒙皮正常 |
| **产出** | 两个 `.glb` + `EXPORT_VALIDATION.md` |

---

### Stage 11 — Three.js（Web 3D runtime 集成）

| 项 | 内容 |
| --- | --- |
| **任务** | 见 §3「WorkBuddy 职责」 |
| **执行** | **WorkBuddy 主导** |
| **前提** | Stage 10 的 GLB 已通过校验；`HR-10`（面数预算）/ `HR-11`（尺度）/ `HR-12`（键面平面）已裁定 |
| **产出** | 可交互的双手 3D 组件 |

---

## 2. 门禁汇总（R1.3 修订）

| 门禁 | 位置 | 判定者 | 状态 / 未通过后果 |
| --- | --- | --- | --- |
| 🚦 **GATE 1** | Stage 0 → 1 | 人工（教学 + 资产） | ✅ **PASS（R1.2 历史判定，保留）** —— 现行含义 = **`STAGE0 = COMPLETE`** |
| 🔑 **`ROUTE_C_SOURCE_GATE`** | **Stage 0 → Stage 2**（Route C） | 人工（资产 + 授权 + 来源） | ✅ **PASS（R1.3）** —— 允许创建 Route C 工程工作副本。**不代表母版已批准** |
| 🔒 **`REFERENCE_ACQUISITION_GATE`** | **仅 `HUNYUAN_MULTIVIEW_BRANCH`** | 人工（资产 + 授权） | ⚠ **R1.3 重定义为 `CONDITIONAL_BRANCH_GATE`。**<br>Route C 下 = **`NOT_APPLICABLE_TO_ROUTE_C`**（**不是 PASS**） |
| 🚦 **GATE 2** | Stage 3 后 | 教学 + 资产 | 打回 **Stage 2** 重新输出工作副本；或否决该母体 |
| 🚦 **GATE 3** | Stage 6 后 | 资产 | 返回 Stage 4/5 修拓扑或权重 |
| 🚦 **GATE 4** | Stage 7 后 | 资产 | 修正镜像问题 |
| 🚦 **GATE 5** | Stage 9 后 | 教学 + 资产（双签） | 不得导出交付 |

**各门禁的未决事项（R1.3）**：

| 门禁 | 状态 |
| --- | --- |
| **GATE 1**（Stage 0 → 1） | ✅ **PASS** —— 无阻塞项。<br>已批准：`HR-06` · `HR-06b` · `HR-06c` · `HR-08` · `HR-07` RESOLVED · `REFERENCE_GAP-01` CLOSED · `HR-09` OPTIONAL_NON_BLOCKING |
| **`ROUTE_C_SOURCE_GATE`** | ✅ **PASS** —— 9 项条件全部成立（见 §1）。**仅授权创建工程工作副本** |
| **`REFERENCE_ACQUISITION_GATE`** | ⚪ **`NOT_APPLICABLE_TO_ROUTE_C`**（Route C 主路线下）。<br>⚠ 一旦启用 Hunyuan Multi-view fallback，**12 项逐条恢复强制力** |
| **Stage 8 前置** | `HR-01` / `HR-02` / `HR-03` / `REFERENCE_GAP-04` / `HR-13` / `HR-14` |
| **Stage 11 前置** | `HR-10` / `HR-11` / `HR-12` |

> **📌 R1.3 关键变化**：`REFERENCE_GAP-02` 的作用域**收窄到 Hunyuan Multi-view 分支**。
> Route C 主路线下，Stage 2 的入口由 **`ROUTE_C_SOURCE_GATE`** 控制，而它已经 PASS。
> → **`STAGE2 = READY_TO_START_ROUTE_C_BOOTSTRAP`**。
> 🚫 **但 Stage 1 的旧门禁并没有被写成 PASS——它是不适用（NOT_APPLICABLE），不是被绕过。**


---

## 3. WorkBuddy 职责边界

### 3.1 ✅ WorkBuddy **负责**

| # | 职责 |
| --- | --- |
| 1 | **项目工程**：目录结构、文档体系、版本管理约定 |
| 2 | **Three.js**：场景搭建、渲染管线、材质与灯光 |
| 3 | **Web 3D runtime**：GLB 加载、模型实例化、资源释放 |
| 4 | **摄像机交互**：自由旋转（orbit）、缩放（zoom）、平移；俯视 / 斜前 / 侧面预设视角切换 |
| 5 | **手指点击检测**：射线拾取（raycasting）、手指热区判定 |
| 6 | **高亮**：点击 / 悬停手指的高亮表现 |
| 7 | **指法编号**：左右手 1–5 指编号的 UI 呈现与骨骼映射 |
| 8 | **AnimationMixer / 骨骼动画调用**：clip 加载、播放 / 暂停 / 重播、交叉淡入淡出、速度与时间控制 |
| 9 | **动画与视角的解耦**：**动画播放或暂停时仍可自由改变观察视角**（用户明确要求） |
| 10 | **UI**：控件、标注、图例、说明文案容器 |
| 11 | **性能优化**：面数与 Draw Call 预算、LOD、纹理尺寸、帧率保障 |
| 12 | **Web 测试**：跨浏览器 / 分辨率 / 交互冒烟测试 |
| 13 | **资产规范的符合性校验**：在 Three.js 层验证骨骼命名、指尖骨存在性、Finger ID 映射等 |

### 3.2 🚫 WorkBuddy **不负责**

| # | 不负责事项 |
| --- | --- |
| 1 | 🚫 **凭空设计人体手部解剖** —— 手部解剖以 Reference 与人工评审为准 |
| 2 | 🚫 **在 Blender 中从零雕刻 / 建模一只手** —— 手资产走 **`CC0 Authoritative Base Mesh → Geometry Bootstrap → Blender Engineering`** 路线（Route C；原 `Reference → Hunyuan3D → Blender Engineering` 已降为 fallback 分支） |
| 3 | 🚫 **无科学依据地决定标准钢琴手型** —— 教学结论须由教学方与权威来源背书 |
| 4 | 🚫 自行调用混元 3D 生成（fallback 分支亦须人工触发） |
| 5 | 🚫 自行裁定 `HUMAN_REVIEW_REQUIRED` 事项 |
| 6 | 🚫 制作 Rig / Skin Weight / 动画（由 3D 资产方完成） |
| 7 | 🚫 采集、下载或拼凑参考图 |
| 8 | 🚫 决定教学文案的最终表述（WorkBuddy 可提供容器与草稿，最终由教学方审定） |

### 3.3 3D 手资产的生产路线（R1.3 修订）

```
  [ 主路线 · ROUTE C PRIMARY ]
     CC0 Authoritative Base Mesh  →  Geometry Bootstrap  →  Geometry Review
       →  Blender Engineering  →  Human Review

  [ 旁支 A · OPTIONAL REFERENCES · 非阻塞 ]
     真人 8 Views  →  Validation / Texture Reference

  [ 旁支 B · OPTIONAL FALLBACK · 仅人工触发 ]
     Hunyuan3D  （Multi-view fallback 重新受 REFERENCE_ACQUISITION_GATE 约束）
```

WorkBuddy 在此路线中的角色：**规范制定者（本阶段）+ 校验者 + 运行层集成者**，**不是**模型生产者。

---

## 4. 风险登记册

> ## ⚠ R1.3 · 按分支生效（branch-scoped）
>
> **不删除任何原风险。** 一律改为**按分支生效**：
>
> | 标签 | 含义 |
> | --- | --- |
> | **`APPLIES_TO = HUNYUAN_BRANCH_ONLY`** | 仅 `HUNYUAN_MULTIVIEW_FALLBACK` / 单图实验分支有效 |
> | **`ROUTE_C_PRIMARY` 下** | = **`NOT_ACTIVE_PRIMARY_ROUTE_RISK`**（非主路线现行风险） |
> | **`APPLIES_TO = OPTIONAL_REFERENCE_BRANCH`** | 仅在执行可选的真人参考采集时有效 |
> | **`APPLIES_TO = BOTH_ROUTES`** | 两条路线均有效 |
>
> **Route C 的新增风险另行登记为 `RC-R1` ~ `RC-R6`（见下）。**

| ID | 风险 | 阶段 | 影响 | 概率 | 缓解措施 |
| --- | --- | --- | --- | --- | --- |
| **RK-01** | 混元 3D 生成"猿手"（拇指方向与四指趋同）<br>**`APPLIES_TO = HUNYUAN_BRANCH_ONLY`**；Route C 下 = `NOT_ACTIVE_PRIMARY_ROUTE_RISK` | 2–3 | 拇指为教学核心部位，返工成本高 | **高**（仅 Hunyuan 分支） | 参考图 RADIAL 视角强制体现旋前；GATE 2 专项判定 G-03；失败则重生成 |
| **RK-02** | 指间粘连（指缝被缝合）<br>**`APPLIES_TO = HUNYUAN_BRANCH_ONLY`**；Route C 下 = `NOT_ACTIVE_PRIMARY_ROUTE_RISK` | 2–3 | 蒙皮权重互相污染，弹一指带动邻指 | **高**（仅 Hunyuan 分支） | 母版姿态强制扇形张开 10–15°；参考图逐视角确认指间间隙；GATE 2 专项判定 G-04 |
| **RK-03** | ~~掌心视图采集时翻手导致姿态漂移~~ | 1 | — | — | ✅ **已消除**（R1.1）：改为 `HAND = FIXED / CAMERA = MOVES`，手全程不动，从物理上消除漂移源。原风险描述所基于的"必须翻手"前提已作废 |
| **RK-04** | 拇指 CMC 拓扑不足，对掌时撕裂<br>**`APPLIES_TO = BOTH_ROUTES`**（Route C 下具体化为 **`RC-R1`**） | 5–6 | 拇指动画不可用 | **中高** | T-04 放射状拓扑；`DEFORM_TEST_THUMB_OPPOSE` 专项测试；Route C 另加 `THUMB_CMC_TOPOLOGY_REVIEW = REQUIRED` |
| **RK-05** | 镜像后法线 / 负缩放 / 权重镜像错误 | 7 | 左手渲染与动画异常 | **中** | §5.4 七项专项检查；GATE 4 |
| **RK-06** | 教学流派差异（Lhevinne vs Taubman）未裁定就做动画 | 8 | 标准手型可能不被教学方认可 | **中高** | `HR-01`~`HR-03` 必须在 Stage 8 前裁定（已设为前置门禁） |
| **RK-07**（R1.2 修正） | 图片总量超限：`BASE64_ENCODED_TOTAL` > **8 MB**（官方硬约束） | 1–2 | 提交失败 | **中** | **先降分辨率 → 再转高质量 JPG**；**优先保留完整 8 视图，不得首先减少视角**。<br>工程目标：原始总量 `RAW_IMAGE_TOTAL_TARGET` ≈ ≤ 6 MB（因 base64 约膨胀 30%）。见多视角规范 §3.1.1 / §3.2.1 |
| **RK-08** | ~~接口版本不支持 `top`/`bottom`/斜视角~~ | 2 | — | — | ✅ **已关闭**（R1.1）：`REFERENCE_GAP-01` = CLOSED，统一 HY-3D-3.1，八视图全支持；旧版兼容降级设计已删除 |
| **RK-09** | 生成的面数过高，表面噪声大<br>**`APPLIES_TO = HUNYUAN_BRANCH_ONLY`** | 2–4 | Retopo 难度上升 | **中**（仅 Hunyuan 分支） | 首轮 `FaceCount` 控制在 80k–150k，不用默认 500k |
| **RK-10** | 参考图授权不清晰（真人肖像 / 素材授权）<br>**`APPLIES_TO = OPTIONAL_REFERENCE_BRANCH`** | 1（旁支） | 商业教材合规风险 | **中** | `LICENSES.md` 强制登记；优先自主拍摄或采购可商用授权。⚠ Route C 主路线下**不阻塞** Stage 2 |
| **RK-11** | ~~母版人群特征未定，做完后发现应为儿童手~~ | 1 | — | — | ✅ **已关闭**（R1.1）：`HR-08` = APPROVED → `ADULT_NEUTRAL`。**变更触发条件**：若教材后续被确认面向儿童学习者，须另起变更重新裁定 |
| **RK-12** | 面数 / 纹理超出 Web 目标设备预算 | 10–11 | 低端设备卡顿 | **中** | `HR-10` 结合目标设备裁定；预留 LOD；**按最终前臂裁切长度复核面数**（Stage 3） |
| **RK-13** | 手型量化角度缺失（`REFERENCE_GAP-04`），动画数值靠推测 | 8 | 教学演示失真 | **高** | 设为 Stage 8 前置门禁；由教学方提供数值 |

### R1.2 新增 / 变更风险

| ID | 风险 | 阶段 | 影响 | 概率 | 缓解措施 |
| --- | --- | --- | --- | --- | --- |
| **RK-17** | **为赶进度绕过 `REFERENCE_ACQUISITION_GATE`**（拼不同人的手 / 拼不同姿态 / 用左手补右手 / 用 AI 图补真人视角 / 用 CC0 模型图代替真人输入 / 缺视角强行提交）<br>**`APPLIES_TO = HUNYUAN_BRANCH_ONLY`** —— R1.3 后该门禁**只约束 Hunyuan Multi-view 分支** | 仅 Hunyuan 分支入口 | 生成几何自相矛盾；缺陷往往到 Rig / 蒙皮阶段才暴露，返工成本极高 | **中**（仅 Hunyuan 分支） | `REFERENCE_ACQUISITION_GATE` 12 项硬条件 + 明确"严禁"清单；`LICENSES.md` 强制登记；GATE 由人工判定 |

### R1.3 新增 · Route C 专项风险

> 对应 `docs/STAGE0_ROUTE_C_AMENDMENT_R1.md` §14。

| ID | 风险 | 阶段 | 影响 | 概率 | 缓解措施 |
| --- | --- | --- | --- | --- | --- |
| **RC-R1** | **THUMB CMC topology 不足**（C1 实测 CMC 区 0 条拇指轴环线） | 4 / 6 | 拇指对掌时掌部撕裂或"橡皮筋"拉伸 | **中高** | Stage 4 topology patch（`THUMB_CMC_TOPOLOGY_REVIEW = REQUIRED`）+ Human Review；Stage 6 `THUMB_OPPOSE` 专项 |
| **RC-R2** | **MCP deformation loops 不足**（base 层 MCP 仅 0–1 圈；L1 后部分指仍不足） | 4 / 6 | 掌指关节屈曲塌陷、体积丢失 | **中高** | Stage 4 topology patch 补至 ≥3 圈 + Human Review |
| **RC-R3** | **RSSF re-pose 后体积塌陷**（MODERATE 量级旋转 10–35°） | 4 / 6 | 关节折面、体积丢失 | **中** | **先建 deformation topology → 再临时骨架 re-pose → 再 Retopo/Rig**；Stage 6 deformation test |
| **RC-R4** | **误把 subdivision density 当作 deformation-ready topology**（含误认 L1 multires 已达标） | 4 / 6 | 拓扑审查被跳过，缺陷延迟到蒙皮阶段暴露 | **中高** | `T-01` / `T-02` / `T-04` 逐条复核 + Stage 6 deformation test；**不得因 L1 存在即判 PASS** |
| **RC-R5** | **修改官方原始 CC0 母文件，导致 provenance 丢失** | 2 / 4 | 来源与授权证据链断裂，不可审计 | **中** | 官方母文件 **byte-frozen**；只在 **`PROJECT WORKING COPY`** 上生产；Stage 2 建立 bootstrap receipt 记录来源 hash |
| **RC-R6** | **5.1.2 runtime 与历史 4.5.9 provenance 混淆** | 4+ | 复现记录失真，资格结论被误引用 | **中** | `PROJECT_RUNTIME = 5.1.2`；`C1_REPRO_RUNTIME = 4.5.9`；**两者永久区分**，历史 provenance 不得改写 |


### R1.1 新增风险

| ID | 风险 | 阶段 | 影响 | 概率 | 缓解措施 |
| --- | --- | --- | --- | --- | --- |
| **RK-14**（R1.2 重写；R1.3 收窄作用域） | **多视角采集过程中光照环境发生变化**<br>**`APPLIES_TO = OPTIONAL_REFERENCE_BRANCH`**（仅在执行可选真人参考采集时有效；Route C 主路线下不阻塞） | 1（旁支） | 各视角光照不一致 → 多视角重建质量下降 | **中高**（仅旁支） | ① 使用**固定室内拍摄环境**；② 使用**固定柔光帐 / 大面积漫射光**；③ **8 视图期间灯位、强度、色温不变**（`LIGHT = FIXED`）；④ **避免自然光作为主要光源**；⑤ 多相机同步可**减少拍摄时间**从而间接降低光线漂移概率，但**不改变 `LIGHT = FIXED` 原则**。见多视角规范 §2.3 / §5.3 |
| **RK-15** | **悬空固定导致姿态难以长时间保持**：手悬空无支撑，长时间采集可能疲劳抖动<br>**`APPLIES_TO = OPTIONAL_REFERENCE_BRANCH`** | 1（旁支） | 姿态漂移 | **中**（仅旁支） | 前臂末端可靠固定；优先多相机同步（缩短采集时长）；单相机方案缩短单圈时间并做 `DORSAL_PRE/POST` 校验 |
| **RK-16** | **`ERROR_DEMO_MODE` 退出后未恢复**：模式切换实现缺陷导致学生停留在可自由反折 DIP 的状态 | 8 / 11 | 学生可随意反折手指 → 教学事故 | **中** | 优先采用 **P-1 专门 Pose**（架构上不可能让学生自由反折）；若用 P-2，必须在运行时保证退出路径；Stage 6 与 Stage 9 双验证（DM-01~DM-03） |

---

## 5. 目录结构（R1.3 对齐实际）

```
hands/
├── docs/                                    # 研究与规范
│   ├── PIANO_HAND_PEDAGOGY_RESEARCH_R1.md
│   ├── CANONICAL_HAND_POSE_SPEC_R1.md
│   ├── MULTIVIEW_REFERENCE_PACK_SPEC_R1.md
│   ├── PIANO_HAND_MASTER_ASSET_SPEC_R1.md
│   ├── PIANO_HAND_PRODUCTION_PIPELINE_R1.md
│   ├── PHASE1_R1_1_AMENDMENT_REPORT.md
│   ├── PHASE1_R1_2_FINAL_CLOSURE.md
│   ├── PHASE1_R1_2_1_CONSISTENCY_PATCH.md
│   ├── STAGE1_AI_MULTIVIEW_*_R1.md          # Stage 1A（FAIL 历史链）
│   ├── STAGE1B_SHARED_3D_BOOTSTRAP_ROUTE_SELECTION_R1.md
│   ├── STAGE1B_HUNYUAN_SINGLE_IMAGE_TEST_CONTRACT_R1.md   # 保留 · 当前 DEFERRED
│   ├── STAGE1C_C1_ASSET_QUALIFICATION_R1.md
│   ├── BLENDER_RUNTIME_DISCOVERY_AUDIT_R1.md
│   ├── BLENDER_5_1_2_RUNTIME_PARITY_CHECK_R1.md
│   └── STAGE0_ROUTE_C_AMENDMENT_R1.md       # R1.3 修订文档（本次新增）
│
├── reference_manifest/
│   └── REFERENCE_MANIFEST_R1.json
│
├── references/
│   ├── hand_r_canonical/                    # 真人 8 视图（旁支 A · 非阻塞 · 尚未采集）
│   │   ├── raw/
│   │   ├── selected/
│   │   ├── qc/
│   │   └── CONSISTENCY_REPORT.md
│   ├── hand_r_canonical_ai/                 # Stage 1A AI 派生候选（已判 FAIL，历史证据）
│   ├── licenses/
│   │   └── blender_human_base_meshes/       # ✅ Route C 官方 CC0 母文件 + 授权证据
│   └── LICENSES.md
│
├── production_spec/
│   ├── stage1c_c1_qualification/            # C1 资格审查证据（Renders / Wireframes / stats / scripts）
│   ├── runtime_parity/blender_5_1_2/        # 5.1.2 runtime parity 证据
│   ├── stage2_bootstrap/                    # ⏳ Stage 2 目标目录（尚未创建；原 stage2_hunyuan 降为 fallback）
│   ├── stage3_geometry_review/
│   ├── stage4_blender/
│   ├── stage5_rig/
│   ├── stage6_deformation_test/
│   ├── stage7_mirror/
│   ├── stage8_animation/
│   ├── stage9_human_review/
│   └── stage10_glb/
│
└── (web runtime)                            # Three.js 集成（Stage 11，尚未创建）
```

> 📌 `production_spec/stage1c_c1_qualification/` 与 `runtime_parity/` 为**已存在的证据目录**，不得删除。
> `stage2_bootstrap/` 为 Stage 2 的目标目录，**本轮不创建**（本轮禁止进入 Stage 2）。


---

## 6. 本阶段产出清单

| # | 文件 | 内容 |
| --- | --- | --- |
| 1 | `docs/PIANO_HAND_PEDAGOGY_RESEARCH_R1.md` | 钢琴标准手型、指法编号、常见错误和来源 |
| 2 | `docs/CANONICAL_HAND_POSE_SPEC_R1.md` | **RSSF 母版手姿态 / 工程 re-pose / Rig neutral pose 定义**（🔄 R1.3.1 路线中立化：不再以"混元 3D 多视角生成的母版"为唯一用途；Hunyuan 多视角只是 fallback 分支的用途之一，见 §1.2.1） |
| 3 | `docs/MULTIVIEW_REFERENCE_PACK_SPEC_R1.md` | 参考视角、图像一致性要求和缺口 |
| 4 | `docs/PIANO_HAND_MASTER_ASSET_SPEC_R1.md` | Geometry / Topology / Rig / Animation / Left-Right strategy |
| 5 | `docs/PIANO_HAND_PRODUCTION_PIPELINE_R1.md` | 本文件：11 阶段流水线与职责边界 |
| 6 | `reference_manifest/REFERENCE_MANIFEST_R1.json` | 实际采用参考资料的结构化清单 |
| 7 | `docs/PHASE1_R1_1_AMENDMENT_REPORT.md` | R1.1 窄修订报告：5 项裁定的逐条变更记录 |
| 8 | `docs/PHASE1_R1_2_FINAL_CLOSURE.md` | **R1.2 最终收口报告**：8 视图规则 / 6MB-8MB 修正 / 采集原则 / 各 HR 裁定 / `REFERENCE_ACQUISITION_GATE` / 冻结状态 |
| 9 | `docs/PHASE1_R1_2_1_CONSISTENCY_PATCH.md` | R1.2.1 一致性补丁 |
| 10 | `docs/STAGE1_AI_MULTIVIEW_RESULT_R1.md` | Stage 1A 结果：`AI_MULTIVIEW_FEASIBILITY = FAIL` |
| 11 | `docs/STAGE1B_SHARED_3D_BOOTSTRAP_ROUTE_SELECTION_R1.md` | Stage 1B 路线选择：推荐 `ROUTE C` 主 + `ROUTE B` 受限实验 |
| 12 | `docs/STAGE1C_C1_ASSET_QUALIFICATION_R1.md` | Stage 1C C-1 资产资格审查：`C1_ASSET_QUALIFICATION = CONDITIONAL_PASS` |
| 13 | `docs/BLENDER_5_1_2_RUNTIME_PARITY_CHECK_R1.md` | 5.1.2 runtime parity：`BLENDER_5_1_2_RUNTIME_PARITY = PASS` |
| 14 | `docs/STAGE0_ROUTE_C_AMENDMENT_R1.md` | **R1.3 Route C 修订文档**：几何来源权威变更、Gate 重定义、`CON-1`~`CON-8`、新风险 |
| 15 | `docs/STAGE0_ROUTE_C_R1_3_1_FINAL_CLOSURE.md` | **R1.3.1 Route C 最终一致性收口**：`ASSET_FRAME_COMPATIBILITY_AUDIT`、`SOURCE_TO_CANONICAL_TRANSFORM`、`CON-9` 绑定 Stage 4、LowPoly 残留清除、旧主流水线字段历史化、最终一致性扫描 |

> 注：`docs/PIANO_HAND_PEDAGOGY_RESEARCH_R1.md`（教学研究）**未修改**（R1.1 / R1.2 / R1.3 均未动）。
> 三轮修订均为 **3D 生产侧决策**，不涉及教学结论，亦不改变教学类的 `HUMAN_REVIEW_REQUIRED` 与 `REFERENCE_GAP-03 / 04`。


---

## 7. 本阶段禁止事项（重申）

**Stage 0 / Phase 1 已完成并冻结（R1.3 后重新冻结）。在完成 Human Review 之前，本阶段未进行且不得进行：**

- 🚫 创建最终 hand mesh
- 🚫 从零 Blender 雕刻 / 建模手
- 🚫 腾讯混元 3D 生成
- 🚫 Rig / Skin Weight
- 🚫 动画
- 🚫 Three.js
- 🚫 HTML UI
- 🚫 钢琴键盘开发
- 🚫 **开始拍摄 / 搜索或下载参考图**（属旁支 A，非阻塞）
- 🚫 自动进入下一阶段

### 7.1 `STAGE0_ROUTE_C_AMENDMENT` 本轮禁止（R1.3）

> 本轮**只做规范修订**。以下**一律不得执行**：

- 🚫 创建 C1 working mesh
- 🚫 修改官方母文件
- 🚫 应用 Multires
- 🚫 补 topology
- 🚫 re-pose
- 🚫 加指甲
- 🚫 改 UV
- 🚫 改 origin
- 🚫 Rig / Skin Weight
- 🚫 镜像左手
- 🚫 动画
- 🚫 Hunyuan3D
- 🚫 Three.js
- 🚫 删除 portable Blender 4.5.9
- 🚫 修改用户 Blender 5.1 配置
- 🚫 **自动进入 Stage 2**


---

## 8. 当前阶段状态（R1.3）

```
STAGE0                  = COMPLETE / REFROZEN_AFTER_ROUTE_C_AMENDMENT
ROUTE_C_SOURCE_GATE     = PASS
STAGE2                  = READY_TO_START_ROUTE_C_BOOTSTRAP
```

| 项 | 状态 |
| --- | --- |
| **Stage 0** | ✅ **COMPLETE** —— 研究完成、母版姿态已定义、几何来源权威已变更（R1.3）<br>🔒 **`REFROZEN_AFTER_ROUTE_C_AMENDMENT`** |
| **`ROUTE_C_SOURCE_GATE`** | ✅ **PASS** —— 允许创建 Route C 工程工作副本 |
| **`REFERENCE_ACQUISITION_GATE`** | ⚪ **`NOT_APPLICABLE_TO_ROUTE_C`**（仅约束 Hunyuan Multi-view 分支） |
| **Stage 1（旁支 A）** | ⚪ **非阻塞** —— `REAL_HUMAN_8VIEW_REFERENCE = OPTIONAL_NON_BLOCKING_FOR_ROUTE_C` |
| **Stage 2** | 🟢 **`READY_TO_START_ROUTE_C_BOOTSTRAP`** —— 主输入 = CC0 `Hand  - Realistic` |
| **Route B** | ⏸ **`DEFERRED`**（不得运行；仅人工明确触发可重启） |

**当前权威字段（R1.3）**：

| 字段 | 值 |
| --- | --- |
| `GEOMETRY_SOURCE_PRIMARY` | **`CC0_AUTHORED_BASE_MESH`** |
| `GEOMETRY_SOURCE_PRIMARY_ASSET` | **`BLENDER_HUMAN_BASE_MESHES_V1_4_1_HAND_REALISTIC`** |
| `GEOMETRY_SOURCE_LICENSE` | **`CC0`** |
| `GEOMETRY_SOURCE_QUALIFICATION` | **`CONDITIONAL_PASS_ACCEPTED_FOR_ENGINEERING`** |
| `PROJECT_BLENDER_RUNTIME` | **`D:\Blender\blender.exe`**（5.1.2） |
| `C1_QUALIFICATION_REPRO_RUNTIME` | **`BLENDER_4_5_9_LTS`**（历史复现，永久区分） |
| `HUNYUAN3D_ROLE` | **`OPTIONAL_FALLBACK_EXPERIMENT`** |
| `2D_IMAGEGEN_MULTIVIEW_ROUTE` | **`REJECTED_BASELINE`** |

> **下一步**：`STAGE0_ROUTE_C_AMENDMENT` 完成后**停止，等待 Human Review**。
> **不得自动开始模型工程（Stage 2）。**

---

**文档状态：PASS（R1.3 · `STAGE0_ROUTE_C_AMENDMENT` 完成）**　**`STAGE0 = REFROZEN`**　**`STAGE2 = READY_TO_START_ROUTE_C_BOOTSTRAP`**

