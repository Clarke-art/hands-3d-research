"""Qualify existing candidate through Blender evaluation only; inputs remain byte-frozen."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
before=protected();verify(before)
assert not (OUT/'CANDIDATE_IDENTITY_R1.json').exists(),'Do not repeat qualification silently'
dump('HUMAN_APPROVAL_BIND_R1.json',{'authority':'Direct current Human instruction, supplied in pasted task attachment','prior_phase':'RIGHT_HAND_FIRST_WEB_FULL_STATIC_WEIGHT_FIELD_CAUSAL_PROBE_R1','prior_causal_phase_status':'HUMAN_APPROVED','STATIC_WEIGHT_FIELD_PROBLEM':'CAUSALLY_SUPPORTED','STATIC_WEIGHT_ROUTE':'OPEN','LEVEL_1_TOPOLOGY_ROUTE':'CLOSED','DEFORMATION_DOF_REBUILD':'NOT_REQUIRED_FOR_CURRENT_BLOCKER','production_promotion_authorized':False,'qualification_only_same_candidate':True})
D=read(PREV/'FULL_VECTOR_FIELD_DEFINITION_R1.json')
ob,rig=open_frozen();native=native_no_weights(ob,rig);shape=shape_state(ob);W=weights(ob);zero_base=coords(ob);constraints=constraint_payload(ob,rig)
pose_cams={};pose_baseline_corrective={};records=[]
(OUT/'pose_renders').mkdir(exist_ok=True);(OUT/'_tmp').mkdir(exist_ok=True);(OUT/'_tmp/motion_frames').mkdir(exist_ok=True)
rr=m.Renderer(MOTION_CAMERAS[1],'pose_renders');rr.sc.display.shading.shadow_intensity=0
for case in CASES:
    m.pose(rig,case);V,F=m.evaluate(ob,ob.matrix_world);VA=np.array([list(v) for v in V]);cams=camera_from_baseline_pose(VA);pose_cams[case['case_id']]=cams
    pose_baseline_corrective[case['case_id']]=values(ob)
    rr.cameras=cams;rr.draw('BASELINE',case['case_id'],V,F,VIEWS)
rr.dispose();records+=rr.records
ob,rig=open_candidate();WW=weights(ob);zero=coords(ob)
roi=D['ROI'];boundary=D['boundary'];outside=sorted(set(range(len(W)))-set(roi))
assert native_no_weights(ob,rig)==native and shape_state(ob)==shape and constraint_payload(ob,rig)==constraints
assert digest(native)==D['baseline_native_no_weights_sha256'] and digest(shape)==D['baseline_shape_sha256']
assert np.array_equal(WW[outside],W[outside]) and np.array_equal(WW[boundary],W[boundary])
for i in roi:
    assert all(float(WW[i,ob.vertex_groups[n].index])==w for n,w in D['candidate_full_21_vector'][str(i)].items() if n in ob.vertex_groups)
assert digest(action_payload(bpy.data.actions[ACTION]))==APPROVED_ACTION_SHA
assert ob.get('DESIGN_ONLY') and bpy.context.scene.get('HUMAN_APPROVED') is False
identity={'PHASE':PHASE,'CANDIDATE_WEIGHT_FIELD_IDENTITY':'MATCHED','candidate_path':CANDIDATE.relative_to(ROOT).as_posix(),'candidate_expected_sha256':PREVIOUS['candidate']['sha256'],'candidate_actual_sha256':sha(CANDIDATE),'candidate_all_weight_components_sha256':digest(WW.tolist()),'candidate_status':'DESIGN_ONLY_PRODUCTION_CANDIDATE_PENDING_QUALIFICATION','previous_ROI_full_vectors_exact':True,'outside_ROI_weights_exact':True,'boundary_weights_exact':True,'native_mesh_topology_Basis_UV_bones_rest_constraints_modifiers_exact':True,'corrective_driver_exact':True,'Action_payload_sha256':APPROVED_ACTION_SHA,'ZERO_baseline_candidate_evaluated_max_mm':float(np.linalg.norm(zero-zero_base,axis=1).max()*1000),'no_weight_writes':True,'no_harmonic_solve':True,'no_candidate_saved':True,'protected_inputs_before':before,'human_prior_causal_approval':'HUMAN_APPROVED','camera_authority':(PRODUCT/'PRODUCT_VIEW_OBSERVATION_R1.json').relative_to(ROOT).as_posix()}
dump('CANDIDATE_IDENTITY_R1.json',identity)
print('CANDIDATE_IDENTITY_MATCHED_NO_WRITES',flush=True)
faces=[list(p.vertices) for p in ob.data.polygons];edges=np.array([list(e.vertices) for e in ob.data.edges])
tris=np.array([[p[0],p[j],p[j+1]] for p in faces for j in range(1,len(p)-1)]);owners=np.array([i for i,p in enumerate(faces) for j in range(1,len(p)-1)])
def areas(v):
    a=np.linalg.norm(np.cross(v[tris[:,1]]-v[tris[:,0]],v[tris[:,2]]-v[tris[:,0]]),axis=1)*.5
    return np.bincount(owners,weights=a,minlength=len(faces))
A0=areas(zero)
def safety(v):
    a=areas(v);length=np.linalg.norm(v[edges[:,1]]-v[edges[:,0]],axis=1)
    return {'NaN_Inf':int((~np.isfinite(v)).sum()),'gross_collapsed_faces':int(((a<=1e-12)|(a/A0<=1e-6)).sum()),'catastrophic_zero_length_edges':int((length<=1e-12).sum())}
observations=[];maximum={'NaN_Inf':0,'gross_collapsed_faces':0,'catastrophic_zero_length_edges':0}
rr=m.Renderer(MOTION_CAMERAS[1],'_tmp/motion_frames');rr.sc.display.shading.shadow_intensity=0
for i in range(421):
    f=1+i//2;sub=(i%2)/2;motion(rig,f,sub);V,F=m.evaluate(ob,ob.matrix_world);VA=np.array([list(v) for v in V]);s=safety(VA)
    for k,v in s.items():maximum[k]=max(maximum[k],v)
    observations.append({'observation':i,'frame':f,'subframe':sub,'source_frame':690+i,'source_time_seconds':11.5+i/60,'minimum_safety':s,'corrective_natural_values':values(ob)})
    if any(s.values()):
        dump('MACHINE_FAILURE_R1.json',{'observation':observations[-1],'STOP':'FAIL_CLOSED'});raise RuntimeError('FAIL_CLOSED: catastrophic geometry; no repair')
    if sub==0 and f<=210:
        rr.cameras=MOTION_CAMERAS[f];rr.draw('CANDIDATE',f'F{f:03}',V,F,VIEWS)
    if i%60==0:print('QUALIFICATION_PROGRESS',i,'/420',flush=True)
rr.dispose()
neutral(rig);restore=float(np.linalg.norm(coords(ob)-zero,axis=1).max()*1000);assert restore==0
dump('FULL_MOTION_MINIMUM_SAFETY_R1.json',{'PHASE':PHASE,'status':'PASS_MACHINE_MINIMUM_ONLY','window_seconds':[11.5,18.5],'duration_seconds':7,'observations':421,'rendered_integer_frames':210,'video_fps':30,'sample_mapping':'source 690+i; frame 1+i//2 + (i%2)/2, i=0..420 inclusive. F211 endpoint safety sampled, not added to 7sec encoding.','maxima':maximum,'ZERO_restore':'PASS','ZERO_restore_max_mm':restore,'gross_tearing':'Ordinary product-video visual screen plus topology identity; no hidden edge-strain census','obvious_penetration':'Ordinary visible product motion + approved poses; no hidden crossing census','human_visible_screen_pending':True,'observation_records':observations})
rr=m.Renderer(MOTION_CAMERAS[1],'pose_renders');rr.sc.display.shading.shadow_intensity=0
pose_rows=[]
for case in CASES:
    m.pose(rig,case);V,F=m.evaluate(ob,ob.matrix_world);VA=np.array([list(v) for v in V]);s=safety(VA)
    assert all(v==0 for v in s.values()),case
    rr.cameras=pose_cams[case['case_id']];rr.draw('CANDIDATE',case['case_id'],V,F,VIEWS)
    vv=values(ob);neutral(rig);err=float(np.linalg.norm(coords(ob)-zero,axis=1).max()*1000);assert err==0
    assert vv==pose_baseline_corrective[case['case_id']]
    pose_rows.append({'pose':case['case_id'],'applied_definition':case,'cameras':pose_cams[case['case_id']],'baseline_corrective_natural_values':pose_baseline_corrective[case['case_id']],'candidate_corrective_natural_values':vv,'minimum_safety':s,'ZERO_restore_mm':err,'human_visible_result':'PENDING'})
rr.dispose();records+=rr.records
assert np.array_equal(weights(ob),WW) and native_no_weights(ob,rig)==native and shape_state(ob)==shape and constraint_payload(ob,rig)==constraints
assert digest(action_payload(bpy.data.actions[ACTION]))==APPROVED_ACTION_SHA
verify(before)
dump('APPROVED_POSE_REGRESSION_R1.json',{'PHASE':PHASE,'poses':pose_rows,'all_six_approved_pose_definitions_reused':True,'same_product_camera_for_baseline_candidate':True,'camera_rule':'Mature product directions/scales/resolution inherited unchanged; per-pose center from evaluated baseline hand/web bbox using original .45/.55 framing rule. Candidate never gets separate framing.','renders':records,'human_visible_result':'PENDING','source_candidate_unchanged':True})
print('READ_ONLY_QUALIFICATION_RENDER_DONE_630_MOTION_36_POSE_IMAGES',flush=True)
