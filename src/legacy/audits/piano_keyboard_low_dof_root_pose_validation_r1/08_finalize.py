from common import *
import collections, html, re

locked()
result=read(P/'MODEL_A_RESULT_R1.json')
clusters=read(P/'MODEL_A_KEY_CLUSTER_PLACEMENT_METRIC_R1.json')
collision=read(P/'MODEL_A_COLLISION_R1.json')['hands']
joined={}
for s in ['R','L']:
    hits={r['observation'] for r in collision[s] if r['palm_vertices'] or r['wrist_vertices']}
    for r in clusters['rows']:
        if r['hand']==s:
            r['palm_or_wrist_key_volume_collision']=r['observation'] in hits
            r['coarse_coverage_and_no_palm_wrist_collision']=r['unlabeled_coarse_placement_feasible'] and r['observation'] not in hits
    rows=[r for r in clusters['rows'] if r['hand']==s and r['cluster_type']!='SINGLE_NOTE']
    joined[s]={'multi_note_observations':len(rows),'coarse_coverage_and_no_palm_wrist_collision':sum(r['coarse_coverage_and_no_palm_wrist_collision'] for r in rows)}
clusters['whole_hand_placement_secondary_summary']=joined
clusters['whole_hand_join_method']='Post-solve conjunction of already locked coarse coverage and inherited palm/wrist collision screen at the SAME observation; no new fitted threshold or solver change. Coarse pad coverage alone is not whole-hand placement.'
clusters['fit_dependence']='Evaluation ignores finger labels for matching, but pose was fitted using unchanged predicted finger labels. This is a conditional diagnostic, not an independently fitted or ground-truth control.'
dump('KEY_CLUSTER_PLACEMENT_METRIC_R1.json',clusters)
dump('CONTACT_MEASUREMENTS_R1.json',read(P/'MODEL_A_CONTACT_MEASUREMENTS_R1.json'))
attr=read(P/'MODEL_A_CONTACT_FAILURE_ATTRIBUTION_R1.json')
multi=[r for r in clusters['rows'] if r['cluster_type']!='SINGLE_NOTE' and not r['labeled_all_pass']]
failed=[r for r in clusters['rows'] if not r['labeled_all_pass']]
attr['combined_multinote_failure_counts']=dict(collections.Counter(r['attribution'] for r in multi))
attr['all_cluster_failed_observations']=len(failed)
attr['all_cluster_likely_label_conflict_observations']=sum(r['attribution']=='LIKELY_FINGERING_LABEL_CONFLICT' for r in failed)
attr['source_bucket_interpretation']='SOURCE_2_5D_OR_CONTACT_PRECISION_LIMIT only means coarse coverage passes but strict contact does not. It does NOT establish source 2.5D as the cause. Root fit, source depth, predicted hand/finger and contact precision remain confounded.'
attr['causal_SOURCE_2_5D_LIMIT']='NOT_ESTABLISHED'
attr['wrong_hand_or_wrong_target_excluded']=False
attr['root_architecture_impossibility']='NOT_ESTABLISHED'
dump('CONTACT_FAILURE_ATTRIBUTION_R1.json',attr)

