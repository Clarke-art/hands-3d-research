# STAGE6A DEFORMATION GATE AMENDMENT R2

Generated: `2026-10-01T08:30:38.314315+08:00`

## 1. Validator defect that triggered this amendment

`STAGE6A R1B` measured but did not gate the two quantities below:

| case | max_edge_ratio | new_severe_self_intersection_pairs | status |
|---|---|---|---|
| `TH_IP_45` | **7.8355** | **78** | PASS |

The hard-blocker set only covered NaN / collapse / degeneration / topology, so a 7.8x edge
stretch and 78 new severe self-intersection pairs passed the gate unnoticed.

## 2. Scale of the gap across all 42 Stage6A R1B cases

- cases with `max_edge_ratio > 5.0`: **7 / 42**
- worst `max_edge_ratio` in the run: **17.6757** (`TH_MCP_45`)
- worst `new_severe_self_intersection_pairs`: **101**

| case | max_edge_ratio | new severe self-intersection |
|---|---|---|
| `TH_MCP_45` | 17.6757 | 101 |
| `TH_MCP_30` | 12.2567 | 77 |
| `IDX_MCP_45` | 8.1591 | 2 |
| `TH_IP_45` | 7.8355 | 78 |
| `TH_MCP_15` | 6.6334 | 57 |
| `IDX_MCP_30` | 5.8588 | 0 |
| `TH_IP_30` | 5.1827 | 68 |
| `IDX_MCP_15` | 3.4583 | 0 |

## 3. Amendments

### 3.1 `SEVERE_EDGE_STRETCH`

For every mesh edge with **BIND length >= 3.0 mm**, if `posed_length / bind_length > 5.0` the edge
is recorded as `SEVERE_EDGE_STRETCH_EDGE`.  Gate:
`SEVERE_EDGE_STRETCH_EDGE_COUNT == 0` over the thumb distal correction domain.  It is always
reported for `TH_IP_45`, `TH_MCP_45`, `CMC_OPP_30`, `CMC_MCP_L3` and `FULL_OPP_L3`.  The edge set
must not be trimmed to pass the gate.

### 3.2 `SEVERE_SELF_INTERSECTION`

Reuse the existing `new_severe_self_intersection_pairs` predicate, restricted to the thumb distal
correction domain.  Gate: `NEW_SEVERE_DISTAL_SELF_INTERSECTION_PAIRS == 0`.

## 4. What stays diagnostic (NOT a blocker)

Global `max_edge_ratio`, global `edges_over_2x` / `edges_over_5x` and global new
self-intersection pairs continue to be **reported** but are not turned into automatic blockers:
physiological surface contact is expected on this asset.  The hard gates focus on same-surface
deformation failure and new severe *local* self-intersection only.

## 5. Per-case recording added

`max_edge_stretch`, `severe_edge_count`, `new_severe_self_intersection_count`,
`affected_semantic_region`.
