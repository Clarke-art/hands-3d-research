"""Verify and report this local read-only audit; never import or execute solve code."""
import sys
sys.dont_write_bytecode=True
from local_data import *
from PIL import Image

NAME='THUMB_FROZEN_WEB_PARTIAL_CIRCUMFERENCE_FRONTIER_AUTHORITY_R1'
S=read(OUT/'THUMB_PROXIMAL_RING_STACK_R1.json')
C=read(OUT/'THUMB_RING_TO_RING_CORRESPONDENCE.json')
D=read(OUT/'LOCAL_DIAGNOSTIC_STRIP_SETS.json')
M=read(OUT/'THUMB_PARTIAL_CIRCUMFERENCE_ROLE_MAP_R1.json')
T=read(OUT/'LOCAL_TERMINATION_NONUNIQUENESS_CONTROLS.json')
L=read(OUT/'THUMB_SHARED_SECTOR_LONGITUDINAL_CONTINUITY_AUDIT.json')
Q=read(OUT/'LOCAL_STATIC_SUMMARY.json')
checks=[]
def check(name,condition):
    checks.append({'check':name,'pass':bool(condition)})
    assert condition,name
check('9 disjoint 16-vertex closed rings',len(S['rings'])==9 and len(S['vertex_set']['vertex_ids'])==144 and all(len(r['vertex_sequence'])==16 and len(set(r['vertex_sequence']))==16 for r in S['rings']))
for r in S['rings']:
    seq=r['vertex_sequence']
    check(r['ring_id']+' cyclic original edges',all(set(E[ei])=={a,b} for ei,a,b in zip(r['edge_sequence'],seq,seq[1:]+seq[:1])))
check('strict distal-to-proximal axial means',all(a['axial_mean_mm']>b['axial_mean_mm'] for a,b in zip(S['rings'],S['rings'][1:])))
check('8 complete face annuli',len(C['pairs'])==8 and len(S['face_ids'])==128 and all(len(p['face_ids'])==16 and p['one_to_one'] and p['closed_quad_annulus'] and p['strip_face_components']==1 for p in C['pairs']))
for p in C['pairs']:
    check(p['distal_ring']+' real face-supported bijection',all(set(E[r['longitudinal_edge_id']])=={r['distal_vertex'],r['proximal_vertex']} and len(r['supporting_face_ids'])==2 for r in p['vertex_correspondence']))
check('native/RSSF exact topology identity',J['NATIVE']['edges']==E and J['NATIVE']['faces']==F)
check('frozen 4 seeds verified in 21 membership',len(WEB)==21 and SEEDS<=WEB and WEB&set(S['vertex_set']['vertex_ids'])==SEEDS)
check('F1 unique two-face minimum connector',T['F1_minimum_face_connector']['all_minimizers']==[[1178,1179]] and set(D['F1']['shared_vertex_ids'])==SEEDS|{305,306})
check('F3 diagnostics counts',len(D['F3']['shared_vertex_ids'])==27 and len(D['F3']['role_extension_ids'])==23 and len(D['F3']['shared_face_ids'])==16 and len(D['F3']['left_frontier_edge_ids'])==len(D['F3']['right_frontier_edge_ids'])==8)
for k in ['F1','F3']:
    a=D[k]['surface_audit']
    check(k+' full face support without wires/dangling points',a['surface_supported'] and not a['wire_only_edge_ids'] and not a['dangling_vertex_ids'])
    check(k+' frozen anchor compatibility',not D[k]['cap_conflict_ids'] and not D[k]['nail_conflict_ids'] and D[k]['complement_cap_nail_continuity']['all_fixed_thumb_anchors_in_tip_component'])
