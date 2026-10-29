import sys,json,hashlib,ast
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent
r=lambda n:json.loads((O/n).read_text(encoding='utf-8-sig'))
def md(n,s):(O/n).write_text(s.strip()+'\n',encoding='utf8')
def save(n,x):(O/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
M=r('SOURCE_COMMITS.json');L=r('LOCAL_BOUNDARY_TRAJECTORY_RESULTS.json');V=r('ACTUAL_BLENDER_VALIDATION.json');B=r('TRAJECTORY_BENCHMARK_INPUT.json');budget=r('RUN_BUDGET.json');model=r('SYMBOLIC_MODEL_VALIDATION.json');solve=r('CASADI_LOCAL_SOLVE.json');j=B['common_junction_actual'];p4=B['references']['P4'];distance=sum(((a-b)*1000)**2 for a,b in zip(j['wrist_world_m'],p4['wrist_world_m']))**.5
om=M['ompl']['commit'];tr=M['trajopt']['commit'];te=M['tesseract_planning']['commit'];cs=M['casadi_executed_tag']['object']['sha']
md('TRAJECTORY_PLANNER_SOURCE_REVIEW.md',f'''# 成熟开源连续规划源码对照

OPEN_SOURCE_TRAJECTORY_PLANNER_REVIEWED。本轮仅选择CasADi实际适配；OMPL、TrajOpt/Tesseract是只读源码调查，未安装或声称运行PASS。源码读取于2026-10-13，逐文件URL、SHA256、获取失败记录在SOURCE_FILES.json；仓库commit及发行包平台元数据另存。未调用第三方云端规划，未上传Rig、MIDI或轨迹。

|候选|本次核实版本|接触/路径/时间能力|实际适配判断|
|---|---|---|---|
|OMPL|{om}|Constraint零集、Projected/Atlas/TangentBundle状态空间、RRTConnect几何搜索、有效性回调；固定音乐时间需另建时间/动力学层|未安装。当前PyPI2.0.1发行文件没有Windows wheel；源码存在Windows构建分支，不能据此称Windows不支持。当前环境需另核实构建/绑定成本|
|TrajOpt|{tr}|联合多步顺序凸优化；关节速度、加速度、jerk项；离散/连续碰撞约束/代价|未安装。已有Windows CI/构建宏，但依赖Tesseract、Eigen、Boost、trajopt_sco、JsonCpp等，非本轮轻量直接替换|
|Tesseract Planning（同候选生态）|{te}|场景/运动规划组织与TrajOpt适配器|需要将本项目外部FK、运动键与非刚性蒙皮碰撞接入其场景和运动学接口；不能直接套刚体link碰撞结果替代皮肤验收|
|CasADi|执行固定3.7.2，commit {cs}|多时刻NLP/最优控制建模、AD、IPOPT后端；接触阶段及轨迹约束由应用表达|Windows CPython3.12 wheel约51MB，隔离安装成功；实际完成144变量、6618约束联合时间问题的一次有输出IPOPT调用，超时未收敛|

CasADi仓库查询HEAD为{M['casadi']['commit']}，PyPI查询当前版本为3.8.1；本轮没有混用HEAD与执行版本，固定3.7.2以对应已读取示例和源码。CasADi不是完整钢琴手规划器，项目必须提供模型、模式、避障与转录。未借外部库单点IK冒充轨迹规划。

## 核实的具体实现

OMPL [ProjectedStateSpace.cpp](https://github.com/ompl/ompl/blob/{om}/src/ompl/base/spaces/constraint/src/ProjectedStateSpace.cpp) 的discreteGeodesic先作局部插值再调用constraint_->project，并通过StateValidityChecker检查；投影失败、步长及曲率问题仍可能失败。[官方约束规划说明](https://ompl.kavrakilab.org/constrainedPlanning.html)说明三种流形表示与可微约束前提。Atlas/TangentBundle头文件及RRTConnect/SpaceInformation接口已保存；碰撞和接触模型仍由应用提供。几何路径不自动等于按MIDI时间可执行的轨迹。

TrajOpt [problem_description.cpp](https://github.com/tesseract-robotics/trajopt/blob/{tr}/trajopt/src/problem_description.cpp)注册joint_vel、joint_acc、joint_jerk及cart_vel；[collision_terms.hpp](https://github.com/tesseract-robotics/trajopt/blob/{tr}/trajopt/include/trajopt/collision_terms.hpp)区分时间步端点自由/固定，使用Tesseract ContinuousContactManager；kinematic_terms.cpp依赖操纵器FK/Jacobian。连续碰撞功能针对其接入的几何表示，不是对Blender蒙皮三角面自动成立的保证。Tesseract [TrajOpt适配源码](https://github.com/tesseract-robotics/tesseract_planning/blob/{te}/motion_planners/trajopt/src/trajopt_motion_planner.cpp)已读取。Windows README步骤仍有TBD；本轮没有尝试复杂编译或机器人模型迁移。

CasADi [direct_collocation.py](https://github.com/casadi/casadi/blob/{cs}/docs/examples/python/direct_collocation.py)联合优化多节点及连续性等式，调用nlpsol(...,'ipopt',...)；[direct_multiple_shooting.py](https://github.com/casadi/casadi/blob/{cs}/docs/examples/python/direct_multiple_shooting.py)展示分段积分与状态匹配；[Callback接口](https://github.com/casadi/casadi/blob/{cs}/casadi/core/callback.hpp)允许外部函数，导数仍须实现或有限差分。本轮采用符号FK/蒙皮及直接多项式配点，未照搬示例玩具系统，也未采用多重打靶积分。源码支持能力与本次实际实现分别记录。

## 许可及离线执行

OMPL所读核心[BSD-3-Clause许可证](https://github.com/ompl/ompl/blob/{om}/LICENSE)允许商业使用/再分发，须保留版权、条件、免责声明及不得背书条款；依赖另计。

TrajOpt本次所读trajopt与trajopt_sco [BSD-2-Clause许可证](https://github.com/tesseract-robotics/trajopt/blob/{tr}/trajopt/LICENSE)要求源/二进制分发保留通知。Tesseract [顶层许可声明](https://github.com/tesseract-robotics/tesseract_planning/blob/{te}/LICENSE)说明逐文件Apache-2.0、BSD-2-Clause、BSD-3-Clause混合许可，分发时应按组件保留相应NOTICE/许可等；不是整个生态统一一个许可证。

CasADi [LICENSE.txt](https://github.com/casadi/casadi/blob/{cs}/LICENSE.txt)为LGPLv3，代码头允许v3或后续版本。商业应用可使用；分发库修改/组合制品应履行对应源码、通知及库替换/重新链接等条件，不能仅理解成“免费所以任意静态封装”。实际IPOPT日志标识EPL，MUMPS及其他打包依赖许可需随分发逐项保留；本轮仅本地研究，未制作商业分发物。未使用付费Gurobi/Pro功能。

三个候选均可设计为完全本地执行。本轮运行只使用本地CasADi/IPOPT；网络仅用于源码、元数据及wheel下载。未调查/使用Ruckig或TOPPRA，不引入社区路点云API。
''')
md('PLANNER_ADAPTER_EXECUTION.md',f'''# 真实适配与执行边界

REAL_TRAJECTORY_PLANNER_ADAPTER_EXECUTED：是，含一个有完整输出的真实多时刻优化问题；不代表求解成功。实际环境Windows、CPython3.12、隔离CasADi3.7.2、IPOPT3.14.11/MUMPS5.4.1；Blender5.1.2独立重放。没有重建Rig、改权重、迁移MuJoCo或安装ROS。

## 输入身份与模型映射

TRAJECTORY_BENCHMARK_INPUT.json冻结P1/B2、P2、共同构型、P3、P4的原始JSON数据与时间。旧25ms失败轨迹和24样本保留路径及SHA256，未作为安全路径初始化。EXPERIMENT_INPUT.json逐项保留原指腹三角面、顶点索引与重心权重；键几何仍为原88键。INPUT_SCENE_VERIFICATION.json实际核对原Action负载和Rig native身份。

12维latent映射26控制：掌根毫米平移、工程Euler度数、拇指4控制、批准长指参考族λ与中指屈曲插值α。手指屈曲/spread使用既有骨骼局部轴和rest矩阵；世界变换BASE、rig_world与原FK同源。未把这些工程角度当成临床角度。

symbolic_skin.py将原rest变换、归一化权重、冻结shape key及FK表达为CasADi图；不是另造手部几何。6个历史实际姿态的符号蒙皮与原数值模型误差约1e-12mm；与完整Blender顶点最大差{model['actual_max_error_mm']:.9f}mm。0.001mm诊断阈值在一姿态略超（1.032微米），记录为未全部满足该诊断阈值，不宣称精确同一浮点结果。独立Blender门禁从未放宽，最终真实验收优先。

## 实际调用与自研部分

外部API：MX/DM、Function、jtimes、Function.expand、nlpsol('contact_trajectory','ipopt',problem,options)、solver(...bounds...)及stats()。CasADi生成约束导数，IPOPT联合优化144个变量、48等式、6570不等式。不是逐点IK调用后事后插值。

项目自研：冻结手模型符号映射、两段五次Bernstein轨迹转录、ContactMode到活动指腹的映射、原Action采样、局部避障证书、参数边界、速度/加速度设置及完整Blender验收。这里“CasADi轨迹方案”指借该开源框架实施的直接配点优化，不宣称获得现成钢琴运动规划器。

两段系数同时优化，在J建立位置、速度、加速度C2等式，原时间固定。13个时间点施加接触和几何约束，控制系数凸包约束保证该多项式的参数域/速度/加速度上界（只有NLP约束实际满足时成立）。世界腕部速度/加速度与映射关节速度在配点处约束，jerk仅进目标；这些有限配点不是全时域几何证明。起点固定共同构型种子；终点在同时间满足新接触但不强制旧末端姿态。

接触使用原材料见证点对移动键面的法向误差±0.0005mm（目标-0.005mm）、原可触区域和pad辅助条件；真实指腹是否跨面仍由Blender判定。目标/非目标内部三角侵入内部采用0.20mm余量，真实门禁0.25mm。

键体避障证书：在139个局部活动三角—键片对上，取键体平面非负凸组合，约束三角三个顶点的加权内侧距离≤0.20mm；18个小型LP选择该证书。对于已覆盖三角/键片，这给出保守内部深度上界；候选过滤和固定活动图不是全网格证明。近指面采用39个活动分离轴；其余面必须独立全量验收。固定活动图可能保守，未开展消融确定其影响。

## 成本和终止

第一次表达尝试保守计{budget['previous_attempt_charged_seconds']:.3f}秒后中断，无保留求解结果。初期曾因重定向stdout缓冲误判为“未迭代”；现已将其内部迭代状态标为未知，不能利用未刷出的日志证明零迭代。

唯一局部表达修正将函数展开为SX；同一个轨迹问题完成构造{solve['solver_construction_seconds']:.3f}秒、IPOPT执行{solve['solver_wall_seconds']:.3f}秒，共31次可核实迭代，返回Maximum_WallTime_Exceeded。约束残差仍{solve['constraint_violation_scaled']:.9f}（混合缩放约束，不能统一解释成毫米）。日志显示约束Jacobian34次耗时{solve['stats']['t_wall_nlp_jac_g']:.3f}秒，约占IPOPT墙钟93%。这是当前适配的直接性能证据；不是所有CasADi问题的性能结论。

完成运行期间观测工作集约5.78GB。曾计划停止第二次构造，但执行停止命令时进程已经正常超时退出并保存结果；失败Stop-Process记录已纠正，不计一次额外中断或第三次求解。

数值预算保守{budget['total_conservative_seconds']:.3f}秒，含第一次中断、图构造、证书LP及额外10秒前置建模计费余量；低于600秒。库安装/源码读取/Blender验收分开统计，不计入数值搜索；前两者精确墙钟未单独instrument，未伪造耗时。

最后迭代被作为失败候选独立重放：没有因收敛失败就隐去真实几何结果，也没有将尚未满足C2等式的两段曲线授予连续性PASS。
''')
md('STAGED_CONTACT_TIME_REVIEW.md',f'''# 原音乐时间下的阶段划分

|阶段|展示时间|持续时间|合同与可允许运动|
|---|---|---:|---|
|自然持键准备|2.527855–2.720000|192.145ms|拇指持续真实G4接触；中指自由准备，掌腕可在接触/避障/手型域内移动；P2只是参考|
|持键后续准备|2.720000–2.921426|201.426ms|同上；不可偷放G4；E5可以几何轻触静止键面但不得改变原键Action，力未建模|
|接触切换|2.921426|原事件|G4 HOLD左极限与E5 PRESS右极限共构型；不是两键同时深按|
|E5初始下压|2.921426–2.956426|35ms|中指接触真实运动E5键面，拇指解除HOLD但不得阻碍G4原Action回弹|

B2至边界可用393.571ms，整个研究窗口428.571ms。25ms是局部模式切换试验，不能解释成整手全部换位只允许25ms。R06→R07入口未研究。

原共同构型与P4腕部直线距离约{distance:.6f}mm；这是两个独立候选的差，不是35ms内最低必需位移。本轮较长窗口未运行，因此没有证明P4在35ms内可达，也没有证明提前持键准备足以完成该换位。后续可重新选择中间/边界/终点姿态，不将P2或当前共同构型锁为全局最优。

本轮局部模型在固定时域直接优化，没有额外时间拉伸。实验速度/加速度限值在TRAJECTORY_BENCHMARK_INPUT.json中公开：世界腕速500mm/s、加速度50000mm/s²，根/拇指与λ/α另有相应单位限制。它们用于限制上一轮剧烈运动并比较算法，不是临床/演奏舒适标准，失败不构成医学不可行证明。

接触轨迹未找到，故最短时间、固定MIDI时间可行性均未确定；不得报告PATH_FOUND_TIMING_BLOCKED。当前没有“路径成立，仅时序不成立”的证据。
''')
md('PRODUCT_ROUTE_REVIEW.md',f'''# 产品路线复盘

**选择B。接触合同、冻结FK/蒙皮和静态成果保留；成熟外部方法已实际执行，但没有显示充分的接触轨迹优势。**

本轮有实际前进：把接触、几何和相邻时间运动关系写成同一个联合时间问题，接通CasADi符号导数/IPOPT及真实Blender重放。没有从“可行静态姿态集合”前进到“已经验证、真正可复用的接触约束连续运动规划方法”，因为实际输出仍失去E5接触。

公平24时刻对照：旧候选10个失败，新候选12个失败；最大目标侵入0.331715→{V['max_target_mm']:.6f}mm，错误区域0.375185→{V['max_wrong_or_non_target_mm']:.6f}mm。相同采样的腕速峰值3104.531→{V['kinematics']['matched_previous24']['maximum_speed_mm_s']:.3f}mm/s，差分加速度1314580.610→{V['kinematics']['matched_previous24']['maximum_acceleration_mm_s2']:.3f}mm/s²。碰撞及剧烈运动有改善，但不能以此抵消12个E5真实接触失败；没有整体PASS或可重复优势。

具体卡点：接触等式残差未消除、IPOPT在180秒名义求解预算（实际182.112秒）内未收敛，导数评估约170秒占主要成本。源码图/导数组织是已定位的性能环节；完整皮肤输出及跨时刻依赖可能放大计算，是待剖析的原因，不能未经profile称已确定内部根因。固定碰撞证书、局部参考族、初始常值曲线和工程动力学限值是否限制可行性，均未排除。

唯一最小技术缺口：在同一冻结Rig上，使多时刻接触约束的稀疏导数/可行性恢复能以可控成本消除移动键面的接触残差，并通过真实重放。下一轮应先核实小规模稀疏Jacobian及接触可行性恢复接口，不再次修补孤立静态节点，不更换一批外部工具，也不直接扩大到整段MIDI。当前没有足够证据选择OMPL或TrajOpt替换生产主线。

## 通用性与实际边界

输入合同采用ContactMode、ActiveDigits、KeyGeometry(t)、JointDomain、EventTime、Start/Goal；算法按midi/finger、真实键枢轴及可触面读取，不含R07/R08/G4/E5名称分支。时间和状态种子属于benchmark数据，不是为这些音符编写的求解特例。

INTERFACE_REUSE_TESTS.json实际执行同指重复、左手和弦起音/持键及原曲黑键事件规则回归，黑白键几何不假设统一高度。规则接口能表达左右手及多接触集合；当前数值适配实际只接入RIGHT HAND R2、两个阶段及一旧一新两接触。左手符号模型、多音联合轨迹、任意模式序列均未适配；这些请求必须另做适配，不能把规则通过宣称为通用MIDI运动通过。

当前参考族λ/α、局部三角见证图与工程运动限值需要按新状态域核实。IPOPT与CasADi本身可复用；本次适配计算成本保守{budget['total_conservative_seconds']:.3f}秒仍未解决25ms接触问题，不具备已证明的整曲扩展能力。

不授予FINGERING_MOTION_FEEDBACK_REQUIRED的冲突结论：没有证明人体、指法或固定时间互相矛盾。失败反馈保留事件/手/指/键/时刻/约束及非收敛状态，供后续上游代价研究；本轮C01不变。Human尚未认可的共同姿态及所有新候选均DESIGN_PROVISIONAL。
''')
md('FINAL_RECOMMENDATION.md',f'''# 最终技术决定

**B：现有接触合同及FK/蒙皮有效，成熟外部方法已执行，但未显示充分优势。** 结论为CONTACT_PATH_NOT_FOUND_WITHIN_BUDGET。不继续扩大窗口或求解次数。

|门禁|本轮结果|
|---|---|
|OPEN_SOURCE_TRAJECTORY_PLANNER_REVIEWED|通过，3个候选组源码/平台/许可对照|
|REAL_TRAJECTORY_PLANNER_ADAPTER_EXECUTED|通过，CasADi＋IPOPT真实多时刻轨迹问题；非单点IK|
|CONTACT_CONSTRAINED_PATH_FOUND|未通过|
|LOCAL_BOUNDARY_SAMPLED_PASS|未通过|
|FIXED_MIDI_TIME_FEASIBLE|未确定；不能由非收敛宣称时间不可行|
|FULL_SHORT_BRIDGE_SAMPLED_PASS_HUMAN_PENDING|NOT_EXECUTED，局部门禁失败|
|PATH_FOUND_TIMING_BLOCKED|不适用，尚无合格接触路径|
|CONTACT_PATH_NOT_FOUND_WITHIN_BUDGET|成立|
|TOOL_ADAPTATION_BLOCKED / FAIL_CLOSED|最终不适用：适配实际进入优化；源保护正常|

唯一局部候选覆盖2.913092667–2.938092667秒。IPOPT31次可核实迭代后超时，未收敛。31条实际Blender记录包含30个时间采样与1个边界左极限；接触在12条记录失败，首次采样失败2.926634333秒，之前通过点为2.925592667秒（不是声称精确失效发生时刻）。最终E5指腹悬空{V['max_required_true_pulp_gap_mm']:.9f}mm，保留原始布尔，不四舍五入改判。

最大目标侵入{V['max_target_mm']:.9f}mm，非目标/错误区域{V['max_wrong_or_non_target_mm']:.9f}mm；非相邻指面交叉0，关节参考族/轴/域在样本处通过，中指/无名指最小精确间隙{V['minimum_middle_ring_exact_mm']:.6f}mm。这些分项不能替代失败的接触门禁或Human自然度认可。

同样24个旧时刻，新候选12个失败，旧候选10个失败；相同采样腕速峰值从3104.531降至{V['kinematics']['matched_previous24']['maximum_speed_mm_s']:.3f}mm/s，差分加速度从1314580.610降至{V['kinematics']['matched_previous24']['maximum_acceleration_mm_s2']:.3f}mm/s²。120Hz粗网格和含微秒边界探针的原始运动学分别保存，不混用统计。微秒间隔差分受Blender浮点精度和未收敛边界残差影响，巨大的原始加速度不能当作可靠人体运动量；边界实际腕位置差{V['kinematics']['actual_left_right_same_event_wrist_difference_mm']:.9f}mm也保留，未宣称精确C2通过。

**是否已经得到真正可复用的接触约束连续规划方法？尚未。** 已接通联合时间外部优化，但主要卡在接触保持与非收敛；约170秒用于34次约束Jacobian评估。没有证据把失败归因于人体、C01或固定MIDI时长。下一项唯一关键工作是同输入下的稀疏接触导数/可行性恢复接口验证，不是再修静态节点。

数值工作保守总计{budget['total_conservative_seconds']:.3f}秒，低于600秒；包括中断表达尝试及10秒建模计费余量。源码/安装与独立验收另计。重定向日志曾造成阶段误判，已根据完整IPOPT输出纠正；最终证据以CASADI_LOCAL_SOLVE.json和真实Blender记录为准。

B2到E5+35ms的428.571ms窗口未执行，R06→R07入口未验证。无新Action、视频、诊断Blend或静帧；所有控制与失败证据只存隔离目录。保护复核详见PROTECTION_CHECK.json。

**DESIGN_PROVISIONAL — STOP — HUMAN REVIEW。** 不自动进入B02、23音双手或教材生产。
''')
# Source protection and deliverable integrity, no numerical solve.
protected=r('PROTECTED_FILES_BEFORE.json');bad=[]
for f,h in protected.items():
 p=Path(f)
 if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=h:bad.append(f)
save('PROTECTION_CHECK.json',dict(status='PASS' if not bad else 'FAIL_CLOSED',checked_files=len(protected),changed_or_missing=bad,original_assets_saved=False));assert not bad
required=['TRAJECTORY_PLANNER_SOURCE_REVIEW.md','TRAJECTORY_BENCHMARK_INPUT.json','PLANNER_ADAPTER_EXECUTION.md','LOCAL_BOUNDARY_TRAJECTORY_RESULTS.json','STAGED_G4_E5_TRAJECTORY_RESULTS.json','ACTUAL_BLENDER_VALIDATION.json','PRODUCT_ROUTE_REVIEW.md','FINAL_RECOMMENDATION.md'];assert all((O/n).stat().st_size for n in required)
for f in O.glob('*.py'):ast.parse(f.read_text(encoding='utf-8-sig'))
for f in O.glob('*.json'):json.loads(f.read_text(encoding='utf-8-sig'))
save('DELIVERY_CHECK.json',dict(required=required,present=True,python_syntax=True,json_parse=True,protected_files=len(protected),decision='B',no_more_solves=True,source_review_only=['OMPL','TrajOpt/Tesseract'],actual_framework='CasADi3.7.2/IPOPT3.14.11',authority='DESIGN_PROVISIONAL'))
print('REPORTS_COMPLETE',len(required),'protected',len(protected),'P4independentdistance',distance)
