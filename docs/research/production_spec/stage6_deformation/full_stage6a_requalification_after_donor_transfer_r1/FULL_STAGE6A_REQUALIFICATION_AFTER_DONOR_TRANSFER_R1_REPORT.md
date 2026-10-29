# FULL_STAGE6A_REQUALIFICATION_AFTER_DONOR_TRANSFER_R1

**FAIL_CLOSED_FULL_STAGE6A_REQUALIFICATION**

42/42 formal cases针对当前donor-transfer R2独立fresh执行；−1 local X，15/30/45，WRIST/CMC locked。旧Full42 status没有被继承，旧9 pair逐对forced fresh测量，当前active blocker authority仅来自本轮。

| Field | Result |
|---|---|
| `FORMAL_CASE_COUNT` | `42` |
| `FORMAL_CASES_COMPLETED` | `42` |
| `FLEXION_AXIS_SIGN_QUALIFIED` | `PASS_LOCAL_X_HISTORICAL_MINUS_ONE` |
| `ZERO_RESTORE` | `PASS` |
| `NAN_INF_COUNT` | `0` |
| `COLLAPSED_FACE_COUNT` | `0` |
| `DEGENERATE_EDGE_COUNT` | `0` |
| `DEGENERATE_FACE_COUNT` | `0` |
| `TOPOLOGY_DRIFT` | `0` |
| `SEVERE_EDGE_STRETCH_CASE_COUNT` | `0` |
| `SEVERE_EDGE_STRETCH_EDGE_COUNT` | `0` |
| `CURRENT_TOTAL_EXACT_CROSSING_COUNT` | `2099` |
| `CURRENT_UNAPPROVED_EXACT_CROSSING_COUNT` | `247` |
| `CURRENT_UNAPPROVED_SEVERE_EXACT_CROSSING_COUNT` | `9` |
| `CURRENT_KNOWN_HUMAN_ACCEPTED_CONTACT_COUNT` | `3` |
| `CURRENT_NEW_PAIR_COUNT` | `0` |
| `CURRENT_DISAPPEARED_OLD_PAIR_COUNT` | `208` |
| `CURRENT_DISAPPEARED_UNIQUE_NATIVE_PAIR_COUNT` | `5` |
| `CURRENT_POSE_GENERATED_EXACT_COUNT` | `250` |
| `CURRENT_SOURCE_EXISTING_CONTACT_COUNT` | `1849` |
| `CURRENT_SOURCE_EXISTING_CLASS_A_CONTEXT_COUNT` | `68` |
| `CURRENT_ALL_NATIVE_NON_HUMAN_APPROVED_CLASS_A_CONTEXT_COUNT` | `77` |
| `OLD_9_REMEASURED_COUNT` | `9` |
| `OLD_9_STILL_PRESENT_COUNT` | `9` |
| `OLD_9_DISAPPEARED_COUNT` | `0` |
| `OLD_9_SEVERITY_REDUCED_COUNT` | `0` |
| `OLD_9_SEVERITY_INCREASED_COUNT` | `0` |
| `NON_TARGET_DIGIT_CONTAMINATION` | `0` |
| `FOREARM_STABILITY` | `PASS` |
| `FOREARM_MOVEMENT_MAX_MM` | `0.0` |
| `TIP_TRAJECTORY_MONOTONIC` | `PASS` |
| `TIP_HELPER_DEFORMATION_INFLUENCE_COUNT` | `0` |
| `NAIL_DEFORMATION` | `MEASURED42_NO_COLLAPSE_TOPOLOGY_FAILURE_APPEARANCE_PENDING_HUMAN` |
| `CAP37_DEFORMATION` | `MEASURED42_NO_CATASTROPHIC_STRUCTURAL_FAILURE_EXACT_CONTACTS_RECORDED` |
| `OLD_CAP9_INDEX_COMPATIBILITY` | `PASS_NATIVE_INDEX_NO_THUMB_OVERRIDE` |
| `DORSAL_MCP_DENT_REAPPEAR_COUNT` | `0` |
| `DORSAL_MCP_NEW_RIDGE_NOTCH_COUNT` | `0` |
| `DORSAL_MCP_NEW_STRUCTURAL_CROSSING_COUNT` | `0` |
| `DORSAL_MCP_SEVERE_STRETCH_COUNT` | `0` |
| `DORSAL_MCP_FACE_REVERSAL` | `0` |
| `DORSAL_MCP_DEGENERATE` | `0` |
| `DORSAL_MCP_COLLAPSE` | `0` |
| `DORSAL_MCP_FULL_STAGE6A_MACHINE` | `PASS` |
| `DORSAL_MCP_HUMAN_VISUAL_STATUS` | `PENDING_HUMAN_REVIEW` |
| `MACHINE_HARD_BLOCKER_COUNT` | `9` |
| `MACHINE_HARD_BLOCKER_CASE_COUNT` | `3` |
| `FAILING_CASES` | `['IDX_MCP_15', 'IDX_MCP_30', 'TH_IP_15']` |
| `HUMAN_REVIEW_ITEM_COUNT` | `42` |
| `INHERITED_STATIC_DEBT_COUNT` | `16` |
| `INHERITED_STATIC_DEBT_TRUE_FAILURE_COUNT` | `0` |
| `STATIC_DEBT_STATUS` | `NOT_RESOLVED` |
| `PRODUCTION_DRIFT` | `0` |
| `FULL_STAGE6A_MACHINE_QUALIFICATION` | `FAIL` |
| `FULL_STAGE6A_REQUALIFICATION_AFTER_DONOR_TRANSFER_R1` | `FAIL_CLOSED_FULL_STAGE6A_REQUALIFICATION` |
| `CURRENT_FULL_STAGE6A_STATUS` | `FAIL_CLOSED_FULL_STAGE6A_REQUALIFICATION` |
| `OLD_FULL_STAGE6A_STATUS` | `HISTORICAL_PRE_DONOR_RESULT` |
| `OLD_FULL_STAGE6A_RAW_VERDICT` | `FAIL_CLOSED_FULL_STAGE6A_REQUALIFICATION` |
| `DEFORMATION_FINAL` | `NOT_SET_PENDING_HUMAN_REVIEW` |
| `HARNESS_FINAL_POSE` | `ZERO / RSSF` |
| `STAGE6B_STARTED` | `False` |
| `PRODUCTION_PROMOTION` | `NO` |
| `PRODUCTION_SAVE_COUNT` | `0` |
| `GEOMETRY_WEIGHT_BONE_GROUP_MODIFIER_MUTATION_COUNT` | `0` |
| `FULL42_FORMAL_POSE_APPLICATIONS` | `42` |
| `HISTORICAL_FULL42_POSE_APPLICATIONS` | `0` |
| `HISTORICAL_AXIS_SIGN_SANITY_POSE_APPLICATIONS` | `28` |
| `NEXT` | `HUMAN_ADJUDICATE_CURRENT_FULL_STAGE6A_CROSSINGS` |
| `NEXT_EXECUTED` | `False` |
| `STOP` | `True` |

