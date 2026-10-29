import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import bpy,numpy as np
from mathutils import Vector
payload_helpers(globals());C=read(OUT/'PALMAR_ROOT_FORMAL_TARGET_COORDINATES_R1.json');W=read(OUT/'PALMAR_ROOT_FORMAL_WRITE_SET_R1.json');ids=W['vertex_ids']
assert sha(CURRENT)==EXPECTED_CURRENT and not CANDIDATE.exists()
bpy.ops.wm.open_mainfile(filepath=str(CURRENT),load_ui=False,use_scripts=False);before=snapshot();assert before==read(OUT/'CURRENT_STAGE4C_NATIVE_SNAPSHOT_R1.json')
ob=bpy.data.objects[before['object_name']];inv=ob.matrix_world.inverted()
for i in ids:ob.data.vertices[i].co=inv@(Vector(C['mathematical_target_world_mm'][i])/1000)
ob.data.update();pre=snapshot();assert pre['protected']==before['protected']
for k in ['DESIGN_ONLY','NOT_PRODUCTION','NOT_HUMAN_APPROVED','DO_NOT_PROMOTE']:bpy.context.scene['PALMAR_'+k]=True
bpy.context.scene['PALMAR_SOURCE_SHA256']=EXPECTED_CURRENT
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(CANDIDATE),copy=True,compress=False)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.wm.open_mainfile(filepath=str(CANDIDATE),load_ui=False,use_scripts=False);after=snapshot()
assert after==pre;assert before['protected']==after['protected'];assert not after['protected']['groups'] and not after['protected']['rigs']
changed=[i for i,(a,b) in enumerate(zip(before['coordinates_local_m'],after['coordinates_local_m'])) if a!=b];assert changed==ids
assert all(before['coordinates_local_m'][i]==after['coordinates_local_m'][i] for i in W['normal_locked_vertex_ids'])
actual=np.array(after['coordinates_world_m'])*1000;errs=np.linalg.norm(actual[ids]-np.array(C['mathematical_target_world_mm'])[ids],axis=1)
assert errs.max()<.0002
P=read(FEAS/'TEMP_PALMAR_ROOT_DONOR_TRANSFER_PROBE_R1.json');dp=np.linalg.norm(actual[ids]-np.array(P['world_mm'])[ids],axis=1);assert dp.max()==0,'FAIL_CLOSED_FORMAL_RESTORATION_REPRODUCTION: formal/probe saved coordinates differ'
C.update(candidate_world_mm=actual.tolist(),candidate_local_m=after['coordinates_local_m'],formal_candidate=ref(CANDIDATE),MAX_COORD_DELTA_VS_PROBE_MM=float(dp.max()),WRITE_SET_IDENTITY_MATCH_VS_PROBE=True)
dump('PALMAR_ROOT_FORMAL_TARGET_COORDINATES_R1.json',C);dump('FORMAL_CANDIDATE_NATIVE_SNAPSHOT_R1.json',after)
dump('PALMAR_ROOT_PAYLOAD_PROTECTION_R1.json',{'status':'PASS','all_protected_fields_exact':True,'protected_fields':list(before['protected']),'protected_sha256':digest(before['protected']),'native_V_E_F':after['protected']['mesh']['counts'],'actual_changed_vertex_ids':changed,'OUTSIDE16_POSITION_DRIFT':0,'NORMAL69_POSITION_DRIFT':0,'TOPOLOGY_DRIFT':0,'UV_DRIFT':0,'MATERIAL_DRIFT':0,'NORMAL_FLAG_CUSTOM_STATE_DRIFT':0,'RSSF_AUTHORITY_DRIFT':0,'added_groups_weights_rigs':0,'groups_count':len(after['protected']['groups']),'rig_count':len(after['protected']['rigs']),'save_reopen_serialization_drift':0,'design_only_candidate':ref(CANDIDATE),'source':ref(CURRENT),'production_save_calls':0})
dump('PALMAR_ROOT_SOURCE_SHAPE_FIDELITY_R1.json',{'status':'PASS','metric':'Euclidean coordinate error to exact ancestry-derived mathematical target; not nearest surface','max_mm':float(errs.max()),'mean_mm':float(errs.mean()),'RMS_mm':float(np.sqrt(np.mean(errs**2))),'p95_mm':float(np.percentile(errs,95)),'per_vertex_error_mm':dict(zip(map(str,ids),errs.tolist())),'native_float32_transform_roundtrip_bound_mm':.0002,'MAX_COORD_DELTA_VS_PROBE_MM':float(dp.max()),'formal_probe_saved_world_coordinates_exact':True,'design_only':True})
print('Formal Stage4C-only clone saved/reopened PASS; outside0 normal0; exact saved probe equality; fidelity max',errs.max(),flush=True)
