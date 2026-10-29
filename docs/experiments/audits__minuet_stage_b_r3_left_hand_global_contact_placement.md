# audits/minuet_stage_b_r3_left_hand_global_contact_placement

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 静态预检两批各10个姿态：首批一个约0.276mm标记目标误差被脚本绝对0.15mm筛选拒绝，但对应实际指腹余量4.57mm，不构成几何不可达证据。生成前改用已取得边余量的10%比例筛选；第二批通过后仅锁定一次正式参数。静态总计20次pose求解，无Action/动态候选保存。不是动态生成重试。

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_b_r3_left_hand_global_contact_placement/IMPLEMENTATION_REPORT.md)

> |Q3|CONFIRMED：3mm中心内缩忽略约8–11mm指腹宽度；偏向不一、横漂小。SUPPORTED：软目标偏好与关节/共同掌腕折衷及投影因素。UNKNOWN：软组织真实压力区。|

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_b_r3_left_hand_global_contact_placement/IMPLEMENTATION_REPORT.md)

## 技术路线

> 本轮完成全部7次R2真实指腹落点只读诊断、几何通用区域代码、固定R2 root的静态可达性测试和一次锁定策略。唯一正式动态生成在最终插值/烘焙前的关节域保护处失败；没有保存motion.npz或Blender候选，没有新视频，没有第二次求解。

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_b_r3_left_hand_global_contact_placement/IMPLEMENTATION_REPORT.md)

> 所有新增代码均在本独立目录，R2代码和历史报告未改。使用实际左FK/事件协调器，新增contact_region.py和相对R2的小范围修正求解。原MIDI、指法、tempo和全部事件保留。

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_b_r3_left_hand_global_contact_placement/IMPLEMENTATION_REPORT.md)

## 测试结论

> 唯一动态求解最后可见日志为残差调用3303、约240.5秒、加权接触RMS0.7916；失败发生在结果持久化之前。实际nfev、是否达到100次上限、最终收敛状态及超限采样没有保存，全部UNKNOWN。残差调用次数不能冒充nfev，数值残差降低不能当作实际触键/视觉通过。GENERATION_FAILURE.json明确区分CONFIRMED/SUPPORTED/UNKNOWN。

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_b_r3_left_hand_global_contact_placement/IMPLEMENTATION_REPORT.md)

> |Q4|通用几何区域与运动保持修正代码已建立，静态可达性支持；动态验证未完成，因此WHITE_KEY_CONTACT_REGION=PARTIAL。|

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_b_r3_left_hand_global_contact_placement/IMPLEMENTATION_REPORT.md)

## 失败原因与证据边界

> **SUPPORTED**：教学和俯视帧可见主动指靠近键缝的轮廓；侧斜视角受到抬起轮廓和遮挡影响。指腹尺寸加上宽松的目标偏好，以及R2各指可达性、关节域与共享掌腕的折衷，是偏边原因。三音和弦的目标受共同root约束，不能把单指标记在键内当作整个指腹安全。

出处：[ALL_ACTIVE_FINGER_PLACEMENT_AUDIT.md](../research/audits/minuet_stage_b_r3_left_hand_global_contact_placement/ALL_ACTIVE_FINGER_PLACEMENT_AUDIT.md)

## 后续建议

> 首份结果guard失败后立即停止；没有裁剪关节、回投影、改参数、重算或手动逐指修补。后续场景/诊断/渲染脚本属于未执行准备代码，不代表已产生对应输出。唯一候选限制按一次正式生成尝试计数；有效保存候选0份。

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_b_r3_left_hand_global_contact_placement/IMPLEMENTATION_REPORT.md)

> |Q7|R2后续单音技术PASS保留；R3未验证，R3验收门FAIL。|

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_b_r3_left_hand_global_contact_placement/IMPLEMENTATION_REPORT.md)

## 原报告与关键代码

