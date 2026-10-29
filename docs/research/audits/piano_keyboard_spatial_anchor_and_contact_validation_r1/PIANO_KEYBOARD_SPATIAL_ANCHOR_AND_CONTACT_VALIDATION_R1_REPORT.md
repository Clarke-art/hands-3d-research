# PIANO_KEYBOARD_SPATIAL_ANCHOR_AND_CONTACT_VALIDATION_R1

**FINAL_STATUS = PIANO_KEYBOARD_SPATIAL_ANCHOR_BLOCKED**  
**STOP — HUMAN REVIEW**

已交付权威88键映射、统一时间轴、外部根候选、接触测量、验证blend和三个完整7秒视角。候选不是合格产品安装；不修改正式资产，不进入IK、生成、多曲目或音源阶段。

| 问题 | 结果 | 证据/边界 |
|---|---|---|
| Q1 | YES | 88键来自V1.1G Human accepted frozen Grand；C0批准复用文件字节一致。 |
| Q2 | YES | 21=A0，60=C4，69=A4，108=C8；88唯一键，52白/36黑，实际几何低→高方向递增。 |
| Q3 | YES | PERFORMANCE_TIMELINE_R1已建立；92相交音符、179窗口事件、421运动观测，同一时基。 |
| Q4 | AUTO_PREDICTED | RIGHT；本地Fingering目录，非Fingering_GT；不伪造置信度。 |
| Q5 | AUTO_PREDICTED | LEFT；同上。手侧标签亦为自动预测。 |
| Q6 | NO | RIGHT外部root候选已求出，但接触/碰撞失败，不能认定可信安装。 |
| Q7 | NO | LEFT外部root候选已求出，但接触/碰撞失败，不能认定可信安装。 |
| Q8 | NO | 完整7秒候选包含明显离键、穿键及姿态问题；代理可见检查不替代Human批准。 |
| Q9 | YES | 每个MIDI音符查唯一权威physical key，包括指法未知音符。 |
| Q10 | PARTIAL | 可测起音：R9/39、L4/26符合预锁定容差；多数失败，不构成接触验证。 |
| Q11 | PARTIAL | 全部用同一整手root；同时持音观测R2/38、L4/82全部满足容差。固定朝向下R1、L8个观测连宽松横向可行域都为空。 |
| Q12 | YES | 存在wrong-key alignment、floating、penetration；掌部/右腕有键体穿入筛查命中。没有>10mm/60Hz的root jump。 |
| Q13 | YES | 统一时间轴驱动继承的pivot/travel/profile；60Hz预览有1个极短音无持键采样，明确保留限制。 |
| Q14 | YES | 精确NOTE_ON/OFF、音高、力度、时间、初始held状态及PEDAL接口齐全；该源MIDI未发现踏板事件。 |
| Q15 | DEFERRED | LEFT快弯保留；已有接触失败，尚不能把根安装/标签/2.5D误差排除后单独归因于fast bend。 |
| Q16 | DEFERRED | RIGHT同上；未修改Action、做IK或调单指。 |
| Q17 | PIANO_KEYBOARD_SPATIAL_ANCHOR_BLOCKED | 本轮固定朝向+平滑XYZ候选不能满足可信接触安装；不是所有可能静态朝向均不可能的证明。 |

## 权威与单位

KEYBOARD_AUTHORITY = `V1_1G_HUMAN_ACCEPTED_FROZEN_GRAND_88_KEY_PERFORMANCE_LAYER / V1_2C0_HUMAN_APPROVED_EQUIVALENT`

KEYBOARD_SOURCE_SHA256 = `712b1d697fab438b1ea575712e848640992a0313179448efb929d33c9891710a`

Runtime SHA256 = `9070f8ac8016e10cb5a39803e13bdc2409a67f94efac5641213020f2136b4a53`

Source master SHA256 = `344089efefbb8c1388849d8c88f5ba6ac164b82119bbb1031b1d8ba297bc1251`

从V1_1G_ACCEPTED_BASELINE_LOCK → 完整candidate manifest → C0 Human approval追溯；运行获批Three构造器生成几何，只替换import解析路径。保留正式白键后部notch，未以整块box覆盖黑键区域。读取初始upright指针为multi-note motion FAIL，明确排除；运行期间该非冻结指针更新为jack/butt只读接触审计，仍不属于获批88键权威。

坐标由MIDI递增中心、REAR pivot、实际top面及正向按压验证推导：native低→高+X、前→后−Z、向下−Y；canonical为X低→高、Y前→后、Z向上，右手系。原点是C4正面键沿中点、白键静止顶面。单位继承0.53255794 m/native unit；白键宽约23.089mm。这个尺度是既有产品的等效尺度，不能升级为制造商公制实测。

## 时间轴与指法

原始SMF解析tempo/running status/track/channel，并将全部192个音符逐项对照TSV。窗口事件保持精确秒时，不吸附60Hz；含初始held音符及窗口末尾仍按住的音符，不伪造NOTE_OFF。hand、key、future audio都引用这一个timeline。

92个相交音符中：RIGHT39，LEFT28，UNKNOWN25。LEFT有2个carry-in音符，因此窗口内可测NOTE_ON为26；RIGHT为39。UNKNOWN不猜手指，不进入接触测量，但仍驱动对应键。

