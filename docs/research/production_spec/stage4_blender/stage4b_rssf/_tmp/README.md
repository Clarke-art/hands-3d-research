# `_tmp/` — 本轮临时文件专用目录

**建立日期**：2026-09-28
**起因**：`STAGE4B_AUTO_RIG_RSSF_REPOSE_R1` 期间，一次 `rm -f .../renders/RSSF_BEFORE_*.png`
的批量删除把 **4 个已完成交付图**（`RSSF_BEFORE_AFTER_*.png`）一起删掉了 ——
因为"临时帧"与"交付图"共用同一目录、同一前缀命名空间，前缀通配符无法区分二者。
（已从冻结基线 + `CAMS.json` 完整重建；事件记录见 `../DELETE_TARGET_AUDIT.json` 的 `P0_INCIDENT`。）

## 规则（自本文件起生效）

1. **所有临时/中间产物一律写入本目录** `stage4b_rssf/_tmp/`，
   包括但不限于：单侧渲染帧、合成用中间图、探针/试跑输出、临时 blend、调试 json。
2. **不再使用批量删除**，尤其**禁止**任何形式的通配符删除
   （`rm -f *`、`rm -f PREFIX_*`、按目录递归清理）。删除只能是"逐个文件、逐个批准"。
3. **交付物必须与临时文件处于不同目录**。交付物留在 `stage4b_rssf/` 与 `stage4b_rssf/renders/`，
   且其文件名不得是任何临时文件名的前缀（避免 `A_*` 命中 `A_B_*`）。
4. 交付物只能**新增或覆盖同名文件**；任何"清理"动作都需 Human Review 明确批准后再执行。
5. 本目录内容即使被清理也不应影响任何交付物 —— 交付物必须能用
   `scripts/stage4b_rssf.py` + `scripts/stage4b_render.py` + `CAMS.json` 从冻结基线一键重建。

## 按新规则，后续应生成到这里的文件

* `RSSF_BEF_<VIEW>.png` / `RSSF_AFT_<VIEW>.png`（合成 BEFORE/AFTER 用的单侧帧）
* 探针、试跑、临时 audit 输出

> 说明：本轮已存在的 10 个单侧帧（`renders/RSSF_BEF_*.png`、`renders/RSSF_AFT_*.png`）
> 仍留在原处**未做任何移动或删除**，等待 Human Review 指示。

---

## 正式批准（Human Review，`STAGE4B_POST_INCIDENT_INTEGRITY_AUDIT`）

```
TEMP_RENDER_OUTPUT_DIR  = production_spec/stage4_blender/stage4b_rssf/_tmp/
FINAL_RENDER_OUTPUT_DIR = production_spec/stage4_blender/stage4b_rssf/renders/

现存 10 个 renders/RSSF_BEF_* 与 renders/RSSF_AFT_* : KEEP_IN_PLACE_UNTIL_HUMAN_REVIEW
_tmp/                                              : DO_NOT_CLEAR
```

**已落地为脚本护栏**（`scripts/stage4b_render.py`）：

- 单侧帧（`RSSF_BEF_*` / `RSSF_AFT_*`）**只**写 `_tmp/`，永不写 `renders/`；
- `renders/` 启用 **精确文件名白名单**（只允许 `RSSF_BEFORE_AFTER_*.png`、
  `RSSF_CMC_CLOSEUP.png`、`RSSF_SKELETON_OVERLAY.png`），其它名字一律硬拒；
  之所以用白名单而非前缀规则：前缀 `RSSF_BEFORE_*` 会命中交付物 `RSSF_BEFORE_AFTER_*`，
  **任何前缀规则都分不开这两个名字**（这正是本次 P0 事故的机制）；
- 新增 `pairs` 模式，一次完成"合成 → 只写交付图"，中间单侧帧不落到 `renders/`；
- `TEMP == FINAL`、或 `TEMP` 目录名为 `renders` → 硬拒；
- 脚本内**不存在任何删除动作**。

**禁止**（继续有效）：glob delete、recursive delete、prefix wildcard delete。
删除只能"逐个文件、逐个批准"。

标记文件：`_tmp/LEGACY_TEMP_LOCATION.json`（10 个旧单侧帧，仅标记，未移动未删除）。
审计记录：`../STAGE4B_POST_INCIDENT_INTEGRITY_AUDIT.md` / `.json`。

## `_tmp/` 下的子目录

* `post_incident_rebuild/` —— 事故后从冻结输入重建的 15 张证据图（用于像素级比对）
* `post_patch_check/` —— 用修补后脚本完整复现的 15 张图（验证隔离规则未改变任何像素）
* `r2/` —— `STAGE4B_RSSF_POSE_SEMANTIC_CORRECTION_R2` 的 10 张单侧帧
  （`RSSF_R2BEF_*` / `RSSF_R2AFT_*`），合成后只把 5 张交付图写入 `renders/RSSF_R2_*`。
  R2 交付名已显式加入 `scripts/stage4b_render.py` 的 `FINAL_ALLOWED` 白名单 ——
  **新增交付物必须逐个登记进白名单，护栏不得被放宽成模式匹配**。

