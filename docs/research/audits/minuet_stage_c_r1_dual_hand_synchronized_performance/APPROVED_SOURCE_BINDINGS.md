# Human-approved sources and protected ownership

Approval authority: the explicit user request MINUET_STAGE_C_R1_DUAL_HAND_SYNCHRONIZED_PERFORMANCE dated2026-10-10. Both named sources are HUMAN_VISUAL_APPROVED_WITH_ENGINEERING_WARN, covering their original single-hand performances only. Their older FINAL_STATUS files still say HUMAN_PENDING; these historical reports are preserved, not rewritten or falsely used as a newer approval receipt. Dual-hand Human approval remains pending.

R: `<HANDS_ROOT>\audits\minuet_stage_a_r2_natural_continuous_motion\STAGE_A_R2_COORDINATED_RIGHT_DESIGN_ONLY.blend`

Source SHA256 `e932b6ec47b0ee8822149cf232157d0a28e95b9878a91abdaca9bf8c62f48185`; scene `STAGE_A_R2_COORDINATED_RIGHT_ONLY`. Original root/rig/mesh mapping `{'root': 'STATIC_ROOT_R1.001', 'rig': 'RIGHT_HAND_PRODUCTION_RIG.002', 'mesh': 'RIGHT_HAND_OFFICIAL_L1_PRODUCT_MESH.002'}`. Numeric motion SHA256 `d162e68b1f2b4bb9ad679ce25a79190696400fee5487834c8f30b7f6dcca5a26`. Original timeline SHA256 `289b1a9fbdc4140aa652f2cd4e48878bfb8275fd14a281d8a763c5ea5a02cbe1`. Engineering diagnostics SHA256 `bc3122baf4a4d5cd8d2a90633b0af83d4deeeefe68dd3cf53872f25bca7c4872`.

L: `<HANDS_ROOT>\audits\minuet_stage_b_r3_budget_policy_candidate_recovery_r1\STAGE_B_R3_RECOVERED_CONTACT_DESIGN_ONLY.blend`

Source SHA256 `a4c51e660725335922916c179d65883146eb249848f95793c566d1e2d5ebfe63`; scene `STAGE_B_R3_DETERMINISTIC_RECOVERY_ONLY`. Original root/rig/mesh mapping `{'root': 'STATIC_ROOT_L1.001', 'rig': 'LEFT_HAND_PRODUCTION_RIG.002', 'mesh': 'LEFT_HAND_OFFICIAL_L1_MIRROR_PRODUCT_MESH.002'}`. Numeric motion SHA256 `4510dd2f72dd15ff08cb06953d0c845ef61e36c8119e2aa1d2920fe75b4df940`. Original timeline SHA256 `5f303a276916565d831ff427a92b00a9ea6b73a8c96d354e46003250b9f61731`. Engineering diagnostics SHA256 `7ee9a67ba31591fc37b0178f6581de2f41c4484321beee107e7b73ece346274a`.

