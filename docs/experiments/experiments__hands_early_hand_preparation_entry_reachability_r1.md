# experiments/hands_early_hand_preparation_entry_reachability_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 全入口共 85 个独立Blender样本，45个失败。补采样后的首个失败为 2.778896666667s，中指与D#5错误区域侵入 0.254667mm；整段最大错误区域侵入3.872186mm >0.25mm。E5在2.928717666667s和终点2.936009333333s接触失败。目标键最大侵入0.199001mm，非相邻指面交叉0，关节族/域均通过；这些通过不能覆盖错误区域和接触失败。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_early_hand_preparation_entry_reachability_r1/FINAL_RECOMMENDATION.md)

> 建议保留冻结Rig、真实蒙皮、Action、合同、参考族、稀疏接口与验收，转向较长上下文手位规划、动作先验+接触IK，以及运动可行性反馈到指法。不要再以增加几个静态节点、优化几毫秒或提高迭代数作为下一里程碑。下一最小产品任务是新的高层方案在同一真实B2入口完整通过原时序和几何门禁；之后才考虑完整25ms及E5 ON+35ms验收。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_early_hand_preparation_entry_reachability_r1/FINAL_RECOMMENDATION.md)

## 技术路线

> 主要问题是音乐上下文中的手位/指尖清障路线、受限运动表示与接触几何代理稳定性。实时多尺度导数保护确实参与求解，并拒绝未验证分支；原伪不连续代理已在实验副本修正，最终IPOPT仍因新的局部导数不一致停止，未收敛。没有证据把所有失败归咎于原接触合同，也不能以预算内搜索失败证明人体不可能。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_early_hand_preparation_entry_reachability_r1/FINAL_RECOMMENDATION.md)

> |PRODUCT_ROUTE_PIVOT_REQUIRED|True|

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_early_hand_preparation_entry_reachability_r1/FINAL_RECOMMENDATION.md)

## 测试结论

> **能真正利用前一个音符的持键时间做部分提前准备；尚不能让已验证局部动作获得完整、自然的真实入口。** 本轮从实际B2起点、原MIDI时序与冻结Rig出发完成一次主入口候选和唯一针对性修正。入口整体FAIL，不能报告PASS，也没有证明当前指法或人体动作绝对不可行。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_early_hand_preparation_entry_reachability_r1/FINAL_RECOMMENDATION.md)

> |G4_HOLD_PREPARATION_FEASIBLE|PASS_SAMPLED_PREFIX_ONLY|

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_early_hand_preparation_entry_reachability_r1/FINAL_RECOMMENDATION.md)

## 失败原因与证据边界

> |前序手位能否提前移动|主候选采样前缀长250.000ms，腕移15.419mm；合法G4接触保持|可提前准备，工程速率下界不是主阻碍|

出处：[PRODUCT_ROUTE_DECISION.md](../research/experiments/hands_early_hand_preparation_entry_reachability_r1/PRODUCT_ROUTE_DECISION.md)

> 修正求解共记录 12 个迭代回调，约束最大违约从3.171479降至 1.408718505，未取得可行解；返回 Invalid_Number_Detected。实时保护记录 93 次局部差分一致、1 次严格拒绝。最终拒绝位于节点2，跨尺度差异1.088481与0.712314，导致Invalid_Number_Detected；这是导数保护中止，不能误报为目标收敛或纯超时。失败导数的完整试探控制向量未记录，故不宣称该特定试探可独立重放。分支日志保留在 ENTRY_CORRECTION_RESULT.json。

出处：[NONSMOOTH_AND_RUNTIME_AUDIT.md](../research/experiments/hands_early_hand_preparation_entry_reachability_r1/NONSMOOTH_AND_RUNTIME_AUDIT.md)

## 后续建议

> 建议保留冻结Rig、真实蒙皮、Action、合同、参考族、稀疏接口与验收，转向较长上下文手位规划、动作先验+接触IK，以及运动可行性反馈到指法。不要再以增加几个静态节点、优化几毫秒或提高迭代数作为下一里程碑。下一最小产品任务是新的高层方案在同一真实B2入口完整通过原时序和几何门禁；之后才考虑完整25ms及E5 ON+35ms验收。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_early_hand_preparation_entry_reachability_r1/FINAL_RECOMMENDATION.md)

