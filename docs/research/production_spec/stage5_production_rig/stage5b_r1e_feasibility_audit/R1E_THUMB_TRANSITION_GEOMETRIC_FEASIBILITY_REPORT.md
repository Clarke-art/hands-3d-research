# R1E THUMB TRANSITION — GEOMETRIC FEASIBILITY AUDIT

**Round:** `R1E_THUMB_TRANSITION_GEOMETRIC_FEASIBILITY_AUDIT`
**Kind:** READ-ONLY · FORENSIC · MATHEMATICAL · TOPOLOGICAL AUDIT
**Generated:** `2026-10-01`
**`BLEND_FILES_WRITTEN` = 0** — no weight, geometry, topology, UV, material, nail face, bone, joint, roll, CMC cage, RSSF, opposition vector or pose magnitude was changed anywhere.

> Stage5B R1E stays **`CANDIDATE_FOR_HUMAN_REVIEW` / `FAIL_CLOSED_PENDING_FEASIBILITY_DIAGNOSIS`**.
> This round does not re-judge PASS/FAIL, does not create R1F, and does not modify anything.

---

## 1. What was audited and why

The previous round closed with two claims that were explicitly listed as **not yet proven**:

* **Suspicion A** — `max_edge_ratio >= (cap_motion + fold_bind) / fold_bind`, giving “≥ 6.687× / ≥ 7.224×”.
* **Suspicion B** — `SEVERE_EDGE_STRETCH_collar = 5 / 12 / 16 / 16` was reported without checking whether those
  edges are the *exact* 16 R3 boundary edges.

Both are resolved below. **Suspicion A is rejected. Suspicion B is confirmed as a classification artefact.**

---

## 2. Frozen inputs (before == after)

31 files hashed before and after the audit; **zero differences**.

| role | path | sha256 |
|---|---|---|
| live production rig | `stage5a_r2a/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend` | `c4fafc56c591411bb5ddf07bde44b5fcd6e6a9aa5e0d43b22f9734c0884c2845` |
| frozen production master | `stage5b_r1b/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend` | `cec5804f1319bf2408fded21a3d0cf8c9f01bf778ae0659c18cf17950b117d10` |
| **R1E candidate (untouched)** | `stage5b_r1e/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1E.blend` | `be1c85cd75338d4ec30ece9be23c93cc1ef0714233dfbaa99c7af4d244fcbbc5` |
| ownership authority | `DIGIT_OWNERSHIP_AUTHORITY_R3.json` | `b289be97b6d860ae…` |
| R3 labels | `R3_OWNERSHIP_LABELS.json` | `dc4e262203213813…` |
| Stage6A R1B / Stage6B R1B / Stage6B R1 harnesses | — | `4e669ba7…` / `295a7394…` / `4b620089…` |

`stage4c_r2/STAGE4B_R2_JOINT_FRAME.json` **read = False**; all joint data comes from the LIVE R2A rig.
Poses reused byte-for-byte: `FLEXION_SIGN = −1`, 30°/45° Stage6A axes, and the Stage6B
`cmc_quaternion_local` + `mcp_deg` + `ip_deg` progression. **Nothing was re-scaled.**

---

## 3. Collar classification (five mutually exclusive levels)

```
C0 = 32 collar vertices = endpoints of the 16 exact R3 boundary edges
C1 = neighbours(C0) \ C0          (32 vertices)
C2 = neighbours(C1) \ (C0 ∪ C1)   (32 vertices)

LEVEL_0_EXACT_R3_BOUNDARY_EDGE   edge id ∈ R3 boundary_edges_R3                16
LEVEL_1_COLLAR_VERTEX_INCIDENT   not L0, ≥1 endpoint ∈ C0                      64
LEVEL_2_COLLAR_ONE_RING          not L0/L1, ≥1 endpoint ∈ C1                   64
LEVEL_3_COLLAR_TWO_RING          not L0/L1/L2, ≥1 endpoint ∈ C2                64
LEVEL_4_PLUS_TRANSITION          everything else                             6620
```

---

## 4. Finding A — the exact 16 R3 collar edges do **not stretch at all**

All 16 exact boundary edges were measured in all six frozen poses (96 measurements).

