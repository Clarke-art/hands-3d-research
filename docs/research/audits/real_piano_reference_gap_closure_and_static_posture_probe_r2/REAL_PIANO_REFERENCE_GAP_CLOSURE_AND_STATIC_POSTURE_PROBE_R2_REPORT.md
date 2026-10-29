# REAL_PIANO_REFERENCE_GAP_CLOSURE_AND_STATIC_POSTURE_PROBE_R2_REPORT

2026-10-08 · DESIGN_ONLY · HUMAN_VISIBLE_PRODUCT_QUALITY_FIRST

**FINAL_STATUS = REFERENCE_EVIDENCE_INSUFFICIENT**。补充了对侧八度静态参考、原版 Musette 身份与真实播放器访问结果，建立八类有证据边界的姿态合同；未执行静态候选。自然几何可行性仍 UNKNOWN，不能将 NOT_RUN 写成 PASS。

## 参考补证与本轮门槛

实际打开 PiaDOOR、Pianote、Hoffman Lesson 14/236；实际查看两张八度照片。PiaDOOR 是 Für Elise 左手 A–E–A 准备，有额外中间指任务；Pianote 新图是右手 C 八度，不能替代左手。Hoffman 官方文字确认五指 D/E/F#/G/A，Lesson 236 确认原版 A 段而非早期简化版。

三个官方教学页内实际点击播放后均要求登录/机器人验证，video.readyState=0、currentTime=0、duration 未知，未观察任何视频时间点。直接嵌入入口的错误 153 不是唯一失败依据；已经在正常来源页中重试播放。没有绕过验证或下载视频。

有限来源核查已停止。关键缺口是右手含黑键五指的可见协调关系，左手三闲置指及腕侧视也仍有限。**没有要求精确同曲、同演奏者、全部关节三维角或静态之前先证明动态过渡**。左手静态图加一般教学文字可支持部分约束，但音级指序本身不能补成可信的五指黑键演示。故本轮不执行条件式静态实验。

详见 [参考清单](REAL_PIANO_REFERENCE_MANIFEST_R2.md)、[八类合同](NATURAL_PIANO_HAND_POSTURE_CONTRACT_R2.md)。本合同 YES 代表依据分类与检验要求明确，不代表科学姿态完整、数值求解政策已校准或模型通过。

## 正式几何与资产保护

Blender 5.1.2 后台只读重新打开正式 RIGHT R2 / LEFT R1。两手 3300 顶点、21 骨；neutral canonical 网格最大偏差分别 2.2602e-13 / 1.7554e-13 mm，intrinsic identity 均匹配。保持 existing pad 定义，未保存 blend。

|测量|R2 结果|边界|
|---|---:|---|
|D2–D3 中心距|167.569 mm|不是必须精确达到的 pad 触点距|
|前部内侧区域最小点距|144.480 mm|零面积边缘下界，不是实际安全 pad 目标|
|左手静置 pad 空间距|153.007 mm|重新读取；不是最大自然跨度|
|D5–A5 中心距|95.754 mm|不证明共享掌位自然|
|F#5 黑白顶面高差|15.444 mm|正式静置键几何|
|F#5 前端相对白键前沿|49.421 mm|靠后；不能排成同深指尖直线|

全部毫米值是正式键盘已批准教学等效比例，不是制造商标定。完整可奏面见 [可行性 JSON](../../../../examples/historical/audits/real_piano_reference_gap_closure_and_static_posture_probe_r2/HAND_KEYBOARD_STATIC_FEASIBILITY_R2.json)。垂直 3 mm / 水平 2 mm 容差保持，且必须处于实际可奏区域；未实际测试任何接触、净空或关节项。

最终复核 **572 个受保护文件**，变化列表为空；三份手 baseline SHA 与用户指定值相同；钢琴 source manifest/runtime 及继承保护集均相同。保护范围/逐路径证据见 [保护 JSON](../../../../examples/historical/audits/real_piano_reference_gap_closure_and_static_posture_probe_r2/FINAL_ASSET_PROTECTION_R2.json) 和 `PROTECTED_INPUTS_BEFORE_R2.json`。没有修改 production pointer、MIDI、指法、音频、键几何、hand mesh/rest/weights/correctives/drivers。

## 静态与失败归因

