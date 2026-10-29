# audits/right_hand_first_web_full_static_weight_field_causal_probe_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 正 conductance 的同一 mesh-edge graph Laplacian 对每个 bone 完全一致。boundary 每分量固定 baseline 值；没有 strength、iteration 参数、目标帧拟合、优化器、painting、support pruning 或第二 candidate。固定边界使每列唯一；非负边界配合离散 maximum principle 保持非负；所有列共用算子使常数 partition-of-unity 被保持。只对内部约 10⁻⁸ 的浮点 sum 误差做 numerical normalization。

出处：[RIGHT_HAND_FIRST_WEB_FULL_STATIC_WEIGHT_FIELD_CAUSAL_PROBE_R1_REPORT.md](../research/audits/right_hand_first_web_full_static_weight_field_causal_probe_r1/RIGHT_HAND_FIRST_WEB_FULL_STATIC_WEIGHT_FIELD_CAUSAL_PROBE_R1_REPORT.md)

## 技术路线

> **STATIC_WEIGHT_ROUTE = OPEN**  

出处：[RIGHT_HAND_FIRST_WEB_FULL_STATIC_WEIGHT_FIELD_CAUSAL_PROBE_R1_REPORT.md](../research/audits/right_hand_first_web_full_static_weight_field_causal_probe_r1/RIGHT_HAND_FIRST_WEB_FULL_STATIC_WEIGHT_FIELD_CAUSAL_PROBE_R1_REPORT.md)

> 读取最近两轮 report / JSON / audit 及两个 DESIGN_ONLY candidate（只读对象与 Action 元数据，未复做其试验）。继承 LEVEL_1_TOPOLOGY_ROUTE=CLOSED 和上一轮 Human 接受的 INSUFFICIENT_EVIDENCE，不重开 retopo/subdivide/edge-flow。旧 pair probe 仅覆盖完整梯度约 9–35%，其失败不代表全向量失败。

出处：[RIGHT_HAND_FIRST_WEB_FULL_STATIC_WEIGHT_FIELD_CAUSAL_PROBE_R1_REPORT.md](../research/audits/right_hand_first_web_full_static_weight_field_causal_probe_r1/RIGHT_HAND_FIRST_WEB_FULL_STATIC_WEIGHT_FIELD_CAUSAL_PROBE_R1_REPORT.md)

## 测试结论

> |Q9 | 最终结论？ | STATIC_WEIGHT_FIELD_PROBLEM_SUPPORTED | 现有 deformation basis 在固定 sample 与六决策帧上具备解决主 blocker 的能力；等待 Human review，不 promotion。|

出处：[RIGHT_HAND_FIRST_WEB_FULL_STATIC_WEIGHT_FIELD_CAUSAL_PROBE_R1_REPORT.md](../research/audits/right_hand_first_web_full_static_weight_field_causal_probe_r1/RIGHT_HAND_FIRST_WEB_FULL_STATIC_WEIGHT_FIELD_CAUSAL_PROBE_R1_REPORT.md)

> F130 对应 ROI 点最大位移 24.515 mm，候选局部 max edge-length ratio=1.765；仅作干预确实影响曲面的佐证，不作为 PASS 条件。六帧完整数值位于 PROBE_MEASUREMENTS_R1.json。421 observations 检查包含最后端点 F211：`i=0..420 → source 690+i → frame 1+i//2, subframe=(i%2)/2`。没有改 sample 或 retarget。

