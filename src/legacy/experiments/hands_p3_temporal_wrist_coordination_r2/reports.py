"""Evidence closure after the sole controlled timeout. No FK, new solve or
Blender candidate diagnosis is performed on the interrupted intermediate state.
"""
from support import *
sys.path.insert(0,str(OLD/'_deps'))
from persistence import atomic_record,atomic_json,load_record
import numpy as np
gate=read(O/'RESULT_PERSISTENCE_GATE.json');inp=read(O/'INPUT_CONTRACT_GATE.json');P=read(O/'POLICY.json');I=read(O/'INPUT_BINDINGS.json');lock=read(O/'POLICY_LOCK.json')
assert gate['RESULT_PERSISTENCE_GATE']=='PASS' and inp['pass_']
assert sha(O/'POLICY.json')==lock['policy_sha256'] and all(sha(O/n)==h for n,h in lock['scripts'].items())
assert not (O/'FINAL_OPTIMIZER_RESULT.npz').exists()
exception=read(O/'FORMAL_EXCEPTION.json');abort,meta=load_record('EXCEPTION_LAST_FINITE_STATE.npz');initial,initial_meta=load_record('FORMAL_INITIAL_STATE.npz');schema,schema_meta=load_record('INPUT_GATE_SCHEMA_RECORD.npz');source,source_meta=load_record('SOURCE_PROBE.npz')
assert meta['record_type']=='EXCEPTION_LAST_FINITE_STATE' and meta['not_final_optimizer_result']
assert np.isfinite(abort['x']).all() and np.isfinite(abort['fun']).all()
T=np.array(P['control_times_sec']);K=len(T);st=schema['source_states'].copy();st[1:-1]=abort['x'][:(K-2)*26].reshape(K-2,26)
xy=schema['contact_xy'].copy();xy[8:14]=abort['x'][(K-2)*26:].reshape(6,2)
lo=np.r_[P['root_low'],np.array(P['joint_bounds_deg'])[:,0].ravel()];hi=np.r_[P['root_high'],np.array(P['joint_bounds_deg'])[:,1].ravel()]
raw_before=sha(O/'EXCEPTION_LAST_FINITE_STATE.npz');checkpoint_before=sha(O/'LAST_FINITE_EVALUATION.npz')
atomic_record('INTERRUPTED_STATE_BUNDLE.npz',dict(x=abort['x'],fun=abort['fun'],control_times=T,states=st,source_states=schema['source_states'],contact_xy=xy,x0=initial['x'],initial_fun=initial['fun'],state_lower=lo,state_upper=hi,sparsity_data=schema['jac_data'],sparsity_indices=schema['jac_indices'],sparsity_indptr=schema['jac_indptr']),dict(**meta,decoded_parameter_layout=True,optimizer_return_status='NOT_RETURNED_CONTROLLED_TIMEOUT',nfev=None,njev=None,optimality=None,accepted_iteration_status='UNKNOWN; last finite residual evaluation may be a finite-difference trial',source_exception_sha256=raw_before,additional_geometry_computed=False))
assert sha(O/'EXCEPTION_LAST_FINITE_STATE.npz')==raw_before and sha(O/'LAST_FINITE_EVALUATION.npz')==checkpoint_before
rootspan=np.ptp(st[:,:6],axis=0);initial_states=schema['states'];rootchange=float(np.max(abs(st[:,:6]-initial_states[:,:6])))
calls=int(meta['residual_calls']);elapsed=float(meta['elapsed_seconds']);cost0=float(initial['fun']@initial['fun']/2);costlast=float(abort['fun']@abort['fun']/2)
info=dict(RESULT_PERSISTENCE_GATE='PASS',input_gate_pass=True,final_optimizer_result_exists=False,exception_state_roundtrip_pass=True,exception_original_evidence_preserved=True,raw_residual_calls=calls,controlled_elapsed_seconds=elapsed,control_nodes=K,variables=len(abort['x']),time_varying_root_parameter_span=rootspan,largest_root_parameter_change_vs_initial=rootchange,intermediate_weighted_cost=costlast,initial_weighted_cost=cost0,cost_is_not_contact_or_geometry_gate=True,accepted_last_iteration_unknown=True,STATIC_LAYOUT_VALID='UNKNOWN_NO_VALID_FINAL_RESULT',TEMPORAL_CONNECTION_PLAUSIBLE='UNKNOWN_NO_VALID_FINAL_RESULT',CONTINUOUS_TRAJECTORY_VALIDATED='NOT_PERFORMED',candidate_blender_validation='NOT_RUN_REQUIRED_STOP_NO_FINAL_RESULT',source_blender_readonly_samples=len(source['times']),formal_optimizer_calls=1,optimizer_retries=0,new_actions=0,new_blends=0,new_videos=0)
atomic_json('EVIDENCE_SUMMARY.json',info)
atomic_json('BLENDER_VALIDATION_STATUS.json',dict(status='NOT_RUN_NO_VALID_FINAL_OPTIMIZER_RESULT',source_preflight_performed=True,source_preflight_samples=len(source['times']),candidate_skin_validated=False,intermediate_or_initialization_not_used_as_candidate=True,reason='User Gate 5 requires stop when a valid terminal result does not exist. Controlled timeout only produced a labeled intermediate state.'))
ledger=read(O/'COMPUTE_LEDGER.json');core_total=float(ledger['used_seconds'])
protect();before=read(O/'PROTECTED_BEFORE.json');after={p:sha(p) for p in before};changes=[p for p in before if before[p]!=after[p]];assert not changes
atomic_json('PROTECTION_CHECK.json',dict(referenced_files_checked=len(before),all_unchanged=True,changes=changes,before=before,after=after,R1_history_unchanged=True,C1_A2_B3_and_formal_assets_unchanged=True,independent_piano_access=False,historical_concurrent_FAIL='Retained; this narrow SHA check does not supersede it',path_migration=0,new_actions=0,new_blends=0,new_videos=0))
def report(name,text):(O/name).write_text(text.strip()+'\n',encoding='utf8')
report('RESULT_PERSISTENCE_VALIDATION.md',f'''
# 结果保存验证

**RESULT_PERSISTENCE_GATE = PASS。实际异常状态已完整留证；正式优化返回终态未产生。**

R1第106行调用`surface_metrics`，而其原导入代码只截取上一轮evaluate.py中`M=read(MODEL/...)`至`ref_t=REF`之前的内容；函数定义位于该截取范围之后。本轮problem.py在隔离副本显式导入该函数。R1源码、失败日志与不可恢复的历史终态未改写，未声称恢复R1结果。

Gate 1在正式优化前独立通过：确定性x、fun、grad、active_mask、状态序列、时间、接触XY、稀疏Jacobian结构及迭代元数据全部序列化并逐字段读回。另做已知接触函数测试。模拟异常可保存最后有限状态；模拟写入失败证明已有最终记录及旧检查点SHA不变；同名最终结果写入直接拒绝。

保存方式是同一NPZ内的数值数组＋UTF-8 JSON元数据，先在本目录写`.pending`、flush/fsync、重新读取核对，再原子替换。最终结果文件不可覆盖；可更新的检查点使用独立文件。测试产生的pending证据保留，并不代表正式终态。二级诊断或报告失败不会删除原始结果。

本地SciPy {gate['scipy_version']}支持callback；本轮采用与实际接口兼容的更小方案：残差完整返回有限值后，至少每5秒原子保存一次独立检查点，异常时保存最后有限参数、残差、调用计数、耗时和完整traceback。检查点可能是有限差分试探点，明确标为中间状态，未冒充已接受迭代。保存机制没有重写优化框架。

正式代码预先规定：least_squares返回后先保存完整参数、fun、grad、active_mask、实际Jacobian、nfev/njev/status、耗时及时间节点等，再做几何诊断。但实际唯一求解在锁定74秒上限处抛出受控TimeoutError，**没有产生OptimizeResult**，所以不能提供实际nfev、njev、收敛状态、返回Jacobian或“最终最优参数”。Gate 1证明的是该保存路径的自测可靠性，不能当本次返回终态存在的证据。

实际异常留证：{calls}次残差调用，异常记录耗时{elapsed:.3f}秒；有限参数{len(abort['x'])}维。`EXCEPTION_LAST_FINITE_STATE.npz`与`LAST_FINITE_EVALUATION.npz`均能读取；`INTERRUPTED_STATE_BUNDLE.npz`补充解码后的32时刻26维状态、触点、原参考、原初始状态、边界和稀疏结构，未计算新的可行性结果，未覆盖原异常文件。完整现场见[solve.log](solve.log)、[FORMAL_EXCEPTION.json](FORMAL_EXCEPTION.json)。

正式优化前，输入预检曾发现24个速度／加速度权重无法匹配26维状态。本轮修正为原A2三个旋转分量各用既有同一权重，保留`POLICY_PRE_INPUT_REPAIR.json`、源码副本及失败日志；修正并通过输入门禁后才锁定并启动一次优化。这不是优化失败后的参数重试。

证据：[RESULT_PERSISTENCE_GATE.json](RESULT_PERSISTENCE_GATE.json)、[INPUT_CONTRACT_GATE.json](INPUT_CONTRACT_GATE.json)、[EVIDENCE_SUMMARY.json](EVIDENCE_SUMMARY.json)。

**STOP — HUMAN REVIEW**
''')
report('TEMPORAL_WRIST_FEASIBILITY.md',f'''
# 时变掌腕可行性

**NOT_FOUND_WITHIN_SCOPE：本轮未取得可核验的合法P3布局。唯一求解受控超时，只有标明身份的中间状态；未做候选Blender认证。**

正式MIDI重新解析并与C1表匹配R07–R14的channel、音高、velocity、NOTE_ON/OFF tick和时间；P3仅R09由3改1、R10由4改2，核心仍为E5(5)→C5(1)→D5(2)→E5(3)→F♯5(4)→G5(5)。未改正式数据，R07/R14仅承担连接边界。见[EVENT_CONTEXT.json](EVENT_CONTEXT.json)。

本次恢复原A2的时序支持、稀疏有界least_squares与分量PCHIP。控制时刻由原事件ON、35ms下沉、40ms释放跟随与必要180/75ms准备时刻派生；按原A2至少4ms支持点间隔规则避免重复节点。事前固定{K}个支持时刻、{len(P['evaluation_times_sec'])}个联合残差检查时刻，{len(abort['x'])}个变量。首尾完整26维状态固定为原C1实际状态；内部每个时刻一个六维共享掌腕＋五指20维姿态，共同一次求解，触点XY按六个事件共享。不是独立静态解拼接，也不是重新固定公共腕位。

掌腕平移／有限旋转作为各内部时刻的实际未知数，进入原速度、加速度、接触与全手姿态残差；中间留证的六维腕参数沿时间跨度为{np.round(rootspan,6).tolist()}（前三项mm、后三项度），相对唯一初始参数的最大根坐标变化为{rootchange:.6f}（混合工程坐标，仅用于证明参数实际参与，不是运动质量评分）。因此**时变掌腕参与这一点成立**，但这些数值不是最终合法轨迹。

使用原C1/A2较窄RSSF增量域：拇指弯曲0–25/25/18°、横展±35°；长指弯曲0–32/32/20°、横展±25°。掌腕采用原完整C1原指法派生范围，旋转X/Y±8°、Z±12°；没有用P3扩大域，没有固定8.70mm平移。参数全部采用同一合法域，五指共享真实根矩阵；保留中立手型和同刻C1先验。

接触使用冻结native FK/LBS真实权重的指腹顶点，沿原琴键Action在真实时刻的运动键面；原接触门槛横向≤0.03mm、垂向绝对间隙≤3mm未放宽。活动、持键、释放、准备与闲置指共同进入原A2任务模型；五指pad键体筛选和关节中心清障保留，未开发新指间避障引擎。准备／闲置指的真实全皮肤安全仍必须由候选Blender复核，不能由该有限代理认证。

输入阶段仅原C1读回187个准确时刻，Rig/native身份匹配；冻结LBS与完整真实皮肤最大误差{inp['full_native_LBS_parity_mm']:.6f}mm，控制点原指腹重建最大误差{inp['all_control_source_pad_reconstruction_error_mm']:.6f}mm。它证明输入模型正确，不是P3动作验证。

正式求解一次，max_nfev=35、内部74秒、外部85秒上限均事前锁定。实际内部超时，中间参数／残差完整保存；未返回迭代终态。中间加权总cost从{cost0:.3f}变为{costlast:.3f}，仅说明某次有限残差评估发生变化；不能从混合代价推断拇指C5、食指D5改善，更不能据此认定真实触键或自然手型合格。

R08持键428.571ms，下沉后最多393.571ms；R09–R12每音214.2855ms，R13持键428.571ms。R08→R09、R09→R10、R13→R14的OFF至ON均无额外休止。原180ms准备、75ms接近、40ms释放跟随和新增关节180°/s规则保留；速度／加速度连接在同次残差中考虑，但**没有合法最终布局端点可用来证明时间连接**。PCHIP内部可连续不代表触键安全，也没有检查候选跨边界的真实速度、皮肤和邻键。

按“终态不存在或无效即停止”执行：[BLENDER_VALIDATION_STATUS.json](BLENDER_VALIDATION_STATUS.json)记录候选验证未运行，未用初始化或中间状态补做P3认证。因此证据等级为：

| 等级 | 本轮状态 |
|---|---|
| STATIC_LAYOUT_VALID | UNKNOWN：无有效返回终态和候选真实skin检查 |
| TEMPORAL_CONNECTION_PLAUSIBLE | UNKNOWN：仅有事件及联合表示依据，没有合法连接证据 |
| CONTINUOUS_TRAJECTORY_VALIDATED | NOT_PERFORMED：未生成或认证完整连续演奏 |

原C1作为输入和风格参考，继承的B02碰撞及邻键WARN不被撤销。本轮没有可公平比较的P3真实候选，不能量化几何收益、把合同冲突归咎于指法或证明人体不可演奏。

**STOP — HUMAN REVIEW**
''')
report('FINAL_HUMAN_REVIEW.md',f'''
# Human最终审核

**HANDS_P3_TEMPORAL_WRIST_COORDINATION_R2 — NOT_FOUND_WITHIN_SCOPE。**

结果保存门禁通过，时变共享掌腕确实参与唯一正式求解；但锁定的74秒内部上限触发受控中止，没有返回优化终态。异常现场与最后有限参数完整留证。按任务规则停止候选Blender验证，不重跑、不增加节点、权重、范围或预算。

本状态表示**本轮未取得可核验的合法布局证据**，不是P3全局不可达或人体不可演奏，也不是一次完整优化终态的几何FAIL。

| 必答项 | 结论 |
|---|---|
| A：保存可靠／终态完整留存？ | **保存门禁PASS，实际异常留证PASS；OptimizeResult终态未产生。** 原始中间参数、残差、调用计数、耗时、traceback和解码状态均保存；nfev/njev及最终Jacobian未知，不虚构。 |
| B：时变掌腕真实参与？ | **YES。** 32个事件支持时刻，内部共享腕状态为独立未知数，与五指、PCHIP及时间残差联合；留证根参数沿时间变化且不同于原初始化。没有整段固定或8.70mm硬移。 |
| C：C5拇指／D5食指改善？ | **UNKNOWN。** 中间混合cost有变化，但没有最终真实指腹诊断，不能转换为两音接触收益。 |
| D：其余活动指接触与整手安全保留？ | **UNKNOWN。** 原事件、合法参数域与原资产保留；候选真实皮肤、黑白键、旁指和自然度没有验收，不能称安全保留。 |
| E：合法静态布局／合理时间连接？ | **未取得。** 有准确事件窗口及一次时序联合表示，没有合法终态端点和真实几何依据，前两级证据未通过，第三级未执行。 |
| F：失败主要原因？ | 可明确的是**该锁定求解配置在74秒内未返回**，R1导出实现错误已修复且本次异常保存奏效。时序控制、PCHIP耦合、稀疏有限差分导致实际{calls}次残差调用，是计算成本事实；指法、Rig触达、手位协调与约束可解性仍UNKNOWN，不能据此选出几何根因或宣布表示绝对失败。 |
| G：值得生成P3动态候选？ | **NO，当前不建议。** 没有合法触键、整手安全和时间连接证据，指法顺序收益不足以批准动态生成。 |
| H：停止P3、评估产品机制？ | **建议停止把P3作为继续追加同类布局优化的研发方向。** 保留P3为未验证的历史候选；不追加R3/R4。产品路线应回到整手运动表示与可复用动作机制的独立评估，先明确接触保持、释放／准备协同、Rig有效自由度、自然手型和计算成本，再由Human决定后续授权。没有证据直接要求复杂优化器，也不启动新机制开发。 |

本轮主要数值执行累计{core_total:.3f}秒；含报告闭合后的最终累计见[COMPUTE_LEDGER.json](COMPUTE_LEDGER.json)，上限180秒。一次正式优化，无第二seed／方案／重跑；首个输入预检的权重维度错误及修正前文件也计入账本、完整保留。内部74秒与外部85秒是事前分配，未因剩余总预算延长它们。

{len(before)}项关键引用源文件前后SHA一致；R1历史、原C1/A2/B3、正式MIDI与指法、冻结Rig/skin及琴键Action均未写。独立piano未访问，历史并发保护FAIL保留；所有新材料在本实验目录，没有路径迁移。新Action、Blend、视频及正式演奏动画均0。[PROTECTION_CHECK.json](PROTECTION_CHECK.json)。

三份报告与原始证据：[RESULT_PERSISTENCE_VALIDATION.md](RESULT_PERSISTENCE_VALIDATION.md)、[TEMPORAL_WRIST_FEASIBILITY.md](TEMPORAL_WRIST_FEASIBILITY.md)、[EXCEPTION_LAST_FINITE_STATE.npz](EXCEPTION_LAST_FINITE_STATE.npz)、[INTERRUPTED_STATE_BUNDLE.npz](INTERRUPTED_STATE_BUNDLE.npz)。本轮没有候选Blender诊断，只有原C1只读输入核对和明确的未运行状态记录，不能把它列成P3验证完成。

**HANDS_P3_TEMPORAL_WRIST_COORDINATION_R2**  
**NOT_FOUND_WITHIN_SCOPE**  
**STOP — HUMAN REVIEW**

等待ChatGPT独立审核和Human授权。停止P3同类优化追加；不修改正式指法、不生成动画、不测试其他MIDI、不进入产品生产。
''')
atomic_json('FINAL_STATUS.json',dict(task='HANDS_P3_TEMPORAL_WRIST_COORDINATION_R2',status='NOT_FOUND_WITHIN_SCOPE',RESULT_PERSISTENCE_GATE='PASS',valid_final_optimizer_result=False,controlled_timeout=True,intermediate_state_saved=True,formal_optimizer_calls=1,optimizer_retries=0,candidate_blender_validated=False,STATIC_LAYOUT_VALID='UNKNOWN',TEMPORAL_CONNECTION_PLAUSIBLE='UNKNOWN',CONTINUOUS_TRAJECTORY_VALIDATED='NOT_PERFORMED',P3_dynamic_generation_recommended=False,further_similar_P3_optimization_recommended=False,new_framework_required='UNKNOWN',global_unreachability_claim=False,new_actions=0,new_blends=0,new_videos=0,next_stage_started=False,stop='STOP — HUMAN REVIEW'))
print('REPORTS_COMPLETE',info);print('PROTECTED_SOURCES_UNCHANGED',len(before));print('STOP — HUMAN REVIEW')
