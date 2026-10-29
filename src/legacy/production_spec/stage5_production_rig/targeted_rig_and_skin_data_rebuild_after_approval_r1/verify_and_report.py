"""Read-only verification of saved extraction, approved scope and evidence.
Writes only new reports/manifests in this task directory; never saves a blend.
"""
from common import *
import math, struct
from collections import Counter

S=read(OUT/f'{PHASE}_STATUS.json')
A=read(OUT/'AUTHORIZED_WEIGHT_WRITE_SET_R1.json')
SRC=read(OUT/'LIVE_SOURCE_DATA_R1.json')
PRE=read(OUT/'CANDIDATE_PRE_SAVE_PAYLOAD_R1.json')
POST=read(OUT/'CANDIDATE_CLEAN_REOPEN_PAYLOAD_R1.json')
GEN=read(OUT/'DETERMINISTIC_WEIGHT_GENERATION_R1.json')
C=read(OUT/'SKIN_CONTINUITY_STATIC_CHECK_R1.json')
CAP=read(PROPOSAL/'CAP37_SKIN_DRIVER_AUTHORITY_R1.json')
OLD=read(PROPOSAL/'OLD_CAP9_SKIN_CORRECTION_AUTHORITY_R1.json')
WEB=read(PROPOSAL/'FIRST_WEB_SKIN_WEIGHT_WRAPPER_R2.json')
CONT=read(PROPOSAL/'SKIN_WEIGHT_CONTINUITY_CONTRACT_R1.json')
EDGE=read(OUT/'EDGE5879_WEIGHT_REBUILD_RESULT_R1.json')
CERT=read(OUT/'STATIC_SCOPE_CONFLICT_CERTIFICATE_R1.json')
DON=SRC['R1B']['weights']; W=POST['weights']; EDGES=POST['mesh']['edges']
sets=[set(A[k]) for k in ['SAFE_REUSE','TARGETED_REVALIDATION','REBUILD_REQUIRED']]
safe,target,write=sets
assert list(map(len,sets))==[2401,771,244]
assert sum(map(len,sets))==len(set.union(*sets))==3416
assert set.union(*sets)==set(range(3416))
assert set(GEN['evaluated_ids'])==write and len(GEN['per_vertex'])==244
assert len(W)==len(DON)==3416
changed={i for i in range(3416) if W[i]!=DON[i]}
assert len(changed)==238 and changed<=write
assert all(W[i]==DON[i] for i in safe|target)
assert PRE['mesh']==POST['mesh'] and PRE['rig']==POST['rig']
assert PRE['weights']==W and PRE['group_order']==POST['group_order']
assert POST['rig']==SRC['CORRECTED']['rig']
for k in ['positions_local_m','positions_world_mm','edges','faces','UV_layers','face_material_indices','material_slots']:
    assert POST['mesh'][k]==SRC['STAGE4C']['mesh'][k]
for k in ['matrix_world','matrix_local','matrix_parent_inverse','location','rotation_mode','rotation_euler','scale','parent']:
    assert POST['mesh'][k]==SRC['CORRECTED']['mesh'][k]
