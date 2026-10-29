# OFFICIAL_L1_PRODUCT_REBASE_FEASIBILITY_R1

**FAIL_PRODUCT_REBASE_FEASIBILITY — STOP — HUMAN REVIEW**

Official L1 的正常静态手型保留，但本次拟合与权重转移没有得到全部自然的代表动作。最小肉眼 blocker 是虎口上缘、连接食指根处的尖折 / 片状硬台阶，同一问题出现在 INDEX_MCP_45、CMC_OPP_30、FULL_OPP_L2 和 FULL_OPP_L3。一次局部平滑后仍存在，故停止本轮调整。此结论限定于本次 candidate，不能推断 Official L1 路线本身不可行。

| 最终字段 | 结果 |
| --- | --- |
| SOURCE_MESH | "Blender Human Base Meshes v1.4.1 / Hand  - Realistic / Official Multires L1" |
| SOURCE_VERTEX_FACE_COUNT | {"vertices": 3300, "edges": 6596, "faces": 3298} |
| RIG_SOURCE | {"path": "production_spec/stage5_production_rig/human_thumb_kinematic_authority_correction_r1/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_THUMB_KINEMATIC_CORRECTED_R1.blend", "sha256": "5d5f86bb59135715a77515468c2b76fe81e2a44e2e8c5d6c17fcc3d56d2147fe"} |
| BONE_COUNT | 21 |
| ARMATURE_FIT_STATUS | "COMPLETED_SOURCE_SHAPE_PRESERVED_DYNAMIC_FIRST_WEB_BLOCKER" |
| WEIGHT_TRANSFER_METHOD | "Nearest surface + barycentric interpolation on an unsaved pose-registered R2 donor proxy; normalize 16 deform influences; no TIP weights" |
| LOCAL_WEIGHT_TUNING_VERTEX_COUNT | 173 |
| ZERO_VISUAL_STATUS | "PASS_CODEX_PRELIMINARY" |
| FOUR_FINGER_FLEX_STATUS | "FAIL_INDEX_FIRST_WEB_HARD_FOLD; MIDDLE_RING_LITTLE_PASS_CODEX_PRELIMINARY" |
| THUMB_FLEX_STATUS | "PASS_CODEX_PRELIMINARY" |
| CMC_OPP_30_STATUS | "FAIL_VISIBLE_UPPER_FIRST_WEB_HARD_FOLD" |
| FULL_OPP_L1_STATUS | "PASS_CODEX_PRELIMINARY" |
| FULL_OPP_L2_STATUS | "FAIL_VISIBLE_UPPER_FIRST_WEB_HARD_FOLD" |
| FULL_OPP_L3_STATUS | "FAIL_VISIBLE_UPPER_FIRST_WEB_HARD_FOLD" |
| VISIBLE_PRODUCT_BLOCKER_COUNT | 1 |
| MACHINE_SAFETY | "PASS_MINIMUM_NUMERICAL_AND_GROSS_VISIBLE_SCREEN" |
| SOURCE_SHAPE_PRESERVED | "YES" |
| PRODUCTION_PROMOTION | "NO" |
| VERDICT | "FAIL_PRODUCT_REBASE_FEASIBILITY" |

## 候选与边界

候选：[RIGHT_HAND_OFFICIAL_L1_PRODUCT_REBASE_CANDIDATE_R1.blend](../../../artifacts/472907192f7539e70aea.md)，SHA256 `9e8b29875fc6c215ef1e0fce4f582774f10b21596835d03763edb771443b11ec`。保存姿态为 ZERO。NOT_PRODUCTION / HUMAN_APPROVAL_PENDING / DO_NOT_PROMOTE。

产品 mesh 直接来自 Official donor 实际 Multires L1 求值，V3300 / E6596 / F3298，原始局部坐标和面序列精确保留，UV 与材质来自同一 source 求值。只做整体刚性显示配准；没有将 engineering palm、旧 patch 或 topology 复制回 source，也没有重拓扑。source 的 thenar 主体、虎口开口、掌宽和背侧表面在六组静态同机位对比中保持原样。

21 骨骼的名字、父子层级、连接关系、16 deform / 5 non-deform TIP 结构来自 corrected rig lineage。允许的空间适配使用已有表面对应关系的局部仿射拟合映射 head / tail，并映射 roll 方向；局部 X 屈曲和 corrected thumb chain 的动作语义继续复用。连接骨骼共用端点。空间拟合完成不等于全部动作验收通过。

