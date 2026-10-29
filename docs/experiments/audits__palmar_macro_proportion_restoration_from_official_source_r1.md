# audits/palmar_macro_proportion_restoration_from_official_source_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 技术路线

原报告未单独概述路线；以下实现文件与原报告共同界定方法，不能由文件名推断算法成功：

- [deliver.py](../../src/legacy/audits/palmar_macro_proportion_restoration_from_official_source_r1/deliver.py)
- [make_sheets.py](../../src/legacy/audits/palmar_macro_proportion_restoration_from_official_source_r1/make_sheets.py)
- [run_iteration.py](../../src/legacy/audits/palmar_macro_proportion_restoration_from_official_source_r1/run_iteration.py)
- [save_and_render_static.py](../../src/legacy/audits/palmar_macro_proportion_restoration_from_official_source_r1/save_and_render_static.py)
- [shared.py](../../src/legacy/audits/palmar_macro_proportion_restoration_from_official_source_r1/shared.py)

## 测试结论

> 结论：**STATIC_PALM_SHAPE_STILL_INSUFFICIENT**。本轮 5 个静态 design iterations 均未达到“正常比例的手掌”。保存第 2 版作为相对平稳的失败设计候选供 Human 审阅；不申请成功验收，不用 BETTER 代替 CORRECT。

出处：[PALMAR_MACRO_PROPORTION_RESTORATION_FROM_OFFICIAL_SOURCE_R1_REPORT.md](../research/audits/palmar_macro_proportion_restoration_from_official_source_r1/PALMAR_MACRO_PROPORTION_RESTORATION_FROM_OFFICIAL_SOURCE_R1_REPORT.md)

> 自动最低数值检查：NaN/Inf=0、collapsed faces=0、degenerate edges=0、ZERO restore=PASS。普通 solid screen 未见明显穿透或撕裂；**new hard contour=1，所以整体 MACHINE_SAFETY=FAIL_VISIBLE_HARD_CONTOUR**。数值通过不抵消产品外形失败。没有 hidden crossing census、normal-dot、strain 或动态审计。

出处：[PALMAR_MACRO_PROPORTION_RESTORATION_FROM_OFFICIAL_SOURCE_R1_REPORT.md](../research/audits/palmar_macro_proportion_restoration_from_official_source_r1/PALMAR_MACRO_PROPORTION_RESTORATION_FROM_OFFICIAL_SOURCE_R1_REPORT.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

> 本轮已达到 5 版上限。最终候选与 review 页面供 Human 判断失败位置和下一步范围。没有运行 FULL_OPP_L1/L2/L3，未调 weights / rig，未跑 Stage6B final、左手镜像、motion retarget 或 production promotion。正式资产哈希保持。

出处：[PALMAR_MACRO_PROPORTION_RESTORATION_FROM_OFFICIAL_SOURCE_R1_REPORT.md](../research/audits/palmar_macro_proportion_restoration_from_official_source_r1/PALMAR_MACRO_PROPORTION_RESTORATION_FROM_OFFICIAL_SOURCE_R1_REPORT.md)

## 原报告与关键代码

- [audits/palmar_macro_proportion_restoration_from_official_source_r1/PALMAR_MACRO_PROPORTION_RESTORATION_FROM_OFFICIAL_SOURCE_R1_REPORT.md](../research/audits/palmar_macro_proportion_restoration_from_official_source_r1/PALMAR_MACRO_PROPORTION_RESTORATION_FROM_OFFICIAL_SOURCE_R1_REPORT.md)
- [audits/palmar_macro_proportion_restoration_from_official_source_r1/deliver.py](../../src/legacy/audits/palmar_macro_proportion_restoration_from_official_source_r1/deliver.py)
- [audits/palmar_macro_proportion_restoration_from_official_source_r1/make_sheets.py](../../src/legacy/audits/palmar_macro_proportion_restoration_from_official_source_r1/make_sheets.py)
- [audits/palmar_macro_proportion_restoration_from_official_source_r1/run_iteration.py](../../src/legacy/audits/palmar_macro_proportion_restoration_from_official_source_r1/run_iteration.py)
- [audits/palmar_macro_proportion_restoration_from_official_source_r1/save_and_render_static.py](../../src/legacy/audits/palmar_macro_proportion_restoration_from_official_source_r1/save_and_render_static.py)
- [audits/palmar_macro_proportion_restoration_from_official_source_r1/shared.py](../../src/legacy/audits/palmar_macro_proportion_restoration_from_official_source_r1/shared.py)

## 输入、输出与大型证据

该目录原始成员 157 项；拟公开身份记录 155 项。
- `audits/palmar_macro_proportion_restoration_from_official_source_r1/FINAL_DISPLAY_COORDINATES_R1.json` → `hands-research-r1-selected-006.zip` / `payload/audits/palmar_macro_proportion_restoration_from_official_source_r1/FINAL_DISPLAY_COORDINATES_R1.json`
- `audits/palmar_macro_proportion_restoration_from_official_source_r1/FINAL_SENTINELS_sheet.png` → `hands-research-r1-selected-006.zip` / `payload/audits/palmar_macro_proportion_restoration_from_official_source_r1/FINAL_SENTINELS_sheet.png`
- `audits/palmar_macro_proportion_restoration_from_official_source_r1/ITERATION_01_GEOMETRY.json` → `hands-research-r1-selected-006.zip` / `payload/audits/palmar_macro_proportion_restoration_from_official_source_r1/ITERATION_01_GEOMETRY.json`
- `audits/palmar_macro_proportion_restoration_from_official_source_r1/ITERATION_01_main_sheet.png` → `hands-research-r1-selected-006.zip` / `payload/audits/palmar_macro_proportion_restoration_from_official_source_r1/ITERATION_01_main_sheet.png`
- `audits/palmar_macro_proportion_restoration_from_official_source_r1/ITERATION_01_other_sheet.png` → `hands-research-r1-selected-006.zip` / `payload/audits/palmar_macro_proportion_restoration_from_official_source_r1/ITERATION_01_other_sheet.png`
- `audits/palmar_macro_proportion_restoration_from_official_source_r1/RIGHT_HAND_STAGE5B_PALMAR_MACRO_RESTORATION_CANDIDATE_R1.blend` → `hands-research-r1-selected-006.zip` / `payload/audits/palmar_macro_proportion_restoration_from_official_source_r1/RIGHT_HAND_STAGE5B_PALMAR_MACRO_RESTORATION_CANDIDATE_R1.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
