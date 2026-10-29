# PIANO_HAND_PHASE1 · R1.2.1 一致性补丁

> `docs/PHASE1_R1_2_1_CONSISTENCY_PATCH.md`
> 项目：钢琴教学双手 3D 交互资产 · 第一阶段
> 版本：**R1.2.1（一致性补丁）**　基准：R1 / R1.1 / R1.2　日期：2026-09-27
> 性质：**极窄一致性补丁** —— 不是新阶段、不是重新研究、不是重新设计

---

## 0. 补丁边界

| 项 | 说明 |
| --- | --- |
| **唯一目标** | 消除 R1.2 最终文件之间残留的旧字段与旧措辞，使冻结后的 Stage 0 内部完全一致 |
| **✅ 做了** | 3 处残留冲突修复 + 2 处状态覆盖补齐 + 只读一致性扫描 |
| **🚫 没做** | 未进入 Stage 1、未采集图片、未调用 Hunyuan3D、未创建 mesh、未启动 Blender、未制作 Rig / Animation / Three.js |
| **未改变** | 任何已批准的技术决策；所有 `ViewType` 映射；教学研究实质内容 |
| **未修改** | `docs/PIANO_HAND_PEDAGOGY_RESEARCH_R1.md`（教学研究正文**未动**，仍作为 Stage 0 冻结依据） |

---

## 1. 发现的 3 个残留冲突

| # | 冲突 | 位置 | 性质 |
| --- | --- | --- | --- |
| **C-1** | 8 视图状态冲突：仍称"前六个强制、后两个强烈建议" | `CANONICAL_HAND_POSE_SPEC_R1.md` §4 | 与 `MULTIVIEW_FIRST_PASS = 8_VIEWS` 冲突 |
| **C-2** | `REFERENCE_GAP-02` 残留旧字段：`impact` / `blocks` 仍写"阻塞 Stage 1" | `REFERENCE_MANIFEST_R1.json` → `gaps[]` → `REFERENCE_GAP-02` | 与 `REFERENCE_SOURCE_TO_BE_ACQUIRED_IN_STAGE1` 冲突 |
| **C-3** | `HR-07` 残留 R1.1 旧光照风险：仍提"光源随动" | `REFERENCE_MANIFEST_R1.json` → `human_review_items[]` → `HR-07.residual_risk` | 与 `HAND_FIXED_LIGHT_FIXED_CAMERA_MOVES` 冲突 |

---

## 2. 冲突 C-1：CANONICAL_HAND_POSE_SPEC 的 8 视图状态

### 2.1 原位置

`docs/CANONICAL_HAND_POSE_SPEC_R1.md` §4「必须提供的参考角度（多视角）」

**原文（冲突）**：
```
**必须**提供以下视角。前六个为**强制**，后两个为**强烈建议**：

| # | 视角代号 | ... | 强制 |
| 7 | DORSAL_OBLIQUE_RADIAL | ... | 建议 |
| 8 | DORSAL_OBLIQUE_ULNAR | ... | 建议 |
```

### 2.2 为什么是冲突

R1.2 已冻结 `MULTIVIEW_FIRST_PASS = 8_VIEWS`：全部 8 个视角地位完全相同、全部为 MANDATORY。
§4 仍保留"前六强制 + 后二建议"的 R1 层级结构，与冻结规则直接矛盾——
若照 §4 执行，Stage 2 首轮可能只交 6 视图。

### 2.3 修复内容

| 项 | 修复 |
| --- | --- |
| **引导语** | 改为："🔒 必须提供**完整 8 视图**，**8 个视角全部为强制**" |
| **删除的旧措辞** | ~~"前六个强制、后两个强烈建议"~~ · ~~"强烈建议"~~ · ~~"建议视角"~~ · ~~"补充视角"~~（以删除线标注并归入已删除清单） |
| **表格最后一列** | 统一为 **`✅ REQUIRED`**（8 行全部一致） |
| **新增** | `ViewType` 映射重申表（**映射未改变**，仅重申）+ "不得无故删除 top / bottom / left_front / right_front" |
| **补充** | 视角存在理由新增第 7、8 视角条目，明确"与其余 6 个视角同为强制" |

### 2.4 结果

> ✅ **`CANONICAL_8_VIEW_STATUS_CONFLICT` = RESOLVED**
> `ViewType` 映射**未改变**。

---

## 3. 冲突 C-2：REFERENCE_MANIFEST 中 GAP-02 的旧字段

### 3.1 原位置

`reference_manifest/REFERENCE_MANIFEST_R1.json` → `gaps[]` → `REFERENCE_GAP-02`

**原文（冲突）**：
```json
"impact": "阻塞 Stage 1（参考图采集）。",
"blocks": ["Stage 1", "Stage 2"]
```

同一对象内已正确声明 `does_not_block: ["Stage 0 完成", "Phase 1 冻结", "Stage 1 启动"]`
与 `must_block: ["Stage 1 -> Stage 2"]` —— 但 `impact` / `blocks` 仍是旧值，自相矛盾。

