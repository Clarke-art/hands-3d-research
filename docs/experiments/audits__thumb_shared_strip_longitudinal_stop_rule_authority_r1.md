# audits/thumb_shared_strip_longitudinal_stop_rule_authority_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 技术路线

原报告未单独概述路线；以下实现文件与原报告共同界定方法，不能由文件名推断算法成功：

- [adjudicate.py](../../src/legacy/audits/thumb_shared_strip_longitudinal_stop_rule_authority_r1/adjudicate.py)
- [data.py](../../src/legacy/audits/thumb_shared_strip_longitudinal_stop_rule_authority_r1/data.py)
- [finalize.py](../../src/legacy/audits/thumb_shared_strip_longitudinal_stop_rule_authority_r1/finalize.py)
- [profiles.py](../../src/legacy/audits/thumb_shared_strip_longitudinal_stop_rule_authority_r1/profiles.py)
- [render.py](../../src/legacy/audits/thumb_shared_strip_longitudinal_stop_rule_authority_r1/render.py)

## 测试结论

> **FAIL_CLOSED。Distal 已形成侧别明确、由 frozen authority conflict 定位的停止规则候选；proximal semantic stop 仍不唯一。没有 role extension、complement 或完整候选审批页面。**

出处：[THUMB_SHARED_STRIP_LONGITUDINAL_STOP_RULE_AUTHORITY_R1_REPORT.md](../research/audits/thumb_shared_strip_longitudinal_stop_rule_authority_r1/THUMB_SHARED_STRIP_LONGITUDINAL_STOP_RULE_AUTHORITY_R1_REPORT.md)

> LEFT=column4，从 R00 v1399 出发；其第一 extension face1177 包含 frozen nail v304。停止边为 e4475=[1399,2774]，必须在进入1177之前停止。RIGHT=column6，从 v1396 出发，经 face1176，属于不立即碰到 nail 的一侧。两者由真实 incident faces / edges 判定，不凭截图。完整 frontier edges、首次 continuation edge、两种状态的 nail/cap 距离、normal 与 tangent 见 `DISTAL_FRONTIER_SIDE_IDENTITY_R1.json`。

出处：[THUMB_SHARED_STRIP_LONGITUDINAL_STOP_RULE_AUTHORITY_R1_REPORT.md](../research/audits/thumb_shared_strip_longitudinal_stop_rule_authority_r1/THUMB_SHARED_STRIP_LONGITUDINAL_STOP_RULE_AUTHORITY_R1_REPORT.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

> Distal 停止规则候选：**沿既有 non-nail 面列继续，在首次 frozen nail/cap 冲突前停止**。最后安全 row=D04 / face1226，末端边 e4524；下一面1227禁止进入 shared extension。左侧在1177前停，右侧在1227前停，允许 asymmetric taper。

出处：[THUMB_SHARED_STRIP_LONGITUDINAL_STOP_RULE_AUTHORITY_R1_REPORT.md](../research/audits/thumb_shared_strip_longitudinal_stop_rule_authority_r1/THUMB_SHARED_STRIP_LONGITUDINAL_STOP_RULE_AUTHORITY_R1_REPORT.md)

> 这里的 RESOLVED 指该固定 face-column 上的停止规则候选已可确定，仍 pending Human；并不是宣称所有安全面已经获得 anatomical shared ownership。硬冲突建立禁止继续的上界；逐面连续性、仍朝 web context 的辅助法向与逐渐接近 frozen distal cap 提供候选的上下文。D01–D04 的正 normal dot 不是 membership 阈值，也不自动证明 shared anatomy。后续 lateral/role authority 仍须独立满足。

出处：[THUMB_SHARED_STRIP_LONGITUDINAL_STOP_RULE_AUTHORITY_R1_REPORT.md](../research/audits/thumb_shared_strip_longitudinal_stop_rule_authority_r1/THUMB_SHARED_STRIP_LONGITUDINAL_STOP_RULE_AUTHORITY_R1_REPORT.md)

## 原报告与关键代码

- [audits/thumb_shared_strip_longitudinal_stop_rule_authority_r1/THUMB_SHARED_STRIP_LONGITUDINAL_STOP_RULE_AUTHORITY_R1_REPORT.md](../research/audits/thumb_shared_strip_longitudinal_stop_rule_authority_r1/THUMB_SHARED_STRIP_LONGITUDINAL_STOP_RULE_AUTHORITY_R1_REPORT.md)
- [audits/thumb_shared_strip_longitudinal_stop_rule_authority_r1/adjudicate.py](../../src/legacy/audits/thumb_shared_strip_longitudinal_stop_rule_authority_r1/adjudicate.py)
- [audits/thumb_shared_strip_longitudinal_stop_rule_authority_r1/data.py](../../src/legacy/audits/thumb_shared_strip_longitudinal_stop_rule_authority_r1/data.py)
- [audits/thumb_shared_strip_longitudinal_stop_rule_authority_r1/finalize.py](../../src/legacy/audits/thumb_shared_strip_longitudinal_stop_rule_authority_r1/finalize.py)
- [audits/thumb_shared_strip_longitudinal_stop_rule_authority_r1/profiles.py](../../src/legacy/audits/thumb_shared_strip_longitudinal_stop_rule_authority_r1/profiles.py)
- [audits/thumb_shared_strip_longitudinal_stop_rule_authority_r1/render.py](../../src/legacy/audits/thumb_shared_strip_longitudinal_stop_rule_authority_r1/render.py)
- [audits/thumb_shared_strip_longitudinal_stop_rule_authority_r1/trace.py](../../src/legacy/audits/thumb_shared_strip_longitudinal_stop_rule_authority_r1/trace.py)

## 输入、输出与大型证据

该目录原始成员 32 项；拟公开身份记录 31 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
