# RIGHT_HAND_PRODUCT_BASELINE_R2_PROMOTION_R1

**PROMOTION = PASS**  
**RIGHT_HAND_PRODUCT_BASELINE_R2 = HUMAN_APPROVED_FROZEN**  
**FIRST_WEB_HUMAN_VISIBLE_BLOCKER = CLOSED**  
**RIGHT_HAND_DEFORMATION = CLOSED**  
**RIGHT_HAND_READY_FOR_LEFT_HAND_STAGE = YES**  
**R1_HISTORICAL_FALLBACK_UNCHANGED = YES**

已将 Human 最终批准的同一份 deformation state 升格并冻结为 R2，production pointer 从 R1 更新到 R2。完整权重和全部核心产品 payload 与批准 candidate 逐项完全一致；只清理审计播放包装与身份标记，没有重求 harmonic、刷 weights、改 mesh/rig 或重新 qualification。

## Q1–Q8

| # | 问题 | 回答 |
|---|---|---|
| Q1 | 获批 candidate SHA 匹配？ | YES |
| Q2 | Candidate container 状态？ | AUDIT_SCAFFOLDING_PRESENT |
| Q3 | R2 完整 weight field EXACT_MATCH？ | YES |
| Q4 | mesh/topology/rig/rest/corrective/driver 一致？ | YES |
| Q5 | ZERO/F130/FULL_OPP_L3 最小 smoke 通过？ | YES |
| Q6 | R1 fallback 原 SHA 保持？ | YES |
| Q7 | production pointer 成功 R1 → R2？ | YES |
| Q8 | R2 = HUMAN_APPROVED_FROZEN 成立？ | YES |

## Human 最终授权与输入

本轮明确获得 Human 决策：RIGHT_HAND_FIRST_WEB_PRODUCTION_WEIGHT_QUALIFICATION_R1 = HUMAN_APPROVED，HUMAN_PRODUCTION_APPROVAL = APPROVED，FIRST_WEB_HUMAN_VISIBLE_BLOCKER = CLOSED，NEW_HUMAN_VISIBLE_REGRESSION = NO，PRODUCTION_PROMOTION = AUTHORIZED。原 qualification report / review / JSON / 视频和原 causal candidate 都保持原样，PENDING / DESIGN_ONLY 历史未追改。独立 HUMAN_APPROVAL_BIND_R1.json 绑定当前用户请求与已审核视频的 SHA。

唯一获批 candidate：`audits/right_hand_first_web_full_static_weight_field_causal_probe_r1/RIGHT_HAND_FIRST_WEB_FULL_STATIC_WEIGHT_PROBE_R1.blend`  
SHA256：`0f6b24fc8d74a0fe37fb4a142169633d525db3c2ea58a440005060c137cc374d`。

上一轮完整 7 秒 / 三产品视角 / 六旧姿态 / ZERO / 421 observations 的 PASS 和 Human approval 直接继承。本轮不重做它们。

## 容器检查与 clean packaging

**CANDIDATE_CONTAINER_STATUS = AUDIT_SCAFFOLDING_PRESENT**。只读 inventory 显示：只有原 Official L1 mesh 与成熟 rig 两个对象；无 audit camera、comparison object、debug collection 或 evidence helper。

仍有两类审计包装：保存于 F130 并绑定的 PianoVAM qualification Action，以及 DESIGN_ONLY / NOT_PRODUCTION / approval pending 标记（包括继承的 HUMAN_APPROVAL=PENDING、DO_NOT_PROMOTE）。它们不应成为正式产品的身份或运行依赖，因此采用 **CLEAN_PRODUCTION_CONTAINER_EXACT_PRODUCT_DATA**，而非 byte-copy 整个审计 .blend。

允许的变化仅为：

