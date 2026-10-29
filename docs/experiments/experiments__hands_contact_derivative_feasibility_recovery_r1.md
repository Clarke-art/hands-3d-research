# experiments/hands_contact_derivative_feasibility_recovery_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> - 原最终失败点真实指腹间隙2.615578mm，经动态检测恢复5次SLSQP迭代，约6.531s；Blender接触/侵入/自交/解剖门禁全通过。目标侵入0.005065796mm、错误区域侵入0、非相邻指面交叉0。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_contact_derivative_feasibility_recovery_r1/FINAL_RECOMMENDATION.md)

> 目标依赖相邻控制系数的一阶至三阶差分及姿态偏好。接触、琴键碰撞、自碰撞仅依赖本节点z；腕速/腕加速度依赖本节点(z,zd,za)。Bernstein节点依赖本段6个控制系数（端点出现自然零）；两段仅通过C0/C1/C2相连。不是将不相邻时间人为置零。

出处：[CASADI_JACOBIAN_ROOT_CAUSE.md](../research/experiments/hands_contact_derivative_feasibility_recovery_r1/CASADI_JACOBIAN_ROOT_CAUSE.md)

## 技术路线

> - J1/J2/原失败点固定图导数通过；真实裁剪指腹面在失效/恢复点通过。J3自碰撞分离轴min/max有非光滑支，故 `DERIVATIVE_METHOD_PARTIAL` 保留，不能宣称所有切换均验证。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_contact_derivative_feasibility_recovery_r1/FINAL_RECOMMENDATION.md)

> |DERIVATIVE_METHOD_PARTIAL|成立|

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_contact_derivative_feasibility_recovery_r1/FINAL_RECOMMENDATION.md)

## 测试结论

> - J1/J2/原失败点固定图导数通过；真实裁剪指腹面在失效/恢复点通过。J3自碰撞分离轴min/max有非光滑支，故 `DERIVATIVE_METHOD_PARTIAL` 保留，不能宣称所有切换均验证。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_contact_derivative_feasibility_recovery_r1/FINAL_RECOMMENDATION.md)

> - 25ms回归 `NOT_EXECUTED`，新轨迹候选0，无新24样本连续轨迹PASS。固定MIDI时间可行性仍未知。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_contact_derivative_feasibility_recovery_r1/FINAL_RECOMMENDATION.md)

## 失败原因与证据边界

> - J1/J2/原失败点固定图导数通过；真实裁剪指腹面在失效/恢复点通过。J3自碰撞分离轴min/max有非光滑支，故 `DERIVATIVE_METHOD_PARTIAL` 保留，不能宣称所有切换均验证。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_contact_derivative_feasibility_recovery_r1/FINAL_RECOMMENDATION.md)

> 原失效控制状态在原事件时间、原Action与关节域下，通过原SLSQP动态三角面约束恢复；3个点均经真实Blender几何/解剖门禁通过。但独立恢复点之间速度约4639与5284mm/s，超过原500mm/s。**静态接触集存在，不代表这些状态可以在既定相邻时刻互相到达。** 固定证书恢复失败而动态检测恢复成功，说明局部证书的适用邻域和活动集合更新值得保留为结构性问题。

出处：[PRODUCT_ROUTE_REVIEW.md](../research/experiments/hands_contact_derivative_feasibility_recovery_r1/PRODUCT_ROUTE_REVIEW.md)

## 后续建议

> 下一阶段由Human决定是否立项：先比较更早的手位准备、接触状态与运动的联合表示、指法的运动可行性反馈、动作先验的代价；本轮不更换架构、指法或MIDI。任何短时路径试验前应先选择满足原速度条件的相邻可行状态及稳定活动集策略。禁止直接把现有独立恢复点插值作为结果。

出处：[PRODUCT_ROUTE_REVIEW.md](../research/experiments/hands_contact_derivative_feasibility_recovery_r1/PRODUCT_ROUTE_REVIEW.md)

> 产品成本限制：原J4图观察RSS约8.95GB，未获得成对峰值内存优势证据；跨MIDI只验证另一既有RELEASE类型，广泛复用仍需后续门禁。固定MIDI时长可行性仍未确定；预算内失败不等于人体不可演奏。

出处：[PRODUCT_ROUTE_REVIEW.md](../research/experiments/hands_contact_derivative_feasibility_recovery_r1/PRODUCT_ROUTE_REVIEW.md)

## 原报告与关键代码

