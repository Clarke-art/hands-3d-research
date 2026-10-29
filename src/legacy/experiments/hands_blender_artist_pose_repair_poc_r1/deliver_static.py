from common import *
import csv
from PIL import Image,ImageDraw,ImageFont
from datetime import datetime,timezone,timedelta
facts=read(OUT/'BASELINE_FACTS.json');live=read(OUT/'ROUND_3_STATIC_CHECK.json');v=read(OUT/'SAVED_REOPEN_STATIC_VALIDATION.json')
rounds=[read(OUT/f'{name}_STATIC_CHECK.json') for name in ['ROUND_1_APPLIED','ROUND_2','ROUND_3']]
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',n)
images=[]
for kind,base_name,new_name,title in [('OVERHEAD','ORIGINAL_2_600_OVERHEAD.png','ROUND_3_2_600_OVERHEAD.png','正式正交俯视'),('SIDE_OBLIQUE','ORIGINAL_2_600_SIDE_OBLIQUE.png','ROUND_3_2_600_SIDE_OBLIQUE.png','原场景侧斜视'),('ARTIST_AUX_INDEX_SIDE','ORIGINAL_AUX_INDEX_SIDE.png','ROUND_3_AUX_INDEX_SIDE.png','辅助近侧视：同一相机')]:
 pr=next(r for r in v['projections'] if r['view']==kind)
 canvas=Image.new('RGB',(2560,1050),'#101723');d=ImageDraw.Draw(canvas)
 for col,(identity,name) in enumerate([('ORIGINAL',base_name),('ROUND_3',new_name)]):
  im=Image.open(OUT/name).convert('RGB');dr=ImageDraw.Draw(im);w=max((r for r in pr['witnesses'] if r['identity']==identity),key=lambda x:x['depth_mm']);px,py=w['pixel']
  dr.ellipse((px-9,py-9,px+9,py+9),outline='#ff364e',width=3);dr.line([(px+8,py-8),(px+42,py-42)],fill='#ff364e',width=2)
  x=col*1280;canvas.paste(im,(x,64));d.text((x+20,10),f"{'原 C1' if col==0 else '第三轮 · NOT_APPROVED'} | {title} | 2.600000s",font=font(28),fill='white')
  q=facts['index_qdeg'] if col==0 else v['qdeg']
  lines=[f"A#4 真实三角面最大穿入：{w['depth_mm']:.6f} mm；净空 0 mm",f"见证三角形顶点：{w['triangle']}",f"MCP/PIP/DIP/展指：{q[0]:.3f} / {q[1]:.3f} / {q[2]:.3f} / {q[3]:.3f}°",'红圈为实际三维内部见证投影；可能被琴键或皮肤遮挡。','食指 IDLE；拇指 G4 ACTIVE 保持。静态未通过，未进入连续动画。']
  for j,line in enumerate(lines):d.text((x+20,802+j*43),line,font=font(24),fill='#ff9b9b' if j==0 else '#c9d6e9')
 path=OUT/f'{kind}_BEFORE_AFTER_ANNOTATED.png';assert not path.exists();canvas.save(path);images.append(path.name)
initial=read(OUT/'PROTECTED_BEFORE.json');hashes={r['path']:r['sha256'] for r in initial['files']}
for p in OUT.glob('*INPUT_RECEIPT.json'):
 for r in read(p)['files']:
  hashes.setdefault(r['path'],r['before']);assert hashes[r['path']]==r['before']
