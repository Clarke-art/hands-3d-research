# CAP_BOUNDARY_E_FIVE_VERTEX_ADJUDICATION_R1

E_FINAL = **READY_FOR_HUMAN_CAP_AUTHORITY_FREEZE**，仅表示五点审阅材料与工程自检完成。Human 本轮 Q1–Q7 未答；未执行 freeze，未应用 production authority。建议 v1453/v2785/v2790 REMOVE，v297/v298 KEEP；E_FINAL 与 Human-selected E baseline 完全一致：37 vertices / 25 faces。

## Binding Human input

先读取原始 `<USER_HOME>\Downloads\HUMAN_THUMB_DISTAL_CAP_BOUNDARY_RESPONSE_R1.json`，SHA-256 `c525b55bf179fa8c77d4d3871bbf6f0c63db31e191f190189e49b7ab2b11c8a5`。本目录 SOURCE_COPY 为逐字节副本。Q1=YES，Q2=YES，Q3=NO，Q4=NO，Q5=YES，Q6=E，Q7=APPROVE_WITH_MINOR_BOUNDARY_FIX。以下 Human notes 原文保留为 binding input；其中既有比较没有在本轮重新计算：

> Candidate E 在当前五组方案中最符合 distal bulb→shaft 的稳定周向边界。A 存在近端外扩，B/C 过紧且未完整覆盖 distal nail-margin，D 过度扩大且 curvature authority 不稳定。批准 E 作为最终 cap boundary 的基线候选，但暂不直接冻结；要求仅对 v1453、v2785、v2790、v297、v298 进行最后的 narrow boundary adjudication，除这 5 个顶点外不得重新打开其它已通过区域。

region identity = ACCEPTED_UNCHANGED；E = SELECTED_HUMAN_BASELINE；old cap9 = INVALID（既有结论未重审）。仅五点进入本轮裁决；其它 E membership 冻结。未读取 A/B/C/D 候选文件，未设计新 boundary family，未重开 seed/branch/48-point identity、R3、first web、CMC cage、RSSF。

## Native evidence and method

NATIVE_PRE_RSSF_STAGE4A_R2，原始 blend SHA-256 `4fa2cb6f31d8097110718e4d9cc424c30d1d2b7057c76abd93c338a5c7201039`；仅使用已保存 native 世界坐标、原始面/边及冻结 native independent THUMB partition。未运行 Blender。approved nail mask 不变；IP 是沿用的 native engineering estimate，IP→v284 axis 不变。

逐点记录 native XYZ、THUMB、seed edge-graph surface geodesic 及最短路径、Euclidean tip distance、IP 距离/轴投影、周向角/轴半径、area-weighted normal、1-ring/2-ring、incident faces、nail membership/proximity、normal curvature proxy 和带拟合残差的 2-ring quadratic curvature。详细记录见 FIVE_VERTEX_INDIVIDUAL_FORENSIC.json。

所有五点均 >9 mm；没有使用 >9 REMOVE 或 <9 KEEP 规则。geodesic 是 native THUMB induced edge graph 路径约定，不是连续曲面最短路径。圆润且朝向 tip 的 bulb-side 表面证据不会自动成为 cap membership；本轮判断 cap 的周向边界及合法 selected-face 支持。曲率、转角和内角阈值都是工程代理，不能独立充当解剖 authority。

| Vertex | Proposal | Geodesic mm | Euclidean tip mm | Axial depth mm | Circumferential angle deg | Nail relation |
|---|---|---:|---:|---:|---:|---|
| v1453 | REMOVE | 14.550214 | 10.813822 | 6.490463 | 231.651 | NAIL_ADJACENT |
| v2785 | REMOVE | 13.276937 | 10.961913 | 6.913326 | 215.232 | NAIL_ADJACENT |
| v2790 | REMOVE | 13.354509 | 11.160404 | 6.668812 | 17.921 | NOT_NAIL_RELATED |
| v297 | KEEP | 13.284340 | 9.693512 | 5.447803 | 332.204 | NOT_NAIL_RELATED |
| v298 | KEEP | 13.367420 | 9.213764 | 5.344341 | 269.988 | NOT_NAIL_RELATED |

全部五点沿用 THUMB identity；正的 tip-axis normal 分量及曲面证据未显示明确 shaft 信号。v1453/v2785 是 NAIL_ADJACENT；其它三点 NOT_NAIL_RELATED；五点均不在 approved distal nail-margin edge v37–v879，接近 nail 不构成 KEEP 理由。

## Individual adjudication

REMOVE 仅表示不进入 cap membership，原始模型顶点保持存在。

