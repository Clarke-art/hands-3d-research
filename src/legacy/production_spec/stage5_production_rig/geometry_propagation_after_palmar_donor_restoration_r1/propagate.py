import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from payload import *
assert read(OUT/'PALMAR_STAGE5_INPUT_PAYLOAD_PREFLIGHT_R1.json')['status']=='PASS'
frozen=read(OUT/'FROZEN_INPUT_NATIVE_PAYLOADS_R1.json');target=frozen['STAGE4']['coordinates_local_m'];results={};assert len(target)==3416 and sha(STAGE4)==EXPECTED['STAGE4']
for k in ('CORRECTED','R2'):
 p=SOURCES[k];asset=ASSETS[k];assert sha(p)==EXPECTED[k] and not asset.exists()
 load(p);before=snapshot();scene0=props(bpy.context.scene);assert before['protected']==frozen[k]['protected'] and before['coordinates_local_m']==frozen[k]['coordinates_local_m']
 ob=bpy.data.objects[before['object_name']]
 # Formal authority is the entire3416-vector payload, not a sparse16-point patch.
 for i,co in enumerate(target):ob.data.vertices[i].co=co
 ob.data.update();after=snapshot();assert after['coordinates_local_m']==target and after['protected']==before['protected']
 changed=[i for i,(a,b) in enumerate(zip(before['coordinates_local_m'],after['coordinates_local_m'])) if a!=b];assert changed==IDS
 if k=='R2':assert digest(after['positive_weight_vectors'])==WEIGHT_HASH
 metadata={'PHASE':PHASE,'SOURCE_STAGE5_PATH':str(p),'SOURCE_STAGE5_SHA256':sha(p),'LATEST_STAGE4C_PATH':str(STAGE4),'LATEST_STAGE4C_SHA256':sha(STAGE4),'COMPLETE_GEOMETRY_ASSIGNED_COUNT':3416,'SCOPE':'Geometry propagation only; original rig/weights/groups/modifiers frozen','MID_MCP_45_MANDATORY_REVALIDATION':'YES','WHOLE_HAND_SURFACE_INTEGRITY_BASELINE_REQUIRED':'YES','HISTORICAL_DESIGN_MID45_CANDIDATE_EDGE_RATIO':'0.477504-1.632646','HISTORICAL_DESIGN_PREVIOUS_CURRENT_EDGE_RATIO':'0.760663-1.577704','HISTORICAL_EDGE_RATIOS_CONTEXT_ONLY':True,'JOINT_RELOCATION_REQUIRED':'NOT_EVALUATED_THIS_PHASE','RIG_REBUILD_REQUIRED':'NO','WEIGHT_CHANGE_REQUIRED':'NO','PRODUCTION_PROMOTION':False,'DO_NOT_PROMOTE_UNTIL_DOWNSTREAM_REQUALIFIED':True,'QUALIFICATION':'joint/surface/rest/zero/bind/static skin/impact/targeted/Full42/whole-hand/Stage6B pending','NEXT_RECORDED_ONLY':NEXT,'USER_SCOPE_SHA256':sha(REQUEST)}
 for name,value in metadata.items():bpy.context.scene['PALMAR_STAGE5_'+name]=value
 assert all(plain(bpy.context.scene[name])==value for name,value in scene0.items()) and snapshot()['protected']==before['protected']
 bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(asset),copy=True,compress=False)
 results[k]={'before':before,'after':after,'source_scene_properties':scene0,'new_scene_provenance_metadata':metadata,'changed_ids':changed,'assigned_coordinate_count':3416,'asset':ref(asset)}
 print('Saved new independent',k,'complete3416 geometry / changed16',sha(asset),flush=True)
dump('PALMAR_STAGE5_BEFORE_SAVE_PAYLOADS_R1.json',results)
