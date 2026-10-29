"""Offline evidence analysis and figures from immutable extraction; no Blender writes."""
import sys
sys.dont_write_bytecode=True
import json, math, heapq, hashlib, textwrap
from pathlib import Path
from collections import Counter, deque
import numpy as np
from PIL import Image, ImageDraw, ImageFont

AUD=Path(__file__).resolve().parents[1]
ROOT=AUD.parents[2]
FEAS=AUD.parent/'stage5b_r1e_feasibility_audit'
R=json.loads((AUD/'_tmp/review_raw.json').read_text(encoding='utf-8'))
V=np.array(R['R1B']['v']); E=R['R1B']['edges']; F=R['R1B']['faces']; N=len(V)
WB,WE=R['R1B']['w'],R['R1E']['w']; LAB=R['R3']; R3=LAB['R3']
CAP=set(LAB['CAP']); WEB=set(LAB['WEB']); NT=set(LAB['NAIL_THUMB']); NI=set(LAB['NAIL_INDEX'])
BOUND=LAB['boundary_edges_R3']; C0={v for k in BOUND for v in E[k]}
ADJ=[set() for _ in V]; INCIDENT=[[] for _ in V]
for a,b in E: ADJ[a].add(b); ADJ[b].add(a)
for fi,p in enumerate(F):
    for v in p: INCIDENT[v].append(fi)
BL=np.array([np.linalg.norm(V[a]-V[b])*1000 for a,b in E]); MED=float(np.median(BL))
def neigh(vs): return set().union(*(ADJ[v] for v in vs)) if vs else set()
C1=neigh(C0)-C0; C2=neigh(C1)-C0-C1
WEBADJ=neigh(WEB)-WEB
DOMAIN=C0|C1|C2|WEBADJ
def gd(seeds):
    d={v:0 for v in seeds}; q=deque(sorted(seeds))
    while q:
        v=q.popleft()
        for u in sorted(ADJ[v]):
            if u not in d: d[u]=d[v]+1; q.append(u)
    return d
GC,GW,GCA=gd(C0),gd(WEB),gd(CAP)
ST=np.array(R['arcs_mm']['THUMB']); SI=np.array(R['arcs_mm']['INDEX'])
chains={d:np.array(p) for d,p in R['R2A_chains'].items()}
tx=np.r_[0,np.cumsum(np.linalg.norm(np.diff(chains['THUMB'],axis=0),axis=1)*1000)]
ix=np.r_[0,np.cumsum(np.linalg.norm(np.diff(chains['INDEX'],axis=0),axis=1)*1000)]
tt=np.median(ST[[v for v in range(N) if R3[v]=='THUMB' and tx[1]<=ST[v,0]<=tx[2]],1])
base=sorted(ST[v,1] for v in range(N) if R3[v]=='THUMB' and ST[v,0]<=tx[1])
tmax=max(base[int(.95*(len(base)-1))],tt*1.25)
def sem(v):
    if v in CAP:return 'DISTAL_CAP'
    if v in NT:return 'THUMB_NAIL'
    if v in NI:return 'INDEX_NAIL'
    if v in WEB:return 'FIRST_WEB'
    if R3[v]=='THUMB':
        if ST[v,0]>=tx[2]-MED:return 'THUMB_DISTAL'
        if ST[v,0]>=tx[1]-MED:return 'THUMB_MCP_TRANSITION'
        return 'THUMB_CMC_TRANSITION' if ST[v,1]<=tmax else 'THENAR'
    if R3[v]=='INDEX':return 'INDEX_ROOT' if SI[v,0]<=ix[2] else 'INDEX_PHALANX'
    if R3[v]=='wrist':return 'THENAR' if ST[v,1]>tt and ST[v,0]<=tx[1]+MED else 'PALM'
    return 'OTHER_'+R3[v]
SEM=[sem(v) for v in range(N)]
PALM={v for v in range(N) if SEM[v]=='PALM'}
GP=gd(PALM); GPT=gd(PALM|{v for v in range(N) if SEM[v]=='THENAR'})
def dom(w): return max(w,key=w.get) if w else None
def klass(v):
    if v in CAP:return 'APPROVED_DISTAL_CAP_FROZEN'
    if v in NT|NI:return 'APPROVED_NAIL_FROZEN'
    if v in WEB:return 'APPROVED_FIRST_WEB_FROZEN'
    if v in C0|C1|C2:
        if R3[v]=='INDEX':return 'INDEX_ROOT_DOMINANT_TISSUE' if SI[v,0]<=ix[2] else 'INDEX_SHAFT_PROTECTED'
        if R3[v]=='THUMB':return 'COLLAR_THUMB_SIDE_ANATOMY_UNRESOLVED'
    if v in WEBADJ:
        if R3[v]=='wrist' and WB[v].get('WRIST_R',0)>=.95 and sum(WB[v].get(g,0) for g in ['THUMB_CMC_R','THUMB_MCP_R'])<1e-6:return 'PALM_ANCHOR_TISSUE'
        return 'FIRST_WEB_ADJACENT_ROLE_REVIEW'
    return 'OUTSIDE_REVIEW_DOMAIN'
K=[klass(v) for v in range(N)]
def desc(v):
    return {'INDEX_ROOT_DOMINANT_TISSUE':'Index-side proximal tube at the approved topological sheet base; index arc and historical index drive agree. This is not established first-web tissue.',
    'COLLAR_THUMB_SIDE_ANATOMY_UNRESOLVED':'Body side of the frozen R3 sheet interface. R3 ownership is THUMB, historical drive is predominantly INDEX, and arc proxy is thumb-distal. Soft-tissue identity cannot be assigned from the contacting RSSF pose or ownership alone.',
    'FIRST_WEB_ADJACENT_ROLE_REVIEW':'Direct mesh neighbor of approved first-web; a local deformation-continuity candidate. Adjacency supports role review, not blanket extension of weights to the distant collar.',
    'PALM_ANCHOR_TISSUE':'Direct web neighbor historically wrist anchored; preserve palm convergence and examine local CMC precedent before any extension.'}.get(K[v],'Frozen authority or protected index-shaft surface; no new local authority granted.')
def row(v):
    r1=ADJ[v]; r2=neigh(r1)-r1-{v}
    return {'vertex_id':v,'R3_ownership':R3[v],'side':R3[v],'semantic_region':SEM[v], 'semantic_region_provenance':'historical ownership + live arc/radius proxy; NOT verified tissue anatomy','anatomical_class':K[v],'local_anatomy_description':desc(v),
    'bind_position_mm':(V[v]*1000).tolist(),'distance_to_joint_mm':{g:float(np.linalg.norm(V[v]-R['R2A_joints'][g])*1000) for g in ['INDEX_MCP_R','THUMB_CMC_R','THUMB_MCP_R']},
    'live_chain_arc_mm':{'thumb':float(ST[v,0]),'index':float(SI[v,0])},'live_chain_lateral_mm':{'thumb':float(ST[v,1]),'index':float(SI[v,1])},
    'graph_distance':{'first_web':GW[v],'thumb_distal_cap':GCA[v],'palm':GP[v],'palm_or_thenar':GPT[v],'exact_collar':GC[v]},
    'R1B_full_weight_vector':WB[v],'R1E_full_weight_vector':WE[v],'dominant_R1B':dom(WB[v]),'dominant_R1E':dom(WE[v]),'first_web_adjacency':sorted(ADJ[v]&WEB),
    'incident_faces':[{'face_id':fi,'vertices':F[fi]} for fi in INCIDENT[v]],'one_ring_vertices':sorted(r1),'two_ring_vertices':sorted(r2),
    'one_ring_semantic_composition':dict(Counter(SEM[u] for u in r1)),'two_ring_semantic_composition':dict(Counter(SEM[u] for u in r2))}
