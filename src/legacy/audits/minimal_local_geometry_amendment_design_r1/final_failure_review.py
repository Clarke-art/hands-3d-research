import sys
sys.dont_write_bytecode=True
from design import *
from PIL import Image
import html,re
D=read(OUT/'GEOMETRY_AMENDMENT_CANDIDATES_R1.json');cs=D['candidates'];M=read(OUT/'CANDIDATE_LOCAL_GEOMETRY_METRICS_R1.json');met=M['metrics'];S=read(OUT/'CANDIDATE_BIND_SMOKE_PREVIEW_R1.json');CONTACT=read(OUT/'CANDIDATE_INDEPENDENT_CONTACT_AUDIT_R1.json');CMP=read(OUT/'CANDIDATE_WRITE_SET_COMPARISON_R1.json')
summary={};folds={}
for label,c in cs.items():
 folds[label]={};smoke={}
 for pose in ['BIND','IDX_MCP_15','IDX_MCP_30','IDX_MCP_45']:
  base={r['edge_id']:r for r in met['CURRENT'][pose]['all_local_dihedrals']};v=met[label][pose]
  interfaces=[]
  corrected=set(v['corrected_preexisting_reference_reversed_faces']);remaining=set(v['reference_normal_reversed_faces'])
  for a in v['all_local_dihedrals']:
   b=base[a['edge_id']]
   if b['angle_deg']<90 and a['angle_deg']>90 and set(a['face_ids'])&corrected and set(a['face_ids'])&remaining:
    interfaces.append({'edge_id':a['edge_id'],'vertices':E[a['edge_id']],'face_ids':a['face_ids'],'baseline_angle_deg':b['angle_deg'],'candidate_angle_deg':a['angle_deg'],'cause':'A corrected formerly inward face now meets a still-inward boundary face; the former nearly aligned facets become opposed across this edge.'})
  folds[label][pose]=interfaces
  smoke[pose]={'status':'FAIL_NEW_LOCAL_STRUCTURAL_DEFECT' if label in ['A','B'] else 'FAIL_NEW_BOUNDARY_SHARP_FOLD','contact_only':'PASS_NO_NEW_CONTACT' if not CONTACT['poses'][label][pose]['introduced_pairs'] else 'FAIL_NEW_CONTACT','introduced_contact_pairs':[r['face_ids'] for r in CONTACT['poses'][label][pose]['introduced_pairs']],'new_boundary_fold_interfaces':interfaces,'new_quad_bowties':v['introduced_projected_quad_bowties'],'new_degenerate_faces':v['introduced_degenerate_faces'],'new_reference_reversals':v['introduced_reference_normal_reversed_faces'],'write_pose_delta_mm':v.get('write_set_pose_displacement_from_bind_max_mm',0)}
 summary[label]={'WRITE_VERTEX_COUNT':len(c['write_vertices']),'MAX_DIHEDRAL_DEG':v['max_dihedral_deg'],'BIND_MAX_DIHEDRAL_DEG':met[label]['BIND']['max_dihedral_deg'],'EDGE6676_DIHEDRAL_DEG':met[label]['BIND']['edge6676_angle_deg'],'MAX_VERTEX_DISPLACEMENT_MM':c['max_displacement_mm'],'MEAN_VERTEX_DISPLACEMENT_MM':c['mean_displacement_mm'],'RMS_VERTEX_DISPLACEMENT_MM':c['RMS_displacement_mm'],'VISIBLE_DENT_STATUS':'CENTRAL_NOTCH_REDUCED_OR_REMOVED_BUT_CANDIDATE_REJECTED','NEW_VISIBLE_DEFECT':'NEW_LOCAL_CONTACT_AND_QUAD_BOWTIE; VISIBLE_SEVERITY_PENDING_HUMAN' if label in ['A','B'] else 'NEW_SHARP_FOLD_AT_TRANSITION_BOUNDARY; VISIBLE_SEVERITY_PENDING_HUMAN','BIND_PREVIEW':smoke['BIND']['status'],'IDX_MCP_15_PREVIEW':smoke['IDX_MCP_15']['status'],'IDX_MCP_30_PREVIEW':smoke['IDX_MCP_30']['status'],'IDX_MCP_45_PREVIEW':smoke['IDX_MCP_45']['status'],'smoke_details':smoke}
