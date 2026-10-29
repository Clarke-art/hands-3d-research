# audits/piano_hand_motion_technology_research_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 1. **三个项目哪个最值得继续验证？** Tipiano的可控接口目标最符合本项目，应关注其正式发布；立即可观察的动作先验以FürElise捕获数据更有针对性。但FürElise公开数据是NC，产品实验优先取得教师自有或另行授权的短段。PianoMotion10M适合作为可运行代码研究对象，优先级低于以上两者。`Tipiano官方发布状态`（链接见原报告）、`FürElise数据卡`（链接见原报告）

出处：[FINAL_RECOMMENDATION.md](../research/audits/piano_hand_motion_technology_research_r1/FINAL_RECOMMENDATION.md)

> 4. **能保留现有Rig与冻结资产吗？** 可以。将外部动作作为目标/先验转换到现有骨长、轴、工程域，保留网格/权重/琴键与静态批准姿态。未来派生动作的短段root/腕变化与修改冻结资产不同；转换后仍必须检查真实skin和键体，不能直接拷MANO角度。详见BLENDER_INTEGRATION_FEASIBILITY.md。

出处：[FINAL_RECOMMENDATION.md](../research/audits/piano_hand_motion_technology_research_r1/FINAL_RECOMMENDATION.md)

## 技术路线

> **算法方向优先Tipiano；眼下最小验证优先“教师核准的短段真实动作先验＋掌腕/指尖联合重定向”。当前没有查到一个可直接接入、可控指定指法并已清楚允许商业教材用途的完整开源模型。**

出处：[FINAL_RECOMMENDATION.md](../research/audits/piano_hand_motion_technology_research_r1/FINAL_RECOMMENDATION.md)

> 2. **有可直接复用的开源模型吗？** PianoMotion10M确实有源码和公开ckpt，不是空壳；但当前推理依赖测试集/CUDA/音频编码器/MANO，缺指定指法硬约束，权重许可不明确，运行也未验证。Tipiano和FürElise未核实完整公开生成实现。因此本项目意义下答案为“没有已验证的即插即用模型”。`PianoMotion源码`（链接见原报告）、`权重树`（链接见原报告）

出处：[FINAL_RECOMMENDATION.md](../research/audits/piano_hand_motion_technology_research_r1/FINAL_RECOMMENDATION.md)

## 测试结论

> 1. **三个项目哪个最值得继续验证？** Tipiano的可控接口目标最符合本项目，应关注其正式发布；立即可观察的动作先验以FürElise捕获数据更有针对性。但FürElise公开数据是NC，产品实验优先取得教师自有或另行授权的短段。PianoMotion10M适合作为可运行代码研究对象，优先级低于以上两者。`Tipiano官方发布状态`（链接见原报告）、`FürElise数据卡`（链接见原报告）

出处：[FINAL_RECOMMENDATION.md](../research/audits/piano_hand_motion_technology_research_r1/FINAL_RECOMMENDATION.md)

> 已验证：官网发布状态、固定源码/配置、四个权重对象的元数据、NC/MANO条款、当前Rig接口、GPU信息，以及报告中列明的实际官方画面。少量预览的两行JSON结构已读取；没有下载权重或47GB数据包。

出处：[FINAL_RECOMMENDATION.md](../research/audits/piano_hand_motion_technology_research_r1/FINAL_RECOMMENDATION.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

> 3. **需要真实演奏先验吗？** 强烈建议至少一段教师核准的3↔4交接参考，用于腕/掌布局、闲置指和释放耦合。并非理论上绝对必需，也不需要直接下载整个数据集；它能让最小实验检验真实路径而非继续猜角度。不能仅从MIDI确定唯一正确手腕轨迹。`FürElise数据预览`（链接见原报告）

出处：[FINAL_RECOMMENDATION.md](../research/audits/piano_hand_motion_technology_research_r1/FINAL_RECOMMENDATION.md)

> 5. **下一阶段最小实验是什么？** 教师先确认C5(3)→D5(4)→E5(3)→F♯5(4)→G5(5)，再取得一个带腕/关节/逐指事件且权利清楚的短样本。仅在约3.25–4.75s范围做一次整手协同重定向试验，保留事件与音乐，原俯视相机验收。对照必须分开看原生先验质量和目标Rig重定向损失。此为建议，未执行。

出处：[FINAL_RECOMMENDATION.md](../research/audits/piano_hand_motion_technology_research_r1/FINAL_RECOMMENDATION.md)

## 原报告与关键代码

- [audits/piano_hand_motion_technology_research_r1/FINAL_RECOMMENDATION.md](../research/audits/piano_hand_motion_technology_research_r1/FINAL_RECOMMENDATION.md)
- [audits/piano_hand_motion_technology_research_r1/BLENDER_INTEGRATION_FEASIBILITY.md](../research/audits/piano_hand_motion_technology_research_r1/BLENDER_INTEGRATION_FEASIBILITY.md)
- [audits/piano_hand_motion_technology_research_r1/EVIDENCE_INDEX.md](../research/audits/piano_hand_motion_technology_research_r1/EVIDENCE_INDEX.md)
- [audits/piano_hand_motion_technology_research_r1/DEMO_VISUAL_REVIEW.md](../research/audits/piano_hand_motion_technology_research_r1/DEMO_VISUAL_REVIEW.md)
- [audits/piano_hand_motion_technology_research_r1/B02_TECHNICAL_OPTIONS.md](../research/audits/piano_hand_motion_technology_research_r1/B02_TECHNICAL_OPTIONS.md)
- [audits/piano_hand_motion_technology_research_r1/TECHNOLOGY_COMPARISON.md](../research/audits/piano_hand_motion_technology_research_r1/TECHNOLOGY_COMPARISON.md)
- [audits/piano_hand_motion_technology_research_r1/check_small_sample.py](../../src/legacy/audits/piano_hand_motion_technology_research_r1/check_small_sample.py)
- [audits/piano_hand_motion_technology_research_r1/collect_followup_evidence.py](../../src/legacy/audits/piano_hand_motion_technology_research_r1/collect_followup_evidence.py)
- [audits/piano_hand_motion_technology_research_r1/collect_static_evidence.py](../../src/legacy/audits/piano_hand_motion_technology_research_r1/collect_static_evidence.py)
- [audits/piano_hand_motion_technology_research_r1/write_reports.py](../../src/legacy/audits/piano_hand_motion_technology_research_r1/write_reports.py)

## 输入、输出与大型证据

该目录原始成员 55 项；拟公开身份记录 16 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
