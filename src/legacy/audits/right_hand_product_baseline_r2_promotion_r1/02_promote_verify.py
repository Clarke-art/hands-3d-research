"""Package the exact approved data, reopen/verify, then minimal ZERO/F130/L3 smoke."""
import sys,shutil
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
inspection=read(OUT/'CANDIDATE_CONTAINER_INSPECTION_R1.json');before=inspection['protected_inputs_before'];verify(before)
assert not R2.exists(),'Refuse overwrite of an existing frozen R2'
assert sha(CANDIDATE)==APPROVED_SHA and sha(BASE)==FROZEN_SHA
R2_DIR.mkdir(exist_ok=True)
ob,rig=open_asset(CANDIDATE)
neutral(rig)
approved=core_payload(ob,rig);W=weights(ob);weight_sha=digest(W.tolist());action_sha=digest(action_payload(bpy.data.actions[ACTION]))
assert action_sha==APPROVED_ACTION_SHA
definition=read(CAUSAL/'FULL_VECTOR_FIELD_DEFINITION_R1.json');roi=definition['ROI'];boundary=definition['boundary']
for i in roi:
    assert all(float(W[i,ob.vertex_groups[n].index])==v for n,v in definition['candidate_full_21_vector'][str(i)].items() if n in ob.vertex_groups)
# Only three minimal smoke states, not qualification or new pose design.
smoke_ids=['ZERO','F130','FULL_OPP_L3'];reference={};reference_values={};cameras={}
qual_poses={r['pose']:r for r in read(QUAL/'APPROVED_POSE_REGRESSION_R1.json')['poses']}
for state in smoke_ids:
    neutral(rig)
    if state=='F130':motion(rig,130)
    elif state=='FULL_OPP_L3':m.pose(rig,next(c for c in CASES if c['case_id']==state))
    reference[state]=coords(ob);reference_values[state]=values(ob)
    cameras[state]=h.MOTION_CAMERAS[130] if state=='F130' else qual_poses[state]['cameras']
neutral(rig);assert core_payload(ob,rig)==approved
changes=[]
if inspection['CANDIDATE_CONTAINER_STATUS']=='PRODUCTION_CLEAN':
    shutil.copyfile(CANDIDATE,R2)
    assert sha(R2)==APPROVED_SHA
    method='BYTE_PRESERVING_COPY'
else:
    # Inspection established no audit camera/comparison object. Do not delete product IDs.
    assert {o.name for o in bpy.data.objects}=={ob.name,rig.name}
    assert len(bpy.data.scenes)==1 and len(bpy.data.actions)==1
    # The source evidence Action payload is unchanged. Exclude only that evidence
    # playback wrapper from the clean production container, not from its original file.
    assert rig.animation_data.action is None
    evidence_action=bpy.data.actions[ACTION]
    assert digest(action_payload(evidence_action))==APPROVED_ACTION_SHA
    bpy.data.actions.remove(evidence_action,do_unlink=True)
    changes.append({'kind':'exclude_evidence_Action_from_production_container','name':ACTION,'original_payload_sha256':action_sha,'original_candidate_file_unmodified':True,'reason':'Qualified source motion is external evidence; R2 does not require it for product deformation.'})
    meta={'DESIGN_ONLY':False,'NOT_PRODUCTION':False,'HUMAN_APPROVAL_PENDING':False,'PRODUCTION_PROMOTION':'HUMAN_APPROVED_PRODUCT_BASELINE_FROZEN','PHASE':'RIGHT_HAND_PRODUCT_BASELINE_R2','PRODUCT_BASELINE_STATUS':'HUMAN_APPROVED_FROZEN','PRODUCT_BASELINE_SOURCE_SHA256':APPROVED_SHA}
    for k,v in meta.items():
        changes.append({'kind':'product_identity_metadata','object':ob.name,'key':k,'before':ob.get(k),'after':v});ob[k]=v
    scene=bpy.context.scene
    scene_meta={'DESIGN_ONLY':False,'NOT_PRODUCTION':False,'HUMAN_APPROVAL_PENDING':False,'HUMAN_APPROVAL':'APPROVED','DO_NOT_PROMOTE':False,'HUMAN_APPROVED':True,'PRODUCTION_PROMOTION':'HUMAN_APPROVED_PRODUCT_BASELINE_FROZEN','PHASE':'RIGHT_HAND_PRODUCT_BASELINE_R2','RIGHT_HAND_PRODUCT_BASELINE':'HUMAN_APPROVED_FROZEN','CURRENT_PRODUCTION_BASELINE':'R2','PREVIOUS_PRODUCTION_BASELINE':'R1','FIRST_WEB_HUMAN_VISIBLE_BLOCKER':'CLOSED','RIGHT_HAND_DEFORMATION':'CLOSED','LEFT_HAND_STARTED':False,'WEB_EXPORT_STARTED':False}
    for k,v in scene_meta.items():
        changes.append({'kind':'scene_product_identity','key':k,'before':scene.get(k),'after':v});scene[k]=v
    scene.frame_set(1);neutral(rig)
    assert core_payload(ob,rig)==approved and np.array_equal(weights(ob),W)
    assert len(bpy.data.actions)==0 and rig.animation_data.action is None
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(R2),compress=False)
    method='CLEAN_PRODUCTION_CONTAINER_EXACT_PRODUCT_DATA'
