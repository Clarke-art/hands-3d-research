# FIRST_WEB_DEFORMATION_ARCHITECTURE_REBUILD_ASSESSMENT_R1

**RECOMMENDED_ROUTE = NONE_OF_THREE**。三条架构各做一份独立 DESIGN_ONLY POC，均未通过 F130 的显著改善门槛，因此按本轮指令停止各路线。完整 7 秒、F31 和六个旧姿态 regression 未执行，不把未知写成通过。四项 Human 审核均未填写。当前结论是没有路线已证明值得正式 rebuild，不是三类架构永远不可行。

三份有界 POC 均未显著解决 F130 主 blocker，A 还让 F61 出现更明显浅沟；没有路线满足进入完整动作/旧姿态回归的前置门槛，因此当前不支持沿任一路线启动正式 rebuild。此选择限定于本轮证据，不宣称三类架构在所有设计下均不可能。

冻结基线 SHA256 `4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2` 未改变。DQS route 根据本次 Human Q1=NO/Q2=NO/Q3=YES/Q4=NO 正式拒绝。没有复用失败 weight2 / real-motion corrective candidate。每份 POC 从 frozen baseline 独立加载，再追加原 `PIANOVAM_PHYSICAL_RIGHT_AXIS_CORRECTED_R1`，原 Action payload hash 均逐项相同。同一 sample、mapping iteration 2、smoothing、421 observations、11.5–18.5 秒保持不变。仅生成 ZERO/F130/F76/F205/F61 同视角 screen。

当前局部网格：149 节点、120 个完全位于区域中的 quad；整个 mesh 3298 面也是 quad，选区节点 global valence 全为 4。不能把这次失败归因为三角面或高 valence pole。F130 的多个可见角折沿相邻桥面网格带形成；读数与 wire overlay 仅作为布局背景，不做 strain/normal-dot/crossing census。代表折线附近边：416–2033、2033–3145、3145–1565、1565–415、415–1677、1677–526。投影线图会显示选区背面/遮挡连接，需和普通实体视图一起读；没有以它证明隐藏几何情况。原/变形 edge vectors、面连接、valence 保存在 CURRENT_FIRST_WEB_TOPOLOGY_AUDIT_R1.json。

|路线|本次 POC|F130|F76/F205|停止原因|
|---|---|---|---|---|
|A local retopology|120 quad 细化，增加387点；83个内部旧点做一次有界切向重新分布并投影回原表面；已有 weights 简单插值|上部稍顺，下部深阶梯仍在|部分顺滑，尖峰/凹沟保留|未显著解决主 blocker，F61新增/加重浅横沟|
|B helper bone|1个 INTERNAL_FIRST_WEB_BRIDGE_R1；两个既有 skin transforms 的中点锚点 + quaternion slerp，转入原 wrist parent；局部最大 helper weight 0.4134|主要深折基本不变|原凹口/尖折保留|主要 blocker 未改善；按立即停止门槛没有试第二个 helper|
|C local cage|一种方法：3×3×3 Lattice，位于原 LBS Armature 后；既有关节四元数差驱动有界2mm控制场，只影响局部mask|实际改变很小，深折不变|原 blocker 保留|没有有意义改善，不尝试其他 cage 或调整场|

A 是局部空间分布/细化的架构探针，不是完成的美术 retopo。已有相对 corrective delta 在旧节点保持，在新增节点按原场插值，driver 表达式和目标完全保留；没有 sculpt 新 corrective、没有修改源批准资产。由于新 topology，候选 Key 数组尺寸会改变，不能声称候选 corrective 的数组逐字节完全相同。A 的边界一圈相邻 faces 可能变为 n-gon，正式版本若获授权还需边界拓扑/UV整理；本轮不做。域外原节点坐标和实际非零 weights 完全一致；重建 datablock 省略部分零值 sparse memberships，不改变数值影响。

B 现有21教学骨骼 names/rest/parents/inherit及原动作完全保留。内部 helper 不需要 mocap channel，不作为教学关节。421 组 helper 变换由固定矩阵混合公式派生，存成单独 helper-only NLA Action；这只保证本段 clip 的 POC 可重放，未来一般动作需运行同一小公式，不能把 POC 烘焙当成泛化验证。保存后的四个 frame helper 矩阵与公式最大绝对差 2.38418579e-07。没有额外 helper tuning 或权重刷调。

C 保持原 mesh、原 bone weights、原 corrective/driver。只加一个 lattice modifier 和非骨骼 local mask group。选择 lattice 是因为局部有界体积位移、无绑定和仿真；没有再实现 Mesh Deform / Surface Deform。实际控制点 lattice 定义域与 object scale 使其空间覆盖大于局部mask；影响顶点范围仍仅限原 first-web 选区。激活量直接使用 index/thumb 不同 local frame 的四元数差，这是弱 articulation proxy，不把它当解剖测量或复杂 solver。F130 实际 mesh 最大变化 0.1468 mm，driver invalid=0，因此确有求值但未解决深折。此阴性结果仅针对该有界字段，不足以否定所有 cage 设计。

