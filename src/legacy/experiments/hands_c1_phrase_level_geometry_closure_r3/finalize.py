from common import *
import csv,datetime
survey=read(OUT/'BOUNDARY_AND_FINGER_SURVEY.json');dense=read(OUT/'DENSE_HANDOFF_BOUNDARY_CHECK.json')
R1=ROOT/'experiments/hands_c1_dynamic_artist_correction_poc_r1';R2=ROOT/'experiments/hands_c1_exit_handoff_correction_r2'
old=read(R2/'CANDIDATE_2_VALIDATION.json');oldsummary=old['summary']
# Protect the actually used inputs and explicitly named official MIDI/native
# assets only, not the historical tree represented by the earlier receipt.
prior_receipt=read(R2/'PROTECTED_INPUTS_SHA256_BEFORE_AFTER.json')
for r in prior_receipt['files']:
 p=Path(r['path'])
 if p.suffix.lower() in ['.mid','.midi'] or ('production_spec' in p.parts and p.suffix.lower()=='.blend'):
  assert sha(p)==r['after'];READS[str(p)]=r['after']
protected={r['path']:r['sha256'] for r in read(OUT/'PROTECTED_BEFORE.json')['files']}
for name in ['SURVEY_INPUT_RECEIPT.json','BOUNDARY_CHECK_INPUT_RECEIPT.json']:
 for r in read(OUT/name)['files']:protected[r['path']]=r['before']
protected.update(READS)
rows=[dict(path=p,before=h,after=sha(p),unchanged=sha(p)==h) for p,h in protected.items()]
assert all(r['unchanged'] for r in rows)
save('PROTECTED_INPUTS_SHA256_BEFORE_AFTER.json',dict(all_unchanged=True,count=len(rows),files=rows,scope='Actual read dependencies, R2 starting blend, sourceC1, official MIDI/native assets explicitly verified against R2 receipt. No historical directory scan.',R2_copy_exact=sha(OUT/'R2_START_ISOLATED_NOT_APPROVED.blend')==sha(R2/'EXIT_CORRECTED_NOT_APPROVED.blend'),piano_access=False))
comparison=[]
for t,key in [(3.058333333333333,'C#5'),(3.12,'C#5'),(3.349997,'C#5'),(3.5642825,'C#5'),(3.778568,'D#5'),(3.8,'D#5')]:
 a=next(r for r in survey['rows'] if r['version']=='C1' and r['time']==t);b=next(r for r in survey['rows'] if r['version']=='R2' and r['time']==t)
 comparison.append(dict(time=t,key=key,C1_depth_mm=a['illegal'].get(key,{}).get('depth_mm',0),R2_depth_mm=b['illegal'].get(key,{}).get('depth_mm',0),R3_copy_depth_mm=b['illegal'].get(key,{}).get('depth_mm',0),finger='/'.join(sorted(set(b['illegal'].get(key,{}).get('dominant_bones',[]))))))
