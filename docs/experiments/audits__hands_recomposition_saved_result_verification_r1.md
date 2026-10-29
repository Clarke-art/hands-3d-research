# audits/hands_recomposition_saved_result_verification_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 第一次自测在 `contract.py:79` 的 `import mido` 处抛出 `ModuleNotFoundError: No module named 'mido'`，尚未调用 `load_inputs()`。本轮适配器的前置依赖加载安排有误：该导入发生在复制的 `model.py` 配置原 `_deps` 路径之前。这是本轮验证代码错误，不能归因于保存 NPZ 损坏，也不能把它记为真实几何失败。

出处：[FINAL_VERIFICATION_REPORT.md](../research/audits/hands_recomposition_saved_result_verification_r1/FINAL_VERIFICATION_REPORT.md)

> 没有真实 skin、琴键 BVH、五指交叉或共享皮肤的本轮几何见证。实际几何覆盖区域为零；全部网格区域均未复核。上一轮数值摘要及历史缺陷仍保留原始记录，不能用其中代理深度为零代替本轮 Blender 验证。

出处：[FINAL_VERIFICATION_REPORT.md](../research/audits/hands_recomposition_saved_result_verification_r1/FINAL_VERIFICATION_REPORT.md)

## 技术路线

原报告未单独概述路线；以下实现文件与原报告共同界定方法，不能由文件名推断算法成功：

- [contract.py](../../src/legacy/audits/hands_recomposition_saved_result_verification_r1/contract.py)
- [model.py](../../src/legacy/audits/hands_recomposition_saved_result_verification_r1/model.py)
- [persistence.py](../../src/legacy/audits/hands_recomposition_saved_result_verification_r1/persistence.py)
- [source_actual_original.py](../../src/legacy/audits/hands_recomposition_saved_result_verification_r1/source_actual_original.py)
- [support.py](../../src/legacy/audits/hands_recomposition_saved_result_verification_r1/support.py)

## 测试结论

> | 时间（秒） | 数值状态与真实 Rig 一致性 | D5 真实 skin pad 触键 | E5 邻键侵入清除 | 其他四指、指蹼、掌部不恶化 |

出处：[FINAL_VERIFICATION_REPORT.md](../research/audits/hands_recomposition_saved_result_verification_r1/FINAL_VERIFICATION_REPORT.md)

> 启动前只读检查确认三个 NPZ 文件存在；独立查看了第一份 NPZ 的数组字段、形状及元数据，并查看了聚合状态和冻结模型的形状。**七项完整输入合同检查未完成**，有限值、三份身份、关节域、MIDI 时钟及诊断重建不能记为本轮通过。草稿中的负向测试也未执行。

出处：[FINAL_VERIFICATION_REPORT.md](../research/audits/hands_recomposition_saved_result_verification_r1/FINAL_VERIFICATION_REPORT.md)

## 失败原因与证据边界

> 本轮只支持：原字段错误已经定位，隔离适配器已有字段映射草稿，但第一次输入自测被新的依赖加载错误阻断，因此结果为 `BLOCKED_INPUT_CONTRACT`。

出处：[FINAL_VERIFICATION_REPORT.md](../research/audits/hands_recomposition_saved_result_verification_r1/FINAL_VERIFICATION_REPORT.md)

## 后续建议

> 当前证据不足以建议进入连续动作重组。Human 如决定继续，应先单独授权修复本轮依赖加载错误、完成输入合同并复核这三个保存姿态；真实静态验证闭合后，再判断是否值得授权连续动作重组。本轮没有自动进入下一阶段。

出处：[FINAL_VERIFICATION_REPORT.md](../research/audits/hands_recomposition_saved_result_verification_r1/FINAL_VERIFICATION_REPORT.md)

## 原报告与关键代码

- [audits/hands_recomposition_saved_result_verification_r1/FINAL_VERIFICATION_REPORT.md](../research/audits/hands_recomposition_saved_result_verification_r1/FINAL_VERIFICATION_REPORT.md)
- [audits/hands_recomposition_saved_result_verification_r1/contract.py](../../src/legacy/audits/hands_recomposition_saved_result_verification_r1/contract.py)
- [audits/hands_recomposition_saved_result_verification_r1/model.py](../../src/legacy/audits/hands_recomposition_saved_result_verification_r1/model.py)
- [audits/hands_recomposition_saved_result_verification_r1/persistence.py](../../src/legacy/audits/hands_recomposition_saved_result_verification_r1/persistence.py)
- [audits/hands_recomposition_saved_result_verification_r1/source_actual_original.py](../../src/legacy/audits/hands_recomposition_saved_result_verification_r1/source_actual_original.py)
- [audits/hands_recomposition_saved_result_verification_r1/support.py](../../src/legacy/audits/hands_recomposition_saved_result_verification_r1/support.py)

## 输入、输出与大型证据

该目录原始成员 11 项；拟公开身份记录 10 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
