# STAGE5B R1C -- LOCAL WEIGHT RECONCILIATION

Status: **CANDIDATE_FOR_HUMAN_REVIEW**  
Generated: `2026-09-30T22:49:20.118608+08:00`  

## 1. Trigger

`STAGE6B_R1B_DIGIT_OWNERSHIP_CORRECTION_AUDIT` reported
`WEIGHT_RECONCILIATION_REQUIRED = 220` on the R2 correction domain, therefore the
round's branch rule §9 authorises a new Stage5B candidate.

## 2. Inputs / outputs

| role | path | sha256 |
|---|---|---|
| input (frozen) | `<HANDS_ROOT>/production_spec/stage5_production_rig/stage5b_r1b/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend` | `cec5804f1319bf2408fded21a3d0cf8c9f01bf778ae0659c18cf17950b117d10` |
| output (candidate) | `<HANDS_ROOT>/production_spec/stage5_production_rig/stage5b_r1c/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1C.blend` | `396e82207d6afba88d634d7c2c796648fba49b9fbc6b15a7c35f989bc868aef7` |

## 3. Authorised region

primary (WEIGHT_RECONCILIATION_REQUIRED) = **220**, 1-ring additions = **62**, 2-ring additions = **29**, final authorised = **311**, actually reweighted = **215**.

FIRST_WEB-protected vertices kept as Dirichlet anchors: **0**.

## 4. Method

The existing Stage5B parametric authority cannot describe an INDEX-owned vertex
(Stage5B never authored index weights: those are automatic proximity bind weights), so the
round uses the fallback explicitly authorised by the round spec §13/§14: a deterministic
**same-digit trusted-neighbour constrained interpolation** with the frozen vertices outside
the authorised region as Dirichlet anchors. No per-vertex free parameter exists.

## 5. Hard gates

- `GEOMETRY_DELTA` = `0.0`
- `RSSF_GEOMETRY_DELTA_MM` = `3.1224e-05`
- `TOPOLOGY_DELTA` = `0`
- `UV_DELTA` = `0`
- `MATERIAL_DELTA` = `0`
- `BONE_DELTA` = `0`
- `OBJECT_ORIGIN_DELTA` = `0`
- `GROUP_SET_UNCHANGED` = `True`
- `UNWEIGHTED_VERTICES` = `0`
- `MAX_INFLUENCES` = `4`
- `MAX_INFLUENCES_LE_4` = `True`
- `NAN_WEIGHTS` = `0`
- `NEGATIVE_WEIGHTS` = `0`
- `NON_NORMALIZED_VERTICES` = `0`

## 6. Drift

- `OUTSIDE_AUTHORISED_WEIGHT_DRIFT` = `0.0`
- `MIDDLE_RING_LITTLE_DRIFT` = `0.0`
- `UNAFFECTED_INDEX_REGION_DRIFT` = `0.0`
- `CMC_CAGE_PROTECTED_DRIFT` = `0.0`

## 7. Freeze rule

Stage5B R1B remains `CURRENT_FROZEN_PRODUCTION_MASTER` until Human Review approves R1C.
