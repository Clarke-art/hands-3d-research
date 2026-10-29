import sys
sys.dont_write_bytecode = True
from common import *
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from PIL import Image
import html, re

roi = read(OUT/'DORSAL_MCP_DENT_ROI_R1.json')
raw = read(OUT/'LINEAGE_RAW_READONLY_EXTRACTION.json')
metrics = read(OUT/'DENT_LOCAL_GEOMETRY_METRICS_R1.json')['stages']
sections = read(OUT/'DENT_CROSS_SECTIONS_R1.json')['stages']
arm = read(OUT/'DENT_ARMATURE_ZERO_POSE_AUDIT_R1.json')
pose = read(OUT/'DENT_POSE_AMPLIFICATION_R1.json')
earlier = read(OUT/'EARLIER_STAGE4A_BASE_LOCAL_IDENTITY_R1.json')
inputs = read(OUT/'LINEAGE_INPUT_STATE_VERIFICATION_R1.json')
render = read(OUT/'DENT_RENDER_MANIFEST_R1.json')
faces = raw['topology']['faces']; edges = raw['topology']['edges']
V = np.array(raw['stages']['R2_PRODUCTION']['raw_world_m']) * 1000
core = set(roi['core_vertices']); ring1 = set(roi['1_ring']); ring2 = set(roi['2_ring']); allroi = set(roi['vertices'])
cap = read(CAP_PATH); r3 = read(R3_PATH)
weightset = read(S5/'targeted_rig_and_skin_data_rebuild_r2/AUTHORIZED_WEIGHT_WRITE_SET_R2.json')
cmc = read(ROOT/'production_spec/stage4_blender/stage4a_r2/CMC_LOCAL_RETOPO_AUDIT_R2.json')
nail = {v for fi,p in enumerate(faces) if raw['stages']['R2_PRODUCTION']['face_material_indices'][fi] == 1 for v in p}
cmc_dist = np.linalg.norm(V-np.array(cmc['cmc']['world'])*1000,axis=1)
protected = {'thumb_nail_native_material_1':nail,'cap37':set(cap['vertex_ids']), 'old_cap9':set(cap['old_cap9_ids']), 'FIRST_WEB21':set(r3['FIRST_WEB21']['membership_vertex_ids']), 'fresh_R3_bounded_domain':set(r3['graph']['vertex_ids']), 'historical_317_weight_universe':set(weightset['approved_write_universe_317']), 'CMC_20mm_context_not_new_authority':set(np.where(cmc_dist <= cmc['surgery']['R_mm'])[0].tolist())}
seed_incident = [fi for fi,p in enumerate(faces) if core.intersection(p)]
blend_incident = [fi for fi,p in enumerate(faces) if (core|ring1).intersection(p)]
intersections = {name:{'core':sorted(core&s),'core_plus_1_ring':sorted((core|ring1)&s),'diagnostic_52':sorted(allroi&s)} for name,s in protected.items()}
topo_checks = []
for ei in roi['edges']:
    a,b=edges[ei]; inc=[]
    for fi,p in enumerate(faces):
        for j in range(len(p)):
            pair=(p[j],p[(j+1)%len(p)])
            if pair==(a,b):inc.append((fi,1))
            if pair==(b,a):inc.append((fi,-1))
    topo_checks.append({'edge_id':ei,'native_face_incidence':len(inc),'consistent_winding':len(inc)==2 and inc[0][1]+inc[1][1]==0})