## Current blockers and old9 remeasurement

当前9个未批准的formal pose-generated severe exact crossing，分布IDX_MCP15(1)、IDX_MCP30(2)、TH_IP15(6)。全部同pose/pair坐标与严重度精确不变；DISAPPEARED/REDUCED/INCREASED/NEW_BLOCKER均0。V2 Class A不是自动的可见教学缺陷判决，当前NEXT为Human adjudication，未修geometry/skin。

| Case / Pair | Poke mm old/current | Bind facet mm | Segment mm old/current | Delta |
|---|---:|---:|---:|---|
| IDX_MCP_15 [377, 1054] | 4.291852237657 / 4.291852237657 | 3.656398753641 | 0.571132346947 / 0.571132346947 | UNCHANGED_EXACT |
| IDX_MCP_30 [1036, 2732] | 3.643731877673 / 3.643731877673 | 3.499050362724 | 0.622803602530 / 0.622803602530 | UNCHANGED_EXACT |
| IDX_MCP_30 [1226, 2742] | 4.881278495304 / 4.881278495304 | 4.166144603819 | 0.225100612494 / 0.225100612494 | UNCHANGED_EXACT |
| TH_IP_15 [77, 408] | 5.135486775544 / 5.135486775544 | 4.234161501363 | 0.160551215443 / 0.160551215443 | UNCHANGED_EXACT |
| TH_IP_15 [376, 1050] | 4.038801154820 / 4.038801154820 | 3.764636363676 | 0.390457303385 / 0.390457303385 | UNCHANGED_EXACT |
| TH_IP_15 [377, 1048] | 4.875181417447 / 4.875181417447 | 4.015601435462 | 0.491366744538 / 0.491366744538 | UNCHANGED_EXACT |
| TH_IP_15 [405, 1946] | 3.677946180687 / 3.677946180687 | 3.526704228757 | 1.224818773652 / 1.224818773652 | UNCHANGED_EXACT |
| TH_IP_15 [407, 1944] | 3.229683377867 / 3.229683377867 | 3.078656727932 | 1.602101430834 / 1.602101430834 | UNCHANGED_EXACT |
| TH_IP_15 [1944, 2743] | 3.229683377867 / 3.229683377867 | 3.178365369576 | 0.208966459371 / 0.208966459371 | UNCHANGED_EXACT |

