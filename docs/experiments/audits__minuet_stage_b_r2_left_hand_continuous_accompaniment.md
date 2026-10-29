# audits/minuet_stage_b_r2_left_hand_continuous_accompaniment

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 所有新增均在本目录。`left_chord_base.py`受控复制B1实际L FK、多目标/共享root/运动键面基础，仅重命名基类；源文件未改。`left_continuous_motion.py`增加事件感知的目标分量：当前持键仍单一精确目标；已释放/准备指在旧恢复与下一键之间连续交接，避免恢复优先遮住下一准备和重新起一个中性pad目标。指法、音高或曲名不参与姿态特例。

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/IMPLEMENTATION_REPORT.md)

> 有限预检一批6个静态任务和正式左皮肤回读，包含持和弦准备无名指、边界4个机械接触任务和食指C4新单音；0静态Action/0保存候选。当前所有姿态在原冻结Rig上实际可达，不据此批准自然度。保存重开候选pad/FK最大差约0.00092mm，实际键几何差约0.000009mm；四静态core、手结构和88键网格保持。

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/IMPLEMENTATION_REPORT.md)

## 技术路线

> **FAIL_CLOSED：完整单候选与技术功能已交付，自然闲置手型尚不足。** 失败来自正常可见开手/伸直，不是因为历史3mm阈值或求解失败。保留原速5.95s真实证据，不生成第二候选。

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/IMPLEMENTATION_REPORT.md)

> 同一框架扩展为7个原事件、所有5指的连续流；时间局部idle软策略复用既有LEFT_IDLE_INDEX/RING域，主动/准备时连续让位给关节可行性。这个扩展仍不完整：闲置拇指和小指的home/形态组织不足，长音单指时持续外展已暴露。不能将接口通用误称自然演奏泛化通过。

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/IMPLEMENTATION_REPORT.md)

## 测试结论

> **FAIL_CLOSED：完整单候选与技术功能已交付，自然闲置手型尚不足。** 失败来自正常可见开手/伸直，不是因为历史3mm阈值或求解失败。保留原速5.95s真实证据，不生成第二候选。

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/IMPLEMENTATION_REPORT.md)

> |Q3 和弦衔接自然吗|技术保持和弦与A3交接接触、同步和4机械任务，整体自然性未通过产品预检；后续单音长持键闲置手型明显张开，状态PARTIAL。|

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/IMPLEMENTATION_REPORT.md)

## 失败原因与证据边界

> |Q7 可见异常吗|正常视角可见闲置拇指/小指持续伸展/外展，此为产品阻断。未发现严重主动错键或脱离，轻微target-B3几何进入另为WARN。无“所有异常皆不存在”声明。|

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/IMPLEMENTATION_REPORT.md)

> 原候选五指G3–D4键中心跨度约95.8mm，材料没有需要大幅寄存器换位的结构。跨度数值仅支持可见开手观察，不是新的毫米级自然度门槛。正常原帧的闲置外展/伸直是产品阻断；最终Human仍可观看真实视频做自己的判断。

出处：[HUMAN_VISIBLE_REVIEW.md](../research/audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/HUMAN_VISIBLE_REVIEW.md)

## 后续建议

> 所有新增均在本目录。`left_chord_base.py`受控复制B1实际L FK、多目标/共享root/运动键面基础，仅重命名基类；源文件未改。`left_continuous_motion.py`增加事件感知的目标分量：当前持键仍单一精确目标；已释放/准备指在旧恢复与下一键之间连续交接，避免恢复优先遮住下一准备和重新起一个中性pad目标。指法、音高或曲名不参与姿态特例。

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/IMPLEMENTATION_REPORT.md)

> |Q3 和弦衔接自然吗|技术保持和弦与A3交接接触、同步和4机械任务，整体自然性未通过产品预检；后续单音长持键闲置手型明显张开，状态PARTIAL。|

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/IMPLEMENTATION_REPORT.md)

## 原报告与关键代码

- [audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/IMPLEMENTATION_REPORT.md)
- [audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/HUMAN_VISIBLE_REVIEW.md](../research/audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/HUMAN_VISIBLE_REVIEW.md)
- [audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/LEFT_HAND_FOUR_BAR_EVENT_PLAN.md](../research/audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/LEFT_HAND_FOUR_BAR_EVENT_PLAN.md)
- [audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/LEFT_HAND_CONTINUOUS_MOTION_DESIGN.md](../research/audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/LEFT_HAND_CONTINUOUS_MOTION_DESIGN.md)
- [audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/00_scope.py](../../src/legacy/audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/00_scope.py)
- [audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/01_preflight.py](../../src/legacy/audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/01_preflight.py)
- [audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/02_static_readback.py](../../src/legacy/audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/02_static_readback.py)
- [audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/03_generate.py](../../src/legacy/audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/03_generate.py)
- [audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/04_scene.py](../../src/legacy/audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/04_scene.py)
- [audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/05_diagnostics.py](../../src/legacy/audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/05_diagnostics.py)
- [audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/06_render.py](../../src/legacy/audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/06_render.py)
- [audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/07_audio.py](../../src/legacy/audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/07_audio.py)
- [audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/08_media.py](../../src/legacy/audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/08_media.py)
- [audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/09_framing_verify.py](../../src/legacy/audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/09_framing_verify.py)
- [audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/09_overhead_framing_repair.py](../../src/legacy/audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/09_overhead_framing_repair.py)
- [audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/09_posture_evidence.py](../../src/legacy/audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/09_posture_evidence.py)

## 输入、输出与大型证据

该目录原始成员 84 项；拟公开身份记录 71 项。
- `audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/evaluated.npz` → `hands-research-r1-selected-002.zip` / `payload/audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/evaluated.npz`
- `audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/STAGE_B_R2_LEFT_CONTINUOUS_DESIGN_ONLY.blend` → `hands-research-r1-selected-002.zip` / `payload/audits/minuet_stage_b_r2_left_hand_continuous_accompaniment/STAGE_B_R2_LEFT_CONTINUOUS_DESIGN_ONLY.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
