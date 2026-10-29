# audits/midi_driven_dual_hand_piano_performance_poc_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> |Q5 双手能按正确目标键演奏？|NO；虽目标音区与横向位置匹配，持续触键失败。|

出处：[MIDI_DRIVEN_DUAL_HAND_PIANO_PERFORMANCE_POC_R1_REPORT.md](../research/audits/midi_driven_dual_hand_piano_performance_poc_r1/MIDI_DRIVEN_DUAL_HAND_PIANO_PERFORMANCE_POC_R1_REPORT.md)

> 统一阶段：PREPARATION → 前100ms APPROACH → NOTE_ON时CONTACT目标 → 35ms KEY_PRESS → NOTE_OFF后70ms RELEASE → 回到home hover的 NEXT_NOTE_TRANSITION。音频释放包络240ms。原 timing没有吸附到帧。数学目标曲线连续，但**数值IK分支并未保证关节连续自然**：右手在展示时间2.608秒、食指中间关节出现最大21.817°/8.33ms跳变，就是当前失败，而不是用插值标签掩盖它。

出处：[MIDI_DRIVEN_DUAL_HAND_PIANO_PERFORMANCE_POC_R1_REPORT.md](../research/audits/midi_driven_dual_hand_piano_performance_poc_r1/MIDI_DRIVEN_DUAL_HAND_PIANO_PERFORMANCE_POC_R1_REPORT.md)

## 技术路线

> 每手一个共享掌位，以五个 home targets 一次规划 root XYZ/yaw；本候选 root 在片段内保持固定。Root 高度限定55–85mm，yaw ±12°。每指3个非负 palmar flexion + 基部 spread，无轴向 twist；长指上限75/95/65°，拇指40/55/55°，spread长指±28°/拇指±35°。这些是本次工程候选限制，不是人体活动范围认证。一次全局 home 求解后，按120Hz顺序局部IK，保存为同一新候选，没有重启参数搜索。

出处：[MIDI_DRIVEN_DUAL_HAND_PIANO_PERFORMANCE_POC_R1_REPORT.md](../research/audits/midi_driven_dual_hand_piano_performance_poc_r1/MIDI_DRIVEN_DUAL_HAND_PIANO_PERFORMANCE_POC_R1_REPORT.md)

> 允许的实现bug修复记录：候选原无材质槽时增加实例槽；评估函数补齐math/tolerance依赖；rest mesh坐标区域诊断改为实际世界坐标，避免把全部3300点误标为腕部；弱低音基频改用强谐波验证。上述修复均未重求解或改动第一次动作候选。渲染缓存重启没有改变材质、相机、采样质量或帧率。

出处：[MIDI_DRIVEN_DUAL_HAND_PIANO_PERFORMANCE_POC_R1_REPORT.md](../research/audits/midi_driven_dual_hand_piano_performance_poc_r1/MIDI_DRIVEN_DUAL_HAND_PIANO_PERFORMANCE_POC_R1_REPORT.md)

## 测试结论

> **MIDI_DRIVEN_PIANO_PERFORMANCE_POC_PARTIAL**。**PRODUCT_DEMO_PASS = NO**。**STOP — HUMAN REVIEW**。

出处：[MIDI_DRIVEN_DUAL_HAND_PIANO_PERFORMANCE_POC_R1_REPORT.md](../research/audits/midi_driven_dual_hand_piano_performance_poc_r1/MIDI_DRIVEN_DUAL_HAND_PIANO_PERFORMANCE_POC_R1_REPORT.md)

> 首次打通了官方 MIDI → 明确声部/候选指法 → 新程序化 Action → 琴键 → 真实钢琴采样音轨，但动作与接触质量未通过。PARTIAL 只表示执行链路和带声音交付成立，不表示产品演奏动作合格。没有继续调旧 PianoVAM root，也没有加载其非商业 Action。

