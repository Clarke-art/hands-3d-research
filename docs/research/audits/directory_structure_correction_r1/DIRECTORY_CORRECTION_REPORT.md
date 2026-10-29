# 3D Hands 目录结构纠偏审计 R1

2026-10-14，Asia/Shanghai。**审计与固定约束已落实；迁移 0/17，目录整理未完成，STOP — HUMAN REVIEW。**

Human 要求的根目录规则已写入 `<HANDS_ROOT>\AGENTS.md`。后续 Hands 研发、实验、审计、日志、临时文件只能在 hands 内；本轮所有新增文件亦在 hands 内。R3 唯一输出路径为 `<HANDS_ROOT>\hands_contact_execution_foundation_r3`，未启动 R3 技术研发。

当前 17 个目录都有未闭合的路径或复核风险，按本次要求“确认安全才允许迁移”“存在风险则先报告，不强制移动”保留原位。没有覆盖、删除、修改冻结成果，没有创建根目录符号链接/junction，也没有移动 piano。**不是所有历史 manifest 成员都天然禁止迁移；本次暂缓依据是实际代码路径阻碍及尚未验证的保护/复核映射。**

## 完整盘点

共同原父目录：`D:\codex one\3D interactive components`。每项完整原路径、拟议新路径、用途、使用证据和源码行号见 [逐目录明细](DIRECTORY_DETAILS.md)、[CSV](../../../../examples/historical/audits/directory_structure_correction_r1/DIRECTORY_INVENTORY.csv)、[机器决策](../../../../examples/historical/audits/directory_structure_correction_r1/MIGRATION_DECISIONS.json)。

17 个目录共 **10,956 文件，1,585,211,167 逻辑 bytes（1.476343 GiB）**；Windows FileStandardInfo 报告分配量合计 1,606,063,576 bytes（1.495763 GiB）。逻辑体积和分配量分开报告，目录/MFT 元数据未计入。同盘移动不会释放这些内容的磁盘空间。本轮没有压缩、去重或清理。

|目录|文件数|逻辑 MiB|报告分配 MiB|外部源码引用文件数*|R2 旧保护表成员数|决定|
|---|---:|---:|---:|---:|---:|---|
|hands_c01_anatomy_preparation_audit_r1|84|11.112|11.267|17|84|待 Human 批准|
|hands_c01_g4_e5_natural_motion_bridge_r2|89|26.059|26.221|17|89|待 Human 批准|
|hands_c01_g4_e5_skin_safe_bridge_r1|49|13.158|13.244|9|49|待 Human 批准|
|hands_c01_s1_constrained_solver_feasibility_r1|52|11.835|11.938|17|52|待 Human 批准|
|hands_c01_whole_hand_motion_feasibility_r1|58|12.509|12.626|51|58|待 Human 批准|
|hands_cleanup_audit_r1|34|129.248|129.317|0|34|待 Human 批准|
|hands_contact_constrained_trajectory_planning_r1|2,540|210.109|214.996|12|2540|待 Human 批准|
|hands_contact_derivative_feasibility_recovery_r1|106|308.869|309.051|2|106|待 Human 批准|
|hands_contact_junction_compatibility_r1|128|10.238|10.481|15|128|待 Human 批准|
|hands_contact_state_motion_planner_comparison_r1|6,137|222.750|233.754|16|6137|待 Human 批准|
|hands_early_hand_preparation_entry_reachability_r1|283|64.893|65.432|8|283|待 Human 批准|
|hands_fingering_inference_poc_r1|785|350.956|352.184|3|785|待 Human 批准|
|hands_long_context_corridor_ik_bridge_r2|207|56.801|57.205|0|0|待 Human 批准|
|hands_long_context_hand_motion_architecture_r1|106|40.119|40.323|3|106|待 Human 批准|
|hands_sequence_fingering_planning_r1|121|14.882|15.049|5|121|待 Human 批准|
|hands_skin_collision_static_feasibility_r1|74|17.742|17.897|32|74|待 Human 批准|
|hands_time_coupled_contact_recovery_r1|103|10.495|10.678|3|103|待 Human 批准|

*引用数是匹配到目录名的可执行源码/配置文件数量，含历史复核和初始化；不是当前运行调用次数，亦不是全部都已证实为直接读取。准确调用位置、字面绝对路径和父层级依赖已单独记录。没有把“无活动进程”解释为“不再使用”。

## 为什么不能直接整体搬入

1. **父层级假设已证实会失效。** 多个脚本以 `O=Path(__file__).resolve().parent`、`ROOT=O.parent/'hands'` 找源码和 `_deps`。即使 17 个目录一起移动，ROOT 仍会变成 `hands\hands`。R2 的 `verify_midi.py:4` 同样如此；它虽没有外部直接引用，仍不能免除复现检查。
2. **历史审计自身仍有固定路径读取。** `hands_cleanup_audit_r1/execution_r1.py:6` 将 O 固定为旧根目录，69–70 行从 O 读取锁定 Manifest、原库存、分类表和批准账本；74–75 行检查锁定哈希，201、214、218 行继续读取原验证输入。直接移动后这些读取找不到文件。没有为迁移修改这份历史删除程序或重新执行任何清理阶段。
3. **跨目录输入必须同时闭合。** 比如 C01 来源、B2 静态起点、原生场景、符号函数、CasADi/ONNX 依赖和原 Action 比较数据仍在后续源码中被引用。单独搬入会破坏 sibling 路径；仅改文件夹位置不能证明调用方安全。
4. **旧保护表保留原路径语义。** 前次 R2 的保护表覆盖其中 16 个目录的 10,749 文件，当前全部与旧 SHA 一致。R2 自身在那张输入保护表中为 0，是此前自输出排除，不是无保护/可随意移动。207 个 R2 输出本轮全部建立前后 SHA。不能覆写历史表来“消除缺失”；需新增迁移映射及独立路径验证，且保留旧 FAIL/PASS。

