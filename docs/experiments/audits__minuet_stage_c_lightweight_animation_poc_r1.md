# audits/minuet_stage_c_lightweight_animation_poc_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> - NOTE_ON/OFF、指法、目标键、MIDI、13 个活动键 Action 和原双手音频保持。所有非右手 rig 的对象 Action 完整 payload/slot/name 一致；琴键重复音的部分回弹/再按下直接保留原曲线。

出处：[MOTION_AND_MUSIC_PRESERVATION.md](../research/audits/minuet_stage_c_lightweight_animation_poc_r1/MOTION_AND_MUSIC_PRESERVATION.md)

> - 实际 Blender 60 Hz、事件边界和历史诊断点共 377 个采样；主动指腹新旧最大差 0.000000 mm，横向目标偏差 0 mm；源与新接触间隙同为约 −0.829 至 2.046 mm（包括敲击/交接边界）。没有新增严重脱键或错键证据。

出处：[MOTION_AND_MUSIC_PRESERVATION.md](../research/audits/minuet_stage_c_lightweight_animation_poc_r1/MOTION_AND_MUSIC_PRESERVATION.md)

## 技术路线

> 没有这样的证据。本轮严格保留主动姿态/保护区、使用近似凸包且修正幅度有限；失败只能界定本策略边界，不能证明重型方法必要。没有继续尝试。

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_c_lightweight_animation_poc_r1/FINAL_ANSWERS.md)

> 唯一策略 CONTACT_GUIDED_LIGHTWEIGHT_ANIMATION，唯一动态候选，产品结果 FAIL_CLOSED。实际采用有限坐标探测和 FK，没有调用 scipy.optimize、IK 非线性优化器或 R6 轨迹求解器。

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_c_lightweight_animation_poc_r1/IMPLEMENTATION_REPORT.md)

## 测试结论

> 唯一策略 CONTACT_GUIDED_LIGHTWEIGHT_ANIMATION，唯一动态候选，产品结果 FAIL_CLOSED。实际采用有限坐标探测和 FK，没有调用 scipy.optimize、IK 非线性优化器或 R6 轨迹求解器。

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_c_lightweight_animation_poc_r1/IMPLEMENTATION_REPORT.md)

> | 检查 | C1 → 轻量 R1 | 结论 |

出处：[BEFORE_AFTER_VISUAL_REVIEW.md](../research/audits/minuet_stage_c_lightweight_animation_poc_r1/BEFORE_AFTER_VISUAL_REVIEW.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 原报告与关键代码

- [audits/minuet_stage_c_lightweight_animation_poc_r1/FINAL_ANSWERS.md](../research/audits/minuet_stage_c_lightweight_animation_poc_r1/FINAL_ANSWERS.md)
- [audits/minuet_stage_c_lightweight_animation_poc_r1/IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_c_lightweight_animation_poc_r1/IMPLEMENTATION_REPORT.md)
- [audits/minuet_stage_c_lightweight_animation_poc_r1/BEFORE_AFTER_VISUAL_REVIEW.md](../research/audits/minuet_stage_c_lightweight_animation_poc_r1/BEFORE_AFTER_VISUAL_REVIEW.md)
- [audits/minuet_stage_c_lightweight_animation_poc_r1/LIGHTWEIGHT_ANIMATION_DESIGN.md](../research/audits/minuet_stage_c_lightweight_animation_poc_r1/LIGHTWEIGHT_ANIMATION_DESIGN.md)
- [audits/minuet_stage_c_lightweight_animation_poc_r1/MOTION_AND_MUSIC_PRESERVATION.md](../research/audits/minuet_stage_c_lightweight_animation_poc_r1/MOTION_AND_MUSIC_PRESERVATION.md)
- [audits/minuet_stage_c_lightweight_animation_poc_r1/bake_validate.py](../../src/legacy/audits/minuet_stage_c_lightweight_animation_poc_r1/bake_validate.py)
- [audits/minuet_stage_c_lightweight_animation_poc_r1/check_asset_identity.py](../../src/legacy/audits/minuet_stage_c_lightweight_animation_poc_r1/check_asset_identity.py)
- [audits/minuet_stage_c_lightweight_animation_poc_r1/check_new_neighbors.py](../../src/legacy/audits/minuet_stage_c_lightweight_animation_poc_r1/check_new_neighbors.py)
- [audits/minuet_stage_c_lightweight_animation_poc_r1/finish.py](../../src/legacy/audits/minuet_stage_c_lightweight_animation_poc_r1/finish.py)
- [audits/minuet_stage_c_lightweight_animation_poc_r1/generate_once.py](../../src/legacy/audits/minuet_stage_c_lightweight_animation_poc_r1/generate_once.py)
- [audits/minuet_stage_c_lightweight_animation_poc_r1/media.py](../../src/legacy/audits/minuet_stage_c_lightweight_animation_poc_r1/media.py)
- [audits/minuet_stage_c_lightweight_animation_poc_r1/prepare.py](../../src/legacy/audits/minuet_stage_c_lightweight_animation_poc_r1/prepare.py)
- [audits/minuet_stage_c_lightweight_animation_poc_r1/render.py](../../src/legacy/audits/minuet_stage_c_lightweight_animation_poc_r1/render.py)
- [audits/minuet_stage_c_lightweight_animation_poc_r1/summarize.py](../../src/legacy/audits/minuet_stage_c_lightweight_animation_poc_r1/summarize.py)
- [audits/minuet_stage_c_lightweight_animation_poc_r1/validate_existing.py](../../src/legacy/audits/minuet_stage_c_lightweight_animation_poc_r1/validate_existing.py)

## 输入、输出与大型证据

该目录原始成员 1184 项；拟公开身份记录 115 项。
- `audits/minuet_stage_c_lightweight_animation_poc_r1/STAGE_C_LIGHTWEIGHT_ANIMATION_POC_R1_DESIGN_ONLY.blend` → `hands-research-r1-selected-002.zip` / `payload/audits/minuet_stage_c_lightweight_animation_poc_r1/STAGE_C_LIGHTWEIGHT_ANIMATION_POC_R1_DESIGN_ONLY.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
