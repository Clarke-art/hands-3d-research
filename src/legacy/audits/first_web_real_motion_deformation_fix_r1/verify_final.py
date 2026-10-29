import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
inputs=check_inputs()
ob,rig=load(BASE);baseline=m.product_payload(ob,rig);baseline_shape=core.shape_payload(ob)
ob,rig=load(SOURCE);source=m.product_payload(ob,rig);oldshape=core.shape_payload(ob)
assert baseline==source and baseline_shape==oldshape
source_actions=actions();materials=[m.material_payload(x) for x in ob.data.materials if x]
source_details={b.name:{'settings':m.rna(b,omit=('color','collections')),'constraints':[m.rna(c,depth=2) for c in rig.pose.bones[b.name].constraints]} for b in rig.data.bones}
zero_before=Varray(ob)
ob,rig=load(CANDIDATE);after=m.product_payload(ob,rig);shape=core.shape_payload(ob)
assert all(source[k]==after[k] for k in source if k!='weights')
assert source_details=={b.name:{'settings':m.rna(b,omit=('color','collections')),'constraints':[m.rna(c,depth=2) for c in rig.pose.bones[b.name].constraints]} for b in rig.data.bones}
assert [m.material_payload(x) for x in ob.data.materials if x]==materials
assert shape['keys'][:-1]==oldshape['keys'] and shape['drivers'][:-1]==oldshape['drivers']
assert len(shape['keys'])==len(oldshape['keys'])+1
assert [list(v.co) for v in ob.data.shape_keys.key_blocks['Basis'].data]==baseline['positions_local_m']
assert actions()==source_actions
region=set(read(OUT/'WEIGHT_ITERATION_2_R1.json')['region_vertex_ids'])
allowed_groups={source['groups'].index(n) for n in ['WRIST_R','THUMB_CMC_R','THUMB_MCP_R','INDEX_MCP_R']}
changed=[]
for i,(a,b) in enumerate(zip(source['weights'],after['weights'])):
    if a!=b:
        assert i in region
        assert {g:w for g,w in a if g not in allowed_groups}=={g:w for g,w in b if g not in allowed_groups}
        assert abs(sum(w for g,w in a)-sum(w for g,w in b))<2e-7
        changed.append(i)
newkey=ob.data.shape_keys.key_blocks['FIRST_WEB_REAL_MOTION_CORRECTIVE_R1']
assert newkey.value==0
V0=Varray(ob);zero_error=float(np.linalg.norm(V0-zero_before,axis=1).max()*1000)
components=[]
for i in range(421):
    motion(rig,1+i//2,(i%2)/2)
    components.append({'source_frame':690+i,'scene_frame':1+i/2,
        'INDEX_MCP_anatomical_abduction_rad':float(ob['_FW_INDEX_ABDUCTION_R1']),
        'THUMB_CMC_calibrated_swing_elevation_rad':float(ob['_FW_THUMB_SWING_ELEVATION_R1']),
        'new_corrective_value':float(newkey.value)})
neutral(rig)
assert newkey.value==0 and np.linalg.norm(Varray(ob)-V0,axis=1).max()==0
assert actions()==source_actions and check_inputs()==inputs
dump('FINAL_ASSET_PROTECTION_R1.json',{'status':'PASS','candidate_path':CANDIDATE.relative_to(ROOT).as_posix(),'candidate_sha256':sha(CANDIDATE),
    'source_baseline_sha256':core.BASE_SHA,'source_motion_test_sha256':SOURCE_SHA,
    'basis_vertex_position_writes':0,'basis_mesh_positions_and_shape_exact':True,'topology_vertex_IDs_UV_materials_modifiers_transforms_exact':True,
    'bone_count':len(rig.data.bones),'bone_hierarchy_rest_joints_roll_inherit_constraints_thumb_chain_exact':True,
    'same_source_mapping_2_smoothing_Action_keys_timing':True,'all_source_Action_payload_hashes':source_actions,
    'only_authorized_local_weights_changed':True,'all_outside_weights_exact':True,'other_influences_exact':True,
    'changed_weight_vertex_count':len(changed),'changed_weight_vertex_ids':changed,
    'existing_shape_and_driver_exact':True,'new_corrective_count':1,'new_corrective_vertex_count':len(read(OUT/'REAL_MOTION_CORRECTIVE_R1.json')['changed_vertex_ids']),
    'new_corrective_ZERO_value':float(newkey.value),'ZERO_before_after_max_mm':zero_error,'ZERO_restore':'PASS','ZERO_restore_max_mm':0,
    'TIP_non_deform_rule_unchanged':True,'fingertip_mapping_weights_corrective_unchanged':True,
    'new_source_Action_channels':0,'forbidden_forensic_runs':0,'all_input_hashes_unchanged':True,'input_hashes':inputs,
    'no_saved_asset_modified_during_verification':True})
dump('REAL_MOTION_CORRECTIVE_COMPONENT_TRACE_R1.json',{'observations':421,'frames':components,
    'note':'Only trace of the two already-defined anatomical components and new scalar driver through the SAME action; no further causal tests or severity census.'})
print('FINAL_INDEPENDENT_PROTECTION_PASS','ZERO_DIFF_MM',zero_error,'BASIS_WRITES_0',flush=True)