* both endpoints carry **`WRIST_R = 1.0` on all 32 collar vertices** (verified in a clean session);
* `WRIST_R` is at bind in every one of the six poses, so both endpoints share the **identical rigid transform**;
* **max stretch ratio over the 96 measurements = 1.000000**, max |ratio − 1| = `5.0e-06` (float round-off).

**Verdict: `NO_STRETCH_ON_EXACT_R3_BOUNDARY_EDGES`.**
`R1E_EXACT_R3_COLLAR_DYNAMIC_AUDIT.json`, `renders/R1E_EXACT_COLLAR_EDGE_STRETCH_6POSE.png`.

---

## 5. Finding B — the old “collar severe” counts are a classification artefact

The old metric was *“SEVERE_EDGE_STRETCH with at least one endpoint in the 32 collar vertices”*, i.e.
`LEVEL_0 ∪ LEVEL_1` pooled into one word.

| pose | old “collar severe” | LEVEL_0 (exact 16) | LEVEL_1 | LEVEL_2 | LEVEL_3 | LEVEL_4+ |
|---|---|---|---|---|---|---|
| TH_MCP_45 | 5 | **0** | 5 | 0 | 0 | 0 |
| CMC_OPP_30 | 12 | **0** | 12 | 0 | 0 | 0 |
| CMC_MCP_L3 | 16 | **0** | 16 | 0 | 0 | 0 |
| FULL_OPP_L3 | 16 | **0** | 16 | 0 | 0 | 0 |

**Answer to section 7: ZERO of the old collar severe edges are exact LEVEL_0 R3 boundary edges.**
All of them are `LEVEL_1_COLLAR_VERTEX_INCIDENT` — the first ring of the R1E palm-valley ramp.
`R1E_OLD_COLLAR_SEVERE_RECLASSIFICATION.json`.

---

## 6. Finding C — the shortest cap → INDEX-collar path, fully expanded

* **source (approved distal cap):** `v2192`
* **target (INDEX side of the exact R3 collar):** `v704`
* **vertex sequence:** `2192 → 703 → 2169 → 704`
* **edge-id sequence:** `2722, 2676, 2677`
* **bind edge lengths (mm):** `4.5406, 4.3875, 4.2366` → **total `13.1646 mm`**, 3 edges
* **R3 ownership sequence:** `THUMB → THUMB → THUMB → INDEX`
* **semantic route:** `DISTAL_CAP → THUMB_DISTAL → THUMB_DISTAL → INDEX_ROOT`
* **graph distance to the collar:** `2, 1, 0, 0` · **to the distal cap:** `0, 1, 2, 3`
* route touches the distal cap, the thumb distal band and the exact collar; it passes through
  **no** thumb-MCP transition, **no** CMC transition, **no** first web, **no** palm.

`R1E_CAP_TO_COLLAR_SHORTEST_PATH_AUDIT.json`, `renders/R1E_CAP_TO_COLLAR_SHORTEST_PATH_BIND.png`.

---

## 7. Finding D — the 13.1646 mm path is not a single-pair artefact, but it *is* the minimum

All **144** cap × INDEX-collar endpoint pairs were measured on the bind mesh:

| statistic | value (mm) |
|---|---|
| min | **13.1646** |
| p05 | 17.7277 |
| median | 32.8862 |
| p95 | 44.7447 |
| max | 48.4583 |
| mean | 32.1421 |

The ten shortest **distinct** pairs are expanded in full (`…PATH_ENSEMBLE_AUDIT.json`):

| cap | collar | distance (mm) | edges | route |
|---|---|---|---|---|
| 2192 | 704 | 13.1646 | 3 | DISTAL_CAP→THUMB_DISTAL→THUMB_DISTAL→INDEX_ROOT |
| 2569 | 2176 | 13.7260 | 3 | DISTAL_CAP→THUMB_DISTAL→THUMB_DISTAL→INDEX_ROOT |
| 2189 | 693 | 14.0878 | 3 | DISTAL_CAP→THUMB_DISTAL→THUMB_DISTAL→INDEX_ROOT |
| 2192 | 2170 | 16.9097 | 4 | …→THUMB_DISTAL→INDEX_ROOT |
| 2192 | 2176 | 17.1149 | 4 | …→THUMB_DISTAL→INDEX_ROOT |
| 2569 | 693 | 17.5619 | 4 | …→INDEX_ROOT |
| 2569 | 704 | 17.6762 | 4 | …→INDEX_ROOT |
| 158 | 704 | 17.7277 | 4 | …→INDEX_ROOT |
| 2189 | 2156 | 17.8716 | 4 | …→INDEX_ROOT |
| 2189 | 2176 | 17.9237 | 4 | …→INDEX_ROOT |

