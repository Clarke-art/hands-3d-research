# R3_FULL_RECOMPUTE_AND_AUTHORITY_REVALIDATION_R1

Verdict: **TECHNICALLY_VALID_BUT_HUMAN_REVIEW_REQUIRED**. Fresh solver and source preservation pass; sheet identity revalidation fails. The Human Review page is generated. No new ownership result is Human-approved or frozen.

## Results

| Metric | Result |
| --- | --- |
| Human contract approval verified | YES |
| Contract canonical hash verified | YES |
| Graph V / E | 962 / 1881 |
| THUMB / INDEX hard sources | 57 / 145 |
| Source conflicts | 0 |
| INF | 387237777 |
| Fresh dT / dI unreachable | 0 / 0 |
| Min-cut flow | 34026920 |
| Final THUMB / INDEX | 498 / 464 |
| Cut edge count | 20 |
| Unary / pairwise capacities | 34001000 / 25920 |
| Unary / pairwise ratio | 1311.766975308642 |
| Closure iterations / converged / changed | 1 / YES / 0 |
| Boundary edges / vertex components / face strips | 20 / 18 / 1 |
| INDEX sheet / body-THUMB side | UNRESOLVED: identity collision in single full face-dual component |
| Islands | 0 |
| Ambiguity vertices | 21 |
| CLASS_A pass | 6/6 |
| FIRST_WEB21 THUMB / INDEX | 7 / 14 |
| Old cap9 hard role count | 0 |
| Old cap9 THUMB / INDEX | 0 / 9 |
| Cap37 / INDEX source preservation | PASS / PASS |
| Historical to fresh changed | 316 |
| Human Review generated | YES |
| Blend writes / skin rebuilds / Stage6 | 0 / 0 / 0 |
| NEXT | HUMAN_R3_FRESH_RESULT_APPROVAL |
| STOP | True |

## Approved input binding

The sole formal response is `R3_RECOVERY_INPUT_CONTRACT_HUMAN_REVIEW_R1_RESPONSE_2026-10-03T10-43-37-453Z.json` (SHA-256 `8662003bc366f7d340a1b8e5d45610e68988cfbf538f1a1613686e92fac7d1d9`). Its review ID, contract ID, Q1–Q7=YES, Q8=APPROVE_INPUT_CONTRACT, true approval fields, authorized phase, validation_mode=false and automatic_solver_execution=false were checked exactly. This user-requested execution is a separate explicit phase, not an automatic reaction to response export.

Canonical contract SHA-256: `f392fd33be0430cabf4b849fb8a4565853c245f2cf09e953d506493c93ca3cab`. Canonicalization: UTF-8, sorted keys, compact comma/colon separators, array order retained, no newline. Frozen proximal authority canonical SHA-256: `5ff37ae7d0915e1ab3b57b00f261b47b038e78a0bf1d316d0c52c39d5b063afb`. Every contract reference and source reference inside bound component contracts was verified; see R3_PRE_SOLVE_GATES_R1.json. Actual values equal all supplied summary expectations, so count differences are empty.

The exact hash-verified graph was consumed without selecting or rebuilding a different workspace. Original face cyclic edges prove real surface support, graph connectivity and hard-source reachability. Other-digit exclusion and independent wrist landmark two-ring exclusion produce zero leakage; 19 uncertain wrist structural candidates remain neutral workspace by the approved contract. ENGINEERING GRAPH != ANATOMICAL OWNERSHIP MAP.

## Fresh computation and exact energy

Fresh multi-source Dijkstra consumed the frozen RSSF coordinates and contract graph edges: `norm(world_m[u]-world_m[v])*1000` exactly once. Source sets are the approved unique 57 THUMB and 145 INDEX vertices; no historical dT/dI, R2/R3 labels or old THUMB_STRONG/tube/FIRST_WEB/cage/cap9 anchor is used. THUMB sources are precisely cap37 union approved thumb nail. Current neutral count is 760. THUMB max dT=188.29026988293873 mm, INDEX max dI=174.50488593745433 mm. Finite cap hits are 0 / 0; exact ties=0, integer-capacity ties=0.

Finite capacities use `min(400000, round(distance_mm*1000))`, Python ties-to-even. TAU=3.888204946698 mm; TAU/3=1.296068315566 mm, integer capacity=1296. For an unlike undirected edge, exactly one 1296 capacity counts in the cut; there is no edge length multiplier. Recomputed B=962*400000+1881*1296=387237776, INF=B+1=387237777. Source terminal encoding is SRC→v=cost(INDEX), v→SNK=cost(THUMB); each unique hard source has exactly one INF constraint, own-label terminal cost zero.

Min-cut flow=34026920, equal to cut energy 34001000 unary + 25920 pairwise. Capacity/mm scale is 1000, so these are 34001.000 and 25.920 mm-equivalent cost. Unary/pairwise=1311.766975308642. This actual energy is unary-dominated; balanced energy was not required and no tuning toward history occurred. Closure consumes fresh labels only, uses sorted components and THUMB then INDEX full sweeps, checks immutable pins after each update, accumulates all changes, and checks state cycles / 20-sweep cap. It converged in one complete sweep with zero changes; raw and final energy/labels coincide. Deterministic fresh rerun agrees, and independent Edmonds-Karp optimal flow=34026920 agrees with Dinic.

