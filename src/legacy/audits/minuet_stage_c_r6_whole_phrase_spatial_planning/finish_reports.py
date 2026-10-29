"""Close a failed sole attempt with measured evidence and explicit limitations."""
from common import *
import time
def doc(n,s):(P/n).write_text(s.strip()+'\n',encoding='utf8')
assert (P/'SUPERVISOR_RECEIPT.json').exists()
receipt=read(P/'SUPERVISOR_RECEIPT.json')
lock=read(P/'STRATEGY_LOCK.json')
if (P/'SOLVER_TERMINATION.json').exists():
    term=read(P/'SOLVER_TERMINATION.json');exact=True
else:
    progress=read(P/'SOLVER_PROGRESS.json') if (P/'SOLVER_PROGRESS.json').exists() else {}
    term=dict(attempts=1,status='WATCHDOG_STOP',success=False,termination_reason=receipt.get('reason','Process exited without final solver receipt'),
        nfev=None,counts=dict(major_iterations=progress.get('iteration',0)),spatial_evaluations=None,
        elapsed_sec=receipt['wall_clock_sec'],last_completed_iteration=progress,
        nfev_exact_unavailable=True,nfev_lower_bound=progress.get('nfev',0),
        spatial_evaluations_lower_bound=progress.get('spatial_evaluations',0))
    dump('SOLVER_TERMINATION.json',term);exact=False
num=read(P/'NUMERICAL_TERMINAL_DIAGNOSTICS.json')
actual=read(P/'ACTUAL_SPATIAL_VALIDATION.json')
records=actual['rows']
def metrics(label,subset):
    phases={}
    for version in ['source','terminal']:
        items=[r[version] for r in subset];hits=[h for r in items for h in r['key_hits']]
        black=[h for h in hits if h['color']=='BLACK' and not h['active_target_for_dominant_digit']]
        white=[h for h in hits if h['color']=='WHITE' and not h['active_target_for_dominant_digit']]
        contacts=[h for r in items for h in r['contacts']]
        phases[version]=dict(
            historical_middle_ring_max_face_pairs=max([r['historical_middle_ring_face_pairs'] for r in items]+[0]),
            historical_middle_ring_sum_face_pairs=sum(r['historical_middle_ring_face_pairs'] for r in items),
            historical_middle_ring_affected_samples=sum(r['historical_middle_ring_face_pairs']>0 for r in items),
            all_pair_intersection_samples=sum(bool(r['finger_intersections']) for r in items),
            pair_totals={f'{a}/{b}':sum(h['face_pairs'] for r in items for h in r['finger_intersections'] if h['digits']==[a,b]) for a,b in __import__('itertools').combinations(['THUMB','INDEX','MIDDLE','RING','LITTLE'],2)},
            non_target_black_max_depth_mm=max([h['depth_mm'] for h in black]+[0]),
            non_target_black_over_limit_hits=sum(h['depth_mm']>.5 for h in black),
            non_target_white_max_depth_mm=max([h['depth_mm'] for h in white]+[0]),
            any_key_max_depth_mm=max([h['depth_mm'] for h in hits]+[0]),
            contacts=len(contacts),contact_gap_min_mm=min([h['gap_mm'] for h in contacts]+[0]),
            contact_gap_max_mm=max([h['gap_mm'] for h in contacts]+[0]),
            contact_horizontal_max_mm=max([h['horizontal_mm'] for h in contacts]+[0]),
            failed_contacts=[dict(**h) for h in contacts if h['gap_mm']<-.5001 or h['gap_mm']>2.1001 or h['horizontal_mm']>.5001])
    return dict(scope=label,samples=len(subset),**phases)
summary=[metrics(label,[r for r in records if a<=r['video_sec']<=b]) for label,a,b in [
    ('FULL',0,5.95),('EARLY',.778571,2.134284),('LATE',2.741426,4.70571),('START',0,0),('END',5.95,5.95)]]
