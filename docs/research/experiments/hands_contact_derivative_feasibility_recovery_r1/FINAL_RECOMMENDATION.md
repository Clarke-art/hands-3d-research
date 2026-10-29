# 最终判断

**A：导数及可行性恢复取得可靠进展。** 保留改进接口；不进入连续运动生产。全部结果 `DESIGN_PROVISIONAL`。

- 原三节点Jacobian约1.154221s → 0.038489s，**29.99倍**；剪枝前后约束值及Jacobian逐元素差0。多步长检查细步长最大误差4.31e-9，无遗漏可检测非零依赖。
- J1/J2/原失败点固定图导数通过；真实裁剪指腹面在失效/恢复点通过。J3自碰撞分离轴min/max有非光滑支，故 `DERIVATIVE_METHOD_PARTIAL` 保留，不能宣称所有切换均验证。
- 原最终失败点真实指腹间隙2.615578mm，经动态检测恢复5次SLSQP迭代，约6.531s；Blender接触/侵入/自交/解剖门禁全通过。目标侵入0.005065796mm、错误区域侵入0、非相邻指面交叉0。
- 相邻两个原失败点亦通过全部静态门禁；恢复点间腕速约4639.371与5283.768mm/s，超过原500mm/s，判定 **CONTACT_RECOVERED_BUT_MOTION_INCOMPATIBLE**。
- 25ms回归 `NOT_EXECUTED`，新轨迹候选0，无新24样本连续轨迹PASS。固定MIDI时间可行性仍未知。
- 数值过程保守计费 **225.170/600s**，包含导数建图/探针、重复诊断、失败启动、恢复与独立Blender回放。细分见TOTAL_NUMERICAL_BUDGET.json。

|验收标记|结果|
|---|---|
|CONTACT_DERIVATIVE_VERIFIED|限定于已测平滑面分支PASS|
|SPARSE_JACOBIAN_VERIFIED|限定于已测真实依赖PASS|
|JACOBIAN_SPEEDUP_CONFIRMED|PASS（三节点）|
|CONTACT_FEASIBILITY_RECOVERED|PASS（3个独立静态点）|
|CONTACT_RECOVERED_BUT_MOTION_INCOMPATIBLE|成立|
|LOCAL_25MS_SAMPLED_PASS_HUMAN_PENDING|未通过 / NOT_EXECUTED|
|DERIVATIVE_METHOD_PARTIAL|成立|
|FEASIBILITY_RECOVERY_BLOCKED|最终不成立；固定证书阶段失败保留|
|METHOD_BLOCKED|底层接口不阻塞；连续运动未证明|
|FAIL_CLOSED|对连续路径/生产门禁保持关闭|

源码、原始单次计时、多步长差分、阶段失败和Blender日志均保留。独立重算9171个受保护文件哈希，0处变化、0个缺失（PROTECTION_CHECK.json）；不修改冻结Rig、批准姿态、Stage A/B/C、原MIDI或琴键Action，无新Action、视频或Blend。

**STOP — HUMAN REVIEW。** 未经Human授权，不进入长窗口、B02、23音双手动画或正式教材生产。
