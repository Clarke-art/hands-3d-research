# One real dual-hand scene

Candidate: `<HANDS_ROOT>\audits\minuet_stage_c_r1_dual_hand_synchronized_performance\STAGE_C_R1_DUAL_HAND_SYNCHRONIZED_DESIGN_ONLY.blend`. SHA256 `d8e0f5a85e71323739bfcd4de485ff7a2b4096f8e59bbd4c578ee9d76d3e51a7`. Scene `STAGE_C_R1_DUAL_HAND_SYNCHRONIZED_DESIGN_ONLY`. Exactly one saved dual-hand candidate; source files never saved or changed.

Pre-generation checks read each approved Blender scene, actual FK/quaternion/skin, root hierarchy, key Actions, source MIDI and audio chain. All88 neutral key world coordinates were identical between sources (maximum difference 0mm). Both matched the frozen Grand table. Hand coordinate transform is identity; roots remain in their approved world trajectories. No hand repositioning.

The right performance scene supplies one complete frozen keyboard mesh set. Only the approved left root, rig, mesh and five key pivots were appended. The left armature modifier and all corrective drivers point to the actual appended left rig. There are exactly two linked hand armatures and one88-key mesh set in the performance scene; four static reference scenes remain unchanged inside the file.

Right active keys:67,69,71,72,74,76,78,79. Left active keys:55,57,59,60,62. No shared key conflict or cross-channel key overwrite. Each of13 active keys has one pivot/Action owner. Existing right G4 reset/repress and left three-key chord curves are copied unchanged.

Shared presentation lead0.35s. Right Action keyframe and handle times shift+3frames; left shift0. Every actual keyframe value, LINEAR interpolation, scale1 and ownership remains unchanged. Root/joint/key trajectory parity is checked before save and after reopen. Original frame ranges need not be byte-identical; original music-time movement is preserved. First0.05s of the unified preparation uses the original right Action’s constant extrapolation. Extra non-musical tail uses its original constant extrapolation; musical motion is never stretched.

One packed Grand WAV strip starts at frame1 and includes the common preparation lead. All delivered views render this same scene and mux this same WAV; there is no independent-hand video overlay.

Full object names, Action names, source payload hashes, slots, copied-curve float32 timing roundoff and cameras: SCENE_MANIFEST.json and READONLY_PREFLIGHT.json.
