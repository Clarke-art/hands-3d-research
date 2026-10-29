# NATURAL_PIANO_HAND_POSTURE_CONTRACT_R2

状态：**EVIDENCE_BOUNDED_PROVISIONAL_CONTRACT / STATIC_EXECUTION_GATE_NOT_MET**。最高原则 HUMAN_VISIBLE_PRODUCT_QUALITY_FIRST。来源代号见 [参考清单](REAL_PIANO_REFERENCE_MANIFEST_R2.md)。YES 建立约束表示证据、几何、假设和未知已有边界，**不表示姿态通过、人体生理校准或求解政策已可激活**。

## 1. LEFT_OCTAVE_POSTURE

- **REFERENCE_SUPPORTED**：S1 左手白键八度准备；S2 对侧白键八度前部触点建议；S5 第五指关节支持及避免向外扭手。只能转移定性原则。
- **GEOMETRY_DERIVED**：正式 D2–D3 键中心距 167.569 mm；内侧前部区域零面积点距下界 144.480 mm；L 静置 pad 空间距 153.007 mm。两者均不是最大自然跨度；内侧极限点也不是安全 pad 处方。
- **ENGINEERING_ASSUMPTION**：L1 小指触 D2、拇指准备 D3；L2 反向任务。两姿态共享相近掌腕布局，必须记录 root 位移/旋转、实际 pad 跨度与触点；不得通过任意迁移分别伪造八度成功。
- **UNKNOWN**：无碰撞自然八度是否可达；两端准备关系的允许 root 差异、三闲置指具体形态以及动态交替。未证实硬几何不可能。

## 2. RIGHT_FIVE_FINGER_POSTURE

- **REFERENCE_SUPPORTED**：S3 官方文字确认 1=D、2=E、3=F#、4=G、5=A。R1 白键照片只能提供有限一般曲度对比，不补成含 F# 的影像证据。
- **GEOMETRY_DERIVED**：D5–A5 中心距 95.754 mm；F#5 高于白键 15.444 mm，前端更靠后 49.421 mm。
- **ENGINEERING_ASSUMPTION**：R1 五指准备无需同时触键；R2 仅中指主动接触 F#5，其余指允许准备/放松。两状态使用一个共享整手变换，不把五个 pad 排成同高同深直线。
- **UNKNOWN**：F# 中指自然接触时各指与掌腕的可见关系。当前未取得可观看的黑键五指示范；这是本轮执行门槛的实质缺口。

## 3. RELAXED_IDLE_FINGERS

- **REFERENCE_SUPPORTED**：S1、S2 可见中间指形态各异；S1 中间 E 有演奏任务，不能推广成三闲置指标准。
- **GEOMETRY_DERIVED**：现有每指独立指链、同一 wrist/root 下的 21 骨架；没有可借用的生理耦合模型。
- **ENGINEERING_ASSUMPTION**：普通产品视角三闲置指保留不同程度弧度，避免统一钩爪、强制伸直、任意抬高与靠近邻键的异常准备。视觉否决优先于 marker 通过。
- **UNKNOWN**：左手 5/1 任务中三指唯一或精确曲度、关节角和被动耦合，不能从二维照片反演。

## 4. FINGERTIP_PAD_CONTACT

- **REFERENCE_SUPPORTED**：S1/S2 仅支持触点与键位的外观关系，不测压力或接触面积。
- **GEOMETRY_DERIVED**：沿用固定 distal frame/local_pad_point/mesh_vertex 与正式 88 键实际可奏面；垂直 3 mm、水平 2 mm 容差不变。目标点须在可奏区域内，容差不能将区域外的点升级为通过。
- **ENGINEERING_ASSUMPTION**：同时记录刚性 pad 和变形皮肤顶点/局部表面；显示皮肤悬浮或穿键时，即使 marker 合格也不能 PASS。禁止重定位 marker 以刷通过。
- **UNKNOWN**：皮肤压缩、完整 pad 有限面积与接触压力。3/2 mm 是项目工程容差，不是人体标准。

