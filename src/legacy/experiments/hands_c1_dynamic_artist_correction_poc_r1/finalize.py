from common import *
import csv,datetime
import numpy as np
A=read(OUT/'CANDIDATE_1_FIXED_VALIDATION.json');B=read(OUT/'CANDIDATE_2_FIXED_VALIDATION.json');base=read(OUT/'BASELINE_DENSE_GEOMETRY.json')
media=read(OUT/'MEDIA_QC.json');reopen=read(OUT/'FINAL_REOPEN_SUBFRAME_VERIFICATION.json');summary=B['summary']
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
result='PARTIAL'
if summary['target_illegal_samples']==0 and summary['new_self_samples']==0 and summary['new_cross_samples']==0 and summary['all_regression_samples']==0 and summary['contact48_pass']==48 and summary['max_domain_violation_deg']<1e-4 and not summary['dense_active_contact_failures']:
 result='DYNAMIC_MACHINE_PASS_PENDING_HUMAN'
target_indices=[i for i,t in enumerate(base['times']) if 2.45-1e-10<=t<=2.92+1e-10]
def peak(rows,key,field='keys'):
 return max((r[field].get(key,{}).get('depth_mm',0) for r in rows),default=0)
baserows=[dict(time=t,keys=cols) for t,cols in zip(base['times'],base['collisions'])]
targetbase=[baserows[i] for i in target_indices];target=[B['rows'][i] for i in target_indices]
base26=baserows[int(np.argmin(abs(np.array(base['times'])-2.6)))];cand26=summary['exact_2_6']
geotable=[]
for key in ['A#4','A4','C#5','G4']:
 rr=[r for r in summary['exact_2_6_clearances'] if r['key']==key]
 geotable.append(dict(key=key,baseline_2_6_mm=base26['keys'].get(key,{}).get('depth_mm',0),candidate_2_6_mm=cand26['keys'].get(key,{}).get('depth_mm',0),candidate_2_6_pairs=cand26['keys'].get(key,{}).get('pairs',0),candidate_2_6_clearance_mm=min([r.get('exact_clearance_mm',0) for r in rr],default=0),baseline_window_peak_mm=peak(targetbase,key),candidate_window_peak_mm=peak(target,key)))
regress=[dict(time=r['time'],keys=r['regressions']) for r in B['rows'] if r['regressions']]
g4_dense=[ct for r in B['rows'] for ct in r['contacts'] if ct['key']=='G4']
g4_fail=sum(not ct['pass_'] for ct in g4_dense)
selfrows=[dict(time=r['time'],pairs=r['new_self']) for r in B['rows'] if r['new_self']]
limits=[dict(time=r['time'],candidate=r['domain_violation_deg'],baseline=r['baseline_domain_violation_deg']) for r in B['rows'] if r['domain_violation_deg']>max(1e-4,r['baseline_domain_violation_deg']+1e-4)]
before=read(OUT/'PROTECTED_BEFORE.json')['files'];protected={r['path']:r['sha256'] for r in before}
for name in ['SESSION_INPUT_RECEIPT.json','DENSE_VALIDATION_INPUT_RECEIPT.json','RENDER_DELIVERY_INPUT_RECEIPT.json','MEDIA_INPUT_RECEIPT.json','FINAL_REOPEN_INPUT_RECEIPT.json']:
 for row in read(OUT/name)['files']:
  p=row['path'];h=row['before'];assert p not in protected or protected[p]==h;protected[p]=h
