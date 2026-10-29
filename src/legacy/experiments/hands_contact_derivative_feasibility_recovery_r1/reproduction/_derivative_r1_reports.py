import json,statistics,hashlib,time,shutil
from pathlib import Path
O=Path(r'<HANDS_ROOT>_contact_derivative_feasibility_recovery_r1');P=O.parent/'hands_contact_constrained_trajectory_planning_r1'
def read(n):return json.loads((O/n).read_text())
def write(n,x):(O/n).write_text(json.dumps(x,ensure_ascii=False,indent=2) if not isinstance(x,str) else x,encoding='utf-8')
def median(x):return statistics.median(x)
perf=read('JACOBIAN_PERFORMANCE_COMPARISON.json');multi=read('MULTINODE_PERFORMANCE.json');pruned=read('MULTINODE_PRUNED_PERFORMANCE.json');direct=read('DIRECT_JACOBIAN_VERIFICATION.json');recovery=read('CONTACT_FEASIBILITY_RECOVERY.json');adj=read('ADJACENT_RECOVERY.json');res=read('RESOURCE_PROFILE.json');face=read('FACE_SURFACE_VALIDATION.json');budget=read('TOTAL_NUMERICAL_BUDGET.json');speed=median(multi['old_jac_seconds'])/median(pruned['old_jac_seconds'])
budget['phases']['resource_profile_seconds']=read('RESOURCE_BUDGET.json')['charged_seconds'];budget['total_charged_seconds']=sum(budget['phases'].values());budget['under_budget']=budget['total_charged_seconds']<=600;write('TOTAL_NUMERICAL_BUDGET.json',budget)
write('JACOBIAN_PERFORMANCE_RAW_LOCAL.json',perf)
write('JACOBIAN_PERFORMANCE_COMPARISON.json',dict(authority='DESIGN_PROVISIONAL',local_cases=perf,J4_original=multi,J4_pruned=pruned,confirmed_J4_speedup=speed,comparison='Original three-node expression vs same expression with wrist/state-only dependency pruning; direct matrix and function values match exactly',rejected_optimization='Full-skin node chain rule alone slows J1/J2/J3; do not promote it',call_accounting=dict(local_old='One composed AD evaluation per sample; includes symbolic differentiated skin. No finite difference or runtime Blender.',local_new='One primal full-skin, one skin-Jacobian and one sparse geometry-Jacobian per fresh sample; extra copy overhead.',J4='3 geometric skin paths and 3 kinematic paths per value evaluation. Old kin carries full skin through nested directional differentiation; new kin includes wrist and state only. AD internal elemental operations are not counted as independent Python FK calls.',contact_detection='Frozen chart benchmarks: zero active face or LP detector calls per Jacobian; separate redetect checks explicitly counted in raw rows.'),memory=res['memory'],J4_memory=res['old_J4_external_observation'],memory_limitations='J4 paired peak RSS unavailable; observed old process RSS and serialized new function bytes recorded. No fabricated zero-memory result.',solver_interface=read('SOLVER_INTERFACE_SMOKE.json')))
validation=read('DERIVATIVE_VALIDATION.json');validation.update(fixed_material_chart_verified=False,fixed_material_chart_per_case={r['id']:r['checks'][-1]['max_abs_error']<1e-3 for r in perf},original_vs_pruned=direct,face_surface=face,non_smooth=read('NONSMOOTH_DIAGNOSIS.json'),status='DERIVATIVE_METHOD_PARTIAL',smooth_branch_derivative_verified=True,sparse_pullback_verified=True,global_all_active_switches_verified=False)
direct['memory_start']=dict(status='INVALID_64_BIT_HANDLE_MEASUREMENT_SUPERSEDED',replacement='RESOURCE_PROFILE.json');direct['memory_end']=direct['memory_start'];write('DIRECT_JACOBIAN_VERIFICATION.json',direct);validation['original_vs_pruned']=direct;write('DERIVATIVE_VALIDATION.json',validation)
recovery.update(adjacent_recovery='ADJACENT_RECOVERY.json',status='CONTACT_RECOVERED_BUT_MOTION_INCOMPATIBLE',static_recovery_pass=True,continuous_motion_pass=False,failure_classification=dict(fixed_certificate_stage='SLSQP iteration limit; frozen local certificate model unsuitable for this excursion; not a proof of physical conflict',dynamic_stage='Original dynamic triangle constraints converge and actual geometry passes',adjacency='Independent recovered states violate original speed conditions; no continuous compatibility demonstrated'),initial_true_gap_mm=read('RECOVERY_INPUT.json')['actual']['contact_results'][0]['geometry']['contact']['true_pulp_surface_contact_distance_mm'])
write('CONTACT_FEASIBILITY_RECOVERY.json',recovery)
gates=dict(CONTACT_DERIVATIVE_VERIFIED='PASS_SCOPED_TO_TESTED_SMOOTH_FACE_BRANCHES',SPARSE_JACOBIAN_VERIFIED='PASS_SCOPED_TO_TESTED_DEPENDENCIES',JACOBIAN_SPEEDUP_CONFIRMED=True,CONTACT_FEASIBILITY_RECOVERED=True,CONTACT_RECOVERED_BUT_MOTION_INCOMPATIBLE=True,LOCAL_25MS_SAMPLED_PASS_HUMAN_PENDING=False,DERIVATIVE_METHOD_PARTIAL=True,FEASIBILITY_RECOVERY_BLOCKED=False,METHOD_BLOCKED=False,FAIL_CLOSED=True)
write('LOCAL_25MS_REGRESSION.json',dict(status='NOT_EXECUTED',interval=[2.913092667,2.938092667],candidate_count=0,reason='Global nonsmooth active-set derivative gate incomplete; independently recovered neighboring states fail original motion limits. No new trajectory optimization authorized by these partial results.',same_24_sample_new_comparison=None,previous_24_sample_failures=12,previous_final_gap_mm=2.615577760,previous_results_source=str(P/'FINAL_RECOMMENDATION.md'),no_new_continuous_motion_claim=True))
write('FINAL_GATES.json',dict(authority='DESIGN_PROVISIONAL',route='A',gates=gates,stop='STOP — HUMAN REVIEW'))
nlp=json.loads((P/'NLP_DESIGN.json').read_text());counts={}
for n in nlp['names']:
 k=n['name'].split('_')[0];counts[k]=counts.get(k,0)+n['count']
