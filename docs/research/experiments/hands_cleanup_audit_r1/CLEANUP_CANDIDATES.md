# 目录级清理候选 R1

**STOP — HUMAN REVIEW。全部均为建议，本轮实际释放0。**

| 方案 | 释放GiB | 释放GB | 剩余GiB | 剩余GB |
| --- | --- | --- | --- | --- |
| 保守 | 6.039 | 6.484 | 16.973 | 18.225 |
| 深度（包含保守） | 12.618 | 13.549 | 10.394 | 11.160 |

两档均不含 HUMAN_REVIEW，不重复加总重复文件。保守主要清除已完成编码的早期渲染缓存、可解码的before_frames及有源码的Python缓存；深度追加当前/批准候选的非必要无损帧，保留全部Blend、NPZ、MIDI、音频、视频、代码、配置、静态姿态、关键报告及审核网页所需文件。清理后重跑旧媒体脚本时应先重建缓存；原始源代码和数值功能保持。此处“安全”指有效功能/资产及审核入口仍保留，不能承诺旧全文件冻结验证脚本原封不动PASS。

原始SHA清单不修改；后续执行必须另加明确的已批准删除例外账本，避免把故意清理报告成异常丢失。

## 保守方案精确候选

| ID | 完整路径 | GiB | 操作范围 | 依据/风险 |
| --- | --- | --- | --- | --- |
| DELETE_CANDIDATE-0325 | <HANDS_ROOT>\audits\minuet_stage_b_r2_left_hand_continuous_accompaniment\_frames | 1.433 | directory | 已编码完成的连续 PNG 渲染/解码中间序列；保留视频、场景/运动输入、脚本、审核图和所有静态 HTML 引用。 风险:MEDIUM |
| DELETE_CANDIDATE-0332 | <HANDS_ROOT>\audits\minuet_target_key_hand_position_planning_r1\_frames | 1.065 | directory | 已编码完成的连续 PNG 渲染/解码中间序列；保留视频、场景/运动输入、脚本、审核图和所有静态 HTML 引用。 风险:MEDIUM |
| DELETE_CANDIDATE-0333 | <HANDS_ROOT>\audits\minuet_stage_c_r2_local_finger_overlap_refinement\before_frames | 0.557 | directory | 由保留的 before_normal_speed_*.mp4 解码得到的中间 PNG；11_media.py 中明确 ffmpeg 解码命令。 风险:LOW |
| DELETE_CANDIDATE-0334 | <HANDS_ROOT>\audits\piano_keyboard_low_dof_root_pose_validation_r1\_render_frames | 0.550 | directory | 已编码完成的连续 PNG 渲染/解码中间序列；保留视频、场景/运动输入、脚本、审核图和所有静态 HTML 引用。 风险:MEDIUM |
| DELETE_CANDIDATE-0335 | <HANDS_ROOT>\audits\right_hand_first_web_product_impact_go_no_go_r1\product_views | 0.505 | directory | 已编码完成的连续 PNG 渲染/解码中间序列；保留视频、场景/运动输入、脚本、审核图和所有静态 HTML 引用。 风险:MEDIUM |
| DELETE_CANDIDATE-0338 | <HANDS_ROOT>\audits\piano_keyboard_spatial_anchor_and_contact_validation_r1\_render_frames | 0.405 | directory | 已编码完成的连续 PNG 渲染/解码中间序列；保留视频、场景/运动输入、脚本、审核图和所有静态 HTML 引用。 风险:MEDIUM |
| DELETE_CANDIDATE-0339 | <HANDS_ROOT>\audits\pianovam_retarget_local_axis_mapping_correction_r1\full_motion_frames | 0.324 | directory | 已编码完成的连续 PNG 渲染/解码中间序列；保留视频、场景/运动输入、脚本、审核图和所有静态 HTML 引用。 风险:MEDIUM |
| DELETE_CANDIDATE-0340 | <HANDS_ROOT>\audits\minuet_stage_b_r1_left_hand_triad_coordination\_frames | 0.299 | directory | 已编码完成的连续 PNG 渲染/解码中间序列；保留视频、场景/运动输入、脚本、审核图和所有静态 HTML 引用。 风险:MEDIUM |
| DELETE_CANDIDATE-0341 | <HANDS_ROOT>\audits\dual_hand_synchronized_real_motion_validation_r1\_render_frames | 0.281 | directory | 已编码完成的连续 PNG 渲染/解码中间序列；保留视频、场景/运动输入、脚本、审核图和所有静态 HTML 引用。 风险:MEDIUM |
| DELETE_CANDIDATE-0345 | <HANDS_ROOT>\audits\left_hand_real_motion_retarget_validation_r1\_render_frames | 0.221 | directory | 已编码完成的连续 PNG 渲染/解码中间序列；保留视频、场景/运动输入、脚本、审核图和所有静态 HTML 引用。 风险:MEDIUM |
| DELETE_CANDIDATE-0350 | <HANDS_ROOT>\audits\first_web_real_motion_deformation_fix_r1\final_motion | 0.165 | directory | 已编码完成的连续 PNG 渲染/解码中间序列；保留视频、场景/运动输入、脚本、审核图和所有静态 HTML 引用。 风险:MEDIUM |
| DELETE_CANDIDATE-0351 | <HANDS_ROOT>\audits\first_web_real_motion_deformation_fix_r1\before_motion | 0.165 | directory | 已编码完成的连续 PNG 渲染/解码中间序列；保留视频、场景/运动输入、脚本、审核图和所有静态 HTML 引用。 风险:MEDIUM |
| DELETE_CANDIDATE-0324 | <HANDS_ROOT>\audits\official_l1_first_web_targeted_deformation_fix_r1\RIGHT_HAND_OFFICIAL_L1_FIRST_WEB_TUNED_DESIGN_ONLY_R1.blend1 | 0.001 | file | 完整 SHA-256 与保留的 .blend 完全相同的 Blender 备份。 风险:LOW |
| DELETE_CANDIDATE-0323 | <HANDS_ROOT>\audits\official_l1_product_rebase_feasibility_r1\RIGHT_HAND_OFFICIAL_L1_PRODUCT_REBASE_CANDIDATE_R1.blend1 | 0.001 | file | 完整 SHA-256 与保留的 .blend 完全相同的 Blender 备份。 风险:LOW |