[Matched full surface / pair evidence](../../../../../examples/historical/production_spec/stage6_deformation/full_stage6a_requalification_after_donor_transfer_r1/review.html)。pair[1226,2742]在IDX_MCP30无Human批准，45°收据不覆盖30°。

## Complete crossing discovery and counting

CURRENT_TOTAL_EXACT_CROSSING_COUNT=2099为完整native nonshared-vertex exact observations，单位case/pair。它分为1849个fresh native-bind SOURCE_EXISTING_CONTACT与250个formal pose-generated crossing；后者=247 unapproved＋3 known accepted，正式unapproved severe9。

原有corrected Full Stage6A gate在每个fresh native bind重新测基线pair；SOURCE_EXISTING_CONTACT独立保留，不伪称Human-approved，也不恢复broadphase/proxy权限。其中68个source Class A observations另行完整披露，它们在same-pose旧/current数值精确一致，并未由donor transfer新增。若把所有source Class A与formal unapproved Class A加总，则非Human-approved Class A context为77；这个context总量不等于既有corrected formal machine blocker数量。

Current new case/pair0。旧2307→current2099，消失208个case/pair observations，属于5个native pair；它们是donor ROI源既有contact移除，并非旧9 severe blocker消失。全部新/旧交叉来自fresh current42坐标与immutable历史坐标的同一现有exact kernel测量，不启动历史Full42。

## Prior Human exact scope

TH_IP30[1225,2740]，IDX_MCP45[1041,2735]、[1226,2742]在本轮再次fresh measured，fixture完整support坐标等于targeted已验证current derivative和pre-donor，severity精确相同；没有新结构失败，因此NON_BLOCKING。OLD_CAP9 TH_IP45也精确reproduce，不重复批准。其余三个CMC/opposition reviewed fixtures不属于本轮42 matrix，原targeted receipt受保护，不新增pose，不扩大批准。

## Donor ROI and non-target response

54点、95incident faces、148incident edges及first fixed outer ring在全部42 endpoints下再检；native fans对whole mesh使用reconciled rational shared-feature subtraction、component/features/extent comparison与continuous linear-chord nonzero fan area补证；当前bind→posed与pre/current same pose均newcontact0、newdegenerate0、newnativefanbowtie0、newboundaryfoldmigration0。线性chord补证不是实际连续运动碰撞资格。fixed reference normal rotation只是诊断，不当作新的anatomy gate。

RING15/30/45在formal42中各执行一次，对应原RNG IDs，没有额外case。匹配full/close/grazing/native strain图已检查：尖锐dent未重现，浅谷仍保持，无明显新ridge/notch/tear/flap/collapse。DORSAL_MCP_FULL_STAGE6A_MACHINE=PASS，但DORSAL_MCP_HUMAN_VISUAL_STATUS=PENDING_HUMAN_REVIEW，FINAL_VISUAL_PASS=false。细微crease/pinching/自然轮廓等待本轮Full Stage6A Human视觉资格。

