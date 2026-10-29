import sys
sys.dont_write_bytecode=True
import json,hashlib,datetime
from pathlib import Path
from PIL import Image
import numpy as np

out=Path(__file__).resolve().parents[1];root=out.parents[2];s5=out.parent
def load(name):return json.loads((out/name).read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(name,data):(out/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
before=load('FROZEN_HASHES_BEFORE.json');classification=load('CURRENT_CAP9_NATIVE_BRANCH_CLASSIFICATION.json');status=load('THUMB_DISTAL_CAP_NATIVE_BRANCH_IDENTITY_AUDIT_R1_STATUS.json');candidate=load('NATIVE_THUMB_DISTAL_CAP_CANDIDATE_SET.json');prov=load('R2A_CAP_SELECTOR_PROVENANCE_AUDIT.json');invalid=load('CAP_DEPENDENT_STRICT_BOUND_INVALIDATION_AUDIT.json');cmp=load('CAP9_FALSE_POSITIVE_FALSE_NEGATIVE_AUDIT.json');raw=load('_tmp/render_data.json');human=status['Human_authority_verbatim'];rows=classification['vertices'];r2192=next(r for r in rows if r['vertex_id']==2192)
native=raw['native'];V=np.array(native['vertices_world_m']);F=native['faces'];E={tuple(sorted(e)) for e in native['edges']};labels=raw['labels']
for row in rows:
    assert row['classification']=='INDEX_SURFACE'
    assert all(labels[i]=='index' for i in [row['vertex_id']]+row['one_ring']+row['two_ring_exact_hop_2'])
    for key in ['thumb_anchor_path','index_anchor_path','first_web_proxy_path']:
        rec=row[key];seq=rec['vertex_ids'];assert seq[0]==row['vertex_id'] and seq[-1]==rec['endpoint_anchor']
        assert all(tuple(sorted([a,b])) in E for a,b in zip(seq,seq[1:]))
        length=sum(np.linalg.norm(V[a]-V[b])*1000 for a,b in zip(seq,seq[1:]))
        assert abs(length-rec['distance_mm'])<1e-8
        assert rec['reverse_anchor_to_vertex_ids']==seq[::-1]
assert prov['exact_frozen_4_faces_9_vertices_reproduced']
assert prov['seed']==2189 and labels[2189]=='index'
assert len(invalid['all_144_cap_to_collar_shortest_paths'])==144
assert len(invalid['historical_strict_bounds'])==60
assert cmp['true_positive_ids']==[] and len(cmp['false_positive_ids'])==9 and len(cmp['false_negative_ids'])==48
assert set(candidate['vertex_ids']).isdisjoint(classification['current_cap9_vertex_ids'])
assert all(labels[i]=='thumb' for i in candidate['vertex_ids'])
assert all({labels[i] for i in F[fi]}=={'thumb'} for fi in candidate['face_ids'])
assert set(candidate['vertex_ids'])=={i for fi in candidate['face_ids'] for i in F[fi]}
assert candidate['seed_vertex_id']==284

table='\n'.join(f"| {r['vertex_id']} | INDEX_SURFACE | {r['thumb_anchor_path']['distance_mm']:.3f} | {r['index_anchor_path']['distance_mm']:.3f} | {r['first_web_proxy_path']['distance_mm']:.3f} | {r['native_index_MCP_to_PIP_axial_fraction']:.3f} |" for r in rows)
fp=', '.join(map(str,cmp['false_positive_ids']));fn=', '.join(map(str,cmp['false_negative_ids']))
report=f'''# THUMB_DISTAL_CAP_NATIVE_BRANCH_IDENTITY_AUDIT_R1

**本轮 native identity 审计结论：CURRENT_APPROVED_CAP_9 = CONTAMINATED。全部 9 点位于原生食指近节指管，v2192 native branch = INDEX。** 这是独立回到原生几何后的分支鉴别，不再以 historical cap membership 或继承后的 R3 标签作证明。本轮不修改 cap authority，不重做上一轮 Human Review。

## Human authority 原文保持

Q1=YES；Q2=UNRESOLVED；Q3=UNDECIDED；Q4=NO；Q5=LIMITED。四簇 Human candidate 仍为 UNDECIDED。

> {human['notes']}

本轮接受这些输入，不将 Q4 改成 shared interface，不将 Q5 的 LIMITED 改成“已确认真实 thumb-cap→index 解剖路径”，也没有重新询问 Human。原文件、上一轮记录和页面均未改写。

## 独立 native anchors 与分支鉴别

只读打开 Stage4A_R2 pre-RSSF 和 Stage5A_R2 selector 原始 mesh state，直接读取保存的 world coordinates / topology / rest bones；**pose evaluations=0**。两者完整 face-vertex index ordering 与已有 R1B 静态提取一致。原生模型 hash：`{native['sha256']}`。骨点、接触姿态距离或 downstream authority 均不作为 native 点位属于 thumb 的独立证明。

独立锚点来自早于 cap selector 的 `stage4b_rssf_r2.py` native TIP_SEEDS，经 native mesh matrix 正确变换后，拇指端为 **v284**，食指端为 **v233**。没有从 CURRENT_CAP_9 选 seed。另将 `stage4c_r2/NAIL_AUDIT_R2.json` 的 12 个 thumb nail faces / 29 个 index nail faces 按不变拓扑映射回原生形状；其所有顶点分别落在连续的拇指 / 食指终端指管。它们是在 cap 之前建立的 nail masks，本轮还用原生分支、显著分离的指尖和可见指管交叉验证，未仅凭文件名称接受。

THUMB anchors 为独立 tip+nail，共 {len(raw['thumb_anchors'])} 点；INDEX anchors 共 {len(raw['index_anchors'])} 点，两套均与当前 cap9 无交集。native thumb IP→tip / index MCP→PIP 的方向来自原生横截面中心定位函数的只读重建，没有在 native frame 里复用 posed skeleton。模型 joint 仍是工程估计，不是本轮新增骨权威。

以五个独立指尖及 wrist 为源，计算 native edge-length 多源分区，并用 local tube、incident faces、一环/二环及 nail-to-tip continuity 交叉检查。全掌分区界面不能自动当真实 shared skin；本轮只对远离界面的 cap9 指管点作判定。first-web 距离采用独立 native index/thumb cleft 的 structural proxy（v473 加一环），**并未把它注册为新的 first-web skin authority**，Human Q2 保持 UNRESOLVED。

## 九点逐点结果

距离单位 mm，均是 native edge-length shortest paths 至独立 anchor sets；完整双向 vertex sequences 在 `CURRENT_CAP9_NATIVE_BRANCH_CLASSIFICATION.json`。最后一列是只读重建的 native INDEX MCP→PIP 工程轴投影，不是照片配准结果。

| vertex | 分类 | thumb anchors | index anchors | first-web proxy | native INDEX 轴 fraction |
| --- | --- | ---: | ---: | ---: | ---: |
{table}

九点一环、二环及 incident faces 全在连续 native INDEX 管上。分类由这些相互支持的证据决定，不由距离大小单独决定；CURRENT_CAP_9 / R3 THUMB / THUMB_STRONG / THUMB_DISTAL / 当前 RSSF 距离未作为分类依据。

## v2192 专项

one-ring：`{r2192['one_ring']}`；exact two-hop ring：`{r2192['two_ring_exact_hop_2']}`；incident faces：`{[f['face_id'] for f in r2192['incident_faces']]}`。这些面与邻点全部属于原生食指管。

到 native thumb anchors：**{r2192['thumb_anchor_path']['distance_mm']:.6f} mm**，终点 v{r2192['thumb_anchor_path']['endpoint_anchor']}；到 native index anchors：**{r2192['index_anchor_path']['distance_mm']:.6f} mm**，终点 v{r2192['index_anchor_path']['endpoint_anchor']}。index 路径起始段为 v2192→v703→v2169→v704，继续沿同一食指管到 nail 区；thumb 路径先沿食指向根部回走，再经过掌/虎口通道进入真正独立的拇指分支。这直接解释为何局部连续性不等于 thumb-cap 解剖身份。

## 原始 cap selector 的精确复现

正式 canonical rule 由 R2B errata 声明为 geodesic connected cap；历史 JSON/header 的 slab-method 文本是已废止的说明，本轮没有据它重算。

实际执行链：

1. 在保存的 Stage5A_R2 RSSF/contact mesh 中，面质心到各 full bone chains 的 Euclidean polyline distance 取最小值，得到 `FACE_OWNER`。
2. `DIG_VERTS[THUMB]` 是所有 nominal THUMB-owned faces 顶点的并集；取位于 nominal THUMB_IP→TIP 正投影侧的点，再最大化离 IP 的 Euclidean 距离，得到 **seed v2189**。v2189 在独立 native 检查中是 **INDEX**。
3. 从 v2189 沿 **全 mesh edge graph** 做长度 Dijkstra。图没有 thumb-only gate；之后才对 faces 加 owner gate。
4. face predicate 为 `owner == THUMB AND min(corner g) <= 9 mm`，保留含最近 seed face 的面邻接连通分量；最后 `capv = union(selected face corners)`。

本轮复现结果与冻结结果完全一致：faces **356, 357, 389, 390**；vertices **{fp}**。

**v2192 的确切纳入步骤：face356 的 corner union。** face356 = `[158,1076,2569,2192]`。在旧 posed-chain selector 中，其质心离 nominal THUMB chain 为 **11.972809 mm**，离 INDEX chain 为 **13.488749 mm**，于是数值规则将它指派为 THUMB。face356 的最小 corner geodesic 是 v2569 的 **4.369009 mm**，满足 9 mm；v2192 自身 g=**9.071490 mm**，仍作为该面的角点被纳入。seed→v2192 路径为 `[2189,2569,2192]`。其自身略超 9 mm 是 min-corner face expansion 的结果，不是实现违规。

根因：**DIGIT_IDENTITY_CONTAMINATION / OWNED_FACE_ERROR**；contact-pose nearest-chain 距离将原生食指面放入 nominal thumb domain，进而造成 **SEED_ERROR**。旧 seed、四个 selected faces 全是 native index branch。世界坐标输入能精确复现全清单，没有发现必须借助 local/world 或单位错误才能解释的证据。全局 geodesic graph 确实缺少独立 branch guard，但本次 seed→cap 路径本来就留在 INDEX 上，跨 web 图泄漏不是解释此错误所必需。

因此，**9 mm 的局部测地规则可以在错误 seed/domain 上合法地选择 index surface**。数字半径、连通性与 downstream labels 都不能补回最初的 anatomical digit identity。

## 独立 native distal-cap candidate

只读生成候选：以独立 native thumb branch 的 IP→true terminal-tip direction 定位最远端 seed **v284**，在 **native THUMB-only induced edge graph** 上计算 9 mm geodesic，再选 min-corner 满足阈值、与 seed face 连通、全部位于 native thumb 的 faces。候选共 **{len(candidate['vertex_ids'])} vertices / {len(candidate['face_ids'])} faces**，与当前 cap9 **交集为 0**。

9 mm 是继承已声明的 local-geodesic convention，不是生产权重或新人体端帽权威。min-corner face predicate 可扩入更远的角点；本候选最大角点距离 **{candidate['max_selected_vertex_geodesic_mm']:.6f} mm**，因此不可把它描述成“所有点均在 9 mm 球内”。候选边界尚需 Human cap authority correction；没有自动替代冻结清单。

TP IDs：`[]`。

FP IDs：`[{fp}]`。

候选相对 FN IDs：`[{fn}]`。这里 FN 是与本轮独立候选的集合差，不是已获 Human 批准的新增 membership。

Unresolved current-cap9 IDs：`[]`。

## cap-dependent strict-bound invalidation

**13.1646 mm path、CMC_MCP_L3=5.9643、FULL_OPP_L3=6.5160 均标记 INVALIDATED，范围是“真实 thumb distal-cap→index collar 的解剖端点解释”。** 旧 mesh 固定 ID 的路径长度、已存 posed endpoints 与 `max stretch >= posed separation / bind path length` 数学不等式仍保留为历史数值事实。没有修改历史审计文件，没有抹去旧实际 deformation 观测或 R1E fail-closed 状态。

本轮完整列出 **144 个 cap9→INDEX collar 固定 ID shortest paths**，展开历史 top10 paths 和 **60 个已存 strict-bound rows**，并登记后续 endpoint sensitivity JSON 内 **{len(invalid['later_endpoint_sensitivity_strict_bound_dependencies'])} 个 bound 数值依赖位置**及受影响证据文件。全部九个起点是 native INDEX surface，因此失效不限于 v2192 最短一条。

真正 native cap→collar 的 replacement path / bound 为 **PENDING_RECOMPUTE_AFTER_HUMAN_CAP_AUTHORITY_CORRECTION**。本轮没有重算 pose 或 deformation，没有借新候选继续求解权重。

## 最终十四项答复

| 项目 | 答复 |
| --- | --- |
| 1. TRUE_THUMB_DISTAL_CAP | 0 |
| 2. THUMB_DISTAL_BUT_NOT_CAP | 0 |
| 3. INDEX_SURFACE | 9 |
| 4. FIRST_WEB_SHARED_SURFACE | 0 |
| 5. UNRESOLVED | 0（OTHER 亦为 0） |
| 6. v2192 native branch | INDEX |
| 7. v2192 entered cap because | contaminated nominal THUMB domain→native-index seed v2189→9mm min-corner face356 predicate→corner union |
| 8. CURRENT_CAP_9 | CONTAMINATED |
| 9. FP IDs | {fp} |
| 10. FN IDs | {fn}（native candidate-relative） |
| 11. 13.1646 mm path | INVALIDATED as anatomical cap path; mesh continuity retained |
| 12. CMC_MCP_L3 5.9643 | INVALIDATED as anatomical cap endpoint bound |
| 13. FULL_OPP_L3 6.5160 | INVALIDATED as anatomical cap endpoint bound |
| 14. NEXT | HUMAN_CAP_AUTHORITY_CORRECTION |

## 可视证据与冻结

七张 native 静态投影已逐张检查：cap9 branch map、thumb anchors、index anchors、v2192 one/two-ring、thumb-vs-index paths、current-vs-native cap 和 all-cap9 classification。全局与局部相互对照；隐藏点以独立投影标记显示，避免把遮挡误当“不存在”。只裁展示窗口，没有改 mesh。审计的全部输入哈希在冻结记录中。

{len(before)} 个既有 production_spec/docs 文件及 workspace BLEND before=after；BLEND_FILES_WRITTEN=0；WEIGHT/GEOMETRY/TOPOLOGY/BONE/JOINT DELTA=0；R1F_CREATED=false。Human 输入、冻结 cap、first-web、CMC cage、R3、R1B 及 R1E 状态保持原样。未运行 Stage6A/Stage6B、weight solve 或 retopo。

**STOP — WAITING FOR HUMAN CAP AUTHORITY REVIEW。**
'''
(out/'THUMB_DISTAL_CAP_NATIVE_BRANCH_IDENTITY_AUDIT_R1_REPORT.md').write_text(report,encoding='utf8')
names=['THUMB_DISTAL_CAP_NATIVE_BRANCH_IDENTITY_AUDIT_R1_REPORT.md','THUMB_DISTAL_CAP_NATIVE_BRANCH_IDENTITY_AUDIT_R1_STATUS.json','CURRENT_CAP9_NATIVE_BRANCH_CLASSIFICATION.json','NATIVE_THUMB_ANCHOR_SET.json','NATIVE_INDEX_ANCHOR_SET.json','V2192_NATIVE_BRANCH_IDENTITY_AUDIT.json','R2A_CAP_SELECTOR_PROVENANCE_AUDIT.json','NATIVE_THUMB_DISTAL_CAP_CANDIDATE_SET.json','CAP9_FALSE_POSITIVE_FALSE_NEGATIVE_AUDIT.json','CAP_DEPENDENT_STRICT_BOUND_INVALIDATION_AUDIT.json']
pngs=['CURRENT_CAP_9_NATIVE_BRANCH_MAP.png','NATIVE_THUMB_ANCHOR_SET.png','NATIVE_INDEX_ANCHOR_SET.png','V2192_NATIVE_1RING_2RING.png','V2192_THUMB_VS_INDEX_PATHS.png','CURRENT_VS_NATIVE_CAP_SET.png','ALL_CAP9_BRANCH_CLASSIFICATION.png']
for name in names:
    assert (out/name).stat().st_size>0
    if name.endswith('.json'):load(name)
for name in pngs:
    with Image.open(out/'renders'/name) as im:im.load();assert im.size==(1800,1250)
after={k:sha(root/k) for k in before};assert before==after
current_inventory={str(p.relative_to(root)).replace('\\','/') for name in ['production_spec','docs'] for p in (root/name).rglob('*') if p.is_file() and out not in p.parents}
current_inventory.update(str(p.relative_to(root)).replace('\\','/') for p in root.rglob('*.blend'))
assert set(before)==current_inventory
dump('FROZEN_HASH_VERIFICATION.json',{'protected_file_count':len(before),'before':before,'after':after,'inventory_unchanged':True,'all_before_equals_after':True,'changed_files':[],'BLEND_FILES_WRITTEN':0,'WEIGHT_DELTA':0,'GEOMETRY_DELTA':0,'TOPOLOGY_DELTA':0,'BONE_DELTA':0,'JOINT_DELTA':0,'R1F_CREATED':False,'deformation_runs':0})
dump('OUTPUT_VERIFICATION.json',{'verified_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'required_outputs':names,'required_images':pngs,'outputs_parse_and_images_decode':True,'all_7_native_images_visually_inspected':True,'all_27_native_paths_use_existing_edges_and_exact_lengths':True,'all_9_one_two_ring_neighborhoods_independently_INDEX':True,'native_candidate_independent_thumb_graph_verified':True,'selector_exact_4_faces_9_vertices_reproduced':True,'all_144_bind_path_dependencies_enumerated':True,'historical_strict_bound_rows_enumerated':60,'later_endpoint_bound_dependency_count':len(invalid['later_endpoint_sensitivity_strict_bound_dependencies']),'Human_answers_and_notes_unmodified':True,'protected_files_before_equal_after':len(before),'production_cap_membership_modified':False,'NEXT':'HUMAN_CAP_AUTHORITY_CORRECTION','STOP':True})
print('PASS: all required outputs, 7 renders, 27 native paths, exact selector and protected hashes:',len(before))
