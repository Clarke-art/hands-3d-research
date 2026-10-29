# experiments/hands_sparse_window_constrained_trajectory_feasibility_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 本轮停止在Stage0，未启动正式优化或生成修正动态候选。原因是实际发现原C1固定边界与本轮整手非目标键0.5mm门禁冲突，且完整Jacobian成本不适合盲目启动180s求解。它不是“求解器不收敛”“优化超时”或Rig全局不可达，也不是一次修正候选的几何FAIL。

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_sparse_window_constrained_trajectory_feasibility_r1/FINAL_HUMAN_REVIEW.md)

> `BOUNDARY_CONTRACT_WITNESS.json`、`BOUNDARY_ACTUAL_WITNESS.npz`给出两端真实坐标、键组件身份、顶点及全部半空间内距。边界检查覆盖全部88键/139组件，不依赖规划邻域筛选。固定边界的52个自由基函数值及导数都为零，任意内窗系数都不能消除上述端点旧侵入。因此本次“原入口/出口不变＋整手非目标顶点≤0.5mm”没有合格候选。

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_sparse_window_constrained_trajectory_feasibility_r1/FINAL_HUMAN_REVIEW.md)

## 技术路线

> 本轮停止在Stage0，未启动正式优化或生成修正动态候选。原因是实际发现原C1固定边界与本轮整手非目标键0.5mm门禁冲突，且完整Jacobian成本不适合盲目启动180s求解。它不是“求解器不收敛”“优化超时”或Rig全局不可达，也不是一次修正候选的几何FAIL。

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_sparse_window_constrained_trajectory_feasibility_r1/FINAL_HUMAN_REVIEW.md)

> | A 真正短窗口联合约束，而非逐点IK？ | **联合模型与约束/Jacobian已建立并评价。** 原26状态流共享6槽/通道，边界消元后52变量；没有独立IK调用。尚未正式求解，不能声称取得联合可行轨迹。 |

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_sparse_window_constrained_trajectory_feasibility_r1/FINAL_HUMAN_REVIEW.md)

## 测试结论

> 本轮停止在Stage0，未启动正式优化或生成修正动态候选。原因是实际发现原C1固定边界与本轮整手非目标键0.5mm门禁冲突，且完整Jacobian成本不适合盲目启动180s求解。它不是“求解器不收敛”“优化超时”或Rig全局不可达，也不是一次修正候选的几何FAIL。

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_sparse_window_constrained_trajectory_feasibility_r1/FINAL_HUMAN_REVIEW.md)

> | R04 C5接触 | 58/58 PASS；横向0，绝对gap最大1.523343mm | 未生成，UNKNOWN |

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_sparse_window_constrained_trajectory_feasibility_r1/FINAL_HUMAN_REVIEW.md)

## 失败原因与证据边界

> 本轮停止在Stage0，未启动正式优化或生成修正动态候选。原因是实际发现原C1固定边界与本轮整手非目标键0.5mm门禁冲突，且完整Jacobian成本不适合盲目启动180s求解。它不是“求解器不收敛”“优化超时”或Rig全局不可达，也不是一次修正候选的几何FAIL。

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_sparse_window_constrained_trajectory_feasibility_r1/FINAL_HUMAN_REVIEW.md)

## 后续建议

> | H 下一独立窗口还是转C？ | **本轮不支持直接进入下一窗口，也不支持据此宣布A失败并自动转C。** 先独立审核边界与绝对/相对几何合同，及原Action导数和Jacobian成本。若仍要求坏端点冻结且整手绝对≤0.5mm，路线C同样继承此逻辑冲突，换工具无法解决。 |

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_sparse_window_constrained_trajectory_feasibility_r1/FINAL_HUMAN_REVIEW.md)

> 本轮最终范围：完成真实C1输入回读、稀疏联合表示/约束自测、成本评价与固定边界反证；**没有取得修正动态可行性证据**。23项实际引用历史输入SHA一致，原Rig/蒙皮/corrective、琴键Action、MIDI、指法及左手保持只读；独立piano完全排除。没有新Action、Blend、视频、外部框架安装或后续实验。

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_sparse_window_constrained_trajectory_feasibility_r1/FINAL_HUMAN_REVIEW.md)

