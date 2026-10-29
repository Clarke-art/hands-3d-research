"""Evaluate approved continuous profiles and constrained static harmonic field.
No poses, R3 reruns, new authority, or edits to immutable donor vectors.
"""
from common import *
import numpy as np, math
from collections import Counter
DATA=read(OUT/'LIVE_SOURCE_DATA_R1.json');AUTH=read(OUT/'AUTHORIZED_WEIGHT_WRITE_SET_R1.json')
CAP=read(PROPOSAL/'CAP37_SKIN_DRIVER_AUTHORITY_R1.json');OLD9=read(PROPOSAL/'OLD_CAP9_SKIN_CORRECTION_AUTHORITY_R1.json')
WEB=read(PROPOSAL/'FIRST_WEB_SKIN_WEIGHT_WRAPPER_R2.json');CONT=read(PROPOSAL/'SKIN_WEIGHT_CONTINUITY_CONTRACT_R1.json')
R3=read(ROOT/'audits/human_r3_fresh_result_authority_freeze_r1/FRESH_R3_OWNERSHIP_AUTHORITY_R1.json')
PARAMS=read(ROOT/CAP['rule']['parameter_source']['path']);IMPACT=read(PROPOSAL/'CORRECTED_RIG_SKIN_FIELD_IMPACT_AUDIT_R1.json')
assert sha(ROOT/CAP['rule']['parameter_source']['path'])==CAP['rule']['parameter_source']['sha256']
V=np.array(DATA['CORRECTED']['mesh']['positions_world_mm']);EDGES=DATA['CORRECTED']['mesh']['edges'];BASE=DATA['R1B']['weights']
for k in ['positions_local_m','positions_world_mm','edges','faces','UV_layers','face_material_indices','material_slots']:
    assert DATA['CORRECTED']['mesh'][k]==DATA['STAGE4C']['mesh'][k]==DATA['R1B']['mesh'][k],('FAIL_CLOSED geometry source',k)
assert digest(BASE)==read(PROPOSAL/'R1B_SAFE_WEIGHT_REUSE_SET_R1.json')['baseline_weights_sha256']
WRITES=set(AUTH['REBUILD_REQUIRED']);SAFE=set(AUTH['SAFE_REUSE']);TARGET=set(AUTH['TARGETED_REVALIDATION'])
capids=set(x['vertex_id'] for x in CAP['per_vertex_surface_evidence']);webids=set(WEB['membership']['vertex_ids']);oldids=set(OLD9['vertex_ids'])
LABEL={int(k):v for k,v in R3['membership']['vertex_labels'].items()}
BONES=DATA['CORRECTED']['rig']['bones'];GROUPS=CONT['deform_bones'];G={g:k for k,g in enumerate(GROUPS)}
assert len(GROUPS)==16 and len(WRITES)==244 and all(LABEL.get(i) in ['THUMB','INDEX'] for i in WRITES)
assert set(GROUPS)=={g for g,b in BONES.items() if b['use_deform']}
def project_simplex(values):
    # Unique Euclidean projection onto nonnegative sum-one simplex.
    values=np.asarray(values);u=np.sort(values)[::-1];css=np.cumsum(u)-1
    rho=np.nonzero(u-css/np.arange(1,len(u)+1)>0)[0][-1];theta=css[rho]/(rho+1)
    return np.maximum(values-theta,0)
def seg_distance(p,a,b):
    p,a,b=np.asarray(p),np.asarray(a),np.asarray(b);ab=b-a;t=float(np.dot(p-a,ab)/np.dot(ab,ab));u=max(0.,min(1.,t))
    return float(np.linalg.norm(p-a-u*ab)),t,u
def chain_projection(i):
    pts=[BONES[g]['head_world_mm'] for g in ['THUMB_CMC_R','THUMB_MCP_R','THUMB_IP_R']]+[BONES['THUMB_IP_R']['tail_world_mm']]
    lengths=np.linalg.norm(np.diff(pts,axis=0),axis=1);cum=np.r_[0,np.cumsum(lengths)];rows=[]
    for k,(a,b) in enumerate(zip(pts,pts[1:])):
        d,raw,mu=seg_distance(V[i],a,b);rows.append((d,k,float(cum[k]+mu*lengths[k])))
    d,k,s=min(rows,key=lambda r:(r[0],r[1]));return d,k,s,cum
def quintic(t):
    t=max(0.,min(1.,float(t)));return t*t*t*(t*(6*t-15)+10)
def smoothstep(t):
    t=max(0.,min(1.,float(t)));return t*t*(3-2*t)
