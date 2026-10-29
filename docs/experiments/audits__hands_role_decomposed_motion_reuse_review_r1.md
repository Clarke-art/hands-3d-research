# audits/hands_role_decomposed_motion_reuse_review_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 只读取指定原C1 R04 C5(4)→R05 D5(5)及其已有前后上下文；不以整段无穿模为提取信息前提。上一轮的真实240Hz＋事件采样原样保留：活动pad168点接触PASS，62点中／无名指skin相交、161点非目标键侵入。没有重新求解或更换来源。

出处：[FINAL_TECHNICAL_DECISION.md](../research/audits/hands_role_decomposed_motion_reuse_review_r1/FINAL_TECHNICAL_DECISION.md)

> | 准备指 | 180ms准备、75ms近键下降、目标键和下一次使用时间 | 提前准备须服从当前占据空间；原准备姿态有非目标键侵入，不能原样拼接 |

出处：[FINAL_TECHNICAL_DECISION.md](../research/audits/hands_role_decomposed_motion_reuse_review_r1/FINAL_TECHNICAL_DECISION.md)

## 技术路线

> 本结论不支持“冻结全部活动指关节角，只改释放／闲置指”。已有反例证明这种更强的拆分不能消除所有缺陷。活动特征可复用，活动皮肤姿态必须重新验收。正式方向保持路线C，不恢复P3、B02局部门户或大型全手优化。

出处：[FINAL_TECHNICAL_DECISION.md](../research/audits/hands_role_decomposed_motion_reuse_review_r1/FINAL_TECHNICAL_DECISION.md)

> 只读取指定原C1 R04 C5(4)→R05 D5(5)及其已有前后上下文；不以整段无穿模为提取信息前提。上一轮的真实240Hz＋事件采样原样保留：活动pad168点接触PASS，62点中／无名指skin相交、161点非目标键侵入。没有重新求解或更换来源。

出处：[FINAL_TECHNICAL_DECISION.md](../research/audits/hands_role_decomposed_motion_reuse_review_r1/FINAL_TECHNICAL_DECISION.md)

## 测试结论

> 已有接口与真实运动／蒙皮数据支持一个有限的计算切口：保留活动接触的事件与运动特征，以同一掌腕为共同条件，重新组织其他角色，并允许少量活动指接触保持校正。**值得Human授权一次有明确退出条件的跨事件验证。** 这不是新动作PASS，也不证明已经存在无碰撞重组轨迹。

出处：[FINAL_TECHNICAL_DECISION.md](../research/audits/hands_role_decomposed_motion_reuse_review_r1/FINAL_TECHNICAL_DECISION.md)

> 本结论不支持“冻结全部活动指关节角，只改释放／闲置指”。已有反例证明这种更强的拆分不能消除所有缺陷。活动特征可复用，活动皮肤姿态必须重新验收。正式方向保持路线C，不恢复P3、B02局部门户或大型全手优化。

出处：[FINAL_TECHNICAL_DECISION.md](../research/audits/hands_role_decomposed_motion_reuse_review_r1/FINAL_TECHNICAL_DECISION.md)

## 失败原因与证据边界

> 关键阻断：`ACTIVE_POSE_FREEZE_BLOCKER.json`（链接见原报告）证实小指顶点2731只受LITTLE骨链／WRIST影响，corrective位移为0。若固定活动小指全部角度和根，改变其他手指不可能移动这个E5侵入见证。**至少需要有限的活动姿态／接触位置或共享腕协调余量**，不能只重新安排闲置指。

出处：[FINAL_TECHNICAL_DECISION.md](../research/audits/hands_role_decomposed_motion_reuse_review_r1/FINAL_TECHNICAL_DECISION.md)

> 最小成本判别方式：一次固定表示、一次来源／目标、一个共享腕适配规则、事前有限外层参数与局部接触修正预算；先查源活动皮肤反例是否被方案允许的有限校正覆盖，再查准确MIDI与入口／出口、接触和连续性。仅无明确阻断时生成一个短候选，沿原事件完整检查五指、活动自身邻键及共享皮肤；机器不合格不制成品视频。不进行新旧局部门户试错，不自动放开全时刻根与五指。**本轮只推荐这一次辨别性验证，没有启动或授予后续执行权限。**

出处：[FINAL_TECHNICAL_DECISION.md](../research/audits/hands_role_decomposed_motion_reuse_review_r1/FINAL_TECHNICAL_DECISION.md)

## 后续建议

> | 准备指 | 180ms准备、75ms近键下降、目标键和下一次使用时间 | 提前准备须服从当前占据空间；原准备姿态有非目标键侵入，不能原样拼接 |

出处：[FINAL_TECHNICAL_DECISION.md](../research/audits/hands_role_decomposed_motion_reuse_review_r1/FINAL_TECHNICAL_DECISION.md)

> 角色时间必须来自MIDI与A2优先级，而非音名角度表：本源小指准备从1.455713秒开始；无名指释放为1.635713–1.675713秒；后续拇指准备从1.884284秒开始。活动／释放／准备／闲置由同指前后事件决定，音名与事件号仅用于此次审查身份。

出处：[FINAL_TECHNICAL_DECISION.md](../research/audits/hands_role_decomposed_motion_reuse_review_r1/FINAL_TECHNICAL_DECISION.md)

## 原报告与关键代码

- [audits/hands_role_decomposed_motion_reuse_review_r1/FINAL_TECHNICAL_DECISION.md](../research/audits/hands_role_decomposed_motion_reuse_review_r1/FINAL_TECHNICAL_DECISION.md)
- [audits/hands_role_decomposed_motion_reuse_review_r1/finalize_review.py](../../src/legacy/audits/hands_role_decomposed_motion_reuse_review_r1/finalize_review.py)
- [audits/hands_role_decomposed_motion_reuse_review_r1/review_evidence.py](../../src/legacy/audits/hands_role_decomposed_motion_reuse_review_r1/review_evidence.py)

## 输入、输出与大型证据

该目录原始成员 15 项；拟公开身份记录 11 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
