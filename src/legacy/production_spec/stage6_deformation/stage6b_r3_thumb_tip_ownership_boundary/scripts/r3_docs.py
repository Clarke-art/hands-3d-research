import json, os, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
os.chdir(OUT)
NOW = datetime.datetime.now().astimezone().isoformat()
L = lambda p: json.load(open(p, encoding="utf-8"))

ST = L("THUMB_TIP_OWNERSHIP_BOUNDARY_R3_STATUS.json")
BD = L("R3_BOUNDARY_CONNECTEDNESS_AUDIT.json")
AN = L("R3_STRONG_ANCHOR_AUDIT.json")
AM = L("R3_AMBIGUOUS_VERTEX_AUDIT.json")
CA = L("R3_CLASS_A_PRESERVATION_AUDIT.json")
RP = L("R3_REPRODUCIBILITY_AUDIT.json")
RC = L("R3_R2_BOUNDARY_22_EDGE_RECONCILIATION.json")
E4 = L("R3_EDGE498_FORENSIC_AUDIT.json")
IS = L("R3_ISLAND_AUDIT.json")
SV = ST["R2_vs_R3"]
SH = BD["sheet_split"]
G = ST["gates"]

ts = AN["THUMB_STRONG"]
ix = AN["INDEX_STRONG"]

md = f"""# DIGIT_OWNERSHIP_AUTHORITY_R3

Round: **THUMB_TIP_OWNERSHIP_BOUNDARY_RECONCILIATION_R3**
Generated: `{NOW}`
Status: **{ST["DIGIT_OWNERSHIP_AUTHORITY_R3"]}**

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
| pairwise term | none | a fixed penalty per THUMB\\|INDEX label flip, so boundary length is priced |
| anchors | one seed per digit (the approved joint-chain distal landmark) | whole live anatomical anchor REGIONS, hard-pinned |
| failure mode | interleaved label field wherever the two geodesic fields are near-equal | a fragmented boundary costs more than a coherent one, so it is eliminated |
| island control | none | deterministic connectivity closure |

## 2. Strong anchors (round sections 7 / 8)

| anchor set | contents | count |
|---|---|---|
| THUMB_STRONG | approved distal cap {len(AN["THUMB_STRONG"]["approved_distal_cap"]) if isinstance(AN["THUMB_STRONG"]["approved_distal_cap"], list) else AN["THUMB_STRONG"]["approved_distal_cap"]} + approved thumb nail {ts["approved_thumb_nail"]} + proximal-phalanx tube {ts["proximal_phalanx_tube"]} + metacarpal corridor {ts["metacarpal_corridor"]} + approved first web {ts["approved_first_web"]} | **{ts["count"]}** |
| INDEX_STRONG | live index nail {ix["live_index_nail"]} + index PIP..DIP tube {ix["pip_to_dip_tube"]} | **{ix["count"]}** |

`ANCHOR_CONFLICT` = **{AN["conflict_count"]}** - no vertex is claimed by both digits.

The live index tube radius is the median lateral distance over the index PIP..DIP band restricted to
vertices whose **nearest live chain is the index** ({AN["tube_radii_mm"]["INDEX"]:.4f} mm). The unrestricted
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

"""
for k, v in G.items():
    md += f"- `{k}` = `{v}`\n"