Three short **distinct** 3-edge bottlenecks exist (all DISTAL_CAP → THUMB_DISTAL → INDEX_ROOT).
Beyond those, distances rise to ≈ 17–48 mm, i.e. **most of the 144 pairs are three to four times longer
than the minimum**. The 13.1646 mm junction is real but **local**: it is a property of three cap vertices
(`2192, 2569, 2189`) only.

---

## 8. Finding E — the strict geometric bound; the old claim is **INVALID**

### Correct derivation (now the only permitted one)

For a fixed mesh path `P = e₁…eₙ` with bind lengths `bᵢ` and posed lengths `pᵢ`:

```
Σ pᵢ  ≥  ‖B_pose − A_pose‖ = d_t
⇒  max_i (pᵢ / bᵢ)  ≥  d_t / Σ bᵢ  =  STRICT_LOWER_BOUND
```

The old expression `(|u_A| + Σbᵢ) / Σbᵢ` silently assumes the whole endpoint displacement runs along
the path **and** that the other endpoint does not move. It is not a bound. It is retained only as a
comparison column.

### Results on the shortest path (`L_bind = 13.1646 mm`)

| pose | motion (IP/MCP/CMC deg) | L_bind | d_pose | **STRICT BOUND** | OLD CLAIM | observed max on path | observed global max | SLACK_5× |
|---|---|---|---|---|---|---|---|---|
| TH_IP_30 | 30 / 0 / 0 | 13.1646 | 15.9183 | **1.2092** | 2.2753 | 1.8168 | 2.1949 | +49.90 |
| TH_IP_45 | 45 / 0 / 0 | 13.1646 | 23.1366 | **1.7575** | 2.8856 | 2.7868 | 3.1838 | +42.69 |
| TH_MCP_45 | 0 / 45 / 0 | 13.1646 | 43.5353 | **3.3070** | 4.4608 | 5.1942 | 6.1560 | +22.29 |
| CMC_OPP_30 | 0 / 0 / 30 | 13.1646 | 51.3588 | **3.9013** | 4.7677 | 5.9617 | 7.3462 | +14.46 |
| CMC_MCP_L3 | 0 / 30 / 30 | 13.1646 | 78.5173 | **5.9643** | 6.8636 | 9.1959 | 11.0413 | **−12.69** |
| FULL_OPP_L3 | 15 / 30 / 30 | 13.1646 | 85.7800 | **6.5160** | 7.4096 | 10.0555 | 11.0413 | **−19.96** |

Max over the ten near-shortest paths (not only the minimum): `CMC_MCP_L3 = 5.9643`,
`FULL_OPP_L3 = 6.5160`; all other poses stay below 4.0.

**`OLD_GEOMETRIC_IMPOSSIBILITY_CLAIM = INVALID / UNSUPPORTED`.**
The old claim exceeds the strict bound by `+0.85 … +1.25` in every pose and was therefore an over-estimate.
`R1E_STRICT_GEOMETRIC_BOUND_AUDIT.json`, `renders/R1E_STRICT_BOUND_VS_OBSERVED.png`.

### Movement character

`Δu = u_B − u_A` was decomposed: `|u_A|` (cap endpoint), `|u_B|` (collar endpoint), `|Δu|`,
`dot(normalise(r₀), Δu)` and `angle(r₀, Δu)`. For the shortest path the movement is **oblique/along** the
bind separation in the MCP-dominated poses and consequently the strict bound is a genuine path limit,
not a by-product of perpendicular motion.
`R1E_STRICT_BOUND_VS_OBSERVED.png` shows the red observed-max bar sitting **above** the blue strict bound in
`TH_MCP_45 (5.19 vs 3.31)` and `CMC_OPP_30 (5.96 vs 3.90)` — i.e. those two poses have real, unused headroom.

---

## 9. Finding F — endpoint constraint authority (section 16)

