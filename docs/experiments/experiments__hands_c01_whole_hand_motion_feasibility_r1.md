# experiments/hands_c01_whole_hand_motion_feasibility_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 现有目标函数主要约束五个pad、少量关节中心与键体代理，没有对完整指腹/指侧/闲置指的皮肤体积和指间互穿建立硬约束。掌根移动加上关节平滑不能自动消除这些缺口；3mm的pad避让和触点区边界也不能代表实际手指厚度。

出处：[C01_MOTION_PLAN.md](../research/experiments/hands_c01_whole_hand_motion_feasibility_r1/C01_MOTION_PLAN.md)

> 视频未渲染。真实碰撞门禁失败，按任务要求停止；无1x视频、0.5x或0.25x降速文件，不能宣称慢速自然度已经验收。没有临时PNG序列/GB缓存，仅保留这些交付静帧。所有截图都是同一份保存Action的求值结果，没有重算或选择替代动作。

出处：[HUMAN_VISUAL_REVIEW.md](../research/experiments/hands_c01_whole_hand_motion_feasibility_r1/HUMAN_VISUAL_REVIEW.md)

## 技术路线

> 复用Stage A R2联合求解：105个事件/阶段支撑节点、2748变量（各节点6个掌根/整体旋转＋20个指部自由度、每音2个可触键区坐标）、27032残差。位置/旋转/五指同时求解，包含时间速度、加速度正则及下一音准备。不是指尖关键帧之间直线插值，也不是固定root的单指重定向。

出处：[C01_MOTION_PLAN.md](../research/experiments/hands_c01_whole_hand_motion_feasibility_r1/C01_MOTION_PLAN.md)

> 求解后的整体/关节状态采用PCHIP连续插值，再以120Hz及精确事件/节点采样成501组状态。Blender烘焙为新掌根Action与五指Action，绝对帧时钟不变；骨骼四元数符号连续化。高频线性烘焙有有限采样/速度转折误差，不据此认定自然。

出处：[C01_MOTION_PLAN.md](../research/experiments/hands_c01_whole_hand_motion_feasibility_r1/C01_MOTION_PLAN.md)

## 测试结论

> 本轮已生成唯一隔离动作，最终MOTION_FEASIBILITY_PARTIAL，不作为可发布方案。保留C01，R06入口上下文＋R07—R14核心；不生成其余23音动作。

出处：[C01_MOTION_PLAN.md](../research/experiments/hands_c01_whole_hand_motion_feasibility_r1/C01_MOTION_PLAN.md)

> 求解后的整体/关节状态采用PCHIP连续插值，再以120Hz及精确事件/节点采样成501组状态。Blender烘焙为新掌根Action与五指Action，绝对帧时钟不变；骨骼四元数符号连续化。高频线性烘焙有有限采样/速度转折误差，不据此认定自然。

出处：[C01_MOTION_PLAN.md](../research/experiments/hands_c01_whole_hand_motion_feasibility_r1/C01_MOTION_PLAN.md)

## 失败原因与证据边界

> 后续仅尝试一次真实事件窗口联合轨迹，未进行逐根手指后修补。实际网格最终仍失败，根因指向现有规划约束不足；本轮没有证据证明冻结Rig或C01在所有可能控制策略下绝对不可行。

出处：[SOURCE_AND_RIG_PREFLIGHT.md](../research/experiments/hands_c01_whole_hand_motion_feasibility_r1/SOURCE_AND_RIG_PREFLIGHT.md)

## 后续建议

> 复用Stage A R2联合求解：105个事件/阶段支撑节点、2748变量（各节点6个掌根/整体旋转＋20个指部自由度、每音2个可触键区坐标）、27032残差。位置/旋转/五指同时求解，包含时间速度、加速度正则及下一音准备。不是指尖关键帧之间直线插值，也不是固定root的单指重定向。

出处：[C01_MOTION_PLAN.md](../research/experiments/hands_c01_whole_hand_motion_feasibility_r1/C01_MOTION_PLAN.md)

> 起点1.9142840秒、终点5.0642810秒为展示时钟。R14最终OFF位于片段边界，后续R15不生成，故不认证R14→R15整套释放/重按循环。

