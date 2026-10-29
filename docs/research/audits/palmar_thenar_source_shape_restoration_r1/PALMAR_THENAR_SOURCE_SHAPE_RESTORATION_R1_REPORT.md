# PALMAR_THENAR_SOURCE_SHAPE_RESTORATION_R1

2026-10-06（Asia/Shanghai）。PRODUCT SHAPE REPAIR；HUMAN_VISIBLE_PRODUCT_QUALITY_FIRST。

## 结果与停止点

已创建并 clean-reopen 核对 **DESIGN_ONLY position-only candidate**，修改 **323 个局部顶点 = 136 个 core + 187 个 transition**。原正式资产未覆盖。

**ZERO 与 FULL_OPP_L1：CLEARLY_IMPROVED。FULL_OPP_L2 / L3：NEW_VISIBLE_PROBLEM。**

ZERO 的虎口下方斜面、大鱼际上缘和拇指根掌侧连接更饱满，保持原 first-web 开口和 crease。L1 的静态改善仍可见。L2/L3 在同一冻结权重下，虎口 floor 出现更突出的硬折角 / 局部压挤凹槽。因此本轮**不判 READY_FOR_HUMAN_APPROVAL，也不判 Stage6B final PASS**。最低 catastrophic 机器门通过不代表局部形变产品外观通过。

`ZERO_SHAPE_PASS = YES` 是 Codex 初步静态判断，最终 Human 尚未批准。`OPPOSITION_VOLUME_PRESERVATION_FAIL = YES` 指 L2/L3 的局部上缘 / floor 压挤外观；下部 thenar mass 仍在，不等于全块大鱼际消失，也未证明权重是唯一根因。

按用户第十三条停止逻辑，保留当前静态 candidate，不继续通过改静态 geometry 掩盖 pose 问题。`NEXT = TARGETED_THENAR_OPPOSITION_WEIGHT_TUNING_R1`，**仅记录，未执行**。**STOP — HUMAN REVIEW。**

## 输入与 candidate

- 正式输入：`production_spec/stage5_production_rig/geometry_propagation_after_palmar_donor_restoration_r1/RIGHT_HAND_STAGE5B_R2_DONOR_TRANSFER_PALMAR_ROOT_GEOMETRY_R1.blend`。
- 正式输入 SHA256：`90d3ebd1c1973f94020b66281781db481d5a366271a9d6aac6b921861e2b45aa`，前后仍是用户指定的 `90d3ebd1c1973f94020b66281781db481d5a366271a9d6aac6b921861e2b45aa`。
- 官方 donor：`references/licenses/blender_human_base_meshes/extracted/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend`，SHA256 `3c121505651140ceb4d69fd1d8923f7788ffadd81672f5be14845a5f2c75c137`。
- Candidate：[RIGHT_HAND_STAGE5B_PALMAR_THENAR_RESTORATION_CANDIDATE_R1.blend](../../../artifacts/b55f42073f03d7496327.md)，SHA256 `950d47f422f5c4b5eb604edefce0d6f4c542a90a395f522c3e9917ad362d12e8`。

Official Hand - Realistic 的 actual stored Multires L1 本轮只读求值，原生坐标与 faces 和既有已验证 snapshot 精确一致。采用已验证、与 Stage2 等价的 official L1；不替换整手、不转入 source topology。

## 局部 source-profile restoration

复用已验证 rigid display registration、historical current-to-base native identity 与 split-parent ancestry。以当前保留的 lower-thenar surface anchors 对 donor 作平移放置；donor 本身不改形状。提取 donor 相对当前的横向轮廓与掌侧饱满度分量，以同一局部 source profile field 连续转移到现有 engineering topology；保留当前 RSSF 轴向安排和上方 thumb shaft。

source profile field 的插值 support 为 9 mm；这只插值 donor-derived displacement 值，**没有平均 / fair 当前 mesh coordinates**，不是自由 smoothing 或 generic fairing。Generated CMC transition vertices 接受该同一场的连续延拓，未为它们编造 exact donor vertex-ID pairing。

