# HUMAN_CAP_AUTHORITY_FREEZE_R1

**THUMB_DISTAL_CAP_CANONICAL_AUTHORITY_R1 = HUMAN_APPROVED_FROZEN**。当前 canonical surface membership 直接冻结自 Human-approved E_FINAL：37 vertices / 25 faces。Combined authority SHA-256：`c81dd96d6925ed402cdf0ba44c148d7a78c2c60640fe23fb6247fb729f346cc8`。本轮完成文档 authority freeze；没有写入 Blender、weight vector 或 downstream authority。NEXT = **CAP_DEPENDENCY_BLAST_RADIUS_AUDIT_R1**，尚未开始。

## 唯一正确 Human input

来源：`<USER_HOME>\Downloads\HUMAN_CAP_BOUNDARY_E_FIVE_VERTEX_RESPONSE_R1 (1).json`。按 review、全部答案、notes、四个布尔状态及精确 recorded_at 内容筛选，不按 filename 选择。原文件 SHA-256：`8e41e5bc79bb06239cba7346f4017c972e024a1629bc237683a06d02ca5efe4f`，新目录逐字节副本 `HUMAN_FINAL_FREEZE_RESPONSE_SOURCE_COPY.json`。

review=CAP_BOUNDARY_E_FIVE_VERTEX_ADJUDICATION_R1；recorded_at=2026-10-02T13:16:50.749Z；Q1/Q2/Q3=REMOVE，Q4/Q5=KEEP，Q6=YES，Q7=APPROVE_FOR_FREEZE；matches_presented_E_FINAL=true；selected_E_FINAL_membership_changed=false；production_authority_applied=false；authority_freeze_performed=false。后两个字段是**批准输入导出时的历史状态**，原文不回写；本轮新增 canonical freeze 状态。

Human notes 原文：

> Human Review：接受五点裁决。v1453、v2785、v2790 REMOVE；v297、v298 KEEP。E_FINAL 保持 Candidate E 的 37 vertices / 25 faces 不变，单连通、单闭环、manifold、nail-compatible，当前五点范围内无 proximal overreach、无局部 spike/notch。批准 E_FINAL 进入 HUMAN_CAP_AUTHORITY_FREEZE；本次批准仅针对新的 thumb distal-cap membership，不自动批准任何下游 R3、skin weight 或 Stage6 结果。

较早同名 response（recorded_at=2026-10-02T13:12:58.997Z、Q4=REMOVE、matches_presented_E_FINAL=false）标记为 SUPERSEDED_HUMAN_RESPONSE。未将其用作 authority，也未覆盖原件。完整选择/排除谓词、路径、哈希和 notes 位于 HUMAN_RESPONSE_AUTHORITY_SELECTION.json。

## Freeze 前核验

已读取上一轮 candidate、topology audit、完整 report、Human response。candidate hash 与上一轮 OUTPUT_VERIFICATION.json 匹配：`f72a7a9c5cc124c7c2e13eb29340e524aa5d226eb473e6d205b38de80b66d541`；audit/report 等上一轮 outputs 也与已记录 hash 一致。此前冻结历史输入仍匹配上一轮记录，本轮开始/结束保护快照均通过。

26 项输入 gates 全部 PASS。E_FINAL 37/25；1453/2785/2790 不在 membership，297/298 在 membership；single connected patch=YES，single closed boundary=YES，manifold=YES，non-manifold incidence=0，nail-compatible=YES，proximal overreach=NO，local spike/notch=NO，region identity=ACCEPTED_UNCHANGED。后两项视觉/解剖结论承接精确匹配的 Human E_FINAL approval 与上一轮限定五点 audit，未重新研究其它区域。

仅验证已选固定 patch 的 native face-corner union、edge incidence、vertex-link manifold、连通性、Euler=1 及既有 boundary loop；没有生成/优化 boundary。所有 membership 与 E_FINAL 完全一致。Loop 直接采用既有 audit：