## 原报告与关键代码

- [experiments/hands_sparse_window_constrained_trajectory_feasibility_r1/FINAL_HUMAN_REVIEW.md](../research/experiments/hands_sparse_window_constrained_trajectory_feasibility_r1/FINAL_HUMAN_REVIEW.md)
- [experiments/hands_sparse_window_constrained_trajectory_feasibility_r1/SPARSE_WINDOW_EXECUTION.md](../research/experiments/hands_sparse_window_constrained_trajectory_feasibility_r1/SPARSE_WINDOW_EXECUTION.md)
- [experiments/hands_sparse_window_constrained_trajectory_feasibility_r1/boundary_audit.py](../../src/legacy/experiments/hands_sparse_window_constrained_trajectory_feasibility_r1/boundary_audit.py)
- [experiments/hands_sparse_window_constrained_trajectory_feasibility_r1/cost_preflight.py](../../src/legacy/experiments/hands_sparse_window_constrained_trajectory_feasibility_r1/cost_preflight.py)
- [experiments/hands_sparse_window_constrained_trajectory_feasibility_r1/cost_preflight_before_clock_fix.py](../../src/legacy/experiments/hands_sparse_window_constrained_trajectory_feasibility_r1/cost_preflight_before_clock_fix.py)
- [experiments/hands_sparse_window_constrained_trajectory_feasibility_r1/export_baseline.py](../../src/legacy/experiments/hands_sparse_window_constrained_trajectory_feasibility_r1/export_baseline.py)
- [experiments/hands_sparse_window_constrained_trajectory_feasibility_r1/export_baseline_before_module_path_fix.py](../../src/legacy/experiments/hands_sparse_window_constrained_trajectory_feasibility_r1/export_baseline_before_module_path_fix.py)
- [experiments/hands_sparse_window_constrained_trajectory_feasibility_r1/finalize_stage0.py](../../src/legacy/experiments/hands_sparse_window_constrained_trajectory_feasibility_r1/finalize_stage0.py)
- [experiments/hands_sparse_window_constrained_trajectory_feasibility_r1/finalize_stage0_before_axis_dtype_fix.py](../../src/legacy/experiments/hands_sparse_window_constrained_trajectory_feasibility_r1/finalize_stage0_before_axis_dtype_fix.py)
- [experiments/hands_sparse_window_constrained_trajectory_feasibility_r1/inspect_inputs.py](../../src/legacy/experiments/hands_sparse_window_constrained_trajectory_feasibility_r1/inspect_inputs.py)
- [experiments/hands_sparse_window_constrained_trajectory_feasibility_r1/io_core.py](../../src/legacy/experiments/hands_sparse_window_constrained_trajectory_feasibility_r1/io_core.py)
- [experiments/hands_sparse_window_constrained_trajectory_feasibility_r1/io_core_before_null_device_fix.py](../../src/legacy/experiments/hands_sparse_window_constrained_trajectory_feasibility_r1/io_core_before_null_device_fix.py)
- [experiments/hands_sparse_window_constrained_trajectory_feasibility_r1/launch.py](../../src/legacy/experiments/hands_sparse_window_constrained_trajectory_feasibility_r1/launch.py)
- [experiments/hands_sparse_window_constrained_trajectory_feasibility_r1/native_model.py](../../src/legacy/experiments/hands_sparse_window_constrained_trajectory_feasibility_r1/native_model.py)

## 输入、输出与大型证据

该目录原始成员 70 项；拟公开身份记录 59 项。
- `experiments/hands_sparse_window_constrained_trajectory_feasibility_r1/BASELINE_ACTUAL.npz` → `hands-research-r1-selected-014.zip` / `payload/experiments/hands_sparse_window_constrained_trajectory_feasibility_r1/BASELINE_ACTUAL.npz`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