## 5. SHARED_PALM_POSITION

- **REFERENCE_SUPPORTED**：S1/S2 单只手承担多个指位；S3 五指任务需要共同掌部上下文。照片不提供可移植三维变换。
- **GEOMETRY_DERIVED**：现有骨架共同 wrist/root 可以平移和旋转整手；不能为各指设置独立手掌。
- **ENGINEERING_ASSUMPTION**：每姿态只有一个 root 变换，主动指、下一指准备、闲置指与掌底净空一起验收。L1/L2、R1/R2 的变换差异完整披露。
- **UNKNOWN**：本任务的可行共同掌位集合。分别触键不能证明八度或五指共同掌位自然。

## 6. WRIST_HEIGHT_AND_ORIENTATION

- **REFERENCE_SUPPORTED**：S5 支持腕部灵活与避免向外扭手；没有经核查的本任务侧面毫米高度。
- **GEOMETRY_DERIVED**：键盘 z 轴向上、白键静置面 z≈0；正式 wrist 网格与骨架可供独立净空测量。
- **ENGINEERING_ASSUMPTION**：只准整手 root XYZ、有界 yaw/pitch/roll 和现有骨骼旋转。局部异常扭转或抬高必须被侧斜视否决。
- **UNKNOWN**：人体或教师认可的高度/朝向范围；没有前臂、肘肩模型，不能认证整条手臂人体工学。本轮不编造角度区间。

## 7. PALM_KEYBOARD_CLEARANCE

- **REFERENCE_SUPPORTED**：S1/S2 隐藏掌底不可直接测量；S5 一般原则不能证明该网格净空。
- **GEOMETRY_DERIVED**：用冻结键体三角面及变形手网格检查掌、腕和相邻键；粗带分组来自 canonical y 区段，仅是工程区域，非解剖分割。
- **ENGINEERING_ASSUMPTION**：穿键、掌部压键、明显悬浮与邻键干扰为否决项；代理点/顶点盒筛查只能辅助，未进行全三角检查时必须保留检查范围限制。
- **UNKNOWN**：当前四姿态的净空数值（NOT_RUN），细小接触的有限面积定义。没有测量不得写零碰撞。

## 8. NATURAL_JOINT_BENDING

- **REFERENCE_SUPPORTED**：S5 第五指避免关节塌陷；S1/S2 定性形态比较。来源不支持精确 MCP/PIP/DIP/CMC 角度。
- **GEOMETRY_DERIVED**：正式两手均 21 骨、3300 顶点；长度、rest、weights、correctives/drivers 均冻结。
- **ENGINEERING_ASSUMPTION**：逐指评估屈曲和展开，不用统一角度处方；禁止为触点反关节、缩放、拉长、helper bone 或逐顶点形变。
- **UNKNOWN**：本模型可接受的数值旋转域；现有旧 bounds/prior 不是人体生理极限，不自动继承为新静态政策。

## 唯一求解政策的执行前要求

本轮 **NOT_RUN**，没有 IK 初始值、参数 sweep、多候选、动作或新 blend。上述合同建立可检验定性要求，但没有据未经观看影像填写数值关节范围。

若下一次授权补证后通过门槛，在任何求解之前锁定一套 DESIGN_ONLY 政策：每骨工程范围、root 与 wrist 边界、四任务触点区域/边缘余量、准备高度、闲置指 prior、损失项、确定性初始化、终止规则、碰撞方法与可接受两姿态 root 差异。所有数值明确标 ENGINEERING_ASSUMPTION，**不是人体生理极限**。只运行一次联合四姿态构建，不生成多套候选挑选。

静态通过最多 CANDIDATE_PASS_PENDING_HUMAN；无法证明动态过渡。任何失败先区分 REFERENCE_EVIDENCE_LIMIT、IK_SOLVER_FAILURE、POSTURE_CONSTRAINT_LIMIT、GEOMETRY_LIMIT，不因单个 IK 解失败要求修改正式资产。
