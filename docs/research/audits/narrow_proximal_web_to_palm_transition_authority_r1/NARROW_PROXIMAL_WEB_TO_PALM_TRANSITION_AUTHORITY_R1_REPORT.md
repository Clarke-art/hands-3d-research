# NARROW_PROXIMAL_WEB_TO_PALM_TRANSITION_AUTHORITY_R1

**FAIL_CLOSED；选择 D：仍无法唯一确定。** 固定 P02–P06 证据支持局部形态转向，但没有建立“最后 digit-web 行 / 第一 broader-interface 行”的唯一邻接对。最强几何提示为 P04/P05；它没有通过独立角色证据及 negative-control gates，不能升级为 authority candidate。

## 范围、输入和冻结约束

审查仅含 10 个指定原始 quad、18 个 incident vertices、28 个直接 vertex-incident faces。未递归追踪 neighbour，未建立 P07+ 搜索链；直接邻面中包含边界外的 incident faces，仅用于法向和局部 face fan。没有读取其更远 longitudinal profile。上一轮 trace/profile JSON 加载后立即筛选 P02–P06；旧脚本均未 import 或运行。

输入：经冻结 hash 校验的 READ_ONLY_LIVE_EXTRACTION.json，含 native/RSSF 原始坐标、相同 topology IDs 和 corrected RSSF chain。native 使用既有独立 native joint/axis evidence；它是 native 结构参照，不冒称有另一个已经应用的 corrected native rig。两状态用各自参照，绝对 chain arc 不被当成跨状态 anatomical equality。继承的 web/proximal-direction cue 只取上一轮对应五行；没有重新研究 distal/lateral/global domain。

FIRST_WEB21=FROZEN，hard pins=0；cap37=HUMAN_APPROVED_FROZEN；thumb nail=FROZEN；corrected rig=HUMAN_APPROVED/APPLIED_VERIFIED；CMC cage=GEOMETRY_PROTECTED/NOT OWNERSHIP HARD SOURCE。CORRECTED_COMMON_MM_SEMANTICS 保持 pending Human。没有 ownership labels、weights、nearest-digit winner、历史 thenar sphere 或 R3 输出作为 truth。

## Same-ID local patch 与可复算定义

每行记录 face/vertex/edge IDs、两侧 longitudinal frontier、incoming/outgoing 二段 section、world positions、polygon normals、直接 incident 面积加权 vertex normals、local L/T/N、orthonormal frame、chain/MCP/CMC 关系和 surface cues。normal 为 world-space Newell 面积向量，vertex normal 为直接 incident polygon 向量和的单位化；不是 Blender cached split normal。中心 radial direction 只用于方向投影，不输出或建立 tube radius/anchors。

L=outgoing 三顶点平均位置减 incoming 三顶点平均位置后单位化；T=两 section left→right 向量和后单位化；N=两面面积向量和后单位化。incoming/outgoing neighbour tangents 仅从本五行引用，窗口端外侧为 null。frame 同时保留原 L/T 和投影到 tangent plane 的 orthonormal L/T。

下表数值均为 **native / RSSF**；宽度为 mm，dots 为方向分量。

| Row | Faces | outgoing chord | arc/chord | L·axis | T·circ | mean N·radial |
|---|---|---|---|---|---|---|
| P02 | 1372 / 1375 | 8.551649 / 8.430882 | 1.011003 / 1.012965 | -0.629473 / -0.898418 | 0.222854 / 0.950892 | 0.347102 / 0.879542 |
| P03 | 1373 / 1374 | 8.912333 / 8.765593 | 1.006116 / 1.006874 | -0.361250 / -0.728719 | 0.510319 / 0.900077 | 0.453403 / 0.664130 |
| P04 | 1368 / 1371 | 9.470545 / 9.313368 | 1.021181 / 1.021986 | 0.015372 / -0.431442 | 0.618769 / 0.867003 | 0.209421 / 0.316326 |
| P05 | 1369 / 1370 | 10.073541 / 9.948103 | 1.020769 / 1.019602 | 0.453584 / 0.044820 | 0.671498 / 0.858928 | -0.118995 / -0.055568 |
| P06 | 1378 / 1377 | 10.023398 / 9.933195 | 1.031297 / 1.027021 | 0.726929 / 0.410710 | 0.705415 / 0.865212 | -0.356098 / -0.287206 |

