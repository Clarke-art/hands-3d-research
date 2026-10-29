from pathlib import Path
from collections import Counter, defaultdict, deque
from datetime import datetime, timezone
import json, hashlib, sys
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
O=Path(__file__).resolve().parents[1]
R=O.parents[2]
assert R==Path(r'<HANDS_ROOT>')
def j(n):return json.loads((O/n).read_text(encoding='utf-8'))
def dump(n,d):(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()

SN=j('PROTECTED_STATE_BEFORE.json');I=j('CAP_DIRECT_REFERENCE_AUDIT.json');SUM=j('_INVENTORY_SUMMARY.json')
W=j('STAGE5B_CAP_DEPENDENT_WEIGHT_REGION_AUDIT.json');A=j('R3_OLD_CAP9_INFLUENCE_RADIUS_AUDIT.json');G=j('CAP_DEPENDENCY_DAG.json');SEQ=j('CAP_CORRECTION_RECOVERY_SEQUENCE_R1.json')
CAN=R/'production_spec/stage5_production_rig/stage5b_r1e_human_cap_authority_freeze_r1/THUMB_DISTAL_CAP_CANONICAL_AUTHORITY_R1.json'
can=json.loads(CAN.read_text(encoding='utf-8'));payload={k:v for k,v in can.items()if k!='combined_authority_hash'}
ch=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf-8')).hexdigest()
EXPECTED='c81dd96d6925ed402cdf0ba44c148d7a78c2c60640fe23fb6247fb729f346cc8'
assert ch==can['combined_authority_hash']==EXPECTED and can['status']=='HUMAN_APPROVED_FROZEN' and can['vertex_count']==37 and can['face_count']==25
assert not set(can['vertex_ids'])&set(A['old_cap9_ids'])

# Evidence index supplements short edge locators; it does not execute any constructor.
refs={}
def collect(v):
    if isinstance(v,dict):
        if 'path' in v and 'sha256' in v and 'locator' in v:
            key=(v['path'],v['locator']);refs[key]=v
        for x in v.values():collect(x)
    elif isinstance(v,list):
        for x in v:collect(x)
for n in ['R3_OLD_CAP9_INFLUENCE_RADIUS_AUDIT.json','STAGE5B_CAP_DEPENDENT_WEIGHT_REGION_AUDIT.json','EDGE5879_CAP_DEPENDENCY_AUDIT.json','STAGE6_CAP_DEPENDENCY_AUDIT.json','EARLIEST_SAFE_REBUILD_BASELINE_AUDIT.json']:collect(j(n))
G['source_evidence_index']=list(refs.values())
G['canonical_membership_evidence']={'path':str(CAN.relative_to(R)),'sha256':sha(CAN),'combined_authority_hash':ch,'locator':'$.vertex_ids,face_ids,status; explicit frozen Human membership'}
for e in G['source_evidence_index']:
    assert sha(R/e['path'])==e['sha256'],e['path']
dump('CAP_DEPENDENCY_DAG.json',G);dump('CAP_DEPENDENCY_GRAPH_R1.json',G)

classes=Counter(x['dependency_class']for x in I['artifact_classification']);tiers=Counter(x['remediation_tier']for x in I['artifact_classification'])
assert dict(classes)==I['classification_counts']==SUM['classes']
assert dict(tiers)==I['remediation_tier_counts']==SUM['tiers']
assert sum(classes.values())==sum(tiers.values())==1532
assert len({x['path']for x in I['artifact_classification']})==1532
assert set(x['path']for x in I['artifact_classification'])|set(x['path']for x in I['excluded_protected_infrastructure'])==set(SN['workspace'])
assert len(SN['workspace'])==1549 and len(SN['external'])==6
ids={n['id']for n in G['nodes']};deg={n:0 for n in ids};adj=defaultdict(list)
for e in G['edges']:
    assert e['from'] in ids and e['to'] in ids
    deg[e['to']]+=1;adj[e['from']].append(e['to'])
q=deque(k for k in deg if deg[k]==0);visited=[]
while q:
    x=q.popleft();visited.append(x)
    for y in adj[x]:
        deg[y]-=1
        if not deg[y]:q.append(y)
assert len(visited)==len(ids)==23 and len(G['edges'])==41
for s in SEQ['steps']:assert all(x<s['step']for x in s['depends_on'])
assert 6 in SEQ['steps'][6]['depends_on']
D=j('_STATIC_AUDIT_DATA.json')
assert all(D['native_labels'][v]=='index'for v in A['two_ring_native_index_THUMB_label_ids'])
assert len(set(D['cap_dependent_review_region_ids'])|set(D['cap_independent_ids']))==3416
assert not set(D['cap_dependent_review_region_ids'])&set(D['cap_independent_ids'])

# Freeze verification covers all historical files, including malformed JSONs and caches.
wr=[];er=[]
for rel,before in SN['workspace'].items():
    p=R/rel;after=sha(p)if p.is_file()else None
    wr.append({'path':rel,'before':before,'after':after,'equal':before==after})
for name,before in SN['external'].items():
    p=Path(name);after=sha(p)if p.is_file()else None
    er.append({'path':name,'before':before,'after':after,'equal':before==after})
new_outside=[str(p.relative_to(R))for p in R.rglob('*')if p.is_file()and O not in p.parents and str(p.relative_to(R)).replace('\\','/')not in SN['workspace']]
assert all(x['equal']for x in wr+er),'A protected historical file changed'
assert not new_outside,new_outside
assert not list(O.rglob('*.blend'))
ZERO={'BLEND_FILES_WRITTEN':0,'WEIGHT_DELTA':0,'GEOMETRY_DELTA':0,'TOPOLOGY_DELTA':0,'BONE_DELTA':0,'JOINT_DELTA':0,'R3_runs':0,'Stage6_runs':0,'strict_bound_recompute_runs':0,'cap_to_collar_path_runs':0,'cap_selector_runs':0,'R1F_created':False,'retopo_runs':0}
FREE={'execution':'CAP_DEPENDENCY_BLAST_RADIUS_AUDIT_R1','verification_time_utc':datetime.now(timezone.utc).isoformat(),'workspace_file_count':len(wr),'external_file_count':len(er),'workspace':wr,'external':er,'all_protected_before_equal_after':True,'new_files_outside_audit_directory':new_outside,'canonical_combined_authority_hash':ch,'delta_basis':'All historical blend/data bytes preserved, and only static audit/diagram scripts executed; no production constructor or Blender process invoked',**ZERO}
dump('PROTECTED_STATE_VERIFICATION.json',FREE)

REPORT=r'''# CAP_DEPENDENCY_BLAST_RADIUS_AUDIT_R1

执行状态：READ-ONLY AUDIT COMPLETED。只在本次新目录写入审计 JSON、报告、脚本及四张 PNG；所有历史 production、authority、Human responses、audits 保持逐文件 SHA256 不变。本报告给出未来恢复范围和顺序，本轮没有启动任何恢复步骤。

## 1. Canonical authority 与计数边界

首先读取并验证 `THUMB_DISTAL_CAP_CANONICAL_AUTHORITY_R1.json`：HUMAN_APPROVED_FROZEN，37 vertices / 25 faces，EXPLICIT FROZEN MEMBERSHIP SET。

`combined_authority_hash = c81dd96d6925ed402cdf0ba44c148d7a78c2c60640fe23fb6247fb729f346cc8`

验证方法：仅移除 `combined_authority_hash` 字段，对其余 payload 使用 UTF-8、sort_keys、紧凑 separators、ensure_ascii=False、allow_nan=False 后 SHA256。读取冻结 IDs，没有执行 selector、修改 seed、boundary 或 membership。cap37 的 membership approval 不等于骨端点、局部轴或 THUMB_IP_R=1 权重规则的 approval。

OLD_CAP9 = SUPERSEDED_CONTAMINATED，9/9 = native INDEX_SURFACE：151、158、1061、1074、1076、2189、2192、2569、2577。该事实沿用正式 native audit，不重新裁决。

计数单位为 **一个既有文件**，每个文件只有一个 primary dependency class 和一个 future-reuse remediation tier。共 1549 个保护文件，其中 17 个 cache/assistant metadata 只作冻结保护，1532 个进入语义 artifact 清单。6 个外部文件（原始 Human responses 与本轮指令附件）另外作冻结保护。新增审计文件不计入历史 artifact 数；23 个 DAG component nodes 与 artifact 数分开。

| Primary class | Artifact count |
|---|---:|
| DIRECT_DEPENDENCY | 144 |
| DERIVED_DEPENDENCY | 195 |
| TRANSITIVE_DEPENDENCY | 503 |
| VALIDATION_ONLY_DEPENDENCY | 23 |
| NO_CAP_DEPENDENCY | 665 |
| UNRESOLVED | 2 |
| 合计 | 1532 |

清单见 [CAP_DIRECT_REFERENCE_AUDIT.json](CAP_DIRECT_REFERENCE_AUDIT.json)，包含每个文件的 SHA256、class、证据 locator、basis、confidence、tier 和历史保留规则。搜索限定 cap 语义字段/authority reference，再结合审阅过的 constructor/import/input lineage；普通 vertex ID、CAP_MAX 流容量、forearm cap、max-influence cap 不算拇指 cap reference。binary blends/renders 的 provenance 来自其生成输入及保存链，而非字符串扫描。缺少 literal ID 不作为独立性证明。

这些是文件粒度的保守主分类，混合文件中的局部独立组件另列在专项 JSON。例如直接引用旧 cap 的 corrective audit 仍是 DIRECT reference，但旧 cap 是审计对象，不是当前 native 真值输入；其 tier 为历史保留。共享“四指 tip 比较方法”的文字引用也不能推导为四指 joint authority 全部错误。665 个 NO_CAP 文件依据独立 upstream constructor、native corrective evidence 或 hash receipt 的作用判定，不能解读为对整套工程无缺陷的声明。

## 2. 最早影响点：R2A kinematic slots → R1 skin → R1A 显式 membership

`stage5a_r2a/scripts/s5a_r2a_build.py` L163–190 从历史 posed thumb domain 计算 cap representative REP；L245–260 将其写入真实骨数据：THUMB_TIP_R.head、THUMB_TIP_R.tail、THUMB_IP_R.tail，并对 IP/TIP 执行 align_roll。REP 来源已经废止，因此这些局部端点/frames 必须独立重新验证。THUMB_IP_R.head、无关 joint heads、hierarchy/origin 没有因这条依赖自动废止。R2 是前序 tip selection evidence；本审计没有改写它。

`stage5b_r1/scripts/s5b_r1_bind.py` L55–59、L206–210、L282、L344 读取真实 R2A 骨 head/tail、计算 segment distance/radius/raw mu。故 **Stage5B R1 是最早 implementation 依赖阶段**，即使 R1 没有旧 cap ID selector。

**Stage5B R1A 是首次显式把错误 cap membership 写进实际 skin weights 的阶段。** `r1a_common.py` L428–483 将 cap 强制归为 THUMB，再生成 ownership、distal/authorized/first-web masks；`s5b_r1a_build.py` L87–94、L121–180 写入受 whitelist/free-budget 约束的实际 vectors。R1A saved delta 有全部九点的 before/after：R1 中 7 点已经 THUMB_IP dominant，v1061/v2189 从 INDEX dominant 被 override。R1A 的九点约为 THUMB_IP=1；冻结的 INDEX residue 仍可能存在，不能声称每点严格纯单骨。

R1B 从 R1A 继承，cap/nail/first-web 从可改区排除，protected drift=0；旧 cap9 没有在 R1B 被纠正。详见 [STAGE5B_CAP_DEPENDENT_WEIGHT_REGION_AUDIT.json](STAGE5B_CAP_DEPENDENT_WEIGHT_REGION_AUDIT.json)，记录九点 R1/R1A/R1B 实际 vectors 和 cap37 当前 vectors，没有生成新 vector。

| 功能 | R1 | R1A | R1B |
|---|---|---|---|
| 显式 cap ownership / IP driver rule | 无 cap-ID selector | cap override 与实际 vector 写入 | 继承并保护 |
| weight generation | live cap-derived rig | cap-derived masks/free budget | cap-derived masks/既有 vectors |
| distal-cap protection / protected drift | 无对应显式 cap gate | cap 与 nail semantic union | cap excluded、drift=0 |
| first-web exclusion / whitelist | 初始 live field | cap-derived boundary/exclusion | 继承 wrapper |
| normalize / prune arithmetic | 算式独立 | 算式独立；support/budget 依赖 | 算式独立；区域/冻结值依赖 |
| dominance / nail-cap interpretation | live rig 间接影响 | cap-derived ownership | 继承的 cap/chain semantic gate |

## 3. R1B 局部范围与 candidate 状态

R1B 仍是 **FROZEN HISTORICAL PRODUCTION MASTER**。保守审查 envelope 为 1485 vertices：既有 R1A/B/C/D/E authorized/repair masks、R2 domain、old9/cap37、以及实际 nonzero THUMB deform-driver carriers 的并集。该集合是依赖范围，不是 1485 点均已证明错误。

其余 1931 个 vector entries 不在这些区域、没有 THUMB driver，也不是 old/new cap，可作为未来重建的独立继承 entries，随后检查 byte/hash 与 regression。原有 four-finger group drift=0 证据保留；native INDEX 的旧 cap9 不能借该 group freeze 获得解剖正确性。

| Candidate | Future corrected-production reuse | 历史状态 |
|---|---|---|
| R1B | REBUILD_REQUIRED：新 skin/data counterpart | 冻结历史 master 保留 |
| R1C | REBUILD_REQUIRED：R2 ownership repair 依赖 | HISTORICAL_ONLY；原失败 verdict 保留 |
| R1D | REBUILD_REQUIRED：R2/live rig distal continuity 依赖 | HISTORICAL_ONLY；原失败 verdict 保留 |
| R1E | REBUILD_REQUIRED：R3 labels/collar/live axis/CAP clamps | HISTORICAL_ONLY；原失败 verdict 保留 |

各 candidate 的 actual authorized/changed IDs 已在专项 JSON 逐项记录。R1C/D/E 各自从 R1B rebase，不把失败候选误画成串行生产继承链。本轮无任何 rebuild。

first-web 有具体例外：R1A FIRST_WEB_21 的 membership 来自 cap-overridden THUMB/INDEX boundary、two-ring expansion 及 cap/nail exclusions（`r1a_common.py` L457–475）。因此 **first-web selector/protection wrapper 需要 targeted static revalidation**，既有 Human approval 保留历史作用。Stage4 first-web geometry、approved nail face mask 和 CMC cage geometry 本身不因 cap 更改而废止；cap/nail weight wrapper 及 R1E 使用 R3 labels 过滤的 cage protection wrapper 要重新验证。无需全盘重设计这些冻结几何。

## 4. R3：不能只替换 CAP 列表

路径不止 THUMB_STRONG：old9 → CAP union/live-tube source anchors → dT unary field/INF hard pins → coupled THUMB/INDEX mincut → closure/labels → boundary/sheet/ambiguous/gates；同时 old-cap centroid → R2 seed/domain → R3 graph，old REP → R2A live axis/tube → R3 anchors。源码 `r3_ownership.py` L176–220、L268–269、L350–450，及 `s6br1b_common.py` L177–181；source hashes 与 locators 在专项 JSON 和 DAG evidence index 中。

静态核对既存 graph/chain snapshot 后发现：**旧 cap9 同时全部满足历史 live thumb tube anchor predicate**。仅从显式 CAP union 删除九点，会移除 **0 个 effective wrong THUMB pins**。这不是一次新的 solve：这里只投影九个固定点到既存 live chain，复核源码 anchor predicate。cap37 现有 R3 labels 全为 THUMB，31 已 strong，新增硬 pins 将为 285、297、339、1378、1450、1452。

| Old vertex | R2 / R3 | Strong | 到既存 boundary 的 mesh-edge hops | Incident final cut |
|---:|---|---|---:|---|
| 151 | THUMB / THUMB | THUMB | 3 | 无 |
| 158 | THUMB / THUMB | THUMB | 3 | 无 |
| 1061 | THUMB / THUMB | THUMB | 4 | 无 |
| 1074 | THUMB / THUMB | THUMB | 4 | 无 |
| 1076 | THUMB / THUMB | THUMB | 3 | 无 |
| 2189 | THUMB / THUMB | THUMB | 2 | 无 |
| 2192 | THUMB / THUMB | THUMB | 2 | 无 |
| 2569 | THUMB / THUMB | THUMB | 2 | 无 |
| 2577 | THUMB / THUMB | THUMB | 4 | 无 |

九点的逐邻接 labels、one/two-ring IDs、strong roles、tube projection、closure role 全部见 [R3_OLD_CAP9_INFLUENCE_RADIUS_AUDIT.json](R3_OLD_CAP9_INFLUENCE_RADIUS_AUDIT.json)。其 1-ring 邻点保持 THUMB strong；被列出的 2-ring THUMB 点均由已冻结 native partition 标为 index。旧九点是 source/closure anchors，没有 incident final cut edge；这不构成“boundary 没有依赖”的证明。

| R3 component | Stored observation | Corrected-input conclusion |
|---|---|---|
| mincut labels | 3416 全 mesh labels；历史 coupled candidate graph 1008；R2→R3 changed34 | 依赖 contaminated inputs；不能把 changed34 当作 old9 单独因果效应 |
| boundary | 九点距 cut 2–4 hops、无 incident cut | Boundary likely affected = UNRESOLVED |
| connectivity closure | 既存 1 round；source anchors 保留 | changed-input closure/relabel effect = UNRESOLVED |
| sheet split | 既存 217 INDEX / 3199 body | 新 sheet 未知；旧 cap9 位于 body 不能证明真实 thumb cap 不入 INDEX sheet |
| ambiguous band | 既存 16 vertices，6 topology assignments | band 与 labels 输入相关，必须重新验证 |
| CLASS_A | 六条保护边的几何 authority 保留 | label preservation gate 重新验证，不能自动撤销几何保护 |

结论：**R3_FULL_RECOMPUTE_REQUIRED = YES**；范围是纠正输入后的完整耦合 THUMB/INDEX fields/mincut/closure/labels/boundary/sheet，不是 blanket invalidation 其他手指。须先解决 kinematic input、R2 seed、重复 tube anchors 与 wrapper semantics。**R3 boundary likely affected = UNRESOLVED**，因为本轮禁止 counterfactual solve，无法预测新的具体 cut。

1/2-ring 只是观测邻域，不能当作因果影响截止半径。算法依赖传播可达完整 coupled solve；没有运行新的 R3 Dijkstra fields、mincut 或 closure。当前 R3 保持 HISTORICALLY_HUMAN_APPROVED；corrected-production reuse 为 REVALIDATION_REQUIRED。

## 5. edge5879 的证据保留

Verdict：**PARTLY_CAP_DERIVED**。v1551/v3125 都不是 old9，现有 R3 均为 THUMB。历史 saved 实测 CMC_MCP_L3 edge ratio = 11.041286717387363；R1B 相应约 1。v1551 在 R1B 是 MCP .968431532 / IP .031568479，R1E 变为 WRIST .939999998 / MCP .059979524 / IP 2.0475e-5；v3125 保留 first-web MCP=1。

这是实际冻结 vectors 与 actual deformation 的局部 weight partition mismatch，仍是 WEIGHT_TRANSITION_PARTITIONING_DEFECT。原证据不使用 true-cap strict-bound 公式，因此不能随 cap endpoint 更正撤销。但生成该场的 R1E allowed family/region、R3 collar/palm_share、live-axis gate 及 relax 都有派生依赖（`s5b_r1e_build.py` L342–411、L425–465），故不判 FULLY independent，也不判全部数值证据失效。完整 saved evidence 见 [EDGE5879_CAP_DEPENDENCY_AUDIT.json](EDGE5879_CAP_DEPENDENCY_AUDIT.json)。没有重跑 pose 或重算 ratio。

## 6. Stage6 数值、解释与 qualification 分离

根据可执行赋值确认实际 skin input，不依据陈旧 header：

| Historical full suite | Actual input |
|---|---|
| Stage6A R1 | Stage5B R1A |
| Stage6A R1A | Stage5B R1B |
| Stage6A R1B | Stage5B R1C |
| Stage6B R1 | Stage5B R1B |
| Stage6B R1B | Stage5B R1C |

其中 Stage6A R1B builder L34–36 和 Stage6B R1B builder L29–30 的 overrides 选择 R1C；历史文件未改写。这五套 full suites 在 R3 之前，不能倒推为消费过 R3。R3 collar metrics 适用于后来 R1E targeted prequalification/audits。

| Result component | Dependency classification / disposition |
|---|---|
| Abstract pose angles/case matrix | NO_CAP_DEPENDENCY；保留 test intent |
| World rotation axes/LBS transforms | DERIVED；IP frame/live rig 需要 reconciliation |
| skin/harness payload | TRANSITIVE；旧 payload 保留，新数据重建 |
| actual deformation/edge stretch/displacement | TRANSITIVE；NUMERIC_OBSERVATION_STILL_FACTUAL，对 corrected data 重新测量 |
| severe-edge threshold arithmetic | NO_CAP；常量独立，测量输入与 region semantics 要分开 |
| distal-cap / nail-cap fixture | DIRECT；ANATOMICAL_INTERPRETATION_INVALIDATED，future fixture 使用 frozen37 |
| raw self-intersection pairs/depth | TRANSITIVE geometry；旧 pair/depth 是实际事实 |
| digit/cap self-intersection buckets | DERIVED classifier；ownership semantics 要重新验证 |
| R3 collar metrics | 五套旧 full suites 不适用；后来 R1E 为 R3-derived |
| status/freeze/qualification/recommendation | 对未来 corrected production 为 QUALIFICATION_VERDICT_NEEDS_REVALIDATION |

[STAGE6_CAP_DEPENDENCY_AUDIT.json](STAGE6_CAP_DEPENDENCY_AUDIT.json) 为每套 suite 分别记录上述 component classes、source path/line/hash，以及后来 R1D/E 的 targeted 路径。旧 FAIL、actual ratio、Human approval 均保留原作用；本轮没有颁发新的 PASS/FAIL。后续新生产数据需要 TIER_4 full Stage6A 和 Stage6B requalification。

## 7. Strict-bound family 的失效范围

以下 anatomical interpretation 已废止：13.1646 mm 为真实 THUMB_CAP→COLLAR path；CMC_MCP_L3 5.9643 为 true-cap endpoint bound；FULL_OPP_L3 6.5160 为 true-cap endpoint bound。固定旧 IDs 的历史 path arithmetic/mesh observations 仍可保留，不能再作为 true-thumb-cap constraint。

扫描记录 **28 个文本文件的 numeric-reference 命中**，每个有 SHA256、line、examples、complete hit count 和 scope classifications。其余只有 semantic 引用的 strict/cap-to-collar/feasibility reports 按 inventory 与 DAG lineage 追踪；历史 PNG 依生成来源分类，没有用 OCR 猜数值。原值的保留、失效解释、未来重算要求分为 HISTORICAL_VALUE_ONLY、INVALIDATED_INTERPRETATION、RECOMPUTE_REQUIRED，详见 [STRICT_BOUND_DEPENDENCY_INVALIDATION_AUDIT.json](STRICT_BOUND_DEPENDENCY_INVALIDATION_AUDIT.json)。

任何依赖“true-cap endpoint bound”的 mesh-limit、retopo、no-legal-weight、cap-constrained recommendation 不得自动继承。历史实际 deformation failure 不会因此消失。新 true-cap bounds 为 **PENDING UNTIL DEPENDENCY RECONCILIATION COMPLETE**：kinematic slots/frames、R2/R3、cap skin driver、重建 endpoint data 均 settled 后，且 static fixtures/targeted checks 通过，才可重算；可与后续 full Stage6A 同阶段安排。本轮没有 path/bound recompute。

## 8. Authority、implementation、validator、reporting 的边界

| Dimension | 具体依赖 | 保留范围 |
|---|---|---|
| AUTHORITY_CONTAMINATION | old membership、R2 seed/R3 anchors、derived region/cut/endpoint | 独立 native/cap37 membership approvals 保留 |
| IMPLEMENTATION_CONTAMINATION | R2A 局部骨数据、R1 bind mu、R1A/B weights、R1C/D/E fields、deformed meshes | 独立 geometry/heads/groups 与实际历史 vectors/measurements 保留 |
| VALIDATOR_CONTAMINATION | cap/nail fixtures、dominance/region/SI buckets、R3 CLASS_A label gates | 数学阈值、raw intersection/edge 值保留，重新验证 semantics |
| REPORTING_ONLY_CONTAMINATION | reused anatomical conclusions、资格状态、bound-based recommendations | 报告与 Human responses 逐字节保留，当前 reuse eligibility 另列 |

Human approval scope 见 [HUMAN_APPROVAL_DEPENDENCY_SCOPE_AUDIT.json](HUMAN_APPROVAL_DEPENDENCY_SCOPE_AUDIT.json)。Stage4 topology/RSSF/nail/CMC geometry、Stage5A hierarchy/origin/无关 heads、independent native corrective review 与最终 cap37 freeze 为 UNAFFECTED_HUMAN_APPROVAL。旧 cap anatomical approval 为 SUPERSEDED_BY_CAP_CORRECTION；historical TIP/IP-tail frame、cap-dependent skin/first-web wrapper、R3、Stage6 qualification 为 REVALIDATION_REQUIRED。被正式 supersede 的早期 Q4=REMOVE response 保持历史身份；最终匹配的 Q4=KEEP response 与冻结结果未改动。

这不重启整只手冻结 authority，只重审具体 cap-derived slots/gates。kinematic endpoint 或 driver 值如需变更，须在独立具体 authority review 后执行，不能把 cap37 membership 审批当作这些值的授权。

## 9. Earliest safe baseline、tiers 与后续顺序

最早安全基底是冻结的 `stage4_blender/stage4c_r2/RIGHT_HAND_ENGINEERING_STAGE4C_R2.blend` 的 unskinned geometry/RSSF/nail/topology，加上 Stage5A 已独立批准的 hierarchy/origin/无关 heads。R2A TIP head/tail、IP tail/local roll 不允许未经针对性 revalidation 自动复用。独立 R1B vector entries 可继承，新候选必须保留原历史 master。证据见 [EARLIEST_SAFE_REBUILD_BASELINE_AUDIT.json](EARLIEST_SAFE_REBUILD_BASELINE_AUDIT.json)。

| Remediation tier | 文件数 | Future action meaning |
|---|---:|---|
| TIER_0 | 1003 | NO ACTION；独立 assets 或只保留历史/corrective provenance |
| TIER_1 | 152 | STATIC REVALIDATION ONLY：fixture/semantics/current-use eligibility |
| TIER_2 | 203 | RECOMPUTE DERIVED AUTHORITY/input context |
| TIER_3 | 30 | REBUILD WEIGHTS / DATA，仅在 authority gates 后 |
| TIER_4 | 144 | FULL DEFORMATION REQUALIFICATION |

Tier 按 1532 文件赋值一次，不与 component tiers 混加；tier 不等于改写历史文件的指令。图与 [CAP_CORRECTION_REMEDIATION_TIERS.json](CAP_CORRECTION_REMEDIATION_TIERS.json) 对应。

未来 recovery sequence（全部 PLANNED ONLY）：

1. CAP_DERIVED_THUMB_KINEMATIC_AUTHORITY_REVALIDATION_R1：先验证 R2A distal endpoints/frames，独立决定是否需要局部改变。
2. CAP_DERIVED_R2_R3_INPUT_RECONCILIATION_R1：处理 seed、重复 live anchors、first-web/nail/cage wrappers；不能只换 CAP union。
3. R3_FULL_RECOMPUTE_AND_AUTHORITY_REVALIDATION_R1：完整 coupled solve 与 derived gates。
4. CAP_SKIN_DRIVER_AND_WEIGHT_AUTHORITY_RECONCILIATION_R1：明确 cap37 driver、原 old9 native INDEX correction、region/whitelist/protection conflicts。
5. TARGETED_RIG_AND_SKIN_DATA_REBUILD_AFTER_APPROVAL：仅批准的 kinematic slots 如需改变时更新；新 skin 基于干净基底与独立 entries，历史文件保留。
6. CAP_FIXTURE_STATIC_VALIDATION_AND_TARGETED_DEFORMATION：old9、cap37、first-web、collar、edge5879。
7. TRUE_CAP_BOUND_RECOMPUTE_AFTER_DEPENDENCY_RECONCILIATION：在 3–6 gates 后重算。
8. FULL_STAGE6A_REQUALIFICATION：在步骤6后；可与步骤7并行。
9. FULL_STAGE6B_REQUALIFICATION：步骤7、8完成后。

不能机械把 R3 放第一位：其 live geometry/tube 输入本身使用 old-cap-derived kinematic data。完整 dependencies/gates 见 [CAP_CORRECTION_RECOVERY_SEQUENCE_R1.json](CAP_CORRECTION_RECOVERY_SEQUENCE_R1.json)。

**NEXT = CAP_DERIVED_THUMB_KINEMATIC_AUTHORITY_REVALIDATION_R1，仅为建议的下一任务，本轮未执行。**

## 10. Evidence limits 与冻结核验

三个 legacy JSON 保持原状，存在原有 syntax errors：`stage5a_freeze/STAGE5A_HUMAN_APPROVAL_FREEZE_R1.json`（L58/C16）、`stage5a_r2a/STAGE5A_R2A_STATUS.json`（L8/C19）、`stage5a_r2b/STAGE5A_R2B_STATUS.json`（L8/C19）。R2A 仍有 direct reference 和 executable/Markdown proof；freeze/R2B status 两个文件的 machine-verifiable provenance 为 UNRESOLVED。没有修补历史 JSON。文件级 UNRESOLVED=2 与 R3 counterfactual boundary effect=UNRESOLVED 是不同计数层级。

Audit 能证明 input dependency 与历史 saved numeric facts，不能证明未运行的 corrected cut/closure、具体新的 weights 或 PASS/FAIL。四图为 source-driven matplotlib diagrams；region projection 显示已有 RSSF/R1B snapshot，不用于重新裁决 native cap anatomy。

冻结检查：1549 / 1549 workspace 文件、6 / 6 外部文件 before==after，audit 目录外新增文件=0；canonical authority hash unchanged。全量 per-file before/after 见 [PROTECTED_STATE_VERIFICATION.json](PROTECTED_STATE_VERIFICATION.json)。

BLEND_FILES_WRITTEN=0；WEIGHT_DELTA=0；GEOMETRY_DELTA=0；TOPOLOGY_DELTA=0；BONE_DELTA=0；JOINT_DELTA=0；R3_runs=0；Stage6_runs=0；strict_bound/path recompute=0；cap_selector_runs=0；R1F_created=false；retopo_runs=0。

## 11. Deliverables

Required report/status 与 9 个专项 JSON 已生成；另有 graph alias、edge5879、Human approval scope、freeze/output verifications、完整 inventory 与静态分析辅助数据。四 PNG：

- [CAP_DEPENDENCY_DAG.png](renders/CAP_DEPENDENCY_DAG.png)
- [OLD_CAP9_TO_R3_PROPAGATION.png](renders/OLD_CAP9_TO_R3_PROPAGATION.png)
- [CAP_DEPENDENT_STAGE5B_REGIONS.png](renders/CAP_DEPENDENT_STAGE5B_REGIONS.png)
- [CAP_CORRECTION_RECOVERY_SEQUENCE.png](renders/CAP_CORRECTION_RECOVERY_SEQUENCE.png)

源脚本只读取既有数据，输出限定本审计目录；不 import/execute production builder。全部 JSON parse、分类/tier总数、DAG 无环、membership hash、region partition 与 PNG dimensions 均验证。视觉核对四 PNG 后通过。

**STOP。没有自动开始下一任务、rebuild、R1F、Stage6、selector、strict-bound recompute 或 retopo。**
'''
(O/'CAP_DEPENDENCY_BLAST_RADIUS_AUDIT_R1_REPORT.md').write_text(REPORT,encoding='utf-8')
STATUS={'execution':'CAP_DEPENDENCY_BLAST_RADIUS_AUDIT_R1','status':'READ_ONLY_AUDIT_COMPLETED','canonical_authority_status':can['status'],'canonical_vertex_count':37,'canonical_face_count':25,'combined_authority_hash':ch,
    'artifact_counting_unit':'Unique preexisting workspace file, one primary class/tier; logical DAG nodes excluded','artifact_count':1532,'classification_counts':dict(classes),'remediation_tier_counts':dict(tiers),'excluded_protected_infrastructure_count':17,
    'DAG_nodes':23,'DAG_edges':41,'DAG_acyclic':True,'R3_revalidation_level':'R3_FULL_RECOMPUTE','R3_full_recompute_required':'YES','R3_boundary_likely_affected':'UNRESOLVED',
    'Stage5B_earliest_contaminated_stage':'R1 via old-cap-derived R2A rig','first_explicit_cap_membership_skin_write':'R1A','earliest_safe_rebuild_baseline':'Frozen Stage4C_R2 unskinned geometry + independent Stage5A hierarchy/origin/unrelated heads; local R2A TIP/IP-tail/frame authority pending',
    'future_reuse_rebuild_required':{'R1B':'YES','R1C':'YES','R1D':'YES','R1E':'YES'},'historical_R1B_status':'FROZEN HISTORICAL PRODUCTION MASTER','historical_R1C_R1D_R1E':'HISTORICAL_ONLY; failed candidate files/verdicts preserved',
    'cap_dependent_review_envelope_vertices':1485,'cap_independent_reusable_vector_entries':1931,'edge5879_dependency_verdict':'PARTLY_CAP_DERIVED','edge5879_numeric_and_defect_evidence':'RETAINED',
    'Stage6A_qualification_status':'QUALIFICATION_VERDICT_NEEDS_REVALIDATION','Stage6B_qualification_status':'QUALIFICATION_VERDICT_NEEDS_REVALIDATION','old_strict_bound_interpretations_invalidated':'YES','strict_reference_artifact_count':28,
    'new_strict_bound_recompute_timing':'After kinematic/R2/R3/skin reconciliation and targeted fixtures/checks; may parallel future full Stage6A','recovery_sequence':'CAP_CORRECTION_RECOVERY_SEQUENCE_R1.json','NEXT':SEQ['NEXT'],'next_task_started':False,
    'frozen_workspace_files':1549,'frozen_external_files':6,'all_protected_before_equal_after':True,'new_files_outside_audit_directory':0,'legacy_JSON_parse_errors':3,'unresolved_artifacts':2,**ZERO,'STOP':True}
dump('CAP_DEPENDENCY_BLAST_RADIUS_AUDIT_R1_STATUS.json',STATUS)
required=['CAP_DEPENDENCY_BLAST_RADIUS_AUDIT_R1_REPORT.md','CAP_DEPENDENCY_BLAST_RADIUS_AUDIT_R1_STATUS.json','CAP_DEPENDENCY_DAG.json','CAP_DIRECT_REFERENCE_AUDIT.json','R3_OLD_CAP9_INFLUENCE_RADIUS_AUDIT.json','STAGE5B_CAP_DEPENDENT_WEIGHT_REGION_AUDIT.json','STAGE6_CAP_DEPENDENCY_AUDIT.json','STRICT_BOUND_DEPENDENCY_INVALIDATION_AUDIT.json','EARLIEST_SAFE_REBUILD_BASELINE_AUDIT.json','CAP_CORRECTION_REMEDIATION_TIERS.json','CAP_CORRECTION_RECOVERY_SEQUENCE_R1.json']
imgs=['CAP_DEPENDENCY_DAG.png','OLD_CAP9_TO_R3_PROPAGATION.png','CAP_DEPENDENT_STAGE5B_REGIONS.png','CAP_CORRECTION_RECOVERY_SEQUENCE.png']
rows=[]
for n in required+['renders/'+n for n in imgs]:
    p=O/n;assert p.is_file()and p.stat().st_size>0
    r={'path':n,'sha256':sha(p),'bytes':p.stat().st_size}
    if p.suffix=='.png':
        with Image.open(p)as im:r['dimensions']=list(im.size);im.verify()
        assert min(r['dimensions'])>1000
    elif p.suffix=='.json':j(n)
    rows.append(r)
for p in O.glob('*.json'):json.loads(p.read_text(encoding='utf-8'))
dump('OUTPUT_VERIFICATION.json',{'status':'PASS','required_deliverable_count':15,'required_files':rows,'all_new_JSONs_parse':True,'artifact_classes_sum':1532,'tiers_sum':1532,'DAG_acyclic':True,'region_partition_sum':3416,'canonical_combined_hash_verified':True,'four_PNG_visual_checks':'PASS after final layout correction; saved-graph/cap semantics clearly labeled','protected_state_verification':'PROTECTED_STATE_VERIFICATION.json','protected_files_unchanged':True,**ZERO,'STOP':True})
print(json.dumps({'status':'READ_ONLY_AUDIT_COMPLETED','required_outputs':15,'workspace_hashes_unchanged':1549,'external_hashes_unchanged':6,'new_files_outside_audit':0,'classes':dict(classes),'tiers':dict(tiers),'NEXT':SEQ['NEXT'],'STOP':True},ensure_ascii=False))
