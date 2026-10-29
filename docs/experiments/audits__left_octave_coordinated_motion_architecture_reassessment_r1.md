# audits/left_octave_coordinated_motion_architecture_reassessment_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> |L1/L2复用|作为接触锚与自然姿态参考；不能每次强制整手静态完全相等。|作为固定资产与有限姿态邻域；重叠时按任务处理。|复用最强，但容易把静态端点当作动态保证。|

出处：[MOTION_PLANNING_OPTIONS.md](../research/audits/left_octave_coordinated_motion_architecture_reassessment_r1/MOTION_PLANNING_OPTIONS.md)

> |双手/多曲目潜力|需处理接触切换、和弦和null-space选择；尚未验证。|任务接口可扩展多手/多音，同时约束规模与局部失败风险升高；尚未验证。|易扩展事件调度；新跨度/手位可能需要额外锚点，手工例外风险较高。|

出处：[MOTION_PLANNING_OPTIONS.md](../research/audits/left_octave_coordinated_motion_architecture_reassessment_r1/MOTION_PLANNING_OPTIONS.md)

## 技术路线

> Human批准的四静态姿态及冻结资产继续有效；当前动态演奏NOT_APPROVED。本轮新轨迹、新Action、新blend、求解器执行和渲染均为0。

出处：[MOTION_PLANNING_OPTIONS.md](../research/audits/left_octave_coordinated_motion_architecture_reassessment_r1/MOTION_PLANNING_OPTIONS.md)

> 评估依据是现有代码的可交易约束与时序限制，而不是方案名称。下列是概念架构判断，未安装新求解器、未做性能benchmark、未执行任一方案。`E08 · 当前29参数轨迹`（链接见原报告）、`E10 · 接触/净空/运动学加权残差`（链接见原报告）、`E11 · 只有参数bounds的least_squares`（链接见原报告）。

出处：[MOTION_PLANNING_OPTIONS.md](../research/audits/left_octave_coordinated_motion_architecture_reassessment_r1/MOTION_PLANNING_OPTIONS.md)

## 测试结论

> **B：可行性先行的分层受约束轨迹规划。** 所有root/active/idle时间参数同时进入同一问题；接触、真实可奏区、非穿透、关节/root域和连续性工程边界形成联合可行域。只有先达到这组要求，才在可行域内优化自然姿态、边界余量和运动代价。较低层优化不能增大高层关键违反量。未找到可行点应输出局部未找到/预算耗尽，而不是以较低cost包装PASS。

出处：[MOTION_PLANNING_OPTIONS.md](../research/audits/left_octave_coordinated_motion_architecture_reassessment_r1/MOTION_PLANNING_OPTIONS.md)

> 4. 保存重开后复用240Hz及原边界样点作独立检查，不重新优化。节点之间失接触/明显穿入即FAIL_CLOSED，不追加节点、seed或第二候选。

出处：[MINIMAL_NEXT_EXPERIMENT_PLAN.md](../research/audits/left_octave_coordinated_motion_architecture_reassessment_r1/MINIMAL_NEXT_EXPERIMENT_PLAN.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

> 上一有效拟合33 nfev、723 residual calls、1557.488s约26分钟，属于该机器/Blender实测路径，不是不同架构benchmark。`唯一有效求解记录`（链接见原报告）。未来硬约束可能更贵，不能承诺实时或普遍收敛。最小验证先限制参数、一次seed、固定采样与预算；准确率未达标不得扩到双手/多曲目。详细唯一实验见`下一阶段提案（未执行）`（链接见原报告）。

出处：[MOTION_PLANNING_OPTIONS.md](../research/audits/left_octave_coordinated_motion_architecture_reassessment_r1/MOTION_PLANNING_OPTIONS.md)

> 1. 下一轮先锁一次政策、输入SHA、单一seed、相位时间基与变量预算；记录算法/约束雅可比及native bind一致性检查。

出处：[MINIMAL_NEXT_EXPERIMENT_PLAN.md](../research/audits/left_octave_coordinated_motion_architecture_reassessment_r1/MINIMAL_NEXT_EXPERIMENT_PLAN.md)

## 原报告与关键代码

- [audits/left_octave_coordinated_motion_architecture_reassessment_r1/MOTION_PLANNING_OPTIONS.md](../research/audits/left_octave_coordinated_motion_architecture_reassessment_r1/MOTION_PLANNING_OPTIONS.md)
- [audits/left_octave_coordinated_motion_architecture_reassessment_r1/MINIMAL_NEXT_EXPERIMENT_PLAN.md](../research/audits/left_octave_coordinated_motion_architecture_reassessment_r1/MINIMAL_NEXT_EXPERIMENT_PLAN.md)
- [audits/left_octave_coordinated_motion_architecture_reassessment_r1/MOTION_ARCHITECTURE_CURRENT_STATE.md](../research/audits/left_octave_coordinated_motion_architecture_reassessment_r1/MOTION_ARCHITECTURE_CURRENT_STATE.md)
- [audits/left_octave_coordinated_motion_architecture_reassessment_r1/CONTACT_CLEARANCE_FAILURE_ANALYSIS.md](../research/audits/left_octave_coordinated_motion_architecture_reassessment_r1/CONTACT_CLEARANCE_FAILURE_ANALYSIS.md)
- [audits/left_octave_coordinated_motion_architecture_reassessment_r1/collect_evidence.py](../../src/legacy/audits/left_octave_coordinated_motion_architecture_reassessment_r1/collect_evidence.py)
- [audits/left_octave_coordinated_motion_architecture_reassessment_r1/write_reports.py](../../src/legacy/audits/left_octave_coordinated_motion_architecture_reassessment_r1/write_reports.py)

## 输入、输出与大型证据

该目录原始成员 11 项；拟公开身份记录 10 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
