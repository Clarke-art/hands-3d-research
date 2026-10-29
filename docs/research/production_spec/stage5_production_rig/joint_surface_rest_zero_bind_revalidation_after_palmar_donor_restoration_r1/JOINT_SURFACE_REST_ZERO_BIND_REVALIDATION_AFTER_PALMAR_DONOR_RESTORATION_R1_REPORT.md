# JOINT_SURFACE_REST_ZERO_BIND_REVALIDATION_AFTER_PALMAR_DONOR_RESTORATION_R1

PASS_JOINT_REST_ZERO_BIND_REQUALIFIED。只读复核完成，STOP。

新 Stage5A、新 Stage5B R2 与最新 Human-approved dorsal54 + palmar16 Stage4C 的完整 3416 local/world raw coordinates 精确一致，两份 Stage5 bone payload 精确一致。实际输入哈希均与指定 authority 匹配。所有 21 joint/helper 都在当前新表面 fresh 测量；16 deform heads required-inside 全部 64/64 inside，5 non-deform TIP helpers 与全部区域规则通过。Actual evaluated ZERO surface 的 21 项交叉检查也通过。

## Authority 与语义

沿用此前成功 donor-transfer revalidation 的 R2/R2A / freeze / errata / Human corrected thumb 优先级，并 fresh 读取与核对其 source hashes。Wrist 使用冻结 transition band，THUMB_CMC 使用已批准 CMC locality sphere，MCP/PIP/DIP 使用 T-01 frozen axial frame/zone。四指 TIP 使用 accepted own-digit face/surface/apex 规则；corrected THUMB_TIP 使用 native terminal v284，旧 cap REP 规则已 superseded。TIP 不执行 deform-inside gate。没有 anatomy、locator、CMC cage、cap、ownership 或 joint fitting 重算。

正式 parity/closest、ZERO reset/evaluate 仅 AST 复用历史函数，无历史 audit/builder 顶层执行。ZERO procedure 为 21 quaternion identity / location zero / scale one，仅临时内存，不保存。源代码明确确认当前 R2 `raw_RSSF_noise_mm <= 1e-4 mm`，Stage5B R1/R1B 亦使用 0.0001mm 门槛；本轮未发明阈值。

## MIDDLE_MCP head / tail

历史 diagnostic fan-BVH 方法独立 fresh 重现：head old **6.136777810752392 mm** → new **6.501595489680767 mm**，delta **+0.36481767892837524 mm**。

正式 frozen Blender native polygon 方法独立成对计算：old **6.136752534888991 mm** → new **6.501595510988015 mm**，delta **+0.36484297609902416 mm**。两种方法的旧值差异来自 fan/native polygon tessellation 与数值空间；禁止把一套旧值与另一套新值相减。报告的正式 joint delta ranking 使用后一方法，最大变化 joint 仍为 MIDDLE_MCP_R；其余 20 head delta 均为 0。

Nearest native face **2783 → 2421**：旧 face 包含 palmar16 的 3360 / 3353，新 face 为 1024 / 125 / 1938 / 3085。Head 64/64 inside，negative signed relation；T-01 MCP axial projection 0mm，approved center 0mm，half-width / margin **9.149mm**，区域 PASS。局部 palmar16 proximity 与 native feature 详见专项 JSON。该距离增量不是 fail threshold，也不要求 joint relocation。

Tail 与 MIDDLE_PIP_R head 精确相同，两种方法的 old/new nearest distance delta 均为 0，64/64 inside，冻结 PIP region PASS。Tail 不被误套 MCP head zone；完整 head/tail 独立报告。全部 42 endpoints 排序与 palmar16 最近 joint/helper 排序已输出，INDEX_MCP / RING_MCP / WRIST 明确列入 focus。

## Rest / ZERO / bind

两份新 Stage5 对各自 propagation source：21 bones 的 names/order、parents/children、head/tail、actual native roll、rest/local matrices、use_deform / inherit / connect flags、完整 mesh/armature object transforms 精确一致。Corrected THUMB_IP / TIP chain frozen。Native EditBone.roll 在临时会话最后只读，无 setter、mode exit 或保存。REST_RIG_PAYLOAD_MATCH PASS。

Clean reopened actual Stage5B R2 Armature ON + formal ZERO：21 matrix_basis exact identity，pose-rest matrix residue 0，NaN/Inf、missing bones/groups/modifier target 和 pose residue 均 0。Full 3416-point raw→evaluated max **5.967009246215726e-05mm**，mean **6.011309139736792e-06mm**，RMS **1.042224028458749e-05mm**，P95 **2.986047331594191e-05mm**；超出 recovered 0.0001mm gate 的点 **0**；max vertex ID **2153**。

