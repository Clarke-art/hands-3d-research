from common import *
import datetime,csv
import numpy as np
R1=ROOT/'experiments/hands_c1_dynamic_artist_correction_poc_r1'
base=read(R1/'BASELINE_DENSE_GEOMETRY.json');r1=read(R1/'CANDIDATE_2_FIXED_VALIDATION.json')
one=read(OUT/'CANDIDATE_1_VALIDATION.json');two=read(OUT/'CANDIDATE_2_VALIDATION.json');s=two['summary']
reopen=read(OUT/'FINAL_REOPEN_SUBFRAME_VERIFICATION.json');media=read(OUT/'MEDIA_QC.json');metadata=read(OUT/'METADATA_RESTORATION.json')
assert all(r['unmodified_full_curve_metadata_exact'] for r in reopen['candidates'])
idx=[i for i,t in enumerate(base['times']) if 2.45-1e-10<=t<=2.92+1e-10]
def maxkey(rows,key):return max(r['keys'].get(key,{}).get('depth_mm',0) for r in rows)
bt=[dict(time=base['times'][i],keys=base['collisions'][i]) for i in idx]
orig_illegal=sum(any(k!='G4' and (v['depth_mm']>1e-6 or v['pairs']) for k,v in r['keys'].items()) for r in bt)
table=[dict(version='原C1',A_sharp4=maxkey(bt,'A#4'),A4=maxkey(bt,'A4'),C_sharp5=maxkey(bt,'C#5'),target_illegal=orig_illegal,context_regressions=0,joint_violation_deg=0.,contacts48_pass=sum(r['pass_'] for r in base['contacts48']))]
for label,data,old in [('R1候选2',r1,True),('R2最佳候选2',two,False)]:
 ss=data['summary'];rr=[data['rows'][i] for i in idx]
 table.append(dict(version=label,A_sharp4=maxkey(rr,'A#4'),A4=maxkey(rr,'A4'),C_sharp5=maxkey(rr,'C#5'),target_illegal=ss['target_illegal_samples'],context_regressions=ss['all_regression_samples'] if old else ss['context_canonical_regression_samples'],joint_violation_deg=ss['max_domain_violation_deg'],contacts48_pass=ss['contact48_pass'] if old else ss['contacts48_pass']))
strict=[dict(time=r['time'],keys=r['strict_regressions_C1']) for r in two['rows'] if r['strict_regressions_C1']]
canonical=[dict(time=r['time'],keys=r['canonical_regressions_C1']) for r in two['rows'] if r['canonical_regressions_C1']]
vsr1=[dict(time=r['time'],keys=r['strict_regressions_R1']) for r in two['rows'] if r['strict_regressions_R1']]
peak=max([dict(time=r['time'],key=k,**v) for r in strict for k,v in r['keys'].items()],key=lambda r:r['increase_mm'],default=None)
classification='PARTIAL'
if s['target_illegal_samples']==0 and s['max_domain_violation_deg']<=1e-5 and s['context_strict_regression_samples']==0 and s['contacts48_pass']==48 and not s['dense_contact_failures'] and s['new_self_samples']==s['new_cross_samples']==0:
 classification='DYNAMIC_MACHINE_PASS_PENDING_HUMAN'
save('R2_REGRESSION_DETAILS.json',dict(strict_C1_0_0001mm=strict,canonical_C1_0_02mm=canonical,strict_R1_comparison=vsr1,maximum_C1_increase=peak,domain_violations=[r for r in two['rows'] if r['joint_domain_violation_deg']>1e-5],dense_contact_failures=s['dense_contact_failures']))
protected={r['path']:r['sha256'] for r in read(OUT/'PROTECTED_BEFORE.json')['files']}
for name in ['DIAGNOSIS_INPUT_RECEIPT.json','EXISTING_VIDEO_INPUT_RECEIPT.json','VALIDATION_INPUT_RECEIPT.json','RENDER_INPUT_RECEIPT.json','MEDIA_INPUT_RECEIPT.json','REOPEN_INPUT_RECEIPT.json','FINAL_REOPEN_INPUT_RECEIPT.json','METADATA_RESTORATION_INPUT_RECEIPT.json']:
 for row in read(OUT/name)['files']:
  assert row['path'] not in protected or protected[row['path']]==row['before']
  protected[row['path']]=row['before']
