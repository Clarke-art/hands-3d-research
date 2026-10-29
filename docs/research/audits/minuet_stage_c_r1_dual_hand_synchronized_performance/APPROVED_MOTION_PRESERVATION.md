# Approved actual motion preservation

Original reference:930 right and829 left music-time samples, including all saved approved motion samples, every357 shared video frame, fractional NOTE_ON/OFF, approach/downstroke/hold/release probes. Actual root/rig matrices, every pose-bone basis/quaternion, evaluated skin, rigid finger-pad markers and corresponding actual skin-pad vertices are compared in the shared scene, before save and again after reopen. This is a trajectory-preservation check, not a forensic collision pass.

| Hand | Samples | Actual skin max error mm | Pad max error mm | Joint rotation max error deg | Key angle max error rad |
|---|---|---|---|---|---|
| R | 930 | 0.000365671922596 | 0.000202782525471 | 3.81819182083e-06 | 0 |
| L | 829 | 0 | 0 | 2.41483653945e-06 | 0 |

Only deterministic float32 origin conversion produces the tiny right-side numerical difference. Left coordinate/basis/skin comparisons are exact; the nonzero quaternion angle diagnostic is arccos floating-point resolution. No speed changes, smoothing, root or joint refit, new motion solver, changed fingering, per-note pose fix, or contact target change. Complete frozen topology/weights/rest/shape corrective geometry and driver structure retain their normalized signatures. Curves retain every keyframe value and interpolation. Four approved static posture SHA values remain identical. Existing single-hand engineering WARN are inherited.

Detailed results: APPROVED_MOTION_PARITY.json.
