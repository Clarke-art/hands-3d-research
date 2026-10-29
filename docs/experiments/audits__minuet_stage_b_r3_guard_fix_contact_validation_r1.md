# audits/minuet_stage_b_r3_guard_fix_contact_validation_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 本轮没有把目标缩小到G3；7个原音符、指法、MIDI、通用安全区域与原R3相同。三个B3事件单独保留。

出处：[ALL_ACTIVE_CONTACT_PLACEMENT.md](../research/audits/minuet_stage_b_r3_guard_fix_contact_validation_r1/ALL_ACTIVE_CONTACT_PLACEMENT.md)

## 技术路线

> |Q5|完成唯一正式求解；nfev=20，njev=20，status=2，success=True，ftol终止；未达到100次上限。数值成功不等于验收PASS。|

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_b_r3_guard_fix_contact_validation_r1/FINAL_ANSWERS.md)

> 关节总角度域保障、actual修正预算表示和失败记录管线已修复并通过生成前门禁。唯一正式求解数值终止success=True，但最终实际delta小幅超过锁定运动保持预算，严格复合guard拒绝。没有修改参数重试，没有裁剪，也没有motion.npz/Blender/新视频。

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_b_r3_guard_fix_contact_validation_r1/IMPLEMENTATION_REPORT.md)

## 测试结论

> |Q1|总关节工程域保障PASS：113个支持点、827个输出与事件/窗口边界均合法，连续112段×20DOF多项式极值无总角度超限。实际delta预算是另一个失败门。|

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_b_r3_guard_fix_contact_validation_r1/FINAL_ANSWERS.md)

> |Q2|PASS：静态与正式共用actual_delta_deg和相同预算；最终插值delta仍小幅超预算，不能混称预算已满足。|

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_b_r3_guard_fix_contact_validation_r1/FINAL_ANSWERS.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

> 交付七个要求报告/状态文件，附完整返回checkpoint、guard checkpoint、稠密mask和失败摘要。推荐或后续修复未自动执行。STOP — HUMAN REVIEW。

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_b_r3_guard_fix_contact_validation_r1/IMPLEMENTATION_REPORT.md)

> 正式输出虽通过全部总角度工程域检查，但实际修正预算guard失败，按授权止损，没有写motion.npz、Blender Action或候选，没有进行skin动态回读或渲染。因此全部7次实际触键改善、和弦三指共同触键、后续单音、有限邻键风险均为本轮动态UNVERIFIED；不得以数值终止或静态余量填写PASS。

出处：[ALL_ACTIVE_CONTACT_PLACEMENT.md](../research/audits/minuet_stage_b_r3_guard_fix_contact_validation_r1/ALL_ACTIVE_CONTACT_PLACEMENT.md)

## 原报告与关键代码

- [audits/minuet_stage_b_r3_guard_fix_contact_validation_r1/FINAL_ANSWERS.md](../research/audits/minuet_stage_b_r3_guard_fix_contact_validation_r1/FINAL_ANSWERS.md)
- [audits/minuet_stage_b_r3_guard_fix_contact_validation_r1/IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_b_r3_guard_fix_contact_validation_r1/IMPLEMENTATION_REPORT.md)
- [audits/minuet_stage_b_r3_guard_fix_contact_validation_r1/MOTION_PRESERVATION_REPORT.md](../research/audits/minuet_stage_b_r3_guard_fix_contact_validation_r1/MOTION_PRESERVATION_REPORT.md)
- [audits/minuet_stage_b_r3_guard_fix_contact_validation_r1/GUARD_FIX_IMPLEMENTATION.md](../research/audits/minuet_stage_b_r3_guard_fix_contact_validation_r1/GUARD_FIX_IMPLEMENTATION.md)
- [audits/minuet_stage_b_r3_guard_fix_contact_validation_r1/PREGENERATION_VALIDATION.md](../research/audits/minuet_stage_b_r3_guard_fix_contact_validation_r1/PREGENERATION_VALIDATION.md)
- [audits/minuet_stage_b_r3_guard_fix_contact_validation_r1/ALL_ACTIVE_CONTACT_PLACEMENT.md](../research/audits/minuet_stage_b_r3_guard_fix_contact_validation_r1/ALL_ACTIVE_CONTACT_PLACEMENT.md)
- [audits/minuet_stage_b_r3_guard_fix_contact_validation_r1/00_prepare.py](../../src/legacy/audits/minuet_stage_b_r3_guard_fix_contact_validation_r1/00_prepare.py)
- [audits/minuet_stage_b_r3_guard_fix_contact_validation_r1/01_preflight.py](../../src/legacy/audits/minuet_stage_b_r3_guard_fix_contact_validation_r1/01_preflight.py)
- [audits/minuet_stage_b_r3_guard_fix_contact_validation_r1/02_lock.py](../../src/legacy/audits/minuet_stage_b_r3_guard_fix_contact_validation_r1/02_lock.py)
- [audits/minuet_stage_b_r3_guard_fix_contact_validation_r1/03_generate_once.py](../../src/legacy/audits/minuet_stage_b_r3_guard_fix_contact_validation_r1/03_generate_once.py)
- [audits/minuet_stage_b_r3_guard_fix_contact_validation_r1/04_failure_delivery.py](../../src/legacy/audits/minuet_stage_b_r3_guard_fix_contact_validation_r1/04_failure_delivery.py)
- [audits/minuet_stage_b_r3_guard_fix_contact_validation_r1/stage_common.py](../../src/legacy/audits/minuet_stage_b_r3_guard_fix_contact_validation_r1/stage_common.py)
- [audits/minuet_stage_b_r3_guard_fix_contact_validation_r1/total_angle_pipeline.py](../../src/legacy/audits/minuet_stage_b_r3_guard_fix_contact_validation_r1/total_angle_pipeline.py)

## 输入、输出与大型证据

该目录原始成员 32 项；拟公开身份记录 27 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
