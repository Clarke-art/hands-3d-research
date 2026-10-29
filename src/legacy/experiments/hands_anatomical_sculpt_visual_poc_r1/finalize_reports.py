import sys,json,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,o):
 with (OUT/n).open('x',encoding='utf8') as f:json.dump(o,f,ensure_ascii=False,indent=2)
def md(n,t):
 with (OUT/n).open('x',encoding='utf8') as f:f.write(t)
before={r['path']:(r['sha256'],'PREPARATION_PROTECTED_BEFORE') for r in read(OUT/'PROTECTED_BEFORE.json')}
for p in sorted(OUT.glob('*INPUT_RECEIPT.json')):
 receipt=read(p);assert receipt['all_unchanged'] and not receipt['piano_access']
 for r in receipt['files']:
  if r['path'] in before:assert before[r['path']][0]==r['before']
  else:before[r['path']]=(r['before'],p.name)
for r in read(OUT/'TOOLING_REUSE_RECEIPT.json'):before.setdefault(r['path'],(r['sha256'],'TOOLING_COPY_RECEIPT_BEFORE_SCULPT'))
oldroot=ROOT/'experiments/hands_local_skin_asset_repair_poc_r1/roi_approved_asset_trials_r1'
historical={r['path']:r['sha256'] for r in read(oldroot/'DELIVERY_SHA256.json')}
for name in ['A_BASIS_CANDIDATE_2_NOT_APPROVED.blend','B1_WEIGHTS_NOT_APPROVED.blend']:
 p=str(oldroot/name);expected=historical[p];assert sha(p)==expected
 before.setdefault(p,(expected,'PREVIOUS_TURN_DELIVERY_SHA256_BEFORE_THIS_TASK'))
checks=[]
for p,(h,origin) in before.items():
 assert Path(p).is_relative_to(ROOT) and not Path(p).is_relative_to(OUT)
 now=sha(p);assert now==h
 checks.append({'path':p,'before':h,'after':now,'unchanged':True,'before_hash_evidence':origin})
save('PROTECTED_SHA256_BEFORE_AFTER.json',{'all_unchanged':True,'count':len(checks),'piano_directory_accessed':False,'files':checks,'old_comparison_candidate_hash_note':'Their before values are the previous turn delivery manifest, not a retrospectively claimed fresh pre-read capture.'})
scope=read(OUT/'SCULPT_SCOPE_ACTIVE_BEFORE_EDIT.json')
edits={r:read(OUT/(r+'_ROUND_2_EDIT_RECEIPT.json')) for r in ['A','B']}
safe=read(OUT/'LIMITED_GEOMETRY_SUMMARY.json');compat=read(OUT/'OLD_CORRECTIVE_OFF_NORMAL_COMPATIBILITY.json')
reopen=read(OUT/'FINAL_CANDIDATE_REOPEN_RECEIPT.json');assert len(reopen)==2 and all(r['reopened_evaluated_error_mm']==0 for r in reopen)
assert all(not r['serious_geometry_regression'] for k,r in safe.items() if not k.startswith('BASE'))
assert all(r['outside_allowed_shift_mm']==0 and r['S_collar_shift_mm']==0 and r['pad_two_edge_ring_shift_mm']==0 for k,r in safe.items() if not k.startswith('BASE'))
changes={}
for r in ['A','B']:
 patch=scope['patches'][r];e=edits[r]
 changes[r]={'actual_moved_vertex_ids':e['actual_changed_vertices'],'core_moved_vertex_ids':sorted(set(e['actual_changed_vertices'])&set(patch['core_editable_vertex_ids'])),'soft_transition_moved_vertex_ids':sorted(set(e['actual_changed_vertices'])&set(patch['soft_transition_vertex_ids'])),'fixed_boundary_and_excluded_vertex_ids':patch['fixed_boundary_and_excluded_vertex_ids'],'affected_native_face_ids':patch['faces_potentially_affected'],'S_core_face_intersection':sorted(set(patch['faces_potentially_affected'])&{1245,1246,2728,2729}),'round2_vertex_deltas':e['vertices']}
 assert not changes[r]['S_core_face_intersection']
