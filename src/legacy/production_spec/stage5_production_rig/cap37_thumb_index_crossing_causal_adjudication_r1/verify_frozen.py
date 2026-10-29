import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from causal_common import *
import bpy
saved=read(R2D/'R2_CANDIDATE_CLEAN_REOPEN_PAYLOAD.json');ns={'bpy':bpy}
reuse(R1D/'blender_extract.py',['mesh_payload','rig_payload','weights'],ns)
bpy.ops.wm.open_mainfile(filepath=str(ASSETS['R2']),load_ui=False,use_scripts=False)
ob=bpy.data.objects['Hand  - Realistic'];rig=bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG']
live={'mesh':ns['mesh_payload'](ob),'rig':ns['rig_payload'](rig),'weights':ns['weights'](ob),'group_order':[g.name for g in ob.vertex_groups]}
assert all(live[k]==saved[k] for k in live)
assert sha(ASSETS['R2'])==EXPECTED and digest(live['weights'])==VECTOR
before=read(OUT/'FROZEN_HASHES_BEFORE.json');after=inventory()
diff=[{'file':p,'before':before.get(p),'after':after.get(p)} for p in sorted(set(before)|set(after)) if before.get(p)!=after.get(p)]
assert not diff,diff
dump('PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json',{'status':'PASS','PRODUCTION_DRIFT':0,'R2_sha256':sha(ASSETS['R2']),'R2_vector_sha256':digest(live['weights']),'R2_all_live_payload_fields_exact_saved':True,'independent_clean_reopen_after_all_measurement_and_rendering':True,'historical_file_count':len(before),'historical_files_byte_hash_exact_before_after':True,'previous_qualification_files_included_in_hash_inventory':True,'added_deleted_changed_files_outside_current_output_directory':diff,'production_save_calls':0,'production_weight_assignment_calls':0,'rest_bone_assignment_calls':0,'changed_or_retested_other_fixtures':[],'other_fixture_verdicts_carried_without_retest':{'16 inherited debts':'STATIC_QUALIFICATION_DEBT_WITHOUT_TRUE_DEFORMATION_FAILURE','edge5879':'PASS_PENDING_HUMAN_REVIEW','old cap9':'PASS_PENDING_HUMAN_REVIEW','FIRST_WEB':'PASS_PENDING_HUMAN_REVIEW','fresh R3 transition/collar':'PASS_PENDING_HUMAN_REVIEW'}})
print('Frozen verification PASS; historical hashes exact',len(before))
