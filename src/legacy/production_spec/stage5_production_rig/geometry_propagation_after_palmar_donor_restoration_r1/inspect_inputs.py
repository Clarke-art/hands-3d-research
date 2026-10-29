import sys,copy
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from payload import *
paths=read(OUT/'PALMAR_STAGE5_INPUT_LINEAGE_RECOVERY_R1.json')['inputs'];result={}
for k,r in paths.items():
 p=Path(r['path']);assert sha(p)==EXPECTED[k];load(p);s=snapshot();s['source_scene_properties']=props(bpy.context.scene);s['native_editbone_rolls']=read_rolls_last();result[k]=s
 assert s['protected']['mesh']['counts']==[3416,6828,3414]
 print('Actual read-only native input',k,'bones',sum(len(r['bones']) for r in s['protected']['rigs'].values()),'groups',len(s['protected']['groups']),flush=True)
target=result['STAGE4'];normal=read(DESIGN/'PALMAR_ROOT_EXCLUDED_NORMAL_CONTEXT_R1.json')['vertex_ids']
def canonical_rig(s):
 r=copy.deepcopy(s['protected']['rigs'])
 for z in r.values():z['object'].pop('custom_properties')
 return r
for k in ('CORRECTED','R2'):
 s=result[k];assert all(s['protected']['mesh'][a]==target['protected']['mesh'][a] for a in ['counts','vertex_ids','edges','faces','loops','face_loop_ranges'])
 changed=[i for i,(a,b) in enumerate(zip(s['coordinates_local_m'],target['coordinates_local_m'])) if a!=b];assert changed==IDS
 assert len(next(iter(s['protected']['rigs'].values()))['bones'])==21
 assert canonical_rig(s)==canonical_rig(result['RIG_AUTHORITY'])
 assert s['native_editbone_rolls']==result['RIG_AUTHORITY']['native_editbone_rolls']
 assert all(s['coordinates_local_m'][i]==target['coordinates_local_m'][i] for i in normal)
 assert s['protected']['object']['matrices']==target['protected']['object']['matrices']
assert digest(result['R2']['positive_weight_vectors'])==WEIGHT_HASH,'FAIL_CLOSED_STAGE5_LINEAGE_INPUT_MISMATCH: weight hash'
dump('FROZEN_INPUT_NATIVE_PAYLOADS_R1.json',result)
dump('PALMAR_STAGE5_INPUT_PAYLOAD_PREFLIGHT_R1.json',{'status':'PASS','file_hashes_verified':True,'R2_WEIGHT_HASH':digest(result['R2']['positive_weight_vectors']),'CORRECTED_RIG_AUTHORITY_HASH':EXPECTED['RIG_AUTHORITY'],'both_source_rigs_match_canonical_corrected_authority':True,'cross_lineage_rig_metadata_only_ignored_for_authority_comparison':True,'all_original_per_source_metadata_preserved_by_full_snapshot':True,'native_rolls_match_authority':True,'both_existing_to_latest_geometry_delta_exact_palmar16':True,'native_topology_and_object_transforms_match':True,'bone_count_each':21,'payload_helper_AST':PROV,'native_roll_method':'Read EditBone.roll last in unsaved session; no setters or exiting edit mode/save'})
print('Native preflight PASS R2 weight authority exact /21 bones /16 delta /rolls exact',flush=True)
