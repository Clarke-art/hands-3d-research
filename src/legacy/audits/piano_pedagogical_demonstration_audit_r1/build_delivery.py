import json,sys,hashlib,html
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1];S=ROOT/'audits/minuet_stage_c_lightweight_animation_poc_r1'
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'audits/midi_driven_dual_hand_piano_performance_poc_r1/_deps'))
import mido
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(n,x): (P/n).write_text(x,encoding='utf8')
def save(n,x):write(n,json.dumps(x,ensure_ascii=False,indent=2))
tl=read(ROOT/'audits/minuet_stage_c_r1_dual_hand_synchronized_performance/PERFORMANCE_TIMELINE.json');samples=read(P/'SKIN_KEY_SAMPLES.json')['rows'];notes=tl['notes']
midipath=ROOT/'audits/minuet_in_g_longer_phrase_validation_r1/source/anna-magdalena-04.mid'
assert hashlib.sha256(midipath.read_bytes()).hexdigest()==tl['source_sha256']
mid=mido.MidiFile(midipath);tempo=500000;tick=0;sec=0;clock={0:0.0}
for msg in mido.merge_tracks(mid.tracks):
 sec+=mido.tick2second(msg.time,mid.ticks_per_beat,tempo);tick+=msg.time;clock[tick]=sec
 if msg.type=='set_tempo':tempo=msg.tempo
tracks=[]
for tr in mid.tracks:
 tick=0;events=[]
 for msg in tr:tick+=msg.time;events.append((tick,msg))
 tracks.append(events)
for n in notes:
 for seq,kind in [(n['on_sequence'],'on'),(n['off_sequence'],'off')]:
  tick,msg=tracks[n['track']][seq];assert tick==n[kind+'_tick'] and msg.note==n['midi_note'] and msg.channel==n['channel']
  assert (msg.type=='note_on' and msg.velocity>0) if kind=='on' else (msg.type=='note_off' or msg.velocity==0)
  assert abs(clock[tick]-n['source_'+kind+'_sec'])<1e-8
 assert abs(n['note_on']-n['source_on_sec']-.35)<1e-8
assert len(notes)==23 and sum(n['hand']=='R' for n in notes)==16
save('MIDI_VERIFICATION.json',dict(source=str(midipath),sha256=tl['source_sha256'],matched_notes=23,matched_events=46,tempo_map_verified=True,lead_sec=.35,fps=60,video_frames=357,key_index_convention='zero based: MIDI - 21',source_duration_sec=tl['source_duration_sec']))
defect=[
 dict(id='B01',severity='BLOCKING',time=1.133333333,range=[1.10,1.42],notes=['R02','R03'],title='中指／无名指早段轮廓融合',detail='A4 持键、B4 准备及进入阶段，两根独立手指的边界合并。原俯视可见，当前 skin 三角片相交支持不是单纯投影遮挡。会误导交替指的相对位置。',fix='仅复核早段中指／无名指准备与交接路径；保护 A4/B4 主动触键。',still='EARLY_NEW_OVERHEAD.png'),
 dict(id='B02',severity='BLOCKING',time=3.825,range=[3.73,3.87],notes=['R10','R11'],title='D5 → E5 交接出现明显穿指',detail='无名指释放 D5、中指弹 E5 时形成交叉和融合轮廓；正常教学与俯视暂停画面均无法作为两指独立交替的正确示范。',fix='只处理 D5 释放与 E5 中指进入的相对路径；保留事件、指法与有效触键。',still='LATE_NEW_TEACHING.png'),
 dict(id='B03',severity='BLOCKING',time=4.05,range=[3.99,4.10],notes=['R07','R12','R14'],title='闲置指嵌入黑键的示范风险',detail='2.600s 食指/A♯4，4.050s 中指/D♯5，4.916667s 无名指/C♯5：可见指端与黑键边界相接或截断，当前候选实际 skin 内部命中佐证嵌入。F♯5 主动指落点正确并不能消除旁边中指的错误路径。',fix='限定这三个片段的闲置食指／中指／无名指与对应黑键让位；先复核正常尺度可见边界，不做全键盘优化。',still='BLACK_75_NEW_SIDE_OBLIQUE.png'),
 dict(id='W01',severity='WARN',time=.433333333,range=[.35,.52],notes=['R00'],title='G♯4 附近接触的教学可见性不充分',detail='食指/G♯4 当前有几何内部命中，但原画面端部遮挡使误导程度不如 B03 明确。不能按毫米数直接升为 BLOCKING，也不能据此说完全无影响。',fix='Human 在原三视角复核；仅在确认误导时列入局部修复。',still='BLACK_68_NEW_OVERHEAD.png'),
 dict(id='W02',severity='WARN',time=2.492855,range=[2.44,2.55],notes=['R06','R07','R14','R15'],title='同指重复 G4 的部分回弹需要辨认',detail='2.492855s、5.064281s 拇指持续贴键，琴键在边界部分回弹再下沉。没有悬空或漏音证据，但远景容易被理解为一直持住；真实键机再击弦有效性未建模。',fix='先由教师确认这一重复音表现能否直接示范；必要时仅改重复音回弹可读性，不改 MIDI。',still=None)
]
validation=read(S/'ACTUAL_VALIDATION.json')
for d in defect:
 d['rate_observation']={'1x':'用户历史整体自然度接受；未提供逐缺陷的原速判定。','0.5x':'本轮以原帧序列核查；连续慢放感知由 Human 在页面确认。','0.25x':'同一原帧序列与关键暂停图支持所列空间判断；不冒称已完成 Human 慢放验收。'}
