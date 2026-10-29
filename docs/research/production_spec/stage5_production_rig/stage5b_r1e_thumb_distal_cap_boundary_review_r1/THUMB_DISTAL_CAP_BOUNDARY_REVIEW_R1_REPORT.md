# THUMB_DISTAL_CAP_BOUNDARY_REVIEW_R1_REPORT

**BOUNDARY=UNRESOLVED；NEXT=MANUAL_CAP_BOUNDARY_REVIEW；STOP。** 工程推荐 E 进入 Human comparison，未批准最终 boundary、未冻结 cap、未应用 production authority。全部计算只来自冻结的 native/pre-RSSF 静态 geometry/topology，未运行动态 deformation。

## Human input 与权威范围

首先读取原始文件 `<USER_HOME>\Downloads\HUMAN_CAP_AUTHORITY_RESPONSE_R1.json`，SHA256 `5c4f9749c98fd9193dc2f5d084c03174535d4a9afc80f426afe4117d0af3b99c`；本目录 source copy 逐字节相同。原样接受 Q1=YES、Q2=YES、Q3=NO、Q4=NO、Q5=UNRESOLVED、Q6=APPROVE_WITH_BOUNDARY_REVIEW。

> Human Review：v284 视觉上位于 native thumb terminal tip；48-vertex candidate 整体对应真实 thumb distal-cap 区域，未见明显侵入中段/近端，也未见明显大片 distal-cap 遗漏。由于当前 min-corner face expansion 使 28/48 个候选顶点自身 geodesic 超过 9 mm，最大 15.894139 mm，当前 33-face 外边界尚不足以直接冻结为最终 membership authority。批准候选的 branch / anatomical region identity，但要求继续进行 boundary-only review 后再冻结最终 cap membership。

CURRENT_48_VERTEX_REGION_IDENTITY=ACCEPTED_UNCHANGED。没有重新提问 thumb identity、重开 native branch identity，或将局部 shaft-edge 观察升级为 region identity contradiction。OLD_CURRENT_CAP_9=CONFIRMED_CONTAMINATED，旧九点 [151, 158, 1061, 1074, 1076, 2189, 2192, 2569, 2577] 全部 native INDEX_SURFACE，不得恢复，也未恢复。

## 候选结果

| candidate | vertices | faces | max g mm | median g mm | boundary edges/vertices | area mm² | perimeter mm | boundary axial spread mm | bulb proxy area coverage |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 48 | 33 | 15.894139 | 9.485449 | 28 | 262.877 | 71.815 | 7.895 | 81.25% |
| B | 17 | 9 | 8.818121 | 5.299689 | 14 | 73.775 | 39.939 | 2.985 | 30.58% |
| C | 23 | 12 | 11.266322 | 6.776220 | 20 | 99.298 | 58.803 | 5.938 | 38.52% |
| D | 75 | 64 | 19.363258 | 12.221454 | 20 | 497.994 | 52.533 | 1.955 | 100.00% |
| E | 37 | 25 | 13.367420 | 8.818121 | 22 | 182.066 | 48.760 | 3.767 | 80.95% |

所有 A–E patch：component_count=1、closed_loop_count=1、Euler=1、seed v284 included=YES、edge nonmanifold=0、vertex-link nonmanifold=0。边界顶点数与边界边数相同。所有周向环 absolute winding=1（方向随 loop traversal ±1）；E 的12个30° sectors 均有点，是展示指标，不是选择条件。A/B/C/D 的11/10/11/11 sectors 不表示有 surface hole。

**A — CURRENT_MIN_CORNER_9MM**：Human-accepted thumb terminal region; min-corner corner union is circumferentially uneven and includes three low-curvature near-shaft corners. Region identity remains accepted; boundary unresolved.

Rule：Fully native-thumb-branch face with min(vertex geodesic from independent native seed) <= 9 mm, connected to closest seed face

Status：`VIABLE_TOPOLOGICAL_REVIEW_CANDIDATE`。

**B — STRICT_FACE_ALL_CORNERS_9MM**：Topologically sound small disk, but misses three core vertices and reduces terminal envelope; valid strict numerical ball is not evidence of anatomical completeness.

Rule：Every corner must have native THUMB-only geodesic <=9.0 mm; retain all qualifying faces without repair

Status：`VIABLE_TOPOLOGICAL_REVIEW_CANDIDATE`。

