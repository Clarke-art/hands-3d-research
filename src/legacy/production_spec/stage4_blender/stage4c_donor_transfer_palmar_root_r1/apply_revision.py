import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import bpy
assert read(OUT/'PALMAR_APPLICATION_PREREQUISITE_GATE_R1.json')['status']=='PASS'
assert not ASSET.exists(),'FAIL_CLOSED: application revision already exists'
gate=read(OUT/'PALMAR_APPLICATION_PREREQUISITE_GATE_R1.json')
for p in [WRITESET,TARGET]:assert sha(p)==gate['approved_write_set' if p==WRITESET else 'approved_target_payload']['sha256']
assert sha(SOURCE)==EXPECTED_SOURCE and sha(CANDIDATE)==EXPECTED_CANDIDATE
payload_provenance=payload_helpers(globals());C=read(TARGET)
# Only the frozen source scene is opened. No candidate/probe or historical modeling code is executed.
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False);before=snapshot();assert before==read(DESIGN/'CURRENT_STAGE4C_NATIVE_SNAPSHOT_R1.json')
assert before['coordinates_local_m']==C['source_local_m'] and [[x*1000 for x in p] for p in before['coordinates_world_m']]==C['source_world_mm']
assert before['protected']['mesh']['counts']==[3416,6828,3414] and not before['protected']['groups'] and not before['protected']['rigs']
ob=bpy.data.objects[before['object_name']];me=ob.data;topology_keys=['vertex_ids','edges','faces','loops','face_loop_ranges'];signature=digest({k:before['protected']['mesh'][k] for k in topology_keys});source_scene_props=props(bpy.context.scene)
for i in IDS:me.vertices[i].co=C['candidate_local_m'][i]
me.update();pre=snapshot();assert pre['protected']==before['protected'];assert pre['coordinates_local_m']==C['candidate_local_m']
changed=[i for i,(a,b) in enumerate(zip(before['coordinates_local_m'],pre['coordinates_local_m'])) if a!=b];assert changed==IDS
assert all(before['coordinates_local_m'][i]==pre['coordinates_local_m'][i] for i in read(WRITESET)['normal_locked_vertex_ids'])
metadata={'PHASE':PHASE,'GEOMETRY_HUMAN_APPROVED':True,'SOURCE_STAGE4C_SHA256':EXPECTED_SOURCE,'APPROVED_FORMAL_CANDIDATE_SHA256':EXPECTED_CANDIDATE,'DONOR_SOURCE_SHA256':EXPECTED_DONOR,'APPROVED_WRITE_SET_SHA256':sha(WRITESET),'APPROVED_TARGET_PAYLOAD_SHA256':sha(TARGET),'HUMAN_APPROVAL_RECEIPT_SHA256':sha(OUT/'HUMAN_PALMAR_DIGIT_ROOT_DONOR_RESTORATION_APPROVAL_R1.json'),'APPROVED16_NATIVE_LOCAL_SHA256':digest([[i,pre['coordinates_local_m'][i]] for i in IDS]),'MID_MCP_45_MANDATORY_DOWNSTREAM_REVALIDATION':True,'NEW_DERIVED_ASSET':True,'SOURCE_ASSET_PRESERVED':True,'DO_NOT_PROMOTE_UNTIL_DOWNSTREAM_REQUALIFIED':True,'PRODUCTION_PROMOTED':False,'STAGE5_PROPAGATED':False,'DEFORMATION_QUALIFIED':False,'FULL42_REQUALIFIED':False}
for k,v in metadata.items():bpy.context.scene['PALMAR_APPLICATION_'+k]=v
assert all(plain(bpy.context.scene[k])==v for k,v in source_scene_props.items())
dump('PALMAR_APPLICATION_BEFORE_SAVE_SNAPSHOT_R1.json',{'source_snapshot':before,'application_before_save_snapshot':pre,'source_scene_properties':source_scene_props,'authorized_scene_metadata':metadata,'topology_signature_sha256':signature,'actual_changed_ids':changed,'payload_helper_AST':payload_provenance,'source':ref(SOURCE),'coordinate_authority':ref(TARGET),'opened_asset_before_save':'SOURCE_STAGE4C_ONLY','target_recalculation_runs':0,'probe_reads':0,'pose_setters':0,'deformation_evaluations':0})
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(ASSET),copy=True,compress=False)
dump('PALMAR_APPLICATION_SAVE_LOG_R1.json',{'status':'SAVED_PENDING_FACTORY_CLEAN_REOPEN','new_asset':ref(ASSET),'saved_from_frozen_source_only':True,'exact16_native_local_assignments':True,'source_overwritten':False,'new_revision_save_calls':1,'existing_asset_save_calls':0,'revision_provenance_metadata_scene_only':metadata,'runtime':bpy.app.version_string})
print('Saved NEW Stage4C derived revision from frozen source; exact approved16 positions only; source preserved',flush=True)
