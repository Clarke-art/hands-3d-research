import sys
sys.dont_write_bytecode=True
import json,hashlib,datetime
from pathlib import Path
from recompute import OUT,ROOT,read,dump,sha,inventory,RESPONSE,RUN
S=read(OUT/(RUN+'_STATUS.json'));C=read(OUT/'R3_HISTORICAL_VS_FRESH_COMPARISON_R1.json');fields=read(OUT/'FRESH_R3_UNARY_FIELDS_R1.json');sheet=read(OUT/'R3_FRESH_SHEET_SPLIT_AUDIT_R1.json');repro=read(OUT/'R3_FRESH_REPRODUCIBILITY_AUDIT_R1.json')
before=read(OUT/'FROZEN_HASHES_BEFORE.json');after=inventory();delta={k:{'before':before.get(k),'after':after.get(k)} for k in before.keys()|after.keys() if before.get(k)!=after.get(k)}
assert not delta and sha(RESPONSE)==read(OUT/'R3_PRE_SOLVE_GATES_R1.json')['Human_response_sha256']
dump('FROZEN_HASHES_AFTER.json',after);dump('FROZEN_HASH_VERIFICATION_R1.json',{'pass':True,'protected_file_count':len(before),'delta':{},'Human_response_sha256_unchanged':True,'BLEND_FILES_WRITTEN':0,'all_historical_and_production_files_unchanged':True})
if (OUT/'R3_EXECUTION_FAILURE_R1.json').exists():
 failure=read(OUT/'R3_EXECUTION_FAILURE_R1.json');failure.update({'recovered':True,'recovery':'Missing optional NetworkX dependency replaced with independent standard-library Edmonds-Karp. Resume revalidated all hashes, preserved original frozen inventory, and reran deterministic fresh solve.','effective_final_verdict':S['technical_validation_verdict']});dump('R3_EXECUTION_FAILURE_R1.json',failure)