| Hand | Owner | Original object | Actual source Action | Actual slot | Source Action payload SHA256 |
|---|---|---|---|---|---|
| R | root | STATIC_ROOT_R1.001 | DESIGN_ONLY_STAGE_A_R2_COORDINATED_ROOT | OBSTATIC_ROOT_R1.001 | 31b5160d4f9183162be86c14ba36aa1e9589badea5756c7eee71445307544637 |
| R | rig | RIGHT_HAND_PRODUCTION_RIG.002 | DESIGN_ONLY_STAGE_A_R2_COORDINATED_JOINTS | OBRIGHT_HAND_PRODUCTION_RIG.002 | 80fe4a3c7e12e30ad9e787b60edb4de23dfd5895f82f4b86a7a9f76d279af6e3 |
| R | 46 | STAGE_A_KEY_67 | STAGE_A_KEY_67Action | OBSTAGE_A_KEY_67 | 933d5b0857e07c12b1c4808a0a54fbe9fabcd97f9eac9574f323480b8b1d0eed |
| R | 48 | STAGE_A_KEY_69 | STAGE_A_KEY_69Action | OBSTAGE_A_KEY_69 | 52413666a5890086ef653f2c744b2fbbe9f31db3193bb8a3878d9d0b18bac3fe |
| R | 50 | STAGE_A_KEY_71 | STAGE_A_KEY_71Action | OBSTAGE_A_KEY_71 | 1bb1b550ae376203e7caccfdbca9004d43032ff966dbcb464b6d26404ba27f1c |
| R | 51 | STAGE_A_KEY_72 | STAGE_A_KEY_72Action | OBSTAGE_A_KEY_72 | 4bcbe1d3fa0ac453b1ea51905fe09b4db12981360da2b8a2871dee84c95e66d5 |
| R | 53 | STAGE_A_KEY_74 | STAGE_A_KEY_74Action | OBSTAGE_A_KEY_74 | b2ab1ad4fb3f3656326d65695f43c1defef38461fe5511d8dc9f54d1733682bf |
| R | 55 | STAGE_A_KEY_76 | STAGE_A_KEY_76Action | OBSTAGE_A_KEY_76 | 0d8affe88780ace40ade70d65107251132f302507474051a390036c1f1d90b45 |
| R | 57 | STAGE_A_KEY_78 | STAGE_A_KEY_78Action | OBSTAGE_A_KEY_78 | d3a37eec00fd267a3117572745a93f97371eead07fcbee10ebc6fe3c69fbb2e9 |
| R | 58 | STAGE_A_KEY_79 | STAGE_A_KEY_79Action | OBSTAGE_A_KEY_79 | 2359c5137c0567c5196c90b47c1a99809b634704e7e964a096d143c7b247ffa0 |
| L | root | STATIC_ROOT_L1.001 | DESIGN_ONLY_STAGE_B_R2_LEFT_CONTINUOUS_ROOT | OBSTATIC_ROOT_L1.001 | 3a7ad1b3ef956af2244db797e8a59ffbd7b0083b666cc236ea0cd6c5dd6238e3 |
| L | rig | LEFT_HAND_PRODUCTION_RIG.002 | DESIGN_ONLY_STAGE_B_R3_SAVED_TRAJECTORY_RECOVERY_JOINTS | OBLEFT_HAND_PRODUCTION_RIG.002 | de5742baaba2dd809811bfd3849ecd387e06edff744ebecc8a3c275aebfc7942 |
| L | 34 | STAGE_A_KEY_55 | STAGE_A_KEY_55Action | OBSTAGE_A_KEY_55 | e6d550afeb94dc3019c2ea061b34710391e318167f9c5246a4e81d5d19807c78 |
| L | 36 | STAGE_A_KEY_57 | STAGE_A_KEY_57Action | OBSTAGE_A_KEY_57 | 0af852188f9d7e85ca4dbe2fb59eb1cf212d4f3d20376d27792c50d458f732dd |
| L | 38 | STAGE_A_KEY_59 | STAGE_A_KEY_59Action | OBSTAGE_A_KEY_59 | f45218be834ad220fbb84996e423b4ef6466ae7f5ea9c78efe88107d5f621dc4 |
| L | 39 | STAGE_A_KEY_60 | STAGE_A_KEY_60Action | OBSTAGE_A_KEY_60 | b97828eaf2dfa8a1b28259d3c3249bb162e4407d592a6b95730a54d76e6ce4d8 |
| L | 41 | STAGE_A_KEY_62 | STAGE_A_KEY_62Action | OBSTAGE_A_KEY_62 | e6d550afeb94dc3019c2ea061b34710391e318167f9c5246a4e81d5d19807c78 |

Actual FK, root motion, joint quaternion curves, key curves, corrective bindings and audio source event relationships were read from these exact saved Blends and approved data. Neither a failed original R3 nor older R1 was substituted. Original Grand sample chain is linked in AUDIO_INTEGRATION.json; source audio/timeline/data files are protected in the full snapshot. All9546 current protected files, including the entire approved source audit directories and frozen input union, match the pre-work SHA snapshot. The four approved static scene core SHA values match both approved scene manifests. No frozen geometry/Rig/weights/Actions on disk were modified.
