# 执行、真实几何与连续性验证

**INCONCLUSIVE — 实现错误导致真实终态复核未执行，目标重组未开始。** 原始局部优化终态完整保存。

运行顺序：prepare输入/数值FK/持久化测试PASS → 一批三个来源局部求解均返回 → 唯一来源真实Blender诊断启动后退出7。错误为[source_actual.py:10](../../../artifacts/cec87c8d9845b558183f.md)访问`I['source_scene']`，实际[INPUT_BINDINGS.json](../../../artifacts/6f97fc3d6cf4e466d1c5.md)字段是`scene`。输入预检验证了MIDI、FK与局部残差和输出读回，却遗漏Blender诊断输入契约。失败发生在`bpy.ops.wm.open_mainfile`之前；没有读取C1姿态、执行真实修改后skin诊断或产生几何结果。完整现场见[source_actual.log](../../../artifacts/15d2f5220f19ead9acab.md)、[STOP_RECORD.json](../../../../examples/historical/experiments/hands_role_aware_motion_recomposition_r1/STOP_RECORD.json)。未修改失败脚本，未重跑诊断或求解。

三个原始结果[SOURCE_LOCAL_RESULT_0.npz](../../../../examples/historical/experiments/hands_role_aware_motion_recomposition_r1/SOURCE_LOCAL_RESULT_0.npz)、[SOURCE_LOCAL_RESULT_1.npz](../../../../examples/historical/experiments/hands_role_aware_motion_recomposition_r1/SOURCE_LOCAL_RESULT_1.npz)、[SOURCE_LOCAL_RESULT_2.npz](../../../../examples/historical/experiments/hands_role_aware_motion_recomposition_r1/SOURCE_LOCAL_RESULT_2.npz)均优先原子保存，然后才计算数值汇总。各文件含x/x0、残差、梯度、active_mask、全手q、共同Rig矩阵、88键角度，内嵌success/message/nfev/njev/cost/optimality、残差调用数与累计耗时。临时文件fsync、读回一致再原子替换；现有证据不可覆盖。本次没有恢复任何P3历史丢失终态。[RESULT_READBACK_CHECK.json](../../../../examples/historical/experiments/hands_role_aware_motion_recomposition_r1/RESULT_READBACK_CHECK.json)确认三个结果完整、有限、同腕且其余四指不变。

| 证据级别 | 本轮结果 |
|---|---|
| 来源信息提取 | 部分完成，239源样本和事件/键面锚点 |
| 来源活动指有限静态数值校正 | 三点数值接触与本指邻键深度通过 |
| 修改后来源真实skin安全 | UNKNOWN；Blender输入错误，0个确认样本 |
| 目标角色重组表示生成 | NOT_TESTED，外层求解0 |
| 目标活动接触/全手skin与88键 | NOT_TESTED |
| 完整限定窗口连续验证 | NOT_TESTED |
| Human自然度 | NOT_TESTED |

Stage 2仅锁定八个参数，没有执行或构建第二方案：共享腕Y ±8mm、Z ±5mm；第一/第二活动角色PIP ±4°；中指/食指闲置MCP 0–8°；拇指闲置CMC 0–5°；第一角色释放MCP 0–8°。局部IK内部6变量另行记账。指法、时序、Rig自由度与原合法域未更改；没有将8.70mm P3条件缺口用作固定腕位移。

目标黑键F♯5与白键G5需要不同高度、纵深和邻键协调，不可把C5→D5整体平移视为适配。当前没有生成共享腕适配曲线、释放/准备/闲置角色曲线、PCHIP目标轨迹或入口/出口速度连接证据。因停止原因是程序字段错误，不能声称目标触键不可达、存在确定几何冲突、时间不足或必须全手重求解。

来源局部求解进程9.280071秒，其中求解脚本报告三点处理累计6.879068秒（含保存及数值诊断，不是纯优化CPU时间）；prepare 2.528121秒；失败Blender诊断0.724040秒。预算保守计入三个进程全耗时，总数值执行12.532232/180秒，另列Blender诊断0.724040秒。报告与SHA核查单列，最终数值见[COMPUTE_LEDGER.json](../../../../examples/historical/experiments/hands_role_aware_motion_recomposition_r1/COMPUTE_LEDGER.json)。`total_process_seconds`为受控子进程累计，并非包含代码编写/阅读的总工作时长；审计闭合同时登记目录创建至闭合的壁钟区间。

新Action、候选Blend、视频、正式动态候选均0。没有可用于与原目标C1比较的动作质量或完整生成/验证成本；不得以这三个静态求解的成本声称优于792变量P3或原C1全手优化。

本轮实际引用源文件26项前后SHA核查PASS，详见[PROTECTION_CHECK.json](../../../artifacts/70bf3499fe1e9f3eaec7.md)；关键执行代码和锁定政策见[EXECUTED_CODE_SHA.json](../../../../examples/historical/experiments/hands_role_aware_motion_recomposition_r1/EXECUTED_CODE_SHA.json)。独立piano无访问；历史并发保护FAIL没有撤销。保护结论只覆盖实际引用文件，不是无关全目录审计。
