# 原始 source dorsal MCP lineage 与局部形状转移可行性 R1

**PASS_LOCAL_DONOR_SHAPE_TRANSFER_FEASIBLE — STOP — HUMAN REVIEW。**

官方 base / L1 与 Stage2 在同一物理区域有自然的指间谷，但没有 Human 指出的尖锐 shelf / 折叠。第一处明确缺陷出现在 Stage4A `CON1_RING_MCP@-1mm` 的 `insert_loop` 平面投影。官方 L1 可作为 shape donor。保存并独立重读的临时探针保留当前拓扑及保护数据，结构可行性通过；尚未获得 Human 视觉批准，未应用生产。

## Q1–Q3

| 问题 | 证据结论 |
|---|---|
| 官方原模型已有这个坑吗？ | 没有同样的尖锐折叠；原本的自然谷仍存在。请查看同机位 source-native / flat 五阶段图及原始 section。 |
| 首次在哪里引入？ | 官方 base → 官方 L1 → Stage2 均未出现该折叠。Stage4A 烘焙 L1、CON9 旋转后仍干净；首个 ring MCP 切环的平面投影立即出现锐折。 |
| 可保留当前工程 topology 只恢复 source shape 吗？ | 可行。54 个顶点根据 donor 父边 ancestry 恢复，经原有 frozen RSSF 坐标变换转入当前表面；临时文件的3416/6828/3414、native face cycles、UV、材质、weights、bones/joints 完全保留。 |

## 真实 lineage

Stage2 不是已应用 base 或 L1 的猜测选择：它保留官方831/1649/820 cage 与启用但未应用的官方 Multires L1。实测 source/Stage2 的 cage 坐标、边、faces、UV 完全相等；其真实 evaluated L1（3300/6596/3298）也完全相等。receipt 两个源文件 SHA256 均重新验证。

Stage4A 将真实官方 L1 烘焙，执行 mesh-data Rx180°，四次 CON1 边环 subdivision + plane projection，再作 CON3 pole 邻域处理，得到3364/6724/3362 R2_BASE。R2 CMC 工程后3416/6828/3414，Human ROI 的52顶点与36 native faces 精确保持；Stage4B RSSF 烘焙后交给 Stage4C / 当前 R2。`SOURCE_GEOMETRY_LINEAGE_R1.json` 提供实际 modifiers、counts、hashes 与构建脚本证据。

## 物理 ROI 与首次 operation

没有跨阶段套用 vertex ID。官方 L1 的每个 oriented 子 face cycle 都与 cage face/corner subdivision graph 核对。当前955追到官方 base79–80边的 L1 子顶点；新增工程点由历史实际 split 父边及 interpolation 权重追溯。R2_BASE 回放仅在 RAM 中执行原操作，剔除历史 SAVE 段；最终 local coordinates 与 native face cycles 和 frozen 文件精确相同。

首步 `CON1_RING_MCP@-1mm` 从3300/6596/3298变到3316/6628/3314，新增16顶点。新点原先在 donor 边上，随后沿 finger axis 投影到 deformation-loop plane，最大4.520mm。该操作没有 donor surface reprojection / preservation constraint。matched patch 最大二面角由60.157°变为169.833°；`-7mm`后177.904°。这是 comparative diagnostic，不是 anatomy threshold。`TRACE_0/TRACE_1`图可直接检查第一步前后。

CON3 后续 pole738两次位移及 smooth factor0.5 另改变邻域，但第一折叠在它之前已存在。`stage4a_engineer.py`的 `insert_loop` AST 与实际 R2_BASE producer相同；审计没有只凭文件名归因。

## Donor、scope 与临时探针

选择 actual official L1：它是 Stage4A 真实最近未工程化祖先，视觉表面正常，correspondence 确定。Stage2 evaluated L1 是精确等价 donor；coarse base 并非真实烘焙输入。仅恢复 shape，不剪 faces、不删除 loops、不换 topology。

