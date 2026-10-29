# CAP_FIXTURE_STATIC_VALIDATION_AND_TARGETED_DEFORMATION_R1

**FAIL_CLOSED_TARGETED_DEFORMATION — STOP / HUMAN REVIEW OF BLOCKING FAILURE**

静态输入确认通过，五个 fixture 的严重伸长、collapse/degenerate 与 0.05 局部面积毁损指标均为零；但 cap37 的 frozen two-ring 连续性邻域存在三条既有 R1C V2 判据确认的 THUMB–INDEX 几何穿插观测。本轮停止，不修权重，不启动后续 recovery。

| Required field | Result |
|---|---|
| `CAP_FIXTURE_STATIC_VALIDATION` | `PASS` |
| `CAP37_TARGETED_DEFORMATION` | `FAIL_CLOSED` |
| `OLD_CAP9_TARGETED_DEFORMATION` | `PASS_PENDING_HUMAN_REVIEW` |
| `FIRST_WEB_TARGETED_DEFORMATION` | `PASS_PENDING_HUMAN_REVIEW` |
| `FRESH_R3_TRANSITION_COLLAR_TARGETED_DEFORMATION` | `PASS_PENDING_HUMAN_REVIEW` |
| `EDGE5879_TARGETED_DEFORMATION` | `PASS_PENDING_HUMAN_REVIEW` |
| `CORRECTED_THUMB_CHAIN_INPUT` | `PASS` |
| `INHERITED_DEBT_TOTAL` | `16` |
| `INHERITED_DEBT_MAPPED` | `16` |
| `INHERITED_DEBT_TRUE_DEFORMATION_FAILURE` | `0` |
| `STATIC_DEBT_WITHOUT_TRUE_DEFORMATION_FAILURE` | `16` |
| `CANDIDATE_INTRODUCED_FAILURE_COUNT` | `3` |
| `R2_INCREMENTAL_INTRODUCED_FAILURE_COUNT` | `0` |
| `PRODUCTION_WEIGHT_DRIFT` | `0` |
| `GEOMETRY_DRIFT` | `0` |
| `TOPOLOGY_DRIFT` | `0` |
| `BONE_JOINT_DRIFT` | `0` |
| `TARGETED_DEFORMATION_VERDICT` | `FAIL_CLOSED_TARGETED_DEFORMATION` |

## Blocking failure and attribution

`CANDIDATE_INTRODUCED_FAILURE_COUNT=3` 的基准是历史 R1B donor → corrected recovery candidate，单位为 pose/face-pair；**R2 相对 corrected R1 的增量新增为 0**。三对几何交叉已经存在于 corrected R1，不能归因于本轮只读验证或 R2 新改坏；它们也不属于本轮 16 条 inherited static debt 的 endpoint incident patch。这个区分不解除当前 candidate 的资格阻塞。

| Pose | Face pair | R2 footprint-constrained poke mm | Bind facet mean mm | Exact crossing segment mm | Historical same pair |
|---|---|---:|---:|---:|---|
| TH_IP_30 | [1225, 2740] | 5.500166 | 4.372096 | 0.929853 | R1B/R1E absent; corrected R1 present |
| IDX_MCP_45 | [1041, 2735] | 3.709175 | 3.619188 | 0.592590 | R1B/R1E absent; corrected R1 present |
| IDX_MCP_45 | [1226, 2742] | 4.626237 | 4.166125 | 0.350317 | R1B/R1E absent; corrected R1 present |

Failure classification: `CANDIDATE_INTRODUCED_DEFORMATION_FAILURE` relative to historical donor; carried forward from corrected R1. Frozen pure-face labels identify both sheets as THUMB and INDEX; this is cross-surface geometric penetration, not illegal foreign driver leakage. The affected THUMB faces are in the cap two-ring, not the 37 core cap points.

Reuse: Stage6A `TH_IP_30` isolated local-X −30° and original `IDX_MCP_45` local-X −45°; Stage6B R1C V2 `pair_evidence`/`classify`: a real triangle crossing plus footprint-constrained poke depth at least one bind local-facet mean length. No new anatomical threshold. All three are away from the classification boundary, have exact crossing points, and have matching isolated-pair renders plus full surface views.

