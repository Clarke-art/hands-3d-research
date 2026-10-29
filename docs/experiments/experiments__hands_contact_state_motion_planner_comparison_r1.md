# experiments/hands_contact_state_motion_planner_comparison_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> | 阶段/方法 | 目标侵入mm | 非目标/非指腹侵入mm | 中/无名间隙mm | 真实接触 |

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_contact_state_motion_planner_comparison_r1/FINAL_RECOMMENDATION.md)

> 本轮找到了可复用的**接触状态合同与离散求解适配原型**，尚未找到已证明可适用于不同MIDI的完整运动生成器。六类合同测试全部来自现有同一MIDI，不应称为多个曲目的运动成功率验证。

出处：[PRODUCT_ROUTE_REVIEW.md](../research/experiments/hands_contact_state_motion_planner_comparison_r1/PRODUCT_ROUTE_REVIEW.md)

## 技术路线

> **路线A：保留现有FK/蒙皮与SLSQP，增加接触状态约束规划层。** 本轮Mink真实适配完成，但没有足够优势证据选择路线B；保留其为同输入对照后端。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_contact_state_motion_planner_comparison_r1/FINAL_RECOMMENDATION.md)

> - EXTERNAL_IK_COMPARISON_EXECUTED：Mink1.3.0经真实冻结FK/蒙皮自定义接口求解，并在Blender独立验收。没有宣称原生MuJoCo骨架和碰撞模型完成迁移。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_contact_state_motion_planner_comparison_r1/FINAL_RECOMMENDATION.md)

## 测试结论

> **路线A：保留现有FK/蒙皮与SLSQP，增加接触状态约束规划层。** 本轮Mink真实适配完成，但没有足够优势证据选择路线B；保留其为同输入对照后端。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_contact_state_motion_planner_comparison_r1/FINAL_RECOMMENDATION.md)

> - CONTACT_STATE_CONTRACT_PASS：正式MIDI与原Blender键Action复核通过，三套时间语义分开，90个事件阶段及六类复用解析通过。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_contact_state_motion_planner_comparison_r1/FINAL_RECOMMENDATION.md)

## 失败原因与证据边界

> 本轮不宣称Mink整体胜出。P2实测0.516秒对SLSQP1.031秒，但没有重复统计；P3种子已可行，约0.094对0.078秒，基本不构成求解挑战。共同的顶点代理曾使两者同样悬空，说明接触表示比换一个QP后端更关键。完整运行变量、约束数量、退出原因和失败版本见 MINIMAL_FEASIBILITY_RESULTS.json。

出处：[OPEN_SOURCE_IK_COMPARISON.md](../research/experiments/hands_contact_state_motion_planner_comparison_r1/OPEN_SOURCE_IK_COMPARISON.md)

> 已知结构性不足：从不可行端点插值种子直接求整条曲线，没有先验证当前持键可行域中的准备增量，也没有独立验证换音接触模式的边界兼容。数值停滞是实测；其究竟由导数质量、活动集合、参数化还是局部不可行组合主导，上一轮没有充分消融，不能宣称唯一根因已确定。原MIDI也没有证据必须改动。

出处：[PREVIOUS_PLANNER_FAILURE_ANALYSIS.md](../research/experiments/hands_contact_state_motion_planner_comparison_r1/PREVIOUS_PLANNER_FAILURE_ANALYSIS.md)

## 后续建议

> 全部最终样本指面交叉0、解剖参考族/授权控制域违规0。P2掌腕移动约3mm，中指更接近下一音，但仍未达到E5最终位置。P3为2.921426秒原E5未下压状态下的接触模式；P4为ON后35ms，二者独立通过，不混为同一时刻。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_contact_state_motion_planner_comparison_r1/FINAL_RECOMMENDATION.md)

> 后续唯一关键验证：换音两侧接触集合的连续边界兼容。旧音OFF后不再必须被按住，但连续位置可能仍要求边界瞬间兼容旧接触左极限和新接触右极限。若这一小范围问题在原时序、自然关节和几何合同下冲突，应保存冲突证据停止，不能通过瞬移、提前释放、改指法或扩大求解时间绕过。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_contact_state_motion_planner_comparison_r1/FINAL_RECOMMENDATION.md)

## 原报告与关键代码

- [experiments/hands_contact_state_motion_planner_comparison_r1/FINAL_RECOMMENDATION.md](../research/experiments/hands_contact_state_motion_planner_comparison_r1/FINAL_RECOMMENDATION.md)
- [experiments/hands_contact_state_motion_planner_comparison_r1/PRODUCT_ROUTE_REVIEW.md](../research/experiments/hands_contact_state_motion_planner_comparison_r1/PRODUCT_ROUTE_REVIEW.md)
- [experiments/hands_contact_state_motion_planner_comparison_r1/CONTACT_STATE_CONTRACT.md](../research/experiments/hands_contact_state_motion_planner_comparison_r1/CONTACT_STATE_CONTRACT.md)
- [experiments/hands_contact_state_motion_planner_comparison_r1/OPEN_SOURCE_IK_COMPARISON.md](../research/experiments/hands_contact_state_motion_planner_comparison_r1/OPEN_SOURCE_IK_COMPARISON.md)
- [experiments/hands_contact_state_motion_planner_comparison_r1/PREVIOUS_PLANNER_FAILURE_ANALYSIS.md](../research/experiments/hands_contact_state_motion_planner_comparison_r1/PREVIOUS_PLANNER_FAILURE_ANALYSIS.md)
- [experiments/hands_contact_state_motion_planner_comparison_r1/contact_state_planner.py](../../src/legacy/experiments/hands_contact_state_motion_planner_comparison_r1/contact_state_planner.py)
- [experiments/hands_contact_state_motion_planner_comparison_r1/inspect_action.py](../../src/legacy/experiments/hands_contact_state_motion_planner_comparison_r1/inspect_action.py)
- [experiments/hands_contact_state_motion_planner_comparison_r1/prepare.py](../../src/legacy/experiments/hands_contact_state_motion_planner_comparison_r1/prepare.py)
- [experiments/hands_contact_state_motion_planner_comparison_r1/run_discrete_comparison.py](../../src/legacy/experiments/hands_contact_state_motion_planner_comparison_r1/run_discrete_comparison.py)
- [experiments/hands_contact_state_motion_planner_comparison_r1/run_face_witness_comparison.py](../../src/legacy/experiments/hands_contact_state_motion_planner_comparison_r1/run_face_witness_comparison.py)
- [experiments/hands_contact_state_motion_planner_comparison_r1/run_mink_step_correction.py](../../src/legacy/experiments/hands_contact_state_motion_planner_comparison_r1/run_mink_step_correction.py)
- [experiments/hands_contact_state_motion_planner_comparison_r1/supplement_evidence.py](../../src/legacy/experiments/hands_contact_state_motion_planner_comparison_r1/supplement_evidence.py)
- [experiments/hands_contact_state_motion_planner_comparison_r1/verify_delivery.py](../../src/legacy/experiments/hands_contact_state_motion_planner_comparison_r1/verify_delivery.py)
- [experiments/hands_contact_state_motion_planner_comparison_r1/verify_discrete_blender.py](../../src/legacy/experiments/hands_contact_state_motion_planner_comparison_r1/verify_discrete_blender.py)
- [experiments/hands_contact_state_motion_planner_comparison_r1/write_reports.py](../../src/legacy/experiments/hands_contact_state_motion_planner_comparison_r1/write_reports.py)

## 输入、输出与大型证据

该目录原始成员 6137 项；拟公开身份记录 47 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
