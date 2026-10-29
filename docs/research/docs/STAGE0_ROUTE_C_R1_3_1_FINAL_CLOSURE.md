# STAGE 0 · ROUTE C · R1.3.1 — FINAL CONSISTENCY CLOSURE

> `docs/STAGE0_ROUTE_C_R1_3_1_FINAL_CLOSURE.md`
> 项目：钢琴教学双手 3D 交互资产
> 阶段：**`STAGE0_ROUTE_C_R1_3_1`（`ROUTE C FINAL CONSISTENCY CLOSURE`）**
> 日期：2026-09-28　状态：**`READY_FOR_HUMAN_REVIEW`**
>
> **本轮性质：极窄一致性收口。** 不重新研究、不改 Route C 选型、不创建 working mesh、不进入 Stage 2、
> 不修改官方 CC0 母文件、不 re-pose / Retopo / Rig。
> **本轮只关闭 5 个残留问题**：① Asset Frame 标签冲突；② `CON-9` 绑定；③ LowPoly 残留；④ manifest 旧主流水线字段；⑤ pipeline 文案残留。
>
> **执行依据**：Human Review 已通过 `R1.3 Route C Amendment` 主体架构方向；
> 正式批准进入 Stage 2 之前，须先完成一次只读一致性闭合。

---

## 0. 本轮一句话结论

> ## ✅ `STAGE0_ROUTE_C_R1_3_1 = PASS` → `STAGE0 = REFROZEN` → `STAGE2 = READY_TO_START_ROUTE_C_BOOTSTRAP`
>
> Asset Frame 的"表面冲突"被证明是 **SOURCE_ORIENTATION_LABEL_ERROR**：
> C1 记录把 **Y 轴的解剖学标签写反了**（写 `DORSAL = +Y`，实为 `DORSAL = −Y`）。
> canonical Asset Frame 本身**正确、无需修正**；`RIGHT_HAND` 语义**未被改变**；
> 源资产→canonical 帧存在**唯一的 proper rotation**（`det = +1`），**不需要**任何负缩放 / 镜像 / 反射。
> 另外 4 项文档残留（LowPoly、manifest 旧字段、pipeline 文案、以及 `CON-9` 绑定）全部闭合。

---

## 1. 最高优先级：`ASSET_FRAME_COMPATIBILITY_AUDIT`

### 1.1 冲突是如何被发现的

| 证据 | 内容 | 来源 |
| --- | --- | --- |
| **A** | `Hand  - Realistic`：`DISTAL = −Z`、**`DORSAL = +Y`**、`RADIAL = +X` | `docs/STAGE1C_C1_ASSET_QUALIFICATION_R1.md` §0 / §5 |
| **B** | `+X = RADIAL`、**`+Y = DORSAL`**、`+Z = DISTAL` | `docs/CANONICAL_HAND_POSE_SPEC_R1.md` §1.2 |

A 与 B 在字面上"一致"（都声称 dorsal = +Y），但二者**对同一资产给出互相矛盾的手性后果**：
只要 A 的三轴字面成立，该资产就是**左手**，而 C1 已判 `G-12 = 解剖学右手 = PASS`。必须闭合。

### 1.2 审计方法（纯数学 / 只读，未创建任何几何）

- 运行时：**`D:\Blender\blender.exe`（5.1.2）**；仅以 `-b` 后台打开官方母文件，**全程未 save / 未 apply Multires / 未生成 working mesh**；
- 母文件：`references/licenses/blender_human_base_meshes/extracted/.../human_base_meshes_bundle.blend`
  （SHA-256 `3c121505651140ceb4d69fd1d8923f7788ffadd81672f5be14845a5f2c75c137`，**byte-unchanged**）；
- 证据：`production_spec/stage0_r1_3_1_frame_audit/`（4 个只读脚本 + 4 份原始 JSON + 1 份结果 JSON）。

### 1.3 五个问题逐条作答

#### Q1 — C1 source orientation 的三轴判读是否全部正确？

**否。三轴中两轴正确、一轴（Y 轴）标签反转。**

