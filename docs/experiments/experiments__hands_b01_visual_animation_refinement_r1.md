# experiments/hands_b01_visual_animation_refinement_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 实际对照视频为 **60fps、51帧、0.85秒、1×**，同一时间轴、相机和尺度。左右都从原1280×720机位画面取相同 `[x=480,y=0,w=640,h=720]` 右手区域，无目标手指裁切；顶部另加44像素标题，明确标注 `NOT_APPROVED`，没有覆盖手指。原WAV按0.90–1.75秒截取同步音频，最终音视频均从0开始、均为0.85秒；解码音频与对应原WAV的零延迟相关约0.99873。完整解码、帧数和时长检查通过。该视频是诊断对照，不能当成正式教学视频。

出处：[FINAL_B01_VISUAL_REVIEW.md](../research/experiments/hands_b01_visual_animation_refinement_r1/FINAL_B01_VISUAL_REVIEW.md)

> 沿用原接触0.03mm横向、绝对gap≤3mm和合法可奏域；原关节域，数值域容差0.002°；新增校正角速度≤180°/s；非目标键顶点回退采用“新深度>0.5mm且比同刻原C1增加>0.02mm”，面内新侵入/增长和新增面对另判。没有放宽门禁，也没有以历史穿模为理由拒绝制作诊断视频。

出处：[FINAL_B01_VISUAL_REVIEW.md](../research/experiments/hands_b01_visual_animation_refinement_r1/FINAL_B01_VISUAL_REVIEW.md)

## 技术路线

> 本轮只采用一种策略：以原C1为底，按准备、持键交接、释放阶段编排少量协同姿态增量，以五次平滑曲线连接，再写入复制Action。修改骨骼为：

出处：[FINAL_B01_VISUAL_REVIEW.md](../research/experiments/hands_b01_visual_animation_refinement_r1/FINAL_B01_VISUAL_REVIEW.md)

> 策略锁定在 `STRATEGY_LOCK.json`，实际写入及关键姿态在 `EDIT_RECEIPT.json`；只有一次编辑、一个保存候选，没有改角度重试。

出处：[FINAL_B01_VISUAL_REVIEW.md](../research/experiments/hands_b01_visual_animation_refinement_r1/FINAL_B01_VISUAL_REVIEW.md)

## 测试结论

> 日期：2026-10-15（Asia/Shanghai）。**RESULT = GENERATED_WITH_DEFECTS；B01_MACHINE_VALIDATION = FAIL。**

出处：[FINAL_B01_VISUAL_REVIEW.md](../research/experiments/hands_b01_visual_animation_refinement_r1/FINAL_B01_VISUAL_REVIEW.md)

> **D、E．真实机器验收：有收益，仍FAIL**

出处：[FINAL_B01_VISUAL_REVIEW.md](../research/experiments/hands_b01_visual_animation_refinement_r1/FINAL_B01_VISUAL_REVIEW.md)

## 失败原因与证据边界

> **失败原因属于本次动作，不是工具链阻断。** 关键姿态之间，原中指MCP快速靠近0°，叠加尚未退出的负修正导致中段越界；准备末段的空间姿态也让无名指在正式起音前进入C5。少量关键姿态看起来合理，不保证其间全部域、邻键、释放回接共同成立。没有证据证明必须改掌腕或第三指，也没有证据证明冻结Rig不可行。本轮不把这些动作失败当普通Bug继续修角度。

出处：[FINAL_B01_VISUAL_REVIEW.md](../research/experiments/hands_b01_visual_animation_refinement_r1/FINAL_B01_VISUAL_REVIEW.md)

## 后续建议

> 编辑支持为 **0.900000–1.705713秒**，检查/预览为 **0.90–1.75秒**。原MIDI中，中指R03 B4为1.207142–1.4214275秒，无名指R04 C5为1.4214275–1.635713秒；原40ms释放随键分别延续到1.4614275、1.675713秒。编辑退出选在C5释放之后，而不是在建议1.60秒处截断仍在持键的无名指。

