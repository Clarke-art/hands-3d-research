from stage_common import *
from left_continuous_motion import *
assert not (P/'RECOVERY_ATTEMPT.json').exists()
r=read(P/'PROVENANCE_AND_RISK_DATA.json');g=read(G/'SOLVER_AND_GUARD_DIAGNOSTICS.json')
# Rig-chain-length angular bound is independent of pose and does not construct
# or clip an alternative trajectory. It covers simultaneous excess components.
radii=[]
for j,digit in enumerate(c.DIGITS):
    names,rels,axes,spread,pad=c.SETUPS['L',digit];paddist=np.linalg.norm(pad[:3]);dist1=np.linalg.norm(rels[1][:3,3]);dist2=np.linalg.norm(rels[2][:3,3])
    radii.extend([float((dist1+dist2+paddist)*1000),float((dist2+paddist)*1000),float(paddist*1000),float((dist1+dist2+paddist)*1000)])
budget=np.array(read(P/'GENERATION_POLICY.json')['joint_delta_limits_deg']).ravel();grouped={}
for x in r['sample_violation_records']:grouped.setdefault(x['time_sec'],{})[x['flat_index']]=x['excess_deg']
import importlib.util
spec=importlib.util.spec_from_file_location('saved_policy_curve',G/'total_angle_pipeline.py');k=importlib.util.module_from_spec(spec);spec.loader.exec_module(k);p=k.TotalAnglePipeline();raw=np.array(read(G/'SOLVER_RETURN_CHECKPOINT.json')['raw_unknown_actual_delta_deg']);curve=p.curve(raw)
for x in r['continuous_extrema_records']:
    t=x['time_sec'];actual=curve(t)-p.refcurve(t);excess=np.maximum(abs(actual)-budget,0);grouped[t]={i:float(excess[i]) for i in np.flatnonzero(excess>1e-7)}
