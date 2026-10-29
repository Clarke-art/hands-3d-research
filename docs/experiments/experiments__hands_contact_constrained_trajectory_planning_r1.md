# experiments/hands_contact_constrained_trajectory_planning_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 最大目标侵入0.115401647mm，非目标/错误区域0.196891178mm；非相邻指面交叉0，关节参考族/轴/域在样本处通过，中指/无名指最小精确间隙3.056809mm。这些分项不能替代失败的接触门禁或Human自然度认可。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_contact_constrained_trajectory_planning_r1/FINAL_RECOMMENDATION.md)

> 本轮有实际前进：把接触、几何和相邻时间运动关系写成同一个联合时间问题，接通CasADi符号导数/IPOPT及真实Blender重放。没有从“可行静态姿态集合”前进到“已经验证、真正可复用的接触约束连续运动规划方法”，因为实际输出仍失去E5接触。

出处：[PRODUCT_ROUTE_REVIEW.md](../research/experiments/hands_contact_constrained_trajectory_planning_r1/PRODUCT_ROUTE_REVIEW.md)

## 技术路线

> **B：现有接触合同及FK/蒙皮有效，成熟外部方法已执行，但未显示充分优势。** 结论为CONTACT_PATH_NOT_FOUND_WITHIN_BUDGET。不继续扩大窗口或求解次数。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_contact_constrained_trajectory_planning_r1/FINAL_RECOMMENDATION.md)

> **是否已经得到真正可复用的接触约束连续规划方法？尚未。** 已接通联合时间外部优化，但主要卡在接触保持与非收敛；约170秒用于34次约束Jacobian评估。没有证据把失败归因于人体、C01或固定MIDI时长。下一项唯一关键工作是同输入下的稀疏接触导数/可行性恢复接口验证，不是再修静态节点。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_contact_constrained_trajectory_planning_r1/FINAL_RECOMMENDATION.md)

## 测试结论

> **B：现有接触合同及FK/蒙皮有效，成熟外部方法已执行，但未显示充分优势。** 结论为CONTACT_PATH_NOT_FOUND_WITHIN_BUDGET。不继续扩大窗口或求解次数。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_contact_constrained_trajectory_planning_r1/FINAL_RECOMMENDATION.md)

> |LOCAL_BOUNDARY_SAMPLED_PASS|未通过|

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_contact_constrained_trajectory_planning_r1/FINAL_RECOMMENDATION.md)

## 失败原因与证据边界

> 唯一局部候选覆盖2.913092667–2.938092667秒。IPOPT31次可核实迭代后超时，未收敛。31条实际Blender记录包含30个时间采样与1个边界左极限；接触在12条记录失败，首次采样失败2.926634333秒，之前通过点为2.925592667秒（不是声称精确失效发生时刻）。最终E5指腹悬空2.615577760mm，保留原始布尔，不四舍五入改判。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_contact_constrained_trajectory_planning_r1/FINAL_RECOMMENDATION.md)

> 具体卡点：接触等式残差未消除、IPOPT在180秒名义求解预算（实际182.112秒）内未收敛，导数评估约170秒占主要成本。源码图/导数组织是已定位的性能环节；完整皮肤输出及跨时刻依赖可能放大计算，是待剖析的原因，不能未经profile称已确定内部根因。固定碰撞证书、局部参考族、初始常值曲线和工程动力学限值是否限制可行性，均未排除。

出处：[PRODUCT_ROUTE_REVIEW.md](../research/experiments/hands_contact_constrained_trajectory_planning_r1/PRODUCT_ROUTE_REVIEW.md)

## 后续建议

> **是否已经得到真正可复用的接触约束连续规划方法？尚未。** 已接通联合时间外部优化，但主要卡在接触保持与非收敛；约170秒用于34次约束Jacobian评估。没有证据把失败归因于人体、C01或固定MIDI时长。下一项唯一关键工作是同输入下的稀疏接触导数/可行性恢复接口验证，不是再修静态节点。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_contact_constrained_trajectory_planning_r1/FINAL_RECOMMENDATION.md)

> 唯一最小技术缺口：在同一冻结Rig上，使多时刻接触约束的稀疏导数/可行性恢复能以可控成本消除移动键面的接触残差，并通过真实重放。下一轮应先核实小规模稀疏Jacobian及接触可行性恢复接口，不再次修补孤立静态节点，不更换一批外部工具，也不直接扩大到整段MIDI。当前没有足够证据选择OMPL或TrajOpt替换生产主线。

