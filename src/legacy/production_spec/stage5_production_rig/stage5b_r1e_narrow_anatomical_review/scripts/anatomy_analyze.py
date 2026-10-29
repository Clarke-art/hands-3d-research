"""Read-only static correspondence review. Offline numerical analysis and original figures.
No Blender API, pose arrays, deformation evaluation or production weight proposals.
"""
import sys
sys.dont_write_bytecode = True
import json, hashlib, heapq, math, textwrap, datetime
from pathlib import Path
from collections import Counter, deque
import numpy as np
from PIL import Image, ImageDraw, ImageFont

AUD = Path(__file__).resolve().parents[1]
ROOT = AUD.parents[2]
PREV = AUD.parent / 'stage5b_r1e_endpoint_authority_review'
R = json.loads((PREV / '_tmp/review_raw.json').read_text(encoding='utf-8'))
S = json.loads((AUD / '_tmp/anatomy_static_extract.json').read_text(encoding='utf-8'))
V = np.array(R['R1B']['v']); E = R['R1B']['edges']; F = R['R1B']['faces']
VP = np.array(S['historical']['STAGE4A_R2_PRE_RSSF']['vertices_world_m'])
LAB = R['R3']; OWN = LAB['R3']; BOUND = LAB['boundary_edges_R3']
C0 = {v for ei in BOUND for v in E[ei]}
BODY = sorted(v for v in C0 if OWN[v] == 'THUMB')
INDEX = sorted(C0 - set(BODY)); WEB = set(LAB['WEB']); CAP = set(LAB['CAP'])
assert len(BODY) == len(INDEX) == len(BOUND) == 16
ADJ = [set() for _ in V]; INC = [[] for _ in V]
for a, b in E: ADJ[a].add(b); ADJ[b].add(a)
for fi, face in enumerate(F):
    for v in face: INC[v].append(fi)
def neigh(ids): return set().union(*(ADJ[i] for i in ids))
C1 = neigh(C0) - C0; C2 = neigh(C1) - C0 - C1
PRECEDENT = json.loads((PREV/'R1E_EXISTING_CROSS_REGION_THUMB_INFLUENCE_PRECEDENT.json').read_text(encoding='utf-8'))
THENAR = {x['vertex_id'] for x in PRECEDENT['regional_neighborhood_census']['thenar_historical_proxy']['vertices']}
SEM = {x['vertex_id']:x['semantic_region'] for x in json.loads((PREV/'R1E_ENDPOINT_REVIEW_DOMAIN.json').read_text(encoding='utf-8'))['vertices']}
def unit(a): return a / max(float(np.linalg.norm(a)), 1e-20)
def normals(v):
    out = np.zeros_like(v)
    for f in F: np.add.at(out, f, np.cross(v[f], np.roll(v[f], -1, axis=0)).sum(axis=0))
    return out / np.maximum(np.linalg.norm(out, axis=1)[:,None], 1e-20)
NP = normals(VP); NV = normals(V)
# Fit the exact same pre-RSSF ring. This is an intrinsic surface plane, not a nearest-bone label.
ev, axes = np.linalg.eigh(np.cov(VP[BODY].T))
LP = axes[:,0] * np.sign(axes[2,0])
DP = unit(np.array([0.,1.,0.]) - LP * LP[1]); RP = unit(np.cross(DP, LP))
J = {g:np.array(p) for g,p in R['R2A_joints'].items()}
LI = unit(J['INDEX_PIP_R']-J['INDEX_MCP_R'])
DI = unit(np.array([0.,1.,0.])-LI*LI[1]); RI = unit(np.cross(DI,LI))
CNAMES = ['DORSAL','PALMAR','RADIAL','ULNAR']
CPA = np.array([DP,-DP,RP,-RP]); CIA = np.array([DI,-DI,RI,-RI])
GROUPS = {s:[] for s in CNAMES}
def graph_dist(seeds):
    d = {v:0 for v in seeds}; q = deque(sorted(seeds))
    while q:
        a=q.popleft()
        for b in sorted(ADJ[a]):
            if b not in d: d[b]=d[a]+1; q.append(b)
    return d
def geodesic(seeds):
    d=np.full(len(V),np.inf); parent={}; q=[]
    for v in seeds:d[v]=0.;heapq.heappush(q,(0.,v))
    while q:
        cost,a=heapq.heappop(q)
        if cost>d[a]:continue
        for b in sorted(ADJ[a]):
            c=cost+float(np.linalg.norm(V[a]-V[b])*1000)
            if c<d[b]:d[b]=c;parent[b]=a;heapq.heappush(q,(c,b))
    return d,parent