## 深度方案追加候选

| ID | 完整路径 | GiB | 操作范围 | 依据/风险 |
| --- | --- | --- | --- | --- |
| DELETE_CANDIDATE-0328 | <HANDS_ROOT>\audits\minuet_stage_c_r2_local_finger_overlap_refinement\_frames | 1.134 | directory | 已编码完成的连续 PNG 渲染/解码中间序列；保留视频、场景/运动输入、脚本、审核图和所有静态 HTML 引用。 风险:MEDIUM |
| DELETE_CANDIDATE-0329 | <HANDS_ROOT>\audits\minuet_stage_c_r1_dual_hand_synchronized_performance\_frames | 1.131 | directory_members_except_keep | 已编码完成的连续 PNG 渲染/解码中间序列；保留视频、场景/运动输入、脚本、审核图和所有静态 HTML 引用。 风险:MEDIUM |
| DELETE_CANDIDATE-0330 | <HANDS_ROOT>\audits\minuet_stage_b_r3_budget_policy_candidate_recovery_r1\_frames | 1.070 | directory | 已编码完成的连续 PNG 渲染/解码中间序列；保留视频、场景/运动输入、脚本、审核图和所有静态 HTML 引用。 风险:MEDIUM |
| DELETE_CANDIDATE-0331 | <HANDS_ROOT>\audits\minuet_stage_a_r2_natural_continuous_motion\_frames | 1.066 | directory | 已编码完成的连续 PNG 渲染/解码中间序列；保留视频、场景/运动输入、脚本、审核图和所有静态 HTML 引用。 风险:MEDIUM |
| DELETE_CANDIDATE-0336 | <HANDS_ROOT>\audits\piano_hand_visual_first_short_phrase_validation_r1\_frames | 0.475 | directory | 已编码完成的连续 PNG 渲染/解码中间序列；保留视频、场景/运动输入、脚本、审核图和所有静态 HTML 引用。 风险:MEDIUM |
| DELETE_CANDIDATE-0337 | <HANDS_ROOT>\audits\right_hand_articulation_contact_short_phrase_r1\_frames | 0.475 | directory | 已编码完成的连续 PNG 渲染/解码中间序列；保留视频、场景/运动输入、脚本、审核图和所有静态 HTML 引用。 风险:MEDIUM |
| DELETE_CANDIDATE-0342 | <HANDS_ROOT>\audits\minuet_stage_c_r2_local_finger_overlap_refinement\diagnostic_frames | 0.247 | directory | 诊断 PNG 子集与 before_frames 完整 SHA-256 重复；保留原视频可重新解码。 风险:MEDIUM |
| DELETE_CANDIDATE-0343 | <HANDS_ROOT>\audits\midi_driven_hand_posture_and_contact_refinement_r1\_frames | 0.240 | directory | 已编码完成的连续 PNG 渲染/解码中间序列；保留视频、场景/运动输入、脚本、审核图和所有静态 HTML 引用。 风险:MEDIUM |
| DELETE_CANDIDATE-0344 | <HANDS_ROOT>\audits\midi_driven_dual_hand_piano_performance_poc_r1\_frames | 0.239 | directory | 已编码完成的连续 PNG 渲染/解码中间序列；保留视频、场景/运动输入、脚本、审核图和所有静态 HTML 引用。 风险:MEDIUM |
| DELETE_CANDIDATE-0346 | <HANDS_ROOT>\audits\piano_hand_static_to_dynamic_transition_r1\_frames | 0.221 | directory | 已编码完成的连续 PNG 渲染/解码中间序列；保留视频、场景/运动输入、脚本、审核图和所有静态 HTML 引用。 风险:MEDIUM |
| DELETE_CANDIDATE-0355 | <HANDS_ROOT>\audits\left_octave_root_finger_coordinated_clearance_r1\_frames | 0.142 | directory | 已编码完成的连续 PNG 渲染/解码中间序列；保留视频、场景/运动输入、脚本、审核图和所有静态 HTML 引用。 风险:MEDIUM |
| DELETE_CANDIDATE-0356 | <HANDS_ROOT>\audits\left_little_finger_moving_key_reachability_r1\_frames | 0.142 | directory | 已编码完成的连续 PNG 渲染/解码中间序列；保留视频、场景/运动输入、脚本、审核图和所有静态 HTML 引用。 风险:MEDIUM |

