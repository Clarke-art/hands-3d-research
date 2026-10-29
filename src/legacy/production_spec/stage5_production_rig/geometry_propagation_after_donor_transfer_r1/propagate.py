import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from payload import *
assert read(OUT/'STAGE5_INPUT_PAYLOAD_PREFLIGHT_R1.json')['status']=='PASS'
frozen=read(OUT/'FROZEN_INPUT_NATIVE_PAYLOADS_R1.json');target=frozen['STAGE4']['coordinates_local_m']
assert sha(STAGE4)==EXPECTED['STAGE4']
results={}
for k in ('CORRECTED','R2'):
 p=inputs()[k];asset=ASSETS[k]
 assert sha(p)==EXPECTED[k] and not asset.exists()
 load(p);before=snapshot()
 assert before['protected']==frozen[k]['protected'] and before['coordinates_local_m']==frozen[k]['coordinates_local_m']
 ob=bpy.data.objects[before['object_name']]
 assert not any(x.startswith('GEOMETRY_PROPAGATION_') for x in ob.keys())
 # Full native Stage4C geometry is the authority. Assign all 3416 stored coordinates.
 for v,co in zip(ob.data.vertices,target):v.co=co
 ob.data.update()
 after=snapshot()
 assert after['coordinates_local_m']==target
 assert after['protected']==before['protected'],'FAIL_CLOSED_STAGE5_GEOMETRY_PROPAGATION: protected payload drift'
 changed=[i for i,(a,b) in enumerate(zip(before['coordinates_local_m'],after['coordinates_local_m'])) if a!=b]
 assert changed==IDS,'FAIL_CLOSED_STAGE5_GEOMETRY_PROPAGATION: unexpected coordinate changes'
 assert after['positive_weight_vectors']==before['positive_weight_vectors']
 if k=='R2':assert digest(after['positive_weight_vectors'])==WEIGHT_HASH
 metadata={'PHASE':PHASE,'SOURCE_STAGE5_PATH':str(p),'SOURCE_STAGE5_SHA256':sha(p),'SOURCE_STAGE4C_PATH':str(STAGE4),'SOURCE_STAGE4C_SHA256':sha(STAGE4),'SCOPE':'Full 3416 native coordinate propagation only; existing rig/weight/binding frozen','QUALIFICATION':'Geometry propagation verified only; joint/rest/zero/bind/skin/cap/deformation pending','PRODUCTION_PROMOTION':False,'DO_NOT_PROMOTE_UNTIL_DOWNSTREAM_REQUALIFIED':True,'NEXT_RECORDED_ONLY':'JOINT_SURFACE_REST_ZERO_BIND_REVALIDATION_AFTER_DONOR_TRANSFER_R1','USER_SCOPE_SHA256':read(OUT/'USER_PHASE_SCOPE_REFERENCE.json')['sha256']}
 names={'DO_NOT_PROMOTE_UNTIL_DOWNSTREAM_REQUALIFIED':'DOWNSTREAM_GATE_REQUIRED'}
 for name,value in metadata.items():ob['GEOMETRY_PROPAGATION_'+names.get(name,name)]=value
 assert snapshot()['protected']==before['protected']
 bpy.ops.wm.save_as_mainfile(filepath=str(asset),check_existing=False)
 results[k]={'before':before,'after':after,'new_provenance_metadata':metadata,'changed_ids':changed,'assigned_coordinate_count':3416,'asset':ref(asset)}
 print('SAVED',k,sha(asset),flush=True)
dump('STAGE5_BEFORE_SAVE_PROPAGATION_PAYLOADS_R1.json',results)
