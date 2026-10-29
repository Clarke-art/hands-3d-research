# experiments/hands_long_context_hand_motion_architecture_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> - 上方清障：在同一2.869521666667s风险时刻通过全部原门禁；整指对实体顶面的最小投影净空4.349362mm，错误区域侵入0，目标侵入0.003345mm，指面自交0。指法、MIDI、琴键Action、Rig和自然参考族不变。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_long_context_hand_motion_architecture_r1/FINAL_RECOMMENDATION.md)

> HandMotionIntent已定义，6类原MIDI事件合同检查和5类拒绝检查通过。独立适配器实际读取序列化意图，生成与真实Blender验收控制/全状态相同的候选，差0。真实执行范围仅右手指定准备指的两个空间原语；双手/和弦、连续跟踪、通用先验重定向不授予执行PASS。下一轮最小任务是高层清障走廊与接触IK的一项受控衔接，携带多音符上下文、下降截止和失败反馈；不是再增加旧局部节点/毫秒/迭代。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_long_context_hand_motion_architecture_r1/FINAL_RECOMMENDATION.md)

## 技术路线

> 这不是完整入口PASS。新状态到旧共同边界的必要恢复时间115.490ms，剩余仅51.904ms；固定边界连接冲突，其他边界集合未被排除。由此得到明确高层需求：抬指和过障碍须更早完成，给下降/触键留足真实时间，不在碰撞末端才求解。R06→R07仍未验证，Human自然度仍待审，任何未经验证的早期入口不可当锚点。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_long_context_hand_motion_architecture_r1/FINAL_RECOMMENDATION.md)

> 新数值适配保守记账7.423000s，优化器0次，最多两种高层候选；含一次输入加载启动错误及修复、同两个状态的序列化接口重放。未制作正式Action、Blend、视频、批量渲染或整曲求解。八项交付齐全，停止待Human审核，不自动开始完整25ms、428.571ms、B02、23音双手动画或数字教材生产。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_long_context_hand_motion_architecture_r1/FINAL_RECOMMENDATION.md)

## 测试结论

> - 前方绕行：G4接触失败，最大其他键侵入6.332802mm，保留FAIL。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_long_context_hand_motion_architecture_r1/FINAL_RECOMMENDATION.md)

> 这不是完整入口PASS。新状态到旧共同边界的必要恢复时间115.490ms，剩余仅51.904ms；固定边界连接冲突，其他边界集合未被排除。由此得到明确高层需求：抬指和过障碍须更早完成，给下降/触键留足真实时间，不在碰撞末端才求解。R06→R07仍未验证，Human自然度仍待审，任何未经验证的早期入口不可当锚点。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_long_context_hand_motion_architecture_r1/FINAL_RECOMMENDATION.md)

## 失败原因与证据边界

> 原失败只读核实：2.527855–2.777855s的40样本前缀通过，腕移15.419mm；2.778896666667s起中指远端皮肤进入D#5，最深3.872186mm，85条中45失败，E5后续接触失效。全部原始数据、实体/三角/材料见证与源码SHA保持可追溯，没有重跑旧局部IK或扩大旧2ms/25ms片段。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_long_context_hand_motion_architecture_r1/FINAL_RECOMMENDATION.md)

> 本轮只读重算85条原始Blender记录（78规则/边界/风险样本+7补采样），确认45条失败；未重跑旧求解。B2从2.527855s开始，40个通过点覆盖至2.777855s，腕移15.418873mm；中指到E5距离27.667432→16.331513mm。首个失败2.778896666667s，错误区侵入0.254667086mm。最大失败在2.869521666667s，为3.872185949mm。E5在2.928717666667s和2.936009333333s接触失败。原数据及SHA见 BASELINE_FAILURE_READONLY_CHECK.json；250ms前缀仍是有限采样证据，不是连续无碰撞定理。

出处：[BASELINE_FAILURE_AND_PLANNING_REQUIREMENTS.md](../research/experiments/hands_long_context_hand_motion_architecture_r1/BASELINE_FAILURE_AND_PLANNING_REQUIREMENTS.md)

## 后续建议

