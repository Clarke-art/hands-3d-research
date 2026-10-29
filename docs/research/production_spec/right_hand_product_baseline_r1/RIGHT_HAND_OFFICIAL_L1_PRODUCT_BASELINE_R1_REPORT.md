# RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1

**RIGHT_HAND_PRODUCT_BASELINE = PASS / HUMAN_APPROVED_FROZEN**

**REAL_PIANO_MOTION_CHECK = BLOCKED_MOTION_SOURCE_NOT_FOUND — STOP**

Human 明确批准上一阶段六个状态，原 first-web 尖折已消除，ZERO 与 INDEX 正常，opposition L1/L2/L3 可接受。当前独立 asset 完整保留该已批准的网格、21 骨骼、权重、UV/材质及 first-web corrective/driver。没有新增 geometry、weight 或 corrective 修改。

| 最终字段 | 结果 |
| --- | --- |
| OFFICIAL_L1_FIRST_WEB_TARGETED_DEFORMATION_FIX_R1 | HUMAN_APPROVED |
| RIGHT_HAND_BASELINE_SOURCE | audits/official_l1_first_web_targeted_deformation_fix_r1/RIGHT_HAND_OFFICIAL_L1_FIRST_WEB_TUNED_DESIGN_ONLY_R1.blend |
| RIGHT_HAND_BASELINE_ASSET | production_spec/right_hand_product_baseline_r1/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1.blend |
| RIGHT_HAND_BASELINE_SHA256 | 4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2 |
| OFFICIAL_L1_MESH_PRESERVED | YES_EXACT |
| MESH_VERTEX_COUNT | 3300 |
| BONE_COUNT | 21 |
| ZERO_VISUAL_STATUS | PASS_HUMAN_APPROVED_SOURCE_IDENTICAL_BASELINE |
| FIRST_WEB_FIX_PRESERVED | YES_EXACT_WEIGHTS_CORRECTIVE_DRIVER |
| VISIBLE_PRODUCT_BLOCKER_COUNT | 0 |
| NEW_VISIBLE_DEFECT_COUNT | 0 |
| FILE_CLEAN_REOPEN | PASS |
| NaN_Inf | 0 |
| ZERO_RESTORE | PASS |
| CORRECTIVE_VALUE_AT_ZERO | 0.0 |
| GEOMETRY_REPAIR_COUNT | 0 |
| WEIGHT_TUNING_COUNT | 0 |
| NEW_CORRECTIVE_COUNT | 0 |
| REAL_PIANO_MOTION_SOURCE | NOT_FOUND |
| MOTION_SOURCE_TYPE | NONE |
| RETARGET_EXECUTED | NO |
| MOTION_CASES_COVERED | [] |
| GROSS_DEFORMATION_FAILURE_COUNT | NOT_EVALUATED |
| REAL_PIANO_MOTION_VISIBLE_STATUS | NOT_EVALUATED_MOTION_SOURCE_NOT_FOUND |
| RIGHT_HAND_PRODUCT_BASELINE | PASS |
| RIGHT_HAND_PRODUCT_BASELINE_STATUS | HUMAN_APPROVED_FROZEN |
| RIGHT_HAND_PRODUCT_BASELINE_R1 | HUMAN_APPROVED_FROZEN |
| REAL_PIANO_MOTION_CHECK | BLOCKED_MOTION_SOURCE_NOT_FOUND |
| REAL_PIANO_MOTION_PRODUCT_CHECK_R1 | BLOCKED_MOTION_SOURCE_NOT_FOUND |
| LEGACY_ENGINEERING_MESH_STATUS | LEGACY_ENGINEERING_REFERENCE_ONLY |
| LEFT_HAND_STARTED | NO |
| WEB_EXPORT_STARTED | NO |
| VERDICT | BASELINE_FROZEN_MOTION_CHECK_BLOCKED_SOURCE_NOT_FOUND |
| STOP | STOP — MOTION SOURCE NOT FOUND |
| NEXT | Find an existing piano hand motion source in a separate task. |

## Human approval 与来源绑定

来源 candidate SHA256：`783a1b8fe414298cb442aa94d72161a3b2f3d5a95c39a341a6885e943e6dea1b`。核对上一阶段最终输出清单中 60 个证据文件的 SHA256 全部相符，candidate 与 review/render evidence 绑定一致。直接用户指令的批准记录保存在 [SOURCE_HUMAN_APPROVAL_BIND_R1.json](../../../artifacts/bb05488147869321cc29.md)，并添加上一阶段的 [Human approval sidecar](../../../../examples/historical/audits/official_l1_first_web_targeted_deformation_fix_r1/HUMAN_APPROVAL_BIND_R1.json)。历史 preliminary report/status 和历史证据保持原样，其 HUMAN_PENDING 状态由该明确批准记录取代。

