import sys
sys.dont_write_bytecode=True
from common import *
import numpy as np, math, html, shutil
from PIL import Image
G=read(OUT/'DIAGNOSTIC_RENDER_GEOMETRY_R1.json');roi=G['roi'];metrics=read(OUT/'PALMAR_IRREGULARITY_GEOMETRY_METRICS_R1.json');states=metrics['states'];native=read(OUT/'NATIVE_SHADING_READBACK_R1.json');over=read(OUT/'PALMAR_IRREGULARITY_CURRENT9_OVERLAP_R1.json');skin=read(OUT/'PALMAR_IRREGULARITY_SKIN_DRIVER_DIAGNOSTIC_R1.json');sections=read(OUT/'PALMAR_IRREGULARITY_NATIVE_CROSS_SECTIONS_R1.json')
# Explicit local face cycle check for exact lineage mapping, no global index assumption.
src=read(SOURCE/'RAW_SOURCE_GEOMETRY.json')['stages'];donor=read(OUT/'PALMAR_IRREGULARITY_SOURCE_DONOR_COMPARISON_R1.json');mapping=donor['candidate_current_to_source'];basefaces={tuple(p):i for i,p in enumerate(src['STAGE4A_R2_BASE']['faces'])}
def cyc(p):return min(tuple(p[i:]+p[:i]) for i in range(len(p)))
basecycles={cyc(p):i for i,p in enumerate(src['STAGE4A_R2_BASE']['faces'])};facemap={};missing=[]
for fi in roi['visible_hit_faces']:
 p=[mapping[str(i)]['stage4a_base_vertex'] for i in G['faces'][fi]];bi=basecycles.get(cyc(p))
 if bi is None:missing.append(fi)
 else:facemap[str(fi)]=bi
donor['candidate_current_to_stage4a_base_oriented_face_ids']=facemap;donor['candidate_unresolved_oriented_face_ids']=missing;donor['exact_face_cycle_validation']=not missing
donor['candidate_source_visual_observation']='Official L1 and identical Stage2 L1 have coarse root creases but the current long diagonal facet band is visually stronger/different. Their topology/shape differ; fixed registration RMS 0.895 mm is not a defect metric. Product defect and Human target are unresolved.';dump('PALMAR_IRREGULARITY_SOURCE_DONOR_COMPARISON_R1.json',donor)
# Native geometric crease witnesses, with no structural/product threshold.
rawedge={x['edge_id']:x for x in states['CURRENT_R2_RAW']['adjacent_face_dihedral']};a4edge={x['edge_id']:x for x in states['STAGE4A_R2']['adjacent_face_dihedral']};posededge={x['edge_id']:x for x in states['IDX_MCP_30']['adjacent_face_dihedral']}
witnesses=sorted([{'edge_id':i,'vertex_ids':r['vertex_ids'],'face_ids':r['face_ids'],'STAGE4A_R2_angle_deg':a4edge[i]['dihedral_degrees'],'CURRENT_RAW_angle_deg':r['dihedral_degrees'],'IDX_MCP_30_angle_deg':posededge[i]['dihedral_degrees'],'base_lineage_angle_change_deg':r['dihedral_degrees']-a4edge[i]['dihedral_degrees'],'pose_angle_change_deg':posededge[i]['dihedral_degrees']-r['dihedral_degrees']} for i,r in rawedge.items()],key=lambda z:-z['base_lineage_angle_change_deg'])
metrics['candidate_hard_crease_edge_witnesses']=witnesses;metrics['native_cross_section_source']='PALMAR_IRREGULARITY_NATIVE_CROSS_SECTIONS_R1.json';metrics['source_lineage_metrics']={}
for label in ['OFFICIAL_L1','STAGE2_L1','STAGE4A_R2_BASE']:
 s=G['source_states'][label];v=np.array(s['positions_mm']);ff=s['faces'];fset=set(s['roi_faces']);nn={};aa={};adj={}
 for fi in fset:
  p=ff[fi];q=v[p];n=sum((np.cross(q[k]-q[0],q[k+1]-q[0]) for k in range(1,len(q)-1)),np.zeros(3));aa[str(fi)]=float(np.linalg.norm(n)/2);nn[fi]=n/max(np.linalg.norm(n),1e-15)
  for a,b in zip(p,p[1:]+p[:1]):adj.setdefault(tuple(sorted((a,b))),[]).append(fi)
 di=[{'vertex_ids':list(e),'face_ids':f,'dihedral_degrees':math.degrees(math.acos(float(np.clip(nn[f[0]]@nn[f[1]],-1,1))))} for e,f in adj.items() if len(f)==2];di.sort(key=lambda z:-z['dihedral_degrees'])
 metrics['source_lineage_metrics'][label]={'ROI_native_face_count':len(fset),'face_area_mm2':aa,'adjacent_face_dihedral':di,'comparison_caveat':'different topology/support boundaries; not numerically equivalent same-face threshold test'}
