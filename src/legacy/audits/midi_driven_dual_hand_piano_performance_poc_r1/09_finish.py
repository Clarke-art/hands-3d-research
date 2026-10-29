from performance_core import *
import html,re
phase='MIDI_DRIVEN_DUAL_HAND_PIANO_PERFORMANCE_POC_R1'
status='MIDI_DRIVEN_PIANO_PERFORMANCE_POC_PARTIAL'
contact=read(P/'CONTACT_VALIDATION_R1.json');summary=contact['summary'];audio=read(P/'KEY_AUDIO_SYNC_R1.json');media=read(P/'VIDEO_VERIFICATION_R1.json');identity=read(P/'CANDIDATE_IDENTITY_R1.json')
assert media['audio_present'] and media['audio_not_silent'] and audio['audio_status']=='PASS'
assert audio['voices_scheduled']==18 and audio['pitch_within25cents']
lock=read(P/'PRE_GENERATION_LOCK_R1.json')
for n,k in [('GENERATION_POLICY_R1.json','policy_sha256'),('PERFORMANCE_TIMELINE_R1.json','timeline_sha256'),('PROVISIONAL_FINGERING_PLAN_R1.json','fingering_sha256')]:assert sha(P/n)==lock[k],('PLAN_DRIFT',n)
candidate='MIDI_DRIVEN_DUAL_HAND_PIANO_PERFORMANCE_CANDIDATE_R1.blend';assert sha(P/candidate)==identity['candidate_sha256']
before=read(P/'PROTECTED_INPUTS_BEFORE_R1.json');rows=[]
for f,v in before.items():
 now=sha(f);rows.append({'path':f,'before_sha256':v,'after_sha256':now,'unchanged':v==now})
