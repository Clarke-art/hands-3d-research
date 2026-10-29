import sys,json,hashlib,re
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;ROOT=P.parents[1];A=ROOT/'audits'
S=A/'piano_hand_static_to_dynamic_transition_r1';R=A/'left_little_finger_moving_key_reachability_r1';D=A/'left_octave_neighbor_key_clearance_conflict_isolation_r1';C=A/'left_octave_root_finger_coordinated_clearance_r1';CORE=A/'midi_driven_dual_hand_piano_performance_poc_r1';STATIC=A/'piano_hand_static_posture_clearance_refinement_r2'
def read(f):return json.loads(f.read_text(encoding='utf-8-sig'))
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def link(f,label,line=None):return f'[{label}](<{f.as_posix()}{":"+str(line) if line else ""}>)'
def source(f,needle,label):
 rows=f.read_text(encoding='utf8').splitlines();ids=[i+1 for i,s in enumerate(rows) if needle in s];assert ids,(f,needle)
 return link(f,label,ids[0])
def save(n,text):(P/n).write_text(text.strip()+'\n',encoding='utf8')
E=read(P/'READ_ONLY_EVIDENCE_SUMMARY.json');protected=read(P/'PROTECTED_EVIDENCE_BEFORE.json')
assert E['solver_code_matches_saved_fit'] and E['policy_matches_saved_fit']
refs={
 'input':source(CORE/'01_source_timeline.py','hand=','E01 · MIDI→手/指/键/共同时钟'),
 'key':source(CORE/'performance_core.py','def keypress','E02 · 原35ms下沉/70ms回弹'),
 'joint':source(CORE/'performance_core.py','def digit_setup','E03 · 21-bone关节适配'),
 'sample':source(S/'common.py','def sample','E04 · 姿态/阶段/三次曲线采样'),
 'surface':source(S/'common.py','def keytransform','E05 · 运动键面逆变换与实测'),
 'oldsolve':source(S/'01_plan.py','def residual','E06 · 固定root全段关节系数拟合'),
 'follow':source(R/'03_probe.py','def motion','E07 · root补偿与拇指混合'),
 'current':source(C/'01_coordinate.py','def motion','E08 · 当前29参数轨迹'),
 'contact':source(C/'01_coordinate.py','def contact_residual','E09 · 运动键可奏区接触目标'),
 'soft':source(C/'01_coordinate.py','def residual','E10 · 接触/净空/运动学加权残差'),
 'solve':source(C/'01_coordinate.py','fit=least_squares','E11 · 只有参数bounds的least_squares'),
 'bake':source(C/'01_coordinate.py','def linear','E12 · 120Hz求值/60fps坐标烘焙'),
 'measure':source(C/'03_measure.py','required=t<','E13 · required contact与natural release分开'),
 'verify':source(C/'02_verify_render.py','expectedbase','E14 · 保存重开绑定身份') if 'expectedbase' in (C/'02_verify_render.py').read_text() else source(C/'02_verify_render.py','Starting native bind','E14 · 保存重开绑定身份'),
 'gate':source(C/'05_finish.py',"status='COORDINATED",'E15 · 后验Fail-closed门禁'),
 'audio':source(CORE/'05_audio.py',"sync={'source'",'E16 · 既有音频适配/几何接触未自动验证')}
