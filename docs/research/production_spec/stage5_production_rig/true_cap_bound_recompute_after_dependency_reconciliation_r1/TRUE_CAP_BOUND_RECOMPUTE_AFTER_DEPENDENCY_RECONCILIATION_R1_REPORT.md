# TRUE_CAP_BOUND_RECOMPUTE_AFTER_DEPENDENCY_RECONCILIATION_R1

**PASS_CORRECTED_BOUND_AUTHORITY_ESTABLISHED — STOP**

本轮建立 corrected geometric / kinematic numeric authority。所有当前数值重新计算，没有继承 old cap9、old REP 或 contaminated derived inputs 的数值。已核验 targeted Human closure = PASS_WITH_HUMAN_REVIEW_COMPLETE；ADDITIONAL_REMEDIATION_REQUIRED = NO、ADDITIONAL_SCOPE_EXPANSION_REQUIRED = NO、PRODUCTION_DRIFT = 0。

| Required field | Result |
|---|---|
| HISTORICAL_METHOD_RECOVERED | True |
| CAP37_SOURCE_COUNT | 37 |
| OLD_CAP9_SOURCE_AUTHORITY_COUNT | 0 |
| CURRENT_TARGET_AUTHORITY | FRESH_R3_OWNERSHIP_AUTHORITY_R1 / INDEX_SIDE_EXACT_BOUNDARY_ENDPOINTS |
| CURRENT_TARGET_COUNT | 19 |
| STATIC_PATH_PAIR_COUNT | 703 |
| TRUE_CAP_STATIC_PATH_MIN_MM | 81.76973560299072 |
| TRUE_CAP_STATIC_PATH_P05_MM | 88.4509022620621 |
| TRUE_CAP_STATIC_PATH_MEDIAN_MM | 103.08216070852043 |
| TRUE_CAP_STATIC_PATH_P95_MM | 121.42116411229027 |
| TRUE_CAP_STATIC_PATH_MAX_MM | 131.54036962594424 |
| TRUE_CAP_STATIC_PATH_MEAN_MM | 103.90916390476099 |
| CMC_MCP_L3_CORRECTED_TRUE_CAP_BOUND | 0.6806198919342639 |
| FULL_OPP_L3_CORRECTED_TRUE_CAP_BOUND | 0.6916621180243677 |
| ADDITIONAL_RECOMPUTED_BOUND_CASES | ['TH_IP_30', 'TH_IP_45', 'TH_MCP_45', 'CMC_OPP_30', '120 historical virtual endpoint LBS recipes, 703 INDEX-target pairs / 1406 full-exact-boundary context pairs per recipe'] |
| DETERMINISTIC_RERUN | PASS_EXACT_VALUE_AND_PAYLOAD_HASH_MATCH |
| PRODUCTION_DRIFT | 0 |
| TRUE_CAP_BOUND_VERDICT | PASS_CORRECTED_BOUND_AUTHORITY_ESTABLISHED |

## Prerequisite 与 source / target authority

[Prerequisite gate](../../../../../examples/historical/production_spec/stage5_production_rig/true_cap_bound_recompute_after_dependency_reconciliation_r1/PREREQUISITE_GATE_R1.json) 完整通过；每次独立 Blender 进程均在数值计算前 clean reopen 核对当前 R2 payload、实际 weight vector SHA256 和全部21 bones 对 corrected frozen rig 的精确一致性。

- cap37：HUMAN_APPROVED_FROZEN，37 vertices / 25 faces；combined authority hash c81dd96d6925ed402cdf0ba44c148d7a78c2c60640fe23fb6247fb729f346cc8。
- old cap9：SUPERSEDED_CONTAMINATED；native INDEX_SURFACE = 9/9；source authority role = 0。
- corrected rig：HUMAN_APPROVED_APPLIED_VERIFIED；SHA256 5d5f86bb59135715a77515468c2b76fe81e2a44e2e8c5d6c17fcc3d56d2147fe。
- fresh-R3：HUMAN_APPROVED_FROZEN；membership hash f57483723e90cc34e0551bf70fac00c7c8cb789dbad5d0e248018fdaddd3741d；combined authority hash 361f4f25201f5810830dc1bfc4bd2cf19db908aef8945801a63bfd2829197ff0。
- R2 candidate：SHA256 adf757aeace8a0d69070b94f102b9bef9eb99da9847dd7a5639c4c2c3799dde9；live weight vector SHA256 1d9437a10354cdd98a2b5cb5e43be8cfabc519e232235483a615e76898129f55。
- targeted Human receipts 与 final closure 原样保留。