Fingering来源为AUTO_PREDICTED，finger_confidence=null；不把总体准确率转成逐事件置信度。源文档明确自动阶段未执行人工消歧：[PianoVAM dataset README](https://huggingface.co/datasets/PianoVAM/PianoVAM_v1/blob/main/README.md)。

当前motion/MIDI/fingering/派生timeline及媒体均为PianoVAM内部非商业验证；CC BY-NC-SA 4.0。作者：Kim, Yonghyun; Park, Junhyung; Bae, Joonhyung; Kim, Kirak; Kwon, Taegyun; Lerch, Alexander; Nam, Juhan，ISMIR2025。未提取源视频音频，也未将任何曲目提升为商业产品。未来音源/乐曲必须使用拥有相应权利的来源。

## 事前锁定和空间模型

CONTACT_VERTICAL_TOLERANCE_MM=3；CONTACT_HORIZONTAL_TOLERANCE_MM=2；正确键还必须处于真实playable region内部。阈值文件先于04_hands提取和05_solve求解写出，并用PRE_RESULT_POLICY_LOCK哈希锁定。没有看结果调容差或逐音调平滑。

每指从正式canonical表面、TIP语义、掌侧末节区域选择固定surface vertex，再变换为distal frame local pad point；不使用bone head作为接触点。10个audit Empty骨父级绑定，不新增骨骼。标记与对应蒙皮vertex最大漂移R0.320mm、L0.133mm，有限代理误差明确保留。

静态朝向来自正式wrist rest anatomical frame；scale=1。只解XYZ整手平移，目标是实际键面上的固定白键front+25mm/黑键front+15mm点。全部assigned held notes等权，二阶时间差分正则lambda=(0.080×60)^4，421观测一次全局求解；内部Action不变，动态yaw/6DOF关闭。所有旧DISPLAY_ONLY review offsets完全未导入。

这些depth点是事前声明的接触假设，不是测得的真实落点。未知标签、单音平移自由度和source非公制2.5D均限制定位可信度。被用于拟合的预测标签不能再次充当独立ground truth。

## 接触结果

| 指标 | RIGHT | LEFT |
|---|---:|---:|
| 可测起音 | 39 | 26 |
| 符合容差的起音 | 9 | 4 |
| 落入正确键区域 | 23 | 9 |
| 最大绝对vertical gap / mm | 17.556 | 14.344 |
| 最大horizontal error / mm | 21.735 | 26.231 |
| 起音穿入目标键 | 11 | 5 |
| 邻键近接候选 | 10 | 9 |
| 同时持音观测 | 38 | 82 |
| 同时全部符合容差 | 2 | 4 |
| 横向平移可行域为空 | 1 | 8 |
| 最大root step / mm每60Hz | 5.386 | 5.480 |
| 掌部碰撞观测筛查 | 156 | 214 |
| 腕部碰撞观测筛查 | 4 | 0 |

多音统计是同一手同时held的观测，包含重叠/连奏，并非全部都是同tick的乐谱和弦。RIGHT有1个同指多音预测冲突，不暗中改finger。横向可行域测试放宽到整键包围宽度再加±2mm；即使如此仍为空的观测，固定朝向下任意XYZ平移都无法解决。该结论依赖预测指法和既定静态朝向，不能推断别的朝向或真实指法也必定不可能。

碰撞筛查使用实际runtime各矩形键体的顶点包容测试，>3mm低于顶面且位于键体内才计数；它不是完整triangle碰撞证明。NO root jump只表示不超过预定10mm/60Hz，不能替代自然性判断。

## 文件与复核

- [review.html](../../../../examples/historical/audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/review.html)：三个7秒视角和Q1–Q17。
- [validation candidate blend](../../../artifacts/f099d621a4769b77602e.md)：88独立键、正式双手、两条原Action、外部根、10个虚拟pad、三台camera。
- [动作身份](../../../../examples/historical/audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/ACTION_IDENTITY_R1.json)：保存并重新打开后payload MATCH；网格/权重/rest/driver/corrective内在数据MATCH；所有421观测验证。
- [资产保护](../../../../examples/historical/audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/FINAL_ASSET_PROTECTION_R1.json)：89个初始跟踪文件中88个不变；唯一变化为非冻结upright阶段指针，另行记录；所有正式冻结资产不变，另验证两份已批准motion源SHA；R1 fallback也不变。
- [完整视频验证](../../../../examples/historical/audits/piano_keyboard_spatial_anchor_and_contact_validation_r1/VIDEO_VERIFICATION_R1.json)：每段210帧@30fps，7.000秒，0音轨。
- FULL_REVIEW_SECOND_1–7.jpg：覆盖全部210输出帧的连续教学视角联系表。

视频键下沉复用批准runtime的0.42 easing和0.00005 snap，在固定60Hz审计clock运行。单个极短音n0183在60Hz无held采样，timeline精确事件仍在，视频不宣称亚帧响应验证。未来音频消费者可以直接使用精确事件，不应依赖视频采样。

未修fast bend；尚无隔离证据证明哪次接触失败由fast bend本身造成，故左右均PRESENT / DEFERRED。first-web不重开。

**最终范围：本轮候选受阻；不能从此自动进入contact IK、MIDI-to-hand生成、多曲目播放器、音源或正式产品集成。等待Human决策。**

## 并行指针变化与视觉复核

CONCURRENT_NON_FROZEN_POINTER_DRIFT_R1.json保留before/after SHA和新指针内容。本轮脚本从未写入Piano路径；未把非冻结指针漂移掩盖成all_unchanged。正式键盘及accepted Grand/Upright冻结文件全部不变。

代理检查覆盖FULL_REVIEW_SECOND_1–7的全部210教学视角输出帧，并检查普通接触近景时间条及大图；观察到持续离键、压入/遮没指尖以及右手明显斜向姿态，不能给出自然性PASS。没有将逐帧联系表检查声称为Human实时播放批准。近景取景按421观测联合包围范围调整，未改模型、动作或测量。