full=summary[0]
def pair_status(s):
    a,b=s['source'],s['terminal']
    if b['historical_middle_ring_max_face_pairs']==0:return 'RESOLVED'
    if b['historical_middle_ring_sum_face_pairs']<a['historical_middle_ring_sum_face_pairs'] and b['historical_middle_ring_max_face_pairs']<=a['historical_middle_ring_max_face_pairs']:return 'IMPROVED'
    return 'FAIL'
early,late=pair_status(summary[1]),pair_status(summary[2])
a,b=full['source'],full['terminal']
black='PASS' if b['non_target_black_over_limit_hits']==0 else ('PARTIAL' if b['non_target_black_max_depth_mm']<a['non_target_black_max_depth_mm'] and b['non_target_black_over_limit_hits']<a['non_target_black_over_limit_hits'] else 'FAIL')
active='PASS' if not b['failed_contacts'] else 'FAIL'
newpairs=[p for p,v in b['pair_totals'].items() if v>a['pair_totals'][p]]
observed_new=[]
for r in records:
    before={(h['digit'],h['midi']) for h in r['source']['key_hits'] if h['depth_mm']>.5}
    observed_new.extend(dict(video_sec=r['video_sec'],**h) for h in r['terminal']['key_hits'] if h['depth_mm']>.5 and (h['digit'],h['midi']) not in before)
assert not (term['success'] and num['pass_'] and active=='PASS' and black=='PASS' and b['all_pair_intersection_samples']==0), 'Potential valid result: use candidate adapter and visual gate before finalizing'
before=read(P/'PROTECTED_INPUTS_BEFORE.json');changed=[p for p,h in before.items() if not Path(p).is_file() or sha(p)!=h]
dump('ASSET_PRESERVATION.json',dict(protected_files=len(before),changed_files=changed,
    source_sha256_after=sha(C1/'STAGE_C_R1_DUAL_HAND_SYNCHRONIZED_DESIGN_ONLY.blend'),
    protected_scene_actions_unchanged=actual['protected_actions_unchanged'],new_blends=0,new_actions=0,new_videos=0))
frozen=not changed and sha(C1/'STAGE_C_R1_DUAL_HAND_SYNCHRONIZED_DESIGN_ONLY.blend')==SOURCE_HASH
trajectory=dict(np.load(P/'TERMINAL_TRAJECTORY_EVIDENCE.npz'))
diff=trajectory['qdeg']-trajectory['source_qdeg']
dump('ENGINEERING_DIAGNOSTICS.json',dict(source_identity=SOURCE_HASH,solver=term,supervisor=receipt,
    numerical=num,actual_summary=summary,actual_evidence='ACTUAL_SPATIAL_VALIDATION.json',
    new_or_worsened_finger_pair_totals=newpairs,new_non_target_or_target_body_hit_samples=observed_new,
    q_style_rms_deg=float(np.sqrt(np.mean(diff**2))),q_style_max_abs_deg=float(abs(diff).max()),
    frozen_assets_unchanged=frozen,protected_files=len(before),changed_files=changed,
    formal_dynamic_solve_attempts=1,valid_dynamic_candidates=0,new_static_solves=0,
    final_gate='FAIL',human_status='HUMAN_PENDING',actual_skin_model_parity=read(P/'TERMINAL_SKIN_PARITY.json') if (P/'TERMINAL_SKIN_PARITY.json').exists() else 'NOT_AVAILABLE'))
