# THUMB_FROZEN_WEB_PARTIAL_CIRCUMFERENCE_FRONTIER_AUTHORITY_R1

**FAIL_CLOSED。未形成可供批准的唯一 frontier；未生成 solver-role extension 或 Human Review HTML。**

本轮仅检查已有 9 条 thumb 环、8 条真实 quad face strips，以及两端各两排面的局部延续。没有重新研究全局 proximal domain。4 个冻结 shared seeds 有效；真实拓扑对应已确定。缺失的是该局部 shared strip 的停止 authority，尤其 distal 非 nail 侧可继续而 proximal 没有可证终止的位置。不能把分析范围裁切线充当解剖边界。

## 输入与冻结约束

几何取自已有 `READ_ONLY_LIVE_EXTRACTION.json` 的 NATIVE/RSSF 状态，corrected chain 取 CORRECTED bones。缓存 SHA256 对照原 reconciliation manifest；独立 cap、nail、FIRST_WEB source 路径与哈希列于 `INPUT_VERIFICATION.json`。使用原始 mesh faces/edges 和 stable vertex IDs，不读取旧 R2/R3 ownership labels，不把 skin weights、最近 chain winner 或连通性当作 anatomy。

cap37、corrected rig、FIRST_WEB21、nail、CMC cage、INDEX ingredients 及既有 Human responses 不改动。first-web 默认 shared-neutral graph-only，hard pins=0；CMC 保持 geometry-protected / non-hard-source。CORRECTED_COMMON_MM_SEMANTICS 仅引用 pending-Human 状态，没有复审单位。

## Ring stack 与真实面带对应

9×16=144 个互不重叠环顶点，8×16=128 个面。相邻环各有 16 条真实纵向边，构成一一对应及完整闭合 quad annulus。R00 使用最小 ID 及较小首邻居作循环索引约定；之后仅沿真实 edge/face strip 传递列编号。索引本身不赋予角色，没有角度最近匹配。

| Ring（distal→proximal） | corrected chain mean arc mm | frozen shared |
|---|---:|---|
| R00 | 73.525587 | v1399, v2774, v1396 |
| R01 | 69.355579 | v1402 |
| R02 | 64.800725 | — |
| R03 | 59.994671 | — |
| R04 | 54.948889 | — |
| R05 | 50.099362 | — |
| R06 | 45.615748 | — |
| R07 | 42.258905 | — |
| R08 | 38.627281 | — |

MCP arc=46.943713 mm；IP arc=74.642942 mm。每环完整 vertex/edge sequence、axial min/max、到 MCP/IP 的 signed arc 与 Euclidean distance，见 `THUMB_PROXIMAL_RING_STACK_R1.json`。各环之间的 face IDs 和逐顶点对应见 `THUMB_RING_TO_RING_CORRESPONDENCE.json`。

R00 seeds 为 columns4/5/6：v1399/v2774/v1396；R01 column5 为 v1402。逐点 incident faces、一环/两环邻域及 surface connections 已记录于 `FROZEN_WEB_SEED_CONTEXT_AUDIT.json`。其余 17 个 frozen web vertices 与此 stack 没有共同 face，也没有一跳或两跳接触；本轮没有制造角度投影或跨区域路径来扩张它们。

## F1–F4 局部候选比较

| Family | 可复核结果 | authority 限制 |
|---|---|---|
| F1 | 唯一最小 seed-connected patch：faces1178/1179；6 点，其中新增支撑点 v305/v306 | 最小 seed cover 不是 shared→exclusive 停止证据；不能因此在 R01 后终止 |
| F2 | native/RSSF normals 对独立 index root、web context 的方向描述；记录 sign crossings 与局部 normal turns | 仅辅助；两种几何状态的 sign crossing edges 可变，不能独立裁决边界或终止 |
| F3 | columns4–6 沿真实面带传到9环：27点，16面，左右链各8边；23点不属于 frozen web21 | 全 stack 延续是假设；R00/R08 是诊断裁切，不是 authority termination |
| F4 | NOT_FORMED | F1/F3 在共同两环的横向列一致，但纵向 extent 不一致，且没有可证终止依据 |

