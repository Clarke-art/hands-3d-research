# audits/minimal_local_geometry_amendment_design_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 各write set分别核对nail/cap37/oldcap9/FIRST_WEB21/fresh R3 bounded graph/historical317/CMC20mm context，交集空。没有重开authority研究。原9对severe exact crossings未重新裁决；局部contact减少仅记INCIDENTAL_DIAGNOSTIC_EFFECT，不用作排名目标。

出处：[MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R1_REPORT.md](../research/audits/minimal_local_geometry_amendment_design_r1/MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R1_REPORT.md)

## 技术路线

> CANDIDATE_COUNT=3；CANDIDATE_A_WRITE_VERTEX_COUNT=15；B=18；C=22。TOPOLOGY_CHANGED_ANY_CANDIDATE=NO。RET0PO_REQUIRED=NO：当前有限方法失败不证明需要retopo。POSITION_ONLY_INSUFFICIENT=NOT_PROVED_GLOBALLY。

出处：[MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R1_REPORT.md](../research/audits/minimal_local_geometry_amendment_design_r1/MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R1_REPORT.md)

> 进一步在相同34点支持池尝试完整边界orientation约束：all-positive target碰到face3316三角[3346,3322,3330]的三个fixed vertices，当前fixed-boundary约束不可满足；保留该固定triangle原绕向后，4000次projection仍未收敛（remaining signed-area deficit2.4778756mm²）。非收敛不是所有position-only方法不可能的证明。该refinement未构成第4个Human candidate，没有新增topology或扩大正式写入权限。

出处：[MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R1_REPORT.md](../research/audits/minimal_local_geometry_amendment_design_r1/MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R1_REPORT.md)

## 测试结论

> **FAIL_CLOSED_POSITION_ONLY_GEOMETRY_DESIGN**。3个候选全部未达到完整要求，**RECOMMENDED_CANDIDATE=NONE，RECOMMENDED_WRITE_VERTEX_COUNT=0**。禁止应用或自动转入retopo。

出处：[MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R1_REPORT.md](../research/audits/minimal_local_geometry_amendment_design_r1/MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R1_REPORT.md)

> C中心原尖notch在实体/grazing中消失，接触/degenerate/reference-reversal/bow-tie检查也pass；但出现两个新过渡折边：

出处：[MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R1_REPORT.md](../research/audits/minimal_local_geometry_amendment_design_r1/MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R1_REPORT.md)

## 失败原因与证据边界

> ROOT_CAUSE_CLASS=BASE_GEOMETRY_CONTOUR_DEFECT。完整继承上一轮诊断：Stage4C raw/RSSF/R2 BIND/IDX15均可见；shading仅强调，armature zero只有浮点误差，skin不是静态根因，原INDEX poses没有支持放大。上一轮所有诊断文件保持原hash。

出处：[MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R1_REPORT.md](../research/audits/minimal_local_geometry_amendment_design_r1/MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R1_REPORT.md)

## 后续建议

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 原报告与关键代码

- [audits/minimal_local_geometry_amendment_design_r1/MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R1_REPORT.md](../research/audits/minimal_local_geometry_amendment_design_r1/MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R1_REPORT.md)
- [audits/minimal_local_geometry_amendment_design_r1/common.py](../../src/legacy/audits/minimal_local_geometry_amendment_design_r1/common.py)
- [audits/minimal_local_geometry_amendment_design_r1/design.py](../../src/legacy/audits/minimal_local_geometry_amendment_design_r1/design.py)
- [audits/minimal_local_geometry_amendment_design_r1/evaluate_candidates.py](../../src/legacy/audits/minimal_local_geometry_amendment_design_r1/evaluate_candidates.py)
- [audits/minimal_local_geometry_amendment_design_r1/finalize.py](../../src/legacy/audits/minimal_local_geometry_amendment_design_r1/finalize.py)
- [audits/minimal_local_geometry_amendment_design_r1/final_failure_review.py](../../src/legacy/audits/minimal_local_geometry_amendment_design_r1/final_failure_review.py)
- [audits/minimal_local_geometry_amendment_design_r1/geometry_metrics.py](../../src/legacy/audits/minimal_local_geometry_amendment_design_r1/geometry_metrics.py)
- [audits/minimal_local_geometry_amendment_design_r1/independent_contact_audit.py](../../src/legacy/audits/minimal_local_geometry_amendment_design_r1/independent_contact_audit.py)
- [audits/minimal_local_geometry_amendment_design_r1/render_candidates.py](../../src/legacy/audits/minimal_local_geometry_amendment_design_r1/render_candidates.py)
- [audits/minimal_local_geometry_amendment_design_r1/study_c.py](../../src/legacy/audits/minimal_local_geometry_amendment_design_r1/study_c.py)

## 输入、输出与大型证据

该目录原始成员 113 项；拟公开身份记录 112 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
