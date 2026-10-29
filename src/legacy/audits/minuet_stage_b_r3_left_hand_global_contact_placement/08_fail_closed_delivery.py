"""Deliver first-attempt failure evidence. Never solve, bake, or render R3."""
from stage_common import *
import shutil,subprocess,html
attempt=read(P/'CANDIDATE_ATTEMPT.json');assert attempt['attempt']==1
assert not (P/'motion.npz').exists() and not list(P.glob('*.blend'))
shutil.copyfile(P/'CANDIDATE_ATTEMPT.json',P/'CANDIDATE_ATTEMPT_ORIGINAL_START.json')
dump('CANDIDATE_ATTEMPT.json',{**attempt,'status':'FAILED_PRE_SAVE_JOINT_DOMAIN_GUARD','saved_dynamic_candidates':0,'second_attempt':False,'restarts':0,'exit_code':1})
lock=read(P/'GENERATION_LOCK.json');assert all(sha(P/n)==h for n,h in lock['scripts'].items());assert sha(P/'GENERATION_POLICY.json')==lock['policy_sha256']
audit=read(P/'R2_ALL_ACTIVE_PLACEMENT.json');stat=read(P/'STATIC_REACHABILITY.json');pol=read(P/'GENERATION_POLICY.json');oldstat=read(R2/'FINAL_STATUS.json')
protected=read(P/'PROTECTED_INPUTS_BEFORE.json');changed=[]
for p,h in protected.items():
    if sha(p)!=h:changed.append(p)