visual={
 'reviewer':'AGENT_PRECHECK; Human approval remains pending',
 'coverage':'All 210 teaching-view output frames inspected in seven chronological QA sheets; matched old/A/close strip at source 12..18s; full-resolution spot views at frames 0,75,130,205. Video playback approval reserved to Human.',
 'natural_and_clearly_better':False,
 'continuous_sampled_motion':True,
 'observations':[
  {'source_time_sec':'11.50–12.17','finding':'Wrists/forearm stubs visibly crowd and overlap in projection near the start; A is not clearly better. No hidden crossing or mesh-intersection audit was performed.'},
  {'source_time_sec':'12.5–13.1, 15.5–16.1','finding':'Right heading is less oblique in parts of these intervals, but this is a local orientation improvement, not contact or full-placement validation.'},
  {'source_time_sec':'14.5–15.5, 16.5–17.5','finding':'Root heading changes smoothly; lateral spread and changing pad height still do not read as consistently seated playing.'},
  {'source_time_sec':'12–18 close-view samples','finding':'Finger/key surface inconsistencies and low palm placement remain visible. Black/white approach is not reliably resolved by yaw.'}
 ],
 'thumb_placement':'Not cleared as credible contact; no first-web/deformation inference.',
 'no_forensic_macro':True,
 'Human_decision':'PENDING'
}
dump('VISIBLE_PRECHECK_R1.json',visual)
result['machine_gates']['Human_visible_precheck']=False
result['status']='FAIL'
result['whole_hand_placement_secondary_summary']=joined
result['visual_precheck']='FAIL; Human decision pending'
dump('MODEL_A_RESULT_R1.json',result)
gate=read(P/'MODEL_B_GATE_R1.json')
gate['visual_orientation_evidence']='Insufficient to isolate dominant depth/approach cause. Visible palm/key issues exist, but source/predicted-label/fit confounding persists.'
gate['status']='NOT_RUN_GATE_NOT_MET'
dump('MODEL_B_GATE_R1.json',gate)
ids=read(P/'INHERITED_IDENTITIES_R1.json')
dump('KEY_TABLE_IDENTITY_R1.json',ids['KEYBOARD_88_KEY_TABLE_R1.json'])
safety=read(P/'MINIMUM_SAFETY_R1.json')
safety.update({'Action_identity':'MATCHED','timeline_identity':'MATCHED','key_table_identity':'MATCHED','marker_identity':'MATCHED','natural_placement':'NOT_CLEARED','first_web':'CLOSED','LEFT_FINGERTIP_FAST_BEND':'PRESENT / DEFERRED','RIGHT_FINGERTIP_FAST_BEND':'PRESENT / DEFERRED','fast_bend_contact_cause_isolated':False})
dump('MINIMUM_SAFETY_R1.json',safety)

before=read(P/'PROTECTED_INPUTS_BEFORE_R1.json')
protection=[]
for f,v in before.items():
    now=sha(f)
    protection.append({'path':f,'before_sha256':v,'after_sha256':now,'unchanged':now==v})
assert all(r['unchanged'] for r in protection),'PROTECTED_INPUT_CHANGED'
act=read(P/'ACTION_IDENTITY_R1.json')
candidate='PIANO_KEYBOARD_LOW_DOF_ROOT_POSE_VALIDATION_CANDIDATE_R1.blend'
assert sha(P/candidate)==act['candidate_sha256']
dump('FINAL_ASSET_PROTECTION_R1.json',{'status':'PASS','protected_file_count':len(protection),'HAND_BASELINES_UNCHANGED':True,'PIANO_BASELINE_UNCHANGED':True,'previous_audit_root_files_unchanged':True,'inherited_identities':'8/8 MATCHED','policy_locks':'MATCHED','candidate_sha256':sha(P/candidate),'scope_note':'Frozen sources and prior audit root files protected. Mutable non-authority CANONICAL_UPRIGHT_ACTION_LATEST_STAGE.json excluded from inherited protection scope; never written by this phase.','files':protection})

