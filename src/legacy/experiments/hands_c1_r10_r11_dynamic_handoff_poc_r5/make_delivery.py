import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
O=Path(__file__).resolve().parent;ROOT=O.parents[1]
def read(p):return json.loads((O/p).read_text(encoding='utf-8-sig'))
def write(p,t):
 with (O/p).open('x',encoding='utf8') as f:f.write(t)
def save(p,d):write(p,json.dumps(d,ensure_ascii=False,indent=2))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
ds=[read(f'CANDIDATE_{n}_VALIDATION.json') for n in [1,2]];ss=[d['summary'] for d in ds]
base=read('BASELINE_CONTEXT_GEOMETRY.json');core=[r for r in base['rows'] if 3.5642825-1e-10<=r['time']<3.9928535-1e-10]
pairaudit=read('ABSOLUTE_AND_NEW_SELF_PAIR_AUDIT.json')['rows'];exterior=read('EXTERIOR_AND_EARLIER_R2_STRICT_AUDIT.json')['rows']
assert all(not s['machine_pass'] for s in ss)
assert sha(O/'R10_R11_DYNAMIC_NOT_APPROVED.blend')==sha(O/'CANDIDATE_1_NOT_APPROVED.blend')
# Minimum failure evidence, same frozen-camera crops; no retouching.
canvas=Image.new('RGB',(1800,1115),(20,25,31));draw=ImageDraw.Draw(canvas)
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',n)
draw.text((18,12),'R5 · 3.778568s 换指失败证据 · TRANSITION_BLOCKED',font=font(27),fill='white')
draw.text((18,54),'真实Action动画；全手evaluated mesh验收失败。两候选均NOT_APPROVED。',font=font(19),fill=(222,228,235))
columns=[('原 R2 · 中/无名指相交95对','R2_ORIGINAL_HANDOFF'),('候选1 · 相交57对，邻键0','CANDIDATE_1_HANDOFF'),('候选2 · 相交155对，D5/F5侵入','CANDIDATE_2_HANDOFF')]
sources=[]
for col,(title,prefix) in enumerate(columns):
 x=col*600+10;draw.text((x,94),title,font=font(21),fill=(255,165,155) if col else (215,222,230))
 for row,(kind,box) in enumerate([('OVERHEAD',(650,120,1000,660)),('SIDE_OBLIQUE',(660,170,1245,640))]):
  p=O/f'{prefix}_{kind}.png';im=Image.open(p).convert('RGB').crop(box)
  if row==0:im=im.resize((350,540));xx=x+110;yy=135
  else:im=im.resize((585,470));xx=x;yy=690
  # Side image is reduced uniformly to fit the evidence sheet.
  if row==1:im.thumbnail((585,395))
  canvas.paste(im,(xx,yy));sources.append(dict(file=p.name,sha256=sha(p),crop=box))