所有case既有own-family clean shaft与forearm fresh motion0，formal0.001mm gate不变。non-target MCP support、sanctioned共享web另行记录；RING15/30/45的MIDDLE/LITTLE clean及MCP位移均0，没有额外邻指probe。

## Other machine gates and debt

NaN/Inf、collapsed/degenerate、topology drift、severe(bind≥3mm且ratio>5x)、TIP helper influence均0。14joint tip palmar trajectories均monotonic。21bones/rest/weights/UV/group/modifier/native geometry before/after完全相同。每个case pre/post ZERO回到同一个current bind为exact0；raw stored RSSF残差5.9670092462157264e-05mm低于既有0.0001mm，未放宽。

所有42case保存native nail components、cap37核心及continuity、old9 INDEX、FIRST_WEB21/fresh bounded collar、local surface/edge/normal/displacement/strain/compression诊断。仅普通crease和compression为Human visual item，不造新anatomy门槛；ray thickness/proxy不作collapse/crossing authority。

16inherited static debts按本轮相关formal target bone subset复核，包括15° cases，endpoint/incident patch无true failure。仍NOT_RESOLVED，不删除或扩大scope。

## Execution and protection

42fresh formal target pose applications，28historical±5° axis/sign sanity applications仅验证旧sign。每case reset→ZERO验证→one-joint apply→depsgraph→metrics→matched render→reset→restore验证。production/harness blend saves均0。CPU pure exact-kernel cache只允许本轮complete byte-identical fan inputs，whole-mesh broadphase对每case重新执行，未复用previous evaluated pose。全部旧文件最终hash验证见独立记录。

当前production SHA256 `d8ea48d5d09635a46aebabb7a6e516f2a2a8599c92f2ca68489cdbeb0ec6866d`；weight hash `1d9437a10354cdd98a2b5cb5e43be8cfabc519e232235483a615e76898129f55`；corrected rig SHA256 `5d5f86bb59135715a77515468c2b76fe81e2a44e2e8c5d6c17fcc3d56d2147fe`。true-cap仅context，没有重算或用于stretch gate。frozen cap37、FIRSTWEB21、R3 side/leakage context没有solver rerun。

OLD_FULL_STAGE6A_STATUS=HISTORICAL_PRE_DONOR_RESULT，历史事实不删。CURRENT_FULL_STAGE6A_STATUS=FAIL_CLOSED_FULL_STAGE6A_REQUALIFICATION，active current qualification由本轮fresh measurement supersede旧结果，不改变旧timepoint status。

**NEXT=HUMAN_ADJUDICATE_CURRENT_FULL_STAGE6A_CROSSINGS；STOP。DEFORMATION_FINAL=NOT_SET_PENDING_HUMAN_REVIEW。Stage6B、repair、Human approval和production promotion未执行。**

[Review](../../../../../examples/historical/production_spec/stage6_deformation/full_stage6a_requalification_after_donor_transfer_r1/review.html) · [Current exact crossing audit](../../../../artifacts/cc8df53f52af4456ce62.md) · [Old9 forced measurement](../../../../../examples/historical/production_spec/stage6_deformation/full_stage6a_requalification_after_donor_transfer_r1/OLD_9_BLOCKER_FRESH_REMEASUREMENT_R1.json)

## Independent final delivery verification

4195个预存workspace文件SHA256逐个完全相同，changed/deleted/new-outside-phase均0。286776条独立全mesh edge-ratio复算，最大float64与历史float32比例极值差6.63862258498682e-08；正式3mm/>5x gate未改变。320张PNG、160对matched camera/scale有效，focus clipping0。原Blender运行时AST及独立clean native reopen PASS，R2全3416权重与frozen corrected rig一致。

交付验证=PASS；变形资格仍=FAIL_CLOSED_FULL_STAGE6A_REQUALIFICATION。当前9个blocker基于fresh42，不继承历史verdict。NEXT=HUMAN_ADJUDICATE_CURRENT_FULL_STAGE6A_CROSSINGS，未执行；STOP。
