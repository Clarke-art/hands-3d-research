# audits/real_piano_reference_gap_closure_and_static_posture_probe_r2

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 实际打开 PiaDOOR、Pianote、Hoffman Lesson 14/236；实际查看两张八度照片。PiaDOOR 是 Für Elise 左手 A–E–A 准备，有额外中间指任务；Pianote 新图是右手 C 八度，不能替代左手。Hoffman 官方文字确认五指 D/E/F#/G/A，Lesson 236 确认原版 A 段而非早期简化版。

出处：[REAL_PIANO_REFERENCE_GAP_CLOSURE_AND_STATIC_POSTURE_PROBE_R2_REPORT.md](../research/audits/real_piano_reference_gap_closure_and_static_posture_probe_r2/REAL_PIANO_REFERENCE_GAP_CLOSURE_AND_STATIC_POSTURE_PROBE_R2_REPORT.md)

> |前部内侧区域最小点距|144.480 mm|零面积边缘下界，不是实际安全 pad 目标|

出处：[REAL_PIANO_REFERENCE_GAP_CLOSURE_AND_STATIC_POSTURE_PROBE_R2_REPORT.md](../research/audits/real_piano_reference_gap_closure_and_static_posture_probe_r2/REAL_PIANO_REFERENCE_GAP_CLOSURE_AND_STATIC_POSTURE_PROBE_R2_REPORT.md)

## 技术路线

> 详见 `参考清单`（链接见原报告）、`八类合同`（链接见原报告）。本合同 YES 代表依据分类与检验要求明确，不代表科学姿态完整、数值求解政策已校准或模型通过。

出处：[REAL_PIANO_REFERENCE_GAP_CLOSURE_AND_STATIC_POSTURE_PROBE_R2_REPORT.md](../research/audits/real_piano_reference_gap_closure_and_static_posture_probe_r2/REAL_PIANO_REFERENCE_GAP_CLOSURE_AND_STATIC_POSTURE_PROBE_R2_REPORT.md)

> |Q4|执行唯一静态候选？|**NO**|关键黑键五指可见关系尚未取得，不启动求解。|

出处：[REAL_PIANO_REFERENCE_GAP_CLOSURE_AND_STATIC_POSTURE_PROBE_R2_REPORT.md](../research/audits/real_piano_reference_gap_closure_and_static_posture_probe_r2/REAL_PIANO_REFERENCE_GAP_CLOSURE_AND_STATIC_POSTURE_PROBE_R2_REPORT.md)

## 测试结论

> **FINAL_STATUS = REFERENCE_EVIDENCE_INSUFFICIENT**。补充了对侧八度静态参考、原版 Musette 身份与真实播放器访问结果，建立八类有证据边界的姿态合同；未执行静态候选。自然几何可行性仍 UNKNOWN，不能将 NOT_RUN 写成 PASS。

出处：[REAL_PIANO_REFERENCE_GAP_CLOSURE_AND_STATIC_POSTURE_PROBE_R2_REPORT.md](../research/audits/real_piano_reference_gap_closure_and_static_posture_probe_r2/REAL_PIANO_REFERENCE_GAP_CLOSURE_AND_STATIC_POSTURE_PROBE_R2_REPORT.md)

> L1/L2/R1/R2 全为 NOT_RUN，候选数 0，动作数 0。root 差异、实际候选 pad 跨度、主动指接触、闲置指、掌腕净空、邻键干扰、关节状态均无新测量。没有把旧失败动态帧重新命名为 R2 静态候选。

出处：[REAL_PIANO_REFERENCE_GAP_CLOSURE_AND_STATIC_POSTURE_PROBE_R2_REPORT.md](../research/audits/real_piano_reference_gap_closure_and_static_posture_probe_r2/REAL_PIANO_REFERENCE_GAP_CLOSURE_AND_STATIC_POSTURE_PROBE_R2_REPORT.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

> 条件式实验未启动，因此 **STATIC_POSTURE_PROBE_R2.blend、STATIC_POSTURE_RESULTS_R2.json、三张 EVIDENCE_*_R2.png 不生成**。这是门槛未满足的明确结果，非遗失文件。已交付报告、review.html、参考清单、合同、可行性 JSON、下一轮要求、最终保护 JSON，另附只读重新测量与访问/交付验证记录。

出处：[REAL_PIANO_REFERENCE_GAP_CLOSURE_AND_STATIC_POSTURE_PROBE_R2_REPORT.md](../research/audits/real_piano_reference_gap_closure_and_static_posture_probe_r2/REAL_PIANO_REFERENCE_GAP_CLOSURE_AND_STATIC_POSTURE_PROBE_R2_REPORT.md)

> |Q12|可进入下一轮动态规划器设计？|**NO**|静态与 Human 门槛均未通过。|

出处：[REAL_PIANO_REFERENCE_GAP_CLOSURE_AND_STATIC_POSTURE_PROBE_R2_REPORT.md](../research/audits/real_piano_reference_gap_closure_and_static_posture_probe_r2/REAL_PIANO_REFERENCE_GAP_CLOSURE_AND_STATIC_POSTURE_PROBE_R2_REPORT.md)

## 原报告与关键代码

- [audits/real_piano_reference_gap_closure_and_static_posture_probe_r2/REAL_PIANO_REFERENCE_GAP_CLOSURE_AND_STATIC_POSTURE_PROBE_R2_REPORT.md](../research/audits/real_piano_reference_gap_closure_and_static_posture_probe_r2/REAL_PIANO_REFERENCE_GAP_CLOSURE_AND_STATIC_POSTURE_PROBE_R2_REPORT.md)
- [audits/real_piano_reference_gap_closure_and_static_posture_probe_r2/REAL_PIANO_REFERENCE_MANIFEST_R2.md](../research/audits/real_piano_reference_gap_closure_and_static_posture_probe_r2/REAL_PIANO_REFERENCE_MANIFEST_R2.md)
- [audits/real_piano_reference_gap_closure_and_static_posture_probe_r2/NEXT_MOTION_PLANNER_REQUIREMENTS_R2.md](../research/audits/real_piano_reference_gap_closure_and_static_posture_probe_r2/NEXT_MOTION_PLANNER_REQUIREMENTS_R2.md)
- [audits/real_piano_reference_gap_closure_and_static_posture_probe_r2/NATURAL_PIANO_HAND_POSTURE_CONTRACT_R2.md](../research/audits/real_piano_reference_gap_closure_and_static_posture_probe_r2/NATURAL_PIANO_HAND_POSTURE_CONTRACT_R2.md)
- [audits/real_piano_reference_gap_closure_and_static_posture_probe_r2/04_fresh_geometry_and_protection.py](../../src/legacy/audits/real_piano_reference_gap_closure_and_static_posture_probe_r2/04_fresh_geometry_and_protection.py)
- [audits/real_piano_reference_gap_closure_and_static_posture_probe_r2/05_delivery.py](../../src/legacy/audits/real_piano_reference_gap_closure_and_static_posture_probe_r2/05_delivery.py)
- [audits/real_piano_reference_gap_closure_and_static_posture_probe_r2/07_verify.py](../../src/legacy/audits/real_piano_reference_gap_closure_and_static_posture_probe_r2/07_verify.py)

## 输入、输出与大型证据

该目录原始成员 36 项；拟公开身份记录 31 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
