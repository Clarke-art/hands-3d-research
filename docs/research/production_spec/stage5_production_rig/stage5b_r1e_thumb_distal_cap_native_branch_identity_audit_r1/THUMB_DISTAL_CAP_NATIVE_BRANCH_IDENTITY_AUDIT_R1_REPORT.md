# THUMB_DISTAL_CAP_NATIVE_BRANCH_IDENTITY_AUDIT_R1

**本轮 native identity 审计结论：CURRENT_APPROVED_CAP_9 = CONTAMINATED。全部 9 点位于原生食指近节指管，v2192 native branch = INDEX。** 这是独立回到原生几何后的分支鉴别，不再以 historical cap membership 或继承后的 R3 标签作证明。本轮不修改 cap authority，不重做上一轮 Human Review。

## Human authority 原文保持

Q1=YES；Q2=UNRESOLVED；Q3=UNDECIDED；Q4=NO；Q5=LIMITED。四簇 Human candidate 仍为 UNDECIDED。

> Human Review：body-side 16 视觉上主要对应食指近节表面；RADIAL cluster 与 first-web 的真实对应尚未确认。v2169 不支持认定为已证明的 index/thumb shared interface。v2192→v703→v2169→v704 作为 mesh 连续表面路径成立，但不支持将其解释为真实 thumb distal cap→index collar 的解剖路径；v2192 的 distal-cap membership 需单独重新审计。

本轮接受这些输入，不将 Q4 改成 shared interface，不将 Q5 的 LIMITED 改成“已确认真实 thumb-cap→index 解剖路径”，也没有重新询问 Human。原文件、上一轮记录和页面均未改写。

## 独立 native anchors 与分支鉴别

只读打开 Stage4A_R2 pre-RSSF 和 Stage5A_R2 selector 原始 mesh state，直接读取保存的 world coordinates / topology / rest bones；**pose evaluations=0**。两者完整 face-vertex index ordering 与已有 R1B 静态提取一致。原生模型 hash：`4fa2cb6f31d8097110718e4d9cc424c30d1d2b7057c76abd93c338a5c7201039`。骨点、接触姿态距离或 downstream authority 均不作为 native 点位属于 thumb 的独立证明。

独立锚点来自早于 cap selector 的 `stage4b_rssf_r2.py` native TIP_SEEDS，经 native mesh matrix 正确变换后，拇指端为 **v284**，食指端为 **v233**。没有从 CURRENT_CAP_9 选 seed。另将 `stage4c_r2/NAIL_AUDIT_R2.json` 的 12 个 thumb nail faces / 29 个 index nail faces 按不变拓扑映射回原生形状；其所有顶点分别落在连续的拇指 / 食指终端指管。它们是在 cap 之前建立的 nail masks，本轮还用原生分支、显著分离的指尖和可见指管交叉验证，未仅凭文件名称接受。

THUMB anchors 为独立 tip+nail，共 23 点；INDEX anchors 共 44 点，两套均与当前 cap9 无交集。native thumb IP→tip / index MCP→PIP 的方向来自原生横截面中心定位函数的只读重建，没有在 native frame 里复用 posed skeleton。模型 joint 仍是工程估计，不是本轮新增骨权威。

以五个独立指尖及 wrist 为源，计算 native edge-length 多源分区，并用 local tube、incident faces、一环/二环及 nail-to-tip continuity 交叉检查。全掌分区界面不能自动当真实 shared skin；本轮只对远离界面的 cap9 指管点作判定。first-web 距离采用独立 native index/thumb cleft 的 structural proxy（v473 加一环），**并未把它注册为新的 first-web skin authority**，Human Q2 保持 UNRESOLVED。

## 九点逐点结果

距离单位 mm，均是 native edge-length shortest paths 至独立 anchor sets；完整双向 vertex sequences 在 `CURRENT_CAP9_NATIVE_BRANCH_CLASSIFICATION.json`。最后一列是只读重建的 native INDEX MCP→PIP 工程轴投影，不是照片配准结果。

| vertex | 分类 | thumb anchors | index anchors | first-web proxy | native INDEX 轴 fraction |
| --- | --- | ---: | ---: | ---: | ---: |
| 151 | INDEX_SURFACE | 134.150 | 49.240 | 52.464 | 0.218 |
| 158 | INDEX_SURFACE | 125.329 | 47.028 | 43.643 | 0.234 |
| 1061 | INDEX_SURFACE | 129.853 | 53.781 | 48.599 | 0.072 |
| 1074 | INDEX_SURFACE | 121.154 | 51.482 | 39.900 | 0.091 |
| 1076 | INDEX_SURFACE | 129.842 | 49.266 | 48.156 | 0.226 |
| 2189 | INDEX_SURFACE | 138.324 | 45.066 | 56.533 | 0.351 |
| 2192 | INDEX_SURFACE | 129.505 | 42.796 | 47.404 | 0.369 |
| 2569 | INDEX_SURFACE | 134.008 | 45.101 | 52.159 | 0.359 |
| 2577 | INDEX_SURFACE | 125.559 | 53.786 | 44.305 | 0.081 |