dump('PALMAR_IRREGULARITY_GEOMETRY_METRICS_R1.json',metrics)
lineage=read(OUT/'PALMAR_IRREGULARITY_LINEAGE_COMPARISON_R1.json');lineage['candidate_earliest_confirmed_coarse_root_crease']='OFFICIAL_L1 / STAGE2_L1';lineage['candidate_earliest_confirmed_engineered_root_band']='STAGE4A_R2_BASE';lineage['candidate_amplification']='STAGE4A_R2 to STAGE4B_RSSF changes native adjacent-face dihedral; e.g. edge 2810 0.6666 to 11.5220 degrees. Current Stage4C and R2 inherit this angle. Donor transfer moves two peripheral ROI vertices but does not alter the measured interior native dihedral witnesses.';lineage['native_face_identity_validation']=donor['exact_face_cycle_validation'];lineage['candidate_geometry_earliest_introduction_causal_limit']='cached snapshots establish earliest observed stage; no new operation replay was executed to prove the specific operation';dump('PALMAR_IRREGULARITY_LINEAGE_COMPARISON_R1.json',lineage)
sh=read(OUT/'PALMAR_IRREGULARITY_GEOMETRY_VS_SHADING_R1.json');sh.update(candidate_flat_shading_shows_native_faceting=True,candidate_smooth_shading_only=False,candidate_real_geometry_crease_present=True,candidate_custom_normal_artifact=False,candidate_shading_amplifies_visibility=True,candidate_evidence='FLAT/SOURCE_NATIVE and WIRE retain native crease; true sections are piecewise geometry; smooth calculated normals alter visibility but do not remove baseline ridge',actual_runtime=native['runtime']);dump('PALMAR_IRREGULARITY_GEOMETRY_VS_SHADING_R1.json',sh)
comparison=read(OUT/'PALMAR_IRREGULARITY_RAW_ZERO_POSED_COMPARISON_R1.json');comparison['candidate_visibility']={'RAW':True,'ZERO':True,'IDX_MCP_15':True,'IDX_MCP_30':True,'TH_IP_15':True};comparison['candidate_ZERO_BIND_DEFORMATION_DEFECT']=False;comparison['candidate_pose_introduction']=False;comparison['candidate_pose_amplification']='localized/mild IDX change; no TH_IP change; no whole-ROI surface collapse';dump('PALMAR_IRREGULARITY_RAW_ZERO_POSED_COMPARISON_R1.json',comparison)
candidate={'ROI_VERTEX_COUNT':len(roi['vertices']),'ROI_FACE_COUNT':len(roi['visible_hit_faces']),'IRREGULARITY_VISIBLE_IN_OFFICIAL_L1':'coarse root creases yes; same current diagonal band unresolved','IRREGULARITY_VISIBLE_IN_STAGE2':'same as saved official L1','IRREGULARITY_VISIBLE_IN_STAGE4C_RAW':True,'IRREGULARITY_VISIBLE_IN_CURRENT_R2_RAW':True,'IRREGULARITY_VISIBLE_IN_ZERO':True,'IRREGULARITY_VISIBLE_IN_POSED':True,'FLAT_SHADING_SHOWS_DEFECT':'native geometric facets yes; structural defect not inferred from flat appearance','SMOOTH_SHADING_ONLY':False,'REAL_GEOMETRY_FOLD_PRESENT':'geometric ridge/crease yes; severe inversion or self-overlap not established','POSE_AMPLIFICATION':'localized IDX influence; max displacement 1.78755 mm; median approx 0.000030 mm; TH_IP none','SKIN_CAUSAL':'existing LBS explains limited IDX displacement, not baseline crease','KINEMATIC_CAUSAL':'frozen single-joint transform explains displacement; rig defect not established','NORMAL_SHADING_CAUSAL':'visual modulation yes; custom split-normal artifact no','CURRENT9_PAIR_DIRECT_OVERLAP_COUNT':over['candidate_direct_pair_overlap_count'],'CURRENT9_NEIGHBORHOOD_OVERLAP_COUNT':over['candidate_neighborhood_overlap_count'],'CROSSING_VISIBLE_MANIFESTATION':'no evidence linking candidate to current9','EARLIEST_CONFIRMED_IRREGULARITY_STAGE':'source coarse root creases at OFFICIAL_L1; engineered band observed at STAGE4A_R2_BASE, strengthened by STAGE4B_RSSF','ROOT_CAUSE_CLASS':'UNRESOLVED_FOR_HUMAN_TARGET; candidate geometry baseline + shading visibility + limited IDX deformation','MACHINE_STRUCTURAL_DEFECT':'UNRESOLVED; no anatomy/product threshold invented','VISIBLE_PRODUCT_CONCERN':'candidate conspicuous facet band, Human product acceptability pending','minimum_repair_layer_if_candidate_confirmed':'first design review of local base geometry continuity and display normals; normal-only sufficiency unproven; no weight/rig repair justified by these data'}
unresolved={k:'UNRESOLVED' for k in candidate if k not in ['ROI_VERTEX_COUNT','ROI_FACE_COUNT','minimum_repair_layer_if_candidate_confirmed']}
status={'phase':PHASE,'status':'UNRESOLVED_HUMAN_TARGET_WITH_COMPLETED_CANDIDATE_DIAGNOSIS','MATCHED_CASE':None,'MATCHED_POSE':None,'MATCH_CONFIDENCE':'UNRESOLVED_NO_SCREENSHOT','ROI_VERTEX_COUNT':len(roi['vertices']),'ROI_FACE_COUNT':len(roi['visible_hit_faces']),'ROI_SCOPE':'PROVISIONAL_CANDIDATE_ONLY',**unresolved,'ROOT_CAUSE_CLASS':'UNRESOLVED','CURRENT_9_CROSSING_HUMAN_RESPONSE':'HOLD_NOT_CLOSED','FULL42_RERUN':0,'DIAGNOSTIC_ONLY_MICRO_POSE_PROBE_COUNT':0,'GEOMETRY_WRITES':0,'WEIGHT_WRITES':0,'NORMAL_WRITES':0,'RIG_WRITES':0,'JOINT_WRITES':0,'MATERIAL_WRITES':0,'MODIFIER_WRITES':0,'STAGE6B_RUNS':0,'PRODUCTION_PROMOTION':'NO','PRODUCTION_DRIFT':0,'NEXT':'PALMAR_DIGIT_ROOT_EVIDENCE_EXPANSION_R1','NEXT_EXECUTED':False,'STOP':'STOP — HUMAN REVIEW','candidate_findings':candidate,'required_evidence':'Human identifies the candidate image/ROI or supplies original screenshot; no automatic product PASS'}
dump('PALMAR_IRREGULARITY_ROOT_CAUSE_R1.json',{'classification':'UNRESOLVED','reason':'exact Human screenshot/region cannot be uniquely matched; candidate findings cannot be substituted for Human target','candidate_findings':candidate,'seven_questions':{'1_geometry_or_normals':'candidate contains actual native geometric creases; smooth display amplifies them; no custom-normal artifact','2_bind_zero':'candidate visible in RAW and ZERO; numerical ZERO noise only','3_stage6_pose':'not introduced by sampled Stage6 poses; IDX limited modulation, TH_IP none','4_pose_related_mechanism':'LBS with fixed joint transform reconstructs saved displacements; skin failure or rig defect not established','5_current9':'candidate has zero direct and neighborhood overlap; no causal crossing linkage','6_earliest_lineage':'coarse source root creases already in official L1/Stage2; engineered band observed at Stage4A_R2_BASE and amplified at Stage4B_RSSF; exact Human target unresolved','7_minimal_repair_layer':'conditional local base geometry/shading design review only; requires target confirmation first'},'product_judgment':'HUMAN_PRODUCT_ACCEPTABILITY_PENDING','NEXT':status['NEXT'],'executed_repair':False})
dump(PHASE+'_STATUS.json',status)
# Preserve the external downloaded response without copying it into authority.
before=read(OUT/'RESPONSE_SOURCE_HASH_BEFORE.json');response=read(RESPONSE);after=ref(RESPONSE)
assert before['source']['sha256']==after['sha256']
dump('CURRENT9_HUMAN_RESPONSE_HOLD_VERIFICATION_R1.json',{'source_external_to_workspace':str(RESPONSE),'sha256_before':before['source']['sha256'],'sha256_after':after['sha256'],'size_bytes':RESPONSE.stat().st_size,'byte_preserved':True,'case_reviews_count':len(response['case_reviews']),'pair_reviews_count':len(response['pair_reviews']),'exact_scope_confirmation':response['exact_scope_confirmation'],'CURRENT_9_CROSSING_HUMAN_RESPONSE':'HOLD_NOT_CLOSED','approval_receipts_created':0,'human_closures_created':0,'active_authority_writes':0})
# Review page preserves the requested ordering while explicitly marking the missing screenshot match.
def img(path,title,desc=''):
 return '<figure><a href="'+html.escape(path)+'" target="_blank"><img loading="lazy" src="'+html.escape(path)+'" alt="'+html.escape(title)+'"></a><figcaption><b>'+html.escape(title)+'</b><br>'+html.escape(desc)+'</figcaption></figure>'