| 轴 | C1 记录 | 判定 | 实测证据 |
| --- | --- | --- | --- |
| `DISTAL` | −Z | ✅ **正确** | 五个指尖簇位于 z = 0.149–0.188（全网格 z 最小端）；前臂平切端（唯一 ngon 盖面）位于 z = 0.4316 |
| `RADIAL` | +X | ✅ **正确** | 拇指远节区域实测 x_mean = 1.485，覆盖全网格 +X 极值 1.4986；四指核心区 x ∈ [1.354, 1.454] |
| `DORSAL` | +Y | ❌ **错误** | 实为 **−Y**（见下 5 条独立证据） |

**DORSAL 标签错误的 5 条独立证据：**

| # | 证据 | 读数 |
| --- | --- | --- |
| **1** | **指中心线**（网格连通性 Dijkstra，从指尖沿边图走到指根；index / middle / ring 三指） | 最远端 y **单调增加 +15 ~ 20 mm**（如 middle：0.0250 → 0.0076）。手指只能向**掌侧**屈曲 → **掌侧 = +Y** |
| **2** | **拇指位置** | 拇指区 y ∈ [0.0228, 0.0456]；其 y 最大值 0.0456 即**全手 y 最大值**所在（x = 1.4876）→ 拇指构成 **+Y 极值**。拇指属掌侧（鱼际）结构，不可能构成背侧极值 |
| **3** | **横向壳层极值** | −Y 侧最凸点在横断面**中央**（x = 1.410, y = −0.0053）= **掌骨拱 → 背侧**；+Y 侧极值在拇指 / 鱼际（x = 1.488）= **掌侧** |
| **4** | **第一指蹼（虎口）** | 过渡面位于 y ≈ +0.02 ~ +0.03，高于掌中平面（≈ +0.0125）→ 指蹼偏向 **+Y = 掌侧** |
| **5** | **C1 记录 G-12 自身的算式（自洽性反证）** | `D × T = (0,0,−1) × (+1,0,0) = (0,−1,0) = −Y`。右手判据要求 `D × R = 背面法向`，故 **−Y 必须是背面法向**；原句却把 −Y 写成"掌面法向" —— 若真是掌面法向，则按 `D × T = 掌侧` 应判**左手**，与本行"右手"结论直接矛盾 |

**原始记录反转位置**（仅记录、未改写历史）：C1 §0 视角约定、§5 视角约定、§5 掌/背侧判定依据一句、§5 `G-05` 一行、§5 `G-12` 一行；连带 `EVIDENCE_DORSAL_*` / `EVIDENCE_PALMAR_*` / `WIREFRAME_DORSAL` / `WIREFRAME_PALMAR` 的**解剖学命名语义互换**（相机位置描述本身正确）。

#### Q2 — Canonical Asset Frame 的三轴定义是否内部构成正确的右手坐标系？

**是。canonical 帧正确、无需修正。**

对右手：`cross(distal, radial) = dorsal`，等价于 `cross(radial, dorsal) = distal`。
canonical 的 (`X = RADIAL`, `Y = DORSAL`, `Z = DISTAL`) 恰满足 `X × Y = Z`
→ 该三轴定义**内部自洽**，且与 `RIGHT_HAND` 语义一致。

#### Q3 — 从 C1 source frame 映射到 canonical asset frame，是否存在一个 proper rotation（det = +1）即可完成的变换？

- **若三轴按 C1 字面记录取值（dorsal = +Y）：不存在。**
  要求把 `(radial, dorsal, distal) = (+X, +Y, −Z)` 映到 `(+X, +Y, +Z)`。
  `X → X` 与 `Y → Y` 已被锁定，线性性迫使 `Z → Z`，与 `Z → −Z` 矛盾；
  等价地该三标签基的行列式 `det = diag(1, 1, −1) = −1`（**improper**，内在手性为左手）。**只能靠负缩放 / 镜像 / 反射"解决" → 明令禁止。**
- **修正 Y 轴标签后（dorsal = −Y）：存在，且唯一。**

```
SOURCE_TO_CANONICAL_TRANSFORM = ROTATION_ONLY_COMPATIBLE

M (source → canonical) =
      ⎡ 1   0   0 ⎤
      ⎢ 0  −1   0 ⎥
      ⎣ 0   0  −1 ⎦
      = Rx(180°)     （绕桡侧轴 X 旋转 180°）

det(M) = +1      proper rotation
scale  = 1.0     归一化后
```

轴映射验证：