protection = {'status':'READ_ONLY_FUTURE_DESIGN_ADVICE_NO_WRITE_AUTHORIZATION', 'diagnostic_ROI_vertex_count':len(allroi), 'candidate_seed_vertices':sorted(core), 'candidate_visible_core_faces':roi['core_faces'], 'all_native_faces_incident_to_seed':seed_incident, 'possible_blend_support_1_ring':sorted(ring1), 'all_native_faces_incident_to_seed_plus_blend':blend_incident, 'fixed_reference_boundary_2_ring':sorted(ring2), 'scope_intersections':intersections, 'ROI_min_CMC_center_distance_mm':float(min(cmc_dist[list(allroi)])), 'local_topology_checks':topo_checks, 'TOPOLOGY_CHANGE_REQUIRED':'NO_REQUIREMENT_IDENTIFIED_FOR_INITIAL_EXISTING_VERTEX_POSITION_ROUTE', 'RET0PO_REQUIRED':'NO', 'minimality_limit':'15 vertices / 7 ray-hit faces are a diagnosis seed, not a proven irreducible amendment set. Every incident face must be checked. Optional ring1 blending needs separate explicit scope review; ring2 is fixed reference only.', 'MINIMAL_REPAIR_LAYER':'LOCAL_EXISTING_VERTEX_POSITIONS_IN_STAGE4_GEOMETRY', 'bones_joints':'No change indicated by this diagnosis. Verify geometry/rest alignment rather than automatically refit joints.', 'skin_weights':'May inherit exact current vectors initially; must revalidate static and deformed behavior after any geometry amendment. No weight write authority is reopened.', 'protected_memberships':'No intersection within current diagnostic52 for nail/cap37/old_cap9/FIRST_WEB21/CMC context/fresh R3 domain. Numeric geometry-derived validity still needs revalidation.', 'downstream_blast_radius':['Create a separately authorized, versioned Stage4 local surface amendment; preserve topology, UV, material slots, vertex IDs, 21 bones and authority memberships. Recheck manifold/winding/local contours and frozen CMC/nail boundaries.', 'Recheck RSSF and exact geometry transfer into corrected Stage5A/R2; verify joint-to-surface alignment, zero/bind transforms, reset and inherited weights. No automatic bone fitting or R3 solver rerun.', 'Recompute all affected geometry-derived numeric results, including true-cap shortest graph distances/bounds on the whole relevant graph; unchanged cap endpoints do not prove unchanged shortest-path lengths. Preserve original authority receipts; record new validation/version references.', 'After an approved repair, requalify Stage5 static/targeted deformation and full42-case Stage6A plus Human product review under a separate authorization. This diagnosis runs none of those stages.', 'The prior9 severe exact crossings remain independent FAIL_CLOSED evidence. A dent amendment does not close them. Stage6B/promotion stay blocked until all required qualification and Human closure.']}
dump('DENT_FUTURE_MINIMAL_AMENDMENT_BLAST_RADIUS_R1.json',protection)

# Actual native-face triangle/plane intersections, fixed axes across every stage.
ext=np.array([q for ss in sections.values() for sec in ss for seg in sec['actual_triangle_plane_segments'] for q in seg['profile_mm']])
limits=((float(ext[:,0].min())-.5,float(ext[:,0].max())+.5),(float(ext[:,1].min())-.5,float(ext[:,1].max())+.5))
for label,ss in sections.items():
    fig,axs=plt.subplots(1,3,figsize=(12,3.6),layout='constrained')
    for ax,sec in zip(axs,ss):
        ax.add_collection(LineCollection([seg['profile_mm'] for seg in sec['actual_triangle_plane_segments']],colors='#195c95',linewidths=1.8))
        ax.axvline(0,color='#bb3829',alpha=.5,lw=.7);ax.axhline(0,color='#888888',lw=.5)
        ax.set(xlim=limits[0],ylim=limits[1],title=f"{sec['angle_degrees_in_local_tangent']} deg / {len(sec['actual_triangle_plane_segments'])} segments",xlabel='In-plane distance (mm)',ylabel='Normal height (mm)')
        ax.set_aspect('equal',adjustable='box'); ax.grid(alpha=.15)
    fig.suptitle(label+' | actual mesh sections; same axes; no anatomy threshold',fontsize=10)
    fig.savefig(OUT/'renders'/f'{label}_CROSS_SECTIONS.png',dpi=140);plt.close(fig)
fig,axs=plt.subplots(1,3,figsize=(12,4),layout='constrained')
colors={'STAGE4A_R2_FROZEN':'#ce542b','STAGE4C_R2_RAW':'#266aa1','R2_BIND_ZERO':'#328455','IDX_MCP_15':'#9c3aab'}
for ax,j in zip(axs,range(3)):
    for label,color in colors.items():
        ax.add_collection(LineCollection([seg['profile_mm'] for seg in sections[label][j]['actual_triangle_plane_segments']],colors=color,linewidths=1.2,label=label,alpha=.85))
    ax.set(xlim=limits[0],ylim=limits[1],xlabel='In-plane distance (mm)',ylabel='Normal height (mm)',title=f'{[0,60,120][j]} deg')
    ax.set_aspect('equal',adjustable='box');ax.grid(alpha=.15)
axs[0].legend(fontsize=6,loc='lower left')
fig.suptitle('Measured surface sections after rigid registration only; near-overlap is expected',fontsize=10)
fig.savefig(OUT/'renders'/'LINEAGE_CROSS_SECTION_OVERLAY.png',dpi=150);plt.close(fig)

