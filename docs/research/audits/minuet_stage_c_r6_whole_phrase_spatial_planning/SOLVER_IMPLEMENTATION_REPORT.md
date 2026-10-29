# 求解器实现与一次正式执行

全段联合规划已经实现并实际尝试；合法空间运动结果未建立。新增代码全部位于本 R6 目录，历史 R5、A2、B3、C1、冻结 Rig、皮肤、权重和 corrective 均未原地修改。

`prepare.py` 复用 R5 角色接口并构建全段节点；`export_readonly.py` / `inspect_shape.py` 只读提取冻结场景；`whole_phrase_model.py` 重建五指绝对关节 FK、真实 LBS 与原拇指 corrective；`trajectory_solver.py` 实现全段 C1 三次曲线、Bezier 工程域、空间/触键不等式和源风格目标；`run_once.py` 设置外部墙钟保险；验证脚本只测量唯一终态，不再求解。

后端 scipy.optimize.minimize / trust-constr 1.18.1 / sparse AugmentedSystem。一次正式调用，3400 个未知数，339 个节点/中点空间样本，7017 个空间与触键不等式，另有全曲线工程域线性约束和变量边界。所有 20 个关节参与；root 自由度 0。主要迭代上限 200，目标 nfev 上限 2000，空间函数调用上限 4300，墙钟 1800 秒。锁定文件、代码与源模型哈希保存在 STRATEGY_LOCK.json；正式开始前独占写入 FORMAL_ATTEMPT_STARTED.json，防止重跑。

终止：`External 1800s watchdog; no restart; last accepted checkpoint retained`。状态 `WATCHDOG_STOP`，数值 success `False`。已完成主要迭代 23；真实 nfev：精确值不可用；最后完成迭代下界 23，见 watchdog 限制；记录墙钟 1800.031 秒。完整 trace/计数见 SOLVER_TERMINATION.json。没有第二次求解、换权重、多起点、静态搜索或 root 扩域。

外部强制停止若发生，`FORMAL_CHECKPOINT.npz` 仅保存最后已完成迭代，不能冒称未完成调用的精确 nfev；计数下界及缺失被显式报告。终态数值证据不是新 Blend/Action 候选。

方法局限：支持平面分离要求强权重指区的保守凸包分离，可能排除真实表面不相交的自然姿态；键体使用实际组件的顶点内部约束，仍需独立表面和视觉验收。因此本次失败不证明固定 root、冻结 Rig 或全部可行轨迹无解。

计数交付限制：日志可确认 23 次已完成目标评估、483 次已完成空间评估及 23 条主要迭代记录；外部止损时仍有调用进行，最终精确 nfev/空间调用总数未可靠落盘。这一项没有完全满足请求，不能补造精确数字。完整已完成 trace 已从日志恢复至 SOLVER_TERMINATION.json。

RELEASING/EXITING 没有独立接触力学模型或强制旧键持键等式；离键与交接由原机械键面、连续源风格和全手空间不等式共同安排。角色组织已实现，实际释放/准备的自然执行仍未通过本轮门禁。
