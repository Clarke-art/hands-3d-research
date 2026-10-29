# experiments/hands_time_coupled_contact_recovery_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> - 唯一修正：共同已有姿态的解析随键初值，原硬约束及目标不变。IPOPT1次迭代后可行性优先回调停止，状态User_Requested_Stop；不是目标完全收敛。最终联合数值违规0。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_time_coupled_contact_recovery_r1/FINAL_RECOMMENDATION.md)

> - 局部自适应补采样17点全部通过，最大采样腕速374.450683mm/s；最大目标侵入0.004927870mm，错误区域侵入0、非相邻指面交叉0。标记LOCAL_ADJACENCY_SAMPLED_PASS_HUMAN_PENDING，不是全连续证明。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_time_coupled_contact_recovery_r1/FINAL_RECOMMENDATION.md)

## 技术路线

> **路线A：联合节点及其局部诊断连接通过，保留时间耦合接口。** 全部结果为DESIGN_PROVISIONAL。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_time_coupled_contact_recovery_r1/FINAL_RECOMMENDATION.md)

> - 主要求解：36变量、963不等式（接触为双侧容差带）、10928个Jacobian结构非零元；39次IPOPT迭代后Maximum_WallTime_Exceeded，违规0.703679，失败保留。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_time_coupled_contact_recovery_r1/FINAL_RECOMMENDATION.md)

## 测试结论

> - 唯一修正：共同已有姿态的解析随键初值，原硬约束及目标不变。IPOPT1次迭代后可行性优先回调停止，状态User_Requested_Stop；不是目标完全收敛。最终联合数值违规0。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_time_coupled_contact_recovery_r1/FINAL_RECOMMENDATION.md)

> - 局部自适应补采样17点全部通过，最大采样腕速374.450683mm/s；最大目标侵入0.004927870mm，错误区域侵入0、非相邻指面交叉0。标记LOCAL_ADJACENCY_SAMPLED_PASS_HUMAN_PENDING，不是全连续证明。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_time_coupled_contact_recovery_r1/FINAL_RECOMMENDATION.md)

## 失败原因与证据边界

> 4. 实际两次求解使用单步长差分回退，不能事后宣称所有试探点导数已验证。最终发现节点0的lambda扰动跨越自碰撞min/max分支：21个自碰撞行对1e-4/1e-5名义步长敏感，最大差0.018561737；接触面签名未变。缩小至1e-5/1e-6后差2.12e-06。这是分支/步长问题，不是接触失效或人体不可行证据。

出处：[NONSMOOTH_DERIVATIVE_GUARD.md](../research/experiments/hands_time_coupled_contact_recovery_r1/NONSMOOTH_DERIVATIVE_GUARD.md)

## 后续建议

> **DESIGN_PROVISIONAL — STOP — HUMAN REVIEW。** 下一步必须先经Human选择入口/出口与产品路线，不自动扩大窗口。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_time_coupled_contact_recovery_r1/FINAL_RECOMMENDATION.md)

> 局部范围只有2.083333ms。与原较早有效参考的必要平均连接速度约6343.34mm/s，因此选中局部解不能直接嵌回原轨迹；也未检验后续出口。这强调更早手位准备和跨事件状态选择的重要性。未证明固定MIDI时间/C01绝对不可行，未更改音乐或指法。

出处：[PRODUCT_ROUTE_EXIT_REVIEW.md](../research/experiments/hands_time_coupled_contact_recovery_r1/PRODUCT_ROUTE_EXIT_REVIEW.md)

## 原报告与关键代码

- [experiments/hands_time_coupled_contact_recovery_r1/FINAL_RECOMMENDATION.md](../research/experiments/hands_time_coupled_contact_recovery_r1/FINAL_RECOMMENDATION.md)
- [experiments/hands_time_coupled_contact_recovery_r1/RECOVERY_TIMELINE_AUDIT.md](../research/experiments/hands_time_coupled_contact_recovery_r1/RECOVERY_TIMELINE_AUDIT.md)
- [experiments/hands_time_coupled_contact_recovery_r1/PRODUCT_ROUTE_EXIT_REVIEW.md](../research/experiments/hands_time_coupled_contact_recovery_r1/PRODUCT_ROUTE_EXIT_REVIEW.md)
- [experiments/hands_time_coupled_contact_recovery_r1/NONSMOOTH_DERIVATIVE_GUARD.md](../research/experiments/hands_time_coupled_contact_recovery_r1/NONSMOOTH_DERIVATIVE_GUARD.md)
- [experiments/hands_time_coupled_contact_recovery_r1/audit_timeline.py](../../src/legacy/experiments/hands_time_coupled_contact_recovery_r1/audit_timeline.py)
- [experiments/hands_time_coupled_contact_recovery_r1/check_adjacency.py](../../src/legacy/experiments/hands_time_coupled_contact_recovery_r1/check_adjacency.py)
- [experiments/hands_time_coupled_contact_recovery_r1/coupled_model.py](../../src/legacy/experiments/hands_time_coupled_contact_recovery_r1/coupled_model.py)
- [experiments/hands_time_coupled_contact_recovery_r1/diagnose_branch.py](../../src/legacy/experiments/hands_time_coupled_contact_recovery_r1/diagnose_branch.py)
- [experiments/hands_time_coupled_contact_recovery_r1/final_guard.py](../../src/legacy/experiments/hands_time_coupled_contact_recovery_r1/final_guard.py)
- [experiments/hands_time_coupled_contact_recovery_r1/make_batch_verifier.py](../../src/legacy/experiments/hands_time_coupled_contact_recovery_r1/make_batch_verifier.py)
- [experiments/hands_time_coupled_contact_recovery_r1/prepare_correction.py](../../src/legacy/experiments/hands_time_coupled_contact_recovery_r1/prepare_correction.py)
- [experiments/hands_time_coupled_contact_recovery_r1/prepare_protection.py](../../src/legacy/experiments/hands_time_coupled_contact_recovery_r1/prepare_protection.py)
- [experiments/hands_time_coupled_contact_recovery_r1/probe_derivatives.py](../../src/legacy/experiments/hands_time_coupled_contact_recovery_r1/probe_derivatives.py)
- [experiments/hands_time_coupled_contact_recovery_r1/solve_correction.py](../../src/legacy/experiments/hands_time_coupled_contact_recovery_r1/solve_correction.py)
- [experiments/hands_time_coupled_contact_recovery_r1/solve_joint.py](../../src/legacy/experiments/hands_time_coupled_contact_recovery_r1/solve_joint.py)
- [experiments/hands_time_coupled_contact_recovery_r1/validate_adaptive_guard.py](../../src/legacy/experiments/hands_time_coupled_contact_recovery_r1/validate_adaptive_guard.py)

## 输入、输出与大型证据

该目录原始成员 103 项；拟公开身份记录 72 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