选定 blend strength = 0.38，局部 compact footprint 与 smooth transition 仅覆盖 thenar / palmar thumb-root / lower first-web floor。它不扩展到整个 palm、wrist、四指掌侧或整手。更远区域原坐标保持精确不变。顶点 ID 及 donor parentage / field extension 记录于 [选定形状记录](../../../artifacts/b1d53a0513b157a43aed.md)。

这是一种由 source 轮廓和体积引导、适配 RSSF 的产品恢复，不是逐毫米复制原始中性 donor。没有进行 anatomy、根因、CMC-axis、retopo 或 topology-correspondence 研究。

## 少量视觉迭代

共三版内存静态预览。前两版在虎口基底引入硬折面，未保存成 blend，未进入 opposition smoke。第三版通过 donor profile field 插值、轴向保留与 distal transition 解决静态新折面，选为唯一正式 design candidate。Candidate blend 只保存一次，且在 ZERO；后续 pose 全部在内存，最后 RESET ZERO，未保存 posed blend。

达到静态明显改善后，才运行三个 FULL_OPP 当前 / candidate matched visual smoke。发现 L2/L3 局部产品问题后，按用户要求停止静态迭代。未添加 CMC_MCP_L3，因为三个正式 FULL_OPP 已足以展示剩余问题。

## Human-visible 分类

| Case | Codex 初步分类 | 人眼观察 |
| --- | --- | --- |
| ZERO | CLEARLY_IMPROVED | 虎口下方连接斜面与大鱼际上缘更饱满，first-web 开口保留；未见前两版的静态硬折面。 |
| FULL_OPP_L1 | CLEARLY_IMPROVED | 连接区改善仍可见，大鱼际主鼓起保留；局部基底 crease 更清楚，最终自然度由 Human 决定。 |
| FULL_OPP_L2 | NEW_VISIBLE_PROBLEM | 增加的静态体积在虎口基底形成更突出的硬折角 / 压挤凹槽，position-only 尚未达到自然形变目标。 |
| FULL_OPP_L3 | NEW_VISIBLE_PROBLEM | 虎口 floor 的角状折面与凹槽更明显；下部 thenar mass 仍在，但局部上缘的体积保持外观不合格。 |

`NEW_VISIBLE_DEFECT_COUNT = 2` 按 pose occurrence 计数：同一类“更突出的 web-floor angular compression”分别见于 L2、L3；不是两个独立拓扑破洞。既有 Current 的高等级 compression crease 也存在，candidate 在该处更硬 / 更角状，因此未把它自动归为通过。

## 普通实体证据与保护

46 张 final matched renders：18 张静态三列（6 camera families）、24 张 opposition current/candidate（3 cases × 4 families × 2 assets）、4 张 dorsal54 / palmar16 回归 sentinel。全部通过六张普通实体 inspection sheets 筛查，并单独看过主要静态、pose 主图与 thenar close。没有 forensic wire、normal-dot、hidden crossing census 或细微数值优化。

当前 / candidate 每组同一相机 center、direction、scale、image size、灰色材质与 studio lighting；cavity OFF。相机沿用上一轮正式 FULL_OPP_L1 掌侧斜视 family。Source default 是未改形状的原始中性 L1，采用已有刚体显示配准，标记 SOURCE_VISUAL_REFERENCE_ONLY，不能当作 RSSF exact overlay。

实际 candidate save/reopen 确认：只有 mesh vertex positions 不同。Topology、vertex order、faces、edges、loops、UV、materials、groups、weights、modifier、bones、joints、parents、rest matrices 与 pose reset 状态完整一致。Roll 所决定的 native rest orientation / matrices 精确保持；没有 edit-mode 或 bone setter。

dorsal54、palmar16、此前 normal69，以及 prior approved patch 的直接邻接边界锁定。原 approved vertices 的 position drift 均 0；matched sentinel 未见回退。其他手掌和四指普通实体图未见 gross contamination。Stage6A Human PASS closure 与 receipt 文件前后 hash 保留，**没有将旧 Human PASS 自动移授给新 candidate**，也未重新宣布 Stage6A / Stage6B Human PASS。

## 最低安全门

