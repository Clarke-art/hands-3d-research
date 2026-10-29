# audits/official_l1_product_rebase_feasibility_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 技术路线

> Official L1 的正常静态手型保留，但本次拟合与权重转移没有得到全部自然的代表动作。最小肉眼 blocker 是虎口上缘、连接食指根处的尖折 / 片状硬台阶，同一问题出现在 INDEX_MCP_45、CMC_OPP_30、FULL_OPP_L2 和 FULL_OPP_L3。一次局部平滑后仍存在，故停止本轮调整。此结论限定于本次 candidate，不能推断 Official L1 路线本身不可行。

出处：[OFFICIAL_L1_PRODUCT_REBASE_FEASIBILITY_R1_REPORT.md](../research/audits/official_l1_product_rebase_feasibility_r1/OFFICIAL_L1_PRODUCT_REBASE_FEASIBILITY_R1_REPORT.md)

> | WEIGHT_TRANSFER_METHOD | "Nearest surface + barycentric interpolation on an unsaved pose-registered R2 donor proxy; normalize 16 deform influences; no TIP weights" |

出处：[OFFICIAL_L1_PRODUCT_REBASE_FEASIBILITY_R1_REPORT.md](../research/audits/official_l1_product_rebase_feasibility_r1/OFFICIAL_L1_PRODUCT_REBASE_FEASIBILITY_R1_REPORT.md)

## 测试结论

> **FAIL_PRODUCT_REBASE_FEASIBILITY — STOP — HUMAN REVIEW**

出处：[OFFICIAL_L1_PRODUCT_REBASE_FEASIBILITY_R1_REPORT.md](../research/audits/official_l1_product_rebase_feasibility_r1/OFFICIAL_L1_PRODUCT_REBASE_FEASIBILITY_R1_REPORT.md)

> Official L1 的正常静态手型保留，但本次拟合与权重转移没有得到全部自然的代表动作。最小肉眼 blocker 是虎口上缘、连接食指根处的尖折 / 片状硬台阶，同一问题出现在 INDEX_MCP_45、CMC_OPP_30、FULL_OPP_L2 和 FULL_OPP_L3。一次局部平滑后仍存在，故停止本轮调整。此结论限定于本次 candidate，不能推断 Official L1 路线本身不可行。

出处：[OFFICIAL_L1_PRODUCT_REBASE_FEASIBILITY_R1_REPORT.md](../research/audits/official_l1_product_rebase_feasibility_r1/OFFICIAL_L1_PRODUCT_REBASE_FEASIBILITY_R1_REPORT.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 原报告与关键代码

- [audits/official_l1_product_rebase_feasibility_r1/OFFICIAL_L1_PRODUCT_REBASE_FEASIBILITY_R1_REPORT.md](../research/audits/official_l1_product_rebase_feasibility_r1/OFFICIAL_L1_PRODUCT_REBASE_FEASIBILITY_R1_REPORT.md)
- [audits/official_l1_product_rebase_feasibility_r1/build_static.py](../../src/legacy/audits/official_l1_product_rebase_feasibility_r1/build_static.py)
- [audits/official_l1_product_rebase_feasibility_r1/common.py](../../src/legacy/audits/official_l1_product_rebase_feasibility_r1/common.py)
- [audits/official_l1_product_rebase_feasibility_r1/finalize_review.py](../../src/legacy/audits/official_l1_product_rebase_feasibility_r1/finalize_review.py)
- [audits/official_l1_product_rebase_feasibility_r1/inspect_no_shadow.py](../../src/legacy/audits/official_l1_product_rebase_feasibility_r1/inspect_no_shadow.py)
- [audits/official_l1_product_rebase_feasibility_r1/local_weight_tune.py](../../src/legacy/audits/official_l1_product_rebase_feasibility_r1/local_weight_tune.py)
- [audits/official_l1_product_rebase_feasibility_r1/make_sheets.py](../../src/legacy/audits/official_l1_product_rebase_feasibility_r1/make_sheets.py)
- [audits/official_l1_product_rebase_feasibility_r1/render_zero_close.py](../../src/legacy/audits/official_l1_product_rebase_feasibility_r1/render_zero_close.py)
- [audits/official_l1_product_rebase_feasibility_r1/test_motion.py](../../src/legacy/audits/official_l1_product_rebase_feasibility_r1/test_motion.py)

## 输入、输出与大型证据

该目录原始成员 284 项；拟公开身份记录 284 项。
- `audits/official_l1_product_rebase_feasibility_r1/CMC_OPP_30_SHEET.png` → `hands-research-r1-selected-004.zip` / `payload/audits/official_l1_product_rebase_feasibility_r1/CMC_OPP_30_SHEET.png`
- `audits/official_l1_product_rebase_feasibility_r1/FULL_OPP_L1_SHEET.png` → `hands-research-r1-selected-004.zip` / `payload/audits/official_l1_product_rebase_feasibility_r1/FULL_OPP_L1_SHEET.png`
- `audits/official_l1_product_rebase_feasibility_r1/FULL_OPP_L2_SHEET.png` → `hands-research-r1-selected-004.zip` / `payload/audits/official_l1_product_rebase_feasibility_r1/FULL_OPP_L2_SHEET.png`
- `audits/official_l1_product_rebase_feasibility_r1/FULL_OPP_L3_SHEET.png` → `hands-research-r1-selected-004.zip` / `payload/audits/official_l1_product_rebase_feasibility_r1/FULL_OPP_L3_SHEET.png`
- `audits/official_l1_product_rebase_feasibility_r1/RIGHT_HAND_OFFICIAL_L1_INITIAL_TRANSFER_R1.blend` → `hands-research-r1-selected-004.zip` / `payload/audits/official_l1_product_rebase_feasibility_r1/RIGHT_HAND_OFFICIAL_L1_INITIAL_TRANSFER_R1.blend`
- `audits/official_l1_product_rebase_feasibility_r1/RIGHT_HAND_OFFICIAL_L1_PRODUCT_REBASE_CANDIDATE_R1.blend` → `hands-research-r1-selected-004.zip` / `payload/audits/official_l1_product_rebase_feasibility_r1/RIGHT_HAND_OFFICIAL_L1_PRODUCT_REBASE_CANDIDATE_R1.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
