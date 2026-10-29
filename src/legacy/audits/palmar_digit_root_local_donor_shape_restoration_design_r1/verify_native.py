import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import bpy,numpy as np
payload_helpers(globals());C=read(OUT/'PALMAR_ROOT_FORMAL_TARGET_COORDINATES_R1.json');ids=C['vertex_ids']
def load_snapshot(path):
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);return snapshot()
source=load_snapshot(CURRENT);assert source==read(OUT/'CURRENT_STAGE4C_NATIVE_SNAPSHOT_R1.json');candidate=load_snapshot(CANDIDATE)
assert candidate==read(OUT/'FORMAL_CANDIDATE_NATIVE_SNAPSHOT_R1.json')
assert all(bpy.context.scene['PALMAR_'+k] for k in ['DESIGN_ONLY','NOT_PRODUCTION','NOT_HUMAN_APPROVED','DO_NOT_PROMOTE'])
assert source['protected']==candidate['protected'];assert not candidate['protected']['groups'] and not candidate['protected']['rigs']
assert candidate['coordinates_local_m']==C['candidate_local_m'];assert (np.array(candidate['coordinates_world_m'])*1000).tolist()==C['candidate_world_mm']
changed=[i for i,(a,b) in enumerate(zip(source['coordinates_local_m'],candidate['coordinates_local_m'])) if a!=b];assert changed==ALLOWED
probe=load_snapshot(FEAS/'TEMP_PALMAR_ROOT_DONOR_TRANSFER_PROBE_R1.blend');assert probe['coordinates_local_m']==candidate['coordinates_local_m'];assert probe['coordinates_world_m']==candidate['coordinates_world_m']
temp=load_snapshot(OUT/'TEMP_STAGE5B_PALMAR16_BIND_PREVIEW_DESIGN_ONLY.blend');currentrig=load_snapshot(R2);assert currentrig['protected']==temp['protected'];assert temp['coordinates_local_m']==candidate['coordinates_local_m']
assert all(temp['coordinates_local_m'][i]==currentrig['coordinates_local_m'][i] for i in range(3416) if i not in set(ids))
dump('INDEPENDENT_NATIVE_REOPEN_VERIFICATION_R1.json',{'status':'PASS','source':ref(CURRENT),'candidate':ref(CANDIDATE),'probe':ref(FEAS/'TEMP_PALMAR_ROOT_DONOR_TRANSFER_PROBE_R1.blend'),'temporary_downstream':ref(OUT/'TEMP_STAGE5B_PALMAR16_BIND_PREVIEW_DESIGN_ONLY.blend'),'protected_source_candidate_exact':True,'actual_reopened_probe_candidate_local_world_exact':True,'actual_changed_native_ids':changed,'candidate_has_no_groups_or_armature':True,'design_flags_actual_scene_verified':True,'temporary_downstream_weights_rig_groups_exact':True,'production_save_calls':0,'candidate_save_calls':0,'separate_Blender_process':True})
print('Independent native reopen PASS: source/candidate/probe/temp; protected payload exact; geometry-only formal asset',flush=True)