assert {x['edge_id'] for x in folds['C']['BIND']}=={6675,6602}
dump('CANDIDATE_BOUNDARY_CONTINUITY_FAILURE_R1.json',{'status':'FAIL_CLOSED_NEW_BOUNDARY_FOLD','definition':'Acute/obtuse are geometric signs of facet dot products, not anatomical acceptance thresholds. Here a corrected old inverted contour face meets an unchanged still-inward boundary face; actual relative facet geometry forms a new sharp transition. Both original/candidate plain solid boundary renders are provided. Do not infer Human-visible severity solely from a scalar.','new_interfaces':folds,'final_recommendation':'NONE','why_contact_pass_is_insufficient':'No contact or degenerate faces does not prove contour continuity. Lower global max angle cannot hide sharpness transferred to another edge.'})
dump('CANDIDATE_C_BOUNDARY_CONSTRAINT_STUDY_R1.json',{'DESIGN_ONLY_NOT_PRODUCTION':True,'study_pool':sorted(R['core_vertices']+R['1_ring']+[3315,3306,3338]),'attempts':[{'constraint_mode':'all_positive','result':'FAIL_FIXED_BOUNDARY_INFEASIBLE_FOR_THIS_CONSTRAINT','face_id':3316,'triangle':[3346,3322,3330],'explanation':'All3 triangle vertices are fixed outside the34-point pool and its signed tangent orientation opposes this constrained target. This proves only that specified fixed-boundary constraint cannot be met.'},{'constraint_mode':'C_boundary','result':'FAIL_FEASIBILITY_PROJECTION_NOT_CONVERGED','iteration_limit':4000,'remaining_signed_area_deficit_mm2':2.477875603846642,'explanation':'Relaxing the fixed face3316 to its original per-triangle sign still did not converge. Nonconvergence is not a proof that every position-only method is impossible.'}],'new_candidate_created':False,'topology_edit_performed':False,'retopo_required_proved':False})
S['candidate_summary']=summary;S['recommended_candidate']='NONE';S['contact_only_pass_does_not_imply_contour_pass']=True;S['final_boundary_audit']='CANDIDATE_BOUNDARY_CONTINUITY_FAILURE_R1.json';dump('CANDIDATE_BIND_SMOKE_PREVIEW_R1.json',S)
CMP['status']='DESIGN_WRITE_SETS_REJECTED_NOT_APPLICATION_AUTHORITY';CMP['recommended_candidate']='NONE';CMP['minimum_scope_limit']='No accepted minimum write set established. C22 came from documented comparative pruning but fails the final per-edge boundary audit. Its previous global-max-angle criterion was insufficient.';dump('CANDIDATE_WRITE_SET_COMPARISON_R1.json',CMP)
plan=read(OUT/'CANDIDATE_DOWNSTREAM_BLAST_RADIUS_R1.json');plan['candidate']='NONE_RECOMMENDED';plan['investigated_C_write_vertex_ids']=plan.pop('write_vertex_ids',plan.get('investigated_C_write_vertex_ids',cs['C']['write_vertices']));plan['future_write_scope_established']=False;plan['status']='CONDITIONAL_DOWNSTREAM_PLAN_ONLY_AFTER_A_NEW_DESIGN_AND_HUMAN_APPROVAL';dump('CANDIDATE_DOWNSTREAM_BLAST_RADIUS_R1.json',plan)
before=read(OUT/'HISTORICAL_HASHES_BEFORE.json');after=inventory();changed=[p for p,h in before.items() if p in after and after[p]!=h];missing=sorted(set(before)-set(after));added=sorted(set(after)-set(before));assert not changed and not missing and not added,(changed,missing,added)
dump('PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json',{'status':'PASS_ALL_PREEXISTING_WORKSPACE_FILES_SHA256_IDENTICAL','file_count':len(before),'changed':changed,'missing':missing,'added_outside_design_directory':added,'PRODUCTION_DRIFT':0,'before_inventory_sha256':digest(before),'after_inventory_sha256':digest(after),'production_blend_saves':0,'Full42Stage6A_rerun':False,'Stage6B':False,'promotion':False,'coverage':'All history, frozen authority, previous diagnosis, Human receipts and prior FullStage6A failure evidence; only this new design directory excluded.'})
status={'phase':PHASE,'status':'FAIL_CLOSED_POSITION_ONLY_GEOMETRY_DESIGN','ROOT_CAUSE_CLASS':'BASE_GEOMETRY_CONTOUR_DEFECT','RECOMMENDED_AMENDMENT_SOURCE_LAYER':plan['RECOMMENDED_AMENDMENT_SOURCE_LAYER'],'CANDIDATE_COUNT':3,'CANDIDATE_A_WRITE_VERTEX_COUNT':15,'CANDIDATE_B_WRITE_VERTEX_COUNT':18,'CANDIDATE_C_WRITE_VERTEX_COUNT':22,'TOPOLOGY_CHANGED_ANY_CANDIDATE':'NO','RET0PO_REQUIRED':'NO','retopo_explanation':'These three local methods failed; no proof that all position-only approaches are impossible or that retopo is required. No topology authority reopened.','BASELINE_MAX_DIHEDRAL_DEG':met['CURRENT']['BIND']['max_dihedral_deg'],'candidates':summary,'RECOMMENDED_CANDIDATE':'NONE','RECOMMENDED_WRITE_VERTEX_COUNT':0,'RECOMMENDATION_REASON':'A/B introduce contacts and quad bow-ties. C removes the selected central notch and passes contacts, but creates boundary sharp folds at6675/6602. Therefore no candidate meets all requirements.','POSITION_ONLY_INSUFFICIENT':'NOT_PROVED_GLOBALLY; THIS_BOUNDED_THREE_CANDIDATE_STUDY_FAILED','PRODUCTION_DRIFT':0,'historical_files_unchanged':len(before),'future_application_authorized':False,'formal_amendment_executed':False,'FullStage6A_status_unchanged':'FAIL_CLOSED_FULL_STAGE6A_REQUALIFICATION','old9_independent_blockers_unchanged':True,'NEXT':'NONE_EXECUTED','STOP':'HUMAN REVIEW'}
dump(PHASE+'_STATUS.json',status)
def im(p,c):return f'<figure><a href="{p}"><img loading="lazy" src="{p}" alt="{html.escape(c)}"></a><figcaption>{c}</figcaption></figure>'
def pair(k,p,m,t):return f'<h3>{t}</h3><div class="pair">'+im(f'renders/CURRENT_{p}_{m}.png','CURRENT / baseline')+im(f'renders/{k}_{p}_{m}.png',f'{k} / DESIGN ONLY / rejected')+'</div>'
rows=''.join(f'<tr><td>{k}</td><td>{s["WRITE_VERTEX_COUNT"]}</td><td>{s["MAX_VERTEX_DISPLACEMENT_MM"]:.6f}</td><td>{s["RMS_VERTEX_DISPLACEMENT_MM"]:.6f}</td><td>{s["BIND_MAX_DIHEDRAL_DEG"]:.3f}</td><td>{s["EDGE6676_DIHEDRAL_DEG"]:.3f}</td><td>{"新contact / quad bow-tie" if k!="C" else "新边界锐折"}</td></tr>' for k,s in summary.items())
gallery=''
for label in ['C','A','B']:
 gallery+=f'<section><h2>Candidate {label} · {len(cs[label]["write_vertices"])}点 · FAIL</h2>'
 for mode,title in [('HUMAN_CAMERA','原Human发现机位'),('DORSAL_WHOLE','完整右手dorsal'),('CLOSE','近距离普通实体'),('GRAZING','Grazing-angle普通实体'),('BOUNDARY_FOLD','边界edge6675附近普通实体')]:gallery+=pair(label,'BIND',mode,title)
 gallery+='<details><summary>RSSF / Bind / IDX15/30/45；wire、三截面、silhouette、额外角度</summary>'+pair(label,'RSSF_RAW','CLOSE','Stage4/RSSF representation')
 for pose in ['IDX_MCP_15','IDX_MCP_30','IDX_MCP_45']:gallery+=pair(label,pose,'CLOSE',pose+' · diagnostic preview only')
 for mode,title in [('WIRE','Native wire'),('SECTIONS','Actual0/60/120degree sections'),('SILHOUETTE','Side silhouette'),('ANGLE_2','额外观察角度')]:gallery+=pair(label,'BIND',mode,title)
 gallery+='</details></section>'
