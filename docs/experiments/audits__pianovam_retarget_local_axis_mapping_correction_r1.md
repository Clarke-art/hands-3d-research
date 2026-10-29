# audits/pianovam_retarget_local_axis_mapping_correction_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 技术路线

原报告未单独概述路线；以下实现文件与原报告共同界定方法，不能由文件名推断算法成功：

- [dry_run.py](../../src/legacy/audits/pianovam_retarget_local_axis_mapping_correction_r1/dry_run.py)
- [finalize.py](../../src/legacy/audits/pianovam_retarget_local_axis_mapping_correction_r1/finalize.py)
- [full_retarget.py](../../src/legacy/audits/pianovam_retarget_local_axis_mapping_correction_r1/full_retarget.py)
- [mapping_core.py](../../src/legacy/audits/pianovam_retarget_local_axis_mapping_correction_r1/mapping_core.py)
- [render_old_matched.py](../../src/legacy/audits/pianovam_retarget_local_axis_mapping_correction_r1/render_old_matched.py)

## 测试结论

> **PRIMARY_CAUSE_CLASSIFICATION = RETARGET_AXIS_MAPPING_PARTIAL_CAUSE. STOP — HUMAN REVIEW.** Second mapping iteration significantly reduces the selected first-web triangular inward folds and makes the hinge chains more coherent, but residual creases and fast fingertip bends remain. Product validation is not accepted automatically.

出处：[PIANOVAM_RETARGET_LOCAL_AXIS_MAPPING_CORRECTION_R1_REPORT.md](../research/audits/pianovam_retarget_local_axis_mapping_correction_r1/PIANOVAM_RETARGET_LOCAL_AXIS_MAPPING_CORRECTION_R1_REPORT.md)

> Thumb CMC is separate: a palm-normal anchored thumb-base frame and CMC→MCP direction, with MCP→IP plane diagnostics. No noisy thumb-plane axial twist is copied; rest roll remains calibrated. Thumb MCP/IP use their own anchored hinge plane and calibrated local axes. Iteration1's wrist→CMC structural neutral reference over-adducted the thumb and failed its dry-run screen. Iteration2 uses the median normalized CMC→MCP stance from the **same421-observation window** as source-rest calibration. It changes no source coordinates, time window or angle limit. This estimated stance-to-RSSF calibration should be reviewed as a retarget convention, not an anatomical assertion.

出处：[PIANOVAM_RETARGET_LOCAL_AXIS_MAPPING_CORRECTION_R1_REPORT.md](../research/audits/pianovam_retarget_local_axis_mapping_correction_r1/PIANOVAM_RETARGET_LOCAL_AXIS_MAPPING_CORRECTION_R1_REPORT.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 原报告与关键代码

- [audits/pianovam_retarget_local_axis_mapping_correction_r1/PIANOVAM_RETARGET_LOCAL_AXIS_MAPPING_CORRECTION_R1_REPORT.md](../research/audits/pianovam_retarget_local_axis_mapping_correction_r1/PIANOVAM_RETARGET_LOCAL_AXIS_MAPPING_CORRECTION_R1_REPORT.md)
- [audits/pianovam_retarget_local_axis_mapping_correction_r1/dry_run.py](../../src/legacy/audits/pianovam_retarget_local_axis_mapping_correction_r1/dry_run.py)
- [audits/pianovam_retarget_local_axis_mapping_correction_r1/finalize.py](../../src/legacy/audits/pianovam_retarget_local_axis_mapping_correction_r1/finalize.py)
- [audits/pianovam_retarget_local_axis_mapping_correction_r1/full_retarget.py](../../src/legacy/audits/pianovam_retarget_local_axis_mapping_correction_r1/full_retarget.py)
- [audits/pianovam_retarget_local_axis_mapping_correction_r1/mapping_core.py](../../src/legacy/audits/pianovam_retarget_local_axis_mapping_correction_r1/mapping_core.py)
- [audits/pianovam_retarget_local_axis_mapping_correction_r1/render_old_matched.py](../../src/legacy/audits/pianovam_retarget_local_axis_mapping_correction_r1/render_old_matched.py)
- [audits/pianovam_retarget_local_axis_mapping_correction_r1/verify_saved.py](../../src/legacy/audits/pianovam_retarget_local_axis_mapping_correction_r1/verify_saved.py)

## 输入、输出与大型证据

该目录原始成员 574 项；拟公开身份记录 7 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