dump('R3_EXECUTION_RECEIPT_R1.json',{'finished':True,'phases':['all pre-solve hash/approval/graph/source gates','fresh Dijkstra mm','fresh exact min-cut','full-sweep closure','fresh labels','boundary/sheet/island/ambiguity and authority wrapper validators','history first loaded after solve','deterministic rerun','independent Edmonds-Karp optimum verification','self-contained review UI and safe response export verification','frozen inventory after comparison'],'technical_verdict':S['technical_validation_verdict'],'historical_solver_script_executed':False,'Blender_launched':False,'blend_write_calls':0,'skin_rebuild_count':0,'Stage6_runs':0,'Human_approval_awaited':True,'STOP':True})
items=[('Human contract approval verified',S['Human_contract_approval_verified']),('Contract canonical hash verified',S['contract_hash_verified']),('Graph V / E',f"{S['graph_V']} / {S['graph_E']}"),('THUMB / INDEX hard sources',f"{S['THUMB_hard_source_count']} / {S['INDEX_hard_source_count']}"),('Source conflicts',S['source_conflicts']),('INF',S['INF']),('Fresh dT / dI unreachable',f"{S['fresh_dT_unreachable_count']} / {S['fresh_dI_unreachable_count']}"),('Min-cut flow',S['mincut_flow']),('Final THUMB / INDEX',f"{S['fresh_THUMB_count']} / {S['fresh_INDEX_count']}"),('Cut edge count',S['cut_edge_count']),('Unary / pairwise capacities',f"{S['total_unary_cost']} / {S['total_pairwise_cost']}"),('Unary / pairwise ratio',S['unary_pairwise_ratio']),('Closure iterations / converged / changed',f"{S['closure_iterations']} / {S['closure_converged']} / {S['closure_changed_count']}"),('Boundary edges / vertex components / face strips',f"{S['final_boundary_edge_count']} / {S['boundary_component_count']} / {S['boundary_face_strip_component_count']}"),('INDEX sheet / body-THUMB side','UNRESOLVED: identity collision in single full face-dual component'),('Islands',S['islands_count']),('Ambiguity vertices',S['ambiguity_vertex_count']),('CLASS_A pass',f"{S['CLASS_A_pass_count']}/6"),('FIRST_WEB21 THUMB / INDEX',f"{S['FIRST_WEB21_distribution']['THUMB']} / {S['FIRST_WEB21_distribution']['INDEX']}"),('Old cap9 hard role count',S['old_cap9_hard_role_count']),('Old cap9 THUMB / INDEX','0 / 9'),('Cap37 / INDEX source preservation',f"{S['cap37_preservation']} / {S['INDEX_hard_source_preservation']}"),('Historical to fresh changed',S['historical_to_fresh_changed_labels']),('Human Review generated',S['Human_Review_page_generated']),('Blend writes / skin rebuilds / Stage6','0 / 0 / 0'),('NEXT',S['NEXT']),('STOP',True)]
table='\n'.join(f'| {k} | {v} |' for k,v in items)
report=f'''# {RUN}

Verdict: **{S['technical_validation_verdict']}**. Fresh solver and source preservation pass; sheet identity revalidation fails. The Human Review page is generated. No new ownership result is Human-approved or frozen.

## Results

| Metric | Result |
| --- | --- |
{table}

## Approved input binding

The sole formal response is `{RESPONSE.name}` (SHA-256 `{sha(RESPONSE)}`). Its review ID, contract ID, Q1–Q7=YES, Q8=APPROVE_INPUT_CONTRACT, true approval fields, authorized phase, validation_mode=false and automatic_solver_execution=false were checked exactly. This user-requested execution is a separate explicit phase, not an automatic reaction to response export.

Canonical contract SHA-256: `f392fd33be0430cabf4b849fb8a4565853c245f2cf09e953d506493c93ca3cab`. Canonicalization: UTF-8, sorted keys, compact comma/colon separators, array order retained, no newline. Frozen proximal authority canonical SHA-256: `5ff37ae7d0915e1ab3b57b00f261b47b038e78a0bf1d316d0c52c39d5b063afb`. Every contract reference and source reference inside bound component contracts was verified; see R3_PRE_SOLVE_GATES_R1.json. Actual values equal all supplied summary expectations, so count differences are empty.

The exact hash-verified graph was consumed without selecting or rebuilding a different workspace. Original face cyclic edges prove real surface support, graph connectivity and hard-source reachability. Other-digit exclusion and independent wrist landmark two-ring exclusion produce zero leakage; 19 uncertain wrist structural candidates remain neutral workspace by the approved contract. ENGINEERING GRAPH != ANATOMICAL OWNERSHIP MAP.

## Fresh computation and exact energy

Fresh multi-source Dijkstra consumed the frozen RSSF coordinates and contract graph edges: `norm(world_m[u]-world_m[v])*1000` exactly once. Source sets are the approved unique 57 THUMB and 145 INDEX vertices; no historical dT/dI, R2/R3 labels or old THUMB_STRONG/tube/FIRST_WEB/cage/cap9 anchor is used. THUMB sources are precisely cap37 union approved thumb nail. Current neutral count is 760. THUMB max dT={fields['dT']['maximum_mm']} mm, INDEX max dI={fields['dI']['maximum_mm']} mm. Finite cap hits are {fields['dT']['finite_cap_hits']} / {fields['dI']['finite_cap_hits']}; exact ties={fields['exact_tie_count']}, integer-capacity ties={fields['integer_capacity_tie_count']}.

Finite capacities use `min(400000, round(distance_mm*1000))`, Python ties-to-even. TAU=3.888204946698 mm; TAU/3=1.296068315566 mm, integer capacity=1296. For an unlike undirected edge, exactly one 1296 capacity counts in the cut; there is no edge length multiplier. Recomputed B=962*400000+1881*1296=387237776, INF=B+1=387237777. Source terminal encoding is SRC→v=cost(INDEX), v→SNK=cost(THUMB); each unique hard source has exactly one INF constraint, own-label terminal cost zero.

Min-cut flow=34026920, equal to cut energy 34001000 unary + 25920 pairwise. Capacity/mm scale is 1000, so these are 34001.000 and 25.920 mm-equivalent cost. Unary/pairwise=1311.766975308642. This actual energy is unary-dominated; balanced energy was not required and no tuning toward history occurred. Closure consumes fresh labels only, uses sorted components and THUMB then INDEX full sweeps, checks immutable pins after each update, accumulates all changes, and checks state cycles / 20-sweep cap. It converged in one complete sweep with zero changes; raw and final energy/labels coincide. Deterministic fresh rerun agrees, and independent Edmonds-Karp optimal flow={repro['independent_flow']} agrees with Dinic.

## Derived authority revalidation

Boundary has 20 unlike-label original surface edges. Vertex-edge adjacency yields 18 components; boundary edges incident to a common face form one coherent face strip. Both metrics are reported because ladder cross edges need not share vertices. Neither count was constrained toward the historical 16-edge boundary.

**Sheet split FAIL_REVALIDATION_REVIEW_REQUIRED:** exactly the approved full frozen face-dual method was executed, removing only the 20 fresh unlike-label cut edges. It yields {sheet['face_component_count']} component containing all 3414 faces / 3416 vertices. Independent INDEX v233 + INDEX nail and THUMB v284 + cap37 + THUMB nail consistently identify that same component. This is an identity collision, not a valid separate INDEX sheet. INDEX sheet vertex count and body/THUMB-side count are therefore `null`/UNRESOLVED, not zero and not assigned by rank. A connected label region cannot substitute for this independent full-mesh sheet identity gate. The HTML shows the failed split explicitly, not a fabricated sheet.

Islands=0: each induced label component contains its own hard source, and none is auto-repaired beyond permitted closure. Every component includes IDs, involved faces, source overlap and fresh distance summaries in the island audit. Fresh ambiguity is abs(dT-dI)<TAU on 21 vertices; records include both distances, difference, boundary geodesic distance, label and FIRST_WEB/band relation. The old 16 vertices were not reused.

All 6 CLASS_A frozen geometry edges retain ID, endpoints and surface support. Fresh endpoints are INDEX/INDEX, so none is cut and protection passes 6/6. The geometry-authority semantics are DO_NOT_CUT, without imposing historical THUMB ownership. Labels were never changed to make this pass.

P04/P05 e4666/e4668 retain semantic STOP_AFTER_P04 only. Neither edge is forced into the fresh cut; band membership and no-hard-pin design remain exactly frozen. No broader proximal anatomy or pointwise ownership authority is inferred. FIRST_WEB21 distribution is THUMB 7 / INDEX 14, hard pins=0, with no anatomy writeback. Old cap9 all become INDEX with hard role NONE; cap37 all remain THUMB sources, and all 145 INDEX sources remain INDEX.

CMC geometry remains frozen. Existing 73-coordinate approximate construction candidates and 120-point unfiltered historical confinement context are separately evaluated; they are not hard sources or exact protection-mask authority. Their graph-participating points are INDEX and remaining points are explicitly unassigned, with no observed THUMB/INDEX partition conflict. The independent wrapper definition remains unresolved, as already established in the approved input contract; no cage geometry or mask is edited and no old/new-label filtering becomes authority.

## Historical comparison only

Historical full-mesh counts: THUMB 791 / INDEX 217; on current graph THUMB 653 / INDEX 217 / wrist 85 / MIDDLE 7. Fresh graph counts are THUMB 498 / INDEX 464; outside graph stays unassigned. Current-graph changed count=316 (224 formerly THUMB/INDEX, 92 formerly wrist/MIDDLE). Boundary 16→20, ambiguity 16→21, flow 33529→34026920. Historical sheet 217/3199 used a vertex adjacency cut method; fresh validator requires the approved full face dual method and cannot confirm separate sheets. Historical outputs are unchanged. **DIFFERENCE != FAILURE**: changed inputs, units, graph, cap and kinematic authority make historical labels/boundary/flow comparison evidence only. Sheet failure is an independently checked validator failure, not a penalty for differing from history.

## Human Review and protection

`R3_FRESH_RESULT_HUMAN_REVIEW.html` is self-contained and provides native/RSSF fresh views, same-coordinate old/new ownership, fresh/old boundary, explicit failed sheet/counterpart context, FIRST_WEB21, cap37, old cap9, fresh ambiguity, CLASS_A, CMC, source maps, energy and changed-label map. Q1–Q7 are real unselected controls with Notes and JSON export. Export binds contract/result/proximal hashes and includes the unresolved sheet blocker. QA uses `?validation=1`, prevents downloads and marks previews AUTOMATED_UI_VALIDATION_NOT_HUMAN. No automatic apply, freeze, skin or Stage6 action exists. Candidate acceptance is separate from frozen authority and downstream execution.

All {len(before)} pre-existing workspace files were hashed before and after; zero file deltas, including every historical R2/R3/R1B/R1C/R1D/R1E/Stage6 artifact, authority, response and blend. The external formal Human response hash also stays unchanged. BLEND_FILES_WRITTEN=0; WEIGHT_DELTA=GEOMETRY_DELTA=TOPOLOGY_DELTA=BONE_DELTA=JOINT_DELTA=0. Blender was never launched.

One optional independent-verification dependency was absent after the first solve; it was replaced with a standard-library Edmonds-Karp verifier. Resume checked the original frozen inventory and input approval again before fresh recomputation. The recovered diagnostic is retained in R3_EXECUTION_FAILURE_R1.json; it is not the effective final verdict.

NEXT: **HUMAN_R3_FRESH_RESULT_APPROVAL**. Fresh result remains a review candidate with sheet identity revalidation unresolved. A later separately authorized phase is CAP_SKIN_DRIVER_AND_WEIGHT_AUTHORITY_RECONCILIATION_R1, after Human approval. No next phase was started. **STOP**.
'''
(OUT/(RUN+'_REPORT.md')).write_text(report,encoding='utf8')
required=[RUN+'_REPORT.md',RUN+'_STATUS.json','FRESH_R3_UNARY_FIELDS_R1.json','R3_HARD_PIN_CAPACITY_AUDIT_R1.json','R3_FRESH_MINCUT_RESULT_R1.json','R3_FRESH_ENERGY_AUDIT_R1.json','R3_FRESH_CLOSURE_AUDIT_R1.json','R3_FRESH_FINAL_LABELS_R1.json','R3_FRESH_BOUNDARY_AUDIT_R1.json','R3_FRESH_SHEET_SPLIT_AUDIT_R1.json','R3_FRESH_ISLAND_AUDIT_R1.json','R3_FRESH_AMBIGUITY_AUDIT_R1.json','R3_FRESH_CLASS_A_AUDIT_R1.json','R3_FRESH_FIRST_WEB21_AUDIT_R1.json','R3_FRESH_CMC_CONTEXT_AUDIT_R1.json','R3_OLD_CAP9_FRESH_RESULT_AUDIT_R1.json','R3_CAP37_SOURCE_PRESERVATION_AUDIT_R1.json','R3_INDEX_SOURCE_PRESERVATION_AUDIT_R1.json','R3_HISTORICAL_VS_FRESH_COMPARISON_R1.json','R3_FRESH_VALIDATION_VERDICT_R1.json','R3_FRESH_RESULT_HUMAN_REVIEW.html']
assert all((OUT/n).is_file() for n in required)
for p in OUT.glob('*.json'):read(p)
dump('FINAL_ARTIFACT_VERIFICATION_R1.json',{'pass':True,'required_artifact_count':len(required),'required_files':required,'JSON_parse_all_pass':True,'frozen_inventory_pass':True,'review_generated':True,'solver_technically_valid':True,'derived_sheet_revalidation_pass':False,'effective_verdict':S['technical_validation_verdict'],'STOP':True})
dump('OUTPUT_EVIDENCE_HASH_MANIFEST_R1.json',{p.name:sha(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='OUTPUT_EVIDENCE_HASH_MANIFEST_R1.json'})
print(json.dumps({'required_artifacts':len(required),'frozen_files':len(before),'unchanged':True,'verdict':S['technical_validation_verdict'],'review_generated':True,'STOP':True}))
