"""Deterministic boundary candidates; no production authority, poses or blend writes."""
import sys
sys.dont_write_bytecode=True
import itertools, time, json, hashlib, collections
from pathlib import Path
import numpy as np
from boundary_geometry import *
def dump(n,o): (OUT/n).write_text(json.dumps(o,indent=2,ensure_ascii=False,allow_nan=False,default=lambda x:x.item() if isinstance(x,np.generic) else x.tolist()),encoding='utf8')
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1048576),b''): h.update(chunk)
    return h.hexdigest()
RESP=Path('<USER_HOME>/Downloads/HUMAN_CAP_AUTHORITY_RESPONSE_R1.json')
HUMAN=load(RESP)
assert {k:HUMAN['answers'][k] for k in ['Q1','Q2','Q3','Q4','Q5','Q6']}==dict(zip(['Q1','Q2','Q3','Q4','Q5','Q6'],['YES','YES','NO','NO','UNRESOLVED','APPROVE_WITH_BOUNDARY_REVIEW']))
assert len(CV)==48 and len(CF)==33 and len(CORE)==20 and len(EXP)==28
assert sha(ROOT/D['native']['path'])==C['mesh_sha256']
COMMON={'execution':'THUMB_DISTAL_CAP_BOUNDARY_REVIEW_R1','mesh_state':'NATIVE_PRE_RSSF_STAGE4A_R2',
    'native_mesh_sha256':C['mesh_sha256'],'seed_vertex_id':284,'region_identity':'ACCEPTED_BY_HUMAN_UNCHANGED',
    'boundary_authority':'UNRESOLVED_PENDING_HUMAN','production_authority_applied':False,
    'geometric_proxies_are_not_anatomical_authority':True}
shaft=[v for v in LOCAL if 14<=DEPTH[v]<=20]
SHAFT_Q=float(np.median(NORMAL_AX[shaft])); SHAFT_K=float(np.median([CURV[v]['normal_variation_rad_per_mm'] for v in shaft]))
PROFILES=[]; FITS=[]
for factor in [.5,.7,1.0]:
    profile=smooth_profile(MESHRES*factor); s=np.array([r['depth_from_tip_mm'] for r in profile])
    y=np.array([[r['tip_facing_normal_component'],r['normal_variation_rad_per_mm']] for r in profile]); y=(y-y.mean(0))/y.std(0)
    tries=[]
    for knot in np.arange(3.,15.,.5):
        m=np.stack([np.ones(len(s)),np.minimum(s,knot),np.maximum(0,s-knot)],axis=1); pars=np.linalg.lstsq(m,y,rcond=None)[0]
        err=float(np.mean((m@pars-y)**2))
        if pars[1,0]<0 and pars[2,0]>pars[1,0] and pars[1,1]<0 and pars[2,1]>pars[1,1]:
            tries.append((err,float(knot),pars.tolist()))
    best=min(tries)
    PROFILES.append({'bandwidth_factor':factor,'bandwidth_mm':MESHRES*factor,'samples':profile})
    FITS.append({'bandwidth_factor':factor,'best_knee_depth_mm':best[1],'standardized_feature_rms_squared':best[0], 'fit_coefficients':best[2]})
TRANSITION_LO=min(r['best_knee_depth_mm'] for r in FITS); TRANSITION_HI=max(r['best_knee_depth_mm'] for r in FITS)
TRANSITION_MID=float(np.median([r['best_knee_depth_mm'] for r in FITS]))
# A clear shaft-extension flag requires three independent native geometric signals, not g>9.
OVER={v for v in LOCAL if DEPTH[v]>TRANSITION_LO and NORMAL_AX[v]<.15 and CURV[v]['normal_variation_rad_per_mm']<.08}
# Bulb envelope is a review proxy: tip-facing rounded surface, within two local edge lengths axially.
BULB={v for v in LOCAL if DEPTH[v]<=2*MESHRES+.5 and NORMAL_AX[v]>=.35 and CURV[v]['normal_variation_rad_per_mm']>=.07}
BFACES={fi for fi in TF if set(F[fi])<=BULB}
print('Transition bracket',TRANSITION_LO,TRANSITION_HI,'overreach A',sorted(CV&OVER),flush=True)

