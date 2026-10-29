from pathlib import Path
import json,hashlib,html
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent;REF=P.parent/'midi_driven_hand_posture_and_contact_refinement_r1'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
G=read(P/'HAND_KEYBOARD_SPAN_FEASIBILITY_R1.json');font='C:/Windows/Fonts/msyh.ttc';F=lambda n:ImageFont.truetype(font,n)
provenance=[]
for side,name,times,crop in [('L','EVIDENCE_LEFT_OCTAVE_POSTURE_R1.png',[.85,1.15],(290,280,650,650)),('R','EVIDENCE_RIGHT_FIVE_FINGER_POSTURE_R1.png',[.65,1.3666666666666667],(870,280,1230,650))]:
 im=Image.new('RGB',(1500,850),'#15232b');d=ImageDraw.Draw(im)
 title='左手八度 · 既有失败姿态' if side=='L' else '右手五指 · 既有准备与 F# 触键姿态'
 d.text((28,20),title,font=F(34),fill='#f5eee2');d.text((28,71),'本轮只读证据｜沿用上一轮渲染与统一肤色｜未生成新静态候选',font=F(21),fill='#efbd76')
 for j,t in enumerate(times):
  src=REF/'_frames'/f'{round(t*60):04}.png';pic=Image.open(src).convert('RGB').crop(crop).resize((475,488),Image.Resampling.LANCZOS);im.paste(pic,(28+j*493,157));d.text((28+j*493,117),f'旧候选  t={t:.3f}s',font=F(24),fill='white');provenance.append({'output':name,'source':str(src),'source_sha256':sha(src),'time_sec':t,'crop_pixels':crop,'display_size':[475,488]})
 lines=(['D2–D3 中心距','167.569 mm','左手静置 pad 跨度','153.007 mm（空间距离）','自然共同掌姿：未证实','掌部碰撞：旧版仍存在'] if side=='L' else ['D5–A5 中心距','95.754 mm','F#5 高于白键','15.444 mm','F#5 前端深度','49.421 mm（白键前缘起）'])
 for j,line in enumerate(lines):d.text((1040,166+j*63),line,font=F(23 if j%2==0 else 27),fill='#f2c384' if j%2 else '#f5eee2')
 d.rounded_rectangle((28,679,1472,821),radius=14,fill='#2c3032');d.text((49,699),'新静态候选：未生成 / REFERENCE_EVIDENCE_INSUFFICIENT',font=F(26),fill='#f2c384');d.text((49,747),'不能用当前截图的跨度或单点接触，证明自然掌腕、闲置指与净空已经合格。',font=F(23),fill='white');d.text((49,784),'真实参考及图片位置见审核页；外部摄影仅链接，不复制为产品证据。',font=F(19),fill='#c0cbd0');im.save(P/name)
