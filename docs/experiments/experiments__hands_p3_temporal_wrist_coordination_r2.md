# experiments/hands_p3_temporal_wrist_coordination_r2

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 接触使用冻结native FK/LBS真实权重的指腹顶点，沿原琴键Action在真实时刻的运动键面；原接触门槛横向≤0.03mm、垂向绝对间隙≤3mm未放宽。活动、持键、释放、准备与闲置指共同进入原A2任务模型；五指pad键体筛选和关节中心清障保留，未开发新指间避障引擎。准备／闲置指的真实全皮肤安全仍必须由候选Blender复核，不能由该有限代理认证。

出处：[TEMPORAL_WRIST_FEASIBILITY.md](../research/experiments/hands_p3_temporal_wrist_coordination_r2/TEMPORAL_WRIST_FEASIBILITY.md)

> 结果保存门禁通过，时变共享掌腕确实参与唯一正式求解；但锁定的74秒内部上限触发受控中止，没有返回优化终态。异常现场与最后有限参数完整留证。按任务规则停止候选Blender验证，不重跑、不增加节点、权重、范围或预算。

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_p3_temporal_wrist_coordination_r2/FINAL_HUMAN_REVIEW.md)

## 技术路线

> **NOT_FOUND_WITHIN_SCOPE：本轮未取得可核验的合法P3布局。唯一求解受控超时，只有标明身份的中间状态；未做候选Blender认证。**

出处：[TEMPORAL_WRIST_FEASIBILITY.md](../research/experiments/hands_p3_temporal_wrist_coordination_r2/TEMPORAL_WRIST_FEASIBILITY.md)

> 本次恢复原A2的时序支持、稀疏有界least_squares与分量PCHIP。控制时刻由原事件ON、35ms下沉、40ms释放跟随与必要180/75ms准备时刻派生；按原A2至少4ms支持点间隔规则避免重复节点。事前固定32个支持时刻、63个联合残差检查时刻，792个变量。首尾完整26维状态固定为原C1实际状态；内部每个时刻一个六维共享掌腕＋五指20维姿态，共同一次求解，触点XY按六个事件共享。不是独立静态解拼接，也不是重新固定公共腕位。

出处：[TEMPORAL_WRIST_FEASIBILITY.md](../research/experiments/hands_p3_temporal_wrist_coordination_r2/TEMPORAL_WRIST_FEASIBILITY.md)

## 测试结论

> **NOT_FOUND_WITHIN_SCOPE：本轮未取得可核验的合法P3布局。唯一求解受控超时，只有标明身份的中间状态；未做候选Blender认证。**

出处：[TEMPORAL_WRIST_FEASIBILITY.md](../research/experiments/hands_p3_temporal_wrist_coordination_r2/TEMPORAL_WRIST_FEASIBILITY.md)

> 本次恢复原A2的时序支持、稀疏有界least_squares与分量PCHIP。控制时刻由原事件ON、35ms下沉、40ms释放跟随与必要180/75ms准备时刻派生；按原A2至少4ms支持点间隔规则避免重复节点。事前固定32个支持时刻、63个联合残差检查时刻，792个变量。首尾完整26维状态固定为原C1实际状态；内部每个时刻一个六维共享掌腕＋五指20维姿态，共同一次求解，触点XY按六个事件共享。不是独立静态解拼接，也不是重新固定公共腕位。

出处：[TEMPORAL_WRIST_FEASIBILITY.md](../research/experiments/hands_p3_temporal_wrist_coordination_r2/TEMPORAL_WRIST_FEASIBILITY.md)

## 失败原因与证据边界

> | F：失败主要原因？ | 可明确的是**该锁定求解配置在74秒内未返回**，R1导出实现错误已修复且本次异常保存奏效。时序控制、PCHIP耦合、稀疏有限差分导致实际4424次残差调用，是计算成本事实；指法、Rig触达、手位协调与约束可解性仍UNKNOWN，不能据此选出几何根因或宣布表示绝对失败。 |

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_p3_temporal_wrist_coordination_r2/FINAL_HUMAN_REVIEW.md)

## 后续建议

> | G：值得生成P3动态候选？ | **NO，当前不建议。** 没有合法触键、整手安全和时间连接证据，指法顺序收益不足以批准动态生成。 |

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_p3_temporal_wrist_coordination_r2/FINAL_HUMAN_REVIEW.md)

> | H：停止P3、评估产品机制？ | **建议停止把P3作为继续追加同类布局优化的研发方向。** 保留P3为未验证的历史候选；不追加R3/R4。产品路线应回到整手运动表示与可复用动作机制的独立评估，先明确接触保持、释放／准备协同、Rig有效自由度、自然手型和计算成本，再由Human决定后续授权。没有证据直接要求复杂优化器，也不启动新机制开发。 |

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_p3_temporal_wrist_coordination_r2/FINAL_HUMAN_REVIEW.md)

## 原报告与关键代码

- [experiments/hands_p3_temporal_wrist_coordination_r2/TEMPORAL_WRIST_FEASIBILITY.md](../research/experiments/hands_p3_temporal_wrist_coordination_r2/TEMPORAL_WRIST_FEASIBILITY.md)
- [experiments/hands_p3_temporal_wrist_coordination_r2/FINAL_HUMAN_REVIEW.md](../research/experiments/hands_p3_temporal_wrist_coordination_r2/FINAL_HUMAN_REVIEW.md)
- [experiments/hands_p3_temporal_wrist_coordination_r2/RESULT_PERSISTENCE_VALIDATION.md](../research/experiments/hands_p3_temporal_wrist_coordination_r2/RESULT_PERSISTENCE_VALIDATION.md)
- [experiments/hands_p3_temporal_wrist_coordination_r2/gate1.py](../../src/legacy/experiments/hands_p3_temporal_wrist_coordination_r2/gate1.py)
- [experiments/hands_p3_temporal_wrist_coordination_r2/input_gate.py](../../src/legacy/experiments/hands_p3_temporal_wrist_coordination_r2/input_gate.py)
- [experiments/hands_p3_temporal_wrist_coordination_r2/prepare.py](../../src/legacy/experiments/hands_p3_temporal_wrist_coordination_r2/prepare.py)
- [experiments/hands_p3_temporal_wrist_coordination_r2/problem.py](../../src/legacy/experiments/hands_p3_temporal_wrist_coordination_r2/problem.py)
- [experiments/hands_p3_temporal_wrist_coordination_r2/reports.py](../../src/legacy/experiments/hands_p3_temporal_wrist_coordination_r2/reports.py)
- [experiments/hands_p3_temporal_wrist_coordination_r2/run_stage.py](../../src/legacy/experiments/hands_p3_temporal_wrist_coordination_r2/run_stage.py)
- [experiments/hands_p3_temporal_wrist_coordination_r2/solve.py](../../src/legacy/experiments/hands_p3_temporal_wrist_coordination_r2/solve.py)
- [experiments/hands_p3_temporal_wrist_coordination_r2/source_probe.py](../../src/legacy/experiments/hands_p3_temporal_wrist_coordination_r2/source_probe.py)

## 输入、输出与大型证据

该目录原始成员 50 项；拟公开身份记录 39 项。
- `experiments/hands_p3_temporal_wrist_coordination_r2/SOURCE_PROBE.npz` → `hands-research-r1-selected-014.zip` / `payload/experiments/hands_p3_temporal_wrist_coordination_r2/SOURCE_PROBE.npz`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
