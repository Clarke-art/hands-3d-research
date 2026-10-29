# MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R2

**FAIL_CLOSED_R2_POSITION_ONLY_GEOMETRY_DESIGN · STOP — HUMAN REVIEW**

ROOT_CAUSE_CLASS=BASE_GEOMETRY_CONTOUR_DEFECT。R1 A/B/C 均未批准。本轮仅 position-only 设计、临时 derived evidence，没有应用或 production master。

SUPPORT_DEPTHS_TESTED=[1,2,3,4,5]；FIRST_STRUCTURALLY_FEASIBLE_SUPPORT_DEPTH=NONE；PROTECTION_BOUNDARY_REACHED=FALSE；POSITION_ONLY_LOCAL_SUPPORT_EXHAUSTED=TRUE；R2_CANDIDATE_COUNT=0；RECOMMENDED_CANDIDATE=NONE；RECOMMENDED_ACTUAL_WRITE_VERTEX_COUNT=0；TOPOLOGY_CHANGE_REQUIRED=NOT_PROVED；RET0PO_REQUIRED=NO；POSITION_ONLY_INSUFFICIENT=NOT_PROVED_GLOBALLY。

## 支持、保护与 source

Source 为 frozen Stage4C_R2：{'path': 'production_spec/stage4_blender/stage4c_r2/RIGHT_HAND_ENGINEERING_STAGE4C_R2.blend', 'sha256': 'fde620b2cebd2b4cd894e32b58d7b59ba7fac9b00d3d2dfa5193cefb32513ab7'}. native vertex/edge/face counts=3416/6828/3414. 原始 source 不覆盖，Stage4A earlier geometry只作历史证据。

S0=Human 已确认15 core vertices。沿 native edge adjacency完整 BFS 建立 S1–S5=31/52/78/111/151。每层新增vertex、incident/new face、edge IDs及authority交集均在NESTED_SUPPORT_SET_AUDIT_R2。R1 core/ring1/ring2与实际C write set作为输入来源保留，support不由手工IDs凑成。S5是S1–S4在初始formulation失败后才测试，没有预设必须S5。

所有支持与 thumb nail/cap37/oldcap9/FIRST_WEB21/fresh R3 bounded protected graph/historical317/现有CMC20mm context交集空。21 bones、joint positions、weights、UV/material/normal flags/custom-normal状态均不是求解变量；原文件全部只读。没有创建新的 anatomy authority。support 是 DESIGN SEARCH POOL，绝不产生应用权限。

## 方法和最小深度搜索

380 主求解 +17 rejected full-guide probes；每个主formulation都按S1→S5顺序测试，若发现first feasible则只允许该层与下一层生成Human候选。本轮没有first feasible。

(1) regularized native graph thin-plate tangent fairing与curved core height prior；(2) R1-C corrected core soft anchors的biharmonic displacement field，isotropic/anisotropic权重；(3) 显式interface normal-dot投影；(4) angle与curved core height联合约束。位移、一级gradient和二级bending同时惩罚，外部精确0。投影修正使用inverse regularized graph biharmonic metric向完整支持池平滑传播，最大单步0.3mm。

Gaussian width6mm/depth0.65mm、core height interval[-0.95,+0.25]mm、angle target max(35°,baseline+10°) capped85°、central6676 target30°都只是SURFACE_DESIGN_PRIOR/工程优化参数，不是ANATOMICAL_AUTHORITY。各attempt保存实际target min-normal-dot、参数及projection trace；源码后续改进不会覆盖旧坐标/trace证据。

初始绝对fairing虽修中心仍新建或迁移折边。核心锚定能恢复6675/6602，却把新hinge迁至2517。只约束角度会让depth变差；加height后，S3–S5可通过初步角度/面gate，但精确接触失败。

| support | pool vertices | main attempts | final formulation failure |
|---|---:|---:|---|
| S1 | 31 | 76 | new_quad_bowties |
| S2 | 52 | 76 | new_reference_reversed_faces |
| S3 | 78 | 76 | new_exact_contact_or_self_intersection |
| S4 | 111 | 76 | new_exact_contact_or_self_intersection |
| S5 | 151 | 76 | new_exact_contact_or_self_intersection |

最终最小失败：S1=quad bow-tie face3312；S2=new reference reverse face3343；S3/S4/S5均新增faces204/207 exact segment（另metric0.1还新增207/3312）。主搜索matrix记录所有其他失败边/面，不以少数成功标量隐藏问题。

## 完整 gate 和逐边数据

native topology/face cycles不变，source全边2-face incidence保持。检查所有moved-incident faces的native area/normal和quad bow-tie，并覆盖write-boundary incident edges、changed/fixed face-interface及完整外侧fixed/fixed edge ring。每边保留baseline/candidate/delta、两侧方向、baseline→candidate normal dot、端点位移和displacement gradient。6675/6602/6676与所有内部高变化边都记录。

boundary筛查拒绝new acute→obtuse或candidate>45°且增量>20°；它是保守工程筛查，不是人体角度标准。global max不能替代逐边检查。旧inward contour展开与新增reverse分别记录；face cycle身份保持不能证明形状合格。

contact采用独立NumPy float64 native fan triangles，changed-incident region against entire mesh；AABB、双向edge/triangle clipping及coplanar-area clipping，shared topology只排除实际公共vertex/edge上的合法接触，离开公共edge的crossing仍计。数值segment tolerance1e-5mm、coplanar area1e-6mm²不是生理阈值。unchanged/unchanged几何完全一致，故新global intersection必触及changed region并被覆盖。

