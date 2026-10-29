# audits/right_hand_first_web_skinning_field_vs_dof_diagnosis_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 方向证据定义为该点位移在“朝向同一代表边另一端”的投影，这是关闭局部边间距的响应代理，不是已有自然软组织目标面。F127/F160/F205多数对应点偏好同号；F130某些点反号。例如点338投影依次+0.0107/−0.0104/+0.0381/+0.0835mm；点1525为+0.0207/−0.0112/+0.0503/+0.0802mm；点2825为−0.0188/+0.0112/−0.0470/−0.0779mm。F130整个微扰的最大位移仅0.0647mm，普通实体视图没有明显改善或破坏。这样微小的代理符号反转不足以宣告有Human-visible STATIC_WEIGHT_CONFLICT；F110/F176两方向均保持平滑。故本次仍未排除静态pair field可能性，执行唯一允许的确定性probe。门槛理由见 SENSITIVITY_GATE_R1.json。

出处：[RIGHT_HAND_FIRST_WEB_SKINNING_FIELD_VS_DOF_DIAGNOSIS_R1_REPORT.md](../research/audits/right_hand_first_web_skinning_field_vs_dof_diagnosis_r1/RIGHT_HAND_FIRST_WEB_SKINNING_FIELD_VS_DOF_DIAGNOSIS_R1_REPORT.md)

> 静态 probe：沿用上一轮234节点ROI/70节点外边界，在164个内部点求一次Dirichlet harmonic解。图conductance固定为1/rest_edge_length，没有smoothing strength、参数sweep、目标姿态拟合、人工刷权重或自动搜索。固定boundary原R，每点S保留，其他所有骨骼项原值不变，R限定[0,1]。mesh/topology/Basis/rest/21 bones/Action/corrective/driver均保持。唯一文件 `audits/right_hand_first_web_skinning_field_vs_dof_diagnosis_r1/RIGHT_HAND_FIRST_WEB_WEIGHT_FIELD_PROBE_R1.blend`，SHA256 `d7d895b5018c80e7b2571884696ae7a5982aed8d1fb06c84f0db60a6e49d1f96`，重新打开验证通过。

出处：[RIGHT_HAND_FIRST_WEB_SKINNING_FIELD_VS_DOF_DIAGNOSIS_R1_REPORT.md](../research/audits/right_hand_first_web_skinning_field_vs_dof_diagnosis_r1/RIGHT_HAND_FIRST_WEB_SKINNING_FIELD_VS_DOF_DIAGNOSIS_R1_REPORT.md)

## 技术路线

> 继承权威：已经读取上一阶段 report、attribution、design、measurements、verification、protection及 DESIGN_ONLY candidate，candidate SHA256 `373b8516fe45d8f9f83e752eeb3607e7bfd7e3135ed8467ad22272a99ac355bb`。只读打开其对象/Action元数据；未重建 topology、未复做其实验。Human 已关闭 LEVEL_1 topology route。正式 fallback SHA256 `4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2` 保持，状态继承 PROTECTED_FROZEN_FALLBACK，blocker仍OPEN。

出处：[RIGHT_HAND_FIRST_WEB_SKINNING_FIELD_VS_DOF_DIAGNOSIS_R1_REPORT.md](../research/audits/right_hand_first_web_skinning_field_vs_dof_diagnosis_r1/RIGHT_HAND_FIRST_WEB_SKINNING_FIELD_VS_DOF_DIAGNOSIS_R1_REPORT.md)

> 输入来自原 frozen mesh + 原 axis-corrected Action，未用 topology candidate 作新权重资产起点。继续同一11.5–18.5秒/421 observations，使用六决策帧110/127/130/160/176/205及上一阶段相机。禁止路线均未开启；也没有扩大到对INDEX做扰动或优化。完整 weight vector 的读取是本轮明确要求，记录 INDEX 项是因为8条指定边上存在直接数据，不是猜测。

出处：[RIGHT_HAND_FIRST_WEB_SKINNING_FIELD_VS_DOF_DIAGNOSIS_R1_REPORT.md](../research/audits/right_hand_first_web_skinning_field_vs_dof_diagnosis_r1/RIGHT_HAND_FIRST_WEB_SKINNING_FIELD_VS_DOF_DIAGNOSIS_R1_REPORT.md)

## 测试结论

> |Q9 最终诊断|**INSUFFICIENT_EVIDENCE**|Causal isolation for the requested whole-field-versus-21-bone-DOF question fails: the allowed manipulated pair accounts for only 9–35% of the inherited endpoint-vector L1. Most of the actual gradient is held constant in directly observed INDEX influences. Asset and pair-intervention controls pass, but an unsuccessful pair-field probe cannot distinguish an untested static full-vector field problem from a DOF limit.|

