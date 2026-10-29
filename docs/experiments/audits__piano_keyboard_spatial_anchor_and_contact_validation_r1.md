# audits/piano_keyboard_spatial_anchor_and_contact_validation_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 静态朝向来自正式wrist rest anatomical frame；scale=1。只解XYZ整手平移，目标是实际键面上的固定白键front+25mm/黑键front+15mm点。全部assigned held notes等权，二阶时间差分正则lambda=(0.080×60)^4，421观测一次全局求解；内部Action不变，动态yaw/6DOF关闭。所有旧DISPLAY_ONLY review offsets完全未导入。

出处：[PIANO_KEYBOARD_SPATIAL_ANCHOR_AND_CONTACT_VALIDATION_R1_REPORT.md](../research/audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/PIANO_KEYBOARD_SPATIAL_ANCHOR_AND_CONTACT_VALIDATION_R1_REPORT.md)

## 技术路线

> CONTACT_VERTICAL_TOLERANCE_MM=3；CONTACT_HORIZONTAL_TOLERANCE_MM=2；正确键还必须处于真实playable region内部。阈值文件先于04_hands提取和05_solve求解写出，并用PRE_RESULT_POLICY_LOCK哈希锁定。没有看结果调容差或逐音调平滑。

出处：[PIANO_KEYBOARD_SPATIAL_ANCHOR_AND_CONTACT_VALIDATION_R1_REPORT.md](../research/audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/PIANO_KEYBOARD_SPATIAL_ANCHOR_AND_CONTACT_VALIDATION_R1_REPORT.md)

> 静态朝向来自正式wrist rest anatomical frame；scale=1。只解XYZ整手平移，目标是实际键面上的固定白键front+25mm/黑键front+15mm点。全部assigned held notes等权，二阶时间差分正则lambda=(0.080×60)^4，421观测一次全局求解；内部Action不变，动态yaw/6DOF关闭。所有旧DISPLAY_ONLY review offsets完全未导入。

出处：[PIANO_KEYBOARD_SPATIAL_ANCHOR_AND_CONTACT_VALIDATION_R1_REPORT.md](../research/audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/PIANO_KEYBOARD_SPATIAL_ANCHOR_AND_CONTACT_VALIDATION_R1_REPORT.md)

## 测试结论

> | Q10 | PARTIAL | 可测起音：R9/39、L4/26符合预锁定容差；多数失败，不构成接触验证。 |

出处：[PIANO_KEYBOARD_SPATIAL_ANCHOR_AND_CONTACT_VALIDATION_R1_REPORT.md](../research/audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/PIANO_KEYBOARD_SPATIAL_ANCHOR_AND_CONTACT_VALIDATION_R1_REPORT.md)

> | Q11 | PARTIAL | 全部用同一整手root；同时持音观测R2/38、L4/82全部满足容差。固定朝向下R1、L8个观测连宽松横向可行域都为空。 |

出处：[PIANO_KEYBOARD_SPATIAL_ANCHOR_AND_CONTACT_VALIDATION_R1_REPORT.md](../research/audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/PIANO_KEYBOARD_SPATIAL_ANCHOR_AND_CONTACT_VALIDATION_R1_REPORT.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 原报告与关键代码

- [audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/PIANO_KEYBOARD_SPATIAL_ANCHOR_AND_CONTACT_VALIDATION_R1_REPORT.md](../research/audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/PIANO_KEYBOARD_SPATIAL_ANCHOR_AND_CONTACT_VALIDATION_R1_REPORT.md)
- [audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/01_keyboard.mjs](../../src/legacy/audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/01_keyboard.mjs)
- [audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/02_probe.py](../../src/legacy/audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/02_probe.py)
- [audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/03_data.py](../../src/legacy/audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/03_data.py)
- [audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/04_hands.py](../../src/legacy/audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/04_hands.py)
- [audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/05_solve.py](../../src/legacy/audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/05_solve.py)
- [audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/06_candidate.py](../../src/legacy/audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/06_candidate.py)
- [audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/07_render.py](../../src/legacy/audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/07_render.py)
- [audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/08_diagnostics.py](../../src/legacy/audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/08_diagnostics.py)
- [audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/09_media.py](../../src/legacy/audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/09_media.py)
- [audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/10_finalize.py](../../src/legacy/audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/10_finalize.py)
- [audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/11_keyboard_verify.py](../../src/legacy/audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/11_keyboard_verify.py)
- [audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/12_camera_polish.py](../../src/legacy/audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/12_camera_polish.py)

## 输入、输出与大型证据

该目录原始成员 63 项；拟公开身份记录 53 项。
- `audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/hand_motion_canonical.npz` → `hands-research-r1-selected-007.zip` / `payload/audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/hand_motion_canonical.npz`
- `audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/PIANO_KEYBOARD_SPATIAL_ANCHOR_VALIDATION_CANDIDATE_R1.blend` → `hands-research-r1-selected-007.zip` / `payload/audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/PIANO_KEYBOARD_SPATIAL_ANCHOR_VALIDATION_CANDIDATE_R1.blend`
- `audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/spatial_evaluations.npz` → `hands-research-r1-selected-007.zip` / `payload/audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/spatial_evaluations.npz`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
