# 必须保留的资产与依赖 R1

只保留本轮建议中的有效功能和必要证据；历史目录含缓存不等于整个目录永久冻结。文件级范围见 FILE_CLASSIFICATIONS.jsonl。

## 正式/明确批准资产：实测SHA全部匹配

| 完整路径 | 角色 | SHA-256 | 校验 |
| --- | --- | --- | --- |
| <HANDS_ROOT>\production_spec\right_hand_product_baseline_r2\RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R2.blend | HUMAN_APPROVED_FROZEN | c946fed318fa88c238d9aacc30cfb4e52f268848f0ad65a4dcbf594754d791f0 | PASS |
| <HANDS_ROOT>\production_spec\right_hand_product_baseline_r1\RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1.blend | HISTORICAL_FROZEN_FALLBACK | 4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2 | PASS |
| <HANDS_ROOT>\production_spec\left_hand_product_baseline_r1\LEFT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1.blend | HUMAN_APPROVED_FROZEN | 54307bb199a75a5e684c29d346de9ca6bf2f8e7696911d9d69c57559516ad1a7 | PASS |
| <HANDS_ROOT>\audits\piano_hand_static_posture_clearance_refinement_r2\STATIC_POSTURE_REFINED_CANDIDATE_R2.blend | FOUR_HUMAN_APPROVED_STATIC_SCENES_STATIC_L1_STATIC_L2_STATIC_R1_STATIC_R2 | 18359b1c2c6e8abaa1a4444f342e7672a1f1fda35d96cc95146bc8d1161b551c | PASS |
| <HANDS_ROOT>\audits\minuet_stage_a_r2_natural_continuous_motion\STAGE_A_R2_COORDINATED_RIGHT_DESIGN_ONLY.blend | HUMAN_VISUAL_APPROVED_WITH_ENGINEERING_WARN | e932b6ec47b0ee8822149cf232157d0a28e95b9878a91abdaca9bf8c62f48185 | PASS |
| <HANDS_ROOT>\audits\minuet_stage_b_r3_budget_policy_candidate_recovery_r1\STAGE_B_R3_RECOVERED_CONTACT_DESIGN_ONLY.blend | HUMAN_VISUAL_APPROVED_WITH_ENGINEERING_WARN | a4c51e660725335922916c179d65883146eb249848f95793c566d1e2d5ebfe63 | PASS |

四个批准的静态姿态位于同一 STATIC_POSTURE_REFINED_CANDIDATE_R2.blend 的 STATIC_L1 / STATIC_L2 / STATIC_R1 / STATIC_R2，不是四个独立Blend。保留其整个R2静态任务、R1原始静态对照、SOLVED_STATIC_POSES_R2、STATIC_REFINEMENT_POLICY_R2、STATIC_SCENE_MANIFEST_R2、审核证据和 STATIC_ANCHOR_IDENTITY_R1 的Human授权绑定。旧状态HUMAN_PENDING由后续明确Human记录补充，不能据旧status当废弃。

## 当前研发核心保护范围

- production_spec/right_hand_product_baseline_r2、left_hand_product_baseline_r1、right_hand_product_baseline_r1及两个生产指针JSON；Mesh、21骨Rig、16 deform骨、5 TIP、权重、材质、corrective/driver及必要配置均随Blend原样保留。
- 全部90个.blend、全部98个.npz、所有.py/.js/.cjs/.mjs/.ps1、配置、MIDI、WAV、MP4和资源许可证，本轮无删除建议。失败候选Blend保留少量可复现源，外围数百MB/GB渲染可清理。
- audits/midi_driven_dual_hand_piano_performance_poc_r1/performance_core.py及完整_deps（仅有源码可再生成的__pycache__列为候选）；原MIDI/Performance Timeline、键表、指腹接触markers、FK/键几何、采样声音/音频同步接口。
- A2右手批准源、B3 recovery左手批准源、C1双手合成、C2局部候选、R3/R4/R5/R6/whole_phrase、lightweight和pedagogical源码/NPZ/真实skin/求解检查点/事件窗口政策，保持失败对照与后续改进能力。
- .workbuddy全部Human决定/记忆/归档、docs、reference_manifest、references和许可；历史冻结/哈希/审批原文件、关键最终状态、研究结论均不删除。
- first-web full static probe、production qualification、两手promotion、ownership/cap/proximal authority freeze及其被引用输入均保留。production_spec旧Stage5/6的失败实验不视为正式生产冻结；但旧Rig/权重权威、唯一源和技术对照仍需保留。

## 真实依赖证据举例

| 消费者 | 保留输入 | 原因 |
| --- | --- | --- |
| minuet_stage_c_r6_whole_phrase_spatial_planning/common.py | C1/PERFORMANCE_TIMELINE.json；R5；MIDI POC/_deps | 明确read与sys.path引入 |
| piano_hand_static_to_dynamic_transition_r1/common.py、00_lock.py | STATIC_POSTURE_REFINED_CANDIDATE_R2.blend、SOLVED_STATIC_POSES_R2.json、MIDI POC/performance_core | 四姿态继承和唯一MIDI/FK接口 |
| minuet_stage_c_r1_dual_hand_synchronized_performance/APPROVED_SOURCE_BINDINGS.md | A2 .blend；B3 recovery .blend及timeline/numericmotion | 明确后续Human批准来源与SHA |
| minuet_stage_c_lightweight_animation_poc_r1/render.py | C2/blender_local.py；C1/SCENE_MANIFEST；R3/LOCAL_SKIN_ROI.json | 实际渲染/验证链跨历史任务 |
| piano_pedagogical_motion_refinement_r1/HUMAN_REVIEW.html | 本任务_frames与lightweight/_frames | 动态PNG地址滑块；整包HUMAN_REVIEW |
| piano_pedagogical_demonstration_audit_r1/HUMAN_REVIEW.html | lightweight/_frames | 动态frameURL而非静态src；不能仅凭HTML属性检查 |
| palmar_root_targeted_visual_deformation_r1/run_and_render.py | 历史POSED_COORDINATES_R1.json | 后续几何/形变基线 |

## 保留但不冒称已完全验证

源码静态索引包含文件名与目录名命中；同名文件的命中需回到完整路径核对。动态import、f-string路径、Blend内部外链和外部工作区调用未执行全量运行时验证；因此全部Blend和数值运动保留，大型JSON/临时包列HUMAN_REVIEW，不据“未搜到引用”判可删。外部D:/Blender/blender.exe与D:/ffmpeg/bin/ffmpeg.exe存在；版本可复现环境（尤其C1的4.5.9）仍需未来执行前确认，未启动任何程序。
