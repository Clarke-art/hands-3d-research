# experiments/hands_contact_continuous_release_r2

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> OFF处约34.278mm瞬时目标跳变已消除；但分段包络仍误报，唯一连续方案发生关节越域、速率违规、E5失触和新增键侵入。没有合法连续路径，正式动态候选0，新Action/Blend/视频0。剩余预算不用于第二次搜索。

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_contact_continuous_release_r2/FINAL_HUMAN_REVIEW.md)

> | A. R1 OFF瞬间目标跳变解决了吗？ | **目标表达已解决。** OFF新增偏移/速度为0，随原40ms释放包络渐入，角色换标不重置路径；连续校正场两端值和导数为0。完整动作仍未合格，不能扩大为释放执行PASS。[阶段/目标Gate] |

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_contact_continuous_release_r2/FINAL_HUMAN_REVIEW.md)

## 技术路线

> | F. 能否区分失败原因？ | **部分能。** 旧瞬时阶段跳变已经闭合；代理仍制造假阻碍；当前校正表示与软域/接触残差未保持合法域，实际接触/键侵入反例明确。是否指骨自由度不足、原指法不可实现或必须增加掌腕，均未证明；ftol数值终止也不是全局无解证书。 |

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_contact_continuous_release_r2/FINAL_HUMAN_REVIEW.md)

> | **运动表示** | 原A2已有有界掌腕/五指稀疏联合求解与PCHIP；本轮少量加性系数虽连续，却导致绝对角域失守、接触被软代价交易。应在路线决策中优先比较保持域/接触的表示，与原有效机制的能力差异 | 未证明换一种表示即可消除B02；不得在当前机制中直接增加节点/系数、调权重或再搜索 |

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_contact_continuous_release_r2/FINAL_HUMAN_REVIEW.md)

## 测试结论

> **HANDS_CONTACT_CONTINUOUS_RELEASE_R2 — FAIL。停止当前“局部门户＋静态FK/IK修正”机制的继续扩展。**

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_contact_continuous_release_r2/FINAL_HUMAN_REVIEW.md)

> | A. R1 OFF瞬间目标跳变解决了吗？ | **目标表达已解决。** OFF新增偏移/速度为0，随原40ms释放包络渐入，角色换标不重置路径；连续校正场两端值和导数为0。完整动作仍未合格，不能扩大为释放执行PASS。[阶段/目标Gate] |

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_contact_continuous_release_r2/FINAL_HUMAN_REVIEW.md)

## 失败原因与证据边界

> | F. 能否区分失败原因？ | **部分能。** 旧瞬时阶段跳变已经闭合；代理仍制造假阻碍；当前校正表示与软域/接触残差未保持合法域，实际接触/键侵入反例明确。是否指骨自由度不足、原指法不可实现或必须增加掌腕，均未证明；ftol数值终止也不是全局无解证书。 |

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_contact_continuous_release_r2/FINAL_HUMAN_REVIEW.md)

> 圆形间距与分离轴间距不是同一种穿透深度，不能凭负值大小比较实际严重度。**本轮只证明了分段形状及完整面覆盖，未证明误判率改善**：三个试验姿态中的两处假阻碍仍存在。R2在窗口起点也报−3.228mm代理重叠，而原C1该指对实际相交为0；固定边界使这项代理残差不能清零，不能当人体或真实边界无解。

出处：[RELEASE_AND_ENVELOPE_FIX.md](../research/experiments/hands_contact_continuous_release_r2/RELEASE_AND_ENVELOPE_FIX.md)

## 后续建议

> **建议Human下一步只审议运动表示及约束保持的路线取舍，再决定是否需要独立的先验或掌腕协同工作。** 不再把“增加门户、阶段节点、包络参数或预算”作为当前机制的下一轮。

出处：[FINAL_HUMAN_REVIEW.md](../research/experiments/hands_contact_continuous_release_r2/FINAL_HUMAN_REVIEW.md)

> `h`由两段五次smoothstep相乘：从OFF起，在原A2的40ms释放跟随区间由0渐入1；之后平滑降到0，在下一音原75ms下降阶段开始前退出。h在OFF的值和一阶导数均为0；在释放跟随结束及退出处也保持一阶连续。角色由RELEASING转PREPARING时不重置目标。40ms是卸力/离键的动作安排，不延长MIDI持音。

出处：[RELEASE_AND_ENVELOPE_FIX.md](../research/experiments/hands_contact_continuous_release_r2/RELEASE_AND_ENVELOPE_FIX.md)

## 原报告与关键代码

- [experiments/hands_contact_continuous_release_r2/FINAL_HUMAN_REVIEW.md](../research/experiments/hands_contact_continuous_release_r2/FINAL_HUMAN_REVIEW.md)
- [experiments/hands_contact_continuous_release_r2/RELEASE_AND_ENVELOPE_FIX.md](../research/experiments/hands_contact_continuous_release_r2/RELEASE_AND_ENVELOPE_FIX.md)
- [experiments/hands_contact_continuous_release_r2/CONTINUOUS_PATH_VALIDATION.md](../research/experiments/hands_contact_continuous_release_r2/CONTINUOUS_PATH_VALIDATION.md)
- [experiments/hands_contact_continuous_release_r2/close.py](../../src/legacy/experiments/hands_contact_continuous_release_r2/close.py)
- [experiments/hands_contact_continuous_release_r2/path_model.py](../../src/legacy/experiments/hands_contact_continuous_release_r2/path_model.py)
- [experiments/hands_contact_continuous_release_r2/prepare.py](../../src/legacy/experiments/hands_contact_continuous_release_r2/prepare.py)
- [experiments/hands_contact_continuous_release_r2/runtime.py](../../src/legacy/experiments/hands_contact_continuous_release_r2/runtime.py)
- [experiments/hands_contact_continuous_release_r2/run_stage.py](../../src/legacy/experiments/hands_contact_continuous_release_r2/run_stage.py)
- [experiments/hands_contact_continuous_release_r2/setup.py](../../src/legacy/experiments/hands_contact_continuous_release_r2/setup.py)
- [experiments/hands_contact_continuous_release_r2/solve_path.py](../../src/legacy/experiments/hands_contact_continuous_release_r2/solve_path.py)
- [experiments/hands_contact_continuous_release_r2/validate_path.py](../../src/legacy/experiments/hands_contact_continuous_release_r2/validate_path.py)
- [experiments/hands_contact_continuous_release_r2/validation_request.py](../../src/legacy/experiments/hands_contact_continuous_release_r2/validation_request.py)

## 输入、输出与大型证据

该目录原始成员 43 项；拟公开身份记录 37 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
