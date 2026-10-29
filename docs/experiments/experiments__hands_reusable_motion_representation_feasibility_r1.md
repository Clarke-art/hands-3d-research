# experiments/hands_reusable_motion_representation_feasibility_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 失败根因是**预先指定的来源不具备整手安全资格**：C5无名指与D5小指的活动pad接触可靠，但中指／无名指释放和闲置动作真实穿插，并有非目标黑键侵入。整体自然观感认可不能将该片段直接升级为已清障原语。按用户止损规则停在Task 1，未改选来源或继续适配目标。

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_reusable_motion_representation_feasibility_r1/FINAL_HUMAN_REVIEW.md)

> | C 触键适配成功 | NOT_TESTED；来源168个活动pad样本PASS，目标适配没有运行。 |

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_reusable_motion_representation_feasibility_r1/FINAL_HUMAN_REVIEW.md)

## 技术路线

> | 5 相比旧高维优化有成本优势？ | **完整路线UNKNOWN。** 本轮来源核查20.568秒、优化0，可提前止损；没有生成＋验收成本，不能与P3求解77.704秒直接宣称加速比。 |

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_reusable_motion_representation_feasibility_r1/FINAL_HUMAN_REVIEW.md)

> | 8 继续修补还是换路线？ | **停止修补本次指定来源和本轮适配。** 不能把含穿插的闲置协调整段继承，再不断添加专用补丁。来源资格问题不证明事件相位＋相对动作表示不可行，也不支持立即重建动画引擎；下一步若获Human授权，应先闭合真正合格的来源契约，而非扩大动作库或恢复P3／B02求解。 |

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_reusable_motion_representation_feasibility_r1/FINAL_HUMAN_REVIEW.md)

## 测试结论

> **HANDS_REUSABLE_MOTION_REPRESENTATION_FEASIBILITY_R1 — FAIL。**

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_reusable_motion_representation_feasibility_r1/FINAL_HUMAN_REVIEW.md)

> | A 动作提取成功 | 原C1原始数据采样成功；**合格自然原语提取未实施**，来源门禁FAIL。 |

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_reusable_motion_representation_feasibility_r1/FINAL_HUMAN_REVIEW.md)

## 失败原因与证据边界

> 失败根因是**预先指定的来源不具备整手安全资格**：C5无名指与D5小指的活动pad接触可靠，但中指／无名指释放和闲置动作真实穿插，并有非目标黑键侵入。整体自然观感认可不能将该片段直接升级为已清障原语。按用户止损规则停在Task 1，未改选来源或继续适配目标。

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_reusable_motion_representation_feasibility_r1/FINAL_HUMAN_REVIEW.md)

> 按Task 1止损：原语提取0、目标生成0、局部IK0、姿态修补0、动态候选0、候选真实Rig验证0。没有尝试参数化适配、目标接触校正或空间校正，所以不能将失败原因写成“黑键适配不可达”或“时间衔接失败”。不制作任何新旧成品视频。

出处：[RETARGET_AND_GEOMETRY_VALIDATION.md](../research/experiments/hands_reusable_motion_representation_feasibility_r1/RETARGET_AND_GEOMETRY_VALIDATION.md)

## 后续建议

> | 6 值得扩展其他手指组合？ | **当前不建议直接扩展或建设动作库。** 缺少本次跨事件成功证据；应先在独立授权下取得并清楚验收一个全手安全、角色完整的来源，再检验单次复用。 |

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_reusable_motion_representation_feasibility_r1/FINAL_HUMAN_REVIEW.md)

> | 8 继续修补还是换路线？ | **停止修补本次指定来源和本轮适配。** 不能把含穿插的闲置协调整段继承，再不断添加专用补丁。来源资格问题不证明事件相位＋相对动作表示不可行，也不支持立即重建动画引擎；下一步若获Human授权，应先闭合真正合格的来源契约，而非扩大动作库或恢复P3／B02求解。 |

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_reusable_motion_representation_feasibility_r1/FINAL_HUMAN_REVIEW.md)

## 原报告与关键代码

- [experiments/hands_reusable_motion_representation_feasibility_r1/FINAL_HUMAN_REVIEW.md](../research/experiments/hands_reusable_motion_representation_feasibility_r1/FINAL_HUMAN_REVIEW.md)
- [experiments/hands_reusable_motion_representation_feasibility_r1/MOTION_PRIMITIVE_DESIGN.md](../research/experiments/hands_reusable_motion_representation_feasibility_r1/MOTION_PRIMITIVE_DESIGN.md)
- [experiments/hands_reusable_motion_representation_feasibility_r1/RETARGET_AND_GEOMETRY_VALIDATION.md](../research/experiments/hands_reusable_motion_representation_feasibility_r1/RETARGET_AND_GEOMETRY_VALIDATION.md)
- [experiments/hands_reusable_motion_representation_feasibility_r1/prepare.py](../../src/legacy/experiments/hands_reusable_motion_representation_feasibility_r1/prepare.py)
- [experiments/hands_reusable_motion_representation_feasibility_r1/reports.py](../../src/legacy/experiments/hands_reusable_motion_representation_feasibility_r1/reports.py)
- [experiments/hands_reusable_motion_representation_feasibility_r1/run_stage.py](../../src/legacy/experiments/hands_reusable_motion_representation_feasibility_r1/run_stage.py)
- [experiments/hands_reusable_motion_representation_feasibility_r1/source_audit.py](../../src/legacy/experiments/hands_reusable_motion_representation_feasibility_r1/source_audit.py)

## 输入、输出与大型证据

该目录原始成员 26 项；拟公开身份记录 20 项。
- `experiments/hands_reusable_motion_representation_feasibility_r1/SOURCE_AUDIT_SAMPLES.npz` → `hands-research-r1-selected-014.zip` / `payload/experiments/hands_reusable_motion_representation_feasibility_r1/SOURCE_AUDIT_SAMPLES.npz`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
