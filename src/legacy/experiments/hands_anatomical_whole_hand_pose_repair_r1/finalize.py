from common import *
import csv,math
from datetime import datetime,timezone,timedelta
facts=read(OUT/'BASELINE_FACTS.json');r1=read(OUT/'ROUND_1_DATA.json');r2=read(OUT/'ROUND_2_DATA.json');verified=read(OUT/'SAVED_REOPEN_MACHINE_VALIDATION.json');extra=read(OUT/'ADDITIONAL_READONLY_FACTS.json');natural=read(OUT/'NATURALITY_AND_STOP.json')
def aggregate(rows):
 out={}
 for r in rows:
  key=r['key'];old=out.get(key,dict(depth_mm=0.,bvh_pairs=0,clearance_mm=None))
  old['depth_mm']=max(old['depth_mm'],r['depth_mm']);old['bvh_pairs']+=r['bvh_pairs']
  if 'exact_clearance_mm' in r:old['clearance_mm']=r['exact_clearance_mm'] if old['clearance_mm'] is None else min(old['clearance_mm'],r['exact_clearance_mm'])
  out[key]=old
 return out
base=aggregate(facts['baseline_keys']);one=aggregate(r1['keys']);best=aggregate(verified['keys'])
metrics=[]
for label,keys,r in [('ORIGINAL_C1',base,None),('ROUND_1',one,r1),('ROUND_2_BEST',best,r2)]:
 metrics.append(dict(pose=label,time_sec=2.6,A_sharp_depth_mm=keys['A#4']['depth_mm'],A_sharp_intersection_triangle_pairs=keys['A#4']['bvh_pairs'],A_sharp_clearance_mm=keys['A#4']['clearance_mm'],A4_depth_mm=keys['A4']['depth_mm'],C_sharp5_depth_mm=keys['C#5']['depth_mm'],illegal_key_count=sum(k!='G4' and (v['depth_mm']>1e-6 or v['bvh_pairs']>0) for k,v in keys.items()),self_intersection_pairs=0 if r is None else r['self_pair_count'],new_cross_hand_pairs=0 if r is None else len(r['new_cross_hand_pairs']),thumb_G4_contact='PASS original contract',G4_active_target_skin_depth_mm=keys['G4']['depth_mm'],wrist_translation_mm=0 if r is None else math.sqrt(sum(x*x for x in r['wrist_delta_world_mm'])),wrist_rotation_deg=0 if r is None else r['wrist_rotation_delta_deg'],joint_domain_pass=True if r is None else r['strict_in_joint_domain'],naturality='Human rejected previous candidate not used as baseline; current selection pending Human'))
with (OUT/'QUANTITATIVE_ACCEPTANCE.csv').open('x',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=list(metrics[0]));w.writeheader();w.writerows(metrics)
with (OUT/'NEIGHBOR_KEY_GEOMETRY.csv').open('x',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=['key','baseline_depth_mm','candidate_depth_mm','candidate_triangle_pairs','candidate_clearance_mm','classification']);w.writeheader()
 for k,v in best.items():w.writerow(dict(key=k,baseline_depth_mm=base.get(k,{}).get('depth_mm',0),candidate_depth_mm=v['depth_mm'],candidate_triangle_pairs=v['bvh_pairs'],candidate_clearance_mm=v['clearance_mm'],classification='ACTIVE_G4_REGISTERED_CONTACT' if k=='G4' else 'MUST_BE_SEPARATED'))
hashes={r['path']:r['sha256'] for r in read(OUT/'PROTECTED_BEFORE.json')['files']}
for p in OUT.glob('*INPUT_RECEIPT.json'):
 for r in read(p)['files']:
  hashes.setdefault(r['path'],r['before']);assert hashes[r['path']]==r['before']
