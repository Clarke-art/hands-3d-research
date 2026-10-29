# LEFT_OCTAVE_ROOT_FINGER_COORDINATED_CLEARANCE_R1_REPORT
2026-10-09 · DESIGN_ONLY · HUMAN_VISIBLE_PRODUCT_QUALITY_FIRST
**FINAL_STATUS = COORDINATED_CLEARANCE_FAIL_CLOSED**。一个完整共享 root＋主动指＋闲置指协调候选；Human approval=false。
## 本轮政策与联合规划
继承 root-path conflict / supported、contact-clearance tradeoff / confirmed、left dynamic not-approved。没有重新求解或覆盖历史证据。先锁定唯一政策及脚本 SHA；一个 29 参数联合运动问题，覆盖 D2→D3→D2 全段原时间轴，没有 root 后补或逐指局部补丁。
政策 SHA `f6b56554716e0b34c27ad761cc8bd4833729530f0bc24b891f8c2e3eedd250ff`。XYZ 偏移范围 x±2、y[-5,0]、z[-3.5,0]mm；腕部仅继承 world-X pitch[-2,0]°，yaw/roll不变。x自由度是本轮求解前声明的有限工程假设：已有E2侧面浅退出距离支持测试侧向避让，同时主动指在真实键面中补偿。未根据结果扩域。小指/拇指继承RSSＦ工程域及锚点±12°、压力上界0.5°余量；闲置三指分别仅允许批准曲度±4°，base spread保持。所有范围不是人体生理极限。
共享root响应与三闲置指变化使用同一原D2 quintic键程因子；同样参数用于两次D2，整段一个统一外部root。小指与拇指的原Bernstein压力曲线分别加入联合求解的四维偏移；拇指继承到L1准备姿态的八项凸组合参数也在同一残差中求解。未创建每音符root，未每帧IK，未事后smoothing。
唯一有效求解 nfev=33、residual calls=723、cost=87292.321130。最终参数完整见 ROOT_FINGER_COORDINATION_R1.json；求解结束不代替质量判断。
实现bug修复：近零参数的相对差分被Blender float32吞掉，root侧移、小指和三闲置指几何导数为零。只读DERIVATIVE_PRECISION_CHECK_R1.json实际复现。首次启动在结果/blend生成前中止；仅改为有界绝对差分，保持原政策SHA、范围、目标、权重、seed与max_nfev。修复启动不是第二候选，未比较选优。完整记录见IMPLEMENTATION_REPAIR_R1.json。
## 接触与自然释放
主动接触仅要求NOTE_ON≤t<NOTE_OFF，包含NOTE_ON、KEY_PRESS、HOLD。NOTE_OFF起进入NATURAL_RELEASE_PHASE；没有要求70ms回弹全程贴键。释放仍检验几何、空间关系与动作连续性。没有延长持键或修改事件。原35ms下沉、70ms回弹、tempo/velocity/5-1分配全部保持。
固定pad与实际skin pad分别对真实移动可奏面检查，3mm垂直/2mm水平容差继承，并严格处于实际可奏区。动态触点可在原接触点附近x±2/y±5mm有限迁移，窗口随键程展开，静态批准接触点不变。
|事件|最大fixed gap mm|最大skin gap mm|起音/下沉/持键|
|---|---:|---:|---|
|n01 / D2小指|3.524178|3.541024|FAIL|
|n02 / D3拇指|4.129395|4.129392|FAIL|
|n04 / D2小指|3.524178|3.541024|FAIL|
实现bug修复补充：第一次差分修复后的输出使用了未激活静态场景的单位root矩阵，丢失原生绑定。首帧与来源正确矩阵最大元素差1.980873823，画面手部离开视野，故无效且不用于候选选优。修复改为已求值的来源动态场景frame1 root，并在求解前及保存重开时断言与来源矩阵相同。两个无效实现启动完整记录于IMPLEMENTATION_REPAIR_R1.json；只保留一份最终候选路径，政策/seed/范围/目标/权重/max_nfev不变，未生成第二套运动方案。
## 净空与连续性
保存后重开，在原120Hz样点和240Hz网格及原阶段边界上测量3300个实际evaluated顶点、全部88键。保留>3mm筛查门槛，同时独立记录E2/F♯2所有正深度穿入。竖向深度与最短退出距离独立报告；不能直接以竖向深度推断肉眼严重程度。
|键|状态|命中唯一顶点|最大竖向深度mm|最短退出距离最大值mm|
|---|---|---:|---:|---:|
|E2|NO_SAMPLED_VERTEX_PENETRATION|0|0.000000|0.000000|
位置来源：无命中；持续区间：`[]`。原E2约3.083mm/8顶点，F♯2约3.406mm/9顶点；原240Hz诊断继承，不重新生成。
|F#2|NO_SAMPLED_VERTEX_PENETRATION|0|0.000000|0.000000|
位置来源：无命中；持续区间：`[]`。原E2约3.083mm/8顶点，F♯2约3.406mm/9顶点；原240Hz诊断继承，不重新生成。
全88键>3mm命中记录0；其他键深命中：无；错误pad接触0；掌部最小投影gap=1.001096mm。有限顶点/矩形键体检查不等于完整三角相交认证。
连续性 `PASS`；关节最大速度742.402°/s、加速度70197.749°/s²；root最大速度98.528mm/s、加速度8063.823mm/s²，pitch速度90.111°/s。idle最大相对批准变化4.000000°。全部实际约束结果见MOTION_CONTINUITY_R1.json。
主动指near-bound记录：`[{"note_id": "n01", "longest_required_near_bound_sec": 0.25, "joints_near_bound_any": [true, false, true, true], "measurement_not_physiology_or_sole_rejection": true}, {"note_id": "n02", "longest_required_near_bound_sec": 0.016666666666666666, "joints_near_bound_any": [false, false, true, false], "measurement_not_physiology_or_sole_rejection": true}, {"note_id": "n04", "longest_required_near_bound_sec": 0.25, "joints_near_bound_any": [true, false, true, true], "measurement_not_physiology_or_sole_rejection": true}]`。近边界不自动证明生理紧张，也不替代可见自然度。
## Human-visible 审核
完整84帧三视角及同相机关键阶段预审：三闲置指有不同程度的小幅伸展，中指变化最大4°；仍保持曲度和既有间距，未见统一伸直或新钩爪，最终自然度HUMAN_PENDING。
掌腕以约2mm横移、0.466mm下降和1.878°world-X俯仰协调随动；未确认每次NOTE_ON定位跳跃、突发抬指或反关节。数值连续性PASS不等于Human批准。
正常近景未见E2小指侧面或F♯2中指/无名指不自然插入；240Hz全段实际顶点筛查两键正穿入均0、全88键>3mm命中0。没有把它包装为穷尽三角碰撞认证。
D3起音0.950s侧斜对照中指腹间隙比上一轮增大，键开始下沉时接触仍不足；max skin gap4.129mm，HOLD稍后恢复PASS。这是局部可见悬空间隙与主动接触时序回退。
两次D2 full-down/HOLD skin gap3.541mm，高于3mm门槛并劣于前轮2.969mm。整体产品质量未明显优于上一轮，不提交通过资格。
小指DIP在两次完整0.250s required-contact区间持续接近0°工程下界；MCP/spread在NOTE_ON也接近上界，仍有工程边界依赖。没有声称人体生理极限冲突，也不将此作为唯一失败理由。
释放及恢复在连续画面中未确认明显弹跳或反关节；按NATURAL_RELEASE_PHASE检查，不要求键回弹全程指腹粘附。
最终按主动接触回退FAIL_CLOSED，停止追加运动候选；COORDINATED_MOTION_ARCHITECTURE_REASSESSMENT_REQUIRED。未确认新增大面积穿模或严重手型畸形。
[review.html](../../../../examples/historical/audits/left_octave_root_finger_coordinated_clearance_r1/review.html) 提供完整三视角候选、上一轮失败版和本轮同相机同时间轴同步对照，1×/0.5×/0.25×速度、逐帧和原MIDI阶段跳转。两个新视频均84帧、60fps、1.4s，完整覆盖0.400–1.800s微片段（末帧1.783333s，数值测量包含1.800s端点）。静音，未制作新音频。没有渲染右手或全曲。证据只交付两张必要合成图，不只选最好单帧。
## 静态及正式资产保护
四个原Human-approved静态场景重开core身份与继承SHA逐一相同。左手正式mesh/rest/weights/corrective、first-web及掌面体积身份相同；右手root/Action/几何、键体顶点/Action、审核相机与来源相同。3039份冻结及继承文件变化0。三份正式手SHA、Grand冻结权威、原MIDI/Performance Timeline/琴键规则/音频接口及production pointers不变。
## Q1–Q13
|编号|问题|答案|
|---|---|---|
|Q1|是否生成唯一 root + finger 协调动态候选|YES|
|Q2|小指 D2 两次持键接触 PASS|NO|
|Q3|拇指 D3 接触 PASS|NO|
|Q4|E2 小指侧面穿入解决|YES|
|Q5|F♯2 中指/无名指穿入解决|YES|
|Q6|中间三指自然协调|HUMAN_PENDING|
|Q7|掌腕连续自然|HUMAN_PENDING|
|Q8|新增明显穿键/悬空/钩爪/反关节|YES|
|Q9|主动指明显工程限位冲突|YES|
|Q10|已批准静态 L1/L2 保持|YES|
|Q11|整体可见质量明显优于上一轮|NO|
|Q12|有证据要求修改正式 mesh/rig|NO|
|Q13|最终状态|COORDINATED_CLEARANCE_FAIL_CLOSED|

```text
D2_LITTLE_CONTACT = FAIL
D3_THUMB_CONTACT = FAIL
E2_CLEARANCE = NO_SAMPLED_VERTEX_PENETRATION
FSHARP2_CLEARANCE = NO_SAMPLED_VERTEX_PENETRATION
IDLE_FINGER_NATURALNESS = BOUNDED_DIFFERENTIATED_CURVES / HUMAN_PENDING
ROOT_FOLLOW_THROUGH = CONTINUOUS_NO_OBVIOUS_JUMP / HUMAN_PENDING
JOINT_CONTINUITY = PASS
STATIC_ANCHOR_IDENTITY = UNCHANGED
HUMAN_VISIBLE_RESULT = NEIGHBOR_CLEARANCE_IMPROVED_BUT_ACTIVE_CONTACT_REGRESSED / NOT_APPROVED
FINAL_STATUS = COORDINATED_CLEARANCE_FAIL_CLOSED
HAND_BASELINES_UNCHANGED = YES
PIANO_BASELINE_UNCHANGED = YES
STOP — HUMAN REVIEW
```
唯一候选未满足全部门槛，停止继续优化。COORDINATED_MOTION_ARCHITECTURE_REASSESSMENT_REQUIRED；不追加候选。
