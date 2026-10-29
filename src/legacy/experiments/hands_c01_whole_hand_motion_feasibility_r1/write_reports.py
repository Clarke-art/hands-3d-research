import json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parent
def read(n):return json.loads((O/n).read_text(encoding='utf-8-sig'))
def doc(n,s):(O/n).write_text(s.rstrip()+'\n',encoding='utf8')
I=read('INPUT_BINDINGS.json');pf=read('RIG_PREFLIGHT.json');metric=read('MOTION_FEASIBILITY_METRICS.json');static=read('STATIC_FK_REACH.json');shots=read('STILL_MANIFEST.json');gen=read('MOTION_GENERATION.json');scene=read('SCENE_MANIFEST.json');notes={n['note_id']:n for n in I['notes']}
regions={}
for label,lo,hi in [('R07_R08_R09',notes['R07']['note_on'],notes['R09']['note_on']),('B02_R09_R13',notes['R09']['note_on'],notes['R13']['note_off']),('R13_R14',notes['R13']['note_on'],notes['R14']['note_off'])]:
 rows=[r for r in metric['actual_rows'] if lo<=r['time']<=hi];regions[label]=dict(samples=len(rows),middle_ring_intersection_pairs_max=max(r['finger_intersection_pairs']['MIDDLE_RING'] for r in rows),wrong_key_depth_max_mm=max(r['max_inactive_or_wrong_key_depth_mm'] for r in rows),pad_gap_residual_max_mm=max([abs(r['contact']['residual_from_expected_hover_mm']) for r in rows if 'contact' in r]+[0]))
