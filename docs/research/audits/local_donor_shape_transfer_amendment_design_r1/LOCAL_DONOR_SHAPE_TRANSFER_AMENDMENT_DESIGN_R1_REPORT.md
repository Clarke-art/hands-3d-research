# LOCAL_DONOR_SHAPE_TRANSFER_AMENDMENT_DESIGN_R1

结论：READY_FOR_HUMAN_AMENDMENT_APPROVAL。STOP — HUMAN REVIEW。

只在本轮独立目录生成正式design候选；未APPLY、未改历史Stage4、未正式传播Stage5、未重算R3/true-cap/ownership/static qualification/targeted deformation/Full42。三档IDX仅按用户允许的临时smoke执行。

## 独立复现与唯一lineage

从实际官方master重新评估stored Multires L1，实际Stage4C与Stage4A rest重新读取；54点按官方L1 parent edge ancestry、历史split权重及frozen RSSF J独立计算。

`target[i] = frozen_Stage4C[i] + frozen_RSSF_J[i] @ (sum(parent_weight * actual_official_L1[parent]) - historical_Stage4A_rest[i])`

64次历史split的唯一真实parent edge与fraction逐个独立验证；沿冻结ancestry闭包重新恢复54点，不复制探针最终坐标，不执行历史surface优化。保存并重新打开正式blend验证。

RECOMPUTED_WRITE_SET_COUNT=54；PROBE_WRITE_SET_COUNT=54；WRITE_SET_IDENTITY_MATCH=True；MAX_COORD_DELTA_VS_PROBE_MM=0。54/54均有donor ancestry、frozen transform、target及restoration reason。scope_expansion=0；optimization/fairing/manual_tuning=0。

Write IDs：738, 2237, 2238, 2276, 2328, 2330, 3300, 3301, 3302, 3303, 3304, 3305, 3306, 3307, 3308, 3309, 3310, 3311, 3312, 3313, 3314, 3315, 3316, 3317, 3318, 3319, 3320, 3321, 3322, 3323, 3324, 3325, 3326, 3327, 3328, 3329, 3330, 3331, 3332, 3333, 3334, 3335, 3336, 3337, 3338, 3339, 3340, 3341, 3342, 3343, 3344, 3345, 3346, 3347。

## 来源与资产hash

DONOR_SOURCE：Blender Human Base Meshes v1.4.1 / Hand  - Realistic / official Multires L1 equivalent to Stage2 evaluated L1。

DONOR_SOURCE_HASH：`3c121505651140ceb4d69fd1d8923f7788ffadd81672f5be14845a5f2c75c137`

SOURCE_STAGE4C_HASH：`fde620b2cebd2b4cd894e32b58d7b59ba7fac9b00d3d2dfa5193cefb32513ab7`

FORMAL_CANDIDATE_HASH：`9788ef1582344b12d17c8c201b59f6f1b5c59eb22648a0753bba1725481ed8e8`

Asset：[RIGHT_HAND_ENGINEERING_STAGE4C_R2_DONOR_TRANSFER_CANDIDATE_R1.blend](../../../artifacts/c6d45b2ba2fb5b183041.md)。对象custom props明确AMENDMENT_DESIGN_ONLY、NOT_PRODUCTION、NOT_HUMAN_APPROVED、DO_NOT_PROMOTE。只有这些新增design标签与54点position属于预期变更；既有全部protected payload精确保持。

## Payload与结构

V/E/F=[3416, 6828, 3414]；vertex/edge/face IDs、native cycles、manifold incidence、UV坐标/连接、materials/assignments、smooth/sharp flags、custom normal state、groups/weights、armatures/bones/joints、object matrices全部精确保持。

Stage4C几何asset本来无vertex groups/armature/custom normals；temporary currentR2 bind副本另外验证实际rig/weights全payload精确保持，未借此宣称Stage4C自带production rig。RSSF、nail、cap37、FIRST_WEB21、freshR3等外部authority以全项目byte hash保护。

