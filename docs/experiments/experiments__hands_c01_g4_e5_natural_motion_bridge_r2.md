# experiments/hands_c01_g4_e5_natural_motion_bridge_r2

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> | 目标键最大侵入 | 3.730269109mm，门禁0.25mm |

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_c01_g4_e5_natural_motion_bridge_r2/FINAL_RECOMMENDATION.md)

> | 全88键非目标/非指腹最大侵入 | 5.629029205mm，门禁0.25mm |

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_c01_g4_e5_natural_motion_bridge_r2/FINAL_RECOMMENDATION.md)

## 技术路线

> | 连续求解 | 19迭代，280.063秒预算停止，未收敛 |

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_c01_g4_e5_natural_motion_bridge_r2/FINAL_RECOMMENDATION.md)

> 新增数值求解共353.687秒（≤600秒）：2次端点、1次连续候选。没有增加迭代追求PASS。序列化修正未重求解；初版根原点导出错误对应的验收已明确排除。经修正Action实际复现B2/终点，才形成上述结论。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_c01_g4_e5_natural_motion_bridge_r2/FINAL_RECOMMENDATION.md)

## 测试结论

> **BRIDGE_MOTION_PARTIAL — DESIGN_PROVISIONAL — STOP — HUMAN REVIEW。**

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_c01_g4_e5_natural_motion_bridge_r2/FINAL_RECOMMENDATION.md)

> 新增数值求解共353.687秒（≤600秒）：2次端点、1次连续候选。没有增加迭代追求PASS。序列化修正未重求解；初版根原点导出错误对应的验收已明确排除。经修正Action实际复现B2/终点，才形成上述结论。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_c01_g4_e5_natural_motion_bridge_r2/FINAL_RECOMMENDATION.md)

## 失败原因与证据边界

> 本次实际证据是：合格静态端点存在，但连续求解未在允许G4持续接触的流形内建立可行路径；实际Action提前失联、提前碰E5并穿键。固定活动集的保守性、接触表示切换、有限差分质量及不可行初始化都可能阻碍SLSQP，尚无消融将单一因素确定为唯一数值根因。可以确定的接口缺口是：缺少由当前持键约束出发、贯穿换音接触状态切换的可行初始化/路径推进，而仅靠两个端点和平滑代价不足。

出处：[PRODUCT_ROUTE_CHECK.md](../research/experiments/hands_c01_g4_e5_natural_motion_bridge_r2/PRODUCT_ROUTE_CHECK.md)

## 后续建议

> 明确建议：保留现有FK和真实皮肤验收接口，暂停扩展当前端点插值式连续拟合，开展接触状态约束IK/姿态先验的同输入小范围实际对照。关键缺口是持键可行路径及换音接触状态的规划接口，不应再自动修补S1或放宽中指侧偏。当前没有证据表明必须更改冻结Rig，也不证明G4(1)→E5(3)在人类演奏中不可行。见 PRODUCT_ROUTE_CHECK.md。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_c01_g4_e5_natural_motion_bridge_r2/FINAL_RECOMMENDATION.md)

> 原键Action和冻结身份验证通过；保护文件最终哈希见 PROTECTED_FILES_AFTER.json。R05/R06/R07手部入口没有验证，结论仅覆盖本轮短连接候选。所有资料留在隔离目录，Human审阅后才决定后续研究。

出处：[FINAL_RECOMMENDATION.md](../research/experiments/hands_c01_g4_e5_natural_motion_bridge_r2/FINAL_RECOMMENDATION.md)

## 原报告与关键代码