canvas.save(O/'HANDOFF_FAILURE_COMPARISON.png')
save('VISUAL_EVIDENCE_MANIFEST.json',dict(sources=sources,geometry_unretouched=True,annotations_and_uniform_layout_only=True,frames_are_exact_handoff=True,videos_generated=False,reason='Both real animation candidates failed dense machine validation; per task cost/stop rule retain minimum still evidence instead of full-video rendering.'))
lines=['# HANDS_C1_R10_R11_DYNAMIC_HANDOFF_POC_R5','', '**TRANSITION_BLOCKED — STOP — HUMAN REVIEW**','',
 '已通过Blender MCP在R2隔离副本内直接制作两个真实关键帧动画候选；两者均失败。局部邻键清障改善不构成安全换指。没有修改冻结输入，未将失败动画合入C1/R2/R3/R4。', '',
 '## R4参考与41.572mm核查','',
 'R4 R10 3.67s腕原点世界位置约(149.971798, −141.877279, 26.358634)mm；R11 3.88s约(190.790385, −139.144361, 33.748124)mm。精确矩阵见 R4_WORLD_TRANSFORM_RECHECK.json。差向量约(+40.818588, +2.732918, +7.389490)mm，长度41.571995mm。定义是 rig.matrix_world @ WRIST_R.matrix 的平移列：前者含原手位动画，PoseBone.matrix是骨局部到Armature对象空间；matrix_basis是rest/parent相关的局部Pose，不可把局部location差当世界位移。',
 '', 'R4两姿态是NOT_APPROVED几何参考，已重新核验两帧触点、全手键体和自交，不作为必须经过的模板。本轮新作中间姿态；没有预设41.572mm必须执行，也没有复制R4快照生成整段。', '',
 '## 编辑骨骼、时钟和曲线','',
 '精确核心 R10=[3.5642825,3.778568)s、R11=[3.778568,3.9928535)s；R12无名指F♯5从3.9928535s开始，冻结事件表不改。上下文3.35–4.08s。两候选拟定编辑支撑均为[3.5642825,3.9928535]，端点写入原值，未扩展主动修复R09、R12正式演奏段。实测仍发现边界外泄漏，见下文，不能据拟定支撑宣称实际完全不变。',
 '', '修改 WRIST_R.location，以及 INDEX/MIDDLE/RING 的 MCP/PIP/DIP rotation_quaternion，共39条标量FCurve（3+9×4）。腕朝向、Rig对象手位动画、拇指/小指曲线、琴键Action、左手Action均未主动编辑。皮肤、Rig/rest、权重、corrective摘要不变。两候选各使用原Action的副本，不修改冻结输入文件。',
 '', '约11个直接指定的协调姿态，在起音/交接及3.60、3.67、3.708333、3.74、3.80、3.84、3.88、3.94秒设置Pose关键帧；精确Pose和曲线范围保留于两个 EDIT_LEDGER.json。关节角由人工指定，活动指目标点由一次实测指腹到声明可奏区域的刚性掌位平移直接放置，无迭代求解、IK、随机/网格搜索或大型运动规划器。实际动画为四元数/位置三次Bezier，内部控制柄平坦，直接求值后再验真实网格；不是静态回调或换帧假动画。',
 '', '- 候选1：沿用R4的分离准备思路，逐渐将无名指放到D5前部、中指抬起后弯下接E5，再释放无名指。活动点D5/E5约在键前部中间，避免原邻键边缘。',
 '- 候选2：根据候选1真实交叉图，改用无名指PIP主屈、中指MCP主屈的相反上下分层，D5落点更靠前，无名指在OFF后更早伸展释放。它仍然失败，没有第三次艺术参数修正。候选2的一个前期交接设计Pose也保留，不能将该Pose当作额外通过的第三候选。',
 '', '## 真实连续过程验收','',
 '268个3.35–4.08s上下文样本，189个R10/R11核心样本。240Hz基础，在3.69–3.73s历史相交区及交接前25ms/后40ms加密960Hz；精确A/H/B边界与±1/960、±1/3840s均检查。完整evaluated右手皮肤、Action驱动的实际键体网格、零epsilon BVH及既有三角面进入键体深度检测；全部右手非相邻三角面、左右手和活动触点复核。离散样本失败即可否决；没有据此证明数学无解或连续时间完备认证。', '',
 '|指标|原R2|候选1|候选2|','|---|---:|---:|---:|',
 f"|核心非法邻键样本 /189|{sum(bool(r['illegal']) for r in core)}|{ss[0]['core_illegal_samples']}|{ss[1]['core_illegal_samples']}|",
 f"|核心真实指间相交样本 /189|{sum(r['self_count']>0 for r in core)}|{ss[0]['core_self_samples']}|{ss[1]['core_self_samples']}|",
 f"|核心自交峰值（面片对）|{max(r['self_count'] for r in core)}|{ss[0]['core_self_peak']}|{ss[1]['core_self_peak']}|",
 '|精确3.778568s中/无名指相交对|95|57|155|',
 '|右手规定触点PASS /48|48|48|48|',
 '|核心活动触点失败样本|0|0|0|',
 f"|实际新增相交对出现的上下文样本|—|{pairaudit[0]['new_pair_samples']}|{pairaudit[1]['new_pair_samples']}|",
 f"|新增跨手碰撞样本|—|{ss[0]['new_cross_samples']}|{ss[1]['new_cross_samples']}|",
 '|左手实际网格最大位移 mm|—|0|0|',
 f"|3.67→3.88s腕部世界位差 mm|—|{ss[0]['representative_wrist_distance_mm']:.6f}|{ss[1]['representative_wrist_distance_mm']:.6f}|",
 f"|上下文腕部速度峰值 mm/s|—|{ss[0]['max_actual_wrist_speed_mm_s']:.3f}|{ss[1]['max_actual_wrist_speed_mm_s']:.3f}|",
 f"|上下文皮肤速度峰值 mm/s|—|{ss[0]['max_actual_skin_speed_mm_s']:.3f}|{ss[1]['max_actual_skin_speed_mm_s']:.3f}|",
 f"|新增关节速度峰值 °/s|—|{ss[0]['max_added_joint_speed_deg_s']:.3f}|{ss[1]['max_added_joint_speed_deg_s']:.3f}|",
 '', '精确交接候选1邻键相交0，但仍有57对两指相交；候选2交接有D5约0.367370mm、F5约0.868085mm的非法侵入及155对相交。整窗两者仍有黑键加深，不能把候选1交接单帧邻键0作为全程PASS。两候选末端3.991811833s均仍有D5约2.368mm侵入。',
 '', '全部规定触点和密集活动触点PASS只说明冻结接触合同成立：指腹在可奏面，横向≤0.03mm、垂直绝对间隙≤3mm。它没有排除整指非法键体相交或提前按键。R11中指在正式ON前准备区有18/22个样本已与E5实际表面相交，说明原事件表虽未动，演奏时序语义仍未完全保持。R12准备区无名指与F♯5表面相交样本均0，但准备轨迹确已变化。',
 '', '自交差分另对真实三角形ID集合逐样本计算，见 ABSOLUTE_AND_NEW_SELF_PAIR_AUDIT.json；两候选实际新增相交对样本分别85、103。初始VALIDATION.summary.new_self_samples只是相交数量净增加的31/79，不能作真实新增面片对结论；以此补充审计为准。没有把“比原R2少”当作绝对0。',
 '', '## 关节、速度、自然度和边界回退','',
 '核心最大域读数均为原R2精确交接处继承的拇指−3.5873719e−7°浮点下界读数；没有显著新增域越界。未放宽冻结关节范围或碰撞阈值。实际Bezier求值及关键帧两侧±10µs检查未检出位置突跳：最大皮肤单侧位差约0.004412mm；但不能据C0位置连续认定动作自然。新增关节速度521.107/1046.669°/s，超过既有新增180°/s约束；快速侧移、抬落及教学俯视交叉不合格。原风格没有获得本轮通过。',
 '', '腕部代表帧差仅从41.571995mm缩至37.330822/39.383335mm，不是大幅压缩，也不证明这些幅度必需；实际轨迹在更短局部时间内有905–1020mm/s腕速峰值。两个候选都不足以支持“必须移动相近幅度”或“已自然缩短”的结论。',
 '', 'R09/R12原有不安全关系保留为开放边界，没有把3.35–4.08s宣称全段安全；核心本身也失败，故不能使用 LOCAL_TRANSITION_MACHINE_PASS_OPEN_BOUNDARY。精确R12触点均PASS，但实际边界外网格相对原R2最多约0.042092/0.042046mm差异，不能声称R12正式动作绝对无影响。',
 '', 'R2 2.45–2.92s另以225个原时刻复核：候选1/2最大网格差0.000611277/0.000634657mm，无名指早段关键帧控制柄payload也有变化。8个外部查询时刻的标量FCurve求值误差读数0，但不足以替代全网格和控制柄完全一致要求；严格一致检查FAIL，不能宣称此前成果在候选内部完全保持。输入R2文件本身SHA256未变。此微小非零差异及0.042mm边界泄漏均作为实现/重存保护失败保留，没有以容差改判PASS。',
 '', '以上是失败候选中的越界影响，未写回任何冻结成果。两个艺术候选已用完，不通过再次构建、恢复控制柄或改曲线暗中增加第三次尝试。',
 '', '## 交付与停止','',
 'R10_R11_DYNAMIC_NOT_APPROVED.blend 是候选1的字节相同分析副本，**FAILED / NOT_APPROVED**，不是获准动画；候选2原文件同时保留。两者都含真实可播放FCurve动画。通过重新打开Blend进行全部密集验收，不依赖运行时静态Pose回调。',
 '', '保留 HANDOFF_FAILURE_COMPARISON.png 和两候选交接/释放必要原始静帧；机器失败后按成本限制未制作 R10_R11_OVERHEAD_1X.mp4、R10_R11_OVERHEAD_0_5X.mp4、R10_R11_SIDE_1X.mp4，不创建空白或冒充成功的视频。',
 '', '冻结原C1、R2/R3/R4、MIDI/指法/23音时钟、Rig/蒙皮/corrective、琴键及左手Action全部文件哈希保持；仅复制起点及必要参考，未访问或递归扫描独立piano目录。保护收据为 PROTECTED_INPUTS_SHA256_BEFORE_AFTER.json。历史失败、首次曲线构建错误日志和两个候选都保留。',
 '', '**TRANSITION_BLOCKED — STOP — HUMAN REVIEW**。限定尝试失败，不代表现有Rig/指法/时钟下数学上无解。']