TOTAL_VERTEX_POSITION_CHANGED=54。OUTSIDE_WRITE_SET_POSITION_DRIFT=0；TOPOLOGY_DRIFT=0；UV_DRIFT=0；MATERIAL_DRIFT=0；WEIGHT_DRIFT=0；BONE_JOINT_DRIFT=0。

STRUCTURAL_GATE=PASS；TOPOLOGY_PRESERVED=PASS；UV_MATERIAL_PRESERVED=PASS；WEIGHT_RIG_PAYLOAD_PRESERVED=PASS；TRUE_CONTACT_NO_REGRESSION=PASS。

54点incident native fans对whole mesh进行真实finite-feature exact rational交集测试，扣除真实legal shared simplex，并跟踪baseline component membership、feature及extent。所有其它静态pair因坐标不变而精确不变。局部baseline12个真实contact components→candidate0。

NEW_TRUE3D_CONTACT_COUNT=0；NEW_SELF_INTERSECTION_COUNT=0；NEW_NONADJACENT_EXACT_INTERSECTION=0；NEW_OFF_SHARED_CROSSING=0；NEW_ILLEGAL_COPLANAR_OVERLAP=0；NEW_STRUCTURAL_BOWTIE=0；FACE_REVERSAL_COUNT=0；DEGENERATE_COUNT=0；BASELINE_CONTACT_WORSENING_COUNT=0；BASELINE_CONTACT_FEATURE_EXPANSION_COUNT=0；NEW_OBTUSE_SHARP_TRANSITION_MIGRATION_COUNT=0。

保留reconciled semantics：不要求absolute projected bowtie zero；不能把固定chart normal翻转当成intrinsic reversal。native oriented cycles不变，声明的直线morph连续fan最小面积=0.0217315680685mm²，无zero-area event。端点exact contacts和连续area证据不构成全程continuous collision qualification，也不构成production资格。

## Donor fidelity（54点ancestry语义）

max=0.0001594459049395mm；mean=7.29966199274239e-05mm；RMS=8.15885314830103e-05mm；p95=0.000142653370526089mm。

这是frozen RSSF之后的unrounded ancestry targets与实际native float32保存值之差，只含存储数值舍入；不采用nearest-surface距离。54点外按设计保留engineered current surface，不声称全手与donor重合。

## Boundary与普通实体

完整boundary及outer fixed-fixed环记录、每边normal dot/position/gradient及全部abs(delta)>10°边见BOUNDARY_AUDIT。保守筛查为newly obtuse interface或angle>45°且increase>20°；仅geometry诊断，不是人体阈值。匹配实体补充检查迁移hinge/ridge/notch/silhouette kink。

|Edge|Source°|Formal°|Delta°|
|---|---:|---:|---:|
|6675|27.929196939|30.432284011|2.503087072|
|6602|25.668912224|29.307174847|3.638262623|
|6676|178.227633924|1.377820914|-176.849813009|

96张匹配render：第一屏四列CURRENT_STAGE4C_R2 / OFFICIAL_L1_DONOR / TEMPORARY_FEASIBILITY_PROBE / FORMAL_AMENDMENT_CANDIDATE普通实体；原始Human640×800机位、close、full dorsal、grazing、side、silhouette、native wire。均保留flat及实际native smooth flags；同一中性材质/光照/尺度。0/60/120°实际native sections及donor/formal overlay提供同物理平面与尺度，faceID追溯。官方donor原始姿态只按冻结刚性display配准展示；精确fidelity依据右侧current-topology ancestry target overlay及机器误差。

VISIBLE_DENT_STATUS=ABSENT_PENDING_HUMAN_CONFIRMATION。NEW_VISIBLE_DEFECT=NONE_OBSERVED_PENDING_HUMAN_CONFIRMATION。Agent实际检查close/grazing/side/full dorsal/silhouette/native wire：尖锐notch消失，自然浅谷恢复，未观察到新增鼓包、ridge、折点或全手dorsal arch缺陷。仍须Human确认。

## Temporary bind与有限pose smoke