Source 数学对象为**全部37个 frozen cap37 vertices，逐点作为 endpoint**，没有 representative、centroid、extreme-vertex 或 REP 选择。Target 继续承担历史 **exact ownership boundary 的 INDEX 侧端点** 角色：fresh20 boundary 提供19个唯一 INDEX endpoints，38个完整 boundary endpoints。本轮不以历史16端点/144对限制 corrected cardinality。

[Source / target authority](../../../../../examples/historical/production_spec/stage5_production_rig/true_cap_bound_recompute_after_dependency_reconciliation_r1/CORRECTED_TRUE_CAP_SOURCE_TARGET_AUTHORITY.json) 区分 exact boundary、collar transition neighborhood、proximal semantic stop 和 FIRST_WEB21。Proximal stop 不当完整 target anatomy map；transition band 与 FIRST_WEB21 不加入 primary target。历史 sensitivity 所用两侧 exact endpoints 独立保留为37×38 = 1406对 context family。

Frozen fresh-R3 labels/boundary 直接消费；R3 Dijkstra、min-cut、closure、sheet validator、R3 solver 均未运行。下面的 mesh-edge Dijkstra 只用于已授权 bind-path bound 重算。

## 历史数学方法恢复

数值计算之前已读取并登记110份直接相关正式实现/报告；逐项分类与完整 relevant excerpts 见 [method recovery](../../../../artifacts/a507c2c2d69950095297.md)。依赖 inventory 中11份 RECOMPUTE_REQUIRED references 全部映射至当前 numeric payload，见 [coverage](../../../../../examples/historical/production_spec/stage5_production_rig/true_cap_bound_recompute_after_dependency_reconciliation_r1/RECOMPUTE_REQUIRED_BOUND_CASE_COVERAGE_R1.json)。

令固定 mesh path 的 bind edge lengths 为 bᵢ、posed edge lengths 为 pᵢ，endpoint separation 为 dₜ：

Σpᵢ ≥ ||B_pose − A_pose|| = dₜ，所以 maxᵢ(pᵢ / bᵢ) ≥ dₜ / Σbᵢ。

正式 strict bound 为 **posed endpoint separation / fixed shortest bind path length**。Graph 使用全 mesh native undirected edges，edge metric 为实际 bind-space world-mm mesh edge Euclidean length。没有用 endpoint chord 替换 path；没有通过新 cost、ownership cut 或 vertex-index distance 改变图。

METHOD_REUSABLE：三角不等式、mesh-edge metric、完整 endpoint enumeration、历史 pose primitive、虚拟 endpoint LBS sensitivity 方法。INPUT_INVALIDATED_RECOMPUTE：old cap9 / REP、old R3 exact endpoints、旧 rig / R1E endpoint transforms。SEMANTIC_INVALIDATED_RECOMPUTE：旧 full-sheet/global ownership 与旧 arc anatomical interpretation，以及已被否定的 (abs(uA)+Lbind)/Lbind。历史数字与 downstream recommendations 为 HISTORICAL_VALUE_ONLY。UNRESOLVED = []。

Historical feasibility 的 bound 汇总是当前最短10个 distinct endpoint pair 上的最大值；本轮保留这项，并按完整 endpoint method 额外报告703对 ensemble 的最大值。**Required 两项 CORRECTED_TRUE_CAP_BOUND 字段明确采用 full703 max**；top10 数值独立列示，避免把两种 aggregation 混同。

## Static path ensemble

完整 primary ensemble = **37×19 = 703**。每条路径都记录 source / target class、vertex sequence、edge IDs、individual edge lengths、total length、semantic proxy sequence、fresh ownership sequence 与 region traversal flags。所有38个 exact boundary endpoints 的1406条 context paths 亦完整记录。

