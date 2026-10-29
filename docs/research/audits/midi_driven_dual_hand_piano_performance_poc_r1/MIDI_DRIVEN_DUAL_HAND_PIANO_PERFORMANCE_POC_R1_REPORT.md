# MIDI_DRIVEN_DUAL_HAND_PIANO_PERFORMANCE_POC_R1

**MIDI_DRIVEN_PIANO_PERFORMANCE_POC_PARTIAL**。**PRODUCT_DEMO_PASS = NO**。**STOP — HUMAN REVIEW**。

首次打通了官方 MIDI → 明确声部/候选指法 → 新程序化 Action → 琴键 → 真实钢琴采样音轨，但动作与接触质量未通过。PARTIAL 只表示执行链路和带声音交付成立，不表示产品演奏动作合格。没有继续调旧 PianoVAM root，也没有加载其非商业 Action。

## Q1–Q13

|问题|回答|
|---|---|
|Q1 官方 MIDI 已取得并与乐谱核对？|YES；PDF 目视 + LilyPond/MIDI 前两小节音高与 tick 逐项一致。|
|Q2 选择小节？|第 1–2 小节，首次出现，完整保留两声部；音乐 2.0 秒，展示含准备与释放共 3.4 秒。|
|Q3 左右手分配明确？|YES；Staff one/track1 → RIGHT，Staff two/track2 → LEFT，经谱面核对。|
|Q4 候选指法及权威程度明确？|YES；DESIGNED_PROVISIONAL，不是官方指法或 ground truth。|
|Q5 双手能按正确目标键演奏？|NO；虽目标音区与横向位置匹配，持续触键失败。|
|Q6 整体手掌与手腕自然？|NO；手指蜷曲、共享掌位缺乏随按键的合理配合。|
|Q7 存在明显穿键、悬浮或指链问题？|YES；持续悬浮、左掌键体命中、右手局部关节变化过快。|
|Q8 琴键下沉与 NOTE_ON 同步？|YES；同 timeline 起动，35ms 达到全行程；最终60fps量化最多8.33ms。|
|Q9 钢琴音高与 MIDI 对应？|YES；原采样 zone/ratio 检查通过，7 个实际音高的强谐波估计均在 ±25 cents 内。|
|Q10 视频有真实可听音轨？|YES；AAC 双声道，解码后非静音，18 个采样 voice，双手复音。|
|Q11 统一自然皮肤材质？|NO（完整质量门槛）；统一肤色 YES，半写实自然观感仍未通过。|
|Q12 更换 MIDI 有清晰复用接口？|YES；歌曲/指法数据 → timeline → 分离的手、键、音频执行器；新曲仍须人工规划与重新验证。|
|Q13 最终状态？|MIDI_DRIVEN_PIANO_PERFORMANCE_POC_PARTIAL；PRODUCT_DEMO_PASS = NO。|

## 曲目与指法审核

官方页面、MIDI、PDF 与同源 LilyPond 都已保留，来源详见 [SOURCE_AND_LICENSE_R1.md](SOURCE_AND_LICENSE_R1.md)。MIDI format1，PPQ384，tempo500000μs/quarter（120BPM），2/4，D大调；两条音乐轨道分别对应谱面的 treble/bass staff。前两小节的音高、起止 tick 和时值通过精确比较。片段 velocity 全90，无 pedal 事件；同手同时持音最多1，两手合计最多2。此 POC **没有验证同手和弦**，不可借双手复音宣称多指和弦能力成立。

第3小节开始需快速换音区，按用户允许的规模缩小到连续第1–2小节，未改音、未删音、未改速度。18个音、36个NOTE_ON/OFF事件，音乐长2秒。统一增加0.7秒准备和0.7秒释放/展示尾部，成片3.4秒。

官方谱面与 MIDI 无可用 finger 编号。如下指法是有限设计候选，不是权威指法，也没有进行自动搜索：

|小节|手|原 MIDI / 音名|候选手指|MIDI 时值 / velocity|
|---|---|---|---|---|
|1、2|RIGHT|81 A5 → 79 G5 → 78 F♯5 → 76 E5 → 74 D5|5 → 4 → 3 → 2 → 1|四分 + 四个十六分；90|
|1、2|LEFT|38 D2 → 50 D3 → 38 D2 → 50 D3|5 → 1 → 5 → 1|四个八分；90|

左手八度采用5/1交替，右手D5–A5五指位置。该设计尚未由钢琴教师确认；本轮没有测试替代指法。逐音审核表在 `PROVISIONAL_FINGERING_PLAN_R1.json`，不将生成结果回写成已批准指法。

## 一个新动作候选