R2 donor 正权重 hash `1d9437a10354cdd98a2b5cb5e43be8cfabc519e232235483a615e76898129f55` 经 nearest surface + face barycentric interpolation 转移，在临时配准 donor proxy 上查找，归一化到 16 组。该 proxy 不进入产品 mesh。历史对应关系覆盖 3341 个工程顶点，其余 75 个只在临时 proxy 中作邻域空间插值。新 topology 使用新权重 payload，未强求旧 hash。

仅进行一次局部权重平滑，173 个 Official L1 顶点参与，只改 WRIST / THUMB_CMC / MCP / IP 四列，其他权重列、源几何、UV、骨架 rest 和 modifier 不变。保留初始转移候选及初始动作证据。没有继续扩大修复范围。

## 可见结果与最低检查

六个静态对比通过 Codex 初步观察，Human 仍待评审。MIDDLE/RING/LITTLE MCP45、THUMB MCP/IP45、FULL_OPP_L1 的正常 crease、软压缩和轻微分面可接受。INDEX MCP45 的根部附近存在同类虎口尖折；CMC30 最明显，L2 与 L3 重复，thenar 主体仍保留，没有整块缺失或粗大撕裂。

严格只跑授权的 10 个代表 case，复用 Stage6A -45° local X 与 Stage6B 原 opposition vector 和 L1/L2/L3 定义。每个 case 有四个静态视角和六帧 ZERO→该 case 的 quaternion slerp 循环预览；预览中间帧用于人眼观看，不扩展资格矩阵。最终展示统一采用普通灰色 studio shading、相同冻结相机和无 cast shadow 投影，避免投影斑块被误认作表面凹陷，没有删面或藏面。

10/10 的 NaN/Inf、collapsed face、degenerate edge、gross severe stretch 检查为零；每次动作后 21 骨骼恢复 ZERO，最大恢复误差 0 mm。普通图像观察未见粗大 tearing / penetration。这些最低检查 PASS 不能消除尖折产品 blocker，也不表示完成了隐藏交叉检查。

原始 source 与绑定后的 ZERO 世界求值最大浮点差为 0.000482062677 mm（约 0.482 微米），原生局部几何精确相同。ZERO restore 以当前绑定 ZERO 为基准，误差为零，两者不是同一比较。

未进行 hidden crossing、normal-dot、R3、true-cap、逐点 anatomy proof 或新动作轴/vector 搜索；没有替换 master、镜像左手、retarget 或 Web export。正式 Stage5B、Official donor、corrected rig 均经 SHA256 复核保持原样。

## Human review

[打开 review.html](../../../../examples/historical/audits/official_l1_product_rebase_feasibility_r1/review.html)。四部分：source vs ZERO 六视图、四指 MCP45、thumb flexion、opposition。Q1/Q2/Q3 = ACCEPT/REJECT，Q4 = NO/YES；不预填，人类结果可下载本地 JSON。此页面只是独立设计候选的评审材料，没有生产推广操作。

原始证据：[静态绑定](../../../artifacts/edf45f7f73f7b4b75186.md)、[10 个动作与恢复](../../../../examples/historical/audits/official_l1_product_rebase_feasibility_r1/REPRESENTATIVE_MOTION_EVIDENCE_R1.json)、[局部权重调整](../../../../examples/historical/audits/official_l1_product_rebase_feasibility_r1/LOCAL_VISIBLE_WEIGHT_TUNING_R1.json)、[可见结论](../../../../examples/historical/audits/official_l1_product_rebase_feasibility_r1/FINAL_VISIBLE_PRODUCT_SCREEN_R1.json)、[状态](../../../../examples/historical/audits/official_l1_product_rebase_feasibility_r1/OFFICIAL_L1_PRODUCT_REBASE_FEASIBILITY_R1_STATUS.json)。

浏览器核对完成：六个静态配对、40 个动作配对视图、10 个动作循环均载入正常，四个 Human 问题未预填。[页面核对记录](../../../../examples/historical/audits/official_l1_product_rebase_feasibility_r1/BROWSER_REVIEW_VERIFICATION_R1.json)。

[CMC_OPP_30 虎口上缘尖折与 ZERO 对比](../../../artifacts/b1ee2cae0b9e5a0b4a0a.md)

**PRODUCTION_PROMOTION = NO. STOP — HUMAN REVIEW.**
