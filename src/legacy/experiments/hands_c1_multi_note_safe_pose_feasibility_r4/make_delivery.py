import json,hashlib,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
O=Path(__file__).resolve().parent;ROOT=O.parents[1]
def read(n):return json.loads((O/n).read_text(encoding='utf-8-sig'))
def write(n,t):
 with (O/n).open('x',encoding='utf8') as f:f.write(t)
def save(n,obj):write(n,json.dumps(obj,ensure_ascii=False,indent=2))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
metrics=read('POSE_COMPATIBILITY_METRICS.json');sel=metrics['selected']
snaps={tag:read(n) for tag,n in sel.items()}
labels=read('COMPARISON_LABEL_COORDINATES.json')['rows']
reopened=read('REOPENED_STATIC_VALIDATION.json')
ctx=read('BOUNDARY_R12_READONLY.json')
fontpath='C:/Windows/Fonts/msyh.ttc'
def font(s):return ImageFont.truetype(fontpath,s)
manifest=[]
for kind,filename,box in [('OVERHEAD','SAFE_POSE_COMPARISON.png',(640,105,1005,700)),('SIDE_OBLIQUE','SAFE_POSE_SIDE_COMPARISON.png',(660,170,1245,640))]:
 cw,ch=box[2]-box[0],box[3]-box[1];tilew=cw*2+36;tileh=ch+102
 canvas=Image.new('RGB',(tilew*2+24,tileh*2+94),(20,25,31));draw=ImageDraw.Draw(canvas)
 draw.text((20,12),'R4 四个静态演奏手型 · NOT_APPROVED',font=font(26),fill='white')
 draw.text((20,51),'机器静态通过；连续路径未验证。洋红圈/箭头为真实活动指腹投影。',font=font(18),fill=(210,217,224))
 for ix,(tag,snap) in enumerate(snaps.items()):
  x=(ix%2)*tilew+12;y=(ix//2)*tileh+92
  r=snap['validation'];digit={3:'中指',4:'无名指',5:'小指'}[r['finger']]
  draw.text((x,y),f"{tag}  {r['time']:.2f}s  {digit} → {r['key']}",font=font(23),fill='white')
  name=sel[tag].replace('_POSE.json','')
  for col,(version,raw) in enumerate([('BASE',f'{tag}_BASE_{kind}.png'),('CANDIDATE',f'{name}_{kind}.png')]):
   xx=x+col*(cw+12);yy=y+68
   draw.text((xx,y+35),'原 R2' if col==0 else '静态候选 · 几何 PASS',font=font(19),fill=(200,210,220) if col==0 else (112,232,174))
   im=Image.open(O/raw).convert('RGB').crop(box);canvas.paste(im,(xx,yy))
   point=next(a for a in labels if a['tag']==tag and a['version']==version)['active_pad_pixels'][kind]
   px=xx+point[0]-box[0];py=yy+point[1]-box[1]
   assert xx<=px<=xx+cw and yy<=py<=yy+ch
   draw.ellipse((px-6,py-6,px+6,py+6),outline=(255,70,160),width=3)
   start=(px+30,py+36);end=(px+6,py+8)
   draw.line([start,end],fill=(255,70,160),width=3)
   draw.polygon([(px+6,py+8),(px+7,py+20),(px+17,py+12)],fill=(255,70,160))
   manifest.append(dict(composite=filename,tag=tag,version=version,raw=raw,raw_sha256=sha(O/raw),crop=list(box),active_pad_original_pixels=point))
 canvas.save(O/filename)
save('COMPARISON_MANIFEST.json',dict(rows=manifest,geometry_unretouched=True,crops_identical_for_each_view=True,frozen_original_cameras=True,annotations_only=True))
save('EXCLUDED_RENDER_EVIDENCE.json',dict(files=['R08_ROUND_1_NOT_APPROVED_OVERHEAD.png'],reason='Initial unverified render caused Action reevaluation and failed RENDER_POSE_CHANGED assertion. Preserved as historical failure, excluded from delivery comparisons and all PASS claims.',replacement_prefix='R08_ROUND_1_NOT_APPROVED_VERIFIED',method='Temporary render/frame callbacks reapply exact static snapshot after Action evaluation. render_post mesh digest must equal validated evaluated mesh. Original Action stays assigned and unchanged. Callbacks removed immediately.'))
lines=['# STATIC_POSE_RESULTS','', '**MULTI_POSE_STATIC_PASS_PENDING_HUMAN + POSE_TRANSITION_RISK**','',
 '本轮仅四个指定单帧通过机器静态几何检查；原动画、事件边界及连续路径未修复。全部候选 NOT_APPROVED。', '',
 '|事件/时间|音符/活动指|本轮候选|活动接触合同：横向/垂直间隙 mm|非目标键最大穿入 mm|非法键相交对|全手非相邻自交对|关节越界 °|Human视觉待审|',
 '|---|---|---|---|---:|---:|---:|---:|---|']
for tag,snap in snaps.items():
 r=snap['validation'];p=r['contact'];digit={3:'中指',4:'无名指',5:'小指'}[r['finger']]
 lines.append(f"|{tag} / {r['time']:.2f}s|{r['key']} / {digit}|第{2 if tag=='R08' else 1}轮 PASS|PASS：{p['horizontal_mm']:.3f} / +{p['gap_mm']:.3f}|0|0|0|{r['domain_violation_deg']:.6f}|"+('闲置中指稍抬直，准备C5时需重新弯曲|' if tag=='R08' else '整手位移后教学可辨认性、自然风格待Human确认|'))
lines+=['','## 直接摆姿依据与范围','',
 '- R08：中指 MCP/PIP/DIP 从约 6.712/18.243/14.365° 改为 2/6/3°，展指不变；腕部、小指关节与小指指腹位置均保持。首轮 4/10/6° 仍有 C♯5 1.254481 mm，第二轮清零。没有进行第三轮。',
 '- R09：腕部世界坐标左移5 mm、向演奏者后收6 mm；所有指关节保留原值。活动中指居于 C5 前部白键区，整指原 C♯5 0.849885 mm、D5 1.668604 mm 清零。',
 '- R10：腕部左移8 mm、后收6 mm；闲置中指从约 0.838/9.656/19.555/−18.855° 改为 1/5/6/−5°，解除向无名指方向侧摆；活动无名指关节不改。原 D♯5 3.267743 mm、E5 3.691368 mm 清零。',
 '- R11：腕部右移6 mm、后收9 mm；所有指关节保留原值。中指落在 E5 前部白键区；原 C♯5 2.111721 mm、D5 2.031685 mm、D♯5 1.313478 mm 清零。',
 '', '## 验收含义', '',
 '每次用原Action驱动的真实琴键与evaluated全右手皮肤，复用既有 BVH 零epsilon、非相邻三角面相交及三角面进入键体的最大深度检测。全部键体进行 broadphase，非目标键要求相交0、内部深度0；未放宽历史标准。检查全部非相邻右手三角面，四候选的绝对自交均0，不仅是新增自交0。跨手相交0、相对原始左手网格位移0；Rig/rest/皮肤/权重/corrective及全部Action语义摘要保持。四候选全部关节越界实际读数0。',
 '', '活动触键仍采用冻结合同：指腹在目标键可奏面，横向≤0.03 mm，垂直绝对间隙≤3 mm。表中的正间隙如实保留，不称为零距离物理接触。除指腹外，对整指/全手同时检查邻键；目标键相交三角形均属于正确活动手指，闲置指没有触入目标键。重开起点后重放每个快照，完整evaluated网格摘要逐一一致。详见 REOPENED_STATIC_VALIDATION.json（含活动末节全皮肤边界与目标键相交分类）。',
 '', '## 视觉与复现', '',
 '已查看正式正交俯视和侧视：R10原中指向无名指跨越的投影在3.67s候选中分开；四个代表帧没有明显新增折断、极端展指或交叉。R08中指更直、更高，是否符合原C1教学风格须Human审阅；历史网格轮廓/掌部体块缺陷未修改，也不计为本轮新增动作缺陷。二维遮挡与真实相交分别记录。',
 '', 'SAFE_POSE_COMPARISON.png 使用原正式正交相机；SAFE_POSE_SIDE_COMPARISON.png 使用原 SIDE_OBLIQUE 辅助相机。两图均为实际渲染的同范围裁切与标注，无几何修图；洋红标记是相机投影的真实活动指腹点。原完整渲染及 COMPARISON_MANIFEST.json 保留。',
 '', '交付为可复现 Pose Bone JSON 快照，原 Action 始终保留，无新Action、关键帧、动画静音或隐藏。用 Blender 打开 R2_START_ISOLATED_NOT_APPROVED.blend 后，按精确时间 frame_set，再应用快照。replay_static.py 提供复现脚本；切换时间会恢复原动画，这些快照不是修复动画Blend。session.py/render 的临时回调仅为防止渲染初始化覆盖静态Pose，渲染后立即移除，并用render_post evaluated网格SHA校验；首次失败渲染另存排除说明，未删除。',
 '', '每帧从各自原R2姿态开始。尝试数 R08=2、R09=1、R10=1、R11=1；无角度网格/随机搜索、IK、求解器或插值。', '', '**STOP — HUMAN REVIEW**。']
write('STATIC_POSE_RESULTS.md','\n'.join(lines)+'\n')
lines=['# POSE_COMPATIBILITY_REPORT','', '**POSE_TRANSITION_RISK**。静态四帧有连接研究价值，未证明安全连续路径。','',
 '|两端姿态|代表帧时间差 s|腕位差 mm|腕朝向差 °|最大单关节差 °|距离/时间 mm/s（非实测速度）|', '|---|---:|---:|---:|---:|---:|']
for p in metrics['pairs']:
 lines.append(f"|{p['from_tag']} → {p['to_tag']}|{p['dt_seconds']:.6f}|{p['wrist_distance_mm']:.3f}|{p['wrist_orientation_difference_deg']:.3f}|{p['max_abs_joint_difference_deg']:.3f}|{p['average_wrist_distance_over_time_mm_s']:.3f}|")
lines+=['', '腕差为世界位置和朝向；各手指 MCP/PIP/DIP/展指逐项差见 POSE_COMPATIBILITY_METRICS.json。表中距离/时间仅为代表帧端点比值，既不是轨迹速度验收，也没有把完整时间差全部视为自由移动时间。', '',
 '## 原时钟与活动指不能提前释放', '',
 'R08小指E5必须持到3.349997s，中指在该时刻接C5；R09中指必须持到3.5642825s，随后无名指D5；无名指持到3.778568s，中指接E5；中指E5持到3.9928535s，无名指接F♯5。中指/无名指180ms准备、40ms释放仅复用既有角色说明，不形成碰撞豁免。四个单帧没有提前释放活动指，但没有验证从它们出发能否持续保持触键至OFF。', '',
 '- R2 2.92s → R08：2.92s仍为拇指G4，约1.426ms后转小指E5。至3.12s腕差18.102mm/7.373°只说明两个端点；不能用0.20s平均值推定极短起音交接安全。原安全终态保留，R08起音未编辑。',
 '- R08 → R09：腕差20.240mm，小指持E5期间中指从较直闲置姿态弯下准备C5。需协调腕位并保持小指落键，不能把所有位移安排在松键之后；尚未证明可行。',
 '- R09 → R10：腕差11.824mm；中指释放与无名指落D5必须同时处理。R10闲置中指撤回向右侧摆，有利于解除交叉，但与中指前一事件持键的运动衔接尚未验证。',
 '- R10 → R11：腕差41.572mm，0.21s代表帧差对应197.962mm/s端点比值；中指最大单关节差22.528°。这是本轮最明显的连接风险，特别是无名指在3.778568s前必须保持D5。需要重新分配相邻腕位/手指准备，不能直接线性插值或提前离键。',
 '- R11 → 原R12起音：至3.9928535s仅112.854ms，腕差19.706mm，端点比值174.616mm/s；中指仍须持续E5，无名指准备后方黑键F♯5。不能直接吸附回原R12姿态。',
 '', '## 边界与R12的限制','',
 '2.921426、3.349997、3.5642825、3.708333333、3.778568s附近只读复用R3真实几何证据（BOUNDARY_R12_READONLY.json）。原3.778568s仍有95对中指/无名指相交，3.80s147对的历史FAIL保留。新3.67和3.88帧自交0不能证明3.78s边界已修复。未把静态快照搬到边界另做第三组摆姿。', '',
 'R12为无名指F♯5，3.9928535–4.207139s；本轮只读检查起音前1/960s、精确起音、后1/960s及R12持音中点，记录真实原始姿态与全手几何，不修改R12。结果：']
for r in ctx['fresh_original_R2_rows']:
 if r['tag']=='R2_SAFE_START':continue
 illegal=', '.join(f"{k} {v['depth_mm']:.6f}mm/{v['pairs']}对" for k,v in r['illegal'].items()) or '无'
 lines.append(f"- {r['tag']}，{r['time']:.9f}s，活动{r['event']['note_id']} {r['key']} 指{r['finger']}：接触合同{'PASS' if r['contact']['pass_'] else 'FAIL'}；非法键 {illegal}；自交{r['self_count']}对。")
lines+=['', '因此3.9928535s不是已完成安全闭合点。即使R12活动触点合格，整指邻键问题仍须保留。下一轮若获授权，应先解决R10→R11及R11→R12的持键/准备与边界约束，再做有限连续验证；本轮没有制作任何关键帧、插值或动态避障证明。', '', '**STOP — HUMAN REVIEW**。']
write('POSE_COMPATIBILITY_REPORT.md','\n'.join(lines)+'\n')
write('HUMAN_REVIEW.md','''# HUMAN_REVIEW

**MULTI_POSE_STATIC_PASS_PENDING_HUMAN + POSE_TRANSITION_RISK**

1. **四个连续音符分别有本轮找到的安全静态手型吗？** 有：R08 3.12s小指E5、R09 3.45s中指C5、R10 3.67s无名指D5、R11 3.88s中指E5。四个候选分别通过冻结活动接触合同、全手非目标键相交/内部深度0、全手非相邻自交0、关节越界0；跨手碰撞0，左手不变。全部NOT_APPROVED，待Human视觉审核。

2. **3.12s C♯5严重侵入能否在保持小指E5时消除？** 本轮可以。原4.227605mm→首轮1.254481mm→第二轮0；仅调整闲置中指，小指Pose及实际触点不动，活动触键合同保持PASS。

3. **中指C5、无名指D5、中指E5能否分别避免邻键穿模？** 三个代表帧均已做到，非法键相交/深度均0。腕部有5–9mm单轴调整；R10额外撤回并抬起闲置中指。活动手指始终在正确目标键可奏区，未更改音符、指法、时钟或键Action。

4. **3.78s附近中指与无名指真实相交是否已消除？** 尚不能认定。R10 3.67s与R11 3.88s候选均为全手真实自交0，R10俯视跨越姿态已解除，说明相邻事件存在分离静态手型。但3.778568s只读原边界仍有95对相交，3.80s历史147对仍保留；本轮没有编辑/验证该边界的新姿态，更没有验证经过边界的连续路径。

5. **安全姿态可能保持原C1自然风格吗？** 四帧仍沿用原腕朝向和活动指关节；主要是毫米级掌位调整及闲置中指抬起/撤回，未见新增极端折弯或展指，具有保留原风格的可能。R08中指更直更高，及相邻姿态约41.572mm腕位变化是否自然，需要Human与后续运动验证，不能凭单帧宣布自然度通过。原基础网格外观缺陷保持。

6. **值得进入下一轮连续关键帧实验吗？** 有足够静态可行性证据，值得在Human审图后开展限定范围的连续验证；没有足够证据直接批准动画或安全闭合。最需先解决R10→R11持键/移腕和R11→R12无名指F♯5准备。R12原始姿态仍有非法邻键关系，本轮未修改，3.9928535s不得作为闭合点。

建议先看 SAFE_POSE_COMPARISON.png 与 SAFE_POSE_SIDE_COMPARISON.png，再核对 STATIC_POSE_RESULTS.md、POSE_COMPATIBILITY_REPORT.md。四个选中快照见 RESULT.json；原样起点及失败首轮/失败渲染证据都保留。

正式C1、R2/R3原成果、MIDI/指法/23音时间、Rig/rest/蒙皮/corrective、左手和全部已有Action未修改。未创建新Action、连续关键帧、修复R12、合并B01失败候选或扩展到23音；未访问/扫描独立piano目录。保护收据见 PROTECTED_INPUTS_SHA256_BEFORE_AFTER.json。全部研发输出位于本轮hands隔离目录。

**STOP — HUMAN REVIEW**
''')
save('RESULT.json',dict(task='HANDS_C1_MULTI_NOTE_SAFE_POSE_FEASIBILITY_R4',static_status='MULTI_POSE_STATIC_PASS_PENDING_HUMAN',transition_status='POSE_TRANSITION_RISK',selected=sel,static_pass_count=4,attempts=dict(R08=2,R09=1,R10=1,R11=1),all_not_approved=True,boundary_3_78_repaired=False,R12_modified=False,safe_closure_3_9928535=False,continuous_animation_created=False,actions_modified=False,stop='STOP — HUMAN REVIEW'))
# All actual prior protected inputs and every runtime-read dependency, no scan.
before=read('PROTECTED_BEFORE.json')['files']
runtime=read('RUNTIME_READ_INPUT_RECEIPT.json')['files']
paths={r['path']:r['sha256'] for r in before}
paths.update({r['path']:r['before'] for r in runtime})
receipt=[]
for path,h in paths.items():
 p=Path(path);assert p.is_relative_to(ROOT)
 a=sha(p);receipt.append(dict(path=path,before=h,after=a,unchanged=a==h))
assert all(r['unchanged'] for r in receipt)
save('PROTECTED_INPUTS_SHA256_BEFORE_AFTER.json',dict(all_unchanged=True,count=len(receipt),files=receipt,piano_directory_accessed=False,no_recursive_scan=True,path_migration=False,source_copy_byte_identical=sha(O/'R2_START_ISOLATED_NOT_APPROVED.blend')==sha(ROOT/'experiments/hands_c1_exit_handoff_correction_r2/EXIT_CORRECTED_NOT_APPROVED.blend')))
print('DELIVERY_WRITTEN',len(receipt),'protected inputs unchanged')