def dump(name,obj):
    (AUD/name).write_text(json.dumps({'review':'R1E_ENDPOINT_WEIGHT_AUTHORITY_REVIEW','generated_at':R['generated_at'],'read_only':True,**obj},indent=1,ensure_ascii=False),encoding='utf-8')
COL=[row(v) for v in sorted(C0)]
classcounts=dict(Counter(K[v] for v in C0))
dump('R1E_ENDPOINT_COLLAR_ANATOMY_AUDIT.json',{'classification_rules':{'priority':'frozen cap/nail/web; then C0/C1/C2 index-side with live arc proximal of PIP -> index-root; thumb/body side -> anatomical identity unresolved; direct web neighbors -> role review or historical palm anchor','not_homogeneous':'INDEX side and THUMB/body side have distinct evidence confidence. No shared-web or palm class is forced into the 32-vertex set.'},'class_counts':classcounts,'vertices':COL,'frozen_R3_ownership_unchanged':True})
domainrows=[row(v) for v in sorted(DOMAIN)]
dump('R1E_ENDPOINT_REVIEW_DOMAIN.json',{'C0':sorted(C0),'C1':sorted(C1),'C2':sorted(C2),'web_direct_transition_neighbors':sorted(WEBADJ),'additional_web_neighbors_outside_C012':sorted(WEBADJ-C0-C1-C2),'approved_web_context':sorted(WEB),'counts':{'C0':len(C0),'C1':len(C1),'C2':len(C2),'C012':len(C0|C1|C2),'extra_web_transition':len(WEBADJ-C0-C1-C2),'total_unique':len(DOMAIN)},'frozen_cap_overlap':sorted(DOMAIN&CAP),'frozen_nail_overlap':sorted(DOMAIN&(NI|NT)), 'vertices':domainrows})

AUTHREG=json.loads((AUD.parent/'stage5b_r1e/STAGE5B_R1E_AUTHORISED_WEIGHT_REGION.json').read_text(encoding='utf-8'))
CAGE=set(AUTHREG['region_exclusions_frozen_authorities']['CMC_CAGE'])
def precedents(g):
    vs=[v for v in range(N) if WB[v].get(g,0)>1e-6 and (R3[v]!='THUMB' or v in WEB)]
    return {'exists':bool(vs),'non_thumb_surface_count':sum(R3[v]!='THUMB' for v in vs),'first_web_count':sum(v in WEB for v in vs),'cage_neighborhood_count':sum(v in CAGE for v in vs),'index_owned_count':sum(R3[v]=='INDEX' for v in vs),'exact_collar_count':sum(v in C0 for v in vs),
    'by_historical_semantic':dict(Counter(SEM[v] for v in vs)),'vertices':[{'vertex_id':v,'R3':R3[v],'semantic':SEM[v],'R1B_weight':WB[v][g],'R1E_weight':WE[v].get(g,0),'frozen_in_R1E':WB[v]==WE[v],'in_CMC_cage':v in CAGE,'in_first_web':v in WEB,'graph_to_collar':GC[v]} for v in vs]}
PC,PM=precedents('THUMB_CMC_R'),precedents('THUMB_MCP_R')
REGIONS={'approved_first_web':WEB,'frozen_CMC_cage_neighborhood':CAGE,
 'thenar_historical_proxy':{v for v in range(N) if SEM[v]=='THENAR'},
 'thumb_base_live_arc_proxy':{v for v in range(N) if R3[v]=='THUMB' and ST[v,0]<=tx[1] and v not in WEB},
 'palm_thumb_transition_historical_proxy':{v for v in range(N) if R3[v]=='wrist' and (WB[v].get('THUMB_CMC_R',0)>1e-6 or WB[v].get('THUMB_MCP_R',0)>1e-6)}}
REGIONAL_CENSUS={name:{'vertex_count':len(vs),'definition_authority':'approved/frozen region' if name in ['approved_first_web','frozen_CMC_cage_neighborhood'] else 'descriptive live-arc/semantic historical proxy; not a new authority',
 'R3_counts':dict(Counter(R3[v] for v in vs)),
 'THUMB_CMC_influence_vertices':sum(WB[v].get('THUMB_CMC_R',0)>1e-6 for v in vs),
 'THUMB_MCP_influence_vertices':sum(WB[v].get('THUMB_MCP_R',0)>1e-6 for v in vs),
 'frozen_R1B_R1E_vector_count':sum(WB[v]==WE[v] for v in vs),
 'vertices':[{'vertex_id':v,'R3':R3[v],'R1B_full_vector':WB[v],'R1E_full_vector':WE[v]} for v in sorted(vs)]} for name,vs in REGIONS.items()}
dump('R1E_EXISTING_CROSS_REGION_THUMB_INFLUENCE_PRECEDENT.json',{'source':'frozen R1B measured field, checked against R1E and R1A first-web field; threshold >1e-6 excludes float residue','THUMB_CMC_R':PC,'THUMB_MCP_R':PM,'regional_neighborhood_census':REGIONAL_CENSUS,'authority_scope':'Existing first-web/thenar/palm and CMC neighborhood precedent establishes that ownership is not allowed-group authority. It does NOT prove anatomical permission on the remote collar. R3-INDEX has no measured CMC/MCP precedent.','first_web_approved_groups':['WRIST_R','THUMB_CMC_R','THUMB_MCP_R','INDEX_MCP_R'],'first_web_weight_delta_R1A_R1B_R1E':0.0})

groups=['WRIST_R','THUMB_CMC_R','THUMB_MCP_R','INDEX_MCP_R']
GRAD=[]
for k,(a,b) in enumerate(E):
    if a not in DOMAIN|WEB or b not in DOMAIN|WEB:continue
    ja={g:abs(WB[a].get(g,0)-WB[b].get(g,0)) for g in groups}
    jb={g:abs(WE[a].get(g,0)-WE[b].get(g,0)) for g in groups}
    l1a=sum(abs(WB[a].get(g,0)-WB[b].get(g,0)) for g in set(WB[a])|set(WB[b]))
    l1b=sum(abs(WE[a].get(g,0)-WE[b].get(g,0)) for g in set(WE[a])|set(WE[b]))
    GRAD.append({'edge_id':k,'vertices':[a,b],'semantics':[SEM[a],SEM[b]],'classes':[K[a],K[b]],'bind_length_mm':float(BL[k]),'FIELD_A_dominants':[dom(WB[a]),dom(WB[b])],'FIELD_B_dominants':[dom(WE[a]),dom(WE[b])],'FIELD_A_abs_group_jump':ja,'FIELD_B_abs_group_jump':jb,'FIELD_A_L1_jump':l1a,'FIELD_B_L1_jump':l1b,'L1_gradient_increase':l1b-l1a,'first_web_boundary':(a in WEB)!=(b in WEB)})