## 独立产品基线

[RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1.blend](../../../artifacts/3e0dd33b51d3b9fa88c0.md)，SHA256 `4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2`，保存姿态 ZERO / RSSF。

本轮只修改新文件中的产品角色 / Human approval 元数据，解除 DESIGN_ONLY 标记。3300 个原生顶点 / 3298 面、全部权重/组、骨架 rest 与 joint layout、UV、材质、两个 shape keys（Basis + 原 corrective）、一个 driver 及其表达式/变量/target 均与 source 逐项相同。16 deform bones，5 non-deform TIP helpers；ZERO corrective = 0。clean reopen PASS；source 与 baseline ZERO 求值差 = 0 mm；NaN/Inf = 0。仅对已批准的 FULL_OPP_L3 做一次直接 round trip 确认 driver 能激活并恢复 ZERO，恢复差 = 0 mm；不重开 Stage6 资格矩阵。

ZERO 普通 palmar/dorsal/thenar 实体图观察正常。来源 Human acceptance 与保存重开后逐项相同的 payload 共同支持当前基线的批准继承，未把新 motion acceptance 混入其中。

当前产品资产权威指针：[production_spec/RIGHT_HAND_PRODUCT_BASELINE.json](../../../../examples/historical/production_spec/RIGHT_HAND_PRODUCT_BASELINE.json)。新的路线说明：[RIGHT_HAND_PRODUCT_BASELINE_AUTHORITY_R1.md](../../docs/RIGHT_HAND_PRODUCT_BASELINE_AUTHORITY_R1.md)。此前 3416 顶点 engineering mesh 降为 LEGACY_ENGINEERING_REFERENCE_ONLY。历史文件没有删除或覆盖。

## 本地 motion source 搜索

按照授权顺序搜索本 hand workspace、references、相邻 piano 项目、项目历史说明、Downloads，以及已知 Desktop/Documents/D:/codex/D:/workbuddy 中具有钢琴手部 motion 特征的文件名。52 个既有 hand workspace `.blend` 通过只读 library datablock-name 检查，全部 Actions = 0；没有 mesh 求值、形变审计或保存。这是 motion 数据发现，不是旧 forensic 重跑。

命中的预览 GIF / manifests 只是 ZERO→单关节或 opposition stress pose 的 quaternion slerp。唯一 hand 项目 NPZ 存储早期局部研究的 A/Z 静态矩阵。相邻 piano 项目中的 motion replay 控制琴键、hammer/butt pivot 等机械件；demo.mid 是音符事件，既无 wrist/finger joints 的旋转或位置通道，也不能直接 retarget 到当前21骨骼手。已有钢琴视频是拆机/击弦机结构参考，没有现成手部运动通道。Downloads 未发现 motion 格式候选。

因此 REAL_PIANO_MOTION_SOURCE = NOT_FOUND；RETARGET_EXECUTED = NO；MOTION_CASES_COVERED = []。没有造新 keyframes、动作库或 MIDI-to-hand 系统，没有联网寻找/下载替代 motion。没有可评审的真实动作，故不生成伪装为真实 motion 的 mp4。GROSS_DEFORMATION_FAILURE_COUNT = NOT_EVALUATED（JSON 为 null），不能写成 0 或判 motion PASS。

完整本地范围、命中文件和排除理由：[REAL_PIANO_MOTION_SOURCE_AUDIT_R1.json](../../../../examples/historical/production_spec/right_hand_product_baseline_r1/REAL_PIANO_MOTION_SOURCE_AUDIT_R1.json)。这不是全磁盘不存在的证明，只是在已搜索的项目/下载范围内未找到可用来源。

## 最低检查与停止点

[BASELINE_FREEZE_VERIFICATION_R1.json](../../../../examples/historical/production_spec/right_hand_product_baseline_r1/BASELINE_FREEZE_VERIFICATION_R1.json)；[LOCAL_BLEND_MOTION_INVENTORY_R1.json](../../../../examples/historical/production_spec/right_hand_product_baseline_r1/LOCAL_BLEND_MOTION_INVENTORY_R1.json)。没有 hidden crossing census、normal-dot、true-cap、R3、整手修补或细微不可见优化。LEFT_HAND_STARTED = NO；WEB_EXPORT_STARTED = NO。

**基线冻结成功；真实钢琴 motion 检查单独 BLOCKED。STOP — MOTION SOURCE NOT FOUND。下一步只记录为专门寻找现成手部 motion source。**