check('F3 single cyclic arc and native/RSSF stable mapping',L['F3_single_arc_per_ring'] and L['F3_frontier_correspondence_continuous'] and L['F3_native_RSSF_membership_identical'])
check('remaining 117 arc vertices reach cap/nail',Q['F3_complement_count']==117 and Q['cap_nail_continuity']['all_remaining_stack_vertices_in_tip_component'])
check('5 distinct supported termination controls',len(T['termination_alternatives'])==5 and all(a['surface_audit']['surface_supported'] and not a['cap_overlap'] and not a['nail_overlap'] and a['cap_nail_continuity'] for a in T['termination_alternatives']))
check('no seed-complement exclusivity inferred',M['counts']=={'UNRESOLVED':140,'SHARED_NEUTRAL':4} and not any(r['role']=='THUMB_EXCLUSIVE' for r in M['vertices']))
check('no unsupported extension or approval page',not (OUT/'THUMB_WEB_SHARED_NEUTRAL_ROLE_EXTENSION_R1.json').exists() and not (OUT/'THUMB_PARTIAL_CIRCUMFERENCE_FRONTIER_HUMAN_REVIEW.html').exists())
pngs=sorted((OUT/'renders').glob('*.png'));check('10 requested scientific evidence renders',len(pngs)==10)
image_rows=[]
for p in pngs:
    with Image.open(p) as im:
        im.load();pixels=np.array(im.convert('RGB'))
        check(p.name+' readable nonblank image',im.width>=1800 and im.height>=1000 and pixels.std()>10)
        image_rows.append({'name':p.name,'size':list(im.size),'sha256':sha(p)})
dump('LOCAL_STATIC_VERIFICATION_R1.json',{'status':'PASS','checks':checks,'images':image_rows,'validation_type':'Static topology, set provenance, image integrity and negative termination controls only','forbidden_execution_performed':False})

# Rehash every pre-existing file, plus externally stored Human authority responses.
before=read(OUT/'FROZEN_HASHES_BEFORE.json')
after={'workspace':{p:sha(ROOT/p) for p in before['workspace']},'external':{p:sha(p) for p in before['external']}}
allnow={str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file() and OUT not in p.parents and '.git' not in p.parts}
added=sorted(allnow-set(before['workspace']));removed=sorted(set(before['workspace'])-allnow)
changed={group:[p for p,h in before[group].items() if after[group][p]!=h] for group in before}
assert not added and not removed and not any(changed.values())
dump('FROZEN_HASHES_AFTER.json',after)
freeze={'status':'PASS','before_equals_after':before==after,'workspace_file_count':len(before['workspace']),'external_authority_file_count':len(before['external']),'changed_files':changed,'added_outside_audit_directory':added,'removed_files':removed,'protected':'All pre-existing workspace files except .git, and six external authority/Human source files; includes cap, rig, web, nail, cage, Stage4/5, R2/R3, Stage6 and Human responses','WEIGHT_DELTA':0,'GEOMETRY_DELTA':0,'TOPOLOGY_DELTA':0,'BONE_DELTA':0,'JOINT_DELTA':0,'BLEND_FILES_WRITTEN':0}
dump('FROZEN_HASH_VERIFICATION_R1.json',freeze)
next_action='THUMB_SHARED_STRIP_LONGITUDINAL_STOP_RULE_AUTHORITY: only resolve the stop rule on the identified local web-connected strip—distal flat R00 cut versus non-nail tapered continuation through faces1176/1213, and proximal continuation beyond R08 through faces3032/3033. A source-backed local shared-to-exclusive transition rule is missing. Do not reopen generic proximal-domain research or assemble a role extension from connectivity.'
status={'authority':NAME,'authority_status':'FAIL_CLOSED','relevant_ring_count':9,'rings_with_partial_shared_sector_count':None,'frozen_shared_seeds':sorted(SEEDS),'shared_sector_extension_vertex_count':None,'shared_sector_extension_face_count':None,'left_frontier_edge_count':None,'right_frontier_edge_count':None,'distal_termination':'UNRESOLVED','proximal_termination':'UNRESOLVED','final_single_continuous_sector_per_ring':None,'final_longitudinal_continuity':None,'native_RSSF_topology_stable':True,'diagnostic_F3':{'partial_ring_count':9,'shared_total_vertices':27,'additional_shared_role_vertices':23,'shared_support_faces':16,'left_edges':8,'right_edges':8,'single_continuous_sector_per_ring':True,'longitudinal_continuity':True,'native_RSSF_topology_stable':True,'surface_supported':True,'wire_only_edges':0,'remaining_arc_vertices':117,'remaining_arc_is_exclusive_authority':False,'authority_candidate_approved':False},'FIRST_WEB_membership_changed':False,'cap37_changed':False,'nail_changed':False,'THUMB_EXCLUSIVE_complement_candidate_count':None,'known_role_map_counts':M['counts'],'role_extension_status':'NOT_FORMED','Human_Review_required':True,'Human_review_page_generated':False,'Human_review_note':'Authority intervention will be required for the missing local transition stop rule; the seven-question candidate approval page is withheld because no unique candidate exists. Frozen seed membership is not being reopened.','R2_runs':0,'R3_runs':0,'Stage6_runs':0,'skin_rebuild_runs':0,'strict_bound_runs':0,'retopo_runs':0,'BLEND_FILES_WRITTEN':0,'historical_labels_used_as_truth':False,'cost_unit_candidate':'CORRECTED_COMMON_MM_SEMANTICS_CANDIDATE_PENDING_HUMAN_APPROVAL','frozen_protection':freeze,'single_remaining_local_blocker':Q['remaining_blocker'],'NEXT':next_action,'STOP':True}
dump(NAME+'_STATUS.json',status)

