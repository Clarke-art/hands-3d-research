# audits/hands_continuous_motion_technical_route_decision_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> | 非目标顶点深度峰值 | 5.517936mm | 7.752886mm |

出处：[FINAL_TECHNICAL_ROUTE_DECISION.md](../research/audits/hands_continuous_motion_technical_route_decision_r1/FINAL_TECHNICAL_ROUTE_DECISION.md)

> | 运动表示缺陷 | 键架相对映射确实正确，却把来源腕模板随目标键架移动；`representation.py`（链接见原报告）的根只给有限 Y/Z 修正，无法充分协调不同黑白键纵深、持键与下一准备 | 表示应把键相对任务作为约束／先验，共享腕作为受绝对状态及导数约束的窗口轨迹；不能以代数读回成功证明空间可行 |

出处：[FINAL_TECHNICAL_ROUTE_DECISION.md](../research/audits/hands_continuous_motion_technical_route_decision_r1/FINAL_TECHNICAL_ROUTE_DECISION.md)

## 技术路线

> 存在避免从零编写大型数值求解器的现实组件组合；但尚无已验证的现成框架，能直接对本项目真实 LBS/corrective 皮肤，在固定 MIDI 时间内同时保证多指接触、整手避障和自然度。首选是工程验证方向，**不是已经可行或低成本的产品承诺**。外部组件的通用功能和主要许可证有官方依据；本项目适配、运行效率和动态成功率尚未验证，因此 readiness 为 PARTIAL。

出处：[FINAL_TECHNICAL_ROUTE_DECISION.md](../research/audits/hands_continuous_motion_technical_route_decision_r1/FINAL_TECHNICAL_ROUTE_DECISION.md)

> 实读 `A2 联合生成源码`（链接见原报告）、`事件协调器`（链接见原报告）及`设计记录`（链接见原报告）：右手每个稀疏支持时刻具有共享掌腕六维、五指二十维，另有每音键内接触 XY；195 支持点、5102 参数，带稀疏 Jacobian 的有界 least_squares 联合求解。活动、40ms 随键释放、180ms 准备及末段 75ms 下降共用同一掌腕；速度、加速度残差按实际 dt 连接相邻状态。保留准确事件阶段，普通点距精确阶段不足 4ms 时不重复加入。PCHIP 是联合求解后的读取方式，流畅性收益不能全归给插值。

出处：[FINAL_TECHNICAL_ROUTE_DECISION.md](../research/audits/hands_continuous_motion_technical_route_decision_r1/FINAL_TECHNICAL_ROUTE_DECISION.md)

## 测试结论

> 存在避免从零编写大型数值求解器的现实组件组合；但尚无已验证的现成框架，能直接对本项目真实 LBS/corrective 皮肤，在固定 MIDI 时间内同时保证多指接触、整手避障和自然度。首选是工程验证方向，**不是已经可行或低成本的产品承诺**。外部组件的通用功能和主要许可证有官方依据；本项目适配、运行效率和动态成功率尚未验证，因此 readiness 为 PARTIAL。

出处：[FINAL_TECHNICAL_ROUTE_DECISION.md](../research/audits/hands_continuous_motion_technical_route_decision_r1/FINAL_TECHNICAL_ROUTE_DECISION.md)

> 实读 `A2 联合生成源码`（链接见原报告）、`事件协调器`（链接见原报告）及`设计记录`（链接见原报告）：右手每个稀疏支持时刻具有共享掌腕六维、五指二十维，另有每音键内接触 XY；195 支持点、5102 参数，带稀疏 Jacobian 的有界 least_squares 联合求解。活动、40ms 随键释放、180ms 准备及末段 75ms 下降共用同一掌腕；速度、加速度残差按实际 dt 连接相邻状态。保留准确事件阶段，普通点距精确阶段不足 4ms 时不重复加入。PCHIP 是联合求解后的读取方式，流畅性收益不能全归给插值。

出处：[FINAL_TECHNICAL_ROUTE_DECISION.md](../research/audits/hands_continuous_motion_technical_route_decision_r1/FINAL_TECHNICAL_ROUTE_DECISION.md)

## 失败原因与证据边界

> `R2 机器结果`（链接见原报告）、`执行记录`（链接见原报告）及`真实失败报告`（链接见原报告）确认：一次连续候选已生成，Blender 240 时刻执行成功；真实 skin 重建最大差异 0.001232mm，故运动质量 FAIL 不能再归为工具链阻断。

出处：[FINAL_TECHNICAL_ROUTE_DECISION.md](../research/audits/hands_continuous_motion_technical_route_decision_r1/FINAL_TECHNICAL_ROUTE_DECISION.md)

> Blender 已有 Action、骨骼求值和蒙皮播放在 C1/R2 中实际使用；`官方 NLA 说明`（链接见原报告）支持层次动画混合，`官方 IK 条目`（链接见原报告）描述骨链跟随目标。但混合与骨链目标均不证明皮肤 pad 持触，更不自动避碰。最新手册/API 直开受抓取错误阻断，未核本机 IK/NLA 新适配；不把它列为可直接安装的解决方案。`Blender 官方许可`（链接见原报告）允许商业使用艺术输出；应用为 GNU GPL，分发 bpy 插件／软件需按实际边界核许可，不能把艺术输出许可扩大到所有代码。

出处：[FINAL_TECHNICAL_ROUTE_DECISION.md](../research/audits/hands_continuous_motion_technical_route_decision_r1/FINAL_TECHNICAL_ROUTE_DECISION.md)

## 后续建议

> 后续 `Human 回执`（链接见原报告）明确：整体原速运动被接受为基线，局部缺陷未接受。旧交付 HUMAN_PENDING 与后续回执需按时间区分。自然度依据是有限片段的 Human 观感，没有量化评分、跨曲成功率或无碰撞认证。

出处：[FINAL_TECHNICAL_ROUTE_DECISION.md](../research/audits/hands_continuous_motion_technical_route_decision_r1/FINAL_TECHNICAL_ROUTE_DECISION.md)

> | B02：原 R10 D5(4)→R11 E5(3) | 释放与下一 F♯5 准备的空间路径冲突，历史有限修正未闭合 | 不是后来的新指法 G4→E5，也不是本轮 R12→R13；局部失败不证明全局无解 |

出处：[FINAL_TECHNICAL_ROUTE_DECISION.md](../research/audits/hands_continuous_motion_technical_route_decision_r1/FINAL_TECHNICAL_ROUTE_DECISION.md)

## 原报告与关键代码

- [audits/hands_continuous_motion_technical_route_decision_r1/FINAL_TECHNICAL_ROUTE_DECISION.md](../research/audits/hands_continuous_motion_technical_route_decision_r1/FINAL_TECHNICAL_ROUTE_DECISION.md)

## 输入、输出与大型证据

该目录原始成员 3 项；拟公开身份记录 3 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
