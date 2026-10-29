# PALMAR_DIGIT_ROOT_SURFACE_IRREGULARITY_CAUSAL_DIAGNOSIS_R1

结果：**UNRESOLVED — STOP — HUMAN REVIEW**。Human 原截图未包含在本次附件中，不能唯一匹配 case / pose / ROI。已完成可复查的候选区域诊断，不把候选结论冒充 Human 实际目标结论。

## 七个问题的证据回答

1. 候选普通实体中的三角折面包含实际 native geometry ridge / crease。RAW、flat / source-native、wire 和真实截面均保留几何折线。Smooth calculated normals 会改变可见度；无 custom split normals 或 sharp edges，不能把它简单归结为 normal-only artifact。自然低模 faceting 与不可接受局部 fold 的产品判断仍由 Human 完成。
2. 候选在 RAW 已有，ZERO 未引入新缺陷。ROI RAW→ZERO 最大坐标差 0.00003003 mm，属于本项目 saved evaluated float 差异。生产资产没有变更。
3. 当前 IDX_MCP_15 / IDX_MCP_30 对候选局部有变化，TH_IP_15 无 driver support。没有证据说 Stage6 pose 引入整个候选折面。IDX30 最大位移 1.78755 mm、edge ratio 范围 0.96648–1.10080、总面积比 1.00184；中央値接近 ZERO numerical noise，不能用单个最大值推断整体 pinch。
4. 从冻结 rest matrices、既有 weights 和保存角度进行纯代数 LBS reconstruction，ROI 最大误差分别约 0.000063 / 0.000060 / 0.000030 mm。这解释 limited IDX deformation 的机制，不证明权重失败或关节变换错误。基线 geometry / 着色可见度是主要候选因素，Human 目标归因仍未解决。
5. current9 在候选 ROI 中 face / vertex direct overlap = 0，1/2-ring neighborhood overlap = 0。IDX 三对是 SAME_DRIVER_ONLY，TH_IP 六对是 NO_MEANINGFUL_OVERLAP。空间近邻不等于因果关系；本轮未重新裁决 pairs。Human 目标的 overlap 仍为 UNRESOLVED。
6. Source official L1 / Stage2 L1 已有粗 root crease；工程 root band 在 cached Stage4A_R2_BASE 可见，Stage4B_RSSF 的 native adjacent-face dihedral 更强。例 edge2810 / faces1840,2954：Stage4A_R2 0.6666° → current RAW 11.5220°。同 topology、exact coordinate ancestry / oriented face cycles 可恢复（本 ROI missing native faces = 0）。Donor transfer 在 ROI 外围两个顶点3306/3314有移动，不能宣称整个 ROI 与 pre-donor 相同；它未改变所列 interior angle witnesses。最早具体 operation 未新增 replay，不作超出 snapshot 证据的宣称。
7. 若 Human 确认此候选且认为不能接受，最小层次首先是局部 base geometry continuity 与显示着色设计；normal-only 足够性未证明，当前数据未支持直接改 weights / rig。这里只记录建议，不执行 NEXT / repair。

## 匹配、方法与限制

- MATCHED_CASE / MATCHED_POSE = null，MATCH_CONFIDENCE = UNRESOLVED_NO_SCREENSHOT。候选主要视图 IDX_MCP_30__LOCAL_ALTERNATE，原图尺寸1600×1100。三个 case 的 PRIMARY / ALTERNATE 原始视图均已保存到 candidate_source_views。
- ROI 由已实际检查图片中的矩形像素选区 + 最近正射线 native-face hit 定位，92 vertices / 62 faces。不是 anatomy authority。每个 hit 记录 face、barycentric 和世界坐标。
- Saved RAW / ZERO / three poses / historical comparator 均复用，没有 pose setter、Full42 rerun 或微 probe。三条截面使用 Blender native loop triangulation。Source 截面用 exact ancestry seed 锚点；source display fixed rigid fit RMS0.895mm，只用于可视对照，不把 offset 当 defect。
- SOURCE_NATIVE 所有3414 faces都是 flat flags；原 review 显示副本所有 faces smooth。这一既有区别是显示语义差异，不是本轮资产漂移。当前与 pre-donor 的 smooth / sharp / custom normal payload 一致，Blender5.1实际 readback 已记录。
- 顶点/face最大角或 flat画面不直接构成人体阈值。本轮没有构造 anatomical threshold、没有 product PASS、没有将审美判断替换为 machine 判断。

## 冻结与当前 Human response

已填写 response 来源：`<USER_HOME>\Downloads\CURRENT_FULL_STAGE6A_CROSSING_HUMAN_RESPONSE_R1.json`，不在工作区内。前后 SHA-256 `59c2447b6a11c7a97a74c2ca73092d507ffa7f84f4198dd64ff4e44935db6e9b`，字节完整保留。3 case / 9 pair / YES 与用户交接一致。**HOLD_NOT_CLOSED**；未复制为 active acceptance authority，未创建 approval receipt 或 Human closure。

FULL42_RERUN=0；DIAGNOSTIC_ONLY_MICRO_POSE_PROBE_COUNT=0；GEOMETRY_WRITES=0；WEIGHT_WRITES=0；NORMAL_WRITES=0；RIG_WRITES=0；JOINT_WRITES=0；MATERIAL_WRITES=0；MODIFIER_WRITES=0；STAGE6B_RUNS=0；PRODUCTION_PROMOTION=NO。这些计数指 qualified assets；render display copies 创建不同着色/overlay是本轮获准诊断可视化。

最终全字段和候选字段分开保存在 `PALMAR_DIGIT_ROOT_SURFACE_IRREGULARITY_CAUSAL_DIAGNOSIS_R1_STATUS.json`。Human target ROOT_CAUSE_CLASS=UNRESOLVED。NEXT=PALMAR_DIGIT_ROOT_EVIDENCE_EXPANSION_R1（只记录、不执行）。STOP — HUMAN REVIEW。