> **已找到更有产品化推进价值的架构与真实接口证据：以多音符时序和实际几何决定清障/下降阶段，再由现有接触IK执行。** 推荐下一阶段只实施A。动作先验的入口保留，但当前核查资料没有完整商用与冻结Rig适配资格；本轮未运行任何外部人体生成器、训练或导入动作数据。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_long_context_hand_motion_architecture_r1/FINAL_RECOMMENDATION.md)

> 原失败只读核实：2.527855–2.777855s的40样本前缀通过，腕移15.419mm；2.778896666667s起中指远端皮肤进入D#5，最深3.872186mm，85条中45失败，E5后续接触失效。全部原始数据、实体/三角/材料见证与源码SHA保持可追溯，没有重跑旧局部IK或扩大旧2ms/25ms片段。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_long_context_hand_motion_architecture_r1/FINAL_RECOMMENDATION.md)

## 原报告与关键代码

- [experiments/hands_long_context_hand_motion_architecture_r1/FINAL_RECOMMENDATION.md](../research/experiments/hands_long_context_hand_motion_architecture_r1/FINAL_RECOMMENDATION.md)
- [experiments/hands_long_context_hand_motion_architecture_r1/MOTION_PRIOR_SOURCE_AUDIT.md](../research/experiments/hands_long_context_hand_motion_architecture_r1/MOTION_PRIOR_SOURCE_AUDIT.md)
- [experiments/hands_long_context_hand_motion_architecture_r1/PROTECTION_CONCURRENCY_AUDIT.md](../research/experiments/hands_long_context_hand_motion_architecture_r1/PROTECTION_CONCURRENCY_AUDIT.md)
- [experiments/hands_long_context_hand_motion_architecture_r1/PRODUCT_ARCHITECTURE_DECISION.md](../research/experiments/hands_long_context_hand_motion_architecture_r1/PRODUCT_ARCHITECTURE_DECISION.md)
- [experiments/hands_long_context_hand_motion_architecture_r1/LONG_CONTEXT_PLANNER_COMPARISON.md](../research/experiments/hands_long_context_hand_motion_architecture_r1/LONG_CONTEXT_PLANNER_COMPARISON.md)
- [experiments/hands_long_context_hand_motion_architecture_r1/BASELINE_FAILURE_AND_PLANNING_REQUIREMENTS.md](../research/experiments/hands_long_context_hand_motion_architecture_r1/BASELINE_FAILURE_AND_PLANNING_REQUIREMENTS.md)
- [experiments/hands_long_context_hand_motion_architecture_r1/analyze_failure_and_propose.py](../../src/legacy/experiments/hands_long_context_hand_motion_architecture_r1/analyze_failure_and_propose.py)
- [experiments/hands_long_context_hand_motion_architecture_r1/define_and_check_contract.py](../../src/legacy/experiments/hands_long_context_hand_motion_architecture_r1/define_and_check_contract.py)
- [experiments/hands_long_context_hand_motion_architecture_r1/fetch_small_sources.py](../../src/legacy/experiments/hands_long_context_hand_motion_architecture_r1/fetch_small_sources.py)
- [experiments/hands_long_context_hand_motion_architecture_r1/finalize_clearance_facts.py](../../src/legacy/experiments/hands_long_context_hand_motion_architecture_r1/finalize_clearance_facts.py)
- [experiments/hands_long_context_hand_motion_architecture_r1/final_source_metadata.py](../../src/legacy/experiments/hands_long_context_hand_motion_architecture_r1/final_source_metadata.py)
- [experiments/hands_long_context_hand_motion_architecture_r1/intent_rig_adapter.py](../../src/legacy/experiments/hands_long_context_hand_motion_architecture_r1/intent_rig_adapter.py)
- [experiments/hands_long_context_hand_motion_architecture_r1/prepare_architecture_experiment.py](../../src/legacy/experiments/hands_long_context_hand_motion_architecture_r1/prepare_architecture_experiment.py)
- [experiments/hands_long_context_hand_motion_architecture_r1/supplement_source_audit.py](../../src/legacy/experiments/hands_long_context_hand_motion_architecture_r1/supplement_source_audit.py)
- [experiments/hands_long_context_hand_motion_architecture_r1/write_architecture_reports.py](../../src/legacy/experiments/hands_long_context_hand_motion_architecture_r1/write_architecture_reports.py)

## 输入、输出与大型证据

该目录原始成员 106 项；拟公开身份记录 34 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
