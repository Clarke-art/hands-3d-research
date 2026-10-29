# audits/minuet_stage_c_r5_phase_aware_spatial_window_implementation

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> Q2：3.825秒任务接口已正确表达中指E5活动、无名指F♯5准备，D5仅退出/机械上下文，不再错误持键；未产生修复动作。

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_c_r5_phase_aware_spatial_window_implementation/FINAL_ANSWERS.md)

> Q4：FAIL。四端点均有必须保持而超过0.5mm的非目标黑键穿入，无法同时满足边界原姿态和安全门槛。

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_c_r5_phase_aware_spatial_window_implementation/FINAL_ANSWERS.md)

## 技术路线

> Q1：实现全五指基于事件的重叠角色计划与共享相邻关系；未完成交接路径求解。

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_c_r5_phase_aware_spatial_window_implementation/FINAL_ANSWERS.md)

> Q3：PARTIAL。实际凸黑键/皮肤内部深度、面交叉和硬裕量已实现；全手连续分离、白键与五指完整保护未完成，因边界失败停止。

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_c_r5_phase_aware_spatial_window_implementation/FINAL_ANSWERS.md)

## 测试结论

> Q3：PARTIAL。实际凸黑键/皮肤内部深度、面交叉和硬裕量已实现；全手连续分离、白键与五指完整保护未完成，因边界失败停止。

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_c_r5_phase_aware_spatial_window_implementation/FINAL_ANSWERS.md)

> Q4：FAIL。四端点均有必须保持而超过0.5mm的非目标黑键穿入，无法同时满足边界原姿态和安全门槛。

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_c_r5_phase_aware_spatial_window_implementation/FINAL_ANSWERS.md)

## 失败原因与证据边界

> Q5：未运行软残差交易；硬边界门禁已阻断，但可行性优先轨迹求解器NOT_IMPLEMENTED。

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_c_r5_phase_aware_spatial_window_implementation/FINAL_ANSWERS.md)

> - close_and_report.py：锁定失败原因、拆分既有冲突范围、写报告和核验哈希。

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_c_r5_phase_aware_spatial_window_implementation/IMPLEMENTATION_REPORT.md)

## 后续建议

> ACTIVE_CONTACT只在原NOTE_ON/OFF内要求原活动键；PREPARING从下一音前180 ms渐入，不获得接触豁免；RELEASING在NOTE_OFF后40 ms衰减，属于卸载偏好而非旧键必须持住；EXITING在NOTE_OFF后120 ms内提供渐入/渐出的单侧离开关系描述，不强制旧键面等式/整指floor；IDLE补足低任务参与部分，交给原动作风格与共同空间约束，不指定固定中性姿态。40/120/180 ms是本次有限角色接口政策，不是普适演奏学结论，也未经新动态验证。

出处：[EVENT_PHASE_ROLE_PLAN.md](../research/audits/minuet_stage_c_r5_phase_aware_spatial_window_implementation/EVENT_PHASE_ROLE_PLAN.md)

> 各角色采用独立条件生成，释放、退出和下一音准备可同时存在，不用互斥elif选唯一目标。当前只落实任务语义与连续偏好包络；阶段角色与NOTE_ON/OFF接触身份会在真实事件处切换，其动作连续性仍需未来轨迹约束，不能由包络平滑直接声称已通过。

出处：[EVENT_PHASE_ROLE_PLAN.md](../research/audits/minuet_stage_c_r5_phase_aware_spatial_window_implementation/EVENT_PHASE_ROLE_PLAN.md)

## 原报告与关键代码

- [audits/minuet_stage_c_r5_phase_aware_spatial_window_implementation/FINAL_ANSWERS.md](../research/audits/minuet_stage_c_r5_phase_aware_spatial_window_implementation/FINAL_ANSWERS.md)
- [audits/minuet_stage_c_r5_phase_aware_spatial_window_implementation/IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_c_r5_phase_aware_spatial_window_implementation/IMPLEMENTATION_REPORT.md)
- [audits/minuet_stage_c_r5_phase_aware_spatial_window_implementation/WINDOW_BOUNDARY_FEASIBILITY.md](../research/audits/minuet_stage_c_r5_phase_aware_spatial_window_implementation/WINDOW_BOUNDARY_FEASIBILITY.md)
- [audits/minuet_stage_c_r5_phase_aware_spatial_window_implementation/MOTION_PRESERVATION.md](../research/audits/minuet_stage_c_r5_phase_aware_spatial_window_implementation/MOTION_PRESERVATION.md)
- [audits/minuet_stage_c_r5_phase_aware_spatial_window_implementation/EVENT_PHASE_ROLE_PLAN.md](../research/audits/minuet_stage_c_r5_phase_aware_spatial_window_implementation/EVENT_PHASE_ROLE_PLAN.md)
- [audits/minuet_stage_c_r5_phase_aware_spatial_window_implementation/SPATIAL_AND_CONTACT_VALIDATION.md](../research/audits/minuet_stage_c_r5_phase_aware_spatial_window_implementation/SPATIAL_AND_CONTACT_VALIDATION.md)
- [audits/minuet_stage_c_r5_phase_aware_spatial_window_implementation/LOCAL_SPATIAL_CONSTRAINT_DESIGN.md](../research/audits/minuet_stage_c_r5_phase_aware_spatial_window_implementation/LOCAL_SPATIAL_CONSTRAINT_DESIGN.md)
- [audits/minuet_stage_c_r5_phase_aware_spatial_window_implementation/boundary_readonly.py](../../src/legacy/audits/minuet_stage_c_r5_phase_aware_spatial_window_implementation/boundary_readonly.py)
- [audits/minuet_stage_c_r5_phase_aware_spatial_window_implementation/close_and_report.py](../../src/legacy/audits/minuet_stage_c_r5_phase_aware_spatial_window_implementation/close_and_report.py)
- [audits/minuet_stage_c_r5_phase_aware_spatial_window_implementation/event_phase_plan.py](../../src/legacy/audits/minuet_stage_c_r5_phase_aware_spatial_window_implementation/event_phase_plan.py)
- [audits/minuet_stage_c_r5_phase_aware_spatial_window_implementation/local_spatial_constraints.py](../../src/legacy/audits/minuet_stage_c_r5_phase_aware_spatial_window_implementation/local_spatial_constraints.py)
- [audits/minuet_stage_c_r5_phase_aware_spatial_window_implementation/precheck_setup.py](../../src/legacy/audits/minuet_stage_c_r5_phase_aware_spatial_window_implementation/precheck_setup.py)

## 输入、输出与大型证据

该目录原始成员 23 项；拟公开身份记录 22 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
