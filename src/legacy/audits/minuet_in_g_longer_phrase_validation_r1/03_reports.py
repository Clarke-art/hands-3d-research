from pathlib import Path
import json,hashlib,ast
from datetime import datetime,timezone,timedelta
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
s=read(P/'MIDI_SCOPE_STATISTICS.json');d=read(P/'FEASIBILITY_DECISION.json');provenance=read(P/'SOURCE_PROVENANCE.json');fp=read(P/'FINGERING_PREFLIGHT.json');protect=read(P/'PROTECTED_INPUTS_BEFORE.json')
changed=[f for f,h in protect.items() if not Path(f).is_file() or sha(f)!=h];assert not changed
assert not list(P.rglob('*.blend')) and not list(P.rglob('*.mp4')) and not list(P.rglob('*.npz'))
assert sha(P/'source/anna-magdalena-04.mid')==provenance['files']['anna-magdalena-04.mid']['sha256']
status={'phase':'MINUET_IN_G_LONGER_PHRASE_VALIDATION_R1','client_time':datetime.now(timezone(timedelta(hours=8))).isoformat(),'HUMAN_VISIBLE_QUALITY':'HUMAN_PENDING','MUSIC_FUNCTIONAL_CORRECTNESS':'UNKNOWN','CHORD_OR_MULTI_FINGER_SUPPORT':'NOT_ESTABLISHED','ENGINEERING_DIAGNOSTICS':'WARN','GENERALIZATION_EVIDENCE':'NOT_ESTABLISHED','FROZEN_BASELINES_UNCHANGED':'YES','FINAL_STATUS':'FAIL_CLOSED','failure_stage':'READ_ONLY_EXECUTABILITY_PREFLIGHT_BEFORE_MOTION','blocking_reason':'Current qualifiedleft generator is tied toD2/D3 two active tasks, currentright uses five fixed digit endpoint pairs and one stance; no key/hand-position-conditioned multi-contact/long-root organizer. Source requires openingleft3-note chord,8left/9right distinct keys across changing positions.','no_physical_Rig_infeasibility_claim':True,'Musette_Human_product_acceptance_preserved':True,'selected_MIDI':'source/anna-magdalena-04.mid','source_MIDI_sha256':s['source_sha256'],'edition':'Mutopia-2017/01/19-75 originalkeyboard','source_tick_range':[0,18432],'source_music_time_range_sec':[0,20.571408],'source_duration_sec':20.571408,'original_note_count':102,'right_notes':65,'left_notes':37,'original_event_count':204,'candidate_count':0,'motion_optimizations':0,'new_actions':0,'rendered_videos':0,'score_simplified':False,'original_source_bytes_unchanged':True,'per_note_manual_animation':False,'existing_motion_code_modified':False,'full_phrase_fingering_validated':False,'protected_file_count':len(protect),'visual_and_geometry_review_not_performed':True,'geometry_values_not_fabricated':True,'main_deliverable':'MIDI_SCOPE_AND_FEASIBILITY.md','review_url':'http://127.0.0.1:8867/HUMAN_REVIEW.html','STOP':'HUMAN_REVIEW'}
dump('FINAL_STATUS.json',status)
dump('ENGINEERING_DIAGNOSTICS.json',{'status':'WARN','stage':'PRE_GENERATION_CAPABILITY_AUDIT','dynamic_measurement_performed':False,'reason':'No candidate was generated; current task-conditioned/chord/long-position movement capability is not established. WARN does not mean measured geometric violation.','active_pad_gap_mm':None,'multi_finger_pad_gap_mm':None,'neighbor_key_penetration_mm':None,'joint_bound_violation_deg':None,'trajectory_continuity':None,'near_limit_dwell_sec':None,'moving_key_contact_samples':None,'no_forensic_geometry_review':True,'no_millimeter_threshold_veto':True,'scope_verification':{'original_source_notes':102,'note_on_off_events':204,'time_range_sec':[0,20.571408],'left_peak_polyphony':3,'right_peak_polyphony':1,'dual_peak_polyphony':4,'same_hand_different_onset_held_overlap':0,'tempo_identity_preserved':True,'no_clipped_boundary_notes':True},'source_code_capability_evidence':'FEASIBILITY_DECISION.json','geometry_failure_claim':False,'frozen_protection':'PASS'})
dump('FROZEN_ASSET_VERIFICATION.json',{'status':'UNCHANGED','snapshot_file_count':len(protect),'all_before_sha256_rechecked':True,'changed':changed,'official_hand_R2_L1_bytes_match_authority':True,'approved_four_static_source_scene_bytes_match_manifest':True,'existing_keyboard_MIDI_audio_mappings_and_runtime_bytes_unchanged':True,'new_original_Minute_MIDI_source_bytes_unchanged':True,'no_blend_loaded_or_written':True,'no_actions_written':True,'no_production_pointer_change':True,'Human_Musette_acceptance_recorded_without_overwriting_historical_engineering_status':True,'source_before_hashes':'PROTECTED_INPUTS_BEFORE.json'})
# MIDI evidence remains source-grounded; all performances/geometry are explicitly not run.
scope=f'''# MIDI_SCOPE_AND_FEASIBILITY

2026-10-09 · HUMAN_VISIBLE_PRODUCT_QUALITY_FIRST · 只读可执行性核查 · FAIL_CLOSED

本轮未生成动作、候选或视频。原因是当前合格运动入口缺少目标键/手位相关的姿态组织与左手三指同时接触机制，不能仅替换输入MIDI就真实演奏本段。没有依据断言冻结Rig本身物理不可行。

## 原始版本与来源

工程内初始没有BWV Anh.114文件；已按Human明确回复采用同一Mutopia上游键盘原版。采用[Mutopia作品75](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=75)，版本 `Mutopia-2017/01/19-75`、LilyPond2.19.49、维护AllenGarvin、Source标注Bach-Gesellschaft、Public Domain。排除吉他、小号和弦乐改编版。

原MIDI：[anna-magdalena-04.mid](source/anna-magdalena-04.mid)，下载URL `https://www.mutopiaproject.org/ftp/BachJS/BWVAnh114/anna-magdalena-04/anna-magdalena-04.mid`；SHA256 `{s['source_sha256']}`。原[乐谱源码](source/anna-magdalena-04.ly)、来源页HTML及响应URL/字节哈希一并保存。原文件只下载和读取，未改谱、改速、删音或替换velocity。

## 前16小节实际范围

|项|实测值|
|---|---|
|格式/PPQ|SMF1 /384|
|拍号|3/4，无弱起|
|速度|源码四分音符140；原MIDI428571μs/四分音符，编码实际约140.00014BPM|
|每小节|1152 ticks|
|NOTE_ON范围|[0,18432)，第1–16小节|
|尾端NOTE_OFF|18432，完整保留，无音符裁断|
|音乐时钟|0–20.571408秒，按原tempo积分|
|NOTE_ON/NOTE_OFF|102/102，204事件|
|右手/左手|65/37音符|
|MIDI velocity|全部90，保留原值|
|全源文件|32小节，36864ticks，约41.142816秒|

LilyPond第一段含16小节volta2重复记号，原MIDI没有展开重复，线性编码第一、第二16小节各一次。本轮明确选第一段一次，不自行补重复；原前16小节含谱内旋律再现，构成第一重复段完整收束。下一小节在tick18432开始，不纳入本段。

右手65音符含原MIDI保留的B4倚音：43ticks约47.991ms，最近两次起音间隔44ticks约49.107ms。它在MIDI中提前进入第7小节末的tick窗口，但对应源码第8小节倚音；保留原时间，不按文字位置重排。普通八分音符间隔192ticks约214.286ms；mordent/prall等谱面装饰不手工扩展为新事件。

## 声部、和弦与位移需求

左右手由源码Staff one/voiceone与Staff two/voicetwo映射到MIDITrack1 `one:` /Track2 `two:`；不是按高低音随意拆手。

- 右手：单音旋律，F♯4–G5（13半音跨度），9不同音高，包含倚音与连续八分交替。MIDI最大同时持音1。
- 左手：G2–D4（19半音跨度），8不同音高。第1小节tick0的G3/B3/D4三音和弦同时按下，三音均持到tick768（0.857142秒），然后A3。其余为单音长持/低音流动，13个音符时值至少二拍。
- 左手峰值3，双手峰值4。同手除首和弦外，没有不同起音之间的实际MIDI持音重叠；琴键回弹/手指释放动作的重叠另属运动规划问题。
- 音区与现有Musette固定手位不同，必须组织覆盖不同键/手位的动作；具体腕路尚未求解，未虚构毫米轨迹。

全部逐音符证据见[CSV](ORIGINAL_EVENTS_FIRST16.csv)与[MIDI_SCOPE_STATISTICS.json](MIDI_SCOPE_STATISTICS.json)。

## Q1–Q3可执行性判断

**Q1：当前合格入口不能合理直接支持这一完整结构。** 它具有FK/skin/键面评价和Action烘焙等可复用基础，但当前右手每指只有一对固定接触/下压端点；NOTE_ON时同digit使用同一接触姿态，整个相邻乐句的root stance保持同幅值。9个不同键无法由5个固定接触点和固定手位合法覆盖。左手仍是D2/D3两类压力曲线与固定键17/29驱动的29参数动作，缺少G3/B3/D4三主动指任务入口。

**Q2：CHORD_OR_MULTI_FINGER_SUPPORT=NOT_ESTABLISHED。** MIDI、88键、混音接口可表示多音，多个digit阶段数组有部分表示基础；这不证明三指实际接触。未渲染和弦，不能声称“和弦肉眼失败”，也不能把键与声支持写成真实演奏通过。

**Q3：不只是换事件列表。** 需要建立按目标键/手位条件变化的指姿态、左手联合和弦接触与较长双手位置/指法组织机制。旧独立逐指/逐时刻IK原型虽然有任意目标接口，但root仍固定，依赖外部home与fingering配置，未提供合格的长段换位/联合三指规划。以它取代现有合格入口并补齐这些核心能力，超出本轮有限复用适配判断；不把未验证核心当作已存在功能。

源码证据与具体行号见[FEASIBILITY_DECISION.json](FEASIBILITY_DECISION.json)。该结论是软件入口与本轮范围判断，不是仅凭“没试过”宣称数学不可行，也不是否定Human已接受的Musette产品观感。

## 止损决定

在动作生成前FAIL_CLOSED，候选0、求解0、Action0、视频0。未简化首三音和弦，未删除倚音，未手动逐音符动画，未修改冻结资产。按本轮“当前系统无法合理支持核心结构则停止”的规则，不为强行产出视频新增一套尚未建立的核心规划。
'''
(P/'MIDI_SCOPE_AND_FEASIBILITY.md').write_text(scope,encoding='utf8')
lines=['# FINGERING_AND_EVENT_PLAN','', '状态：NOT_COMMITTED_NOT_EXECUTABLE_PREFLIGHT_STOP。全段可执行指法尚未建立，不套用Musette的固定pitch→finger字典，也不凭此表伪造手部动作。','', '原LilyPond未提供钢琴手指编号。仅给出首小节的音乐级候选参考：右D5/G4/A4/B4/C5 →5/1/2/3/4；左G3/B3/D4 →5/3/1，三指必须同时持到tick768。它们不是已批准的新静态姿态或已验证可执行指法。','', '剩余全段指法UNASSIGNED：必须结合不同手位、倚音、重复音、持键及和弦的同时唯一指分配建立通用方案。本轮在核心能力核查失败后不虚构后续分配。','', '|小节|源tick范围|右手原序列|左手原序列|R/L音符数|','|---|---|---|---|---|']
for row in s['measure_rows']:
 R=' → '.join(n['note_name'] for n in row['R_sequence']);L=' → '.join(n['note_name'] for n in row['L_sequence']);
 if row['measure']==1:L='[G3+B3+D4] 同时持键 → A3'
 if row['measure']==7:R+='（末端B4为第8小节倚音的MIDI提前编码）'
 lines.append(f"|{row['measure']}|{row['tick_range'][0]}–{row['tick_range'][1]}|{R}|{L}|{row['R_notes']}/{row['L_notes']}|")
