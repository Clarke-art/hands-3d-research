import sys
sys.dont_write_bytecode=True
from common import *
from html import escape
import math
from PIL import Image
W=read(OUT/'FORMAL_DONOR_TRANSFER_WRITE_SET_R1.json');C=read(OUT/'FORMAL_DONOR_TRANSFER_COORDINATES_R1.json');P=read(OUT/'FORMAL_DONOR_TRANSFER_PROVENANCE_R1.json');S=read(OUT/'FORMAL_DONOR_TRANSFER_STRUCTURE_AUDIT_R1.json');B=read(OUT/'FORMAL_DONOR_TRANSFER_BOUNDARY_AUDIT_R1.json');M=read(OUT/'FORMAL_MATCHED_RENDER_MANIFEST_R1.json');Q=read(OUT/'FORMAL_NATIVE_SECTION_COMPARISON_R1.json');I=set(W['vertex_ids'])
assert len(I)==54 and W['WRITE_SET_IDENTITY_MATCH'] and C['MAX_COORD_DELTA_VS_PROBE_MM']==0 and S['status']==B['status']=='PASS'
assert M['render_count']==96
for r in M['renders']:
 with Image.open(OUT/r['path']) as im:assert list(im.size)==r['resolution']
labels=['CURRENT_STAGE4C_R2','OFFICIAL_L1_DONOR','TEMPORARY_FEASIBILITY_PROBE','FORMAL_AMENDMENT_CANDIDATE'];titles=['当前 Stage4C_R2','官方 L1 donor','临时 feasibility probe','正式 amendment candidate'];smokes=['FORMAL_AMENDMENT_CANDIDATE','TEMP_BIND','TEMP_IDX_MCP_15','TEMP_IDX_MCP_30','TEMP_IDX_MCP_45']
inspected=['FOUR_COLUMN_SOLID_REVIEW_R1.png','PRIMARY_VISUAL_INSPECTION_SHEET_R1.png','BIND_IDX_VISUAL_INSPECTION_SHEET_R1.png']+['renders/'+n for n in ['FORMAL_AMENDMENT_CANDIDATE_HUMAN_SOURCE_NATIVE.png','FORMAL_AMENDMENT_CANDIDATE_GRAZING_FLAT.png','TEMP_BIND_SIDE_FLAT.png','TEMP_IDX_MCP_45_GRAZING_FLAT.png']]
visual={'reviewer':'Codex image inspection; Human approval pending','VISIBLE_DENT_STATUS':'ABSENT_PENDING_HUMAN_CONFIRMATION','NEW_VISIBLE_DEFECT':'NONE_OBSERVED_PENDING_HUMAN_CONFIRMATION','natural_valley':'Restored in inspected close/grazing/side views','whole_dorsal_arch':'Engineered current hand retained outside54; no new arch defect observed','new_boundary_hinge_ridge_notch_fold_migration_silhouette_kink':'NONE_OBSERVED_PENDING_HUMAN_CONFIRMATION','inspected_files':inspected,'all_render_paths':[r['path'] for r in M['renders']],'NOT_HUMAN_APPROVED':True}
dump('FORMAL_HUMAN_CONTOUR_REVIEW_R1.json',visual)
bind=read(OUT/'FORMAL_DONOR_TRANSFER_BIND_PREVIEW_R1.json');assert bind['status']=='PASS';bind.update({'DENT_REAPPEARED_IN_BIND':'NO','NEW_BIND_VISIBLE_DEFECT':'NONE_OBSERVED_PENDING_HUMAN_CONFIRMATION','visual_review_scope':'Matched close/grazing/side/full dorsal/native wire; agent observation, Human pending','render_review':visual});dump('FORMAL_DONOR_TRANSFER_BIND_PREVIEW_R1.json',bind)
smoke=read(OUT/'FORMAL_DONOR_TRANSFER_LIMITED_IDX_SMOKE_R1.json');assert smoke['status']=='PASS'
for cid,d in smoke['states'].items():
 assert d['status']=='PASS';d['render_review']='NO_NEW_LOCAL_DONOR_TRANSFER_DEFECT_OBSERVED_PENDING_HUMAN_CONFIRMATION'
smoke['NOT_FULL42']=True;smoke['old9_crossings_adjudicated']=False;dump('FORMAL_DONOR_TRANSFER_LIMITED_IDX_SMOKE_R1.json',smoke)
B['new_ridge_notch_silhouette_kink']='NONE_OBSERVED_PENDING_HUMAN_CONFIRMATION';B['visual_review']=visual;dump('FORMAL_DONOR_TRANSFER_BOUNDARY_AUDIT_R1.json',B)