## E1–E6 的独立核查与限制

**E1 longitudinal turn：** native 首次 sign reversal 为 P03/P04；RSSF 为 P04/P05。四段 tangent turns：native 17.842/23.740/26.446/22.678°，RSSF 17.172/22.664/28.346/24.446°。最大采样 turn 在 P04/P05，但没有 degree threshold，也不把 sampled maximum 视为 semantic authority。

**E2 frontier separation：** native chord 8.552→8.912→9.471→10.074→10.023 mm；RSSF 8.431→8.766→9.313→9.948→9.933 mm。P02→P05 分别增宽约 17.80% / 17.99%；随后小幅收缩。arc/chord 全程约 1.006–1.031。该带宽变化是真实 surface widening，却没有离散的两侧 fan-out/fusion 事件。局部近直的两条 edges 既可能属于 digit-sector，也可能属于 broader interface，不能单独选 P05 或 P04。

**E3 partial circumference：** 两条 face columns 不被解释为完整环。P04/P05 出现同状态 area-mean N·radial 正→负，属于共同几何提示。不过以每一 face 自己的 centroid radial 复核，P05 两种状态都混合：native face1369 +0.115233、1370 -0.365526；RSSF face1369 +0.046377、1370 -0.109587。RSSF P05/P06 的 T·circ 仍为 0.858928 / 0.865212。native P02 的 vertex317 径向 vertex-normal dot 已为负；以“所有法向都须朝 radial outward”作语义规则会使早端 control 先失效。kinematic chain 没有被批准为圆柱 surface axis；mean sign、per-face sign、vertex sign 不能互相替代。因此“columns4–6 在哪行之后不再是 thumb-local partial sector”仍 UNRESOLVED。

**E4 normal field：** normal turn 连续：native 22.112/22.433/19.549/12.476°；RSSF 21.720/24.125/21.866/13.030°。web cue native 从 0.843→−0.210，RSSF 从 0.956→0.534；不要求同一个 scalar 在同一行翻转。但局部 flank-normal agreement 在 P02 已为 0.993/0.992，全程约 0.971–0.998，无法作为只在 later rows onset 的 broader-interface discriminator。没有把 CMC direction/proximal proxy 命名成 anatomical palmar/thenar normal basis，也没有因负 palm-proxy dot 宣称“不是 palm”。

继承的 web/proximal cue 使用上一轮 equal-weight face-normal mean；本轮重新计算的 field 使用 area-weighted mean，JSON 和图表明确标为 inherited，不能当成同一新 N 的严格分量。继承 thenar-facing direction 是先前 v794 方向 proxy，不等同于本轮 corrected-chain CMC head direction。它们只保留描述性上下文，均没有成为本轮独立 role authority。

**E5 local frame：** 窗口内所有行均有非退化 surface frame，随 row 平滑旋转。P04/P05 的转动最大并不证明角色刚在该边转换；P05 的 lane 差异和 P02 的 state discrepancy 都阻止 frame scalar 自行获得 authority。local frame transition 的准确语义边界 UNRESOLVED。

**E6 MCP/CMC：** 所有 row centre 的最近 thumb reference segment 都是 CMC→MCP（segment0），不存在本窗口中的 chain-segment switch。MCP/CMC distance、offset、direction 均逐行记录；这些只表述位置，不以“越过 MCP”或 CMC cage 来决定 role。当前片带到 metacarpal/thenar/palm 的具体 anatomical fusion 没有独立局部表面证明。

## Row evidence matrix

PRESENT 表示有该方向的证据，不等于 membership 被批准。缺少排除证据记 AMBIGUOUS，不记 ABSENT；没有加权总分。