write('MODEL_ROW_COUNTS.json',counts)
fk=median([r['FK_seconds'] for r in res['skin_instrumentation']]);sk=median([r['weighted_skin_seconds'] for r in res['skin_instrumentation']]);ct=median(res['face_contact_detection_seconds']);col=median(read('WORKLOAD_PROFILE.json')['SLSQP_full_contact_collision_seconds'])
write('CASADI_JACOBIAN_ROOT_CAUSE.md',f'''# CasADi Jacobian 根因审计

DESIGN_PROVISIONAL。证据来源：上一轮 `solve_trajectory.py`、`symbolic_skin.py`、`NLP_DESIGN.json`、`logs/casadi_local.log` 与实际 Blender 数据；本轮未运行旧31次迭代。

## 原模型与单位

144个决策变量：两个五次 Bernstein 段，每段12维×6控制系数；13个原始时间节点。6618约束行，48个严格等式（初始位置12、段间C0/C1/C2各12），6570不等式，另有144个双侧变量界。14个材料接触行在实现中是双侧容差不等式 ±0.0005 mm，不能误报为IPOPT等式。关节域由12维变量界及参考族映射限定，mapped joint rate为每节点20行。139个琴键三角证书各3顶点、39个自碰撞证书每节点，碰撞合计5928行。完整行分类见 `MODEL_ROW_COUNTS.json`。

根平移mm、根/拇指角度deg、两个参考族混合系数无量纲；蒙皮输出m，接触乘1000转mm。时间s，速度/加速度按原上限归一化；连续性残差乘0.01^order。未发现度/弧度误用。接触0.0005mm容差与位移/混合参数的数值尺度差异明显，IPOPT初始约2.8mm违规非舍入噪声；这不是人体可行性判据。

目标依赖相邻控制系数的一阶至三阶差分及姿态偏好。接触、琴键碰撞、自碰撞仅依赖本节点z；腕速/腕加速度依赖本节点(z,zd,za)。Bernstein节点依赖本段6个控制系数（端点出现自然零）；两段仅通过C0/C1/C2相连。不是将不相邻时间人为置零。

## 169.82秒的证据边界

原日志：34次 `nlp_jac_g` 共169.82s，均值约4.995s；62次 `nlp_g` 共7.29s；目标0.000718s、目标梯度0.000279s；总IPOPT182.10s，剩余约4.99s为其他求解器工作。自动微分贯穿模型，`jtimes`构造腕运动学；有限差分属于旧SLSQP，不能混为IPOPT根因。碰撞LP只用于固定证书建立，Blender不在这个Jacobian回调中。

历史日志未分别计时169.82s内部的FK、skin、kin，不能编造精确历史内部秒数。本轮保留同表达式、同输入、原问题三个相邻节点做反事实拆分：

|计算|3次中位数|
|---|---:|
|原三节点Jacobian（144×1728的转置方向：矩阵1728×144）|{median(multi['old_jac_seconds']):.6f}s|
|只做节点链式拆分，保留原腕运动学|{median(multi['new_jac_seconds']):.6f}s|
|剪除腕运动学无关skin输出|{median(pruned['old_jac_seconds']):.6f}s|

**主要瓶颈为腕/关节运动学函数携带完整蒙皮输出进入嵌套方向求导。** `f(zz)`输出V、wr、st，kin只用wr/st；但原SX函数边界把全skin计算带入方向导数。用SX输入先构造只输出wr/st的函数，使依赖剪枝发生在嵌套求导之前。完整约束值与Jacobian逐元素差为0，实测{speed:.3f}倍；该小实例约{100*(1-1/speed):.2f}%开销被去除。不能把这个比例冒充169.82s的逐项历史测量，也未声称完整13节点已加速同倍数。

独立负载探针中位数：数值FK {fk*1000:.3f}ms、加权蒙皮 {sk*1000:.3f}ms（原Skin函数AST副本插桩，输出完全一致），两个活动指腹面检测 {ct*1000:.3f}ms，原SLSQP整套接触/动态碰撞评估 {col*1000:.3f}ms。最后一项包含FK/skin，不能与前项直接相加。细节及单次原始数值见 `RESOURCE_PROFILE.json`、`WORKLOAD_PROFILE.json`。J1/J2/J3节点链式拆分反而变慢，其负结果全部保留。

J4旧进程曾观察到8,945,868,800字节RSS；不是峰值。成对峰值内存没有可靠记录，不作内存改善声明。J1—J3有实际Windows RSS。原内存API因64位伪句柄读到0的结果已作废并替换为有效测量。
''')
write('CONTACT_DERIVATIVE_CONTRACT.md','''# 接触导数合同

DESIGN_PROVISIONAL。接口为 `RigState + ContactSet + MovingKeyGeometry + EventTime + JointDomain`。

`surface_derivative.py::surface_chart`：RigState提供冻结蒙皮函数、真实三角拓扑、授权指腹面成员和状态；ContactSet提供key/finger/required_contact；MovingKeyGeometry提供在EventTime从原Action取得的枢轴、逆转动与真实playable surfaces；JointDomain为原界。无音名、事件ID、25ms时间常量。实验驱动文件中的G4/E5标识仅选择原数据。

对每个真实指腹三角面，在移动琴键局部坐标系逐平面裁剪可演奏区域，再取裁剪多边形高度下包络。见证点可能是三角面顶点，也可能是三角面与区域边界的交点；这是完整面计算的结果，不是先挑一个指腹顶点代替面。交点的比例随姿态变化，其导数包括比例变化，不能固定上轮重心坐标冒充全局导数。每次重建检测所有授权指腹面，返回face、clip_signature、tie_count；相同签名内使用链式求导，签名变化或不同梯度并列必须重新建图并标注NON_SMOOTH_OR_UNVERIFIED。

本轮失效点与恢复点的最低面点恰好是501号共享顶点，5个面候选并列，但微扰签名稳定且差分一致；不能由此证明任意活动面切换正确。本轮未遇到真实clip交点活动切换，交点分支仍未覆盖。高度下包络只是可行性方向，不能代替跨面、正面积、pad区域、全88键侵入及自交的最终几何验收。

局部材料面约束保留原真实三角面+重心坐标、原容差及区域界。所有旧CasADi碰撞证书仅是局部冻结图，离开邻域可能过保守或漏掉新对；不作为全局安全保证。动态恢复使用原SLSQP的全三角面侵入LP，并在每个状态更新候选三角；自碰撞优化保留原局部分离轴，最终必须用Blender全非相邻面检查。

Jacobian中真实蒙皮依赖由CasADi自动微分产生；几何矩阵乘节点Jacobian，再乘Bernstein映射矩阵。没有人为消除小值。验证使用多步长差分、原新矩阵逐元素比较及所有144变量的零依赖检查。坐标为mm/deg/无量纲混合，导数单位是输出mm/相应输入单位。

J1/J2/原失败点平滑支通过；J3共同边界自碰撞min/max行437起的一批行存在一侧导数分离，三个差分尺度均约0.3643误差，不能归为随机噪声或优化器性能不足。保留NONSMOOTH_DIAGNOSIS.json的一侧符号、变量和行号。用固定分离轴的min/max时必须检测该分支，不能静默宣称全局光滑。

可复用性能改动：对任意冻结skin Function，先抽取并展开独立的wrist/state-only函数，再构造运动学方向导数，见kinematic_derivative_api.py。保留原skin和完整几何验收。恢复的通用原接口是ContactProblem(state, contacts, angles)与JointDomain；本轮未把特定目标姿态作为PASS条件。

跨MIDI接口检查采用已有R00/D5第五指RELEASE，其required_contact=false，因此不生成接触等式；原碰撞/关节条件不能因此删除。该检查是类型接口验证，不是另一首曲子的运动求解，也不是完整跨MIDI性能证明。
''')
write('PRODUCT_ROUTE_REVIEW.md',f'''# 产品路线退出评估

选择 **A：导数及可行性恢复取得可靠进展**，保留经过验证的依赖剪枝与恢复入口；不增加本轮优化时长、不进入新轨迹求解。DESIGN_PROVISIONAL。

这次改善的是通用计算依赖：wr/st不应携带无关skin输出进入高阶导数；不是给G4→E5调接触权重。三节点{speed:.2f}倍加速有原新函数值、矩阵零差和差分校验支持。单节点链式拆分没有优势，不推荐照搬。

原失效控制状态在原事件时间、原Action与关节域下，通过原SLSQP动态三角面约束恢复；3个点均经真实Blender几何/解剖门禁通过。但独立恢复点之间速度约4639与5284mm/s，超过原500mm/s。**静态接触集存在，不代表这些状态可以在既定相邻时刻互相到达。** 固定证书恢复失败而动态检测恢复成功，说明局部证书的适用邻域和活动集合更新值得保留为结构性问题。

退出条件核对：导数并非完全不可验证；实际成本改善不是很小；真实静态恢复并非无可信结果，因此本轮不触发C。也不选B，因为恢复已通过真实门禁。A仅保留可靠底层能力；共同边界非光滑、活动面切换覆盖与跨时刻状态兼容尚未解决，不能认定产品级规划方法已经成立。

下一阶段由Human决定是否立项：先比较更早的手位准备、接触状态与运动的联合表示、指法的运动可行性反馈、动作先验的代价；本轮不更换架构、指法或MIDI。任何短时路径试验前应先选择满足原速度条件的相邻可行状态及稳定活动集策略。禁止直接把现有独立恢复点插值作为结果。

产品成本限制：原J4图观察RSS约8.95GB，未获得成对峰值内存优势证据；跨MIDI只验证另一既有RELEASE类型，广泛复用仍需后续门禁。固定MIDI时长可行性仍未确定；预算内失败不等于人体不可演奏。

STOP — HUMAN REVIEW。
''')
ac=recovery['dynamic_detector_stage']['actual'];write('FINAL_RECOMMENDATION.md',f'''# 最终判断

**A：导数及可行性恢复取得可靠进展。** 保留改进接口；不进入连续运动生产。全部结果 `DESIGN_PROVISIONAL`。

- 原三节点Jacobian约{median(multi['old_jac_seconds']):.6f}s → {median(pruned['old_jac_seconds']):.6f}s，**{speed:.2f}倍**；剪枝前后约束值及Jacobian逐元素差0。多步长检查细步长最大误差4.31e-9，无遗漏可检测非零依赖。
- J1/J2/原失败点固定图导数通过；真实裁剪指腹面在失效/恢复点通过。J3自碰撞分离轴min/max有非光滑支，故 `DERIVATIVE_METHOD_PARTIAL` 保留，不能宣称所有切换均验证。
- 原最终失败点真实指腹间隙2.615578mm，经动态检测恢复5次SLSQP迭代，约6.531s；Blender接触/侵入/自交/解剖门禁全通过。目标侵入{ac['target_max_depth_mm']:.9f}mm、错误区域侵入0、非相邻指面交叉0。
- 相邻两个原失败点亦通过全部静态门禁；恢复点间腕速约4639.371与5283.768mm/s，超过原500mm/s，判定 **CONTACT_RECOVERED_BUT_MOTION_INCOMPATIBLE**。
- 25ms回归 `NOT_EXECUTED`，新轨迹候选0，无新24样本连续轨迹PASS。固定MIDI时间可行性仍未知。
- 数值过程保守计费 **{budget['total_charged_seconds']:.3f}/600s**，包含导数建图/探针、重复诊断、失败启动、恢复与独立Blender回放。细分见TOTAL_NUMERICAL_BUDGET.json。

|验收标记|结果|
|---|---|
|CONTACT_DERIVATIVE_VERIFIED|限定于已测平滑面分支PASS|
|SPARSE_JACOBIAN_VERIFIED|限定于已测真实依赖PASS|
|JACOBIAN_SPEEDUP_CONFIRMED|PASS（三节点）|
|CONTACT_FEASIBILITY_RECOVERED|PASS（3个独立静态点）|
|CONTACT_RECOVERED_BUT_MOTION_INCOMPATIBLE|成立|
|LOCAL_25MS_SAMPLED_PASS_HUMAN_PENDING|未通过 / NOT_EXECUTED|
|DERIVATIVE_METHOD_PARTIAL|成立|
|FEASIBILITY_RECOVERY_BLOCKED|最终不成立；固定证书阶段失败保留|
|METHOD_BLOCKED|底层接口不阻塞；连续运动未证明|
|FAIL_CLOSED|对连续路径/生产门禁保持关闭|

源码、原始单次计时、多步长差分、阶段失败和Blender日志均保留。保护独立复核结果见PROTECTION_CHECK.json；不修改冻结Rig、批准姿态、Stage A/B/C、原MIDI或琴键Action，无新Action、视频或Blend。

**STOP — HUMAN REVIEW。** 未经Human授权，不进入长窗口、B02、23音双手动画或正式教材生产。
''')
write('kinematic_derivative_api.py','''"""Generic frozen-rig derivative dependency pruning; geometry output stays intact."""
import casadi as ca

def wrist_state_function(frozen_skin):
    q = ca.SX.sym("rig_state", frozen_skin.size1_in(0), frozen_skin.size2_in(0))
    _, wrist, engineering_state = frozen_skin(q)
    return ca.Function("wrist_state_only", [q], [wrist, engineering_state])

def motion_derivatives(frozen_skin):
    f = wrist_state_function(frozen_skin)
    n = frozen_skin.numel_in(0)
    q, qd, qdd = [ca.MX.sym(s, n) for s in ("state", "velocity", "acceleration")]
    wrist, engineering_state = f(q)
    velocity = ca.jtimes(wrist, q, qd) * 1000
    acceleration = ca.jtimes(velocity, q, qd) + ca.jtimes(velocity, qd, qdd)
    rates = ca.jtimes(engineering_state[6:], q, qd)
    return ca.Function("motion_derivatives", [q, qd, qdd], [velocity, acceleration, rates])
''')
policy=read('POLICY_LOCK.json');policy.update(task='PIANO_CONTACT_DERIVATIVE_FEASIBILITY_RECOVERY_R1',no_more_solves=True,authority='DESIGN_PROVISIONAL',route='A',stop='STOP — HUMAN REVIEW');write('POLICY_LOCK.json',policy)
print('reports written',budget['total_charged_seconds'],speed)