# Render actual native sections, preserving common physical scale per angle.
(OUT/'sections').mkdir(exist_ok=True)
def plot(angle,groups,name):
 profiles=[p for group in groups for label,_,_ in group for r in Q['stages'][label][str(angle)]['native_triangle_plane_intersections'] for p in r['profile_mm']]
 xmin=min(p[0] for p in profiles)-1;xmax=max(p[0] for p in profiles)+1;ymin=min(p[1] for p in profiles)-1;ymax=max(p[1] for p in profiles)+1
 # Equal physical x/y units and identical axes in all panels.
 scale=min(440/(xmax-xmin),270/(ymax-ymin));width=520*len(groups);bits=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} 400"><rect width="100%" height="100%" fill="#fafafa"/>']
 for col,group in enumerate(groups):
  ox=col*520+55;oy=345;xy=lambda p:(ox+(p[0]-xmin)*scale,oy-(p[1]-ymin)*scale)
  for v in range(math.ceil(xmin),math.floor(xmax)+1,2):
   a,b=xy([v,ymin]),xy([v,ymax]);bits.append(f'<path d="M{a[0]},{a[1]}L{b[0]},{b[1]}" stroke="#ddd"/><text x="{a[0]}" y="365" font-size="11" text-anchor="middle">{v}</text>')
  for v in range(math.ceil(ymin),math.floor(ymax)+1,2):
   a,b=xy([xmin,v]),xy([xmax,v]);bits.append(f'<path d="M{a[0]},{a[1]}L{b[0]},{b[1]}" stroke="#ddd"/><text x="{ox-6}" y="{a[1]+4}" font-size="11" text-anchor="end">{v}</text>')
  for row,(label,title,color) in enumerate(group):
   bits.append(f'<text x="{col*520+15}" y="{22+row*21}" font-size="14" fill="{color}">{escape(title)}</text>')
   for r in Q['stages'][label][str(angle)]['native_triangle_plane_intersections']:
    a,b=map(xy,r['profile_mm']);bits.append(f'<path d="M{a[0]:.5f},{a[1]:.5f}L{b[0]:.5f},{b[1]:.5f}" stroke="{color}" stroke-width="2.2" fill="none"><title>{label} native face {r["face_id"]}</title></path>')
  bits.append(f'<text x="{col*520+200}" y="388" font-size="12">{angle}° | tangent / outward (mm) | native sections</text>')
 bits.append('</svg>');(OUT/'sections'/name).write_text(''.join(bits),encoding='utf-8')
for angle in [0,60,120]:
 plot(angle,[[(l,t,'#303b42')] for l,t in zip(labels,titles)],f'FOUR_NATIVE_SECTIONS_{angle}.svg')
 plot(angle,[[('OFFICIAL_L1_DONOR','Official L1: frozen rigid display registration','#a24a37'),('FORMAL_AMENDMENT_CANDIDATE','Formal candidate: engineered current hand','#24597f')],[('ANCESTRY_DONOR_TARGET','54 ancestry + frozen RSSF target (current topology)','#a24a37'),('FORMAL_AMENDMENT_CANDIDATE','Formal: native stored coordinates','#24597f')]],f'DONOR_FORMAL_OVERLAY_{angle}.svg')

