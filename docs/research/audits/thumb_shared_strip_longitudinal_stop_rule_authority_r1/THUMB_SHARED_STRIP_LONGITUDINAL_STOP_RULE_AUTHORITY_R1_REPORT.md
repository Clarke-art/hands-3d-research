# THUMB_SHARED_STRIP_LONGITUDINAL_STOP_RULE_AUTHORITY_R1

**FAIL_CLOSED。Distal 已形成侧别明确、由 frozen authority conflict 定位的停止规则候选；proximal semantic stop 仍不唯一。没有 role extension、complement 或完整候选审批页面。**

## 审查范围与保护

仅从已有 R00–R08 / F3 columns4–6 出发，沿原始 quad 的 opposite edge 追踪局部 face columns。没有横向扩大到全掌，没有重建四角色地图、tube radius、R3 graph/unary/solve，没有 skin、Stage6、strict bound、retopo 或 production 写入。

9条环、8个完整 annulus、4个 frozen shared seeds、FIRST_WEB21、cap37、nail、corrected rig 与 CMC geometry-protected/non-hard-source 角色保持原样。F3 仍是诊断。first-web hard pins=0。旧 R2/R3 labels、skin weights、nearest winner 都未作为输入 truth。单位候选不复审。

输入使用前轮已校验的原始 native/RSSF 坐标、stable vertex/edge/face IDs 和 corrected chain。`INPUT_VERIFICATION.json` 校验前轮输出 manifest 及冻结 source hashes。代码只运行本新目录内的纯 Python 静态审查；既有 Blender/R2/R3/skin 脚本没有执行。

## Distal 侧别及可支持的停止规则

LEFT=column4，从 R00 v1399 出发；其第一 extension face1177 包含 frozen nail v304。停止边为 e4475=[1399,2774]，必须在进入1177之前停止。RIGHT=column6，从 v1396 出发，经 face1176，属于不立即碰到 nail 的一侧。两者由真实 incident faces / edges 判定，不凭截图。完整 frontier edges、首次 continuation edge、两种状态的 nail/cap 距离、normal 与 tangent 见 `DISTAL_FRONTIER_SIDE_IDENTITY_R1.json`。

RIGHT 的确定性 opposite-edge 延续为：1176→1213→1214→1226→1227。D01–D04 无 frozen cap/nail 冲突；D05 face1227 首次含 cap37 的 v298/v1454，同时出现非4-valence 顶点。native/RSSF 使用同样 IDs。这个事件不是任意角度或曲率阈值。

| Row | Face | native 最近 cap 顶点距离 mm | RSSF 同指标 mm | web-context normal dot native / RSSF |
|---|---:|---:|---:|---|
| D01 | 1176 | 13.910409 | 13.798752 | 0.632472 / 0.526257 |
| D02 | 1213 | 9.927953 | 9.830623 | 0.480190 / 0.361638 |
| D03 | 1214 | 5.951088 | 5.878505 | 0.360839 / 0.242460 |
| D04 | 1226 | 2.343856 | 2.301493 | 0.228748 / 0.121942 |
| D05 | 1227 | 0.000000 | 0.000000 | 0.076692 / -0.018415 |

Distal 停止规则候选：**沿既有 non-nail 面列继续，在首次 frozen nail/cap 冲突前停止**。最后安全 row=D04 / face1226，末端边 e4524；下一面1227禁止进入 shared extension。左侧在1177前停，右侧在1227前停，允许 asymmetric taper。

这里的 RESOLVED 指该固定 face-column 上的停止规则候选已可确定，仍 pending Human；并不是宣称所有安全面已经获得 anatomical shared ownership。硬冲突建立禁止继续的上界；逐面连续性、仍朝 web context 的辅助法向与逐渐接近 frozen distal cap 提供候选的上下文。D01–D04 的正 normal dot 不是 membership 阈值，也不自动证明 shared anatomy。后续 lateral/role authority 仍须独立满足。

