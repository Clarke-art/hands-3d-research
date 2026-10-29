# experiments/hands_p3_whole_hand_layout_feasibility_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> | **B：是否兼容R08小指、R09拇指、R10食指？** | **未证实。** 十阶段实际使用同一共享掌腕、真实五指模型及交接／释放任务；保存初始化在两个R08点仅marker接触合格，但有邻键回退；R09、R10失触。没有合法联合布局或准备范围。 |

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_p3_whole_hand_layout_feasibility_r1/FINAL_RECOMMENDATION.md)

> 复用A2/C1的EventCoordinator、FK、稀疏有界SciPy least_squares及冻结native FK/LBS与拇指修正形状。十个事件阶段共同拥有**一个掌腕状态**；各阶段有五指协调角度，共享六个事件的合法触点XY。包含R08下沉、R09前180/75ms准备、R09/R10准确ON交接及各音下沉35ms点。活动、释放跟随、即将触键与闲置指都进入现有任务／键体筛选。接触使用真实权重对应的skin pad，而非仅骨骼marker。没有新Rig自由度、避障框架或运动轨迹。

出处：[P3_LAYOUT_FEASIBILITY.md](../research/experiments/hands_p3_whole_hand_layout_feasibility_r1/P3_LAYOUT_FEASIBILITY.md)

## 技术路线

> 本轮未得到可审查的合法P3整手布局，也没有连续演奏PASS。唯一求解因终态导出实现错误丢失结果；后续只检查原批同一个初始化，没有重跑。该初始化存在真实失触与新增键体侵入。当前不建议授权P3短动态生成；这不是P3或人体不可演奏的结论，也不是复杂整手优化器必需的证据。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_p3_whole_hand_layout_feasibility_r1/FINAL_RECOMMENDATION.md)

> | **A：能否克服原C5拇指缺口？** | **UNKNOWN。** 原固定上游／掌腕最高8.70mm条件缺口仍成立；允许掌腕协调后的求解终态没有保存。仅初始公共根下拇指C5仍失触，不能当P3最佳布局或全局下界。 |

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_p3_whole_hand_layout_feasibility_r1/FINAL_RECOMMENDATION.md)

## 测试结论

> 本轮未得到可审查的合法P3整手布局，也没有连续演奏PASS。唯一求解因终态导出实现错误丢失结果；后续只检查原批同一个初始化，没有重跑。该初始化存在真实失触与新增键体侵入。当前不建议授权P3短动态生成；这不是P3或人体不可演奏的结论，也不是复杂整手优化器必需的证据。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_p3_whole_hand_layout_feasibility_r1/FINAL_RECOMMENDATION.md)

> 详情见`P3_LAYOUT_FEASIBILITY.md`（链接见原报告）及`TEMPORAL_AND_COLLISION_RISK.md`（链接见原报告）。正式MIDI上下文在`EVENT_CONTEXT.json`（链接见原报告）；真实静态对照在`BLENDER_STATIC_DIAGNOSTICS.json`（链接见原报告）；导出失败在`solve.log`（链接见原报告）及`EXPORT_FAILURE_RECEIPT.json`（链接见原报告）。必须连同失败日志审核，不能只抽取两点R08 marker PASS。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_p3_whole_hand_layout_feasibility_r1/FINAL_RECOMMENDATION.md)

## 失败原因与证据边界

> 详情见`P3_LAYOUT_FEASIBILITY.md`（链接见原报告）及`TEMPORAL_AND_COLLISION_RISK.md`（链接见原报告）。正式MIDI上下文在`EVENT_CONTEXT.json`（链接见原报告）；真实静态对照在`BLENDER_STATIC_DIAGNOSTICS.json`（链接见原报告）；导出失败在`solve.log`（链接见原报告）及`EXPORT_FAILURE_RECEIPT.json`（链接见原报告）。必须连同失败日志审核，不能只抽取两点R08 marker PASS。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_p3_whole_hand_layout_feasibility_r1/FINAL_RECOMMENDATION.md)

> 本轮没有保留下可验收的P3联合布局。唯一一批数值求解实际进入并执行了least_squares，但随后在接触诊断导出处发生`NameError: surface_metrics`；终态尚未落盘，无法恢复，不能报告其收敛状态、接触成绩或失败原因。遵守一批上限，没有重跑。后续真实Blender检查的是**同一批事前确定的初始布局**，不是求解终态，也不是额外候选搜索。证据不足主要来自这一实现失败，不能据此给P3作全局负面判决。

出处：[P3_LAYOUT_FEASIBILITY.md](../research/experiments/hands_p3_whole_hand_layout_feasibility_r1/P3_LAYOUT_FEASIBILITY.md)

## 后续建议

> 本轮未得到可审查的合法P3整手布局，也没有连续演奏PASS。唯一求解因终态导出实现错误丢失结果；后续只检查原批同一个初始化，没有重跑。该初始化存在真实失触与新增键体侵入。当前不建议授权P3短动态生成；这不是P3或人体不可演奏的结论，也不是复杂整手优化器必需的证据。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_p3_whole_hand_layout_feasibility_r1/FINAL_RECOMMENDATION.md)

> | **C：后续E5/F♯5/G5能否保持合理手型？** | **UNKNOWN。** 保存初始化后三音均失触，F♯5处公共根较原参考差49.821mm。它没有完成P3五指协调，不能外推所有协调布局。 |

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_p3_whole_hand_layout_feasibility_r1/FINAL_RECOMMENDATION.md)

## 原报告与关键代码

- [experiments/hands_p3_whole_hand_layout_feasibility_r1/FINAL_RECOMMENDATION.md](../research/experiments/hands_p3_whole_hand_layout_feasibility_r1/FINAL_RECOMMENDATION.md)
- [experiments/hands_p3_whole_hand_layout_feasibility_r1/P3_LAYOUT_FEASIBILITY.md](../research/experiments/hands_p3_whole_hand_layout_feasibility_r1/P3_LAYOUT_FEASIBILITY.md)
- [experiments/hands_p3_whole_hand_layout_feasibility_r1/TEMPORAL_AND_COLLISION_RISK.md](../research/experiments/hands_p3_whole_hand_layout_feasibility_r1/TEMPORAL_AND_COLLISION_RISK.md)
- [experiments/hands_p3_whole_hand_layout_feasibility_r1/actual.py](../../src/legacy/experiments/hands_p3_whole_hand_layout_feasibility_r1/actual.py)
- [experiments/hands_p3_whole_hand_layout_feasibility_r1/close.py](../../src/legacy/experiments/hands_p3_whole_hand_layout_feasibility_r1/close.py)
- [experiments/hands_p3_whole_hand_layout_feasibility_r1/prepare.py](../../src/legacy/experiments/hands_p3_whole_hand_layout_feasibility_r1/prepare.py)
- [experiments/hands_p3_whole_hand_layout_feasibility_r1/recover_initial.py](../../src/legacy/experiments/hands_p3_whole_hand_layout_feasibility_r1/recover_initial.py)
- [experiments/hands_p3_whole_hand_layout_feasibility_r1/run_stage.py](../../src/legacy/experiments/hands_p3_whole_hand_layout_feasibility_r1/run_stage.py)
- [experiments/hands_p3_whole_hand_layout_feasibility_r1/solve.py](../../src/legacy/experiments/hands_p3_whole_hand_layout_feasibility_r1/solve.py)

## 输入、输出与大型证据

该目录原始成员 35 项；拟公开身份记录 26 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
