# NARROW_PROXIMAL_DOMAIN_WRAPPERS_AND_UNARY_UNITS_AUTHORITY_REVIEW_R1

**FAIL_CLOSED**。R3 单位候选裁决为 **CORRECTED_COMMON_MM_SEMANTICS**；独立 proximal exclusive/shared extent 仍未唯一成立。没有 canonical graph、corrected radius、最终 hard-source 集合或可执行 unary input contract。Human Review 页面不生成。

本轮所有产物独立写入 `audits/narrow_proximal_domain_wrappers_and_unary_units_authority_review_r1`。production、既有 authority/Human response、Stage4/5、R2/R3、Stage6 未改写。已解决的 cap37、corrected live rig、v284 seed、index ingredients、nail/cap wrapper、closure 输入语义均保留，不重新裁决。

## 单位裁决与 provenance

R3 实际使用 `ADJ=world edge length`（m），Dijkstra 累计 m，之后 `round(d*1000)` 得到旧 unary。TAU 则先在 `r1a_common.py` 从 edge length×1000 取 upper median，单位 mm；`round(TAU/3*1000)` 得到 pairwise。TAU=3.888204946698 mm，TAU/3=1.296068315566 mm，整数 P=1296。

U1 精确描述历史执行，但若使用报告的 mm 成本单位，其能量实为 `Σ min(0.001*d_mm,400) + (TAU_mm/3)*cut_edge_count`，随后统一×1000量化。这个0.001距离权重未被设计文件声明。等价地，以真实 mm 距离作为 unary 尺度，旧一条边的惩罚为1296 mm，旧finite cap为400000 mm。

U2 的设计 intent 由已记录的数学 contract 确认：报告把 unary 定义为物理测地距离，把 pairwise 定义为 TAU/3 mm；参数 JSON 明确 CAP_MAX_mm=400；前序 `_r3_geo.py` 实际返回 mm；正式 ambiguity 判据也实际将 dT/dI ×MM 后与 TAU 比较。它们共同支持共同毫米成本。仅 terminal-capacity 和复制的复算实现漏掉 m→mm 换算。此判断不是只依赖注释，也未比较哪组单位复现旧边界。记录中的设计 contract 与执行相矛盾，**historical unit bug=YES**；不声称已获 Human 批准，也不推断未记录的主观想法。

U3=NOT_SUPPORTED：没有发现共同 reference scale、无量纲 lambda 或相应量化测试的历史定义。数学上能构造归一化能量，不代表存在其 authority。

历史测试审查：`recompute(None)` 是同公式复算，两个结果一致不能检测单位错误；历史 expected P=1296、flow=33529 和1008点只作 execution evidence。没有发现独立单位测试或单位负控。新审查只做 scalar conversion、400mm cap反例、双向边容量真值表，不执行 graph distance field 或 solve。来源文件 hash、行号、摘录、搜索范围与局限见 `R3_COST_UNIT_PROVENANCE_AUDIT.json`。

| 物理距离 mm | 旧 unary capacity | 旧单边 pairwise | unary/pairwise | 共同mm unary |
|---|---:|---:|---:|---:|
| 1 | 1 | 1296 | 0.000771605 | 1000 |
| 5 | 5 | 1296 | 0.003858025 | 5000 |
| 10 | 10 | 1296 | 0.007716049 | 10000 |
| 20 | 20 | 1296 | 0.015432099 | 20000 |

历史 finite local scale verdict=**PAIRWISE-DOMINATED**。10mm的 unary 为10，一条pairwise为1296，倍率129.6；1–20mm范围倍率64.8–1296。此结论指局部代价尺度，不等于每个全局能量的pairwise总和都占多数；真正的换标签取舍看 unary 差值和多条边，hard pins又是单独约束。新解不得以历史labels、边界数量或flow为目标。

## 四角色与 static topology

角色必须区分 graph membership 与 source membership。SHARED_NEUTRAL 不提供源；OUTSIDE 不入图。native Voronoi只是结构证据，其两环侵蚀也不能自动成为 biological exclusivity。为可复查地比较family，本轮用“两环全同native分支且不在frozen web”作为**结构exclusive代理**，不写canonical role map。G3仅在原始边图上加1或2环，限定native THUMB/INDEX/wrist候选域，所有新增点为shared候选；cage不强制扩图。没有把可运行性当authority。

| Family | V | E | components | native wrist候选 | surface wire edges | 审查 |
|---|---:|---:|---:|---:|---:|---|
| G1 | 794 | 1535 | 2 | 0 | 3 | NON_VIABLE |
| G2 | 815 | 1573 | 2 | 6 | 7 | NON_VIABLE |
| G3_K1 | 892 | 1727 | 2 | 12 | 3 | NON_VIABLE |
| G3_K2 | 963 | 1882 | 1 | 19 | 1 | CONNECTIVITY_PASSES_ONLY_AUTHORITY_UNRESOLVED |
| G4_HISTORICAL_COMPARISON_ONLY | 1008 | 1977 | 1 | 150 | 0 | CONNECTIVITY_PASSES_ONLY_AUTHORITY_UNRESOLVED |

G1、G2、G3_K1断开必要的双源连接，NON_VIABLE。G1/G3_K1另有无outside landmark的complement小岛候选。G3_K2为963点/1882边/1组件，能从各点到达两类既有source ingredients，但仍有1条surface wire edge及1个无完整incident face的点。edge-graph连通不等于完整surface support通过；没有因此忽略潜在holes。其19个native wrist候选中没有wrist seed或其两环邻域；到独立native wrist seed最小欧氏距离57.287396mm。这只能排除某些明显泄漏，不能证明所有274个双链proximal候选的anatomical role正确。G4历史1008点/1977边只作comparison。