def metric(fs):
    p=patch(fs); vs=p['vertices']; bv=p['boundary_vertices']; fs=set(fs)
    nail_inter=fs&NF; denom=sum(AREA[list(NF)])
    bulb_coverage=sum(AREA[list(fs&BFACES)])/max(sum(AREA[list(BFACES)]),1e-12)
    distalnail=sorted(v for v in NV if DEPTH[v]<=MESHRES*1.7)
    nail_face_depth={str(fi):float(FDEPTH[fi]) for fi in sorted(NF)}
    # Requiring all nail is intentionally not a cap criterion: proximal nail reaches 19.63 mm from tip.
    return {**p,'vertex_count':len(vs),'face_count':len(fs),'boundary_edge_count':len(p['boundary_edges']),
        'boundary_vertex_count':len(bv),'seed_included':SEED in vs,
        'max_geodesic_mm':float(max(G[vs])) if vs else None,'median_geodesic_mm':float(np.median(G[vs])) if vs else None,
        'axial_min_mm_from_IP':float(min(AXIAL[vs])) if vs else None,'axial_max_mm_from_IP':float(max(AXIAL[vs])) if vs else None,
        'depth_from_tip_min_mm':float(min(DEPTH[vs])) if vs else None,'depth_from_tip_max_mm':float(max(DEPTH[vs])) if vs else None,
        'boundary_geodesic_median_mm':float(np.median(G[bv])) if bv else None,
        'boundary_geodesic_rms_offset_from_9mm':float(np.sqrt(np.mean((G[bv]-9)**2))) if bv else None,
        'boundary_axial_spread_mm':float(np.ptp(DEPTH[bv])) if bv else None,
        'circumferential_completeness':{'occupied_30deg_sector_count':len(p['occupied_30deg_sectors']),
            'max_angular_gap_deg':p['max_angular_gap_deg'],'complete_12_sectors':len(p['occupied_30deg_sectors'])==12,
            'boundary_angular_winding_numbers':p['boundary_angular_winding_numbers'],
            'interpretation':'Projected boundary angular coverage about engineering IP-to-tip centerline; not uniform shaft rings or anatomical proof'},
        'core_9mm_vertex_count_covered':len(set(vs)&CORE),'missing_core_9mm_vertices':sorted(CORE-set(vs)),
        'bulb_coverage':{'rounded_tip_proxy_face_count':len(BFACES),'rounded_tip_proxy_area_coverage_fraction':float(bulb_coverage),
            'rounded_tip_proxy_vertex_count_covered':len(set(vs)&BULB),'rounded_tip_proxy_vertex_count_total':len(BULB),
            'definition':'Depth <= 2*local median edge + 0.5 mm; normal axial component >=0.35; normal variation >=0.07 rad/mm. Proxy only.'},
        'proximal_shaft_intrusion':{'flagged_vertex_ids':sorted(set(vs)&OVER),'count':len(set(vs)&OVER),
            'definition':f'Depth > global transition lower knee {TRANSITION_LO} mm AND normal axial component <0.15 AND normal variation <0.08 rad/mm',
            'scope':'Local distal-shaft continuation relative to rounded tip; not middle/proximal thumb region identity contradiction'},
        'thumb_nail_coverage':{'selected_approved_nail_face_ids':sorted(nail_inter),'total_approved_nail_face_count':len(NF),
            'selected_nail_face_count':len(nail_inter),'selected_nail_vertex_ids':sorted(set(vs)&NV),
            'nail_area_fraction':float(sum(AREA[list(nail_inter)])/denom),
            'nail_distal_edge_proxy_vertex_ids':distalnail,'nail_distal_edge_proxy_ids_covered':sorted(set(vs)&set(distalnail)),
            'approved_nail_face_depths_mm':nail_face_depth,'whole_nail_inside_cap_required':False,
            'approved_nail_native_depth_range_mm':[float(min(DEPTH[list(NV)])),float(max(DEPTH[list(NV)]))],
            'cap_nail_intersection_face_components':components(nail_inter),
            'approved_nail_edges_coincident_with_cap_boundary':[e for e in p['boundary_edges'] if any(fi in NF for fi in EF[tuple(e)])],
            'nail_compatibility':'ENGINEERING_COMPATIBLE_DISTAL_MARGIN_CONTACT' if set(distalnail)<=set(vs) else 'DISTAL_NAIL_MARGIN_PROXY_PARTLY_OMITTED',
            'nail_compatibility_scope':'Native mask relationship only; final anatomical cap boundary remains unresolved',
            'reason':'Cap may intersect the terminal nail edge; approved proximal nail extends onto the distal shaft and need not be in terminal cap. No nail authority change.'}}

