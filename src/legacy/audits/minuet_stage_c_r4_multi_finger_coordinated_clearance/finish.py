from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent;ROOT=P.parents[1];R3=ROOT/'audits/minuet_stage_c_r3_right_hand_local_spatial_clearance';C1=ROOT/'audits/minuet_stage_c_r1_dual_hand_synchronized_performance';C2=ROOT/'audits/minuet_stage_c_r2_local_finger_overlap_refinement'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def dump(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf8')
def doc(n,s):(P/n).write_text(s.strip()+'\n',encoding='utf8')
scope=read(P/'PROPOSED_EVENT_SCOPE.json');pre=read(P/'STATIC_PREFLIGHT.json');actual=read(P/'ACTUAL_STATIC_GEOMETRY.json');gate=read(P/'PREGENERATION_GATE.json');policy=read(P/'PREFLIGHT_POLICY_RECORD.json')
before=read(P/'PROTECTED_INPUTS_BEFORE.json');changed=[p for p,h in before.items() if not Path(p).is_file() or sha(p)!=h];assert not changed,changed
historical=read(R3/'ASSET_AND_HISTORY_PRESERVATION.json');static_receipt=read(C2/'PROTECTED_INPUTS_BEFORE.json');static_files=[p for p in static_receipt if 'piano_hand_static_posture_clearance_refinement_r2' in p and Path(p).suffix in ['.blend','.json'] and Path(p).is_file()];static_changed=[p for p in static_files if sha(p)!=static_receipt[p]];assert not static_changed
assert not (C2/'LOCAL_MODEL_MANIFEST.json').exists()
assert not list(P.glob('*.blend'))
protection=dict(pass_=True,source_files_verified=len(before),changed=changed,static_files_verified=len(static_files),static_changed=static_changed,new_saved_actions=0,new_blends=0,historical_directory_recovered=True,implementation_note='Initial export helper wrote one newly named manifest to R2 due to inherited output-directory binding. No existing file was overwritten. It was moved immediately into R4, helper binding fixed, and absence in R2 verified. This incident is disclosed; final historical assets and reports are unchanged.')
dump('ASSET_PRESERVATION.json',protection)
names={'INDEX':'食指','MIDDLE':'中指','RING':'无名指'}
wtable='| 手指 | 演示窗口 s | 音乐窗口 s | 保持区间 |\n|---|---|---|---|\n'
retained={'INDEX':'A4 主动触键 0.9928565–1.207142，以及 3.349997–3.5642825','MIDDLE':'0–0.778571、2.064284–2.741426、4.635710–结束','RING':'0–0.350000、3.349997–3.3842825'}
for d,ws in scope['windows_video_sec'].items():
    wtable+=f"| {names[d]} | "+'；'.join(f'{a:.6f}–{b:.6f}' for a,b in ws)+' | '+'；'.join(f'{a-.35:.6f}–{b-.35:.6f}' for a,b in ws)+f" | {retained[d]} |\n"
btable='| 指 / 黑键 | 已确认 R1 演示区间 s | R1 最大内部见证深度 mm |\n|---|---|---|\n'
for r in read(R3/'R1_BLACK_SUMMARY.json'):
    btable+=f"| {names[r['digit']]} / {r['note']} | "+'；'.join(f'{a:.3f}–{b:.3f}' for a,b in r['intervals'])+f" | {r['max_depth_mm']:.3f} |\n"
table='| 演示 t / 音乐 t s | 中指—无名指原面交叉→静态检查后 | 黑键检查后 | 主动接触 |\n|---|---|---|---|\n'
for r in actual['poses']:
    pair=next(v for v in r['pairs'] if v['digits']==['MIDDLE','RING'])
    bh='未命中' if not r['black_after'] else '；'.join(f"{h['digit']}/{h['note']}：面交叉 {h['triangle_pairs']}，内部顶点 {h['inside_vertices']}，深度 {h['depth_mm']:.4f} mm" for h in r['black_after'])
    cc='无右手活动音' if not r['contacts'] else '；'.join(f"{v['note']} gap {v['skin']['gap_mm']:.4f} mm / 横向 {v['skin']['horizontal_mm']:.4f} mm" for v in r['contacts'])
    table+=f"| {r['video_sec']:.6f} / {r['music_sec']:.6f} | {pair['before_face_pairs']} → {pair['after_face_pairs']} | {bh} | {cc} |\n"
doc('SPATIAL_CONFLICT_SCOPE.md',f'''
# R4 有限协调范围

2026-10-11。唯一原始运动基线 Stage C R1，SHA-256 `{scope['baseline_sha256']}`；R2 只作为失败方法对照，不继承其 −6° 修正。R3 数据原样读取，没有重新审计整个项目。

本轮预检结果 FAIL_CLOSED，未生成正式动态候选。以下为预检前定义的拟协调支持窗口，不代表已有新轨迹。演示时钟与音乐时钟相差 +0.35 秒；音乐段 5.142852 秒，演示采样从 0 到 5.933333 秒（357帧、视频长度5.95秒）。负音乐时间属于引入准备。

{wtable}

食指首段支撑覆盖首音 D5/G4 时的闲置指冲突，到食指 A4 NOTE_ON 归零；第二段从 A4 NOTE_OFF 起，经 B4/C5/D5 与 G4 重奏的关联手位变化，到中指 C5 NOTE_ON 恢复；末段从无名指 D5 NOTE_ON 经 E5/F#5/G5 与返回 G4 延续到片尾。中指两组窗口分别覆盖 G4→A4→B4→C5→D5、以及 E5→C5→D5→E5→F#5→G5。无名指窗口覆盖相应早段准备/释放与晚段交接恢复。

窗口由原音符事件和既有 0.18秒准备量定义，不为某个渲染帧硬编码姿态。域内接缝计划使用零增量、零速度包络；视频首尾已存在穿入，不把首尾视为必须回到带穿入姿态的人工接缝。动态阶段没有执行，因此边界连续性设计未获得动态验证。

## 指对冲突与主动任务

修复基线是 R1，不能只拿 R2 的 1.108–1.192 秒残余作为全部早段范围。R1 早段面交叉在 60 Hz 已命中样本为 0.966667–1.450000、1.666667–1.850000 秒。A4/食指主动时中指、无名指准备，接着中指 B4 与无名指 C5 交接，随后小指 D5 主动、中指/无名指恢复。1.4214275秒静态检查直接检查 C5 接触。

R3 确认的晚段为 3.729167–3.866667 秒，即音乐 3.379167–3.516667 秒；无名指 D5 向中指 E5 交接。3.825秒中指正在 E5 主动触键，无名指释放，同时中指与非目标 D#5 干涉。这个事件具有真实的邻指、黑键、主动接触耦合。

## 黑键与独立冲突阶段

{btable}

除 F#5 以外，上表为非目标黑键。F#5 是无名指的正常主动目标，0.563mm原局部进入作为独立触键误差检查，不把目标键接触全体豁免。跨阶段食指闲置净空与原 root 路线相联系；晚段中指 E5 的三项约束直接耦合。几何深度不自动等于同等可见严重度；本轮决定性阻断来自正常三视角仍明显的晚段指对穿插。

仅 INDEX/MIDDLE/RING 的 MCP屈伸、PIP屈伸、DIP屈伸、MCP横展共12个增量未知数；小指仅作邻指检查，拇指、小指动作、root、左手、琴键、原事件及音频固定。不是重算全部五指/root的原演奏规划。
''')
doc('MULTI_FINGER_COORDINATION_DESIGN.md','''
# 多指联合协调设计

实现状态 PARTIAL：已实现同时求解食指、中指、无名指12个关节增量的有限静态协调内核，并完成 Blender实际皮肤验证；未实现/执行一份新的连续动态规划轨迹。不把静态结果串成“候选”或逐帧修补。

继承 Stage A R2 使用的四自由度长指 FK 定义，扩展到冻结 Mesh 的实际线性蒙皮（原 Armature preserve_volume=False）。皮肤计算使用冻结 rest matrices、实际 vertex weights 和保存姿态；没有修改骨架、权重、mesh 或 corrective。816个已确认远端局部顶点（含接触标记及邻指区域）用于有限计算，未扫描掌部、左手或全部88键。

联合目标包括：三根手指皮肤对7根附近真实黑键体的当前运动框架距离；INDEX/MIDDLE、MIDDLE/RING、RING/LITTLE 双向近邻表面有符号距离；主动 pad 对原目标运动键面的接触、可用面内范围、适度位置保持；原关节偏离成本与工程边界。关节变量从原源姿态出发同时更新，不先改无名指再改中指。主动指接触优先于闲置姿态保持。

黑键约束使用真实键体几何，非目标安全余量0.5mm；目标 F#5 仅允许所涉皮肤不深于0.65mm的微差，不允许整个目标键实体任意穿越。邻指内核采用有限近邻表面法向场作为数值引导，最后必须以 Blender BVH 实际面相交和正常视角判断，不把这个近似场当作最终碰撞证明。

绝对域 MCP 0–75°、PIP 0–95°、DIP 0–65°、横展 ±28°；相对原姿态增量分别限制 ±18°/±25°/±22°/±14°。这些只是有限工程/姿态偏移界限，不是自然手型批准。原姿态偏离惩罚对 DIP 和横展更强，防止以单纯大外展或极端钩指作为廉价避障。

计划的连续层应在事先限定的支持窗口上求平滑增量，同时约束增量速度/加速度及零边界速度，并在活动接触阶段设置密集检查。由于有限静态门禁已经失败，未创建该动态未知量集，未插值拼接静态解，未调用正式动态求解。

## root政策

root完全固定。早段及多个黑键静态样本可在固定 root 下改善；3.825秒的有限局部求解仍陷在明显指对相交。一次有界非凸局部求解失败不能证明“所有合理关节姿态都无解”，因此没有满足本轮条件式启用 root 的证据，未开放任何补偿自由度。既不声称无需 root，也不声称必须调整 root。

当前瓶颈更像是晚段已有交叉姿态中，局部距离场与起始状态未提供有效的释放/准备避让方向（SUPPORTED），而非已证明冻结Rig不可达。改善接触阶段引导或连续路径初始化的效果尚未验证，本轮不在失败后继续换策略试解。
''')
doc('PREGENERATION_FEASIBILITY.md',f'''
# 正式生成前可行性门禁

结果：FAIL_CLOSED。13个有效静态样本中，晚段3.825秒未消除可见实际相交。正式动态尝试0，候选0。

固定基线、时间映射、12个局部关节自由度、接触/黑键/邻指约束、增量幅度、工程边界及root锁定条件均记录在 PREFLIGHT_POLICY_RECORD.json；源代码SHA一并保留。它是预检策略和最终关闭记录，不冒称存在一份已在预检失败后启动的动态策略锁。预检后没有改变权重、幅度或root重新求解。

有限源姿态模型验证：18个源采样时刻最大 skin差0.000931mm。非采样时刻使用源数据插值；这不是连续全域等价证明。13个参数解均在原Blend中直接重放为独立静态姿态，实际Blender结果优先。首次C5交接处数值模型和实际skin接触差约0.2224mm，已保留，实际仍在接触域内；将来动态阶段需要更精确的源Action采样，不能只依赖该模型。

所有静态检查都使用原root、原键动作、原时间与原摄像机；没有给这些姿态插入关键帧或保存Blend。完整数据见 STATIC_PREFLIGHT.json、ACTUAL_STATIC_GEOMETRY.json。

## 决定性失败

3.825秒（音乐3.475秒）中指E5主动触键、无名指释放。数值终止：{gate['numerical_termination']['message']}，nfev={gate['numerical_termination']['nfev']}。这只是数值停止，不是约束满足。

原中指—无名指93对面相交，检查后92对；主动E5皮肤gap约0.751811mm，横向错位0；本时刻黑键BVH未命中。三视角仍有明显指对穿插。因此黑键及接触改善不能放行。邻指距离场最大残差约7.634mm只作为数值目标残差，不能解释成可靠的皮肤穿透深度。

本次有限检查未证明固定root全域无解，也未证明必须重规划整个4小节。它证明了当前实现和有限预检未找到足以安全进入动态阶段的姿态。因此保留真实失败证据并停止，不将失败静态锚点扩展成唯一动态候选。

## 执行记录的技术纠正

预检开发阶段有1批无效静态检查：其中白键地面保护误用了静止键面，错误阻碍主动指随键下沉。全部结果保存在 INVALID_STATIONARY_FLOOR_DEVELOPMENT_CHECK.json 及对应log，明确作废。修正为实际运动目标键面后完成1批13姿态的有效可行性检查。没有隐瞒该执行记录；不把两批数值计算写成只运行过一次，也不把它们称为动态候选。有效批失败后没有继续调参或搜索。

停止条件已触发：正常视角明确的邻指穿插。不是因极微小隐藏误差追求几何清零。
''')
doc('IMPLEMENTATION_REPORT.md','''
# 实现报告

本轮新增代码全部保存在R4独立目录，未修改现有演奏系统或冻结资产。

- export_local_model.py：只读提取局部权重/Rest/FK/保存姿态及实际skin对照。
- coordination.py：三指12自由度同时优化内核，实际局部LBS皮肤、移动黑键、主动接触及源姿态约束。
- static_preflight.py：有限静态预检与真实数值终止记录。
- scope_and_protection.py：事件支持窗口、时间映射和源文件保护快照。
- verify_static_geometry.py：将固定参数解作为独立静态姿态放回原Blend，检查真实BVH和运动键接触；输出明确标识的静态图。
- render_static_source.py：同音乐时刻、同相机的原态静态对照。
- close_preflight.py：关闭门禁并记录策略、代码哈希及失败。
- finish.py：报告、静态对照页及最终完整性验证。

调用SciPy有界least_squares的是有限静态问题，每次12个关节增量；没有时间序列未知量、root未知量或左手优化。不能称为已经实现并通过了完整多指动态规划。单批内部正常数值迭代保留，多个静态时刻不拼接为动作。

正式动态求解尝试0；新动态候选0；保存Blend0；新Action0；逐帧姿态修补0；有效预检后调参重试0。唯一动态名额未消耗。真实终止为生成前可行性失败，不是超时伪装成功或求解器success即产品通过。

有两项技术纠正完整披露：一是静止白键地面保护导致的无效开发批，已保存原始记录并纠正运动键面模型；二是导出时复用旧辅助函数的输出目录绑定，一份全新 LOCAL_MODEL_MANIFEST.json 曾落在R2目录，未覆盖任何原文件，立即移入R4并修正输出函数。最终确认R2中该新文件不存在，所有历史文件哈希保持。这些纠正均发生在任何动态生成之前。

没有生成有效动态候选，因此不交付R4 HUMAN_REVIEW.html、Blend或R4演奏视频。补充的 DIAGNOSTIC_REVIEW.html 只包含标明“静态预检”的证据及原视频链接。
''')
doc('SPATIAL_CLEARANCE_VALIDATION.md',f'''
# 空间净空有限验证

全部“检查后”都是独立静态预检姿态，未成为保存动画。原R1/R2运动完全未变，不能以本表宣称已修复整段演奏。

{table}

早段1.133333、1.4214275、1.800秒三个锚点的中指—无名指实际面相交清除。晚段3.825秒仍93→92对面相交，静态正常教学、俯视、侧斜均可见穿插；这项明确失败阻止动态生成。没有进行失败后的第二次参数方案。

代表性黑键内部顶点穿入在这些样本中明显减少：例如2.6秒食指/A#4、4.916667秒食指/A#4与无名指/C#5不再有原深层内部顶点见证。若表中仍有面交叉而内部顶点为0，不等于零穿透；保留原交叉对，未扩大成全局表面forensic。未因这些较小局部残余继续搜解，决定性问题是晚段明显指对交叉。

目标F#5在4.0及4.05秒实际skin gap约0.49996/0.49998mm、横向错位0，正常目标接触没有被黑键禁区粗暴排除。未对F#5完整持续段的新动态接触作通过声明，因为没有动态候选。

13个静态时刻的INDEX/MIDDLE及RING/LITTLE未新增面相交。没有穷尽全部指对/全部白键，未声称不存在任何其他键体干涉。静态样本只能提供可行性证据，不能证明原速自然度、速度、加速度或连续过渡。

所有静态图与原态对照保持相同相机、分辨率及确切时间；图上明确标注STATIC，未制作任何新视频，也未用静态图代替Human完整1×验收。
''')
source_contact=read(R3/'ORIGINAL_ACTIVE_CONTACT_RECHECK.json')['summary']
doc('APPROVED_MOTION_PRESERVATION.md',f'''
# 批准动作保持

{len(before)}个受保护源文件在本轮前后SHA-256一致，另核对四静态姿态相关{len(static_files)}个Blend/JSON与原保护收据一致。包括A2、B3、C1、C2、R3报告/证据、正式右手R2、左手R1和正式Grand88发布资产。ASSET_PRESERVATION.json保留具体计数与技术纠正说明。

本轮未保存任何Blend或新Action，未改原音乐/MIDI/琴键/音频。原右手root、全部手指与全部时段、原左手Stage B R3动作仍完全保持；不仅仅是拟定窗口外保持。

拟定局部窗口和增量不会自动修改原动作。静态姿态仅存在于后台Blender进程的内存，用于一次有限预检和截图，退出后未覆盖源文件。四批准静态场景未修改。

原23音符（R16/L7）、时长5.142852s、音高/NOTE_ON/OFF/tempo/velocity/channel/指法/G3+B3+D4和弦/G4重奏/键下沉回弹/统一音频时钟保持。继承R3的原态1148个活动接触实测，源文件及时间线哈希相同：最大skin gap {source_contact['max_skin_gap_mm']:.6f}mm、水平错位0。此次13个静态姿态另核实对应主动指；它不是对一份新动态演奏的功能认证。

右手运动保持PASS、左手保持YES和音乐PASS仅指原批准源完全不变；不代表新修复质量通过。动态增量位移/速度/加速度实际为0（无动作），拟规划的非零增量时间连续性NOT_RUN，不把零修改伪称连续新解通过。
''')
answers=[
'Q1：预检范围为按事件定义的食指3组、中指2组、无名指2组支持窗口；精确演示/音乐时间见SPATIAL_CONFLICT_SCOPE.md。无动态窗口被实际写入动作。',
'Q2：食指、中指、无名指的MCP/PIP/DIP屈伸与MCP横展共12自由度。重点黑键G#4/A#4/C#5/D#5，F#5目标接触另检；附近F#4/G#5作为防止新增干涉的有限边界。',
'Q3：实现了同时包含三指的联合静态协调，不是单指MCP修正；连续动态规划未通过门禁、未执行，因此整体PARTIAL。',
'Q4：root未启用。当前失败不能证明固定root不可行，故条件式root授权没有被激活。是否必须补偿仍UNKNOWN。',
'Q5：早段三个静态锚点改善；晚段3.825秒仍93→92对真实面相交。未生成动态修复，两处完整区间不能宣称解决。',
'Q6：多个静态代表点的深层黑键穿入改善，但部分实际面交叉仍在；完整动态黑键净空NOT_RUN。',
'Q7：原F#5动作未变，4.0/4.05秒静态检查实际接触约0.5mm间隙、水平错位0。无新动态持续段可另作认证。',
'Q8：13个检查点未新增INDEX/MIDDLE或RING/LITTLE相交；晚段MIDDLE/RING仍失败。其他全键体/全时段未穷尽，不作零新增全面承诺。',
'Q9：原右手动作完全保留。没有新的连续演奏供自然度评价，不能声称新修复保留了原速质量。',
'Q10：是，左手Stage B R3批准动作与源文件完全保持。',
'Q11：原23音符、琴键、音频和时钟完全保持，原功能PASS；本轮没有新动态候选。',
'Q12：正式动态候选0、正式动态求解0。有限静态数值检查未被包装成多份动态候选。',
'Q13：是，全部冻结资产和历史报告/候选最终保持；文件哈希验证通过。',
'Q14：关节增量/FK/LBS/真实黑键与接触约束具有复用潜力；其他曲目、手位、左手、连续窗口边界、稳定非凸引导、root补偿均未验证，不称生产级通用能力。',
'Q15：不提交为成功修复的Human原速候选；只提交明确标注的静态可行性失败证据。FAIL_CLOSED，STOP — HUMAN REVIEW。'
]
doc('FINAL_ANSWERS.md','# R4 Q1–Q15\n\n'+'\n\n'.join(answers))
status=dict(MULTI_FINGER_COORDINATION='PARTIAL',EARLY_MIDDLE_RING_INTERSECTION='NOT_RUN',LATE_MIDDLE_RING_INTERSECTION='FAIL',BLACK_KEY_SPATIAL_CLEARANCE='NOT_RUN',ACTIVE_KEY_CONTACT='PASS',RIGHT_HAND_MOTION_PRESERVATION='PASS',LEFT_HAND_APPROVED_MOTION_PRESERVED='YES',DUAL_HAND_MUSIC_FUNCTION='PASS',ENGINEERING_DIAGNOSTICS='FAIL',HUMAN_VISIBLE_QUALITY='HUMAN_PENDING',NEW_DYNAMIC_CANDIDATES=0,FROZEN_ASSETS_UNCHANGED='YES',FINAL_STATUS='FAIL_CLOSED',FORMAL_DYNAMIC_SOLVE_ATTEMPTS=0,ROOT_COMPENSATION_ENABLED=False,status_scope='No new animation. NOT_RUN refers to repaired dynamic intervals; late FAIL is confirmed in finite static feasibility. Contact/music/preservation PASS refers to unchanged original sources and finite active-contact samples, not a successful repaired performance.',static_preflight_early='IMPROVED_AT_THREE_SAMPLES_ONLY',static_preflight_black='PARTIAL',candidate_path=None,stop='STOP — HUMAN REVIEW',client_date='2026-10-11')
dump('FINAL_STATUS.json',status)
diag=dict(status=status,pre_generation_gate=gate,policy=policy,source_skin_model_parity=read(P/'NUMERICAL_SKIN_PARITY.json'),actual_static_geometry=actual,static_numerical_termination=pre,asset_preservation=protection,original_contact_evidence=source_contact,formal_dynamic_execution=dict(attempts=0,candidates=0,bakes=0,save_reopen='NOT_APPLICABLE_NO_CANDIDATE',velocity_acceleration_continuity='NOT_RUN_FOR_NEW_MOTION',second_formal_attempt=False),limitations=['Finite static constraints do not certify temporal feasibility','Signed local nearest-surface field is an optimizer guide; BVH and visible evidence overrule numerical success','No proof of global infeasibility or root necessity','No full 88-key forensic or whole hand scan','An invalid development floor check is retained and excluded; one valid 13-pose preflight batch remains the decision basis'])
dump('ENGINEERING_DIAGNOSTICS.json',diag)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
for i in [0,2,5,6,7,9,11,12]:
    sheet=Image.new('RGB',(1440,750),'#eeeade');draw=ImageDraw.Draw(sheet);t=pre['poses'][i]['video_sec']
    for col,view in enumerate(['TEACHING','OVERHEAD','SIDE_OBLIQUE']):
        for row,(folder,label) in enumerate([('source_static_frames','R1 ORIGINAL STATIC'),('static_check_frames','R4 STATIC PREFLIGHT ONLY')]):
            im=Image.open(P/folder/f'{i:02d}_{view}.png').convert('RGB').crop((610,95,1090,445));x=col*480;y=row*375;sheet.paste(im,(x,y+25));draw.text((x+4,y+2),f'{label} {t:.3f}s',font=font,fill='black')
    sheet.save(P/f'static_comparison_{i:02d}.jpg',quality=96)
body='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>Stage C R4 · 静态可行性失败</title><style>body{max-width:1160px;margin:40px auto;padding:0 24px;background:#eeeae2;color:#193a36;font:17px/1.7 system-ui}h1{font-size:36px}.fail{padding:20px;background:#ffebe3;border-left:6px solid #a6382b}img{width:100%;height:auto}section{padding:22px;margin:25px 0;background:#faf9f5;border-radius:10px}a{color:#15606b}h2{margin-top:36px}</style><h1>Stage C R4 · 静态可行性失败</h1><div class="fail"><b>FAIL_CLOSED · 正式动态求解 0 · 新动态候选 0</b><p>已实现三指12自由度联合静态协调。3.825秒晚段交接仍有92对真实skin面相交，正常视角可见，未进入动态生成。未启用root或换策略重试。</p><p>下方全部为同时间、同相机的独立静态预检图，不能代表连续动画效果。不存在R4演奏视频或Blend。</p></div><p>'''
for file,label in [('SPATIAL_CONFLICT_SCOPE.md','事件窗口'),('MULTI_FINGER_COORDINATION_DESIGN.md','联合设计'),('PREGENERATION_FEASIBILITY.md','门禁及执行记录'),('SPATIAL_CLEARANCE_VALIDATION.md','实际几何'),('FINAL_ANSWERS.md','Q1–Q15'),('FINAL_STATUS.json','状态'),('ENGINEERING_DIAGNOSTICS.json','工程数据')]:body+=f'<a href="{file}">{label}</a> · '
body+='</p><section><h2>决定性失败 · 晚段3.825秒</h2><p>上：原R1静态；下：R4静态预检。中指E5接触仍在，黑键避开，邻指却仍明显穿插。不能因接触或黑键指标改善而放行。</p><img src="static_comparison_07.jpg"></section><h2>其余有限静态锚点</h2><p>上原R1、下静态预检；教学、俯视、侧斜。没有连续性或原速自然度认证。</p>'
for i in [2,5,6,9,11,0,12]:body+=f'<section><img loading="lazy" src="static_comparison_{i:02d}.jpg"></section>'
body+=f'<h2>原演奏参考</h2><p><a href="../{C1.name}/normal_speed_teaching.mp4">原R1完整教学1×（未修复）</a> · <a href="../{C2.name}/normal_speed_teaching.mp4">原R2失败候选1×（未修改）</a></p><p><a href="IMPLEMENTATION_REPORT.md">实现与技术纠正</a> · <a href="APPROVED_MOTION_PRESERVATION.md">原动作保护</a> · <a href="ASSET_PRESERVATION.json">哈希核验</a></p><p>STOP — HUMAN REVIEW。无新的原速动态候选可供批准。</p></html>'
doc('DIAGNOSTIC_REVIEW.html',body)
required=['SPATIAL_CONFLICT_SCOPE.md','MULTI_FINGER_COORDINATION_DESIGN.md','PREGENERATION_FEASIBILITY.md','IMPLEMENTATION_REPORT.md','SPATIAL_CLEARANCE_VALIDATION.md','APPROVED_MOTION_PRESERVATION.md','ENGINEERING_DIAGNOSTICS.json','FINAL_STATUS.json']
assert all((P/f).is_file() for f in required)
dump('FINAL_DELIVERY_VERIFICATION.json',dict(required_reports=required,all_present=True,protected_files=len(before),changed_files=0,new_blends=0,new_videos=0,new_dynamic_actions=0,no_second_formal_solve=True,late_actual_intersection_pairs=92))
print('R4_DELIVERY_FAIL_CLOSED',len(before),'protected files unchanged; 0 candidates; 0 dynamic attempts')