出处：[MIDI_DRIVEN_DUAL_HAND_PIANO_PERFORMANCE_POC_R1_REPORT.md](../research/audits/midi_driven_dual_hand_piano_performance_poc_r1/MIDI_DRIVEN_DUAL_HAND_PIANO_PERFORMANCE_POC_R1_REPORT.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 原报告与关键代码

- [audits/midi_driven_dual_hand_piano_performance_poc_r1/MIDI_DRIVEN_DUAL_HAND_PIANO_PERFORMANCE_POC_R1_REPORT.md](../research/audits/midi_driven_dual_hand_piano_performance_poc_r1/MIDI_DRIVEN_DUAL_HAND_PIANO_PERFORMANCE_POC_R1_REPORT.md)
- [audits/midi_driven_dual_hand_piano_performance_poc_r1/SOURCE_AND_LICENSE_R1.md](../research/audits/midi_driven_dual_hand_piano_performance_poc_r1/SOURCE_AND_LICENSE_R1.md)
- [audits/midi_driven_dual_hand_piano_performance_poc_r1/source/PIANO_SAMPLE_LICENSE.md](../research/audits/midi_driven_dual_hand_piano_performance_poc_r1/source/PIANO_SAMPLE_LICENSE.md)
- [audits/midi_driven_dual_hand_piano_performance_poc_r1/01_source_timeline.py](../../src/legacy/audits/midi_driven_dual_hand_piano_performance_poc_r1/01_source_timeline.py)
- [audits/midi_driven_dual_hand_piano_performance_poc_r1/02_rig_probe.py](../../src/legacy/audits/midi_driven_dual_hand_piano_performance_poc_r1/02_rig_probe.py)
- [audits/midi_driven_dual_hand_piano_performance_poc_r1/03_motion_plan.py](../../src/legacy/audits/midi_driven_dual_hand_piano_performance_poc_r1/03_motion_plan.py)
- [audits/midi_driven_dual_hand_piano_performance_poc_r1/04_scene.py](../../src/legacy/audits/midi_driven_dual_hand_piano_performance_poc_r1/04_scene.py)
- [audits/midi_driven_dual_hand_piano_performance_poc_r1/05_audio.py](../../src/legacy/audits/midi_driven_dual_hand_piano_performance_poc_r1/05_audio.py)
- [audits/midi_driven_dual_hand_piano_performance_poc_r1/06_render.py](../../src/legacy/audits/midi_driven_dual_hand_piano_performance_poc_r1/06_render.py)
- [audits/midi_driven_dual_hand_piano_performance_poc_r1/07_evaluate.py](../../src/legacy/audits/midi_driven_dual_hand_piano_performance_poc_r1/07_evaluate.py)
- [audits/midi_driven_dual_hand_piano_performance_poc_r1/08_media.py](../../src/legacy/audits/midi_driven_dual_hand_piano_performance_poc_r1/08_media.py)
- [audits/midi_driven_dual_hand_piano_performance_poc_r1/09_finish.py](../../src/legacy/audits/midi_driven_dual_hand_piano_performance_poc_r1/09_finish.py)
- [audits/midi_driven_dual_hand_piano_performance_poc_r1/performance_core.py](../../src/legacy/audits/midi_driven_dual_hand_piano_performance_poc_r1/performance_core.py)

## 输入、输出与大型证据

该目录原始成员 2750 项；拟公开身份记录 60 项。
- `audits/midi_driven_dual_hand_piano_performance_poc_r1/evaluated_candidate.npz` → `hands-research-r1-selected-001.zip` / `payload/audits/midi_driven_dual_hand_piano_performance_poc_r1/evaluated_candidate.npz`
- `audits/midi_driven_dual_hand_piano_performance_poc_r1/MIDI_DRIVEN_DUAL_HAND_PIANO_PERFORMANCE_CANDIDATE_R1.blend` → `hands-research-r1-selected-001.zip` / `payload/audits/midi_driven_dual_hand_piano_performance_poc_r1/MIDI_DRIVEN_DUAL_HAND_PIANO_PERFORMANCE_CANDIDATE_R1.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
