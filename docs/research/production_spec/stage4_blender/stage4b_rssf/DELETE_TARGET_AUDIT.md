# DELETE_TARGET_AUDIT — 只读删除目标审计
## `STAGE4B_DELETE_TARGET_AUDIT_R1`

> 目录：`production_spec/stage4_blender/stage4b_rssf/`
> 模式：**READ_ONLY** —— 产出本审计的过程中**未删除任何文件**
> 机读版：`DELETE_TARGET_AUDIT.json`（含 126 项完整清单与逐项分类）
> 生成脚本：`scripts/stage4b_delete_audit.py`
> 日期：2026-09-28

---

## 0. 结论摘要

| 项 | 值 |
| --- | --- |
| `DELETE_TARGET_COUNT`（去重后路径数） | **26** |
| `DELETE_TARGET_ITEM_INSTANCES`（含重复出现次数） | **52** |
| 其中会命中**非临时**文件的 | **6**（见 §3 P0） |
| 纯临时目标 | **20**（`RSSF_BEF_*` / `RSSF_AFT_*` / `RSSF_BEFORE_*` / `RSSF_AFTER_*` 的单侧帧） |
| `FROZEN_BASELINE_COUNT` | **6** |
| `CURRENT_DELIVERABLE_COUNT` | **16** |
| `HISTORICAL_EVIDENCE_COUNT` | **94** |
| `CURRENT_TASK_TEMP_COUNT` | **10** |
| `UNKNOWN_COUNT` | **0** |
| 本次执行的动作 | 仅**新增** `DELETE_TARGET_AUDIT.{json,md}` 与 `_tmp/README.md`、创建 `_tmp/`；**未移动、未删除任何既有文件** |

> **关于"54"**：拒批那次命令的沙箱消息本身只列了 **5** 条被阻路径（`RSSF_BEF_*.png`），
> 而其通配符真实展开是 **10** 条。把本轮**全部**删除命令的通配展开相加得到
> **52 条 item-instances / 26 条去重路径**。审阅方工具计到 54，本轮无法精确复现该数字，
> 因此**附上 `stage4_blender` 全目录 126 个文件的逐项分类**（`DELETE_TARGET_AUDIT.json`
> 的 `inventory.files`），确保没有任何文件处于未分类状态。

---

## 1. 本轮全部删除事件（重构）

| # | 命令形态 | 状态 | 目标数 |
| --- | --- | --- | --- |
| 1 | `rm -f ".../renders"/*.png` | 已执行 | 6 |
| 2 | `rm -f ".../renders"/RSSF_BEF_*.png ".../renders"/RSSF_AFT_*.png` | 已执行 | 10 |
| 3 | `rm -f ".../renders"/RSSF_BEFORE_*.png ".../renders"/RSSF_AFTER_*.png` + 5 个显式 AFTER 文件 | 已执行 | 10 |
| 4 | 再次 `*.png` + `RSSF_BEF_*/RSSF_AFT_*`（最终渲染轮） | 已执行 | 16 |
| 5 | `rm -f ".../renders"/RSSF_BEF_*.png ".../renders"/RSSF_AFT_*.png` | **被用户阻断，未执行** | 10 |
|   | **合计** | | **52** |

事件 1 / 4 的目标是**上一轮的旧渲染**（调参前产物），删后已用最终 blend 重建 —— 属可接受。
事件 2 / 5 的目标是**纯临时帧** —— 属安全类。
**事件 3 造成了实际损失**（见 §3）。

---

## 2. 逐项分类

### 2.1 `CURRENT_TASK_TEMP`（本轮临时物 → 唯一可清理类别，20 条去重路径）

