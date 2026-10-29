import sys,json,hashlib,platform
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O))
from skin_proxy import *
OLD=O.parent/'hands_c01_g4_e5_skin_safe_bridge_r1'
def read(name):return json.loads((O/name).read_text(encoding='utf-8-sig'))
def old(name):return json.loads((OLD/name).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(name,x):(O/name).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
def link(name):return f'[{name}](<{(O/name).as_posix()}>)'
solves=[read(f'SOLVE_{i}.json') for i in [1,2]];actual=[read(f'ACTUAL_VALIDATION_{i}.json') for i in [1,2]];supp=read('INDEPENDENT_DISTANCE_AND_PARITY.json');rb=read('READBACK_2.json')
assert all(actual[1]['gates'].values()) and solves[1]['convergence']['success']
assert rb['max_vertex_difference_mm']<.001 and rb['native_identity_verified']
rm=rb['actual_geometry'];assert rm['contact']['top_surface_crossing_triangles']>0 and rm['contact']['true_pulp_surface_contact_distance_mm']==0 and rm['target_key_max_depth_mm']<=.25 and rm['wrong_key_or_nonpulp_max_depth_mm']<=.25 and rm['nonadjacent_self_triangle_pairs']==0
protected=read('PROTECTED_FILES_BEFORE.json');after={p:sha(Path(p)) for p in protected};mismatch=[p for p in protected if after[p]!=protected[p]]
assert not mismatch,mismatch
dump('PROTECTED_FILES_AFTER.json',dict(unchanged=True,checked_count=len(after),mismatches=mismatch,hashes=after))
stills=read('STILLS_1.json')+read('STILLS_2.json');assert len(stills)==4
for item in stills:item['sha256']=sha(Path(item['file']))
dump('STILL_MANIFEST.json',stills)
sources=[
dict(candidate='SciPy SLSQP',scope='public documentation, locally executed installed version',urls=['https://docs.scipy.org/doc/scipy/reference/optimize.minimize-slsqp.html','https://docs.scipy.org/doc/scipy/reference/optimize.minimize-trustconstr.html'],executed=True),
dict(candidate='Mink',scope='read-only public source and documentation; not installed or run',urls=['https://github.com/kevinzakka/mink','https://raw.githubusercontent.com/kevinzakka/mink/main/src/mink/limits/collision_avoidance_limit.py','https://raw.githubusercontent.com/kevinzakka/mink/main/pyproject.toml','https://raw.githubusercontent.com/kevinzakka/mink/main/LICENSE'],license='Apache-2.0',executed=False),
dict(candidate='Pink',scope='read-only public source and documentation; not installed or run',urls=['https://github.com/pink-kinematics/pink','https://raw.githubusercontent.com/pink-kinematics/pink/main/pink/barriers/self_collision_barrier.py','https://raw.githubusercontent.com/pink-kinematics/pink/main/pyproject.toml','https://raw.githubusercontent.com/pink-kinematics/pink/main/LICENSE'],license='Apache-2.0',executed=False),
dict(candidate='Drake',scope='read-only public source and documentation; not installed or run',urls=['https://drake.mit.edu/pydrake/pydrake.multibody.inverse_kinematics.html','https://drake.mit.edu/installation.html','https://raw.githubusercontent.com/RobotLocomotion/drake/master/LICENSE.TXT'],license='BSD-3-Clause plus third-party component licenses',executed=False)]
dump('RESEARCH_SOURCES.json',sources)
import scipy
deps=dict(python_executable=sys.executable,python_version=platform.python_version(),numpy_version=np.__version__,numpy_path=np.__file__,scipy_version=scipy.__version__,scipy_path=scipy.__file__,newly_installed_dependencies=[],blender_executable='D:/blender/blender.exe',blender_version='5.1.2',reused_existing_dependency_directory=str(ROOT/'audits/midi_driven_dual_hand_piano_performance_poc_r1/_deps'),reused_source_modules=[str(ROOT/'audits/midi_driven_dual_hand_piano_performance_poc_r1/performance_core.py'),str(ROOT/'audits/minuet_stage_c_r6_whole_phrase_spatial_planning/whole_phrase_model.py'),str(O.parent/'hands_c01_whole_hand_motion_feasibility_r1/blender_utils.py')],note='No external IK installed. Frozen geometry/proxy/distance code and data copied into this isolated directory; existing numerical dependencies reused read-only.')
deps['reused_source_sha256']={p:sha(Path(p)) for p in deps['reused_source_modules']}
dump('DEPENDENCY_MANIFEST.json',deps)
total=sum(s['elapsed_seconds'] for s in solves);status='CONSTRAINED_S1_PASS'
result=dict(task='PIANO_C01_S1_CONSTRAINED_SOLVER_FEASIBILITY_R1',status=status,authority='DESIGN_PROVISIONAL',technical_decision='A',stop='STOP — HUMAN REVIEW',selected_attempt=2,test_problem='R07 G4 thumb real hold + middle E5 preparation',display_time_sec=2.527855,source_midi_time_sec=2.177855,original_key_action_required=True,budget=dict(max_new_solve_wall_seconds=600,actual_new_solve_wall_seconds=total,main_solves=2,max_main_solves=2,supplementary_solves=0,includes_setup_and_derivative_probe=True,per_solve_wall_limit_seconds=240,retry_count=0),attempts=[dict(solve=s,independent_blender=a,supplement=supp['attempts'][i]) for i,(s,a) in enumerate(zip(solves,actual))],selected_saved_blend=str(O/'S1_CONSTRAINED_DIAGNOSTIC_R1.blend'),independent_saved_blend_readback=rb,previous_results_readonly=[dict(attempt=i,solver=old(f'REPAIR_ATTEMPT_{i}.json'),independent_blender=old(f'S1_REPAIR_{i}_ACTUAL_VALIDATION.json')) for i in [1,2]],distance_regression=supp['S2_readonly_distance_regression'],previous_hover_supplement=supp['previous_second_repair_hover_true_distance_supplement'],source_protection=dict(unchanged=True,checked_count=len(after)),visual_naturalness='HUMAN_PENDING',continuous_motion_safety='NOT_EVALUATED',external_solvers_run=0,external_solvers_researched=3,static_success_rate_observed='1/2 new methods; not a statistical reliability estimate',no_root_z_ablation=True,no_animation_generated=True,stills=stills)
dump('S1_CONSTRAINED_RESULTS.json',result)
a=actual[1];ct=a['actual_geometry']['contact'];mr=a['middle_ring_exact_clearance'];delta=np.array(solves[1]['state'])-np.array(solves[1]['initial_state'])
root_cause="""# S1 求解器约束与数值原因复核

任务：PIANO_C01_S1_CONSTRAINED_SOLVER_FEASIBILITY_R1。全部候选 DESIGN_PROVISIONAL。历史复核为只读，本轮计算另存。旧系统没有把接触和完整面级避障作为必须满足的可行性条件；有限优化失败不证明Rig不可行。本轮第二次找到实际合格静态姿态。

## 已有证据

旧solve_static_skin.py使用有界least_squares，目标为残差平方和。原权重：指腹顶点接触15、pad内部12、高度区间3、preferred XY 0.1、皮肤键顶点避障20、采样有向自碰撞8、关节先验0.012、root XY先验0.012、root旋转0.04、E5准备1.5。非目标期望间隙0.6mm、接触期望-0.005mm。只有变量bounds是明确约束。

上一轮repair_s1.py继承这些代理，新增/替换完整指腹面裁剪接触25、键面材质见证点60、pad内缩0.2mm、面见证允许侵入0.05mm、E5中心偏好0.25和准备区间8。第二次9对指面分离轴沿用权重60、目标0.3mm。它们仍是残差，没有constraints；加权不能保证有限预算内残差为零。

历史第一次：4个顶面接触/交叉面、目标内部侵入0.00316273mm、非目标/非指腹0；中指/无名指9对真实面交叉。历史第二次交叉和侵入0，原指腹裁剪足迹距离0.00484241mm、顶面交叉0、真实接触布尔false。1055/1095次残差调用，nfev均55，optimality 3.42038/16.55279，上限退出、未收敛。Z条件不同：第一次固定，第二次开放，最终下降到-2.410312964847451mm；不能单因果归因于碰撞反馈。

## 确认的限制与未确认的根因

- 第一次有向近邻代理每5个指顶点采样，匹配对侧面心而非最近特征；不枚举全部边–边/面–面。BVH发现9对交叉，确认覆盖不足；不能声称这些时刻代理每项都为零。
- 第二次接触仍是加权残差；终止时代理最小高度+0.0046800094mm，实际原指标+0.00484241mm，均悬空，明确未达到-0.005mm目标。哪一个先验/避障/准备项主导尚无因果消融证据。
- 预算停止已确认；局部停滞/目标冲突可能，但缺少旧活动集和梯度谱，不能宣称根因已确定。
- clip、min/max、最近面切换与采样8mm激活阈值产生分段/不连续行为；交叉计数是离散量。这是代码性质，未证明具体哪次切换触发旧失败。
- 旧默认有限差分未保存梯度一致性检查，未提供解析完整蒙皮Jacobian。新种子中心差分0.001与0.0005相对Frobenius差3.30e-10/1.46e-7，局部稳定，不能倒推旧轨迹可靠。

## 本轮实验确认

新#1将无交叉第二种子的轴用于第一种子的局部域，初始最小轴间隙-5.06817873mm；实际9对交叉无法换算为5mm深度。固定键平面初始余量-0.51485333mm也可能错误拒绝安全跨角面。SLSQP退出码8，最终实际交叉0、却悬空0.0553108877mm。证明这种保守表示不能直接恢复该局部姿态，不证明真实约束不可行。

新#2从历史第二次完整最终状态初始化，固定其Z；琴键改用原面内LP，分离轴来自自身附近。2次迭代收敛并通过完整Blender静态门禁。两种新尝试同时改变种子与表示，不能分别估计贡献；这是局部可行性证据，不是任意初始化的成功率结论。

## 可复用接口

冻结FK/蒙皮rest、relative matrices、LOCAL、SHLOCAL和纠正形变可复用；没有现成解析完整皮肤Jacobian。本轮每列有限差分共享整向量几何。旧键面见证有面ID和重心坐标，精确三角距离有双方最近点，可构建分离轴。完整BVH/面内LP/原指腹clip继续独立验收。

补测完整指腹到完整可触矩形欧氏距离：旧第二次0.0042602260mm，与原0.00484241mm裁剪足迹法向指标的域不同。原数值及false不改写，两种距离均不能把悬空追认为接触。
"""
design="""# 显式约束求解设计与实际执行

全部DESIGN_PROVISIONAL。仅R07 G4拇指持键+中指E5准备，展示2.527855s；G4原角0.08712320774793625rad、E5为0。C01、冻结R2、88键几何/Action和MIDI时钟不变。

## 变量与算法

状态26项：root XYZ(mm)、额外旋转XYZ(deg)、五指各4项原授权关节增量(deg)。删除Z后优化25项，分别固定两个历史最终种子的Z，没有Z消融。原界XY [-150,-30]至[60,35]mm、旋转±[8,8,12]deg、原静态R2关节界；再与局部XY±1mm、旋转±2deg、关节±3deg求交。每项bounds和完整state保存。

采用SLSQP原生ineq字典，maxiter60、ftol1e-8、每次240s、累计600s。25变量且种子接近可行；本轮未运行trust-constr或外部求解器，不声称它们性能更差。NonlinearConstraint只是接口，不能令计数可微。目标仅0.5*||x-x0||²，几何条件进入constraints，没有几何残差调权；合格优先于姿态成本。

## 接触和准备

原完整指腹三角面clip到可触矩形，最小有符号高度g约束-0.020≤g≤-0.005mm；小负裕量覆盖已观测亚微米proxy/Blender差异，0.25mm侵入门禁不改。另要求指腹正侧高度、pad在原区域内部0.01mm、辅助pad高度绝对值≤3mm。负侧/正侧点不保证属于同一面，因此代理不是全域接触拓扑等价证明；最终必须用实际完整面交叉原布尔验收。不能用“距离小”或薄层面积代替接触。

E5原pad在原矩形外扩2mm内、法向高4–20mm。逐轴扩2mm在角点比原欧氏越界≤2mm更宽，不宣称严格全域等价；最终保留原欧氏条件。本轮实际越界0.042103mm，差异不影响PASS。

## 琴键实体侵入

#1对近键面选择一个固定支持平面，全部三个顶点到平面≥-0.20mm。足以限制面内侵入但比0.25mm条件更强，安全跨角面可被拒绝；该表示失败、不推荐保留。

#2直接复用原triangle_inside_depth：面内最大支持平面实体深度≤0.20mm，为原0.25mm留裕量。三变量LP用重心二坐标+深度，枚举活动多面体顶点；非面心/顶点样本。按原88键角度构造凸块，521个近键面/块组合。种子面AABB对块外扩5mm过滤，全部皮肤顶点约束位移≤4mm，三角面内部点也≤4mm，因此被排除面在该域不可能触及块。目标、非目标及目标非指腹同用更严0.20mm条件，最终全88键原0.25mm验收。

LP活动集和极值切换使函数分段可微，浮点容差沿用检测器，不称光滑签名距离场。

## 指间避障

五指10种配对，原语义面及共享顶点/拓扑邻居排除不变；取两个种子AABB≤1mm近面并加入历史9对。无交叉种子的精确最近点形成轴n，min(Ta·n)-max(Tb·n)≥0.020mm。进入池的面有保守真实分离条件，是明确不等式。#1有1265对，#2有605对。

固定1mm池未与允许4mm位移形成全局排除证明，不能担保未入池面；最终独立完整BVH检查全部非邻接面。合格姿态依赖该oracle反馈门禁，不能单凭数值约束接受。本轮无重启、无第三次求解。未来产品需活动池更新或最大闭合距离证明，避免漏过检测带。

## Jacobian和独立验证

中心差分0.001mm/deg；整向量共享FK/皮肤，缓存控制点；步长减半诊断计入求解预算。没有解析Jacobian复用主张。目标nfev、nit与实际几何调用分开记录。

独立Blender进程从原源场景同时间读取88键Action payload、角度、实际几何；复制场景后施加控制，取消复制对象绑定Action，不新增关键帧。native冻结身份核对，实际求值完整皮肤用原全键BVH、面内LP、clip接触、五指自交与E5验收。通过才存诊断Blend并重读。原源文件不保存。

四项判断分开：优化收敛、几何全部通过、Human自然度、动态安全；末两项仍待审/未验证。Blender与外部Python ABI不一致，最初验收误导入SciPy报错；修复为实际快照外部补测proxy误差，无重新优化。原错误日志保留。

## 精确距离

中指/无名指沿用上一轮完整特征枚举：双方点–面、顶点–边、9种边–边，采样作上界、AABB作下界，仅原拓扑排除。只读S2回归0.11774766739016501mm完全复现。新#2 S1为0.07986473418668923mm，差-0.03788293320347578mm来自姿态不同。

完整指腹至键面额外穷举142个原指腹面与完整可触矩形三角化，包含矩形边角外最近点；域与原clip法向距离不同。新#1原距离0.0553108877mm、完整欧氏0.0453407288mm，交叉0且布尔false。合格#2由原独立面交叉确认精确0。Float64作用于Blender求值坐标，特征枚举精确、浮点实现，不是形式化精确算术。区域和皮肤都未改。
"""
comparison="""# 求解方法与适配证据对照

路线A实际2次；路线B仅调查3个候选，均未安装/运行，没有外部对照PASS。

| 方法 | 约束语义 | 实际证据 | 建议 |
| --- | --- | --- | --- |
| 原least_squares及修复 | bounds+加权接触/采样碰撞 | 2次nfev55未收敛，接触/交叉互换或悬空 | 几何可行性迁出残差 |
| SLSQP #1 | 明确ineq、过强固定轴/平面 | 11.500s、退出8；实际安全但悬空 | 不沿用这种恢复表示 |
| SLSQP #2 | 面内LP、接触区间、近面分离+全网格门禁 | 22.765s、2迭代、静态PASS、重读通过 | 保留局部静态内核 |
| Mink/Pink/Drake | 成熟机器人约束IK架构 | 只读调查，冻结Rig未运行 | 无外部优越性结论 |

[官方SLSQP文档](https://docs.scipy.org/doc/scipy/reference/optimize.minimize-slsqp.html)用于明确constraints、Jacobian和停止条件；本地版本记录于DEPENDENCY_MANIFEST.json，网页版本不是运行版本。[trust-constr文档](https://docs.scipy.org/doc/scipy/reference/optimize.minimize-trustconstr.html)仅选型，未实际比较性能。

## Mink — 只读

[Mink](https://github.com/kevinzakka/mink)有关节界和碰撞限制。[碰撞限制源码](https://raw.githubusercontent.com/kevinzakka/mink/main/src/mink/limits/collision_avoidance_limit.py)用MuJoCo距离及法向Jacobian构成QP不等式；检测带须覆盖一步闭合距离，有parent/weld过滤。这与原皮肤拓扑排除不同。接触帧任务不等于原指腹真实接触，需要自定义皮肤约束/oracle。

[构建配置](https://raw.githubusercontent.com/kevinzakka/mink/main/pyproject.toml)含MuJoCo、qpsolvers/DAQP和Windows AMD64构建；本机未安装验证。需原骨架自由度映射MJCF或自定义约束Jacobian桥接，多骨蒙皮/纠正形变不能由刚性geom直接复现。公平验证仍需原Blender网格，不能换手模型。估计适配中至高，未测工时。[Apache-2.0](https://raw.githubusercontent.com/kevinzakka/mink/main/LICENSE)允许商业使用和修改/分发，须保留许可/所需NOTICE并标记修改，专利/商标及依赖边界另核对。

## Pink — 只读

[Pink](https://github.com/pink-kinematics/pink)为加权任务差分IK QP，含配置/速度界。[自碰撞barrier源码](https://raw.githubusercontent.com/pink-kinematics/pink/main/pink/barriers/self_collision_barrier.py)用FCL距离/最近点Jacobian，声明非光滑几何行为未定义，可只取最近若干对。当前6596三角面和蒙皮不自动满足光滑凸体假设。需Pinocchio原骨架映射、自定义皮肤Jacobian、硬接触接口和原过滤。

[依赖配置](https://raw.githubusercontent.com/pink-kinematics/pink/main/pyproject.toml)含Pinocchio/qpsolvers，仓库pixi表未列Windows，这不证明全部Windows安装不可行；本机兼容性未试。适配中至高。[Apache-2.0](https://raw.githubusercontent.com/pink-kinematics/pink/main/LICENSE)商业边界同上，Pinocchio/FCL/QP依赖逐项核查。

## Drake — 只读

[官方IK API](https://drake.mit.edu/pydrake/pydrake.multibody.inverse_kinematics.html)有显式位置和MinimumDistanceLowerBound/UpperBound，但至少一对距离上界不自动指定原指腹/可触区域，仍需完整皮肤验收。需MultibodyPlant骨架映射和SceneGraph蒙皮桥接，刚性几何不能替代原真实网格。

[官方平台](https://drake.mit.edu/installation.html)列Linux/macOS、无Windows原生支持；WSL/系统转换或重建超出轻量验证。[BSD-3-Clause](https://raw.githubusercontent.com/RobotLocomotion/drake/master/LICENSE.TXT)允许商业使用/修改/分发，保留声明、不以作者名背书；第三方/可选商业优化器另核查。适配高，不部署。

## 公平性与成本

新#2从历史失败#2最终完整状态初始化，固定Z/原FK/皮肤/Action，证明局部修复可行；不是从相同原始C01分别重跑的统计实验。新#1/#2同时改变种子和表示，不能估计LP的单独贡献。

旧两次47.156s，新两次34.265s（含准备和差分诊断）。新#2 nfev2是目标调用，实际约束求值205；新#1目标84、约束987；旧残差1055/1095。不能仅比较55和2宣称27.5倍加速。本轮总墙钟未明显更慢，但22.8秒近可行单姿态不能外推整首MIDI效率。产品需共享解析Jacobian、活动集更新/步长约束、跨音缓存与失败闭锁，未做吞吐验证。外部方案没有实际更好的证据。
"""
metrics='\n'.join(f"| {i+1} | {s['convergence']['success']} / {s['convergence']['status']} | {s['convergence']['nit']} | {s['elapsed_seconds']:.3f} | {aa['gates']['actual_surface_contact']} | {aa['actual_geometry']['contact']['true_pulp_surface_contact_distance_mm']:.10f} | {aa['actual_geometry']['target_key_max_depth_mm']:.10f} | {aa['actual_geometry']['wrong_key_or_nonpulp_max_depth_mm']:.10f} | {aa['actual_geometry']['nonadjacent_self_triangle_pairs']} | {aa['E5_preparation']['pad_gap_mm']:.8f} |" for i,(s,aa) in enumerate(zip(solves,actual)))
final=f"""# 最终技术建议 — {status}

**A — 保留现有求解器体系，采用第二次已验证的约束式局部改造。** 保留原冻结FK/蒙皮/oracle和SciPy环境；几何条件迁入SLSQP显式ineq。第一次固定键平面/跨姿态固定轴表示不保留。全部候选DESIGN_PROVISIONAL。**STOP — HUMAN REVIEW**。

## 实际结果

| 尝试 | 优化收敛/状态 | nit | 求解秒 | 原始接触布尔 | 原距离mm | 目标侵入mm | 非目标/非指腹mm | 指面交叉对 | E5高度mm |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
{metrics}

合格#2指腹顶面接触/交叉2面（3869、3870），完整指腹到可触键面精确欧氏距离0，近接触投影面积{ct['near_contact_projected_area_mm2']:.10f}mm²；pad水平越界0、辅助高度{ct['pad_gap_mm']:.10f}mm；E5越界{a['E5_preparation']['pad_horizontal_outside_mm']:.10f}mm。全88键和五指10对BVH检查已执行，native、原Action/键几何核对通过。保存后顶点重读差{rb['max_vertex_difference_mm']}mm、几何复验一致。

Z固定{solves[1]['root_Z_fixed_mm']:.15f}mm，较旧#2变化0；其余最大控制改变量{float(np.max(abs(delta))):.10f}mm或deg。未抬高手掌、缩皮肤、更改区域/键位或拉长手指。旧#2悬空0.00484241mm与false原样保留。

2次主要求解累计**{total:.3f}s / 600s**，含池构建和差分诊断。无额外消融/重试、随机搜索、调权或挑中间迭代。第一次失败完整保留。Mink/Pink/Drake只读调查，安装/对照运行数0。

## 推荐范围

采用#2原面内LP、完整指腹接触区间和局部分离ineq，加完整Blender失败闭锁门禁。证明当前冻结Rig存在合格S1静态姿态；不证明任意初始化稳定，观察1/2不是成功概率。

1mm固定活动池尚未覆盖全部允许运动域，不能单独称为全局等价碰撞约束。后续技术关注应集中“活动面覆盖与每步闭合距离证明/更新”，不继续无目标调残差。没有证据要求改Rig或直接迁往未运行外部方案。

中指/无名指精确间隙**{mr['distance_mm']:.10f}mm**，比旧#2约0.07983220mm略增，比S2的0.1177476674mm小0.0378829332mm。静帧不能建立运动余量。优化收敛、几何通过、视觉自然和连续运动安全独立：前两项已验证，Human视觉待审，动态未验证。

本轮未明显变慢，但22.8s单个近可行姿态不足以证明整曲产品性能。解析皮肤Jacobian/活动池更新属于后续工程成本，本轮不自动开展。

## 交付和保护

{link('S1_SOLVER_ROOT_CAUSE.md')}、{link('CONSTRAINED_SOLVER_DESIGN.md')}、{link('EXISTING_SOLVER_COMPARISON.md')}、{link('S1_CONSTRAINED_RESULTS.json')}、{link('HUMAN_VISUAL_REVIEW.md')}。

{len(after)}项保护哈希不变；4张720p静帧与1份独立诊断Blend。复制诊断文件继承源参考Actions，两个实验场景本身无绑定Action/新关键帧；未生成新动画。Stage A/B/C、四批准姿态、C01、MIDI、冻结资产和两轮失败证据不改写。

**STOP — HUMAN REVIEW。** 不自动进入B02、G4→E5桥接、23音双手动画或视频。
"""
human=f"""# Human视觉审查 — DESIGN_PROVISIONAL

**CONSTRAINED_S1_PASS / STOP — HUMAN REVIEW。** S1时间2.527855s，四张实际Blender求值网格1280×720静帧。源左手在边缘作为继承参考，不代表本轮左手实验。没有视频。

## 合格#2

![S1 #2俯视](<{(O/'stills/S1_2_OVERHEAD.png').as_posix()}>)

![S1 #2侧斜](<{(O/'stills/S1_2_SIDE_OBLIQUE.png').as_posix()}>)

模型已查看两张：标签可读、原手和键盘可见；俯视中中指/无名指投影重叠不等于3D交叉。完整面交叉0，精确间隙{mr['distance_mm']:.10f}mm。侧斜显示扁平伸展与紧密指群，尚未判定教学自然度。

待Human审查：

- 拇指在G4可触键前缘，有2面真实接触。0.0516753676mm²为±0.05mm薄层投影，不是压力/承力面积；是否适合持键教学。
- E5准备高度19.52785820mm接近20mm上限；中指准备、腕部和掌部倾斜是否自然。
- 中指/无名指间隙0.07986473mm非常小，画面无法验出运动安全。
- 五指整体间距和指腹触键视觉是否可接受。几何通过不替代审美/教学判断。

## 失败#1保留

![S1 #1俯视](<{(O/'stills/S1_1_OVERHEAD.png').as_posix()}>)

![S1 #1侧斜](<{(O/'stills/S1_1_SIDE_OBLIQUE.png').as_posix()}>)

原真实接触false、交叉0、原clip距离0.0553108877mm；完整键面欧氏距离0.0453407288mm即使小于0.05mm仍不能通过。实际侵入/交叉0、优化线搜索失败，不追认为PASS。

图像SHA见STILL_MANIFEST.json，文字与网格边线为诊断展示；皮肤/区域/键位不改。候选#2Blend保存后独立重读，旧失败文件只读。

**STOP — HUMAN REVIEW。** Human未批准自然度、整曲使用或动态阶段。
"""
for name,body in [('S1_SOLVER_ROOT_CAUSE.md',root_cause),('CONSTRAINED_SOLVER_DESIGN.md',design),('EXISTING_SOLVER_COMPARISON.md',comparison),('FINAL_RECOMMENDATION.md',final),('HUMAN_VISUAL_REVIEW.md',human)]:(O/name).write_text(body+'\n',encoding='utf8')
print('FINAL_STATUS',status,'DECISION A','solve seconds',total,'protected',len(after))