| 源轴（实测） | → | Canonical 目标轴 |
| --- | --- | --- |
| `+X`（RADIAL） | → | `+X` = RADIAL ✅ |
| `−Y`（DORSAL） | → | `+Y` = DORSAL ✅ |
| `−Z`（DISTAL） | → | `+Z` = DISTAL ✅ |

#### Q4 — 如果不能只靠 proper rotation，是哪一个方向标签 / 手性判断 / frame 定义产生冲突？

**是 `DORSAL`（连带 `PALMAR`）这一对 Y 轴解剖学标签。**

| 项 | 结论 |
| --- | --- |
| 冲突类别 | **`SOURCE_ORIENTATION_LABEL_ERROR`** |
| 错误标签 | `DORSAL = +Y`（连带 `PALMAR = −Y`） |
| 更正后 | **`DORSAL = −Y` / `PALMAR = +Y`** |
| **不是**冲突源 | canonical frame 定义（正确）、`RIGHT_HAND` 语义（正确）、`DISTAL`（正确）、`RADIAL`（正确）、资产本体手性（确为解剖学右手） |

#### Q5 — 是否使用了 negative scale / runtime mirror / reflection？

**否。三者均未使用，也未被允许。** 全部闭合在 proper rotation 内。

#### Q6 — `RIGHT_HAND` 语义是否被改变？

**未改变。** 更正后重新验证：

```
D = (0, 0, −1)        R = (+1, 0, 0)        DORSAL = (0, −1, 0)
(D × R) · DORSAL = (0,−1,0) · (0,−1,0) = +1   →  RIGHT HAND（与 C1 G-12 结论一致）
```

### 1.4 `SOURCE_TO_CANONICAL_TRANSFORM`（正式结论）

```
结论码  = B. SOURCE_ORIENTATION_LABEL_ERROR
          （已给出"哪一个 source label 错了"+ 5 条实测证据）
变换    = ROTATION_ONLY_COMPATIBLE
矩阵    = diag(1, −1, −1) = Rx(180°)
det     = +1（proper）    禁止负缩放 / 镜像 / 反射
scale   = 1（归一化后）    RIGHT_HAND 语义不变
```

### 1.5 本轮**未**做（审计合规声明）

- 🚫 未创建 working mesh；🚫 未应用 Multires；🚫 未修改 / 未写回官方 CC0 母文件（`BYTE-UNCHANGED`）；
- 🚫 未 re-pose / Retopo / Rig；🚫 未改任何顶点；🚫 未调用 Hunyuan3D；
- 🚫 未删除或重命名任何历史证据图；
- ✅ 审计为**纯数学 / 只读**：4 个 Python 脚本 + 4 份原始 JSON + 1 份结果 JSON。

---

## 2. `CON-9 = ASSET_FRAME_NORMALIZATION` 正式绑定 Stage 4

**仅修改规范，不修改 mesh。** 已在三处 authority 同步绑定：

1. `docs/CANONICAL_HAND_POSE_SPEC_R1.md` **§1.2.1**（新增，权威定义）
2. `docs/STAGE0_ROUTE_C_AMENDMENT_R1.md` **§13（+§13.1）**
3. `docs/PIANO_HAND_PRODUCTION_PIPELINE_R1.md` **Stage 4 · Route C 专项合同（新增 `CON-9` 行）**
4. `docs/PIANO_HAND_MASTER_ASSET_SPEC_R1.md` **§2.4.2**（绑定表新增 `CON-9` 行）
5. `reference_manifest/REFERENCE_MANIFEST_R1.json` → `c1_conditional_items_binding.CON-9`

### 2.1 `CON-9` 工程义务（逐条）

| # | 义务 | 状态 |
| --- | --- | --- |
| 1 | **source asset orientation 明确记录** | ✅ `DISTAL = −Z` / `RADIAL = +X` / `DORSAL = −Y` / `PALMAR = +Y` |
| 2 | **canonical target frame 明确记录** | ✅ `+X = RADIAL` / `+Y = DORSAL` / `+Z = DISTAL` |
| 3 | 使用**已批准的 proper transform** | ✅ `M = diag(1, −1, −1) = Rx(180°)` |
| 4 | 🚫 **禁止负缩放** | ✅ 明令禁止 |
| 5 | normalize 后 **`scale = 1`** | ✅ 强制 |
| 6 | **hand chirality 必须保持 `RIGHT`** | ✅ 强制 |
| 7 | **canonical frame validation 必须 `PASS`** | ✅ 强制（作为 Stage 4 出口条件） |
| 8 | 完成以上后**才允许 Rig** | ✅ 作为 Stage 4 → Stage 5 门禁 |

