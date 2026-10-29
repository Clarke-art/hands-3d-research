import sys
sys.dont_write_bytecode=True
from common import *
from PIL import Image
NAME='PROXIMAL_EXCLUSIVE_SHARED_EXTENT_AUTHORITY_R1';S=read(OUT/'STATIC_SUMMARY.json');BLOCK=S['blocker']
cs=read(OUT/'PROXIMAL_CROSS_SECTION_TRANSITION_AUDIT.json');sector=read(OUT/'THUMB_LOCAL_SHARED_SECTOR_EVIDENCE.json')
rows=read(OUT/'PROXIMAL_FOUR_ROLE_MAP_R1.json')['vertices'];support=read(OUT/'PROXIMAL_GRAPH_SURFACE_SUPPORT_AUDIT.json')
T=read(OUT/'THUMB_BRANCH_CONTINUITY_AUDIT.json');I=read(OUT/'INDEX_BRANCH_CONTINUITY_AUDIT.json')
ir=I['true_topological_rings']['unique_maximal_core']
checks=[]
def check(name,condition):
    assert condition,name
    checks.append({'name':name,'status':'PASS'})
check('Cached geometry identity: native/RSSF/corrected original edges and faces identical',all(J[k]['edges']==E and J[k]['faces']==F for k in ['NATIVE','CORRECTED']))
check('Corrected/RSSF frozen world geometry identical',J['CORRECTED']['vertices_world_m']==J['RSSF']['vertices_world_m'])
check('All3416 vertices accounted once in partial evidence map',len(rows)==NV and [r['vertex_id'] for r in rows]==list(range(NV)))
check('No retained INDEX ingredient relabelled shared',all(rows[v]['role']=='INDEX_EXCLUSIVE' for v in INDEX_SOURCES))
check('All frozen web points shared and no hard pin',all(rows[v]['role']=='SHARED_NEUTRAL' for v in WEB) and read(OUT/'FIRST_WEB_R3_ROLE_AUTHORITY_R1.json')['hard_pin_count']==0)
check('All cap37/nail retained without new selection',all(rows[v]['role']=='THUMB_EXCLUSIVE' for v in CAP|NAILS['thumb']))
check('Each enumerated true ring has a degree2 cycle and only original mesh edges',all(len(r['edge_ids'])==len(r['vertex_ids']) and all(sum(v in E[e] for e in r['edge_ids'])==2 for v in r['vertex_ids']) for b in [T,I] for r in b['true_topological_rings']['rings']))
check('Local blocker is fixed-web intersection, not native nearest partition',len(T['true_topological_rings']['rings'])==9 and all(r['frozen_web_in_core'] for r in T['true_topological_rings']['rings']))
check('First complete ring has shared sector3/16, regular degree4',len(sector['known_shared_ring_vertices'])==3 and sector['ring_vertex_count']==16 and sector['closed_regular_valence4'])
check('INDEX diagnostic core preserves all145 source ingredients',INDEX_SOURCES<=set(ir['core_including_ring']['vertex_ids']))
check('G3_K2 reconstructed statically with exact unsupported spur',support['G3_K2']['vertices']['count']==963 and support['G3_K2']['edge_count']==1882 and support['G3_K2']['non_face_supported_vertices']==[3049] and support['G3_K2']['wire_only_edge_endpoints']==[[1891,3049]])
check('No final graph/sample/radius/tube artifact falsely populated',read(OUT/'R3_GRAPH_DOMAIN_CANDIDATE_R2.json')['final_candidate_vertex_ids'] is None and read(OUT/'THUMB_TUBE_RADIUS_AUTHORITY_PROPOSAL_R1.json')['radius_mm'] is None and read(OUT/'CORRECTED_THUMB_TUBE_ANCHOR_CANDIDATE_R2.json')['candidate_vertex_ids'] is None)
pngs=sorted((OUT/'renders').glob('*.png'));check('All11 required evidence PNGs present',len(pngs)==11)
pnginfo=[]
for p in pngs:
    with Image.open(p) as im:
        im.verify()
    with Image.open(p) as im:
        check('PNG nonblank '+p.name,im.size==(2100,1200) and np.asarray(im.convert('RGB')).std()>10)
        pnginfo.append({'name':p.name,'size':list(im.size)})