save('ACTUAL_SCULPT_CHANGES.json',changes)
status={'A':'VISUAL_DISTORTION','B':'VISUAL_NO_MEANINGFUL_IMPROVEMENT'}
report=f'''# HANDS_ANATOMICAL_SCULPT_VISUAL_POC_R1

本轮没有获得视觉通过候选。Codex初步判定：**A = VISUAL_DISTORTION；B = VISUAL_NO_MEANINGFUL_IMPROVEMENT**。Human尚未审核本轮新形体。A、B各完成两轮实质性雕塑，达到次数上限后停止。

## 方法与实际成果

使用Blender 5.1.2后台Python API，对从未修改原C1重新打开的两个独立右手mesh副本进行受控顶点雕塑。每个副本新增一个独立实验shape key，relative_key为未修改Basis，手动value=1；没有新driver或自动触发。A与B没有叠加或合并，未微调旧A2/B1候选。

做法是有限的局部grab／支撑笔触：给定空间中心、半径、方向，以局部比例衰减直接拖动顶点，再观察真实皮肤渲染并修正。现有Armature的3×3线性变换只用于将世界空间笔触换算到mesh局部坐标，没有建立新蒙皮算法、曲面优化器、随机搜索器或自动纠错Agent。

真正保存并交付：
- A_SCULPT_NOT_APPROVED.blend
- B_SCULPT_NOT_APPROVED.blend

二者是各自第2轮真实文件的同目录字节相同副本，不是空壳。最终文件重开后，2.6秒evaluated mesh与建模记录逐点误差0。原Basis、原shape key绝对坐标和相对差分、权重、UV、3300顶点／3298原生面、rest骨数据、驱动表达式／目标与全部Action摘要均与原C1一致。

## 真人参考与造型意图

沿用准备阶段已经实际查看的MusicRadar／Daniel Griffiths右手摆位照片、PiaDOOR左手八度照片、PianoVAM实拍第420帧。来源／哈希／内部使用限制见REAL_REFERENCE_OBSERVATIONS.json及原项目参考清单。没有采用AI手图，也没有移植照片姿态或数据集动作。

A意图是减少近节靠虎口侧的非关节突起，保留背侧软组织圆度及MCP—PIP骨段关系；B意图是形成连续的下部第一指蹼组织扇面，保留自然虎口凹面。照片只提供定性形态依据，不提供唯一三维目标。

## 扩展范围与保护

原ROI-A/B核心仍来自既有CONFIRMED_ROI_PROPOSAL.json。保留原草案，实际范围在任何雕塑前另存SCULPT_SCOPE_ACTIVE_BEFORE_EDIT.json。

| 区域 | 核心可动点 | 柔和过渡可动点 | 实际移动 | 外围／排除点 |
|---|---:|---:|---:|---:|
|A|{len(scope['patches']['A']['core_editable_vertex_ids'])}|{len(scope['patches']['A']['soft_transition_vertex_ids'])}|{edits['A']['actual_changed_count']}|{len(scope['patches']['A']['fixed_boundary_and_excluded_vertex_ids'])}|
|B|{len(scope['patches']['B']['core_editable_vertex_ids'])}|{len(scope['patches']['B']['soft_transition_vertex_ids'])}|{edits['B']['actual_changed_count']}|{len(scope['patches']['B']['fixed_boundary_and_excluded_vertex_ids'])}|

A为原核心相邻的局部侧壁与MCP过渡，按原MCP—PIP轴保留PIP附近区域固定，没有扩到整根食指。B为下部第一指蹼与掌部连接的相邻局部扇面；为获得实际柔和过渡，将草案的两圈上下文扩为三圈，并限制在同一局部空间范围。该补充在雕塑前记录，未扩展到大半掌部。

S核心及额外一圈保护邻域全固定。没有S核心面进入实际受影响面集。指尖、指腹、skin pad marker及其两圈网格邻域、其他手指、无关掌部、左手与授权范围外所有求值点均保持原位。详细顶点／面号、固定边界、前后局部坐标见ACTUAL_SCULPT_CHANGES.json和各ROUND_EDIT_RECEIPT。

## 两轮雕塑与视觉判断

A第1轮：广泛侧向收整并轻支撑背侧肩部，最大2.6秒求值位移1.848027mm。变化比上一轮A2明显，但上端终止处产生新的折点。
A第2轮：减弱侧向拖动，给近端／远端终止增加较长衰减，最大位移{edits['A']['max_evaluated_shift_2_6_mm']:.6f}mm。上端突变有所减弱，但仍有收腰、分段折点，不能称为合理的人体近节皮肤改善。因此判VISUAL_DISTORTION。没有因差异变大就判成功。

B第1轮：向外及向上填充下部组织扇面，最大位移1.525158mm；侧向推出偏多，原折陷观感仍在。
B第2轮：保持原足迹，将侧向分量减小、更多转向凹陷深度方向，限制峰值不超过首轮，最大位移{edits['B']['max_evaluated_shift_2_6_mm']:.6f}mm。存在局部填充，但高清俯视、近侧和反向没有形成足够清楚、可信的自然形体改善，判VISUAL_NO_MEANINGFUL_IMPROVEMENT。

这两个判定是本轮Codex视觉初评，不冒充Human已认可／否决新候选。S原有独立观感仍保留。没有将本次未获成功直接归咎于网格质量，也没有继续第三轮增大位移。

## 旧corrective兼容性

在原C1 0.88571375秒，对同一姿态分别测试原corrective正常启用0.942156与临时关闭，新雕塑key均为1。关闭只在未保存的测试实例中进行，交付文件原driver未改变。

| 区域 | 正常激活时雕塑最大位移mm | 原key关闭时mm | 两种启用条件的位移场最大差mm |
|---|---:|---:|---:|
|A|{compat[0]['max_actual_sculpt_shift_mm']:.6f}|{compat[1]['max_actual_sculpt_shift_mm']:.6f}|{compat[0]['effect_difference_from_old_off_mm']:.6f}|
|B|{compat[2]['max_actual_sculpt_shift_mm']:.6f}|{compat[3]['max_actual_sculpt_shift_mm']:.6f}|{compat[2]['effect_difference_from_old_off_mm']:.6f}|

独立key没有像上轮Basis修改一样被旧key约94%抵消。这里仅证明雕塑位移承载的兼容性，不证明其形体自然或具备自动触发机制。

## 有限安全检查

对原C1 2.600秒、历史固定几何PASS姿态分别实际重算evaluated mesh、实际三角化、全右手与实际键体相交／内部深度、非邻接自交、跨手碰撞、局部翻面、面积／边长与法向射线厚度代理、皮肤触点及接触邻域。不是沿用旧PASS。

两处候选在这两个姿态均没有新增自交／跨手碰撞／非目标键相交或深度增加，没有面翻转。授权范围外、S核心和保护邻域、左右手skin pad接触点／相关网格区域位移为0。固定姿态新算A♯4全手精确表面净空均为**0.282075256mm**；A4与C♯5保持分离。G4与左手B3活动skin pad位置保持。

A局部边长比约0.8816–1.0377；B约0.9303–1.0780。没有边或面几何塌缩，但A视觉收腰仍是不可忽略的形体问题；有限几何检查不能把它升级为自然性通过。法向射线是局部厚度代理，不是真实组织厚度或体积认证。

原C1已有非目标穿键仍保留，不宣称原C1全手PASS。完整六态回归、右手16音48活动触点复验、整曲高频几何验收、动画及自动激活机制均为**NOT_RUN**；按本轮要求未在Human视觉确认前展开。

## 视觉交付

A_SCULPT_HUMAN_REVIEW.png和B_SCULPT_HUMAN_REVIEW.png各含三栏：原C1／上轮Human否决候选（A2或B1）／本轮第2轮。每张含正式正交俯视、局部高清俯视、真侧视或虎口近侧视，以及局部透视／反向。

所有同组相机矩阵、投影、光照、材质、倍率和flat标志一致；正式俯视1280×720，局部1280×960。真实皮肤无遮挡，不依赖线框；没有smooth shading、光照美化、隐藏模型、单栏换镜头或改变姿态。原始渲染与两轮工作图留作证据，核心审核图只有上述两张。

## 保护与停止

受保护输入{len(checks)}项SHA256均与对应前值一致。前值来源逐条写入PROTECTED_SHA256_BEFORE_AFTER.json；旧A2/B1对照Blend采用前轮交付manifest中的SHA作为本轮之前的证据，并未伪称重新捕获了更早的当前任务前值。原C1仍为d8e0f5a85e71323739bfcd4de485ff7a2b4096f8e59bbd4c578ee9d76d3e51a7。

独立piano目录未访问；原C1、正式MIDI、指法、冻结Rig、Basis、权重、corrective、琴键Action、旧报告与历史FAIL全部未改。PREPARATION_STATUS是此前等待补全指令的历史记录；当前状态以RESULT.json为准。没有组合A+B、正式晋升或替换。

**STOP — HUMAN REVIEW**
'''
# CommonMark blank line before the candidate list.
report=report.replace('真正保存并交付：\n-','真正保存并交付：\n\n-')
md('TECHNICAL_REPORT.md',report)
review=f'''# Human审核

本轮各执行两轮直接雕塑，**没有获得视觉通过候选**。以下为Codex初评，等待你查看真实对照：

- **A：VISUAL_DISTORTION。** 比旧A2更容易看出形体变化，但近节侧缘仍有收腰和新折点；不能把更明显的位移当作更自然。
- **B：VISUAL_NO_MEANINGFUL_IMPROVEMENT。** 下部有实际填充，但尚未形成清楚、可信的自然虎口过渡。S的独立问题没有修复。

请优先打开原尺寸对照图：

- [A：原C1／Human否决的旧A2／本轮雕塑](A_SCULPT_HUMAN_REVIEW.png)
- [B：原C1／Human否决的旧B1／本轮雕塑](B_SCULPT_HUMAN_REVIEW.png)

真实候选：[A_SCULPT_NOT_APPROVED.blend](A_SCULPT_NOT_APPROVED.blend)、[B_SCULPT_NOT_APPROVED.blend](B_SCULPT_NOT_APPROVED.blend)。都只新增独立实验shape key，手动value=1，尚无自动触发。原Basis、权重、旧corrective／driver和Action保持。

已完成两姿态的有限几何检查，未见新增自交、翻面或非目标键碰撞，A♯4净空仍0.282075mm，skin pad及邻域不变。独立key在旧corrective关闭与正常0.942激活时均保持效果；这不等于形体合格。完整六态、48活动触点和整曲验收NOT_RUN。

受保护输入{len(checks)}项哈希一致，独立piano目录未访问。详细范围、位移、失败观察及风险见[技术报告](TECHNICAL_REPORT.md)。

两轮上限已到，不继续增加位移，不合并A+B，不晋升正式资产。

**STOP — HUMAN REVIEW**
'''
md('HUMAN_REVIEW.md',review)
save('RESULT.json',{'task':'HANDS_ANATOMICAL_SCULPT_VISUAL_POC_R1','visual_success_obtained':False,'per_region':status,'assessment_author':'Codex preliminary visual assessment; new Human review pending','substantive_rounds_per_region':2,'selected_round':2,'new_shape_keys_only':True,'Basis_weights_original_corrective_driver_changes':False,'serious_regression_in_executed_geometry_checks':False,'original_C1_inherited_collisions_preserved':True,'S_core_and_collar_changed':False,'complete_six_pose_regression':'NOT_RUN','right16_active48':'NOT_RUN','full_music_high_frequency':'NOT_RUN','human_approved':False,'protected_input_count':len(checks),'all_checked_inputs_unchanged':True,'combined_asset_created':False,'stop':'STOP — HUMAN REVIEW'})
files=['A_SCULPT_NOT_APPROVED.blend','B_SCULPT_NOT_APPROVED.blend','A_SCULPT_HUMAN_REVIEW.png','B_SCULPT_HUMAN_REVIEW.png','TECHNICAL_REPORT.md','HUMAN_REVIEW.md','PROTECTED_SHA256_BEFORE_AFTER.json','RESULT.json','SCULPT_SCOPE_ACTIVE_BEFORE_EDIT.json','ACTUAL_SCULPT_CHANGES.json','FINAL_CANDIDATE_REOPEN_RECEIPT.json']
save('DELIVERY_SHA256.json',[{'path':str(OUT/n),'sha256':sha(OUT/n)} for n in files])
print(json.dumps({'results':status,'protected_inputs':len(checks),'all_unchanged':True,'stop':'STOP — HUMAN REVIEW'}))