reports=[S/'PIANO_HAND_STATIC_TO_DYNAMIC_TRANSITION_R1_REPORT.md',R/'LEFT_LITTLE_FINGER_MOVING_KEY_REACHABILITY_R1_REPORT.md',D/'LEFT_OCTAVE_NEIGHBOR_KEY_CLEARANCE_CONFLICT_ISOLATION_R1_REPORT.md',C/'LEFT_OCTAVE_ROOT_FINGER_COORDINATED_CLEARANCE_R1_REPORT.md']
pol=link(C/'COORDINATED_CLEARANCE_POLICY_R1.json','锁定协调政策');fit=link(C/'ROOT_FINGER_COORDINATION_R1.json','唯一有效求解记录');data=link(P/'READ_ONLY_EVIDENCE_SUMMARY.json','本轮有限只读摘要');counter=link(D/'ROOT_COUNTERFACTUAL_R1.json','已保存root因果对照');anchors=link(C/'STATIC_ANCHOR_PROTECTION_R1.json','四静态姿态身份');clear=link(C/'NEIGHBOR_KEY_CLEARANCE_R1.json','已保存净空');contacts=link(C/'DYNAMIC_CONTACT_R1.json','已保存接触分相位数据');cont=link(C/'MOTION_CONTINUITY_R1.json','工程连续性/边界驻留');repairs=link(C/'IMPLEMENTATION_REPAIR_R1.json','实现修复记录')
common='2026-10-09 · ARCHITECTURE_REASSESSMENT_ONLY · HUMAN_VISIBLE_PRODUCT_QUALITY_FIRST\n\nHuman批准的四静态姿态及冻结资产继续有效；当前动态演奏NOT_APPROVED。本轮新轨迹、新Action、新blend、求解器执行和渲染均为0。\n'
current=f'''# MOTION_ARCHITECTURE_CURRENT_STATE

{common}

当前是**离线、整段、低维参数化的联合运动拟合，然后烘焙为Blender预设Action播放**。它已经共同优化掌腕和五指相关参数，不能称为完全独立逐指IK；但也不是带硬接触/非穿透可行性证明的联合受约束轨迹规划。对应证据：{refs['current']}、{refs['soft']}、{refs['solve']}、{refs['bake']}。

## 实际链路与复用边界

|环节|实际实现|证据|
|---|---|---|
|MIDI→手、指、键|原Musette源MIDI384 PPQ、120 BPM；原时间加0.7s统一展示偏移。左D2=5/D3=1，key_index=midi−21。指法是保存的设计候选，不是从MIDI自动估计人体动作。|{refs['input']}|
|输入裁剪|common.EVENTS固定n01/n02/n04。区间0.400–1.800s；NOTE_ON/OFF为0.700/0.950、0.950/1.200、1.200/1.450s。原两小节其它音符不进入本微实验。|{refs['sample']}、{pol}|
|静态参考|读取批准R2派生L1/L2 qanchor与共同root。准备/回位120ms等使用quintic；压力路径使用三次Bernstein。完整静态场景保留，不在重叠时强制动态全手同时等于整个L2。|{refs['sample']}、{anchors}|
|琴键时间轴|原quintic 35ms下沉、70ms回弹，与NOTE_ON/OFF共时钟；演奏规划不能反过来推迟琴键。|{refs['key']}|
|掌腕与手指|当前一个外部root；3 XYZ幅值+1 world-X pitch幅值；两主动指各4统一系数偏移；拇指8准备混合系数；闲置三指各3屈伸偏移。共29参数，全部在一个residual内优化。|{refs['current']}、{fit}|
|冻结Rig适配|每指3个内部关节旋转：thumb CMC/MCP/IP，其它MCP/PIP/DIP；基部另有spread轴，共20工程角变量。21骨包含其它现有骨段/终端，不表示21×3个自由度都在使用。rest、weights、mesh和corrective保持。|{refs['joint']}、{data}|
|接触目标|固定pad及实际skin pad均逆变换到**当前旋转琴键**可奏面；目标gap0.5mm，动态XY窗口为原批准触点附近±2/±5mm，随该目标键键程展开。|{refs['contact']}、{refs['surface']}|
|净空|原冻结矩形键体SDF；求解覆盖MIDI21–61，全部3300实际evaluated皮肤顶点。邻键2mm、掌部5mm是软规划距离；主动pad附近18mm区域仅对其本键margin设0，仍惩罚内部穿入。E2/F♯2无豁免。|{refs['soft']}、{pol}|
|输出/审核|采样120Hz，按frame=1+(t−0.4)×60插入现有骨骼和root四元数关键帧、线性插值；保存后重开验实际几何，再渲染60fps三视角。Action是输出载体，不是最初凭手工编好的全部动作。|{refs['bake']}、{refs['verify']}|
|音频|既有48kHz音频适配直接消费同一Performance Timeline，NOTE_ON安排声部；旧音频代码明确手部几何接触可失败。最新微动作视频静音，不能据共同时钟宣布手/键/声几何同步通过。|{refs['audio']}|

## 现有约束的真实性质

|要求|求解器内|求解后|架构缺口|
|---|---|---|---|
|root/关节参数域|least_squares(bounds)硬限制参数；关节系数域继承已批准附近工程范围。|逐样点实际关节及语义wrist检查。|范围是工程域，人体生理域UNKNOWN。|
|主动接触、可奏区域|fixed=10、skin=6的软误差；区域越界是投影残差。|abs(gap)≤3mm且严格inside，所有required样点均须通过。|3mm及inside不是优化内硬不等式。|
|非穿透、净空|clearance=4的软SDF残差；与接触放入同一总平方和。|E2/F♯2正穿入及88键>3mm有限筛查，另有正常视图审核。|不能证明软距离被同时满足；2/5mm规划margin不能等同最终门槛。|
|速度/加速度|超界软残差；joint850/90000、root450/45000、angular150/15000继承。|独立连续性检查；当前PASS。|连续性合格不强制几何接触合格。|
|自然手型|idle偏移正则、±4°硬域；非均匀曲度、spread固定。|正常三视角/完整动作、Human决定。|没有生理模型或已验证自然度评分。|
|近限位驻留|当前只measure，未进入hard constraint或驻留残差。|DIP近下界两次约0.250s，保留为风险。|与旧0.05s否决政策不同，不能混称同一验收规则。|
|冻结姿态/资产|复用源场景；不重新设计。|完整文件SHA与四静态core身份。|动态重叠不等于源整个L1/L2场景；要分别保护静态身份和动态任务。|

以上由{refs['soft']}、{refs['solve']}、{refs['measure']}、{cont}、{pol}核实。对人体可行性只能报告工程域及正常画面，没有据此证明生理极限。

## 联合存在，但时间自由度受限

设p2/p3为当前D2/D3键程。实际root为ΔXYZ=a·p2、Δpitch=b·p2；idle q=q_ref+d·p2。三指幅值不同，时间包络相同。p2=0时root无额外偏移，即使D3仍full-down。保存数组核实1.020/1.100s：p2=0、p3=1；0.950s D3起音时p2=1、p3=0。{refs['current']}、{data}。

主动指对原三组Bernstein控制点加同一个4维offset，等价Δq=[1−(1−p)^3]·offset。原三组曲线不能独立重新塑形；同一p基本沿用同一压力/回弹路径。拇指另有p2×[(1−p3)b0+p3 b1]的准备混合，故D3在未下沉起音时也受到前一D2 root/混合的影响。存在真实全手数值耦合，但尚无充分的独立准备、交接、D3持键与释放轨迹空间。

## 允许指标退化的机制

J=Σ接触残差²+Σ净空残差²+Σ超限残差²+Σ姿态正则²。各块按不同单位/权重/非零数量累加，没有可行性层或词典序保护；较低总J可以伴随更大的某一主动指gap。大量零净空项不影响J；实际非零项数和尺度才影响折中，不能仅凭3300顶点数断言谁必然占优。{refs['soft']}、{refs['solve']}。

求解success=True仅表示ftol/xtol收敛；保存动作前只断言参数有限，几何PASS在后验报告判断。后验门禁确实最终FAIL_CLOSED，故问题是生成内核允许折中，**不是系统把失败正式升级为通过**。{refs['solve']}、{refs['gate']}。

## 索引

'''+'\n\n'.join(refs.values())+'\n\n四阶段正式报告：\n\n'+'\n'.join('- '+link(f,f.stem) for f in reports)
save('MOTION_ARCHITECTURE_CURRENT_STATE.md',current)

