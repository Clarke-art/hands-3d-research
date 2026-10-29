# 3D Hands 项目固定目录约束

Human 于 2026-10-14 确认本约束，后续任务必须遵守。

- 上级目录 D:\codex one\3D interactive components 仅允许 hands、piano 两个项目目录。
- 所有 Hands 研发、实验、审计、报告、日志、临时结果必须写入本 hands 目录内部。不得在上级目录新增任何实验目录或过程文件。
- Piano 文件只能位于 piano；Hands 任务不得修改 piano。
- PIANO_CONTACT_EXECUTION_FOUNDATION_R3 的唯一实验输出目录为 <HANDS_ROOT>\hands_contact_execution_foundation_r3。
- 本目录规则不授予技术研发、资产修改、清理或冻结成果迁移的额外权限。迁移须单独核查活动任务、路径引用、冻结保护与可复现性，存在未闭合风险则等待 Human 批准。
- 不覆盖同名目录，不删除历史证据，不在上级目录建立符号链接或 junction。
- 不修改冻结 Rig、正式 MIDI、琴键 Action、指法和已批准原始资产；历史并发保护 FAIL 必须保留。
- 路径迁移与内容变化分别记账。内容哈希相同不等于路径依赖安全。