FAMILIES={}; META={}
FAMILIES['A']=CF.copy(); META['A']={'name':'CURRENT_MIN_CORNER_9MM','rule':C['face_predicate'],'construction':'Exact existing 33-face baseline; no selection changes'}
FAMILIES['B']={fi for fi in TF if max(G[F[fi]])<=9.0}; META['B']={'name':'STRICT_FACE_ALL_CORNERS_9MM',
    'rule':'Every corner must have native THUMB-only geodesic <=9.0 mm; retain all qualifying faces without repair',
    'construction':'No component repair, hole fill or automatic terminal-bulb completion'}

# C: minimum number of added native faces to the strict face ball, containing all 20 ball vertices.
# Exhaustive cardinality search within A, with explicit geometry gate and exact disk predicate.
base=FAMILIES['B']; missing=CORE-{v for fi in base for v in F[fi]}
allowed=sorted(fi for fi in CF-base if not set(F[fi])&OVER)
bit={v:1<<i for i,v in enumerate(sorted(missing))}; target=sum(bit.values())
masks={fi:sum(bit.get(v,0) for v in F[fi]) for fi in allowed}
solutions=[]; examined=0; start=time.monotonic(); proof=[]; cutoff=False
lower_bound=(len(missing)+max(m.bit_count() for m in masks.values())-1)//max(m.bit_count() for m in masks.values())
for nadd in range(lower_bound,len(allowed)+1):
    count=0; covers=0
    for extras in itertools.combinations(allowed,nadd):
        count+=1; examined+=1
        mask=0
        for fi in extras: mask|=masks[fi]
        if mask!=target: continue
        covers+=1; fs=base|set(extras); p=patch(fs)
        if not p['single_disk']: continue
        bv=p['boundary_vertices']; score=(float(np.ptp(DEPTH[bv])),float(np.sqrt(np.mean((G[bv]-9)**2))),float(sum(AREA[list(fs)])),tuple(extras))
        solutions.append((score,fs,extras))
    proof.append({'added_face_count':nadd,'combinations_examined':count,'combinations_covering_all_core_vertices':covers,'viable_disk_solutions':len(solutions)})
    if solutions: break
    if time.monotonic()-start>40: cutoff=True; break
if solutions:
    score,fs,extras=min(solutions,key=lambda x:x[0]); FAMILIES['C']=fs
else: FAMILIES['C']=set(); extras=[]
META['C']={'name':'VERTEX_BALL_TOPOLOGY_CLOSED','rule':'Preserve all strict all-corner faces B; add the minimum number of A faces to cover every <=9 mm vertex, excluding faces with multi-signal distal-shaft overreach corners. Require one edge-connected manifold disk and one closed boundary loop.',
    'tie_break':'Minimum boundary axial spread, then boundary geodesic RMS offset from9, then surface area, then sorted added face IDs',
    'base_face_ids':sorted(base),'missing_core_vertex_ids_before_closure':sorted(missing),'admissible_added_faces':allowed,
    'added_face_ids':list(extras),'exhaustive_cardinality_search':proof,'minimum_additions_proven':bool(solutions) and not cutoff,
    'minimum_additions_coverage_lower_bound':lower_bound,
    'scope_of_minimality':'Global minimum added face count within the stated B-preserving/A-face domain and geometry gate; not a global anatomical optimum over all thumb faces',
    'construction_status':'CONSTRUCTED' if solutions else 'NON_VIABLE_NO_DISK_CLOSURE'}

