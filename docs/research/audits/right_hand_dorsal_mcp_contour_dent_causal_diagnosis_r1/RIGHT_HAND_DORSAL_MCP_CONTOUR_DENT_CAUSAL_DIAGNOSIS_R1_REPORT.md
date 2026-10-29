# RIGHT_HAND_DORSAL_MCP_CONTOUR_DENT_CAUSAL_DIAGNOSIS_R1

状态：**READY_FOR_HUMAN_DENT_CAUSAL_REVIEW**。本轮严格只读诊断，无repair。根因确认：**BASE_GEOMETRY_CONTOUR_DEFECT**。

用户确认的A点通过原IDX_MCP15 FULL_SOLID图像的准确camera/view_frame射线映射到face3328，中心vertex955；不是根据文字猜点。原图、像素坐标、相机和采样参数、native面/边/1-ring/2-ring均在[DORSAL_MCP_DENT_ROI_R1.json](../../../../examples/historical/audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/DORSAL_MCP_DENT_ROI_R1.json)。15个核心顶点为`[79, 80, 955, 2089, 2096, 2327, 2328, 2531, 3025, 3316, 3323, 3324, 3332, 3339, 3340]`；7个命中面为`[204, 205, 2181, 2182, 3328, 3329, 3330]`。1-ring16、2-ring21，共52个诊断顶点、36个完整ROI面。数值均为诊断描述，不建立anatomy或write authority。

Human finding记录仍为`RIGHT_HAND_DORSAL_MCP_CONTOUR_DENT = PRODUCTION_BLOCKER_PENDING_CAUSAL_DIAGNOSIS`。本次已给出因果证据，产品blocker仍开放；没有Human验收或repair批准。

## 最终字段

| 字段 | 结果 |
|---|---|
| `DENT_VISIBLE_IN_STAGE4C_RAW` | `True` |
| `DENT_VISIBLE_IN_RSSF` | `True` |
| `DENT_VISIBLE_IN_R2_BIND` | `True` |
| `DENT_VISIBLE_IN_IDX_MCP_15` | `True` |
| `EARLIEST_CONFIRMED_DENT_STAGE` | `STAGE4A_R2_BASE_PRE_CMC_RETOPO` |
| `RAW_TO_BIND_GEOMETRY_DELTA` | `{"Stage4C_raw_to_R2_raw_max_mm": 0.0, "R2_ROI_raw_to_evaluated_bind_max_mm": 3.0163926520760446e-05, "R2_core_raw_to_evaluated_bind_max_mm": 4.656612873077393e-06}` |
| `ZERO_POSE_ARMATURE_GEOMETRY_DELTA` | `3.0163926520760446e-05` |
| `SHADING_CAUSAL` | `VISUAL_EMPHASIS_ONLY_NOT_ROOT_CAUSE` |
| `ARMATURE_ZERO_POSE_CAUSAL` | `NO_EFFECT_BEYOND_KNOWN_FLOAT_NOISE` |
| `SKIN_CAUSAL` | `NO_STATIC_ROOT_CAUSE; NO_SUPPORTED_REQUESTED_INDEX_POSE_AMPLIFIER` |
| `POSE_AMPLIFICATION` | `NO_SUPPORTED_IDX_MCP15_30_45_AMPLIFICATION` |
| `ROOT_CAUSE_CLASS` | `BASE_GEOMETRY_CONTOUR_DEFECT` |
| `TOPOLOGY_CHANGE_REQUIRED` | `NO_REQUIREMENT_IDENTIFIED_FOR_INITIAL_POSITION_ONLY_DESIGN` |
| `RET0PO_REQUIRED` | `NO` |
| `MINIMAL_REPAIR_LAYER` | `LOCAL_EXISTING_VERTEX_POSITIONS_IN_STAGE4_GEOMETRY` |
| `PRODUCTION_DRIFT` | `0` |

## Lineage与最早确认来源

正式Stage4A_R2_BASE是CMC重拓扑前工程基线，3364顶点；当前网格3416顶点。没有假设其全局topology一致：逐个唯一精确world坐标匹配了52个局部顶点，并验证36个native面有相同的有向顶点cycle。[EARLIER_STAGE4A_BASE_LOCAL_IDENTITY_R1.json](../../../../examples/historical/audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/EARLIER_STAGE4A_BASE_LOCAL_IDENTITY_R1.json)完整保存映射、source hash和绕序验证。其局部几何与实际渲染的Stage4A_R2相同，故凹口最早已确认在**STAGE4A_R2_BASE_PRE_CMC_RETOPO**。这不是首次制造缺陷的日期；未进一步审计Stage2或更早历史。