九点一环、二环及 incident faces 全在连续 native INDEX 管上。分类由这些相互支持的证据决定，不由距离大小单独决定；CURRENT_CAP_9 / R3 THUMB / THUMB_STRONG / THUMB_DISTAL / 当前 RSSF 距离未作为分类依据。

## v2192 专项

one-ring：`[158, 703, 2569, 2591]`；exact two-hop ring：`[1074, 1075, 1076, 2168, 2169, 2175, 2178, 2189]`；incident faces：`[356, 359, 445, 446]`。这些面与邻点全部属于原生食指管。

到 native thumb anchors：**129.505028 mm**，终点 v304；到 native index anchors：**42.796075 mm**，终点 v230。index 路径起始段为 v2192→v703→v2169→v704，继续沿同一食指管到 nail 区；thumb 路径先沿食指向根部回走，再经过掌/虎口通道进入真正独立的拇指分支。这直接解释为何局部连续性不等于 thumb-cap 解剖身份。

## 原始 cap selector 的精确复现

正式 canonical rule 由 R2B errata 声明为 geodesic connected cap；历史 JSON/header 的 slab-method 文本是已废止的说明，本轮没有据它重算。

实际执行链：

1. 在保存的 Stage5A_R2 RSSF/contact mesh 中，面质心到各 full bone chains 的 Euclidean polyline distance 取最小值，得到 `FACE_OWNER`。
2. `DIG_VERTS[THUMB]` 是所有 nominal THUMB-owned faces 顶点的并集；取位于 nominal THUMB_IP→TIP 正投影侧的点，再最大化离 IP 的 Euclidean 距离，得到 **seed v2189**。v2189 在独立 native 检查中是 **INDEX**。
3. 从 v2189 沿 **全 mesh edge graph** 做长度 Dijkstra。图没有 thumb-only gate；之后才对 faces 加 owner gate。
4. face predicate 为 `owner == THUMB AND min(corner g) <= 9 mm`，保留含最近 seed face 的面邻接连通分量；最后 `capv = union(selected face corners)`。

本轮复现结果与冻结结果完全一致：faces **356, 357, 389, 390**；vertices **151, 158, 1061, 1074, 1076, 2189, 2192, 2569, 2577**。

**v2192 的确切纳入步骤：face356 的 corner union。** face356 = `[158,1076,2569,2192]`。在旧 posed-chain selector 中，其质心离 nominal THUMB chain 为 **11.972809 mm**，离 INDEX chain 为 **13.488749 mm**，于是数值规则将它指派为 THUMB。face356 的最小 corner geodesic 是 v2569 的 **4.369009 mm**，满足 9 mm；v2192 自身 g=**9.071490 mm**，仍作为该面的角点被纳入。seed→v2192 路径为 `[2189,2569,2192]`。其自身略超 9 mm 是 min-corner face expansion 的结果，不是实现违规。

根因：**DIGIT_IDENTITY_CONTAMINATION / OWNED_FACE_ERROR**；contact-pose nearest-chain 距离将原生食指面放入 nominal thumb domain，进而造成 **SEED_ERROR**。旧 seed、四个 selected faces 全是 native index branch。世界坐标输入能精确复现全清单，没有发现必须借助 local/world 或单位错误才能解释的证据。全局 geodesic graph 确实缺少独立 branch guard，但本次 seed→cap 路径本来就留在 INDEX 上，跨 web 图泄漏不是解释此错误所必需。

因此，**9 mm 的局部测地规则可以在错误 seed/domain 上合法地选择 index surface**。数字半径、连通性与 downstream labels 都不能补回最初的 anatomical digit identity。

## 独立 native distal-cap candidate

只读生成候选：以独立 native thumb branch 的 IP→true terminal-tip direction 定位最远端 seed **v284**，在 **native THUMB-only induced edge graph** 上计算 9 mm geodesic，再选 min-corner 满足阈值、与 seed face 连通、全部位于 native thumb 的 faces。候选共 **48 vertices / 33 faces**，与当前 cap9 **交集为 0**。

9 mm 是继承已声明的 local-geodesic convention，不是生产权重或新人体端帽权威。min-corner face predicate 可扩入更远的角点；本候选最大角点距离 **15.894139 mm**，因此不可把它描述成“所有点均在 9 mm 球内”。候选边界尚需 Human cap authority correction；没有自动替代冻结清单。

