"""Close evidence after the first diagnostic error. No solver or geometry rerun."""
from support import *
sys.path.insert(0,str(OLD/'_deps'))
from persistence import atomic_json,load_record
import numpy as np
from datetime import datetime,timezone
P=read(O/'POLICY.json');I=read(O/'INPUT_BINDINGS.json');L=read(O/'COMPUTE_LEDGER.json');gate=read(O/'INPUT_GATE.json')
N=read(O/'SOURCE_LOCAL_NUMERIC_SUMMARY.json')
assert sha(O/'POLICY.json')==gate['policy_sha256']
assert [s['name'] for s in L['stages']]==['prepare','source_fit','source_actual']
assert L['stages'][-1]['returncode']==7
log=(O/'source_actual.log').read_text(encoding='utf8');assert "KeyError: 'source_scene'" in log
error=dict(task=P['task'],stop_reason='BLENDER_DIAGNOSTIC_INPUT_SCHEMA_ERROR_AFTER_SOURCE_LOCAL_SOLVE',exception="KeyError: 'source_scene'",file='source_actual.py',line=10,requested_binding='source_scene',actual_binding='scene',blender_scene_loaded=False,actual_corrected_skin_samples=0,source_local_terminal_records=3,source_fit_repeated=False,failed_diagnostic_repeated=False,stage2_started=False,target_optimizer_calls=0,formal_dynamic_candidates=0,actions_generated=0,blends_generated=0,videos_generated=0,status='INCONCLUSIVE',hypothesis='UNKNOWN',human_naturalness='NOT_TESTED',script_sha256=sha(O/'source_actual.py'),log_sha256=sha(O/'source_actual.log'),input_sha256=sha(O/'INPUT_BINDINGS.json'),utc=datetime.now(timezone.utc).isoformat())
atomic_json('STOP_RECORD.json',error)
verification=[]
with np.load(ROOT/'experiments/hands_reusable_motion_representation_feasibility_r1/SOURCE_AUDIT_SAMPLES.npz',allow_pickle=False) as src:
 for i,row in enumerate(N['rows']):
  a,m=load_record('SOURCE_LOCAL_RESULT_'+str(i)+'.npz');ix=int(np.argmin(abs(src['times']-row['time'])));q0=src['qdeg'][ix]
  required={'x','fun','grad','active_mask','q','world','key_angles','x0'};assert set(a)==required
  assert all(np.isfinite(v).all() for v in a.values())
  assert np.array_equal(a['q'][:4],q0[:4]) and np.array_equal(a['world'],src['rig_world'][ix])
  assert np.array_equal(a['key_angles'],src['key_angles'][ix])
  bounds=np.array(P['joint_bounds_deg'][4]);domain=bool(np.all(a['q'][4]>=bounds[0]) and np.all(a['q'][4]<=bounds[1]));assert domain
  verification.append(dict(time=row['time'],file='SOURCE_LOCAL_RESULT_'+str(i)+'.npz',fields=sorted(a),nfev=m['nfev'],njev=m['njev'],residual_calls=m['residual_calls'],success=m['success'],message=m['message'],cost=m['cost'],optimality=m['optimality'],q_little_deg=a['q'][4].tolist(),q_little_prior_deg=q0[4].tolist(),other_digits_identical=True,shared_wrist_identical=True,key_action_identical=True,own_joint_domain_pass=domain,actual_blender_terminal_validated=False))
atomic_json('RESULT_READBACK_CHECK.json',dict(pass_=True,rows=verification,static_only=True,raw_optimization_state_complete=True,no_geometry_recomputation=True))
features,meta=load_record('SOURCE_FEATURES.npz')
atomic_json('FEATURE_PROVENANCE.json',dict(source_only=True,target_joint_samples=0,phase_samples=len(features['times']),source_context_events=[n['note_id'] for n in I['source_context']],target_context_events=[n['note_id'] for n in I['target_context']],joint_reference='All source joint samples retained as prior/evidence; defective idle traces are forbidden to copy into target',wrist_storage='wrist_relative_world actually stores source rig_world; key-relative normalization/generator not completed',contact_storage='Skin pads and key angles per source sample; four source-context inset-normalized XY anchors',roles='Events and A2 role rules identified; synthesized target role curves not implemented',target_generation_executed=False))
protect();before=read(O/'PROTECTED_BEFORE.json');after={p:sha(p) for p in before};changed=[p for p in before if after[p]!=before[p]]
atomic_json('PROTECTION_CHECK.json',dict(pass_=not changed,count=len(before),changed=changed,before=before,after=after,independent_piano_access=False,historical_concurrent_FAIL_revoked=False,scope='Referenced files only; no unrelated full-tree scan; original C1 and production native Blend hashes included'))
codefiles=['prepare.py','model.py','source_fit.py','source_actual.py','run_stage.py','persistence.py','support.py','reports.py']
atomic_json('EXECUTED_CODE_SHA.json',dict(files={n:sha(O/n) for n in codefiles},policy_sha256=sha(O/'POLICY.json'),source_batch_start=read(O/'SOURCE_PRECHECK_STARTED.json'),failed_diagnostic_left_unchanged=True))
def report(n,s):
 assert not (O/n).exists()
 (O/n).write_text(s,encoding='utf8')
