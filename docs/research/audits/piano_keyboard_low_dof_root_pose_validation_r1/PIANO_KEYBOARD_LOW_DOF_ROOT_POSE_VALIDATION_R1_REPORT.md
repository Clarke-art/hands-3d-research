# PIANO_KEYBOARD_LOW_DOF_ROOT_POSE_VALIDATION_R1

最终：**ROOT_POSE_MODEL_STILL_BLOCKED**。**STOP — HUMAN REVIEW**。

本状态针对本轮 MODEL A 候选安装：手掌放置和整体自然度未过关，不能用“只是预测指法不准”放行。它不证明所有合法 root orientation 都失败；源数据、指法和拟合误差的因果占比仍未隔离。

MODEL A 不通过；MODEL B 未达到合法启动条件，未执行。没有 MODEL C、第二轮参数 sweep 或 finger correction。不能把 `SOURCE_2_5D_OR_CONTACT_PRECISION_LIMIT` 的名称当作因果结论：它只是“粗略覆盖可行、严格接触不可行”的待解释残差。当前也不满足 C 类“root 本身已经合理”的前提，因此不以 EVIDENCE_LIMITED 状态暗示安装已成功。B 类在本报告中的结论边界是当前候选仍然阻塞；**未证实失败主要来自源/指法，也未证明排除了它们**。

## Q1–Q18

|问题|回答|
|---|---|
|Q1 上一轮 fixed-orientation model 保持 REJECTED？|YES；仅重放原缓存作对照，没有重新求解。|
|Q2 MODEL A = XYZ + YAW 是否执行？|YES；完整 421 observations，全局单次求解。|
|Q3 MODEL A 是否明显优于上一轮？|NO；部分朝向改善，整体自然度与接触未明显改善。|
|Q4 MODEL A 多音整体 placement 是否大部分合理？|NO；粗略 pad 覆盖 R 27/38、L 64/82，但结合无掌腕压键仅 R 27/38、L 20/82。|
|Q5 预测指法接触是否实质改善？|NO；R 9/39 → 7/39，L 4/26 → 3/26。|
|Q6 可能指法标签冲突占失败多少？|多音 0/116；含单音 2/297（0.67%），R、L 各 1 次。分母为相关的持音观测，不是独立音符。|
|Q7 ROOT_POSE_GEOMETRIC_FAILURE 是否仍为主要问题？|NO（限事前诊断桶）；多音失败中 9/116（7.76%）。这不等于整体掌部放置通过，也不证明余项由源数据造成。|
|Q8 MODEL B 满足启动条件？|NO；depth/approach 20/116（17.24%），两手均未占主要失败。|
|Q9 MODEL B 是否执行？|NO。|
|Q10 MODEL B 是否进一步改善？|NOT_RUN。|
|Q11 最终双手 keyboard placement 是否可信？|NO（agent 可见预检）；Human 审阅待定。|
|Q12 Labeled contact？|RIGHT 7/39（17.95%）；LEFT 3/26（11.54%）。PREDICTED_FINGER_CONTACT，非 ground truth。|
|Q13 Unlabeled cluster feasibility？|多音严格：R 1/38、L 3/82；粗略覆盖：R 27/38、L 64/82。粗略覆盖不是接触。|
|Q14 掌腕碰撞是否明显降低？|NO；掌+腕观测计数 374 → 319，仅下降 14.71%，未到事前 50% 门槛。|
|Q15 Root orientation / translation 是否连续自然？|NO；数值连续性 YES，自然度 NO。最大每 60Hz 步长 R 6.072mm / 1.679°，L 4.383mm / 1.357°。|
|Q16 LEFT fast bend？|DEFERRED；未隔离为 contact blocker。|
|Q17 RIGHT fast bend？|DEFERRED；未隔离为 contact blocker。|
|Q18 最终状态？|ROOT_POSE_MODEL_STILL_BLOCKED；仅指本轮候选仍阻塞，不是架构不可能性结论。|

## 事前锁定与执行边界

冻结的 R2 / L1、双手 Action、88 键几何、canonical frame、键面、可奏区域、10 个 pad marker 全部继承。timeline 与 8 份继承 JSON 逐字节一致。上一轮固定朝向模型继续 REJECTED，仅复用已存空间缓存制作同机位视频，没有再次求解旧模型。

外部 root 属于 **PRODUCT SPATIALIZATION LAYER**；输入是 non-metric 2.5D source，不能称为真实测得 wrist-world mocap。MODEL A 只增加绕 canonical +Z 的 yaw；pitch=roll=0，scale=1。

事前范围 yaw ±60°、预留 pitch ±25°、roll ±35°。依据 approved Action 中 wrist 最大 heading 49.388°、longitudinal elevation 15.068°、bank 19.175°，再加一白键宽/掌长或黑键高度/掌长、掌宽的几何裕量，向上取整到 5°。这不是实测人体活动范围。掌宽 78.445mm、腕至中指 MCP 123.444mm；总 heading 超出 ±32.435° 软走廊受到惩罚。正常演奏外观仍须独立预检，不能靠 bounds 内即算自然。

