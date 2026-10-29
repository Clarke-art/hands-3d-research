# LEFT_HAND_PRODUCT_BASELINE_R1_PROMOTION_R1

2026-10-07 · **PROMOTION = PASS** · **LEFT_HAND_PRODUCT_BASELINE_R1 = HUMAN_APPROVED_FROZEN**

已根据本轮 Human 最终授权，将指定 SHA 的已批准左手候选升格为正式 R1。
仅更改 scene / mesh object 的审核身份元数据及 scene 容器名称；没有重新镜像或重建任何产品数据。
正式 .blend 重新打开后，13 类产品 payload 逐项精确一致，三个最小 smoke 全部通过，随后设置正式文件只读并创建左手 R1 指针。

## Q1–Q10

| 问题 | 检查 | 结果 |
|---|---|---|
| Q1 | Human-approved candidate SHA 匹配 | YES |
| Q2 | Candidate container | AUDIT_SCAFFOLDING_PRESENT |
| Q3 | 完整 weight field 与 candidate EXACT_MATCH | YES |
| Q4 | mesh / topology / UV / rig / rest / corrective / driver 一致 | YES |
| Q5 | NO_NEGATIVE_SCALE_RUNTIME_DEPENDENCY | YES |
| Q6 | ZERO / CMC_OPP_30 / FULL_OPP_L3 smoke 全部 PASS | YES |
| Q7 | 右手 R2 原 SHA 保持 | YES |
| Q8 | 右手 R1 fallback 原 SHA 保持 | YES |
| Q9 | 左手 production pointer 建立为 R1 | YES |
| Q10 | 左手 R1 = HUMAN_APPROVED_FROZEN | YES |

## Human 批准绑定与 container

Human 最终批准绑定至 `c31190de326c5af44baf876f4066a130c8a9fef42d6c71c0071de5f63f0f2750`，明确授权 promotion，确认六项批准姿态的可见外观 PASS。原文附件路径及其 SHA 记录于 HUMAN_APPROVAL_BIND_R1.json。

CANDIDATE_CONTAINER_STATUS = AUDIT_SCAFFOLDING_PRESENT，具体仅为待审身份标签及 candidate scene 名称。
只读检查发现：2 objects（mesh + armature），无 review/evidence camera、debug collection、comparison object、temporary Action 或 Text script。
因此采用 **CLEAN_PRODUCTION_CONTAINER_EXACT_PRODUCT_DATA**。

清理 DESIGN_ONLY、NOT_PRODUCTION、HUMAN_APPROVAL_PENDING、PRODUCTION_POINTER_UPDATED 等审核身份字段，设置正式产品批准身份。
scene 名称改为 LEFT_HAND_PRODUCT_BASELINE_R1。保留 CANONICAL_SOURCE、其 SHA、Official L1 source identity 等来源信息。
所有实际变更和明确排除的纯身份字段逐项记录在 PROMOTION_IDENTITY_R1.json；未删除任何产品 object、bone、modifier、shape key 或 driver。

## 精确产品身份验证

正式 R1 保持 3300 vertices、3298 faces、21 bone teaching rig（16 deform + 5 non-deform TIP）。
全部骨骼使用 *_L 语义。文件仍为 mesh + armature skin + bones + corrective morph，只有原有 ARMATURE modifier。
保存状态为 ZERO / RSSF，frame 1，无 Action、无约束或 mirror modifier 运行依赖；mesh/rig 均保持正 scale 与正行列式。

完整 **3300 × 21** weight semantics 逐值一致，最大差值 **0**；原始稀疏权重、vertex group 名称/索引/锁定设置也全部一致。
没有 normalize、weight rewrite、solver 或 repaint。weight vector SHA256：`88de68b7db5de12342ef1cd8ef72d9b7a206e41033d17f95342c33f1cf1de8de`。

| 产品组件 | candidate vs production | production payload SHA256 |
|---|---|---|
| mesh_object | EXACT_MATCH | `79f62bf6b96cac34d8a7d5363870f7eb45f92800c8e0771b3cecf63a931c5dcb` |
| armature_object | EXACT_MATCH | `abb3e6433c927df55e8db919b55d08ce25c645dec5bf0a1a3956128fdfb3a456` |
| mesh_identity | EXACT_MATCH | `f5cec216a45fc4bc25b6070aca08a54cbda1159c31699e0c9976158e962c25a1` |
| coordinates_vertex_order | EXACT_MATCH | `7222eaa82c701f06c56c2956b1030b490b278ba4da82d5b2961094873d077e43` |
| topology_face_winding | EXACT_MATCH | `290e7d806a0519d8b454906a40fee155a105d9cdf00aff0ee14b9c6e89aca50b` |
| UV | EXACT_MATCH | `d62b348b0ce18ca2305c58a6d1e70d932ee2411b09432fa189fff5ba9897c970` |
| native_shading | EXACT_MATCH | `dfafad638ad86ce8c3f4be05fd94110c85c330236a63c35f1b27e33e32a356f1` |
| attributes | EXACT_MATCH | `79530c172e9b952493e4774084a58f57c4ed4c729ab44fabbdf958fd2e56e69c` |
| groups_and_weights | EXACT_MATCH | `585a401798d22b4a6a6d6b5ccf569588cdfcab59bc60df94680766f91aa73870` |
| modifiers | EXACT_MATCH | `cde1825a71341f1b8e69cecbe554993b240b8bd0e953adb1cb1d32f8e20f345d` |
| rig_rest_and_semantics | EXACT_MATCH | `a198dbee09d08b4c96c46b966ca2f3dd31868941528bfb4006c86ad57304e620` |
| pose_state | EXACT_MATCH | `3fba05844b0c7a75a16e807e3a3d8933fc888ddc0197bf56e34a4da8b47ebe25` |
| corrective_geometry_and_driver | EXACT_MATCH | `c4939b7d39e3eff2c9cc994f24bf1d6bd75571d48260d9f8ad59b59ce2276e5c` |

