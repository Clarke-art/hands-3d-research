# audits/minimal_local_geometry_amendment_design_r3

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 本轮完成read-only因果分析、真实参照提取、两种position-only目标、collision-aware S3–S5设计求解和普通实体证据。没有合格Human candidate，没有应用、生产修改、topology/retopo、weight/bone/joint/RSSF改动、fresh ownership R3重跑、Full42、Stage6A/6B或promotion。

出处：[MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R3_REPORT.md](../research/audits/minimal_local_geometry_amendment_design_r3/MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R3_REPORT.md)

> Rigid/similarity alignment使用frozen joint-spacing比例、bone frame和选定surface landmarks；normal refinement只改变chart旋转。整个source surface只作刚体加uniform scale显示，没有非刚性warp。其权威标签仅GEOMETRIC_SHAPE_PRIOR，非anatomy authority。Reference2的0 depth并不要求把目标沟谷抹平；本手MCP、指距、整体宽度、dorsal arch、外围silhouette保持source约束。

出处：[MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R3_REPORT.md](../research/audits/minimal_local_geometry_amendment_design_r3/MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R3_REPORT.md)

## 技术路线

> 本轮完成read-only因果分析、真实参照提取、两种position-only目标、collision-aware S3–S5设计求解和普通实体证据。没有合格Human candidate，没有应用、生产修改、topology/retopo、weight/bone/joint/RSSF改动、fresh ownership R3重跑、Full42、Stage6A/6B或promotion。

出处：[MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R3_REPORT.md](../research/audits/minimal_local_geometry_amendment_design_r3/MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R3_REPORT.md)

> CCD边界：cubic coplanarity-event检查是projection与每个accepted endpoint硬gate的补强。恒定全程coplanar事件不由cubic roots完全认证；本轮没有声称global continuous-feasibility或topology-limit证明。该缺口列入下一方法研究。独立最终审核还检查全部局部baseline normal hemispheres，六个修正试解没有face reversal。

出处：[MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R3_REPORT.md](../research/audits/minimal_local_geometry_amendment_design_r3/MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R3_REPORT.md)

## 测试结论

> **FAIL_CLOSED_R3_GEOMETRY_DESIGN · D_OPTIMIZER_NONCONVERGENCE · STOP — HUMAN REVIEW**

出处：[MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R3_REPORT.md](../research/audits/minimal_local_geometry_amendment_design_r3/MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R3_REPORT.md)

> R2 S3/S4/S5的8个相关点均保存baseline/failed xyz、world/frame displacement及contact features。Face204-only与207-only均无该crossing，双方移动才有。Normal-only不cross，tangentX-only及tangentY-only都cross；单点移动不足，恢复3308或3324分别去掉crossing。因此这不是只由一侧或大法线旋转驱动的机制。

出处：[MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R3_REPORT.md](../research/audits/minimal_local_geometry_amendment_design_r3/MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R3_REPORT.md)

## 失败原因与证据边界

> 六个最终选定试解（A-V2/B-V3）在向量化exact point/segment/coplanar审核及独立scalar segment审核中均无新增face-pair family；boundary screen均0新增fold，native degenerate/bowtie/reverse均无新增，support外exact0位移。每步accepted/rejected trace、dynamic feature IDs/barycentric/side axes、CCD events、area/normal gates和终止原因均保存。

出处：[MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R3_REPORT.md](../research/audits/minimal_local_geometry_amendment_design_r3/MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R3_REPORT.md)

> 新方向阻碍主要为2182/3330：两面shared edge79/955上的接触合法，离开公共edge的接触被阻断。这类active set导致保守side projection与backtracking停滞，204/207不是唯一需要约束的pair。四个基于新阻碍的normal-first机械motion-seed假设（不是target/clearance）分别被3329/3331、2182/3330、3312/3313等新pair拒绝，保存完整证据，没有把这些seed当候选。

出处：[MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R3_REPORT.md](../research/audits/minimal_local_geometry_amendment_design_r3/MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R3_REPORT.md)

## 后续建议

> CCD边界：cubic coplanarity-event检查是projection与每个accepted endpoint硬gate的补强。恒定全程coplanar事件不由cubic roots完全认证；本轮没有声称global continuous-feasibility或topology-limit证明。该缺口列入下一方法研究。独立最终审核还检查全部局部baseline normal hemispheres，六个修正试解没有face reversal。

出处：[MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R3_REPORT.md](../research/audits/minimal_local_geometry_amendment_design_r3/MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R3_REPORT.md)

> 冻结source已有投影quad bowtie flags2771/3332/3351，native area并不退化。它们是投影诊断，不能隐藏或把零新增写成绝对零。六个选定试解的绝对flags仍是这三项：S3/S4 affected3332，S5 affected2771/3332。循环防止新增flag，但没有消除既有affected flags，所以绝对no-bowtie候选条件也未成立；全体失败。下一方法还需处理这些既有局部fold，同时保持nonpenetration。

出处：[MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R3_REPORT.md](../research/audits/minimal_local_geometry_amendment_design_r3/MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R3_REPORT.md)

## 原报告与关键代码

- [audits/minimal_local_geometry_amendment_design_r3/MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R3_REPORT.md](../research/audits/minimal_local_geometry_amendment_design_r3/MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R3_REPORT.md)
- [audits/minimal_local_geometry_amendment_design_r3/build_outputs.py](../../src/legacy/audits/minimal_local_geometry_amendment_design_r3/build_outputs.py)
- [audits/minimal_local_geometry_amendment_design_r3/causal.py](../../src/legacy/audits/minimal_local_geometry_amendment_design_r3/causal.py)
- [audits/minimal_local_geometry_amendment_design_r3/collision_engine.py](../../src/legacy/audits/minimal_local_geometry_amendment_design_r3/collision_engine.py)
- [audits/minimal_local_geometry_amendment_design_r3/common.py](../../src/legacy/audits/minimal_local_geometry_amendment_design_r3/common.py)
- [audits/minimal_local_geometry_amendment_design_r3/contact_geometry.py](../../src/legacy/audits/minimal_local_geometry_amendment_design_r3/contact_geometry.py)
- [audits/minimal_local_geometry_amendment_design_r3/extract_frames.py](../../src/legacy/audits/minimal_local_geometry_amendment_design_r3/extract_frames.py)
- [audits/minimal_local_geometry_amendment_design_r3/finalize.py](../../src/legacy/audits/minimal_local_geometry_amendment_design_r3/finalize.py)
- [audits/minimal_local_geometry_amendment_design_r3/forensic.py](../../src/legacy/audits/minimal_local_geometry_amendment_design_r3/forensic.py)
- [audits/minimal_local_geometry_amendment_design_r3/path_seed_probe.py](../../src/legacy/audits/minimal_local_geometry_amendment_design_r3/path_seed_probe.py)
- [audits/minimal_local_geometry_amendment_design_r3/prepare_reference_review.py](../../src/legacy/audits/minimal_local_geometry_amendment_design_r3/prepare_reference_review.py)
- [audits/minimal_local_geometry_amendment_design_r3/references.py](../../src/legacy/audits/minimal_local_geometry_amendment_design_r3/references.py)
- [audits/minimal_local_geometry_amendment_design_r3/reference_features.py](../../src/legacy/audits/minimal_local_geometry_amendment_design_r3/reference_features.py)

## 输入、输出与大型证据

该目录原始成员 90 项；拟公开身份记录 89 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
