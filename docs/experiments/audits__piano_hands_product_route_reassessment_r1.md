# audits/piano_hands_product_route_reassessment_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 任务：**PIANO_HANDS_PRODUCT_ROUTE_REASSESSMENT_R1**；2026-10-14。

出处：[FINAL_RECOMMENDATION.md](../research/audits/piano_hands_product_route_reassessment_r1/FINAL_RECOMMENDATION.md)

> 本轮Human补充了三个准确名称与定义，说明它们是**此前拟定、尚未执行的修复任务，不是本轮审核前置条件**。以下为重新选路线后的范围建议，不授予R3实施权限。

出处：[FINAL_RECOMMENDATION.md](../research/audits/piano_hands_product_route_reassessment_r1/FINAL_RECOMMENDATION.md)

## 技术路线

> 任务：**PIANO_HANDS_PRODUCT_ROUTE_REASSESSMENT_R1**；2026-10-14。

出处：[FINAL_RECOMMENDATION.md](../research/audits/piano_hands_product_route_reassessment_r1/FINAL_RECOMMENDATION.md)

> **建议选择路线C，以C1较自然的23音作为新研发比较基准，复用有效稀疏联合求解，先验证短事件路径修正。暂停把复杂接触规划设为日常生成的强制主链。该建议尚未实施。**

出处：[FINAL_RECOMMENDATION.md](../research/audits/piano_hands_product_route_reassessment_r1/FINAL_RECOMMENDATION.md)

## 测试结论

> - B02：固定root、严格主动姿态保护下数次修正未解决；短事件路径、释放/下一准备协调值得验证。局部root比较失败且引入旁指风险，不能直接升为全局必要性结论。[E6、E8、T1]

出处：[FINAL_RECOMMENDATION.md](../research/audits/piano_hands_product_route_reassessment_r1/FINAL_RECOMMENDATION.md)

> **应保留的投入：** 原事件/键时钟、现成序列指法算法及持音检查、FK/真实烘焙一致性、运动键指腹范围、局部实际skin验证、准备/释放/闲置角色、连续曲线域检查、风格参考与有限运动回归。这些直接解释了已发现假PASS及真实缺陷。[E3–E8、T5、T7、T8]

出处：[FINAL_RECOMMENDATION.md](../research/audits/piano_hands_product_route_reassessment_r1/FINAL_RECOMMENDATION.md)

## 失败原因与证据边界

> **可能过度工程化的投入方式：** 默认全曲全皮肤硬不等式；在完整事件路径未通过前长期优化毫秒片段；不断修支持特征导数、增加区间节点/接口层，却不回到完整可见演奏；把C01一个大跨度难例升级为所有MIDI的强制接触执行器。C6 1800秒无合法候选、2ms局部与外部连接脱节、最新R2首次Jacobian阻断支持这一判断。[T3、T9、T10、T12]

出处：[FINAL_RECOMMENDATION.md](../research/audits/piano_hands_product_route_reassessment_r1/FINAL_RECOMMENDATION.md)

> | GEOMETRY_JACOBIAN_RELIABLE | **退出普通生成的强制Gate；高级后端有条件保留** | 如果继续使用R2支持特征几何优化，必须先修Invalid_Number_Detected并验证合法分支；未修不能调用该后端。局部模板/FK探测/碰撞后验本身无需此Jacobian。早期least_squares自己的导数/稀疏结构仍须正确，不能与R2几何导数混同。[E3、E6、T9、T12] |

出处：[FINAL_RECOMMENDATION.md](../research/audits/piano_hands_product_route_reassessment_r1/FINAL_RECOMMENDATION.md)

## 后续建议

> **建议选择路线C，以C1较自然的23音作为新研发比较基准，复用有效稀疏联合求解，先验证短事件路径修正。暂停把复杂接触规划设为日常生成的强制主链。该建议尚未实施。**

出处：[FINAL_RECOMMENDATION.md](../research/audits/piano_hands_product_route_reassessment_r1/FINAL_RECOMMENDATION.md)

> - B02：固定root、严格主动姿态保护下数次修正未解决；短事件路径、释放/下一准备协调值得验证。局部root比较失败且引入旁指风险，不能直接升为全局必要性结论。[E6、E8、T1]

出处：[FINAL_RECOMMENDATION.md](../research/audits/piano_hands_product_route_reassessment_r1/FINAL_RECOMMENDATION.md)

## 原报告与关键代码

- [audits/piano_hands_product_route_reassessment_r1/FINAL_RECOMMENDATION.md](../research/audits/piano_hands_product_route_reassessment_r1/FINAL_RECOMMENDATION.md)
- [audits/piano_hands_product_route_reassessment_r1/PRODUCT_BASELINE_REVIEW.md](../research/audits/piano_hands_product_route_reassessment_r1/PRODUCT_BASELINE_REVIEW.md)
- [audits/piano_hands_product_route_reassessment_r1/TECHNICAL_ROUTE_COMPARISON.md](../research/audits/piano_hands_product_route_reassessment_r1/TECHNICAL_ROUTE_COMPARISON.md)

## 输入、输出与大型证据

该目录原始成员 3 项；拟公开身份记录 3 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
