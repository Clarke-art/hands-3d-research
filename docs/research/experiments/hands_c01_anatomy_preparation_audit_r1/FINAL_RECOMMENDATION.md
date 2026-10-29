# 最终建议 — ANATOMY_STATIC_CANDIDATE_PASS_HUMAN_PENDING

**C — 解剖/手型约束与E5准备策略都存在问题，需要联合改进。** 直接证据支持ANATOMY_CAUSE_IDENTIFIED；在不改冻结Rig下已得到满足真实几何及明确参考关节约束的B2静态候选，Human自然度仍待审。全部DESIGN_PROVISIONAL。

原A继续保持：

- S1_NUMERICAL_GEOMETRY = PASS
- S1_HUMAN_ANATOMICAL_VISUAL = FAIL
- DYNAMIC_BRIDGE_AUTHORIZATION = NOT_GRANTED

## 查清的原因

实际中指MCP spread接近-25°工程边界，掌面heading26.17°；批准参考约8–9°。PIP/DIP未发现额外侧向控制，异常主要为MCP侧摆及失去参考曲率分布。canonical spread轴还与rest长轴斜交，不是纯临床侧摆。

只恢复MCP spread时旧E5越界变为17.96mm，而G4接触/零交叉保持，证明当前掌位与旧精确提前目标不协调。0.393571s的准备窗口不能推导必须提前精确悬停。共同骨架/皮肤已能在保守参考族内求得安全S1，没有直接证据支持现在修改冻结Rig。

## 实际B2

- G4真实指腹接触距离0mm，目标侵入0.00327214mm。
- 非目标/非指腹侵入0，五指非邻接皮肤交叉0。
- 中指MCP spread -6.73202°、heading8.23417°；中指/无名指精确间隙4.93699261mm。
- 实际骨角符合批准R1/R2局部参考族；Z与A相同，原键Action、时钟、Rig和网格不变。
- 两次优化均11迭代收敛，累计25.984s；B1的约0.20mm残留未隐藏，B2将其消除。保存后重读一致。

B2旧E5精确悬停合同仍FAIL（越界19.96865mm）；通过的是本轮分阶段早期准备定义。不能把它追认为原静态合同PASS，也不能证明下一音能及时触键。整体自然度、拇指形态和教学习惯由Human审查，不能以数值替代。

## 下一步技术决策

先由Human审查四张同视角A/B图和保守手型族。若认可，应把阶段依赖的手型族、MCP flex/spread协调和接触/全网格门禁纳入规划接口；不要继续用均匀独立角界和“pad精确提前到位”作为自然度替代。人体最大ROM/舒适主动角域对当前Rig的精确映射仍证据不足，需明确校准，不以论文最大角作默认目标。

登记FINGERING_MOTION_FEEDBACK_REQUIRED：未来指法候选的运动成本应包含参考手型偏离、掌位移动、跨指/穿指阶段、剩余时间和失败可行性反馈。C01固定G4(1)→E5(3)→C5(1)→D5(2)→E5(3)→F♯5(4)→G5(5)未改；没有证据宣称该人类指法绝对不可行。G4→E5大跨度及随后的回移需要整手协调，当前静态研究只识别规划接口风险。

前臂/腕绝对解剖角、全域手型族和连续可达性尚未验证；即使B视觉获认可，也仍需单独的动态授权。本轮不自动执行任何后续运动实验。

[RIG_JOINT_ANATOMY_AUDIT.md](../../../artifacts/f9440a672da5b7949de5.md)、[S1_UNNATURAL_POSE_ROOT_CAUSE.md](../../../artifacts/7925b338f97e0f72a399.md)、[E5_PREPARATION_CONSTRAINT_REVIEW.md](../../../artifacts/c0bfe6da86cd33eff897.md)、[ANATOMY_CONSTRAINT_PROPOSAL.json](../../../artifacts/3789edc1ffa094c3b98b.md)、[STATIC_AB_COMPARISON.md](../../../artifacts/0cb311e9a1e0c8a4ee64.md)、[HUMAN_VISUAL_REVIEW.md](../../../artifacts/b242333f692c0aae5fca.md)。

201项保护哈希不变，四个批准姿态、冻结Hands/Piano、C01/MIDI及全部旧失败记录只读。4张720p静帧、独立诊断Blend和完整实际数值证据已保存。

**STOP — HUMAN REVIEW。**

