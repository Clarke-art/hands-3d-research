# 23 音符教学审核表

所有时间为秒。源 ON/OFF 是实际 MIDI 时间；视频 ON/OFF 已加 0.35s。键编号采用原项目 0-based（MIDI−21），不是钢琴常见 1–88 编号。音符 ID 沿用源事件。

|音符/手指|目标键（MIDI/index）|类型|源 ON → OFF|视频 ON → OFF|触键|持键释放|空间自然性|教学结论|证据/问题|
|---|---|---|---|---|---|---|---|---|---|
|R00 R D5 / 5指|D5 (74/53)|连续单音|0.000000 → 0.428571|0.350000 → 0.778571|PASS|PASS|WARN|WARN|[逐音定位](../../../artifacts/cae600aa68556f497aa6.md) · [画面](../../../artifacts/d353fbe2b5faa630cd5f.md) · W01|
|L00 L G3 / 5指|G3 (55/34)|和弦 G3+B3+D4|0.000000 → 0.857142|0.350000 → 1.207142|PASS|PASS|PASS|PASS|[逐音定位](../../../artifacts/cae600aa68556f497aa6.md) · [画面](../../../artifacts/d353fbe2b5faa630cd5f.md) · 无本音已证实阻断|
|L01 L B3 / 3指|B3 (59/38)|和弦 G3+B3+D4|0.000000 → 0.857142|0.350000 → 1.207142|PASS|PASS|PASS|PASS|[逐音定位](../../../artifacts/cae600aa68556f497aa6.md) · [画面](../../../artifacts/d353fbe2b5faa630cd5f.md) · 无本音已证实阻断|
|L02 L D4 / 1指|D4 (62/41)|和弦 G3+B3+D4|0.000000 → 0.857142|0.350000 → 1.207142|PASS|PASS|PASS|PASS|[逐音定位](../../../artifacts/cae600aa68556f497aa6.md) · [画面](../../../artifacts/d353fbe2b5faa630cd5f.md) · 无本音已证实阻断|
|R01 R G4 / 1指|G4 (67/46)|连续单音|0.428571 → 0.642856|0.778571 → 0.992856|PASS|PASS|UNKNOWN|UNKNOWN|[逐音定位](../../../artifacts/cae600aa68556f497aa6.md) · [画面](../../../artifacts/f0aae963f2cd0149ec94.md) · 无本音已证实阻断|
|R02 R A4 / 2指|A4 (69/48)|连续单音|0.642856 → 0.857142|0.992856 → 1.207142|PASS|PASS|BLOCKING|BLOCKING|[逐音定位](../../../artifacts/cae600aa68556f497aa6.md) · [画面](../../../artifacts/f0aae963f2cd0149ec94.md) · B01|
|R03 R B4 / 3指|B4 (71/50)|连续单音|0.857142 → 1.071427|1.207142 → 1.421428|PASS|PASS|BLOCKING|BLOCKING|[逐音定位](../../../artifacts/cae600aa68556f497aa6.md) · [画面](../../../artifacts/f0aae963f2cd0149ec94.md) · B01|
|L03 L A3 / 4指|A3 (57/36)|连续单音|0.857142 → 1.285713|1.207142 → 1.635713|PASS|PASS|PASS|PASS|[逐音定位](../../../artifacts/cae600aa68556f497aa6.md) · [画面](../../../artifacts/f0aae963f2cd0149ec94.md) · 无本音已证实阻断|
|R04 R C5 / 4指|C5 (72/51)|连续单音|1.071427 → 1.285713|1.421428 → 1.635713|PASS|PASS|UNKNOWN|UNKNOWN|[逐音定位](../../../artifacts/cae600aa68556f497aa6.md) · [画面](../../../artifacts/b6c03921ea14136dbd89.md) · 无本音已证实阻断|
|R05 R D5 / 5指|D5 (74/53)|连续单音|1.285713 → 1.714284|1.635713 → 2.064284|PASS|PASS|UNKNOWN|UNKNOWN|[逐音定位](../../../artifacts/cae600aa68556f497aa6.md) · [画面](../../../artifacts/b6c03921ea14136dbd89.md) · 无本音已证实阻断|
|L04 L B3 / 3指|B3 (59/38)|连续单音|1.285713 → 2.571426|1.635713 → 2.921426|PASS|PASS|PASS|PASS|[逐音定位](../../../artifacts/cae600aa68556f497aa6.md) · [画面](../../../artifacts/b6c03921ea14136dbd89.md) · 无本音已证实阻断|
|R06 R G4 / 1指|G4 (67/46)|同指重复音|1.714284 → 2.142855|2.064284 → 2.492855|PASS|WARN|UNKNOWN|UNKNOWN|[逐音定位](../../../artifacts/cae600aa68556f497aa6.md) · [画面](../../../artifacts/b6c03921ea14136dbd89.md) · W02|
|R07 R G4 / 1指|G4 (67/46)|同指重复音|2.142855 → 2.571426|2.492855 → 2.921426|PASS|WARN|BLOCKING|BLOCKING|[逐音定位](../../../artifacts/cae600aa68556f497aa6.md) · [画面](../../../artifacts/778141f3d1828f30a179.md) · B03,W02|
|R08 R E5 / 5指|E5 (76/55)|连续单音|2.571426 → 2.999997|2.921426 → 3.349997|PASS|PASS|UNKNOWN|UNKNOWN|[逐音定位](../../../artifacts/cae600aa68556f497aa6.md) · [画面](../../../artifacts/778141f3d1828f30a179.md) · 无本音已证实阻断|
|L05 L C4 / 2指|C4 (60/39)|连续单音|2.571426 → 3.857139|2.921426 → 4.207139|PASS|PASS|PASS|PASS|[逐音定位](../../../artifacts/cae600aa68556f497aa6.md) · [画面](../../../artifacts/778141f3d1828f30a179.md) · 无本音已证实阻断|
|R09 R C5 / 3指|C5 (72/51)|连续单音|2.999997 → 3.214282|3.349997 → 3.564283|PASS|PASS|UNKNOWN|UNKNOWN|[逐音定位](../../../artifacts/cae600aa68556f497aa6.md) · [画面](../../../artifacts/778141f3d1828f30a179.md) · 无本音已证实阻断|
|R10 R D5 / 4指|D5 (74/53)|连续单音|3.214282 → 3.428568|3.564283 → 3.778568|PASS|PASS|BLOCKING|BLOCKING|[逐音定位](../../../artifacts/cae600aa68556f497aa6.md) · [画面](../../../artifacts/83c2504ff90b487146e9.md) · B02|
|R11 R E5 / 3指|E5 (76/55)|连续单音|3.428568 → 3.642854|3.778568 → 3.992854|PASS|PASS|BLOCKING|BLOCKING|[逐音定位](../../../artifacts/cae600aa68556f497aa6.md) · [画面](../../../artifacts/83c2504ff90b487146e9.md) · B02|
|R12 R F#5 / 4指|F#5 (78/57)|连续单音|3.642854 → 3.857139|3.992854 → 4.207139|PASS|PASS|BLOCKING|BLOCKING|[逐音定位](../../../artifacts/cae600aa68556f497aa6.md) · [画面](../../../artifacts/83c2504ff90b487146e9.md) · B03|
|R13 R G5 / 5指|G5 (79/58)|连续单音|3.857139 → 4.285710|4.207139 → 4.635710|PASS|PASS|UNKNOWN|UNKNOWN|[逐音定位](../../../artifacts/cae600aa68556f497aa6.md) · [画面](../../../artifacts/83c2504ff90b487146e9.md) · 无本音已证实阻断|
|L06 L B3 / 3指|B3 (59/38)|连续单音|3.857139 → 5.142852|4.207139 → 5.492852|PASS|PASS|PASS|PASS|[逐音定位](../../../artifacts/cae600aa68556f497aa6.md) · [画面](../../../artifacts/242f9c82560e5a2a2231.md) · 无本音已证实阻断|
|R14 R G4 / 1指|G4 (67/46)|同指重复音|4.285710 → 4.714281|4.635710 → 5.064281|PASS|WARN|BLOCKING|BLOCKING|[逐音定位](../../../artifacts/cae600aa68556f497aa6.md) · [画面](../../../artifacts/242f9c82560e5a2a2231.md) · B03,W02|
|R15 R G4 / 1指|G4 (67/46)|同指重复音|4.714281 → 5.142852|5.064281 → 5.492852|PASS|WARN|UNKNOWN|UNKNOWN|[逐音定位](../../../artifacts/cae600aa68556f497aa6.md) · [画面](../../../artifacts/242f9c82560e5a2a2231.md) · W02|

