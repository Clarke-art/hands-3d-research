# audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> R2 Armature OFF/raw与ON/evaluated zero的ROI最大差为3.01639265208e-05mm，core最大差为4.65661287308e-06mm，全网格最大差为5.96700924622e-05mm。OFF/ON不是bitwise一致，差异落在项目原有0.0001mm zero校验范围内；本轮不建立新阈值。object/armature world matrices一致，parent inverse为单位阵，pose zero已验证。该浮点量级不能解释静态毫米级局部折陷。`DENT_ARMATURE_ZERO_POSE_AUDIT_R1.json`（链接见原报告）记录准确结果。

出处：[RIGHT_HAND_DORSAL_MCP_CONTOUR_DENT_CAUSAL_DIAGNOSIS_R1_REPORT.md](../research/audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/RIGHT_HAND_DORSAL_MCP_CONTOUR_DENT_CAUSAL_DIAGNOSIS_R1_REPORT.md)

## 技术路线

原报告未单独概述路线；以下实现文件与原报告共同界定方法，不能由文件名推断算法成功：

- [analyze_geometry.py](../../src/legacy/audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/analyze_geometry.py)
- [common.py](../../src/legacy/audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/common.py)
- [complete_diagnosis.py](../../src/legacy/audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/complete_diagnosis.py)
- [extract_lineage.py](../../src/legacy/audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/extract_lineage.py)
- [record_independent_checks.py](../../src/legacy/audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/record_independent_checks.py)

## 测试结论

> 状态：**READY_FOR_HUMAN_DENT_CAUSAL_REVIEW**。本轮严格只读诊断，无repair。根因确认：**BASE_GEOMETRY_CONTOUR_DEFECT**。

出处：[RIGHT_HAND_DORSAL_MCP_CONTOUR_DENT_CAUSAL_DIAGNOSIS_R1_REPORT.md](../research/audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/RIGHT_HAND_DORSAL_MCP_CONTOUR_DENT_CAUSAL_DIAGNOSIS_R1_REPORT.md)

> 匹配展示采用2-ring21的proper刚性rotation/translation，scale=1，无反射或局部修正。配准矩阵、支持环RMS、原始与registered坐标全部保留。早期pre-RSSF局部形状仍是实际原形。`DENT_STAGE_LINEAGE_COMPARISON_R1.json`（链接见原报告）提供输入状态与每阶段诊断结果。没有用BASE的局部等同性伪称渲染了其整个旧网格。

出处：[RIGHT_HAND_DORSAL_MCP_CONTOUR_DENT_CAUSAL_DIAGNOSIS_R1_REPORT.md](../research/audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/RIGHT_HAND_DORSAL_MCP_CONTOUR_DENT_CAUSAL_DIAGNOSIS_R1_REPORT.md)

## 失败原因与证据边界

> 状态：**READY_FOR_HUMAN_DENT_CAUSAL_REVIEW**。本轮严格只读诊断，无repair。根因确认：**BASE_GEOMETRY_CONTOUR_DEFECT**。

出处：[RIGHT_HAND_DORSAL_MCP_CONTOUR_DENT_CAUSAL_DIAGNOSIS_R1_REPORT.md](../research/audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/RIGHT_HAND_DORSAL_MCP_CONTOUR_DENT_CAUSAL_DIAGNOSIS_R1_REPORT.md)

## 后续建议

> 唯一NEXT建议：**MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R1**。本轮未执行NEXT。

出处：[RIGHT_HAND_DORSAL_MCP_CONTOUR_DENT_CAUSAL_DIAGNOSIS_R1_REPORT.md](../research/audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/RIGHT_HAND_DORSAL_MCP_CONTOUR_DENT_CAUSAL_DIAGNOSIS_R1_REPORT.md)

## 原报告与关键代码

- [audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/RIGHT_HAND_DORSAL_MCP_CONTOUR_DENT_CAUSAL_DIAGNOSIS_R1_REPORT.md](../research/audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/RIGHT_HAND_DORSAL_MCP_CONTOUR_DENT_CAUSAL_DIAGNOSIS_R1_REPORT.md)
- [audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/analyze_geometry.py](../../src/legacy/audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/analyze_geometry.py)
- [audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/common.py](../../src/legacy/audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/common.py)
- [audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/complete_diagnosis.py](../../src/legacy/audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/complete_diagnosis.py)
- [audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/extract_lineage.py](../../src/legacy/audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/extract_lineage.py)
- [audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/record_independent_checks.py](../../src/legacy/audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/record_independent_checks.py)
- [audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/record_pending_roi.py](../../src/legacy/audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/record_pending_roi.py)
- [audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/render_dent.py](../../src/legacy/audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/render_dent.py)
- [audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/select_roi.py](../../src/legacy/audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/select_roi.py)
- [audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/verify_earlier_local_identity.py](../../src/legacy/audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/verify_earlier_local_identity.py)

## 输入、输出与大型证据

该目录原始成员 106 项；拟公开身份记录 103 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