| endpoint | current value | proven-classification | evidence |
|---|---|---|---|
| **A — approved distal cap** (9 verts) | `THUMB_IP_R = 1.0` on all 9 | **`BINDING_PROJECT_AUTHORITY`** | Stage5B R1A decision (`THUMB_DISTAL` region → `THUMB_IP_R`, dominant = 1.0), carried verbatim into the frozen R1B master; previous-round Human-Review section 14A forbids a `WRIST_R` island or an `INDEX_*` dominant island there. R1E kept `THUMB_IP_R = 1.0` on all nine cap vertices. |
| **B — exact R3 collar** (32 verts) | `WRIST_R = 1.0` on both sides | **`R1E_IMPLEMENTATION_CHOICE`** | R1B carried `INDEX_MCP_R 0.83–0.98` (+ `INDEX_PIP_R 0.02–0.17`) at exactly these vertices; `DIGIT_OWNERSHIP_AUTHORITY_R3` is explicitly *not* a skin-weight authority. The `WRIST_R = 1.0` collar field was introduced by R1E's own palm valley in the previous round. |

**Caveat recorded for honesty (Finding F′)**: two of the nine cap vertices (`v1061`, `v2189`) were not
*bit*-identical between R1B and R1E — R1E's renormalisation dropped residual `INDEX_PIP_R / INDEX_DIP_R`
traces of order `2.4e-04`. The dominant group and the `THUMB_IP_R` value are identical before and after,
so the **endpoint transform is unchanged**, but the difference is disclosed rather than hidden.

With endpoint B classified as an implementation choice, the governing rule of section 16 applies:

> **`CURRENT_R1E_ENDPOINT_KINEMATICS_INFEASIBLE`** — and **not**
> “any weight assignment infeasible”.
`R1E_ENDPOINT_CONSTRAINT_AUTHORITY_AUDIT.json`.

---

## 10. Finding G — where the severe strain actually lives

| pose | severe total | LEVEL_0 | LEVEL_1 | LEVEL_2 | LEVEL_3 | LEVEL_4+ | dominant semantic pair |
|---|---|---|---|---|---|---|---|
| CMC_OPP_30 | 32 | **0** | 12 | 16 | 0 | 4 | `THUMB_DISTAL｜THUMB_DISTAL` (25) |
| CMC_MCP_L3 | 39 | **0** | 16 | 16 | 0 | 7 | `THUMB_DISTAL｜THUMB_DISTAL` (29) |
| FULL_OPP_L3 | 41 | **0** | 16 | 16 | 0 | 9 | `THUMB_DISTAL｜THUMB_DISTAL` (31) |

* **No exact R3 boundary edge is ever severe** in any pose.
* The strain is concentrated in the **`LEVEL_1 + LEVEL_2` band** — the two mesh rings that carry the R1E
  palm-valley ramp between the collar and the thumb chain (32 of 41 severe edges in FULL_OPP_L3).
* The remaining `LEVEL_4+` edges (9 / 7 / 4) are **not** on the collar ramp; they sit at the boundary
  between the R1E reweighted region and the frozen first web / thenar (see Finding H).

`R1E_{CMC_OPP_30,CMC_MCP_L3,FULL_OPP_L3}_SEVERE_EDGE_TOPOLOGY_MAP.json`,
`renders/R1E_{FULL_OPP_L3,CMC_OPP30}_SEVERE_BY_COLLAR_DISTANCE.png`,
`renders/R1E_TRANSITION_WEIGHT_FIELD_WITH_SEVERE_EDGES.png`.

---

## 11. Finding H — edge 5879 forensic (the reported global max)

| property | value |
|---|---|
| endpoints | `v1551 ↔ v3125` |
| bind length | `3.3701 mm` |
| R3 ownership | `THUMB / THUMB` |
| semantic regions | `THUMB_DISTAL` / **`FIRST_WEB`** (v3125 ∈ the frozen 21-vertex first web) |
| graph distance to exact collar | `12 / 12` → **LEVEL_4_PLUS_TRANSITION** (not a collar edge) |
| graph distance to distal cap | `8 / 9` |
| weights R1B | v1551 `{THUMB_IP_R 0.0316, THUMB_MCP_R 0.9684}` ; v3125 `{THUMB_MCP_R 1.0}` |
| weights R1E | v1551 `{WRIST_R 0.94, THUMB_MCP_R 0.06}` ; v3125 `{THUMB_MCP_R 1.0}` (frozen first web) |
| worst pose / ratio | `CMC_MCP_L3` / `11.0413×` |