dump('EVIDENCE_IMAGE_PROVENANCE_R1.json',provenance)
qa=[
('Q1','是，找到并查看 PiaDOOR 左手白键八度静态照片；不是 D2/D3，且有 E 的额外任务。三闲置指及连续腕部证据不足。'),
('Q2','是，找到并查看 Daniel Griffiths 右手 C–G 五指照片；Hoffman 官方文字支持 D/E/F#/G/A 指序，但视频未能播放，未验证黑键换指画面。'),
('Q3','未证实自然匹配。D2–D3 中心距 167.569 mm；左手静置 pad 空间跨度 153.007 mm，旧失败候选最大 176.185 mm。后者有碰撞，不能作为自然可达证明。'),
('Q4','未证实自然匹配。D5–A5 中心距 95.754 mm；F# 高 15.444 mm、前端深度 49.421 mm。各指单独能触键不等于五指共同掌姿可行。'),
('Q5','是。固定姿态增量/简单被动耦合、逐时刻接触目标、掌部回拉初始化、少量净空代理，均缺少已验证的真实演奏姿态依据；旧版已有 shared root 和连续性限制。'),
('Q6','已建立带来源、产品要求、rig 支持与未知项的 A–F 合同草案；未获教师批准，连续动作部分证据未闭合。'),
('Q7','未执行。参考不足，未通过用户规定的静态试验前置门槛；静态候选 0 份、新完整 Action 0 份。'),
('Q8','未知。没有证明左手三闲置指自然与拇指/小指正确接触、掌部净空能同时成立。'),
('Q9','尚不可接受为已验证结果。旧版掌部碰撞筛查 L 129/409、R 10/409；真实腕高和掌底侧视证据不足。'),
('Q10','未发现必须改正式 mesh、骨长或 rig 的证据；也未证明硬几何不可达。保持正式资产不变。'),
('Q11','可据需求草案讨论协调规划器架构；不能据此宣布证据充分并开始实现。先补可核查动作参考，再完成唯一四姿态静态验证。')]
status={'REAL_PIANO_REFERENCE':'PARTIAL_VERIFIED_STATIC_AND_TEXT','LEFT_OCTAVE_GEOMETRY':'NATURAL_FEASIBILITY_UNPROVEN','RIGHT_FIVE_FINGER_GEOMETRY':'NATURAL_FEASIBILITY_UNPROVEN','LEFT_IDLE_FINGER_POSTURE':'UNVERIFIED','HAND_WRIST_POSTURE':'UNVERIFIED_WITH_PRIOR_COLLISION_RISK','STATIC_CONTACT_FEASIBILITY':'NOT_TESTED_REFERENCE_GATE_FAILED','NEXT_MOTION_ENGINE_REQUIREMENTS':'DRAFTED_IMPLEMENTATION_GATE_CLOSED','FINAL_STATUS':'REFERENCE_EVIDENCE_INSUFFICIENT','HAND_BASELINES_UNCHANGED':True,'PIANO_BASELINE_UNCHANGED':True}
dump('FINAL_STATUS_R1.json',{'questions':dict(qa),**status,'STOP':'HUMAN REVIEW','static_candidate_count':0,'new_action_count':0})
body='''# PIANO_HAND_POSTURE_REFERENCE_AND_STATIC_FEASIBILITY_R1

最高原则：HUMAN_VISIBLE_PRODUCT_QUALITY_FIRST。最终状态：**REFERENCE_EVIDENCE_INSUFFICIENT**。

本轮完成实际参考核查、冻结几何测量、旧规划问题分析和自然姿态合同草案；未生成静态候选，未进入动态演奏生成。不是宣称手的几何不可达，也不是自然手型通过。

## 证据结论与静态试验门槛

2 项真实静态照片已查看，另有 2 项官方教学文字。PiaDOOR 左手照片有八度跨度，但内部手指承担额外 E；MusicRadar 右手照片是 C–G 白键。Hoffman 视频遇到登录/机器人验证，只核对了官方文字；Fitch 公开教学文字不能代替实际侧视。缺失的是三闲置指及腕部在交替中的可见关系和含黑键的五指协调，未从透视图编造角度。

依据用户“如果参考和几何检查具备足够证据”的条件，本轮不执行静态摆放。四个目标状态均标 NOT_EXECUTED：L5 D2/L1 D3 准备、L1 D3/L5 D2 准备、R 五指准备、R 代表音触键。审核页第三栏明确显示候选未生成，旧图不冒充新静态结果。

## 几何测量

正式 R2/L1 用 Blender 5.1.2 后台只读重新打开；两手均 3300 顶点、21 骨。重新读取的 neutral 网格与既有 canonical probe 差异 < 0.000001 mm，intrinsic static identity 匹配；没有保存正式 blend。完整数字见 [HAND_KEYBOARD_SPAN_FEASIBILITY_R1.json](HAND_KEYBOARD_SPAN_FEASIBILITY_R1.json)，重新读取证明见 [FORMAL_ASSET_READBACK_R1.json](FORMAL_ASSET_READBACK_R1.json)。

冻结键盘沿用每 native unit = 0.53255794 m 的已批准等效比例；这是项目教学等效尺度，不是厂家标定。坐标 x 低音→高音、y 白键前沿→后方、z 向上；白键静置顶面 z=0。

| 项目 | 测量 | 解释 |
|---|---:|---|
| D2–D3 白键中心水平距 | 167.569 mm | 同深度、静置目标面距离 |
| 两键前部可奏区域最小点距 | 144.480 mm | 内侧边缘，零面积点；不能当作安全 pad 目标 |
| L 静置拇指–小指 pad 空间距 | 153.007 mm | x 投影 145.793 mm，不是最大伸展 |
| L 旧失败候选 pad 距离区间 | 149.929–176.185 mm | 已有轨迹只读统计，未做搜索；不证明自然姿态 |
| L 无关节限位链长上界 | 253.461 mm | 三角不等式松上界，不保证可达、无碰撞或自然 |
| L 掌宽（index–little MCP） | 78.445 mm | 骨头位置间距，不是照片测量 |
| D5–A5 中心水平距 | 95.754 mm | 五指共同掌姿仍待验证 |
| F#5 静置顶面/前端深度 | z=15.444 / y=49.421 mm | 黑键高且靠后，不能套白键同平面 |

手指长度在 JSON 中逐指记录：骨长、关节起点到 pad 的分段折线长度，避免把弯曲指的直线端点距离称为指长。每个目标键的完整前/后可奏矩形保留，无标准尺寸替换。

可用腕高的完整自然区间**未知**。旧 root 实际 z：L 45.000–62.554 mm、R 45.000–57.480 mm；这只是旧候选摆放结果。模型没有完整前臂/肘，俯视照片不能给可信侧视约束，旧数值边界不升级为人体范围。

基本净空：沿用已保存/重开的真实变形网格筛查，L 掌部碰撞观察 129/409，R 10/409，腕部为 0/409。该结果是顶点入键体的粗筛，掌区按静置 y 分段且包含近端拇指；“腕部 0”不等于完整表面无碰撞。每个手的实际 mesh 最低 z 另在 JSON 中，跨键外的最低 z 不能直接解释成键体穿透。

因此回答“当前左手是否能在自然掌腕下完成 D2/D3”：**尚不能确认**。有单点跨度空间和已有接触记录，但没有同时满足自然形态、正确接触、共同掌部与净空的可信见证。不能反向宣称必须放大手或改骨骼。

## 继承与保护

曲目 Musette BWV Anh.126 第 1–2 小节。右手 D5/E5/F#5/G5/A5 → 1/2/3/4/5，左手 D2/D3 → 5/1；继续 DESIGN_PROVISIONAL。没有改 MIDI、Timeline、velocity、NOTE_ON/OFF、88 键映射、下沉规则、采样音源、音频调度、PianoVAM、材质、weights、first-web corrective、rig 或 production pointer。

两张交付证据图仅用上一轮正常教学视角作适度裁切，时间点和哈希见 EVIDENCE_IMAGE_PROVENANCE_R1.json；没有重新渲染或美化。外部照片不嵌入审核页，只给原站链接与图片位置。皮肤真实感仍独立待解决。

## Q1–Q11

'''
body+='\n\n'.join(f'**{q}.** {a}' for q,a in qa)
body+='\n\n## 状态\n\n```text\n'+'\n'.join(f'{k} = {str(v).upper()}' for k,v in status.items())+'\nSTOP — HUMAN REVIEW\n```\n'
body+='\n交付：[review.html](review.html) · [真实参考](REAL_PIANO_REFERENCE_MANIFEST_R1.md) · [姿态合同](NATURAL_PIANO_HAND_POSTURE_CONTRACT_R1.md) · [下一阶段需求](NEXT_MOTION_ENGINE_REQUIREMENTS_R1.md)。不自动进入完整动态演奏。\n'
(P/'PIANO_HAND_POSTURE_REFERENCE_AND_STATIC_FEASIBILITY_R1_REPORT.md').write_text(body,encoding='utf-8')
left='https://piadoor.com/en/piece/2/basic/';leftimg='https://piadoor.com/content/piece/000/02/11_basic/image_left_hand_1_en.png';right='https://cdn.mos.cms.futurecdn.net/N2M4LgaytGt4Vza8r9eFTB.jpg';hoff='https://app.hoffmanacademy.com/lessons/piano/d-major-pentascale/video/'
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>真实手型与几何可行性 · R1</title><style>
:root{color-scheme:dark;font-family:Segoe UI,Microsoft YaHei,sans-serif;color:#f4eee4;background:#101a20}*{box-sizing:border-box}body{margin:0}main{max-width:1340px;margin:auto;padding:36px 28px}h1{font-size:clamp(28px,4vw,46px);margin:14px 0}h2{font-size:25px;margin:0 0 18px}h3{font-size:18px;color:#efbd76}p{line-height:1.75;color:#cbd5da}a{color:#a9d7e4;text-underline-offset:4px}.eyebrow{letter-spacing:.15em;color:#efbd76;font-size:12px}.status{border-left:4px solid #efbd76;background:#293034;padding:16px 22px;margin:24px 0}.status strong{overflow-wrap:anywhere}.numbers{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:26px 0}.number{background:#1a2931;padding:22px;border-radius:12px}.number b{font-size:32px;display:block;margin:8px 0}.number span{color:#aebfc8}.compare{display:grid;grid-template-columns:240px minmax(0,1fr) 230px;gap:20px;align-items:start;margin:22px 0 48px}.card{background:#192831;border:1px solid #30444f;border-radius:12px;padding:18px}.card p{font-size:14px}img{width:100%;height:auto;display:block}.missing{border:1px dashed #a38862;min-height:250px}.label{font-size:12px;color:#aabec8;letter-spacing:.06em}.docs{display:flex;flex-wrap:wrap;gap:12px;margin:24px 0}.docs a{padding:10px 14px;background:#263843;border-radius:8px}details{border-top:1px solid #33434d;padding:18px 0}summary{cursor:pointer;font-size:18px}li{line-height:1.8;margin:8px 0;color:#cbd5da}footer{padding:30px 0;color:#efbd76}section{margin-top:42px}@media(max-width:950px){.compare{grid-template-columns:1fr}.missing{min-height:0}.numbers{grid-template-columns:1fr}main{padding:24px 16px}}
</style><main><div class="eyebrow">PIANO HAND POSTURE / REFERENCE & FEASIBILITY / R1</div><h1>先确认自然手型，再规划触键</h1><p>Musette · BWV Anh.126 · 第 1–2 小节。真实参考、冻结几何与旧版失败姿态的只读审核。</p><div class="status"><strong>REFERENCE_EVIDENCE_INSUFFICIENT</strong><p>已核查 2 份真人静态照片与 2 份教学文字。左手三闲置指与掌腕侧面、右手含 F# 的连续协调证据仍不足。<br>新静态候选 0 份 · 新 Action 0 份 · 正式资产保持不变。</p></div>
<div class="numbers"><div class="number"><span>D2 → D3 / 冻结键中心距</span><b>167.569 <small>mm</small></b><span>自然共同掌姿尚未证明</span></div><div class="number"><span>D5 → A5 / 冻结键中心距</span><b>95.754 <small>mm</small></b><span>F# 顶面高 15.444 mm</span></div><div class="number"><span>左手静置 pad / 空间跨度</span><b>153.007 <small>mm</small></b><span>静置跨度不是最大可达跨度</span></div></div>
<section><h2>01 / 左手八度与中间三指</h2><div class="compare"><div class="card"><div class="label">真实参考 · 已查看照片</div><h3>PiaDOOR · A–E–A</h3><p>左手小指与拇指跨白键八度。照片还包含 E 的额外任务，不能当作三指全闲置标准。</p><p><a href="LEFT" target="_blank" rel="noopener">打开教学原页 ↗</a></p><p><a href="LEFTIMG" target="_blank" rel="noopener">打开真实照片 ↗</a></p><p>位置：Prepare The Left Hand Octave Position 下方 A–E–A 照片。无连续持键/释放、无可靠侧视。</p></div><div><div class="label">现有失败姿态 · 上一轮原图裁切</div><a href="EVIDENCE_LEFT_OCTAVE_POSTURE_R1.png"><img src="EVIDENCE_LEFT_OCTAVE_POSTURE_R1.png" alt="旧左手 D2 与 D3 姿态和本轮测量，明确未生成新候选"></a><p>t=0.850s：D2 / 小指；t=1.150s：D3 / 拇指。旧候选虽已有触键，仍未通过自然性与掌部净空审核。</p></div><div class="card missing"><div class="label">新静态候选</div><h3>未生成</h3><p>关键姿态参考尚未闭合。本栏没有摆放新手型，也不将旧候选改名为静态验证。</p><p>待核查：三指曲度、拇指/小指触点、掌底与腕部侧面关系。</p></div></div></section>
<section><h2>02 / 右手五指与 F# 黑键</h2><div class="compare"><div class="card"><div class="label">真实参考 · 已查看照片</div><h3>Daniel Griffiths · C–G</h3><p>右手白键五指位置。长指弯曲程度不同；这张照片不能证明 F# 的触键姿态。</p><p><a href="RIGHT" target="_blank" rel="noopener">打开作者摄影 ↗</a></p><p>来源：MusicRadar 的 Get your hands comfortable 小节，Right hand on a piano keyboard 图。</p><p><a href="HOFF" target="_blank" rel="noopener">Hoffman · D 大调课程 ↗</a></p><p>仅核对官方文字末段 1–5 指序。视频遇到验证，未观看、无已验证时间点。</p></div><div><div class="label">现有准备与触键 · 上一轮原图裁切</div><a href="EVIDENCE_RIGHT_FIVE_FINGER_POSTURE_R1.png"><img src="EVIDENCE_RIGHT_FIVE_FINGER_POSTURE_R1.png" alt="旧右手准备与 F# 触键画面，不代表新的五指姿态验证"></a><p>t=0.650s：首音前准备；t=1.367s：F#5 / 中指。有限 pad 接触不能证明掌腕自然。</p></div><div class="card missing"><div class="label">新静态候选</div><h3>未生成</h3><p>待核查含黑键的真实五指手型，以及一次代表性触键的共同掌部配置。</p><p>不以白键照片推算黑键关节角度。</p></div></div></section>
<details><summary>几何结论：跨度够不等于自然可达</summary><p>左手旧失败轨迹最大 pad 距为 176.185 mm，但同时存在掌部碰撞。无关节限位的链长松上界为 253.461 mm，只能排除一种简单的“总长度必然不够”判断，不能证明可达。右手还要处理 F# 高差与后移。</p><p>旧 root 腕高 L 45.000–62.554 mm、R 45.000–57.480 mm 不是自然腕高区间。尚无必须改变手比例或骨长的证据。</p></details>
<details><summary>规划根因与下一阶段门槛</summary><p>旧版已有共享掌部和速度/加速度限制。剩余问题包括固定曲度目标、简单闲置指激活耦合、逐时刻接触规划、掌部回拉初始化及仅 12 个掌部净空代理点。</p><p>先补可核查的左手交替和右手黑键五指行为参考，再审核合同并验证唯一四姿态候选。本轮没有实施生成器或新完整演奏。</p></details>
<details><summary>正式资产保护与证据许可</summary><p id="protect">PROTECTIONCOUNT 个既有文件哈希一致；正式 R2/L1 重新只读打开，3300 顶点 / 21 骨及静态身份匹配。MIDI、音频、键盘系统与 production pointers 未修改。</p><p>外部照片版权归来源所有，本页仅原始链接；无外部视频下载、无商业素材授权声明。肤色沿用旧候选，半真实皮肤仍未合格。</p></details>
<div class="docs"><a href="PIANO_HAND_POSTURE_REFERENCE_AND_STATIC_FEASIBILITY_R1_REPORT.md">完整报告 / Q1–Q11</a><a href="REAL_PIANO_REFERENCE_MANIFEST_R1.md">参考来源与许可</a><a href="HAND_KEYBOARD_SPAN_FEASIBILITY_R1.json">几何测量</a><a href="NATURAL_PIANO_HAND_POSTURE_CONTRACT_R1.md">自然姿态合同</a><a href="NEXT_MOTION_ENGINE_REQUIREMENTS_R1.md">下一阶段需求</a><a href="FINAL_ASSET_PROTECTION_R1.json">资产保护</a></div><footer>STOP — HUMAN REVIEW · 不自动进入完整动态演奏生成</footer></main></html>'''
before=read(P/'PROTECTED_INPUTS_BEFORE_R1.json');changed=[]
for p,v in before.items():
 if not Path(p).is_file() or sha(Path(p))!=v:changed.append(p)
assert not changed,changed
protection={'status':'UNCHANGED','checked_file_count':len(before),'changed_files':changed,'baseline_expected_hashes':{'RIGHT_R2':'c946fed318fa88c238d9aacc30cfb4e52f268848f0ad65a4dcbf594754d791f0','LEFT_R1':'54307bb199a75a5e684c29d346de9ca6bf2f8e7696911d9d69c57559516ad1a7','RIGHT_R1_fallback':'4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2'},'before_manifest_sha256':sha(P/'PROTECTED_INPUTS_BEFORE_R1.json'),'formal_readback':read(P/'FORMAL_ASSET_READBACK_R1.json'),'scope':'Inherited full frozen-input protection plus all prior refinement files excluding Python bytecode. Includes previous renders, candidate, key/audio/timeline data and protected production files.','HAND_BASELINES_UNCHANGED':True,'PIANO_BASELINE_UNCHANGED':True,'no_blend_saved_this_phase':True,'new_action_count':0}
for label,digest in protection['baseline_expected_hashes'].items():assert digest in before.values(),label
dump('FINAL_ASSET_PROTECTION_R1.json',protection)
for token,value in [('LEFTIMG',leftimg),('LEFT',left),('RIGHT',right),('HOFF',hoff)]:page=page.replace('href="'+token+'"','href="'+value+'"')
page=page.replace('PROTECTIONCOUNT',str(len(before)))
(P/'review.html').write_text(page,encoding='utf-8')
assert not list(P.glob('*.blend*'))
print('DELIVERED; protected',len(before),'UNCHANGED; static candidates 0; no new Actions')
