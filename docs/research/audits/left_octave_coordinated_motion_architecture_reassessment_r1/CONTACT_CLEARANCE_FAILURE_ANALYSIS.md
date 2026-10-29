# CONTACT_CLEARANCE_FAILURE_ANALYSIS

2026-10-09 · ARCHITECTURE_REASSESSMENT_ONLY · HUMAN_VISIBLE_PRODUCT_QUALITY_FIRST

Human批准的四静态姿态及冻结资产继续有效；当前动态演奏NOT_APPROVED。本轮新轨迹、新Action、新blend、求解器执行和渲染均为0。


结论：**已确认当前路径的触键/净空折中，以及优化器允许折中；支持时序参数化过窄与局部可达性紧张。尚未确定现有冻结Rig内是否不存在共同可行轨迹。**

## 四阶段有限比较

|阶段|root/手指可变空间|D2 max skin gap|D3 max skin gap|净空|结论|
|---|---|---:|---:|---|---|
|STATIC_TO_DYNAMIC_TRANSITION_R1|固定批准root；主动指全段Bernstein系数；idle固定。|7.689mm|1.000mm|有限筛查PASS|静态起音正确不能保证按下动态键。|
|MOVING_KEY_REACHABILITY_R1|D2驱动root Z/Y/pitch+拇指准备混合；小指、idle原轨迹保持。|2.969mm|1.983mm|E2/F♯2新增已记录穿入|root改变确实补足原轨迹接近键面，空间却同时影响其它皮肤。|
|CONFLICT_ISOLATION_R1|不求解：同关节/键Action，仅动态root→静态root反事实。|2.969→7.689mm|1.983→6.653mm|原两键穿入→0|受控证据确认当前root-contact-clearance tradeoff。|
|ROOT_FINGER_COORDINATED_CLEARANCE_R1|29参数一起拟合；root/idle仍D2-only包络。|3.541mm|4.129mm|两键有限样点正穿入0、全88键>3mm0|可接受接触被牺牲，最终FAIL_CLOSED。|

前三阶段最大值包含要求贴合70ms回弹的统计；末阶段仅[NOTE_ON,NOTE_OFF)必需接触。不能把自然离键计为失败或直接把全部旧/新统计看成相同定义。本轮按已保存phase摘要确认末阶段失败出现在**KEY_PRESS/HOLD与NOTE_ON/KEY_PRESS**，不是释放规则变化造成的假FAIL。[本轮有限只读摘要](../../../artifacts/819e3b4e13e09a1ac34d.md)、[已保存接触分相位数据](../../../artifacts/19e2db1b8c41de2478d7.md)。四报告对应证据见当前状态文档索引。

## CONFIRMED_CAUSE

1. **原路径的共享root具有因果影响。** 隔离阶段关节矩阵差0、键角差0、Action哈希不变；恢复静态root时两键进入清空，而两主动接触恶化。只对该已保存轨迹成立。[已保存root因果对照](../../../artifacts/0b5c8d81979a7626d4c5.md)。
2. **共同平方和没有同时满足关键约束的机制。** contact与SDF都是residual中的软项，solver只有参数box bounds。success=True仍输出D2/D3 FAIL；后验门禁才能拒绝。[E10 · 接触/净空/运动学加权残差](../../../artifacts/650724f7a0c43b7eab23.md)、[E11 · 只有参数bounds的least_squares](../../../artifacts/885caff04d7189845548.md)、[E15 · 后验Fail-closed门禁](../../../artifacts/2de00dfdfa71a964f795.md)。
3. **运动键跟踪存在，当前失败不是按静止键面算出来。** keytransform使用原pivot与当前角度；保存重开独立顶平面/键顶点一致性已验证。[E05 · 运动键面逆变换与实测](../../../artifacts/0db7879eb4ccc47e0205.md)、[E14 · 保存重开绑定身份](../../../artifacts/311c284b114586e3f384.md)、[实际几何校验](../../../artifacts/9f3e8383e518452925df.md)。
4. **最新失败集中于实际演奏阶段。** 两次D2 NOTE_ON skin gap约0.541mm、KEY_PRESS约3.538mm、HOLD约3.541mm；D3 NOTE_ON约4.129mm、KEY_PRESS约4.092mm，但HOLD最大约1.392mm且通过。所有这些阶段skin pad仍inside真实可奏区，因此不是主要XY越界。[已保存接触分相位数据](../../../artifacts/19e2db1b8c41de2478d7.md)、[本轮有限只读摘要](../../../artifacts/819e3b4e13e09a1ac34d.md)。
5. **当前轨迹族没有独立D3 root随动。** p2=0时root/idle偏移强制0；0.950s起音同时处于前一D2 full-down，1.020–1.200s D3持键时root恢复静态。主动三组控制点统一偏移也固定了主要曲线形状。[E08 · 当前29参数轨迹](../../../artifacts/d1550f6ef09f15650b96.md)、[本轮有限只读摘要](../../../artifacts/819e3b4e13e09a1ac34d.md)。

