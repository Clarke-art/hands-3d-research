# audits/midi_driven_hand_posture_and_contact_refinement_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> |Q5 左手八度姿态自然|NO；可到达多数接触目标，但拇指/掌侧接触风险和持音遗漏仍在，整手自然度未通过。|

出处：[MIDI_DRIVEN_HAND_POSTURE_AND_CONTACT_REFINEMENT_R1_REPORT.md](../research/audits/midi_driven_hand_posture_and_contact_refinement_r1/MIDI_DRIVEN_HAND_POSTURE_AND_CONTACT_REFINEMENT_R1_REPORT.md)

> |Q9 仍有悬浮/穿键/错键/掌腕问题|YES；持音悬空和掌部键体筛查命中仍在。演奏指未发现目标键区域错误或超过阈值的pad穿键；闲置pad另有邻键接近风险。|

出处：[MIDI_DRIVEN_HAND_POSTURE_AND_CONTACT_REFINEMENT_R1_REPORT.md](../research/audits/midi_driven_hand_posture_and_contact_refinement_r1/MIDI_DRIVEN_HAND_POSTURE_AND_CONTACT_REFINEMENT_R1_REPORT.md)

## 技术路线

> |Q2 整手协调姿态规划|YES；共享掌坐标系、四类状态、闲置指被动随动与掌腕共同求解。|

出处：[MIDI_DRIVEN_HAND_POSTURE_AND_CONTACT_REFINEMENT_R1_REPORT.md](../research/audits/midi_driven_hand_posture_and_contact_refinement_r1/MIDI_DRIVEN_HAND_POSTURE_AND_CONTACT_REFINEMENT_R1_REPORT.md)

> |Q7 掌腕合理随动|NO（完整质量门槛）；已实现有界连续随动，但仍存在掌部命中和接触不稳定。|

出处：[MIDI_DRIVEN_HAND_POSTURE_AND_CONTACT_REFINEMENT_R1_REPORT.md](../research/audits/midi_driven_hand_posture_and_contact_refinement_r1/MIDI_DRIVEN_HAND_POSTURE_AND_CONTACT_REFINEMENT_R1_REPORT.md)

## 测试结论

> **MOTION_REFINEMENT_PARTIAL**。**STOP — HUMAN REVIEW**。只保留一个 DESIGN_ONLY 候选。左手闲置三指与原右手跳变有改善；接触和整手自然度未达到提交资格门槛，不冒充 Human PASS。

出处：[MIDI_DRIVEN_HAND_POSTURE_AND_CONTACT_REFINEMENT_R1_REPORT.md](../research/audits/midi_driven_hand_posture_and_contact_refinement_r1/MIDI_DRIVEN_HAND_POSTURE_AND_CONTACT_REFINEMENT_R1_REPORT.md)

> |Q2 整手协调姿态规划|YES；共享掌坐标系、四类状态、闲置指被动随动与掌腕共同求解。|

出处：[MIDI_DRIVEN_HAND_POSTURE_AND_CONTACT_REFINEMENT_R1_REPORT.md](../research/audits/midi_driven_hand_posture_and_contact_refinement_r1/MIDI_DRIVEN_HAND_POSTURE_AND_CONTACT_REFINEMENT_R1_REPORT.md)

## 失败原因与证据边界

> |Q1 左手2/3/4指异常蜷曲的原因|闲置指也被独立 IK 强制拉到虚构 home 键位；自然/连续性权重极弱，固定掌位与伸距冲突。PIP约72/60/53°，中指DIP到65°边界，缺乏整手协调。|

出处：[MIDI_DRIVEN_HAND_POSTURE_AND_CONTACT_REFINEMENT_R1_REPORT.md](../research/audits/midi_driven_hand_posture_and_contact_refinement_r1/MIDI_DRIVEN_HAND_POSTURE_AND_CONTACT_REFINEMENT_R1_REPORT.md)

## 后续建议

> - **C 右手2.608s跳变**：发生在食指 E5 NOTE_OFF=2.575s后的释放段。每帧局部求解虽warm-start，却没有速度/加速度边界，连续性权重极弱；上一帧合法姿态无法约束下一解，出现21.817°变化。代码与轨迹支持这一机制；没有额外声称已数学证明全部IK解分支。

