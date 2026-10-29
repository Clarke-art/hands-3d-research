"""Finish read-only provenance and fail-closed reconciliation records. No solvers imported."""
import json,hashlib,sys,math
from pathlib import Path
from collections import Counter
import numpy as np
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[2];S5=OUT.parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canon(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def dump(n,x):(OUT/n).write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
A=read(OUT/'AUTHORITY_INPUT_VERIFICATION.json');J=read(OUT/'READ_ONLY_LIVE_EXTRACTION.json');B=J['CORRECTED']['bones'];V=np.array(J['RSSF']['vertices_world_m']);E=J['RSSF']['edges'];F=J['RSSF']['faces'];M=read(OUT/'STATIC_RECONCILIATION_MEASUREMENTS.json');T=read(OUT/'CORRECTED_THUMB_TUBE_ANCHOR_CANDIDATE_AUDIT.json');C=read(OUT/'CORRECTED_LIVE_THUMB_CHAIN_R1.json')
native=read(ROOT/A['sources']['native_partition_evidence']['path']);labels=native['labels']
P='production_spec/'
R3=P+'stage6_deformation/stage6b_r3_thumb_tip_ownership_boundary/scripts/r3_ownership.py'
R2=P+'stage6_deformation/stage6b_r1b/scripts/s6br1b_common.py'
BASE=P+'stage5_production_rig/stage5b_r1a/scripts/r1a_common.py'
sections=[
 (R3,117,163,'live chain and arc; corrected source replaces R2A'),(R3,165,220,'radii/nails/tube/corridor/web and post-hoc conflict masking'),(R3,228,246,'historical R2 and graph domain'),(R3,249,280,'geodesic units and capacity constants'),(R3,350,414,'unary capacities and closure convergence'),(R3,435,444,'old-label initialization'),(R3,554,564,'distal exclusion domain'),(R3,660,720,'tip/sheet and CLASS_A historic label gate'),
 (R2,140,216,'R2 graph seed override and partition semantics; source read only, never executed'),(R2,263,323,'R2 correction domain and historical own_r1a fallback'),(BASE,136,203,'stale AC versus live BHBT; ownership reference provenance'),(BASE,407,483,'nail/ownership/web/thenar wrappers'),
 (P+'stage5_production_rig/stage5b_r1d/scripts/s5b_r1d_build.py',247,255,'thumb radius contaminated CORR sampling domain'),(P+'stage6_deformation/stage6b/scripts/s6b_common.py',92,132,'CMC sphere filtered by own_r1a'),(P+'stage5_production_rig/stage5b_r1e/scripts/s5b_r1e_build.py',288,303,'later cage wrapper filtered by R3'),
 (P+'stage5_production_rig/stage5b_r1e_thumb_distal_cap_native_branch_identity_audit_r1/scripts/investigate_native.py',1,140,'independent native partition construction provenance, not executed'),(P+'stage5_production_rig/stage5b_r1e_thumb_distal_cap_native_branch_identity_audit_r1/scripts/analyze_identity.py',80,110,'native cap9 branch evidence and web limitation; selector not executed'),
 (P+'stage4_blender/scripts/stage4a_r2_cage.py',465,481,'cage builder moves boundary neighbours; initial boundary coordinate table may differ from saved cage'),(P+'stage4_blender/scripts/stage4a_r2_cage.py',525,530,'final new cage vertex coordinates snapshot'),(P+'stage4_blender/scripts/stage4a_r2_cage.py',616,623,'initial boundary versus final new vertex coordinate outputs')]
evidence=[]
for path,start,end,role in sections:
 p=ROOT/path;lines=p.read_text(encoding='utf-8-sig').splitlines();evidence.append({'path':path,'sha256':sha(p),'lines':[start,end],'role':role,'source_excerpt':'\n'.join(f'{i+1}: {lines[i]}' for i in range(start-1,min(end,len(lines))))})
dump('SOURCE_CODE_PROVENANCE_R1.json',evidence)
# Stale numbers are read only into a historical record. They never enter a candidate computation.
stalePath=ROOT/'production_spec/stage4_blender/stage4c_r2/STAGE4B_R2_JOINT_FRAME.json';stale=read(stalePath)['bones']
chainnames={d:[d+'_'+s+'_R' for s in (['CMC','MCP','IP'] if d=='THUMB' else ['MCP','PIP','DIP'])] for d in ['THUMB','INDEX','MIDDLE','RING','LITTLE']}
originPath=ROOT/'production_spec/stage4_blender/stage4c_r2/ORIGIN_AUDIT_R2.json';origin=read(originPath)
historicalAC={d:[stale[n]['head'] for n in ns]+[stale[ns[-1]]['tail']] for d,ns in chainnames.items()};historicalAC['wrist']=[origin['WRIST_ORIGIN'],stale['WRIST_R']['tail']]
oldRawPath=S5/'cap_derived_thumb_kinematic_authority_revalidation_r1/RAW_READ_ONLY_GEOMETRY_AND_BONES.json';oldRaw=read(oldRawPath);oldB=oldRaw['R2A']['bones'];oldC=np.array([oldB[n]['head_world_m'] for n in chainnames['THUMB']]+[oldB['THUMB_IP_R']['tail_world_m']])
def project(C):
 dd=np.full(len(V),np.inf);ss=np.zeros(len(V));base=0.;knots=[0.]
 for a,b in zip(C[:-1],C[1:]):
  ab=b-a;length=np.linalg.norm(ab);t=np.clip((V-a)@ab/(length*length),0,1);d=np.linalg.norm(V-(a+t[:,None]*ab),axis=1)*1000;sel=d<dd;dd[sel]=d[sel];ss[sel]=base+t[sel]*length*1000;base+=length*1000;knots.append(base)
 return ss,dd,knots
os,od,ok=project(oldC);oldTube={i for i in range(len(V)) if od[i]<=10.4735 and os[i]>=ok[1]};oldCorr={i for i in range(len(V)) if od[i]<=.85*10.4735 and .30*ok[1]<=os[i]<ok[1]}
def pack(s):
 s=sorted(set(s));return {'count':len(s),'vertex_ids':s,'set_sha256':canon(s),'native_counts':dict(Counter(labels[i] for i in s))}
def difference(a,b):return {'old_count':len(a),'candidate_count':len(b),'removed':sorted(set(a)-set(b)),'added':sorted(set(b)-set(a))}
legacy={'historical_only':True,'forbidden_as_current_truth':True,'source':{'path':str(stalePath.relative_to(ROOT)),'sha256':sha(stalePath)},'old_AC_world_m':historicalAC,'old_reference_axis_vectors_m':{d:(np.array(p[-1])-np.array(p[0])).tolist() for d,p in historicalAC.items()},'old_origin_reference':{'path':str(originPath.relative_to(ROOT)),'sha256':sha(originPath),'world_m':origin['WRIST_ORIGIN']},'old_live_chain_world_m':oldC.tolist(),'old_live_chain_source':{'path':oldRaw['R2A']['path'],'sha256':oldRaw['R2A']['sha256'],'archival_read_only_extraction_path':str(oldRawPath.relative_to(ROOT)),'extraction_sha256':sha(oldRawPath)},'current_replacement':'CORRECTED_LIVE_THUMB_CHAIN_R1.json from saved corrected rig; no stale numeric result used in candidate pipeline','old_AC_cap_direct_dependency':False,'old_AC_status':'STALE_GEOMETRY_FRAME; not old REP but not current production geometry authority','old_live_chain_cap_dependency':'YES: IP.tail/TIP.head inherited cap-derived REP','origin_policy':'KEEP corrected rig origin/hierarchy verified by correction record; old frame is listed only for provenance','old_default_seed':'cap9 mean -> nearestvertex1076, separate from AC chain default','old_tube_predicate_only':pack(oldTube),'old_corridor_predicate_only':pack(oldCorr),'execution_scope':'STATIC historical predicate replay only. No cap selection, partition, strong union, graph solve, closure or boundary generation.'}
dump('HISTORICAL_REFERENCE_INPUT_PROVENANCE_R1.json',legacy)
diff=read(OUT/'R2_R3_INPUT_DIFF_PREVIEW.json');diff['chain']['old_polyline_world_m']=oldC.tolist();diff['chain']['endpoint_displacements_mm']=[float(np.linalg.norm(a-b)*1000) for a,b in zip(oldC,np.array(C['polyline_world_m']))];diff['thumb_tube_oldchain_vs_corrected_chain_fixed_oldradius']=difference(oldTube,T['sets']['historical_radius_corrected_chain_raw_tube']['vertex_ids']);diff['thumb_corridor_oldchain_vs_corrected_chain_fixed_oldradius']=difference(oldCorr,T['sets']['historical_radius_corrected_chain_raw_corridor']['vertex_ids']);diff['thumb_tube_calibration_candidates']=T['radius_sampling_sensitivity'];dump('R2_R3_INPUT_DIFF_PREVIEW.json',diff)
cage=read(OUT/'CMC_CAGE_R3_WRAPPER_RECONCILIATION_R1.json');cage['construction_coordinate_candidate']=cage.pop('exact_topological_cage_candidate');cage['mapping_caveat']+=' Initial boundary coordinates precede smoothing of pole neighbours (builder465-481/620); final new57 coordinates are saved after smoothing. Nearest matches are candidates, not asserted exact IDs when tolerance fails.';cid=set(cage['construction_coordinate_candidate']['vertex_ids']);cage['candidate_faces_fully_inside_count']=sum(set(f)<=cid for f in F);cage['final57_coordinate_max_error_mm']=max(x['native_match_error_mm'] for x in cage['mapping_records'][16:]);cage['boundary16_coordinate_max_error_mm']=max(x['native_match_error_mm'] for x in cage['mapping_records'][:16]);dump('CMC_CAGE_R3_WRAPPER_RECONCILIATION_R1.json',cage)
# Set/source hash manifest is an audit package, deliberately NOT a recompute contract.
statusInputs={'corrected_live_thumb_chain':'RESOLVED','R2_seed':'RESOLVED','R2_domain_guard':'UNRESOLVED','thumb_tube_anchors':'UNRESOLVED','thumb_strong_anchor_sources':'UNRESOLVED','index_strong_anchor_sources':'RESOLVED','first_web_wrapper':'UNRESOLVED','nail_cap_wrapper':'RESOLVED','CMC_cage_wrapper':'UNRESOLVED','R3_unary_field_input':'UNRESOLVED','R3_graph_domain':'UNRESOLVED','closure_input_semantics':'RESOLVED','validator_reuse':'PARTIAL'}
blockers=[
 {'id':'PROXIMAL_NATIVE_DOMAIN_AND_RADIUS','affects':['R2 domain guard','thumb tube radius sampling','metacarpal corridor','thumb strong sources','R3 graph domain'],'evidence':'Native source explicitly limits whole-palm Voronoi authority. Full116 versus stable102 calibration vertices yields radius10.299381 versus10.180583mm, tube164 versus155 and corridor5 versus4.','needed_decision':'Approve a bounded native/canonical proximal domain and radius-sampling rule. Use current candidates as comparison; do not choose by matching historical R3.','source_files':['R2_DOMAIN_INPUT_RULE_R1.json','CORRECTED_THUMB_TUBE_ANCHOR_CANDIDATE_AUDIT.json','R3_GRAPH_DOMAIN_INPUT_RECONCILIATION.json']},
 {'id':'FIRST_WEB_ROLE','affects':['first-web wrapper','thumb strong sources','R3 graph domain'],'evidence':'Frozen21 web region has independent native evidence thumb5/index10/wrist6; approval is geometry/weight locality, not proof of categorical THUMB pins.','needed_decision':'Preserve all21 geometry; separately establish whether any subset has independent THUMB hard-pin authority or whether web is protected shared graph support only. Native Voronoi alone cannot decide.','source_files':['FIRST_WEB_WRAPPER_RECONCILIATION_R1.json']},
 {'id':'CMC_THENAR_PROTECTION_SUPPORT','affects':['CMC cage wrapper','graph/validation protection'],'evidence':'R3 only logs CMC_CAGE; legacy protection uses native-centre sphere filtered by old ownership. 73-vertex topological cage construction and broader deformation patch are different scopes. Initial boundary coordinates precede smoothing.','needed_decision':'Define independent immutable protection membership/role without R3 label filters. Keep approved cage geometry frozen; no geometry review or rebuild.','source_files':['CMC_CAGE_R3_WRAPPER_RECONCILIATION_R1.json']},
 {'id':'UNARY_PAIRWISE_UNITS','affects':['R3 unary field input','validator/numeric reuse'],'evidence':'Geodesic d is metres; TAU is millimetres. Executed unary round(d_m*1000) versus pairwise round(TAU_mm/3*1000) differs by1000 from common mm-cost semantics described in report.','needed_decision':'Resolve intended numerical energy unit/ratio explicitly before constructing canonical input contract. Suggested correction is common mm costs, but no methodology change is applied this round.','source_files':['R3_UNARY_FIELD_INPUT_CONTRACT_R1.json','SOURCE_CODE_PROVENANCE_R1.json']}
]
dump('UNRESOLVED_INPUT_AUTHORITY_REVIEW_R1.json',{'status':'FAIL_CLOSED','blockers':blockers,'R3_RECOMPUTE_ALLOWED':False,'scope':'Narrow input-role/domain/numeric decisions only, not rig/geometry/skin or per-vertex whole-hand approval.','not_ready_for_contract_approval':True})
nextStep='NARROW_PROXIMAL_DOMAIN_WRAPPERS_AND_UNARY_UNITS_AUTHORITY_REVIEW'
zero={'R2_runs':0,'R3_runs':0,'skin_rebuild_count':0,'Stage6_runs':0,'BLEND_FILES_WRITTEN':0,'WEIGHT_DELTA':0,'GEOMETRY_DELTA':0,'TOPOLOGY_DELTA':0,'BONE_DELTA':0,'JOINT_DELTA':0,'R1F_CREATED':False,'R3_mincut_runs':0,'R3_closure_runs':0,'R3_boundary_generation_runs':0,'cap_selector_runs':0}
status={'task':'CAP_DERIVED_R2_R3_INPUT_RECONCILIATION_R1','status':'FAIL_CLOSED_UNRESOLVED_INPUT_AUTHORITY','inputs':statusInputs,'old_cap9_can_reenter_THUMB_strong':False,'old_cap9_answer_scope':'NO under mandatory proposed independent digit guard; corrected raw historical tube also selects none of oldcap9, but41 other nativeINDEX vertices show why guard remains mandatory. No final contract or final strong set exists.','old_R2_R3_labels_used_as_truth':False,'new_input_contract_generated':False,'combined_input_contract_hash':None,'Human_Review_required':True,'Human_review_type':'NARROW_INPUT_AUTHORITY_REVIEW, not permission to recompute','R3_FULL_RECOMPUTE_REQUIRED':True,'R3_RECOMPUTE_ALLOWED':False,'resolved_does_not_mean_Human_approved_contract':True,'unresolved_input_ids':[x['id'] for x in blockers],**zero,'NEXT':nextStep,'STOP':True}
dump('CAP_DERIVED_R2_R3_INPUT_RECONCILIATION_R1_STATUS.json',status)
report=f'''# CAP_DERIVED_R2_R3_INPUT_RECONCILIATION_R1

状态：**FAIL_CLOSED_UNRESOLVED_INPUT_AUTHORITY**。已完成只读 provenance、候选静态测量与输入差异审计；没有生成 canonical recompute contract，也不能进入 R3。

## 正式输入已验证

- cap37：HUMAN_APPROVED_FROZEN，37 vertices /25 faces，combined authority hash `{A['cap_combined_authority_hash']}`。
- corrected rig：HUMAN_APPROVED / APPLIED_VERIFIED，SHA256 `{A['sources']['corrected_rig']['sha256']}`。直接读取 live21 bones；IP head、hierarchy/origin 等保持已批准状态。THUMB_IP.tail/TIP.head 来自 corrected rig。
- Stage4C_R2：SHA256 `{A['sources']['Stage4C_geometry']['sha256']}`。corrected rig mesh 与 RSSF 的顶点/边/面完全一致；native→RSSF 顶点编号、边及 polygon 顺序完全一致。未选择或更改 cap、nail、first-web、cage geometry。
- 各 authority 文件及源码行号/摘录见 AUTHORITY_INPUT_VERIFICATION.json、SOURCE_CODE_PROVENANCE_R1.json；集合与文件哈希见 RECONCILIATION_EVIDENCE_HASH_MANIFEST_R1.json。该 manifest 是审计包，不是 input contract。

## 结果

| Input | Status |
|---|---|
'''+''.join(f'| {k} | {v} |\n' for k,v in statusInputs.items())+f'''
RESOLVED 仅表示该输入定义有唯一可追溯候选；不代表整份 contract 获批。

## Live chain 和 seed

distance/arc/tube 使用 CMC.head→MCP.head→IP.head→IP.tail (=TIP.head)。TIP.tail 是 non-deform helper 的外延，不延长解剖 tube；roll 存档但距离公式不使用 roll。未来 dT/dI 是 graph edge-geodesic 距离到 hard-source regions，不是 Euclidean chain distance。

历史 R2 seed 实际执行 `nearestvertex(mean(oldcap9))`，得到 **v1076（native INDEX）**。它不是直接读取 REP，也不是报告声称的单纯 chain terminal seed。必须 RETIRE。

候选比较：cap37 centroid 最近顶点与 cap37 induced-graph geodesic medoid 都是 **v1752**；独立 terminal landmark 是 **v284**。选择 v284 是因为 R2 初始化需要 terminal surface graph source，且 native identity、cap37 membership 与 corrected terminal kinematics 相互支持；不是把 cap centroid 当端点。JSON 记录各 XYZ、delta、native→RSSF映射及 medoid全部得分。没有运行六源 partition。

旧 AC 数值仅存入 HISTORICAL_REFERENCE_INPUT_PROVENANCE_R1.json，明确为 HISTORICAL_ONLY。它们未参与当前候选计算，future AC 由 corrected live rig替换。

## Anchor 静态检查

- 旧 THUMB_STRONG241：native THUMB169 / INDEX66 / wrist6；旧 INDEX_STRONG145 全部 native INDEX。历史集合只作差异证据。
- corrected chain +历史10.4735mm radius：raw tube219；旧cap9进入数0。不能因这9点不再进入而删除guard。
- native THUMB band重新测得10.299381mm：raw tube205，其中41个native INDEX；guard后164，metacarpal corridor5。cap37全部在该tube中，语义保留cap/tube双来源、future去重，不累计两份硬约束。
- radius采样仍包含14个native proximal interface点。去掉这些点得到10.180583mm、tube155、corridor4；变化9个tube点与1个corridor点。两种规则都确定性但authority未唯一，故thumb tube输入不能写RESOLVED。
- INDEX radius独立采样67点，全部两环稳定，8.057679980mm；INDEX tube143，nail43保持正式face mask。旧loader竞争过污染的thumb chain，因此是REVALIDATE后确认ingredients，不是机械保留历史145标签。
- 所有 geometry-only hard-pin routes 都必须先经过 independent digit guard；nativeINDEX不能仅凭thumb proximity入强锚。跨digit冲突必须在union前FAIL_CLOSED，禁止沿用先 `THUMB_STRONG -= INDEX_STRONG` 再声称零冲突。
- 未生成任何最终新THUMB_STRONG/INDEX_STRONG union。

## 四项窄范围 authority 阻塞

1. **Proximal domain/radius/graph**：native partition文件明确说明掌部Voronoi界面只是结构候选。旧graph1008依赖旧R2与anchors，不能复用。native THUMB∪INDEX953、再纳入frozenweb959只是候选；不能擅自将任一集合升级为解剖truth。必须先明确shared proximal/wrist域及采样规则。
2. **FIRST_WEB角色**：21点membership保留。既有批准明确weights locality，不能证明全部21点都应THUMB hard-pin。native evidence为THUMB5/INDEX10/wrist6，不能反过来把这个Voronoi分类当最终web truth。建议保留几何/validator保护，单独裁决shared graph及anchor角色。
3. **CMC/thenar wrapper**：cage geometry保持PASS/FROZEN。R3脚本仅记录CMC_CAGE；其旧selector及后续保护用了旧ownership或R3过滤。73点construction候选与较大的sphere/thenar保护支持域语义不同。冻结表的16个boundary坐标在pole-neighbour smoothing前，最大映射误差0.700591mm，因此没有把最近匹配自动宣布为精确authority。需要label-independent protection支持域，不能重开cage几何。
4. **Unary/pairwise单位**：dT/dI图边按米累计，TAU按毫米提取，二者容量都乘1000。10mm距离在旧代码unary容量为10，而统一mm成本为10000；pairwise约1296。执行比例与报告写出的共同mm成本不一致，差1000倍。已记录两个语义，未静默选择或修改算法。

## Closure 与 gates

closure只能接受新solved labels、新graph、新anchors：**NO HISTORICAL LABEL INJECTION**。禁止 `R3=list(oldR2)` 作为域外truth。旧closure将changed在每个target内复位，future应使用完整sweep累计变化、检测未收敛；本轮没有执行closure。

connectedness、face-component、sheet split、island、ambiguity等数学检查可保留，但输入与保护bucket必须替换。CLASS_A6条边的几何authority保留，future在corrected结果上重新验证；旧THUMB标签不作为要求复刻的目标。sheet归属要以独立INDEX tip/nail识别，不以“第二大component”或旧label决定。validator reuse=PARTIAL。

## 冻结与执行范围

本轮仅写入本目录。FROZEN_HASH_VERIFICATION_R1.json记录1633个既有workspace文件与6个外部authority/Human文件before==after。所有既有blend、Human responses、Stage4/5、historical R2/R3、Stage6保持原hash。各delta与run counts均为0。

仅cap37的固定membership内做了候选medoid距离；仅对冻结geometry做静态chain/tube测量。没有R2 ownership solve、R3 unary full field、mincut、closure、boundary generation、skin rebuild、Stage6或R1F。

CANONICAL_R2_R3_RECONCILED_INPUT_CONTRACT_R1.json **未生成**。combined contract hash = null。未生成READY_FOR_R3的Human approval页面。UNRESOLVED_INPUT_AUTHORITY_REVIEW_R1.json提供四个窄范围决定及依赖证据。

NEXT = **{nextStep}**

STOP。不得跳过未解决输入进入R3。
'''
(OUT/'CAP_DERIVED_R2_R3_INPUT_RECONCILIATION_R1_REPORT.md').write_text(report,encoding='utf-8')
# Add dependency sources to each required audit without duplicating excerpts.
for p in OUT.glob('*.json'):
 if p.name in ['FROZEN_HASHES_BEFORE.json','READ_ONLY_LIVE_EXTRACTION.json','SOURCE_CODE_PROVENANCE_R1.json','AUTHORITY_INPUT_VERIFICATION.json'] or 'MANIFEST' in p.name:continue
 d=read(p)
 if isinstance(d,dict):
  d['provenance_index']='SOURCE_CODE_PROVENANCE_R1.json';d['authority_source_index']='AUTHORITY_INPUT_VERIFICATION.json';dump(p.name,d)
print('Documentation complete, FAIL_CLOSED; no canonical contract.')
