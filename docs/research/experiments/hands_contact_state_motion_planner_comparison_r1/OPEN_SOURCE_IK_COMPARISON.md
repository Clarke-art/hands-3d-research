# 开源IK源码与实际对照

调查日期2026-10-13。最多三个项目，只有Mink安装和实际运行。下载文件、URL及SHA256见 SOURCE_RESEARCH_INDEX.json；源码观察提交：Mink ae6759602593113ed7e5431ac7c65726ea27dc29，Pink 2c333161fc260de93fb7be1dd8d6519d2ecc2df2，Drake 613025408f14c68a7f0c844e5ef18588ce42578c。默认分支源码和已发布版本分别记录，不用README中的旧引用版本替代包版本。

| 项目 | 版本/运行条件 | 可复用接口 | 本轮层级 |
|---|---|---|---|
| Mink | PyPI及当前项目1.3.0；本机Windows CPython3.12轮子安装成功；MuJoCo3.15.0 | solve_ik/build_ik、Task.compute_error/compute_jacobian、constraints等式、Limit不等式；内建configuration/velocity/collision limits | 五层均实际完成 |
| Pink | PyPI4.4.0；依赖Pinocchio及QP。官方CI为Ubuntu/macOS，项目Pixi平台不含Windows；此次Pin4.1.0 PyPI无Windows轮子 | solve_ik(constraints=...)显式等式、关节/速度限制、SelfCollisionBarrier | SOURCE_REVIEWED；其余未执行 |
| Drake | 最新正式release v1.57.0；官方安装支持表为Ubuntu/macOS，无原生Windows发行路线 | MultibodyPlant InverseKinematics位置、姿态、距离上下界及关节限制 | SOURCE_REVIEWED；其余未执行 |

依据：[Mink依赖/Windows构建](https://github.com/kevinzakka/mink/blob/main/pyproject.toml)、[Mink等式接口](https://github.com/kevinzakka/mink/blob/main/src/mink/solve_ik.py)、[Pink依赖](https://github.com/pink-kinematics/pink/blob/main/pyproject.toml)、[Pink CI](https://github.com/pink-kinematics/pink/blob/main/.github/workflows/ci.yml)、[Pink显式约束](https://github.com/pink-kinematics/pink/blob/main/pink/solve_ik.py)、[Drake安装](https://drake.mit.edu/installation.html)、[Drake IK接口](https://drake.mit.edu/doxygen_cxx/classdrake_1_1multibody_1_1_inverse_kinematics.html)。Pink缺原生轮子不等于原则上不能在Windows编译，只是本轮不迁移Conda/WSL或构建复杂C++栈。

Mink和Pink均可将任务放入硬等式；普通FrameTask成本项本身仍是软目标，名称包含contact不会自动成为接触约束。Mink内建碰撞依赖MuJoCo geom距离；Pink的SelfCollisionBarrier依赖Pinocchio/HPP-FCL的光滑凸碰撞几何，源码说明非光滑几何行为未定义。两者不会自动理解Blender多骨权重皮肤的凹面、指腹材料区域或琴键Action时钟。[Mink碰撞实现](https://github.com/kevinzakka/mink/blob/main/src/mink/limits/collision_avoidance_limit.py)、[Pink碰撞实现](https://github.com/pink-kinematics/pink/blob/main/pink/barriers/self_collision_barrier.py)。Drake能表达距离约束，但仍需骨架/碰撞映射及动态蒙皮反馈，转换成本在本轮范围外。

许可：Mink/Pink为Apache-2.0，允许商业使用及分发，须遵守许可证副本、归属/NOTICE及修改声明等条件；专利授权和商标权边界见原许可。[Mink许可](https://github.com/kevinzakka/mink/blob/main/LICENSE)、[Pink许可](https://github.com/pink-kinematics/pink/blob/main/LICENSE)。Drake主体BSD-3-Clause，商业使用可行，保留版权/免责声明且不得未经许可用作者名背书，第三方组件另有许可。[Drake许可](https://github.com/RobotLocomotion/drake/blob/master/LICENSE.TXT)。本次DAQP为MIT，但qpsolvers为LGPL-3.0，商业分发仍需满足相应库修改/源码、通知及替换或重链接条件，不能把整个依赖栈统一说成Apache。[qpsolvers许可](https://github.com/qpsolvers/qpsolvers/blob/main/LICENSE)。所有安装包许可随deps保存，未采用商业QP后端。

实际Mink适配：12维真实Rig控制（掌根6、拇指4、λ、α）经原FK和加权皮肤求材料点/碰撞残差，公开Task/Limit子类提供误差和有限差分雅可比，调用未修改的mink.solve_ik(..., solver='daqp', constraints=[...], limits=[...])。MuJoCo中12个标量关节仅承载配置向量及积分，**不是重建的解剖骨架**；没有使用其小球几何做验收。真实外部求解输出映射回同一冻结Blender Rig，独立完整皮肤检查通过。因此属于REAL_RIG_ADAPTER_EXECUTED和CONTACT_CONSTRAINT_TESTED，但不是“MuJoCo原生骨架FK/原生碰撞已适配”。这一区别限制了可宣称的性能收益。

| 层级 | Mink证据 | Pink / Drake |
|---|---|---|
| SOURCE_REVIEWED | sources与源码索引 | 是 |
| TOOL_INSTALLED | INSTALL_REPORT.json，隔离deps | 否 |
| TOOL_SMOKE_TESTED | MINK_SMOKE_TEST.json，真实FK任务构造QP | 否 |
| REAL_RIG_ADAPTER_EXECUTED | 四阶段控制映射；P2/P3外部求解输出 | 否 |
| CONTACT_CONSTRAINT_TESTED | ACTUAL_DISCRETE_VALIDATION.json，面级P2/P3触键及几何通过 | 否 |

本轮不宣称Mink整体胜出。P2实测0.516秒对SLSQP1.031秒，但没有重复统计；P3种子已可行，约0.094对0.078秒，基本不构成求解挑战。共同的顶点代理曾使两者同样悬空，说明接触表示比换一个QP后端更关键。完整运行变量、约束数量、退出原因和失败版本见 MINIMAL_FEASIBILITY_RESULTS.json。