MED=PARAMS['derivation']['med_edge_mm'];H=CAP['rule']['h_mm'];SIP=CAP['rule']['s_IP_mm'];RADIUS=IMPACT['radius_scale_mm'];RMAX=IMPACT['outer_radius_mm']
assert H==PARAMS['accepted_params']['W_IP']*MED and WEB['prior_strength']==0.01
assert '6t^5-15t^4+10t^3' in CAP['rule']['profile']
X=np.zeros((3416,16))
for i,w in enumerate(BASE):
    for g,x in w.items():assert g in G;X[i,G[g]]=x
RULE={};EVALUATIONS={}
# Approved thumb profile is evaluated exactly. Cap is the distal 2-group special
# case; proximal base blending follows the hash-bound historical approved family.
thumb=set(i for i in WRITES if LABEL[i]=='THUMB' and i not in webids)
for i in sorted(thumb):
    d,k,s,knots=chain_projection(i);u=quintic(0.5+(s-SIP)/(2*H))
    if i in capids:
        assert d<RADIUS and k==2
        vec={'THUMB_IP_R':u,'THUMB_MCP_R':1-u};rule='APPROVED_CAP37_CORRECTED_ARC_QUINTIC'
    else:
        hb=PARAMS['accepted_params']['W_BASE']*MED
        base=1-quintic(0.5+(s-knots[1])/(2*hb))
        if u+base>1:u,base=u/(u+base),base/(u+base)
        ft=1-smoothstep((d-RADIUS)/(RMAX-RADIUS))
        vec={'THUMB_IP_R':u,'THUMB_MCP_R':max(0.,1-u-base),'THUMB_CMC_R':base*ft,'WRIST_R':base*(1-ft)}
        rule='APPROVED_THUMB_PROFILE_WITH_HISTORICAL_CENTERED_BASE_TRANSITION'
    X[i]=0
    for g,w in vec.items():X[i,G[g]]=w
    assert abs(float(X[i].sum())-1)<1e-12 and np.min(X[i])>=0
    RULE[i]=rule;EVALUATIONS[i]={'vertex_id':i,'rule':rule,'distance_mm':d,'nearest_segment':k,'arc_mm':s,'IP_quintic_t':max(0.,min(1.,0.5+(s-SIP)/(2*H))),
        'authority_reference':'CAP37_SKIN_DRIVER_AUTHORITY_R1.rule + hash-bound approved R1B parameter family'}
# INDEX rebuild sites and the one shared web site are solved together. Only
# approved write IDs are unknowns; immutable copy-only vectors are Dirichlet data.
unknown=sorted(WRITES-thumb);allowed={i:WEB['allowed_deform_groups'] if i in webids else CONT['ownership_guard']['allowed_by_side'][LABEL[i]] for i in unknown}
IDX={i:[G[g] for g in allowed[i]] for i in unknown};PRIOR={};ADJ={i:[] for i in unknown};edge_rows=[]
for i in unknown:
    ds=np.array([seg_distance(V[i],BONES[g]['head_world_mm'],BONES[g]['tail_world_mm'])[0] for g in allowed[i]])
    p=1/(ds+MED)**2;p=p/p.sum();PRIOR[i]=p
    X[i]=0;X[i,IDX[i]]=p
for eid,(a,b) in enumerate(EDGES):
    if a not in ADJ and b not in ADJ:continue
    coeff=MED/float(np.linalg.norm(V[a]-V[b]));assert coeff>0 and math.isfinite(coeff)
    for i,j in [(a,b),(b,a)]:
        if i not in ADJ:continue
        if i not in webids and j not in WRITES:
            # Only independently compatible retained vectors may be INDEX pins.
            # Numerical foreign residue is ignored for boundary inference only,
            # never removed from the actual copy-only candidate vector.
            ok=(LABEL.get(j)=='INDEX' and j not in webids and sum(w for g,w in BASE[j].items() if g not in allowed[i])<=1e-6)
            if not ok:continue
        ADJ[i].append((j,coeff));edge_rows.append({'vertex_id':i,'neighbor':j,'edge_id':eid,'coefficient':coeff,'unknown_neighbor':j in ADJ})
lam=WEB['prior_strength'];diag={i:lam+sum(c for j,c in ADJ[i]) for i in unknown}
assert all(diag[i]>0 for i in unknown)
def residual():
    mx=0.
    for i in unknown:
        rhs=lam*PRIOR[i].copy()
        for j,c in ADJ[i]:rhs+=c*X[j,IDX[i]]
        q=project_simplex(rhs/diag[i]);mx=max(mx,float(np.max(np.abs(q-X[i,IDX[i]]))))
    return mx