# D: normal/curvature two-feature hinge fit; an unmodified diagnostic patch, not invented anatomical authority.
D_RAW={fi for fi in TF if FDEPTH[fi]<=TRANSITION_MID}; FAMILIES['D']=seed_component(D_RAW)
META['D']={'name':'CURVATURE_TRANSITION_BOUNDARY','rule':'Fit continuous two-slope hinge regressions jointly to standardized smoothed axial normal component and normal-variation curvature proxy; use median best knee over bandwidths 0.5/0.7/1.0 local median edge length; select native-thumb faces whose centroid is distal of that knee; keep seed component without boundary repairs.',
    'profile_depth_grid_mm':'1 to23 in0.5 mm increments','knot_search_mm':'3 to14.5 in0.5 mm increments',
    'features':'Native area-weighted normal dot IP-tip axis; median edge normal angle/edge length',
    'fits':FITS,'transition_depth_mm':TRANSITION_MID,'bandwidth_knee_range_mm':[TRANSITION_LO,TRANSITION_HI],
    'raw_face_ids':sorted(D_RAW),'discarded_nonseed_components':components(D_RAW-FAMILIES['D']),
    'limitation':'Global knee is a smoothed gradual bend; it is not a unique circumferential anatomical crease. Direction-specific profiles are tested separately.'}

# E: deterministic axial face cut closest to a 9mm boundary, requiring a full projected circumference and a disk.
thresholds=sorted(set(float(FDEPTH[fi]) for fi in TF if 1<=FDEPTH[fi]<=15))
sweep=[]; finalists=[]
for threshold in thresholds:
    raw={fi for fi in TF if FDEPTH[fi]<=threshold}; fs=seed_component(raw); p=patch(fs)
    bv=p['boundary_vertices']
    if not bv: continue
    rms=float(np.sqrt(np.mean((G[bv]-9)**2)))
    ok=p['single_disk'] and CORE<=set(p['vertices']) and len(p['boundary_angular_winding_numbers'])==1 and abs(abs(p['boundary_angular_winding_numbers'][0])-1)<1e-8 and p['max_angular_gap_deg']<=60
    sweep.append({'centroid_depth_cut_mm':threshold,'face_count':len(fs),'vertex_count':len(p['vertices']),
        'single_disk':p['single_disk'],'angular_sector_count':len(p['occupied_30deg_sectors']),
        'max_angular_gap_deg':p['max_angular_gap_deg'],'boundary_geodesic_rms_offset_from9_mm':rms,'admissible':ok})
    if ok: finalists.append(((rms, p['surface_area_mm2'],threshold,tuple(sorted(fs))),fs,threshold))
if finalists:
    _,fs,threshold=min(finalists,key=lambda x:x[0]); FAMILIES['E']=fs
else: FAMILIES['E']=set(); threshold=None
META['E']={'name':'AXIAL_CIRCUMFERENTIAL_BOUNDARY','rule':'Sweep all unique native thumb face-centroid axial depths from1 to15 mm, retain seed-connected distal sublevel patch, preserve all20 core ball vertices, require one manifold disk/closed loop and absolute projected angular winding1 about the IP-tip axis with maximum angular gap <=60 degrees. Minimize RMS boundary geodesic offset from9 mm; break ties by patch area, cut depth and face IDs. Twelve-sector coverage is a descriptive metric, not a bin-orientation-dependent selection gate.',
    'axis_origin_world_mm':IP.tolist(),'axis_unit':AXIS.tolist(),'circumferential_zero_unit_dorsal':DORSAL.tolist(),
    'circumferential_positive_unit':SIDE.tolist(),'centroid_depth_cut_mm':threshold,'sweep':sweep,
    'limitation':'Existing-face centroid cut approximates a circumferential ring; it is a staircase of native edges, not retopology or a continuous mathematical plane intersection.'}

