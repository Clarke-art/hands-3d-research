# STAGE6B R1C -- THUMB / INDEX / PALM PENETRATION VISUAL ADJUDICATION

Round kind: **HUMAN_REVIEW_EVIDENCE_ONLY**.  Generated `2026-09-30T23:29:50.018486+08:00`.

No model change of any kind.  Nothing was written to any `.blend`; no weight, ownership,
geometry, topology, CMC cage, bone, joint, opposition vector, test angle or pose path was
touched; no collision correction, no Stage6C, no freeze.  Only read / reproduce / render / measure.

## 1. Frozen inputs (verified unchanged)

| input | sha256 |
|---|---|
| `stage5b_r1b_frozen_master` | `cec5804f1319bf2408fded21a3d0cf8c9f01bf778ae0659c18cf17950b117d10` |
| `stage5b_r1c_candidate` | `396e82207d6afba88d634d7c2c796648fba49b9fbc6b15a7c35f989bc868aef7` |
| `stage6a_r1b_harness` | `4e669ba720993beb579eef27039c221063d46f9a2ebe31f30d97888282c8c316` |
| `stage6b_r1b_harness` | `295a73944dad1d345e370dd2b12393d4edebcd42a86582e6f307c21a2aaaa612` |
| `stage6b_r1_harness` | `4b6200899fe4d2f5a67e3254aec2a5cb17b734b14acefe381a2ac9c1241f549d` |

`stage5b_r1b_frozen_master` still equals the recorded CURRENT_FROZEN_PRODUCTION_MASTER: **True**  
`stage5b_r1c_candidate` still equals the recorded candidate: **True**

## 2. THE HEADLINE RESULT -- the published 2.60-4.69 mm proxy is not a thumb-index number

The three frozen poses were reproduced verbatim (`re_solved_pose = False`) and every new
intersecting face pair was decomposed by **DIGIT_OWNERSHIP_AUTHORITY_R2** (corrected ownership):

| pose | published overall max proxy | which pair it belongs to | THUMB\_INDEX max proxy | THUMB\_PALM max proxy |
|---|---|---|---|---|
| CMC_OPP_30 | **3.4173 mm** | `INTRA_THUMB` | **0.4248 mm** | 2.3614 mm |
| CMC_MCP_L3 | **4.3112 mm** | `THUMB_OTHER_DIGIT` | **1.1306 mm** | 2.6378 mm |
| FULL_OPP_L3 | **4.6857 mm** | `THUMB_OTHER_DIGIT` | **0.6513 mm** | 2.5824 mm |

In all three poses the adjudicated subject -- **thumb/index** -- is the *smallest* class present
(6-8 real crossing pairs, 0.42-1.13 mm proxy).  The large values belong to **thumb/palm**, 
**thumb/other-digit** and **intra-thumb**.

## 3. WHY the numbers are large -- the decisive evidence

It is **not** physiological surface contact, and it is **not** an over-optimistic posture.
The three poses deform the thumb's own distal surface into a **torn flap**:

| metric | Stage6B R1 (frozen R1B master) | Stage6B R1B (R1C candidate) |
|---|---|---|
| hard 0/1 weight-flip edges in the input master | **2** | **24** |
| CMC_OPP_30: edges >2x / >5x | 148 / 112 | 146 / 102 |
| CMC_MCP_L3: edges >2x / >5x | 150 / 120 | 152 / 116 |
| FULL_OPP_L3: edges >2x / >5x | 150 / 120 | 152 / 116 |
| worst stretch ratio (all poses) | 19.30x | 24.37x |
| faces over 5x, by corrected ownership | {"THUMB": 68, "wrist": 1} | {"THUMB": 59, "wrist": 3} |

