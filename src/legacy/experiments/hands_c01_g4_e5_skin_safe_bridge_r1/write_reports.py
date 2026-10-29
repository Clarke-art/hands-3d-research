import sys,json,hashlib,platform
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent
read=lambda n:json.loads((O/n).read_text(encoding='utf-8-sig'))
A=[read(f'S1_REPAIR_{i}_ACTUAL_VALIDATION.json') for i in [1,2]];R=read('MINIMAL_PREFLIGHT_REGRESSION.json');RB=read('INDEPENDENT_READBACK_CHECKS.json');E=read('ENTRY_CONTEXT_READONLY.json');P=read('POLICY_LOCK.json');ST=read('STILL_MANIFEST.json');total=sum(a['solver']['elapsed_seconds'] for a in A)
assert all(a['status']=='STATIC_BLOCKED' for a in A)
def write(name,text):(O/name).write_text(text.strip()+'\n',encoding='utf8')
def link(name):return '['+name+']('+str(O/name).replace('\\','/')+')'
metrics=dict(task='PIANO_C01_G4_E5_SKIN_SAFE_BRIDGE_R1',status='STATIC_BLOCKED',authority='DESIGN_PROVISIONAL',S1_static_gate_pass=False,static_attempts=A,static_solve_count=2,total_new_numerical_wall_seconds=total,numerical_wall_budget_seconds=900,per_attempt_wall_limit_seconds=140,max_nfev_per_attempt=55,preflight_status=R['status'],S2_exact_clearance=R['S2_exact_clearance'],independent_scene_readback=RB,entry_boundary_status='ENTRY_BOUNDARY_UNVERIFIED',entry_context_file=str(O/'ENTRY_CONTEXT_READONLY.json'),dynamic_phase=dict(executed=False,reason='Both new S1 attempts failed strict actual static gates; stop rule prohibits dynamic attempt',trajectory=None,new_actions=0,new_keyframes=0,validation_120hz_samples=0,contact_timing_measurements=None,wrist_velocity_mm_per_sec=None,wrist_acceleration_mm_per_sec2=None,continuous_collision_claim=False),new_video_count=0,static_still_count=len(ST),diagnostic_blend=str(O/'S1_SKIN_SAFE_REPAIR_DIAGNOSTIC_R1.blend'),runtime=dict(python=platform.python_version(),blender='5.1.2',cpu_only=True,new_dependencies_installed=False),setup_exceptions=[dict(file='setup_encoding_error.log',description='UTF-8 JSON read initially used Windows default encoding; failed before optimizer invocation; fixed explicit UTF-8',optimizer_calls=0),dict(file='verify_1.log',description='Blender interpreted trailing argument 0 as a file after completing actual verification; output saved, later independent scene readback verified it. Second invocation used -- 1')])
write('BRIDGE_MOTION_METRICS.json',json.dumps(metrics,ensure_ascii=False,indent=2))
rows=[]
for a in A:
 c=a['actual_geometry']['contact'];m=a['actual_geometry'];s=a['solver'];rows.append(f"| {a['attempt']} | {c['true_pulp_surface_contact_distance_mm']:.8f} | {c['top_surface_crossing_triangles']} | {c['near_contact_projected_area_mm2']:.8f} | {m['target_key_max_depth_mm']:.8f} | {m['wrong_key_or_nonpulp_max_depth_mm']:.8f} | {m['nonadjacent_self_triangle_pairs']} | {a['E5_preparation']['pad_gap_mm']:.6f} | {s['elapsed_seconds']:.3f} |")
