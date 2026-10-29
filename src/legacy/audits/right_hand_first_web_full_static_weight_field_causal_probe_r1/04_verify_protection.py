"""Read-only final asset controls; no deformation experiment rerun, no .blend writes."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
D=read(OUT/'FULL_VECTOR_FIELD_DEFINITION_R1.json');M=read(OUT/'PROBE_MEASUREMENTS_R1.json')
before=D['protected_inputs_before'];verify_inputs(before)
assert sha(CANDIDATE)==M['candidate']['sha256']
ob,rig=open_frozen();W=weights(ob);native=native_no_weights(ob,rig);shape=shape_state(ob)
def constraint_payload(ob,rig):
    return {'rig':m.rig_payload(rig),'mesh_constraints':[m.rna(c,depth=2) for c in ob.constraints], 'rig_constraints':[m.rna(c,depth=2) for c in rig.constraints]}
controls=constraint_payload(ob,rig)
group_controls=[(g.name,g.lock_weight) for g in ob.vertex_groups]
extra={'edges':[list(e.vertices) for e in ob.data.edges],'smooth_flags':[p.use_smooth for p in ob.data.polygons],'shape_count':len(ob.data.shape_keys.key_blocks),'mesh_count':sum(o.type=='MESH' for o in bpy.data.objects),'armature_count':sum(o.type=='ARMATURE' for o in bpy.data.objects)}
bpy.ops.wm.open_mainfile(filepath=str(CANDIDATE),load_ui=False,use_scripts=False)
ob=bpy.data.objects[m.MESH_NAME];rig=bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG'];neutral(rig);WW=weights(ob)
assert native_no_weights(ob,rig)==native and shape_state(ob)==shape
assert constraint_payload(ob,rig)==controls
assert [(g.name,g.lock_weight) for g in ob.vertex_groups]==group_controls
assert {'edges':[list(e.vertices) for e in ob.data.edges],'smooth_flags':[p.use_smooth for p in ob.data.polygons],'shape_count':len(ob.data.shape_keys.key_blocks),'mesh_count':sum(o.type=='MESH' for o in bpy.data.objects),'armature_count':sum(o.type=='ARMATURE' for o in bpy.data.objects)}==extra
roi=D['ROI'];boundary=D['boundary'];outside=sorted(set(range(len(W)))-set(roi));free=D['free']
inactive=[g.index for g in ob.vertex_groups if g.name not in D['ACTIVE_WEIGHT_BONES_IN_ROI']]
assert np.array_equal(W[outside],WW[outside]) and np.array_equal(W[boundary],WW[boundary])
assert np.array_equal(W[:,inactive],WW[:,inactive])
assert np.all(WW>=0) and np.max(abs(WW.sum(1)-1))<2e-7
assert digest(action_payload(bpy.data.actions[ACTION]))==APPROVED_ACTION_SHA
assert len(list(OUT.glob('*.blend')))==1 and len(list((OUT/'renders').glob('*.png')))==24
assert ob.get('DESIGN_ONLY') and bpy.context.scene.get('HUMAN_APPROVED') is False
verify_inputs(before)
dump('FINAL_ASSET_PROTECTION_R1.json',{'PHASE':PHASE,'status':'PASS','FROZEN_FALLBACK_UNCHANGED':'YES','fallback_expected_sha256':FROZEN_SHA,'fallback_actual_sha256':sha(BASE),'fallback_status':'PROTECTED_FROZEN_FALLBACK','protected_inputs_expected_and_final':before,'all_authoritative_prior_outputs_unchanged':True,'candidate':M['candidate'],'candidate_count':1,'candidate_status':'DESIGN_ONLY','outside_ROI_weight_vectors_numerically_exact':True,'boundary_weight_vectors_numerically_exact':True,'inactive_weight_components_numerically_exact':True,'native_mesh_coordinates_edges_faces_UV_smooth_flags_rest_bones_modifiers_exact':True,'all_rig_properties_constraints_and_drivers_exact':True,'corrective_shape_payload_and_driver_exact':True,'Action_payload_sha256':APPROVED_ACTION_SHA,'Action_mapping_sample_unchanged':True,'ZERO_restore_max_mm':M['minimal_safety']['ZERO_restore_max_mm'],'minimum_machine_safety':M['minimal_safety'],'changed_scope':'Complete 8-active-bone field, same 164 free vertices; same fixed 70 boundary vertices. No additional candidate.','production_pointer_moved':False,'candidate_promoted':False,'production_weight_rebuild':False,'new_bone':False,'new_corrective':False,'new_helper':False,'new_cage':False,'DQS':False,'left_hand_started':False,'web_export_started':False,'historical_experiment_repeated':False,'forbidden_forensic_performed':False,'blend_files_written_this_phase':[CANDIDATE.relative_to(ROOT).as_posix()],'WORKFLOW_STATUS':'STOP_HUMAN_REVIEW'})
print('FINAL_ASSET_PROTECTION_PASS_ONE_DESIGN_ONLY_CANDIDATE',flush=True)
