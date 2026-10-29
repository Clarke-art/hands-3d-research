# RIGHT_HAND_FIRST_WEB_SKINNING_FIELD_VS_DOF_DIAGNOSIS_R1

**FINAL_DIAGNOSIS = INSUFFICIENT_EVIDENCE**

WEIGHT_FIELD_PROBE = RUN（恰好一份）；F130_HUMAN_VISIBLE_RESULT = NO_CLEAR_IMPROVEMENT_BLOCKER_OPEN；FROZEN_FALLBACK_UNCHANGED = YES。STOP — HUMAN REVIEW。

本次出现的是**因果隔离控制失效**，而不是资产污染或执行缺失：只允许改变的 WRIST/THUMB 两项实际仅覆盖继承最坏8边完整权重向量 L1 差的9.45%–35.18%。直接读取的 INDEX MCP/PIP/DIP 项贡献更大，且按本轮要求逐点固定保留。失败的两项 probe 不能排除这些未改变的静态场仍不合理，因此不能推出整个21-bone deformation basis不足。此处使用 INSUFFICIENT_EVIDENCE 的原因是 A/B 所需隔离对照没有成立；并非因为还想多做候选或不愿作选择。

|题|回答|口径|
|---|---|---|
|Q1 F130 fold 与 WRIST/THUMB 高 ratio-gradient 区域空间一致？|**YES**|7/8 inherited band edges have pair-ratio gradients above the ROI mean. Spatial association only; the pair is not the largest full-vector contribution.|
|Q2 多个 folded frame 是否要求大体一致的局部 transfer 方向？|**MIXED**|F127/F160/F205 corresponding-point closure projections broadly agree, but several F130 signs reverse. These tiny edge-closure proxies do not establish a visible static-weight conflict.|
|Q3 改善方向是否明显破坏 F110/F176？|**NO**|Both 0.02 micro-transfer directions preserve the two smooth-frame appearances; no visibly destructive direction has been demonstrated.|
|Q4 是否执行 ONE deterministic weight-field candidate？|**YES**|One unique Dirichlet harmonic R field, 234-node inherited ROI / 70 pinned boundary nodes / 164 free nodes.|
|Q5 weight-gradient 是否实质性降低？|**YES**|YES for the preselected F130 8-edge pair-ratio band: mean gradient decreases 34.83% (7/8 edges decrease). Whole ROI mean/max do not decrease; full-vector band L1 decreases only 11.62%. Do not generalize this answer to the whole weight field.|
|Q6 F130 blocker 是否明显改善？|**NO**|Deep stepped fold remains in both prescribed views; the pair field has not made F130 natural.|
|Q7 F127/F160/F205 是否一致改善？|**NO**|No consistent visible blocker improvement across the three other folded frames.|
|Q8 F110/F176 是否保持自然平滑？|**YES**|The two control frames stay smooth; no obvious new bulge/flap/hard shelf/palm-volume distortion in the matched views.|
|Q9 最终诊断|**INSUFFICIENT_EVIDENCE**|Causal isolation for the requested whole-field-versus-21-bone-DOF question fails: the allowed manipulated pair accounts for only 9–35% of the inherited endpoint-vector L1. Most of the actual gradient is held constant in directly observed INDEX influences. Asset and pair-intervention controls pass, but an unsuccessful pair-field probe cannot distinguish an untested static full-vector field problem from a DOF limit.|


继承权威：已经读取上一阶段 report、attribution、design、measurements、verification、protection及 DESIGN_ONLY candidate，candidate SHA256 `373b8516fe45d8f9f83e752eeb3607e7bfd7e3135ed8467ad22272a99ac355bb`。只读打开其对象/Action元数据；未重建 topology、未复做其实验。Human 已关闭 LEVEL_1 topology route。正式 fallback SHA256 `4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2` 保持，状态继承 PROTECTED_FROZEN_FALLBACK，blocker仍OPEN。

输入来自原 frozen mesh + 原 axis-corrected Action，未用 topology candidate 作新权重资产起点。继续同一11.5–18.5秒/421 observations，使用六决策帧110/127/130/160/176/205及上一阶段相机。禁止路线均未开启；也没有扩大到对INDEX做扰动或优化。完整 weight vector 的读取是本轮明确要求，记录 INDEX 项是因为8条指定边上存在直接数据，不是猜测。

只读完整向量的重要新事实：

|原F130代表边|WRIST+THUMB占全部向量L1差|保留的INDEX MCP/PIP/DIP L1贡献合计|
|---|---|---|
|2035–646|28.52%|0.3875|
|2035–3143|9.45%|0.4356|
|2041–2852|31.49%|0.3360|
|388–2031|29.60%|0.3495|
|1525–2825|29.23%|0.3197|
|1566–3143|35.18%|0.3305|
|645–1577|31.37%|0.2302|
|1447–338|33.78%|0.2578|

所以“空间重合”是YES，但不能把“最大两项的bone名称是WRIST/THUMB”当成“完整向量梯度主要由这两项产生”。例如2035–3143，完整L1差0.4900，WRIST/THUMB两项只贡献0.0463，其余大部分是INDEX链项；其pair ratio gradient本来只有0.00218/mm。所有端点完整16项向量见 READ_ONLY_WEIGHT_FIELD_R1.json，未重做strain census或相关系数研究。