scope 由实际 donor/current deviation、Human core 连通域和共享 L1 父边 ancestry 闭合得到54顶点，非15/52/111预设。每顶点理由、父权重和前后坐标在临时 JSON 的 `write_set`。最大位移4.637473mm；无需 boundary fairing。未连接的 DIP / CMC 操作保持不动。

初始38点 scope 漏掉共享相同 donor edges 的第一圈，205/207已有 contact 增长0.002749mm，严格 FAIL。其失败证据保留。依据真实 ancestry 补齐第一圈后得到54点探针，没有调整目标曲面或运行 optimizer。

冻结 RSSF 的历史 mathutils forward reconstruction 与保存 Stage4B local coordinates 精确相等。只是恢复已有坐标 correspondence，不修改 RSSF authority。double线性公式与原float32逐步累积存在0.000318mm最大数值差，实际探针 anchoring当前点并保存后重读；结构 gate 检查重读后的真实存储坐标。

## 结构与视觉可行性

| Gate | 结果 |
|---|---|
| native V/E/F / cycles / incidence | 完全相同 |
| UV / materials / smoothing / weights / bones / joints | 保存重读后与来源 payload 完全相同 |
| 新非邻接 exact intersection / off-shared crossing / 非法 coplanar overlap | 0 / 0 / 0 |
| 新 structural bow-tie / self-intersection / degenerate / face reversal | 0 / 0 / 0 / 0 |
| 新 true contact component / 既有恶化 / feature expansion | 0 / 0 / 0 |
| scope 内 source-existing true contact components | 12 → 0；远端未改变，不宣称全手无 contact |
| declared linear path 最小 native fan area | 0.021731568mm² > numerical area tolerance；该检查不等于完整 continuous collision certificate |
| ROI 最大局部二面角 | 178.228° → 61.400° |
| 新 obtuse boundary edges | 0 |

gate 使用已 reconciliation 的 exact rational finite-feature predicates，并扣除真实共享 simplex。没有恢复 absolute projected bowtie zero。旧 contact 可以消失，不允许新增、扩张或恶化；完整 changed fan scope 对全手 unchanged mesh 检查。所有未移动 coordinates 精确相等。

已检查 matched close / grazing / side：原尖锐折叠不再出现，自然 source 谷保留；未观察到新鼓包或边界锐折。整体 arch 除54点外逐坐标相同。原始 Human camera 640×800、full dorsal、wire、silhouette、0/60/120实际三角面切线均在 review。视觉结论仍待 Human；metrics绝不代替 anatomy批准。

## 整手替换 vs 局部恢复

**不推荐整手替换；推荐局部 donor shape transfer amendment design。** 原模型可作为另一个新资产，不能直接作为当前 production replacement。替换会重置 MCP/CMC、mesh IDs/UV/nail semantics，要求重新 binding/weights、bone compatibility、fresh R3、cap37、true-cap及 Stage6证据。局部探针保留这些数据和authority文件；未来正式 shape amendment 仍需重新验证 geometry-dependent derived authority 与下游资格，不能沿用旧通过结论。

surface-preserving Stage4 operation rebuild 原理上可设计，但未执行；重跑可能改变 geometry-dependent seed selection、顺序和 downstream IDs。当前 fixed-topology 局部恢复是更明确的范围。

## 保护与停止

官方、Stage2、所有 historical/frozen assets 与 production文件按全项目SHA256前后核验；新输出只在本轮audit目录。详见 `PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json`。未执行 formal amendment、Stage5 propagation、true-cap recompute、targeted deformation、Full42、Stage6B、retopo或正式promotion。

Stage6A继续 `FAIL_CLOSED_FULL_STAGE6A_REQUALIFICATION`，9个unapproved severe crossings独立存在；未运行也未裁决 incidental crossing effect。探针明确 **NOT_PRODUCTION / NOT_APPROVED**。

NEXT只记录 `LOCAL_DONOR_SHAPE_TRANSFER_AMENDMENT_DESIGN_R1`，未执行。**STOP — HUMAN REVIEW**。

## 最终字段