仅staticPASS后建立实际currentR2 rig/weights独立副本，54点raw位置写入此临时副本；bindPASS后执行IDX_MCP_15/30/45。没有正式Stage5 propagation。RAW_TO_BIND_ROI_MAX_DELTA_MM=3.01639265207604e-05；数值zero核对tolerance0.0001mm。currentbaseline bind和3poses均精确复现旧坐标；每case零姿态恢复精确一致；临时bindblend重新打开核对PASS。

BIND_PREVIEW=PASS；DENT_REAPPEARED_IN_BIND=NO；NEW_BIND_VISIBLE_DEFECT=NONE_OBSERVED_PENDING_HUMAN_CONFIRMATION。IDX15_SMOKE=PASS_LOCAL_TEMPORARY；IDX30_SMOKE=PASS_LOCAL_TEMPORARY；IDX45_SMOKE=PASS_LOCAL_TEMPORARY。每个同pose相对currentbaseline执行局部contact/feature-no-regression及边界筛查，新contact/新边界transition=0。匹配实体未见由本次transfer造成局部折回或新缺陷，Human pending。

## 独立旧blocker

FULL_STAGE6A_STATUS_RETAINED=FAIL_CLOSED_FULL_STAGE6A_REQUALIFICATION。原9对unapproved severe exact crossings继续独立保留，不优化、不裁决、不PASS/FAIL重新分类、不human接受。INCIDENTAL_STAGE6A_CROSSING_DELTA仅记录已运行IDXcase旧witness顶点坐标变化；TH_IP_15未运行。旧Full42status文件hash保持。

## 下游影响与计划

直接几何footprint：54点；95个incident native faces；148个incident edges；详细IDs/one-ring/boundary及authority集合交集见DOWNSTREAM_PLAN。cap37点交集=[]；FIRST_WEB21交集=[]；freshR3 frozen domain交集=[]；317weight universe交集=[]。冻结cap源/target endpoint交集分别=[] / []；703条历史primary path中0条经过write点，仅查看已有记录，无新path/bound重算。即使原path没有经过write点，改变edge metric仍可能改变新最短路，正式APPLY后必须geometry-dependent重验证。

计划执行次序：Stage4 local validation → Stage5独立geometry propagation → joint-to-surface → rest/zero/bind → static skin compatibility → geometry-dependent frozen true-cap paths/bounds → targeted deformation → Full42 Stage6A → Human contour review。每步依赖与成功证据要求、冻结authority哈希、703/1406endpoint覆盖及required-bound-case manifest已记录。所有步骤PLAN_ONLY_NOT_EXECUTED。

NO_RESEARCH_REOPEN：cap37 anatomy、freshR3 ownership、FIRST_WEB anatomy、CMC topology、thumb kinematics、317 weight authority、retopo、bone/joint authority；只有后续实际revalidation出现新直接证据时，另定范围。

## Human审批

Human只批准：唯一donor identity、54个IDs、54点正式target coords、frozenStage4C→独立candidate lineage、currenttopology preservation、visible contour result及下游重验证影响范围。HUMAN_AMENDMENT_APPROVAL_SCOPE_R1.json绑定source/donor/candidate hash、write-set hash与54target local coordinate hash。批准不包含production promotion、Stage6A PASS或Stage6B PASS。

NEXT=HUMAN_APPROVE_LOCAL_DONOR_SHAPE_TRANSFER_AMENDMENT_R1。下一轮Human批准后才可执行LOCAL_DONOR_SHAPE_TRANSFER_AMENDMENT_APPLICATION_R1。

STOP — HUMAN REVIEW。

最终全项目只读hash验证与verdict由verify_delivery.py追加如下。

## 最终只读与交付验证

PRODUCTION_DRIFT=0。全部3668个预先存在文件SHA256逐个相同；changed/deleted/new-outside-current-audit均为0。Stage4C、official master、currentR2、既有authority与旧Full42文件byte identical。正式candidate保存之后hash未变。

AMENDMENT_DESIGN_VERDICT=READY_FOR_HUMAN_AMENDMENT_APPROVAL。NEXT=HUMAN_APPROVE_LOCAL_DONOR_SHAPE_TRANSFER_AMENDMENT_R1。STOP — HUMAN REVIEW。