Corrected THUMB terminal 的 stored raw exact native-v284 authority PASS。其 evaluated ZERO native-terminal noise 为 0.000003725290298461914mm，按 recovered bind tolerance 处理。补充脚本初稿曾把 raw exact equality 用于 evaluated geometry，现已修正其实现适用范围；没有 joint、geometry 或阈值改动。该数值不得误判为 geometry write。所有 21 evaluated-zero surface/region cross-check PASS。

Modifier target/order/settings、groups/order、每个 weight scalar 含零、deform mapping、mesh/armature transforms 与旧 R2 精确一致。完整 3416 weight-vector hash **1d9437a10354cdd98a2b5cb5e43be8cfabc519e232235483a615e76898129f55**。实际 Blender Armature modifier 无独立用户 bind matrix；沿用其 object/rest mapping，记录已有 matrix_parent_inverse，无 rebind / inverse-bind recompute。

## 掌侧与 dorsal / normal69

27 张实际 fresh matched renders：掌侧 6 rows × 3 columns，dorsal sentinel 3 rows × 3 columns。掌侧覆盖 Human confirmed camera solid、close solid、alternate solid、grazing、flat/source-native、wire。同一 row 三列 camera/light/material/scale 相同，坐标源为 latest Stage4C RAW / new Stage5B RAW / actual evaluated ZERO。已由 Codex 直接检查 contact sheets：hard shelf/dent 未回返，natural crease PRESERVED，未观察到新 ridge、notch、collapse 或 boundary discontinuity。这仅证明现有 Human-approved geometry 的 ZERO preservation，不生成新 Human closure 或 acceptance。

Dorsal54 regression sentinel PASS；normal69 raw coordinates exact Stage4C，evaluated ZERO 全部 within formal gate。三类区域 incident native triangles 零面积与方向反转数均 0，面积比仅记录为补充 contour 数值支持，无新增 skin gate。所有 rendered Stage4C→Stage5B RAW 像素精确一致；RAW→ZERO pixel difference 单列。

## Current9、历史与 NEXT

两份实际 Stage5 native ID/topology fresh recheck：palmar16/current9 direct / 1-ring / 2-ring **0 / 0 / 0**。Current9 **HOLD_NOT_CLOSED**，answer/closure/acceptance 无写入。已 hash 核对 **5277** 个受保护 pre-existing files，漂移 **0**。本轮新产物仅位于本目录，blend 保存 **0**。

JOINT_RELOCATION_REQUIRED=NO；RIG_REBUILD_REQUIRED=NO；WEIGHT_CHANGE_REQUIRED=NO。STATIC_SKIN_REQUALIFICATION=NOT_RUN；MID_MCP_45_MANDATORY_REVALIDATION=YES；WHOLE_HAND_SURFACE_INTEGRITY_BASELINE_REQUIRED=YES。

NEXT=`STATIC_SKIN_COMPATIBILITY_REVALIDATION_AFTER_PALMAR_DONOR_RESTORATION_R1`，只记录，未执行。后续顺序：static skin compatibility → geometry-dependent authority impact audit → palmar targeted MID15/30/45（45 mandatory）→ fresh FullStage6A42 → Human visual review → current9 closure resume → whole-hand surface integrity baseline → 之后才考虑 Stage6B。本轮未执行任何非零 pose、skin continuity、R3、true-cap、Full42、Stage6B 或 promotion。

## 全部最终字段