**v1453 — REMOVE**. The E edge v1382–v341 is already a smooth native boundary continuation (turns22.887/12.272deg), not a clear missing terminal corner. Legal support requires coupled face1220 with v2785; that addition creates concave corners at v1382/v341 and a long outward tab. Rounded skin evidence does not force this selected cap boundary to include it.

**v2785 — REMOVE**. Native rounded bulb-side evidence is retained, but legal addition is coupled to v1453 via face1220. The resulting corner turns115.272deg, with new concave endpoints and8.693155mm extra perimeter. It is not classified as shaft merely because g>9; it is excluded to preserve the selected circumferential boundary.

**v2790 — REMOVE**. Native bulb-side geometry is compatible with THUMB, but no incident face can support KEEP within E plus these five vertices. The closest supporting face1243 also requires non-disputed v1342. A KEEP vertex without selected-face support is prohibited, so it remains excluded under the authorized scope.

**v297 — KEEP**. Face1942 provides a rounded circumferential boundary completion at axial depth5.447803mm. Removing it preserves a disk/loop but introduces a concave notch at v2965 (interior279.457deg) and larger local turns. Its positive tip-facing normal and curved native surface support KEEP; no distance-threshold rule is used.

**v298 — KEEP**. Face1944 provides the corresponding rounded circumferential completion at axial depth5.344341mm. Removing it preserves a disk/loop but introduces a concave notch at v2966 (interior266.588deg). KEEP maintains the native rounded edge and does not rely on proximity to nail.

v1453：E 原边界在 v1382/v341 的 turn 为 22.887°/12.272°，没有清楚的 terminal-corner notch。最小合法加入 face1220 虽恢复一些 rounded skin，却形成面尺度外凸 tab 和两个凹角；不能据此认定 E 有缺口。

v2785/v2790：不把这些点重新归类为 shaft 或否定已接受的 distal region identity。v2785 的合法加入与 v1453 耦合；v2790 无法获得五点范围内的 selected-face 支持。因此它们的排除基于 boundary/face consistency，而非仅凭距离或“expansion tail”名称。

v297/v298：E 的 axial-face selection 纳入 face1942/1944，角点虽都超过 9 mm，仍提供圆润周向边界补全。删除后闭环依然存在，故它们不是维持拓扑闭环的必要点；KEEP 的依据是避免局部凹口。未为“为何仅 E 有”重开其它 family。

## Five independent tests and one necessary coupling check

5 个 requested independent test records，3 个 unique feasible hypothetical patches，只有一次必要 face1220 coupling check；未搜索 2^5 组合。所有假设仅存在于新审计数据。

v1453/v2785 的严格单点 add-one 都不能形成合法面。face1220=[341,1382,2785,1453] 是仅有五点范围内合法支持，需两点同时进入；分别的单点报告标注这一约束，并共用最小 coupling patch。该 patch 是 39v/26f，仍为单 disk/loop，却新增 v1382/v341 凹角（intrinsic interior 281.477°/260.463°），perimeter 增加 8.693155 mm，axial spread 增加 0.222507 mm。

v2790 四个 incident faces 全部要求未获授权的额外顶点；最近 face1243=[1450,2790,1342,285] 也需要 v1342。本轮禁止新增其它点，故报告 NON_VIABLE_KEEP_WITHIN_FIVE_VERTEX_SCOPE，不能伪造 unsupported KEEP vertex，也没有构造越界 patch。

v297 leave-one-out 仅移除 selected face1942；v298 仅移除 face1944。均保留其余已接受 E 顶点，仍连通闭环/manifold disk，但分别产生 v2965/v2966 凹口（intrinsic interior 279.457°/266.588°）。

- v1453: 39 vertices / 26 faces; perimeter 57.453619 mm; axial spread 3.989999 mm; component/loop 1/1; new concave-notch proxies [1382, 341].
- v2785: 39 vertices / 26 faces; perimeter 57.453619 mm; axial spread 3.989999 mm; component/loop 1/1; new concave-notch proxies [1382, 341].
- v2790: KEEP is non-viable within the authorized five-vertex scope; no unsupported vertex-only membership or out-of-scope face patch constructed.
- v297: 36 vertices / 24 faces; perimeter 50.236988 mm; axial spread 3.767492 mm; component/loop 1/1; new concave-notch proxies [2965].
- v298: 36 vertices / 24 faces; perimeter 49.680173 mm; axial spread 3.767492 mm; component/loop 1/1; new concave-notch proxies [2966].

## E baseline versus E_FINAL and face-level consistency