[静态路径影响](../../../../examples/historical/audits/directory_structure_correction_r1/STATIC_PATH_IMPACT.json) 保存 295 条有限 AST 规则结果，其中 74 条在整体迁入假设下仍不等价；这不是所有动态/原生路径的完整证明。扫描 388 个匹配文件，编码错误 0。没有执行旧求解器、旧审计删除程序、Blender 验证或新技术研发。未知动态路径、外部调用、二进制原生资源关系仍不能被文本扫描排除。

## 活动任务与 R3

前后 Codex 任务快照显示当前 active Hands 聊天是本目录纠偏任务；其余可见 Hands 聊天为 notLoaded。当前另有 active Piano 依赖闭合任务，核对到 `LOCAL_GB_01_DEPENDENCY_CLOSURE_R1`，它的文件未移动、停止或改写。本轮也未向其他聊天发送消息。

进程快照未发现引用这 17 个目录的 R3/求解/渲染命令；历史审计 pid 368 不存在，历史报告记载服务已关闭。进程和任务快照不能排除所有外部动态引用，因此不把它们作为迁移安全的唯一证明。

错误目标 `<HANDS_ROOT>_contact_execution_foundation_r3` 不存在；正确目标也尚未创建。R3 名称的本地引用仅来自本轮新 AGENTS 规则，未发现需移动的 R3 输出。只纠正后续目标路径，未创建实验、未产生技术结果；后续正式启动时仍需再核对当时运行状态。见 [R3 路径登记](../../../../examples/historical/audits/directory_structure_correction_r1/R3_OUTPUT_PATH_CORRECTION.json)。

## 迁移记账与内容保护

- [路径映射](../../../../examples/historical/audits/directory_structure_correction_r1/PATH_MAPPING.json) 的 17 行均为 **PROPOSED_ONLY**；实际迁移数组为空。各目标路径均无同名冲突。没有冒用“映射已登记”声明迁移完成。
- 17 个原目录的 **10,956 文件前后 SHA-256 全部相同**，成员无新增、无缺失；补充有效文件身份也未变化。清理审计 34 文件/135,526,542 bytes 的 Manifest、批准账本和历史报告完整保留。
- 原 hands 中 **19,779 文件**全部建立 before SHA，结束时全部 size/mtime 复核；其中 **6,581 个原生/科学/源码后缀文件**另做 after SHA，全部相同。大体积媒体/图像本轮结束时仅复核元数据，不声称它们全量 after SHA。六项已批准原生资产与批准哈希全部一致；正式 MIDI、已有 .blend 内 Rig/Action、源指法绑定未修改。
- 85850 项历史全局 FAIL（3 处并发变化、15 新增）、86148 项历史 PASS、86259 项 R2 全局 FAIL（618 并发新路径）及账本中的获批清理缺失例外原样保留。本轮局部字节一致不重置任何历史结论；亦不声称正在并发写入的 piano 全目录当前全局 PASS。
- 新增范围只有 hands/AGENTS.md 和本审计子目录。目录调整与 R3 科学预算、轨迹状态、优化调用数分开，技术运行数为 0。

原始证据：[before 清单](../../../artifacts/2649e9c2df21a09fa80b.md)、[after SHA](../../../artifacts/db28ed1116512ac3c743.md)、[验证结果](../../../../examples/historical/audits/directory_structure_correction_r1/VERIFICATION_RESULTS.json)、[引用索引](../../../artifacts/b6ed63e24351301feb86.md)、[保护关系](../../../../examples/historical/audits/directory_structure_correction_r1/PROTECTION_RELATIONSHIPS.json)、[历史结论保留](../../../../examples/historical/audits/directory_structure_correction_r1/HISTORICAL_PROTECTION_PRESERVATION.json)。Windows DirEntry.stat 的 inode/device/nlink 返回 0，原始 before 表这三列不作身份依据；已使用 Path.stat 补充有效身份并独立验证，原始表和问题说明都保留。分配量采用有效身份重新计算，未沿用错误的 0-ID 去重值。

## 留待 Human 审核的具体范围

**17 个目录全列为 PENDING_HUMAN_APPROVAL，尚无可直接执行的安全批次。** 其中 cleanup 审计需先决定只读历史复核入口如何在新路径使用锁定输入；其他实验需决定路径适配是否可在新增副本/适配入口实现，涉及旧源码/冻结合同的改写必须另有明确授权。

可审查的迁移目标和阻碍已逐项提供。后续若批准，应先在 hands 内准备不会重跑求解/清理的路径复核方案，验证正式 hands/piano 根、跨实验来源、输入 SHA 与可访问性；对动态/native 未闭合项继续保护。实际移动时使用精确旧→新路径、拒绝覆盖、迁前实时重查活动任务和文件身份、迁后逐文件 SHA/成员及引用复核，再登记 `PATH_RELOCATION` 事件。旧 manifest、历史源码/FAIL 不覆盖，不创建旧根链接。

## 根目录终检与结束

[ROOT_AFTER.json](../../../../examples/historical/audits/directory_structure_correction_r1/ROOT_AFTER.json) 实测根目录仍有 **hands、piano 和原 17 个 hands_* 共 19 项**；`only_hands_and_piano=false`。固定规则已落地，根目录符合性尚未达成。没有把未完成整理伪报为 PASS。

**STOP — HUMAN REVIEW。不自动开始迁移、其他清理或 R3 技术研发。**