review='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Geometry design R1 · fail closed</title><style>body{font:16px/1.6 system-ui,sans-serif;background:#f5f3ee;color:#272e35;max-width:1200px;margin:30px auto;padding:0 22px}section{background:white;padding:20px;margin:20px 0;border-radius:8px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:14px}img{width:100%;display:block;max-height:660px;object-fit:contain}figure{margin:8px 0}figcaption{text-align:center;font-size:13px}h1{font-size:26px}h2{font-size:22px}h3{font-size:16px}.fail{background:#f9dfd7;padding:18px;border-radius:8px}td,th{border:1px solid #ddd;padding:6px}table{border-collapse:collapse;width:100%;font-size:13px}code{overflow-wrap:anywhere}a{color:#235e83}summary{cursor:pointer}@media(max-width:650px){.pair{grid-template-columns:1fr}}</style><h1>3个position-only方案均未达到完整要求</h1><p class="fail"><strong>FAIL_CLOSED_POSITION_ONLY_GEOMETRY_DESIGN · STOP — HUMAN REVIEW</strong><br>无推荐candidate，无future application。A/B改善中心凹口，但引入contact / quad bow-tie。C通过接触检查且中心凹口消失，却把锐折推到过渡边界；降低全局最大角不能掩盖这项失败。</p><section><h2>C的最小失败原因：边界锐折被新建</h2><p>edge6675（faces3344/3345）由27.929°变为153.910°；edge6602（faces3298/3301）由25.669°变为116.906°。展开的旧向内面仍连接到未展开的边界面，形成新的相向facet界面。这里是实际几何改变与前后对照，不创造人体角度验收阈值。可见严重性仍由Human判断；设计边界连续性已不足，故不推荐。</p>'''+pair('C','BIND','BOUNDARY_FOLD','边界matched普通实体：CURRENT → C')+pair('C','BIND','CLOSE','中心notch改善不能替代边界检查')+'''</section><section><h2>候选数据</h2><table><tr><th>候选</th><th>点数</th><th>最大位移mm</th><th>RMS mm</th><th>全比较域最大角°</th><th>edge6676°</th><th>失败原因</th></tr>'''+rows+'''</table><p>C从必要34点支持池逐点恢复到22点（12core、7原1-ring、3原2-ring），恢复12点，包括3个core。该比较缩减并未建立合格最小write scope。三候选拓扑/UV/material/normal flags/weights/bones不变，write之外坐标精确不变。</p><p>C的22点及全部15诊断core在INDEX15/30/45相对BIND不动；这只说明没有被这些pose再放大，不代表静态边界已合格。原Full42 FAIL_CLOSED与9对独立crossings保持原样。</p><p>C移动3个原2-ring支持点，refitted depth proxy1.652734mm，冻结baseline ring-fit参考下0.747559mm；两者都保留，实际截面与实体为主。其中心shallow target未平面化，但边界失败仍阻止推荐。</p>'''+im('renders/CANDIDATE_SECTION_OVERLAY.png','Actual sections CURRENT / A / B / C；固定axes，无人体threshold')+'''</section>'''+gallery+'''<section><h2>Source layer、范围与STOP</h2><p>未来逻辑源应为frozen Stage4C_R2 / RSSF的新派生版本；Stage4A_R2_BASE只作earliest evidence，不能覆盖历史。本轮所有设计coordinate copies为DESIGN_ONLY_NOT_PRODUCTION，没有保存blend或正式amendment。</p><p>试图在34点pool中约束完整边界：all-positive目标碰到face3316三个固定顶点；放松该固定三角绕序后投影未收敛。这只证明当前约束/方法失败，不能推导所有position-only方法都不可能，也不能自动进入retopo。</p><p><strong>RECOMMENDED_CANDIDATE=NONE · RECOMMENDED_WRITE_VERTEX_COUNT=0</strong><br>RET0PO_REQUIRED=NO（未证明需要）。不执行更大geometry scope、topology/retopo、skin/bone修改或应用。</p><p><a href="MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R1_REPORT.md">完整报告</a> · <a href="MINIMAL_LOCAL_GEOMETRY_AMENDMENT_DESIGN_R1_STATUS.json">状态</a> · <a href="CANDIDATE_WRITE_SET_COMPARISON_R1.json">每点位移/实际write IDs</a> · <a href="CANDIDATE_BOUNDARY_CONTINUITY_FAILURE_R1.json">逐边失败证据</a> · <a href="CANDIDATE_DOWNSTREAM_BLAST_RADIUS_R1.json">条件downstream plan</a> · <a href="PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json">零漂移</a></p><strong>STOP — HUMAN REVIEW</strong></section></html>'''
review=review.replace('可见严重性仍由Human判断；设计边界连续性已不足，故不推荐。','完整手表面机位中部分边界facet被其他表面遮挡；此处不宣称新增产品瑕疵的Human-visible严重性。真实vertex/facet的过渡折返未解决，设计边界连续性不足，故不推荐。')
(OUT/'review.html').write_text(review,encoding='utf-8')
report_rows='\n'.join(f'| {k} | {s["WRITE_VERTEX_COUNT"]} | {s["MAX_VERTEX_DISPLACEMENT_MM"]:.9f} | {s["MEAN_VERTEX_DISPLACEMENT_MM"]:.9f} | {s["RMS_VERTEX_DISPLACEMENT_MM"]:.9f} | {s["BIND_MAX_DIHEDRAL_DEG"]:.9f} | {s["EDGE6676_DIHEDRAL_DEG"]:.9f} |' for k,s in summary.items())
report=f'''# {PHASE}

**FAIL_CLOSED_POSITION_ONLY_GEOMETRY_DESIGN**。3个候选全部未达到完整要求，**RECOMMENDED_CANDIDATE=NONE，RECOMMENDED_WRITE_VERTEX_COUNT=0**。禁止应用或自动转入retopo。

## Root与正确source layer

ROOT_CAUSE_CLASS=BASE_GEOMETRY_CONTOUR_DEFECT。完整继承上一轮诊断：Stage4C raw/RSSF/R2 BIND/IDX15均可见；shading仅强调，armature zero只有浮点误差，skin不是静态根因，原INDEX poses没有支持放大。上一轮所有诊断文件保持原hash。

RECOMMENDED_AMENDMENT_SOURCE_LAYER={plan['RECOMMENDED_AMENDMENT_SOURCE_LAYER']}。现有frozen Stage4C_R2是生产lineage geometry baseline，包含现有CMC/RSSF；未来必须新建派生geometry版本，再明确派生corrected Stage5A/R2候选，不能原位覆盖。Stage4A_R2_BASE_PRE_CMC_RETOPO只作earliest defect evidence，不回填改写历史。本轮仅mesh coordinate copies / temporary rig evaluation，无blend save。

## 方法与candidate scope

A：15core-only，graph biharmonic tangent fairing；normal方向75% curved quadratic ring-fit shallow-valley target+25% biharmonic height。6mm Gaussian width与0.65mm offset为设计参数，不是人体阈值。保留curved valley，未以平面或normal/material伪修复。

B：core+3300/3308/3347，18点。初版无非邻接contact，但完整quad检查发现bow-tie；加入面方向可行性约束后仍有新contact/bow-tie，失败。

C只在A/B失败后创建：15core+16诊断1-ring+3 directly incident2-ring点3315/3306/3338，34点局部支持池。确定性按初始位移/vertex ID排序逐点恢复，比较bow-tie/reference reversal、global max角、固定ring reference深度与主折边，恢复12点到22点（12core/7ring1/3ring2），包含恢复3个原core点80/2096/3323。没有默认write52或默认core15必须全部改。恢复顺序、每点trial接受/拒绝理由、所有candidate position vectors/幅度/新坐标在GEOMETRY_AMENDMENT_CANDIDATES_R1.json。

最终逐边检查揭示：仅限制global max角的缩减准则不足，会让锐折迁移到边界。因此22点不是合格最小write set，也不是全局最小集合证明。

## 必需数字

CANDIDATE_COUNT=3；CANDIDATE_A_WRITE_VERTEX_COUNT=15；B=18；C=22。TOPOLOGY_CHANGED_ANY_CANDIDATE=NO。RET0PO_REQUIRED=NO：当前有限方法失败不证明需要retopo。POSITION_ONLY_INSUFFICIENT=NOT_PROVED_GLOBALLY。

BASELINE_MAX_DIHEDRAL_DEG={met['CURRENT']['BIND']['max_dihedral_deg']:.9f}。

| Candidate | 点数 | MAX_VERTEX_DISPLACEMENT_MM | mean mm | RMS_VERTEX_DISPLACEMENT_MM | MAX_DIHEDRAL_DEG（BIND，同域） | edge6676° |
|---|---:|---:|---:|---:|---:|---:|
{report_rows}

全比较域包括所有candidate incident faces及诊断面，各方案同域。每点design world-mm displacement和actual float32-preview displacement完整保存于CANDIDATE_WRITE_SET_COMPARISON_R1.json。actual22点之外精确0；design-to-float32最大误差约0.000060mm。C完整ids=`{cs['C']['write_vertices']}`，仅作为失败设计证据，无写入授权。

## 最小失败原因与最终gate

A/B中心notch减弱，但引入新的local exact contact（独立包含shared-topology检查分别3/6对）及projected quad bow-tie。因此它们不合格，不因小scope或好看的solid而推荐。

C中心原尖notch在实体/grazing中消失，接触/degenerate/reference-reversal/bow-tie检查也pass；但出现两个新过渡折边：

* edge6675，faces3344/3345：baseline27.929° → C153.910°。
* edge6602，faces3298/3301：baseline25.669° → C116.906°。

展开的旧向内face连接到仍向内的boundary face，从原近同向facet变成新的相向facet界面。该现象在实际geometry中，普通matched boundary实体及grazing/side图可审阅。acute/obtuse只是法线dot product几何符号，不是人体阈值；可见严重性仍由Human决定。但是新sharp transition已不满足“不得把缺陷推到边界”，因此C拒绝。C整体max仍169.036°（旧边界edge6689），不能用global max下降隐藏新edge6675。

各candidate VISIBLE_DENT_STATUS=CENTRAL_NOTCH_REDUCED_OR_REMOVED_BUT_CANDIDATE_REJECTED。NEW_VISIBLE_DEFECT：A/B有新local contact/quad bow-tie，具体视觉severity由Human；C有新boundary sharp fold，不能宣称无新问题。BIND_PREVIEW / IDX_MCP_15_PREVIEW / IDX_MCP_30_PREVIEW / IDX_MCP_45_PREVIEW：A/B=FAIL_NEW_LOCAL_STRUCTURAL_DEFECT，C=FAIL_NEW_BOUNDARY_SHARP_FOLD。C的contact-only PASS不等于overall contour PASS。

进一步在相同34点支持池尝试完整边界orientation约束：all-positive target碰到face3316三角[3346,3322,3330]的三个fixed vertices，当前fixed-boundary约束不可满足；保留该固定triangle原绕向后，4000次projection仍未收敛（remaining signed-area deficit2.4778756mm²）。非收敛不是所有position-only方法不可能的证明。该refinement未构成第4个Human candidate，没有新增topology或扩大正式写入权限。

## RSSF / Bind / smoke与证据

每candidate均以source原flat flags/material/UV matched普通实体为主，提供原Human机位、完整右手dorsal、close、grazing、额外角度、wire、actual0/60/120degree sections及side silhouette。Stage4/RSSF raw与temporary downstream BIND展示均有。相同camera/scale/light/material/pose比较；normal仅自然随顶点几何重算，不改flags作为伪修复。

source R2 existing weights/rig只临时绑定到copy。Baseline4states与原FullStage6A保存坐标全mesh精确一致。C所有22个write vertices与15 diagnostic core在IDX15/30/45相对BIND坐标精确不动；因此失败是静态边界问题，不是被INDEX pose再放大。仅4-state diagnostic preview，不是Full42 qualification。

BVH/既有exact kernels之外，独立float64 AABB+双向edge/triangle clipping+coplanar area clipping检查candidate incident region against whole mesh；包括sharing vertex/edge native faces，只排除真正公共点/边本身合法接触。C无新contact，仍因boundary fold失败。数值容差属于计算几何，不是Stage6或生理gate。

三截面保留native face ID及world/profile segments，native quad fan triangulation，固定diagnosis frame/axes。plane/quadratic residual、umbrella curvature、normal angles均保存。C移动3个2-ring点，refit quadratic depth1.652734mm与冻结baseline ring-fit reference depth0.747559mm都保留（baseline1.546247mm）；不能把reference变化掩饰为真实深度，也不能以中心depth改善代替边界连续性。

## Frozen gate与条件downstream plan

所有candidate vertex/edge/face count unchanged：{len(V)}/{len(E)}/{len(F)}。face winding、2-face incidence/manifold、UV/material assignment、原normal flags、自定义normal状态、全部weights/21-bone rest不变。native计数/绕序不变不保证contour，故C仍失败。

各write set分别核对nail/cap37/oldcap9/FIRST_WEB21/fresh R3 bounded graph/historical317/CMC20mm context，交集空。没有重开authority研究。原9对severe exact crossings未重新裁决；局部contact减少仅记INCIDENTAL_DIAGNOSTIC_EFFECT，不用作排名目标。

无推荐candidate或future write scope。条件downstream plan仍说明未来若另一个设计经Human批准：MUST_REVALIDATE Stage4所有incident/boundary contour/manifold/winding/UV/material、Stage5 geometry propagation/joint-surface alignment/rest/bind/zero/static skin、geometry-derived true-cap paths/bounds、targeted deformation/Full42/Human product review；LIKELY_HASH_NUMERIC_RECOMPUTE new geometry/blend payload与相关path/edge/bound数值；NO_RESEARCH_REOPEN anatomy、R3/cap37/FIRST_WEB/CMC、317、bone/joint、retopo。当前不执行这些阶段。

## 零漂移与STOP

PRODUCTION_DRIFT=0：本轮前已有{len(before)}个工作区文件全部SHA256一致，changed/missing/目录外added均0。全部frozen资产、历史blend、Human receipts、上一轮诊断与FullStage6A失败证据不变。无正式geometry/weight/bone/RSSF edit，未Full42 rerun、Stage6B或promotion。

RECOMMENDATION_REASON=All3 candidates fail at least one required structural/contour condition。RECOMMENDED_CANDIDATE=NONE。RECOMMENDED_WRITE_VERTEX_COUNT=0。不自动进入更大scope、topology/retopo或正式geometry amendment。

**STOP — HUMAN REVIEW**
'''
report=report.replace('可见严重性仍由Human决定。但是新sharp transition','完整手表面机位下部分边界facet遮挡，不能仅靠该实体机位宣称新增可见产品瑕疵；Human-visible严重性仍由Human决定。但是实际vertex/facet的新sharp transition')
(OUT/(PHASE+'_REPORT.md')).write_text(report,encoding='utf-8')
for p in (OUT/'renders').glob('*.png'):
 with Image.open(p) as im2:im2.verify()
assert all((OUT/p).is_file() for p in re.findall(r'(?:href|src)="([^"]+)"',review))
dump('FINAL_ARTIFACT_VALIDATION_R1.json',{'status':'PASS_ARTIFACT_INTEGRITY_NOT_CANDIDATE_ACCEPTANCE','candidate_gate':'FAIL_CLOSED_ALL3','PNG_decode_count':len(list((OUT/'renders').glob('*.png'))),'review_references_resolve':True,'historical_files_unchanged':len(before),'no_application':True})
dump('ROUND_ARTIFACT_MANIFEST.json',{'phase':PHASE,'status':status['status'],'artifact_hashes':{p.relative_to(OUT).as_posix():sha(p) for p in OUT.rglob('*') if p.is_file() and p.name!='ROUND_ARTIFACT_MANIFEST.json'}})
print(json.dumps({'status':status['status'],'recommended':'NONE','candidates':3,'historical_unchanged':len(before)},indent=2))