checks=[dict(path=p,before=h,after=sha(p),unchanged=sha(p)==h) for p,h in hashes.items()];assert all(r['unchanged'] for r in checks)
save('PROTECTED_SHA256_BEFORE_AFTER.json',dict(all_unchanged=True,files=checks,independent_piano_directory_access=False,embedded_checks=dict(rest_mesh_weights_correctives_unchanged=verified['native_unchanged'],all_unedited_action_payloads_unchanged=verified['all_unedited_action_payloads_unchanged'],key_action_payloads_unchanged=True),scope='Protected/actually read task inputs, including original C1, native frozen baselines, formal MIDI/timelines/fingering, keyboard/marker/Rig/acceptance data, prior failed results and rejected comparison Blend, and local human-reference files. No recursive audit of unrelated projects.'))
frames=read(OUT/'MATCHED_CAMERA_RENDER_MANIFEST.json')
camera_equal=True
for kind in ['OVERHEAD','SIDE_OBLIQUE','AUX_INDEX_SIDE','AUX_PALM_PERSP']:
 rows=[r for r in frames if r['view']==kind];camera_equal &= all(r['camera_matrix']==rows[0]['camera_matrix'] and r['scale']==rows[0]['scale'] and r['type']==rows[0]['type'] for r in rows)
assert camera_equal
result=dict(result='STATIC_PASS_PENDING_HUMAN',human_approved=False,teaching_animation_approved=False,substantive_pose_rounds=2,selected_round=2,only_time_sec=2.6,time_sample_count=1,animation_created=False,original_A_sharp_depth_mm=base['A#4']['depth_mm'],current_A_sharp_depth_mm=best['A#4']['depth_mm'],current_A_sharp_triangle_pairs=best['A#4']['bvh_pairs'],current_A_sharp_clearance_mm=best['A#4']['clearance_mm'],illegal_key_intersections=0,new_self_pairs=0,new_cross_hand_pairs=0,active_contacts=verified['active_contacts'],G4_legal_contact_skin_depth_mm=best['G4']['depth_mm'],wrist_delta_mm=r2['wrist_delta_world_mm'],wrist_translation_norm_mm=metrics[-1]['wrist_translation_mm'],wrist_rotation_delta_deg=r2['wrist_rotation_delta_deg'],index_qdeg=verified['qdeg']['INDEX'],joint_domain_pass=True,saved_skin_error_mm=verified['saved_live_skin_error_mm'],saved_joint_error_deg=verified['saved_live_joint_error_deg'],protected_files=len(checks),same_camera_projection_verified=camera_equal,candidate=str(OUT/'ROUND_2_STATIC_NOT_APPROVED.blend'),candidate_sha256=verified['candidate_sha256'],source_sha256=sha(SOURCE),next_gate='Human must explicitly approve static naturality before a separately authorized animation task.',stop='STOP — HUMAN REVIEW')
save('RESULT.json',result)
def link(name):return f'[{name}](<{(OUT/name).as_posix()}>)'
now=datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S +08:00')
text=f'''# HANDS_ANATOMICAL_WHOLE_HAND_POSE_REPAIR_R1

**STATIC_PASS_PENDING_HUMAN — STOP — HUMAN REVIEW**。{now}。

本轮从原 C1 独立副本出发，经 **2 轮** Blender MCP 直接摆姿，得到仅针对 **2.600000s** 的静态候选。独立重新打开后，右手对全部非目标琴键未检出非法相交，原关节域及当前两手活动接触保持；Codex 初步认为轮廓较前轮被否决候选合理，可以交 Human 判断。**没有 Human 自然性批准，没有正式教学动画批准，没有连续动画。** 未使用剩余轮次继续刷指标。

**真人依据与自然性边界**

任何骨姿修改前，先查看 Hands 已存 MusicRadar / Daniel Griffiths 右手五指真人照片、PiaDOOR 真人八度照片，及本地 PianoVAM 真实演奏视频 4.0s / 10.0s 两张提取帧。图片能支持各指曲度不同、连续指弧和整手上下文的重要性；不能由二维照片反演关节标准角度、腕高或压力，视频两帧也未被冒充已核实的 G4 拇指持键示范。4.0s 有运动模糊。没有用 AI 人手作为人体依据。

补读 [Practising the Piano 教学公开页](https://practisingthepiano.com/preparing-to-play-octaves/) 的关节支撑与腕部活动说明，仅采用定性观察原则，未把八度练习转成当前任务的角度处方。Hoffman 页面本轮未能取到正文，不作新增证据。来源、当地文件和限制详见 {link('REFERENCE_BASIS.md')}。PianoVAM 为 Kim et al., ISMIR 2025，CC BY-NC-SA 4.0，仅内部非商业定性验证，没有复制数据集动作或晋升产品资产。

前轮第三候选已经被 Human 明确否决，始终保持 NOT_APPROVED，仅在最终统一相机对照中读取。没有载入它作为摆姿起点，也没有把它当自然手型模板。

**原 C1 空间事实**

原右腕骨头世界位置约 (135.832,−122.634,33.359)mm；食指 MCP 约 (126.642,2.982,45.420)mm，PIP约 (129.051,31.128,29.773)mm，DIP约 (132.908,45.063,14.709)mm。黑键前沿中性 Y≈49.421mm，顶面 Z≈15.444mm。原食指末端皮肤到达黑键前沿后方，并处于键体高度内。腕—食指 MCP 连线约向前升高12.061mm，不单凭此数值判腕高错误。

原食指局部增量 MCP/PIP/DIP/展指约 16.865/17.383/9.053/−13.787°。沿用冻结 Rig 定义的现有屈伸与展指轴；完整局部轴、原掌腕矩阵、各 MCP 点及真实变形数据保留在 {link('BASELINE_FACTS.json')}。原共享掌位下，活动拇指 G4、食指 IDLE 的状态已核对；左手此刻中指 B3 ACTIVE。

这次对**整个右手皮肤**而非只食指作键体检查，额外检出原 C1 在此刻对 A4 约0.745018mm、C#5约4.252741mm 的非目标键侵入。它们是本轮前已存在的缺陷，不归咎本轮；但也不能在最终候选中忽略。原 G4 是活动目标键，存在约1.841165mm 的皮肤键体内部深度，单独作为活动接触的原始读数记录。

**动画师式编辑与两轮决定**

控制使用现有 Blender MCP 的 `execute_blender_code`，直接修改现有 Pose Bone；没有 IK、优化器、随机/网格搜索或自动姿态生成。三根食指骨沿已有局部轴写入旋转；必要整手调整写入 `WRIST_R` 的位置和旋转，Rig/root 对象、骨结构/rest、网格/权重/corrective 均不改。frame157 的关键帧仅用于保存静态姿态、避免原 Action 在重开后覆盖；没有制作进入、保持、退出动画。

| 状态 | 食指 MCP/PIP/DIP/展指 ° | 掌腕调整 | A#4 穿入 / 净空 mm | 其他非法键 | 新自交 |
|---|---|---|---|---|---:|
| 原 C1 | 16.865 /17.383 /9.053 /−13.787 | 原样 | 5.637124 / 0 | A4、C#5 | 0 |
| 第1轮 | 8 /12 /6 /−12 | 不动掌腕 | 3.009237 / 0 | A4、C#5 保留 | 0 |
| 第2轮，保留 | 8 /12 /6 /−12 | 后收4mm，小幅联合倾斜 | 0 / **{best['A#4']['clearance_mm']:.6f}** | **无** | 0 |

第1轮依据近侧视把过于向下的末端钩扣改为较均匀的指弧，并保持适度展指；原掌腕不动。这一轮没有像前候选那样用接近极限的侧摆挤向中指，轮廓初步更合理，但不能以此接受残余3.009mm穿入。

第2轮保持**同样的食指局部姿态**，基于共有掌位与黑键前沿的关系，直接将整手后收4mm，并绕拇指附近作世界 X +1°、Y −4° 的小幅联合旋转。它是人工选择的单次刚体摆放操作，不是保持接触的迭代求解器。活动 pad 允许在原合法 G4 键面内移动，随后实测验收，没有改 marker、键面或接触容差。

实际腕骨位移为 ({r2['wrist_delta_world_mm'][0]:.6f},{r2['wrist_delta_world_mm'][1]:.6f},{r2['wrist_delta_world_mm'][2]:.6f})mm，模长 **{metrics[-1]['wrist_translation_mm']:.6f}mm**，朝向变化 **{r2['wrist_rotation_delta_deg']:.6f}°**。食指 MCP 移动约 (−3.857,−4.948,+1.771)mm；小指 MCP 高度随倾斜增加约6.423mm，需 Human 同时看整手是否仍放松。没有单独改中指、无名指、小指或拇指局部关节。root 对象矩阵保持，整手空间变化由 WRIST_R 传递。

原冻结蒙皮正常参与求值。矩阵分解后的腕骨 scale 原始读数为 {extra['wrist_pose_scale']}，与1的差为约1.2×10⁻⁷量级浮点舍入，未主动修改缩放、未用缩放避障。原生 rest、顶点、拓扑、权重和 corrective driver 摘要前后一致。

**真实几何及当前演奏验收**

使用实际 evaluated LBS/corrective 皮肤三角面与原 Action 驱动的实际键网格。检查整个右手网格，覆盖所有混合蒙皮区域、掌腕及各指；88键逐组件用真实变换及 AABB 排除远键，邻近组件作真实 BVH 面相交和必要的三角面内部深度 primal/dual 证书检测。实际键网格与注册几何逐点核对，非单点、骨代理或二维投影判断。正净空以真实顶点–三角面与完整边–边最小距离补全，不只看顶点距离。

| 非目标键 | 原最大内部深度 mm | 候选内部深度 mm | 候选相交面对 | 候选真实最小净空 mm |
|---|---:|---:|---:|---:|
| A#4 | {base['A#4']['depth_mm']:.6f} | 0 | 0 | {best['A#4']['clearance_mm']:.6f} |
| A4 | {base['A4']['depth_mm']:.6f} | 0 | 0 | {best['A4']['clearance_mm']:.6f} |
| C#5 | {base['C#5']['depth_mm']:.6f} | 0 | 0 | {best['C#5']['clearance_mm']:.6f} |
| G#4 | 0 | 0 | 0 | {best['G#4']['clearance_mm']:.6f} |

其余附近白/黑键均无非法相交，完整数据见 {link('NEIGHBOR_KEY_GEOMETRY.csv')}。右手皮肤自交0、新跨手面对0；左手实际皮肤前后差0mm，没有将改变传给另一只手。该“无非法碰撞”判断针对本轮受编辑的右手及其与左手的关系，不声称修好了原左手未审计历史缺陷。

G4活动触键按原合同保留：真实skin pad面内、横向误差0、gap **0.785998mm**，原gap0.437994mm；世界点后移约4.000027mm，键中性坐标前沿余量 **{extra['thumb_front_edge_margin_mm']:.6f}mm**。活动G4键体仍与拇指皮肤有12对相交面对、最大内部深度约 **{best['G4']['depth_mm']:.6f}mm**，低于原1.841165mm/27面对。它是当前主动演奏目标，明确单列，不能把这12对伪报为整个场景零相交，也不能用活动身份豁免邻键。

左手B3原活动接触保持：pad面内、gap0.506926mm、皮肤不变。没有压力/接触面积模型，接触 PASS 只代表原有固定skin pad与合法面及距离合同。原3mm垂向、0.03mm面外距离/inside条件及其余验收数据均未放宽。

全右手关节均在原域内；本轮食指8/12/6/−12°，没有接近±25°的展指逃逸。实际骨旋转可由既有屈伸/展指轴重建，记录的误差为0（Blender浮点分辨率内），没有加入横向扭转自由度。此检查只验证用轴与工程域，不是人体解剖或自然性证明。

重新打开最终 Blend，在2.600000s测得：与编辑时骨角差0°、真实皮肤差0mm；仍无非法键相交及新增指间/跨手碰撞。见 {link('SAVED_REOPEN_MACHINE_VALIDATION.json')}。只有一个静态时间样本，**不证明连续时间安全**，0.282mm的 A#4 净空也没有动画鲁棒性保证。没有检查或修复0.433s、其他时刻，没有制作连续动画。

**自然性专项与剩余风险**

Codex已实际观察原图、两轮完整俯视/侧视/近侧视/掌腕透视，以及与前轮被否决候选的同相机对照。初步认为当前食指弧度较前候选连续，末端钩扣较少、侧摆较小、未向中指明显挤拢，整体掌腕仍接近原布局，达到交 Human 静态审核的条件。这是**初步观察，不是自然性通过证书**。

冻结网格的多边形折面、指根附近皮肤凹折仍可见，需要 Human 判断是否有不合理折角/塌陷；不能凭无自交认定表面自然。也需要判断当前食指悬停高度、拇指靠白键前部的位置以及小指随掌倾斜后的整体放松程度。没有前臂/肘肩模型，没有可信的侧面真人腕高标定，不能认证整条手臂人体工学。

**五个指定问题**

1. **掌腕位置是否可能是主要因素？** 有直接的局部证据支持它是重要因素：第1轮和第2轮食指局部角完全相同，仅做小幅共享掌腕调整，A#4深度3.009mm变为正净空，同时A4/C#5原侵入消失。原MCP至黑键前沿只有约46.439mm，而末端在键体高度内伸入后方。它支持共享手位是该时刻的因果贡献，不能据这一个联合平移/旋转实验断言它是唯一主因或原整曲手位规划普遍错误。
2. **是否找到自然且无碰撞姿态？** 找到真实无非法键碰撞、关节合法、当前接触保持且Codex初步认为合理的静态候选。人体自然性尚待Human，不能把“初步合理”写成已获自然性批准。
3. **是否比前轮第三候选更自然？** 初步判断有改善：前候选2/26/14/−24.5°与本轮8/12/6/−12°相比，后者不把基节接近伸直与强末端卷曲/大侧摆叠在一起，侧视轮廓较缓，俯视与中指间距更舒展。最终判断请看并排图，Human先前否决前候选的意见不被推翻。
4. **限制主要在哪？** 本轮未出现机器静态失败；第1轮表明温和食指单独调整不足，第2轮表明适度共享掌位可解决当前几何冲突。没有发现必须改Rig轴/权重的证据，也没有证明它们完全无缺陷。剩余限制是自然性、原接触合同的单点范围及很小的A#4净空，不是已证明合法关节域无解。
5. **能否进入下一轮动画？** 当前证据足够交Human进行静态自然性审核，**不足以直接开做动画**。必须先取得Human对这组实际俯视/侧视图片的明确认可，再另行授权进入/保持/退出关键帧任务；静态无碰撞不推出动态安全。

**交付、保护与停止**

优先查看 {link('NATURALITY_TRIPTYCH_OVERHEAD.png')} 和 {link('NATURALITY_TRIPTYCH_AUX_INDEX_SIDE.png')}，原C1 / 前轮Human否决姿态 / 本轮候选均在相同时间、相机、投影比例下，统一裁切/缩放并明确标注。数字不用于自然性排名。

原C1与当前对照：{link('COMPARISON_OVERHEAD.png')}；{link('COMPARISON_INDEX_CLOSE.png')}；{link('COMPARISON_SIDE_OBLIQUE.png')}；{link('COMPARISON_AUX_INDEX_SIDE.png')}；{link('COMPARISON_AUX_PALM_PERSP.png')}。所有图来自真实 Blender 渲染，未修图改变手型/琴键、未隐藏对象；正式镜头参数保持。原始12张匹配渲染与相机矩阵见 {link('MATCHED_CAMERA_RENDER_MANIFEST.json')}，实际核对三方相机矩阵/类型/比例完全一致。

最佳静态候选：{link('ROUND_2_STATIC_NOT_APPROVED.blend')}，打开后看 **2.600000s / frame157**。仅该静态姿态获机器复核，附近曲线未进行动画验收。SHA256 `{result['candidate_sha256']}`。

原 C1 SHA256 `{result['source_sha256']}`。{len(checks)}项保护/实际读取输入前后 SHA256 一致，见 {link('PROTECTED_SHA256_BEFORE_AFTER.json')}；内嵌原生Rig、rest/层级、网格/蒙皮/corrective、键Action及全部未编辑动画路径摘要亦保持。文件收据不是对无关历史目录的递归扫描。

所有新增内容仅写本隔离目录。独立 piano 目录没有访问、扫描、读取、运行或间接跟随。原 C1、正式 MIDI、23音时钟/冻结指法、历史候选与全部保护输入不改。当前两轮姿态都从原C1直接编辑；前轮第三候选仅后置读取作自然性对照，没有作为起点。未开发求解器或自动纠错Agent。

找到第2轮合格机器静态候选后立即停止摆姿，仅完成保存复核、对照渲染与报告。**STOP — HUMAN REVIEW**。
'''
with (OUT/'TECHNICAL_REPORT.md').open('x',encoding='utf8') as f:f.write(text)
human=f'''# HUMAN REVIEW · STATIC_PASS_PENDING_HUMAN

{now}。只验证2.600000s静态：右手对非目标键无相交，A#4净空0.282075mm；G4当前接触保持。**尚未批准人体自然性或教学用途，未制作连续动画。**

建议按此顺序看：

1. {link('NATURALITY_TRIPTYCH_OVERHEAD.png')}：原C1 / Human已否决的前轮第三候选 / 本轮第二候选，同投影等倍率。
2. {link('NATURALITY_TRIPTYCH_AUX_INDEX_SIDE.png')}：直接比较指根—PIP—DIP轮廓，不按几何数字排名。
3. {link('COMPARISON_AUX_PALM_PERSP.png')}：看小幅整手后收/倾斜后的掌腕与其他指。
4. {link('COMPARISON_OVERHEAD.png')}、{link('COMPARISON_INDEX_CLOSE.png')}、{link('COMPARISON_SIDE_OBLIQUE.png')}。

请Human明确判断四件事：

- 食指弯曲与悬停是否自然、放松？
- 指根或PIP/DIP附近是否仍有视觉上的异常折角、塌陷？
- 手掌/腕部的小幅调整，以及拇指较前部触键、其他指的高度是否合理？
- 整体是否满足钢琴教学演示的辨识与自然观感要求？

文件：{link('ROUND_2_STATIC_NOT_APPROVED.blend')}（**2.600000s / frame157**，静态重开已复现）；{link('TECHNICAL_REPORT.md')}；{link('QUANTITATIVE_ACCEPTANCE.csv')}；{link('NEIGHBOR_KEY_GEOMETRY.csv')}；{link('SAVED_REOPEN_MACHINE_VALIDATION.json')}；{link('PROTECTED_SHA256_BEFORE_AFTER.json')}。

0.282mm净空只属单姿态结果，不是动态保证。G4是合法活动目标，仍有0.607091mm皮肤键体内部深度并单列记录，不能理解为全场景任何面都不接触。当前接触按原合同保持，没有压力模型。

只有Human明确认可本静态姿态后，再单独授权动画。不会自行制作进入/保持/退出，不扩展0.433s、其他时刻或其他项目。

STOP — HUMAN REVIEW
'''
with (OUT/'HUMAN_REVIEW.md').open('x',encoding='utf8') as f:f.write(human)
imgs=read(OUT/'REVIEW_IMAGE_MANIFEST.json')['images'];deliver=['TECHNICAL_REPORT.md','HUMAN_REVIEW.md','RESULT.json','QUANTITATIVE_ACCEPTANCE.csv','NEIGHBOR_KEY_GEOMETRY.csv','SAVED_REOPEN_MACHINE_VALIDATION.json','PROTECTED_SHA256_BEFORE_AFTER.json','ROUND_2_STATIC_NOT_APPROVED.blend','REFERENCE_BASIS.md']
save('FINAL_DELIVERY_MANIFEST.json',dict(result=result['result'],files=[dict(path=str(OUT/n),sha256=sha(OUT/n)) for n in deliver]+imgs,pose_rounds=2,animation_created=False,stop='STOP — HUMAN REVIEW'))
print('FINALIZED',result['result'],'protected',len(checks),'unchanged',flush=True)
