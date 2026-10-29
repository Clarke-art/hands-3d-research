# C01源输入与真实Rig预检 — R1

任务PIANO_C01_WHOLE_HAND_MOTION_FEASIBILITY_R1，2026-10-12 Asia/Shanghai。只在本隔离目录新增文件。最终MOTION_FEASIBILITY_PARTIAL，已生成一份连续Action，但皮肤碰撞门禁失败。

## 输入及冻结身份

C01来源：`<HANDS_ROOT>_sequence_fingering_planning_r1\SEQUENCE_CANDIDATES.json`，SHA256 `86ca8525577943389bf5ad73716c1062609d886a180766037c0159eb1fe495a9`，候选C01_PIANOPLAYER。Human本轮授权仅为隔离动态验证，仍为DESIGN_PROVISIONAL。右手R06作为入口上下文，核心R07—R14；没有改任何手指编号，也没有再搜索指法。

正式RIGHT HAND R2：`<HANDS_ROOT>\production_spec\right_hand_product_baseline_r2\RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R2.blend`，文件SHA256 `c946fed318fa88c238d9aacc30cfb4e52f268848f0ad65a4dcbf594754d791f0`。实际打开冻结文件、四静态姿态文件及Stage C源Blender：比较原生3300顶点/3298面、逐顶点语义权重、21骨骼rest/head/tail/parent、全部shape-key几何与driver表达式/骨目标，右手副本与R2一致。原生身份摘要 `68dbc53e29b636bc8e1c573644d19a7da99ceec71eba3d1dcee7a5f1c01c472d`。四静态姿态记录在RIG_PREFLIGHT.json；静态R1/R2原生身份也匹配冻结右手。LEFT HAND R1只作为受保护输入，不生成左手动作。

源Stage C：`<HANDS_ROOT>\audits\minuet_stage_c_r1_dual_hand_synchronized_performance\STAGE_C_R1_DUAL_HAND_SYNCHRONIZED_DESIGN_ONLY.blend`，SHA256 `d8e0f5a85e71323739bfcd4de485ff7a2b4096f8e59bbd4c578ee9d76d3e51a7`。其右手副本用于本轮动作；原源文件未保存或覆盖。原场景内已有左手保持不变，可能出现在静帧边缘，不能把它当成本轮双手生成。

## 真实手型及控制接口

Blender 5.1.2，本机D:/blender/blender.exe，独立后台进程。当前插件未连接，未改当前交互界面。

实际Rig：21骨骼、16变形骨骼、5个非变形TIP；冻结网格与权重不改。复用Stage A R2 coordinated_motion.py的canonical FK、EventCoordinator和带状联合least_squares。实际Blender pad点与现有FK最大差 `0.000313` mm；初始对应皮肤顶点与骨端pad的最大差约0.026754 mm。

整体运动通过STATIC_ROOT_R1.001对象的三轴平移和三轴旋转绕真实腕部锚点实现；WRIST_R及掌部随冻结Rig整体运动。不新增手腕骨骼、不缩放网格或钢琴、不改变绑定、bone rest或拓扑。每指复用三段屈曲与根部spread的已有工程参数，20个指部变量；与6个整体变量联合求解。工程增量域：拇指[0..25,0..25,0..18,−35..35]度，长指[0..32,0..32,0..20,−25..25]度。它们是已用静态规划域，不是人体生理极限，也不能据此证明Rig的一切能力。

使用真实键位、真实指尖及Rig尺寸来求解；PianoPlayer估算的+6.046cm没有作为运动命令或约束输入。

## 88键和时间

原Stage C中全部88键各几何件与现有KEYBOARD_88_KEY_TABLE_R1真实顶点逐件核对，最大差 `0.00002218` mm。白键各可触键区、黑键高度/横向窄面、press pivot/axis及真实Action均读取，关键键位详情保存在RIG_PREFLIGHT.json/key_rows。没有重建或缩放钢琴。

原MIDIanna-magdalena-04.mid与正式PERFORMANCE_TIMELINE逐音绑定，音高、velocity、channel、on/off tick及源秒数不变。模型规划结果也不改。Blender沿用原展示时钟：T_PRESENT=T_MUSIC+0.35，FRAME=1+60×T_PRESENT；0.35没有并入MIDI音乐时间。

从原琴键Action采样453个时间点，存KEY_ACTION_SAMPLES.npz；连续求解读取这些真实角度，烘焙时原琴键Action仍原样保留，没有用新动作替代琴键语义。接触/释放必须面对既有键面运动。

## 可达性预检与限制

先做9个相邻事件初始化姿态，共919.493秒CPU求解，低内存；未安装新依赖或训练。当前指尖FK误差0.004—0.494mm，说明关键触点并非简单不可达。但真实皮肤初检已经出现闲置键侵入和中/无名指互穿，所以骨点可达不等于动作合格。

Blender自带Python无法使用旧Python3.12的SciPy扩展，因此Blender只提取原FK函数并做几何/烘焙；SciPy数值求解在已存在Python3.12环境运行，没有重装环境。首次导入错误日志保留。

后续仅尝试一次真实事件窗口联合轨迹，未进行逐根手指后修补。实际网格最终仍失败，根因指向现有规划约束不足；本轮没有证据证明冻结Rig或C01在所有可能控制策略下绝对不可行。
