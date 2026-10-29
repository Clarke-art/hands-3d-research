from pathlib import Path
import json,hashlib,html
P=Path(__file__).resolve().parent;ROOT=P.parents[1];C1=P.parent/'minuet_stage_c_r1_dual_hand_synchronized_performance'
def read(n):return json.loads((P/n).read_text(encoding='utf8'))
def save(n,x):(P/n).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf8')
def doc(n,x):(P/n).write_text(x,encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
g=read('GENERATION_RECEIPT.json');b=read('BAKE_RECEIPT.json');a=read('ACTUAL_VALIDATION.json');s=read('SPATIAL_SUMMARY.json');v=read('VIDEO_VERIFICATION.json');identity=read('SCENE_ASSET_IDENTITY.json');neighbors=read('NEIGHBOR_REGRESSION_CHECK.json')
protected=read('PROTECTED_INPUTS_BEFORE.json');changed=[p for p,h in protected.items() if not Path(p).exists() or sha(p)!=h]
assert not changed,changed
save('ASSET_PRESERVATION.json',dict(pass_=True,protected_files=len(protected),changed=[],candidate_native_asset_identity=identity,source_sha256=sha(C1/'STAGE_C_R1_DUAL_HAND_SYNCHRONIZED_DESIGN_ONLY.blend'),audio_sha256=sha(C1/'piano_performance.wav'),timeline_sha256=sha(C1/'PERFORMANCE_TIMELINE.json'),scope='Before/after content checks of protected frozen assets, approved and historical audit files including R6; no repeat of historical geometric audits'))
total=g['motion_generation_time_sec']+b['seconds']
status=dict(LIGHTWEIGHT_METHOD_IMPLEMENTED='YES',FULL_PHRASE_ANIMATION_GENERATED='YES',MOTION_GENERATION_TIME_SEC=round(total,6),NEW_HEAVY_SOLVER_CALLS=0,ACTIVE_KEY_CONTACT='PASS',MIDDLE_RING_OVERLAP='IMPROVED',BLACK_KEY_VISIBLE_INTERFERENCE='NOT_IMPROVED',ORIGINAL_MOTION_NATURALNESS='HUMAN_PENDING',LEFT_HAND_APPROVED_MOTION_PRESERVED='YES',DUAL_HAND_MUSIC_FUNCTION='PASS',ENGINEERING_DIAGNOSTICS='WARN',GENERALIZATION_EVIDENCE='LIMITED',FROZEN_ASSETS_UNCHANGED='YES',FINAL_STATUS='FAIL_CLOSED',DELIVERY_CLASS='DIAGNOSTIC_ONLY / NOT_APPROVED',STOP='HUMAN REVIEW',motion_time_definition='25.859680 seconds numerical correction plus 3.216221 seconds successful bake/export; excludes verification, rendering, encoding and earlier failed bake API call',early_overlap='IMPROVED, not resolved',late_overlap='NOT_IMPROVED at 3.825 s',black_interference_explanation='Some measured depths decrease, but visible interference persists with regressions; no established overall visible product improvement',human_review_available=True,candidate_count=1)
save('FINAL_STATUS.json',status)
diag=dict(status=status,generation=g,bake=b,basic_engineering_music_pass=a['basic_engineering_music_pass'],engineering_max_violation_deg=a['engineering_max_violation_deg'],engineering_float_tolerance_deg=.002,active_pad_change_max_mm=a['active_pad_change_max_mm'],active_contact_gap_range_mm=[min(r['new']['gap_mm'] for r in a['active_pads']),max(r['new']['gap_mm'] for r in a['active_pads'])],active_contact_horizontal_max_mm=max(r['new']['horizontal_mm'] for r in a['active_pads']),source_peak_velocity_deg_sec=a['peak_joint_velocity_source_deg_sec'],new_peak_velocity_deg_sec=a['peak_joint_velocity_new_deg_sec'],added_velocity_max_deg_sec=a['added_velocity_max_deg_sec'],protected_actions_exact=a['protected_actions_unchanged'],other_rig_curves_exact=a['unmodified_rig_curves_exact'],cameras_exact=a['cameras_unchanged'],spatial=s,neighbor_regression_summary=neighbors['summary'],new_intersection_pair_types=neighbors['new_intersection_pair_types'],native_assets_exact=identity['pass_'],protected_file_count=len(protected),video_count=len(v),notes_right=16,notes_left=7,notes_total=23,music_duration_sec=5.142852,presentation_duration_sec=5.95,formal_motion_attempts=1,nonlinear_optimizer_calls=0,new_heavy_solver_calls=0,limitations=['Finite actual Blender geometry samples, not a continuous collision proof','Convex finger guidance is approximate and source contact guard restricts late avoidance','Pair counts are witnesses, not penetration-volume or perception scores','New shallow black-key contact events exist; persistent deep black-key overlap remains','Human naturalness and final product quality are not approved','One phrase, one source rig, one camera set; other songs and pitches untested'])
save('ENGINEERING_DIAGNOSTICS.json',diag)
doc('IMPLEMENTATION_REPORT.md',f'''# 轻量动画实现与成本

唯一策略 CONTACT_GUIDED_LIGHTWEIGHT_ANIMATION，唯一动态候选，产品结果 FAIL_CLOSED。实际采用有限坐标探测和 FK，没有调用 scipy.optimize、IK 非线性优化器或 R6 轨迹求解器。

- 180 个 30 Hz 规划采样（含末端 5.95 秒），3 根手指、12 个工程坐标、9 根现有骨骼。
- {g['local_fk_evaluations']:,} 次局部 FK 评价，{g['batched_calls']:,} 个向量化调用；三档步长，最多三轮。原姿态/上一帧修正作种子，没有多起点、随机数或版本择优。
- 修正计算 {g['motion_generation_time_sec']:.6f} 秒；成功烘焙/导出 {b['seconds']:.6f} 秒；合计 {total:.6f} 秒，低于 600 秒上限。验证、渲染与编码单列，不计入此数。
- 烘焙 912 个采样点（源关键帧、120 Hz 和事件边界合并），改动 36 条 quaternion 曲线；其余 rig 曲线保持原始完整关键帧与切线信息。
- 最大修正速度约 49.224°/s；原整段峰值 370.964°/s，新版 371.267°/s。没有新增大幅跳变的采样证据；自然度仍待 Human 判断。

`prepare.py` 核实源身份并锁定策略；`generate_once.py` 只运行一次；`bake_validate.py` 写入唯一 Blend；`validate_existing.py` 只读续跑验证；`render.py`、`media.py` 输出同相机证据；其他脚本负责只读回归和报告。

实现期间修复过 Blender 删除关键帧 API 用法：第一次烘焙未保存文件便失败。改用 clear() 后保存唯一 Blend。重开后发现未绑定的源 Action 没被保存，因此只读验证从 C1 加载源 Action；没有重写候选、没有第二轮运动生成。成功 Blend SHA256：`{b['candidate_sha256']}`。这两处属于 API/验证修复，并非隐藏的动作拟合。

没有逐音符手工 pose、指定某帧固定旋转、曲目专属运动补丁。时间窗从事件计算，黑键邻域从音高范围和真实表计算。EARLY/LATE 与四个黑键的专用标签仅用于诊断选帧，不参与生成。平滑为锁定策略中的一次确定性后处理，不作再次搜索。

重型求解调用数 = 0。不会在失败后继续优化、生成第二候选、扩展 8/16 小节或做 Web 产品集成。
''')
doc('BEFORE_AFTER_VISUAL_REVIEW.md','''# 真实前后对照：FAIL_CLOSED / NOT_APPROVED

完整三视角 1× 视频是主要审核入口。18 组同时间、同原相机、同裁剪与缩放的局部图，以及三段 0.5× 静音辅助片段，只作定位。所有完整画面保持 C1 摄像机；标记条位于新增画布区域，不遮挡原画面。

| 检查 | C1 → 轻量 R1 | 结论 |
|---|---:|---|
| 早段 1.133333s 中指/无名指 distal 相交面配对 | 63 → 39 | 几何减少，局部图中仍融合，未解决 |
| 早段 0.95–1.65s 相交配对累计 | 1642 → 885 | 改善；累计数依赖采样，非体积/感知分数 |
| 晚段 3.825s 相交面配对 | 93 → 93 | 未改善，局部图基本相同 |
| 晚段 3.70–3.90s 累计 | 497 → 495 | 不构成有意义改善 |
| 全段 distal MIDDLE/RING 受影响采样 | 58 → 45 | 仍有残余 |
| G♯4 最大黑键内部深度 / 受影响采样 | 4.328 → 3.858 mm / 78 → 124 | 深度减小但事件增多 |
| A♯4 最大深度 | 5.604 → 5.618 mm | 略退化 |
| C♯5 最大深度 | 5.222 → 4.908 mm | 数值减小，仍穿入 |
| D♯5 最大深度 | 5.556 → 5.469 mm | 小幅变化，仍穿入 |

可见黑键效果不认定为整体改善：部分指尖/指侧位置略有变化，但教学与侧斜视角仍保留手指覆盖、嵌入黑键的外观。没有用平均深度下降来宣称产品成功。黑键命中行数 507 → 534，最大深度也没有下降。

邻指回归检查覆盖全部涉及这三根修改手指的九种组合，每种均使用实际 Blender 网格。没有新增其他相交配对类型；只有原有 MIDDLE/RING 问题持续存在。更宽的 MCP 之后 ROI 与历史 distal ROI 的计数口径不同，分别存档，不能混用。

晚段中指正主动演奏 E5，无名指刚离开 D5，源触键保护区和准备恢复包络限制了这一时段可改动作。保留可靠触键的严格策略因此几乎不给晚段让位空间；这说明本轮锁定策略的能力边界，不证明重型求解是必要条件。

局部静帧检查没有支持夸张 V 形外展或新增严重钩爪的结论；完整动态自然度仍为 HUMAN_PENDING。没有宣称 Human 已通过。正式结论：早段有限改善、晚段未修复、黑键问题持续，FAIL_CLOSED。
''')
doc('MOTION_AND_MUSIC_PRESERVATION.md',f'''# 动作与音乐保持

源文件 SHA256 `d8e0f5a85e71323739bfcd4de485ff7a2b4096f8e59bbd4c578ee9d76d3e51a7`，执行前与交付后均一致。

- 右手 16 音符、左手 7 音符，共 23；原音乐 5.142852 秒，视频时间轴 5.95 秒、60 fps、357 帧，统一 lead 0.35 秒。
- NOTE_ON/OFF、指法、目标键、MIDI、13 个活动键 Action 和原双手音频保持。所有非右手 rig 的对象 Action 完整 payload/slot/name 一致；琴键重复音的部分回弹/再按下直接保留原曲线。
- 实际 Blender 60 Hz、事件边界和历史诊断点共 377 个采样；主动指腹新旧最大差 0.000000 mm，横向目标偏差 0 mm；源与新接触间隙同为约 −0.829 至 2.046 mm（包括敲击/交接边界）。没有新增严重脱键或错键证据。
- 左手批准 Action、RIGHT_ROOT、拇指和小指所有曲线完全一致。只调整非主动食指、中指、无名指，原始掌腕节奏与主动姿态不变。
- 工程关节范围最大数值越界 {a['engineering_max_violation_deg']:.10f}°，仅浮点分解误差，低于 0.002° 诊断容差。原 quaternion 被直接保留于主动区间，非主动区间以小旋转增量叠加。
- 173 个场景对象的原生资产信息完全一致：网格、拓扑、权重、形变键及驱动、骨架静止结构、绑定、相机。原教学/俯视/侧斜相机未改动。
- {len(protected):,} 个冻结、批准与历史文件的前后 SHA256 全部一致。只复用必要历史结论，没有重跑全部历史几何审计。
- 六个完整视频（新三视角 + 三视角同步对照）均用同一个原 WAV 编码 AAC；视频与音频从 0 开始，均 5.95 秒。三段 0.5× 辅助片段明确静音，不冒充原速音乐演奏。

自然度保持了主要结构和接触，但“基本自然”最终由 Human 观看判定，本轮不替 Human 批准。
''')
answers=[
('Q1 是否复用 C1？','是。源身份核实，以原双手场景和原右手 Action 为母版，仅复制右手关节 Action。'),
('Q2 是否轻量局部修正？','是。有限局部 FK 坐标探测，非 R6 全段大型优化；重型/非线性优化器调用均为 0。'),
('Q3 实际耗时？',f'数值修正 {g["motion_generation_time_sec"]:.2f} 秒，烘焙 {b["seconds"]:.2f} 秒，合计 {total:.2f} 秒；180 个规划采样、22,878 次局部 FK 评价。'),
('Q4 23 音符、琴键、音频？','保持。16R + 7L、原时钟和键曲线、原 WAV；六个原速视频均 357 帧/60fps/5.95s，音画起点相同。'),
('Q5 两处相交是否改善？','早段改善但未解决：1.133333s 63→39 对相交面。晚段未改善：3.825s 93→93。'),
('Q6 可见黑键穿模是否改善？','不认定整体可见改善。部分测量减轻，但 G♯4 命中采样增加，A♯4 峰值略增，明显残余持续。'),
('Q7 新异常或错键？','未发现新增邻指相交类型、错键或主动脱键；存在新增黑键干涉采样，不能声称无新增异常。'),
('Q8 自然度是否保持？','掌腕、主动指、拇指/小指与左手保持，局部修正有限且平滑；最终自然度 HUMAN_PENDING。'),
('Q9 左手是否完全保持？','是。完整 Action、绑定及原生资产一致。'),
('Q10 手工逐音 pose/专属补丁？','没有。几何与事件驱动；诊断标签有指定时间/音高，但不参与动作生成。'),
('Q11 仅一份动态候选？','是。一次动作计算，一份保存的 DESIGN_ONLY Blend；烘焙 API 修复及只读验证续跑没有生成第二轨迹。'),
('Q12 可复用潜力？','机制使用事件角色、真实几何和工程范围，具有复用潜力。仅验证这段 C1；其他曲目/音高、和弦密度、速度、手型均未验证，证据 LIMITED。'),
('Q13 必须回重型求解？','没有这样的证据。本轮严格保留主动姿态/保护区、使用近似凸包且修正幅度有限；失败只能界定本策略边界，不能证明重型方法必要。没有继续尝试。'),
('Q14 冻结与历史成果？',f'全部 {len(protected):,} 个受保护文件前后 hash 一致，源场景 173 个对象的原生资产一致。'),
('Q15 可直接观看？','可以。HUMAN_REVIEW.html 提供三视角完整原速、新旧同步对照、18 组局部对照与三段静音慢放。全部标记 NOT_APPROVED。')]
doc('FINAL_ANSWERS.md','# 本轮结论：FAIL_CLOSED，诊断视频可审阅\n\n'+'\n\n'.join('## '+q+'\n\n'+ans for q,ans in answers)+'\n\n**STOP — HUMAN REVIEW**\n')
def player(file,title):return f'<article><h3>{title}</h3><video controls playsinline preload="metadata" src="{file}"></video><p><a href="{file}">打开 / 下载视频</a></p></article>'
full=''.join(player(f'normal_speed_{view}_NOT_APPROVED.mp4',label+' · 新候选 1×') for view,label in [('teaching','教学'),('overhead','俯视'),('side_oblique','侧斜')])
comp=''.join(player(f'comparison_{view}_1x_NOT_APPROVED.mp4',label+' · 左 C1 / 右新候选 · 原音频') for view,label in [('teaching','教学同步对照'),('overhead','俯视同步对照'),('side_oblique','侧斜同步对照')])
slow=''.join(player(f'local_{view}_05x_NOT_APPROVED.mp4',label+' · 0.5× 静音辅助') for view,label in [('early','早段'),('late','晚段'),('black_keys','黑键')])
imgs=''.join(f'<figure><img loading="lazy" src="{x["comparison"]}" alt="{x["label"]} {x["view"]} 新旧同尺度对照"><figcaption>{x["label"]} · {x["view"]} · 视频时间 {x["time"]:.6f}s</figcaption></figure>' for x in read('COMPARISON_MANIFEST.json'))
qas=''.join(f'<details><summary>{html.escape(q)}</summary><p>{html.escape(ans)}</p></details>' for q,ans in answers)
doc('HUMAN_REVIEW.html','''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>轻量钢琴动画 R1 · NOT_APPROVED</title><style>
*{box-sizing:border-box}body{margin:0;background:#111719;color:#edf2ed;font:16px/1.7 system-ui,"Microsoft YaHei",sans-serif}main{max-width:1200px;margin:auto;padding:36px 28px 80px}h1{font-size:34px;line-height:1.3;margin:12px 0}h2{margin-top:52px;font-size:25px}h3{font-size:18px}p{color:#bfcac7}.badge{display:inline-block;background:#6e2929;color:#fff3ed;border:1px solid #c5756d;padding:7px 14px;border-radius:5px;font-weight:700}.notice{background:#2a2021;border-left:4px solid #de8c80;padding:18px 22px;margin:24px 0}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.stats div,article,details{background:#1b2528;border:1px solid #344245;border-radius:8px;padding:16px}.stats strong{display:block;font-size:27px;color:#f3e2b6}.stats span{font-size:14px;color:#bfcac7}article{margin:18px 0}video{display:block;width:100%;background:#080b0c}a{color:#a9dccf}nav{display:flex;flex-wrap:wrap;gap:20px;margin:20px 0}figure{margin:22px 0;padding:12px;background:#21191a}img{display:block;max-width:100%;height:auto;margin:auto}figcaption{font-size:14px;color:#c9c0b9;margin-top:8px}details{margin:10px 0}summary{cursor:pointer;font-weight:600}table{width:100%;border-collapse:collapse}td,th{text-align:left;padding:12px;border-bottom:1px solid #344245}.muted{font-size:14px;color:#9baba7}@media(max-width:700px){main{padding:24px 14px}.stats{grid-template-columns:repeat(2,1fr)}h1{font-size:27px}}
</style><main><span class="badge">DIAGNOSTIC_ONLY / NOT_APPROVED</span><h1>已有自然演奏上的轻量修正</h1><p>3D Hands × 88-key Piano · Stage C lightweight animation POC R1</p><div class="notice"><strong>产品结论：FAIL_CLOSED</strong><p>早段邻指相交有所减少；晚段关键相交未改善，黑键穿模仍在。基本关节、触键和音乐检查通过，所以提供真实视频供 Human 判断。此页及视频均不代表获批。</p></div><div class="stats"><div><strong>29.08 s</strong><span>修正计算 + 烘焙</span></div><div><strong>1</strong><span>唯一动态候选</span></div><div><strong>0</strong><span>重型求解 / 非线性优化</span></div><div><strong>23 / 23</strong><span>原音符与琴键保持</span></div></div><nav><a href="#full">完整原速</a><a href="#compare">同步对照</a><a href="#local">局部证据</a><a href="#answers">15 项回答</a><a href="#files">文件</a></nav><h2 id="full">先看完整 1× 演奏</h2><p>使用原 C1 摄像机、原双手音频与时间轴。点击播放即可听到声音；没有自动播放。自然度仍为 HUMAN_PENDING。</p>'''+full+'<h2 id="compare">同一时钟的新旧对照</h2><p>每个对照为同一视频中的左右分屏，避免两个播放器漂移。左侧 C1，右侧本轮唯一候选。原画面仅等比例缩小，未改变相机。</p>'+comp+'''<h2>已确认的边界</h2><table><tr><th>问题</th><th>C1 → 新候选</th><th>判断</th></tr><tr><td>早段 1.133333s 相交面配对</td><td>63 → 39</td><td>改善，仍融合</td></tr><tr><td>晚段 3.825s 相交面配对</td><td>93 → 93</td><td>未改善</td></tr><tr><td>黑键最大内部深度</td><td>5.604 → 5.618 mm</td><td>仍严重，略退化</td></tr><tr><td>G♯4 受干涉采样数</td><td>78 → 124</td><td>新增干涉采样</td></tr><tr><td>主动指腹新旧位置差</td><td>0 mm</td><td>触键保持</td></tr></table><p class="muted">配对数和内部深度是局部几何诊断，不是穿入体积或视觉质量评分。没有以平均数改善替代产品验收。</p><h2 id="local">局部辅助证据</h2><p>以下慢放无音频，不能替代完整原速观看。静帧采用相同原相机、时间、裁剪和尺度。EARLY/LATE 及四个黑键时间来自诊断，不参与动作生成。</p>'''+slow+imgs+'<h2 id="answers">本轮 15 项回答</h2>'+qas+'''<h2 id="files">候选与工程记录</h2><p><a href="STAGE_C_LIGHTWEIGHT_ANIMATION_POC_R1_DESIGN_ONLY.blend">唯一 DESIGN_ONLY Blend（NOT_APPROVED）</a></p><p><a href="LIGHTWEIGHT_ANIMATION_DESIGN.md">锁定设计</a> · <a href="IMPLEMENTATION_REPORT.md">实现与成本</a> · <a href="BEFORE_AFTER_VISUAL_REVIEW.md">可见效果</a> · <a href="MOTION_AND_MUSIC_PRESERVATION.md">音乐与资产保持</a> · <a href="ENGINEERING_DIAGNOSTICS.json">工程诊断</a> · <a href="FINAL_STATUS.json">最终状态</a></p><div class="notice"><strong>STOP — HUMAN REVIEW</strong><p>本轮已停止。没有重型回退、第二候选或扩大曲目。本次失败也不构成必须使用重型求解的证据。</p></div></main></html>''')
assert len(list(P.glob('*.blend')))==1
save('DELIVERY_VERIFICATION.json',dict(required_reports_present=all((P/n).exists() for n in ['LIGHTWEIGHT_ANIMATION_DESIGN.md','IMPLEMENTATION_REPORT.md','BEFORE_AFTER_VISUAL_REVIEW.md','MOTION_AND_MUSIC_PRESERVATION.md','ENGINEERING_DIAGNOSTICS.json','FINAL_STATUS.json','HUMAN_REVIEW.html']),candidate_count=1,videos_verified=len(v),comparison_still_count=len(read('COMPARISON_MANIFEST.json')),candidate_sha256=sha(P/'STAGE_C_LIGHTWEIGHT_ANIMATION_POC_R1_DESIGN_ONLY.blend'),protected_files_unchanged=len(protected),final_status='FAIL_CLOSED',delivery_class='DIAGNOSTIC_ONLY / NOT_APPROVED'))
print('DELIVERY_COMPLETE',json.dumps(status,ensure_ascii=False),flush=True)