for n,r in zip(notes,samples):
 n['kind']='和弦 G3+B3+D4' if n['note_id'] in ['L00','L01','L02'] else ('同指重复音' if n['note_id'] in ['R06','R07','R14','R15'] else '连续单音')
 ds=[d for d in defect if n['note_id'] in d['notes']];n['defects']=[d['id'] for d in ds]
 n['contact']='PASS';n['hold_release']='WARN' if 'W02' in n['defects'] else 'PASS'
 n['spatial']='BLOCKING' if any(d['severity']=='BLOCKING' for d in ds) else ('WARN' if 'W01' in n['defects'] else 'PASS')
 if n['hand']=='R' and n['spatial']=='PASS':n['spatial']='UNKNOWN'
 n['teaching']='BLOCKING' if n['spatial']=='BLOCKING' else ('WARN' if ds else 'PASS')
 if n['spatial']=='UNKNOWN':n['teaching']='UNKNOWN'
 n['evidence_frames']={s['phase']:s['frame'] for s in r['samples']}
 n['scope']='PASS 仅针对该音主动指及已检查的交接，不表示同帧另一只手或所有闲置指均通过。'
save('NOTE_INDEX.json',notes);save('DEFECTS.json',defect)
write('PEDAGOGICAL_DEMONSTRATION_STANDARD.md','''# 教学示范审核标准 R1

原则：PEDAGOGICALLY_CORRECT_AND_HUMAN_VISIBLE_FIRST。模式：PEDAGOGICAL_AUDIT_ONLY。

PASS：实际候选指与真实目标键一致；准备、触键、键下沉、持键及释放有相互支持的实际 skin、运动键面和正常尺度画面证据；未发现会误导初学者的可见错误。有限采样 PASS 不等于连续几何证明。

WARN：轻微或教学影响不明的问题；必须说明学习影响与是否需要教师判断。BLOCKING：正常教学、俯视或侧斜视角下，慢放或暂停能把错误指位、穿指、穿键或虚假触键传达给学生；不能因原速不明显降级。UNKNOWN：证据不足，不算 PASS。

本轮直接打开唯一 Lightweight R1 Blend，只评估已保存 Action；23 音 × 6 阶段（准备 -80ms、NOTE_ON、+40ms、持键中点、NOTE_OFF、+60ms）检查实际变形网格。使用已有真实皮肤顶点及其固定 6mm 邻域，对实际键轴旋转后的可奏键面进行核查。局部顶点不是抽象 pad，也不是完整连续表面接触证明；微小正间隙和浅层负间隙不自动阻断。

三视角原视频 SHA256 对照通过，357 帧、60fps、5.95s。音乐时长 5.142852s；video_time = MIDI_source_time + 0.35s。事件时间由原 MIDI 逐事件/tempo map 核实。视频近邻帧可能在 NOTE_ON 前后 8.34ms 内；界面明确显示事件时间与原帧时间，不把近邻帧说成精确事件子帧。

教学结论按音符自己的主动指及交接评定，整段画面的其他缺陷单独列出。三视角切换暂停并保持同一原时间；单播放器避免多播放器时钟漂移。逐帧显示原渲染 PNG，不依赖浏览器 MP4 seek 的帧精度。连续播放速度由浏览器 playbackRate 实现，不生成新中间姿态。

本轮视觉检查是原帧静态/序列检查，并非人类连续观看实验。各速度主观显著性仍需 Human 操作确认；无证据不编写“半速已明显”的观察。指法符合候选，不代表专业最优或适合所有初学者；FINGERING_PROFESSIONAL_APPROVAL = DESIGN_PROVISIONAL。教师需确认跨指、同指重复音、闲置指伸展及左手手型。

冻结资产、MIDI、历史结论不改。工程历史 FAIL_CLOSED / NOT_APPROVED 保留。READY_FOR_HUMAN_PEDAGOGICAL_REVIEW 仅表示审核证据可交付，绝不等于教学通过。最终教学质量 HUMAN_PENDING。
''')
table=['# 23 音符教学审核表','', '所有时间为秒。源 ON/OFF 是实际 MIDI 时间；视频 ON/OFF 已加 0.35s。键编号采用原项目 0-based（MIDI−21），不是钢琴常见 1–88 编号。音符 ID 沿用源事件。','', '|音符/手指|目标键（MIDI/index）|类型|源 ON → OFF|视频 ON → OFF|触键|持键释放|空间自然性|教学结论|证据/问题|','|---|---|---|---|---|---|---|---|---|---|']
for i,n in enumerate(notes):
 table.append(f"|{n['note_id']} {n['hand']} {n['note_name']} / {n['finger']}指|{n['note_name']} ({n['midi_note']}/{n['key_index']})|{n['kind']}|{n['source_on_sec']:.6f} → {n['source_off_sec']:.6f}|{n['note_on']:.6f} → {n['note_off']:.6f}|{n['contact']}|{n['hold_release']}|{n['spatial']}|{n['teaching']}|[逐音定位](HUMAN_REVIEW.html#note={n['note_id']}) · [画面](contact_sheet_{i//4+1}.jpg) · {','.join(n['defects']) or '无本音已证实阻断'}|")
