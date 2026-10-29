# HANDS_RECOMPOSITION_SAVED_RESULT_VERIFICATION_R1

RESULT = BLOCKED_INPUT_CONTRACT

DYNAMIC_RECOMPOSITION = NOT_EXECUTED

HUMAN_NATURALNESS = NOT_TESTED

STOP — HUMAN REVIEW

2026-10-14（Asia/Shanghai）。本轮确定性输入自测执行一次，真实 Blender 正式复核执行零次。未重跑优化、修改保存参数、生成 Action / Blend / 视频，未访问独立 piano 目录。

## A. 字段修复与执行

原 `source_actual.py:10` 读取 `I['source_scene']`，原 `INPUT_BINDINGS.json` 实际提供 `scene`。本轮在隔离适配器 `contract.py:28` 使用 `value['scene']`；原脚本只复制为 `source_actual_original.py` 保存证据，原 R1 文件未修改。这个字段映射已经写入草稿，但**不能宣布完整诊断脚本已修复或自测通过**。

第一次自测在 `contract.py:79` 的 `import mido` 处抛出 `ModuleNotFoundError: No module named 'mido'`，尚未调用 `load_inputs()`。本轮适配器的前置依赖加载安排有误：该导入发生在复制的 `model.py` 配置原 `_deps` 路径之前。这是本轮验证代码错误，不能归因于保存 NPZ 损坏，也不能把它记为真实几何失败。

按照“发生新的合同错误时，保存现场并停止”的要求，未修复后重试，未启动 Blender，未继续制作正式执行适配器。错误保存在 `input_contract.log` 与 `INPUT_CONTRACT_GATE.json`。

## B–E. 三个姿态的真实验证

| 时间（秒） | 数值状态与真实 Rig 一致性 | D5 真实 skin pad 触键 | E5 邻键侵入清除 | 其他四指、指蹼、掌部不恶化 |
|---|---|---|---|---|
| 1.7000 | 未验证 | 未验证 | 未验证 | 未验证 |
| 2.0000 | 未验证 | 未验证 | 未验证 | 未验证 |
| 2.0625 | 未验证 | 未验证 | 未验证 | 未验证 |

启动前只读检查确认三个 NPZ 文件存在；独立查看了第一份 NPZ 的数组字段、形状及元数据，并查看了聚合状态和冻结模型的形状。**七项完整输入合同检查未完成**，有限值、三份身份、关节域、MIDI 时钟及诊断重建不能记为本轮通过。草稿中的负向测试也未执行。

没有真实 skin、琴键 BVH、五指交叉或共享皮肤的本轮几何见证。实际几何覆盖区域为零；全部网格区域均未复核。上一轮数值摘要及历史缺陷仍保留原始记录，不能用其中代理深度为零代替本轮 Blender 验证。

## 冻结保护与哈希

`KEY_INPUT_SHA_CHECK.json` 对 16 个关键输入给出两次 SHA-256 及可用的上一轮历史 SHA 对比。两次检查均在自测停止之后完成，全部相同。原 C1 Blend、原 MIDI、原事件时间表、冻结数值蒙皮模型及 corrective delta 的五项历史 SHA 全部匹配。

原 R1 源码、NPZ 和结果没有写入操作；Python 只允许写入本审计目录，且禁用字节码写入。C1 文件 SHA 与历史一致支持文件内 Rig、骨骼、蒙皮、corrective 及琴键 Action 的磁盘资产未变；**没有本轮 Blender 内存状态或其他四指、共享掌腕参数的运行时一致性验证**。三份 NPZ 没有可用的本轮执行前哈希收据，停止后的双检查不能冒称覆盖完整执行前后。未开展全目录扫描、资产迁移、删除或冻结成果修改。

## F. 可支持的技术结论

本轮只支持：原字段错误已经定位，隔离适配器已有字段映射草稿，但第一次输入自测被新的依赖加载错误阻断，因此结果为 `BLOCKED_INPUT_CONTRACT`。

本轮不支持任何三个静态姿态的真实验证通过结论；也不支持整段 C1 修复、自然连续连接、角色动作重组成功、F♯5→G5 适配通过或通用整手避障完成。没有连续轨迹生成或 Human 自然度测试。

## G. 是否授权真正的跨事件连续动作重组

当前证据不足以建议进入连续动作重组。Human 如决定继续，应先单独授权修复本轮依赖加载错误、完成输入合同并复核这三个保存姿态；真实静态验证闭合后，再判断是否值得授权连续动作重组。本轮没有自动进入下一阶段。

附属证据：`INPUT_CONTRACT_GATE.json`、`input_contract.log`、`KEY_INPUT_SHA_CHECK.json`、`POST_STOP_SHA_CHECKPOINT_1.json`、`VERIFICATION_RESULT.json`；诊断源码复制与适配器草稿保留用于独立审核。

**STOP — HUMAN REVIEW**