### 2.2 阶段边界（重申，避免 Stage 2 越界）

```
STAGE 2 BOOTSTRAP   = 只复制 source asset；🚫 不得修改 geometry
STAGE 4 ENGINEERING = CON-9 ASSET_FRAME_NORMALIZATION（本项属于此阶段）
```

---

## 3. 修正：Hunyuan fallback 中的 LowPoly 残留

**文件**：`docs/MULTIVIEW_REFERENCE_PACK_SPEC_R1.md` **§4.2**

| 项 | 修正前 | 修正后 |
| --- | --- | --- |
| `PolygonType` 行 | `` `quadrilateral`（若使用 LowPoly 模式） `` | **当前不设定**（`quadrilateral` 只对 `LowPoly` 模式有意义，而 `LowPoly` 在当前绑定接口下**不可用**） |
| 旧警示行 | "⚠ **不建议**首轮使用 `LowPoly`……" | 移入 **📜 FORMER / LEGACY** 区块 |

**当前事实（权威）**：

```
绑定接口            = SubmitHunyuanTo3DProJob（Version 2023-09-01，Model = 3.1）
LowPoly             = UNavailable for Model 3.1
Sketch              = 接口枚举仍存在，但本项目 PROHIBIT_SKETCH_FOR_THIS_EXPERIMENT
```

- 已**删除任何把 `LowPoly` 当作当前可用选项的有效语气**（含绑定 `quadrilateral` 的取值）；
- 历史说明**保留但明确标注** `FORMER / LEGACY`，并写明"**该前提已不成立，上述措辞整体失效，不得作为当前 fallback 参数建议**"。

```
HUNYUAN_LOW_POLY_STALE_RULE = RESOLVED
```

---

## 4. 修正：manifest 旧主流水线残留

**文件**：`reference_manifest/REFERENCE_MANIFEST_R1.json`

| 项 | 修正前 | 修正后 |
| --- | --- | --- |
| 字段名 | `amendment_unchanged`（**无历史标签**的 current field） | **`former_r1_1_amendment_unchanged`** |
| 元数据 | 无 | `former_revision = "R1_1"`<br>`NOT_CURRENT_AUTHORITY = true`<br>`superseded_by = "r1_3_scope / geometry_source_authority"`<br>`historical_note`（说明第 4 条语义已被 R1.3 取代） |
| 第 4 条 | `主流水线：Reference -> Hunyuan -> ...` | `［历史写法，已失效］主流水线：Reference -> Hunyuan -> ...（当前权威主流水线 = CC0 Authoritative Base Mesh -> Geometry Bootstrap -> Geometry Review -> Blender Engineering -> ...；Hunyuan 仅为 OPTIONAL_FALLBACK_EXPERIMENT）` |

- **历史未删除**（保留可审计），但已**明确历史字段 + `NOT_CURRENT_AUTHORITY = true`**；
- 确认：manifest 中**不再存在**任何**无历史标签的 current field** 声称 Hunyuan 是主流水线。

```
MANIFEST_OLD_MAIN_PIPELINE_FIELD = HISTORICIZED
```

---

## 5. 修正：流水线产出清单中的旧描述

**文件**：`docs/PIANO_HAND_PRODUCTION_PIPELINE_R1.md` **§6 产出清单 第 2 行**

| 项 | 修正前 | 修正后 |
| --- | --- | --- |
| `CANONICAL_HAND_POSE_SPEC_R1.md` 的描述 | "混元 3D 多视角生成的母版手姿态定义" | "**RSSF 母版手姿态 / 工程 re-pose / Rig neutral pose 定义**"（路线中立；Hunyuan 多视角只是 fallback 分支的用途之一） |

```
PIPELINE_CANONICAL_POSE_DESCRIPTION = RESOLVED
```

---

## 6. 本轮修改位置汇总（唯一写入清单）

### 6.1 既有文件（**5 份修改 / 2 份恢复原状**）