status=dict(WHOLE_PHRASE_ROLE_PLANNING='IMPLEMENTED',WHOLE_PHRASE_SPATIAL_PLANNING='PARTIAL',
    PREVIOUS_BOUNDARY_CONTRADICTION='RESOLVED',RIGHT_ROOT_POLICY='PRESERVED',
    FORMAL_DYNAMIC_SOLVE_ATTEMPTS=1,VALID_DYNAMIC_CANDIDATE='NO',
    EARLY_FINGER_INTERSECTION=early,LATE_FINGER_INTERSECTION=late,BLACK_KEY_SPATIAL_CLEARANCE=black,
    ACTIVE_KEY_CONTACT=active,RIGHT_HAND_NATURALNESS='HUMAN_PENDING',
    LEFT_HAND_APPROVED_MOTION_PRESERVED='YES' if frozen and actual['protected_actions_unchanged'] else 'NO',
    DUAL_HAND_MUSIC_FUNCTION='UNKNOWN',ENGINEERING_DIAGNOSTICS='FAIL',
    FROZEN_ASSETS_UNCHANGED='YES' if frozen else 'NO',FINAL_STATUS='FAIL_CLOSED',
    status_scope='Terminal numerical iterate assessed in memory; no valid derived dual-hand candidate; music preservation verified separately',
    source_music_preservation='PASS' if frozen else 'FAIL',new_static_solves=0,new_dynamic_candidates=0,
    root_unknowns=0,old_window_boundary_equalities=0,human_approval_claimed=False,
    formal_nfev=term['nfev'],formal_nfev_exact=exact,termination_reason=term['termination_reason'],stop='STOP — HUMAN REVIEW')