Stage4A_R2、Stage4B_RSSF_R2、Stage4C_R2、corrected Stage5A和R2之间native顶点/边/面一致。Stage4C raw本身已经处于RSSF；RSSF比较用正式Stage4B_RSSF_R2而非创造一个不存在的Stage4C原生姿态。Stage4C raw与corrected Stage5A/R2 raw全网格world坐标精确一致；Stage4B RSSF相对Stage4C最大差约0.00000373mm。前后native原始坐标、evaluated坐标及source flags存于[LINEAGE_RAW_READONLY_EXTRACTION.json](../../../artifacts/d026355f7fecf2ec6428.md)。

匹配展示采用2-ring21的proper刚性rotation/translation，scale=1，无反射或局部修正。配准矩阵、支持环RMS、原始与registered坐标全部保留。早期pre-RSSF局部形状仍是实际原形。[DENT_STAGE_LINEAGE_COMPARISON_R1.json](../../../../examples/historical/audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/DENT_STAGE_LINEAGE_COMPARISON_R1.json)提供输入状态与每阶段诊断结果。没有用BASE的局部等同性伪称渲染了其整个旧网格。

## Geometry与shading

每个阶段生成CURRENT、FLAT、WIRE、NORMALS、GRAZING、SILHOUETTE、两额外角度及smooth-reset诊断副本，共63张matched渲染，另有ROI定位图。主相机23mm正交画幅，各阶段同机位/尺度/光照和R2生产材质UV规则。[review.html](../../../artifacts/430423b50fe7b2463454.md)同时给出三条实际截面。CURRENT是R2原有材质/UV/normal flags，不是每个历史阶段当时光照的复刻。

**R2 ROI的36个面全部use_smooth=false，且没有custom normals。** CURRENT与FLAT近似相同是原始资产本来就flat。已有Stage6A renderer将展示副本设为smooth，视觉上加重沟谷；本轮smooth counterfactual复现这种强调，但它没有创造凹陷。无Armature的Stage4A原始vertex geometry、wire、flat及actual sections均保留锐折陷，因此不是normal/shading artifact，也不因视觉强调而分类为mixed cause。

R2最大native相邻面法线夹角为178.227634°，edge6676、vertices[3340, 3332]、faces[3329, 3330]。两侧面遍历该边方向相反，绕序一致；这是接近反折的实际几何面关系，不能通过解释为简单倒置normal排除。仅对ROI检查的所有边均为2-face incidence且绕序一致，未发现需要重拓扑的局部连接错误。

三截面穿过vertex955、局部切向0°/60°/120°，用native面fan三角化与平面真实相交，保留face IDs和world/profile坐标；无best-fit修平。[DENT_CROSS_SECTIONS_R1.json](../../../../examples/historical/audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/DENT_CROSS_SECTIONS_R1.json)可重算。截面图固定坐标轴，不把相互重叠的数据夸大为阶段变化。

2-ring二次曲面拟合的核心负残差proxy：pre-RSSF Stage4A约1.807104mm；Stage4B/RSSF与Stage4C约1.546239mm；R2 BIND约1.546248mm。该proxy只描述邻域几何，不是生理深度、人体标准或新Stage6 gate。plane残差、umbrella curvature proxy、vertex-normal variation及每条dihedral也完整保存于[DENT_LOCAL_GEOMETRY_METRICS_R1.json](../../../../examples/historical/audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/DENT_LOCAL_GEOMETRY_METRICS_R1.json)。

## Armature / bind / skin / pose

R2 Armature OFF/raw与ON/evaluated zero的ROI最大差为3.01639265208e-05mm，core最大差为4.65661287308e-06mm，全网格最大差为5.96700924622e-05mm。OFF/ON不是bitwise一致，差异落在项目原有0.0001mm zero校验范围内；本轮不建立新阈值。object/armature world matrices一致，parent inverse为单位阵，pose zero已验证。该浮点量级不能解释静态毫米级局部折陷。[DENT_ARMATURE_ZERO_POSE_AUDIT_R1.json](../../../../examples/historical/audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/DENT_ARMATURE_ZERO_POSE_AUDIT_R1.json)记录准确结果。

