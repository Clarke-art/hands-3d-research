# P3整手布局可行性

**HANDS_P3_WHOLE_HAND_LAYOUT_FEASIBILITY_R1 — INCONCLUSIVE**

本轮没有保留下可验收的P3联合布局。唯一一批数值求解实际进入并执行了least_squares，但随后在接触诊断导出处发生`NameError: surface_metrics`；终态尚未落盘，无法恢复，不能报告其收敛状态、接触成绩或失败原因。遵守一批上限，没有重跑。后续真实Blender检查的是**同一批事前确定的初始布局**，不是求解终态，也不是额外候选搜索。证据不足主要来自这一实现失败，不能据此给P3作全局负面判决。

## 输入与冻结约束

先读取Hands根目录AGENTS.md；新文件全部位于本实验目录。独立piano目录未访问；键数据与真实键体均来自Hands已有88键表及C1内嵌场景。正式MIDI重新解析，R07–R14的音高、channel、velocity、ON/OFF tick与C1事件逐一匹配；展示时钟是源时钟+0.35秒，误差小于1e-10秒。P3来自上一轮CANDIDATES.json，只改变R09/R10。见[EVENT_CONTEXT.json](../../../../examples/historical/experiments/hands_p3_whole_hand_layout_feasibility_r1/EVENT_CONTEXT.json)、[INPUT_BINDINGS.json](../../../../examples/historical/experiments/hands_p3_whole_hand_layout_feasibility_r1/INPUT_BINDINGS.json)。

| 事件 | 音／P3手指 | 原ON–OFF，秒 |
|---|---|---|
| R07 | G4／1 | 2.4928550–2.9214260 |
| R08 | E5／5 | 2.9214260–3.3499970 |
| R09 | C5／1 | 3.3499970–3.5642825 |
| R10 | D5／2 | 3.5642825–3.7785680 |
| R11 | E5／3 | 3.7785680–3.9928535 |
| R12 | F♯5／4 | 3.9928535–4.2071390 |
| R13 | G5／5 | 4.2071390–4.6357100 |
| R14 | G4／1 | 4.6357100–5.0642810 |

原C1掌腕、正式指法与Action未改写。R07/R14仅检查原参考姿态和连接距离，没有为它们求新解。A2与B3批准Blend只读保护；未运行其他曲目或B01/B03。

## 事前限定的唯一整手问题

复用A2/C1的EventCoordinator、FK、稀疏有界SciPy least_squares及冻结native FK/LBS与拇指修正形状。十个事件阶段共同拥有**一个掌腕状态**；各阶段有五指协调角度，共享六个事件的合法触点XY。包含R08下沉、R09前180/75ms准备、R09/R10准确ON交接及各音下沉35ms点。活动、释放跟随、即将触键与闲置指都进入现有任务／键体筛选。接触使用真实权重对应的skin pad，而非仅骨骼marker。没有新Rig自由度、避障框架或运动轨迹。

一个整段不变的掌腕是本批的保守布局假设，**不是P3全部允许解空间**。求解未评估分时掌腕布局族；因此即使该假设失败，也不能证明允许的小幅掌腕协调失败。见[POLICY.json](../../../../examples/historical/experiments/hands_p3_whole_hand_layout_feasibility_r1/POLICY.json)、[POLICY_LOCK.json](../../../../examples/historical/experiments/hands_p3_whole_hand_layout_feasibility_r1/POLICY_LOCK.json)、[BATCH_STARTED.json](../../../../examples/historical/experiments/hands_p3_whole_hand_layout_feasibility_r1/BATCH_STARTED.json)。

采用原A2/C1完整原指法计算得到的掌腕边界，不用P3重新扩大域。相对A2根基准的平移范围为X[-154.586149,33.938388]、Y[-30,35]、Z[-16,12]mm；增量旋转为X/Y±8°、Z±12°。基准位置是(223.679593,-124.339649,42.217247)mm。这是历史工程规划域，不是生理学关节限位或实际无碰撞活动空间。

采用**原协调模型较窄的RSSF相对关节增量域**：拇指三个弯曲增量0–25/25/18°、横展±35°；四长指0–32/32/20°、横展±25°。上一轮外层触达探针的0–40/55/55°、0–75/95/65°等角域没有用于本次求解。保留A2自然手型与同刻C1先验，没有以极限张指替代自然度判断。未引入C01另一轮修改过的30–65mm根高度政策。

接触横向≤0.03mm、垂向绝对间隙≤3mm；新增键体顶点深度>0.5mm且较原同刻允许深度增加>0.02mm记录回退；既有新增关节速度180°/s只用于条件性时间分析。以上门槛没有放宽。