| # | 文件 | 修改内容 |
| --- | --- | --- |
| 1 | `docs/CANONICAL_HAND_POSE_SPEC_R1.md` | 新增 **§1.2.1 `SOURCE_ASSET_ORIENTATION` → `CANONICAL_ASSET_FRAME`**（更正后的源朝向 + 手性 + `SOURCE_TO_CANONICAL_TRANSFORM` + `CON-9` 指向） |
| 2 | `docs/STAGE0_ROUTE_C_AMENDMENT_R1.md` | §13 表新增 **`CON-9`** 行 + 新增 **§13.1 R1.3.1 追加记录（Asset Frame 闭合）**；§16 authority 块追加 4 个字段 |
| 3 | `docs/PIANO_HAND_PRODUCTION_PIPELINE_R1.md` | Stage 4 专项合同新增 **`CON-9`** 行；§6 第 2 行文案路线中立化；§6 新增第 15 行（本收口文档） |
| 4 | `docs/PIANO_HAND_MASTER_ASSET_SPEC_R1.md` | §2.4.2 绑定表新增 **`CON-9`** 行 + 说明 |
| 5 | `docs/MULTIVIEW_REFERENCE_PACK_SPEC_R1.md` | §4.2 `PolygonType` 行 + LowPoly / Sketch 段落（删除 LowPoly 当前有效性，历史标注 FORMER / LEGACY） |
| 6 | `docs/STAGE1C_C1_ASSET_QUALIFICATION_R1.md` | **`HISTORICAL_FILES_RESTORED_BYTEWISE / CONTENTWISE`** —— 本轮一度追加的更正框 / 更正标记 / 文末勘误章节**已全部撤回**，文件恢复至 R1.3.1 修改前状态（**30563 bytes，byte-exact**）。**现为未修改** |
| 7 | `production_spec/stage1c_c1_qualification/stats/GEOMETRY_ANATOMY_CHECK.md` | **`HISTORICAL_FILES_RESTORED_BYTEWISE / CONTENTWISE`** —— 同上，恢复后 **9208 bytes（byte-exact）**。**现为未修改** |

> ### `ERRATA_MOVED_TO_SIDECAR`
> 正式勘误**不再写入历史文件**，唯一载体为 sidecar：
> **`docs/STAGE1C_C1_ASSET_QUALIFICATION_R1_ERRATA.md`**（`ERRATA_ID = C1_Y_AXIS_ANATOMICAL_LABEL_REVERSAL`）
> 与本文档（R1.3.1 closure）。
>
> ```
> HISTORICAL_PROVENANCE_HYGIENE = PASS
> C1_HISTORY_IMMUTABLE          = YES
> C1_ERRATA_SIDECAR             = PRESENT
> ```

### 6.2 修改的数据文件（1）

| # | 文件 | 修改内容 |
| --- | --- | --- |
| 8 | `reference_manifest/REFERENCE_MANIFEST_R1.json` | ① `amendment_unchanged` → **`former_r1_1_amendment_unchanged`**（+ `former_revision` / `NOT_CURRENT_AUTHORITY` / `historical_note`）；② 新增 **`asset_frame_authority`** 块；③ `c1_conditional_items_binding` 新增 **`CON-9`**；④ `review_status` 追加 R1.3.1 字段。**JSON 解析校验通过** |

### 6.3 新增文件

| # | 路径 | 内容 |
| --- | --- | --- |
| 9 | `docs/STAGE0_ROUTE_C_R1_3_1_FINAL_CLOSURE.md` | 本文件 |
| 10 | `production_spec/stage0_r1_3_1_frame_audit/scripts/asset_frame_compatibility_audit.py` | 只读：全局朝向 / z 分层 / 横向壳层 / 极值点 |
| 11 | `production_spec/stage0_r1_3_1_frame_audit/scripts/finger_centreline_probe.py` | 只读：连通性 Dijkstra 指中心线 + 审计量 |
| 12 | `production_spec/stage0_r1_3_1_frame_audit/scripts/side_calibration_probe.py` | 只读：`.L`/`.R` 侧别标定 |
| 13 | `production_spec/stage0_r1_3_1_frame_audit/scripts/body_hand_orientation_probe.py` | 只读：body / skeleton 手部朝向一致性校验 |
| 14 | `production_spec/stage0_r1_3_1_frame_audit/scripts/authority_consistency_scan.py` | 只读：最终一致性扫描 |
| 15 | `production_spec/stage0_r1_3_1_frame_audit/raw/*.json`（4 份原始 + 1 份结果） | 审计原始证据与正式结论 |
| 16 | `docs/STAGE1C_C1_ASSET_QUALIFICATION_R1_ERRATA.md` | **勘误 sidecar**（`ERRATA_ID = C1_Y_AXIS_ANATOMICAL_LABEL_REVERSAL`）。历史 C1 文件保持 byte-unchanged；勘误唯一载体 |
| 17 | `production_spec/stage0_r1_3_1_frame_audit/scripts/restore_history.py` / `restore_history_fix.py` | 只读恢复脚本（记录 byte-exact 恢复过程，含 size 校验） |