出处：[RIGHT_HAND_FIRST_WEB_SKINNING_FIELD_VS_DOF_DIAGNOSIS_R1_REPORT.md](../research/audits/right_hand_first_web_skinning_field_vs_dof_diagnosis_r1/RIGHT_HAND_FIRST_WEB_SKINNING_FIELD_VS_DOF_DIAGNOSIS_R1_REPORT.md)

> 继承权威：已经读取上一阶段 report、attribution、design、measurements、verification、protection及 DESIGN_ONLY candidate，candidate SHA256 `373b8516fe45d8f9f83e752eeb3607e7bfd7e3135ed8467ad22272a99ac355bb`。只读打开其对象/Action元数据；未重建 topology、未复做其实验。Human 已关闭 LEVEL_1 topology route。正式 fallback SHA256 `4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2` 保持，状态继承 PROTECTED_FROZEN_FALLBACK，blocker仍OPEN。

出处：[RIGHT_HAND_FIRST_WEB_SKINNING_FIELD_VS_DOF_DIAGNOSIS_R1_REPORT.md](../research/audits/right_hand_first_web_skinning_field_vs_dof_diagnosis_r1/RIGHT_HAND_FIRST_WEB_SKINNING_FIELD_VS_DOF_DIAGNOSIS_R1_REPORT.md)

## 失败原因与证据边界

> 本次出现的是**因果隔离控制失效**，而不是资产污染或执行缺失：只允许改变的 WRIST/THUMB 两项实际仅覆盖继承最坏8边完整权重向量 L1 差的9.45%–35.18%。直接读取的 INDEX MCP/PIP/DIP 项贡献更大，且按本轮要求逐点固定保留。失败的两项 probe 不能排除这些未改变的静态场仍不合理，因此不能推出整个21-bone deformation basis不足。此处使用 INSUFFICIENT_EVIDENCE 的原因是 A/B 所需隔离对照没有成立；并非因为还想多做候选或不愿作选择。

出处：[RIGHT_HAND_FIRST_WEB_SKINNING_FIELD_VS_DOF_DIAGNOSIS_R1_REPORT.md](../research/audits/right_hand_first_web_skinning_field_vs_dof_diagnosis_r1/RIGHT_HAND_FIRST_WEB_SKINNING_FIELD_VS_DOF_DIAGNOSIS_R1_REPORT.md)

## 后续建议

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 原报告与关键代码

- [audits/right_hand_first_web_skinning_field_vs_dof_diagnosis_r1/RIGHT_HAND_FIRST_WEB_SKINNING_FIELD_VS_DOF_DIAGNOSIS_R1_REPORT.md](../research/audits/right_hand_first_web_skinning_field_vs_dof_diagnosis_r1/RIGHT_HAND_FIRST_WEB_SKINNING_FIELD_VS_DOF_DIAGNOSIS_R1_REPORT.md)
- [audits/right_hand_first_web_skinning_field_vs_dof_diagnosis_r1/01_sensitivity.py](../../src/legacy/audits/right_hand_first_web_skinning_field_vs_dof_diagnosis_r1/01_sensitivity.py)
- [audits/right_hand_first_web_skinning_field_vs_dof_diagnosis_r1/02_weight_field_probe.py](../../src/legacy/audits/right_hand_first_web_skinning_field_vs_dof_diagnosis_r1/02_weight_field_probe.py)
- [audits/right_hand_first_web_skinning_field_vs_dof_diagnosis_r1/03_evidence.py](../../src/legacy/audits/right_hand_first_web_skinning_field_vs_dof_diagnosis_r1/03_evidence.py)
- [audits/right_hand_first_web_skinning_field_vs_dof_diagnosis_r1/04_deliver.py](../../src/legacy/audits/right_hand_first_web_skinning_field_vs_dof_diagnosis_r1/04_deliver.py)
- [audits/right_hand_first_web_skinning_field_vs_dof_diagnosis_r1/05_finalize.py](../../src/legacy/audits/right_hand_first_web_skinning_field_vs_dof_diagnosis_r1/05_finalize.py)
- [audits/right_hand_first_web_skinning_field_vs_dof_diagnosis_r1/common.py](../../src/legacy/audits/right_hand_first_web_skinning_field_vs_dof_diagnosis_r1/common.py)

## 输入、输出与大型证据

该目录原始成员 75 项；拟公开身份记录 61 项。
- `audits/right_hand_first_web_skinning_field_vs_dof_diagnosis_r1/RIGHT_HAND_FIRST_WEB_WEIGHT_FIELD_PROBE_R1.blend` → `hands-research-r1-selected-008.zip` / `payload/audits/right_hand_first_web_skinning_field_vs_dof_diagnosis_r1/RIGHT_HAND_FIRST_WEB_WEIGHT_FIELD_PROBE_R1.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
