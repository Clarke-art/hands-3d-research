# R2 最小时空走廊设计

DESIGN_PROVISIONAL — STOP — HUMAN REVIEW

高层自动输出阶段窗口、整指实体分离请求、合法目标区域子集与释放后避让，由低层联合接触IK寻找自由控制状态。只固定真实B2；所有其他节点可调。没有把上轮4.349mm安全状态提前后接受，也没有把初始化曲线当求解结果。

时序来源：原当前OFF/下一ON窗口0.393571s；原PRESS时长35.000000ms。参考手位的根平移、根角、拇指/映射关节、lambda/alpha运动成本取原门禁最大下界，再乘1.5作为所选C1初始化的保守分配启发。二维LP最小化清障完成时刻，同时预留参考下降时间；这是参考条件估计，不能证明所有Rig路径时间可行或不可行。

自动得到清障完成/下降开始2.703912497675s，比上轮风险静态状态时刻2.869521666667s提前约165.609ms；下降窗口217.513502ms，所选参考下降预留173.235486ms。R2计划不强制实际IK使用该旧边界参考。准备、抬指/维持已抬状态和上方横移可重叠；最小示例没有凭空制造休止。

|阶段|窗口秒|进入条件|退出条件（未经IK验证）|
|---|---|---|---|
|PREPARE|2.527855000000–2.703912497675|Actual known start and all active contacts|Target hand region compatible with raised digit|
|LIFT_OR_MAINTAIN_ALREADY_RAISED|2.527855000000–2.703912497675|Source free preparing digit only|Whole preparing digit satisfies upper clearance region; no early key Action|
|UPPER_CLEARANCE_TRAVERSE|2.527855000000–2.703912497675|Original held contacts remain hard|Reached a position admitting the selected descending corridor|
|DESCEND|2.703912497675–2.921426000000|Clearance transition occurs while all held contacts stay valid|Original target contact set met at exact MIDI ON|
|PRESS_AND_RELEASE_ESCAPE|2.921426000000–2.956426000000|Atomic original OFF/ON; closed boundary contact compatibility|Follow source target descent and avoid recovering released key|

空间约束使用原实体边界和整指三角面：每个面须由上方或指定外侧半空间分离，请求余量0.5mm。该走廊是额外的保守规划请求，未替换原0.25mm接受门禁。下降阶段前方候选与右侧候选使用不同半空间组合及E5合法触键子集；G4在原OFF前始终为硬接触，OFF后按源恢复并要求相关释放皮肤在首个完整E5下行结束时避让。

|候选|目标pad X mm|目标pad Y mm|下降/释放策略|
|---|---:|---:|---|
|candidate_front|203.921790–215.446315|0.020000–39.076180|FRONT_DESCENT_AND_FRONT_RELEASE|
|candidate_right|220.655163–226.970839|0.020000–49.401377|RIGHT_DESCENT_AND_FRONT_RELEASE|

前方子集还根据未来R09键中心在当前目标左/右侧选近侧区域，实际利用后续音符信息；它只是几何启发，没有计算完整下一音的手部可达代价。D#5障碍由R1真实失败见证提供，尚未实现任意MIDI的自动扫掠障碍发现。参考族/公共姿态库仍为C01专用初始化能力，必须披露。

HandMotionIntent以阶段序列方式复用，原实例字段保留，阶段内增加区域/截止等嵌套数据。接口审计发现第一版从R1复制的active_contact_modes未随phase更新；低层原方程直接从源时钟读接触，物理合同未被更改，但序列化层失配，第一候选不授予接口合格。原输入保存candidate_front_PLAN_EXECUTED.json。第二输入按源半开区间更新状态并校验，另声明事件左闭接触相容；没有重新优化第一候选。

修正编译器实际读取阶段意图的窗口、障碍、margin、下降策略与目标子集，不以root摘要绕开接口语义。证据：R2_INTENT_SEMANTIC_AUDIT.json、candidate_right_PLAN_COMPILED.json。第二输入通过字段/时序检查仍不等于走廊可达。

失败反馈分类：EMPTY_TARGET_SET、SELECTED_REFERENCE_TIME_WINDOW_FAILED、SERIALIZED_CONTACT_MODE_MISMATCH、NONSMOOTH_DERIVATIVE_REJECTED、AUTHORIZED_DOMAIN_VIOLATION、HOLD_CONTACT_LOST、WRONG_KEY_COLLISION、TARGET_CONTACT_LOST。当前尚缺可达走廊连边证明；输出只是有几何依据的受限计划。
