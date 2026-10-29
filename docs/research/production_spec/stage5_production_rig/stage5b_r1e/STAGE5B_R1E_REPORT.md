# STAGE5B R1E -- LOCAL WEIGHT RECONCILIATION FROM R1B

Status: **CANDIDATE_FOR_HUMAN_REVIEW**  
Generated: `2026-10-01T16:53:45.305415+08:00`

Rebuilt from the **Stage5B R1B frozen master**.  R1C / R1D are never used as a source
(`FAILED_CANDIDATE_REFERENCE_ONLY`).

## 1. Inputs

| role | path | sha256 |
|---|---|---|
| input (frozen master) | `<HANDS_ROOT>/production_spec/stage5_production_rig/stage5b_r1b/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend` | `cec5804f1319bf2408fded21a3d0cf8c9f01bf778ae0659c18cf17950b117d10` |
| live production rig | `<HANDS_ROOT>/production_spec/stage5_production_rig/stage5a_r2a/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend` | `c4fafc56c591411bb5ddf07bde44b5fcd6e6a9aa5e0d43b22f9734c0884c2845` |
| ownership authority | `DIGIT_OWNERSHIP_AUTHORITY_R3` | `b289be97b6d860ae` |
| R3 labels | `R3_OWNERSHIP_LABELS.json` | `dc4e262203213813` |
| failed candidate (reference) | `<HANDS_ROOT>/production_spec/stage5_production_rig/stage5b_r1c/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1C.blend` | `396e82207d6afba88d634d7c2c796648fba49b9fbc6b15a7c35f989bc868aef7` |
| failed candidate (reference) | `<HANDS_ROOT>/production_spec/stage5_production_rig/stage5b_r1d/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1D.blend` | `bdf69683f19829c3a86986f8c743e2d7290982e53ae632770e2a7d58e56f20eb` |
| output (candidate) | `<HANDS_ROOT>/production_spec/stage5_production_rig/stage5b_r1e/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1E.blend` | `be1c85cd75338d4ec30ece9be23c93cc1ef0714233dfbaa99c7af4d244fcbbc5` |

`STAGE4B_R2_JOINT_FRAME.json` read: **False** (all joint data comes from the LIVE R2A rig).

## 2. Authority split (round section 6)

`DIGIT_OWNERSHIP_AUTHORITY_R3` defines the **digit family domain** only.  It is *not* a
skin-weight authority: the R3 THUMB|INDEX collar is an interdigit commissure, so its skin
is driven with a graded palm share while the ownership stays R3-exact.

R3 facts used verbatim: boundary edges = 16, edge vertex-components = 16, boundary face-component = 1 (`SINGLE_COHERENT_COLLAR_CUT_SET`), THUMB components = 1, INDEX components = 1, islands = 0, manual overrides = 0.

## 3. Live joint polylines (mm)

- thumb `[0.0, 46.9437, 74.6429, 106.7898]`
- index `[0.0, 31.5077, 51.9246, 67.296]`
- median edge `3.888205` mm

## 4. Authorised region