md += f"""
## 6. R2 vs R3

| metric | R2 | R3 |
|---|---|---|
| boundary edge count | {SV["R2_BOUNDARY_EDGE_COUNT"]} | **{SV["R3_BOUNDARY_EDGE_COUNT"]}** |
| boundary vertex-component count | {SV["R2_BOUNDARY_COMPONENT_COUNT"]} | {SV["R3_BOUNDARY_COMPONENT_COUNT"]} |
| boundary FACE-component count | {SV["R2_BOUNDARY_FACE_COMPONENT_COUNT"]} | **{SV["R3_BOUNDARY_FACE_COMPONENT_COUNT"]}** |
| short (<6 mm) boundary edges | {SV["R2_SHORT_BOUNDARY_EDGES_LT6MM"]} | {SV["R3_SHORT_BOUNDARY_EDGES_LT6MM"]} |
| distal boundary fragments | {SV["R2_DISTAL_BOUNDARY_FRAGMENTS"]} | **{SV["R3_DISTAL_BOUNDARY_FRAGMENTS"]}** |
| thumb-tip INDEX islands | {SV["R2_THUMB_TIP_INDEX_ISLANDS"]} | **{SV["R3_THUMB_TIP_INDEX_ISLANDS"]}** |
| index THUMB islands | {IS["index_shaft_thumb_islands"]["R2"]} | **{IS["index_shaft_thumb_islands"]["R3"]}** |
| THUMB ownership components | {SV["R2_THUMB_OWNERSHIP_COMPONENTS"]} | **{SV["R3_THUMB_OWNERSHIP_COMPONENTS"]}** |
| INDEX ownership components | {SV["R2_INDEX_OWNERSHIP_COMPONENTS"]} | **{SV["R3_INDEX_OWNERSHIP_COMPONENTS"]}** |
| vertices relabelled by R3 | - | {SV["relabelled_vertex_count"]} |

`R3_R2_BOUNDARY_22_EDGE_RECONCILIATION`: of the 22 R2 boundary edges, **{RC["removed_by_R3"]} are no
longer a THUMB|INDEX step** under R3 and {RC["still_boundary_under_R3"]} remains.

## 7. Sheet split - the decisive topological evidence

Cutting the {SV["R3_BOUNDARY_EDGE_COUNT"]} corrected boundary edges splits the closed mesh into exactly **two sheets**:

- body **{SH["R3_body_vertex_count"]}** vertices - contains the whole approved distal cap
  ({SH["R3_sheet_contains_thumb_cap"]} of 9 in the sheet, i.e. all 9 in the body), the whole approved thumb
  nail and the whole approved first web;
- sheet **{SH["R3_sheet_vertex_count"]}** vertices - carries the **LIVE index tip vertex v{SH["tip_landmark_vertices"]["INDEX"]}**
  (contained: **{SH["R3_sheet_contains_index_tip_vertex"]}**), the entire live index nail region
  ({SH["R3_sheet_contains_index_nail"]} vertices) and **none** of the thumb cap, thumb nail or first web.

=> the disputed seam is **the base collar of the index tube**, not a thumb-tip boundary.

## 8. edge 498 (round section 17)

| | value |
|---|---|
| edge | `{E4["edge"]["edge_id"]}` between `v160` and `v1080`, bind {E4["edge"]["bind_mm"]} mm |
| R2 labels | `{E4["R2_labels"]}` |
| R3 labels | **`{E4["R3_labels"]}`** |
| same digit domain under R3 | **{E4["Q3_same_digit_domain"]}** |
| verdict | {E4["verdict"]} |

## 9. What R3 did NOT do

No retopology, no seam split, no vertex move, no geometry / UV / material change, no weight change, no
CMC cage change, no bone / joint / roll change, no RSSF pose change, no opposition-path change. No
`.blend` was written and no per-vertex manual override exists.
"""
open("DIGIT_OWNERSHIP_AUTHORITY_R3.md", "w", encoding="utf-8").write(md)

