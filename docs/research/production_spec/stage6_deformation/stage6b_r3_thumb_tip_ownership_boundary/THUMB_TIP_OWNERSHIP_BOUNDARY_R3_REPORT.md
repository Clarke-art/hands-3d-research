# THUMB_TIP_OWNERSHIP_BOUNDARY_R3 - REPORT

Generated: `2026-10-01T16:16:44.929101+08:00`

Round kind: **OWNERSHIP_AUTHORITY_ONLY** - read / analyse / classify / write authority / render evidence.

## 1. Verdict

```
THUMB_TIP_OWNERSHIP_BOUNDARY_R3 = READY_FOR_HUMAN_REVIEW
DIGIT_OWNERSHIP_AUTHORITY_R3    = QUALIFIED_PENDING_HUMAN_REVIEW
Stage5B R1E = NOT_STARTED
Stage6A     = NOT_STARTED
Stage6B     = NOT_STARTED
DEFORMATION_FINAL = PENDING
```

## 2. Method

1. STRONG anchors are pinned from LIVE R2A anatomy only.
2. Two geodesic fields over the real mesh edge graph: distance to THUMB_STRONG and to INDEX_STRONG.
3. Exact s-t minimum cut (Dinic), source = THUMB, sink = INDEX, restricted to the 1008
   vertices that R2 labelled THUMB or INDEX. Unary = the two geodesic distances; pairwise =
   `TAU/3 = 1.296 mm` per THUMB|INDEX flip; anchors pinned.
   **No per-vertex parameter, no randomness.**
4. The 16 ambiguous vertices (|dT-dI| < TAU) are decided by topological
   coherence, not locally; 6 of them were
   assigned against their own unary preference.
5. Deterministic connectivity closure removes any label component with no anchor of its own digit.

## 3. Results

| gate | before (R2) | after (R3) |
|---|---|---|
| boundary edges | 22 | **16** |
| boundary face components | 1 | **1** |
| distal boundary fragments | 0 | **0** |
| thumb-tip INDEX islands | 0 | **0** |
| index THUMB islands | 0 | **0** |
| THUMB components | 1 | **1** |
| INDEX components | 1 | **1** |
| ambiguous vertices remaining unresolved | - | **0** |
| R2 boundary edges no longer a boundary | - | **21 of 22** |

## 4. The round's 30 summary points

| # | item | value |
|---|---|---|
| 1 | R2 boundary edge count | 22 |
| 2 | R3 boundary edge count | **16** |
| 3 | R2 short <6 mm boundary count | 22 |
| 4 | R3 short <6 mm boundary count | 16 |
| 5 | R2 boundary component count (vertex based) | 10 |
| 6 | R3 boundary component count (vertex based) | 16 |
| 6b | boundary FACE component count R2 / R3 | 1 / **1** |
| 7 | R2 distal boundary fragments | 0 |
| 8 | R3 distal boundary fragments | **0** |
| 9 | R2 thumb-tip INDEX islands | 0 |
| 10 | R3 thumb-tip INDEX islands | **0** |
| 11 | R2 index-distal THUMB islands | 0 |
| 12 | R3 index-distal THUMB islands | **0** |
| 13 | distal-cap touching boundary before / after | 0 / **0** |
| 14 | nail touching boundary before / after | 0 / **0** |
| 15 | CLASS_A 6 edges preserved | **PASS** |
| 16 | historic CLASS_B remains closed | **PASS** |
| 17 | ambiguous vertices before / after | 16 / **0** |
| 18 | edge498 R2 labels | `['THUMB', 'INDEX']` |
| 19 | edge498 R3 labels | **`['INDEX', 'INDEX']`** |
| 20 | edge498 anatomical verdict | RESOLVED_WITH_ANATOMICAL_AND_TOPOLOGICAL_EVIDENCE: both endpoints belong to the INDEX surface; the disputed seam is the base collar of the index tube, not a thumb-tip boundary |
| 21 | THUMB ownership components | **1** |
| 22 | INDEX ownership components | **1** |
| 23 | boundary connectedness verdict | **SINGLE_COHERENT_SEAM (boundary faces form one connected strip)** |
| 24 | manual per-vertex override count | **0** |
| 25 | reproducibility | **True** |
| 26 | frozen input hash verification | **True** |
| 27 | R3 authority status | **QUALIFIED_PENDING_HUMAN_REVIEW** |
| 28 | Stage5B R1E | **NOT_STARTED** |
| 29 | next candidate | `STAGE5B_R1E_LOCAL_WEIGHT_RECONCILIATION_FROM_R1B (NOT_STARTED)` |
| 30 | STOP | yes |

