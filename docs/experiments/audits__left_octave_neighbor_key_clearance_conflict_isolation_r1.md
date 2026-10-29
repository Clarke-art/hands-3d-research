# audits/left_octave_neighbor_key_clearance_conflict_isolation_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 技术路线

> |Q10|NO — 未发现评价实现错误；旧>3mm筛查与本轮全部正穿入的统计范围不同。|

出处：[LEFT_OCTAVE_NEIGHBOR_KEY_CLEARANCE_CONFLICT_ISOLATION_R1_REPORT.md](../research/audits/left_octave_neighbor_key_clearance_conflict_isolation_r1/LEFT_OCTAVE_NEIGHBOR_KEY_CLEARANCE_CONFLICT_ISOLATION_R1_REPORT.md)

> NEXT_RECOMMENDED_ROUTE = ROOT_PATH_CONFLICT / HUMAN_DECISION_REQUIRED

出处：[LEFT_OCTAVE_NEIGHBOR_KEY_CLEARANCE_CONFLICT_ISOLATION_R1_REPORT.md](../research/audits/left_octave_neighbor_key_clearance_conflict_isolation_r1/LEFT_OCTAVE_NEIGHBOR_KEY_CLEARANCE_CONFLICT_ISOLATION_R1_REPORT.md)

## 测试结论

> 没有发现INDEX、THUMB或PALM进入这两个键体的已采样顶点。这里的结论仅指所检查区域与时段，不是全手解剖审计，也不是所有三角面相交的穷尽证明。

出处：[LEFT_OCTAVE_NEIGHBOR_KEY_CLEARANCE_CONFLICT_ISOLATION_R1_REPORT.md](../research/audits/left_octave_neighbor_key_clearance_conflict_isolation_r1/LEFT_OCTAVE_NEIGHBOR_KEY_CLEARANCE_CONFLICT_ISOLATION_R1_REPORT.md)

> 穿入起止为last-clear/first-hit、last-hit/first-clear采样夹逼，时间分辨率约4.167ms。两次合计E2约0.525s，F♯2约0.550s；>3mm旧门槛的每次持续估计分别0.229167s、0.237500s。详细事件逐项记录当前键状态、手部对象、区域、顶点、两种深度和当时D2/D3接触，见NEIGHBOR_KEY_PENETRATION_EVENTS_R1.json。

出处：[LEFT_OCTAVE_NEIGHBOR_KEY_CLEARANCE_CONFLICT_ISOLATION_R1_REPORT.md](../research/audits/left_octave_neighbor_key_clearance_conflict_isolation_r1/LEFT_OCTAVE_NEIGHBOR_KEY_CLEARANCE_CONFLICT_ISOLATION_R1_REPORT.md)

## 失败原因与证据边界

> 因此，root变化对于当前轨迹中的冲突有受控因果证据，选择ROOT_PATH_CONFLICT。中指/无名指当前姿态在A路径下缺少净空也是直接事实，但B保持同样姿态即可清空，不能据此宣称闲置关节独立致因或直接改判COUPLED_ROOT_FINGER_CONFLICT。未实施任何关节干预，故不能量化其独立贡献。此结论限定于该已保存动作，不能扩展成所有可选root或指法方案的唯一根因。

出处：[LEFT_OCTAVE_NEIGHBOR_KEY_CLEARANCE_CONFLICT_ISOLATION_R1_REPORT.md](../research/audits/left_octave_neighbor_key_clearance_conflict_isolation_r1/LEFT_OCTAVE_NEIGHBOR_KEY_CLEARANCE_CONFLICT_ISOLATION_R1_REPORT.md)

## 后续建议

> 仅推荐 **ROOT_PATH_CONFLICT**：如果Human后续授权，应以现有root路径造成的接触/净空权衡为研究对象。当前结果没有证明已经存在满足所有条件的解，也没有证明需要修改正式mesh/rig。本轮不实施路径或手指修复，不开第二种对照。

出处：[LEFT_OCTAVE_NEIGHBOR_KEY_CLEARANCE_CONFLICT_ISOLATION_R1_REPORT.md](../research/audits/left_octave_neighbor_key_clearance_conflict_isolation_r1/LEFT_OCTAVE_NEIGHBOR_KEY_CLEARANCE_CONFLICT_ISOLATION_R1_REPORT.md)

## 原报告与关键代码

- [audits/left_octave_neighbor_key_clearance_conflict_isolation_r1/LEFT_OCTAVE_NEIGHBOR_KEY_CLEARANCE_CONFLICT_ISOLATION_R1_REPORT.md](../research/audits/left_octave_neighbor_key_clearance_conflict_isolation_r1/LEFT_OCTAVE_NEIGHBOR_KEY_CLEARANCE_CONFLICT_ISOLATION_R1_REPORT.md)
- [audits/left_octave_neighbor_key_clearance_conflict_isolation_r1/HUMAN_VISIBLE_CONFLICT_REVIEW_R1.md](../research/audits/left_octave_neighbor_key_clearance_conflict_isolation_r1/HUMAN_VISIBLE_CONFLICT_REVIEW_R1.md)
- [audits/left_octave_neighbor_key_clearance_conflict_isolation_r1/01_counterfactual.py](../../src/legacy/audits/left_octave_neighbor_key_clearance_conflict_isolation_r1/01_counterfactual.py)
- [audits/left_octave_neighbor_key_clearance_conflict_isolation_r1/02_summarize.py](../../src/legacy/audits/left_octave_neighbor_key_clearance_conflict_isolation_r1/02_summarize.py)
- [audits/left_octave_neighbor_key_clearance_conflict_isolation_r1/03_evidence.py](../../src/legacy/audits/left_octave_neighbor_key_clearance_conflict_isolation_r1/03_evidence.py)
- [audits/left_octave_neighbor_key_clearance_conflict_isolation_r1/04_finish.py](../../src/legacy/audits/left_octave_neighbor_key_clearance_conflict_isolation_r1/04_finish.py)

## 输入、输出与大型证据

该目录原始成员 46 项；拟公开身份记录 44 项。
- `audits/left_octave_neighbor_key_clearance_conflict_isolation_r1/COUNTERFACTUAL_RAW_R1.json` → `hands-research-r1-selected-001.zip` / `payload/audits/left_octave_neighbor_key_clearance_conflict_isolation_r1/COUNTERFACTUAL_RAW_R1.json`
- `audits/left_octave_neighbor_key_clearance_conflict_isolation_r1/EVIDENCE_E2_FSHARP2_CONFLICT_R1.png` → `hands-research-r1-selected-001.zip` / `payload/audits/left_octave_neighbor_key_clearance_conflict_isolation_r1/EVIDENCE_E2_FSHARP2_CONFLICT_R1.png`
- `audits/left_octave_neighbor_key_clearance_conflict_isolation_r1/EVIDENCE_ROOT_COUNTERFACTUAL_R1.png` → `hands-research-r1-selected-001.zip` / `payload/audits/left_octave_neighbor_key_clearance_conflict_isolation_r1/EVIDENCE_ROOT_COUNTERFACTUAL_R1.png`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
