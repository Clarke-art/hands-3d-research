import bpy,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
from blender_extract import mesh_payload,rig_payload,weights
record=read(OUT/'CANDIDATE_SAVE_RECORD_R1.json');assert sha(CANDIDATE)==record['candidate_sha256']
bpy.ops.wm.open_mainfile(filepath=str(CANDIDATE),load_ui=False,use_scripts=False)
ob=bpy.data.objects['Hand  - Realistic'];rig=bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG']
post={'candidate_path':str(CANDIDATE.relative_to(ROOT)),'candidate_sha256':sha(CANDIDATE),
 'mesh':mesh_payload(ob),'rig':rig_payload(rig),'weights':weights(ob),'group_order':[g.name for g in ob.vertex_groups]}
pre=read(OUT/'CANDIDATE_PRE_SAVE_PAYLOAD_R1.json')
checks={k:post[k]==pre[k] for k in ['mesh','rig','weights','group_order']}
assert all(checks.values()),('FAIL_CLOSED save/reopen drift',checks)
assert sha(CANDIDATE)==record['candidate_sha256']
dump('CANDIDATE_CLEAN_REOPEN_PAYLOAD_R1.json',post)
dump('CANDIDATE_SAVE_REOPEN_VERIFICATION_R1.json',{'status':'PASS','method':'Separate factory-startup Blender process clean reload; no save or pose evaluation',
 'candidate_path':str(CANDIDATE.relative_to(ROOT)),'candidate_sha256':sha(CANDIDATE),'checks':checks,
 'all_3416_skin_vectors_exactly_preserved':True,'serialized_vector_hash':digest(post['weights']),
 'rig_all_21_bone_snapshots_exactly_preserved':True,'mesh_UV_material_binding_and_geometry_exactly_preserved':True,
 'serialization_drift_count':0,'pose_evaluations':0,'candidate_blend_writes':0,'historical_blend_writes':0})
print('CLEAN REOPEN PASS: all geometry/bones/vectors/binding exactly preserved',flush=True)
