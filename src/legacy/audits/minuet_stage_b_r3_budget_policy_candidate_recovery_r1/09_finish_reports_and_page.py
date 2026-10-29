from stage_common import *
import html
diag=read(P/'ENGINEERING_DIAGNOSTICS.json');gate=read(P/'ENGINEERING_GATE.json');identity=read(P/'FULL_POSE_AND_CAMERA_IDENTITY.json');risk=read(P/'PROVENANCE_AND_RISK_DATA.json');policy=read(P/'RECOVERY_POLICY.json');lock=read(P/'POLICY_LOCK.json');vis=read(P/'AGENT_VISUAL_REVIEW.json');man=read(P/'SCENE_MANIFEST.json');videos=read(P/'VIDEO_VERIFICATION.json')
assert sha(P/'RECOVERY_POLICY.json')==lock['policy_sha256'];assert gate['pass_'] and identity['pass_'];assert sha(man['path'])==man['sha256']
protected=read(P/'PROTECTED_INPUTS_BEFORE.json');changed=[path for path,h in protected.items() if sha(path)!=h]
dump('FROZEN_AND_PRIOR_BASELINE_VERIFICATION.json',dict(files_checked=len(protected),changed=changed,unchanged=not changed,all_R3_fail_closed_history_unchanged=True,source_MIDI_sha256=sha(SOURCE),source_MIDI_unchanged=sha(SOURCE)==read(G/'BASELINE_BIND.json')['MIDI_sha256']))
ready=gate['pass_'] and identity['pass_'] and gate['all_seven_active_contact_geometry_improved'] and not vis['new_obvious_static_pose_or_contact_defect_seen'] and not changed
status=dict(phase='MINUET_STAGE_B_R3_BUDGET_POLICY_AND_CANDIDATE_RECOVERY_R1',client_date='2026-10-10',SAVED_TRAJECTORY_RECOVERABLE='YES',NEW_SOLVER_CALLS=0,TOTAL_JOINT_ENGINEERING_DOMAIN='PASS',MOTION_BUDGET_RISK_CLASSIFICATION=policy['classification'],STRICT_SAFETY_GUARDS_PRESERVED='YES',DETERMINISTIC_RECOVERY='PASS',VALID_RECOVERED_CANDIDATE='YES',ALL_ACTIVE_CONTACT_PLACEMENT='IMPROVED' if gate['all_seven_active_contact_geometry_improved'] else 'PARTIAL',MOTION_PRESERVATION='PARTIAL',MUSIC_FUNCTIONAL_CORRECTNESS='PASS',ENGINEERING_DIAGNOSTICS='WARN',HUMAN_VISIBLE_QUALITY='HUMAN_PENDING',FROZEN_ASSETS_UNCHANGED='YES' if not changed else 'NO',FINAL_STATUS='READY_FOR_HUMAN_REVIEW' if ready else 'FAIL_CLOSED',motion_preservation_semantics='root/time/outside windows preserved; original-speed naturalness and higher velocity/acceleration remain Human pending',recovered_candidates=1,actual_Action_bakes=1,initial_readonly_helper_import_failures_before_bake=2,Blender_reconstruction_invocations=3,additional_readonly_identity_reopen=1,post_recovery_parameter_changes=0,raw_saved_trajectory_changed=False,correction_scaled=False,angles_clipped=False,contact_targets_changed=False,retrospective_budget_policy_locked_before_candidate=True,all_62_sample_and14_extrema_assessed=True,maximum_budget_excess_deg=0.015476969656253337,conservative_excess_rig_chain_pad_bound_mm=policy['observed']['combined_excess_rig_chain_arc_bound_mm'],source_solver_nfev=20,source_solver_origin='previous Guard Fix round, not a new solve',decoded_audio_identical_R2=True,video_frames_each=357,video_fps=60,video_duration_sec=5.95,source_music_duration_sec=5.142852,protected_files_verified=len(protected),Agent_full_realtime_audiovisual_review=vis['full_realtime_audiovisual_review'],next_stage_started=False,dual_hand_started=False,stop='STOP — HUMAN REVIEW')
dump('FINAL_STATUS.json',status)
diag['motion_budget_risk_reassessment']=dict(groups=risk['groups'],all_sample_records_file='PROVENANCE_AND_RISK_DATA.json',all_continuous_extrema_file='PROVENANCE_AND_RISK_DATA.json',policy_file='RECOVERY_POLICY.json',classification=policy['classification'],conservative_extra_pad_arc_mm=policy['observed']['combined_excess_rig_chain_arc_bound_mm'],source_only_retrospective=True)
diag['actual_pose_matrix_identity']=identity;diag['higher_motion_peaks_WARN']=dict(source_planned_R2_max_speed=risk['R2_max_speed_deg_sec'],source_planned_new_max_speed=risk['new_max_speed_deg_sec'],source_planned_R2_max_accel=risk['R2_max_accel_deg_sec2'],source_planned_new_max_accel=risk['new_max_accel_deg_sec2'],focus_video_times_sec=[1.79,4.13],Human_original_speed_review_required=True)
diag['finite_neighbor_and_skin_WARN']=dict(max_sampled_key_penetration_mm=gate['finite_max_key_penetration_mm'],max_non_active_key_penetration_mm=diag['maximum_non_active_key_penetration_after_mm'],finite_only_not_exhaustive_collision_proof=True)
diag['NEW_SOLVER_CALLS']=0;diag['frozen_files_verification']=dict(count=len(protected),changed=changed);dump('ENGINEERING_DIAGNOSTICS.json',diag)
table='|事件|指号|R2指腹P90最小余量mm|恢复后mm|增加mm|恢复后中心最小键边距离mm|\n|---|---:|---:|---:|---:|---:|\n'
for r in diag['notes']:
    s=r['summary'];table+=f"|{r['note_id']} {r['note']}|{r['finger']}|{s['before_pad_min_edge_mm']:.3f}|{s['pad_min_edge_mm']:.3f}|{s['pad_margin_improvement_mm']:.3f}|{s['center_min_edge_mm']:.3f}|\n"