receipts=[dict(path=p,before=h,after=sha(p),unchanged=sha(p)==h) for p,h in hashes.items()]
assert all(r['unchanged'] for r in receipts)
save('PROTECTED_SHA256_BEFORE_AFTER.json',dict(all_unchanged=True,independent_piano_access=False,files=receipts,embedded_protection=dict(native_rest_skinning_correctives=v['native_unchanged'],other_scene_actions=v['protected_actions_unchanged'],other_finger_animation=v['other_finger_action_payload_unchanged'])))
basepeak=max(r['depth_mm'] for r in v['baseline_keys']);newpeak=max(r['depth_mm'] for r in v['keys'])
old=read(ROOT/'experiments/hands_idle_index_black_key_clearance_prototype_r1/STILL_GEOMETRY_PROJECTIONS.json');oldpeak=max(k['depth_mm'] for r in old if r['identity']=='CANDIDATE_B' and r['label']=='B' for k in r['geometry'])
quant=[]
for tag,r in [('ORIGINAL',None),*[(f'ROUND_{i+1}',r) for i,r in enumerate(rounds)]]:
 keys=v['baseline_keys'] if r is None else r['keys'];contacts=facts['thumb_contact'] if r is None else r['thumb_contact'];peak=max(k['depth_mm'] for k in keys)
 quant.append(dict(pose=tag,time_sec=2.6,max_depth_mm=peak,a_sharp_clearance_mm=0,collision_free_time_samples='0/1 (0%)',new_key_identities=0,new_self_pairs=0 if r is None else len(r['new_self_pairs']),thumb_contact_pass=contacts['pass_'],thumb_gap_mm=contacts['gap_mm'],joint_bounds='BASELINE' if r is None else ('IN_DOMAIN' if r['strict_q_in_bounds'] else 'raw floating-point readout; see JSON'),animation_boundary_error='NOT_TESTED: stage2 not entered',outside_recovery='NOT_TESTED: static-only candidate'))
with (OUT/'QUANTITATIVE_ACCEPTANCE.csv').open('x',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=list(quant[0]));w.writeheader();w.writerows(quant)
result=dict(result='PARTIAL',static_pass=False,animation_pass=False,phase2_executed=False,reason='Three substantive observed pose corrections reduce actual penetration but do not eliminate A#4 skin intersection. Static prerequisite failed; stop before stage2.',used_blender_mcp=True,direct_pose_bone_edit=True,substantive_pose_rounds=3,bones=candidate_bones if False else ['INDEX_MCP_R','INDEX_PIP_R','INDEX_DIP_R'],baseline_peak_mm=basepeak,final_peak_mm=newpeak,baseline_reduction_percent=(1-newpeak/basepeak)*100,previous_fixed_strategy_at_2_6_mm=oldpeak,relative_to_previous_static_reduction_percent=(1-newpeak/oldpeak)*100,final_pose_qdeg=v['qdeg'],q_legal=v['strict_q_in_bounds'],new_key_identities=v['new_key_identities'],new_self_pairs=v['new_self_pairs'],new_cross_hand_pairs=v['new_cross_hand_pairs'],current_thumb_pad_shift_mm=v['thumb_pad_shift_mm'],saved_reopen_pose_error_deg=v['saved_vs_live_q_error_deg'],saved_reopen_skin_error_mm=v['saved_vs_live_skin_error_mm'],contact_48_samples='NOT_RUN: phase2 not entered',source_sha256=sha(SOURCE),candidate_sha256=sha(OUT/'ROUND_3_STATIC_NOT_APPROVED.blend'),stop='STOP — HUMAN REVIEW')
save('RESULT.json',result)
def link(name):return f'[{name}](<{(OUT/name).as_posix()}>)'
now=datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S +08:00')
text=f'''# HANDS_BLENDER_ARTIST_POSE_REPAIR_POC_R1

**PARTIAL — STOP — HUMAN REVIEW**。{now}。

三轮直接姿态编辑把 2.600000s 的真实 A♯4 穿入由 **{basepeak:.6f}mm 降至 {newpeak:.6f}mm**，但仍有 19 对三角面相交。没有找到满足全部条件的静态姿态，故未进入阶段2、未制作或验收连续动画，不能描述为修复成功。没有尝试第四轮、调整手掌/腕、修改其他手指或扩大问题范围。

**控制方式与实际编辑**

使用已配置 Blender MCP 的 `execute_blender_code` 实际操作当前 Blender。先将原 C1 另存到本隔离目录，再直接给 `INDEX_MCP_R`、`INDEX_PIP_R`、`INDEX_DIP_R` 的 `rotation_quaternion` 赋值并在原时间 2.600000s（frame 157）插入静态姿态关键帧。MCP 的实际骨骼读数及真实 Blender 渲染确认操作落地。Python 仅用于把人工选定的关节姿态写入现有骨骼，并检查网格；没有运动求解器、随机/网格搜索或自动角度生成器。

工作循环是原俯视/侧视观察 → 一次直接摆姿 → 真正模型渲染 → mesh/BVH/三角面读数 → 下一轮观察修正。原场景侧斜视对食指内侧遮挡较多，另建固定辅助近侧视相机，原 C1 与候选采用相同位置/投影。正式 STAGE_C_OVERHEAD 和原侧斜视相机保持不变，所有对象可见性未改。保存后另用现有 Blender Python API 后台进程独立重新打开候选，验证不是只改变内存或绘制示意图。

首次打开原文件后出现 MCP window context 暂时为空，随后复用已加载原 C1 完成隔离另存；第一次 Action copy 后的依赖求值曾恢复原姿态。`ROUND_1_STATIC_*`（不带 APPLIED）记录的正是原姿态，作为工具执行失败证据保留，不算额外姿态候选。随后先提交实际 Pose Bone 关键帧再求值，`ROUND_1_APPLIED` 才是第一轮实质性修改。没有将这次无效操作冒充改善。

**三轮观察及结果**

| 姿态 | MCP/PIP/DIP/展指（°） | A♯4 面内深度 mm | BVH 面对 | 新增自交面对 | 观察与判断 |
|---|---|---:|---:|---:|---|
| 原 C1 | 16.865 / 17.383 / 9.053 / −13.787 | {basepeak:.6f} | 58 | 0 | 食指末端进入黑键前沿 |
'''
reasons=['朝 A4 前方收拢并缩短末端弧度；侧缘仍入键，新增第一指蹼附近自交，拒绝','保留弯曲弧度、改向 B4 一侧展开；自交消失，但向下末端仍擦黑键前角','根据近侧视打开 MCP、略放松 PIP/DIP，保留侧向通道；仍有小幅真实相交']
for i,r in enumerate(rounds):
 key=max(r['keys'],key=lambda k:k['depth_mm']);q=r['qdeg'];text+=f"| 第{i+1}轮 | {q[0]:.3f} / {q[1]:.3f} / {q[2]:.3f} / {q[3]:.3f} | {key['depth_mm']:.6f} | {key['bvh_pairs']} | {len(r['new_self_pairs'])} | {reasons[i]} |\n"
