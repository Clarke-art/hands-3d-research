import sys,json,hashlib
from pathlib import Path
sys.dont_write_bytecode=True;O=Path(__file__).resolve().parent
def rd(n):return json.loads((O/n).read_text(encoding='utf8'))
def js(n,d):(O/n).write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf8')
def md(n,s):(O/n).write_text(s.strip()+'\n',encoding='utf8')
ctx=rd('R2_CONTEXT_RAW.json');f=rd('R2_FINAL_FACTS.json');plans=rd('R2_PLANS.json');front=rd('candidate_front_RESULT.json');right=rd('candidate_right_RESULT.json');budget=rd('NUMERICAL_BUDGET.json');prot=rd('R2_PROTECTION_SCOPE_AUDIT.json');feature=rd('R2_OFFENDING_DERIVATIVE_FEATURE.json');lint=rd('R2_INTENT_SEMANTIC_AUDIT.json');domain=rd('R2_ANALYTIC_DOMAIN_INTERVALS.json');p0=plans[0];scope=ctx['time_span'];alloc=p0['reference_time_allocation'];evt=f['event_contacts'];held=ctx['pair']['held'];nextn=ctx['pair']['next']
status=dict(task='PIANO_LONG_CONTEXT_CORRIDOR_IK_BRIDGE_R2',authority='DESIGN_PROVISIONAL — STOP — HUMAN REVIEW',status='PARTIAL',evidence_grade='PARTIAL_EVIDENCE_ONLY',C01_G4_E5_SCOPED_CONTINUOUS_BRIDGE_PASS=False,HUMAN_NATURALNESS_REVIEW_PENDING=True,high_level_timing='AUTOMATIC_REFERENCE_SCOPED_PLAN_PROPOSED_NOT_REACHABILITY_PASS',high_level_serialization=dict(first_candidate='FAILED_STALE_CONTACT_MODE_HEADER',second_candidate='CORRECTED_AND_SOURCE_CHECKED'),optimizer_calls=1,accepted_optimizer_iterations=0,proposed_candidates=2,second_optimizer='EARLY_STOP_SHARED_DERIVATIVE_GATE_REJECTION',unique_actual_samples=f['unique_actual_samples'],failed_actual_samples=f['failed_samples'],C1_latent_curve_math_defined=True,discrete_trajectory_PASS=False,continuous_domain_PASS=False,continuous_geometry_certified=False,current_original_assets_hash_PASS=True,current_global_protection_PASS=False,historical85850_FAIL_preserved=True,historical86148_PASS_preserved=True,original_MIDI_fingering_KeyAction_Rig_changed=False,other_hand_skin_contact='UNMODIFIED_REFERENCE_NOT_INDEPENDENTLY_CERTIFIED',numerical_wall_seconds=budget['total_seconds'],no_further_work_authorized_in_this_run=True)
js('R2_FINAL_STATUS.json',status)
event_rows='\n'.join(f"|{n['note_id']}|{n['midi']}|{n['finger']}|{n['display_on']:.9f}|{n['display_off']:.9f}|" for n in ctx['events'])
md('R2_CONTEXT_AND_BASELINE.md',f'''
# R2 真实上下文与冻结基线

PIANO_LONG_CONTEXT_CORRIDOR_IK_BRIDGE_R2  
DESIGN_PROVISIONAL — STOP — HUMAN REVIEW

原MIDI重新解析23条绑定，C01_PIANOPLAYER指法重新核对；冻结Rig/实际88键/琴键Action从真实Blender源文件读取。源MIDI SHA为{ctx['source_MIDI']['midi_sha256']}，指法候选SHA为{ctx['source_MIDI']['candidate_sha256']}；完整路径、原曲线点、Action payload、精确键角与起点复现见 R2_CONTEXT_RAW.json、SOURCE_MIDI_REVALIDATION.json、R2_PREFLIGHT_ACTUAL.json。源文件未保存，原Action未改。

|事件ID（仅本次输入实例）|MIDI|固定指法|ON展示秒|OFF展示秒|
|---|---:|---:|---:|---:|
{event_rows}

允许的实际起点只有{scope['start']:.9f}s的B2。历史250ms前缀终点2.777855s已只读重新通过真实验收，但未固定其后续状态或中间节点。原G4持键要求保持至{scope['junction']:.12f}s，原E5在同一原ON时刻开始真实PRESS。首次完整下行来自原Action并与接触合同核对，终点{scope['first_full_press']:.9f}s；额外+1us只作终点静态右探针，不宣称完整E5 HOLD连续通过。

原7事件上下文包含R06同指重复、当前持键/换音及后续音。R06→R07真实连续入口仍UNKNOWN，未从其时刻启动动作或把未验证姿态当锚点。运动从B2开始，上下文用于阶段时限和下一音位偏好。左手同时间存在L04/B3释放与L05/C4开始；其键Action被纳入原88键时间评估，左手动作保持源引用，本轮未独立认证左手皮肤接触，不报告双手演奏PASS。

固定工程门禁：腕速500mm/s；根方向速率120deg/s，拇指控制及映射关节240deg/s；lambda5/s、alpha8/s。根XYZ、Euler、拇指域及自然参考族完全继承LOW/HIGH；真实目标/错误区域侵入≤0.25mm、非相邻指面交叉0、面级指腹接触和原pad约束不变。模型代理仍使用更保守0.20mm深度；没有调低真实碰撞精度。

旧共同构型和上方状态作为只读参考。115.490324ms只对旧上方alpha0状态→旧共同状态的固定连接成立，剩余51.904333ms的缺口不能推广为全部合法边界的最短时间。R2允许边界集合变化，不把旧共同向量、旧P2或2ms片段设为硬锚点。

本轮保护基线{prot['current_before_count']}项；既有文件SHA全部一致，另观察到并发Piano安全测试618个新路径，全局保护FAIL单独保留。历史85850项FAIL/3变化/15新增与86148项PASS不被追改。
''')
phase_rows='\n'.join(f"|{p['name']}|{p['window'][0]:.12f}–{p['window'][1]:.12f}|{p['entry']}|{p['exit']}|" for p in p0['phase_schedule'])
subset_rows='\n'.join(f"|{p['candidate_id']}|{p['target_subset']['xmin']*1000:.6f}–{p['target_subset']['xmax']*1000:.6f}|{p['target_subset']['ymin']*1000:.6f}–{p['target_subset']['ymax']*1000:.6f}|{p['mode']}|" for p in plans)
md('R2_HIGH_LEVEL_CORRIDOR_DESIGN.md',f'''
# R2 最小时空走廊设计

DESIGN_PROVISIONAL — STOP — HUMAN REVIEW

高层自动输出阶段窗口、整指实体分离请求、合法目标区域子集与释放后避让，由低层联合接触IK寻找自由控制状态。只固定真实B2；所有其他节点可调。没有把上轮4.349mm安全状态提前后接受，也没有把初始化曲线当求解结果。

时序来源：原当前OFF/下一ON窗口{scope['junction']-scope['start']:.6f}s；原PRESS时长{(scope['first_full_press']-scope['junction'])*1000:.6f}ms。参考手位的根平移、根角、拇指/映射关节、lambda/alpha运动成本取原门禁最大下界，再乘1.5作为所选C1初始化的保守分配启发。二维LP最小化清障完成时刻，同时预留参考下降时间；这是参考条件估计，不能证明所有Rig路径时间可行或不可行。

自动得到清障完成/下降开始{alloc['ready']:.12f}s，比上轮风险静态状态时刻2.869521666667s提前约165.609ms；下降窗口{(scope['junction']-alloc['ready'])*1000:.6f}ms，所选参考下降预留{alloc['descent_minimum_seconds']*1000:.6f}ms。R2计划不强制实际IK使用该旧边界参考。准备、抬指/维持已抬状态和上方横移可重叠；最小示例没有凭空制造休止。

|阶段|窗口秒|进入条件|退出条件（未经IK验证）|
|---|---|---|---|
{phase_rows}

空间约束使用原实体边界和整指三角面：每个面须由上方或指定外侧半空间分离，请求余量0.5mm。该走廊是额外的保守规划请求，未替换原0.25mm接受门禁。下降阶段前方候选与右侧候选使用不同半空间组合及E5合法触键子集；G4在原OFF前始终为硬接触，OFF后按源恢复并要求相关释放皮肤在首个完整E5下行结束时避让。

|候选|目标pad X mm|目标pad Y mm|下降/释放策略|
|---|---:|---:|---|
{subset_rows}

前方子集还根据未来R09键中心在当前目标左/右侧选近侧区域，实际利用后续音符信息；它只是几何启发，没有计算完整下一音的手部可达代价。D#5障碍由R1真实失败见证提供，尚未实现任意MIDI的自动扫掠障碍发现。参考族/公共姿态库仍为C01专用初始化能力，必须披露。

HandMotionIntent以阶段序列方式复用，原实例字段保留，阶段内增加区域/截止等嵌套数据。接口审计发现第一版从R1复制的active_contact_modes未随phase更新；低层原方程直接从源时钟读接触，物理合同未被更改，但序列化层失配，第一候选不授予接口合格。原输入保存candidate_front_PLAN_EXECUTED.json。第二输入按源半开区间更新状态并校验，另声明事件左闭接触相容；没有重新优化第一候选。

修正编译器实际读取阶段意图的窗口、障碍、margin、下降策略与目标子集，不以root摘要绕开接口语义。证据：R2_INTENT_SEMANTIC_AUDIT.json、candidate_right_PLAN_COMPILED.json。第二输入通过字段/时序检查仍不等于走廊可达。

失败反馈分类：EMPTY_TARGET_SET、SELECTED_REFERENCE_TIME_WINDOW_FAILED、SERIALIZED_CONTACT_MODE_MISMATCH、NONSMOOTH_DERIVATIVE_REJECTED、AUTHORIZED_DOMAIN_VIOLATION、HOLD_CONTACT_LOST、WRONG_KEY_COLLISION、TARGET_CONTACT_LOST。当前尚缺可达走廊连边证明；输出只是有几何依据的受限计划。
''')
stage_rows='\n'.join(f"|{s['name']}|{s['wall_seconds']:.6f}|{s['exit_code']}|{s['status']}|" for s in budget['stages'])
md('R2_PLAN_AND_IK_EXECUTION.md',f'''
# R2 高层到接触IK实际执行

DESIGN_PROVISIONAL — STOP — HUMAN REVIEW

两个高层候选是不同触键区域/下降边界策略，不是增加节点、迭代或同问题重启。相同源B2/公共参考库产生共享准备初值；数据均明确标为未验证初始化。没有一条获资格的IK连续轨迹。

前方候选实际进入CasADi/IPOPT：{front['interface']['variables']}控制变量、{front['interface']['constraints']}约束、{front['interface']['jacobian_nonzeros']}结构Jacobian非零、15个全几何接触配点，运动AD每段5点；C1 Hermite连接引入多邻节点依赖。只有B2固定。原Key Action、控制域、接触、碰撞与速率门禁不变。用于裁剪见证点的4个XY不等式在编译中去除，因见证点已由原patch裁剪保证在域内；pad与完整跨面、实际实体深度和真实验收完全保留，不属于放宽物理合同。

前方求解返回{front['status']}，优化迭代0；原日志IPOPT46.543s，其中Jacobian约45.69s，含建模的阶段墙钟58.844s。返回的是IPOPT边界内移后的初值，并未产生有效局部修正。原NLP变量/回调/出错控制输入均在candidate_front_RESULT.json和logs/candidate_front_bridge_execution.log。初始化代码曾漏导入函数，属于迭代前启动错误，记录计费后修复，不算额外候选；没有为失败增加节点或再次执行前方优化。

拒绝在准备区间2.571869374419s的中间配点。具体为MIDDLE/RING非相邻面646/1412的分离支持函数，local row148；约7.682760mm正余量，非实际穿插。alpha近下界，min/max特征切换导致跨步长差异0.248467009和0.361326152，未过1e-3严格差分门禁。保守拒绝正确；该结果说明当前执行器导数前置条件不可靠，不能推导人体或指法不可能。

右侧候选先校验序列化输入；共享准备初值在相同配点复现同一拒绝。第二昂贵优化按早停规则未调用。只读尝试合法单侧差分，原严格阈值不改，最后差异{feature['domain_aware_last_error']:.9f}仍失败；没有采用未经验证的导数继续。R2_DERIVATIVE_SHARED_BLOCKER.json、R2_DOMAIN_DERIVATIVE_CHECK.json、R2_OFFENDING_DERIVATIVE_FEATURE.json可复核原始步长、分支与轴。

两套未优化预览仅有IPOPT内移的浮点舍入差（约1.208e-13控制单位）；float32 Rig输入一致，统一诊断预览只为了避免重复Blender扫描。右侧没有求解成功或独立连续路径证据。R2_INITIALIZER_IDENTITY_CHECK.json保留推导与舍入量；不把复用样本计为两条成功轨迹。

|数值阶段|墙钟秒|退出码|状态|
|---|---:|---:|---|
{stage_rows}

保守数值阶段计账{budget['total_seconds']:.6f}s，1次优化器调用、0次有效迭代、2个提案；诊断/启动错误也计入。独立SHA和Blender验收/报告I/O另记，不作为求解优化时间。无第三候选、随机重启、重复旧25ms/2ms求解或扩大训练平台。
''')
first_rows='\n'.join(f"|{gate}|{v['previous_sample_time']:.12f}|{v['first_failure_time']:.12f}|" for gate,v in f['first_failures'].items())
domain_rows='\n'.join(f"|{r['control']}|{r['bound_type']} {r['actual_gate_bound']}|{r['time_interval'][0]:.12f}–{r['time_interval'][1]:.12f}|" for r in domain['intervals'])
md('R2_BLENDER_CONTINUITY_VALIDATION.md',f'''
# R2 真实采样与区间验证：FAIL

DESIGN_PROVISIONAL — STOP — HUMAN REVIEW

本轮未得到有效IK路径。Blender检查对象为返回的C1初始化诊断预览；不得将这些姿态人工拼接或称作成功演奏。75个规则/阶段/事件/内部点加28个首次失败区间补采样，共{f['unique_actual_samples']}个唯一真实样本，{f['passing_samples']}通过、{f['failed_samples']}失败。第二候选只复用相同诊断预览的物理几何，不授予第二次IK执行或新路径PASS。

原88键实际几何、源动画键角、完整冻结右手FK/加权皮肤、面级指腹、实体深度、自交、参考公式、授权域及反解关节均验收。原Action与native身份在全部样本一致。全皮肤数值模型对实际皮肤最大误差{f['maximum_skin_parity_mm']:.9f}mm；原始AUDIT_*_ACTUAL_SKIN.npz、R2_FULL_SKIN_PARITY.json保存逐帧比较。

|原门禁|前一采样秒|首个补采样失败秒（不是精确失效时刻）|
|---|---:|---:|
{first_rows}

连续域违规由C1控制多项式另作区间求根确认，沿用原实际验收容差（普通控制1e-3、lambda/alpha1e-6），没有扩大允许域：
|控制索引|违规边界|违规开区间秒（双精度数值根）|
|---|---|---|
{domain_rows}

对应alpha最低约-0.030614、根yaw约-12.017872°、拇指IP约-0.007199°。这些是超出本轮授权参数域，不是医学舒适或人体不可能判断。初始化C1中心切线在平坦/边界节点发生过冲；仅把合法节点用C1曲线连起来不能保证曲线留在合法域。至少这些区间使本条诊断曲线连续意义上必不合格，不能靠多采几毫秒获得PASS。

E5在原ON={scope['junction']:.12f}s单独的面级接触为{next(r['contact_gate'] for r in evt if r['midi']==nextn['midi'])}。旧G4左侧闭接触为{next(r['contact_gate'] for r in evt if r['midi']==held['midi'])}，且G4在HOLD结束前已丢接触；不能从E5单时刻触键成功推出连续换音。首次完整E5下行终点也未通过全部接触/错误区域门禁。

实际最大目标深度{f['target_max_depth_mm']:.6f}mm，最大错误区域{f['wrong_region_max_depth_mm']:.6f}mm。最严重后段C5/INDEX侵入5.353383mm，D5/MIDDLE约4.721488mm；因此不只是D#5单障碍。非相邻指面交叉0。自然参考公式和轴检查通过，但域检查失败；公式一致不能代替“属于授权参考族”的资格。

501点/段运动复核峰值腕速{f['kinematic_dense_peak_wrist_mm_s']:.6f}mm/s、映射关节{f['kinematic_dense_peak_joint_deg_s']:.6f}deg/s；真实不等时间差峰值分别{f['actual_secant_peak_wrist_mm_s']:.6f}mm/s、{f['actual_secant_peak_joint_deg_s']:.6f}deg/s。速率通过不能覆盖接触、碰撞和域失败。多项式定义在范围内的latent位置/速度C1，未证明所有皮肤驱动速度C1、C2或力学自然度。

规则网格120Hz；精确事件旁有±1us探针，首次失败括区间做8等分，几何最小样本间距{f['geometry_sample_min_step_seconds']*1000:.6f}ms。未进行全区间无碰撞证明或有界扫掠皮肤证书。采样失败区间、解析域失败、数学曲线连续与Human自然度分开记录。Human无合格轨迹可审，状态HUMAN_NATURALNESS_REVIEW_PENDING。没有正式Action/Blend/视频。

原始来源：R2_BASE_ACTUAL.json、R2_ADAPTIVE_ACTUAL.json、R2_ADAPTIVE_BRACKETS.json、R2_ANALYTIC_DOMAIN_INTERVALS.json、R2_DENSE_MOTION_AUDIT.json、R2_ACTUAL_TIME_DIFFERENCES.json、R2_FINAL_FACTS.json。
''')
md('R2_GENERALIZATION_AND_COMPLEXITY_REVIEW.md',f'''
# R2 通用性、接口责任与复杂度

DESIGN_PROVISIONAL — STOP — HUMAN REVIEW

|问题|实际实现与边界|
|---|---|
|哪些时间/走廊由高层决定|原事件窗口内自动LP分配2.703912497675s清障完成与后续下降；自动前方/右侧合法子区域和释放避让请求；进入/退出条件明示|
|哪些修正由IK决定|原意是联合调整所有非起点控制并满足C1/接触/几何；实际0次优化迭代，没有获资格的IK修正；IPOPT内部边界push不是动作规划成果|
|较旧局部求解改变什么|由单终点/旧局部窗转为完整原准备—清障—下降—PRESS语义和15个区间内全几何配点；通过不同目标集合表达不同策略|
|是否利用多个MIDI事件|读取7个实际事件；当前ON/OFF、下一ON/完整下行决定窗口，后续R09键中心改变前方目标近侧区域；前序只作原时序证据，未使用未验证R06姿态|
|是否减少人工中间姿态|没有新人工设计的硬中间姿态，只有B2硬锚点；仍使用C01公共静态姿态库作暖启动，不能称完全自动动作生成|
|当前失败在哪里|高层序列化第一版有状态标签失配；执行器在共享准备配点的支持特征导数不一致；初始化C1越域、脱离持键流形，后段闲指穿其他键；高层走廊可达性尚未验证|
|能推广哪些部分|事件驱动窗口、分离区域、子目标集合、失败类型和序列化校验可以复用；未证明其他音型/左手/和弦的真实执行|
|C01特殊依赖|B2/公共姿态/自然族、R1失败给定障碍、指定中指alpha能力、原线性Action；不会自动发现任意MIDI的障碍或构造手部初始状态|

第一版HMI active_contact_modes从旧静态实例继承，没有随阶段正确变换，这是实际接口缺陷；低层使用正确源时钟，原音乐和物理合同没有被修改，但“意图→执行单一来源”验收不成立。已在第二输入加入前置语义检查，第一原输入与调用结果永久保留；第二没有昂贵重试。

C1插值不会自动保持控制域或活动接触流形。控制、物理皮肤、接触模式和时钟需要在同一编译步骤形成位置与切线约束，不能只对节点做静态IK然后插值。当前15个几何配点仍是离散约束，不等于连续实体证书。

运动表示也限制了高层意图：冻结Rig本来有20个手指工程坐标，但当前12维接口只有根6、拇指4与lambda/alpha。INDEX三个flex在Q1-Q0中严格为0，RING/LITTLE也基本不变；不能独立抬闲置食指。实际最深C5/INDEX错误区域碰撞应与此能力缺口一并反馈。不同掌腕路线可能避免它，本轮没有排除所有路径；若需要扩展动作参考族，须Human单独授权，不修改Rig或自动扩大域。R2_MOTION_REPRESENTATION_AUDIT.json保存真实差分。

存在过度复杂化风险：96变量、5579约束、114929结构非零，15个全几何有限差分回调，46.543s仍0次有效迭代。高层本身是简单2变量时间分配，主要成本来自C1邻状态依赖与几何导数。继续添加阶段、节点或大模型不能修复这一基础问题。

最小下一项技术工作应是一套“接触模式单一来源→域保持/接触切线相容的连接→经分支校验的低层执行”的合同闭环，先解决当前可重放的界面/表示反例。之后才评估原参考族下的不同掌腕通道；必要时提出闲指准备能力的授权扩展请求。没有准备好进入另一段换音的真实性能测试；合同级表达可以讨论，本轮不执行。
''')
md('R2_PROTECTION_AUDIT.md',f'''
# R2 保护与并发审计

DESIGN_PROVISIONAL — STOP — HUMAN REVIEW

本轮开始前继承86148项已通过快照，扩展覆盖正式Hands/Piano、冻结Rig/MIDI/指法/Action、所有Hands历史实验及R1成果，实际保护{prot['current_before_count']}项。独立前后SHA256重算：原有{prot['current_after_rehashed_count']}项全部一致，修改0、删除0，冻结输入与Hands历史未受影响。

全局保护仍记FAIL：后验扫描观察到{prot['observed_new_path_count']}个新增路径，全部位于Piano/local_gb_01_execution_safety_patch_r1。已只读核实另一聊天Human授权的LOCAL_GB_01_EXECUTION_SAFETY_PATCH_R1，授权隔离安全测试及脚本修订，禁止实际原项目清理；原始Human文本、fileChange和commandExecution保存在R2_CONCURRENT_TASK_RAW_EVIDENCE.json。Task归属为ATTRIBUTED_CONCURRENT_ADDITION。

新增路径包含隔离测试文件、日志、恢复映射以及重解析/junction视图；不能把618路径当作618个独立正式资产或物理副本。逐路径完整名称、大小/时间/属性、瞬态情况见R2_PROTECTION_SCOPE_AUDIT.json。没有读取这些大测试资产内容作为运动依赖，没有删除、移动、恢复或覆盖另一任务成果。Snapshot之后的并发瞬态变化不被声称全面掌握。

历史85850项扩展FAIL（另一次Piano存储审计3处变化/15新增）与86148项PASS继续独立保留，没有用本轮原文件哈希一致追改历史，也未把本轮全局FAIL改成PASS。

本Hands任务新增内容只在独立R2目录；原Action/Rig/88键/指法/MIDI没有写入，Blender源文件未保存。实际每样本native与原Key Action身份均匹配。必要机器清单：PROTECTED_FILES_BEFORE.json、PROTECTED_FILES_AFTER.json、PROTECTION_SETUP.json、PROTECTION_CHECK.json、R2_PROTECTION_SCOPE_AUDIT.json、HISTORICAL_CONCURRENCY_ATTRIBUTION.json。

由于技术失败和全局保护FAIL，正式生产保持fail closed。核心科学输入未变化可以支持本轮诊断结论，不授予其他资产或动画生产资格。
''')
md('R2_FINAL_RECOMMENDATION.md',f'''
# PIANO_LONG_CONTEXT_CORRIDOR_IK_BRIDGE_R2

**PARTIAL — PARTIAL_EVIDENCE_ONLY**  
**STOP — HUMAN REVIEW**

没有实现合格的高层清障规划→现有IK真实连续换音。不会报告C01_G4_E5_SCOPED_CONTINUOUS_BRIDGE_PASS，更不会升级为通用MIDI自动演奏。

本轮真实恢复原MIDI/C01/Action/Rig，自动提出前方与右侧两个下降边界策略，将清障完成时刻回推到2.703912497675s，保留原E5 ON2.921426s和原完整下行2.956426s，只有真实B2固定。阶段窗口与区域由源码生成、不是把旧安全静态姿态提前后接受。C01姿态库仍用于暖启动，走廊可达性尚未证明。

前方候选进入96变量/5579约束联合接触IK，返回Invalid_Number_Detected，0次优化迭代。准备段2.571869374419s的MIDDLE/RING支持特征导数跨步长差异0.248467/0.361326，严格拒绝；该行有7.683mm正余量，不是发现真实指面穿插。右侧共享该执行器前置失败，未重复昂贵优化。域内单侧差分检查也未通过1e-3门禁，因此没有采用错误导数继续。第一候选序列化接触模式标签未按phase更新，另记协议失败；第二输入已按源时钟修正，但未获得执行成功资格。

独立Blender只验收未优化的C1诊断预览：{f['unique_actual_samples']}个唯一样本、{f['failed_samples']}失败。参数域首个补采样失败{f['first_failures']['authorized_domain']['first_failure_time']:.12f}s；G4持键接触失效{f['first_failures']['all_required_contacts']['first_failure_time']:.12f}s；最大目标实体深度{f['target_max_depth_mm']:.6f}mm、错误区域{f['wrong_region_max_depth_mm']:.6f}mm。最大错误为C5/INDEX，后段另有D5/MIDDLE。C1多项式解析确认alpha、根yaw和拇指IP越域区间；不是只有采样不足。

E5在ON时刻单独触键通过，但G4早已丢失HOLD和闭边界相容，完整PRESS后续也失败。腕速约{f['kinematic_dense_peak_wrist_mm_s']:.3f}mm/s、关节速率约{f['kinematic_dense_peak_joint_deg_s']:.3f}deg/s虽低于工程门禁，不能覆盖域、接触和碰撞失败。数学C1构型不等于连续接触/无碰撞验证；Human自然度仍REVIEW_PENDING，无合格路径送审。

A. **真实连续衔接实现了吗？没有。** 只完成受限时间/空间意图及失败执行证据。高层计划提案、静态姿态、离散曲线、区间技术资格和Human自然度保持分级，未跨级PASS。

B. **主要阻碍及证据充分度？** 已充分定位当前执行器支持特征导数拒绝、序列化状态失配、C1域/接触流形不保持及闲置食指准备能力不足。未优化曲线实际侵入，不能据此证明所有时空走廊、当前指法或人体动作不可能；时序LP只是参考条件分配，尚未证明高层本身可达。

C. **继续A的最小必要工作？** 保留简单高层事件/走廊接口，先完成接触模式单一来源、域保持且与活动接触切线相容的曲线、经合法分支验证的接触执行器。之后才在原参考族下验证一项受控连接；闲指能力若需新增参考族必须Human另授权，不松原Rig/碰撞/速度门禁。停止旧2ms/25ms的局部节点、毫秒和迭代补丁循环。

D. **过度复杂化风险？有。** 114929结构非零与15个几何回调在首次Jacobian就阻断；继续增加规划层/大模型或更多节点会掩盖基础缺口。下一工作应缩为执行合同的可复现反例闭环，不再大范围选型。

E. **可以开始另一段换音真实测试吗？尚不具备。** 通用合同的结构可复用，真实跨序列与双手生成资格没有建立，应先解决基础衔接；本轮不自动执行其他样本。

数值阶段保守墙钟{budget['total_seconds']:.6f}s，1次优化器调用/2个提案；全部启动错误和诊断计账，无第三候选。原有{prot['current_before_count']}项保护SHA一致，新增618个并发Piano隔离测试路径已归属，当前全局保护FAIL保留；历史85850项FAIL/3变化/15新增及86148项PASS独立保留。未制作正式Action、Blend成品、完整视频、批量渲染或双手引擎。

七项报告及原始结果、实际调用记录、源代码哈希已交付。停止，等待ChatGPT独立审核和Human授权。
''')
required=['R2_CONTEXT_AND_BASELINE.md','R2_HIGH_LEVEL_CORRIDOR_DESIGN.md','R2_PLAN_AND_IK_EXECUTION.md','R2_BLENDER_CONTINUITY_VALIDATION.md','R2_GENERALIZATION_AND_COMPLEXITY_REVIEW.md','R2_PROTECTION_AUDIT.md','R2_FINAL_RECOMMENDATION.md']
assert all((O/n).is_file() for n in required);assert rd('POLICY_LOCK.json')['no_more_solves'];assert not any(O.glob('*.blend'))
js('R2_DELIVERY_CHECK.json',dict(task='PIANO_LONG_CONTEXT_CORRIDOR_IK_BRIDGE_R2',status='PARTIAL_STOP_HUMAN_REVIEW',required_deliverables={n:hashlib.sha256((O/n).read_bytes()).hexdigest() for n in required},unique_actual_samples=f['unique_actual_samples'],failed_actual_samples=f['failed_samples'],optimizer_calls=1,proposed_candidates=2,second_optimizer_early_stopped=True,numerical_wall_seconds=budget['total_seconds'],core_protected_hashes_unchanged=True,current_global_protection_PASS=False,observed_concurrent_new_paths=618,historical85850_FAIL_preserved=True,historical86148_PASS_preserved=True,scoped_continuous_bridge_PASS=False))
print('R2_DELIVERY_COMPLETE_PARTIAL',len(required),'reports',f['unique_actual_samples'],'samples',f['failed_samples'],'failures',flush=True)