- R2 以 ZERO / RSSF、frame 1 保存，清除 qualification playback binding；生产容器不嵌入 PianoVAM evidence Action。
- 在新容器内将审计 approval/identity labels 改为 Human-approved frozen 状态；原 candidate 的 Action payload 与文件均未改。
- 该同一 Action 在重新打开 R2 的未保存 smoke 会话中临时 library-append，验证 F130 兼容；不写回 R2，因此 **PianoVAM_RUNTIME_DEPENDENCY = NO**。

新 R2 SHA 与 candidate 不同是容器包装变化，并非重新生成等价 weights。所有差异白名单、数据哈希与清理前后 container SHA 都记录于 PROMOTION_IDENTITY_R1.json。首次新容器保存后补齐两个继承的 scene approval 标签，**在 pointer 更新前**重新验证所有核心 payload 完全一致；未改任何 approved deformation data。

## Exact product identity

R2：`production_spec/right_hand_product_baseline_r2/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R2.blend`  
**R2_BASELINE_SHA256 = `c946fed318fa88c238d9aacc30cfb4e52f268848f0ad65a4dcbf594754d791f0`**。

保留 Official L1 source identity、3300 vertices / 3298 faces、现有 21-bone teaching rig（16 deform + 5 non-deform TIP helpers）、原 approved corrective/driver 和 Human-approved complete static field。

**WEIGHT_FIELD_IDENTITY = EXACT_MATCH**。全部 3300 个完整 weight vectors、ROI active-bone 向量、boundary 和 ROI 外 weights 均完全相同。weight-field SHA256：`ad4c82d2d108084aaf41c618dca625b8704b51ee42174f7c54ae1121884243cc`。没有 weight setter 或 harmonic solve。