### 3.2 修复内容

| 字段 | 修复后 |
| --- | --- |
| **`impact`** | `Stage 1 中需要实际获得并验证参考图包；在 REFERENCE_ACQUISITION_GATE PASS 前阻塞 Stage 2。` |
| **`blocks`** | `["Stage 1 -> Stage 2 transition"]` |
| **新增 `current_state`** | 显式声明 `formal_definition` / `does_not_block` / `must_block` / `reference_gap_02_does_not_block_stage1: "YES"` / `enforced_by` |
| **新增 `FORMER_R1`** | 归档旧 `impact` 与旧 `blocks`，**标注"不得作为当前状态引用"** |
| **新增 `FORMER_R1_1`** | 归档 R1.1 历史说明，同样标注 |
| **新增 `r1_2_1_update`** | 记录本次修复 |

### 3.3 结果

> ✅ **`REFERENCE_GAP_02_STALE_FIELDS` = RESOLVED**
>
> 当前状态中**不再出现**任何"`REFERENCE_GAP-02` 阻塞 Stage 1 启动"的字段。
> 旧值已归档至 `FORMER_R1` / `FORMER_R1_1`，并明确标记为历史记录，**不与 current state 混淆**。

---

## 4. 冲突 C-3：REFERENCE_MANIFEST 中 HR-07 的旧光照风险

### 4.1 原位置

`reference_manifest/REFERENCE_MANIFEST_R1.json` → `human_review_items[]` → `HR-07.residual_risk`

**原文（冲突，R1.1 旧逻辑）**：
```
"RK-14 相机移动破坏光照一致性（约束 MV-02：光源随动或环绕柔光；优先多相机同步）"
```

R1.2 已正式废弃 `LIGHT FOLLOWS CAMERA`；"光源随动"不得再作为当前建议出现。

### 4.2 修复内容

| 字段 | 修复后 |
| --- | --- |
| **`residual_risk`** | `多视角采集期间光照环境发生变化的风险。缓解：固定室内环境 + 固定环绕柔光 / 柔光帐 / 大面积漫射光；8 视图期间灯位、方向、强度、色温与柔光环境保持不变；避免自然光作为主光源。LIGHT MUST NOT FOLLOW CAMERA。` |
| **`decision`** | 补全为 `HAND = FIXED / LIGHT = FIXED / CAMERA = MOVES`；并澄清多相机同步"价值在于减少时间漂移，不是让光源跟随相机" |
| **新增 `lighting_rule`** | `HAND_FIXED_LIGHT_FIXED_CAMERA_MOVES` |
| **新增 `light_must_not_follow_camera`** | `true` |
| **新增 `FORMER_R1_1_deprecated`** | 归档旧文本，标注"已废弃，不得作为当前建议引用" |

### 4.3 结果

> ✅ **`HR_07_STALE_LIGHTING_RULE` = RESOLVED**
>
> 当前状态明确：`LIGHT MUST NOT FOLLOW CAMERA`。
> "光源随相机同步移动" / "光源随动" 仅存在于 `FORMER_R1_1_deprecated`（历史归档）与文档中的"已废弃"标记处，
> **不再作为当前建议**。

---

## 5. 附带补齐：状态覆盖（非冲突，一致性增强）

只读扫描发现两份规范文件未完整声明冻结事实（属**覆盖缺口**，不是冲突）：

| 文件 | 缺口 |
| --- | --- |
| `CANONICAL_HAND_POSE_SPEC_R1.md` | 未声明 `GATE_1` / `STAGE1` / `REFERENCE_ACQUISITION_GATE` / `STAGE2` |
| `PIANO_HAND_MASTER_ASSET_SPEC_R1.md` | 未声明 `LIGHTING_RULE` / `GATE_1` |

**修复**：各新增一节「当前权威状态（R1.2.1 对齐）」，以表格声明 10 项冻结事实。
**明确标注**：该节仅为状态声明，**不改变任何已批准的技术决策**。

---

## 6. 一致性扫描结果

### 6.1 扫描范围（只读）

| # | 文件 |
| --- | --- |
| 1 | `docs/CANONICAL_HAND_POSE_SPEC_R1.md` |
| 2 | `docs/MULTIVIEW_REFERENCE_PACK_SPEC_R1.md` |
| 3 | `docs/PIANO_HAND_MASTER_ASSET_SPEC_R1.md` |
| 4 | `docs/PIANO_HAND_PRODUCTION_PIPELINE_R1.md` |
| 5 | `reference_manifest/REFERENCE_MANIFEST_R1.json` |
| 6 | `docs/PHASE1_R1_2_FINAL_CLOSURE.md` |

> 历史修订报告 `docs/PHASE1_R1_1_AMENDMENT_REPORT.md` **不在扫描范围内**——它是历史记录，
> 允许记载旧状态，**未做篡改**。

### 6.2 冻结事实覆盖矩阵（修复后）

