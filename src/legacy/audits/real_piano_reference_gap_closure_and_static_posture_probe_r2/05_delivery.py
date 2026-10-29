from pathlib import Path
import json,hashlib,html
P=Path(__file__).resolve().parent;ROOT=P.parents[1];R1=P.parent/'piano_hand_posture_reference_and_static_feasibility_r1';OLD=P.parent/'midi_driven_dual_hand_piano_performance_poc_r1';REF=P.parent/'midi_driven_hand_posture_and_contact_refinement_r1'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
# Raw third-party page text is not needed in the delivered access diagnostic.
a=read(P/'REFERENCE_ACCESS_R2.json')
for row in a:
 row.pop('text',None);row['iframes']=[x for x in row['iframes'] if 'youtube.com/embed' in x]
 row['images']=[x for x in row['images'] if 'octave-stretch' in x['src'] or 'left_hand' in x['src']]
dump('REFERENCE_ACCESS_R2.json',a)
before=read(P/'PROTECTED_INPUTS_BEFORE_R2.json');changed=[p for p,v in before.items() if not Path(p).is_file() or sha(Path(p))!=v];assert not changed,changed
paths={'RIGHT_R2':ROOT/'production_spec/right_hand_product_baseline_r2/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R2.blend','LEFT_R1':ROOT/'production_spec/left_hand_product_baseline_r1/LEFT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1.blend','RIGHT_R1_fallback':ROOT/'production_spec/right_hand_product_baseline_r1/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1.blend'}
expected={'RIGHT_R2':'c946fed318fa88c238d9aacc30cfb4e52f268848f0ad65a4dcbf594754d791f0','LEFT_R1':'54307bb199a75a5e684c29d346de9ca6bf2f8e7696911d9d69c57559516ad1a7','RIGHT_R1_fallback':'4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2'}
hands={n:{'path':str(p),'expected_sha256':expected[n],'current_sha256':sha(p),'matches':sha(p)==expected[n]} for n,p in paths.items()};assert all(x['matches'] for x in hands.values())
authority=read(OLD/'KEYBOARD_AUTHORITY_R1.json');piano={n:{'path':authority[n],'current_sha256':sha(Path(authority[n])),'expected_sha256':authority[k],'matches':sha(Path(authority[n]))==authority[k]} for n,k in [('source_manifest','KEYBOARD_SOURCE_SHA256'),('runtime','runtime_sha256')]};assert all(x['matches'] for x in piano.values())
protect={'status':'UNCHANGED','checked_file_count':len(before),'changed_files':changed,'hands':hands,'piano_authority':piano,'formal_readback':read(P/'FORMAL_ASSET_READBACK_R2.json'),'before_manifest_sha256':sha(P/'PROTECTED_INPUTS_BEFORE_R2.json'),'scope':'Inherited protected-input corpus plus all R1 posture-reference audit files excluding bytecode; includes frozen piano models/master/manifests/runtime, formal hand baselines/pointers, prior candidate/actions/media, MIDI/audio/timeline and markers. Exact paths/hashes in before manifest. Not a claim about every unrelated file on the computer.','HAND_BASELINES_UNCHANGED':True,'PIANO_BASELINE_UNCHANGED':True,'production_pointer_changed':False,'new_blend_count':0,'new_action_count':0,'candidate_mesh_rig_changes':'NOT_APPLICABLE_NO_CANDIDATE','saved_any_formal_blend':False}
dump('FINAL_ASSET_PROTECTION_R2.json',protect)
questions=[('Q1','真实左手八度参考有效补充？','PARTIAL','左手静态图重新核验；新增对侧八度图片/文字，左手三闲置指与侧面仍缺证据。'),('Q2','右手含 F# 真人五指参考有效补充？','PARTIAL','官方指序文字重新核验；实际影像未播放，未新增黑键姿态观察。'),('Q3','建立有证据边界的自然姿态约束？','YES','八类约束逐项区分四种依据；定性合同成立，执行门槛未满足。'),('Q4','执行唯一静态候选？','NO','关键黑键五指可见关系尚未取得，不启动求解。'),('Q5','LEFT L1 小指 D2 自然触键？','NOT_RUN','未测试。'),('Q6','LEFT L2 拇指 D3 自然触键？','NOT_RUN','未测试。'),('Q7','左手中间三指自然？','NOT_RUN','未测试。'),('Q8','左手掌腕/键盘净空合理？','NOT_RUN','未测试。'),('Q9','RIGHT R1 五指准备自然？','NOT_RUN','未测试。'),('Q10','RIGHT R2 中指 F#5 触键自然？','NOT_RUN','未测试。'),('Q11','发现必须修改正式 mesh/rig 的证据？','NO','没有新候选或硬几何不可达证明；此 NO 不证明当前模型自然可达。'),('Q12','可进入下一轮动态规划器设计？','NO','静态与 Human 门槛均未通过。')]
status={'Q1_Q12':{q:{'question':t,'answer':ans,'reason':why} for q,t,ans,why in questions},'REAL_REFERENCE_STATUS':'PARTIAL_STATIC_AND_TEXT / BLACK_KEY_VISUAL_UNVERIFIED','STATIC_PROBE':'NOT_RUN','LEFT_OCTAVE_FEASIBILITY':'UNKNOWN_NOT_RUN','RIGHT_FIVE_FINGER_FEASIBILITY':'UNKNOWN_NOT_RUN','FSHARP_CONTACT':'NOT_RUN','LEFT_IDLE_FINGERS':'NOT_RUN','PALM_WRIST_CLEARANCE':'NOT_RUN','NEXT_MOTION_PLANNER_READY':'NO','FINAL_STATUS':'REFERENCE_EVIDENCE_INSUFFICIENT','HAND_BASELINES_UNCHANGED':True,'PIANO_BASELINE_UNCHANGED':True,'stop':'STOP — HUMAN REVIEW','new_static_candidate_count':0,'observed_video_timestamps':[],'failure_class':'REFERENCE_EVIDENCE_LIMIT'}
dump('FINAL_STATUS_R2.json',status)
geom=read(P/'HAND_KEYBOARD_STATIC_FEASIBILITY_R2.json')['geometry']
rows='\n'.join(f'|{q}|{t}|**{ans}**|{why}|' for q,t,ans,why in questions)
lines='\n'.join(f'{k} = {v}' for k,v in status.items() if k not in ['Q1_Q12','new_static_candidate_count','observed_video_timestamps','failure_class','stop'])
report=f'''# REAL_PIANO_REFERENCE_GAP_CLOSURE_AND_STATIC_POSTURE_PROBE_R2_REPORT

2026-10-08 · DESIGN_ONLY · HUMAN_VISIBLE_PRODUCT_QUALITY_FIRST

**FINAL_STATUS = REFERENCE_EVIDENCE_INSUFFICIENT**。补充了对侧八度静态参考、原版 Musette 身份与真实播放器访问结果，建立八类有证据边界的姿态合同；未执行静态候选。自然几何可行性仍 UNKNOWN，不能将 NOT_RUN 写成 PASS。

## 参考补证与本轮门槛

实际打开 PiaDOOR、Pianote、Hoffman Lesson 14/236；实际查看两张八度照片。PiaDOOR 是 Für Elise 左手 A–E–A 准备，有额外中间指任务；Pianote 新图是右手 C 八度，不能替代左手。Hoffman 官方文字确认五指 D/E/F#/G/A，Lesson 236 确认原版 A 段而非早期简化版。

三个官方教学页内实际点击播放后均要求登录/机器人验证，video.readyState=0、currentTime=0、duration 未知，未观察任何视频时间点。直接嵌入入口的错误 153 不是唯一失败依据；已经在正常来源页中重试播放。没有绕过验证或下载视频。

有限来源核查已停止。关键缺口是右手含黑键五指的可见协调关系，左手三闲置指及腕侧视也仍有限。**没有要求精确同曲、同演奏者、全部关节三维角或静态之前先证明动态过渡**。左手静态图加一般教学文字可支持部分约束，但音级指序本身不能补成可信的五指黑键演示。故本轮不执行条件式静态实验。

详见 [参考清单](REAL_PIANO_REFERENCE_MANIFEST_R2.md)、[八类合同](NATURAL_PIANO_HAND_POSTURE_CONTRACT_R2.md)。本合同 YES 代表依据分类与检验要求明确，不代表科学姿态完整、数值求解政策已校准或模型通过。

## 正式几何与资产保护

Blender 5.1.2 后台只读重新打开正式 RIGHT R2 / LEFT R1。两手 3300 顶点、21 骨；neutral canonical 网格最大偏差分别 2.2602e-13 / 1.7554e-13 mm，intrinsic identity 均匹配。保持 existing pad 定义，未保存 blend。

|测量|R2 结果|边界|
|---|---:|---|
|D2–D3 中心距|{geom['left_octave_centers_mm']:.3f} mm|不是必须精确达到的 pad 触点距|
|前部内侧区域最小点距|{geom['left_front_inner_edges_point_minimum_mm']:.3f} mm|零面积边缘下界，不是实际安全 pad 目标|
|左手静置 pad 空间距|153.007 mm|重新读取；不是最大自然跨度|
|D5–A5 中心距|{geom['right_D5_A5_centers_mm']:.3f} mm|不证明共享掌位自然|
|F#5 黑白顶面高差|{geom['Fsharp5_height_above_white_mm']:.3f} mm|正式静置键几何|
|F#5 前端相对白键前沿|{geom['Fsharp5_front_offset_from_white_mm']:.3f} mm|靠后；不能排成同深指尖直线|

全部毫米值是正式键盘已批准教学等效比例，不是制造商标定。完整可奏面见 [可行性 JSON](HAND_KEYBOARD_STATIC_FEASIBILITY_R2.json)。垂直 3 mm / 水平 2 mm 容差保持，且必须处于实际可奏区域；未实际测试任何接触、净空或关节项。

最终复核 **{len(before)} 个受保护文件**，变化列表为空；三份手 baseline SHA 与用户指定值相同；钢琴 source manifest/runtime 及继承保护集均相同。保护范围/逐路径证据见 [保护 JSON](FINAL_ASSET_PROTECTION_R2.json) 和 `PROTECTED_INPUTS_BEFORE_R2.json`。没有修改 production pointer、MIDI、指法、音频、键几何、hand mesh/rest/weights/correctives/drivers。

## 静态与失败归因

L1/L2/R1/R2 全为 NOT_RUN，候选数 0，动作数 0。root 差异、实际候选 pad 跨度、主动指接触、闲置指、掌腕净空、邻键干扰、关节状态均无新测量。没有把旧失败动态帧重新命名为 R2 静态候选。

REFERENCE_EVIDENCE_LIMIT = BLOCKING；GEOMETRY_LIMIT = NOT_ESTABLISHED；POSTURE_CONSTRAINT_LIMIT = NOT_TESTED；IK_SOLVER_FAILURE = NOT_RUN。未证明需改正式 mesh/rig，也未证明自然可达。

## Human-visible 对比与交付

[review.html](review.html) 使用“真人来源链接 → 旧失败图 → R2 未执行状态”三栏。没有嵌入或重发布外部照片；引用旧图原文件，不生成重复图/视频。普通产品斜上方旧图及旧 CONTACT_SIDE 斜视风险图保留，不将其误标为新顶视、严格侧视或新 first-web 证据。R2 教学顶视、侧斜视、first-web 三项均明确 NOT_RUN。

条件式实验未启动，因此 **STATIC_POSTURE_PROBE_R2.blend、STATIC_POSTURE_RESULTS_R2.json、三张 EVIDENCE_*_R2.png 不生成**。这是门槛未满足的明确结果，非遗失文件。已交付报告、review.html、参考清单、合同、可行性 JSON、下一轮要求、最终保护 JSON，另附只读重新测量与访问/交付验证记录。

## Q1–Q12

|编号|问题|回答|依据|
|---|---|---|---|
{rows}

## 最终停止状态

```text
{lines}
STOP — HUMAN REVIEW
```

本轮等待 Human 决策。最小下一步是使可信五指黑键示范可实际核查，再判断是否授权一次有界四姿态静态实验；[后续要求](NEXT_MOTION_PLANNER_REQUIREMENTS_R2.md) 不构成自动进入动态规划或完整演奏生成的许可。
'''
(P/'REAL_PIANO_REFERENCE_GAP_CLOSURE_AND_STATIC_POSTURE_PROBE_R2_REPORT.md').write_text(report,encoding='utf-8')
qhtml=''.join(f'<tr><th>{q}</th><td>{t}</td><td><b>{ans}</b></td><td>{why}</td></tr>' for q,t,ans,why in questions)
docnames=['REAL_PIANO_REFERENCE_GAP_CLOSURE_AND_STATIC_POSTURE_PROBE_R2_REPORT.md','REAL_PIANO_REFERENCE_MANIFEST_R2.md','NATURAL_PIANO_HAND_POSTURE_CONTRACT_R2.md','HAND_KEYBOARD_STATIC_FEASIBILITY_R2.json','NEXT_MOTION_PLANNER_REQUIREMENTS_R2.md','FINAL_ASSET_PROTECTION_R2.json','FORMAL_ASSET_READBACK_R2.json','FINAL_STATUS_R2.json']
doclinks=''.join(f'<a href="{n}">{label}</a>' for n,label in zip(docnames,['完整报告','参考与证据边界','八类姿态合同','四姿态/冻结几何 JSON','下一轮门槛','资产保护','正式资产重新测量','最终状态']))
page=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R2 · 钢琴手姿态补证审核</title>
<style>:root{{color-scheme:light}}*{{box-sizing:border-box}}body{{margin:0;background:#f4f1ec;color:#292722;font:16px/1.7 system-ui,"Microsoft YaHei",sans-serif}}main{{max-width:1440px;margin:auto;padding:44px 28px}}h1{{font-size:clamp(26px,3vw,42px);line-height:1.25;max-width:900px}}h2{{font-size:24px;margin-top:38px}}h3{{font-size:18px}}.eyebrow{{letter-spacing:.14em;font-size:12px;color:#6b655b}}.status{{display:inline-block;background:#ffe1b2;color:#704508;padding:6px 12px;border-radius:6px;overflow-wrap:anywhere}}.lede{{max-width:900px}}.facts,.compare,.poses{{display:grid;gap:16px}}.facts{{grid-template-columns:repeat(4,1fr);margin:28px 0}}.fact,.card,.pose{{background:#fffdf9;border:1px solid #dcd7cd;border-radius:12px;padding:20px}}.fact strong{{display:block;font-size:23px}}.fact small{{color:#71695e}}.compare{{grid-template-columns:repeat(3,minmax(0,1fr))}}.poses{{grid-template-columns:repeat(4,minmax(0,1fr))}}a{{color:#285c62;text-underline-offset:3px;overflow-wrap:anywhere}}img{{width:100%;height:auto;display:block;border-radius:5px;margin-top:14px}}figure{{margin:0 0 18px}}figcaption{{font-size:13px;color:#736a5e;line-height:1.6}}.pending{{border:1px dashed #b6a994;padding:24px 16px;background:#faf5e9;margin-top:16px}}.pending b{{display:block;font-size:23px}}.tag{{font:12px/1.5 ui-monospace,monospace;background:#eee9df;padding:3px 6px;overflow-wrap:anywhere}}.tablewrap{{overflow-x:auto}}table{{width:100%;border-collapse:collapse;background:#fffdf9;font-size:14px}}th,td{{padding:12px;border-bottom:1px solid #ded8cb;text-align:left;vertical-align:top}}td:nth-child(3){{white-space:nowrap}}.docs{{display:flex;flex-wrap:wrap;gap:10px;margin-top:20px}}.docs a{{background:#fffdf9;border:1px solid #dcd7cd;border-radius:6px;padding:8px 12px}}details{{background:#fffdf9;border:1px solid #dcd7cd;border-radius:8px;padding:14px 18px;margin-top:18px}}summary{{cursor:pointer;font-weight:600}}footer{{margin-top:36px;color:#71695e}}@media(max-width:980px){{.compare{{grid-template-columns:1fr}}.poses,.facts{{grid-template-columns:repeat(2,1fr)}}}}@media(max-width:540px){{main{{padding:26px 16px}}.poses{{grid-template-columns:1fr}}.fact{{padding:12px}}table{{min-width:740px}}}}</style>
<main><div class="eyebrow">DESIGN ONLY · HUMAN VISIBLE PRODUCT QUALITY FIRST · 2026-10-08</div><h1>真人演奏参考补证<br>与静态姿态可行性审核 · R2</h1><span class="status">REFERENCE_EVIDENCE_INSUFFICIENT</span><p class="lede">官方文字和八度静态图已核验。三个视频实际点击播放后都要求登录验证，含 F# 的五指协调影像仍未看到。本轮没有构建静态候选，自然可行性仍未知。正式资产经重新读取与哈希检查保持不变。</p>
<div class="facts"><div class="fact"><strong>PARTIAL</strong><small>真人参考补证</small></div><div class="fact"><strong>0 / 4</strong><small>执行的静态姿态</small></div><div class="fact"><strong>{len(before)} / {len(before)}</strong><small>冻结文件哈希不变</small></div><div class="fact"><strong>NO</strong><small>进入动态规划设计</small></div></div>
<h2>真人来源 → 旧失败姿态 → R2 状态</h2><div class="compare"><section class="card"><h3>① 原始真人来源</h3><p><span class="tag">STATIC_REFERENCE</span></p><p><a href="https://piadoor.com/en/piece/2/basic/" target="_blank" rel="noreferrer">PiaDOOR · 左手八度</a><br>Beginning → Prepare The Left Hand Octave Position；A–E–A 照片。中间 E 有任务，不能当成三指全闲置。</p><p><a href="https://www.pianote.com/blog/play-piano-with-small-hands/" target="_blank" rel="noreferrer">Pianote · 小手八度</a><br>Octaves 小节。新增照片是右手 C 八度，可比较前部触点，不能冒充左手。</p><p><span class="tag">TEXT VERIFIED / VIDEO UNVERIFIED</span></p><p><a href="https://app.hoffmanacademy.com/lessons/piano/d-major-pentascale/video/" target="_blank" rel="noreferrer">Hoffman Lesson 14</a><br>Full Transcript 后段指位说明：D/E/F#/G/A → 1/2/3/4/5。未观看到黑键触点或共享掌位。</p><p><a href="https://app.hoffmanacademy.com/lessons/piano/musette-in-d-a-section/video/" target="_blank" rel="noreferrer">Hoffman Lesson 236 · Musette 原版</a><br>开头版本介绍；不能用早期简化版替代。没有已观察的演奏时间点。</p><p>未获外部照片重发布授权，因此只给原始链接和具体位置。视频登录验证没有被绕过。</p></section>
<section class="card"><h3>② 旧失败证据 · 不是 R2</h3><figure><a href="../piano_hand_posture_reference_and_static_feasibility_r1/EVIDENCE_LEFT_OCTAVE_POSTURE_R1.png"><img src="../piano_hand_posture_reference_and_static_feasibility_r1/EVIDENCE_LEFT_OCTAVE_POSTURE_R1.png" alt="旧失败左手姿态对比，0.85 秒与 1.15 秒"></a><figcaption>R1 审核图，来自更早动态失败候选；0.85 / 1.15 s。观察八度两端、中间三指与掌侧风险，不作为新静态接触证据。</figcaption></figure><figure><a href="../piano_hand_posture_reference_and_static_feasibility_r1/EVIDENCE_RIGHT_FIVE_FINGER_POSTURE_R1.png"><img src="../piano_hand_posture_reference_and_static_feasibility_r1/EVIDENCE_RIGHT_FIVE_FINGER_POSTURE_R1.png" alt="旧失败右手五指图"></a><figcaption>旧右手 0.65 / 1.367 s 产品斜上方图。既有机械姿态和接触限制继续保留。</figcaption></figure><a href="../midi_driven_hand_posture_and_contact_refinement_r1/_contact_left.png">旧 CONTACT_SIDE 左手风险图 · 1.142 s</a><br><a href="../midi_driven_hand_posture_and_contact_refinement_r1/_contact_right.png">旧 CONTACT_SIDE 右手风险图 · 2.567 s</a><p>这些是既有斜视检查，不是 R2 新图，也不是完整三视图通过证明。点击旧图可查看原尺寸。</p></section>
<section class="card"><h3>③ 本轮静态候选</h3><div class="pending"><b>NOT_RUN</b>关键黑键五指可见关系仍缺证据，条件式静态求解未启动。</div><p>没有新 blend、静态解、证据图或 Action。没有把旧帧重命名成 R2。</p><p>教学顶视 / PALMAR：<b>NOT_RUN</b><br>SIDE OBLIQUE：<b>NOT_RUN</b><br>FIRST_WEB 合理近景：<b>NOT_RUN</b></p><p>四姿态主动接触、闲置指、掌腕净空、邻键干扰、关节姿态全部未测试。机器检查与视觉自然性均不写 PASS。</p><p>缺的是可观看的真人黑键五指关系，不要求精确同曲、精确三维角度或预先证明动态过渡。</p><p>失败归因：<b>REFERENCE_EVIDENCE_LIMIT</b>。几何极限未证实；IK 未运行；没有必须改正式 mesh/rig 的证据。</p></section></div>
<h2>唯一四姿态实验的执行记录</h2><div class="poses"><section class="pose"><h3>L1 · 小指 D2</h3><span class="tag">NOT_RUN</span><p>拇指准备 D3，中间三指放松。接触、跨度、root 差异和净空均未知。</p></section><section class="pose"><h3>L2 · 拇指 D3</h3><span class="tag">NOT_RUN</span><p>小指准备 D2，中间三指有自然曲度。单独触键不能证明交替自然。</p></section><section class="pose"><h3>R1 · D5–A5 准备</h3><span class="tag">NOT_RUN</span><p>五指共享掌位，不强迫全部同时触键；F# 高且靠后。</p></section><section class="pose"><h3>R2 · 中指 F#5</h3><span class="tag">NOT_RUN</span><p>其他四指准备或放松；中指与掌腕关系尚无新验证。</p></section></div>
<details><summary>几何和接触条件 · 不能代替自然性验证</summary><p>D2–D3 中心距 167.569 mm；左手静置 pad 空间距 153.007 mm；两键前部内边缘点下界 144.480 mm。静置不是最大自然跨度，键中心不是唯一触点。</p><p>D5–A5 中心距 95.754 mm；F#5 高差 15.444 mm、前端深度 49.421 mm。保持垂直 3 mm / 水平 2 mm 容差，且必须在实际可奏面内。</p><p>两手只读重新打开：3300 顶点 / 21 骨，neutral 网格与 intrinsic identity 匹配。没有保存正式 blend。{len(before)} 个保护文件 SHA 不变。</p></details>
<h2>Q1–Q12</h2><div class="tablewrap"><table><thead><tr><th>编号</th><th>问题</th><th>结果</th><th>依据</th></tr></thead><tbody>{qhtml}</tbody></table></div>
<h2>审核文件</h2><nav class="docs">{doclinks}</nav><footer><b>STOP — HUMAN REVIEW</b><p>下一步仅供 Human 决策：补足可观看的可信五指黑键示范，再评估是否启动一次静态实验。本轮不会自动进入完整演奏动作生成。</p></footer></main></html>'''
(P/'review.html').write_text(page,encoding='utf-8')
images=[R1/'EVIDENCE_LEFT_OCTAVE_POSTURE_R1.png',R1/'EVIDENCE_RIGHT_FIVE_FINGER_POSTURE_R1.png',REF/'_contact_left.png',REF/'_contact_right.png']
dump('REVIEW_IMAGE_PROVENANCE_R2.json',{'new_candidate_image_count':0,'external_images_embedded':False,'prior_images':[{'path':str(p),'sha256':sha(p),'role':'PRIOR_FAILED_CANDIDATE_ONLY'} for p in images]})
print('DELIVERED',status['FINAL_STATUS'],len(before),'UNCHANGED')