def render(state,kind='SMOOTH',angle='MATCHED_CANDIDATE'):return f'renders/{state}__{angle}__{kind}.png'
originals=OUT/'candidate_source_views';originals.mkdir(exist_ok=True)
for cid in CASES:
 for kind in ['LOCAL_ALTERNATE','LOCAL_PRIMARY']:
  shutil.copyfile(PREP/f'renders/{cid}__{kind}.png',originals/f'{cid}__{kind}.png')
body='<h1>掌侧指根表面不规则 · 只读因果诊断 R1</h1><div class="hold">STOP — HUMAN REVIEW · Current9 HOLD_NOT_CLOSED · 所有 production writes = 0</div>'
body+='<h2>1 · Human screenshot-matched view：未能唯一匹配</h2><p>本次未提供原始截图。以下为原有 fresh renders 的候选，图片可点击放大。详细 ROI 来自 IDX_MCP_30 / LOCAL_ALTERNATE；它不是已确认的 Human 目标。</p><div class="grid">'
for cid in CASES:body+=img(f'candidate_source_views/{cid}__LOCAL_ALTERNATE.png',cid+' · LOCAL_ALTERNATE','原 review 实体图；case/相机可恢复，截图身份待确认')
body+='</div>'+img('renders/CANDIDATE_PIXEL_SELECTION.png','候选 ROI 的像素选区','射线定位：92 vertices / 62 faces；选区仅用于诊断，不是解剖或验收 authority')
body+='<h2>2 · RAW / ZERO / POSED · 三列普通实体</h2><p>同一相机、scale 和原生 topology，使用与原 review 相同的 smooth 显示副本；无 forensic overlay。正式 SOURCE_NATIVE flags 全为 flat，见下一行。</p><div class="grid">'
for state,label in [('CURRENT_R2_RAW','RAW · Armature OFF coordinates'),('CURRENT_R2_ZERO','ZERO · saved evaluated BIND'),('IDX_MCP_30','POSED · saved IDX_MCP_30')]:body+=img(render(state),label)
body+='</div><h2>3 · FLAT / SMOOTH / WIRE</h2><p>FLAT = 当前 SOURCE_NATIVE。SMOOTH 为 display-only calculated normals。WIRE 显示候选 ROI；全部原生 surface faces 保留。</p><div class="grid">'
for kind in ['SOURCE_NATIVE','SMOOTH','WIRE']:body+=img(render('IDX_MCP_30',kind),'IDX_MCP_30 · '+kind)
body+='</div><h2>4 · 真实 mesh cross-section</h2><p>使用 Blender 原生 loop triangles 与平面相交；RAW/ZERO/POSED 共用固定 RAW 原点。Official / Stage2 / Base 截面以同一 seed-face ancestry 的物理锚点居中，拓扑与曲率不同，图中偏移不自动代表缺陷。</p>'
for name in ['FINGER_AXIS','CROSS_FINGER_AXIS','DIAGONAL_TANGENT']:body+=img('sections/'+name+'.png',name)
body+='<h2>5 · Normals / grazing / silhouette</h2><p>无 sharp edges、无 custom split normals、无 normals modifier。下面的 normal arrows 是显示副本的计算结果，不是写入生产 normals。</p><div class="grid">'
for kind in ['FACE_NORMALS','VERTEX_NORMALS','GRAZING','SILHOUETTE']:body+=img(render('CURRENT_R2_RAW',kind),kind)
body+='</div>'+img('sections/ROI_BOUNDARY_PROJECTION.png','ROI 边界投影','此图是局部 patch 边界位移，不是整手 silhouette 偏差阈值。')
body+='<h2>6 · 第二观察角 · 同相机普通实体</h2><div class="grid">'
for state in ['CURRENT_R2_RAW','CURRENT_R2_ZERO','IDX_MCP_30']:body+=img(render(state,'SMOOTH','SECOND_ANGLE'),state)
body+='</div><details><summary>第二角度 flat / wire / normals / grazing / silhouette</summary><div class="grid">'
for kind in ['SOURCE_NATIVE','WIRE','FACE_NORMALS','VERTEX_NORMALS','GRAZING','SILHOUETTE']:body+=img(render('IDX_MCP_30',kind,'SECOND_ANGLE'),kind)
body+='</div></details><h2>7 · OFFICIAL_L1 / CURRENT_RAW / CURRENT_POSED</h2><p>相同相机和 scale。Official 用先前 exact ancestry audit 的固定 rigid registration（RMS 0.895 mm），保留 donor native topology。没有 nearest projection。</p><div class="grid">'
for state in ['OFFICIAL_L1','CURRENT_R2_RAW','IDX_MCP_30']:body+=img(render(state),state)
body+='</div><details open><summary>最早 lineage 候选与 donor-transfer 前后</summary><div class="grid">'
for state in ['STAGE2_L1','STAGE4A_R2_BASE','STAGE4A_R2','STAGE4B_RSSF','PRE_DONOR_STAGE4C_RAW','NEW_STAGE4C_RAW']:body+=img(render(state),state)
body+='</div></details><h2>8 · 三个 poses 与 current9 forensic 空间关系</h2><p>候选 ROI 对 current9：direct overlap 0，1/2-ring overlap 0。IDX 仅有同 driver support；TH_IP 对 ROI 无驱动。彩色面仅是当前 named pairs 的位置，未重新裁决 pair。</p><div class="grid">'
for state in CASES:body+=img(render(state,'FORENSIC'),state+' · current9 locations')
body+='</div><p>某些 crossing 位于另一面或被遮挡；以下保留原 pair plain/locator 证据链接以核对 C1–C6 / A1 / B1–B2。</p><ul>'
for p in G['all_current9']:
 rel='../../production_spec/stage6_deformation/current_full_stage6a_crossing_human_adjudication_prep_r1/renders/'+p['pair_id']+'__'+p['case_id']+'__PRODUCT_LOCATION.png'
 body+='<li><a href="'+rel+'">'+p['pair_id']+' '+p['case_id']+' '+str(p['face_ids'])+'</a></li>'
