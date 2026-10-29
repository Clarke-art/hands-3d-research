# audits/minuet_stage_c_r6_whole_phrase_spatial_planning

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> **Q10**：FAIL；非目标黑键最大深度 5.6039 → 5.6368 mm，不能据此放行整段。

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/FINAL_ANSWERS.md)

> `prepare.py` 复用 R5 角色接口并构建全段节点；`export_readonly.py` / `inspect_shape.py` 只读提取冻结场景；`whole_phrase_model.py` 重建五指绝对关节 FK、真实 LBS 与原拇指 corrective；`trajectory_solver.py` 实现全段 C1 三次曲线、Bezier 工程域、空间/触键不等式和源风格目标；`run_once.py` 设置外部墙钟保险；验证脚本只测量唯一终态，不再求解。

出处：[SOLVER_IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/SOLVER_IMPLEMENTATION_REPORT.md)

## 技术路线

> **Q1**：是。0–5.95 秒全段 20 关节统一求解；旧两窗口仅作为诊断分组。

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/FINAL_ANSWERS.md)

> **Q2**：已实现五指事件角色及重叠，区分卸力、退出、机械回弹和下一音准备；未证明所有角色的实际运动都达到质量门禁。

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/FINAL_ANSWERS.md)

## 测试结论

> **Q4**：起止关节自由，但未建立自然可行结果。开始状态的采样黑键最大深度 0.4308 mm、无已检指对相交，仅可待审 WARN；结束状态仍穿入黑键 1.6743 mm，明确未通过。Human 未批准。

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/FINAL_ANSWERS.md)

> **Q10**：FAIL；非目标黑键最大深度 5.6039 → 5.6368 mm，不能据此放行整段。

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/FINAL_ANSWERS.md)

## 失败原因与证据边界

> 空间不等式独立于自然度目标，使用 SciPy trust-constr；允许不可行初值及正常数值迭代，最终任何硬条件违规都阻断候选。没有把碰撞和触键仅作为可相互交易的软罚项。

出处：[SPATIAL_CONSTRAINT_AND_FEASIBILITY.md](../research/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/SPATIAL_CONSTRAINT_AND_FEASIBILITY.md)

## 后续建议

> **Q2**：已实现五指事件角色及重叠，区分卸力、退出、机械回弹和下一音准备；未证明所有角色的实际运动都达到质量门禁。

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/FINAL_ANSWERS.md)

> 3.825 秒：中指 E5 为 ACTIVE_CONTACT；无名指 F♯5 为 PREPARING，旧 D5 仅有 EXITING 和机械回弹上下文，无旧 D5 硬持键。早段 G4→A4→B4→C5→D5、晚段 D5→E5→F♯5 及其后续均来自同一事件计划。

出处：[WHOLE_PHRASE_ROLE_AND_MOTION_PLAN.md](../research/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/WHOLE_PHRASE_ROLE_AND_MOTION_PLAN.md)

## 原报告与关键代码

- [audits/minuet_stage_c_r6_whole_phrase_spatial_planning/FINAL_ANSWERS.md](../research/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/FINAL_ANSWERS.md)
- [audits/minuet_stage_c_r6_whole_phrase_spatial_planning/SOLVER_IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/SOLVER_IMPLEMENTATION_REPORT.md)
- [audits/minuet_stage_c_r6_whole_phrase_spatial_planning/SPATIAL_CONSTRAINT_AND_FEASIBILITY.md](../research/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/SPATIAL_CONSTRAINT_AND_FEASIBILITY.md)
- [audits/minuet_stage_c_r6_whole_phrase_spatial_planning/DUAL_HAND_FUNCTIONAL_VALIDATION.md](../research/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/DUAL_HAND_FUNCTIONAL_VALIDATION.md)
- [audits/minuet_stage_c_r6_whole_phrase_spatial_planning/WHOLE_PHRASE_SPATIAL_VALIDATION.md](../research/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/WHOLE_PHRASE_SPATIAL_VALIDATION.md)
- [audits/minuet_stage_c_r6_whole_phrase_spatial_planning/WHOLE_PHRASE_ROLE_AND_MOTION_PLAN.md](../research/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/WHOLE_PHRASE_ROLE_AND_MOTION_PLAN.md)
- [audits/minuet_stage_c_r6_whole_phrase_spatial_planning/MOTION_NATURALNESS_AND_PRESERVATION.md](../research/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/MOTION_NATURALNESS_AND_PRESERVATION.md)
- [audits/minuet_stage_c_r6_whole_phrase_spatial_planning/check_readonly.py](../../src/legacy/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/check_readonly.py)
- [audits/minuet_stage_c_r6_whole_phrase_spatial_planning/check_terminal_parity.py](../../src/legacy/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/check_terminal_parity.py)
- [audits/minuet_stage_c_r6_whole_phrase_spatial_planning/close_evidence.py](../../src/legacy/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/close_evidence.py)
- [audits/minuet_stage_c_r6_whole_phrase_spatial_planning/common.py](../../src/legacy/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/common.py)
- [audits/minuet_stage_c_r6_whole_phrase_spatial_planning/export_readonly.py](../../src/legacy/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/export_readonly.py)
- [audits/minuet_stage_c_r6_whole_phrase_spatial_planning/finish_reports.py](../../src/legacy/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/finish_reports.py)
- [audits/minuet_stage_c_r6_whole_phrase_spatial_planning/inspect_shape.py](../../src/legacy/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/inspect_shape.py)
- [audits/minuet_stage_c_r6_whole_phrase_spatial_planning/lock_strategy.py](../../src/legacy/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/lock_strategy.py)
- [audits/minuet_stage_c_r6_whole_phrase_spatial_planning/postprocess_once.py](../../src/legacy/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/postprocess_once.py)
- [audits/minuet_stage_c_r6_whole_phrase_spatial_planning/prepare.py](../../src/legacy/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/prepare.py)
- [audits/minuet_stage_c_r6_whole_phrase_spatial_planning/prepare_validation.py](../../src/legacy/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/prepare_validation.py)
- [audits/minuet_stage_c_r6_whole_phrase_spatial_planning/render_terminal_diagnostics.py](../../src/legacy/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/render_terminal_diagnostics.py)

## 输入、输出与大型证据

该目录原始成员 69 项；拟公开身份记录 62 项。
- `audits/minuet_stage_c_r6_whole_phrase_spatial_planning/ACTUAL_TERMINAL_SKIN.npz` → `hands-research-r1-selected-003.zip` / `payload/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/ACTUAL_TERMINAL_SKIN.npz`
- `audits/minuet_stage_c_r6_whole_phrase_spatial_planning/SOURCE_MODEL.npz` → `hands-research-r1-selected-003.zip` / `payload/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/SOURCE_MODEL.npz`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