**C — VERTEX_BALL_TOPOLOGY_CLOSED**：Minimum topology closure preserves every core vertex and every strict B face, avoids the three strong shaft-extension proxy corners. Minimality is geometric/topological, not a complete bulb guarantee.

Rule：Preserve all strict all-corner faces B; add the minimum number of A faces to cover every <=9 mm vertex, excluding faces with multi-signal distal-shaft overreach corners. Require one edge-connected manifold disk and one closed boundary loop.

Status：`VIABLE_TOPOLOGICAL_REVIEW_CANDIDATE`。

**D — CURVATURE_TRANSITION_BOUNDARY**：Global curvature/normal knee has a plausible numeric fit, but varies around the circumference and with smoothing. Broad diagnostic patch cannot establish a unique stable anatomical transition.

Rule：Fit continuous two-slope hinge regressions jointly to standardized smoothed axial normal component and normal-variation curvature proxy; use median best knee over bandwidths 0.5/0.7/1.0 local median edge length; select native-thumb faces whose centroid is distal of that knee; keep seed component without boundary repairs.

Status：`NON_VIABLE_AS_UNIQUE_STABLE_CURVATURE_AUTHORITY_DIAGNOSTIC_PATCH_ONLY`。

**E — AXIAL_CIRCUMFERENTIAL_BOUNDARY**：Closed existing-edge circumferential cut selected near the inherited9 mm region; more consistent axis depth than min-corner A, but a planar centroid prior may under-cover the asymmetric bulb.

Rule：Sweep all unique native thumb face-centroid axial depths from1 to15 mm, retain seed-connected distal sublevel patch, preserve all20 core ball vertices, require one manifold disk/closed loop and absolute projected angular winding1 about the IP-tip axis with maximum angular gap <=60 degrees. Minimize RMS boundary geodesic offset from9 mm; break ties by patch area, cut depth and face IDs. Twelve-sector coverage is a descriptive metric, not a bin-orientation-dependent selection gate.

Status：`VIABLE_TOPOLOGICAL_REVIEW_CANDIDATE`。

## C 的最小 closure 证明

B 是17点/9面的单闭环 disk，但缺核心 v880/v1755/v285。C 在保留 B 全部 faces 的前提下，允许从 A 添加 face，排除含多信号 shaft-extension corners 的 faces，要求全部20核心点、单 disk / 单闭环。每个允许 added face 最多覆盖一个缺失核心，故至少需3个 added faces。穷举3-face combinations 1540个，其中32个覆盖核心，8个形成有效disk。按 boundary axial spread→geodesic RMS→area→face IDs 排序得到 added faces [78, 1050, 1940]。这证明限定域内最低补面数，不声称全球最小 anatomical cap。没有自由手选顶点或补造新面。

## D 的 curvature transition 与限制

从 native area-weighted normals 计算 normal dot(IP→tip)，并计算一环 median normal-angle/edge-length curvature proxy。另对两环点拟合 quadratic surface，输出 principal curvature proxies、RMS、rank 与样本数。以 native edge median 3.318625 mm 的0.5/0.7/1.0倍为平滑带宽，对1–23 mm轴深 profile 联合拟合连续双线性 hinge，搜索3–14.5 mm knot。

全局最佳 knees 为9.5/10.0/11.5 mm；median10mm生成诊断 D（64 faces /75 vertices）。十二周向窗口35° Gaussian 下，带宽/方向的最佳 knees 为7.5–14.0mm，跨度6.5mm 大于一个 local median edge。没有唯一稳定的全周 curvature crease。因此 D 标记 **NON_VIABLE_AS_UNIQUE_STABLE_CURVATURE_AUTHORITY_DIAGNOSTIC_PATCH_ONLY**，保留未经修补的诊断 patch 供 Human 看清失败范围。D 的连通闭环只是拓扑事实，不能反证这一限制。

## E 的 deterministic axial circumferential rule

使用既有 native IP→tip engineering axis，以tip为轴深0；扫描 native THUMB faces 的1–15mm唯一 centroid-depth thresholds。每阈值取 distal sublevel 的 seed-connected component；必须保持20个核心点、一个 manifold disk / closed loop、absolute angular winding=1、最大角间隙≤60°。最小化 boundary geodesic 对9mm的RMS偏差，随后以area→cut depth→IDs破同分。最终 centroid-depth cut=4.904543 mm，37点/25面。并非逐点手选，也不是新增切面/retopo；face角点可跨越这一 centroid plane，最大 corner轴深6.690820mm。

