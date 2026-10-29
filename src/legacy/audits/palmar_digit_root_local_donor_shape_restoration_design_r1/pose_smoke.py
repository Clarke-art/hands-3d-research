import sys,math
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import bpy,numpy as np
from mathutils import Vector,Quaternion
assert read(OUT/'PALMAR_ROOT_STRUCTURE_AUDIT_R1.json')['status']=='PASS'
assert read(OUT/'PALMAR_ROOT_BIND_ZERO_PREVIEW_R1.json')['status']=='PASS'
payload_helpers(globals());C=read(OUT/'PALMAR_ROOT_FORMAL_TARGET_COORDINATES_R1.json');selection=read(OUT/'PALMAR_ROOT_WEIGHT_SUPPORT_FAMILY_R1.json');case_ids=selection['smoke_cases_selected'];assert len(case_ids)<=4
cases={c['case_id']:c for c in read(FULL/'FULL_STAGE6A_CASE_MATRIX_R1.json')['cases'] if c['case_id'] in case_ids};assert set(cases)==set(case_ids)
sn={'bpy':bpy,'math':math,'Vector':Vector,'Quaternion':Quaternion,'MM':1000.};prov=reuse(ROOT/'production_spec/stage6_deformation/stage6a/scripts/s6a_common.py',['reset_pose','set_joint_rotation','evaluate','pose_state'],sn)
def eval_pos(ob):
 bpy.context.view_layer.update();v,f=sn['evaluate'](ob,ob.matrix_world.copy());assert [list(p) for p in f]==C['faces'];return np.array([list(p) for p in v])*1000
def sample(path,expected):
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);s=snapshot();assert s['coordinates_local_m']==expected;ob=bpy.data.objects[s['object_name']];rig=bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG'];base=eval_pos(ob);out={};poses={}
 for cid in case_ids:
  c=cases[cid];assert c['axis']=='bone_local_X' and c['sign']==-1 and c['applied_rotation_deg']==-c['angle_deg']
  sn['reset_pose'](rig);sn['set_joint_rotation'](rig,c['bone'],c['applied_rotation_deg']);out[cid]=eval_pos(ob);poses[cid]=sn['pose_state'](rig)
  assert [b.name for b in rig.pose.bones if abs(b.rotation_quaternion.angle)>1e-7]==[c['bone']]
  sn['reset_pose'](rig);assert np.array_equal(base,eval_pos(ob));assert snapshot()['protected']==s['protected']
 assert snapshot()['coordinates_local_m']==expected
 return out,poses,s['protected']
baseline,poses,payload=sample(R2,C['source_local_m']);candidate,cposes,cpayload=sample(OUT/'TEMP_STAGE5B_PALMAR16_BIND_PREVIEW_DESIGN_ONLY.blend',C['candidate_local_m']);assert payload==cpayload and poses==cposes
frozen=read(FULL/'POSED_COORDINATES_R1.json')['positions_world_m'];deltas={cid:float(np.linalg.norm(baseline[cid]-np.array(frozen[cid])*1000,axis=1).max()) for cid in case_ids};assert max(deltas.values())<.0001
D=read(OUT/'TEMP_DOWNSTREAM_COORDINATES_R1.json')
for cid in case_ids:
 D['states']['CURRENT'][cid]=baseline[cid].tolist();D['states']['FORMAL_CANDIDATE'][cid]=candidate[cid].tolist()
D['pose_smoke_cases']=case_ids;D['formal_case_definitions']=cases;D['classification']='TEMPORARY LOCAL SMOKE ONLY; not FullStage6A PASS or deformation qualification'
dump('TEMP_DOWNSTREAM_COORDINATES_R1.json',D)
dump('PALMAR_ROOT_LOCAL_POSE_SMOKE_R1.json',{'status':'EVALUATED_PENDING_STRUCTURAL_AND_VISIBLE_REVIEW','POSE_SMOKE_COUNT':len(case_ids),'POSE_SMOKE_CASES':case_ids,'case_matrix_source':ref(FULL/'FULL_STAGE6A_CASE_MATRIX_R1.json'),'case_definitions':cases,'historical_local_X_minus1':True,'weight_support_selection':ref(OUT/'PALMAR_ROOT_WEIGHT_SUPPORT_FAMILY_R1.json'),'frozen_baseline_pose_reproduction_max_mm':deltas,'current_candidate_pose_state_exact':True,'pose_states':poses,'weights_groups_rig_protected_exact':True,'source_candidate_reset_after_every_case':True,'production_save_calls':0,'posed_blend_save_calls':0,'current9_answers_or_closure_writes':0,'not_Full42':True,'not_FullStage6A_PASS':True,'pose_helper_AST':prov})
print('TEMP LOCAL SMOKE evaluated',case_ids,'payload exact frozenbaseline',deltas,flush=True)