dump('STATIC_VERIFICATION.json',{'status':'PASS','checks':checks,'image_metadata':pnginfo,'visual_inspection':['THUMB_EXCLUSIVE_RING_EXTENT.png','PROXIMAL_ROLE_MAP_DORSAL.png','G3K2_VS_PROPOSED_DOMAIN.png'],'scope':'Topology/payload/scalar checks only; not a solve or deformation test','R2_runs':0,'R3_Dijkstra_full_fields':0,'R3_mincut':0,'R3_closure':0,'Stage6_runs':0})
status={'round':NAME,'mode':'READ_ONLY_NARROW_ANATOMICAL_TOPOLOGICAL_DOMAIN_AUTHORITY_REVIEW','PROXIMAL_EXCLUSIVE_SHARED_EXTENT_AUTHORITY_R1':'FAIL_CLOSED','four_role_map':'UNRESOLVED','formal_guard':'UNRESOLVED','final_role_counts':{'THUMB_EXCLUSIVE':None,'INDEX_EXCLUSIVE':None,'SHARED_NEUTRAL':None,'OUTSIDE_COUPLED_DOMAIN':None},'partial_known_input_counts':S['fixed_role_counts'],'thumb_last_stable_exclusive_ring':None,'thumb_ring_blocker':'All9 complete topology loops enclosing thumb anchors include frozen web; first ring has3 shared vertices of16 at corrected arc71.544666..74.642942mm.','index_last_stable_ring':'STRUCTURAL_CANDIDATE_ONLY_16_VERTEX_RING','index_ring_vertex_ids':ir['vertex_ids'],'index_ring_axial_extent_mm':ir['corrected_chain_arc_min_max_mm'],'index_diagnostic_core_count':329,'first_web_role':'SHARED_NEUTRAL_GRAPH_ONLY_CANDIDATE','minimal_shared_support_count':None,'final_graph_vertex_count':None,'final_graph_edge_count':None,'final_graph_connected':None,'final_graph_surface_supported':None,'diagnostic_graph':{'vertices':471,'edges':903,'components':4,'connected':False,'surface_supported':False,'unsupported_vertices':12,'wire_only_edges':11},'wrist_palm_leakage_count':None,'G3K2_comparison_native_wrist_candidates':19,'tube_sample_authority':'UNRESOLVED','tube_sample_count':None,'corrected_tube_radius_mm':None,'tube_anchor_count':None,'native_INDEX_conflicts_in_thumb_tube':None,'shared_neutral_conflicts_in_thumb_tube':None,'uncomputed_conflicts_are_not_zero':True,'thumb_strong_source_proposal':'UNRESOLVED','first_web_hard_pin_count':0,'CMC_cage_role':'GEOMETRY_PROTECTED_NOT_OWNERSHIP_HARD_SOURCE; graph role assignment blocked','thenar_palm_role':'LIMITED_SHARED_SUPPORT_OR_OUTSIDE; no hard source; extent blocked','R3_graph_domain':'UNRESOLVED','unary_contract':'BLOCKED','cost_unit_candidate':'CORRECTED_MM','cost_authority_status':'CANDIDATE_PENDING_HUMAN_APPROVAL','cost_provenance_reopened':False,'Human_Review_required':True,'Human_Review_page_generated':False,'Human_Review_reason':'No unique final candidate. Region-level sector frontier evidence is required first.','R2_runs':0,'R3_runs':0,'R3_Dijkstra_full_fields':0,'R3_mincut':0,'R3_closure':0,'skin_rebuilds':0,'Stage6_runs':0,'strict_bound_recompute':0,'BLEND_FILES_WRITTEN':0,'WEIGHT_DELTA':0,'GEOMETRY_DELTA':0,'TOPOLOGY_DELTA':0,'BONE_DELTA':0,'JOINT_DELTA':0,'production_files_written':0,'old_labels_used_as_truth':False,'historical_R2_R3_labels_loaded':False,'G3K2_used_only_as_comparison':True,'NEXT':BLOCK,'NEXT_scope':'Define one thumb MCP/IP shared-sector frontier around frozen v1396/v1399/v1402/v2774, including its intersection with intact circumferential rings. Preserve all FIRST_WEB21 and cap/nail/rig memberships; do not reopen their approval. No broad research or solver run.','STOP':True}
dump(NAME+'_STATUS.json',status)
st='\n'.join('| '+k+' | '+str(v['slices'])+' | '+(f"{v['last_clean']['station_mm']:.6f} / {v['last_clean']['distal_count']}" if v['last_clean'] else 'none')+' | '+str(v['first_marker_merge']['web_hit'] or 'other digit anchors')+' |' for k,v in cs['summary'].items())
image_list='\n\n'.join(f'### {p.stem}\n\n![{p.stem}](renders/{p.name})' for p in pngs)
report=f'''# {NAME}

**FAIL_CLOSED**。本轮把 blocker 缩小到 **{BLOCK}**：thumb MCP/IP 段上，frozen FIRST_WEB 的局部 shared 扇区如何与仍完整的 circumferential digit tube 相接。没有以最近链、native winner、历史标签或连通性代替解剖 authority。

已完成完整截面扫描、真实原始边环遍历、逐顶点部分 evidence map、surface support 审查与11张静态图片。未形成唯一四角色完整范围；radius/sample/tube/strong union/最终graph/unary均没有填入猜测值。Human Review页面未生成。

## 保留的输入和读取范围

cap37/25faces、corrected rig、v284、INDEX source ingredients、nail/cap wrapper、NO HISTORICAL LABEL INJECTION保持。Stage4C_R2 RSSF与native原始geometry通过上轮缓存的source hash及提取hash验证；edges/faces/stable IDs一致。此次没有启动Blender，没有调用旧R2/R3模块，也未加载旧R2/R3 labels。

单位仅引用上一轮CORRECTED_COMMON_MM_SEMANTICS，状态仍为CANDIDATE_PENDING_HUMAN_APPROVAL。没有重审provenance、freeze单位或更改TAU/3=1.296068315566mm与×1000候选。

## 真正局部的阻塞证据

在原始mesh上，以face cyclic order的opposite-edge traversal枚举closed loops；只执行既有T-01代码的 `vcycle / opposite_at / walk` 三个纯拓扑函数，**未执行含旧partition/Dijkstra的模块主体**。闭合环移除后，以独立tip所在component识别远端分支，要求其包含已固定cap/nail或INDEX source ingredients，且排除其他digit/wrist anchors与frozen web。这里没有native Voronoi选择。

thumb找到9条能包住其独立锚点的完整环。每条的远端区域都包含frozen first-web。最远端环有16个valence4顶点，其中 **v1396、v1399、v2774** 为KNOWN_SHARED；下一近端环还引入 **v1402**。第一个环corrected arc范围为 **71.544666–74.642942mm**，IP站为74.642942mm。全部9条环的vertex/edge/face sets和轴向范围在 `THUMB_BRANCH_CONTINUITY_AUDIT.json / true_topological_rings`。

该环shared三点只占一个局部角扇区：native最小包络角 **{sector['states']['NATIVE']['known_shared_minimum_circular_span_deg']:.6f}°**，RSSF **{sector['states']['RSSF']['known_shared_minimum_circular_span_deg']:.6f}°**。角度基准取同digit独立nail dorsal cue，normal/valence/incident faces逐点记录在 `THUMB_LOCAL_SHARED_SECTOR_EVIDENCE.json`。这只描述扇区，不把44°阈值发明成新region rule。

结论并非first-web21批准无效，也不是要求移除这4点。它说明**完整横环不能直接充当此处的exclusive/shared解剖分界**；shared membership已经落在完整规则tube的一部分。需要局部sector frontier，不能选择某个环深或把native稳定core升级为truth。

## Cross-sections与连续性

每个digit比较native engineering axis、native MCP→TIP axis与RSSF live MCP→TIP axis。轴向station取相邻vertex projection值的中点，逐事件扫描，不用任意固定步长或两环深。plane与原始polygon相交，以crossed edge IDs为节点；单个degree2闭环且绕axis的winding为±1才记circumferential_complete。四交点面明确标记，不静默triangulate。

| Variant | 扫描station数 | 最后marker-free平面截面 station mm / distal点数 | 首次合并 |
|---|---:|---|---|
{st}

所有thumb首次遇到shared marker的截面仍是完整circumference，因此没有可用的“独立tube在此断开/融合”几何事件。不同native方向给出121与136点的marker-free distal component，证明平面方向影响界面。进一步检查mesh边端点后，三个方向都没有一个同时包住全部fixed thumb anchors、又完全避开known-shared crossed-edge endpoints的完整候选ring。JSON明确区分plane intersection clean与mesh-vertex-supported exclusive ring，避免把连续截面和离散membership混为一谈。

INDEX找到13条分支环，其中10条满足无shared/source冲突及完整surface support；按distal component包含关系只有一个maximal ring。其16个顶点为 `{ir['vertex_ids']}`，围成329点结构core，corrected arc **0.000000–2.432774mm**。145个固定INDEX source ingredients均在其中，与frozen web无交集。这个结构结果保留，但未把它独立拼成获批四角色全域。

## First-web与最小support

FIRST_WEB_21保持SHARED_NEUTRAL_GRAPH_ONLY候选，hard-pin count=0。未找到要求其中任何点成为独立THUMB/INDEX hard source的既有authority；权重没有参与判定。21点induced graph有 **11/6/4** 三个组件，仅2个完整面；共有76个顶点位于其incident-face context，这76点**没有**自动升级为shared。

作为诊断，121点thumb plane core +329点INDEX topology core +21点web共有 **471 vertices /903 edges /4 components**，12点无完整incident face支撑，11条wire-only edge，surface-supported=NO。它不是final graph，且没有通过加点来强行连接。最小anatomically defensible support仍未确定，所以不能给出minimum support count。

## G3_K2 comparison与outside

G3_K2仅作comparison：963 vertices/1882 edges/1 component；**v3049** 无完整face support，wire为 **(1891,3049)**。相对471点诊断域，多出492点；其中19点属于native wrist结构候选。492不是已证实的excess palm数量，19也不是biological leakage verdict，二者均不能用native winner作truth。逐点差集及surface证据见 `G3K2_COMPARISON_ONLY_AUDIT.json`。

完整OUTSIDE边界尚未建立。仅其它digit nail/terminal与独立wrist landmark共128点可以保留为明确outside input evidence；未把剩余general palm用距离/nearest标签强制排除。

## 部分四角色记录与下游阻塞

`PROXIMAL_FOUR_ROLE_MAP_R1.json`逐3416点记录role、evidence_basis、confidence、source memberships、transition reason。确定输入/局部提案计数为THUMB57、INDEX145、SHARED21、OUTSIDE landmarks128，另3065点明确UNASSIGNED。**这些不是完整extent计数**。null role不是第五个solver role，也不能默认为OUTSIDE；该文件是partial evidence map，不是solver input。

`INDEPENDENT_DIGIT_DOMAIN_GUARD_R2.json`没有伪装成formal guard：status UNRESOLVED、guard payload null。只有formal exclusive region成立后才可产生几何hard sources。没有让native INDEX凭thumb proximity重新进入THUMB。

因此本轮不选择tube sample、统计量、radius、tube anchors或metacarpal corridor；相关要求的JSON均是明确blocked record。sample的未来必要条件已记录：formal exclusive + MCP..IP +稳定ring/sector，排除shared、web、index-facing transition、cap bulb、nail-special surface以及可追溯joint/pole outlier。未通过重算radius来绕过region前置条件，也未复刻10.4735或上一轮10.149390。

THUMB强源仅保留cap37与nail共57个独立landmarks，最终union未组装；future同ID多来源只保留provenance tags并仅一份hard capacity。INDEX既有145点保留，known web conflict=0；因最终shared boundary未定，final-boundary conflict仍为null。

CMC保持GEOMETRY_PROTECTED / NOT OWNERSHIP HARD SOURCE；graph role由最终domain决定。73-coordinate construction只是近似映射candidate，本轮部分role map下73点都尚未assigned，不能宣称已精确确定其graph role。全冻结mesh hash/equality保护cage，不改geometry。thenar/palm仅可为limited shared support或outside，无THUMB hard pin；extent仍blocked。

R3_GRAPH_DOMAIN_CANDIDATE_R2与R3_UNARY_FIELD_INPUT_CONTRACT_CANDIDATE_R3均BLOCKED。future距离定义保留mm edge-geodesic到unique sources，shared不作源、outside不入图；没有实际计算任何R3 full field。

## NEXT / Human Review

唯一NEXT：**{BLOCK}**。

只解决thumb MCP/IP表面上frozen v1396/v1399/v1402/v2774所在shared扇区的连续边界，以及它如何与完整circumferential rings相接；保持全部first-web21/cap/nail/rig批准状态。这应是一个局部区域规则/边界审查，不是900点逐点审批，也不是再次泛研究。现有证据未给出唯一sector frontier，不能生成九问最终authority审批页面。

## 冻结与静态核验

输入hash与完整cache拓扑identity核验通过；闭环degree2、固定source不变、web无hard pin、G3 spur复现及11张PNG完整性检查见 `STATIC_VERIFICATION.json`。运行计数：R2=0、R3 full fields/mincut/closure=0、skin rebuild=0、Stage6=0、strict-bound recompute=0、BLEND_FILES_WRITTEN=0。

WEIGHT/GEOMETRY/TOPOLOGY/BONE/JOINT DELTA全部0。所有既有workspace文件和6个external Human/authority文件before==after；见 `FROZEN_HASH_VERIFICATION_R1.json`。本轮只写此独立audit目录。

**STOP。FAIL_CLOSED。**

## 可视证据

图中pale区域仅为结构诊断，灰色未分配，不表示OUTSIDE；橙色web membership冻结。所有图明确标识没有final role/graph/sample/anchor。native与RSSF使用相同vertex IDs，marker为x-ray叠加。

{image_list}
'''
(OUT/(NAME+'_REPORT.md')).write_text(report,encoding='utf8')
before=read(OUT/'FROZEN_HASHES_BEFORE.json');after={};diff=[]
for bucket,data in before.items():
    after[bucket]={}
    for name,h in data.items():
        p=ROOT/name if bucket=='workspace' else Path(name);hh=sha(p) if p.exists() else None;after[bucket][name]=hh
        if h!=hh:diff.append({'path':str(p),'before':h,'after':hh})
