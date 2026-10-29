# audits/original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 初始38点 scope 漏掉共享相同 donor edges 的第一圈，205/207已有 contact 增长0.002749mm，严格 FAIL。其失败证据保留。依据真实 ancestry 补齐第一圈后得到54点探针，没有调整目标曲面或运行 optimizer。

出处：[ORIGINAL_SOURCE_DORSAL_MCP_LINEAGE_AND_PATCH_TRANSFER_FEASIBILITY_R1_REPORT.md](../research/audits/original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1/ORIGINAL_SOURCE_DORSAL_MCP_LINEAGE_AND_PATCH_TRANSFER_FEASIBILITY_R1_REPORT.md)

## 技术路线

> | `DONOR_CORRESPONDENCE_METHOD` | EXACT_SUBDIVISION_GRAPH_ANCESTRY + HISTORICAL_SPLIT_EDGE_WEIGHTS + FROZEN_RSSF_LINEAR_TRANSFORM |

出处：[ORIGINAL_SOURCE_DORSAL_MCP_LINEAGE_AND_PATCH_TRANSFER_FEASIBILITY_R1_REPORT.md](../research/audits/original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1/ORIGINAL_SOURCE_DORSAL_MCP_LINEAGE_AND_PATCH_TRANSFER_FEASIBILITY_R1_REPORT.md)

## 测试结论

> **PASS_LOCAL_DONOR_SHAPE_TRANSFER_FEASIBLE — STOP — HUMAN REVIEW。**

出处：[ORIGINAL_SOURCE_DORSAL_MCP_LINEAGE_AND_PATCH_TRANSFER_FEASIBILITY_R1_REPORT.md](../research/audits/original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1/ORIGINAL_SOURCE_DORSAL_MCP_LINEAGE_AND_PATCH_TRANSFER_FEASIBILITY_R1_REPORT.md)

> 初始38点 scope 漏掉共享相同 donor edges 的第一圈，205/207已有 contact 增长0.002749mm，严格 FAIL。其失败证据保留。依据真实 ancestry 补齐第一圈后得到54点探针，没有调整目标曲面或运行 optimizer。

出处：[ORIGINAL_SOURCE_DORSAL_MCP_LINEAGE_AND_PATCH_TRANSFER_FEASIBILITY_R1_REPORT.md](../research/audits/original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1/ORIGINAL_SOURCE_DORSAL_MCP_LINEAGE_AND_PATCH_TRANSFER_FEASIBILITY_R1_REPORT.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

> CON3 后续 pole738两次位移及 smooth factor0.5 另改变邻域，但第一折叠在它之前已存在。`stage4a_engineer.py`的 `insert_loop` AST 与实际 R2_BASE producer相同；审计没有只凭文件名归因。

出处：[ORIGINAL_SOURCE_DORSAL_MCP_LINEAGE_AND_PATCH_TRANSFER_FEASIBILITY_R1_REPORT.md](../research/audits/original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1/ORIGINAL_SOURCE_DORSAL_MCP_LINEAGE_AND_PATCH_TRANSFER_FEASIBILITY_R1_REPORT.md)

## 原报告与关键代码

- [audits/original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1/ORIGINAL_SOURCE_DORSAL_MCP_LINEAGE_AND_PATCH_TRANSFER_FEASIBILITY_R1_REPORT.md](../research/audits/original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1/ORIGINAL_SOURCE_DORSAL_MCP_LINEAGE_AND_PATCH_TRANSFER_FEASIBILITY_R1_REPORT.md)
- [audits/original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1/analyze.py](../../src/legacy/audits/original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1/analyze.py)
- [audits/original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1/append_display.py](../../src/legacy/audits/original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1/append_display.py)
- [audits/original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1/common.py](../../src/legacy/audits/original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1/common.py)
- [audits/original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1/comparison_sheet.py](../../src/legacy/audits/original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1/comparison_sheet.py)
- [audits/original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1/extract.py](../../src/legacy/audits/original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1/extract.py)
- [audits/original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1/finalize.py](../../src/legacy/audits/original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1/finalize.py)
- [audits/original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1/gate_probe.py](../../src/legacy/audits/original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1/gate_probe.py)
- [audits/original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1/make_probe.py](../../src/legacy/audits/original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1/make_probe.py)
- [audits/original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1/native_contacts.py](../../src/legacy/audits/original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1/native_contacts.py)
- [audits/original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1/recover_rssf.py](../../src/legacy/audits/original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1/recover_rssf.py)
- [audits/original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1/render.py](../../src/legacy/audits/original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1/render.py)
- [audits/original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1/save_probe.py](../../src/legacy/audits/original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1/save_probe.py)

## 输入、输出与大型证据

该目录原始成员 166 项；拟公开身份记录 149 项。
- `audits/original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1/TEMP_DONOR_TRANSFER_DESIGN_ONLY.blend` → `hands-research-r1-selected-004.zip` / `payload/audits/original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1/TEMP_DONOR_TRANSFER_DESIGN_ONLY.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