pose.update({'classification':'STATIC_BASELINE_DEFECT','POSE_AMPLIFICATION':'NO_SUPPORTED_IDX_MCP15_30_45_AMPLIFICATION', 'interpretation':'All15 core vertices remain exactly equal to evaluated BIND in all three saved poses. Core area and largest crease dihedral also stay equal. Tiny increasing fitted depth proxy follows support-ring motion/refitting, not actual core deepening.', 'limits':'Only requested saved INDEX MCP15/30/45 cases analyzed; no statement about other possible drivers or untested poses.'})
dump('DENT_POSE_AMPLIFICATION_R1.json',pose)
lineage={'status':'PASS_MATCHED_LOCAL_GEOMETRY_LINEAGE_DIAGNOSIS', 'EARLIEST_CONFIRMED_DENT_STAGE':'STAGE4A_R2_BASE_PRE_CMC_RETOPO', 'earliest_scope':'Earliest among minimally inspected official candidates; the original creation event / earlier Stage2 is not established.', 'earlier_local_identity':earlier, 'input_state_checks':inputs, 'current_native_topology':{'vertex_count':3416,'edge_count':len(edges),'face_count':len(faces)}, 'ROI':{'vertices':roi['vertices'],'faces':roi['faces']}, 'Stage4C_raw_interpretation':'Stored Stage4C_R2 raw coordinates are already RSSF. RSSF comparator is official Stage4B_RSSF_R2, not an invented alternate Stage4C pose.', 'stage_metrics':metrics, 'visibility':{label:True for label in metrics}, 'Stage4C_to_R2_raw_max_mm':arm['raw_Stage4C_to_R2_raw_max_mm'], 'render_registration':'Outer-ring21 proper rigid rotation+translation, no scale. Pre-RSSF Stage4A has its actual original local shape retained. After registration residual RMS is reported per stage; this is display matching, not geometry repair.', 'BASE_render_evidence':'No fabricated whole-BASE rendering: its exact52-vertex/36-face local identity is proved, and STAGE4A_R2_FROZEN local evidence represents that same measured patch.'}
dump('DENT_STAGE_LINEAGE_COMPARISON_R1.json',lineage)
sharp=max(metrics['R2_BIND_ZERO']['dihedral'],key=lambda d:d['unsigned_angle_deg'])
shading={'status':'TRUE_GEOMETRY_DEFECT_CONFIRMED','ROOT_CAUSE_CLASS':'BASE_GEOMETRY_CONTOUR_DEFECT','SHADING_CAUSAL':'VISUAL_EMPHASIS_ONLY_NOT_ROOT_CAUSE', 'actual_production_ROI_smooth_faces':sum(raw['stages']['R2_PRODUCTION']['source_face_use_smooth'][fi] for fi in roi['faces']), 'actual_production_custom_normals':raw['stages']['R2_PRODUCTION']['has_custom_normals'], 'display_modes':['CURRENT','FLAT','WIRE','NORMALS','GRAZING','SILHOUETTE','ANGLE_2','ANGLE_3','SMOOTH_RESET_COUNTERFACTUAL'], 'evidence':'Visible folded surface in current/flat, native wire and three actual mesh sections. Largest crease has opposite directed edge traversal in its two incident faces; it is a geometry fold, not a simple normal/winding inversion.', 'sharpest_native_edge':sharp, 'prior_review_shading':'Existing Stage6A renderer explicitly smoothed its display clone. That can emphasize the crater appearance; native R2 ROI polygons are all flat. Historical render source is unchanged.', 'material_interpretation':'R2 production material/UV/current flags held fixed for cross-stage geometry comparison. Not a reconstruction of each historical stage illumination or material appearance.', 'counterfactual_scope':'Smooth normal reset uses diagnostic display copies only; not saved as production or offered as a repair candidate.', 'silhouette_limit':'Multiple views and grazing illumination support the fold; no silhouette-derived anatomical acceptance threshold is created.', 'render_manifest':'DENT_RENDER_MANIFEST_R1.json','cross_sections':'DENT_CROSS_SECTIONS_R1.json','geometry_metrics':'DENT_LOCAL_GEOMETRY_METRICS_R1.json'}
dump('DENT_GEOMETRY_VS_SHADING_R1.json',shading)

