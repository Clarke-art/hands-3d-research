# experiments/hands_role_aware_motion_recomposition_r2

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 首个接触失败为 **3.9003535s，R11**；首个核心目标接触失败为 **4.4795202s，R13**。R12 黑键接触可以保持，但不能把它记为整个 F♯5→G5 成功。释放跟随最大横向偏差约21.332mm、任务高度偏差约17.425mm；准备阶段也记录了较大过程偏差，未将整个准备阶段套用活动触键的0.03mm门禁。

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_role_aware_motion_recomposition_r2/FINAL_HUMAN_REVIEW.md)

> 4.0045202s，中指真实顶点 **2715** 进入非目标 **F5 REAR_NOTCHED**，深度约 **7.752886mm**。同刻真实三角面 `[1162,1288,2715]` 的最大面内深度证书为 **[7.767782934,7.767782940]mm**；该时刻原 C1 的非目标面内最大值约2.185538mm。证书针对缓存真实 skin 和按实际Action旋转的登记组件，后者逐帧与实际键体对应误差小于0.001mm；窄证书区间不是物理测量精度。全动态窗口至少存在这一严重面内穿入，不能以顶点或少量采样为零掩盖。

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_role_aware_motion_recomposition_r2/FINAL_HUMAN_REVIEW.md)

## 技术路线

> 生成机制已实际执行，但当前锁定策略没有得到合格跨事件动作。失败是接触、速度与整手几何问题，共享腕幅度也明显增加；不是工具链未完成，也不证明所有低复杂度机制都不可能。

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_role_aware_motion_recomposition_r2/FINAL_HUMAN_REVIEW.md)

> 初始边界后约0.7145ms即存在一个局部支持点，局部 IK 与边界姿态差异在极短 Hermite 段内连接，造成速度尖峰。事件支持点逐次对齐和插值没有同时维持全过程接触/速度；向黑键纵深重定位的共享根运动也明显放大。以上是本次确定策略的失败原因，未按失败时刻修改节点、角度、权重或重新求解。

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_role_aware_motion_recomposition_r2/FINAL_HUMAN_REVIEW.md)

## 测试结论

> 连续关节域的精确多项式检查通过，入口/出口关节位置及导数连接通过。质量仍 FAIL：

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_role_aware_motion_recomposition_r2/FINAL_HUMAN_REVIEW.md)

> | F 原接触/域/几何/连续性合同？ | **整体FAIL。** 关节域和数学边界连接通过；接触、增加速度与整手几何不通过。根幅度对照另记，不作为新增门禁。 |

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_role_aware_motion_recomposition_r2/FINAL_HUMAN_REVIEW.md)

## 失败原因与证据边界

> 初始边界后约0.7145ms即存在一个局部支持点，局部 IK 与边界姿态差异在极短 Hermite 段内连接，造成速度尖峰。事件支持点逐次对齐和插值没有同时维持全过程接触/速度；向黑键纵深重定位的共享根运动也明显放大。以上是本次确定策略的失败原因，未按失败时刻修改节点、角度、权重或重新求解。

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_role_aware_motion_recomposition_r2/FINAL_HUMAN_REVIEW.md)

> 恢复后的真实 Blender 复核执行 **63.406s**，完成全部 240 个时刻；实际 skin 对候选 native FK/LBS 的最大偏差 **0.001232mm**，低于原 0.01mm 重建尺度，琴键角度与保存时钟差异约 **1.04×10⁻¹³rad**。这将运动质量失败与工具链阻断明确分开。

出处：[MOTION_RECOMPOSITION_EXECUTION.md](../research/experiments/hands_role_aware_motion_recomposition_r2/MOTION_RECOMPOSITION_EXECUTION.md)

## 后续建议

> | D 有限活动指校正适用于连续动作？ | **仅有局部效果。** 第一活动指触键成功，后续持键与共享根移动不能保持；三个静态结果未被重新求解或拼接。 |

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_role_aware_motion_recomposition_r2/FINAL_HUMAN_REVIEW.md)