failure=f'''# CONTACT_CLEARANCE_FAILURE_ANALYSIS

{common}

结论：**已确认当前路径的触键/净空折中，以及优化器允许折中；支持时序参数化过窄与局部可达性紧张。尚未确定现有冻结Rig内是否不存在共同可行轨迹。**

## 四阶段有限比较

|阶段|root/手指可变空间|D2 max skin gap|D3 max skin gap|净空|结论|
|---|---|---:|---:|---|---|
|STATIC_TO_DYNAMIC_TRANSITION_R1|固定批准root；主动指全段Bernstein系数；idle固定。|7.689mm|1.000mm|有限筛查PASS|静态起音正确不能保证按下动态键。|
|MOVING_KEY_REACHABILITY_R1|D2驱动root Z/Y/pitch+拇指准备混合；小指、idle原轨迹保持。|2.969mm|1.983mm|E2/F♯2新增已记录穿入|root改变确实补足原轨迹接近键面，空间却同时影响其它皮肤。|
|CONFLICT_ISOLATION_R1|不求解：同关节/键Action，仅动态root→静态root反事实。|2.969→7.689mm|1.983→6.653mm|原两键穿入→0|受控证据确认当前root-contact-clearance tradeoff。|
|ROOT_FINGER_COORDINATED_CLEARANCE_R1|29参数一起拟合；root/idle仍D2-only包络。|3.541mm|4.129mm|两键有限样点正穿入0、全88键>3mm0|可接受接触被牺牲，最终FAIL_CLOSED。|

前三阶段最大值包含要求贴合70ms回弹的统计；末阶段仅[NOTE_ON,NOTE_OFF)必需接触。不能把自然离键计为失败或直接把全部旧/新统计看成相同定义。本轮按已保存phase摘要确认末阶段失败出现在**KEY_PRESS/HOLD与NOTE_ON/KEY_PRESS**，不是释放规则变化造成的假FAIL。{data}、{contacts}。四报告对应证据见当前状态文档索引。

## CONFIRMED_CAUSE

1. **原路径的共享root具有因果影响。** 隔离阶段关节矩阵差0、键角差0、Action哈希不变；恢复静态root时两键进入清空，而两主动接触恶化。只对该已保存轨迹成立。{counter}。
2. **共同平方和没有同时满足关键约束的机制。** contact与SDF都是residual中的软项，solver只有参数box bounds。success=True仍输出D2/D3 FAIL；后验门禁才能拒绝。{refs['soft']}、{refs['solve']}、{refs['gate']}。
3. **运动键跟踪存在，当前失败不是按静止键面算出来。** keytransform使用原pivot与当前角度；保存重开独立顶平面/键顶点一致性已验证。{refs['surface']}、{refs['verify']}、{link(C/'SAVE_REOPEN_VERIFICATION_R1.json','实际几何校验')}。
4. **最新失败集中于实际演奏阶段。** 两次D2 NOTE_ON skin gap约0.541mm、KEY_PRESS约3.538mm、HOLD约3.541mm；D3 NOTE_ON约4.129mm、KEY_PRESS约4.092mm，但HOLD最大约1.392mm且通过。所有这些阶段skin pad仍inside真实可奏区，因此不是主要XY越界。{contacts}、{data}。
5. **当前轨迹族没有独立D3 root随动。** p2=0时root/idle偏移强制0；0.950s起音同时处于前一D2 full-down，1.020–1.200s D3持键时root恢复静态。主动三组控制点统一偏移也固定了主要曲线形状。{refs['current']}、{data}。

## SUPPORTED_HYPOTHESIS

|假设|支持依据|尚不能证明|
|---|---|---|
|可行性优先级/求解架构是首要瓶颈|软接触+软非穿透可以互相补偿，输出与success分离；已得到净空清空而接触退化的实际结果。|把软项改硬即可找到合格解。|
|时序轨迹空间过窄|D2-only root、idle相同包络、主动控制点统一offset、两次D2共用曲线；D3失败集中在交接。|具体需要几个新增时间控制量，或哪段腕部运动一定能解决。|
|现有边界附近局部可达性紧张|前阶段小指MCP/spread接近工程上限，压力DIP接近0；最终中指三个增量均到−4°偏移边界，root X到−2mm边界。|冻结21骨Rig的全局不足、所有自然路径不可行。|
|目标窗口/准备混合进一步约束交接|D3键程0时XY窗口收缩到原触点，但root在D2包络上；thumb blending同时改变未下沉拇指姿态。|该目标窗口本身错误，或放宽窗口是唯一/正确修复。|
|局部求解/数值可影响结果|一次确定seed与有限参数域；有float32差分与跨场景root单位矩阵的真实实现bug修复记录。|最终修复后失败仍由同一实现bug造成。|

依据{pol}、{fit}、{repairs}。最新有效输出code/policy SHA与保存记录匹配；两次无效实现启动不纳入产品候选结果。本轮不重跑求解、不重开Blender来重新制造反事实。

## NOT_YET_DETERMINED / UNKNOWN

- 在**保持冻结Rig与相同幅度/角度域**但拥有独立阶段共享轨迹时，共同可行集是否非空。
- 当前bounds、目标窗口、姿态参考、root时间基分别贡献了多少失败；没有新的单因素干预，不能分配独立因果比例。
- 有证据的人体生理关节域、演奏者差异、软组织压力和完整上肢生物力学。现有数值域仅为RSSF-relative工程增量；DIP增量0不是人体反关节或绝对伸直。
- 连续时间、全部三角面非穿透是否严格成立；现有有限筛查与正常教学画面不构成穷尽几何证明。
- 最优规划器在未来双手、和弦、指法切换和多曲目的性能及成功率；本3事件实验不提供泛化证据。

## 瓶颈分级与停止解释

|候选原因|判断|
|---|---|
|约束表达不完整|**部分确认**：移动面与清空目标有实现，但接触/非穿透可行域与失败分类没有进入求解器硬约束；驻留仅测量。|
|约束优先级/求解策略|**CONFIRMED结构缺口**：必须同时满足的要求被做成可交易残差。|
|root与手指完全无协调|**否**：29参数确实联合；问题是协调表达受限。|
|缺乏下沉/持键/释放时序控制|**否（存在）/受限（确认）**：有阶段、运动键目标及自然释放区分，但多数轨迹仍绑定键程单一包络。|
|时间自由度不足|**SUPPORTED_HYPOTHESIS**；当前族的限制确定，换族是否可行仍UNKNOWN。|
|冻结Rig本体自由度不足|**NOT_YET_DETERMINED**；无正式Rig修改依据。|

Human最新判断优先：旧正常视角不明显的邻键小幅几何问题不能夸大；最新净空改善也不能抵消D2/D3真实触键失败。工程可行性和Human-visible自然度分别审核。下一步应改变规划问题的结构，局部root/IK补丁路线保持停止。
'''
save('CONTACT_CLEARANCE_FAILURE_ANALYSIS.md',failure)

