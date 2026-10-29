import bpy,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
from blender_extract import mesh_payload,rig_payload,weights
assert not CANDIDATE.exists(),'FAIL_CLOSED: never overwrite an existing candidate'
DATA=read(OUT/'LIVE_SOURCE_DATA_R1.json');PAY=read(OUT/'CANDIDATE_WEIGHT_PAYLOAD_R1.json')
VERIFY=read(OUT/'APPROVAL_AND_INPUT_HASH_VERIFICATION_R1.json');CONT=read(PROPOSAL/'SKIN_WEIGHT_CONTINUITY_CONTRACT_R1.json')
for f,h in VERIFY['proposal_component_hashes'].items():assert sha(PROPOSAL/f)==h
assert sha(CORRECTED)==VERIFY['corrected_rig_sha256'] and sha(STAGE4)==VERIFY['Stage4C_geometry_source_sha256']
assert sha(DONOR)==VERIFY['R1B_donor_sha256'] and sha(RESPONSE)==VERIFY['response_sha256']
assert digest(PAY['weights'])==PAY['vector_hash']
bpy.ops.wm.open_mainfile(filepath=str(CORRECTED),load_ui=False,use_scripts=False)
ob=bpy.data.objects['Hand  - Realistic'];rig=bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG']
assert mesh_payload(ob)==DATA['CORRECTED']['mesh'] and rig_payload(rig)==DATA['CORRECTED']['rig']
original_materials=list(ob.data.materials)
# Import the frozen Stage4C geometry datablock directly. Keep the corrected source
# object's exact origin/transforms and all approved rig bones unchanged.
with bpy.data.libraries.load(str(STAGE4),link=False) as (source,target):
    assert 'Hand  - Realistic' in source.objects
    target.objects=['Hand  - Realistic']
supplier=target.objects[0];assert supplier is not None
ob.data=supplier.data
assert len(original_materials)==len(ob.data.materials)
for i,m in enumerate(original_materials):ob.data.materials[i]=m
bpy.data.objects.remove(supplier,do_unlink=True)
M=mesh_payload(ob)
for k in ['positions_local_m','positions_world_mm','edges','faces','face_material_indices','UV_layers','material_slots']:
    assert M[k]==DATA['STAGE4C']['mesh'][k],('FAIL_CLOSED frozen geometry',k)
assert len(ob.vertex_groups)==0 and not any(m.type=='ARMATURE' for m in ob.modifiers)
for g in DATA['R1B']['group_order']:ob.vertex_groups.new(name=g)
assert set(g.name for g in ob.vertex_groups)==set(CONT['deform_bones'])
VG={g.name:g for g in ob.vertex_groups}
for i,w in enumerate(PAY['weights']):
    for g,value in w.items():
        assert g in VG and value>0
        VG[g].add([i],value,'REPLACE')
bind=ob.modifiers.new(name='PRODUCTION_ARMATURE',type='ARMATURE');bind.object=rig
donor=DATA['R1B']['mesh']['modifiers'][0]
for k in ['use_deform_preserve_volume','use_vertex_groups','use_bone_envelopes','show_viewport','show_render']:setattr(bind,k,donor[k])
# Modifier binding works with both objects in their frozen aligned spaces; no
# reparenting or transform application is necessary. Preserve corrected hierarchy.
assert ob.parent is None and DATA['CORRECTED']['mesh']['parent'] is None
actual=weights(ob);assert actual==PAY['weights'],'FAIL_CLOSED pre-save vector storage drift'
assert rig_payload(rig)==DATA['CORRECTED']['rig']
PRE={'candidate_path':str(CANDIDATE.relative_to(ROOT)),'mesh':mesh_payload(ob),'rig':rig_payload(rig),
 'weights':actual,'group_order':[g.name for g in ob.vertex_groups],'vector_hash':digest(actual),
 'geometry_source':str(STAGE4.relative_to(ROOT)),'rig_source':str(CORRECTED.relative_to(ROOT)),
 'donor_source':str(DONOR.relative_to(ROOT)),'armature_binding':'Modifier only; frozen source object hierarchy/origin retained',
 'pose_evaluations':0,'Stage6_runs':0,'R3_reruns':0}
dump('CANDIDATE_PRE_SAVE_PAYLOAD_R1.json',PRE)
rig['candidate_phase']=PHASE;rig['Human_approval_sha256']=VERIFY['response_sha256']
rig['proposal_bundle_hash']=VERIFY['proposal_bundle_hash'];rig['candidate_only_not_production_promoted']=True
rig['candidate_geometry_source_SHA256']=sha(STAGE4);rig['candidate_weight_donor_SHA256']=sha(DONOR)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(CANDIDATE),copy=True,compress=False)
dump('CANDIDATE_SAVE_RECORD_R1.json',{'status':'SAVED_PENDING_CLEAN_REOPEN_VERIFICATION','candidate_path':str(CANDIDATE.relative_to(ROOT)),
 'candidate_sha256':sha(CANDIDATE),'bytes':CANDIDATE.stat().st_size,'candidate_blend_writes':1,'historical_blend_writes':0,
 'Stage6_runs':0,'R3_reruns':0,'pose_evaluations':0,'production_promoted':False})
print('NEW CANDIDATE SAVED:',CANDIDATE,'SHA256',sha(CANDIDATE),flush=True)