body+='</ul><h2>9 · 当前可以回答什么</h2><p>候选折面在 RAW 中已有，不能由 normal-only 解释。ZERO 未引入候选折面。IDX 有局部蒙皮变形，TH_IP 无候选驱动。现有矩阵和 weights 能复现 saved pose，不能由此认定 rig 或 skin failure。候选与 current9 没有直接/邻域 overlap。</p><p>原始 Human 目标仍未匹配，ROOT_CAUSE_CLASS = UNRESOLVED，NEXT 只记录为 PALMAR_DIGIT_ROOT_EVIDENCE_EXPANSION_R1，不执行。</p><h2>10 · Human review 的五个判断</h2><ol><li>橙色选区是否就是你指出的区域？来自哪个 case / image？</li><li>RAW 与 POSED 是否都有你认为不自然的真实折面？</li><li>FLAT / SMOOTH 差异是否只是可见程度，还是你指的另一种 shading 问题？</li><li>它是否与列出的 pair 位置一致？本轮证据未证明 causal linkage。</li><li>作为半真实教学手，正常旋转/近景下保留这种表面是否明显不可接受？</li></ol><p>无 repair approval、无 product PASS、无 current9 closure。此页面仅供诊断 review。</p><details><summary>完整 machine 字段（Human target 与 candidate 分开）</summary><pre>'+html.escape(json.dumps(status,ensure_ascii=False,indent=2))+'</pre></details>'
page='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Palmar root diagnosis R1</title><style>body{font:16px/1.65 system-ui,sans-serif;color:#1d2834;background:#f6f7f9;max-width:1500px;margin:auto;padding:24px}h1{font-size:28px}h2{margin-top:36px}.hold{padding:14px;background:#ffeed0;border-left:5px solid #d79520}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}figure{margin:10px 0;background:white;border:1px solid #d9dfe6;padding:10px}img{width:100%;display:block}figcaption{padding-top:8px;font-size:14px}pre{white-space:pre-wrap;overflow-wrap:anywhere}details{margin:20px 0}a{color:#2757a0}@media(max-width:900px){.grid{grid-template-columns:1fr}}@media print{details{display:block}.grid{grid-template-columns:repeat(3,1fr)}h2{break-before:auto}}</style><body>'+body+'</body></html>'
(OUT/'PALMAR_DIGIT_ROOT_SURFACE_IRREGULARITY_HUMAN_REVIEW_R1.html').write_text(page,encoding='utf-8')
report=f'''# {PHASE}

结果：**UNRESOLVED — STOP — HUMAN REVIEW**。Human 原截图未包含在本次附件中，不能唯一匹配 case / pose / ROI。已完成可复查的候选区域诊断，不把候选结论冒充 Human 实际目标结论。

## 七个问题的证据回答

1. 候选普通实体中的三角折面包含实际 native geometry ridge / crease。RAW、flat / source-native、wire 和真实截面均保留几何折线。Smooth calculated normals 会改变可见度；无 custom split normals 或 sharp edges，不能把它简单归结为 normal-only artifact。自然低模 faceting 与不可接受局部 fold 的产品判断仍由 Human 完成。
2. 候选在 RAW 已有，ZERO 未引入新缺陷。ROI RAW→ZERO 最大坐标差 {lineage['RAW_ZERO_max_delta_mm']:.8f} mm，属于本项目 saved evaluated float 差异。生产资产没有变更。
3. 当前 IDX_MCP_15 / IDX_MCP_30 对候选局部有变化，TH_IP_15 无 driver support。没有证据说 Stage6 pose 引入整个候选折面。IDX30 最大位移 1.78755 mm、edge ratio 范围 0.96648–1.10080、总面积比 1.00184；中央値接近 ZERO numerical noise，不能用单个最大值推断整体 pinch。
4. 从冻结 rest matrices、既有 weights 和保存角度进行纯代数 LBS reconstruction，ROI 最大误差分别约 0.000063 / 0.000060 / 0.000030 mm。这解释 limited IDX deformation 的机制，不证明权重失败或关节变换错误。基线 geometry / 着色可见度是主要候选因素，Human 目标归因仍未解决。
5. current9 在候选 ROI 中 face / vertex direct overlap = 0，1/2-ring neighborhood overlap = 0。IDX 三对是 SAME_DRIVER_ONLY，TH_IP 六对是 NO_MEANINGFUL_OVERLAP。空间近邻不等于因果关系；本轮未重新裁决 pairs。Human 目标的 overlap 仍为 UNRESOLVED。
6. Source official L1 / Stage2 L1 已有粗 root crease；工程 root band 在 cached Stage4A_R2_BASE 可见，Stage4B_RSSF 的 native adjacent-face dihedral 更强。例 edge2810 / faces1840,2954：Stage4A_R2 0.6666° → current RAW 11.5220°。同 topology、exact coordinate ancestry / oriented face cycles 可恢复（本 ROI missing native faces = {len(missing)}）。Donor transfer 在 ROI 外围两个顶点3306/3314有移动，不能宣称整个 ROI 与 pre-donor 相同；它未改变所列 interior angle witnesses。最早具体 operation 未新增 replay，不作超出 snapshot 证据的宣称。
7. 若 Human 确认此候选且认为不能接受，最小层次首先是局部 base geometry continuity 与显示着色设计；normal-only 足够性未证明，当前数据未支持直接改 weights / rig。这里只记录建议，不执行 NEXT / repair。

## 匹配、方法与限制

- MATCHED_CASE / MATCHED_POSE = null，MATCH_CONFIDENCE = UNRESOLVED_NO_SCREENSHOT。候选主要视图 IDX_MCP_30__LOCAL_ALTERNATE，原图尺寸1600×1100。三个 case 的 PRIMARY / ALTERNATE 原始视图均已保存到 candidate_source_views。
- ROI 由已实际检查图片中的矩形像素选区 + 最近正射线 native-face hit 定位，{len(roi['vertices'])} vertices / {len(roi['visible_hit_faces'])} faces。不是 anatomy authority。每个 hit 记录 face、barycentric 和世界坐标。
- Saved RAW / ZERO / three poses / historical comparator 均复用，没有 pose setter、Full42 rerun 或微 probe。三条截面使用 Blender native loop triangulation。Source 截面用 exact ancestry seed 锚点；source display fixed rigid fit RMS0.895mm，只用于可视对照，不把 offset 当 defect。
- SOURCE_NATIVE 所有3414 faces都是 flat flags；原 review 显示副本所有 faces smooth。这一既有区别是显示语义差异，不是本轮资产漂移。当前与 pre-donor 的 smooth / sharp / custom normal payload 一致，Blender5.1实际 readback 已记录。
- 顶点/face最大角或 flat画面不直接构成人体阈值。本轮没有构造 anatomical threshold、没有 product PASS、没有将审美判断替换为 machine 判断。

## 冻结与当前 Human response

已填写 response 来源：`{RESPONSE}`，不在工作区内。前后 SHA-256 `{after['sha256']}`，字节完整保留。3 case / 9 pair / YES 与用户交接一致。**HOLD_NOT_CLOSED**；未复制为 active acceptance authority，未创建 approval receipt 或 Human closure。

FULL42_RERUN=0；DIAGNOSTIC_ONLY_MICRO_POSE_PROBE_COUNT=0；GEOMETRY_WRITES=0；WEIGHT_WRITES=0；NORMAL_WRITES=0；RIG_WRITES=0；JOINT_WRITES=0；MATERIAL_WRITES=0；MODIFIER_WRITES=0；STAGE6B_RUNS=0；PRODUCTION_PROMOTION=NO。这些计数指 qualified assets；render display copies 创建不同着色/overlay是本轮获准诊断可视化。

最终全字段和候选字段分开保存在 `{PHASE}_STATUS.json`。Human target ROOT_CAUSE_CLASS=UNRESOLVED。NEXT=PALMAR_DIGIT_ROOT_EVIDENCE_EXPANSION_R1（只记录、不执行）。STOP — HUMAN REVIEW。
'''
(OUT/(PHASE+'_REPORT.md')).write_text(report,encoding='utf-8')
print('Delivered report / status / review with explicit unresolved Human target',flush=True)