E 加入 A 之外 v297/v298，通过 faces1942/1944：两点 g=13.284340/13.367420mm，轴深5.447803/5.344341mm，normal轴分量约0.473/0.469，符合 tip-facing rounded surface proxy。它们只属于新审阅候选，不登记新的 authority。

**E 未包含暂列 rounded-bulb corner 类的 v1453/v2785/v2790。** E80.95%与A81.25%的 bulb proxy 面积近似，不代表逐面或逐点相同。Human 需判断上述新增与遗漏是否合理或需 narrow fix；本轮不会为保留 E 而改写分类。这是推荐的明确未解决限制。

## 28 个 expansion vertices 分类

全部48点/33面的 CURRENT_CAP_BOUNDARY_FORENSIC.json 包含 vertex/face IDs、g、Euclidean tip距离、world XYZ mm、area-weighted native normal、curvature proxies、nail/边界 membership、IP距离、轴投影/深度、周向角、1-ring、exact2-ring、selected/native face incidence。face rows另含几何面积、最大边长、native normal与各候选归属。

分类仅为 **PROVISIONAL_ENGINEERING_FOR_HUMAN_BOUNDARY_REVIEW**。“A/D REQUIRED”是暂定保留解释，不能自行注册为 Human anatomical necessity。E 保留未决情形；没有 >9mm→DELETE 规则，也没有 connected→15.89mm acceptable 规则。

统计：A=15、B=5、C=3、D=1、E=4。

- A / ANATOMICALLY_REQUIRED_BOUNDARY_CORNER：v339, v340, v341, v1340, v1344, v1378, v1380, v1450, v1452, v1453, v1454, v2785, v2790, v2965, v2966
- B / MESH_FACE_COMPLETION_ONLY：v881, v889, v2496, v2740, v2743
- C / PROXIMAL_OVERREACH：v39, v882, v886
- D / NAIL_EDGE_REQUIRED：v37
- E / UNRESOLVED：v44, v1339, v1342, v2499

分类依据同时包含轴深、native法线朝向、normal-variation curvature、nail关系、mesh resolution、face admission、各候选归属、core retention与boundary topology。C类要求轴深超过最低profile knee9.5mm、normal轴分量<0.15、normal variation<0.08rad/mm三项共同成立；这些工程阈值须 Human 验证，不能把它们当人体固定常数。A类要求短轴深、tip-facing法线与曲率代理共同支持 rounded envelope；沿周向较长的geodesic并不把其自动判为shaft。

## v882 与其余 >13mm 顶点

v882仅通过 **face67=[882,2496,880,39]** 的 corner union 纳入：其中 core v880 g=8.826592mm，故 face满足min-corner9mm；v882自身g=15.894139mm。face67不是 approved nail face，虽v882也是邻接approved nail的顶点。

v882 tip Euclidean=11.951136mm，IP Euclidean=11.722515mm；轴深11.154648mm，IP→tip投影10.909349mm，仍在IP distal侧。normal dotaxis=0.039780，median normal variation=0.042974rad/mm；两环quadratic RMS=0.097030mm。它对应 distal nail margin / near-transverse distal-shaft continuation，不是靠一个长距离就作出的分类。暂定 **C/PROXIMAL_OVERREACH** 指 terminal cap边界的局部shaft尾角，不指middle/proximal thumb identity，也不撤回Human Q3=NO。

| vertex | g mm | axial depth mm | normal axial | normal variation rad/mm | provisional class |
| --- | ---: | ---: | ---: | ---: | --- |
| 39 | 13.007251 | 10.675774 | 0.0237 | 0.0600 | C |
| 881 | 13.380550 | 7.778866 | 0.0067 | 0.0574 | B |
| 882 | 15.894139 | 11.154648 | 0.0398 | 0.0430 | C |
| 886 | 15.070941 | 10.487242 | 0.0200 | 0.0599 | C |
| 1453 | 14.550214 | 6.490463 | 0.4087 | 0.1308 | A |
| 2740 | 13.177649 | 8.028273 | 0.0764 | 0.0902 | B |
| 2785 | 13.276937 | 6.913326 | 0.3692 | 0.1387 | A |
| 2790 | 13.354509 | 6.668812 | 0.3875 | 0.1482 | A |

v1453/v2785/v2790虽g>13mm，仍有tip-facing curved-bulb证据，因此暂列A；这直接展示分类不是距离截断。其余逐点判据及face-admission证据全部在classification JSON。