dump('FROZEN_AND_PRIOR_BASELINE_VERIFICATION.json',dict(files_checked=len(protected),changed=changed,verified=not changed,all_R2_files_included=True,old_R2_reports_unchanged=True,source_MIDI_unchanged=sha(SOURCE)==read(R2/'INPUT_LOCK.json')['source_sha256']))
from left_continuous_motion import *
A=dict(np.load(R2/'motion.npz'));co=EventCoordinator(read(P/'PERFORMANCE_TIMELINE.json')['notes'],pol['source_policy']);q=np.degrees(A['L_q']);oldexcess=float(max(0,np.max(co.state_low[6:].reshape(5,4)-q),np.max(q-co.state_high[6:].reshape(5,4))))
failure=dict(stage='02_generate_once.py final interpolation guard before np.savez',exception='AssertionError: Bound exceeded: stop, no refit',failed_assertion='np.all(q >= co.state_low[6:] - 1e-7) and np.all(q <= co.state_high[6:] + 1e-7)',CONFIRMED=['First dynamic solve ran; corrected sampled q failed original joint-domain guard before any motion.npz or blend save.','No second dynamic solve or per-note correction occurred.'],SUPPORTED=['Support-knot bounds do not by themselves guarantee the sum of R2 reference q and separately interpolated tapered correction stays in domain between knots.'],UNKNOWN=['Exact violating sample, finger, amount, final solver nfev and numerical convergence were not saved before the assertion; they are not reconstructed by rerunning.'],R2_joint_bound_excess_deg=oldexcess,last_visible_progress=dict(residual_calls=3303,elapsed_sec=240.5,contact_weighted_RMS=0.7916),skin_marker_model_parity_max_mm=0.07972896653122975,actual_nfev=None,solver_converged=None,solver_limit_reached=None,failed_bake_guard_not_proof_of_anatomical_unreachability=True,saved_dynamic_candidates=0,dynamic_generation_attempts=1,second_attempt=False,no_parameter_change_after_generation=True)
dump('GENERATION_FAILURE.json',failure)
(P/'GENERATION_FAILURE_LOG.txt').write_text('''First dynamic invocation: python 02_generate_once.py
EXACT_SKIN_MARKER_PARITY 0.07972896653122975
Last observed progress: ONE_CORRECTION_SOLVE 3303 elapsed 240.5 contact_rms 0.7916
Traceback: 02_generate_once.py line 46, final sampled joint bounds assertion
AssertionError: Bound exceeded: stop, no refit
Process exit code: 1

This records observed tool output, not a complete captured solver stdout stream.
No motion.npz or blend was saved. No second invocation was made.
Final nfev, success, limit flag and violating sample were not persisted; UNKNOWN.
''',encoding='utf8')
diagnostic=dict(R2_all_seven_actual_skin_contacts=audit['notes'],R2_source_motion_sha256=audit['source_motion_sha256'],R2_source_candidate_sha256=audit['source_candidate_sha256'],static_reachability=stat,generation_failure=failure,root_preservation=dict(strategy='fixed original R2 root translation/rotation',static_root_delta_mm=0,static_root_delta_deg=0,dynamic_saved_result=None),joint_preservation=dict(locked_delta_limits_deg=pol['joint_delta_limits_deg'],static_max_actual_joint_delta_deg=float(np.max(np.abs([t['joint_delta_deg'] for t in stat['tests']]))),R3_saved_readback='NOT_AVAILABLE'),R2_retained_engineering_WARN=oldstat['retained_engineering_WARN'],R3_contact_correctness='UNVERIFIED',R3_finite_neighbor_contact_risk='UNVERIFIED',solver_actual_nfev=None,solver_actual_convergence=None,solver_limit_reached=None,ENGINEERING_DIAGNOSTICS='FAIL',scope='R2 all hold samples plus finite static pad-cap tests; no R3 save/readback; no exhaustive vertex forensic')
dump('ENGINEERING_DIAGNOSTICS.json',diagnostic)
status=dict(phase='MINUET_STAGE_B_R3_LEFT_HAND_GLOBAL_CONTACT_PLACEMENT',client_date='2026-10-10',GLOBAL_CONTACT_PLACEMENT='NOT_IMPROVED',ALL_ACTIVE_FINGER_COVERAGE='INCOMPLETE',WHITE_KEY_CONTACT_REGION='PARTIAL',TRIAD_CONTACT_PRESERVED='FAIL',SUBSEQUENT_NOTES_PRESERVED='FAIL',MOTION_PRESERVATION='FAIL',MUSIC_FUNCTIONAL_CORRECTNESS='UNKNOWN',ENGINEERING_DIAGNOSTICS='FAIL',HUMAN_VISIBLE_QUALITY='HUMAN_PENDING',FROZEN_ASSETS_UNCHANGED='YES' if not changed else 'NO',FINAL_STATUS='FAIL_CLOSED',status_semantics='FAIL values are R3 acceptance gates: no saved R3 motion exists. They do not revoke R2 musical contact or Human acceptance.',R2_all_active_finger_coverage='VERIFIED',R3_all_active_finger_coverage='INCOMPLETE',white_key_region_code_implemented=True,white_key_region_dynamic_validation=False,dynamic_generation_attempts=1,saved_dynamic_candidates=0,second_dynamic_candidate=False,post_generation_parameter_changes=0,manual_note_coordinate_patches=False,source_notes=7,source_duration_sec=5.142852,original_MIDI_unchanged=sha(SOURCE)==read(R2/'INPUT_LOCK.json')['source_sha256'],fingering_unchanged=True,frozen_asset_files_checked=len(protected),R2_latest_Human_motion_acceptance_preserved=True,R2_original_reports_unchanged=True,static_preflight_batches=2,static_pose_solves=20,static_Actions_saved=0,policy_locks=1,solver_nfev=None,solver_converged=None,solver_limit_reached=None,blocking_reason='First correction trajectory violated joint-domain guard at output interpolation, before motion save. No refit permitted.',new_three_view_videos='NOT_PRODUCED_NO_VALID_SAVED_CANDIDATE',before_after_videos='NOT_PRODUCED',dual_hand_started=False,next_stage_started=False,stop='STOP — HUMAN REVIEW')
dump('FINAL_STATUS.json',status)
dump('SOLVER_EXECUTION_ACCOUNTING.json',dict(static_pose_solves=20,static_batches=2,static_Actions_saved=0,dynamic_generation_attempts=1,policy_locks=1,saved_dynamic_candidates=0,post_generation_refits=0,second_attempt=False,actual_dynamic_nfev=None,actual_dynamic_convergence=None,actual_dynamic_limit_flag=None,observed_last_residual_call_counter=3303))
beforetable='|事件|指号|中心最小键边余量mm|有限指腹P90最小余量mm|\n|---|---:|---:|---:|\n'+''.join(f"|{r['note_id']} {r['note']}|{r['finger']}|{r['summary']['center_min_edge_mm']:.3f}|{r['summary']['pad_min_edge_mm']:.3f}|\n" for r in audit['notes'])
(P/'BEFORE_AFTER_CONTACT_REVIEW.md').write_text('''# 前后对照交付状态：FAIL_CLOSED

首次动态修正未通过输出采样的关节域保护，未保存R3 motion/Blender文件。遵守唯一候选止损要求，没有重算、修补或从第二份候选挑选。没有R3原速视频，因此不能填写全部7次实际触键已改善，也不能制作真实的新旧同步视频。审核页只呈现原R2证据和失败状态，不用静态测试替代R3动态视频。

R2真实落点：

'''+beforetable+'''

10个静态任务中，原root固定时各有限指腹获得约3.94–4.77mm边缘余量。它们只能证明局部静态可达性，不能证明整段动态输出、视觉动作保持或音乐功能通过。

教学、俯视与侧斜R2阶段图已由Agent检查。正常教学和俯视支持多指贴缝观感；侧斜的轮廓遮挡影响更大。未执行完整实时原速影音观看，不据此声明自然度通过。Human最新已认可R2整体动作，其权威保留；原R2历史FAIL记录不改写。

如果未来另获授权开展独立新轮次，支持点约束与最终输出采样约束的一致性是需要诊断的问题。本轮不执行该修复，也不启动第二候选。

STOP — HUMAN REVIEW。
''',encoding='utf8')
(P/'MOTION_PRESERVATION_REPORT.md').write_text('''# 运动保持：R3验收FAIL，R2原动作完整保护

原R2所有827个采样、root轨迹、关节轨迹、键盘下沉、事件、音频及保存候选均未修改。'''+f'{len(protected)}个保护文件最终哈希核验，变化文件{len(changed)}个。'+'''

生成前锁定：root平移/旋转修正为0；只允许原准备、触键、恢复窗口内的指关节局部修正；原窗口外修正为0；指腹横向目标由真实键/skin cap计算，纵向及键面间隙参考R2。每DOF范围由几何leverage、静态联合可达性和原Rig域约束推导，见GENERATION_POLICY.json。

静态修正最大约10.99度，主要是主动指横展及必要屈伸协调；不能把该静态结果当作动态保持报告。正式求解的最终采样未通过关节域检查，因此没有保存的轨迹可用于root/关节前后回读。具体违规采样、关节和程度未在失败前持久化，UNKNOWN；没有为取得这些数据重新求解。

R2基线关节域本身只读复核的最大超限：'''+f'{oldexcess:.9g}度。'+'''

首份生成失败源于输出采样保护；不是已证实无法在保持自然动作时完成落点改善，也不是R2的Human认可被撤销。没有交付新视频，不能断言新悬空、钩爪、抽动或掌腕异常存在/不存在。

STOP — HUMAN REVIEW。
''',encoding='utf8')
answers=[
('Q1','确认多个主动指的有限指腹范围偏边；全部skin pad中心仍在键内。'),
('Q2','G3/小指5、和弦B3/中指3、D4/拇指1、A3/无名指4、C4/食指2、末次B3/中指3。中间一次B3/3相对安全，也独立覆盖。'),
('Q3','CONFIRMED：3mm中心内缩忽略约8–11mm指腹宽度；偏向不一、横漂小。SUPPORTED：软目标偏好与关节/共同掌腕折衷及投影因素。UNKNOWN：软组织真实压力区。'),
('Q4','通用几何区域与运动保持修正代码已建立，静态可达性支持；动态验证未完成，因此WHITE_KEY_CONTACT_REGION=PARTIAL。'),
('Q5','不能确认全部7次改善。静态结果改善不能代替未保存的动态候选。'),
('Q6','R2和弦技术PASS保留；R3未保存、未回读，R3验收门FAIL（未验证），不是已证实错键。'),
('Q7','R2后续单音技术PASS保留；R3未验证，R3验收门FAIL。'),
('Q8','R2原文件完整保护；没有有效R3轨迹和视频，无法确认新动作自然度保持。'),
('Q9','root在策略及静态测试中固定为0变化；正式输出失败，具体动态关节变化/新异常UNKNOWN。静态最大微协调约10.99度。'),
('Q10','无逐音坐标硬编码、无手工姿态补丁、无第二动态尝试。事件JSON目标由相同几何公式推导。'),
('Q11',f"{'YES' if not changed else 'NO'}：{len(protected)}个保护文件哈希核验，源MIDI、键/声链、冻结资产、四静态姿态和Stage A R2成果保持。"),
('Q12','不提交不存在的有效R3候选做原速验收；只交付原R2诊断和首次失败证据，FAIL_CLOSED后停止。')]
(P/'IMPLEMENTATION_REPORT.md').write_text('''# 实现报告：FAIL_CLOSED

本轮完成全部7次R2真实指腹落点只读诊断、几何通用区域代码、固定R2 root的静态可达性测试和一次锁定策略。唯一正式动态生成在最终插值/烘焙前的关节域保护处失败；没有保存motion.npz或Blender候选，没有新视频，没有第二次求解。

所有新增代码均在本独立目录，R2代码和历史报告未改。使用实际左FK/事件协调器，新增contact_region.py和相对R2的小范围修正求解。原MIDI、指法、tempo和全部事件保留。

静态预检两批各10个姿态：首批一个约0.276mm标记目标误差被脚本绝对0.15mm筛选拒绝，但对应实际指腹余量4.57mm，不构成几何不可达证据。生成前改用已取得边余量的10%比例筛选；第二批通过后仅锁定一次正式参数。静态总计20次pose求解，无Action/动态候选保存。不是动态生成重试。

唯一动态求解最后可见日志为残差调用3303、约240.5秒、加权接触RMS0.7916；失败发生在结果持久化之前。实际nfev、是否达到100次上限、最终收敛状态及超限采样没有保存，全部UNKNOWN。残差调用次数不能冒充nfev，数值残差降低不能当作实际触键/视觉通过。GENERATION_FAILURE.json明确区分CONFIRMED/SUPPORTED/UNKNOWN。

首份结果guard失败后立即停止；没有裁剪关节、回投影、改参数、重算或手动逐指修补。后续场景/诊断/渲染脚本属于未执行准备代码，不代表已产生对应输出。唯一候选限制按一次正式生成尝试计数；有效保存候选0份。

|问题|回答|
|---|---|
'''+''.join(f'|{q}|{a}|\n' for q,a in answers)+'''

交付缺项如实标记：R3有效动态文件、原速三视角新视频、同期新旧对照视频均未产生，不能用静态或原R2视频冒充。最终状态的FAIL为R3验收门失败；R2的Human动作认可及技术检查不被撤销。

STOP — HUMAN REVIEW。未启动双手或16小节。
''',encoding='utf8')
ff='D:/ffmpeg/bin/ffmpeg.exe';fp='D:/ffmpeg/bin/ffprobe.exe';media={}
for view in ['teaching','overhead','side_oblique']:
    path=R2/f'normal_speed_{view}.mp4'
    data=json.loads(subprocess.check_output([fp,'-v','error','-count_frames','-show_streams','-of','json',str(path)]));v=next(s for s in data['streams'] if s['codec_type']=='video');subprocess.run([ff,'-v','error','-i',str(path),'-f','null','-'],check=True)
    media[view]=dict(path=str(path),sha256=sha(path),frames=int(v['nb_read_frames']),fps=v['r_frame_rate'],duration_sec=float(v['duration']),full_decode='PASS',R2_original_unchanged=True,R3_video=None)
