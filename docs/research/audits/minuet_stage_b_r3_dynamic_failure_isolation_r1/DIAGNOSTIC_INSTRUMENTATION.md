# 最小失败记录机制

本目录新增独立diagnostic_recorder.py；不修改或导入执行R3生成脚本，不包含优化器、FK、动画保存或关节裁剪。当前只运行有限人工数组测试与历史数据只读复核。没有写motion.npz或Blender Action。

## 未来授权运行中的三个记录点

1. **优化器刚返回，先保存再处理**：真实fit.nfev、njev（若可用）、success、status、message、cost、optimality、active_mask、max_nfev及与上限的比较；residual callback计数另列。保存knots、reference states、最终latent、原source hashes、degree bounds、物理/latent预算、包络策略、timegrid和策略哈希。此时不依赖PCHIP或guard成功。
2. **按实际处理阶段分别检查**：raw support q、support corrected q、final interpolated q、若生成后进入Action则saved Action回读q分别记录。每阶段保存采样时间、总q、合法mask、非有限值mask、全部超限的hand/finger/joint/DOF/flat index/value/lower/upper/excess以及有限摘要。样本数和DOF预先有限，禁止逐顶点forensic。原始支持点失败与插值后失败必须分开，不用“joint failure”单字符串混淆。
3. **抛异常之前记录**：诊断JSON写入并fsync返回后才允许guard拒绝。即使插值阶段抛错，也应保留第1步已有的solver checkpoint，并另存exception/type/处理阶段；不能把所有保存安排在最终assert之后。

建议未来调用顺序（示意，**本轮未执行**）：

```python
# 此处fit必须来自未来授权的唯一求解，不能以callback计数代替nfev
write_checkpoint(new_run/'SOLVER_TERMINATION.json', {
    'solver': actual_returned_fit_metadata,
    'knots': knots, 'reference': reference, 'latent': fit.x,
    'source_hashes': hashes, 'bounds_deg': boundaries,
})
# 用统一评价器得到support/final总角度，保留同一原事件时钟
stages = [inspect_stage(stage, times, q_deg, lower, upper)
          for stage, times, q_deg in diagnostic_stages]
ok = record_before_guard(new_run/'OUTPUT_GUARD_CHECKPOINT.json',
                         actual_returned_fit_metadata, stages,
                         raw_reference_and_correction_inputs, hashes,
                         origin='AUTHORIZED_FUTURE_RUN_DIAGNOSTICS')
if not ok:
    raise RuntimeError('Recorded joint-domain guard failure; no refit')
```

所有轨迹数字属于诊断checkpoint；它不是有效motion候选，不自动写Action或重试。使用独立新目录，exclusive-create防止覆盖已有证据。记录器不修改输入数组。NaN/Infinity使用显式JSON标记，并与有限值超限分开；不将缺失值置零制造PASS。

## 已验证的有限人工测试

7项检查：合法数组不变；上下边界/时间/身份映射；非有限值独立报告；合法支持点相加后插值越界反例；checkpoint在拒绝前存在；nfev与callback计数分开；旧checkpoint不允许覆盖。另只读核验非有限值JSON标记可正确读回。相关文件均标记ARTIFICIAL_ARRAYS，不能当成R3原失败现场。

人工反例的“THUMB CMC / t=0.61 / 0.078033°”仅用于记录器身份与机制测试，绝不用于原R3定位结论。测试中的nfev=7/status=1也是人工元数据，本轮没有实际优化器执行。

原R3真实nfev、最终收敛状态和超限样本仍UNKNOWN，不由诊断工具补造。

STOP — HUMAN REVIEW。
