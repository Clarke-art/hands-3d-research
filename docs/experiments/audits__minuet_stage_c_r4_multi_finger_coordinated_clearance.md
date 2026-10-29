# audits/minuet_stage_c_r4_multi_finger_coordinated_clearance

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> Q2：食指、中指、无名指的MCP/PIP/DIP屈伸与MCP横展共12自由度。重点黑键G#4/A#4/C#5/D#5，F#5目标接触另检；附近F#4/G#5作为防止新增干涉的有限边界。

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_c_r4_multi_finger_coordinated_clearance/FINAL_ANSWERS.md)

> 原中指—无名指93对面相交，检查后92对；主动E5皮肤gap约0.751811mm，横向错位0；本时刻黑键BVH未命中。三视角仍有明显指对穿插。因此黑键及接触改善不能放行。邻指距离场最大残差约7.634mm只作为数值目标残差，不能解释成可靠的皮肤穿透深度。

出处：[PREGENERATION_FEASIBILITY.md](../research/audits/minuet_stage_c_r4_multi_finger_coordinated_clearance/PREGENERATION_FEASIBILITY.md)

## 技术路线

> Q3：实现了同时包含三指的联合静态协调，不是单指MCP修正；连续动态规划未通过门禁、未执行，因此整体PARTIAL。

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_c_r4_multi_finger_coordinated_clearance/FINAL_ANSWERS.md)

> Q12：正式动态候选0、正式动态求解0。有限静态数值检查未被包装成多份动态候选。

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_c_r4_multi_finger_coordinated_clearance/FINAL_ANSWERS.md)

## 测试结论

> Q3：实现了同时包含三指的联合静态协调，不是单指MCP修正；连续动态规划未通过门禁、未执行，因此整体PARTIAL。

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_c_r4_multi_finger_coordinated_clearance/FINAL_ANSWERS.md)

> Q11：原23音符、琴键、音频和时钟完全保持，原功能PASS；本轮没有新动态候选。

出处：[FINAL_ANSWERS.md](../research/audits/minuet_stage_c_r4_multi_finger_coordinated_clearance/FINAL_ANSWERS.md)

## 失败原因与证据边界

> 预检开发阶段有1批无效静态检查：其中白键地面保护误用了静止键面，错误阻碍主动指随键下沉。全部结果保存在 INVALID_STATIONARY_FLOOR_DEVELOPMENT_CHECK.json 及对应log，明确作废。修正为实际运动目标键面后完成1批13姿态的有效可行性检查。没有隐瞒该执行记录；不把两批数值计算写成只运行过一次，也不把它们称为动态候选。有效批失败后没有继续调参或搜索。

出处：[PREGENERATION_FEASIBILITY.md](../research/audits/minuet_stage_c_r4_multi_finger_coordinated_clearance/PREGENERATION_FEASIBILITY.md)

> 除 F#5 以外，上表为非目标黑键。F#5 是无名指的正常主动目标，0.563mm原局部进入作为独立触键误差检查，不把目标键接触全体豁免。跨阶段食指闲置净空与原 root 路线相联系；晚段中指 E5 的三项约束直接耦合。几何深度不自动等于同等可见严重度；本轮决定性阻断来自正常三视角仍明显的晚段指对穿插。

出处：[SPATIAL_CONFLICT_SCOPE.md](../research/audits/minuet_stage_c_r4_multi_finger_coordinated_clearance/SPATIAL_CONFLICT_SCOPE.md)

## 后续建议

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 原报告与关键代码