status={'phase':PHASE,'status':'READY_FOR_HUMAN_DENT_CAUSAL_REVIEW','issue':'RIGHT_HAND_DORSAL_MCP_CONTOUR_DENT','Human_product_requirement_record':'PRODUCTION_BLOCKER_PENDING_CAUSAL_DIAGNOSIS','product_blocker_still_open':True,'repair_executed':False,'DENT_VISIBLE_IN_STAGE4C_RAW':True,'DENT_VISIBLE_IN_RSSF':True,'DENT_VISIBLE_IN_R2_BIND':True,'DENT_VISIBLE_IN_IDX_MCP_15':True,'EARLIEST_CONFIRMED_DENT_STAGE':lineage['EARLIEST_CONFIRMED_DENT_STAGE'],'RAW_TO_BIND_GEOMETRY_DELTA':{'Stage4C_raw_to_R2_raw_max_mm':0.0,'R2_ROI_raw_to_evaluated_bind_max_mm':arm['ROI_max_raw_off_to_evaluated_bind_mm'],'R2_core_raw_to_evaluated_bind_max_mm':arm['core_max_raw_off_to_evaluated_bind_mm']},'ZERO_POSE_ARMATURE_GEOMETRY_DELTA':arm['ROI_max_raw_off_to_evaluated_bind_mm'],'SHADING_CAUSAL':shading['SHADING_CAUSAL'],'ARMATURE_ZERO_POSE_CAUSAL':'NO_EFFECT_BEYOND_KNOWN_FLOAT_NOISE','SKIN_CAUSAL':'NO_STATIC_ROOT_CAUSE; NO_SUPPORTED_REQUESTED_INDEX_POSE_AMPLIFIER','POSE_AMPLIFICATION':pose['POSE_AMPLIFICATION'],'ROOT_CAUSE_CLASS':'BASE_GEOMETRY_CONTOUR_DEFECT','TOPOLOGY_CHANGE_REQUIRED':'NO_REQUIREMENT_IDENTIFIED_FOR_INITIAL_POSITION_ONLY_DESIGN','RET0PO_REQUIRED':'NO','MINIMAL_REPAIR_LAYER':protection['MINIMAL_REPAIR_LAYER'],'repair_requirement':'MINIMAL_LOCAL_GEOMETRY_AMENDMENT_REQUIRED_PENDING_HUMAN_APPROVAL','PRODUCTION_DRIFT':0,'existing_Stage6A_status':'FAIL_CLOSED_FULL_STAGE6A_REQUALIFICATION','existing_severe_exact_crossings':9,'Stage6A_rerun':False,'Stage6B':False,'production_promotion':False,'NEXT':'MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R1','NEXT_executed':False,'STOP':'HUMAN REVIEW'}
# Write completion status only after historical drift check passes below.

labels=[('STAGE4A_R2_FROZEN','Stage4A_R2 / BASE同一局部几何'),('STAGE4B_RSSF_R2','Stage4B RSSF（Stage4C/RSSF对照）'),('STAGE4C_R2_RAW','Stage4C_R2 raw（已处于RSSF）'),('CORRECTED_STAGE5A_ZERO','Corrected Stage5A zero'),('R2_ARMATURE_OFF','R2 Armature OFF'),('R2_BIND_ZERO','R2 BIND / zero'),('IDX_MCP_15','IDX_MCP15（复用原坐标）')]
def image_tag(path,caption):
    return f'<figure><a href="{path}"><img loading="lazy" src="{path}" alt="{html.escape(caption)}"></a><figcaption>{html.escape(caption)}</figcaption></figure>'
cards=''
for label,title in labels:
    cards+=f'<section><h2>{title}</h2><div class="grid">'+''.join(image_tag(f'renders/{label}_{mode}.png',caption) for mode,caption in [('CURRENT','实体 / 当前production shading'),('FLAT','Flat shading'),('WIRE','真实native edges')])+'</div>'+image_tag(f'renders/{label}_CROSS_SECTIONS.png','三条实际截面 · 0°/60°/120° · 全阶段固定坐标轴')
    cards+='<details><summary>Normals、grazing、轮廓、两角度、smooth诊断副本</summary><div class="grid">'+''.join(image_tag(f'renders/{label}_{mode}.png',mode) for mode in ['NORMALS','GRAZING','SILHOUETTE','ANGLE_2','ANGLE_3','SMOOTH_RESET_COUNTERFACTUAL'])+'</div></details></section>'
