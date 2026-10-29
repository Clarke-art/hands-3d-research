"""Report saved failed output. No solve, animation save, clipping or retry."""
from total_angle_pipeline import *
assert (P/'CANDIDATE_ATTEMPT.json').exists()
assert read(P/'CANDIDATE_ATTEMPT.json')['formal_dynamic_attempts']==1
assert not (P/'motion.npz').exists() and not list(P.glob('*.blend'))
d=read(P/'SOLVER_AND_GUARD_DIAGNOSTICS.json');returned=read(P/'SOLVER_RETURN_CHECKPOINT.json');meta=d['solver'];cert=d['continuous_polynomial_certificate'];pre=read(P/'PREGENERATION_VALIDATION.json');p=TotalAnglePipeline()
raw=np.array(returned['raw_unknown_actual_delta_deg']);curve=p.curve(raw)
assert not d['valid_output'] and cert['domain']['pass_'] and not cert['actual_delta_budget']['pass_']
stage_masks=[]
for s in d['stages']:
    q=np.array(s['q_deg']);lo=np.array(s['lower_deg']);hi=np.array(s['upper_deg']);mask=(~np.isfinite(q))|(q<lo-s['tolerance_deg'])|(q>hi+s['tolerance_deg'])
    stored=np.zeros_like(mask)
    for r in s['violations']:stored[r['sample_index'],r['flat_index']]=True
    assert np.array_equal(stored,mask)
    stage_masks.append(dict(stage=s['stage'],shape=list(mask.shape),violation_mask=mask,violation_count=int(mask.sum()),matches_complete_sparse_mask_saved_before_guard=True))
dump('OUTPUT_VIOLATION_MASKS.json',dict(stages=stage_masks,origin='computed_read_only_from_complete_pre_guard_checkpoint',new_solve=False))
worst=max(cert['actual_delta_budget']['violations'],key=lambda r:r['excess_deg']);j=worst['flat_index'];t=worst['time_sec'];identity=rec.joint_identities()[j]
summary=dict(current_round=True,historical_R3_original_failed_trajectory_still_unavailable=True,
    solver={k:v for k,v in meta.items() if k!='active_mask'},total_engineering_domain_pass=True,total_engineering_domain_violation_count=0,
    actual_budget_compliance=False,max_continuous_actual_budget_excess_deg=cert['actual_delta_budget']['max_excess_deg'],
    worst_current_actual_budget_violation={**worst,**identity,'reference_total_angle_deg':float(p.refcurve(t)[j]),'actual_total_angle_deg':float(curve(t)[j]),'engineering_total_lower_deg':float(p.low[j]),'engineering_total_upper_deg':float(p.high[j]),'value_is_actual_correction_not_absolute_joint_angle':True},
    output_budget_violation_count=next(s['violation_count'] for s in d['stages'] if s['stage']=='ACTUAL_OUTPUT_CORRECTION_BUDGET'),
    continuous_budget_extrema_violations=len(cert['actual_delta_budget']['violations']),
    outside_window_change_deg=cert['outside_window_max_change_deg'],C1_position_jump_deg=cert['C1_position_jump_max_deg'],C1_velocity_jump_deg_sec=cert['C1_velocity_jump_max_deg_sec'],
    boundary_values_and_velocities_preserved=cert['boundary_position_and_velocity_preserved'],guard_failure_reason='actual correction budget exceeded; total joint engineering domain PASS',
    saved_valid_candidate=False,no_second_attempt=True)