### 6.4 未修改（明确）

- 🚫 **官方 CC0 母文件**（`human_base_meshes_bundle.blend`）**byte-unchanged**（SHA-256 复核一致）
- 🚫 **`docs/STAGE1C_C1_ASSET_QUALIFICATION_R1.md`** —— 恢复后**未修改**（30563 bytes，byte-exact）
- 🚫 **`production_spec/stage1c_c1_qualification/stats/GEOMETRY_ANATOMY_CHECK.md`** —— 恢复后**未修改**（9208 bytes，byte-exact）
- 🚫 **任何历史证据 PNG / 历史 JSON / 历史统计输出**（`renders/`、`wireframes/`、`stats/*.json` 等）—— 未删除、未重命名、未改内容
- 🚫 **Stage 1A / Stage 1B / Stage 1C 原始报告的其他内容** —— 未修改
- 🚫 任何历史报告（`PHASE1_R1_1_AMENDMENT_REPORT.md`、`PHASE1_R1_2_FINAL_CLOSURE.md`、`PHASE1_R1_2_1_CONSISTENCY_PATCH.md`、`BLENDER_RUNTIME_DISCOVERY_AUDIT_R1.md` 等）
- 🚫 `PIANO_HAND_PEDAGOGY_RESEARCH_R1.md`（教学文档，R1.1 / R1.2 / R1.3 / R1.3.1 均未动）
- 🚫 任何证据图（未删除、未重命名）
- 🚫 未创建 `stage2_bootstrap/`、未创建 working mesh

---

## 7. 当前 authority 一致性扫描（只读，扫描后不改）

**扫描对象（6）**：`STAGE0_ROUTE_C_AMENDMENT_R1.md`、`PIANO_HAND_PRODUCTION_PIPELINE_R1.md`、
`PIANO_HAND_MASTER_ASSET_SPEC_R1.md`、`MULTIVIEW_REFERENCE_PACK_SPEC_R1.md`、
`CANONICAL_HAND_POSE_SPEC_R1.md`、`REFERENCE_MANIFEST_R1.json`

**脚本**：`production_spec/stage0_r1_3_1_frame_audit/scripts/authority_consistency_scan.py`

### 7.1 必需字段

| 字段 | 期望值 | 结果 |
| --- | --- | --- |
| `GEOMETRY_SOURCE_PRIMARY` | `CC0_AUTHORED_BASE_MESH` | ✅ 一致（5 份文件） |
| `PROJECT_BLENDER_RUNTIME` | `D:\Blender\blender.exe` | ✅ 一致（5 份文件） |
| `ROUTE_C_SOURCE_GATE` | `PASS` | ✅ 一致（5 份文件） |
| `REFERENCE_ACQUISITION_GATE` | `CONDITIONAL_BRANCH_GATE_FOR_HUNYUAN_MULTIVIEW` | ✅ 一致（6 份文件） |
| `REAL_HUMAN_8VIEW_REFERENCE` | `OPTIONAL_NON_BLOCKING_FOR_ROUTE_C` | ✅ 一致（6 份文件） |
| `HUNYUAN3D_ROLE` | `OPTIONAL_FALLBACK_EXPERIMENT` | ✅ 一致（5 份文件） |
| `2D_IMAGEGEN_MULTIVIEW_ROUTE` | `REJECTED_BASELINE` | ✅ 一致（5 份文件） |
| `ASSET_FRAME_AUTHORITY` | `CONSISTENT` | ✅ **本轮新增，一致**（3 份文件） |
| `SOURCE_TO_CANONICAL_TRANSFORM` | `DEFINED` | ✅ **本轮新增，一致**（3 份文件） |
| `CON-9_ASSET_FRAME_NORMALIZATION` | `BOUND_TO_STAGE4` | ✅ **本轮新增**（定义处 `CANONICAL_HAND_POSE_SPEC_R1.md` §1.2.1；绑定处另见 amendment / pipeline / master spec / manifest） |

