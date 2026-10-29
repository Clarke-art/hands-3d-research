import sys,traceback
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
def main():
 before=read(OUT/'PROTECTED_INPUTS_BEFORE_R1.json');validate_protected(before)
 inspection=read(OUT/'CANDIDATE_CONTAINER_INSPECTION_R1.json')
 assert inspection['CANDIDATE_CONTAINER_STATUS']=='AUDIT_SCAFFOLDING_PRESENT'
 assert sha(CAND)==EXPECTED_CAND and not DEST.exists() and not POINTER.exists()
 ob,rig=open_asset(CAND);approved=core(ob,rig);W=weights(ob,rig)
 assert {k:digest(v) for k,v in approved.items()}==inspection['core_component_sha256']
 assert len(ob.data.vertices)==3300 and len(ob.data.polygons)==3298
 assert len(rig.data.bones)==21 and sum(b.use_deform for b in rig.data.bones)==16
 assert all(b.name.endswith('_L') for b in rig.data.bones)
 smoke_ids=['ZERO','CMC_OPP_30','FULL_OPP_L3'];reference={};reference_values={};reference_bones={}
 for state in smoke_ids:
  apply_smoke(rig,state);reference[state]=coords(ob);reference_values[state]=values(ob);reference_bones[state]={p.name:mat(p.matrix) for p in rig.pose.bones}
 # Reopen approved candidate to package its exact saved neutral state, never save a test pose.
 ob,rig=open_asset(CAND);assert core(ob,rig)==approved and is_zero(rig)
 changes=[]
 meta={'PHASE':'LEFT_HAND_PRODUCT_BASELINE_R1','HUMAN_APPROVAL':'APPROVED','PRODUCT_BASELINE_STATUS':'HUMAN_APPROVED_FROZEN','PRODUCT_BASELINE_SOURCE_SHA256':EXPECTED_CAND,'PRODUCTION_PROMOTION':'COMPLETE'}
 for owner in [ob,bpy.context.scene]:
  for k in sorted(AUDIT_KEYS):
   if k in owner:
    changes.append({'owner':owner.name,'key':k,'operation':'remove_audit_identity','before':plain(owner[k])});del owner[k]
  for k,v in meta.items():owner[k]=v;changes.append({'owner':owner.name,'key':k,'operation':'set_production_identity','after':v})
 scene=bpy.context.scene;changes.append({'owner':'scene','operation':'rename_container','before':scene.name,'after':'LEFT_HAND_PRODUCT_BASELINE_R1'});scene.name='LEFT_HAND_PRODUCT_BASELINE_R1'
 assert core(ob,rig)==approved,'PRODUCT_PAYLOAD_CHANGED_DURING_PACKAGING'
 assert is_zero(rig) and scene.frame_current==1
 DESTDIR.mkdir(exist_ok=True);bpy.context.preferences.filepaths.save_version=0
 bpy.ops.wm.save_as_mainfile(filepath=str(DEST),compress=False)
 ob,rig=open_asset(DEST);result=core(ob,rig)
 matches={k:result[k]==v for k,v in approved.items()}
 assert all(matches.values()),('SAVED_PRODUCT_IDENTITY_MISMATCH',[k for k,v in matches.items() if not v])
 assert np.array_equal(W,weights(ob,rig)),'WEIGHT_IDENTITY_MISMATCH'
 assert is_zero(rig) and bpy.context.scene.frame_current==1
 assert all(k not in owner for owner in [ob,bpy.context.scene] for k in ['DESIGN_ONLY','NOT_PRODUCTION','HUMAN_APPROVAL_PENDING','PRODUCTION_POINTER_UPDATED'])
 assert len(bpy.data.objects)==2 and len(bpy.data.actions)==0 and len(bpy.data.cameras)==0
 assert all(min(o.scale)>0 and o.matrix_world.to_3x3().determinant()>0 for o in [ob,rig])
 assert len(ob.modifiers)==1 and ob.modifiers[0].type=='ARMATURE' and ob.modifiers[0].object==rig
 assert all(not len(p.constraints) for p in rig.pose.bones)
 assert all(not o.library and not o.data.library for o in [ob,rig])
 saved_hash=sha(DEST);zero,_=coords(ob);checks=[]
 def areas(V,F):return np.array([sum(np.linalg.norm(np.cross(V[f[i]]-V[f[0]],V[f[i+1]]-V[f[0]]))*.5 for i in range(1,len(f)-1)) for f in F])
 E=np.array([list(e.vertices) for e in ob.data.edges]);base_areas=areas(zero,reference['ZERO'][1])
 for state in smoke_ids:
  apply_smoke(rig,state);V,F=coords(ob);refV,refF=reference[state]
  assert np.array_equal(V,refV) and F==refF,('EVALUATED_GEOMETRY_MISMATCH',state)
  val=values(ob);assert val==reference_values[state],('CORRECTIVE_TRIGGER_MISMATCH',state)
  assert {p.name:mat(p.matrix) for p in rig.pose.bones}==reference_bones[state]
  assert all(f.driver.is_valid for f in ob.data.shape_keys.animation_data.drivers)
  A=areas(V,F);length=np.linalg.norm(V[E[:,0]]-V[E[:,1]],axis=1)
  finite=bool(np.isfinite(V).all());collapse=int(((A<=1e-12)|(A/base_areas<=1e-6)).sum());degenerate=int((length<=1e-12).sum())
  assert finite and collapse==degenerate==0,('MINIMUM_SAFETY_FAILURE',state)
  neutral(rig);restore=float(np.max(np.abs(coords(ob)[0]-zero))*1000);assert restore==0
  checks.append({'state':state,'status':'PASS','evaluated_geometry_exact':True,'max_difference_mm':0.0,'evaluated_topology_exact':True,'bone_pose_matrices_exact':True,'candidate_corrective_values':reference_values[state],'production_corrective_values':val,'corrective_trigger_parity':'PASS','NaN_Inf':0,'gross_collapsed_faces':collapse,'degenerate_edges':degenerate,'tearing':'No topology or evaluated geometry change','obvious_penetration':'No new penetration possible from packaging: exact evaluated surface matches Human-approved candidate; not a new forensic intersection census','ZERO_restore_mm':restore})
 assert core(ob,rig)==approved,'ZERO_RESTORE_PRODUCT_STATE_MISMATCH'
 assert sha(DEST)==saved_hash,'SMOKE_MUST_NOT_SAVE_BASELINE'
 validate_protected(before)
 dump('PROMOTION_IDENTITY_R1.json',{'PHASE':PHASE,'status':'PASS','promotion_method':'CLEAN_PRODUCTION_CONTAINER_EXACT_PRODUCT_DATA','CANDIDATE_CONTAINER_STATUS':'AUDIT_SCAFFOLDING_PRESENT','production_container_status':'PRODUCTION_CLEAN','candidate':{'path':CAND.relative_to(ROOT).as_posix(),'sha256':EXPECTED_CAND},'baseline':{'path':DEST.relative_to(ROOT).as_posix(),'sha256':saved_hash},'LEFT_WEIGHT_FIELD_IDENTITY':'EXACT_MATCH','weight_semantic_shape':[3300,21],'weight_max_difference':0.0,'weight_semantic_columns':[b.name for b in rig.data.bones],'weight_vectors_sha256':hashlib.sha256(W.tobytes()).hexdigest(),'core_component_exact_match':matches,'candidate_component_sha256':{k:digest(v) for k,v in approved.items()},'production_component_sha256':{k:digest(v) for k,v in result.items()},'excluded_identity_metadata_only':sorted(AUDIT_KEYS),'permitted_packaging_changes':changes,'vertex_count':3300,'face_count':3298,'bone_count':21,'deform_count':16,'non_deform_TIP':[b.name for b in rig.data.bones if not b.use_deform],'NO_NEGATIVE_SCALE_RUNTIME_DEPENDENCY':True,'saved_pose':'ZERO / RSSF','saved_frame':1,'runtime_review_or_debug_dependency':False,'clean_reopen':'PASS','smoke':checks,'smoke_only_three_cases':True,'full_six_pose_qualification_repeated':False,'new_screenshots_required':False,'no_new_screenshots_reason':'Packaging changed identity metadata only; all three evaluated surfaces and natural corrective values are exactly equal to Human-approved candidate.','source_mirror_record':{'SOURCE_CANONICAL_MASTER':'RIGHT_HAND_PRODUCT_BASELINE_R2','MIRROR_SOURCE_SHA256':next(iter(RIGHTS.values())),'MIRROR_PLANE':'WRIST rest-local X=0','MIRROR_SPACE':'ARMATURE_DATA -> MESH_DATA conjugation'},'mesh_rig_weights_corrective_driver_writers_called':False,'production_pointer_created':False,'identity_and_smoke_passed_before_pointer':True})
 print('EXACT_PRODUCT_IDENTITY_AND_3_CASE_SMOKE_PASS',saved_hash,flush=True)
try:main()
except Exception as e:
 dump('PROMOTION_FAIL_CLOSED_R1.json',{'PROMOTION':'FAIL_CLOSED','reason':str(e),'traceback':traceback.format_exc(),'pointer_exists':POINTER.exists(),'automatic_repair':False,'STOP':'STOP — HUMAN REVIEW'})
 raise