[完整路径 family](../../../../artifacts/5f1d5dcf8196cd0ca920.md) 包含 count、min、p05、median、p95、max、mean，以及10 shortest distinct pairs 和 global shortest path。Percentile 沿用历史离散排序规则：p05 = floor(0.05×(n−1))；median = floor(n/2)；p95 = floor(0.95×(n−1))，没有替换为 interpolation。

Global shortest：**v1380 → v2035，24 edges，81.769735603 mm**。

Vertex sequence：1380 → 2787 → 1456 → 2782 → 1398 → 2775 → 1407 → 2770 → 1369 → 2753 → 1433 → 2757 → 2375 → 3245 → 1427 → 2856 → 1584 → 2855 → 1581 → 2854 → 1579 → 2853 → 2040 → 3143 → 2035。

Edge ID sequence：4526, 4528, 4507, 4509, 4481, 4479, 4460, 4458, 4392, 4390, 4407, 4409, 6360, 6358, 4805, 4803, 4800, 4798, 4797, 4795, 4791, 4793, 5951, 5950。

Shortest route traversal：cap37 / thumb distal / thumb MCP transition / CMC transition / collar = YES；first-web = NO。全部703条 shortest routes 都位于 frozen fresh-R3 bounded domain 内。Semantic region labels 承接 corrected chain / bounded ownership 的历史 descriptive proxy，不构造新 anatomy authority。Fresh-R3 未批准 full palm anatomy map；path payload 中域外 route 的 palm flag 必须 UNKNOWN；域内 false 仅指当前 bounded proxy 没有标出 PALM，不能当 full biological palm exclusion 证明。

## Posed true-cap bounds 与额外 cases

只运行正式历史方法中的六个 poses，且每项标注 BOUND_RECOMPUTATION_PROBE。原有 pose primitive 函数 AST 与 Stage6B quaternion / MCP-IP progression 原样复用；当前 R2 corrected rig、actual endpoint weights、cap37 与 fresh targets 被消费。未保存 production blend。

| Pose | Full703 max bound | Current top10 max bound | cap37 mean displacement mm |
|---|---:|---:|---:|
| TH_IP_30 | 0.529806317 | 0.513450762 | 9.913453005 |
| TH_IP_45 | 0.508486086 | 0.483224929 | 14.657787565 |
| TH_MCP_45 | 0.571834996 | 0.525743818 | 35.654289598 |
| CMC_OPP_30 | 0.570159368 | 0.549231628 | 43.721630914 |
| CMC_MCP_L3 | 0.680619892 | 0.658333124 | 64.132880726 |
| FULL_OPP_L3 | 0.691662118 | 0.669136062 | 67.683622588 |

[Posed recomputation](../../../../artifacts/9e8a68ae5bfa23b31427.md) 保存六个 poses 的全部703对 bound、bind/posed endpoint positions、endpoint displacement、fixed denominator、global shortest pair bound、top10/full max、actual pose state 与两侧 exact-boundary context max。

另重算历史 **120个 virtual endpoint LBS recipes**：五类原有 group-pair × 四个原有 poses × 六个原有 fractions。每个 recipe 计算完整703 INDEX-side pairs 和1406 full exact-boundary context pairs；source A 始终 actual evaluated R2 cap37，target B 为原数学方法的 algebraic virtual mixture。无 production weights mutation、无新 per-vertex weight assignment、无 percentage authority。虚拟 sensitivity 数字不会替代 actual R2 primary bound。

## Historical vs corrected

历史13.1646 mm路径以及 CMC_MCP_L3 = 5.9643、FULL_OPP_L3 = 6.5160 的 true-cap interpretation 均保持 INVALIDATED；只能作为历史 comparison。Old shortest v2192→v704 与 corrected v1380→v2035 不同，已有同图 forensic 对照。

| Pose | Historical top10 max, historical only | Corrected current top10 max | Corrected full703 max |
|---|---:|---:|---:|
| TH_IP_30 | 1.343500000 | 0.513450762 | 0.529806317 |
| TH_IP_45 | 1.933700000 | 0.483224929 | 0.508486086 |
| TH_MCP_45 | 3.367500000 | 0.525743818 | 0.571834996 |
| CMC_OPP_30 | 3.901300000 | 0.549231628 | 0.570159368 |
| CMC_MCP_L3 | 5.964300000 | 0.658333124 | 0.680619892 |
| FULL_OPP_L3 | 6.516000000 | 0.669136062 | 0.691662118 |