`[36, 879, 37, 1340, 283, 1382, 341, 1454, 298, 1380, 340, 1452, 297, 1378, 339, 1450, 285, 1344, 44, 890, 2499, 880, 36]`

22 boundary edges、22 boundary vertices；loop start/end v36。Native/pre-RSSF geometry SHA-256：`4fa2cb6f31d8097110718e4d9cc424c30d1d2b7057c76abd93c338a5c7201039`。全部 37 点在冻结 independent native THUMB partition 内，独立 terminal-tip seed=v284。没有重新决定 seed、跑 9 mm selector 或新增删除任何 membership。

## Canonical semantics and deterministic hashes

Canonical source：THUMB_DISTAL_CAP_CANONICAL_AUTHORITY_R1.json。完整保存 vertex、face、boundary edge ID/端点、boundary vertex 及闭环拓扑顺序。Authority = **EXPLICIT FROZEN MEMBERSHIP SET**；9 mm min-corner convention 仅是早期 48-point/33-face candidate-generation provenance，绝不成为未来重算同名 authority 的规则，也不意味着最终 37 点全在 9 mm 内。

固定 serialization：UTF-8，JSON keys 字典序，compact separators，ensure_ascii=false，allow_nan=false，无 BOM/尾随换行；hash payload 数值仅整数。vertices/faces/boundary vertex IDs 升序；edge IDs 升序，与对应 native endpoint pairs 同步排序；loop 完全保留既有 audit 拓扑顺序，不重选方向。

| Hash | SHA-256 |
|---|---|
| Vertex membership | `3658481ff79d9cb4c03b404248a6e8e9f8b2a12e4a776c9f169cbe260e779cba` |
| Face membership | `5cf21d32c79a041de60681acd5727f104e625fe1fe39280589b7bd2c1920dd21` |
| Boundary | `6847d081e19f72641444894374f7890e55e781785d678d415c7d3565206d5fca` |
| Combined authority | `c81dd96d6925ed402cdf0ba44c148d7a78c2c60640fe23fb6247fb729f346cc8` |

Combined digest 覆盖 authority JSON 的全部字段，唯一排除 self-field combined_authority_hash。CAP_AUTHORITY_CANONICAL_PAYLOAD.json 保存精确 hash bytes；CAP_AUTHORITY_FROZEN_MEMBERSHIP_HASH.json 定义四个 payload。Authority JSON 格式化文件本身另有 byte hash 在 FREEZE_OUTPUT_VERIFICATION.json；它与 combined canonical hash 的用途区分明确。后续 Stage5/Stage6 rebuild 必须验证 combined 及 membership hashes；mismatch=FAIL_CLOSED，不能重新 selector 或默默映射 ID 仍称同一 authority。

## Approval/provenance chain

1. MANUAL_ANATOMICAL_REFERENCE_REVIEW_R1：原始 anatomical/manual reference responses，保留 Q2/Q3 unresolved、Q4 NO、Q5 LIMITED。
2. HUMAN_CAP_AUTHORITY_CORRECTION_R1：native v284、THUMB/distal region identity 接受，要求 boundary review。
3. THUMB_DISTAL_CAP_BOUNDARY_REVIEW_R1：E selected baseline，只允许五点 narrow review。
4. CAP_BOUNDARY_E_FIVE_VERTEX_ADJUDICATION_R1：唯一正确最终 response，三 REMOVE/二 KEEP、boundary YES、APPROVE_FOR_FREEZE。

CAP_AUTHORITY_PROVENANCE_CHAIN.json 逐项记录原始 path/hash、逐字 response、copy、authority effect；native extraction/branch、48-point candidate、E、E_FINAL、历史 audit sources 的 hashes 一并记录。早期 response 不回写为已冻结。

## Old cap9 supersession and historical preservation

