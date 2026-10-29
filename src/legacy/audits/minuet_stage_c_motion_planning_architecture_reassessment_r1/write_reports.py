"""Documentation only: stdlib reads, arithmetic on saved event times, hashes.
Does not import/run any motion module, FK, geometry evaluator or optimizer.
"""
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent;ROOT=P.parents[1];A=ROOT/'audits/minuet_stage_a_r2_natural_continuous_motion';C=ROOT/'audits/minuet_stage_c_r1_dual_hand_synchronized_performance';R2=ROOT/'audits/minuet_stage_c_r2_local_finger_overlap_refinement';R3=ROOT/'audits/minuet_stage_c_r3_right_hand_local_spatial_clearance';R4=ROOT/'audits/minuet_stage_c_r4_multi_finger_coordinated_clearance';RF=ROOT/'audits/minuet_stage_c_root_finger_spatial_feasibility_r1'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def dump(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
sources={}
def ref(folder,name,needle,label=None):
 path=folder/name;lines=path.read_text(encoding='utf-8-sig').splitlines();line=next(i for i,s in enumerate(lines,1) if needle in s);sources[str(path)]=sha(path)
 return f'[{label or name+":"+str(line)}](<{path.as_posix()}:{line}>)'
def file(folder,name,label=None):
 path=folder/name;assert path.is_file();sources[str(path)]=sha(path);return f'[{label or name}](<{path.as_posix()}>)'
def doc(name,text):(P/name).write_text(text.strip()+'\n',encoding='utf8')
prior=read(RF/'PROTECTED_INPUTS_BEFORE.json');bad=[p for p,h in prior.items() if not Path(p).is_file() or sha(p)!=h];assert not bad,bad
for p in RF.rglob('*'):
 if p.is_file() and '__pycache__' not in str(p):prior[str(p)]=sha(p)
dump('PROTECTED_INPUTS_BEFORE.json',prior)
scope=ref(ROOT/'audits/minuet_target_key_hand_position_planning_r1','00_scope.py','fingers=')
inherit=ref(A,'01_preflight.py',"tl=read(R1/")
fk=ref(A,'coordinated_motion.py','def fk_batch')
targets=ref(A,'coordinated_motion.py','self.surfaces=[]')
roles=ref(A,'coordinated_motion.py','def tasks')
pressure=ref(A,'coordinated_motion.py','def pressure')
priorcode=ref(A,'coordinated_motion.py','out.extend((state[6:]')
generate=ref(A,'02_generate.py','priority=np.unique')
seed=ref(A,'02_generate.py','seedstates=[]')
residual=ref(A,'02_generate.py','def residual')
boxes=ref(A,'02_generate.py','margin=np.full')
solve=ref(A,'02_generate.py','fit=least_squares')
interp=ref(A,'02_generate.py','traj=PchipInterpolator')
bake=ref(A,'03_scene.py',"for i,t in enumerate(A['times']):")
diag=ref(A,'04_diagnostics.py','# Same limited representative skin screen')
copy=ref(C,'03_integrate.py','def copied_action')
screen=ref(C,'03_integrate.py','# Normal visible spatial overlap')
timeline=file(C,'PERFORMANCE_TIMELINE.json')
originalfit=file(A,'COORDINATED_TRAJECTORY_FIT.json')
patch=ref(R2,'05_lock_local_policy.py','policy=dict')
partial=ref(R2,'09_commit_same_locked_motion.py','def evaluate_same_partial')
diagnose=ref(R3,'diagnose.py','def black_relation')
blackhist=file(R3,'R1_BLACK_SUMMARY.json')
pair=ref(R4,'coordination.py','def pair_clearance')
blackcode=ref(R4,'coordination.py','def black_clearance')
contact=ref(R4,'coordination.py','def contacts')
floor=ref(R4,'coordination.py',"owned={n['finger']-1")
statics=ref(R4,'static_preflight.py','for t in times:')
bounded=ref(RF,'bounded_static.py','class Bounded')
actual=file(RF,'ACTUAL_STATIC_COMPARISON.json')
bfit=file(RF,'BOUNDED_STATIC_RESULTS.json')
gate=file(R4,'PREGENERATION_GATE.json')
pol=read(A/'GENERATION_POLICY.json');notes=[n for n in read(C/'PERFORMANCE_TIMELINE.json')['notes'] if n['hand']=='R'];byid={n['note_id']:n for n in notes}
def role(t,j):
 ns=[n for n in notes if n['finger']==j]
 active=[n for n in ns if n['note_on']<=t+1e-10 and t<n['note_off']-1e-10]
 releasing=[n for n in ns if n['note_off']<=t+1e-10 and t<n['note_off']+pol['finger_release_follow_sec']]
 future=[n for n in ns if t<n['note_on'] and n['note_on']-pol['prepare_sec']<=t]
 phase,seq=('ACTIVE',active) if active else ('RELEASE_FOLLOW',releasing) if releasing else ('PREPARE',future) if future else ('IDLE',[])
 return dict(finger=j,role=phase,note=seq[0]['note_name'] if seq else None,note_id=seq[0]['note_id'] if seq else None)
rt=[dict(video_sec=t,music_sec=t-.35,A2_video_sec=t-.05,roles=[role(t,j) for j in range(1,6)]) for t in [1.108333333,1.133333333,1.191666667,1.25,1.4214275,3.75,3.8128535,3.818568,3.825,3.85]]
role_table='| C1演示秒 | 音乐秒 | 食指 | 中指 | 无名指 | 小指 |\n|---|---|---|---|---|---|\n'
for r in rt:
 role_table+=f"| {r['video_sec']:.7f} | {r['music_sec']:.7f} | "+' | '.join(x['role']+(' '+x['note'] if x['note'] else '') for x in r['roles'][1:])+' |\n'
doc('CURRENT_RIGHT_HAND_MOTION_ARCHITECTURE.md',f'''# 当前右手连续运动架构：基于代码的还原

本轮 ARCHITECTURE_REASSESSMENT_ONLY。只读代码与已有结果；没有导入运动模块、打开Blender、运行FK/蒙皮/碰撞检查或任何优化。事件阶段表只对已有JSON时钟做算术解释，不是新运动数据。历史Human批准、WARN与FAIL_CLOSED原样保留。

## 实际链路

```mermaid
flowchart LR
 MIDI[冻结 MIDI 与既定指法] --> Events[原音符事件与可奏键面]
 Events --> Tasks[逐指阶段任务与相邻事件种子]
 Tasks --> Joint[掌腕6维 + 五指20维 + 每音2维触点联合轨迹]
 Joint --> PCHIP[PCHIP插值与120Hz采样]
 PCHIP --> Bake[四元数线性烘焙并重开核对]
 Bake --> C1[C1复制左右手Action并对齐时钟]
 Joint -.生成时.-> Proxy[指腹点及关节中心空间代理]
 C1 -.后续R3诊断.-> Skin[真实局部skin与键体相交]
```

1. **音乐与指法**：上游读取原MIDI右手track 1、ticks 0–4608、PPQ384、tempo428571，赋予预先锁定的16项指法 `[5,1,2,3,4,5,1,1,5,3,4,3,4,5,1,1]`。这不是自动指法，也不是训练过的演奏策略。A2复制已有timeline并保持指法，没有重新运行旧R1的root规划器。证据：{scope}、{inherit}。
2. **键面目标**：EventCoordinator从冻结键表读取目标键可奏面第一片，白键内缩3/7 mm、黑键2/2 mm；触点XY初值由键中心及R1静态锚点纵深给出。每音XY是联合变量，限制在内缩键面，Z为键面+0.5 mm并随目标键旋转。证据：{targets}。
3. **掌腕与五指**：每支撑时刻26维状态（root平移3、额外旋转3、每指3屈伸+1横展共20），加每音2维触点。使用既有冻结FK轴与标记；root不是预先写死的轨迹。基准手型为单一R1锚点NEUTRAL，关节和root有显式变量域。证据：{fk}。
4. **活动、准备、释放与闲置**：`tasks(t)`逐指按 ACTIVE > RELEASE_FOLLOW > PREPARE 优先级选一个任务。活动时追随运动键面；NOTE_OFF后40 ms仍跟随原键，抬升最多2 mm，接触权重由6降到4.2；下一次同指音符开始前180 ms进入准备，前段最多悬高9 mm，最后75 ms下降，准备权重平滑增至4。没有任务的手指并非固定不动：所有指一直受NEUTRAL软先验及时间平滑影响，闲置pad另有5 mm高度软约束。它们没有根据邻指占据空间制定的独立准备通道。证据：{roles}、{priorcode}、{residual}。
5. **重复音机械模型**：最后45 ms部分释放至pressure0.42，下一NOTE_ON后35 ms重新下沉；由最新同键事件拥有机械状态，MIDI事件不变。此逻辑需原样保留，不能在新协调器内另造键时钟。证据：{pressure}。
6. **联合轨迹求解**：事件ON/OFF邻域加约90 ms网格生成支撑点；按当前音与下一不同指音（8 mm准备高度）静态求解生成种子，然后所有支撑点的root和五指再次联合优化，不是五个互不关联的IK求解。各点触键、pad—键体代理、关节中心高度、姿态先验与相邻点速度/加速度全部进入一个带稀疏Jacobian的有界least_squares。变量边界是硬域，其余这些残差是加权软项。证据：{generate}、{seed}、{residual}、{solve}。
7. **求解结果与插值**：保存结果为195支撑点、5102参数，达到75次nfev上限，`success=false`；代码仍在有限性与变量域检查后保存结果。这不抹去历史Human接受，也不能视为收敛或空间可行性证书。随后按状态分量PCHIP插值，120 Hz及额外事件点采样。PCHIP的C1性质不等于实际Blender烘焙或空间净空成立。证据：{originalfit}、{interp}。
8. **烘焙**：从批准静态场景复制派生场景；围绕锚腕应用root变换；各指局部旋转转四元数、连续符号，插入LINEAR关键帧。运动琴键单独绑定pivot。保存重开，比较FK/实际pad及键体变换，保存实际skin供诊断。没有在烘焙阶段重新求解空间关系。证据：{bake}。
9. **C1双手合成**：从批准左右手复制root、rig、键Action，仅右手时间原点+3帧、左手+0帧；键帧值与LINEAR模式保持，单一键盘与音频。C1原演示=音乐+0.35 s，A2=音乐+0.30 s。合成时核对源动作保持、双手x包络及有限接触，没有规划右手内部避碰。证据：{copy}、{screen}。

## 空间能力边界

| 能力 | A2/C1实际状态 | 后续补丁 | 尚缺失 |
|---|---|---|---|
| 五指与root联合变量 | 已实现 | R4只有三指静态，有限root增加5参数 | 无需从零重建FK |
| 音符阶段 | 已有逐指活动/准备/短释放 | R4活动pad和70 ms释放floor | 跨指占用、释放与下一准备的协调计划 |
| 键体空间 | 生成时已有附近白/黑键体box的pad约束，动态主求解使用运动键逆变换 | R3实际skin诊断；R4四指局部skin顶点对七黑键 | 连续表面、非目标白键及所有受root影响手指的一致保护 |
| 邻指空间 | 没有直接指—指残差 | R2单MCP偏移；R4三个相邻指对的局部最近顶点法向场 | 与事件轨迹联合的稳定皮肤分离约束 |
| 自然度与连续性 | 单一静态先验、速度/加速度软项，PCHIP | R4以原姿态增量为先验 | 任务条件化的手型先验与连续避让通道 |
| 验收 | 触点/有限skin采样与Human观看 | R3/R4实际表面检查并保留失败 | 生成中空间可行优先与保存后独立一致门禁 |

A2不是“完全不考虑黑键”：其主求解对局部音域键体做运动坐标转换，但只有pad点；近端/PIP/DIP中心的高度代理仍取静态box顶面、低权重。静态种子中的pad box也为静止键体，并对被任务拥有且weight>1的键允许−4 mm裕量；主求解对应裕量是0。准备任务weight>1也会得到该键豁免，不只真正活动触键。这些都不同于真实皮肤安全证明。证据：{boxes}、{residual}。A2后验只取每指附近少量skin点与掌部点、每音两个时刻，没有邻指皮肤相交检查：{diag}。

## 事件阶段的关键澄清

{role_table}

以上来自原 {timeline} 与A2角色分支，不重新执行规划。

- 早段1.108–1.192 s：食指A4持键，中指准备B4；无名指要到1.2414275 s才显式准备C5，因此该段应称“中指准备、无名指未分配任务”，不能笼统写两指都有准备目标。无名指仍可能受未来支撑点平滑影响而提前运动。
- 晚段：D5由无名指持键，3.778568 s释放；A2释放跟随结束3.818568 s。F♯5准备窗从3.8128535 s开始，约5.7145 ms与释放窗重叠，优先级使释放先执行。到3.825 s无名指已是F♯5 PREPARE，而非A2的RELEASE_FOLLOW。
- R4另以NOTE_OFF+70 ms设置释放floor，因此3.825 s仍受旧D5键面的下界影响，却没有显式F♯5准备任务。这是两个不同模型的已证差异；不能把R4说成原A2连续阶段规划的完整延续。证据：{floor}。历史报告中“释放过程”可描述音乐语义，本轮细化算法状态而不改历史记录。
''')
doc('SPATIAL_CONFLICT_ROOT_CAUSE_ANALYSIS.md',f'''# 空间缺陷与失败机制分级

PRIMARY_FAILURE_CAUSE = SUPPORTED：核心判断是生成机制的空间表述与任务角色协调不足，而非已证明Rig不可行。以下结构事实可CONFIRMED，哪一项对各帧占主导及修复能否成功仍不能由只读分析证明。

## CONFIRMED：代码或已保存测量直接支持

| ID | 事实 | 证据与意义 |
|---|---|---|
| C01 | A2联合root/五指，但没有直接指—指空间残差 | {residual}；共同变量不自动排除邻指相交 |
| C02 | 触点与空间形体不同 | {fk}、{diag}；pad在正确键面不代表侧面、远端曲面或非活动指不穿入 |
| C03 | 触键/净空/自然先验/平滑均为加权软项 | {solve}；只有变量域是硬边界，较低总残差不等于每项满足 |
| C04 | 阶段按各指独立分支选择，无跨指通行/交接协议 | {roles}；共享root和时间差分确实耦合变量，但不表达谁应等待谁释放 |
| C05 | 闲置指主要由单一NEUTRAL与时间正则维持 | {priorcode}；不存在随邻指、键体与下一任务变化的空闲可行域 |
| C06 | 生成已考虑局部白黑键，但只用pad/关节中心代理 | {residual}；不能称“完全无键盘空间规划”，也不能称实际skin约束 |
| C07 | R4约束的距离与几何检查不等价 | {pair}、{blackcode}；最近顶点argmin、局部法向和8 mm硬启停不是三角面间稳定有符号距离；黑键SDF只测顶点，面跨越仍可能漏检 |
| C08 | R4与有限root不是连续事件规划实验 | {statics}、{bounded}；分别13个与3个独立静态状态，没有时序决策或连续边界约束 |
| C09 | 有限root带动未参与关节求解的手指 | {actual}；中心小指/F5新增20面对、19内部顶点、约1.2706 mm；原模型未给非目标白键完整皮肤约束 |
| C10 | 阶段定义不一致 | A2释放40 ms、随后F♯5准备；R4旧键floor70 ms；3.825 s不同角色约束并非同口径 |
| C11 | 数值终止不是工程可行 | A2 nfev=75耗尽；R4中心xtol success仍92面对；有限root中心ftol success、optimality约693.7仍83面对。{originalfit}、{gate}、{bfit} |

## SUPPORTED：有根据的机制解释，但没有隔离因果实验

1. **空间约束缺口是首要结构原因。** 原始相交继承自A2，C1只复制动作；缺少指—指项且仅检查点状键体代理，解释了接触合格而skin失败。不能分配数值“责任百分比”。
2. **相向准备/恢复路径缺少协调。** 当前提前准备、固定中性先验和有限释放任务可能把手指引向另一指所在通道。早段闲置无名指与准备中指、晚段中指E5与无名指转F♯5尤其相关。阶段切换造成目标方向变化是已知，是否是某帧穿入的充分原因未知。
3. **软约束交易与局部引导不足维持坏姿态。** R4中心中指DIP约0.0033°、无名指PIP约0.0102°接近下限，仍有其他自由度余量；不能以“碰到一些边界”推断整体不可行。最近顶点切换/8 mm启停可使有限差分与局部优化不稳定；这是求解机制风险，不是已定位的唯一数值故障。
4. **只改局部角度或root无法修补缺失的任务表达。** 增加变量不增加释放路径、非目标白键或闲置指保护；有限root虽然保持E5，却把问题转给小指，是已观察的例子。
5. **支持点可行与插值可行存在缺口。** PCHIP保状态分量边界不保FK皮肤避碰；LINEAR四元数烘焙也不是解析PCHIP。它们是必须验证的风险，现有证据没有证明烘焙是主要根因。

## UNKNOWN：不能由本轮推断

- 固定root在合理全手事件协调下是否存在自然可行轨迹。
- 有限root配合新的空间与阶段模型是否能成功；±范围扩大是否有效。
- 指法保持不变时所有窗口是否均可行，窗口是否最终必须合并为全段。
- 精确分离/角色规划对每个缺陷的贡献；替换某一种优化器能否单独解决。
- 任意曲目、手型、速度、多声部/和弦下的覆盖率、计算时间与自然度。
- 需要修改冻结Rig、权重、Corrective的证据不存在，不能从局部失败推出物理不可行。

## 已失败路线为何不能继续原样试错

R2采用无名指MCP单自由度、0.80–2.08 s支撑、−6°平台；有限静态检查有改善，但动态残余仍在，且无名指/C♯5干涉部分提前约0.117 s。它不处理另一指曲度、晚段、黑键约束或跨事件角色。其PARTIAL及原严格几何FAIL均保留，不追溯改判：{patch}、{partial}。

R3是实际四指远端皮肤/七黑键诊断，不是新规划器。历史2.17–5.60 mm见证来自不同时间与指键组合，不能套到3.825 s或全部时刻：{diagnose}、{blackhist}。

R4已加入真实加权蒙皮与三指12DOF，但只是有限静态联合残差。中心93→92面对，主动E5约0.752 mm gap，黑键已无命中，说明“改善黑键”与“解决邻指”不是同一条件。保留一次作废的静止键面开发检查及一次有效静态批次；本轮只读有效结果，不隐去该历史：{gate}。

有限root沿用R4模型，中心92→83面对，内部采样见证最大距离6.695→6.651 mm，E5约0.8605 mm gap；D♯5无内部顶点但11面对仍在，相对固定root并无优势。前后邻居相交消失，但3.750 s无名指/非目标E5深度3.0873→4.3084 mm，3.850 s中指/D5约1.3014→1.4193 mm；不能只择取有利指标。{actual}。

本轮不再增加root上限、尝试角度/权重、重优化静态点，也不把当前状态标为FIXED_ROOT_INFEASIBLE。
''')
doc('WHOLE_HAND_PLANNING_OPTIONS.md',f'''# 全手规划方案比较与唯一推荐

以下均为设计，不是实现或实验结果。关于演奏组织的原则用于本项目运动合成，不冒充生物力学普适定律。已有A2阶段机制应扩展，不另造一套MIDI或FK系统。

## 三种不同主导架构

| 指标 | A 事件阶段驱动 PHASE_AWARE_WHOLE_HAND_PLANNING | B 空间约束联合轨迹 SPATIAL_CONSTRAINED_WHOLE_HAND_TRAJECTORY | C 姿态引导窗口 POSTURE_GUIDED_EVENT_WINDOW_PLANNING |
|---|---|---|---|
| 核心决策 | 当前持键、下一准备、释放和闲置如何共同占用局部空间 | 直接为时间支撑上的全手状态施加接触与空间可行域 | 在批准风格邻域内寻找事件姿态并连续连接 |
| 针对邻指/黑键 | 减少相向路径，但没有几何约束仍可能穿模 | 直接针对已知缺陷，但可能找到僵硬姿态 | 减少不自然回中性，但先验本身可能含缺陷 |
| 风格保持 | 用角色一致的路径取代机械回位 | 需额外风格目标，纯距离可导致钩爪/夸张外展 | 最强动机，但不能硬复制碰撞源姿态 |
| 冻结21骨Rig/FK | 全部复用 | 全部复用，增加局部蒙皮距离接口 | 全部复用 |
| MIDI/键/音频 | 事件不变，只调整允许的准备/恢复安排 | 全部作为外部不可变时钟 | 全部作为外部不可变时钟 |
| 新曲目 | 角色规则可复用，不能依赖音名特殊表 | 几何查询可复用，需事件局部邻域和复杂度控制 | 可复用先验接口，但现有四姿态样本覆盖有限 |
| 实现成本 | 中：扩展tasks与窗口/角色转换 | 中高：空间残差稳定性、可行门禁与采样覆盖 | 中：选先验及衔接，但单独不足以解决空间 |
| 计算成本 | 小于大规模几何求解的外围逻辑成本；未测量 | 最主要成本，局部稀疏查询而非88键×全skin×全时刻 | 先验本身便宜，不能免除空间检查 |
| 长曲价值 | 事件图/滚动窗口扩展，需未来上下文 | 能按窗口保持约束，仍可能遇到不可行片段 | 帮助维持风格一致，需更多姿态证据 |
| 单独采用的风险 | 有阶段名却仍无安全通道 | 几何改善但失去自然度、陷入非凸局部解 | 复制当前缺陷或插值经过障碍 |

## 唯一主路线

**PHASE_AWARE_SPATIAL_EVENT_WINDOW_PLANNING：事件阶段驱动、受空间约束的全手局部窗口规划。**

用A组织任务，用B定义不可交易的可行条件，用C仅作为保留风格的软先验。它是一条最小组合路线，不是并行试三套算法或从结果挑赢家。依据：原A2已有联合26维/事件支撑，缺的是指间实际空间与跨指角色协同（{roles}、{residual}）；有限root证明未参与求解的手指也必须进入保护（{actual}）。

建议只有三个新增职责，加一个现有适配层：

1. **事件窗口与角色计划**：输入不可变note/finger/key clock、原动作参考；输出每指“承载接触、准备、卸载/退出、恢复/闲置”的连续任务区间、共享交接约束和窗口边界。阶段可重叠表达，不再靠`elif`截断后突然切换目标。准备指可以提前移动，但任务可行域须排除持键指和非目标键；闲置指根据邻指与下一事件保留自然布局，退出指不默认回固定中性。全部ON/OFF不动。
2. **局部空间可行域**：在冻结FK/LBS上保留四指已有局部patch，并按受影响关系纳入必要拇指/小指保护；距离使用三角面最近特征/稳定局部表面查询，方向取角色与原姿态上下文，不能把开放皮肤patch法向符号当全局inside oracle。计算前固定局部邻接图与附近键清单；白/黑键都用实际运动变换。目标键接触许可只限活动指腹接触区，不豁免整根手指，更不因准备权重大于1就当持键。
3. **有可行门禁的联合窗口轨迹**：复用原稀疏支撑与速度结构；用显式约束或可行性优先的单次受限求解，禁止总加权损失拿触键/严重穿入换取先验。先验、距离偏好、平滑优化只在允许的可行容差内起作用。保留迭代预算、原姿态种子与失败出口，不做多起点/权重扫描。
4. **派生烘焙/验收适配层**：继续复用已有四元数烘焙、单键盘单音频合成，窗口外保持原曲线，窗口内输出仅派生动作；有限局部独立实际skin检查需覆盖支撑点、相间及事件边界。解析曲线、烘焙和保存重开的结果须一致。

建议接口是声明性的：`EventWindowPlan(events, source_motion, phase_policy)` → `role_intervals, task_envelopes, collision_pairs, boundary_states`；`LocalSpaceModel(frozen_geometry, FK, skin_binding, key_clock)` → `contact_and_clearance_constraints(state,time,roles)`；`solve_window_once(plan, reference, budget)` → `feasible_derived_motion 或 failure_certificate`。名称与文件是设计占位，本轮没有实现。

## 什么必须保证，什么只是偏好

| 层级 | 条件 | 处理 |
|---|---|---|
| 不变量 | 冻结资产、关节工程域、音乐事件、左手、窗口外曲线、原键运动 | 硬阻断，优化不得更改 |
| 任务可行性 | 所有活动指实际运动键面接触与可奏域；严重邻指/非目标键体穿入；阶段与边界连续 | 独立容差约束与最终实际几何门禁，不由加权损失豁免 |
| 风格偏好 | 接近批准源的非冲突姿态、适度曲度/横展、少量准备运动、平滑速度/加速度 | 软先验；不能强拉回碰撞姿态 |
| 工程WARN | 浅层、孤立、正常视角不可见且不影响触键的数值几何接触 | 预先限定容差并保留证据，Human裁决；不追求所有隐藏关系严格归零 |

全手协调表示全五指任务与保护一致，不表示必须每时刻给所有骨骼自由参数。最小后续实验保留原root路线，五指关节在授权窗口内联合协调；这测试“补齐机制”是否有效，不再同时试root范围。root作为只读参考参与所有几何计算，接口为未来有证据的小补偿留入口，但本次研究及建议实验不默认启用。冻结root下若失败，只能判测试域未建立可行性，不自动开放root重试。

自然风格不能压缩成一个全局NEUTRAL：选用原批准演奏的相同阶段邻域和四静态姿态作软参考；原源有穿模的自由度不能锁死。边界值/导数与无冲突指姿态优先保持，几何改善后仍要Human完整1×教学视角确认。不存在不看画面就能证明“自然”的通用角度阈值。

无需重写音乐、目标键映射、FK、冻结Rig、音频、Blender基础设施；也不默认引入物理仿真、重新绑定权重或大规模轨迹搜索。跨曲目复用潜力来自事件/角色/几何接口，尚未验证任意曲目，8/16小节与产品集成本轮不执行。
''')
doc('MINIMAL_ARCHITECTURE_EXPERIMENT_PLAN.md',f'''# 最小后续实验计划（仅设计，尚未授权执行）

目标：在原16音符右手输入上验证“生成时的阶段协同+局部真实空间约束”是否能同时改善早/晚交接，保持自然手型和目标接触，再证明与原23音符双手演奏兼容。不是只避开3.825秒，也不预先承诺清除全曲所有干涉。

## 输入、窗口与派生保护

唯一运动参考C1原双手，右手等价于A2时间原点+0.05 s；沿用给定指法、MIDI/键机械时钟/音频/左手。C2不作为修复源，C3/C4/root比较只提供失败证据。源文件保持只读，未来派生代码与候选放新目录，单独manifest标明源哈希、事件域和Human未批准，不写回A2/B3/C1任何文件。

首轮建议两个事件窗口，同一候选中联合求解，不分别试多个候选：

| 窗口 | C1演示范围 s | 音乐范围 s | 上下文与验证任务 |
|---|---|---|---|
| 早段 | 0.778571–2.134284 | 0.428571–1.784284 | 从G4开始，含食指A4持键、中指B4准备/持键、无名指C5准备/持键、小指D5及70ms回弹上下文；覆盖原R1较宽的早段与1.108–1.192残余 |
| 晚段 | 2.741426–4.705710 | 2.391426–4.355710 | E5(R08)准备起点，含C5→D5→E5→F♯5→G5和返回G4交接，含G5释放后70ms；覆盖3.729–3.867及既有局部黑键证据 |

两段是本轮设计的待审议上限，不是已获证明的安全边界。不同于上一轮只定位D5→E5的更短建议，这次扩大到其事件上下文是为了容纳早/晚共同机制；绝不自动合并为整个5.14秒。初始准备、部分中段/片尾黑键历史问题仍可能在窗口外，不可宣称整段产品PASS。

边界有已知困难：R3在早窗起点附近无名指/C♯5、晚窗边界附近食指/A♯4等已有冲突。严格零增量边界与“边界所有冲突清零”可能矛盾。下一轮生成前须用已有保存数据核对具体冲突是否属于本次保证域，建立显式边界未修复清单；若目标冲突延伸到边界、无法在上限内衔接，则0候选FAIL_CLOSED并报告所需新范围，不能通过降低容差/删掉冲突/自动扩窗来放行。此计划不是窗口足够性的证明。

修改域：窗口内五指20关节坐标可共同参与，绝对工程域不变；root轨迹初次实验固定，关节增量信赖域须在下一轮计算前结合源姿态锁定。窗口外所有原关键帧保持；使用零增量、零一阶导边界条件，并验证实际烘焙连接，不能仅宣称quintic/PCHIP就连续。上下文事件只读，不改变源音符时间。

## 未来可修改的非冻结代码职责

只允许在新实现目录派生以下职责；表中的历史文件作为参考，不原地编辑：

| 参考实现 | 新增或替换职责 | 保留部分 |
|---|---|---|
| {roles} | `event_phase_plan.py`：全五指角色、交接与窗口计划；清晰区分接触退出和下一音准备 | 原events与机械key clock |
| {pair}、{blackcode} | `local_spatial_constraints.py`：稳定表面距离、接触许可局部化、附近白/黑键及小指保护 | 冻结FK/LBS、几何绑定与局部ROI证据 |
| {residual}、{solve} | `window_trajectory_solver.py`：同一次局部联合轨迹的可行优先门禁、源风格先验与边界 | 稀疏支撑和有限预算组织；不照搬软罚项当硬约束 |
| {bake}、{copy} | `derived_action_adapter.py`：只烘焙派生窗口、重开与两手兼容检查 | 原键、音频、左手、时间原点和源动作 |
| {diagnose}、{actual} | `window_acceptance.py`：实际表面/目标接触/自然度证据分层 | 有限局部检查，独立于优化代理 |

以上文件名仅设计，未创建模块。全局performance_core、冻结Rig/mesh/weights/corrective、历史审计脚本不修改。

## 生成前门禁：不再多批静态参数搜索

1. 只读确认输入身份、事件角色、源/实际skin绑定与已有失败见证；无重新MIDI/音频功能实验。定位旧释放结束与新准备起点、短任务重叠及窗口边界冲突。
2. 先审查约束的一致性：活动接触许可只覆盖实际指腹；所有跟随root的手指有保护；白键也进入局部候选键域；开放patch不能简单作为闭体符号距离。实现时可用已有存档姿态对新距离接口做非优化的对照验证，禁止用它试角度。
3. 锁定两窗口、五指变量、root固定、目标与非目标键集合、关节域、风格先验、距离容差、单一种子与单次预算。局部键清单按事件涉及键及其紧邻键导出，不是全88键逐顶点遍历。若形成大范围未知保护域则停止审议。
4. 这些检查只能排除已知矛盾，不能证明动态可行。真正的连续可行性必须在下一次唯一正式求解中接受检验；不允许把额外静态多起点、多权重试验藏在“预检”里。

## 一次求解与预算

建议未来只允许一次正式联合轨迹求解、最多一份新动态候选。两窗口同属一个锁定问题，可利用块稀疏结构；不能先后调两套权重挑结果。初值来自原C1曲线，不从多组随机或优化种子择优。使用单一受限求解/可行性过滤策略，在同一次调用内允许正常迭代；不得把外层调权重重启称为一次求解。

建议预算上限200个主要迭代、30分钟墙钟，以先到为准；实际后端的函数评估计数必须另外记录并在实施前锁定上限。这只是实验止损预算，不是运行时间预测。若后端接口无法明确计数或无法表达非交易门禁，生成前停止。失败输出约束证书而非烘焙候选，禁止另换优化器/root域重试。

## 验收与硬阻断

以下是待Human审议的未来实验门禁，不是追溯改判历史成果的标准：

- 不变量：任一冻结文件、原事件/指法/键时钟/音频、左手或窗口外动作发生变化，直接FAIL_CLOSED。
- 接触：活动pad及对应实际skin对原运动键面，计划采用绝对gap≤2.1 mm、横向越界≤0.5 mm；2.1 mm容纳已有C1约2.046 mm源误差，不能事后调大。目标键内部皮肤另检；接触锚点合格不豁免侧面穿入。若原边界已不满足锁定门禁，生成前记录并停止而非改标准。
- 空间：已确认可见的中指/无名指穿插必须实质消除；已知2–6 mm深穿入或新增小指/F5约1.27 mm这类问题必须阻断。建议非目标skin内部采样深度>0.5 mm硬阻断；≤0.5 mm仅可作为WARN候选，仍需实际交线范围与原速三视角确认不可见、孤立且不影响触键。零内部顶点却有面跨越不能自动PASS；严重范围无法判定则UNKNOWN并阻断，不无限细化搜索。
- 关节与曲线：越绝对工程域、窗口边界值/一阶衔接不满足、出现明显跳变/钩爪/V形外展直接阻断。速度/加速度不得只报全局均值；实施前基于原源同事件的既有数据锁定每类上限，不在此无依据发明生理阈值。缺乏足够证据就保留UNKNOWN，不能生成后再选阈值。
- 覆盖：按两窗口60Hz及固定事件/支撑/中点检查，最多再做两层局部时间二分用于定位疑似区间，不求解、不修pose；到达预算仍无法判清就停止。点采样不能冒充严格连续无碰撞证明。所有相邻指与窗口内受影响近键均要看，不能只验证中心样本。
- 保存重开：实际动作与计划FK/局部skin误差沿用0.03 mm一致性预算；只是表示链一致，不是产品PASS。源窗口外Action保留、左手继承与23音符兼容必须同时成立。
- Human可见性：同原机位、完整23音符1×有声演奏，加两窗口同期对照；重点看早段准备、晚段D5→E5→F♯5交接、闲置指曲度及释放恢复。慢放只辅助，不以裁切掩盖缺陷。窗口内达标但窗口外已知缺陷仍存在时，只能报告限定范围改善，不能自动宣布整段Human通过。

任何需要扩大root/关节域、改指法、改源时序、整段重规划、冻结资产改造或第二次正式求解的情况，立即停止并说明新的授权需求。当前没有证据证明两个窗口足够，也没有证据必须重写全段；应由上述边界与可行性门禁决定。

STOP — HUMAN REVIEW。本轮未执行本计划。
''')
status=dict(CURRENT_ARCHITECTURE_IDENTIFIED='YES',WHOLE_HAND_SPATIAL_COORDINATION='PARTIAL',PRIMARY_FAILURE_CAUSE='SUPPORTED',FIXED_ROOT_INFEASIBILITY='NOT_ESTABLISHED',BOUNDED_ROOT_FEASIBILITY='NOT_ESTABLISHED',FROZEN_RIG_CHANGE_REQUIRED='NO_EVIDENCE',RECOMMENDED_ARCHITECTURE_ROUTE='PHASE_AWARE_SPATIAL_EVENT_WINDOW_PLANNING',NEXT_MINIMAL_EXPERIMENT='DEFINED',NEW_STATIC_SOLVES=0,NEW_DYNAMIC_SOLVES=0,NEW_DYNAMIC_CANDIDATES=0,FROZEN_ASSETS_UNCHANGED='YES',FINAL_STATUS='ARCHITECTURE_REASSESSMENT_COMPLETE_READY_FOR_HUMAN_REVIEW',scope='Documentation and read-only saved-data arithmetic only. Proposed experiment not executed or authorized by this report.',confirmed=['A2 joint root/all-finger/contact variables already implemented','A2 no direct finger-finger surface residual','A2 moving-key pad proxy is not actual skin constraint','A2 weighted residuals permit contact-clearance-prior tradeoffs','A2 per-finger task priority and single NEUTRAL prior','R4 nearest-vertex field and 8mm gate differ from surface intersection','R4 and bounded-root comparison use independent static states','Original phase at3.825 is ring PREPARE F#5, R4 still applies old D5 release floor','Bounded root introduced local little/F5 penetration'],supported=['Missing surface feasibility and cross-finger phase coordination are primary architecture gaps','Non-smooth local distance guidance and soft tradeoffs may contribute to failed local fits'],unknown=['Fixed-root natural trajectory feasibility','Necessity and adequacy of bounded root','Finite window boundary feasibility','Cross-piece naturalness and runtime','Dominant causal contribution of each deficiency'],historical_fit={'A2_success':False,'A2_nfev':75,'A2_knots':195,'A2_parameters':5102},event_role_readonly_analysis=rt,evidence_files=sources,proposed_experiment={'windows_presentation_sec':[[.778571,2.134284],[2.741426,4.705710]],'root':'FIXED_ORIGINAL_FOR_INITIAL_MECHANISM_TEST','candidate_limit':1,'formal_solve_limit':1,'boundary_feasibility':'NOT_ESTABLISHED','not_executed':True})
dump('ARCHITECTURE_REASSESSMENT_STATUS.json',status)
answers='''# Q1–Q14

Q1：真实架构是原MIDI+预定指法→逐指事件阶段/键面目标→root6维、五指20维及每音触点联合稀疏轨迹→PCHIP与LINEAR四元数烘焙→C1复制两手Action并统一时间原点。不是固定root的五个独立IK。

Q2：PARTIAL。联合变量、准备/释放和pad—键体代理已有；完整五指真实表面空间与跨事件角色协调没有形成连续生成机制。

Q3：活动pad点正确不能代表手指侧面、邻指或闲置指安全；空间与接触是软罚项，实际skin检查覆盖有限且主要在生成后。

Q4：首要结构缺口是实际空间约束与跨指角色协同，闲置先验和阶段切换是相关机制；局部求解方法有支持性风险。哪个因素对每帧主导UNKNOWN，不归罪于单个时间常数。

Q5：R2单关节没有联合空间上下文；R4/root比较虽然增变量，仍是独立静态软约束，保留不稳定距离代理和释放任务缺口；root带动未保护的小指造成新冲突。

Q6：没有修改冻结Rig的证据。

Q7：不必默认重写。复用原事件、键表、FK/冻结21骨Rig、稀疏支撑、烘焙、双手/音频合成。

Q8：唯一推荐PHASE_AWARE_SPATIAL_EVENT_WINDOW_PLANNING：事件阶段驱动、受真实局部空间约束的全手窗口规划，以批准风格作软先验。

Q9：保留原root路线、窗口外全部动作、左手与音乐；窗口内按角色引用原自然姿态，避免强复制碰撞姿态或固定回NEUTRAL，最后Human完整1×验收。

Q10：有跨曲目潜力，因接口基于事件、角色和几何而非音名/视频帧补丁；其他曲目、和弦/速度及8/16小节未验证。

Q11：在16音符输入上用早/晚两个有限事件窗口验证准备、持键、释放、闲置姿态、邻指和附近白黑键安全及连续衔接，再验证23音符双手兼容；边界可行尚未建立。

Q12：未来派生目录内新增角色/窗口计划、局部空间约束、可行优先窗口求解与派生烘焙/验收适配。历史运动代码本轮零修改，未来也不原地编辑批准源。

Q13：目标冲突不能清除、新增明显穿模、接触丢失/越界、自然度恶化、窗口边界不可衔接、预算耗尽、需扩域或改冻结源，均FAIL_CLOSED；不调参重试。

Q14：冻结资产、批准成果、历史代码/报告均经哈希保护并保持不变。新静态求解0、新动态求解0、新候选0。

STOP — HUMAN REVIEW。推荐方案未执行。
'''
doc('FINAL_ANSWERS.md',answers)
# Final hashes validate every pre-existing protected byte after report creation.
changed=[p for p,h in prior.items() if sha(p)!=h];assert not changed,changed
receipt=read(R2/'PROTECTED_INPUTS_BEFORE.json');ss={p:h for p,h in receipt.items() if 'piano_hand_static_posture_clearance_refinement_r2' in p and Path(p).suffix in ['.blend','.json'] and Path(p).is_file()};assert all(sha(p)==h for p,h in ss.items())
assert not any(P.glob('*.npz')) and not any(P.glob('*.blend')) and not any(P.glob('*.mp4'))
dump('READONLY_EXECUTION_RECEIPT.json',dict(protected_files=len(prior),changed_files=changed,approved_static_related_files=len(ss),approved_static_changed=0,evidence_files_read=len(sources),historical_modules_imported=0,Blender_processes_started=0,new_geometry_evaluations=0,new_static_solves=0,new_dynamic_solves=0,new_dynamic_candidates=0,new_motion_data_files=0,report_generation='stdlib-only reads, hashes, documentation, event-time arithmetic; no planner code executed'))
status['preservation']=dict(protected_files=len(prior),changed_files=0,approved_static_related_files=len(ss));dump('ARCHITECTURE_REASSESSMENT_STATUS.json',status)
print('ARCHITECTURE_REPORTS_COMPLETE',len(prior),'protected',len(sources),'evidence files; zero solves')
