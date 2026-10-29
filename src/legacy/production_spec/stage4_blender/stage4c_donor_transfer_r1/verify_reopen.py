import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import bpy,numpy as np
exec(compile((DESIGN/'payload.py').read_text(encoding='utf-8-sig'),str(DESIGN/'payload.py'),'exec'),globals())
C=read(DESIGN/'FORMAL_DONOR_TRANSFER_COORDINATES_R1.json');pre=read(OUT/'APPLICATION_BEFORE_SAVE_SNAPSHOT_R1.json')
def snapshot(path):
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 ob=bpy.data.objects['Hand  - Realistic'];me=ob.data
 return ob,{'local_m':[list(v.co) for v in me.vertices],'world_mm':[[z*1000 for z in <REDACTED_EMAIL>] for v in me.vertices],'protected_payload':protected(ob),'native_vertex_ids':[v.index for v in me.vertices],'native_edge_ids':[e.index for e in me.edges],'native_face_ids':[f.index for f in me.polygons]}
ob,ap=snapshot(ASSET)
assert ap['local_m']==pre['application_before_save_local_m']==C['candidate_local_m']
assert ap['world_mm']==pre['application_before_save_world_mm']==C['candidate_world_mm']
assert ap['protected_payload']==pre['protected_payload']
assert len(ob.vertex_groups)==0 and not ap['protected_payload']['armatures']
metadata={k:plain(ob[k]) for k in ob.keys() if k.startswith('AMENDMENT_')}
assert metadata=={'AMENDMENT_'+k:v for k,v in pre['authorized_metadata'].items()}
application=ap
bpy.ops.wm.read_factory_settings(use_empty=True)
_,ca=snapshot(CANDIDATE);assert sha(CANDIDATE)==EXPECTED_CANDIDATE
assert ca==application, 'FAIL_CLOSED approved candidate / saved application actual geometry or protected payload differs'
changed=[i for i,(a,b) in enumerate(zip(pre['source_local_m'],ap['local_m'])) if a!=b];assert changed==IDS
delta=(np.array(ap['local_m'])[IDS]-np.array(C['candidate_local_m'])[IDS])*1000;eu=np.linalg.norm(delta,axis=1)
write={'status':'PASS','APPROVED_WRITE_COUNT':54,'ACTUAL_CHANGED_VERTEX_COUNT':len(changed),'actual_changed_vertex_ids':changed,'OUTSIDE54_POSITION_DRIFT_COUNT':sum(i not in IDS for i in changed),'MAX_ABSOLUTE_COORDINATE_DELTA_MM':float(np.abs(delta).max()),'MAX_EUCLIDEAN_COORDINATE_DELTA_MM':float(eu.max()),'MEAN_EUCLIDEAN_COORDINATE_DELTA_MM':float(eu.mean()),'RMS_EUCLIDEAN_COORDINATE_DELTA_MM':float(np.sqrt(np.mean(eu**2))),'coordinate_semantics':'Approved candidate_local_m already contains native float32 storage values. Direct native assignment/save/factory-clean reopen is exactly equal, no additional tolerance or rounding allowed.','per_vertex':[{'vertex_id':i,'approved_local_m':C['candidate_local_m'][i],'actual_saved_local_m':ap['local_m'][i],'absolute_component_delta_mm':np.abs(delta[j]).tolist(),'Euclidean_delta_mm':float(eu[j])} for j,i in enumerate(IDS)],'approved_coordinate_payload':ref(DESIGN/'FORMAL_DONOR_TRANSFER_COORDINATES_R1.json'),'source':ref(SOURCE),'application':ref(ASSET)}
dump('APPLICATION_WRITE_VERIFICATION_R1.json',write)
dump('APPLICATION_GEOMETRY_EQUIVALENCE_R1.json',{'status':'PASS','APPROVED_CANDIDATE_TO_APPLICATION_GEOMETRY_EQUIVALENCE':'PASS','compared_actual_native_reopened_blends':True,'candidate':ref(CANDIDATE),'application':ref(ASSET),'positions_exact':True,'edges_faces_cycles_ids_exact':True,'UV_coordinates_connectivity_exact':True,'materials_assignments_nodes_exact':True,'smooth_sharp_flags_exact':True,'custom_normal_state_exact':True,'all_other_protected_payload_exact':True,'protected_payload_sha256':digest(ap['protected_payload']),'geometry_with_ids_and_protected_payload_sha256':digest(ap),'ignored_metadata_only':'Only AMENDMENT_* object provenance properties differ: historical design flags vs new application receipt/source/phase/not-promoted flags. Existing custom properties retained.','no_added_groups_armature_weights_bones':True})
dump('APPLICATION_SAVE_REOPEN_AUDIT_R1.json',{'status':'PASS','SAVE_REOPEN':'PASS','separate_process_factory_startup':True,'actual_asset_native_coordinates_re_read':True,'pre_save_and_reopened_positions_local_world_exact':True,'SERIALIZATION_GEOMETRY_DRIFT':0,'OUTSIDE54_POSITION_DRIFT':0,'topology_UV_material_payload_drift':0,'metadata_exact':True,'application':ref(ASSET),'approved54_native_local_sha256':digest([[i,ap['local_m'][i]] for i in IDS])})
dump('APPLICATION_NATIVE_GEOMETRY_R1.json',{'source_local_m':pre['source_local_m'],'source_world_mm':pre['source_world_mm'],'application_local_m':ap['local_m'],'application_world_mm':ap['world_mm'],'approved_candidate_world_mm':ca['world_mm'],'faces':ap['protected_payload']['faces'],'edges':ap['protected_payload']['edges'],'smooth_flags':ap['protected_payload']['smooth_flags'],'native_V_E_F':[3416,6828,3414],'native_IDs_exact':True,'application_metadata':metadata,'reopened_geometry_sha256':digest(ap)})
print('FACTORY CLEAN REOPEN PASS; saved application actual native payload exactly equals approved candidate; changed54/outside0/serialization0',flush=True)
