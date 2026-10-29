# audits/minuet_stage_c_r2_local_finger_overlap_refinement

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> Q9：所有非目标关节、双root、左手、窗口外运动保持；无名指局部动作变化的自然度待Human复审。

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_c_r2_local_finger_overlap_refinement/FINAL_ANSWERS.md)

## 技术路线

> Q13：没有第二候选、第二次优化、参数改动或扩大求解；新运动求解0。

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_c_r2_local_finger_overlap_refinement/FINAL_ANSWERS.md)

> One strategy lock, no full planner, no optimizer required: the correction is closed-form and uses0 motion solver calls. No later amplitude/window tuning or second animated candidate is permitted. If actual time-continuous local checks/contact/visual review fail, FAIL_CLOSED.

出处：[MINIMAL_LOCAL_CORRECTION_DESIGN.md](../research/audits/minuet_stage_c_r2_local_finger_overlap_refinement/MINIMAL_LOCAL_CORRECTION_DESIGN.md)

## 测试结论

> Q6：一次锁定局部修正有明显改善，但仍是PARTIAL；未完成几何清零。

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_c_r2_local_finger_overlap_refinement/FINAL_ANSWERS.md)

> Q8：PASS，原键/指法保持，主动skin最大绝对间隙2.0460mm、横向错键0mm；C5指腹P90边缘余量6.4247mm。

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_c_r2_local_finger_overlap_refinement/FINAL_ANSWERS.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 原报告与关键代码

- [audits/minuet_stage_c_r2_local_finger_overlap_refinement/FINAL_ANSWERS.md](../research/audits/minuet_stage_c_r2_local_finger_overlap_refinement/FINAL_ANSWERS.md)
- [audits/minuet_stage_c_r2_local_finger_overlap_refinement/IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_c_r2_local_finger_overlap_refinement/IMPLEMENTATION_REPORT.md)
- [audits/minuet_stage_c_r2_local_finger_overlap_refinement/OVERLAP_IDENTITY_AND_CAUSE.md](../research/audits/minuet_stage_c_r2_local_finger_overlap_refinement/OVERLAP_IDENTITY_AND_CAUSE.md)
- [audits/minuet_stage_c_r2_local_finger_overlap_refinement/BEFORE_AFTER_OVERLAP_REVIEW.md](../research/audits/minuet_stage_c_r2_local_finger_overlap_refinement/BEFORE_AFTER_OVERLAP_REVIEW.md)
- [audits/minuet_stage_c_r2_local_finger_overlap_refinement/APPROVED_MOTION_PRESERVATION.md](../research/audits/minuet_stage_c_r2_local_finger_overlap_refinement/APPROVED_MOTION_PRESERVATION.md)
- [audits/minuet_stage_c_r2_local_finger_overlap_refinement/MINIMAL_LOCAL_CORRECTION_DESIGN.md](../research/audits/minuet_stage_c_r2_local_finger_overlap_refinement/MINIMAL_LOCAL_CORRECTION_DESIGN.md)
- [audits/minuet_stage_c_r2_local_finger_overlap_refinement/STRICT_CLEARANCE_GATE_AND_USER_SCOPE.md](../research/audits/minuet_stage_c_r2_local_finger_overlap_refinement/STRICT_CLEARANCE_GATE_AND_USER_SCOPE.md)
- [audits/minuet_stage_c_r2_local_finger_overlap_refinement/00_readonly_intake.py](../../src/legacy/audits/minuet_stage_c_r2_local_finger_overlap_refinement/00_readonly_intake.py)
- [audits/minuet_stage_c_r2_local_finger_overlap_refinement/01_readonly_overlap.py](../../src/legacy/audits/minuet_stage_c_r2_local_finger_overlap_refinement/01_readonly_overlap.py)
- [audits/minuet_stage_c_r2_local_finger_overlap_refinement/02_diagnostic_summary.py](../../src/legacy/audits/minuet_stage_c_r2_local_finger_overlap_refinement/02_diagnostic_summary.py)
- [audits/minuet_stage_c_r2_local_finger_overlap_refinement/03_static_feasibility.py](../../src/legacy/audits/minuet_stage_c_r2_local_finger_overlap_refinement/03_static_feasibility.py)
- [audits/minuet_stage_c_r2_local_finger_overlap_refinement/04_static_visual_check.py](../../src/legacy/audits/minuet_stage_c_r2_local_finger_overlap_refinement/04_static_visual_check.py)
- [audits/minuet_stage_c_r2_local_finger_overlap_refinement/05_lock_local_policy.py](../../src/legacy/audits/minuet_stage_c_r2_local_finger_overlap_refinement/05_lock_local_policy.py)
- [audits/minuet_stage_c_r2_local_finger_overlap_refinement/06_apply_validate.py](../../src/legacy/audits/minuet_stage_c_r2_local_finger_overlap_refinement/06_apply_validate.py)
- [audits/minuet_stage_c_r2_local_finger_overlap_refinement/07_local_domain_certificate.py](../../src/legacy/audits/minuet_stage_c_r2_local_finger_overlap_refinement/07_local_domain_certificate.py)
- [audits/minuet_stage_c_r2_local_finger_overlap_refinement/08_locked_residual_review.py](../../src/legacy/audits/minuet_stage_c_r2_local_finger_overlap_refinement/08_locked_residual_review.py)
- [audits/minuet_stage_c_r2_local_finger_overlap_refinement/09_commit_same_locked_motion.py](../../src/legacy/audits/minuet_stage_c_r2_local_finger_overlap_refinement/09_commit_same_locked_motion.py)
- [audits/minuet_stage_c_r2_local_finger_overlap_refinement/10_render_and_contact_cap.py](../../src/legacy/audits/minuet_stage_c_r2_local_finger_overlap_refinement/10_render_and_contact_cap.py)
- [audits/minuet_stage_c_r2_local_finger_overlap_refinement/11_media.py](../../src/legacy/audits/minuet_stage_c_r2_local_finger_overlap_refinement/11_media.py)

## 输入、输出与大型证据

该目录原始成员 186 项；拟公开身份记录 166 项。
- `audits/minuet_stage_c_r2_local_finger_overlap_refinement/BASELINE_REFERENCE.npz` → `hands-research-r1-selected-003.zip` / `payload/audits/minuet_stage_c_r2_local_finger_overlap_refinement/BASELINE_REFERENCE.npz`
- `audits/minuet_stage_c_r2_local_finger_overlap_refinement/STAGE_C_R2_LOCAL_FINGER_OVERLAP_DESIGN_ONLY.blend` → `hands-research-r1-selected-003.zip` / `payload/audits/minuet_stage_c_r2_local_finger_overlap_refinement/STAGE_C_R2_LOCAL_FINGER_OVERLAP_DESIGN_ONLY.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
