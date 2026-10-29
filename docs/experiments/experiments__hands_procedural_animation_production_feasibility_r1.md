# experiments/hands_procedural_animation_production_feasibility_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> **结果：HUMAN_EDIT_REQUIRED。** 成功复用原 C1、制作了正常速度基线视频、生成一个独立单指修整 Action，并完成一次真实 Blender 全窗口复核。目标穿键有所减轻，但仍明显残留，且新增邻键侵入、退出段回退；机器验收 FAIL。因此没有渲染修整后视频，没有第二个候选。交付的是基线预览及从原 C1 准备的人工编辑副本，尚未完成可用于教学的新片段。

出处：[FINAL_PRODUCTION_FEASIBILITY.md](../research/experiments/hands_procedural_animation_production_feasibility_r1/FINAL_PRODUCTION_FEASIBILITY.md)

> 锁定唯一片段：**展示时间 4.4–5.6s，60fps 第 265–336 帧；主要目标为 4.916666667s、第 296 帧右手闲置无名指嵌入 C♯5（MIDI 73，键索引 52）**。没有选择 B02，也没有测试其他缺陷片段或其他 MIDI。无名指在整个片段中均不承担 ACTIVE/释放/准备触键任务，适合先尝试单个局部关节的制作编辑；不需要先启动掌腕或多指规划。

出处：[FINAL_PRODUCTION_FEASIBILITY.md](../research/experiments/hands_procedural_animation_production_feasibility_r1/FINAL_PRODUCTION_FEASIBILITY.md)

## 技术路线

> 日期：2026-10-15（Asia/Shanghai）。路线 C 的一次真实制作实验，已完成并停止。

出处：[FINAL_PRODUCTION_FEASIBILITY.md](../research/experiments/hands_procedural_animation_production_feasibility_r1/FINAL_PRODUCTION_FEASIBILITY.md)

> 五次包络的值、一阶和二阶修正在两端为零，理论新增屈曲速度峰值 56.25°/s、横展 15°/s。烘焙后的 quaternion 曲线仍须单独检查，不能把包络光滑等同于最终动作处处光滑。策略和门禁在候选写入前保存为 `STRATEGY_LOCK.json`（链接见原报告）。

出处：[FINAL_PRODUCTION_FEASIBILITY.md](../research/experiments/hands_procedural_animation_production_feasibility_r1/FINAL_PRODUCTION_FEASIBILITY.md)

## 测试结论

> **结果：HUMAN_EDIT_REQUIRED。** 成功复用原 C1、制作了正常速度基线视频、生成一个独立单指修整 Action，并完成一次真实 Blender 全窗口复核。目标穿键有所减轻，但仍明显残留，且新增邻键侵入、退出段回退；机器验收 FAIL。因此没有渲染修整后视频，没有第二个候选。交付的是基线预览及从原 C1 准备的人工编辑副本，尚未完成可用于教学的新片段。

出处：[FINAL_PRODUCTION_FEASIBILITY.md](../research/experiments/hands_procedural_animation_production_feasibility_r1/FINAL_PRODUCTION_FEASIBILITY.md)

> MACHINE_VALIDATION = FAIL