| criterion | count |
|---|---|
| R3 != R2 label | 34 |
| R3 cross-digit dominant (R1B drives it from the other digit's chain) | 150 |
| incident to an R3 collar boundary edge | 32 |
| incident to a historic CLASS_A/B probe edge | 92 |
| thumb-distal previous failure region | 173 |
| R3 THUMB carrying a foreign group | 173 |
| collar 2-ring (index-root continuity) | 64 |
| **core** | **262** |
| + same-domain 1-ring | 52 |
| + same-domain 2-ring | 27 |
| **authorised (final)** | **341** |
| actually reweighted | 320 |

## 5. Weight field

- continuous function of the LIVE arc length only, centred quintic ramps;
  `W_IP` = 19.4410 mm, `W_BASE` = 11.6646 mm, index `W_MCP/PIP/DIP` = 19.4410 / 19.4410 / 19.4410 mm.
- no one-hot ownership mapping: an R3 THUMB vertex is *not* snapped to the nearest thumb
  bone, it follows the continuous thumb-chain field (and vice versa for INDEX).
- palm valley: pure function of the integer graph distance to the R3 collar, `GFOLD` = 2,
  clamped to 0 on the approved distal cap and on both approved nail sets.

## 6. Hard 0/1 flips

| scope | before (R1B) | after (R1E) |
|---|---|---|
| GLOBAL | **18** | **6** |
| THUMB_DISTAL | 12 | 0 |
| R3_COLLAR | 0 | 0 |
| FIRST_WEB | 3 | 3 |

NEW hard flips = **0** ; correction-domain false hard flips = **0**

## 7. Static gates

- `UNWEIGHTED_VERTICES` = `0`
- `MAX_INFLUENCES` = `4`
- `MAX_INFLUENCES_LE_4` = `True`
- `NAN_WEIGHTS` = `0`
- `NEGATIVE_WEIGHTS` = `0`
- `NON_NORMALIZED_VERTICES` = `0`
- `RSSF_GEOMETRY_DELTA_MM` = `3.1223622e-05`
- `GEOMETRY_DELTA_M` = `0.0`
- `TOPOLOGY_DELTA` = `0`
- `UV_DELTA` = `0`
- `MATERIAL_DELTA` = `0`
- `NAIL_FACE_DELTA` = `0`
- `BONE_DELTA` = `0`
- `JOINT_DELTA` = `0`
- `ROLL_DELTA` = `0`
- `OBJECT_ORIGIN_DELTA` = `0`
- `GROUP_SET_UNCHANGED` = `True`

## 8. Protected drift

- `OUTSIDE_AUTHORISED_REGION` = `0.0`
- `MIDDLE_RING_LITTLE` = `0.0`
- `UNAFFECTED_INDEX` = `0.0`
- `UNAFFECTED_THUMB` = `0.0`
- `FIRST_WEB` = `0.0`
- `NAIL` = `0.0`
- `DISTAL_CAP` = `0.0`
- `CMC_CAGE` = `0.0`
- `verdict` = `PASS`

## 9. R3 collar continuity

- boundary edges = 16, collar vertices = 32
- weight-vector L1 difference across the collar: max `0.0`, median `0.0`
- collar ring palm-driven = **True**
- verdict = **PASS**

## 10. Freeze rule

Stage5B R1B remains `CURRENT_FROZEN_PRODUCTION_MASTER` until Human Review approves R1E.
No freeze was performed.  R1C / R1D are NOT deleted.

## 11. Not authorised this round

Stage6A 42-case regression and Stage6B 9-case retest are **NOT_STARTED**.

## 12. Targeted prequalification (6 poses - NOT the 42-case / 9-case sets)

Verdict: **FAIL_CLOSED**

| pose | R1B severe | R1D severe | **R1E severe** | R1E max | R1E CLASS_B tear | R1E collar severe | R1E distal severe | cap motion mm |
|---|---|---|---|---|---|---|---|---|
| TH_IP_30 | 0 | 2 | **0** | 2.1949x | 0 | 0 | 0 | 16.538 |
| TH_IP_45 | 7 | 17 | **0** | 3.1838x | 0 | 0 | 0 | 24.453 |
| TH_MCP_45 | 53 | 31 | **17** | 6.156x | 6 | 5 | 17 | 45.041 |
| CMC_OPP_30 | 56 | 33 | **32** | 7.3462x | 6 | 12 | 31 | 47.53 |
| CMC_MCP_L3 | 60 | 38 | **39** | 11.0413x | 8 | 16 | 37 | 74.871 |
| FULL_OPP_L3 | 60 | 38 | **41** | 11.0413x | 8 | 16 | 39 | 81.937 |

### Gate checks

- `R3_ownership_used_exactly` = **True**
- `historic_CLASS_B_closed_all_poses` = **False**
- `distal_hard_flip_zero` = **True**
- `false_R3_collar_hard_flip_zero` = **True**
- `new_hard_flip_zero` = **True**
- `TH_IP_45_severe_tear_zero` = **True**
- `TH_IP_45_new_severe_same_surface_SI_zero` = **False**
- `CMC_OPP_30_severe_tear_zero` = **False**
- `CMC_MCP_L3_severe_tear_zero` = **False**
- `FULL_OPP_L3_severe_tear_zero` = **False**
- `FULL_OPP_L3_new_severe_same_surface_SI_zero` = **False**
- `collar_weights_continuous` = **True**
- `first_web_no_regression` = **True**
- `nail_no_regression` = **True**
- `distal_cap_no_regression` = **True**
- `cmc_cage_no_drift` = **True**
- `static_gates_all_pass` = **True**
- `frozen_inputs_unchanged` = **True**

### Same-surface self-intersection (not zero, but a large reduction)

`new_severe_same_surface_self_intersection` counts NEW intersection pairs whose two faces
lie inside the SAME R3 cut component (i.e. the surface folds into itself).  Thumb/INDEX
contact pairs are therefore excluded.

| pose | R1B | R1D | **R1E** |
|---|---|---|---|
| TH_IP_30 | 108 | 24 | **9** |
| TH_IP_45 | 146 | 28 | **31** |
| TH_MCP_45 | 217 | 62 | **29** |
| CMC_OPP_30 | 302 | 208 | **239** |
| CMC_MCP_L3 | 296 | 157 | **194** |
| FULL_OPP_L3 | 284 | 154 | **194** |

### Geometric feasibility bound (why some poses cannot reach the 5x gate)

The approved thumb distal cap and the INDEX side of the R3 collar are joined by a
shortest **bind** path of `13.1646` mm (cap 9 vertices -> 16 INDEX-side collar vertices).
For ANY weight assignment the relative motion across that junction must appear as
edge stretch, therefore

`max_edge_ratio >= (cap_motion + fold_bind) / fold_bind`.

| pose | cap motion (mm) | geometric floor | floor > 5x gate |
|---|---|---|---|
| TH_IP_30 | 16.538 | **2.256x** | no |
| TH_IP_45 | 24.453 | **2.857x** | no |
| TH_MCP_45 | 45.041 | **4.421x** | no |
| CMC_OPP_30 | 47.53 | **4.61x** | no |
| CMC_MCP_L3 | 74.871 | **6.687x** | YES |
| FULL_OPP_L3 | 81.937 | **7.224x** | YES |

A `YES` row means the pose cannot satisfy `SEVERE_EDGE_STRETCH <= 5x` for any weight
field that keeps the approved distal-cap authority and the R3 ownership boundary.
This is a property of the mesh junction, not of the solver.


Hard-gate definition: `SEVERE_EDGE_STRETCH` = bind edge >= 3 mm AND posed/bind > 5x
(Stage6A Gate Amendment R2).  `historic_CLASS_B` = the frozen 61-edge probe set, still
measured in every pose (round section 19).