new=[str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file() and OUT not in p.parents and '.git' not in p.parts and str(p.relative_to(ROOT)) not in before['workspace']]
assert not diff and not new,(diff,new)
dump('FROZEN_HASHES_AFTER.json',after)
dump('FROZEN_HASH_VERIFICATION_R1.json',{'status':'PASS','all_before_equal_after':True,'workspace_files':len(before['workspace']),'external_files':len(before['external']),'changed_files':diff,'new_files_outside_audit_directory':new,'production_files_written':0,'BLEND_FILES_WRITTEN':0,'WEIGHT_DELTA':0,'GEOMETRY_DELTA':0,'TOPOLOGY_DELTA':0,'BONE_DELTA':0,'JOINT_DELTA':0,'proof':'Byte identity of all pre-existing files; no Blender or production writer invoked.'})
dump('OUTPUT_HASH_MANIFEST.json',{'kind':'AUDIT_PACKAGE_NOT_INPUT_CONTRACT','files':{str(p.relative_to(OUT)):sha(p) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='OUTPUT_HASH_MANIFEST.json'},'combined_input_contract_hash':None})
print('FAIL_CLOSED;',len(before['workspace']),'+',len(before['external']),'frozen files unchanged;',len(checks),'checks PASS; 11 PNGs. NEXT='+BLOCK+'; STOP.')
