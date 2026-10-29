from stage_common import *
import urllib.request
diag=read(P/'ENGINEERING_DIAGNOSTICS.json');fit=read(P/'COORDINATED_TRAJECTORY_FIT.json');man=read(P/'SCENE_MANIFEST.json');posture=read(P/'VISIBLE_POSTURE_EVIDENCE.json')
protected=read(P/'FROZEN_AND_PRIOR_BASELINE_VERIFICATION.json');assert protected['all_protected_hashes_unchanged']
fr=read(P/'VIDEO_FRAMING_REPAIR.json');assert fr['no_pose_or_solver_change'] and fr['candidate_sha256']==sha(man['path']) and fr['motion_sha256']==sha(P/'motion.npz')
status=dict(phase='MINUET_STAGE_B_R2_LEFT_HAND_CONTINUOUS_ACCOMPANIMENT',client_date='2026-10-10',
    LEFT_HAND_FOUR_BAR_EVENTS='VERIFIED',LEFT_HAND_CONTINUOUS_MOTION='PARTIAL',CHORD_TO_SINGLE_TRANSITION='PARTIAL',
    MULTI_FINGER_COORDINATION='PASS',MUSIC_FUNCTIONAL_CORRECTNESS='PASS',ENGINEERING_DIAGNOSTICS='WARN',
    HUMAN_VISIBLE_QUALITY='HUMAN_PENDING',GENERALIZABLE_LEFT_HAND_MECHANISM='PARTIAL',
    STAGE_A_R2_APPROVED_BASELINE_PRESERVED='YES',STAGE_B_R1_BASELINE_PRESERVED='YES',FROZEN_ASSETS_UNCHANGED='YES',
    FINAL_STATUS='FAIL_CLOSED',
    product_precheck='FAIL_VISIBLE_IDLE_HAND_SPREAD_DURING_SINGLE_LONG_NOTES',
    technical_PASS_not_naturalness_approval=True,blocking_visible_defect='Idle thumb/little extend into a wide open hand during B3/C4 long single notes; relaxed five-finger preparation relationship not maintained.',
    supported_architecture_limit='Static L1/L2 joint prior and collision clearance are insufficient to organize all inactive fingers around the current event-relative hand layout. Only index/ring received time-local idle-domain treatment.',
    new_dynamic_candidates=1,post_render_refits=0,manual_note_finger_patches=False,second_dynamic_candidate=False,
    source_notes=7,source_note_on_count=7,source_note_off_count=7,source_duration_sec=5.142852,source_tick_range=[0,4608],
    provisional_fingers=[5,3,1,4,3,2,3],fingering_changed_after_render=False,original_MIDI_unchanged=True,
    true_different_onset_music_held_overlaps=0,adjacent_same_key_restrikes=0,required_large_register_shift=False,
    mechanical_task_peak=4,solver_converged=fit['success'],solver_nfev=fit['nfev'],
    video_frames=357,video_fps=60,video_duration_sec=5.95,right_hand_motion_or_audio=False,
    Agent_full_realtime_audiovisual_review='NOT_PERFORMED_BROWSER_HELPER_INITIALIZATION_FAILURE',
    browser_error='windows sandbox failed: helper_unknown_error: setup refresh had errors',
    visible_pose_failure_based_on_normal_frames_and_persistent_hold_data_not_full_naturalness_PASS=True,
    Human_may_review_true_failure_evidence=True,
    B1_Human_naturalness='INCONCLUSIVE_DURATION_TOO_SHORT',B1_technical_PASS_not_revoked=True,
    retained_engineering_WARN=['finite target-B3 skin probe entry about2.33mm','root acceleration and C1 support-knot acceleration changes','LINEAR120Hz bake is not exact C2'],
    presentation_only_overhead_reframe=.60,candidate_and_motion_unchanged_during_reframe=True,
    full_four_bar_dual_hand_ready=False,dual_hand_stage_started=False,stop='STOP — HUMAN REVIEW')
