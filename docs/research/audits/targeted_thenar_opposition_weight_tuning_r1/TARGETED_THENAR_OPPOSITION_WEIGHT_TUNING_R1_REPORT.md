# TARGETED_THENAR_OPPOSITION_WEIGHT_TUNING_R1

2026-10-06（Asia/Shanghai）。PRODUCT_VISIBLE_QUALITY_FIRST。

## 结论

**VERDICT = VISIBLE_ISSUE_STILL_PRESENT。** ZERO 保持已接受的静态形状；L1 未见明显回退；L2 的硬折面减弱，但尚留角状边缘；L3 的虎口基底硬折角仍清楚可见。**没有宣布修好或 READY_FOR_HUMAN_VISUAL_APPROVAL。**

本轮先做局部 weight tuning，再做一次局部 pose-corrective support，均未改 ZERO 静态 vertex positions。纯局部权重调节不足以完成这一产品修复，剩余路线应是**更有针对性的 pose-corrective support**；本轮小范围平滑型支持也不足以消除 L3，故停止微调，不新开研究线。该路线判断来自可见效果，不是对唯一数学根因的证明。

## 正式 Human 绑定与隔离基线

用户本轮明示 `Q1 = ACCEPT / Q2 = REJECT / Q3 = YES`；Human note：ZERO 与 FULL_OPP_L1 可接受，FULL_OPP_L2 / L3 在虎口下方 / 大鱼际连接区硬折角不可接受。[正式绑定记录](../../../../examples/historical/audits/targeted_thenar_opposition_weight_tuning_r1/PRIOR_HUMAN_REVIEW_BINDING_R1.json)保留用户请求路径与 SHA256，并绑定实际 candidate SHA256。

输入：[已接受静态 candidate](../../../artifacts/b55f42073f03d7496327.md)，SHA256 `950d47f422f5c4b5eb604edefce0d6f4c542a90a395f522c3e9917ad362d12e8`。本工作区没有 Git repository，使用独立 `audits/targeted_thenar_opposition_weight_tuning_r1` 目录和独立 tuned blend 作为 design asset 分支，未覆盖旧 candidate 或 production。

输出：[RIGHT_HAND_STAGE5B_PALMAR_THENAR_OPPOSITION_TUNED_CANDIDATE_R1.blend](../../../artifacts/03a52f59dd767d7e067b.md)，SHA256 `07403e568b4c193e471e8047a39bbcc30a3c54e7503329246ec1169dc1c449d0`。仍为 DESIGN_ONLY / HUMAN_APPROVAL PENDING / PRODUCTION_PROMOTION NO。

## 实际修复范围

1. **局部权重调节：372 vertices。** 仅修改已有 WRIST_R / THUMB_CMC_R / THUMB_MCP_R / THUMB_IP_R 权重。使用 native one-ring 局部 smooth 与紧凑 transition；没有整手 weight solver。其他 influence columns 和区域外权重精确保持。
2. **局部动态支持：257 vertices，2 relative shape keys。** 从 L2 / L3 的 posed local surface 生成一个固定边界、紧凑 falloff 的有限 corrective，存为 native key delta。只软化局部动态 surface，不 fair / rewrite 静态 Basis。简单 drivers 依据既有 CMC opposition 与 MCP flexion 通道作门控，无新骨骼、joint、rest、modifier 或控制器。
3. **ZERO / L1 关闭支持。** 实际 clean-reopen 后求值：ZERO key values `[0,0]`；L1 `[0,0]`；L2 `[1,0]`；L3 `[0,1]`。组合 flexion 门控阻止仅 CMC 通道激活支持。其他未测试姿态不获资格声明。

区域限制在 PALMAR_THENAR_OPPOSITION_REGION：虎口下方、上部 thenar connection、palmar thumb-root、lower first-web floor 与局部 transition。dorsal54 / palmar16 / 原 normal69 及直接边界锁定；不改变无关四指主体。

## 产品结果

| Case | 状态 | 可见结果 |
| --- | --- | --- |
| ZERO | PRESERVED_ACCEPTED_STATIC_BASIS | 已接受的 ZERO 静态形状保持，native positions 和 Basis 坐标逐点不变，corrective 值均为 0。 |
| FULL_OPP_L1 | NO_VISIBLE_REGRESSION | 局部权重变化后未见明显回退；两项 corrective 在 L1 精确为 0。 |
| FULL_OPP_L2 | IMPROVED_BUT_VISIBLE_ISSUE_REMAINS | 虎口 floor 的过渡比基线柔和，但仍有角状边缘，尚不判自然度通过。 |
| FULL_OPP_L3 | VISIBLE_ISSUE_STILL_PRESENT | 硬折角减弱但仍清楚可见，未达到 Human 要求，停止本轮微调。 |

