from pathlib import Path
import json,hashlib,html
P=Path(__file__).resolve().parent;ROOT=P.parents[1];C2=ROOT/'audits/minuet_stage_c_r2_local_finger_overlap_refinement';C1=ROOT/'audits/minuet_stage_c_r1_dual_hand_synchronized_performance'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def dump(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def doc(n,v):(P/n).write_text(v.strip()+'\n',encoding='utf8')
before=read(P/'PROTECTED_INPUTS_BEFORE.json');changed=[p for p,h in before.items() if not Path(p).is_file() or sha(p)!=h]
assert not changed,changed
history=read(C2/'PROTECTED_INPUTS_BEFORE.json')
static_files=[p for p in history if 'piano_hand_static_posture_clearance_refinement_r2' in p and Path(p).suffix in ['.blend','.json'] and Path(p).is_file()]
static_changed=[p for p in static_files if sha(p)!=history[p]];assert not static_changed
midi=ROOT/'audits/minuet_in_g_longer_phrase_validation_r1/source/anna-magdalena-04.mid'
music=read(C2/'AUDIO_AND_TIMELINE_PRESERVATION.json');assert sha(midi)==music['MIDI_sha256']
protection=dict(pass_=True,pre_post_files_verified=len(before),changed_files=changed,static_files_verified_against_R2_receipt=len(static_files),static_changed_files=static_changed,MIDI_sha256=sha(midi),file_write_scope='New R3 audit directory only',new_blend_files=0,new_actions=0)
dump('ASSET_AND_HISTORY_PRESERVATION.json',protection)
contact=read(P/'ORIGINAL_ACTIVE_CONTACT_RECHECK.json')['summary'];gate=read(P/'PREGENERATION_FEASIBILITY_GATE.json');summary=read(P/'R2_BLACK_SUMMARY.json');witness=read(P/'BLACK_KEY_WITNESSES.json');parity=read(P/'WITNESS_SOURCE_PARITY_AND_CONTACT.json');res=read(P/'R2_RESIDUAL_240HZ.json')['samples']
def intervals(rows,field='video_sec'):
    out=[]
    for r in rows:
        t=r[field]
        if out and t-out[-1][1]<.017:out[-1][1]=t
        else:out.append([t,t])
    return out
ov1=intervals([r for r in read(P/'R1_LOCAL_GEOMETRY.json')['middle_ring'] if r['intersecting_patch_triangle_pairs']])
names={'INDEX':'食指','MIDDLE':'中指','RING':'无名指'}
table='| 手指 | 黑键 / MIDI | R2 视频时间（秒，60 Hz 样本） | 最大内部深度 | 性质 |\n|---|---|---|---|---|\n'
for r in summary:
    times='；'.join(f'{a:.3f}–{b:.3f}' if a!=b else f'{a:.3f}' for a,b in r['intervals'])
    table+=f"| {names[r['digit']]} | {r['note']} / {r['midi']} | {times} | {r['max_depth_mm']:.3f} mm | {'目标键触键边缘微差，WARN' if r['midi']==78 else '相邻非目标黑键，确认真实穿入'} |\n"
doc('RIGHT_HAND_OVERLAP_AND_BLACK_KEY_DIAGNOSIS.md',f'''
# 右手重叠与黑键联合诊断

2026-10-11。结论：黑键真实穿入 CONFIRMED，黑键可见干涉 CONFIRMED。本轮生成前门禁 FAIL_CLOSED，无新候选。

所有正文时间为 Stage C 视频时间；音乐时间 = 视频时间 − 0.35 秒。Stage A R2 同音乐时刻使用视频时间 − 0.05 秒。黑键表为 60 Hz 已命中样本区间，真实进入/退出在相邻未命中样本间，不能把三位小数视为精确连续碰撞时刻。

## 中指—无名指残余

保存的 R2 Action 在 240 Hz、0.8–2.1 秒局部复核：1.108333–1.191667 秒共 {len(res)} 个命中样本，最多 16 对局部面相交。进入边界位于 (1.104167, 1.108333]，退出位于 [1.191667, 1.195833)。R1 的 60 Hz 两次原相交区间为 {ov1}。这些是实际 evaluated skin 的 BVH 面交叉，不是骨点距离或轮廓代理。

位于中指与无名指相邻的远端侧面/指尖，受 DIP 主导并混有 PIP 权重。以 1.150 秒的交叉面为例，中指关联顶点平均 DIP/PIP 权重约 0.629/0.366；无名指约 0.840/0.159。MCP 是驱动远端位置的上游关节，不是此处主要发生交叉的皮肤区域。顶点号、面、世界坐标范围见 R2_RESIDUAL_240HZ.json。

该残余全段正在演奏的是食指 A4（R02，0.9928565–1.207142 秒）；中指正在准备 B4（1.207142 秒开始），无名指在准备随后 C5（1.4214275 秒开始）。因此仅针对残余片段，先协调闲置/准备指是有依据的；但不能据此声称整个原重叠及黑键问题都能用闲置指解决。原 R1 在 B4→C5 交接也有相交；较晚的中指 C5/E5 主动触键同时存在相邻黑键干涉。

源动作在 1.133333 秒中指 MCP/PIP/DIP/横展约 1.862/26.894/19.972/−13.655°，无名指约 6.109/8.916/6.836/+9.052°。相向横展与不同屈曲程度把两指远端带到共同空间。R2 仅把无名指横展减去 6°，保留全部屈伸与中指运动，仍不能在连续过渡峰值形成净空。其有限静态取样从 1.05 跳到 1.20 秒，未覆盖 1.108–1.192 秒峰值；已有稠密 R2 失败结果证实这一遗漏，不能归因于新同步或音乐时间改变。

## 黑键身份、区间与性质

{table}

R1 与 R2 的组合和绝大部分时段相同；唯一明确局部差异：RING/C#5 在 R1 的第二段从 1.850 秒开始，R2 提前至 1.733333 秒，提前 7 帧约 0.116667 秒。其他列出的最大深度相同。小指在这次有限远端区域检查中 NOT_FOUND；拇指在完整三视角画面中未见黑键邻接，未据此开展额外皮肤扫描，不能宣称全手全面无碰撞。

除 F#5 以外，这些黑键不是对应手指当时的目标键。F#5 是 R12 无名指主动目标，4.000 秒约 0.563 mm 顶面局部进入，属于微小触键误差 WARN；它不构成本次拒绝门禁的主要理由。

## 有限实际几何证据

仅检查视频显示靠近黑键的 INDEX/MIDDLE/RING/LITTLE 远端强权重 patches（权重 > 0.55，PIP 前 5 mm 以远），不检查掌部、左手、全手逐顶点或全 88 键。只使用右手附近 MIDI 66/68/70/73/75/78/80 共 7 根真实黑键。每帧以保存场景的实际 matrix_world、当前运动键体 evaluated mesh 构建 BVH，并结合真实面平面半空间检查；凸性误差 < 2e−18 m。内部证据阈值为 0.02 mm；报告深度为内部 skin 顶点到最近键体表面的距离，不是沿 z 的压入量，也不是整片 skin 的最大连续穿透深度。

独立复核了 8 个组合的代表顶点；正内部深度样本的三个射线方向均命中向外出口。纯面相交但无内部顶点的个别样本不使用该射线判据，不能把 outside 顶点的射线未命中说成反证。详见 BLACK_KEY_WITNESSES.json 和 WITNESS_SOURCE_PARITY_AND_CONTACT.json。

例如视频 2.600 秒食指/A#4：真实 skin 顶点 35 位于世界坐标 (0.131628379, 0.055700190, 0.006684491) m，距最近实际键侧面 5.603865 mm，45 个局部顶点在实体内，40 对面相交。这不可能仅由俯视投影造成。教学与俯视见指尖被黑键前缘截断/贴入；侧斜视角会被本身背侧皮肤遮挡，因此不能要求内部见证点在所有视角都可直接看到。

正式键表与当前运动目标键真实 mesh 的最大差异为 {contact['max_moving_key_mesh_vs_authoritative_table_mm']:.8f} mm。13 个问题/接触见证时间的 Stage A R2 与 Stage C R1 右手皮肤、骨基矩阵、root 最大差异均为 0；相同黑键关系在原 Stage A R2 已存在。没有打开或重规划其他历史运动。

## 因果等级

- CONFIRMED：原单手动作已含两类缺陷；R2 的无名指横展使其 C#5 干涉提前；中指—无名指交接与键盘净空不能分开设计。
- SUPPORTED：现有局部姿态只保证目标 pad 接触，未充分约束准备/释放指及主动指侧面与邻近黑键。主动 pad 正确不代表整个指尖皮肤有净空。
- UNKNOWN：固定 root 与冻结 Rig 下是否可通过更长区间的多指联合协调全部解决，未求解；不声称冻结 Rig 本身无解，也不声称必须改 root。

见 witness_*.jpg（三列固定相机；红圈仅标识内部几何见证点的投影，不是可见表面的替代或新渲染）及 residual_*.jpg。原图另存 evidence_frames；未改相机、尺度、光照或材质。
''')
doc('LOCAL_JOINT_COORDINATION_DESIGN.md',f'''
# 局部联合协调设计与生成前门禁

唯一参考/拟修复基线锁定 Stage C R1：{read(P/'BASELINE_LOCK.json')['sha256']}。原因是保留原 Stage A R2 右手动作；R2 只用于对照，不叠加它的 −6° 修正，也不在生成后挑选候选。

门禁结论 FAIL_CLOSED。没有执行任何静态关节修正试验，没有生成动态 Action，没有正式局部求解，没有锁定一个未经证实安全的幅度后强行生成。

诊断支持的最小方向：中指—无名指残余时食指 A4 正在主动触键，应保持食指目标 pad；在准备指上联合考虑少量 MCP 相对横展与必要的 PIP/DIP 屈伸，把两指的远端侧面分离，并同时对实际附近黑键限制皮肤净空。MCP/PIP/DIP 都是可用关节，不代表必须全部改变。原四指工程域 MCP 0–75°、PIP 0–95°、DIP 0–65°、spread ±28°仅为数值约束，不足以证明自然手型或可达性。

禁止把增加无名指横展当作下一策略。中指 B4→无名指 C5 的主动交接应保护当前活动 pad 并连续交接，关节增量的支撑边界应具有零位置/速度差，优先平滑 C2 包络；不以逐帧角度特判补丁替代协调。未来若获得额外范围授权，需以事件/接触阶段和实际目标键定义窗口，先锁定全部参数，再至多一次动态求解。这是未来设计方向，未作为本轮已执行成果。

## 为什么本轮不能进入生成

问题并非只在原 0.80–2.08 秒交接窗口。仅食指黑键干涉就占 {gate['index_collision_frame_count']} 个原速帧样本（约 {gate['index_collision_sample_duration_sec']:.2f} 秒的采样覆盖），其中 {gate['index_collision_frames_outside_existing_local_window']} 帧在原局部窗口之外；它还涉及整段开头与结尾。中指后半段 C5/E5 主动触键时进入 C#5/D#5，不能全部归为闲置指避让。

反例：2.600 秒食指/A#4 和 4.916667 秒无名指/C#5 完全位于原局部窗口外。任何保持这些关节/时段不变的局部交接修正，都严格保留该实体穿入。若扩大到全部诊断窗口，至少食指约 4.15 秒的分散阶段要重新协调，已不是短交接窗口的最小修正，而是用户要求另行授权的较长区间右手多指协调。

这不是冻结 Rig 不可解证明。当前缺少的是更广时间与手指范围授权及该范围下的安全可行性验证；不能在现有边界内声称联合约束可同时满足。故在唯一动态候选生成前停止，正式求解尝试 0，候选 0。未修改 root、左手、冻结资产或音乐。
''')
doc('IMPLEMENTATION_REPORT.md','''
# 实现报告

本轮仅在 audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/ 新增可复现诊断、文档及证据媒体。未编辑现有生产代码或历史脚本。

- intake.py：保护输入哈希及完整原视频帧观察。早期 fps 采样页被 diagnostic_media.py 的精确帧索引页覆盖，最终交付使用精确索引。
- inspect_scene.py：读取真实琴键对象标识与边界。
- diagnose.py：R1/R2 有限远端 skin / 7 根黑键、目标指对检查。
- verify_witnesses.py：8 个黑键组合见证、13 时刻 A2/R1/R2 同时钟复核、240 Hz 残余范围与原活动 pad。
- contact_and_scope_gate.py：原 23 音符活动 pad 对真实运动琴键核验、基线锁和生成前门禁。
- diagnostic_media.py：相同时间、相机、原画面像素裁切与见证投影标记；不改变运动或渲染。
- deliver.py：交付文档、状态与历史哈希复核。
- review_server.py：仅在本机提供诊断资料浏览，不是产品集成。

通过 Blender 后台只读打开必要历史 .blend；不保存历史文件，不插入任何动画关键帧、不创建 Action、不调用优化器。所有导入脚本禁用 Python 字节码写入，导入的是有限数学/皮肤读取辅助函数。没有 Stage A/Stage B 重规划，也没有 R3 动态候选或 Blend。正式局部运动求解尝试 0，动态候选 0，参数锁后重试 0。

未生成有效候选，按用户条件不交付 R3 HUMAN_REVIEW.html、R3 三视角或 R1/R2/R3 伪对照。补充 DIAGNOSTIC_REVIEW.html 用于审核失败证据，只引用原 R1/R2 视频和同帧诊断图。
''')
doc('BEFORE_AFTER_SPATIAL_REVIEW.md','''
# R1 / R2 / R3 空间审阅

| 项目 | R1 | R2 | 本轮 R3 |
|---|---|---|---|
| 中指—无名指 | 原两次远端相交 | 减轻但 1.108–1.192 s 残余 | 未生成，NOT_IMPROVED 相对 R2 |
| 非目标黑键 | 已含食指/中指/无名指干涉 | 多数保留，无名指/C#5 第二段提前 | 未修复，NOT_IMPROVED |
| 目标接触 | 原音乐功能通过 | 实际 pad 接触仍在继承域内 | 不改变原轨迹，原态核验 PASS |
| 自然度 | Human 曾接受总体，局部重开 | Human 明确指出修复不足 | 没有新手型可供评估 |

原教学、俯视、侧斜 R1/R2 同步视频均在浏览器按 1× 播放至 5.95 秒结束。工具可核实播放状态；Agent视觉判断来自覆盖完整时轴的精确帧序列与问题同帧三视角原图，不冒充人类连续视觉/听觉体验。最终 Human 质量仍为 HUMAN_PENDING。

教学与俯视可以看到指尖被黑键前缘截断或不可信贴入，侧斜时内部部分可能被手指背部遮挡；实际几何测量排除仅投影的解释。R2 保留两类缺陷，不能将接触 PASS 或原自然动作总体可接受替代空间质量通过。

1.133 秒的指对残余属于两个准备指的远端融合。2.600 秒食指/A#4、3.400 秒中指/C#5、3.883 秒中指/D#5、4.917 秒无名指/C#5 提供窗口外见证。1.800 秒 R2 无名指/C#5 的新提前干涉用于因果对照。红圈标示几何见证点投影，不表示这个内部点直接可见。

没有 R3 before/after 改善可声明；不会把原 R2 视频重新贴上 R3 标签，也不会通过镜头隐藏问题。无需为未生成的候选创建 0.5×验收视频。
''')
doc('APPROVED_MOTION_PRESERVATION.md',f'''
# 已批准动作及资产保持

本轮没有保存任何 .blend，没有新运动 Action。全部文件写入限制在新 R3 审计目录。

本轮前后 SHA-256 校验 {len(before)} 个必要源/资产/历史交付文件，变化 0；另将 {len(static_files)} 个原四静态姿态相关 Blend/JSON 与 R2 已存保护收据对照，变化 0。包含 Stage A R2、Stage B R3 保存源、Stage C R1/R2、右手正式 R2、左手正式 R1、正式 Grand 88-key 发布目录。详见 ASSET_AND_HISTORY_PRESERVATION.json 与 PROTECTED_INPUTS_BEFORE.json。

13 个同音乐时刻的 Stage A R2 vs C R1 右手皮肤/骨基/root差异均为 0，原缺陷是继承的。Stage B R3 不重新求解，其源文件哈希保持。

新增候选运动差异不适用（候选 0）；原两个 root、左手全部关节、右手全部关节与全部时间段、琴键 Action、原 NOTE_ON/OFF、指法、G4 重奏、和弦与统一音乐时钟均保持。增量关节位移/速度/加速度为 0，不重新认证原动作所有工程 WARN。没有新增 V 形外展、钩爪或跳变，因为没有新动作。

原 23 音符（R16/L7）在原速帧及每音符 9 个额外样本共 {contact['samples']} 个活动接触记录中，实际 skin 最大绝对目标面间隙 {contact['max_skin_gap_mm']:.6f} mm，marker {contact['max_marker_gap_mm']:.6f} mm，水平错位 {contact['max_horizontal_miss_mm']:.6f} mm；实际运动键 mesh 最近距离上界 {contact['max_actual_key_mesh_nearest_mm']:.6f} mm。此 PASS 使用继承的 3 mm 接触域，并不是宣称每个 skin 点零间隙。旁侧 skin 进入黑键独立判 FAIL。

原 MIDI、WAV 哈希保持；音乐时长 5.142852 秒，含引入/收尾的视频 5.95 秒。没有新音频、NOTE_ON/OFF 偏移、重采样或静音替换。
''')
answers=[
'Q1：R2 残余是两个准备指远端侧面/指尖的真实交叉，DIP/PIP 皮肤权重主导；保留的屈伸轨迹与相向横展在过渡峰值仍将远端带入同一空间。',
'Q2：食指—G#4/A#4/C#5；中指—C#5/D#5；无名指—C#5/D#5。另有无名指在目标 F#5 上轻微触键进入，独立 WARN。完整时段见诊断表。',
'Q3：上述主要组合均已确认实际三维 skin 进入键体，非仅视觉投影；有限检查不等于全手碰撞普查。',
'Q4：部分相关。R2 横展使无名指/C#5 干涉提前约 0.117 秒；其余多数问题在 A2/R1 已存在，不是 R2 新造成。',
'Q5：单独 −6° 无名指横展没有调整远端曲度/中指准备轨迹，静态取样漏过残余峰值，且没有联合约束黑键。',
'Q6：建立了证据约束和协调方向；未执行修正。生成前门禁发现需要更长区间多指协调，按范围限制停止。',
'Q7：本轮未生成动作，无新改善；相对 R2 为 NOT_IMPROVED，原残余仍存在。',
'Q8：未解决。多时段真实及可见干涉仍在，NOT_IMPROVED。',
'Q9：原态主动目标 pad 保持，1148 个记录覆盖 23 音符，继承接触域 PASS；这不覆盖侧面黑键净空。无 R3 候选可另作验证。',
'Q10：原动作、音乐及文件全部保持；此前整体自然感未因本轮改变，但带缺陷的整体空间质量不能宣称通过。',
'Q11：没有新增异常外展、钩爪、错键或跳变，因为没有修改轨迹；原有缺陷保留。',
'Q12：新候选 0，正式局部求解尝试 0，未消耗唯一候选名额，未重试。',
'Q13：是。冻结资产、四姿态、A2/B3/C1/C2 保存源及历史交付哈希保持。',
'Q14：不具备提交“修复候选”审核条件；可审核诊断与范围瓶颈。FINAL_STATUS=FAIL_CLOSED，STOP — HUMAN REVIEW。'
]
doc('FINAL_ANSWERS.md','# 本轮 Q1–Q14\n\n'+'\n\n'.join(answers))
status=dict(MIDDLE_RING_OVERLAP='NOT_IMPROVED',BLACK_KEY_GEOMETRIC_PENETRATION='CONFIRMED',BLACK_KEY_VISIBLE_INTERFERENCE='NOT_IMPROVED',LOCAL_SPATIAL_COORDINATION='FAIL',ACTIVE_CONTACT_PRESERVED='PASS',NON_TARGET_MOTION_PRESERVED='PASS',DUAL_HAND_MUSIC_FUNCTION='PASS',HUMAN_VISIBLE_QUALITY='HUMAN_PENDING',ENGINEERING_DIAGNOSTICS='FAIL',NEW_DYNAMIC_CANDIDATES=0,FROZEN_ASSETS_UNCHANGED='YES',FINAL_STATUS='FAIL_CLOSED',BLACK_KEY_VISIBLE_INTERFERENCE_DIAGNOSIS='CONFIRMED',FORMAL_LOCAL_MOTION_SOLVE_ATTEMPTS=0,STATIC_CORRECTION_TRIALS=0,status_scope='Original sources unchanged; no R3 dynamic candidate. NOT_IMPROVED is relative to supplied R2. Contact/music PASS describes preserved original function, not a successful repair.',failure_stage='PREGENERATION_FEASIBILITY',baseline='Stage C R1',candidate_path=None,requires_additional_authorization='Longer right-hand multi-finger temporal coordination; root/frozen asset changes not proposed or proven necessary',stop='STOP — HUMAN REVIEW',client_date='2026-10-11')
dump('FINAL_STATUS.json',status)
diag=dict(status=status,method='Finite distal patches and 7 nearby actual black meshes only; 60Hz source frame scan, 240Hz residual window, 13 witness times',baseline_lock=read(P/'BASELINE_LOCK.json'),scope_gate=gate,black_key_summary=summary,residual=dict(first_video_sec=res[0]['video_sec'],last_video_sec=res[-1]['video_sec'],sampling_hz=240,hit_samples=len(res),max_triangle_pairs=max(r['triangle_pairs'] for r in res)),active_contact=contact,preservation=protection,A2_R1_max_skin_delta_mm=max(r['source_parity']['skin_max_mm'] for r in parity['A2']),correction_derivatives=dict(position_delta=0,velocity_delta=0,acceleration_delta=0,reason='No action changed'),full_original_speed_playback=dict(files=[f'synchronized_{v}_before_after.mp4' for v in ['teaching','overhead','side_oblique']],source='R2 existing review page',playbackRate=1,duration=5.95,ended=True,visual_evidence='Exact-frame full sequence sheets and witness triptychs; no claim of human perceptual/audio approval'),limitations=['Finite spatial/temporal samples, not exhaustive collision certification','Geometry status refers to unchanged source','No mathematical proof that frozen rig is globally infeasible','No wider temporal correction authorized or attempted'])
dump('ENGINEERING_DIAGNOSTICS.json',diag)
body='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>Stage C R3 · 生成前诊断停止</title><style>body{max-width:1160px;margin:40px auto;background:#eeeae2;color:#172e2c;font:17px/1.7 system-ui;padding:0 24px}h1{font-size:36px}h2{margin-top:44px}video,img{width:100%;height:auto;background:#555}section{padding:22px;background:#faf8f3;margin:22px 0;border-radius:10px}.fail{border-left:6px solid #ae3f33;padding:20px;background:#ffebe5}a{color:#165d63}button{padding:9px 18px;margin:8px}</style><h1>Stage C R3 · 生成前诊断停止</h1><div class="fail"><strong>FAIL_CLOSED · 新候选 0 · 正式求解 0</strong><p>已确认食指、中指、无名指与相邻黑键真实穿入，且跨越原局部交接窗口。中指—无名指残余仍存在。本轮没有修改动作，也没有可供批准的 R3 候选。</p><p>下列 R1/R2 原视频与诊断证据用于判断范围瓶颈。STOP — HUMAN REVIEW。</p></div><p><a href="RIGHT_HAND_OVERLAP_AND_BLACK_KEY_DIAGNOSIS.md">完整诊断与时间表</a> · <a href="LOCAL_JOINT_COORDINATION_DESIGN.md">协调设计与门禁</a> · <a href="FINAL_ANSWERS.md">Q1–Q14</a> · <a href="FINAL_STATUS.json">最终状态</a> · <a href="ENGINEERING_DIAGNOSTICS.json">工程数据</a></p>'''
for view,label in [('teaching','完整教学'),('overhead','完整俯视'),('side_oblique','完整侧斜')]:
    body+=f'<section><h2>{label} · 原 R1 / R2 同步 1×</h2><p>左 R1、右 R2；保持原相机、尺度、时间轴、显示方式和原声音。不存在 R3 视频。</p><video controls preload="metadata" src="../{C2.name}/synchronized_{view}_before_after.mp4"></video></section>'
body+='<h2>中指—无名指残余</h2><p>固定相机原帧；上 R1，下 R2。未应用 R3 修正。</p><img src="residual_teaching.jpg"><img src="residual_overhead.jpg"><img src="residual_side_oblique.jpg"><h2>黑键真实穿入的同帧证据</h2><p>上 R1，下 R2；教学、俯视、侧斜。红圈是实际内部见证点的相机投影，可能被背侧皮肤遮挡，不是可见轮廓的替代。</p>'
for idx in [26,108,156,204,233,295]:body+=f'<section><img loading="lazy" src="witness_{idx:03d}.jpg"></section>'
body+='<h2>保护与交付</h2><p><a href="APPROVED_MOTION_PRESERVATION.md">原动作保持</a> · <a href="IMPLEMENTATION_REPORT.md">实现报告</a> · <a href="BEFORE_AFTER_SPATIAL_REVIEW.md">空间审阅</a> · <a href="ASSET_AND_HISTORY_PRESERVATION.json">资产哈希复核</a></p><p>HUMAN_VISIBLE_QUALITY = HUMAN_PENDING。没有新动作改善可宣称。STOP — HUMAN REVIEW。</p></html>'
doc('DIAGNOSTIC_REVIEW.html',body)
# Final full-timeline diagnosis includes the second R2 episode, absent from the
# prior task's short-window report. No animation is generated by this addendum.
late=read(P/'LATE_HANDOFF_240HZ.json');lh=[r for r in late['R2'] if r['triangle_pairs']];peak=max(lh,key=lambda r:r['triangle_pairs'])
late_text=f'''完整视频 357 帧同一局部指对检查还确认 R2 第二处相交：视频 {lh[0]['video_sec']:.6f}–{lh[-1]['video_sec']:.6f} 秒（音乐 {lh[0]['music_sec']:.6f}–{lh[-1]['music_sec']:.6f} 秒）。240 Hz 进入边界 (3.725000, 3.729167]，退出 [3.866667, 3.870833)。峰值 {peak['triangle_pairs']} 对面，位于 {peak['video_sec']:.6f} 秒。无名指 R10/D5 持续至 3.778568 秒，随后中指 R11/E5 主动触键，无名指释放；中指同时与 D#5 相交。因此这里是主动/释放交接，不能只调整不受触键约束的两个闲置指。A2/R1/R2 在 51 个局部时刻的 skin 完全一致，此次相交在 R2 的 0.8–2.08 秒修正窗口外，原先短窗口报告未覆盖。三视角可见无名指与中指远端相互覆盖/插入，见 late_overlap_*.jpg 与 LATE_HANDOFF_240HZ.json。'''
n='RIGHT_HAND_OVERLAP_AND_BLACK_KEY_DIAGNOSIS.md';v=(P/n).read_text(encoding='utf8').replace('R1 的 60 Hz 两次原相交区间','R1 的完整 60 Hz 三次原相交区间');v=v.replace('## 黑键身份、区间与性质','## 完整时轴发现的第二处 R2 相交\n\n'+late_text+'\n\n## 黑键身份、区间与性质');doc(n,v)
n='LOCAL_JOINT_COORDINATION_DESIGN.md';doc(n,(P/n).read_text(encoding='utf8')+'\n\n此外，完整时轴确认 3.729167–3.866667 秒还存在中指—无名指的第二处相交，属于 D5→E5 主动/释放交接，伴随中指/D#5 干涉。该窗口也需要单独的接触约束；仅修早段残余无法满足整段质量。\n')
n='BEFORE_AFTER_SPATIAL_REVIEW.md';v=(P/n).read_text(encoding='utf8').replace('原两次远端相交','完整时轴三次远端相交').replace('减轻但 1.108–1.192 s 残余','早段 1.108–1.192 s 残余；另 3.729–3.867 s 相交完全未变');doc(n,v+'\n\n'+late_text)
n='FINAL_ANSWERS.md';v=(P/n).read_text(encoding='utf8').replace('Q1：R2 残余是','Q1：R2 在 1.108–1.192 秒的残余是').replace('Q2：食指','另确认 3.729–3.867 秒第二处中指—无名指相交（D5→E5 主动/释放交接），原 A2/R1/R2 完全一致。\n\nQ2：食指').replace('Q4：部分相关。','Q4：部分相关；晚段指对相交与中指/D#5 干涉同时发生。').replace('且没有联合约束黑键。','且没有联合约束黑键；还完全未覆盖晚段第二处相交。');doc(n,v)
n='IMPLEMENTATION_REPORT.md';doc(n,(P/n).read_text(encoding='utf8')+'\n\n完整时轴追加核验仅运行 late_handoff_verify.py（原保存动作只读、240 Hz、51 个晚段样本）及 late_media.py（原视频同帧截图）。未执行任何第二次修正或优化；本轮所有动作生成仍为 0。\n')
gate['additional_middle_ring_episode_video_sec']=[lh[0]['video_sec'],lh[-1]['video_sec']];gate['additional_episode_source_parity_max_mm']=max(r['skin_vs_R1_max_mm'] for rows in late.values() for r in rows);dump('PREGENERATION_FEASIBILITY_GATE.json',gate)
diag['scope_gate']=gate;diag['residual']['complete_episode_intervals_video_sec']=[[res[0]['video_sec'],res[-1]['video_sec']],[lh[0]['video_sec'],lh[-1]['video_sec']]];diag['residual']['late_max_triangle_pairs']=peak['triangle_pairs'];diag['residual']['full_frame_pair_check_frames_per_stage']=357;dump('ENGINEERING_DIAGNOSTICS.json',diag)
body=body.replace('<h2>黑键真实穿入的同帧证据</h2>','<h2>完整时轴第二处相交 · 3.729–3.867 秒</h2><p>D5→E5 主动/释放交接，R1/R2 完全相同，原修正窗口未覆盖。同时存在中指/D#5 干涉。</p><img src="late_overlap_teaching.jpg"><img src="late_overlap_overhead.jpg"><img src="late_overlap_side_oblique.jpg"><h2>黑键真实穿入的同帧证据</h2>');doc('DIAGNOSTIC_REVIEW.html',body)
print('DELIVERY_DONE',len(before),'source hashes unchanged; candidates=0; FAIL_CLOSED; both R2 episodes documented')