with (OUT/'C1_R2_R3_GEOMETRY_COMPARISON.csv').open('x',encoding='utf8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(comparison[0]));w.writeheader();w.writerows(comparison)
sp=[r for r in dense['extension_rows'] if r['self_count']]
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
classification='PHRASE_BOUNDARY_BLOCKED'
lines='\n'.join(f"| {r['time']:.6f} | {r['key']} | {r['C1_depth_mm']:.6f} | {r['R2_depth_mm']:.6f} | {r['R3_copy_depth_mm']:.6f} | {r['finger']} |" for r in comparison)
def link(name):return f'[{name}](<{(OUT/name).as_posix()}>)'
report=f'''# HANDS_C1_PHRASE_LEVEL_GEOMETRY_CLOSURE_R3

**PHRASE_BOUNDARY_BLOCKED — STOP — HUMAN REVIEW**。{stamp}。

本轮完成事件/角色、真实几何及安全回接边界检查，**未进入关键帧编辑，动画设计数0**。本轮没有证明“不存在合法纠错动画”：只是在允许的既有后续动作中，未找到可安全接回且能关闭本轮编辑影响的区间。若在3.80s新造一个安全终态而未验证后续交接，仍不能称为完整短句闭合；本轮没有创建这种未闭合候选。未生成 `PHRASE_CORRECTED_NOT_APPROVED.blend` 或新的修复对照视频。

## 窗口与真实角色

R06/R07为拇指G4，分别2.064284–2.492855及2.492855–2.921426s。R08为小指E5，2.921426–3.349997；R09为中指C5，3.349997–3.5642825；R10为无名指D5，3.5642825–3.778568；R11为中指E5，3.778568–3.9928535。下一R12 F#5在3.9928535开始，仅读取事件资料，没有检查3.80s以后的姿态。

3.02s是小指E5持音中，食指/中指当时闲置；中指随后准备C5，并在3.349997s转为ACTIVE，小指进入RELEASE。3.5642825s无名指ACTIVE、中指RELEASE；3.778568s中指ACTIVE、无名指RELEASE。细分角色见 `DENSE_HANDOFF_BOUNDARY_CHECK.json`：PREPARE按既有180ms、RELEASE按既有40ms约定标注，ACTIVE严格按正式ON/OFF，未改时钟。角色约定不等于真实碰撞豁免。

不能把3.02、3.12、3.35当作固定恢复点。原C1在3.349997s的中指C5触点虽然合格，同一根手指的皮肤仍侵入C#5约2.756mm；3.5642825s仍侵入C#5约0.887mm。继续到R11 E5又出现D#5侵入和中/无名指相交。

## 同刻几何对比

单位mm；**R3列为未编辑隔离副本，不是新修复成果**。同刻原C1与R2均用实际evaluated全右手皮肤、原Action驱动的实际键网格、BVH及三角面内部深度计算。全部见证三角形、世界点、主要蒙皮骨及关节角保留在 `BOUNDARY_AND_FINGER_SURVEY.json`。

| 时间s | 非目标键 | 原C1 | R2 | R3隔离副本 | 实际涉及骨 |
|---|---|---:|---:|---:|---|
{lines}

3.02之后的A#4主要由INDEX_DIP_R末端皮肤造成；C#5早段有无名指末端参与，3.0–3.6的关键见证主要为MIDDLE_DIP_R。3.6以后还出现无名指RING_DIP_R侵入非目标E5，中指末端转入D#5。这些不是只移动一个闲置食指就能一并验收的独立问题。

原C1不含R2这次后收，3.058333s仍有C#5约3.657118mm侵入；R2约3.692315mm，其中只约0.035198mm是相对加深。说明撤销R2小位移不能消除既有严重问题。共享掌位与手指姿态共同决定实际空间关系；本轮没有进行单因素姿态试验，未推断唯一病因，也未证明必须更换Rig或皮肤。

## 回接区检查及指间关系

复用R2已验证的3.02–3.35s **107个样本**，非法琴键碰撞清零的样本为0。仅将回接搜索扩展到3.80s，追加 **144个**实际时刻：240Hz基础及事件边界附近960Hz、精确ON/OFF；安全既有回接样本为 **0/144**。这些扩展样本中每个都有非法键关系，最小的“同刻最深非法侵入”仍约0.887500mm，发生在3.5642825s。未找到可作为本轮闭合点的既有安全片段。有限离散采样不证明所有连续时刻或所有合法新姿态均不安全。

指间检测不是“新增自交0”：对完整右手网格的非相邻三角面作绝对相交计数。R2原2.10–3.35s已验证数据的绝对self_count为0；新增回接范围内 **{dense['self_intersection_samples']}个采样存在真实MIDDLE/RING相交**，首次检出{sp[0]['time']:.9f}s。3.778568s为95对，3.80s达 **147对**。这些在原C1与未编辑R2中已经存在，本轮没有新增，但也没有消除。

正式正交俯视已实际查看C5、D5、E5起音和3.80s，辅助侧视已查看上限姿态。E5起音处中指/无名指明显交叉，教学可辨认性不能通过；也不能把之前几帧真实相交0等同于整段没有视觉粘连。本轮没有完成全短句的视觉分离认证。

B01核心为1.10–1.4214275s、编辑0.90–1.705713s、预览0.90–1.75s，**与本轮不重合**。其核心87/87→0/87但整体FAIL的事实保留；未加载其Blend、未改B01、未将3.708s后的另一段MIDDLE/RING相交冒称为B01或宣称B01已解决。

## 保留、未解决与停止原因

- R2的2.45–2.92s目标0/225、三键清障、G4密集350点PASS和关节越界清零原样保留，因为实验起点仅作字节相同复制、没有关键帧编辑。
- 本轮新消除的碰撞：**无**。3.02后的严重A#4/C#5侵入和后续邻键/指间问题仍在，未把微小加深当作全部问题。
- 新增或加深回退：本轮未改动画，因此相对R2无新增。R2相对原C1原有22个加深样本仍保留，未被修复或掩盖。
- 重新打开隔离副本实际复核规定 **48/48活动触点PASS**；扩展区活动触点也无失败。关节扩展采样最大域读数约{max(r['joint_violation_deg'] for r in dense['extension_rows']):.9g}°，是原动作约3.6×10⁻⁷°浮点下界读数；未修改域或容差。pad合格并未消除已经证实的整指邻键侵入。
- 正式MIDI、23音时间/指法、所有键Action、左手、Rig/rest/蒙皮/corrective均未修改。原C1自然动作未被本轮改变，但不能据原自然性认可宣布这些几何/教学可辨认问题合格。

本轮以阶段1的边界条件停止，没有进入最多两候选的制作阶段，也没有用失败动作覆盖现有成果。要继续闭合，需要另行明确连续规划与后续持键交接范围；当前R11 E5一直持到3.9928535s，已超出3.80s检查上限。本轮没有自动扩展，不把这些证据升级为冻结资产无解结论。

## 交付与保护

诊断图：{link('BOUNDARY_C5_ON_OVERHEAD.png')}、{link('BOUNDARY_D5_ON_OVERHEAD.png')}、{link('BOUNDARY_E5_ON_OVERHEAD.png')}、{link('BOUNDARY_LIMIT_SIDE_OBLIQUE.png')}。这些是未编辑副本的真实诊断渲染，正式相机保持，没有隐藏物体、修图或制作成功视频。

{link('R2_START_ISOLATED_NOT_APPROVED.blend')}仅为R2原样副本，不是R3修复候选。保护收据 {link('PROTECTED_INPUTS_SHA256_BEFORE_AFTER.json')}，{len(rows)}项实际读取/保护输入前后SHA256一致；包含源C1、R2起点、正式MIDI/native资产及所用历史证据，没有递归扫描全部历史目录。独立piano目录没有访问，历史FAIL没有删除或改写。Blender MCP曾因上一轮进程的输出目录保护拒绝新目录写入，已改用本轮独立进程；未修改旧目录保护或旧文件。

**STOP — HUMAN REVIEW**。
'''
with (OUT/'TECHNICAL_REPORT.md').open('x',encoding='utf8') as f:f.write(report)
human=f'''# HUMAN REVIEW

**PHRASE_BOUNDARY_BLOCKED — STOP — HUMAN REVIEW**。本轮没有编辑动画，没有新修复候选或新对照视频。

优先查看 {link('BOUNDARY_E5_ON_OVERHEAD.png')} 和 {link('BOUNDARY_LIMIT_SIDE_OBLIQUE.png')}：这是原样R2副本在3.778568/3.80s的真实画面，中指/无名指已交叉，真实相交分别95/147对。不是B01窗口，也未修复B01。

再看 {link('TECHNICAL_REPORT.md')} 的同刻三方表及 {link('DENSE_HANDOFF_BOUNDARY_CHECK.json')}。3.02–3.35s已有107个样本和后续144个新检查时刻都未找到安全既有回接样本；中指C5、小指E5触点PASS不能替代整指几何正确。

需要Human决定后续是否另行授权一个覆盖后续持键/交接的连续规划范围，或在现范围内另行设计全新连接姿态及其后续验证。当前证据既不足以批准教学动画，也不证明合法新路径不存在。

R2原0/225目标成果保留，48/48触点重检通过；本轮没有新消除严重穿模，没有完整机器合格短句。冻结皮肤缺陷未修复，R2原动画自然性结论没有被本轮扩大。
'''
with (OUT/'HUMAN_REVIEW.md').open('x',encoding='utf8') as f:f.write(human)
save('RESULT.json',dict(classification=classification,stop='STOP — HUMAN REVIEW',animation_designs=0,keyframes_edited=False,source_R2_copy_exact=True,R2_target_success_preserved=True,serious_collisions_solved=False,safe_existing_boundary_found=False,extension_samples=144,safe_extension_samples=0,absolute_interfinger_self_samples=dense['self_intersection_samples'],max_interfinger_triangle_pairs=147,B01_in_scope=False,B01_status='FAIL retained',contacts48_pass=48,machine_pass=False,human_approved=False,protected_count=len(rows),time=stamp))
files=['TECHNICAL_REPORT.md','HUMAN_REVIEW.md','RESULT.json','PROTECTED_INPUTS_SHA256_BEFORE_AFTER.json','C1_R2_R3_GEOMETRY_COMPARISON.csv','BOUNDARY_AND_FINGER_SURVEY.json','DENSE_HANDOFF_BOUNDARY_CHECK.json','BOUNDARY_C5_ON_OVERHEAD.png','BOUNDARY_D5_ON_OVERHEAD.png','BOUNDARY_E5_ON_OVERHEAD.png','BOUNDARY_LIMIT_SIDE_OBLIQUE.png','R2_START_ISOLATED_NOT_APPROVED.blend']
save('FINAL_DELIVERY_MANIFEST.json',dict(classification=classification,files=[dict(path=str(OUT/n),sha256=sha(OUT/n)) for n in files],stop='STOP — HUMAN REVIEW'))
assert all(sha(r['path'])==r['before'] for r in rows)
save('FINAL_POST_REPORT_CHECK.json',dict(delivery_hashes_pass=all(sha(r['path'])==r['sha256'] for r in read(OUT/'FINAL_DELIVERY_MANIFEST.json')['files']),protected_inputs_unchanged=True,classification=classification,stop='STOP — HUMAN REVIEW'))
print('R3_FINALIZED',classification,'protected',len(rows),flush=True)