### 7.2 陈旧规则清扫

| 规则 | 期望 | 结果 |
| --- | --- | --- |
| LowPoly 被当作当前可用 | 0 | ✅ **0** |
| 无历史标签的 current「主流水线 = Reference → Hunyuan」 | 0 | ✅ **0**（唯一命中位于 `former_r1_1_amendment_unchanged` 内，已标注"［历史写法，已失效］"+ `NOT_CURRENT_AUTHORITY = true`） |
| 旧键 `amendment_unchanged`（作为现行字段） | 0 | ✅ **0** |
| `CANONICAL_HAND_POSE_SPEC` 被描述为"混元多视角母版姿态定义" | 0 | ✅ **0** |
| 在 canonical 规范中把 `背侧 +Y` 作为**当前**约定 | 0 | ✅ **0**（唯一命中为本轮**更正说明**中引用的旧文原文） |

### 7.3 数据结构校验

| 项 | 结果 |
| --- | --- |
| `REFERENCE_MANIFEST_R1.json` 解析 | ✅ OK（39 个顶层键） |
| `former_r1_1_amendment_unchanged.NOT_CURRENT_AUTHORITY` | ✅ `true` |
| `c1_conditional_items_binding.CON-9.stage` | ✅ `Stage 4` |
| `asset_frame_authority.SOURCE_TO_CANONICAL_TRANSFORM_DET` | ✅ `1` |

---

## 8. 最终状态

```
ASSET_FRAME_CONFLICT                = RESOLVED
SOURCE_TO_CANONICAL_TRANSFORM       = DEFINED
CON_9_ASSET_FRAME_NORMALIZATION     = BOUND_TO_STAGE4

HUNYUAN_LOW_POLY_STALE_RULE         = RESOLVED
MANIFEST_OLD_MAIN_PIPELINE_FIELD    = HISTORICIZED
PIPELINE_CANONICAL_POSE_DESCRIPTION = RESOLVED

CURRENT_AUTHORITY_CONSISTENCY       = PASS

HISTORICAL_PROVENANCE_HYGIENE       = PASS
C1_HISTORY_IMMUTABLE                = YES
C1_ERRATA_SIDECAR                   = PRESENT

STAGE0_ROUTE_C_R1_3_1               = PASS
STAGE0                              = REFROZEN

STAGE2                              = READY_TO_START_ROUTE_C_BOOTSTRAP
```

**附加字段（供下游引用）**：

```
ASSET_FRAME_CONFLICT_CLASS          = SOURCE_ORIENTATION_LABEL_ERROR   （错的是 DORSAL / PALMAR 的 Y 轴标签）
SOURCE_TO_CANONICAL_TRANSFORM_RESULT= ROTATION_ONLY_COMPATIBLE
SOURCE_TO_CANONICAL_TRANSFORM_MATRIX= diag(1, −1, −1)  = Rx(180°)
SOURCE_TO_CANONICAL_TRANSFORM_DET   = +1   （proper；无负缩放 / 无镜像 / 无反射）
HAND_CHIRALITY                      = RIGHT   （未改变）
OFFICIAL_MASTER_FILE                = BYTE_UNCHANGED
```

---

## 9. 停止条件确认

- 🚫 **未创建 working mesh**
- 🚫 **未进入 Stage 2**（本轮不执行 Stage 2 Bootstrap）
- 🚫 未修改官方 CC0 母文件（未 save、未 apply Multires）
- 🚫 未 re-pose / Retopo / Rig / 权重 / 动画
- 🚫 未调用 Hunyuan3D（`HUNYUAN3D_CALLED = NO`）
- 🚫 未进入 Three.js
- 🚫 未删除任何历史文件 / 证据图
- ✅ 已完成：① `ASSET_FRAME_COMPATIBILITY_AUDIT`（纯数学 / 只读）；② `CON-9` 绑定 Stage 4；③ LowPoly 残留清除；④ manifest 旧主流水线字段历史化；⑤ pipeline 文案路线中立化；⑥ 6 份 authority 只读一致性扫描；⑦ 本收口文档

**等待 Human Review。不自动开始 Stage 2。**

**文档状态：`READY_FOR_HUMAN_REVIEW`**