| 核心组件 | 结果 | 与 approved candidate 相同的 SHA256 |
|---|---|---|
| mesh_topology_UV_weights_rest_modifiers | EXACT_MATCH | `044dcbbc0c9ac0277729aaaa2e3d18883b2fb0a2bfff07fee7a9052177424854` |
| mesh_object_state | EXACT_MATCH | `026dd6cbe6f5f89270bcce05360cb412110b815c1dc460263b440bf5a1ebbcf8` |
| armature_complete | EXACT_MATCH | `8157a15b50e24eca1b870f7502d6b59de40c554f7e79ac7e3772a901c28a410c` |
| Basis_corrective_and_driver | EXACT_MATCH | `bd160aef46c8c34b4cd41caed9f53666a2cdedcf5020ea8f911fc027fff012a2` |
| materials_native | EXACT_MATCH | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` |
| native_shading | EXACT_MATCH | `19196f79bef37b259ff781addab0dfd5dccb8ccc1dd545762e1f6b2f54ff3adc` |
| mesh_edges_loops | EXACT_MATCH | `7baa4a2cb9a4653d4e49f8244cd6996140fab9c10c42858e9cb9659366f7bae5` |
| UV_layer_flags | EXACT_MATCH | `e5ebae25ec57c67d2c5232a3410c1777b77be4b057e0129cabc8d23ab349f7ef` |
| vertex_group_settings | EXACT_MATCH | `298d20d901ba9d82ed5f02dfa13f2ab95f54e47fd26f466bdac46ddb686342f4` |
| mesh_attributes | EXACT_MATCH | `9364a7eef4d6b4f3c69868d41e8b55994a6971ce9c84d1aa9c5a5093d5e205ac` |
| mesh_native_settings | EXACT_MATCH | `6482d384db12294e7c0e34f4daddcc03969313893363faf09d8b2f2824f3b1cd` |
| mesh_custom_properties | EXACT_MATCH | `44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a` |

armature 完整 payload 包括 21 bone names、parents、rest transforms、inherit settings、pose/rig constraints、bone collections 及原 driver/settings。其他验证包含 Basis、corrective 数据、UV、materials、native shading、modifiers、topology edges/faces/loops 与 group settings。只对白名单的产品身份 metadata 排除比较，其余产品字段没有豁免。

六个旧批准 pose 的定义直接继承且未改；没有重新渲染六姿态资格矩阵。Action compatibility = EXACT_MATCH，临时读取的 approved Action payload SHA256 为 `b03d02e4f9f4f624c6c3faf1c1c1d53d717eac4770a216d3b1f54af89672cdb0`。

## 最小 smoke check

只检查 ZERO、F130 和 FULL_OPP_L3（用于确认原 corrective 可自然参与），没有 210 帧或 421 observations 重验。

| 状态 | 结果 | candidate ↔ R2 最大求值位置差 mm | 原 corrective 自然值 |
|---|---|---:|---:|
| ZERO | PASS | 0.0 | 0.0 |
| F130 | PASS | 0.0 | 0.0 |
| FULL_OPP_L3 | PASS | 0.0 | 1.0 |

三状态全部对应点数值完全相同；NaN/Inf=0，ZERO restore=0.0 mm。成熟正常产品相机、lighting/shading 匹配图的像素也完全相同，未见新 packaging regression。

[Promotion smoke](../../../artifacts/59fbb08a49081db20d5d.md)

## Pointer 更新与新 freeze

仅在 identity、clean reopen 和 smoke 全部 PASS 后，将 `production_spec/RIGHT_HAND_PRODUCT_BASELINE.json` 原子更新为：

`PREVIOUS_PRODUCTION_BASELINE = R1`  
`CURRENT_PRODUCTION_BASELINE = R2`。

更新前 SHA256：`c4e92fc5d55217a9a7aa677b003a4a9055a91fcb9ff653af98ed3fddb68f786d`；更新后 SHA256：`bd5aafa012cbcfb81459c359d4ffc4164fb168aa00f744e5cd83b0def0e508cd`。旧 pointer 原始字节另存 PRODUCTION_POINTER_BEFORE_R1.json，供审计或经授权回滚。PRODUCTION_POINTER_UPDATE_R1.json 同时记录完整 before/after。

R2 已重新打开验证、以 ZERO 保存、无 active motion Action、无 audit objects，并设置 Windows read-only 文件属性（不影响文件 SHA）。R2_STATUS sidecar 与 pointer 同时记录 HUMAN_APPROVED_FROZEN、FIRST_WEB CLOSED、RIGHT_HAND_DEFORMATION CLOSED、STATIC_WEIGHT_FIELD_PROBLEM RESOLVED_IN_R2。

## 永久 fallback 与历史保护

R1 保留原路径 `production_spec/right_hand_product_baseline_r1/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1.blend`，新角色 **HISTORICAL_FROZEN_FALLBACK**，永久保留。

**R1_FALLBACK_SHA256 = `4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2`**，轮前轮后不变。R1 资产、原候选、所有旧 report / audit / review / JSON / matched evidence / approved sample / retarget source 均未改或删除。正式 role 更新只在新的 pointer/promotion record 中记录，不追改旧状态。

本轮写入的正式 .blend 只有新 R2 容器；R1 写入 0，approved candidate 写入 0，deformation mutation 0。没有新 bone/corrective/helper/cage/DQS，未开始左手、Three.js/Web export 或钢琴集成。

## 交付与停止

本报告、PROMOTION_IDENTITY_R1.json、PRODUCTION_POINTER_UPDATE_R1.json、FINAL_BASELINE_PROTECTION_R1.json、HUMAN_APPROVAL_BIND_R1.json、EVIDENCE_PROMOTION_SMOKE_R1.png 和新正式 R2 .blend 已完成。独立 R2 status 与原 pointer 的 byte-exact 备份一并保留。

**PROMOTION = PASS**  
**RIGHT_HAND_PRODUCT_BASELINE_R2 = HUMAN_APPROVED_FROZEN**  
**FIRST_WEB_HUMAN_VISIBLE_BLOCKER = CLOSED**  
**RIGHT_HAND_DEFORMATION_CLOSED = YES**  
**RIGHT_HAND_READY_FOR_LEFT_HAND_STAGE = YES**

**STOP — HUMAN REVIEW。等待下一阶段 Human 决策。**