GRAD.sort(key=lambda x:(-x['L1_gradient_increase'],x['edge_id']))
for edge in GRAD:
    a,b=edge['vertices']; k=edge['edge_id']
    edge['R1E_six_pose_stretch']={c:float(np.linalg.norm(np.array(p['posed'][a])-p['posed'][b])*1000/BL[k]) for c,p in R['poses'].items()}
    edge['severe_in_poses']=[c for c,r in edge['R1E_six_pose_stretch'].items() if r>5 and BL[k]>=3]
    edge['collar_topology_level']=('LEVEL_0_EXACT_COLLAR' if k in BOUND else 'LEVEL_1_COLLAR_VERTEX_INCIDENT' if a in C0 or b in C0 else 'LEVEL_2_COLLAR_ONE_RING' if a in C1 or b in C1 else 'LEVEL_3_COLLAR_TWO_RING' if a in C2 or b in C2 else 'WEB_TRANSITION_OUTSIDE_C012')
dump('R1E_ENDPOINT_WEIGHT_FIELD_CONTINUITY_AUDIT.json',{'FIELD_A':'R1B original full field','FIELD_B':'R1E current full field','FIELD_C':R['first_web_approved_weights'],'R1B_collar_dominant_counts':dict(Counter(dom(WB[v]) for v in C0)),'R1E_collar_dominant_counts':dict(Counter(dom(WE[v]) for v in C0)), 'new_WRIST_heavy_vertices':[v for v in sorted(DOMAIN) if WE[v].get('WRIST_R',0)>=.9 and WB[v].get('WRIST_R',0)<.5], 'edge_gradients':GRAD,'semantic_caution':'A longitudinal projection of non-tubular web/thenar tissue can return a distal arc. Edge5879 cannot be anatomically called a distal tube from this proxy alone.'})

RULES={
 'INDEX_ROOT_DOMINANT_TISSUE':{'candidate_allowed':['WRIST_R','INDEX_MCP_R','INDEX_PIP_R'],'thumb_base_extension':'UNRESOLVED_FOR_EXACT_COLLAR','basis':'index proximal-tube location and full R1B history; PIP transition exists, while DIP residue has no root role'},
 'COLLAR_THUMB_SIDE_ANATOMY_UNRESOLVED':{'candidate_allowed':None,'observed_historical_groups':['WRIST_R','INDEX_MCP_R','INDEX_PIP_R'],'thumb_base_extension':'UNRESOLVED','basis':'frozen THUMB ownership does not establish distal/base tissue identity; no invented mapping or new approval'},
 'FIRST_WEB_ADJACENT_ROLE_REVIEW':{'candidate_allowed':['WRIST_R','INDEX_MCP_R','THUMB_CMC_R','THUMB_MCP_R'],'thumb_base_extension':'SUPPORTED_AS_LOCAL_ROLE_CANDIDATE_PENDING_HUMAN_REVIEW','basis':'direct adjacency to approved mixed first-web and measured neighboring thumb-base fields; local boundary continuity, not collar transfer'},
 'PALM_ANCHOR_TISSUE':{'candidate_allowed':['WRIST_R'],'conditional_groups':['THUMB_CMC_R'],'thumb_base_extension':'CMC_ONLY_IF_LOCAL_EXISTING_PRECEDENT_AND_CONTINUOUS_ROLE','basis':'historical wrist anchor; remote MCP/thumb drag not justified'},
 'INDEX_SHAFT_PROTECTED':{'candidate_allowed':['INDEX_MCP_R','INDEX_PIP_R','INDEX_DIP_R'],'thumb_base_extension':'NO','basis':'preserve existing index chain shaft field; DIP allowance here does not apply to collar'},
 'APPROVED_DISTAL_CAP_FROZEN':{'candidate_allowed':['THUMB_IP_R'],'constraint':'THUMB_IP_R=1.0; immutable'},
 'APPROVED_NAIL_FROZEN':{'candidate_allowed':'EXISTING_FROZEN_VECTOR','constraint':'immutable'},
 'APPROVED_FIRST_WEB_FROZEN':{'candidate_allowed':['WRIST_R','THUMB_CMC_R','THUMB_MCP_R','INDEX_MCP_R'],'constraint':'existing vector immutable; THUMB_IP_R=0'}
}
envelope=['Keep all existing first-web, cap, nails and CMC-cage fields frozen.', 'Where tissue identity is verified as shared web/base, thumb-base influence follows adjacency and regional role, decaying toward independent index tube and toward wrist on palm anchors.', 'The 10–16-edge remote exact collar is outside this locally evidenced envelope until its body-side tissue identity and anatomical correspondence are reviewed.', 'Maintain an INDEX_MCP deformation degree of freedom on index-root tissue; never bind the entire collar to thumb groups.', 'Each collar pair needs dynamically compatible local deformation; do not impose identical vectors solely from digit ownership.', 'No numerical percentages or per-vertex assignments are approved; sensitivity fractions have no authority.']
dump('R1E_ENDPOINT_ALLOWED_GROUP_AUTHORITY_PROPOSAL.json',{'name':'ENDPOINT_WEIGHT_ALLOWED_GROUP_AUTHORITY_R1','status':'UNRESOLVED','human_review_branch':'C','regional_rules':RULES,'envelope':envelope,'THUMB_IP_collar_allowed':False,'INDEX_DIP_collar_allowed':False,'mixed_CMC_exact_collar_supported':'UNRESOLVED','mixed_MCP_exact_collar_supported':'UNRESOLVED','local_web_thumb_base_role_supported':True,'no_production_authority_granted':True})

POSED={c:np.array(p['posed']) for c,p in R['poses'].items()}
def T(c,g):return np.array(R['poses'][c]['transforms'][g])
def move(c,g,v):return (T(c,g)@np.r_[V[v],1])[:3]
PAIRS=[]
for k in BOUND:
    a,b=E[k]; ratios={c:float(np.linalg.norm(p[a]-p[b])*1000/BL[k]) for c,p in POSED.items()}
    PAIRS.append({'edge_id':k,'vertices':[a,b],'classes':[K[a],K[b]],'bind_length_mm':float(BL[k]),'R1B_vectors':[WB[a],WB[b]],'R1E_vectors':[WE[a],WE[b]],'identical_R1B_vectors':WB[a]==WB[b],'identical_R1E_vectors':WE[a]==WE[b],'R1E_six_pose_ratios':ratios,'rule':'B_APPROXIMATE_EFFECTIVE_TRANSFORM_COMPATIBILITY_WITH_HARD_DYNAMIC_CONSTRAINTS','rule_reason':'an actual finite edge joins distinct tissue points; shared transforms suffice to preserve length, but identical transforms are not anatomically necessary for a continuous deforming surface.'})
