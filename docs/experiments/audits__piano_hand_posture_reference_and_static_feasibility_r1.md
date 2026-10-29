# audits/piano_hand_posture_reference_and_static_feasibility_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> - 手与任务：左手，Für Elise 的 A–E–A 分解伴奏八度准备；低 A 小指、高 A 拇指。可比较白键八度空间，但不是本项目 D2/D3 交替，中间还有 E 的任务。

出处：[REAL_PIANO_REFERENCE_MANIFEST_R1.md](../research/audits/piano_hand_posture_reference_and_static_feasibility_r1/REAL_PIANO_REFERENCE_MANIFEST_R1.md)

> - 手与任务：右手 C–G 白键五指基础练习摆位。拇指在白键前部，长指呈不同程度的弯曲；各指不是等长等高地垂直排列。

出处：[REAL_PIANO_REFERENCE_MANIFEST_R1.md](../research/audits/piano_hand_posture_reference_and_static_feasibility_r1/REAL_PIANO_REFERENCE_MANIFEST_R1.md)

## 技术路线

> 1. **自然姿态目标没有真人标定。** `qrest`、`natural` 是 RSSF 的固定增量，`drive` 是激活量的加权组合。左手闲置指刚硬可能来自这些低维目标；这是基于实现与画面的因果假说，不是受控消融结论。

出处：[NEXT_MOTION_ENGINE_REQUIREMENTS_R1.md](../research/audits/piano_hand_posture_reference_and_static_feasibility_r1/NEXT_MOTION_ENGINE_REQUIREMENTS_R1.md)

> 2. **已有 shared root，但目标仍偏单帧。** 每个时间点用前一解预测，求解当下活跃/准备/释放 pad；掌部正则拉向初始化 `base`。缺少跨下一音的整体手型、掌部承载和重新布置计划。不能把问题错误归为“旧版五指各自没有共同手掌”。

出处：[NEXT_MOTION_ENGINE_REQUIREMENTS_R1.md](../research/audits/piano_hand_posture_reference_and_static_feasibility_r1/NEXT_MOTION_ENGINE_REQUIREMENTS_R1.md)

## 测试结论

> 状态：**REQUIREMENTS_DRAFTED / IMPLEMENTATION_GATE_CLOSED**。本轮无新生成器、Action、IK 调参或候选筛选。

出处：[NEXT_MOTION_ENGINE_REQUIREMENTS_R1.md](../research/audits/piano_hand_posture_reference_and_static_feasibility_r1/NEXT_MOTION_ENGINE_REQUIREMENTS_R1.md)

> 1. **自然姿态目标没有真人标定。** `qrest`、`natural` 是 RSSF 的固定增量，`drive` 是激活量的加权组合。左手闲置指刚硬可能来自这些低维目标；这是基于实现与画面的因果假说，不是受控消融结论。

出处：[NEXT_MOTION_ENGINE_REQUIREMENTS_R1.md](../research/audits/piano_hand_posture_reference_and_static_feasibility_r1/NEXT_MOTION_ENGINE_REQUIREMENTS_R1.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

> 2. **已有 shared root，但目标仍偏单帧。** 每个时间点用前一解预测，求解当下活跃/准备/释放 pad；掌部正则拉向初始化 `base`。缺少跨下一音的整体手型、掌部承载和重新布置计划。不能把问题错误归为“旧版五指各自没有共同手掌”。

出处：[NEXT_MOTION_ENGINE_REQUIREMENTS_R1.md](../research/audits/piano_hand_posture_reference_and_static_feasibility_r1/NEXT_MOTION_ENGINE_REQUIREMENTS_R1.md)

> | 共同掌部规划 | 接收一个短音符区间及每指角色，输出可行共同掌姿与下一音准备；不是逐音独立寻找 root。 |

出处：[NEXT_MOTION_ENGINE_REQUIREMENTS_R1.md](../research/audits/piano_hand_posture_reference_and_static_feasibility_r1/NEXT_MOTION_ENGINE_REQUIREMENTS_R1.md)

## 原报告与关键代码

- [audits/piano_hand_posture_reference_and_static_feasibility_r1/REAL_PIANO_REFERENCE_MANIFEST_R1.md](../research/audits/piano_hand_posture_reference_and_static_feasibility_r1/REAL_PIANO_REFERENCE_MANIFEST_R1.md)
- [audits/piano_hand_posture_reference_and_static_feasibility_r1/NEXT_MOTION_ENGINE_REQUIREMENTS_R1.md](../research/audits/piano_hand_posture_reference_and_static_feasibility_r1/NEXT_MOTION_ENGINE_REQUIREMENTS_R1.md)
- [audits/piano_hand_posture_reference_and_static_feasibility_r1/NATURAL_PIANO_HAND_POSTURE_CONTRACT_R1.md](../research/audits/piano_hand_posture_reference_and_static_feasibility_r1/NATURAL_PIANO_HAND_POSTURE_CONTRACT_R1.md)
- [audits/piano_hand_posture_reference_and_static_feasibility_r1/PIANO_HAND_POSTURE_REFERENCE_AND_STATIC_FEASIBILITY_R1_REPORT.md](../research/audits/piano_hand_posture_reference_and_static_feasibility_r1/PIANO_HAND_POSTURE_REFERENCE_AND_STATIC_FEASIBILITY_R1_REPORT.md)
- [audits/piano_hand_posture_reference_and_static_feasibility_r1/03_measure.py](../../src/legacy/audits/piano_hand_posture_reference_and_static_feasibility_r1/03_measure.py)
- [audits/piano_hand_posture_reference_and_static_feasibility_r1/04_read_formal.py](../../src/legacy/audits/piano_hand_posture_reference_and_static_feasibility_r1/04_read_formal.py)
- [audits/piano_hand_posture_reference_and_static_feasibility_r1/05_deliver.py](../../src/legacy/audits/piano_hand_posture_reference_and_static_feasibility_r1/05_deliver.py)
- [audits/piano_hand_posture_reference_and_static_feasibility_r1/07_verify.py](../../src/legacy/audits/piano_hand_posture_reference_and_static_feasibility_r1/07_verify.py)

## 输入、输出与大型证据

该目录原始成员 29 项；拟公开身份记录 28 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
