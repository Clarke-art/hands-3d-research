# experiments/hands_c1_phrase_level_geometry_closure_r3

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 本轮完成事件/角色、真实几何及安全回接边界检查，**未进入关键帧编辑，动画设计数0**。本轮没有证明“不存在合法纠错动画”：只是在允许的既有后续动作中，未找到可安全接回且能关闭本轮编辑影响的区间。若在3.80s新造一个安全终态而未验证后续交接，仍不能称为完整短句闭合；本轮没有创建这种未闭合候选。未生成 `PHRASE_CORRECTED_NOT_APPROVED.blend` 或新的修复对照视频。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_c1_phrase_level_geometry_closure_r3/TECHNICAL_REPORT.md)

> | 时间s | 非目标键 | 原C1 | R2 | R3隔离副本 | 实际涉及骨 |

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_c1_phrase_level_geometry_closure_r3/TECHNICAL_REPORT.md)

## 技术路线

原报告未单独概述路线；以下实现文件与原报告共同界定方法，不能由文件名推断算法成功：

- [check_boundary.py](../../src/legacy/experiments/hands_c1_phrase_level_geometry_closure_r3/check_boundary.py)
- [finalize.py](../../src/legacy/experiments/hands_c1_phrase_level_geometry_closure_r3/finalize.py)
- [session.py](../../src/legacy/experiments/hands_c1_phrase_level_geometry_closure_r3/session.py)
- [start_mcp.py](../../src/legacy/experiments/hands_c1_phrase_level_geometry_closure_r3/start_mcp.py)

## 测试结论

> B01核心为1.10–1.4214275s、编辑0.90–1.705713s、预览0.90–1.75s，**与本轮不重合**。其核心87/87→0/87但整体FAIL的事实保留；未加载其Blend、未改B01、未将3.708s后的另一段MIDDLE/RING相交冒称为B01或宣称B01已解决。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_c1_phrase_level_geometry_closure_r3/TECHNICAL_REPORT.md)

> - R2的2.45–2.92s目标0/225、三键清障、G4密集350点PASS和关节越界清零原样保留，因为实验起点仅作字节相同复制、没有关键帧编辑。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_c1_phrase_level_geometry_closure_r3/TECHNICAL_REPORT.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

> 本轮完成事件/角色、真实几何及安全回接边界检查，**未进入关键帧编辑，动画设计数0**。本轮没有证明“不存在合法纠错动画”：只是在允许的既有后续动作中，未找到可安全接回且能关闭本轮编辑影响的区间。若在3.80s新造一个安全终态而未验证后续交接，仍不能称为完整短句闭合；本轮没有创建这种未闭合候选。未生成 `PHRASE_CORRECTED_NOT_APPROVED.blend` 或新的修复对照视频。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_c1_phrase_level_geometry_closure_r3/TECHNICAL_REPORT.md)

> R06/R07为拇指G4，分别2.064284–2.492855及2.492855–2.921426s。R08为小指E5，2.921426–3.349997；R09为中指C5，3.349997–3.5642825；R10为无名指D5，3.5642825–3.778568；R11为中指E5，3.778568–3.9928535。下一R12 F#5在3.9928535开始，仅读取事件资料，没有检查3.80s以后的姿态。

出处：[TECHNICAL_REPORT.md](../research/experiments/hands_c1_phrase_level_geometry_closure_r3/TECHNICAL_REPORT.md)

## 原报告与关键代码

- [experiments/hands_c1_phrase_level_geometry_closure_r3/TECHNICAL_REPORT.md](../research/experiments/hands_c1_phrase_level_geometry_closure_r3/TECHNICAL_REPORT.md)
- [experiments/hands_c1_phrase_level_geometry_closure_r3/HUMAN_REVIEW.md](../research/experiments/hands_c1_phrase_level_geometry_closure_r3/HUMAN_REVIEW.md)
- [experiments/hands_c1_phrase_level_geometry_closure_r3/check_boundary.py](../../src/legacy/experiments/hands_c1_phrase_level_geometry_closure_r3/check_boundary.py)
- [experiments/hands_c1_phrase_level_geometry_closure_r3/finalize.py](../../src/legacy/experiments/hands_c1_phrase_level_geometry_closure_r3/finalize.py)
- [experiments/hands_c1_phrase_level_geometry_closure_r3/session.py](../../src/legacy/experiments/hands_c1_phrase_level_geometry_closure_r3/session.py)
- [experiments/hands_c1_phrase_level_geometry_closure_r3/start_mcp.py](../../src/legacy/experiments/hands_c1_phrase_level_geometry_closure_r3/start_mcp.py)

## 输入、输出与大型证据

该目录原始成员 34 项；拟公开身份记录 25 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
