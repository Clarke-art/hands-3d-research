# GUARD_FIX实现

旧输出把reference PCHIP与envelope×correction PCHIP相加；新实现只对合法的**总关节角度支持点**作一次PCHIP。优化未知量直接是actual_delta_deg，旧latent在本轮定义为相同的实际修正参数；没有delta/envelope除法，没有插值后再乘envelope。phase envelope只确定原准备/恢复窗口，不能隐式改变修正预算。

静态/正式共用actual_delta_bounds和total_angles，使用原R3相同的每DOF实际修正预算及原工程域。最终输出还检查实际修正全曲线预算，不能仅检查节点。接触区域及其参数未改。

保持原113个支撑点。标量PCHIP的节点i影响i-2..i+2范围；只有该完整影响范围严格落在原活动窗口内的节点才允许修正。冻结影响边缘，使窗口外总q及窗口边界位置/导数精确复用R2。所有root及键角完全固定。新曲线仍为全局C1 PCHIP，不在窗口边界拼接两条具有不同斜率的曲线。

PCHIP保域性质由合法节点及各标量段的保形行为支持；实现另逐段求三次多项式的端点与导数实根，确认连续域、实际修正预算和全部窗口边界，不以名称代替验证。113节点、827原输出采样和真实事件/窗口边界共享同一评价器和严格guard。

未裁剪输出角度，未放宽工程域或原1e-7度guard容差。唯一有clip的是正式求解**初始化参数**进入已锁定可行参数域，它不修改结果或强制PASS。求解返回即保存实际终止状态、raw actual参数、support total q；guard前保存全部输出和违规mask，失败也留下JSON证据。

冻结Rig/Mesh/Weights、接触区域、root、MIDI和历史文件均未修改。