只读取冻结 R2/L1 的 rest rig、weights、corrective 与固定 pad 定义，从零生成新的 `NEW_MIDI_PROCEDURAL_R_R1` / `NEW_MIDI_PROCEDURAL_L_R1`。无 PianoVAM 动画、landmark、已拟合 root 数组输入。使用的既有辅助代码只负责静态身份与键面几何测量。

每手一个共享掌位，以五个 home targets 一次规划 root XYZ/yaw；本候选 root 在片段内保持固定。Root 高度限定55–85mm，yaw ±12°。每指3个非负 palmar flexion + 基部 spread，无轴向 twist；长指上限75/95/65°，拇指40/55/55°，spread长指±28°/拇指±35°。这些是本次工程候选限制，不是人体活动范围认证。一次全局 home 求解后，按120Hz顺序局部IK，保存为同一新候选，没有重启参数搜索。

统一阶段：PREPARATION → 前100ms APPROACH → NOTE_ON时CONTACT目标 → 35ms KEY_PRESS → NOTE_OFF后70ms RELEASE → 回到home hover的 NEXT_NOTE_TRANSITION。音频释放包络240ms。原 timing没有吸附到帧。数学目标曲线连续，但**数值IK分支并未保证关节连续自然**：右手在展示时间2.608秒、食指中间关节出现最大21.817°/8.33ms跳变，就是当前失败，而不是用插值标签掩盖它。

具体失败层级：

- FINGERING_PLAN：尚为设计候选，不能归罪于错误权威指法；未测试替代。
- ROOT_PLANNING：固定共享home掌位对八度与按键行程配合不足，没有自然随动。
- FINGER_KINEMATICS：关节达到边界，部分手指过度蜷曲；右手有局部分支快速变化。
- KEY_CONTACT：多数持音时 pad 仍在键面上方，左掌区域也出现键体命中。
- AUDIO_SYNC：音频与琴键事件时钟通过；由于实际手部未触键，**手指触键与声音的完整产品同步没有通过**。

## 接触与静态资产保护

沿用固定 pad 标记、原垂直3mm / 水平2mm容差和实际可奏键面区域，未为提高成绩改 marker 或 tolerance。

|指标|RIGHT|LEFT|
|---|---:|---:|
|起音接触|8/10|4/8|
|持音接触（120Hz相关观测）|48/240|12/240|
|持音悬浮 >3mm|192|228|
|最大垂直误差|17.480mm|14.908mm|
|目标键横向区域误差最大值|0mm|0mm|
|掌部键体命中观测 /409|0|120|
|腕部键体命中观测 /409|0|0|

机器使用 inherited key-piece vertex-volume screen；不是完整穿插证明，也没有开展 frozen anatomy 重审。0mm横向误差只说明所分配 pad 落在目标键平面区域，不能说明实际按下。其他手指/mesh与相邻键接触不由该数字排除。起音8/10也不能掩盖持音阶段48/240。

保存场景重新打开验证：R/L都是3300 vertices、21 bones；移除实验 root/新Action/展示材质后，rest、topology、static weights、corrective/driver、原shading等静态身份 MATCH。FK pad与保存场景最大差R0.000422mm、L0.000367mm；rigid pad与实际skin顶点最大差R0.213mm、L0.247mm。最低有限性检查通过，不表示动作自然。

212个受保护文件 SHA256 unchanged，包括三份正式手基线、Grand frozen authority、原音源和之前审计根目录产物。右R2 `c946fed318fa88c238d9aacc30cfb4e52f268848f0ad65a4dcbf594754d791f0`；左R1 `54307bb199a75a5e684c29d346de9ca6bf2f8e7696911d9d69c57559516ad1a7`；右R1 fallback `4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2`。所有修改仅在本审计目录和候选实例中。

## 音频与音画同步

使用现有 Grand 的 CC0 VCSL Kawai Grand 真钢琴采样。18个NOTE_ON各有独立voice，NOTE_OFF按原时刻进入240ms指数释放。复用既有采样zone、velocity≥80选V4、pitchRatio、力度公式与master0.72；离线适配器用48kHz PCM统一调度，取代浏览器即时音频时钟，不使用正弦波。

音源以 sampler C3=MIDI60命名，界面以scientific C4=MIDI60显示，按manifest数字映射，避免错八度。源文件hash全部匹配。逐asset移除录音前的leading silence，阈值与trim样本数逐项记录。没有提前音符时间，也没有改音高内容。单弱基频测量在D2不可靠，修正为前6谐波中最强3项的f/n中位数，保留全部频谱证据；7个用到的音最大估计偏差10.37cents，均小于25cents。该检查结合已核验root/ratio，不冒充盲转谱或听觉专家验收。

最终 MP4 实含AAC stereo音轨，解码RMS=0.056072，非静音。PCM与最终AAC交叉相关滞后0.000ms；事件调度量化0ms，键下沉开始与NOTE_ON共时，35ms后达全行程，60fps展示量化最多8.33ms。复音峰值2个held voice，release tail可叠加；18voice没有丢音、无clipping。手触键失败不能由这些时钟检查抵消。

