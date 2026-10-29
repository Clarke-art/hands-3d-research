# 与现有Blender资产的兼容性分析

本轮仅读取必要接口文件与数据结构，没有启动Blender、修改Action、解码MANO资产或生成候选。**可以保留现有Rig、Mesh、权重、88键几何与已批准静态姿态**；可接收外部轨迹不代表无需重定向。

## 已有接口

`audits/midi_driven_dual_hand_piano_performance_poc_r1/performance_core.py` 的 `SETUPS`、`joint_mats`、`fk`、`bounds`：每指三个可驱动关节加MCP横展的4个工程坐标；每手五指。非拇指MCP/PIP/DIP flex范围0–75/95/65°，横展±28°；拇指命名是CMC/MCP/IP而非直接照搬MANO三个名称。真实骨架/轴来自 `RIG_CANONICAL_PROBE_R1.json`。

|21点语义|现有骨架接口|
|---|---|
|wrist|WRIST_R/WRIST_L及其已有root对象；须区分global/root运动与骨骼local旋转|
|食/中/无名/小指MCP/PIP/DIP/tip|对应 DIGIT_MCP/PIP/DIP/TIP_R或_L|
|拇指三个关节与tip|THUMB_CMC/MCP/IP/TIP_R或_L；按语义匹配，不能按数组序号盲拷|
|掌部朝向|由腕及MCP基部共同约束；21点不包含完整掌面或前臂，需要从本Rig几何恢复|

已有动作以 `pose.bones[...].rotation_quaternion` 的骨架local basis烘焙，root另有轨迹。现有事件表包含hand、finger、midi_note、key_index、NOTE_ON/OFF，key_index=MIDI−21。钢琴X沿键盘、Y沿键深、Z向上，白键和F♯5黑键在未按下时键面高度差约15.444mm。源表有真实playable surface分片、键轴与press angle，接触目标必须使用随原Action运动的键面。

## 三种输出的接入难度

|输出|可以怎样用|必要转换与风险|
|---|---|---|
|Tipiano 每手21×3点|作为腕/指尖/中间关节的目标轨迹，拟合现有骨骼|不是现成local rotation；缺少轴向twist信息。原论文的MANO拟合也不是本Rig动作转换器。当前缺源码/权重|
|PianoMotion MANO全局姿态+45维轴角|先恢复语义关节/参考旋转，再转换到本Rig或拟合|[输出渲染代码](https://github.com/agnJason/PianoMotion10M/blob/86539e5a16d10ba462005f1f2bd9d72459ac2000/datasets/show.py#L91)在相机/渲染坐标内，左手镜像右模型。不能直接把45个数字填入本Rig旋转或手工改符号|
|FürElise joints与global_rotation|短段参考轨迹可绕开运行MANO网格解码，作为运动先验|数据本身仍受NC许可；21点无完整twist。卡片pose维度/编码有待实际小包核查，优先使用joints而不是猜pose编码|
|FürElise物理策略输出|需要先取得公开实现，再把控制结果转换成现有动画|论文仿真手17 links/27DoF与本Rig不一致；不是直接可接骨架API，现阶段不建议此路线|

## 坐标、旋转与骨长：建议的后续转换合同

以下是**工程设计建议，不是已实现的代码**。

1. 先以几何语义确认单位、轴方向、左右手标识、关节顺序与源键盘尺度，至少用多个键中心及键面标定，禁止凭相机图猜世界坐标。
2. 使用 `p_target = s R p_source + t`，R必须是合法旋转，左右镜像单独记录。Tipiano v1声明X朝演奏者、Y沿键盘、Z为高度；在方向一致的条件下，候选映射可为 `(X_t,Y_t,Z_t)=(Y_s,-X_s,Z_s)`，但必须用实数据确认正向，不能只交换X/Y造成反射。
3. 重定向保留目标Rig的rest骨长和轴，源人手比例不能改变冻结Mesh。单段骨方向能给bend方向，不能唯一给twist；补充掌面朝向、上一帧旋转和当前工程关节域，再得到local basis quaternion。
4. 如果用源旋转，先区分global与relative：`R_child_rel = R_parent_global^-1 R_child_global`，再进行rest轴变换；不能把世界旋转直接作为Blender matrix_basis。MCP多个自由度也须投影到现有工程域。
5. 原NOTE_ON/OFF仍是时间权威。59.94fps与30fps轨迹按真实时间重采样至60/120Hz；不得按相同帧序号直接对齐。保持0.35s视频lead和原琴键/音频Action，用事件边界约束插值，尤其NOTE_OFF后的释放不能继续按持键处理。

## 正确触键、穿指与穿键会不会重新出现？

会有重新出现的风险。来源可包括骨长比例、pad与关节tip的差异、MANO世界系到本Rig local basis转换、左右反射、关节域投影、59.94→60fps插值及滤波。源21点合法也不保证目标skin无相交；原模型中指尖刚好触键，也可能在本Rig中成为悬空或指侧穿黑键。

因此未来小实验应以**现有实际skin、运动键面和原俯视相机**验收，测目标键、pad接触与独立指形，并保留侧斜检查。学习先验应指导整手布局/关节协同，精确MIDI接触约束负责功能；避免最后用大幅局部修正把学到的掌腕协调破坏掉。这是研究推论，不是任何项目已有的无碰撞保证。

## 动态root与冻结资产不是同一件事

保留冻结骨架/网格/静态姿态可以同时在**未来另行授权的派生动作**中验证短段root/腕轨迹变化。上一轮固定root的限制不应被无条件带入新路线，因为本次研究目的正是判断整手协同是否需要改变。不过目前批准的root和左手Action仍为参考资产，本轮无任何变更。

专业指法DESIGN_PROVISIONAL。新实验首先需要教师确认指定3–4–3–4–5是否适合此速度与上下文；本报告不修改指法，也不承诺可以在固定root下完成。

本机Windows、RTX3060 12GiB、系统Python3.12.1已只读核实；推理依赖应将来隔离，不能装进现有Blender运行时。本轮没有环境安装、权重下载或原型接入。

STOP — HUMAN REVIEW。