dump('R1E_EXACT_COLLAR_PAIR_TRANSFORM_RULE_AUDIT.json',{'candidate_rule':'B','identical_effective_transform_required':False,'identical_transform_is_sufficient':True,'R1E_max_ratio':max(x for p in PAIRS for x in p['R1E_six_pose_ratios'].values()),'hard_constraints':{'retain_existing_severe_gate':'>5x AND bind >=3 mm','retain_existing_tear_gate':'>3x AND posed >5 mm','future_requirement':'future independent INDEX_MCP flex and opposition combinations must constrain any implemented candidate; not tested in this read-only round'},'same_six_poses_not_general_proof':True,'pairs':PAIRS})

# Dijkstra retains exact unrounded bind lengths; all 9x16 index endpoints and 9x32 collar endpoints.
def dij(s):
    d={s:0}; pred={}; q=[(0,s)]
    while q:
        dd,v=heapq.heappop(q)
        if dd!=d[v]:continue
        for u in sorted(ADJ[v]):
            nd=dd+float(np.linalg.norm(V[v]-V[u])*1000)
            if nd<d.get(u,math.inf):d[u]=nd;pred[u]=v;heapq.heappush(q,(nd,u))
    return d,pred
DI={s:dij(s) for s in sorted(CAP)}
IDX=sorted(v for v in C0 if R3[v]=='INDEX')
PATHS=[{'cap_vertex':a,'collar_vertex':b,'L_bind_path_mm':DI[a][0][b]} for a in sorted(CAP) for b in IDX]
ALLPATHS=[{'cap_vertex':a,'collar_vertex':b,'L_bind_path_mm':DI[a][0][b]} for a in sorted(CAP) for b in sorted(C0)]
FAMILIES=[('WRIST+THUMB_CMC','WRIST_R','THUMB_CMC_R'),('WRIST+THUMB_MCP','WRIST_R','THUMB_MCP_R'),('INDEX_MCP+THUMB_CMC','INDEX_MCP_R','THUMB_CMC_R'),('INDEX_MCP+THUMB_MCP','INDEX_MCP_R','THUMB_MCP_R'),('THUMB_CMC+THUMB_MCP','THUMB_CMC_R','THUMB_MCP_R')]
SENS=[]
for name,g0,g1 in FAMILIES:
    for c in ['TH_MCP_45','CMC_OPP_30','CMC_MCP_L3','FULL_OPP_L3']:
        for frac in [0,.1,.2,.3,.4,.5]:
            pts={b:(1-frac)*move(c,g0,b)+frac*move(c,g1,b) for b in C0}
            def values(paths):return [{'cap_vertex':p['cap_vertex'],'collar_vertex':p['collar_vertex'],'L_bind_path_mm':p['L_bind_path_mm'],'posed_endpoint_separation_mm':float(np.linalg.norm(POSED[c][p['cap_vertex']]-pts[p['collar_vertex']])*1000),'strict_bound':float(np.linalg.norm(POSED[c][p['cap_vertex']]-pts[p['collar_vertex']])*1000/p['L_bind_path_mm'])} for p in paths]
            vals=values(PATHS); allvals=values(ALLPATHS)
            worst=max(vals,key=lambda p:p['strict_bound']); worstall=max(allvals,key=lambda p:p['strict_bound'])
            SENS.append({'family':name,'base_group':g0,'added_group':g1,'parameter_fraction':frac,'parameter_definition':'second-group fraction; CMC+MCP family has 100% total thumb influence at every sample','total_thumb_influence':1.0 if g0.startswith('THUMB') else frac,'pose':c,'max_strict_bound_144_index_pairs':worst['strict_bound'],'worst_index_pair':worst,'max_strict_bound_288_all_collar_pairs':worstall['strict_bound'],'collar_mean_displacement_mm':float(np.mean([np.linalg.norm(pts[b]-V[b])*1000 for b in C0])),'collar_max_displacement_mm':float(max(np.linalg.norm(pts[b]-V[b])*1000 for b in C0)), 'collar_endpoint_trajectories':[{'vertex_id':b,'posed_position_mm':(pts[b]*1000).tolist(),'displacement_mm':float(np.linalg.norm(pts[b]-V[b])*1000)} for b in sorted(C0)],'all_144_index_pair_bounds':vals})
ZERO={c:next(x['max_strict_bound_144_index_pairs'] for x in SENS if x['family']=='WRIST+THUMB_CMC' and x['pose']==c and x['parameter_fraction']==0) for c in POSED if c not in ['TH_IP_30','TH_IP_45']}
old=json.loads((FEAS/'R1E_STRICT_GEOMETRIC_BOUND_AUDIT.json').read_text(encoding='utf-8'))
dump('R1E_ENDPOINT_SENSITIVITY_AUDIT.json',{'formula':'POSED_ENDPOINT_SEPARATION / exact unrounded BIND_PATH_LENGTH','distal_cap_kept_immutable':True,'evaluation':'hypothetical algebraic LBS on exported bone matrices; no skin-weight mutation even in Blender memory','samples':SENS,'zero_thumb_strict_bound_144_pairs':ZERO,'prior_10_shortest_path_bound':{c:old['per_pose'][c]['max_STRICT_LOWER_BOUND'] for c in ZERO},'stationary_groups_in_all_six_poses':{c:p['stationary_group_identity_errors'] for c,p in R['poses'].items()},'interpretation':'A lower bound below 5 is necessary, not sufficient, for passing edge gates. Uniform virtual mixtures are diagnostic families, not a regional weight field, not anatomy, and not authorization. Full 288-pair bounds additionally include body-side THUMB collar endpoints.','legal_authority_path_without_cap_change':'UNPROVEN_UNTIL_REMOTE_COLLAR_ANATOMY_IS_RESOLVED'})

dump('R1E_FUTURE_INDEX_MOTION_COMPATIBILITY_AUDIT.json',{'verdict':'CONDITIONAL_STRUCTURAL_COMPATIBILITY_ONLY; EXACT_COLLAR_AUTHORITY_UNRESOLVED','index_animation_run':False,'analysis':'For normalized LBS, with thumb bones bind and INDEX_MCP independently moving, the index-driven displacement term is w_INDEX_MCP*(T_INDEX-I)*x. A regional mixture retaining index drive permits index-root freedom. Replacing the entire collar with thumb-only drive removes that degree of freedom. INDEX_PIP transitions must retain their anatomically proximal role. Shared skin can interpolate, while shaft/nail and frozen authorities must retain independent drives.','sensitivities':[{'family':n,'index_MCP_fraction': [1-f for f in [0,.1,.2,.3,.4,.5]] if a=='INDEX_MCP_R' else [0]*6,'verdict':'retains INDEX_MCP freedom but not validated anatomy' if a=='INDEX_MCP_R' else 'no independent index drive in this simplified diagnostic family; cannot be a blanket root authority'} for n,a,b in FAMILIES],'constraints':['preserve index shaft and nail field','preserve first-web and CMC-cage locality','prohibit wholesale thumb-binding of the collar','preserve palm anchor convergence','require future INDEX_MCP flex + combined opposition qualification after human approval'],'no_dynamic_compatibility_PASS_claim':True})

