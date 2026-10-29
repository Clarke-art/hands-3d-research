"""Read frozen JSON only. No Blender, ownership solve, mincut or source-distance field."""
import sys,json,math,re
from collections import Counter,deque
from pathlib import Path
import numpy as np
sys.dont_write_bytecode=True
from intake import ROOT,OUT,PREV,read,sha,dump
S5=ROOT/'production_spec/stage5_production_rig'
R3=ROOT/'production_spec/stage6_deformation/stage6b_r3_thumb_tip_ownership_boundary'
A=read(PREV/'AUTHORITY_INPUT_VERIFICATION.json')
def src(k):return read(ROOT/A['sources'][k]['path'])
J=read(PREV/'READ_ONLY_LIVE_EXTRACTION.json')
V=np.array(J['RSSF']['vertices_world_m']);N=np.array(J['NATIVE']['vertices_world_m'])
E=J['RSSF']['edges'];F=J['RSSF']['faces'];nv=len(V)
native=src('native_partition_evidence');labels=native['labels']
cap=set(src('cap_authority')['vertex_ids']);web=set(src('first_web_membership')['selected_vertices'])
nails={d:{v for fi in ids for v in F[fi]} for d,ids in src('nail_authority')['per_digit_faces'].items()}
adj=[set() for _ in range(nv)]
for a,b in E:adj[a].add(b);adj[b].add(a)
edge_mm=[float(np.linalg.norm(V[a]-V[b])*1000) for a,b in E]
tau=sorted(edge_mm)[len(E)//2];pflip=round(tau/3*1000)
def pack(ids):
    ids=sorted(set(map(int,ids)))
    return {'count':len(ids),'vertex_ids':ids,'native_partition_candidate_counts':dict(Counter(labels[i] for i in ids))}
def grow(ids,k):
    result=set(ids);front=set(ids)
    for _ in range(k):front={w for v in front for w in adj[v]}-result;result|=front
    return result
def components(ids,custom_adj=None):
    ids=set(ids);todo=set(ids);result=[];aa=adj if custom_adj is None else custom_adj
    while todo:
        seed=min(todo);seen={seed};q=[seed];todo.remove(seed)
        while q:
            v=q.pop()
            for w in aa[v]:
                if w in todo:todo.remove(w);seen.add(w);q.append(w)
        result.append(seen)
    return sorted(result,key=lambda x:(-len(x),min(x)))
native_sets={d:{i for i in range(nv) if labels[i]==d} for d in ['thumb','index','wrist']}
cores={d:{i for i in ids if grow({i},2)<=ids} for d,ids in native_sets.items()}
chain_data=read(PREV/'CORRECTED_LIVE_THUMB_CHAIN_R1.json')
chains={'thumb':np.array(chain_data['polyline_world_m']),'index':np.array(chain_data['all_other_live_chains']['INDEX']['polyline_world_m'])}
def project(C,P):
    ds=np.full(len(P),np.inf);ss=np.zeros(len(P));ks=[0.];base=0.
    for a,b in zip(C[:-1],C[1:]):
        ab=b-a;l=np.linalg.norm(ab);t=np.clip((P-a)@ab/(l*l),0,1);dd=np.linalg.norm(P-(a+t[:,None]*ab),axis=1)*1000
        take=dd<ds;ds[take]=dd[take];ss[take]=base+t[take]*l*1000;base+=l*1000;ks.append(base)
    return ss,ds,ks
sT,dT,kT=project(chains['thumb'],V);sI,dI,kI=project(chains['index'],V)
old=read(R3/'R3_OWNERSHIP_LABELS.json') # comparison / provenance only
oldgraph=set(read(PREV/'R3_GRAPH_DOMAIN_INPUT_RECONCILIATION.json')['old_graph']['vertex_ids'])
cageaudit=read(PREV/'CMC_CAGE_R3_WRAPPER_RECONCILIATION_R1.json')
cage=set(cageaudit['construction_coordinate_candidate']['vertex_ids'])
sp=set(cageaudit['unfiltered_historical_support']['vertex_ids'])
index_tube=set(read(PREV/'CORRECTED_THUMB_TUBE_ANCHOR_CANDIDATE_AUDIT.json')['sets']['index_native_guarded_tube']['vertex_ids'])
idx_sources=index_tube|nails['index']
thumb_landmarks=cap|nails['thumb']|{284}
wrist_seed=native['tip_seeds']['wrist']

# Candidate structures: never assert native Voronoi or its erosion is anatomical exclusivity.
exT=cores['thumb']-web;exI=cores['index']-web
g1=exT|exI;g2=g1|web
allowed=native_sets['thumb']|native_sets['index']|native_sets['wrist']
# Finite k-ring dilation is a topology-only extent hypothesis. Cage does not add graph members.
g3={k:g2|((grow(g2,k)-g2)&allowed) for k in [1,2]}
graphs={'G1':g1,'G2':g2,'G3_K1':g3[1],'G3_K2':g3[2],'G4_HISTORICAL_COMPARISON_ONLY':oldgraph}
def graph_audit(ids):
    ids=set(ids);ee=[(a,b) for a,b in E if a in ids and b in ids];cs=components(ids)
    faces=[fi for fi,vs in enumerate(F) if set(vs)<=ids]
    ef=Counter();facevs=set()
    for fi in faces:
        vs=F[fi];facevs.update(vs)
        for a,b in zip(vs,vs[1:]+vs[:1]):ef[tuple(sorted((a,b)))]+=1
    be=[e for e,n in ef.items() if n==1];ba={v:set() for e in be for v in e}
    for a,b in be:ba[a].add(b);ba[b].add(a)
    bc=components(ba,ba) if ba else []
    complement=components(set(range(nv))-ids)
    holes=[c for c in complement if not any(native['tip_seeds'][d] in c for d in ['wrist','middle','ring','little'])]
    eligibleT=thumb_landmarks&ids;eligibleI=idx_sources&ids
    reach=[{'size':len(c),'thumb_landmark_count':len(c&eligibleT),'index_source_count':len(c&eligibleI),'web_count':len(c&web),'has_both_source_families':bool(c&eligibleT) and bool(c&eligibleI)} for c in cs]
    missingT=thumb_landmarks-ids;missingI=idx_sources-ids
    edge_isolates=sorted(v for v in ids if not adj[v]&ids)
    face_orphans=ids-facevs
    out={'membership':pack(ids),'edge_count':len(ee),'fully_included_face_count':len(faces),'connected_components':len(cs),'component_sizes':[len(c) for c in cs],'component_anchor_reachability':reach,'missing_thumb_landmarks':sorted(missingT),'missing_index_sources':sorted(missingI),'all_vertices_reach_both_source_families':all(r['has_both_source_families'] for r in reach) and not missingT and not missingI,'shared_region_membership':pack(ids-(exT|exI)),'web_induced_component_sizes':[len(c) for c in components(web&ids)],'web_reachable_via_whole_graph':all(any(v in c and c&eligibleT and c&eligibleI for c in cs) for v in web) if web<=ids else False,'edge_isolates':edge_isolates,'surface_boundary_edge_count':len(be),'surface_boundary_component_sizes':[len(c) for c in bc],'surface_boundary_non_degree2_vertices':sorted(v for v in ba if len(ba[v])!=2),'euler_characteristic_surface':len(facevs)-len(ef)+len(faces),'surface_orphan_graph_vertices':sorted(face_orphans),'surface_wire_edges':[list(e) for e in ee if tuple(sorted(e)) not in ef],'complement_components':[pack(c) for c in complement],'potential_enclosed_holes_no_outside_tip_or_wrist': [pack(c) for c in holes],'hole_caveat':'Complement components without excluded digit/wrist landmarks are hole candidates, not a complete manifold proof; boundary branching and wire edges reported separately.','wrist_leakage':{'native_wrist_candidate_count':len(ids&native_sets['wrist']),'native_wrist_seed_present':wrist_seed in ids,'within_2_rings_of_wrist_seed':sorted(ids&grow({wrist_seed},2)),'min_native_euclidean_distance_to_wrist_seed_mm':float(min(np.linalg.norm(N[v]-N[wrist_seed])*1000 for v in ids)),'deep_native_thumb_index_palm_count_not_certified_anatomy':len([v for v in ids if (sT[v]<kT[1] and sI[v]==0)])},'cage_construction_candidate_overlap':pack(ids&cage),'cage_sphere_overlap':pack(ids&sp),'native_other_digit_conflicts':pack(ids-allowed),'provisional_hard_pin_native_index_conflicts':sorted(exT&native_sets['index']),'canonical_domain_selected':False}
    out['static_viability']='NON_VIABLE' if len(cs)!=1 or missingT or missingI or edge_isolates or holes else 'CONNECTIVITY_PASSES_ONLY_AUTHORITY_UNRESOLVED'
    return out
audits={k:graph_audit(v) for k,v in graphs.items()}
dump('PROXIMAL_COUPLED_DOMAIN_CANDIDATE_AUDIT.json',{'status':'UNRESOLVED','no_solve':True,'exclusive_operational_hypothesis':'Native tip/nail-linked Voronoi branch with unanimous 2-hop neighborhood, frozen web removed. Structural proxy ONLY: does not certify biological ownership or palm extent.','G1':'proxy THUMB_EXCLUSIVE union INDEX_EXCLUSIVE','G2':'G1 union frozen FIRST_WEB_21 as shared neutral','G3':'G2 plus 1 or 2 mesh rings, allowed native structural THUMB/INDEX/wrist only; added vertices shared neutral. K is not approved. Cage membership never forces inclusion.','G4':'Legacy membership comparison only; no authority candidacy','candidates':audits,'reason_not_selected':'Connectivity can exclude disconnected candidates; it cannot establish exclusive anatomy or choose proximal support width. Two-ring erosion cannot turn Voronoi into anatomy.','remaining_single_blocker':'PROXIMAL_EXCLUSIVE_SHARED_EXTENT_AUTHORITY'})

# Radius calibration: disjoint sampling hypotheses recorded rather than a manual 14-ID blacklist.
baseband={i for i in native_sets['thumb'] if kT[1]<=sT[i]<=kT[2]}
sample_candidates={}
for rings in [0,1,2,3]:
    pool={i for i in baseband if grow({i},rings)<=native_sets['thumb']} - web
    radius=float(sorted(dT[i] for i in pool)[len(pool)//2])
    raw={i for i in range(nv) if dT[i]<=radius and sT[i]>=kT[1]}
    guarded=raw&exT
    corridor={i for i in exT if dT[i]<=.85*radius and .30*kT[1]<=sT[i]<kT[1]}
    sample_candidates[str(rings)]={'sample':pack(pool),'radius_mm':radius,'rejected_vs_full_native_band':pack(baseband-pool),'raw_tube':pack(raw),'raw_native_index_conflicts':pack(raw&native_sets['index']),'provisional_guarded_tube':pack(guarded),'provisional_corridor':pack(corridor),'guarded_native_index_conflicts':sorted(guarded&native_sets['index']),'cap37_overlap':sorted(cap&guarded),'first_web_sample_overlap':sorted(pool&web)}
radius_authority={'status':'UNRESOLVED','required_semantics':'Exclusive digit surface / cross-sections in corrected MCP..IP band, excluding shared proximal interface, first web and index-facing contact surface. Frozen cap not reselected.','historical_statistic':'Upper order median sorted distances[n//2], not averaged median; empty population FAIL_CLOSED.','independent_guard_authority':'UNRESOLVED','candidates':sample_candidates,'two_ring_removes_14_deterministically':len(baseband-{i for i in baseband if grow({i},2)<=native_sets['thumb']})==14,'why_not_resolved':'A k-ring unanimous Voronoi neighborhood is structural stability only. No authoritative independent boundary identifies all exclusive cross-sections/contact surfaces; k=2 has no unique anatomy provenance. An explicit contact-facing surface mask is also absent.','canonical_radius_mm':None,'manual_exception_blacklist':False}
historical_pools={'full_native_band':baseband,'two_ring_stable_including_web':baseband&cores['thumb']}
radius_authority['previous_candidate_reproduction']={name:{'sample':pack(pool),'radius_mm':float(sorted(dT[i] for i in pool)[len(pool)//2]),'first_web_overlap':sorted(pool&web)} for name,pool in historical_pools.items()}
radius_authority['new_counterexample']='Two-ring stability does not exclude frozen FIRST_WEB: its sample overlap is recorded. Thus 10.180583 mm is not an exclusive-only population even under the proposed default FW1 role.'
dump('THUMB_TUBE_RADIUS_SAMPLE_AUTHORITY_R1.json',radius_authority)
chosen_diag=sample_candidates['2'];tube2=set(chosen_diag['provisional_guarded_tube']['vertex_ids']);corr2=set(chosen_diag['provisional_corridor']['vertex_ids'])
provenance={str(v):[name for name,ids in [('CAP37',cap),('THUMB_NAIL',nails['thumb']),('TUBE_DIAGNOSTIC_K2',tube2),('CORRIDOR_DIAGNOSTIC_K2',corr2)] if v in ids] for v in sorted(cap|nails['thumb']|tube2|corr2)}
dump('CORRECTED_THUMB_TUBE_ANCHOR_AUTHORITY_PROPOSAL.json',{'status':'UNRESOLVED','canonical_radius_mm':None,'canonical_tube_anchor_count':None,'predicate':'distance<=approved radius AND arc>=MCP AND independent role==THUMB_EXCLUSIVE; no default shared hard pin','provisional_k2_only':chosen_diag,'source_deduplication':'Union of unique vertex IDs; retain all provenance tags; one hard constraint per vertex, no duplicated capacity/weight/INF.','diagnostic_source_provenance_tags':provenance,'diagnostic_unique_union_count':len(provenance),'diagnostic_cross_digit_conflicts':sorted(set(map(int,provenance))&idx_sources),'final_strong_sources_generated':False,'oldcap9_can_reenter_thumb_strong':False,'remaining_single_blocker':'PROXIMAL_EXCLUSIVE_SHARED_EXTENT_AUTHORITY'})
dump('INDEPENDENT_DIGIT_DOMAIN_GUARD_R1.json',{'status':'UNRESOLVED','rule_invariants_resolved':True,'four_roles':['THUMB_EXCLUSIVE','INDEX_EXCLUSIVE','SHARED_NEUTRAL','OUTSIDE_COUPLED_DOMAIN'],'source_eligibility':'Geometry-only sources require independently established exclusive class; shared neutral has no source role; explicit approved cap/nail source ingredients retained; cross-role conflict fails closed before union.','graph_eligibility':'Exclusive or approved limited shared support; outside excluded. Graph membership never implies hard pin.','native_partition_is_truth':False,'rejected_methods':['Nearest corrected chain wins','Native Voronoi winner grants ownership','Two-ring erosion alone grants biological ownership','Old R2/R3 labels','Handwritten 14-point exception list'],'structural_exclusive_candidates':{'thumb':pack(exT),'index':pack(exI)},'shared_neutral_approved_membership_proposal':pack(web),'rest_unassigned_authority':True,'canonical_role_map':None,'outside_coupled_membership':None,'oldcap9_hard_thumb_forbidden':True,'native_index_cannot_enter_thumb_by_proximity':True,'native_thumb_cannot_enter_index_by_proximity':True,'remaining_single_blocker':'PROXIMAL_EXCLUSIVE_SHARED_EXTENT_AUTHORITY'})

# Pointwise wrapper evidence; historical roles recorded but never selectors.
web_source=src('first_web_membership');webrows=[]
for v in sorted(web):
    webrows.append({'vertex_id':v,'native_partition_candidate':labels[v],'historical_R3':{'label':old['R3'][v],'THUMB_STRONG':v in old['THUMB_STRONG'],'INDEX_STRONG':v in old['INDEX_STRONG'],'role_is_truth':False},'skin_weight_authority_role':{'allowed_family':['WRIST_R','THUMB_CMC_R','THUMB_MCP_R','INDEX_MCP_R'],'THUMB_IP_WEIGHT':0,'source':'STAGE5B_HUMAN_APPROVAL_FREEZE_R1.json / semantic_regions.FIRST_WEB','weights_are_ownership_proof':False},'corrected_chain_distance_mm':{'thumb':float(dT[v]),'index':float(dI[v])},'corrected_arc_mm':{'thumb':float(sT[v]),'index':float(sI[v])},'topology':{'mesh_degree':len(adj[v]),'web_neighbors':sorted(adj[v]&web),'outside_web_neighbors':sorted(adj[v]-web),'incident_face_ids':[fi for fi,vs in enumerate(F) if v in vs],'web_boundary_vertex':bool(adj[v]-web),'native_partition_interface_vertex':any(labels[w]!=labels[v] for w in adj[v]),'historical_thumb_side_boundary_record':v in web_source['thumb_side_boundary'],'historical_boundary_is_authority':False},'proposed_role':'SHARED_NEUTRAL_GRAPH_ONLY','hard_source':False})
dump('FIRST_WEB_R3_ROLE_AUTHORITY_PROPOSAL.json',{'status':'RESOLVED_PROPOSAL_PENDING_HUMAN','membership':'FIRST_WEB_21_FROZEN_UNCHANGED','selected_candidate':'FW1_SHARED_NEUTRAL_GRAPH_ONLY','graph_membership_required':True,'hard_source_ids':[],'FW2':'NOT_SUPPORTED: no independent exclusive-anchor authority for a subset supplied','FW3':'NOT_SUPPORTED: weight locality approval is not categorical ownership authority; old implementation alone insufficient','vertices':webrows,'actual_graph_finalization':'BLOCKED_BY_PROXIMAL_EXCLUSIVE_SHARED_EXTENT_AUTHORITY'})
dump('CMC_CAGE_R3_ROLE_AUTHORITY_PROPOSAL.json',{'status':'RESOLVED_ROLE_PROPOSAL_PENDING_HUMAN','geometry':'FROZEN_PASS_UNCHANGED','role':'CAGE_GEOMETRY_PROTECTED_BUT_NOT_R3_HARD_SOURCE','A_graph_membership':'No automatic inclusion; intersect with eventual independently approved graph. Cage existence cannot set graph extent.','B_THUMB_hard_source':False,'C_validator_protection':True,'D_ownership_independent':True,'label_independent_protection':'Frozen complete mesh geometry/topology hash/equality preserves cage geometry without relying on approximate 73-point reconstruction. Future local deformation mask identity requires exact topology provenance, separately from R3 input authority.','construction_candidate':pack(cage),'construction_exact_mapping_confirmed':False,'mapping_max_error_mm':max(x['native_match_error_mm'] for x in cageaudit['mapping_records']),'historical_R3_direct_cage_hard_source':False,'historical_sphere_not_construction':True,'no_cage_geometry_reconstruction':True})
dump('THENAR_PALM_R3_ROLE_AUDIT.json',{'status':'RESOLVED_ROLE_RESTRICTION_EXTENT_UNRESOLVED','role':'GRAPH_SUPPORT_OR_VALIDATION_CANDIDATE_ONLY','THUMB_hard_source':False,'whole_palm_admission':False,'historical_sphere':pack(sp),'cage_construction_candidate':pack(cage),'sphere_only':pack(sp-cage),'cage_only':pack(cage-sp),'historical_thenar_definition':'r1a_common.py: thenar_thumb selected by own_r1a plus s<=MCP+TAU and d>R_TT; thenar_wrist from two rings around thumb ownership filtered by wrist and arc. NOT ownership-independent.','frozen_thenar_ownership_authority_found':False,'skin_locality_approval_is_ownership_authority':False,'finite_support_candidates':['G3_K1','G3_K2'],'remaining_single_blocker':'PROXIMAL_EXCLUSIVE_SHARED_EXTENT_AUTHORITY'})

# INF bounds do not require or generate geodesic unary fields.
# For capped common-mm unary: each graph vertex pays at most ONE of its two costs.
bounds={}
for name,gg in graphs.items():
    ec=audits[name]['edge_count'];uc=len(gg)*400000;pc=ec*pflip
    bounds[name]={'vertex_count':len(gg),'edge_count':ec,'max_finite_unary_sum_safe_upper_bound':uc,'max_pairwise_contribution_safe_upper_bound':pc,'finite_cut_cost_safe_upper_bound':uc+pc,'INF_SAFE_LOWER_BOUND_strict':uc+pc,'minimum_safe_integer_INF':uc+pc+1,'unary_bound_is_attained_maximum':False,'pairwise_bound_is_attained_maximum':False,'source':'400 mm cap x 1000 integer/mm; 1 pairwise penalty per undirected cut edge, not twice','static_viability':audits[name]['static_viability'],'canonical':False}
dump('R3_INF_BOUND_AUDIT.json',{'status':'RESOLVED_BOUND_FORMULA_GRAPH_INSTANCE_UNRESOLVED','canonical_units':'COMMON_MM','formula':'U=sum_v max(C_T(v),C_I(v)) <= |V|*400000; P<=|E|*1296; choose INF=|V|*400000+|E|*1296+1','proof':'A pin-respecting assignment exists only if source sets are disjoint. It has cost <=B. Every pin-violating cut has cost>=INF>B, hence cannot minimize. Each vertex contributes at most one terminal edge; each undirected unlike-label edge contributes one directed forward arc even when encoded by two directions.','preconditions':['finite nonnegative fields','every component reaches both unique source families','hard sources disjoint','confirmed 400 mm finite cap','integer accumulation does not overflow'],'candidates':bounds,'canonical_INF':None,'note':'Source-independent conservative upper bounds, not exact maxima and not solve results. NON_VIABLE graph rows cannot authorize solving. Historical magic INF=10^15 retired.'})
dump('R3_GRAPH_DOMAIN_AUTHORITY_PROPOSAL.json',{'status':'UNRESOLVED','selected_graph_candidate':None,'canonical_role_map':None,'graph_membership_does_not_imply_hard_source':True,'candidate_audit':'PROXIMAL_COUPLED_DOMAIN_CANDIDATE_AUDIT.json','missing_evidence':'Independent, label-free proximal exclusive/shared boundary and bounded support extent; ring width and contact-facing sample exclusions lack unique provenance.','remaining_single_blocker':'PROXIMAL_EXCLUSIVE_SHARED_EXTENT_AUTHORITY'})
dump('STATIC_MEASUREMENTS.json',{'tau_mm':tau,'pairwise_capacity':pflip,'graphs':{k:{x:v[x] for x in ['edge_count','connected_components','component_sizes','static_viability','all_vertices_reach_both_source_families']}|{'vertices':len(graphs[k]),'wrist':v['wrist_leakage'],'holes':len(v['potential_enclosed_holes_no_outside_tip_or_wrist'])} for k,v in audits.items()},'radius_candidates':{k:{'samples':v['sample']['count'],'radius_mm':v['radius_mm'],'raw_tube':v['raw_tube']['count'],'guarded_tube':v['provisional_guarded_tube']['count'],'corridor':v['provisional_corridor']['count']} for k,v in sample_candidates.items()},'index_sources_count':len(idx_sources),'index_ingredients_unchanged':True,'web_count':len(web),'cage_count':len(cage),'cage_sphere_count':len(sp)})
print(json.dumps(read(OUT/'STATIC_MEASUREMENTS.json'),indent=2))
