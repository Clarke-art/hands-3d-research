# audits/skin_static_gate_semantics_and_scope_reconciliation_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 技术路线

原报告未单独概述路线；以下实现文件与原报告共同界定方法，不能由文件名推断算法成功：

- [reconcile.py](../../src/legacy/audits/skin_static_gate_semantics_and_scope_reconciliation_r1/reconcile.py)
- [verify_outputs.py](../../src/legacy/audits/skin_static_gate_semantics_and_scope_reconciliation_r1/verify_outputs.py)

## 测试结论

> | REBUILD_IMPROVED_BUT_STILL_ABSOLUTE_FAIL | 0 |

出处：[SKIN_STATIC_GATE_SEMANTICS_AND_SCOPE_RECONCILIATION_R1_REPORT.md](../research/audits/skin_static_gate_semantics_and_scope_reconciliation_r1/SKIN_STATIC_GATE_SEMANTICS_AND_SCOPE_RECONCILIATION_R1_REPORT.md)

> 独立时间因果标签保留真实变化：**37 introduced，3 worsened，2 improved-but-fail，2 rebuilt endpoint但无实质恶化，20 exact copy-only**。主分类中worsened/improved为0是优先级归入scope conflict，不表示不存在恶化或改善。64条edge ID、两端原分类/side/支持、donor/candidate完整向量与逐group L∞/L1均在`STATIC_BLOCKER_CLASSIFICATION_R1.json`。

出处：[SKIN_STATIC_GATE_SEMANTICS_AND_SCOPE_RECONCILIATION_R1_REPORT.md](../research/audits/skin_static_gate_semantics_and_scope_reconciliation_r1/SKIN_STATIC_GATE_SEMANTICS_AND_SCOPE_RECONCILIATION_R1_REPORT.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

> 没有任何恢复出的正式contract要求全局清零所有donor旧defect。copy-only edge必须记为inherited baseline defect，不能归因于本轮制造；若在受影响interface中仍超过screen，其后续qualification义务仍存在。此审计没有waive gate、没有判candidate PASS、没有批准deformation。所有来源的文件hash、准确行号和原文摘录在`CONTINUITY_GATE_PROVENANCE_R1.json`。

出处：[SKIN_STATIC_GATE_SEMANTICS_AND_SCOPE_RECONCILIATION_R1_REPORT.md](../research/audits/skin_static_gate_semantics_and_scope_reconciliation_r1/SKIN_STATIC_GATE_SEMANTICS_AND_SCOPE_RECONCILIATION_R1_REPORT.md)

> v303/v1396均TARGETED_REVALIDATION且exact donor copy。Donor=candidate：L∞=0.655587911605835、L1=1.31117582321167。结论为 **INHERITED_BASELINE_DEFECT**，新增/恶化为0；244-only当然无法改变它。它不是candidate-introduced blocker，也不构成强制全局旧defect清零权限。其FIRST_WEB受影响interface的绝对screen仍fail，后续必须明确记录并qualify，不因exact-copy自动PASS。

出处：[SKIN_STATIC_GATE_SEMANTICS_AND_SCOPE_RECONCILIATION_R1_REPORT.md](../research/audits/skin_static_gate_semantics_and_scope_reconciliation_r1/SKIN_STATIC_GATE_SEMANTICS_AND_SCOPE_RECONCILIATION_R1_REPORT.md)

## 原报告与关键代码

- [audits/skin_static_gate_semantics_and_scope_reconciliation_r1/SKIN_STATIC_GATE_SEMANTICS_AND_SCOPE_RECONCILIATION_R1_REPORT.md](../research/audits/skin_static_gate_semantics_and_scope_reconciliation_r1/SKIN_STATIC_GATE_SEMANTICS_AND_SCOPE_RECONCILIATION_R1_REPORT.md)
- [audits/skin_static_gate_semantics_and_scope_reconciliation_r1/reconcile.py](../../src/legacy/audits/skin_static_gate_semantics_and_scope_reconciliation_r1/reconcile.py)
- [audits/skin_static_gate_semantics_and_scope_reconciliation_r1/verify_outputs.py](../../src/legacy/audits/skin_static_gate_semantics_and_scope_reconciliation_r1/verify_outputs.py)

## 输入、输出与大型证据

该目录原始成员 15 项；拟公开身份记录 14 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