| Row | DIGIT_WEB_EVIDENCE | TRANSITION_EVIDENCE | PALM_INTERFACE_EVIDENCE |
|---|---|---|---|
| P02 | PRESENT | AMBIGUOUS | AMBIGUOUS |
| P03 | PRESENT | PRESENT | AMBIGUOUS |
| P04 | AMBIGUOUS | PRESENT | AMBIGUOUS |
| P05 | AMBIGUOUS | PRESENT | AMBIGUOUS |
| P06 | AMBIGUOUS | PRESENT | AMBIGUOUS |

P02 保留较强 web-facing 与 digit-side continuation 支持；P03 仍有 digit-web 支持并进入 morphology transition；P04 为双状态转向窗口；P05 已有径向 orientation 变化但逐面混合；P06 为 post-reversal morphology，仍缺少 positive broader-interface role certification。

## Negative controls 与真实 edge alternatives

**P02=FAIL（required exclusion 未证）**：它不像 P05/P06 的后续转向状态，但 proposed broader-context proxy——与 flank normal 对齐——从 P02 就已同样强。不能因此证明候选前一侧一定独立于 broader interface。FAIL 不把 P02 反向标成 palm。

**P06=FAIL（required broader role 未证）**：它已经 post-reversal，且两 face 的 own-centroid N·radial 都为负；仍没有积极表面角色证据证明它“已经太晚”。RSSF 中的 circumferential/web cue 仍存在。FAIL 不宣称它完整保持 digit-web，也不扩展到 P07。

所有 18 个 patch vertices valence4；每行 vertex-incident face union=12；28 个直接邻面均为 quads。每个 incident vertex 的 4 面 cyclic fan 和 shared-edge sequence 已记录，均无本窗口独有的 pole、branch 或 fan event。该结果只作辅助；没有用 graph connectivity 作 authority。

以下是三个 **未被排除的真实边对**，不是批准候选；cross-strip boundary edges 与 longitudinal frontier edges 分开记录。

| Stop alternative | Left boundary edge / vertices | Right boundary edge / vertices | Incident face transition | semantic authority |
|---|---|---|---|---|
| STOP_AFTER_P03 | e1375 = [1518, 293] | e1374 = [386, 1518] | 1373→1368 / 1374→1371 | UNPROVEN |
| STOP_AFTER_P04 | e4666 = [1444, 2822] | e4668 = [1520, 2822] | 1368→1369 / 1371→1370 | UNPROVEN |
| STOP_AFTER_P05 | e1376 = [294, 1519] | e1377 = [1519, 385] | 1369→1378 / 1370→1377 | UNPROVEN |

STOP_AFTER_P03：native turn 跨该 cut；RSSF P04 仍未 reversal，没有证明 P04 是首行 broader-interface。STOP_AFTER_P04：共同 mean radial sign 与最大 tangent turn 是最强提示；但 P05 两状态逐面仍混合，positive broader-interface onset 未证。STOP_AFTER_P05：P06 后续转动和 P05 最大 chord 无法证明 P05 是最后 web 行。这三者不是同样已批准的 boundaries；它们是三个仍不能排除的裁切位置。**neighbor alternatives rejected=NO**。

native/RSSF 确实共享 P03–P05 stable topology neighbourhood；这满足窗口稳定性，不满足唯一语义 stop。surface-supported=YES 仅针对原始十个 quads。

## 输出、核验和唯一 NEXT

10 张要求的无条件证据图已经生成。没有 boundary-candidate JSON、proposed-boundary PNG、Human Review HTML 或 role extension，因为唯一 candidate 未成立。没有把无候选的裁决问题发给 Human 当作批准页面。

245 项静态核验通过：原始 incidence/opposite-edge、same-ID rows、Newell normals 独立复算、normal/frame 有限性及正交性、真实 section arc/chord、逐面 sign mixture、semantic gate、10 PNG 解码与完整性及 conditional artifacts。静态 PASS 不等于 authority PASS。

冻结核验：1808 个既有工作区文件 + 8 个 external frozen/Human/request 文件，before==after；新增审查目录外新增、删除、修改均 0。全部既有 Stage4/5、rig、cap37、FIRST_WEB21、nail、CMC cage、R2/R3、Stage6、Human responses、distal evidence byte hashes 不变。WEIGHT/GEOMETRY/TOPOLOGY/BONE/JOINT DELTA 全部 0；R2=R3=Stage6=BLEND_FILES_WRITTEN=0。