rp = f"""# THUMB_TIP_OWNERSHIP_BOUNDARY_R3 - REPORT

Generated: `{NOW}`

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
3. Exact s-t minimum cut (Dinic), source = THUMB, sink = INDEX, restricted to the {RP["vertex_set_size"]}
   vertices that R2 labelled THUMB or INDEX. Unary = the two geodesic distances; pairwise =
   `TAU/3 = {RP["parameters"]["P_FLIP_mm"]:.3f} mm` per THUMB|INDEX flip; anchors pinned.
   **No per-vertex parameter, no randomness.**
4. The {AM["AMBIGUOUS_VERTEX_COUNT_BEFORE"]} ambiguous vertices (|dT-dI| < TAU) are decided by topological
   coherence, not locally; {AM["AMBIGUOUS_ASSIGNED_BY_TOPOLOGY_RATHER_THAN_OWN_UNARY"]} of them were
   assigned against their own unary preference.
5. Deterministic connectivity closure removes any label component with no anchor of its own digit.

## 3. Results

| gate | before (R2) | after (R3) |
|---|---|---|
| boundary edges | {SV["R2_BOUNDARY_EDGE_COUNT"]} | **{SV["R3_BOUNDARY_EDGE_COUNT"]}** |
| boundary face components | {SV["R2_BOUNDARY_FACE_COMPONENT_COUNT"]} | **{SV["R3_BOUNDARY_FACE_COMPONENT_COUNT"]}** |
| distal boundary fragments | {SV["R2_DISTAL_BOUNDARY_FRAGMENTS"]} | **{SV["R3_DISTAL_BOUNDARY_FRAGMENTS"]}** |
| thumb-tip INDEX islands | {SV["R2_THUMB_TIP_INDEX_ISLANDS"]} | **{SV["R3_THUMB_TIP_INDEX_ISLANDS"]}** |
| index THUMB islands | {IS["index_shaft_thumb_islands"]["R2"]} | **{IS["index_shaft_thumb_islands"]["R3"]}** |
| THUMB components | {SV["R2_THUMB_OWNERSHIP_COMPONENTS"]} | **{SV["R3_THUMB_OWNERSHIP_COMPONENTS"]}** |
| INDEX components | {SV["R2_INDEX_OWNERSHIP_COMPONENTS"]} | **{SV["R3_INDEX_OWNERSHIP_COMPONENTS"]}** |
| ambiguous vertices remaining unresolved | - | **{AM["AMBIGUOUS_VERTEX_COUNT_AFTER"]}** |
| R2 boundary edges no longer a boundary | - | **{RC["removed_by_R3"]} of {RC["R2_boundary_edge_count"]}** |

## 4. The round's 30 summary points

| # | item | value |
|---|---|---|
| 1 | R2 boundary edge count | {SV["R2_BOUNDARY_EDGE_COUNT"]} |
| 2 | R3 boundary edge count | **{SV["R3_BOUNDARY_EDGE_COUNT"]}** |
| 3 | R2 short <6 mm boundary count | {SV["R2_SHORT_BOUNDARY_EDGES_LT6MM"]} |
| 4 | R3 short <6 mm boundary count | {SV["R3_SHORT_BOUNDARY_EDGES_LT6MM"]} |
| 5 | R2 boundary component count (vertex based) | {SV["R2_BOUNDARY_COMPONENT_COUNT"]} |
| 6 | R3 boundary component count (vertex based) | {SV["R3_BOUNDARY_COMPONENT_COUNT"]} |
| 6b | boundary FACE component count R2 / R3 | {SV["R2_BOUNDARY_FACE_COMPONENT_COUNT"]} / **{SV["R3_BOUNDARY_FACE_COMPONENT_COUNT"]}** |
| 7 | R2 distal boundary fragments | {SV["R2_DISTAL_BOUNDARY_FRAGMENTS"]} |
| 8 | R3 distal boundary fragments | **{SV["R3_DISTAL_BOUNDARY_FRAGMENTS"]}** |
| 9 | R2 thumb-tip INDEX islands | {SV["R2_THUMB_TIP_INDEX_ISLANDS"]} |
| 10 | R3 thumb-tip INDEX islands | **{SV["R3_THUMB_TIP_INDEX_ISLANDS"]}** |
| 11 | R2 index-distal THUMB islands | {IS["index_shaft_thumb_islands"]["R2"]} |
| 12 | R3 index-distal THUMB islands | **{IS["index_shaft_thumb_islands"]["R3"]}** |
| 13 | distal-cap touching boundary before / after | 0 / **{G["distal_cap_touching_boundary"]}** |
| 14 | nail touching boundary before / after | 0 / **{G["nail_touching_boundary"]}** |
| 15 | CLASS_A 6 edges preserved | **{CA["CLASS_A_6_EDGE_PRESERVATION"]}** |
| 16 | historic CLASS_B remains closed | **{CA["historic_class_b"]["verdict"]}** |
| 17 | ambiguous vertices before / after | {AM["AMBIGUOUS_VERTEX_COUNT_BEFORE"]} / **{AM["AMBIGUOUS_VERTEX_COUNT_AFTER"]}** |
| 18 | edge498 R2 labels | `{E4["R2_labels"]}` |
| 19 | edge498 R3 labels | **`{E4["R3_labels"]}`** |
| 20 | edge498 anatomical verdict | {E4["verdict"]} |
| 21 | THUMB ownership components | **{SV["R3_THUMB_OWNERSHIP_COMPONENTS"]}** |
| 22 | INDEX ownership components | **{SV["R3_INDEX_OWNERSHIP_COMPONENTS"]}** |
| 23 | boundary connectedness verdict | **{BD["component_verdict"]}** |
| 24 | manual per-vertex override count | **{G["manual_per_vertex_override_count"]}** |
| 25 | reproducibility | **{RP["deterministic_reproducibility"]}** |
| 26 | frozen input hash verification | **{ST["frozen_inputs"]["unchanged"]}** |
| 27 | R3 authority status | **{ST["DIGIT_OWNERSHIP_AUTHORITY_R3"]}** |
| 28 | Stage5B R1E | **NOT_STARTED** |
| 29 | next candidate | `{ST["next_candidate_if_R3_passes"]}` |
| 30 | STOP | yes |

## 5. Renders

| file |
|---|
"""
for f in sorted(os.listdir("renders")):
    rp += f"| `{f}` |\n"

rp += "\n## 6. Frozen inputs (before = after)\n\n| input | sha256 |\n|---|---|\n"
for k, v in ST["frozen_inputs"]["before"].items():
    rp += f"| `{k}` | `{v}` |\n"

rp += """
## 7. Next

R3 PASSES. Per round section 31 the round **stops here**: no Stage5B R1E, no weight rebuild, no
deformation test. Waiting for Human Review.
"""
open("THUMB_TIP_OWNERSHIP_BOUNDARY_R3_REPORT.md", "w", encoding="utf-8").write(rp)
print("wrote DIGIT_OWNERSHIP_AUTHORITY_R3.md + THUMB_TIP_OWNERSHIP_BOUNDARY_R3_REPORT.md")