In the **R1B master this edge was a 1.0× edge** — both endpoints were `THUMB_MCP_R`-driven. The `11.04×`
differential was **created by R1E**: the lateral gate handed `v1551` to the palm while its neighbour is a
frozen first-web vertex. This is a **weight-transition partitioning defect, not a geometric limit**.

**`WEIGHT_TRANSITION_NOT_YET_OPTIMAL`** (per section 24). `R1E_EDGE5879_FORENSIC_AUDIT.json`,
`renders/R1E_EDGE5879_NEIGHBORHOOD.png`.

---

## 12. Finding I — same-surface self-intersection topology

Definition: a **new** intersection pair whose two faces lie inside the **same** side of the R3 collar cut
(thumb/INDEX contact pairs are therefore excluded).

| pose | same-surface new pairs | EXACT_COLLAR band | ONE_RING | TWO_RING | 3+ rings | dominant semantic pair |
|---|---|---|---|---|---|---|
| TH_IP_45 (control) | 31 | 22 | 7 | 0 | 2 | `THUMB_DISTAL｜THUMB_DISTAL` (19) |
| CMC_OPP_30 | 239 | 13 | 49 | 8 | 169 | `THUMB_DISTAL｜THUMB_DISTAL` (85), `PALM｜THUMB_DISTAL` (52) |
| CMC_MCP_L3 | 194 | 15 | 17 | 16 | 146 | `THUMB_DISTAL｜THUMB_DISTAL` (82), `PALM｜THUMB_DISTAL` (41) |
| FULL_OPP_L3 | 194 | 15 | 17 | 15 | 149 | `THUMB_DISTAL｜THUMB_DISTAL` (81), `PALM｜THUMB_DISTAL` (41) |

The dominant region is the **thumb distal / palm transition band**, again not the exact collar.
`R1E_SAME_SURFACE_SI_TOPOLOGY_AUDIT.json`.

---

## 13. Finding J — control pose and motion decomposition

| pose | THUMB_IP° | THUMB_MCP° | CMC opposition° | severe | max stretch | strict bound |
|---|---|---|---|---|---|---|
| TH_IP_30 | 30 | 0 | 0 | **0** | 2.19× | 1.34 |
| **TH_IP_45 (CONTROL_PASS)** | 45 | 0 | 0 | **0** | 3.18× | 1.93 |
| TH_MCP_45 | 0 | 45 | 0 | **17** | 6.16× | 3.37 |
| CMC_OPP_30 | 0 | 0 | 30 | 32 | 7.35× | 3.90 |
| CMC_MCP_L3 | 0 | 30 | 30 | 39 | 11.04× | 5.96 |
| FULL_OPP_L3 | 15 | 30 | 30 | 41 | 11.04× | 6.52 |

**The first severe population appears the moment THUMB_MCP enters the motion.**
45° of pure IP flexion is clean (control passes); the same 45° applied to the MCP produces 17 severe edges.
Adding MCP to a CMC opposition roughly doubles the residual (32 → 39). The residual is therefore
dominated by the **MCP/proximal component acting on the transition band**, not by the IP.

---

## 14. Verdict

* **Suspicion A**: `OLD_GEOMETRIC_IMPOSSIBILITY_CLAIM = INVALID / UNSUPPORTED`. The old formula was never
  a strict bound; the correct `STRICT_LOWER_BOUND = d_pose / L_bind` is `−0.85 … −1.25` lower everywhere.
* **Suspicion B**: confirmed. **All 16 exact R3 boundary edges are invariant (ratio 1.000000) in all six
  poses**; the old `5 / 12 / 16 / 16` collar-severe counts are **100 % `LEVEL_1`** — a classification
  artefact, not a skin-weight stretch.
* **Strict bound > 5×** holds only for `CMC_MCP_L3 (5.9643)` and `FULL_OPP_L3 (6.5160)`, and only on
  `3 / 10` and `6 / 10` of the near-shortest paths. `TH_IP_30 / TH_IP_45 / TH_MCP_45 / CMC_OPP_30`
  are all **≤ 3.9013**, i.e. **geometrically compliant with the 5× gate on these paths**.
