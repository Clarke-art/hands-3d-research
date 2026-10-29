# audits/targeted_thenar_opposition_weight_tuning_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 技术路线

> 本轮先做局部 weight tuning，再做一次局部 pose-corrective support，均未改 ZERO 静态 vertex positions。纯局部权重调节不足以完成这一产品修复，剩余路线应是**更有针对性的 pose-corrective support**；本轮小范围平滑型支持也不足以消除 L3，故停止微调，不新开研究线。该路线判断来自可见效果，不是对唯一数学根因的证明。

出处：[TARGETED_THENAR_OPPOSITION_WEIGHT_TUNING_R1_REPORT.md](../research/audits/targeted_thenar_opposition_weight_tuning_r1/TARGETED_THENAR_OPPOSITION_WEIGHT_TUNING_R1_REPORT.md)

> **STOP — HUMAN REVIEW。** 不继续 weight/geometry/corrective 微调，不自动进入后续路线，不做 production promotion 或 Stage6B final PASS。

出处：[TARGETED_THENAR_OPPOSITION_WEIGHT_TUNING_R1_REPORT.md](../research/audits/targeted_thenar_opposition_weight_tuning_r1/TARGETED_THENAR_OPPOSITION_WEIGHT_TUNING_R1_REPORT.md)

## 测试结论

> NaN / Inf = 0；collapsed face = 0；degenerate = 0；明显 self-intersection / penetration = 0；gross tearing = 0；gross contamination = 0；ZERO restore PASS。可见 gross 门不声称所有隐蔽数学 crossing 为零。局部硬折角是仍未通过的产品条件。

出处：[TARGETED_THENAR_OPPOSITION_WEIGHT_TUNING_R1_REPORT.md](../research/audits/targeted_thenar_opposition_weight_tuning_r1/TARGETED_THENAR_OPPOSITION_WEIGHT_TUNING_R1_REPORT.md)

> 机器安全 PASS 与产品 verdict VISIBLE_ISSUE_STILL_PRESENT 分开记录。没有 normal-dot、2127 edge、true-cap、隐藏 crossing census、大范围 Stage6A/Stage6B 资格流程或新 root-cause 研究。

出处：[TARGETED_THENAR_OPPOSITION_WEIGHT_TUNING_R1_REPORT.md](../research/audits/targeted_thenar_opposition_weight_tuning_r1/TARGETED_THENAR_OPPOSITION_WEIGHT_TUNING_R1_REPORT.md)

## 失败原因与证据边界

> 本轮先做局部 weight tuning，再做一次局部 pose-corrective support，均未改 ZERO 静态 vertex positions。纯局部权重调节不足以完成这一产品修复，剩余路线应是**更有针对性的 pose-corrective support**；本轮小范围平滑型支持也不足以消除 L3，故停止微调，不新开研究线。该路线判断来自可见效果，不是对唯一数学根因的证明。

出处：[TARGETED_THENAR_OPPOSITION_WEIGHT_TUNING_R1_REPORT.md](../research/audits/targeted_thenar_opposition_weight_tuning_r1/TARGETED_THENAR_OPPOSITION_WEIGHT_TUNING_R1_REPORT.md)

## 后续建议

> **STOP — HUMAN REVIEW。** 不继续 weight/geometry/corrective 微调，不自动进入后续路线，不做 production promotion 或 Stage6B final PASS。

出处：[TARGETED_THENAR_OPPOSITION_WEIGHT_TUNING_R1_REPORT.md](../research/audits/targeted_thenar_opposition_weight_tuning_r1/TARGETED_THENAR_OPPOSITION_WEIGHT_TUNING_R1_REPORT.md)

## 原报告与关键代码

- [audits/targeted_thenar_opposition_weight_tuning_r1/TARGETED_THENAR_OPPOSITION_WEIGHT_TUNING_R1_REPORT.md](../research/audits/targeted_thenar_opposition_weight_tuning_r1/TARGETED_THENAR_OPPOSITION_WEIGHT_TUNING_R1_REPORT.md)
- [audits/targeted_thenar_opposition_weight_tuning_r1/corrective_and_save.py](../../src/legacy/audits/targeted_thenar_opposition_weight_tuning_r1/corrective_and_save.py)
- [audits/targeted_thenar_opposition_weight_tuning_r1/deliver.py](../../src/legacy/audits/targeted_thenar_opposition_weight_tuning_r1/deliver.py)
- [audits/targeted_thenar_opposition_weight_tuning_r1/make_sheets.py](../../src/legacy/audits/targeted_thenar_opposition_weight_tuning_r1/make_sheets.py)
- [audits/targeted_thenar_opposition_weight_tuning_r1/shared.py](../../src/legacy/audits/targeted_thenar_opposition_weight_tuning_r1/shared.py)
- [audits/targeted_thenar_opposition_weight_tuning_r1/tune_preview.py](../../src/legacy/audits/targeted_thenar_opposition_weight_tuning_r1/tune_preview.py)

## 输入、输出与大型证据

该目录原始成员 89 项；拟公开身份记录 87 项。
- `audits/targeted_thenar_opposition_weight_tuning_r1/FINAL_DISPLAY_COORDINATES_R1.json` → `hands-research-r1-selected-008.zip` / `payload/audits/targeted_thenar_opposition_weight_tuning_r1/FINAL_DISPLAY_COORDINATES_R1.json`
- `audits/targeted_thenar_opposition_weight_tuning_r1/ITERATION_01_PREVIEW.json` → `hands-research-r1-selected-008.zip` / `payload/audits/targeted_thenar_opposition_weight_tuning_r1/ITERATION_01_PREVIEW.json`
- `audits/targeted_thenar_opposition_weight_tuning_r1/REVIEW_L3_SCREENSHOT_R1.png` → `hands-research-r1-selected-008.zip` / `payload/audits/targeted_thenar_opposition_weight_tuning_r1/REVIEW_L3_SCREENSHOT_R1.png`
- `audits/targeted_thenar_opposition_weight_tuning_r1/RIGHT_HAND_STAGE5B_PALMAR_THENAR_OPPOSITION_TUNED_CANDIDATE_R1.blend` → `hands-research-r1-selected-008.zip` / `payload/audits/targeted_thenar_opposition_weight_tuning_r1/RIGHT_HAND_STAGE5B_PALMAR_THENAR_OPPOSITION_TUNED_CANDIDATE_R1.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