def objective():
    # Directed rows sum /2 for unknown-unknown, once for unknown-fixed.
    val=0.
    for row in edge_rows:
        i,j=row['vertex_id'],row['neighbor'];f=0.5 if j in ADJ else 1.
        val+=f*row['coefficient']*float(np.dot(X[i]-X[j],X[i]-X[j]))
    return val+lam*sum(float(np.dot(X[i,IDX[i]]-PRIOR[i],X[i,IDX[i]]-PRIOR[i])) for i in unknown)
history=[];initial=objective()
for iteration in range(1,20001):
    for i in unknown:
        rhs=lam*PRIOR[i].copy()
        for j,c in ADJ[i]:rhs+=c*X[j,IDX[i]]
        X[i]=0;X[i,IDX[i]]=project_simplex(rhs/diag[i])
    if iteration%10==0:
        err=residual();history.append({'iteration':iteration,'projected_fixed_point_residual':err,'objective':objective()})
        if err<=1e-12:break
else:raise RuntimeError('FAIL_CLOSED: approved deterministic convex field did not converge')
for i in unknown:
    RULE[i]='APPROVED_SHARED_WEB_CONSTRAINED_HARMONIC' if i in webids else 'APPROVED_INDEX_COMPATIBLE_CONSTRAINED_HARMONIC'
    EVALUATIONS[i]={'vertex_id':i,'rule':RULE[i],'allowed_groups':allowed[i],'geometry_prior':dict(zip(allowed[i],map(float,PRIOR[i]))),
       'edge_neighbors':[{'vertex_id':j,'coefficient':c} for j,c in ADJ[i]],'prior_strength':lam,
       'authority_reference':'OLD_CAP9_SKIN_CORRECTION_AUTHORITY_R1.deterministic_future_reconstruction + FIRST_WEB_SKIN_WEIGHT_WRAPPER_R2'}
assert set(EVALUATIONS)==WRITES
FINAL=[dict(w) for w in BASE]
for i in sorted(WRITES):
    # Blender stores float32 group weights. Quantize only authorized regenerated
    # vectors, leaving every copied float32 donor value exactly as read.
    FINAL[i]={g:float(np.float32(X[i,G[g]])) for g in GROUPS if X[i,G[g]]>0}
    assert len(FINAL[i])<=CONT['max_influences'] and abs(sum(FINAL[i].values())-1)<CONT['normalization']['absolute_tolerance']
for i in SAFE|TARGET:assert FINAL[i]==BASE[i]
changed=[i for i in range(3416) if FINAL[i]!=BASE[i]];assert set(changed)<=WRITES
dump('DETERMINISTIC_WEIGHT_GENERATION_R1.json',{'status':'PASS','evaluated_count':len(EVALUATIONS),'evaluated_ids':sorted(EVALUATIONS),
 'rule_counts':dict(Counter(RULE.values())),'per_vertex':[EVALUATIONS[i] for i in sorted(EVALUATIONS)],
 'harmonic_solve':{'method':'Sorted cyclic exact block minimization on approved nonnegative sum-one simplex; fixed copied neighbor data; fixed approved geometry regularization',
 'unknown_count':len(unknown),'positive_regularization_strength':lam,'iterations':iteration,'projected_fixed_point_residual':residual(),
 'initial_objective':initial,'final_objective':objective(),'sampled_progress':history,'deformation_objective':False,
 'boundary_pin_policy':'Copy-only candidate entries untouched. For INDEX inference use only compatible fixed INDEX context with at most 1e-6 numerical foreign residue. Such residue is not written away; subsequent strict guard audit records it.',
 'constraint_scope':'No unknown or write permission outside approved244; cap/compatible thumb profile fixed to approved formula.'},
 'intended_changed_ids':changed,'intended_changed_count':len(changed),'safe_copy_count':len(SAFE),'targeted_copy_count':len(TARGET),
 'pose_tests':0,'R3_reruns':0,'new_authority_created':False})
dump('CANDIDATE_WEIGHT_PAYLOAD_R1.json',{'phase':PHASE,'source_R1B_vector_hash':digest(BASE),'corrected_rig_sha256':sha(CORRECTED),
 'weights':FINAL,'vector_hash':digest(FINAL),'authorized_write_ids':sorted(WRITES),'rule_evaluated_ids':sorted(EVALUATIONS),
 'outside_authorized_write_count':0,'SAFE_REUSE_changed_count':0,'TARGETED_REVALIDATION_changed_count':0})
print(json.dumps({'evaluated':len(WRITES),'intended_changed':len(changed),'harmonic_unknowns':len(unknown),'iterations':iteration,'residual':residual(),'rules':dict(Counter(RULE.values()))},indent=2))