F1 的最小性通过枚举 stack 内 128 面中的一面/两面连接器独立验证，唯一最小解为1178/1179。F3 每环是一个连续3点弧，绝不把整环设 shared。左右各再加一真实 face column 的诊断方案同样能保持 surface support；因此“最小列宽”也不能自行升级成解剖 exclusivity。当前左右链只是证据最小的 topology candidate，尚未成为最终 authority。

所有完整 vertex/face/edge ID 集合保存在 `LOCAL_DIAGNOSTIC_STRIP_SETS.json`；最终候选字段在 `THUMB_SHARED_SECTOR_FRONTIER_CANDIDATE_AUDIT.json` 明确为 null，而不是空集合。没有手工批准额外点，也没有以4个 seeds 的补集直接定义 THUMB_EXCLUSIVE。

## 纵向连续、法向与 native/RSSF 稳定性

F3 使用同样的 vertex IDs、face IDs、左右 frontier topology，在 native/RSSF 完全一致。单环是一个连续 arc；邻环最大 centroid 变化为 native 2.300296°、RSSF 2.580222°，没有180°跳转、全环扩张或中断后重现。左右轨迹与宽度逐环详见 continuity JSON。

这些角度仅描述几何。本轮用局部 ring-center tangent 与 nail dorsal cue 定义角度坐标，R00 宽度约43.469592°/43.774876°；此前约44.024973°/44.323624°来自不同轴基准，不能互作阈值或据此改变 membership。本轮没有 ±22°、44°、normal-dot 阈值或 nearest winner 生成规则。

4 个 seeds 的 web-facing normal dots 在两种几何状态均为正，支持其局部 web-facing 位置；这不意味着正 dot 的其余顶点都应 shared，也不证明负 dot 就 exclusive。法向 sign crossing 在 repose 后不固定，因此 F2 不能补上缺失的局部边界 authority。

## Distal / proximal termination：非唯一性的具体证据

Distal R00 两条 sector 边都存在唯一 quad continuation。face1177 包含 frozen thumb nail v304，约束该侧不能直接纳入默认 shared support；相邻 face1176 无 cap/nail 冲突，下一排 face1213 同样无冲突。故“停在 R00 的平截线”和“只向非 nail 侧做 taper”并未被现有证据唯一裁决。不是因为下一环缺 seed 就停止。

Proximal R08 两侧继续进入 faces3032/3033，再下一排也有真实 quad continuation；局部没有 topology stop/pole 或固定 anchor 冲突支持把 R08 当作 broader-palm transition 的确定边界。这里只检查两排面的局部证据，不扩张 palm role map。

以下仅为 negative controls，全部通过真实面支撑、零 wire/dangling、cap/nail 无冲突及连接保留。它们证明结构可行性不足以选定停止位置；没有任何一个被批准：

| 诊断停止方案 | F3 外追加 faces | shared 诊断点数 | surface/anchor gates |
|---|---|---:|---|
| CROP_AT_R00_R08 | — | 27 | PASS |
| DISTAL_ONE_NON_NAIL_FACE | 1176 | 29 | PASS |
| DISTAL_TWO_NON_NAIL_FACES | 1176, 1213 | 31 | PASS |
| PROXIMAL_ONE_FACE_ROW | 3032, 3033 | 30 | PASS |
| PROXIMAL_TWO_FACE_ROWS | 3032, 3033, 1372, 1375 | 33 | PASS |

`DISTAL_PROXIMAL_TERMINATION_AUDIT.json` 提供逐边、逐面、opposite edge 和 valence；`LOCAL_TERMINATION_NONUNIQUENESS_CONTROLS.json` 提供上述多解。distal termination=UNRESOLVED；proximal termination=UNRESOLVED。

## Surface support、cap/nail 连续与局部角色

F1/F3 所有支撑顶点均属于其完整原始 faces；induced edges 全部有完整面支撑，wire-only edges=0，dangling vertices=0。纵向8个面带加两端一排/两排 probes 说明结果不是单个低分辨率面角的偶然连接。但“多排支持”仍不授予解剖停止 authority。

