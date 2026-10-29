# R3动态失败现场与证据恢复

本轮仅诊断，正式/静态求解调用均0，动态候选0，Blender Action和motion.npz新增0。

**FINAL_FAILED_TRAJECTORY = UNAVAILABLE**。只读盘点R3目录全部42个文件；无最终motion.npz、COORDINATED_TRAJECTORY_FIT.json、潜变量checkpoint、npy/npz/pickle/hdf5/tmp/dmp。已有ENGINEERING_DIAGNOSTICS.json包含R2落点及静态证据，没有首次动态fit.x或最终q。额外限定检查系统临时目录顶层中含minuet/stage-b-r3/hands-checkpoint/crash/dump的文件名，无匹配；未声称扫描整个磁盘或恢复已结束进程内存。

已读GENERATION_FAILURE.json、GENERATION_FAILURE_LOG.txt、IMPLEMENTATION_REPORT.md、CANDIDATE_ATTEMPT.json、GENERATION_LOCK.json、contact_region.py、02_generate_once.py、01_static_and_lock.py、STATIC_REACHABILITY.json，以及R2原fit、motion.npz、工程关节域和FK定义。R3原脚本/策略哈希与生成锁一致。

## 实际触发路径

[02_generate_once.py 第46行](../../../artifacts/a4e8b809621e016c517d.md)：

```python
fit = least_squares(...)  # 第43行；本轮未执行
latent = fit.x.reshape(K, 20)
corr = PchipInterpolator(knots, latent, axis=0)(times) * envelope20
q = np.degrees(A['L_q']).reshape(-1, 20) + corr
assert np.all(q >= co.state_low[6:] - 1e-7) and np.all(q <= co.state_high[6:] + 1e-7)
# motion.npz与fit元数据的保存都在assert之后
```

CONFIRMED：异常发生在优化器调用返回后的输出重采样/插值检查，尚未写motion.npz，尚未运行Blender场景保存或Action烘焙。检查整段827个输出采样×20DOF，包含主动、准备、恢复与闲置阶段，非仅7次触键。不是root或琴键范围检查。

CONFIRMED：最终fit、真实nfev、status/success/message、最优性、latent、插值q、违规mask均未在assert前持久化，这是失败证据保存缺陷。GENERATION_FAILURE_LOG.txt自述为已观察工具输出重建，非完整stdout。最后观察值：残差调用3303、约240.5秒、加权接触RMS0.7916；不可换算成nfev，不证明求解器达到100次上限或收敛。

## 能恢复与不能恢复

|数据|结果与边界|
|---|---|
|R2原始轨迹、支持点、时间、root及键角|可恢复；113个支持点、827个输出采样|
|R3最终一批10个静态姿态修正|可恢复；无需再求解，重构其静态关节值用于域复核|
|静态预检总20次|历史记账可读；原第一批完整数值没有独立保存，不能以最终一批冒充两批现场|
|R3代码、策略、guard位置、异常文本|可恢复、锁哈希核验一致|
|R3最终动态fit.x / latent / q / optimizer termination|不可恢复；UNKNOWN|
|原动态违规手指/关节/DOF/时间/值/量|不可定位；全部UNKNOWN|
|本轮人工数组反例|独立合成机制验证，明确不是R3失败轨迹|

详细清单见EVIDENCE_INVENTORY.json；全域复核见READ_ONLY_BASELINE_AND_DOMAIN_CHECKS.json。本轮未为恢复未知字段重跑R3。

STOP — HUMAN REVIEW。
