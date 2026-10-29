# LEFT_TRIAD_MIDI_AND_FINGERING · Stage B R1

本轮只隔离演示开头左手G3+B3+D4三音，不是完整小节、双手演奏或完整曲目。

原文件沿用 `../minuet_in_g_longer_phrase_validation_r1/source/anna-magdalena-04.mid`，SHA256 `fd87a6673e18104047842a1c858d2c9d8eb9ad845d7a8fa46e3664b17642cb75`。来源沿用已核实Mutopia BWV Anh.114，不重新下载、不替换、不写MIDI。

|原声部|原MIDI|音名|指法|键index|NOTE_ON tick|NOTE_OFF tick|原channel/velocity|
|---|---:|---|---:|---:|---:|---:|---|
|track2 `two:`|55|G3|左小指5|34|0|768|1 / 90|
|track2 `two:`|59|B3|左中指3|38|0|768|1 / 90|
|track2 `two:`|62|D4|左拇指1|41|0|768|1 / 90|

三音完全同时起音及释放。PPQ384，3/4，tempo428571μs/四分音符，约140bpm；tick768对应二分音符（两拍）持键，准确时长 **0.857142秒**。原源时间三音均为0.000000→0.857142秒。

持键区间[0,768)没有其他左手音。原右手有D5（tick0–384）、G4（384–576）、A4（576–768）重叠，本隔离演示不生成/播放它们；原文件不删除任何事件。左手后继A3不进入该隔离演示。

原LilyPond `voicetwo` 以嵌套声部写出 `<b d>2` 与 `g2`，没有可靠指法数字；2是时值，不是指法。采用 **DESIGN_PROVISIONAL 5–3–1**，未获教师正式认证，在所有静态及动态结果前锁定，不失败后换指。

视频统一添加0.35秒准备前导：三音在呈现0.350000s起音、1.207142s NOTE_OFF；音乐关系和tempo不变。尾部只保留释放/回位，不加重奏或其他音。100帧/60fps呈现约1.666667秒。

精确事件与哈希见 `SOURCE_TRIAD_EVENT_VERIFICATION.json`、`ORIGINAL_LEFT_TRIAD_EVENTS.csv`、`INPUT_LOCK.json`。左右手归属按源staff/track识别，不按音高临时分割。
