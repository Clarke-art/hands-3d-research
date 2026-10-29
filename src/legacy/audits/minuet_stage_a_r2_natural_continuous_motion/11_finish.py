from stage_common import *
import urllib.request
diag=read(P/'ENGINEERING_DIAGNOSTICS.json');fit=read(P/'COORDINATED_TRAJECTORY_FIT.json');man=read(P/'SCENE_MANIFEST.json')
assert read(P/'FROZEN_ASSET_VERIFICATION.json')['all_protected_hashes_unchanged']
assert read(P/'ACTUAL_CAMERA_VERIFICATION.json')['all_actual_R1_R2_camera_transforms_equal']
major=diag['major_contact_mismatch_notes'];repeat=diag['repeated_key_mechanical_pass']
status=dict(phase='MINUET_STAGE_A_R2_NATURAL_CONTINUOUS_MOTION',client_date='2026-10-10',
    MOTION_TRANSITION_CONTINUITY='UNKNOWN',ROOT_FINGER_COORDINATION='PASS' if not major else 'PARTIAL',
    HAND_POSITION_TRANSITION='PARTIAL',REPEATED_KEY_MECHANISM='PASS' if repeat else 'FAIL',
    MUSIC_FUNCTIONAL_CORRECTNESS='PASS' if not major and repeat else 'FAIL',ENGINEERING_DIAGNOSTICS='WARN' if not major else 'FAIL',
    HUMAN_VISIBLE_QUALITY='HUMAN_PENDING',FROZEN_BASELINES_UNCHANGED='YES',
    FINAL_STATUS='READY_FOR_HUMAN_REVIEW' if not major and repeat else 'FAIL_CLOSED',
    interpretation='Coordination/music PASS are bounded technical checks only. Complete 1x naturalness and hand-position product quality remain unapproved.',
    engineering_joint_continuity_improved=True,original_human_primary_defect='UNNATURAL_MOTION_TRANSITIONS',
    new_dynamic_candidates=1,dynamic_trajectory_solves=1,post_render_refits=0,manual_per_note_fixes=False,
    frozen_rig_changes=False,left_motion_generated=False,next_stage_B_authorized_or_started=False,
    next_stage_ready=False,stop='STOP — HUMAN REVIEW',
    explicit_warnings=['Solver reached max_nfev=75; convergence not claimed',
        'Root acceleration peak about20798 mm/s²; C1 support curve has acceleration changes at knots',
        'Finite representative skin penetration max about2.75mm; not exhaustive collision proof',
        'Browser playback tool failed twice before entering page; complete Agent realtime audiovisual review not performed',
        'Octave return shows an opened hand and a release/recovery posture; Human must judge its naturalness'],
    source_notes=16,source_duration_sec=5.142852,video_duration_sec=5.7,
    browser_control_errors=['trusted Node process exited unexpectedly; kernel reset, rerun your request']*2,
    full_original_speed_media_available=True,HUMAN_approval_granted=False)
dump('FINAL_STATUS.json',status)
def write(n,text):(P/n).write_text(text,encoding='utf8')
old=read(R1/'ENGINEERING_DIAGNOSTICS.json');oldA=np.load(R1/'motion.npz');dt=np.diff(oldA['times'])
oldv=np.diff(oldA['R_delta'],axis=0)/dt[:,None]*1000;oldacc=np.diff(oldv,axis=0)/((dt[:-1]+dt[1:])/2)[:,None]
oldpeak=float(np.max(np.linalg.norm(oldacc,axis=1)))
dump('ROOT_ACCELERATION_COMPARISON.json',dict(R1_finite_sample_max_mm_sec2=oldpeak,R2_analytic_curve_max_mm_sec2=diag['root_max_accel_mm_sec2'],
    acceleration_improvement_claimed=False,methods_differ=True,warning='R2 peak is higher; must inspect wrist rhythm at 1x, not market joint-speed improvement as universal smoothness.'))