METRICS={k:metric(fs) for k,fs in FAMILIES.items()}
for k,m in METRICS.items(): print(k,m['vertex_count'],m['face_count'],m['max_geodesic_mm'],'disk',m['single_disk'],'sectors',len(m['occupied_30deg_sectors']),'shaft',m['proximal_shaft_intrusion']['flagged_vertex_ids'],flush=True)

# Regional curvature sensitivity at twelve angles: do not hide ambiguity behind the global knee.
sector_fits=[]
for theta in range(0,360,30):
    fits=[]; delta=(ANGLE[LOCAL]-theta+180)%360-180; angular=np.exp(-.5*(delta/35)**2)
    for factor in [.5,.7,1.0]:
        s=np.arange(1.,23.01,.5); yp=[]
        for depth in s:
            w=angular*np.exp(-.5*((DEPTH[LOCAL]-depth)/(MESHRES*factor))**2)
            yp.append([float(w@NORMAL_AX[LOCAL]/w.sum()),float(<REDACTED_EMAIL>([CURV[v]['normal_variation_rad_per_mm'] for v in LOCAL])/w.sum())])
        y=np.array(yp); y=(y-y.mean(0))/y.std(0); tries=[]
        for knot in np.arange(3.,15.,.5):
            mat=np.stack([np.ones(len(s)),np.minimum(s,knot),np.maximum(0,s-knot)],axis=1); pars=np.linalg.lstsq(mat,y,rcond=None)[0]
            if pars[1,0]<0 and pars[2,0]>pars[1,0]: tries.append((float(np.mean((mat@pars-y)**2)),float(knot)))
        if tries: error,knee=min(tries); fits.append({'bandwidth_factor':factor,'knee_depth_mm':knee,'fit_squared_error':error})
    sector_fits.append({'circumferential_angle_deg':theta,'fits':fits})
sector_knees=[r['knee_depth_mm'] for s in sector_fits for r in s['fits']]
META['D']['sector_transition_knee_range_mm']=[min(sector_knees),max(sector_knees)]
META['D']['sector_fits']=sector_fits
META['D']['unique_stable_circumferential_transition_established']=max(sector_knees)-min(sector_knees)<=MESHRES

ROW=[]
for v in sorted(CV):
    one,two=ring(v)
    ROW.append({'vertex_id':v,'face_ids':VF[v],'selected_candidate_face_ids':sorted(set(VF[v])&CF),
        'geodesic_from_v284_mm':float(G[v]),'euclidean_tip_distance_mm':float(np.linalg.norm(V[v]-TIP)),
        'native_XYZ_world_mm':V[v].tolist(),'native_normal_area_weighted':VN[v].tolist(),
        'normal_tip_axis_component':float(NORMAL_AX[v]),'curvature_proxy':CURV[v],
        'nail_membership':v in NV,'approved_nail_incident_face_ids':sorted(set(VF[v])&NF),
        'boundary_membership':v in METRICS['A']['boundary_vertices'],'distance_to_thumb_IP_mm':float(np.linalg.norm(V[v]-IP)),
        'projection_on_IP_to_tip_axis_mm':float(AXIAL[v]),'projection_fraction_IP_to_tip':float(AXIAL[v]/TIPAX),
        'axial_depth_from_tip_mm':float(DEPTH[v]),'circumferential_angle_deg':float(ANGLE[v]),
        'radial_distance_to_axis_mm':float(RADIUS[v]),'one_ring':one,'two_ring_exact_hop_2':two,
        'selected_face_incidence':len(set(VF[v])&CF),'native_face_incidence':len(VF[v]),
        'candidate_memberships':[k for k,m in METRICS.items() if v in m['vertices']],
        'geodesic_class':'CORE_LE_9MM' if v in CORE else 'EXPANSION_GT_9MM'})