## 5. Renders

| file |
|---|
| `DIGIT_OWNERSHIP_R2_VS_R3_DORSAL.png` |
| `DIGIT_OWNERSHIP_R2_VS_R3_FIRST_WEB_CLOSEUP.png` |
| `DIGIT_OWNERSHIP_R2_VS_R3_PALMAR.png` |
| `DIGIT_OWNERSHIP_R2_VS_R3_RADIAL.png` |
| `DIGIT_OWNERSHIP_R2_VS_R3_THUMB_TIP_CLOSEUP.png` |
| `R3_EDGE498_NEIGHBORHOOD.png` |
| `R3_INDEX_STRONG_ANCHOR_MAP.png` |
| `R3_THUMB_INDEX_BOUNDARY_CONNECTED_COMPONENTS.png` |
| `R3_THUMB_INDEX_BOUNDARY_TOPOLOGY_MAP.png` |
| `R3_THUMB_STRONG_ANCHOR_MAP.png` |

## 6. Frozen inputs (before = after)

| input | sha256 |
|---|---|
| `stage5a_r2a_rig` | `c4fafc56c591411bb5ddf07bde44b5fcd6e6a9aa5e0d43b22f9734c0884c2845` |
| `stage5b_r1b_frozen_master` | `cec5804f1319bf2408fded21a3d0cf8c9f01bf778ae0659c18cf17950b117d10` |
| `stage5b_r1c_failed_candidate` | `396e82207d6afba88d634d7c2c796648fba49b9fbc6b15a7c35f989bc868aef7` |
| `stage5b_r1d_candidate` | `bdf69683f19829c3a86986f8c743e2d7290982e53ae632770e2a7d58e56f20eb` |
| `stage6a_r1b_harness` | `4e669ba720993beb579eef27039c221063d46f9a2ebe31f30d97888282c8c316` |
| `stage6b_r1b_harness` | `295a73944dad1d345e370dd2b12393d4edebcd42a86582e6f307c21a2aaaa612` |
| `stage6b_r1_harness` | `4b6200899fe4d2f5a67e3254aec2a5cb17b734b14acefe381a2ac9c1241f549d` |
| `digit_ownership_authority_r2_md` | `4ee2995e29537c0e42c4ba90bf5a61e630dbd108f10141fa3c75f984ad4a89fd` |
| `stage6b_r1c_status` | `d350bbb8a1f0197938f8a433c28969e9e39f32617be5ee46eba18a3bc0ea9ab1` |
| `stage6b_r1c_deformation_continuity` | `179401eb0071c9638b74670d1884d70933eb0239fcf18c4144f50f56d21adf28` |
| `stage5b_r1d_status` | `4d7542c4cb2ae9926847d49b056b4d33e58800f7eb3a5d650acba537780b6fa6` |
| `stage5b_r1d_prequalification` | `844f56cbdd45276a1af50a2f0ade2feccfc4720b546b1c76b5ef15dbe2cb2be8` |
| `stage5b_r1d_r2_boundary` | `42be4a8d8381ef482bee70f26545fa7eb4428b1912f1ef9c0ea23cfa2440fe26` |
| `stage6b_r1a_class_a` | `8ab48a9c3ced0461ef2041d302cb8711dbd6c96fd67fbbc2d476798f7b2774a6` |
| `stage6b_r1a_class_b` | `2f3f42c873a5b7713a88e43e2c6ff2a431138c6f02553f07e557bf99bcea5904` |
| `thumb_distal_cap_audit` | `c9f7ccf089a309f7331f3efbca4010cc9fbdfe592df23b0a110c908fb1ee0f45` |

## 7. Next

R3 PASSES. Per round section 31 the round **stops here**: no Stage5B R1E, no weight rebuild, no
deformation test. Waiting for Human Review.