D0 CROP_AT_R00、D1 单面、D2 两面都没有在其截断处发现独立事件。D3 追至首个冻结冲突产生 D04 规则候选。不能因为它们更短或新增点更少选择 D0–D2。

## Proximal：首次形态转向窗口已定位，唯一 stop 未确定

沿 R08 两个真实面列，P01=3032/3033，P02=1372/1375，之后 P03=1373/1374，P04=1368/1371，P05=1369/1370，P06=1378/1377。所有这些行仍有完整原始 quad 支撑。

| Row | Face IDs | native outgoing mean chain arc mm | RSSF outgoing mean chain arc mm |
|---|---|---:|---:|
| P02 | 1372,1375 | 30.875508 | 33.701616 |
| P03 | 1373,1374 | 29.930316 | 31.831315 |
| P04 | 1368,1371 | 29.968738 | 30.840123 |
| P05 | 1369,1370 | 31.303167 | 30.957692 |
| P06 | 1378,1377 | 33.852640 | 32.251041 |

native 的纵向方向在 P03→P04 首次反转；RSSF 在 P04→P05 首次反转。同一批顶点逐步远离各自 thumb centerline，表面方向转向更广的 interface。这个变化支持 **P03–P05 是待裁决的 morphology transition window**，不足以唯一选择某行作为 DIGIT_WEB_TO_PALM_SEMANTIC_TRANSITION。

两种状态的差异来自 repose 与各自轴估计，不把它伪装成精确不变的 stop。native axis 取独立 native joint evidence，RSSF axis 取 corrected live chain；两者 arc 原点不同，绝对 arc 不作为跨状态 anatomical equality。MCP 仅作参照，没有“过 MCP 自动停止”。profile 中 R06–R08 的 arc 是 columns4–6 采样值，不是16点整环平均值。

为检验 S3，只沿同两个面列继续到第一个 lane valence event：P35 的 v247 valence3，且 successor faces1923/1922仍为 quads。这个纯拓扑 negative control 证明 regular quad continuation 可远远越过早期形态转折；P35 不能作为 web-strip semantic stop。没有搜索任意 shortest path，也没有把这35行纳入 shared region。不存在全掌 membership 或 ownership 重建。

`PROXIMAL_SHARED_STRIP_LONGITUDINAL_PROFILE.json` 包含 R06/R07/R08 与全部实际 trace rows 的 arc、距离轴 proxy、frontier separation、partial-section arc/chord、角宽、normal progression、tangent、valence、CMC v794 空间距离及 proximal/thenar-facing 方向 proxy。这些方向只表示结构位置，不能制造 thenar ownership。CMC cage 原 geometry 完全保留，没有使用先前不精确的73点重构作为精确 cage mask。

**证据限制明确保留：** 已知 R06–R08 的 circumferential completeness 可沿用；R08 后仅两列的完整 faces 不足以证明全圆周是否完整。该字段记为未证，而非把两列连续当作完整 thumb ring。没有为补足它而横向扩展整个 palm。距离为 mm；nail/cap 距离明确为最近冻结顶点距离，非连续面距离。local tube radius proxy 只是距离轴描述，不是被禁止的 tube-radius authority 重算。

## Negative controls 与候选 family

Distal 对 D04 检查提前2行D02、提前1行D03、延后1行D05、延后2行D06。早停没有对应 frozen conflict；晚停跨过 cap37，不能接受。该 gate 对“沿此固定列走到首个冲突前”的停止规则候选通过，但不代替 role-membership approval。nail侧也检查早一行、1177前及晚一行；进入1177造成 nail v304 冲突。

Proximal 对 P02–P06 各停止方案检查：全部有真实 surface support，零 cap/nail 冲突，均无对应的独立拓扑切断。native 与 RSSF 的几何转折落在相邻行；没有现有冻结 anatomical boundary 能从中选一个。因此 **neighbor-stop 完整 gate=FAIL**，不是选择最短/最连通方案。