L1/L2/R1/R2 全为 NOT_RUN，候选数 0，动作数 0。root 差异、实际候选 pad 跨度、主动指接触、闲置指、掌腕净空、邻键干扰、关节状态均无新测量。没有把旧失败动态帧重新命名为 R2 静态候选。

REFERENCE_EVIDENCE_LIMIT = BLOCKING；GEOMETRY_LIMIT = NOT_ESTABLISHED；POSTURE_CONSTRAINT_LIMIT = NOT_TESTED；IK_SOLVER_FAILURE = NOT_RUN。未证明需改正式 mesh/rig，也未证明自然可达。

## Human-visible 对比与交付

[review.html](../../../../examples/historical/audits/real_piano_reference_gap_closure_and_static_posture_probe_r2/review.html) 使用“真人来源链接 → 旧失败图 → R2 未执行状态”三栏。没有嵌入或重发布外部照片；引用旧图原文件，不生成重复图/视频。普通产品斜上方旧图及旧 CONTACT_SIDE 斜视风险图保留，不将其误标为新顶视、严格侧视或新 first-web 证据。R2 教学顶视、侧斜视、first-web 三项均明确 NOT_RUN。

条件式实验未启动，因此 **STATIC_POSTURE_PROBE_R2.blend、STATIC_POSTURE_RESULTS_R2.json、三张 EVIDENCE_*_R2.png 不生成**。这是门槛未满足的明确结果，非遗失文件。已交付报告、review.html、参考清单、合同、可行性 JSON、下一轮要求、最终保护 JSON，另附只读重新测量与访问/交付验证记录。

## Q1–Q12

|编号|问题|回答|依据|
|---|---|---|---|
|Q1|真实左手八度参考有效补充？|**PARTIAL**|左手静态图重新核验；新增对侧八度图片/文字，左手三闲置指与侧面仍缺证据。|
|Q2|右手含 F# 真人五指参考有效补充？|**PARTIAL**|官方指序文字重新核验；实际影像未播放，未新增黑键姿态观察。|
|Q3|建立有证据边界的自然姿态约束？|**YES**|八类约束逐项区分四种依据；定性合同成立，执行门槛未满足。|
|Q4|执行唯一静态候选？|**NO**|关键黑键五指可见关系尚未取得，不启动求解。|
|Q5|LEFT L1 小指 D2 自然触键？|**NOT_RUN**|未测试。|
|Q6|LEFT L2 拇指 D3 自然触键？|**NOT_RUN**|未测试。|
|Q7|左手中间三指自然？|**NOT_RUN**|未测试。|
|Q8|左手掌腕/键盘净空合理？|**NOT_RUN**|未测试。|
|Q9|RIGHT R1 五指准备自然？|**NOT_RUN**|未测试。|
|Q10|RIGHT R2 中指 F#5 触键自然？|**NOT_RUN**|未测试。|
|Q11|发现必须修改正式 mesh/rig 的证据？|**NO**|没有新候选或硬几何不可达证明；此 NO 不证明当前模型自然可达。|
|Q12|可进入下一轮动态规划器设计？|**NO**|静态与 Human 门槛均未通过。|

## 最终停止状态

```text
REAL_REFERENCE_STATUS = PARTIAL_STATIC_AND_TEXT / BLACK_KEY_VISUAL_UNVERIFIED
STATIC_PROBE = NOT_RUN
LEFT_OCTAVE_FEASIBILITY = UNKNOWN_NOT_RUN
RIGHT_FIVE_FINGER_FEASIBILITY = UNKNOWN_NOT_RUN
FSHARP_CONTACT = NOT_RUN
LEFT_IDLE_FINGERS = NOT_RUN
PALM_WRIST_CLEARANCE = NOT_RUN
NEXT_MOTION_PLANNER_READY = NO
FINAL_STATUS = REFERENCE_EVIDENCE_INSUFFICIENT
HAND_BASELINES_UNCHANGED = True
PIANO_BASELINE_UNCHANGED = True
STOP — HUMAN REVIEW
```

本轮等待 Human 决策。最小下一步是使可信五指黑键示范可实际核查，再判断是否授权一次有界四姿态静态实验；[后续要求](NEXT_MOTION_PLANNER_REQUIREMENTS_R2.md) 不构成自动进入动态规划或完整演奏生成的许可。