## SUPPORTED_HYPOTHESIS

|假设|支持依据|尚不能证明|
|---|---|---|
|可行性优先级/求解架构是首要瓶颈|软接触+软非穿透可以互相补偿，输出与success分离；已得到净空清空而接触退化的实际结果。|把软项改硬即可找到合格解。|
|时序轨迹空间过窄|D2-only root、idle相同包络、主动控制点统一offset、两次D2共用曲线；D3失败集中在交接。|具体需要几个新增时间控制量，或哪段腕部运动一定能解决。|
|现有边界附近局部可达性紧张|前阶段小指MCP/spread接近工程上限，压力DIP接近0；最终中指三个增量均到−4°偏移边界，root X到−2mm边界。|冻结21骨Rig的全局不足、所有自然路径不可行。|
|目标窗口/准备混合进一步约束交接|D3键程0时XY窗口收缩到原触点，但root在D2包络上；thumb blending同时改变未下沉拇指姿态。|该目标窗口本身错误，或放宽窗口是唯一/正确修复。|
|局部求解/数值可影响结果|一次确定seed与有限参数域；有float32差分与跨场景root单位矩阵的真实实现bug修复记录。|最终修复后失败仍由同一实现bug造成。|

依据[锁定协调政策](../../../artifacts/1cbb789fcbd3ac719c83.md)、[唯一有效求解记录](../../../artifacts/77eefc7d7bd72cc769f2.md)、[实现修复记录](../../../artifacts/67ba3ac31081fcd32288.md)。最新有效输出code/policy SHA与保存记录匹配；两次无效实现启动不纳入产品候选结果。本轮不重跑求解、不重开Blender来重新制造反事实。

## NOT_YET_DETERMINED / UNKNOWN

- 在**保持冻结Rig与相同幅度/角度域**但拥有独立阶段共享轨迹时，共同可行集是否非空。
- 当前bounds、目标窗口、姿态参考、root时间基分别贡献了多少失败；没有新的单因素干预，不能分配独立因果比例。
- 有证据的人体生理关节域、演奏者差异、软组织压力和完整上肢生物力学。现有数值域仅为RSSF-relative工程增量；DIP增量0不是人体反关节或绝对伸直。
- 连续时间、全部三角面非穿透是否严格成立；现有有限筛查与正常教学画面不构成穷尽几何证明。
- 最优规划器在未来双手、和弦、指法切换和多曲目的性能及成功率；本3事件实验不提供泛化证据。

## 瓶颈分级与停止解释

|候选原因|判断|
|---|---|
|约束表达不完整|**部分确认**：移动面与清空目标有实现，但接触/非穿透可行域与失败分类没有进入求解器硬约束；驻留仅测量。|
|约束优先级/求解策略|**CONFIRMED结构缺口**：必须同时满足的要求被做成可交易残差。|
|root与手指完全无协调|**否**：29参数确实联合；问题是协调表达受限。|
|缺乏下沉/持键/释放时序控制|**否（存在）/受限（确认）**：有阶段、运动键目标及自然释放区分，但多数轨迹仍绑定键程单一包络。|
|时间自由度不足|**SUPPORTED_HYPOTHESIS**；当前族的限制确定，换族是否可行仍UNKNOWN。|
|冻结Rig本体自由度不足|**NOT_YET_DETERMINED**；无正式Rig修改依据。|

Human最新判断优先：旧正常视角不明显的邻键小幅几何问题不能夸大；最新净空改善也不能抵消D2/D3真实触键失败。工程可行性和Human-visible自然度分别审核。下一步应改变规划问题的结构，局部root/IK补丁路线保持停止。