assert all(r['unchanged'] for r in rows)
inherit=['KEYBOARD_AUTHORITY_R1.json','KEYBOARD_COORDINATE_FRAME_R1.json','KEYBOARD_88_KEY_TABLE_R1.json','CONTACT_TOLERANCE_POLICY_R1.json','FINGERTIP_CONTACT_MARKERS_R1.json']
for n in inherit:assert sha(P/n)==sha(PRE/n)
dump('FINAL_ASSET_PROTECTION_R1.json',{'status':'PASS','RIGHT_R2_UNCHANGED':True,'LEFT_R1_UNCHANGED':True,'RIGHT_R1_FALLBACK_UNCHANGED':True,'PIANO_BASELINE_UNCHANGED':True,'protected_file_count':len(rows),'inherited_geometry_metadata_identity':'MATCHED','candidate_static_components':'MATCHED after removing only candidate animation/root and display material in unsaved verification memory','source_PianoVAM_actions_loaded':False,'candidate_sha256':sha(P/candidate),'scope':'Frozen sources plus previous two audit root files; mutable non-authority latest-stage pointer was never written and is excluded.','files':rows})
visual={'review_type':'AGENT_PRECHECK_NOT_HUMAN_APPROVAL','PRODUCT_DEMO_PASS':False,'natural_hand_motion':False,'unified_skin_material':True,'semi_realistic_skin_quality_pass':False,'observations':['RH nonplaying/playing fingers visibly over-curled; local joint branch change is abrupt.','Active fingers can remain above sinking keys; actual touch is not guaranteed just because target clock is correct.','Left palmar region hits frozen key volumes at120 of409 observations; wrists have no screen hits.','Both hands have the same skin shader. Bright pale/faceted appearance still reads as a model, not convincingly natural skin.','Full88 keys and both hands remain visible; no hidden fingers or cosmetic masking of failed contacts.'],'stop_loss':'Only one procedural candidate, one fingering design and one material setup. No root/IK/art retuning after failure.','failure_layers':{'FINGERING_PLAN':'PROVISIONAL; no human validation and no alternative tested','ROOT_PLANNING':'INSUFFICIENT: static shared home root did not accommodate press travel and octave reach','FINGER_KINEMATICS':'FAIL: bounds saturate and RH branch step reaches21.817deg/120Hz','KEY_CONTACT':'FAIL: sustained contact R48/240 L12/240; left palmar penetration screen','AUDIO_SYNC':'KEY/AUDIO_CLOCK_PASS; ACTUAL_HAND_TOUCH_SYNC_FAIL'}}
dump('PRODUCT_REVIEW_R1.json',visual)
questions=[
 ('Q1','官方 MIDI 已取得并与乐谱核对？','YES；PDF 目视 + LilyPond/MIDI 前两小节音高与 tick 逐项一致。'),
 ('Q2','选择小节？','第 1–2 小节，首次出现，完整保留两声部；音乐 2.0 秒，展示含准备与释放共 3.4 秒。'),
 ('Q3','左右手分配明确？','YES；Staff one/track1 → RIGHT，Staff two/track2 → LEFT，经谱面核对。'),
 ('Q4','候选指法及权威程度明确？','YES；DESIGNED_PROVISIONAL，不是官方指法或 ground truth。'),
 ('Q5','双手能按正确目标键演奏？','NO；虽目标音区与横向位置匹配，持续触键失败。'),
 ('Q6','整体手掌与手腕自然？','NO；手指蜷曲、共享掌位缺乏随按键的合理配合。'),
 ('Q7','存在明显穿键、悬浮或指链问题？','YES；持续悬浮、左掌键体命中、右手局部关节变化过快。'),
 ('Q8','琴键下沉与 NOTE_ON 同步？','YES；同 timeline 起动，35ms 达到全行程；最终60fps量化最多8.33ms。'),
 ('Q9','钢琴音高与 MIDI 对应？','YES；原采样 zone/ratio 检查通过，7 个实际音高的强谐波估计均在 ±25 cents 内。'),
 ('Q10','视频有真实可听音轨？','YES；AAC 双声道，解码后非静音，18 个采样 voice，双手复音。'),
 ('Q11','统一自然皮肤材质？','NO（完整质量门槛）；统一肤色 YES，半写实自然观感仍未通过。'),
 ('Q12','更换 MIDI 有清晰复用接口？','YES；歌曲/指法数据 → timeline → 分离的手、键、音频执行器；新曲仍须人工规划与重新验证。'),
 ('Q13','最终状态？',status+'；PRODUCT_DEMO_PASS = NO。')
]
fields={'TEST_PIECE':'Musette, BWV Anh.126','TEST_MEASURES':'1–2','MIDI_SOURCE':'Mutopia Project official MIDI; Public Domain','FINGERING_STATUS':'DESIGNED_PROVISIONAL / HUMAN_REVIEW_PENDING','HAND_MOTION':'NEW_PROCEDURAL_CANDIDATE / NATURALNESS_FAIL','KEY_CONTACT':'FAIL; onset R8/10 L4/8; held R48/240 L12/240','AUDIO_SYNC':'KEY_AUDIO_PASS / HAND_CONTACT_SYNC_FAIL','SKIN_MATERIAL':'UNIFIED_SKIN_APPLIED / REALISM_NOT_PASSED','PRODUCT_DEMO_VIDEO':'product_midi_dual_hand_with_audio.mp4','PRODUCT_DEMO_PASS':'NO','FINAL_STATUS':status,'RIGHT_R2_UNCHANGED':'YES','LEFT_R1_UNCHANGED':'YES','PIANO_BASELINE_UNCHANGED':'YES'}
dump('FINAL_STATUS_R1.json',{'phase':phase,'fields':fields,'Q1_Q13':[{'id':q,'question':t,'answer':a} for q,t,a in questions],'STOP':'HUMAN REVIEW'})
qt='|问题|回答|\n|---|---|\n'+'\n'.join(f'|{q} {t}|{a}|' for q,t,a in questions)
ft='|字段|结果|\n|---|---|\n'+'\n'.join(f'|{k}|{v}|' for k,v in fields.items())
fingering='|小节|手|原 MIDI / 音名|候选手指|MIDI 时值 / velocity|\n|---|---|---|---|---|\n|1、2|RIGHT|81 A5 → 79 G5 → 78 F♯5 → 76 E5 → 74 D5|5 → 4 → 3 → 2 → 1|四分 + 四个十六分；90|\n|1、2|LEFT|38 D2 → 50 D3 → 38 D2 → 50 D3|5 → 1 → 5 → 1|四个八分；90|'
pitchmax=max(abs(p['cents']) for p in audio['pitch_checks'].values())
report=f'''# {phase}

**{status}**。**PRODUCT_DEMO_PASS = NO**。**STOP — HUMAN REVIEW**。

首次打通了官方 MIDI → 明确声部/候选指法 → 新程序化 Action → 琴键 → 真实钢琴采样音轨，但动作与接触质量未通过。PARTIAL 只表示执行链路和带声音交付成立，不表示产品演奏动作合格。没有继续调旧 PianoVAM root，也没有加载其非商业 Action。

## Q1–Q13

{qt}

## 曲目与指法审核

官方页面、MIDI、PDF 与同源 LilyPond 都已保留，来源详见 [SOURCE_AND_LICENSE_R1.md](SOURCE_AND_LICENSE_R1.md)。MIDI format1，PPQ384，tempo500000μs/quarter（120BPM），2/4，D大调；两条音乐轨道分别对应谱面的 treble/bass staff。前两小节的音高、起止 tick 和时值通过精确比较。片段 velocity 全90，无 pedal 事件；同手同时持音最多1，两手合计最多2。此 POC **没有验证同手和弦**，不可借双手复音宣称多指和弦能力成立。

第3小节开始需快速换音区，按用户允许的规模缩小到连续第1–2小节，未改音、未删音、未改速度。18个音、36个NOTE_ON/OFF事件，音乐长2秒。统一增加0.7秒准备和0.7秒释放/展示尾部，成片3.4秒。

官方谱面与 MIDI 无可用 finger 编号。如下指法是有限设计候选，不是权威指法，也没有进行自动搜索：

{fingering}

左手八度采用5/1交替，右手D5–A5五指位置。该设计尚未由钢琴教师确认；本轮没有测试替代指法。逐音审核表在 `PROVISIONAL_FINGERING_PLAN_R1.json`，不将生成结果回写成已批准指法。

## 一个新动作候选

只读取冻结 R2/L1 的 rest rig、weights、corrective 与固定 pad 定义，从零生成新的 `NEW_MIDI_PROCEDURAL_R_R1` / `NEW_MIDI_PROCEDURAL_L_R1`。无 PianoVAM 动画、landmark、已拟合 root 数组输入。使用的既有辅助代码只负责静态身份与键面几何测量。

每手一个共享掌位，以五个 home targets 一次规划 root XYZ/yaw；本候选 root 在片段内保持固定。Root 高度限定55–85mm，yaw ±12°。每指3个非负 palmar flexion + 基部 spread，无轴向 twist；长指上限75/95/65°，拇指40/55/55°，spread长指±28°/拇指±35°。这些是本次工程候选限制，不是人体活动范围认证。一次全局 home 求解后，按120Hz顺序局部IK，保存为同一新候选，没有重启参数搜索。

统一阶段：PREPARATION → 前100ms APPROACH → NOTE_ON时CONTACT目标 → 35ms KEY_PRESS → NOTE_OFF后70ms RELEASE → 回到home hover的 NEXT_NOTE_TRANSITION。音频释放包络240ms。原 timing没有吸附到帧。数学目标曲线连续，但**数值IK分支并未保证关节连续自然**：右手在展示时间2.608秒、食指中间关节出现最大21.817°/8.33ms跳变，就是当前失败，而不是用插值标签掩盖它。

具体失败层级：

- FINGERING_PLAN：尚为设计候选，不能归罪于错误权威指法；未测试替代。
- ROOT_PLANNING：固定共享home掌位对八度与按键行程配合不足，没有自然随动。
- FINGER_KINEMATICS：关节达到边界，部分手指过度蜷曲；右手有局部分支快速变化。
- KEY_CONTACT：多数持音时 pad 仍在键面上方，左掌区域也出现键体命中。
- AUDIO_SYNC：音频与琴键事件时钟通过；由于实际手部未触键，**手指触键与声音的完整产品同步没有通过**。

## 接触与静态资产保护

沿用固定 pad 标记、原垂直3mm / 水平2mm容差和实际可奏键面区域，未为提高成绩改 marker 或 tolerance。

|指标|RIGHT|LEFT|
|---|---:|---:|
|起音接触|8/10|4/8|
|持音接触（120Hz相关观测）|48/240|12/240|
|持音悬浮 >3mm|192|228|
|最大垂直误差|17.480mm|14.908mm|
|目标键横向区域误差最大值|0mm|0mm|
|掌部键体命中观测 /409|0|120|
|腕部键体命中观测 /409|0|0|

机器使用 inherited key-piece vertex-volume screen；不是完整穿插证明，也没有开展 frozen anatomy 重审。0mm横向误差只说明所分配 pad 落在目标键平面区域，不能说明实际按下。其他手指/mesh与相邻键接触不由该数字排除。起音8/10也不能掩盖持音阶段48/240。

保存场景重新打开验证：R/L都是3300 vertices、21 bones；移除实验 root/新Action/展示材质后，rest、topology、static weights、corrective/driver、原shading等静态身份 MATCH。FK pad与保存场景最大差R0.000422mm、L0.000367mm；rigid pad与实际skin顶点最大差R0.213mm、L0.247mm。最低有限性检查通过，不表示动作自然。

{len(rows)}个受保护文件 SHA256 unchanged，包括三份正式手基线、Grand frozen authority、原音源和之前审计根目录产物。右R2 `c946fed318fa88c238d9aacc30cfb4e52f268848f0ad65a4dcbf594754d791f0`；左R1 `54307bb199a75a5e684c29d346de9ca6bf2f8e7696911d9d69c57559516ad1a7`；右R1 fallback `4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2`。所有修改仅在本审计目录和候选实例中。

## 音频与音画同步

使用现有 Grand 的 CC0 VCSL Kawai Grand 真钢琴采样。18个NOTE_ON各有独立voice，NOTE_OFF按原时刻进入240ms指数释放。复用既有采样zone、velocity≥80选V4、pitchRatio、力度公式与master0.72；离线适配器用48kHz PCM统一调度，取代浏览器即时音频时钟，不使用正弦波。

音源以 sampler C3=MIDI60命名，界面以scientific C4=MIDI60显示，按manifest数字映射，避免错八度。源文件hash全部匹配。逐asset移除录音前的leading silence，阈值与trim样本数逐项记录。没有提前音符时间，也没有改音高内容。单弱基频测量在D2不可靠，修正为前6谐波中最强3项的f/n中位数，保留全部频谱证据；7个用到的音最大估计偏差{pitchmax:.2f}cents，均小于25cents。该检查结合已核验root/ratio，不冒充盲转谱或听觉专家验收。

最终 MP4 实含AAC stereo音轨，解码RMS={media['decoded_audio_rms']:.6f}，非静音。PCM与最终AAC交叉相关滞后{media['AAC_PCM_lag_ms']:.3f}ms；事件调度量化0ms，键下沉开始与NOTE_ON共时，35ms后达全行程，60fps展示量化最多8.33ms。复音峰值2个held voice，release tail可叠加；18voice没有丢音、无clipping。手触键失败不能由这些时钟检查抵消。

## 统一皮肤材质

左右实例共用一个 `SEMI_REALISTIC_HUMAN_SKIN` 目标shader：同base color，roughness0.49、subsurface0.055、轻微微表面bump，无金属和夸张褶皱。只增加候选实例材质，未保存回正式资产；不以不同颜色区分左右手，界面用LEFT/RIGHT。

实际预检中材质虽统一，画面仍偏粉白、平面分面与模型感可见，**不能认定满足半写实真人皮肤观感**。只有这一套材质/灯光，没有多轮美术调参。[SKIN_MATERIAL_REVIEW_R1.png](SKIN_MATERIAL_REVIEW_R1.png)保留原样供Human判断。

## 可复用接口与重现

`SONG_DATA_R1.json` 保存曲目、谱面声部、指法/布局输入；`PERFORMANCE_TIMELINE_R1.json` 是唯一事件时钟。`03_motion_plan.py`生成手关节轨迹，`performance_core.py`派生key curve，`05_audio.py`独立生成PCM；`04_scene.py`产生Blender候选，`08_media.py`仅把已同步视频/音轨封装。音频不写进hand Action，Blender动作没有硬编码音频剪辑。

更换MIDI需要新的score-checked hand/finger plan和layout，再交给同一timeline/执行接口；当前导入核对入口专门验证Musette前两小节。**没有验证任意MIDI，也没有完整指法生成器、同手和弦系统或多曲播放器**。首次运行后仅把home layout同值提取为SONG_DATA，未改变候选数组。

重现入口：`powershell -File reproduce.ps1 -Mode Verify`复核现有交付；显式`-Mode Rebuild`用相同输入重建同一候选。依赖：Python3.12、审计内`_deps`的mido/scipy/PyMuPDF、Pillow/numpy、Blender5.1.2、ffmpeg/ffprobe；本次全部具备。脚本保留，正式资产只读。渲染从已有帧续跑仅用于恢复相同候选，不用于美术变体。

允许的实现bug修复记录：候选原无材质槽时增加实例槽；评估函数补齐math/tolerance依赖；rest mesh坐标区域诊断改为实际世界坐标，避免把全部3300点误标为腕部；弱低音基频改用强谐波验证。上述修复均未重求解或改动第一次动作候选。渲染缓存重启没有改变材质、相机、采样质量或帧率。

## 交付与停止

[审阅页](review.html)含播放/暂停/重播、音量与原速/慢速查看；[第一版带声音视频](product_midi_dual_hand_with_audio.mp4)为1600×900、60fps、204帧、3.4秒；[候选Blend]({candidate})可检查全部手、键、Action和相机。谱面、timeline、指法、规划、sync与保护JSON保留。机器没有代替Human批准，声音检测也没有冒充实际聆听评价。

{ft}

**STOP — HUMAN REVIEW。没有进入整首、多曲目播放器、正式Web集成或商业发布。**
'''
(P/f'{phase}_REPORT.md').write_text(report,encoding='utf-8')
qhtml=''.join(f'<tr><th>{q} {html.escape(t)}</th><td>{html.escape(a)}</td></tr>' for q,t,a in questions)
files=[f'{phase}_REPORT.md',candidate,'SONG_DATA_R1.json','PERFORMANCE_TIMELINE_R1.json','PROVISIONAL_FINGERING_PLAN_R1.json','HAND_MOTION_PLAN_R1.json','KEY_AUDIO_SYNC_R1.json','CONTACT_VALIDATION_R1.json','CANDIDATE_IDENTITY_R1.json','SOURCE_AND_LICENSE_R1.md','FINAL_ASSET_PROTECTION_R1.json','VIDEO_VERIFICATION_R1.json','reproduce.ps1']
if (P/'REVIEW_UI_VALIDATION_R1.json').is_file():
 assert read(P/'REVIEW_UI_VALIDATION_R1.json')['status']=='PASS'
 files+=['REVIEW_UI_VALIDATION_R1.json','review_server.cjs']
 report+='\n本地审阅交互复核：隔离 Chrome 验证播放推进、暂停保持、定位和重播推进均 PASS，未静音。内置 CUA 进程不可用，因此使用本地浏览器回退。临时简易 HTTP 服务不支持视频 Range，改用 `node review_server.cjs` 后验证通过（仅127.0.0.1:8788）。可直接打开 review.html 或以此服务审阅；并非正式 Web 集成。\n'
 (P/f'{phase}_REPORT.md').write_text(report,encoding='utf-8')