当前core主要由WRIST/RING_MCP及少量MIDDLE/LITTLE驱动；所有15核心点INDEX_MCP权重为0，52点中INDEX_MCP最大权重仅0.000390139757656。完整向量、邻边L1变化保存在[DENT_POSE_AMPLIFICATION_R1.json](../../../../examples/historical/audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/DENT_POSE_AMPLIFICATION_R1.json)。不能因为weight variation存在就归因skin：折陷在无Armature的历史raw mesh早已存在。

本轮只读复用了旧Full Stage6A BIND、IDX15/30/45的保存坐标，未执行pose cases。15核心点相对evaluated BIND最大位移均**精确0**，核心面积/最大折边角保持不变；诊断52点的最大位移分别约0.002090/0.004126/0.006117mm。depth proxy分别1.547854/1.549611/1.551419mm的微小增加来自支持环移动与重拟合，不能当作核心凹陷加深证据。因此分类**STATIC_BASELINE_DEFECT**；没有支持所要求INDEX poses的amplification。该结论不推广到其他未经本轮分析的driver或pose。

## 最小未来修改层与downstream

输出：**MINIMAL_LOCAL_GEOMETRY_AMENDMENT_REQUIRED_PENDING_HUMAN_APPROVAL**。最小候选层是Stage4局部现有顶点位置。没有证据要求改topology、retopo、bone/joint或frozen membership；可优先设计位置修正。**本轮未实施或证明repair成功，15点也不是已证明不可缩减的最终写入集。**

诊断seed15点/7可见命中面之外，还需验证seed全部24个native incident faces。若需1-ring16点过渡，另行确定其范围；2-ring21仅固定参考。精确列表见[DENT_FUTURE_MINIMAL_AMENDMENT_BLAST_RADIUS_R1.json](../../../../examples/historical/audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/DENT_FUTURE_MINIMAL_AMENDMENT_BLAST_RADIUS_R1.json)。不能把52点诊断ROI变成默认写入授权。

当前52点与native thumb nail、cap37、old_cap9、FIRST_WEB21、fresh R3 bounded graph、历史317权重集合及CMC20mm原有保护context都无交集。ROI离CMC center最小约89.391mm。CMC20mm只是核对既有surgery context，不新建anatomical membership。局部位置修改预计可保留这些membership及21-bone hierarchy；仍必须核对边界与几何衍生结果，不能以零交集代替downstream验证。

未来经授权修正后必须：

1. 对新版本Stage4候选复核局部contour、所有incident faces、manifold/winding、UV/material不变量，以及nail/CMC/RSSF保护。
2. 复核到corrected Stage5A和R2的geometry传递、joint-to-surface alignment、rest/zero/bind、reset及静态skin。可先精确继承weights，不自动重拟合bones或重跑R3。历史317 weight scope不会因此重新打开。
3. 重算依赖geometry的数值结果，尤其true-cap图边长度/全图最短路径/bounds；即使cap37 endpoint没有移动，最短路径数值也不能仅凭membership不变直接承袭。保留原始Human receipts，另存新版本验证，不重写authority。
4. 在另行授权的修复阶段完成Stage5 static/targeted deformation、Full42-case Stage6A requalification及Human产品轮廓验收。本轮没有重跑这些流程。
5. 原9对unapproved severe exact crossings继续独立FAIL_CLOSED，不因dent问题诊断或未来修复自动消失。Stage6B与production promotion继续受资格验证和Human闭环约束。

## 只读核验与停止

全工作区本轮前已有2790个文件逐一SHA256比较：changed=0、missing=0、诊断目录外added=0，**PRODUCTION_DRIFT=0**。包括Stage4C/RSSF、nail/CMC、21 bones/corrected kinematics、cap37/fresh R3/FIRST_WEB21、R2、true-cap corrected numeric authority、所有Human receipts与全部旧Full Stage6A证据。完整基线和[PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json](../../../../examples/historical/audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json)可复查。未保存blend、未执行geometry/weight/bone/material/normal/RSSF edits、未Stage6A rerun、未Stage6B或promotion。

唯一NEXT建议：**MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R1**。本轮未执行NEXT。

**STOP — HUMAN REVIEW**
