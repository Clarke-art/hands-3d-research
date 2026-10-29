# MOTION_ARCHITECTURE_CURRENT_STATE

2026-10-09 · ARCHITECTURE_REASSESSMENT_ONLY · HUMAN_VISIBLE_PRODUCT_QUALITY_FIRST

Human批准的四静态姿态及冻结资产继续有效；当前动态演奏NOT_APPROVED。本轮新轨迹、新Action、新blend、求解器执行和渲染均为0。


当前是**离线、整段、低维参数化的联合运动拟合，然后烘焙为Blender预设Action播放**。它已经共同优化掌腕和五指相关参数，不能称为完全独立逐指IK；但也不是带硬接触/非穿透可行性证明的联合受约束轨迹规划。对应证据：[E08 · 当前29参数轨迹](../../../artifacts/d1550f6ef09f15650b96.md)、[E10 · 接触/净空/运动学加权残差](../../../artifacts/650724f7a0c43b7eab23.md)、[E11 · 只有参数bounds的least_squares](../../../artifacts/885caff04d7189845548.md)、[E12 · 120Hz求值/60fps坐标烘焙](../../../artifacts/d0e85664ebf185a28b2e.md)。

## 实际链路与复用边界

|环节|实际实现|证据|
|---|---|---|
|MIDI→手、指、键|原Musette源MIDI384 PPQ、120 BPM；原时间加0.7s统一展示偏移。左D2=5/D3=1，key_index=midi−21。指法是保存的设计候选，不是从MIDI自动估计人体动作。|[E01 · MIDI→手/指/键/共同时钟](../../../artifacts/4d5163a6f92f2b40f05d.md)|
|输入裁剪|common.EVENTS固定n01/n02/n04。区间0.400–1.800s；NOTE_ON/OFF为0.700/0.950、0.950/1.200、1.200/1.450s。原两小节其它音符不进入本微实验。|[E04 · 姿态/阶段/三次曲线采样](../../../artifacts/db8a2595e1cedf5fa5c0.md)、[锁定协调政策](../../../artifacts/1cbb789fcbd3ac719c83.md)|
|静态参考|读取批准R2派生L1/L2 qanchor与共同root。准备/回位120ms等使用quintic；压力路径使用三次Bernstein。完整静态场景保留，不在重叠时强制动态全手同时等于整个L2。|[E04 · 姿态/阶段/三次曲线采样](../../../artifacts/db8a2595e1cedf5fa5c0.md)、[四静态姿态身份](../../../artifacts/c76f98b3e00095c8187e.md)|
|琴键时间轴|原quintic 35ms下沉、70ms回弹，与NOTE_ON/OFF共时钟；演奏规划不能反过来推迟琴键。|[E02 · 原35ms下沉/70ms回弹](../../../artifacts/db029916fa9511d47e4e.md)|
|掌腕与手指|当前一个外部root；3 XYZ幅值+1 world-X pitch幅值；两主动指各4统一系数偏移；拇指8准备混合系数；闲置三指各3屈伸偏移。共29参数，全部在一个residual内优化。|[E08 · 当前29参数轨迹](../../../artifacts/d1550f6ef09f15650b96.md)、[唯一有效求解记录](../../../artifacts/77eefc7d7bd72cc769f2.md)|
|冻结Rig适配|每指3个内部关节旋转：thumb CMC/MCP/IP，其它MCP/PIP/DIP；基部另有spread轴，共20工程角变量。21骨包含其它现有骨段/终端，不表示21×3个自由度都在使用。rest、weights、mesh和corrective保持。|[E03 · 21-bone关节适配](../../../artifacts/131cabf2808b21cdbf1a.md)、[本轮有限只读摘要](../../../artifacts/819e3b4e13e09a1ac34d.md)|
|接触目标|固定pad及实际skin pad均逆变换到**当前旋转琴键**可奏面；目标gap0.5mm，动态XY窗口为原批准触点附近±2/±5mm，随该目标键键程展开。|[E09 · 运动键可奏区接触目标](../../../artifacts/e47a49ced824cb0e3768.md)、[E05 · 运动键面逆变换与实测](../../../artifacts/0db7879eb4ccc47e0205.md)|
|净空|原冻结矩形键体SDF；求解覆盖MIDI21–61，全部3300实际evaluated皮肤顶点。邻键2mm、掌部5mm是软规划距离；主动pad附近18mm区域仅对其本键margin设0，仍惩罚内部穿入。E2/F♯2无豁免。|[E10 · 接触/净空/运动学加权残差](../../../artifacts/650724f7a0c43b7eab23.md)、[锁定协调政策](../../../artifacts/1cbb789fcbd3ac719c83.md)|
|输出/审核|采样120Hz，按frame=1+(t−0.4)×60插入现有骨骼和root四元数关键帧、线性插值；保存后重开验实际几何，再渲染60fps三视角。Action是输出载体，不是最初凭手工编好的全部动作。|[E12 · 120Hz求值/60fps坐标烘焙](../../../artifacts/d0e85664ebf185a28b2e.md)、[E14 · 保存重开绑定身份](../../../artifacts/311c284b114586e3f384.md)|
|音频|既有48kHz音频适配直接消费同一Performance Timeline，NOTE_ON安排声部；旧音频代码明确手部几何接触可失败。最新微动作视频静音，不能据共同时钟宣布手/键/声几何同步通过。|[E16 · 既有音频适配/几何接触未自动验证](../../../artifacts/53653c8cfd20edeeb9f8.md)|