bounds=[]
for t,es in sorted(grouped.items()):
    byfinger=np.zeros(5)
    for i,e in es.items():byfinger[i//4]+=radii[i]*e*np.pi/180
    bounds.append(dict(time=t,combined_excess_arc_bound_mm_by_finger=byfinger))
maxarc=float(max(np.max(x['combined_excess_arc_bound_mm_by_finger']) for x in bounds))
width=min(float(s['key_width_mm']) for s in read(P/'GENERATION_POLICY.json')['regions'])
maxstep=max(r['new_max_60fps_pad_step_mm_by_finger'])
pass_=r['saved_source_manifest_verified'] and r['total_q_engineering_domain']['pass_'] and r['max_correction_budget_ratio']<=1.02 and maxarc<=.005*width and maxstep<=.5*width and r['outside_window_change_deg']==0 and r['window_boundary_parity']
policy=dict(scope='RETROSPECTIVE_RECLASSIFICATION_OF_ONE_HASH_BOUND_SAVED_TRAJECTORY_ONLY',source_guard_checkpoint_sha256=r['source_guard_checkpoint_sha256'],source_solver_checkpoint_sha256=r['source_solver_checkpoint_sha256'],historical_FAIL_CLOSED_unchanged=True,classification='WARN_ACCEPTABLE' if pass_ else 'BLOCKING',budget_reclassified_as='MOTION_PRESERVATION_PREFERENCE',budget_checks_removed=False,actual_total_joint_domain_is_hard=True,actual_total_joint_domain_tolerance_deg=1e-7,source_time_root_keyboard_MIDI_audio_frozen_identity_hard=True,raw_angles_modified=False,limits=dict(max_correction_to_budget_ratio=1.02,max_combined_excess_pad_arc_as_white_key_fraction=.005,max_60fps_pad_step_as_white_key_fraction=.5),observed=dict(max_correction_to_budget_ratio=r['max_correction_budget_ratio'],combined_excess_rig_chain_arc_bound_mm=maxarc,white_key_width_mm=width,max_60fps_pad_step_mm=maxstep,rig_chain_arc_bounds=bounds,all62_sample_and14_extrema_assessed=True),higher_speed_and_acceleration='RETAINED_WARN_REQUIRES_FRAME_AND_HUMAN_ORIGINAL_SPEED_REVIEW',actual_skin_readback_correct_key_contact_and_no_dangerous_new_penetration_hard=True,obvious_visible_motion_or_contact_defect_hard_block=True,human_naturalness='HUMAN_PENDING_NO_AUTOMATIC_PASS',no_new_solver=True,no_rescaling_clipping_or_pose_patch=True,policy_locked_before_candidate=True,one_policy_decision_no_threshold_iteration=True)
dump('RECOVERY_POLICY.json',policy)
dump('POLICY_LOCK.json',dict(policy_sha256=sha(P/'RECOVERY_POLICY.json'),source_guard_sha256=sha(G/'SOLVER_AND_GUARD_DIAGNOSTICS.json'),source_solver_sha256=sha(G/'SOLVER_RETURN_CHECKPOINT.json'),source_parameters_sha256=sha(G/'GENERATION_POLICY.json'),source_pipeline_sha256=sha(G/'total_angle_pipeline.py'),classification_locked_before_recovery=True))
(P/'SAVED_TRAJECTORY_PROVENANCE.md').write_text(f'''# 保存轨迹来源：完整可信，可确定性恢复

唯一来源为Guard Fix轮的SOLVER_RETURN_CHECKPOINT.json与SOLVER_AND_GUARD_DIAGNOSTICS.json，solver nfev=20/status=2/success=True/ftol，原780个actual_delta参数及113支持点齐全。全部源交付manifest与生成锁哈希一致。

用原数值评价器只读重建，与保存827×20总角度逐位相同；actual_delta与reference之差也逐位相同。原R2 motion的root、旋转、键角、时间数组和源MIDI身份核验通过。重建没有调用任何优化器。

本轮恢复的是最新Guard Fix失败输出，绝不把它当作更早R3未保存的失败现场。原所有FAIL_CLOSED记录只读。

恢复采用原拟输出配方：原R2数组复制，仅在原活动窗口内写入保存总q的弧度；窗口外保留原弧度字节。没有缩放、裁剪、改root、改接触目标或手工补姿态。原生Blender动作回读验证仍是后续硬门禁。
''',encoding='utf8')
table='|指/关节DOF|采样记录|连续极值|最大超预算°|最大修正/预算|超限累计时长s|\n|---|---:|---:|---:|---:|---:|\n'
for x in r['groups']:table+=f"|{x['digit']} {x['joint']} {x['dof']}|{x['sample_violations']}|{x['continuous_extrema_violations']}|{x['max_excess_deg']:.9f}|{x['max_correction_budget_ratio']:.6f}|{x['total_excess_duration_sec']:.6f}|\n"
(P/'MOTION_BUDGET_RISK_ASSESSMENT.md').write_text('''# 全部预算违规风险复评

这是对已失败数值对象的**追溯性政策复评**，不是改写旧门禁或宣称旧轮事先已通过。

'''+table+f'''

62个DOF/时间记录（并非62个独立视频帧）及14条连续极值全部评估，合并超限时段和每条空间估算见PROVENANCE_AND_RISK_DATA.json。集中于食指/中指的5DOF；最大相对预算比例{r['max_correction_budget_ratio']:.6f}。

超预算部分的保守Rig链长角弧界：同一时刻同一指多个超出量相加，最大{maxarc:.6f}mm；不构造裁剪后的反事实轨迹。它只界定**预算额外溢出部分**，不能代替整个修正造成的手型改变。实际总修正的pad位移、skin marker位移与60fps步长另行记录。

白键宽约{width:.6f}mm；超预算空间界远小于键宽。对当前固定来源对象，一次锁定上限为预算比例≤1.02、超出部分角弧≤键宽0.5%。这两个条件不能推广成对所有曲目/所有预算超限的忽略。

整段新轨迹的速度/加速度峰值确实更高：速度峰{r['new_max_speed_deg_sec']:.3f}度/秒，R2约{r['R2_max_speed_deg_sec']:.3f}；加速度峰{r['new_max_accel_deg_sec2']:.3f}度/平方秒。最大单帧pad步长{maxstep:.3f}mm，原值和新增步长逐指列在数据文件。位置/速度没有不连续，但C1不保证C2；更高峰值保留独立WARN，必须在真实回读及正常原速视频中复核，不能以微小预算超限掩盖。

这轮预算偏差分类为{policy['classification']}，前提是总工程域、真实键身份与接触、音频时序、回读一致、无危险新穿入及无明显可见运动异常继续通过硬门禁。没有自动填写Human自然度PASS。
''',encoding='utf8')
(P/'ENGINEERING_GATE_CLASSIFICATION.md').write_text(f'''# 工程门禁与预算分类：{policy['classification']}

HARD_ENGINEERING_SAFETY_CONSTRAINT：原总关节工程域及1e-7度检查、原root/时钟/MIDI/指法/键角/音频、实际目标键身份、严重持键失配、危险新穿入、明显运动跳变、冻结资产与保存重开回读一致。全部保持阻断，不因预算复评放宽。

MOTION_PRESERVATION_PREFERENCE：仅当前来源哈希绑定对象的actual_delta相对R2预算偏差。62条采样/14条连续极值保留，依据有限角弧、比例与时段评估，一次分类WARN。没有删除预算检查，没有改求解参数、缩放修正或裁剪角度。

RECOVERY_POLICY.json和POLICY_LOCK.json在任何motion/Blender候选/视频产生前写入。已知更高速度/加速度独立记录WARN，明显可见异常仍然硬阻断。该政策是本轮Human明确授权的追溯复评，原Guard Fix和原R3 FAIL_CLOSED完全保留。

适用范围只有本次source_solver/source_guard SHA所定义的轨迹，不推广为一般容差。政策锁定后不继续调整阈值。若真实回读或视觉预检失败，停止，不重算或修补。
''',encoding='utf8')
print('RETROSPECTIVE_POLICY_LOCKED',policy['classification'],'rig chain excess bound mm',maxarc,'ratio',r['max_correction_budget_ratio'],'framepad',maxstep,flush=True)
if not pass_:raise RuntimeError('BLOCKING_RISK_STOP_BEFORE_RECOVERY')
