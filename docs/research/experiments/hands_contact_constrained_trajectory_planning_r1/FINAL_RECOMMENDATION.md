# 最终技术决定

**B：现有接触合同及FK/蒙皮有效，成熟外部方法已执行，但未显示充分优势。** 结论为CONTACT_PATH_NOT_FOUND_WITHIN_BUDGET。不继续扩大窗口或求解次数。

|门禁|本轮结果|
|---|---|
|OPEN_SOURCE_TRAJECTORY_PLANNER_REVIEWED|通过，3个候选组源码/平台/许可对照|
|REAL_TRAJECTORY_PLANNER_ADAPTER_EXECUTED|通过，CasADi＋IPOPT真实多时刻轨迹问题；非单点IK|
|CONTACT_CONSTRAINED_PATH_FOUND|未通过|
|LOCAL_BOUNDARY_SAMPLED_PASS|未通过|
|FIXED_MIDI_TIME_FEASIBLE|未确定；不能由非收敛宣称时间不可行|
|FULL_SHORT_BRIDGE_SAMPLED_PASS_HUMAN_PENDING|NOT_EXECUTED，局部门禁失败|
|PATH_FOUND_TIMING_BLOCKED|不适用，尚无合格接触路径|
|CONTACT_PATH_NOT_FOUND_WITHIN_BUDGET|成立|
|TOOL_ADAPTATION_BLOCKED / FAIL_CLOSED|最终不适用：适配实际进入优化；源保护正常|

唯一局部候选覆盖2.913092667–2.938092667秒。IPOPT31次可核实迭代后超时，未收敛。31条实际Blender记录包含30个时间采样与1个边界左极限；接触在12条记录失败，首次采样失败2.926634333秒，之前通过点为2.925592667秒（不是声称精确失效发生时刻）。最终E5指腹悬空2.615577760mm，保留原始布尔，不四舍五入改判。

最大目标侵入0.115401647mm，非目标/错误区域0.196891178mm；非相邻指面交叉0，关节参考族/轴/域在样本处通过，中指/无名指最小精确间隙3.056809mm。这些分项不能替代失败的接触门禁或Human自然度认可。

同样24个旧时刻，新候选12个失败，旧候选10个失败；相同采样腕速峰值从3104.531降至461.215mm/s，差分加速度从1314580.610降至44076.265mm/s²。120Hz粗网格和含微秒边界探针的原始运动学分别保存，不混用统计。微秒间隔差分受Blender浮点精度和未收敛边界残差影响，巨大的原始加速度不能当作可靠人体运动量；边界实际腕位置差0.000194287mm也保留，未宣称精确C2通过。

**是否已经得到真正可复用的接触约束连续规划方法？尚未。** 已接通联合时间外部优化，但主要卡在接触保持与非收敛；约170秒用于34次约束Jacobian评估。没有证据把失败归因于人体、C01或固定MIDI时长。下一项唯一关键工作是同输入下的稀疏接触导数/可行性恢复接口验证，不是再修静态节点。

数值工作保守总计441.296秒，低于600秒；包括中断表达尝试及10秒建模计费余量。源码/安装与独立验收另计。重定向日志曾造成阶段误判，已根据完整IPOPT输出纠正；最终证据以CASADI_LOCAL_SOLVE.json和真实Blender记录为准。

B2到E5+35ms的428.571ms窗口未执行，R06→R07入口未验证。无新Action、视频、诊断Blend或静帧；所有控制与失败证据只存隔离目录。保护复核详见PROTECTION_CHECK.json。

**DESIGN_PROVISIONAL — STOP — HUMAN REVIEW。** 不自动进入B02、23音双手或教材生产。
