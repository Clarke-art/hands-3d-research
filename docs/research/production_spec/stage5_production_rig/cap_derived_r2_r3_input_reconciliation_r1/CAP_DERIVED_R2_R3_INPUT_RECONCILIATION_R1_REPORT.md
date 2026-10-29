# CAP_DERIVED_R2_R3_INPUT_RECONCILIATION_R1

状态：**FAIL_CLOSED_UNRESOLVED_INPUT_AUTHORITY**。已完成只读 provenance、候选静态测量与输入差异审计；没有生成 canonical recompute contract，也不能进入 R3。

## 正式输入已验证

- cap37：HUMAN_APPROVED_FROZEN，37 vertices /25 faces，combined authority hash `c81dd96d6925ed402cdf0ba44c148d7a78c2c60640fe23fb6247fb729f346cc8`。
- corrected rig：HUMAN_APPROVED / APPLIED_VERIFIED，SHA256 `5d5f86bb59135715a77515468c2b76fe81e2a44e2e8c5d6c17fcc3d56d2147fe`。直接读取 live21 bones；IP head、hierarchy/origin 等保持已批准状态。THUMB_IP.tail/TIP.head 来自 corrected rig。
- Stage4C_R2：SHA256 `fde620b2cebd2b4cd894e32b58d7b59ba7fac9b00d3d2dfa5193cefb32513ab7`。corrected rig mesh 与 RSSF 的顶点/边/面完全一致；native→RSSF 顶点编号、边及 polygon 顺序完全一致。未选择或更改 cap、nail、first-web、cage geometry。
- 各 authority 文件及源码行号/摘录见 AUTHORITY_INPUT_VERIFICATION.json、SOURCE_CODE_PROVENANCE_R1.json；集合与文件哈希见 RECONCILIATION_EVIDENCE_HASH_MANIFEST_R1.json。该 manifest 是审计包，不是 input contract。

## 结果

| Input | Status |
|---|---|
| corrected_live_thumb_chain | RESOLVED |
| R2_seed | RESOLVED |
| R2_domain_guard | UNRESOLVED |
| thumb_tube_anchors | UNRESOLVED |
| thumb_strong_anchor_sources | UNRESOLVED |
| index_strong_anchor_sources | RESOLVED |
| first_web_wrapper | UNRESOLVED |
| nail_cap_wrapper | RESOLVED |
| CMC_cage_wrapper | UNRESOLVED |
| R3_unary_field_input | UNRESOLVED |
| R3_graph_domain | UNRESOLVED |
| closure_input_semantics | RESOLVED |
| validator_reuse | PARTIAL |

RESOLVED 仅表示该输入定义有唯一可追溯候选；不代表整份 contract 获批。

## Live chain 和 seed

distance/arc/tube 使用 CMC.head→MCP.head→IP.head→IP.tail (=TIP.head)。TIP.tail 是 non-deform helper 的外延，不延长解剖 tube；roll 存档但距离公式不使用 roll。未来 dT/dI 是 graph edge-geodesic 距离到 hard-source regions，不是 Euclidean chain distance。

历史 R2 seed 实际执行 `nearestvertex(mean(oldcap9))`，得到 **v1076（native INDEX）**。它不是直接读取 REP，也不是报告声称的单纯 chain terminal seed。必须 RETIRE。

候选比较：cap37 centroid 最近顶点与 cap37 induced-graph geodesic medoid 都是 **v1752**；独立 terminal landmark 是 **v284**。选择 v284 是因为 R2 初始化需要 terminal surface graph source，且 native identity、cap37 membership 与 corrected terminal kinematics 相互支持；不是把 cap centroid 当端点。JSON 记录各 XYZ、delta、native→RSSF映射及 medoid全部得分。没有运行六源 partition。

旧 AC 数值仅存入 HISTORICAL_REFERENCE_INPUT_PROVENANCE_R1.json，明确为 HISTORICAL_ONLY。它们未参与当前候选计算，future AC 由 corrected live rig替换。

## Anchor 静态检查

