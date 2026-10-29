# WHOLE_HAND_SURFACE_INTEGRITY_BASELINE_R1

已完成静态整手六视图、dorsal54 / palmar16 sentinel、14 个正式 45° case。最低机器安全门 PASS，源资产保持不变。普通实体初筛保留 **INDEX_MCP_45 的一个 POSSIBLE_VISIBLE_ISSUE**；其余 13 case 未观察到明显产品问题。尚未获得本轮整手 Human approval，停止于 Human review。

## Human approval 绑定

以当前聊天中 Human 明确答复作为正式来源：MID_MCP_15 / 30 / 45 = ACCEPT；all_three_visually_approved = true。PALMAR_ROOT_TARGETED_VISUAL_DEFORMATION_R1 = HUMAN_APPROVED。Human 明确说明原 JSON 不在本地并授权以消息绑定。只创建本轮绑定记录，未改写历史 response 或历史报告。current9_closure_approved = false；production_promotion_approved = false。

## 唯一视觉候选

- 位置：食指 MCP 根部靠拇指的 first-web 边缘。
- pose：INDEX_MCP_45（已有正式 IDX_MCP_45，骨骼 INDEX_MCP_R，local X -45°）。
- 分类：POSSIBLE_VISIBLE_ISSUE，尚非 Human 确认 blocker。
- 描述：普通斜侧整手图可见尖角状折边，近景呈 V 形硬折；由 Human 判断是否超出正常 crease / 轻微 faceting 的可接受范围。
- 普通整手截图：[斜侧实体图](../../../../artifacts/e94e386285a1bf5a1c44.md)；[主实体图](../../../../artifacts/de880c7a1c6f691f2b02.md)。
- 只为此 case 追加近景、替代、掠光和普通整手斜侧证据。未展开数值根因研究，未自动修复。

## 视觉与最低安全门

静态六视图初筛：未观察到明显异常，ACCEPTABLE_PENDING_HUMAN。指甲、指缝、拇指根、掌背轮廓、腕部过渡纳入普通实体检查。轻微低模 faceting / shading 保留，未据此自动升级。dorsal54 / palmar16 回退初筛 = NO / NO。

14 个 45° case 各自执行 RESET ZERO → 单骨 local X -45° → evaluate → render → RESET ZERO。有限值、面塌陷、边退化、明显严重拉伸均为 0；ZERO restore 14/14 PASS；WRIST_R 与 THUMB_CMC_R 保持锁定 ZERO。普通实体中未观察到明显新增穿模或严重邻指误带动，gross non-target contamination = 0。检查沿用已有最低阈值，不运行 hidden triangle crossing census。

初始斜侧相机遮住部分无名指 / 小指动作。展示阶段使用已评估的坐标替换 12 个四指主图为 distal/dorsal oblique，相机与灯光改变不施加新 pose，不打开源 blend。两个拇指主图保留可见拇指的斜侧视角。全手视图统一 scale / 中性材质 / studio lighting，sentinel 使用正常局部近景 scale。最终共 26 张普通实体图。

## 保护

源资产：`<HANDS_ROOT>\production_spec\stage5_production_rig\geometry_propagation_after_palmar_donor_restoration_r1\RIGHT_HAND_STAGE5B_R2_DONOR_TRANSFER_PALMAR_ROOT_GEOMETRY_R1.blend`

SHA256 前后均为 `90d3ebd1c1973f94020b66281781db481d5a366271a9d6aac6b921861e2b45aa`。原始 mesh 坐标、拓扑、权重、rig rest bones、modifiers、groups 等 native payload 前后完全一致，最终 ZERO。GEOMETRY_WRITES = WEIGHT_WRITES = RIG_WRITES = JOINT_WRITES = BLEND_PRODUCTION_SAVES = 0。

未执行 R3、true-cap、2127-edge continuity、normal-dot、weight solver、joint fitting、anatomy / retopo research、Full42 或 Stage6B；未重做 dorsal54 / palmar16 因果研究；未检查 current9 forensic pairs。

## 最终字段

| 字段 | 结果 |
|---|---|
| PALMAR_THREE_POSE_HUMAN_APPROVAL_BOUND | true |
| STATIC_VIEW_COUNT | 6 |
| POSE45_CASE_COUNT / COMPLETED | 14 / 14 |
| MACHINE_SAFETY | PASS |
| STATIC_VISIBLE_ISSUE_COUNT | 0 |
| POSE45_VISIBLE_ISSUE_COUNT | 1 POSSIBLE，0 CLEAR |
| VISIBLE_ISSUE_CASES | INDEX_MCP_45 |
| DORSAL / PALMAR_REPAIR_VISIBLE_REGRESSION | NO / NO |
| ZERO_RESTORE | PASS |
| GROSS_NON_TARGET_CONTAMINATION | 0 |
| GEOMETRY / WEIGHT / RIG / JOINT_WRITES | 0 / 0 / 0 / 0 |
| BLEND_PRODUCTION_SAVES | 0 |
| CURRENT9_HUMAN_RESPONSE | HOLD_NOT_CLOSED |
| PRODUCTION_PROMOTION | NO |
| VERDICT | HUMAN_REVIEW_REQUIRED_POSSIBLE_VISIBLE_ISSUE |

## Human 回答

打开 [review.html](../../../../../examples/historical/production_spec/stage6_deformation/whole_hand_surface_integrity_baseline_r1/review.html)，只回答：

1. Q1：静态整手 ACCEPT / VISIBLE_ISSUE。
2. Q2：14 动作 ACCEPT_ALL / ISSUE_IN_CASES（如有问题，case ID + 简短描述）。尤其判断 INDEX_MCP_45 折边是否可接受。
3. Q3：dorsal54 / palmar16 修复保持 YES / NO。

若 Human 接受该候选并确认整手通过，才可将本轮记录为 whole-hand Human PASS。NEXT 条件为 CURRENT_FULL_STAGE6A_CROSSING_HUMAN_CLOSURE_R1，本轮未执行 NEXT。STOP — HUMAN REVIEW。