table=''.join(f'<tr><td>{label}</td><td>{m["core_quadratic_ring_depth_proxy_mm"]:.6f}</td><td>{m["max_dihedral_deg"]:.3f}</td></tr>' for label,m in metrics.items())
review='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Dorsal MCP dent · causal review R1</title><style>body{font:16px/1.6 system-ui,sans-serif;background:#f5f3ee;color:#292c32;max-width:1280px;margin:32px auto;padding:0 24px}h1{font-size:28px}h2{font-size:20px}section{background:white;padding:20px;margin:20px 0;border-radius:10px}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}figure{margin:10px 0}img{display:block;width:100%;height:auto}figcaption{font-size:13px}summary{cursor:pointer}table{border-collapse:collapse;width:100%;font-size:13px}td,th{border:1px solid #ddd;padding:6px}code{overflow-wrap:anywhere}a{color:#235e83}.note{background:#fff0d7;padding:16px;border-radius:8px}@media(max-width:700px){.grid{grid-template-columns:1fr}}</style><h1>A 区域：真实的基础几何折陷</h1><p><strong>READY_FOR_HUMAN_DENT_CAUSAL_REVIEW · STOP — HUMAN REVIEW</strong></p><p>最早已确认：<code>Stage4A_R2_BASE（CMC重拓扑之前）</code>。其52个局部顶点与36个面和Stage4A_R2完全一致。之后RSSF、Stage4C、corrected Stage5A、R2 BIND及IDX_MCP15均保留这个凹口。此结论不追溯未检查的更早创建事件。</p><p class="note">本轮只诊断，无修复。主因：<code>BASE_GEOMETRY_CONTOUR_DEFECT</code>。平滑着色会强调凹口，但flat / wire / 实际截面已显示真实折陷。IDX15/30/45中15个核心顶点相对BIND完全不动，未支持pose加深。原Stage6A的9对严重exact crossing与FAIL_CLOSED保持原样。</p><p>所有主视图使用相同ROI、23mm画幅、相同相机/光照/生产材质规则。早期网格仅刚性配准，无缩放；图像中的surface没有被修平。Stage4C raw自身已经是RSSF。CURRENT与FLAT接近一致是因为R2原始ROI面本来就是flat。原Stage6A展示副本使用过smooth，其视觉强调效果见折叠区诊断图。</p><section><h2>Human A → 可复现ROI</h2><div class="grid">'''+image_tag('ROI_LOCATION_CLARIFICATION.png','用户确认A的原图位置')+image_tag('renders/ROI_SELECTION_CLOSEUP.png','native拓扑中的15核心顶点 / 1-ring / 2-ring')+'''</div><p>52个诊断顶点、36个完整ROI面；15个核心顶点、7个射线命中面。ROI仅供本轮诊断，不创建anatomy authority。</p></section>'''+cards+'''<section><h2>几何描述与pose趋势</h2><p>深度proxy是对2-ring21拟合二次曲面的核心负残差；不是人体阈值，也不是新Stage6 gate。三截面是native四边形fan三角化后的真实平面交线，保留face ID。</p><table><tr><th>阶段</th><th>二次曲面深度proxy mm</th><th>最大法线夹角 °</th></tr>'''+table+'''</table><p>核心面折边edge6676（3340–3332）约178.228°；两侧面绕序一致。IDX角度下深度proxy的微小变化来自支持环移动与重拟合，核心顶点、核心面积和锐折角本身不变。</p>'''+image_tag('renders/LINEAGE_CROSS_SECTION_OVERLAY.png','刚性对齐后的实际截面重叠')+'''</section><section><h2>最小未来修改层与停止边界</h2><p>仅建议下一轮设计局部现有顶点位置修正。15核心顶点/7命中面是起始诊断seed，须覆盖其所有incident faces；如需1-ring过渡，需单独确定写入范围，2-ring保留参考。没有证据要求retopo、改joint或改authority membership；目前并未证明15点就是最终最小修改集合。</p><p>当前52点与nail/cap37/old_cap9/FIRST_WEB21/CMC20mm context/fresh R3 domain均无交集。可先继承权重，但任何geometry修改都需重新验证RSSF、rig/bind/skin和依赖几何的true-cap数值，再在另行授权后重新资格验证。凹口修复不会自动解决9对crossing。</p><p><code>MINIMAL_LOCAL_GEOMETRY_AMENDMENT_REQUIRED_PENDING_HUMAN_APPROVAL</code><br>唯一NEXT建议：<code>MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R1</code>（未执行）。</p><p><a href="RIGHT_HAND_DORSAL_MCP_CONTOUR_DENT_CAUSAL_DIAGNOSIS_R1_REPORT.md">完整报告</a> · <a href="RIGHT_HAND_DORSAL_MCP_CONTOUR_DENT_CAUSAL_DIAGNOSIS_R1_STATUS.json">状态</a> · <a href="DENT_FUTURE_MINIMAL_AMENDMENT_BLAST_RADIUS_R1.json">范围与downstream</a> · <a href="DORSAL_MCP_DENT_ROI_R1.json">ROI重现</a> · <a href="PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json">历史零漂移</a></p></section></html>'''
(OUT/'review.html').write_text(review,encoding='utf-8')