report('ROLE_MOTION_REPRESENTATION.md',f'''# 角色动作表示与来源能力预检

**来源特征提取有部分实证；跨事件可复用生成尚未实施。** 本轮没有再次将来源整手无碰撞作为提取前提。

唯一来源为冻结C1 R04 C5(4)→R05 D5(5)，上下文R03 B4(3)与R06 G4(1)；唯一锁定目标为R12 F♯5(4)→R13 G5(5)，上下文R11 E5(3)与R14 G4(1)。正式MIDI重新解析并对照ON/OFF tick、音高、channel、velocity；展示时间为原MIDI时间加0.35秒。来源ON分别1.4214275、1.635713秒，目标ON分别3.9928535、4.207139秒；持键时长分别0.2142855、0.428571秒，两组事件相位相差2.571426秒。目标关节轨迹未读取。

唯一表示锁定为“事件相位＋共享掌腕相对运动＋五指RSSF相对姿态＋真实活动接触特征”。[SOURCE_FEATURES.npz](SOURCE_FEATURES.npz)保存239个来源采样：事件相位、五指角度先验、共享Rig世界矩阵、五个真实skin pad、88键Action角度及四个上下文事件的键面内相对XY锚点。它是带缺陷标记的来源特征记录，**不是安全原语或新动作**。其中`wrist_relative_world`实际仍是源Rig世界矩阵，尚未完成相对键位归一化或生成器；五指原曲线仅作来源证据/先验，禁止直接复制缺陷闲置轨迹。来源速度与关节曲度可供后续先验，本轮没有新时标或连续速度验收。详细边界见[FEATURE_PROVENANCE.json](FEATURE_PROVENANCE.json)。

已有证据支持活动pad与其他指的条件性分离，但全手皮肤有跨指权重、共享指蹼和拇指corrective，不能分开五个掌根。原来源168个活动pad样本PASS；62个中／无名指相交样本、161个非目标键侵入样本仍存在。原R05小指103/110样本有自身E5侵入，2.0秒见证顶点2731深1.715146mm。它不能靠只改闲置指消除。以上数字来自前轮真实Blender审计，不能记为本轮新验证。

本轮只做一批三点局部必要能力测试：1.7000、2.0000、2.0625秒。每点开放本活动指四个合法工程角和D5既有inset键面内XY，共6变量；共同掌腕、其他四指及键Action完全固定。一次确定性初始化，每点最多45 nfev；三个实际调用为13、12、13 nfev。没有源整段修复或逐帧来源求解。

复用冻结FK/LBS与corrective、既有SciPy bounded least_squares和真实skin pad定义；局部残差同时包含pad对运动键面、活动指权重>0.05皮肤对非目标凸键体深度及姿态/XY先验。深度基于真实皮肤顶点与登记凸键体，**仍缺少Blender终态面相交确认及连续整手覆盖**。接触门槛横向≤0.03mm、绝对gap≤3mm，邻键深度≤0.5mm；未放宽关节域或碰撞门禁。

| 来源时刻s | pad横向mm | gap mm | 计算皮肤邻键最大正深度mm | 关节角增量MCP/PIP/DIP/外展° |
|---|---:|---:|---:|---|
| 1.7000 | 0 | 0.528003 | 0 | −4.274 / +12.257 / +8.087 / +4.009 |
| 2.0000 | 0 | 0.500046 | 0 | +1.051 / +0.061 / −0.451 / +4.346 |
| 2.0625 | 0 | 0.500011 | 0 | +0.881 / +0.087 / −0.392 / +3.849 |

三解本指角度在既有域内，其他指/腕/键Action逐数组相同。1.7秒需要PIP改变12.26°和DIP改变8.09°，不能未经视觉或速度检查称为微调且自然。源三姿态原始皮肤的FK重建误差最大0.000612mm支持数值映射，但不是对修改后终态的真实Blender确认。

真实诊断在输入字段读取处失败，尚未加载C1。结论为**有限校正能力有静态数值线索，真实skin安全UNKNOWN**；不是完整来源修复，也不是相邻指安全或动态成功。按出错止损，未进入目标适配。
''')
report('RECOMPOSITION_EXECUTION_AND_VALIDATION.md',f'''# 执行、真实几何与连续性验证

**INCONCLUSIVE — 实现错误导致真实终态复核未执行，目标重组未开始。** 原始局部优化终态完整保存。

运行顺序：prepare输入/数值FK/持久化测试PASS → 一批三个来源局部求解均返回 → 唯一来源真实Blender诊断启动后退出7。错误为[source_actual.py:10](source_actual.py)访问`I['source_scene']`，实际[INPUT_BINDINGS.json](INPUT_BINDINGS.json)字段是`scene`。输入预检验证了MIDI、FK与局部残差和输出读回，却遗漏Blender诊断输入契约。失败发生在`bpy.ops.wm.open_mainfile`之前；没有读取C1姿态、执行真实修改后skin诊断或产生几何结果。完整现场见[source_actual.log](source_actual.log)、[STOP_RECORD.json](STOP_RECORD.json)。未修改失败脚本，未重跑诊断或求解。

三个原始结果[SOURCE_LOCAL_RESULT_0.npz](SOURCE_LOCAL_RESULT_0.npz)、[SOURCE_LOCAL_RESULT_1.npz](SOURCE_LOCAL_RESULT_1.npz)、[SOURCE_LOCAL_RESULT_2.npz](SOURCE_LOCAL_RESULT_2.npz)均优先原子保存，然后才计算数值汇总。各文件含x/x0、残差、梯度、active_mask、全手q、共同Rig矩阵、88键角度，内嵌success/message/nfev/njev/cost/optimality、残差调用数与累计耗时。临时文件fsync、读回一致再原子替换；现有证据不可覆盖。本次没有恢复任何P3历史丢失终态。[RESULT_READBACK_CHECK.json](RESULT_READBACK_CHECK.json)确认三个结果完整、有限、同腕且其余四指不变。

| 证据级别 | 本轮结果 |
|---|---|
| 来源信息提取 | 部分完成，239源样本和事件/键面锚点 |
| 来源活动指有限静态数值校正 | 三点数值接触与本指邻键深度通过 |
| 修改后来源真实skin安全 | UNKNOWN；Blender输入错误，0个确认样本 |
| 目标角色重组表示生成 | NOT_TESTED，外层求解0 |
| 目标活动接触/全手skin与88键 | NOT_TESTED |
| 完整限定窗口连续验证 | NOT_TESTED |
| Human自然度 | NOT_TESTED |

Stage 2仅锁定八个参数，没有执行或构建第二方案：共享腕Y ±8mm、Z ±5mm；第一/第二活动角色PIP ±4°；中指/食指闲置MCP 0–8°；拇指闲置CMC 0–5°；第一角色释放MCP 0–8°。局部IK内部6变量另行记账。指法、时序、Rig自由度与原合法域未更改；没有将8.70mm P3条件缺口用作固定腕位移。

目标黑键F♯5与白键G5需要不同高度、纵深和邻键协调，不可把C5→D5整体平移视为适配。当前没有生成共享腕适配曲线、释放/准备/闲置角色曲线、PCHIP目标轨迹或入口/出口速度连接证据。因停止原因是程序字段错误，不能声称目标触键不可达、存在确定几何冲突、时间不足或必须全手重求解。

来源局部求解进程9.280071秒，其中求解脚本报告三点处理累计6.879068秒（含保存及数值诊断，不是纯优化CPU时间）；prepare 2.528121秒；失败Blender诊断0.724040秒。预算保守计入三个进程全耗时，总数值执行12.532232/180秒，另列Blender诊断0.724040秒。报告与SHA核查单列，最终数值见[COMPUTE_LEDGER.json](COMPUTE_LEDGER.json)。`total_process_seconds`为受控子进程累计，并非包含代码编写/阅读的总工作时长；审计闭合同时登记目录创建至闭合的壁钟区间。

新Action、候选Blend、视频、正式动态候选均0。没有可用于与原目标C1比较的动作质量或完整生成/验证成本；不得以这三个静态求解的成本声称优于792变量P3或原C1全手优化。

本轮实际引用源文件{len(before)}项前后SHA核查{'PASS' if not changed else 'FAIL'}，详见[PROTECTION_CHECK.json](PROTECTION_CHECK.json)；关键执行代码和锁定政策见[EXECUTED_CODE_SHA.json](EXECUTED_CODE_SHA.json)。独立piano无访问；历史并发保护FAIL没有撤销。保护结论只覆盖实际引用文件，不是无关全目录审计。
''')
report('FINAL_HUMAN_REVIEW.md','''# 最终Human审核

**HANDS_ROLE_AWARE_MOTION_RECOMPOSITION_R1 — INCONCLUSIVE。**

本轮完成来源特征记录和一批三点活动小指有限校正，取得保接触并降低自身邻键侵入的静态数值线索；随后真实Blender诊断因新增脚本输入字段错误停止。该错误属于本轮实现缺陷，不是指法、Rig、来源资格或动作复用理论失败。按“正式求解开始后发生错误即停止”留证，没有修复后重跑，也没有进入目标重组。

| 必答项 | 结论 |
|---|---|
| A 真正提取并使用C1有效特征？ | **部分。** 源事件相位、关节先验、共享腕数据、skin接触与键内锚点已提取；源活动姿态和接触用于局部校正。尚未完成键相对腕表示或目标生成，不能宣称完整原语复用。没有复制目标关节答案。 |
| B 有限活动校正保持真实接触及自身安全？ | 三个冻结FK/LBS静态结果满足数值接触与自身邻键深度，角度合法；真实Blender修改后skin确认缺失，**UNKNOWN**。 |
| C 释放/准备/闲置按MIDI重组？ | **NOT_TESTED。** 角色输入与原规则具备，目标角色曲线未生成。 |
| D 实际合法跨事件连续动作？ | **没有。** 动态候选0，静态局部解不能拼接成成功动作。 |
| E 新穿指、黑键侵入、接触丢失、域违规？ | 仅三点本指角度域数值通过；其他指/腕原样。新终态指间/共享皮肤及全窗口风险未真实检查；目标全部NOT_TESTED。不能声称没有新增回退。 |
| F 工程成本和质量？ | 本次数值执行12.532232秒，真实诊断未完成。没有目标质量或完整成本对照，不能给出加速比、收益或成功率。 |
| G 跨音符/角色复用依据？ | 事件相位、条件FK分离与局部数值校正提供有限接口线索；跨黑白键、共同腕协调、全角色与连续安全仍未证明。 |
| H 扩展通用避障还是换路线？ | **本轮停止，不建议直接扩展通用系统或进入产品。** 当前错误尚不能否定表示或证明必须全手重解；也不足以授权继续同类调参。由独立审核与Human决定是否另行处理实现契约，不能自动重跑或改选路线。 |

`LOW_COMPLEXITY_RECOMPOSITION_HYPOTHESIS = UNKNOWN`

没有证据要求重新开放全时刻26维，但也没有一段合格跨事件动作支撑低复杂度假设。不得将输入字段错误记为`NOT_SUPPORTED_WITHIN_SCOPE`的运动学反证。

`HUMAN_NATURALNESS = NOT_TESTED`

没有合格候选，不制作形式性对照视频。原Human认可只属于原C1整体观感，未转移到本次三个局部解。

交付：[ROLE_MOTION_REPRESENTATION.md](ROLE_MOTION_REPRESENTATION.md)、[RECOMPOSITION_EXECUTION_AND_VALIDATION.md](RECOMPOSITION_EXECUTION_AND_VALIDATION.md)及本报告。原始数组、失败日志、参数锁定和SHA保护记录均在本目录。

**HANDS_ROLE_AWARE_MOTION_RECOMPOSITION_R1**  
**INCONCLUSIVE**  
**STOP — HUMAN REVIEW**

等待ChatGPT独立审核及Human授权。不得自动开展第二次跨事件适配、P3/B02修补、新指法、其他MIDI、动作库或正式动画生产。
''')
directory_birth=datetime.fromtimestamp(O.stat().st_ctime,timezone.utc)
atomic_json('WORKFLOW_TIME.json',dict(directory_created_utc=directory_birth.isoformat(),audit_closed_utc=datetime.now(timezone.utc).isoformat(),elapsed_since_directory_creation_seconds=(datetime.now(timezone.utc)-directory_birth).total_seconds(),scope='Observed directory lifetime; includes editing/reading pauses after directory creation; excludes earlier task reading; distinct from numerical execution budget'))
print('CLOSED INCONCLUSIVE; UNKNOWN; NOT_TESTED; protection',len(before),not changed,flush=True)
