# FINGERING_AND_EVENT_SCOPE · 前4小节真实右手

复用原文件 `../minuet_in_g_longer_phrase_validation_r1/source/anna-magdalena-04.mid`，SHA256 `fd87a6673e18104047842a1c858d2c9d8eb9ad845d7a8fa46e3664b17642cb75`。来源沿用已核实Mutopia BWV Anh.114；不下载、不替换、不重写。Staff one / MIDI track 1 `one:` 对应右手；不按音高分手。

3/4，PPQ384，tempo428571μs/四分音符，约140bpm。半开tick范围[0,4608)，源时长5.142852秒。16音符、16NOTE_ON、16NOTE_OFF，8种音高G4–G5，含F♯5黑键。NOTE_ON/OFF相邻无间隙、无裁音、无左手声音或动作。呈现只添加0.3秒前导与尾余量，60fps视频5.7秒。

原LilyPond `voiceone` 没有可靠指法数字；源码中的8、4是时值，mordent是装饰记号，不得当作指法或凭空扩展音符。本轮严格使用原MIDI导出的音符，包括原MIDI没有展开的装饰。

指法在任何规划或运动生成前锁定为 **DESIGN_PROVISIONAL**：前两小节G五指位，E5用5、C5用3、D5用4，再E5用3/F♯5用4/G5用5为上行换位提供条件，G4用1回落。这是有音乐依据的候选输入，未获教师批准，也不是自动指法结果。渲染失败后不得修改。

|小节|实际旋律|候选指法|tick起止|
|---|---|---|---|
|1|D5四分；G4/A4/B4/C5八分|5 / 1 / 2 / 3 / 4|0–1152|
|2|D5/G4/G4四分|5 / 1 / 1|1152–2304|
|3|E5四分；C5/D5/E5/F♯5八分|5 / 3 / 4 / 3 / 4|2304–3456|
|4|G5/G4/G4四分|5 / 1 / 1|3456–4608|

完整逐事件原始ticks、原velocity、起止秒、指号和键身份见 `ORIGINAL_RIGHT_EVENTS_FIRST4.csv` 与 `PERFORMANCE_TIMELINE.json`。`INPUT_LOCK.json` 保存渲染前指法和时间表哈希。

本材料确实要求掌位变化：G4–D5初始位、第三小节向高音区迁移、第四小节G5→G4八度回落。规划结果为4段，不通过选取有利音符伪造换位。两次紧邻G4同键重奏（R06→R07、R14→R15）如实保留，暴露既有键压力仲裁缺口。

ONE NEW CANDIDATE ONLY：16音符全部进入一个右手运动数组和一个候选blend。三角度视频是同一候选；没有第二轨迹、优化重启或逐音补丁。左手不在动态场景中，不冒充演奏。Musette既有Human接受和历史工程限制保持有效。
