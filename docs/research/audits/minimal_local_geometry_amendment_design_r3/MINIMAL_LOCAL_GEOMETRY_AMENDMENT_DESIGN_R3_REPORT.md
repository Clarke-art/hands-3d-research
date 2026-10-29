# MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R3

**FAIL_CLOSED_R3_GEOMETRY_DESIGN · D_OPTIMIZER_NONCONVERGENCE · STOP — HUMAN REVIEW**

本轮完成read-only因果分析、真实参照提取、两种position-only目标、collision-aware S3–S5设计求解和普通实体证据。没有合格Human candidate，没有应用、生产修改、topology/retopo、weight/bone/joint/RSSF改动、fresh ownership R3重跑、Full42、Stage6A/6B或promotion。

## 最终字段

{
  "FACE204_207_BASELINE_RELATION": {
    "shared_vertex": false,
    "shared_edge": false,
    "minimum_separation_mm": 0.024319952062078574,
    "normal_angle_deg": 5.955192279372143,
    "closest_features": "Vertex2531 to face207 fan interior; signs to native face207 plane are mixed, so a single face-plane sign is not a universal side predicate."
  },
  "INTERPOLATION_FIRST_NEAR_FRACTION": 0.7147023015545526,
  "INTERPOLATION_FIRST_EXACT_FRACTION": 0.7359184860853838,
  "INTERPOLATION_FIRST_CROSSING_FRACTION": 0.735918763665786,
  "HEALTHY_REFERENCE_AVAILABLE": true,
  "REFERENCE_REGION": [
    "INDEX_MIDDLE_DORSAL_ROOT:face2795",
    "RING_LITTLE_DORSAL_ROOT:face2822"
  ],
  "TARGET_FAMILY_COUNT": 2,
  "SUPPORT_DEPTHS_TESTED": [
    3,
    4,
    5
  ],
  "FIRST_STRUCTURALLY_FEASIBLE_SOLVE": null,
  "R3_CANDIDATE_COUNT": 0,
  "RECOMMENDED_CANDIDATE": "NONE",
  "TOPOLOGY_EXPRESSIVITY_LIMIT_EVIDENCE": "NOT_FOUND",
  "TOPOLOGY_CHANGE_REQUIRED": "NOT_PROVED",
  "POSITION_ONLY_INSUFFICIENT": "NOT_PROVED_GLOBALLY",
  "RET0PO_REQUIRED": "NO",
  "PRODUCTION_DRIFT": 0,
  "BIND_PREVIEW": "NOT_RUN_NO_QUALIFIED_CANDIDATE",
  "IDX15_PREVIEW": "NOT_RUN_NO_QUALIFIED_CANDIDATE",
  "IDX30_PREVIEW": "NOT_RUN_NO_QUALIFIED_CANDIDATE",
  "IDX45_PREVIEW": "NOT_RUN_NO_QUALIFIED_CANDIDATE",
  "NEXT": "POSITION_ONLY_FORMULATION_RESEARCH_AFTER_HUMAN_REVIEW",
  "STOP": "HUMAN REVIEW"
}

## 204/207形成过程

分析在任何R3试解坐标生成前完成。Native204=[3316,3324,2531,2089]；207=[3300,3308,1107,181]，无共同vertex/edge。记录各自incident faces、完整1-ring/2-ring vertices/faces、native edges。Baseline最近距离0.024319952062mm，normal夹角5.955192°；2531最近于207 fan[3300,3308,1107]内部，barycentric约[0.251671,0.719736,0.028593]。

Native face207平均平面上的204各顶点signed distances有正有负，说明不能用一个face-plane符号冒充完整side relationship；实际局部closest-feature side轴和原生fan triangles必须动态更新。101点确定性插值和40轮二分分别给near t0.714702301555、exact t0.735918486085、crossing t0.735918763666。容差1e-3/1e-8/1e-7mm均为COMPUTATIONAL_GEOMETRY_TOLERANCE。

