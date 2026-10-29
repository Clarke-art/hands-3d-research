# audits/hands_recomposition_saved_result_verification_r2

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> **本轮完整验证仍未完成。** 初次诊断错误地追加“非目标键 BVH 相交必须为零”的停止判据，且将活动小指的面组合变化计入其他区域回退。它比原 0.5mm 深度门禁更严格，因此原始机器文件中的 `STATIC_SOURCE_CORRECTION_FAIL` **不是本报告认可的最终分类**；原文件、源码快照和几何观测全部保留。

出处：[FINAL_VERIFICATION_REPORT.md](../research/audits/hands_recomposition_saved_result_verification_r2/FINAL_VERIFICATION_REPORT.md)

> 1.7000s、相同实际网格/键体口径：原 C1 小指非目标键最大内部顶点深度 **1.494929mm**，校正后 **0mm**；小指/E5 实际 BVH 表面相交由 **22 对降至 6 对**，涉及 skin 面 968、1004、1005 和 E5 FRONT 面 2、4。

出处：[FINAL_VERIFICATION_REPORT.md](../research/audits/hands_recomposition_saved_result_verification_r2/FINAL_VERIFICATION_REPORT.md)

## 技术路线

> 第二轮软件修复恢复原判据，拟复用已捕获的真实 skin 继续只读检查；但恢复脚本在配置脚本目录前导入 `source_actual`，发生 `ModuleNotFoundError`，退出码 7。第二次进程尚未打开 C1，也未执行恢复自测或重新施加姿态。两轮修复额度耗尽，停止，没有第三次修复或重启。该错误属于本轮诊断实现，不能记为运动学失败。

出处：[FINAL_VERIFICATION_REPORT.md](../research/audits/hands_recomposition_saved_result_verification_r2/FINAL_VERIFICATION_REPORT.md)

## 测试结论

> **本轮完整验证仍未完成。** 初次诊断错误地追加“非目标键 BVH 相交必须为零”的停止判据，且将活动小指的面组合变化计入其他区域回退。它比原 0.5mm 深度门禁更严格，因此原始机器文件中的 `STATIC_SOURCE_CORRECTION_FAIL` **不是本报告认可的最终分类**；原文件、源码快照和几何观测全部保留。

出处：[FINAL_VERIFICATION_REPORT.md](../research/audits/hands_recomposition_saved_result_verification_r2/FINAL_VERIFICATION_REPORT.md)

## 失败原因与证据边界

> 当前不足以支持进入跨事件连续动作重组：三个真实重建已证实，但只有首个时刻的几何观测，最终门禁仍被工具链错误阻断，且 E5 有残留表面穿入。连续连接、整段 C1 安全、F♯5→G5、Human 自然度及通用整手避障均未验证。应由独立审核与 Human 决定是否另行授权闭合静态验证，不能自动进入连续研发。

出处：[FINAL_VERIFICATION_REPORT.md](../research/audits/hands_recomposition_saved_result_verification_r2/FINAL_VERIFICATION_REPORT.md)

## 后续建议

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 原报告与关键代码

- [audits/hands_recomposition_saved_result_verification_r2/FINAL_VERIFICATION_REPORT.md](../research/audits/hands_recomposition_saved_result_verification_r2/FINAL_VERIFICATION_REPORT.md)
- [audits/hands_recomposition_saved_result_verification_r2/blender_helpers.py](../../src/legacy/audits/hands_recomposition_saved_result_verification_r2/blender_helpers.py)
- [audits/hands_recomposition_saved_result_verification_r2/contract.py](../../src/legacy/audits/hands_recomposition_saved_result_verification_r2/contract.py)
- [audits/hands_recomposition_saved_result_verification_r2/contract_attempt_0.py](../../src/legacy/audits/hands_recomposition_saved_result_verification_r2/contract_attempt_0.py)
- [audits/hands_recomposition_saved_result_verification_r2/recover_geometry.py](../../src/legacy/audits/hands_recomposition_saved_result_verification_r2/recover_geometry.py)
- [audits/hands_recomposition_saved_result_verification_r2/run_blender.py](../../src/legacy/audits/hands_recomposition_saved_result_verification_r2/run_blender.py)
- [audits/hands_recomposition_saved_result_verification_r2/source_actual.py](../../src/legacy/audits/hands_recomposition_saved_result_verification_r2/source_actual.py)
- [audits/hands_recomposition_saved_result_verification_r2/source_actual_attempt_0.py](../../src/legacy/audits/hands_recomposition_saved_result_verification_r2/source_actual_attempt_0.py)
- [audits/hands_recomposition_saved_result_verification_r2/witness_postprocess.py](../../src/legacy/audits/hands_recomposition_saved_result_verification_r2/witness_postprocess.py)

## 输入、输出与大型证据

该目录原始成员 42 项；拟公开身份记录 33 项。
- `audits/hands_recomposition_saved_result_verification_r2/E5_REAL_SKIN_WITNESS.png` → `hands-research-r1-selected-001-r1a.zip` / `payload/audits/hands_recomposition_saved_result_verification_r2/E5_REAL_SKIN_WITNESS.png`
- `audits/hands_recomposition_saved_result_verification_r2/GEOMETRY_COVERAGE.json` → `hands-research-r1-selected-001-r1a.zip` / `payload/audits/hands_recomposition_saved_result_verification_r2/GEOMETRY_COVERAGE.json`
- `audits/hands_recomposition_saved_result_verification_r2/GEOMETRY_POSE_0.json` → `hands-research-r1-selected-001-r1a.zip` / `payload/audits/hands_recomposition_saved_result_verification_r2/GEOMETRY_POSE_0.json`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
