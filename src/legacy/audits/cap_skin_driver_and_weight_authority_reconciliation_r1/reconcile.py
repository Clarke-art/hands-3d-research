"""Static authority planning only: no weight generation and no pose/solver runs."""
import json, math, hashlib, statistics
from pathlib import Path
from collections import Counter
import numpy as np
from snapshot import ROOT, OUT, sha
S5=ROOT/'production_spec/stage5_production_rig'
FZ=ROOT/'audits/human_r3_fresh_result_authority_freeze_r1'
INPUTS={}
def read(p):
    p=Path(p);p=p if p.is_absolute() else ROOT/p
    INPUTS[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)]=sha(p)
    return json.loads(p.read_text(encoding='utf-8-sig'))
def ref(p,role='FROZEN_INPUT'):
    p=Path(p);p=p if p.is_absolute() else ROOT/p
    return {'path':str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p),'sha256':sha(p),'role':role}
def canonical(d):return json.dumps(d,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def digest(d):return hashlib.sha256(canonical(d)).hexdigest()
def dump(n,d):
    (OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def ids(s):return sorted(map(int,s))
A=read(FZ/'FRESH_R3_OWNERSHIP_AUTHORITY_R1.json')
AH='361f4f25201f5810830dc1bfc4bd2cf19db908aef8945801a63bfd2829197ff0'
MH='f57483723e90cc34e0551bf70fac00c7c8cb789dbad5d0e248018fdaddd3741d'
assert digest(A)==AH and A['status']=='HUMAN_APPROVED_FROZEN'
assert A['authority_scope']=='BOUNDED_SOLVER_DOMAIN_VERTEX_OWNERSHIP_AUTHORITY'
MEM=read(FZ/'R3_OWNERSHIP_MEMBERSHIP_CANONICAL.json');assert digest(MEM)==MH
LABEL={int(i):x for i,x in A['membership']['vertex_labels'].items()}
assert len(LABEL)==962 and Counter(LABEL.values())=={'THUMB':498,'INDEX':464}
assert len(A['boundary']['edge_ids'])==20 and A['ambiguity']['vertex_count']==21
assert A['CLASS_A']['pass_count']==A['CLASS_A']['total_count']==6
assert A['FIRST_WEB21']['fresh_distribution']=={'THUMB':7,'INDEX':14} and A['FIRST_WEB21']['hard_pin_count']==0
assert A['old_cap9']['fresh_distribution']=={'THUMB':0,'INDEX':9} and A['old_cap9']['hard_role_count']==0
assert A['cap37_preservation']['count']==37 and A['cap37_preservation']['all_hard_source_preserved']
assert A['INDEX_source_preservation']['preserved_count']==145
def verify_refs(x):
    if isinstance(x,dict):
        if 'path' in x and 'sha256' in x:
            p=ROOT/x['path'];assert p.is_file() and sha(p)==x['sha256'],str(p)
            INPUTS[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)]=sha(p)
        for v in x.values():verify_refs(v)
    elif isinstance(x,list):
        for v in x:verify_refs(v)
verify_refs(A)
EVID=read(OUT/'SAVED_RIG_AND_SKIN_EVIDENCE_R1.json')['sources']
for v in EVID.values():
    p=ROOT/v['source_path'];assert sha(p)==v['source_sha256'];INPUTS[v['source_path']]=sha(p)
C=EVID['CORRECTED'];OLD=EVID['R2A'];BASE=EVID['R1B'];W=BASE['weights'];V=np.array(BASE['vertex_positions_world_mm']);EDGES=BASE['edges'];FACES=BASE['faces'];N=len(V)
assert N==3416 and len(EDGES)==6828 and len(FACES)==3414
assert C['source_sha256']=='5d5f86bb59135715a77515468c2b76fe81e2a44e2e8c5d6c17fcc3d56d2147fe'
assert OLD['source_sha256']=='c4fafc56c591411bb5ddf07bde44b5fcd6e6a9aa5e0d43b22f9734c0884c2845'
freeze=read(S5/'stage5b_freeze_r1b/STAGE5B_R1B_HUMAN_APPROVAL_FREEZE_R1.json')
assert BASE['source_sha256']==freeze['active_stage5b_master']['sha256']
SNAP=read(S5/'human_thumb_kinematic_authority_correction_r1/RIG_BEFORE_AFTER_FULL_SNAPSHOTS.json')
for tag,source in [('before',OLD),('after_saved_reloaded',C)]:
    for name,b in source['bones'].items():
        h=SNAP[tag]['bones'][name]
        for local in ['head_local_m','tail_local_m','matrix_local','parent','use_deform']:
            assert b[local]==h[local],(tag,name,local)
assert C['bones']['THUMB_IP_R']['head_local_m']==OLD['bones']['THUMB_IP_R']['head_local_m']
SLOTS=read(S5/'human_thumb_kinematic_authority_correction_r1/THUMB_KINEMATIC_BEFORE_AFTER_SLOT_VALUES.json')
assert SLOTS['saved_reload_exact_match'] and SNAP['output_rig_sha256']==C['source_sha256']
DEFORM=[n for n,b in C['bones'].items() if b['use_deform']];HELPERS=[n for n,b in C['bones'].items() if not b['use_deform']]
assert len(DEFORM)==16 and len(HELPERS)==5 and all(n.endswith('_TIP_R') for n in HELPERS)
assert set(W[0])<=set(DEFORM)
for name,e in EVID.items():
    assert e['edges']==EDGES and e['faces']==FACES
    if name!='RSSF':assert e['vertex_positions_local_m']==BASE['vertex_positions_local_m']
rssf_delta=float(np.max(np.linalg.norm(np.array(EVID['RSSF']['vertex_positions_world_mm'])-V,axis=1)))
assert rssf_delta<1e-4
STATIC=read(S5/'stage5b_r1e_cap_dependency_blast_radius_audit_r1/_STATIC_AUDIT_DATA.json')
NATIVE=read(S5/'stage5b_r1e_thumb_distal_cap_native_branch_identity_audit_r1/_tmp/static_mesh_states.json')['NATIVE']
assert sha(ROOT/NATIVE['path'])==NATIVE['sha256'] and NATIVE['edges']==EDGES and NATIVE['faces']==FACES
INPUTS[NATIVE['path']]=NATIVE['sha256'];NV=np.array(NATIVE['vertices_world_m'])*1000
native=STATIC['native_labels'];assert len(native)==N
cap=set(A['cap37_preservation']['vertex_ids']);old9=set(A['old_cap9']['vertex_ids']);web=set(A['FIRST_WEB21']['membership_vertex_ids'])
CAPA=read(ROOT/A['cap37_preservation']['authority_reference']['path']);assert set(CAPA['vertex_ids'])==cap
assert cap.isdisjoint(old9|web) and all(native[i]=='index' for i in old9)
NAILA=read(ROOT/'production_spec/stage4_blender/stage4c_r2/NAIL_AUDIT_R2.json')
NAIL={d:set(i for f in NAILA['per_digit_faces'][d] for i in FACES[f]) for d in ['thumb','index']}
adj=[set() for _ in range(N)]
for a,b in EDGES:adj[a].add(b);adj[b].add(a)
def ring(seed,n):
    out=set(seed);front=set(seed)
    for _ in range(n):
        nxt={j for i in front for j in adj[i]}-out;out|=nxt;front=nxt
    return out
def projection(points,P):
    points=np.asarray(points);lengths=np.linalg.norm(np.diff(points,axis=0),axis=1);cum=np.r_[0,np.cumsum(lengths)]
    out=[]
    for p in P:
        candidates=[]
        for k,(a,b) in enumerate(zip(points,points[1:])):
            ab=b-a;raw=float(np.dot(p-a,ab)/np.dot(ab,ab));mu=max(0.,min(1.,raw));q=a+mu*ab
            candidates.append((float(np.linalg.norm(p-q)),k,raw,mu,float(cum[k]+mu*lengths[k])))
        d,k,raw,mu,s=min(candidates,key=lambda c:(c[0],c[1]))
        out.append({'nearest_segment':k,'distance_mm':d,'mu_raw':raw,'mu_clamped':mu,'arc_mm':s,'normalized_longitudinal':s/cum[-1]})
    return out,cum.tolist()
def chain(e,d):
    names=['THUMB_CMC_R','THUMB_MCP_R','THUMB_IP_R'] if d=='THUMB' else ['INDEX_MCP_R','INDEX_PIP_R','INDEX_DIP_R']
    return [e['bones'][n]['head_world_mm'] for n in names]+[e['bones'][names[-1]]['tail_world_mm']]
new,knots=projection(chain(C,'THUMB'),V);old,oldknots=projection(chain(OLD,'THUMB'),V);iproj,iknots=projection(chain(C,'INDEX'),V)
assert all(C['bones'][n]==OLD['bones'][n] for n in DEFORM if n!='THUMB_IP_R')
REG=read(S5/'stage5b_r1b/_tmp/R1B_REGIONS.json');MED=REG['derivation']['med_edge_mm'];RT=REG['derivation']['R_TT_mm'];RMAX=REG['derivation']['R_MAX_mm'];H=5*MED
assert REG['accepted_params']['W_IP']==5 and REG['accepted_params']['profile']=='quintic'
material=set();numeric=set();rows=[]
for i,(a,b) in enumerate(zip(old,new)):
    delta={'nearest_segment_changed':a['nearest_segment']!=b['nearest_segment'],
           'distance_mm':abs(b['distance_mm']-a['distance_mm']),
           'mu_raw':abs(b['mu_raw']-a['mu_raw']),'mu_clamped':abs(b['mu_clamped']-a['mu_clamped']),
           'arc_mm':abs(b['arc_mm']-a['arc_mm']),
           'normalized_longitudinal':abs(b['normalized_longitudinal']-a['normalized_longitudinal']),
           'radius_normalized':abs(b['distance_mm']-a['distance_mm'])/RT}
    reasons=[]
    if delta['nearest_segment_changed']:reasons.append('NEAREST_SEGMENT_CHANGED')
    if delta['distance_mm']>=0.5*MED:reasons.append('DISTANCE_GE_HALF_MED')
    if delta['mu_clamped']>=0.05:reasons.append('MU_CLAMPED_GE_0_05')
    if delta['arc_mm']>=0.5*MED:reasons.append('ARC_GE_HALF_MED')
    if delta['radius_normalized']>=0.1:reasons.append('RADIUS_NORMALIZED_GE_0_1')
    if delta['normalized_longitudinal']>=0.05:reasons.append('NORMALIZED_LONGITUDINAL_GE_0_05')
    if reasons:numeric.add(i)
    support=(LABEL.get(i)=='THUMB' or any(w>1e-8 and g.startswith('THUMB_') for g,w in W[i].items()))
    ipactive=(W[i].get('THUMB_IP_R',0)>1e-6 or (max(a['arc_mm'],b['arc_mm'])>=knots[2]-H and min(a['distance_mm'],b['distance_mm'])<=RMAX))
    # The shared wrapper has no IP driver. Moving IP.tail does not invalidate its
    # CMC/MCP/WRIST/INDEX-MCP distances, which are all unchanged.
    active=support and ipactive and (i not in web or W[i].get('THUMB_IP_R',0)>1e-8)
    # R1B and the proposal use physical arc in mm, not s / total chain length.
    # A denominator-only change is diagnostic and does not require a new vector.
    physical_reasons=[r for r in reasons if r!='NORMALIZED_LONGITUDINAL_GE_0_05']
    if physical_reasons and active:material.add(i)
    rows.append({'vertex_id':i,'old':{**a,'radius_normalized':a['distance_mm']/RT},'corrected':{**b,'radius_normalized':b['distance_mm']/RT},
        'delta':delta,'material_metric_reasons':reasons,'consumed_field_change_reasons':physical_reasons,
        'normalized_denominator_only_change':reasons==['NORMALIZED_LONGITUDINAL_GE_0_05'],
        'thumb_field_active':bool(active),'material_skin_field_change':i in material})
RIGIMPACT={'authority_id':'CORRECTED_RIG_SKIN_FIELD_IMPACT_AUDIT_R1','status':'RESOLVED',
 'coordinate_space':'Saved world-space mm; no posed/evaluated coordinates',
 'old_source':ref(ROOT/OLD['source_path']),'corrected_source':ref(ROOT/C['source_path']),
 'IP_head_exactly_preserved':True,'corrected_slots_verified':SLOTS['slots'],
 'deform_bones':DEFORM,'non_deform_helpers':HELPERS,'TIP_weight_allowed':False,
 'old_thumb_chain_mm':chain(OLD,'THUMB'),'corrected_thumb_chain_mm':chain(C,'THUMB'),
 'old_arc_knots_mm':oldknots,'corrected_arc_knots_mm':knots,'INDEX_chain_mm':chain(C,'INDEX'),
 'radius_scale_policy':'Common historical R1B diagnostic scales, not a new anatomical membership selector',
 'radius_scale_mm':RT,'outer_radius_mm':RMAX,'MED_mm':MED,
 'material_thresholds':{'distance_mm':0.5*MED,'clamped_mu':0.05,'arc_mm':0.5*MED,'radius_normalized':0.1,'normalized_longitudinal':0.05,'nearest_segment_change':True},
 'active_field_rule':'THUMB frozen ownership OR positive historical thumb weight, AND (positive historical IP weight >1e-6 OR corrected/old arc >= corrected IP arc - historical W_IP*MED and distance <= historical outer radius). FIRST_WEB21 has IP=0 and unchanged allowed bone slots. The approved field uses physical arc mm: normalized-longitudinal denominator-only changes are diagnostic and do not require rebuild. Remote projection changes alone do not invalidate non-thumb skin.',
 'normalized_longitudinal_role':'Diagnostic s/total_length, not a consumed weight coordinate; its changes remain recorded separately.',
 'all_mesh_material_numeric_change_ids':ids(numeric),'all_mesh_material_numeric_change_count':len(numeric),
 'material_skin_field_affected_vertex_ids':ids(material),'material_skin_field_affected_vertex_count':len(material),
 'bone_roll_effect':'IP roll changed: any positive IP carrier is at least targeted revalidation even below distance thresholds; rotation response cannot be certified by segment comparison. No deformation executed.',
 'all_IP_carrier_ids':ids(i for i in range(N) if W[i].get('THUMB_IP_R',0)>1e-8),
 'per_vertex':rows,'weights_generated':0,'weights_written':0,'deformation_runs':0}
dump('CORRECTED_RIG_SKIN_FIELD_IMPACT_AUDIT_R1.json',RIGIMPACT)
GUARD={'THUMB':{'WRIST_R','THUMB_CMC_R','THUMB_MCP_R','THUMB_IP_R'},'INDEX':{'WRIST_R','INDEX_MCP_R','INDEX_PIP_R','INDEX_DIP_R'}}
WEBGROUP={'WRIST_R','THUMB_CMC_R','THUMB_MCP_R','INDEX_MCP_R'}
viol=set();tiny=set();violrows=[]
for i,w in enumerate(W):
    allowed=WEBGROUP if i in web else GUARD.get(LABEL.get(i),set(DEFORM))
    bad={g:x for g,x in w.items() if g not in allowed and x>1e-8}
    if bad:
        (viol if max(bad.values())>1e-6 else tiny).add(i)
        violrows.append({'vertex_id':i,'side':LABEL.get(i),'FIRST_WEB21':i in web,'forbidden_historical_groups':bad})
dump('R1B_FROZEN_SIDE_GUARD_AUDIT_R1.json',{'status':'RESOLVED','role':'Static eligible-driver guard audit, not new ownership or weights','significant_violation_ids':ids(viol),'numerical_only_violation_ids':ids(tiny),'per_vertex':violrows,'shared_interface_exception_ids':ids(web),'outside_R3_domain_not_relabelled':True})
BCORE=set(v for r in A['boundary']['edge_records'] for v in r['vertex_ids']);B1=ring(BCORE,1);B2=ring(BCORE,2)
CAP2=ring(cap,2);WEB2=ring(web,2);OLD2=ring(old9,2);EDGE2=ring({1551,3125},2)
DEP=read(S5/'stage5b_r1e_cap_dependency_blast_radius_audit_r1/STAGE5B_CAP_DEPENDENT_WEIGHT_REGION_AUDIT.json')
RA=read(S5/'stage5b_r1a/_tmp/R1A_REGIONS.json');legacy_selector=set(RA['AUTH'])|set(REG['AUTH'])|old9
repairs=set();repairrows=[]
for r in DEP['region_sets']:
    if r['stage'] in ['R1C','R1D','R1E']:
        source=read(ROOT/r['source']['path']);changes=set(source['changed_vertices'])
        actual={i for i in range(N) if EVID[r['stage']]['weights'][i]!=W[i]}
        relevant=changes|actual;repairs|=relevant
        repairrows.append({'stage':r['stage'],'source':r['source'],'recorded_changed_ids':ids(changes),'actual_saved_vs_R1B_delta_ids':ids(actual),
            'plan_scope_ids':ids(relevant),'dependency':'Cap/old R2-R3-derived selector and repair-field support; inspect R1B baseline here, never copy failed candidate vectors.'})
ipcarriers={i for i,w in enumerate(W) if w.get('THUMB_IP_R',0)>1e-8}
# All core reasons require candidate writes; rings allow retention if gates pass.
rebuild=cap|old9|material|viol|{1551,3125}
target=(CAP2|WEB2|OLD2|B2|EDGE2|legacy_selector|repairs|ipcarriers|tiny)-rebuild
safe=set(range(N))-rebuild-target;unresolved=set()
assert len(safe|target|rebuild)==N and not(safe&target or target&rebuild or safe&rebuild)
component_map={'CAP37':cap,'CAP37_CONTINUITY_2RING':CAP2,'OLD_CAP9':old9,'OLD_CAP9_INDEX_CONTINUITY_2RING':OLD2,
 'FRESH_R3_BOUNDARY_TRANSITION_2RING':B2,'FIRST_WEB21':web,'FIRST_WEB_CONTINUITY_2RING':WEB2,
 'CORRECTED_DISTAL_FIELD_AFFECTED':material,'EDGE5879_CONTINUITY_2RING':EDGE2,
 'HISTORICAL_R1C_D_E_DEPENDENT_REPAIR':repairs,'LEGACY_R1A_B_SELECTOR_REVALIDATION':legacy_selector,
 'IP_FRAME_CARRIER_REVALIDATION':ipcarriers,'R1B_SIDE_GUARD_VIOLATIONS':viol|tiny}
envelope=rebuild|target
def why(i):return sorted(k for k,s in component_map.items() if i in s)
classes={i:'REBUILD_REQUIRED' if i in rebuild else 'TARGETED_REVALIDATION' if i in target else 'SAFE_REUSE' for i in range(N)}
safe_proofs=[]
for i in ids(safe):
    assert i not in legacy_selector|material|ipcarriers|CAP2|WEB2|OLD2|B2|EDGE2|repairs|viol|tiny
    assert not any(g in HELPERS for g in W[i]) and all(x>=0 and math.isfinite(x) for x in W[i].values())
    assert len(W[i])<=4 and abs(sum(W[i].values())-1)<1e-5
    safe_proofs.append({'vertex_id':i,'vector_sha256':digest(W[i]),'side_context':LABEL.get(i,'OUTSIDE_BOUNDED_R3'),
        'no_cap_selector_write_dependency':True,'no_corrected_IP_frame_carrier':True,'outside_transition_and_repair_scope':True,
        'unchanged_driving_bone_slots':True,'distance_field_material_change':False})
REUSE={'authority_id':'R1B_SAFE_WEIGHT_REUSE_SET_R1','status':'RESOLVED','proposal_status':'PENDING_HUMAN_APPROVAL',
 'baseline_role':'FROZEN HISTORICAL PRODUCTION MASTER; exact vector reuse candidate only, not new production truth',
 'baseline_source':ref(ROOT/BASE['source_path']),'baseline_weights_sha256':digest(W),
 'precedence':'REBUILD_REQUIRED > TARGETED_REVALIDATION > SAFE_REUSE. No default mesh-wide rebuild.',
 'threshold_policy':'Forbidden significant weight >1e-6 requires rebuild; 1e-8..1e-6 numerical remnants require targeted revalidation and exact forbidden-group removal if retained. IP roll carriers never automatically safe.',
 'counts':dict(Counter(classes.values()),UNRESOLVED=0),'SAFE_REUSE':ids(safe),'REBUILD_REQUIRED':ids(rebuild),
 'TARGETED_REVALIDATION':ids(target),'UNRESOLVED':[],
 'safe_THUMB_label_count':sum(LABEL.get(i)=='THUMB' for i in safe),
 'safe_thumb_CMC_MCP_carrier_count':sum(any(g in ['THUMB_CMC_R','THUMB_MCP_R'] and x>1e-8 for g,x in W[i].items()) for i in safe),
 'previous_1931_independent_set_rechecked':{'still_safe':len(set(DEP['no_cap_or_thumb_driver_dependency_proven_ids'])&safe),'now_targeted_or_rebuild':len(set(DEP['no_cap_or_thumb_driver_dependency_proven_ids'])&envelope)},
 'per_vertex':[{'vertex_id':i,'classification':classes[i],'reasons':why(i),'R1B_vector_sha256':digest(W[i])} for i in range(N)],
 'safe_reuse_proof':safe_proofs,'reuse_requires_corrected_rig_bind_and_zero_pose_check_after_approval':True,
 'targeted_resolution':'Retain exact R1B vector if corrected-rig/static/continuity/deformation gates pass; otherwise create a new candidate vector inside envelope. No anatomy research prerequisite.',
 'historical_repair_dependencies':repairrows,'weights_generated':0}
dump('R1B_SAFE_WEIGHT_REUSE_SET_R1.json',REUSE)
ENV={'authority_id':'SKIN_REBUILD_ENVELOPE_R1','status':'RESOLVED','proposal_status':'PENDING_HUMAN_APPROVAL',
 'scope_type':'ENGINEERING_SKIN_TRANSITION_AND_VALIDATION_SCOPE_NOT_ANATOMICAL_MEMBERSHIP',
 'vertex_ids':ids(envelope),'total_count':len(envelope),'REBUILD_REQUIRED':ids(rebuild),'TARGETED_REVALIDATION':ids(target),
 'overlapping_components':{k:{'vertex_ids':ids(s),'count':len(s),'rebuild_required_count':len(s&rebuild),'targeted_revalidation_count':len(s&target)} for k,s in component_map.items()},
 'boundary_neighborhood_rule':'2 topology rings around frozen cut endpoints; layer 1 resolves driver support change, layer 2 supplies continuity pins/regression boundary. Do not rerun ownership or elevate rings to anatomy.',
 'first_web_neighborhood_rule':'2 topology rings for thumb/index/palm three-way continuity; FIRST_WEB21 exact membership unchanged; wrapper allowed groups apply only to its 21 vertices. Neighbors obey their own side guard.',
 'cap_neighborhood_rule':'2 topology rings; same corrected longitudinal rule continues into actual thumb support, no cap membership step or cap-exclusive one-hot clamp.',
 'outer_boundary_policy':'Retain exact safe vectors as Dirichlet pins; inspect every envelope-crossing edge. Failure promotes necessary neighbors inside a separately recorded candidate scope extension; no mesh-wide fallback.',
 'edge5879_endpoints_included':all(i in envelope for i in [1551,3125]),'full_mesh_rebuild_required':False,
 'historical_C_D_E_vectors_reused':False,'no_new_anatomical_membership':True}
dump('SKIN_REBUILD_ENVELOPE_R1.json',ENV)
def jumps(seed,group=None):
    out=[]
    for k,(i,j) in enumerate(EDGES):
        if i not in seed and j not in seed:continue
        groups=set(W[i])|set(W[j]);inf=max((abs(W[i].get(g,0)-W[j].get(g,0)) for g in groups),default=0)
        l1=sum(abs(W[i].get(g,0)-W[j].get(g,0)) for g in groups)
        out.append({'edge_id':k,'vertex_ids':[i,j],'L_inf':inf,'L1':l1,
            'IP_jump':abs(W[i].get('THUMB_IP_R',0)-W[j].get('THUMB_IP_R',0)),
            'MCP_jump':abs(W[i].get('THUMB_MCP_R',0)-W[j].get('THUMB_MCP_R',0))})
    return sorted(out,key=lambda r:(-r['L_inf'],r['edge_id']))
caprows=[]
for i in ids(cap):
    # Record geometry/support only. Do not evaluate the proposed weight ramp.
    caprows.append({'vertex_id':i,'position_RSSF_mm':V[i].tolist(),'position_native_mm':NV[i].tolist(),
       'corrected_thumb_projection':new[i],'distance_to_IP_head_mm':float(np.linalg.norm(V[i]-np.array(chain(C,'THUMB')[2]))),
       'distance_to_terminal_v284_mm':float(np.linalg.norm(V[i]-V[284])),
       'distance_to_thumb_nail_mm':min(float(np.linalg.norm(V[i]-V[j])) for j in NAIL['thumb']),
       'R1B_historical_vector':W[i],'R1B_foreign_driver':i in viol,
       'proximal_1ring_ids':ids(j for j in adj[i]-cap if new[j]['arc_mm']<new[i]['arc_mm']),
       'skin_classification':classes[i]})
assert all(r['corrected_thumb_projection']['nearest_segment']==2 for r in caprows)
maxs=max(abs(new[i]['arc_mm']-new[j]['arc_mm']) for i,j in EDGES if i in CAP2 and j in CAP2)
CAPDRIVER={'authority_id':'CAP37_SKIN_DRIVER_AUTHORITY_R1','status':'RESOLVED','proposal_status':'PENDING_HUMAN_APPROVAL',
 'membership_reference':ref(ROOT/A['cap37_preservation']['authority_reference']['path']),
 'ownership_authority_hash':AH,'corrected_rig_sha256':C['source_sha256'],
 'driver_decision':'THUMB_IP_R primary, continuous THUMB_MCP_R residual; no THUMB_TIP_R driver',
 'allowed_cap_deform_groups':['THUMB_MCP_R','THUMB_IP_R'],
 'forbidden_cap_groups':[g for g in DEFORM if g not in ['THUMB_MCP_R','THUMB_IP_R']]+HELPERS,
 'rule':{'projection':'Clamped nearest corrected CMC-MCP-IP-terminal deform chain; proximal segment wins exact ties; cumulative arc s in mm',
   'profile':'q(t)=6t^5-15t^4+10t^3, t=clamp(0.5+(s-s_IP)/(2h),0,1)',
   'h_mm':H,'s_IP_mm':knots[2],'IP_share_semantics':'q(t)','MCP_share_semantics':'1-q(t)',
   'parameter_source':ref(S5/'stage5b_r1b/_tmp/R1B_REGIONS.json','Historical approved centered quintic family W_IP=5*MED; corrected chain replaces contaminated slots, not old cap selector'),
   'scope':'Use same profile on cap and adjacent true thumb distal/proximal support, with CMC/WRIST base transition only farther proximal where supported; no membership-dependent clamp',
   'tip_plateau':'IP=1 is allowed only where longitudinal ramp mathematically saturates; terminal v284 satisfies plateau by geometry, not cap identity',
   'weights_evaluated_or_generated_this_round':False},
 'geometry_evidence':{'count':37,'IP_segment_projection_count':37,
   'IP_segment_mu_range':[min(new[i]['mu_clamped'] for i in cap),max(new[i]['mu_clamped'] for i in cap)],
   'IP_head_relative_longitudinal_mm':[min(new[i]['arc_mm']-knots[2] for i in cap),max(new[i]['arc_mm']-knots[2] for i in cap)],
   'radial_distance_mm':[min(new[i]['distance_mm'] for i in cap),max(new[i]['distance_mm'] for i in cap)],
   'all_inside_historical_tube_radius':all(new[i]['distance_mm']<RT for i in cap),
   'historical_FOREIGN_driver_cap_count':len(cap&viol)},
 'per_vertex_surface_evidence':caprows,
 'continuity_gate':{'status':'RESOLVED','candidate_validation':'DEFORMATION_VALIDATION_REQUIRED',
   'formula_continuity':'C2 quintic continuous field, no cap-edge step; nearest-chain arc tie seams must be checked before acceptance',
   'maximum_profile_derivative_per_mm':1.875/(2*H),
   'profile_delta_bound_rule':'abs(q_u-q_v)<=min(1, 1.875/(2h)*abs(s_u-s_v)); recorded geometric upper bound, not generated weights',
   'max_cap_2ring_arc_jump_mm':maxs,'upper_bound_at_largest_jump':min(1,1.875/(2*H)*maxs),
   'cap_1ring_vertex_ids':ids(ring(cap,1)),'cap_2ring_vertex_ids':ids(CAP2),
   'historical_top_edge_jumps':jumps(cap)[:20],
   'acceptance':'Apply continuity contract to all cap-crossing and proximal 1/2-ring edges; widen shared thumb transition or optimize in candidate phase if profile-to-retained-field seam fails. Do not accept solely from analytic smoothness.'},
 '37_point_one_hot_due_to_cap_name':False,'historical_old_cap9_rule_inherited':False,
 'skin_vectors_approved':False,'weights_generated':0}
dump('CAP37_SKIN_DRIVER_AUTHORITY_R1.json',CAPDRIVER)
dump('CAP_SKIN_DRIVER_AUTHORITY_R1.json',{'authority_id':'CAP_SKIN_DRIVER_AUTHORITY_R1','status':'RESOLVED','proposal_status':'PENDING_HUMAN_APPROVAL','cap37_driver':ref(OUT/'CAP37_SKIN_DRIVER_AUTHORITY_R1.json','PROPOSAL'),'ownership_label_to_one_hot':False,'skin_vectors_approved':False})
oldrows=[]
def cleanindex(i):
    return native[i]=='index' and LABEL.get(i)=='INDEX' and i not in old9|web|cap and sum(x for g,x in W[i].items() if g.startswith('THUMB_'))<=1e-6 and sum(x for g,x in W[i].items() if g.startswith('INDEX_'))>1e-6
for i in ids(old9):
    clean={j for j in ring({i},2)-old9 if cleanindex(j)};assert clean
    witnesses=[{'vertex_id':j,'hops':1 if j in adj[i] else 2,'vector':W[j],'vector_sha256':digest(W[j]),
       'fresh_side':'INDEX','native_branch':'INDEX','INDEX_projection':iproj[j],
       'index_source_backed':j in set(A['hard_sources']['INDEX']['vertex_ids']),
       'support_type':'FROZEN_INDEX_HARD_SOURCE' if j in set(A['hard_sources']['INDEX']['vertex_ids']) else 'NATIVE_AND_FROZEN_R3_INDEX_EXCLUSIVE'} for j in ids(clean)]
    oldrows.append({'vertex_id':i,'native_branch':'INDEX_SURFACE','fresh_R3_side':'INDEX','hard_role':0,
       'native_position_mm':NV[i].tolist(),'RSSF_position_mm':V[i].tolist(),'INDEX_chain_projection':iproj[i],
       'distances_to_INDEX_deform_segments_mm':[projection([C['bones'][g]['head_world_mm'],C['bones'][g]['tail_world_mm']],[V[i]])[0][0]['distance_mm'] for g in ['INDEX_MCP_R','INDEX_PIP_R','INDEX_DIP_R']],
       'history':{k:EVID[k]['weights'][i] for k in ['R1','R1A','R1B']},
       'clean_INDEX_witnesses':witnesses,'witness_count':len(witnesses),
       'support_ranges':{g:[min(W[j].get(g,0) for j in clean),max(W[j].get(g,0) for j in clean)] for g in sorted(GUARD['INDEX'])},
       'one_hot_MCP_independently_supported':all(W[j].get('INDEX_MCP_R',0)>=1-1e-6 for j in clean),
       'classification':'REBUILD_REQUIRED','validation':'DEFORMATION_VALIDATION_REQUIRED'})
OLDPLAN={'authority_id':'OLD_CAP9_SKIN_CORRECTION_AUTHORITY_R1','status':'RESOLVED','proposal_status':'PENDING_HUMAN_APPROVAL',
 'vertex_ids':ids(old9),'fresh_side':'9/9 INDEX','hard_role':0,
 'retired_protections':['THUMB_DISTAL_CAP_PROTECTION','THUMB_IP_ONE_HOT','THUMB_CAP_OWNERSHIP_OVERRIDE'],
 'allowed_deform_groups':sorted(GUARD['INDEX']),'forbidden_groups':[g for g in DEFORM if g not in GUARD['INDEX']]+HELPERS,
 'deterministic_future_reconstruction':{'domain':'old cap9 + INDEX-compatible 2-ring engineering patch, with coherent INDEX pins; shared first-web points keep wrapper constraints',
   'Dirichlet_pins':'Historical clean native-INDEX + frozen-R3 INDEX-exclusive/source-backed vectors; numerical <=1e-6 thumb residue must be removed inside candidate phase and normalized, never imported as thumb authority',
   'objective':'Unique convex simplex-constrained harmonic interpolation: sum_edges (MED/edge_length_mm)*||w_u-w_v||^2 + 0.01*sum_unknown ||w_i - normalized_inverse_distance_INDEX_chain_and_WRIST_prior_i||^2',
   'prior':'p_g proportional 1/(distance_mm_to_allowed_saved_bone_segment+MED)^2. Geometry regularizer only; no forced dominant driver.',
   'constraints':'Nonnegative, sum=1, allowed 4 groups, Dirichlet anchors; shared outer interface handled simultaneously by wrapper; stable sorted vertex/bone IDs and fixed objective',
   'not_executed':True,'no_manual_vertex_ratios':True},
 'per_vertex_evidence':oldrows,'INDEX_MCP_one_hot_as_blanket_rule':False,
 'continuity_gate':{'status':'RESOLVED','patch_vertex_ids':ids(OLD2),'historical_top_edge_jumps':jumps(old9)[:20],
   'candidate_validation':'DEFORMATION_VALIDATION_REQUIRED','acceptance':'INDEX-native 1/2-ring continuity contract, convex anchor range + geometric prior, no crater/spike, check all patch-to-retained crossing edges; harmonic field alone is not deformation qualification.'},
 'weights_generated':0,'weights_written':0}
dump('OLD_CAP9_SKIN_CORRECTION_AUTHORITY_R1.json',OLDPLAN)
WEBPLAN={'authority_id':'FIRST_WEB_SKIN_WEIGHT_WRAPPER_R2','status':'RESOLVED','proposal_status':'PENDING_HUMAN_APPROVAL',
 'FIRST_WEB_WEIGHT_SEMANTICS':'RETAINED_AND_STATICALLY_REVALIDATED_AS_SHARED_DEFORMATION_INTERFACE',
 'OLD_FIRST_WEB_SELECTOR':'RETIRED_FOR_FUTURE_USE; do not rerun cap/ownership-dependent selector or legacy exclusions',
 'membership':{'vertex_ids':ids(web),'count':21,'reference':A['FIRST_WEB21']['original_anatomical_membership_reference'],'unchanged':True},
 'R3_side_information':'7 THUMB / 14 INDEX, context/guard only, not bone ratios; wrapper exception has priority for the exact 21 frozen points',
 'allowed_deform_groups':sorted(WEBGROUP),'forbidden_groups':[g for g in DEFORM if g not in WEBGROUP]+HELPERS,
 'THUMB_IP_allowed':False,'THUMB_IP_required_weight':0,
 'normalization':{'sum':1,'nonnegative':True,'max_influences':4,'normalization_tolerance':1e-5,'forbidden_weight':0},
 'continuity_scope':ids(WEB2),'scope_type':'Engineering 2-ring test neighborhood; not expanded anatomical FIRST_WEB membership',
 'three_way_contexts':{'thumb_side_ids':ids(i for i in WEB2-web if LABEL.get(i)=='THUMB'),
     'index_side_ids':ids(i for i in WEB2-web if LABEL.get(i)=='INDEX'),
     'palm_wrist_context_ids':ids(i for i in WEB2-web if native[i]=='wrist' or W[i].get('WRIST_R',0)>=0.05),
     'outside_bounded_domain_ids':ids(i for i in WEB2-web if i not in LABEL),
     'palm_wrist_context_rule':'Existing WRIST carrier >=0.05 or frozen native wrist context; overlapping deformation support context, not anatomical membership. Palm/wrist continuity remains required even when all neighbors have bounded THUMB/INDEX side labels.'},
 'deterministic_future_field':'Jointly optimize the patch with corrected thumb CMC/MCP and unchanged INDEX_MCP/WRIST bone-distance priors; same positive-edge quadratic objective and simplex constraints as old cap9. Exact 21 web points permit the four shared groups only; neighboring points retain their own approved support. Keep valid R1B vectors as retention priors, never as forced old selector clamps.',
 'prior_strength':0.01,'edge_coefficient':'MED/edge_length_mm','constraints':'All three interfaces contribute edges simultaneously; every component has positive geometry-prior term and fixed valid outer pins; no thumb-only or index-only optimization',
 'protection_rules':['Frozen FIRST_WEB21 exact IDs unchanged','IP=0 and TIP=0 absolute','No R3-label-to-weight ratio mapping','No cap/old cap exclusion used to reconstruct membership','Preserve CMC geometry, use locality context only','Outer safe vectors byte-retained after acceptance'],
 'R1B_wrapper_group_violations':ids(web&viol),'historical_top_crossing_edge_jumps':jumps(web)[:20],
 'FIRST_WEB21_classification_counts':dict(Counter(classes[i] for i in web)),
 'continuity_gate':'DEFORMATION_VALIDATION_REQUIRED: static three-way seam checks then thumb/index/wrist targeted deformation. Semantic resolution does not claim candidate field already passed.',
 'weights_generated':0}
dump('FIRST_WEB_SKIN_WEIGHT_WRAPPER_R2.json',WEBPLAN)
CMC=read(ROOT/'production_spec/stage4_blender/stage4a_r2/CMC_LOCAL_RETOPO_AUDIT_R2.json')
assert CMC['VERDICT']['STAGE4A']=='PASS'
dump('CMC_GEOMETRY_PROTECTION_CONTEXT_R1.json',{'status':'RESOLVED','geometry':'FROZEN / PASS','source':ref(ROOT/'production_spec/stage4_blender/stage4a_r2/CMC_LOCAL_RETOPO_AUDIT_R2.json'),
 'exact_skin_mask_authority':'NOT_NEWLY_FROZEN','policy':'Geometry protection / locality / continuity context only; never derive anatomical membership or one-hot driver from fresh R3. Historical R1E R3-filtered cage wrapper retired. Exact skin mask not needed to resolve this plan.',
 'geometry_or_topology_research':False,'new_membership_generated':False})
CONTRACT={'authority_id':'SKIN_WEIGHT_CONTINUITY_CONTRACT_R1','status':'RESOLVED','proposal_status':'PENDING_HUMAN_APPROVAL',
 'deform_bones':DEFORM,'max_influences':4,'production_rule_source':ref(S5/'stage5b_r1b/scripts/r1b_common.py','MAX_INF=4; official 16-group production weight contract'),
 'normalization':{'target_sum':1,'absolute_tolerance':1e-5,'minimum_weight':0,'finite_only':True},
 'helpers':{'names':HELPERS,'deform_weight':0},'ownership_guard':{'scope':'962 frozen vertices only','allowed_by_side':{k:sorted(v) for k,v in GUARD.items()},'FIRST_WEB21_exception':sorted(WEBGROUP),'no_label_to_ratio':True,'forbidden_weight':0},
 'first_web_IP_weight':0,'old_cap9_thumb_override':False,
 'static_edge_gates':{'all_envelope_internal_and_crossing_edges':True,
   'max_single_group_jump_proposal':0.5,'max_L1_jump_proposal':1.0,
   'proposal_origin':'New conservative screening gates for Human review, not falsely attributed to old production approval. Retained baseline edges outside affected scope remain regression context.',
   'no_hard_swap':'Reject same-interface one-ring disjoint one-hot drivers, and any new jump beyond these gates; every exceeding edge requires local smoothing or targeted deformation justification before candidate acceptance.',
   'comparison':'No increase in a preexisting seam over its R1B jump +1e-5 unless explicitly recorded and qualified; existing bad baseline does not waive new absolute gates.',
   'profile_gate':'Check corrected IP/MCP quintic derivative bound plus physical adjacent-edge continuity; do not prove surface continuity from arc smoothness alone',
   'projection_tie_seams':'Record nearest-segment arc discontinuities and validate them; no implicit propagation from ownership labels',
   'scope_extension':'Failed outer seams may extend candidate envelope locally under recorded reason, never default all-mesh rebuild.'},
 'cap_IP_MCP_transition':'Same corrected longitudinal profile on compatible proximal 1/2-ring thumb support; no cap boundary clamp',
 'first_web_three_way':'Thumb/index/palm simultaneous continuity, exact membership not expanded',
 'old_cap9_INDEX_continuity':'No crater/spike relative clean INDEX field; continuous constrained interpolation with geometry prior, never all MCP by assumption',
 'safe_reuse':'Exact vector hashes retained where permitted; corrected bind, zero pose and local regression must be verified after approved candidate exists',
 'targeted_deformation_gate':'DEFORMATION_VALIDATION_REQUIRED: cap-IP/MCP flex, INDEX MCP/PIP, first-web CMC opposition plus wrist/palm, and edge5879 combined CMC/MCP. No runs in this phase.',
 'Stage6':'Separate later qualification; Q7 approval is permission for targeted rig/skin candidate rebuild only, never Stage6 or final production promotion',
 'candidate_static_pass':'NOT_RUN_NO_NEW_VECTORS','candidate_deformation_pass':'NOT_RUN','weights_generated':0}
dump('SKIN_WEIGHT_CONTINUITY_CONTRACT_R1.json',CONTRACT)
EDGE=read(S5/'stage5b_r1e_cap_dependency_blast_radius_audit_r1/EDGE5879_CAP_DEPENDENCY_AUDIT.json')
assert EDGES[5879]==[1551,3125] or EDGES[5879]==[3125,1551]
dump('EDGE5879_REBUILD_SCOPE_R1.json',{'status':'RESOLVED','action':'TARGETED_REBUILD_REQUIRED','historical_dependency':'PARTLY_CAP_DERIVED',
 'edge_id':5879,'endpoints':[1551,3125],'endpoint_fresh_side':[LABEL.get(i) for i in [1551,3125]],
 'endpoint_R1B_vectors':[W[i] for i in [1551,3125]],'historical_R1E_CMC_MCP_L3_ratio':EDGE['numeric_and_local_mechanism_evidence']['ratios']['CMC_MCP_L3']['R1E_ratio'],
 'historical_measurement_retained':True,'source':ref(S5/'stage5b_r1e_cap_dependency_blast_radius_audit_r1/EDGE5879_CAP_DEPENDENCY_AUDIT.json'),
 'neighborhood_ids':ids(EDGE2),'neighborhood_count':len(EDGE2),'endpoints_in_envelope':True,
 'v3125_rule':'Frozen FIRST_WEB21: THUMB_IP=0, shared four-group wrapper regardless of fresh side',
 'v1551_rule':'Use corrected geometry and frozen side guard; couple to v3125 shared interface without historical wrist-heavy partition step',
 'neighborhood_classification_counts':dict(Counter(classes[i] for i in EDGE2)),
 'why_rebuild_instead_of_revalidation_only':'Recorded R1E 0.94 wrist/MCP partition mismatch is a real defect; do not inherit R1E field. New joint candidate transition covers both endpoints. R1B near-continuous pair is a retention prior, not a waiver of wrapper/corrected-chain qualification.',
 'validation':'DEFORMATION_VALIDATION_REQUIRED','new_vector_written':False,'new_deformation_run':False})
SUMMARY={'phase':'CAP_SKIN_DRIVER_AND_WEIGHT_AUTHORITY_RECONCILIATION_R1','status':'RESOLVED','proposal_status':'PENDING_HUMAN_APPROVAL',
 'authority_inputs_verified':True,'cap37_driver_authority':'RESOLVED','cap37_driver_rule':'THUMB_IP_R primary + THUMB_MCP_R residual, corrected-arc centered quintic, h=5*MED; no cap-membership one-hot',
 'old_cap9_correction':'RESOLVED','FIRST_WEB_weight_wrapper':'RESOLVED','THUMB_IP_allowed_on_FIRST_WEB':False,
 'R1B_safe_reuse_count':len(safe),'targeted_revalidation_count':len(target),'rebuild_required_count':len(rebuild),'unresolved_count':0,
 'rebuild_envelope_total_count':len(envelope),'corrected_rig_affected_vertex_count':len(material),
 'fresh_R3_boundary_transition_count':len(B2),'boundary_endpoint_count':len(BCORE),'boundary_1ring_count':len(B1),
 'old_cap9_rebuild_count':len(old9&rebuild),'FIRST_WEB_rebuild_revalidate_count':len(web&envelope),
 'FIRST_WEB_plus_continuity_neighborhood_count':len(WEB2),'edge5879_status':'TARGETED_REBUILD_REQUIRED',
 'v1551_v3125_included_in_envelope':True,'full_mesh_rebuild_required':False,
 'ownership_labels_converted_directly_to_weights':False,'TIP_helper_deform_influence_allowed':False,
 'continuity_contract':'RESOLVED','Human_Review_generated':False,
 'BLEND_FILES_WRITTEN':0,'weights_generated':0,'weights_written':0,'R3_reruns':0,'Stage6_runs':0,
 'WEIGHT_DELTA':0,'GEOMETRY_DELTA':0,'TOPOLOGY_DELTA':0,'BONE_DELTA':0,'JOINT_DELTA':0,
 'NEXT':'HUMAN_SKIN_AUTHORITY_RECONCILIATION_APPROVAL','after_Human_approval':'TARGETED_RIG_AND_SKIN_DATA_REBUILD_AFTER_APPROVAL_R1','STOP':True}
dump('INPUT_AUTHORITY_VERIFICATION_R1.json',{'status':'RESOLVED','R3_combined_authority_hash':AH,'R3_membership_hash':MH,
 'R3_count_checks':'962/1881;498/464;20/21;CLASS_A6/6;WEB7/14;cap37;INDEX145 PASS',
 'corrected_rig_saved_snapshot_slots_exactly_verified':True,'deform_count':16,'non_deform_helpers':5,
 'historical_R1B_master_hash_verified':True,'RSSF_max_geometry_storage_delta_mm':rssf_delta,
 'native_geometry_source_hash_verified':True,'input_file_sha256':INPUTS})
dump('CAP_SKIN_DRIVER_AND_WEIGHT_AUTHORITY_RECONCILIATION_R1_STATUS.json',SUMMARY)
dump('REVIEW_VISUAL_DATA_R1.json',{'positions_mm':V.tolist(),'native_positions_mm':NV.tolist(),'edges':EDGES,
 'classifications':[classes[i] for i in range(N)],'sets':{k:ids(s) for k,s in component_map.items()},
 'frozen_labels':LABEL,'THUMB_chain_mm':chain(C,'THUMB'),'old_THUMB_chain_mm':chain(OLD,'THUMB'),'INDEX_chain_mm':chain(C,'INDEX'),
 'nail_thumb':ids(NAIL['thumb']),'nail_index':ids(NAIL['index']),'summary':SUMMARY})
print(json.dumps(SUMMARY,indent=2))
