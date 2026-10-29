# audits/palmar_digit_root_local_donor_shape_restoration_feasibility_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> Source本身有自然root crease，目标不是smooth flat surface。Matched静态图中probe去掉current的异常局部shelf，保留attachment、掌面体积与source-like transition。write-incident native dihedral平均值约57.29°→16.68°、最大178.18°→49.60°；source native对应patch均值约15.70°、最大39.82°。这些是不同topology的描述量，不是产品或人体阈值。原生截面显示current折返/shelf消失，probe向donor progression恢复。

出处：[PALMAR_DIGIT_ROOT_LOCAL_DONOR_SHAPE_RESTORATION_FEASIBILITY_R1_REPORT.md](../research/audits/palmar_digit_root_local_donor_shape_restoration_feasibility_r1/PALMAR_DIGIT_ROOT_LOCAL_DONOR_SHAPE_RESTORATION_FEASIBILITY_R1_REPORT.md)

## 技术路线

原报告未单独概述路线；以下实现文件与原报告共同界定方法，不能由文件名推断算法成功：

- [common.py](../../src/legacy/audits/palmar_digit_root_local_donor_shape_restoration_feasibility_r1/common.py)
- [deliver.py](../../src/legacy/audits/palmar_digit_root_local_donor_shape_restoration_feasibility_r1/deliver.py)
- [metrics_and_sections.py](../../src/legacy/audits/palmar_digit_root_local_donor_shape_restoration_feasibility_r1/metrics_and_sections.py)
- [prepare.py](../../src/legacy/audits/palmar_digit_root_local_donor_shape_restoration_feasibility_r1/prepare.py)
- [render.py](../../src/legacy/audits/palmar_digit_root_local_donor_shape_restoration_feasibility_r1/render.py)

## 测试结论

> **VERDICT = PASS_LOCAL_DONOR_SHAPE_RESTORATION_FEASIBLE**。临时position-only donor restoration可行：上方小框hard shelf明显减弱、自然指根crease保留；下方正常区域几何精确不变。本轮是feasibility，不是Human最终接受、正式design或APPLY。

出处：[PALMAR_DIGIT_ROOT_LOCAL_DONOR_SHAPE_RESTORATION_FEASIBILITY_R1_REPORT.md](../research/audits/palmar_digit_root_local_donor_shape_restoration_feasibility_r1/PALMAR_DIGIT_ROOT_LOCAL_DONOR_SHAPE_RESTORATION_FEASIBILITY_R1_REPORT.md)

> 连续linear transfer path最小fan triangle area0.02931984mm²，无zero-area event；这不是完整连续collision qualification。endpoint static PASS，不替代任何Stage6 deformation qualification。

出处：[PALMAR_DIGIT_ROOT_LOCAL_DONOR_SHAPE_RESTORATION_FEASIBILITY_R1_REPORT.md](../research/audits/palmar_digit_root_local_donor_shape_restoration_feasibility_r1/PALMAR_DIGIT_ROOT_LOCAL_DONOR_SHAPE_RESTORATION_FEASIBILITY_R1_REPORT.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 原报告与关键代码

- [audits/palmar_digit_root_local_donor_shape_restoration_feasibility_r1/PALMAR_DIGIT_ROOT_LOCAL_DONOR_SHAPE_RESTORATION_FEASIBILITY_R1_REPORT.md](../research/audits/palmar_digit_root_local_donor_shape_restoration_feasibility_r1/PALMAR_DIGIT_ROOT_LOCAL_DONOR_SHAPE_RESTORATION_FEASIBILITY_R1_REPORT.md)
- [audits/palmar_digit_root_local_donor_shape_restoration_feasibility_r1/common.py](../../src/legacy/audits/palmar_digit_root_local_donor_shape_restoration_feasibility_r1/common.py)
- [audits/palmar_digit_root_local_donor_shape_restoration_feasibility_r1/deliver.py](../../src/legacy/audits/palmar_digit_root_local_donor_shape_restoration_feasibility_r1/deliver.py)
- [audits/palmar_digit_root_local_donor_shape_restoration_feasibility_r1/metrics_and_sections.py](../../src/legacy/audits/palmar_digit_root_local_donor_shape_restoration_feasibility_r1/metrics_and_sections.py)
- [audits/palmar_digit_root_local_donor_shape_restoration_feasibility_r1/prepare.py](../../src/legacy/audits/palmar_digit_root_local_donor_shape_restoration_feasibility_r1/prepare.py)
- [audits/palmar_digit_root_local_donor_shape_restoration_feasibility_r1/render.py](../../src/legacy/audits/palmar_digit_root_local_donor_shape_restoration_feasibility_r1/render.py)
- [audits/palmar_digit_root_local_donor_shape_restoration_feasibility_r1/save_probe.py](../../src/legacy/audits/palmar_digit_root_local_donor_shape_restoration_feasibility_r1/save_probe.py)
- [audits/palmar_digit_root_local_donor_shape_restoration_feasibility_r1/structure_gate.py](../../src/legacy/audits/palmar_digit_root_local_donor_shape_restoration_feasibility_r1/structure_gate.py)
- [audits/palmar_digit_root_local_donor_shape_restoration_feasibility_r1/verify_delivery.py](../../src/legacy/audits/palmar_digit_root_local_donor_shape_restoration_feasibility_r1/verify_delivery.py)

## 输入、输出与大型证据

该目录原始成员 94 项；拟公开身份记录 82 项。
- `audits/palmar_digit_root_local_donor_shape_restoration_feasibility_r1/MATCHED_REVIEW_GEOMETRY_R1.json` → `hands-research-r1-selected-005.zip` / `payload/audits/palmar_digit_root_local_donor_shape_restoration_feasibility_r1/MATCHED_REVIEW_GEOMETRY_R1.json`
- `audits/palmar_digit_root_local_donor_shape_restoration_feasibility_r1/NATIVE_RENDER_LOOP_TRIANGLES_R1.json` → `hands-research-r1-selected-005.zip` / `payload/audits/palmar_digit_root_local_donor_shape_restoration_feasibility_r1/NATIVE_RENDER_LOOP_TRIANGLES_R1.json`
- `audits/palmar_digit_root_local_donor_shape_restoration_feasibility_r1/TEMP_PALMAR_ROOT_DONOR_TRANSFER_PROBE_R1.blend` → `hands-research-r1-selected-005.zip` / `payload/audits/palmar_digit_root_local_donor_shape_restoration_feasibility_r1/TEMP_PALMAR_ROOT_DONOR_TRANSFER_PROBE_R1.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