# Clean reopen is required BEFORE pointer can move.
ob,rig=open_asset(R2)
saved_zero_action=rig.animation_data.action.name if rig.animation_data and rig.animation_data.action else None
assert saved_zero_action is None and len(bpy.data.actions)==0
assert bpy.context.scene.frame_current==1 and m.state_zero(rig)
neutral(rig);promoted=core_payload(ob,rig);WW=weights(ob)
component_match={k:approved[k]==promoted[k] for k in approved}
assert all(component_match.values()),[k for k,v in component_match.items() if not v]
assert np.array_equal(W,WW) and digest(WW.tolist())==weight_sha
assert np.array_equal(W[roi],WW[roi]) and np.array_equal(W[boundary],WW[boundary])
assert ob['DESIGN_ONLY'] is False and ob['PRODUCT_BASELINE_STATUS']=='HUMAN_APPROVED_FROZEN' and bpy.context.scene['HUMAN_APPROVED'] is True
assert len(rig.data.bones)==21 and sum(b.use_deform for b in rig.data.bones)==16
assert not any(o.library or o.data.library for o in [ob,rig])
zero=coords(ob)
# Compatibility test appends the SAME evidence Action only in this unsaved session.
with bpy.data.libraries.load(str(CANDIDATE),link=False) as (src,dst):dst.actions=[ACTION]
assert digest(action_payload(bpy.data.actions[ACTION]))==APPROVED_ACTION_SHA
rig.animation_data_create()
checks=[];records=[]
(OUT/'smoke_renders').mkdir(exist_ok=True)
for state in smoke_ids:
    neutral(rig)
    if state=='F130':motion(rig,130)
    elif state=='FULL_OPP_L3':m.pose(rig,next(c for c in CASES if c['case_id']==state))
    got=coords(ob);delta=float(np.max(np.linalg.norm(got-reference[state],axis=1))*1000)
    assert np.isfinite(got).all() and delta<.001 and values(ob)==reference_values[state]
    # Actual evaluated positions give corresponding-point identity, not a new quality score.
    checks.append({'state':state,'candidate_R2_positions_numerically_exact':bool(np.array_equal(got,reference[state])),'max_difference_mm':delta,'NaN_Inf':0,'candidate_corrective_natural_values':reference_values[state],'R2_corrective_natural_values':values(ob),'status':'PASS'})
    rr=m.Renderer(cameras[state],'smoke_renders');rr.sc.display.shading.shadow_intensity=0
    faces=[tuple(p.vertices) for p in ob.data.polygons]
    rr.draw('APPROVED_CANDIDATE',state,[h.h.Vector(v) for v in reference[state]],faces,['REASONABLE_CLOSE_VIEW'])
    V,F=m.evaluate(ob,ob.matrix_world);rr.draw('R2',state,V,F,['REASONABLE_CLOSE_VIEW']);rr.dispose();records+=rr.records
neutral(rig);restore=float(np.max(np.linalg.norm(coords(ob)-zero,axis=1))*1000);assert restore==0
assert core_payload(ob,rig)==approved and np.array_equal(weights(ob),W)
verify(before)
assert sha(R2)!=APPROVED_SHA if method.startswith('CLEAN') else sha(R2)==APPROVED_SHA
dump('PROMOTION_IDENTITY_R1.json',{'PHASE':PHASE,'status':'PASS','CANDIDATE_CONTAINER_STATUS':inspection['CANDIDATE_CONTAINER_STATUS'],'promotion_method':method,'approved_candidate':{'path':CANDIDATE.relative_to(ROOT).as_posix(),'expected_sha256':APPROVED_SHA,'actual_sha256':sha(CANDIDATE)},'R2_baseline':{'path':R2.relative_to(ROOT).as_posix(),'sha256':sha(R2),'status':'HUMAN_APPROVED_FROZEN'},'WEIGHT_FIELD_IDENTITY':'EXACT_MATCH','all_3300_complete_weight_vectors_exact':True,'ROI_active_bone_full_vectors_exact':True,'boundary_weights_exact':True,'weight_field_sha256':weight_sha,'core_component_exact_match':component_match,'core_component_candidate_sha256':{k:digest(v) for k,v in approved.items()},'core_component_R2_sha256':{k:digest(v) for k,v in promoted.items()},'mesh_vertex_count':3300,'face_count':3298,'bone_count':21,'deform_bones':16,'TIP_non_deform':[b.name for b in rig.data.bones if not b.use_deform],'approved_six_pose_definitions_unchanged':CASES==h.CASES,'approved_six_pose_definitions':CASES,'Action_compatibility':'EXACT_MATCH','qualification_Action_payload_sha256':action_sha,'saved_R2_has_no_active_motion_Action':True,'saved_R2_contains_no_PianoVAM_Action':True,'PianoVAM_runtime_dependency':False,'clean_reopen':'PASS','saved_pose':'ZERO / RSSF','permitted_packaging_changes':changes,'smoke_checks':checks,'ZERO_restore_mm':restore,'smoke_renders':records,'full_qualification_repeated':False,'weights_solved_or_written':False,'new_bone_corrective_helper_cage_DQS':False,'production_pointer_updated_in_this_script':False,'identity_and_smoke_passed_before_pointer_update':True})
print('PROMOTION_IDENTITY_SMOKE_PASS_R2_READY_FOR_POINTER_UPDATE',sha(R2),flush=True)
