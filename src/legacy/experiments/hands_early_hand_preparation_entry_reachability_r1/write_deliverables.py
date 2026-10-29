import sys,json,math,hashlib
from pathlib import Path
sys.dont_write_bytecode=True;O=Path(__file__).resolve().parent
def rd(n):return json.loads((O/n).read_text(encoding='utf8'))
def js(n,d):(O/n).write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf8')
def md(n,s):(O/n).write_text(s.strip()+'\n',encoding='utf8')
f=rd('FINAL_FACTS.json');budget=rd('NUMERICAL_BUDGET.json');protection=rd('PROTECTION_CHECK.json');scope=rd('PROTECTION_SCOPE_AUDIT.json');assert scope['inherited_frozen_protection_status']=='PASS'
cfg=rd('EXPERIMENT_CONFIG.json');bounds=rd('ENTRY_KINEMATIC_BOUNDS.json');main=rd('ENTRY_MAIN_RESULT.json');corr=rd('ENTRY_CORRECTION_RESULT.json');motion=rd('ENTRY_CANDIDATE_MOTION.json');midi=rd('SOURCE_MIDI_REVALIDATION.json');before=rd('PROTECTED_FILES_BEFORE.json');policy=rd('POLICY_LOCK.json')
entry=sorted(rd('ENTRY_ACTUAL_SAMPLES.json')+rd('ENTRY_ADAPTIVE_ACTUAL.json'),key=lambda r:r['display_time']);hold=sorted(rd('HOLD_PATH_BASE_ACTUAL.json')+rd('HOLD_PATH_ADAPTIVE_ACTUAL.json'),key=lambda r:r['display_time']);ep=f['entry_prefix'];hp=f['hold_diagnostic_prefix']
native= json.loads((O.parent/'hands_c01_whole_hand_motion_feasibility_r1/RIG_PREFLIGHT.json').read_text(encoding='utf8'))['right_native_sha256']
identity=dict(task=cfg['task'],source_MIDI_path=midi['midi'],source_MIDI_sha256=midi['midi_sha256'],source_timeline_path=midi['timeline'],source_timeline_sha256=midi['timeline_sha256'],fingering_path=midi['candidate_file'],fingering_sha256=midi['candidate_sha256'],candidate_id='C01_PIANOPLAYER',right_fingers=dict(R07=1,R08=3),source_scene_path=policy['source_action_scene']['path'],source_scene_sha256=before[policy['source_action_scene']['path']],frozen_right_native_sha256=native,source_skin_sha256=before[str(O.parent/'hands_time_coupled_contact_recovery_r1/SKIN_MODEL.npz')],source_key_table_sha256=before[str(O.parent/'hands_time_coupled_contact_recovery_r1/SKIN_MODEL_META.json')],MIDI_reparsed=True,Action_reevaluated=True,all_original_Action_payloads_match=f['original_actions_all'],all_native_mesh_rig_identities_match=f['native_identity_all'],history_baseline_match=True,protected_file_count=protection['before_count'])
identity.update(global_protection_status='FAIL_CONCURRENT_AUDIT_CHANGES',inherited_frozen_protected_count=scope['inherited_frozen_protection_count'],inherited_frozen_protected_all_match=True,protection_scope_file='PROTECTION_SCOPE_AUDIT.json');js('INPUT_IDENTITY_AUDIT.json',identity)
speed=max(r['maximum_wrist_speed_mm_s'] for r in motion['dense_segment_checks']);joint=max(r['maximum_joint_rate_deg_s'] for r in motion['dense_segment_checks']);latentpass=all(r['latent_pass'] for r in motion['samples']);ratepass=speed<=500 and joint<=240 and latentpass and f['actual_secant_peak_wrist_mm_s']<=500+1e-5 and f['actual_secant_peak_joint_deg_s']<=240+1e-5
guardrecords=[g for gs in corr['guards'] for g in gs];accepted=sum(g['status']=='VERIFIED_LOCAL_STRICT_FD' for g in guardrecords);rejected=sum(g['status'].startswith('FAIL_CLOSED') for g in guardrecords)
gates=dict(G4_HOLD_PREPARATION_FEASIBLE='PASS_SAMPLED_PREFIX_ONLY',ENTRY_KINEMATIC_BOUNDS_VERIFIED=True,ENTRY_TARGET_REACHABLE=False,EARLY_PREPARATION_PATH_SAMPLED_PASS=False,ENTRY_CONTACT_TIMING_PASS=False,ENTRY_MOTION_BOUNDS_PASS='PASS_SCOPED_TO_ORIGINAL_SPEED_RATE_GATES' if ratepass else False,NONSMOOTH_DERIVATIVE_GUARDED='PARTIAL: IN_SOLVER_GUARD_EXECUTED_AND_REJECTION_ENFORCED; UNIVERSAL_AND_NEW_SELF_AXIS_COVERAGE_UNPROVEN',ENTRY_NOT_FOUND_WITHIN_BUDGET=True,PRODUCT_ROUTE_PIVOT_REQUIRED=True,FAIL_CLOSED=True)
js('FINAL_GATES.json',dict(authority='DESIGN_PROVISIONAL — STOP — HUMAN REVIEW',route='B',gates=gates,GLOBAL_PROTECTION_PASS=False,INHERITED_FROZEN_INPUT_PROTECTION_PASS=True,full_entry_PASS=False,full_25ms_PASS=False,E5_ON_plus_35ms_PASS=False,Human_naturalness='PENDING',numerical_budget_seconds=budget['total_seconds'],protected_file_count=protection['before_count']))
js('G4_HOLD_PREPARATION_RESULTS.json',dict(authority='DESIGN_PROVISIONAL — STOP — HUMAN REVIEW',status='SAMPLED_PARTIAL_PREPARATION_FEASIBLE_FULL_HOLD_ENTRY_FAILED',actual_B2_start=True,original_G4_HOLD_window=[cfg['start'],cfg['junction']],hold_diagnostic_prefix=hp,main_candidate_hold_prefix=ep,continuous_position_representation='Main candidate is C0 in latent controls and frozen FK; diagnostic normal projection has only sampled branch evidence',sampling='120Hz + exact knots/events + first-failure adaptive subdivisions',naturalness='Reference-family and domain pass; Human not approved; no medical comfort claim',failed_regions='Preparing MIDDLE intersects intervening D#5; original simultaneous-flex probes also C#5',static_probe_sources=['HOLD_PROBE_ACTUAL.json','HOLD_CORRECTED_ACTUAL.json','DELAYED_FLEX_ACTUAL.json'],actual_path_sources=['HOLD_PATH_BASE_ACTUAL.json','HOLD_PATH_ADAPTIVE_ACTUAL.json','ENTRY_ACTUAL_SAMPLES.json','ENTRY_ADAPTIVE_ACTUAL.json'],remaining_full_entry_obligations='Late G4 HOLD clearance, common boundary contact residual, E5 PRESS surface contact plus RELEASE-key clearance',absolute_anatomical_or_fingering_impossibility_proven=False))
validation=dict(authority='DESIGN_PROVISIONAL — STOP — HUMAN REVIEW',status='FAIL_FULL_ENTRY',actual_oracle='Independent Blender 5.1.2 evaluation of frozen Rig/FK/weighted skin and original key Action; triangle-level contact and entity penetration; actual whole-key geometry',all_88_keys=f['all_keys_count']==88,full_skin_parity=f['maximum_full_skin_parity_mm'],wrist_parity_mm=f['maximum_wrist_parity_mm'],raw_skin_parity_file='FULL_SKIN_AND_WRIST_PARITY.json',original_input_identity=identity,full_entry_sample_count=f['entry_sample_count'],full_entry_failed_count=f['entry_failed_count'],first_failure=ep,required_contact_failures=f['required_contact_failures'],maximum_target_depth_mm=f['entry_target_max_depth_mm'],maximum_wrong_region_depth_mm=f['entry_wrong_max_depth_mm'],maximum_nonadjacent_self_crossings=f['entry_self_crossings_max'],all_authorized_anatomy=f['all_authorized_anatomy'],motion_bounds_pass=ratepass,maximum_analytic_wrist_speed_mm_s=speed,maximum_analytic_joint_rate_deg_s=joint,maximum_actual_secant_wrist_speed_mm_s=f['actual_secant_peak_wrist_mm_s'],maximum_actual_secant_joint_rate_deg_s=f['actual_secant_peak_joint_deg_s'],actual_fd_peak_acceleration_mm_s2=f['actual_fd_peak_acceleration_mm_s2'],velocity_continuity=motion['C1_velocity_continuity'],acceleration_at_velocity_jumps='Undefined; finite difference estimates do not certify smoothness',finite_samples_not_continuous_collision_proof=True,Human_naturalness='NOT_APPROVED',source_saved=False,source_files=['ANCHOR_ACTUAL.json','HOLD_PROBE_ACTUAL.json','HOLD_CORRECTED_ACTUAL.json','DELAYED_FLEX_ACTUAL.json','HOLD_PATH_BASE_ACTUAL.json','HOLD_PATH_ADAPTIVE_ACTUAL.json','ENTRY_ACTUAL_SAMPLES.json','ENTRY_ADAPTIVE_ACTUAL.json','ACTUAL_CANDIDATE_TIME_DIFFERENCES.json'])
validation.update(global_protection_status='FAIL_CONCURRENT_AUDIT_CHANGES',inherited_frozen_protection_status='PASS',protection_scope_file='PROTECTION_SCOPE_AUDIT.json');js('ACTUAL_BLENDER_VALIDATION.json',validation)
trajectory=rd('EARLY_PREPARATION_TRAJECTORY.json');trajectory.update(status='EXECUTED_CANDIDATE_FAILED',complete_entry_pass=False,actual_validation_file='ACTUAL_BLENDER_VALIDATION.json',actual_samples_file=['ENTRY_ACTUAL_SAMPLES.json','ENTRY_ADAPTIVE_ACTUAL.json'],sample_count=f['entry_sample_count'],failed_samples=f['entry_failed_count'],first_sampled_failure_time=ep['first_sampled_failure_time'],primary_candidates=1,targeted_corrections=1,C0_position_continuity=True,C1_velocity_continuity=False,Human_naturalness='NOT_APPROVED');js('EARLY_PREPARATION_TRAJECTORY.json',trajectory)
table='\n'.join(f"| {r['from_id']} → {r['to_id']} | {r['wrist_distance_mm']:.6f} | {r['minimum_wrist_seconds']*1000:.6f} | {r['minimum_joint_seconds']*1000:.6f} | {r['available_seconds']*1000:.6f} | {'满足必要下界' if r['necessary_bounds_pass'] else '固定端点冲突'} |" for r in bounds['anchors'])
md('ENTRY_TIMELINE_AND_KINEMATIC_BOUNDS.md',f'''
# 真实入口时间与必要运动下界

DESIGN_PROVISIONAL — STOP — HUMAN REVIEW

本轮实际重新解析原 MIDI、绑定23音符与C01指法，并在独立后台 Blender 中读取原 Action、冻结 Rig 和实际88键几何。本轮没有写入正式或历史目录。输入路径与 SHA256 见 INPUT_IDENTITY_AUDIT.json；独立前后重算扩展保护文件 {protection['before_count']} 个。全集合检测到3个变化、15个新增，均在Piano存储清理审计目录；已通过另一聊天的原始记录确认同期授权审计写入，未回滚其成果。继承冻结保护清单 {scope['inherited_frozen_protection_count']} 个文件和本轮源输入全部一致。扩展保护集仍标FAIL，不把并发变更排除后冒充原全集合PASS。详见 PROTECTION_SCOPE_AUDIT.json。

|事件|展示时间 s|证据|
|---|---:|---|
|R07/G4 ON|2.492855|MIDI tick1920，PPQ384，tempo428571us，展示偏移0.35s|
|B2自然G4持键起点|{cfg['start']:.9f}|原B_SOLVE_2状态精确固定，真实几何复现|
|旧P2参考|2.720000000|原Action复读；不强制经过|
|G4 OFF / E5 ON|{cfg['junction']:.12f}|tick2304，原Action和合同一致|
|旧局部合格入口|{cfg['end']:.12f}|上一轮修正首节点重新验收|
|E5 ON+35ms|2.956426000|本轮只复读Action，不做该完整窗口回归|

G4准备可用时间 {(cfg['junction']-cfg['start'])*1000:.6f}ms；到本轮E5目标时间 {(cfg['end']-cfg['start'])*1000:.6f}ms。G4在HOLD为持续合法拇指面级接触，原Action转角约0.087123208rad。事件后按原合同解除G4持键义务，E5转入PRESS，琴键恢复和下行曲线原样保留。声学、接触力与舒适医学标准未建模。

|连接（端点固定时）|腕距 mm|腕速500下最短时间 ms|关节240下最短时间 ms|真实可用 ms|判断|
|---|---:|---:|---:|---:|---|
{table}

下界使用实际Blender腕位置、恢复的工程关节和原latent速率限制；综合必要时间另见 ENTRY_KINEMATIC_BOUNDS.json。前三个固定连接的重要区分：B2到旧共同边界和旧局部入口都有足够的总时间下界，但共同边界到旧局部入口只有14.583333ms，腕距67.006710mm，至少需要134.013420ms，固定端点时排除。不能把早期速度余量当作持键几何可达证明，也不能把这个局部固定端点冲突扩展到所有可调整入口。

实际准备证据：诊断路径通过至 {hp['last_pass_time']:.12f}s，主候选通过的采样前缀至 {ep['last_pass_time']:.12f}s。中指与途经黑键D#5的干涉首先破坏后续准备，而不是500mm/s速度下界。拇指持续接触本身在通过前缀内不阻止腕移动；完整可达手位区域和跨障碍路线没有建立。

所有速度、差分加速度均使用真实时间差；详见 ENTRY_CANDIDATE_MOTION.json、ACTUAL_CANDIDATE_TIME_DIFFERENCES.json。候选只保证位置C0，节点处速度跳变，不能用节点速率通过推出自然或加速度连续。
''')
md('ENTRY_TARGET_SET_AND_ANCHORS.md',f'''
# 入口集合与锚点

DESIGN_PROVISIONAL — STOP — HUMAN REVIEW

唯一不可调整的运动锚点是 {cfg['start']:.9f}s 的实际B2完整12维latent状态，来自原B_SOLVE_2，并保持精确原26维关节参考映射。真实固定误差为 {corr['fixed_start_error']:.12g}。音乐时间、原C01的拇指G4与中指E5、88键Action、冻结Rig、自然参考族、原碰撞和速率门禁不可调整。

目标是 {cfg['end']:.12f}s 的任意原合同合格E5接触构型集合，不指定原局部控制向量。每个成员必须真实指腹跨面、pad在合法区域、侵入≤0.25mm、非相邻指面交叉0，并满足原关节族与域。事件构型也可调整；事件左右位置连续要求共同闭接触边界相容，不能借半开状态标签瞬移。

旧P2、candidate_017和旧局部入口均为只读参考，不是必经锚点。旧共同边界重新通过实际双指接触检查，B2腕距24.273069mm；掌根yaw=-12°、拇指末节控制接近0°边界，Human自然度风险保留。旧局部入口也重新通过，但它离旧共同边界67.006710mm，不能在14.583333ms直接接入。

本轮7个时间耦合节点同时施加接触、全键代理碰撞、参考族、邻接腕速和映射关节速率。实际B2固定，其余均可调整；原旧局部片段保持不变。初始化使用延后准备指屈曲和原Action法向运输，后段有受原240deg/s限制的拇指释放控制。没有把目标指定为E5专属手工终点；这些参考值只作为本次输入初值。

实际结果：没有找到合格入口集合成员的连续可达路径。修正候选的终点E5真实接触失败，并发生非目标/错误区域侵入。即使前缀、事件或单点通过，也不升级为入口集合可达PASS。

输入与实现：EXPERIMENT_CONFIG.json、ENTRY_SOLVE_INPUT.json、TIME_COUPLED_ENTRY_CORRECTION_INTERFACE.json、ENTRY_CORRECTION_RESULT.json、EARLY_PREPARATION_TRAJECTORY.json。
''')
rows='\n'.join(f"|{r['name']}|{r['wall_seconds']:.6f}|{r['status']}|" for r in budget['stages'])
md('NONSMOOTH_AND_RUNTIME_AUDIT.md',f'''
# 非光滑与运行审计

DESIGN_PROVISIONAL — STOP — HUMAN REVIEW

严格导数保护实际参与了SLSQP和CasADi/IPOPT回调。每次检查接触面/裁剪特征、琴键实体获胜面、固定自碰撞轴的min/max特征；重算每个扰动下的分支，用1e-4、1e-5、必要时1e-6尺度的中心差分交叉验证，最大差异<1e-3才使用。失败抛异常并拒绝导数，没有静默冻结错误分支。这个数值一致性条件只证明测试点的局部一致性，不证明全局光滑。

原延拓前两个状态在优化器内实际拒绝。分支诊断定位到接触不等式第10行：随着最低接触面的选择改变，该面所属裁剪多边形的max-gap从约1.775772mm跳到0.041037mm。差分误差分别达到954104.026822与242.287450。该跳变主要来自代理表达，而非原接触合同的必然矛盾。

修正仅在本实验副本进行：以所有投影指腹三角面 max(min(-min_gap,max_gap)) 表示真实跨面存在条件，消除“最低面绑定整片max-gap”的伪跳变；允许裁剪见证点在可触区边界（移除内部额外0.001mm见证内缩），保留pad域、跨面阈值以及全部真实Blender接触/侵入验收。原接触合同和历史模块未改。CONTACT_PROXY_REPAIR.json保存改前后哈希与理由。

主候选因继承的HIGH整数数组使固定B2上界被截断，在任何迭代前被IPOPT拒绝。唯一针对性修正将上下界转float再固定精确B2，原时序和约束不变，完整失败记录保留于 ENTRY_MAIN_RESULT.json 与 ENTRY_CORRECTION_RATIONALE.json。

修正求解共记录 {len(corr['history'])} 个迭代回调，约束最大违约从3.171479降至 {corr['violation']:.9f}，未取得可行解；返回 {corr['status']}。实时保护记录 {accepted} 次局部差分一致、{rejected} 次严格拒绝。最终拒绝位于节点2，跨尺度差异1.088481与0.712314，导致Invalid_Number_Detected；这是导数保护中止，不能误报为目标收敛或纯超时。失败导数的完整试探控制向量未记录，故不宣称该特定试探可独立重放。分支日志保留在 ENTRY_CORRECTION_RESULT.json。

IPOPT日志：总墙钟约203.881s，Jacobian约198.65s，局部几何多尺度差分为主要瓶颈。并未关闭真实碰撞验收。稀疏邻接腕/关节块用已验证CasADi AD；本轮另以真实时间方向中心差分验证不同节点段的运动AD，原始误差见 ENTRY_CANDIDATE_MOTION.json。固定B2对应变量经IPOPT消元，但完整接口仍保留84维与节点结构。

|阶段|保守墙钟秒|结果|
|---|---:|---|
{rows}

记录总数值阶段墙钟 {budget['total_seconds']:.6f}s <600s；其中数值优化阶段为持键延拓、主候选与唯一修正，其余记录包括分支与采样计算，属于更保守口径。保护SHA、只读输入解析、Blender独立验收和报告I/O不属于求解耗时。未使用剩余预算增加迭代或第三条轨迹。

边界：自碰撞分离轴仍按节点初始近面集合固定，只检查其min/max特征；新轴重生成、未进入代理近面集合的新自碰撞对，以及所有未经触达分支并未获得通用导数验证。接受端仍以全88键及全部真实非相邻指面检查fail closed。本轮 NONSMOOTH_DERIVATIVE_GUARDED 为“部分执行证据”，不是所有分支/轴覆盖PASS。下一路线需要把特征依赖和安全回退作为正式接口，而不是再以局部有限差分成功代替完整保证。
''')
md('PRODUCT_ROUTE_DECISION.md',f'''
# 产品路线决策：B，必须转向更高层规划与运动表示

DESIGN_PROVISIONAL — STOP — HUMAN REVIEW

保留项目，停止同一G4→E5局部补丁循环。本轮确实利用B2之后的持键时间完成了部分提前准备，但没有建立真实完整入口，因此路线A不成立。路线B成立：有完整从真实起点出发的采样可行前缀，而不是新增几个独立静态点；剩余持键清障和释放/触键入口仍失败。不据此宣称当前指法或人体动作绝对不可行。

|问题|实际证据|决策含义|
|---|---|---|
|前序手位能否提前移动|主候选采样前缀长{ep['duration_sampled_prefix_ms']:.3f}ms，腕移{ep['wrist_displacement_mm']:.3f}mm；合法G4接触保持|可提前准备，工程速率下界不是主阻碍|
|拇指持键是否封死换位|通过前缀内未失去拇指接触；共同静态边界也通过|未证明封死全部可达域，不能推论人体/指法绝对不可行|
|是否有更近入口|共同边界比旧局部入口更近；端点与事件均允许调整|原入口并非唯一，但较近静态候选不等于整段可达|
|能否消除最后10ms大位移|新后段峰值腕速{speed:.3f}mm/s、关节速率{joint:.3f}deg/s，低于原门禁|速度问题可以缓解；几何与E5接触仍失败，不能产品验收|
|实际瓶颈|中指途经D#5实体；参考族/屈曲与横移参数组合；代理分支跳变和实时导数拒绝|主要是手位路线与运动表示/求解稳定性，接触清障是实质约束|
|接触合同是否矛盾|原合同下B2、共同静态边界、旧局部片段均可复现|没有合同绝对矛盾证据；代理表达缺陷已经实测定位|
|产品收益|一次主候选+一次修正，仍{f['entry_failed_count']}/{f['entry_sample_count']}样本失败|保留资产接口，停止增加节点/毫秒/迭代的循环|

下一阶段先做较长音乐上下文的手位走廊规划：在多个音符的HOLD/RELEASE/PRESS条件下选择腕位置、手掌朝向、指尖清障顺序与边界状态集合，再把走廊交给约束IK/轨迹优化。指法规划加入可达性与清障反馈，避免仅按音符跨度选择指法。运动表示应结合真实演奏参考/动作数据形成腕—指协调先验，再以原接触合同和实际几何修正；比较多种运动先验或重定向框架时使用同一冻结输入、时间与验收接口，先跑一个入口级对照，不能凭算法名称宣称成熟框架更优。本轮没有安装、调研或实测其他后端，没有外部成熟框架优越性结论。

复用资产：冻结Rig与FK/加权蒙皮、88键几何和原Action、源MIDI/指法绑定、接触状态编译器、自然参考族、面级验收、稀疏运动AD、实时导数保护与输入哈希基线。将“接触特征的选择与更新”做成明确依赖；当前12维lambda/alpha参考族仍是受限研究表示，不能当作通用自然动作空间。

新接口按 MIDI Event Timeline + Fingering + Contact Modes + Key Action + Rig + Motion Constraints 传入。新增输入与求解核心未按G4/E5音名分支；B2、共同边界、延后屈曲和拇指释放初始化仍来自本例的人工参考，本轮只验证一个输入，因此不能宣称自动手位规划或通用MIDI生成已完成。继承rig_model中的旧fixture时间常量没有参与本轮新时间网格，也未被提升为通用产品接口。

后续两个代表任务只指定、未执行：较容易的C4–D4–E4–F4–G4均匀连续上行；困难的跨八度C4→C5并伴随换指/再定位序列。指法应由规划器产生并接受运动可行性反馈；正式回归前固定各自MIDI、Action和合同。本轮真实入口尚未通过，先批准新的高层路线并解决入口级可达性，之后才进入这两个样本，不能自动进入完整25ms、ON+35ms、B02、23音双手或教材生产。
''')
gate_table='\n'.join(f'|{k}|{v}|' for k,v in gates.items())
md('FINAL_RECOMMENDATION.md',f'''
# 最终建议：路线B，停止G4→E5专项局部修补

DESIGN_PROVISIONAL — STOP — HUMAN REVIEW

**能真正利用前一个音符的持键时间做部分提前准备；尚不能让已验证局部动作获得完整、自然的真实入口。** 本轮从实际B2起点、原MIDI时序与冻结Rig出发完成一次主入口候选和唯一针对性修正。入口整体FAIL，不能报告PASS，也没有证明当前指法或人体动作绝对不可行。

最强实际证据是主候选从 {ep['start']:.9f}s 到 {ep['last_pass_time']:.12f}s 的采样可行前缀：{ep['passing_prefix_sample_count']}个时刻、{ep['duration_sampled_prefix_ms']:.3f}ms，腕移{ep['wrist_displacement_mm']:.3f}mm，中指到E5可触面的距离从{ep['initial_middle_distance_mm']:.3f}降至{ep['middle_to_E5_distance_mm']:.3f}mm。G4真实面级接触、88键侵入、非相邻指面与关节门禁通过。有限采样不构成连续无碰撞数学证明，Human自然度尚未批准。

全入口共 {f['entry_sample_count']} 个独立Blender样本，{f['entry_failed_count']}个失败。补采样后的首个失败为 {ep['first_sampled_failure_time']:.12f}s，中指与D#5错误区域侵入 {ep['first_failure_wrong_depth_mm']:.6f}mm；整段最大错误区域侵入{f['entry_wrong_max_depth_mm']:.6f}mm >0.25mm。E5在2.928717666667s和终点2.936009333333s接触失败。目标键最大侵入{f['entry_target_max_depth_mm']:.6f}mm，非相邻指面交叉0，关节族/域均通过；这些通过不能覆盖错误区域和接触失败。

腕速峰值{speed:.3f}mm/s、关节速率峰值{joint:.3f}deg/s，原速率门禁通过。候选位置连续，但节点速度跳变，节点处有限加速度和自然度没有成立。旧共同边界到旧局部入口67.007mm，在14.583ms内固定连接不可行；本轮端点允许调整，仍未打通几何和接触入口。因此既有2.083ms片段原样保留为技术资产，不能升级为整段动作。

主要问题是音乐上下文中的手位/指尖清障路线、受限运动表示与接触几何代理稳定性。实时多尺度导数保护确实参与求解，并拒绝未验证分支；原伪不连续代理已在实验副本修正，最终IPOPT仍因新的局部导数不一致停止，未收敛。没有证据把所有失败归咎于原接触合同，也不能以预算内搜索失败证明人体不可能。

建议保留冻结Rig、真实蒙皮、Action、合同、参考族、稀疏接口与验收，转向较长上下文手位规划、动作先验+接触IK，以及运动可行性反馈到指法。不要再以增加几个静态节点、优化几毫秒或提高迭代数作为下一里程碑。下一最小产品任务是新的高层方案在同一真实B2入口完整通过原时序和几何门禁；之后才考虑完整25ms及E5 ON+35ms验收。

|最终门禁|结果|
|---|---|
{gate_table}

数值阶段总墙钟{budget['total_seconds']:.6f}s <600s；一条主候选和一次有证据修正，无随机重启。扩展保护集{protection['before_count']}个文件独立前后重算：3个变化、15个新增、删除0，全部发生在同期另一个聊天授权生成的Piano存储清理审计目录，保留原变更并将全集合标FAIL。继承冻结清单{scope['inherited_frozen_protection_count']}个文件、所有Hands历史及原MIDI/C01/Action/Rig身份均一致；没有恢复或覆盖其他聊天成果。范围与并发证据见 PROTECTION_SCOPE_AUDIT.json。完整实际蒙皮/FK最大误差{f['maximum_full_skin_parity_mm']:.9f}mm。未输出正式Action、Blend、视频或诊断静帧。

八项交付齐全，所有原始候选、拒绝导数和失败采样保留。批准前停止，不自动进入25ms回归、B02、23音双手动画、其他代表音型或教材生产。
''')
required=['ENTRY_TIMELINE_AND_KINEMATIC_BOUNDS.md','G4_HOLD_PREPARATION_RESULTS.json','ENTRY_TARGET_SET_AND_ANCHORS.md','EARLY_PREPARATION_TRAJECTORY.json','ACTUAL_BLENDER_VALIDATION.json','NONSMOOTH_AND_RUNTIME_AUDIT.md','PRODUCT_ROUTE_DECISION.md','FINAL_RECOMMENDATION.md']
assert all((O/n).is_file() for n in required);assert policy['no_more_solves'] and budget['under_budget'];assert not any(O.glob('*.blend'))
receipt=dict(status='DELIVERABLES_COMPLETE_GLOBAL_PROTECTION_FAIL_CONCURRENT_AUDIT_STOP_HUMAN_REVIEW',route='B',required_deliverables={n:hashlib.sha256((O/n).read_bytes()).hexdigest() for n in required},gates_file='FINAL_GATES.json',input_identity_file='INPUT_IDENTITY_AUDIT.json',protected_before_count=protection['before_count'],protected_after_count=protection['after_count'],protected_all_match=False,protected_changed_count=3,protected_new_count=15,protected_deleted_count=0,inherited_frozen_protected_all_match=True,protection_scope_file='PROTECTION_SCOPE_AUDIT.json',main_candidates=1,targeted_corrections=1,numerical_wall_seconds=budget['total_seconds'],complete_entry_pass=False)
js('DELIVERY_CHECK.json',receipt);print('DELIVERY_COMPLETE',json.dumps(receipt,ensure_ascii=False),flush=True)
