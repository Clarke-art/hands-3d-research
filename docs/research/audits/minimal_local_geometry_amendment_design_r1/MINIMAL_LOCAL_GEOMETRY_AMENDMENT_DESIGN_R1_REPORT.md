# MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R1

**FAIL_CLOSED_POSITION_ONLY_GEOMETRY_DESIGN**。3个候选全部未达到完整要求，**RECOMMENDED_CANDIDATE=NONE，RECOMMENDED_WRITE_VERTEX_COUNT=0**。禁止应用或自动转入retopo。

## Root与正确source layer

ROOT_CAUSE_CLASS=BASE_GEOMETRY_CONTOUR_DEFECT。完整继承上一轮诊断：Stage4C raw/RSSF/R2 BIND/IDX15均可见；shading仅强调，armature zero只有浮点误差，skin不是静态根因，原INDEX poses没有支持放大。上一轮所有诊断文件保持原hash。

RECOMMENDED_AMENDMENT_SOURCE_LAYER=NEW_VERSION_DERIVED_FROM_FROZEN_STAGE4C_R2_RSSF_GEOMETRY。现有frozen Stage4C_R2是生产lineage geometry baseline，包含现有CMC/RSSF；未来必须新建派生geometry版本，再明确派生corrected Stage5A/R2候选，不能原位覆盖。Stage4A_R2_BASE_PRE_CMC_RETOPO只作earliest defect evidence，不回填改写历史。本轮仅mesh coordinate copies / temporary rig evaluation，无blend save。

## 方法与candidate scope

A：15core-only，graph biharmonic tangent fairing；normal方向75% curved quadratic ring-fit shallow-valley target+25% biharmonic height。6mm Gaussian width与0.65mm offset为设计参数，不是人体阈值。保留curved valley，未以平面或normal/material伪修复。

B：core+3300/3308/3347，18点。初版无非邻接contact，但完整quad检查发现bow-tie；加入面方向可行性约束后仍有新contact/bow-tie，失败。

C只在A/B失败后创建：15core+16诊断1-ring+3 directly incident2-ring点3315/3306/3338，34点局部支持池。确定性按初始位移/vertex ID排序逐点恢复，比较bow-tie/reference reversal、global max角、固定ring reference深度与主折边，恢复12点到22点（12core/7ring1/3ring2），包含恢复3个原core点80/2096/3323。没有默认write52或默认core15必须全部改。恢复顺序、每点trial接受/拒绝理由、所有candidate position vectors/幅度/新坐标在GEOMETRY_AMENDMENT_CANDIDATES_R1.json。

最终逐边检查揭示：仅限制global max角的缩减准则不足，会让锐折迁移到边界。因此22点不是合格最小write set，也不是全局最小集合证明。

## 必需数字

CANDIDATE_COUNT=3；CANDIDATE_A_WRITE_VERTEX_COUNT=15；B=18；C=22。TOPOLOGY_CHANGED_ANY_CANDIDATE=NO。RET0PO_REQUIRED=NO：当前有限方法失败不证明需要retopo。POSITION_ONLY_INSUFFICIENT=NOT_PROVED_GLOBALLY。

BASELINE_MAX_DIHEDRAL_DEG=178.227633629。

| Candidate | 点数 | MAX_VERTEX_DISPLACEMENT_MM | mean mm | RMS_VERTEX_DISPLACEMENT_MM | MAX_DIHEDRAL_DEG（BIND，同域） | edge6676° |
|---|---:|---:|---:|---:|---:|---:|
| A | 15 | 2.157403177 | 1.085690873 | 1.200962247 | 171.239558515 | 9.041967021 |
| B | 18 | 2.470027226 | 1.086424721 | 1.215761482 | 171.239558515 | 31.679973652 |
| C | 22 | 3.107465157 | 1.480071384 | 1.715686223 | 169.036002634 | 0.797572528 |

全比较域包括所有candidate incident faces及诊断面，各方案同域。每点design world-mm displacement和actual float32-preview displacement完整保存于CANDIDATE_WRITE_SET_COMPARISON_R1.json。actual22点之外精确0；design-to-float32最大误差约0.000060mm。C完整ids=`[79, 955, 962, 2089, 2238, 2327, 2328, 2531, 2609, 3025, 3300, 3306, 3308, 3315, 3316, 3324, 3331, 3332, 3338, 3339, 3340, 3347]`，仅作为失败设计证据，无写入授权。

## 最小失败原因与最终gate

A/B中心notch减弱，但引入新的local exact contact（独立包含shared-topology检查分别3/6对）及projected quad bow-tie。因此它们不合格，不因小scope或好看的solid而推荐。

C中心原尖notch在实体/grazing中消失，接触/degenerate/reference-reversal/bow-tie检查也pass；但出现两个新过渡折边：

* edge6675，faces3344/3345：baseline27.929° → C153.910°。
* edge6602，faces3298/3301：baseline25.669° → C116.906°。