before=read(OUT/'HISTORICAL_HASHES_BEFORE.json'); after=inventory()
changed=[p for p,h in before.items() if p in after and after[p]!=h]; missing=sorted(set(before)-set(after)); added=sorted(set(after)-set(before))
assert not changed and not missing and not added, (changed,missing,added)
verification={'status':'PASS_ALL_PREEXISTING_WORKSPACE_FILES_HASH_IDENTICAL','before_file_count':len(before),'after_file_count':len(after),'changed':changed,'missing':missing,'added_outside_diagnosis':added,'PRODUCTION_DRIFT':0,'baseline':'HISTORICAL_HASHES_BEFORE.json','scope':'Every preexisting workspace file, excluding only this new diagnosis directory; all frozen assets, Human receipts and prior Stage6A evidence covered.','baseline_inventory_sha256':digest(before),'after_inventory_sha256':digest(after),'candidate':ref(CAND),'corrected_rig':ref(CORRECTED),'cap_authority':ref(CAP_PATH),'fresh_R3_authority':ref(R3_PATH)}
dump('PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json',verification)
status['historical_files_verified_unchanged']=len(before)
dump(PHASE+'_STATUS.json',status)
rows='\n'.join(f'| `{k}` | `{json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v}` |' for k,v in status.items() if k.startswith('DENT_VISIBLE') or k in ['EARLIEST_CONFIRMED_DENT_STAGE','RAW_TO_BIND_GEOMETRY_DELTA','ZERO_POSE_ARMATURE_GEOMETRY_DELTA','SHADING_CAUSAL','ARMATURE_ZERO_POSE_CAUSAL','SKIN_CAUSAL','POSE_AMPLIFICATION','ROOT_CAUSE_CLASS','TOPOLOGY_CHANGE_REQUIRED','RET0PO_REQUIRED','MINIMAL_REPAIR_LAYER','PRODUCTION_DRIFT'])
report=f'''# {PHASE}

状态：**READY_FOR_HUMAN_DENT_CAUSAL_REVIEW**。本轮严格只读诊断，无repair。根因确认：**BASE_GEOMETRY_CONTOUR_DEFECT**。

用户确认的A点通过原IDX_MCP15 FULL_SOLID图像的准确camera/view_frame射线映射到face3328，中心vertex955；不是根据文字猜点。原图、像素坐标、相机和采样参数、native面/边/1-ring/2-ring均在[DORSAL_MCP_DENT_ROI_R1.json](DORSAL_MCP_DENT_ROI_R1.json)。15个核心顶点为`{sorted(core)}`；7个命中面为`{roi['core_faces']}`。1-ring16、2-ring21，共52个诊断顶点、36个完整ROI面。数值均为诊断描述，不建立anatomy或write authority。

Human finding记录仍为`RIGHT_HAND_DORSAL_MCP_CONTOUR_DENT = PRODUCTION_BLOCKER_PENDING_CAUSAL_DIAGNOSIS`。本次已给出因果证据，产品blocker仍开放；没有Human验收或repair批准。

## 最终字段

| 字段 | 结果 |
|---|---|
{rows}

## Lineage与最早确认来源

正式Stage4A_R2_BASE是CMC重拓扑前工程基线，3364顶点；当前网格3416顶点。没有假设其全局topology一致：逐个唯一精确world坐标匹配了52个局部顶点，并验证36个native面有相同的有向顶点cycle。[EARLIER_STAGE4A_BASE_LOCAL_IDENTITY_R1.json](EARLIER_STAGE4A_BASE_LOCAL_IDENTITY_R1.json)完整保存映射、source hash和绕序验证。其局部几何与实际渲染的Stage4A_R2相同，故凹口最早已确认在**STAGE4A_R2_BASE_PRE_CMC_RETOPO**。这不是首次制造缺陷的日期；未进一步审计Stage2或更早历史。

Stage4A_R2、Stage4B_RSSF_R2、Stage4C_R2、corrected Stage5A和R2之间native顶点/边/面一致。Stage4C raw本身已经处于RSSF；RSSF比较用正式Stage4B_RSSF_R2而非创造一个不存在的Stage4C原生姿态。Stage4C raw与corrected Stage5A/R2 raw全网格world坐标精确一致；Stage4B RSSF相对Stage4C最大差约0.00000373mm。前后native原始坐标、evaluated坐标及source flags存于[LINEAGE_RAW_READONLY_EXTRACTION.json](LINEAGE_RAW_READONLY_EXTRACTION.json)。

匹配展示采用2-ring21的proper刚性rotation/translation，scale=1，无反射或局部修正。配准矩阵、支持环RMS、原始与registered坐标全部保留。早期pre-RSSF局部形状仍是实际原形。[DENT_STAGE_LINEAGE_COMPARISON_R1.json](DENT_STAGE_LINEAGE_COMPARISON_R1.json)提供输入状态与每阶段诊断结果。没有用BASE的局部等同性伪称渲染了其整个旧网格。

## Geometry与shading

每个阶段生成CURRENT、FLAT、WIRE、NORMALS、GRAZING、SILHOUETTE、两额外角度及smooth-reset诊断副本，共63张matched渲染，另有ROI定位图。主相机23mm正交画幅，各阶段同机位/尺度/光照和R2生产材质UV规则。[review.html](review.html)同时给出三条实际截面。CURRENT是R2原有材质/UV/normal flags，不是每个历史阶段当时光照的复刻。

**R2 ROI的36个面全部use_smooth=false，且没有custom normals。** CURRENT与FLAT近似相同是原始资产本来就flat。已有Stage6A renderer将展示副本设为smooth，视觉上加重沟谷；本轮smooth counterfactual复现这种强调，但它没有创造凹陷。无Armature的Stage4A原始vertex geometry、wire、flat及actual sections均保留锐折陷，因此不是normal/shading artifact，也不因视觉强调而分类为mixed cause。

R2最大native相邻面法线夹角为{sharp['unsigned_angle_deg']:.6f}°，edge{sharp['edge_id']}、vertices{sharp['vertices']}、faces{sharp['faces']}。两侧面遍历该边方向相反，绕序一致；这是接近反折的实际几何面关系，不能通过解释为简单倒置normal排除。仅对ROI检查的所有边均为2-face incidence且绕序一致，未发现需要重拓扑的局部连接错误。

三截面穿过vertex955、局部切向0°/60°/120°，用native面fan三角化与平面真实相交，保留face IDs和world/profile坐标；无best-fit修平。[DENT_CROSS_SECTIONS_R1.json](DENT_CROSS_SECTIONS_R1.json)可重算。截面图固定坐标轴，不把相互重叠的数据夸大为阶段变化。

2-ring二次曲面拟合的核心负残差proxy：pre-RSSF Stage4A约1.807104mm；Stage4B/RSSF与Stage4C约1.546239mm；R2 BIND约1.546248mm。该proxy只描述邻域几何，不是生理深度、人体标准或新Stage6 gate。plane残差、umbrella curvature proxy、vertex-normal variation及每条dihedral也完整保存于[DENT_LOCAL_GEOMETRY_METRICS_R1.json](DENT_LOCAL_GEOMETRY_METRICS_R1.json)。

## Armature / bind / skin / pose

R2 Armature OFF/raw与ON/evaluated zero的ROI最大差为{arm['ROI_max_raw_off_to_evaluated_bind_mm']:.12g}mm，core最大差为{arm['core_max_raw_off_to_evaluated_bind_mm']:.12g}mm，全网格最大差为{arm['global_max_mm']:.12g}mm。OFF/ON不是bitwise一致，差异落在项目原有0.0001mm zero校验范围内；本轮不建立新阈值。object/armature world matrices一致，parent inverse为单位阵，pose zero已验证。该浮点量级不能解释静态毫米级局部折陷。[DENT_ARMATURE_ZERO_POSE_AUDIT_R1.json](DENT_ARMATURE_ZERO_POSE_AUDIT_R1.json)记录准确结果。

当前core主要由WRIST/RING_MCP及少量MIDDLE/LITTLE驱动；所有15核心点INDEX_MCP权重为0，52点中INDEX_MCP最大权重仅{pose['ROI_INDEX_MCP_weight_max']:.12g}。完整向量、邻边L1变化保存在[DENT_POSE_AMPLIFICATION_R1.json](DENT_POSE_AMPLIFICATION_R1.json)。不能因为weight variation存在就归因skin：折陷在无Armature的历史raw mesh早已存在。

本轮只读复用了旧Full Stage6A BIND、IDX15/30/45的保存坐标，未执行pose cases。15核心点相对evaluated BIND最大位移均**精确0**，核心面积/最大折边角保持不变；诊断52点的最大位移分别约0.002090/0.004126/0.006117mm。depth proxy分别1.547854/1.549611/1.551419mm的微小增加来自支持环移动与重拟合，不能当作核心凹陷加深证据。因此分类**STATIC_BASELINE_DEFECT**；没有支持所要求INDEX poses的amplification。该结论不推广到其他未经本轮分析的driver或pose。

## 最小未来修改层与downstream

输出：**MINIMAL_LOCAL_GEOMETRY_AMENDMENT_REQUIRED_PENDING_HUMAN_APPROVAL**。最小候选层是Stage4局部现有顶点位置。没有证据要求改topology、retopo、bone/joint或frozen membership；可优先设计位置修正。**本轮未实施或证明repair成功，15点也不是已证明不可缩减的最终写入集。**

诊断seed15点/7可见命中面之外，还需验证seed全部{len(seed_incident)}个native incident faces。若需1-ring16点过渡，另行确定其范围；2-ring21仅固定参考。精确列表见[DENT_FUTURE_MINIMAL_AMENDMENT_BLAST_RADIUS_R1.json](DENT_FUTURE_MINIMAL_AMENDMENT_BLAST_RADIUS_R1.json)。不能把52点诊断ROI变成默认写入授权。

当前52点与native thumb nail、cap37、old_cap9、FIRST_WEB21、fresh R3 bounded graph、历史317权重集合及CMC20mm原有保护context都无交集。ROI离CMC center最小约{protection['ROI_min_CMC_center_distance_mm']:.3f}mm。CMC20mm只是核对既有surgery context，不新建anatomical membership。局部位置修改预计可保留这些membership及21-bone hierarchy；仍必须核对边界与几何衍生结果，不能以零交集代替downstream验证。

未来经授权修正后必须：

1. 对新版本Stage4候选复核局部contour、所有incident faces、manifold/winding、UV/material不变量，以及nail/CMC/RSSF保护。
2. 复核到corrected Stage5A和R2的geometry传递、joint-to-surface alignment、rest/zero/bind、reset及静态skin。可先精确继承weights，不自动重拟合bones或重跑R3。历史317 weight scope不会因此重新打开。
3. 重算依赖geometry的数值结果，尤其true-cap图边长度/全图最短路径/bounds；即使cap37 endpoint没有移动，最短路径数值也不能仅凭membership不变直接承袭。保留原始Human receipts，另存新版本验证，不重写authority。
4. 在另行授权的修复阶段完成Stage5 static/targeted deformation、Full42-case Stage6A requalification及Human产品轮廓验收。本轮没有重跑这些流程。
5. 原9对unapproved severe exact crossings继续独立FAIL_CLOSED，不因dent问题诊断或未来修复自动消失。Stage6B与production promotion继续受资格验证和Human闭环约束。

## 只读核验与停止

全工作区本轮前已有{len(before)}个文件逐一SHA256比较：changed=0、missing=0、诊断目录外added=0，**PRODUCTION_DRIFT=0**。包括Stage4C/RSSF、nail/CMC、21 bones/corrected kinematics、cap37/fresh R3/FIRST_WEB21、R2、true-cap corrected numeric authority、所有Human receipts与全部旧Full Stage6A证据。完整基线和[PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json](PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json)可复查。未保存blend、未执行geometry/weight/bone/material/normal/RSSF edits、未Stage6A rerun、未Stage6B或promotion。

唯一NEXT建议：**MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R1**。本轮未执行NEXT。

**STOP — HUMAN REVIEW**
'''
(OUT/(PHASE+'_REPORT.md')).write_text(report,encoding='utf-8')
# Validate all generated PNGs and review references.
pngs=list(OUT.rglob('*.png'))
for p in pngs:
    with Image.open(p) as im: im.verify()
