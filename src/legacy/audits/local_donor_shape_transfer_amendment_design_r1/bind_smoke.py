"""Temporary current rig/current weights BIND + isolated IDX15/30/45 only."""
import sys,math
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
from payload import protected
import bpy,numpy as np
from mathutils import Vector,Quaternion
assert read(OUT/'FORMAL_DONOR_TRANSFER_STRUCTURE_AUDIT_R1.json')['status']=='PASS'
C=read(OUT/'FORMAL_DONOR_TRANSFER_COORDINATES_R1.json');ids=read(OUT/'FORMAL_DONOR_TRANSFER_WRITE_SET_R1.json')['vertex_ids'];roi=read(DIAG/'DORSAL_MCP_DENT_ROI_R1.json')['vertices']
sn={'bpy':bpy,'math':math,'Vector':Vector,'Quaternion':Quaternion,'MM':1000.}
prov=reuse(ROOT/'production_spec/stage6_deformation/stage6a/scripts/s6a_common.py',['reset_pose','set_joint_rotation','evaluate','pose_state'],sn)
cases={z['case_id']:z for z in read(FULL/'FULL_STAGE6A_CASE_MATRIX_R1.json')['cases'] if z['case_id'] in ['IDX_MCP_15','IDX_MCP_30','IDX_MCP_45']}
frozenpose=read(FULL/'POSED_COORDINATES_R1.json')['positions_world_m'];states={}
def evaluate(ob):
 bpy.context.view_layer.update();v,p=sn['evaluate'](ob,ob.matrix_world.copy())
 assert [list(z) for z in p]==C['faces'];return np.array([list(z) for z in v])*1000
def sample(ob,rig):
 sn['reset_pose'](rig);result={'BIND':evaluate(ob)}
 for cid,c in cases.items():
  sn['reset_pose'](rig);sn['set_joint_rotation'](rig,c['bone'],c['applied_rotation_deg']);result[cid]=evaluate(ob)
  nonzero=[b.name for b in rig.pose.bones if abs(b.rotation_quaternion.angle)>1e-7];assert nonzero==['INDEX_MCP_R']
 sn['reset_pose'](rig);restored=evaluate(ob);assert np.array_equal(restored,result['BIND'])
 return result
bpy.ops.wm.open_mainfile(filepath=str(R2),load_ui=False,use_scripts=False);ob=bpy.data.objects['Hand  - Realistic'];rig=bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG'];before=protected(ob)
assert all(abs(b.rotation_quaternion.angle)<1e-7 and tuple(b.location)==(0,0,0) and tuple(b.scale)==(1,1,1) for b in rig.pose.bones)
assert [list(v.co) for v in ob.data.vertices]==C['source_local_m'];baseline=sample(ob,rig);assert protected(ob)==before
frozen_deltas={cid:float(np.max(np.linalg.norm(v-np.array(frozenpose[cid])*1000,axis=1))) for cid,v in baseline.items()};assert max(frozen_deltas.values())<1e-4
for i in ids:ob.data.vertices[i].co=C['candidate_local_m'][i]
ob.data.update();assert protected(ob)==before
# Bind is evaluated before authorizing any smoke on this temporary derived copy.
sn['reset_pose'](rig);bind=evaluate(ob);raw=np.array(C['candidate_world_mm']);err=np.linalg.norm(bind[roi]-raw[roi],axis=1)
assert err.max()<1e-4,'FAIL_CLOSED_DONOR_TRANSFER_BIND_PREVIEW'
candidate=sample(ob,rig);assert np.array_equal(bind,candidate['BIND']);assert protected(ob)==before
for k,v in {'DESIGN_ONLY':True,'NOT_PRODUCTION':True,'NOT_HUMAN_APPROVED':True,'DO_NOT_PROMOTE':True,'BIND_SMOKE_ONLY':True}.items():ob['AMENDMENT_'+k]=v
temp=OUT/'TEMP_CURRENT_RIG_WEIGHT_BIND_PREVIEW_DESIGN_ONLY.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(temp),copy=True,compress=False)
bpy.ops.wm.open_mainfile(filepath=str(temp),load_ui=False,use_scripts=False);ob=bpy.data.objects['Hand  - Realistic'];assert protected(ob)==before
reopened=evaluate(ob);assert np.array_equal(bind,reopened)
dump('FORMAL_DONOR_TRANSFER_BIND_PREVIEW_R1.json',{'status':'PASS','RAW_TO_BIND_ROI_MAX_DELTA_MM':float(err.max()),'RAW_TO_BIND_ROI_MEAN_DELTA_MM':float(err.mean()),'numeric_zero_tolerance_mm':1e-4,'DENT_REAPPEARED_IN_BIND':'NO_GEOMETRIC_EVIDENCE_PENDING_RENDER_REVIEW','NEW_BIND_VISIBLE_DEFECT':'PENDING_RENDER_REVIEW','current_rig_weights_payload_preserved_exactly':True,'formal_candidate_unmodified':True,'temporary_current_rig_copy':ref(temp),'frozen_baseline_coordinate_reproduction_max_mm':frozen_deltas,'pose_helper_AST':prov,'BIND_zero_reopen_exact':True,'reset_after_each_IDX':True,'case_count':3,'NOT_FULL42':True,'NOT_STAGE5_PROPAGATION':True})
dump('TEMP_BIND_SMOKE_COORDINATES_R1.json',{'states':{'CURRENT':{cid:v.tolist() for cid,v in baseline.items()},'FORMAL_CANDIDATE':{cid:v.tolist() for cid,v in candidate.items()}},'faces':C['faces'],'edges':C['edges'],'smoke_cases':cases,'classification':'Limited temporary local shape smoke only; no Stage6 requalification or acceptance'})
# Record only coordinate effects on the9 frozen witnesses; no intersection/severity recategorization.
old=read(FULL/'FULL_STAGE6A_SELF_INTERSECTION_AUDIT_R1.json');rows=[]
for row in old['rows']:
 if not row.get('hard_blocker'):continue
 cid=row['case_id'];vertices=sorted({v for fi in row['face_ids'] for v in C['faces'][fi]});tested=cid in cases
 rows.append({'case_id':cid,'frozen_face_pair':row['face_ids'],'original_evidence_preserved':True,'smoke_case_evaluated':tested,'affected_by_formal_write_set':sorted(set(vertices)&set(ids)),'witness_vertex_coordinate_delta_mm':float(np.max(np.linalg.norm(candidate[cid][vertices]-baseline[cid][vertices],axis=1))) if tested else None,'geometry_pair_identical_under_this_smoke':bool(np.array_equal(candidate[cid][vertices],baseline[cid][vertices])) if tested else None,'severity_acceptance_status_not_reclassified':True})
assert len(rows)==9
dump('INCIDENTAL_STAGE6A_CROSSING_DELTA.json',{'rows':rows,'frozen_blocker_count':9,'TH_IP_not_run':True,'FULL_STAGE6A_REQUALIFICATION_R1_RETAINED':'FAIL_CLOSED_FULL_STAGE6A_REQUALIFICATION','intersection_reclassification_count':0,'scope':'Only witness coordinates recorded for existing IDX smoke cases; six TH_IP witnesses not rerun. No old-pair optimization or acceptance.'})
print('TEMP BIND /3 IDX evaluations saved; ROI raw-bind max mm',err.max(),'rig/weights preserved',flush=True)
