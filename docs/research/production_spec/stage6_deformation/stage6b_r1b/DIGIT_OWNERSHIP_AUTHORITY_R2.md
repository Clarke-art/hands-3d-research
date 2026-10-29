# DIGIT_OWNERSHIP_AUTHORITY_R2

Round: **STAGE6B_R1B_SEMANTIC_OWNERSHIP_AND_LOCAL_WEIGHT_RECONCILIATION**  
Generated: `2026-09-30T22:49:11.226358+08:00`  
Status: effective for this round; Stage5B R1B remains the CURRENT_FROZEN_PRODUCTION_MASTER.

## 1. Authority

```
DIGIT_OWNERSHIP_AUTHORITY_R2 =
    MESH_TOPOLOGY_AWARE
  + MULTI_SOURCE_GEODESIC_DIGIT_PARTITION
  + APPROVED_ANATOMICAL_CHAIN_CONTEXT
```

`MESH_TOPOLOGY_AWARE` -- the partition is an exact Dijkstra over the REAL mesh edge
graph (edge length metric), never a Euclidean proximity test.

`MULTI_SOURCE_GEODESIC_DIGIT_PARTITION` -- six sources: the approved joint-polyline
distal landmark of each of the five digits plus the approved wrist origin vertex.
Seed vertices: `{"THUMB": 1076, "INDEX": 1228, "MIDDLE": 1737, "RING": 1741, "LITTLE": 225, "wrist": 2255}`.

`APPROVED_ANATOMICAL_CHAIN_CONTEXT` -- the seeds come from the frozen joint frame
chain used by every Stage5B / Stage6A / Stage6B script. The thumb source is the approved
joint-chain tip vertex, which is **outside** the disputed Class-B set, so the partition
cannot be self-fulfilling.

## 2. Forbidden authority (retired)

`NEAREST_CHAIN_EUCLIDEAN_DISTANCE` may no longer be used alone as the digit-ownership
authority for an RSSF or any other near-contact pose. Its failure mode is documented by
Stage6B R1A: the RSSF bind pose brings the thumb sheet and the index sheet to 0.2465 mm,
after which the purely spatial test flips 61 edge labels at random.

## 3. Separation of authorities (binding)

| purpose | authority |
|---|---|
| digit partition / topological ownership | **mesh geodesic (this document)** |
| thumb longitudinal weight coordinate | **APPROVED_JOINT_POLYLINE_ARC_LENGTH** (unchanged) |

`GLOBAL_SURFACE_GEODESIC_FROM_DISTAL_TIP` remains FORBIDDEN as a longitudinal weight
coordinate. The mesh geodesic is used here ONLY for digit partition.

## 4. What this round did NOT do

No retopology, no seam split, no vertex move, no CMC cage change, no joint move, no bone
roll change, no bone-count change, no opposition-vector change, no test-angle shrink.

## 5. Frozen Class-A protection

The six CLASS_A edges keep `ANATOMIC_FIRST_WEB_TRANSITION`, `DO_NOT_CUT`,
`DO_NOT_RECLASSIFY_AS_ERROR`; their topology and anatomical classification are untouched.

## 6. Historic probe

The 61 CLASS_B edges are renamed **HISTORIC_CLASS_B_EDGES** and are kept forever as a
before/after dynamic-stretch probe set, whether or not they are still a semantic boundary.