ZERO 四个普通视图：palmar full/thenar close/dorsal full/first-web close，三路线初判轮廓可接受。A 原节点最大变化 0.1694mm；B 0.00012mm 浮点量级；C 0mm。所有 screen NaN/Inf=0、collapsed face=0、degenerate edge=0、恢复各自ZERO=PASS；普通可见检查 gross tearing=0、gross penetration=0，残留虎口 fold 本身仍是 blocker。以上仅覆盖 ZERO 和四选中帧，不是完整421点安全验收，不证明 hidden intersections。未跑 Stage6/R3/true-cap/2127 edges/normal-dot 或其他复杂研究。

统一产品工程比较：

|维度|A|B|C|
|---|---|---|---|
|F130修复能力|PARTIAL：上部平顺，深阶梯仍在|FAIL：主要深折保留|FAIL：无有意义改善|
|F76/F205泛化|PARTIAL：部分平顺，凹沟尖峰仍在|FAIL：原 blocker 保留|FAIL：原 blocker 保留|
|完整7秒稳定性|NOT_TESTED：关键帧未过门槛|NOT_TESTED：关键帧未过门槛|NOT_TESTED：关键帧未过门槛|
|ZERO外形保持|PRELIM_PASS：0.1694 mm 原顶点最大差|PRELIM_PASS：0.00012 mm 浮点差|PRELIM_PASS：0 mm|
|六旧姿态regression|NOT_TESTED：关键帧未过门槛|NOT_TESTED：关键帧未过门槛|NOT_TESTED：关键帧未过门槛|
|新bulge/flap或可见回退|F61 浅沟更明显；残留 flap|残留 flap，upper fold略尖|没有明显新 bulge；残留 flap|
|维护复杂度|MEDIUM：UV/旧 corrective 转移和边界整理|LOW–MEDIUM：一个内部骨骼和固定矩阵混合|HIGH：后置 cage 与 Web 表达一致性|
|motion retarget兼容|HIGH：21关节及原 Action不变|HIGH：内部helper从原关节派生|MEDIUM：需稳定的手部坐标/控制器定义|
|左手镜像难度|MEDIUM：局部流线、UV和形态审核|LOW–MEDIUM：镜像锚点/rest矩阵|MEDIUM–HIGH：cage坐标和位移方向重标定|
|Three.js/Web实现难度|LOW：仍为普通 bone+morph mesh|LOW–MEDIUM：多一个骨骼，运行时矩阵派生或 helper 曲线烘焙|HIGH：Blender lattice无法直接当标准bone+morph导入；需证明转换或额外后置deformation实现|
|运行时性能|LOW增量：387局部顶点；未benchmark|LOW增量：1个骨骼和两个矩阵的简单混合；未benchmark|MEDIUM–HIGH工程负担：局部cage插值或转译；未benchmark|
|未来钢琴动作鲁棒性|UNPROVEN：当前POC不足|UNPROVEN：固定平均桥接不能保证更广动作|UNPROVEN：当前场与激活代理不足|

Web 结论为工程评估，未做导出或 benchmark。Three.js 原生 SkinnedMesh 支持 skeleton 与 skin indices/weights，Animation System 支持 bone/morph tracks，因此 A/B 可继续保留 bone+morph 形式；B 的 Blender 派生关系需要转成运行时小公式或仅helper烘焙曲线，不能假设 driver/constraint 会自动被 Web 导入。[SkinnedMesh 官方文档](https://threejs.org/docs/pages/SkinnedMesh.html)、[Animation System 官方文档](https://threejs.org/manual/pages/animation-system.html)。C 的后置 lattice 场超出这里使用的标准 bone+morph 表达，需证明离线转换后的语义等价或自定义后置层；不能仅因为 Blender 有效就认为产品可部署。Lattice 的 vertex group 限域机制参考 [Blender 官方文档](https://docs.blender.org/UATEST/manual/en/dev/modeling/modifiers/deform/lattice.html)。这是路线成本推断，未执行 Web 产品验证。

再打开保护验证已确认：所有原21骨骼 rest/inherit 与材料保持；B/C approved corrective 内容完全一致；A 保留并插值同一 approved 相对场、driver 完全一致；原 Action hash 一致；域外原 Basis/有效weights一致；源7个受保护文件哈希不变。保存 ZERO 时原 Action 被显式 retained（fake user）；序列化修正仅保留Action，没有改变 POC 设计。

交付 review.html、三份 POC blend、4条件×12=48张 matched renders、局部 topology/线图、各路线结果、12维成本比较和脚本。没有路线进入完整motion，所以不交付伪造或沿用旧clip的 POC视频；旧六姿态也明确 NOT_RUN_KEYFRAME_GATE_FAILED。被冻结的六姿态 Human批准仍属于原baseline，未重新授予POC。

Human 只需四题：

1. 三条路线中哪一条 first-web 外观最好？A / B / C / NONE
2. 该路线是否已经证明值得正式重建？YES / NO
3. 是否保持 Official L1 整体手型与旧姿态可接受？YES / NO（POC仅ZERO已检查，旧姿态未过门槛而未执行，不能视为已证明）
4. 是否同意下一阶段只沿推荐路线实施正式 rebuild？YES / NO

STOP — HUMAN REVIEW。正式 rebuild / production promotion / 左手 / Web export 均 NO。指尖继续 DEFERRED。不新增路线或继续局部patch。