## Derived authority revalidation

Boundary has 20 unlike-label original surface edges. Vertex-edge adjacency yields 18 components; boundary edges incident to a common face form one coherent face strip. Both metrics are reported because ladder cross edges need not share vertices. Neither count was constrained toward the historical 16-edge boundary.

**Sheet split FAIL_REVALIDATION_REVIEW_REQUIRED:** exactly the approved full frozen face-dual method was executed, removing only the 20 fresh unlike-label cut edges. It yields 1 component containing all 3414 faces / 3416 vertices. Independent INDEX v233 + INDEX nail and THUMB v284 + cap37 + THUMB nail consistently identify that same component. This is an identity collision, not a valid separate INDEX sheet. INDEX sheet vertex count and body/THUMB-side count are therefore `null`/UNRESOLVED, not zero and not assigned by rank. A connected label region cannot substitute for this independent full-mesh sheet identity gate. The HTML shows the failed split explicitly, not a fabricated sheet.

Islands=0: each induced label component contains its own hard source, and none is auto-repaired beyond permitted closure. Every component includes IDs, involved faces, source overlap and fresh distance summaries in the island audit. Fresh ambiguity is abs(dT-dI)<TAU on 21 vertices; records include both distances, difference, boundary geodesic distance, label and FIRST_WEB/band relation. The old 16 vertices were not reused.

All 6 CLASS_A frozen geometry edges retain ID, endpoints and surface support. Fresh endpoints are INDEX/INDEX, so none is cut and protection passes 6/6. The geometry-authority semantics are DO_NOT_CUT, without imposing historical THUMB ownership. Labels were never changed to make this pass.

P04/P05 e4666/e4668 retain semantic STOP_AFTER_P04 only. Neither edge is forced into the fresh cut; band membership and no-hard-pin design remain exactly frozen. No broader proximal anatomy or pointwise ownership authority is inferred. FIRST_WEB21 distribution is THUMB 7 / INDEX 14, hard pins=0, with no anatomy writeback. Old cap9 all become INDEX with hard role NONE; cap37 all remain THUMB sources, and all 145 INDEX sources remain INDEX.

CMC geometry remains frozen. Existing 73-coordinate approximate construction candidates and 120-point unfiltered historical confinement context are separately evaluated; they are not hard sources or exact protection-mask authority. Their graph-participating points are INDEX and remaining points are explicitly unassigned, with no observed THUMB/INDEX partition conflict. The independent wrapper definition remains unresolved, as already established in the approved input contract; no cage geometry or mask is edited and no old/new-label filtering becomes authority.

## Historical comparison only

Historical full-mesh counts: THUMB 791 / INDEX 217; on current graph THUMB 653 / INDEX 217 / wrist 85 / MIDDLE 7. Fresh graph counts are THUMB 498 / INDEX 464; outside graph stays unassigned. Current-graph changed count=316 (224 formerly THUMB/INDEX, 92 formerly wrist/MIDDLE). Boundary 16→20, ambiguity 16→21, flow 33529→34026920. Historical sheet 217/3199 used a vertex adjacency cut method; fresh validator requires the approved full face dual method and cannot confirm separate sheets. Historical outputs are unchanged. **DIFFERENCE != FAILURE**: changed inputs, units, graph, cap and kinematic authority make historical labels/boundary/flow comparison evidence only. Sheet failure is an independently checked validator failure, not a penalty for differing from history.

## Human Review and protection

`R3_FRESH_RESULT_HUMAN_REVIEW.html` is self-contained and provides native/RSSF fresh views, same-coordinate old/new ownership, fresh/old boundary, explicit failed sheet/counterpart context, FIRST_WEB21, cap37, old cap9, fresh ambiguity, CLASS_A, CMC, source maps, energy and changed-label map. Q1–Q7 are real unselected controls with Notes and JSON export. Export binds contract/result/proximal hashes and includes the unresolved sheet blocker. QA uses `?validation=1`, prevents downloads and marks previews AUTOMATED_UI_VALIDATION_NOT_HUMAN. No automatic apply, freeze, skin or Stage6 action exists. Candidate acceptance is separate from frozen authority and downstream execution.

All 1939 pre-existing workspace files were hashed before and after; zero file deltas, including every historical R2/R3/R1B/R1C/R1D/R1E/Stage6 artifact, authority, response and blend. The external formal Human response hash also stays unchanged. BLEND_FILES_WRITTEN=0; WEIGHT_DELTA=GEOMETRY_DELTA=TOPOLOGY_DELTA=BONE_DELTA=JOINT_DELTA=0. Blender was never launched.

One optional independent-verification dependency was absent after the first solve; it was replaced with a standard-library Edmonds-Karp verifier. Resume checked the original frozen inventory and input approval again before fresh recomputation. The recovered diagnostic is retained in R3_EXECUTION_FAILURE_R1.json; it is not the effective final verdict.

NEXT: **HUMAN_R3_FRESH_RESULT_APPROVAL**. Fresh result remains a review candidate with sheet identity revalidation unresolved. A later separately authorized phase is CAP_SKIN_DRIVER_AND_WEIGHT_AUTHORITY_RECONCILIATION_R1, after Human approval. No next phase was started. **STOP**.
