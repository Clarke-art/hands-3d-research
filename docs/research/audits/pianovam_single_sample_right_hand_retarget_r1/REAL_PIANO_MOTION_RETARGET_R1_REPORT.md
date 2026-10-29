# REAL_PIANO_MOTION_RETARGET_R1

**VERDICT = RETARGET_PIPELINE_NEEDS_WORK. STOP — HUMAN REVIEW.** A real seven-second physical-right PianoVAM sequence was successfully retargeted and rendered, but this result does not establish natural piano playing. Do not interpret it as RIGHT_HAND_BASELINE_FAIL or commercial motion approval.

The visible blockers are (1) a jagged inward first-web fold, visible particularly at source 15.5–15.8 s / review 4.0–4.3 s and 18.3 s / review 6.8 s, and (2) pronounced PIP/DIP fingertip folding and quick reversals that remain after light filtering. The palm/thenar retain broad volume in the two ordinary solid views. No gross whole-hand collapse or open mesh tearing was observed in the agent's visual precheck. Local first-web penetration is **not cleared**. Human judgment remains pending. Visual issue families, not a hidden crossing census: one deformation blocker and one motion naturalness blocker.

| Final field | Value |
|---|---|
| DATASET | PianoVAM_v1 |
| DATASET_VERSION | v1.2 |
| LICENSE | CC BY-NC-SA 4.0 |
| USAGE_SCOPE | INTERNAL_NONCOMMERCIAL_VALIDATION_ONLY |
| SOURCE_RECORDING_ID | 2024-03-04_03-46-36 |
| SOURCE_PIECE | N/A [Piano Sonata No. 16 in C Major, K.545 (1st Mvt)] |
| SOURCE_PERFORMER | Yonghyun |
| DOWNLOADED_FILE_COUNT | 5 |
| DOWNLOADED_BYTES | 10679148 |
| WINDOW_START_SEC | 11.5 |
| WINDOW_END_SEC | 18.5 |
| WINDOW_DURATION_SEC | 7.0 |
| RIGHT_HAND_VALID_FRAME_RATIO | 1.0 |
| RIGHT_HAND_NOTE_COUNT | 39 |
| RIGHT_HAND_FINGERS_PRESENT | [1, 2, 3, 4, 5] |
| LANDMARK_ORDER_VERIFIED | YES |
| BONE_MAPPING_COMPLETE | YES |
| WRIST_RETARGET_MODE | B_FIXED_TRANSLATION_SOURCE_PALM_ORIENTATION |
| TEMPORAL_SMOOTHING_USED | YES_LIGHT_3_TAP |
| RETARGET_FRAME_COUNT | 421 |
| BONE_FLIP_COUNT | 0 |
| VISIBLE_DEFORMATION_BLOCKER_COUNT | 1 |
| FIRST_WEB_VISIBLE_STATUS | LOCAL_JAGGED_FOLD_BLOCKER_UNDER_THIS_RETARGET |
| THENAR_PALM_VISIBLE_STATUS | NO_GROSS_COLLAPSE_OBSERVED_IN_TWO_REVIEW_VIEWS_AGENT_PRECHECK |
| ZERO_RESTORE | PASS |
| RIGHT_HAND_BASELINE_MODIFIED | NO |
| RETARGET_EXECUTED | YES |
| REAL_PIANO_MOTION_VISIBLE_STATUS | NOT_CLEARED_NATURALNESS_AND_FIRST_WEB_BLOCKERS |
| PRODUCTION_PROMOTION | NO |
| VERDICT | RETARGET_PIPELINE_NEEDS_WORK |

Wrist mode B fixes translation and copies only relative source palm orientation, plus articulation. Every frame forms a stable palm basis from wrist/index/middle/little MCP, aspect-corrected image coordinates, and expresses all 21 points locally. Parent-first minimal swing aligns each approved bone direction to its corresponding source segment. Local quaternion removes the predicted parent/rest rotation. Rest roll is transported, and no single-segment axial twist is invented. Frozen lengths, joint positions, hierarchy, mesh, Basis, UV, materials, all weights, the first-web key and driver remain exactly unchanged. All 21 names map; the five TIP helpers inherit their parents, remain non-deform, and have zero motion channels or new influences. 16 deform bones receive quaternion rotation keys only. 421 native 60fps observations use half-frame keys in a 30fps scene; rendered review is 210 frames / 7 seconds. Scene saved at motion frame 1.

The original retarget had 4 consecutive world direction changes above 90 degrees, consistent with conspicuous raw tracking pops. RAW_RETARGET_PREVIEW.mp4 and the raw Action are preserved. After visual raw inspection, one symmetric three-tap quaternion filter [0.25,0.5,0.25] at 60fps was applied, with sign continuity and normalization: neighbor support 33.3ms, zero phase, no heavy smoothing or motion synthesis. Final >90-degree flips = 0, quaternion sign discontinuities = 0, NaN/Inf = 0. Remaining maximum source-step world direction change is 46.839 degrees; that numeric pass does not clear visible naturalness. One hand-label mapping correction was used (limit two). No speculative second axis/depth correction was applied after exact source-direction alignment; stronger filtering or arbitrary depth scaling would conceal or reinterpret the source. Classification: source skeleton noise / retarget limitations; an intrinsic product-model deformation failure has not been isolated.

ZERO restoration: detach the test Action, reset all pose transforms, update dependency graph. All 3300 evaluated vertices match frozen baseline ZERO exactly; maximum error = 0.0 mm. Reattach Action for motion playback. First-web driver is preserved and evaluates in range [0.0, 0.31215521693229675]; its continued presence is not a claim that it clears every unqualified multi-axis source pose.

Protected native payload, rest matrices/head-tail/hierarchy, weights/groups, Basis and corrective coordinates/driver, UV, transforms, modifiers and materials were compared exactly before and after independent .blend save/reopen. Baseline SHA256 before and after:
`4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2`
Test SHA256: `43e8e2854aa24c74053830118ea6d939fc56af4efb450bf0098a7bd99838dae8`. Actions: PIANOVAM_PHYSICAL_RIGHT_RAW_R1 and PIANOVAM_PHYSICAL_RIGHT_SMOOTHED_R1. No baseline write occurred.

Review: review.html contains the solid palmar/dorsal two-view review.mp4, raw solid preview, synchronized original performance, source skeleton reference, handedness overlay and three unfilled Human questions. Audio is copied from the selected source video for synchronization only; no MIDI-to-hand or procedural note animation.

Q1: Overall right-hand motion natural? **ACCEPT / REJECT** — unanswered.
Q2: Obvious model deformation problem? **NO / YES** — unanswered.
Q3: Sufficient to advance to future piano motion / left-hand stage? **YES / NO** — unanswered.

Dataset v1.2, CC BY-NC-SA 4.0. [PianoVAM source and attribution](https://huggingface.co/datasets/PianoVAM/PianoVAM_v1); [license](https://creativecommons.org/licenses/by-nc-sa/4.0/). INTERNAL_NONCOMMERCIAL_VALIDATION_ONLY. DO_NOT_PROMOTE_DATASET_MOTION_TO_COMMERCIAL_PRODUCT. No extra recordings, training, MIDI generation system, left-hand work, Web export, stress matrix, normal-dot/crossing census, model repair or production promotion. Machine evidence: RETARGET_MACHINE_CHECKS_R1.json; all final fields and unfilled Human answers: REAL_PIANO_MOTION_RETARGET_R1_STATUS.json.