NaN / Inf = 0；collapsed face = 0；degenerate = 0；明显 gross self-intersection / penetration = 0；明显 tearing = 0；gross neighbor contamination = 0；ZERO restore = PASS。后三项是普通实体可见筛查，未声称没有所有数学 self-intersections。

Current 与 candidate 均对 L1、L2、L3 执行 RESET ZERO → 原定义 apply → evaluate → render → RESET ZERO，6 次 reset 全 PASS，最终 21 pose channels ZERO。静态 + pose 的最低检查均通过。局部角状折痕作为产品外观问题单独记录，不与 catastrophic face collapse 混为一谈。

## 最终字段

| 字段 | 值 |
| --- | --- |
| DONOR_SOURCE | BLENDER_HUMAN_BASE_MESHES_V1_4_1_HAND_REALISTIC_OFFICIAL_MULTIRES_L1 |
| RESTORATION_VERTEX_COUNT | 323 |
| RESTORATION_REGION | PALMAR_THENAR_VOLUME_REGION; lower first-web floor, upper thenar, palmar thumb-root connection and compact transition |
| ZERO_VISIBLE_RESULT | CLEARLY_IMPROVED |
| FULL_OPP_L1_VISIBLE_RESULT | CLEARLY_IMPROVED |
| FULL_OPP_L2_VISIBLE_RESULT | NEW_VISIBLE_PROBLEM |
| FULL_OPP_L3_VISIBLE_RESULT | NEW_VISIBLE_PROBLEM |
| DORSAL54_REGRESSION | NO |
| PALMAR16_REGRESSION | NO |
| NEW_VISIBLE_DEFECT_COUNT | 2 |
| MACHINE_SAFETY | PASS |
| ZERO_RESTORE | PASS |
| ZERO_SHAPE_PASS | YES |
| OPPOSITION_VOLUME_PRESERVATION_FAIL | YES |
| WEIGHTS_CHANGED | NO |
| RIG_CHANGED | NO |
| PRODUCTION_PROMOTION | NO |
| VERDICT | ZERO_SHAPE_PASS_OPPOSITION_VOLUME_PRESERVATION_FAIL_STOP_HUMAN_REVIEW |
| NEXT | TARGETED_THENAR_OPPOSITION_WEIGHT_TUNING_R1 |
| NEXT_EXECUTED | False |

## 审阅

[review.html](../../../../examples/historical/audits/palmar_thenar_source_shape_restoration_r1/review.html)：第一屏 Official L1 / Current ZERO / Candidate ZERO；第二屏 L1；第三屏 L2/L3；第四屏 dorsal54 / palmar16 sentinel。静态可切换 full palm、thenar close、side、silhouette、first-web close；pose 可切换 main、thenar close、side、full palm。点击图片放大，左右切换同组。Human 的 Q1/Q2/Q3 均未预选；页面可下载本地审阅答案，不自动批准或 promotion。

候选文件内部 scene flag 为 DESIGN_ONLY / HUMAN_APPROVAL PENDING / PRODUCTION_PROMOTION NO。没有 weight / joint / rig edit、左手镜像、motion retarget、Web export 或 production promotion。正式当前资产继续保持原样。

证据：[状态](../../../../examples/historical/audits/palmar_thenar_source_shape_restoration_r1/PALMAR_THENAR_SOURCE_SHAPE_RESTORATION_R1_STATUS.json)、[save/reopen 与只读保护](../../../../examples/historical/audits/palmar_thenar_source_shape_restoration_r1/CANDIDATE_SAVE_REOPEN_PROTECTION_R1.json)、[最低安全](../../../../examples/historical/audits/palmar_thenar_source_shape_restoration_r1/MINIMUM_MACHINE_SAFETY_R1.json)、[姿态与历史保护](../../../../examples/historical/audits/palmar_thenar_source_shape_restoration_r1/POSE_DEFINITION_AND_PROTECTION_R1.json)、[普通实体视觉记录](../../../../examples/historical/audits/palmar_thenar_source_shape_restoration_r1/ORDINARY_SOLID_VISUAL_INSPECTION_R1.json)、[matched manifest](../../../../examples/historical/audits/palmar_thenar_source_shape_restoration_r1/MATCHED_RENDER_MANIFEST_R1.json)。
