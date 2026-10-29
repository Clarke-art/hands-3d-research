import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import bpy
source=S5/'geometry_propagation_after_donor_transfer_r1/payload.py'
reuse_record=reuse(source,['plain','props','rna','object_payload','rig_payload','material_payload','snapshot','load'],globals())
result={}
for key,p in FILES.items():
 assert sha(p)==EXPECTED[key]
 load(p)
 data=snapshot()
 data['protected']['object']['custom_properties']=props(bpy.data.objects[data['object_name']])
 ob=bpy.data.objects[data['object_name']]
 data['group_order']=[g.name for g in ob.vertex_groups]
 data['dense_float32_rows']=[[dict((g.group,float(g.weight)) for g in v.groups).get(j,0.0) for j in range(len(ob.vertex_groups))] for v in ob.data.vertices]
 # Retain the actual sparse order and explicit zeros in addition to the dense zero-completed payload.
 data['source']=ref(p)
 data['blender_version']=bpy.app.version_string
 if key=='CURRENT':
  h=digest(data['positive_weight_vectors'])
  dump('STATIC_SKIN_WEIGHT_PAYLOAD_PREFLIGHT_R1.json',{'R2_WEIGHT_VECTOR_HASH':h,'match':h==WEIGHT_HASH,'count':len(data['positive_weight_vectors'])})
  if h!=WEIGHT_HASH:
   dump(PHASE+'_STATUS.json',{'VERDICT':'FAIL_CLOSED_STATIC_SKIN_PAYLOAD_DRIFT','STOP':True,'POSE_RUNS':0,'STAGE6_RUNS':0})
   raise RuntimeError('FAIL_CLOSED_STATIC_SKIN_PAYLOAD_DRIFT')
 dump(key+'_CLEAN_REOPEN_NATIVE_PAYLOAD_R1.json',data)
 result[key]={'source':ref(p),'weight_hash':digest(data['positive_weight_vectors']),'protected_payload_hash':digest(data['protected'])}
 print('CLEAN REOPEN READONLY',key,'PASS',flush=True)
dump('READONLY_FUNCTION_REUSE_R1.json',reuse_record)
dump('CLEAN_REOPEN_EXTRACTION_R1.json',{'status':'PASS','Blender_version':bpy.app.version_string,'sources':result,'save_calls':0,'weight_write_calls':0,'pose_runs':0,'Stage6_runs':0,'evaluated_deformation_reads':0,'mode_switches':0})
