# PIANO_HAND_STATIC_TO_DYNAMIC_TRANSITION_R1_REPORT

2026-10-09 · DESIGN_ONLY · HUMAN_VISIBLE_PRODUCT_QUALITY_FIRST

**FINAL_STATUS = STATIC_TO_DYNAMIC_TRANSITION_FAIL_CLOSED**。这是 Agent 候选提交判断；动态 Human 批准仍为 false。

## 四姿态身份与唯一方案

R2 静态候选 SHA `18359b1c2c6e8abaa1a4444f342e7672a1f1fda35d96cc95146bc8d1161b551c`；唯一动态候选 SHA `664a0702637e7c3d7aef6b4ba260d8b464f87c9704aa2d4b56b8492d01492284`。四个原静态场景完整保留且保存重开内部状态完全一致。当前用户明确的静态 Human 批准覆盖旧报告 HUMAN_PENDING，只用于动作参考，不 Promotion。

事前政策与 core/solver SHA 先锁后算。每手一次确定初始化，全段有界三次 Bernstein 关节轨迹；按原琴键下沉比例跟踪注册触点；准备/恢复使用 C2 quintic。没有逐帧独立 IK、事后 smoothing、restart、sweep 或根据结果改参数。两手共同构成一个候选，未拼完整演奏。