- 旧 THUMB_STRONG241：native THUMB169 / INDEX66 / wrist6；旧 INDEX_STRONG145 全部 native INDEX。历史集合只作差异证据。
- corrected chain +历史10.4735mm radius：raw tube219；旧cap9进入数0。不能因这9点不再进入而删除guard。
- native THUMB band重新测得10.299381mm：raw tube205，其中41个native INDEX；guard后164，metacarpal corridor5。cap37全部在该tube中，语义保留cap/tube双来源、future去重，不累计两份硬约束。
- radius采样仍包含14个native proximal interface点。去掉这些点得到10.180583mm、tube155、corridor4；变化9个tube点与1个corridor点。两种规则都确定性但authority未唯一，故thumb tube输入不能写RESOLVED。
- INDEX radius独立采样67点，全部两环稳定，8.057679980mm；INDEX tube143，nail43保持正式face mask。旧loader竞争过污染的thumb chain，因此是REVALIDATE后确认ingredients，不是机械保留历史145标签。
- 所有 geometry-only hard-pin routes 都必须先经过 independent digit guard；nativeINDEX不能仅凭thumb proximity入强锚。跨digit冲突必须在union前FAIL_CLOSED，禁止沿用先 `THUMB_STRONG -= INDEX_STRONG` 再声称零冲突。
- 未生成任何最终新THUMB_STRONG/INDEX_STRONG union。

## 四项窄范围 authority 阻塞

1. **Proximal domain/radius/graph**：native partition文件明确说明掌部Voronoi界面只是结构候选。旧graph1008依赖旧R2与anchors，不能复用。native THUMB∪INDEX953、再纳入frozenweb959只是候选；不能擅自将任一集合升级为解剖truth。必须先明确shared proximal/wrist域及采样规则。
2. **FIRST_WEB角色**：21点membership保留。既有批准明确weights locality，不能证明全部21点都应THUMB hard-pin。native evidence为THUMB5/INDEX10/wrist6，不能反过来把这个Voronoi分类当最终web truth。建议保留几何/validator保护，单独裁决shared graph及anchor角色。
3. **CMC/thenar wrapper**：cage geometry保持PASS/FROZEN。R3脚本仅记录CMC_CAGE；其旧selector及后续保护用了旧ownership或R3过滤。73点construction候选与较大的sphere/thenar保护支持域语义不同。冻结表的16个boundary坐标在pole-neighbour smoothing前，最大映射误差0.700591mm，因此没有把最近匹配自动宣布为精确authority。需要label-independent protection支持域，不能重开cage几何。
4. **Unary/pairwise单位**：dT/dI图边按米累计，TAU按毫米提取，二者容量都乘1000。10mm距离在旧代码unary容量为10，而统一mm成本为10000；pairwise约1296。执行比例与报告写出的共同mm成本不一致，差1000倍。已记录两个语义，未静默选择或修改算法。

## Closure 与 gates

closure只能接受新solved labels、新graph、新anchors：**NO HISTORICAL LABEL INJECTION**。禁止 `R3=list(oldR2)` 作为域外truth。旧closure将changed在每个target内复位，future应使用完整sweep累计变化、检测未收敛；本轮没有执行closure。

connectedness、face-component、sheet split、island、ambiguity等数学检查可保留，但输入与保护bucket必须替换。CLASS_A6条边的几何authority保留，future在corrected结果上重新验证；旧THUMB标签不作为要求复刻的目标。sheet归属要以独立INDEX tip/nail识别，不以“第二大component”或旧label决定。validator reuse=PARTIAL。

## 冻结与执行范围

本轮仅写入本目录。FROZEN_HASH_VERIFICATION_R1.json记录1633个既有workspace文件与6个外部authority/Human文件before==after。所有既有blend、Human responses、Stage4/5、historical R2/R3、Stage6保持原hash。各delta与run counts均为0。

仅cap37的固定membership内做了候选medoid距离；仅对冻结geometry做静态chain/tube测量。没有R2 ownership solve、R3 unary full field、mincut、closure、boundary generation、skin rebuild、Stage6或R1F。

CANONICAL_R2_R3_RECONCILED_INPUT_CONTRACT_R1.json **未生成**。combined contract hash = null。未生成READY_FOR_R3的Human approval页面。UNRESOLVED_INPUT_AUTHORITY_REVIEW_R1.json提供四个窄范围决定及依赖证据。

NEXT = **NARROW_PROXIMAL_DOMAIN_WRAPPERS_AND_UNARY_UNITS_AUTHORITY_REVIEW**

STOP。不得跳过未解决输入进入R3。
