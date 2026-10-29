# experiments/hands_role_aware_motion_recomposition_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 本轮完成来源特征记录和一批三点活动小指有限校正，取得保接触并降低自身邻键侵入的静态数值线索；随后真实Blender诊断因新增脚本输入字段错误停止。该错误属于本轮实现缺陷，不是指法、Rig、来源资格或动作复用理论失败。按“正式求解开始后发生错误即停止”留证，没有修复后重跑，也没有进入目标重组。

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_role_aware_motion_recomposition_r1/FINAL_HUMAN_REVIEW.md)

> | A 真正提取并使用C1有效特征？ | **部分。** 源事件相位、关节先验、共享腕数据、skin接触与键内锚点已提取；源活动姿态和接触用于局部校正。尚未完成键相对腕表示或目标生成，不能宣称完整原语复用。没有复制目标关节答案。 |

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_role_aware_motion_recomposition_r1/FINAL_HUMAN_REVIEW.md)

## 技术路线

> 本轮完成来源特征记录和一批三点活动小指有限校正，取得保接触并降低自身邻键侵入的静态数值线索；随后真实Blender诊断因新增脚本输入字段错误停止。该错误属于本轮实现缺陷，不是指法、Rig、来源资格或动作复用理论失败。按“正式求解开始后发生错误即停止”留证，没有修复后重跑，也没有进入目标重组。

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_role_aware_motion_recomposition_r1/FINAL_HUMAN_REVIEW.md)

> | H 扩展通用避障还是换路线？ | **本轮停止，不建议直接扩展通用系统或进入产品。** 当前错误尚不能否定表示或证明必须全手重解；也不足以授权继续同类调参。由独立审核与Human决定是否另行处理实现契约，不能自动重跑或改选路线。 |

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_role_aware_motion_recomposition_r1/FINAL_HUMAN_REVIEW.md)

## 测试结论

> 已有证据支持活动pad与其他指的条件性分离，但全手皮肤有跨指权重、共享指蹼和拇指corrective，不能分开五个掌根。原来源168个活动pad样本PASS；62个中／无名指相交样本、161个非目标键侵入样本仍存在。原R05小指103/110样本有自身E5侵入，2.0秒见证顶点2731深1.715146mm。它不能靠只改闲置指消除。以上数字来自前轮真实Blender审计，不能记为本轮新验证。

出处：[ROLE_MOTION_REPRESENTATION.md](../research/experiments/hands_role_aware_motion_recomposition_r1/ROLE_MOTION_REPRESENTATION.md)

> 真实诊断在输入字段读取处失败，尚未加载C1。结论为**有限校正能力有静态数值线索，真实skin安全UNKNOWN**；不是完整来源修复，也不是相邻指安全或动态成功。按出错止损，未进入目标适配。

出处：[ROLE_MOTION_REPRESENTATION.md](../research/experiments/hands_role_aware_motion_recomposition_r1/ROLE_MOTION_REPRESENTATION.md)

## 失败原因与证据边界

> 目标黑键F♯5与白键G5需要不同高度、纵深和邻键协调，不可把C5→D5整体平移视为适配。当前没有生成共享腕适配曲线、释放/准备/闲置角色曲线、PCHIP目标轨迹或入口/出口速度连接证据。因停止原因是程序字段错误，不能声称目标触键不可达、存在确定几何冲突、时间不足或必须全手重求解。

出处：[RECOMPOSITION_EXECUTION_AND_VALIDATION.md](../research/experiments/hands_role_aware_motion_recomposition_r1/RECOMPOSITION_EXECUTION_AND_VALIDATION.md)

## 后续建议

> | H 扩展通用避障还是换路线？ | **本轮停止，不建议直接扩展通用系统或进入产品。** 当前错误尚不能否定表示或证明必须全手重解；也不足以授权继续同类调参。由独立审核与Human决定是否另行处理实现契约，不能自动重跑或改选路线。 |

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_role_aware_motion_recomposition_r1/FINAL_HUMAN_REVIEW.md)

> 唯一表示锁定为“事件相位＋共享掌腕相对运动＋五指RSSF相对姿态＋真实活动接触特征”。`SOURCE_FEATURES.npz`（链接见原报告）保存239个来源采样：事件相位、五指角度先验、共享Rig世界矩阵、五个真实skin pad、88键Action角度及四个上下文事件的键面内相对XY锚点。它是带缺陷标记的来源特征记录，**不是安全原语或新动作**。其中`wrist_relative_world`实际仍是源Rig世界矩阵，尚未完成相对键位归一化或生成器；五指原曲线仅作来源证据/先验，禁止直接复制缺陷闲置轨迹。来源速度与关节曲度可供后续先验，本轮没有新时标或连续速度验收。详细边界见`FEATURE_PROVENANCE.json`（链接见原报告）。

出处：[ROLE_MOTION_REPRESENTATION.md](../research/experiments/hands_role_aware_motion_recomposition_r1/ROLE_MOTION_REPRESENTATION.md)

## 原报告与关键代码

- [experiments/hands_role_aware_motion_recomposition_r1/FINAL_HUMAN_REVIEW.md](../research/experiments/hands_role_aware_motion_recomposition_r1/FINAL_HUMAN_REVIEW.md)
- [experiments/hands_role_aware_motion_recomposition_r1/ROLE_MOTION_REPRESENTATION.md](../research/experiments/hands_role_aware_motion_recomposition_r1/ROLE_MOTION_REPRESENTATION.md)
- [experiments/hands_role_aware_motion_recomposition_r1/RECOMPOSITION_EXECUTION_AND_VALIDATION.md](../research/experiments/hands_role_aware_motion_recomposition_r1/RECOMPOSITION_EXECUTION_AND_VALIDATION.md)
- [experiments/hands_role_aware_motion_recomposition_r1/prepare.py](../../src/legacy/experiments/hands_role_aware_motion_recomposition_r1/prepare.py)
- [experiments/hands_role_aware_motion_recomposition_r1/reports.py](../../src/legacy/experiments/hands_role_aware_motion_recomposition_r1/reports.py)
- [experiments/hands_role_aware_motion_recomposition_r1/run_stage.py](../../src/legacy/experiments/hands_role_aware_motion_recomposition_r1/run_stage.py)
- [experiments/hands_role_aware_motion_recomposition_r1/source_fit.py](../../src/legacy/experiments/hands_role_aware_motion_recomposition_r1/source_fit.py)

## 输入、输出与大型证据

该目录原始成员 35 项；拟公开身份记录 26 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
