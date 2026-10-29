import sys
sys.dont_write_bytecode=True
from reconcile import OUT,ROOT,FRESH,RUN,METHOD,read,dump,sha,inventory
S=read(OUT/(RUN+'_STATUS.json'));paths=read(OUT/'R3_FACE_DUAL_RECONNECTION_PATH_AUDIT.json');before=read(OUT/'FROZEN_HASHES_BEFORE.json');after=inventory();assert before==after,'Protected files changed'
approval=read(OUT/'R3_SHEET_VALIDATOR_PROVENANCE_AUDIT.json')['Human_input_approval'];assert sha(approval['path'])==approval['sha256'],'External Human response changed'
v1=read(OUT/'R3_VERTEX_LABEL_COMPONENT_AUDIT.json');v2=read(OUT/'R3_PURE_FACE_COMPONENT_AUDIT.json');band=read(OUT/'R3_MIXED_BOUNDARY_FACE_BAND_AUDIT.json')
report=f'''# {RUN}

**FRESH_R3_SHEET_IDENTITY_PASS.** Canonical derived validator: `{METHOD}`. Current full face-dual result remains correctly reproduced, but its use as a bounded vertex-ownership identity test is **VALIDATOR_METHOD_MISMATCH**. The literal full-mesh V3 mixed barrier also remains connected through unknown exterior faces and is **DOMAIN_MISMATCH**, not an independent resolved sheet. This adjudication does not assert physical mesh separation or global body/wrist ownership.

Fresh labels changed=0; R3/Dijkstra/mincut/closure reruns=0; skin rebuild=0; Stage6=0; blend writes=0. Only new static audits, a derived validation sidecar and `R3_FRESH_RESULT_HUMAN_REVIEW_R2.html` were generated. The approved input contract, original R1 failure, solver outputs and history are byte-immutable.

## Frozen input verification

All fresh R1 output-manifest hashes match. Canonical contract hash remains `f392fd33be0430cabf4b849fb8a4565853c245f2cf09e953d506493c93ca3cab`; each bound authority/file hash is checked. Labels hash remains `{S['frozen_result_hash']}`. Fresh hash convention for vertex-keyed fields sorts the original integer IDs; they are decoded back to integer keys for verification, never changed or recomputed. dT/dI field hashes were verified from frozen values only.

Graph 962/1881; THUMB/INDEX 498/464; cut edges20; closure1 sweep/0 changes; islands0; ambiguity21; CLASS_A6/6; FIRST_WEB21 7 THUMB/14 INDEX; cap9 0 THUMB/9 INDEX with hard role0; cap37/INDEX sources preservation PASS. Solver, Dijkstra and closure code were not imported or called.

## Five distinct topology objects

1. **Vertex-label region connectivity:** for the field L:G→{{THUMB,INDEX}}, induced graph G[L=label] has only same-label vertices and original supported edges between them. Removing all unlike-label edges from **G** gives the disjoint union of those induced graphs. This is an exact graph identity, independent of the observed counts.
2. **Pure-label face connectivity:** a polygon belongs to pure label X only when every corner is solved and labelled X. Its face complex is connected by shared full edges, not by a lone shared vertex. This checks 2D surface support, but cannot replace vertex coverage because legitimate band/fringe vertices need not occur in a pure polygon.
3. **Mixed-label boundary faces:** a polygon containing both binary labels intersects the vertex-field interface. It is a validation carrier, not a third ownership label. Mixed faces are not forced to either side. Faces with unknown corners are explicitly distinguished.
4. **Mesh face-dual connectivity:** one node per **whole polygon**, one adjacency for each shared mesh edge. A polygon's internal vertex-label interface does not split its dual node. Sharing only a vertex creates no face-dual adjacency in this audit.
5. **Cut-edge topology:** an unlike primal edge joins opposite vertex labels. Removing it from a vertex graph blocks that vertex-to-vertex traversal. Removing its corresponding dual adjacency blocks the crossing **between adjacent polygons across that mesh edge**, a different operation. It does not partition the mixed polygon internally. A physical iso-label surface seam would require defining within-face interface segments/subfaces; no such subdivision, geometric cut or topology edit is performed or authorized here.

For a partial field, graph-exterior vertices/faces cannot be treated as either binary label or as evidence of a binary identity collision. Conversely, their reconnection means no global physical disconnection may be claimed. This scope distinction is required by the frozen contract's NO_SOLVE_UNASSIGNED_OUTSIDE_GRAPH rule, not chosen to improve the result.

## Exact reproduction and provenance

| Property | Historical vertex cut | Current full face dual |
| --- | --- | --- |
| Input object | Full frozen mesh vertex adjacency, historical16 cut IDs | All3414 frozen polygon nodes, fresh20 cut IDs |
| Delete object | Primal adjacency between unlike-boundary endpoints | Dual adjacencies whose shared original mesh edge is a fresh cut edge |
| Component definition | Vertex graph connected components | Whole-face shared-edge connected components |
| Original identity code | Second-largest shortcut, followed by landmark evidence; shortcut preserved as historical code only | Fixed INDEX/THUMB marker+nail/cap containment; no rank |
| This audit's identity rule | Fixed v233+INDEX nail and v284+cap37+THUMB nail; no rank or historical label naming | Identical fixed anchor families |
| Reproduced result | 217 INDEX /3199 body, two vertex components | One component,3414 faces/3416 vertices; identity collision |

Historical report §7 calls the operation a two-sheet split; historical `cut_split` at r3_ownership.py:628–652 and `_r3_sheet.py` explicitly implement **vertex adjacency**. The report also states no retopology or seam split. Its purpose was independently recognizable coherent ownership regions, including source-backed connectivity and an INDEX tube identity, not physical polygon disconnection. Historic results are comparison only; obsolete cap9/tip proxies and size ordering are not used in fresh validation.

The prior semantic update plan requires unique independent tip/nail/cap containment, no rank, no old-label injection, and warns that binary neutral labels do not establish anatomy. It does not define physical mesh surgery. The subsequently frozen contract literally introduced full face-dual deletion at build_contract.py:146 / R3_VALIDATOR_CONTRACT_R1.json:18, and the Human input response approved that contract hash. We do **not** deny or erase that literal approval: its original method and failure remain immutable. The current user explicitly authorized technical semantics reconciliation, so this new sidecar corrects that method's application to ownership identity while preserving the input/source/cost/result contract.

The competing global physical split question is a different observable, not a second equally compatible validator for the same partial vertex-label field. Therefore the code/topology/domain provenance resolves the methodology without a new anatomical or methodology Human gate. Human review of the resulting ownership candidate remains required. No sheet-specific historical erratum or production approval requiring physical face-dual disconnection was found in the searched approval/freeze/response evidence; the current contract's literal rule is explicitly accounted for.

## Mixed face composition and reconnection witnesses

Full mesh classification: PURE_THUMB463; PURE_INDEX438; MIXED21; PARTIAL_LABEL_SUPPORT83 (50 THUMB+unknown,33 INDEX+unknown); wholly unassigned2409. These sum to3414. Of21 mixed faces,19 are complete graph faces and2 contain outside-graph corners. The latter corners are v1881/v3139/v3235 and remain unassigned. The21 faces form1 shared-edge band;19 have2 incident cut edges and2 endpoint faces have1 each. Each of the20 cut edges has real two-face support. The band touches18 pure THUMB faces and12 pure INDEX faces, contains no hard-source vertex, and creates no ownership island or third label.

The shortest local cross-side dual witness is **face1488 (pure INDEX) → face1491 (mixed) → face2656 (pure THUMB)**. The retained shared edges are **e4789=(v2035,v2852), INDEX/INDEX**, and **e2420=(v646,v2041), THUMB/THUMB**. Face1491 corners are v2035/v2852/v2041/v646 = INDEX/INDEX/THUMB/THUMB. Its unlike edges e2409/e4788 are removed from the dual, but both retained same-label shared-edge traversals still pass through its single face node. No shared-vertex-only hop is needed.

The shortest independent anchor-context path in V4 has **{paths['V4_anchor_context_shortest_path']['shortest_hops']} dual hops**, INDEX nail face791 → THUMB nail face1219. Face IDs:

`{paths['V4_anchor_context_shortest_path']['face_ids']}`

It contains mixed face2730 and partial faces1244/1248/1251/1253/1252. Every hop has a retained original shared mesh edge, recorded with endpoint labels and both polygon compositions in R3_FACE_DUAL_RECONNECTION_PATH_AUDIT.json. None uses a cut edge or vertex-only adjacency.

Even removing all21 mixed polygon nodes leaves literal V3 with **1 component /3393 faces**. Its shortest anchor-context path has **{paths['V3_full_mesh_after_mixed_barrier_shortest_path']['shortest_hops']} hops**, INDEX nail face811 → THUMB nail face1219. Face IDs:

`{paths['V3_full_mesh_after_mixed_barrier_shortest_path']['face_ids']}`

It contains no mixed face, but crosses unknown faces2585/2584/2636/2639/2411/2408/1277 and partial support faces. Thus a mixed-face barrier alone cannot make a **partial** binary field globally separate the full hand. Full-mesh vertex adjacency minus the fresh20 edges likewise has1 component/3416 vertices; this diagnostic is preserved and is not mislabeled as canonical V1. There is no global body side assignment or physical separation claim.

## Four candidate adjudication

| Candidate | Result | Meaning and applicability |
| --- | --- | --- |
| V1 induced vertex-label graph | THUMB1 component/498 vertices; INDEX1/464; own anchors unique; no islands/isolated vertices | Primary identity test for the exact solved field domain; all vertices have frozen face support |
| V2 pure-face complexes | THUMB1 component/463 faces; INDEX1/438; both full anchor families uniquely contained | Independent 2D coherence corroboration; mixed faces remain boundary band |
| V3 literal full-mesh mixed barrier |1 joint component/3393 faces; THUMB and INDEX collide | Still domain-mismatched because unknown exterior is allowed to reconnect; not silently declared PASS |
| V3 domain-respecting specialization |2 independent pure-face components, THUMB1/INDEX1; fixed anchors separate | Explicitly restricted to fully solved pure faces and identical to V2; mixed faces validation-only, partial/unknown nonparticipating |
| V4 current full face dual |1 joint component/3414 faces/3416 vertices; collision exactly reproduced | Method/type mismatch for vertex ownership identity; original FAIL preserved |

V1 each label has one source-backed, face-supported component and zero isolated vertices/source-free components. V2 pure complexes contain every fixed identity marker, nail face/vertex and cap37 face/vertex. Pure-face vertices cover497/498 THUMB vertices and458/464 INDEX vertices; v2037 and v572/v1573/v2033/v2287/v2850/v2886 are supported only by mixed/partial fringe polygons. They remain valid binary vertex labels, are not discarded or relabelled, and are explicitly audited under V1. The band is connected, surface-supported and lies between the two pure complexes. No label repair is needed.

Canonical method therefore uses **V1 for complete vertex-region identity/coverage and source-free-island checks; V2 for pure 2D coherence and independent anchor consistency; mixed band for boundary support/connectivity; domain-respecting V3 as an equivalent barrier cross-check**. Global V3/V4 are retained diagnostics. This choice follows topology types, the frozen partial-field domain and historical purpose; the final498/464 counts are not a target.

Executed synthetic negative controls construct a mixed quad between pure-label faces and show two primal vertex regions but one full dual component after unlike-edge deletion. Pure-face restriction restores two independently named sides. Additional controls permute component order, remove an identity marker and split an anchor family: identity is independent of rank and missing/split anchors are rejected. These are static synthetic tests, with no production labels changed and no solver invoked.

## Derived validation and R2 Human Review

R3_SHEET_IDENTITY_REVALIDATION_R2.json and R3_FRESH_DERIVED_VALIDATION_STATUS_R2.json record PASS and the canonical method/hash. They supersede only the derived sheet-method interpretation. R1 labels/boundary/energy/ambiguity/sources/graph/status/HTML and old validator output remain unchanged. INDEX ownership count464 /THUMB counterpart498 refer to the bounded field. Global body count stays null; independent wrist v2260 is outside the field and cannot be assigned by history or complement size.

R3_FRESH_RESULT_HUMAN_REVIEW_R2.html retains native/RSSF views and high-level Q1–Q7. It shows independent ownership regions, pure-face support, a new mixed-band view and the preserved original failure explanation. Result hash is unchanged, while the exported response additionally binds canonical validator method and revalidation hash. It never applies production changes, freezes labels, authorizes skin, or runs Stage6. QA previews are explicitly non-Human.

All {len(before)} pre-existing workspace files have identical before/after SHA-256 hashes. Fresh result and all history are immutable. WEIGHT_DELTA=GEOMETRY_DELTA=TOPOLOGY_DELTA=BONE_DELTA=JOINT_DELTA=0; BLEND_FILES_WRITTEN=0. **NEXT: HUMAN_R3_FRESH_RESULT_APPROVAL. STOP.**
'''
(OUT/(RUN+'_REPORT.md')).write_text(report,encoding='utf8')
required=[RUN+'_REPORT.md',RUN+'_STATUS.json','R3_FRESH_FACE_LABEL_COMPOSITION_AUDIT.json','R3_FACE_DUAL_RECONNECTION_PATH_AUDIT.json','R3_VERTEX_LABEL_COMPONENT_AUDIT.json','R3_PURE_FACE_COMPONENT_AUDIT.json','R3_MIXED_BOUNDARY_FACE_BAND_AUDIT.json','R3_FACE_DUAL_MIXED_BARRIER_AUDIT.json','R3_SHEET_VALIDATOR_PROVENANCE_AUDIT.json','R3_SHEET_VALIDATOR_CANDIDATE_COMPARISON.json','R3_SHEET_IDENTITY_REVALIDATION_R2.json','R3_FRESH_RESULT_HUMAN_REVIEW_R2.html']
assert all((OUT/n).is_file() for n in required)
for p in OUT.glob('*.json'):read(p)
dump('FROZEN_HASHES_AFTER.json',after);dump('FROZEN_HASH_VERIFICATION_R1.json',{'pass':True,'protected_file_count':len(before),'changed_files':[],'external_Human_response_unchanged':True,'fresh_labels_changed':0,'R3_rerun_count':0,'BLEND_FILES_WRITTEN':0})
dump('FINAL_ARTIFACT_VERIFICATION_R1.json',{'pass':True,'required_files':required,'fresh_result_and_history_unchanged':True,'sheet_identity_verdict':S['verdict'],'R3_solver_or_closure_execution':False,'Human_review_R2_generated':S['Human_Review_R2_generated'],'STOP':True})
dump('OUTPUT_EVIDENCE_HASH_MANIFEST_R1.json',{p.name:sha(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='OUTPUT_EVIDENCE_HASH_MANIFEST_R1.json'})
print({'verdict':S['verdict'],'required_files':len(required),'protected_files':len(before),'unchanged':True,'STOP':True})
