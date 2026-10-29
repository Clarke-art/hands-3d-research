# 空间缺陷与失败机制分级

PRIMARY_FAILURE_CAUSE = SUPPORTED：核心判断是生成机制的空间表述与任务角色协调不足，而非已证明Rig不可行。以下结构事实可CONFIRMED，哪一项对各帧占主导及修复能否成功仍不能由只读分析证明。

## CONFIRMED：代码或已保存测量直接支持

| ID | 事实 | 证据与意义 |
|---|---|---|
| C01 | A2联合root/五指，但没有直接指—指空间残差 | [02_generate.py:51](../../../artifacts/6eb2250cc3b274e3319e.md)；共同变量不自动排除邻指相交 |
| C02 | 触点与空间形体不同 | [coordinated_motion.py:20](../../../artifacts/15cbc4f5009c9b8e1b00.md)、[04_diagnostics.py:37](../../../artifacts/b819027d56116ee11bb8.md)；pad在正确键面不代表侧面、远端曲面或非活动指不穿入 |
| C03 | 触键/净空/自然先验/平滑均为加权软项 | [02_generate.py:92](../../../artifacts/4bcf4e22f7115c7eb9ef.md)；只有变量域是硬边界，较低总残差不等于每项满足 |
| C04 | 阶段按各指独立分支选择，无跨指通行/交接协议 | [coordinated_motion.py:89](../../../artifacts/b9f43495a87a24fa199f.md)；共享root和时间差分确实耦合变量，但不表达谁应等待谁释放 |
| C05 | 闲置指主要由单一NEUTRAL与时间正则维持 | [coordinated_motion.py:128](../../../artifacts/f01de84f59a7ce47fc92.md)；不存在随邻指、键体与下一任务变化的空闲可行域 |
| C06 | 生成已考虑局部白黑键，但只用pad/关节中心代理 | [02_generate.py:51](../../../artifacts/6eb2250cc3b274e3319e.md)；不能称“完全无键盘空间规划”，也不能称实际skin约束 |
| C07 | R4约束的距离与几何检查不等价 | [coordination.py:69](../../../artifacts/14fd94e4dc200fa9a802.md)、[coordination.py:81](../../../artifacts/d7933e76c0eb99c43c6d.md)；最近顶点argmin、局部法向和8 mm硬启停不是三角面间稳定有符号距离；黑键SDF只测顶点，面跨越仍可能漏检 |
| C08 | R4与有限root不是连续事件规划实验 | [static_preflight.py:10](../../../artifacts/ad4cbdde38b0bce15831.md)、[bounded_static.py:6](../../../artifacts/33a85e73dbfbd2656b9c.md)；分别13个与3个独立静态状态，没有时序决策或连续边界约束 |
| C09 | 有限root带动未参与关节求解的手指 | [ACTUAL_STATIC_COMPARISON.json](../../../artifacts/81a1ef453656b62d31e8.md)；中心小指/F5新增20面对、19内部顶点、约1.2706 mm；原模型未给非目标白键完整皮肤约束 |
| C10 | 阶段定义不一致 | A2释放40 ms、随后F♯5准备；R4旧键floor70 ms；3.825 s不同角色约束并非同口径 |
| C11 | 数值终止不是工程可行 | A2 nfev=75耗尽；R4中心xtol success仍92面对；有限root中心ftol success、optimality约693.7仍83面对。[COORDINATED_TRAJECTORY_FIT.json](../../../artifacts/4173941bf114e3fe7f55.md)、[PREGENERATION_GATE.json](../../../artifacts/37cba642f7bb1d7fbefb.md)、[BOUNDED_STATIC_RESULTS.json](../../../artifacts/de8ab56e38eafe7a1873.md) |

## SUPPORTED：有根据的机制解释，但没有隔离因果实验