| 字段 | 结果 |
|---|---|
| `ORIGINAL_SOURCE_DORSAL_MCP_LINEAGE_AND_PATCH_TRANSFER_FEASIBILITY_R1` | PASS_LOCAL_DONOR_SHAPE_TRANSFER_FEASIBLE |
| `OFFICIAL_BASE_DENT_VISIBLE` | NO_TARGET_SHARP_FOLD_NATURAL_VALLEY_PRESENT |
| `OFFICIAL_L1_DENT_VISIBLE` | NO_TARGET_SHARP_FOLD_NATURAL_VALLEY_PRESENT |
| `STAGE2_BOOTSTRAP_DENT_VISIBLE` | NO_TARGET_SHARP_FOLD_NATURAL_VALLEY_PRESENT |
| `STAGE4A_R2_BASE_DENT_VISIBLE` | YES |
| `FIRST_CONFIRMED_CLEAN_STAGE` | OFFICIAL_BASE |
| `LAST_CONFIRMED_CLEAN_STAGE` | STAGE4A_L1_NORMALIZED_BEFORE_CON1 |
| `FIRST_CONFIRMED_DEFECT_STAGE` | CON1_RING_MCP@-1mm_RAM_TRACE / STAGE4A_R2_BASE_FIRST_FROZEN_FILE |
| `FIRST_DEFECT_TRANSITION` | STAGE4A_CON1_RING_MCP@-1mm_EDGE_SUBDIVISION_THEN_PLANE_PROJECTION |
| `FIRST_DEFECT_OPERATION_IDENTIFIED` | YES |
| `FIRST_DEFECT_OPERATION` | stage4a_r2_base.py::insert_loop / CON1_RING_MCP@-1mm plane projection |
| `DONOR_SOURCE_AVAILABLE` | YES |
| `RECOMMENDED_DONOR_SOURCE` | OFFICIAL_MULTIRES_L1_EQUIVALENT_TO_STAGE2_EVALUATED_L1 |
| `DONOR_CORRESPONDENCE_METHOD` | EXACT_SUBDIVISION_GRAPH_ANCESTRY + HISTORICAL_SPLIT_EDGE_WEIGHTS + FROZEN_RSSF_LINEAR_TRANSFORM |
| `CURRENT_TOPOLOGY_PRESERVED_IN_TRANSFER` | YES |
| `TRANSFER_PROBE_CREATED` | YES_NOT_PRODUCTION_NOT_APPROVED |
| `TRANSFER_STRUCTURAL_GATE` | PASS |
| `TRANSFER_VISIBLE_DENT_STATUS` | TARGET_SHARP_FOLD_ABSENT_IN_INSPECTED_MATCHED_VIEWS_HUMAN_REVIEW_PENDING |
| `TRANSFER_NEW_VISIBLE_DEFECT` | NONE_OBSERVED_HUMAN_REVIEW_PENDING |
| `FULL_ORIGINAL_MODEL_REPLACEMENT_FEASIBLE` | NEW_ASSET_YES_DROP_IN_NO |
| `FULL_REPLACEMENT_RECOMMENDED` | NO |
| `LOCAL_DONOR_SHAPE_TRANSFER_FEASIBLE` | YES_DESIGN_ONLY_STATIC |
| `LOCAL_DONOR_TRANSFER_RECOMMENDED` | YES |
| `STAGE4_OPERATION_REBUILD_FEASIBLE` | YES_IN_PRINCIPLE_NOT_EXECUTED |
| `TOPOLOGY_CHANGE_REQUIRED` | NO_FOR_THIS_PROBE |
| `RET0PO_REQUIRED` | NO |
| `PRODUCTION_DRIFT` | 0 |
| `FULL_STAGE6A_REQUALIFICATION_R1` | FAIL_CLOSED_FULL_STAGE6A_REQUALIFICATION |
| `UNAPPROVED_SEVERE_CROSSINGS` | 9 |
| `NEXT` | LOCAL_DONOR_SHAPE_TRANSFER_AMENDMENT_DESIGN_R1 |
| `NEXT_EXECUTED` | False |
| `STOP` | STOP — HUMAN REVIEW |
| `human_approval` | NOT_APPROVED |