assert sha(CANDIDATE)==S['candidate_blend_hash']=='290d2734f80edb25872962bf378dbc4c122d6fafe3fd118b22a6e550ddfcb84a'
bundle=read(PROPOSAL/'SKIN_AUTHORITY_PROPOSAL_BUNDLE_R1.json')
assert digest(bundle)=='a0a3811f00984edce73db6ff4171d72aeaec07e27dbe17936266dec6d9da1340'
for name,h in bundle['proposal_files'].items(): assert sha(PROPOSAL/name)==h
assert RESPONSE.read_bytes()==(OUT/'HUMAN_APPROVAL_RESPONSE_SOURCE_COPY.json').read_bytes()
capids={r['vertex_id'] for r in CAP['per_vertex_surface_evidence']}
webids=set(WEB['membership']['vertex_ids']); oldids=set(OLD['vertex_ids'])
assert len(capids)==37 and len(oldids)==9 and len(webids)==21
assert capids|oldids<=write and webids&write=={3125}
assert all(set(W[i])<=set(OLD['allowed_deform_groups']) for i in oldids)
assert all(set(W[i])<=set(WEB['allowed_deform_groups']) and W[i].get('THUMB_IP_R',0)==0 for i in webids)
# Independently project cap points from the saved corrected joint positions.
def f32(x):return struct.unpack('f',struct.pack('f',x))[0]
def vsub(a,b):return [x-y for x,y in zip(a,b)]
def dot(a,b):return sum(x*y for x,y in zip(a,b))
b=POST['rig']['bones']
points=[b[g]['head_world_mm'] for g in ['THUMB_CMC_R','THUMB_MCP_R','THUMB_IP_R']]+[b['THUMB_IP_R']['tail_world_mm']]
lengths=[math.sqrt(dot(vsub(z,a),vsub(z,a))) for a,z in zip(points,points[1:])]
for i in capids:
    p=POST['mesh']['positions_world_mm'][i]; projections=[]; offset=0
    for k,(a,z) in enumerate(zip(points,points[1:])):
        az=vsub(z,a); mu=max(0,min(1,dot(vsub(p,a),az)/dot(az,az)))
        d2=sum((p[t]-a[t]-mu*az[t])**2 for t in range(3))
        projections.append((d2,k,offset+mu*lengths[k])); offset+=lengths[k]
    _,_,arc=min(projections)
    t=max(0,min(1,.5+(arc-CAP['rule']['s_IP_mm'])/(2*CAP['rule']['h_mm'])))
    u=t*t*t*(t*(6*t-15)+10)
    expected={g:f32(v) for g,v in [('THUMB_IP_R',u),('THUMB_MCP_R',1-u)] if v>0}
    assert W[i]==expected,('Saved cap rule mismatch',i)
for i,w in enumerate(W):
    assert all(math.isfinite(v) and v>=0 for v in w.values())
    assert abs(sum(w.values())-1)<=CONT['normalization']['absolute_tolerance']
    assert len(w)<=CONT['max_influences'] and set(w)<=set(CONT['deform_bones'])
    assert all(w.get(g,0)==0 for g in CONT['helpers']['names'])
def metrics(i,j):
    ds=[abs(W[i].get(g,0)-W[j].get(g,0)) for g in set(W[i])|set(W[j])]
    return max(ds,default=0),sum(ds)
for r in C['all_checked_edges']:
    i,j=EDGES[r['edge_id']]; mx,l1=metrics(i,j)
    assert r['vertex_ids']==[i,j] and r['after']['L_inf']==mx
    assert abs(r['after']['L1']-l1)<1e-14
gates=CONT['static_edge_gates']
bad=[r for r in C['all_checked_edges'] if r['after']['L_inf']>gates['max_single_group_jump_proposal'] or r['after']['L1']>gates['max_L1_jump_proposal']]
assert len(bad)==64==S['continuity_static_blocker_count']
for r in C['ownership_guard']['per_vertex']:
    i=r['vertex_id']; assert i not in write and W[i]==DON[i]
    assert all(W[i][g]==v and v>0 for g,v in r['forbidden_groups'].items())
assert len(C['ownership_guard']['per_vertex'])==55
for witness in CERT['continuity_impossibility_witnesses']:
    kind=witness['type']
    if kind=='IMMUTABLE_EDGE_EXCEEDS_APPROVED_GATE':
        i,j=witness['vertices']; assert i not in write and j not in write
        assert [W[i],W[j]]==witness['immutable_endpoint_vectors']
        mx,l1=metrics(i,j); assert mx>.5 or l1>1
    elif kind=='FORBIDDEN_GROUP_ZERO_VS_IMMUTABLE_NEIGHBOR':
        i,j,g=witness['write_vertex'],witness['immutable_vertex'],witness['group']
        assert i in write and j not in write and W[i].get(g,0)==0
        assert W[j][g]==witness['immutable_neighbor_weight']>.5
    else:
        i=witness['vertex_id']; assert i not in write and W[i]==DON[i]