> 如 Human 另行决定研究，应先明确适配后的根运动范围、连续接触、释放交接及按真实时间间隔约束速度。当前不建议同策略继续调参、增加候选或扩展通用避障系统，本轮不启动下一阶段。

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_role_aware_motion_recomposition_r2/FINAL_HUMAN_REVIEW.md)

## 原报告与关键代码

- [experiments/hands_role_aware_motion_recomposition_r2/FINAL_HUMAN_REVIEW.md](../research/experiments/hands_role_aware_motion_recomposition_r2/FINAL_HUMAN_REVIEW.md)
- [experiments/hands_role_aware_motion_recomposition_r2/MOTION_RECOMPOSITION_EXECUTION.md](../research/experiments/hands_role_aware_motion_recomposition_r2/MOTION_RECOMPOSITION_EXECUTION.md)
- [experiments/hands_role_aware_motion_recomposition_r2/analyze_failures.py](../../src/legacy/experiments/hands_role_aware_motion_recomposition_r2/analyze_failures.py)
- [experiments/hands_role_aware_motion_recomposition_r2/bootstrap.py](../../src/legacy/experiments/hands_role_aware_motion_recomposition_r2/bootstrap.py)
- [experiments/hands_role_aware_motion_recomposition_r2/diagnostic_readback.py](../../src/legacy/experiments/hands_role_aware_motion_recomposition_r2/diagnostic_readback.py)
- [experiments/hands_role_aware_motion_recomposition_r2/finalize.py](../../src/legacy/experiments/hands_role_aware_motion_recomposition_r2/finalize.py)
- [experiments/hands_role_aware_motion_recomposition_r2/generate.py](../../src/legacy/experiments/hands_role_aware_motion_recomposition_r2/generate.py)
- [experiments/hands_role_aware_motion_recomposition_r2/representation.py](../../src/legacy/experiments/hands_role_aware_motion_recomposition_r2/representation.py)
- [experiments/hands_role_aware_motion_recomposition_r2/run.py](../../src/legacy/experiments/hands_role_aware_motion_recomposition_r2/run.py)
- [experiments/hands_role_aware_motion_recomposition_r2/stage0.py](../../src/legacy/experiments/hands_role_aware_motion_recomposition_r2/stage0.py)
- [experiments/hands_role_aware_motion_recomposition_r2/stage0_blender.py](../../src/legacy/experiments/hands_role_aware_motion_recomposition_r2/stage0_blender.py)
- [experiments/hands_role_aware_motion_recomposition_r2/stage1.py](../../src/legacy/experiments/hands_role_aware_motion_recomposition_r2/stage1.py)
- [experiments/hands_role_aware_motion_recomposition_r2/support.py](../../src/legacy/experiments/hands_role_aware_motion_recomposition_r2/support.py)
- [experiments/hands_role_aware_motion_recomposition_r2/validate_blender.py](../../src/legacy/experiments/hands_role_aware_motion_recomposition_r2/validate_blender.py)

## 输入、输出与大型证据

该目录原始成员 197 项；拟公开身份记录 182 项。
- `experiments/hands_role_aware_motion_recomposition_r2/CANDIDATE_ACTUAL_SKIN.npz` → `hands-research-r1-selected-014.zip` / `payload/experiments/hands_role_aware_motion_recomposition_r2/CANDIDATE_ACTUAL_SKIN.npz`
- `experiments/hands_role_aware_motion_recomposition_r2/MOTION_CANDIDATE.npz` → `hands-research-r1-selected-014.zip` / `payload/experiments/hands_role_aware_motion_recomposition_r2/MOTION_CANDIDATE.npz`
- `experiments/hands_role_aware_motion_recomposition_r2/TARGET_C1_POSTHOC_REFERENCE.npz` → `hands-research-r1-selected-014.zip` / `payload/experiments/hands_role_aware_motion_recomposition_r2/TARGET_C1_POSTHOC_REFERENCE.npz`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
