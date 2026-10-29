# audits/piano_hand_visual_first_short_phrase_validation_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> - 右手残差包含运动键目标、fixed/skin pad、完整皮肤净空、连续性和姿态正则。一次确定性least_squares，13次nfev、533次残差调用，约252.7s；收敛不表示接触成功。

出处：[SHORT_PHRASE_IMPLEMENTATION_REPORT.md](../research/audits/piano_hand_visual_first_short_phrase_validation_r1/SHORT_PHRASE_IMPLEMENTATION_REPORT.md)

> 原MIDI18音符、36 on/off事件与已有timeline逐项一致。正确目标键index=MIDI−21；所有required-contact样点实际skin pad的水平位置均在目标可奏区。实际键角与时间数组一致；全部原声部保留。按错键/漏键/错手没有证据，但A5的手-键持续按下表现失配导致整体 MUSIC_FUNCTIONAL_CORRECTNESS=FAIL。

出处：[SHORT_PHRASE_IMPLEMENTATION_REPORT.md](../research/audits/piano_hand_visual_first_short_phrase_validation_r1/SHORT_PHRASE_IMPLEMENTATION_REPORT.md)

## 技术路线

> 这是本轮右手白键压力轨迹/共同掌根适配不足的证据；不能据此断言冻结Rig必须修改，也不能断言换一种运动规划一定可解。此前左手29参数没有被自动泛化为右手五指联合掌腕规划。本轮未实施架构复评提出的求解器重构。

出处：[SHORT_PHRASE_IMPLEMENTATION_REPORT.md](../research/audits/piano_hand_visual_first_short_phrase_validation_r1/SHORT_PHRASE_IMPLEMENTATION_REPORT.md)

> |Q8 扩展潜力/未经验证|完整调度和重复系数复用可以实现，但本轮短句音乐功能失败，更多简单旋律的有效产品泛化NOT_ESTABLISHED。未验证跨手型、转指、跨区/掌根迁移、和弦/同手重叠、长段动作、自动指法或在线演奏。|

出处：[HUMAN_VISIBLE_PRODUCT_REVIEW.md](../research/audits/piano_hand_visual_first_short_phrase_validation_r1/HUMAN_VISIBLE_PRODUCT_REVIEW.md)

## 测试结论

> 2026-10-09 · 唯一 DESIGN_ONLY 候选 · FAIL_CLOSED · STOP

出处：[SHORT_PHRASE_IMPLEMENTATION_REPORT.md](../research/audits/piano_hand_visual_first_short_phrase_validation_r1/SHORT_PHRASE_IMPLEMENTATION_REPORT.md)

> 原MIDI18音符、36 on/off事件与已有timeline逐项一致。正确目标键index=MIDI−21；所有required-contact样点实际skin pad的水平位置均在目标可奏区。实际键角与时间数组一致；全部原声部保留。按错键/漏键/错手没有证据，但A5的手-键持续按下表现失配导致整体 MUSIC_FUNCTIONAL_CORRECTNESS=FAIL。

出处：[SHORT_PHRASE_IMPLEMENTATION_REPORT.md](../research/audits/piano_hand_visual_first_short_phrase_validation_r1/SHORT_PHRASE_IMPLEMENTATION_REPORT.md)

## 失败原因与证据边界

> 唯一候选整体 **FAIL_CLOSED**。`HUMAN_VISIBLE_QUALITY=HUMAN_PENDING`；代理发现真实可见阻断问题，不授予产品批准。

出处：[HUMAN_VISIBLE_PRODUCT_REVIEW.md](../research/audits/piano_hand_visual_first_short_phrase_validation_r1/HUMAN_VISIBLE_PRODUCT_REVIEW.md)

> |Q5 可见错键/悬空/穿键/跳变|阻断问题是右A5明显悬空；未发现实质错键、严重穿键或明显关节瞬跳。不得把未发现当作完整三角碰撞证明。|

出处：[HUMAN_VISIBLE_PRODUCT_REVIEW.md](../research/audits/piano_hand_visual_first_short_phrase_validation_r1/HUMAN_VISIBLE_PRODUCT_REVIEW.md)

## 后续建议

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 原报告与关键代码

- [audits/piano_hand_visual_first_short_phrase_validation_r1/SHORT_PHRASE_IMPLEMENTATION_REPORT.md](../research/audits/piano_hand_visual_first_short_phrase_validation_r1/SHORT_PHRASE_IMPLEMENTATION_REPORT.md)
- [audits/piano_hand_visual_first_short_phrase_validation_r1/HUMAN_VISIBLE_PRODUCT_REVIEW.md](../research/audits/piano_hand_visual_first_short_phrase_validation_r1/HUMAN_VISIBLE_PRODUCT_REVIEW.md)
- [audits/piano_hand_visual_first_short_phrase_validation_r1/SHORT_PHRASE_EVENT_AND_FINGERING.md](../research/audits/piano_hand_visual_first_short_phrase_validation_r1/SHORT_PHRASE_EVENT_AND_FINGERING.md)
- [audits/piano_hand_visual_first_short_phrase_validation_r1/00_verify_source.py](../../src/legacy/audits/piano_hand_visual_first_short_phrase_validation_r1/00_verify_source.py)
- [audits/piano_hand_visual_first_short_phrase_validation_r1/01_generate.py](../../src/legacy/audits/piano_hand_visual_first_short_phrase_validation_r1/01_generate.py)
- [audits/piano_hand_visual_first_short_phrase_validation_r1/02_scene.py](../../src/legacy/audits/piano_hand_visual_first_short_phrase_validation_r1/02_scene.py)
- [audits/piano_hand_visual_first_short_phrase_validation_r1/03_diagnostics.py](../../src/legacy/audits/piano_hand_visual_first_short_phrase_validation_r1/03_diagnostics.py)
- [audits/piano_hand_visual_first_short_phrase_validation_r1/04_render.py](../../src/legacy/audits/piano_hand_visual_first_short_phrase_validation_r1/04_render.py)
- [audits/piano_hand_visual_first_short_phrase_validation_r1/05_media.py](../../src/legacy/audits/piano_hand_visual_first_short_phrase_validation_r1/05_media.py)
- [audits/piano_hand_visual_first_short_phrase_validation_r1/06_finish.py](../../src/legacy/audits/piano_hand_visual_first_short_phrase_validation_r1/06_finish.py)
- [audits/piano_hand_visual_first_short_phrase_validation_r1/phrase_common.py](../../src/legacy/audits/piano_hand_visual_first_short_phrase_validation_r1/phrase_common.py)
- [audits/piano_hand_visual_first_short_phrase_validation_r1/verify_export_repair.py](../../src/legacy/audits/piano_hand_visual_first_short_phrase_validation_r1/verify_export_repair.py)

## 输入、输出与大型证据

该目录原始成员 48 项；拟公开身份记录 42 项。
- `audits/piano_hand_visual_first_short_phrase_validation_r1/evaluated.npz` → `hands-research-r1-selected-006.zip` / `payload/audits/piano_hand_visual_first_short_phrase_validation_r1/evaluated.npz`
- `audits/piano_hand_visual_first_short_phrase_validation_r1/SHORT_PHRASE_DESIGN_ONLY_R1.blend` → `hands-research-r1-selected-006.zip` / `payload/audits/piano_hand_visual_first_short_phrase_validation_r1/SHORT_PHRASE_DESIGN_ONLY_R1.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