XYZ 继承全局二阶时间正则 λ=530.8416。Yaw 使用每 0.2 秒一个 cubic B-spline control、36 个系数，同一时间正则及固定弱零先验。单个零朝向初值，单次全局 variable-projection Gauss-Newton；右 26、左 16 次迭代，没有重启、局部参数调节或重配手指。实际 yaw R −21.117°..30.842°、L −16.359°..25.222°，无系数触碰边界。

保存场景将求解曲线烘焙为 421 个 60Hz 外部 root location/quaternion 关键帧，使用同半球四元数和线性插值。数学 yaw 曲线为 C2；**Blender 烘焙回放仅保证连续，不能声称烘焙曲线本身 C2**。上限 10mm、2.207°/60Hz 均满足。

求解前保存以下 SHA256；结果后复核全部 MATCHED，未扩大 bounds：

- `ROOT_POSE_DOF_POLICY_R1.json` SHA256 `4650601e344c46d4f2637cbe86bcc64e3004d910ecd8a242d04eb12c5db1d1cb`
- `ROOT_POSE_TEMPORAL_POLICY_R1.json` SHA256 `f30aa481c6256082cb63c86837d10006bb5a9cf27c97fc2272f730d5a3898448`
- `EVALUATION_AND_MODEL_B_GATE_POLICY_R1.json` SHA256 `397b3f3cd26b04f8c3de223c808d724d1f8c186cc91c70f010b4cef111efb21a`

## 接触、键群、整体手掌放置

严格接触容差仍为垂直 3mm、水平 2mm，并检查原可奏键面区域。起音按原始事件时间插值测量，未吸附 MIDI timing。粗略键群覆盖另用事前半白键宽 11.545mm 水平裕量、完整白键行程 10mm 高度裕量，**不是放宽接触 PASS**。

|手 / cluster|观测|原预测标签全部接触|无标签严格可行|无标签粗略覆盖|
|---|---:|---:|---:|---:|
|R SINGLE_NOTE|189|70|71|169|
|R 2_NOTE_CLUSTER|37|1|1|27|
|R 3_PLUS_NOTE_CLUSTER|1|0|0|0|
|L SINGLE_NOTE|235|173|174|229|
|L 2_NOTE_CLUSTER|80|3|3|63|
|L 3_PLUS_NOTE_CLUSTER|2|0|0|1|

多音是主要判断依据，单音成功没有用于包装 root 成功。3+ 观测极少，不能泛化为丰富和弦验证。全手五 pad 的 span、target span、中心偏差、5×N 键面距离矩阵和诊断匹配见 `KEY_CLUSTER_PLACEMENT_METRIC_R1.json`。匹配只用于诊断，未回写 label 或输入 solver。每个 target 要求不同 pad，不能用一个 pad 覆盖多音。

同一时刻合并粗略覆盖与原掌腕碰撞结果后，多音整体放置的必要条件只有 R 27/38、L 20/82。这个合并检查没有新阈值，保留事前 pad 粗覆盖指标原值，但防止把“手指大概在音区上”误报成“手掌安装可信”。

## 失败归因与 MODEL B gate

多音原标签失败共 116 个相关 held observations：

|事前诊断类别|数量|占多音失败|
|---|---:|---:|
|LIKELY_FINGERING_LABEL_CONFLICT|0|0%|
|SOURCE_2_5D_OR_CONTACT_PRECISION_LIMIT|87|75%|
|DEPTH_OR_APPROACH_ORIENTATION_LIMIT|20|17.24%|
|ROOT_POSE_GEOMETRIC_FAILURE|9|7.76%|

87 次只意味着粗略覆盖与严格接触之间有精度缺口，**不能证明 SOURCE_2_5D_LIMIT**。9 次几何失败也只描述当前 fitted pose，不能证明所有合法 root pose 不可行。含单音的 297 次标签失败中仅 2 次可由严格无标签匹配救回；不足以认为主要失败是 predicted fingering error，也不能排除预测错误。

Finger-label-independent 匹配仍继承 predicted HAND 集合；当前 pose 本身又由原 predicted finger 拟合，因此这不是完全独立的对照。无逐事件 confidence，25 个 UNKNOWN hand 音没有自动重分。错误 hand、target、非标定 source 与根拟合误差尚未因果隔离。

MODEL B 事前要求双方及合计 depth/approach >50%，且可见证据支持主要由方向自由度受限造成。R 10/37、L 10/79、合计 20/116，均不满足。仅看到 palm 低或指尖穿键，不足以证明 pitch/roll 会解决主要误差。**不运行 B**，无 B result 或虚构改善。

## 碰撞、悬浮、可见预检

