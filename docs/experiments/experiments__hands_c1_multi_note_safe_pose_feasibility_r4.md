# experiments/hands_c1_multi_note_safe_pose_feasibility_r4

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 1. **四个连续音符分别有本轮找到的安全静态手型吗？** 有：R08 3.12s小指E5、R09 3.45s中指C5、R10 3.67s无名指D5、R11 3.88s中指E5。四个候选分别通过冻结活动接触合同、全手非目标键相交/内部深度0、全手非相邻自交0、关节越界0；跨手碰撞0，左手不变。全部NOT_APPROVED，待Human视觉审核。

出处：[HUMAN_REVIEW.md](../research/experiments/hands_c1_multi_note_safe_pose_feasibility_r4/HUMAN_REVIEW.md)

> 3. **中指C5、无名指D5、中指E5能否分别避免邻键穿模？** 三个代表帧均已做到，非法键相交/深度均0。腕部有5–9mm单轴调整；R10额外撤回并抬起闲置中指。活动手指始终在正确目标键可奏区，未更改音符、指法、时钟或键Action。

出处：[HUMAN_REVIEW.md](../research/experiments/hands_c1_multi_note_safe_pose_feasibility_r4/HUMAN_REVIEW.md)

## 技术路线

> 每帧从各自原R2姿态开始。尝试数 R08=2、R09=1、R10=1、R11=1；无角度网格/随机搜索、IK、求解器或插值。

出处：[STATIC_POSE_RESULTS.md](../research/experiments/hands_c1_multi_note_safe_pose_feasibility_r4/STATIC_POSE_RESULTS.md)

## 测试结论

> **MULTI_POSE_STATIC_PASS_PENDING_HUMAN + POSE_TRANSITION_RISK**

出处：[HUMAN_REVIEW.md](../research/experiments/hands_c1_multi_note_safe_pose_feasibility_r4/HUMAN_REVIEW.md)

> 2. **3.12s C♯5严重侵入能否在保持小指E5时消除？** 本轮可以。原4.227605mm→首轮1.254481mm→第二轮0；仅调整闲置中指，小指Pose及实际触点不动，活动触键合同保持PASS。

出处：[HUMAN_REVIEW.md](../research/experiments/hands_c1_multi_note_safe_pose_feasibility_r4/HUMAN_REVIEW.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

> 5. **安全姿态可能保持原C1自然风格吗？** 四帧仍沿用原腕朝向和活动指关节；主要是毫米级掌位调整及闲置中指抬起/撤回，未见新增极端折弯或展指，具有保留原风格的可能。R08中指更直更高，及相邻姿态约41.572mm腕位变化是否自然，需要Human与后续运动验证，不能凭单帧宣布自然度通过。原基础网格外观缺陷保持。

出处：[HUMAN_REVIEW.md](../research/experiments/hands_c1_multi_note_safe_pose_feasibility_r4/HUMAN_REVIEW.md)

> 6. **值得进入下一轮连续关键帧实验吗？** 有足够静态可行性证据，值得在Human审图后开展限定范围的连续验证；没有足够证据直接批准动画或安全闭合。最需先解决R10→R11持键/移腕和R11→R12无名指F♯5准备。R12原始姿态仍有非法邻键关系，本轮未修改，3.9928535s不得作为闭合点。

出处：[HUMAN_REVIEW.md](../research/experiments/hands_c1_multi_note_safe_pose_feasibility_r4/HUMAN_REVIEW.md)

## 原报告与关键代码

- [experiments/hands_c1_multi_note_safe_pose_feasibility_r4/HUMAN_REVIEW.md](../research/experiments/hands_c1_multi_note_safe_pose_feasibility_r4/HUMAN_REVIEW.md)
- [experiments/hands_c1_multi_note_safe_pose_feasibility_r4/STATIC_POSE_RESULTS.md](../research/experiments/hands_c1_multi_note_safe_pose_feasibility_r4/STATIC_POSE_RESULTS.md)
- [experiments/hands_c1_multi_note_safe_pose_feasibility_r4/POSE_COMPATIBILITY_REPORT.md](../research/experiments/hands_c1_multi_note_safe_pose_feasibility_r4/POSE_COMPATIBILITY_REPORT.md)
- [experiments/hands_c1_multi_note_safe_pose_feasibility_r4/make_delivery.py](../../src/legacy/experiments/hands_c1_multi_note_safe_pose_feasibility_r4/make_delivery.py)
- [experiments/hands_c1_multi_note_safe_pose_feasibility_r4/replay_static.py](../../src/legacy/experiments/hands_c1_multi_note_safe_pose_feasibility_r4/replay_static.py)
- [experiments/hands_c1_multi_note_safe_pose_feasibility_r4/session.py](../../src/legacy/experiments/hands_c1_multi_note_safe_pose_feasibility_r4/session.py)
- [experiments/hands_c1_multi_note_safe_pose_feasibility_r4/start_mcp.py](../../src/legacy/experiments/hands_c1_multi_note_safe_pose_feasibility_r4/start_mcp.py)
- [experiments/hands_c1_multi_note_safe_pose_feasibility_r4/verify_and_context.py](../../src/legacy/experiments/hands_c1_multi_note_safe_pose_feasibility_r4/verify_and_context.py)

## 输入、输出与大型证据

该目录原始成员 74 项；拟公开身份记录 60 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