从 distal thumb surface 排除 F3 后，剩余238点为一个连通 component，包含 cap37、thumb nail 及 stack 剩余117点。这个测试只证明相容性，117点尚未被判为 THUMB_EXCLUSIVE。

正式局部 map 覆盖144点：4 SHARED_NEUTRAL（仅已冻结 seeds），140 UNRESOLVED，0 已裁决 THUMB_EXCLUSIVE。各环 A/B/C final state 保留 null；F3 诊断分类为9条 PARTIAL_SHARED_SECTOR。其余局部点不得伪装成 FULLY_THUMB_EXCLUSIVE 或 FULLY_SHARED。没有 INDEX_EXCLUSIVE / OUTSIDE 全域裁决。

FIRST_WEB21 membership 与未来 R3_SHARED_ROLE_EXTENSION 是不同 authority。本轮没有生成 `THUMB_WEB_SHARED_NEUTRAL_ROLE_EXTENSION_R1.json`。23 只是 F3 假设的非 web21 支撑点数，16 是整个假设扇区的支撑面数，不是已批准的新 anatomical web faces。shared hard pins 始终为0。

## 验证、冻结与停止

`LOCAL_STATIC_VERIFICATION_R1.json`：44 项静态检查通过，包括真实循环边、face bijections、native/RSSF identity、唯一 seed connector、多解 negative controls、保守 role map 和10张 PNG 的完整性。没有运行 solver。

`FROZEN_HASH_VERIFICATION_R1.json`：1740 个既有工作区文件 + 6 个外部 authority/Human 文件 before==after；审查目录外新增/删除/变更均为0。WEIGHT_DELTA=GEOMETRY_DELTA=TOPOLOGY_DELTA=BONE_DELTA=JOINT_DELTA=0。R2=R3=Stage6=skin rebuild=strict bound=retopo=0；BLEND_FILES_WRITTEN=0。

唯一 NEXT：**THUMB_SHARED_STRIP_LONGITUDINAL_STOP_RULE_AUTHORITY**。在已识别局部 web-connected 面带内，为 shared→exclusive transition 提供独立停止依据，具体区分 R00 平截与 faces1176/1213 非 nail 侧 taper，并确定 R08 后 faces3032/3033 延续何处停止。当前横向最小列宽也是候选，不能因后续停止规则被确定便自动冻结左右链；须以该局部 transition 证据复核。不得回到 generic proximal-domain research，不得依靠连通性选择。

Human authority 仍需介入缺失的局部停止依据；由于未形成唯一完整候选，未生成成功用的7问 Human Review 页面。没有要求重新批准4个 frozen seeds 的既有 membership。

**STOP。**

## 局部可视证据（全部为诊断，不是已批准 role extension）

[DISTAL_PROXIMAL_TERMINATION](../../../artifacts/c9861cf828c3b30ec93e.md)

[FROZEN_WEB_SEEDS_ON_RINGS](../../../artifacts/dcb0f7544d0133a4b38c.md)

[LEFT_RIGHT_FRONTIER_CHAINS](../../../artifacts/53d91306c239bb033588.md)

[NATIVE_VS_RSSF_SECTOR_STABILITY](../../../artifacts/a6c0b1783aa818052405.md)

[PARTIAL_SHARED_SECTOR_DORSAL](../../../artifacts/6e76343daff8b8d9bfeb.md)

[PARTIAL_SHARED_SECTOR_PALMAR](../../../artifacts/b4ca4e0e3eda7111f980.md)

[PARTIAL_SHARED_SECTOR_RADIAL](../../../artifacts/ac5fa5a0a1742922b103.md)

[PARTIAL_SHARED_SECTOR_ULNAR](../../../artifacts/be4bfba05831b9794cd3.md)

[THUMB_EXCLUSIVE_COMPLEMENT_ARC](../../../artifacts/66db03f205742d7bc027.md)

[THUMB_RING_STACK_OVERVIEW](../../../artifacts/925cd4057f2fa862ab2f.md)
