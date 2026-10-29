# 关节范围机制与原因分级

结论：**guard触发路径已定位；首次动态超限关节、时间和量尚未定位。** 确认了输出域保障不足、静态/正式变量预算不一致及失败前未保存结果三个工程问题；它们不等于证明上次具体违规样本，更不证明冻结Rig不可行。

## 1. 实际检查对象、单位与范围

20个左手DOF，flat_index = (finger-1)×4 + local_dof，顺序THUMB/INDEX/MIDDLE/RING/LITTLE，每指3个局部屈曲增量+同一基部骨的横展增量。横展不是第4个骨关节，不含轴向扭转。

|手指|屈曲增量1/2/3（度）|基部横展增量（度）|
|---|---|---|
|拇指1：CMC/MCP/IP|0..25 / 0..25 / 0..18|-35..35（CMC）|
|食指2、中指3、无名指4、小指5：MCP/PIP/DIP|0..32 / 0..32 / 0..20|-25..25（MCP）|


范围来自piano_hand_static_posture_clearance_refinement_r2/STATIC_REFINEMENT_POLICY_R2.json的joint_increment_bounds_deg，经R2 left_chord_base.py的B/self.bounds/state_low/state_high进入guard。全部五指本曲目都被使用，因此未替换成LEFT_IDLE_INDEX/RING的整指hard域；闲置策略只是另有软约束。它是已有弯曲RSSF rest上的工程增量域，不是测得的解剖生理角度或被冻结Rig的全部物理极限。

R2保存L_q为弧度，输出guard先np.degrees转换；latent和corr为度，与degree bounds比较，合法后才np.radians保存。FK将degree states转弧度，明确取L的SETUPS。5×4数组与bounds的展开顺序一致。**未发现单位、左右手、轴/关节索引转换错误**；没有修改工程域。

只读验证：R2支持点与827个原采样均PASS；零修正不改R2且PASS；保存角度与PCHIP参考重建最大差3.55e-15度；转换往返最大差0度；时间范围及支持点范围都是0..5.95秒，没有外推采样。窗口包络在[0,1]。

## 2. CONFIRMED：支持点合法不保证输出加法合法

在支持点，latent边界是max(-limit,lo-reference)..min(limit,hi-reference)。若reference本身合法、e∈[0,1]且返回latent满足这些边界，则reference+e×latent是两个合法值的凸组合，支持点总角度合法。

但输出是PCHIP(reference)+e(t)×PCHIP(latent)，**不是**对支持点总角度PCHIP(reference+e×latent)。PCHIP导数取决于各自数据的相邻割线，不能把两个曲线的保形性质自动推广到相加结果或乘包络的结果。当前residual仅约束113个支持点；输出另有706个离任何支持点超过1e-12秒的采样。没有输出层域约束或总角度保形保证。

独立人工反例（非R3现场）：3点t=[0,1,2]，参考角度=[22,24.7,25]°，修正=[3,0.3,-0.3]°，包络恒为1。支持点总角度=[25,25,24.7]°合法；分别PCHIP后相加在人工t=0.61时为25.078033°，超过人工使用的0..25°域约0.078033°。对支持点总角度单独PCHIP则保持域内。**该数值与人工关节身份绝不能用于填写原R3超限关节、时刻或超限量。**

因此结构性的域保障缺口CONFIRMED；原R3是否恰由此导致某个具体违规，仅SUPPORTED。guard拒绝非法输出本身是正确的，不能通过取消assert、扩大容差或裁剪角度修复。

## 3. CONFIRMED：静态通过与正式修正域不是同一条件

静态先用geometry-leverage预算进行独立pose解，保存actual_delta = latent×e；随后使用1.2×max(abs(actual_delta))收紧budget。正式求解把这个收紧后的actual量预算用作**latent**的hard边界，实际修正又乘e。e<1时，正式允许的actual幅度更小。

只读比较已保存静态t=1.4214275秒，e≈0.205488。静态中指MCP横展actual_delta=3.329830°，对应latent=16.204491°；正式latent上限10.523030°，差5.681461°。同一静态姿态还有拇指CMC横展和小指MCP屈曲的latent预算不一致。详见SUPPLEMENTAL_CHECKS.json。

**这些是已保存静态姿态对正式潜变量预算的差额，不是Rig关节绝对值超限，也不是首次动态超限量。** 所有10个保存静态姿态的实际关节值均在原工程域内。差异说明静态通过没有验证正式收紧域、时间耦合和输出插值的整套条件；并不证明正式问题在该时刻没有其他合法解。

## 4. 静态与动态为何不能互相替代

静态仅测试每个起音组on+0.04秒及持键中点，共10个不同姿态；没有覆盖所有NOTE_ON/OFF、准备/释放边界和连续曲线。两批20次独立静态求解也没有施加全段修正速度/加速度约束。正式问题另外有潜变量prior、修正速度/加速度惩罚、收紧预算及包络。局部可达不等于存在满足这些附加条件的整段解。

R2本身存在接近工程边界的自由度：THUMB CMC FLEXION_INCREMENT（66个近边界样本）；MIDDLE MCP FLEXION_INCREMENT（1个近边界样本）；MIDDLE PIP FLEXION_INCREMENT（22个近边界样本）；MIDDLE DIP FLEXION_INCREMENT（28个近边界样本）；RING DIP FLEXION_INCREMENT（6个近边界样本）；LITTLE DIP FLEXION_INCREMENT（1个近边界样本）。它們都是合法原样本，说明支持点间余量可能很小，支持插值叠加风险；它们不是已定位的R3肇事关节。

## 5. 假设分级

|假设|等级|判断|
|---|---|---|
|输出插值/叠加未保持总角度域|结构缺口CONFIRMED；原失败归因SUPPORTED|人工反例与代码证明缺口，原fit丢失所以不能确定实际违规|
|静态/正式预算表示不一致|CONFIRMED|一条保存静态恢复姿态不能满足正式latent预算；不证明全段无解|
|新接触目标与R2姿态存在完整动态冲突|UNKNOWN|独立pose支持静态可达；无完整动态解/约束残差|
|固定root是主因|UNKNOWN|10个固定root静态任务实际触键可达，不能归因于root|
|安全区域几何本身不合理|UNKNOWN作为失败原因|已有静态正余量，无新证据需调整区域|
|单位/左手索引错误|NOT_FOUND|源代码及R2复核一致|
|求解器方法必须更换|UNKNOWN，无支持|没有nfev/status/optimality证据|
|异常前未保存求解结果|CONFIRMED|所有有效结果保存语句在guard之后|

目前最有支持的解释是**约束验证管线不一致，尤其最终曲线域保障不足**，不是Rig不可能或root一定需要重做。实际违规的finger/joint/DOF/time/value/bounds/excess仍UNKNOWN。

STOP — HUMAN REVIEW。