## Approved nail relation

12-face approved nail冻结，native轴深3.737248–19.631122mm。不能要求 entire nail 必须在terminal cap内。distal margin proxy为v37/v879：A/D/E均包含；B/C只含v879。E的闭环边界沿 approved nail distal margin **edge v37–v879** 相接，未选入approved nail整面，也没有给nail创建内部孔或拆开nail权威。A选入distal nail face65；D选入64/65/1040，连成一个nail intersection component，但其shaft延伸问题独立存在。B/C虽未修改nail，对完整distal-margin关系偏小，需Human判断。

Nail-compatible工程关系：A/D/E；其中D仍不成立为稳定curvature authority。B/C属于distal nail-margin proxy partly omitted。这些关系不等同于 final anatomical boundary approval；v882 nail membership不能强制cap保留。

## ENGINEERING_RECOMMENDATION（E，仅供 Human）

- GEOMETRIC_REASON：E keeps all20 <=9mm core vertices and80.95% of the rounded-tip proxy face area, close to A81.25%, while reducing boundary axial spread7.895 to3.767 mm and avoiding the3 low-normal/low-curvature shaft-extension corners. All12 angular sectors are occupied.
- ANATOMICAL_REASON：E retains the distal nail-margin edge v37-v879 without treating the entire19.63mm-long approved nail as terminal cap. It follows the terminal envelope more evenly than A and avoids the strong distal-shaft tails; this is a provisional native-anatomy interpretation.
- TOPOLOGICAL_REASON：One edge-connected manifold disk, one closed boundary loop, seed included, Euler characteristic1, no edge or vertex-link nonmanifold incidence. C has the same topology but covers substantially less of the rounded terminal envelope.
- LIMITATIONS：Engineering IP/axis estimate; circumferential ring is an existing-face centroid staircase. Rounded bulb coverage is a resolution-dependent proxy, not a ground-truth mask. E omits the provisional rounded-corner vertices v1453/v2785/v2790 and adds v297/v298 through native faces1942/1944; these differences explicitly require Human judgment. D transition is not stable around the circumference. Human has not selected or approved a final boundary.

没有使用 Stage6 stretch、历史deformation Gate、权重或strict bound来选边界。旧13.1646mm /5.9643 /6.5160继续保持 INVALIDATED AS ANATOMICAL CAP-ENDPOINT EVIDENCE，没有replacement bound。

## 审阅页与核验

THUMB_DISTAL_CAP_BOUNDARY_REVIEW.html：六方向切换；A/B/C/D/E/nail/core/expansion/vertexID/faceID开关；boundary-only；local tip closeup。灰色表面深度测试，彩色面/点/边为明确标示X-ray。方向为DORSAL(-Y)、PALMAR(+Y)、RADIAL(+X)、ULNAR(-X)、thumb side、tip axial。所有required7张PNG已验证并检查六视角和forensic图；浏览器真实运行测试全部开关、viewBox缩放、空答案拦截、脚本无错误，截图另存。Human Q1–Q7初始为空，测试没有生成Human verdict；无网络提交或自动freeze。

页面只问用户指定boundary Q1–Q7，不重新问region身份。Q6=A/B/C/D/E/UNRESOLVED；Q7=APPROVE_FOR_FREEZE/APPROVE_WITH_MINOR_BOUNDARY_FIX/REJECT/UNRESOLVED。

## 冻结保护与 STOP

1467个既有workspace文件（包括所有Stage4A R2、Stage4B RSSF、Stage4C、Stage5A R2A、Stage5B R1B/R1E、R3 evidence/authority、旧Human registration response及全部审阅材料）与1个原始外部Human cap response，逐文件hash before==after。新增文件全部在本轮review目录。source copy bytes与原始response一致。完整记录见FROZEN_HASH_VERIFICATION.json。

BLEND_FILES_WRITTEN=0；WEIGHT_DELTA=0；GEOMETRY_DELTA=0；TOPOLOGY_DELTA=0；BONE_DELTA=0；JOINT_DELTA=0；R1F_CREATED=false；Stage6_runs=0；R3_runs=0；retopo=false；production_authority_applied=false。

**STOP — WAITING FOR HUMAN BOUNDARY REVIEW。BOUNDARY=UNRESOLVED；NEXT=MANUAL_CAP_BOUNDARY_REVIEW。**