text+=f'''
数值是观察后直接摆出的姿态读数，不是预设一组参数后进行扫描。第二轮到第三轮同时依据侧面弧度调整基节与末端，并没有无限增加抬指角度。第三轮展指已接近合法侧向边界、MCP 接近伸展端；停止三轮实验不能推出合法域中一定无解。尚未证明必须微调手掌，因此未动掌或腕。

**静态几何与演奏复核**

使用实际 evaluated LBS/corrective 皮肤和原 Action 驱动的真实键网格。除了整食指 ROI，还将本次所有实际变动皮肤顶点关联面纳入检查，覆盖混合蒙皮邻域及所有附近白/黑键。实际键网格与注册几何在当前 Action 姿态逐点校对；BVH 检测面相交，凸键真实网格面半空间加三角面 primal/dual 证书测内部最大深度，不能用 skin pad 或 TIP 骨点替代。

最终见证三角形顶点 `[237,2698,1244]`，世界点约 `(0.136725285,0.052708220,0.014870702)m`；深度上下界约 0.573477496–0.573477502mm，证明仍是实际皮肤侵入，不是二维遮挡。A♯4 净空 **0mm**。其他最近键：B4 表面最小净空约 10.584224mm、A4 约 14.698114mm、G♯4 约 20.908222mm。分离距离由顶点–真实三角面及边–边最小距离补全，不只用顶点最近距离估计。

最终候选未出现新的碰撞键身份、新增非相邻皮肤自交或新增跨手碰撞；第一轮新增的 2 对自交仅保留在被拒绝的第一轮文件中。最终关节实际值 2.000000 / 25.999998 / 14.000000 / −24.500000°，位于原 MCP/PIP/DIP 0–32/0–32/0–20°、展指±25°域内，没有改约束或验收阈值。

2.600000s 右手拇指 G4：真实 pad 保持面内、gap `{facts['thumb_contact']['gap_mm']:.9f}mm`、pad 位移 **0mm**，接触 PASS。当前其他活动音的真实接触也逐项记录在 {link('SAVED_REOPEN_STATIC_VALIDATION.json')}。掌/root、腕及其他手指动画路径摘要保持，左手变形皮肤变化为 0。食指动作经冻结混合权重传到拇指 ROI 的最大皮肤位移 `{v['other_digit_skin_max_mm']['THUMB']:.6f}mm`；这些变动面已参与检测，不能把“拇指骨没动”当作所有拇指皮肤绝对不变。

**保存、静态门槛与未执行项**

重新打开 {link('ROUND_3_STATIC_NOT_APPROVED.blend')} 并精确设置 2.600000s 后，骨姿态与编辑时差 **0°**、真实皮肤差 **0mm**；仍复现 0.573478mm 穿入。Rig rest/层级、mesh 顶点/拓扑、权重、corrective driver 摘要保持一致；除三根食指骨曲线外，所有原有动画路径和全部键 Action payload 保持一致。全 23 音原 MIDI、指法、时钟没有改动。

最终无碰撞时间采样比例为 **0/1（0%）**，这里只检测静态 t=2.600000s，不伪造时间窗口比例。阶段2未执行，所以 2.45–2.90s 与 2.10–3.35s 的密集时间网格、48 活动接触采样、进入/退出关键帧、异常关节速度、亚帧边界误差、区间外回归均为 **NOT_RUN / NOT_TESTED**。保存再打开的静态误差为零不等于动画边界误差为零。此 Blend 仅为静态失败证据，其邻接时间的曲线没有取得连续动画验收，不能作为完整动画播放交付。

原 C1 既有 A♯4 穿入是继承问题；本轮第一轮自交是新增问题，已在最终候选消失。最终残余碰撞不能归为“可忽略”，也没有通过放宽阈值计为 PASS。

**Codex 初步视觉判断（非 Human 批准）**

最终俯视仍能辨认各指，但食指向中指侧收拢，侧面屈曲与其他指形成的悬停弧度尚不能认定自然教学手型。辅助近侧视可看到末端已明显离开原深穿位置，却仍擦黑键前角；因此几何门槛先行失败。未检查连续动作，更不能评价进入/退出是否自然。Human 需要判断侧向挤拢、基节接近伸展端和末端曲度是否可接受。

**对五个最终问题的回答**

1. Codex 确实通过 Blender MCP 直接摆姿、设置关键帧、观察渲染并迭代；但本轮没有证明能摆出同时满足全部条件的正确钢琴演奏手型。
2. 本轮没有找到真实无碰撞静态姿态。不能据三轮局部尝试断言它不存在，也不能声称原 Rig 无解。
3. 静态门槛失败，按任务要求停止阶段2。自然嵌入原 C1 的能力本轮未验证，不能回答“已做到”。
4. 相对原 C1，单时刻深度减少约 `{result['baseline_reduction_percent']:.2f}%`；相对上一轮固定策略在同一时刻的 `{oldpeak:.6f}mm`，再减少约 `{result['relative_to_previous_static_reduction_percent']:.2f}%`。新增证据是观察驱动的合法展指与关节弧度编辑能够进一步减轻碰撞，并保持当前 G4 接触；这只是静态改善，仍不是成功清障。未载入或复用上轮候选姿态，也没有对上轮动画作优劣泛化结论。
5. 目前只有“工具控制→真实模型观察→直接姿态编辑→几何反馈→保存复现”的流程可操作性证据。缺少合格静态姿态及连续修复案例，不足以支持自动动画纠错 Agent 的可靠性、泛化或生产封装。本轮未建立此类 Agent。

**文件与保护**

对照图：{link('OVERHEAD_BEFORE_AFTER_ANNOTATED.png')}；{link('SIDE_OBLIQUE_BEFORE_AFTER_ANNOTATED.png')}；{link('ARTIST_AUX_INDEX_SIDE_BEFORE_AFTER_ANNOTATED.png')}。这些均由真实 Blender 渲染加标注，红圈仅为内部见证点投影，可能被遮挡。原始未标注俯视/侧视及三轮全部证据均保留。阶段2未执行，因此无连续对照视频，未用静态图拼视频冒充动画。

定量表：{link('QUANTITATIVE_ACCEPTANCE.csv')}。阶段状态：{link('RESULT.json')}；MCP 使用与停止记录：{link('MCP_SESSION_STOP.json')}。保护收据：{link('PROTECTED_SHA256_BEFORE_AFTER.json')}，`{len(receipts)}` 项原始输入前后 SHA256 全部一致，另有内存中原生 Rig/蒙皮/corrective、未编辑动画路径及琴键 Action 摘要复核。

原 C1 SHA256：`{sha(SOURCE)}`。

最终静态候选 SHA256：`{result['candidate_sha256']}`。

所有新增内容只在本实验隔离目录。未访问、扫描、读取或运行独立 piano 目录，未跟随旧脚本的外部项目引用；只复用已读过的 Hands 纯几何辅助函数。原资产、历史失败和前轮候选不变。未修 0.433s、其他手指或整段 C1；不更改合同，不合并候选。

**STOP — HUMAN REVIEW**
'''
with (OUT/'TECHNICAL_REPORT.md').open('x',encoding='utf8') as f:f.write(text)
human=f'''# HUMAN REVIEW · PARTIAL · STATIC GATE FAILED

{now}。三轮直接 Pose Bone 编辑已结束；原 A♯4 深度 5.637124 → 0.573478mm，但仍真实相交。**没有 STATIC_PASS，未进入阶段2，没有连续动画批准。**

- {link('OVERHEAD_BEFORE_AFTER_ANNOTATED.png')}：正式 STAGE_C_OVERHEAD 同相机原 C1 / 第三轮。
- {link('ARTIST_AUX_INDEX_SIDE_BEFORE_AFTER_ANNOTATED.png')}：推荐优先看，能辨认食指末端与黑键前角；仍有残余穿入。
- {link('SIDE_OBLIQUE_BEFORE_AFTER_ANNOTATED.png')}：原场景侧斜视，保留整体手型。
- {link('ROUND_3_STATIC_NOT_APPROVED.blend')}：重新打开后查看 **2.600000s / frame 157**。静态姿态已独立复现；不要将附近未验收曲线当作修复动画。
- {link('TECHNICAL_REPORT.md')}：含五个指定问题的回答。
- {link('QUANTITATIVE_ACCEPTANCE.csv')}；{link('SAVED_REOPEN_STATIC_VALIDATION.json')}。
- {link('PROTECTED_SHA256_BEFORE_AFTER.json')}。

Human 待判断：食指向中指侧收拢的程度、MCP 接近伸展端、PIP/DIP 弯曲弧度及俯视辨识度是否合理。这些只是 Codex 初步观察，没有 Human 自然度批准。红圈是实际内部三角面见证投影，不表示该点应在原渲染中裸露可见。

三轮文件和第一轮拒绝证据保留；不再改姿态、不动手掌、不追加第四轮，不扩展到 0.433s 或其他指。阶段1未成功，因此没有制作连续对照视频。

STOP — HUMAN REVIEW
'''
with (OUT/'HUMAN_REVIEW.md').open('x',encoding='utf8') as f:f.write(human)
deliver=['TECHNICAL_REPORT.md','HUMAN_REVIEW.md','QUANTITATIVE_ACCEPTANCE.csv','RESULT.json','ROUND_3_STATIC_NOT_APPROVED.blend','SAVED_REOPEN_STATIC_VALIDATION.json','PROTECTED_SHA256_BEFORE_AFTER.json',*images]
save('FINAL_DELIVERY_MANIFEST.json',dict(result='PARTIAL',static_pass=False,phase2_executed=False,files=[dict(path=str(OUT/n),sha256=sha(OUT/n)) for n in deliver],stop='STOP — HUMAN REVIEW'))
print('STATIC_DELIVERY_COMPLETE',json.dumps(dict(result='PARTIAL',static_pass=False,phase2=False,original_depth=basepeak,best_depth=newpeak,previous_fixed_depth=oldpeak,protected=len(receipts),all_unchanged=True),ensure_ascii=False),flush=True)
