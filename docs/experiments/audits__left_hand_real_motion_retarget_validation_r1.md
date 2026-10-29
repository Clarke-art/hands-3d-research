# audits/left_hand_real_motion_retarget_validation_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> “VALIDATED”在此是本轮提交给 Human 的 Agent 分类，不代表 Human 已批准这段新 motion，也不等同于公制生物力学或琴键接触验证。

出处：[LEFT_HAND_REAL_MOTION_RETARGET_VALIDATION_R1_REPORT.md](../research/audits/left_hand_real_motion_retarget_validation_r1/LEFT_HAND_REAL_MOTION_RETARGET_VALIDATION_R1_REPORT.md)

> 这是视频估计的非公制2.5D landmarks，不是标定后的真实公制3D mocap。源数据能支持本轮方向/时序retarget验证，不能独立证明精确解剖关节角、指尖落键或空间接触。

出处：[LEFT_HAND_REAL_MOTION_RETARGET_VALIDATION_R1_REPORT.md](../research/audits/left_hand_real_motion_retarget_validation_r1/LEFT_HAND_REAL_MOTION_RETARGET_VALIDATION_R1_REPORT.md)

## 技术路线

> 直接以AST读取既有 approved `mapping_core.py` 的校准、raw mapping和smoothed方法；未执行其旧顶层脚本，未打开或修改旧右手工程资产。

出处：[LEFT_HAND_REAL_MOTION_RETARGET_VALIDATION_R1_REPORT.md](../research/audits/left_hand_real_motion_retarget_validation_r1/LEFT_HAND_REAL_MOTION_RETARGET_VALIDATION_R1_REPORT.md)

## 测试结论

> 明显penetration与surface接受度由可见证据预检记录，机器检查不作为Human PASS。没有hidden crossing、normal-dot、R3、true-cap、2127-edge或anatomy forensic。

出处：[LEFT_HAND_REAL_MOTION_RETARGET_VALIDATION_R1_REPORT.md](../research/audits/left_hand_real_motion_retarget_validation_r1/LEFT_HAND_REAL_MOTION_RETARGET_VALIDATION_R1_REPORT.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

> smoothing直接复用60Hz quaternion三点`[0.25,0.5,0.25]`，邻居符号对齐并normalize；边界重复端点，后续quaternion符号连续，half-frame LINEAR keys。

出处：[LEFT_HAND_REAL_MOTION_RETARGET_VALIDATION_R1_REPORT.md](../research/audits/left_hand_real_motion_retarget_validation_r1/LEFT_HAND_REAL_MOTION_RETARGET_VALIDATION_R1_REPORT.md)

## 原报告与关键代码

- [audits/left_hand_real_motion_retarget_validation_r1/LEFT_HAND_REAL_MOTION_RETARGET_VALIDATION_R1_REPORT.md](../research/audits/left_hand_real_motion_retarget_validation_r1/LEFT_HAND_REAL_MOTION_RETARGET_VALIDATION_R1_REPORT.md)
- [audits/left_hand_real_motion_retarget_validation_r1/01_source.py](../../src/legacy/audits/left_hand_real_motion_retarget_validation_r1/01_source.py)
- [audits/left_hand_real_motion_retarget_validation_r1/02_retarget.py](../../src/legacy/audits/left_hand_real_motion_retarget_validation_r1/02_retarget.py)
- [audits/left_hand_real_motion_retarget_validation_r1/03_render.py](../../src/legacy/audits/left_hand_real_motion_retarget_validation_r1/03_render.py)
- [audits/left_hand_real_motion_retarget_validation_r1/04_media.py](../../src/legacy/audits/left_hand_real_motion_retarget_validation_r1/04_media.py)
- [audits/left_hand_real_motion_retarget_validation_r1/05_matched_review.py](../../src/legacy/audits/left_hand_real_motion_retarget_validation_r1/05_matched_review.py)
- [audits/left_hand_real_motion_retarget_validation_r1/06_verify_saved.py](../../src/legacy/audits/left_hand_real_motion_retarget_validation_r1/06_verify_saved.py)
- [audits/left_hand_real_motion_retarget_validation_r1/07_finalize.py](../../src/legacy/audits/left_hand_real_motion_retarget_validation_r1/07_finalize.py)
- [audits/left_hand_real_motion_retarget_validation_r1/approved_solver_with_left_source_adapter.py](../../src/legacy/audits/left_hand_real_motion_retarget_validation_r1/approved_solver_with_left_source_adapter.py)

## 输入、输出与大型证据

该目录原始成员 40 项；拟公开身份记录 10 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
