# LEFT_OCTAVE_NEIGHBOR_KEY_CLEARANCE_CONFLICT_ISOLATION_R1_REPORT

2026-10-09 · DIAGNOSIS_ONLY · HUMAN_VISIBLE_PRODUCT_QUALITY_FIRST

**诊断分类：ROOT_PATH_CONFLICT。受控对照支持ROOT_CONTACT_CLEARANCE_TRADEOFF。** 本轮新动态候选0，不修复、不推翻静态批准、不解除上一候选BLOCKED。

## 有限对象定位
对最新保存重开的候选做一次A/B对照，共348个240Hz及原边界样点。只检查E2/F♯2两个正式键体和实际进入它们的17个皮肤顶点；区域归属依据原骨骼权重与指链名，不依据“处于两端之间”的位置猜测。E2/F♯2均全程未下沉，穿入发生于手移动靠近它们。键体实际顶点验证为8角点矩形体，非不贴合包围盒近似。
|键 / 表面|有限顶点|最大低于键顶深度|最短退出距离的最大值|原>3mm门槛范围|
|---|---|---:|---:|---|
|E2 / LITTLE末节侧面|272,279,1315,1331,1333,1334,2736,2737|3.083002mm|1.449395mm|2点：279,1333|
|F♯2 / MIDDLE末节侧面|211,259,261,1291,1292,1294,2716|3.405533mm|1.189097mm|1点：1294|
|F♯2 / RING末节侧面|61,2652|1.789859mm|0.270593mm|0点|
没有发现INDEX、THUMB或PALM进入这两个键体的已采样顶点。这里的结论仅指所检查区域与时段，不是全手解剖审计，也不是所有三角面相交的穷尽证明。
“最大竖向深度”与“最短退出距离”可能来自不同顶点，均不能直接换算为可见面积。以前只列>3mm深度命中的报告没有覆盖无名指浅层进入；本轮完整列出正穿入，原容差与门槛均未放宽。
## 时间及动作过程
准备和两次NOTE_ON本身没有命中。D2下沉驱动掌腕follow-through后，F♯2先出现中指侧面进入，随后E2小指及F♯2无名指进入；持键期间保持。D2释放、root恢复时逐步清空。首轮冲突跨越D3起音，第二轮冲突跨越D3回弹；独立D3持键时（如1.100s）没有这两个邻键冲突，因此不能归因为拇指D3单独按键。
|区域|第一次已观测命中|第二次已观测命中|每次持续时间估计 / 上下界|
|---|---|---|---|
|E2小指|0.720833–0.979167s|1.220833–1.479167s|0.262500s / [0.258333,0.266667]s|
|F♯2中指|0.716667–0.987500s|1.216667–1.487500s|0.275000s / [0.270833,0.279167]s|
|F♯2无名指|0.725000–0.975000s|1.225000–1.475000s|0.254167s / [0.250000,0.258333]s|
穿入起止为last-clear/first-hit、last-hit/first-clear采样夹逼，时间分辨率约4.167ms。两次合计E2约0.525s，F♯2约0.550s；>3mm旧门槛的每次持续估计分别0.229167s、0.237500s。详细事件逐项记录当前键状态、手部对象、区域、顶点、两种深度和当时D2/D3接触，见NEIGHBOR_KEY_PENETRATION_EVENTS_R1.json。
## 唯一root因果对照
A = 当前保存的动态root + 当前指关节Action。B = 完全相同的当前指关节Action，仅临时移除外部root动画绑定并恢复已批准L1/L2共同root矩阵。B只存在于内存，之后恢复原Action绑定，从未保存blend或插入关键帧。
每个样点A/B的全部局部关节矩阵差为0，D2/D3键角差为0；会话前后全部6个Action的曲线数据哈希完全相同。A在原180个样点的skin位置与上一轮保存重开数据最大差0mm。10个原pad定义原样读取。
|检查|A 当前动态root|B 静态root反事实|
|---|---|---|
|E2/F♯2实际顶点穿入|8 / 9顶点峰值|0 / 0，全部已采样穿入清空|
|两次D2完整接触|PASS，max skin2.969126mm|FAIL，max skin7.689179mm|
|D3完整接触|PASS，max skin1.983426mm|FAIL，max skin6.652730mm|
B在D3独立持键区间与A相同，例如1.100s均gap约0.933mm；失接触集中在与D2/root变化相重叠的起音及释放区间。B沿用最新已协调过的拇指Action，绝不等同于“恢复更早的整个原失败动作”。
因此，root变化对于当前轨迹中的冲突有受控因果证据，选择ROOT_PATH_CONFLICT。中指/无名指当前姿态在A路径下缺少净空也是直接事实，但B保持同样姿态即可清空，不能据此宣称闲置关节独立致因或直接改判COUPLED_ROOT_FINGER_CONFLICT。未实施任何关节干预，故不能量化其独立贡献。此结论限定于该已保存动作，不能扩展成所有可选root或指法方案的唯一根因。
## Human-visible产品视角
两张证据图只使用0.733333/0.750000/0.766667s三张连续60fps正常画面，三成熟相机齐备；A复用，B仅新增9张内部静帧。证据标签均位于画外，没有放大局部、增加骨骼或遮盖皮肤。未生成新视频或完整演奏。
正常图像可以看到掌腕高度与D2接近程度差异，B小指重新明显悬空；但未确认E2/F♯2存在明显大面积穿键。最终可见证据等级GEOMETRY_ONLY_CONFLICT，局部被遮挡表面的可辨性仍有限。SUBTLE_VISIBLE_INTERFERENCE未独立确证，不能把邻近/遮挡等同于穿越。B腕部保持批准静态位置，未见额外明显畸形，但动态接触失败，因此不是可接受的新方案。详见HUMAN_VISIBLE_CONFLICT_REVIEW_R1.md。
## 唯一推荐路线与停止
仅推荐 **ROOT_PATH_CONFLICT**：如果Human后续授权，应以现有root路径造成的接触/净空权衡为研究对象。当前结果没有证明已经存在满足所有条件的解，也没有证明需要修改正式mesh/rig。本轮不实施路径或手指修复，不开第二种对照。
最终重新核对2993份继承/冻结文件，变化0；三份正式手基线SHA、Grand权威、四静态core、当前及原失败Action、MIDI、音频、marker、production pointers保持。输出目录无blend文件，新Action数量0。
## Q1–Q12
|问题|答案|
|---|---|
|Q1|LITTLE：小指末节侧面，8个有限命中顶点；不是中间三指或掌面。|
|Q2|MIDDLE + RING：中指7个、无名指2个末节侧面顶点。超过3mm的最深命中仅来自中指。|
|Q3|E2观测命中0.720833–0.979167及1.220833–1.479167s；F♯2为0.716667–0.987500及1.216667–1.487500s。均集中两次D2下沉、持键及回弹前段。|
|Q4|E2最大竖向3.083mm，8顶点，每次约0.2625s；F♯2最大3.406mm，9顶点，每次约0.2750s。持续时间为240Hz采样区间估计，不是精确穿越时刻。|
|Q5|NO — 正常产品视角未确认明显大面积穿入；证据等级GEOMETRY_ONLY_CONFLICT。|
|Q6|YES — 保持同一当前关节Action，恢复静态root后，两键所有已采样顶点穿入消失。|
|Q7|YES — D2最大skin gap恢复7.689mm；D3也失接触，最大6.653mm。|
|Q8|YES — 受控root干预支持当前路径中的ROOT_CONTACT_CLEARANCE_TRADEOFF。|
|Q9|YES — 当前root下中指/无名指未避开F♯2；但同样姿态在静态root下清空，未证明闲置指关节独立致因。|
|Q10|NO — 未发现评价实现错误；旧>3mm筛查与本轮全部正穿入的统计范围不同。|
|Q11|YES — 有依据继续研究现有root路径的接触与净空协调；尚未证明合格解，也无证据要求改正式mesh/rig。|
|Q12|ROOT_PATH_CONFLICT|

