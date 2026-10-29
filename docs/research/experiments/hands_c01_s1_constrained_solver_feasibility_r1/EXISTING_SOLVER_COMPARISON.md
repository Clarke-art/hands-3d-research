# 求解方法与适配证据对照

路线A实际2次；路线B仅调查3个候选，均未安装/运行，没有外部对照PASS。

| 方法 | 约束语义 | 实际证据 | 建议 |
| --- | --- | --- | --- |
| 原least_squares及修复 | bounds+加权接触/采样碰撞 | 2次nfev55未收敛，接触/交叉互换或悬空 | 几何可行性迁出残差 |
| SLSQP #1 | 明确ineq、过强固定轴/平面 | 11.500s、退出8；实际安全但悬空 | 不沿用这种恢复表示 |
| SLSQP #2 | 面内LP、接触区间、近面分离+全网格门禁 | 22.765s、2迭代、静态PASS、重读通过 | 保留局部静态内核 |
| Mink/Pink/Drake | 成熟机器人约束IK架构 | 只读调查，冻结Rig未运行 | 无外部优越性结论 |

[官方SLSQP文档](https://docs.scipy.org/doc/scipy/reference/optimize.minimize-slsqp.html)用于明确constraints、Jacobian和停止条件；本地版本记录于DEPENDENCY_MANIFEST.json，网页版本不是运行版本。[trust-constr文档](https://docs.scipy.org/doc/scipy/reference/optimize.minimize-trustconstr.html)仅选型，未实际比较性能。

## Mink — 只读

[Mink](https://github.com/kevinzakka/mink)有关节界和碰撞限制。[碰撞限制源码](https://raw.githubusercontent.com/kevinzakka/mink/main/src/mink/limits/collision_avoidance_limit.py)用MuJoCo距离及法向Jacobian构成QP不等式；检测带须覆盖一步闭合距离，有parent/weld过滤。这与原皮肤拓扑排除不同。接触帧任务不等于原指腹真实接触，需要自定义皮肤约束/oracle。

[构建配置](https://raw.githubusercontent.com/kevinzakka/mink/main/pyproject.toml)含MuJoCo、qpsolvers/DAQP和Windows AMD64构建；本机未安装验证。需原骨架自由度映射MJCF或自定义约束Jacobian桥接，多骨蒙皮/纠正形变不能由刚性geom直接复现。公平验证仍需原Blender网格，不能换手模型。估计适配中至高，未测工时。[Apache-2.0](https://raw.githubusercontent.com/kevinzakka/mink/main/LICENSE)允许商业使用和修改/分发，须保留许可/所需NOTICE并标记修改，专利/商标及依赖边界另核对。

## Pink — 只读

[Pink](https://github.com/pink-kinematics/pink)为加权任务差分IK QP，含配置/速度界。[自碰撞barrier源码](https://raw.githubusercontent.com/pink-kinematics/pink/main/pink/barriers/self_collision_barrier.py)用FCL距离/最近点Jacobian，声明非光滑几何行为未定义，可只取最近若干对。当前6596三角面和蒙皮不自动满足光滑凸体假设。需Pinocchio原骨架映射、自定义皮肤Jacobian、硬接触接口和原过滤。

[依赖配置](https://raw.githubusercontent.com/pink-kinematics/pink/main/pyproject.toml)含Pinocchio/qpsolvers，仓库pixi表未列Windows，这不证明全部Windows安装不可行；本机兼容性未试。适配中至高。[Apache-2.0](https://raw.githubusercontent.com/pink-kinematics/pink/main/LICENSE)商业边界同上，Pinocchio/FCL/QP依赖逐项核查。

## Drake — 只读

[官方IK API](https://drake.mit.edu/pydrake/pydrake.multibody.inverse_kinematics.html)有显式位置和MinimumDistanceLowerBound/UpperBound，但至少一对距离上界不自动指定原指腹/可触区域，仍需完整皮肤验收。需MultibodyPlant骨架映射和SceneGraph蒙皮桥接，刚性几何不能替代原真实网格。

[官方平台](https://drake.mit.edu/installation.html)列Linux/macOS、无Windows原生支持；WSL/系统转换或重建超出轻量验证。[BSD-3-Clause](https://raw.githubusercontent.com/RobotLocomotion/drake/master/LICENSE.TXT)允许商业使用/修改/分发，保留声明、不以作者名背书；第三方/可选商业优化器另核查。适配高，不部署。

## 公平性与成本

新#2从历史失败#2最终完整状态初始化，固定Z/原FK/皮肤/Action，证明局部修复可行；不是从相同原始C01分别重跑的统计实验。新#1/#2同时改变种子和表示，不能估计LP的单独贡献。

旧两次47.156s，新两次34.265s（含准备和差分诊断）。新#2 nfev2是目标调用，实际约束求值205；新#1目标84、约束987；旧残差1055/1095。不能仅比较55和2宣称27.5倍加速。本轮总墙钟未明显更慢，但22.8秒近可行单姿态不能外推整首MIDI效率。产品需共享解析Jacobian、活动集更新/步长约束、跨音缓存与失败闭锁，未做吞吐验证。外部方案没有实际更好的证据。