左手三个原事件 n01/n02/n04：0.700–0.950、0.950–1.200、1.200–1.450 秒。右手 n05 F#5：1.325–1.450 秒。原35ms琴键下沉、70ms回弹不变。视频首帧使用原时间窗起点，音乐事件没有重排或变速。
左手 NOTE_OFF 与后一指 NOTE_ON 同时发生，上一指仍需70ms跟随回弹。因此动态整手在第二起音时不会假称与静态 L2 全部骨骼完全相等；源全手 anchor、当前主动指静止键面 contact anchor、三闲置指和共享 root 原样继承，动态只改变正在释放/按键的两指。它们没有重新设计。
共享 root 保持已批准值，变化0mm/0°。没有为每音搬掌；本候选选择稳定掌位，未伪造腕部随动。左三闲置指与右四闲置指保持批准曲度，右中指 PIP/DIP 有界正向曲度。左工程限位在contact anchor保留，但按键曲线control points预先要求主动饱和关节向内至少0.5°，实测近限位持续时间独立报告。
## 实际运动键面与连续路径
|手|动态接触|最大固定pad/皮肤gap|120Hz关节速度/加速度|max单步|邻键/掌腕筛查|
|---|---|---|---|---|---|
|左|FAIL_CONTACT_SCREEN|7.672/7.689mm|610.30°/s / 43253.48°/s²|5.086°|PASS_FINITE_SCREEN|
|右|PASS_CONTACT_SCREEN|0.710/0.710mm|459.01°/s / 41523.39°/s²|3.825°|PASS_FINITE_SCREEN|
本候选的明确阻断：左手小指两次D2按键起音端点合格，但下沉/持键/回弹阶段固定pad最高7.672mm、实际皮肤最高7.689mm，正常近景可见手指未持续跟随键面，属于已批准接触在动态阶段的重大可见回退。左拇指D3全过程接触通过（最大约1.000mm）；右中指F#5全过程接触通过（最大约0.710mm）。不能用右手成功抵消左手失败。
左小指近限位持续0.2917s、右中指近限位持续0.1167s，均超过事前0.05s门槛。左拇指0.025s通过。速度/加速度和硬角度域通过，只说明数值有界连续；DIP/PIP等持续贴近工程边界未通过。没有自动扩大关节范围、速度或缩短已锁定准备时间。
POSTURE_ANCHOR_CONFLICT = NO_REDESIGN; 唯一固定掌位方案失败，不构成静态姿态被推翻，也不能证明其它获授权运动方案或骨架不可达。现有失败不获 Promotion，等待Human裁决。
实现错误修复：第一次保存的琴键父平移未正确抵消，已只读记录于 CONFIRMED_CODE_ERROR_R1.json；修复为显式逆pivot局部变换。第一次属性数组复制错误也已修复。动作NPZ/事前政策/优化control points完全不变，没有重跑solver或生成第二套轨迹。修复后实际运动键世界顶点逐120Hz与原规则最大差小于0.00002mm；旧错误画面已替换，所有最终素材绑定修复后唯一blend SHA。
所有 CONTACT/KEY_PRESS/HOLD/RELEASE 样点均按保存重开的实际当前key角度，把pad与皮肤点逆变换到真实可奏面；不是按静止键面代替。容差≤3mm vertical、≤2mm horizontal且严格在可奏面。全3300顶点/全部88键在120Hz检查>3mm键体穿入与错键pad；这仍是有限筛查，不是hidden triangle forensic。
数值连续不等于自然。预审读取完整60fps三视角所有帧及关键触键帧，详细观察记录见 HUMAN_VISIBLE_PRECHECK_R1.json；最终自然度由Human决定。
- 左三闲置指保留批准曲度、间距和整体形态，完整路径未见新的钩爪或反关节；没有给它们添加假home-key运动。
- 共享批准掌腕在全部画面稳定，未为每音搬掌、抬高或扭转；稳定性通过，不声称真实肌肉放松已测。
- D2两次起音contact端点正确，但下沉/持键时小指没有有效跟随琴键，近景可见悬空；最大皮肤间隙7.689mm，不能称自然交替演奏成功。
- 拇指D3下压/持键/回弹的实际接触通过，release/recovery连续；这不能抵消小指失败。
- 小指工程近限位持续0.2917s，超过事前0.05s。限位失败保留，没有扩大域或重算另一候选。
- 正常顶视/侧斜/近景中五指准备保持批准形态；中指在原F#5事件接近、下压、持键、跟随回弹后恢复准备，未见IK分支切换或反折。
- F#5下沉/持键/回弹固定pad与实际皮肤接触均通过，最大gap约0.710mm；实际运动键世界顶点与冻结规则一致。
- 食指D#5与无名指G#5邻键净空贯穿整段，未见新的吞入黑键或错键，完整顶点筛查也无命中。
- PIP/DIP工程增量靠近下边界持续0.1167s，超过事前0.05s，故右手仅接触/正常画面预审部分通过，不能宣布完整动态合格。增量0是已有曲度rest，并非把实际关节反折。
## 交付与资产保护
[review.html](../../../../examples/historical/audits/piano_hand_static_to_dynamic_transition_r1/review.html) 提供两个完整同步三视角视频，原速/0.5×/0.25×、暂停和逐帧控制。源材质、原相机方向/orthographic范围继承，渲染适配三视角布局。少量对照为静态对动态，以及下沉/持键/回弹真实触键证据。视频静音；既有合法采样音轨与音源接口仅保护复用为已验证输入，本轮未开发或重跑音频引擎。
最终重新核对 710 个正式/继承文件；变化 0。三份手 SHA、Grand权威、MIDI、指法、声音接口、production pointers、历史静态候选和证据均保持。候选新 Action 只保存在本 DESIGN_ONLY audit。
## Q1–Q13
|问题|答案|
|---|---|
|1. 是否精确继承四个 Human-approved 静态姿态|YES|
|2. 左手 L1→L2→L1 连续动作是否生成|YES|
|3. 左手中间三指是否保持自然协调|YES|
|4. 左手拇指/小指动态持键接触是否合理|NO|
|5. 左手掌腕是否连续自然|YES|
|6. 右手 R1→R2→R1 连续动作是否生成|YES|
|7. 中指是否跟随 F#5 下沉、持键和释放|YES|
|8. D#5/G#5 邻键干扰是否保持解决|YES|
|9. 是否出现新明显悬浮、穿键、钩爪、反关节或掌腕异常|YES|
|10. 关节/root 是否连续且 Human-visible 自然|NO|
|11. 原 MIDI、琴键事件和声音接口是否不变|YES|
|12. 两段微动作是否达到提交 Human 审核的产品质量|NO|
|13. 最终状态|STATIC_TO_DYNAMIC_TRANSITION_FAIL_CLOSED|
```text
LEFT_TRANSITION = GENERATED / FAIL_DYNAMIC_CONTACT
LEFT_IDLE_FINGERS = PASS_CANDIDATE
LEFT_DYNAMIC_CONTACT = FAIL_CONTACT_SCREEN
LEFT_WRIST_MOTION = CONSTANT_APPROVED_ROOT / PASS_PRECHECK
RIGHT_TRANSITION = GENERATED / CONTACT_PASS / LIMIT_DWELL_FAIL
RIGHT_FSHARP_CONTACT = PASS_CONTACT_SCREEN
RIGHT_NEIGHBOR_CLEARANCE = PASS_FINITE_SCREEN
JOINT_CONTINUITY = PASS_NUMERIC / LIMIT_DWELL_FAIL
ROOT_CONTINUITY = PASS / CONSTANT_SHARED_ROOT
HUMAN_VISIBLE_NATURALNESS = NOT_READY / HUMAN_PENDING
FINAL_STATUS = STATIC_TO_DYNAMIC_TRANSITION_FAIL_CLOSED
HAND_BASELINES_UNCHANGED = YES
PIANO_BASELINE_UNCHANGED = YES
STOP — HUMAN REVIEW
```
未自动进入完整《Musette》演奏动作生成。
