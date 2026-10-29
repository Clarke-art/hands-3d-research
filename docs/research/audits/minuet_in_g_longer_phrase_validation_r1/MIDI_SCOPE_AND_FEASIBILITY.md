# MIDI_SCOPE_AND_FEASIBILITY

2026-10-09 · HUMAN_VISIBLE_PRODUCT_QUALITY_FIRST · 只读可执行性核查 · FAIL_CLOSED

本轮未生成动作、候选或视频。原因是当前合格运动入口缺少目标键/手位相关的姿态组织与左手三指同时接触机制，不能仅替换输入MIDI就真实演奏本段。没有依据断言冻结Rig本身物理不可行。

## 原始版本与来源

工程内初始没有BWV Anh.114文件；已按Human明确回复采用同一Mutopia上游键盘原版。采用[Mutopia作品75](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=75)，版本 `Mutopia-2017/01/19-75`、LilyPond2.19.49、维护AllenGarvin、Source标注Bach-Gesellschaft、Public Domain。排除吉他、小号和弦乐改编版。

原MIDI：[anna-magdalena-04.mid](../../../../examples/historical/audits/minuet_in_g_longer_phrase_validation_r1/source/anna-magdalena-04.mid)，下载URL `https://www.mutopiaproject.org/ftp/BachJS/BWVAnh114/anna-magdalena-04/anna-magdalena-04.mid`；SHA256 `fd87a6673e18104047842a1c858d2c9d8eb9ad845d7a8fa46e3664b17642cb75`。原[乐谱源码](../../../artifacts/0d529542b179092e7f85.md)、来源页HTML及响应URL/字节哈希一并保存。原文件只下载和读取，未改谱、改速、删音或替换velocity。

## 前16小节实际范围

|项|实测值|
|---|---|
|格式/PPQ|SMF1 /384|
|拍号|3/4，无弱起|
|速度|源码四分音符140；原MIDI428571μs/四分音符，编码实际约140.00014BPM|
|每小节|1152 ticks|
|NOTE_ON范围|[0,18432)，第1–16小节|
|尾端NOTE_OFF|18432，完整保留，无音符裁断|
|音乐时钟|0–20.571408秒，按原tempo积分|
|NOTE_ON/NOTE_OFF|102/102，204事件|
|右手/左手|65/37音符|
|MIDI velocity|全部90，保留原值|
|全源文件|32小节，36864ticks，约41.142816秒|

LilyPond第一段含16小节volta2重复记号，原MIDI没有展开重复，线性编码第一、第二16小节各一次。本轮明确选第一段一次，不自行补重复；原前16小节含谱内旋律再现，构成第一重复段完整收束。下一小节在tick18432开始，不纳入本段。

右手65音符含原MIDI保留的B4倚音：43ticks约47.991ms，最近两次起音间隔44ticks约49.107ms。它在MIDI中提前进入第7小节末的tick窗口，但对应源码第8小节倚音；保留原时间，不按文字位置重排。普通八分音符间隔192ticks约214.286ms；mordent/prall等谱面装饰不手工扩展为新事件。

## 声部、和弦与位移需求

左右手由源码Staff one/voiceone与Staff two/voicetwo映射到MIDITrack1 `one:` /Track2 `two:`；不是按高低音随意拆手。

- 右手：单音旋律，F♯4–G5（13半音跨度），9不同音高，包含倚音与连续八分交替。MIDI最大同时持音1。
- 左手：G2–D4（19半音跨度），8不同音高。第1小节tick0的G3/B3/D4三音和弦同时按下，三音均持到tick768（0.857142秒），然后A3。其余为单音长持/低音流动，13个音符时值至少二拍。
- 左手峰值3，双手峰值4。同手除首和弦外，没有不同起音之间的实际MIDI持音重叠；琴键回弹/手指释放动作的重叠另属运动规划问题。
- 音区与现有Musette固定手位不同，必须组织覆盖不同键/手位的动作；具体腕路尚未求解，未虚构毫米轨迹。

全部逐音符证据见[CSV](../../../../examples/historical/audits/minuet_in_g_longer_phrase_validation_r1/ORIGINAL_EVENTS_FIRST16.csv)与[MIDI_SCOPE_STATISTICS.json](../../../../examples/historical/audits/minuet_in_g_longer_phrase_validation_r1/MIDI_SCOPE_STATISTICS.json)。

## Q1–Q3可执行性判断

**Q1：当前合格入口不能合理直接支持这一完整结构。** 它具有FK/skin/键面评价和Action烘焙等可复用基础，但当前右手每指只有一对固定接触/下压端点；NOTE_ON时同digit使用同一接触姿态，整个相邻乐句的root stance保持同幅值。9个不同键无法由5个固定接触点和固定手位合法覆盖。左手仍是D2/D3两类压力曲线与固定键17/29驱动的29参数动作，缺少G3/B3/D4三主动指任务入口。

**Q2：CHORD_OR_MULTI_FINGER_SUPPORT=NOT_ESTABLISHED。** MIDI、88键、混音接口可表示多音，多个digit阶段数组有部分表示基础；这不证明三指实际接触。未渲染和弦，不能声称“和弦肉眼失败”，也不能把键与声支持写成真实演奏通过。

**Q3：不只是换事件列表。** 需要建立按目标键/手位条件变化的指姿态、左手联合和弦接触与较长双手位置/指法组织机制。旧独立逐指/逐时刻IK原型虽然有任意目标接口，但root仍固定，依赖外部home与fingering配置，未提供合格的长段换位/联合三指规划。以它取代现有合格入口并补齐这些核心能力，超出本轮有限复用适配判断；不把未验证核心当作已存在功能。

源码证据与具体行号见[FEASIBILITY_DECISION.json](../../../../examples/historical/audits/minuet_in_g_longer_phrase_validation_r1/FEASIBILITY_DECISION.json)。该结论是软件入口与本轮范围判断，不是仅凭“没试过”宣称数学不可行，也不是否定Human已接受的Musette产品观感。

## 止损决定

在动作生成前FAIL_CLOSED，候选0、求解0、Action0、视频0。未简化首三音和弦，未删除倚音，未手动逐音符动画，未修改冻结资产。按本轮“当前系统无法合理支持核心结构则停止”的规则，不为强行产出视频新增一套尚未建立的核心规划。
