# audits/pianovam_single_sample_right_hand_retarget_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 技术路线

原报告未单独概述路线；以下实现文件与原报告共同界定方法，不能由文件名推断算法成功：

- [acquire.py](../../src/legacy/audits/pianovam_single_sample_right_hand_retarget_r1/acquire.py)
- [finalize.py](../../src/legacy/audits/pianovam_single_sample_right_hand_retarget_r1/finalize.py)
- [inspect_source.py](../../src/legacy/audits/pianovam_single_sample_right_hand_retarget_r1/inspect_source.py)
- [preview_server.py](../../src/legacy/audits/pianovam_single_sample_right_hand_retarget_r1/preview_server.py)
- [render_motion.py](../../src/legacy/audits/pianovam_single_sample_right_hand_retarget_r1/render_motion.py)

## 测试结论

> **VERDICT = RETARGET_PIPELINE_NEEDS_WORK. STOP — HUMAN REVIEW.** A real seven-second physical-right PianoVAM sequence was successfully retargeted and rendered, but this result does not establish natural piano playing. Do not interpret it as RIGHT_HAND_BASELINE_FAIL or commercial motion approval.

出处：[REAL_PIANO_MOTION_RETARGET_R1_REPORT.md](../research/audits/pianovam_single_sample_right_hand_retarget_r1/REAL_PIANO_MOTION_RETARGET_R1_REPORT.md)

> | ZERO_RESTORE | PASS |

出处：[REAL_PIANO_MOTION_RETARGET_R1_REPORT.md](../research/audits/pianovam_single_sample_right_hand_retarget_r1/REAL_PIANO_MOTION_RETARGET_R1_REPORT.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 原报告与关键代码

- [audits/pianovam_single_sample_right_hand_retarget_r1/REAL_PIANO_MOTION_RETARGET_R1_REPORT.md](../research/audits/pianovam_single_sample_right_hand_retarget_r1/REAL_PIANO_MOTION_RETARGET_R1_REPORT.md)
- [audits/pianovam_single_sample_right_hand_retarget_r1/PIANOVAM_SINGLE_SAMPLE_ACQUISITION_R1_REPORT.md](../research/audits/pianovam_single_sample_right_hand_retarget_r1/PIANOVAM_SINGLE_SAMPLE_ACQUISITION_R1_REPORT.md)
- [audits/pianovam_single_sample_right_hand_retarget_r1/acquire.py](../../src/legacy/audits/pianovam_single_sample_right_hand_retarget_r1/acquire.py)
- [audits/pianovam_single_sample_right_hand_retarget_r1/finalize.py](../../src/legacy/audits/pianovam_single_sample_right_hand_retarget_r1/finalize.py)
- [audits/pianovam_single_sample_right_hand_retarget_r1/inspect_source.py](../../src/legacy/audits/pianovam_single_sample_right_hand_retarget_r1/inspect_source.py)
- [audits/pianovam_single_sample_right_hand_retarget_r1/preview_server.py](../../src/legacy/audits/pianovam_single_sample_right_hand_retarget_r1/preview_server.py)
- [audits/pianovam_single_sample_right_hand_retarget_r1/render_motion.py](../../src/legacy/audits/pianovam_single_sample_right_hand_retarget_r1/render_motion.py)
- [audits/pianovam_single_sample_right_hand_retarget_r1/retarget.py](../../src/legacy/audits/pianovam_single_sample_right_hand_retarget_r1/retarget.py)
- [audits/pianovam_single_sample_right_hand_retarget_r1/smooth_and_check.py](../../src/legacy/audits/pianovam_single_sample_right_hand_retarget_r1/smooth_and_check.py)

## 输入、输出与大型证据

该目录原始成员 1348 项；拟公开身份记录 9 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