| 文件 | 8_VIEWS | ALL_8_REQ | LIGHTING | GAP02_DEF | ACQ_GATE | GATE_1 | STAGE0 | STAGE1 | STAGE2 |
| --- | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| CANONICAL_HAND_POSE_SPEC | 4 | 13 | 5 | 1 | 2 | 1 | 5 | 2 | 1 |
| MULTIVIEW_REFERENCE_PACK | 18 | 2 | 39 | 3 | 4 | 1 | 1 | 1 | 1 |
| MASTER_ASSET_SPEC | 6 | 6 | 1 | 1 | 5 | 1 | 4 | 2 | 2 |
| PRODUCTION_PIPELINE | 13 | 2 | 14 | 2 | 13 | 9 | 10 | 4 | 4 |
| R1_2_FINAL_CLOSURE | 10 | 2 | 16 | 2 | 8 | 5 | 7 | 2 | 1 |
| REFERENCE_MANIFEST | 11 | 3 | 12 | 6 | 12 | 6 | 8 | 5 | 2 |

**结论：6 份文件对 9 项冻结事实全部有覆盖，无非零缺失。**

### 6.3 旧规则残留检查

| 检查项 | 结果 |
| --- | --- |
| "前六个强制 / 强烈建议 / 建议视角 / 补充视角" 作为**当前有效规则** | ✅ **无**。仅存在于"已删除"清单（删除线标注） |
| "光源随相机同步移动 / 光源随动" 作为**当前建议** | ✅ **无**。仅存在于"已废弃"标记与 `FORMER_R1_1_deprecated` 历史归档 |
| "`REFERENCE_GAP-02` 阻塞 Stage 1 启动" 作为**当前状态字段** | ✅ **无**。旧值已归档至 `FORMER_R1` / `FORMER_R1_1` |
| "base64 编码后总量 ≤ 6 MB" | ✅ **无**（R1.2 已更正） |
| "首轮只提交 6 个" | ✅ **无** |

### 6.4 判定

> ✅ **`CURRENT_AUTHORITY_CONSISTENCY` = PASS**

---

## 7. 当前权威状态（修复后统一）

| 冻结事实 | 值 |
| --- | --- |
| `MULTIVIEW_FIRST_PASS` | **`8_VIEWS`** |
| `ALL_8_VIEWS` | **`REQUIRED`**（8 个视角地位相同，全部强制） |
| `LIGHTING_RULE` | **`HAND_FIXED_LIGHT_FIXED_CAMERA_MOVES`** |
| `IMAGE_SIZE_RULE` | **`RAW_APPROX_6MB` / `BASE64_ENCODED_MAX_8MB`** |
| `REFERENCE_GAP_02` | **`REFERENCE_SOURCE_TO_BE_ACQUIRED_IN_STAGE1`** |
| `REFERENCE_GAP_02_DOES_NOT_BLOCK_STAGE1` | **`YES`** |
| `REFERENCE_ACQUISITION_GATE` | **`REQUIRED_BETWEEN_STAGE1_AND_STAGE2`** |
| `GATE_1` | **`PASS`** |
| `STAGE0` | **`FROZEN`** |
| `STAGE1` | **`READY_TO_START`** |
| `STAGE2` | **`BLOCKED_UNTIL_REFERENCE_ACQUISITION_GATE_PASS`** |

### 8 视图 ViewType 映射（未改变）

| # | 视角 | `ViewType` |
| --- | --- | --- |
| 1 | DORSAL | `front` ⭐ 必填 |
| 2 | PALMAR | `back` |
| 3 | RADIAL | `right` |
| 4 | ULNAR | `left` |
| 5 | DISTAL | `top` |
| 6 | PROXIMAL | `bottom` |
| 7 | DORSAL_OBLIQUE_RADIAL | `right_front` |
| 8 | DORSAL_OBLIQUE_ULNAR | `left_front` |

---

## 8. 最终状态输出

```
CANONICAL_8_VIEW_STATUS_CONFLICT   = RESOLVED

REFERENCE_GAP_02_STALE_FIELDS      = RESOLVED

HR_07_STALE_LIGHTING_RULE          = RESOLVED

CURRENT_AUTHORITY_CONSISTENCY      = PASS

PIANO_HAND_PHASE1_R1_2_1           = PASS

STAGE0                             = FROZEN

GATE_1                             = PASS

STAGE1                             = READY_TO_START

STAGE2                             = BLOCKED_UNTIL_REFERENCE_ACQUISITION_GATE_PASS
```

---

## 9. 停止条件

**R1.2.1 一致性补丁完成，立即停止。**

本轮**未**进行且**不得**进行：

- 🚫 进入 Stage 1
- 🚫 采集或下载图片
- 🚫 调用 Hunyuan3D
- 🚫 创建 mesh
- 🚫 启动 Blender
- 🚫 制作 Rig / Animation
- 🚫 进行 Three.js 开发
- 🚫 修改教学研究实质内容

**等待 Human Review。不要自动进入 Stage 1。**