TP IDs：`[]`。

FP IDs：`[151, 158, 1061, 1074, 1076, 2189, 2192, 2569, 2577]`。

候选相对 FN IDs：`[36, 37, 39, 44, 283, 284, 285, 339, 340, 341, 505, 879, 880, 881, 882, 886, 889, 890, 1338, 1339, 1340, 1341, 1342, 1343, 1344, 1378, 1380, 1382, 1450, 1452, 1453, 1454, 1752, 1753, 1754, 1755, 2496, 2499, 2740, 2741, 2742, 2743, 2785, 2790, 2963, 2964, 2965, 2966]`。这里 FN 是与本轮独立候选的集合差，不是已获 Human 批准的新增 membership。

Unresolved current-cap9 IDs：`[]`。

## cap-dependent strict-bound invalidation

**13.1646 mm path、CMC_MCP_L3=5.9643、FULL_OPP_L3=6.5160 均标记 INVALIDATED，范围是“真实 thumb distal-cap→index collar 的解剖端点解释”。** 旧 mesh 固定 ID 的路径长度、已存 posed endpoints 与 `max stretch >= posed separation / bind path length` 数学不等式仍保留为历史数值事实。没有修改历史审计文件，没有抹去旧实际 deformation 观测或 R1E fail-closed 状态。

本轮完整列出 **144 个 cap9→INDEX collar 固定 ID shortest paths**，展开历史 top10 paths 和 **60 个已存 strict-bound rows**，并登记后续 endpoint sensitivity JSON 内 **17640 个 bound 数值依赖位置**及受影响证据文件。全部九个起点是 native INDEX surface，因此失效不限于 v2192 最短一条。

真正 native cap→collar 的 replacement path / bound 为 **PENDING_RECOMPUTE_AFTER_HUMAN_CAP_AUTHORITY_CORRECTION**。本轮没有重算 pose 或 deformation，没有借新候选继续求解权重。

## 最终十四项答复

| 项目 | 答复 |
| --- | --- |
| 1. TRUE_THUMB_DISTAL_CAP | 0 |
| 2. THUMB_DISTAL_BUT_NOT_CAP | 0 |
| 3. INDEX_SURFACE | 9 |
| 4. FIRST_WEB_SHARED_SURFACE | 0 |
| 5. UNRESOLVED | 0（OTHER 亦为 0） |
| 6. v2192 native branch | INDEX |
| 7. v2192 entered cap because | contaminated nominal THUMB domain→native-index seed v2189→9mm min-corner face356 predicate→corner union |
| 8. CURRENT_CAP_9 | CONTAMINATED |
| 9. FP IDs | 151, 158, 1061, 1074, 1076, 2189, 2192, 2569, 2577 |
| 10. FN IDs | 36, 37, 39, 44, 283, 284, 285, 339, 340, 341, 505, 879, 880, 881, 882, 886, 889, 890, 1338, 1339, 1340, 1341, 1342, 1343, 1344, 1378, 1380, 1382, 1450, 1452, 1453, 1454, 1752, 1753, 1754, 1755, 2496, 2499, 2740, 2741, 2742, 2743, 2785, 2790, 2963, 2964, 2965, 2966（native candidate-relative） |
| 11. 13.1646 mm path | INVALIDATED as anatomical cap path; mesh continuity retained |
| 12. CMC_MCP_L3 5.9643 | INVALIDATED as anatomical cap endpoint bound |
| 13. FULL_OPP_L3 6.5160 | INVALIDATED as anatomical cap endpoint bound |
| 14. NEXT | HUMAN_CAP_AUTHORITY_CORRECTION |

## 可视证据与冻结

七张 native 静态投影已逐张检查：cap9 branch map、thumb anchors、index anchors、v2192 one/two-ring、thumb-vs-index paths、current-vs-native cap 和 all-cap9 classification。全局与局部相互对照；隐藏点以独立投影标记显示，避免把遮挡误当“不存在”。只裁展示窗口，没有改 mesh。审计的全部输入哈希在冻结记录中。

1378 个既有 production_spec/docs 文件及 workspace BLEND before=after；BLEND_FILES_WRITTEN=0；WEIGHT/GEOMETRY/TOPOLOGY/BONE/JOINT DELTA=0；R1F_CREATED=false。Human 输入、冻结 cap、first-web、CMC cage、R3、R1B 及 R1E 状态保持原样。未运行 Stage6A/Stage6B、weight solve 或 retopo。

**STOP — WAITING FOR HUMAN CAP AUTHORITY REVIEW。**