**Root cause, measured directly on the input master** (bind state, Blender's own vertex groups):
adjacent vertices on the **thumb's own distal surface** carry
`THUMB_IP_R = 1.0` next to `WRIST_R = 1.0` (and one `INDEX_MCP_R` case).  The flip vertices are
**14.5-24.3 mm from the thumb distal-cap centroid** and are `22 / 22` inside the R2 correction
domain, i.e. they are thumb vertices with wrist/index weights.  Under opposition one side
travels ~70-95 mm and the other stays put, so the surface tears open (bind 3-4 mm edges become
40-95 mm) and the resulting flap sweeps back through the palm and the neighbouring digits.

This is therefore **NOT** `THUMB_INDEX_DEEP_PENETRATION` caused by contact or by the pose path.
It is a **local blend-weight continuity failure on the thumb distal surface**.

## 4. Per-pose adjudication of the actual thumb/index pair

Single unified rule (`classification_rule` in the JSON): the depth is a footprint-constrained
poke depth, normalised by the **bind** mean edge of the SAME triangle pair, so the verdict does
not depend on facet size.

| pose | focus pair | faces | real tri/tri crossing | segment | poke | bind local edge | poke/edge | classification |
|---|---|---|---|---|---|---|---|---|
| CMC_OPP_30 | `THUMB_INDEX` | 375 / 431 | True | 1.3644 mm | 2.2109 mm | 3.9344 mm | **0.5619** | **CASE_B_SURFACE_CONTACT_OR_NEAR_CONTACT** |
| CMC_MCP_L3 | `THUMB_INDEX` | 375 / 439 | True | 0.7107 mm | 0.6205 mm | 3.9286 mm | **0.1580** | **CASE_B_SURFACE_CONTACT_OR_NEAR_CONTACT** |
| FULL_OPP_L3 | `THUMB_INDEX` | 419 / 420 | True | 1.7184 mm | 2.1389 mm | 4.4462 mm | **0.4811** | **CASE_B_SURFACE_CONTACT_OR_NEAR_CONTACT** |

Every class present in each pose:

| pose | class | pairs | real | affected faces | max proxy | max poke | max segment | class at max |
|---|---|---|---|---|---|---|---|---|
| CMC_OPP_30 | INTRA_THUMB | 130 | 116 | 109 | 3.4173 mm | 20.9806 mm | 3.7459 mm | - |
| CMC_OPP_30 | OTHER | 2 | 2 | 3 | 0.1760 mm | 0.4065 mm | 1.0193 mm | - |
| CMC_OPP_30 | THUMB_INDEX | 6 | 6 | 7 | 0.4248 mm | 2.9076 mm | 1.7994 mm | - |
| CMC_OPP_30 | THUMB_OTHER_DIGIT | 120 | 117 | 90 | 2.2373 mm | 29.7406 mm | 4.2853 mm | - |
| CMC_OPP_30 | THUMB_PALM | 92 | 89 | 74 | 2.3614 mm | 3.8366 mm | 3.6130 mm | - |
| CMC_MCP_L3 | INTRA_THUMB | 140 | 134 | 108 | 2.4386 mm | 4.6314 mm | 10.2751 mm | - |
| CMC_MCP_L3 | OTHER | 4 | 4 | 5 | 1.0201 mm | 0.5302 mm | 2.6452 mm | - |
| CMC_MCP_L3 | THUMB_INDEX | 8 | 8 | 9 | 1.1306 mm | 2.2864 mm | 2.3825 mm | - |
| CMC_MCP_L3 | THUMB_OTHER_DIGIT | 34 | 32 | 29 | 4.3112 mm | 2.3848 mm | 3.7251 mm | - |
| CMC_MCP_L3 | THUMB_PALM | 72 | 62 | 62 | 2.6378 mm | 5.4931 mm | 4.0121 mm | - |
| FULL_OPP_L3 | INTRA_THUMB | 151 | 140 | 112 | 3.2488 mm | 6.9177 mm | 11.4679 mm | - |
| FULL_OPP_L3 | OTHER | 4 | 4 | 5 | 1.0202 mm | 0.5310 mm | 2.6468 mm | - |
| FULL_OPP_L3 | THUMB_INDEX | 7 | 7 | 8 | 0.6513 mm | 2.6827 mm | 1.9610 mm | - |
| FULL_OPP_L3 | THUMB_OTHER_DIGIT | 25 | 23 | 22 | 4.6857 mm | 2.5614 mm | 3.7518 mm | - |
| FULL_OPP_L3 | THUMB_PALM | 75 | 68 | 67 | 2.5824 mm | 5.6563 mm | 4.0897 mm | - |

## 5. Actual geometric intersection census

| pose | new intersecting pairs | with a real tri/tri crossing | affected faces | components | largest | total crossing length | mean crossing length |
|---|---|---|---|---|---|---|---|
| CMC_OPP_30 | 350 | **330** | 230 | 4 | 184 | 411.76 mm | 1.2478 mm |
| CMC_MCP_L3 | 258 | **240** | 186 | 6 | 98 | 304.97 mm | 1.2707 mm |
| FULL_OPP_L3 | 262 | **242** | 185 | 7 | 137 | 320.61 mm | 1.3248 mm |

Morphology: a broad but shallow interdigitation band -- **hundreds** of crossing pairs whose
mean crossing length is only ~1.2-1.3 mm -- plus the torn flap.  There is no isolated deep
spear-through of one finger through another.

## 6. Answer to the twelve questions of the round

- **1. CMC_OPP_30 max proxy depth** -- **3.4173 mm**, and it belongs to `INTRA_THUMB`, not to thumb/index
- **2. CMC_OPP_30 actual classification** -- thumb/index focus = **CASE_B_SURFACE_CONTACT_OR_NEAR_CONTACT**; overall max pair = **CASE_B_SURFACE_CONTACT_OR_NEAR_CONTACT**
- **3. CMC_MCP_L3 max proxy depth** -- **4.3112 mm** (`THUMB_OTHER_DIGIT`)
- **4. CMC_MCP_L3 actual classification** -- thumb/index focus = **CASE_B_SURFACE_CONTACT_OR_NEAR_CONTACT**; overall = **CASE_B_SURFACE_CONTACT_OR_NEAR_CONTACT**
- **5. FULL_OPP_L3 max proxy depth** -- **4.6857 mm** (`THUMB_OTHER_DIGIT`)
- **6. FULL_OPP_L3 actual classification** -- thumb/index focus = **CASE_B_SURFACE_CONTACT_OR_NEAR_CONTACT**; overall = **CASE_B_SURFACE_CONTACT_OR_NEAR_CONTACT**
- **7. actual intersecting face count** -- CMC_OPP_30 230, CMC_MCP_L3 186, FULL_OPP_L3 185 (330/240/242 real crossing pairs)
- **8. connected intersection components** -- CMC_OPP_30 4, CMC_MCP_L3 6, FULL_OPP_L3 7
- **9. visible gross interpenetration** -- **YES for the poses as a whole** -- the torn thumb flap crosses back through the palm and the middle finger (see the strain map and the solid renders). NO for the thumb/index pair itself, which is a shallow grazing contact.
- **10. teaching acceptability** -- **NOT acceptable as-is** -- the torn flap is grossly visible. The thumb/index contact alone would be acceptable.
- **11. recommendation** -- **STAGE6C_REQUIRED** (see section 7; note the root cause is a weight continuity failure, not the pose path)
- **12. renders** -- `production_spec/stage6_deformation/stage6b_r1c/renders/` -- 21 files, 6 evidence types per pose (A solid, B close-up, C face highlight, D alpha overlay, E real cross-section, F depth vector) + a per-pose edge-strain map

## 7. Status

```
THUMB_INDEX_DEEP_PENETRATION (the pair itself) = CANDIDATE_ACCEPTED_DOCUMENTED_CONTACT_RESIDUAL
THUMB_DISTAL_WEIGHT_CONTINUITY_DEFECT        = CONFIRMED_VISUAL_BLOCKER
STAGE6B_R1C                                  = READY_FOR_HUMAN_REVIEW
STAGE5B_R1C                                  = CANDIDATE_FOR_HUMAN_REVIEW
DEFORMATION_FINAL                            = PENDING_HUMAN_REVIEW
```

Hypothesis opened for Human Review (NOT started, nothing executed):

* the round's own branch rule names `STAGE6C_POSE_PATH_AND_CONTACT_CONSTRAINT_DIAGNOSIS` as the
  next candidate when a pose shows visible interpenetration, **but the evidence of this round
  says the pose path is not the cause**.  Re-tuning the CMC quaternion or the MCP/IP progression
  would not remove a 0/1 weight discontinuity;
* the previous round's own section 37 classification applies instead:
  `LOCAL_WEIGHT_CONTINUITY_INSUFFICIENT`, i.e. the Stage5B R1C local weight reconciliation did
  not achieve same-digit deformation continuity on the thumb distal surface, and in fact raised
  the mesh-wide hard 0/1 weight-flip edge count from **2 to 24**.
* a further fact worth recording: **Stage6A R1B measured but did not gate** the same signal --
  its `TH_IP_45` case records `max_edge_ratio = 7.835` and
  `new_severe_self_intersection_pairs = 78`, yet the case counts as PASS because the hard-blocker
  set only covers NaN / collapse / degeneration / topology.  The Stage6A gate set should be
  amended in a later round to include a maximum-stretch and self-intersection gate.

No freeze has been performed.  Stage5B R1B remains the CURRENT_FROZEN_PRODUCTION_MASTER.