`NEW_VISIBLE_DEFECT_COUNT = 0` 指未观察到新的独立明显缺陷。原已知的硬折角问题仍有 L2 / L3 两个 residual case，尤其 L3；这不是“缺陷为零”或产品通过。

掌面主鼓起、first-web 开口与四指关系没有明显被带坏；未见新的 gross flap / penetration / tearing / contamination。dorsal54 / palmar16 matched sentinel 未见回退。

## 最低机器安全与保存核验

36 张 final matched ordinary renders：ZERO 与三种 FULL_OPP，每组 current candidate / tuned result，4 views；另有4张 sentinel。全部通过五张实体 inspection sheets 筛查，重点 close 另逐图检查。同相机、light、material、scale、image size；cavity OFF。

NaN / Inf = 0；collapsed face = 0；degenerate = 0；明显 self-intersection / penetration = 0；gross tearing = 0；gross contamination = 0；ZERO restore PASS。可见 gross 门不声称所有隐蔽数学 crossing 为零。局部硬折角是仍未通过的产品条件。

Clean reopen 确认原 native vertex positions 与新增 Basis 坐标逐点保持；topology、vertex IDs、UV、materials、groups、骨骼 / joints / rest matrices / modifiers 精确一致。变化只包含明确局部权重、两个局部 shape keys 及其简单驱动。Source candidate 和正式 production 不变。每个正式 case 都先 RESET ZERO，再 apply 原 Stage6B 定义、evaluate、render、RESET ZERO；最终所有21 pose channels ZERO，keys ZERO。未保存 nonzero pose。

机器安全 PASS 与产品 verdict VISIBLE_ISSUE_STILL_PRESENT 分开记录。没有 normal-dot、2127 edge、true-cap、隐藏 crossing census、大范围 Stage6A/Stage6B 资格流程或新 root-cause 研究。

## 最终字段

| 字段 | 值 |
| --- | --- |
| ZERO_STATIC_STATUS | PRESERVED_ACCEPTED_STATIC_BASIS |
| FULL_OPP_L1_STATUS | NO_VISIBLE_REGRESSION |
| FULL_OPP_L2_STATUS | IMPROVED_BUT_VISIBLE_ISSUE_REMAINS |
| FULL_OPP_L3_STATUS | VISIBLE_ISSUE_STILL_PRESENT |
| NEW_VISIBLE_DEFECT_COUNT | 0 |
| DORSAL54_REGRESSION | NO |
| PALMAR16_REGRESSION | NO |
| WEIGHT_TUNING_SCOPE | PALMAR_THENAR_OPPOSITION_REGION; 372 vertices; only existing WRIST / THUMB_CMC / THUMB_MCP / THUMB_IP influences |
| GEOMETRY_REWRITE_SCOPE | ZERO native/Basis positions: NONE; dynamic local support keys on 257 vertices only |
| MACHINE_SAFETY | PASS |
| PRODUCTION_PROMOTION | NO |
| VERDICT | VISIBLE_ISSUE_STILL_PRESENT |

## Human review 与停止

[review.html](../../../../examples/historical/audits/targeted_thenar_opposition_weight_tuning_r1/review.html) 提供 ZERO、L1、L2、L3 current/tuned 同机位比较，以及 dorsal54 / palmar16 sentinel；main、thenar close、side、full palm 可切换。Human 只回答 Q1 static、Q2 L1/L2/L3、Q3 新问题；本轮答案未预选，上一轮 Human 结论不会被填进新表单。

**STOP — HUMAN REVIEW。** 不继续 weight/geometry/corrective 微调，不自动进入后续路线，不做 production promotion 或 Stage6B final PASS。

证据：[状态](../../../../examples/historical/audits/targeted_thenar_opposition_weight_tuning_r1/TARGETED_THENAR_OPPOSITION_WEIGHT_TUNING_R1_STATUS.json)、[save/reopen](../../../../examples/historical/audits/targeted_thenar_opposition_weight_tuning_r1/TUNED_SAVE_REOPEN_PROTECTION_R1.json)、[最低自动检查](../../../../examples/historical/audits/targeted_thenar_opposition_weight_tuning_r1/MINIMUM_MACHINE_AUTOMATIC_R1.json)、[最低安全](../../../../examples/historical/audits/targeted_thenar_opposition_weight_tuning_r1/MINIMUM_MACHINE_SAFETY_R1.json)、[普通视觉记录](../../../../examples/historical/audits/targeted_thenar_opposition_weight_tuning_r1/ORDINARY_SOLID_VISUAL_INSPECTION_R1.json)。