# Read frozen authority membership only. No path/bound, ownership or skin recomputation.
cap_path=ROOT/'production_spec/stage5_production_rig/stage5b_r1e_human_cap_authority_freeze_r1/THUMB_DISTAL_CAP_CANONICAL_AUTHORITY_R1.json';r3_path=ROOT/'audits/human_r3_fresh_result_authority_freeze_r1/FRESH_R3_OWNERSHIP_AUTHORITY_R1.json';weight_path=R2.parent/'AUTHORIZED_WEIGHT_WRITE_SET_R2.json';true_dir=ROOT/'production_spec/stage5_production_rig/true_cap_bound_recompute_after_dependency_reconciliation_r1'
cap=read(cap_path);r3=read(r3_path);weights=read(weight_path);true=read(true_dir/'CORRECTED_TRUE_CAP_SOURCE_TARGET_AUTHORITY.json');paths=read(true_dir/'TRUE_CAP_STATIC_PATH_ENSEMBLE_R1.json')
faces=C['faces'];edges=C['edges'];incident_faces=[i for i,f in enumerate(faces) if I.intersection(f)];incident_edges=[i for i,e in enumerate(edges) if I.intersection(e)];one_ring=sorted({v for fi in incident_faces for v in faces[fi]});r3labels=r3['membership']['vertex_labels'];historical_touched=[{'source_vertex':p['source_vertex'],'target_vertex':p['target_vertex'],'changed_vertex_ids_on_stored_path':sorted(I.intersection(p['vertex_sequence']))} for p in paths['paths'] if I.intersection(p['vertex_sequence'])]
footprint={'write_vertex_ids':sorted(I),'write_vertex_count':54,'incident_native_face_ids':incident_faces,'incident_native_face_count':len(incident_faces),'incident_edge_ids':incident_edges,'incident_edge_count':len(incident_edges),'native_incident_face_vertex_closure':one_ring,'boundary_diagnostic_edge_ids':B['boundary_edge_ids'],'outer_fixed_fixed_diagnostic_edge_ids':B['outer_fixed_fixed_edge_ids'],'cap37_write_overlap':sorted(I.intersection(cap['vertex_ids'])),'cap37_incident_face_overlap':sorted(set(incident_faces).intersection(cap['face_ids'])),'FIRST_WEB21_write_overlap':sorted(I.intersection(r3['FIRST_WEB21']['membership_vertex_ids'])),'fresh_R3_frozen_domain_write_overlap':sorted(I.intersection(r3['graph']['vertex_ids'])),'fresh_R3_overlap_frozen_labels':{str(i):r3labels[str(i)] for i in sorted(I.intersection(r3['graph']['vertex_ids']))},'fresh_R3_exact_boundary_incident_edge_overlap':sorted(set(incident_edges).intersection(r3['boundary']['edge_ids'])),'approved_317_weight_universe_write_overlap':sorted(I.intersection(weights['approved_write_universe_317'])),'true_cap_frozen_source_endpoint_write_overlap':sorted(I.intersection(true['source']['vertex_ids'])),'true_cap_frozen_target_endpoint_write_overlap':sorted(I.intersection(true['target']['vertex_ids'])),'stored_primary_703_paths_touched':historical_touched,'stored_primary_paths_touched_count':len(historical_touched),'path_overlap_check_is_new_path_or_bound_recompute':False,'metric_change_rule':'Every edge with a moved endpoint changes the potential geometric metric. Existing-path overlap alone does not exclude a new shortest route; rebuild geometry-dependent path/bound results after APPLY without reselecting authority membership.'}
steps=[
 ('S4_LOCAL',[],'Validate separately applied Stage4 derived geometry against this exact candidate hash and54 local targets; topology/payload/outside54 exact, reconciled local true3D contact + boundary + native sections.'),
 ('S5_PROPAGATE',['S4_LOCAL'],'Create independent Stage5 geometry derivative with existing R2 rig and weight payload unchanged; propagate54 positions only by native IDs and verify every protected field. No skin rebuild or weight edit.'),
 ('JOINT_SURFACE',['S5_PROPAGATE'],'Check frozen joints/frames against amended surface and adjacent ring/core; report distances/alignment, preserve bone/joint authority. Direct failure evidence is required before any new authority research.'),
 ('REST_ZERO_BIND',['JOINT_SURFACE'],'Revalidate rest/RSSF/zero/bind and exact zero restoration on real propagated asset. Compare54 shape and whole mesh against expected bind evaluation; temporary preview here is not this qualification.'),
 ('STATIC_SKIN',['REST_ZERO_BIND'],'Rerun static skin compatibility and incident edge/support tests with existing weights and frozen317 write authority; geometry-dependent skin assumptions refreshed, weight vectors unchanged.'),
 ('TRUE_CAP_DERIVED',['REST_ZERO_BIND','STATIC_SKIN'],'Recompute geometry-dependent metric, frozen source37 x frozen target19 path ensemble703 and contextual endpoint pairs1406; rebuild posed-bound cases from frozen required-case manifest and documented sensitivity cases. Preserve cap37/R3/FIRST_WEB memberships and method; no anatomy/ownership re-selection.'),
 ('TARGETED_DEFORM',['STATIC_SKIN','TRUE_CAP_DERIVED'],'Targeted deformation revalidation on propagated asset with existing required-case coverage: donor ROI/index/ring neighborhood, all inherited skin debt interfaces, thumb/cap/nails/FIRST_WEB context and9 independent crossing witnesses. Preserve old acceptance classifications unless separately authorized adjudication.'),
 ('FULL42',['TARGETED_DEFORM'],'Full42 Stage6A requalification on the actual propagated asset, existing exact finite-feature contact semantics and all formal checks; report all9 old severe blockers separately. Current3 IDX smoke cannot grant this PASS.'),
 ('HUMAN_CONTOUR',['S4_LOCAL','REST_ZERO_BIND','TARGETED_DEFORM','FULL42'],'Human contour review of resulting Stage4/Stage5/bind/poses, whole hand arch and boundary under plain solid matched cameras; human acceptance never silently upgrades crossing or Stage6B qualification.')]