links=''.join(f'<li><a href="{n}">{n}</a></li>' for n in files)
page=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Musette · 双手 MIDI 演奏 POC R1</title><style>
:root{{color-scheme:dark}}body{{margin:0;background:#111a23;color:#e6edf2;font:16px/1.7 system-ui,"Microsoft YaHei",sans-serif}}main{{max-width:1240px;margin:auto;padding:36px 24px 70px}}h1{{font-size:34px;line-height:1.3;margin:12px 0}}h2{{font-size:22px;margin:32px 0 12px}}.eyebrow{{color:#a9c0cf;letter-spacing:.12em}}.status{{background:#3c2a21;color:#ffd3a8;border-left:4px solid #e7ac6a;padding:16px 20px;margin:24px 0}}.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}}.card{{background:#1d2b38;padding:17px;border-radius:8px}}.card strong{{display:block;color:#d9e8f1}}small{{color:#a9bac8}}video,img{{width:100%;display:block;border-radius:10px}}video{{background:#080d12}}button,select{{font:inherit;color:#e6edf2;background:#273c4d;border:1px solid #536d81;border-radius:7px;padding:8px 16px;cursor:pointer}}button:hover{{background:#35536b}}.controls{{display:flex;gap:10px;flex-wrap:wrap;margin:14px 0}}a{{color:#9dd4fa}}table{{border-collapse:collapse;width:100%}}td,th{{text-align:left;border-bottom:1px solid #344553;padding:12px;vertical-align:top}}th{{width:37%}}li{{overflow-wrap:anywhere}}.footer{{margin-top:30px;color:#bacad6}}@media(max-width:720px){{main{{padding:20px 12px}}.grid{{grid-template-columns:1fr}}h1{{font-size:27px}}}}
</style><main><div class="eyebrow">PIANO PERFORMANCE / ONE EXCERPT / R1</div><h1>Musette · 双手 MIDI 演奏</h1><p>BWV Anh.126，第 1–2 小节。官方 MIDI 原速 120 BPM，2 秒音乐，加准备与释放共 3.4 秒。</p>
<div class="status"><strong>PARTIAL · PRODUCT_DEMO_PASS = NO</strong><br>音符、琴键与钢琴音轨链路已运行；手部动作和持续接触未通过。这里展示的是唯一实验候选，等待 Human Review。</div>
<video id="performance" controls playsinline preload="metadata" poster="review_poster.jpg" src="product_midi_dual_hand_with_audio.mp4"></video>
<div class="controls"><button id="play" type="button">播放并开启声音</button><button id="pause" type="button">暂停</button><button id="replay" type="button">重播</button><label>速度 <select id="speed"><option value="1">原速 1×</option><option value="0.5">慢看 0.5×</option></select></label></div><p id="playback-status" role="status">点击播放后可听声音；音量也可在视频控件中调节。</p>
<div class="grid"><div class="card"><strong>18 个原始音符</strong><small>两条谱面声部；候选指法非官方真值。</small></div><div class="card"><strong>真实 Kawai Grand 采样</strong><small>CC0 音源，AAC 双声道；每个音都有对应 voice。</small></div><div class="card"><strong>持续接触未通过</strong><small>R 48/240，L 12/240；不能把起音接触当作完整按键成功。</small></div></div>
<h2>指法审核表</h2><table><tr><th>声部</th><th>每小节音符</th><th>候选手指</th></tr><tr><td>RIGHT · 第1、2小节</td><td>A5 → G5 → F♯5 → E5 → D5</td><td>5 → 4 → 3 → 2 → 1</td></tr><tr><td>LEFT · 第1、2小节</td><td>D2 → D3 → D2 → D3</td><td>5 → 1 → 5 → 1</td></tr></table><small>设计候选，待钢琴指法审核；没有自动搜索其他方案。1=拇指，5=小指。</small>
<h2>需要 Human 判断的问题</h2><p>部分指链过度蜷曲、右手局部变化过快、指尖未持续跟随下沉的键面；左掌区域仍有键体命中。视频保留了这些失败，没有隐藏琴键或手指。</p>
<h2>统一肤色审核</h2><img src="SKIN_MATERIAL_REVIEW_R1.png" alt="同一肤色材质的左右手候选，供 Human 检查真实感"><p>两手共用同一 skin shader。当前画面偏粉白、模型感仍强；统一颜色已完成，半写实自然度未通过。</p>
<h2>Q1–Q13</h2><table>{qhtml}</table><h2>复核文件</h2><ul>{links}</ul><p><a href="source/anna-magdalena-22-a4.pdf">官方乐谱 PDF</a> · <a href="source/anna-magdalena-22.mid">官方 MIDI</a> · <a href="piano_performance.wav">独立钢琴音轨 WAV</a></p><p class="footer">正式双手、Grand keyboard 与音源文件全部 unchanged。新动作未使用 PianoVAM Action。STOP — HUMAN REVIEW。</p></main>
<script>const v=document.querySelector('#performance'),s=document.querySelector('#playback-status');v.volume=.8;async function play(){{v.muted=false;try{{await v.play();s.textContent='正在播放：钢琴音轨已开启。';}}catch(e){{s.textContent='未能播放：'+e.message+'。可下载 MP4 在本地播放器审阅。';}}}}document.querySelector('#play').onclick=play;document.querySelector('#pause').onclick=()=>{{v.pause();s.textContent='已暂停。';}};document.querySelector('#replay').onclick=()=>{{v.currentTime=0;play();}};document.querySelector('#speed').onchange=e=>{{v.playbackRate=Number(e.target.value);}};v.onended=()=>s.textContent='播放结束，可重播审阅。';v.onerror=()=>s.textContent='媒体加载失败，请通过下方文件或本地播放器打开 MP4。';</script></html>'''
(P/'review.html').write_text(page,encoding='utf-8')
for n in re.findall(r'(?:href|src|poster)="([^"]+)"',page):assert (P/n).is_file(),n
dump('DELIVERY_MANIFEST_R1.json',{'status':'PASS_DELIVERY_NOT_PRODUCT','files':{n:{'sha256':sha(P/n),'bytes':(P/n).stat().st_size} for n in files+['review.html','review_poster.jpg','SKIN_MATERIAL_REVIEW_R1.png','product_midi_dual_hand_with_audio.mp4','piano_performance.wav','FINAL_STATUS_R1.json']},'candidate_count':1,'PRODUCT_DEMO_PASS':False,'STOP':'HUMAN REVIEW'})
print(json.dumps({'status':status,'protected_unchanged':len(rows),'media':media['status'],'PRODUCT_DEMO_PASS':False},ensure_ascii=False))
