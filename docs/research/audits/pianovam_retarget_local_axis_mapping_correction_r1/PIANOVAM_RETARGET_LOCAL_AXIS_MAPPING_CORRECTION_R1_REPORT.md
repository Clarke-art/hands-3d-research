# PIANOVAM_RETARGET_LOCAL_AXIS_MAPPING_CORRECTION_R1

**PRIMARY_CAUSE_CLASSIFICATION = RETARGET_AXIS_MAPPING_PARTIAL_CAUSE. STOP — HUMAN REVIEW.** Second mapping iteration significantly reduces the selected first-web triangular inward folds and makes the hinge chains more coherent, but residual creases and fast fingertip bends remain. Product validation is not accepted automatically.

## What the coordinate audit found

The source is the original video-verified physical right (`Left` JSON field), frames690–1110, exactly421 observations /11.5–18.5s. Native normalized image x/y/z are aspect-corrected (y×1080/1920) and are not metric world points. Radial X comes from index-MCP minus little-MCP; distal Y from wrist to middle-MCP; Z=X×Y. Determinants stay approximately1 (0.99999982..1.00000024). Normal, radial and distal sign flips are all0. Raw normal steps reach23.597deg: stable handedness is not a claim of noise-free depth/orientation. No new smoothing hides a basis flip.

Rig object matrix_world is identity; mesh world transform is nonidentity and preserved. Each actual frozen bone's rest matrix, parent-relative rest matrix, local XYZ axes, primary Y, inherited rotation/scale semantics and palm-local direction are recorded. Native Blender convert_local_to_pose checks agree within1.8e-7. **No reversed palm handedness or parent/local matrix-order bug was established.** Old positive INDEX local Euler X was not sufficient proof of a sign mistake: its frozen rest phalanx already has17.964deg palmar elevation and11.777deg splay. Absolute source phalanx alignment with less elevation unfolds that rest bend, yielding a positive local delta. Prior stress fixtures are not ROM and are never used by the new solver.

## What mapping changed

Four-finger MCPs use a palm-radial anchored anatomical frame plus MCP→PIP direction. Source neutral-palm flexion and abduction map through the rig's frozen rest-anatomical frame, with the rest-roll offset retained. This is a **rest-space component calibration**, not copying every source segment's absolute orientation. Intrinsic RSSF rest curvature/splay are retained, so the calibrated rig's absolute bend need not equal the camera-space landmark bend. The calibrated neutral reference is explicitly documented; it is not asserted to be a measured anatomical neutral pose.

PIP/DIP use signed consecutive-segment bends about a stable digit-plane hinge, expressed in each actual bone's rest-local axes. Off-plane residuals are diagnostic data; no unknown axial twist is copied. Thus no direct +X→−X edit, -45deg clamp, blanket Z-channel deletion, or Stage6 pose forcing is applied. Quaternion/matrix/vector computations are primary; Euler is not a solver.

Thumb CMC is separate: a palm-normal anchored thumb-base frame and CMC→MCP direction, with MCP→IP plane diagnostics. No noisy thumb-plane axial twist is copied; rest roll remains calibrated. Thumb MCP/IP use their own anchored hinge plane and calibrated local axes. Iteration1's wrist→CMC structural neutral reference over-adducted the thumb and failed its dry-run screen. Iteration2 uses the median normalized CMC→MCP stance from the **same421-observation window** as source-rest calibration. It changes no source coordinates, time window or angle limit. This estimated stance-to-RSSF calibration should be reviewed as a retarget convention, not an anatomical assertion.

## Dry run before full Action

Each iteration first mapped only the10 existing selected frames and their unchanged3-tap neighbors (30 source observations), and rendered OLD/NEW with identical cameras in palmar/thenar close, first-web oblique and full dorsal views. No full421-frame Action was produced for iteration1. Iteration2 significantly reduces the large sharp web wedges, with residual creases, and improves finger-chain coherence. DEFECT_FRAME_OLD_VS_CORRECTED_R1.json contains the4重点骨 old/new quaternions, source flexion/abduction or hinge bend, actual rest-local axes and parent conversion checks. After this PROMISING gate, the full Action was created. Mapping iteration count=2; no further tuning follows.

## Full seven-second result and limits

The new independent `PIANOVAM_PHYSICAL_RIGHT_AXIS_CORRECTED_R1` Action preserves the old raw and smoothed Actions exactly in the independent test .blend. All421 source observations have quaternion keys at half-frame positions1..211 in a30fps scene. A raw corrected Action is also preserved. Review videos are210 frames/7.000s and re-render OLD/NEW using the same cameras. Smoothing remains exactly [.25,.5,.25] at source60fps with sign alignment/normalization, zero phase and33.3ms neighbor support. No larger window or extra filtering was used.

Machine checks: NaN/Inf0; quaternion sign discontinuity0; >90deg consecutive world-direction flips0; >90deg local-quaternion catastrophic step frames0; ZERO restorePASS with0mm maximum evaluated-vertex error. Maximum local quaternion step remains54.698deg per source observation: the numeric catastrophic threshold does not establish smooth or natural playing. Ordinary solid precheck found no gross whole-hand collapse/open tearing, but local web creases and fast bends remain unqualified. Thenar/palm broad volume is retained in the two views. Preliminary classification is **partial cause**, not full cause or motion approval.

The first-web key and driver are unchanged and never overridden. Natural corrected Action activation ranges0..0.0406101. Mesh/Basis/weights/rig rest/joints/roll/hierarchy/UV/materials/corrective/driver payloads compare exactly after save/reopen. Detaching the Action and resetting all pose transforms restores the frozen ZERO mesh exactly. Both previous Actions' keyframe payloads are unchanged. Source, old .blend and frozen baseline hashes remain unchanged.

No new sample/download, left-hand work, Web export, mesh/weight/corrective/driver/rig repair, R3/true-cap/hidden-crossing/2127-edge/normal-dot/full Stage6 audit was performed. PianoVAM scope remains CC BY-NC-SA4.0 / INTERNAL_NONCOMMERCIAL_VALIDATION_ONLY; PRODUCTION_PROMOTION=NO.

## Human review

Q1. Has the obvious first-web notch disappeared or reached acceptable appearance? YES/NO — unanswered.
Q2. Are fingers/fingertips more natural than the old retarget? YES/NO — unanswered.
Q3. Is the complete7s real piano motion acceptable for product validation? ACCEPT/REJECT — unanswered.

Review page: review.html. Primary matched palmar movie: review_axis_corrected.mp4; matched dorsal movie: review_axis_corrected_dorsal.mp4. All final fields: PIANOVAM_RETARGET_LOCAL_AXIS_MAPPING_CORRECTION_R1_STATUS.json. Coordinate audit, bone-axis mapping, dry-run old/new records and Action preservation/continuity are separate JSON evidence files. **STOP — HUMAN REVIEW.**

Baseline SHA256: `4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2`
Old retarget SHA256: `43e8e2854aa24c74053830118ea6d939fc56af4efb450bf0098a7bd99838dae8`
New test: `audits/pianovam_retarget_local_axis_mapping_correction_r1/RIGHT_HAND_PIANO_AXIS_CORRECTED_TEST_R1.blend`
New test SHA256: `a5190adc13d39318096490f8fd2c9956d0daff457d25753fa3c216eee2027bbd`