metric['regional_summary']=regions;metric['render_review']=dict(stills=len(shots),video_generated=False,half_speed_verified=False,quarter_speed_verified=False,reason='Actual collision gate failed; no video render or slow-motion files')
metric['solver_execution_receipt']=gen
(O/'MOTION_FEASIBILITY_METRICS.json').write_text(json.dumps(metric,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
doc('SOURCE_AND_RIG_PREFLIGHT.md',f'''# C01源输入与真实Rig预检 — R1

任务PIANO_C01_WHOLE_HAND_MOTION_FEASIBILITY_R1，2026-10-12 Asia/Shanghai。只在本隔离目录新增文件。最终MOTION_FEASIBILITY_PARTIAL，已生成一份连续Action，但皮肤碰撞门禁失败。

## 输入及冻结身份

C01来源：`{I['candidate_source']}`，SHA256 `{I['candidate_sha256']}`，候选C01_PIANOPLAYER。Human本轮授权仅为隔离动态验证，仍为DESIGN_PROVISIONAL。右手R06作为入口上下文，核心R07—R14；没有改任何手指编号，也没有再搜索指法。

正式RIGHT HAND R2：`{pf['right_frozen_asset']}`，文件SHA256 `{I['right_pointer']['asset']['sha256']}`。实际打开冻结文件、四静态姿态文件及Stage C源Blender：比较原生3300顶点/3298面、逐顶点语义权重、21骨骼rest/head/tail/parent、全部shape-key几何与driver表达式/骨目标，右手副本与R2一致。原生身份摘要 `{pf['right_native_sha256']}`。四静态姿态记录在RIG_PREFLIGHT.json；静态R1/R2原生身份也匹配冻结右手。LEFT HAND R1只作为受保护输入，不生成左手动作。

源Stage C：`{I['source_scene']['path']}`，SHA256 `{I['source_scene']['sha256']}`。其右手副本用于本轮动作；原源文件未保存或覆盖。原场景内已有左手保持不变，可能出现在静帧边缘，不能把它当成本轮双手生成。

## 真实手型及控制接口

Blender {pf['blender']}，本机D:/blender/blender.exe，独立后台进程。当前插件未连接，未改当前交互界面。

实际Rig：21骨骼、16变形骨骼、5个非变形TIP；冻结网格与权重不改。复用Stage A R2 coordinated_motion.py的canonical FK、EventCoordinator和带状联合least_squares。实际Blender pad点与现有FK最大差 `{pf['actual_bone_pad_vs_existing_FK_mm']:.6f}` mm；初始对应皮肤顶点与骨端pad的最大差约{max(pf['actual_skin_vs_bone_pad_mm']):.6f} mm。

整体运动通过STATIC_ROOT_R1.001对象的三轴平移和三轴旋转绕真实腕部锚点实现；WRIST_R及掌部随冻结Rig整体运动。不新增手腕骨骼、不缩放网格或钢琴、不改变绑定、bone rest或拓扑。每指复用三段屈曲与根部spread的已有工程参数，20个指部变量；与6个整体变量联合求解。工程增量域：拇指[0..25,0..25,0..18,−35..35]度，长指[0..32,0..32,0..20,−25..25]度。它们是已用静态规划域，不是人体生理极限，也不能据此证明Rig的一切能力。

使用真实键位、真实指尖及Rig尺寸来求解；PianoPlayer估算的+6.046cm没有作为运动命令或约束输入。

## 88键和时间

原Stage C中全部88键各几何件与现有KEYBOARD_88_KEY_TABLE_R1真实顶点逐件核对，最大差 `{pf['key_geometry_parity_max_mm']:.8f}` mm。白键各可触键区、黑键高度/横向窄面、press pivot/axis及真实Action均读取，关键键位详情保存在RIG_PREFLIGHT.json/key_rows。没有重建或缩放钢琴。

原MIDIanna-magdalena-04.mid与正式PERFORMANCE_TIMELINE逐音绑定，音高、velocity、channel、on/off tick及源秒数不变。模型规划结果也不改。Blender沿用原展示时钟：T_PRESENT=T_MUSIC+0.35，FRAME=1+60×T_PRESENT；0.35没有并入MIDI音乐时间。

从原琴键Action采样453个时间点，存KEY_ACTION_SAMPLES.npz；连续求解读取这些真实角度，烘焙时原琴键Action仍原样保留，没有用新动作替代琴键语义。接触/释放必须面对既有键面运动。

## 可达性预检与限制

先做9个相邻事件初始化姿态，共{static['seconds']:.3f}秒CPU求解，低内存；未安装新依赖或训练。当前指尖FK误差0.004—0.494mm，说明关键触点并非简单不可达。但真实皮肤初检已经出现闲置键侵入和中/无名指互穿，所以骨点可达不等于动作合格。

Blender自带Python无法使用旧Python3.12的SciPy扩展，因此Blender只提取原FK函数并做几何/烘焙；SciPy数值求解在已存在Python3.12环境运行，没有重装环境。首次导入错误日志保留。

后续仅尝试一次真实事件窗口联合轨迹，未进行逐根手指后修补。实际网格最终仍失败，根因指向现有规划约束不足；本轮没有证据证明冻结Rig或C01在所有可能控制策略下绝对不可行。
''')
table='| ID | MIDI/音名 | 指 | 源ON秒 | 源OFF秒 | Blender ON秒 | Blender OFF秒 |\n|---|---|---|---|---|---|---|\n'+'\n'.join(f"| {n['note_id']} | {n['midi']}/{n['note_name'].replace('F#','F♯')} | {n['finger']} | {n['source_on_sec']:.7f} | {n['source_off_sec']:.7f} | {n['note_on']:.7f} | {n['note_off']:.7f} |" for n in I['notes'])
doc('C01_MOTION_PLAN.md',f'''# C01整手连续动作方案与实测边界 — R1

本轮已生成唯一隔离动作，最终MOTION_FEASIBILITY_PARTIAL，不作为可发布方案。保留C01，R06入口上下文＋R07—R14核心；不生成其余23音动作。

{table}

## 连续策略

复用Stage A R2联合求解：105个事件/阶段支撑节点、2748变量（各节点6个掌根/整体旋转＋20个指部自由度、每音2个可触键区坐标）、27032残差。位置/旋转/五指同时求解，包含时间速度、加速度正则及下一音准备。不是指尖关键帧之间直线插值，也不是固定root的单指重定向。

真实准备窗口0.22秒；末0.075秒下降。活动手指跟随正在运动的真实键面，准备指在键面上方约9mm进入；释放阶段跟随原键回弹约40ms。R06→R07同指重复的原45ms键复位窗口内，计划有至多2mm抬指再触键，没有新增休止或改MIDI。

起点{I['clip_start_sec']:.7f}秒、终点{I['clip_end_sec']:.7f}秒为展示时钟。R14最终OFF位于片段边界，后续R15不生成，故不认证R14→R15整套释放/重按循环。

求解后的整体/关节状态采用PCHIP连续插值，再以120Hz及精确事件/节点采样成501组状态。Blender烘焙为新掌根Action与五指Action，绝对帧时钟不变；骨骼四元数符号连续化。高频线性烘焙有有限采样/速度转折误差，不据此认定自然。

数值预算固定最多40次外层评估，仅一条连续轨迹，无重启、无局部修补。轨迹文件已保存后，元数据模块哈希路径迁移错误导致脚本退出；保持同一motion.npz并补充可核实导出收据，没有重算。未保留优化器最终收敛标志/nfev，明确记为null，不伪称收敛；最终门禁基于已保存/实际烘焙的网格结果。

## 各过渡的目标与结果

- R07→R08：以真实G4和E5键面约束、拇指保持/释放与中指提前准备共同求解掌根移动。实际做到了触点接近，但该窗口中/无名指相交峰91对，错误键侵入峰5.144mm，未自然通过。
- R08→R09：中指E5释放、拇指C5提前布置；仍带有此前互穿/邻键问题，不能把触点到位当作自然回位成功。
- R09→R13：C5/D5/E5/F♯5/G5依次1/2/3/4/5不改。历史3.825秒探针中/无名指相交122→0，但整个五音窗口仍有峰41对，最大错误键侵入3.441mm，交叉没有被整段清除。
- R12黑键：四指确实跟随F♯5真实高键面；4.0278535秒处其他手指仍侵入C♯5、E5等邻键，未通过完整避障。
- R13→R14：小指G5到拇指G4的整手回位已生成，pad可到达，但此窗口错误键侵入峰4.991mm；在4.670710秒处拇指侵入A4约4.671mm，不能判为可执行回位。

## 已识别的策略缺口

现有目标函数主要约束五个pad、少量关节中心与键体代理，没有对完整指腹/指侧/闲置指的皮肤体积和指间互穿建立硬约束。掌根移动加上关节平滑不能自动消除这些缺口；3mm的pad避让和触点区边界也不能代表实际手指厚度。

大手位移动时，正在触键的拇指、准备的中指以及闲置无名指需要共同的几何避障/释放策略；目前仅有代理点成本，导致局部旧B02改善，却在入口和五音准备阶段留下问题。后续若授权，应在现有联合求解器上处理真实皮肤/可触键区足迹和释放可用时间，而不是修改C01、拉长手指或继续逐指补洞。本轮停止。
''')
shotmap={x['label']+'_'+x['view']+'_'+x['version']:x for x in shots}
visual='\n\n'.join(f"### {x['version']} · {x['label']} · {x['view']}\n\n展示时间{x['time']:.7f}秒，真实求值Action静帧；[原图]({Path(x['file']).as_posix()})\n\n![{x['label']}]({Path(x['file']).as_posix()})" for x in shots)
doc('HUMAN_VISUAL_REVIEW.md',f'''# Human视觉复核 — C01 R1

状态MOTION_FEASIBILITY_PARTIAL；不是Human视觉PASS。只渲染7张720p Workbench静帧；正确显示原对象黑白键颜色，保留网格线便于看交叠。左手若出现在画面边缘，是源场景未改变的既有左手，不是本轮双手生成。

视频未渲染。真实碰撞门禁失败，按任务要求停止；无1x视频、0.5x或0.25x降速文件，不能宣称慢速自然度已经验收。没有临时PNG序列/GB缓存，仅保留这些交付静帧。所有截图都是同一份保存Action的求值结果，没有重算或选择替代动作。

隔离场景：[C01_WHOLE_HAND_MOTION_DESIGN_PROVISIONAL_R1.blend]({Path(scene['path']).as_posix()})。其中实验场景{scene['scene']}，60fps，原绝对时间轴；新Action为C01_R1_WHOLE_HAND_ROOT_DESIGN_ONLY及C01_R1_FIVE_DIGIT_COORDINATED_DESIGN_ONLY。可由Human在Blender中低速复核，不能替换旧动画。

## 重点判断

1. R07→R08：观察中/无名指明显交叉。R08触键+35ms截图对应80对相交；原同时间为0。不能仅看上行指序就断言该段成功。
2. B02同视角、同时间3.825秒：旧中/无名指明显交叉，新图在该探针分开；数值122→0。但五音前段仍有互穿峰41对，单张新图不能证明整个B02已解决。
3. F♯5四指：用侧斜图看键面高差、指腹侧面及闲置指邻键侵入；接触点到位不等于整指体避障。
4. 八度回位：R14拇指接近G4，但拇指侧面/其他区域侵入邻A4，不能批准回位。
5. 手腕自然度：240Hz实际腕点速度峰277.226mm/s，加速度峰14527.103mm/s²；不是生理门槛或视觉判定。连续Action存在并已测量，但没有视频与慢放自然度通过证据。

{visual}

**STOP — HUMAN REVIEW。** 本轮不再优化，不扩展完整23音或双手制作。
''')
doc('FINAL_RECOMMENDATION.md',f'''# 最终建议 — PIANO_C01_WHOLE_HAND_MOTION_FEASIBILITY_R1

**MOTION_FEASIBILITY_PARTIAL**。真实隔离连续Action已生成并保存，C01、冻结手型、琴键Action和原事件身份保持。指尖大体到位，但实际皮肤仍互穿、侵入邻键，因此没有通过“自然、连贯、无明显穿指穿键”的目标。不是Rig绝对不可行的证明，也不是教学批准。

| 必答问题 | 实测结论 |
|---|---|
| C01在现有Rig是否具备实际运动可行性？ | 存在可生成的连续运动，实际活动pad相对目标键面最大残差1.354mm、横向超出0mm；但完整皮肤碰撞失败，合格动态可行性尚未证明。 |
| R07→R08能自然完成吗？ | 未通过。窗口相交峰91对，错误键侵入峰5.144mm；R08触键+35ms时相交80对，原同时间0对，新增问题明确。 |
| B02原中/无名指交叉消失了吗？ | 仅历史3.825秒探针122→0。完整R09—R13窗口仍峰41对，不能宣布B02整段已清除交叉。 |
| 是否有新互穿、黑键穿模或腕突跳？ | 有互穿及黑键侵入：例如R07时中指进入D♯5约5.144mm。实际腕点有连续采样轨迹，但速度/加速度峰277.226mm/s、14527.103mm/s²，自然度和突兀程度未通过慢放审阅。 |
| R13→R14八度回位可行吗？ | 可生成并接近G4，未合格。窗口错误键侵入峰4.991mm；4.670710秒拇指进入邻A4约4.671mm，较原同时间约4.184mm更深。 |
| 相比原动画有可观察/测量改善吗？ | 局部有：历史B02探针相交122→0，F♯5触键+35ms邻键最大侵入3.364→1.952mm。但R08新增80对交叉，B02探针邻键侵入0.727→2.823mm，八度回位也有退步；不能判定整体改善。 |
| 值得扩展完整23音双手吗？ | 当前不建议。先在相同短片段解决整手/五指真实皮肤避障、键面接触足迹、释放与复位协调，再单独申请下一阶段。无需先改指法或重训，不能直接推广。 |

## 门禁证据

一套连续轨迹、501组状态、两个新Action，仅R06上下文与R07—R14核心。掌根和五指联合求解；未将PianoPlayer估计厘米数当作腕命令。265个实际皮肤/键体样本，另有5个关键时刻的手/键三角面交叉检查，以及756个240Hz真实腕点样本。实际腕点与计划位移最大差0.054mm，说明动作已真实烘焙；这不是自然度证明。

实际错误键侵入最大5.144mm，中/无名指相交峰91对。相交指标是同一强权重真实皮肤ROI的BVH面配对计数，不是穿透体积或深度。鍵侵入深度来自求值后顶点与真实凸几何件的内侧平面距离，另以实际三角面交叉验证；有限采样不是连续零碰撞证明。

原琴键和其他源Action payload逐项保持，手部原生网格/权重/骨骼rest/修正形状及驱动表达式身份保持。源MIDI、候选C01和保护文件哈希前后核对。重复G4沿用原Action的部分复位：该窗口角度从约0.08712rad回到最低约0.03659rad，并未完全归零；真实指尖pad在复位窗口最高离键约1.100mm。因为皮肤侵入与物理琴键机构未建模，不能认证完整释放/再次触键已正确。

## 根因及停止决定

当前现成接口有整手控制能力，问题不能简单归为“没有手腕移动”。已允许真实掌根平移/旋转并约束速度、加速度，仍出现错误。关键缺口是优化目标只用pad/关节代理描述键体避让，没有完整皮肤体积、相邻指互穿和释放时机的联合约束；端点到位与轨迹平滑不自动保证几何安全。

静态诊断用了{static['seconds']:.3f}秒CPU；连续求解只尝试一次、固定40步预算。运动导出后出现元数据路径引用错误，保留同一运动数组而未重算；优化器收敛标志/nfev未保留，记null。Blender实际烘焙/网格检查约{metric['seconds']:.3f}秒。未安装大型环境、修改指法、绑定、拓扑或冻结资产。

已停止所有动作优化及视频渲染。交付7张真实静帧和隔离Blend，没有PNG帧序列缓存；0.5x/0.25x自然度未通过，未伪造降速验收。全部仍为DESIGN_PROVISIONAL，权重商业授权状态不因本轮动作实验改变。

交付：SOURCE_AND_RIG_PREFLIGHT.md、C01_MOTION_PLAN.md、MOTION_FEASIBILITY_METRICS.json、HUMAN_VISUAL_REVIEW.md、本报告；额外保留唯一Action场景、运动数组、输入/源保护哈希、静帧和全部运行日志。

**STOP — HUMAN REVIEW。** 不扩展完整23音双手动画，不替换旧方案。
''')
status=dict(task='PIANO_C01_WHOLE_HAND_MOTION_FEASIBILITY_R1',status='MOTION_FEASIBILITY_PARTIAL',candidate='C01_PIANOPLAYER',authority='DESIGN_PROVISIONAL',continuous_actions_generated=True,motion_candidates=1,local_repair_iterations=0,contact_screen='PASS',collision_screen='FAIL',human_visual_acceptance='NOT_APPROVED',b02_historical_probe=dict(old_pairs=122,new_pairs=0),b02_whole_window_max_pairs=41,full_clip_middle_ring_max_pairs=91,wrong_key_penetration_max_mm=metric['passive_or_wrong_key_max_vertex_depth_mm'],video_generated=False,slow_motion_verified=False,expand_to_full_23=False,stop='STOP — HUMAN REVIEW')
(O/'FINAL_STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('REPORTS_COMPLETE',status['status'])