- [experiments/hands_contact_derivative_feasibility_recovery_r1/FINAL_RECOMMENDATION.md](../research/experiments/hands_contact_derivative_feasibility_recovery_r1/FINAL_RECOMMENDATION.md)
- [experiments/hands_contact_derivative_feasibility_recovery_r1/PRODUCT_ROUTE_REVIEW.md](../research/experiments/hands_contact_derivative_feasibility_recovery_r1/PRODUCT_ROUTE_REVIEW.md)
- [experiments/hands_contact_derivative_feasibility_recovery_r1/CASADI_JACOBIAN_ROOT_CAUSE.md](../research/experiments/hands_contact_derivative_feasibility_recovery_r1/CASADI_JACOBIAN_ROOT_CAUSE.md)
- [experiments/hands_contact_derivative_feasibility_recovery_r1/CONTACT_DERIVATIVE_CONTRACT.md](../research/experiments/hands_contact_derivative_feasibility_recovery_r1/CONTACT_DERIVATIVE_CONTRACT.md)
- [experiments/hands_contact_derivative_feasibility_recovery_r1/contact_solver.py](../../src/legacy/experiments/hands_contact_derivative_feasibility_recovery_r1/contact_solver.py)
- [experiments/hands_contact_derivative_feasibility_recovery_r1/derivative_probe.py](../../src/legacy/experiments/hands_contact_derivative_feasibility_recovery_r1/derivative_probe.py)
- [experiments/hands_contact_derivative_feasibility_recovery_r1/direct_original.py](../../src/legacy/experiments/hands_contact_derivative_feasibility_recovery_r1/direct_original.py)
- [experiments/hands_contact_derivative_feasibility_recovery_r1/extra_probe.py](../../src/legacy/experiments/hands_contact_derivative_feasibility_recovery_r1/extra_probe.py)
- [experiments/hands_contact_derivative_feasibility_recovery_r1/final_check.py](../../src/legacy/experiments/hands_contact_derivative_feasibility_recovery_r1/final_check.py)
- [experiments/hands_contact_derivative_feasibility_recovery_r1/neighbors.py](../../src/legacy/experiments/hands_contact_derivative_feasibility_recovery_r1/neighbors.py)
- [experiments/hands_contact_derivative_feasibility_recovery_r1/pruned_probe.py](../../src/legacy/experiments/hands_contact_derivative_feasibility_recovery_r1/pruned_probe.py)
- [experiments/hands_contact_derivative_feasibility_recovery_r1/resource_profile.py](../../src/legacy/experiments/hands_contact_derivative_feasibility_recovery_r1/resource_profile.py)
- [experiments/hands_contact_derivative_feasibility_recovery_r1/stage2.py](../../src/legacy/experiments/hands_contact_derivative_feasibility_recovery_r1/stage2.py)
- [experiments/hands_contact_derivative_feasibility_recovery_r1/surface_derivative.py](../../src/legacy/experiments/hands_contact_derivative_feasibility_recovery_r1/surface_derivative.py)
- [experiments/hands_contact_derivative_feasibility_recovery_r1/reproduction/_derivative_r1_direct_prepare.py](../../src/legacy/experiments/hands_contact_derivative_feasibility_recovery_r1/reproduction/_derivative_r1_direct_prepare.py)
- [experiments/hands_contact_derivative_feasibility_recovery_r1/reproduction/_derivative_r1_extra.py](../../src/legacy/experiments/hands_contact_derivative_feasibility_recovery_r1/reproduction/_derivative_r1_extra.py)

## 输入、输出与大型证据

该目录原始成员 106 项；拟公开身份记录 76 项。
- `experiments/hands_contact_derivative_feasibility_recovery_r1/ORIGINAL_G.casadi` → `hands-research-r1-selected-012.zip` / `payload/experiments/hands_contact_derivative_feasibility_recovery_r1/ORIGINAL_G.casadi`
- `experiments/hands_contact_derivative_feasibility_recovery_r1/PRUNED_G.casadi` → `hands-research-r1-selected-012.zip` / `payload/experiments/hands_contact_derivative_feasibility_recovery_r1/PRUNED_G.casadi`
- `experiments/hands_contact_derivative_feasibility_recovery_r1/PRUNED_J.casadi` → `hands-research-r1-selected-012.zip` / `payload/experiments/hands_contact_derivative_feasibility_recovery_r1/PRUNED_J.casadi`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
