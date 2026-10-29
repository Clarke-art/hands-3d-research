# audits/minuet_stage_c_root_finger_spatial_feasibility_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> Q8：是。中心新增小指/F5：20面对、19个内部采样顶点、约1.2706 mm深度；邻居原有非目标白键穿入部分恶化。没有新增食指/中指或无名指/小指相交，但不能报告无新增冲突。

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_c_root_finger_spatial_feasibility_r1/FINAL_ANSWERS.md)

> 复用同一批静态姿态追加实际D5/E5/F5键体测量，没有再次求解。中心B小指/F5为20面对、19个内部采样顶点，最大采样深度1.2706 mm；原R1与A均无该命中。前邻居3.750 s虽清除邻指相交，但无名指进入非目标E5的内部见证深度由3.0873增加到4.3084 mm；后邻居3.850 s中指/D5约1.3014→1.4193 mm，主动E5浅层内部见证约0.1289→0.1654 mm。它们不能因为主动指腹锚点gap合格就被当作整体可行姿态。检查仅限这三个相邻白键及既有七黑键，未扩大到全88键。

出处：[LATE_CONFLICT_GEOMETRY.md](../research/audits/minuet_stage_c_root_finger_spatial_feasibility_r1/LATE_CONFLICT_GEOMETRY.md)

## 技术路线

> Q13：没有。正式动态求解0、动态候选0、新Action0、新完整Blend0、新视频0；仅一个三状态静态比较批次，固定root未重优化。

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_c_root_finger_spatial_feasibility_r1/FINAL_ANSWERS.md)

> 深度方法：仅使用原R3四指远端强权重皮肤区域；在近端切口加人工封口，以实体角判断内部点，再测到对指真实皮肤的距离，排除最近点在人工封口上的见证。它是局部采样内部深度证据，不是全局最大穿透或最小分离平移。真实面交线无需依赖封口。具体见证顶点、坐标、最近皮肤点及封口排除数保存在 ACTUAL_STATIC_COMPARISON.json。没有全手逐顶点检查。

出处：[LATE_CONFLICT_GEOMETRY.md](../research/audits/minuet_stage_c_root_finger_spatial_feasibility_r1/LATE_CONFLICT_GEOMETRY.md)

## 测试结论

> Q9：中心明显穿插仍在，释放指偏直与小指下沉存在风险；未取得自然度PASS。没有连续动作，不能评价抽动或原速自然度。

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_c_root_finger_spatial_feasibility_r1/FINAL_ANSWERS.md)

> Q13：没有。正式动态求解0、动态候选0、新Action0、新完整Blend0、新视频0；仅一个三状态静态比较批次，固定root未重优化。

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_c_root_finger_spatial_feasibility_r1/FINAL_ANSWERS.md)

## 失败原因与证据边界

> Human重点看：1）中心两指侧面和远端交叉；2）无名指释放是否自然；3）小指/F5新增干涉；4）相邻静态样本之间手型差异是否支持将来做连续验证。当前只能审核失败原因与路线，不是批准新演奏。

出处：[NATURAL_POSTURE_ASSESSMENT.md](../research/audits/minuet_stage_c_root_finger_spatial_feasibility_r1/NATURAL_POSTURE_ASSESSMENT.md)

> A的失败核心是E5触键与无名指释放时相向远端皮肤分离未能同时达标，不是D♯5不可避开。R4固定root A已清除该静态D♯5命中，仍保留约6.695 mm内部见证与92面对。B中心残差代价20617.51，ftol终止、optimality约693.7，仍有83面对；数值success只是停止条件。前邻居xtol终止且optimality很大也说明不应把成功标志当约束证明。R4沿用的最近顶点/法向场和8 mm启停阈值是非光滑局部代理；释放只靠原姿态保真与键面下界，没有完整释放准备可行通道。它们是下一步需要复评的约束表达，不是已证明的唯一根因。

出处：[FIXED_VS_BOUNDED_ROOT_FEASIBILITY.md](../research/audits/minuet_stage_c_root_finger_spatial_feasibility_r1/FIXED_VS_BOUNDED_ROOT_FEASIBILITY.md)

## 后续建议

> Q11：唯一建议先复评非冻结局部接触、释放准备、稳定表面分离约束及root带动闲置指的安全保护。取得中心与邻域可靠静态依据后，再单独授权有限事件窗口内的联合动态验证；root不预设为必需。

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_c_root_finger_spatial_feasibility_r1/FINAL_ANSWERS.md)

> Q12：没有证据要求整段重规划；有限D5→E5→后续交接事件窗口是下一轮最小研究范围，但尚未证明足够或边界连续可行。

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_c_root_finger_spatial_feasibility_r1/FINAL_ANSWERS.md)

## 原报告与关键代码

- [audits/minuet_stage_c_root_finger_spatial_feasibility_r1/FINAL_ANSWERS.md](../research/audits/minuet_stage_c_root_finger_spatial_feasibility_r1/FINAL_ANSWERS.md)
- [audits/minuet_stage_c_root_finger_spatial_feasibility_r1/LATE_CONFLICT_GEOMETRY.md](../research/audits/minuet_stage_c_root_finger_spatial_feasibility_r1/LATE_CONFLICT_GEOMETRY.md)
- [audits/minuet_stage_c_root_finger_spatial_feasibility_r1/NATURAL_POSTURE_ASSESSMENT.md](../research/audits/minuet_stage_c_root_finger_spatial_feasibility_r1/NATURAL_POSTURE_ASSESSMENT.md)
- [audits/minuet_stage_c_root_finger_spatial_feasibility_r1/NEXT_MOTION_PLANNING_DECISION.md](../research/audits/minuet_stage_c_root_finger_spatial_feasibility_r1/NEXT_MOTION_PLANNING_DECISION.md)
- [audits/minuet_stage_c_root_finger_spatial_feasibility_r1/FIXED_VS_BOUNDED_ROOT_FEASIBILITY.md](../research/audits/minuet_stage_c_root_finger_spatial_feasibility_r1/FIXED_VS_BOUNDED_ROOT_FEASIBILITY.md)
- [audits/minuet_stage_c_root_finger_spatial_feasibility_r1/bounded_static.py](../../src/legacy/audits/minuet_stage_c_root_finger_spatial_feasibility_r1/bounded_static.py)
- [audits/minuet_stage_c_root_finger_spatial_feasibility_r1/export_exact_model.py](../../src/legacy/audits/minuet_stage_c_root_finger_spatial_feasibility_r1/export_exact_model.py)
- [audits/minuet_stage_c_root_finger_spatial_feasibility_r1/finish.py](../../src/legacy/audits/minuet_stage_c_root_finger_spatial_feasibility_r1/finish.py)
- [audits/minuet_stage_c_root_finger_spatial_feasibility_r1/prepare.py](../../src/legacy/audits/minuet_stage_c_root_finger_spatial_feasibility_r1/prepare.py)
- [audits/minuet_stage_c_root_finger_spatial_feasibility_r1/validate_actual.py](../../src/legacy/audits/minuet_stage_c_root_finger_spatial_feasibility_r1/validate_actual.py)
- [audits/minuet_stage_c_root_finger_spatial_feasibility_r1/verify_delivery.py](../../src/legacy/audits/minuet_stage_c_root_finger_spatial_feasibility_r1/verify_delivery.py)

## 输入、输出与大型证据

该目录原始成员 61 项；拟公开身份记录 57 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