因此 graph candidate **未选定**。支撑环宽、exclusive/shared界面与contact-facing表面没有唯一独立依据；仅靠两环能连通不能批准G3_K2。

## Radius population 与来源

旧候选可复现：全native thumb MCP..IP sample=116，radius=10.299380996mm；两环稳定sample=102，radius=10.180583158mm，14点差异来自确定性邻域条件，非手工黑名单。

新反例：全band包含5个frozen web点；两环band仍包含 **[1396, 1399, 1402, 2774]** 共4个web点。按FW1默认shared-neutral排除它们后，两环sample=98，radius=10.149389548mm；raw tube191、provisional guard后152、corridor4，native INDEX冲突0。零冲突是代理guard的静态结果，不能称为最终corrected anchor count。0/1/2/3环并排敏感性与全membership均在radius JSON。第一环排web也恰好得到10.180583mm，进一步表明数值相同不证明population authority相同。

sampling必须排除first web、shared proximal interface及index-facing contact surface；现有稳定性谓词不足以完成这些语义，故 radius/sample/source均 **UNRESOLVED**。corrected radius与anchor count为null。cap37不重新选择：多provenance标签保留，future仅做unique-vertex union，一个ID一份hard constraint，禁止重复INF/容量/权重。index nail43、tube143及其145点unique ingredients保持。

## Wrappers

FIRST_WEB_21 membership保持；逐点记录native candidate、历史角色、批准的skin-weight角色、两条corrected chain距离/弧长及真实拓扑邻接。建议FW1 **SHARED_NEUTRAL_GRAPH_ONLY**。没有支持FW2独立exclusive子集的authority；FW3历史硬pin不能从权重批准推导。shared-neutral是solver输入角色，不等于要求未来二元label仍为第三类，更不能从未来label回推anatomical exclusivity。

CMC cage geometry保持FROZEN/PASS，建议 **CAGE_GEOMETRY_PROTECTED_BUT_NOT_R3_HARD_SOURCE**；是否入图由最终domain决定，不因cage身份自动入图。全冻结mesh几何/topology/hash保护无需近似73点映射。局部deformation保护mask如果未来需要，应另依exact topology provenance确认；本轮不批准它。73点construction候选和120点unfiltered历史sphere不同；16点坐标受既有pole-neighbour smoothing影响，不把0.700591mm最近映射宣称为精确authority。旧R3仅加载/log cage，无直接cage hard-source条目。

thenar/palm仅作为有限graph-support或validation候选。历史thenar依赖own_r1a与ring expansion，skin locality批准不构成冻结ownership，历史sphere不可整体作THUMB pin。

## Unary、pairwise、INF 与 validators

`R3_UNARY_FIELD_INPUT_CONTRACT_R2.json` 是**阻塞记录，不是可执行input contract**；graph/source IDs均null，没有计算dT/dI。未来仅允许approved graph到unique THUMB/INDEX sources的edge-geodesic，单位统一mm；shared不作源，outside不入图，unreachable在cap前fail closed。

pairwise数学contract已形成候选：所有finite成本同一mm尺度；nearest/ties-even量化×1000，TAU/3单边1296，不乘边长，双向编码cut只计一次。400mm finite cap对应400000。未来只有domain/anchors一起获批才可组装solve输入。

保守严格界：`B=|V|*400000+|E|*1296`，每点最多付一个terminal finite cost，每条无向边最多付一个pairwise。source disjoint且可达时有pin-respecting assignment成本≤B，而任何违反pin的cut成本≥INF；因此取 **INF=B+1**。它是上界，不是声称求出了可同时达到的exact最大cut。G3_K2：unary上界385200000、pairwise上界2439072，故 **INF>387639072**，建议387639073。G1/G2/G3_K1/G4各自界见JSON；这些数值均非canonical graph的INF。

validator复用=**PARTIAL_WITH_DEFINED_UPDATES**。组件、face、sheet、island及ambiguity数学可复用，必须替换source/graph/shared/CLASS_A输入。INDEX sheet以独立native tip **v233** 与固定INDEX nail faces/vertices识别，禁止“第二大component”或旧tip代理。THUMB counterpart用v284/cap37/thumb nail；body身份另检查独立wrist v2260。多匹配、无匹配、anchor family被拆散均fail closed。六条CLASS_A只保留有效几何身份，不强制复现旧THUMB|THUMB。没有执行sheet split或closure。

## 结论与冻结

唯一NEXT authority问题：**PROXIMAL_EXCLUSIVE_SHARED_EXTENT_AUTHORITY**。需要以独立cross-section/branch/palm evidence确定exclusive/shared界面和有限支撑extent；它下游决定采样population、tube/corridor、THUMB sources、graph和unary。不得用旧labels、最近winner或“能跑”的G3代替。无需逐点Human审批；目前也不提交不完整的六问页面。

R2 runs=0；R3 runs=0；Stage6 runs=0；skin rebuilds=0；BLEND_FILES_WRITTEN=0。WEIGHT/GEOMETRY/TOPOLOGY/BONE/JOINT DELTA全部0。所有既有文件before==after证据见 `FROZEN_HASH_VERIFICATION_R1.json`，新产物hash见 `OUTPUT_HASH_MANIFEST.json`。

**STOP。FAIL_CLOSED；不进入CANONICAL_R2_R3_INPUT_CONTRACT finalization。**
