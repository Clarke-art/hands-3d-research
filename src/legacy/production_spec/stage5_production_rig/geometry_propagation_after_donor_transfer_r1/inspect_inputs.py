import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from payload import *
result={}
for k,p in inputs().items():
 assert sha(p)==EXPECTED[k]
 load(p);s=snapshot();s['native_editbone_rolls']=read_rolls_last();result[k]=s
 assert s['protected']['mesh']['counts']==[3416,6828,3414]
 print('INPUT READ',k,s['object_name'],'rigs',list(s['protected']['rigs']),'groups',len(s['protected']['groups']),flush=True)
dump('FROZEN_INPUT_NATIVE_PAYLOADS_R1.json',result)
topkeys=['counts','vertex_ids','edges','faces','loops','face_loop_ranges']
for k in ('CORRECTED','R2'):
 assert all(result[k]['protected']['mesh'][f]==result['STAGE4']['protected']['mesh'][f] for f in topkeys)
 changed=[i for i,(a,b) in enumerate(zip(result[k]['coordinates_local_m'],result['STAGE4']['coordinates_local_m'])) if a!=b]
 assert changed==IDS,(k,len(changed),changed)
 assert len(next(iter(result[k]['protected']['rigs'].values()))['bones'])==21
import copy
a=copy.deepcopy(result['CORRECTED']['protected']['rigs']);b=copy.deepcopy(result['R2']['protected']['rigs'])
for r in [a,b]:
 for v in r.values():v['object'].pop('custom_properties')
assert a==b,'Current R2 native rig does not equal corrected authority'
assert result['CORRECTED']['native_editbone_rolls']==result['R2']['native_editbone_rolls']
assert digest(result['R2']['positive_weight_vectors'])==WEIGHT_HASH
dump('STAGE5_INPUT_PAYLOAD_PREFLIGHT_R1.json',{'status':'PASS','all_native_topology_equal':True,'both_expected_geometry_delta_ids':IDS,'bone_count_each':21,'R2_native_rig_equals_current_corrected_authority':True,'cross_source_historical_rig_metadata_difference_only':True,'per_source_all_metadata_will_be_preserved':True,'R2_positive_weight_vector_sha256':digest(result['R2']['positive_weight_vectors']),'explicit_roll_read_method':'EditBone.roll read last in unsaved temporary session; no edit setters, no mode exit or save'})
print('PREFLIGHT PASS',flush=True)