```text
E2_PENETRATION_SOURCE = LITTLE_DISTAL_SIDE / 8_VERTICES
FSHARP2_PENETRATION_SOURCE = MIDDLE_7 + RING_2 / DISTAL_SIDES
CONFLICT_TIME_RANGE = E2:0.720833–0.979167,1.220833–1.479167; F#2:0.716667–0.987500,1.216667–1.487500 (OBSERVED_SECONDS)
ROOT_COUNTERFACTUAL_RESULT = BOTH_KEY_PENETRATIONS_REMOVED
D2_CONTACT_TRADEOFF = PASS_2.969_MM → FAIL_7.689_MM
IDLE_FINGER_CONTRIBUTION = MIDDLE_RING_CLEARANCE_INSUFFICIENT_UNDER_CURRENT_ROOT / INDEPENDENT_CAUSE_UNPROVEN
HUMAN_VISIBLE_SEVERITY = GEOMETRY_ONLY_CONFLICT / HUMAN_PENDING
PRIMARY_CAUSE_CLASSIFICATION = ROOT_PATH_CONFLICT
NEXT_RECOMMENDED_ROUTE = ROOT_PATH_CONFLICT / HUMAN_DECISION_REQUIRED
NEW_ACTION_CANDIDATES = 0
HAND_BASELINES_UNCHANGED = YES
PIANO_BASELINE_UNCHANGED = YES
STOP — HUMAN REVIEW
```