## 现有约束的真实性质

|要求|求解器内|求解后|架构缺口|
|---|---|---|---|
|root/关节参数域|least_squares(bounds)硬限制参数；关节系数域继承已批准附近工程范围。|逐样点实际关节及语义wrist检查。|范围是工程域，人体生理域UNKNOWN。|
|主动接触、可奏区域|fixed=10、skin=6的软误差；区域越界是投影残差。|abs(gap)≤3mm且严格inside，所有required样点均须通过。|3mm及inside不是优化内硬不等式。|
|非穿透、净空|clearance=4的软SDF残差；与接触放入同一总平方和。|E2/F♯2正穿入及88键>3mm有限筛查，另有正常视图审核。|不能证明软距离被同时满足；2/5mm规划margin不能等同最终门槛。|
|速度/加速度|超界软残差；joint850/90000、root450/45000、angular150/15000继承。|独立连续性检查；当前PASS。|连续性合格不强制几何接触合格。|
|自然手型|idle偏移正则、±4°硬域；非均匀曲度、spread固定。|正常三视角/完整动作、Human决定。|没有生理模型或已验证自然度评分。|
|近限位驻留|当前只measure，未进入hard constraint或驻留残差。|DIP近下界两次约0.250s，保留为风险。|与旧0.05s否决政策不同，不能混称同一验收规则。|
|冻结姿态/资产|复用源场景；不重新设计。|完整文件SHA与四静态core身份。|动态重叠不等于源整个L1/L2场景；要分别保护静态身份和动态任务。|

以上由[E10 · 接触/净空/运动学加权残差](../../../artifacts/650724f7a0c43b7eab23.md)、[E11 · 只有参数bounds的least_squares](../../../artifacts/885caff04d7189845548.md)、[E13 · required contact与natural release分开](../../../artifacts/f718733f5d8114e57ccb.md)、[工程连续性/边界驻留](../../../artifacts/7db56105f8fb3a1824f5.md)、[锁定协调政策](../../../artifacts/1cbb789fcbd3ac719c83.md)核实。对人体可行性只能报告工程域及正常画面，没有据此证明生理极限。

## 联合存在，但时间自由度受限

设p2/p3为当前D2/D3键程。实际root为ΔXYZ=a·p2、Δpitch=b·p2；idle q=q_ref+d·p2。三指幅值不同，时间包络相同。p2=0时root无额外偏移，即使D3仍full-down。保存数组核实1.020/1.100s：p2=0、p3=1；0.950s D3起音时p2=1、p3=0。[E08 · 当前29参数轨迹](../../../artifacts/d1550f6ef09f15650b96.md)、[本轮有限只读摘要](../../../artifacts/819e3b4e13e09a1ac34d.md)。

