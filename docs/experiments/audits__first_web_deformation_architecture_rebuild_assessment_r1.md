# audits/first_web_deformation_architecture_rebuild_assessment_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> A 是局部空间分布/细化的架构探针，不是完成的美术 retopo。已有相对 corrective delta 在旧节点保持，在新增节点按原场插值，driver 表达式和目标完全保留；没有 sculpt 新 corrective、没有修改源批准资产。由于新 topology，候选 Key 数组尺寸会改变，不能声称候选 corrective 的数组逐字节完全相同。A 的边界一圈相邻 faces 可能变为 n-gon，正式版本若获授权还需边界拓扑/UV整理；本轮不做。域外原节点坐标和实际非零 weights 完全一致；重建 datablock 省略部分零值 sparse memberships，不改变数值影响。

出处：[FIRST_WEB_DEFORMATION_ARCHITECTURE_REBUILD_ASSESSMENT_R1_REPORT.md](../research/audits/first_web_deformation_architecture_rebuild_assessment_r1/FIRST_WEB_DEFORMATION_ARCHITECTURE_REBUILD_ASSESSMENT_R1_REPORT.md)

## 技术路线

> **RECOMMENDED_ROUTE = NONE_OF_THREE**。三条架构各做一份独立 DESIGN_ONLY POC，均未通过 F130 的显著改善门槛，因此按本轮指令停止各路线。完整 7 秒、F31 和六个旧姿态 regression 未执行，不把未知写成通过。四项 Human 审核均未填写。当前结论是没有路线已证明值得正式 rebuild，不是三类架构永远不可行。

出处：[FIRST_WEB_DEFORMATION_ARCHITECTURE_REBUILD_ASSESSMENT_R1_REPORT.md](../research/audits/first_web_deformation_architecture_rebuild_assessment_r1/FIRST_WEB_DEFORMATION_ARCHITECTURE_REBUILD_ASSESSMENT_R1_REPORT.md)

> 三份有界 POC 均未显著解决 F130 主 blocker，A 还让 F61 出现更明显浅沟；没有路线满足进入完整动作/旧姿态回归的前置门槛，因此当前不支持沿任一路线启动正式 rebuild。此选择限定于本轮证据，不宣称三类架构在所有设计下均不可能。

出处：[FIRST_WEB_DEFORMATION_ARCHITECTURE_REBUILD_ASSESSMENT_R1_REPORT.md](../research/audits/first_web_deformation_architecture_rebuild_assessment_r1/FIRST_WEB_DEFORMATION_ARCHITECTURE_REBUILD_ASSESSMENT_R1_REPORT.md)

## 测试结论

> **RECOMMENDED_ROUTE = NONE_OF_THREE**。三条架构各做一份独立 DESIGN_ONLY POC，均未通过 F130 的显著改善门槛，因此按本轮指令停止各路线。完整 7 秒、F31 和六个旧姿态 regression 未执行，不把未知写成通过。四项 Human 审核均未填写。当前结论是没有路线已证明值得正式 rebuild，不是三类架构永远不可行。

出处：[FIRST_WEB_DEFORMATION_ARCHITECTURE_REBUILD_ASSESSMENT_R1_REPORT.md](../research/audits/first_web_deformation_architecture_rebuild_assessment_r1/FIRST_WEB_DEFORMATION_ARCHITECTURE_REBUILD_ASSESSMENT_R1_REPORT.md)

> ZERO 四个普通视图：palmar full/thenar close/dorsal full/first-web close，三路线初判轮廓可接受。A 原节点最大变化 0.1694mm；B 0.00012mm 浮点量级；C 0mm。所有 screen NaN/Inf=0、collapsed face=0、degenerate edge=0、恢复各自ZERO=PASS；普通可见检查 gross tearing=0、gross penetration=0，残留虎口 fold 本身仍是 blocker。以上仅覆盖 ZERO 和四选中帧，不是完整421点安全验收，不证明 hidden intersections。未跑 Stage6/R3/true-cap/2127 edges/normal-dot 或其他复杂研究。

出处：[FIRST_WEB_DEFORMATION_ARCHITECTURE_REBUILD_ASSESSMENT_R1_REPORT.md](../research/audits/first_web_deformation_architecture_rebuild_assessment_r1/FIRST_WEB_DEFORMATION_ARCHITECTURE_REBUILD_ASSESSMENT_R1_REPORT.md)

