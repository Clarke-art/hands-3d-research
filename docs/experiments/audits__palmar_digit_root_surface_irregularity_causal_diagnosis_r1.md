# audits/palmar_digit_root_surface_irregularity_causal_diagnosis_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 结果：**UNRESOLVED — STOP — HUMAN REVIEW**。Human 原截图未包含在本次附件中，不能唯一匹配 case / pose / ROI。已完成可复查的候选区域诊断，不把候选结论冒充 Human 实际目标结论。

出处：[PALMAR_DIGIT_ROOT_SURFACE_IRREGULARITY_CAUSAL_DIAGNOSIS_R1_REPORT.md](../research/audits/palmar_digit_root_surface_irregularity_causal_diagnosis_r1/PALMAR_DIGIT_ROOT_SURFACE_IRREGULARITY_CAUSAL_DIAGNOSIS_R1_REPORT.md)

> 4. 从冻结 rest matrices、既有 weights 和保存角度进行纯代数 LBS reconstruction，ROI 最大误差分别约 0.000063 / 0.000060 / 0.000030 mm。这解释 limited IDX deformation 的机制，不证明权重失败或关节变换错误。基线 geometry / 着色可见度是主要候选因素，Human 目标归因仍未解决。

出处：[PALMAR_DIGIT_ROOT_SURFACE_IRREGULARITY_CAUSAL_DIAGNOSIS_R1_REPORT.md](../research/audits/palmar_digit_root_surface_irregularity_causal_diagnosis_r1/PALMAR_DIGIT_ROOT_SURFACE_IRREGULARITY_CAUSAL_DIAGNOSIS_R1_REPORT.md)

## 技术路线

原报告未单独概述路线；以下实现文件与原报告共同界定方法，不能由文件名推断算法成功：

- [common.py](../../src/legacy/audits/palmar_digit_root_surface_irregularity_causal_diagnosis_r1/common.py)
- [deliver.py](../../src/legacy/audits/palmar_digit_root_surface_irregularity_causal_diagnosis_r1/deliver.py)
- [diagnose.py](../../src/legacy/audits/palmar_digit_root_surface_irregularity_causal_diagnosis_r1/diagnose.py)
- [native_readback.py](../../src/legacy/audits/palmar_digit_root_surface_irregularity_causal_diagnosis_r1/native_readback.py)
- [render_diagnostic.py](../../src/legacy/audits/palmar_digit_root_surface_irregularity_causal_diagnosis_r1/render_diagnostic.py)

## 测试结论

> 结果：**UNRESOLVED — STOP — HUMAN REVIEW**。Human 原截图未包含在本次附件中，不能唯一匹配 case / pose / ROI。已完成可复查的候选区域诊断，不把候选结论冒充 Human 实际目标结论。

出处：[PALMAR_DIGIT_ROOT_SURFACE_IRREGULARITY_CAUSAL_DIAGNOSIS_R1_REPORT.md](../research/audits/palmar_digit_root_surface_irregularity_causal_diagnosis_r1/PALMAR_DIGIT_ROOT_SURFACE_IRREGULARITY_CAUSAL_DIAGNOSIS_R1_REPORT.md)

> - 顶点/face最大角或 flat画面不直接构成人体阈值。本轮没有构造 anatomical threshold、没有 product PASS、没有将审美判断替换为 machine 判断。

出处：[PALMAR_DIGIT_ROOT_SURFACE_IRREGULARITY_CAUSAL_DIAGNOSIS_R1_REPORT.md](../research/audits/palmar_digit_root_surface_irregularity_causal_diagnosis_r1/PALMAR_DIGIT_ROOT_SURFACE_IRREGULARITY_CAUSAL_DIAGNOSIS_R1_REPORT.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

> 7. 若 Human 确认此候选且认为不能接受，最小层次首先是局部 base geometry continuity 与显示着色设计；normal-only 足够性未证明，当前数据未支持直接改 weights / rig。这里只记录建议，不执行 NEXT / repair。

出处：[PALMAR_DIGIT_ROOT_SURFACE_IRREGULARITY_CAUSAL_DIAGNOSIS_R1_REPORT.md](../research/audits/palmar_digit_root_surface_irregularity_causal_diagnosis_r1/PALMAR_DIGIT_ROOT_SURFACE_IRREGULARITY_CAUSAL_DIAGNOSIS_R1_REPORT.md)

## 原报告与关键代码

- [audits/palmar_digit_root_surface_irregularity_causal_diagnosis_r1/PALMAR_DIGIT_ROOT_SURFACE_IRREGULARITY_CAUSAL_DIAGNOSIS_R1_REPORT.md](../research/audits/palmar_digit_root_surface_irregularity_causal_diagnosis_r1/PALMAR_DIGIT_ROOT_SURFACE_IRREGULARITY_CAUSAL_DIAGNOSIS_R1_REPORT.md)
- [audits/palmar_digit_root_surface_irregularity_causal_diagnosis_r1/common.py](../../src/legacy/audits/palmar_digit_root_surface_irregularity_causal_diagnosis_r1/common.py)
- [audits/palmar_digit_root_surface_irregularity_causal_diagnosis_r1/deliver.py](../../src/legacy/audits/palmar_digit_root_surface_irregularity_causal_diagnosis_r1/deliver.py)
- [audits/palmar_digit_root_surface_irregularity_causal_diagnosis_r1/diagnose.py](../../src/legacy/audits/palmar_digit_root_surface_irregularity_causal_diagnosis_r1/diagnose.py)
- [audits/palmar_digit_root_surface_irregularity_causal_diagnosis_r1/native_readback.py](../../src/legacy/audits/palmar_digit_root_surface_irregularity_causal_diagnosis_r1/native_readback.py)
- [audits/palmar_digit_root_surface_irregularity_causal_diagnosis_r1/render_diagnostic.py](../../src/legacy/audits/palmar_digit_root_surface_irregularity_causal_diagnosis_r1/render_diagnostic.py)
- [audits/palmar_digit_root_surface_irregularity_causal_diagnosis_r1/sections_and_drivers.py](../../src/legacy/audits/palmar_digit_root_surface_irregularity_causal_diagnosis_r1/sections_and_drivers.py)
- [audits/palmar_digit_root_surface_irregularity_causal_diagnosis_r1/silhouette_metrics.py](../../src/legacy/audits/palmar_digit_root_surface_irregularity_causal_diagnosis_r1/silhouette_metrics.py)
- [audits/palmar_digit_root_surface_irregularity_causal_diagnosis_r1/verify_delivery.py](../../src/legacy/audits/palmar_digit_root_surface_irregularity_causal_diagnosis_r1/verify_delivery.py)

## 输入、输出与大型证据

该目录原始成员 114 项；拟公开身份记录 112 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
