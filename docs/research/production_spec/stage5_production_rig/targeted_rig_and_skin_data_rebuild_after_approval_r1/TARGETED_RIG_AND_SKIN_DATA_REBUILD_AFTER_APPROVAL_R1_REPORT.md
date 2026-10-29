# TARGETED_RIG_AND_SKIN_DATA_REBUILD_AFTER_APPROVAL_R1

结论：**FAIL_CLOSED_REBUILD_OR_STATIC_INTEGRITY**。新 candidate 已创建，244/244 点完成批准规则 evaluation；保存和独立 Blender clean reload 通过。静态 contract 仍有 64 条阻塞边与 55 个历史微量 forbidden influence 点，不能据此推进 targeted deformation。candidate_static_pass=false，candidate_deformation_pass=false，production_promotion=false。

## 审批和输入

唯一审批：`<USER_HOME>\Downloads\SKIN_AUTHORITY_RECONCILIATION_HUMAN_REVIEW_R1_RESPONSE_2026-10-03T13-24-31-414Z.json`。原始字节复制到 HUMAN_APPROVAL_RESPONSE_SOURCE_COPY.json，notes 原样保留；Q1–Q7 均 YES，全部约束字段逐类型逐值验证。审批只授权本轮 skin authority plan/scope 和新 candidate，不预先批准生成权重、deformation、Stage6 或 production qualification。

| 输入 | 已验证 SHA256 / canonical hash |
|---|---|
| proposal bundle | a0a3811f00984edce73db6ff4171d72aeaec07e27dbe17936266dec6d9da1340 |
| R3 authority | 361f4f25201f5810830dc1bfc4bd2cf19db908aef8945801a63bfd2829197ff0 |
| R3 membership | f57483723e90cc34e0551bf70fac00c7c8cb789dbad5d0e248018fdaddd3741d |
| corrected rig | 5d5f86bb59135715a77515468c2b76fe81e2a44e2e8c5d6c17fcc3d56d2147fe |
| frozen Stage4C_R2 | fde620b2cebd2b4cd894e32b58d7b59ba7fac9b00d3d2dfa5193cefb32513ab7 |
| R1B weight donor | cec5804f1319bf2408fded21a3d0cf8c9f01bf778ae0659c18cf17950b117d10 |

proposal 中所有 component 文件逐字节 hash 验证，包含 cap37、old cap9、FIRST_WEB、reuse set、envelope、continuity contract 和 edge5879 scope。未创建或重新计算 authority；R3 labels 仅用于 guard 和 transition context。

## 候选和逐点写入范围

新 candidate：`<HANDS_ROOT>\production_spec\stage5_production_rig\targeted_rig_and_skin_data_rebuild_after_approval_r1\RIGHT_HAND_STAGE5B_TARGETED_SKIN_REBUILD_R1.blend`

SHA256：`290d2734f80edb25872962bf378dbc4c122d6fafe3fd118b22a6e550ddfcb84a`

geometry/topology/UV/mesh coordinates/material assignment 直接继承冻结 Stage4C_R2；全部 21 bones 的 rest/pose transforms、head/tail、local frame、deform flags、origin/hierarchy 与 corrected rig 逐值一致。16 deform groups 继承 R1B 的 group order。5 TIP helpers 为 non-deform，全 mesh 权重为零。

使用 Armature modifier 绑定 corrected rig，保留 corrected mesh parent=None 和全部 object transforms；未 apply transform、改 origin 或 reparent。未计算 pose/deformed geometry。

| 正式分类 | 点数 | 处理 | 实际变化 |
|---|---:|---|---:|
| SAFE_REUSE | 2401 | R1B vector exact copy，不 normalize/prune | 0 |
| TARGETED_REVALIDATION | 771 | R1B vector exact copy；仅 flag | 0 |
| REBUILD_REQUIRED | 244 | 244/244 deterministic rule evaluation | 238 |

三个集合互斥、完整覆盖 3416 点。实际 changed IDs 全部属于批准 244；outside write=0。6 点 evaluation 后与 donor 数值相同，未制造变化。完整 group delta 见 WEIGHT_DELTA_CENSUS_R1.json。

## 批准规则执行

cap37：corrected thumb arc 上按批准 `h=19.441025 mm`、`s_IP=74.64295890757278 mm` 和 centered quintic `6t^5−15t^4+10t^3` 生成 IP/MCP 混合。37 点全 evaluation，31 点实际变化。只有 IP/MCP，无 INDEX/WRIST/TIP；12 点为公式 plateau 导致 IP=1，未把全部 37 点设为 one-hot。83 条 incident edges 的最大 L∞=0.0566409863532、L1=0.113281968981，本局部绝对静态 gate 阻塞 0。逐点 before/after、分布和邻接证据均已保存。

其余批准 THUMB rebuild 点按 hash-bound historical centered-base/tube family 与 corrected arc 的连续 profile evaluation。没有将 rig affected 163 点或 fresh boundary 126 点自动扩为 write set。