Both face fields are required in the face-motion counterfactual. Tangent-X or tangent-Y alone produces a crossing, while normal-only does not. Restoring 3308 or 3324 individually removes it; no individual moved vertex alone creates it. Starting at vertex2531 versus face207 interior with 0.024319952mm separation, relative tangential motion changes the closest feature ordering and exhausts the separation at t=0.735918486. Face rotations are only 5.778deg and0.738deg. Therefore the observed recurrence is a jointly driven local tangential side/feature reordering, rather than a large-normal-rotation event or one uniquely faulty vertex.

R2 S3/S4/S5的8个相关点均保存baseline/failed xyz、world/frame displacement及contact features。Face204-only与207-only均无该crossing，双方移动才有。Normal-only不cross，tangentX-only及tangentY-only都cross；单点移动不足，恢复3308或3324分别去掉crossing。因此这不是只由一侧或大法线旋转驱动的机制。

## 两个健康同手形态参照

Frozen Stage4C_R2 source与当前冻结21-bone rig只读。邻接INDEX/MIDDLE及RING/LITTLE的bone-pair frames、head/tail和unaffected surface ray landmarks建立对应区域预测。比较确定性longitudinal位置，以没有核心obtuse/bowtie且接近对应valley位置为筛选；不按minimum depth选肩部，不假设ID镜像或严格解剖同源。

采用INDEX_MIDDLE_DORSAL_ROOT face2795（局部width proxy11.632932mm、depth diagnostic0.853815mm）和RING_LITTLE_DORSAL_ROOT face2822（width7.266260mm、depth0的浅肩/谷过渡）。普通实体、grazing及真实wire均已检查：无核心异常对向折边。每个记录bone/surface frames、valley axis、0/60/120°原生截面、width/depth proxy、normal progression、boundary slope、curvature fit、native side/tangent silhouette envelope和unaffected landmarks。

Rigid/similarity alignment使用frozen joint-spacing比例、bone frame和选定surface landmarks；normal refinement只改变chart旋转。整个source surface只作刚体加uniform scale显示，没有非刚性warp。其权威标签仅GEOMETRIC_SHAPE_PRIOR，非anatomy authority。Reference2的0 depth并不要求把目标沟谷抹平；本手MCP、指距、整体宽度、dorsal arch、外围silhouette保持source约束。

## 目标与求解

A：actual native surrounding continuation，仅软调整core，normal-coordinate guide强度弱，central opposing hinge目标60°以保守消除V-notch。B：参考1的实际native triangles在aligned tangent chart中采样，移除其affine trend后保留目标外环当前dorsal arch的affine trend；以0.35软profile权重和reference95th-percentile normal progression（30°下限设计cap）引导。没有硬复制absolute reference depth/width，没有abstract quadratic fixed target；旧quadratic core depth只作报告诊断。

两者均惩罚position displacement、length-normalized first displacement gradient、native second bending，并将support外位移精确固定0。Local normal progression按baseline逐边约束；没有单一global max angle主目标。A/B尚未形成充分改善的结构合格解，所以C启用条件不满足，未生成机械R3-C。

在frozen baseline初始化，每次拟议方向内部动态查询changed-incident fan triangles vs whole mesh的proximity band。Inverse displacement/gradient/bending metric投影closest-feature signed separation；共边面不以永远0的shared-edge距离放行，而对预测off-edge接触的非重复四点signed-volume features补充side投影。每次接受前检查exact point/segment/coplanar-area新增contact、area、bowtie和orientation，并检查swept-AABB cubic coplanarity events及0.25/0.5/0.75内点orientation。

Activation band0.05mm、separation floor1e-6mm、point1e-8mm、coplanar area1e-8mm²、face area1e-8mm²、CCD shared-feature exclusion1e-7mm是计算参数，不是anatomy clearance。最低separation不会超过已有feature gap的一半；不设大间隙改手型。Native cycles/winding/F/E保持不变量；已向外的valid baseline faces保持chart及baseline normal hemisphere，已有向内fold的展开与新增reverse分开报告。

