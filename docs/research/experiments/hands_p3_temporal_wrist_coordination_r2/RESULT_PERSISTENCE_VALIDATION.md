# 结果保存验证

**RESULT_PERSISTENCE_GATE = PASS。实际异常状态已完整留证；正式优化返回终态未产生。**

R1第106行调用`surface_metrics`，而其原导入代码只截取上一轮evaluate.py中`M=read(MODEL/...)`至`ref_t=REF`之前的内容；函数定义位于该截取范围之后。本轮problem.py在隔离副本显式导入该函数。R1源码、失败日志与不可恢复的历史终态未改写，未声称恢复R1结果。

Gate 1在正式优化前独立通过：确定性x、fun、grad、active_mask、状态序列、时间、接触XY、稀疏Jacobian结构及迭代元数据全部序列化并逐字段读回。另做已知接触函数测试。模拟异常可保存最后有限状态；模拟写入失败证明已有最终记录及旧检查点SHA不变；同名最终结果写入直接拒绝。

保存方式是同一NPZ内的数值数组＋UTF-8 JSON元数据，先在本目录写`.pending`、flush/fsync、重新读取核对，再原子替换。最终结果文件不可覆盖；可更新的检查点使用独立文件。测试产生的pending证据保留，并不代表正式终态。二级诊断或报告失败不会删除原始结果。

本地SciPy 1.18.1支持callback；本轮采用与实际接口兼容的更小方案：残差完整返回有限值后，至少每5秒原子保存一次独立检查点，异常时保存最后有限参数、残差、调用计数、耗时和完整traceback。检查点可能是有限差分试探点，明确标为中间状态，未冒充已接受迭代。保存机制没有重写优化框架。

正式代码预先规定：least_squares返回后先保存完整参数、fun、grad、active_mask、实际Jacobian、nfev/njev/status、耗时及时间节点等，再做几何诊断。但实际唯一求解在锁定74秒上限处抛出受控TimeoutError，**没有产生OptimizeResult**，所以不能提供实际nfev、njev、收敛状态、返回Jacobian或“最终最优参数”。Gate 1证明的是该保存路径的自测可靠性，不能当本次返回终态存在的证据。

实际异常留证：4424次残差调用，异常记录耗时74.569秒；有限参数792维。`EXCEPTION_LAST_FINITE_STATE.npz`与`LAST_FINITE_EVALUATION.npz`均能读取；`INTERRUPTED_STATE_BUNDLE.npz`补充解码后的32时刻26维状态、触点、原参考、原初始状态、边界和稀疏结构，未计算新的可行性结果，未覆盖原异常文件。完整现场见[solve.log](../../../artifacts/15ae088bddb4d4eda603.md)、[FORMAL_EXCEPTION.json](../../../../examples/historical/experiments/hands_p3_temporal_wrist_coordination_r2/FORMAL_EXCEPTION.json)。

正式优化前，输入预检曾发现24个速度／加速度权重无法匹配26维状态。本轮修正为原A2三个旋转分量各用既有同一权重，保留`POLICY_PRE_INPUT_REPAIR.json`、源码副本及失败日志；修正并通过输入门禁后才锁定并启动一次优化。这不是优化失败后的参数重试。

报告子进程已返回0、文件及账本已写入，父进程随后预览stdout日志时遇到Windows编码与UTF-8不一致的UnicodeDecodeError。这只影响日志文本展示，没有重跑报告或优化，原日志保留；交付阶段另行核对三份UTF-8报告及原始异常文件SHA。

证据：[RESULT_PERSISTENCE_GATE.json](../../../../examples/historical/experiments/hands_p3_temporal_wrist_coordination_r2/RESULT_PERSISTENCE_GATE.json)、[INPUT_CONTRACT_GATE.json](../../../../examples/historical/experiments/hands_p3_temporal_wrist_coordination_r2/INPUT_CONTRACT_GATE.json)、[EVIDENCE_SUMMARY.json](../../../../examples/historical/experiments/hands_p3_temporal_wrist_coordination_r2/EVIDENCE_SUMMARY.json)。

**STOP — HUMAN REVIEW**