lines+=['', '音符身份/时值/velocity及独立on/off见原事件CSV，显示序列不替代精确时值。第一左三音为唯一同起和弦；其余左手长音与流动单音。右手含65单音事件，无真正同时按下的右和弦。','', '102 NOTE_ON与102 NOTE_OFF全部保留，未跳过和弦、持续音、倚音或低G2。没有新增音符、删音、改速度或修改原MIDI。']
(P/'FINGERING_AND_EVENT_PLAN.md').write_text('\n'.join(lines),encoding='utf8')
impl=f'''# IMPLEMENTATION_REPORT

本轮完成可验证源下载、原MIDI精确解析及有限只读可执行性核查；在生成前FAIL_CLOSED。候选/动作/视频均0。没有对原Musette重新作视觉验收，承接当前Human“产品视角可接受”的新权威，并保留历史工程结果。

## 复用与新代码

复用了项目内mido读取依赖、现有声部→左右手与MIDI−21的88键身份约定、已有冻结权威/哈希保护方法。只读检查现有FK/skin、事件阶段、运动键面残差、原逐指IK、Action烘焙及PCM接口；未运行运动求解或渲染。

新非冻结文件仅在本审计目录：`00_source.py`（原始来源/字节哈希保存）、`01_scope.py`（tempo积分、102事件对、声部/多音/逐小节统计）、`02_preflight.py`（源码能力证据/冻结快照）、`03_reports.py`（报告与最终保护验证）、`HUMAN_REVIEW.html`及本地服务器。现有运动代码、正式资产指针、原Musette文件、琴键/声音runtime未修改。

这些是通用审计/输入统计机制，不是新增演奏能力。没有按音符手调pose、手工独立动画、逐帧修补、参数搜索、隐藏角度渲染或第二次优化。

## 为什么没有生成候选

源音乐从第1小节就要求左手G3/B3/D4三指同时接触，后续两手8/9不同键及新手位，右手有倚音。当前合格左轨迹仍 tied toD2/D3，当前右轨迹的五指固定端点/共同stance不以当前pitch/手位改变。通用phase数组与数据层多音支持不等于联合多指触键。

建立缺失的目标键/手位条件姿态、多指接触和较长根路径/指法组织属于新的核心动作能力，不能伪称已有链路只改一张曲目表就能完成。根据用户显式止损条件，在本轮产品验证范围内不引入并临时审批这些未建立机制；不做简化版本或键/声-only假演奏。

既有FK/Rig可能成为后续能力建立的基础，本轮未证明冻结Rig物理不可行，也未要求改Rig。这里的NOT_ESTABLISHED针对真实新曲演奏能力，Human接受Musette不受撤销。

## 原输入与冻结保护

Mutopia键盘原版MIDI/乐谱源码保持下载原字节；tempo428571μs/q、全部102音符与204事件、首三音和弦与倚音都保留。未输出改编或裁音MIDI。

最终复查{len(protect)}个受保护文件哈希全部一致，包括正式RIGHT_R2、LEFT_L1、四批准静态源、Grand键盘/映射/音频链及原审计输入。未加载或保存任何blend，未写任何Action，未产生演奏视频。工程诊断数值均null/NOT_RUN，不虚构动态gap或穿入测量。

HUMAN_REVIEW页面审核的是本轮可执行性证据，明确标示“无新候选/无视频”。最终STOP — HUMAN REVIEW，不启动完整曲目或Web产品集成。
'''
(P/'IMPLEMENTATION_REPORT.md').write_text(impl,encoding='utf8')
review=f'''# HUMAN_VISIBLE_REVIEW

**FAIL_CLOSED：在只读可执行性核查阶段停止。** 没有新手部动作、候选blend或演奏视频，不能给这20.571408秒乐句做肉眼自然度评分。

HUMAN_VISIBLE_QUALITY=HUMAN_PENDING仅表示未作新视觉判断，不代表存在已生成待验收视频。MUSIC_FUNCTIONAL_CORRECTNESS=UNKNOWN，ENGINEERING_DIAGNOSTICS=WARN（未运行动态测量）。没有看到新曲的悬空/错键/穿键/跳变，所以既不声称发生这些错误，也不声称没有这些错误。

当前首三音和弦、不同目标键/手位组织不在合格运动入口的实际能力内；直接换MIDI会失配，故按用户止损条件0候选停止。NOT_ESTABLISHED不是Rig物理失败判断。用户本轮给出的Musette产品视觉接受结论完整承接，历史工程验收记录不改写。

## 最终18项回答

|问题|结论|
|---|---|
|1 MIDI文件|新保存的Mutopia-2017/01/19-75键盘原版 `source/anna-magdalena-04.mid`，用于只读预检；未用于动作生成。|
|2 前16小节范围|NOTE_ON tick[0,18432)，尾端NOTE_OFF保留至18432；源音乐0–20.571408s；第一16小节一次、不补重复。|
|3 时长|20.571408s，由原tempo428571μs/q积分。|
|4 音符总数|102（右65、左37），204 on/off事件。|
|5 结构|右F♯4–G5单音旋律、连续八分与倚音；左G2–D4低音长持/流动单音，开头G3+B3+D4三音和弦。|
|6 当前是否合理支持|当前合格入口不能直接支持全段；缺少目标键/手位条件姿态、左手三主动指任务和长段换位组织。|
|7 多指/和弦如何处理|首左三音同起同释，须3独立指共同持到tick768。真实contact NOT_ESTABLISHED；没有丢音、拆和弦或假装已处理。|
|8 非冻结代码修改|新增来源/解析/预检/报告代码；既有运动模块0修改。|
|9 通用机制还是定制|新代码为输入/统计审计，可复用；未新增运动能力，不能包装成跨曲目运动泛化。|
|10 手工修补|无动作生成，因此无逐音符pose/动画/逐帧修补。初始指法仅音乐级候选参考，非完整执行计划。|
|11 正常视角自然可信|未生成，UNKNOWN；没有借用Musette视频冒充本曲。|
|12 可见错误|未渲染、未判断，UNKNOWN；不是“未发现就PASS”。|
|13 音乐功能|UNKNOWN；源MIDI身份/范围核实PASS不等于新曲手/键/声演奏通过。|
|14 工程诊断|WARN，阶段能力缺口，动态几何数据NOT_RUN/null；不是毫米超限否决。|
|15 跨曲目复用证据|NOT_ESTABLISHED；有可复用FK/skin/数据/烘焙基础，尚未形成本段真实演奏证据。|
|16 是否继续扩展|当前不建议直接扩长演示；先建立并独立验证新手位和左多指接触能力。本轮不自动推进。|
|17 主要真实产品缺陷|当前生成器缺乏多目标键/手位与左三指和弦的可信动作机制；不是缺键/缺音频，也非已证明冻结Rig缺陷。|
|18 冻结是否不变|YES，{len(protect)}受保护文件最终SHA一致，无blend/Action写入，原谱/速度/映射/PCM链保留。|

## 最终字段

- HUMAN_VISIBLE_QUALITY = HUMAN_PENDING
- MUSIC_FUNCTIONAL_CORRECTNESS = UNKNOWN
- CHORD_OR_MULTI_FINGER_SUPPORT = NOT_ESTABLISHED
- ENGINEERING_DIAGNOSTICS = WARN
- GENERALIZATION_EVIDENCE = NOT_ESTABLISHED
- FROZEN_BASELINES_UNCHANGED = YES
- FINAL_STATUS = FAIL_CLOSED

0候选、0求解、0视频；没有第二轮优化，也没有为了产出视频简化原乐谱。STOP — HUMAN REVIEW。
'''
(P/'HUMAN_VISIBLE_REVIEW.md').write_text(review,encoding='utf8')
rows=''.join(f"<tr><td>{r['measure']}</td><td>{r['tick_range'][0]}–{r['tick_range'][1]}</td><td>{r['R_notes']}</td><td>{r['L_notes']}</td></tr>" for r in s['measure_rows'])
html=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Minuet in G · 只读可执行性审核</title><style>body{{margin:0;background:#f3f1e9;color:#20372e;font:16px/1.65 system-ui,"Microsoft YaHei",sans-serif}}main{{max-width:1100px;margin:auto;padding:28px}}h1{{font-size:28px}}.panel{{background:white;padding:22px;border-radius:14px;margin:20px 0}}.status{{background:#eee0d7;padding:12px 16px;border-radius:10px}}a{{color:#315f49}}table{{border-collapse:collapse;width:100%}}td,th{{text-align:left;border-bottom:1px solid #dbe1d5;padding:8px}}.note{{color:#56705c}}</style><main><p class="status"><strong>FAIL_CLOSED · 在动作生成前停止 · 0候选 /0视频</strong></p><h1>G大调小步舞曲 · 前16小节可执行性审核</h1><p>采用Human选定的Mutopia原键盘版 · 原速140BPM标记 · 源事件不变</p><div class="panel"><strong>没有新的演奏视频</strong><p>本轮首先核查真实音乐结构。开头左G3+B3+D4要求三指同时持键；当前左D2/D3轨迹与右五指固定端点/共同stance没有目标键与手位条件化机制，不能仅换入新MIDI就完成这段演奏。为避免改谱、拆和弦或伪造自动演奏，未启动求解或渲染。</p><p>HUMAN_PENDING表示没有新视觉评分；请审核本轮能力证据。没有借用旧曲视频冒充本曲。此判断不撤销Human对Musette产品视角的接受，也不证明冻结Rig物理不可行。</p></div><div class="panel"><table><tr><th>原输入项</th><th>实测</th></tr><tr><td>文件</td><td>anna-magdalena-04.mid · Mutopia-2017/01/19-75键盘版</td></tr><tr><td>前16小节</td><td>tick[0,18432)，尾端NOTE_OFF保留</td></tr><tr><td>时长</td><td>20.571408秒 · 原tempo428571μs/q积分</td></tr><tr><td>音符</td><td>102：右65、左37 · 204 on/off事件</td></tr><tr><td>右手</td><td>F♯4–G5，9音高，单音旋律含倚音</td></tr><tr><td>左手</td><td>G2–D4，8音高，首三音和弦与单音长持/流动</td></tr><tr><td>峰值</td><td>左手3、右手1、双手4</td></tr><tr><td>冻结保护</td><td>{len(protect)}文件SHA全部一致，无blend/Action写入</td></tr></table></div><div class="panel"><strong>原始事件证据</strong><p><a href="source/anna-magdalena-04.mid">原MIDI下载</a> · <a href="source/anna-magdalena-04.ly">原LilyPond乐谱</a> · <a href="https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=75">Mutopia来源</a> · <a href="ORIGINAL_EVENTS_FIRST16.csv">102音符CSV</a> · <a href="MIDI_SCOPE_STATISTICS.json">精确统计JSON</a></p><table><tr><th>小节</th><th>tick窗口</th><th>右音符</th><th>左音符</th></tr>{rows}</table><p class="note">第7小节计入提前编码的第8小节B4倚音；保留MIDI原时刻，不重排或删去。</p></div><div class="panel"><strong>报告</strong><p><a href="MIDI_SCOPE_AND_FEASIBILITY.md">范围与可执行性</a> · <a href="FINGERING_AND_EVENT_PLAN.md">指法/事件预计划</a> · <a href="IMPLEMENTATION_REPORT.md">实现与边界</a> · <a href="HUMAN_VISIBLE_REVIEW.md">18项回答</a> · <a href="FEASIBILITY_DECISION.json">源码能力证据</a> · <a href="ENGINEERING_DIAGNOSTICS.json">工程诊断（动态未运行）</a> · <a href="FINAL_STATUS.json">最终状态</a></p></div><p class="note">STOP — HUMAN REVIEW · 未启动完整曲目或Web产品集成。</p></main></html>'''
(P/'HUMAN_REVIEW.html').write_text(html,encoding='utf8')
for f in P.glob('*.py'):ast.parse(f.read_text(encoding='utf-8-sig'))
dump('DELIVERY_MANIFEST.json',{'status':'FAIL_CLOSED','failure_stage':'BEFORE_GENERATION','required_reports_present':True,'candidate_count':0,'video_count':0,'motion_solves':0,'preserved_source_notes':102,'full_source_original_bytes_preserved':True,'all_protected_files_unchanged':True,'script_syntax':'PASS','files':{f.relative_to(P).as_posix():sha(f) for f in P.rglob('*') if f.is_file() and f.name!='DELIVERY_MANIFEST.json'},'stop':True})
print('FINAL_PREFLIGHT_FAIL_CLOSED_SOURCE102_NOTES_PROTECTED',len(protect),'NO_CANDIDATE_NO_VIDEO',flush=True)