EA=json.loads((FEAS/'R1E_EDGE5879_FORENSIC_AUDIT.json').read_text(encoding='utf-8'))
a,b=E[5879]
ER={c:{'R1E_ratio':float(np.linalg.norm(p[a]-p[b])*1000/BL[5879]),'R1B_ratio_analytical_LBS':float(np.linalg.norm(sum((move(c,g,a)*w for g,w in WB[a].items()),np.zeros(3))/sum(WB[a].values())-sum((move(c,g,b)*w for g,w in WB[b].items()),np.zeros(3))/sum(WB[b].values()))*1000/BL[5879])} for c,p in POSED.items()}
dump('R1E_EDGE5879_AUTHORITY_CONTEXT_AUDIT.json',{'edge_id':5879,'vertices':[a,b],'R3':[R3[a],R3[b]],'historical_semantics':[SEM[a],SEM[b]],'true_tissue_label_caution':'THUMB_DISTAL is a longitudinal projection proxy here, not anatomical proof; first-web adjacency plus MCP historical drive defines the local continuity role.','weights_R1B':[WB[a],WB[b]],'weights_R1E':[WE[a],WE[b]],'ratios':ER,'first_web_neighbor':b in WEB,'graph_to_exact_collar':[GC[a],GC[b]],'FIELD_A_group_jump_MCP':abs(WB[a].get('THUMB_MCP_R',0)-WB[b].get('THUMB_MCP_R',0)),'FIELD_B_group_jump_MCP':abs(WE[a].get('THUMB_MCP_R',0)-WE[b].get('THUMB_MCP_R',0)),'verdict':'WEIGHT_TRANSITION_PARTITIONING_DEFECT','binding_evidence':True,'mesh_limit':False,'does_not_prove_exact_collar_thumb_authority':True})
print('AUDITS READY',classcounts,'domain',len(C0),len(C1),len(C2),len(DOMAIN),'zero',ZERO,flush=True)

# Deterministic standalone scientific maps from measured mesh; two viewpoints per map.
REND=AUD/'renders'; REND.mkdir(exist_ok=True)
FONT=Path('C:/Windows/Fonts/arial.ttf'); BOLD=Path('C:/Windows/Fonts/arialbd.ttf')
def font(n,b=False):return ImageFont.truetype(str(BOLD if b else FONT),n)
BG='#101721'; FG='#e9edf3'; MUT='#a8b6c8'
COLORS={'INDEX_ROOT_DOMINANT_TISSUE':'#4fa9ff','COLLAR_THUMB_SIDE_ANATOMY_UNRESOLVED':'#eea954','FIRST_WEB_ADJACENT_ROLE_REVIEW':'#49dcb7','PALM_ANCHOR_TISSUE':'#bf86f1','APPROVED_DISTAL_CAP_FROZEN':'#f77883','APPROVED_NAIL_FROZEN':'#ff8dbc','INDEX_SHAFT_PROTECTED':'#637cff','APPROVED_FIRST_WEB_FROZEN':'#49dcb7'}
def start(title,subtitle):
    im=Image.new('RGB',(1800,1100),BG); d=ImageDraw.Draw(im);d.text((38,25),title,font=font(30,True),fill=FG);d.text((38,70),subtitle,font=font(20),fill=MUT)
    return im,d
def project(vs,rect,focus, direction):
    dr=np.array(direction,dtype=float);dr/=np.linalg.norm(dr);up=np.array([0,0,1.]);rt=np.cross(dr,up);rt/=np.linalg.norm(rt);uu=np.cross(rt,dr)
    cen=np.mean(V[list(focus)],axis=0); q=vs-cen; xyz=np.column_stack((q@rt,-q@uu,q@dr)); fp=xyz[list(focus),:2]
    span=np.maximum(np.ptp(fp,axis=0),.006)*1.22; scale=min((rect[2]-rect[0])/span[0],(rect[3]-rect[1])/span[1]); mid=(fp.min(axis=0)+fp.max(axis=0))/2
    xy=(xyz[:,:2]-mid)*scale+np.array([(rect[0]+rect[2])/2,(rect[1]+rect[3])/2]);return xy,xyz[:,2]
def panel(d,rect,focus,markers,direction=(.92,.25,.3),labels=False,highlight=None):
    xy,depth=project(V,rect,focus,direction)
    d.rectangle(rect,fill='#16212d',outline='#34485d')
    # Actual mesh edges provide transparent geometry context; markers expose all selected vertices.
    for a,b in E:
        p,q=xy[a],xy[b]
        if all(rect[0]<=z[0]<=rect[2] and rect[1]<=z[1]<=rect[3] for z in [p,q]):d.line([tuple(p),tuple(q)],fill='#344454',width=1)
    for k in BOUND:
        a,b=E[k];p,q=xy[a],xy[b]
        if all(rect[0]<=z[0]<=rect[2] and rect[1]<=z[1]<=rect[3] for z in [p,q]):d.line([tuple(p),tuple(q)],fill='#f4ef9b',width=3)
    if highlight:
        for k in highlight:
            a,b=E[k]; d.line([tuple(xy[a]),tuple(xy[b])],fill='#ff637c',width=5)
    for v,col in sorted(markers.items()):
        x,y=xy[v]
        if rect[0]+5<=x<=rect[2]-5 and rect[1]+5<=y<=rect[3]-5:
            rr=6 if v in C0 else 4;d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=col,outline=BG)
            if labels:d.text((x+7,y-9),str(v),font=font(13),fill=FG)
def legend(d,items,y=990):
    x=40
    for label,col in items:
        d.rectangle((x,y+5,x+15,y+20),fill=col); d.text((x+24,y),label,font=font(18),fill=FG); x+=len(label)*10+62
def save(im,name):im.save(REND/name);print('FIGURE',name,flush=True)
def twoview(name,title,subtitle,focus,markers,items,labels=False,highlight=None):
    im,d=start(title,subtitle)
    panel(d,(35,130,880,950),focus,markers,labels=labels,highlight=highlight)
    panel(d,(920,130,1765,950),focus,markers,direction=(-.6,.8,.35),labels=labels,highlight=highlight)
    d.text((50,105),'View A',font=font(16),fill=MUT);d.text((940,105),'View B',font=font(16),fill=MUT)
    legend(d,items);d.text((40,1045),'Bind geometry | yellow lines = exact 16 R3 edges | scientific evidence map; no production modifications',font=font(18),fill=MUT)
    save(im,name)
