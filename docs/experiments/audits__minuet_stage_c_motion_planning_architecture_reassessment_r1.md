# audits/minuet_stage_c_motion_planning_architecture_reassessment_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> Q1：真实架构是原MIDI+预定指法→逐指事件阶段/键面目标→root6维、五指20维及每音触点联合稀疏轨迹→PCHIP与LINEAR四元数烘焙→C1复制两手Action并统一时间原点。不是固定root的五个独立IK。

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_c_motion_planning_architecture_reassessment_r1/FINAL_ANSWERS.md)

> Q5：R2单关节没有联合空间上下文；R4/root比较虽然增变量，仍是独立静态软约束，保留不稳定距离代理和释放任务缺口；root带动未保护的小指造成新冲突。

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_c_motion_planning_architecture_reassessment_r1/FINAL_ANSWERS.md)

## 技术路线

> Q4：首要结构缺口是实际空间约束与跨指角色协同，闲置先验和阶段切换是相关机制；局部求解方法有支持性风险。哪个因素对每帧主导UNKNOWN，不归罪于单个时间常数。

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_c_motion_planning_architecture_reassessment_r1/FINAL_ANSWERS.md)

> Q9：保留原root路线、窗口外全部动作、左手与音乐；窗口内按角色引用原自然姿态，避免强复制碰撞姿态或固定回NEUTRAL，最后Human完整1×验收。

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_c_motion_planning_architecture_reassessment_r1/FINAL_ANSWERS.md)

## 测试结论

> Q2：PARTIAL。联合变量、准备/释放和pad—键体代理已有；完整五指真实表面空间与跨事件角色协调没有形成连续生成机制。

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_c_motion_planning_architecture_reassessment_r1/FINAL_ANSWERS.md)

> Q13：目标冲突不能清除、新增明显穿模、接触丢失/越界、自然度恶化、窗口边界不可衔接、预算耗尽、需扩域或改冻结源，均FAIL_CLOSED；不调参重试。

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_c_motion_planning_architecture_reassessment_r1/FINAL_ANSWERS.md)

## 失败原因与证据边界

> 1. **空间约束缺口是首要结构原因。** 原始相交继承自A2，C1只复制动作；缺少指—指项且仅检查点状键体代理，解释了接触合格而skin失败。不能分配数值“责任百分比”。

出处：[SPATIAL_CONFLICT_ROOT_CAUSE_ANALYSIS.md](../research/audits/minuet_stage_c_motion_planning_architecture_reassessment_r1/SPATIAL_CONFLICT_ROOT_CAUSE_ANALYSIS.md)

> 2. **相向准备/恢复路径缺少协调。** 当前提前准备、固定中性先验和有限释放任务可能把手指引向另一指所在通道。早段闲置无名指与准备中指、晚段中指E5与无名指转F♯5尤其相关。阶段切换造成目标方向变化是已知，是否是某帧穿入的充分原因未知。

出处：[SPATIAL_CONFLICT_ROOT_CAUSE_ANALYSIS.md](../research/audits/minuet_stage_c_motion_planning_architecture_reassessment_r1/SPATIAL_CONFLICT_ROOT_CAUSE_ANALYSIS.md)

## 后续建议

> | C05 | 闲置指主要由单一NEUTRAL与时间正则维持 | `coordinated_motion.py:128`（链接见原报告）；不存在随邻指、键体与下一任务变化的空闲可行域 |

出处：[SPATIAL_CONFLICT_ROOT_CAUSE_ANALYSIS.md](../research/audits/minuet_stage_c_motion_planning_architecture_reassessment_r1/SPATIAL_CONFLICT_ROOT_CAUSE_ANALYSIS.md)

> | 核心决策 | 当前持键、下一准备、释放和闲置如何共同占用局部空间 | 直接为时间支撑上的全手状态施加接触与空间可行域 | 在批准风格邻域内寻找事件姿态并连续连接 |

出处：[WHOLE_HAND_PLANNING_OPTIONS.md](../research/audits/minuet_stage_c_motion_planning_architecture_reassessment_r1/WHOLE_HAND_PLANNING_OPTIONS.md)

## 原报告与关键代码

- [audits/minuet_stage_c_motion_planning_architecture_reassessment_r1/FINAL_ANSWERS.md](../research/audits/minuet_stage_c_motion_planning_architecture_reassessment_r1/FINAL_ANSWERS.md)
- [audits/minuet_stage_c_motion_planning_architecture_reassessment_r1/SPATIAL_CONFLICT_ROOT_CAUSE_ANALYSIS.md](../research/audits/minuet_stage_c_motion_planning_architecture_reassessment_r1/SPATIAL_CONFLICT_ROOT_CAUSE_ANALYSIS.md)
- [audits/minuet_stage_c_motion_planning_architecture_reassessment_r1/WHOLE_HAND_PLANNING_OPTIONS.md](../research/audits/minuet_stage_c_motion_planning_architecture_reassessment_r1/WHOLE_HAND_PLANNING_OPTIONS.md)
- [audits/minuet_stage_c_motion_planning_architecture_reassessment_r1/MINIMAL_ARCHITECTURE_EXPERIMENT_PLAN.md](../research/audits/minuet_stage_c_motion_planning_architecture_reassessment_r1/MINIMAL_ARCHITECTURE_EXPERIMENT_PLAN.md)
- [audits/minuet_stage_c_motion_planning_architecture_reassessment_r1/CURRENT_RIGHT_HAND_MOTION_ARCHITECTURE.md](../research/audits/minuet_stage_c_motion_planning_architecture_reassessment_r1/CURRENT_RIGHT_HAND_MOTION_ARCHITECTURE.md)
- [audits/minuet_stage_c_motion_planning_architecture_reassessment_r1/verify_reports.py](../../src/legacy/audits/minuet_stage_c_motion_planning_architecture_reassessment_r1/verify_reports.py)
- [audits/minuet_stage_c_motion_planning_architecture_reassessment_r1/write_reports.py](../../src/legacy/audits/minuet_stage_c_motion_planning_architecture_reassessment_r1/write_reports.py)

## 输入、输出与大型证据

该目录原始成员 11 项；拟公开身份记录 11 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