| Field | Value |
|---|---|
| phase | "JOINT_SURFACE_REST_ZERO_BIND_REVALIDATION_AFTER_PALMAR_DONOR_RESTORATION_R1" |
| recorded_at_Asia_Shanghai | "2026-10-06T13:16:38.817056+08:00" |
| STAGE5A_INPUT_HASH_VERIFIED | "PASS" |
| STAGE5B_INPUT_HASH_VERIFIED | "PASS" |
| FORMAL_JOINT_HELPER_COUNT | 21 |
| FORMAL_JOINT_HELPER_PASS_COUNT | 21 |
| ALL_REQUIRED_INSIDE_JOINTS | "PASS" |
| REQUIRED_INSIDE_JOINT_FAILURE_COUNT | 0 |
| TIP_HELPER_FAILURE_COUNT | 0 |
| JOINT_REGION_FAILURE_COUNT | 0 |
| MAX_JOINT_SURFACE_DISTANCE_DELTA_MM | 0.36484297609902416 |
| MAX_JOINT_SURFACE_DISTANCE_DELTA_JOINT | "MIDDLE_MCP_R" |
| MAX_JOINT_SURFACE_DISTANCE_DELTA_METHOD | "Formal current frozen Blender native polygon closest, paired old/new" |
| MIDDLE_MCP_R_HEAD_OLD_SURFACE_MM | 6.136777810752392 |
| MIDDLE_MCP_R_HEAD_NEW_SURFACE_MM | 6.501595489680767 |
| MIDDLE_MCP_R_HEAD_DELTA_MM | 0.36481767892837524 |
| MIDDLE_MCP_R_HEAD_REPORTED_DISTANCE_METHOD | "Historical diagnostic native fan BVH, independently fresh reproduced; do not mix with formal polygon method" |
| MIDDLE_MCP_R_HEAD_FORMAL_OLD_SURFACE_MM | 6.136752534888991 |
| MIDDLE_MCP_R_HEAD_FORMAL_NEW_SURFACE_MM | 6.5015955109880155 |
| MIDDLE_MCP_R_HEAD_FORMAL_DELTA_MM | 0.36484297609902416 |
| MIDDLE_MCP_R_HEAD_NEAREST_FACE_BEFORE | 2783 |
| MIDDLE_MCP_R_HEAD_NEAREST_FACE_AFTER | 2421 |
| MIDDLE_MCP_R_INSIDE_STATUS | "PASS" |
| MIDDLE_MCP_R_INSIDE_VOTES | "64/64" |
| MIDDLE_MCP_R_REGION_STATUS | "PASS" |
| MIDDLE_MCP_R_T01_MARGIN_MM | 9.149 |
| CORRECTED_THUMB_CHAIN_PRESERVED | "PASS" |
| BONE_PAYLOAD_DELTA | 0 |
| JOINT_PAYLOAD_DELTA | 0 |
| JOINT_HEAD_DELTA_MM | 0 |
| JOINT_TAIL_DELTA_MM | 0 |
| ROLL_DELTA | 0 |
| REST_MATRIX_DELTA | 0 |
| BONE_HIERARCHY_DELTA | 0 |
| OBJECT_ARMATURE_TRANSFORM_DELTA | 0 |
| REST_RIG_PAYLOAD_MATCH | "PASS" |
| ZERO_POSE_REVALIDATION | "PASS" |
| RAW_TO_BIND_MAX_DELTA_MM | 5.9670092462157264e-05 |
| RAW_TO_BIND_MEAN_DELTA_MM | 6.011309139736792e-06 |
| RAW_TO_BIND_RMS_DELTA_MM | 1.0422240284587488e-05 |
| RAW_TO_BIND_P95_DELTA_MM | 2.9860473315941913e-05 |
| RAW_TO_BIND_OUT_OF_TOLERANCE_COUNT | 0 |
| MAX_DELTA_VERTEX_ID | 2153 |
| RAW_TO_BIND_POINT_COUNT | 3416 |
| RECOVERED_FORMAL_ZERO_GATE_MM | 0.0001 |
| BIND_ZERO | "PASS" |
| PALMAR_ROOT_DENT_REAPPEARED_AT_BIND_ZERO | "NO" |
| PALMAR_ROOT_NATURAL_CREASE_BIND_ZERO | "PRESERVED" |
| PALMAR_ROOT_NEW_BIND_VISIBLE_DEFECT | "NONE" |
| DORSAL54_BIND_ZERO_REGRESSION | "PASS" |
| NORMAL69_RAW_COORD_MATCH | "PASS" |
| NORMAL69_ZERO_WITHIN_FORMAL_GATE | "PASS" |
| MODIFIER_BINDING | "PASS" |
| R2_WEIGHT_HASH | "1d9437a10354cdd98a2b5cb5e43be8cfabc519e232235483a615e76898129f55" |
| R2_WEIGHT_HASH_MATCH | "PASS" |
| CURRENT9_DIRECT_OVERLAP | 0 |
| CURRENT9_1RING_OVERLAP | 0 |
| CURRENT9_2RING_OVERLAP | 0 |
| CURRENT9_HUMAN_RESPONSE | "HOLD_NOT_CLOSED" |
| JOINT_RELOCATION_REQUIRED | "NO" |
| RIG_REBUILD_REQUIRED | "NO" |
| WEIGHT_CHANGE_REQUIRED | "NO" |
| STATIC_SKIN_REQUALIFICATION | "NOT_RUN" |
| MID_MCP_45_MANDATORY_REVALIDATION | "YES" |
| WHOLE_HAND_SURFACE_INTEGRITY_BASELINE_REQUIRED | "YES" |
| TRUE_CAP_RECOMPUTATION | "NOT_RUN" |
| R3_RERUN | "NOT_RUN" |
| NONZERO_POSE_EVALUATIONS | 0 |
| FULL42 | "NOT_RUN" |
| STAGE6B | "NOT_RUN" |
| PRODUCTION_PROMOTION | "NO" |
| PROTECTED_HISTORY_DRIFT | 0 |
| PROTECTED_FILE_COUNT | 5277 |
| BLEND_SAVES | 0 |
| VERDICT | "PASS_JOINT_REST_ZERO_BIND_REQUALIFIED" |
| NEXT | "STATIC_SKIN_COMPATIBILITY_REVALIDATION_AFTER_PALMAR_DONOR_RESTORATION_R1" |
| NEXT_EXECUTED | false |
| STOP | true |

