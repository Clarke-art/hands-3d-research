# RIGHT_HAND_MOTION_IMPLEMENTATION

2026-10-09 · HUMAN_VISIBLE_PRODUCT_QUALITY_FIRST · ONE NEW PERFORMANCE CANDIDATE ONLY

最终状态：FAIL_CLOSED；自然度/双手协调正式结论待Human。唯一新候选 `RIGHT_HAND_ARTICULATION_CONTACT_DESIGN_ONLY_R1.blend`，SHA256 `dcb80abadaf8c441254159038ed055d44c1e6b21d2ae8316b669ac72028385ee`。

## 最小必要改动

只修改本审计目录的非冻结运动适配，新文件 `articulation_common.py`、`right_motion.py`、`02_generate.py`。继续消费原performance_core FK/关节轴、teaching rig适配、static common皮肤预测/实际键面测量和bounded least_squares；没有重构求解器或增加骨骼。

通用事件阶段：原120ms靠近→20ms预备抬指+40ms落向触键；保持原35ms键下沉和70ms键回弹；原150ms额外回位→50ms。持键一直到原NOTE_OFF，不提前弹起，不改变原MIDI120BPM/时值/velocity。

抬指只将现有基部屈曲削减最多3°并按既有工程域裁剪；不放大全部关节。接触/压力端点按每指实际可奏面整段拟合，Bernstein系数由端点派生；所有重复音复用同一digit系数，无按A5、F♯5或绝对时间特殊分支。

共同掌根仅一条由所有事件生成的stance：60ms靠近，在相邻发声音符期间保持稳定，最后70ms回弹+50ms回位。上限XYZ±2/±3/−5..0mm、pitch−2..0.5°，绕批准语义wrist旋转，不是逐音符root修补。闲置指各三屈曲轴±4°以内、有界共用补偿，保留批准R1自然曲度参考。接触端点基部±16°/其它±12°邻域与原工程关节域相交，解除此前未经生理确认的±12°基部限制；没有修改任何静态姿态或Rig工程骨轴。

总59参数：五指接触/全键程端点40、共同XYZ/pitch4、五指闲置屈曲15。一个完整序列残差共同优化contact、skin、既有净空、运动连续性和姿态正则。拟合次数1，重启0；nfev=21，calls=1142，约933.3s。root实际幅值XYZ mm/pitch deg：[-0.9194159529965074, 2.486674247324791, -4.999999999999989, -0.9616594150509167]。成功收敛只说明数值求解终止，不取代后验几何/产品检查。

## 当前仍未解决的机制瓶颈

A5起音已经到位，但35ms后仍有约4.30mm分离。新小指full-down的MCP增量触及32°工程上界、DIP增量贴0下界，共同root Z幅值触及−5mm限值。`REMAINING_MOTION_BOTTLENECK.json`保留具体参数证据。当前一次共同stance+两端点压力曲线在既定自然度/范围域内仍未生成可靠持键追随；接触、净空用软残差共同折中，数值收敛没有接触可行性保证。

这支持本轮非冻结运动参数化/协调能力不足，不支持MIDI或指法输入错误。没有全局不可行性证明，不能断言冻结Rig必须改或所有现有运动系统根本不可用。本轮到此止损，不继续加局部root/IK/DIP补丁。

## 原输入与输出保护

独立重新解析原MIDI，第1–2小节全部18音符身份、时值、顺序、velocity逐项一致。右手10音符先在原事件上验证生成轨迹，再组合完全复制的上一轮左手8音符数组。左手29参数没有重拟合。

新blend直接继承上一轮唯一候选，仅替换右手design-only骨骼Action并添加外部掌根Action。左手与琴键Action payload不变；保存重开后左手实际几何差0.000000000mm。右手pad/FK误差0.000604mm，键世界变换误差0.000017mm。四批准静态core、手mesh/rest/weights/corrective/driver intrinsic与88键mesh均一致。

三视角使用上一轮摄像机原变换、同一源时间窗口0.4–3.1s；各162帧/60fps/2.7s，正常播放。原钢琴PCM逐字节相同，未变速、改谱或重新配乐，三个音视频完整解码通过。旧视频只作reference复制，不构成第二新候选。

## 验证与限制

必要检查含actual active-pad gap、有限8mm指腹邻域、运动白/黑键可奏面、汇总邻键穿入、工程范围与120Hz连续性。没有逐顶点forensic报告、隐藏相机或参数搜索。

代理同视角预检：G5/E5/D5与A5起音接触改善，但两次A5 full-down/HOLD仍可见指腹与下沉白键分离（最大skin gap约4.30mm，旧约10.99mm）。F♯5持键近贴合，没有确认明显悬空；其起音浅表穿入约1.47mm作为新增工程WARN。原速自然节奏尚不能由代理实时观看确认，Human仍需完整播放。没有第二轮优化。

浏览器自动化内核初始化失败，代理未声称完成1×带声实时浏览器观看；帧序列/同视角接触预检与可播放完整视频已交付，真实自然度由Human原速评审。

最终3633受保护文件哈希全部不变。无正式资产指针更新、正式产品批准、完整曲目制作或Web集成。完成后STOP — HUMAN REVIEW。
