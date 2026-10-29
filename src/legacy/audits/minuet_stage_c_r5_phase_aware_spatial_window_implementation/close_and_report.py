"""Close failed pre-generation gate; write evidence reports, never solve."""
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent;ROOT=P.parents[1];R3=ROOT/'audits/minuet_stage_c_r3_right_hand_local_spatial_clearance';C1=ROOT/'audits/minuet_stage_c_r1_dual_hand_synchronized_performance'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def dump(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
def doc(n,s):(P/n).write_text(s.strip()+'\n',encoding='utf8')
policy=read(P/'PRECHECK_POLICY.json');role=read(P/'EVENT_ROLE_VALIDATION.json');data=read(P/'EXACT_BOUNDARY_GEOMETRY.json');assert data['gate']=='FAIL' and role['pass_']
violations=[dict(window=r['window'],edge=r['edge'],video_sec=r['video_sec'],**h) for r in data['samples'] for h in r['hits'] if h['hard_violation']]
assert violations
dump('PREGENERATION_GATE.json',dict(status='FAIL_CLOSED',reason='IMMUTABLE_BOUNDARY_NON_TARGET_KEY_PENETRATION',proof='Boundary equality q=q_source, root=root_source and unchanged key geometry/clock uniquely preserve source skin; measured non-target penetration exceeds 0.5mm at all four endpoints. Even excluding the exact endpoint cannot repair the immediate interior continuously.',boundary_violations=violations,roles_pass=True,spatial_kernel='PARTIAL_ACTUAL_GEOMETRY_BOUNDARY_QUERY',feasibility_solver='NOT_IMPLEMENTED_STOPPED_AT_BOUNDARY_GATE',formal_dynamic_solve_attempts=0,new_static_solves=0,nfev=0,major_iterations=0,optimizer_status='NOT_STARTED_GATE_BLOCKED',dynamic_candidate_count=0,backend_method='NOT_LOCKED_NOT_RUN',backend_function_evaluation_limit='NOT_LOCKED_NOT_RUN',authorized_budget_only=dict(max_major_iterations=200,max_wall_seconds=1800),new_blend='NOT_RUN',new_action='NOT_RUN',new_video='NOT_RUN',root_expansion=False,window_expansion=False,tolerance_relaxation=False,script_hashes={n:sha(P/n) for n in ['event_phase_plan.py','local_spatial_constraints.py','precheck_setup.py','boundary_readonly.py']},stop='STOP — HUMAN REVIEW'))
table='| 窗口边界 | 演示 / 音乐 s | 手指 / 非目标键 | 内部采样深度 mm | 硬约束裕量 mm |\n|---|---|---|---:|---:|\n'
for r in violations:table+=f"| {r['window']+1} {r['edge']} | {r['video_sec']:.6f} / {r['video_sec']-.35:.6f} | {r['digit']} / {r['note']} | {r['max_internal_depth_mm']:.6f} | {r['slack_mm']:.6f} |\n"
contacts='| 边界演示 s | 活动音 / 手指 | 实际skin gap mm | 横向越界 mm |\n|---|---|---:|---:|\n'
for r in data['samples']:
 for c in r['contacts']:contacts+=f"| {r['video_sec']:.6f} | {c['note']} / {c['finger']} | {c['gap_mm']:.6f} | {c['horizontal_mm']:.6f} |\n"
summary=read(R3/'R1_BLACK_SUMMARY.json');windows=policy['windows_video_sec'];outside=[];inside=[]
for s in summary:
 for a,b in s['intervals']:
  for lo,hi in windows:
   if max(a,lo)<=min(b,hi):inside.append(dict(digit=s['digit'],note=s['note'],interval=[max(a,lo),min(b,hi)]))
  fragments=[[a,b]]
  for lo,hi in windows:
   cut=[]
   for x,y in fragments:
    if y<lo or x>hi:cut.append([x,y])
    else:
     if x<lo:cut.append([x,lo])
     if y>hi:cut.append([hi,y])
   fragments=cut
  for interval in fragments:outside.append(dict(digit=s['digit'],note=s['note'],interval=interval,depth_scope='Episode max not assigned to clipped interval; use historical original records'))
dump('KNOWN_CONFLICT_SCOPE.json',dict(source=str(R3/'R1_BLACK_SUMMARY.json'),method='Interval intersection/difference on saved R3 60Hz reports; no new full-time geometry search',inside_windows=inside,outside_windows=outside,note='Closed interval notation is descriptive; exact endpoints reported separately. No problems repaired because no new motion.'))
outtable='| 手指 / 键 | 窗口外已知R3采样区间（演示秒） |\n|---|---|\n'
for d,k in sorted({(r['digit'],r['note']) for r in outside}):
 outtable+=f'| {d} / {k} | '+'；'.join(f"{r['interval'][0]:.6f}–{r['interval'][1]:.6f}" for r in outside if (r['digit'],r['note'])==(d,k))+' |\n'
doc('EVENT_PHASE_ROLE_PLAN.md','''# 全五指事件角色计划

已新增可运行的 event_phase_plan.py。输入只用原右手事件、既定指法和时间信息，输出全五指独立叠加的任务包络、相邻指共享关系及机械回弹上下文；无音名/3.825秒特殊姿态分支，不生成关节轨迹。

ACTIVE_CONTACT只在原NOTE_ON/OFF内要求原活动键；PREPARING从下一音前180 ms渐入，不获得接触豁免；RELEASING在NOTE_OFF后40 ms衰减，属于卸载偏好而非旧键必须持住；EXITING在NOTE_OFF后120 ms内提供渐入/渐出的单侧离开关系描述，不强制旧键面等式/整指floor；IDLE补足低任务参与部分，交给原动作风格与共同空间约束，不指定固定中性姿态。40/120/180 ms是本次有限角色接口政策，不是普适演奏学结论，也未经新动态验证。

各角色采用独立条件生成，释放、退出和下一音准备可同时存在，不用互斥elif选唯一目标。当前只落实任务语义与连续偏好包络；阶段角色与NOTE_ON/OFF接触身份会在真实事件处切换，其动作连续性仍需未来轨迹约束，不能由包络平滑直接声称已通过。

3.825秒：中指E5 ACTIVE_CONTACT；无名指F♯5 PREPARING，旧D5只有EXITING（无持键等式/无接触许可）；D5的机械回弹仍列为环境上下文，其实际角度权威是原键Action，未重新生成键运动。机械回弹70 ms不等于手指必须保持接触70 ms。

早段1.108–1.192秒：食指A4活动、中指B4准备、无名指暂IDLE；1.25秒无名指已准备C5。共享计划包含五指与四组相邻关系，但不是已经实现的交接通道优化。

EVENT_ROLE_VALIDATION.json保留16音符完整阶段区间与九个语义样本。验证包括：E5活动、F♯5准备、D5不再被错误延长为持键，D5机械上下文不丢失；仅活动目标+验证pad顶点可获得接触许可，准备指、非目标键、pad外顶点全部拒绝；全事件时间平移7秒、音高移调−12后角色关系保持。测试无静态或动态求解。

角色模块IMPLEMENTED；总体跨指角色/空间冲突PARTIAL。旧D5强制持键冲突已在任务接口消除，实际手指相交没有被修复。
''')
doc('LOCAL_SPATIAL_CONSTRAINT_DESIGN.md','''# 局部真实skin空间约束：当前完成范围

LOCAL_SPATIAL_CONSTRAINTS = PARTIAL。新增local_spatial_constraints.py实现实际评估skin对真实凸键体的内部采样深度、BVH面交叉和硬裕量输出，已用于四个原源边界。不是完整连续轨迹约束，更不是把R4最近顶点法向残差包装成新求解器。

键体内部由实际键面向外平面确定，先验证键顶点满足凸体条件；内部顶点距离与最近实际键面点均保留，超过0.5 mm即负裕量/硬阻断。开放手指patch仅作为真实表面参与BVH，不用其法向推断全局inside/outside。零内部顶点而有面交叉不会成为净空证书。

复用：C1冻结场景、R3四指远端ROI、原皮肤评估、真实运动键体与接触评价器。只检查四个端点、四个已有局部patch与七个既知黑键。无全88键/全时段逐顶点查询，无运动参数修改。

接触许可接口在事件模块中已实现：原活动时间、相同目标键且属于调用方提供的经验证pad区域才允许；默认空区域全部拒绝。没有将整指、准备指或非目标键豁免。当前边界没有活动黑键，因此这些可信非目标黑键证据根本不需要触键豁免。自动pad区域提取、五指完整保护和运动求解集成尚未实施，不能把接口测试说成全五指skin覆盖认证。

未完成项因边界硬失败停止：相邻三组手指的稳定连续分离约束、必要白键闭体查询、拇指保护区域集成、角色条件化自然先验与20关节联合轨迹。凸体接口拒绝不满足凸性的键形，不能用于冒充非凸白键通用检查。

目标接触候选阈值绝对gap≤2.1 mm、横向≤0.5 mm；非目标键可信内部穿入>0.5 mm硬阻断。≤0.5 mm也必须另核实正常视角不可见、孤立且不影响接触才可WARN。本轮未得到候选、未应用浅层WARN豁免。冻结工程域不改，root完全保留。
''')
doc('WINDOW_BOUNDARY_FEASIBILITY.md',f'''# 窗口边界：FAIL，0候选停止

唯一源C1 SHA256 `{policy['source_sha256']}`。窗口严格固定0.778571–2.134284与2.741426–4.705710演示秒，音乐时钟减0.35秒；未扩窗。

{table}

四个端点均存在目标检查范围内的非目标黑键可信内部穿入，全部高于0.5 mm。检查在原Blender场景的精确浮点时间进行，不用60Hz邻近样本代替端点。世界坐标、原顶点编号、真实键面最近点、面交叉数、内部顶点数与硬裕量见EXACT_BOUNDARY_GEOMETRY.json。

**不相容证明**：边界要求关节/位置与原源相同，root、冻结skin和键时钟也相同，故边界实际skin必与原源相同；同一点既必须保留2.602 mm等穿入，又必须满足≤0.5 mm，条件矛盾。位置连续已经不可能满足全部硬约束，无需再求解一阶连续条件。即使从检验集合删掉精确端点，连续运动在端点附近仍保留超过阈值的穿入，不能借此规避。

不是原Rig全局不可行证明，也不是固定root在其他事件范围无解的证明。只是本轮授权窗口、边界保持与安全门槛无法同时满足。依据用户第5/15节，立即FAIL_CLOSED，不扩大窗口、不删除相关键、不允许边界豁免、不调容差。

预检已锁：源、两窗口、root固定、边界等值要求、0.5 mm门槛及有限读取范围。完整动态方法/初始化/变量增量/后端函数评估上限尚未进入锁定阶段，明确NOT_LOCKED_NOT_RUN；不能把授权的200主迭代/30分钟预算冒充已配置可执行求解器。真实优化器nfev=0，主要迭代=0，终止为NOT_STARTED_GATE_BLOCKED。
''')
doc('IMPLEMENTATION_REPORT.md','''# 实际实施与停止记录

新增非冻结目录内文件：
- event_phase_plan.py：全五指重叠角色包络、共享相邻关系、活动pad许可接口；IMPLEMENTED，纯事件测试通过。
- local_spatial_constraints.py：实际凸键体/局部skin面相交与硬裕量查询；PARTIAL，已用于原源端点。
- precheck_setup.py：源保护、角色验证、预检政策。
- boundary_readonly.py：只读原C1精确四端点实际几何与活动接触。
- close_and_report.py：锁定失败原因、拆分既有冲突范围、写报告和核验哈希。

没有创建或宣称实现window_trajectory_solver.py；FEASIBILITY_FIRST_SOLVER=NOT_IMPLEMENTED。发现边界数学不相容后，按止损条款停止运动开发与生成。硬边界诊断门禁不是受限轨迹求解器，不能混为IMPLEMENTED。

复用代码只读：R3几何读取/实际网格与接触工具、R2底层Blender读取、原performance_core键表与指法/FK元数据；这些历史文件没有修改。只加载R3定义前缀，不执行其全时段扫描主体。未导入/调用R4或root实验优化器。

本轮新静态优化0、正式动态求解0、nfev0、主迭代0、动态候选0、Action0、Blend0、视频0。Blender仅打开原源、设置四个读取时间，没有改pose、插帧或保存。失败终止记录位于PREGENERATION_GATE.json。

没有为某音高/某时刻定义姿态；测试中3.825秒和移调输入只验证语义。项目目录和两授权窗口/0.35秒音乐前导属于外部任务配置，不是角度补丁。EXITING等只输出任务描述，尚未成为可运行轨迹约束，复用能力不夸大。

成功候选才需要的HUMAN_REVIEW.html、新双手Blend、三视角原速视频、同期对照一律NOT_RUN。无旧视频冒充新候选。
''')
doc('SPATIAL_AND_CONTACT_VALIDATION.md',f'''# 验证范围与未修复问题

早段邻指修复NOT_RUN；晚段邻指修复NOT_RUN；黑键修复NOT_RUN。没有新轨迹，已修复窗口内问题数量为0。原R3/C4/root研究的几何问题仍全部保留，不能将角色接口正确宣称为实际空间改善。

新增验证仅四个不可改变端点的真实局部几何：

{table}

端点原源活动skin接触：

{contacts}

源动作/时序完全未改，因此活动接触功能按原记录保持；这四个样本也不能认证一个不存在的新候选的全音符接触。原23音符音乐及同步链未重新生成或全量重测。

窗口内：继承早段与3.729–3.867秒中指/无名指相交，以及R3所列食指G♯4/A♯4/C♯5、中指C♯5/D♯5、无名指C♯5/D♯5干涉；细分区间来自原R3保存数据，见KNOWN_CONFLICT_SCOPE.json。不重复全窗口几何扫描。

窗口外及两窗间保留问题：

{outtable}

这些区间由原60Hz诊断范围与授权窗口作交/差运算，端点开放/闭合仅为显示记法；精确端点以上述新读取为准。不能把某个历史episode的最大深度赋给切分后的每一段。两窗口之间食指/A♯4和无名指/C♯5已有持续干涉，片头/尾也有问题，不能称完整4小节已清除空间缺陷。

正常教学视角已确认的邻指穿插与部分穿键仍是产品风险；本轮没有新原速演奏可评估哪些窗口外问题最终可被Human接受。不隐去这些问题，也不扩求解范围。SOURCE问题、边界硬失败、新候选NOT_RUN三者分别记录。
''')
doc('MOTION_PRESERVATION.md','''# 已批准动作保持

唯一运动源为原Stage C R1，不继承R2−6°修正。原right root、左手Stage B R3、全部右手关节轨迹（含窗口内外）、琴键Action、原MIDI/指法/0.35秒前导/音频均未改变。真实改变的动作时间段为空，真实改变的骨骼为空。

RIGHT_HAND_MOTION_PRESERVATION=PASS指原动作字节与源文件保持，并非证明新修复自然度。ACTIVE_CONTACT_PRESERVED与DUAL_HAND_MUSIC_FUNCTION的PASS同样指原功能保持；没有新候选全动态验收。

冻结Rig/Mesh/Weights/Corrective/钢琴几何和四个批准静态姿态，以及历史代码、报告、Human决定均保持只读。最终哈希见ASSET_PRESERVATION.json。未重写历史FAIL_CLOSED、PARTIAL或WARN。正常姿态、局部速度/加速度、烘焙与重开的一致性对新候选均NOT_RUN；保持原样不等于修复成功。
''')
before=read(P/'PROTECTED_INPUTS_BEFORE.json');changed=[p for p,h in before.items() if sha(p)!=h];assert not changed,changed
static=read(ROOT/'audits/minuet_stage_c_r2_local_finger_overlap_refinement/PROTECTED_INPUTS_BEFORE.json');static={p:h for p,h in static.items() if 'piano_hand_static_posture_clearance_refinement_r2' in p and Path(p).suffix in ['.blend','.json'] and Path(p).is_file()};assert all(sha(p)==h for p,h in static.items())
assert not list(P.glob('*.blend')) and not list(P.glob('*.mp4')) and not list(P.glob('*.npz'))
preserve=dict(protected_files=len(before),changed_files=changed,approved_static_related_files=len(static),static_changed=0,new_actions=0,new_blends=0,new_videos=0,new_motion_trajectories=0);dump('ASSET_PRESERVATION.json',preserve)
status=dict(PHASE_AWARE_ROLE_PLANNING='IMPLEMENTED',CROSS_FINGER_ROLE_CONFLICT='PARTIAL',LOCAL_SPATIAL_CONSTRAINTS='PARTIAL',WINDOW_BOUNDARY_FEASIBILITY='FAIL',FEASIBILITY_FIRST_SOLVER='NOT_IMPLEMENTED',FORMAL_DYNAMIC_SOLVE_ATTEMPTS=0,VALID_DYNAMIC_CANDIDATE='NO',EARLY_MIDDLE_RING_CLEARANCE='NOT_RUN',LATE_MIDDLE_RING_CLEARANCE='NOT_RUN',BLACK_KEY_CLEARANCE='NOT_RUN',ACTIVE_CONTACT_PRESERVED='PASS',RIGHT_HAND_MOTION_PRESERVATION='PASS',LEFT_HAND_MOTION_PRESERVED='YES',DUAL_HAND_MUSIC_FUNCTION='PASS',ENGINEERING_DIAGNOSTICS='FAIL',HUMAN_VISIBLE_QUALITY='HUMAN_PENDING',FROZEN_ASSETS_UNCHANGED='YES',FINAL_STATUS='FAIL_CLOSED',NEW_STATIC_SOLVES=0,NEW_DYNAMIC_CANDIDATES=0,specific_D5_Fsharp_task_conflict='RESOLVED_IN_ROLE_INTERFACE_ONLY',pass_scope='Original motion/function preserved unchanged; no new dynamic contact or naturalness certification',candidate_outputs='NOT_RUN',protected_files=len(before))
dump('FINAL_STATUS.json',status);dump('ENGINEERING_DIAGNOSTICS.json',dict(status='FAIL',blocking_stage='EXACT_IMMUTABLE_BOUNDARY_CHECK',boundary=data,role_tests_pass=True,nfev=0,major_iterations=0,optimizer_termination='NOT_STARTED_GATE_BLOCKED',phase_to_geometry_integration='NOT_RUN',continuous_skin_constraints='NOT_RUN',all_five_finger_skin_certification='NOT_RUN',dynamic_continuity='NOT_RUN',actual_bake_reopen='NOT_RUN',static_optimizations=0,formal_dynamic_solve_attempts=0,preservation=preserve))
doc('FINAL_ANSWERS.md','''# Q1–Q17

Q1：实现全五指基于事件的重叠角色计划与共享相邻关系；未完成交接路径求解。
Q2：3.825秒任务接口已正确表达中指E5活动、无名指F♯5准备，D5仅退出/机械上下文，不再错误持键；未产生修复动作。
Q3：PARTIAL。实际凸黑键/皮肤内部深度、面交叉和硬裕量已实现；全手连续分离、白键与五指完整保护未完成，因边界失败停止。
Q4：FAIL。四端点均有必须保持而超过0.5mm的非目标黑键穿入，无法同时满足边界原姿态和安全门槛。
Q5：未运行软残差交易；硬边界门禁已阻断，但可行性优先轨迹求解器NOT_IMPLEMENTED。
Q6：正式动态求解0次，新静态优化0次，未消耗唯一动态尝试。
Q7：早段实际相交修复NOT_RUN，原问题保留。
Q8：晚段实际相交修复NOT_RUN，原问题保留。
Q9：黑键实际穿入未改善；窗口内、边界、窗间与窗口外已知问题分别记录。
Q10：原活动接触保持，新增四端点读取；没有新候选可做全动态接触认证。
Q11：原动作完全保留，新修复自然度与连续性NOT_RUN。
Q12：原23音符、琴键、音频、左手和共同时间轴完全保持。
Q13：是，KNOWN_CONFLICT_SCOPE.json及验证报告单列窗口外与两窗间问题，无全曲空间PASS。
Q14：没有改变任何动作，因此未引入新动作异常；原有缺陷未修复。
Q15：是，全部受保护文件及四批准静态姿态相关文件哈希一致。
Q16：新增事件派生重叠角色、活动pad许可接口及真实凸键体/局部skin硬边界查询；其他曲目仅角色移调/移时语义测试，未验证跨曲目运动质量。
Q17：没有新原速候选可提交；只提交本轮实现与生成前失败证据。

FAIL_CLOSED。STOP — HUMAN REVIEW。
''')
print('R5_FAIL_CLOSED',len(violations),'boundary violations',len(before),'protected files; zero solves',flush=True)