旧 IDs `[151, 158, 1061, 1074, 1076, 2189, 2192, 2569, 2577]`，独立 native audit = 9/9 INDEX_SURFACE。OLD_THUMB_DISTAL_CAP_9=SUPERSEDED_INVALID_ANATOMICAL_MEMBERSHIP；OLD_CAP9=SUPERSEDED_CONTAMINATED。历史 Stage5A R2A THUMB_DISTAL_CAP_AUDIT.json 及 R1/R1A/R1B/R1C/R1D/R1E 文件/旧 blends 均保留 byte-identical。仅新增 OLD_CAP9_SUPERSESSION_RECORD.json，不删除或重写历史证明。旧 9 mm method 声明仅就当前 THUMB membership 被新显式 authority supersede；其它 digit/landmark authority 不变。

## Downstream states and strict-bound evidence

DIGIT_OWNERSHIP_AUTHORITY_R3 = **HISTORICALLY_HUMAN_APPROVED / REVALIDATION_REQUIRED_AFTER_CAP_AUTHORITY_CORRECTION**。THUMB_STRONG 曾继承错误 cap9，因此需后续 revalidation；不宣告 R3 INVALID，也不宣告仍 fully qualified，历史 R3 文件不回写。

Stage5B R1B 保留 **FROZEN HISTORICAL PRODUCTION MASTER**；cap-dependent skin semantics 需 dependency audit，未重建。R1C/R1D/R1E 历史文件和 verdict 原样保留，只在新上层 artifact 增加 DOWNSTREAM_CAP_DEPENDENT_REVALIDATION=REQUIRED；未重新评价 PASS/FAIL。

13.1646 mm path = INVALIDATED AS TRUE_THUMB_CAP→COLLAR ANATOMICAL ENDPOINT EVIDENCE；CMC_MCP_L3 5.9643 和 FULL_OPP_L3 6.5160 = INVALIDATED AS TRUE_THUMB_CAP ENDPOINT BOUND。固定历史 mesh 数值事实保留，不删除、不重算。新 true-cap bounds = PENDING_RECOMPUTE_AFTER_DEPENDENCY_RECONCILIATION。

CAP_WEIGHT_AUTHORITY=NOT_YET_RECONCILED。旧 cap9 的 THUMB_IP_R=1.0 rule 没有继承给新 37 点；本轮未 freeze weight vector。Surface membership authority 不自动控制：skin values、bone driver、THUMB_IP_R=1.0 rule、R3 ownership、nail authority、first-web authority、CMC cage、pose limits、Stage6 qualification，以及旧 skin/deformation/strict-bound verdict；这些需独立 downstream reconciliation。Human 批准范围保持 membership-only。

CAP_DOWNSTREAM_REVALIDATION_TRIGGER.json 仅记录上述触发状态与 NEXT，没有开始 blast-radius audit、R3 rebuild、skin rebuild、R1F 或 Stage6。

## Registry and protected state

检查未发现正式 registry/current pointer/canonical index；找到的旧 canonical method errata 是历史语义声明，不是可变 registry。未创建全局 registry，也未修改其它 authority；本目录 immutable freeze artifacts 是 authoritative source。见 AUTHORITY_REGISTRY_DISCOVERY.json。

1531 个既有 workspace 文件 + 6 个外部 Human responses/本轮用户指令 source：before SHA-256 == after SHA-256；所有 .blend、docs、references、reference_manifest、production_spec、historical audits、Human originals/copies 保持 byte-identical。没有目录外新文件、没有既有 pointer update。详见 PROTECTED_STATE_BEFORE.json / PROTECTED_STATE_VERIFICATION.json。

BLEND_FILES_WRITTEN=0；WEIGHT_DELTA=0；GEOMETRY_DELTA=0；TOPOLOGY_DELTA=0；BONE_DELTA=0；JOINT_DELTA=0；R1F_CREATED=false；Stage6_runs=0；R3_runs=0；strict_bound_recalculations=0；geodesic_selector_runs=0；boundary_solver_runs=0。CAP_REGION_IDENTITY=FROZEN；CAP_BOUNDARY=FROZEN；SKIN_REBUILD=NOT_STARTED；Stage6=NOT_RUN。

**NEXT=CAP_DEPENDENCY_BLAST_RADIUS_AUDIT_R1；STOP。** 本轮 freeze 成功后不自动开始下一轮。
