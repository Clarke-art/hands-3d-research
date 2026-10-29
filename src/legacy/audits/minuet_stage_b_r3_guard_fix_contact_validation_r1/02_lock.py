from stage_common import *
assert not (P/'CANDIDATE_ATTEMPT.json').exists()
v=read(P/'PREGENERATION_VALIDATION.json');assert v['pass_']
(P/'GUARD_FIX_IMPLEMENTATION.md').write_text('''# GUARD_FIX实现

旧输出把reference PCHIP与envelope×correction PCHIP相加；新实现只对合法的**总关节角度支持点**作一次PCHIP。优化未知量直接是actual_delta_deg，旧latent在本轮定义为相同的实际修正参数；没有delta/envelope除法，没有插值后再乘envelope。phase envelope只确定原准备/恢复窗口，不能隐式改变修正预算。

静态/正式共用actual_delta_bounds和total_angles，使用原R3相同的每DOF实际修正预算及原工程域。最终输出还检查实际修正全曲线预算，不能仅检查节点。接触区域及其参数未改。

保持原113个支撑点。标量PCHIP的节点i影响i-2..i+2范围；只有该完整影响范围严格落在原活动窗口内的节点才允许修正。冻结影响边缘，使窗口外总q及窗口边界位置/导数精确复用R2。所有root及键角完全固定。新曲线仍为全局C1 PCHIP，不在窗口边界拼接两条具有不同斜率的曲线。

PCHIP保域性质由合法节点及各标量段的保形行为支持；实现另逐段求三次多项式的端点与导数实根，确认连续域、实际修正预算和全部窗口边界，不以名称代替验证。113节点、827原输出采样和真实事件/窗口边界共享同一评价器和严格guard。

未裁剪输出角度，未放宽工程域或原1e-7度guard容差。唯一有clip的是正式求解**初始化参数**进入已锁定可行参数域，它不修改结果或强制PASS。求解返回即保存实际终止状态、raw actual参数、support total q；guard前保存全部输出和违规mask，失败也留下JSON证据。

冻结Rig/Mesh/Weights、接触区域、root、MIDI和历史文件均未修改。
''',encoding='utf8')
(P/'PREGENERATION_VALIDATION.md').write_text(f'''# 生成前门禁：PASS

- 零修正：新总q评价器与R2保存动作最大差{v['zero_correction_max_abs_deg']:.3g}度；root、事件与原数组保持。窗口外精确保持，全部工程域及实际修正预算通过连续多项式证书。
- 非零工程小数组：在原113节点、827输出时间和边界上核验实际域、窗口外不变与C1；不是演奏候选。
- 原人工反例：旧分开插值相加超限约{v['old_counterexample_max_excess_deg']:.6f}度；新总q插值域内；人为非法q仍被严格guard拒绝。
- 失败记录人工测试：checkpoint先于guard拒绝写入，真实nfev字段与callback计数分开。
- 预算统一：10个有限静态pose求解与正式使用相同actual_delta_deg及原R3每DOF预算；所有实际域与触键余量检查通过。不把旧静态结果直接冒充新预检。
- 接触区域：与原R3完全相同，无逐音坐标、特殊指法或root偏移。
- 自然动作保护：完整PCHIP影响范围须在原窗口内；窗外与边界速度固定为R2，root不优化。

可修改节点数按指号：{v['mutable_nodes_by_finger']}；实际未知量{v['free_actual_delta_parameters']}个。正式求解尚未启动时写入此报告，生成前只锁定一次；正式允许一次求解，不重试。

详细证据见PREGENERATION_VALIDATION.json与preflight.log。本轮先前工具中断发生在人工checkpoint之前，无静态求解结果或正式候选产生；恢复后的有效预检10次静态pose，正式attempt仍0。
''',encoding='utf8')
names=['stage_common.py','total_angle_pipeline.py','03_generate_once.py']
dump('GENERATION_LOCK.json',dict(scripts={n:sha(P/n) for n in names},policy_sha256=sha(P/'GENERATION_POLICY.json'),timeline_sha256=sha(P/'PERFORMANCE_TIMELINE.json'),pregeneration_sha256=sha(P/'PREGENERATION_VALIDATION.json'),baseline_bind_sha256=sha(P/'BASELINE_BIND.json'),locked_before_formal_solve=True,formal_attempt_limit=1,candidate_limit=1))
print('SINGLE_POLICY_LOCKED_AFTER_ALL_PRECHECKS',flush=True)
