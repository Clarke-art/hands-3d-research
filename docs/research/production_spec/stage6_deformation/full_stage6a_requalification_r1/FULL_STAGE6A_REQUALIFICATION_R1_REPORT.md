# FULL_STAGE6A_REQUALIFICATION_R1_REPORT

FAIL_CLOSED_FULL_STAGE6A_REQUALIFICATION

42 formal isolated-flex cases completed on the sole current corrected R2, read-only. No production freeze, skin/rig/geometry change, R3 rerun, true-cap recomputation, or Stage6B.

## Qualification result

| Field | Value |
|---|---|
| FORMAL_CASE_COUNT | 42 |
| FORMAL_CASES_COMPLETED | 42 |
| FLEXION_AXIS_SIGN_QUALIFIED | PASS_LOCAL_X_HISTORICAL_MINUS_ONE |
| ZERO_RESTORE | PASS |
| NAN_INF_COUNT | 0 |
| COLLAPSED_FACE_COUNT | 0 |
| DEGENERATE_EDGE_COUNT | 0 |
| TOPOLOGY_DRIFT | 0 |
| SEVERE_EDGE_STRETCH_CASE_COUNT | 0 |
| SEVERE_EDGE_STRETCH_EDGE_COUNT | 0 |
| NEW_UNAPPROVED_EXACT_CROSSING_COUNT | 247 |
| NEW_UNAPPROVED_SEVERE_EXACT_CROSSING_COUNT | 9 |
| KNOWN_HUMAN_ACCEPTED_CONTACT_COUNT | 3 |
| NON_TARGET_DIGIT_CONTAMINATION | 0 |
| FOREARM_STABILITY | PASS |
| FOREARM_MOVEMENT_MAX_MM | 0.0 |
| TIP_TRAJECTORY_MONOTONIC | PASS |
| TIP_HELPER_DEFORMATION_INFLUENCE_COUNT | 0 |
| NAIL_DEFORMATION | MEASURED_42_CASES_NO_COLLAPSE_OR_TOPOLOGY_FAILURE_APPEARANCE_PENDING_HUMAN |
| CAP37_DEFORMATION | MEASURED_42_CASES_NO_SEVERE_STRETCH_OR_COLLAPSE_NEW_CONTACT_BLOCKERS_RECORDED_SEPARATELY |
| OLD_CAP9_INDEX_COMPATIBILITY | PASS_NATIVE_INDEX_NO_THUMB_OVERRIDE |
| MACHINE_HARD_BLOCKER_COUNT | 9 |
| MACHINE_HARD_BLOCKER_CASE_COUNT | 3 |
| FAILING_CASES | ['IDX_MCP_15', 'IDX_MCP_30', 'TH_IP_15'] |
| HUMAN_REVIEW_ITEM_COUNT | 42 |
| PRODUCTION_DRIFT | 0 |
| FULL_STAGE6A_MACHINE_QUALIFICATION | FAIL |
| FULL_STAGE6A_REQUALIFICATION_R1 | FAIL_CLOSED_FULL_STAGE6A_REQUALIFICATION |
| DEFORMATION_FINAL | NOT_SET_PENDING_HUMAN_REVIEW |
| NEXT | STOP_FAILURE_EVIDENCE_REQUIRES_INDEPENDENT_ADJUDICATION |
| STOP | True |
| STAGE6B_STARTED | False |
| AUTOMATIC_REPAIR_COUNT | 0 |

## Failure evidence and scope

9 unapproved severe exact pairs occur in IDX_MCP_15 (1), IDX_MCP_30 (2), TH_IP_15 (6). They are THUMB/INDEX contact surfaces, confirmed both by the fresh frozen labels and current functional driver families. This is a severe exact crossing qualification failure; V2 Class A is not an automatic visible teaching-defect, flap, tearing, or inversion judgment.

