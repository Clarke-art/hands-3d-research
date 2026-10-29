# experiments/hands_fingering_inference_poc_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 技术接入成本较低：秒转毫秒、已有分手、两份约501KB ONNX、固定Node依赖即可运行。质量限制来自逐音贪心argmax和有限上下文：每音使用每指上次状态及最多20个后续音，没有显式和弦手指唯一约束、全局生物力学求解或整手轨迹。源码将仍持键与刚释放的负/零时间信息压到同一零边界，并不保证重叠可行性。其他曲目仍需要独立的冲突检测与人工复核。四小节末端缺少后续乐句上下文，本次结果不应外推为完整曲目的最优指法。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_fingering_inference_poc_r1/FINAL_RECOMMENDATION.md)

## 技术路线

> **INFERENCE_PARTIAL**。真实预训练CPU推理成功；23音身份、46消息、时间和输出结构全部PASS。由于B02的E5(4)→F♯5(2)有明显非拇指逆序换位风险，不能将结果视作已具备基本动作可行性或教学认可。没有判定它绝对不可弹；风险没有通过动作策略或教师审阅解决。全部预测仍为DESIGN_PROVISIONAL。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_fingering_inference_poc_r1/FINAL_RECOMMENDATION.md)

> 技术接入成本较低：秒转毫秒、已有分手、两份约501KB ONNX、固定Node依赖即可运行。质量限制来自逐音贪心argmax和有限上下文：每音使用每指上次状态及最多20个后续音，没有显式和弦手指唯一约束、全局生物力学求解或整手轨迹。源码将仍持键与刚释放的负/零时间信息压到同一零边界，并不保证重叠可行性。其他曲目仍需要独立的冲突检测与人工复核。四小节末端缺少后续乐句上下文，本次结果不应外推为完整曲目的最优指法。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_fingering_inference_poc_r1/FINAL_RECOMMENDATION.md)

## 测试结论

> **INFERENCE_PARTIAL**。真实预训练CPU推理成功；23音身份、46消息、时间和输出结构全部PASS。由于B02的E5(4)→F♯5(2)有明显非拇指逆序换位风险，不能将结果视作已具备基本动作可行性或教学认可。没有判定它绝对不可弹；风险没有通过动作策略或教师审阅解决。全部预测仍为DESIGN_PROVISIONAL。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_fingering_inference_poc_r1/FINAL_RECOMMENDATION.md)

> 技术接入成本较低：秒转毫秒、已有分手、两份约501KB ONNX、固定Node依赖即可运行。质量限制来自逐音贪心argmax和有限上下文：每音使用每指上次状态及最多20个后续音，没有显式和弦手指唯一约束、全局生物力学求解或整手轨迹。源码将仍持键与刚释放的负/零时间信息压到同一零边界，并不保证重叠可行性。其他曲目仍需要独立的冲突检测与人工复核。四小节末端缺少后续乐句上下文，本次结果不应外推为完整曲目的最优指法。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_fingering_inference_poc_r1/FINAL_RECOMMENDATION.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

> | B02是否产生更值得验证的候选？ | 产生2–3–4–2–3。D5→E5的3→4比旧4→3在局部顺序上更直接，值得验证；E5→F♯5的新4→2将风险转移到下一交接，整段尚不能认定更优。 |

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_fingering_inference_poc_r1/FINAL_RECOMMENDATION.md)

> | 是否值得接入下一阶段3D Hands动作规划？ | 值得作为研究用途候选生成器保留；先对唯一候选作教师审阅并确认授权。当前不建议将未经筛查的finger直接驱动正式3D Hands，不能直接接入商业教材。后续验证必须另行授权。 |

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_fingering_inference_poc_r1/FINAL_RECOMMENDATION.md)

## 原报告与关键代码

- [experiments/hands_fingering_inference_poc_r1/FINAL_RECOMMENDATION.md](../research/experiments/hands_fingering_inference_poc_r1/FINAL_RECOMMENDATION.md)
- [experiments/hands_fingering_inference_poc_r1/B02_FINGERING_ANALYSIS.md](../research/experiments/hands_fingering_inference_poc_r1/B02_FINGERING_ANALYSIS.md)
- [experiments/hands_fingering_inference_poc_r1/MODEL_RUNTIME_AND_LICENSE.md](../research/experiments/hands_fingering_inference_poc_r1/MODEL_RUNTIME_AND_LICENSE.md)
- [experiments/hands_fingering_inference_poc_r1/ALL_23_FINGERING_COMPARISON.md](../research/experiments/hands_fingering_inference_poc_r1/ALL_23_FINGERING_COMPARISON.md)
- [experiments/hands_fingering_inference_poc_r1/adapt_source.py](../../src/legacy/experiments/hands_fingering_inference_poc_r1/adapt_source.py)
- [experiments/hands_fingering_inference_poc_r1/collect_provenance.py](../../src/legacy/experiments/hands_fingering_inference_poc_r1/collect_provenance.py)
- [experiments/hands_fingering_inference_poc_r1/extra_evidence.py](../../src/legacy/experiments/hands_fingering_inference_poc_r1/extra_evidence.py)
- [experiments/hands_fingering_inference_poc_r1/infer_once.mjs](../../src/legacy/experiments/hands_fingering_inference_poc_r1/infer_once.mjs)
- [experiments/hands_fingering_inference_poc_r1/validate_output.py](../../src/legacy/experiments/hands_fingering_inference_poc_r1/validate_output.py)
- [experiments/hands_fingering_inference_poc_r1/verify_delivery.py](../../src/legacy/experiments/hands_fingering_inference_poc_r1/verify_delivery.py)
- [experiments/hands_fingering_inference_poc_r1/write_reports.py](../../src/legacy/experiments/hands_fingering_inference_poc_r1/write_reports.py)

## 输入、输出与大型证据

该目录原始成员 670 项；拟公开身份记录 25 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