出处：[RIGHT_HAND_FIRST_WEB_FULL_STATIC_WEIGHT_FIELD_CAUSAL_PROBE_R1_REPORT.md](../research/audits/right_hand_first_web_full_static_weight_field_causal_probe_r1/RIGHT_HAND_FIRST_WEB_FULL_STATIC_WEIGHT_FIELD_CAUSAL_PROBE_R1_REPORT.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

> **STATIC_WEIGHT_ROUTE = OPEN**。本轮证明 existing static field 具有解决当前六帧主 blocker 的能力；production-quality weight solution 的设计需下一轮 Human 决策。`DEFORMATION_DOF_LIMIT_SUPPORTED` 本轮不成立，不自动进入新 bone / helper / cage / PSD / RBF / muscle / new rig。

出处：[RIGHT_HAND_FIRST_WEB_FULL_STATIC_WEIGHT_FIELD_CAUSAL_PROBE_R1_REPORT.md](../research/audits/right_hand_first_web_full_static_weight_field_causal_probe_r1/RIGHT_HAND_FIRST_WEB_FULL_STATIC_WEIGHT_FIELD_CAUSAL_PROBE_R1_REPORT.md)

## 原报告与关键代码

- [audits/right_hand_first_web_full_static_weight_field_causal_probe_r1/RIGHT_HAND_FIRST_WEB_FULL_STATIC_WEIGHT_FIELD_CAUSAL_PROBE_R1_REPORT.md](../research/audits/right_hand_first_web_full_static_weight_field_causal_probe_r1/RIGHT_HAND_FIRST_WEB_FULL_STATIC_WEIGHT_FIELD_CAUSAL_PROBE_R1_REPORT.md)
- [audits/right_hand_first_web_full_static_weight_field_causal_probe_r1/01_build_full_vector.py](../../src/legacy/audits/right_hand_first_web_full_static_weight_field_causal_probe_r1/01_build_full_vector.py)
- [audits/right_hand_first_web_full_static_weight_field_causal_probe_r1/02_verify_and_render.py](../../src/legacy/audits/right_hand_first_web_full_static_weight_field_causal_probe_r1/02_verify_and_render.py)
- [audits/right_hand_first_web_full_static_weight_field_causal_probe_r1/03_evidence.py](../../src/legacy/audits/right_hand_first_web_full_static_weight_field_causal_probe_r1/03_evidence.py)
- [audits/right_hand_first_web_full_static_weight_field_causal_probe_r1/04_verify_protection.py](../../src/legacy/audits/right_hand_first_web_full_static_weight_field_causal_probe_r1/04_verify_protection.py)
- [audits/right_hand_first_web_full_static_weight_field_causal_probe_r1/05_deliver.py](../../src/legacy/audits/right_hand_first_web_full_static_weight_field_causal_probe_r1/05_deliver.py)
- [audits/right_hand_first_web_full_static_weight_field_causal_probe_r1/common.py](../../src/legacy/audits/right_hand_first_web_full_static_weight_field_causal_probe_r1/common.py)

## 输入、输出与大型证据

该目录原始成员 48 项；拟公开身份记录 45 项。
- `audits/right_hand_first_web_full_static_weight_field_causal_probe_r1/EVIDENCE_F130_FULL_WEIGHT_FIELD_PROBE.png` → `hands-research-r1-selected-007.zip` / `payload/audits/right_hand_first_web_full_static_weight_field_causal_probe_r1/EVIDENCE_F130_FULL_WEIGHT_FIELD_PROBE.png`
- `audits/right_hand_first_web_full_static_weight_field_causal_probe_r1/EVIDENCE_FULL_VECTOR_GRADIENT_R1.png` → `hands-research-r1-selected-007.zip` / `payload/audits/right_hand_first_web_full_static_weight_field_causal_probe_r1/EVIDENCE_FULL_VECTOR_GRADIENT_R1.png`
- `audits/right_hand_first_web_full_static_weight_field_causal_probe_r1/RIGHT_HAND_FIRST_WEB_FULL_STATIC_WEIGHT_PROBE_R1.blend` → `hands-research-r1-selected-007.zip` / `payload/audits/right_hand_first_web_full_static_weight_field_causal_probe_r1/RIGHT_HAND_FIRST_WEB_FULL_STATIC_WEIGHT_PROBE_R1.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