| Case | Faces | Affected vertices | poke mm | bind local facet mm | ratio | intersection segment mm |
|---|---|---|---|---|---|---|
| IDX_MCP_15 | [377, 1054] | [156, 285, 1071, 1342, 1344, 2177, 2574, 2743] | 4.291852238 | 3.656398754 | 1.173792173 | 0.571132347 |
| IDX_MCP_30 | [1036, 2732] | [150, 282, 1055, 1336, 1337, 2064, 2739, 3163] | 3.643731878 | 3.499050363 | 1.041348795 | 0.622803603 |
| IDX_MCP_30 | [1226, 2742] | [342, 654, 1381, 1385, 2063, 2068, 2786, 3165] | 4.881278495 | 4.166144604 | 1.171653641 | 0.225100612 |
| TH_IP_15 | [77, 408] | [39, 655, 880, 886, 1070, 2067, 2499, 2582] | 5.135486776 | 4.234161501 | 1.212869838 | 0.160551215 |
| TH_IP_15 | [376, 1050] | [155, 285, 1071, 1343, 1344, 2182, 2574, 2742] | 4.038801155 | 3.764636364 | 1.072826367 | 0.390457303 |
| TH_IP_15 | [377, 1048] | [36, 156, 890, 1071, 1341, 2177, 2574, 2742] | 4.875181417 | 4.015601435 | 1.214060084 | 0.491366745 |
| TH_IP_15 | [405, 1946] | [155, 505, 1068, 1069, 1754, 1755, 2581, 2966] | 3.677946181 | 3.526704229 | 1.042884785 | 1.224818774 |
| TH_IP_15 | [407, 1944] | [298, 653, 1066, 1380, 1454, 2068, 2581, 2966] | 3.229683378 | 3.078656728 | 1.049056021 | 1.602101431 |
| TH_IP_15 | [1944, 2743] | [298, 653, 1380, 1454, 2062, 2068, 2966, 3165] | 3.229683378 | 3.178365370 | 1.016146038 | 0.208966459 |

[统一审阅入口](../../../../../examples/historical/production_spec/stage6_deformation/full_stage6a_requalification_r1/review.html)。每个案例均含全手实体、背侧/掌侧局部实体、应变诊断和目标指甲。Thumb 与 INDEX MCP 另含 cap37；9 个严重 pair 与3个已批准 pair 都有独立取证实体及周围表面。

The pair [1226,2742] at IDX_MCP_30 is unapproved: the existing receipt covers IDX_MCP_45 only. No cross-pose acceptance extension was made. The three exact accepted pose/pair contacts reproduce their frozen numeric severity to 5 decimal places and remain non-blocking.

## Measurement and authority

All reset-before/after differences relative to the evaluated current bind mesh are exactly zero. Raw native RSSF float noise is 0.000059670092462 mm, below the unchanged 0.0001 mm zero gate. Non-target clean own-driver movement and forearm movement use the existing 0.001 mm gate. All TIP helpers remain non-deform, with zero vertex influence. CMC and WRIST remained locked.

Local patches reuse T01 kappa and approved bone-chain arc mathematics. THUMB/INDEX use ONLY the 962-vertex frozen fresh membership. Other three fingers and outside-domain clean audits use explicit own-family-only functional weight-support sets; these are not new anatomical ownership. Native nail material components are frozen by current topology, recorded explicitly and checked against fresh labels where available. FIRST_WEB21 is unchanged, uses only WRIST/TH_CMC/TH_MCP/IDX_MCP, and has exact-zero TH_IP/TIP influence.

Edge/face ratios, local surface area, compression, displacement, normal changes, tear-strain candidates, tip trajectories, cap37 plus approved continuity neighborhood, old9 native INDEX regression, and all exact crossings are recorded. The historical ray thickness proxy is formally DIAGNOSTIC_ONLY and is not used as collapse authority. Normal rotation or tear-strain alone is not called surface inversion/tearing. No cap/mesh topology separation, severe edge stretch or collapse was found; appearance remains for Human Review.

## Historical comparison

Actual Stage6A R1 input: Stage5B R1A. Actual Stage6A R1A input: Stage5B R1B candidate. Actual Stage6A R1B input: Stage5B R1C. The latter is not the R1B donor. Historical 42-case numeric tables are context only and their old broadphase intersection counts are not current exact severe counts. The old Stage6A validator blind spot is not inherited. Subsequent R1C gate amendment / V2 classifier, R1D/R1E/R2 targeted evidence, human receipts and static debt context were read; historical qualification suites were not rerun.

Corrected true-cap authority remains context only: 37 sources,19 INDEX endpoints,703 primary pairs, static path min81.76973560299072 mm, bounds0.6806198919342639 /0.6916621180243677. These are not Stage6A stretch, anatomy or skin PASS gates.

## Stop

FAIL CLOSED. Causes to adjudicate: pose contact and local skin/geometry interaction; this run does not establish a rig-rest defect. No authorized fixes were made. Final deformation approval is unset. Full Stage6B must not start. Production and historical protection verification is saved separately.

Final protection verification: all 2436 preexisting files retain exact SHA256; no writes outside this new round directory. The saved zero/RSSF harness reopened with an identical complete R2 mesh/rig/weight payload. Independent fresh-process reproduction matched all42 posed coordinate arrays and all12 severe/accepted exact-pair numeric records exactly.
