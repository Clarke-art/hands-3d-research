# audits/minuet_stage_c_r3_right_hand_local_spatial_clearance

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> Q2：食指—G#4/A#4/C#5；中指—C#5/D#5；无名指—C#5/D#5。另有无名指在目标 F#5 上轻微触键进入，独立 WARN。完整时段见诊断表。

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/FINAL_ANSWERS.md)

> Q9：原态主动目标 pad 保持，1148 个记录覆盖 23 音符，继承接触域 PASS；这不覆盖侧面黑键净空。无 R3 候选可另作验证。

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/FINAL_ANSWERS.md)

## 技术路线

> Q12：新候选 0，正式局部求解尝试 0，未消耗唯一候选名额，未重试。

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/FINAL_ANSWERS.md)

> 通过 Blender 后台只读打开必要历史 .blend；不保存历史文件，不插入任何动画关键帧、不创建 Action、不调用优化器。所有导入脚本禁用 Python 字节码写入，导入的是有限数学/皮肤读取辅助函数。没有 Stage A/Stage B 重规划，也没有 R3 动态候选或 Blend。正式局部运动求解尝试 0，动态候选 0，参数锁后重试 0。

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/IMPLEMENTATION_REPORT.md)

## 测试结论

> Q9：原态主动目标 pad 保持，1148 个记录覆盖 23 音符，继承接触域 PASS；这不覆盖侧面黑键净空。无 R3 候选可另作验证。

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/FINAL_ANSWERS.md)

> Q14：不具备提交“修复候选”审核条件；可审核诊断与范围瓶颈。FINAL_STATUS=FAIL_CLOSED，STOP — HUMAN REVIEW。

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/FINAL_ANSWERS.md)

## 失败原因与证据边界

> 唯一参考/拟修复基线锁定 Stage C R1：d8e0f5a85e71323739bfcd4de485ff7a2b4096f8e59bbd4c578ee9d76d3e51a7。原因是保留原 Stage A R2 右手动作；R2 只用于对照，不叠加它的 −6° 修正，也不在生成后挑选候选。

出处：[LOCAL_JOINT_COORDINATION_DESIGN.md](../research/audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/LOCAL_JOINT_COORDINATION_DESIGN.md)

## 后续建议

> 禁止把增加无名指横展当作下一策略。中指 B4→无名指 C5 的主动交接应保护当前活动 pad 并连续交接，关节增量的支撑边界应具有零位置/速度差，优先平滑 C2 包络；不以逐帧角度特判补丁替代协调。未来若获得额外范围授权，需以事件/接触阶段和实际目标键定义窗口，先锁定全部参数，再至多一次动态求解。这是未来设计方向，未作为本轮已执行成果。

出处：[LOCAL_JOINT_COORDINATION_DESIGN.md](../research/audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/LOCAL_JOINT_COORDINATION_DESIGN.md)

## 原报告与关键代码

- [audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/FINAL_ANSWERS.md](../research/audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/FINAL_ANSWERS.md)
- [audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/IMPLEMENTATION_REPORT.md)
- [audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/BEFORE_AFTER_SPATIAL_REVIEW.md](../research/audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/BEFORE_AFTER_SPATIAL_REVIEW.md)
- [audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/APPROVED_MOTION_PRESERVATION.md](../research/audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/APPROVED_MOTION_PRESERVATION.md)
- [audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/LOCAL_JOINT_COORDINATION_DESIGN.md](../research/audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/LOCAL_JOINT_COORDINATION_DESIGN.md)
- [audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/RIGHT_HAND_OVERLAP_AND_BLACK_KEY_DIAGNOSIS.md](../research/audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/RIGHT_HAND_OVERLAP_AND_BLACK_KEY_DIAGNOSIS.md)
- [audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/contact_and_scope_gate.py](../../src/legacy/audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/contact_and_scope_gate.py)
- [audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/deliver.py](../../src/legacy/audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/deliver.py)
- [audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/diagnose.py](../../src/legacy/audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/diagnose.py)
- [audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/diagnostic_media.py](../../src/legacy/audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/diagnostic_media.py)
- [audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/inspect_scene.py](../../src/legacy/audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/inspect_scene.py)
- [audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/intake.py](../../src/legacy/audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/intake.py)
- [audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/late_handoff_verify.py](../../src/legacy/audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/late_handoff_verify.py)
- [audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/late_media.py](../../src/legacy/audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/late_media.py)
- [audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/review_server.py](../../src/legacy/audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/review_server.py)
- [audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/verify_delivery.py](../../src/legacy/audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/verify_delivery.py)
- [audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/verify_witnesses.py](../../src/legacy/audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/verify_witnesses.py)

## 输入、输出与大型证据

该目录原始成员 188 项；拟公开身份记录 179 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
