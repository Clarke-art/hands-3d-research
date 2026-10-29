import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import bpy
records=read(OUT/'FULL_STAGE6A_MACHINE_EVIDENCE_R1.json')['historical_functions']+read(OUT/'EVIDENCE_RENDER_MANIFEST_R1.json')['renderer_functions']+read(OUT/'COMPLETE_NATIVE_CROSSING_CENSUS_R1.json')['methods']+read(OUT/'OLD_9_BLOCKER_FRESH_REMEASUREMENT_R1.json')['method']
checks={}
for i,r in enumerate(records):
 p=ROOT/r['source']['path'];checks[str(i)+'_source_bytes']=sha(p)==r['source']['sha256']
 nodes={n.name:digest(ast.dump(n)) for n in ast.parse(p.read_text(encoding='utf-8-sig')).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
 for n,h in r['function_AST_sha256'].items():checks[str(i)+'_'+n]=nodes[n]==h
# An independent clean reopen checks native current data after every qualification/render process.
ns={'bpy':bpy};reuse(S5/'targeted_rig_and_skin_data_rebuild_after_approval_r1/blender_extract.py',['mesh_payload','rig_payload','weights'],ns)
bpy.ops.wm.open_mainfile(filepath=str(CAND),load_ui=False,use_scripts=False)
ob=bpy.data.objects['Hand  - Realistic'];rig=bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG'];payload={'mesh':ns['mesh_payload'](ob),'rig':ns['rig_payload'](rig),'weights':ns['weights'](ob),'group_order':[g.name for g in ob.vertex_groups]}
old=read(OLD_CAND.parent/'R2_CANDIDATE_CLEAN_REOPEN_PAYLOAD.json');geo=read(CAND.parent/'R2_REOPENED_NATIVE_PAYLOAD_R1.json')
checks['weight_exact_all3416']=digest(payload['weights'])==EXPECTED_WEIGHTS and payload['weights']==old['weights']
checks['current_geometry_exact_reopened_receipt']=payload['mesh']['positions_local_m']==geo['coordinates_local_m']
for k,v in old['mesh'].items():
 if k not in ['positions_local_m','positions_world_mm']:checks['protected_mesh_'+k]=payload['mesh'][k]==v
checks['group_order_exact']=payload['group_order']==old['group_order']
checks['native_before_after_checks']=read(OUT/'HARNESS_ZERO_REOPEN_VERIFICATION.json')['all_case_memory_payload_unchanged']
bpy.ops.wm.open_mainfile(filepath=str(CORRECTED),load_ui=False,use_scripts=False)
checks['rig_equals_frozen_corrected_authority']=payload['rig']==ns['rig_payload'](bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG'])
checks['current_file_hash']=sha(CAND)==EXPECTED_CAND
dump('BLENDER_RUNTIME_SOURCE_AND_CLEAN_REOPEN_VERIFICATION_R1.json',{'status':'PASS' if all(checks.values()) else 'FAIL_CLOSED','checks':checks,'runtime':sys.version,'current_native_payload_digest':digest(payload),'extra_pose_applications':0,'production_saves':0,'raw_weight_hash':digest(payload['weights']),'runtime_AST_serialization_verified_in_originating_Blender_Python':True})
assert all(checks.values()),checks
print('ORIGINATING BLENDER AST + INDEPENDENT NATIVE CLEAN REOPEN PASS',flush=True)