```
stage4b_rssf/renders/RSSF_BEF_DORSAL.png      stage4b_rssf/renders/RSSF_AFT_DORSAL.png
stage4b_rssf/renders/RSSF_BEF_PALMAR.png      stage4b_rssf/renders/RSSF_AFT_PALMAR.png
stage4b_rssf/renders/RSSF_BEF_RADIAL.png      stage4b_rssf/renders/RSSF_AFT_RADIAL.png
stage4b_rssf/renders/RSSF_BEF_OBLIQUE.png     stage4b_rssf/renders/RSSF_AFT_OBLIQUE.png
stage4b_rssf/renders/RSSF_BEF_CMC.png         stage4b_rssf/renders/RSSF_AFT_CMC.png
stage4b_rssf/renders/RSSF_BEFORE_DORSAL.png   stage4b_rssf/renders/RSSF_AFTER_DORSAL.png
stage4b_rssf/renders/RSSF_BEFORE_PALMAR.png   stage4b_rssf/renders/RSSF_AFTER_PALMAR.png
stage4b_rssf/renders/RSSF_BEFORE_RADIAL.png   stage4b_rssf/renders/RSSF_AFTER_RADIAL.png
stage4b_rssf/renders/RSSF_BEFORE_OBLIQUE.png  stage4b_rssf/renders/RSSF_AFTER_OBLIQUE.png
stage4b_rssf/renders/RSSF_BEFORE_CMC.png      stage4b_rssf/renders/RSSF_AFTER_CMC.png
```
* 性质：合成 BEFORE/AFTER 对比图用的**单侧帧**；两侧内容都已保存在对比图内部；
  可由 `scripts/stage4b_render.py` + `CAMS.json` 一条命令重建。
* 其中只有 10 条当前**实际存在**（`RSSF_BEF_*` / `RSSF_AFT_*`）；另外 10 条是事件 3 已删的旧命名帧。
* **本轮不做任何清理**，等 Human Review 指示。

### 2.2 `CURRENT_DELIVERABLE`（本轮交付物，16 条 —— 绝对不可删）

```
stage4b_rssf/RIGHT_HAND_ENGINEERING_STAGE4B_RSSF_R1.blend   ← Stage-4B 交付网格
stage4b_rssf/STAGE4B_RSSF_REPOSE_REPORT_R1.md
stage4b_rssf/RSSF_POSE_AUDIT.json            stage4b_rssf/TEMP_RIG_AUDIT.json
stage4b_rssf/TOPOLOGY_FREEZE_AUDIT.json      stage4b_rssf/TEMP_WEIGHT_AUDIT.json
stage4b_rssf/RSSF_DEFORM_CHECK.json          stage4b_rssf/RSSF_RUN.json
stage4b_rssf/CAMS.json
stage4b_rssf/renders/RSSF_BEFORE_AFTER_DORSAL.png
stage4b_rssf/renders/RSSF_BEFORE_AFTER_PALMAR.png
stage4b_rssf/renders/RSSF_BEFORE_AFTER_RADIAL.png
stage4b_rssf/renders/RSSF_BEFORE_AFTER_OBLIQUE.png
stage4b_rssf/renders/RSSF_CMC_CLOSEUP.png
stage4b_rssf/renders/RSSF_SKELETON_OVERLAY.png
stage4b_rssf/_tmp/README.md   （目录清单自带的约定文件；`inventory` 计数已排除 `_tmp/` 内容）
```
> 上列 16 条与审计 JSON 的 `CURRENT_DELIVERABLE_COUNT` 一致（`_tmp/README.md` 由 `_tmp/` 规则排除，
> 清单为 `stage4b_rssf/` 下 15 项 + 后加入的 1 项）。

### 2.3 `FROZEN_BASELINE`（6 条 —— 绝对不可删）

```
RIGHT_HAND_ENGINEERING_STAGE4A_R2.blend          ← Human Review 批准的 Stage-4A 冻结输入
RIGHT_HAND_ENGINEERING_STAGE4A_R2_BASE.blend     ← CON-1 完成 / CON-2 未施加的复现基线
RIGHT_HAND_ENGINEERING_STAGE4A.blend             ← legacy 基线（保留作 provenance）
RIGHT_HAND_ENGINEERING_STAGE4A_CMC_R1.blend      ← R1 轮工作副本（历史）
RIGHT_HAND_ENGINEERING_CANDIDATE_STAGE4A.blend   ← Stage-3 评审通过候选
stage4a_r2/RIGHT_HAND_ENGINEERING_STAGE4A_R2.blend ← 同上 Stage-4A 冻结输入的副本（逐字节相同）
```

