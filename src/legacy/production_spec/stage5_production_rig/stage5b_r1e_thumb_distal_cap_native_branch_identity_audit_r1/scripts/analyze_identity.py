"""Native identity and historical selector provenance only; no deformation or weights."""
import sys
sys.dont_write_bytecode=True
import json,heapq,hashlib,datetime
from pathlib import Path
from collections import Counter
import numpy as np

out=Path(__file__).resolve().parents[1];root=out.parents[2];s5=out.parent
def load(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(name,data):(out/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
states=load(out/'_tmp/static_mesh_states.json');native=states['NATIVE'];V=np.array(native['vertices_world_m']);F=native['faces'];E=native['edges'];N=len(V)
part=load(out/'_tmp/native_independent_partition.json');label=part['labels'];tip=part['tip_seeds'];nail=load(root/'production_spec/stage4_blender/stage4c_r2/NAIL_AUDIT_R2.json')['per_digit_faces']
capaudit=load(s5/'stage5a_r2a/THUMB_DISTAL_CAP_AUDIT.json');CAP=capaudit['thumb_cap_vertex_ids'];CF=capaudit['thumb_cap_face_ids'];selector=load(out/'_tmp/selector_reproduction.json')
human_source=s5/'stage5b_r1e_human_authority_and_v2192_cap_reaudit_r1/HUMAN_MANUAL_REGISTRATION_RESPONSES_R1.json';human=load(human_source)
assert human['questions']=={'Q1':'YES','Q2':'UNRESOLVED','Q3':'UNDECIDED','Q4':'NO','Q5':'LIMITED'}
before=load(out/'FROZEN_HASHES_BEFORE.json');assert all(sha(root/k)==h for k,h in before.items())
adj=[[] for _ in V];incident=[[] for _ in V];edgefaces={};fadj=[set() for _ in F]
for a,b in E:
    length=float(np.linalg.norm(V[a]-V[b])*1000);adj[a].append((b,length));adj[b].append((a,length))
for fi,vs in enumerate(F):
    for a in vs:incident[a].append(fi)
    for a,b in zip(vs,vs[1:]+vs[:1]):edgefaces.setdefault(tuple(sorted([a,b])),[]).append(fi)
for fs in edgefaces.values():
    for a in fs:fadj[a].update(set(fs)-{a})
def dij(seeds,domain=None):
    dist=np.full(N,np.inf);pred={};q=[]
    for a in sorted(seeds):dist[a]=0.;heapq.heappush(q,(0.,a))
    while q:
        cost,a=heapq.heappop(q)
        if cost>dist[a]+1e-12:continue
        for b,l in adj[a]:
            if domain is not None and b not in domain:continue
            nc=cost+l
            if nc<dist[b]-1e-12:dist[b]=nc;pred[b]=a;heapq.heappush(q,(nc,b))
    return dist,pred
def path_record(start,result,anchors):
    ds,pred=result;seq=[start]
    while seq[-1] in pred:seq.append(pred[seq[-1]])
    assert seq[-1] in anchors
    assert abs(sum(np.linalg.norm(V[a]-V[b])*1000 for a,b in zip(seq,seq[1:]))-ds[start])<1e-8
    return {'distance_mm':float(ds[start]),'endpoint_anchor':seq[-1],'vertex_ids':seq,'reverse_anchor_to_vertex_ids':seq[::-1],'native_branch_sequence':[label[i] for i in seq]}
def ring(a):return {b for b,l in adj[a]}
def rings(a):
    one=ring(a);two={j for b in one for j,l in adj[b]}-one-{a}
    return sorted(one),sorted(two)
def unit(v):return v/np.linalg.norm(v)
tip_dist={n:dij([i])[0] for n,i in tip.items()}
indexids={i for i,n in enumerate(label) if n=='index'};thumbids={i for i,n in enumerate(label) if n=='thumb'}
fore_idx=int(np.argmin(np.linalg.norm(V-np.array([1.4048,.0113282045,.275691007]),axis=1)))
def native_axis_joints(nm):
    domain={i for i,n in enumerate(label) if n==nm};tipv=tip[nm]
    if nm=='thumb':
        axis=np.array(part['thumb_axis']);anchor=np.array(part['thumb_axis_anchor']);length=part['thumb_length_m'];fracs={'MCP':.44,'IP':.75}
    else:
        length=tip_dist[nm][part['notches']['index-middle']]/1000
        band=[i for i in domain if .25*length<=tip_dist[nm][i]/1000<=.55*length]
        axis=unit(V[tipv]-V[band].mean(0));ref=V[part['notches']['index-middle']];anchor=V[tipv]+axis*((ref-V[tipv])@axis);length=float((V[tipv]-anchor)@axis);fracs={'MCP':0.,'PIP':.46,'DIP':.77}
    joints={}
    for name,frac in fracs.items():
        sel=[i for i in domain if abs((V[i]-anchor)@axis-length*frac)<=.003]
        if len(sel)<6:sel=[i for i in domain if abs((V[i]-anchor)@axis-length*frac)<=.009]
        joints[name]=V[sel].mean(0).tolist()
    joints['TIP']=V[tipv].tolist()
    return {'axis':axis.tolist(),'axis_anchor_world_m':anchor.tolist(),'length_m':length,'joint_world_m':joints,'method':'Read-only reconstruction of pre-deformation native centerline/cross-section locator from stage4b_rssf_r2.py; no posed coordinates reused; engineering joint estimates support branch continuity, not photo bone visibility.'}
native_thumb=native_axis_joints('thumb');native_index=native_axis_joints('index')
thumb_nail=sorted({i for fi in nail['thumb'] for i in F[fi]});index_nail=sorted({i for fi in nail['index'] for i in F[fi]})
assert all(label[i]=='thumb' for i in thumb_nail) and all(label[i]=='index' for i in index_nail)
TH=sorted(set(thumb_nail)|{tip['thumb']});IX=sorted(set(index_nail)|{tip['index']})
assert not set(TH)&set(CAP);assert not set(IX)&set(CAP)
WEB=sorted({part['notches']['index-thumb']}|ring(part['notches']['index-thumb']))
def anchors(nm,ids,nail_ids,nail_faces,geo):
    return {'anchor_name':'NATIVE_'+nm.upper()+'_ANCHOR_SET','native_mesh':native['path'],'native_sha256':native['sha256'],'depends_on_CURRENT_CAP_9':False,'depends_on_R3_labels':False,'tip_seed_source':'stage4_blender/scripts/stage4b_rssf_r2.py TIP_SEEDS (native, before cap generation)','tip_vertex_id':tip[nm],'tip_world_m':V[tip[nm]].tolist(),'nail_face_source':'stage4_blender/stage4c_r2/NAIL_AUDIT_R2.json / per_digit_faces; predates R2A cap selector','nail_face_ids':nail_faces,'nail_vertex_ids':nail_ids,'nail_identity_independent_check':'All nail vertices lie in the native continuous branch attached to the visibly separate same-named terminal tip; current contact-pose proximity is not used.','anchor_vertex_ids':ids,'native_continuous_branch_vertex_ids':[i for i,n in enumerate(label) if n==nm],'native_direction_support':geo,'independent_mesh_partition':'Multi-source native surface Dijkstra from 5 unmistakable terminal tips plus wrist, transformed via saved native matrix; no cap or downstream ownership labels input. Local/two-ring, nail and native tube geometry cross-check required for final cap9 classification.','known_limitations':'Whole-palm Voronoi interfaces are structural candidates, not an anatomical shared-skin authority. Cap9 points are well inside index tube, away from those interfaces.'}
dump('NATIVE_THUMB_ANCHOR_SET.json',anchors('thumb',TH,thumb_nail,nail['thumb'],native_thumb))
dump('NATIVE_INDEX_ANCHOR_SET.json',anchors('index',IX,index_nail,nail['index'],native_index))
dump('NATIVE_FIRST_WEB_ANCHOR_SET.json',{'anchor_vertex_ids':WEB,'notch_vertex_id':part['notches']['index-thumb'],'source':'Independent native thumb/index tip-based branch interface, distal-most native cleft candidate plus one-ring','depends_on_CURRENT_CAP_9':False,'depends_on_R3_labels':False,'role':'Structural first-web/cleft proxy for distance provenance; not a new Human surface registration','Human_Q2':'UNRESOLVED','exact_shared_skin_correspondence':'NOT_CLAIMED'})
distT=dij(TH);distI=dij(IX);distW=dij(WEB)

# Independent native candidate: reproduce declared local radius on a native thumb-only graph.
IP=np.array(native_thumb['joint_world_m']['IP']);TIP=np.array(native_thumb['joint_world_m']['TIP']);axis=unit(TIP-IP)
eligible_seeds=[i for i in thumbids if (V[i]-IP)@axis>0];native_seed=max(eligible_seeds,key=lambda i:float(np.linalg.norm(V[i]-IP)))
native_g,native_pred=dij([native_seed],thumbids)
thumbfaces={fi for fi,vs in enumerate(F) if all(i in thumbids for i in vs)}
near=min(thumbfaces,key=lambda fi:float(np.linalg.norm(V[F[fi]].mean(0)-V[native_seed])))
ok={fi for fi in thumbfaces if min(native_g[i] for i in F[fi])<=9.0};ok.add(near)
native_cf=set();stack=[near]
while stack:
    fi=stack.pop()
    if fi in native_cf or fi not in ok:continue
    native_cf.add(fi);stack.extend(fadj[fi]-native_cf)
native_cap=sorted({i for fi in native_cf for i in F[fi]});assert set(native_cap)<=thumbids
candidate={'candidate_name':'NATIVE_THUMB_DISTAL_CAP_CANDIDATE_SET','status':'READ_ONLY_CANDIDATE_PENDING_HUMAN_CAP_AUTHORITY_CORRECTION','independent_of_CURRENT_CAP_9':True,'seed_vertex_id':native_seed,'seed_world_m':V[native_seed].tolist(),'seed_rule':'Farthest native thumb-branch vertex from independently reconstructed native IP, distal of IP along native IP-to-terminal-tip direction','native_thumb_tip_vertex':tip['thumb'],'mesh_state':'NATIVE_PRE_RSSF_STAGE4A_R2','mesh_sha256':native['sha256'],'graph_domain':'Induced edge graph on independently identified native thumb branch; no current cap IDs or R3 labels used','graph_vertex_ids':sorted(thumbids),'radius_mm':9.0,'face_predicate':'Fully native-thumb-branch face with min(vertex geodesic from independent native seed) <= 9 mm, connected to closest seed face','face_ids':sorted(native_cf),'vertex_ids':native_cap,'max_selected_vertex_geodesic_mm':float(max(native_g[i] for i in native_cap)),'face_expansion_warning':'The declared min-vertex face predicate may include corners farther than 9 mm; 9 mm is not an all-vertices hard radius.','production_cap_replaced':False,'not_a_weight_proposal':True}
dump('NATIVE_THUMB_DISTAL_CAP_CANDIDATE_SET.json',candidate)

rows=[];mcp=np.array(native_index['joint_world_m']['MCP']);pip=np.array(native_index['joint_world_m']['PIP']);ia=pip-mcp
for a in CAP:
    one,two=rings(a);local={a}|set(one)|set(two);local_labels=sorted({label[i] for i in local})
    cls='INDEX_SURFACE' if label[a]=='index' and local_labels==['index'] else 'UNRESOLVED'
    if a in native_cap:cls='TRUE_THUMB_DISTAL_CAP'
    row={'vertex_id':a,'classification':cls,'native_branch':label[a].upper(),'classification_confidence':'HIGH_NATIVE_MESH_BRANCH' if cls=='INDEX_SURFACE' else 'UNRESOLVED','native_world_mm':(V[a]*1000).tolist(),'one_ring':one,'two_ring_exact_hop_2':two,'local_branch_labels_including_two_ring':local_labels,'incident_faces':[{'face_id':fi,'vertex_ids':F[fi],'native_vertex_branch_labels':[label[i] for i in F[fi]]} for fi in incident[a]],'native_index_MCP_to_PIP_axial_fraction':float((V[a]-mcp)@ia/(ia@ia)),'thumb_anchor_path':path_record(a,distT,set(TH)),'index_anchor_path':path_record(a,distI,set(IX)),'first_web_proxy_path':path_record(a,distW,set(WEB)),'native_tip_distances_mm':{'thumb':float(tip_dist['thumb'][a]),'index':float(tip_dist['index'][a])},'current_cap_membership_used_as_proof':False,'R3_or_THUMB_STRONG_used_as_proof':False,'current_RSSF_proximity_used_as_proof':False,'reason':'Native index tube continuity, entirely index one/two-ring and incident-face neighborhood, independent index-nail/terminal-tip connections, native MCP/PIP tube direction; thumb route exits the finger and traverses the palm/web corridor.'}
    rows.append(row)
counts={name:sum(r['classification']==name for r in rows) for name in ['TRUE_THUMB_DISTAL_CAP','THUMB_DISTAL_BUT_NOT_CAP','INDEX_SURFACE','FIRST_WEB_SHARED_SURFACE','OTHER','UNRESOLVED']}
assert counts['INDEX_SURFACE']==9
dump('CURRENT_CAP9_NATIVE_BRANCH_CLASSIFICATION.json',{'current_cap9_vertex_ids':CAP,'counts':counts,'vertices':rows,'CURRENT_CAP_9':'CONTAMINATED','classification_basis':'Native topology and independently located native nails/tips only; cap list is audit target, never an identity seed','Human_input_verbatim':{'questions':human['questions'],'notes':human['notes']},'first_web_proxy_limitations':'First-web correspondence remains unresolved per Human Q2; structural proxy does not grant shared-skin authority'})
dump('V2192_NATIVE_BRANCH_IDENTITY_AUDIT.json',{'vertex_id':2192,'native_branch':'INDEX','record':next(r for r in rows if r['vertex_id']==2192),'Human_Q4':'NO','Human_Q5':'LIMITED','notes_verbatim':human['notes'],'historical_membership_only_is_not_this_verdict':True})
tp=sorted(set(CAP)&set(native_cap));fp=[r['vertex_id'] for r in rows if r['classification'] not in ['TRUE_THUMB_DISTAL_CAP','UNRESOLVED']];fn=sorted(set(native_cap)-set(CAP));unres=[r['vertex_id'] for r in rows if r['classification']=='UNRESOLVED']
dump('CAP9_FALSE_POSITIVE_FALSE_NEGATIVE_AUDIT.json',{'comparison_basis':'CURRENT_CAP_9 vs independently constructed native local-geodesic cap candidate. Candidate-relative FN list is not approved membership.','true_positive_ids':tp,'false_positive_ids':fp,'false_negative_candidate_ids':fn,'false_negative_ids':fn,'unresolved_ids':unres,'current_cap9_count':len(CAP),'native_candidate_count':len(native_cap),'candidate_requires_Human_authority_correction':True,'current_cap_production_membership_changed':False})

assert selector['exact_approved_cap_reproduced']
native_owner_count=Counter('PURE_'+label[F[fi][0]].upper() if len({label[i] for i in F[fi]})==1 else 'MIXED_NATIVE_BRANCH' for fi in selector['owned_face_ids'])
selected_native=[{'face_id':fi,'native_branches':sorted({label[i] for i in F[fi]})} for fi in selector['selected_face_ids']]
prov={'audit_name':'R2A_CAP_SELECTOR_PROVENANCE_AUDIT','original_selector':'production_spec/stage5_production_rig/stage5a_r2a/scripts/s5a_r2a_audit.py','canonical_method_source':'production_spec/stage5_production_rig/stage5a_r2b/STAGE5A_R2A_DISTAL_CAP_METHOD_ERRATA.md','older_slab_method_prose':'SUPERSEDED; not the executed canonical selector','original_mesh_state':states['R2_SELECTOR_STATE']['path'],'original_mesh_sha256':states['R2_SELECTOR_STATE']['sha256'],'coordinate_frame':'Mesh matrix_world vertices and Stage4B R2 joint JSON heads/tails are compared in world coordinates; exact selection reproduced','seed':selector['seed'],'seed_native_branch':label[selector['seed']].upper(),'seed_to_v2192_path':selector['seed_to_v2192_path'],'v2192_geodesic_from_seed_mm':selector['v2192_geodesic_mm'],'candidate_domain':'DIG_VERTS[THUMB] = union of vertices of faces assigned THUMB by nearest full-chain Euclidean distance in the RSSF/contact mesh; then positive projection beyond nominal THUMB_IP','candidate_domain_vertex_ids':selector['candidate_domain_vertex_ids'],'owned_face_ids':selector['owned_face_ids'],'owned_face_native_branch_counts':dict(native_owner_count),'distance_metric':'Seed selection maximizes Euclidean distance from nominal IP; patch distance is edge-length Dijkstra in RSSF mesh','graph_domain':'All saved mesh edges, unrestricted by digit ownership during Dijkstra; ownership filter applies to faces afterwards','selector_predicate':'FACE_OWNER == THUMB; min(vertex g) <= 9 mm; face-adjacent connected component containing nearest seed face; cap vertex IDs = union of selected face corners','radius_mm':9.0,'selected_faces_detailed':selector['selected_faces'],'selected_faces_native_branch_check':selected_native,'selected_face_ids':selector['selected_face_ids'],'selected_vertex_ids':selector['selected_vertex_ids'],'exact_frozen_4_faces_9_vertices_reproduced':True,'v2192_exact_inclusion_step':'v2192 is a corner of selected face 356. Face 356 was assigned THUMB by nearest full posed bone chain and passes min-corner geodesic <=9 mm; capv union includes every corner, including v2192. It is not a native thumb-tip identification.','root_cause':{'DIGIT_IDENTITY_CONTAMINATION':'CONFIRMED: all selected cap faces and the seed are native INDEX surface','CONTACT_POSE_PROXIMITY':'CONFIRMED selector mechanism: nearest Euclidean posed-chain assignment chooses THUMB for native index faces; selected face distances recorded','SEED_ERROR':'CONFIRMED anatomical seed mismatch: v2189 is native INDEX; it follows from contaminated domain','OWNED_FACE_ERROR':'CONFIRMED anatomical mismatch in FACE_OWNER domain, despite exact numerical rule execution','COORDINATE_FRAME_ERROR':'NOT_DEMONSTRATED: world-space rule reproduces exact frozen set; no unit or local/world mixing needed to explain result','GEODESIC_DOMAIN_ERROR':'Global graph lacks native-branch guard, but seed-to-cap paths remain entirely on native INDEX: cross-web Dijkstra leakage is not needed for this failure','OTHER':'min-vertex face predicate can include corners beyond 9 mm; not independently the anatomical root cause'},'can_wrong_seed_or_owned_domain_select_index_surface_under_legal_9mm_rule':True,'answer_9mm':'Yes. A geodesic ball around a misidentified index seed is still numerically valid. Radius, connectedness and inherited labels cannot recover correct anatomical identity.','no_selector_or_production_authority_modified':True}
dump('R2A_CAP_SELECTOR_PROVENANCE_AUDIT.json',prov)

# Consume historical evidence only. No posed arrays evaluated or deformation re-run.
feas=s5/'stage5b_r1e_feasibility_audit';ens=load(feas/'R1E_CAP_TO_COLLAR_PATH_ENSEMBLE_AUDIT.json');strict=load(feas/'R1E_STRICT_GEOMETRIC_BOUND_AUDIT.json');short=load(feas/'R1E_CAP_TO_COLLAR_SHORTEST_PATH_AUDIT.json')
dependent_paths=[{'path_vertex_ids':r['vertex_sequence'],'cap_endpoint':r['vertex_sequence'][0],'collar_endpoint':r['vertex_sequence'][-1],'bind_length_mm':r['total_bind_polyline_mm'],'status':'INVALIDATED','scope':'Anatomical thumb-cap-to-index-collar argument; original fixed-ID mesh metric retained','cause':'Native INDEX_SURFACE endpoint in frozen cap list'} for r in ens['top10_distinct_paths']]
dependent_bounds=[]
for pose,block in strict['per_pose'].items():
    for idx,row in enumerate(block['paths']):
        pth=ens['top10_distinct_paths'][idx]['vertex_sequence']
        dependent_bounds.append({'pose':pose,'path_index':idx,'path_vertex_ids':pth,'cap_endpoint':pth[0],'collar_endpoint':pth[-1],'historical_strict_lower_bound':row['STRICT_LOWER_BOUND_dt_over_L_bind'],'status':'INVALIDATED','mathematical_fixed_ID_inequality':'VALID_AS_HISTORICAL_NUMERICAL_EVIDENCE','anatomical_endpoint_authority':'INVALIDATED','replacement_bound':'PENDING_RECOMPUTE_AFTER_HUMAN_CAP_AUTHORITY_CORRECTION'})
bind=np.array(load(s5/'stage5b_r1e_endpoint_authority_review/_tmp/review_raw.json')['R1B']['v'])
bind_adj=[[] for _ in bind]
for a,b in E:
    l=float(np.linalg.norm(bind[a]-bind[b])*1000);bind_adj[a].append((b,l));bind_adj[b].append((a,l))
all_144=[]
for start in CAP:
    bd=np.full(N,np.inf);bd[start]=0.;bp={};q=[(0.,start)]
    while q:
        cost,a=heapq.heappop(q)
        if cost>bd[a]+1e-12:continue
        for b,l in bind_adj[a]:
            if cost+l<bd[b]-1e-12:bd[b]=cost+l;bp[b]=a;heapq.heappush(q,(bd[b],b))
    for target in short['index_side_collar_vertices']:
        seq=[target]
        while seq[-1]!=start:seq.append(bp[seq[-1]])
        all_144.append({'cap_endpoint':start,'collar_endpoint':target,'path_vertex_ids':seq[::-1],'historical_bind_distance_mm':float(bd[target]),'status':'INVALIDATED_AS_ANATOMICAL_CAP_PATH'})
assert len(all_144)==144
assert abs(min(r['historical_bind_distance_mm'] for r in all_144)-13.164617897796292)<1e-7
sens_path=s5/'stage5b_r1e_endpoint_authority_review/R1E_ENDPOINT_SENSITIVITY_AUDIT.json'
sens=load(sens_path)
def historical_bounds(obj,loc='$'):
    found=[]
    if isinstance(obj,dict):
        for key,value in obj.items():
            here=loc+'.'+key
            if isinstance(value,(int,float)) and ('strict_bound' in key.lower() or 'bound' in key.lower() and 'max_' in key.lower()):
                found.append({'source':str(sens_path.relative_to(root)),'json_location':here,'historical_value':value,'status':'INVALIDATED_AS_ANATOMICAL_CAP_ENDPOINT_BOUND','new_value_computed':False})
            elif isinstance(value,(dict,list)):found.extend(historical_bounds(value,here))
    elif isinstance(obj,list):
        for i,value in enumerate(obj):found.extend(historical_bounds(value,loc+'['+str(i)+']'))
    return found
endpoint_sensitivity_bounds=historical_bounds(sens)
historical_references=[]
for directory in [feas,s5/'stage5b_r1e_endpoint_authority_review',s5/'stage5b_r1e_narrow_anatomical_review',s5/'stage5b_r1e_manual_anatomical_reference_review_r1',s5/'stage5b_r1e_human_authority_and_v2192_cap_reaudit_r1']:
    for p in directory.rglob('*'):
        if not p.is_file() or p.suffix not in ['.json','.md'] or '_tmp' in p.parts:continue
        text=p.read_text(encoding='utf8')
        if any(s in text for s in ['STRICT_LOWER_BOUND','STRICT_BOUND','13.1646','cap→collar','cap->collar','cap_to_collar']):
            historical_references.append({'file':str(p.relative_to(root)),'status':'DEPENDENT_CAP_INTERPRETATION_INVALIDATED_IF_USING_CURRENT_CAP9','physical_file_modified':False})
invalidation={'audit_name':'CAP_DEPENDENT_STRICT_BOUND_INVALIDATION_AUDIT','false_positive_endpoints':fp,'unresolved_endpoints':unres,'scope':'Invalidates anatomical thumb distal-cap endpoint claims, not arithmetic facts about historical fixed-ID mesh paths','13.1646_mm_path':{'path':[2192,703,2169,704],'status':'INVALIDATED','native_topological_continuity':'VALID; Human Q5 LIMITED preserved','reason':'Start is native INDEX_SURFACE, not true thumb distal cap'},'CMC_MCP_L3_5.9643':{'status':'INVALIDATED','replacement':'PENDING_RECOMPUTE_AFTER_HUMAN_CORRECTION'},'FULL_OPP_L3_6.5160':{'status':'INVALIDATED','replacement':'PENDING_RECOMPUTE_AFTER_HUMAN_CORRECTION'},'all_144_cap9_to_collar_pairs':{'count':len(CAP)*len(short['index_side_collar_vertices']),'cap_endpoint_ids':CAP,'collar_endpoint_ids':short['index_side_collar_vertices'],'status':'INVALIDATED','reason':'Every audited cap endpoint belongs to native index surface; not merely v2192'},'expanded_historical_paths':dependent_paths,'historical_strict_bounds':dependent_bounds,'affected_evidence_files':historical_references,'numeric_formula_dt_over_L_remains_correct':True,'historical_observed_stretches_or_R1E_FAIL_CLOSED_status_not_erased':True,'new_deformation_runs':0,'new_strict_bounds_computed':False,'replacement_requires_corrected_endpoints_and_separate_authorized_motion_work':True}
dump('CAP_DEPENDENT_STRICT_BOUND_INVALIDATION_AUDIT.json',invalidation)
invalidation['all_144_cap_to_collar_shortest_paths']=all_144
invalidation['later_endpoint_sensitivity_strict_bound_dependencies']=endpoint_sensitivity_bounds
dump('CAP_DEPENDENT_STRICT_BOUND_INVALIDATION_AUDIT.json',invalidation)
dump('_tmp/render_data.json',{'native':native,'labels':label,'tip':tip,'current_cap9':CAP,'current_cap_faces':CF,'native_cap':native_cap,'native_cap_faces':sorted(native_cf),'thumb_anchors':TH,'index_anchors':IX,'thumb_nail_faces':nail['thumb'],'index_nail_faces':nail['index'],'first_web_proxy':WEB,'native_thumb':native_thumb,'native_index':native_index,'rows':rows})
status={'audit':'THUMB_DISTAL_CAP_NATIVE_BRANCH_IDENTITY_AUDIT_R1','Human_authority_verbatim':{'questions':human['questions'],'notes':human['notes']},'Human_source_sha256':sha(human_source),'counts':counts,'v2192_native_branch':'INDEX','v2192_entered_cap_because':'Native index seed v2189 selected from posed nearest-chain THUMB-owned domain; selected face356 passes min-corner 9mm geodesic; cap-vertex union includes v2192','CURRENT_CAP_9':'CONTAMINATED','false_positive_ids':fp,'false_negative_ids':fn,'false_negative_semantics':'Relative to independent native cap candidate; not approved replacement','unresolved_ids':unres,'13.1646mm_path':'INVALIDATED','CMC_MCP_L3_5.9643':'INVALIDATED','FULL_OPP_L3_6.5160':'INVALIDATED','replacement_cap_authority_and_bounds':'PENDING_HUMAN_CORRECTION_AND_LATER_RECOMPUTE','NEXT':'HUMAN_CAP_AUTHORITY_CORRECTION','APPROVED_DISTAL_CAP':'FROZEN_UNCHANGED','DIGIT_OWNERSHIP_AUTHORITY_R3':'HUMAN_APPROVED_UNCHANGED','R3_EXACT_COLLAR':'PASS_UNCHANGED','FIRST_WEB_AUTHORITY':'FROZEN_UNCHANGED','CMC_CAGE':'FROZEN_UNCHANGED','Stage5B_R1B':'FROZEN_PRODUCTION_MASTER_UNCHANGED','Stage5B_R1E':'FAIL_CLOSED_CANDIDATE_UNCHANGED','BLEND_FILES_WRITTEN':0,'WEIGHT_DELTA':0,'GEOMETRY_DELTA':0,'TOPOLOGY_DELTA':0,'BONE_DELTA':0,'JOINT_DELTA':0,'R1F_CREATED':False,'deformation_runs':0,'weight_solves':0,'retopo':False,'STOP':'WAITING_FOR_HUMAN_CAP_AUTHORITY_REVIEW'}
dump('THUMB_DISTAL_CAP_NATIVE_BRANCH_IDENTITY_AUDIT_R1_STATUS.json',status)
print('Native thumb/index tip:',tip['thumb'],tip['index'],'native cap seed:',native_seed,'candidate IDs:',native_cap)
print('Classification:',counts,'false positive:',fp,'true positive:',tp)
print('v2192:',rows[6]['thumb_anchor_path']['distance_mm'],rows[6]['index_anchor_path']['distance_mm'],'mm to thumb/index independent anchors')
print('Historical dependency rows:',len(dependent_paths),'paths',len(dependent_bounds),'bounds. No deformation runs.')