dump('FINAL_STATUS.json',status)
attempt=read(P/'CANDIDATE_ATTEMPT.json');attempt.update(status='COMPLETED_ONE_TRUE_CANDIDATE_FAIL_CLOSED',post_render_refits=0);dump('CANDIDATE_ATTEMPT.json',attempt)
def write(n,t):(P/n).write_text(t,encoding='utf8')
table='\n'.join(f"|{r['note_id']} {r['note']}|{r['finger']}|{r['skin_gap_min_mm']:.3f} .. {r['skin_gap_max_mm']:.3f}|{r['horizontal_max_mm']:.3f}|" for r in diag['notes'])
span_table='\n'.join(f"|{r['label']}|{r['time']:.3f}|{r['thumb_little_lateral_span_mm']:.1f}|" for r in posture['rows'])
write('HUMAN_VISIBLE_REVIEW.md',f'''# HUMAN_VISIBLE_REVIEW · Stage B R2

**Agent产品预检 FAIL_CLOSED；Human完整原速判断仍HUMAN_PENDING。** 本轮接触和音乐功能技术检查成立，但闲置手型存在正常视角可见缺陷，不按轻微工程WARN掩盖。

## 完整原速材料

一个连续四小节左手候选，全部7个原音符/5起音组，源音乐5.142852s；0.35s准备与收尾呈现5.95s。教学、俯视、侧斜3个完整357帧/60fps视频，全部带原左声部Grand样本声音并完整解码；右手不出现、无假重奏、未降低tempo。

正常教学和侧斜视角完整显示左手。原俯视在某些采样裁掉腕端约1.49%；只将该视角正交画幅0.56m扩大到0.60m，方向和位置不变，所有采样全手可见。教学/侧视没有改；动作和保存blend的SHA256完全不变。这是同一候选的显示修复，不是新动作或让手型看起来合格的求解。原裁切检查与修复记录都保留。

Agent查看了全段阶段表及正常教学/侧斜原帧。1.250s和弦→A3交接保持较紧凑手型；约3.083s、3.567s的C4长音阶段闲置拇指与小指明显伸展/张开，B3单音段也有相同持续开放姿态。该问题不需要放大几个毫米才能观察，且不是只出现于单个交接瞬间。不能凭单指到键就称整手自然。

|阶段|呈现秒|拇指–小指横向标记跨度mm|
|---|---:|---:|
{span_table}

原候选五指G3–D4键中心跨度约{posture['provisional_G3_D4_key_center_span_mm']:.1f}mm，材料没有需要大幅寄存器换位的结构。跨度数值仅支持可见开手观察，不是新的毫米级自然度门槛。正常原帧的闲置外展/伸直是产品阻断；最终Human仍可观看真实视频做自己的判断。

## 触键与音乐功能不能替代手型

|事件|指号|实际skin持键间隙mm|水平出界max mm|
|---|---:|---|---:|
{table}

所有7音主动标记在实际可奏区域内；其他指准备时持键指最大间隙约{diag['held_during_preparation_max_skin_gap_mm']:.2f}mm。初和弦3键压力完全一致；原三键释放与A3起音交接的4机械任务被共同求解。原音乐没有异时持键重叠，不能拿这些机械尾部任务冒充新和弦或音乐重叠测试。

工程记录：root最高速度约{diag['root_max_speed_mm_sec']:.1f}mm/s，加速度约{diag['root_max_accel_mm_sec2']:.0f}mm/s²；关节最高约{diag['joint_max_speed_deg_sec']:.1f}°/s；范围内。有限32点skin最大键体进入约{diag['maximum_sampled_key_penetration_mm']:.2f}mm（目标B3），此类有限几何/加速度记录可WARN；明显闲置手型问题单独阻断，不能混为普通WARN。求解66次评估满足xtol终止，未达到75次上限，不伪称全局/人体最优。

浏览器完整实时播放检查未完成：工具初始化返回 `windows sandbox failed: helper_unknown_error: setup refresh had errors`，未进入页面。故不声称Agent实时观看/听取完整1×，更不声称自然度PASS。原速媒体完整性和正常持键姿态的失败证据是两类检查。

## 共性瓶颈与止损

已实现连续释放→准备目标交接，当前持键目标不被混合，技术衔接成立；但对全部闲置指只有静态L1/L2关节参考和避键代理，尤其闲置拇指/小指没有事件相邻五指布局/home关系约束，单音时可回到较宽开放姿态。该解释SUPPORTED；没有证明冻结Rig必须重建。

后续应在局部事件布局中组织所有非主动指的合理准备关系，并仍保留当前持键约束，不能逐音补DIP或调root掩盖。**本轮不实施第二求解、不改指、不修单指。** Stage A R2批准与Stage B R1技术成果不受撤销。STOP — HUMAN REVIEW。
''')
write('IMPLEMENTATION_REPORT.md',f'''# IMPLEMENTATION_REPORT · MINUET_STAGE_B_R2_LEFT_HAND_CONTINUOUS_ACCOMPANIMENT

**FAIL_CLOSED：完整单候选与技术功能已交付，自然闲置手型尚不足。** 失败来自正常可见开手/伸直，不是因为历史3mm阈值或求解失败。保留原速5.95s真实证据，不生成第二候选。

## 实际新增代码

所有新增均在本目录。`left_chord_base.py`受控复制B1实际L FK、多目标/共享root/运动键面基础，仅重命名基类；源文件未改。`left_continuous_motion.py`增加事件感知的目标分量：当前持键仍单一精确目标；已释放/准备指在旧恢复与下一键之间连续交接，避免恢复优先遮住下一准备和重新起一个中性pad目标。指法、音高或曲名不参与姿态特例。

同一框架扩展为7个原事件、所有5指的连续流；时间局部idle软策略复用既有LEFT_IDLE_INDEX/RING域，主动/准备时连续让位给关节可行性。这个扩展仍不完整：闲置拇指和小指的home/形态组织不足，长音单指时持续外展已暴露。不能将接口通用误称自然演奏泛化通过。

`03_generate.py`在一个问题中优化整段113个支撑、2952未知量；28个机械阶段联合pose仅作同一次求解的初始化，未拼接28份动画。66次评估满足xtol终止。827个输出采样包括120Hz与精确事件点；计划C1、120Hz LINEAR烘焙近似。没有先固定root、没有镜像右手或固定D2/D3。

有限预检一批6个静态任务和正式左皮肤回读，包含持和弦准备无名指、边界4个机械接触任务和食指C4新单音；0静态Action/0保存候选。当前所有姿态在原冻结Rig上实际可达，不据此批准自然度。保存重开候选pad/FK最大差约{man['actual_pad_vs_FK_max_mm']:.5f}mm，实际键几何差约{man['actual_key_world_parity_max_mm']:.6f}mm；四静态core、手结构和88键网格保持。

新音频使用原7个左voice、原velocity/channel、原tempo和既有Grand PCM方法，source MIDI保持原字节。无右手，无曲目简化、虚构重奏或音乐慢放。三个原速视频全部357帧/60fps，完整解码，原声5.142852s外只加准备/回位。

生成后仅补充诊断/文档及俯视画幅修复：原俯视腕端裁切，方向位置不变将画幅放大到0.60m，动作npz和保存blend字节相同；教学/侧视帧原样。没有重新拟合、换指、单指pose补丁、原型“优胜挑选”或第二候选。

## Q1–Q12

|问题|回答|
|---|---|
|Q1 真实数量/结构|7音符、14ON/OFF、5起音组：G3+B3+D4二分和弦→A3四分→B3/C4/B3各附点二分。源范围tick0–4608，最后OFF正好4608，5.142852s；无异时持键重叠/紧邻同键重奏。|
|Q2 候选指法|初和弦沿用5/3/1；A3=4、B3=3、C4=2、B3=3，一次锁定DESIGN_PROVISIONAL，无教师认证。|
|Q3 和弦衔接自然吗|技术保持和弦与A3交接接触、同步和4机械任务，整体自然性未通过产品预检；后续单音长持键闲置手型明显张开，状态PARTIAL。|
|Q4 重叠与独立指|原音乐无不同起音持键重叠，如实记录；支持3音同时持键/下一指准备、旧3释放+新A3触键。B3/C4长音期间下一不同指准备时当前指接触保持。未冒充验证未出现的音乐结构。|
|Q5 连续协调实现吗|共同root/旋转、全部关节、键内XY和相邻状态导数一份全段求解，技术实现；但自然idle关系不足，LEFT_HAND_CONTINUOUS_MOTION=PARTIAL。|
|Q6 单音/和弦/换位自然吗|HUMAN_PENDING且Agent可见预检FAIL；长音单指闲指展开明显。材料无需跨寄存器换位，不能宣称大跳换位验证。|
|Q7 可见异常吗|正常视角可见闲置拇指/小指持续伸展/外展，此为产品阻断。未发现严重主动错键或脱离，轻微target-B3几何进入另为WARN。无“所有异常皆不存在”声明。|
|Q8 原时间保留吗|是，7个原MIDI字段及tempo完整，全部真实NOTE_ON/OFF和末端OFF保留，7声部PCM/琴键共享事件钟，不修改源文件。|
|Q9 通用而非特例？|事件/真实键几何/指号驱动，无B3/C4专属姿态，持键目标与释放准备目标分量可复用；自然闲指布局还不完整，泛化质量未证明，机制PARTIAL。|
|Q10 手修/第二候选？|无。只有一个动态求解/保存候选；无渲染后参数、指法、动作重试。俯视仅显示修复，同一动作、同一候选。|
|Q11 保护基线？|YES，{protected['protected_files']}个文件哈希一致；Stage A R2批准、Stage B R1技术/视频/代码及全部正式冻结资产不变。B1自然度新权威仅存本轮绑定，仍INCONCLUSIVE_DURATION_TOO_SHORT，不误写PASS。|
|Q12 能进双手吗|不能。本轮自然手型目标未达且Human完整1×待审，未启动双手或自动合成。|

## 交付与下一局部架构问题

`HUMAN_REVIEW.html`保留真实原速失败材料与3个正常视角；`VISIBLE_POSTURE_EVIDENCE.json`提供持键阶段开手证据；工程诊断与可见FAIL分开。浏览器自动检查初始化失败，未声称完整实时影音观看；完整媒体/HTTP/Range和帧记录可复核。

后续应为全部闲置指建立相邻事件推导的准备布局/形态关系，而非只向L1/L2静态关节参考恢复。这是通用局部规划缺口，不要求改冻结Rig，也不以逐音修补实现。本轮停止，不执行该修改。严格状态见 `FINAL_STATUS.json`。
''')
checks={}
for n in ['HUMAN_REVIEW.html','normal_speed_teaching.mp4','normal_speed_overhead.mp4','normal_speed_side_oblique.mp4']:
    with urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8873/'+n,method='HEAD')) as r:
        assert r.status==200;checks[n]=dict(status=r.status,bytes=int(r.headers['Content-Length']),content_type=r.headers.get('Content-Type'))
with urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8873/normal_speed_teaching.mp4',headers={'Range':'bytes=0-127'})) as r:assert r.status==206 and len(r.read())==128
dump('REVIEW_DELIVERY_VERIFICATION.json',dict(url='http://127.0.0.1:8873/HUMAN_REVIEW.html',HEAD_checks=checks,range_response=206,
    all_delivered_views_whole_hand=True,Agent_realtime_review='NOT_PERFORMED_HELPER_INITIALIZATION_FAILED',Human_quality='PENDING',
    no_reoptimization=True,Codex_open_result='queued'))
files={str(f.relative_to(P)):dict(sha256=sha(f),bytes=f.stat().st_size) for f in P.rglob('*') if f.is_file() and '_frames' not in f.parts and f.name!='DELIVERY_MANIFEST.json'}
dump('DELIVERY_MANIFEST.json',dict(candidate_count=1,new_blend=man['path'],files=files,views=3,frames_each=357,fps=60,
    source_music_duration_sec=5.142852,video_duration_sec=5.95,overhead_reframing_motion_unchanged=True,status='FAIL_CLOSED',stop='STOP — HUMAN REVIEW'))
print('FINAL_LEFT_CONTINUOUS',json.dumps({k:v for k,v in status.items() if k.isupper()},ensure_ascii=False),flush=True)
