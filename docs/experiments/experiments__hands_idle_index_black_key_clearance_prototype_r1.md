# experiments/hands_idle_index_black_key_clearance_prototype_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 27 项受保护/实际读取输入的前后 SHA256 全部一致：`PROTECTED_AFTER_AND_SHA256_RECEIPT.json`（链接见原报告）。原 C1、双方冻结 baseline、正式 MIDI、源指法/时间表、琴键表/marker/Rig记录、既有验收 policy、B01 失败候选/证据与前轮诊断均保留；原 C1 内嵌全部键 Action、rest Rig、顶点/面、蒙皮权重和 corrective driver 摘要亦保持。本收据不是对无关历史目录的大规模递归审计。独立 piano 目录没有扫描、读取或运行；旧脚本仅选择已读过的纯辅助函数，未执行历史任务入口或跟随外部项目路径。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_idle_index_black_key_clearance_prototype_r1/TECHNICAL_REPORT.md)

> 27 项受保护/实际读取输入的前后 SHA256 全部一致：`PROTECTED_AFTER_AND_SHA256_RECEIPT.json`（链接见原报告）。原 C1、双方冻结 baseline、正式 MIDI、源指法/时间表、琴键表/marker/Rig记录、既有验收 policy、B01 失败候选/证据与前轮诊断均保留；原 C1 内嵌全部键 Action、rest Rig、顶点/面、蒙皮权重和 corrective driver 摘要亦保持。本收据不是对无关历史目录的大规模递归审计。独立 piano 目录没有扫描、读取或运行；旧脚本仅选择已读过的纯辅助函数，未执行历史任务入口或跟随外部项目路径。

出处：[TECHNICAL_REPORT_PRE_AUDIO_VERIFICATION.md](../research/experiments/hands_idle_index_black_key_clearance_prototype_r1/TECHNICAL_REPORT_PRE_AUDIO_VERIFICATION.md)

## 技术路线

> 实际策略：从原 C1 的 LBS/corrective 后食指皮肤三角面，与原 Action 驱动黑键网格的保守 3mm AABB 邻近关系检测威胁区间。在 IDLE 内以 MCP 伸展抬指，配合 PIP/DIP 少量屈曲。A 静态探针增量为 −10/+4/+2°，B 为 −16/+6/+3°，展指不主动调整，按原合法域裁剪。仅 B 制成时间候选；没有第三组配置、IK、全手求解或逐音特判。两个指定时刻不参与触发条件，音名也不参与姿态选择。详见 `STRATEGY.md`（链接见原报告） 与 `STRATEGY_AND_ENVELOPE.json`（链接见原报告）。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_idle_index_black_key_clearance_prototype_r1/TECHNICAL_REPORT.md)

> 保存后亚帧核查发现烘焙实现缺陷：浮点时间网格遗漏精确 3.35s 端点，原关键帧值又使用网格插值，导致 3.35s 最大皮肤偏差 0.111793mm，至 3.36s 才恢复；1.247142s RELEASE 退出点偏差 0.016292mm。PREPARE 起点和 A4 NOTE_ON 的真实皮肤偏差为 0。故“严格只在 IDLE 生效并完整归零”尚未闭合。此缺陷由本次烘焙引入，不归咎原 C1。保留原候选及证据，没有追加导出修复或第三参数配置。见 `TRANSITION_SUBFRAME_CHECK.json`（链接见原报告）、`BAKE_BOUNDARY_DIAGNOSIS.json`（链接见原报告）。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_idle_index_black_key_clearance_prototype_r1/TECHNICAL_REPORT.md)

## 测试结论

> 结果：**PARTIAL**。2026-10-15 21:27:37 +08:00。同一套局部姿态机制改善两个窗口，但真实碰撞仍在，且出现既有侵入加深及烘焙边界偏差。候选仅供失败/部分改善证据与 Human Review，不能合并原 C1。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_idle_index_black_key_clearance_prototype_r1/TECHNICAL_REPORT.md)

> 右手 16 音 ON/HOLD/OFF前1ms 共 **48/48** 原合同接触 PASS；最大活动 pad 位移 0.000059721mm。全部 23 音时钟、原 MIDI/指法和键 Action 由文件 SHA 与未编辑 Action payload 一致性保持。A4 准备与实际触键保持；原 C1 其他历史缺陷不宣称已修复。三根食指骨的改动通过原有混合权重传至拇指 ROI，最大皮肤位移 0.587362mm；中/无名/小指 ROI 位移均为 0，拇指骨曲线不变，pad 保持。所有这类真实变动面均参与新增碰撞对照。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_idle_index_black_key_clearance_prototype_r1/TECHNICAL_REPORT.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 原报告与关键代码

