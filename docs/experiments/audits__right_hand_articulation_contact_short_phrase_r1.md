# audits/right_hand_articulation_contact_short_phrase_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> **CONFIRMED：初始接触未到达，35ms压力下降不足，且持续HOLD维持失败姿态。** x/y在目标白键可奏区；不是按错键或目标身份错。小指MCP接触/下压系数停在“准备角+12°”界限；该边界是上一轮适配的工程限制，不是冻结Rig证明的生理极限。固定掌根与受限曲线不能补足白键键程。HOLD并未过早回升：真正回升只在原NOTE_OFF后。

出处：[RIGHT_HAND_MOTION_CAUSE_ANALYSIS.md](../research/audits/right_hand_articulation_contact_short_phrase_r1/RIGHT_HAND_MOTION_CAUSE_ANALYSIS.md)

> |音符|起音pad gap mm|full-down gap mm|35ms pad Z变化 mm|35ms key目标Z变化 mm|

出处：[RIGHT_HAND_MOTION_CAUSE_ANALYSIS.md](../research/audits/right_hand_articulation_contact_short_phrase_r1/RIGHT_HAND_MOTION_CAUSE_ANALYSIS.md)

## 技术路线

> 只修改本审计目录的非冻结运动适配，新文件 `articulation_common.py`、`right_motion.py`、`02_generate.py`。继续消费原performance_core FK/关节轴、teaching rig适配、static common皮肤预测/实际键面测量和bounded least_squares；没有重构求解器或增加骨骼。

出处：[RIGHT_HAND_MOTION_IMPLEMENTATION.md](../research/audits/right_hand_articulation_contact_short_phrase_r1/RIGHT_HAND_MOTION_IMPLEMENTATION.md)

> 总59参数：五指接触/全键程端点40、共同XYZ/pitch4、五指闲置屈曲15。一个完整序列残差共同优化contact、skin、既有净空、运动连续性和姿态正则。拟合次数1，重启0；nfev=21，calls=1142，约933.3s。root实际幅值XYZ mm/pitch deg：[-0.9194159529965074, 2.486674247324791, -4.999999999999989, -0.9616594150509167]。成功收敛只说明数值求解终止，不取代后验几何/产品检查。

出处：[RIGHT_HAND_MOTION_IMPLEMENTATION.md](../research/audits/right_hand_articulation_contact_short_phrase_r1/RIGHT_HAND_MOTION_IMPLEMENTATION.md)

## 测试结论

> A5_CONTACT=FAIL；FSHARP5_CONTACT=PASS。候选级触键检查，非Human最终产品批准。

出处：[A5_FSHARP5_CONTACT_REVIEW.md](../research/audits/right_hand_articulation_contact_short_phrase_r1/A5_FSHARP5_CONTACT_REVIEW.md)

> 最终状态：FAIL_CLOSED；自然度/双手协调正式结论待Human。唯一新候选 `RIGHT_HAND_ARTICULATION_CONTACT_DESIGN_ONLY_R1.blend`，SHA256 `dcb80abadaf8c441254159038ed055d44c1e6b21d2ae8316b669ac72028385ee`。

出处：[RIGHT_HAND_MOTION_IMPLEMENTATION.md](../research/audits/right_hand_articulation_contact_short_phrase_r1/RIGHT_HAND_MOTION_IMPLEMENTATION.md)

## 失败原因与证据边界

> **CONFIRMED：虚拟皮肤pad水平位于实际抬高黑键可奏面内；SUPPORTED：该局部指腹已贴近并追随运动黑键。** 上轮 required gap约0.464–0.748mm，未测到A5那样的持续分离。有限8mm指腹邻域/实际运动黑键面证据见JSON；不会预认Human错看，也不会把虚拟pad等同有受力面积的真实接触。摄像机/指尖与pad不同位置能解释悬空观感，但其为唯一原因仍UNKNOWN；需匹配俯视与侧斜Human复核。

出处：[RIGHT_HAND_MOTION_CAUSE_ANALYSIS.md](../research/audits/right_hand_articulation_contact_short_phrase_r1/RIGHT_HAND_MOTION_CAUSE_ANALYSIS.md)

> F♯5此前实际skin pad位于运动黑键抬高可奏面，gap0.464–0.748mm；有限指腹邻域closest gap约0.464–0.730mm。几何到位CONFIRMED，近接触跟随SUPPORTED，严重悬空NOT_CONFIRMED；摄像机是观感唯一原因UNKNOWN。没有先认定Human观察错误。