早期gate失败的contact明确NOT_RUN，不冒充0。S3–S5 finalmetric1.0新增204/207相交长度分别约0.452221/0.456393/0.455187mm。隔离forensic保存实际native face IDs及交点world-mm，便于独立核查。原9 Stage6A severe crossings未放进objective；任何减少仅INCIDENTAL_EFFECT。

## S5失败证据数字（不是candidate或write authority）

{
  "SUPPORT_DEPTH": 5,
  "SUPPORT_POOL_VERTEX_COUNT": 151,
  "ACTUAL_DESIGN_MOVED_VERTEX_COUNT": 151,
  "MAX_DISPLACEMENT_MM": 2.652874371134679,
  "RMS_DISPLACEMENT_MM": 0.5000522763950646,
  "MAX_BOUNDARY_DISPLACEMENT_MM": 0.17335996096246256,
  "MAX_BOUNDARY_DIHEDRAL_DEG": 178.23846213697004,
  "EDGE6675_DIHEDRAL_DEG": 37.92920529449978,
  "EDGE6602_DIHEDRAL_DEG": 25.950652835451134,
  "EDGE6676_DIHEDRAL_DEG": 30.000000646687603,
  "NEW_CONTACT_COUNT": 1,
  "BOW_TIE_COUNT": 0,
  "FACE_REVERSAL_COUNT": 0,
  "SELF_INTERSECTION_COUNT": 1,
  "self_intersection_count_semantics": "Introduced incident-to-whole-mesh exact intersections, not unchanged historical/global total.",
  "VISIBLE_DENT_STATUS": "REDUCED_BUT_DESIGN_REJECTED",
  "BOUNDARY_FOLD_STATUS": "NO_NEW_SCREENED_BOUNDARY_FOLD",
  "NEW_VISIBLE_DEFECT": "NEW_STRUCTURAL_DEFECT_VISIBLE_SEVERITY_NOT_ADJUDICATED",
  "BIND_PREVIEW": "NOT_RUN",
  "IDX15_PREVIEW": "NOT_RUN",
  "IDX30_PREVIEW": "NOT_RUN",
  "IDX45_PREVIEW": "NOT_RUN"
}

每个失败试解每点baseline xyz/candidate xyz/delta xyz/magnitude，以及max/mean/RMS/p95、boundary位移/gradient保存在R2_FAILED_SOLVE_WRITE_SET_EVIDENCE。≈0位移不计actual moved set。R2_CANDIDATE_WRITE_SET_COMPARISON的candidate列表为空，推荐应用点数0。

## 视觉、preview与失败归因

review.html首屏 CURRENT / R1-C失败参考 / S5失败证据，同机位普通实体，无forensic overlay。后续给完整dorsal、原Human机位、grazing、flat、wire、silhouette、两side views、6675/6602matched solids、isolated boundary/contact forensic及expanded真实0°/60°/120°截面与central zoom。未用改normal/material伪修复。

已查看普通实体、grazing、边界、全手、side和截面；中央原notch减弱，但自然连续浅谷完整PASS未建立。部分boundary facet在全表面视图被遮挡，所以不用一张solid图宣称无新defect。Human可见严重性仍待审；新exact contact已经足以拒绝。

没有结构合格candidate，故BIND/RSSF/IDX15/30/45 downstream smoke=NOT_RUN_NO_STRUCTURALLY_FEASIBLE_CANDIDATE。没有把未运行写成PASS。Full42未运行，原FullStage6A=FAIL_CLOSED_FULL_STAGE6A_REQUALIFICATION与9对crossings保持独立。

POSITION_ONLY_LOCAL_SUPPORT_EXHAUSTED仅表示本次最大S5范围和记录的formulation未找到joint-gate解，不是所有position-only方法的不可行证明。失败分类D_OPTIMIZER_FORMULATION_INSUFFICIENCY：angle/height约束可收敛，但未找到同时避免contact的优化解。A topology distribution limitation无直接证据；B protected conflict没有；C target-surface conflict未证明。不得自动建议topology edit或RET0PO_REQUIRED=YES。

## Conditional downstream与零漂移

R2_DOWNSTREAM_BLAST_RADIUS保留未来获批后新Stage4 version、corrected Stage5A/R2显式propagation、joint-to-surface/bind/reset/skin兼容、geometry-derived true-cap graph paths/bounds与hash数值重新核对、targeted deformation/Full42/Human复核。当前不执行任何应用、bone/weight重建、R3重新研究、Full42、Stage6B或promotion。

PRODUCTION_DRIFT=0由全preexisting workspace文件SHA256比较确认。新增只在本轮audits目录与stage4b_rssf/_tmp的独立本轮derived frames；临时单帧和最终contact sheets分开，无删除，已有_tmp文件也保持hash。

RECOMMENDED_CANDIDATE=NONE；RECOMMENDED_ACTUAL_WRITE_VERTEX_COUNT=0；RET0PO_REQUIRED=NO。**STOP — HUMAN REVIEW**。

模型补充检查：120° central section 显示重新分布的 ridge / slope change；完整自然浅谷仍未建立。隔离 204/207 forensic 直接显示约0.455187mm新相交段，baseline与R1-C均无该段。该几何失败独立于Human可见严重性的最终裁定。
