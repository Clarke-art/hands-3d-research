# R2 高层到接触IK实际执行

DESIGN_PROVISIONAL — STOP — HUMAN REVIEW

两个高层候选是不同触键区域/下降边界策略，不是增加节点、迭代或同问题重启。相同源B2/公共参考库产生共享准备初值；数据均明确标为未验证初始化。没有一条获资格的IK连续轨迹。

前方候选实际进入CasADi/IPOPT：96控制变量、5579约束、114929结构Jacobian非零、15个全几何接触配点，运动AD每段5点；C1 Hermite连接引入多邻节点依赖。只有B2固定。原Key Action、控制域、接触、碰撞与速率门禁不变。用于裁剪见证点的4个XY不等式在编译中去除，因见证点已由原patch裁剪保证在域内；pad与完整跨面、实际实体深度和真实验收完全保留，不属于放宽物理合同。

前方求解返回Invalid_Number_Detected，优化迭代0；原日志IPOPT46.543s，其中Jacobian约45.69s，含建模的阶段墙钟58.844s。返回的是IPOPT边界内移后的初值，并未产生有效局部修正。原NLP变量/回调/出错控制输入均在candidate_front_RESULT.json和logs/candidate_front_bridge_execution.log。初始化代码曾漏导入函数，属于迭代前启动错误，记录计费后修复，不算额外候选；没有为失败增加节点或再次执行前方优化。

拒绝在准备区间2.571869374419s的中间配点。具体为MIDDLE/RING非相邻面646/1412的分离支持函数，local row148；约7.682760mm正余量，非实际穿插。alpha近下界，min/max特征切换导致跨步长差异0.248467009和0.361326152，未过1e-3严格差分门禁。保守拒绝正确；该结果说明当前执行器导数前置条件不可靠，不能推导人体或指法不可能。

右侧候选先校验序列化输入；共享准备初值在相同配点复现同一拒绝。第二昂贵优化按早停规则未调用。只读尝试合法单侧差分，原严格阈值不改，最后差异0.019971178仍失败；没有采用未经验证的导数继续。R2_DERIVATIVE_SHARED_BLOCKER.json、R2_DOMAIN_DERIVATIVE_CHECK.json、R2_OFFENDING_DERIVATIVE_FEATURE.json可复核原始步长、分支与轴。

两套未优化预览仅有IPOPT内移的浮点舍入差（约1.208e-13控制单位）；float32 Rig输入一致，统一诊断预览只为了避免重复Blender扫描。右侧没有求解成功或独立连续路径证据。R2_INITIALIZER_IDENTITY_CHECK.json保留推导与舍入量；不把复用样本计为两条成功轨迹。

|数值阶段|墙钟秒|退出码|状态|
|---|---:|---:|---|
|high_level_schedule|2.079000|1|COMPLETED|
|high_level_schedule_compiled|9.359000|0|COMPLETED|
|candidate_front_bridge|1.828000|1|COMPLETED|
|candidate_front_bridge_execution|58.844000|0|COMPLETED|
|intent_and_shared_derivative_audit|10.078000|0|COMPLETED|
|legitimate_domain_derivative_check|7.313000|0|COMPLETED|
|c1_curve_sampling_audit|1.828000|1|COMPLETED|
|c1_curve_sampling_diagnostic|1.765000|1|COMPLETED|
|c1_curve_sampling_final_diagnostic|2.391000|0|COMPLETED|

保守数值阶段计账95.485000s，1次优化器调用、0次有效迭代、2个提案；诊断/启动错误也计入。独立SHA和Blender验收/报告I/O另记，不作为求解优化时间。无第三候选、随机重启、重复旧25ms/2ms求解或扩大训练平台。
