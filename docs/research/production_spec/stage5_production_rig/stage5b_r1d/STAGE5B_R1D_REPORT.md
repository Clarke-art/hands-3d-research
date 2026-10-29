# STAGE5B R1D -- THUMB DISTAL WEIGHT CONTINUITY RECONCILIATION R2

Generated: `2026-10-01T08:32:29.052366+08:00`

## 1. Verdict

```
LOCAL_WEIGHT_CONTINUITY_RECONCILIATION = FAIL
ROOT_CAUSE                             = LOCAL_SKIN_WEIGHT_FIELD_INSUFFICIENT
ROOT_CAUSE_OPERATIVE                   = OWNERSHIP_LABEL_FIELD_INTERLEAVED_AT_THUMB_TIP
targeted_prequalification              = FAIL_CLOSED
Stage6A R1C (42 cases)                 = NOT_RUN
Stage6B R1D (9 cases)                  = NOT_RUN
```

Rebuilt from the **Stage5B R1B frozen master** (`cec5804f…`), never from R1C.  R1C is retained only
as a failed-candidate comparison reference and was not modified.

## 2. What R1D did achieve

| quantity | R1B frozen master | R1C failed candidate | R1D candidate |
|---|---|---|---|
| global hard 0/1 flip edges | **18** | 24 (narrower definition: 24) | **3** |
| hard flips fixed | - | - | **15 fixed, 0 new** |
| R2 distal hard flip edges | 12 | 24 | **0** |

| `TH_IP_45` distal edges > 5x | 7 | 26 | **0** |
| `TH_MCP_45` distal edges > 5x | 53 | 47 | **0** |
| `CMC_OPP_30` distal edges > 5x | 54 | 48 | **0** |
| `CMC_MCP_L3` distal edges > 5x | 55 | 51 | **0** |
| `FULL_OPP_L3` distal edges > 5x | 55 | 51 | **0** |
| `TH_IP_45` distal new self-intersection pairs | 146 | 66 | **1** |
| `TH_MCP_45` distal new self-intersection pairs | 217 | 80 | **0** |
| `CMC_OPP_30` distal new self-intersection pairs | 208 | 109 | **0** |
| `CMC_MCP_L3` distal new self-intersection pairs | 200 | 124 | **0** |
| `FULL_OPP_L3` distal new self-intersection pairs | 200 | 134 | **0** |

The historic CLASS_B 61-edge tear is **CLOSED in R1D** on all six poses (max stretch 1.000-1.111x,
0 torn edges) - the visible torn flap of R1B is gone.

## 3. Why it still fails closed

Enforcing the corrected ownership at the thumb tip exposes a defect **inside the ownership authority
itself**: the `DIGIT_OWNERSHIP_AUTHORITY_R2` label field **alternates THUMB / INDEX between adjacent
vertices** at the thumb tip.

- R2 corrected THUMB|INDEX boundary edges: **22**, of which **22** are shorter than 6 mm
- worst case: edge 498, `v160` (corrected THUMB) to `v1080` (corrected INDEX), **bind 3.098 mm**
  - R1B: posed 3.1 mm in every pose (both endpoints carried INDEX bind weights)
  - R1C: posed 3.1 mm (the local interpolation left the INDEX weights in place)
  - **R1D: posed 31.3 mm (TH_IP_45) / 56.7 mm (CMC_OPP_30) / 94.2 mm (FULL_OPP_L3)**

R1D gives `v160` `THUMB_IP_R = 1.0` because that is what the corrected ownership demands, while
`v1080` must keep INDEX weights for the same reason.  **No weight field can be simultaneously
ownership-consistent and continuous on a label field that alternates between neighbours.**

This is therefore not a weight-field defect: the weight field in R1D is a continuous function of the
approved live arc length, with no per-vertex parameter.  It is an **ownership-label defect at the
thumb tip** that R2 did not resolve.

## 4. Static gates (all PASS)

- `GEOMETRY_DELTA_M` = `0.0`
- `RSSF_GEOMETRY_DELTA_MM` = `3.1223622e-05`
- `TOPOLOGY_DELTA` = `0`
- `UV_DELTA` = `0`
- `MATERIAL_DELTA` = `0`
- `NAIL_FACE_DELTA` = `0`
- `BONE_DELTA` = `0`
- `OBJECT_ORIGIN_DELTA` = `0`
- `GROUP_SET_UNCHANGED` = `True`
- `UNWEIGHTED_VERTICES` = `0`
- `MAX_INFLUENCES` = `4`
- `MAX_INFLUENCES_LE_4` = `True`
- `NAN_WEIGHTS` = `0`
- `NEGATIVE_WEIGHTS` = `0`
- `NON_NORMALIZED_VERTICES` = `0`

## 5. Protected drift

- `OUTSIDE_AUTHORISED_REGION` = `0.0`
- `MIDDLE_RING_LITTLE` = `0.0`
- `UNAFFECTED_INDEX` = `0.0`
- `CMC_CAGE` = `0.0`
- first web reweighted = 0, THUMB_IP_R carriers in the first web = 0

## 6. Region / method

- primary 266, 1-ring 39, 2-ring 9, expansion rounds 2, final authorised 320, reweighted 283
- longitudinal authority = LIVE Stage5A R2A thumb joint polyline arc length; the stale
  `STAGE4B_R2_JOINT_FRAME.json` was never opened this round
- weight field = centered quintic ramps in `s` (R1B approved configuration) + a deterministic
  boundary relaxation; no per-vertex free parameter
- constrained Laplacian iterations = 0, boundary relaxation rounds = 0

## 7. Freeze / next

No freeze.  Stage5B R1B remains `CURRENT_FROZEN_PRODUCTION_MASTER`.  Per round sections 26 / 40 the
round stops here and waits for Human Review.  The 42-case and 9-case runs were deliberately **not**
executed.

Next candidate (NOT started): **`THUMB_TIP_OWNERSHIP_BOUNDARY_RECONCILIATION_R3`** - clean the R2
label field at the thumb tip into a single THUMB|INDEX topological boundary (the same treatment R1A
applied to the nearest-chain authority), and only then re-run the distal weight reconciliation.