- TH_IP_30 faces [1225, 2740]: vertices `[148, 299, 1053, 1385, 1453, 2062, 2786, 3165]`; bones `['INDEX_DIP_R', 'INDEX_MCP_R', 'INDEX_PIP_R', 'THUMB_IP_R', 'THUMB_MCP_R', 'WRIST_R']`. Outside317 `[148, 1053, 2062, 3165]`. [Matched R2 geometry](../../../../artifacts/a9639e71ffbb1f662c77.md).
- IDX_MCP_45 faces [1041, 2735]: vertices `[282, 655, 1337, 1339, 2064, 2066, 2740, 3163]`; bones `['INDEX_DIP_R', 'INDEX_MCP_R', 'INDEX_PIP_R', 'THUMB_IP_R', 'THUMB_MCP_R', 'WRIST_R']`. Outside317 `[]`. [Matched R2 geometry](../../../../artifacts/3c9ff5ea2f855fc8e5a6.md).
- IDX_MCP_45 faces [1226, 2742]: vertices `[342, 654, 1381, 1385, 2063, 2068, 2786, 3165]`; bones `['INDEX_DIP_R', 'INDEX_MCP_R', 'INDEX_PIP_R', 'THUMB_IP_R', 'THUMB_MCP_R', 'WRIST_R']`. Outside317 `[2068, 3165]`. [Matched R2 geometry](../../../../artifacts/862dc407c3a877f8d2bd.md).

The future remedy is **not determined here**. If a proposed weight remedy touches listed outside317 vertices, it needs a separate scope amendment; changing pinned corrected quintic semantics needs separate authority review. No broader scope is inferred or applied. Full endpoint vectors and historical per-pair measurements are in `TARGETED_BLOCKING_FAILURE_CLASSIFICATION.json`.

## Historical reuse and bounded measurements

The six R1D/R1E targeted poses were reused verbatim: TH_IP_30, TH_IP_45, TH_MCP_45, CMC_OPP_30, CMC_MCP_L3, FULL_OPP_L3. One existing IDX_MCP_45 case checks native old9 INDEX compatibility. CMC cases are **TARGETED_DIAGNOSTIC_PROBE only**; no opposition or Stage6B pass claim. Four immutable skin assets were measured in memory: historical R1E, R1B donor, corrected R1 and R2. No Action, harness blend, production weights, rest bones or joint positions were created/edited/saved.

Existing Stage6A R1B metrics, R1E pose primitives/BVH and R1C V2 crossing classifier were executed from their existing definitions. An adapter supplies the frozen corrected selector and candidate. Legacy top-level scripts were not executed. Their old cap9 cap gate and old whole-mesh R3 cut-component ownership classifier are explicitly retired; no replacement anatomical split is invented. Function AST hashes and full source hashes are included.

| Fixture | Targeted result | Min face-area ratio | Min compression edge ratio | Severe observations | V2 Class A observations |
|---|---|---:|---:|---:|---:|
| CAP37 | FAIL_CLOSED | 0.808573 | 0.802951 | 0 | 3 |
| OLD_CAP9 | PASS_PENDING_HUMAN_REVIEW | 0.775605 | 0.868139 | 0 | 0 |
| FIRST_WEB | PASS_PENDING_HUMAN_REVIEW | 0.427630 | 0.382217 | 0 | 0 |
| FRESH_R3_TRANSITION_COLLAR | PASS_PENDING_HUMAN_REVIEW | 0.088754 | 0.397935 | 0 | 0 |
| EDGE5879 | PASS_PENDING_HUMAN_REVIEW | 0.427630 | 0.600565 | 0 | 0 |

The collar retains diagnostic normal flips/contact and compression under CMC probes. They do not meet the existing collapse/area-destruction/visible-crossing criterion and remain Human Review for contour, crease, pinching, volume appearance and teaching readability. The same applies to all nonblocking fixture results; `PASS_PENDING_HUMAN_REVIEW` is bounded machine qualification, not FINAL.

| edge5879 pose | R1E rerun | corrected R1 | R2 |
|---|---:|---:|---:|
| TH_IP_30 | 1.000023 | 0.999999 | 0.999996 |
| TH_IP_45 | 1.000031 | 0.999999 | 0.999996 |
| TH_MCP_45 | 6.156014 | 3.541361 | 1.062028 |
| CMC_OPP_30 | 7.250812 | 4.073856 | 1.081635 |
| CMC_MCP_L3 | 11.041275 | 6.084938 | 1.136250 |
| FULL_OPP_L3 | 11.041243 | 6.084938 | 1.136250 |