options=f'''# MOTION_PLANNING_OPTIONS

{common}

评估依据是现有代码的可交易约束与时序限制，而不是方案名称。下列是概念架构判断，未安装新求解器、未做性能benchmark、未执行任一方案。{refs['current']}、{refs['soft']}、{refs['solve']}。

## 三种不同组织方式

**A：接触锚定的路径构造。** 先用真实运动键面上的pad约束构造主动接触流形，再在其可行自由度内选择共享root/关节与idle避让。其核心是减少破坏接触的方向；若每帧分别IK或事后抬闲置指，仍会重犯当前问题。要将接触、非穿透和时间连续性共同投影，而不是先接触后净空的串行补丁。

**B：可行性先行的分层受约束轨迹规划。** 所有root/active/idle时间参数同时进入同一问题；接触、真实可奏区、非穿透、关节/root域和连续性工程边界形成联合可行域。只有先达到这组要求，才在可行域内优化自然姿态、边界余量和运动代价。较低层优化不能增大高层关键违反量。未找到可行点应输出局部未找到/预算耗尽，而不是以较低cost包装PASS。

**C：阶段/静态锚点引导的受约束插值。** 用批准L1/L2与准备/起音/按压/持键/释放/回位组织全段共享曲线；在有限阶段控制点求解连续路径。核心是有限时间结构和参考姿态，不是接触可行性层。仅做线性/quintic插值不能保证运动键接触；仅在关键帧用局部IK，节点间仍可能失败。

## 比较

|维度|A 接触锚定|B 分层联合可行性|C 阶段/锚点引导|
|---|---|---|---|
|21-bone teaching rig|兼容已有FK、pad和外部root；接触流形可能病态。|兼容相同角变量/冻结变形评价，无需新骨。|最直接复用骨骼角和批准姿态。|
|冻结mesh/rig/weights/corrective|可全部保留。|可全部保留。|可全部保留。|
|L1/L2复用|作为接触锚与自然姿态参考；不能每次强制整手静态完全相等。|作为固定资产与有限姿态邻域；重叠时按任务处理。|复用最强，但容易把静态端点当作动态保证。|
|MIDI/88键/音频时钟|可以复用真实面与固定NOTE_ON/OFF。|可以直接把已有事件编为阶段约束，时间不可变。|简单，但必须由事件自动生成阶段，不能逐曲手工排帧。|
|双手/多曲目潜力|需处理接触切换、和弦和null-space选择；尚未验证。|任务接口可扩展多手/多音，同时约束规模与局部失败风险升高；尚未验证。|易扩展事件调度；新跨度/手位可能需要额外锚点，手工例外风险较高。|
|实现复杂度|中高：接触投影、奇异性、自然姿态空间选择。|中高：硬约束与可靠可行性报告，但最直接修复已确认缺口。|低中：阶段样条容易；缺少硬约束时不会解决当前核心矛盾。|
|性能代价|接触降维可有帮助；每帧重复IK不一定更快。|较重；复用缓存、有限样条与约束聚合控制规模，不能承诺实时。|较低；若不断补关键帧/单音IK，代价与手工复杂度会增加。|
|主要失败风险|投影接触后邻键不可行、分支跳变、释放仍粘附。|非凸问题仅局部搜索、约束不光滑、错误宣称全局不可行、算力预算超限。|节点合格但中途失接触、交接不兼容、逐曲修补。|
|单独采用是否够用|未有证据；接触保护不能排除净空冲突。|最符合已确认问题，但可行性仍UNKNOWN。|不足：当前已有阶段与quintic，仍失败。|

## 推荐

推荐**B作为规划内核**，用A的运动键接触任务表达和C的有限自动相位基来限制复杂度。这是一条方案：一个分层联合约束问题，原子地求解全手连续轨迹；不是三个独立候选或三次串行补丁。

理由：当前并非完全没有全手联合能力，也非完全没有阶段控制；直接追加接触IK或更多关键帧只改变拟合空间而不消除“关键指标可以互相牺牲”。B优先修复该已确认结构，再让时间基独立于D2包络。推荐不以更高接触/净空权重为实现。{refs['soft']}、{refs['solve']}、{refs['sample']}。

## 复用与替换

|保留|规划内核重构|本轮不涉及|
|---|---|---|
|原MIDI/5-1映射/Performance Timeline、35/70ms琴键运动|由事件编译接触/自然释放与交接约束|冻结手、钢琴、权重、corrective、helper bone|
|批准L1/L2场景与姿态数据|一条共享低幅时间轨迹，不再强制Δroot=a·p2|PianoVAM非公制2.5D强制精确触键|
|冻结关节适配/registered pad/Blender实际变形评价|接触+非穿透+关节/root边界同层硬约束；自然度低层优化|生产pointer、完整Musette、多曲目制作、Web集成|
|保存重开、相机、播放器、后验Human门禁|明确区分FOUND_LOCAL_FEASIBLE / NOT_FOUND_LOCAL / BUDGET_EXHAUSTED / INVALID_IMPLEMENTATION|修改旧审计求解器或现有候选|

这是**架构级部分重构**：保留可信输入/资产/输出适配，替换软折中内核与D2-only时间基。不是从头重建项目，也不继续局部root/DIP修补。

## 复杂度与未知成本

上一有效拟合33 nfev、723 residual calls、1557.488s约26分钟，属于该机器/Blender实测路径，不是不同架构benchmark。{fit}。未来硬约束可能更贵，不能承诺实时或普遍收敛。最小验证先限制参数、一次seed、固定采样与预算；准确率未达标不得扩到双手/多曲目。详细唯一实验见{link(P/'MINIMAL_NEXT_EXPERIMENT_PLAN.md','下一阶段提案（未执行）')}。
'''
save('MOTION_PLANNING_OPTIONS.md',options)