write('TECHNICAL_REPORT.md','\n'.join(lines)+'\n')
write('HUMAN_REVIEW.md','''# HUMAN_REVIEW

**TRANSITION_BLOCKED — STOP — HUMAN REVIEW**

1. **是否真实消除了3.778568s附近中指/无名指相交？** 没有。精确交接原95对，候选1为57对，候选2为155对；整个核心仍有85/103个相交样本，且出现新的真实面片对相交。两候选均不能交付为安全动画。

2. **R10→R11全过程是否无非法邻键碰撞？** 否。189个核心样本中，候选1有37个、候选2有56个存在非法键关系；不能用个别帧清障替代全程通过。候选2还将局部碰撞带到F5。

3. **两个活动手指触键和时序是否保持？** 冻结音符、指法、时钟未改，48/48规定触点及核心密集活动触点均PASS；但中指在R11起音前有18/22个样本真实提前触及E5，演奏时序语义未完整保持，不能仅凭pad PASS判定正确。

4. **41.572mm腕位差是否缩小？** 两个代表帧差分别约37.331/39.383mm，略有缩小，未找到显著缩短且安全的连接。局部腕速峰值约1020/905mm/s，动作仍急促。没有证明必须执行41.572mm或相近位移。

5. **R12准备是否受到影响？** 受到影响：无名指准备路径改变。两候选R12正式起音触点仍PASS，未检出F♯5提前表面相交，但边界外出现最多约0.042mm全手网格差异，不能认定R12完全不受影响。未扩展修复R12，原有邻键问题仍开放。

6. **是否取得真正连续、安全的换指动画？** 没有。已经做出两个真实连续关键帧实验，但相交、邻键、提前触键、速度及严格窗口保护均存在失败，不能进入批准或合并。

先看 HANDOFF_FAILURE_COMPARISON.png。打开 R10_R11_DYNAMIC_NOT_APPROVED.blend 可回放候选1（失败分析副本），不要将其替换正式C1。关键时刻：3.60–3.708s部分清障；3.726s之后候选1开始两指相交；3.778568s看交接交叉；3.80s看释放粘连；3.88s虽单帧清晰，不代表前后安全；3.94–3.9928535s看高速回接和邻键再侵入。候选2约3.70s开始相交，3.84s已分离，但交接本身仍失败。

机器失败后未渲染三段完整对照视频，仅保存必要真实静帧。候选1/2没有隐藏原动画或静态Pose回调；原Action被复制后直接编辑关键帧。两个候选均NOT_APPROVED，所有失败和日志保留。冻结输入SHA256不变；失败候选内的R2早段严格一致检查FAIL也如实保留，详见TECHNICAL_REPORT.md。

**STOP — HUMAN REVIEW**
''')
save('RESULT.json',dict(task='HANDS_C1_R10_R11_DYNAMIC_HANDOFF_POC_R5',status='TRANSITION_BLOCKED',local_improvement_only=True,animation_candidates_created=2,selected_analysis_candidate=1,selected_blend='R10_R11_DYNAMIC_NOT_APPROVED.blend',selected_is_failed=True,approved=False,core_machine_pass=False,video_rendered=False,stop='STOP — HUMAN REVIEW',mathematical_impossibility_proven=False,strict_R2_earlier_preservation_pass=False,exact_R12_no_effect_claim=False))
paths={r['path']:r['sha256'] for r in read('PROTECTED_BEFORE.json')['files']}
for receipt in ['VALIDATION_INPUT_RECEIPT.json','FINAL_AUDIT_INPUT_RECEIPT.json','FINAL_SESSION_INPUT_RECEIPT.json']:
 for r in read(receipt)['files']:paths.setdefault(r['path'],r['before'])
rows=[]
for name,h in paths.items():
 p=Path(name);assert p.is_relative_to(ROOT);a=sha(p);rows.append(dict(path=name,before=h,after=a,unchanged=h==a))
assert all(r['unchanged'] for r in rows)
save('PROTECTED_INPUTS_SHA256_BEFORE_AFTER.json',dict(all_unchanged=True,count=len(rows),files=rows,piano_access=False,no_recursive_external_scan=True,path_migration=False,R2_start_byte_identical=sha(O/'R2_START_ISOLATED_NOT_APPROVED.blend')==sha(ROOT/'experiments/hands_c1_exit_handoff_correction_r2/EXIT_CORRECTED_NOT_APPROVED.blend'),note='This receipt protects original input files. It does not turn failed earlier-window/candidate-boundary preservation checks into PASS.'))
print('R5_FAILED_EXPERIMENT_DELIVERED',len(rows),'protected original inputs unchanged')
