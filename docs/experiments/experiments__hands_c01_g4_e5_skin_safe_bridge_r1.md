# experiments/hands_c01_g4_e5_skin_safe_bridge_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> | 第1次修复 | 实际触键、目标侵入0.00316mm及E5准备通过，但中指/无名指9对交叉。 |

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_c01_g4_e5_skin_safe_bridge_r1/FINAL_RECOMMENDATION.md)

> | 是否值得增强已有求解器 | 有依据继续：面内约束显著减少目标侵入，真实面反馈能消除已知交叉。但下一次需优先解决实际接触硬约束与自适应全局近面分离，并独立验收；不宜继续靠调软权重和逐指补洞。 |

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_c01_g4_e5_skin_safe_bridge_r1/FINAL_RECOMMENDATION.md)

## 技术路线

> **本轮未证明G4拇指安全持键同时中指自然移动到E5可行。** 两次新增定向静态求解均未满足全部S1真实皮肤门禁，因此按前置条件停止；没有生成G4→E5短连接、Action或视频。全部结果保持`DESIGN_PROVISIONAL`。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_c01_g4_e5_skin_safe_bridge_r1/FINAL_RECOMMENDATION.md)

> | 是否值得增强已有求解器 | 有依据继续：面内约束显著减少目标侵入，真实面反馈能消除已知交叉。但下一次需优先解决实际接触硬约束与自适应全局近面分离，并独立验收；不宜继续靠调软权重和逐指补洞。 |

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_c01_g4_e5_skin_safe_bridge_r1/FINAL_RECOMMENDATION.md)

## 测试结论

> | 面级检测是否可靠支撑本轮 | 最小回归通过、旧侵入复现，实际Blender独立验收与保存后重读一致。使用真实88键按压状态和完整求值皮肤；S2增加精确面/边距离。仍不代表软组织/物理认证。 |

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_c01_g4_e5_skin_safe_bridge_r1/FINAL_RECOMMENDATION.md)

> 数值求解共 **47.156秒**（预算900秒），两个初值、每次55nfev；完整调用数、残差改进历史、控制参数、实际碰撞见证点和收敛状态保留。达到2次上限后立即停止动态工作。另交付5张720p静帧及一份隔离诊断Blend。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_c01_g4_e5_skin_safe_bridge_r1/FINAL_RECOMMENDATION.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

> | 是否值得增强已有求解器 | 有依据继续：面内约束显著减少目标侵入，真实面反馈能消除已知交叉。但下一次需优先解决实际接触硬约束与自适应全局近面分离，并独立验收；不宜继续靠调软权重和逐指补洞。 |

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_c01_g4_e5_skin_safe_bridge_r1/FINAL_RECOMMENDATION.md)

> 下一步建议仅供Human选择：保持冻结资产和C01，在新授权下将真实指腹接触设为显式约束/接触保持，并采用自适应近面候选的分离约束，确认至少一组严格S1通过及可接受指间余量后再讨论单条短连接。本轮不执行这些后续动作，也不挑选/修补中间结果升级为PASS。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_c01_g4_e5_skin_safe_bridge_r1/FINAL_RECOMMENDATION.md)

## 原报告与关键代码

- [experiments/hands_c01_g4_e5_skin_safe_bridge_r1/FINAL_RECOMMENDATION.md](../research/experiments/hands_c01_g4_e5_skin_safe_bridge_r1/FINAL_RECOMMENDATION.md)
- [experiments/hands_c01_g4_e5_skin_safe_bridge_r1/S1_STATIC_REPAIR_REPORT.md](../research/experiments/hands_c01_g4_e5_skin_safe_bridge_r1/S1_STATIC_REPAIR_REPORT.md)
- [experiments/hands_c01_g4_e5_skin_safe_bridge_r1/HUMAN_VISUAL_REVIEW.md](../research/experiments/hands_c01_g4_e5_skin_safe_bridge_r1/HUMAN_VISUAL_REVIEW.md)
- [experiments/hands_c01_g4_e5_skin_safe_bridge_r1/S2_CLEARANCE_REVIEW.md](../research/experiments/hands_c01_g4_e5_skin_safe_bridge_r1/S2_CLEARANCE_REVIEW.md)
- [experiments/hands_c01_g4_e5_skin_safe_bridge_r1/preflight_geometry.py](../../src/legacy/experiments/hands_c01_g4_e5_skin_safe_bridge_r1/preflight_geometry.py)
- [experiments/hands_c01_g4_e5_skin_safe_bridge_r1/prepare.py](../../src/legacy/experiments/hands_c01_g4_e5_skin_safe_bridge_r1/prepare.py)
- [experiments/hands_c01_g4_e5_skin_safe_bridge_r1/readback_and_stills.py](../../src/legacy/experiments/hands_c01_g4_e5_skin_safe_bridge_r1/readback_and_stills.py)
- [experiments/hands_c01_g4_e5_skin_safe_bridge_r1/read_entry_context.py](../../src/legacy/experiments/hands_c01_g4_e5_skin_safe_bridge_r1/read_entry_context.py)
- [experiments/hands_c01_g4_e5_skin_safe_bridge_r1/repair_s1.py](../../src/legacy/experiments/hands_c01_g4_e5_skin_safe_bridge_r1/repair_s1.py)
- [experiments/hands_c01_g4_e5_skin_safe_bridge_r1/verify_s1_actual.py](../../src/legacy/experiments/hands_c01_g4_e5_skin_safe_bridge_r1/verify_s1_actual.py)
- [experiments/hands_c01_g4_e5_skin_safe_bridge_r1/write_reports.py](../../src/legacy/experiments/hands_c01_g4_e5_skin_safe_bridge_r1/write_reports.py)

## 输入、输出与大型证据

该目录原始成员 49 项；拟公开身份记录 35 项。
- `experiments/hands_c01_g4_e5_skin_safe_bridge_r1/S1_SKIN_SAFE_REPAIR_DIAGNOSTIC_R1.blend` → `hands-research-r1-selected-008.zip` / `payload/experiments/hands_c01_g4_e5_skin_safe_bridge_r1/S1_SKIN_SAFE_REPAIR_DIAGNOSTIC_R1.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