plan={'phase':PHASE,'status':'PLAN_ONLY_NOT_EXECUTED','trigger':'Future LOCAL_DONOR_SHAPE_TRANSFER_AMENDMENT_APPLICATION_R1 after explicit Human approval of exact candidate','candidate':P['FORMAL_CANDIDATE'],'geometry_footprint':footprint,'frozen_authorities':[ref(p) for p in [cap_path,r3_path,weight_path,true_dir/'CORRECTED_TRUE_CAP_SOURCE_TARGET_AUTHORITY.json',true_dir/'RECOMPUTE_REQUIRED_BOUND_CASE_COVERAGE_R1.json',ROOT/'production_spec/stage5_production_rig/human_thumb_kinematic_authority_correction_r1/THUMB_DISTAL_IP_TIP_KINEMATIC_CORRECTION_AUTHORITY_R1.json',PRIOR/'HISTORICAL_RSSF_COORDINATE_CORRESPONDENCE.json',ROOT/'production_spec/stage4_blender/stage4b_r2/STAGE4B_R2_JOINT_FRAME.json'] if p.exists()],'steps':[{'id':a,'requires':b,'required_work':c,'executed':False} for a,b,c in steps],'NO_RESEARCH_REOPEN':['cap37 anatomy','fresh R3 ownership research','FIRST_WEB anatomy','CMC topology research','thumb kinematic anatomy','317 weight authority research','retopo research','bone/joint authority'],'research_exception':'Only future actual revalidation with new direct evidence may justify a separately scoped authority review. Geometry change alone grants no research reopening.','production_promotion_authorized':False,'Stage6B_PASS_authorized':False}
dump('FORMAL_DONOR_TRANSFER_DOWNSTREAM_PLAN_R1.json',plan)
approval={'status':'NOT_HUMAN_APPROVED','phase':PHASE,'candidate':P['FORMAL_CANDIDATE'],'source_stage4c':P['SOURCE_STAGE4C'],'official_L1_donor':P['DONOR_SOURCE'],'donor_object':P['donor_object'],'donor_layer':P['donor_layer'],'write_set_count':54,'vertex_ids':sorted(I),'vertex_id_set_sha256':digest(sorted(I)),'exact54_stored_local_coordinates_sha256':digest([[i,C['candidate_local_m'][i]] for i in sorted(I)]),'write_set_evidence':ref(OUT/'FORMAL_DONOR_TRANSFER_WRITE_SET_R1.json'),'coordinate_evidence':ref(OUT/'FORMAL_DONOR_TRANSFER_COORDINATES_R1.json'),'approval_scope':['donor source identity','exact54 vertex write set','exact54 formal target coordinates','frozen Stage4C_R2 to independent derived candidate lineage','current topology preservation','visible contour result','downstream revalidation blast radius'],'scope_exclusions':['production application/promotion','historical overwrite','Stage6A PASS','Stage6B PASS','9 independent severe crossing adjudication'],'downstream_plan':ref(OUT/'FORMAL_DONOR_TRANSFER_DOWNSTREAM_PLAN_R1.json'),'NEXT':'HUMAN_APPROVE_LOCAL_DONOR_SHAPE_TRANSFER_AMENDMENT_R1','STOP':'HUMAN REVIEW'}
dump('HUMAN_AMENDMENT_APPROVAL_SCOPE_R1.json',approval)
old=read(FULL/'FULL_STAGE6A_REQUALIFICATION_R1_STATUS.json');assert old['MACHINE_HARD_BLOCKER_COUNT']==9 and old['FULL_STAGE6A_REQUALIFICATION_R1']=='FAIL_CLOSED_FULL_STAGE6A_REQUALIFICATION'
status={'phase':PHASE,'DONOR_SOURCE':'Blender Human Base Meshes v1.4.1 / Hand  - Realistic / official Multires L1 equivalent to Stage2 evaluated L1','DONOR_SOURCE_HASH':P['DONOR_SOURCE']['sha256'],'DONOR_SOURCE_VERIFIED':'PASS','SOURCE_STAGE4C_HASH':P['SOURCE_STAGE4C']['sha256'],'FORMAL_CANDIDATE_HASH':P['FORMAL_CANDIDATE']['sha256'],'WRITE_SET_COUNT':54,'RECOMPUTED_WRITE_SET_COUNT':54,'PROBE_WRITE_SET_COUNT':54,'WRITE_SET_REPRODUCED':'54/54','WRITE_SET_IDENTITY_MATCH_VS_PROBE':True,'MAX_COORD_DELTA_VS_PROBE_MM':0.0,'TOTAL_VERTEX_POSITION_CHANGED':54,'OUTSIDE_WRITE_SET_POSITION_DRIFT':0,**{k:C[k] for k in ['TOPOLOGY_DRIFT','UV_DRIFT','MATERIAL_DRIFT','WEIGHT_DRIFT','BONE_JOINT_DRIFT']},'STRUCTURAL_GATE':'PASS','TOPOLOGY_PRESERVED':'PASS','UV_MATERIAL_PRESERVED':'PASS','WEIGHT_RIG_PAYLOAD_PRESERVED':'PASS','TRUE_CONTACT_NO_REGRESSION':'PASS','NEW_TRUE3D_CONTACT_COUNT':0,'NEW_SELF_INTERSECTION_COUNT':0,'NEW_NONADJACENT_EXACT_INTERSECTION_COUNT':0,'NEW_OFF_SHARED_CROSSING_COUNT':0,'NEW_ILLEGAL_COPLANAR_OVERLAP_COUNT':0,'NEW_STRUCTURAL_BOWTIE_COUNT':0,'FACE_REVERSAL_COUNT':0,'DEGENERATE_COUNT':0,'BASELINE_CONTACT_WORSENING_COUNT':0,'BASELINE_CONTACT_FEATURE_EXPANSION_COUNT':0,'NEW_OBTUSE_SHARP_TRANSITION_MIGRATION_COUNT':0,'LOCAL_BASELINE_CONTACT_COMPONENTS':12,'LOCAL_CANDIDATE_CONTACT_COMPONENTS':0,'NATIVE_V_E_F':S['native_V_E_F'],**{'EDGE'+e+'_DIHEDRAL':B['named_edges'][e] for e in ['6675','6602','6676']},'DONOR_FIDELITY_MAX_MM':C['DONOR_FIDELITY']['max_mm'],'DONOR_FIDELITY_MEAN_MM':C['DONOR_FIDELITY']['mean_mm'],'DONOR_FIDELITY_RMS_MM':C['DONOR_FIDELITY']['RMS_mm'],'DONOR_FIDELITY_P95_MM':C['DONOR_FIDELITY']['p95_mm'],'DONOR_FIDELITY_SEMANTICS':C['DONOR_FIDELITY']['semantics'],'VISIBLE_DENT_STATUS':visual['VISIBLE_DENT_STATUS'],'NEW_VISIBLE_DEFECT':visual['NEW_VISIBLE_DEFECT'],'BIND_PREVIEW':'PASS','RAW_TO_BIND_ROI_MAX_DELTA_MM':bind['RAW_TO_BIND_ROI_MAX_DELTA_MM'],'DENT_REAPPEARED_IN_BIND':'NO','NEW_BIND_VISIBLE_DEFECT':bind['NEW_BIND_VISIBLE_DEFECT'],'IDX15_SMOKE':'PASS_LOCAL_TEMPORARY','IDX30_SMOKE':'PASS_LOCAL_TEMPORARY','IDX45_SMOKE':'PASS_LOCAL_TEMPORARY','FULL_STAGE6A_STATUS_RETAINED':old['FULL_STAGE6A_REQUALIFICATION_R1'],'FULL_STAGE6A_MACHINE_HARD_BLOCKER_COUNT_RETAINED':9,'OLD_SEVERE_CROSSINGS_ADJUDICATED':False,'OLD_FULL42_STATUS_FILE':ref(FULL/'FULL_STAGE6A_REQUALIFICATION_R1_STATUS.json'),'PRODUCTION_DRIFT':'PENDING_FINAL_HASH_VERIFICATION','AMENDMENT_DESIGN_VERDICT':'PENDING_FINAL_HASH_VERIFICATION','NEXT':approval['NEXT'],'STOP':'HUMAN REVIEW','DESIGN_ONLY':True,'NOT_PRODUCTION':True,'NOT_HUMAN_APPROVED':True,'DO_NOT_PROMOTE':True,'GEOMETRY_APPLICATION_PERFORMED':False,'FULL42_RERUN':False,'R3_RERUN':False,'RENDER_COUNT':96}
dump(PHASE+'_STATUS.json',status)
def grid(ls,v,shade):
 return '<div class="grid" style="--cols:'+str(len(ls))+'">'+''.join(f'<figure><figcaption>{escape(titles[labels.index(l)] if l in labels else l)}<small>{escape(l)}</small></figcaption><a href="renders/{l}_{v}_{shade}.png"><img src="renders/{l}_{v}_{shade}.png" alt="{l} {v} {shade}" loading="{("eager" if v=="CLOSE" and ls==labels else "lazy")}"></a></figure>' for l in ls)+'</div>'
