# Stage 1A · AI 多视角可行性测试方案 R1

日期：2026-09-27  
状态：`AI_MULTIVIEW_PLAN = READY`  
范围：`STAGE1A_AI_MULTIVIEW_FEASIBILITY_TEST`，只验证 AI 参考图路线。

## 1. 继承的冻结基线

- 对象：`ADULT_NEUTRAL RIGHT HAND`；范围：`HAND + SHORT FOREARM`。
- 母版姿态：`CANONICAL_HAND_POSE = RSSF`；手指张开约 10–15°，MCP 约 20–30°、PIP 约 25–35°、DIP 约 10–20°。这些是母版生成技术范围，不是 `STANDARD_HAND` 教学参数。角度仅凭二维图不能精确量测，预检以可见半屈曲及跨视图一致性判断。
- 完整目标视角：`DORSAL`、`PALMAR`、`RADIAL`、`ULNAR`、`DISTAL`、`PROXIMAL`、`DORSAL_OBLIQUE_RADIAL`、`DORSAL_OBLIQUE_ULNAR`；8 个均为强制。
- 原则：`HAND = FIXED / LIGHT = FIXED / CAMERA = MOVES`。此原则作为 AI 图的可验证目标，不因生成工具缺少真实相机参数而假定已满足。
- Stage 2 首轮输入仍为 `8_VIEWS`，本测试不改变 `REFERENCE_ACQUISITION_GATE`。

权威依据：`CANONICAL_HAND_POSE_SPEC_R1.md`、`MULTIVIEW_REFERENCE_PACK_SPEC_R1.md`、`PHASE1_R1_2_FINAL_CLOSURE.md`。本文件不修订上述冻结文档。

## 2. 待验证命题

AI 生成的完整 8 张图，是否有足够证据被视为**同一只右手、同一母版姿态、同一短前臂、同一背景与固定光照下的不同相机视角**，并有潜力替代真人拍摄参考图。单张逼真或八张风格相近不构成通过证据。

## 3. 实施路线

使用内置 `image_gen`。先生成一个 Anchor，再以 Anchor 为图像输入做身份保持的视角派生。每次派生明确要求只移动相机，并重复锁定手别、五指比例、指甲、虎口、掌宽、腕与前臂、RSSF、背景和光照；生成器的文字承诺不等于几何锁定。

| 阶段 | 动作 | 放行条件 |
| --- | --- | --- |
| A | 生成 `AI_CANONICAL_RIGHT_HAND_ANCHOR`；检查右手、五指、RSSF、短前臂、无接触、分离度 | Anchor 达到可做跨视角试验的最低要求；否则定向重试，保留淘汰图 |
| B | 从合格 Anchor 派生 DORSAL / PALMAR / RADIAL / ULNAR | 四图逐张通过 `AI_MULTIVIEW_QC` 的关键结构、姿态和视角检查 |
| C | 仅在 B 通过后再派生 DISTAL / PROXIMAL / 两张 dorsal oblique | 完整八图通过同一 QC；仍须人工审核，不能自动批准正式包 |

若 B 出现无法解释的指长、掌宽、拇指、姿态或相机侧别冲突，停止扩展并判本轮 `FAIL` 或 `CONDITIONAL_PASS`。候选图均标记 `PRECHECK`，不得与正式参考包混用。

## 4. 生成与留痕约束

- 一视角一生成请求；不得把八次无约束文生图拼成图包。
- 生成图片先保存至工具默认目录，再复制进 `references/hand_r_canonical_ai/`；版本号不覆盖。
- Anchor 的身份保持尝试和四视角派生关系记录在结果文档和 `references/hand_r_canonical_ai/qc/GENERATION_LOG_R1.md`。
- QC 使用逐图目视与两两结构比对，区分“可观察”与“从图中不可验证”。不伪称有真实 3D 模型、相机外参或精确关节角度。
- 四视角失败则不生成后四视角，不调用 Hunyuan3D，不进入 Stage 2。

## 5. 判定

以 `STAGE1_AI_MULTIVIEW_QC_SPEC_R1.md` 为准。`PASS` 需要完整八图无关键冲突；`CONDITIONAL_PASS` 只适用于四视角主体关系基本自洽且缺陷局部可修；若四视角已发生主体几何或 RSSF 的明显漂移，判 `FAIL`。三种结论均不能自动通过 `REFERENCE_ACQUISITION_GATE`。
