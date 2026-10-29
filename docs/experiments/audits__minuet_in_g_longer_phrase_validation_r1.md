# audits/minuet_in_g_longer_phrase_validation_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 本轮完成可验证源下载、原MIDI精确解析及有限只读可执行性核查；在生成前FAIL_CLOSED。候选/动作/视频均0。没有对原Musette重新作视觉验收，承接当前Human“产品视角可接受”的新权威，并保留历史工程结果。

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_in_g_longer_phrase_validation_r1/IMPLEMENTATION_REPORT.md)

> 建立缺失的目标键/手位条件姿态、多指接触和较长根路径/指法组织属于新的核心动作能力，不能伪称已有链路只改一张曲目表就能完成。根据用户显式止损条件，在本轮产品验证范围内不引入并临时审批这些未建立机制；不做简化版本或键/声-only假演奏。

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_in_g_longer_phrase_validation_r1/IMPLEMENTATION_REPORT.md)

## 技术路线

> 复用了项目内mido读取依赖、现有声部→左右手与MIDI−21的88键身份约定、已有冻结权威/哈希保护方法。只读检查现有FK/skin、事件阶段、运动键面残差、原逐指IK、Action烘焙及PCM接口；未运行运动求解或渲染。

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_in_g_longer_phrase_validation_r1/IMPLEMENTATION_REPORT.md)

> - 音区与现有Musette固定手位不同，必须组织覆盖不同键/手位的动作；具体腕路尚未求解，未虚构毫米轨迹。

出处：[MIDI_SCOPE_AND_FEASIBILITY.md](../research/audits/minuet_in_g_longer_phrase_validation_r1/MIDI_SCOPE_AND_FEASIBILITY.md)

## 测试结论

> 本轮完成可验证源下载、原MIDI精确解析及有限只读可执行性核查；在生成前FAIL_CLOSED。候选/动作/视频均0。没有对原Musette重新作视觉验收，承接当前Human“产品视角可接受”的新权威，并保留历史工程结果。

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_in_g_longer_phrase_validation_r1/IMPLEMENTATION_REPORT.md)

> 2026-10-09 · HUMAN_VISIBLE_PRODUCT_QUALITY_FIRST · 只读可执行性核查 · FAIL_CLOSED

出处：[MIDI_SCOPE_AND_FEASIBILITY.md](../research/audits/minuet_in_g_longer_phrase_validation_r1/MIDI_SCOPE_AND_FEASIBILITY.md)

## 失败原因与证据边界

> 本轮未生成动作、候选或视频。原因是当前合格运动入口缺少目标键/手位相关的姿态组织与左手三指同时接触机制，不能仅替换输入MIDI就真实演奏本段。没有依据断言冻结Rig本身物理不可行。

出处：[MIDI_SCOPE_AND_FEASIBILITY.md](../research/audits/minuet_in_g_longer_phrase_validation_r1/MIDI_SCOPE_AND_FEASIBILITY.md)

## 后续建议

> 源音乐从第1小节就要求左手G3/B3/D4三指同时接触，后续两手8/9不同键及新手位，右手有倚音。当前合格左轨迹仍 tied toD2/D3，当前右轨迹的五指固定端点/共同stance不以当前pitch/手位改变。通用phase数组与数据层多音支持不等于联合多指触键。

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_in_g_longer_phrase_validation_r1/IMPLEMENTATION_REPORT.md)

> 既有FK/Rig可能成为后续能力建立的基础，本轮未证明冻结Rig物理不可行，也未要求改Rig。这里的NOT_ESTABLISHED针对真实新曲演奏能力，Human接受Musette不受撤销。

出处：[IMPLEMENTATION_REPORT.md](../research/audits/minuet_in_g_longer_phrase_validation_r1/IMPLEMENTATION_REPORT.md)

## 原报告与关键代码

- [audits/minuet_in_g_longer_phrase_validation_r1/IMPLEMENTATION_REPORT.md](../research/audits/minuet_in_g_longer_phrase_validation_r1/IMPLEMENTATION_REPORT.md)
- [audits/minuet_in_g_longer_phrase_validation_r1/MIDI_SCOPE_AND_FEASIBILITY.md](../research/audits/minuet_in_g_longer_phrase_validation_r1/MIDI_SCOPE_AND_FEASIBILITY.md)
- [audits/minuet_in_g_longer_phrase_validation_r1/HUMAN_VISIBLE_REVIEW.md](../research/audits/minuet_in_g_longer_phrase_validation_r1/HUMAN_VISIBLE_REVIEW.md)
- [audits/minuet_in_g_longer_phrase_validation_r1/FINGERING_AND_EVENT_PLAN.md](../research/audits/minuet_in_g_longer_phrase_validation_r1/FINGERING_AND_EVENT_PLAN.md)
- [audits/minuet_in_g_longer_phrase_validation_r1/00_source.py](../../src/legacy/audits/minuet_in_g_longer_phrase_validation_r1/00_source.py)
- [audits/minuet_in_g_longer_phrase_validation_r1/01_scope.py](../../src/legacy/audits/minuet_in_g_longer_phrase_validation_r1/01_scope.py)
- [audits/minuet_in_g_longer_phrase_validation_r1/02_preflight.py](../../src/legacy/audits/minuet_in_g_longer_phrase_validation_r1/02_preflight.py)
- [audits/minuet_in_g_longer_phrase_validation_r1/03_reports.py](../../src/legacy/audits/minuet_in_g_longer_phrase_validation_r1/03_reports.py)

## 输入、输出与大型证据

该目录原始成员 25 项；拟公开身份记录 25 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