table+=['','每音六阶段原始数值见 SKIN_KEY_SAMPLES.json，页面“阶段”按钮可查全部阶段及三视角原帧。实际 skin 标记在全部 NOTE_ON、settle、hold、NOTE_OFF 样本内横向超出目标区域为 0mm；全部这些采样未发现明显悬空。离键后横移到下一目标不按错键处理。', '', '左手 G3/B3/D4 的 5/3/1 指同在 0.35s 触键，+40ms 三键均下沉，实际皮肤贴近键面；释放后 A3(4)、B3(3)、C4(2)、B3(3) 的目标及接触保持。左手闲置拇指/小指后段伸展是否适于初学者模仿，属于教师专业判断，不替教师认证。', '', 'F♯5（R12）由无名指落在抬高黑键面，主动触键 PASS；旁边中指/D♯5 干涉使该音整体空间结论 BLOCKING。G4 重复音四行 WARN 是回弹教学可读性，不是检测到错误 MIDI。', '', 'PASS 不等于整帧全体手指无几何接触；仅覆盖有限六阶段及已查关键交接。全段真实慢放主观自然度与未观察到的细节仍由 Human 判断。']
table+=['','右手未登记明确 BLOCKING/WARN 的其他八音，空间/综合结论记 UNKNOWN：当前候选有限采样仍有黑键或邻指几何命中，已有抽样画面不足以逐一确定教学可见性。不能因主动触键 PASS 而把这些音的整体空间判为 PASS。R04/R05 还覆盖早段邻指残余的尾部；未另行无限扩展检查。']
write('ALL_23_NOTES_TEACHING_AUDIT.md','\n'.join(table))
reg=['# 教学缺陷登记','', '共 3 项 BLOCKING、2 项 WARN。按教学问题分组计数，不按碰撞顶点、音符行或帧数重复累计。分级为本轮机器辅助审核意见，最终教学判定 HUMAN_PENDING。','']
for d in defect:
 reg += [f"## {d['id']} — {d['severity']} — {d['title']}",'',f"音符：{', '.join(d['notes'])}。主定位：视频 {d['time']:.9f}s；重点窗 {d['range']}s。",'',d['detail'],'', '最小后续范围：'+d['fix'],'',*[f"- {rate}：{obs}" for rate,obs in d['rate_observation'].items()],'']
 if d['still']:reg+=[f"[原候选原相机画面](../{S.name}/stills/{d['still']})",'']