## 逐项 fresh formal surface qualification

| Joint/helper | Type | Inside votes | Old mm | New mm | Delta mm | Region/helper | Final |
|---|---|---|---|---|---|---|---|
| WRIST_R | DEFORM_JOINT_HEAD | 64/64 | 18.901024821950 | 18.901024821950 | +0.000000000000 | PASS | PASS |
| THUMB_CMC_R | DEFORM_JOINT_HEAD | 64/64 | 12.000322775338 | 12.000322775338 | +0.000000000000 | PASS | PASS |
| THUMB_MCP_R | DEFORM_JOINT_HEAD | 64/64 | 9.484081825788 | 9.484081825788 | +0.000000000000 | PASS | PASS |
| THUMB_IP_R | DEFORM_JOINT_HEAD | 64/64 | 6.217311453779 | 6.217311453779 | +0.000000000000 | PASS | PASS |
| THUMB_TIP_R | NON_DEFORM_TIP_HELPER | N/A | 0.000000000000 | 0.000000000000 | +0.000000000000 | PASS | PASS |
| INDEX_MCP_R | DEFORM_JOINT_HEAD | 64/64 | 5.866985152818 | 5.866985152818 | +0.000000000000 | PASS | PASS |
| INDEX_PIP_R | DEFORM_JOINT_HEAD | 64/64 | 6.102529535507 | 6.102529535507 | +0.000000000000 | PASS | PASS |
| INDEX_DIP_R | DEFORM_JOINT_HEAD | 64/64 | 5.067485656259 | 5.067485656259 | +0.000000000000 | PASS | PASS |
| INDEX_TIP_R | NON_DEFORM_TIP_HELPER | N/A | 0.254003730340 | 0.254003730340 | +0.000000000000 | PASS | PASS |
| MIDDLE_MCP_R | DEFORM_JOINT_HEAD | 64/64 | 6.136752534889 | 6.501595510988 | +0.364842976099 | PASS | PASS |
| MIDDLE_PIP_R | DEFORM_JOINT_HEAD | 64/64 | 6.624789635874 | 6.624789635874 | +0.000000000000 | PASS | PASS |
| MIDDLE_DIP_R | DEFORM_JOINT_HEAD | 64/64 | 5.965571830187 | 5.965571830187 | +0.000000000000 | PASS | PASS |
| MIDDLE_TIP_R | NON_DEFORM_TIP_HELPER | N/A | 0.241906763412 | 0.241906763412 | +0.000000000000 | PASS | PASS |
| RING_MCP_R | DEFORM_JOINT_HEAD | 64/64 | 5.587250661216 | 5.587250661216 | +0.000000000000 | PASS | PASS |
| RING_PIP_R | DEFORM_JOINT_HEAD | 64/64 | 6.212428845067 | 6.212428845067 | +0.000000000000 | PASS | PASS |
| RING_DIP_R | DEFORM_JOINT_HEAD | 64/64 | 5.085878235091 | 5.085878235091 | +0.000000000000 | PASS | PASS |
| RING_TIP_R | NON_DEFORM_TIP_HELPER | N/A | 0.232069763992 | 0.232069763992 | +0.000000000000 | PASS | PASS |
| LITTLE_MCP_R | DEFORM_JOINT_HEAD | 64/64 | 4.749688023336 | 4.749688023336 | +0.000000000000 | PASS | PASS |
| LITTLE_PIP_R | DEFORM_JOINT_HEAD | 64/64 | 5.132156843468 | 5.132156843468 | +0.000000000000 | PASS | PASS |
| LITTLE_DIP_R | DEFORM_JOINT_HEAD | 64/64 | 4.001341479859 | 4.001341479859 | +0.000000000000 | PASS | PASS |
| LITTLE_TIP_R | NON_DEFORM_TIP_HELPER | N/A | 0.213540843921 | 0.213540843921 | +0.000000000000 | PASS | PASS |

复现顺序：prepare.py → recover_semantics.py → Blender revalidate.py → Blender supplement.py → build_visual_tools.py → Blender render_palmar.py / render_dorsal.py → prepare_evidence.py → direct image inspection → deliver.py → validate_delivery.py。只读 native 查询副本与 display meshes 在内存创建；唯一 pose 操作为 frozen ZERO procedure。

[Matched review](../../../../artifacts/48d264cd27d8c797f49e.md)。STOP。
