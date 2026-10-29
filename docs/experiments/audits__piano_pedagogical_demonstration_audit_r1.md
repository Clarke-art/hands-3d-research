# audits/piano_pedagogical_demonstration_audit_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 1. **Q1 — 正确候选手指/琴键？** PASS。23 音及 46 个事件与实际 MIDI 对齐；对应 skin 顶点在触键/持键样本中落于目标可奏键面范围。包含 F♯5 黑键；不是只验证音名映射。

出处：[FINAL_ANSWERS.md](../research/audits/piano_pedagogical_demonstration_audit_r1/FINAL_ANSWERS.md)

> |音符/手指|目标键（MIDI/index）|类型|源 ON → OFF|视频 ON → OFF|触键|持键释放|空间自然性|教学结论|证据/问题|

出处：[ALL_23_NOTES_TEACHING_AUDIT.md](../research/audits/piano_pedagogical_demonstration_audit_r1/ALL_23_NOTES_TEACHING_AUDIT.md)

## 技术路线

> 12. **Q12 — 冻结资产与历史是否保护？** 是。7,911 个受保护文件前后 SHA256 一致，其中 6,727 个亦匹配既有历史冻结记录；含唯一候选、MIDI、原媒体、历史资产。无新运动求解、无新动态候选、无 Blend 保存、无 Rig/权重/琴键修改。结论范围以清单为准，历史 FAIL_CLOSED / NOT_APPROVED 保留。

出处：[FINAL_ANSWERS.md](../research/audits/piano_pedagogical_demonstration_audit_r1/FINAL_ANSWERS.md)

> 教学结论按音符自己的主动指及交接评定，整段画面的其他缺陷单独列出。三视角切换暂停并保持同一原时间；单播放器避免多播放器时钟漂移。逐帧显示原渲染 PNG，不依赖浏览器 MP4 seek 的帧精度。连续播放速度由浏览器 playbackRate 实现，不生成新中间姿态。

出处：[PEDAGOGICAL_DEMONSTRATION_STANDARD.md](../research/audits/piano_pedagogical_demonstration_audit_r1/PEDAGOGICAL_DEMONSTRATION_STANDARD.md)

## 测试结论

> 当前已具备独立 Human 教学审核条件；尚不具备直接向初学者发布、反复模仿的通过结论。

出处：[FINAL_ANSWERS.md](../research/audits/piano_pedagogical_demonstration_audit_r1/FINAL_ANSWERS.md)

> 1. **Q1 — 正确候选手指/琴键？** PASS。23 音及 46 个事件与实际 MIDI 对齐；对应 skin 顶点在触键/持键样本中落于目标可奏键面范围。包含 F♯5 黑键；不是只验证音名映射。

出处：[FINAL_ANSWERS.md](../research/audits/piano_pedagogical_demonstration_audit_r1/FINAL_ANSWERS.md)

## 失败原因与证据边界

> 6. **Q6 — 左手教学价值？** 有条件支持。7 音自身触键/持键/释放检查通过，开头 G3+B3+D4 为 5/3/1 指，后续 A3/B3/C4/B3 落点保持；原片同时包含右手阻断问题。左手闲置指伸展和专业手型仍待教师确认。

出处：[FINAL_ANSWERS.md](../research/audits/piano_pedagogical_demonstration_audit_r1/FINAL_ANSWERS.md)

> |L00 L G3 / 5指|G3 (55/34)|和弦 G3+B3+D4|0.000000 → 0.857142|0.350000 → 1.207142|PASS|PASS|PASS|PASS|`逐音定位`（链接见原报告） · `画面`（链接见原报告） · 无本音已证实阻断|

出处：[ALL_23_NOTES_TEACHING_AUDIT.md](../research/audits/piano_pedagogical_demonstration_audit_r1/ALL_23_NOTES_TEACHING_AUDIT.md)

## 后续建议

> 6. **Q6 — 左手教学价值？** 有条件支持。7 音自身触键/持键/释放检查通过，开头 G3+B3+D4 为 5/3/1 指，后续 A3/B3/C4/B3 落点保持；原片同时包含右手阻断问题。左手闲置指伸展和专业手型仍待教师确认。

出处：[FINAL_ANSWERS.md](../research/audits/piano_pedagogical_demonstration_audit_r1/FINAL_ANSWERS.md)

> 8. **Q8 — 必须修复什么？** 审核建议必须修复 B01/B02 的独立手指位置/交替表达，以及 B03 中可见嵌入黑键的闲置指路径。它们可能让学生模仿物理上不可行的动作。

出处：[FINAL_ANSWERS.md](../research/audits/piano_pedagogical_demonstration_audit_r1/FINAL_ANSWERS.md)

## 原报告与关键代码

- [audits/piano_pedagogical_demonstration_audit_r1/FINAL_ANSWERS.md](../research/audits/piano_pedagogical_demonstration_audit_r1/FINAL_ANSWERS.md)
- [audits/piano_pedagogical_demonstration_audit_r1/TEACHING_DEFECT_REGISTER.md](../research/audits/piano_pedagogical_demonstration_audit_r1/TEACHING_DEFECT_REGISTER.md)
- [audits/piano_pedagogical_demonstration_audit_r1/ALL_23_NOTES_TEACHING_AUDIT.md](../research/audits/piano_pedagogical_demonstration_audit_r1/ALL_23_NOTES_TEACHING_AUDIT.md)
- [audits/piano_pedagogical_demonstration_audit_r1/PEDAGOGICAL_DEMONSTRATION_STANDARD.md](../research/audits/piano_pedagogical_demonstration_audit_r1/PEDAGOGICAL_DEMONSTRATION_STANDARD.md)
- [audits/piano_pedagogical_demonstration_audit_r1/build_delivery.py](../../src/legacy/audits/piano_pedagogical_demonstration_audit_r1/build_delivery.py)
- [audits/piano_pedagogical_demonstration_audit_r1/finish_audit.py](../../src/legacy/audits/piano_pedagogical_demonstration_audit_r1/finish_audit.py)
- [audits/piano_pedagogical_demonstration_audit_r1/prepare_evidence.py](../../src/legacy/audits/piano_pedagogical_demonstration_audit_r1/prepare_evidence.py)
- [audits/piano_pedagogical_demonstration_audit_r1/probe_readonly.py](../../src/legacy/audits/piano_pedagogical_demonstration_audit_r1/probe_readonly.py)
- [audits/piano_pedagogical_demonstration_audit_r1/serve_review.py](../../src/legacy/audits/piano_pedagogical_demonstration_audit_r1/serve_review.py)

## 输入、输出与大型证据

该目录原始成员 25 项；拟公开身份记录 24 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
