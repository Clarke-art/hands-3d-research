# STAGE6B R1B -- FULL OPPOSITION RETEST (9 cases)

Generated: `2026-09-30T22:53:43.805072+08:00`  
Harness: `stage6b_r1b/RIGHT_HAND_STAGE6B_OPPOSITION_HARNESS_R1B.blend` (built from the Stage5B R1C candidate).

The CMC opposition unit rotation and the axial twist sign are the **frozen Stage6B R1 values**, reused
verbatim (no re-solve): `[-0.868788327174, -0.250000007244, -0.427442205385]`, twist sign `-1`.

## 1. Historic Class-B 61-edge probe (before / after)

| case | R1 max stretch | R1 torn (>3x & >5mm) | R1B max stretch | R1B torn |
|---|---|---|---|---|
| CMC_OPP_10 | 12.5977 | 48 / 61 | **1.0001** | **0 / 61** |
| CMC_OPP_20 | 25.5140 | 64 / 61 | **1.0000** | **0 / 61** |
| CMC_OPP_30 | 38.2469 | 67 / 61 | **1.0000** | **0 / 61** |
| CMC_MCP_L1 | 19.5493 | 63 / 61 | **1.0000** | **0 / 61** |
| CMC_MCP_L2 | 38.9758 | 67 / 61 | **1.0000** | **0 / 61** |
| CMC_MCP_L3 | 57.4720 | 67 / 61 | **1.0000** | **0 / 61** |
| FULL_OPP_L1 | 20.9960 | 63 / 61 | **1.0200** | **0 / 61** |
| FULL_OPP_L2 | 41.7740 | 67 / 61 | **1.0401** | **0 / 61** |
| FULL_OPP_L3 | 61.3116 | 67 / 61 | **1.0602** | **0 / 61** |

`HISTORIC_CLASS_B_EDGE_TEAR` = **CLOSED** in all 9 cases (round spec section 22 gate: 0 edges over 3x AND over 5 mm).

## 2. Corrected ownership boundary (R2) deformation

The corrected THUMB|INDEX ownership boundary (22 edges at the thumb tip / first web) was measured with
the same freeze criterion:

| case | boundary edges | max stretch | torn |
|---|---|---|---|
| CMC_OPP_10 | 22 | 1.000415 | 0 |
| CMC_OPP_20 | 22 | 1.011742 | 0 |
| CMC_OPP_30 | 22 | 1.033242 | 0 |
| CMC_MCP_L1 | 22 | 1.000004 | 0 |
| CMC_MCP_L2 | 22 | 1.016675 | 0 |
| CMC_MCP_L3 | 22 | 1.055854 | 0 |
| FULL_OPP_L1 | 22 | 1.000004 | 0 |
| FULL_OPP_L2 | 22 | 1.016675 | 0 |
| FULL_OPP_L3 | 22 | 1.055854 | 0 |

## 3. Region gates

| case | CMC cage min face-area | min edge | fold-over | new cage self-intersection | thenar bbox vol | first-web area | first-web tear |
|---|---|---|---|---|---|---|---|
| CMC_OPP_10 | 0.849356 | 0.839297 | False | 0 | 0.9737 | 0.9569 | False |
| CMC_OPP_20 | 0.718022 | 0.714090 | False | 0 | 0.9483 | 1.0774 | False |
| CMC_OPP_30 | 0.624729 | 0.629499 | False | 0 | 0.9359 | 1.2410 | False |
| CMC_MCP_L1 | 0.849356 | 0.839297 | False | 0 | 0.9920 | 0.9923 | False |
| CMC_MCP_L2 | 0.718022 | 0.714090 | False | 0 | 0.9706 | 1.0913 | False |
| CMC_MCP_L3 | 0.624729 | 0.629499 | False | 0 | 0.9488 | 1.1471 | False |
| FULL_OPP_L1 | 0.849356 | 0.839297 | False | 0 | 0.9920 | 0.9923 | False |
| FULL_OPP_L2 | 0.718022 | 0.714090 | False | 0 | 0.9706 | 1.0913 | False |
| FULL_OPP_L3 | 0.624729 | 0.629499 | False | 0 | 0.9488 | 1.1471 | False |

- `CMC_CAGE_DYNAMIC_QUALIFICATION` = **PASS** (fold-over 0, no new cage self-intersection)
- `CMC_CAGE_UNCHANGED_VS_R1` = **True** (identical min face-area / min edge ratios)
- `FIRST_WEB` = **NO_REGRESSION** (area ratio identical to R1, no tear)

## 4. Contact progression with the corrected ownership (section 27)

| case | R1 thumb-index pairs | R1B thumb-index pairs | R1 max pen (mm) | R1B max pen (mm) | R1 >0.5mm | R1B >0.5mm |
|---|---|---|---|---|---|---|
| CMC_OPP_10 | 119 | **8** | 2.4151 | 3.0008 | 118 | 60 |
| CMC_OPP_20 | 110 | **6** | 3.4701 | 3.3936 | 137 | 116 |
| CMC_OPP_30 | 100 | **6** | 4.1770 | 3.4173 | 165 | 200 |
| CMC_MCP_L1 | 108 | **12** | 2.9544 | 2.5963 | 121 | 81 |
| CMC_MCP_L2 | 95 | **13** | 2.4347 | 3.3123 | 160 | 148 |
| CMC_MCP_L3 | 85 | **8** | 2.5703 | 4.3112 | 167 | 146 |
| FULL_OPP_L1 | 116 | **13** | 3.0753 | 2.8571 | 130 | 87 |
| FULL_OPP_L2 | 93 | **12** | 2.5720 | 3.0527 | 156 | 124 |
| FULL_OPP_L3 | 83 | **7** | 3.5676 | 4.6857 | 163 | 150 |

## 5. Nail / distal cap

| case | R1 nail rigid fit rel | R1B nail rigid fit rel | R1B cap area ratio | R1B cap displacement max (mm) | R1B cap rigid fit rel |
|---|---|---|---|---|---|
| CMC_OPP_10 | 0.000013 | 0.000013 | 1.000101 | 16.873 | 0.000011 |
| CMC_MCP_L3 | 0.000015 | 0.000015 | 1.001021 | 79.498 | 0.000010 |
| FULL_OPP_L3 | 0.134088 | 0.133808 | 1.000451 | 87.232 | 0.000007 |

`NAIL_DEFORMATION` = **NO_REGRESSION**, `DISTAL_CAP` = **NO_REGRESSION** (the cap follows the thumb
and keeps its rigid-unit behaviour).

## 6. Zero restore / progression / blockers

- `ZERO_RESTORE` = **PASS** (max 0.000031224 mm, hard gate 1e-04 mm)
- `TIP_PROGRESSION_CONTINUITY` = **PASS**
- `PAD_ORIENTATION_CONTINUITY` = **PASS**
- `FIRST_WEB_PROGRESSIVE_CONTINUITY` = **PASS**
- blockers = **0**
