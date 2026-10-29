# 接触导数合同

DESIGN_PROVISIONAL。接口为 `RigState + ContactSet + MovingKeyGeometry + EventTime + JointDomain`。

`surface_derivative.py::surface_chart`：RigState提供冻结蒙皮函数、真实三角拓扑、授权指腹面成员和状态；ContactSet提供key/finger/required_contact；MovingKeyGeometry提供在EventTime从原Action取得的枢轴、逆转动与真实playable surfaces；JointDomain为原界。无音名、事件ID、25ms时间常量。实验驱动文件中的G4/E5标识仅选择原数据。

对每个真实指腹三角面，在移动琴键局部坐标系逐平面裁剪可演奏区域，再取裁剪多边形高度下包络。见证点可能是三角面顶点，也可能是三角面与区域边界的交点；这是完整面计算的结果，不是先挑一个指腹顶点代替面。交点的比例随姿态变化，其导数包括比例变化，不能固定上轮重心坐标冒充全局导数。每次重建检测所有授权指腹面，返回face、clip_signature、tie_count；相同签名内使用链式求导，签名变化或不同梯度并列必须重新建图并标注NON_SMOOTH_OR_UNVERIFIED。

本轮失效点与恢复点的最低面点恰好是501号共享顶点，5个面候选并列，但微扰签名稳定且差分一致；不能由此证明任意活动面切换正确。本轮未遇到真实clip交点活动切换，交点分支仍未覆盖。高度下包络只是可行性方向，不能代替跨面、正面积、pad区域、全88键侵入及自交的最终几何验收。

局部材料面约束保留原真实三角面+重心坐标、原容差及区域界。所有旧CasADi碰撞证书仅是局部冻结图，离开邻域可能过保守或漏掉新对；不作为全局安全保证。动态恢复使用原SLSQP的全三角面侵入LP，并在每个状态更新候选三角；自碰撞优化保留原局部分离轴，最终必须用Blender全非相邻面检查。

Jacobian中真实蒙皮依赖由CasADi自动微分产生；几何矩阵乘节点Jacobian，再乘Bernstein映射矩阵。没有人为消除小值。验证使用多步长差分、原新矩阵逐元素比较及所有144变量的零依赖检查。坐标为mm/deg/无量纲混合，导数单位是输出mm/相应输入单位。

J1/J2/原失败点平滑支通过；J3共同边界自碰撞min/max行437起的一批行存在一侧导数分离，三个差分尺度均约0.3643误差，不能归为随机噪声或优化器性能不足。保留NONSMOOTH_DIAGNOSIS.json的一侧符号、变量和行号。用固定分离轴的min/max时必须检测该分支，不能静默宣称全局光滑。

可复用性能改动：对任意冻结skin Function，先抽取并展开独立的wrist/state-only函数，再构造运动学方向导数，见kinematic_derivative_api.py。保留原skin和完整几何验收。恢复的通用原接口是ContactProblem(state, contacts, angles)与JointDomain；本轮未把特定目标姿态作为PASS条件。

跨MIDI接口检查采用已有R00/D5第五指RELEASE，其required_contact=false，因此不生成接触等式；原碰撞/关节条件不能因此删除。该检查是类型接口验证，不是另一首曲子的运动求解，也不是完整跨MIDI性能证明。