phase='PIANO_KEYBOARD_LOW_DOF_ROOT_POSE_VALIDATION_R1'
status='ROOT_POSE_MODEL_STILL_BLOCKED'
scope='本状态针对本轮 MODEL A 候选安装：手掌放置和整体自然度未过关，不能用“只是预测指法不准”放行。它不证明所有合法 root orientation 都失败；源数据、指法和拟合误差的因果占比仍未隔离。'
questions=[
 ('Q1','上一轮 fixed-orientation model 保持 REJECTED？','YES；仅重放原缓存作对照，没有重新求解。'),
 ('Q2','MODEL A = XYZ + YAW 是否执行？','YES；完整 421 observations，全局单次求解。'),
 ('Q3','MODEL A 是否明显优于上一轮？','NO；部分朝向改善，整体自然度与接触未明显改善。'),
 ('Q4','MODEL A 多音整体 placement 是否大部分合理？','NO；粗略 pad 覆盖 R 27/38、L 64/82，但结合无掌腕压键仅 R 27/38、L 20/82。'),
 ('Q5','预测指法接触是否实质改善？','NO；R 9/39 → 7/39，L 4/26 → 3/26。'),
 ('Q6','可能指法标签冲突占失败多少？','多音 0/116；含单音 2/297（0.67%），R、L 各 1 次。分母为相关的持音观测，不是独立音符。'),
 ('Q7','ROOT_POSE_GEOMETRIC_FAILURE 是否仍为主要问题？','NO（限事前诊断桶）；多音失败中 9/116（7.76%）。这不等于整体掌部放置通过，也不证明余项由源数据造成。'),
 ('Q8','MODEL B 满足启动条件？','NO；depth/approach 20/116（17.24%），两手均未占主要失败。'),
 ('Q9','MODEL B 是否执行？','NO。'),
 ('Q10','MODEL B 是否进一步改善？','NOT_RUN。'),
 ('Q11','最终双手 keyboard placement 是否可信？','NO（agent 可见预检）；Human 审阅待定。'),
 ('Q12','Labeled contact？','RIGHT 7/39（17.95%）；LEFT 3/26（11.54%）。PREDICTED_FINGER_CONTACT，非 ground truth。'),
 ('Q13','Unlabeled cluster feasibility？','多音严格：R 1/38、L 3/82；粗略覆盖：R 27/38、L 64/82。粗略覆盖不是接触。'),
 ('Q14','掌腕碰撞是否明显降低？','NO；掌+腕观测计数 374 → 319，仅下降 14.71%，未到事前 50% 门槛。'),
 ('Q15','Root orientation / translation 是否连续自然？','NO；数值连续性 YES，自然度 NO。最大每 60Hz 步长 R 6.072mm / 1.679°，L 4.383mm / 1.357°。'),
 ('Q16','LEFT fast bend？','DEFERRED；未隔离为 contact blocker。'),
 ('Q17','RIGHT fast bend？','DEFERRED；未隔离为 contact blocker。'),
 ('Q18','最终状态？',status+'；仅指本轮候选仍阻塞，不是架构不可能性结论。')
]
fields={
 'MODEL_A_STATUS':'FAIL', 'MODEL_B_STATUS':'NOT_RUN_GATE_NOT_MET',
 'ROOT_POSE':'CONTINUOUS_BUT_PLACEMENT_NOT_VALIDATED',
 'LABELED_CONTACT':'R 7/39; L 3/26; AUTO_PREDICTED',
 'UNLABELED_CLUSTER_FEASIBILITY':'strict R 1/38, L 3/82; coarse R 27/38, L 64/82',
 'FINGERING_CONFLICT':'multi 0/116; all failed clusters 2/297 (0.67%)',
 'COLLISION_STATUS':'NOT_CLEARED; palm+wrist observations reduced 14.71%',
 'LEFT_FINGERTIP_FAST_BEND':'DEFERRED', 'RIGHT_FINGERTIP_FAST_BEND':'DEFERRED',
 'FINAL_STATUS':status,
 'NEXT_STAGE_RECOMMENDATION':'Human 审阅后，优先取得可人工核验的 hand/finger 标注及有标定依据的 motion/contact 数据，再判别 root 与 source 的因果；本轮不启动。',
 'HAND_BASELINES_UNCHANGED':'YES','PIANO_BASELINE_UNCHANGED':'YES'
}
dump('FINAL_SUMMARY_R1.json',{'phase':phase,'fields':fields,'scope':scope,'source_cause':'UNRESOLVED','questions':[{'id':q,'question':t,'answer':a} for q,t,a in questions],'STOP':'HUMAN REVIEW'})
qtable='|问题|回答|\n|---|---|\n'+'\n'.join(f'|{q} {t}|{a}|' for q,t,a in questions)
ftable='|字段|结果|\n|---|---|\n'+'\n'.join(f'|{k}|{v}|' for k,v in fields.items())
policyhash=read(P/'PRE_RESULT_POLICY_LOCK_R1.json')['hashes']
hashlines='\n'.join(f'- `{n}` SHA256 `{v}`' for n,v in policyhash.items())
report=f'''# {phase}

最终：**{status}**。**STOP — HUMAN REVIEW**。

{scope}

MODEL A 不通过；MODEL B 未达到合法启动条件，未执行。没有 MODEL C、第二轮参数 sweep 或 finger correction。不能把 `SOURCE_2_5D_OR_CONTACT_PRECISION_LIMIT` 的名称当作因果结论：它只是“粗略覆盖可行、严格接触不可行”的待解释残差。当前也不满足 C 类“root 本身已经合理”的前提，因此不以 EVIDENCE_LIMITED 状态暗示安装已成功。B 类在本报告中的结论边界是当前候选仍然阻塞；**未证实失败主要来自源/指法，也未证明排除了它们**。

## Q1–Q18

{qtable}

## 事前锁定与执行边界

冻结的 R2 / L1、双手 Action、88 键几何、canonical frame、键面、可奏区域、10 个 pad marker 全部继承。timeline 与 8 份继承 JSON 逐字节一致。上一轮固定朝向模型继续 REJECTED，仅复用已存空间缓存制作同机位视频，没有再次求解旧模型。

外部 root 属于 **PRODUCT SPATIALIZATION LAYER**；输入是 non-metric 2.5D source，不能称为真实测得 wrist-world mocap。MODEL A 只增加绕 canonical +Z 的 yaw；pitch=roll=0，scale=1。

事前范围 yaw ±60°、预留 pitch ±25°、roll ±35°。依据 approved Action 中 wrist 最大 heading 49.388°、longitudinal elevation 15.068°、bank 19.175°，再加一白键宽/掌长或黑键高度/掌长、掌宽的几何裕量，向上取整到 5°。这不是实测人体活动范围。掌宽 78.445mm、腕至中指 MCP 123.444mm；总 heading 超出 ±32.435° 软走廊受到惩罚。正常演奏外观仍须独立预检，不能靠 bounds 内即算自然。

XYZ 继承全局二阶时间正则 λ=530.8416。Yaw 使用每 0.2 秒一个 cubic B-spline control、36 个系数，同一时间正则及固定弱零先验。单个零朝向初值，单次全局 variable-projection Gauss-Newton；右 26、左 16 次迭代，没有重启、局部参数调节或重配手指。实际 yaw R −21.117°..30.842°、L −16.359°..25.222°，无系数触碰边界。

保存场景将求解曲线烘焙为 421 个 60Hz 外部 root location/quaternion 关键帧，使用同半球四元数和线性插值。数学 yaw 曲线为 C2；**Blender 烘焙回放仅保证连续，不能声称烘焙曲线本身 C2**。上限 10mm、2.207°/60Hz 均满足。

求解前保存以下 SHA256；结果后复核全部 MATCHED，未扩大 bounds：

{hashlines}

## 接触、键群、整体手掌放置

严格接触容差仍为垂直 3mm、水平 2mm，并检查原可奏键面区域。起音按原始事件时间插值测量，未吸附 MIDI timing。粗略键群覆盖另用事前半白键宽 11.545mm 水平裕量、完整白键行程 10mm 高度裕量，**不是放宽接触 PASS**。

|手 / cluster|观测|原预测标签全部接触|无标签严格可行|无标签粗略覆盖|
|---|---:|---:|---:|---:|
|R SINGLE_NOTE|189|70|71|169|
|R 2_NOTE_CLUSTER|37|1|1|27|
|R 3_PLUS_NOTE_CLUSTER|1|0|0|0|
|L SINGLE_NOTE|235|173|174|229|
|L 2_NOTE_CLUSTER|80|3|3|63|
|L 3_PLUS_NOTE_CLUSTER|2|0|0|1|

多音是主要判断依据，单音成功没有用于包装 root 成功。3+ 观测极少，不能泛化为丰富和弦验证。全手五 pad 的 span、target span、中心偏差、5×N 键面距离矩阵和诊断匹配见 `KEY_CLUSTER_PLACEMENT_METRIC_R1.json`。匹配只用于诊断，未回写 label 或输入 solver。每个 target 要求不同 pad，不能用一个 pad 覆盖多音。

同一时刻合并粗略覆盖与原掌腕碰撞结果后，多音整体放置的必要条件只有 R 27/38、L 20/82。这个合并检查没有新阈值，保留事前 pad 粗覆盖指标原值，但防止把“手指大概在音区上”误报成“手掌安装可信”。

## 失败归因与 MODEL B gate

多音原标签失败共 116 个相关 held observations：

|事前诊断类别|数量|占多音失败|
|---|---:|---:|
|LIKELY_FINGERING_LABEL_CONFLICT|0|0%|
|SOURCE_2_5D_OR_CONTACT_PRECISION_LIMIT|87|75%|
|DEPTH_OR_APPROACH_ORIENTATION_LIMIT|20|17.24%|
|ROOT_POSE_GEOMETRIC_FAILURE|9|7.76%|

87 次只意味着粗略覆盖与严格接触之间有精度缺口，**不能证明 SOURCE_2_5D_LIMIT**。9 次几何失败也只描述当前 fitted pose，不能证明所有合法 root pose 不可行。含单音的 297 次标签失败中仅 2 次可由严格无标签匹配救回；不足以认为主要失败是 predicted fingering error，也不能排除预测错误。

Finger-label-independent 匹配仍继承 predicted HAND 集合；当前 pose 本身又由原 predicted finger 拟合，因此这不是完全独立的对照。无逐事件 confidence，25 个 UNKNOWN hand 音没有自动重分。错误 hand、target、非标定 source 与根拟合误差尚未因果隔离。

MODEL B 事前要求双方及合计 depth/approach >50%，且可见证据支持主要由方向自由度受限造成。R 10/37、L 10/79、合计 20/116，均不满足。仅看到 palm 低或指尖穿键，不足以证明 pitch/roll 会解决主要误差。**不运行 B**，无 B result 或虚构改善。

## 碰撞、悬浮、可见预检

|指标（421 观测/手）|R 旧 → A|L 旧 → A|
|---|---:|---:|
|掌部压入键体|156 → 107|214 → 212|
|腕部压入键体|4 → 0|0 → 0|
|任意 mesh 顶点键体命中|293 → 288|418 → 416|

继承原 key-piece volume screen，仅计超过键面 3mm 的顶点；是候选碰撞筛查，不是完整碰撞证明。掌+腕计数总和 374 → 319，下降 14.71% 未通过事前 50%。R 起音穿透 14、悬浮 9；L 穿透 6、悬浮 0，但错键及横向不匹配仍会失败。不能用“没有悬浮”替代完整接触。

Agent 查看全部 210 个 teaching-view 输出帧及 old/A/close 时间条。开头约 source 11.50–12.17s 双腕/前臂端投影拥挤；部分时刻右手朝向更顺，但全段没有一致自然的键上落位。没有做 hidden crossing、normal-dot、逐顶点 anatomy 或 forensic macro。可见评价是 agent 预检，**不是 Human 批准**。

## 保护、timeline、最低机器检查

候选保存后重新打开，421 evaluations 全部检查；R/L geometry 最大差 0.001404/0.001175mm，marker 最大差 0.001178/0.001067mm。NaN/Inf、gross collapse、degenerate、gross tearing 均为 0；移除外部 audit root/Action 后 intrinsic ZERO digest MATCH。内部 Action digest MATCH，mesh/weights/rest/driver/corrective identity MATCH。

R2 SHA256 `c946fed318fa88c238d9aacc30cfb4e52f268848f0ad65a4dcbf594754d791f0`；L1 `54307bb199a75a5e684c29d346de9ca6bf2f8e7696911d9d69c57559516ad1a7`；R1 fallback `4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2`。全部 unchanged。正式 frozen piano 及上一轮根目录产物均 unchanged，{len(protection)} 个受保护文件全部复核。非 frozen 的 mutable latest-stage pointer 不属于此保护范围；本轮从未写入。

timeline 仍为原窗口 11.5–18.5s：92 个相交音、179 个窗口事件；原 NOTE_ON/OFF、velocity、hand、finger、timing、pedal interface 不改。本窗口无 pedal event。键运动直接复用 timeline/animation，音频接口 READY，无音源、无碰撞触发。旧动画的一个 UNKNOWN G3 约 1.04ms 音在 60Hz held sampling 中未显现，精确事件仍保留；本轮未改这个继承限制。

first-web CLOSED。双手 fast bend PRESENT / DEFERRED，尚无可隔离 contact 因果，不升级 blocker。结构保护通过不等于 spatial contact safety 通过。

## Human 审阅产物

- [审阅页](review.html)
- [完整 player + teaching 双视角](product_7s_low_dof_root_pose.mp4)
- [接触近景](product_7s_low_dof_contact_close.mp4)
- [固定朝向 vs MODEL A 同机位对照](product_7s_fixed_vs_low_dof_matched.mp4)
- [可继续检查的候选场景]({candidate})

三条视频均 7.000s / 30fps / 210 帧，三视角、旧/A 对照同 camera、同 source time、同 keyboard/key animation。对照旧段来自既有缓存，未重新优化。视频无音轨，本轮不做音源。单张 review poster；连续 PNG 是渲染中间文件，不作为大量重复图片交付。

PianoVAM：CC BY-NC-SA 4.0；仅内部非商业验证，不改变原 source/license 限制。

## 交付状态

{ftable}

**STOP — HUMAN REVIEW。等待 Human 决策。**
'''
(P/f'{phase}_REPORT.md').write_text(report,encoding='utf-8')
links=[f'{phase}_REPORT.md',candidate,'ROOT_POSE_DOF_POLICY_R1.json','ROOT_POSE_TEMPORAL_POLICY_R1.json','PRE_RESULT_POLICY_LOCK_R1.json','MODEL_A_RESULT_R1.json','MODEL_B_GATE_R1.json','KEY_CLUSTER_PLACEMENT_METRIC_R1.json','CONTACT_FAILURE_ATTRIBUTION_R1.json','CONTACT_MEASUREMENTS_R1.json','ACTION_IDENTITY_R1.json','PERFORMANCE_TIMELINE_IDENTITY_R1.json','FINGERTIP_MARKER_IDENTITY_R1.json','KEY_TABLE_IDENTITY_R1.json','MINIMUM_SAFETY_R1.json','FINAL_ASSET_PROTECTION_R1.json','VIDEO_VERIFICATION_R1.json']
linkhtml=''.join(f'<li><a href="{n}">{n}</a></li>' for n in links)
qhtml=''.join(f'<tr><th>{q} {html.escape(t)}</th><td>{html.escape(a)}</td></tr>' for q,t,a in questions)
page=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Low DOF root pose · Human review</title>
<style>body{{margin:0;background:#101924;color:#e6edf4;font:16px/1.7 system-ui,"Microsoft YaHei",sans-serif}}main{{max-width:1280px;margin:auto;padding:32px 24px 70px}}h1{{font-size:30px;line-height:1.35}}h2{{margin-top:36px}}.tag{{color:#ffbf91;font-weight:700}}.panel{{background:#1b2939;padding:20px;border-radius:12px;margin:20px 0}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}video{{width:100%;background:#080d12;border-radius:8px;display:block}}a{{color:#96d4ff}}table{{border-collapse:collapse;width:100%}}th,td{{text-align:left;vertical-align:top;border-bottom:1px solid #35465b;padding:12px}}th{{width:38%}}li{{overflow-wrap:anywhere}}small{{color:#aec0d2}}@media(max-width:800px){{.grid{{grid-template-columns:1fr}}main{{padding:20px 12px}}h1{{font-size:23px}}}}</style>
<main><div class="tag">STOP — HUMAN REVIEW · MODEL A FAIL · MODEL B NOT RUN</div><h1>钢琴教学 3D 手 × 88 键钢琴<br>低自由度根姿态验证 R1</h1>
<div class="panel"><strong>{status}</strong><p>{scope}</p><p>粗略 pad 覆盖 R 27/38、L 64/82；同时没有掌腕压键仅 R 27/38、L 20/82。预测起音接触 R 7/39、L 3/26，未改善。剩余精度误差的来源尚未隔离，不能声称 root 已合理而仅接触证据不足。</p></div>
<h2>同机位对照：旧固定朝向 → MODEL A</h2><p>同一源时间、相机、琴键运动。开头双腕拥挤；部分右手朝向更顺，但全段放置仍未过关。</p><video controls preload="metadata" poster="review_poster.jpg" src="product_7s_fixed_vs_low_dof_matched.mp4"></video>
<div class="grid"><section><h2>完整 player + teaching</h2><video controls preload="metadata" src="product_7s_low_dof_root_pose.mp4"></video></section><section><h2>Contact close</h2><video controls preload="metadata" src="product_7s_low_dof_contact_close.mp4"></video><div class="panel">严格接触保持垂直 3mm / 水平 2mm 与原键面区域。粗略覆盖采用另一组 placement 阈值，不能当作接触 PASS。<br><br>Root 为产品空间层，不是真实测得 wrist-world mocap。三条视频均 7 秒 / 210 帧 / 30fps；本轮无音源。</div></section></div>
<h2>Q1–Q18</h2><table>{qhtml}</table><h2>可复核产物</h2><ul>{linkhtml}</ul><p class="tag">Hands / Piano frozen assets unchanged · Action / timeline / key table / markers MATCHED</p><small>PianoVAM · CC BY-NC-SA 4.0 · 内部非商业验证。Agent 可见预检已完成，Human 决策待定。first-web CLOSED；双手 fast bend DEFERRED。</small></main></html>'''
(P/'review.html').write_text(page,encoding='utf-8')
for n in re.findall(r'(?:href|src|poster)="([^"]+)"',page):assert (P/n).is_file(),n
assert read(P/'VIDEO_VERIFICATION_R1.json')['status']=='PASS'
locked()
dump('DELIVERY_MANIFEST_R1.json',{'status':'PASS','phase':phase,'files':{n:{'sha256':sha(P/n),'bytes':(P/n).stat().st_size} for n in links+['review.html','review_poster.jpg','product_7s_low_dof_root_pose.mp4','product_7s_low_dof_contact_close.mp4','product_7s_fixed_vs_low_dof_matched.mp4','FINAL_SUMMARY_R1.json']},'model_B_not_run':True,'STOP':'HUMAN REVIEW'})
print(json.dumps({'status':status,'protected_files_unchanged':len(protection),'whole_hand_placement':joined,'review_links':'PASS','videos':'PASS'},ensure_ascii=False))