**唯一剩余 blocker / NEXT：PROXIMAL_PARTIAL_CIRCUMFERENCE_SEMANTIC_BOUNDARY_AUTHORITY。** 只需对同三个真实 edge pairs 取得能独立区分“仍有 partial thumb-circumference 语义 / 已进入 broader-interface”的局部 surface-role discriminator，配合同样 P02/P06 controls；可以是局部可复核的 anatomical surface-frame reference 或 exact-face role evidence。不能再把另一 scalar extremum 替代角色证据，也不能扩展 proximal domain。lateral 仍保留 unresolved，等待本上游问题解决。

## 30 项最终汇总

| # | Field | Result |
|---|---|---|
| 1 | P02 semantic state | DIGIT_WEB supported；negative-control certification unresolved |
| 2 | P03 semantic state | DIGIT_WEB + morphology transition |
| 3 | P04 semantic state | TRANSITION；role AMBIGUOUS |
| 4 | P05 semantic state | TRANSITION；per-face own-centroid radial signs mixed；role AMBIGUOUS |
| 5 | P06 semantic state | Post-reversal morphology；broader-interface role UNPROVEN |
| 6 | last defensible digit-web row | UNRESOLVED |
| 7 | first defensible broader-interface row | UNRESOLVED |
| 8 | proposed boundary | UNRESOLVED |
| 9 | left boundary edge ID | null；no authority candidate |
| 10 | right boundary edge ID | null；no authority candidate |
| 11 | partial-circumference validity stop | UNRESOLVED |
| 12 | local-frame transition | UNRESOLVED |
| 13 | normal-field evidence | AMBIGUOUS for semantic boundary |
| 14 | frontier-separation evidence | AMBIGUOUS for semantic boundary |
| 15 | P02 negative control | FAIL；required exclusion not proven |
| 16 | P06 negative control | FAIL；required broader role not proven |
| 17 | neighbor-stop alternatives rejected | NO |
| 18 | native/RSSF same topological transition neighbourhood | YES；P03–P05 only |
| 19 | surface-supported | YES；fixed ten original quads |
| 20 | FIRST_WEB21 changed | NO |
| 21 | cap37 changed | NO |
| 22 | nail changed | NO |
| 23 | authority status | FAIL_CLOSED |
| 24 | Human Review page generated | NO |
| 25 | R2 runs | 0 |
| 26 | R3 runs | 0 |
| 27 | Stage6 runs | 0 |
| 28 | BLEND_FILES_WRITTEN | 0 |
| 29 | NEXT | PROXIMAL_PARTIAL_CIRCUMFERENCE_SEMANTIC_BOUNDARY_AUTHORITY |
| 30 | STOP | YES |

**STOP。**

## 可视证据

[P02_P06_TRANSITION_OVERVIEW](../../../artifacts/8da4d43ed413fbb29345.md)

[P03_P05_TRANSITION_CLOSEUP](../../../artifacts/1dbb71371170772f05d9.md)

[ROW_LOCAL_FRAMES_NATIVE](../../../artifacts/5f5b7e7e3d69f662a721.md)

[ROW_LOCAL_FRAMES_RSSF](../../../artifacts/003b77d54c53a561bf2a.md)

[FRONTIER_SEPARATION_PROFILE](../../../artifacts/74716537592698cfcef5.md)

[NORMAL_FIELD_TRANSITION](../../../artifacts/65c0697c3e4e591655e9.md)

[PARTIAL_CIRCUMFERENCE_VALIDITY](../../../artifacts/ecd3a14799fca68fe10c.md)

[MCP_CMC_LOCAL_CONTEXT](../../../artifacts/af10478d99a53227271f.md)

[P02_NEGATIVE_CONTROL](../../../artifacts/cccb86a759911a56260d.md)

[P06_NEGATIVE_CONTROL](../../../artifacts/928649d6bc87cc2977d8.md)
