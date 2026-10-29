import sys,json,hashlib,ast,math
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O));from rig_model import np,PchipInterpolator
read=lambda n:json.loads((O/n).read_text(encoding='utf-8-sig'))
def save(n,d):(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def md(n,s):(O/n).write_text(s.strip()+'\n',encoding='utf8')
I=read('EXPERIMENT_INPUT.json');P=read('POLICY_LOCK.json');runs=[read('runs/'+f.name) for f in sorted((O/'runs').glob('*.json')) if not f.stem.endswith('_actual')];j=read('runs/junction_2_actual.json');h=read('runs/hold_corrected_actual.json');p2=read('runs/hold_1_actual.json');samples=read('LOCAL_PATH_ACTUAL_SAMPLES.json');trajectory=read('LOCAL_CONTROL_TRAJECTORY.json');times=np.array([r['display_time'] for r in samples]);w=np.array([r['wrist_world_m'] for r in samples])*1000;q=np.array([r['anatomy']['recovered_controls'] for r in samples]);dt=np.diff(times);v=np.diff(w,axis=0)/dt[:,None];tv=(times[:-1]+times[1:])/2;acc=np.diff(v,axis=0)/np.diff(tv)[:,None];qv=np.diff(q,axis=0)/dt[:,None,None];fails=[r for r in samples if not r['all_gates']];budget=sum(r['elapsed_seconds'] for r in runs)+35
budgetdata=dict(completed_solve_count=len(runs),interrupted_solve_count=1,completed_seconds=sum(r['elapsed_seconds'] for r in runs),interrupted_conservative_charge_seconds=35,total_conservative_seconds=budget,limit_seconds=600,under_budget=budget<=600,verification_and_file_IO_excluded=True,runs=[dict(id=r['id'],seconds=r['elapsed_seconds'],convergence=r['convergence']) for r in runs]);save('SOLVE_BUDGET.json',budgetdata)
joint=dict(status='STATIC_JUNCTION_COMPATIBLE',authority='DESIGN_PROVISIONAL',boundary_contract='BOUNDARY_CONTRACT_PASS',attempt_count=2,attempts=[dict(numerical=read(f'runs/junction_{n}.json'),actual=read(f'runs/junction_{n}_actual.json')) for n in (1,2)],comparison=dict(previous_P2_P3_wrist_distance_mm=67.8053011329,P2_to_common_boundary_wrist_distance_mm=float(np.linalg.norm((np.array(j['wrist_world_m'])-p2['wrist_world_m'])*1000)),not_minimum_required_distance=True),Human_naturalness='PENDING',active_bounds=['root control yaw -12deg','thumb third flex near0deg'],scope='Static common configuration only; not reached by a validated path from B2/P2');save('JUNCTION_STATIC_FEASIBILITY.json',joint)
holdrows=[]
for name in ['hold_1','hold_2','hold_3','hold_4','hold_5','hold_corrected']:
 r=read('runs/'+name+'.json');a=read('runs/'+name+'_actual.json');holdrows.append(dict(numerical=r,actual=a,wrist_delta_from_P2_mm=((np.array(a['wrist_world_m'])-p2['wrist_world_m'])*1000).tolist(),wrist_distance_from_P2_mm=float(np.linalg.norm((np.array(a['wrist_world_m'])-p2['wrist_world_m'])*1000)),identical_P2_latent=bool(np.array_equal(r['latent'],I['seeds']['P2']['latent']))))
hold=dict(status='DISCRETE_HOLD_ADVANCE_FOUND_CONTINUOUS_EXTENSION_NOT_PROVEN',HOLD_CONTINUATION_FEASIBLE='NOT_ESTABLISHED_AS_CONTINUOUS_PATH',authority='DESIGN_PROVISIONAL',meaningful_new_discrete_nodes=1,completed_duplicate_nodes=5,interrupted_record=read('HOLD_STAGNATION_RECORD.json'),rows=holdrows,P2_next_pad_surface_distance_mm=p2['next_pad_distance_to_playable_surface_mm'],corrected_next_pad_surface_distance_mm=h['next_pad_distance_to_playable_surface_mm'],corrected_wrist_advance_mm=holdrows[-1]['wrist_distance_from_P2_mm'],corrected_convergence=False,maximum_reachable_preparation='NOT_ESTABLISHED',connection_B2_P2_corrected_junction='UNVALIDATED',metric_definition='Euclidean distance of existing middle pad reference point to nearest playable key patch, not exact pulp distance or legacy center target error',objective_metadata_correction='hold_corrected uses bounded pose_target predictor projection, as executable objective and goal record show; generic objective description in raw run is stale',failure_analysis='Old distance objective exhausted budget and retained P2; no-progress guard was missing, so five identical outputs occurred before interruption. One bounded predictor correction made a real but small advance. No retry beyond that.');save('G4_HOLD_CONTINUATION.json',hold)
failrows=[]
for r in fails:
 failrows.append(dict(time=r['display_time'],failed_gates=[k for k,val in r['gates'].items() if not val],target_depth_mm=r['target_max_depth_mm'],non_target_or_wrong_region_mm=r['non_target_or_wrong_region_max_mm'],contacts=[dict(midi=c['midi'],strict_crossing_faces=c['strict_crossing_faces'],contact_gate=c['contact_gate'],metrics=c['geometry']['contact']) for c in r['contact_results']]))
path=dict(status='CONTINUOUS_PATH_NOT_PROVEN',authority='DESIGN_PROVISIONAL',candidate_count=1,interval=trajectory['plan']['interval'],duration_seconds=float(times[-1]-times[0]),boundary=I['junction_time'],knots=read('LOCAL_PATH_KNOT_INDEX.json'),trajectory_file='LOCAL_CONTROL_TRAJECTORY.json',actual_samples_file='LOCAL_PATH_ACTUAL_SAMPLES.json',sample_count=len(samples),base_rate_hz=120,maximum_sample_gap_seconds=float(dt.max()),sampling=trajectory['adaptive_reason'],failed_sample_count=len(fails),failed_samples=failrows,maximum_target_depth_mm=max(r['target_max_depth_mm'] for r in samples),maximum_non_target_or_wrong_region_mm=max(r['non_target_or_wrong_region_max_mm'] for r in samples),maximum_self_crossings=max(r['self_crossings'] for r in samples),minimum_middle_ring_exact_gap_mm=min(r['middle_ring_exact']['distance_mm'] for r in samples),all_joint_reference_and_axes_pass=all(r['gates']['natural_family'] and r['gates']['authorized_axes'] and r['gates']['authorized_domain'] for r in samples),kinematics=dict(method='Secants of actual Blender wrist world coordinates and recovered engineering joint controls on irregular sample times; accelerations are differences of consecutive secant velocities at midpoint times. Estimates, not clinical limits or analytic maxima.',wrist_segment_peak_speed_mm_s=float(np.linalg.norm(v,axis=1).max()),wrist_midpoint_peak_acceleration_mm_s2=float(np.linalg.norm(acc,axis=1).max()),maximum_joint_control_secant_deg_s=float(abs(qv).max()),segment_velocities_mm_s=v.tolist(),velocity_midpoint_times=tv.tolist(),accelerations_mm_s2=acc.tolist(),joint_control_velocities_deg_s=qv.tolist(),joint_control_order='five digits x flex1,flex2,flex3,spread; engineering mapped axes, not clinical Euler angles'),position_and_first_parameter_derivative_continuous=True,second_derivative_continuity=False,naturalness='HUMAN_PENDING; geometric failure already rejects candidate',not_B2_to_junction=True,not_P4_at_ON_plus35ms=True,no_Action_video=True,root_cause_direct_evidence='Feasible knot controls interpolated in Euclidean latent coordinates leave nonlinear contact/obstacle constraint sets between knots; actual geometry rejects them.',unexcluded='Contact-manifold continuation with tangent constraints and between-node correction, alternative surface witness charts, multi-frame constrained local planning',no_more_solves=True);save('LOCAL_PATH_FEASIBILITY.json',path)
protected=read('PROTECTED_FILES_BEFORE.json');changed=[];missing=[]
for file,expected in protected.items():
 f=Path(file)
 if not f.exists():missing.append(file)
 elif hashlib.sha256(f.read_bytes()).hexdigest()!=expected:changed.append(file)
save('PROTECTED_FILES_AFTER.json',dict(status='PASS' if not changed and not missing else 'FAIL_CLOSED',checked_files=len(protected),changed=changed,missing=missing,source_manifest='PROTECTED_FILES_BEFORE.json',all_original_key_Action_payloads_match=True,all_evaluated_native_Rig_identities_match=True));assert not changed and not missing
P['no_more_solves']=True;P['termination']='CONTINUOUS_PATH_NOT_PROVEN — STOP HUMAN REVIEW';save('POLICY_LOCK.json',P)
md('JUNCTION_CONTACT_SEMANTICS.md',f'''# 换音边界接触语义

结论：BOUNDARY_CONTRACT_PASS。DESIGN_PROVISIONAL。

本轮只读复用上一轮 CONTACT_STATE_SEQUENCE.json 的90阶段合同、C01指法及实际琴键Action。展示时间=音乐时间+0.35秒。B2=2.527855，P2=2.720000，换音J=2.921426，P4=2.956426秒。原事件未改。

G4在J左侧必须保持真实指腹接触；E5从J右侧进入PRESS，按既有合同从初始键面开始接触。手的构型连续，键面位置连续，因此闭合几何接触集合的左右极限需要在J存在共同构型。本轮验证的是G4仍下压、E5仍在起始高度的两个几何接触，不是两键同时深按，也未强制两接触贯穿后续换位。

实际Blender求值：J处G4转角0.0871232077479rad，E5为0；E5在ON后35ms完成下压，G4按原70ms回弹。源Action负载哈希与上一轮一致，见BOUNDARY_SOURCE_VERIFICATION.json及BOUNDARY_KEY_STATES.npz。浮点时间保留原值2.9214260000000003，边界判断使用1e-9秒识别同一事件，不改音乐时间。

MIDI ON/OFF、几何接触、机械键位是三层合同；按压力、击弦机构及声学起音未建模。PRE_TOUCH只允许在静止键面几何预接触，不据此宣称提前声音或主动按压。

接触验收沿用真实指腹三角面裁剪/跨面布尔、投影面积与原pad区域辅助条件；保留原始悬空和越界值。pad参考点离面并不等于完整指腹离面，不能用点距离取代真实接触。共同边界#1真实跨面存在，但E5 pad越界0.000126653mm超过1e-5mm，仍判失败；#2将数值pad内边距收紧至0.01mm后通过，未放宽验收。

## 数值表示与独立验收

12维控制：掌根平移3、旋转3、拇指4、批准长指参考族λ与中指屈曲插值α。控制范围及轴映射来自前轮，不把工程角直接当临床活动角。λ/α混合保持长指spread参考族与PIP/DIP屈曲轴；这不等于Human认可全部姿态。

SLSQP显式等式为已有面级材料见证点相对实际键面的法向位置（目标-0.005mm）；不等式为可触区域、pad辅助范围、全部键体三角面内部深度≤0.20mm及局部近面分离轴。三角面深度由候选过滤后几何计算，非光滑最大值仍存在；自碰撞近面轴在单次求解初值建立，不是全局碰撞证明。有限差分雅可比0.001mm/度、λ/α为0.0001。自然度采用既有参考族，未新增臆造角限。

独立Blender验收重算实际deformed mesh、全部88键0.25mm门禁、所有非相邻指面相交、真实指腹跨面及关节轴。多接触目标从非目标集合排除，但各目标错误区域深度仍单独计入。中指/无名指使用完整非相邻三角对AABB下界过滤、点面及全部边边精确特征距离；不是顶点抽样。未更换该距离算法，不能将本轮几毫米间隙与旧S2的0.1177mm视作算法精度变化。
''')
md('CROSS_EVENT_REUSE_CHECK.md','''# 跨事件规则回归

RULE_REUSE_PASS；实际执行结果见BOUNDARY_REUSE_TESTS.json，代码boundary_rules.py。

|结构|展示时间|左右接触并集结果|
|---|---:|---|
|本次R07→R08|2.921426|拇指G4与中指E5共2项|
|同指重复R06→R07|2.492855|相同手/手指/键去重为1项|
|左手和弦起音|0.350000|从0项到L00/L01/L02共3项|
|左手和弦持键内部|0.700000|左右3项去重为3项|

边界函数按原合同事件时间及(hand,finger,midi)组合工作，无G4/E5或R07/R08分支。contact_solver.py按传入contacts和实际88键角构造约束，未写死该换音身份。实验驱动的时间窗与12维参考族特意属于本次试验；共享rig_model.py中保留的旧端点常量不是新约束分支，但说明当前封装尚未成为任意MIDI产品接口。

以上是实际规则级回归，不是左手几何/运动通过，也不能证明同指重复音的再次激发或声学起音。多接触数值约束能接收列表；本轮只实际求解了右手两接触，和弦求解成本未验证。Mink未在本轮再次调用或安装；上一轮已执行对照证据只读引用，未包装为本轮路径PASS。
''')
md('PRODUCT_ROUTE_REVIEW.md',f'''# 技术路线与产品化复盘

建议B：保留冻结FK/蒙皮、真实几何验收及SLSQP静态后端，对接触约束运动规划做一次同输入实际对照。现有独立可行节点加普通PCHIP插值不足以生成合格路径；本轮不重新推翻已验证的静态求解能力，也不宣称Mink优于SLSQP。

已解决的问题：共同边界确实存在。旧P2/P3腕部距离67.805mm是独立候选差异；本轮共同边界与P2只有{joint['comparison']['P2_to_common_boundary_wrist_distance_mm']:.6f}mm，且同时满足真实G4/E5接触。该数值不是最短路径，也未证明从B2可达。

尚未解决的问题：保持接触的可行集合曲率与键面随时间运动，需要在节点之间持续约束。四个局部下压节点收敛且全部通过；同一C1控制路径24个实际样本中{len(fails)}个失败，直接显示节点可行性不能由插值继承。中间节点虽保持参考手型，仍有目标/错误区域侵入及接触失效。单纯更换点IK求解器不能自动补上这一接口。

持键延拓也暴露计算策略问题：自由指距离目标最小化多次耗尽35秒，只保留原P2。驱动缺少无进展停止条件，导致5次重复，发现后中断第6次并保留证据。最后唯一有依据的小步预测+约束修正得到{hold['corrected_wrist_advance_mm']:.6f}mm实际腕移，但仍为预算终止，且没有验证P2到该点的连续接触。不能把这些重复结果当5个延拓节点，更不能声称最远准备能力已确定。

新增数值求解累计{budget:.3f}秒（{budget/60:.3f}分钟），包含中断运行保守计35秒；12次完成输出加1次中断，2次边界联合求解、7次持键求解启动、4次局部节点求解，只有1条路径候选。真实几何验收与文件处理另计。25ms局部片段尚且失败，当前成本与成功率不足以支持整首MIDI自动生产；本轮不是可扩展性基准测试。

可复用：事件接触并集、面级见证、原Action求值、完整几何验收。仍专用：本例参考族、材料面选择、节点间隔、固定局部自碰撞轴及小步预测比例。临床角限、舒适速度或演奏自然度没有新临床证据，不作阈值结论。

下一项唯一关键验证：在同一冻结Rig、同一25ms时间窗和同一初始共同构型上，实际比较具有接触切向约束及节点间几何修正的局部路径方法，保持0.25mm与真实接触门禁。需输出时间参数化路径，再独立采样；不得仅比较孤立IK点。可以复用已适配Mink作为后端，但其接触运动规划能力仍需实际证据。当前未排除其他见证面选择、流形延拓或局部多时刻约束方法。

不登记为已证实的指法/人体冲突：FINGERING_MOTION_FEEDBACK_REQUIRED本轮未触发强结论。共同构型存在，失败发生在数值路径表示，不能据此断言C01指法错误或人体不能演奏。若未来可靠规划仍持续发生关节/接触冲突，再反馈上游。

所有结果DESIGN_PROVISIONAL。STOP — HUMAN REVIEW。
''')
md('FINAL_RECOMMENDATION.md',f'''# 最终决定

**建议B：接触状态合同成立，但本轮局部延拓与节点间路径表示不足，需要成熟接触约束运动规划方法的同输入实际对照。** 保留现有FK、蒙皮、真实几何验收与SLSQP静态求解；本轮未证明其他后端更好。

|门禁|结论|
|---|---|
|BOUNDARY_CONTRACT_PASS|通过，原MIDI/Action一致|
|STATIC_JUNCTION_COMPATIBLE|通过，第2次共同构型真实验收合格|
|HOLD_CONTINUATION_FEASIBLE|连续意义尚未成立；仅找到1个有小幅实际提前换位的离散新点|
|CONTINUOUS_PATH_NOT_PROVEN|成立，唯一局部连续候选采样失败|
|LOCAL_PATH_SAMPLED_PASS_HUMAN_PENDING|不授予|

共同边界：两指真实接触，目标最大侵入{j['target_max_depth_mm']:.9f}mm，非目标/错误区域{j['non_target_or_wrong_region_max_mm']:.9f}mm，非相邻指面交叉0，中指/无名指精确间隙{j['middle_ring_exact']['distance_mm']:.6f}mm。SLSQP第2次收敛；第1次E5 pad微小越界失败原样保留。掌根yaw和拇指末节控制接近边界，Human自然度仍待审，计算参考族通过不能替代视觉认可。

提前换位：纠正后的新离散点相对P2腕移{hold['corrected_wrist_advance_mm']:.6f}mm；中指pad到E5可触面距离从{hold['P2_next_pad_surface_distance_mm']:.6f}降到{hold['corrected_next_pad_surface_distance_mm']:.6f}mm。真实几何通过，但求解预算终止、非收敛。最远准备位置及与B2的连续可达性未确定。

唯一局部路径：2.913092667–2.938092667秒，25ms；在共同构型附近起步，未连接B2/P2。四个后续节点都收敛并通过；120Hz基础采样加风险区补采样共24个时刻，{len(fails)}个失败。目标侵入最大{path['maximum_target_depth_mm']:.9f}mm，非目标/错误区域最大{path['maximum_non_target_or_wrong_region_mm']:.9f}mm；部分时刻指腹真实跨面为0，其他时刻pad超出原可触区域。失败时间与原始布尔详见LOCAL_PATH_FEASIBILITY.json和LOCAL_PATH_ACTUAL_SAMPLES.json。

实际腕部采样段峰值速度约{path['kinematics']['wrist_segment_peak_speed_mm_s']:.3f}mm/s，差分加速度约{path['kinematics']['wrist_midpoint_peak_acceleration_mm_s2']:.3f}mm/s²；工程关节控制最大差分速度{path['kinematics']['maximum_joint_control_secant_deg_s']:.3f}度/s。这些是短窗、不规则采样估计，非临床舒适阈值；参数C1连续但不保证加速度连续或自然运动。中指/无名指样本最小精确间隙{path['minimum_middle_ring_exact_gap_mm']:.6f}mm且指面交叉0，不能覆盖其他门禁失败或证明连续时间绝对安全。

数值求解保守总墙钟{budget:.3f}秒，低于600秒。持键驱动曾遗漏无进展停止，产生5个原P2重复结果，已记录并停止；没有把它们计为新可行路径点。全部{len(protected)}个保护文件复核一致，冻结Rig和原琴键Action身份一致。未生成正式Action、Blend、视频或静帧。

本轮是实际求解与实际Blender验收，另含规则级跨事件回归；没有新增外部IK实验。最终仅证明共同静态边界兼容，不证明整段G4→E5、E5 ON后35ms完成、入口R06→R07或其他曲目运动。

**DESIGN_PROVISIONAL — STOP — HUMAN REVIEW。** 不自动开始下一实验或正式教学动画。
''')
# Independent artifact checks: syntax only, no rerunning solvers.
for f in O.glob('*.py'):ast.parse(f.read_text(encoding='utf-8-sig'))
for f in O.glob('*.json'):json.loads(f.read_text(encoding='utf-8-sig'))
required=['JUNCTION_CONTACT_SEMANTICS.md','JUNCTION_STATIC_FEASIBILITY.json','G4_HOLD_CONTINUATION.json','LOCAL_PATH_FEASIBILITY.json','CROSS_EVENT_REUSE_CHECK.md','PRODUCT_ROUTE_REVIEW.md','FINAL_RECOMMENDATION.md'];assert all((O/n).stat().st_size>0 for n in required)
save('DELIVERY_VALIDATION.json',dict(required_deliverables=required,all_present=True,python_parse_pass=True,json_parse_pass=True,protection_pass=True,no_more_solves=True,decision='B',authority='DESIGN_PROVISIONAL'))
print(json.dumps(dict(failed_samples=len(fails),samples=len(samples),budget=budget,min_gap=path['minimum_middle_ring_exact_gap_mm'],kinematics={k:v for k,v in path['kinematics'].items() if k in ['wrist_segment_peak_speed_mm_s','wrist_midpoint_peak_acceleration_mm_s2','maximum_joint_control_secant_deg_s']},protected=len(protected)),indent=2))