write('BEFORE_AFTER_MOTION_REVIEW.md',f'''# BEFORE_AFTER_MOTION_REVIEW · R1 / R2

**新候选已具备原速同期审核材料；整段自然度 UNKNOWN / HUMAN_PENDING。** 技术检查改善与Human产品批准严格分开。没有依据几个关键帧宣称整段自然度通过。

## 同期对照绑定

实际读取R1保存候选的摄像机矩阵、正交比例、裁剪和渲染引擎，再在R2保存重开后逐一比较：教学/俯视矩阵差0，侧斜旋转矩阵元素最大差1.49×10⁻⁷，属于Blender float32矩阵分解/序列化舍入；位置与正交比例相同。不能声称侧视矩阵逐位相同，该量级不构成机位、比例或角度重设计。两个候选同1280×720、60fps、342帧、5.7秒；同源音乐5.142852秒和0.3秒前导。新旧右手PCM逐字节相同。R1原始视频仅复制，未改、未重渲染。审核页两片同秒播放，默认1×并仅一份音频发声；0.5×仅辅助。

|对照项|R1|R2及结论边界|
|---|---|---|
|普通相邻指交接|进入下一准备分支时重新从中性pad目标启动；中指峰值1677.6°/s|联合当前/释放/下一指窗口，计划C1连续，关节峰值{diag['joint_max_speed_deg_sec']:.1f}°/s；工程支持改善，但完整原速自然感尚UNKNOWN。|
|D5小指|R00/R05间隙最大约9.4mm，侧视可见悬空|最大约1.39/1.50mm。相同0.350s侧视原帧可见指端到达下沉键面；未重做资产。|
|G5→G4|root提前200ms单独回迁，G5最大间隙21.5mm、水平出界17.9mm|G5间隙最大约2.03mm，全部持键采样在键区域；4.500s同机位侧视保持接触。开手、腕移和释放后的张开姿态是否自然须看完整1×。|
|G4重复|旧释放和新按压取max，最低键压约0.81/0.87，没有可信再下压|两次读回1→0.42→1，手指随移动键面；事件和原声音重奏时刻相同。0.42是显示机械假设，不是实测擒纵阈值。|
|root与手型|最高root速度482.7mm/s；已被Human判定衔接不自然|最高root速度{diag['root_max_speed_mm_sec']:.1f}mm/s，但最高加速度约{diag['root_max_accel_mm_sec2']:.0f}mm/s²，高于R1约{oldpeak:.0f}的有限差分参考；不能只报告关节速度下降。回落处开手与腕部节奏是Human重点。|

Agent查看了新旧全部16音符的教学/侧视接触表和匹配的正常原帧。这能确认D5/G5可见触键改善，不能确认完整动作衔接改善。浏览器工具两次初始化失败，均未进入页面（`trusted Node process exited unexpectedly; kernel reset`）；未实际实时观看/听取完整1×带声播放。完整媒体已全解码并核验时钟，Human可通过审核页直接播放。

有限工程检查：主动pad所有16音符水平出界0，间隙约−0.85至2.03mm；真实skin pad约−0.83至2.05mm；32个代表性skin点最大键体穿入约2.75mm。后者保留WARN，不做逐点修补，不宣称完整零碰撞。

计划曲线C1，烘焙使用120Hz加精确事件时刻的LINEAR采样，非数学上严格C1；加速度结点变化保留诊断。求解达到75次上限，`success=False`，不能伪称已收敛。尚需Human判断普通衔接、回落张开是否像真实弹奏及是否明显优于R1。

本轮最终 {status['FINAL_STATUS']}；不自动进入左手Stage B。
''')
write('IMPLEMENTATION_REPORT.md',f'''# IMPLEMENTATION_REPORT · R2

**{status['FINAL_STATUS']} · HUMAN_PENDING · STOP — HUMAN REVIEW。** 本轮新增一份动态候选，技术触键/重奏改善，但不声称Human已批准整段自然度。

## 实際改动

全部新增在本独立审计目录。`coordinated_motion.py` 定义共享root平移/旋转、五指关节、键内接触点及相邻事件状态；`02_generate.py` 将这些状态作为同一带状最小二乘的未知量，明确加入按真实dt计算的速度/加速度约束。195个支撑时刻、5102个未知量；一份轨迹求解内部75次评估，达到上限，未再优化。16个相邻事件静态pose仅为该次求解初始化，不是16份动态候选，也不是人工逐音拟合；生成前另有3个有限静态测试。

共享root不固定为R1的分段路径，所有五指参与连续窗口。向量化FK经3组确定性静态输入与原FK逐点对比，误差小于1e−12m。目标XY从键真实面派生，并作为受键内边界约束的通用接触变量；没有D5/G5/G4姿态分支、逐音世界坐标表或改指法。

同键机制按任意键身份及NOTE_ON/OFF关系识别重复，使用最近事件拥有机械曲线，部分复位后再下压。正式Piano runtime未改；新候选的通用运动适配器使用原键几何/枢轴/35ms按压/70ms普通回弹，并增加重复时45ms部分复位。NOTE_ON/OFF、原音高、velocity、channel、指法和PCM均保持原值。

`03_scene.py` 在批准R1静态场景副本上烘焙root旋转与关节，不改变Rig/mesh/weights/rest/driver/corrective。保存重开后实际pad与FK最大差约{man['actual_pad_vs_FK_max_mm']:.5f}mm，实际运动键几何差约{man['actual_key_world_parity_max_mm']:.6f}mm；四个静态core、复制手结构、全部88键网格保持一致。`05_render.py`和`07_media.py`局部复用R1渲染/编码链；完整三视角均全解码通过。

原R1代码、资产、视频与报告全部保留。唯一生成前修正是移除距精确事件支撑不足4ms的冗余非事件点，记录在 `PREGENERATION_SUPPORT_CONDITIONING.json`；音乐时刻未改，修正时动态候选为0。生成后没有调整规划模块、参数或指法；没有第二求解、逐帧补丁或第二动画。

## 最终Q1–Q12

|问题|回答|
|---|---|
|Q1 核心原因|先固定root再逐指追键；独立phase切换重新取中性目标、缺少导数约束；提前回迁未受持键约束；旧max压掉同键重奏。CONFIRMED/SUPPORTED/UNKNOWN见因果报告。|
|Q2 是否真正联合规划|是。root三维/必要旋转、五指关节、键内接触XY与相邻状态导数共同求解，不是只换平滑函数。|
|Q3 跨音高/曲目复用|机制按输入事件、指号和实际键几何驱动，无曲名或音高pose特例。结构可复用；未另生成曲目，跨曲目动态自然度未获验证。|
|Q4 16音符是否完整|是，16NOTE_ON/16NOTE_OFF，原源时长5.142852s、候选指法完整不变，左手0。|
|Q5 普通衔接是否改善|工程连续性支持改善（峰值关节速度1677.6→{diag['joint_max_speed_deg_sec']:.1f}°/s），但完整1×自然度 UNKNOWN，等待Human；不能抽帧当作自然度通过。|
|Q6 G5→G4是否改善|持键功能已改善：最大间隙约2.03mm、水平出界0，正常同机位原帧保持接触；换位自然性仍HUMAN_PENDING，状态PARTIAL。|
|Q7 D5和G4问题|D5明显悬空在匹配原帧中减轻、间隙最大约1.5mm；G4两次部分释放/再下压读回通过。动作是否可信自然仍需Human原速确认。|
|Q8 新异常|无工程角度越界、无严重主动触键失配；root加速度偏高、C1结点加速度变化、有限skin穿入约2.75mm以及回落处张开/回位姿态保留WARN/审核重点，不称“无一切异常”。|
|Q9 音乐与音频|正确：逐音原MIDI字段完全一致，右手PCM与R1字节相同，视频/音频同5.7s且全解码。重复音的新机械轨迹未改音乐或声音重奏时刻。|
|Q10 人工修补/硬编码|没有。没有D5/G5/G4专属pose，生成后无调参、改指或逐帧手修；有通用颜色几何和事件关系规则及锁定工程常量。|
|Q11 冻结资产|YES，最终5290个保护文件SHA256一致；右R2、左R1、四批准姿态、Grand88键、原MIDI/链路及历史接受均保持。|
|Q12 能进入Stage B吗|不能。Human完整1×自然度审核尚未批准；没有启动左手多指、完整双手或Web集成。|

## 状态解释

`MOTION_TRANSITION_CONTINUITY=UNKNOWN`指Human-visible整体原速改善尚未确认；工程轨迹连续性确有改善支持。`ROOT_FINGER_COORDINATION=PASS`与`MUSIC_FUNCTIONAL_CORRECTNESS=PASS`仅指有限技术功能检查，不能兑换成自然度批准。`HAND_POSITION_TRANSITION=PARTIAL`保留回落开手与腕部节奏审查；`REPEATED_KEY_MECHANISM=PASS`仅验证通用部分复位/再下压与手指跟随，不宣称钢琴擒纵物理仿真。

工程WARN包含求解上限、root高加速度、有限代表性碰撞代理及烘焙插值边界。所有严格状态见 `FINAL_STATUS.json`。本轮不因这些小几何误差无限调参，也不掩盖它们。

交付入口 `HUMAN_REVIEW.html`；唯一候选 `STAGE_A_R2_COORDINATED_RIGHT_DESIGN_ONLY.blend`；原速3视角及同机位R1对照、必要0.5×辅助均已提供。浏览器检查工具未能初始化，所以Agent完整实时音视频审核NOT_PERFORMED；这不是Human批准。媒体完整性与有限可见触键检查另有可复核证据。
''')
# Read-only HTTP and range delivery verification, not a visual playback claim.
checks={}
for rel in ['HUMAN_REVIEW.html','normal_speed_teaching.mp4','normal_speed_side_oblique.mp4','normal_speed_overhead.mp4','before/normal_speed_teaching.mp4']:
    with urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8871/'+rel,method='HEAD')) as r:
        assert r.status==200;checks[rel]=dict(status=r.status,content_type=r.headers.get('Content-Type'),bytes=int(r.headers['Content-Length']))
req=urllib.request.Request('http://127.0.0.1:8871/normal_speed_teaching.mp4',headers={'Range':'bytes=0-127'})
with urllib.request.urlopen(req) as r:assert r.status==206 and len(r.read())==128
dump('REVIEW_DELIVERY_VERIFICATION.json',dict(url='http://127.0.0.1:8871/HUMAN_REVIEW.html',HEAD_checks=checks,range_response=206,
    Agent_full_1x_audiovisual_review='NOT_PERFORMED_TOOL_INITIALIZATION_FAILURE',Human_approval='PENDING',open_in_Codex_result='queued'))
files={str(f.relative_to(P)):dict(sha256=sha(f),bytes=f.stat().st_size) for f in P.rglob('*') if f.is_file() and '_frames' not in f.parts and f.name!='DELIVERY_MANIFEST.json'}
dump('DELIVERY_MANIFEST.json',dict(candidate_count=1,new_blend=man['path'],files=files,
    original_R1_media_copied_not_generated=True,frames_each=342,views=3,status=status['FINAL_STATUS'],stop='STOP — HUMAN REVIEW'))
print('FINAL',json.dumps({k:v for k,v in status.items() if k.isupper()},ensure_ascii=False),flush=True)
