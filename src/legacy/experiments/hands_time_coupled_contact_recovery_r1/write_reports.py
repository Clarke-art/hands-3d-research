import json,time
from pathlib import Path
O=Path(__file__).resolve().parent
read=lambda n:json.loads((O/n).read_text(encoding='utf-8-sig'))
def write(n,v):(O/n).write_text(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
t=read('RECOVERY_TIMELINE_INPUT.json');m=read('MAIN_SOLVE_RESULTS.json');c=read('CORRECTION_SOLVE_RESULTS.json');a=read('ACTUAL_BLENDER_VALIDATION.json');adj=read('LOCAL_ADJACENCY_CHECK.json');guard=read('ADAPTIVE_DERIVATIVE_FALLBACK_CHECK.json');budget=read('NUMERICAL_BUDGET.json');contract=read('TIME_COUPLED_CONSTRAINT_CONTRACT.json');initial=read('DERIVATIVE_GUARD_VALIDATION.json');branch=read('NONSMOOTH_BRANCH_DIAGNOSIS.json');finalguard=read('FINAL_DERIVATIVE_GUARD.json')
contract.update(interface='ContactSet(t) + RigState(t) + MovingKeyGeometry(t) + TimeGrid + JointDomain + MotionBounds',authority='DESIGN_PROVISIONAL',mode_timeline=[dict(time=n['time'],modes=n['modes'],required_contacts=n['contacts']) for n in t['nodes']],external_reference=dict(id=t['preceding_valid_reference']['id'],time=t['preceding_valid_reference']['display_time'],use='held-out diagnostic only'),node_geometry='Full clipped pulp-face lower envelope at actual key angle, positive height extent on same face, original witness/pad-region and pad-height bounds; all88 key convex-piece triangle depth LP. Local self separating certificates plus mandatory full BVH acceptance.',joint_domain=t['joint_domain'],motion_bounds=t['motion_bounds'],variable_units=['mm']*3+['degree']*7+['unitless']*2,old_restored_states_are_fixed=False,targeted_initializer='One existing earliest feasible hand posture, analytically transported in root-Z to actual moving surfaces; all states checked against unchanged joint NLP, no independent IK solves.',initializer_scope='Tested on common single-required-contact mode only. Multi-contact/mode-change initialization not demonstrated.',solver_run_derivative='Single-step central FD node geometry and CasADi AD motion; final sensitivity disclosed separately',delivered_derivative_guard='Repeated FD step consistency with reject-on-unstable guard, added after solve and independently verified; not claimed retroactively')
write('TIME_COUPLED_CONSTRAINT_CONTRACT.json',contract)
solve=dict(authority='DESIGN_PROVISIONAL',main_solve_count=1,targeted_correction_count=1,independent_static_solves=0,main=m,correction=c,selected_attempt='targeted_correction',selected_nodes=c['nodes'],acceptance=dict(numerical_violation=c['violation'],all_actual_node_geometry=a['all_geometry_gates'],actual_motion=a['motion_pass'],actual_key_angle_difference_rad=a['key_state_match_max_rad'],solver_return_status=c['solver_stats']['return_status'],solver_objective_converged=False,stop_reason='Predeclared feasibility-first callback stops after an actually feasible iterate; native solver success=false is retained'),local_adjacency=adj['status'],performance=dict(main_jacobian_calls=m['solver_stats']['n_call_nlp_jac_g'],main_jacobian_wall_seconds=m['solver_stats']['t_wall_nlp_jac_g'],main_jacobian_mean_seconds=m['solver_stats']['t_wall_nlp_jac_g']/m['solver_stats']['n_call_nlp_jac_g'],correction_jacobian_calls=c['solver_stats']['n_call_nlp_jac_g'],correction_jacobian_wall_seconds=c['solver_stats']['t_wall_nlp_jac_g'],correction_jacobian_mean_seconds=c['solver_stats']['t_wall_nlp_jac_g']/c['solver_stats']['n_call_nlp_jac_g'],postsolve_cold_single_step_jacobian_seconds=finalguard['cold_full_jacobian_seconds'],postsolve_checked_adaptive_jacobian_seconds=guard['full_checked_jacobian_seconds'],geometry_node_evaluation_seconds=dict(main=[n['eval_seconds'] for n in m['node_stats']],correction=[n['eval_seconds'] for n in c['node_stats']]),actual_blender_nodes_seconds=a['wall_seconds'],actual_adaptive_connection_seconds=adj['wall_seconds'],budget=budget),derivative_scope=guard,prior_reference_connection=adj['external_reference_diagnostic'])
write('TIME_COUPLED_SOLVE_RESULTS.json',solve)
gates=dict(TIMELINE_AND_CONTACT_CONTRACT_PASS=True,TIME_COUPLED_JACOBIAN_VERIFIED='PASS_SCOPED_TO_TESTED_BLOCK_STRUCTURE_AND_POSTCHECKED_LOCAL_BRANCHES',COUPLED_CONTACT_FEASIBILITY_PASS=True,COUPLED_MOTION_BOUNDS_PASS=True,COUPLED_NODES_PASS_INTERPOLATION_FAIL=False,LOCAL_ADJACENCY_SAMPLED_PASS_HUMAN_PENDING=True,CONTACT_RECOVERED_BUT_MOTION_INCOMPATIBLE=False,TIME_COUPLED_RECOVERY_NOT_FOUND_WITHIN_BUDGET=False,NONSMOOTH_DERIVATIVE_PARTIAL=True,FAIL_CLOSED='ENFORCED_FOR_UNVERIFIED_BRANCHES_EXTERNAL_CONNECTION_AND_FULL_WINDOW')
write('FINAL_GATES.json',dict(authority='DESIGN_PROVISIONAL',route='A',gates=gates,full_25ms_pass=False,full_428ms_pass=False,prior_reference_connection_pass=False,Human_review='PENDING'))
lines=['# 精确时间与运动冲突复核','','DESIGN_PROVISIONAL。所有时间来自原候选JSON与Blender实际数据，不由报告速度反推。','', '|原样本|展示时间(s)|必要接触|运动琴键角(rad)|', '|---|---:|---|---:|']
for n in t['nodes']:lines.append(f"|{n['id']}|{n['time']:.12f}|MIDI {n['contacts'][0]['midi']} / 指{n['contacts'][0]['finger']} PRESS|{n['key_angles'][n['contacts'][0]['midi']-21]:.12f}|")
lines+=['','三个核心时刻均为同一新键PRESS；旧键处于RELEASE，不再强加旧键持键条件。原Action与原MIDI未改。全部控制向量、掌腕世界坐标、真实指腹三角面与见证点、对应键状态保存在RECOVERY_TIMELINE_INPUT.json的original_failed/recovered字段。','', '|相邻段|实际dt(s)|腕位移(mm)|平均腕速(mm/s)|500门禁允许位移(mm)|','|---|---:|---:|---:|---:|']
for i,s in enumerate(t['segments']):lines.append(f"|{i}→{i+1}|{s['dt']:.12f}|{s['wrist_displacement_mm']:.9f}|{s['wrist_speed_mm_s']:.6f}|{s['allowed_wrist_displacement_mm']:.9f}|")
lines+=['','参考族参数lambda分别为'+', '.join(f"{n['initial_latent'][10]:.9f}" for n in t['nodes'])+'；对应变化率约−440.566和482.768/s，超过已有5/s工程门禁。根位置、根旋转也有多项原授权速度违规；逐项角度/控制差与变化率见JSON。500mm/s是工程门禁，不是医学极限。','', '证据支持：独立单点求解缺少邻接约束，选择了分散的可行状态；没有接触模式切换。不足以证明它们位于数学意义上不连通的可行分支，更不能归因于C01绝对不可行。若将原三点强行固定，必要位移已证明违反速度上界；本轮三点均允许在原域内调整，故没有把该已知冲突作为固定边界启动优化。','', '未增加固定外部锚点：本任务只检验三个核心时刻。最近较早有效原状态'+t['preceding_valid_reference']['id']+f"在{t['preceding_valid_reference']['display_time']:.12f}s，仅作独立诊断。选中的局部首点与它相距{adj['external_reference_diagnostic']['distance_mm']:.6f}mm，允许位移仅{adj['external_reference_diagnostic']['allowed_mm']:.6f}mm；如果两端固定，所需平均速度{adj['external_reference_diagnostic']['necessary_average_speed_mm_s']:.3f}mm/s，不能连接。这个外部边没有被优化，也不能由此证明所有可调整内点都不可能。",'', '主要求解从独立恢复点出发，39次IPOPT迭代后超时，仍有接触/碰撞/运动违规。唯一修正采用已有最早恢复姿态作为共同手型，依据各时刻真实键法向解析调整根Z；未独立求解三个静态问题。初始化在同一963条硬约束中违规为0；随后真实联合求解保持可行并通过完整Blender验收。']
write('RECOVERY_TIMELINE_AUDIT.md','\n'.join(lines)+'\n')
write('NONSMOOTH_DERIVATIVE_GUARD.md',f'''# 非光滑导数防护

DESIGN_PROVISIONAL。不声明所有分支适合自动微分。

1. 每次节点值评估重新遍历授权指腹三角面，裁剪到真实运动键可演奏区域，重新选择下包络点与面身份。优化接触来自真实面计算，面最低点恰为顶点时也不是预选单顶点代理。记录face/surface/clipped-corner签名；没有固定错误接触面身份。
2. 每次值评估对全88键凸体重做三角候选过滤和内部侵入LP，记录最深三角见证点。自碰撞使用初始有效分离轴证书，记录min/max顶点分支；其固定轴是局部保守证书，不冒充全局最近轴。初始和接受状态另行重算最近轴，节点1/2分别检测到134/145个最近轴变化。每个被接受节点及补采样都必须通过Blender全非相邻面BVH零交叉门禁。
3. 同节点几何采用当前真实几何函数的局部中心差分；节点间腕坐标和关节运动块复用剪枝后的CasADi自动微分。结构非零来自真实局部/邻接依赖，未人为截掉小导数。36变量完整差分检查初值最大差{initial['global_vs_block_max_abs']:.3g}，遗漏可检测非零元0。
4. 实际两次求解使用单步长差分回退，不能事后宣称所有试探点导数已验证。最终发现节点0的lambda扰动跨越自碰撞min/max分支：21个自碰撞行对1e-4/1e-5名义步长敏感，最大差{branch['coarse_to_fine_max']:.9f}；接触面签名未变。缩小至1e-5/1e-6后差{branch['fine_to_finer_max']:.3g}。这是分支/步长问题，不是接触失效或人体不可行证据。
5. 交付的checked_jac进一步实施步长一致性回退：比较1e-4、1e-5、1e-6（无量纲变量另乘0.1）；差异小于1e-3才返回更细导数，否则抛出NON_SMOOTH_OR_UNVERIFIED，拒绝导数。该严格机制在求解后独立执行验证，未重跑优化，也不冒充历史求解时已启用。完整耦合方向检验在1e-6尺度最大误差约1.16e-6，在1e-7尺度约4.14e-6。全局未访问分支仍为NONSMOOTH_DERIVATIVE_PARTIAL。

几何代理与实际Blender不同步时必须拒绝候选；本轮接受节点和17个局部采样没有发生几何门禁不一致。不能由这些样本证明全部中间时刻或全MIDI。

性能需如实计费：实际主要求解44次Jacobian共162.109s；修正3次共11.942s；接受状态冷缓存单步长Jacobian约3.478s，新增严格回退检查约7.779s。初始报告中的0.0044s来自已缓存差分值，不能当作冷计算性能。未复述上一轮29.99倍为本轮速度。

证据：DERIVATIVE_GUARD_VALIDATION.json、FINAL_DERIVATIVE_GUARD.json、NONSMOOTH_BRANCH_DIAGNOSIS.json、ADAPTIVE_DERIVATIVE_FALLBACK_CHECK.json、JACOBIAN_SPARSITY.json。
''')
write('PRODUCT_ROUTE_EXIT_REVIEW.md',f'''# 产品路线退出评估

**A：三个核心节点的联合接触与运动约束得到可靠可行解，局部诊断采样通过。** 保留参数化接口；Human审核前不进入完整25ms回归。DESIGN_PROVISIONAL。

主要求解未证明稳健恢复能力：从相互分散的独立静态解出发，170.156秒后仍失败。可靠进展来自一个可复用的结构选择：优先选择共同姿态分支并随真实移动表面构造时间一致初值，再在同一时间耦合问题内验证与调整。修正初值已经满足硬约束，IPOPT执行1次迭代后以可行性优先回调退出；这不是声称完整目标函数收敛，更不是另一次静态IK搜索。

一般联合接口接受ContactSet(t)、RigState(t)、MovingKeyGeometry(t)、TimeGrid、JointDomain与MotionBounds；音乐身份来自数据。每节点动态面接触/全键几何，加上邻接腕/关节块，无逐音符手工改数学公式。RELEASE-only接口已检查：0条必要接触约束，仍保留全部碰撞块。共同姿态解析随键初值目前仅测试单个共同必要接触，尚未证明多接触切换、双手或换指通用性。

**可扩展性缺口仍大。** 3节点36变量963约束，几何FD依然使每次Jacobian约3.68—3.98秒，严格分支回退约7.78秒；不能用上一轮运动学剪枝的29.99倍代表本轮成本。数值总计{budget['total_seconds']:.3f}秒（含失败主要求解、准备、回放与后验导数诊断），未证明整曲规模可接受。

局部范围只有2.083333ms。与原较早有效参考的必要平均连接速度约6343.34mm/s，因此选中局部解不能直接嵌回原轨迹；也未检验后续出口。这强调更早手位准备和跨事件状态选择的重要性。未证明固定MIDI时间/C01绝对不可行，未更改音乐或指法。

本轮不触发B：节点间17个实际采样没有丢失接触或碰撞；不触发C：唯一针对性修正已得到独立真实验证的局部可行结果。下一阶段是否值得继续，必须由Human围绕入口/出口可行状态、时间参数化、动作先验、上游指法运动代价和成熟规划方法作产品级决策。不得继续单纯增加静态节点或把本结果推广为25ms通过。

STOP — HUMAN REVIEW。
''')
write('FINAL_RECOMMENDATION.md',f'''# 最终判断

**路线A：联合节点及其局部诊断连接通过，保留时间耦合接口。** 全部结果为DESIGN_PROVISIONAL。

- 范围：2.936009333333 → 2.938092666667s，共2.083333ms。3个节点均可调整，无固定外部锚点。有效接触始终为同一PRESS，旧键RELEASE不加持键要求。
- 主要求解：36变量、963不等式（接触为双侧容差带）、10928个Jacobian结构非零元；39次IPOPT迭代后Maximum_WallTime_Exceeded，违规0.703679，失败保留。
- 唯一修正：共同已有姿态的解析随键初值，原硬约束及目标不变。IPOPT1次迭代后可行性优先回调停止，状态User_Requested_Stop；不是目标完全收敛。最终联合数值违规0。
- 3个节点真实Blender接触、0.25mm侵入、全88键、自交、自然参考族、关节轴和域全部通过。两段实际腕速约374.322、374.136mm/s，原500mm/s门禁通过，所有原授权控制/关节变化界通过。
- 局部自适应补采样17点全部通过，最大采样腕速{adj['max_wrist_speed_mm_s']:.6f}mm/s；最大目标侵入{adj['max_target_intrusion_mm']:.9f}mm，错误区域侵入0、非相邻指面交叉0。标记LOCAL_ADJACENCY_SAMPLED_PASS_HUMAN_PENDING，不是全连续证明。
- 已测Jacobian块结构与严格回退分支通过；最终曾检出lambda引起的自碰撞min/max步长敏感，未访问分支继续NONSMOOTH_DERIVATIVE_PARTIAL。严格回退是在求解后单独验证，未重新运行求解。
- 新数值墙钟预算{budget['total_seconds']:.3f}/600秒，含失败主要求解及所有诊断。实际Jacobian成本未获得产品级优化结论。

**不能直接接回旧轨迹。** 与原较早有效参考candidate_017相距66.076459mm，真实时差下只允许5.208333mm；两端固定时所需平均腕速6343.34mm/s。该外部连接未优化，不能据此证明所有可调整选择均不可行。

|门禁|结论|
|---|---|
|TIMELINE_AND_CONTACT_CONTRACT_PASS|PASS|
|TIME_COUPLED_JACOBIAN_VERIFIED|已测结构与后验局部分支PASS；全局不作PASS声明|
|COUPLED_CONTACT_FEASIBILITY_PASS|PASS，真实Blender|
|COUPLED_MOTION_BOUNDS_PASS|PASS，仅核心节点与局部采样|
|COUPLED_NODES_PASS_INTERPOLATION_FAIL|不成立|
|LOCAL_ADJACENCY_SAMPLED_PASS_HUMAN_PENDING|成立|
|CONTACT_RECOVERED_BUT_MOTION_INCOMPATIBLE|本轮核心局部不成立；外部连接仍不兼容|
|TIME_COUPLED_RECOVERY_NOT_FOUND_WITHIN_BUDGET|最终不成立；主要尝试失败证据保留|
|NONSMOOTH_DERIVATIVE_PARTIAL|成立|
|FAIL_CLOSED|未验证分支、外部边和完整窗口保持关闭|

保护文件独立复核见PROTECTION_CHECK.json。无正式Action、视频、渲染序列、Rig/MIDI/琴键Action修改；原24样本25ms回归、428.571ms连接、B02及23音演奏全部未执行。

**DESIGN_PROVISIONAL — STOP — HUMAN REVIEW。** 下一步必须先经Human选择入口/出口与产品路线，不自动扩大窗口。
''')
# Label the known cached timing explicitly; preserve raw value, no replacement by an invented one.
initial['full_jacobian_timing_cache_state']='warm cache from preceding per-node finite differences; not a cold-performance claim';write('DERIVATIVE_GUARD_VALIDATION.json',initial)
policy=read('POLICY_LOCK.json');policy.update(no_more_solves=True,completed_main_solves=1,completed_corrections=1,stop='STOP — HUMAN REVIEW',route='A');write('POLICY_LOCK.json',policy)
print('Reports complete; numerical budget',budget['total_seconds'])