twoview('R1E_ENDPOINT_REVIEW_DOMAIN_MAP.png','Endpoint review domain: local collar and separate web transition','Disjoint C0/C1/C2 graph rings; direct first-web neighbors included. Frozen cap/nail overlap is review context only.',DOMAIN|WEB,{**{v:'#f5ee9b' for v in C0},**{v:'#6db5ff' for v in C1},**{v:'#ba8dfa' for v in C2},**{v:'#42d9b5' for v in WEBADJ},**{v:'#f67c85' for v in WEB}},[('C0: 32','#f5ee9b'),('C1: '+str(len(C1)),'#6db5ff'),('C2: '+str(len(C2)),'#ba8dfa'),('Web-adjacent','#42d9b5'),('Frozen web','#f67c85')])
twoview('R1E_COLLAR_ANATOMICAL_CLASSIFICATION.png','Collar classification: evidence confidence differs across the interface','Blue: index-side proximal tube. Orange: R3-THUMB body side, tissue identity unresolved; no forced shared-web class.',C0|C1,{v:COLORS[K[v]] for v in C0},[('Index root: 16',COLORS['INDEX_ROOT_DOMINANT_TISSUE']),('Body-side unresolved: 16',COLORS['COLLAR_THUMB_SIDE_ANATOMY_UNRESOLVED'])],labels=True)
GCO={'WRIST_R':'#b98ff5','INDEX_MCP_R':'#4fa9ff','THUMB_MCP_R':'#49dcb7','THUMB_CMC_R':'#e7c661','THUMB_IP_R':'#f77883','INDEX_PIP_R':'#4674cb'}
im,d=start('R1B vs R1E collar weight field','Actual dominant-group map; same bind geometry. Full weight vectors and group gradients are supplied in JSON.')
panel(d,(35,140,880,955),C0|C1|C2,{v:GCO.get(dom(WB[v]),'#8895a3') for v in C0|C1|C2})
panel(d,(920,140,1765,955),C0|C1|C2,{v:GCO.get(dom(WE[v]),'#8895a3') for v in C0|C1|C2})
d.text((45,110),'FIELD A / R1B: 32 collar INDEX_MCP dominant',font=font(20),fill=FG);d.text((930,110),'FIELD B / R1E: 32 collar WRIST dominant',font=font(20),fill=FG)
legend(d,[(g.replace('_R',''),co) for g,co in list(GCO.items())[:5]])
save(im,'R1B_VS_R1E_COLLAR_WEIGHT_FIELD.png')
twoview('R1E_FIRST_WEB_COLLAR_TRANSITION_MAP.png','First-web boundary: R1E-generated WRIST islands and MCP gradient','The distant collar is not the first-web band. Red line: edge5879; new WRIST-heavy vertices shown in orange.',DOMAIN|WEB,{**{v:'#49dcb7' for v in WEB},**{v:'#eea954' for v in DOMAIN if WE[v].get('WRIST_R',0)>=.9 and WB[v].get('WRIST_R',0)<.5},**{v:'#f5ee9b' for v in C0}},[('Frozen web','#49dcb7'),('New WRIST-heavy','#eea954'),('Exact collar','#f5ee9b'),('Edge5879','#ff637c')],highlight=[5879])
precvs={x['vertex_id'] for x in PC['vertices']+PM['vertices']}
twoview('R1E_THUMB_CMC_MCP_EXISTING_INFLUENCE_PRECEDENT.png','Existing cross-region thumb influence: scope matters','Frozen R1B evidence on non-THUMB or approved shared web. No CMC/MCP weights occur on R3-INDEX or exact collar.',precvs|C0,{v:('#e7c661' if WB[v].get('THUMB_CMC_R',0)>WB[v].get('THUMB_MCP_R',0) else '#49dcb7') for v in precvs},[('CMC > MCP','#e7c661'),('MCP >= CMC','#49dcb7'),('Exact collar outline','#f5ee9b')])
focus={a,b}|ADJ[a]|ADJ[b]|neigh(ADJ[a]|ADJ[b])
twoview('R1E_EDGE5879_AUTHORITY_CONTEXT.png','Edge5879: binding weight-transition partitioning defect','v1551 MCP 0.9684 -> 0.0600 / WRIST 0.9400; v3125 frozen MCP 1.0. L3 R1E stretch ~11.041x.',focus,{v:('#49dcb7' if v in WEB else GCO.get(dom(WE[v]),'#8895a3')) for v in focus},[('Frozen web / MCP','#49dcb7'),('WRIST','#b98ff5'),('Edge5879','#ff637c')],labels=True,highlight=[5879])
twoview('R1E_ENDPOINT_ALLOWED_GROUP_PROPOSAL_MAP.png','Allowed-group proposal: exact collar remains unresolved','Local web proposal W/I_MCP/T_CMC/T_MCP; index root W/I_MCP/I_PIP; orange region has no new authority.',DOMAIN|WEB,{v:COLORS.get(K[v],'#8291a3') for v in DOMAIN|WEB},[('Index-root candidate','#4fa9ff'),('Unresolved','#eea954'),('Local shared-web role','#49dcb7'),('Frozen cap','#f77883')])
im,d=start('Endpoint sensitivity: strict bound is a diagnostic, not authority','144 cap-to-INDEX-collar pairs | unchanged cap | max separation / exact shortest bind-path length')
LINECO=['#e7c661','#49dcb7','#e89ad3','#72aaff','#ff7e7e']
for i,c in enumerate(['TH_MCP_45','CMC_OPP_30','CMC_MCP_L3','FULL_OPP_L3']):
    x0=70+(i%2)*880; y0=160+(i//2)*380; x1=x0+760;y1=y0+280
    d.text((x0,y0-36),c,font=font(24,True),fill=FG)
    for tick in [0,2,4,5,6,8]:
        yy=y1-tick/8*(y1-y0);d.line([(x0,yy),(x1,yy)],fill='#7b6170' if tick==5 else '#2a3949',width=2 if tick==5 else 1);d.text((x0-35,yy-10),str(tick),font=font(16),fill=MUT)
    for tick in range(6):
        xx=x0+tick/5*(x1-x0);d.text((xx-15,y1+10),str(tick*10)+'%',font=font(16),fill=MUT)
    for j,(fam,g0,g1) in enumerate(FAMILIES):
        ss=sorted([r for r in SENS if r['family']==fam and r['pose']==c],key=lambda r:r['parameter_fraction'])
        coords=[(x0+r['parameter_fraction']/.5*(x1-x0),y1-r['max_strict_bound_144_index_pairs']/8*(y1-y0)) for r in ss]
        d.line(coords,fill=LINECO[j],width=4)
        for x,y in coords:d.ellipse((x-4,y-4,x+4,y+4),fill=LINECO[j])
legend(d,[(n,LINECO[i]) for i,(n,a,b) in enumerate(FAMILIES)],y=980)
d.text((40,1030),'X = second-group fraction. CMC+MCP curve has 100% total thumb influence; it is not the 0% thumb baseline.',font=font(20),fill=MUT)
d.text((40,1060),'No fraction is approved. Bound <5 does not prove a smooth field, index stability, or legal anatomical authority.',font=font(20),fill=MUT)
save(im,'R1E_ENDPOINT_SENSITIVITY_STRICT_BOUND.png')

# Hash validation is performed after figures. Include the entire protected evidence folders and all existing blends.
before=json.loads((AUD/'R1E_ENDPOINT_FROZEN_HASHES_BEFORE.json').read_text(encoding='utf-8'))
after={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in before}
newblend=sorted(str(p.relative_to(ROOT)).replace('\\','/') for p in ROOT.rglob('*.blend') if str(p.relative_to(ROOT)).replace('\\','/') not in before)
assert before==after and not newblend
dump('R1E_ENDPOINT_FROZEN_HASH_VERIFICATION.json',{'before_hashes':before,'after_hashes':after,'all_equal':True,'protected_file_count':len(before),'new_blend_files':newblend})
status={'human_review_branch':'C','ENDPOINT_WEIGHT_AUTHORITY_R1':'UNRESOLVED','ENDPOINT_WEIGHT_ALLOWED_GROUP_AUTHORITY_R1':'UNRESOLVED','NEXT':'NARROW_ANATOMICAL_EVIDENCE_REVIEW','STOP':'WAITING_FOR_HUMAN_REVIEW','class_counts':classcounts,'domain_counts':{'C0':len(C0),'C1':len(C1),'C2':len(C2),'extra_web_neighbors':len(WEBADJ-C0-C1-C2),'total':len(DOMAIN)},'R1B_collar_dominants':dict(Counter(dom(WB[v]) for v in C0)),'R1E_collar_dominants':dict(Counter(dom(WE[v]) for v in C0)), 'existing_THUMB_CMC_cross_region_precedent':PC['exists'],'existing_THUMB_MCP_cross_region_precedent':PM['exists'],'exact_collar_mixed_CMC_supported':'UNRESOLVED','exact_collar_mixed_MCP_supported':'UNRESOLVED','exact_collar_identical_transform_required':False,'THUMB_IP_collar_allowed':False,'INDEX_DIP_collar_allowed':False,'edge5879':'WEIGHT_TRANSITION_PARTITIONING_DEFECT','zero_thumb_strict_bounds':ZERO,'legal_authority_path_reducing_bound_without_cap_change':'NOT_ESTABLISHED','CURRENT_MESH_SUPPORT_INSUFFICIENT_FOR_THIS_POSE_RANGE':'NOT_PROVEN','RETOPO_REQUIRED':'NO','retopo_authorized':False,'frozen_hashes_equal':True,'protected_file_count':len(before),'BLEND_FILES_WRITTEN':0,'WEIGHT_DELTA':0,'GEOMETRY_DELTA':0,'TOPOLOGY_DELTA':0,'BONE_DELTA':0,'JOINT_DELTA':0,'R3_AUTHORITY_DELTA':0,'DIGIT_OWNERSHIP_AUTHORITY_R3':'HUMAN_APPROVED_PER_CURRENT_USER_FREEZE','R3_EXACT_COLLAR':'PASS','EXACT_R3_COLLAR_TOPOLOGY':'NOT_A_FAILURE','CMC_CAGE_DYNAMIC_QUALIFICATION':'PASS_PER_CURRENT_USER_FREEZE','Stage6A_full_run':False,'Stage6B_full_run':False,'Stage6C_entered':False,'Stage5B_R1F_created':False,'runtime':R['runtime'],'evidence_limitations':['R3 historical files still say pending human review; current user instruction supplies HUMAN_APPROVED authority, historical files unchanged.','Arc-derived semantic labels are proxies and cannot establish biological tissue identity in contacting RSSF pose.','Cross-region thumb precedent exists on thenar/palm/web, but not on the remote exact collar or R3-INDEX.','Future index motion compatibility is static structural analysis only, no dynamic PASS.']}
dump('R1E_ENDPOINT_WEIGHT_AUTHORITY_REVIEW_STATUS.json',status)
summary=[]
for fam,g0,g1 in FAMILIES:
    values=[]
    for c in ['TH_MCP_45','CMC_OPP_30','CMC_MCP_L3','FULL_OPP_L3']:
        ss=[r for r in SENS if r['family']==fam and r['pose']==c]
        values.append(f"{ss[0]['max_strict_bound_144_index_pairs']:.4f} → {ss[-1]['max_strict_bound_144_index_pairs']:.4f}")
    summary.append('| '+fam+' | '+' | '.join(values)+' |')
report=f'''# R1E_ENDPOINT_WEIGHT_AUTHORITY_REVIEW

**Branch C — ENDPOINT_WEIGHT_AUTHORITY_R1 = UNRESOLVED. STOP — Human Review.**

Generated {R['generated_at']}. Read-only review of R1B/R1E, live R2A joint frames, R3 ownership and existing feasibility evidence. No production file, skin weight, mesh, bone, angle, first-web, CMC cage or distal-cap authority was modified. No R1F was created and no full Stage6A/6B or Stage6C was run.

## Evidence-led authority finding

Existing thumb-base mixed influence is supported in the already approved first-web and frozen thenar/palm fields. CMC cage and thumb-base fields are also separately inventoried; thumb-owned cage drive by itself is not cross-digit precedent. **That precedent does not establish exact-collar permission.** All 32 exact-collar vertices have first-web graph distance {min(GW[v] for v in C0)}–{max(GW[v] for v in C0)}, no direct first-web adjacency and no historical CMC/MCP thumb weights. The index-owned surface has zero CMC/MCP precedent. The frozen topological cut isolates the 217-vertex index sheet; its 16 collar vertices are index-root/proximal tube. The 16 R3-THUMB body-side vertices retain their approved ownership, but their actual soft-tissue role is unresolved: R1B historically drove them with INDEX groups, while the longitudinal thumb projection names them distal. Neither ownership nor arc projection resolves the tissue identity. No class named shared web or palm is forced into C0.

The nearest body-side collar approaches the approved thumb cap by a few mesh edges while remaining 10–16 edges from the approved web. This is an **anatomical correspondence uncertainty**, not a reopened R3 topology failure and not mesh insufficiency proof. The next narrow review should establish the biological deformation role of these body-side interface faces in the frozen asset using an anatomical surface reference and the measured 1/2-ring context. R3 labels and all frozen authorities must remain unchanged. Do not optimize a thumb percentage or create R1F while this evidence is unresolved.

## Measured domain and fields

* C0 {len(C0)}, C1 {len(C1)}, C2 {len(C2)}; C012 {len(C0|C1|C2)}; extra direct web neighbors {len(WEBADJ-C0-C1-C2)}; unique review domain {len(DOMAIN)}. Frozen cap/nails inside these rings are context, never candidates.
* C0 classes: INDEX_ROOT_DOMINANT_TISSUE 16; COLLAR_THUMB_SIDE_ANATOMY_UNRESOLVED 16. Each vertex has full float weight vectors, actual incident-face IDs and vertices, distances to joints, exact graph distances and 1/2-ring composition.
* R1B collar dominant: INDEX_MCP_R 32. R1E collar dominant: WRIST_R 32.
* FIELD_C is measured directly from R1A approved first-web weights; its 21 vectors exactly equal R1B and R1E. Allowed groups remain WRIST_R / THUMB_CMC_R / THUMB_MCP_R / INDEX_MCP_R; THUMB_IP_R=0.
* CMC cross-region precedent YES: {PC['non_thumb_surface_count']} non-THUMB vertices, {PC['first_web_count']} first-web vertices, {PC['index_owned_count']} R3-INDEX vertices. MCP precedent YES: {PM['non_thumb_surface_count']} non-THUMB vertices, {PM['first_web_count']} first-web vertices, {PM['index_owned_count']} R3-INDEX vertices. Positive values use >1e-6 to exclude float residue. Full IDs and frozen comparisons are in the precedent JSON; global precedent is not new approval.

## Local partitioning defect: edge5879

v1551↔v3125 remains THUMB/THUMB. v3125 is frozen first-web MCP=1. v1551 changes from MCP={WB[1551].get('THUMB_MCP_R',0):.6f} to MCP={WE[1551].get('THUMB_MCP_R',0):.6f}, WRIST={WE[1551].get('WRIST_R',0):.6f}. In CMC_MCP_L3, analytical R1B ratio is {ER['CMC_MCP_L3']['R1B_ratio_analytical_LBS']:.6f} and R1E ratio is {ER['CMC_MCP_L3']['R1E_ratio']:.6f}. MCP discontinuity increases from ~0.0316 to ~0.94. Verdict: **WEIGHT_TRANSITION_PARTITIONING_DEFECT**, binding evidence. It is 12 graph edges from exact collar and establishes a web-boundary defect, not a mesh limit or collar authority. The historical THUMB_DISTAL name is explicitly a proxy here: index arc=0, lateral thumb distance ~31.6 mm, first-web adjacency and historical MCP drive must be considered together.

## Candidate regional rules (not implementation approval)

| Region class | Candidate group role |
|---|---|
| INDEX_ROOT_DOMINANT_TISSUE | WRIST / INDEX_MCP / INDEX_PIP; thumb-base extension unresolved |
| COLLAR_THUMB_SIDE_ANATOMY_UNRESOLVED | No new allowed-group authority; historical INDEX field is evidence, not an approved replacement |
| FIRST_WEB_ADJACENT_ROLE_REVIEW | WRIST / INDEX_MCP / THUMB_CMC / THUMB_MCP local role candidate, subject to Human Review |
| PALM_ANCHOR_TISSUE | WRIST; CMC conditional on existing local precedent and continuous role |
| Approved first-web / cap / nails / CMC cage | Existing frozen vectors preserved |

THUMB_IP and INDEX_DIP are **not allowed on collar/root/shared-web candidates**. Tiny R1B DIP residue does not establish anatomical DIP authority. Cap IP=1 and legitimate index shaft DIP are separately frozen. Proposed envelopes follow actual shared tissue continuity, decay toward independent index-root and wrist anchors and never bind the whole collar to thumb. No per-vertex free parameters or numeric weight envelope is approved.

## Exact-pair transform rule

Candidate rule **B**: local effective deformation compatibility with existing hard severe/tear constraints. Identical effective transforms are sufficient to keep edge lengths fixed, but are not anatomically necessary for finite edges on deformable tissue. R1B pair weight vectors can differ while all their active groups remain bind in these six thumb-only poses. R1E exact-pair maximum remains {max(x for p in PAIRS for x in p['R1E_six_pose_ratios'].values()):.9f}. Future index motion must preserve index deformation freedom and dynamically constrain any future implementation after approval; this review does not declare future motion PASS or revise gates.

## Sensitivity, separate from authority

Exact unrounded Dijkstra paths, all 9×16 cap-to-INDEX-collar pairs; 9×32 all-collar bounds are also supplied. Endpoint A is always the actual unchanged evaluated cap. The analytical matrices are validated against Blender at cap and edge5879 within {max(p['LBS_validation_max_error_mm'] for p in R['poses'].values()):.7f} mm. All WRIST/INDEX matrices remain bind to float noise, so restoring R1B INDEX drive alone yields the same endpoint separation.

Zero-thumb maximum strict bound: **CMC_MCP_L3 {ZERO['CMC_MCP_L3']:.6f}; FULL_OPP_L3 {ZERO['FULL_OPP_L3']:.6f}**. These agree with the prior 10-expanded-shortest-path evidence; this review additionally covers every pair. The strict formula is separation / bind-path length; the old (cap_motion + path)/path claim is rejected.

| Diagnostic family | TH_MCP_45 | CMC_OPP_30 | CMC_MCP_L3 | FULL_OPP_L3 |
|---|---|---|---|---|
{chr(10).join(summary)}

Each entry is 0%→50% of the second group. The CMC+MCP family has 100% total thumb influence even at 0% MCP, and is not the zero-thumb baseline. CMC adds no motion under MCP-only flex; MCP includes CMC ancestor motion during opposition. All endpoint trajectories, displacement magnitudes and individual pair bounds are in the sensitivity JSON. A strict bound below 5 does not prove the existence of a passing field, and no sample approves an authority or percentage.

**A numerical cap-preserving path to lower endpoint bounds exists; a legal anatomical authority path at exact collar has not been established.** Correcting edge5879's local web transition alone cannot move the remote collar endpoint. It is not valid to declare branch A solely because a virtual mixture lowers the bound; branch B also requires a binding stationary/index-only anatomy decision, which is not available. Therefore branch C is the evidence-supported outcome.

## Static future index compatibility

Mixed regional fields retaining INDEX_MCP influence preserve an index-motion degree of freedom in LBS. WRIST+thumb-only and CMC+MCP-only families remove independent index drive at the collar and cannot be blanket root authorities. INDEX_MCP+thumb families retain 100%→50% index coefficient across the diagnostic samples, but anatomical extent and combined-motion deformation remain unqualified. Protect index shaft, nail/cap independence, first-web shape, palm convergence and CMC locality. No index animation was run.

## Anatomical literature and limits

A cadaver morphology study describes first-web skin as an irregular quadrilateral inclined toward the index side, supporting an actual shared region rather than a simple digit-exclusive skin role ([Measurement and observation of the first web space](https://pubmed.ncbi.nlm.nih.gov/39084025/)). A first-web flap study describes vascular communication serving thumb and index tissue ([The dorsal flap of the first web](https://pubmed.ncbi.nlm.nih.gov/12631482/)). These primary anatomical findings support shared first-web tissue conceptually. **They provide no bone-weight percentages or a correspondence of this project's remote C0 vertices.** The inference to regional skinning roles is a modeling inference, not a measured biological weight law. Project measurements and frozen region authorities control scope.

## Integrity and stop

All {len(before)} protected files have identical before/after SHA-256, including Stage5A R2A, Stage5B R1B/R1E directories, R3 authority/evidence, the full geometric-feasibility audit and all existing blend files. See R1E_ENDPOINT_FROZEN_HASH_VERIFICATION.json for complete hashes. No new blend exists. BLEND_FILES_WRITTEN=0; WEIGHT_DELTA=GEOMETRY_DELTA=TOPOLOGY_DELTA=BONE_DELTA=JOINT_DELTA=R3_AUTHORITY_DELTA=0. R3 approval comes from this round's explicit Human Review freeze; historical pending wording is preserved byte-for-byte. CMC cage PASS and approved distal cap remain binding.

CURRENT_MESH_SUPPORT_INSUFFICIENT_FOR_THIS_POSE_RANGE=NOT_PROVEN. RETOPO_REQUIRED=NO. RETOPO_AUTHORIZED=NO. ENDPOINT_WEIGHT_AUTHORITY_R1=UNRESOLVED. NEXT=NARROW_ANATOMICAL_EVIDENCE_REVIEW. **STOP — wait for Human Review.**
'''
(AUD/'R1E_ENDPOINT_WEIGHT_AUTHORITY_REVIEW_REPORT.md').write_text(report,encoding='utf-8')
print('COMPLETE BRANCH C; STOP; HASHES',len(before),'UNCHANGED',flush=True)
