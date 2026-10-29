# HANDS_SPARSE_WINDOW_CONSTRAINED_TRAJECTORY_FEASIBILITY_R1

**RESULT = NO_FEASIBLE_CANDIDATE_WITHIN_SCOPE**  
**SPARSE_WINDOW_HYPOTHESIS = UNKNOWN**  
**HUMAN_NATURALNESS = NOT_TESTED**

本轮停止在Stage0，未启动正式优化或生成修正动态候选。原因是实际发现原C1固定边界与本轮整手非目标键0.5mm门禁冲突，且完整Jacobian成本不适合盲目启动180s求解。它不是“求解器不收敛”“优化超时”或Rig全局不可达，也不是一次修正候选的几何FAIL。

原C1已在真实Blender中只读复核完整固定窗口 **1.2414275–2.134284s**，保存241个原始时刻、双手skin及原键时钟；没有改原动作。真实skin重建最大误差 **0.002002mm**，实际键体登记对应最大误差 **0.00002218mm**，Rig/corrective和全部Action摘要前后相同。这是原C1输入验证，**不能冒称新轨迹验证**。

| 项目 | 原C1真实参考 | 新修正候选 |
|---|---|---|
| R04 C5接触 | 58/58 PASS；横向0，绝对gap最大1.523343mm | 未生成，UNKNOWN |
| R05 D5接触 | 110/110 PASS；横向0，绝对gap最大1.512087mm | 未生成，UNKNOWN |
| R03 B4 / R06 G4上下文接触 | 50/50、23/23 PASS | 未生成，UNKNOWN |
| 固定入口中指/C5侵入 | 顶点1292：2.031165mm | 端点修正恒为零，不能满足≤0.5mm |
| 固定出口食指/A♯4侵入 | 顶点250：1.485202mm | 端点修正恒为零，不能满足≤0.5mm |
| 整手新增回退、连续小指E5收益 | 旧缺陷保留；本轮未重复全历史审计 | 未生成，UNKNOWN |
| 面内侵入、BVH、左右手候选关系 | 未对不存在的候选计算或伪造零值 | NOT_EXECUTED |
| 修正后的速度、自然度 | 原参考适配器已有分段导数读回，但连续腕/skin界仍UNKNOWN | NOT_TESTED |

接触来自 `ORIGINAL_C1_CONTACT_REFERENCE.json`，是真实skin pad与实际键面，未使用骨骼marker代替。241原始节点中的两个二进制等价读取节点被保留；连续适配器仅合并数值等价节点为239，原MIDI事件/角色时间不变。没有0.7145ms独立修正状态或逐点IK拼接。

**核心见证与适用范围**

`BOUNDARY_CONTRACT_WITNESS.json`、`BOUNDARY_ACTUAL_WITNESS.npz`给出两端真实坐标、键组件身份、顶点及全部半空间内距。边界检查覆盖全部88键/139组件，不依赖规划邻域筛选。固定边界的52个自由基函数值及导数都为零，任意内窗系数都不能消除上述端点旧侵入。因此本次“原入口/出口不变＋整手非目标顶点≤0.5mm”没有合格候选。

这里没有追溯新增零BVH或面内0.5mm门禁，也没有把历史缺陷算成新增失败。若原意为“活动小指≤0.5mm，其他区域仅不恶化”，上述整手绝对门禁冲突应由Human独立审核；本轮遵循最新整手门禁原文，未自行改为更弱版本。即使改成相对不恶化，也不能自动宣称整手已清障。

**A–H回答**

| 问题 | 本轮实际结论 |
|---|---|
| A 真正短窗口联合约束，而非逐点IK？ | **联合模型与约束/Jacobian已建立并评价。** 原26状态流共享6槽/通道，边界消元后52变量；没有独立IK调用。尚未正式求解，不能声称取得联合可行轨迹。 |
| B 原MIDI时间内保持全部活动触键？ | **新候选UNKNOWN。** 原C1的R04/R05及上下文真实参考通过；不得把基线PASS转记为候选PASS。 |
| C 避免R2极端速度/异常腕运动？ | **新候选UNKNOWN。** 修正基的独立节点间隔约297.619ms，导数与边界自测通过；无独立短段。原连续Action导数/腕安全界未完全闭合，不虚构新候选峰值。 |
| D 小指邻键侵入连续降低？ | **未取得证据。** 没有新轨迹、没有重算或拼接三个静态终态。 |
| E 新增整手穿模或接触回退？ | **无法评估新候选。** 发现的是原C1两端已有非目标侵入；原记录保留，未产生姿态修改。 |
| F ≤164变量、≤180s得到有效动态结果？ | **NO。** 模型自由变量52；有效Jacobian成本45.078s；正式求解0次、候选0条，在Stage0合同冲突后停止。不是耗尽预算的OptimizeResult失败。 |
| G C1自然特征保留及Human审核？ | C1被保留为固定先验；原资产/动作没有修改。不存在修正成果供Human自然度验收，**NOT_TESTED**。分段数学导数不等于自然动作证明。 |
| H 下一独立窗口还是转C？ | **本轮不支持直接进入下一窗口，也不支持据此宣布A失败并自动转C。** 先独立审核边界与绝对/相对几何合同，及原Action导数和Jacobian成本。若仍要求坏端点冻结且整手绝对≤0.5mm，路线C同样继承此逻辑冲突，换工具无法解决。 |

`COST_PREFLIGHT_CLOCK_FIXED.json`实测单次约束0.860s、完整52列Jacobian45.078s、11149个约束；完整NLP所需迭代/成功率仍未知。没有为了获得输出放松门禁、加控制点、改seed或扩大窗口。

参考时钟解析曾产生虚假导数尖峰，错误包络与首轮成本文件保留并明确作废；有效文件带 `_CLOCK_FIXED`。修正后的关节参考适配器峰速约198.501°/s，腕枢轴约268.84mm/s/120.00°/s。加速度峰值约188779.577°/s²是适配器数学值，尚不能作为原Action或自然度合格阈值。连续区间安全为UNKNOWN，未以240Hz参考采样宣布连续安全。

本轮最终范围：完成真实C1输入回读、稀疏联合表示/约束自测、成本评价与固定边界反证；**没有取得修正动态可行性证据**。23项实际引用历史输入SHA一致，原Rig/蒙皮/corrective、琴键Action、MIDI、指法及左手保持只读；独立piano完全排除。没有新Action、Blend、视频、外部框架安装或后续实验。

执行细节见 `SPARSE_WINDOW_EXECUTION.md`；机器结果见 `FINAL_RESULT.json`、`EXECUTION_POLICY_AND_STOP.json`、`PROTECTION_FINAL.json`。

```text
HANDS_SPARSE_WINDOW_CONSTRAINED_TRAJECTORY_FEASIBILITY_R1
RESULT = NO_FEASIBLE_CANDIDATE_WITHIN_SCOPE
SPARSE_WINDOW_HYPOTHESIS = UNKNOWN
HUMAN_NATURALNESS = NOT_TESTED
STOP — HUMAN REVIEW
```