展开的旧向内face连接到仍向内的boundary face，从原近同向facet变成新的相向facet界面。该现象在实际geometry中，普通matched boundary实体及grazing/side图可审阅。acute/obtuse只是法线dot product几何符号，不是人体阈值；完整手表面机位下部分边界facet遮挡，不能仅靠该实体机位宣称新增可见产品瑕疵；Human-visible严重性仍由Human决定。但是实际vertex/facet的新sharp transition已不满足“不得把缺陷推到边界”，因此C拒绝。C整体max仍169.036°（旧边界edge6689），不能用global max下降隐藏新edge6675。

各candidate VISIBLE_DENT_STATUS=CENTRAL_NOTCH_REDUCED_OR_REMOVED_BUT_CANDIDATE_REJECTED。NEW_VISIBLE_DEFECT：A/B有新local contact/quad bow-tie，具体视觉severity由Human；C有新boundary sharp fold，不能宣称无新问题。BIND_PREVIEW / IDX_MCP_15_PREVIEW / IDX_MCP_30_PREVIEW / IDX_MCP_45_PREVIEW：A/B=FAIL_NEW_LOCAL_STRUCTURAL_DEFECT，C=FAIL_NEW_BOUNDARY_SHARP_FOLD。C的contact-only PASS不等于overall contour PASS。

进一步在相同34点支持池尝试完整边界orientation约束：all-positive target碰到face3316三角[3346,3322,3330]的三个fixed vertices，当前fixed-boundary约束不可满足；保留该固定triangle原绕向后，4000次projection仍未收敛（remaining signed-area deficit2.4778756mm²）。非收敛不是所有position-only方法不可能的证明。该refinement未构成第4个Human candidate，没有新增topology或扩大正式写入权限。

## RSSF / Bind / smoke与证据

每candidate均以source原flat flags/material/UV matched普通实体为主，提供原Human机位、完整右手dorsal、close、grazing、额外角度、wire、actual0/60/120degree sections及side silhouette。Stage4/RSSF raw与temporary downstream BIND展示均有。相同camera/scale/light/material/pose比较；normal仅自然随顶点几何重算，不改flags作为伪修复。

source R2 existing weights/rig只临时绑定到copy。Baseline4states与原FullStage6A保存坐标全mesh精确一致。C所有22个write vertices与15 diagnostic core在IDX15/30/45相对BIND坐标精确不动；因此失败是静态边界问题，不是被INDEX pose再放大。仅4-state diagnostic preview，不是Full42 qualification。

BVH/既有exact kernels之外，独立float64 AABB+双向edge/triangle clipping+coplanar area clipping检查candidate incident region against whole mesh；包括sharing vertex/edge native faces，只排除真正公共点/边本身合法接触。C无新contact，仍因boundary fold失败。数值容差属于计算几何，不是Stage6或生理gate。

三截面保留native face ID及world/profile segments，native quad fan triangulation，固定diagnosis frame/axes。plane/quadratic residual、umbrella curvature、normal angles均保存。C移动3个2-ring点，refit quadratic depth1.652734mm与冻结baseline ring-fit reference depth0.747559mm都保留（baseline1.546247mm）；不能把reference变化掩饰为真实深度，也不能以中心depth改善代替边界连续性。

## Frozen gate与条件downstream plan

所有candidate vertex/edge/face count unchanged：3416/6828/3414。face winding、2-face incidence/manifold、UV/material assignment、原normal flags、自定义normal状态、全部weights/21-bone rest不变。native计数/绕序不变不保证contour，故C仍失败。

各write set分别核对nail/cap37/oldcap9/FIRST_WEB21/fresh R3 bounded graph/historical317/CMC20mm context，交集空。没有重开authority研究。原9对severe exact crossings未重新裁决；局部contact减少仅记INCIDENTAL_DIAGNOSTIC_EFFECT，不用作排名目标。

无推荐candidate或future write scope。条件downstream plan仍说明未来若另一个设计经Human批准：MUST_REVALIDATE Stage4所有incident/boundary contour/manifold/winding/UV/material、Stage5 geometry propagation/joint-surface alignment/rest/bind/zero/static skin、geometry-derived true-cap paths/bounds、targeted deformation/Full42/Human product review；LIKELY_HASH_NUMERIC_RECOMPUTE new geometry/blend payload与相关path/edge/bound数值；NO_RESEARCH_REOPEN anatomy、R3/cap37/FIRST_WEB/CMC、317、bone/joint、retopo。当前不执行这些阶段。

## 零漂移与STOP

PRODUCTION_DRIFT=0：本轮前已有2896个工作区文件全部SHA256一致，changed/missing/目录外added均0。全部frozen资产、历史blend、Human receipts、上一轮诊断与FullStage6A失败证据不变。无正式geometry/weight/bone/RSSF edit，未Full42 rerun、Stage6B或promotion。

RECOMMENDATION_REASON=All3 candidates fail at least one required structural/contour condition。RECOMMENDED_CANDIDATE=NONE。RECOMMENDED_WRITE_VERTEX_COUNT=0。不自动进入更大scope、topology/retopo或正式geometry amendment。

**STOP — HUMAN REVIEW**