出处：[C01_MOTION_PLAN.md](../research/experiments/hands_c01_whole_hand_motion_feasibility_r1/C01_MOTION_PLAN.md)

## 原报告与关键代码

- [experiments/hands_c01_whole_hand_motion_feasibility_r1/C01_MOTION_PLAN.md](../research/experiments/hands_c01_whole_hand_motion_feasibility_r1/C01_MOTION_PLAN.md)
- [experiments/hands_c01_whole_hand_motion_feasibility_r1/HUMAN_VISUAL_REVIEW.md](../research/experiments/hands_c01_whole_hand_motion_feasibility_r1/HUMAN_VISUAL_REVIEW.md)
- [experiments/hands_c01_whole_hand_motion_feasibility_r1/FINAL_RECOMMENDATION.md](../research/experiments/hands_c01_whole_hand_motion_feasibility_r1/FINAL_RECOMMENDATION.md)
- [experiments/hands_c01_whole_hand_motion_feasibility_r1/SOURCE_AND_RIG_PREFLIGHT.md](../research/experiments/hands_c01_whole_hand_motion_feasibility_r1/SOURCE_AND_RIG_PREFLIGHT.md)
- [experiments/hands_c01_whole_hand_motion_feasibility_r1/bake_and_check.py](../../src/legacy/experiments/hands_c01_whole_hand_motion_feasibility_r1/bake_and_check.py)
- [experiments/hands_c01_whole_hand_motion_feasibility_r1/blender_preflight.py](../../src/legacy/experiments/hands_c01_whole_hand_motion_feasibility_r1/blender_preflight.py)
- [experiments/hands_c01_whole_hand_motion_feasibility_r1/blender_utils.py](../../src/legacy/experiments/hands_c01_whole_hand_motion_feasibility_r1/blender_utils.py)
- [experiments/hands_c01_whole_hand_motion_feasibility_r1/check_static_actual.py](../../src/legacy/experiments/hands_c01_whole_hand_motion_feasibility_r1/check_static_actual.py)
- [experiments/hands_c01_whole_hand_motion_feasibility_r1/motion_core.py](../../src/legacy/experiments/hands_c01_whole_hand_motion_feasibility_r1/motion_core.py)
- [experiments/hands_c01_whole_hand_motion_feasibility_r1/prepare_continuous_solver.py](../../src/legacy/experiments/hands_c01_whole_hand_motion_feasibility_r1/prepare_continuous_solver.py)
- [experiments/hands_c01_whole_hand_motion_feasibility_r1/prepare_inputs.py](../../src/legacy/experiments/hands_c01_whole_hand_motion_feasibility_r1/prepare_inputs.py)
- [experiments/hands_c01_whole_hand_motion_feasibility_r1/recover_export_receipt.py](../../src/legacy/experiments/hands_c01_whole_hand_motion_feasibility_r1/recover_export_receipt.py)
- [experiments/hands_c01_whole_hand_motion_feasibility_r1/render_diagnostics.py](../../src/legacy/experiments/hands_c01_whole_hand_motion_feasibility_r1/render_diagnostics.py)
- [experiments/hands_c01_whole_hand_motion_feasibility_r1/render_static_diagnostics.py](../../src/legacy/experiments/hands_c01_whole_hand_motion_feasibility_r1/render_static_diagnostics.py)
- [experiments/hands_c01_whole_hand_motion_feasibility_r1/solve_continuous.py](../../src/legacy/experiments/hands_c01_whole_hand_motion_feasibility_r1/solve_continuous.py)
- [experiments/hands_c01_whole_hand_motion_feasibility_r1/solve_continuous_executed.py](../../src/legacy/experiments/hands_c01_whole_hand_motion_feasibility_r1/solve_continuous_executed.py)

## 输入、输出与大型证据

该目录原始成员 56 项；拟公开身份记录 46 项。
- `experiments/hands_c01_whole_hand_motion_feasibility_r1/C01_WHOLE_HAND_MOTION_DESIGN_PROVISIONAL_R1.blend` → `hands-research-r1-selected-008.zip` / `payload/experiments/hands_c01_whole_hand_motion_feasibility_r1/C01_WHOLE_HAND_MOTION_DESIGN_PROVISIONAL_R1.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
