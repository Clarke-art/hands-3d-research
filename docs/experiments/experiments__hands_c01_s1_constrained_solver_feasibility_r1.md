# experiments/hands_c01_s1_constrained_solver_feasibility_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> | 尝试 | 优化收敛/状态 | nit | 求解秒 | 原始接触布尔 | 原距离mm | 目标侵入mm | 非目标/非指腹mm | 指面交叉对 | E5高度mm |

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_c01_s1_constrained_solver_feasibility_r1/FINAL_RECOMMENDATION.md)

> 1mm固定活动池尚未覆盖全部允许运动域，不能单独称为全局等价碰撞约束。后续技术关注应集中“活动面覆盖与每步闭合距离证明/更新”，不继续无目标调残差。没有证据要求改Rig或直接迁往未运行外部方案。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_c01_s1_constrained_solver_feasibility_r1/FINAL_RECOMMENDATION.md)

## 技术路线

> **A — 保留现有求解器体系，采用第二次已验证的约束式局部改造。** 保留原冻结FK/蒙皮/oracle和SciPy环境；几何条件迁入SLSQP显式ineq。第一次固定键平面/跨姿态固定轴表示不保留。全部候选DESIGN_PROVISIONAL。**STOP — HUMAN REVIEW**。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_c01_s1_constrained_solver_feasibility_r1/FINAL_RECOMMENDATION.md)

> | 尝试 | 优化收敛/状态 | nit | 求解秒 | 原始接触布尔 | 原距离mm | 目标侵入mm | 非目标/非指腹mm | 指面交叉对 | E5高度mm |

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_c01_s1_constrained_solver_feasibility_r1/FINAL_RECOMMENDATION.md)

## 测试结论

> **CONSTRAINED_S1_PASS / STOP — HUMAN REVIEW。** S1时间2.527855s，四张实际Blender求值网格1280×720静帧。源左手在边缘作为继承参考，不代表本轮左手实验。没有视频。

出处：[HUMAN_VISUAL_REVIEW.md](../research/experiments/hands_c01_s1_constrained_solver_feasibility_r1/HUMAN_VISUAL_REVIEW.md)

> 原真实接触false、交叉0、原clip距离0.0553108877mm；完整键面欧氏距离0.0453407288mm即使小于0.05mm仍不能通过。实际侵入/交叉0、优化线搜索失败，不追认为PASS。

出处：[HUMAN_VISUAL_REVIEW.md](../research/experiments/hands_c01_s1_constrained_solver_feasibility_r1/HUMAN_VISUAL_REVIEW.md)

## 失败原因与证据边界

> - 预算停止已确认；局部停滞/目标冲突可能，但缺少旧活动集和梯度谱，不能宣称根因已确定。

出处：[S1_SOLVER_ROOT_CAUSE.md](../research/experiments/hands_c01_s1_constrained_solver_feasibility_r1/S1_SOLVER_ROOT_CAUSE.md)

## 后续建议

> 1mm固定活动池尚未覆盖全部允许运动域，不能单独称为全局等价碰撞约束。后续技术关注应集中“活动面覆盖与每步闭合距离证明/更新”，不继续无目标调残差。没有证据要求改Rig或直接迁往未运行外部方案。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_c01_s1_constrained_solver_feasibility_r1/FINAL_RECOMMENDATION.md)

> 本轮未明显变慢，但22.8s单个近可行姿态不足以证明整曲产品性能。解析皮肤Jacobian/活动池更新属于后续工程成本，本轮不自动开展。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_c01_s1_constrained_solver_feasibility_r1/FINAL_RECOMMENDATION.md)

## 原报告与关键代码

- [experiments/hands_c01_s1_constrained_solver_feasibility_r1/HUMAN_VISUAL_REVIEW.md](../research/experiments/hands_c01_s1_constrained_solver_feasibility_r1/HUMAN_VISUAL_REVIEW.md)
- [experiments/hands_c01_s1_constrained_solver_feasibility_r1/FINAL_RECOMMENDATION.md](../research/experiments/hands_c01_s1_constrained_solver_feasibility_r1/FINAL_RECOMMENDATION.md)
- [experiments/hands_c01_s1_constrained_solver_feasibility_r1/S1_SOLVER_ROOT_CAUSE.md](../research/experiments/hands_c01_s1_constrained_solver_feasibility_r1/S1_SOLVER_ROOT_CAUSE.md)
- [experiments/hands_c01_s1_constrained_solver_feasibility_r1/CONSTRAINED_SOLVER_DESIGN.md](../research/experiments/hands_c01_s1_constrained_solver_feasibility_r1/CONSTRAINED_SOLVER_DESIGN.md)
- [experiments/hands_c01_s1_constrained_solver_feasibility_r1/EXISTING_SOLVER_COMPARISON.md](../research/experiments/hands_c01_s1_constrained_solver_feasibility_r1/EXISTING_SOLVER_COMPARISON.md)
- [experiments/hands_c01_s1_constrained_solver_feasibility_r1/finalize_policy.py](../../src/legacy/experiments/hands_c01_s1_constrained_solver_feasibility_r1/finalize_policy.py)
- [experiments/hands_c01_s1_constrained_solver_feasibility_r1/prepare.py](../../src/legacy/experiments/hands_c01_s1_constrained_solver_feasibility_r1/prepare.py)
- [experiments/hands_c01_s1_constrained_solver_feasibility_r1/solve_s1.py](../../src/legacy/experiments/hands_c01_s1_constrained_solver_feasibility_r1/solve_s1.py)
- [experiments/hands_c01_s1_constrained_solver_feasibility_r1/solve_s1_attempt1.py](../../src/legacy/experiments/hands_c01_s1_constrained_solver_feasibility_r1/solve_s1_attempt1.py)
- [experiments/hands_c01_s1_constrained_solver_feasibility_r1/supplement_measurements.py](../../src/legacy/experiments/hands_c01_s1_constrained_solver_feasibility_r1/supplement_measurements.py)
- [experiments/hands_c01_s1_constrained_solver_feasibility_r1/verify_actual.py](../../src/legacy/experiments/hands_c01_s1_constrained_solver_feasibility_r1/verify_actual.py)
- [experiments/hands_c01_s1_constrained_solver_feasibility_r1/verify_delivery.py](../../src/legacy/experiments/hands_c01_s1_constrained_solver_feasibility_r1/verify_delivery.py)
- [experiments/hands_c01_s1_constrained_solver_feasibility_r1/write_reports.py](../../src/legacy/experiments/hands_c01_s1_constrained_solver_feasibility_r1/write_reports.py)

## 输入、输出与大型证据

该目录原始成员 52 项；拟公开身份记录 38 项。
- `experiments/hands_c01_s1_constrained_solver_feasibility_r1/S1_CONSTRAINED_DIAGNOSTIC_R1.blend` → `hands-research-r1-selected-008.zip` / `payload/experiments/hands_c01_s1_constrained_solver_feasibility_r1/S1_CONSTRAINED_DIAGNOSTIC_R1.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
