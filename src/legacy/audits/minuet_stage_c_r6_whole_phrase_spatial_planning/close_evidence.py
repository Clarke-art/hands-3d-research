from common import *
import ast
lock=read(P/'STRATEGY_LOCK.json');start=read(P/'FORMAL_ATTEMPT_STARTED.json')
assert start['lock_sha256']==sha(P/'STRATEGY_LOCK.json')
assert all(sha(P/n)==h for n,h in lock['code_sha256'].items())
term=read(P/'SOLVER_TERMINATION.json')
term['trace']=[json.loads(line.split('R6_ITERATION ',1)[1]) for line in (P/'formal_solver.log').read_text().splitlines() if line.startswith('R6_ITERATION ')]
term['completed_iteration_count']=len(term['trace'])
term['counter_limitation']='Watchdog interrupted an in-flight evaluation. 23 objective evaluations and 483 spatial evaluations are verified lower bounds from the last completed iteration; the exact final totals were not durably recorded. This requested accounting item is incomplete.'
dump('SOLVER_TERMINATION.json',term)
diag=read(P/'ENGINEERING_DIAGNOSTICS.json');actual=read(P/'ACTUAL_SPATIAL_VALIDATION.json')
newpairs=[dict(video_sec=r['video_sec'],**h) for r in actual['rows'] for h in r['terminal']['finger_intersections'] if tuple(h['digits']) not in {tuple(x['digits']) for x in r['source']['finger_intersections']}]
diag['solver']=term;diag['new_finger_intersection_time_pair_samples']=newpairs
diag['terminal_render_manifest']='TERMINAL_DIAGNOSTIC_RENDER_MANIFEST.json'
diag['agent_still_review']=dict(human_approval=False,original_speed_review=False,
    views_inspected=['LATE_SOURCE_OVERHEAD','LATE_TERMINAL_NON_CANDIDATE_OVERHEAD','LATE_TERMINAL_NON_CANDIDATE_SIDE_OBLIQUE','EARLY_TERMINAL_NON_CANDIDATE_TEACHING'],
    finding='At 3.825s the right middle/ring fingertip overlap is still visible in the matched overhead terminal still; actual historical ROI intersection pairs are 93 source versus 68 terminal. No claim of complete naturalness or product acceptance.')
dump('ENGINEERING_DIAGNOSTICS.json',diag)
f=P/'WHOLE_PHRASE_SPATIAL_VALIDATION.md'
f.write_text(f.read_text(encoding='utf8')+'\n同一时刻新增指对相交记录为 0；此结论限于已检的 396 个时刻和既定指区。3.825 秒原俯视与终态俯视已直接查看，终态仍能看到中指/无名指末端重叠；该时刻实际历史 ROI 相交面片对为 93 → 68，未消除。另查看终态侧斜和早段教学静帧，不能替代完整 1× 自然度验收。12 张同机位、同尺度、同时间的源/终态静帧位于 `terminal_diagnostic_stills/`，明确标为 NON_CANDIDATE。渲染后实际皮肤与测量终态的一致性见 TERMINAL_DIAGNOSTIC_RENDER_MANIFEST.json；没有演奏视频或新 Blend。\n',encoding='utf8')
f=P/'MOTION_NATURALNESS_AND_PRESERVATION.md'
f.write_text(f.read_text(encoding='utf8')+'\n实际曲线采样还出现拇指第一屈伸最小 −0.496679°、中指 MCP 最小 −0.220233°，均低于工程下界 0°；不是只有保守 Bezier 控制点越界。全局角速度峰值约 359.860°/s、加速度峰值约 247168.872°/s²，逐关节门槛仍见诊断 JSON。密集事件节点的最小间隔为 0.0007145 秒；这说明 C1 连续并不保证合理加速度，本次未作任何求解后平滑或修正。\n',encoding='utf8')
f=P/'SOLVER_IMPLEMENTATION_REPORT.md'
f.write_text(f.read_text(encoding='utf8')+'\n计数交付限制：日志可确认 23 次已完成目标评估、483 次已完成空间评估及 23 条主要迭代记录；外部止损时仍有调用进行，最终精确 nfev/空间调用总数未可靠落盘。这一项没有完全满足请求，不能补造精确数字。完整已完成 trace 已从日志恢复至 SOLVER_TERMINATION.json。\n\nRELEASING/EXITING 没有独立接触力学模型或强制旧键持键等式；离键与交接由原机械键面、连续源风格和全手空间不等式共同安排。角色组织已实现，实际释放/准备的自然执行仍未通过本轮门禁。\n',encoding='utf8')
f=P/'FINAL_ANSWERS.md';s=f.read_text(encoding='utf8')
s=s.replace('起止关节自由，连续连接原则已实现；几何结果见 START/END，整体自然可行性尚未建立，Human 未批准。','起止关节自由，但未建立自然可行结果。开始状态的采样黑键最大深度 0.4308 mm、无已检指对相交，仅可待审 WARN；结束状态仍穿入黑键 1.6743 mm，明确未通过。Human 未批准。')
s=s.replace('同一时间新增超过门槛的主导指/键记录 88；计数恶化指对 []。','同一时间新增超过门槛的主导指/键记录 88；已检时间与区域内新增指对相交记录 0，未见指对相交总计数恶化。')
f.write_text(s,encoding='utf8')
ver=read(P/'DELIVERY_VERIFICATION.json');ver['files']={n:sha(P/n) for n in ver['files']}
render=read(P/'TERMINAL_DIAGNOSTIC_RENDER_MANIFEST.json')
assert len(render['rows'])==12 and max(r['actual_render_skin_parity_mm'] for r in render['rows'])<.03
assert all(sha(P/'terminal_diagnostic_stills'/f'{label}_SOURCE_{view}.png') != sha(P/'terminal_diagnostic_stills'/f'{label}_TERMINAL_NON_CANDIDATE_{view}.png') for label in ['EARLY','LATE'] for view in ['TEACHING','OVERHEAD','SIDE_OBLIQUE'])
assert read(P/'TERMINAL_SKIN_PARITY.json')['pass_']
assert sha(C1/'STAGE_C_R1_DUAL_HAND_SYNCHRONIZED_DESIGN_ONLY.blend')==SOURCE_HASH
assert not list(P.glob('*.blend')) and not list(P.glob('*.mp4')) and not (P/'HUMAN_REVIEW.html').exists()
for script in P.glob('*.py'):ast.parse(script.read_text(encoding='utf8'),filename=str(script))
ver.update(locked_code_and_policy_unchanged=True,terminal_actual_skin_parity_pass=True,
    diagnostic_stills=12,stills_are_not_candidates=True,rendered_skin_parity_pass=True,
    source_terminal_images_distinct=True,exact_final_evaluation_counters_available=False,
    final_nfev_lower_bound=23,final_spatial_evaluations_lower_bound=483)
dump('DELIVERY_VERIFICATION.json',ver)
print('R6_CLOSED_VERIFIED_FAIL_CLOSED_NO_RETRY',flush=True)
