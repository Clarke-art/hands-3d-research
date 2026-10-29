# CONTACT_GUIDED_LIGHTWEIGHT_ANIMATION — locked single attempt

C1 is the natural performance master. Root, left hand, thumb, little finger, keys, MIDI, audio and cameras remain unchanged. Only a copied right-hand joint Action may differ, for INDEX/MIDDLE/RING.

At 30 Hz, use the original engineering joint coordinates and the previous legal local correction as seed. Three deterministic coordinate-probe sweeps (2°, 1°, 0.5°) examine positive/negative MCP, PIP, DIP and spread adjustments. Bounds are the original engineering limits intersected with ±5°, ±7°, ±5°, ±5° of the source. No random seeds, scipy optimizer, whole-phrase constraint solve or alternative candidate selection.

Costs use sampled actual skinned digit surfaces against neighboring digit convex envelopes and real nearby raised black-key bodies. Movement direction follows the measured geometry; raising is not prescribed. Source-pose and previous-correction costs resist claws, exaggerated spread and jitter. A convex envelope is deliberately only a local guidance proxy; final before/after checks use actual Blender skin and triangle intersections.

An event-derived quintic envelope is zero during every active note and a 25 ms contact guard, with 160 ms approach/recovery ramps. Active joint animation stays at the C1 source. Preparing digits smoothly return to their next original target; releasing digits begin avoidance only after the contact guard. Idle digits retain the source curvature plus bounded correction. Two-frame Gaussian smoothing followed by the same contact envelope produces a single continuous correction field. This is one locked processing pass, not another fit.

Bake the correction onto actual C1 quaternion samples at 120 Hz plus original keyframes and exact note boundaries. Preserve every non-target curve. Reopen the sole derived Blend; measure active pads, original engineering limits, motion continuity, root/left/key parity and actual localized spatial changes. Basic engineering/music failure blocks video. Residual visible intersections permit DIAGNOSTIC_ONLY / NOT_APPROVED evidence, with FAIL_CLOSED.

Generation is guarded at 600 seconds. Rendering and verification are separate. No per-note poses, pitch-specific rotation constants, new rig, camera changes, or fallback to R6. Nearby black-key selection and roles come from the original note data. Generalization to other music remains untested.