FR=[]
for fi in sorted(CF):
    FR.append({'face_id':fi,'vertex_ids':F[fi],'corner_geodesic_mm':[float(G[v]) for v in F[fi]],
        'native_centroid_world_mm':CENT[fi].tolist(),'native_normal':FN[fi].tolist(),'surface_area_mm2':float(AREA[fi]),
        'max_edge_length_mm':max(float(np.linalg.norm(V[a]-V[b])) for a,b in zip(F[fi],F[fi][1:]+F[fi][:1])),
        'centroid_axial_depth_from_tip_mm':float(FDEPTH[fi]),'nail_membership':fi in NF,
        'selected_face_boundary_edges':[e for e in METRICS['A']['boundary_edges'] if fi in EF[tuple(e)]],
        'candidate_memberships':[k for k,fs in FAMILIES.items() if fi in fs]})

CLASS={}; labels={'A':'ANATOMICALLY_REQUIRED_BOUNDARY_CORNER','B':'MESH_FACE_COMPLETION_ONLY','C':'PROXIMAL_OVERREACH','D':'NAIL_EDGE_REQUIRED','E':'UNRESOLVED'}
for v in sorted(EXP):
    rr=next(r for r in ROW if r['vertex_id']==v); classes=[]
    if v in OVER:
        cls='C'; reason='Beyond lower smoothed bulb-to-shaft knee, near transverse shaft normal, and low normal variation. This is a local distal-shaft tail of the cap patch, not a reclassification of the accepted thumb region.'
    elif v in NV and DEPTH[v]<=MESHRES*1.7 and v in set(METRICS['C']['vertices'])|set(METRICS['E']['vertices']):
        cls='D'; reason='Native distal nail-margin corner within the terminal-edge depth band; participates in an approved distal nail face adjoining the core. Retention is a review preference, not a requirement to include the whole nail.'
    elif v in BULB:
        cls='A'; reason='Tip-facing convex bulb surface supported jointly by short axial depth, positive axial normal and appreciable local normal variation. Long tangential geodesic alone is not shaft intrusion.'
    elif v not in set(METRICS['C']['vertices'])|set(METRICS['E']['vertices']) and NORMAL_AX[v]<.2:
        cls='B'; reason='Corner union extends onto a nearly shaft-directed side surface; topology-complete alternatives exist without this corner. Exact anatomical transition remains Human-reviewed.'
    else:
        cls='E'; reason='Metrics disagree or put the corner in a gradual transition. No unique anatomical boundary is established by the native proxies.'
    incident=sorted(set(VF[v])&CF)
    support=[{'face_id':fi,'face_is_approved_nail':fi in NF,'face_corners':F[fi],
        'core_corner_ids':[a for a in F[fi] if a in CORE], 'min_corner_geodesic_mm':float(min(G[F[fi]]))} for fi in incident]
    CLASS[v]={**rr,'classification_code':cls,'classification':labels[cls],
        'classification_status':'PROVISIONAL_ENGINEERING_FOR_HUMAN_BOUNDARY_REVIEW',
        'anatomical_authority_changed':False,'reason':reason,'multi_signal_basis':{
            'native_tip_shape':{'tip_facing_normal_component':float(NORMAL_AX[v]),'axis_depth_mm':float(DEPTH[v]),'radius_mm':float(RADIUS[v])},
            'normal_variation_rad_per_mm':CURV[v]['normal_variation_rad_per_mm'],'local_median_edge_length_mm':MESHRES,
            'nail_membership':v in NV,'candidate_memberships':rr['candidate_memberships'],
            'baseline_surface_continuity':'A is one manifold disk; this alone does not justify retaining the vertex'},
        'why_included_by_A':support,
        'remove_all_incident_A_faces_test':{'remaining_core_vertices':len(CORE&{a for fi in CF-set(incident) for a in F[fi]}),
            'single_disk':patch(CF-set(incident))['single_disk'],
            'caution':'Face-removal topology test is not a single-vertex delete proposal or proof of anatomical necessity'}}