receipts=[dict(path=p,before=h,after=sha(p),unchanged=sha(p)==h) for p,h in protected.items()];assert all(r['unchanged'] for r in receipts)
save('PROTECTED_INPUTS_SHA256_BEFORE_AFTER.json',dict(all_unchanged=True,count=len(receipts),files=receipts,all_R1_files_frozen=True,piano_directory_access=False))
with (OUT/'THREE_WAY_COMPARISON.csv').open('x',encoding='utf8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(table[0]));w.writeheader();w.writerows(table)
def link(name):return f'[{name}](<{(OUT/name).as_posix()}>)'
lines='\n'.join(f"| {r['version']} | {r['A_sharp4']:.6f} | {r['A4']:.6f} | {r['C_sharp5']:.6f} | {r['target_illegal']}/225 | {r['context_regressions']} | {r['joint_violation_deg']:.6f} | {r['contacts48_pass']}/48 |" for r in table)
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
report=f'''# HANDS_C1_EXIT_HANDOFF_CORRECTION_R2

**{classification} — STOP — HUMAN REVIEW**。{stamp}。

保留R1进入/保持段，只对2.68–3.12s退出进行两种局部修正。最佳为候选2；目标窗结果与上下文结果分别记账，不把局部成功当成整段合格。没有第三候选、重新烘焙、IK、参数扫描、资产修改或正式C1合并。

## 三方对比

穿入列是**2.45–2.92s全目标窗口最大内部深度mm**，不是单帧；225个目标样本，2.10–3.35s上下文501样本。上下文回退列沿用R1的相对原C1加深>0.02mm统计口径（只作三方比较，不改变零非法碰撞要求）。本轮另以0.0001mm数值分辨率列出更严格的加深清单。

| 版本 | A♯4 mm | A4 mm | C♯5 mm | 目标非法样本 | 上下文回退样本 | 最大越界° | 活动触点 |
|---|---:|---:|---:|---:|---:|---:|---:|
{lines}

## A/B/C诊断与实际编辑

**A4是拇指侧面**：2.92s见证三角形2787/1381/342，93–98%属于THUMB_IP_R，其余THUMB_MCP_R；原R1深0.577845mm。发生在回腕、G4尚未结束而E5正在准备时。没有编辑拇指骨，只通过共享腕位做毫米级避让。真实三角面/键体证据、权重和曲线handle原始值见 `EXIT_DIAGNOSIS.json`，原因计划见 `DIAGNOSIS_AND_LOCAL_PLAN.md`。

**越界是MIDDLE_MCP_R屈伸**：68样本，2.8610417–2.9210417s；2.890625s达到−0.267121466°，原合法域[0,32]°。2.86/2.921426两关键姿态均0°，FREE Bezier handle把中间曲线带入负值。本轮收平这两个平台关键点的左右handle，保留Bezier，未整段改成LINEAR。食指/中指平台的其他分量一并收平以避免非预期反向运动。

**19个旧回退**：位于3.0416667–3.11375s，原C1已有A#4/C#5侵入，R1返回曲线将其加深。食指末端对应A#4；C#5早段见无名指、后段主要为中指末端。原最高加深A#4约0.764003mm。无名指曲线保持冻结，其空间关系只能随允许的腕部变化重新验收。

候选1：腕位额外世界−X峰值1.10mm；A4/关节越界清零，但目标新增C#5最大0.167259mm、{one['summary']['target_illegal_samples']}个非法样本，拒绝作为最佳。

候选2：改为世界−X峰值0.80mm、−Y峰值1.20mm的左后方小幅退让；后收分量保持到3.02s，再平滑回至3.12s。只改WRIST_R位置/旋转及INDEX、MIDDLE的MCP/PIP/DIP旋转曲线；未新增骨自由度或局部缩放。变动关键时间2.68、2.78、2.86、2.921426、3.02、3.12s；平台收平2.86/2.921426，腕曲线3.02/3.12收平。食指/中指在3.02s接回**原C1既有曲线**，匹配该时刻值及相邻斜率；这是退出连接，不复制或合并历史失败动作。详细通道与位移见 `CANDIDATE_2_EDIT_LEDGER.json`。

2.68s及之前对R1完整皮肤最大差 **{s['preserved_entry_hold_skin_delta_mm']:.9g}mm**；2.600秒安全姿态原样保留，A#4约3.118256mm净空可继承，因为实际皮肤、琴键和时刻相同。范围外上下文采样皮肤对R1最大差 **{s['outside_skin_delta_R1_mm']:.9g}mm**。未编辑骨曲线、Pose Bone scale、native Rig/rest/蒙皮/corrective、其他Action均已精确复核。

## 验收结论与剩余问题

候选2目标窗非法样本 **{s['target_illegal_samples']}/225**；最大关节越界 **{s['max_domain_violation_deg']:.9g}°**，越界样本{s['domain_violation_samples']}。G4活动密集{s['G4_dense_count']}点、失败{s['G4_dense_failures']}；右手16音48点{s['contacts48_pass']}/48；全部密集活动触点失败{len(s['dense_contact_failures'])}。R06/R07 G4、R08 E5及23音ON/OFF/指法不变，键Action内容未改。全皮肤同时对所有邻键检查，包含E5 ON及两侧亚帧，因此不以pad替代整指落指检查；合法接触仍仅按原3mm垂向、0.03mm横向及inside合同，不声称压力/接触面积模型。

上下文相对原C1仍有 **{s['context_canonical_regression_samples']}个>0.02mm加深样本**，更严格>0.0001mm共{s['context_strict_regression_samples']}个；最大加深见证为 `{peak}`。相对R1的严格加深样本另有{s['context_R1_strict_regression_samples']}个，单独保留，不能把恢复原C1历史缺陷称为全面改善。见 {link('R2_REGRESSION_DETAILS.json')}。这部分若非零，就不能认定整段达到机器验收，亦不能因两次尝试未通过就断言所有合法退出路径不存在。未证明需要更大范围重规划，不使用STRUCTURAL_HANDOFF_CONFLICT。

新增自交{s['new_self_samples']}、新增跨手{s['new_cross_samples']}；左手皮肤最大差{s['left_max_delta_mm']:.9g}mm。最大关节速率{s['joint_speed_peak_deg_s']:.3f}°/s、相对R1新增速率峰值{s['added_joint_speed_vs_R1_peak_deg_s']:.3f}°/s；腕位峰值{s['wrist_speed_peak_mm_s']:.3f}mm/s、皮肤峰值{s['skin_speed_peak_mm_s']:.3f}mm/s（后两者包含原运动）。曲线位置连续，没有瞬间复位；实际速度与皮肤样本记录保留，不用平滑曲线的存在替代自然性判断。

复用R1已保护的原C1/R1真实求值数组及深度结果，未重做整曲诊断；对两候选分别重新打开，在相同501亚帧重新计算完整evaluated右手皮肤、实际Action驱动键体、BVH与三角面内部深度，复核全皮肤自交/跨手。两候选再独立重开共{sum(len(r['samples']) for r in reopen['candidates'])}个关键/事件及相邻亚帧，最大皮肤差{max(r['max_skin_delta_mm'] for r in reopen['candidates']):.9g}mm、关节差{max(r['max_joint_delta_deg'] for r in reopen['candidates']):.9g}°。有限240Hz/高风险960Hz采样不构成连续时间数学安全证明。

## 视频与Human判断

{link('C1_VS_EXIT_CORRECTED_OVERHEAD_1X.mp4')}；{link('C1_VS_EXIT_CORRECTED_OVERHEAD_0_5X.mp4')}；{link('C1_VS_EXIT_CORRECTED_SIDE_1X.mp4')}。

正式正交俯视及侧视相机与原C1参数逐项相同，未隐藏物体、改模型或修改渲染画面。C1画面复用R1已校验的原C1同帧渲染，候选全部从本轮保存Blend重新渲染。每侧1280×720完整置于2560×816对照画布，标题仅在画面外。源frame127–202 / 2.10–3.35s；1X76帧1.266667s，0.5X152帧2.533333s，均60fps。完整解码、无黑帧、时长/起点/慢速floor(j/2)映射通过，最大低分辨率MAE {media['slow_mapping_max_MAE']:.6f}。音轨复用R1原WAV裁切与保音高慢速波形，重新核对解码相关性及完整覆盖；保留已测15/20ms局部起音偏差，不称为全音符亚帧声学认证或真人听审。

已查看两轮正式俯视/侧视退出画面和6态对照。新的腕部退让幅度很小，G4→E5手型整体接近R1；中指平台不再负向超调。但闲置指的回收、E5前准备、小指随腕的整体运动，以及原有食指根部/虎口硬折面仍需Human审看。冻结网格缺陷未修好；本轮没有凭原有缺陷为新增回退免责，也没有宣布自然性通过。

## 保护与停止

{len(receipts)}项受保护/读取输入前后SHA256一致，包含R1目录全部文件；见 {link('PROTECTED_INPUTS_SHA256_BEFORE_AFTER.json')}。原C1仍为d8e0f5a85e71323739bfcd4de485ff7a2b4096f8e59bbd4c578ee9d76d3e51a7；R1起点仍为0afd1b6a0997b62dd0311f61ce44add5a8e0147d441a29556f51dc6bd7993cad。未访问独立piano目录，未修0.433秒，未写入R1或正式资产。启动/脚本错误及一次缓存读取性能重启日志全部保留；重启未产生额外动作设计，只有两个实际候选。

最佳真实动画 {link('EXIT_CORRECTED_NOT_APPROVED.blend')}，打开看frame157并播放frame127–202。**STOP — HUMAN REVIEW**。
'''
report=report.replace('## 保护与停止','最终保护复核发现36条未编辑LINEAR通道的闲置handle横坐标被FCurve.update作浮点重算，关键值、LINEAR插值和实际关节角均未变。为满足冻结约束，已从未改动R1 Action重建，仅转入允许通道；两设计所有501个全皮肤/关节样本与原验收值差均严格0，所有未编辑通道完整metadata已恢复。原候选和初次最终文件均保留；这不是第三个动作设计。最终Blend的字节哈希更新，视频几何仍是完全相同的求值函数，证明见 `METADATA_RESTORATION.json`。\n\n## 保护与停止')
with (OUT/'TECHNICAL_REPORT.md').open('x',encoding='utf8') as f:f.write(report)
human=f'''# HUMAN REVIEW

**{classification} — STOP — HUMAN REVIEW**。本轮两次局部尝试已停止，未合并正式C1。

先看 {link('C1_VS_EXIT_CORRECTED_OVERHEAD_1X.mp4')}，再看 {link('C1_VS_EXIT_CORRECTED_OVERHEAD_0_5X.mp4')}、{link('C1_VS_EXIT_CORRECTED_SIDE_1X.mp4')}。左原C1、右本轮候选2；源时间2.10–3.35s，视频名CORRECTED不代表正式验收批准。

- 源2.78–2.92s（1X片内0.68–0.82s）：拇指持G4期间的微小左后方退让是否放松；食指悬停和中指平台是否自然。
- 源2.921426–3.02s（片内0.821–0.92s）：小指E5准备/触键、食指/中指接回原动作是否协调，有无仓促回收。
- 源3.02–3.12s（片内0.92–1.02s）：后收位移消退与既有黑键问题。即使目标窗归零，也必须结合上下文回退表审核。

0.5X中片内时间乘2。音轨保音高，已知局部能量起音偏差约15–20ms；完整时长和音轨波形已复核。

机器目标非法{s['target_illegal_samples']}/225，关节越界{s['max_domain_violation_deg']:.6f}°，48触点{s['contacts48_pass']}/48；上下文>{.02}mm加深仍{s['context_canonical_regression_samples']}个样本。若上下文非零，本轮只供审看改进和失败原因，**不能进入最终合格动作批准**。详见 {link('TECHNICAL_REPORT.md')} 与 {link('R2_REGRESSION_DETAILS.json')}。

原有食指根部、虎口和低多边形折面未修复，需判断新运动是否放大这些问题。Human视觉意见不能自动消除机器回退；机器数据也不能替代自然性审核。

最终文件 {link('EXIT_CORRECTED_NOT_APPROVED.blend')}；同时间静帧 {link('R2_TARGET_END_SIDE_OBLIQUE.png')} / {link('R1_TARGET_END_SIDE_OBLIQUE.png')}；6态视频画面 {link('VIDEO_REVIEW_CONTACT_SHEET.png')}。
'''
with (OUT/'HUMAN_REVIEW.md').open('x',encoding='utf8') as f:f.write(human)
save('RESULT.json',dict(classification=classification,stop='STOP — HUMAN REVIEW',time=stamp,best_candidate=2,designs=2,machine_approved=classification=='DYNAMIC_MACHINE_PASS_PENDING_HUMAN',human_approved=False,summary=s,comparison=table,maximum_context_regression=peak,protected_count=len(receipts),all_protected_unchanged=True))
files=['EXIT_CORRECTED_NOT_APPROVED.blend','C1_VS_EXIT_CORRECTED_OVERHEAD_1X.mp4','C1_VS_EXIT_CORRECTED_OVERHEAD_0_5X.mp4','C1_VS_EXIT_CORRECTED_SIDE_1X.mp4','TECHNICAL_REPORT.md','HUMAN_REVIEW.md','PROTECTED_INPUTS_SHA256_BEFORE_AFTER.json','THREE_WAY_COMPARISON.csv','R2_REGRESSION_DETAILS.json','FINAL_REOPEN_SUBFRAME_VERIFICATION.json','MEDIA_QC.json','METADATA_RESTORATION.json','RESULT.json']
save('FINAL_DELIVERY_MANIFEST.json',dict(classification=classification,files=[dict(path=str(OUT/n),sha256=sha(OUT/n)) for n in files],code=[dict(path=str(p),sha256=sha(p)) for p in OUT.glob('*.py')],stop='STOP — HUMAN REVIEW'))
assert all(sha(r['path'])==r['before'] for r in receipts)
save('FINAL_POST_REPORT_CHECK.json',dict(delivery_hashes_pass=all(sha(r['path'])==r['sha256'] for r in read(OUT/'FINAL_DELIVERY_MANIFEST.json')['files']),all_protected_unchanged=True,classification=classification,stop='STOP — HUMAN REVIEW'))
print('R2_FINALIZED',classification,json.dumps(dict(summary=s,peak=peak),ensure_ascii=False))