- [audits/minuet_stage_c_r4_multi_finger_coordinated_clearance/FINAL_ANSWERS.md](../research/audits/minuet_stage_c_r4_multi_finger_coordinated_clearance/FINAL_ANSWERS.md)
- [audits/minuet_stage_c_r4_multi_finger_coordinated_clearance/IMPLEMENTATION_REPORT.md](../research/audits/minuet_stage_c_r4_multi_finger_coordinated_clearance/IMPLEMENTATION_REPORT.md)
- [audits/minuet_stage_c_r4_multi_finger_coordinated_clearance/PREGENERATION_FEASIBILITY.md](../research/audits/minuet_stage_c_r4_multi_finger_coordinated_clearance/PREGENERATION_FEASIBILITY.md)
- [audits/minuet_stage_c_r4_multi_finger_coordinated_clearance/SPATIAL_CONFLICT_SCOPE.md](../research/audits/minuet_stage_c_r4_multi_finger_coordinated_clearance/SPATIAL_CONFLICT_SCOPE.md)
- [audits/minuet_stage_c_r4_multi_finger_coordinated_clearance/APPROVED_MOTION_PRESERVATION.md](../research/audits/minuet_stage_c_r4_multi_finger_coordinated_clearance/APPROVED_MOTION_PRESERVATION.md)
- [audits/minuet_stage_c_r4_multi_finger_coordinated_clearance/SPATIAL_CLEARANCE_VALIDATION.md](../research/audits/minuet_stage_c_r4_multi_finger_coordinated_clearance/SPATIAL_CLEARANCE_VALIDATION.md)
- [audits/minuet_stage_c_r4_multi_finger_coordinated_clearance/MULTI_FINGER_COORDINATION_DESIGN.md](../research/audits/minuet_stage_c_r4_multi_finger_coordinated_clearance/MULTI_FINGER_COORDINATION_DESIGN.md)
- [audits/minuet_stage_c_r4_multi_finger_coordinated_clearance/close_preflight.py](../../src/legacy/audits/minuet_stage_c_r4_multi_finger_coordinated_clearance/close_preflight.py)
- [audits/minuet_stage_c_r4_multi_finger_coordinated_clearance/coordination.py](../../src/legacy/audits/minuet_stage_c_r4_multi_finger_coordinated_clearance/coordination.py)
- [audits/minuet_stage_c_r4_multi_finger_coordinated_clearance/export_local_model.py](../../src/legacy/audits/minuet_stage_c_r4_multi_finger_coordinated_clearance/export_local_model.py)
- [audits/minuet_stage_c_r4_multi_finger_coordinated_clearance/finish.py](../../src/legacy/audits/minuet_stage_c_r4_multi_finger_coordinated_clearance/finish.py)
- [audits/minuet_stage_c_r4_multi_finger_coordinated_clearance/render_static_source.py](../../src/legacy/audits/minuet_stage_c_r4_multi_finger_coordinated_clearance/render_static_source.py)
- [audits/minuet_stage_c_r4_multi_finger_coordinated_clearance/scope_and_protection.py](../../src/legacy/audits/minuet_stage_c_r4_multi_finger_coordinated_clearance/scope_and_protection.py)
- [audits/minuet_stage_c_r4_multi_finger_coordinated_clearance/static_preflight.py](../../src/legacy/audits/minuet_stage_c_r4_multi_finger_coordinated_clearance/static_preflight.py)
- [audits/minuet_stage_c_r4_multi_finger_coordinated_clearance/verify_delivery.py](../../src/legacy/audits/minuet_stage_c_r4_multi_finger_coordinated_clearance/verify_delivery.py)
- [audits/minuet_stage_c_r4_multi_finger_coordinated_clearance/verify_static_geometry.py](../../src/legacy/audits/minuet_stage_c_r4_multi_finger_coordinated_clearance/verify_static_geometry.py)

## 输入、输出与大型证据

该目录原始成员 92 项；拟公开身份记录 87 项。
- `audits/minuet_stage_c_r4_multi_finger_coordinated_clearance/LOCAL_MODEL.npz` → `hands-research-r1-selected-003.zip` / `payload/audits/minuet_stage_c_r4_multi_finger_coordinated_clearance/LOCAL_MODEL.npz`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