> 保留项目，停止同一G4→E5局部补丁循环。本轮确实利用B2之后的持键时间完成了部分提前准备，但没有建立真实完整入口，因此路线A不成立。路线B成立：有完整从真实起点出发的采样可行前缀，而不是新增几个独立静态点；剩余持键清障和释放/触键入口仍失败。不据此宣称当前指法或人体动作绝对不可行。

出处：[PRODUCT_ROUTE_DECISION.md](../research/experiments/hands_early_hand_preparation_entry_reachability_r1/PRODUCT_ROUTE_DECISION.md)

## 原报告与关键代码

- [experiments/hands_early_hand_preparation_entry_reachability_r1/FINAL_RECOMMENDATION.md](../research/experiments/hands_early_hand_preparation_entry_reachability_r1/FINAL_RECOMMENDATION.md)
- [experiments/hands_early_hand_preparation_entry_reachability_r1/PRODUCT_ROUTE_DECISION.md](../research/experiments/hands_early_hand_preparation_entry_reachability_r1/PRODUCT_ROUTE_DECISION.md)
- [experiments/hands_early_hand_preparation_entry_reachability_r1/NONSMOOTH_AND_RUNTIME_AUDIT.md](../research/experiments/hands_early_hand_preparation_entry_reachability_r1/NONSMOOTH_AND_RUNTIME_AUDIT.md)
- [experiments/hands_early_hand_preparation_entry_reachability_r1/ENTRY_TARGET_SET_AND_ANCHORS.md](../research/experiments/hands_early_hand_preparation_entry_reachability_r1/ENTRY_TARGET_SET_AND_ANCHORS.md)
- [experiments/hands_early_hand_preparation_entry_reachability_r1/ENTRY_TIMELINE_AND_KINEMATIC_BOUNDS.md](../research/experiments/hands_early_hand_preparation_entry_reachability_r1/ENTRY_TIMELINE_AND_KINEMATIC_BOUNDS.md)
- [experiments/hands_early_hand_preparation_entry_reachability_r1/adaptive_hold_and_bounds.py](../../src/legacy/experiments/hands_early_hand_preparation_entry_reachability_r1/adaptive_hold_and_bounds.py)
- [experiments/hands_early_hand_preparation_entry_reachability_r1/batch_verify.py](../../src/legacy/experiments/hands_early_hand_preparation_entry_reachability_r1/batch_verify.py)
- [experiments/hands_early_hand_preparation_entry_reachability_r1/build_hold_probes.py](../../src/legacy/experiments/hands_early_hand_preparation_entry_reachability_r1/build_hold_probes.py)
- [experiments/hands_early_hand_preparation_entry_reachability_r1/diagnose_guard.py](../../src/legacy/experiments/hands_early_hand_preparation_entry_reachability_r1/diagnose_guard.py)
- [experiments/hands_early_hand_preparation_entry_reachability_r1/finalize_facts.py](../../src/legacy/experiments/hands_early_hand_preparation_entry_reachability_r1/finalize_facts.py)
- [experiments/hands_early_hand_preparation_entry_reachability_r1/guarded_node.py](../../src/legacy/experiments/hands_early_hand_preparation_entry_reachability_r1/guarded_node.py)
- [experiments/hands_early_hand_preparation_entry_reachability_r1/preflight.py](../../src/legacy/experiments/hands_early_hand_preparation_entry_reachability_r1/preflight.py)
- [experiments/hands_early_hand_preparation_entry_reachability_r1/prepare_delayed_flex.py](../../src/legacy/experiments/hands_early_hand_preparation_entry_reachability_r1/prepare_delayed_flex.py)
- [experiments/hands_early_hand_preparation_entry_reachability_r1/prepare_entry_adaptive.py](../../src/legacy/experiments/hands_early_hand_preparation_entry_reachability_r1/prepare_entry_adaptive.py)
- [experiments/hands_early_hand_preparation_entry_reachability_r1/prepare_entry_correction.py](../../src/legacy/experiments/hands_early_hand_preparation_entry_reachability_r1/prepare_entry_correction.py)
- [experiments/hands_early_hand_preparation_entry_reachability_r1/record_protection_scope.py](../../src/legacy/experiments/hands_early_hand_preparation_entry_reachability_r1/record_protection_scope.py)
- [experiments/hands_early_hand_preparation_entry_reachability_r1/repair_proxy_and_build_entry.py](../../src/legacy/experiments/hands_early_hand_preparation_entry_reachability_r1/repair_proxy_and_build_entry.py)

## 输入、输出与大型证据

该目录原始成员 283 项；拟公开身份记录 238 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
