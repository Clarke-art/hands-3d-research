# 最终建议：路线B，停止G4→E5专项局部修补

DESIGN_PROVISIONAL — STOP — HUMAN REVIEW

**能真正利用前一个音符的持键时间做部分提前准备；尚不能让已验证局部动作获得完整、自然的真实入口。** 本轮从实际B2起点、原MIDI时序与冻结Rig出发完成一次主入口候选和唯一针对性修正。入口整体FAIL，不能报告PASS，也没有证明当前指法或人体动作绝对不可行。

最强实际证据是主候选从 2.527855000s 到 2.777855000000s 的采样可行前缀：40个时刻、250.000ms，腕移15.419mm，中指到E5可触面的距离从27.667降至16.332mm。G4真实面级接触、88键侵入、非相邻指面与关节门禁通过。有限采样不构成连续无碰撞数学证明，Human自然度尚未批准。

全入口共 85 个独立Blender样本，45个失败。补采样后的首个失败为 2.778896666667s，中指与D#5错误区域侵入 0.254667mm；整段最大错误区域侵入3.872186mm >0.25mm。E5在2.928717666667s和终点2.936009333333s接触失败。目标键最大侵入0.199001mm，非相邻指面交叉0，关节族/域均通过；这些通过不能覆盖错误区域和接触失败。

腕速峰值320.521mm/s、关节速率峰值206.167deg/s，原速率门禁通过。候选位置连续，但节点速度跳变，节点处有限加速度和自然度没有成立。旧共同边界到旧局部入口67.007mm，在14.583ms内固定连接不可行；本轮端点允许调整，仍未打通几何和接触入口。因此既有2.083ms片段原样保留为技术资产，不能升级为整段动作。

主要问题是音乐上下文中的手位/指尖清障路线、受限运动表示与接触几何代理稳定性。实时多尺度导数保护确实参与求解，并拒绝未验证分支；原伪不连续代理已在实验副本修正，最终IPOPT仍因新的局部导数不一致停止，未收敛。没有证据把所有失败归咎于原接触合同，也不能以预算内搜索失败证明人体不可能。

建议保留冻结Rig、真实蒙皮、Action、合同、参考族、稀疏接口与验收，转向较长上下文手位规划、动作先验+接触IK，以及运动可行性反馈到指法。不要再以增加几个静态节点、优化几毫秒或提高迭代数作为下一里程碑。下一最小产品任务是新的高层方案在同一真实B2入口完整通过原时序和几何门禁；之后才考虑完整25ms及E5 ON+35ms验收。

|最终门禁|结果|
|---|---|
|G4_HOLD_PREPARATION_FEASIBLE|PASS_SAMPLED_PREFIX_ONLY|
|ENTRY_KINEMATIC_BOUNDS_VERIFIED|True|
|ENTRY_TARGET_REACHABLE|False|
|EARLY_PREPARATION_PATH_SAMPLED_PASS|False|
|ENTRY_CONTACT_TIMING_PASS|False|
|ENTRY_MOTION_BOUNDS_PASS|PASS_SCOPED_TO_ORIGINAL_SPEED_RATE_GATES|
|NONSMOOTH_DERIVATIVE_GUARDED|PARTIAL: IN_SOLVER_GUARD_EXECUTED_AND_REJECTION_ENFORCED; UNIVERSAL_AND_NEW_SELF_AXIS_COVERAGE_UNPROVEN|
|ENTRY_NOT_FOUND_WITHIN_BUDGET|True|
|PRODUCT_ROUTE_PIVOT_REQUIRED|True|
|FAIL_CLOSED|True|

数值阶段总墙钟269.080000s <600s；一条主候选和一次有证据修正，无随机重启。扩展保护集85850个文件独立前后重算：3个变化、15个新增、删除0，全部发生在同期另一个聊天授权生成的Piano存储清理审计目录，保留原变更并将全集合标FAIL。继承冻结清单9277个文件、所有Hands历史及原MIDI/C01/Action/Rig身份均一致；没有恢复或覆盖其他聊天成果。范围与并发证据见 PROTECTION_SCOPE_AUDIT.json。完整实际蒙皮/FK最大误差0.001087222mm。未输出正式Action、Blend、视频或诊断静帧。

八项交付齐全，所有原始候选、拒绝导数和失败采样保留。批准前停止，不自动进入25ms回归、B02、23音双手动画、其他代表音型或教材生产。