dump('FAILED_OUTPUT_SUMMARY.json',summary)
qout=np.array(d['final_total_q_deg']);delta=np.array(d['final_actual_delta_deg']);reg=np.linspace(0,p.knots[-1],715)
v=curve.derivative()(reg);v0=p.refcurve.derivative()(reg);acc=curve.derivative(2)(reg);acc0=p.refcurve.derivative(2)(reg)
motion=dict(origin='numeric_failed_output_only_not_Blender_readback',root_original_arrays_unmodified=True,root_optimized=False,events_and_key_angles_unmodified=True,actual_joint_delta_max_abs_deg_by_dof=np.max(abs(delta),axis=0).reshape(5,4),planned_window_outside_change_deg=cert['outside_window_max_change_deg'],planned_C1_position_jump_deg=cert['C1_position_jump_max_deg'],planned_C1_velocity_jump_deg_sec=cert['C1_velocity_jump_max_deg_sec'],planned_R2_max_joint_speed_deg_sec=float(np.max(abs(v0))),planned_new_max_joint_speed_deg_sec=float(np.max(abs(v))),planned_R2_max_joint_accel_deg_sec2=float(np.max(abs(acc0))),planned_new_max_joint_accel_deg_sec2=float(np.max(abs(acc))),new_visible_motion_anomalies='UNKNOWN_NO_VIDEO_OR_ACTION',strict_actual_budget_pass=False)
dump('MOTION_PRESERVATION_DIAGNOSTICS.json',motion)
protected=read(P/'PROTECTED_INPUTS_BEFORE.json');changed=[path for path,h in protected.items() if sha(path)!=h]
dump('FROZEN_AND_PRIOR_BASELINE_VERIFICATION.json',dict(files_checked=len(protected),changed=changed,unchanged=not changed,includes_stage_A_R2_B1_B2_original_R3_and_failure_isolation=True,source_MIDI_unchanged=sha(SOURCE)==read(P/'BASELINE_BIND.json')['MIDI_sha256']))
old=read(R3/'R2_ALL_ACTIVE_PLACEMENT.json')
table='|事件|指号|R2中心最小边余量mm|R2有限指腹P90最小余量mm|本轮动态回读|\n|---|---:|---:|---:|---|\n'
for r in old['notes']:table+=f"|{r['note_id']} {r['note']}|{r['finger']}|{r['summary']['center_min_edge_mm']:.3f}|{r['summary']['pad_min_edge_mm']:.3f}|未进行，输出预算guard失败|\n"
(P/'ALL_ACTIVE_CONTACT_PLACEMENT.md').write_text('''# 全部7次主动触键：动态改善未验收

本轮没有把目标缩小到G3；7个原音符、指法、MIDI、通用安全区域与原R3相同。三个B3事件单独保留。

'''+table+'''

生成前10个同actual预算静态pose覆盖全部7个事件，有限指腹余量约3.94–4.77mm。它是生成前可达性证据，不是本轮动态触键前后对照。

正式输出虽通过全部总角度工程域检查，但实际修正预算guard失败，按授权止损，没有写motion.npz、Blender Action或候选，没有进行skin动态回读或渲染。因此全部7次实际触键改善、和弦三指共同触键、后续单音、有限邻键风险均为本轮动态UNVERIFIED；不得以数值终止或静态余量填写PASS。

没有新视频或虚假新旧对照。原R2素材与历史验收不变。
''',encoding='utf8')
(P/'MOTION_PRESERVATION_REPORT.md').write_text(f'''# 运动保持：数值部分通过，有效候选未交付

保存的失败数值输出root未优化，原R2 root、键角和事件数组没有改写。窗口外总q变化{cert['outside_window_max_change_deg']:.3g}度；全部窗口边界位置与速度差0。计划曲线C1位置跳变最大{cert['C1_position_jump_max_deg']:.3g}度、速度跳变最大{cert['C1_velocity_jump_max_deg_sec']:.3g}度/秒。

失败输出每DOF实际修正最大幅度（度，行按指号1..5，列为屈曲1/2/3及基部横展）：

```json
{json.dumps(motion['actual_joint_delta_max_abs_deg_by_dof'].tolist(),indent=2)}
```

计划最大关节速度R2/新输出约{motion['planned_R2_max_joint_speed_deg_sec']:.3f}/{motion['planned_new_max_joint_speed_deg_sec']:.3f}度/秒；计划最大加速度约{motion['planned_R2_max_joint_accel_deg_sec2']:.3f}/{motion['planned_new_max_joint_accel_deg_sec2']:.3f}度/平方秒。数据来自已保存失败数值的只读评价，无新求解，不证明实际视频自然度。

严格实际修正预算失败，最大超预算{worst['excess_deg']:.9f}度；它是相对于R2的delta预算超出，不是冻结Rig总角度超限。MOTION_PRESERVATION=PARTIAL：root、窗口外、时序与C1部分通过，实际修正预算不通过，Human动作质量未评估。

没有Action或视频，新增错键、悬空、钩爪或可见跳变不能判定存在/不存在。没有以关闭guard、扩大预算、裁剪输出或重算补救。STOP — HUMAN REVIEW。
''',encoding='utf8')
status=dict(phase='MINUET_STAGE_B_R3_GUARD_FIX_AND_CONTACT_VALIDATION_R1',client_date='2026-10-10',OUTPUT_JOINT_DOMAIN_GUARANTEE='PASS',STATIC_DYNAMIC_BUDGET_CONSISTENCY='PASS',ZERO_CORRECTION_R2_PARITY='PASS',STRICT_GUARD_PRESERVED='YES',SOLVER_TERMINATION_RECORDED='YES',FORMAL_DYNAMIC_ATTEMPTS=1,VALID_DYNAMIC_CANDIDATE='NO',GLOBAL_CONTACT_PLACEMENT='NOT_EVALUATED',MOTION_PRESERVATION='PARTIAL',MUSIC_FUNCTIONAL_CORRECTNESS='UNKNOWN',ENGINEERING_DIAGNOSTICS='FAIL',HUMAN_VISIBLE_QUALITY='HUMAN_PENDING',FROZEN_ASSETS_UNCHANGED='YES' if not changed else 'NO',FINAL_STATUS='FAIL_CLOSED',ACTUAL_CORRECTION_BUDGET_COMPLIANCE='FAIL',budget_consistency_semantics='same actual-delta quantity and same budget in static/formal checks; consistency PASS does not mean final budget compliance PASS',solver_nfev=meta['nfev'],solver_njev=meta['njev'],solver_status=meta['status'],solver_success=meta['success'],solver_message=meta['message'],solver_limit_reached=meta['limit_reached'],residual_calls=meta['residual_calls'],total_engineering_domain_violation_count=0,maximum_actual_budget_excess_deg=worst['excess_deg'],blocking_reason='Interpolated actual delta exceeded locked motion-preservation budget; strict composite output guard rejected',complete_failed_numeric_trajectory_saved=True,historical_original_R3_failure_not_reconstructed=True,new_motion_npz=False,new_Blender_candidate=False,new_videos=False,new_synchronized_comparison=False,post_solve_parameter_changes=0,second_formal_solve=False,output_angle_clipping=False,root_optimized=False,per_note_manual_pose_patch=False,contact_region_unchanged=True,static_actual_pose_prechecks=10,protected_files_verified=len(protected),changed_protected_files=changed,next_stage_started=False,dual_hand_started=False,stop='STOP — HUMAN REVIEW')
dump('FINAL_STATUS.json',status)
qa=[
('Q1','总关节工程域保障PASS：113个支持点、827个输出与事件/窗口边界均合法，连续112段×20DOF多项式极值无总角度超限。实际delta预算是另一个失败门。'),
('Q2','PASS：静态与正式共用actual_delta_deg和相同预算；最终插值delta仍小幅超预算，不能混称预算已满足。'),
('Q3',f"PASS：零修正角度最大差{pre['zero_correction_max_abs_deg']:.3g}度，root/原时钟与窗口外保持。"),
('Q4','YES：保留原1e-7度工程域guard，无输出裁剪、放宽域或预算。'),
('Q5',f"完成唯一正式求解；nfev={meta['nfev']}，njev={meta['njev']}，status={meta['status']}，success={meta['success']}，ftol终止；未达到100次上限。数值成功不等于验收PASS。"),
('Q6','YES：返回元数据/支持点/raw actual参数立即保存；guard前保存全部输出、角度、边界、完整稀疏违规mask及连续极值。另有可复核的稠密mask文件。'),
('Q7','NO：严格实际delta预算检查拒绝，未保存有效motion或Blender候选。'),
('Q8','NOT_EVALUATED：全部7次原落点和新静态预检记录完整；未进行新动态skin回读，不宣称已改善。'),
('Q9','root、原事件和窗口外数值保持；计划C1通过；预算超出导致运动保持PARTIAL，原自然度无法做视频判断。'),
('Q10','总角度无越界、计划曲线无C1跳变；实际新错键/悬空/不自然观感UNKNOWN，没有有效Action/视频。'),
('Q11','无第二次正式优化、逐音pose补丁、输出裁剪或生成后调参；接触规则沿用通用几何公式。'),
('Q12',f"{'YES' if not changed else 'NO'}：{len(protected)}个历史保护文件哈希一致。"),
('Q13','NO：没有有效候选可提交原速视觉验收；只交付完整首次失败证据，FAIL_CLOSED后停止。')]
(P/'IMPLEMENTATION_REPORT.md').write_text(f'''# 本轮实现与实际结果：FAIL_CLOSED

关节总角度域保障、actual修正预算表示和失败记录管线已修复并通过生成前门禁。唯一正式求解数值终止success=True，但最终实际delta小幅超过锁定运动保持预算，严格复合guard拒绝。没有修改参数重试，没有裁剪，也没有motion.npz/Blender/新视频。

## 两种边界必须区分

总关节角度工程域：PASS，超限0。实际修正预算：FAIL，输出采样有{summary['output_budget_violation_count']}个违规DOF采样；连续多项式有{summary['continuous_budget_extrema_violations']}条记录。最大连续违规是本轮左手中指MCP屈曲修正，在演示时钟t={t:.9f}s（音乐时钟t={t-.35:.9f}s），actual_delta={worst['actual_deg']:.9f}°，锁定预算±{worst['upper_deg']:.9f}°，超出{worst['excess_deg']:.9f}°。该时刻总关节角度={summary['worst_current_actual_budget_violation']['actual_total_angle_deg']:.9f}°，仍在0..32°工程域内。

这是本轮保存的失败证据，不能用于冒充原R3未保存的违规现场。原R3具体关节/时刻仍UNKNOWN。

soft budget和Bernstein控制点惩罚不能保证优化器一定把所有delta留在预算内；本轮最终严格guard检出了剩余误差。没有把约0.01548°按“不可见小偏差”擅自放宽成PASS，也未因数值success宣布产品通过。

## 实际执行

10次有限静态pose预检，0静态Action；一次策略锁定；一次正式求解。正式nfev={meta['nfev']}、njev={meta['njev']}、status={meta['status']}、message={meta['message']}、callback调用{meta['residual_calls']}；这些数量分开记录，未达到100次上限。raw actual参数、全部支持点和输出在guard之前保存，因此本轮没有再丢失现场。

所有新增代码与报告在独立目录，原R3、诊断目录与所有冻结历史文件只读。guard通过之前不写有效motion，预算guard失败后没有进行Blender回读或渲染。HUMAN_REVIEW.html、新候选、三视角与同期视频未生成，不列为已交付。

|问题|回答|
|---|---|
'''+''.join(f'|{q}|{a}|\n' for q,a in qa)+'''

交付七个要求报告/状态文件，附完整返回checkpoint、guard checkpoint、稠密mask和失败摘要。推荐或后续修复未自动执行。STOP — HUMAN REVIEW。
''',encoding='utf8')
(P/'FINAL_ANSWERS.md').write_text('# Q1–Q13\n\n|问题|回答|\n|---|---|\n'+''.join(f'|{q}|{a}|\n' for q,a in qa)+'\nSTOP — HUMAN REVIEW。\n',encoding='utf8')
dump('DELIVERY_MANIFEST.json',dict(files={f.name:sha(f) for f in P.iterdir() if f.is_file() and f.name!='DELIVERY_MANIFEST.json'},required_seven_reports_present=True,valid_candidate=False,videos=False,Human_review_page=False,no_second_attempt=True))
print('FAILURE_DELIVERY_COMPLETE','protected',len(protected),'changed',changed,'maxbudget',worst['excess_deg'],'nfev',meta['nfev'],flush=True)
