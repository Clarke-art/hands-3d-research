# DIGIT_OWNERSHIP_AUTHORITY_R3

Round: **THUMB_TIP_OWNERSHIP_BOUNDARY_RECONCILIATION_R3**
Generated: `2026-10-01T16:16:44.929101+08:00`
Status: **QUALIFIED_PENDING_HUMAN_REVIEW**

Supersedes `DIGIT_OWNERSHIP_AUTHORITY_R2` for the THUMB|INDEX partition. The R2 document is
**kept unchanged** as historical authority and was not overwritten.

## 1. Authority

```
DIGIT_OWNERSHIP_AUTHORITY_R3 =
    TOPOLOGY_AWARE_BINARY_SEGMENTATION
  = deterministic exact s-t MINIMUM CUT (Dinic) over the REAL mesh adjacency graph
  + STRONG ANCHORS pinned from LIVE Stage5A R2A anatomy
  + connectivity closure (no label island may survive without its own anchor)
```

### 1.1 Why R2 failed and what R3 changes

| | R2 | R3 |
|---|---|---|
| decision | independent per-vertex argmin over 6 single geodesic seeds | global min-cut over the mesh adjacency graph |
| pairwise term | none | a fixed penalty per THUMB\|INDEX label flip, so boundary length is priced |
| anchors | one seed per digit (the approved joint-chain distal landmark) | whole live anatomical anchor REGIONS, hard-pinned |
| failure mode | interleaved label field wherever the two geodesic fields are near-equal | a fragmented boundary costs more than a coherent one, so it is eliminated |
| island control | none | deterministic connectivity closure |

## 2. Strong anchors (round sections 7 / 8)

| anchor set | contents | count |
|---|---|---|
| THUMB_STRONG | approved distal cap 9 + approved thumb nail 22 + proximal-phalanx tube 212 + metacarpal corridor 8 + approved first web 21 | **241** |
| INDEX_STRONG | live index nail 43 + index PIP..DIP tube 143 | **145** |

`ANCHOR_CONFLICT` = **0** - no vertex is claimed by both digits.

The live index tube radius is the median lateral distance over the index PIP..DIP band restricted to
vertices whose **nearest live chain is the index** (8.0577 mm). The unrestricted
median (28.4551 mm) is unusable here: the RSSF bind pose presses the thumb tip against the index and
inflates it by about 3.5x.

## 3. Separation of authorities (binding, unchanged from R2)

| purpose | authority |
|---|---|
| digit partition / topological ownership | **this document (R3)** |
| thumb longitudinal weight coordinate | **APPROVED_JOINT_POLYLINE_ARC_LENGTH on the LIVE R2A rig** |

`NEAREST_CHAIN_EUCLIDEAN_DISTANCE` and `GEODESIC_NEAREST_SEED_ARGMIN_ALONE` are RETIRED. The stale
`STAGE4B_R2_JOINT_FRAME.json` is not read; all joint coordinates come from the live R2A rig
(`ob.matrix_world @ bone.head_local`).

## 4. No animation input (round section 6)

No stretch, collision or deformation result was used anywhere in the ownership decision. Stage5B R1D
stretch data appears only in the verification sections of the round report.

## 5. Gates

- `TOPOLOGY_DELTA` = `0`
- `GEOMETRY_DELTA` = `0`
- `VERTEX_POSITION_DELTA` = `0`
- `UV_DELTA` = `0`
- `MATERIAL_DELTA` = `0`
- `BONE_DELTA` = `0`
- `WEIGHT_DELTA` = `0`
- `NAIL_FACE_DELTA` = `0`
- `BLEND_FILES_WRITTEN` = `0`
- `historic_CLASS_B_misclassified_edges` = `0`
- `CLASS_A_preserved` = `True`
- `distal_cap_touching_boundary` = `0`
- `nail_touching_boundary` = `0`
- `thumb_tip_index_islands` = `0`
- `index_distal_thumb_islands` = `0`
- `index_shaft_thumb_islands` = `0`
- `distal_boundary_fragments` = `0`
- `distal_thumb_surface_touching_boundary` = `0`
- `DISTAL_BOUNDARY_FRAGMENTS_diagnostic_loose_lateral_band` = `4`
- `index_strong_anchor_touching_boundary` = `0`
- `manual_per_vertex_override_count` = `0`
- `thumb_index_anchor_conflicts` = `0`
- `deterministic_reproducibility` = `True`
- `frozen_inputs_unchanged` = `True`

## 6. R2 vs R3

| metric | R2 | R3 |
|---|---|---|
| boundary edge count | 22 | **16** |
| boundary vertex-component count | 10 | 16 |
| boundary FACE-component count | 1 | **1** |
| short (<6 mm) boundary edges | 22 | 16 |
| distal boundary fragments | 0 | **0** |
| thumb-tip INDEX islands | 0 | **0** |
| index THUMB islands | 0 | **0** |
| THUMB ownership components | 1 | **1** |
| INDEX ownership components | 1 | **1** |
| vertices relabelled by R3 | - | 34 |

`R3_R2_BOUNDARY_22_EDGE_RECONCILIATION`: of the 22 R2 boundary edges, **21 are no
longer a THUMB|INDEX step** under R3 and 1 remains.

## 7. Sheet split - the decisive topological evidence

Cutting the 16 corrected boundary edges splits the closed mesh into exactly **two sheets**:

- body **3199** vertices - contains the whole approved distal cap
  (0 of 9 in the sheet, i.e. all 9 in the body), the whole approved thumb
  nail and the whole approved first web;
- sheet **217** vertices - carries the **LIVE index tip vertex v1228**
  (contained: **True**), the entire live index nail region
  (43 vertices) and **none** of the thumb cap, thumb nail or first web.

=> the disputed seam is **the base collar of the index tube**, not a thumb-tip boundary.

## 8. edge 498 (round section 17)

| | value |
|---|---|
| edge | `498` between `v160` and `v1080`, bind 3.0983 mm |
| R2 labels | `['THUMB', 'INDEX']` |
| R3 labels | **`['INDEX', 'INDEX']`** |
| same digit domain under R3 | **True** |
| verdict | RESOLVED_WITH_ANATOMICAL_AND_TOPOLOGICAL_EVIDENCE: both endpoints belong to the INDEX surface; the disputed seam is the base collar of the index tube, not a thumb-tip boundary |

## 9. What R3 did NOT do

No retopology, no seam split, no vertex move, no geometry / UV / material change, no weight change, no
CMC cage change, no bone / joint / roll change, no RSSF pose change, no opposition-path change. No
`.blend` was written and no per-vertex manual override exists.