### 2.4 `HISTORICAL_EVIDENCE`（94 条 —— 绝对不可删）

`stage4a/`（含 renders 9 张）、`stage4a_r1/`（含 renders 12 项）、`stage4a_r2/`、
`stage4a_t01/`（含 renders 4 张）四个已闭环评审轮次的报告 / 审计 JSON / 证据图，以及
`scripts/` 下全部 37 个 `.py`（可复现性脚本）。

### 2.5 `UNKNOWN`（0 条）

无未分类文件。

---

## 3. `P0_INCIDENT` — 已发生的真实损失（必须记录）

**事件 3 的通配符 `RSSF_BEFORE_*.png` 同时命中了交付图 `RSSF_BEFORE_AFTER_*.png`**，
导致 **4 张已完成的 Stage-4B 交付对比图被一并删除**：

```
stage4b_rssf/renders/RSSF_BEFORE_AFTER_DORSAL.png
stage4b_rssf/renders/RSSF_BEFORE_AFTER_PALMAR.png
stage4b_rssf/renders/RSSF_BEFORE_AFTER_RADIAL.png
stage4b_rssf/renders/RSSF_BEFORE_AFTER_OBLIQUE.png
```

* **恢复**：已用冻结基线 `RIGHT_HAND_ENGINEERING_STAGE4A_R2.blend` + RSSF blend + `CAMS.json`
  完整重建，四张图**现已存在于磁盘**且为最终版本。
* **根因**：临时帧与交付图**共用同一目录、同一前缀命名空间**，前缀通配符在语义上无法区分
  `RSSF_BEFORE_<VIEW>`（临时）与 `RSSF_BEFORE_AFTER_<VIEW>`（交付）。
* **本次审计同时暴露的第二处同类风险**：`RSSF_AFTER_*` 与任何未来可能出现的
  `RSSF_AFTER_<SOMETHING>_*` 交付名同样会冲突。
* **隔离方案**：见 §4。

---

## 4. 新约定：临时文件目录 `_tmp/`

已创建 `stage4b_rssf/_tmp/` 并写入 `_tmp/README.md`（约定全文）。要点：

1. **所有临时/中间产物一律写入 `_tmp/`**（单侧渲染帧、合成中间图、探针/试跑输出、临时 blend、调试 json）。
2. **不再使用批量删除**：禁止 `rm -f *`、`rm -f PREFIX_*`、按目录递归清理；
   删除只能"逐个文件、逐个批准"。
3. **交付物与临时文件必须分属不同目录**；且交付物文件名不得是任何临时文件名的前缀
   （正是 `RSSF_BEFORE_*` → `RSSF_BEFORE_AFTER_*` 这次踩的坑）。
4. 交付物只能新增或覆盖同名文件；任何"清理"动作须经 Human Review 明确批准。
5. `_tmp/` 可被安全清空而不影响任何交付物 —— 交付物必须能由
   `scripts/stage4b_rssf.py` + `scripts/stage4b_render.py` + `CAMS.json` 从冻结基线一键重建。

**本轮未执行迁移**：现有 10 个单侧帧仍留在 `renders/` 原处，**未移动、未删除**。

---

## 5. 请求 Human Review 指示的事项

1. 是否批准把现有 10 个单侧帧（`renders/RSSF_BEF_*.png`、`renders/RSSF_AFT_*.png`）
   **移动到 `_tmp/`**（移动，不删除）？还是保留原位？
2. 是否批准清空 `_tmp/`（当前仅含 `README.md`）？默认**不清理**。
3. 后续渲染是否统一改为"临时帧直接写 `_tmp/`、只把对比图写入 `renders/`"？—— 这是本审计建议的默认做法。

> 在收到明确批准之前，**不执行任何删除或移动**。