experiment=f'''# MINIMAL_NEXT_EXPERIMENT_PLAN

{common}

**PROPOSED_ONLY / NOT_EXECUTED / HUMAN_AUTHORIZATION_REQUIRED_FOR_NEXT_STAGE。** 唯一提案：`LEFT_OCTAVE_PHASE_GUIDED_HARD_CONSTRAINT_FEASIBILITY_R1`。先验证在同一冻结Rig、同一幅度/关节域下，改用有限共享时间轨迹与同时硬约束，是否能找到D2→D3→D2合格路径。不是第二轮原root-follow参数修补。

## 唯一待验证假设

现有失败可能主要来自关键约束可交易及D2-only时间基，而非冻结Rig不可用。用一次可行性优先的整段问题验证此假设；找到可行路径只证明这一微片段，未找到不证明Rig全局不可用。{refs['current']}、{refs['solve']}、{counter}。

## 输入和冻结边界

- 仅原n01/n02/n04：D2 .700–.950、D3 .950–1.200、D2 1.200–1.450s；窗口.400–1.800s。
- L1/L2/R1/R2批准场景完全保留；右手既有Action、正式手/钢琴、marker、rest、weights、corrective、原音频接口、MIDI和所有production pointers保持SHA一致。
- 复用当前工程域：root x±2/y[-5,0]/z[-3.5,0]mm、world-X pitch[-2,0]°、不添加yaw/roll运动；关节原hard bounds，主动邻域±12°、idle曲度变化≤4°与既有spread。未来求解前一次锁定，不能根据结果扩域。
- 这里改变的是**时间函数族和约束层**，不是提高运动幅度或扩大人体关节限位。批准RSSF-relative工程角不能冒充已知生理极限。

## 同一个联合问题

决策对象只有一条全段共享root与现有手指关节连续路径。自动从MIDI生成准备、NOTE_ON、35ms下沉、HOLD、NOTE_OFF后70ms自然释放及恢复阶段。root可在既定120ms准备/交接中提前进行低幅协调，也可响应D3阶段；不再被迫只有p2非零才允许运动。两次D2同一任务规则，不单独为每音另建root或逐帧独立IK。

采用有限C2样条/受约束阶段插值，直接复用批准姿态作参考。实现时最多60个自由轨迹标量，固定由事件生成的时间基；这个数是拟议算力预算，不是已证实的充分自由度。若覆盖全部角色需要超过预算，则停止并报告计划实现边界，不偷偷增加控制点或逐曲手动修形。两个active角色与三个idle角色必须都在同一个决策向量中；不冻结其中角色来冒充已测试的全手空间。

root幅度参数与active/idle曲线独立时间系数由同一求解器同时求解。D3起音不硬套整个静态L2（因为前指仍自然释放），而要求当前主动pad正确接触、姿态在批准参考邻域、冻结L2身份不变。首次D2无重叠时尽可能使用批准L1接触端点；如果需要重新设计静态L1/L2才能进入可行域，记录STATIC_ANCHOR_CONFLICT并停止。

**可行性层：** 运动键接触+实际可奏区+非穿透+关节/root/速度加速度域必须同时满足；其中任何一项不得被其它项较好数值抵消。用显式约束与最大违反量检查，而非增加least_squares权重。不存在“接触优先就允许穿键”或“净空优先就允许悬空”。

**可行域内质量层：** 接近批准非均匀自然曲度、减少长期边界依赖、减少掌腕位移/角变化与jerk。可行性违反量不得因低层质量优化上升。高层硬约束与低层自然度都一起解释，不能只将接触置硬后再逐指避让。

## 联合约束与验收

|对象|工程条件|Human-visible条件|
|---|---|---|
|小指两次D2|NOTE_ON≤t<NOTE_OFF fixed/skin gap绝对值≤3mm、horizontal≤2mm且严格在真实可奏区，跟踪当前运动键；分别报告起音/下沉/持键。|两次都有可靠持续触键，无看得见的悬空按键。|
|拇指D3|同上；特别检查.950–1.020s交接，在起音即满足，不以稍后HOLD通过替代。|声/键起音时指腹已合理就位，不延迟补触键。|
|释放|NOTE_OFF后自然释放，键保持原70ms回弹，不强制全程粘附；空间、非穿透与连续性仍生效。|无突发弹指、追键、跳跃或不合理空间关系。|
|E2/F♯2/掌腕|复用既有冻结键体和evaluated几何，以聚合非穿透约束参与同一问题；不开展命中顶点追查、normal-dot或新的hidden forensic。既有>3mm有限筛查不放宽。2/5mm软规划margin不是必须追逐的零残差目标，可保留为可行域内偏好。|正常教学顶视/侧斜/合理近景无不自然干扰。极小不可见残余只据实分级，不制造重大故障叙述。|
|其它邻键|独立保存重开全88键有限筛查与错误pad接触检测。|无新增明显吞键/错键；不通过遮挡改变审核视角。|
|idle三指|批准非均匀曲度/间距参考、原工程域和≤4°变化；不设home-key、不统一抬直。|随整手自然避让，无钩爪、僵直或突然抬指。|
|小指DIP及其它关节|原工程域、不扩大range；记录per-phase近界驻留，并在可行域内偏好更多余量。|若仍长时间靠DIP下界且自然触键合理性未获新证据，不能包装READY；由Human判断。增量0不自动判反关节。|
|共享掌腕|原幅度域；joint850°/s、90000°/s²；root450mm/s、45000mm/s²；angular150°/s、15000°/s²，与当前政策相同。|低幅、自然、连续，无每音重新定位；数值连续不是自然保证。|
|锚点/资产|原四静态core和正式文件SHA一致；真实起音/动态交接按任务分别检查。|已批准八度手型基础仍可识别，first-web和掌面无明显回退。|
|MIDI/键/声|原tempo/velocity/5-1/key_index/NOTE_ON/OFF不变；将声部计划时间与接触就位时间独立核对；不重制音源。|手在原起音时就位，不能靠移动音频/琴键事件取得视觉同步。|

人体生理可行性UNKNOWN：只能使用现有批准姿态、有限工程域和Human质量审核。不得擅自增加DIP正角下限或声明已验证人体极限来解决失败。

## 有界执行提案

1. 下一轮先锁一次政策、输入SHA、单一seed、相位时间基与变量预算；记录算法/约束雅可比及native bind一致性检查。
2. 一个整段受约束问题；求解节点复用原120Hz必需接触/释放与已有准备恢复样点。最多30次主要迭代、1500次前向评价、30分钟墙钟，三者任一达到即停止。这是下一轮拟议预算，性能UNKNOWN，本轮没有执行。
3. 可行性需要fixed/skin/键面/邻键/域所有最大违反量独立合格，不能用success=True或总cost代替。只有通过后才允许一次DESIGN_ONLY烘焙。
4. 保存重开后复用240Hz及原边界样点作独立检查，不重新优化。节点之间失接触/明显穿入即FAIL_CLOSED，不追加节点、seed或第二候选。
5. 若工程门禁通过，再提供同相机完整正常速度/慢速D2→D3→D2与上一失败版对照。Human另行裁决；禁止直接正式集成。

预算不足、导数噪声或solver未收敛应分别记BUDGET_EXHAUSTED、INVALID_IMPLEMENTATION或NOT_FOUND_LOCAL_FEASIBLE；它们不是全局不可行证书。若有限工程差分精度无法验证，不能继续长时间求解来掩盖。

## 再次FAIL_CLOSED条件

任一required阶段pad接触/实际可奏区不合格；非穿透与关节/root可行域不能同时满足；明显新增悬空/吞键/钩爪/反关节/跳跃；持续边界依赖仍未证明自然；需改变静态锚点/冻结资产/时间轴/幅度域才能继续；实现身份或保存重开验证失败；超出已锁定预算。除“自然度仅Human待决”可保持未批准审核状态外，任何关键工程失败都不得生成或推广后续版本。

只允许一次有效规划。报告局部冲突涉及哪些任务、最大违反量与相位，不开始逐顶点forensic，不据此修改Rig或声部时间。完成后STOP；完整Musette/双手扩展/多曲目/产品集成仍未授权。

## 下一阶段非冻结代码模块（仅提案）

|未来新模块|职责|复用接口|
|---|---|---|
|motion_tasks.py|原事件→相位/交接/运动键接触任务|Performance Timeline、common.recovery_end、keytransform、批准anchors|
|constrained_trajectory.py|有限全段共享时间基、硬可行域、域内自然度优化和局部失败分类|冻结工程bounds与21骨角变量|
|rig_eval_adapter.py|现有Rig/native bind/registered pads与实际变形的可信前向评价、缓存/导数精度门禁|performance_core.joint_mats及Blender evaluation|
|validate_and_bake.py|最大违反量门禁→一次DESIGN_ONLY烘焙→重开/有限筛查/Human三视角材料|现有保存重开、key Action、相机和播放器流程|

未来放在新的实验审计目录中；不修改本轮或旧审计代码，不改production输入。当前没有创建上述运动模块。
'''
save('MINIMAL_NEXT_EXPERIMENT_PLAN.md',experiment)

