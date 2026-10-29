# PALMAR_MACRO_PROPORTION_RESTORATION_FROM_OFFICIAL_SOURCE_R1

结论：**STATIC_PALM_SHAPE_STILL_INSUFFICIENT**。本轮 5 个静态 design iterations 均未达到“正常比例的手掌”。保存第 2 版作为相对平稳的失败设计候选供 Human 审阅；不申请成功验收，不用 BETTER 代替 CORRECT。

从正式 asset `production_spec/stage5_production_rig/geometry_propagation_after_palmar_donor_restoration_r1/RIGHT_HAND_STAGE5B_R2_DONOR_TRANSFER_PALMAR_ROOT_GEOMETRY_R1.blend`（SHA256 `90d3ebd1c1973f94020b66281781db481d5a366271a9d6aac6b921861e2b45aa`）重新建立候选，没有使用上一轮 tuned candidate。最终候选 `RIGHT_HAND_STAGE5B_PALMAR_MACRO_RESTORATION_CANDIDATE_R1.blend`，SHA256 `1a138c04b359bc407705870f6d7d3282227a617c46a56393112464ef37a48a6e`。DESIGN_ONLY / NOT_PRODUCTION / HUMAN_APPROVAL_PENDING。

Official reference 为 v1.4.1 Hand - Realistic 实际 evaluated Multires L1（3300 vertices / 3298 faces）。读取官方 blend 后验证 L1 原生坐标与历史只读快照一致；未使用工程化 RSSF donor。A 列展示 native source 经 palm rigid registration 后的外形，保持原始 thumb neutral pose。

配准使用 wrist/palm-base、四个 MCP root patches、central metacarpal 六组结构中心，scale=1。独立 thumb-shaft rigid fit 为 thumb-root 的 donor field 处理姿态差；不把 source 张开角直接复制到当前手。配准是本轮设计近似，不宣称已完全分离姿态和外形；各 landmark residual 见 REGISTRATION_AND_SOURCE_REFERENCE_R1.json。宏观比例恢复不足仍是可见结果，不作 root-cause 推断。

完整掌侧范围覆盖 palm width、thenar、thumb-root、lower first-web floor 和 wrist/MCP 过渡，第 2 版实际修改 **1238** 个原生顶点，restoration strength=1.4，非最小点集或默认低比例 blend。场从 source 的 ancestry-derived outward contour / palmar fullness 缺额估计，在当前手上连续插值；generated CMC 顶点只用周围场插值，不伪造 source ID 对应。没有复制 donor faces / topology。为连续过渡修改 lower proximal thumb 的根部部分，其主体与 distal segment 在高度裙边以外保持原坐标。

- 01：宏观 signed source contour 场；锁住整个 proximal thumb 的突变边界造成虎口底部明显折面。
- 02：完整掌面与连续 thumb-root skirt；只恢复 outward contour / palmar fullness 缺额。比其他版本平稳，但仍非正确比例；thumb-root / lower proximal 交界出现角状轮廓。
- 03：加强上 thenar palmar envelope 恢复；侧视掌缘外鼓，局部过渡不自然。
- 04：7 mm signed source field + 连续过渡；thumb-root 仍形成角状收缩，未恢复自然掌形。
- 05：5 mm 三维 source field + 全局连续 thumb pose registration skirt；连接体积变大，但 first-web 开口过窄、底部形成尖角。

最终视觉判断：掌宽和 thenar 体积有改善，upper thenar / thumb-root connection 仍没有达到来源模型的自然饱满比例；first-web 底部仍偏薄或角状。新的 thumb-root 至 lower proximal 角状轮廓 / diagonal facet，以及侧视中的 upper ulnar palm 外鼓，共计 2 个可见缺陷。故不能输出 VISUALLY_CORRECT_PALM_PROPORTION_PENDING_HUMAN，也不能输出 READY_FOR_HUMAN_STATIC_SHAPE_APPROVAL。

dorsal54 原生坐标保持，匹配哨兵未见回退。palmar16 按本轮要求作为视觉哨兵，允许坐标改变；匹配近景中旧 hard shelf 未重新出现，crease 仍存在。变化 ID 见 CANDIDATE_SAVE_REOPEN_PROTECTION_R1.json。

自动最低数值检查：NaN/Inf=0、collapsed faces=0、degenerate edges=0、ZERO restore=PASS。普通 solid screen 未见明显穿透或撕裂；**new hard contour=1，所以整体 MACHINE_SAFETY=FAIL_VISIBLE_HARD_CONTOUR**。数值通过不抵消产品外形失败。没有 hidden crossing census、normal-dot、strain 或动态审计。

候选保存一次并干净重开，原生位置与选中版本一致。UV/materials、topology/IDs、weights（含零项）、groups、modifiers、全部 21-bone rig / joints / rest / roll 均保持。仅自动 texspace bound 的派生值随 mesh bounds 改变；use_auto_texspace 原值保留，没有写 texture settings。无 shape keys / corrective。

22 张最终 matched renders：六个视图 × 三个资产，两个 sentinel × current/candidate。统一 camera、scale、material、lighting；source 的中性拇指姿态差明确保留，不能用整个手的 silhouette 差直接判断 pose-free volume。轮廓 overlay 仅供视觉辅助，不是数学 gate。

本轮已达到 5 版上限。最终候选与 review 页面供 Human 判断失败位置和下一步范围。没有运行 FULL_OPP_L1/L2/L3，未调 weights / rig，未跑 Stage6B final、左手镜像、motion retarget 或 production promotion。正式资产哈希保持。

**STOP — HUMAN REVIEW**。
