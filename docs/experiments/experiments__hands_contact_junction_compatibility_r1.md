# experiments/hands_contact_junction_compatibility_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 共同边界：两指真实接触，目标最大侵入0.164884392mm，非目标/错误区域0.176797055mm，非相邻指面交叉0，中指/无名指精确间隙3.158507mm。SLSQP第2次收敛；第1次E5 pad微小越界失败原样保留。掌根yaw和拇指末节控制接近边界，Human自然度仍待审，计算参考族通过不能替代视觉认可。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_contact_junction_compatibility_r1/FINAL_RECOMMENDATION.md)

> 唯一局部路径：2.913092667–2.938092667秒，25ms；在共同构型附近起步，未连接B2/P2。四个后续节点都收敛并通过；120Hz基础采样加风险区补采样共24个时刻，10个失败。目标侵入最大0.331715375mm，非目标/错误区域最大0.375185411mm；部分时刻指腹真实跨面为0，其他时刻pad超出原可触区域。失败时间与原始布尔详见LOCAL_PATH_FEASIBILITY.json和LOCAL_PATH_ACTUAL_SAMPLES.json。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_contact_junction_compatibility_r1/FINAL_RECOMMENDATION.md)

## 技术路线

> **建议B：接触状态合同成立，但本轮局部延拓与节点间路径表示不足，需要成熟接触约束运动规划方法的同输入实际对照。** 保留现有FK、蒙皮、真实几何验收与SLSQP静态求解；本轮未证明其他后端更好。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_contact_junction_compatibility_r1/FINAL_RECOMMENDATION.md)

> 提前换位：纠正后的新离散点相对P2腕移1.119713mm；中指pad到E5可触面距离从23.857588降到22.692997mm。真实几何通过，但求解预算终止、非收敛。最远准备位置及与B2的连续可达性未确定。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_contact_junction_compatibility_r1/FINAL_RECOMMENDATION.md)

## 测试结论

> **建议B：接触状态合同成立，但本轮局部延拓与节点间路径表示不足，需要成熟接触约束运动规划方法的同输入实际对照。** 保留现有FK、蒙皮、真实几何验收与SLSQP静态求解；本轮未证明其他后端更好。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_contact_junction_compatibility_r1/FINAL_RECOMMENDATION.md)

> |BOUNDARY_CONTRACT_PASS|通过，原MIDI/Action一致|

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_contact_junction_compatibility_r1/FINAL_RECOMMENDATION.md)

## 失败原因与证据边界

> 尚未解决的问题：保持接触的可行集合曲率与键面随时间运动，需要在节点之间持续约束。四个局部下压节点收敛且全部通过；同一C1控制路径24个实际样本中10个失败，直接显示节点可行性不能由插值继承。中间节点虽保持参考手型，仍有目标/错误区域侵入及接触失效。单纯更换点IK求解器不能自动补上这一接口。

出处：[PRODUCT_ROUTE_REVIEW.md](../research/experiments/hands_contact_junction_compatibility_r1/PRODUCT_ROUTE_REVIEW.md)

## 后续建议

> **建议B：接触状态合同成立，但本轮局部延拓与节点间路径表示不足，需要成熟接触约束运动规划方法的同输入实际对照。** 保留现有FK、蒙皮、真实几何验收与SLSQP静态求解；本轮未证明其他后端更好。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_contact_junction_compatibility_r1/FINAL_RECOMMENDATION.md)

> 唯一局部路径：2.913092667–2.938092667秒，25ms；在共同构型附近起步，未连接B2/P2。四个后续节点都收敛并通过；120Hz基础采样加风险区补采样共24个时刻，10个失败。目标侵入最大0.331715375mm，非目标/错误区域最大0.375185411mm；部分时刻指腹真实跨面为0，其他时刻pad超出原可触区域。失败时间与原始布尔详见LOCAL_PATH_FEASIBILITY.json和LOCAL_PATH_ACTUAL_SAMPLES.json。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_contact_junction_compatibility_r1/FINAL_RECOMMENDATION.md)

## 原报告与关键代码

- [experiments/hands_contact_junction_compatibility_r1/FINAL_RECOMMENDATION.md](../research/experiments/hands_contact_junction_compatibility_r1/FINAL_RECOMMENDATION.md)
- [experiments/hands_contact_junction_compatibility_r1/PRODUCT_ROUTE_REVIEW.md](../research/experiments/hands_contact_junction_compatibility_r1/PRODUCT_ROUTE_REVIEW.md)
- [experiments/hands_contact_junction_compatibility_r1/CROSS_EVENT_REUSE_CHECK.md](../research/experiments/hands_contact_junction_compatibility_r1/CROSS_EVENT_REUSE_CHECK.md)
- [experiments/hands_contact_junction_compatibility_r1/JUNCTION_CONTACT_SEMANTICS.md](../research/experiments/hands_contact_junction_compatibility_r1/JUNCTION_CONTACT_SEMANTICS.md)
- [experiments/hands_contact_junction_compatibility_r1/contact_solver_attempt1.py](../../src/legacy/experiments/hands_contact_junction_compatibility_r1/contact_solver_attempt1.py)
- [experiments/hands_contact_junction_compatibility_r1/contact_solver_hold_distance.py](../../src/legacy/experiments/hands_contact_junction_compatibility_r1/contact_solver_hold_distance.py)
- [experiments/hands_contact_junction_compatibility_r1/finalize_reports.py](../../src/legacy/experiments/hands_contact_junction_compatibility_r1/finalize_reports.py)
- [experiments/hands_contact_junction_compatibility_r1/local_key_states.py](../../src/legacy/experiments/hands_contact_junction_compatibility_r1/local_key_states.py)
- [experiments/hands_contact_junction_compatibility_r1/prepare.py](../../src/legacy/experiments/hands_contact_junction_compatibility_r1/prepare.py)
- [experiments/hands_contact_junction_compatibility_r1/prepare_local_sampling.py](../../src/legacy/experiments/hands_contact_junction_compatibility_r1/prepare_local_sampling.py)
- [experiments/hands_contact_junction_compatibility_r1/run_hold_continuation.py](../../src/legacy/experiments/hands_contact_junction_compatibility_r1/run_hold_continuation.py)
- [experiments/hands_contact_junction_compatibility_r1/run_hold_corrected.py](../../src/legacy/experiments/hands_contact_junction_compatibility_r1/run_hold_corrected.py)
- [experiments/hands_contact_junction_compatibility_r1/run_local_path.py](../../src/legacy/experiments/hands_contact_junction_compatibility_r1/run_local_path.py)
- [experiments/hands_contact_junction_compatibility_r1/verify_local_path.py](../../src/legacy/experiments/hands_contact_junction_compatibility_r1/verify_local_path.py)

## 输入、输出与大型证据

该目录原始成员 128 项；拟公开身份记录 79 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