## 实际保存的证据

冻结LBS十个原C1全皮肤姿态重建最大误差小于0.001mm。[FK_LBS_SELF_CHECK.json](../../../../examples/historical/experiments/hands_p3_whole_hand_layout_feasibility_r1/FK_LBS_SELF_CHECK.json)。唯一求解进程21.063秒后因导出错误退出，日志保留。[solve.log](../../../artifacts/5cedcf061896fb9bb4ab.md)、[EXPORT_FAILURE_RECEIPT.json](../../../../examples/historical/experiments/hands_p3_whole_hand_layout_feasibility_r1/EXPORT_FAILURE_RECEIPT.json)。没有NUMERIC_RESULT.json或求解终态STATIC_LAYOUTS.npz；不能虚构这些结果。

按原初始化规则重新导出同一个初始化值：十个同刻C1五指姿态＋这些时刻原C1掌腕的中位数。**没有优化调用、第二个seed或重设参数。** 初始化姿态相对同刻C1角度只差约7.36e-8°的边界浮点夹入量；其主要变化是把原随时刻变化的掌腕替为公共掌腕，因此它不是完成换指协调后的P3手型。

该公共掌腕实际位置(160.468710,-136.623862,28.162162)mm，额外旋转(2.098583,4.822731,0.658821)°。有界参数合法并不使全手接触／碰撞合法。真实Blender 5.1.2逐姿态评估的skin pad与冻结LBS最大差0.0004333mm；真实共享rig world与预测差不超过1.74e-7。见[INITIAL_SEED_LAYOUTS.npz](../../../../examples/historical/experiments/hands_p3_whole_hand_layout_feasibility_r1/INITIAL_SEED_LAYOUTS.npz)、[BLENDER_STATIC_DIAGNOSTICS.json](../../../../examples/historical/experiments/hands_p3_whole_hand_layout_feasibility_r1/BLENDER_STATIC_DIAGNOSTICS.json)。

| 初始布局检查点 | 活动指横向误差mm | 活动指垂向间隙mm | 接触 |
|---|---:|---:|---|
| R08 ON+35ms，小指E5 | 2.429 | −2.721 | FAIL |
| R09前180ms，仍小指E5 | 0 | −1.860 | marker条件PASS；全手FAIL |
| R09前75ms，仍小指E5 | 0 | −1.456 | marker条件PASS；全手FAIL |
| R09 ON，拇指C5 | 44.666 | 8.390 | FAIL |
| R09 ON+35ms，拇指C5 | 44.682 | 19.039 | FAIL |
| R10 ON，食指D5 | 28.281 | 10.296 | FAIL |
| R10 ON+35ms，食指D5 | 28.316 | 16.206 | FAIL |
| R11 ON+35ms，中指E5 | 11.964 | 4.328 | FAIL |
| R12 ON+35ms，无名指F♯5 | 39.781 | −7.910 | FAIL |
| R13 ON+35ms，小指G5 | 27.464 | 0.036 | FAIL |

这些数值是**失败初始化的实际测量**，不是优化后P3最优触达缺口。原C1对应各活动指接触均满足上述marker门槛；R08下沉点原R07释放跟随gap3.089mm的诊断WARN单列，不能称活动R08失败。接触记录明确区分HOLD_OR_PRESS与RELEASE_FOLLOW。

## 整手与真实几何结论

全部五指十对强权重skin ROI使用真实BVH面相交；全3300顶点检查88键各组件深度，并检查非活动指／键表面相交。有限指腹区域顶点也保存，但12mm近pad区域只是诊断范围，没有新增或放宽门禁。共享掌根／指蹼区域的指间相交没有完整认证，不能声称全表面绝对安全。

R08两点保住小指接触时仍有C♯5等侵入和新增同顶点深度回退，所以**没有得到合法R08持键准备空间或其最大范围**。C5、D5及后续三指在保存初始化中失败。R11的中／无名指95对相交同原C1检查点，属于继承的原手型问题；它不是新布局消除B02的证据，也不能记成P3新生成的碰撞。其余关键反例见风险报告与机器见证。

**没有LAYOUT_FEASIBLE_PRELIMINARY，也没有STATIC_ONLY成功解。** 保存结果是INITIALIZATION_ONLY；求解终态UNKNOWN。原C5拇指最高8.70mm条件缺口是否能由允许掌腕协调消除仍未知；本轮既没有证明成功，也没有证明P3或人体不可演奏。

**STOP — HUMAN REVIEW**