出处：[FINAL_PRODUCTION_FEASIBILITY.md](../research/experiments/hands_procedural_animation_production_feasibility_r1/FINAL_PRODUCTION_FEASIBILITY.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

> 5. 在第292、296、316帧建立少量视觉姿态，尝试更小的 MCP 让位，保留原弧形和手指相对位置。屈曲工程轴不等同于原生 Euler X，使用现有旋转 gizmo和实际皮肤观察，不平移骨骼、不抬腕、不改 rest/蒙皮。此次自动 −7.5°/−2° 组合已经失败，不应直接再施加。若单MCP无法兼顾邻键，可由Human将少量曲度分配到 `RING_PIP_R`/`RING_DIP_R`；这只是人工建议，未经验证。

出处：[FINAL_PRODUCTION_FEASIBILITY.md](../research/experiments/hands_procedural_animation_production_feasibility_r1/FINAL_PRODUCTION_FEASIBILITY.md)

> 从首个可核时钟（08:05:54）到初次交付统计（08:16:33）约 **10分39秒**；包含读取、脚本适配、一次编辑、完整复核及普通软件错误处理，之后补充了密集键人工说明、保存并重开最终交接副本。最终收据给出交付时实际总墙钟；整体在建议45分钟内。最初几次读取发生在首个时钟前，没有单独计时，不虚构其秒数。

出处：[FINAL_PRODUCTION_FEASIBILITY.md](../research/experiments/hands_procedural_animation_production_feasibility_r1/FINAL_PRODUCTION_FEASIBILITY.md)

## 原报告与关键代码

- [experiments/hands_procedural_animation_production_feasibility_r1/FINAL_PRODUCTION_FEASIBILITY.md](../research/experiments/hands_procedural_animation_production_feasibility_r1/FINAL_PRODUCTION_FEASIBILITY.md)
- [experiments/hands_procedural_animation_production_feasibility_r1/baseline_previews.py](../../src/legacy/experiments/hands_procedural_animation_production_feasibility_r1/baseline_previews.py)
- [experiments/hands_procedural_animation_production_feasibility_r1/common.py](../../src/legacy/experiments/hands_procedural_animation_production_feasibility_r1/common.py)
- [experiments/hands_procedural_animation_production_feasibility_r1/finalize_handoff_instructions.py](../../src/legacy/experiments/hands_procedural_animation_production_feasibility_r1/finalize_handoff_instructions.py)
- [experiments/hands_procedural_animation_production_feasibility_r1/lock_and_edit.py](../../src/legacy/experiments/hands_procedural_animation_production_feasibility_r1/lock_and_edit.py)
- [experiments/hands_procedural_animation_production_feasibility_r1/lock_and_edit_before_handle_fix.py](../../src/legacy/experiments/hands_procedural_animation_production_feasibility_r1/lock_and_edit_before_handle_fix.py)
- [experiments/hands_procedural_animation_production_feasibility_r1/prepare_baseline.py](../../src/legacy/experiments/hands_procedural_animation_production_feasibility_r1/prepare_baseline.py)
- [experiments/hands_procedural_animation_production_feasibility_r1/prepare_human_handoff.py](../../src/legacy/experiments/hands_procedural_animation_production_feasibility_r1/prepare_human_handoff.py)
- [experiments/hands_procedural_animation_production_feasibility_r1/summarize_delivery.py](../../src/legacy/experiments/hands_procedural_animation_production_feasibility_r1/summarize_delivery.py)
- [experiments/hands_procedural_animation_production_feasibility_r1/validate_once.py](../../src/legacy/experiments/hands_procedural_animation_production_feasibility_r1/validate_once.py)
- [experiments/hands_procedural_animation_production_feasibility_r1/verify_delivery.py](../../src/legacy/experiments/hands_procedural_animation_production_feasibility_r1/verify_delivery.py)
- [experiments/hands_procedural_animation_production_feasibility_r1/verify_handoff_readback.py](../../src/legacy/experiments/hands_procedural_animation_production_feasibility_r1/verify_handoff_readback.py)

## 输入、输出与大型证据

该目录原始成员 68 项；拟公开身份记录 51 项。
- `experiments/hands_procedural_animation_production_feasibility_r1/ACTUAL_LOCAL_SKIN_QC.npz` → `hands-research-r1-selected-014.zip` / `payload/experiments/hands_procedural_animation_production_feasibility_r1/ACTUAL_LOCAL_SKIN_QC.npz`
- `experiments/hands_procedural_animation_production_feasibility_r1/C_RING_SINGLE_CANDIDATE_NOT_APPROVED.blend` → `hands-research-r1-selected-014.zip` / `payload/experiments/hands_procedural_animation_production_feasibility_r1/C_RING_SINGLE_CANDIDATE_NOT_APPROVED.blend`
- `experiments/hands_procedural_animation_production_feasibility_r1/HUMAN_RING_EDIT_HANDOFF.blend` → `hands-research-r1-selected-014.zip` / `payload/experiments/hands_procedural_animation_production_feasibility_r1/HUMAN_RING_EDIT_HANDOFF.blend`
- `experiments/hands_procedural_animation_production_feasibility_r1/HUMAN_RING_EDIT_HANDOFF_READY.blend` → `hands-research-r1-selected-014.zip` / `payload/experiments/hands_procedural_animation_production_feasibility_r1/HUMAN_RING_EDIT_HANDOFF_READY.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