html=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>54点 donor transfer — Human amendment review</title><style>body{margin:0;background:#f4f5f6;color:#202b34;font:15px/1.5 system-ui,"Microsoft YaHei",sans-serif}header{padding:12px 20px;background:#fff}h1{margin:0;font-size:20px}p{margin:6px 0}main{padding:12px 18px}h2{font-size:19px;margin:24px 0 8px}.grid{display:grid;grid-template-columns:repeat(var(--cols),minmax(0,1fr));gap:8px}figure{margin:0;background:white}figcaption{padding:8px;font-weight:600;font-size:14px}small{display:block;font-size:10px;font-weight:400;overflow-wrap:anywhere}img{display:block;width:100%;height:auto}a{color:#285d86}details{background:#fff;padding:12px;margin:8px 0}table{border-collapse:collapse;background:#fff;width:100%;font-size:13px}td,th{padding:7px;text-align:left;border:1px solid #dce1e6}code{overflow-wrap:anywhere}pre{white-space:pre-wrap;overflow-wrap:anywhere}button{padding:6px 12px;border:1px solid #bbc6cd;background:#fff;cursor:pointer}nav{display:flex;gap:8px;margin:8px 0}.muted{color:#596a76}.note{padding:12px;background:#fff4dd}svg{width:100%;height:auto}</style><header><h1>54点 donor transfer · 正式 amendment candidate</h1><p>DESIGN_ONLY · NOT_PRODUCTION · NOT_HUMAN_APPROVED · DO_NOT_PROMOTE</p><p>独立重算54/54；与探针差0mm；机器 gate / bind / IDX smoke通过。STOP — HUMAN REVIEW。</p></header><main><p class="muted">第一屏：普通实体、同机位、同光照、同尺度。点击任意图可查看原始640px图。</p>',grid(labels,'CLOSE','FLAT')]
html.append('<nav><a href="#views">全部视图</a><a href="#sections">原生剖面与 overlay</a><a href="#bind">Bind / IDX</a><a href="#approval">审批范围与证据</a></nav><p>左侧当前几何保留尖锐折槽；右侧正式候选恢复 donor 浅谷。请以普通实体判断 notch、鼓包、边界 ridge 与整手 dorsal arch；视觉结论仍待 Human 确认。</p><div class="note">旧 Full42 Stage6A：FAIL_CLOSED_FULL_STAGE6A_REQUALIFICATION；9对 unapproved severe crossing继续独立保留。本轮临时3档 IDX smoke不改变此状态。</div><h2 id="views">匹配视图</h2>')
view_names={'HUMAN':'最初发现 dent 的原始 Human 机位 · 640×800','CLOSE':'Close solid','FULL_DORSAL':'Full dorsal hand','GRAZING':'Grazing','SIDE':'Side','SILHOUETTE':'Silhouette / 外轮廓','WIRE':'Native wire'}
for v in ['HUMAN','CLOSE','FULL_DORSAL','GRAZING','SIDE','SILHOUETTE','WIRE']:
 html.append(f'<h2>{view_names[v]}</h2>'+grid(labels,v,'FLAT')+f'<details><summary>实际 source native smooth flags：{v}</summary>'+grid(labels,v,'SOURCE_NATIVE')+'</details>')
html.append('<h2 id="sections">0° / 60° / 120° native sections</h2><p>每个面按实际 native fan 与同一物理平面求交，四列坐标尺度一致；单位mm。Overlay左图为官方 donor 原始形状的冻结刚性展示配准；工程 RSSF 手姿不同，不能据其全局差异判定 lineage fidelity。右图比较当前拓扑上的54点 ancestry + frozen RSSF target 与正式保存结果。ROI54点精确对应误差另见机器数值。</p>')
for a in [0,60,120]:html.append(f'<h2>{a}° 原生剖面</h2><img src="sections/FOUR_NATIVE_SECTIONS_{a}.svg" alt="{a} degree four native sections"><img src="sections/DONOR_FORMAL_OVERLAY_{a}.svg" alt="{a} degree donor formal overlays">')
html.append('<h2 id="bind">Temporary current rig / current weight bind 与有限 IDX smoke</h2><p>RAW_TO_BIND_ROI_MAX_DELTA_MM = '+format(bind['RAW_TO_BIND_ROI_MAX_DELTA_MM'],'.12g')+'。仅当前 rig/weights 评估副本，未正式传播Stage5。原始正式候选 / bind / IDX15 / IDX30 / IDX45：</p>')
for v in ['CLOSE','GRAZING','SIDE','FULL_DORSAL','WIRE']:html.append('<h2>'+v+'</h2>'+grid(smokes,v,'FLAT')+'<details><summary>Source native flags</summary>'+grid(smokes,v,'SOURCE_NATIVE')+'</details>')
html.append('<h2>边界二面角诊断</h2><p>角度用于诊断，不是人体阈值。完整write-boundary与外固定环记录均已保留，所有高delta边可逐条检查。</p><table><tr><th>Edge</th><th>Source°</th><th>Formal°</th><th>Delta°</th></tr>')
for e in ['6675','6602','6676']:
 r=B['named_edges'][e];html.append(f'<tr><td>{e}</td><td>{r["source_dihedral_deg"]:.9f}</td><td>{r["candidate_dihedral_deg"]:.9f}</td><td>{r["delta_deg"]:.9f}</td></tr>')
html.append('</table><details><summary>所有高delta boundary edges</summary><table><tr><th>Edge</th><th>Vertices</th><th>Source°</th><th>Formal°</th><th>Delta°</th></tr>')
for r in B['high_delta_boundary_edges']:html.append(f'<tr><td>{r["edge_id"]}</td><td>{r["vertex_ids"]}</td><td>{r["baseline_dihedral_deg"]:.6f}</td><td>{r["candidate_dihedral_deg"]:.6f}</td><td>{r["delta_deg"]:.6f}</td></tr>')
html.append('</table></details><h2 id="approval">Human approval scope</h2><p>审批此唯一候选的 donor身份、54点集合和正式target、Stage4C派生lineage、拓扑保持、视觉轮廓及下游验证影响范围。批准不包含production promotion、Stage6A PASS或Stage6B PASS。</p><p>候选 SHA256：<code>'+P['FORMAL_CANDIDATE']['sha256']+'</code></p><p>Write IDs：<code>'+', '.join(map(str,sorted(I)))+'</code></p><p>下一步：HUMAN_APPROVE_LOCAL_DONOR_SHAPE_TRANSFER_AMENDMENT_R1。Human批准后下一轮才可执行APPLICATION。</p><h2>后续重验证计划 · 本轮未执行</h2><ol>')
for a,b,c in steps:html.append(f'<li><b>{a}</b> · {escape(c)}</li>')
html.append('</ol><p>NO_RESEARCH_REOPEN：cap37、fresh R3 ownership、FIRST_WEB、CMC、thumb anatomy、317 weights、retopo、bone/joint authority；只有实际后续验证出现新的直接证据才重新定范围。</p><h2>完整证据</h2><ul>')
for name in [PHASE+'_REPORT.md',PHASE+'_STATUS.json','HUMAN_AMENDMENT_APPROVAL_SCOPE_R1.json','FORMAL_DONOR_TRANSFER_WRITE_SET_R1.json','FORMAL_DONOR_TRANSFER_COORDINATES_R1.json','FORMAL_DONOR_TRANSFER_PROVENANCE_R1.json','FORMAL_PAYLOAD_PRESERVATION_R1.json','FORMAL_DONOR_TRANSFER_STRUCTURE_AUDIT_R1.json','FORMAL_DONOR_TRANSFER_CONTACT_AUDIT_R1.json','FORMAL_DONOR_TRANSFER_BOUNDARY_AUDIT_R1.json','FORMAL_DONOR_TRANSFER_BIND_PREVIEW_R1.json','FORMAL_DONOR_TRANSFER_LIMITED_IDX_SMOKE_R1.json','INCIDENTAL_STAGE6A_CROSSING_DELTA.json','FORMAL_DONOR_TRANSFER_DOWNSTREAM_PLAN_R1.json','PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json','FORMAL_NATIVE_SECTION_COMPARISON_R1.json','FORMAL_MATCHED_RENDER_MANIFEST_R1.json',CANDIDATE.name]:html.append(f'<li><a href="{name}">{name}</a></li>')
html.append('</ul><p>STOP — HUMAN REVIEW · 当前没有正式APPLY。</p></main></html>');(OUT/'review.html').write_text(''.join(html),encoding='utf-8')
report=f'''# {PHASE}

结论：待最终只读hash验证后，READY_FOR_HUMAN_AMENDMENT_APPROVAL。STOP — HUMAN REVIEW。

只在本轮独立目录生成正式design候选；未APPLY、未改历史Stage4、未正式传播Stage5、未重算R3/true-cap/ownership/static qualification/targeted deformation/Full42。三档IDX仅按用户允许的临时smoke执行。

## 独立复现与唯一lineage

从实际官方master重新评估stored Multires L1，实际Stage4C与Stage4A rest重新读取；54点按官方L1 parent edge ancestry、历史split权重及frozen RSSF J独立计算。

`target[i] = frozen_Stage4C[i] + frozen_RSSF_J[i] @ (sum(parent_weight * actual_official_L1[parent]) - historical_Stage4A_rest[i])`

64次历史split的唯一真实parent edge与fraction逐个独立验证；沿冻结ancestry闭包重新恢复54点，不复制探针最终坐标，不执行历史surface优化。保存并重新打开正式blend验证。

RECOMPUTED_WRITE_SET_COUNT=54；PROBE_WRITE_SET_COUNT=54；WRITE_SET_IDENTITY_MATCH=True；MAX_COORD_DELTA_VS_PROBE_MM=0。54/54均有donor ancestry、frozen transform、target及restoration reason。scope_expansion=0；optimization/fairing/manual_tuning=0。

Write IDs：{', '.join(map(str,sorted(I)))}。

## 来源与资产hash

DONOR_SOURCE：{status['DONOR_SOURCE']}。

DONOR_SOURCE_HASH：`{status['DONOR_SOURCE_HASH']}`

SOURCE_STAGE4C_HASH：`{status['SOURCE_STAGE4C_HASH']}`

FORMAL_CANDIDATE_HASH：`{status['FORMAL_CANDIDATE_HASH']}`

Asset：[{CANDIDATE.name}]({CANDIDATE.name})。对象custom props明确AMENDMENT_DESIGN_ONLY、NOT_PRODUCTION、NOT_HUMAN_APPROVED、DO_NOT_PROMOTE。只有这些新增design标签与54点position属于预期变更；既有全部protected payload精确保持。

## Payload与结构

V/E/F={S['native_V_E_F']}；vertex/edge/face IDs、native cycles、manifold incidence、UV坐标/连接、materials/assignments、smooth/sharp flags、custom normal state、groups/weights、armatures/bones/joints、object matrices全部精确保持。

Stage4C几何asset本来无vertex groups/armature/custom normals；temporary currentR2 bind副本另外验证实际rig/weights全payload精确保持，未借此宣称Stage4C自带production rig。RSSF、nail、cap37、FIRST_WEB21、freshR3等外部authority以全项目byte hash保护。

TOTAL_VERTEX_POSITION_CHANGED=54。OUTSIDE_WRITE_SET_POSITION_DRIFT=0；TOPOLOGY_DRIFT=0；UV_DRIFT=0；MATERIAL_DRIFT=0；WEIGHT_DRIFT=0；BONE_JOINT_DRIFT=0。

STRUCTURAL_GATE=PASS；TOPOLOGY_PRESERVED=PASS；UV_MATERIAL_PRESERVED=PASS；WEIGHT_RIG_PAYLOAD_PRESERVED=PASS；TRUE_CONTACT_NO_REGRESSION=PASS。

54点incident native fans对whole mesh进行真实finite-feature exact rational交集测试，扣除真实legal shared simplex，并跟踪baseline component membership、feature及extent。所有其它静态pair因坐标不变而精确不变。局部baseline12个真实contact components→candidate0。

NEW_TRUE3D_CONTACT_COUNT=0；NEW_SELF_INTERSECTION_COUNT=0；NEW_NONADJACENT_EXACT_INTERSECTION=0；NEW_OFF_SHARED_CROSSING=0；NEW_ILLEGAL_COPLANAR_OVERLAP=0；NEW_STRUCTURAL_BOWTIE=0；FACE_REVERSAL_COUNT=0；DEGENERATE_COUNT=0；BASELINE_CONTACT_WORSENING_COUNT=0；BASELINE_CONTACT_FEATURE_EXPANSION_COUNT=0；NEW_OBTUSE_SHARP_TRANSITION_MIGRATION_COUNT=0。

保留reconciled semantics：不要求absolute projected bowtie zero；不能把固定chart normal翻转当成intrinsic reversal。native oriented cycles不变，声明的直线morph连续fan最小面积={S['continuous_fan_area']['minimum_fan_triangle_area_mm2']:.12g}mm²，无zero-area event。端点exact contacts和连续area证据不构成全程continuous collision qualification，也不构成production资格。

## Donor fidelity（54点ancestry语义）

max={C['DONOR_FIDELITY']['max_mm']:.15g}mm；mean={C['DONOR_FIDELITY']['mean_mm']:.15g}mm；RMS={C['DONOR_FIDELITY']['RMS_mm']:.15g}mm；p95={C['DONOR_FIDELITY']['p95_mm']:.15g}mm。

这是frozen RSSF之后的unrounded ancestry targets与实际native float32保存值之差，只含存储数值舍入；不采用nearest-surface距离。54点外按设计保留engineered current surface，不声称全手与donor重合。

## Boundary与普通实体

完整boundary及outer fixed-fixed环记录、每边normal dot/position/gradient及全部abs(delta)>10°边见BOUNDARY_AUDIT。保守筛查为newly obtuse interface或angle>45°且increase>20°；仅geometry诊断，不是人体阈值。匹配实体补充检查迁移hinge/ridge/notch/silhouette kink。

|Edge|Source°|Formal°|Delta°|
|---|---:|---:|---:|
'''
for e in ['6675','6602','6676']:
 r=B['named_edges'][e];report+=f'|{e}|{r["source_dihedral_deg"]:.9f}|{r["candidate_dihedral_deg"]:.9f}|{r["delta_deg"]:.9f}|\n'
report+=f'''
96张匹配render：第一屏四列CURRENT_STAGE4C_R2 / OFFICIAL_L1_DONOR / TEMPORARY_FEASIBILITY_PROBE / FORMAL_AMENDMENT_CANDIDATE普通实体；原始Human640×800机位、close、full dorsal、grazing、side、silhouette、native wire。均保留flat及实际native smooth flags；同一中性材质/光照/尺度。0/60/120°实际native sections及donor/formal overlay提供同物理平面与尺度，faceID追溯。官方donor原始姿态只按冻结刚性display配准展示；精确fidelity依据右侧current-topology ancestry target overlay及机器误差。

VISIBLE_DENT_STATUS=ABSENT_PENDING_HUMAN_CONFIRMATION。NEW_VISIBLE_DEFECT=NONE_OBSERVED_PENDING_HUMAN_CONFIRMATION。Agent实际检查close/grazing/side/full dorsal/silhouette/native wire：尖锐notch消失，自然浅谷恢复，未观察到新增鼓包、ridge、折点或全手dorsal arch缺陷。仍须Human确认。

## Temporary bind与有限pose smoke

仅staticPASS后建立实际currentR2 rig/weights独立副本，54点raw位置写入此临时副本；bindPASS后执行IDX_MCP_15/30/45。没有正式Stage5 propagation。RAW_TO_BIND_ROI_MAX_DELTA_MM={bind['RAW_TO_BIND_ROI_MAX_DELTA_MM']:.15g}；数值zero核对tolerance0.0001mm。currentbaseline bind和3poses均精确复现旧坐标；每case零姿态恢复精确一致；临时bindblend重新打开核对PASS。

BIND_PREVIEW=PASS；DENT_REAPPEARED_IN_BIND=NO；NEW_BIND_VISIBLE_DEFECT=NONE_OBSERVED_PENDING_HUMAN_CONFIRMATION。IDX15_SMOKE=PASS_LOCAL_TEMPORARY；IDX30_SMOKE=PASS_LOCAL_TEMPORARY；IDX45_SMOKE=PASS_LOCAL_TEMPORARY。每个同pose相对currentbaseline执行局部contact/feature-no-regression及边界筛查，新contact/新边界transition=0。匹配实体未见由本次transfer造成局部折回或新缺陷，Human pending。

## 独立旧blocker

FULL_STAGE6A_STATUS_RETAINED=FAIL_CLOSED_FULL_STAGE6A_REQUALIFICATION。原9对unapproved severe exact crossings继续独立保留，不优化、不裁决、不PASS/FAIL重新分类、不human接受。INCIDENTAL_STAGE6A_CROSSING_DELTA仅记录已运行IDXcase旧witness顶点坐标变化；TH_IP_15未运行。旧Full42status文件hash保持。

## 下游影响与计划

直接几何footprint：54点；{len(incident_faces)}个incident native faces；{len(incident_edges)}个incident edges；详细IDs/one-ring/boundary及authority集合交集见DOWNSTREAM_PLAN。cap37点交集={footprint['cap37_write_overlap']}；FIRST_WEB21交集={footprint['FIRST_WEB21_write_overlap']}；freshR3 frozen domain交集={footprint['fresh_R3_frozen_domain_write_overlap']}；317weight universe交集={footprint['approved_317_weight_universe_write_overlap']}。冻结cap源/target endpoint交集分别={footprint['true_cap_frozen_source_endpoint_write_overlap']} / {footprint['true_cap_frozen_target_endpoint_write_overlap']}；703条历史primary path中{len(historical_touched)}条经过write点，仅查看已有记录，无新path/bound重算。即使原path没有经过write点，改变edge metric仍可能改变新最短路，正式APPLY后必须geometry-dependent重验证。

计划执行次序：Stage4 local validation → Stage5独立geometry propagation → joint-to-surface → rest/zero/bind → static skin compatibility → geometry-dependent frozen true-cap paths/bounds → targeted deformation → Full42 Stage6A → Human contour review。每步依赖与成功证据要求、冻结authority哈希、703/1406endpoint覆盖及required-bound-case manifest已记录。所有步骤PLAN_ONLY_NOT_EXECUTED。

NO_RESEARCH_REOPEN：cap37 anatomy、freshR3 ownership、FIRST_WEB anatomy、CMC topology、thumb kinematics、317 weight authority、retopo、bone/joint authority；只有后续实际revalidation出现新直接证据时，另定范围。

## Human审批

Human只批准：唯一donor identity、54个IDs、54点正式target coords、frozenStage4C→独立candidate lineage、currenttopology preservation、visible contour result及下游重验证影响范围。HUMAN_AMENDMENT_APPROVAL_SCOPE_R1.json绑定source/donor/candidate hash、write-set hash与54target local coordinate hash。批准不包含production promotion、Stage6A PASS或Stage6B PASS。

NEXT=HUMAN_APPROVE_LOCAL_DONOR_SHAPE_TRANSFER_AMENDMENT_R1。下一轮Human批准后才可执行LOCAL_DONOR_SHAPE_TRANSFER_AMENDMENT_APPLICATION_R1。

STOP — HUMAN REVIEW。

最终全项目只读hash验证与verdict由verify_delivery.py追加如下。
'''
(OUT/(PHASE+'_REPORT.md')).write_text(report,encoding='utf-8')
print('Review, exact approval scope, downstream plan, report and pending final hash status generated')
