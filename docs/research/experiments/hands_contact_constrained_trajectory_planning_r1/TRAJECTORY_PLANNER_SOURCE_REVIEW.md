# 成熟开源连续规划源码对照

OPEN_SOURCE_TRAJECTORY_PLANNER_REVIEWED。本轮仅选择CasADi实际适配；OMPL、TrajOpt/Tesseract是只读源码调查，未安装或声称运行PASS。源码读取于2026-10-13，逐文件URL、SHA256、获取失败记录在SOURCE_FILES.json；仓库commit及发行包平台元数据另存。未调用第三方云端规划，未上传Rig、MIDI或轨迹。

|候选|本次核实版本|接触/路径/时间能力|实际适配判断|
|---|---|---|---|
|OMPL|5b209a03fe48c41f7a2f364382c2e425bf1c7c1c|Constraint零集、Projected/Atlas/TangentBundle状态空间、RRTConnect几何搜索、有效性回调；固定音乐时间需另建时间/动力学层|未安装。当前PyPI2.0.1发行文件没有Windows wheel；源码存在Windows构建分支，不能据此称Windows不支持。当前环境需另核实构建/绑定成本|
|TrajOpt|48c9e54d67123d4dd92cdb0b8d40cfa5643a6d90|联合多步顺序凸优化；关节速度、加速度、jerk项；离散/连续碰撞约束/代价|未安装。已有Windows CI/构建宏，但依赖Tesseract、Eigen、Boost、trajopt_sco、JsonCpp等，非本轮轻量直接替换|
|Tesseract Planning（同候选生态）|261c19ff3aa09fd31b97363b6853a74c594d4db4|场景/运动规划组织与TrajOpt适配器|需要将本项目外部FK、运动键与非刚性蒙皮碰撞接入其场景和运动学接口；不能直接套刚体link碰撞结果替代皮肤验收|
|CasADi|执行固定3.7.2，commit f959d3175a444d763e4eda4aece48f4c5f4a6f90|多时刻NLP/最优控制建模、AD、IPOPT后端；接触阶段及轨迹约束由应用表达|Windows CPython3.12 wheel约51MB，隔离安装成功；实际完成144变量、6618约束联合时间问题的一次有输出IPOPT调用，超时未收敛|

CasADi仓库查询HEAD为168f53e307eee70278ba07e583d29b961c32ca34，PyPI查询当前版本为3.8.1；本轮没有混用HEAD与执行版本，固定3.7.2以对应已读取示例和源码。CasADi不是完整钢琴手规划器，项目必须提供模型、模式、避障与转录。未借外部库单点IK冒充轨迹规划。

## 核实的具体实现

OMPL [ProjectedStateSpace.cpp](https://github.com/ompl/ompl/blob/5b209a03fe48c41f7a2f364382c2e425bf1c7c1c/src/ompl/base/spaces/constraint/src/ProjectedStateSpace.cpp) 的discreteGeodesic先作局部插值再调用constraint_->project，并通过StateValidityChecker检查；投影失败、步长及曲率问题仍可能失败。[官方约束规划说明](https://ompl.kavrakilab.org/constrainedPlanning.html)说明三种流形表示与可微约束前提。Atlas/TangentBundle头文件及RRTConnect/SpaceInformation接口已保存；碰撞和接触模型仍由应用提供。几何路径不自动等于按MIDI时间可执行的轨迹。

TrajOpt [problem_description.cpp](https://github.com/tesseract-robotics/trajopt/blob/48c9e54d67123d4dd92cdb0b8d40cfa5643a6d90/trajopt/src/problem_description.cpp)注册joint_vel、joint_acc、joint_jerk及cart_vel；[collision_terms.hpp](https://github.com/tesseract-robotics/trajopt/blob/48c9e54d67123d4dd92cdb0b8d40cfa5643a6d90/trajopt/include/trajopt/collision_terms.hpp)区分时间步端点自由/固定，使用Tesseract ContinuousContactManager；kinematic_terms.cpp依赖操纵器FK/Jacobian。连续碰撞功能针对其接入的几何表示，不是对Blender蒙皮三角面自动成立的保证。Tesseract [TrajOpt适配源码](https://github.com/tesseract-robotics/tesseract_planning/blob/261c19ff3aa09fd31b97363b6853a74c594d4db4/motion_planners/trajopt/src/trajopt_motion_planner.cpp)已读取。Windows README步骤仍有TBD；本轮没有尝试复杂编译或机器人模型迁移。

CasADi [direct_collocation.py](https://github.com/casadi/casadi/blob/f959d3175a444d763e4eda4aece48f4c5f4a6f90/docs/examples/python/direct_collocation.py)联合优化多节点及连续性等式，调用nlpsol(...,'ipopt',...)；[direct_multiple_shooting.py](https://github.com/casadi/casadi/blob/f959d3175a444d763e4eda4aece48f4c5f4a6f90/docs/examples/python/direct_multiple_shooting.py)展示分段积分与状态匹配；[Callback接口](https://github.com/casadi/casadi/blob/f959d3175a444d763e4eda4aece48f4c5f4a6f90/casadi/core/callback.hpp)允许外部函数，导数仍须实现或有限差分。本轮采用符号FK/蒙皮及直接多项式配点，未照搬示例玩具系统，也未采用多重打靶积分。源码支持能力与本次实际实现分别记录。

## 许可及离线执行

OMPL所读核心[BSD-3-Clause许可证](https://github.com/ompl/ompl/blob/5b209a03fe48c41f7a2f364382c2e425bf1c7c1c/LICENSE)允许商业使用/再分发，须保留版权、条件、免责声明及不得背书条款；依赖另计。

TrajOpt本次所读trajopt与trajopt_sco [BSD-2-Clause许可证](https://github.com/tesseract-robotics/trajopt/blob/48c9e54d67123d4dd92cdb0b8d40cfa5643a6d90/trajopt/LICENSE)要求源/二进制分发保留通知。Tesseract [顶层许可声明](https://github.com/tesseract-robotics/tesseract_planning/blob/261c19ff3aa09fd31b97363b6853a74c594d4db4/LICENSE)说明逐文件Apache-2.0、BSD-2-Clause、BSD-3-Clause混合许可，分发时应按组件保留相应NOTICE/许可等；不是整个生态统一一个许可证。

CasADi [LICENSE.txt](https://github.com/casadi/casadi/blob/f959d3175a444d763e4eda4aece48f4c5f4a6f90/LICENSE.txt)为LGPLv3，代码头允许v3或后续版本。商业应用可使用；分发库修改/组合制品应履行对应源码、通知及库替换/重新链接等条件，不能仅理解成“免费所以任意静态封装”。实际IPOPT日志标识EPL，MUMPS及其他打包依赖许可需随分发逐项保留；本轮仅本地研究，未制作商业分发物。未使用付费Gurobi/Pro功能。

三个候选均可设计为完全本地执行。本轮运行只使用本地CasADi/IPOPT；网络仅用于源码、元数据及wheel下载。未调查/使用Ruckig或TOPPRA，不引入社区路点云API。