COUNTS=dict(collections.Counter(r['classification_code'] for r in CLASS.values()))
COUNTS={k:COUNTS.get(k,0) for k in labels}
dump('CURRENT_CAP_BOUNDARY_FORENSIC.json',{**COMMON,'human_response_path':str(RESP),'human_response_sha256':sha(RESP),'Human_authority_verbatim':HUMAN,
    'native_branch_identity_reopened':False,'vertex_count':48,'face_count':33,'vertices':ROW,'faces':FR,
    'baseline_topology':METRICS['A'],'axis':{'IP_world_mm':IP.tolist(),'tip_world_mm':TIP.tolist(),'IP_to_tip_unit':AXIS.tolist(),'length_mm':TIPAX,
        'IP_status':'Inherited native engineering estimate; unchanged','circumferential_basis_dorsal':DORSAL.tolist(),'circumferential_basis_side':SIDE.tolist()},
    'curvature_method':'Median one-edge normal angle divided by edge length; supplementary least-squares quadratic fit of the native two-ring, with fit RMS and rank. Proxies depend on quad triangulation and mesh resolution.',
    'local_median_edge_length_mm':MESHRES,'profiles':PROFILES,'shaft_reference_normal_axis_median':SHAFT_Q,'shaft_reference_normal_variation_median':SHAFT_K})
dump('CAP_EXPANSION_VERTEX_CLASSIFICATION.json',{**COMMON,'classification_labels':labels,'classification_counts':COUNTS,'vertices':[CLASS[v] for v in sorted(CLASS)],
    'limits':'A/D required denotes provisional anatomical/engineering retention interpretation for Human review, not a newly approved cap membership or demonstrated anatomical necessity. E is retained where evidence does not decide.',
    'distance_only_classification':False,'over_13mm_vertex_ids':sorted(v for v in EXP if G[v]>13)})
v882=CLASS[882]
dump('V882_BOUNDARY_FORENSIC.json',{**COMMON,'vertex':v882,'geodesic_matches_15_894139_mm':abs(G[882]-15.8941392684)<1e-8,
    'native_region_interpretation':'Approved nail-margin vertex on near-transverse distal-shaft continuation; beyond rounded terminal-bulb proxy, still distal of IP. Whole nail need not lie in cap.',
    'other_over_13mm_vertices':[CLASS[v] for v in sorted(EXP) if G[v]>13 and v!=882],
    'why_nail_membership_does_not_force_cap_retention':'Approved nail extends axially3.74 to19.63 mm from tip; v882 is11.16 mm proximal to tip. Anatomical nail authority is frozen, and cap/nail are different masks.'})
for k,fs in FAMILIES.items():
    m=METRICS[k]
    viable=m['single_disk'] and m['seed_included']
    state='VIABLE_TOPOLOGICAL_REVIEW_CANDIDATE' if viable else 'NON_VIABLE'
    if k=='D' and not META['D']['unique_stable_circumferential_transition_established']: state='NON_VIABLE_AS_UNIQUE_STABLE_CURVATURE_AUTHORITY_DIAGNOSTIC_PATCH_ONLY'
    interpretation={
        'A':'Human-accepted thumb terminal region; min-corner corner union is circumferentially uneven and includes three low-curvature near-shaft corners. Region identity remains accepted; boundary unresolved.',
        'B':'Topologically sound small disk, but misses three core vertices and reduces terminal envelope; valid strict numerical ball is not evidence of anatomical completeness.',
        'C':'Minimum topology closure preserves every core vertex and every strict B face, avoids the three strong shaft-extension proxy corners. Minimality is geometric/topological, not a complete bulb guarantee.',
        'D':'Global curvature/normal knee has a plausible numeric fit, but varies around the circumference and with smoothing. Broad diagnostic patch cannot establish a unique stable anatomical transition.',
        'E':'Closed existing-edge circumferential cut selected near the inherited9 mm region; more consistent axis depth than min-corner A, but a planar centroid prior may under-cover the asymmetric bulb.'}[k]
    dump('CAP_BOUNDARY_CANDIDATE_'+k+'.json',{**COMMON,'candidate':k,**META[k],'status':state,
        'face_ids':sorted(fs),'vertex_ids':m['vertices'],'metrics':m,'human_readable_anatomical_interpretation':interpretation,
        'recommended_for_human_review_only':True,'membership_authority_applied':False})
