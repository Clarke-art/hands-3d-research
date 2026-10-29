# experiments/hands_fingering_motion_co_design_feasibility_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> | B02指骨空间顺序 | 无名→中指MCP横向−21.15mm，键目标＋23.94mm，方向相反 | 食→中指MCP＋24.55mm，与目标同向 | 同P1 | 同P1 |

出处：[HAND_MOTION_FEASIBILITY.md](../research/experiments/hands_fingering_motion_co_design_feasibility_r1/HAND_MOTION_FEASIBILITY.md)

## 技术路线

> | 6. 值得选一组立即生成短片段吗？ | **目前不建议。** P3有研究理由，却无原布局下新触键支持；不能用“数字更顺”批准生成。若Human另行选择受控掌腕协同路线，先确认R08 E5持键→R09拇指C5→R10食指D5的联合触达及旁指条件，再决定是否授权一次真实动作验证。不得只截原B02窗口。 |

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_fingering_motion_co_design_feasibility_r1/FINAL_RECOMMENDATION.md)

> | 7. 需要新增指法算法吗？ | **不需要。** 现有PianoPlayer的完整序列、原生记忆/锚点＋C1/A2协调基础足够产生评估建议。缺口是新指法下保持接触与真实几何安全的运动证据，不是搜索器数量；本轮未证明原C1机制能直接生成合格新动作，也未证明更强规划必需。 |

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_fingering_motion_co_design_feasibility_r1/FINAL_RECOMMENDATION.md)

## 测试结论

> 3次原生搜索合计17.701秒；主评估28.617秒，附加界限核对约1.327秒（详见日志，不含人工阅读/报告）。26项实际引用关键源文件前后SHA一致；C1 Blend仍`d8e0f5a8…e51a7`。本轮窄范围核对不覆盖或撤销历史并发保护FAIL；没有跟随历史Manifest中的旧路径访问资产。`源SHA`（链接见原报告）、`运行成本`（链接见原报告）、`历史保护说明`（链接见原报告）。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_fingering_motion_co_design_feasibility_r1/FINAL_RECOMMENDATION.md)

> **替代指法具有可证明的顺序与空闲时间收益，但没有一组证明整体3D优势。三组均需要改变原C1掌腕布局才能支持新的C5拇指触键。** 此结论限定原掌腕与上游状态；不等于人体无法演奏，也不决定必须采用更强优化器。

出处：[HAND_MOTION_FEASIBILITY.md](../research/experiments/hands_fingering_motion_co_design_feasibility_r1/HAND_MOTION_FEASIBILITY.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

> 低成本“指法候选＋冻结3D手前置评估”有实际判别价值：识别了数字顺序改善背后的触达与前后事件代价。当前没有足够证据选出整体运动更好的替代指法，**不建议立即进入新动作生成**。停止追加指法搜索，保留原C1比较基准与正式指法。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_fingering_motion_co_design_feasibility_r1/FINAL_RECOMMENDATION.md)

> | 1. 找到有实际优势的替代指法了吗？ | **局部结构/时间优势有，整体3D优势未证明。** 三组都改B02为2→3；P3只改变R09/R10并保留原R08，是后续决策中较少改动的备选，尚未达到事前PROMISING门槛。 |

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_fingering_motion_co_design_feasibility_r1/FINAL_RECOMMENDATION.md)

## 原报告与关键代码

- [experiments/hands_fingering_motion_co_design_feasibility_r1/FINAL_RECOMMENDATION.md](../research/experiments/hands_fingering_motion_co_design_feasibility_r1/FINAL_RECOMMENDATION.md)
- [experiments/hands_fingering_motion_co_design_feasibility_r1/FINGERING_CANDIDATES.md](../research/experiments/hands_fingering_motion_co_design_feasibility_r1/FINGERING_CANDIDATES.md)
- [experiments/hands_fingering_motion_co_design_feasibility_r1/HAND_MOTION_FEASIBILITY.md](../research/experiments/hands_fingering_motion_co_design_feasibility_r1/HAND_MOTION_FEASIBILITY.md)
- [experiments/hands_fingering_motion_co_design_feasibility_r1/audit_details.py](../../src/legacy/experiments/hands_fingering_motion_co_design_feasibility_r1/audit_details.py)
- [experiments/hands_fingering_motion_co_design_feasibility_r1/evaluate.py](../../src/legacy/experiments/hands_fingering_motion_co_design_feasibility_r1/evaluate.py)
- [experiments/hands_fingering_motion_co_design_feasibility_r1/verify_delivery.py](../../src/legacy/experiments/hands_fingering_motion_co_design_feasibility_r1/verify_delivery.py)

## 输入、输出与大型证据

该目录原始成员 28 项；拟公开身份记录 24 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
