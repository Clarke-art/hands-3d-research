from performance_core import *
import html
OLD=P.parent/'midi_driven_dual_hand_piano_performance_poc_r1'
contact=read(P/'KEY_CONTACT_R1.json');S=contact['summary'];motion=read(P/'MOTION_CONTINUITY_R1.json');visual=read(P/'VISUAL_REVIEW_R1.json');media=read(P/'VIDEO_VERIFICATION_R1.json');identity=read(P/'CANDIDATE_IDENTITY_R1.json')
assert visual['complete_3_4sec_reviewed'];assert media['status']=='PASS_MEDIA_STRUCTURE_AND_AUDIO_IDENTITY'
status=visual['FINAL_STATUS'];assert status in ['MOTION_REFINEMENT_PARTIAL','MOTION_REFINEMENT_FAIL_CLOSED','MOTION_REFINEMENT_READY_FOR_HUMAN_REVIEW']
protected=read(P/'PROTECTED_INPUTS_BEFORE_R1.json');rows=[]
for f,h in protected.items():
 actual=sha(f);rows.append({'path':f,'before_sha256':h,'after_sha256':actual,'unchanged':h==actual})
assert all(r['unchanged'] for r in rows)
for n,h in read(P/'INHERITED_INPUTS_R1.json').items():assert sha(P/n)==h
dump('FINAL_ASSET_PROTECTION_R1.json',{'status':'PASS','RIGHT_R2_UNCHANGED':True,'LEFT_R1_UNCHANGED':True,'RIGHT_R1_FALLBACK_UNCHANGED':True,'PIANO_BASELINE_UNCHANGED':True,'protected_file_count':len(rows),'candidate_count':1,'candidate_static_components':'MATCHED','candidate_sha256':identity['candidate_sha256'],'inherited_inputs':'BYTE_IDENTICAL','formal_assets_written':False,'files':rows})
Q=[
('Q1','左手2/3/4指异常蜷曲的原因','闲置指也被独立 IK 强制拉到虚构 home 键位；自然/连续性权重极弱，固定掌位与伸距冲突。PIP约72/60/53°，中指DIP到65°边界，缺乏整手协调。'),
('Q2','整手协调姿态规划','YES；共享掌坐标系、四类状态、闲置指被动随动与掌腕共同求解。'),
('Q3','左手中间三指明显改善','YES；钩爪形态明显减轻。仅为本轮比较观察，不是教师批准。'),
('Q4','避免强行伸直或锁死','YES；RSS F自然曲度保留，叠加小幅曲度；三指基关节全程各有约4–5°变化。'.replace('RSS F','RSSF')),
('Q5','左手八度姿态自然','NO；可到达多数接触目标，但拇指/掌侧接触风险和持音遗漏仍在，整手自然度未通过。'),
('Q6','右手原IK跳变消除','YES；原21.817°/8.33ms跳变消除，最大步进3°，原2.608s时刻也为3°；不等于所有动作已自然。'),
('Q7','掌腕合理随动','NO（完整质量门槛）；已实现有界连续随动，但仍存在掌部命中和接触不稳定。'),
('Q8','持音接触',f"RIGHT 48/240 → {S['R']['held_contact_pass']}/240；LEFT 12/240 → {S['L']['held_contact_pass']}/240。两手均未全程通过。"),
('Q9','仍有悬浮/穿键/错键/掌腕问题','YES；持音悬空和掌部键体筛查命中仍在。演奏指未发现目标键区域错误或超过阈值的pad穿键；闲置pad另有邻键接近风险。'),
('Q10','MIDI/琴键/音频同步保持','YES；时间轴、指法、键盘/marker/tolerance、WAV均字节一致，键角数组完全一致；最终AAC payload直接复制并比对一致。'),
('Q11','左右肤色继续统一','YES；共用原皮肤材质和原灯光。半写实皮肤质感仍未通过，作为独立问题保留。'),
('Q12','最终状态',status)]
fields={'LEFT_IDLE_FINGERS':'IMPROVED / HUMAN_REVIEW_PENDING','HAND_WRIST_MOTION':'IMPLEMENTED / NATURALNESS_NOT_PASSED','RIGHT_IK_CONTINUITY':'ORIGINAL_JUMP_REMOVED / TEMPORAL_BOUNDS_PASS','RIGHT_HELD_CONTACT':f"{S['R']['held_contact_pass']}/240 / FAIL",'LEFT_HELD_CONTACT':f"{S['L']['held_contact_pass']}/240 / FAIL",'KEY_AUDIO_SYNC':'PASS / UNCHANGED','FINAL_STATUS':status,'RIGHT_R2_UNCHANGED':'YES','LEFT_R1_UNCHANGED':'YES','PIANO_BASELINE_UNCHANGED':'YES'}
dump('FINAL_STATUS_R1.json',{'Q1_Q12':[{'id':i,'question':q,'answer':a} for i,q,a in Q],'fields':fields,'STOP':'HUMAN REVIEW','HUMAN_PASS':False})
qt='|问题|回答|\n|---|---|\n'+'\n'.join(f'|{i} {q}|{a}|' for i,q,a in Q)
ft='|字段|结果|\n|---|---|\n'+'\n'.join(f'|{k}|{v}|' for k,v in fields.items())
def fmt(v):return f'{v:.3f}' if isinstance(v,float) else str(v)
ct='|指标|RIGHT|LEFT|\n|---|---:|---:|\n'+'\n'.join(f"|{label}|{fmt(S['R'][key])}|{fmt(S['L'][key])}|" for label,key in [('起音通过','onset_contact_pass'),('持音通过 /240','held_contact_pass'),('持音悬空','held_floating'),('持音pad穿键超过阈值','held_penetrating'),('最大持音垂直误差mm','max_abs_held_vertical_mm'),('目标键平面区域误差mm','max_held_horizontal_mm'),('释放pad穿键超过阈值','release_penetrating'),('闲置pad邻键接近观测','unexpected_key_pad_contacts'),('掌部键体命中 /409','palm_collision_observations'),('腕部键体命中 /409','wrist_collision_observations')])
report=f'''# MIDI_DRIVEN_HAND_POSTURE_AND_CONTACT_REFINEMENT_R1

**{status}**。**STOP — HUMAN REVIEW**。只保留一个 DESIGN_ONLY 候选。左手闲置三指与原右手跳变有改善；接触和整手自然度未达到提交资格门槛，不冒充 Human PASS。

## Q1–Q12

{qt}

## 最小根因检查

- **A 闲置指钩爪**：上一版 `03_motion_plan.py` 对五指每帧都执行 local IK，即使没有该指的演奏音符，也追逐虚构的 home key +12mm目标。左手闲置三指 PIP 为72.33/59.83/53.21°，DIP为45.80/65.00/37.52°；中指 DIP和spread抵边界。位置误差按毫米放大1000，自然/连续项只乘0.07/0.04（弧度），实质被位置压倒。这些值是相对于既有rest的旋转增量。
- **B 起音部分成功、持音悬空**：目标随正式琴键下沉，根部保持固定。达到边界的指链不能继续追踪键面，初始悬停拟合好不代表按下后可达。旧持音R48/240、L12/240就是直接证据。新方案保持键曲线，允许掌腕分担位移，但仍未完全解决。
- **C 右手2.608s跳变**：发生在食指 E5 NOTE_OFF=2.575s后的释放段。每帧局部求解虽warm-start，却没有速度/加速度边界，连续性权重极弱；上一帧合法姿态无法约束下一解，出现21.817°变化。代码与轨迹支持这一机制；没有额外声称已数学证明全部IK解分支。
- **D 固定掌位与八度**：旧左根Z被压到55mm下界，拇指三屈曲近0，小指spread到28°边界，还要照顾三个不演奏的home targets。固定根和错误闲置约束共同挤压了合理姿态空间。本轮不以这个失败证明5/1指法绝对不可行，也不改变指法。

## 唯一协调候选

参考正式左L1的 `SAVED_POSE = ZERO / RSSF`（来自正式R2镜像），直接使用冻结rest几何、21骨架和pad定义。RSSF本身已有几何曲度，零pose参数不等于把手指拉直。本轮闲置长指参考是在其上增加约5/8/5°的小幅屈曲，并由拇指/小指负载生成相关随动；这是当前rig的工程候选，不是凭空制定的人体标准。最终三指MCP增量约2.5–7.7°、PIP约5.9–9.9°、DIP约4.0–6.1°，全程有变化。

每个120Hz时刻明确标记 ACTIVE_PRESS / PREPARING / RELEASING / RELAXED_IDLE。准备160ms，释放140ms；**这些是手部动作窗口，NOTE_ON/OFF没有移动**。不演奏手指没有键位接触目标，追踪RSSF派生的协调参考和共享掌位，允许适度清空键面。当前音和即将换入的音、释放指共同参与同一掌坐标系求解。

掌根XYZ/yaw/pitch/roll与指关节联合求解，始终一个整体root，比例恒为1。全局范围和逐步速度/加速度边界在 `GENERATION_POLICY_R1.json`。上一合法状态与速度预测进入下一步目标和可行范围；非负palmar flexion、关节限位、姿态参考、闲置pad与少量掌部代理点的clearance一起约束。不做事后轨迹平滑，不把指尖直接写入键面。

连续性实测最大关节步进R/L均3°/8.33ms，最大角速度360°/s，加速度14400°/s²（数值误差约百万分之一）；root逐轴速度≤0.32m/s、加速度≤14m/s²。R原跳变时刻为3°。这些工程边界阻止旧式跳变，但不能独自认证自然度。实际掌根全程范围见 `MOTION_CONTINUITY_R1.json`，不是每个NOTE_ON瞬移。

## 接触与全片观察

正式垂直3mm、水平2mm阈值和10个pad均保持原样，并仍要求点位处于目标实际可奏polygon。起音18次、持音每手240次、全场409次观测；另检查每音释放后140ms。起音全部通过不能代替持音。

{ct}

释放末端间隙均为正，pad未出现超过继承阈值的穿键。但触键仍未全程可靠，不能以零横向误差宣称没有悬空。闲置pad邻键接近统计全部出现在 RELAXED_IDLE，属于未演奏键的接近/轻触风险，**不是观测到的错误发音，也不能当作演奏指弹错目标键**。琴键与音频仍由未改动的MIDI驱动。

掌部screen沿用旧版rest区域和key-piece体积筛查，不是隐藏解剖学审计或完整三角碰撞证明。左掌命中旧120→新{S['L']['palm_collision_observations']}，右掌旧0→新{S['R']['palm_collision_observations']}，因此不能说掌腕安全已通过；右掌新增的小范围筛查命中明确保留。侧面额外查看了1.1417s和2.5667s，未因主视角遮挡就抹掉这些风险。

全3.4秒按原速/慢速检查，并逐帧检查204幅渲染图；强制证据时间0.85、1.15、1.85、2.50s未换成最佳帧。`EVIDENCE_LEFT_IDLE_FINGERS_R1.png`采用同相机同裁切比例，上旧下新。具体视觉结论见 `VISUAL_REVIEW_R1.json`：{html.escape('；'.join(visual['observations']))}。

## 不变系统与资产

Musette BWV Anh.126前1–2小节，音乐2.0秒、展示3.4秒；RIGHT A5/G5/F#5/E5/D5=5/4/3/2/1，LEFT D2/D3=5/1交替。仍为 DESIGN_PROVISIONAL，未经钢琴教师批准。没有改MIDI源、NOTE_ON/OFF、velocity、声部、节拍、速度、指法或音高。

继承11个输入文件逐字节一致，包含timeline、指法、键盘权威/几何/坐标、marker、容差、rig probe、音频sync与WAV。88键曲线数组逐元素一致。两份新视频直接复制上一版AAC音轨，ADTS payload字节比较一致，未重新合成音频。原采样zone、音高、音量事件和时钟不变；完整手触键同步仍受接触失败限制。

R2/L1仍各3300顶点、21骨。新候选保存后重开，FK pad最大偏差小于0.002mm，实际skin marker漂移小于0.13mm；移除候选root/Action/展示材质的未保存验证状态后，mesh/rest/weights/corrective/driver静态身份MATCHED。原资产、前轮产物与Grand authority共{len(rows)}个受保护文件SHA不变。

RIGHT R2 SHA256 `c946fed318fa88c238d9aacc30cfb4e52f268848f0ad65a4dcbf594754d791f0`；LEFT R1 `54307bb199a75a5e684c29d346de9ca6bf2f8e7696911d9d69c57559516ad1a7`；RIGHT R1 fallback `4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2`。

两手继续共用原POC皮肤shader，灯光、相机、材质参数和24 samples保持；渲染使用RTX3060 OptiX。颜色统一不表示半写实观感通过，粉白/分面模型感仍在，本轮未改正式skin。

## 实现修复与重现

设计参数在首次求解前锁定，只有一个候选设计，没有参数sweep、替代指法或动作版本抽选。允许的实现bug修复：连续停止距离未包含离散末步，改用精确停止位移和；零宽度可行区间曾误用当前姿态，改为保留唯一合法的下一姿态，并加入逐步速度/加速度断言。中间数值轨迹和旧缓存已覆盖，仅保留最终DESIGN_ONLY候选。未用平滑隐藏问题。

入口 `powershell -File reproduce.ps1 -Mode Verify`；`-Mode Rebuild`按相同输入重建这一候选，`-Mode Render`从现有候选续渲染。Python/numpy/scipy依赖复用上一轮 `_deps`，Blender5.1.2、Pillow、ffmpeg/ffprobe。只写本审计目录。`01_coordinate.py`是动作规划；`03_scene.py`保存/重开验证；`04_evaluate.py`接触与连续性；`05_render.py`渲染；`06_media.py`视频与原AAC复制；`08_verify.py`身份与边界校验。重建前如修改动作或场景脚本，须清除本轮帧缓存，避免拿旧帧冒充新结果。

## 交付与停止

[审阅页](review.html) · [完整有声演奏](product_midi_dual_hand_motion_refined.mp4) · [同步前后对照](product_motion_before_after.mp4) · [四时刻左手证据](EVIDENCE_LEFT_IDLE_FINGERS_R1.png) · [唯一DESIGN_ONLY候选](HAND_POSTURE_CONTACT_REFINED_DESIGN_ONLY_R1.blend)。两份视频各204帧、60fps、3.4秒，含原AAC音轨。对照图像上下共用一个视频时钟，不使用两个容易漂移的播放器。

{ft}

**STOP — HUMAN REVIEW。未进入整首曲目、多曲目播放器、正式Web集成或商业发布。**
'''
(P/'MIDI_DRIVEN_HAND_POSTURE_AND_CONTACT_REFINEMENT_R1_REPORT.md').write_text(report,encoding='utf-8')
qhtml=''.join(f'<tr><th>{i} {html.escape(q)}</th><td>{html.escape(a)}</td></tr>' for i,q,a in Q)
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>钢琴教学手 · 动作修正 R1</title>
<style>:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#10191f;color:#e5edf2;font:16px/1.65 system-ui,"Microsoft YaHei",sans-serif}main{max-width:1360px;margin:auto;padding:30px 24px 70px}h1{font-size:29px;margin:6px 0}h2{font-size:22px;margin-top:30px}p{color:#b7c7d1}.eyebrow{font-size:13px;letter-spacing:.15em;color:#9dafba}.status{overflow-wrap:anywhere;max-width:100%;display:inline-block;background:#3f3222;color:#ffcf91;padding:8px 14px;border-radius:6px;margin:14px 0}.metrics{display:flex;gap:12px;flex-wrap:wrap}.metrics div{flex:1;min-width:200px;background:#1c2932;padding:16px;border:1px solid #34434d;border-radius:7px}.metrics strong{display:block;color:#fff;font-size:25px}video{width:100%;max-height:75vh;background:#0c1318;border:1px solid #34434d;border-radius:6px}button,select{padding:9px 14px;font:inherit;background:#263c48;color:white;border:1px solid #4d6776;border-radius:5px;cursor:pointer}button:focus-visible,a:focus-visible,select:focus-visible{outline:3px solid #e4b37b}nav,.controls{display:flex;flex-wrap:wrap;gap:10px;margin:12px 0}a{color:#a7d9fa}img{max-width:100%;border:1px solid #34434d}table{border-collapse:collapse;width:100%;font-size:15px}th,td{padding:12px;border-bottom:1px solid #34434d;text-align:left;vertical-align:top}th{width:31%}td{overflow-wrap:anywhere}small{color:#a6b8c5}.pane[hidden]{display:none}.warning{border-left:3px solid #e5ae70;padding:10px 18px;background:#211f1c}.seek{font-size:14px}footer{margin-top:30px;color:#ffcf91}</style>
<main><div class="eyebrow">DESIGN ONLY · MUSETTE BWV ANH.126 · MEASURES 1–2</div><h1>钢琴教学 3D 手 · 动作与接触修正</h1><div class="status">__STATUS__</div><p>左手闲置三指姿态与右手原跳变已有改善。持音接触、八度自然度和掌腕安全仍未通过。指法仍为设计候选，皮肤质感另待后续审核。</p>
<div class="metrics"><div>右手持音接触<strong>48 → __R__ / 240</strong><small>原垂直3mm、水平2mm容差</small></div><div>左手持音接触<strong>12 → __L__ / 240</strong><small>起音18/18通过不替代持音</small></div><div>右手最大关节步进<strong>21.817° → 3°</strong><small>每8.33ms；原事件/键角/音轨未改</small></div></div>
<nav aria-label="视频选择"><button id="show-new" aria-pressed="true">本版完整演奏</button><button id="show-compare" aria-pressed="false">同步前后对照</button></nav>
<section class="pane" id="new-pane"><video id="new-video" controls preload="metadata" playsinline poster="review_poster.jpg" src="product_midi_dual_hand_motion_refined.mp4"></video></section><section class="pane" id="compare-pane" hidden><video id="compare-video" controls preload="metadata" playsinline src="product_motion_before_after.mp4"></video><small>上：上一版；下：本版。相同相机裁切、同一时间轴、单份原音轨。</small></section>
<div class="controls"><button id="play">播放</button><button id="pause">暂停</button><button id="replay">从头重播</button><label>速度 <select id="speed"><option value="1">原速 1×</option><option value="0.5">慢速 0.5×</option></select></label><button id="previous">上一帧</button><button id="next">下一帧</button><span id="clock" aria-live="off">0.000 / 3.400s</span></div>
<div class="controls seek"><span>指定时刻：</span><button data-time="0.85">0.85s</button><button data-time="1.15">1.15s</button><button data-time="1.85">1.85s</button><button data-time="2.50">2.50s</button><button data-time="2.608333">原跳变处 2.608s</button></div>
<p class="warning">仍有持音悬空与掌部筛查命中。闲置指接近邻键不等于弹错音；实际音符与琴键事件完全继承上一版。此页不代表 Human PASS。</p>
<h2>左手三指：固定四个时刻</h2><img src="EVIDENCE_LEFT_IDLE_FINGERS_R1.png" alt="左手在0.85、1.15、1.85、2.50秒的相同比例前后对照；上旧下新"><h2>Q1–Q12</h2><table>__Q__</table>
<nav><a href="MIDI_DRIVEN_HAND_POSTURE_AND_CONTACT_REFINEMENT_R1_REPORT.md">完整报告</a><a href="KEY_CONTACT_R1.json">接触测量</a><a href="MOTION_CONTINUITY_R1.json">动作连续性</a><a href="HAND_POSTURE_COORDINATION_R1.json">协调规划</a><a href="FINAL_ASSET_PROTECTION_R1.json">资产保护</a><a href="HAND_POSTURE_CONTACT_REFINED_DESIGN_ONLY_R1.blend">唯一候选 .blend</a></nav><footer>STOP — HUMAN REVIEW · 等待 Human 决策</footer></main>
<script>const vids=[document.querySelector('#new-video'),document.querySelector('#compare-video')];let active=vids[0];vids.forEach(v=>{v.volume=.8;v.muted=false;v.addEventListener('timeupdate',()=>{if(v===active)document.querySelector('#clock').textContent=v.currentTime.toFixed(3)+' / 3.400s'})});function show(i){const t=active.currentTime;active.pause();active=vids[i];active.currentTime=Math.min(t,3.4);active.playbackRate=+document.querySelector('#speed').value;document.querySelector('#new-pane').hidden=i!==0;document.querySelector('#compare-pane').hidden=i!==1;document.querySelector('#show-new').setAttribute('aria-pressed',i===0);document.querySelector('#show-compare').setAttribute('aria-pressed',i===1)}document.querySelector('#show-new').onclick=()=>show(0);document.querySelector('#show-compare').onclick=()=>show(1);document.querySelector('#play').onclick=()=>active.play();document.querySelector('#pause').onclick=()=>active.pause();document.querySelector('#replay').onclick=()=>{active.currentTime=0;active.play()};document.querySelector('#speed').onchange=e=>{active.playbackRate=+e.target.value};document.querySelectorAll('[data-time]').forEach(b=>b.onclick=()=>{active.pause();active.currentTime=+b.dataset.time});function step(d){active.pause();active.currentTime=Math.max(0,Math.min(203/60,active.currentTime+d/60))}document.querySelector('#previous').onclick=()=>step(-1);document.querySelector('#next').onclick=()=>step(1);</script></html>'''
page=page.replace('__STATUS__',status).replace('__R__',str(S['R']['held_contact_pass'])).replace('__L__',str(S['L']['held_contact_pass'])).replace('__Q__',qhtml)
(P/'review.html').write_text(page,encoding='utf-8')
deliverables=['MIDI_DRIVEN_HAND_POSTURE_AND_CONTACT_REFINEMENT_R1_REPORT.md','review.html','product_midi_dual_hand_motion_refined.mp4','product_motion_before_after.mp4','EVIDENCE_LEFT_IDLE_FINGERS_R1.png','MOTION_CONTINUITY_R1.json','KEY_CONTACT_R1.json','HAND_POSTURE_COORDINATION_R1.json','FINAL_ASSET_PROTECTION_R1.json','HAND_POSTURE_CONTACT_REFINED_DESIGN_ONLY_R1.blend']
dump('DELIVERY_MANIFEST_R1.json',{'candidate_count':1,'files':[{'name':n,'bytes':(P/n).stat().st_size,'sha256':sha(P/n)} for n in deliverables],'STOP':'HUMAN REVIEW'})
print(status,'; protection',len(rows),'unchanged; report/review ready')