comparison={**COMMON,'candidates':{k:{'name':META[k]['name'],'metrics':METRICS[k]} for k in FAMILIES},
    'transition_bracket_mm':[TRANSITION_LO,TRANSITION_HI],'distal_shaft_proxy_ids_in_A':sorted(CV&OVER),
    'expansion_classification_counts':COUNTS,'accepted_region_identity_unchanged':True,
    'old_cap9_status':'CONFIRMED_CONTAMINATED_NATIVE_INDEX_SURFACE','old_cap9_ids':D['current_cap9'],
    'old_anatomical_bounds_status':'13.1646 mm, 5.9643, 6.5160 remain INVALIDATED AS ANATOMICAL CAP-ENDPOINT EVIDENCE',
    'replacement_bound_produced':False,'human_response_sha256':sha(RESP)}
comparison['ENGINEERING_RECOMMENDATION']={
    'candidate':'E','status':'RECOMMENDED_FOR_HUMAN_REVIEW_ONLY',
    'GEOMETRIC_REASON':'E keeps all20 <=9mm core vertices and80.95% of the rounded-tip proxy face area, close to A81.25%, while reducing boundary axial spread7.895 to3.767 mm and avoiding the3 low-normal/low-curvature shaft-extension corners. All12 angular sectors are occupied.',
    'ANATOMICAL_REASON':'E retains the distal nail-margin edge v37-v879 without treating the entire19.63mm-long approved nail as terminal cap. It follows the terminal envelope more evenly than A and avoids the strong distal-shaft tails; this is a provisional native-anatomy interpretation.',
    'TOPOLOGICAL_REASON':'One edge-connected manifold disk, one closed boundary loop, seed included, Euler characteristic1, no edge or vertex-link nonmanifold incidence. C has the same topology but covers substantially less of the rounded terminal envelope.',
    'LIMITATIONS':'Engineering IP/axis estimate; circumferential ring is an existing-face centroid staircase. Rounded bulb coverage is a resolution-dependent proxy, not a ground-truth mask. E omits the provisional rounded-corner vertices v1453/v2785/v2790 and adds v297/v298 through native faces1942/1944; these differences explicitly require Human judgment. D transition is not stable around the circumference. Human has not selected or approved a final boundary.',
    'E_provisional_bulb_corner_ids_omitted':[1453,2785,2790], 'E_vertex_ids_added_outside_A':[297,298], 'E_face_ids_added_outside_A':[1942,1944]}
comparison['BOUNDARY']='UNRESOLVED'; comparison['NEXT']='MANUAL_CAP_BOUNDARY_REVIEW'
dump('CAP_BOUNDARY_CANDIDATE_COMPARISON.json',comparison)
dump('_RENDER_DATA.json',{'world_mm':V.tolist(),'faces':F,'native_normals':VN.tolist(),'vertex_geodesic_mm':{str(v):float(G[v]) for v in DOMAIN},
    'axis':{'IP_world_mm':IP.tolist(),'tip_world_mm':TIP.tolist(),'unit':AXIS.tolist()},'candidate_faces':{k:sorted(fs) for k,fs in FAMILIES.items()},
    'candidate_boundary_edges':{k:METRICS[k]['boundary_edges'] for k in FAMILIES},'candidate_vertices':{k:METRICS[k]['vertices'] for k in FAMILIES},
    'core_vertex_ids':sorted(CORE),'expansion_vertex_ids':sorted(EXP),'nail_face_ids':sorted(NF),
    'classifications':{str(v):r['classification_code'] for v,r in CLASS.items()},'class_labels':labels,
    'local_median_edge_length_mm':MESHRES,'metrics':METRICS})
print('Classifications',COUNTS,'v882',CLASS[882]['classification_code'],flush=True)
