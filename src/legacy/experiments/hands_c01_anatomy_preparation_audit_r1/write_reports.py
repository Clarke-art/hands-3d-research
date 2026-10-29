import sys,json,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;PRE=O.parent/'hands_c01_s1_constrained_solver_feasibility_r1'
def read(n):return json.loads((O/n).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,x):(O/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
def lk(n):return f'[{n}](<{(O/n).as_posix()}>)'
def md(n,s):(O/n).write_text(s+'\n',encoding='utf8')
audit=read('ACTUAL_RIG_ANATOMY.json');rows={r['label']:r for r in audit['rows']};supp=read('ANGLE_AND_PARITY_SUPPLEMENT.json')
A=json.loads((PRE/'ACTUAL_VALIDATION_2.json').read_text());Bs=[read(f'B_ACTUAL_{i}.json') for i in [1,2]];B=Bs[1];solves=[read(f'B_SOLVE_{i}.json') for i in [1,2]];rb=read('B_READBACK_2.json');proposal=read('ANATOMY_CONSTRAINT_PROPOSAL.json')
assert all(B['gates'].values()) and B['zero_non_target_intrusion'] and solves[1]['convergence']['success']
assert rb['vertex_difference_mm']==0 and rb['native_identity_verified']
assert sha(O/'ANATOMY_CONSTRAINT_PROPOSAL_B1_LOCK.json')==solves[0]['proposal_sha256']
assert sha(O/'ANATOMY_CONSTRAINT_PROPOSAL.json')==solves[1]['proposal_sha256']
protected=read('PROTECTED_FILES_BEFORE.json');after={p:sha(Path(p)) for p in protected};assert after==protected
dump('PROTECTED_FILES_AFTER.json',dict(unchanged=True,checked_count=len(after),hashes=after))
human=dict(task=proposal['task'],authority='Direct human current request',A_S1_2=dict(S1_NUMERICAL_GEOMETRY='PASS',S1_HUMAN_ANATOMICAL_VISUAL='FAIL'),B=dict(geometric_and_reference_constraints='PASS',human_anatomical_visual='PENDING'),DYNAMIC_BRIDGE_AUTHORIZATION='NOT_GRANTED',old_experiment_records_not_overwritten=True)
dump('HUMAN_DECISION_LOCK.json',human)
status='ANATOMY_STATIC_CANDIDATE_PASS_HUMAN_PENDING';total=sum(s['elapsed_seconds'] for s in solves)
pert=read('READONLY_PREPARATION_PERTURBATIONS.json');stills=read('STILL_MANIFEST.json')
summary=dict(task=proposal['task'],status=status,cause_finding='ANATOMY_CAUSE_IDENTIFIED',decision='C',authority='DESIGN_PROVISIONAL',stop='STOP — HUMAN REVIEW',human_decision=human,budget=dict(max_main_solves=2,actual_main_solves=2,reported_main_solve_wall_seconds=total,limit_seconds=300,per_solve_limit_seconds=140,pre_optimizer_startup_error_process_wall_seconds=2.4783135,main_plus_startup_error_seconds=total+2.4783135,postprocess_failures_are_not_solves=True),A_original_state=A['state'],A_source_readonly=str(PRE),B_selected_attempt=2,actual_B_attempts=Bs,optimizer_results=solves,independent_saved_B_readback=rb,actual_rig_audit_file=str(O/'ACTUAL_RIG_ANATOMY.json'),angle_supplement=supp,diagnostic_perturbations=pert,proposal_versions=dict(B1_sha256=solves[0]['proposal_sha256'],B2_sha256=solves[1]['proposal_sha256']),music_events=dict(R07_G4_ON=2.492855,S1=2.527855,R07_OFF_R08_E5_ON=2.921426,S1_to_E5_seconds=2.921426-2.527855,unchanged=True),fingering='G4(1) -> E5(3) -> C5(1) -> D5(2) -> E5(3) -> F#5(4) -> G5(5)',fingering_motion_feedback=dict(status='FINGERING_MOTION_FEEDBACK_REQUIRED',scope='Add hand-shape and phase-dependent preparation costs to upstream/downstream interface; no claim that human fingering is impossible',fingering_changed=False),no_continuous_motion_generated=True,no_new_action=True,stills=stills,protected_count=len(after),runtime_issues=[dict(log='b_solve_1_startup_error.log',reason='Empty 1mm nearface pool in natural reference pose; failed before optimizer, repaired empty handling and pool radius5mm'),dict(log='supplement_angles_startup_error.log',reason='Recovered policy hash initially used LF rather than original Windows CRLF bytes; fixed byte preservation'),dict(log='supplement_angles_frame_mismatch.log',reason='Direct canonical-vs-raw armature rest comparison ignores common global frame; common near-rigid transform aligns all right bones to 2.22e-16')])
dump('ANATOMY_STATIC_RESULTS.json',summary)
def mid(r):return next(d for d in r['digits'] if d['digit']=='MIDDLE')
pose_table=[]
for label,r in list(rows.items())+[('B2',B['actual_anatomy'])]:
 d=mid(r);j=d['joints'];q=d['controls_recovered_deg']
 pose_table.append(f"| {label} | {q[0]:.5f} | {q[1]:.5f} | {q[2]:.5f} | {q[3]:.5f} | {j[0]['palm_heading_deg']:.5f} | {j[1]['parent_to_child_projected_bend_deg']:.5f} | {j[2]['parent_to_child_projected_bend_deg']:.5f} |")
axis_table=[]
for d in rows['FROZEN_R2_REST']['digits']:
 for j in d['joints']:
  af=', '.join(f'{v:.6f}' for v in j['axis_flex_local']);sp=', '.join(f'{v:.6f}' for v in j['axis_spread_local']) if j['axis_spread_local'] else '无独立spread'
  axis_table.append(f"| {j['bone']} | {j['parent']} | [{af}] | {sp} |")
rootdoc=f"""# 实际Rig关节与解剖审核

任务：{proposal['task']}。全部新候选DESIGN_PROVISIONAL。A保持S1_NUMERICAL_GEOMETRY=PASS、S1_HUMAN_ANATOMICAL_VISUAL=FAIL；动态授权NOT_GRANTED。

## 身份、骨链与真实求值

只读加载正式RIGHT HAND R2、四批准静态场景、上一轮S1 #2保存场景、按完整控制重建S1 #1和合格S2；提取实际pose/rest矩阵及3300个deformed mesh顶点，另存快照，不保存源文件。四批准静态姿态均实际读取，左右镜像不混作右手的数值边界。

长指链为WRIST_R → DIGIT_MCP_R → DIGIT_PIP_R → DIGIT_DIP_R → DIGIT_TIP_R；拇指为THUMB_CMC_R → THUMB_MCP_R → THUMB_IP_R → THUMB_TIP_R。TIP为非变形末端。Rig无独立metacarpal或前臂段，因此MCP绝对临床角和腕相对前臂角不能从名称直接推断。

异常身份通过MIDDLE三骨名称、相应deform权重集合及原pad顶点确认，中指pad累计中指组权重约1.000000003（float误差），强权重顶点{mid(rows['S1_2_HUMAN_FAIL'])['skin_identity']['strong_digit_vertices']}个。原三角语义/拓扑排除不改。青色骨链图显示实际中指，紫色为无名指；不是截图猜测。

## rest空间、控制轴和角度约定

canonical probe与正式armature数据不是同一全局坐标。补测确认一个共同near-rigid 4×4变换可对齐全部右手rest骨，最大矩阵残差{supp['canonical_rest_matrix_error']:.3g}；变换完整保存在ANGLE_AND_PARITY_SUPPLEMENT.json。直接逐元素比两种空间曾触发诊断断言，日志保留；不是源身份损坏。

屈曲局部轴由canonical rest长轴y与掌侧-Z叉积，再转换到该骨局部空间。spread为canonical +Z在基部骨局部空间的表示。MCP/CMC的basis为Rot(spread,s)·Rot(flex,f)，PIP/DIP只有单轴flex。先以实际basis还原有序轴旋转，检查重建误差，再计算掌面骨长轴heading及相邻骨在运输后的铰链平面内的投影弯角。没有使用Euler XYZ冒充解剖角。

| 实际骨 | 父骨 | flex局部单位轴 | 基部spread轴 |
| --- | --- | --- | --- |
{chr(10).join(axis_table)}

“控制角”是已经弯曲的RSSF rest增量；“投影弯角”是骨长轴几何量，均不是CT/解剖标志校准的绝对人体角。MCP使用掌参考平面heading，不能以WRIST骨方向当真实metacarpal临床测角。正flex方向为原掌侧弯曲，spread符号按控制轴定义，不直接称径向/尺向。

## 中指实际对照

| 场景 | MCP增量 | PIP增量 | DIP增量 | 基部spread | 掌面heading | PIP投影弯角 | DIP投影弯角 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
{chr(10).join(pose_table)}

A的MCP spread -24.99871°接近原-25°工程界；批准右手参考约-6.73至-7.20°，heading约8.23至9.03°，A为26.17°。S1 #1也在-25°；S2同样接近该边界，应标记解剖风险待审，不能将其旧几何合格改称教学自然度合格或擅自添加Human FAIL。

PIP/DIP的basis重建误差约1e-10，只有授权flex旋转；其“偏出铰链平面”几何分量约-2.81/-2.60°也存在于冻结rest与批准姿态，变化仅浮点量级，不能误诊为新增PIP/DIP侧向DOF。A弯角约10.82/1.26°，较批准R1的15.11/3.53°更接近rest，不是发现了过度PIP/DIP屈曲。

中指spread轴沿rest长轴的分量{supp['MCP_spread_axis_longitudinal_component']:.6f}，因此并非纯解剖侧摆轴。有序旋转的rest-Y swing/twist分量，A约3.77°，批准R1约1.14°，S2约7.66°；它是几何分解，不可直接按临床旋前角判病理。说明控制命名“spread”仍会耦合骨链弯曲平面/轴向表现。尚未证明需改冻结Rig。

无名指A spread约-1.35°，批准参考约+5.65°；新B同时恢复协调参考，其与中指间隙从0.079865增至4.936993mm。没有证明无名指违反人体最大活动范围。

掌根及WRIST world位置/矩阵在原始JSON中；A和B使用同一Z，B保留原root旋转授权界。WRIST basis无新增屈曲，root旋转是整个手掌刚体姿态；没有前臂，不能据此宣布真实腕角异常或正常。

## 人体依据与限制

[正式MCP解剖资料](https://pubmed.ncbi.nlm.nih.gov/30860699/)支持MCP有屈伸及侧向运动；因此不全面禁止spread。[PIP运动学试验](https://pmc.ncbi.nlm.nih.gov/articles/PMC3835607/)为单个尸体食指，支持以屈曲为主并有小量耦合3D运动，不能提供全部长指统一边界。

[钢琴手部运动研究](https://pubmed.ncbi.nlm.nih.gov/21880938/)显示专家手指与手部平移按任务协调；不支持固定全局PIP/DIP比例或静止掌位。文献人体最大ROM、舒适主动范围和本项目教学参考分别记录：前两类对当前rest映射的精确数值证据不足，未编造阈值；本次B采用已批准同Rig姿态族作为保守工程参考，仍待Human确认。

Rig原pose bones未发现旋转限制约束，手工任意quaternion可越过合理运动。实际求解器长指仅4DOF，PIP/DIP没有任意XYZ自由度，但MCP flex/spread独立工程边界仍允许Human否决姿态。原LONG界[0,0,0,-25]至[32,32,20,25]是rest增量设计域；performance_core通用bounds更宽且非本S1使用域，均不能当生理活动范围。
"""
md('RIG_JOINT_ANATOMY_AUDIT.md',rootdoc)
cause=f"""# Human否决姿态的原因 — ANATOMY_CAUSE_IDENTIFIED

**原A的Human FAIL不变。** 发现的是可核实控制/准备设计问题；没有证明人体绝对不能演奏C01，也没有证明冻结网格必须改造。

## 直接证据

1. 实际中指MCP spread约-25°，骨链掌面heading约26°，超出本项目已批准右手参考族8–9°。PIP/DIP没有额外侧向basis旋转；主侧偏发生在MCP。spread绕canonical Z而非纯解剖侧摆轴，耦合弯曲平面和rest-Y twist表现。
2. A的中指flex增量约1.399/0.300/0.032°，相比批准R1为3.878/4.589/2.303°，未保持参考弯曲分布。没有证据把截图中的“弯曲异常”单独解释为PIP/DIP过屈。
3. 旧准备只要求中指pad进入E5区域和4–20mm高度，未约束整根骨链方向、手型协调或MCP flex/spread联合域。此前SLSQP目标为对Human未批准种子的小控制改变量，故能保留异常形态并几何收敛。

## 单控制诊断（非求解、非候选）

在A掌位/其他角不变时，只将中指spread恢复批准R1值，G4接触、目标深度0.00324273mm、非目标0及交叉0仍成立；但旧E5 pad越界从0.042103增到17.963238mm，高度21.378171mm。这直接证明该掌位下的旧精确提前目标与参考中指朝向不协调；不证明所有掌位下都矛盾。

将全部非拇指恢复批准参考而不调整掌位，会出现约3.353881mm非目标侵入。故不能仅手工“摆正手指”就判合格，需要接触、避障与手型联合求解。原raw布尔/数值都保留在READONLY_PREPARATION_PERTURBATIONS.json，没有把这些诊断当PASS。

## 实际B验证

联合参考族与分阶段准备后，B2在原冻结Rig、同一S1/Action、同一Z完成G4真实接触、非目标侵入0、交叉0；MCP spread -6.73202°、heading8.23417°，中指/无名指间隙4.93699mm。支持两种设计问题可以在静态层面协调修复，不支持“只改准备就足够”或“只加一个角阈值就足够”的因果结论。B两项联合改变未做完整因素分离，视觉仍待Human。

## 尚未解决

人体绝对角的骨性标志校准、舒适主动活动域、MCP flex/spread随屈曲耦合、腕与前臂关系均不足。网格rest本身有固定曲率/轻微非平面性，可能影响外观，但冻结身份与批准姿态同一，当前没有结构性不可行证据。尚未验证0.393571s内保持G4并到达E5的连续运动。

S2几何合格但同样近-25°spread，说明风险也应进入后续触键目标，而不是仅修改S1提前准备。S2Human自然度未重新判定。
"""
md('S1_UNNATURAL_POSE_ROOT_CAUSE.md',cause)
prep=f"""# E5提前准备约束审核

S1在R07 G4 ON后35ms：2.492855 → 2.527855。E5 ON为2.921426，剩余**0.393571s**；R07 OFF与R08 ON同为2.921426。全部原NOTE_ON/OFF、指法和键Action不变。

## 原约束

中指mesh pad必须在E5可触矩形外2mm内、高度4–20mm，早期软目标还偏好E5中心/Y=35mm/高度12mm。原数值约束没有骨链方向、手掌相对手指朝向、正常曲率分布和未来掌位路径。可出现“pad在正确位置，整根指形异常”。

原目标矩形及精确位置由冻结SKIN_MODEL_META的E5记录给出，不重建键位；A实际pad越界0.042103mm、height19.527858mm。B2在同一时刻height19.150453mm、越界19.968649mm，原E5精确目标明确FAIL。新B不能追认为原合同全部通过；它通过的是授权本轮阶段性准备合同。

[提前动作研究](https://pubmed.ncbi.nlm.nih.gov/9063705/)发现准备时机随曲句变化，特定穿指任务可提前约500ms，也有近串行执行；不能由剩余394ms推导必须精确悬停或必须完全不准备。[协调研究](https://pubmed.ncbi.nlm.nih.gov/21880938/)支持手掌平移和手指动作按任务联合参与。

## 建议阶段（不是已生成的时间线）

| 阶段 | 必须保持 | 准备目标 |
| --- | --- | --- |
| 当前持键 | 原G4真实指腹接触及全网格门禁 | 当前音为硬目标 |
| 自然手位准备 | 原音仍持至原OFF；参考手型和不撞键 | 不强制下一pad此时对准E5；允许掌位参与 |
| 释放与换位 | MIDI边界不变，无新增休止 | 提前掌位移动须一直保持G4；边界时协调拇指释放/中指落键 |
| 下一音触键 | 2.921426原E5事件及其原Action状态 | 此时应满足E5真实接触/正常手型，需另行验证 |

阶段可以重叠，不是给每阶段额外分配时间。不能在2.921426之前提前释放G4来制造换位间隙，也不能在OFF/ON之间塞一个正时长的休止。“释放与换位”不是在当前两音之间已经存在的自由空档。

本轮S1只实现早期自然参考族与原准备下界4mm；去掉精确E5 XY和20mm上界，4mm是沿用工程下界而非生理值。完整皮肤避障不变，手掌Z未放开，不通过整体抬高取得安全。

B2距E5矩形约19.97mm只是当前空间差，不能证明剩余时段能到达；更不能用20mm/0.394s的平均速度算术替代关节、加速度、接触和碰撞轨迹验收。后续若获授权，应按任务可达域和离事件时间递进收紧目标，最终在原事件达到真实触键，不沿用固定“所有下一指提前悬停”的规则。
"""
md('E5_PREPARATION_CONSTRAINT_REVIEW.md',prep)
ctB=B['actual_geometry']['contact'];gapB=B['middle_ring_exact_clearance']['distance_mm'];controltable=[]
for d,qA,qB in zip(['THUMB','INDEX','MIDDLE','RING','LITTLE'],[A['state'][6+4*i:10+4*i] for i in range(5)],B['actual_anatomy']['recovered_controls']):
 controltable.append(f"| {d} | "+', '.join(f'{v:.6f}' for v in qA)+" | "+', '.join(f'{v:.6f}' for v in qB)+" |")
ab=f"""# S1静态A/B真实对照

A为原S1 #2原样只读，Human FAIL；B1/B2均是本轮实际SLSQP求解、独立Blender验收。全DESIGN_PROVISIONAL，B2待Human。

| 指标 | A：原Human否决 | B1：参考族+早期准备 | B2：再消除非目标侵入 |
| --- | ---: | ---: | ---: |
| 真实G4接触布尔 | true | true | true |
| 接触距离mm | 0 | 0 | 0 |
| 目标实体侵入mm | {A['actual_geometry']['target_key_max_depth_mm']:.10f} | {Bs[0]['actual_geometry']['target_key_max_depth_mm']:.10f} | {B['actual_geometry']['target_key_max_depth_mm']:.10f} |
| 非目标/非指腹侵入mm | 0 | {Bs[0]['actual_geometry']['wrong_key_or_nonpulp_max_depth_mm']:.10f} | 0 |
| 五指非邻接面交叉 | 0 | 0 | 0 |
| 中指/无名指精确间隙mm | {A['middle_ring_exact_clearance']['distance_mm']:.10f} | {Bs[0]['middle_ring_exact_clearance']['distance_mm']:.10f} | {gapB:.10f} |
| 中指MCP spread deg | -24.998713 | -6.732022 | -6.732022 |
| 中指掌面heading deg | 26.169566 | 8.234167 | 8.234167 |
| 原E5精确悬停合同 | PASS | FAIL | FAIL |
| 新阶段性准备/参考族 | 不满足 | PASS | PASS |
| Human解剖视觉 | FAIL | 未审 | PENDING |
| SLSQP nit / success | 原2 / true | 11 / true | 11 / true |
| 新优化墙钟秒 | 不重跑 | {solves[0]['elapsed_seconds']:.3f} | {solves[1]['elapsed_seconds']:.3f} |

B1留有A4拇指区域/B4食指约0.20mm侵入，虽低于原0.25mm门禁，不能称零侵入。本轮第二次的明确理由是去除此残留，未扩大角域或调软权重。B2目标只留G4合法指腹微小深度，非目标/非指腹均0。

## 明确关节约束与控制

非拇指q=(1-λ)q_R1+λq_R2，共享λ∈[0,1]，为已批准同Rig局部保守参考族；实际λ约1.09e-9接近R1。这是结构映射，不是软姿态先验。实际Blender还原的所有被动关节和输入误差低于1e-4deg，未发现非授权轴旋转。精确临床“正常范围”证据不足，不将参考族说成人群舒适域。

| 手指 | A控制（flex1,2,3,spread）deg | B2实际还原 |
| --- | --- | --- |
{chr(10).join(controltable)}

Root Z固定{B['state'][2]:.15f}mm；A与B完整root/五指参数在ANATOMY_STATIC_RESULTS.json。root XY保持原授权界且限定A附近±15mm，旋转保持原±[8,8,12]deg；拇指保留原4控制界。没有改骨长、蒙皮、网格、键位或接触区。

## 真实几何与数值表示

B1用原面内LP最大depth≤0.20mm；B2对非目标块把同一LP延伸到负outside深度，要求≤-0.05mm，保留目标≤0.20mm。不是用软残差改名。动态AABB/支持平面必要条件过滤后枚举全部候选面内最深点；最后完整原检测器全88键、6596三角、五指10配对独立验收。

自碰撞数值用5mm近面池的保守分离轴≥0.02mm；池不保证覆盖整个角域，不能单独担保全局安全，完整BVH最终门禁不可省。两次均未重启，不挑中间迭代。

B2指腹接触/交叉面{ctB['top_surface_crossing_triangles']}个、原接触距离0、薄层投影面积{ctB['near_contact_projected_area_mm2']:.10f}mm²。面积不是压力/承力面积。B2精确间隙算法与上一轮相同：采样作上界、AABB下界剪枝、全部点–面及边–边特征；1298对精确候选。不是更换算法获得4.94mm余量。

B2诊断Blend保存后独立重读顶点差{rb['vertex_difference_mm']}mm，原键Action payload/实际网格及冻结native匹配。代理到实际顶点最大误差{B['proxy_actual_max_vertex_error_mm']:.10f}mm，独立结果优先。

两次新优化总{total:.3f}s/300s；优化前空近面池错误在minimize前退出，过程约2.478s另计，未产生第三次求解。后处理LF/CRLF哈希和坐标frame断言错误保留原日志并修复，不属于额外优化。没有模型训练、下载数据或连续动作。
"""
md('STATIC_AB_COMPARISON.md',ab)
humanmd=f"""# Human视觉审查 — STOP — HUMAN REVIEW

A的既有Human解剖FAIL保持不变。B2为ANATOMY_STATIC_CANDIDATE_PASS_HUMAN_PENDING，数值与保守参考族通过不替代视觉批准。

四张1280×720静帧来自实际deformed mesh，A/B相同camera矩阵和ortho_scale。青色为MIDDLE_MCP/PIP/DIP真实骨链在相机前景平面上的屏幕对齐投影，紫色为RING骨链；仅注释显示，不移动实际骨骼或皮肤。原左手在画面边缘作继承参考，未进行左手求解。已查看全部初版和修正后图，清除注释阴影并分开侧面标签；最终只交付四张。

## 相同俯视

![A Human FAIL](<{(O/'stills/A_OVERHEAD.png').as_posix()}>)

![B2 Human PENDING](<{(O/'stills/B_OVERHEAD.png').as_posix()}>)

## 相同侧斜

![A Human FAIL侧斜](<{(O/'stills/A_SIDE_OBLIQUE.png').as_posix()}>)

![B2 Human PENDING侧斜](<{(O/'stills/B_SIDE_OBLIQUE.png').as_posix()}>)

待Human审查：

- 中指MCP侧摆已从约-25°恢复-6.73°，骨链heading约8.23°；整根手指方向和曲率分布是否自然。
- 中指/无名指实际间隙{gapB:.6f}mm，是否接受相邻手指协调关系；间隙增加不证明动态安全。
- 拇指G4前缘真实持键、腕掌倾斜及食指状态是否适合教学。当前参考约束只严格覆盖非拇指；不能自动批准拇指/整体姿态。
- B2中指尚未在E5正上方（越界19.97mm），这是早期阶段定义，不代表E5最终触键可行。是否接受“自然准备 → 持键中换位 → 边界协调交接”的研究方向。

原A照片判定不因B结果改变。未授权G4→E5连续桥接、B02或正式教学生产；没有视频/新Action/关键帧。诊断Blend最终仅保留B2静态场景，Action数据块为0；原Action身份/状态已在独立验收中核对。
"""
md('HUMAN_VISUAL_REVIEW.md',humanmd)
final=f"""# 最终建议 — {status}

**C — 解剖/手型约束与E5准备策略都存在问题，需要联合改进。** 直接证据支持ANATOMY_CAUSE_IDENTIFIED；在不改冻结Rig下已得到满足真实几何及明确参考关节约束的B2静态候选，Human自然度仍待审。全部DESIGN_PROVISIONAL。

原A继续保持：

- S1_NUMERICAL_GEOMETRY = PASS
- S1_HUMAN_ANATOMICAL_VISUAL = FAIL
- DYNAMIC_BRIDGE_AUTHORIZATION = NOT_GRANTED

## 查清的原因

实际中指MCP spread接近-25°工程边界，掌面heading26.17°；批准参考约8–9°。PIP/DIP未发现额外侧向控制，异常主要为MCP侧摆及失去参考曲率分布。canonical spread轴还与rest长轴斜交，不是纯临床侧摆。

只恢复MCP spread时旧E5越界变为17.96mm，而G4接触/零交叉保持，证明当前掌位与旧精确提前目标不协调。0.393571s的准备窗口不能推导必须提前精确悬停。共同骨架/皮肤已能在保守参考族内求得安全S1，没有直接证据支持现在修改冻结Rig。

## 实际B2

- G4真实指腹接触距离0mm，目标侵入{B['actual_geometry']['target_key_max_depth_mm']:.8f}mm。
- 非目标/非指腹侵入0，五指非邻接皮肤交叉0。
- 中指MCP spread -6.73202°、heading8.23417°；中指/无名指精确间隙{gapB:.8f}mm。
- 实际骨角符合批准R1/R2局部参考族；Z与A相同，原键Action、时钟、Rig和网格不变。
- 两次优化均11迭代收敛，累计{total:.3f}s；B1的约0.20mm残留未隐藏，B2将其消除。保存后重读一致。

B2旧E5精确悬停合同仍FAIL（越界19.96865mm）；通过的是本轮分阶段早期准备定义。不能把它追认为原静态合同PASS，也不能证明下一音能及时触键。整体自然度、拇指形态和教学习惯由Human审查，不能以数值替代。

## 下一步技术决策

先由Human审查四张同视角A/B图和保守手型族。若认可，应把阶段依赖的手型族、MCP flex/spread协调和接触/全网格门禁纳入规划接口；不要继续用均匀独立角界和“pad精确提前到位”作为自然度替代。人体最大ROM/舒适主动角域对当前Rig的精确映射仍证据不足，需明确校准，不以论文最大角作默认目标。

登记FINGERING_MOTION_FEEDBACK_REQUIRED：未来指法候选的运动成本应包含参考手型偏离、掌位移动、跨指/穿指阶段、剩余时间和失败可行性反馈。C01固定G4(1)→E5(3)→C5(1)→D5(2)→E5(3)→F♯5(4)→G5(5)未改；没有证据宣称该人类指法绝对不可行。G4→E5大跨度及随后的回移需要整手协调，当前静态研究只识别规划接口风险。

前臂/腕绝对解剖角、全域手型族和连续可达性尚未验证；即使B视觉获认可，也仍需单独的动态授权。本轮不自动执行任何后续运动实验。

{lk('RIG_JOINT_ANATOMY_AUDIT.md')}、{lk('S1_UNNATURAL_POSE_ROOT_CAUSE.md')}、{lk('E5_PREPARATION_CONSTRAINT_REVIEW.md')}、{lk('ANATOMY_CONSTRAINT_PROPOSAL.json')}、{lk('STATIC_AB_COMPARISON.md')}、{lk('HUMAN_VISUAL_REVIEW.md')}。

{len(after)}项保护哈希不变，四个批准姿态、冻结Hands/Piano、C01/MIDI及全部旧失败记录只读。4张720p静帧、独立诊断Blend和完整实际数值证据已保存。

**STOP — HUMAN REVIEW。**
"""
md('FINAL_RECOMMENDATION.md',final)
print('FINAL',status,'decision C','optimization',total,'protected',len(after))
