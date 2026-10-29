# audits/directory_structure_correction_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 4. **旧保护表保留原路径语义。** 前次 R2 的保护表覆盖其中 16 个目录的 10,749 文件，当前全部与旧 SHA 一致。R2 自身在那张输入保护表中为 0，是此前自输出排除，不是无保护/可随意移动。207 个 R2 输出本轮全部建立前后 SHA。不能覆写历史表来“消除缺失”；需新增迁移映射及独立路径验证，且保留旧 FAIL/PASS。

出处：[DIRECTORY_CORRECTION_REPORT.md](../research/audits/directory_structure_correction_r1/DIRECTORY_CORRECTION_REPORT.md)

> 前后 Codex 任务快照显示当前 active Hands 聊天是本目录纠偏任务；其余可见 Hands 聊天为 notLoaded。当前另有 active Piano 依赖闭合任务，核对到 `LOCAL_GB_01_DEPENDENCY_CLOSURE_R1`，它的文件未移动、停止或改写。本轮也未向其他聊天发送消息。

出处：[DIRECTORY_CORRECTION_REPORT.md](../research/audits/directory_structure_correction_r1/DIRECTORY_CORRECTION_REPORT.md)

## 技术路线

> `静态路径影响`（链接见原报告） 保存 295 条有限 AST 规则结果，其中 74 条在整体迁入假设下仍不等价；这不是所有动态/原生路径的完整证明。扫描 388 个匹配文件，编码错误 0。没有执行旧求解器、旧审计删除程序、Blender 验证或新技术研发。未知动态路径、外部调用、二进制原生资源关系仍不能被文本扫描排除。

出处：[DIRECTORY_CORRECTION_REPORT.md](../research/audits/directory_structure_correction_r1/DIRECTORY_CORRECTION_REPORT.md)

> 进程快照未发现引用这 17 个目录的 R3/求解/渲染命令；历史审计 pid 368 不存在，历史报告记载服务已关闭。进程和任务快照不能排除所有外部动态引用，因此不把它们作为迁移安全的唯一证明。

出处：[DIRECTORY_CORRECTION_REPORT.md](../research/audits/directory_structure_correction_r1/DIRECTORY_CORRECTION_REPORT.md)

## 测试结论

> 4. **旧保护表保留原路径语义。** 前次 R2 的保护表覆盖其中 16 个目录的 10,749 文件，当前全部与旧 SHA 一致。R2 自身在那张输入保护表中为 0，是此前自输出排除，不是无保护/可随意移动。207 个 R2 输出本轮全部建立前后 SHA。不能覆写历史表来“消除缺失”；需新增迁移映射及独立路径验证，且保留旧 FAIL/PASS。

出处：[DIRECTORY_CORRECTION_REPORT.md](../research/audits/directory_structure_correction_r1/DIRECTORY_CORRECTION_REPORT.md)

> 错误目标 `<HANDS_ROOT>_contact_execution_foundation_r3` 不存在；正确目标也尚未创建。R3 名称的本地引用仅来自本轮新 AGENTS 规则，未发现需移动的 R3 输出。只纠正后续目标路径，未创建实验、未产生技术结果；后续正式启动时仍需再核对当时运行状态。见 `R3 路径登记`（链接见原报告）。

出处：[DIRECTORY_CORRECTION_REPORT.md](../research/audits/directory_structure_correction_r1/DIRECTORY_CORRECTION_REPORT.md)

## 失败原因与证据边界

> 当前 17 个目录都有未闭合的路径或复核风险，按本次要求“确认安全才允许迁移”“存在风险则先报告，不强制移动”保留原位。没有覆盖、删除、修改冻结成果，没有创建根目录符号链接/junction，也没有移动 piano。**不是所有历史 manifest 成员都天然禁止迁移；本次暂缓依据是实际代码路径阻碍及尚未验证的保护/复核映射。**

出处：[DIRECTORY_CORRECTION_REPORT.md](../research/audits/directory_structure_correction_r1/DIRECTORY_CORRECTION_REPORT.md)

> 1. **父层级假设已证实会失效。** 多个脚本以 `O=Path(__file__).resolve().parent`、`ROOT=O.parent/'hands'` 找源码和 `_deps`。即使 17 个目录一起移动，ROOT 仍会变成 `hands\hands`。R2 的 `verify_midi.py:4` 同样如此；它虽没有外部直接引用，仍不能免除复现检查。

出处：[DIRECTORY_CORRECTION_REPORT.md](../research/audits/directory_structure_correction_r1/DIRECTORY_CORRECTION_REPORT.md)

## 后续建议

> Human 要求的根目录规则已写入 `<HANDS_ROOT>\AGENTS.md`。后续 Hands 研发、实验、审计、日志、临时文件只能在 hands 内；本轮所有新增文件亦在 hands 内。R3 唯一输出路径为 `<HANDS_ROOT>\hands_contact_execution_foundation_r3`，未启动 R3 技术研发。

出处：[DIRECTORY_CORRECTION_REPORT.md](../research/audits/directory_structure_correction_r1/DIRECTORY_CORRECTION_REPORT.md)

> 3. **跨目录输入必须同时闭合。** 比如 C01 来源、B2 静态起点、原生场景、符号函数、CasADi/ONNX 依赖和原 Action 比较数据仍在后续源码中被引用。单独搬入会破坏 sibling 路径；仅改文件夹位置不能证明调用方安全。

出处：[DIRECTORY_CORRECTION_REPORT.md](../research/audits/directory_structure_correction_r1/DIRECTORY_CORRECTION_REPORT.md)

## 原报告与关键代码

- [audits/directory_structure_correction_r1/DIRECTORY_CORRECTION_REPORT.md](../research/audits/directory_structure_correction_r1/DIRECTORY_CORRECTION_REPORT.md)
- [audits/directory_structure_correction_r1/HUMAN_REVIEW.md](../research/audits/directory_structure_correction_r1/HUMAN_REVIEW.md)
- [audits/directory_structure_correction_r1/DIRECTORY_DETAILS.md](../research/audits/directory_structure_correction_r1/DIRECTORY_DETAILS.md)
- [audits/directory_structure_correction_r1/assess_migration.py](../../src/legacy/audits/directory_structure_correction_r1/assess_migration.py)
- [audits/directory_structure_correction_r1/audit_directory.py](../../src/legacy/audits/directory_structure_correction_r1/audit_directory.py)
- [audits/directory_structure_correction_r1/verify_directory.py](../../src/legacy/audits/directory_structure_correction_r1/verify_directory.py)
- [audits/directory_structure_correction_r1/write_report.py](../../src/legacy/audits/directory_structure_correction_r1/write_report.py)

## 输入、输出与大型证据

该目录原始成员 34 项；拟公开身份记录 34 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