* **Endpoint authority**: the cap endpoint is a genuine frozen authority; the **collar endpoint is an R1E
  implementation choice**. Therefore only `CURRENT_R1E_ENDPOINT_KINEMATICS_INFEASIBLE` is admissible —
  **not** “any weight assignment infeasible”, and **not** “mesh geometrically impossible”.

### Branch (section 31)

```
BRANCH = B
STRICT_LOWER_BOUND > 5 on some paths, AND at least one endpoint transform
(the exact R3 collar, WRIST_R = 1.0) is an R1E implementation choice.

NEXT_CANDIDATE = ENDPOINT_WEIGHT_AUTHORITY_REVIEW
```

**Also recorded**: for `TH_MCP_45` and `CMC_OPP_30` the strict bound is below 5× while the observed max is
above it, so those two poses simultaneously satisfy branch **A**'s premise
(`NEXT_CANDIDATE = R1E_TRANSITION_WEIGHT_FIELD_RECONCILIATION_R2`). The transition field demonstrably has
headroom there, and edge 5879 is a concrete, reproducible instance of that headroom.

---

## 15. What is **NOT** claimed

Unless branch C's conditions are met — and they are not — the following wordings are forbidden and
**none of them appears in any output of this round**:

* `ANY WEIGHT ASSIGNMENT MUST FAIL`
* `GEOMETRICALLY IMPOSSIBLE`
* `MESH CANNOT SUPPORT L3`
* `RETOPO REQUIRED`

The single permitted statement of limitation is:

> `CURRENT_MESH_SUPPORT_INSUFFICIENT_FOR_THIS_POSE_RANGE` = **NOT_PROVEN**
> (only `CURRENT_R1E_ENDPOINT_KINEMATICS_INFEASIBLE` is supported, and only for `CMC_MCP_L3` /
> `FULL_OPP_L3`, on 3/10 and 6/10 tested paths).

---

## 16. Deliverables

| file | content |
|---|---|
| `R1E_THUMB_TRANSITION_GEOMETRIC_FEASIBILITY_REPORT.md` | this report |
| `R1E_THUMB_TRANSITION_GEOMETRIC_FEASIBILITY_STATUS.json` | status, findings, branch, next candidate |
| `R1E_EXACT_R3_COLLAR_DYNAMIC_AUDIT.json` | 16 exact edges × 6 poses, full weights + transforms |
| `R1E_OLD_COLLAR_SEVERE_RECLASSIFICATION.json` | 5 / 12 / 16 / 16 re-binned into LEVEL_0…LEVEL_4+ |
| `R1E_CAP_TO_COLLAR_SHORTEST_PATH_AUDIT.json` | full expansion of the shortest path + all 144 pairs |
| `R1E_CAP_TO_COLLAR_PATH_ENSEMBLE_AUDIT.json` | 144-pair statistics + top-10 expanded paths |
| `R1E_ENDPOINT_CONSTRAINT_AUTHORITY_AUDIT.json` | endpoint A / B provenance classification |
| `R1E_STRICT_GEOMETRIC_BOUND_AUDIT.json` | strict vs old bound, endpoint geometry, Δu decomposition |
| `R1E_FULL_OPP_L3_SEVERE_EDGE_TOPOLOGY_MAP.json` | severe edges by level + semantic region |
| `R1E_CMC_OPP30_SEVERE_EDGE_TOPOLOGY_MAP.json` | same |
| `R1E_CMC_MCP_L3_SEVERE_EDGE_TOPOLOGY_MAP.json` | same |
| `R1E_EDGE5879_FORENSIC_AUDIT.json` | edge 5879 full forensic |
| `R1E_SAME_SURFACE_SI_TOPOLOGY_AUDIT.json` | same-surface SI by region |
| `R1E_MOTION_DECOMPOSITION.json` | motion components / control-pose comparison |
| `renders/` | 10 evidence PNGs |

Stage5B R1E is **unchanged**; R1F was **not** created; no weight, cap, collar, mesh, bone, joint, roll,
CMC cage, RSSF or opposition value was touched.

**STOP — awaiting Human Review.**
