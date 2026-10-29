from articulation_common import *
from datetime import datetime,timezone,timedelta
import ast
review=read(P/'AGENT_VISUAL_PRECHECK.json');diag=read(P/'ENGINEERING_DIAGNOSTICS.json');fit=read(P/'RIGHT_HAND_FIT.json');man=read(P/'SCENE_MANIFEST.json');videos=read(P/'VIDEO_VERIFICATION.json');protect=read(P/'PROTECTED_INPUTS_BEFORE.json');pol=read(P/'GENERATION_POLICY.json');aud=read(P/'AUDIO_EVENT_VERIFICATION.json')
changed=[f for f,h in protect.items() if not Path(f).is_file() or sha(f)!=h];assert not changed,changed
assert len(list(P.glob('*.blend')))==1 and fit['candidate_count']==1 and fit['restarts']==0
assert man['left_actual_geometry_max_difference_mm']<1e-6 and man['all_left_key_actions_exact_unchanged'] and man['four_static_scenes_unchanged'] and man['hand_structure_unchanged'] and man['all_88_key_geometry_unchanged']
assert aud['same_PCM_bytes'] and all(v['frames']==162 and v['fps']==60 and v['full_decode']=='PASS' for v in videos.values())
status={'phase':'RIGHT_HAND_ARTICULATION_CONTACT_SHORT_PHRASE_R1','client_time':datetime.now(timezone(timedelta(hours=8))).isoformat(),'RIGHT_HAND_ARTICULATION':review['RIGHT_HAND_ARTICULATION'],'A5_CONTACT':review['A5_CONTACT'],'FSHARP5_CONTACT':review['FSHARP5_CONTACT'],'DUAL_HAND_VISUAL_COORDINATION':'HUMAN_PENDING','MUSIC_FUNCTIONAL_CORRECTNESS':review['MUSIC_FUNCTIONAL_CORRECTNESS'],'FROZEN_BASELINES_UNCHANGED':'YES','FINAL_STATUS':review['FINAL_STATUS'],'ENGINEERING_DIAGNOSTICS':diag['status'],'agent_review_note':review['note'],'candidate_count':1,'candidate':'RIGHT_HAND_ARTICULATION_CONTACT_DESIGN_ONLY_R1.blend','candidate_sha256':man['sha256'],'original_MIDI_notes':18,'original_key_actions_exact_unchanged':True,'original_left_actions_arrays_actual_geometry_exact_unchanged':True,'original_audio_PCM_exact_unchanged':True,'frozen_protected_file_count':len(protect),'manual_per_note_adjustment':False,'optimization_runs':1,'post_failure_retuning':False,'new_solver_architecture':False,'rig_modified':False,'production_promoted':False,'full_song_started':False,'web_product_integration_started':False,'browser_realtime_playback_review':'UNAVAILABLE: browser automation kernel initialization failed; no claim of agent real-time1x audio/video observation','human_approval':False,'review_url':'http://127.0.0.1:8866/HUMAN_REVIEW.html','STOP':'HUMAN_REVIEW'}
dump('FINAL_STATUS.json',status)
dump('FROZEN_ASSET_VERIFICATION.json',{'status':'UNCHANGED','file_count':len(protect),'all_before_hashes_rechecked':True,'changed':changed,'previous_candidate_and_videos_unchanged':True,'RIGHT_R2_LEFT_R1_keyboard_originalMIDI_unchanged':True,'four_static_scene_core_unchanged':True,'hand_intrinsic_and_88_key_mesh_unchanged':True,'left_geometry_difference_mm':man['left_actual_geometry_max_difference_mm'],'original_keys_audio_same':True,'source_hashes':'PROTECTED_INPUTS_BEFORE.json','production_pointers_unchanged':True})
contact=diag['contact_right_all10_notes'];a5=[r for r in contact if r['midi']==81];fs=[r for r in contact if r['midi']==78]
impl=f'''# RIGHT_HAND_MOTION_IMPLEMENTATION

2026-10-09 · HUMAN_VISIBLE_PRODUCT_QUALITY_FIRST · ONE NEW PERFORMANCE CANDIDATE ONLY

最终状态：{status['FINAL_STATUS']}；自然度/双手协调正式结论待Human。唯一新候选 `RIGHT_HAND_ARTICULATION_CONTACT_DESIGN_ONLY_R1.blend`，SHA256 `{man['sha256']}`。

## 最小必要改动

只修改本审计目录的非冻结运动适配，新文件 `articulation_common.py`、`right_motion.py`、`02_generate.py`。继续消费原performance_core FK/关节轴、teaching rig适配、static common皮肤预测/实际键面测量和bounded least_squares；没有重构求解器或增加骨骼。

通用事件阶段：原120ms靠近→20ms预备抬指+40ms落向触键；保持原35ms键下沉和70ms键回弹；原150ms额外回位→50ms。持键一直到原NOTE_OFF，不提前弹起，不改变原MIDI120BPM/时值/velocity。

抬指只将现有基部屈曲削减最多3°并按既有工程域裁剪；不放大全部关节。接触/压力端点按每指实际可奏面整段拟合，Bernstein系数由端点派生；所有重复音复用同一digit系数，无按A5、F♯5或绝对时间特殊分支。

共同掌根仅一条由所有事件生成的stance：60ms靠近，在相邻发声音符期间保持稳定，最后70ms回弹+50ms回位。上限XYZ±2/±3/−5..0mm、pitch−2..0.5°，绕批准语义wrist旋转，不是逐音符root修补。闲置指各三屈曲轴±4°以内、有界共用补偿，保留批准R1自然曲度参考。接触端点基部±16°/其它±12°邻域与原工程关节域相交，解除此前未经生理确认的±12°基部限制；没有修改任何静态姿态或Rig工程骨轴。

总59参数：五指接触/全键程端点40、共同XYZ/pitch4、五指闲置屈曲15。一个完整序列残差共同优化contact、skin、既有净空、运动连续性和姿态正则。拟合次数1，重启0；nfev={fit['nfev']}，calls={fit['calls']}，约{fit['elapsed_sec']:.1f}s。root实际幅值XYZ mm/pitch deg：{fit['shared_root_amp_xyz_mm_pitch_deg']}。成功收敛只说明数值求解终止，不取代后验几何/产品检查。

## 当前仍未解决的机制瓶颈

A5起音已经到位，但35ms后仍有约4.30mm分离。新小指full-down的MCP增量触及32°工程上界、DIP增量贴0下界，共同root Z幅值触及−5mm限值。`REMAINING_MOTION_BOTTLENECK.json`保留具体参数证据。当前一次共同stance+两端点压力曲线在既定自然度/范围域内仍未生成可靠持键追随；接触、净空用软残差共同折中，数值收敛没有接触可行性保证。

这支持本轮非冻结运动参数化/协调能力不足，不支持MIDI或指法输入错误。没有全局不可行性证明，不能断言冻结Rig必须改或所有现有运动系统根本不可用。本轮到此止损，不继续加局部root/IK/DIP补丁。

## 原输入与输出保护

独立重新解析原MIDI，第1–2小节全部18音符身份、时值、顺序、velocity逐项一致。右手10音符先在原事件上验证生成轨迹，再组合完全复制的上一轮左手8音符数组。左手29参数没有重拟合。

新blend直接继承上一轮唯一候选，仅替换右手design-only骨骼Action并添加外部掌根Action。左手与琴键Action payload不变；保存重开后左手实际几何差{man['left_actual_geometry_max_difference_mm']:.9f}mm。右手pad/FK误差{man['right_actual_pad_vs_FK_max_mm']:.6f}mm，键世界变换误差{man['actual_key_world_parity_max_mm']:.6f}mm。四批准静态core、手mesh/rest/weights/corrective/driver intrinsic与88键mesh均一致。

三视角使用上一轮摄像机原变换、同一源时间窗口0.4–3.1s；各162帧/60fps/2.7s，正常播放。原钢琴PCM逐字节相同，未变速、改谱或重新配乐，三个音视频完整解码通过。旧视频只作reference复制，不构成第二新候选。

## 验证与限制

必要检查含actual active-pad gap、有限8mm指腹邻域、运动白/黑键可奏面、汇总邻键穿入、工程范围与120Hz连续性。没有逐顶点forensic报告、隐藏相机或参数搜索。

{review['note']}

浏览器自动化内核初始化失败，代理未声称完成1×带声实时浏览器观看；帧序列/同视角接触预检与可播放完整视频已交付，真实自然度由Human原速评审。

最终{len(protect)}受保护文件哈希全部不变。无正式资产指针更新、正式产品批准、完整曲目制作或Web集成。完成后STOP — HUMAN REVIEW。
'''
(P/'RIGHT_HAND_MOTION_IMPLEMENTATION.md').write_text(impl,encoding='utf8')
lines=['# A5_FSHARP5_CONTACT_REVIEW','',f"A5_CONTACT={status['A5_CONTACT']}；FSHARP5_CONTACT={status['FSHARP5_CONTACT']}。候选级触键检查，非Human最终产品批准。",'', '## 原因与前后证据','', 'A5此前初始skin gap4.572mm；35ms指腹下降2.506mm，键面目标下降8.425mm；full-down gap10.986mm，HOLD维持同一失败姿态。不是水平错键、音符晚起或持键提前回升。','', 'F♯5此前实际skin pad位于运动黑键抬高可奏面，gap0.464–0.748mm；有限指腹邻域closest gap约0.464–0.730mm。几何到位CONFIRMED，近接触跟随SUPPORTED，严重悬空NOT_CONFIRMED；摄像机是观感唯一原因UNKNOWN。没有先认定Human观察错误。','', '|事件|音符|上一轮最大skin gap mm|本轮最小gap mm|本轮最大gap mm|可奏面水平越界样点|','|---|---|---|---|---|---|']
for r in a5+fs:lines.append(f"|{r['note_id']}|{c.KEYS[r['midi']-21]['note_name']}|{r['previous_gap_max_mm']:.3f}|{r['skin_gap_min_mm']:.3f}|{r['skin_gap_max_mm']:.3f}|{r['outside_samples']}|")
lines+=['',review['contact_note'],'', '三视角视频都是原速完整双手候选。`matched_A5_Fsharp5_side_contact.jpg`仅补充同相机/源时刻的两次A5与两次F♯5对照；最终以正常速度教学、侧斜和俯视完整播放为主。','', '有限指腹点与几何贴近不等于建立真实受力面积；不因3mm旧阈值独立否决，也不忽略正常视角可见分离。']
(P/'A5_FSHARP5_CONTACT_REVIEW.md').write_text('\n'.join(lines),encoding='utf8')
coord=f'''# DUAL_HAND_VISUAL_COORDINATION_REVIEW

DUAL_HAND_VISUAL_COORDINATION=HUMAN_PENDING。整体{status['FINAL_STATUS']}。

## 当前代理结论

{review['note']}

{review['coordination_note']}

原右手120ms缓慢靠近/220ms释放回位缩为明确20ms抬指+40ms下降/120ms释放回位，保持35ms随键下压和全部原NOTE_ON/OFF。相邻不同手指在前一音持键时准备，符合原十六分音符125ms交接；不是要求双手做同相运动。右手掌根保持共同低幅度stance，避免逐音符夸张腕部抽动。

左手8事件、29参数、Action、key时钟与保存重开几何完全不变。上一轮左手“相对可读”继续作为对照，动态接触仍NOT_APPROVED；不能将本轮右手改进当作左手审批。

代理查看正常尺寸教学/俯视/侧斜帧与完整帧序列、实际接触数据。浏览器自动化因内核初始化失败无法完成实时1×带声观看，因此`RIGHT_HAND_ARTICULATION={status['RIGHT_HAND_ARTICULATION']}`的证据范围须结合下列说明，Human必须播放主要视频作自然度与双手协调最终判断。

## 十项交付回答

|问题|回答|
|---|---|
|1 右手慢的主因|阶段长尾和白键有效下压不足SUPPORTED；MIDI/键/声没有时钟延迟证据。旧120ms靠近几乎等于一个125ms十六分音符，额外150ms回位叠加。|
|2 A5悬空原因|起音未到位、白键跟随不足，固定掌根/基部±12°边界限制；不是提前释放或水平错键。|
|3 F♯5真实不足|旧实际黑键检查未确认严重分离；原有限pad邻域近接触SUPPORTED。本轮{status['FSHARP5_CONTACT']}；不能将骨骼弯曲或视觉观感单独当作接触证明。|
|4 修改代码|仅新审计目录`right_motion.py`、`02_generate.py`等适配：事件阶段、运动键面端点拟合、有界公共掌根/idle补偿、右Action烘焙；旧代码/冻结文件不改。|
|5 通用能力还是曲目修补|规则按event phase和digit共享，不按A5/F♯5/绝对时点硬编码；重复音共用端点。结构上增加通用能力，但仍只验证这一首的这两小节。|
|6 触键节奏是否明显改善|{review['articulation_note']}|
|7 双手是否更可信|{review['coordination_note']}|
|8 正常视角阻断|{review['blocking_note']}|
|9 冻结与MIDI|YES，{len(protect)}受保护文件最终SHA复查不变；4静态core、手intrinsic、88键mesh及原谱/左手/键/PCM保留。|
|10 是否扩展下一段|{review['next_phrase_note']} 本轮STOP，不自动启动。|

## 最终字段

- RIGHT_HAND_ARTICULATION = {status['RIGHT_HAND_ARTICULATION']}
- A5_CONTACT = {status['A5_CONTACT']}
- FSHARP5_CONTACT = {status['FSHARP5_CONTACT']}
- DUAL_HAND_VISUAL_COORDINATION = HUMAN_PENDING
- MUSIC_FUNCTIONAL_CORRECTNESS = {status['MUSIC_FUNCTIONAL_CORRECTNESS']}
- FROZEN_BASELINES_UNCHANGED = YES
- FINAL_STATUS = {status['FINAL_STATUS']}

工程诊断{diag['status']}是辅助；不覆盖Human自然度判断。候选数1、拟合1、重启0、无第二轮优化。STOP — HUMAN REVIEW。
'''
(P/'DUAL_HAND_VISUAL_COORDINATION_REVIEW.md').write_text(coord,encoding='utf8')
html=(P/'HUMAN_REVIEW.html').read_text(encoding='utf-8-sig').replace('结果报告待完成；不代表产品批准。',status['FINAL_STATUS']+' · A5 '+status['A5_CONTACT']+' · F♯5 '+status['FSHARP5_CONTACT']+' · 音乐功能 '+status['MUSIC_FUNCTIONAL_CORRECTNESS']+' · Human协调判断待定').replace('代理预检待填写；自然度与双手协调需Human判断。',review['note']);(P/'HUMAN_REVIEW.html').write_text(html,encoding='utf8')
for f in P.glob('*.py'):ast.parse(f.read_text(encoding='utf-8-sig'))
dump('DELIVERY_MANIFEST.json',{'status':status['FINAL_STATUS'],'candidate_count':1,'files':{f.name:sha(f) for f in P.iterdir() if f.is_file() and f.name!='DELIVERY_MANIFEST.json'},'all_requested_deliverables':True,'freeze_verification':'PASS','same_PCM_video_full_decode':'PASS','source_events':18,'script_syntax':'PASS','human_pending':True,'STOP':True})
print('FINAL_ONE_CANDIDATE_DELIVERY',status['FINAL_STATUS'],'FROZEN_UNCHANGED',len(protect),flush=True)