微扰严格一次固定幅度 δw=0.02，复用原最坏8条边的14个唯一端点。先分别对14点同时执行 WRIST→THUMB / THUMB→WRIST 两方向，渲染六帧×两视角；再每点独立执行同幅度±扰动，测实际 evaluated vertex displacement。每次恢复原值，其他bones逐点完全一致，每点S不变（float32误差界1e−7）；ZERO恢复误差0mm。局部Jacobian用实际求值的中心差分 `(X_plus-X_minus)/(2δw)`，**没有重建LBS矩阵链**。

方向证据定义为该点位移在“朝向同一代表边另一端”的投影，这是关闭局部边间距的响应代理，不是已有自然软组织目标面。F127/F160/F205多数对应点偏好同号；F130某些点反号。例如点338投影依次+0.0107/−0.0104/+0.0381/+0.0835mm；点1525为+0.0207/−0.0112/+0.0503/+0.0802mm；点2825为−0.0188/+0.0112/−0.0470/−0.0779mm。F130整个微扰的最大位移仅0.0647mm，普通实体视图没有明显改善或破坏。这样微小的代理符号反转不足以宣告有Human-visible STATIC_WEIGHT_CONFLICT；F110/F176两方向均保持平滑。故本次仍未排除静态pair field可能性，执行唯一允许的确定性probe。门槛理由见 SENSITIVITY_GATE_R1.json。

静态 probe：沿用上一轮234节点ROI/70节点外边界，在164个内部点求一次Dirichlet harmonic解。图conductance固定为1/rest_edge_length，没有smoothing strength、参数sweep、目标姿态拟合、人工刷权重或自动搜索。固定boundary原R，每点S保留，其他所有骨骼项原值不变，R限定[0,1]。mesh/topology/Basis/rest/21 bones/Action/corrective/driver均保持。唯一文件 `audits/right_hand_first_web_skinning_field_vs_dof_diagnosis_r1/RIGHT_HAND_FIRST_WEB_WEIGHT_FIELD_PROBE_R1.blend`，SHA256 `d7d895b5018c80e7b2571884696ae7a5982aed8d1fb06c84f0db60a6e49d1f96`，重新打开验证通过。

梯度结果必须区分三个口径：

|口径|Before|Probe|解释|
|---|---|---|---|
|F130原8边 pair ratio-gradient均值|0.02642486/mm|0.01722230/mm|下降34.83%；7/8下降，1/8上升|
|全部ROI边 pair ratio-gradient均值|0.00996587/mm|0.01002301/mm|没有下降；固定边界可保留/重分配陡变|
|全部ROI边最大 pair ratio-gradient|0.06063801/mm|0.06063801/mm|没有下降|
|原8边完整向量L1差均值|0.48431547|0.42803863|仅下降11.62%，被固定项的主要差仍在|

Q5的YES只指本轮预先选定主带的pair ratio-gradient，不能被解读为整个ROI/完整weight-vector transition已被有效重建。单一harmonic候选未能形成“实际主导的完整梯度已经被消除”的对照，因此也不能将没有视觉收益解释为所有静态weights都不可能。

普通可见结果：F130两指定视角仍保留主阶梯深折，没有自然很多；F127/F160/F205也没有一致明显改善。F110/F176保持平滑，未见新bulge/flap/hard shelf或明显palm-volume distortion。这里只判六帧，不虚构完整7秒验证。旧approved corrective在六帧都自然求值0.0，未强制ON/OFF。候选原Basis/rest完全不变，ZERO求值最大float差0.000240858mm，恢复自身ZERO误差0mm；S误差2.98023224e-08，权重和范围[0.999999925494194, 1.0000001015141606]。

局部表面差只用于确认干预发生，不作为改善分数。六帧ROI最大差依次为F110 0.5546mm, F127 0.6629mm, F130 0.4602mm, F160 0.6159mm, F176 0.5153mm, F205 2.2650mm. 三张证据PNG为 sensitivity、F130 pair-field对比、六帧对比；review页面可以查看同帧同相机原图。没有第二套候选，没有开启其它influence实验。

结论边界：本轮支持“仅重构WRIST/THUMB比例的唯一probe未解决blocker”。本轮既未证明完整静态weight field可解决，也未证明21-bone deformation DOF不足。由于直接观察到主要固定influence梯度，A/B因果隔离条件不成立，最终选INSUFFICIENT_EVIDENCE。资产/求值/干预控制PASS与因果隔离FAIL分别记录在 CAUSAL_DISCRIMINATION_CONTROL_R1.json，避免混淆。等待Human决定；不自动扩展研究或启动helper。

冻结fallback、上一阶段candidate/audit、生产pointer与sample输入哈希均在结束复核。未move pointer、未promotion、未正式weight rebuild、未新增helper/cage/corrective、未开始左手或Web。未执行hidden crossing、normal-dot、R3、true-cap、2127-edge或逐顶点大型audit。完整手部位置快照已缩减为234节点ROI记录。

STOP — HUMAN REVIEW。