每音六阶段原始数值见 SKIN_KEY_SAMPLES.json，页面“阶段”按钮可查全部阶段及三视角原帧。实际 skin 标记在全部 NOTE_ON、settle、hold、NOTE_OFF 样本内横向超出目标区域为 0mm；全部这些采样未发现明显悬空。离键后横移到下一目标不按错键处理。

左手 G3/B3/D4 的 5/3/1 指同在 0.35s 触键，+40ms 三键均下沉，实际皮肤贴近键面；释放后 A3(4)、B3(3)、C4(2)、B3(3) 的目标及接触保持。左手闲置拇指/小指后段伸展是否适于初学者模仿，属于教师专业判断，不替教师认证。

F♯5（R12）由无名指落在抬高黑键面，主动触键 PASS；旁边中指/D♯5 干涉使该音整体空间结论 BLOCKING。G4 重复音四行 WARN 是回弹教学可读性，不是检测到错误 MIDI。

PASS 不等于整帧全体手指无几何接触；仅覆盖有限六阶段及已查关键交接。全段真实慢放主观自然度与未观察到的细节仍由 Human 判断。

右手未登记明确 BLOCKING/WARN 的其他八音，空间/综合结论记 UNKNOWN：当前候选有限采样仍有黑键或邻指几何命中，已有抽样画面不足以逐一确定教学可见性。不能因主动触键 PASS 而把这些音的整体空间判为 PASS。R04/R05 还覆盖早段邻指残余的尾部；未另行无限扩展检查。