reg+=['## 当前候选的局部几何佐证','', '以下全取 ACTUAL_VALIDATION.json 的 new 分支，不是旧候选深度：1.133333333s 中/无名指相交面配对 39；3.825s 为 93（不是毫米/体积）。0.433333333s 食指/G♯4 3.382mm；2.600s 食指/A♯4 4.427mm、无名指/C♯5 2.201mm；4.050s 中指/D♯5 5.469mm；4.916667s 无名指/C♯5 2.915mm。数值仅支持画面解释，不单独决定教学等级。','', '已优先检查食指/G♯4、A♯4、C♯5，中指/C♯5、D♯5，无名指/C♯5、D♯5。没有独立画面支持的组合不新增 BLOCKING；有限样本也不证明它们全程无干涉。','', '正常靠近黑键：仅二维覆盖不足以定穿模。摄像机遮挡：跨视角仍需结合当前 skin。浅层几何瑕疵：主动指局部小于约 1mm 的间隙/浅接触，未损害已查触键理解，不要求零间隙。不能把全部黑键内部命中一律归入无害瑕疵。','', '没有自动修复，没有新候选。STOP — HUMAN REVIEW。']
write('TEACHING_DEFECT_REGISTER.md','\n'.join(reg))
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>23 音符 · 教学示范审核 R1</title><style>
*{box-sizing:border-box}body{margin:0;background:#12191f;color:#edf3f6;font:15px system-ui,sans-serif}main{max-width:1320px;margin:auto;padding:18px}h1{font-size:22px;margin:0 0 6px}p{margin:6px 0;color:#b8c6d1}button,select{background:#263440;border:1px solid #506170;color:white;border-radius:5px;padding:8px;cursor:pointer}button:hover{background:#405364}.bar{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:10px 0}#stage{background:#343b41;position:relative}video,#frame{width:100%;max-height:64vh;object-fit:contain;display:block}#frame{display:none}input[type=range]{width:100%}table{border-collapse:collapse;width:100%;font-size:13px}td,th{padding:9px;border-bottom:1px solid #33414c;text-align:left}th{position:sticky;top:0;background:#263440}tr.active{background:#324757}.scroll{overflow:auto;max-height:420px}.BLOCKING{color:#ff9c8e}.WARN{color:#f2cf80}.PASS{color:#96d7b7}details{margin-top:15px}#issue{color:#f2cf80;min-height:24px}.note{color:#92cdda}a{color:#92cdda}#error{color:#ff9c8e}.chips{display:flex;flex-wrap:wrap;gap:6px}
</style><main><h1>3D Hands × 88-key Piano · 教学示范审核</h1><p>唯一 Lightweight R1 · 23 音符 · HUMAN_PENDING · 3 BLOCKING / 2 WARN · 历史 NOT_APPROVED 保留</p>
<div class="bar"><button id="restart">从头 1× 播放</button><button id="play">播放 / 暂停</button><label>速度 <select id="rate"><option value="1">1× 原速</option><option value="0.5">0.5×</option><option value="0.25">0.25×</option></select></label><label>视角 <select id="view"><option value="TEACHING">正常教学</option><option value="OVERHEAD">俯视</option><option value="SIDE_OBLIQUE">侧斜</option></select></label><button id="prev">← 前一原帧</button><button id="next">后一原帧 →</button></div>
<div id="stage"><video id="video" controls preload="metadata"></video><img id="frame" alt="原渲染帧，无插值"></div><div id="error" role="alert"></div><input aria-label="原视频时间轴" id="seek" type="range" min="0" max="356" step="1" value="0"><p id="clock"></p><p id="selected">默认原速完整演奏；点击音符可进入六阶段审核。</p><div class="bar" id="phases"></div>
<div class="chips" id="defects"></div><p id="issue"></p><div class="scroll"><table><thead><tr><th>音符 · 手 / 指</th><th>目标键 MIDI/index</th><th>类型</th><th>MIDI ON / OFF</th><th>视频 ON / OFF</th><th>触键</th><th>持/放</th><th>空间</th><th>教学</th></tr></thead><tbody id="notes"></tbody></table></div>
<details><summary>证据与限制</summary><p>视频 60fps / 357 帧；音乐时间加 0.35s 对应视频。切换视角会暂停并保持同一时刻。逐帧使用已有 PNG，显示实际原帧时间；事件子帧与最近视频帧可能相差最多 8.34ms。连续慢放的主观显著性待 Human 确认；未补帧、未生成动作。若媒体加载失败，请保留本目录与相邻原候选目录的相对位置。</p><p>逐音 PASS 仅覆盖本音主动指及已查交接，不代表另一只手和全部闲置指无问题。键 index 沿用 0-based。指法专业认可仍为 DESIGN_PROVISIONAL。</p><p><a href="ALL_23_NOTES_TEACHING_AUDIT.md">23 音符审核表</a> · <a href="TEACHING_DEFECT_REGISTER.md">缺陷登记</a> · <a href="FINAL_ANSWERS.md">12 问回答</a></p></details></main><script>
const notes=__NOTES__,defects=__DEFECTS__,base='../minuet_stage_c_lightweight_animation_poc_r1/';
const $=id=>document.getElementById(id),v=$('video'),img=$('frame');let frame=0,still=false,chosen=null,requested=0;
function frameURL(f){return base+'_frames/'+$('view').value+'/'+String(f).padStart(4,'0')+'.png'}
function display(){let t=still?frame/60:v.currentTime;frame=Math.max(0,Math.min(356,Math.round(t*60)));$('seek').value=frame;$('clock').textContent=`视频 ${t.toFixed(6)}s · 音乐 ${(t-.35).toFixed(6)}s · 原帧 ${frame}/356${still?' · 精确 PNG 帧':' · 播放时近邻帧索引'}`;for(const row of $('notes').children){const n=notes.find(n=>n.note_id===row.dataset.id);row.classList.toggle('active',t>=n.note_on&&t<n.note_off)}}
function locate(t){v.pause();requested=t;frame=Math.max(0,Math.min(356,Math.round(t*60)));still=true;img.src=frameURL(frame);img.style.display='block';v.style.display='none';if(v.readyState)v.currentTime=frame/60;display()}
function loadView(){v.pause();const t=still?frame/60:v.currentTime;v.src=base+'normal_speed_'+$('view').value.toLowerCase()+'_NOT_APPROVED.mp4';v.onloadedmetadata=()=>{v.currentTime=t;v.playbackRate=Number($('rate').value);display()};if(still)img.src=frameURL(frame)}
async function play(){if(!v.paused){locate(v.currentTime);return}if(still){v.currentTime=frame/60;still=false;img.style.display='none';v.style.display='block'}try{await v.play()}catch(e){$('error').textContent='播放未开始：'+e.message}}
function selectNote(n){chosen=n;location.hash='note='+n.note_id;$('selected').textContent=`${n.note_id} ${n.hand} ${n.note_name} / ${n.finger}指 · 事件 ON ${n.note_on.toFixed(6)}s · 最近原帧 ${(Math.round(n.note_on*60)/60).toFixed(6)}s`;$('phases').replaceChildren();for(const [label,t] of [['准备',n.note_on-.08],['NOTE_ON',n.note_on],['下沉 +40ms',n.note_on+.04],['持键',(n.note_on+n.note_off)/2],['NOTE_OFF',n.note_off],['释放 +60ms',n.note_off+.06]]){const b=document.createElement('button');b.textContent=label;b.onclick=()=>locate(t);$('phases').append(b)}$('issue').textContent=n.defects.length?n.defects.join(' / ')+'：'+defects.filter(d=>n.defects.includes(d.id)).map(d=>d.title).join('；'):'本音所查主动触键与交接未发现阻断；专业指法待教师确认。';locate(n.note_on)}
for(const n of notes){const tr=document.createElement('tr');tr.dataset.id=n.note_id;tr.innerHTML=`<td><button>${n.note_id} ${n.note_name} · ${n.hand}/${n.finger}</button></td><td>${n.note_name} ${n.midi_note}/${n.key_index}</td><td>${n.kind}</td><td>${n.source_on_sec.toFixed(6)} / ${n.source_off_sec.toFixed(6)}</td><td>${n.note_on.toFixed(6)} / ${n.note_off.toFixed(6)}</td>${['contact','hold_release','spatial','teaching'].map(k=>`<td class="${n[k]}">${n[k]}</td>`).join('')}`;tr.querySelector('button').onclick=()=>selectNote(n);$('notes').append(tr)}
for(const d of defects){const b=document.createElement('button');b.className=d.severity;b.textContent=d.id+' '+d.title;b.onclick=()=>{locate(d.time);$('issue').textContent=d.detail;$('selected').textContent=d.id+' · 精确证据 '+d.time.toFixed(9)+'s · 当前为最近原帧';$('phases').replaceChildren();if(d.still){const a=document.createElement('a');a.href=base+'stills/'+d.still;a.target='_blank';a.textContent='打开精确诊断时刻原图';$('phases').append(a)}if(d.id==='B03'||d.id==='W02'){for(const t of d.id==='B03'?[2.6,4.05,4.916666667]:[2.492855,5.064281]){const q=document.createElement('button');q.textContent=t.toFixed(6)+'s';q.onclick=()=>locate(t);$('phases').append(q)}}};$('defects').append(b)}
$('play').onclick=play;$('rate').onchange=()=>v.playbackRate=Number($('rate').value);$('view').onchange=loadView;$('prev').onclick=()=>locate((frame-1)/60);$('next').onclick=()=>locate((frame+1)/60);$('seek').oninput=()=>locate(Number($('seek').value)/60);$('restart').onclick=()=>{$('rate').value='1';v.playbackRate=1;locate(0);play()};v.ontimeupdate=display;v.onerror=()=>{$('error').textContent='媒体加载失败；仍可使用原帧模式，或从本地 HTTP 服务打开。'};img.onerror=()=>{$('error').textContent='原帧加载失败，请检查相邻候选目录。'};loadView();display();const id=new URLSearchParams(location.hash.slice(1)).get('note');if(id&&notes.some(n=>n.note_id===id))selectNote(notes.find(n=>n.note_id===id));
</script></html>'''
write('HUMAN_REVIEW.html',page.replace('__NOTES__',json.dumps(notes,ensure_ascii=False)).replace('__DEFECTS__',json.dumps(defect,ensure_ascii=False)))
write('HUMAN_REVIEW.html',(P/'HUMAN_REVIEW.html').read_text(encoding='utf8').replace("'本音所查主动触键与交接未发现阻断；专业指法待教师确认。'","(n.spatial==='UNKNOWN'?'主动触键 PASS；该音其他空间命中的教学可见性证据不足，UNKNOWN。':'本音所查主动触键与交接未发现阻断；专业指法待教师确认。')"))
print('DELIVERY_BUILT',len(notes),'notes',len(defect),'defects')