出处：[A5_FSHARP5_CONTACT_REVIEW.md](../research/audits/right_hand_articulation_contact_short_phrase_r1/A5_FSHARP5_CONTACT_REVIEW.md)

## 后续建议

> |10 是否扩展下一段|当前不建议扩展下一段：A5持键追随仍失败，且本轮原速自然度与双手协调尚需Human审核。 本轮STOP，不自动启动。|

出处：[DUAL_HAND_VISUAL_COORDINATION_REVIEW.md](../research/audits/right_hand_articulation_contact_short_phrase_r1/DUAL_HAND_VISUAL_COORDINATION_REVIEW.md)

## 原报告与关键代码

- [audits/right_hand_articulation_contact_short_phrase_r1/RIGHT_HAND_MOTION_CAUSE_ANALYSIS.md](../research/audits/right_hand_articulation_contact_short_phrase_r1/RIGHT_HAND_MOTION_CAUSE_ANALYSIS.md)
- [audits/right_hand_articulation_contact_short_phrase_r1/A5_FSHARP5_CONTACT_REVIEW.md](../research/audits/right_hand_articulation_contact_short_phrase_r1/A5_FSHARP5_CONTACT_REVIEW.md)
- [audits/right_hand_articulation_contact_short_phrase_r1/RIGHT_HAND_MOTION_IMPLEMENTATION.md](../research/audits/right_hand_articulation_contact_short_phrase_r1/RIGHT_HAND_MOTION_IMPLEMENTATION.md)
- [audits/right_hand_articulation_contact_short_phrase_r1/DUAL_HAND_VISUAL_COORDINATION_REVIEW.md](../research/audits/right_hand_articulation_contact_short_phrase_r1/DUAL_HAND_VISUAL_COORDINATION_REVIEW.md)
- [audits/right_hand_articulation_contact_short_phrase_r1/00_diagnose.py](../../src/legacy/audits/right_hand_articulation_contact_short_phrase_r1/00_diagnose.py)
- [audits/right_hand_articulation_contact_short_phrase_r1/01_lock.py](../../src/legacy/audits/right_hand_articulation_contact_short_phrase_r1/01_lock.py)
- [audits/right_hand_articulation_contact_short_phrase_r1/02_generate.py](../../src/legacy/audits/right_hand_articulation_contact_short_phrase_r1/02_generate.py)
- [audits/right_hand_articulation_contact_short_phrase_r1/03_scene.py](../../src/legacy/audits/right_hand_articulation_contact_short_phrase_r1/03_scene.py)
- [audits/right_hand_articulation_contact_short_phrase_r1/04_diagnostics.py](../../src/legacy/audits/right_hand_articulation_contact_short_phrase_r1/04_diagnostics.py)
- [audits/right_hand_articulation_contact_short_phrase_r1/05_render.py](../../src/legacy/audits/right_hand_articulation_contact_short_phrase_r1/05_render.py)
- [audits/right_hand_articulation_contact_short_phrase_r1/06_media.py](../../src/legacy/audits/right_hand_articulation_contact_short_phrase_r1/06_media.py)
- [audits/right_hand_articulation_contact_short_phrase_r1/07_finish.py](../../src/legacy/audits/right_hand_articulation_contact_short_phrase_r1/07_finish.py)
- [audits/right_hand_articulation_contact_short_phrase_r1/articulation_common.py](../../src/legacy/audits/right_hand_articulation_contact_short_phrase_r1/articulation_common.py)
- [audits/right_hand_articulation_contact_short_phrase_r1/right_motion.py](../../src/legacy/audits/right_hand_articulation_contact_short_phrase_r1/right_motion.py)

## 输入、输出与大型证据

该目录原始成员 56 项；拟公开身份记录 46 项。
- `audits/right_hand_articulation_contact_short_phrase_r1/evaluated.npz` → `hands-research-r1-selected-007.zip` / `payload/audits/right_hand_articulation_contact_short_phrase_r1/evaluated.npz`
- `audits/right_hand_articulation_contact_short_phrase_r1/RIGHT_HAND_ARTICULATION_CONTACT_DESIGN_ONLY_R1.blend` → `hands-research-r1-selected-007.zip` / `payload/audits/right_hand_articulation_contact_short_phrase_r1/RIGHT_HAND_ARTICULATION_CONTACT_DESIGN_ONLY_R1.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