出处：[FINAL_B01_VISUAL_REVIEW.md](../research/experiments/hands_b01_visual_animation_refinement_r1/FINAL_B01_VISUAL_REVIEW.md)

> 到阶段汇总时墙钟为 **16分49秒**；其余时间包括原始证据读取、脚本适配、姿态编排、逐帧视觉观察、软件修复及报告。最终交付墙钟另记 `DELIVERY_RECEIPT.json`，不把3秒脚本运行时冒称整个编辑工作量。总体在建议45分钟内。Human未实施任何人工编辑，不编造人工耗时。

出处：[FINAL_B01_VISUAL_REVIEW.md](../research/experiments/hands_b01_visual_animation_refinement_r1/FINAL_B01_VISUAL_REVIEW.md)

## 原报告与关键代码

- [experiments/hands_b01_visual_animation_refinement_r1/FINAL_B01_VISUAL_REVIEW.md](../research/experiments/hands_b01_visual_animation_refinement_r1/FINAL_B01_VISUAL_REVIEW.md)
- [experiments/hands_b01_visual_animation_refinement_r1/baseline_b01.py](../../src/legacy/experiments/hands_b01_visual_animation_refinement_r1/baseline_b01.py)
- [experiments/hands_b01_visual_animation_refinement_r1/edit_b01_once.py](../../src/legacy/experiments/hands_b01_visual_animation_refinement_r1/edit_b01_once.py)
- [experiments/hands_b01_visual_animation_refinement_r1/fix_local_audio_mux.py](../../src/legacy/experiments/hands_b01_visual_animation_refinement_r1/fix_local_audio_mux.py)
- [experiments/hands_b01_visual_animation_refinement_r1/local_comparison.py](../../src/legacy/experiments/hands_b01_visual_animation_refinement_r1/local_comparison.py)
- [experiments/hands_b01_visual_animation_refinement_r1/render_local.py](../../src/legacy/experiments/hands_b01_visual_animation_refinement_r1/render_local.py)
- [experiments/hands_b01_visual_animation_refinement_r1/summarize_result.py](../../src/legacy/experiments/hands_b01_visual_animation_refinement_r1/summarize_result.py)
- [experiments/hands_b01_visual_animation_refinement_r1/validate_b01_before_triangulation_fix.py](../../src/legacy/experiments/hands_b01_visual_animation_refinement_r1/validate_b01_before_triangulation_fix.py)
- [experiments/hands_b01_visual_animation_refinement_r1/validate_b01_once.py](../../src/legacy/experiments/hands_b01_visual_animation_refinement_r1/validate_b01_once.py)
- [experiments/hands_b01_visual_animation_refinement_r1/verify_candidate_readback.py](../../src/legacy/experiments/hands_b01_visual_animation_refinement_r1/verify_candidate_readback.py)
- [experiments/hands_b01_visual_animation_refinement_r1/verify_delivery.py](../../src/legacy/experiments/hands_b01_visual_animation_refinement_r1/verify_delivery.py)

## 输入、输出与大型证据

该目录原始成员 110 项；拟公开身份记录 97 项。
- `experiments/hands_b01_visual_animation_refinement_r1/ACTUAL_B01_SKIN_QC.npz` → `hands-research-r1-selected-008.zip` / `payload/experiments/hands_b01_visual_animation_refinement_r1/ACTUAL_B01_SKIN_QC.npz`
- `experiments/hands_b01_visual_animation_refinement_r1/B01_MULTIJOIN_SINGLE_CANDIDATE_NOT_APPROVED.blend` → `hands-research-r1-selected-008.zip` / `payload/experiments/hands_b01_visual_animation_refinement_r1/B01_MULTIJOIN_SINGLE_CANDIDATE_NOT_APPROVED.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
