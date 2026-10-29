import sys,json,hashlib,ast
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent
sys.path.insert(0,str(O.parent/'hands/audits/midi_driven_dual_hand_piano_performance_poc_r1/_deps'))
import numpy as np
from scipy.spatial.transform import Rotation
load=lambda n:json.loads((O/n).read_text(encoding='utf-8-sig'))
def save(n,v): (O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def md(n,s): (O/n).write_text(s.strip()+'\n',encoding='utf8')
a=load('ACTUAL_ACTION_VALIDATION.json');ep=[load(f'ENDPOINT_ACTUAL_{i}.json') for i in (1,2)];sol=[load(f'ENDPOINT_SOLVE_{i}.json') for i in (1,2)];p=load('POLICY_LOCK.json');pre=load('PREFLIGHT_AND_ENDPOINT_DIAGNOSIS.json');meta=load('SKIN_MODEL_META.json')
pf=json.loads((O.parent/'hands_c01_whole_hand_motion_feasibility_r1/RIG_PREFLIGHT.json').read_text());BM=np.array(pf['static_root_base_matrix']);BASE=np.array(meta['root_base_xyz_m']);R0=Rotation.from_matrix(BM[:3,:3]).as_matrix()
rows=a['rows'];roots=[]
for r in rows:
 RR=Rotation.from_quat(np.array(r['root_world_quaternion'])[[1,2,3,0]]).as_matrix()@R0.T
 delta=(np.array(r['root_world_position_m'])-BASE-RR@(BM[:3,3]-BASE))*1000
 angles=Rotation.from_matrix(RR).as_euler('xyz',degrees=True)
 roots.append(dict(time=r['time'],translation_mm=delta.tolist(),extra_rotation_control_deg=angles.tolist(),in_authorized_domain=bool(np.all(delta>=np.array([-150,-30,-12.217247311392744])-.001) and np.all(delta<=np.array([60,35,12])+.001) and np.all(abs(angles)<=np.array([8,8,12])+.001))))
T=np.arange(2.527855,3.349997,1/120);un=[min(rows,key=lambda r:abs(r['time']-t)) for t in T];ur=[min(roots,key=lambda r:abs(r['time']-t)) for t in T];C=np.array([r['translation_mm'] for r in ur]);cv=np.gradient(C,T,axis=0,edge_order=2);ca=np.gradient(cv,T,axis=0,edge_order=2)
kin=dict(a['kinematics']);kin['object_origin_speed_peak_mm_s']=kin.pop('root_speed_peak_mm_s');kin['root_control_translation_speed_peak_mm_s']=float(np.linalg.norm(cv,axis=1).max());kin['root_control_translation_acceleration_peak_mm_s2']=float(np.linalg.norm(ca,axis=1).max())
qs=Rotation.from_quat(np.array([r['root_world_quaternion'] for r in un])[:,[1,2,3,0]]);kin['root_angular_speed_peak_deg_s']=float(np.max((qs[:-1].inv()*qs[1:]).magnitude())*120*180/np.pi)
first={n:min((r['time'] for r in rows if r[n+'_strict_crossing_faces']>0),default=None) for n in ['G4','E5']}
q=np.array([r['joint_controls_deg'] for r in rows]);total=sum(s['elapsed_seconds'] for s in sol)+a['optimizer']['elapsed_seconds']
summary=dict(task=p['task'],status=a['status'],authority='DESIGN_PROVISIONAL',stop='STOP — HUMAN REVIEW',candidate_count=1,numerical_budget=dict(endpoint_attempt_seconds=[s['elapsed_seconds'] for s in sol],trajectory_seconds=a['optimizer']['elapsed_seconds'],total_seconds=total,limit_seconds=600,setup_and_actual_validation_excluded=True,actual_validation_seconds=a['check_seconds']),endpoints=ep,source_start_B2=pre,optimizer=a['optimizer'],actual_validation_file='ACTUAL_ACTION_VALIDATION.json',validation=a['validation'],timing=dict(G4_first_observed_hold_gate_failure=a['G4_first_hold_loss_time'],G4_first_and_only_sampled_strict_surface_contact=first['G4'],E5_first_observed_strict_surface_contact=first['E5'],E5_first_full_contact_gate=a['E5_first_observed_contact_time'],E5_first_touch_relative_to_ON_seconds=first['E5']-2.921426,sampling_brackets_not_exact_continuous_transition=True,contact_gate_definition='Strict clipped pulp triangle/top-plane crossing plus nonzero projected area, pad inside and abs(pad gap)<=3mm; crossing alone does not imply <=0.25mm penetration'),critical_times=a['critical_times'],maximum_target_depth_mm=a['maximum_target_depth_mm'],maximum_non_target_depth_mm=a['maximum_non_target_depth_mm'],maximum_nonadjacent_crossing_pairs=a['maximum_nonadjacent_crossing_pairs'],middle_ring_min_exact_mm=a['middle_ring_min_exact_mm'],failed_samples=a['failed_samples'],joint_failed_samples=a['joint_failed_samples'],middle_spread_control_range_deg=[float(q[:,2,3].min()),float(q[:,2,3].max())],root_domain_failed_samples=sum(not r['in_authorized_domain'] for r in roots),actual_root_controls=roots,kinematics=kin,semantic_corrections=dict(raw_root_relative_Z_mm='Legacy field is object-origin z minus reference z, NOT wrist/control translation. Use actual_root_controls here.',raw_root_speed_peak_mm_s='Object-origin speed; correctly labelled in this summary.',invalid_initial_action_measurements='ACTION_EXPORT_INVALID_ROOT_FRAME_VALIDATION.json excluded from all conclusions; export mapping corrected without optimization.'),export_correction=load('ROOT_ACTION_EXPORT_CORRECTION.json'),video_generated=False,native_frozen_identity_verified=a['native_frozen_identity_verified'],original_key_action_payloads_unchanged=a['original_key_action_payloads_unchanged'],naturalness_Human='PENDING; endpoint active-flex reference and trajectory not Human accepted',entry_hand_motion='UNVERIFIED',finite_samples_not_continuous_time_proof=True)
save('BRIDGE_MOTION_METRICS.json',summary)
md('ENDPOINT_ANATOMY_AND_GEOMETRY.md',f'''
# 端点解剖与实际几何验收

PIANO_C01_G4_E5_NATURAL_MOTION_BRIDGE_R2 · DESIGN_PROVISIONAL

B2按原参数和2.527855秒键状态只读复现，没有重新求解。原Human对中指的初审认可仅授权本轮研究。正式教学仍未通过。原A的Human否决保持有效。

实际Blender求值、原88键几何和Action身份、冻结RIGHT HAND R2 native身份均完成检查，详见 PREFLIGHT_AND_ENDPOINT_DIAGNOSIS.json、ENDPOINT_ACTUAL_1/2.json。B2原样皮肤复现误差见preflight；导出Action后的B2最大顶点差0.00041540mm，终点0.00043028mm，均保留未四舍五入的原始几何布尔值。

原S2中指MCP spread控制约−24.99845°，不属于本轮Human认可的自然参考族，不能因其0.118mm间隙和静态零交叉就作为自然端点。角度均是按rest局部轴恢复的Rig控制；不等同于临床关节角。

| 实际求解 | 参考族 | SLSQP | E5真实指腹接触 | 目标侵入mm | 非目标/非指腹侵入mm | 指面交叉 | 中/无名精确间隙mm |
|---|---|---|---|---|---|---|---|
| #1 | 四长指共享被动R1/R2参考 | 未收敛，status8，17迭代 | 否，距离8.76631mm | {ep[0]['actual_geometry']['target_key_max_depth_mm']:.6f} | 1.546024 | 0 | 见原始JSON |
| #2 | 同参考spread，加中指独立主动屈曲阶段系数 | 收敛，28迭代 | 是 | 0.00508938 | 0 | 0 | 2.89621965 |

#1耗时{sol[0]['elapsed_seconds']:.3f}秒，#2耗时{sol[1]['elapsed_seconds']:.3f}秒。#1的保守被动手型族缺少主动触键屈曲表达；有限失败不能证明Rig或指法不可能。

#2采用有界α将中指三节屈曲从被动参考插值到原S2已审计的铰链屈曲[18.988115,14.196144,7.282417]°，MCP spread约−7.195903°，其余长指仍共享λ参考。PIP/DIP没有新增侧向自由度，未扩大原授权角域。λ=α=1。该主动屈曲锚点有Rig运动依据，但舒适度及整手自然度尚未Human验收；不能称为已证实的人体正常范围。详见 ENDPOINT_SECOND_ATTEMPT_PLAN.json、POLICY_LOCK.json。

端点#2实际映射、参考族误差、原键状态及全皮肤检查通过，作为技术端点进入一次受控连接。其时间为2.956426秒，即E5 ON后35ms，不能替代2.921426秒的边界姿态。

皮肤验收复用既有三角面内部侵入、五指已标识皮肤区域的非相邻三角面交叉和三角面精确距离算法，保留既有拓扑邻接排除规则。精确中/无名间隙沿用原算法与面域，并用采样上界进行候选过滤；不是更换采样距离后与0.11774767mm混比。它是静态分离指标，不是动态安全认证。

STOP — HUMAN REVIEW。
''')
md('STAGED_MOTION_PLAN.md','''
# 分阶段运动与本次实际执行

DESIGN_PROVISIONAL。只制作一个R07→R08候选，范围2.527855–3.349997秒，音乐时间=展示时间−0.35秒。原MIDI、C01指法和88键Action均不改动。

| 边界 | 原Action与要求 |
|---|---|
| 2.492855 R07 ON | 入口上下文，只读检查，手部入口未验证 |
| 2.527855 B2 | 固定已认可研究起点，G4持键 |
| 2.921426 R07 OFF / R08 ON | G4仍全按下，E5角度0；需在换音边界协调接触，不能提前释放G4 |
| 2.956426 ON+35ms | E5全按下，G4回弹至半程；与ON分开验收 |
| 3.349997 E5 OFF | 检查至该边界；不宣称后续释放动画通过 |

意图：当前持键→自然准备→在原事件允许的时刻换位→随原键Action触键并保持。约0.393571秒是B2到换音的可用时间，不能把它全部用于失去G4接触的自由平移。

实际实现：7个时间结点[2.527855,2.72,2.86,2.921426,2.956426,3.14,3.349997]，44个变量；12维局部状态含掌根6维、拇指4维、参考族λ及主动屈曲α。PCHIP斜率生成C1 Hermite轨迹，端部斜率0；在Blender中导出两条独立Action，原键Action保持原样。起点和最终端点固定，后35ms时掌根和长指固定到端点，拇指保留释放自由度。未恢复旧版提前精确E5悬停要求。

29个几何配点：G4持键到精确换音边界，E5从精确换音边界触键；真实指腹局部三角面裁剪构造签名距离约束，活动皮肤见证点/LP内部点约束琴键实体，近面分离轴约束指间。几何代理不是完整网格验收的等价光滑表达；面集合切换仍可不连续，固定活动集也可能过保守。平滑和动作成本仅为次目标。未靠软权重反复修补。

唯一轨迹求解达到280秒硬上限，19迭代，未收敛。最大代理违反约22.3111mm，停滞主要指标位于换音时G4 pad高度/区域失败；不能据此认定冻结Rig或人类指法不可行。对“固定终点拇指释放平面冲突”的怀疑已计算排除：其释放约束余量约+3.5125mm。见 ACTIVITY_PROXY_FAILURE_DIAGNOSIS.json 与 FIXED_ENDPOINT_RELEASE_PROXY_DIAGNOSIS.json。

为独立验收保留这一失败候选并导出Action，没有第二次轨迹拟合。初版导出遗漏对象根原点相对腕部参考点的旋转偏移，且Blender keyframe_insert会合并极近事件；分别改为正确坐标公式和直接FCurve点写入。初版无效几何记录单独保留并排除结论。修正仅涉及同一候选的序列化，没有改变求解状态或新增候选。

实际采样：120Hz基础网格，加精确事件、±0.1/1/4ms近边界和高风险区间补采样，共171个不同实际求值时间点。36个请求的自适应点中35个新增。有限采样不构成连续时间零碰撞证明。

结果已失败，停止优化和视频制作。R06→R07原键最低仍约0.42按压，未完整复位；此前R05手部轨迹及R07 ON到B2段均未新制或验证，因此没有整段连续演奏结论。
''')
md('PRODUCT_ROUTE_CHECK.md',f'''
# 产品路线检查

结论：当前直接从自然静态端点拟合连续轨迹的实现尚不适合扩展到整首MIDI。建议暂停扩大现有拟合，下一步开展同一冻结Rig、同一时序、同一真实几何验收下的成熟碰撞约束IK/姿态先验小范围实际对照；本轮未运行任何外部替代实现，也不宣称外部方法更好。

可复用：固定Rig FK/蒙皮接口、rest轴控制恢复、原Action时钟读取、指腹三角面触键判定、88键内部侵入、指间面交叉、独立Blender Action验收。与旧中指−25°异常相比，本轮把MCP spread及PIP/DIP运动轴约束保留在整个曲线中，171采样未发现参考族越界；这在本例阻止旧机制重现，但不是通用自然手型模型。

仍有特例：G4/E5持键与触键对、7个手选结点、原键35ms下降段、原S2主动屈曲锚点、共享λ/α低维族、活动面阈值、拇指释放辅助平面。并非任意MIDI到动作的通用接口。尤其被动参考族无法直接充当所有主动触键姿态先验；#1→#2端点对照显示增加主动屈曲表达后可取得静态解，但没有单独证明其对动态成功的因果效果。

本次实际证据是：合格静态端点存在，但连续求解未在允许G4持续接触的流形内建立可行路径；实际Action提前失联、提前碰E5并穿键。固定活动集的保守性、接触表示切换、有限差分质量及不可行初始化都可能阻碍SLSQP，尚无消融将单一因素确定为唯一数值根因。可以确定的接口缺口是：缺少由当前持键约束出发、贯穿换音接触状态切换的可行初始化/路径推进，而仅靠两个端点和平滑代价不足。

计算：两个端点共{sum(s['elapsed_seconds'] for s in sol):.3f}秒，0.822142秒短连接单次拟合{a['optimizer']['elapsed_seconds']:.3f}秒，共{total:.3f}秒新增数值求解；轨迹44变量、29配点、1795次约束调用、24533次局部皮肤代理计算，未收敛。独立真实几何验收另耗时{a['check_seconds']:.2f}秒，不混入求解预算。单例不足以估算整曲成本，但当前成本和失败恢复能力没有产品扩展依据。

下一项研究应只回答一个问题：在同一自然参考族与原键Action下，接触状态明确、持键可行域推进的约束IK/姿态先验接口，能否生成兼顾G4持键与E5按时到位的可行初始路径。必须实际运行、用本轮完整几何验收公平对照，不能只比较项目名气。保留现有几何验收基础，不再无目标地重调S1、增加角域或更改C01指法。

本次失败不足以证明C01指法在人类演奏中绝对不可行，亦不足以要求改造冻结Rig。未改指法、未自动发起下一轮。

STOP — HUMAN REVIEW。
''')
md('HUMAN_VISUAL_REVIEW.md',f'''
# Human视觉复核

BRIDGE_MOTION_PARTIAL · DESIGN_PROVISIONAL · STOP — HUMAN REVIEW。

动态技术检查失败，因此没有1倍速或0.5倍速视频。保留6张1280×720实际Blender静帧用于诊断；没有PNG序列缓存。端点两图与Action四图使用相同视向，后者为容纳整手扩大了视野，不能按像素直接量距。

| 文件（stills目录） | 时刻/内容 |
|---|---|
| ENDPOINT_OVERHEAD.png | 新E5端点，ON+35ms，俯视 |
| ENDPOINT_SIDE_OBLIQUE.png | 同端点，侧斜 |
| BRIDGE_START_OVERHEAD.png | B2实际Action起点2.527855秒 |
| EXCHANGE_OVERHEAD.png | 精确换音2.921426秒，失败 |
| EXCHANGE_SIDE_OBLIQUE.png | 同换音，侧斜，失败 |
| PLUS35MS_OVERHEAD.png | 2.956426秒，局部触键通过但不能补偿ON失败 |

待审：新端点的主动中指屈曲与掌腕姿态是否自然；拇指在换位中的打开是否过快；整体准备路线是否像自然手部协调。Human对B2中指的初审认可不扩展到新端点或整个候选。

数据支持的风险：腕部峰值速度{kin['wrist_speed_peak_mm_s']:.3f}mm/s、峰值加速度{kin['wrist_acceleration_peak_mm_s2']:.3f}mm/s²；拇指spread控制峰值约256.912°/s。没有足够临床依据把这些设为统一舒适阈值，保留为视觉风险指标。原始root速度是远离腕部的对象原点速度，应使用汇总JSON中明确区分的腕部、控制平移与对象原点指标。

中指spread全程约−6.732至−7.196°，PIP/DIP没有独立侧向自由度，参考族检查0失败；这不代表Human自然度已通过。中/无名最小精确间隙2.896212mm也不能单独宣称连续动作安全。

图中穿键与接触丢失以实际几何记录为准；静帧不能显示完整速度、加速度或证明动作连续。所有图仅支持失败诊断，不用于教学发布。
''')
md('FINAL_RECOMMENDATION.md',f'''
# 最终结论

**BRIDGE_MOTION_PARTIAL — DESIGN_PROVISIONAL — STOP — HUMAN REVIEW。**

取得一个新的自然参考族内E5静态技术端点，但唯一连续候选没有保持正确的接触和琴键避障。本轮不进入视频、B02、23音或正式教学生产。

| 独立实际Action验收 | 结果 |
|---|---|
| 采样 | 120Hz + 精确事件 + 风险补采样，171个不同时间点 |
| G4首次观察到持键失败 | 2.536188333秒，B2之后约8.333ms |
| E5首次观察到严格指腹表面交叉 | 2.825000秒，比ON早96.426ms |
| 精确ON：2.921426秒 | G4无真实接触；E5有表面交叉但深度超标，完整触键门禁失败 |
| ON+35ms：2.956426秒 | E5局部接触及几何通过；不能追认为ON通过 |
| 目标键最大侵入 | {a['maximum_target_depth_mm']:.9f}mm，门禁0.25mm |
| 全88键非目标/非指腹最大侵入 | {a['maximum_non_target_depth_mm']:.9f}mm，门禁0.25mm |
| 非相邻真实指面交叉 | 最大0对 |
| 中/无名最小精确间隙 | {a['middle_ring_min_exact_mm']:.9f}mm |
| 关节参考族失败 | 0采样；Human整体自然度仍待审 |
| 连续求解 | 19迭代，280.063秒预算停止，未收敛 |

精确换音时E5目标侵入3.654074522mm、非目标/非指腹1.032524219mm；ON后35ms目标侵入约0.004942568mm、非目标0。严格表面交叉并不等于合格接触，更不等于正确起音。首次采样时间只是观测结果，不是对连续触碰时刻的无限精度定位。

新增数值求解共{total:.3f}秒（≤600秒）：2次端点、1次连续候选。没有增加迭代追求PASS。序列化修正未重求解；初版根原点导出错误对应的验收已明确排除。经修正Action实际复现B2/终点，才形成上述结论。

明确建议：保留现有FK和真实皮肤验收接口，暂停扩展当前端点插值式连续拟合，开展接触状态约束IK/姿态先验的同输入小范围实际对照。关键缺口是持键可行路径及换音接触状态的规划接口，不应再自动修补S1或放宽中指侧偏。当前没有证据表明必须更改冻结Rig，也不证明G4(1)→E5(3)在人类演奏中不可行。见 PRODUCT_ROUTE_CHECK.md。

原键Action和冻结身份验证通过；保护文件最终哈希见 PROTECTED_FILES_AFTER.json。R05/R06/R07手部入口没有验证，结论仅覆盖本轮短连接候选。所有资料留在隔离目录，Human审阅后才决定后续研究。
''')
print('SIX_REPORTS_WRITTEN','total_solve',total,'root_fail',summary['root_domain_failed_samples'],'KIN',kin)