receipts=[dict(path=p,before=h,after=sha(p),unchanged=sha(p)==h) for p,h in protected.items()]
assert all(r['unchanged'] for r in receipts)
save('PROTECTED_INPUTS_SHA256_BEFORE_AFTER.json',dict(all_unchanged=True,count=len(receipts),files=receipts,piano_directory_access=False,scope='Exact protected inputs and actual read dependencies only; no historical directory scan. Native rig/rest/mesh/weights/corrective and nonedited Action payloads also compared in Blender.'))
save('REGRESSION_DETAILS.json',dict(key_depth_regressions_over_0_02mm=regress,new_self=selfrows,new_joint_limit_violations=limits,dense_contact_failures=summary['dense_active_contact_failures']))
with (OUT/'QUANTITATIVE_RESULTS.csv').open('x',encoding='utf8',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=list(geotable[0]));writer.writeheader();writer.writerows(geotable)
ledger=read(OUT/'CANDIDATE_2_FIXED_EDIT_LEDGER.json')
timekeys=', '.join(f'{t:.6f}' for t in ledger['times'])
def link(name):return f'[{name}](<{(OUT/name).as_posix()}>)'
table='\n'.join(f"| {r['key']} | {r['baseline_2_6_mm']:.6f} | {r['candidate_2_6_mm']:.6f} | {r['candidate_2_6_pairs']} | {r['candidate_2_6_clearance_mm']:.6f} | {r['baseline_window_peak_mm']:.6f} | {r['candidate_window_peak_mm']:.6f} |" for r in geotable)
candidate_table='\n'.join(f"| {n} | {d['summary']['target_illegal_samples']}/{d['summary']['target_samples']} | {d['summary']['contact48_pass']}/48 | {d['summary']['new_self_samples']} | {d['summary']['max_domain_violation_deg']:.6f} |" for n,d in [(1,A),(2,B)])
report=f'''# HANDS_C1_DYNAMIC_ARTIST_CORRECTION_POC_R1

**{result} — STOP — HUMAN REVIEW**。{stamp}。候选2是最终交付；不是正式教学片批准，未合并原C1。

本轮通过Blender MCP直接调整现有Pose Bone，做出了可重新打开的进入、保持、退出动画；但是目标窗口仍有非法几何关系，尚未完成合格的连续纠错。没有开发IK、运动规划器、参数扫描或自动纠错Agent。只制作两个有差异的动画设计；停止继续调参。

## 优先交付

- {link('C1_VS_REPAIRED_OVERHEAD_1X.mp4')}
- {link('C1_VS_REPAIRED_OVERHEAD_0_5X.mp4')}
- {link('C1_VS_REPAIRED_SIDE_1X.mp4')}
- {link('DYNAMIC_CANDIDATE_NOT_APPROVED.blend')}（打开看frame157 / 2.600000s，然后播放frame127–202）
- {link('HUMAN_REVIEW.md')}

## 编辑与边界

原C1独立副本起步。先做两次定向静态参考：A仍穿A#4 2.276981mm；B无非法键相交，A#4精确净空0.924226mm，G4 pad gap0.959968mm，无新增自交/跨手。B与上轮被否决姿态不同；没有复制上轮静态骨矩阵。Codex观察正式俯视、侧视及辅助局部侧视后，未见明显新增极端折角，故进入连续关键帧阶段；这不是Human自然性批准。

实际修改右手 `WRIST_R` location / rotation_quaternion，以及 `INDEX_MCP_R/PIP_R/DIP_R`、`MIDDLE_MCP_R/PIP_R/DIP_R` rotation_quaternion；其他骨曲线保持。腕骨静态参考是绕原G4拇指pad枢轴世界X+4°、Y−6°并后收6mm的直接摆放，再转换成腕骨局部关键帧；没有改root对象、结构、rest、scale通道、网格、权重或corrective。

编辑时间 **2.200000–3.120000s**。作者控制时间共10个：{timekeys}。每条编辑通道10个Bezier关键点，保留区间外原烘焙曲线；未重新烘焙全曲。原区间外曲线的值与LINEAR插值保持，邻接自动handle坐标可能被Blender重算，对LINEAR段无作用。区间外抽查曲线最大误差 {summary['outside_curve_value_max_error']:.9g}。

2.20–2.42进入；2.42–2.68保持；之后掌腕逐渐回位，2.921426仍保留15%腕修正，3.02归零；食指/中指到3.12归回原C1。起点位于R06 G4拇指持音中，食指闲置，且已离开前一D5；退出跨越R08 E5准备/初始持音，专门检测其触点，并未扩大到其他历史修复。R06时间2.064284–2.492855，R07时间2.492855–2.9214260000000003，R08 E5于2.9214260000000003开始；23音原时钟、指法、键Action不变。

候选1食指目标10/15/8/−12°，腕部较早回位；候选2为10/10/5/−12°，减小末两节钩曲并较晚回位。中指仅为退出协同，目标0/4/3°，展指约−5.802°。具体权重、动作路径和所有关键时刻见 `CANDIDATE_2_FIXED_EDIT_LEDGER.json`。Bezier插值可能在关键姿态间产生超调，因此以实际求值验收，不能把作者关键角代替实际全段合法性。

初次写入出现Blender RNA关键点数组引用失效，导致旧点残留/点列表错误；未使用这些结果验收。初次 `CANDIDATE_1_NOT_APPROVED.blend`、`CANDIDATE_2_NOT_APPROVED.blend` 与初始survey保留为**无效过程证据**。修正为逆序删除并在全部插入后重新获取点引用，再以同两个设计生成 `IMPLEMENTATION_FIXED` 文件。没有新增第三个动作设计。另一次渲染manifest的numpy数组比较报错发生在全部PNG已保存后；修复元数据比较并复用原PNG，未覆写画面。日志全部保留。

## 真实几何

在2.10–3.35s共 **{summary['samples']}个实际亚帧**，240Hz基础、事件及10个关键时刻精确采样，附近±6.25ms加密960Hz；2.875–2.925危险退出段另加960Hz。完整目标2.45–2.92s有{summary['target_samples']}样本。所有实际受影响右手皮肤（含混合蒙皮掌腕、各指）对88键实际组件先AABB排除远键，再BVH真实三角面相交和真实三角面/凸键体内部深度证书；逐次确认实际键顶点等于注册几何经原Action的实际变换。不是pad/骨代理。指间/整手自交及跨手用完整三角网格；左手皮肤单独比对。

| 键 | 原2.6穿入mm | 候选2.6穿入mm | 候选2.6面对 | 候选2.6净空mm | 原目标窗最大深度mm | 候选目标窗最大深度mm |
|---|---:|---:|---:|---:|---:|---:|
{table}

G4的键体相交须单独按活动目标解释，不能宣称场景绝对零相交；活动身份不豁免A4等邻键。正净空仅在2.6秒对A#4/A4/C#5以顶点–面与完整边–边最小距离复核；G4净空列的0不代表相交深度0。

候选2目标窗口有 **{summary['target_illegal_samples']}/{summary['target_samples']}个样本存在非目标键相交**，最早{summary['target_first_illegal']}，最晚{summary['target_last_illegal']}。最大非法见证：`{summary['target_illegal_peak']}`。因此没有消除整个目标窗口的非法穿模。全部逐帧键深度、面对和见证顶点保留于 `CANDIDATE_2_FIXED_VALIDATION.json`。

| 动画设计 | 目标非法样本 | 48触点PASS | 新自交样本 | 最大关节越界° |
|---|---:|---:|---:|---:|
{candidate_table}

## 演奏、连续性与回退

原右手16音ON/HOLD/PRE_OFF共48点：原 {summary['baseline_contact48_pass']}/48、候选 {summary['contact48_pass']}/48。密集实际活动触点失败时间样本数 **{len(summary['dense_active_contact_failures'])}**。G4拇指、两次相邻G4时钟及E5准备按原3mm垂向、0.03mm横向及inside合同检查，没有放宽容差；点PASS不替代整指正确落指或真实网格碰撞。所有23音的原始数据与键Action内容哈希保持。

完整上下文新/加深键体深度（超过原值0.02mm，仅作回退记账阈值，零碰撞标准未放宽）{summary['all_regression_samples']}个样本，其中目标窗{summary['target_regression_samples']}。新自交样本{summary['new_self_samples']}，新增跨手{summary['new_cross_samples']}。左手最大真实皮肤差{summary['left_max_delta_mm']:.9g}mm。关节原域最大越界{summary['max_domain_violation_deg']:.6f}°，原基线最大{summary['max_baseline_domain_violation_deg']:.6f}°；新增越界样本{len(limits)}。详细回退、关节及触点失败见 {link('REGRESSION_DETAILS.json')}，不得用2.6秒静态PASS掩盖。

实际全手关节峰值速度{float(np.max(summary['max_joint_speed_deg_s'])):.3f}°/s，原峰值{float(np.max(summary['baseline_max_joint_speed_deg_s'])):.3f}°/s；新增差值峰值{float(np.max(summary['max_added_joint_speed_deg_s'])):.3f}°/s。腕骨最大平移速率{summary['max_wrist_speed_mm_s']:.3f}mm/s，皮肤点最大速率{summary['max_skin_speed_mm_s']:.3f}mm/s（含原动作，不能等同新增量）。Bezier曲线位置连续，未插入瞬时复位；但速度、超调及退出仍需结合回退和视频判断，不宣称自然连续验收通过。

最终交付Blend再独立打开，检查事件、关键点及两侧亚帧共{len(reopen['samples'])}个，完整皮肤与保存前密集结果最大差{reopen['max_skin_delta_mm']:.9g}mm、关节最大差{reopen['max_joint_delta_deg']:.9g}°。最终文件与候选2字节一致，可复现真实动画。有限离散采样不构成数学连续安全证明。

## 视频及自然性边界

同时间左右并排，实际正式正交教学相机及原辅助侧相机矩阵/尺度逐项一致；没有隐藏物体或改动几何画面。每侧原渲染1280×720，完整放入2560×816画布，额外区域只放标题/时码。源frame127–202，即2.10–3.35s；容器因包含末帧保持，共76帧、1.266667s；0.5X逐帧复制，共152帧、2.533333s，60fps。完整解码、无黑帧、视频/音频起点和时长已核对，慢速帧floor(j/2)最大低分辨率MAE{media['all_slow_frame_mapping_max_MAE']:.6f}。

音轨来自Hands内原C1 WAV；原音符/MIDI不变。慢速采用保音高atempo=0.5，补偿首次起音延迟{media['full_waveform_delay_samples']/48:.3f}ms，再按双倍时间裁切。R07 G4和R08 E5局部能量上升相对理想双倍时间分别约15/20ms偏差。这只是有限声学同步检测，不是所有复音声部的亚帧认证；未宣称真人听审已完成。详见 `MEDIA_QC.json`。

Codex逐张查看原/候选正式俯视、侧视、辅助食指侧视及6态对照，并核对整段帧序。食指与掌腕动作改变量可见，现有指根硬折面、低多边形轮廓、虎口凹折均保留；没有修复冻结皮肤缺陷。保持段相较原侵入有改善，但闲置食指保持较固定、小指随腕倾斜抬高、退出时协同及指根外观都须Human实际观看判断。机器关节/回退问题本身已阻止本轮通过，不能以皮肤原有缺陷为新增问题免责。

## 保护与五问

受保护及实际读取输入{len(receipts)}项前后SHA256一致，见 {link('PROTECTED_INPUTS_SHA256_BEFORE_AFTER.json')}。原C1哈希仍 `d8e0f5a85e71323739bfcd4de485ff7a2b4096f8e59bbd4c578ee9d76d3e51a7`。Rig/rest/网格/权重/corrective原生摘要、全部其他Action及未编辑骨曲线内容保持；原C1与23音正式成果、历史证据均未改。未访问/扫描独立piano目录，也未触及0.433秒。全体新增文件仅在本实验目录。

1. **能否直接完成完整连续纠错？** 已证明能直接制作完整可复现进入/保持/退出候选；本轮未证明能完成全部验收合格的纠错。
2. **目标非法穿模消除？** 2.6秒局部已改善/清除；整个2.45–2.92秒仍失败，不能宣布消除。
3. **G4拇指正确？** 按原活动触点合同及密集数据报告；键Action、时序不变。若有dense失败，已列出而不以48点掩盖。
4. **进入保持退出自然连续？** 有真实连续曲线和复现证据；存在机器回退/关节及潜在自然性问题，不认定通过，Human终审。
5. **值得推广另一窗口？** 直接摆姿与稀疏关键帧值得保留为人工制作方式；当前结果不足以批准复制推广。先由Human审看片和回退，另轮是否继续需新授权。本轮停止，不追加第三候选。

**STOP — HUMAN REVIEW**。
'''
report=report.replace('## 保护与五问',f"两处编辑端点的全皮肤差分别为 {reopen['joins'][0]['endpoint_skin_delta_mm']:.9f} / {reopen['joins'][1]['endpoint_skin_delta_mm']:.9f} mm（浮点求值误差量级），关节端点差均0°。腕骨保存scale为 {reopen['wrist_pose_scale']}，约6×10⁻⁸的矩阵分解舍入，未主动缩放、未创建scale曲线。\n\n## 保护与五问")
report=report.replace('按原活动触点合同及密集数据报告；键Action、时序不变。若有dense失败，已列出而不以48点掩盖。',f'保持原合同内正确：G4密集活动触点共{len(g4_dense)}点、失败{g4_fail}点；16音48点全通过；键Action、两次G4时序不变。单点触键合同不等于压力/整指落指形态批准。')
with (OUT/'TECHNICAL_REPORT.md').open('x',encoding='utf8') as f:f.write(report)
review=f'''# HUMAN REVIEW

**{result} — STOP — HUMAN REVIEW**。优先观看 {link('C1_VS_REPAIRED_OVERHEAD_1X.mp4')}，再看 {link('C1_VS_REPAIRED_OVERHEAD_0_5X.mp4')} 与 {link('C1_VS_REPAIRED_SIDE_1X.mp4')}。每段只含2.10–3.35s，左原C1、右候选2。视频名字中的REPAIRED是交付指定名称，不代表已经验收合格。

- 源2.20–2.42s（1X片内0.10–0.32s）：手掌后收/倾斜是否协调，食指是否自然过渡。
- 源2.45–2.68s（片内0.35–0.58s）：G4持键时食指是否过直、僵硬或不合理悬停；虎口与食指近节的既有硬折面是否因新姿态更显著。
- 源2.78–2.95s（片内0.68–0.85s）：掌腕退出、中指配合、小指E5准备是否自然；这里仍有真实非法相交/回退，请不要只看2.600s的安全截图。
- 源3.12s（片内1.02s）后：应回到原C1后续动作。0.5X中上述片内时间乘2。

机器结果：目标非法样本{summary['target_illegal_samples']}/{summary['target_samples']}；48触点{summary['contact48_pass']}/48，密集触点失败样本{len(summary['dense_active_contact_failures'])}；关节最大越界{summary['max_domain_violation_deg']:.6f}°；新自交{summary['new_self_samples']}、新增跨手{summary['new_cross_samples']}。完整数字和新增回退见 {link('TECHNICAL_REPORT.md')} / {link('REGRESSION_DETAILS.json')}。

辅助图 {link('CANDIDATE_AUX_HOLD.png')}、{link('CANDIDATE_AUX_EXIT.png')}；原始对照 {link('ORIGINAL_AUX_HOLD.png')}；6态整手 {link('VIDEO_REVIEW_CONTACT_SHEET.png')}。

已知冻结皮肤形态缺陷未修复，不能因此宣称新手型自然，也不能据机器碰撞改善批准教学视频。音轨慢速保音高但局部起音检测仍有约15–20ms时间偏差，未做真人听审。

最终Blend {link('DYNAMIC_CANDIDATE_NOT_APPROVED.blend')}。本轮已停止；没有合并正式C1，不再追加候选。
'''
with (OUT/'HUMAN_REVIEW.md').open('x',encoding='utf8') as f:f.write(review)
save('RESULT.json',dict(classification=result,stop='STOP — HUMAN REVIEW',time=stamp,final_candidate=2,two_animation_designs_only=True,machine_approved=False,human_approved=False,summary=summary,geometry_table=geotable,protected_inputs=len(receipts),all_protected_unchanged=True))
deliver=['C1_VS_REPAIRED_OVERHEAD_1X.mp4','C1_VS_REPAIRED_OVERHEAD_0_5X.mp4','C1_VS_REPAIRED_SIDE_1X.mp4','DYNAMIC_CANDIDATE_NOT_APPROVED.blend','TECHNICAL_REPORT.md','HUMAN_REVIEW.md','RESULT.json','PROTECTED_INPUTS_SHA256_BEFORE_AFTER.json','MEDIA_QC.json','FINAL_REOPEN_SUBFRAME_VERIFICATION.json','REGRESSION_DETAILS.json','QUANTITATIVE_RESULTS.csv']
save('FINAL_DELIVERY_MANIFEST.json',dict(classification=result,files=[dict(name=n,path=str(OUT/n),sha256=sha(OUT/n)) for n in deliver],code=[dict(name=p.name,sha256=sha(p)) for p in OUT.glob('*.py')],stop='STOP — HUMAN REVIEW'))
assert all(sha(r['path'])==r['before'] for r in receipts)
save('FINAL_POST_REPORT_CHECK.json',dict(all_delivery_hashes_correct=all(sha(r['path'])==r['sha256'] for r in read(OUT/'FINAL_DELIVERY_MANIFEST.json')['files']),protected_unchanged=True,classification=result,stop='STOP — HUMAN REVIEW'))
print('FINALIZED',result,json.dumps(dict(target_illegal=summary['target_illegal_samples'],contacts=summary['contact48_pass'],dense_contact_failures=len(summary['dense_active_contact_failures']),domain=summary['max_domain_violation_deg'],keys=geotable),ensure_ascii=False))