CCD边界：cubic coplanarity-event检查是projection与每个accepted endpoint硬gate的补强。恒定全程coplanar事件不由cubic roots完全认证；本轮没有声称global continuous-feasibility或topology-limit证明。该缺口列入下一方法研究。独立最终审核还检查全部局部baseline normal hemispheres，六个修正试解没有face reversal。

S1/S2只引用R2 bowtie3312和reverse3343 regression。完整native BFS支持S3=78/S4=111/S5=151点；thumb/nail/cap37/oldcap9/FIRST_WEB21/fresh R3 protected graph/historical317/CMC20mm保护集交集全部空。S6没有扩展：stall涉及core/shared-feature相对运动，相关点已在S3，无直接证据指向新增ring；不以失败自动扩圈。

## 求解结果（全为失败证据，不是候选）

| Trial | Pool | Moved | Max mm | RMS mm | Edge6676 deg | Depth diagnostic mm | New contact / bowtie / reversal / boundary fold |
|---|---:|---:|---:|---:|---:|---:|---|
| R3_A_S3_V2 | 78 | 78 | 0.199420 | 0.035649 | 173.285294 | 1.495183 | 0 / 0 / 0 / 0 |
| R3_A_S4_V2 | 111 | 111 | 0.250536 | 0.037641 | 172.033017 | 1.481040 | 0 / 0 / 0 / 0 |
| R3_A_S5_V2 | 151 | 151 | 0.224074 | 0.028818 | 172.680216 | 1.488259 | 0 / 0 / 0 / 0 |
| R3_B_S3_V3 | 78 | 78 | 0.186775 | 0.032716 | 173.737977 | 1.506722 | 0 / 0 / 0 / 0 |
| R3_B_S4_V3 | 111 | 111 | 0.216979 | 0.031726 | 173.115968 | 1.505799 | 0 / 0 / 0 / 0 |
| R3_B_S5_V3 | 151 | 151 | 0.260136 | 0.032780 | 172.301336 | 1.509230 | 0 / 0 / 0 / 0 |

六个最终选定试解（A-V2/B-V3）在向量化exact point/segment/coplanar审核及独立scalar segment审核中均无新增face-pair family；boundary screen均0新增fold，native degenerate/bowtie/reverse均无新增，support外exact0位移。每步accepted/rejected trace、dynamic feature IDs/barycentric/side axes、CCD events、area/normal gates和终止原因均保存。

但baseline core6676=178.227634°，本轮末端仍172.033–173.738°，核心depth proxy从1.546239mm只降到约1.481–1.509mm；尖折和沟谷连续性不足。机械checkpoint通过部分hard gates不等于结构可行Human候选。FIRST_STRUCTURALLY_FEASIBLE_SOLVE=NONE，candidate_count=0，actual recommended application points=0。

新方向阻碍主要为2182/3330：两面shared edge79/955上的接触合法，离开公共edge的接触被阻断。这类active set导致保守side projection与backtracking停滞，204/207不是唯一需要约束的pair。四个基于新阻碍的normal-first机械motion-seed假设（不是target/clearance）分别被3329/3331、2182/3330、3312/3313等新pair拒绝，保存完整证据，没有把这些seed当候选。

初始有限差分实现通过重复加减还原坐标产生微小浮点漂移，在1e-8mm阈值附近影响最终接触判断；旧S4-A末端显示1.475e-8mm的新segment并被拒绝。改为精确恢复saved scalar，重跑全部六个V2 trial及双实现终审；随后将参照健康核心与显示外环分开，对三个B再做V3复核。旧S3/A/B、S4-A结果与slow S4-B部分日志保留，后者因实现被替换而停止，均不计为合格trial。

## Baseline projected bowtie与严格候选gate

