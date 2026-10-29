import json,hashlib,sys,ast
from pathlib import Path
O=Path(__file__).resolve().parent
load=lambda n:json.loads((O/n).read_text(encoding='utf-8-sig'))
def md(n,s):(O/n).write_text(s.strip()+'\n',encoding='utf8')
def js(n,x):(O/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
a=load('ACTUAL_DISCRETE_VALIDATION.json');final=load('FACE_WITNESS_SOLVER_RUNS.json');initial=load('DISCRETE_SOLVER_RUNS.json');fix=load('MINK_CORRECTED_RUNS.json');allruns=initial+fix+final;total=sum(r['elapsed_seconds'] for r in allruns);runtime=load('RUNTIME_DEPENDENCIES.json');contract=load('CONTACT_STATE_SEQUENCE.json');old=load('ACTUAL_VERTEX_PROXY_VALIDATION.json');base=next(r for r in a['results'] if r['phase']=='P1');rows=[]
for r in a['results']:
 s=r['solver'];g=r['geometry'];rows.append(dict(phase=r['phase'],method=r['method'],actual_PASS=r['all_geometry_and_joint_gates'],real_pulp_contact=r['gates']['strict_pulp_contact'],target_depth_mm=g['target_key_max_depth_mm'],non_target_or_nonpulp_depth_mm=g['wrong_key_or_nonpulp_max_depth_mm'],self_crossings=g['nonadjacent_self_triangle_pairs'],middle_ring_gap_mm=r['middle_ring_exact']['distance_mm'],middle_E5_reference_distance_mm=r['middle_pad_distance_to_E5_reference_mm'],contact_violations=int(not r['gates']['strict_pulp_contact']),anatomy_violations=int(not(r['gates']['natural_reference_family'] and r['gates']['authorized_axes'] and r['gates']['authorized_control_domain'])),solve_seconds=s.get('elapsed_seconds',0),iterations=s.get('iterations',0),wrist_shift_from_B2_mm=[1000*(x-y) for x,y in zip(r['wrist_world_m'],base['wrist_world_m'])]))
stages={name:{k:(name=='Mink' or k=='SOURCE_REVIEWED') for k in ['SOURCE_REVIEWED','TOOL_INSTALLED','TOOL_SMOKE_TESTED','REAL_RIG_ADAPTER_EXECUTED','CONTACT_CONSTRAINT_TESTED']} for name in ['Mink','Pink','Drake']}
result=dict(task='PIANO_CONTACT_STATE_MOTION_PLANNER_COMPARISON_R1',authority='DESIGN_PROVISIONAL',gates=dict(CONTACT_STATE_CONTRACT_PASS=True,DISCRETE_STATE_FEASIBILITY_PASS=True,EXTERNAL_IK_COMPARISON_EXECUTED=True),scope='DISCRETE_STATE_FEASIBILITY_ONLY',continuous_path_pass=False,continuous_junction_compatibility='UNVERIFIED',physical_force_and_acoustic_attack='NOT_MODELLED',recommendation='A',tool_stages=stages,runtime_dependencies=runtime,summary=rows,actual_Blender_results=a,all_numerical_calls=allruns,pre_correction_actual_results=old,numerical_budget=dict(total_inner_solve_wall_seconds=total,successful_launch_command_wall_seconds=6.9669242+4.1820663+6.1065643,limit_seconds=600,counts=dict(initial=4,interface_step_correction=2,face_witness_correction=4),no_old280s_rerun=True,no_continuous_candidate=True,setup_excluded_from_inner_timer=True),adapter_scope='Mink Task/Limit callbacks consume frozen FK and weighted skin in12 real Rig control coordinates. MuJoCo model is only scalar configuration carrier. Native MuJoCo skeleton FK and collision avoidance are NOT exercised.',interface_corrections=['3mm equality vs0.5mm trust step caused QP infeasibility; corrected once without anatomy/geometry relaxation','Both solvers satisfied vertex equality but actual pulp hovered; one face-barycentric witness correction validated independently'],fairness=dict(same_inputs_and_latent_family=True,same_geometry_constraints=True,same_initialization_per_phase=True,SLSQP_iterations='nonlinear iterations',Mink_iterations='differential IK iterations dt0.01 is pseudo-time, not MIDI elapsed time',Mink_additional_trust_bounds=True,repeat_statistics=False,P3_feasible_seed=True,no_global_advantage_claim=True),contact_state_sequence='CONTACT_STATE_SEQUENCE.json',reuse_tests='CONTRACT_REUSE_TESTS.json',stop='STOP — HUMAN REVIEW')
js('MINIMAL_FEASIBILITY_RESULTS.json',result)
md('CONTACT_STATE_CONTRACT.md','''
# 接触状态合同 R1

CONTACT_STATE_CONTRACT_PASS · DESIGN_PROVISIONAL。表示层通过独立校验；不等于整条运动通过。

正式MIDI已从原二进制重新解析，23音的46条NOTE_ON/OFF逐项与原绑定核对。源哈希、PPQ384、恒定tempo428571μs/拍和C01指法身份见 SOURCE_MIDI_REVALIDATION.json。原Blender琴键Action重新求值，并核对原Action payload和冻结Rig身份；没有只依据上一轮文字报告推断机械过程。见 ORIGINAL_ACTION_INSPECTION.json。

三套时间分别保留：MIDI tick/音乐秒、展示秒=音乐秒+0.35、原键Action的实际角度/表面位置。接触状态是规划义务，不是由音符音高直接指定的三维姿态，也不是力度估计。

| 展示时间 | G4角rad | E5角rad | 合同解释 |
|---|---|---|---|
| 2.492855 | 0.036591746 | 0 | R07重复音开始，G4未完全回弹 |
| 2.527855 | 0.087123208 | 0 | B2持G4，E5可自由准备 |
| 2.921426 | 0.087123208 | 0 | R07义务结束、R08 PRESS开始，G4开始恢复、E5开始下压 |
| 2.956426 | 0.043561604 | 0.087123208 | E5全按下；不是ON瞬间 |
| 2.991426 | 0 | 0.087123208 | G4恢复完成 |
| 3.349997 | 0 | 0.087123208 | E5音符结束，尚未立即复位 |
| 3.419997 | 0 | 0 | E5恢复完成 |

| 状态 | 接触义务 | 机械与掌腕/切向规则 |
|---|---|---|
| FREE | 无 | 无活动接触时可整手移动，仍受关节/全部琴键/指面避障限制 |
| APPROACH | 无；可选PRE_TOUCH | 下一手指准备不能解除当前其他手指的HOLD。无提前精确悬停要求 |
| PRE_TOUCH | 选择该状态后需真实表面接触 | 只对原Action静止键允许，不新增键运动；表面接触不能证明无载荷或有足够按压力 |
| PRESS | 必须 | 从NOTE_ON起跟随原移动键面；ON时键无需已全下压 |
| HOLD | 必须 | 保持实际指腹/可触区域相交。掌腕可协调移动，必须补偿持键手指 |
| RELEASE | 可分离；仍相触时须兼容回弹 | NOTE_OFF解除持续按住义务，但不能阻挡复位或穿入其他键 |

所有活动接触取并集，同手和弦不是只保留最后一音。一次事件批次按半开区间[start,end)移除结束义务并加入新义务，重复音保留原键未复位警告。过去手指占用高于未来APPROACH选择，不能令同一手指同时自由准备与持住另键。

切向模式是合同参数：STICK固定面级材料见证点，或SLIDE在同一可触区域内受控迁移。数值适配本轮选择STICK。广义SLIDE的预算、见证点更新和接触法向跟踪仍需后续实施。法向约束在当前真实键面坐标中定义，PRESS/HOLD必须更新到原Action表面，不把静止世界点永久用于运动琴键。

原0.25mm目标及非目标实体侵入、非相邻实际指面交叉0、正常Rig参考族均保留。接触验收采用裁剪后指腹三角面跨过真实键面且存在非零投影面积；单独“小距离”、顶点到平面相等或QP等式满足都不算实际触键。微小允许侵入是既有几何合同，不是软组织压缩或力学模型。

提前轻触E5在本合同中可以合法，不自动表示提前发声。上一轮2.825秒E5指腹签名间隙约−0.01954mm，仅凭这一接触时刻不能判定早触发；但当时全局非目标/非指腹侵入约5.596mm，仍然明确不合格。本轮不改历史记录，仅修正其可作出的物理推论。

关键边界：半开区间不是瞬移许可。若要求G4一直接触到OFF左极限、E5从同一时刻ON右极限接触，连续位置可能要求边界瞬间兼容两接触集合；这不同于强制整个换位期间同时按住两键。必须另验一侧极限、共同边界姿态与速度。P3本轮仅验证新接触模式，未证明这种接缝可行。

CONTACT_STATE_SCHEMA.json给出求解器无关结构；contact_state_planner.py以note_id、hand、finger、key、tick/秒、原Action为输入。CONTACT_STATE_SEQUENCE.json包含真实R07/R08合同及全部23音解析，独立线性Action重建与Blender求值最大差5.82e−7rad。CONTRACT_REUSE_TESTS.json是六类已有事件解析测试。无物理按压力、击弦或声学起音证明。
''')
md('PREVIOUS_PLANNER_FAILURE_ANALYSIS.md','''
# 上一轮约束结构复核

只读复核 solve_motion.py、motion_model.py、ONE_BRIDGE_SOLVE.json、ACTUAL_ACTION_VALIDATION.json及其诊断文件，没有重跑280秒优化。

| 问题 | 直接证据与判断 |
|---|---|
| 只约束端点？ | 否。29配点的cell()在换音前明确加入G4指腹间隙/区域约束；不是遗漏所有中间持键约束 |
| 是否联合准备？ | 是。44变量共同拟合根控制、拇指和λ/α，并在同一配点约束持键/碰撞。但不等于已找到可行联合状态 |
| 为什么G4失联？ | 初始直达端点的曲线已违反持键。最大违反22.3128→22.3111mm基本停滞，预算结束保留失败候选；真实2.536188秒即观察到失联。没有“约束收敛而仍宣称持键”的证据 |
| 掌腕是否获得补偿？ | 变量允许拇指补偿，实际优化没有找到足以保持接触的补偿；不是完全锁死拇指 |
| 法/切向与接触状态 | 旧方法使用最小签名间隙、pad区域和高度，缺少显式材料接触锚点、滑移/释放模式及活动面更新。间隙和指腹裁剪有分段变化，不能视为光滑完整表面约束 |
| 是否软惩罚丢接触？ | 本轮复核的上一轮已经用显式不等式，目标主要是速度/加速度平滑。不能误写成“只有软接触惩罚” |
| 活动接触是否随事件切换？ | 有硬编码G4→双接触→E5分支；缺通用事件批次/接触对象集合与键机械状态合同。原精确边界双接触有可能由连续性要求导出，但不能仅从MIDI就认定全换位必须双持键 |
| 碰撞代理限制 | 固定近面池和分离轴、材料顶点/少量LP见证点可能保守或漏检新活动面；代理并不等价于全三角面验收 |

已知结构性不足：从不可行端点插值种子直接求整条曲线，没有先验证当前持键可行域中的准备增量，也没有独立验证换音接触模式的边界兼容。数值停滞是实测；其究竟由导数质量、活动集合、参数化还是局部不可行组合主导，上一轮没有充分消融，不能宣称唯一根因已确定。原MIDI也没有证据必须改动。

本轮新增可核实诊断：同一冻结FK下，两种算法均满足顶点保持等式，但Blender指腹悬空约0.072mm；把接触表示一次性换为实际裁剪三角面的重心坐标材料见证点后，两方法P2均真实触键。直接支持“见证点必须代表接触面”的接口结论。它解释本轮顶点代理失败，不追认为已证明上一轮全部动态失败的唯一原因。

Mink初次适配的3mm等式与0.5mm步长限制矛盾已定位并一次修正；原结果保留。P3旧顶点代理下SLSQP虽收敛，实际非目标侵入3.240mm；Mink则QP无解。最终面级预定位使P3种子本身可行，两工具均通过，不应把这一结果夸大成算法从困难初值全局收敛。

面级锚点仍不是完整碰撞/动力学解法。滑移接触需重选活动面，连续的持键→按键接缝尚未解决。没有重优化原A，没有更改指法或关节活动域。
''')
commits={n:load('sources/'+n+'_commit.txt')['sha'] for n in ['mink','pink','drake']}
md('OPEN_SOURCE_IK_COMPARISON.md',f'''
# 开源IK源码与实际对照

调查日期2026-10-13。最多三个项目，只有Mink安装和实际运行。下载文件、URL及SHA256见 SOURCE_RESEARCH_INDEX.json；源码观察提交：Mink {commits['mink']}，Pink {commits['pink']}，Drake {commits['drake']}。默认分支源码和已发布版本分别记录，不用README中的旧引用版本替代包版本。

| 项目 | 版本/运行条件 | 可复用接口 | 本轮层级 |
|---|---|---|---|
| Mink | PyPI及当前项目1.3.0；本机Windows CPython3.12轮子安装成功；MuJoCo3.15.0 | solve_ik/build_ik、Task.compute_error/compute_jacobian、constraints等式、Limit不等式；内建configuration/velocity/collision limits | 五层均实际完成 |
| Pink | PyPI4.4.0；依赖Pinocchio及QP。官方CI为Ubuntu/macOS，项目Pixi平台不含Windows；此次Pin4.1.0 PyPI无Windows轮子 | solve_ik(constraints=...)显式等式、关节/速度限制、SelfCollisionBarrier | SOURCE_REVIEWED；其余未执行 |
| Drake | 最新正式release v1.57.0；官方安装支持表为Ubuntu/macOS，无原生Windows发行路线 | MultibodyPlant InverseKinematics位置、姿态、距离上下界及关节限制 | SOURCE_REVIEWED；其余未执行 |

依据：[Mink依赖/Windows构建](https://github.com/kevinzakka/mink/blob/main/pyproject.toml)、[Mink等式接口](https://github.com/kevinzakka/mink/blob/main/src/mink/solve_ik.py)、[Pink依赖](https://github.com/pink-kinematics/pink/blob/main/pyproject.toml)、[Pink CI](https://github.com/pink-kinematics/pink/blob/main/.github/workflows/ci.yml)、[Pink显式约束](https://github.com/pink-kinematics/pink/blob/main/pink/solve_ik.py)、[Drake安装](https://drake.mit.edu/installation.html)、[Drake IK接口](https://drake.mit.edu/doxygen_cxx/classdrake_1_1multibody_1_1_inverse_kinematics.html)。Pink缺原生轮子不等于原则上不能在Windows编译，只是本轮不迁移Conda/WSL或构建复杂C++栈。

Mink和Pink均可将任务放入硬等式；普通FrameTask成本项本身仍是软目标，名称包含contact不会自动成为接触约束。Mink内建碰撞依赖MuJoCo geom距离；Pink的SelfCollisionBarrier依赖Pinocchio/HPP-FCL的光滑凸碰撞几何，源码说明非光滑几何行为未定义。两者不会自动理解Blender多骨权重皮肤的凹面、指腹材料区域或琴键Action时钟。[Mink碰撞实现](https://github.com/kevinzakka/mink/blob/main/src/mink/limits/collision_avoidance_limit.py)、[Pink碰撞实现](https://github.com/pink-kinematics/pink/blob/main/pink/barriers/self_collision_barrier.py)。Drake能表达距离约束，但仍需骨架/碰撞映射及动态蒙皮反馈，转换成本在本轮范围外。

许可：Mink/Pink为Apache-2.0，允许商业使用及分发，须遵守许可证副本、归属/NOTICE及修改声明等条件；专利授权和商标权边界见原许可。[Mink许可](https://github.com/kevinzakka/mink/blob/main/LICENSE)、[Pink许可](https://github.com/pink-kinematics/pink/blob/main/LICENSE)。Drake主体BSD-3-Clause，商业使用可行，保留版权/免责声明且不得未经许可用作者名背书，第三方组件另有许可。[Drake许可](https://github.com/RobotLocomotion/drake/blob/master/LICENSE.TXT)。本次DAQP为MIT，但qpsolvers为LGPL-3.0，商业分发仍需满足相应库修改/源码、通知及替换或重链接条件，不能把整个依赖栈统一说成Apache。[qpsolvers许可](https://github.com/qpsolvers/qpsolvers/blob/main/LICENSE)。所有安装包许可随deps保存，未采用商业QP后端。

实际Mink适配：12维真实Rig控制（掌根6、拇指4、λ、α）经原FK和加权皮肤求材料点/碰撞残差，公开Task/Limit子类提供误差和有限差分雅可比，调用未修改的mink.solve_ik(..., solver='daqp', constraints=[...], limits=[...])。MuJoCo中12个标量关节仅承载配置向量及积分，**不是重建的解剖骨架**；没有使用其小球几何做验收。真实外部求解输出映射回同一冻结Blender Rig，独立完整皮肤检查通过。因此属于REAL_RIG_ADAPTER_EXECUTED和CONTACT_CONSTRAINT_TESTED，但不是“MuJoCo原生骨架FK/原生碰撞已适配”。这一区别限制了可宣称的性能收益。

| 层级 | Mink证据 | Pink / Drake |
|---|---|---|
| SOURCE_REVIEWED | sources与源码索引 | 是 |
| TOOL_INSTALLED | INSTALL_REPORT.json，隔离deps | 否 |
| TOOL_SMOKE_TESTED | MINK_SMOKE_TEST.json，真实FK任务构造QP | 否 |
| REAL_RIG_ADAPTER_EXECUTED | 四阶段控制映射；P2/P3外部求解输出 | 否 |
| CONTACT_CONSTRAINT_TESTED | ACTUAL_DISCRETE_VALIDATION.json，面级P2/P3触键及几何通过 | 否 |

本轮不宣称Mink整体胜出。P2实测0.516秒对SLSQP1.031秒，但没有重复统计；P3种子已可行，约0.094对0.078秒，基本不构成求解挑战。共同的顶点代理曾使两者同样悬空，说明接触表示比换一个QP后端更关键。完整运行变量、约束数量、退出原因和失败版本见 MINIMAL_FEASIBILITY_RESULTS.json。
''')
md('PRODUCT_ROUTE_REVIEW.md',f'''
# 产品路线复盘

本轮找到了可复用的**接触状态合同与离散求解适配原型**，尚未找到已证明可适用于不同MIDI的完整运动生成器。六类合同测试全部来自现有同一MIDI，不应称为多个曲目的运动成功率验证。

contact_state_planner.py不按G4/E5分支编译事件，而以音符ID、键ID、手/指、原tick和机械轨迹构造APPROACH/PRESS/HOLD/RELEASE集合，PRE_TOUCH作为有条件选择，FREE是无活动义务时的状态。单指重复音R06→R07、不同指R09→R10、左手L00/L01/L02和弦、白E5释放与黑F#5触键R11→R12、八度R13→R14、R07持键/R08准备均完成真实数据解析测试。重复音未全复位被保留为机械警告，没有为消除警告修改Action。

可推广部分：事件批次、半开义务区间、接触并集、机械面跟踪、可选预触、接触面材料见证点、数值后端可替换、Blender独立验收。面级锚点不依赖G4/E5名称；对接触区域的选择来自冻结网格与键面几何。

仍为本例参数：自然λ/α参考族、旧S2主动屈曲锚点、3mm局部掌腕准备测试、P2展示2.72秒、特定两指的STICK选择、从已知E5姿态作面级法向预定位。没有声称这些可直接覆盖黑键、和弦或八度的几何求解。一般滑移、动态活动面更新、更多指法下的主动姿态参考族仍未验证；不能将所有侧向运动禁掉来获得自然度。

关键进展：P2两个方法均保持G4真实接触并实现约3mm掌腕移动，中指到统一E5参考点的距离由39.650mm降至约35.96mm。该距离是本轮固定参考点的欧氏距离，不是上一轮约19.97mm旧准备区域距离，不能混比。P2非目标/非指腹侵入约0.030mm，低于原0.25mm合同，但不是严格零侵入。

性能：最终四个离散求解内计时1.719秒；含全部失败/修正共{total:.3f}秒、10次记录调用。三个计算脚本成功启动墙钟合计约17.26秒，包含导入和活动集合构建；此前UTF-8初始化失败没有启动求解。未重跑上一轮280秒轨迹。P2：12变量、4等式、66几何不等式加24边界；P3：12变量、3等式、295几何不等式加24边界。Mink另有24局部步长界。约束计数为构造的标量数，不是独立秩或全部网格对；完整几何只在Blender验收。

不能用离散测试秒级成本外推整首MIDI：同一持键材料点可保持一小步，并不说明所有准备距离都可完成；P3还借用了可行端点，实际边界接缝没有被解出。Mink的本例较快P2也不足以抵消依赖和适配成本并据此替换SLSQP。

路线建议A：保留现有FK/蒙皮与SLSQP，增加接触状态规划层；保留Mink适配器作为同输入回归对照。下一轮唯一关键缺口是**换音两侧接触集合的连续边界兼容**：保持G4直到OFF左极限、在同一ON右极限接触E5，是否存在自然且无穿模的共同边界/局部可行连接。用半开标签排除旧义务不能替代这一验证。先研究该接口，不生成整段Action，不重新修补S1。

STOP — HUMAN REVIEW。
''')
table='\n'.join('| '+r['phase']+' / '+r['method']+' | '+f"{r['target_depth_mm']:.6f}"+' | '+f"{r['non_target_or_nonpulp_depth_mm']:.6f}"+' | '+f"{r['middle_ring_gap_mm']:.6f}"+' | 是 |' for r in rows)
md('FINAL_RECOMMENDATION.md',f'''
# 最终结论

**路线A：保留现有FK/蒙皮与SLSQP，增加接触状态约束规划层。** 本轮Mink真实适配完成，但没有足够优势证据选择路线B；保留其为同输入对照后端。

- CONTACT_STATE_CONTRACT_PASS：正式MIDI与原Blender键Action复核通过，三套时间语义分开，90个事件阶段及六类复用解析通过。
- DISCRETE_STATE_FEASIBILITY_PASS：B2/P1、新端点/P4只读复现；最终P2/P3在SLSQP与Mink下均通过真实皮肤接触、原侵入门禁、指面交叉和关节参考族检查。
- EXTERNAL_IK_COMPARISON_EXECUTED：Mink1.3.0经真实冻结FK/蒙皮自定义接口求解，并在Blender独立验收。没有宣称原生MuJoCo骨架和碰撞模型完成迁移。
- **DISCRETE_STATE_FEASIBILITY_ONLY**：连续边界兼容、整条无碰撞路径、物理按压力和Human整体自然度仍未通过。本轮没有运动PASS结论。

| 阶段/方法 | 目标侵入mm | 非目标/非指腹侵入mm | 中/无名间隙mm | 真实接触 |
|---|---|---|---|---|
{table}

全部最终样本指面交叉0、解剖参考族/授权控制域违规0。P2掌腕移动约3mm，中指更接近下一音，但仍未达到E5最终位置。P3为2.921426秒原E5未下压状态下的接触模式；P4为ON后35ms，二者独立通过，不混为同一时刻。

结构性证据：上一轮存在中间持键硬约束，失败源于没有找到可行曲线，不能简单说“只管端点”。本轮两工具曾同时出现代理满足而真实指腹悬空0.072mm；一次面级见证点改造后同时通过，支持优先修正接触接口而非仅更换求解器。旧失败数据完整保留。

求解内计时合计{total:.3f}秒，计入全部10次初始、接口修正和面级对照调用；含载入/构建的三次计算命令约17.26秒，低于600秒预算。没有增加权重、扩大解剖范围或重跑旧280秒优化。P3最终种子已可行，因此不把其收敛当成困难运动求解能力证明。

对核心问题的回答：**已经建立可复用于不同MIDI事件结构的合同与离散接触求解接口；尚未证明不同MIDI的真实连续运动可行。** 六类复用测试用的是原曲既有数据，不是新曲库，也不是跨曲目成功率统计。

后续唯一关键验证：换音两侧接触集合的连续边界兼容。旧音OFF后不再必须被按住，但连续位置可能仍要求边界瞬间兼容旧接触左极限和新接触右极限。若这一小范围问题在原时序、自然关节和几何合同下冲突，应保存冲突证据停止，不能通过瞬移、提前释放、改指法或扩大求解时间绕过。

本轮无新Action、视频或渲染序列。源身份与保护哈希核验见 PROTECTED_FILES_AFTER.json。所有新结果为DESIGN_PROVISIONAL，原E5端点Human视觉仍待审。

**STOP — HUMAN REVIEW。** 不自动进入G4→E5正式连续Action、B02或23音双手动画。
''')
# Explicitly supersede inherited obsolete policy fields; geometry and source identity remain.
p=load('POLICY_LOCK.json');keep=['task','authority','contact','collision','source_input','source_action_scene','root_domains','human_decision'];clean={k:p[k] for k in keep if k in p};clean.update(static_only=True,continuous_action_authorized=False,total_new_numerical_budget_seconds=600,actual_execution_counts=dict(initial=4,step_correction=2,face_witness_correction=4),no_more_solves=True,root_control='Existing6DOF domain reused; not frozen Z. See root_domains.',reference_family='Unchanged B2/endpoint λ plus active middle α; not clinical ROM',external_adapter_scope=result['adapter_scope'],stop='STOP — HUMAN REVIEW');js('POLICY_LOCK.json',clean)
print('REPORTS_COMPLETE',total,stages)