## 缓存汇总

313 个可整目录删除的 __pycache__，共 0.067 GiB。每个pyc的对应.py都已逐一确认存在；完整路径、文件ID、时间、大小和源码路径均在manifest中，不以通配符清理。不能证明有.py的缓存保留。

## 可以整包删除什么

可整目录删除的是上表精确列出的 `_frames`、`_render_frames`、before/诊断/运动帧缓存包，以及符合源码条件的 __pycache__。Stage C R1 `_frames` 有两张静态审核poster例外，必须按成员清单删除其余图片，不能递归删整个目录。

**本轮未批准任何完整 audits/任务根目录删除。** 大目录仍有唯一脚本、原始运动或实际下游引用；删渲染子包已经得到主要空间收益，不必冒险删任务骨架。所有任务逐项结论在 TASK_ASSESSMENTS.json；源码/依赖不会因 FAIL_CLOSED 自动变成垃圾。

典型阻碍：B2 → B3原始求解/guard fix → B3 recovery → C1；A2和B3 recovery是已获Human视觉批准的单手源；C1 → C2 → R3/R6 → lightweight → pedagogical。MIDI POC 的performance_core和_deps被48份跨任务代码命中。

## 恢复和执行条件

`before_frames` 是ffmpeg解码缓存，原视频仍在；普通渲染PNG需用原场景/Action、原相机、原Blender版本重新渲染，可能耗时，且字节级渲染再现不保证。解码有损视频不能恢复原始无损PNG。审核图/静态src和动态滑块引用另行保留。未来执行前还必须检查有效渲染脚本的实际输入和运行环境；无需重新运行重型求解。

CLEANUP_MANIFEST.json中的每项包含成员绝对路径、bytes、mtime_ns、device/fileID/nlink、可用SHA、风险、保留输入和证据。`preflight_readonly.py --plan conservative|deep` 只做核对，无删除功能。不能把目录本次大小当作以后无限递归删除授权。