出处：[PRODUCT_ROUTE_REVIEW.md](../research/experiments/hands_contact_constrained_trajectory_planning_r1/PRODUCT_ROUTE_REVIEW.md)

## 原报告与关键代码

- [experiments/hands_contact_constrained_trajectory_planning_r1/FINAL_RECOMMENDATION.md](../research/experiments/hands_contact_constrained_trajectory_planning_r1/FINAL_RECOMMENDATION.md)
- [experiments/hands_contact_constrained_trajectory_planning_r1/PRODUCT_ROUTE_REVIEW.md](../research/experiments/hands_contact_constrained_trajectory_planning_r1/PRODUCT_ROUTE_REVIEW.md)
- [experiments/hands_contact_constrained_trajectory_planning_r1/PLANNER_ADAPTER_EXECUTION.md](../research/experiments/hands_contact_constrained_trajectory_planning_r1/PLANNER_ADAPTER_EXECUTION.md)
- [experiments/hands_contact_constrained_trajectory_planning_r1/STAGED_CONTACT_TIME_REVIEW.md](../research/experiments/hands_contact_constrained_trajectory_planning_r1/STAGED_CONTACT_TIME_REVIEW.md)
- [experiments/hands_contact_constrained_trajectory_planning_r1/TRAJECTORY_PLANNER_SOURCE_REVIEW.md](../research/experiments/hands_contact_constrained_trajectory_planning_r1/TRAJECTORY_PLANNER_SOURCE_REVIEW.md)
- [experiments/hands_contact_constrained_trajectory_planning_r1/benchmark.py](../../src/legacy/experiments/hands_contact_constrained_trajectory_planning_r1/benchmark.py)
- [experiments/hands_contact_constrained_trajectory_planning_r1/blender_verify.py](../../src/legacy/experiments/hands_contact_constrained_trajectory_planning_r1/blender_verify.py)
- [experiments/hands_contact_constrained_trajectory_planning_r1/boundary_rules.py](../../src/legacy/experiments/hands_contact_constrained_trajectory_planning_r1/boundary_rules.py)
- [experiments/hands_contact_constrained_trajectory_planning_r1/build_chart.py](../../src/legacy/experiments/hands_contact_constrained_trajectory_planning_r1/build_chart.py)
- [experiments/hands_contact_constrained_trajectory_planning_r1/extract_keys.py](../../src/legacy/experiments/hands_contact_constrained_trajectory_planning_r1/extract_keys.py)
- [experiments/hands_contact_constrained_trajectory_planning_r1/fetch_sources.py](../../src/legacy/experiments/hands_contact_constrained_trajectory_planning_r1/fetch_sources.py)
- [experiments/hands_contact_constrained_trajectory_planning_r1/fetch_trajectory_sources.py](../../src/legacy/experiments/hands_contact_constrained_trajectory_planning_r1/fetch_trajectory_sources.py)
- [experiments/hands_contact_constrained_trajectory_planning_r1/finish_source_metadata.py](../../src/legacy/experiments/hands_contact_constrained_trajectory_planning_r1/finish_source_metadata.py)
- [experiments/hands_contact_constrained_trajectory_planning_r1/prepare.py](../../src/legacy/experiments/hands_contact_constrained_trajectory_planning_r1/prepare.py)
- [experiments/hands_contact_constrained_trajectory_planning_r1/prepare_actual_validation.py](../../src/legacy/experiments/hands_contact_constrained_trajectory_planning_r1/prepare_actual_validation.py)
- [experiments/hands_contact_constrained_trajectory_planning_r1/solve_trajectory.py](../../src/legacy/experiments/hands_contact_constrained_trajectory_planning_r1/solve_trajectory.py)
- [experiments/hands_contact_constrained_trajectory_planning_r1/solve_trajectory_mx_build.py](../../src/legacy/experiments/hands_contact_constrained_trajectory_planning_r1/solve_trajectory_mx_build.py)

## 输入、输出与大型证据

该目录原始成员 2532 项；拟公开身份记录 79 项。
- `experiments/hands_contact_constrained_trajectory_planning_r1/FROZEN_SKIN_SYMBOLIC.casadi` → `hands-research-r1-selected-011.zip` / `payload/experiments/hands_contact_constrained_trajectory_planning_r1/FROZEN_SKIN_SYMBOLIC.casadi`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