冻结source已有投影quad bowtie flags2771/3332/3351，native area并不退化。它们是投影诊断，不能隐藏或把零新增写成绝对零。六个选定试解的绝对flags仍是这三项：S3/S4 affected3332，S5 affected2771/3332。循环防止新增flag，但没有消除既有affected flags，所以绝对no-bowtie候选条件也未成立；全体失败。下一方法还需处理这些既有局部fold，同时保持nonpenetration。

参照1显示外环含3351flag，已明确排除其显示外环作为求解prior，仅使用健康outward central native faces和对应vertices；三个B重新运行并保存V3证据。未将带标记的外环伪装成健康patch。

## Boundary、基线接触及视觉

完整mixed moved/fixed face边、changed/fixed face interfaces与外侧fixed/fixed edge ring逐边记录baseline/candidate/delta、adjacent normals、baseline→candidate dots、位移gradient、端点位移；6675/6602/6676与ring displacement decay均保留。筛查定义new acute→obtuse或candidate>45°且增加>20°，是设计筛查，非人体阈值。

接触计数必须区分新增与既有。使用3414个native faces的稳定fan triangles和3416个source vertices，对全部changed-incident vs whole mesh检查；source本来存在10个本地contact families（本次diagnostic范畴），在JSON全披露。它们不等同于原Stage6A9个severe crossing分类。本轮仅记录incidental removed/retained pair变化，没有为原9优化、重跑、重新判级或覆盖历史证据。

review.html第一屏是原Human机位的CURRENT / R1-C失败 / R2-S5失败普通实体，并明确显示R3-A/B无合格候选。随后有全手、close solid、grazing、side、silhouette、wire、0/60/120截面、健康参照对比和204/207 onset forensic。R3 S5失败checkpoint只在诊断区，不能选择。

普通close/grazing/side仍可见原有尖notch与短折痕；R3 A/B失败checkpoint与CURRENT近似重合，0/60/120°截面也仅有微小变化。未形成足够改善且连续的自然沟谷，不能成为Human候选。

没有结构合格Human candidate，因此BIND RSSF、IDX_MCP_15/30/45全部NOT_RUN；不能冒充PASS。没有Full42、Stage6A/6B。

## 失败分类与下一方法缺口

D_OPTIMIZER_NONCONVERGENCE：目标仍严重未达，局部可行方向与contact active set停滞。没有A reference冲突、B collision infeasible、C boundary infeasible或E native topology expressivity的直接证明；F保护冲突也不存在。Baseline已经折叠并有既有局部交叉，保守四点side投影可能过度限制方向，不能把这套方法没有找到解写成数学不可行。

具体缺口：normal/tangent联合非线性方向、合法shared-contact active-set释放、feature re-identification与persistent-coplanar连续contact处理。不能重复R1/R2的generic fairing+事后check，也不能用S6机械扩圈替代该方法缺口。NEXT=POSITION_ONLY_FORMULATION_RESEARCH_AFTER_HUMAN_REVIEW；不建议LOCAL_TOPOLOGY_AMENDMENT_DESIGN_R1，因为E无证明。

TOPOLOGY_EXPRESSIVITY_LIMIT_EVIDENCE=NOT_FOUND；TOPOLOGY_CHANGE_REQUIRED=NOT_PROVED；POSITION_ONLY_INSUFFICIENT=NOT_PROVED_GLOBALLY；RET0PO_REQUIRED=NO。

## 不变量与零漂移

V/E/F=3416/6828/3414，face cycles/native2-face incidence来自同一冻结source，求解变量仅position数组。UV、materials、face smooth/sharp flags、custom normals状态、weights、21-bone frames与production authority都不作为变量；renderer只创建derived mesh copy/new scene，0个blend save。

全部3107个已有workspace文件SHA256与开始快照完全相同，包括R1/R2、prior_tmp、生产.blend、fresh protected authority及Stage6A证据；无missing、无unexpected outside additions。新增限定在本轮audit与独立geometry_design_r3_reference_guided_tmp。PRODUCTION_DRIFT=0。

**STOP — HUMAN REVIEW。没有推荐候选，没有应用。**