| Family | 结论 |
|---|---|
| S1 SYMMETRIC_CROP | 拒绝作为 authority；R00/R08 是旧分析范围 |
| S2 ASYMMETRIC_TAPER + PROXIMAL_SEMANTIC_STOP | Distal 可形成停止规则候选；proximal 未解 |
| S3 FULL_FACE_STRIP_UNTIL_TOPOLOGY_STOP | 拒绝作为语义 authority；lane pole 不能说明 web/palm role transition |
| S4 HYBRID_AUTHORITY_CONFLICT_AND_MORPHOLOGY_STOP | 未形成完整候选；仅 distal conflict 已确定 |

`LONGITUDINAL_STOP_NEGATIVE_CONTROL_AUDIT.json` 保留全部面/点/冲突/支撑证据；不把邻近安全裁切隐瞒成唯一解。

## Lateral 与 role extension gate

columns4–6 维持原 topology candidate，不扩大横向范围。Distal frozen conflicts 不能反证其余圆周为 exclusive；proximal stop 又未解，故 `LATERAL_FRONTIER_POST_STOP_REVALIDATION.json`=UNRESOLVED。

F3+D04 仅诊断：35点/20面，完整 surface support，wire-only=0，dangling=0。这不是 final shared extension count。正式 extension 顶点/面数及 THUMB_EXCLUSIVE complement count 均为 null，不能写0来假装已批准空集合。

没有生成 `THUMB_WEB_SHARED_NEUTRAL_ROLE_EXTENSION_R1.json`、`FINAL_LONGITUDINAL_STOP_CANDIDATE.png` 或完整 Human Review HTML，符合仅成功时生成的条件。8张无条件证据图已生成，所有视图标注 FAIL CLOSED。

## 验证与冻结

104 项静态检查通过：原始 opposite-edge 邻接、侧别 frozen conflict、相邻行对照、局部 metric 范围、native/RSSF exact topology、surface support、输出条件与8张 PNG 完整性。验证通过不等于 authority 成功。

用户要求的 shared-seed edge-geodesic 仅在 F3 加 distal trace 的固定面图上计算，用于 profile 描述。未计算全场 R3 dT/dI，也未建 R3 graph；proximal 没有 shortest-path 搜索。curvature 使用 normal turn/edge dihedral 描述，没有 magic threshold。

冻结核验：1776 个既有工作区文件 + 7 个外部 authority/Human/本轮请求文件 before==after；新审查目录外新增、删除、修改均为0。WEIGHT_DELTA=GEOMETRY_DELTA=TOPOLOGY_DELTA=BONE_DELTA=JOINT_DELTA=0。R2=R3=Stage6=skin rebuild=strict bound=retopo=0，BLEND_FILES_WRITTEN=0。

## 唯一 NEXT

**NARROW_PROXIMAL_WEB_TO_PALM_TRANSITION_AUTHORITY**：仅在 P03–P05（1373/1374、1368/1371、1369/1370）及 P02/P06 邻接对照内，取得能确定 web strip→broader shared interface 的独立、同 IDs 可复核的边界证据。不要再次追踪整个 domain。lateral confirmation 保留为该上游问题解决后的 gate，不在本轮扩大研究。

**STOP。**

## 可视证据

[DISTAL_NAIL_SIDE_HARD_STOP](../../../artifacts/7da5c30560655b7d94b2.md)

[DISTAL_NON_NAIL_TAPER_PROFILE](../../../artifacts/639841ca0ada072b592c.md)

[DISTAL_STOP_OPTIONS_CLOSEUP](../../../artifacts/2bb66f88e73977e2659b.md)

[MCP_TO_PALM_TRANSITION_CONTEXT](../../../artifacts/f836f8dee907cdcebd9b.md)

[NATIVE_RSSF_STOP_STABILITY](../../../artifacts/e406747afa69c49f2b92.md)

[PROXIMAL_LONGITUDINAL_PROFILE](../../../artifacts/72554821ae4b6b701eaf.md)

[PROXIMAL_R08_CONTINUATION](../../../artifacts/5832c2918152f298b0ea.md)

[STOP_EVENT_NEGATIVE_CONTROLS](../../../artifacts/ac67378dca5272486a22.md)