links=re.findall(r'(?:href|src)="([^"]+)"',review)
missinglinks=[p for p in links if not (OUT/p).is_file()]
assert not missinglinks,missinglinks
assert all(not any(v['core'] or v['core_plus_1_ring'] or v['diagnostic_52'] for v in [intersections[k]]) for k in intersections)
assert all(e['native_face_incidence']==2 and e['consistent_winding'] for e in topo_checks)
dump('DIAGNOSIS_ARTIFACT_VALIDATION_R1.json',{'status':'PASS','PNG_decodes':len(pngs),'review_local_references_checked':len(links),'missing_review_references':missinglinks,'three_actual_sections_per_stage':all(len(v)==3 for v in sections.values()),'all_protected_scope_intersections_empty':True,'ROI_native_manifold_winding_checks_pass':True})
artifacts={p.relative_to(OUT).as_posix():sha(p) for p in OUT.rglob('*') if p.is_file() and p.name!='ROUND_ARTIFACT_MANIFEST.json'}
dump('ROUND_ARTIFACT_MANIFEST.json',{'phase':PHASE,'status':status['status'],'artifact_count':len(artifacts),'artifacts_sha256':artifacts})
print(json.dumps({'status':status['status'],'historical_unchanged':len(before),'pngs':len(pngs),'seed_incident_faces':len(seed_incident),'CMC_min_distance_mm':protection['ROI_min_CMC_center_distance_mm']},indent=2))