R1E rerun reproduces all six historical edge5879 ratios within one reported 4-decimal ratio unit (0.0001x). The saved world-mm float32 snapshot produces a shared bind-evaluation residual of 0.000134mm; FULL_OPP_L3 lies on the last-digit rounding boundary. This is numeric storage precision, not a new gate tolerance or pose change. Worst historical trigger `CMC_MCP_L3`: approximately 11.04128x → R2 1.13625x; same original CMC quaternion/MCP angle, corrected candidate input. This is a targeted diagnostic result only.

## Sixteen inherited debt dispositions

All16 mapped to frozen endpoint driver support → existing thumb transition fixture → relevant subset of six historical poses. Every endpoint vector remains donor-exact. No debt endpoint or incident patch produced severe ≥3mm/>5x stretch, collapsed/degenerate geometry, face area below0.05, or V2 visible geometric interpenetration. All16 are `STATIC_QUALIFICATION_DEBT_WITHOUT_TRUE_DEFORMATION_FAILURE` in this bounded run.

| Debt | Driver region | Max edge ratio | >3x strain poses | True failure |
|---|---|---:|---|---:|
| 1130 | THUMB_IP_MCP_FIRST_WEB_INTERFACE | 1.000011 | none | 0 |
| 1137 | THUMB_IP_MCP_FIRST_WEB_INTERFACE | 1.611993 | none | 0 |
| 1171 | THUMB_CMC_MCP_TRANSITION | 2.007951 | none | 0 |
| 1172 | THUMB_CMC_MCP_TRANSITION | 2.560319 | none | 0 |
| 1174 | THUMB_CMC_MCP_TRANSITION | 3.481454 | CMC_OPP_30, CMC_MCP_L3, FULL_OPP_L3 | 0 |
| 1176 | THUMB_CMC_MCP_TRANSITION | 3.003059 | CMC_OPP_30 | 0 |
| 1555 | THUMB_CMC_WRIST_TRANSITION | 1.580691 | none | 0 |
| 4417 | THUMB_CMC_MCP_TRANSITION | 2.149348 | none | 0 |
| 4421 | THUMB_CMC_MCP_TRANSITION | 3.459129 | CMC_OPP_30, CMC_MCP_L3, FULL_OPP_L3 | 0 |
| 4425 | THUMB_CMC_MCP_TRANSITION | 3.143431 | CMC_MCP_L3, FULL_OPP_L3 | 0 |
| 4427 | THUMB_CMC_MCP_TRANSITION | 2.171336 | none | 0 |
| 4428 | THUMB_CMC_MCP_TRANSITION | 1.333024 | none | 0 |
| 4431 | THUMB_CMC_MCP_TRANSITION | 1.649300 | none | 0 |
| 4474 | THUMB_IP_MCP_FIRST_WEB_INTERFACE | 1.000004 | none | 0 |
| 4881 | THUMB_CMC_WRIST_TRANSITION | 1.473503 | none | 0 |
| 5474 | THUMB_CMC_WRIST_TRANSITION | 1.645091 | none | 0 |

Some proximal seam edges exceed the old >3x/>5mm **strain diagnostic**, but have no local surface destruction; existing Stage6B R1B explicitly distinguishes seam strain from actual tearing. Natural contour/strain appearance remains Human Review. Static debt is retained; no automatic scope expansion. Driver CMC/MCP/WRIST transforms are donor-identical. IP driven interface cases use the approved corrected IP transform; the mapping records this difference rather than claiming identical historical rig matrices.

## Read-only protection and evidence

Independent clean reopen after measurement/rendering: all3416 vectors, geometry, topology, UV, binding/groups and21 bone/rest/pose snapshots equal saved R2 and pre-test payload. Candidate SHA256 `adf757aeace8a0d69070b94f102b9bef9eb99da9847dd7a5639c4c2c3799dde9`; vector SHA256 `1d9437a10354cdd98a2b5cb5e43be8cfabc519e232235483a615e76898129f55`. All 2172 historical files match the before inventory exactly; new files occur only in this qualification directory.

[Human Review](../../../../artifacts/c8e7205c45880ff2c327.md) provides 84 matched full surface/strain/pair-isolation PNGs. Camera directions and light follow R1E/feasibility conventions. Centre, scale and pose are shared across all candidates for each comparison; one common framing contains every posed region, with no core clipping. Yellow core markers, green fresh20 boundary edges; isolated pairs are supplementary geometric evidence, not anatomy proof.

## Stop state

No full Stage6A/B, no true-cap bound recompute, no R3 rerun, no skin rebuild, no new anatomical rule, no production freeze/promotion. Required successful recovery sequence is blocked by this targeted failure; it has not started.

**NEXT = STOP — HUMAN REVIEW OF BLOCKING FAILURE.**