write('S1_STATIC_REPAIR_REPORT.md',f'''
# S1真实皮肤静态修复 — STATIC_BLOCKED

任务：`PIANO_C01_G4_E5_SKIN_SAFE_BRIDGE_R1`。全部新结果为`DESIGN_PROVISIONAL`。本轮只完成两个新增定向静态求解，均未通过；动态阶段未启动。

## 输入与验收合同

复用前轮校准的6596个真实皮肤三角面、冻结FK/蒙皮/原有纠正形变、实际88键几何、原琴键Action与C01固定指法：G4拇指，下一E5中指。9个关键前轮文件与交付清单SHA-256一致，见{link('PREFLIGHT_INPUT_CHECKS.json')}。保护范围中的100个文件在交付前再次核对。没有重跑旧初始化或历史全量审计。

S1沿用原记录展示时间 **2.527855s**，即R07起音后35ms、MIDI源时间2.177855s。原Action此刻G4实际铰链角0.08712320774793625rad；E5为0rad。最终验收读取场景真实88键角度，和记录最大差0rad。没有将琴键统一改成静止位置。

事前锁定{link('CONTRACT_LOCK.json')}：目标实体侵入≤0.25mm，非目标键/目标键非指腹区域侵入≤0.25mm；五指非相邻真实面交叉必须0；完整指腹在可弹顶面有实际接触，真实接触距离≤0.05mm且有顶面交叉/接触证据、近接触投影面积>0；悬空不可通过。pad水平越界≤0.00001mm、辅助pad高度绝对值≤3mm；中指E5准备pad越界≤2mm、高度4–20mm。没有事后放宽。

目标侵入为实体支持平面距离，不是垂直深度；面交叉对数不是毫米；近接触面积为±0.05mm几何薄层投影面积，不是承力接触面积。真实接触由可弹顶面裁剪后的完整指腹三角面验证，不能由pad或顶点代替。

## 原失败原因与最小回归

旧S1第一组：完整面内侵入0.54900234mm，但区域内最低皮肤顶点仍高于键面0.00629804mm。三角面3869的内部侵入见证点被旧顶点代理漏掉。旧第二组：完整面内侵入0.27765371mm；pad水平越界0.00013015mm，亦超过合同；区域内最低顶点高于键面约0.270465mm，裁剪后指腹面最低点却低于键面约0.601402mm。pad所在位置与真正触键的皮肤面足迹并不相同。

{link('MINIMAL_PREFLIGHT_REGRESSION.json')}重新复现两组失败，并通过：已知顶点均在盒外、三角面内部5mm侵入；相切0与安全分离；实际完整皮肤上移的无遮挡**检测器测试夹具**；已知平行面1mm距离、边–边0.1mm距离。测试夹具未作为候选姿态。自然指根/指蹼仅按原共享顶点和拓扑邻接排除，其他88键与完整皮肤都保留检测。

## 两次受控求解

共用事前权重{link('REPAIR_WEIGHT_LOCK.json')}，不随机搜索、不扫描权重。以两组旧S1实际控制参数分别初始化：

1. 保持第一组root Z，替换旧顶点最低高度目标为完整裁剪指腹面的最低高度，取预定-0.005mm微小接触目标；加入旧两组实际面内见证点的固定材质重心坐标约束、指腹面心样本，并将pad限定在可弹区域内侧0.2mm。其他五指仍复用原完整皮肤/琴键顶点和有向近邻代理。
2. 只进行一次真实几何反馈：将第1次出现的9对中指/无名指相交三角面加入分离轴约束。轴来自第二组旧S1中这些面的实际最近特征方向，分离代理目标0.3mm，沿用已有面见证点权重60，未调权重。见{link('SECOND_ATTEMPT_SURFACE_FEEDBACK.json')}。root Z按事前批准的原控制域[-12.2172473,12]mm做一次消融；最终delta Z=-2.410313mm，比第二组初值下降，未靠整体抬高获得“安全”。

这些都是求解代理；最终结果由独立Blender求值后的完整皮肤、88键BVH及真实面内最大侵入LP验收。没有用代理成本替代PASS。

| 新尝试 | 真实指腹距离mm | 顶面接触/交叉三角面 | 近接触面积mm² | 目标实体侵入mm | 非目标/非指腹侵入mm | 非相邻指面交叉对 | E5准备高度mm | 求解秒 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
{chr(10).join(rows)}

第1次pad高度2.276005mm、水平越界0，实际指腹触键成立，目标侵入0.00316273mm，但中指/无名指9对交叉，失败。交叉面IDs及精确键侵入见证点见{link('S1_REPAIR_1_ACTUAL_VALIDATION.json')}。旧有向采样代理无法覆盖所有面–面相交，这是新的明确检测结果。

第2次pad高度0.916223mm、水平越界0，键侵入0、指面交叉0，E5准备高度19.537253mm、越界0.043742mm，但实际指腹最低面距顶面仍 **0.00484241mm（4.84241µm）**，顶面交叉为0，仍悬空。虽然距离在0.05mm近接触薄层内，非零薄层面积**不能证明已经接触**。最接近位置为指腹三角面3869裁剪到可弹区域前缘的面/边点，世界坐标和对应键面坐标见{link('INDEPENDENT_READBACK_CHECKS.json')}，不是pad点。

第2次中指/无名指精确最小间隙另有0.07983220mm，发生于面659/1143，而不是反馈约束中的那9对。有限见证点能消除已知交叉，但尚不能形成可靠的全局安全余量。

## 收敛、证据与停止

第1次21.453s、1055次残差调用、55次nfev；第2次25.703s、1095次残差调用、55次nfev。两者均因nfev上限退出，未数值收敛，最终optimality分别3.42038、16.55279。总新增数值求解 **{total:.3f}s / 900s**；达到“两次新增静态求解”上限后停止，并非耗尽15分钟。完整改进历史、控制状态、代理总成本、面接触残差和见证点残差保留于`REPAIR_ATTEMPT_1.json`、`REPAIR_ATTEMPT_2.json`；逐次实际验收和保存后独立重读证据均保留，没有只留最后结果。

首次启动存在中文JSON编码错误，发生在优化器调用前，修正为UTF-8后运行。首次Blender验收完成后将未用`--`隔开的参数0当作文件，产生退出错误；验收与Blend已成功保存，随后独立重读验证完全一致。两项异常均保留原日志，不隐藏运行问题。

最小剩余违规：第2次真实指腹仍未接触；另有0.07983mm微小指间间隙待Human关注。不能再做额外向下移动、挑选中间迭代或第三次求解来制造PASS。状态 **STATIC_BLOCKED**，未进入短连接、未新增Action/关键帧/视频。隔离Blend含原失败Action的继承参考数据；两个新静态场景没有绑定对象Action。

有限局部求解失败不证明冻结Rig数学上不可行，也没有证据要求改Rig。主要工程缺口是接触硬约束与面级自碰撞约束未完整进入求解器，以及软残差在有限迭代内仍有接触残差；不能将这两条观察扩大成绝对约束矛盾。
''')
write('S2_CLEARANCE_REVIEW.md',f'''
# S2真实面间间隙复核

状态：`STATIC_ONLY_HUMAN_PENDING`，全部为`DESIGN_PROVISIONAL`。没有修改S2或其旧批准状态，也没有进行S2数值求解。

原选中S2（E5中指）的实际求值皮肤快照SHA-256与前轮清单一致。本轮独立加载其旧诊断Blend，顶点与快照一致。既有BVH排除原共享顶点/拓扑相邻后，中指/无名指非相邻面相交仍为0。

旧有限顶点→对侧面采样距离0.13770572mm；本轮精确最近特征距离 **0.11774767mm**，减小0.01995805mm（约14.49%）。顶点采样确实高估了间隙，但没有在该姿态发现非相邻三角面交叉。

方法：对全部中指与无名指语义三角面，用AABB距离下界剪枝；以前轮已有采样距离作为可信上界，370对非相邻面进入精确计算。对每对不相交三角面计算双方所有顶点→面内部、顶点→边及全部9种边–边最短特征距离。最短特征必落于这些组合；上界外的AABB对不可能更近。只排除原自然连接拓扑，不能按当前空间近距离排除。平行面1mm和内部边–边0.1mm校准通过，见{link('MINIMAL_PREFLIGHT_REGRESSION.json')}。

最小间隙三角面IDs **593（中指）/286（无名指）**。两世界坐标见证点（米）：

```json
{json.dumps(R['S2_exact_clearance']['witness_points_world_m'],indent=2)}
```

该计算是给定冻结网格快照的最近表面距离，不含皮肤软组织厚度、压力、Rig轨迹或速度；它没有建立动态安全余量。0.11775mm小于1个720p像素通常可分辨的运动余量，截图无法替代数值判断。邻接排除范围沿用已校准方法，语义未归属的掌根/指蹼仍参与全部键碰撞，但不会被强行当成独立指面。

本轮S1第2次也展示采样局限：采样中指/无名指间距约0.519774mm，真实最近特征仅0.079832mm，面659/1143。下一次经Human授权的工作应将全局近距离面–面候选自适应反馈到求解，并保持独立完整网格验收。不能将S2旧静态通过解释为Human批准或G4→E5动态通过。
''')
visual='\n\n'.join(f"### {x['test']} / {x['view']}\n\n![{x['caption']}]({x['file'].replace(chr(92),'/')})\n\n{x['caption']}" for x in ST)
write('HUMAN_VISUAL_REVIEW.md',f'''
# Human静态审核入口

最终状态`STATIC_BLOCKED`；`DESIGN_PROVISIONAL`。仅5张1280×720静帧，无视频、无新动态Action。

诊断文件：{link('S1_SKIN_SAFE_REPAIR_DIAGNOSTIC_R1.blend')}。打开`S1_REPAIR_1_STATIC_ONLY`或`S1_REPAIR_2_STATIC_ONLY`，均为冻结静态对象状态。该Blend继承的历史源场景/Action只用于参考，不是新短连接成果。S2图来自旧诊断文件的只读加载，不复制推广其姿态。

审核重点：第1组图中的红色标记与真实相交三角面对应，中指/无名指9对非自然连接交叉；标记球上移15mm作定位，不能当作实际碰撞点或侵入深度。第2组无面交叉，但4.842µm悬空在720p图中无法可靠分辨，必须查看数值和三角面3869裁剪点。第2组中指/无名指0.07983mm以及S2的0.11775mm间隙均不足以凭截图宣布动态安全。俯视和斜侧视供审查整体姿态、伸展与前缘触键位置，渲染不用于接触门禁。

所有图均已逐张查看；没有为了看似安全改变手型或键盘。图中文字为诊断叠层，不进入求解或保存的静态控制。

{visual}

**STOP — HUMAN REVIEW。** 不批准连续动作，不自动进入B02或完整双手生产。
''')
write('FINAL_RECOMMENDATION.md',f'''
# 最终结论：STATIC_BLOCKED

**本轮未证明G4拇指安全持键同时中指自然移动到E5可行。** 两次新增定向静态求解均未满足全部S1真实皮肤门禁，因此按前置条件停止；没有生成G4→E5短连接、Action或视频。全部结果保持`DESIGN_PROVISIONAL`。

| 项目 | 实际结论 |
| --- | --- |
| 面级检测是否可靠支撑本轮 | 最小回归通过、旧侵入复现，实际Blender独立验收与保存后重读一致。使用真实88键按压状态和完整求值皮肤；S2增加精确面/边距离。仍不代表软组织/物理认证。 |
| 原S1为什么失败 | 顶点代理未看到三角面内部侵入；第二组还存在pad可弹区域边界问题。 |
| 第1次修复 | 实际触键、目标侵入0.00316mm及E5准备通过，但中指/无名指9对交叉。 |
| 第2次修复 | 键侵入0、指面交叉0、E5准备通过，但真实指腹仍悬空0.00484241mm，无顶面接触；中指/无名指仅0.07983mm间隙。 |
| S2的微小间隙 | 精确0.11774767mm，旧0.13770572mm采样高估，动态安全未知。 |
| 能否断言现有Rig不可行/需更换 | 不能。两次均55nfev未收敛，找到近可行姿态不等于满足接触；没有修改Rig所需的明确证据。 |
| 是否能验证自然G4→E5及腕速/加速度 | 不能；动态阶段未启动，这些量明确为null。 |
| 是否值得增强已有求解器 | 有依据继续：面内约束显著减少目标侵入，真实面反馈能消除已知交叉。但下一次需优先解决实际接触硬约束与自适应全局近面分离，并独立验收；不宜继续靠调软权重和逐指补洞。 |
| 是否自动转向新Rig/IK/完整动画 | 否。先Human审核；若再授权，应对比现有求解器的硬接触/约束式改造或成熟约束求解器的小范围适配，当前没有充分证据决定替换。 |

数值求解共 **{total:.3f}秒**（预算900秒），两个初值、每次55nfev；完整调用数、残差改进历史、控制参数、实际碰撞见证点和收敛状态保留。达到2次上限后立即停止动态工作。另交付5张720p静帧及一份隔离诊断Blend。

入口上下文只读核实：正式时间轴R05 D5展示1.635713–2.064284s，旧1.914284s初始时刻R05仍持键；R06/R07 G4交接2.492855s，原Action此刻G4按压比例约0.42（不是完全复位）；R07/R08交接2.921426s，R08 OFF3.349997s，MIDI源时钟均减0.35s。没有修改事件、提前释放或增加休止。因为没有新安全起点和释放/重按轨迹，保持 **ENTRY_BOUNDARY_UNVERIFIED**，原键部分复位不能代替手指运动验证。

下一步建议仅供Human选择：保持冻结资产和C01，在新授权下将真实指腹接触设为显式约束/接触保持，并采用自适应近面候选的分离约束，确认至少一组严格S1通过及可接受指间余量后再讨论单条短连接。本轮不执行这些后续动作，也不挑选/修补中间结果升级为PASS。

主要证据：{link('S1_STATIC_REPAIR_REPORT.md')}、{link('S2_CLEARANCE_REVIEW.md')}、{link('BRIDGE_MOTION_METRICS.json')}、{link('HUMAN_VISUAL_REVIEW.md')}。

**STOP — HUMAN REVIEW。**
''')
protected=read('PROTECTED_FILES_BEFORE.json');after={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in protected};unchanged=after==protected;assert unchanged,'Protected asset changed'
write('PROTECTED_FILES_AFTER.json',json.dumps(dict(unchanged=True,checked_count=len(after),hashes=after),indent=2))
manifest=[]
for p in O.rglob('*'):
 if p.is_file() and p.name!='DELIVERY_MANIFEST.json':manifest.append(dict(file=str(p.relative_to(O)),size_bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
write('DELIVERY_MANIFEST.json',json.dumps(dict(task=metrics['task'],status='STATIC_BLOCKED',authority='DESIGN_PROVISIONAL',files=manifest,protected_files_unchanged=unchanged,protected_count=len(after),stills=5,videos=0,new_actions=0),indent=2))
print('FINAL_DELIVERY',len(manifest),'files',len(after),'protected unchanged','numerical_seconds',total,flush=True)
