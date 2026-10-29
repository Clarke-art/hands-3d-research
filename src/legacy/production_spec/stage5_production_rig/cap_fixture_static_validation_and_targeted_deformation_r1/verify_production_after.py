import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from qualification_common import *
import bpy
assert sha(CAND)==EXPECTED
ns={'bpy':bpy};reuse_functions(R1D/'blender_extract.py',['mesh_payload','rig_payload','weights'],ns)
bpy.ops.wm.open_mainfile(filepath=str(CAND),load_ui=False,use_scripts=False)
ob=bpy.data.objects['Hand  - Realistic'];rig=bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG']
live={'mesh':ns['mesh_payload'](ob),'rig':ns['rig_payload'](rig),'weights':ns['weights'](ob),'group_order':[g.name for g in ob.vertex_groups]}
before=read(OUT/'STATIC_LIVE_REOPEN_PAYLOAD.json');saved=read(R2D/'R2_CANDIDATE_CLEAN_REOPEN_PAYLOAD.json')
checks={k:live[k]==before[k]==saved[k] for k in live}
assert all(checks.values()) and digest(live['weights'])==VECTOR
after=inventory();beforehash=read(OUT/'FROZEN_HASHES_BEFORE.json')
assert after==beforehash
dump('FROZEN_HASHES_AFTER.json',after)
dump('PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json',{'status':'PASS','method':'Independent factory-startup Blender clean reopen after bounded measurement and rendering; historical whole-workspace hash comparison','candidate_sha256_before_and_after':sha(CAND),'weight_vector_sha256_before_and_after':digest(live['weights']),'checks':checks,'historical_files_unchanged_count':len(after),'changed_historical_paths':[],'new_paths_outside_qualification_directory':[],'PRODUCTION_WEIGHT_DRIFT':0,'GEOMETRY_DRIFT':0,'TOPOLOGY_DRIFT':0,'BONE_JOINT_DRIFT':0,'group_binding_UV_material_drift':0,'production_save_calls':0})
print('Independent clean reopen PASS; all historical files and production payload unchanged')
