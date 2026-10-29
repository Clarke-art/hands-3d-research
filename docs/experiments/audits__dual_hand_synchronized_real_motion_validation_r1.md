# audits/dual_hand_synchronized_real_motion_validation_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 双手分别单独运行与合并运行的 421 × 3300 个顶点均数值精确一致；左右 mesh、Armature、Action slot、corrective driver 目标严格独立，无 NLA、跨手约束或错误通道。左手亦与上一轮已批准的全部 421 个保存观测数值精确一致。

出处：[DUAL_HAND_SYNCHRONIZED_REAL_MOTION_VALIDATION_R1_REPORT.md](../research/audits/dual_hand_synchronized_real_motion_validation_r1/DUAL_HAND_SYNCHRONIZED_REAL_MOTION_VALIDATION_R1_REPORT.md)

> 没有开展 keyboard installation、contact、root/wrist 世界位置解算、MIDI-to-key、fingering、glTF、Three.js 或正式集成。源 landmarks 为 video-estimated non-metric 2.5D；本轮仅验证两个 skeleton tracks 的同时间轴同步播放，不声称音符、指法、落键或琴键接触正确。

出处：[DUAL_HAND_SYNCHRONIZED_REAL_MOTION_VALIDATION_R1_REPORT.md](../research/audits/dual_hand_synchronized_real_motion_validation_r1/DUAL_HAND_SYNCHRONIZED_REAL_MOTION_VALIDATION_R1_REPORT.md)

## 技术路线

原报告未单独概述路线；以下实现文件与原报告共同界定方法，不能由文件名推断算法成功：

- [01_build_verify.py](../../src/legacy/audits/dual_hand_synchronized_real_motion_validation_r1/01_build_verify.py)
- [02_render.py](../../src/legacy/audits/dual_hand_synchronized_real_motion_validation_r1/02_render.py)
- [03_media.py](../../src/legacy/audits/dual_hand_synchronized_real_motion_validation_r1/03_media.py)
- [04_finalize.py](../../src/legacy/audits/dual_hand_synchronized_real_motion_validation_r1/04_finalize.py)

## 测试结论

> **结论：DUAL_HAND_SYNCHRONIZED_MOTION_VALIDATED。Agent 预检完成，最终 Human Review 待定。**

出处：[DUAL_HAND_SYNCHRONIZED_REAL_MOTION_VALIDATION_R1_REPORT.md](../research/audits/dual_hand_synchronized_real_motion_validation_r1/DUAL_HAND_SYNCHRONIZED_REAL_MOTION_VALIDATION_R1_REPORT.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 原报告与关键代码

- [audits/dual_hand_synchronized_real_motion_validation_r1/DUAL_HAND_SYNCHRONIZED_REAL_MOTION_VALIDATION_R1_REPORT.md](../research/audits/dual_hand_synchronized_real_motion_validation_r1/DUAL_HAND_SYNCHRONIZED_REAL_MOTION_VALIDATION_R1_REPORT.md)
- [audits/dual_hand_synchronized_real_motion_validation_r1/01_build_verify.py](../../src/legacy/audits/dual_hand_synchronized_real_motion_validation_r1/01_build_verify.py)
- [audits/dual_hand_synchronized_real_motion_validation_r1/02_render.py](../../src/legacy/audits/dual_hand_synchronized_real_motion_validation_r1/02_render.py)
- [audits/dual_hand_synchronized_real_motion_validation_r1/03_media.py](../../src/legacy/audits/dual_hand_synchronized_real_motion_validation_r1/03_media.py)
- [audits/dual_hand_synchronized_real_motion_validation_r1/04_finalize.py](../../src/legacy/audits/dual_hand_synchronized_real_motion_validation_r1/04_finalize.py)

## 输入、输出与大型证据

该目录原始成员 30 项；拟公开身份记录 6 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
