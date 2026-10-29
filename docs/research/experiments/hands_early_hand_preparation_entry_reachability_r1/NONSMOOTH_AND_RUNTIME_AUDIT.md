# 非光滑与运行审计

DESIGN_PROVISIONAL — STOP — HUMAN REVIEW

严格导数保护实际参与了SLSQP和CasADi/IPOPT回调。每次检查接触面/裁剪特征、琴键实体获胜面、固定自碰撞轴的min/max特征；重算每个扰动下的分支，用1e-4、1e-5、必要时1e-6尺度的中心差分交叉验证，最大差异<1e-3才使用。失败抛异常并拒绝导数，没有静默冻结错误分支。这个数值一致性条件只证明测试点的局部一致性，不证明全局光滑。

原延拓前两个状态在优化器内实际拒绝。分支诊断定位到接触不等式第10行：随着最低接触面的选择改变，该面所属裁剪多边形的max-gap从约1.775772mm跳到0.041037mm。差分误差分别达到954104.026822与242.287450。该跳变主要来自代理表达，而非原接触合同的必然矛盾。

修正仅在本实验副本进行：以所有投影指腹三角面 max(min(-min_gap,max_gap)) 表示真实跨面存在条件，消除“最低面绑定整片max-gap”的伪跳变；允许裁剪见证点在可触区边界（移除内部额外0.001mm见证内缩），保留pad域、跨面阈值以及全部真实Blender接触/侵入验收。原接触合同和历史模块未改。CONTACT_PROXY_REPAIR.json保存改前后哈希与理由。

主候选因继承的HIGH整数数组使固定B2上界被截断，在任何迭代前被IPOPT拒绝。唯一针对性修正将上下界转float再固定精确B2，原时序和约束不变，完整失败记录保留于 ENTRY_MAIN_RESULT.json 与 ENTRY_CORRECTION_RATIONALE.json。

修正求解共记录 12 个迭代回调，约束最大违约从3.171479降至 1.408718505，未取得可行解；返回 Invalid_Number_Detected。实时保护记录 93 次局部差分一致、1 次严格拒绝。最终拒绝位于节点2，跨尺度差异1.088481与0.712314，导致Invalid_Number_Detected；这是导数保护中止，不能误报为目标收敛或纯超时。失败导数的完整试探控制向量未记录，故不宣称该特定试探可独立重放。分支日志保留在 ENTRY_CORRECTION_RESULT.json。

IPOPT日志：总墙钟约203.881s，Jacobian约198.65s，局部几何多尺度差分为主要瓶颈。并未关闭真实碰撞验收。稀疏邻接腕/关节块用已验证CasADi AD；本轮另以真实时间方向中心差分验证不同节点段的运动AD，原始误差见 ENTRY_CANDIDATE_MOTION.json。固定B2对应变量经IPOPT消元，但完整接口仍保留84维与节点结构。

|阶段|保守墙钟秒|结果|
|---|---:|---|
|hold_continuation|11.937000|COMPLETED|
|branch_diagnosis|9.344000|COMPLETED|
|hold_path_diagnostic|30.032000|COMPLETED|
|contact_proxy_repair_and_entry_input|2.782000|COMPLETED|
|main_entry_candidate|4.734000|COMPLETED|
|sole_entry_correction|208.391000|COMPLETED|
|final_candidate_sampling|1.860000|COMPLETED|

记录总数值阶段墙钟 269.080000s <600s；其中数值优化阶段为持键延拓、主候选与唯一修正，其余记录包括分支与采样计算，属于更保守口径。保护SHA、只读输入解析、Blender独立验收和报告I/O不属于求解耗时。未使用剩余预算增加迭代或第三条轨迹。

边界：自碰撞分离轴仍按节点初始近面集合固定，只检查其min/max特征；新轴重生成、未进入代理近面集合的新自碰撞对，以及所有未经触达分支并未获得通用导数验证。接受端仍以全88键及全部真实非相邻指面检查fail closed。本轮 NONSMOOTH_DERIVATIVE_GUARDED 为“部分执行证据”，不是所有分支/轴覆盖PASS。下一路线需要把特征依赖和安全回退作为正式接口，而不是再以局部有限差分成功代替完整保证。
