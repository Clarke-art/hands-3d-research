# experiments/hands_cleanup_audit_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> B2连续伴奏、旧target-key规划等大任务的_frames，历史PianoVAM/琴键空间/低DOF/双手实动的_render_frames和已编码motion序列，以及C2的before_frames。深度追加A2/B3 recovery/C2的非必要_frames及C1除两张审核poster以外的帧。保留任务根目录内代码、数值、Blend、视频、报告，可继续研发，不把曾参与研发的整个目录永久保护。

出处：[HUMAN_REVIEW.md](../research/experiments/hands_cleanup_audit_r1/HUMAN_REVIEW.md)

> 没有完整任务根目录能在现有证据下直接整包删除。多个FAIL_CLOSED任务仍是有效后续代码/对照输入；TASK_ASSESSMENTS.json逐个给出具体阻碍。

出处：[HUMAN_REVIEW.md](../research/experiments/hands_cleanup_audit_r1/HUMAN_REVIEW.md)

## 技术路线

> 任务 `HANDS_WORKSPACE_DEEP_CLEANUP_AUDIT_R1`。审计日期：2026-10-11（Asia/Shanghai）。Hands 只读，未删除、移动、压缩、保存 Blend、修改配置或运行求解/渲染。报告只写在工作区外。

出处：[SPACE_INVENTORY.md](../research/experiments/hands_cleanup_audit_r1/SPACE_INVENTORY.md)

> PNG 19.533 GiB（约84.88%）是主因，多为按视角保存的连续无损帧。JSON约1.774 GiB、NPZ约0.800 GiB是原生提取、Action、求解/实际skin记录；其中有后续真实依赖。Blend约0.242 GiB/90份，MP4约0.133 GiB/121份，blend1约0.005 GiB/3份，日志仅约0.004 GiB。因此只删视频或Blend备份无法显著瘦身。Action主要嵌在Blend和JSON中，没有独立Action后缀总量可诚实单列；90份Blend全部保留。

出处：[SPACE_INVENTORY.md](../research/experiments/hands_cleanup_audit_r1/SPACE_INVENTORY.md)

## 测试结论

> **最终状态：DEEP_CLEANUP_PASS。STOP — HUMAN REVIEW。**

出处：[FINAL_CLEANUP_REPORT.md](../research/experiments/hands_cleanup_audit_r1/FINAL_CLEANUP_REPORT.md)

> 锁定Manifest SHA256 `d1e33316b66c254a9ba08acfb85bb9af79754766e1c99ab8abe1dd059f2503b7` 保持不变。Human批准独立写入APPROVED_CLEANUP_LEDGER.jsonl，原human_approval_received=false不修改。全量及补充预检PASS后，严格逐文件执行339条目/18409成员；没有按目录通配符删除，没有递归删除目录。

出处：[FINAL_CLEANUP_REPORT.md](../research/experiments/hands_cleanup_audit_r1/FINAL_CLEANUP_REPORT.md)

## 失败原因与证据边界

> 首次准备的广泛本地网页服务被自动审批拒绝，未启动；原因是暴露整个工作区。改为明确2174资源白名单服务后完成验收，其他源码路径HTTP403；此为已解决的非阻断事件，无文件清理范围变化。测试服务仅用于验收，结束后关闭。

出处：[FINAL_CLEANUP_REPORT.md](../research/experiments/hands_cleanup_audit_r1/FINAL_CLEANUP_REPORT.md)

> 没有完整任务根目录能在现有证据下直接整包删除。多个FAIL_CLOSED任务仍是有效后续代码/对照输入；TASK_ASSESSMENTS.json逐个给出具体阻碍。

出处：[HUMAN_REVIEW.md](../research/experiments/hands_cleanup_audit_r1/HUMAN_REVIEW.md)

## 后续建议

> 历史全目录冻结清单未改写，不能宣称它们的所有文件仍然存在。后续仅接受本账本中实际SUCCESS成员作为精确缺失例外；其余缺失仍是异常。

出处：[FINAL_CLEANUP_REPORT.md](../research/experiments/hands_cleanup_audit_r1/FINAL_CLEANUP_REPORT.md)

> **STOP — HUMAN REVIEW。未安排或启动下一轮清理、研发或动画生成。**

出处：[FINAL_CLEANUP_REPORT.md](../research/experiments/hands_cleanup_audit_r1/FINAL_CLEANUP_REPORT.md)

## 原报告与关键代码

- [experiments/hands_cleanup_audit_r1/FINAL_CLEANUP_REPORT.md](../research/experiments/hands_cleanup_audit_r1/FINAL_CLEANUP_REPORT.md)
- [experiments/hands_cleanup_audit_r1/HUMAN_REVIEW.md](../research/experiments/hands_cleanup_audit_r1/HUMAN_REVIEW.md)
- [experiments/hands_cleanup_audit_r1/SPACE_INVENTORY.md](../research/experiments/hands_cleanup_audit_r1/SPACE_INVENTORY.md)
- [experiments/hands_cleanup_audit_r1/PROTECTED_ASSETS.md](../research/experiments/hands_cleanup_audit_r1/PROTECTED_ASSETS.md)
- [experiments/hands_cleanup_audit_r1/CLEANUP_CANDIDATES.md](../research/experiments/hands_cleanup_audit_r1/CLEANUP_CANDIDATES.md)
- [experiments/hands_cleanup_audit_r1/CLEANUP_PREFLIGHT_RESULT.md](../research/experiments/hands_cleanup_audit_r1/CLEANUP_PREFLIGHT_RESULT.md)
- [experiments/hands_cleanup_audit_r1/POST_CLEANUP_PROTECTION_CHECK.md](../research/experiments/hands_cleanup_audit_r1/POST_CLEANUP_PROTECTION_CHECK.md)
- [experiments/hands_cleanup_audit_r1/execution_r1.py](../../src/legacy/experiments/hands_cleanup_audit_r1/execution_r1.py)
- [experiments/hands_cleanup_audit_r1/preflight_readonly.py](../../src/legacy/experiments/hands_cleanup_audit_r1/preflight_readonly.py)

## 输入、输出与大型证据

该目录原始成员 34 项；拟公开身份记录 33 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