dump('VIDEO_VERIFICATION.json',dict(R2=media,R3='NOT_PRODUCED',before_after='NOT_PRODUCED',full_realtime_audiovisual_review='NOT_PERFORMED',Agent_R2_three_view_phase_sheets_reviewed=True))
contact='<table><tr><th>原R2事件 / 指</th><th>中心最小键边余量mm</th><th>有限指腹P90最小余量mm</th><th>R3</th></tr>'+''.join(f"<tr><td>{r['note_id']} {r['note']} / {r['finger']}</td><td>{r['summary']['center_min_edge_mm']:.2f}</td><td>{r['summary']['pad_min_edge_mm']:.2f}</td><td>未生成有效结果</td></tr>" for r in audit['notes'])+'</table>'
links=' · '.join(f'<a href="{n}">{n}</a>' for n in ['ALL_ACTIVE_FINGER_PLACEMENT_AUDIT.md','GENERAL_WHITE_KEY_CONTACT_REGION_DESIGN.md','MOTION_PRESERVATION_REPORT.md','BEFORE_AFTER_CONTACT_REVIEW.md','IMPLEMENTATION_REPORT.md','ENGINEERING_DIAGNOSTICS.json','GENERATION_FAILURE.json','FINAL_STATUS.json'])
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Minuet Stage B R3 · FAIL_CLOSED</title><style>body{margin:0;background:#eeeadf;color:#29382d;font:16px/1.65 system-ui}main{max-width:1180px;margin:34px auto;padding:0 24px}h1{font-size:29px}aside{padding:18px;background:#fff;border-left:5px solid #a64437;border-radius:7px}video,img{width:100%;background:#555}select{font:inherit;padding:8px;margin:14px 0}table{width:100%;border-collapse:collapse;background:#fff}td,th{padding:9px;border-bottom:1px solid #ccc;text-align:left}a{color:#216341}.note{font-size:14px;color:#59665c}</style><main><h1>左手全部主动指落点 · 首次生成失败证据</h1><aside><strong>FAIL_CLOSED · HUMAN_PENDING · STOP — HUMAN REVIEW</strong><br>唯一动态生成在最终输出采样的关节域检查失败，未保存有效R3候选。没有第二次求解或人工修补。<br>以下视频明确是原R2，供复核原落点；没有R3视频或新旧同步对照。</aside><h2>全部7次原R2实际皮肤落点</h2>CONTACT_TABLE<p>6次事件的有限指腹P90范围靠近或跨出一侧键边，原skin中心均在键内。中间一次B3有较好余量。偏向不同、持键横向漂移小。通用区域代码和固定root的静态测试已完成，不能据此宣称动态改善。</p><h2>原R2三视角 · 原速1×</h2><select id="view"><option value="teaching">正常教学</option><option value="overhead">俯视</option><option value="side_oblique">侧斜</option></select><video id="baseline" controls preload="metadata" playsinline></video><p class="note">原音乐5.142852秒；完整演示5.95秒、357帧、60fps。最新Human认可的R2整体动作保持，原报告不改写。</p><h2>R3与同期对照</h2><aside>未提供：有效动态候选未保存，R3接触正确性、动作自然度和新旧视觉改善均未验证。不得用静态测试冒充。</aside><h2>首次失败</h2><p><code>AssertionError: Bound exceeded: stop, no refit</code><br>失败发生在修正轨迹插值后、motion.npz保存前。具体超限采样及最终nfev/收敛状态未持久化，标记UNKNOWN。没有扩大自由度或修改冻结资产。</p><h2>报告</h2><p>REPORT_LINKS</p><h2>原R2阶段证据</h2><img src="../minuet_stage_b_r2_left_hand_continuous_accompaniment/phase_sheet_teaching.jpg" alt="原R2教学视角阶段图"><p class="note">Agent查看了三视角阶段图并解码验证原视频，未执行完整实时原速影音观看；未填写Human PASS。</p><aside>STOP — HUMAN REVIEW。本轮不自动修复求解/插值保护，不生成第二份，不启动双手或下一阶段。</aside></main><script>const view=document.getElementById('view'),v=document.getElementById('baseline');function load(){v.pause();v.playbackRate=1;v.src=`../minuet_stage_b_r2_left_hand_continuous_accompaniment/normal_speed_${view.value}.mp4`;}view.addEventListener('change',load);load();</script></html>'''
(P/'HUMAN_REVIEW.html').write_text(page.replace('CONTACT_TABLE',contact).replace('REPORT_LINKS',links),encoding='utf8')
dump('DELIVERY_MANIFEST.json',dict(files={p.name:sha(p) for p in P.iterdir() if p.is_file() and p.name not in ['DELIVERY_MANIFEST.json','PROTECTED_INPUTS_BEFORE.json']},required_reports_present=True,valid_R3_candidate=False,new_videos=False,synchronized_comparisons=False,second_generation=False))
print('FAIL_CLOSED_DELIVERED',len(protected),'protected files','changed',changed,'R2 bound excess',oldexcess,flush=True)