- [experiments/hands_c01_g4_e5_natural_motion_bridge_r2/FINAL_RECOMMENDATION.md](../research/experiments/hands_c01_g4_e5_natural_motion_bridge_r2/FINAL_RECOMMENDATION.md)
- [experiments/hands_c01_g4_e5_natural_motion_bridge_r2/STAGED_MOTION_PLAN.md](../research/experiments/hands_c01_g4_e5_natural_motion_bridge_r2/STAGED_MOTION_PLAN.md)
- [experiments/hands_c01_g4_e5_natural_motion_bridge_r2/HUMAN_VISUAL_REVIEW.md](../research/experiments/hands_c01_g4_e5_natural_motion_bridge_r2/HUMAN_VISUAL_REVIEW.md)
- [experiments/hands_c01_g4_e5_natural_motion_bridge_r2/PRODUCT_ROUTE_CHECK.md](../research/experiments/hands_c01_g4_e5_natural_motion_bridge_r2/PRODUCT_ROUTE_CHECK.md)
- [experiments/hands_c01_g4_e5_natural_motion_bridge_r2/ENDPOINT_ANATOMY_AND_GEOMETRY.md](../research/experiments/hands_c01_g4_e5_natural_motion_bridge_r2/ENDPOINT_ANATOMY_AND_GEOMETRY.md)
- [experiments/hands_c01_g4_e5_natural_motion_bridge_r2/bake_and_validate.py](../../src/legacy/experiments/hands_c01_g4_e5_natural_motion_bridge_r2/bake_and_validate.py)
- [experiments/hands_c01_g4_e5_natural_motion_bridge_r2/bake_and_validate_initial.py](../../src/legacy/experiments/hands_c01_g4_e5_natural_motion_bridge_r2/bake_and_validate_initial.py)
- [experiments/hands_c01_g4_e5_natural_motion_bridge_r2/diagnose_activity.py](../../src/legacy/experiments/hands_c01_g4_e5_natural_motion_bridge_r2/diagnose_activity.py)
- [experiments/hands_c01_g4_e5_natural_motion_bridge_r2/export_tracks.py](../../src/legacy/experiments/hands_c01_g4_e5_natural_motion_bridge_r2/export_tracks.py)
- [experiments/hands_c01_g4_e5_natural_motion_bridge_r2/export_tracks_initial.py](../../src/legacy/experiments/hands_c01_g4_e5_natural_motion_bridge_r2/export_tracks_initial.py)
- [experiments/hands_c01_g4_e5_natural_motion_bridge_r2/finalize_reports.py](../../src/legacy/experiments/hands_c01_g4_e5_natural_motion_bridge_r2/finalize_reports.py)
- [experiments/hands_c01_g4_e5_natural_motion_bridge_r2/fix_action_serialization.py](../../src/legacy/experiments/hands_c01_g4_e5_natural_motion_bridge_r2/fix_action_serialization.py)
- [experiments/hands_c01_g4_e5_natural_motion_bridge_r2/fix_root_action.py](../../src/legacy/experiments/hands_c01_g4_e5_natural_motion_bridge_r2/fix_root_action.py)
- [experiments/hands_c01_g4_e5_natural_motion_bridge_r2/preflight.py](../../src/legacy/experiments/hands_c01_g4_e5_natural_motion_bridge_r2/preflight.py)
- [experiments/hands_c01_g4_e5_natural_motion_bridge_r2/prepare.py](../../src/legacy/experiments/hands_c01_g4_e5_natural_motion_bridge_r2/prepare.py)
- [experiments/hands_c01_g4_e5_natural_motion_bridge_r2/prepare_endpoint_second.py](../../src/legacy/experiments/hands_c01_g4_e5_natural_motion_bridge_r2/prepare_endpoint_second.py)
- [experiments/hands_c01_g4_e5_natural_motion_bridge_r2/prepare_motion.py](../../src/legacy/experiments/hands_c01_g4_e5_natural_motion_bridge_r2/prepare_motion.py)

## 输入、输出与大型证据

该目录原始成员 89 项；拟公开身份记录 65 项。
- `experiments/hands_c01_g4_e5_natural_motion_bridge_r2/E5_ENDPOINT_1_DIAGNOSTIC.blend` → `hands-research-r1-selected-008.zip` / `payload/experiments/hands_c01_g4_e5_natural_motion_bridge_r2/E5_ENDPOINT_1_DIAGNOSTIC.blend`
- `experiments/hands_c01_g4_e5_natural_motion_bridge_r2/E5_ENDPOINT_2_DIAGNOSTIC.blend` → `hands-research-r1-selected-008.zip` / `payload/experiments/hands_c01_g4_e5_natural_motion_bridge_r2/E5_ENDPOINT_2_DIAGNOSTIC.blend`
- `experiments/hands_c01_g4_e5_natural_motion_bridge_r2/G4_E5_NATURAL_BRIDGE_DESIGN_PROVISIONAL_R2.blend` → `hands-research-r1-selected-008.zip` / `payload/experiments/hands_c01_g4_e5_natural_motion_bridge_r2/G4_E5_NATURAL_BRIDGE_DESIGN_PROVISIONAL_R2.blend`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
