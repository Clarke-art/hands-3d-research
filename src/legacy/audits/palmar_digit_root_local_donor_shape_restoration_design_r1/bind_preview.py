import sys,math
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import bpy,numpy as np
from mathutils import Vector,Quaternion
assert read(OUT/'PALMAR_ROOT_STRUCTURE_AUDIT_R1.json')['status']=='PASS'
payload_helpers(globals());C=read(OUT/'PALMAR_ROOT_FORMAL_TARGET_COORDINATES_R1.json');core=read(OUT/'PALMAR_ROOT_DEFECT_CORE_R1.json');normal=read(OUT/'PALMAR_ROOT_EXCLUDED_NORMAL_CONTEXT_R1.json');ids=C['vertex_ids']
sn={'bpy':bpy,'math':math,'Vector':Vector,'Quaternion':Quaternion,'MM':1000.}
poseprov=reuse(ROOT/'production_spec/stage6_deformation/stage6a/scripts/s6a_common.py',['reset_pose','set_joint_rotation','evaluate','pose_state'],sn)
def eval_positions(ob):
 bpy.context.view_layer.update();v,f=sn['evaluate'](ob,ob.matrix_world.copy());assert [list(p) for p in f]==C['faces'];return np.array([list(p) for p in v])*1000
bpy.ops.wm.open_mainfile(filepath=str(R2),load_ui=False,use_scripts=False);before=snapshot();ob=bpy.data.objects[before['object_name']];rig=bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG']
assert before['coordinates_local_m']==C['source_local_m'];assert before['protected']['mesh']['counts']==[3416,6828,3414]
assert all(abs(b.rotation_quaternion.angle)<1e-7 and tuple(b.location)==(0,0,0) and tuple(b.scale)==(1,1,1) for b in rig.pose.bones)
current_bind=eval_positions(ob);assert snapshot()['protected']==before['protected']
weights={str(i):before['positive_weight_vectors'][i] for i in ids};family={}
for vec in weights.values():
 for bone,w in vec.items():family.setdefault(bone,[]).append(w)
support={k:{'max_weight':max(v),'mean_over16':sum(v)/16,'nonzero_vertex_count':len(v)} for k,v in family.items()}
cases=['MID_MCP_15','MID_MCP_30','MID_MCP_45']
# A10% direct MCP contribution is a declared smoke scheduling choice, never a weight/anatomy gate.
idx=support.get('INDEX_MCP_R',{}).get('max_weight',0)
if idx>=.10:cases.append('IDX_MCP_30')
dump('PALMAR_ROOT_WEIGHT_SUPPORT_FAMILY_R1.json',{'per_vertex':weights,'support':support,'smoke_cases_selected':cases,'INDEX_MCP_scheduling_threshold':.10,'INDEX_MCP_scheduling_reason':'include locator-linked supplemental smoke only if at least one of16 has direct MCP weight>=10%','no_weights_modified':True,'NOT_anatomy_or_qualification_threshold':True,'temporary_source':ref(R2)})
for i in ids:ob.data.vertices[i].co=C['candidate_local_m'][i]
ob.data.update();assert snapshot()['protected']==before['protected']
bind=eval_positions(ob);raw=np.array(C['candidate_world_mm']);roi=core['visible_upper_box_hit_vertex_ids'];err=np.linalg.norm(bind[roi]-raw[roi],axis=1);assert err.max()<.0001,'FAIL_CLOSED_PALMAR_DONOR_RESTORATION_DESIGN: bind numerical error'
assert all(snapshot()['coordinates_local_m'][i]==before['coordinates_local_m'][i] for i in normal['vertex_ids'])
for k in ['DESIGN_ONLY','NOT_PRODUCTION','NOT_HUMAN_APPROVED','DO_NOT_PROMOTE','TEMP_DOWNSTREAM_ONLY']:bpy.context.scene['PALMAR_'+k]=True
temp=OUT/'TEMP_STAGE5B_PALMAR16_BIND_PREVIEW_DESIGN_ONLY.blend';assert not temp.exists()
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(temp),copy=True,compress=False)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.wm.open_mainfile(filepath=str(temp),load_ui=False,use_scripts=False);after=snapshot();assert after['protected']==before['protected'];assert after['coordinates_local_m']==C['candidate_local_m']
reopen=eval_positions(bpy.data.objects[after['object_name']]);assert np.array_equal(bind,reopen)
dump('PALMAR_ROOT_BIND_ZERO_PREVIEW_R1.json',{'status':'PASS_NUMERIC_PENDING_VISIBLE_REVIEW','RAW_TO_BIND_ROI_MAX_DELTA_MM':float(err.max()),'RAW_TO_BIND_ROI_MEAN_DELTA_MM':float(err.mean()),'RAW_TO_BIND_WRITE16_MAX_DELTA_MM':float(np.linalg.norm(bind[ids]-raw[ids],axis=1).max()),'numeric_zero_bound_mm':.0001,'PALMAR_DEFECT_REAPPEARED_AT_BIND_ZERO':'PENDING_VISIBLE_REVIEW','NEW_BIND_VISIBLE_DEFECT':'PENDING_VISIBLE_REVIEW','weights_rig_groups_exact':True,'bone_count':len(next(iter(after['protected']['rigs'].values()))['bones']),'protected_payload_sha256':digest(before['protected']),'no_production_candidate_save':True,'temporary_saved_copy':ref(temp),'zero_reopen_coordinates_exact':True,'actual_pose_smoke_count':0,'pose_helper_AST':poseprov})
dump('TEMP_DOWNSTREAM_COORDINATES_R1.json',{'states':{'CURRENT':{'RAW':C['source_world_mm'],'BIND':current_bind.tolist()},'FORMAL_CANDIDATE':{'RAW':C['candidate_world_mm'],'BIND':bind.tolist()}},'faces':C['faces'],'edges':C['edges'],'pose_smoke_cases':[],'classification':'temporary RAW/BIND only; not formal Stage5 propagation'})
dump('TEMP_DOWNSTREAM_PAYLOAD_PROTECTION_R1.json',{'status':'PASS','protected_sha256':digest(before['protected']),'weights_rig_groups_materials_modifiers_exact':True,'outside16_native_local_positions_exact':True,'normal69_native_local_positions_exact':True,'native_V_E_F':after['protected']['mesh']['counts'],'bone_count':len(next(iter(after['protected']['rigs'].values()))['bones']),'production_save_calls':0})
print('TEMP bind numeric PASS max ROI',err.max(),'mm; support',support,'selected cases',cases,flush=True)
