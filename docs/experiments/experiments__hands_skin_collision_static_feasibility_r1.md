# experiments/hands_skin_collision_static_feasibility_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> | 测试 | 实际指/键 | 状态 | pad距键mm | 真表面接触距mm | 目标实体侵入mm | 非目标/非指腹最大侵入mm | 指面相交 | 近接触面积mm² |

出处：[HUMAN_VISUAL_REVIEW.md](../research/experiments/hands_skin_collision_static_feasibility_r1/HUMAN_VISUAL_REVIEW.md)

> - S1图采用第一次C01初始化，目标G4面侵入0.549mm，最小顶点看似尚有+0.006mm间隙，却不是合法整体接触。第二批准R1初始化也未过，目标侵入0.278mm；两组都保留在Blend和JSON。拇指白键前缘/侧缘及三角面3869见证点为重点。

出处：[HUMAN_VISUAL_REVIEW.md](../research/experiments/hands_skin_collision_static_feasibility_r1/HUMAN_VISUAL_REVIEW.md)

## 技术路线

> 状态STATIC_FEASIBILITY_PARTIAL，全部DESIGN_PROVISIONAL。仅8张1280×720静帧，未制作视频或PNG序列。已有左手若在画面边缘，仅为原场景参考，不是本轮新求解。

出处：[HUMAN_VISUAL_REVIEW.md](../research/experiments/hands_skin_collision_static_feasibility_r1/HUMAN_VISUAL_REVIEW.md)

> **STOP — HUMAN REVIEW。** 不自动进入连续动作求解。

出处：[HUMAN_VISUAL_REVIEW.md](../research/experiments/hands_skin_collision_static_feasibility_r1/HUMAN_VISUAL_REVIEW.md)

## 测试结论

> 状态STATIC_FEASIBILITY_PARTIAL，全部DESIGN_PROVISIONAL。仅8张1280×720静帧，未制作视频或PNG序列。已有左手若在画面边缘，仅为原场景参考，不是本轮新求解。

出处：[HUMAN_VISUAL_REVIEW.md](../research/experiments/hands_skin_collision_static_feasibility_r1/HUMAN_VISUAL_REVIEW.md)

> | 测试 | 实际指/键 | 状态 | pad距键mm | 真表面接触距mm | 目标实体侵入mm | 非目标/非指腹最大侵入mm | 指面相交 | 近接触面积mm² |

出处：[HUMAN_VISUAL_REVIEW.md](../research/experiments/hands_skin_collision_static_feasibility_r1/HUMAN_VISUAL_REVIEW.md)

## 失败原因与证据边界

> 2. **C01初始为什么侵入？** 已确认食指/无名指远节实际进入A♯4/C♯5，不是误报。批准R1/R2无同类侵入；C01入口掌根/指部状态不同且约束遗漏完整皮肤。腕点低4.166mm及左移87.840mm是相关差异，不能未经消融就称唯一根因。旧pad近似目标和入口上下文不完整也有证据支持。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_skin_collision_static_feasibility_r1/FINAL_RECOMMENDATION.md)

## 后续建议

> 8. **应转向成熟IK/碰撞约束方案吗？** 本轮没有比较外部IK，不能凭名称判断更好。优先保留已验证FK/蒙皮与控制接口，加强真正表面约束；若这一有限改造在后续受控试验仍失败，再评估带碰撞约束的IK。没有证据要求现在替换整套系统。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_skin_collision_static_feasibility_r1/FINAL_RECOMMENDATION.md)

> **STOP — HUMAN REVIEW。** 不进入下一轮连续求解、动画或视频。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_skin_collision_static_feasibility_r1/FINAL_RECOMMENDATION.md)

## 原报告与关键代码

- [experiments/hands_skin_collision_static_feasibility_r1/HUMAN_VISUAL_REVIEW.md](../research/experiments/hands_skin_collision_static_feasibility_r1/HUMAN_VISUAL_REVIEW.md)
- [experiments/hands_skin_collision_static_feasibility_r1/FINAL_RECOMMENDATION.md](../research/experiments/hands_skin_collision_static_feasibility_r1/FINAL_RECOMMENDATION.md)
- [experiments/hands_skin_collision_static_feasibility_r1/COLLISION_METHOD_VALIDATION.md](../research/experiments/hands_skin_collision_static_feasibility_r1/COLLISION_METHOD_VALIDATION.md)
- [experiments/hands_skin_collision_static_feasibility_r1/INITIAL_POSE_COLLISION_DIAGNOSIS.md](../research/experiments/hands_skin_collision_static_feasibility_r1/INITIAL_POSE_COLLISION_DIAGNOSIS.md)
- [experiments/hands_skin_collision_static_feasibility_r1/complete_results.py](../../src/legacy/experiments/hands_skin_collision_static_feasibility_r1/complete_results.py)
- [experiments/hands_skin_collision_static_feasibility_r1/complete_surface_measurement.py](../../src/legacy/experiments/hands_skin_collision_static_feasibility_r1/complete_surface_measurement.py)
- [experiments/hands_skin_collision_static_feasibility_r1/correct_contact_metric_separation.py](../../src/legacy/experiments/hands_skin_collision_static_feasibility_r1/correct_contact_metric_separation.py)
- [experiments/hands_skin_collision_static_feasibility_r1/extract_actual_model.py](../../src/legacy/experiments/hands_skin_collision_static_feasibility_r1/extract_actual_model.py)
- [experiments/hands_skin_collision_static_feasibility_r1/prepare.py](../../src/legacy/experiments/hands_skin_collision_static_feasibility_r1/prepare.py)
- [experiments/hands_skin_collision_static_feasibility_r1/recheck_source_surfaces.py](../../src/legacy/experiments/hands_skin_collision_static_feasibility_r1/recheck_source_surfaces.py)
- [experiments/hands_skin_collision_static_feasibility_r1/render_static_review.py](../../src/legacy/experiments/hands_skin_collision_static_feasibility_r1/render_static_review.py)
- [experiments/hands_skin_collision_static_feasibility_r1/render_static_review_original.py](../../src/legacy/experiments/hands_skin_collision_static_feasibility_r1/render_static_review_original.py)
- [experiments/hands_skin_collision_static_feasibility_r1/solve_static_skin.py](../../src/legacy/experiments/hands_skin_collision_static_feasibility_r1/solve_static_skin.py)
- [experiments/hands_skin_collision_static_feasibility_r1/validate_detector.py](../../src/legacy/experiments/hands_skin_collision_static_feasibility_r1/validate_detector.py)
- [experiments/hands_skin_collision_static_feasibility_r1/validate_skin_proxy.py](../../src/legacy/experiments/hands_skin_collision_static_feasibility_r1/validate_skin_proxy.py)
- [experiments/hands_skin_collision_static_feasibility_r1/validate_triangle_interior.py](../../src/legacy/experiments/hands_skin_collision_static_feasibility_r1/validate_triangle_interior.py)

## 输入、输出与大型证据

该目录原始成员 73 项；拟公开身份记录 55 项。
- `experiments/hands_skin_collision_static_feasibility_r1/SKIN_COLLISION_STATIC_DIAGNOSTIC_R1.blend` → `hands-research-r1-selected-014.zip` / `payload/experiments/hands_skin_collision_static_feasibility_r1/SKIN_COLLISION_STATIC_DIAGNOSTIC_R1.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
