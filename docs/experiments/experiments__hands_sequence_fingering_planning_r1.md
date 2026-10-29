# experiments/hands_sequence_fingering_planning_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> score_paths.mjs使用官方predictFingerings和官方状态更新。每条完整路径使用全新内存notes，最初都没有finger；包装session.run记录并执行真实ONNX，然后只为**当前**音设置该路径的finger。官方接口在await run后读取当前finger，并据此更新每指历史；所有未来音始终未知。输入tokens的26个finger_hint逐个验证均为-1。这里的临时finger是已生成路径的评分复放，不是生成阶段提供的目标答案，也未回写任何源文件。

出处：[SEQUENCE_PLANNING_FEASIBILITY.md](../research/experiments/hands_sequence_fingering_planning_r1/SEQUENCE_PLANNING_FEASIBILITY.md)

> 1. 模型候选评分：已按路径条件正确计算，作为独立复评；未进入PianoPlayer优化目标。

出处：[SEQUENCE_PLANNING_FEASIBILITY.md](../research/experiments/hands_sequence_fingering_planning_r1/SEQUENCE_PLANNING_FEASIBILITY.md)

## 技术路线

> | 1. 有没有真正可复用的序列级开源算法？ | 有。PianoPlayer的MIT核心实际跑通约5.637秒，无需训练。作者HMM有完整Viterbi和已训练参数，但C++环境及授权未解决；ArLSTM/ArGNN有真实Beam代码与公开权重，未在本轮运行。 |

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_sequence_fingering_planning_r1/FINAL_RECOMMENDATION.md)

> | 3. 相比逐音贪心有实质改善吗？ | 在本轮近似成本与结构上有：右手整段作者成本5.229089→2.902030，非拇指逆序1→0，重复换指减少；神经NLL反而6.328477→7.001293，模型并不更偏爱它。近似成本来自所选算法，不是独立教师评测。 |

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_sequence_fingering_planning_r1/FINAL_RECOMMENDATION.md)

## 测试结论

> **SEQUENCE_POC_PASS（技术候选门禁）**。现成PianoPlayer序列前瞻搜索已真实运行，产生一套完整23音候选，身份/46事件约束通过，没有已知明显持音硬冲突。全部仍为DESIGN_PROVISIONAL，没有钢琴教师认证、掌腕物理可行性证明或商业教材接入授权。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_sequence_fingering_planning_r1/FINAL_RECOMMENDATION.md)

> 本轮选用的是“现成演奏成本搜索生成＋Lumikey条件复评＋事件/跨度/上下文检查”，不是模型与动作成本的联合Beam或全曲最短路径。真实评分保留分项，未任意混成总分，也未为得到PASS改指。仅保留1套新完整候选，旧/贪心是对照而非额外交付候选。合理穿指仍可能存在，PianoPlayer部分剪枝不应推广成统一禁令。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_sequence_fingering_planning_r1/FINAL_RECOMMENDATION.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

> | 7. 还缺什么条件？ | 教师认可、适合冻结手型的跨度/掌腕轨迹验证、真实释放与复位、完整后续乐句优化、跨曲/复音回归，以及Lumikey权重和训练来源的明确商业授权。 |

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_sequence_fingering_planning_r1/FINAL_RECOMMENDATION.md)

> 交付：EXISTING_ALGORITHM_REVIEW.md、SEQUENCE_PLANNING_FEASIBILITY.md、SEQUENCE_CANDIDATES.json、ALL_23_SEQUENCE_COMPARISON.md及本报告。额外保留原始PianoPlayer输出、三路径逐音条件logits、CPU profiles、原始源码/许可、真实下一乐句上下文和保护哈希。现有Hands/Piano、旧实验、冻结资产、MIDI、音频、琴键和旧候选未修改。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_sequence_fingering_planning_r1/FINAL_RECOMMENDATION.md)

## 原报告与关键代码

- [experiments/hands_sequence_fingering_planning_r1/FINAL_RECOMMENDATION.md](../research/experiments/hands_sequence_fingering_planning_r1/FINAL_RECOMMENDATION.md)
- [experiments/hands_sequence_fingering_planning_r1/SEQUENCE_PLANNING_FEASIBILITY.md](../research/experiments/hands_sequence_fingering_planning_r1/SEQUENCE_PLANNING_FEASIBILITY.md)
- [experiments/hands_sequence_fingering_planning_r1/EXISTING_ALGORITHM_REVIEW.md](../research/experiments/hands_sequence_fingering_planning_r1/EXISTING_ALGORITHM_REVIEW.md)
- [experiments/hands_sequence_fingering_planning_r1/ALL_23_SEQUENCE_COMPARISON.md](../research/experiments/hands_sequence_fingering_planning_r1/ALL_23_SEQUENCE_COMPARISON.md)
- [experiments/hands_sequence_fingering_planning_r1/collect_existing.py](../../src/legacy/experiments/hands_sequence_fingering_planning_r1/collect_existing.py)
- [experiments/hands_sequence_fingering_planning_r1/evaluate_sequence.py](../../src/legacy/experiments/hands_sequence_fingering_planning_r1/evaluate_sequence.py)
- [experiments/hands_sequence_fingering_planning_r1/fetch_more.py](../../src/legacy/experiments/hands_sequence_fingering_planning_r1/fetch_more.py)
- [experiments/hands_sequence_fingering_planning_r1/run_pianoplayer.py](../../src/legacy/experiments/hands_sequence_fingering_planning_r1/run_pianoplayer.py)
- [experiments/hands_sequence_fingering_planning_r1/score_paths.mjs](../../src/legacy/experiments/hands_sequence_fingering_planning_r1/score_paths.mjs)
- [experiments/hands_sequence_fingering_planning_r1/verify_delivery.py](../../src/legacy/experiments/hands_sequence_fingering_planning_r1/verify_delivery.py)
- [experiments/hands_sequence_fingering_planning_r1/verify_inputs.py](../../src/legacy/experiments/hands_sequence_fingering_planning_r1/verify_inputs.py)
- [experiments/hands_sequence_fingering_planning_r1/verify_source_revision.py](../../src/legacy/experiments/hands_sequence_fingering_planning_r1/verify_source_revision.py)
- [experiments/hands_sequence_fingering_planning_r1/write_reports.py](../../src/legacy/experiments/hands_sequence_fingering_planning_r1/write_reports.py)

## 输入、输出与大型证据

该目录原始成员 121 项；拟公开身份记录 23 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