- [experiments/hands_idle_index_black_key_clearance_prototype_r1/TECHNICAL_REPORT.md](../research/experiments/hands_idle_index_black_key_clearance_prototype_r1/TECHNICAL_REPORT.md)
- [experiments/hands_idle_index_black_key_clearance_prototype_r1/TECHNICAL_REPORT_PRE_AUDIO_VERIFICATION.md](../research/experiments/hands_idle_index_black_key_clearance_prototype_r1/TECHNICAL_REPORT_PRE_AUDIO_VERIFICATION.md)
- [experiments/hands_idle_index_black_key_clearance_prototype_r1/STRATEGY.md](../research/experiments/hands_idle_index_black_key_clearance_prototype_r1/STRATEGY.md)
- [experiments/hands_idle_index_black_key_clearance_prototype_r1/HUMAN_REVIEW.md](../research/experiments/hands_idle_index_black_key_clearance_prototype_r1/HUMAN_REVIEW.md)
- [experiments/hands_idle_index_black_key_clearance_prototype_r1/HUMAN_REVIEW_PRE_AUDIO_VERIFICATION.md](../research/experiments/hands_idle_index_black_key_clearance_prototype_r1/HUMAN_REVIEW_PRE_AUDIO_VERIFICATION.md)
- [experiments/hands_idle_index_black_key_clearance_prototype_r1/build.py](../../src/legacy/experiments/hands_idle_index_black_key_clearance_prototype_r1/build.py)
- [experiments/hands_idle_index_black_key_clearance_prototype_r1/extend_media.py](../../src/legacy/experiments/hands_idle_index_black_key_clearance_prototype_r1/extend_media.py)
- [experiments/hands_idle_index_black_key_clearance_prototype_r1/facts.py](../../src/legacy/experiments/hands_idle_index_black_key_clearance_prototype_r1/facts.py)
- [experiments/hands_idle_index_black_key_clearance_prototype_r1/finalize.py](../../src/legacy/experiments/hands_idle_index_black_key_clearance_prototype_r1/finalize.py)
- [experiments/hands_idle_index_black_key_clearance_prototype_r1/final_checks.py](../../src/legacy/experiments/hands_idle_index_black_key_clearance_prototype_r1/final_checks.py)
- [experiments/hands_idle_index_black_key_clearance_prototype_r1/geometry.py](../../src/legacy/experiments/hands_idle_index_black_key_clearance_prototype_r1/geometry.py)
- [experiments/hands_idle_index_black_key_clearance_prototype_r1/inspect_bake.py](../../src/legacy/experiments/hands_idle_index_black_key_clearance_prototype_r1/inspect_bake.py)
- [experiments/hands_idle_index_black_key_clearance_prototype_r1/make_media.py](../../src/legacy/experiments/hands_idle_index_black_key_clearance_prototype_r1/make_media.py)
- [experiments/hands_idle_index_black_key_clearance_prototype_r1/probe.py](../../src/legacy/experiments/hands_idle_index_black_key_clearance_prototype_r1/probe.py)
- [experiments/hands_idle_index_black_key_clearance_prototype_r1/render.py](../../src/legacy/experiments/hands_idle_index_black_key_clearance_prototype_r1/render.py)
- [experiments/hands_idle_index_black_key_clearance_prototype_r1/repair_audio_delivery.py](../../src/legacy/experiments/hands_idle_index_black_key_clearance_prototype_r1/repair_audio_delivery.py)
- [experiments/hands_idle_index_black_key_clearance_prototype_r1/support.py](../../src/legacy/experiments/hands_idle_index_black_key_clearance_prototype_r1/support.py)

## 输入、输出与大型证据

该目录原始成员 774 项；拟公开身份记录 595 项。
- `experiments/hands_idle_index_black_key_clearance_prototype_r1/BASELINE_LOCAL_SAMPLES.npz` → `hands-research-r1-selected-012.zip` / `payload/experiments/hands_idle_index_black_key_clearance_prototype_r1/BASELINE_LOCAL_SAMPLES.npz`
- `experiments/hands_idle_index_black_key_clearance_prototype_r1/CANDIDATE_LOCAL_SAMPLES.npz` → `hands-research-r1-selected-012.zip` / `payload/experiments/hands_idle_index_black_key_clearance_prototype_r1/CANDIDATE_LOCAL_SAMPLES.npz`
- `experiments/hands_idle_index_black_key_clearance_prototype_r1/IDLE_INDEX_CLEARANCE_B_NOT_APPROVED.blend` → `hands-research-r1-selected-013.zip` / `payload/experiments/hands_idle_index_black_key_clearance_prototype_r1/IDLE_INDEX_CLEARANCE_B_NOT_APPROVED.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