## 失败原因与证据边界

> |路线|本次 POC|F130|F76/F205|停止原因|

出处：[FIRST_WEB_DEFORMATION_ARCHITECTURE_REBUILD_ASSESSMENT_R1_REPORT.md](../research/audits/first_web_deformation_architecture_rebuild_assessment_r1/FIRST_WEB_DEFORMATION_ARCHITECTURE_REBUILD_ASSESSMENT_R1_REPORT.md)

## 后续建议

> 4. 是否同意下一阶段只沿推荐路线实施正式 rebuild？YES / NO

出处：[FIRST_WEB_DEFORMATION_ARCHITECTURE_REBUILD_ASSESSMENT_R1_REPORT.md](../research/audits/first_web_deformation_architecture_rebuild_assessment_r1/FIRST_WEB_DEFORMATION_ARCHITECTURE_REBUILD_ASSESSMENT_R1_REPORT.md)

## 原报告与关键代码

- [audits/first_web_deformation_architecture_rebuild_assessment_r1/FIRST_WEB_DEFORMATION_ARCHITECTURE_REBUILD_ASSESSMENT_R1_REPORT.md](../research/audits/first_web_deformation_architecture_rebuild_assessment_r1/FIRST_WEB_DEFORMATION_ARCHITECTURE_REBUILD_ASSESSMENT_R1_REPORT.md)
- [audits/first_web_deformation_architecture_rebuild_assessment_r1/audit_topology.py](../../src/legacy/audits/first_web_deformation_architecture_rebuild_assessment_r1/audit_topology.py)
- [audits/first_web_deformation_architecture_rebuild_assessment_r1/build_pocs.py](../../src/legacy/audits/first_web_deformation_architecture_rebuild_assessment_r1/build_pocs.py)
- [audits/first_web_deformation_architecture_rebuild_assessment_r1/common.py](../../src/legacy/audits/first_web_deformation_architecture_rebuild_assessment_r1/common.py)
- [audits/first_web_deformation_architecture_rebuild_assessment_r1/deliver.py](../../src/legacy/audits/first_web_deformation_architecture_rebuild_assessment_r1/deliver.py)
- [audits/first_web_deformation_architecture_rebuild_assessment_r1/finalize.py](../../src/legacy/audits/first_web_deformation_architecture_rebuild_assessment_r1/finalize.py)
- [audits/first_web_deformation_architecture_rebuild_assessment_r1/inspection.py](../../src/legacy/audits/first_web_deformation_architecture_rebuild_assessment_r1/inspection.py)
- [audits/first_web_deformation_architecture_rebuild_assessment_r1/retain_source_action.py](../../src/legacy/audits/first_web_deformation_architecture_rebuild_assessment_r1/retain_source_action.py)
- [audits/first_web_deformation_architecture_rebuild_assessment_r1/screen_pocs.py](../../src/legacy/audits/first_web_deformation_architecture_rebuild_assessment_r1/screen_pocs.py)
- [audits/first_web_deformation_architecture_rebuild_assessment_r1/verify_pocs.py](../../src/legacy/audits/first_web_deformation_architecture_rebuild_assessment_r1/verify_pocs.py)

## 输入、输出与大型证据

该目录原始成员 118 项；拟公开身份记录 111 项。
- `audits/first_web_deformation_architecture_rebuild_assessment_r1/ROUTE_A_LOCAL_RETOPOLOGY_POC_R1.blend` → `hands-research-r1-selected-001-r1a.zip` / `payload/audits/first_web_deformation_architecture_rebuild_assessment_r1/ROUTE_A_LOCAL_RETOPOLOGY_POC_R1.blend`
- `audits/first_web_deformation_architecture_rebuild_assessment_r1/ROUTE_B_HELPER_BONE_POC_R1.blend` → `hands-research-r1-selected-001-r1a.zip` / `payload/audits/first_web_deformation_architecture_rebuild_assessment_r1/ROUTE_B_HELPER_BONE_POC_R1.blend`
- `audits/first_web_deformation_architecture_rebuild_assessment_r1/ROUTE_C_LOCAL_CAGE_POC_R1.blend` → `hands-research-r1-selected-001-r1a.zip` / `payload/audits/first_web_deformation_architecture_rebuild_assessment_r1/ROUTE_C_LOCAL_CAGE_POC_R1.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