|指标（421 观测/手）|R 旧 → A|L 旧 → A|
|---|---:|---:|
|掌部压入键体|156 → 107|214 → 212|
|腕部压入键体|4 → 0|0 → 0|
|任意 mesh 顶点键体命中|293 → 288|418 → 416|

继承原 key-piece volume screen，仅计超过键面 3mm 的顶点；是候选碰撞筛查，不是完整碰撞证明。掌+腕计数总和 374 → 319，下降 14.71% 未通过事前 50%。R 起音穿透 14、悬浮 9；L 穿透 6、悬浮 0，但错键及横向不匹配仍会失败。不能用“没有悬浮”替代完整接触。

Agent 查看全部 210 个 teaching-view 输出帧及 old/A/close 时间条。开头约 source 11.50–12.17s 双腕/前臂端投影拥挤；部分时刻右手朝向更顺，但全段没有一致自然的键上落位。没有做 hidden crossing、normal-dot、逐顶点 anatomy 或 forensic macro。可见评价是 agent 预检，**不是 Human 批准**。

## 保护、timeline、最低机器检查

候选保存后重新打开，421 evaluations 全部检查；R/L geometry 最大差 0.001404/0.001175mm，marker 最大差 0.001178/0.001067mm。NaN/Inf、gross collapse、degenerate、gross tearing 均为 0；移除外部 audit root/Action 后 intrinsic ZERO digest MATCH。内部 Action digest MATCH，mesh/weights/rest/driver/corrective identity MATCH。

R2 SHA256 `c946fed318fa88c238d9aacc30cfb4e52f268848f0ad65a4dcbf594754d791f0`；L1 `54307bb199a75a5e684c29d346de9ca6bf2f8e7696911d9d69c57559516ad1a7`；R1 fallback `4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2`。全部 unchanged。正式 frozen piano 及上一轮根目录产物均 unchanged，153 个受保护文件全部复核。非 frozen 的 mutable latest-stage pointer 不属于此保护范围；本轮从未写入。

timeline 仍为原窗口 11.5–18.5s：92 个相交音、179 个窗口事件；原 NOTE_ON/OFF、velocity、hand、finger、timing、pedal interface 不改。本窗口无 pedal event。键运动直接复用 timeline/animation，音频接口 READY，无音源、无碰撞触发。旧动画的一个 UNKNOWN G3 约 1.04ms 音在 60Hz held sampling 中未显现，精确事件仍保留；本轮未改这个继承限制。

first-web CLOSED。双手 fast bend PRESENT / DEFERRED，尚无可隔离 contact 因果，不升级 blocker。结构保护通过不等于 spatial contact safety 通过。

## Human 审阅产物

- [审阅页](../../../../examples/historical/audits/piano_keyboard_low_dof_root_pose_validation_r1/review.html)
- [完整 player + teaching 双视角](../../../artifacts/e23071caf74270cdd04f.md)
- [接触近景](../../../artifacts/ffcea179e8bb05f8f0ba.md)
- [固定朝向 vs MODEL A 同机位对照](../../../artifacts/43b7e4b3399bcde338f9.md)
- [可继续检查的候选场景](../../../artifacts/54166af92ff1841fbab4.md)

三条视频均 7.000s / 30fps / 210 帧，三视角、旧/A 对照同 camera、同 source time、同 keyboard/key animation。对照旧段来自既有缓存，未重新优化。视频无音轨，本轮不做音源。单张 review poster；连续 PNG 是渲染中间文件，不作为大量重复图片交付。

PianoVAM：CC BY-NC-SA 4.0；仅内部非商业验证，不改变原 source/license 限制。

## 交付状态

|字段|结果|
|---|---|
|MODEL_A_STATUS|FAIL|
|MODEL_B_STATUS|NOT_RUN_GATE_NOT_MET|
|ROOT_POSE|CONTINUOUS_BUT_PLACEMENT_NOT_VALIDATED|
|LABELED_CONTACT|R 7/39; L 3/26; AUTO_PREDICTED|
|UNLABELED_CLUSTER_FEASIBILITY|strict R 1/38, L 3/82; coarse R 27/38, L 64/82|
|FINGERING_CONFLICT|multi 0/116; all failed clusters 2/297 (0.67%)|
|COLLISION_STATUS|NOT_CLEARED; palm+wrist observations reduced 14.71%|
|LEFT_FINGERTIP_FAST_BEND|DEFERRED|
|RIGHT_FINGERTIP_FAST_BEND|DEFERRED|
|FINAL_STATUS|ROOT_POSE_MODEL_STILL_BLOCKED|
|NEXT_STAGE_RECOMMENDATION|Human 审阅后，优先取得可人工核验的 hand/finger 标注及有标定依据的 motion/contact 数据，再判别 root 与 source 的因果；本轮不启动。|
|HAND_BASELINES_UNCHANGED|YES|
|PIANO_BASELINE_UNCHANGED|YES|

**STOP — HUMAN REVIEW。等待 Human 决策。**