GD={n:graph_dist(ids) for n,ids in [('first_web',WEB),('distal_cap',CAP),('thenar_proxy',THENAR)]}
GE={n:geodesic(ids) for n,ids in [('first_web',WEB),('distal_cap',CAP),('thenar_proxy',THENAR)]}
GENERATED=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
def dump(name,obj):
    (AUD/name).write_text(json.dumps({'review':'NARROW_ANATOMICAL_EVIDENCE_REVIEW','generated_at':GENERATED,'read_only':True,**obj},indent=2,ensure_ascii=False),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

SOURCES = [
 dict(id='S1',title='Measurement and observation of the first web space based on morphology and clinical applications',authors=['Xuwei Zhu','Zhenglin Chi','Chenhao Ye','Rasheed Aaman Robinson','Zongwei Zhou','Liangfu Jiang','Lilian Zhang','Feiya Zhou','Yiheng Chen'],year=2024,journal='Journal of Plastic, Reconstructive & Aesthetic Surgery 96:123–128',institution='Wenzhou Medical University and collaborating institutions',url='https://pubmed.ncbi.nlm.nih.gov/39084025/',doi='10.1016/j.bjps.2024.07.014',pmid='39084025',evidence_type='Primary cadaver/morphology paper; limited accessible content',relevant_anatomy='Actual first-web skin morphology',level='LEVEL_C',classification='BACKGROUND_ACCESS_LIMITED',claim='Indexed primary record verifies the relevant morphology study. No numerical boundary or point-level assignment is taken from inaccessible full text.',limitations='PubMed direct open returned a browser challenge; primary indexed metadata inspected. Detailed anatomical figures/full methods were not available; this source cannot carry the authority decision.',concepts=['ANATOMICAL_CONTINUITY'],access='Indexed primary metadata only; inaccessible full text'),
 dict(id='S2',title='The dorsal flap of the first web',authors=['A. Pagliei','L. Rocchi','A. Tulli'],year=2003,journal='Journal of Hand Surgery (British and European Volume) 28(2):121–124',institution='Primary surgical publication',url='https://www.sciencedirect.com/science/article/abs/pii/S026676810200298X',doi='10.1016/S0266-7681(02)00298-X',pmid='12631482',evidence_type='Primary clinical flap series, 15 cases',relevant_anatomy='Dorsal first web; vascular communication involving index and thumb',level='LEVEL_C',classification='BACKGROUND_FOR_DEFORMATION',claim='A dorsal first-web flap can use regional vascular communication. Surgical flap survival establishes blood supply, not a native thumb-joint skin driver.',limitations='Flap transposition changes attachments. Vascular continuity is direct evidence for perfusion only; no native skin trajectory or exact collar mapping.',concepts=['VASCULAR_CONTINUITY'],access='Primary publisher abstract and clinical introduction'),
 dict(id='S3',title='Regional first web flap used to cover the amputated stump of the thumb',authors=['Kazufumi Sano','Kazumasa Kimura','Satoru Ozeki'],year=2012,journal='Journal of Plastic Surgery and Hand Surgery 46(2):128–131',institution='Primary surgical publication',url='https://pubmed.ncbi.nlm.nih.gov/22471263/',doi='10.3109/2000656X.2011.588453',pmid='22471263',evidence_type='Primary reconstructive clinical report',relevant_anatomy='Radiodorsal index MCP surface toward dorsal first web',level='LEVEL_B',classification='STRONG_INFERENCE_ADJACENT_REGION',claim='The reported flap donor extends from radiodorsal index MCP toward the dorsal first web. This establishes an adjacent surface corridor, not native CMC/MCP coupling at the model ring.',limitations='Donor design is at index MCP, whereas the model ring projects well along the proximal phalanx. Mobilization after surgery does not measure intact regional skin displacement.',concepts=['ANATOMICAL_CONTINUITY','SKIN_MOBILITY'],access='Primary indexed abstract'),
 dict(id='S4',title="The anatomy and function of Cleland’s ligaments",authors=['R. L. Zwanenburg','P. M. N. Werker','D. A. McGrouther'],year=2014,journal='Journal of Hand Surgery (European Volume) 39(5):482–490',institution='University Medical Center Groningen; University of Manchester',url='https://pubmed.ncbi.nlm.nih.gov/24305724/',full_text_url='https://pure.rug.nl/ws/files/118517525/The_anatomy_and_function_of_Cleland_s_ligaments.pdf',doi='10.1177/1753193413511944',pmid='24305724',evidence_type='Cadaver microdissection; 20 fresh-frozen digits and four Thiel-preserved fingers for dynamics',relevant_anatomy='Lateral digital skin anchors; proximal phalanx/PIP relationship',level='LEVEL_B',classification='STRONG_INFERENCE_DIGITAL_HOMOLOGY',claim='Lateral cutaneous attachments anchor digital skin through flexion and extension. Origins include phalangeal, tendon-sheath and extensor-associated fascia; fibre orientation and tension change with finger motion.',limitations='Fresh-frozen sample: six little, eight ring, six middle fingers; not an index/thumb sample. The mesh contains no dermis, fascia or ligament layers, so a surface vertex cannot be declared a specific ligament insertion.',concepts=['FASCIAL_CONTINUITY','SKIN_MOBILITY','DEFORMATION_COUPLING_LOCAL_DIGIT'],access='Primary full-text university PDF; methods, results and dynamics inspected'),
 dict(id='S5',title='Grayson Ligament: A Revised Description of its Anatomy and Function',authors=['Rinze L. Zwanenburg','Duncan A. McGrouther','Paul M. N. Werker'],year=2019,journal='Journal of Hand Surgery (American Volume) 44(4):341.e1–341.e6',institution='University Medical Center Groningen; University of Manchester',url='https://pubmed.ncbi.nlm.nih.gov/30170887/',full_text_url='https://pure.rug.nl/ws/portalfiles/portal/80559878/1_s2.0_S0363502317319688_main.pdf',doi='10.1016/j.jhsa.2018.07.002',pmid='30170887',evidence_type='20-digit cadaver microdissection plus Thiel-preserved hand dynamics',relevant_anatomy='Volar digital skin/fat and flexor-sheath trabecular network',level='LEVEL_B',classification='STRONG_INFERENCE_DIGITAL_HOMOLOGY',claim='A volar fascial network links tendon-sheath adventitia to skin and fat. Its orientation changes during finger flexion, permitting local fat-pad adaptation.',limitations='Long-finger analogy, not direct index/first-web thumb motion measurement. Does not identify an individual model skin vertex as Grayson tissue or distinguish CMC from MCP effects.',concepts=['FASCIAL_CONTINUITY','SKIN_MOBILITY','DEFORMATION_COUPLING_LOCAL_DIGIT'],access='Primary indexed abstract and university full text'),
 dict(id='S6',title='The dorsal wrinkle ligaments of the proximal interphalangeal joint',authors=['P. Law','D. A. McGrouther'],year=1984,journal='Journal of Hand Surgery (British Volume) 9(3):271–275',institution='Primary anatomical publication',url='https://pubmed.ncbi.nlm.nih.gov/6512362/',doi='10.1016/0266-7681(84)90040-8',pmid='6512362',evidence_type='Cadaver dorsal digital skin attachment study',relevant_anatomy='Dorsal PIP wrinkle/attachment apparatus',level='LEVEL_B',classification='STRONG_INFERENCE_ADJACENT_DIGITAL_SKIN',claim='Dorsal skin at the PIP has structured wrinkle attachments. This supports a local digital skin role as a candidate for nearby dorsal proximal-phalanx surface.',limitations='The model ring is proximal to PIP, not proven to coincide with a crease; sample does not register this specific index ring. No thumb opposition coupling measurement.',concepts=['ANATOMICAL_CONTINUITY','SKIN_MOBILITY'],access='Primary indexed abstract; author manuscript metadata cross-check'),
 dict(id='S7',title='Predictors of successful outcomes in first web space contracture release',authors=['Derek L. Masden','James P. Higgins'],year=2011,journal='Hand (New York) 6(1):50–55',institution='Primary clinical publication',url='https://pubmed.ncbi.nlm.nih.gov/22379438/',doi='10.1007/s11552-010-9294-4',pmid='22379438',evidence_type='Clinical functional outcomes after first-web contracture release',relevant_anatomy='First-web function in abduction/opposition',level='LEVEL_A',classification='DIRECT_REAL_FIRST_WEB_FUNCTION',claim='After first-web contracture release, restored abduction and persistent opposition deficits differ. Real first-web tissue matters functionally for opposition, but the study does not isolate native skin drivers.',limitations='Pathological/reconstructed webs, small follow-up sample; not normal skin tracking. No index-ring registration and no separation of CMC versus MCP contribution.',concepts=['SKIN_MOBILITY','FUNCTIONAL_RELATION_TO_OPPOSITION'],access='Primary indexed abstract'),
 dict(id='S8',title='Robust Identification of Three-Dimensional Thumb and Index Finger Kinematics With a Minimal Set of Markers',authors=['Raviraj Nataraj','Zong-Ming Li'],year=2013,journal='Journal of Biomechanical Engineering 135(9):091002',institution='Cleveland Clinic',url='https://pubmed.ncbi.nlm.nih.gov/23775305/',full_text_url='https://pmc.ncbi.nlm.nih.gov/articles/PMC3708711/',doi='10.1115/1.4024753',pmid='23775305',evidence_type='Six-subject thumb/index pinch kinematics study',relevant_anatomy='Skin-marker passive motion relative to skeletal kinematics',level='LEVEL_C',classification='BACKGROUND_MEASUREMENT_LIMITATION',claim='Skin-marker passive motion complicates skeletal kinematics. Fewer markers and nail clusters reduce artifacts; joint kinematics alone do not establish a local skin deformation field.',limitations='No absolute gold standard and no spatially resolved commissure/thenar skin-displacement map. It cannot authorize either thumb group at the collar.',concepts=['SKIN_MOBILITY','KINEMATICS_NOT_SURFACE_DRIVER_AUTHORITY'],access='Primary indexed abstract and PMC full text')
]
for source in SOURCES:
    source['commercial_use_relevance']='N/A — research citation only; no external figure or asset incorporated'
    source['exact_model_vertex_registration']=False
    source['exact_collar_deformation_authority_level']='NONE'
SOURCE_COUNTS=dict(Counter(s['level'] for s in SOURCES))
dump('ANATOMICAL_SOURCE_REGISTER.json',{'sources':SOURCES,'counts':SOURCE_COUNTS,'level_scope':'Levels apply to the narrow anatomical claim described, not to an exact model mapping. LEVEL_A source count is not a count of authorized vertices.','research_method':'Focused primary literature searches: first-web morphology/flaps/contracture function; lateral and volar digital attachments; dorsal PIP skin; skin-marker artifact. No ordinary 3D model, AI image, blog, forum or commercial illustration supplies anatomical authority.','access_limitations':['S1 cannot supply an inspected detailed boundary; explicitly downgraded to LEVEL_C.','No reviewed source maps normal skin displacement at these exact model points separately to CMC opposition and thumb MCP flexion.'],'excluded_scope_examples':['Tonkin 2015 web measurements concern second/third/fourth webs and are not first-web authority.','Secondary surgical reviews and commercial atlas pages were search leads only.']})

IDENTITY={
 'DORSAL':'Dorsal index proximal-phalanx integument; local digital gliding/wrinkle apparatus candidate, not a registered PIP crease',
 'PALMAR':'Volar index proximal-phalanx skin/fat with local fascial tether and adaptation candidate; not proven thenar anchor',
 'RADIAL':'Radial index proximal-phalanx lateral integument; possible commissure-facing extension remains unregistered',
 'ULNAR':'Ulnar index proximal-phalanx lateral integument; local digital cutaneous anchoring candidate'}
SUPPORT={'DORSAL':['S4','S6','S8'],'PALMAR':['S4','S5'],'RADIAL':['S3','S4','S7'],'ULNAR':['S4','S5']}
CONFLICT={
 'DORSAL':['A dorsal first-web flap exists, but a circumferential phalangeal ring is not its demonstrated MCP donor footprint.','Dorsal PIP attachments cannot be mapped exactly to a ring proximal to PIP.'],
 'PALMAR':['Volar digital surface and thenar skin are both soft tissues; continuity alone does not equate their drivers.','S5 studied other long fingers and cannot prove the index-specific fascial insertion.'],
 'RADIAL':['S3 donor corridor reaches radiodorsal index MCP; the present ring lies farther along the proximal phalanx.','No human commissure margin/skin crease registration exists, so some radial extension cannot be categorically excluded.'],
 'ULNAR':['General fascial continuity does not imply thumb opposition drive on the far side of the index tube.','S4/S5 long-finger homology does not prove a model-specific thumb coupling is zero.']}
ROWS=[]
seglen=float(np.linalg.norm(J['INDEX_PIP_R']-J['INDEX_MCP_R'])*1000)
for v in BODY:
    scores=CPA@NP[v]; order=np.argsort(scores)[::-1]; name=CNAMES[int(order[0])]; GROUPS[name].append(v)
    cur_scores=CIA@NV[v]; cur_name=CNAMES[int(np.argmax(cur_scores))]
    r=V[v]-J['INDEX_MCP_R']; t=float(r@LI*1000)
    landmark_dist={g:float(np.linalg.norm(V[v]-p)*1000) for g,p in J.items() if g in ['THUMB_CMC_R','THUMB_MCP_R','THUMB_IP_R','INDEX_MCP_R','INDEX_PIP_R']}
    distances={}
    for n,ids in [('first_web',WEB),('distal_cap',CAP),('thenar_proxy',THENAR)]:
        a=min(ids,key=lambda i:(float(np.linalg.norm(V[v]-V[i])),i))
        distances[n]={'closest_model_vertex':a,'euclidean_mm':float(np.linalg.norm(V[v]-V[a])*1000),'edge_graph_distance':GD[n][v],'surface_edge_geodesic_mm':float(GE[n][0][v]),'human_registration':'NOT_ESTABLISHED' if n!='distal_cap' else 'PROJECT_AUTHORITY_ONLY'}
    ROWS.append(dict(vertex_id=v,R3_ownership='THUMB',cluster=name,model_surface_location=IDENTITY[name],candidate_real_anatomical_structure=IDENTITY[name],bind_world_mm=(V[v]*1000).tolist(),pre_RSSF_world_mm=(VP[v]*1000).tolist(),surface_normal_bind=NV[v].tolist(),surface_normal_pre_RSSF=NP[v].tolist(),pre_intrinsic_direction_scores=dict(zip(CNAMES,map(float,scores))),cluster_margin=float(scores[order[0]]-scores[order[1]]),sector_boundary_caution=float(scores[order[0]]-scores[order[1]])<.2,current_live_index_frame_sector=cur_name,current_vs_pre_sector_agree=cur_name==name,local_index_coordinates_mm={'radial':float(r@RI*1000),'dorsal':float(r@DI*1000),'distal':t},MCP_to_PIP_axial_fraction=t/seglen,distance_to_joint_mm=landmark_dist,closest_skeletal_landmark=min(landmark_dist,key=landmark_dist.get),closest_anatomical_landmark='Actual crease/commissure/fascial attachment UNREGISTERED; skeletal distances are descriptive only',model_region_distances=distances,first_web_direct_neighbors=sorted(ADJ[v]&WEB),one_ring_vertices=sorted(ADJ[v]),incident_face_ids=INC[v],neighbor_semantic_context=dict(Counter(SEM.get(i,'OUTSIDE_PREVIOUS_REVIEW_DOMAIN') for i in ADJ[v])),historical_semantic=SEM.get(v),supporting_sources=SUPPORT[name],evidence_level='LEVEL_B',confidence={'model_location':'HIGH','circumferential_sector':'MEDIUM' if name!=cur_name or float(scores[order[0]]-scores[order[1]])<.2 else 'HIGH','human_regional_identity':'MEDIUM','exact_tissue_insertion':'UNRESOLVED','thumb_CMC_coupling':'UNRESOLVED','thumb_MCP_coupling':'UNRESOLVED'},conflicting_evidence=CONFLICT[name],thumb_CMC_authority='UNRESOLVED — NO NEW AUTHORITY',thumb_MCP_authority='UNRESOLVED — NO NEW AUTHORITY'))
CLUSTERS=[]
for name in CNAMES:
    ids=GROUPS[name]
    CLUSTERS.append(dict(cluster=name,vertex_ids=ids,vertex_count=len(ids),proposed_anatomical_identity=IDENTITY[name],identity_status='CANDIDATE_REGIONAL_CORRESPONDENCE',supporting_sources=SUPPORT[name],evidence_level='LEVEL_B',confidence='MEDIUM for regional identity; UNRESOLVED for driver authority',conflicting_evidence=CONFLICT[name],registered_human_tissue_boundary=False,allowed_new_thumb_groups=[],CMC_verdict='UNRESOLVED',MCP_verdict='UNRESOLVED'))
assert sorted(v for c in CLUSTERS for v in c['vertex_ids'])==BODY
dump('BODY_SIDE_COLLAR_ANATOMICAL_CLUSTER_AUDIT.json',{'body_vertex_ids':BODY,'index_side_vertex_ids':INDEX,'C0':sorted(C0),'C1':sorted(C1),'C2':sorted(C2),'R3_cut_set':[{'edge_id':i,'vertices':E[i]} for i in BOUND],'cluster_count':len(CLUSTERS),'cluster_counts':{k:len(v) for k,v in GROUPS.items()},'clustering_method':{'geometry_basis':'Identical vertex and polygon ordering in the pre-RSSF Stage4A R2 and current static R1B asset. PCA plane fitted to exact 16 pre-RSSF body vertices. The smallest eigenvector points distally; canonical +Y projected into plane is dorsal; dorsal cross distal is radial. Select largest signed area-weighted vertex-normal dot product among dorsal/palmar/radial/ulnar. No weight, R3 name, or nearest bone selects the sector.','tie_rule':'CNAMES order DORSAL, PALMAR, RADIAL, ULNAR; no equal scores occurred','PCA_eigenvalues_m2':ev.tolist(),'pre_frame':{'distal':LP.tolist(),'dorsal':DP.tolist(),'radial':RP.tolist()},'current_live_index_frame':{'distal':LI.tolist(),'dorsal':DI.tolist(),'radial':RI.tolist()},'frame_crosscheck':'Current frame uses live MCP→PIP geometry and projected canonical dorsal. Sector changes near an angular border are recorded; source/pre-RSSF sector is the primary assignment. Static mesh shape changed historically, so this is not a posed-motion experiment.','canonical_authority':'stage4a_r2/R2_AUDIT.json frame; docs/CANONICAL_HAND_POSE_SPEC_R1.md (Stage2 source axes differ).','anatomy_step':'PCA/normal sectors are geometric clusters. Literature-based candidate tissue roles are assigned separately; none is a histological segmentation.','weights_used_for_clustering':False,'neighbor_context':'C0/C1/C2 topology and approved WEB, frozen CAP, historical THENAR proxy checked. No direct web edge on any body vertex. The geodesic distance is descriptive and never used to reject a real commissure extension.'},'clusters':CLUSTERS,'vertices':ROWS})
INDEX_ROWS=[]
for v in INDEX:
    rel=V[v]-J['INDEX_MCP_R']
    INDEX_ROWS.append({'vertex_id':v,'R3_ownership':'INDEX','bind_world_mm':(V[v]*1000).tolist(),'surface_normal':NV[v].tolist(),'MCP_to_PIP_axial_fraction':float(rel@LI*1000/seglen),'first_web_graph_edges':GD['first_web'][v],'direct_web_neighbors':sorted(ADJ[v]&WEB),'candidate_anatomy':'Same index proximal-tube interface; counterpart ring','evidence_level':'LEVEL_B','new_thumb_authority':'NONE','reason':'No exact native thumb-driven skin registration or historical collar CMC/MCP precedent. Sensitivity need is not anatomical evidence.'})
dump('MODEL_ANATOMY_CORRESPONDENCE_AUDIT.json',{'ANATOMICAL_CORRESPONDENCE':'UNRESOLVED','regional_index_surface_correspondence':'STRONG_GEOMETRIC_CANDIDATE; finer shared-driver correspondence unresolved','clusters':CLUSTERS,'body_vertices':ROWS,'index_side_vertices':INDEX_ROWS,'landmarks':{'live_joint_world_mm':{g:(p*1000).tolist() for g,p in J.items() if g in ['THUMB_CMC_R','THUMB_MCP_R','INDEX_MCP_R','INDEX_PIP_R']},'first_web_model_vertices':sorted(WEB),'distal_cap_model_vertices':sorted(CAP),'thenar_proxy_model_vertices':sorted(THENAR),'thenar_proxy_scope':'Inherited descriptive arc/ownership proxy; NOT a human thenar boundary. It is displayed as context, not used as anatomical permission.','index_proximal_segment_length_mm':seglen},'first_web_correspondence_verdict':'UNRESOLVED for radial extension; no positive evidence for the whole circumferential ring','thenar_correspondence_verdict':'NOT_ESTABLISHED; a circumferential index phalangeal surface is not a demonstrated thenar footprint; physical continuity and motion transmission remain unmeasured','index_root_correspondence_verdict':'SUPPORTED_AS_REGIONAL_INDEX_PROXIMAL_INTEGUMENT_CANDIDATE (LEVEL_B); literal MCP-root label is imprecise, because axial location is farther toward PIP','independent_R1B_INDEX_anatomy_verdict':'Regional index association is geometrically plausible independently of weights. Exact INDEX_MCP field and exclusion of all transmitted thumb motion are not anatomically qualified.','concept_separation':{'ANATOMICAL_CONTINUITY':'S3 supplies adjacent MCP/web donor corridor; adjacency cannot register this ring.','VASCULAR_CONTINUITY':'S2 supports perfusion; it supplies no deformation authority.','FASCIAL_CONTINUITY':'S4/S5 support digital skin/fascial anchors by long-finger analogy; continuity is not a rigid driver assignment.','SKIN_MOBILITY':'S4/S5/S6 describe local finger skin adaptation; S7 functional first-web outcomes; S8 marker artifacts.','DEFORMATION_COUPLING':'No inspected primary source independently measures native CMC versus thumb MCP skin displacement at a corresponding exact collar site.'},'CMC_cross_region_evidence':{'real_web_function':'LEVEL_A via S7 for opposition-associated function, not an isolated CMC driver','candidate_radial_surface_transfer':'LEVEL_B via S3; incomplete correspondence','exact_body_collar_authority':'NONE / UNRESOLVED'},'MCP_cross_region_evidence':{'adjacent_surgical_corridor':'LEVEL_B via S3; not a native thumb MCP motion measurement','vascular_background':'LEVEL_C via S2','exact_body_collar_authority':'NONE / UNRESOLVED'},'why_branch_D_not_C':'Normal directions, topology and axial position strongly favor index integument. They do not register the true human commissure boundary or measure transmission through intact fascia. D avoids asserting a proven stationary/index-only role or zero thumb coupling from a geometric candidate alone.','manual_review_required':['Register an actual right-hand dorsal/palmar/radial surface reference with index MCP/PIP skin creases and true first commissure margin to these IDs.','Distinguish radial lateral digital integument from a commissure extension using those landmarks.','If a shared patch is identified, obtain native skin-motion evidence isolating CMC opposition from thumb MCP flexion before allowed-group authority.'],'registration_error_mm':None,'ownership_authority':'HUMAN_APPROVED; unchanged; surface-domain identity is not a musculoskeletal skin driver.'})

H=S['historical']; PROV=[]
for v in BODY:
    ws={tag:H[tag]['full_weights'][v] for tag in ['STAGE5B_R1','STAGE5B_R1A','STAGE5B_R1B']}
    assert ws['STAGE5B_R1']==ws['STAGE5B_R1A']==ws['STAGE5B_R1B']==R['R1B']['w'][v]
    PROV.append({'vertex_id':v,'historical_vectors':ws,'current_R1E_vector':R['R1E']['w'][v],'R1_to_R1A_to_R1B_exactly_identical':True,'R1B_dominant_group':max(ws['STAGE5B_R1B'],key=ws['STAGE5B_R1B'].get),'R1B_CMC_MCP_precedent':False,'anatomical_permission_from_historical_vector':False})
dump('BODY_SIDE_COLLAR_EXISTING_WEIGHT_PROVENANCE.json',{'vertices':PROV,'all_16_R1_R1A_R1B_vectors_identical':True,'initial_script':'production_spec/stage5_production_rig/stage5b_r1/scripts/s5b_r1_bind.py','initial_algorithm':{'ownership_selector':'line 111: OWN_V selects nearest chain polyline','allowed_groups':'lines 295–317: ownership-based whitelist with proximity-based first-web cross-blend exception','field':'lines 321–365: Gaussian longitudinal/lateral scores, guards, normalization and nearest allowed fallback','provenance_conclusion':'The existing INDEX assignment is traceable to an engineering nearest-chain / whitelist / Gaussian field and inherited unchanged. It is not an anatomical observation. The recorded pipeline was not rerun and its old joint metadata was not promoted into current authority.'},'source_asset_receipt':{'path':'production_spec/stage2_bootstrap/BOOTSTRAP_RECEIPT.json','armature':'NONE','vertex_groups':[],'meaning':'The source geometry carries no original anatomical skin-weight calibration.'},'independent_anatomy_assessment':'Index association is a plausible geometric/LEVEL_B anatomical candidate. No source validates the exact numerical R1B INDEX field. A possibly imperfect old assignment does not establish a correct new thumb assignment.','R3_ownership':'THUMB unchanged; independent from old procedural ownership selector and skin driver identity','weight_delta_this_review':0})

# Original measured figures; no copied medical images, AI reference or production asset edits.
REND=AUD/'renders'; REND.mkdir(exist_ok=True)
FONT=Path('C:/Windows/Fonts/arial.ttf'); BOLD=Path('C:/Windows/Fonts/arialbd.ttf')
def ft(size,bold=False):return ImageFont.truetype(str(BOLD if bold else FONT),size)
COLORS={'DORSAL':'#356cb5','PALMAR':'#ad517f','RADIAL':'#b2731b','ULNAR':'#657d2b'}
BODYCOL='#d94c43'; INDEXCOL='#2a72ae'; WEBCOL='#854aaa'; CAPCOL='#b78313'; THCOL='#328b7b'
def canvas(title,subtitle):
    im=Image.new('RGB',(1800,1200),'#f5f6f9'); d=ImageDraw.Draw(im)
    d.text((38,26),title,font=ft(34,True),fill='#172a42');d.text((38,77),subtitle,font=ft(21),fill='#43516a')
    d.text((38,1150),'STATIC READS ONLY | no poses evaluated | original measured geometry | candidate anatomy, no new weight authority',font=ft(19),fill='#4e5e72')
    return im,d
def txt(d,xy,text,width=65,size=22,color='#273950',bold=False):
    x,y=xy
    for paragraph in text.split('\n'):
        for line in textwrap.wrap(paragraph,width=width) or ['']:
            d.text((x,y),line,font=ft(size,bold),fill=color);y+=int(size*1.4)
    return y
def meshpanel(d,box,v,horizontal,vertical,view,focus,caption,labels=False,clusters=False,paths=None):
    x,y,w,h=box
    d.rounded_rectangle((x,y,x+w,y+h),radius=12,fill='white',outline='#d8dfe8',width=2)
    d.text((x+15,y+12),caption,font=ft(21,True),fill='#29394f')
    A=np.array([unit(np.array(horizontal)),unit(np.array(vertical)),unit(np.array(view))])
    Q=v@A.T*1000
    target=Q[sorted(focus),:2]; lo=target.min(axis=0);hi=target.max(axis=0)
    pad=np.maximum((hi-lo)*.15,4);lo-=pad;hi+=pad
    scale=min((w-80)/(hi[0]-lo[0]),(h-110)/(hi[1]-lo[1]));cen=(lo+hi)/2
    def pos(q):return (x+w/2+(q[0]-cen[0])*scale,y+65+(h-95)/2-(q[1]-cen[1])*scale)
    pts=[pos(q) for q in Q]
    center=np.array([np.mean(Q[f],axis=0) for f in F]);norm=normals(v)
    localfaces=[i for i,f in enumerate(F) if any(lo[0]<=Q[j,0]<=hi[0] and lo[1]<=Q[j,1]<=hi[1] for j in f)]
    for fi in sorted(localfaces,key=lambda i:center[i,2]):
        face=F[fi];p=[pts[a] for a in face]
        if any(a<x+7 or a>x+w-7 or b<y+52 or b>y+h-10 for a,b in p):continue
        shade=.50+.4*abs(float(unit(norm[face].sum(axis=0))@A[2]));val=int(155+65*shade)
        color=(val,val+2,min(255,val+7))
        if len(set(face)&THENAR)>=2:color=(170,213,203)
        if len(set(face)&WEB)>=2:color=(199,177,222)
        if len(set(face)&CAP)>=2:color=(232,211,154)
        d.polygon(p,fill=color);d.line(p+[p[0]],fill='#c5cbd2',width=1)
    def drawline(ids,color,width):
        p=[pts[a] for a in ids]
        for a,b in zip(p,p[1:]):
            if all(x+8<=u<=x+w-8 and y+53<=vv<=y+h-8 for u,vv in [a,b]):d.line([a,b],fill=color,width=width)
    for ei in BOUND:drawline(E[ei],'#252d3b',5)
    for digit in ['THUMB','INDEX']:
        chain=np.array(R['R2A_chains'][digit])@A.T*1000
        if v is V:
            p=[pos(q) for q in chain]
            for a,b in zip(p,p[1:]):
                if all(x+8<=u<=x+w-8 and y+53<=vv<=y+h-8 for u,vv in [a,b]):d.line([a,b],fill='#495562',width=4)
    for ids,color in [(WEB,WEBCOL),(CAP,CAPCOL),(INDEX,INDEXCOL),(BODY,BODYCOL)]:
        for a in sorted(ids):
            u,vv=pts[a]
            if not(x+10<=u<=x+w-10 and y+55<=vv<=y+h-10):continue
            color=COLORS[next(n for n in CNAMES if a in GROUPS[n])] if clusters and a in BODY else color
            front=float(norm[a]@A[2])>=0
            rad=8 if a in BODY else 5
            d.ellipse((u-rad,vv-rad,u+rad,vv+rad),fill=color if front else 'white',outline=color,width=3)
    if paths:
        for ids in paths:drawline(ids,'#d09219',4)
    if v is V:
        for name in ['THUMB_CMC_R','THUMB_MCP_R','INDEX_MCP_R','INDEX_PIP_R']:
            u,vv=pos(J[name]@A.T*1000)
            if x+10<=u<=x+w-10 and y+55<=vv<=y+h-10:
                d.line((u-8,vv,u+8,vv),fill='#122238',width=3);d.line((u,vv-8,u,vv+8),fill='#122238',width=3)
                d.text((u+9,vv-18),name.replace('_R',''),font=ft(17,True),fill='#14243b')
    if labels:
        for a in BODY:
            u,vv=pts[a]
            if x+25<=u<=x+w-60 and y+70<=vv<=y+h-35:d.text((u+9,vv-21),str(a),font=ft(17,True),fill='#9d322e')
    return pts
ALLFOCUS=set(np.where((VP[:,2]>.405)&(VP[:,2]<.56))[0])
LOCAL=set(BODY)|set(INDEX)|C1|C2
RELFOCUS=LOCAL|WEB|CAP
thumbbase=np.where((VP[:,2]>.395)&(VP[:,0]>1.412))[0]
def save(im,name):im.save(REND/name)
def legend(d,x,y):
    for name,col in [('BODY 16 (R3 THUMB)',BODYCOL),('INDEX-side 16',INDEXCOL),('Approved first web 21',WEBCOL),('Approved distal cap 9',CAPCOL),('Thenar engineering proxy',THCOL),('Exact R3 cut-set 16 edges','#252d3b')]:
        d.rectangle((x,y+5,x+16,y+21),fill=col);d.text((x+26,y),name,font=ft(20),fill='#34435a');y+=32
    return y
axial=[r['MCP_to_PIP_axial_fraction'] for r in ROWS]
im,d=canvas('Body-side exact collar: model location','Same 16 IDs before RSSF and in frozen R1B; joint overlays use the current live R2A frame only')
meshpanel(d,(38,125,825,875),VP,[1,0,0],[0,0,1],[0,1,0],ALLFOCUS,'Stage4A R2 / pre-RSSF: dorsal +Y')
meshpanel(d,(897,125,865,875),V,[1,0,0],[0,0,1],[0,1,0],ALLFOCUS,'Frozen R1B: dorsal +Y, x-ray point overlay')
txt(d,(50,1020),'The highlighted ring surrounds the index proximal tube in both static assets. Coincidence with the thumb cap in the RSSF pose is not tissue identity.',width=125,size=22)
save(im,'BODY_SIDE_COLLAR_16_MODEL_LOCATION.png')
for name,view in [('DORSAL',DI),('PALMAR',-DI)]:
    im,d=canvas('Body-side collar: '+name.lower()+' view','Local index frame: live MCP -> PIP distal axis; dorsal is projected canonical +Y')
    meshpanel(d,(38,125,960,960),V,RI if name=='DORSAL' else -RI,LI,view,LOCAL,'Current static local index surface',labels=False,clusters=True)
    y=legend(d,1040,140)
    y=txt(d,(1040,y+24),'Solid points face the viewer. Hollow points are on the opposite surface. All 16 IDs remain in the audit; surface normals, not inherited semantic labels, determine sectors.',width=45)
    y=txt(d,(1040,y+25),f'Index MCP->PIP segment: {seglen:.2f} mm. Body ring axial projection: {min(axial):.3f}–{max(axial):.3f} of that segment.',width=45)
    for n in CNAMES:y=txt(d,(1040,y+25),n+': '+', '.join(map(str,GROUPS[n])),width=45,size=20,color=COLORS[n])
    txt(d,(1040,y+25),'Candidate: index proximal integument. Fine human attachment and thumb driver remain UNRESOLVED.',width=45,size=23,bold=True)
    save(im,'BODY_SIDE_COLLAR_'+name+'_VIEW.png')
pathseed=min(BODY,key=lambda v:GE['first_web'][0][v]);path=[pathseed]
while path[-1] not in WEB:path.append(GE['first_web'][1][path[-1]])
im,d=canvas('Body-side collar and first web','Engineering web is shown in purple; a native human commissure margin is not registered')
meshpanel(d,(38,125,1030,960),V,[1,0,0],[0,0,1],[0,1,0],RELFOCUS,'Static model: web / collar / distal cap',paths=[path])
y=legend(d,1100,145)
y=txt(d,(1100,y+20),'10–16 graph edges and no direct web edge describe model topology only. They do not define the human first-web margin.',width=40)
y=txt(d,(1100,y+25),'S3: a radiodorsal index MCP donor corridor reaches the dorsal web. LEVEL_B transfer to this more distal index ring remains incomplete.',width=40)
y=txt(d,(1100,y+25),'S7: real first-web function relates to opposition. LEVEL_A regional function does not isolate CMC/MCP skin drivers at this ring.',width=40)
txt(d,(1100,y+25),'Radial extension: UNRESOLVED. Whole ring = shared web: not established.',width=40,size=25,bold=True)
save(im,'BODY_SIDE_COLLAR_FIRST_WEB_RELATION.png')
im,d=canvas('Body-side collar and thenar / thumb base','Green surface = inherited engineering thenar proxy; it is not a human thenar segmentation')
meshpanel(d,(38,125,1020,960),VP,[1,0,0],[0,0,1],[0,-1,0],set(thumbbase)|LOCAL|WEB,'Pre-RSSF palmar projection: separate ring and base')
y=legend(d,1095,145)
y=txt(d,(1095,y+20),'The ring surrounds the index phalangeal tube. The thenar proxy occupies proximal palm/base context; its boundary is not anatomically registered.',width=41)
y=txt(d,(1095,y+25),'Skin and fascia can be continuous while showing different local tethering and sliding. S4/S5 support local digit roles by analogy, not thenar-to-ring transmission.',width=41)
y=txt(d,(1095,y+25),'Opposition-related web function (S7) cannot establish thumb CMC or MCP coupling across all sides of an index tube.',width=41)
txt(d,(1095,y+25),'Thenar correspondence: NOT ESTABLISHED. New group authority: NONE.',width=41,size=25,bold=True)
save(im,'BODY_SIDE_COLLAR_THENAR_RELATION.png')
im,d=canvas('Deterministic anatomical candidate clusters','Pre-RSSF surface-normal sectors; topology preserved; anatomical roles are LEVEL_B candidates')
# A measured transverse scatter, not a fictional anatomical illustration.
q=(VP[BODY]-VP[BODY].mean(axis=0))@np.array([RP,DP]).T*1000
center=(465,610);scale=30
d.rounded_rectangle((38,125,900,1085),radius=15,fill='white',outline='#d8dfe8')
d.text((70,155),'Intrinsic ring section / pre-RSSF geometry',font=ft(24,True),fill='#273950')
d.line((130,610,800,610),fill='#9eaabe',width=2);d.line((465,280,465,950),fill='#9eaabe',width=2)
for label,xy in [('DORSAL',(415,245)),('PALMAR',(415,970)),('ULNAR',(110,570)),('RADIAL',(730,570))]:d.text(xy,label,font=ft(21,True),fill='#43516a')
angles=np.arctan2(q[:,1],q[:,0]);order=np.argsort(angles)
poly=[(center[0]+q[i,0]*scale,center[1]-q[i,1]*scale) for i in order]
d.line(poly+[poly[0]],fill='#617185',width=3)
for i,v in enumerate(BODY):
    n=next(n for n in CNAMES if v in GROUPS[n]);x,y=center[0]+q[i,0]*scale,center[1]-q[i,1]*scale
    d.ellipse((x-8,y-8,x+8,y+8),fill=COLORS[n]);direction=unit(q[i]);ex=center[0]+direction[0]*325;ey=center[1]-direction[1]*325
    d.line((x,y,ex,ey),fill=COLORS[n],width=2);d.text((ex-25,ey-12),str(v),font=ft(20,True),fill=COLORS[n])
txt(d,(70,1020),'PCA fitted section + area-weighted normals; no weights or ownership names select a sector.',width=65,size=20)
y=140
for n in CNAMES:
    y=txt(d,(975,y),f'{n}: {len(GROUPS[n])} vertices',width=50,size=25,color=COLORS[n],bold=True)
    y=txt(d,(975,y+6),IDENTITY[n],width=52,size=22)
    y=txt(d,(975,y+6),'Sources '+', '.join(SUPPORT[n])+' | LEVEL_B | driver UNRESOLVED',width=52,size=20)
    y+=28
save(im,'BODY_SIDE_COLLAR_ANATOMICAL_CLUSTERS.png')
im,d=canvas('Model -> human anatomy: candidate correspondence','Measured model locations linked to published regional roles; this is not a registered human anatomical reference')
meshpanel(d,(38,125,960,925),V,[1,0,0],[0,0,1],[0,1,0],set(thumbbase)|RELFOCUS,'Required context: joints, web, thenar proxy, cap, cut-set')
y=legend(d,1025,135)
cards=[('Body 16 / INDEX-side 16','Circumferential index proximal integument candidate. S4–S6 LEVEL_B; exact fascial attachment unresolved.'),('Approved first web','Project patch -> real commissure candidate. S3 adjacent MCP donor corridor; S7 real-web function. Boundary not registered.'),('Thumb CMC / thumb MCP','Live skeletal landmarks. Joint position is not surface-driver authority; CMC and MCP permissions remain separate and unresolved.'),('Thenar proxy / distal cap','Thenar proxy -> human thenar NOT ESTABLISHED. Distal cap retains binding project IP authority; it does not label the collar.'),('R3 cut-set / ownership','16 frozen cut edges; THUMB ownership preserved. Surface identity does not establish a musculoskeletal driver.')]
for a,b in cards:
    y=txt(d,(1025,y+18),a,width=49,size=22,bold=True)
    y=txt(d,(1025,y+3),b,width=49,size=20)
txt(d,(45,1070),'Branch D: ANATOMICAL_CORRESPONDENCE = UNRESOLVED | NEXT = MANUAL_ANATOMICAL_REFERENCE_REVIEW',width=135,size=23,bold=True)
save(im,'MODEL_TO_ANATOMY_CORRESPONDENCE_MAP.png')

BEFORE=json.loads((AUD/'FROZEN_HASHES_BEFORE.json').read_text(encoding='utf-8'))
AFTER={k:sha(ROOT/k) for k in BEFORE};changed=[k for k in BEFORE if BEFORE[k]!=AFTER[k]]
assert not changed,changed
blends_before={k:v for k,v in BEFORE.items() if k.endswith('.blend')}
blends_after={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in ROOT.rglob('*.blend')}
assert blends_before==blends_after
dump('FROZEN_HASH_VERIFICATION.json',{'before':BEFORE,'after':AFTER,'protected_file_count':len(BEFORE),'changed_files':changed,'all_before_equals_after':True,'all_workspace_blend_inventory_before':blends_before,'all_workspace_blend_inventory_after':blends_after,'new_blends':[],'removed_blends':[],'WEIGHT_DELTA':0,'GEOMETRY_DELTA':0,'TOPOLOGY_DELTA':0,'BONE_DELTA':0,'JOINT_DELTA':0,'BLEND_FILES_WRITTEN':0,'meaning':'Whole-file SHA-256 equality protects serialized fields including geometry, weights, topology, bones, joints, rolls and frozen settings; no historical pose was rerun.','supplemental_read_reference_hashes':{k:sha(ROOT/k) for k in ['production_spec/stage4_blender/stage4a_r2/R2_AUDIT.json','production_spec/stage2_bootstrap/BOOTSTRAP_RECEIPT.json']}})
STATUS={'BRANCH':'D','ANATOMICAL_CORRESPONDENCE':'UNRESOLVED','BODY_SIDE_COLLAR_THUMB_BASE_COUPLING':'UNRESOLVED','ENDPOINT_WEIGHT_ALLOWED_GROUP_AUTHORITY_R1':'UNRESOLVED — NO NEW AUTHORITY','NEXT':'MANUAL_ANATOMICAL_REFERENCE_REVIEW','body_vertex_ids':BODY,'cluster_count':4,'cluster_counts':{k:len(v) for k,v in GROUPS.items()},'entire_16_thumb_coupling_supported':False,'partial_regional_coupling_supported':False,'THUMB_CMC_R_authority':'UNRESOLVED — NOT GRANTED','THUMB_MCP_R_authority':'UNRESOLVED — NOT GRANTED','INDEX_SIDE_16':'NO NEW THUMB AUTHORITY','THUMB_IP_R_forbidden_on_new_collar_authority':True,'INDEX_DIP_R_forbidden_on_new_collar_authority':True,'scope_of_forbidden':'Constraints for any future allowed-group extension, not a claim that tiny historical R1B DIP residues are zero. Frozen cap retains THUMB_IP_R=1.0.','R3_ownership_unchanged':True,'DIGIT_OWNERSHIP_AUTHORITY_R3':'HUMAN_APPROVED','R3_EXACT_COLLAR':'PASS (inherited, no rerun)','CMC_CAGE_DYNAMIC_QUALIFICATION':'PASS (inherited, no dynamic evaluation this turn)','APPROVED_DISTAL_CAP':'BINDING_PROJECT_AUTHORITY; THUMB_IP_R=1.0 unchanged','FIRST_WEB_SKINNING_AUTHORITY':{'allowed':['WRIST_R','THUMB_CMC_R','THUMB_MCP_R','INDEX_MCP_R'],'forbidden':['THUMB_IP_R'],'unchanged':True},'Stage5B_R1B':'CURRENT_FROZEN_PRODUCTION_MASTER','Stage5B_R1E':'CANDIDATE_FOR_HUMAN_REVIEW; FAIL_CLOSED_PENDING_ENDPOINT_AUTHORITY_REVIEW','Stage5B_R1F':'NOT_CREATED','source_count':len(SOURCES),'source_level_counts':SOURCE_COUNTS,'exact_model_direct_authority_source_count':0,'conditional_outputs_omitted':{'BODY_SIDE_COLLAR_ALLOWED_GROUP_AUTHORITY_PROPOSAL.json':'Evidence is insufficient; no allowed-group or decay proposal is made.','PROPOSED_REGIONAL_WEIGHT_AUTHORITY_MAP.png':'No regional thumb authority supported; omitting conditional map avoids implying approval.'},'production_weight_percentages_proposed':False,'protected_files_equal':len(BEFORE),'WEIGHT_DELTA':0,'GEOMETRY_DELTA':0,'TOPOLOGY_DELTA':0,'BONE_DELTA':0,'JOINT_DELTA':0,'BLEND_FILES_WRITTEN':0,'POSE_EVALUATIONS_THIS_REVIEW':0,'deformation_runs':0,'full_stage6A_runs':0,'full_stage6B_runs':0,'stage6C_entered':False,'retopo_performed':False,'STOP':'WAITING_FOR_HUMAN_REVIEW'}
dump('NARROW_ANATOMICAL_EVIDENCE_REVIEW_STATUS.json',STATUS)

REPORT=f'''# NARROW_ANATOMICAL_EVIDENCE_REVIEW

结论：**Branch D — ANATOMICAL_CORRESPONDENCE = UNRESOLVED**。
下一候选：**MANUAL_ANATOMICAL_REFERENCE_REVIEW**。完成本轮后 STOP，等待 Human Review。

这 16 点在模型中确实绕食指近节管形成周向环，而非单一虎口/拇指基部表面片。可提出“食指近节表面组织”的强候选对应；但未完成真实虎口边界、皮纹或皮下附着点的配准，也没有对应位置的原生 CMC/MCP 分离皮肤位移证据。因此整圈及局部新 thumb authority 均未获支持。本轮的 UNRESOLVED 不表示已证明 thumb coupling 为零，也不表示 R1B 的具体权重已经被解剖学验证。

## 精确对象与静态定位

Body-side IDs：{', '.join(map(str,BODY))}。
INDEX-side IDs：{', '.join(map(str,INDEX))}。
Exact cut-set = 16 edges；C0/C1/C2 = {len(C0)}/{len(C1)}/{len(C2)}。

从 Stage4A R2（pre-RSSF）到 R1、R1A、R1B，3416 顶点及 3414 面的顶点顺序完全相同，允许追踪同一 ID；只读取静态数据，没有运行 deformation。定位不是从 R3 THUMB、THUMB_DISTAL 或旧 INDEX_ROOT 标签推出。Stage4A R2 的 canonical frame 为右手、+X 桡侧、+Y 背侧、+Z 远端；Stage2 源轴不同，未混用。pre-RSSF 精确环 PCA 平面与面积加权法线决定周向簇；current live MCP→PIP 轴独立检查。当前法线跨过扇区边界的点在逐点 JSON 中标注，簇不是组织学分割。

当前 body 点沿 INDEX MCP→PIP 的轴投影在 **{min(axial):.3f}–{max(axial):.3f}**，该骨段长 {seglen:.3f} mm。“index-root”作为宽泛历史术语不够精确，环实际位于近节管向 PIP 的一段。每点记录背/掌/桡/尺位置、两份法线、live thumb CMC/MCP、index MCP/PIP 距离、WEB/CAP/thenar proxy 欧氏/图/边长测地距离及邻面。骨点只作描述，不作组织许可。closest skeletal landmark 也不等于 closest skin attachment。

## 四个可复现候选簇

| 簇 | 数量与 IDs | 候选真实表面角色 | 证据与限制 |
|---|---|---|---|
'''
for n in CNAMES:REPORT+=f"| {n} | {len(GROUPS[n])}：{', '.join(map(str,GROUPS[n]))} | {IDENTITY[n]} | {', '.join(SUPPORT[n])}，LEVEL_B；精确附着及 thumb driver 未决 |\n"
REPORT+='''
簇的区域身份 confidence = MEDIUM；模型坐标定位 confidence = HIGH；具体组织插入点和 CMC/MCP authority = UNRESOLVED。不会把皮肤顶点命名为某条韧带本体。

## 窄范围文献证据与对应缺口

S1 为第一虎口形态原始论文；本轮可访问的 primary 索引内容不足以核查详细边界，明确降为 LEVEL_C，不能凭题名转成模型定位证据。[Zhu 等，2024](https://pubmed.ncbi.nlm.nih.gov/39084025/)

S3 的供区描述从食指 MCP 桡背侧朝背侧虎口延伸，说明真实界面并不由工程 WEB 标签封闭定义。但移植皮瓣供区是邻域参考，不能将更远端近节管整圈或其桡侧直接认定为原生虎口组织；对本模型的推断为 LEVEL_B。[Sano 等，2012](https://pubmed.ncbi.nlm.nih.gov/22471263/)

S4 的新鲜标本为小/环/中指，另有 Thiel 动态标本；显示侧方指皮肤的锚定与滑移关系。S5 则说明掌侧皮肤脂肪的局部筋膜网络随指屈曲改变方向。它们支持食指同源区域的候选角色（LEVEL_B），没有直接研究本食指虎口或 thumb motion，也不能证明模型上的韧带插入点。[Cleland 研究](https://pubmed.ncbi.nlm.nih.gov/24305724/)、[Grayson 研究](https://pubmed.ncbi.nlm.nih.gov/30170887/)

S6 提供 PIP 背侧皮纹附着的邻域证据；本环位于 PIP 近侧，未与真实皮纹配准，不能冒称位于 PIP wrinkle ligament 插入点。[Law 与 McGrouther，1984](https://pubmed.ncbi.nlm.nih.gov/6512362/)

S7 直接研究真实第一虎口挛缩松解后的功能：外展改善和对掌功能并不完全等价。LEVEL_A 只适用于真实 web 的功能关系，不能分离本位置 CMC 与 MCP 的原生皮肤驱动，也没有该模型注册。[Masden 与 Higgins，2011](https://pubmed.ncbi.nlm.nih.gov/22379438/)

S2 的血供交通仅为 vascular continuity（用于本变形问题是 LEVEL_C）；手术可移动的供区不等于完整皮肤原来的运动牵引。S8 的皮肤标记被动运动问题也提醒骨运动不是局部皮肤驱动身份的直接观测。[Pagliei 等，2003](https://www.sciencedirect.com/science/article/abs/pii/S026676810200298X)、[Nataraj 与 Li，2013](https://pubmed.ncbi.nlm.nih.gov/23775305/)

本轮注册 8 项原始研究：LEVEL_A=1、LEVEL_B=4、LEVEL_C=3；**直接注册 exact collar 并给出 driver authority 的来源数=0**。S1 可访问内容受限，已在 register 记载。无外部插图被复制进资产；commercial-use relevance = N/A。

## first web、thenar 与组织连续性

first-web correspondence：**UNRESOLVED**。模型已批准 WEB 是工程语义片，真实 commissure 可有延伸。10–16 graph edges 与无 direct adjacency 仅描述模型拓扑；既不能直接否定延伸，也不能因距离近就肯定。桡侧簇最值得人工配准，但目前不是 SUPPORTED shared cluster。

thenar correspondence：**NOT ESTABLISHED**。模型 thenar 仅有历史 arc/ownership proxy，不存在注册的人体边界；本环周向覆盖食指近节表面，不能当成 thenar/palm anchor 的已证身份。检索到的证据没有量化原生 thenar→此环在 thumb opposition、CMC opposition 或 thumb MCP flex 下的位移传递。

ANATOMICAL CONTINUITY 是可连续的区域布局；VASCULAR CONTINUITY 是血管通路；FASCIAL CONTINUITY 是筋膜附着/连续网络；SKIN MOBILITY 是皮肤可滑移或调整；DEFORMATION COUPLING 需要对应位置随指定关节动作的实际运动关系。前四者不能自动推出第五者，更不能推出某个 production 权重值。

CMC cross-region evidence：真实 web 对掌功能为 LEVEL_A，传递到候选桡侧模型位置最多 LEVEL_B 且未注册；**exact collar CMC authority = UNRESOLVED**。
MCP cross-region evidence：相邻手术供区为 LEVEL_B、血供为 LEVEL_C；没有原生 thumb MCP flex 对本环皮肤的独立测量；**exact collar MCP authority = UNRESOLVED**。两关节没有合并推定。

## 独立权重 provenance 审查

16 点 R1→R1A→R1B 的完整权重向量逐项完全相同，均由 INDEX_MCP_R 主导。初始 R1 脚本 line 111 使用 nearest-chain ownership，lines 295–317 设置语义/距离白名单，lines 321–365 以纵向/横向 Gaussian 场及 guard/归一化分配。源 bootstrap receipt 记录无 armature、无 vertex groups。因此它是可追溯的工程生成和继承，不能当作解剖测量。没有重跑旧算法。

独立模型几何及 LEVEL_B 文献使“食指近节表面组织”合理；但这只能支持区域 association，不能验证 R1B INDEX_MCP 的具体数值或证明所有 thumb transmission 必为零。旧权重可能不完全正确，也不能反推 thumb influence 正确。

R3 ownership 仍是 HUMAN_APPROVED 的 surface-domain identity；不能据此把其 THUMB 身份变成 skin driver identity。INDEX-side 16 点是同一食指管界面 counterpart，缺少新的对应运动证据，继续 **NO NEW THUMB AUTHORITY**。数值 sensitivity 需求不作为本轮解剖证据。

## Authority 与分支

整圈 thumb coupling supported = NO；partial regional coupling supported = NO（未获支持，不代表已证明生理 coupling 不存在）。CMC/MCP 新组许可均未授予。本轮不生成有条件的 allowed-group proposal 或 authority map，避免产生已批准区域的印象。没有提出 production 百分比、衰减方向或 anchor solver。

THUMB_IP_R 与 INDEX_DIP_R 不得作为未来新 collar authority；这不改写冻结历史向量或宣称其极小旧 residue 不存在。Approved distal cap 继续 THUMB_IP_R=1.0，approved first-web 继续既有四组并禁止 IP，未重开。

选择 D 而非 C：模型表面定位强烈支持 index integument 候选，但真实 commissure margin 和皮肤附着点未注册；缺少独立动态证据，不应将强区域候选升级成“已证明 index-only/stationary”或“已证明零 thumb coupling”。下一轮仅在用户授权后可人工将真实右手背/掌/桡侧图像及 MCP/PIP 皮纹、commissure margin 配准到 ID；如确认 shared patch，再寻找可区分 CMC/MCP 的原生皮肤运动证据。

## 输出与冻结验证

必需的 7 张 PNG 已生成，模型↔人体图逐项展示 body 16、INDEX 16、WEB、thumb CMC/MCP、index MCP、thenar proxy、cap、cut-set；人体对应写作候选，未伪造配准参考。逐点/逐簇定位、来源、confidence、冲突与 full vector provenance 在 JSON 可审计。

'''
REPORT+=f'保护的 {len(BEFORE)} 个既有文件全部 SHA-256 before=after，包括 R2A、R1B、R1E、R3 evidence、feasibility audit、上一轮 endpoint audit 及所有 workspace blend。全 blend inventory 相同，无新增/删除。WEIGHT/GEOMETRY/TOPOLOGY/BONE/JOINT DELTA 均为 0，BLEND_FILES_WRITTEN=0。\n\n'
REPORT+='冻结 production master=R1B；R1E 仍 fail-closed candidate；R1F=NOT_CREATED。R3 exact collar 与 CMC cage PASS 为既有资格继承，本轮未重新测试。Pose/deformation runs=0；Stage6A/B/C=0；retopo=0。\n\n**STOP — WAITING FOR HUMAN REVIEW**。\n'
(AUD/'NARROW_ANATOMICAL_EVIDENCE_REVIEW_REPORT.md').write_text(REPORT,encoding='utf-8')
required=['BODY_SIDE_COLLAR_16_MODEL_LOCATION.png','BODY_SIDE_COLLAR_DORSAL_VIEW.png','BODY_SIDE_COLLAR_PALMAR_VIEW.png','BODY_SIDE_COLLAR_FIRST_WEB_RELATION.png','BODY_SIDE_COLLAR_THENAR_RELATION.png','BODY_SIDE_COLLAR_ANATOMICAL_CLUSTERS.png','MODEL_TO_ANATOMY_CORRESPONDENCE_MAP.png']
for n in required:
    with Image.open(REND/n) as im:assert im.size==(1800,1200);im.verify()
for p in AUD.glob('*.json'):json.loads(p.read_text(encoding='utf-8'))
dump('OUTPUT_VERIFICATION.json',{'required_figures':required,'required_figure_count':7,'image_dimensions':[1800,1200],'all_png_decode_pass':True,'cluster_partition_exact':True,'source_ids_unique':len({s['id'] for s in SOURCES})==len(SOURCES),'protected_hash_check_pass':True,'required_reports_exist':True,'visual_inspection':'PENDING_SEPARATE_CONTACT_SHEET_REVIEW'})
contact=Image.new('RGB',(1200,4*435),'white')
for i,n in enumerate(required):
    with Image.open(REND/n) as im:im.thumbnail((590,394));contact.paste(im,((i%2)*600, (i//2)*435))
    ImageDraw.Draw(contact).text(((i%2)*600+8,(i//2)*435+399),n,font=ft(12),fill='black')
contact.save(AUD/'_tmp/anatomy_contact_sheet.png')
print(json.dumps({'body':BODY,'clusters':{k:len(v) for k,v in GROUPS.items()},'axial_range':(min(axial),max(axial)),'branch':'D','frozen_equal':len(BEFORE),'sources':SOURCE_COUNTS,'figures':7,'blend_writes':0},indent=2))
