from bounded_static import *
from PIL import Image,ImageDraw,ImageFont
import hashlib,html
def filehash(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def doc(n,s):(P/n).write_text(s.strip()+'\n',encoding='utf8')
a=read(P/'ACTUAL_STATIC_COMPARISON.json');assert a['complete'];rows=a['poses'];result=read(P/'BOUNDED_STATIC_RESULTS.json');policy=read(P/'STRATEGY_LOCK.json');evidence=read(P/'ROOT_RANGE_EVIDENCE.json')
for n,h in policy['script_sha256'].items():assert sha(P/n)==h
parity=[]
for i,r in enumerate(result['poses']):
 ctx=Bounded(r['video_sec']);ctx.root_delta=np.array(r['root_delta']);pred=ctx.skin(np.array(r['delta_deg']))[0];actual=np.load(P/f'{i+4:02d}_actual_skin.npz')['V'];parity.append(dict(video_sec=r['video_sec'],max_mm=float(np.linalg.norm(pred-actual,axis=1).max()*1000)))
assert max(r['max_mm'] for r in parity)<.03,parity
dump('BOUNDED_ACTUAL_SKIN_PARITY.json',parity)
protected=read(P/'PROTECTED_INPUTS_BEFORE.json');changed=[p for p,h in protected.items() if not Path(p).is_file() or filehash(p)!=h];assert not changed,changed
static=read(ROOT/'audits/minuet_stage_c_r2_local_finger_overlap_refinement/PROTECTED_INPUTS_BEFORE.json');static={p:h for p,h in static.items() if 'piano_hand_static_posture_clearance_refinement_r2' in p and Path(p).suffix in ['.blend','.json'] and Path(p).is_file()};assert all(filehash(p)==h for p,h in static.items())
assert not list(P.glob('*.blend')) and not list(P.glob('*.mp4'))
dump('ASSET_PRESERVATION.json',dict(protected_files=len(protected),changed=changed,approved_static_related_files=len(static),static_changed=0,source_baseline=M['baseline']['sha256'],new_actions=0,new_blends=0,new_videos=0,new_dynamic_solves=0,new_dynamic_candidates=0,policy_hashes_unchanged=True))
def pair(r):return r['pairs'][1]
def depth(r):return max([x['max_depth_mm'] for x in pair(r)['penetration']]+[0])
def black(r):
 hits=[h for h in r['black'] if h['digit']=='MIDDLE' and h['midi']==75]
 return '无命中' if not hits else f"{hits[0]['triangle_pairs']} 面对 / {hits[0]['inside_vertices']} 内部顶点 / {hits[0]['depth_mm']:.4f} mm"
def compact_table():
 s='| 条件 / 演示秒 | 中—无名指面片对 | 最大内部顶点→实际对指皮肤距离 mm | 中指 D♯5 | 活动触键间隙 / 横向越界 mm |\n|---|---:|---:|---|---|\n'
 for r in rows:
  ct=r['contacts'][0];s+=f"| {r['label']} / {r['video_sec']:.3f} | {pair(r)['face_pairs']} | {depth(r):.4f} | {black(r)} | {ct['note']} {ct['skin']['gap_mm']:.4f} / {ct['skin']['horizontal_mm']:.4f} |\n"
 return s
table=compact_table();center=rows[5];fixedrow=rows[3];source=rows[1];center_fit=result['poses'][1]
root_table='| 演示秒 | ΔX mm | ΔY mm | ΔZ mm | pitch° | yaw° | nfev / 终止 |\n|---|---:|---:|---:|---:|---:|---|\n'
for r in result['poses']:root_table+=f"| {r['video_sec']} | "+' | '.join(f'{x:.4f}' for x in r['root_delta'])+f" | {r['nfev']} / {r['message']} |\n"
joint_table='| 条件 / 手指 | MCP 屈伸° | PIP° | DIP° | MCP 横展° |\n|---|---:|---:|---:|---:|\n'
for label,angles in [('R1',original_degrees([3.825])[0]),('A',read(R4/'STATIC_PREFLIGHT.json')['poses'][7]['actual_degrees']),('B',center_fit['actual_degrees'])]:
 for digit,values in zip(DIGITS,angles):joint_table+=f'| {label} / {digit} | '+' | '.join(f'{x:.4f}' for x in values)+' |\n'
# Static collages: same full source camera pixels in every row, with identically
# cropped right-hand detail presented separately. Never hide a conflict by camera changes.
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
views=['TEACHING','OVERHEAD','SIDE_OBLIQUE']
def sheet(name,ids,labels,crop=False):
 w,h=(480,350) if crop else (640,360);canvas=Image.new('RGB',(w*3,(h+42)*len(ids)),(24,29,35));draw=ImageDraw.Draw(canvas)
 for rr,(i,label) in enumerate(zip(ids,labels)):
  for cc,view in enumerate(views):
   im=Image.open(P/'static_frames'/f'{i:02d}_{view}.png').convert('RGB')
   im=im.crop((610,95,1090,445)) if crop else im.resize((w,h))
   canvas.paste(im,(cc*w,rr*(h+42)+42));draw.text((cc*w+10,rr*(h+42)+10),f'{label} | {view}',font=font,fill='white')
 canvas.save(P/name,quality=95)
sheet('DECISIVE_FULL_THREE_VIEW.jpg',[1,3,5],['R1 ORIGINAL 3.825s','A FIXED ROOT (R4)','B BOUNDED ROOT'])
sheet('DECISIVE_DETAIL_THREE_VIEW.jpg',[1,3,5],['R1 ORIGINAL 3.825s','A FIXED ROOT (R4)','B BOUNDED ROOT'],True)
sheet('BEFORE_NEIGHBOR_DETAIL.jpg',[0,4],['R1 ORIGINAL 3.750s','B BOUNDED ROOT'],True)
sheet('AFTER_NEIGHBOR_DETAIL.jpg',[2,6],['R1 ORIGINAL 3.850s','B BOUNDED ROOT'],True)
neighbor=[]
for x,y in zip(result['poses'],result['poses'][1:]):
 dt=y['video_sec']-x['video_sec'];dx=np.array(y['root_delta'])-np.array(x['root_delta']);dq=np.array(y['delta_deg'])-np.array(x['delta_deg']);neighbor.append(dict(from_sec=x['video_sec'],to_sec=y['video_sec'],delta_root_parameters=dx,translation_difference_mm=float(np.linalg.norm(dx[:3])),rotation_vector_difference_deg=float(np.linalg.norm(dx[3:])),max_joint_increment_difference_deg=float(abs(dq).max()),meaning='Differences between independent static solutions, not an executed/interpolated trajectory or derivative certificate'))
dump('STATIC_NEIGHBOR_CONSISTENCY.json',neighbor)
doc('LATE_CONFLICT_GEOMETRY.md',f'''# 晚段真实空间定位

仅复评 3.729–3.867 s 已知局部冲突，实际静态比较 3.750、3.825、3.850 s。音乐时钟 = 演示时钟 −0.35 s。3.750 s 无名指仍保持 D5；3.778568 s 开始中指 E5，3.825 s 无名指已经释放约46.4 ms。冻结源为 Stage C R1 `{M['baseline']['sha256']}`，未继承 R2 −6° 修正。

{table}

在3.825 s，真实三角面交线的世界坐标范围：
- 原R1：{pair(source)['intersection_world_bbox_m']} m。
- 固定root A：{pair(fixedrow)['intersection_world_bbox_m']} m。
- 有限root B：{pair(center)['intersection_world_bbox_m']} m。

这不是仅俯视投影重叠。交线位于两指远端相向的皮肤区域，三视角图保留完整机位。面片数量依赖离散几何，不能单独说明严重程度。原R1、A、B内部顶点到对指实际皮肤的最大采样距离分别为 {depth(source):.3f}、{depth(fixedrow):.3f}、{depth(center):.3f} mm；B未实质降低A的内部见证深度，画面仍明显穿插。

深度方法：仅使用原R3四指远端强权重皮肤区域；在近端切口加人工封口，以实体角判断内部点，再测到对指真实皮肤的距离，排除最近点在人工封口上的见证。它是局部采样内部深度证据，不是全局最大穿透或最小分离平移。真实面交线无需依赖封口。具体见证顶点、坐标、最近皮肤点及封口排除数保存在 ACTUAL_STATIC_COMPARISON.json。没有全手逐顶点检查。

原中指D♯5内部顶点深度约0.7274 mm；A无命中，B没有内部采样顶点，但仍存在实际面交叉，因此不能将B数值黑键残差0当作真实净空PASS。E5按该时刻真实运动键面计算，不修改键时序。

新风险：B在3.825 s小指/F5有20对表面交叉；原R1和A此处均无命中。详见局部白键深度记录。这是root带动未参与关节求解的小指产生的风险，不能靠主动中指触键PASS放行。
''')
doc('FIXED_VS_BOUNDED_ROOT_FEASIBILITY.md',f'''# 固定root与有限root比较

结论：CURRENT_LOCAL_FEASIBILITY = NOT_ESTABLISHED。A复用R4有效静态结果，未重新优化固定root；只在原C1中复现以补充同口径几何测量。B仅一套预先锁定策略、一个三状态静态批次，每状态一次局部数值求解，没有重启、挑选、改权重或扩大范围。A/B使用相同关节域、局部实际蒙皮、接触与黑键残差，B只增加root参数与其保真代价。没有同自由度多起点的全局可行性证明，不能把结果归因于root的单独因果效应。

锁定：world X/Y/Z 各±3/±5/±3 mm，原WRIST_R腕点为旋转中心，world X pitch、world Z yaw旋转向量分量各±2°，roll未开放。原腕点在3.729–3.867 s的坐标包络约20.318/3.750/6.107 mm；D♯5宽/长/高11.274/64.866/15.444 mm。补偿上限是保守研究限制，纵深上限略大于原短区间纵深包络，不能据此宣称自然。与原局部姿态方向变化同量级的2°上限在计算前固定。原root总体路线没有写入任何改动。

{root_table}

{joint_table}

表中角度按原数值关节坐标加增量记录；实际Blender骨骼四元数另外保存。工程域MCP0–75、PIP0–95、DIP0–65、横展±28°不变，增量上限18/25/22/14°不变。A中指DIP约0.0033°、无名指PIP约0.0102°，B中指DIP约0.4057°、无名指PIP约0.0054°，已靠近伸直边界；其余自由度仍有余量。B的pitch −1.965°靠近−2°上限，但不能据此扩域。

{table}

所有活动音实际pad gap在2 mm内、水平越界0；3.825与3.850 s保持E5，3.750 s保持D5而非错误强制E5。原始蒙皮最大重建误差 <0.001 mm，B实际Blender与数值皮肤最大差 {max(r['max_mm'] for r in parity):.6f} mm。

A的失败核心是E5触键与无名指释放时相向远端皮肤分离未能同时达标，不是D♯5不可避开。R4固定root A已清除该静态D♯5命中，仍保留约6.695 mm内部见证与92面对。B中心残差代价20617.51，ftol终止、optimality约693.7，仍有83面对；数值success只是停止条件。前邻居xtol终止且optimality很大也说明不应把成功标志当约束证明。R4沿用的最近顶点/法向场和8 mm启停阈值是非光滑局部代理；释放只靠原姿态保真与键面下界，没有完整释放准备可行通道。它们是下一步需要复评的约束表达，不是已证明的唯一根因。

两邻居改善不能证明root必须参与；未做其固定root优化。中心仍失败且引入小指/F5，故B不足以支持进入有限root动态生成。不能推断固定root全局不可行、冻结Rig物理不可行，或更大root必然有效。
''')
doc('NATURAL_POSTURE_ASSESSMENT.md',f'''# 静态手型评估

NATURAL_POSTURE = HUMAN_PENDING。本轮无连续动态演奏，不能评价原速流畅度、抽动、速度/加速度或边界连续性。

DECISIVE_FULL_THREE_VIEW.jpg保留三个完整原机位；DECISIVE_DETAIL_THREE_VIEW.jpg是所有条件相同像素区域的辅助裁切，不用于隐藏冲突。行顺序为原R1、A固定root、B有限root。前后邻居图分别为3.750/3.850 s原R1与B。

中心B平移模长 {np.linalg.norm(center_fit['root_delta'][:3]):.3f} mm，旋转向量模长 {np.linalg.norm(center_fit['root_delta'][3:]):.3f}°。掌腕整体偏移不大，但小幅参数不能等同于产品自然度合格。中指/无名指仍明显交叉、释放指局部偏直，且小指接近F5并发生实际面交叉；不应将83比92略少包装成明显改善。没有证据显示需要通过修改冻结Rig解决。

前后邻居的相交消失，但独立静态解的中心参数与两侧差异明显。邻域差分（STATIC_NEIGHBOR_CONSISTENCY.json）只是潜在衔接风险，不是速度实测：从3.825到3.850 s，补偿平移变化 {neighbor[1]['translation_difference_mm']:.3f} mm，旋转参数变化 {neighbor[1]['rotation_vector_difference_deg']:.3f}°，最大关节增量变化 {neighbor[1]['max_joint_increment_difference_deg']:.3f}°。不连接这些姿态，不生成插值轨迹。

Human重点看：1）中心两指侧面和远端交叉；2）无名指释放是否自然；3）小指/F5新增干涉；4）相邻静态样本之间手型差异是否支持将来做连续验证。当前只能审核失败原因与路线，不是批准新演奏。
''')
doc('NEXT_MOTION_PLANNING_DECISION.md','''# 下一阶段唯一推荐路线

本轮结论 CURRENT_LOCAL_FEASIBILITY = NOT_ESTABLISHED。先复评非冻结局部接触、释放准备、相邻表面分离和事件窗口约束表达；暂不把增加root自由度作为下一次正式动态求解的既定方案。

最小后续研究模块：隔离目录内的coordination.Context.pair_clearance（真实三角面/连续距离的稳定引导，避免最近顶点切换与8 mm启停使局部优化停滞）；contacts与释放任务表达（区别D5持键、中指E5接手、无名指卸载/收回，不能仅依赖姿态先验和短时floor）；root变量的非主动指保护（已有小指/F5新增冲突，需纳入有限安全护栏）。不改冻结Rig/Mesh/Weights/Corrective，不改原A2/B3轨迹文件。

待这套约束能在同一工程域给出自然、接触正确的中心与邻域静态依据后，才值得另行授权一次局部联合动态验证。root是否纳入仍取决于固定root与有限root的同口径证据，不能默认扩域。本轮不执行该研究迭代或动态阶段。

下一次动态验证的最小候选事件支持：D5准备起点3.3842825 s（D5开始前0.18 s），经D5持键3.5642825–3.778568 s、E5持键3.778568–3.9928535 s及随后的交接恢复，候选终点4.1728535 s（E5释放后0.18 s）。音乐时间减0.35 s。此范围仅是供下一轮预检的事件定义建议，不是已证连续可行的窗口；必须在F♯5正在触键的末段保护目标接触并证明边界能够衔接，否则重新申请范围，不默认重算整段。

本轮没有证据要求重规划全部4小节，也没有证据证明上述有限窗口已经足够。保护：左手全部批准动作、右手窗口外动作、原root总体路线、23音符/指法/时序、全部琴键与音频。不要再次重审既有音乐链路。

止损：预检中心或邻域仍严重相交、新非目标键体穿入、手型明显恶化、或边界无法衔接，即停止；需冻结资产变化/大幅掌腕补偿/全段重规划则停并说明新授权。若未来获授权正式动态求解，只允许一次，失败不调权重重试。本轮不会自动进入R5。

STOP — HUMAN REVIEW
''')
status=dict(LATE_CONFLICT_DIAGNOSIS='COMPLETE',FIXED_ROOT_FEASIBILITY='FAIL_WITHIN_TESTED_CONSTRAINTS',BOUNDED_ROOT_FEASIBILITY='FAIL_WITHIN_TESTED_CONSTRAINTS',E5_ACTIVE_CONTACT='PASS',MIDDLE_RING_SPATIAL_CLEARANCE='NOT_IMPROVED',DSHARP5_CLEARANCE='IMPROVED',NATURAL_POSTURE='HUMAN_PENDING',FROZEN_RIG_CHANGE_REQUIRED='NO_EVIDENCE',NEW_DYNAMIC_SOLVES=0,NEW_DYNAMIC_CANDIDATES=0,FROZEN_ASSETS_UNCHANGED='YES',FINAL_STATUS='FEASIBILITY_COMPLETE_READY_FOR_HUMAN_REVIEW',architecture_conclusion='CURRENT_LOCAL_FEASIBILITY = NOT_ESTABLISHED',scope_notes=dict(diagnosis='Complete for requested local comparison, not entire four bars or a global infeasibility proof',middle_ring='Decisive 3.825s not substantially improved; neighboring 3.75/3.85s improved',Dsharp5='Improved vs original R1 sampled internal penetration, NOT improved vs A (A no hit, B residual surface crossings)',E5='Two finite static E5 contact samples only; no new sustained/dynamic certification',naturalness='Static review pending; no successful product candidate'),static_optimization_batches=1,static_B_states=3,new_fixed_root_optimizations=0,root_range_expansions=0,protected_files=len(protected))
dump('FINAL_STATUS.json',status)
links=['LATE_CONFLICT_GEOMETRY.md','FIXED_VS_BOUNDED_ROOT_FEASIBILITY.md','NATURAL_POSTURE_ASSESSMENT.md','NEXT_MOTION_PLANNING_DECISION.md','FINAL_STATUS.json','STRATEGY_LOCK.json','ROOT_RANGE_EVIDENCE.json','ACTUAL_STATIC_COMPARISON.json','BOUNDED_STATIC_RESULTS.json','ASSET_PRESERVATION.json','STATIC_NEIGHBOR_CONSISTENCY.json']
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Root + 多指 · 有限静态可行性比较</title><style>body{background:#141a21;color:#e6edf5;font:17px/1.6 system-ui;margin:0 auto;padding:30px;max-width:1500px}h1{font-size:30px}a{color:#8fc9ff}img{max-width:100%;height:auto}section{margin:28px 0;padding:18px;background:#202b37;border-radius:12px}.bad{color:#ffb89f}table{border-collapse:collapse;font-size:14px}td,th{border:1px solid #526274;padding:7px}code{white-space:pre-wrap}</style><h1>Root + 多指：有限静态可行性比较</h1><p class="bad">比较完成；当前局部可行性尚未建立。动态求解 0 / 动态候选 0 / 新 Action 0。</p><p>3.825秒：固定root 92对 → 有限root 83对实际皮肤面相交，内部见证深度未实质改善；E5触键保持，出现小指/F5新增面交叉。不能进入动态修复。邻居静态样本的改善不证明root必需。</p><p>以下均为静态诊断。三行顺序：原R1、复用R4固定root、唯一有限root策略。机位一致，不是演奏视频，也不证明动态自然度。</p>'''
for title,name in [('决定性3.825秒：完整三视角','DECISIVE_FULL_THREE_VIEW.jpg'),('相同像素裁切辅助：中心仍失败','DECISIVE_DETAIL_THREE_VIEW.jpg'),('3.750秒邻居：D5仍持键','BEFORE_NEIGHBOR_DETAIL.jpg'),('3.850秒邻居：E5持键','AFTER_NEIGHBOR_DETAIL.jpg')]:page+=f'<section><h2>{title}</h2><a href="{name}"><img src="{name}" alt="{title}"></a></section>'
page+='<section><h2>证据与报告</h2><ul>'+''.join(f'<li><a href="{n}">{n}</a></li>' for n in links)+'</ul></section><p>6563个受保护文件哈希一致，四个批准静态姿态相关20文件一致。NATURAL_POSTURE = HUMAN_PENDING。STOP — HUMAN REVIEW。</p></html>'
doc('STATIC_REVIEW.html',page)
print('DELIVERY_CREATED',json.dumps(status),flush=True)
