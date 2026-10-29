# PIANO_HAND_POSTURE_REFERENCE_AND_STATIC_FEASIBILITY_R1

最高原则：HUMAN_VISIBLE_PRODUCT_QUALITY_FIRST。最终状态：**REFERENCE_EVIDENCE_INSUFFICIENT**。

本轮完成实际参考核查、冻结几何测量、旧规划问题分析和自然姿态合同草案；未生成静态候选，未进入动态演奏生成。不是宣称手的几何不可达，也不是自然手型通过。

## 证据结论与静态试验门槛

2 项真实静态照片已查看，另有 2 项官方教学文字。PiaDOOR 左手照片有八度跨度，但内部手指承担额外 E；MusicRadar 右手照片是 C–G 白键。Hoffman 视频遇到登录/机器人验证，只核对了官方文字；Fitch 公开教学文字不能代替实际侧视。缺失的是三闲置指及腕部在交替中的可见关系和含黑键的五指协调，未从透视图编造角度。

依据用户“如果参考和几何检查具备足够证据”的条件，本轮不执行静态摆放。四个目标状态均标 NOT_EXECUTED：L5 D2/L1 D3 准备、L1 D3/L5 D2 准备、R 五指准备、R 代表音触键。审核页第三栏明确显示候选未生成，旧图不冒充新静态结果。

## 几何测量

正式 R2/L1 用 Blender 5.1.2 后台只读重新打开；两手均 3300 顶点、21 骨。重新读取的 neutral 网格与既有 canonical probe 差异 < 0.000001 mm，intrinsic static identity 匹配；没有保存正式 blend。完整数字见 [HAND_KEYBOARD_SPAN_FEASIBILITY_R1.json](../../../../examples/historical/audits/piano_hand_posture_reference_and_static_feasibility_r1/HAND_KEYBOARD_SPAN_FEASIBILITY_R1.json)，重新读取证明见 [FORMAL_ASSET_READBACK_R1.json](../../../../examples/historical/audits/piano_hand_posture_reference_and_static_feasibility_r1/FORMAL_ASSET_READBACK_R1.json)。

冻结键盘沿用每 native unit = 0.53255794 m 的已批准等效比例；这是项目教学等效尺度，不是厂家标定。坐标 x 低音→高音、y 白键前沿→后方、z 向上；白键静置顶面 z=0。

| 项目 | 测量 | 解释 |
|---|---:|---|
| D2–D3 白键中心水平距 | 167.569 mm | 同深度、静置目标面距离 |
| 两键前部可奏区域最小点距 | 144.480 mm | 内侧边缘，零面积点；不能当作安全 pad 目标 |
| L 静置拇指–小指 pad 空间距 | 153.007 mm | x 投影 145.793 mm，不是最大伸展 |
| L 旧失败候选 pad 距离区间 | 149.929–176.185 mm | 已有轨迹只读统计，未做搜索；不证明自然姿态 |
| L 无关节限位链长上界 | 253.461 mm | 三角不等式松上界，不保证可达、无碰撞或自然 |
| L 掌宽（index–little MCP） | 78.445 mm | 骨头位置间距，不是照片测量 |
| D5–A5 中心水平距 | 95.754 mm | 五指共同掌姿仍待验证 |
| F#5 静置顶面/前端深度 | z=15.444 / y=49.421 mm | 黑键高且靠后，不能套白键同平面 |

手指长度在 JSON 中逐指记录：骨长、关节起点到 pad 的分段折线长度，避免把弯曲指的直线端点距离称为指长。每个目标键的完整前/后可奏矩形保留，无标准尺寸替换。

可用腕高的完整自然区间**未知**。旧 root 实际 z：L 45.000–62.554 mm、R 45.000–57.480 mm；这只是旧候选摆放结果。模型没有完整前臂/肘，俯视照片不能给可信侧视约束，旧数值边界不升级为人体范围。

基本净空：沿用已保存/重开的真实变形网格筛查，L 掌部碰撞观察 129/409，R 10/409，腕部为 0/409。该结果是顶点入键体的粗筛，掌区按静置 y 分段且包含近端拇指；“腕部 0”不等于完整表面无碰撞。每个手的实际 mesh 最低 z 另在 JSON 中，跨键外的最低 z 不能直接解释成键体穿透。