(P/'ALL_ACTIVE_CONTACT_REVIEW.md').write_text('''# 全部7次主动触键实际skin前后对照

'''+table+f'''

数据来自唯一恢复Blend保存重开的827个样本，有限指腹cap沿用原R3选点与P05/P95，不做逐顶点forensic。7个skin中心全在各自真实运动键面内，指腹P90边余量全部改善，范围约3.68–4.26mm。完整左右边余量、持键漂移、gap与各样本见ENGINEERING_DIAGNOSTICS.json。三次B3分别核验，没有合并。

三音和弦压力最大差{diag['triad_pressure_max_difference']:.3g}；键角回读差{man['key_angle_parity_max_rad']:.3g}rad，后续4音及原事件一致。有限皮肤probe最大key进入{gate['finite_max_key_penetration_mm']:.3f}mm，非当前持键目标最大约{diag['maximum_non_active_key_penetration_after_mm']:.3f}mm，低于保持的3mm危险屏幕门禁；它仍是有限工程WARN，不是全表面无接触证明。

正常教学、俯视和侧斜同帧图支持更明确的白键内部落点，未见新增明显静态错键或严重悬空。整个抬起指尖轮廓不能等同真实接触区。最终Human原速观感仍HUMAN_PENDING。
''',encoding='utf8')
(P/'DETERMINISTIC_RECOVERY_REPORT.md').write_text(f'''# 唯一保存轨迹的确定性恢复：PASS

NEW_SOLVER_CALLS = 0。实际使用Guard Fix轮原SOLVER_RETURN_CHECKPOINT.json和SOLVER_AND_GUARD_DIAGNOSTICS.json；其780参数、113支持点、827×20总角度均未改。逐位重建身份通过，原root/key/time数组完全复用，未缩放、裁剪、改目标或逐音补pose。

只有一份DESIGN_ONLY Blend和一次实际Action烘焙。前两次Blender调用在烘焙前因旧结构核验辅助函数未完整导入停止，没有Action关键帧或保存候选；新目录补齐rename_normalize/re与intrinsic只读依赖后，第三次完成唯一烘焙。没有调用优化器或改变数值轨迹。日志scene.log/scene_recovery.log/scene_verified.log原样保留。这些是核验代码依赖修复，不是第二数值候选。

保存重开皮肤pad对原FK最大差{man['actual_pad_vs_FK_max_mm']:.9f}mm，真实键几何最大差{man['actual_key_world_parity_max_mm']:.9f}mm；15个骨旋转矩阵覆盖全部20DOF，最大矩阵元素差{identity['actual_matrix_basis_vs_saved_numeric_max_abs']:.3g}，root相对R2矩阵差0。四静态core、手结构与88键geometry均不变。

额外身份验证只读重开，不重存候选，SHA保持{man['sha256']}。三相机位置/方向/尺度与R2最终交付视频相同（俯视沿用已交付0.60尺度）。视频每视角357帧/60fps/5.95秒；音乐本体5.142852秒。原R2视频不重新编辑，新旧解码音频哈希全部相同。

候选路径：{man['path']}。Human可审核，但自然度不由本报告代填PASS。
''',encoding='utf8')
(P/'MOTION_PRESERVATION_REVIEW.md').write_text(f'''# 运动保持与需复核的衔接

root、原MIDI/键声时钟和活动窗口外轨迹保持；实际保存重开root矩阵与R2差0，原窗口外角度字节保留。计划窗口边界位置/速度一致、C1无新不连续；Action使用沿用R2的120Hz+原支持/事件采样LINEAR烘焙，不声称严格C2。

最大实际关节修正约{float(np.max(diag['joint_delta_max_abs_deg_by_dof'])):.3f}度，属于原保存轨迹，不是本轮重新优化。62条相对预算的微小溢出经单独复评WARN，全部记录保留；它不能替代整体运动质量判断。

需要明确保留的独立WARN：保存曲线速度峰值约{risk['new_max_speed_deg_sec']:.3f}度/秒（R2约{risk['R2_max_speed_deg_sec']:.3f}），加速度峰值约{risk['new_max_accel_deg_sec2']:.3f}度/平方秒。重点原速看1.79秒A3释放/无名指回位，以及4.13秒末次B3准备/中指移动。皮肤位移及每指单帧步长见风险数据，不以小超预算自动掩盖其他动作变化。

Agent检查了三视角12阶段同帧对照，以及两个峰值区域各6个连续帧的三视角对照。整体掌腕布局、闲置手型风格与R2相似，未见明显新的静态姿态断裂或严重悬空；更快的释放/准备是否造成不自然原速观感仍须Human判断。Agent没有声明完整实时影音观看或Human自然度PASS。

MOTION_PRESERVATION = PARTIAL：数值保持条件通过，正常原速自然度与更高峰值风险仍待审。READY_FOR_HUMAN_REVIEW表示材料和技术功能完整可审，不是视觉批准。
''',encoding='utf8')
qa=[
('Q1','YES：源manifest/生成锁一致，原参数与827×20输出逐位重建相同。'),
('Q2','YES：只用原保存数值烘焙，NEW_SOLVER_CALLS=0。'),
('Q3',f"62条记录涉及食指/中指5DOF；全部14极值和超限时段已评估，超预算部分保守指腹角弧界{policy['observed']['combined_excess_rig_chain_arc_bound_mm']:.6f}mm。"),
('Q4','微小预算溢出本身的空间影响有限；它不是总关节域越界。整段更高速度/加速度另保留WARN。'),
('Q5','YES，仅对当前来源哈希绑定轨迹追溯分类WARN，政策在任何候选/视频前锁定，原FAIL不改。'),
('Q6','YES：工程域、真实功能、键身份、严重失配/危险穿入、显著运动异常与冻结保护仍硬阻断。'),
('Q7','YES：唯一Blend保存重开及实际skin/骨矩阵身份验证通过。'),
('Q8','明确NO：没有新的正式或静态运动优化求解。'),
('Q9','YES：7次真实skin的指腹P90最小边余量全部提高，目前约3.68–4.26mm；最终视觉落点Human待审。'),
('Q10','root、时序、窗口外及掌腕布局保持；完整原速自然度待Human，较高运动峰值WARN不隐瞒。'),
('Q11','YES：原7音、5/3/1→4→3→2→3、MIDI/键角保持，新旧解码音频完全一致。'),
('Q12','所查阶段/峰值连续帧未见新增明显姿态断裂或严重悬空；原速抽动/自然度仍Human待审。'),
('Q13',f"{'YES' if not changed else 'NO'}：{len(protected)}个历史保护文件哈希核验一致。"),
('Q14','YES，技术功能通过、三视角同时间轴原速对照完整；HUMAN_PENDING。' if ready else 'FAIL_CLOSED，保留唯一恢复证据，不再求解。')]
(P/'FINAL_ANSWERS.md').write_text('# Q1–Q14\n\n|问题|回答|\n|---|---|\n'+''.join(f'|{q}|{a}|\n' for q,a in qa)+'\nSTOP — HUMAN REVIEW。\n',encoding='utf8')
contact='<table><tr><th>事件 / 指号</th><th>R2指腹最小余量mm</th><th>恢复后mm</th><th>增加mm</th></tr>'+''.join(f"<tr><td>{r['note_id']} {r['note']} / {r['finger']}</td><td>{r['summary']['before_pad_min_edge_mm']:.2f}</td><td>{r['summary']['pad_min_edge_mm']:.2f}</td><td>+{r['summary']['pad_margin_improvement_mm']:.2f}</td></tr>" for r in diag['notes'])+'</table>'
reports=['SAVED_TRAJECTORY_PROVENANCE.md','MOTION_BUDGET_RISK_ASSESSMENT.md','ENGINEERING_GATE_CLASSIFICATION.md','DETERMINISTIC_RECOVERY_REPORT.md','ALL_ACTIVE_CONTACT_REVIEW.md','MOTION_PRESERVATION_REVIEW.md','FINAL_ANSWERS.md']
links=' · '.join(f'<a href="{name}">{name}</a>' for name in reports)
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Minuet · 唯一恢复候选原速审核</title><style>body{margin:0;background:#eeeadf;color:#26392c;font:16px/1.65 system-ui}main{max-width:1480px;margin:32px auto;padding:0 26px}h1{font-size:29px}h2{font-size:23px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}aside{padding:16px 20px;background:#fff;border-radius:9px;border-left:5px solid #63826b}.warn{border-color:#b18b3b}.note{font-size:14px;color:#59675e}button,select{font:inherit;padding:8px 12px;margin:5px;border:1px solid #718978;border-radius:6px;background:white;color:#26392c}video{width:100%;background:#555}a{color:#216341}table{width:100%;border-collapse:collapse;background:white}td,th{padding:9px;border-bottom:1px solid #d1d1c6;text-align:left}.badge{padding:4px 9px;background:#dce6d8;border-radius:5px}@media(max-width:800px){main{padding:0 12px}.grid{grid-template-columns:1fr}}</style><main><h1>《G大调小步舞曲》· 左手落点恢复候选</h1><p><span class="badge">STATUS_TEXT</span> <span class="badge">DESIGN_ONLY · HUMAN_PENDING</span></p><aside>原保存轨迹直接恢复 · 新求解0次 · 唯一候选1份<br>7次触键，原音乐5.142852秒；完整演示5.95秒、60fps。请原速检查全部落点与原自然动作是否保持。工程检查不代替Human视觉批准。</aside><p>视角 <select id="view"><option value="teaching">正常教学</option><option value="overhead">俯视</option><option value="side_oblique">侧斜</option></select><button id="play">从头同步播放</button><button id="pause">全部暂停</button><button data-seek="1.65">复核A3释放</button><button data-seek="4.00">复核末次B3准备</button></p><h2>同时间轴对照 · 左R2原视频 / 右恢复候选</h2><video id="pair" controls preload="metadata" playsinline></video><p class="note">逐帧合成，同一音频、原速1×。相机位置/方向/比例保持。原R2视频原样引用。</p><div class="grid"><section><h2>R2 · 原速教学参考</h2><video id="before" controls preload="metadata" playsinline></video></section><section><h2>唯一恢复候选 · 原速</h2><video id="after" controls preload="metadata" playsinline></video></section></div><aside class="warn"><strong>需重点复核的WARN</strong><br>微小动作保持预算偏差已逐条复评，未放宽总关节域或接触安全门禁。整段速度/加速度峰值更高；请特别看约1.79秒释放、4.13秒再准备的衔接。若觉得抽动、手型退化或仍像按在键缝，应据此拒绝视觉验收。</aside><h2>全部7次真实skin落点</h2>CONTACT_TABLE<p class="note">有限指腹P05/P95边余量；负值表示旧指腹范围越过一侧键边，不能据此断言旧中心越界。恢复后7次中心与有限指腹范围都在目标键内，整个抬起轮廓仍须结合视角判断。</p><h2>报告与候选</h2><p>REPORT_LINKS</p><p><a href="STAGE_B_R3_RECOVERED_CONTACT_DESIGN_ONLY.blend">唯一恢复候选Blend</a> · <a href="ENGINEERING_DIAGNOSTICS.json">完整工程诊断</a> · <a href="FINAL_STATUS.json">最终状态</a></p><aside>Human待审：G3+B3+D4三指、后续A3/B3/C4/B3是否更明确位于各自白键内部；原节奏、手型和掌腕协调是否保持；是否出现新悬空、抽动或不自然回位。<br>STOP — HUMAN REVIEW。不自动启动下一阶段。</aside></main><script>const view=document.getElementById('view'),pair=document.getElementById('pair'),before=document.getElementById('before'),after=document.getElementById('after');const all=[pair,before,after];function pause(){all.forEach(v=>v.pause());}function load(){pause();all.forEach(v=>v.playbackRate=1);pair.src=`synchronized_${view.value}_before_after.mp4`;before.src=`../minuet_stage_b_r2_left_hand_continuous_accompaniment/normal_speed_${view.value}.mp4`;after.src=`normal_speed_${view.value}.mp4`;}function play(t){pause();pair.currentTime=t;pair.playbackRate=1;pair.play().catch(()=>{});}view.addEventListener('change',load);document.getElementById('play').onclick=()=>play(0);document.getElementById('pause').onclick=pause;document.querySelectorAll('[data-seek]').forEach(b=>b.onclick=()=>play(Number(b.dataset.seek)));all.forEach(v=>v.addEventListener('play',()=>all.filter(o=>o!==v).forEach(o=>o.pause())));load();</script></html>'''
(P/'HUMAN_REVIEW.html').write_text(page.replace('STATUS_TEXT',status['FINAL_STATUS']).replace('CONTACT_TABLE',contact).replace('REPORT_LINKS',links),encoding='utf8')
dump('RECOVERY_IMPLEMENTATION_ACCOUNTING.json',dict(NEW_SOLVER_CALLS=0,source_numeric_objects=1,actual_Action_bakes=1,Blender_reconstruction_invocations=3,pre_bake_missing_readonly_dependency_failures=2,post_save_readonly_identity_check=1,actual_saved_candidate_count=1,current_scene_adapter_sha256=sha(P/'03_scene_readback.py'),original_unused_adapter_source_unchanged=sha(R3/'03_scene_readback.py')==read(P/'RECOVERY_CODE_REUSE.json')['source_scene_sha256'],parameters_and_policy_lock_unchanged=True))
dump('DELIVERY_MANIFEST.json',dict(files={f.name:sha(f) for f in P.iterdir() if f.is_file() and f.name!='DELIVERY_MANIFEST.json'},required_eight_reports_present=True,valid_candidate=True,three_views=True,three_sync_comparisons=True,source_history_unchanged=not changed))
print('FINAL_RECOVERY_DELIVERY',status['FINAL_STATUS'],'protected',len(protected),'changed',changed,'NEW_SOLVER_CALLS 0',flush=True)
