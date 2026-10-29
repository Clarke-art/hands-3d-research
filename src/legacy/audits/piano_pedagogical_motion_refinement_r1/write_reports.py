import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent
def read(n):return json.loads((P/n).read_text(encoding='utf8'))
def save(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
def doc(n,x):(P/n).write_text(x,encoding='utf8')
gen=read('GENERATION_RECEIPT.json');bake=read('BAKE_RECEIPT.json');a=read('ACTUAL_VALIDATION.json');neighbor=read('NEIGHBOR_REGRESSION_CHECK.json');assets=read('SCENE_ASSET_IDENTITY.json');total=gen['seconds']+bake['seconds'];assert total<300
worst=sorted(a['active_pads'],key=lambda r:r['pad_change_mm'],reverse=True)[:6]
probes=[min(a['rows'],key=lambda r:abs(r['time']-t)) for t in [1.133333333,3.825,2.6,4.05,4.916666667]]
regressions=[]
for r in a['rows']:
 old={(h['digit'],h['midi']):h['depth_mm'] for h in r['source']['black_hits']}
 for h in r['new']['black_hits']:
  change=h['depth_mm']-old.get((h['digit'],h['midi']),0)
  if change>.3:regressions.append(dict(time=r['time'],digit=h['digit'],key=h['key'],source_depth_mm=old.get((h['digit'],h['midi']),0),new_depth_mm=h['depth_mm'],increase_mm=change))
save('ENGINEERING_DIAGNOSTICS.json',dict(overall='FAIL',reason='Strict source active skin preservation tolerance failed at two NOTE_OFF boundaries; threshold retained, not relaxed.',joint_domain='PASS',actual_key_contact='PASS_FINITE_SAMPLES',source_contact_drift_gate='FAIL',source_contact_drift_limit_mm=.25,worst_drift_mm=a['active_pad_change_max_mm'],worst_rows=worst,source_and_new_contact_gap_range_mm=[min(r['new']['gap_mm'] for r in a['active_pads']),max(r['new']['gap_mm'] for r in a['active_pads'])],max_target_horizontal_mm=max(r['new']['horizontal_mm'] for r in a['active_pads']),joint_limit_float_residual_deg=a['engineering_max_violation_deg'],added_velocity_deg_sec=a['added_velocity_max_deg_sec'],source_peak_velocity_deg_sec=a['peak_joint_velocity_source_deg_sec'],new_peak_velocity_deg_sec=a['peak_joint_velocity_new_deg_sec'],left_root_key_actions_unchanged=a['protected_actions_unchanged'],native_assets=assets,adjacent_pair_regression_summary=neighbor['summary'],new_pair_types=neighbor['new_intersection_pair_types'],black_key_depth_regressions=regressions,probes=probes,full_23_note_reaudit=False,review_scope='Changed right local curves; right active marker drift at 60Hz and boundaries, preserved action identities for other assets. Historical 23-note mapping/left qualification reused.'))
doc('PEDAGOGICAL_REPAIR_SCOPE.md','''# 教学动作修复范围 R1

本轮实际修复，不是仅再次审计。唯一母版为 Lightweight R1：SHA256 `18d3c729ff16759a4a7b41a621a1682711d876ad2e109a748d1ea9e675762df3`；Action `DESIGN_ONLY_LIGHTWEIGHT_R1_RIGHT_JOINTS_NOT_APPROVED`。

直接复用上一轮23音符映射、左手资格、事件与教学问题；不重新求解全段双手。

- B01：1.10–1.42s 中指/无名指准备交替，保护A4食指和B4中指的真实NOTE_ON/OFF区间。
- B02：3.73–3.87s 无名指离开D5、准备F♯5，中指触E5。D5 在3.778568s结束，此后释放自由度可用，没有错误强制持续持键。
- B03：2.600s 食指/A♯4、4.050s 中指/D♯5、4.916667s 无名指/C♯5；同时考虑其他四根指与附近真实抬高黑键实体。

修正空间为食指/中指/无名指的MCP、PIP、DIP和MCP横展共12个工程坐标。局部时间支持窗为0.90–1.78、2.25–2.95、3.50–4.35、4.55–5.40s，边缘120ms平滑；窗内仍按真实事件保护主动指。支持窗是缺陷定位范围，不是逐音符手工pose。位置/角度由通用邻指与键体几何代价产生。

原root、左手、拇指、小指、琴键Action、MIDI、指法、音频、相机、网格、Rig、权重和Corrective不修改。一个正式修正过程，一个动态候选，不重跑、不选优。
''')
doc('LIGHTWEIGHT_MOTION_REPAIR.md',f'''# 轻量修正实现

CONTACT_GUIDED_LIGHTWEIGHT_ANIMATION。一次固定策略的局部坐标探测，未调用非线性IK/重型全手优化。

从实际Lightweight Blend读出120Hz工程角、骨骼quaternion、rig world与键轴角；旧工具只复用冻结rest/weights/FK代码，不复用旧动态轨迹。五个只读几何探针的模型误差最大0.000737mm，没有预检姿态搜索。

60Hz局部修正以当前实际skin局部包络、附近真实运动黑键实体和其他手指为约束。固定4°/2°/1°探测、每级三轮，偏离原风格与前帧增量受惩罚；不按音符设置人工角度。接触区间NOTE_ON−15ms至NOTE_OFF保护；释放55ms渐入、准备90ms渐出。一次时域滤波和速度投影属于本次修正过程。

原quaternion细节保留，只有9根局部骨骼36条旋转通道写入派生Action；其余通道payload精确保留。以原有键帧及120Hz样本烘焙成唯一DESIGN_ONLY Blend。

- 数值修正：{gen['seconds']:.6f}s。
- 烘焙/导出：{bake['seconds']:.6f}s。
- 正式修正总计：{total:.6f}s，低于300s上限；验证、渲染、编码另计。
- 局部完整FK/skin候选评价：{gen['local_fk_evaluations']} 次，{gen['batched_calls']}批。
- 烘焙局部关节旋转矩阵构造：{bake['samples']*6} 次（不是追加IK搜索）。
- IK优化器调用0；重型求解0；新动态候选1。

最大修正约7.98°，新增采样角速度峰值153.75°/s；工程角域通过。严格主动指腹保持门限0.25mm在两处NOTE_OFF边界失败，最大0.283404mm。该门限未放宽，未重新烘焙、未改参数再求解。结果保持FAIL_CLOSED。

预检时共享模块导出的路径变量曾导致3个新临时文件写入旧工具目录，随后已移入本轮目录并修正脚本路径变量；不存在覆盖既有文件，冻结清单前后复核。此问题发生在正式修正前，不构成第二次动作尝试。
''')
doc('BEFORE_AFTER_TEACHING_REVIEW.md','''# 新旧教学动作对照

旧：本轮指定Lightweight R1。新：本轮唯一实际保存的Pedagogical Refinement R1。全部对照同相机、同时间、同画幅和比例。

|问题|实际几何旧→新|原视角判断|结论|
|---|---|---|---|
|B01 1.133333333s|中/无名指相交面配对39→0；1.10–1.42s累计723→140|局部分离改善，但两指投影仍贴近，其他帧还有残余；不宣称完全解决|IMPROVED|
|B02 3.825s|93→81；3.73–3.87s累计495→436|仍能看到两指交叉/融合，暂停示范仍不合格；数量减少不足以叫可见教学修复|NOT_IMPROVED|
|B03 食指/A♯4 2.600s|内部深度4.427→0.470mm|接触明显减轻，浅残余仍需Human判断|IMPROVED，未RESOLVED|
|B03 中指/D♯5 4.050s|5.469→2.938mm|嵌入残余仍会影响指尖路径理解|IMPROVED，仍有阻断风险|
|B03 无名指/C♯5 4.916667s|2.915→0.275mm|端部与键的关系改善；不能等同全程无穿键|IMPROVED，未RESOLVED|

计数是相交面配对，不是体积、穿透深度或主观分数；B01/B02使用同一实际distal skin范围。更宽回归ROI的峰值/帧数不能与本表混用。

检查了新候选真实原视角关键帧，没有发现因修正新增的夸张V形外展或严重钩爪；连续自然度仍HUMAN_PENDING。1×、0.5×、0.25×均提供同一动作媒体，未声称机器静帧观察已代替Human完整慢放观看。

九种局部邻指组合没有新增相交类型，但不能宣称没有任何新穿模：4.866667s无名指/D♯5出现旧样本未命中的0.917mm内部接触；4.783333s该对深度0.431→1.065mm；3.650s中指/D♯5也加深约0.480mm。俯视帧0292对照未显示足以单独认定严重错误的清晰证据，暂为WARN/可见影响待Human，不把它隐藏成“全部改善”。页面可定位该回归点。

严格指腹源保持门限在R03 NOTE_OFF与R11 NOTE_OFF失败，分别0.258821mm和0.283404mm；实际触键没有越出目标面，接触间隙仍在母版范围。保持该失败记录，不通过自动改阈值放行。

仍可能误导初学者：晚段中指/无名指交叉、D♯5残余嵌入，以及早段其他帧的剩余贴合。W01/W02及先前8个UNKNOWN没有被本轮重新认证。

视频与图：HUMAN_REVIEW.html；15组原相机关键图、3视角原速、3视角完整同期对照、0.5×/0.25×完整教学视频、5段局部0.5×同期对照。所有新媒体标注DIAGNOSTIC_ONLY / NOT_APPROVED。

STOP — HUMAN REVIEW。下一次动作修正必须是另一个明确授权阶段。
''')
doc('MOTION_AND_CONTACT_PRESERVATION.md',f'''# 动作、触键与音乐保持

23音符原事件/指法保持：右16、左7；源MIDI SHA256 `fd87a6673e18104047842a1c858d2c9d8eb9ad845d7a8fa46e3664b17642cb75`。复用上一轮46个事件核对结论。本轮预检再次核对原MIDI哈希，没有重编事件、节奏或速度。

音乐5.142852s；共同视频5.95s/357帧/60fps，lead 0.35s。所有非右手rig对象Action的name/slot/keyframe payload完整一致，包含左手、双root、13个活动琴键。右手拇指/小指和其他未修改通道精确一致。原WAV直接用于全部原速和完整同期对照，慢放导出静音且明确标注。

改动关联的右手主动skin在60Hz及事件边界检查：横向超出目标可奏区域最大0mm；新旧完整接触间隙范围均约−0.829至2.046mm。没有新增明显悬空或错键证据。左手7音由完整Action及173场景原生资产一致性继承，不重新大规模审计。

主动指并非所有子帧绝对不动：R03 NOTE_OFF 1.4214275s发生0.258821mm源偏移（新间隙0.903889mm）；R11 NOTE_OFF 3.9928535s发生0.283404mm源偏移（新间隙0.644380mm）。这超过已采用0.25mm保持门限，严格保持检查FAIL。其余60Hz主动样本无这类大于0.25mm偏移。疑似事件边界与原键帧/新增采样的线性插值影响，但本轮不追查或修复、不进行第二次烘焙。

ACTIVE_KEY_CONTACT = PASS（有限实际skin/运动键面意义）；STRICT_SOURCE_CONTACT_PRESERVATION = FAIL。两者分别记录，不能把几何距离较小当作通过严格保持门禁。

关节工程域浮点残差{a['engineering_max_violation_deg']:.12f}°，小于0.002°数值容差；速度峰值原{a['peak_joint_velocity_source_deg_sec']:.3f}°/s、新{a['peak_joint_velocity_new_deg_sec']:.3f}°/s。没有严重速度跳变的采样证据，不证明连续加速度或教师自然度通过。

唯一新Blend SHA256：`{read('SCENE_MANIFEST.json')['sha256']}`。原母版、冻结资产和历史记录逐文件最终哈希结果见ASSET_PRESERVATION.json。
''')
save('FINAL_STATUS.json',dict(NEW_MOTION_ACTUALLY_GENERATED='YES',LIGHTWEIGHT_REPAIR_TIME_SEC=total,NUMERICAL_CORRECTION_TIME_SEC=gen['seconds'],BAKE_TIME_SEC=bake['seconds'],B01_EARLY_FINGER_CROSSING='IMPROVED',B02_LATE_FINGER_CROSSING='NOT_IMPROVED',B03_BLACK_KEY_INTERFERENCE='IMPROVED',ACTIVE_KEY_CONTACT='PASS',ACTIVE_CONTACT_SCOPE='Finite actual skin samples remain in target footprint and source contact range; not exact zero-drift',STRICT_SOURCE_CONTACT_PRESERVATION='FAIL',DUAL_HAND_MUSIC_FUNCTION='PASS',SLOW_MOTION_TEACHING_READABILITY='HUMAN_PENDING',ENGINEERING_DIAGNOSTICS='FAIL',JOINT_ENGINEERING_DOMAIN='PASS',NEW_DYNAMIC_CANDIDATES=1,NEW_HEAVY_SOLVER_CALLS=0,FK_SKIN_EVALUATIONS=gen['local_fk_evaluations'],IK_OPTIMIZER_CALLS=0,FROZEN_ASSETS_UNCHANGED='PENDING_FINAL_HASH',FINAL_STATUS='FAIL_CLOSED',DELIVERY_CLASS='DIAGNOSTIC_ONLY / NOT_APPROVED / HUMAN_PENDING',STOP='HUMAN REVIEW',remaining=['B02 visible crossing','B03 middle/D#5 residual','B01 residual frames','two NOTE_OFF source-pad-drift guard failures','new local D#5 contact samples; perceptual significance pending'],candidate_sha256=read('SCENE_MANIFEST.json')['sha256'],second_motion_attempt=False,professional_fingering='DESIGN_PROVISIONAL',historical_unknown_notes_not_reapproved=True))
doc('FINAL_ANSWERS.md',f'''# 最终15问

1. Q1：是，实际生成唯一新Action、Blend和新媒体，不是仅重新审核。
2. Q2：B01局部改善；主证据相交39→0，窗口仍有残余，不宣称RESOLVED。
3. Q3：B02未取得足以消除教学误导的可见改善；93→81不能代替可见正确性，仍穿指。
4. Q4：B03三个重点内部深度均下降，分别4.427→0.470、5.469→2.938、2.915→0.275mm；未完全消除。
5. Q5：实际目标接触范围保持，未见新增明显悬空/错键；但两处NOTE_OFF的0.25mm源保持门限失败，最大0.283404mm，不能声称主动指绝对不变。
6. Q6：已提供同一实际动作0.5×/0.25×媒体。关键暂停仍有错误；连续清楚自然与否HUMAN_PENDING，未自行批准。
7. Q7：未发现新增邻指相交组合或明显悬空；存在新的D♯5局部命中和局部深度退化。未看到严重新钩爪，专业自然度仍待判断。
8. Q8：原23音、指法、NOTE_ON/OFF、琴键Action、统一时间轴和原WAV保持。
9. Q9：左手批准Action完整payload保持，原文件不变。
10. Q10：数值修正{gen['seconds']:.6f}s + 烘焙{bake['seconds']:.6f}s = {total:.6f}s；渲染/验证/编码另计。FK/skin评价{gen['local_fk_evaluations']}次。
11. Q11：是；重型求解0、IK优化0、无逐音符人工姿态补丁；有限局部坐标探测仅在唯一正式尝试内执行。
12. Q12：是，只有一个派生动态候选，没有自动第二轮修正或重新烘焙择优。
13. Q13：晚段穿指、D♯5残余、早段其他帧贴合仍可能误导。新增浅层局部键体命中待Human判断；原WARN/UNKNOWN不自动升级。
14. Q14：冻结原生资产173对象一致；最终文件哈希保护结果见ASSET_PRESERVATION.json及FINAL_STATUS.json。
15. Q15：可提交Human观看真实修复结果及慢放对照，但只作DIAGNOSTIC_ONLY / NOT_APPROVED。最终FAIL_CLOSED，不能提交为已满足所有门禁的正式教学候选。

STOP — HUMAN REVIEW。
''')
print('REPORTS_WRITTEN',total)