## 统一皮肤材质

左右实例共用一个 `SEMI_REALISTIC_HUMAN_SKIN` 目标shader：同base color，roughness0.49、subsurface0.055、轻微微表面bump，无金属和夸张褶皱。只增加候选实例材质，未保存回正式资产；不以不同颜色区分左右手，界面用LEFT/RIGHT。

实际预检中材质虽统一，画面仍偏粉白、平面分面与模型感可见，**不能认定满足半写实真人皮肤观感**。只有这一套材质/灯光，没有多轮美术调参。[SKIN_MATERIAL_REVIEW_R1.png](../../../artifacts/91a6d975e0359a8b2660.md)保留原样供Human判断。

## 可复用接口与重现

`SONG_DATA_R1.json` 保存曲目、谱面声部、指法/布局输入；`PERFORMANCE_TIMELINE_R1.json` 是唯一事件时钟。`03_motion_plan.py`生成手关节轨迹，`performance_core.py`派生key curve，`05_audio.py`独立生成PCM；`04_scene.py`产生Blender候选，`08_media.py`仅把已同步视频/音轨封装。音频不写进hand Action，Blender动作没有硬编码音频剪辑。

更换MIDI需要新的score-checked hand/finger plan和layout，再交给同一timeline/执行接口；当前导入核对入口专门验证Musette前两小节。**没有验证任意MIDI，也没有完整指法生成器、同手和弦系统或多曲播放器**。首次运行后仅把home layout同值提取为SONG_DATA，未改变候选数组。

重现入口：`powershell -File reproduce.ps1 -Mode Verify`复核现有交付；显式`-Mode Rebuild`用相同输入重建同一候选。依赖：Python3.12、审计内`_deps`的mido/scipy/PyMuPDF、Pillow/numpy、Blender5.1.2、ffmpeg/ffprobe；本次全部具备。脚本保留，正式资产只读。渲染从已有帧续跑仅用于恢复相同候选，不用于美术变体。

允许的实现bug修复记录：候选原无材质槽时增加实例槽；评估函数补齐math/tolerance依赖；rest mesh坐标区域诊断改为实际世界坐标，避免把全部3300点误标为腕部；弱低音基频改用强谐波验证。上述修复均未重求解或改动第一次动作候选。渲染缓存重启没有改变材质、相机、采样质量或帧率。

## 交付与停止

[审阅页](../../../../examples/historical/audits/midi_driven_dual_hand_piano_performance_poc_r1/review.html)含播放/暂停/重播、音量与原速/慢速查看；[第一版带声音视频](../../../artifacts/9aa30112111453d4efc7.md)为1600×900、60fps、204帧、3.4秒；[候选Blend](../../../artifacts/71ea4932d9318c389bd2.md)可检查全部手、键、Action和相机。谱面、timeline、指法、规划、sync与保护JSON保留。机器没有代替Human批准，声音检测也没有冒充实际聆听评价。

|字段|结果|
|---|---|
|TEST_PIECE|Musette, BWV Anh.126|
|TEST_MEASURES|1–2|
|MIDI_SOURCE|Mutopia Project official MIDI; Public Domain|
|FINGERING_STATUS|DESIGNED_PROVISIONAL / HUMAN_REVIEW_PENDING|
|HAND_MOTION|NEW_PROCEDURAL_CANDIDATE / NATURALNESS_FAIL|
|KEY_CONTACT|FAIL; onset R8/10 L4/8; held R48/240 L12/240|
|AUDIO_SYNC|KEY_AUDIO_PASS / HAND_CONTACT_SYNC_FAIL|
|SKIN_MATERIAL|UNIFIED_SKIN_APPLIED / REALISM_NOT_PASSED|
|PRODUCT_DEMO_VIDEO|product_midi_dual_hand_with_audio.mp4|
|PRODUCT_DEMO_PASS|NO|
|FINAL_STATUS|MIDI_DRIVEN_PIANO_PERFORMANCE_POC_PARTIAL|
|RIGHT_R2_UNCHANGED|YES|
|LEFT_R1_UNCHANGED|YES|
|PIANO_BASELINE_UNCHANGED|YES|

**STOP — HUMAN REVIEW。没有进入整首、多曲目播放器、正式Web集成或商业发布。**

本地审阅交互复核：隔离 Chrome 验证播放推进、暂停保持、定位和重播推进均 PASS，未静音。内置 CUA 进程不可用，因此使用本地浏览器回退。临时简易 HTTP 服务不支持视频 Range，改用 `node review_server.cjs` 后验证通过（仅127.0.0.1:8788）。可直接打开 review.html 或以此服务审阅；并非正式 Web 集成。