1. **空间约束缺口是首要结构原因。** 原始相交继承自A2，C1只复制动作；缺少指—指项且仅检查点状键体代理，解释了接触合格而skin失败。不能分配数值“责任百分比”。
2. **相向准备/恢复路径缺少协调。** 当前提前准备、固定中性先验和有限释放任务可能把手指引向另一指所在通道。早段闲置无名指与准备中指、晚段中指E5与无名指转F♯5尤其相关。阶段切换造成目标方向变化是已知，是否是某帧穿入的充分原因未知。
3. **软约束交易与局部引导不足维持坏姿态。** R4中心中指DIP约0.0033°、无名指PIP约0.0102°接近下限，仍有其他自由度余量；不能以“碰到一些边界”推断整体不可行。最近顶点切换/8 mm启停可使有限差分与局部优化不稳定；这是求解机制风险，不是已定位的唯一数值故障。
4. **只改局部角度或root无法修补缺失的任务表达。** 增加变量不增加释放路径、非目标白键或闲置指保护；有限root虽然保持E5，却把问题转给小指，是已观察的例子。
5. **支持点可行与插值可行存在缺口。** PCHIP保状态分量边界不保FK皮肤避碰；LINEAR四元数烘焙也不是解析PCHIP。它们是必须验证的风险，现有证据没有证明烘焙是主要根因。

## UNKNOWN：不能由本轮推断

- 固定root在合理全手事件协调下是否存在自然可行轨迹。
- 有限root配合新的空间与阶段模型是否能成功；±范围扩大是否有效。
- 指法保持不变时所有窗口是否均可行，窗口是否最终必须合并为全段。
- 精确分离/角色规划对每个缺陷的贡献；替换某一种优化器能否单独解决。
- 任意曲目、手型、速度、多声部/和弦下的覆盖率、计算时间与自然度。
- 需要修改冻结Rig、权重、Corrective的证据不存在，不能从局部失败推出物理不可行。

## 已失败路线为何不能继续原样试错

R2采用无名指MCP单自由度、0.80–2.08 s支撑、−6°平台；有限静态检查有改善，但动态残余仍在，且无名指/C♯5干涉部分提前约0.117 s。它不处理另一指曲度、晚段、黑键约束或跨事件角色。其PARTIAL及原严格几何FAIL均保留，不追溯改判：[05_lock_local_policy.py:7](../../../artifacts/e2c5bb72e69b41b62d0b.md)、[09_commit_same_locked_motion.py:20](../../../artifacts/7c33767772a65aae1ed0.md)。

R3是实际四指远端皮肤/七黑键诊断，不是新规划器。历史2.17–5.60 mm见证来自不同时间与指键组合，不能套到3.825 s或全部时刻：[diagnose.py:31](../../../artifacts/cf99d530e98112e79b04.md)、[R1_BLACK_SUMMARY.json](../../../artifacts/6f37f72aca30f05c7907.md)。

R4已加入真实加权蒙皮与三指12DOF，但只是有限静态联合残差。中心93→92面对，主动E5约0.752 mm gap，黑键已无命中，说明“改善黑键”与“解决邻指”不是同一条件。保留一次作废的静止键面开发检查及一次有效静态批次；本轮只读有效结果，不隐去该历史：[PREGENERATION_GATE.json](../../../artifacts/37cba642f7bb1d7fbefb.md)。

有限root沿用R4模型，中心92→83面对，内部采样见证最大距离6.695→6.651 mm，E5约0.8605 mm gap；D♯5无内部顶点但11面对仍在，相对固定root并无优势。前后邻居相交消失，但3.750 s无名指/非目标E5深度3.0873→4.3084 mm，3.850 s中指/D5约1.3014→1.4193 mm；不能只择取有利指标。[ACTUAL_STATIC_COMPARISON.json](../../../artifacts/81a1ef453656b62d31e8.md)。

本轮不再增加root上限、尝试角度/权重、重优化静态点，也不把当前状态标为FIXED_ROOT_INFEASIBLE。
