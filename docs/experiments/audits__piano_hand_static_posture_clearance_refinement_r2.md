# audits/piano_hand_static_posture_clearance_refinement_r2

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 净空目标从R1少数低顶点代理改为冻结权重对完整3300顶点的预测与矩形键体距离，覆盖先前漏检指侧点；保存后实测仍独立检查全部88键。数值范围/权重执行前确定，未放宽；左/右各一次确定初始化联合两姿态求解，分别68 / 38 evaluations收敛。无restart、sweep、第二候选或连续Action。

出处：[PIANO_HAND_STATIC_POSTURE_CLEARANCE_REFINEMENT_R2_REPORT.md](../research/audits/piano_hand_static_posture_clearance_refinement_r2/PIANO_HAND_STATIC_POSTURE_CLEARANCE_REFINEMENT_R2_REPORT.md)

> |姿态|任务|固定pad gap R1→R2|R2皮肤gap|水平误差|结果|

出处：[PIANO_HAND_STATIC_POSTURE_CLEARANCE_REFINEMENT_R2_REPORT.md](../research/audits/piano_hand_static_posture_clearance_refinement_r2/PIANO_HAND_STATIC_POSTURE_CLEARANCE_REFINEMENT_R2_REPORT.md)

## 技术路线

> 净空目标从R1少数低顶点代理改为冻结权重对完整3300顶点的预测与矩形键体距离，覆盖先前漏检指侧点；保存后实测仍独立检查全部88键。数值范围/权重执行前确定，未放宽；左/右各一次确定初始化联合两姿态求解，分别68 / 38 evaluations收敛。无restart、sweep、第二候选或连续Action。

出处：[PIANO_HAND_STATIC_POSTURE_CLEARANCE_REFINEMENT_R2_REPORT.md](../research/audits/piano_hand_static_posture_clearance_refinement_r2/PIANO_HAND_STATIC_POSTURE_CLEARANCE_REFINEMENT_R2_REPORT.md)

## 测试结论

> 继承R1完整blend、政策、结果、网格/权重、键盘、固定pads及12原视角，不重跑R1、不搜索参考、不改材质。Human纠正权威完整保存：LEFT_NATURALNESS=NOT_APPROVED、RIGHT_NEIGHBOR_CLEARANCE=FAIL、FOUR_POSE_HUMAN_APPROVAL=NOT_GRANTED。

出处：[PIANO_HAND_STATIC_POSTURE_CLEARANCE_REFINEMENT_R2_REPORT.md](../research/audits/piano_hand_static_posture_clearance_refinement_r2/PIANO_HAND_STATIC_POSTURE_CLEARANCE_REFINEMENT_R2_REPORT.md)

> |L1|小指D2|0.586→0.523mm|0.541mm|0|PASS|

出处：[PIANO_HAND_STATIC_POSTURE_CLEARANCE_REFINEMENT_R2_REPORT.md](../research/audits/piano_hand_static_posture_clearance_refinement_r2/PIANO_HAND_STATIC_POSTURE_CLEARANCE_REFINEMENT_R2_REPORT.md)

## 失败原因与证据边界

> L1/L2 root仍相差0mm/0°，三闲置指形态一致，两个端点主动/准备成立。Thumb MCP饱和从25°减到约17.68°；但L2 thumb IP18°、L1 little MCP32°及spread25°、左roll-6°仍在边界，**没有声称端点紧张全部消除**。边界风险保留给Human，不当成生理极限或新技术阻断。静态共同配置为候选级通过，动态转换未生成/未验证。

出处：[PIANO_HAND_STATIC_POSTURE_CLEARANCE_REFINEMENT_R2_REPORT.md](../research/audits/piano_hand_static_posture_clearance_refinement_r2/PIANO_HAND_STATIC_POSTURE_CLEARANCE_REFINEMENT_R2_REPORT.md)

## 后续建议

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 原报告与关键代码

- [audits/piano_hand_static_posture_clearance_refinement_r2/PIANO_HAND_STATIC_POSTURE_CLEARANCE_REFINEMENT_R2_REPORT.md](../research/audits/piano_hand_static_posture_clearance_refinement_r2/PIANO_HAND_STATIC_POSTURE_CLEARANCE_REFINEMENT_R2_REPORT.md)
- [audits/piano_hand_static_posture_clearance_refinement_r2/00_policy.py](../../src/legacy/audits/piano_hand_static_posture_clearance_refinement_r2/00_policy.py)
- [audits/piano_hand_static_posture_clearance_refinement_r2/01_solve.py](../../src/legacy/audits/piano_hand_static_posture_clearance_refinement_r2/01_solve.py)
- [audits/piano_hand_static_posture_clearance_refinement_r2/02_scene.py](../../src/legacy/audits/piano_hand_static_posture_clearance_refinement_r2/02_scene.py)
- [audits/piano_hand_static_posture_clearance_refinement_r2/03_render.py](../../src/legacy/audits/piano_hand_static_posture_clearance_refinement_r2/03_render.py)
- [audits/piano_hand_static_posture_clearance_refinement_r2/04_measure.py](../../src/legacy/audits/piano_hand_static_posture_clearance_refinement_r2/04_measure.py)
- [audits/piano_hand_static_posture_clearance_refinement_r2/05_compare.py](../../src/legacy/audits/piano_hand_static_posture_clearance_refinement_r2/05_compare.py)
- [audits/piano_hand_static_posture_clearance_refinement_r2/06_finish.py](../../src/legacy/audits/piano_hand_static_posture_clearance_refinement_r2/06_finish.py)
- [audits/piano_hand_static_posture_clearance_refinement_r2/07_review.py](../../src/legacy/audits/piano_hand_static_posture_clearance_refinement_r2/07_review.py)
- [audits/piano_hand_static_posture_clearance_refinement_r2/09_verify.py](../../src/legacy/audits/piano_hand_static_posture_clearance_refinement_r2/09_verify.py)

## 输入、输出与大型证据

该目录原始成员 51 项；拟公开身份记录 50 项。
- `audits/piano_hand_static_posture_clearance_refinement_r2/STATIC_POSTURE_REFINED_CANDIDATE_R2.blend` → `hands-research-r1-selected-006.zip` / `payload/audits/piano_hand_static_posture_clearance_refinement_r2/STATIC_POSTURE_REFINED_CANDIDATE_R2.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