完整 [old-vs-corrected comparison](../../../../../examples/historical/production_spec/stage5_production_rig/true_cap_bound_recompute_after_dependency_reconciliation_r1/TRUE_CAP_HISTORICAL_VS_CORRECTED_COMPARISON.json) 同时保留历史144/288与当前703/1406 cardinality 和全部120 recipes 对比。旧数值未用作 seed、threshold、expected answer、acceptance target 或 anatomical truth。

本轮新 bound 只为 geometric / kinematic derived constraint，不等于人体最大允许角度、钢琴动作范围、deformation PASS、skin-quality threshold、教学姿态 canonical value 或 Stage6B opposition qualification。Bound 数值变化不会独自成立 skin failure、topology failure、retopo required、no legal weights 或 production failure。历史 mesh-limit / retopo / no-legal-weight / cap-constrained feasibility recommendations **没有自动复活**；若未来需恢复，必须另开 downstream reconciliation。

## 确定性与保护

完整 computation 在两个独立 Blender 5.1.2 processes 中运行；每个进程从 frozen candidate clean reopen 开始并完整执行 path family、六个 actual pose bounds 与120 virtual recipes。A/B 每个 path vertex/edge sequence、每个浮点值和 payload 都**精确相同**，没有通过四舍五入掩盖不同 path。[Determinism verification](../../../../../examples/historical/production_spec/stage5_production_rig/true_cap_bound_recompute_after_dependency_reconciliation_r1/TRUE_CAP_BOUND_DETERMINISM_VERIFICATION.json) 记录全部 input/source/target/graph/path/bound hashes 与 canonical tie rule。

- Source-set hash：8711ef3a9c1518a75623410bd278858adeda0a551d6d2f8385d0df6210cdf377
- Target-set hash：755efe3bfb5ee0d24d4614d2965c5273f805c8c81e93211363158ff5349bed27
- Graph/metric hash：2cccf0b698177850d9d32e80854c533c3b82ac5a897d3d478532939c5b21428a
- Path-family payload hash：ce537f0919cc8005747232273a1a927cfd17f7ae05376f4a23487c7d816c9a25
- Bound payload hash：387c985a6177c6a7d08c8290d5b7009791a361f9ecf64af507a5dfc2212269f1

Path tie handling 沿用历史严格 relaxation 与 epsilon，ascending source/target/adjacency IDs、(distance,vertex) heap；等长候选保持首次 predecessor。不按 rounded lengths 选路。Path edge-length sum 与 Dijkstra accumulation 的 binary64 加法顺序残差逐路径记录；这不是 A/B 差异，不影响 path identity。

[Production verification](../../../../../examples/historical/production_spec/stage5_production_rig/true_cap_bound_recompute_after_dependency_reconciliation_r1/PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json)：全部 **2400** 个既有工作区文件前后 SHA256 相同；新增文件仅在本轮目录。每个 run 的 before/after in-memory mesh、UV、materials、weights、group order、21 bones、pose 与 transforms 精确恢复。R2、geometry、topology、UV、materials、bones、joints、RSSF、cap37 authority、corrected kinematics、fresh-R3、FIRST_WEB、Human receipts、历史 reports/numeric evidence 均未修改。

## 最小 forensic evidence

生成六张 endpoint/path sanity figures，见 [render manifest](../../../../../examples/historical/production_spec/stage5_production_rig/true_cap_bound_recompute_after_dependency_reconciliation_r1/FORENSIC_RENDER_MANIFEST.json)：bind cap37、current exact target/collar、global shortest、historical/corrected 同图、CMC_MCP_L3 与 FULL_OPP_L3 actual endpoints / retained fixed-path context。颜色仅用于 forensic evidence，不是 Human anatomy review。

[Forensic contact sheet](../../../../artifacts/28d5ddc927f1ea0e777e.md)

## NEXT 与 STOP

**NEXT = FULL_STAGE6A_REQUALIFICATION**，只记录；NEXT_EXECUTED = false，automatic_next_phase = false，**STOP = true**。

本轮未执行 full Stage6A / Stage6B、R3 solve/rerun、skin rebuild、rig modification、retopo、production freeze 或 promotion。
