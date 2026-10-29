# 最终判断

**路线A：联合节点及其局部诊断连接通过，保留时间耦合接口。** 全部结果为DESIGN_PROVISIONAL。

- 范围：2.936009333333 → 2.938092666667s，共2.083333ms。3个节点均可调整，无固定外部锚点。有效接触始终为同一PRESS，旧键RELEASE不加持键要求。
- 主要求解：36变量、963不等式（接触为双侧容差带）、10928个Jacobian结构非零元；39次IPOPT迭代后Maximum_WallTime_Exceeded，违规0.703679，失败保留。
- 唯一修正：共同已有姿态的解析随键初值，原硬约束及目标不变。IPOPT1次迭代后可行性优先回调停止，状态User_Requested_Stop；不是目标完全收敛。最终联合数值违规0。
- 3个节点真实Blender接触、0.25mm侵入、全88键、自交、自然参考族、关节轴和域全部通过。两段实际腕速约374.322、374.136mm/s，原500mm/s门禁通过，所有原授权控制/关节变化界通过。
- 局部自适应补采样17点全部通过，最大采样腕速374.450683mm/s；最大目标侵入0.004927870mm，错误区域侵入0、非相邻指面交叉0。标记LOCAL_ADJACENCY_SAMPLED_PASS_HUMAN_PENDING，不是全连续证明。
- 已测Jacobian块结构与严格回退分支通过；最终曾检出lambda引起的自碰撞min/max步长敏感，未访问分支继续NONSMOOTH_DERIVATIVE_PARTIAL。严格回退是在求解后单独验证，未重新运行求解。
- 新数值墙钟预算258.719/600秒，含失败主要求解及所有诊断。实际Jacobian成本未获得产品级优化结论。

**不能直接接回旧轨迹。** 与原较早有效参考candidate_017相距66.076459mm，真实时差下只允许5.208333mm；两端固定时所需平均腕速6343.34mm/s。该外部连接未优化，不能据此证明所有可调整选择均不可行。

|门禁|结论|
|---|---|
|TIMELINE_AND_CONTACT_CONTRACT_PASS|PASS|
|TIME_COUPLED_JACOBIAN_VERIFIED|已测结构与后验局部分支PASS；全局不作PASS声明|
|COUPLED_CONTACT_FEASIBILITY_PASS|PASS，真实Blender|
|COUPLED_MOTION_BOUNDS_PASS|PASS，仅核心节点与局部采样|
|COUPLED_NODES_PASS_INTERPOLATION_FAIL|不成立|
|LOCAL_ADJACENCY_SAMPLED_PASS_HUMAN_PENDING|成立|
|CONTACT_RECOVERED_BUT_MOTION_INCOMPATIBLE|本轮核心局部不成立；外部连接仍不兼容|
|TIME_COUPLED_RECOVERY_NOT_FOUND_WITHIN_BUDGET|最终不成立；主要尝试失败证据保留|
|NONSMOOTH_DERIVATIVE_PARTIAL|成立|
|FAIL_CLOSED|未验证分支、外部边和完整窗口保持关闭|

独立重算9277个受保护文件哈希，0处变化、0个缺失（PROTECTION_CHECK.json）。Blender反解关节角的相邻速率也独立通过240deg/s原门禁。无正式Action、视频、渲染序列、Rig/MIDI/琴键Action修改；原24样本25ms回归、428.571ms连接、B02及23音演奏全部未执行。

**DESIGN_PROVISIONAL — STOP — HUMAN REVIEW。** 下一步必须先经Human选择入口/出口与产品路线，不自动扩大窗口。
