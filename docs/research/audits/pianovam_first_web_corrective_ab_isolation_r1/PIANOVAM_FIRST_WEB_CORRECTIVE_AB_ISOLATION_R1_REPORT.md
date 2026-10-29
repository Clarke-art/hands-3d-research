# PIANOVAM_FIRST_WEB_CORRECTIVE_AB_ISOLATION_R1

**PRIMARY_CAUSE = RETARGET_ROTATION_OUT_OF_VALIDATED_RANGE**, under the requested Case B classification. **STOP — HUMAN REVIEW.** No repair was attempted.

CURRENT and CORRECTIVE_OFF show the same triangular notch, sharp inward fold and web contour in the selected solid views. The decisive finding is that **the corrective was already 0.0 in all eight selected defect frames**. Forcing it to zero leaves the defect unchanged. These frames do not support abnormal corrective/driver activation as the primary cause.

After unchanged A/B, one read-only rotation inspection compared exactly THUMB_CMC_R, THUMB_MCP_R, THUMB_IP_R and INDEX_MCP_R to INDEX_MCP_45, CMC_OPP_30 and FULL_OPP_L1/L2/L3. The clearest difference is INDEX_MCP_R: source local Euler X is **+8.994° to +13.240°**, whereas the approved representatives use **0° to −45°** around local X. Source local Z is **−20.101° to −2.637°**, while those reference fixtures use Z = 0. This is a visibly different direction/combination from what was approved. THUMB_CMC also uses a different swing direction, with source X from −7.094° to +10.177° and Z from −14.734° to −1.906°. Its total angle remains 10.358°–15.802°, below the 30° reference: the main mismatch is not blanket excessive magnitude.

These are **sampled representative-pose comparisons, not anatomical ROM, angle authority, or proof that the source posture is anatomically impossible**. The base skin outputs the fold under this combined motion; this isolation does not absolutely exonerate base-skin sensitivity. The user-defined Case C is not assigned because its condition (no clearly different/uncovered rotation direction) is not met. No weights were investigated beyond exact unchanged-payload verification.

## Input and selected frames

Source: `audits/pianovam_single_sample_right_hand_retarget_r1/RIGHT_HAND_PIANO_MOTION_TEST_R1.blend`
SHA256: `43e8e2854aa24c74053830118ea6d939fc56af4efb450bf0098a7bd99838dae8`
Action: `PIANOVAM_PHYSICAL_RIGHT_SMOOTHED_R1`. The existing smoothed 11.5–18.5 s / 421-observation sequence is used unchanged. Scene frame numbers are 1-based at 30fps; source video/skeleton frame = 690 + 2 × (scene frame − 1). `time_sec` is absolute source time. No new motion, window, sample or smoothing.

Eight defect frames include mild/moderate/severe/most-severe examples. Two relative-low-defect controls are included; they still have small folds and are not labeled fully normal. Severity was selected visually from the existing review frames, without numerical scoring. The current user explicitly rejected the prior real-motion retarget; that instruction is bound in PRIOR_RETARGET_HUMAN_REJECTION_BIND_R1.json. New A/B Human answers remain unfilled.

| Blender frame | Source frame | Source time s | Visual severity | CURRENT key | OFF key | Off improves / disappears |
|---|---|---|---|---|---|---|
| 16 | 720 | 12.000000 | MILD | 0 | 0 | NO / NO |
| 31 | 750 | 12.500000 | MODERATE | 0 | 0 | NO / NO |
| 76 | 840 | 14.000000 | SEVERE | 0 | 0 | NO / NO |
| 106 | 900 | 15.000000 | MODERATE | 0 | 0 | NO / NO |
| 121 | 930 | 15.500000 | SEVERE | 0 | 0 | NO / NO |
| 126 | 940 | 15.666667 | SEVERE | 0 | 0 | NO / NO |
| 130 | 948 | 15.800000 | MOST_SEVERE | 0 | 0 | NO / NO |
| 205 | 1098 | 18.300000 | MOST_SEVERE | 0 | 0 | NO / NO |
| 61 | 810 | 13.500000 | LOW_DEFECT_REFERENCE | 0 | 0 | NO / NO |
| 181 | 1050 | 17.500000 | LOW_DEFECT_REFERENCE | 0 | 0 | NO / NO |

## A/B method and driver readings

A = current driver-driven existing FIRST_WEB_OPPOSITION_CREASE_R1 value. B = direct temporary scalar `key.value = 0.0`, evaluated on the **same frame**. Because all selected A values were already zero, no driver mute, key mute, driver-expression change, key-content change or other animation-channel change was needed. After B, the original scalar/frame state was restored. No .blend was saved.

Exactly two views per selected frame: PALMAR_THENAR_CLOSE and FIRST_WEB_OBLIQUE. Cameras track the current web region only for framing; each A/B pair uses identical camera parameters, projection, resolution, neutral Workbench shading and all native faces. Both hands are the same original asset at the same source Action state. Evaluated A/B vertices are identical in all ten comparisons. This is an invariant check, not a numerical severity score; image encoding/shading may have negligible render variation, and no byte-identical-image claim is made.

The existing driver actually references `opp = THUMB_CMC_R LOCAL_SPACE ROT_X XYZ` and `mcp = THUMB_MCP_R LOCAL_SPACE ROT_X XYZ`. **INDEX_MCP_R is not a driver variable.** Actual driver inputs in radians/degrees and the driver value are recorded for each selected frame; recomputing the existing expression agrees with the evaluated scalar. This is a read of the current driver, not a new driver study. Defect-frame activation minimum = maximum = 0.0, active defect frames = 0/8. This conclusion applies to selected frames; it does not claim the corrective stays zero throughout the complete window.

## Preservation and output

Source and frozen baseline hashes are unchanged. Protected mesh/Basis, all weights, UV, material data, object transforms, modifiers, rest head/tail/matrices/hierarchy/deform flags, shape-key coordinates/settings and driver expression/targets/mute were compared exactly. Both source Actions' keyframe payload hashes remain unchanged. For each A/B pair all bone matrices, local quaternions, scale/location, current Action and frame match. Only the existing scalar zero override is requested, and here it equals the natural A value.

Frozen baseline SHA256: `4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2`. Its saved ZERO is intact; no baseline pose/channel or production file write occurred. All temporary overrides were restored. No mesh/weight/rig/rest/joint/roll/corrective/driver/mapping/smoothing edit, added/deleted corrective, model repair, fingertip work, R3, true-cap, hidden crossing, normal-dot, 2127-edge or full Stage6 run.

Files: FIRST_WEB_DEFECT_FRAME_SELECTION_R1.json; FIRST_WEB_CORRECTIVE_DRIVER_VALUES_R1.json; FIRST_WEB_DEFECT_ROTATION_COMPARISON_R1.json; MATCHED_AB_VERIFICATION_R1.json; FIRST_WEB_AB_VISUAL_PRECHECK_R1.json; review.html; 40 matched renders. All final fields are in PIANOVAM_FIRST_WEB_CORRECTIVE_AB_ISOLATION_R1_STATUS.json.

Human Q1: Does turning off the corrective visibly reduce the notch? **YES / NO — unanswered.**
Human Q2: In the worst defect frames, does corrective off restore acceptable appearance? **YES / NO — unanswered.**

PianoVAM motion retains its existing CC BY-NC-SA 4.0 / INTERNAL_NONCOMMERCIAL_VALIDATION_ONLY scope. No production promotion. STOP — HUMAN REVIEW; no automatic repair follows this classification.