ring_rows='\n'.join(f"| {r['ring_id']} | {r['axial_mean_mm']:.6f} | {', '.join('v'+str(v) for v in r['known_shared_vertices']) or '—'} |" for r in S['rings'])
control_rows='\n'.join(f"| {r['name']} | {', '.join(map(str,r['added_face_ids'])) or '—'} | {r['diagnostic_shared_vertex_count']} | PASS |" for r in T['termination_alternatives'])
visuals='\n\n'.join(f'![{p.stem}](renders/{p.name})' for p in pngs)
report=f'''# {NAME}

**FAIL_CLOSED。未形成可供批准的唯一 frontier；未生成 solver-role extension 或 Human Review HTML。**

本轮仅检查已有 9 条 thumb 环、8 条真实 quad face strips，以及两端各两排面的局部延续。没有重新研究全局 proximal domain。4 个冻结 shared seeds 有效；真实拓扑对应已确定。缺失的是该局部 shared strip 的停止 authority，尤其 distal 非 nail 侧可继续而 proximal 没有可证终止的位置。不能把分析范围裁切线充当解剖边界。

## 输入与冻结约束

几何取自已有 `READ_ONLY_LIVE_EXTRACTION.json` 的 NATIVE/RSSF 状态，corrected chain 取 CORRECTED bones。缓存 SHA256 对照原 reconciliation manifest；独立 cap、nail、FIRST_WEB source 路径与哈希列于 `INPUT_VERIFICATION.json`。使用原始 mesh faces/edges 和 stable vertex IDs，不读取旧 R2/R3 ownership labels，不把 skin weights、最近 chain winner 或连通性当作 anatomy。

cap37、corrected rig、FIRST_WEB21、nail、CMC cage、INDEX ingredients 及既有 Human responses 不改动。first-web 默认 shared-neutral graph-only，hard pins=0；CMC 保持 geometry-protected / non-hard-source。CORRECTED_COMMON_MM_SEMANTICS 仅引用 pending-Human 状态，没有复审单位。

## Ring stack 与真实面带对应

9×16=144 个互不重叠环顶点，8×16=128 个面。相邻环各有 16 条真实纵向边，构成一一对应及完整闭合 quad annulus。R00 使用最小 ID 及较小首邻居作循环索引约定；之后仅沿真实 edge/face strip 传递列编号。索引本身不赋予角色，没有角度最近匹配。

| Ring（distal→proximal） | corrected chain mean arc mm | frozen shared |
|---|---:|---|
{ring_rows}

MCP arc={S['MCP_arc_mm']:.6f} mm；IP arc={S['IP_arc_mm']:.6f} mm。每环完整 vertex/edge sequence、axial min/max、到 MCP/IP 的 signed arc 与 Euclidean distance，见 `THUMB_PROXIMAL_RING_STACK_R1.json`。各环之间的 face IDs 和逐顶点对应见 `THUMB_RING_TO_RING_CORRESPONDENCE.json`。

R00 seeds 为 columns4/5/6：v1399/v2774/v1396；R01 column5 为 v1402。逐点 incident faces、一环/两环邻域及 surface connections 已记录于 `FROZEN_WEB_SEED_CONTEXT_AUDIT.json`。其余 17 个 frozen web vertices 与此 stack 没有共同 face，也没有一跳或两跳接触；本轮没有制造角度投影或跨区域路径来扩张它们。

## F1–F4 局部候选比较

| Family | 可复核结果 | authority 限制 |
|---|---|---|
| F1 | 唯一最小 seed-connected patch：faces1178/1179；6 点，其中新增支撑点 v305/v306 | 最小 seed cover 不是 shared→exclusive 停止证据；不能因此在 R01 后终止 |
| F2 | native/RSSF normals 对独立 index root、web context 的方向描述；记录 sign crossings 与局部 normal turns | 仅辅助；两种几何状态的 sign crossing edges 可变，不能独立裁决边界或终止 |
| F3 | columns4–6 沿真实面带传到9环：27点，16面，左右链各8边；23点不属于 frozen web21 | 全 stack 延续是假设；R00/R08 是诊断裁切，不是 authority termination |
| F4 | NOT_FORMED | F1/F3 在共同两环的横向列一致，但纵向 extent 不一致，且没有可证终止依据 |

F1 的最小性通过枚举 stack 内 128 面中的一面/两面连接器独立验证，唯一最小解为1178/1179。F3 每环是一个连续3点弧，绝不把整环设 shared。左右各再加一真实 face column 的诊断方案同样能保持 surface support；因此“最小列宽”也不能自行升级成解剖 exclusivity。当前左右链只是证据最小的 topology candidate，尚未成为最终 authority。

所有完整 vertex/face/edge ID 集合保存在 `LOCAL_DIAGNOSTIC_STRIP_SETS.json`；最终候选字段在 `THUMB_SHARED_SECTOR_FRONTIER_CANDIDATE_AUDIT.json` 明确为 null，而不是空集合。没有手工批准额外点，也没有以4个 seeds 的补集直接定义 THUMB_EXCLUSIVE。

## 纵向连续、法向与 native/RSSF 稳定性

F3 使用同样的 vertex IDs、face IDs、左右 frontier topology，在 native/RSSF 完全一致。单环是一个连续 arc；邻环最大 centroid 变化为 native {Q['max_centroid_jumps']['NATIVE']:.6f}°、RSSF {Q['max_centroid_jumps']['RSSF']:.6f}°，没有180°跳转、全环扩张或中断后重现。左右轨迹与宽度逐环详见 continuity JSON。

这些角度仅描述几何。本轮用局部 ring-center tangent 与 nail dorsal cue 定义角度坐标，R00 宽度约43.469592°/43.774876°；此前约44.024973°/44.323624°来自不同轴基准，不能互作阈值或据此改变 membership。本轮没有 ±22°、44°、normal-dot 阈值或 nearest winner 生成规则。

4 个 seeds 的 web-facing normal dots 在两种几何状态均为正，支持其局部 web-facing 位置；这不意味着正 dot 的其余顶点都应 shared，也不证明负 dot 就 exclusive。法向 sign crossing 在 repose 后不固定，因此 F2 不能补上缺失的局部边界 authority。

## Distal / proximal termination：非唯一性的具体证据

Distal R00 两条 sector 边都存在唯一 quad continuation。face1177 包含 frozen thumb nail v304，约束该侧不能直接纳入默认 shared support；相邻 face1176 无 cap/nail 冲突，下一排 face1213 同样无冲突。故“停在 R00 的平截线”和“只向非 nail 侧做 taper”并未被现有证据唯一裁决。不是因为下一环缺 seed 就停止。

Proximal R08 两侧继续进入 faces3032/3033，再下一排也有真实 quad continuation；局部没有 topology stop/pole 或固定 anchor 冲突支持把 R08 当作 broader-palm transition 的确定边界。这里只检查两排面的局部证据，不扩张 palm role map。

以下仅为 negative controls，全部通过真实面支撑、零 wire/dangling、cap/nail 无冲突及连接保留。它们证明结构可行性不足以选定停止位置；没有任何一个被批准：

| 诊断停止方案 | F3 外追加 faces | shared 诊断点数 | surface/anchor gates |
|---|---|---:|---|
{control_rows}

`DISTAL_PROXIMAL_TERMINATION_AUDIT.json` 提供逐边、逐面、opposite edge 和 valence；`LOCAL_TERMINATION_NONUNIQUENESS_CONTROLS.json` 提供上述多解。distal termination=UNRESOLVED；proximal termination=UNRESOLVED。

## Surface support、cap/nail 连续与局部角色

F1/F3 所有支撑顶点均属于其完整原始 faces；induced edges 全部有完整面支撑，wire-only edges=0，dangling vertices=0。纵向8个面带加两端一排/两排 probes 说明结果不是单个低分辨率面角的偶然连接。但“多排支持”仍不授予解剖停止 authority。

从 distal thumb surface 排除 F3 后，剩余238点为一个连通 component，包含 cap37、thumb nail 及 stack 剩余117点。这个测试只证明相容性，117点尚未被判为 THUMB_EXCLUSIVE。

正式局部 map 覆盖144点：4 SHARED_NEUTRAL（仅已冻结 seeds），140 UNRESOLVED，0 已裁决 THUMB_EXCLUSIVE。各环 A/B/C final state 保留 null；F3 诊断分类为9条 PARTIAL_SHARED_SECTOR。其余局部点不得伪装成 FULLY_THUMB_EXCLUSIVE 或 FULLY_SHARED。没有 INDEX_EXCLUSIVE / OUTSIDE 全域裁决。

FIRST_WEB21 membership 与未来 R3_SHARED_ROLE_EXTENSION 是不同 authority。本轮没有生成 `THUMB_WEB_SHARED_NEUTRAL_ROLE_EXTENSION_R1.json`。23 只是 F3 假设的非 web21 支撑点数，16 是整个假设扇区的支撑面数，不是已批准的新 anatomical web faces。shared hard pins 始终为0。

## 验证、冻结与停止

`LOCAL_STATIC_VERIFICATION_R1.json`：{len(checks)} 项静态检查通过，包括真实循环边、face bijections、native/RSSF identity、唯一 seed connector、多解 negative controls、保守 role map 和10张 PNG 的完整性。没有运行 solver。

`FROZEN_HASH_VERIFICATION_R1.json`：{len(before['workspace'])} 个既有工作区文件 + {len(before['external'])} 个外部 authority/Human 文件 before==after；审查目录外新增/删除/变更均为0。WEIGHT_DELTA=GEOMETRY_DELTA=TOPOLOGY_DELTA=BONE_DELTA=JOINT_DELTA=0。R2=R3=Stage6=skin rebuild=strict bound=retopo=0；BLEND_FILES_WRITTEN=0。

唯一 NEXT：**THUMB_SHARED_STRIP_LONGITUDINAL_STOP_RULE_AUTHORITY**。在已识别局部 web-connected 面带内，为 shared→exclusive transition 提供独立停止依据，具体区分 R00 平截与 faces1176/1213 非 nail 侧 taper，并确定 R08 后 faces3032/3033 延续何处停止。当前横向最小列宽也是候选，不能因后续停止规则被确定便自动冻结左右链；须以该局部 transition 证据复核。不得回到 generic proximal-domain research，不得依靠连通性选择。

Human authority 仍需介入缺失的局部停止依据；由于未形成唯一完整候选，未生成成功用的7问 Human Review 页面。没有要求重新批准4个 frozen seeds 的既有 membership。

**STOP。**

## 局部可视证据（全部为诊断，不是已批准 role extension）

{visuals}
'''
(OUT/(NAME+'_REPORT.md')).write_text(report,encoding='utf8')
dump('OUTPUT_EVIDENCE_HASH_MANIFEST_R1.json',{'scope':'New audit directory only','files':{str(p.relative_to(OUT)):sha(p) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='OUTPUT_EVIDENCE_HASH_MANIFEST_R1.json' and '__pycache__' not in p.parts}})
print(json.dumps({'status':'FAIL_CLOSED','checks_passed':len(checks),'frozen_workspace_files':len(before['workspace']),'frozen_external_files':len(before['external']),'before_equals_after':before==after,'NEXT':Q['remaining_blocker'],'STOP':True},indent=2))