| Metric | Baseline | E_FINAL |
|---|---:|---:|
| Vertices | 37 | 37 |
| Faces | 25 | 25 |
| Max geodesic (mm) | 13.367420 | 13.367420 |
| Boundary axial spread (mm) | 3.767492 | 3.767492 |
| Area (mm²) | 182.066159 | 182.066159 |
| Perimeter (mm) | 48.760464 | 48.760464 |
| Boundary edges / vertices | 22 / 22 | 22 / 22 |
| Connected components / closed loops | 1 / 1 | 1 / 1 |
| Euler characteristic | 1 | 1 |
| Nonmanifold edges / vertex links | 0 / 0 | 0 / 0 |

face union = final vertex membership；native edge IDs 与端点逐项一致；boundary = selected face incidence 1 的边；boundary 顶点 degree 全部 2。KEEP297/298 均有 selected-face 支持，三个 REMOVE 点均无 selected membership。其它 E 顶点零改动，faces/vertices/boundary 均与 baseline 相同。

每个 boundary 点记录 3D tangent turn、selected-face intrinsic angle sum、normal-angle/edge-length curvature discontinuity、turn curvature、入/出边长及 degree。局部角 sum >240° 为 concave notch proxy，<60° 为 narrow spike proxy。五点及其 1-ring 中 E_FINAL 无该类 spike/notch；所有 baseline smoothness 数值原样保留，无其它区域重审。边界是 native polygon edge 近似，不宣称光滑解析曲线。

Self-check：单 connected patch YES；单 closed boundary YES；non-manifold incidence 0；region identity unchanged YES；没有新增 proximal overreach（本轮五点范围，并沿用 Human E baseline）；nail coherent YES（edge37–879 保留）；五点邻域无 local spike/notch。上述检查使审阅包 READY；Human 仍需判断 boundary 的视觉合理性。

## Human review and outputs

打开 [CAP_BOUNDARY_E_FIVE_VERTEX_REVIEW.html](../../../../artifacts/e0e8cebba7194e11f722.md)。六个 native closeups：DORSAL/PALMAR/RADIAL/ULNAR/THUMB_SIDE/TIP，及统一 contact sheet，所有图都标出五个 ID。仅显示 E baseline、E_FINAL 和五点裁决，保留 approved nail/IP/v284 context。蓝虚线与绿相位线区分完全重合的 baseline/final；红 REMOVE / 绿 KEEP 点仍位于原 native mesh。彩色 evidence 为 X-ray 投影，灰色 mesh 深度显示；隐藏表面不会被冒充前表面。TIP 中 IP/seed 沿轴投影重合，页面明确标注。

Q1–Q5 各点 KEEP/REMOVE；Q6 YES/NO/UNRESOLVED；Q7 APPROVE_FOR_FREEZE/REJECT/UNRESOLVED。答案初始全空，不预填 Human 判断。网页只下载本地 response；与展示 proposal 不同的回答明确记录 mismatch，不自动修改 membership 或 authority。UI 检查 PASS：六 view、每 view 五标记、四 layer 开关、七题/选项、空提交阻止、无 script error；未生成 Human response。

主要 evidence：E_BASELINE_FIVE_VERTEX_CONTEXT.json；FIVE_VERTEX_INDIVIDUAL_FORENSIC.json；E_FIVE_VERTEX_VARIANT_ANALYSIS.json；NATIVE_THUMB_DISTAL_CAP_CANDIDATE_E_FINAL.json；E_FINAL_BOUNDARY_TOPOLOGY_AUDIT.json；NATIVE_FIVE_VERTEX_VIEW_METADATA.json；UI_VERIFICATION.json；OUTPUT_VERIFICATION.json；FROZEN_HASH_VERIFICATION.json；STATUS.json 及 renders/ 六张图/contact sheet。脚本位于本轮 scripts/，均未触及既有文件。

## Freeze preservation and STOP

1502 个既有 workspace 文件和 2 个外部原始 Human response SHA-256 before == after。包含 Stage4A R2 / Stage4B RSSF / Stage4C / Stage5A R2A / Stage5B R1B / Stage5B R1E / R3 authority/evidence / Human registration、cap authority、boundary response；完整逐文件记录在 FROZEN_HASH_VERIFICATION.json。新文件仅在本审阅目录。

BLEND_FILES_WRITTEN=0；WEIGHT_DELTA=0；GEOMETRY_DELTA=0；TOPOLOGY_DELTA=0；BONE_DELTA=0；JOINT_DELTA=0；R1F_CREATED=false；Stage6_runs=0；R3_runs=0；strict_bound_recalculations=0；retopology=false。

NEXT=HUMAN_CAP_AUTHORITY_FREEZE，须先收到并核对本页 Human 五点/边界回答。本轮到此 STOP，等待 Human。production authority applied=NO，freeze performed=NO。
