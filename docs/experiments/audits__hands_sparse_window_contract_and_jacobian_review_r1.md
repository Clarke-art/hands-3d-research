# audits/hands_sparse_window_contract_and_jacobian_review_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 上轮实际执行了对每个非所有权区域的 `depth ≤ min(0.5, C1同刻depth+0.02)`，见 `window_problem.py:153`（链接见原报告）。因此所有非目标区域都被套上了绝对 0.5mm 上限，而不只是重点校正的小指。

出处：[FINAL_CONTRACT_AND_JACOBIAN_REVIEW.md](../research/audits/hands_sparse_window_contract_and_jacobian_review_r1/FINAL_CONTRACT_AND_JACOBIAN_REVIEW.md)

> | 固定状态 | 原活动任务 | 非目标键历史见证 | 真实顶点侵入 | 与 0.5mm 的冲突 |

出处：[FINAL_CONTRACT_AND_JACOBIAN_REVIEW.md](../research/audits/hands_sparse_window_contract_and_jacobian_review_r1/FINAL_CONTRACT_AND_JACOBIAN_REVIEW.md)

## 技术路线

> **结论：拟议局部合同没有发现原来的固定边界矛盾，但适用范围仍须 Human 明确认可；现有 11149 行模型的 Jacobian 数值对照通过，实测仍需 31.089–33.458 秒，未达到 ≤8 秒预筛门槛。不建议现在授权路线 A 正式求解。** 此结果既不证明路线 A 或冻结 Rig 不可行，也不证明存在可行运动。

出处：[FINAL_CONTRACT_AND_JACOBIAN_REVIEW.md](../research/audits/hands_sparse_window_contract_and_jacobian_review_r1/FINAL_CONTRACT_AND_JACOBIAN_REVIEW.md)

> ROUTE_A_NEXT_EXPERIMENT = NOT_RECOMMENDED

出处：[FINAL_CONTRACT_AND_JACOBIAN_REVIEW.md](../research/audits/hands_sparse_window_contract_and_jacobian_review_r1/FINAL_CONTRACT_AND_JACOBIAN_REVIEW.md)

## 测试结论

> **结论：拟议局部合同没有发现原来的固定边界矛盾，但适用范围仍须 Human 明确认可；现有 11149 行模型的 Jacobian 数值对照通过，实测仍需 31.089–33.458 秒，未达到 ≤8 秒预筛门槛。不建议现在授权路线 A 正式求解。** 此结果既不证明路线 A 或冻结 Rig 不可行，也不证明存在可行运动。

出处：[FINAL_CONTRACT_AND_JACOBIAN_REVIEW.md](../research/audits/hands_sparse_window_contract_and_jacobian_review_r1/FINAL_CONTRACT_AND_JACOBIAN_REVIEW.md)

> 窗口为展示时间 1.2414275–2.134284s。六槽三次 B-spline 中每个状态流仅第 2、3 槽自由；其在两端的基函数值与一阶导数恒为零。26 流共 52 个自由系数，对任意系数，入口、出口的位置和速度修正均为零。

出处：[FINAL_CONTRACT_AND_JACOBIAN_REVIEW.md](../research/audits/hands_sparse_window_contract_and_jacobian_review_r1/FINAL_CONTRACT_AND_JACOBIAN_REVIEW.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

> **结论：拟议局部合同没有发现原来的固定边界矛盾，但适用范围仍须 Human 明确认可；现有 11149 行模型的 Jacobian 数值对照通过，实测仍需 31.089–33.458 秒，未达到 ≤8 秒预筛门槛。不建议现在授权路线 A 正式求解。** 此结果既不证明路线 A 或冻结 Rig 不可行，也不证明存在可行运动。

出处：[FINAL_CONTRACT_AND_JACOBIAN_REVIEW.md](../research/audits/hands_sparse_window_contract_and_jacobian_review_r1/FINAL_CONTRACT_AND_JACOBIAN_REVIEW.md)

> | C1 后续 Human 回执，2026-10-10 | `Human accepted as overall baseline, local defect not accepted` | 接受整体原速基线，局部缺陷未接受；不是几何安全批准。见 `HUMAN_AUTHORITY_RECEIPT.json`（链接见原报告）。 |

出处：[FINAL_CONTRACT_AND_JACOBIAN_REVIEW.md](../research/audits/hands_sparse_window_contract_and_jacobian_review_r1/FINAL_CONTRACT_AND_JACOBIAN_REVIEW.md)

## 原报告与关键代码

- [audits/hands_sparse_window_contract_and_jacobian_review_r1/FINAL_CONTRACT_AND_JACOBIAN_REVIEW.md](../research/audits/hands_sparse_window_contract_and_jacobian_review_r1/FINAL_CONTRACT_AND_JACOBIAN_REVIEW.md)
- [audits/hands_sparse_window_contract_and_jacobian_review_r1/review_diagnostics.py](../../src/legacy/audits/hands_sparse_window_contract_and_jacobian_review_r1/review_diagnostics.py)
- [audits/hands_sparse_window_contract_and_jacobian_review_r1/supplement_evidence.py](../../src/legacy/audits/hands_sparse_window_contract_and_jacobian_review_r1/supplement_evidence.py)

## 输入、输出与大型证据

该目录原始成员 14 项；拟公开身份记录 14 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
