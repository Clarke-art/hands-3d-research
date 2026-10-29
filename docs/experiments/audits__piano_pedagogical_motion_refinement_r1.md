# audits/piano_pedagogical_motion_refinement_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 5. Q5：实际目标接触范围保持，未见新增明显悬空/错键；但两处NOTE_OFF的0.25mm源保持门限失败，最大0.283404mm，不能声称主动指绝对不变。

出处：[FINAL_ANSWERS.md](../research/audits/piano_pedagogical_motion_refinement_r1/FINAL_ANSWERS.md)

> 严格指腹源保持门限在R03 NOTE_OFF与R11 NOTE_OFF失败，分别0.258821mm和0.283404mm；实际触键没有越出目标面，接触间隙仍在母版范围。保持该失败记录，不通过自动改阈值放行。

出处：[BEFORE_AFTER_TEACHING_REVIEW.md](../research/audits/piano_pedagogical_motion_refinement_r1/BEFORE_AFTER_TEACHING_REVIEW.md)

## 技术路线

> 11. Q11：是；重型求解0、IK优化0、无逐音符人工姿态补丁；有限局部坐标探测仅在唯一正式尝试内执行。

出处：[FINAL_ANSWERS.md](../research/audits/piano_pedagogical_motion_refinement_r1/FINAL_ANSWERS.md)

> 直接复用上一轮23音符映射、左手资格、事件与教学问题；不重新求解全段双手。

出处：[PEDAGOGICAL_REPAIR_SCOPE.md](../research/audits/piano_pedagogical_motion_refinement_r1/PEDAGOGICAL_REPAIR_SCOPE.md)

## 测试结论

> 15. Q15：可提交Human观看真实修复结果及慢放对照，但只作DIAGNOSTIC_ONLY / NOT_APPROVED。最终FAIL_CLOSED，不能提交为已满足所有门禁的正式教学候选。

出处：[FINAL_ANSWERS.md](../research/audits/piano_pedagogical_motion_refinement_r1/FINAL_ANSWERS.md)

> 最大修正约7.98°，新增采样角速度峰值153.75°/s；工程角域通过。严格主动指腹保持门限0.25mm在两处NOTE_OFF边界失败，最大0.283404mm。该门限未放宽，未重新烘焙、未改参数再求解。结果保持FAIL_CLOSED。

出处：[LIGHTWEIGHT_MOTION_REPAIR.md](../research/audits/piano_pedagogical_motion_refinement_r1/LIGHTWEIGHT_MOTION_REPAIR.md)

## 失败原因与证据边界

> |B03 中指/D♯5 4.050s|5.469→2.938mm|嵌入残余仍会影响指尖路径理解|IMPROVED，仍有阻断风险|

出处：[BEFORE_AFTER_TEACHING_REVIEW.md](../research/audits/piano_pedagogical_motion_refinement_r1/BEFORE_AFTER_TEACHING_REVIEW.md)

## 后续建议

> STOP — HUMAN REVIEW。下一次动作修正必须是另一个明确授权阶段。

出处：[BEFORE_AFTER_TEACHING_REVIEW.md](../research/audits/piano_pedagogical_motion_refinement_r1/BEFORE_AFTER_TEACHING_REVIEW.md)

## 原报告与关键代码

- [audits/piano_pedagogical_motion_refinement_r1/FINAL_ANSWERS.md](../research/audits/piano_pedagogical_motion_refinement_r1/FINAL_ANSWERS.md)
- [audits/piano_pedagogical_motion_refinement_r1/PEDAGOGICAL_REPAIR_SCOPE.md](../research/audits/piano_pedagogical_motion_refinement_r1/PEDAGOGICAL_REPAIR_SCOPE.md)
- [audits/piano_pedagogical_motion_refinement_r1/LIGHTWEIGHT_MOTION_REPAIR.md](../research/audits/piano_pedagogical_motion_refinement_r1/LIGHTWEIGHT_MOTION_REPAIR.md)
- [audits/piano_pedagogical_motion_refinement_r1/BEFORE_AFTER_TEACHING_REVIEW.md](../research/audits/piano_pedagogical_motion_refinement_r1/BEFORE_AFTER_TEACHING_REVIEW.md)
- [audits/piano_pedagogical_motion_refinement_r1/MOTION_AND_CONTACT_PRESERVATION.md](../research/audits/piano_pedagogical_motion_refinement_r1/MOTION_AND_CONTACT_PRESERVATION.md)
- [audits/piano_pedagogical_motion_refinement_r1/authorize_diagnostic_render.py](../../src/legacy/audits/piano_pedagogical_motion_refinement_r1/authorize_diagnostic_render.py)
- [audits/piano_pedagogical_motion_refinement_r1/bake_validate.py](../../src/legacy/audits/piano_pedagogical_motion_refinement_r1/bake_validate.py)
- [audits/piano_pedagogical_motion_refinement_r1/build_review.py](../../src/legacy/audits/piano_pedagogical_motion_refinement_r1/build_review.py)
- [audits/piano_pedagogical_motion_refinement_r1/check_asset_identity.py](../../src/legacy/audits/piano_pedagogical_motion_refinement_r1/check_asset_identity.py)
- [audits/piano_pedagogical_motion_refinement_r1/check_new_neighbors.py](../../src/legacy/audits/piano_pedagogical_motion_refinement_r1/check_new_neighbors.py)
- [audits/piano_pedagogical_motion_refinement_r1/finalize.py](../../src/legacy/audits/piano_pedagogical_motion_refinement_r1/finalize.py)
- [audits/piano_pedagogical_motion_refinement_r1/generate_once.py](../../src/legacy/audits/piano_pedagogical_motion_refinement_r1/generate_once.py)
- [audits/piano_pedagogical_motion_refinement_r1/lock_strategy.py](../../src/legacy/audits/piano_pedagogical_motion_refinement_r1/lock_strategy.py)
- [audits/piano_pedagogical_motion_refinement_r1/media.py](../../src/legacy/audits/piano_pedagogical_motion_refinement_r1/media.py)
- [audits/piano_pedagogical_motion_refinement_r1/preflight.py](../../src/legacy/audits/piano_pedagogical_motion_refinement_r1/preflight.py)
- [audits/piano_pedagogical_motion_refinement_r1/prepare_bake_tools.py](../../src/legacy/audits/piano_pedagogical_motion_refinement_r1/prepare_bake_tools.py)
- [audits/piano_pedagogical_motion_refinement_r1/render.py](../../src/legacy/audits/piano_pedagogical_motion_refinement_r1/render.py)

## 输入、输出与大型证据

该目录原始成员 1184 项；拟公开身份记录 116 项。
- `audits/piano_pedagogical_motion_refinement_r1/PIANO_PEDAGOGICAL_MOTION_REFINEMENT_R1_DESIGN_ONLY.blend` → `hands-research-r1-selected-007.zip` / `payload/audits/piano_pedagogical_motion_refinement_r1/PIANO_PEDAGOGICAL_MOTION_REFINEMENT_R1_DESIGN_ONLY.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
