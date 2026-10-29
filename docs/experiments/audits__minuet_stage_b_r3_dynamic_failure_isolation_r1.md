# audits/minuet_stage_b_r3_dynamic_failure_isolation_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> |Q6|不是已证实的限制；固定root静态任务实际可达，完整动态root冲突UNKNOWN。|

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_b_r3_dynamic_failure_isolation_r1/FINAL_ANSWERS.md)

> |新接触目标与R2姿态存在完整动态冲突|UNKNOWN|独立pose支持静态可达；无完整动态解/约束残差|

出处：[JOINT_LIMIT_CAUSE_ANALYSIS.md](../research/audits/minuet_stage_b_r3_dynamic_failure_isolation_r1/JOINT_LIMIT_CAUSE_ANALYSIS.md)

## 技术路线

> |Q12|YES：8336个保护文件哈希一致，含原8294文件及全部42个R3文件；无历史修改、动态求解或新候选。|

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_b_r3_dynamic_failure_isolation_r1/FINAL_ANSWERS.md)

> 范围来自piano_hand_static_posture_clearance_refinement_r2/STATIC_REFINEMENT_POLICY_R2.json的joint_increment_bounds_deg，经R2 left_chord_base.py的B/self.bounds/state_low/state_high进入guard。全部五指本曲目都被使用，因此未替换成LEFT_IDLE_INDEX/RING的整指hard域；闲置策略只是另有软约束。它是已有弯曲RSSF rest上的工程增量域，不是测得的解剖生理角度或被冻结Rig的全部物理极限。

出处：[JOINT_LIMIT_CAUSE_ANALYSIS.md](../research/audits/minuet_stage_b_r3_dynamic_failure_isolation_r1/JOINT_LIMIT_CAUSE_ANALYSIS.md)

## 测试结论

> |Q2|没有。现有R3未保存fit.x、latent、输出q或违规mask；FINAL_FAILED_TRAJECTORY=UNAVAILABLE。|

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_b_r3_dynamic_failure_isolation_r1/FINAL_ANSWERS.md)

> 结论：**guard触发路径已定位；首次动态超限关节、时间和量尚未定位。** 确认了输出域保障不足、静态/正式变量预算不一致及失败前未保存结果三个工程问题；它们不等于证明上次具体违规样本，更不证明冻结Rig不可行。

出处：[JOINT_LIMIT_CAUSE_ANALYSIS.md](../research/audits/minuet_stage_b_r3_dynamic_failure_isolation_r1/JOINT_LIMIT_CAUSE_ANALYSIS.md)

## 失败原因与证据边界

> |安全区域几何本身不合理|UNKNOWN作为失败原因|已有静态正余量，无新证据需调整区域|

出处：[JOINT_LIMIT_CAUSE_ANALYSIS.md](../research/audits/minuet_stage_b_r3_dynamic_failure_isolation_r1/JOINT_LIMIT_CAUSE_ANALYSIS.md)

## 后续建议

> 建议未来调用顺序（示意，**本轮未执行**）：

出处：[DIAGNOSTIC_INSTRUMENTATION.md](../research/audits/minuet_stage_b_r3_dynamic_failure_isolation_r1/DIAGNOSTIC_INSTRUMENTATION.md)

## 原报告与关键代码

- [audits/minuet_stage_b_r3_dynamic_failure_isolation_r1/FINAL_ANSWERS.md](../research/audits/minuet_stage_b_r3_dynamic_failure_isolation_r1/FINAL_ANSWERS.md)
- [audits/minuet_stage_b_r3_dynamic_failure_isolation_r1/JOINT_LIMIT_CAUSE_ANALYSIS.md](../research/audits/minuet_stage_b_r3_dynamic_failure_isolation_r1/JOINT_LIMIT_CAUSE_ANALYSIS.md)
- [audits/minuet_stage_b_r3_dynamic_failure_isolation_r1/DYNAMIC_FAILURE_EVIDENCE.md](../research/audits/minuet_stage_b_r3_dynamic_failure_isolation_r1/DYNAMIC_FAILURE_EVIDENCE.md)
- [audits/minuet_stage_b_r3_dynamic_failure_isolation_r1/MINIMAL_NEXT_REPAIR_PLAN.md](../research/audits/minuet_stage_b_r3_dynamic_failure_isolation_r1/MINIMAL_NEXT_REPAIR_PLAN.md)
- [audits/minuet_stage_b_r3_dynamic_failure_isolation_r1/DIAGNOSTIC_INSTRUMENTATION.md](../research/audits/minuet_stage_b_r3_dynamic_failure_isolation_r1/DIAGNOSTIC_INSTRUMENTATION.md)
- [audits/minuet_stage_b_r3_dynamic_failure_isolation_r1/ROOT_CONTACT_CONSTRAINT_ASSESSMENT.md](../research/audits/minuet_stage_b_r3_dynamic_failure_isolation_r1/ROOT_CONTACT_CONSTRAINT_ASSESSMENT.md)
- [audits/minuet_stage_b_r3_dynamic_failure_isolation_r1/diagnostic_recorder.py](../../src/legacy/audits/minuet_stage_b_r3_dynamic_failure_isolation_r1/diagnostic_recorder.py)
- [audits/minuet_stage_b_r3_dynamic_failure_isolation_r1/readonly_analysis.py](../../src/legacy/audits/minuet_stage_b_r3_dynamic_failure_isolation_r1/readonly_analysis.py)
- [audits/minuet_stage_b_r3_dynamic_failure_isolation_r1/supplemental_checks.py](../../src/legacy/audits/minuet_stage_b_r3_dynamic_failure_isolation_r1/supplemental_checks.py)
- [audits/minuet_stage_b_r3_dynamic_failure_isolation_r1/test_small_fixtures.py](../../src/legacy/audits/minuet_stage_b_r3_dynamic_failure_isolation_r1/test_small_fixtures.py)
- [audits/minuet_stage_b_r3_dynamic_failure_isolation_r1/write_reports.py](../../src/legacy/audits/minuet_stage_b_r3_dynamic_failure_isolation_r1/write_reports.py)

## 输入、输出与大型证据

该目录原始成员 21 项；拟公开身份记录 21 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