主动指对原三组Bernstein控制点加同一个4维offset，等价Δq=[1−(1−p)^3]·offset。原三组曲线不能独立重新塑形；同一p基本沿用同一压力/回弹路径。拇指另有p2×[(1−p3)b0+p3 b1]的准备混合，故D3在未下沉起音时也受到前一D2 root/混合的影响。存在真实全手数值耦合，但尚无充分的独立准备、交接、D3持键与释放轨迹空间。

## 允许指标退化的机制

J=Σ接触残差²+Σ净空残差²+Σ超限残差²+Σ姿态正则²。各块按不同单位/权重/非零数量累加，没有可行性层或词典序保护；较低总J可以伴随更大的某一主动指gap。大量零净空项不影响J；实际非零项数和尺度才影响折中，不能仅凭3300顶点数断言谁必然占优。[E10 · 接触/净空/运动学加权残差](../../../artifacts/650724f7a0c43b7eab23.md)、[E11 · 只有参数bounds的least_squares](../../../artifacts/885caff04d7189845548.md)。

求解success=True仅表示ftol/xtol收敛；保存动作前只断言参数有限，几何PASS在后验报告判断。后验门禁确实最终FAIL_CLOSED，故问题是生成内核允许折中，**不是系统把失败正式升级为通过**。[E11 · 只有参数bounds的least_squares](../../../artifacts/885caff04d7189845548.md)、[E15 · 后验Fail-closed门禁](../../../artifacts/2de00dfdfa71a964f795.md)。

## 索引

[E01 · MIDI→手/指/键/共同时钟](../../../artifacts/4d5163a6f92f2b40f05d.md)

[E02 · 原35ms下沉/70ms回弹](../../../artifacts/db029916fa9511d47e4e.md)

[E03 · 21-bone关节适配](../../../artifacts/131cabf2808b21cdbf1a.md)

[E04 · 姿态/阶段/三次曲线采样](../../../artifacts/db8a2595e1cedf5fa5c0.md)

[E05 · 运动键面逆变换与实测](../../../artifacts/0db7879eb4ccc47e0205.md)

[E06 · 固定root全段关节系数拟合](../../../artifacts/d86820f46b48523b7abd.md)

[E07 · root补偿与拇指混合](../../../artifacts/0a403603f3100d725180.md)

[E08 · 当前29参数轨迹](../../../artifacts/d1550f6ef09f15650b96.md)

[E09 · 运动键可奏区接触目标](../../../artifacts/e47a49ced824cb0e3768.md)

[E10 · 接触/净空/运动学加权残差](../../../artifacts/650724f7a0c43b7eab23.md)

[E11 · 只有参数bounds的least_squares](../../../artifacts/885caff04d7189845548.md)

[E12 · 120Hz求值/60fps坐标烘焙](../../../artifacts/d0e85664ebf185a28b2e.md)

[E13 · required contact与natural release分开](../../../artifacts/f718733f5d8114e57ccb.md)

[E14 · 保存重开绑定身份](../../../artifacts/311c284b114586e3f384.md)

[E15 · 后验Fail-closed门禁](../../../artifacts/2de00dfdfa71a964f795.md)

[E16 · 既有音频适配/几何接触未自动验证](../../../artifacts/53653c8cfd20edeeb9f8.md)

四阶段正式报告：

- [PIANO_HAND_STATIC_TO_DYNAMIC_TRANSITION_R1_REPORT](../../../artifacts/5a85f4afa0366f203b1b.md)
- [LEFT_LITTLE_FINGER_MOVING_KEY_REACHABILITY_R1_REPORT](../../../artifacts/f28abba48e4aa2c13f29.md)
- [LEFT_OCTAVE_NEIGHBOR_KEY_CLEARANCE_CONFLICT_ISOLATION_R1_REPORT](../../../artifacts/6819611aaf88c2d78a2e.md)
- [LEFT_OCTAVE_ROOT_FINGER_COORDINATED_CLEARANCE_R1_REPORT](../../../artifacts/3f9240de7ec36d387b74.md)