因此回答“当前左手是否能在自然掌腕下完成 D2/D3”：**尚不能确认**。有单点跨度空间和已有接触记录，但没有同时满足自然形态、正确接触、共同掌部与净空的可信见证。不能反向宣称必须放大手或改骨骼。

## 继承与保护

曲目 Musette BWV Anh.126 第 1–2 小节。右手 D5/E5/F#5/G5/A5 → 1/2/3/4/5，左手 D2/D3 → 5/1；继续 DESIGN_PROVISIONAL。没有改 MIDI、Timeline、velocity、NOTE_ON/OFF、88 键映射、下沉规则、采样音源、音频调度、PianoVAM、材质、weights、first-web corrective、rig 或 production pointer。

两张交付证据图仅用上一轮正常教学视角作适度裁切，时间点和哈希见 EVIDENCE_IMAGE_PROVENANCE_R1.json；没有重新渲染或美化。外部照片不嵌入审核页，只给原站链接与图片位置。皮肤真实感仍独立待解决。

## Q1–Q11

**Q1.** 是，找到并查看 PiaDOOR 左手白键八度静态照片；不是 D2/D3，且有 E 的额外任务。三闲置指及连续腕部证据不足。

**Q2.** 是，找到并查看 Daniel Griffiths 右手 C–G 五指照片；Hoffman 官方文字支持 D/E/F#/G/A 指序，但视频未能播放，未验证黑键换指画面。

**Q3.** 未证实自然匹配。D2–D3 中心距 167.569 mm；左手静置 pad 空间跨度 153.007 mm，旧失败候选最大 176.185 mm。后者有碰撞，不能作为自然可达证明。

**Q4.** 未证实自然匹配。D5–A5 中心距 95.754 mm；F# 高 15.444 mm、前端深度 49.421 mm。各指单独能触键不等于五指共同掌姿可行。

**Q5.** 是。固定姿态增量/简单被动耦合、逐时刻接触目标、掌部回拉初始化、少量净空代理，均缺少已验证的真实演奏姿态依据；旧版已有 shared root 和连续性限制。

**Q6.** 已建立带来源、产品要求、rig 支持与未知项的 A–F 合同草案；未获教师批准，连续动作部分证据未闭合。

**Q7.** 未执行。参考不足，未通过用户规定的静态试验前置门槛；静态候选 0 份、新完整 Action 0 份。

**Q8.** 未知。没有证明左手三闲置指自然与拇指/小指正确接触、掌部净空能同时成立。

**Q9.** 尚不可接受为已验证结果。旧版掌部碰撞筛查 L 129/409、R 10/409；真实腕高和掌底侧视证据不足。

**Q10.** 未发现必须改正式 mesh、骨长或 rig 的证据；也未证明硬几何不可达。保持正式资产不变。

**Q11.** 可据需求草案讨论协调规划器架构；不能据此宣布证据充分并开始实现。先补可核查动作参考，再完成唯一四姿态静态验证。

## 状态

```text
REAL_PIANO_REFERENCE = PARTIAL_VERIFIED_STATIC_AND_TEXT
LEFT_OCTAVE_GEOMETRY = NATURAL_FEASIBILITY_UNPROVEN
RIGHT_FIVE_FINGER_GEOMETRY = NATURAL_FEASIBILITY_UNPROVEN
LEFT_IDLE_FINGER_POSTURE = UNVERIFIED
HAND_WRIST_POSTURE = UNVERIFIED_WITH_PRIOR_COLLISION_RISK
STATIC_CONTACT_FEASIBILITY = NOT_TESTED_REFERENCE_GATE_FAILED
NEXT_MOTION_ENGINE_REQUIREMENTS = DRAFTED_IMPLEMENTATION_GATE_CLOSED
FINAL_STATUS = REFERENCE_EVIDENCE_INSUFFICIENT
HAND_BASELINES_UNCHANGED = TRUE
PIANO_BASELINE_UNCHANGED = TRUE
STOP — HUMAN REVIEW
```

交付：[review.html](../../../../examples/historical/audits/piano_hand_posture_reference_and_static_feasibility_r1/review.html) · [真实参考](REAL_PIANO_REFERENCE_MANIFEST_R1.md) · [姿态合同](NATURAL_PIANO_HAND_POSTURE_CONTRACT_R1.md) · [下一阶段需求](NEXT_MOTION_ENGINE_REQUIREMENTS_R1.md)。不自动进入完整动态演奏。