rig rest 检查覆盖 head/tail、rest/local 矩阵与 local frames（含 roll 所决定的方向）、parent hierarchy、inherit/deform 设置、bone collections、角色及 pose state。
corrective 检查覆盖 shape key 坐标/相对基准、delta 所依赖的 Basis、driver expression、variables、target IDs/bones、FCurve 设置。所有比较为精确相等，无放宽误差阈值。
正式文件 SHA 与候选不同仅来自允许的容器/身份元数据清理和保存；产品 payload 未变。

## 最小 promotion smoke

仅使用上一阶段已批准的左手 pose matrices，在候选与重新打开的正式 R1 中分别应用。
未重新镜像、未重新定义姿态、未重复整个六项 Human qualification。

| 状态 | evaluated geometry 最大差值 mm | 正式 corrective 自然值 | trigger parity | ZERO restore mm |
|---|---:|---:|---|---:|
| ZERO | 0 | 0.000000000 | PASS | 0 |
| CMC_OPP_30 | 0 | 1.000000000 | PASS | 0 |
| FULL_OPP_L3 | 0 | 1.000000000 | PASS | 0 |

三项中 evaluated geometry、面连接/绕序、骨骼 pose matrices 与 corrective 值均为精确一致。
NaN/Inf、gross collapsed faces、degenerate edges 全部为 0；未产生新的 tearing。
明显 penetration 的依据为 Human 已批准候选 + 对应 evaluated surface 完全相同，不声称重新进行了视觉资格审查或 hidden crossing census。
因此没有生成重复截图；没有 hidden crossing、normal-dot、R3、true-cap 或逐顶点 anatomy forensic。
smoke 在未保存的测试会话中执行，磁盘正式文件维持 ZERO，SHA 在 smoke 前后相同。

## 正式指针与冻结

- 正式资产：`production_spec/left_hand_product_baseline_r1/LEFT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1.blend`
- LEFT_R1_BASELINE_SHA256：`54307bb199a75a5e684c29d346de9ca6bf2f8e7696911d9d69c57559516ad1a7`
- 正式文件只读：YES
- 指针：`production_spec/LEFT_HAND_PRODUCT_BASELINE.json`
- PREVIOUS_PRODUCTION_BASELINE = NONE
- CURRENT_PRODUCTION_BASELINE = R1
- LEFT_HAND_PRODUCT_BASELINE_R1 = HUMAN_APPROVED_FROZEN
- LEFT_HAND_CANONICAL_MIRROR = CLOSED
- LEFT_HAND_STATIC_DEFORMATION_BASELINE = CLOSED
- LEFT_HAND_READY_FOR_REAL_MOTION_STAGE = YES

SOURCE_CANONICAL_MASTER = RIGHT_HAND_PRODUCT_BASELINE_R2

MIRROR_SOURCE_SHA256 = c946fed318fa88c238d9aacc30cfb4e52f268848f0ad65a4dcbf594754d791f0

MIRROR_PLANE = WRIST rest-local X=0

MIRROR_SPACE = ARMATURE_DATA → MESH_DATA conjugation

这些来源记录是 sidecar/status 信息，不构成运行依赖。
原有 corrective driver 未来仍需 Web 转译；本轮没有 Web 导出、Three.js、真实 motion、retarget、MIDI、fingering 或钢琴安装。

## 原字节保护

共保护并复核 **90** 个文件，包括全部旧左手 audit/report/evidence/candidate、右手 R2/R1 目录文件及右手 production pointer。

RIGHT_R2_UNCHANGED = YES · `c946fed318fa88c238d9aacc30cfb4e52f268848f0ad65a4dcbf594754d791f0`

RIGHT_R1_UNCHANGED = YES · `4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2`

历史 DESIGN_ONLY / HUMAN_REVIEW_PENDING / READY_FOR_HUMAN_REVIEW 记录保留原字节；新批准仅写入本轮绑定记录。

**STOP — HUMAN REVIEW。未自动进入下一阶段。**