assert S['candidate_verdict']=='FAIL_CLOSED_REBUILD_OR_STATIC_INTEGRITY'
assert S['Stage6_runs']==S['R3_reruns']==S['pose_deformation_runs']==S['strict_bound_recomputations']==0
assert not S['candidate_static_pass'] and not S['candidate_deformation_pass'] and not S['production_promotion']
before=read(OUT/'FROZEN_HASHES_BEFORE.json'); after=inventory()
removed=sorted(set(before)-set(after)); added=sorted(set(after)-set(before))
modified=[p for p in before.keys()&after.keys() if before[p]!=after[p]]
assert not removed and not added and not modified,('Protected history changed',removed,added,modified)
dump('FROZEN_HASHES_AFTER.json',after)
dump('FROZEN_HASH_VERIFICATION_R1.json',{'status':'PASS','protected_file_count':len(before),'modified':modified,'removed':removed,'added_outside_task_directory':added,'historical_blend_writes':0,'only_new_task_directory_written':True})
capresult=read(OUT/'CAP37_WEIGHT_REBUILD_RESULT_R1.json')
oldresult=read(OUT/'OLD_CAP9_WEIGHT_REBUILD_RESULT_R1.json')
webresult=read(OUT/'FIRST_WEB_WEIGHT_REBUILD_RESULT_R1.json')
leakclass=Counter(r['classification'] for r in C['ownership_guard']['per_vertex'])
report=f'''# TARGETED_RIG_AND_SKIN_DATA_REBUILD_AFTER_APPROVAL_R1

结论：**FAIL_CLOSED_REBUILD_OR_STATIC_INTEGRITY**。新 candidate 已创建，244/244 点完成批准规则 evaluation；保存和独立 Blender clean reload 通过。静态 contract 仍有 64 条阻塞边与 55 个历史微量 forbidden influence 点，不能据此推进 targeted deformation。candidate_static_pass=false，candidate_deformation_pass=false，production_promotion=false。

## 审批和输入

唯一审批：`{RESPONSE}`。原始字节复制到 HUMAN_APPROVAL_RESPONSE_SOURCE_COPY.json，notes 原样保留；Q1–Q7 均 YES，全部约束字段逐类型逐值验证。审批只授权本轮 skin authority plan/scope 和新 candidate，不预先批准生成权重、deformation、Stage6 或 production qualification。

| 输入 | 已验证 SHA256 / canonical hash |
|---|---|
| proposal bundle | a0a3811f00984edce73db6ff4171d72aeaec07e27dbe17936266dec6d9da1340 |
| R3 authority | 361f4f25201f5810830dc1bfc4bd2cf19db908aef8945801a63bfd2829197ff0 |
| R3 membership | f57483723e90cc34e0551bf70fac00c7c8cb789dbad5d0e248018fdaddd3741d |
| corrected rig | {sha(CORRECTED)} |
| frozen Stage4C_R2 | {sha(STAGE4)} |
| R1B weight donor | {sha(DONOR)} |

proposal 中所有 component 文件逐字节 hash 验证，包含 cap37、old cap9、FIRST_WEB、reuse set、envelope、continuity contract 和 edge5879 scope。未创建或重新计算 authority；R3 labels 仅用于 guard 和 transition context。

## 候选和逐点写入范围

新 candidate：`{CANDIDATE}`

SHA256：`{sha(CANDIDATE)}`

geometry/topology/UV/mesh coordinates/material assignment 直接继承冻结 Stage4C_R2；全部 21 bones 的 rest/pose transforms、head/tail、local frame、deform flags、origin/hierarchy 与 corrected rig 逐值一致。16 deform groups 继承 R1B 的 group order。5 TIP helpers 为 non-deform，全 mesh 权重为零。

使用 Armature modifier 绑定 corrected rig，保留 corrected mesh parent=None 和全部 object transforms；未 apply transform、改 origin 或 reparent。未计算 pose/deformed geometry。

| 正式分类 | 点数 | 处理 | 实际变化 |
|---|---:|---|---:|
| SAFE_REUSE | 2401 | R1B vector exact copy，不 normalize/prune | 0 |
| TARGETED_REVALIDATION | 771 | R1B vector exact copy；仅 flag | 0 |
| REBUILD_REQUIRED | 244 | 244/244 deterministic rule evaluation | 238 |

三个集合互斥、完整覆盖 3416 点。实际 changed IDs 全部属于批准 244；outside write=0。6 点 evaluation 后与 donor 数值相同，未制造变化。完整 group delta 见 WEIGHT_DELTA_CENSUS_R1.json。

## 批准规则执行

cap37：corrected thumb arc 上按批准 `h={CAP['rule']['h_mm']} mm`、`s_IP={CAP['rule']['s_IP_mm']} mm` 和 centered quintic `6t^5−15t^4+10t^3` 生成 IP/MCP 混合。37 点全 evaluation，31 点实际变化。只有 IP/MCP，无 INDEX/WRIST/TIP；{capresult['IP_exact_one_hot_count']} 点为公式 plateau 导致 IP=1，未把全部 37 点设为 one-hot。83 条 incident edges 的最大 L∞={capresult['one_ring_continuity']['max_after_L_inf']:.12g}、L1={capresult['one_ring_continuity']['max_after_L1']:.12g}，本局部绝对静态 gate 阻塞 0。逐点 before/after、分布和邻接证据均已保存。

其余批准 THUMB rebuild 点按 hash-bound historical centered-base/tube family 与 corrected arc 的连续 profile evaluation。没有将 rig affected 163 点或 fresh boundary 126 点自动扩为 write set。

old cap9：151、158、1061、1074、1076、2189、2192、2569、2577 全部 evaluation 并实际变化；删除旧 THUMB distal override，仅允许 INDEX chain + WRIST。119 个 INDEX rebuild unknown 与唯一可改 shared-web 点联合求解批准的静态 simplex harmonic field；sorted cyclic exact block minimization，lambda=0.01，370 iterations，projected residual={GEN['harmonic_solve']['projected_fixed_point_residual']:.12g}。只用批准的 geometry prior 和 compatible retained INDEX boundary；没有 deformation objective。9 点无 INDEX_MCP one-hot，局部 24 条边阻塞 0，最大 L∞={oldresult['one_ring_continuity']['max_after_L_inf']:.12g}、L1={oldresult['one_ring_continuity']['max_after_L1']:.12g}。9/9 before、after、邻点向量、driver family、dominance、gradient 与 metric 已保存。

FIRST_WEB21：仅 v3125 rebuild 并实际改变；其余 20 点逐值复制。只允许 WRIST_R、THUMB_CMC_R、THUMB_MCP_R、INDEX_MCP_R，全部 THUMB_IP=0、TIP=0。未依据 R3 的 7/14 标签改 one-hot。

edge5879：v1551 与 v3125 都在批准 244 内并实际改变。正式 hash-bound neighborhood 18 点包含 7 rebuild、11 targeted-revalidation；7 点 evaluation，11 点 exact copy，全部 18 点参与静态邻域审计。采用正式分类优先规则，未把 11 点扩为 write set。

端点新向量：

```json
{json.dumps(dict(zip(map(str,EDGE['endpoints']),EDGE['after'])),ensure_ascii=False,indent=2)}
```

edge5879 本边 L∞={EDGE['edge_static_metric']['after']['L_inf']:.12g}，L1={EDGE['edge_static_metric']['after']['L1']:.12g}；其整个批准邻域仍有 {EDGE['approved_neighborhood_continuity']['blocker_count']} 条静态 blocker。历史 R1E deformation defect 仍是有效证据，未用 R1E vector 作为 base，未运行 CMC_MCP_L3 或声称 deformation defect 已消除。

## 静态阻塞与范围冲突

全 mesh 数学检查通过：sum tolerance=1e-5，最大误差 {C['weight_math']['max_sum_error']:.12g}，负值/NaN/Inf/nondeform group/TIP/influence-count 违规均 0，最大 influences=4。

envelope 内部及 crossing 共检查 2089 条边；严格 gate 为单 group jump≤0.5、L1 jump≤1。64 条 blocker 中 44 条接触批准 rebuild，20 条为 copy-only。274 条边比 R1B 增加了至少一个 jump metric（以批准 sum tolerance 记录数值增量）；这些增量完整保存，不等同 274 个绝对 gate blocker，也不代表 pose qualification。

strict forbidden-weight=0 guard 发现 55 点微量历史 residue（{leakclass['TARGETED_REVALIDATION']} TARGETED_REVALIDATION、{leakclass['SAFE_REUSE']} SAFE_REUSE）。全部 exact donor copy，本轮新增违规 0；其中 23 点超过 1e-8，0 点超过 1e-6。未擅自将 guard 改为 1e-6，未清除 copy-only 微量值。TARGETED 点仅标 TARGETED_VALIDATION_FLAG。

以下阻塞不能通过任意合法 244-only 权重求解消除，详见 STATIC_SCOPE_CONFLICT_CERTIFICATE_R1.json：

1. edge1130，v303/v1396 均必须 immutable copy，L∞=0.655587911605835、L1=1.31117582321167 超过 gate；改任意批准 244 点不能改变这条边。
2. edge1234，v338 是 INDEX rebuild，THUMB_MCP 必须 0；v1448 是 copy-only FIRST_WEB，THUMB_MCP 必须保留 1。该 group jump 恒为 1，大于 0.5；调整 solver 参数无法同时满足 support 和 copy contract。
3. 上述 55 个 copy-only 点必须保留历史正 forbidden weight，但严格 guard 要求 0；移除将违反批准 exact-copy/write scope。

因此保留完整 candidate 与可复核失败证据，未增大 scope、改 membership/support、暗调参数或进入下一阶段。局部 cap37/old cap9 的静态 gate 通过不抵消全候选 failure。

## 保存、保护和停止

candidate 保存一次，独立 factory-startup Blender clean reopen 读取 mesh、UV、material、binding、all bones、all 3416 vectors；pre-save 与 reload payload 全部 exact，serialization drift=0。

历史保护核对 {len(before)} 个文件，before=after 全部一致；modified/removed/added outside task directory=0。历史 blend writes=0，candidate blend writes=1。所有新增文件仅在本轮目录。可复核的 raw payload、逐点 delta、authority hashes、static metrics 和冲突证据随报告保存；独立输出核对与 evidence hash manifest 区分 artifact consistency PASS 和 candidate FAIL_CLOSED。

Stage6 runs=0；pose/deformation runs=0；R3 reruns=0；strict-bound recomputations=0；production promotion=false。NEXT=NONE_FAIL_CLOSED_STATIC_GATE_RECONCILIATION_REQUIRED；STOP=true。未推进成功路径 CAP_FIXTURE_STATIC_VALIDATION_AND_TARGETED_DEFORMATION_R1。
'''
(OUT/f'{PHASE}_REPORT.md').write_text(report,encoding='utf-8')
required=[f'{PHASE}_REPORT.md',f'{PHASE}_STATUS.json','AUTHORIZED_WEIGHT_WRITE_SET_R1.json','SAFE_REUSE_EXACT_COPY_AUDIT_R1.json','TARGETED_REVALIDATION_COPY_AUDIT_R1.json','CAP37_WEIGHT_REBUILD_RESULT_R1.json','OLD_CAP9_WEIGHT_REBUILD_RESULT_R1.json','FIRST_WEB_WEIGHT_REBUILD_RESULT_R1.json','EDGE5879_WEIGHT_REBUILD_RESULT_R1.json','WEIGHT_DELTA_CENSUS_R1.json','SKIN_CONTINUITY_STATIC_CHECK_R1.json','RIG_AND_GEOMETRY_NO_DRIFT_AUDIT_R1.json','CANDIDATE_SAVE_REOPEN_VERIFICATION_R1.json',CANDIDATE.name]
assert all((OUT/f).is_file() for f in required)
dump('OUTPUT_VERIFICATION_R1.json',{'artifact_integrity_status':'PASS','candidate_verdict':S['candidate_verdict'],'required_outputs_present':required,'protected_history_exact':True,'exact_copy_and_write_scope_verified':True,'full_save_reopen_payloads_exact':True,'cap_formula_independently_verified':True,'all_recorded_edge_metrics_recomputed':True,'immutable_conflict_witnesses_verified':True,'new_blend_writes_by_this_verifier':0,'Stage6_runs':0,'STOP':True})
manifest={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and p.name!='OUTPUT_EVIDENCE_HASH_MANIFEST_R1.json'}
dump('OUTPUT_EVIDENCE_HASH_MANIFEST_R1.json',{'phase':PHASE,'excluded_self':True,'file_count':len(manifest),'files':manifest,'canonical_files_hash':digest(manifest)})
print(json.dumps({'artifact_integrity':'PASS','candidate_verdict':S['candidate_verdict'],'historical_files_verified':len(before),'changed':len(changed),'blockers':len(bad),'strict_historical_residue_points':55,'STOP':True},indent=2))
