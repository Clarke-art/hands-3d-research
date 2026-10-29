from phrase_common import *
from datetime import datetime,timezone,timedelta
import ast,subprocess
D=read(P/'ENGINEERING_DIAGNOSTICS.json');man=read(P/'SCENE_MANIFEST.json');M=read(P/'MOTION_GENERATION.json');fit=read(P/'RIGHT_SEQUENCE_FIT.json');video=read(P/'VIDEO_VERIFICATION.json');audio=read(P/'AUDIO_SYNC.json');before=read(P/'PROTECTED_INPUTS_BEFORE.json')
changed=[f for f,h in before.items() if not Path(f).is_file() or sha(f)!=h];assert not changed,changed
assert len(list(P.glob('*.blend')))==1 and man['candidate_count']==1 and fit['restarts']==0
assert len(video)==3 and all(v['frames']==162 and v['normal_speed'] and v['full_decode']=='PASS' for v in video.values())
assert man['four_static_scenes_unchanged'] and man['hand_structure_unchanged'] and man['all_88_key_geometry_unchanged']
assert all(r['outside_samples']==0 for hand in D['contact'].values() for r in hand)
assert all(v['joint_bound_violation_max_deg']==0 for v in D['continuity'].values())
reason='右手 A5 小指在琴键已下沉并持续发声时仍明显悬空；正常侧斜帧可见，实际皮肤 pad gap 4.572–10.986mm。不是仅凭历史3mm阈值否决。'
status={'phase':'PIANO_HAND_VISUAL_FIRST_SHORT_PHRASE_VALIDATION_R1','client_time':datetime.now(timezone(timedelta(hours=8))).isoformat(),'overall_status':'FAIL_CLOSED','HUMAN_VISIBLE_QUALITY':'HUMAN_PENDING','MUSIC_FUNCTIONAL_CORRECTNESS':'FAIL','ENGINEERING_DIAGNOSTICS':'WARN','GENERALIZATION_EVIDENCE':'NOT_ESTABLISHED','agent_visible_precheck':'FAIL：'+reason,'blocking_reason':reason,'subchecks':{'original_MIDI_key_identity':'PASS','all18_note_events_retained':'PASS','keys_original_timing':'PASS','audio_key_correspondence':'PASS','hand_target_key_horizontal_identity':'PASS','continuous_baked_motion':'PASS','active_hand_key_press_visible_correspondence':'FAIL'},'candidate_count':1,'candidate':'SHORT_PHRASE_DESIGN_ONLY_R1.blend','candidate_sha256':man['sha256'],'motion_optimization_runs':1,'left_previous_coefficients_reused':True,'new_right_fit_runs':1,'post_failure_retuning':False,'manual_per_note_adjustment':False,'frozen_assets_unchanged':True,'protected_file_count':len(before),'four_approved_static_poses_unchanged':True,'human_approval_granted':False,'production_pointer_updated':False,'full_song_started':False,'web_product_integration_started':False,'review_url':'http://127.0.0.1:8865/review.html','stopped':True,'next_action':'STOP_WAIT_FOR_HUMAN_REVIEW','browser_real_time_playback_review':'UNAVAILABLE: browser automation kernel initialization failed; no claim of agent1x playback observation','normal_speed_videos_delivered':list(video)}
dump('SHORT_PHRASE_STATUS.json',status)
D['music_status']='FAIL_VISIBLE_ACTIVE_HAND_KEY_MISMATCH';D['visible_blocking_failure']=reason;D['status']='WARN';D['diagnostic_severity_definition']='WARN: contact-tracking deviations and near-limit residence; no joint domain violation or >3mm key penetration in sampled actual geometry. This does not override the separately FAIL music-function gate.'
dump('ENGINEERING_DIAGNOSTICS.json',D)
dump('FINAL_FROZEN_ASSET_VERIFICATION.json',{'status':'UNCHANGED','count':len(before),'all_before_sha256_rechecked':True,'changed':changed,'four_static_scene_core_unchanged':True,'copied_hand_intrinsic_unchanged':True,'all88_copied_key_meshes_unchanged':True,'source_MIDI_unchanged':True,'right_R2_left_R1_frozen_unchanged':True,'source_hash_file':'PROTECTED_INPUTS_BEFORE.json','verification_scope':'The inherited3098 protected files plus static/source scene/core and new candidate playback identities; no claim of hashing every unrelated file on disk'})
impl='''# SHORT_PHRASE_IMPLEMENTATION_REPORT

2026-10-09 · 唯一 DESIGN_ONLY 候选 · FAIL_CLOSED · STOP

本轮完整读取原 MIDI，保留第1–2小节18音符；生成一个双手连续同场景动作，并输出三个正常速度审核视频。右手A5存在可见悬空按键，音乐功能失败。没有第二次优化，没有修改冻结Rig。

## 复用与有限适配

- 原 `performance_core.py`：MIDI→88键身份、现有FK/关节轴、35ms下沉/70ms回弹、quintic准备/释放。
- 原 `common.py`：批准静态姿态、三次Bernstein压力曲线、完整3300顶点皮肤预测、运动键面测量。
- 左手：此前29参数全手协调结果与原两种压力曲线完全复用，只扩展事件调度到原谱全部8次D2/D3起音；每次同类事件共享同一系数。未重新拟合、未修改源文件。
- 右手：以批准R1准备姿态及R2中指接触参考生成五指共用的接触/全键程系数对；40变量在一个完整序列残差内有界拟合，两个小节重复音共享系数。三次Bernstein控制点由端点等分派生。右手root保持批准共同root。约束沿用原静态工程域与准备姿态±12°。
- 右手残差包含运动键目标、fixed/skin pad、完整皮肤净空、连续性和姿态正则。一次确定性least_squares，13次nfev、533次残差调用，约252.7s；收敛不表示接触成功。
- 烘焙120Hz，正常视频60fps；两个手和琴键在同一scene，同一连续时钟播放。保存重开核实实际骨骼矩阵、pad和键世界变换；未用独立姿态拼接视频。
- 音频直接裁剪已有原钢琴PCM展示时钟0.4–3.1s。复用原VCSL采样、18声部、原速度与时值，不另作配乐或改谱。

新增非冻结文件均在本审计目录：`phrase_common.py`、`00_verify_source.py`、`01_generate.py`、`02_scene.py`、`03_diagnostics.py`、`04_render.py`、`05_media.py`、`06_finish.py`及审核页面/本地服务器。旧代码未修改。

## 失败性质与边界

输入、曲谱事件和既有候选指法已被独立核实，没有证据表明错误来自MIDI或左右手分配。右手有限适配中，固定root与受限接触/压力系数未让A5小指跟随整段白键下沉：起音约4.6mm、full-down约11.0mm pad gap。右小指MCP系数达到本轮准备姿态+12°的生成边界，不能由“fit.success=True”推出可奏接触。

这是本轮右手白键压力轨迹/共同掌根适配不足的证据；不能据此断言冻结Rig必须修改，也不能断言换一种运动规划一定可解。此前左手29参数没有被自动泛化为右手五指联合掌腕规划。本轮未实施架构复评提出的求解器重构。

发现失败后没有调root、IK、DIP或任何局部系数，只完成同一已生成候选的失败证据渲染、报告和保护验证。无逐音符人工动作、逐帧IK、隐含指法替换或失败后特殊硬编码。参数按digit/键身份共享是既有指法输入，不是逐音符手工补丁。

## 音乐与输出核验

原MIDI18音符、36 on/off事件与已有timeline逐项一致。正确目标键index=MIDI−21；所有required-contact样点实际skin pad的水平位置均在目标可奏区。实际键角与时间数组一致；全部原声部保留。按错键/漏键/错手没有证据，但A5的手-键持续按下表现失配导致整体 MUSIC_FUNCTIONAL_CORRECTNESS=FAIL。

三个视频各162帧、60fps、2.7秒并带钢琴声音，均经过ffprobe和完整解码。没有高速播放、静态拼接或删去失败段。

## 冻结保护

最终复查3098个受保护文件哈希全部一致。源RIGHT HAND R2、LEFT HAND R1、Grand键盘、原MIDI、映射和既有音频均不改写；新blend内四个批准静态场景core完全一致，动态复制手部intrinsic和88键mesh一致。新动作与外部root仅写在唯一DESIGN_ONLY派生候选中，未更新任何正式指针。

## 环境限制

受限执行器初始化失败后，通过已获自动审核允许的本地执行完成任务；Blender后台CLI可用。浏览器自动化内核仍无法初始化，因此代理未声称亲自完成1×带声浏览器播放体验审查。代理预检基于正常教学/侧斜/俯视原尺寸帧与完整帧序列、实际动作和声音事件验证；真实速度的完整视频交由Human审核。
'''
(P/'SHORT_PHRASE_IMPLEMENTATION_REPORT.md').write_text(impl,encoding='utf8')
review='''# HUMAN_VISIBLE_PRODUCT_REVIEW

唯一候选整体 **FAIL_CLOSED**。`HUMAN_VISIBLE_QUALITY=HUMAN_PENDING`；代理发现真实可见阻断问题，不授予产品批准。

主内容：[正常速度完整教学视频](normal_speed_teaching.mp4)；辅助：[侧斜视频](normal_speed_side_oblique.mp4)、[俯视视频](normal_speed_overhead.mp4)。三个视频都是同一2.7秒连续候选，60fps、原钢琴声音，保留失败音符。review.html默认1×，可0.5×辅助回放。

## 代理视觉预检证据

右A5小指full-down持键阶段可见手指与下沉白键之间的空隙：例如成片0.333s（源时钟0.733s，frame20）及0.583s（源0.983s，frame35）。第二小节重现相同失配。这些是正常侧斜完整双手视角，没有采用微观顶点/隐藏角度否决。正常教学视角该指看起来在演奏，侧斜视角明确暴露按键与手指未贴合。

连续帧中左右手按候选指法移动，掌腕没有突发位移；没有发现实质按错键、漏键、错手、明显严重穿键或骨骼瞬跳。不能由此宣布整段像真实演奏：持续发声的A5明显悬空已破坏音乐功能。线框/拓扑线沿用既有Workbench审核显示，非本轮新增网格。

浏览器自动化因执行器初始化失败不可用。代理只作正常视角原尺寸帧/完整帧序列与动作连续性预检，未声称完成1×带声浏览器实时观看；Human请完整播放主要视频，给出独立自然度判断。

## Q1–Q10

|问题|结论|
|---|---|
|Q1 真实MIDI片段|Musette原 `anna-magdalena-22.mid`，第1–2小节tick0–1536，源0–2s，18音符。右A5/G5/F#5/E5/D5各重复一遍；左D2/D3各4次。原时间、速度、事件与源Track保留。详见事件报告。|
|Q2 原运动系统与代码变化|复用原FK/skin/quintic/Bernstein、左29参数、88键、音频；本目录新增完整事件调度、一次右五指系数拟合、双手烘焙及审核输出。旧代码和冻结Rig不改。|
|Q3 人工调整/硬编码|无逐音符人工修补、独立手工动作、逐帧IK或失败后二次调参。五指输入按既有设计键/指映射；重复音共享系数。左29参数来自历史拟合，非本轮手调。|
|Q4 正常教学是否基本自然|不能给整体肯定结论。动作顺序与连续性可读，掌腕平顺，但侧斜可见A5小指悬空持键使真实演奏表现不成立。自然度正式结论仍HUMAN_PENDING。|
|Q5 可见错键/悬空/穿键/跳变|阻断问题是右A5明显悬空；未发现实质错键、严重穿键或明显关节瞬跳。不得把未发现当作完整三角碰撞证明。|
|Q6 MIDI/键/音频对应|MIDI身份、琴键时间与原钢琴声部对应PASS，视频带声且完整解码。但手-键持键表现FAIL，因此整体音乐功能FAIL。|
|Q7 仅工程数值问题|左D2 pad gap约3.54mm、D3交接最高约4.16mm，在教学视角并非本轮否决依据；浅表键体穿入左0.229mm/右1.345mm、近限位驻留保留风险记录。右A5 gap4.57–10.99mm有正常侧斜可见失配，不能归入“仅数值”。|
|Q8 扩展潜力/未经验证|完整调度和重复系数复用可以实现，但本轮短句音乐功能失败，更多简单旋律的有效产品泛化NOT_ESTABLISHED。未验证跨手型、转指、跨区/掌根迁移、和弦/同手重叠、长段动作、自动指法或在线演奏。|
|Q9 优先产品缺陷|右白键主动指持键时不能可靠追随下沉键面，尤其A5小指。先解决可见手-键同步能力；本轮不继续优化，也无依据要求改冻结Rig。|
|Q10 冻结资产|全部保持：3098文件最终哈希复查通过，新blend四批准静态core、手intrinsic和88键mesh一致，原MIDI、音频、映射与正式指针未改变。|

## 三层结论

- HUMAN_VISIBLE_QUALITY = HUMAN_PENDING；代理预检发现阻断悬空。
- MUSIC_FUNCTIONAL_CORRECTNESS = FAIL（手-键可见持键失配）；MIDI/键/声子链路PASS。
- ENGINEERING_DIAGNOSTICS = WARN：接触偏差与近限位驻留，无工程关节越界，无采样键体>3mm穿入。WARN不覆盖音乐功能FAIL。
- GENERALIZATION_EVIDENCE = NOT_ESTABLISHED。
- 整体 FAIL_CLOSED；单一DESIGN_ONLY失败候选保留供Human审阅。STOP，等待Human Review。
'''
(P/'HUMAN_VISIBLE_PRODUCT_REVIEW.md').write_text(review,encoding='utf8')
# Clear FAIL_CLOSED heading is visible even before status JSON fetch completes.
html=(P/'review.html').read_text(encoding='utf-8-sig').replace('结果尚未填写；请参阅 SHORT_PHRASE_STATUS.json。','FAIL_CLOSED · 右A5小指可见悬空持键 · 音乐功能FAIL · 工程WARN · Human判断待定').replace('代理视觉预检记录待填写。','代理预检发现右A5小指悬空；MIDI、键、声对应通过，但手-键持键表现失败。本轮已停止，不再生成第二候选。')
(P/'review.html').write_text(html,encoding='utf8')
# Syntax validation only; no additional optimization or candidate generation.
for f in P.glob('*.py'):ast.parse(f.read_text(encoding='utf-8-sig'))
dump('DELIVERY_MANIFEST.json',{'overall_status':'FAIL_CLOSED','candidate_count':1,'files':{f.name:sha(f) for f in P.iterdir() if f.is_file() and f.name!='DELIVERY_MANIFEST.json'},'script_syntax':'PASS','normal_video_primary':'normal_speed_teaching.mp4','frozen_verification':'PASS','human_pending':True,'stop':True})
print('FINAL_FAIL_CLOSED_DELIVERY_FROZEN_UNCHANGED',len(before),flush=True)