old cap9：151、158、1061、1074、1076、2189、2192、2569、2577 全部 evaluation 并实际变化；删除旧 THUMB distal override，仅允许 INDEX chain + WRIST。119 个 INDEX rebuild unknown 与唯一可改 shared-web 点联合求解批准的静态 simplex harmonic field；sorted cyclic exact block minimization，lambda=0.01，370 iterations，projected residual=7.61724017195e-13。只用批准的 geometry prior 和 compatible retained INDEX boundary；没有 deformation objective。9 点无 INDEX_MCP one-hot，局部 24 条边阻塞 0，最大 L∞=0.0729888826609、L1=0.145977779042。9/9 before、after、邻点向量、driver family、dominance、gradient 与 metric 已保存。

FIRST_WEB21：仅 v3125 rebuild 并实际改变；其余 20 点逐值复制。只允许 WRIST_R、THUMB_CMC_R、THUMB_MCP_R、INDEX_MCP_R，全部 THUMB_IP=0、TIP=0。未依据 R3 的 7/14 标签改 one-hot。

edge5879：v1551 与 v3125 都在批准 244 内并实际改变。正式 hash-bound neighborhood 18 点包含 7 rebuild、11 targeted-revalidation；7 点 evaluation，11 点 exact copy，全部 18 点参与静态邻域审计。采用正式分类优先规则，未把 11 点扩为 write set。

端点新向量：

```json
{
  "1551": {
    "WRIST_R": 0.7061624526977539,
    "INDEX_MCP_R": 0.14673694968223572,
    "INDEX_PIP_R": 0.07376766204833984,
    "INDEX_DIP_R": 0.07333293557167053
  },
  "3125": {
    "WRIST_R": 0.39925962686538696,
    "THUMB_CMC_R": 0.01638963259756565,
    "THUMB_MCP_R": 0.4930126667022705,
    "INDEX_MCP_R": 0.09133804589509964
  }
}
```

edge5879 本边 L∞=0.493012666702，L1=1.01880462654；其整个批准邻域仍有 17 条静态 blocker。历史 R1E deformation defect 仍是有效证据，未用 R1E vector 作为 base，未运行 CMC_MCP_L3 或声称 deformation defect 已消除。

## 静态阻塞与范围冲突

全 mesh 数学检查通过：sum tolerance=1e-5，最大误差 4.40049916506e-08，负值/NaN/Inf/nondeform group/TIP/influence-count 违规均 0，最大 influences=4。

envelope 内部及 crossing 共检查 2089 条边；严格 gate 为单 group jump≤0.5、L1 jump≤1。64 条 blocker 中 44 条接触批准 rebuild，20 条为 copy-only。274 条边比 R1B 增加了至少一个 jump metric（以批准 sum tolerance 记录数值增量）；这些增量完整保存，不等同 274 个绝对 gate blocker，也不代表 pose qualification。

strict forbidden-weight=0 guard 发现 55 点微量历史 residue（34 TARGETED_REVALIDATION、21 SAFE_REUSE）。全部 exact donor copy，本轮新增违规 0；其中 23 点超过 1e-8，0 点超过 1e-6。未擅自将 guard 改为 1e-6，未清除 copy-only 微量值。TARGETED 点仅标 TARGETED_VALIDATION_FLAG。

以下阻塞不能通过任意合法 244-only 权重求解消除，详见 STATIC_SCOPE_CONFLICT_CERTIFICATE_R1.json：

1. edge1130，v303/v1396 均必须 immutable copy，L∞=0.655587911605835、L1=1.31117582321167 超过 gate；改任意批准 244 点不能改变这条边。
2. edge1234，v338 是 INDEX rebuild，THUMB_MCP 必须 0；v1448 是 copy-only FIRST_WEB，THUMB_MCP 必须保留 1。该 group jump 恒为 1，大于 0.5；调整 solver 参数无法同时满足 support 和 copy contract。
3. 上述 55 个 copy-only 点必须保留历史正 forbidden weight，但严格 guard 要求 0；移除将违反批准 exact-copy/write scope。

因此保留完整 candidate 与可复核失败证据，未增大 scope、改 membership/support、暗调参数或进入下一阶段。局部 cap37/old cap9 的静态 gate 通过不抵消全候选 failure。

## 保存、保护和停止

candidate 保存一次，独立 factory-startup Blender clean reopen 读取 mesh、UV、material、binding、all bones、all 3416 vectors；pre-save 与 reload payload 全部 exact，serialization drift=0。

历史保护核对 2081 个文件，before=after 全部一致；modified/removed/added outside task directory=0。历史 blend writes=0，candidate blend writes=1。所有新增文件仅在本轮目录。可复核的 raw payload、逐点 delta、authority hashes、static metrics 和冲突证据随报告保存；独立输出核对与 evidence hash manifest 区分 artifact consistency PASS 和 candidate FAIL_CLOSED。

Stage6 runs=0；pose/deformation runs=0；R3 reruns=0；strict-bound recomputations=0；production promotion=false。NEXT=NONE_FAIL_CLOSED_STATIC_GATE_RECONCILIATION_REQUIRED；STOP=true。未推进成功路径 CAP_FIXTURE_STATIC_VALIDATION_AND_TARGETED_DEFORMATION_R1。