q={'Q1':'离线全段低维参数化联合least-squares拟合，然后烘焙预设Blender Action；不是逐帧独立IK，也不是硬接触可行性规划。','Q2':'接触/净空/连续性是可互相补偿的软残差；root/idle时间基限于D2键程，active曲线只有统一offset，交接阶段的有限空间使折中反复出现。','Q3':'已有真正联合变量与共同残差，但没有接触+非穿透+关节域同时硬可行的求解/证书能力。','Q4':'首要为约束及求解架构；时间参数化受限与局部工程可达性紧张有支持。冻结Rig全局自由度不足UNKNOWN。','Q5':'NO_EVIDENCE_REQUIRING_FROZEN_RIG_MODIFICATION','Q6':'架构级部分重构：保留输入/冻结姿态/几何/适配/输出验证，替换软折中规划内核与D2-only时间基。','Q7':'仅一次LEFT D2→D3→D2相位引导联合硬约束可行性实验，保持幅度/关节域与时间轴，检验是否同时满足接触、非穿透与自然曲度；PROPOSED_ONLY。','Q8':'未来新审计内motion_tasks.py、constrained_trajectory.py、rig_eval_adapter.py、validate_and_bake.py；本轮不创建运动代码、不修改旧模块。','Q9':'必需接触/可奏区/非穿透/工程域失败，明显产品回退，持续边界依赖自然性未证，需改冻结资产/锚点/时间/域，实现验证失败或预算耗尽时FAIL_CLOSED。','Q10':'YES，正式手/Grand权威、四静态场景、已有候选、MIDI/音频适配和本轮所引用代码与记录均保持。'}
changed=[f for f,s in protected.items() if not Path(f).is_file() or sha(Path(f))!=s];assert not changed,changed
formal=E['formal_assets'];assert all(v['matches'] for v in formal.values())
status={'phase':'LEFT_OCTAVE_COORDINATED_MOTION_ARCHITECTURE_REASSESSMENT_R1','scope':'ARCHITECTURE_REASSESSMENT_ONLY','date':'2026-10-09','highest_principle':'HUMAN_VISIBLE_PRODUCT_QUALITY_FIRST','final_status':'ARCHITECTURE_REASSESSMENT_COMPLETE / READY_FOR_HUMAN_REVIEW','human_approval':False,'dynamic_performance':'NOT_APPROVED','Q1_Q10':q,'current_architecture':{'joint_optimization_exists':True,'parameters':29,'method':'Bounded whole-sequence soft-residual least_squares → baked quaternion Actions','hard_constraints_in_optimizer':['parameter_box_bounds'],'soft_requirements':['active_contact','playable_region','neighbor_clearance','palm_clearance','velocity_acceleration','posture_priors'],'time_basis_limitations':['D2-driven shared root','D2-driven idle flexion envelopes','uniform offsets across inherited active Bernstein control points'],'feasibility_gate':'Post-solve independent measurement + Human review; not an optimizer-level simultaneous feasibility certificate'},'evidence_classification':{'CONFIRMED_CAUSE':['Root intervention changes contact/neighbor clearance in saved trajectory','Soft objective permits critical requirement tradeoff','Latest D2 KEY_PRESS/HOLD and D3 NOTE_ON/KEY_PRESS contact failures','Motion surface and phase control exist','Restricted D2-only root and tied active coefficient family are implemented'],'SUPPORTED_HYPOTHESIS':['Feasibility-first solver architecture is primary bottleneck','Independent shared phase trajectory may relieve handover conflict','Approved neighborhood has local engineering reachability pressure'],'NOT_YET_DETERMINED':['Nonempty joint feasible set within frozen rig/current amplitude domains','Independent contributions of objective, basis, target window and parameter bounds','Validated physiological ranges','Cross-repertoire/two-hand performance']},'recommended_route':'PARTIAL_ARCHITECTURAL_REFACTOR / FEASIBILITY_FIRST_HIERARCHICAL_JOINT_PLANNING','options_evaluated':['Contact-anchored construction','Hierarchical constrained feasibility','Phase/keyframe-guided coordination'],'single_next_experiment':{'id':'LEFT_OCTAVE_PHASE_GUIDED_HARD_CONSTRAINT_FEASIBILITY_R1','status':'PROPOSED_ONLY_NOT_EXECUTED','scope':'LEFT D2 → D3 → D2','requires_new_human_authorization':True,'no_parameter_range_expansion':True,'no_MIDI_or_key_time_change':True,'hard_joint_requirements':['fixed_and_skin_active_contact','true_playable_region','nonpenetration','joint_root_domains','velocity_acceleration_limits'],'proposed_budgets':{'free_trajectory_scalars_max':60,'major_iterations_max':30,'forward_evaluations_max':1500,'wall_clock_minutes_max':30,'seeds':1,'effective_candidates_max':1},'local_failure_is_not_global_rig_infeasibility':True},'evidence_sources': [{'path':f,'sha256':s} for f,s in protected.items()],'read_only_validation':{'existing_phase_rows_and_saved_small_q_key_arrays_only':True,'new_skin_or_collision_computation':False,'sources_match_saved_fit':True,'file_count':len(protected),'changed_files':changed},'asset_protection':{'hand_and_piano_baselines':formal,'four_approved_static_scenes':read(C/'STATIC_ANCHOR_PROTECTION_R1.json')['four_approved_static_scenes'],'HAND_BASELINES_UNCHANGED':True,'PIANO_BASELINE_UNCHANGED':True,'PRODUCTION_POINTER_CHANGED':False,'authority':'Current Human user approval overrides historical static HUMAN_PENDING labels'},'executed':{'new_dynamic_candidates':0,'new_Blender_Actions':0,'new_blend_files':0,'solver_runs':0,'renders':0,'motion_or_IK_or_root_code_changes':0,'rig_or_mesh_changes':0,'PianoVAM_retarget':False,'full_Musette_or_Web_product_integration':False,'existing_review_server_restarted':True},'STOP':'HUMAN REVIEW','execute_recommendation_automatically':False}
(P/'ARCHITECTURE_REASSESSMENT_STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf8')
required=['MOTION_ARCHITECTURE_CURRENT_STATE.md','CONTACT_CLEARANCE_FAILURE_ANALYSIS.md','MOTION_PLANNING_OPTIONS.md','MINIMAL_NEXT_EXPERIMENT_PLAN.md','ARCHITECTURE_REASSESSMENT_STATUS.json']
assert all((P/n).is_file() and (P/n).stat().st_size>100 for n in required)
assert not list(P.glob('*.blend')) and not list(P.glob('*.mp4'))
for n in required[:4]:
 text=(P/n).read_text(encoding='utf8')
 for target in re.findall(r'\]\(<([^>]+)>\)',text):
  target=re.sub(r':\d+$','',target);assert Path(target).exists(),(n,target)
(P/'DELIVERY_AND_PROTECTION.json').write_text(json.dumps({'status':'PASS_DOCUMENTS_LINKS_AND_READ_ONLY_PROTECTION','protected_source_count':len(protected),'changed_sources':changed,'required_files':{n:{'sha256':sha(P/n),'bytes':(P/n).stat().st_size} for n in required},'new_dynamic_candidates':0,'new_actions':0,'solver_runs':0,'new_blend_files':0,'next_experiment_executed':False},ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'status':status['final_status'],'sources':len(protected),'changed_sources':changed,'required_files':required,'solver_runs':0,'new_dynamic_candidates':0},ensure_ascii=False))