dump('FINAL_STATUS.json',status)
rows='\n'.join(f"| {s['scope']} | {s['samples']} | {s['source']['historical_middle_ring_max_face_pairs']} → {s['terminal']['historical_middle_ring_max_face_pairs']} | {s['source']['historical_middle_ring_affected_samples']} → {s['terminal']['historical_middle_ring_affected_samples']} | {s['source']['non_target_black_max_depth_mm']:.4f} → {s['terminal']['non_target_black_max_depth_mm']:.4f} |" for s in summary)
doc('WHOLE_PHRASE_SPATIAL_VALIDATION.md',f'''
# 完整短句空间验证

结论：FAIL_CLOSED。这里比较的是同一源场景和唯一求解终态的实际蒙皮证据，不是合法动态候选，更不代表 Human 视觉批准。

| 范围 | 样本数 | 历史中指/无名指最大面片对：原→终态 | 有相交样本：原→终态 | 非目标黑键最深内部顶点 mm：原→终态 |
|---|---:|---:|---:|---:|
{rows}

早段状态 {early}，晚段 {late}，黑键状态 {black}。RESOLVED/IMPROVED 如出现，仅指上述有限实际几何采样，不证明连续无碰撞或正常视角自然。真实 BVH 相交与求解器支持平面代理分别保存，不混为穿透深度。

全段非目标白键最大内部顶点深度：{a['non_target_white_max_depth_mm']:.4f} → {b['non_target_white_max_depth_mm']:.4f} mm。实际指间相交样本数：{a['all_pair_intersection_samples']} → {b['all_pair_intersection_samples']}。计数变多的指对：{newpairs}。原同一采样时刻没有超过 0.5 mm、终态新增超过门槛的“主导指/键”记录数 {len(observed_new)}，详见 ENGINEERING_DIAGNOSTICS.json；这不是整个源曲从未发生过该冲突的断言。

检查覆盖全段 60 Hz 加有限事件探针，全部皮肤顶点对音区白黑键体，10 个强权重指区 BVH，以及与历史完全同口径的中/无名指远端 ROI。实际渲染键顶点与正式键组件数据已核实。顶点检查不能排除面片跨越；开放指区不使用任意法向来伪造内部深度。保留采样与区域局限，不宣称全 88 键逐顶点连续无碰撞证明。
''')
nf=str(term['nfev']) if exact else f"精确值不可用；最后完成迭代下界 {term.get('nfev_lower_bound')}，见 watchdog 限制"
doc('SOLVER_IMPLEMENTATION_REPORT.md',f'''
# 求解器实现与一次正式执行

全段联合规划已经实现并实际尝试；合法空间运动结果未建立。新增代码全部位于本 R6 目录，历史 R5、A2、B3、C1、冻结 Rig、皮肤、权重和 corrective 均未原地修改。

`prepare.py` 复用 R5 角色接口并构建全段节点；`export_readonly.py` / `inspect_shape.py` 只读提取冻结场景；`whole_phrase_model.py` 重建五指绝对关节 FK、真实 LBS 与原拇指 corrective；`trajectory_solver.py` 实现全段 C1 三次曲线、Bezier 工程域、空间/触键不等式和源风格目标；`run_once.py` 设置外部墙钟保险；验证脚本只测量唯一终态，不再求解。

后端 {lock['backend']}。一次正式调用，3400 个未知数，339 个节点/中点空间样本，7017 个空间与触键不等式，另有全曲线工程域线性约束和变量边界。所有 20 个关节参与；root 自由度 0。主要迭代上限 200，目标 nfev 上限 2000，空间函数调用上限 4300，墙钟 1800 秒。锁定文件、代码与源模型哈希保存在 STRATEGY_LOCK.json；正式开始前独占写入 FORMAL_ATTEMPT_STARTED.json，防止重跑。

终止：`{term['termination_reason']}`。状态 `{term['status']}`，数值 success `{term['success']}`。已完成主要迭代 {term['counts']['major_iterations']}；真实 nfev：{nf}；记录墙钟 {term['elapsed_sec']:.3f} 秒。完整 trace/计数见 SOLVER_TERMINATION.json。没有第二次求解、换权重、多起点、静态搜索或 root 扩域。

外部强制停止若发生，`FORMAL_CHECKPOINT.npz` 仅保存最后已完成迭代，不能冒称未完成调用的精确 nfev；计数下界及缺失被显式报告。终态数值证据不是新 Blend/Action 候选。

方法局限：支持平面分离要求强权重指区的保守凸包分离，可能排除真实表面不相交的自然姿态；键体使用实际组件的顶点内部约束，仍需独立表面和视觉验收。因此本次失败不证明固定 root、冻结 Rig 或全部可行轨迹无解。
''')
doc('MOTION_NATURALNESS_AND_PRESERVATION.md',f'''
# 自然度与批准动作保持

自然度仍为 HUMAN_PENDING。没有有效候选，不提供旧视频充当 R6 演奏，也没有宣称原速 Human 通过。源 A2/C1 风格是唯一初值和连续偏好，允许修改原有碰撞关节值；未固定旧两个窗口边界。

终态相对源角度 RMS {np.sqrt(np.mean(diff**2)):.6f}°、最大绝对变化 {abs(diff).max():.6f}°。完整角度、速度和加速度在 TERMINAL_TRAJECTORY_EVIDENCE.npz，峰值及预先锁定上限在 NUMERICAL_TERMINAL_DIAGNOSTICS.json。速度门禁 {num['velocity_gate']}，加速度门禁 {num['acceleration_gate']}，Bezier 全段工程域最大越界 {num['engineering_bezier_box_violation_deg']:.9f}°。C1 连续和低速度本身不能证明没有钩爪、V 形横展或僵硬。

原 root Action、左手 root/rig Action、全部活动琴键 Action 在实际复核前后保持相同，源磁盘文件按 SHA256 保持。最终保护清单 {len(before)} 文件，变化 {len(changed)}。没有重做左手、没有改正式手资产或四个批准静态姿态；具体保护路径见 PROTECTED_INPUTS_BEFORE.json 与 ASSET_PRESERVATION.json。
''')
doc('DUAL_HAND_FUNCTIONAL_VALIDATION.md',f'''
# 双手音乐功能与保持

原输入保持 PASS；R6 新双手演奏功能 UNKNOWN，因为没有合法派生候选。不能把原 C1 的音乐 PASS 当成本轮新轨迹通过。

原 23 音符（右 16、左 7）、指法、tempo、velocity、channel、NOTE_ON/OFF、琴键原 Action、重复 G4 部分释放/再次下压机制、双手共用音频和 0.35 秒前导均未更改。源时长 5.142852 秒，演示 5.95 秒；未扩到 8/16 小节。左手继承源动作完整保持。源 MIDI、音频、timeline、场景及历史批准输入由最终保护哈希检查覆盖。

唯一终态的实际主动触键检查为 {active}：共 {b['contacts']} 个接触样本，gap 范围 {b['contact_gap_min_mm']:.6f} 至 {b['contact_gap_max_mm']:.6f} mm，最大水平偏离 {b['contact_horizontal_max_mm']:.6f} mm，失败接触记录 {len(b['failed_contacts'])}。这些是真实皮肤对原机械键面的测量，未通过削弱接触条件来替代空间验收。

未创建新双手 Blend、Action、视频或 HUMAN_REVIEW.html；没有用两个视频叠加模拟合奏。保存重开和音画渲染验收仅适用于合法候选，本轮未进入该阶段。
''')
answers=[
('Q1','是。0–5.95 秒全段 20 关节统一求解；旧两窗口仅作为诊断分组。'),
('Q2','已实现五指事件角色及重叠，区分卸力、退出、机械回弹和下一音准备；未证明所有角色的实际运动都达到质量门禁。'),
('Q3','是。旧边界姿态和零增量锁已解除；不代表所有空间约束已可行。'),
('Q4','起止关节自由，连续连接原则已实现；几何结果见 START/END，整体自然可行性尚未建立，Human 未批准。'),
('Q5','保持原 root，无 root 变量、无超授权变更。'),
('Q6','是，已使用独立硬不等式的全段联合规划；保守支持包络和有限采样有局限，结果未过门禁。'),
('Q7',f"是，恰好一次正式求解；终止 {term['termination_reason']}，没有重试。"),
('Q8',f'{early}；同口径实际远端 ROI 的早段有限采样，详见空间报告。'),
('Q9',f'{late}；同口径实际远端 ROI 的晚段有限采样，详见空间报告。'),
('Q10',f'{black}；非目标黑键最大深度 {a["non_target_black_max_depth_mm"]:.4f} → {b["non_target_black_max_depth_mm"]:.4f} mm，不能据此放行整段。'),
('Q11',f'同一时间新增超过门槛的主导指/键记录 {len(observed_new)}；计数恶化指对 {newpairs}。'),
('Q12',f'{active}；真实接触失败记录 {len(b["failed_contacts"])}。'),
('Q13','未建立。源风格作为偏好保留，Human 自然度仍待评；无合法原速候选可提交。'),
('Q14','是，原左手批准动作及源文件保持。' if frozen else '保护检查失败，见资产报告。'),
('Q15','原 23 音符、键 Action 和音频保持；没有本轮新演奏的功能 PASS。'),
('Q16','是，保护哈希无变化。' if frozen else '否，见变化清单。'),
('Q17','机制由事件、指法、关节域和真实键体驱动，无逐音补 pose；通用成功率未由本次失败证明。'),
('Q18','否。FAIL_CLOSED；没有合法 Blend/原速视频，STOP — HUMAN REVIEW。')]
doc('FINAL_ANSWERS.md','# R6 最终回答\n\n'+'\n\n'.join(f'**{q}**：{v}' for q,v in answers))
required=['WHOLE_PHRASE_ROLE_AND_MOTION_PLAN.md','SPATIAL_CONSTRAINT_AND_FEASIBILITY.md','SOLVER_IMPLEMENTATION_REPORT.md',
    'WHOLE_PHRASE_SPATIAL_VALIDATION.md','MOTION_NATURALNESS_AND_PRESERVATION.md','DUAL_HAND_FUNCTIONAL_VALIDATION.md','ENGINEERING_DIAGNOSTICS.json','FINAL_STATUS.json','FINAL_ANSWERS.md']
dump('DELIVERY_VERIFICATION.json',dict(required_present=all((P/n).is_file() for n in required),
    files={n:sha(P/n) for n in required},formal_attempts=1,valid_candidates=0,new_blends=len(list(P.glob('*.blend'))),
    new_videos=len(list(P.glob('*.mp4'))),human_review_html=(P/'HUMAN_REVIEW.html').exists(),source_and_frozen_unchanged=frozen,
    stop='STOP — HUMAN REVIEW'))
print('R6_FINAL',json.dumps(status,ensure_ascii=False),flush=True)