- [audits/minuet_stage_b_r3_left_hand_global_contact_placement/IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_b_r3_left_hand_global_contact_placement/IMPLEMENTATION_REPORT.md)
- [audits/minuet_stage_b_r3_left_hand_global_contact_placement/MOTION_PRESERVATION_REPORT.md](../research/audits/minuet_stage_b_r3_left_hand_global_contact_placement/MOTION_PRESERVATION_REPORT.md)
- [audits/minuet_stage_b_r3_left_hand_global_contact_placement/BEFORE_AFTER_CONTACT_REVIEW.md](../research/audits/minuet_stage_b_r3_left_hand_global_contact_placement/BEFORE_AFTER_CONTACT_REVIEW.md)
- [audits/minuet_stage_b_r3_left_hand_global_contact_placement/ALL_ACTIVE_FINGER_PLACEMENT_AUDIT.md](../research/audits/minuet_stage_b_r3_left_hand_global_contact_placement/ALL_ACTIVE_FINGER_PLACEMENT_AUDIT.md)
- [audits/minuet_stage_b_r3_left_hand_global_contact_placement/GENERAL_WHITE_KEY_CONTACT_REGION_DESIGN.md](../research/audits/minuet_stage_b_r3_left_hand_global_contact_placement/GENERAL_WHITE_KEY_CONTACT_REGION_DESIGN.md)
- [audits/minuet_stage_b_r3_left_hand_global_contact_placement/00_readonly_audit.py](../../src/legacy/audits/minuet_stage_b_r3_left_hand_global_contact_placement/00_readonly_audit.py)
- [audits/minuet_stage_b_r3_left_hand_global_contact_placement/01_static_and_lock.py](../../src/legacy/audits/minuet_stage_b_r3_left_hand_global_contact_placement/01_static_and_lock.py)
- [audits/minuet_stage_b_r3_left_hand_global_contact_placement/02_generate_once.py](../../src/legacy/audits/minuet_stage_b_r3_left_hand_global_contact_placement/02_generate_once.py)
- [audits/minuet_stage_b_r3_left_hand_global_contact_placement/03_scene_readback.py](../../src/legacy/audits/minuet_stage_b_r3_left_hand_global_contact_placement/03_scene_readback.py)
- [audits/minuet_stage_b_r3_left_hand_global_contact_placement/04_diagnostics.py](../../src/legacy/audits/minuet_stage_b_r3_left_hand_global_contact_placement/04_diagnostics.py)
- [audits/minuet_stage_b_r3_left_hand_global_contact_placement/05_render.py](../../src/legacy/audits/minuet_stage_b_r3_left_hand_global_contact_placement/05_render.py)
- [audits/minuet_stage_b_r3_left_hand_global_contact_placement/06_media.py](../../src/legacy/audits/minuet_stage_b_r3_left_hand_global_contact_placement/06_media.py)
- [audits/minuet_stage_b_r3_left_hand_global_contact_placement/07_finish.py](../../src/legacy/audits/minuet_stage_b_r3_left_hand_global_contact_placement/07_finish.py)
- [audits/minuet_stage_b_r3_left_hand_global_contact_placement/08_fail_closed_delivery.py](../../src/legacy/audits/minuet_stage_b_r3_left_hand_global_contact_placement/08_fail_closed_delivery.py)
- [audits/minuet_stage_b_r3_left_hand_global_contact_placement/contact_region.py](../../src/legacy/audits/minuet_stage_b_r3_left_hand_global_contact_placement/contact_region.py)
- [audits/minuet_stage_b_r3_left_hand_global_contact_placement/lock_generation.py](../../src/legacy/audits/minuet_stage_b_r3_left_hand_global_contact_placement/lock_generation.py)
- [audits/minuet_stage_b_r3_left_hand_global_contact_placement/stage_common.py](../../src/legacy/audits/minuet_stage_b_r3_left_hand_global_contact_placement/stage_common.py)

## 输入、输出与大型证据

该目录原始成员 40 项；拟公开身份记录 35 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