出处：[MIDI_DRIVEN_HAND_POSTURE_AND_CONTACT_REFINEMENT_R1_REPORT.md](../research/audits/midi_driven_hand_posture_and_contact_refinement_r1/MIDI_DRIVEN_HAND_POSTURE_AND_CONTACT_REFINEMENT_R1_REPORT.md)

> 掌根XYZ/yaw/pitch/roll与指关节联合求解，始终一个整体root，比例恒为1。全局范围和逐步速度/加速度边界在 `GENERATION_POLICY_R1.json`。上一合法状态与速度预测进入下一步目标和可行范围；非负palmar flexion、关节限位、姿态参考、闲置pad与少量掌部代理点的clearance一起约束。不做事后轨迹平滑，不把指尖直接写入键面。

出处：[MIDI_DRIVEN_HAND_POSTURE_AND_CONTACT_REFINEMENT_R1_REPORT.md](../research/audits/midi_driven_hand_posture_and_contact_refinement_r1/MIDI_DRIVEN_HAND_POSTURE_AND_CONTACT_REFINEMENT_R1_REPORT.md)

## 原报告与关键代码

- [audits/midi_driven_hand_posture_and_contact_refinement_r1/MIDI_DRIVEN_HAND_POSTURE_AND_CONTACT_REFINEMENT_R1_REPORT.md](../research/audits/midi_driven_hand_posture_and_contact_refinement_r1/MIDI_DRIVEN_HAND_POSTURE_AND_CONTACT_REFINEMENT_R1_REPORT.md)
- [audits/midi_driven_hand_posture_and_contact_refinement_r1/00_inherit.py](../../src/legacy/audits/midi_driven_hand_posture_and_contact_refinement_r1/00_inherit.py)
- [audits/midi_driven_hand_posture_and_contact_refinement_r1/01_coordinate.py](../../src/legacy/audits/midi_driven_hand_posture_and_contact_refinement_r1/01_coordinate.py)
- [audits/midi_driven_hand_posture_and_contact_refinement_r1/02_build_scripts.py](../../src/legacy/audits/midi_driven_hand_posture_and_contact_refinement_r1/02_build_scripts.py)
- [audits/midi_driven_hand_posture_and_contact_refinement_r1/03_scene.py](../../src/legacy/audits/midi_driven_hand_posture_and_contact_refinement_r1/03_scene.py)
- [audits/midi_driven_hand_posture_and_contact_refinement_r1/04_evaluate.py](../../src/legacy/audits/midi_driven_hand_posture_and_contact_refinement_r1/04_evaluate.py)
- [audits/midi_driven_hand_posture_and_contact_refinement_r1/05_render.py](../../src/legacy/audits/midi_driven_hand_posture_and_contact_refinement_r1/05_render.py)
- [audits/midi_driven_hand_posture_and_contact_refinement_r1/06_media.py](../../src/legacy/audits/midi_driven_hand_posture_and_contact_refinement_r1/06_media.py)
- [audits/midi_driven_hand_posture_and_contact_refinement_r1/07_finish.py](../../src/legacy/audits/midi_driven_hand_posture_and_contact_refinement_r1/07_finish.py)
- [audits/midi_driven_hand_posture_and_contact_refinement_r1/08_verify.py](../../src/legacy/audits/midi_driven_hand_posture_and_contact_refinement_r1/08_verify.py)
- [audits/midi_driven_hand_posture_and_contact_refinement_r1/09_contact_view.py](../../src/legacy/audits/midi_driven_hand_posture_and_contact_refinement_r1/09_contact_view.py)
- [audits/midi_driven_hand_posture_and_contact_refinement_r1/performance_core.py](../../src/legacy/audits/midi_driven_hand_posture_and_contact_refinement_r1/performance_core.py)

## 输入、输出与大型证据

该目录原始成员 65 项；拟公开身份记录 45 项。
- `audits/midi_driven_hand_posture_and_contact_refinement_r1/evaluated_candidate.npz` → `hands-research-r1-selected-002.zip` / `payload/audits/midi_driven_hand_posture_and_contact_refinement_r1/evaluated_candidate.npz`
- `audits/midi_driven_hand_posture_and_contact_refinement_r1/HAND_POSTURE_CONTACT_REFINED_DESIGN_ONLY_R1.blend` → `hands-research-r1-selected-002.zip` / `payload/audits/midi_driven_hand_posture_and_contact_refinement_r1/HAND_POSTURE_CONTACT_REFINED_DESIGN_ONLY_R1.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
