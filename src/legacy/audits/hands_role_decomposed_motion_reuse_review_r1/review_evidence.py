"""Read-only role/weight review and a few fixed FK dependency probes.
No optimizer import/call from an executed historical planner; no animation,
collision repair, retargeted candidate, new role generator or pose file.
"""
from support import *
from persistence import atomic_json,load_record
sys.path.insert(0,str(OLD/'_deps'))
import numpy as np
SOURCE=ROOT/'experiments/hands_reusable_motion_representation_feasibility_r1'
for p in [ROOT/'AGENTS.md',SOURCE/'MOTION_PRIMITIVE_DESIGN.md',SOURCE/'RETARGET_AND_GEOMETRY_VALIDATION.md',SOURCE/'FINAL_HUMAN_REVIEW.md',A2/'coordinated_motion.py',A2/'02_generate.py',ROOT/'audits/minuet_target_key_hand_position_planning_r1/02_generate.py',ROOT/'audits/minuet_stage_c_motion_planning_architecture_reassessment_r1/CURRENT_RIGHT_HAND_MOTION_ARCHITECTURE.md',ROOT/'experiments/hands_contact_continuous_release_r2/FINAL_HUMAN_REVIEW.md',ROOT/'experiments/hands_p3_temporal_wrist_coordination_r2/FINAL_HUMAN_REVIEW.md']:
 p.read_bytes()
I=read(SOURCE/'INPUT_BINDINGS.json');P=read(SOURCE/'POLICY.json');audit=read(SOURCE/'SOURCE_GEOMETRY_AUDIT.json')
rawpath=SOURCE/'SOURCE_AUDIT_SAMPLES.npz'
with np.load(rawpath,allow_pickle=False) as raw:
 S={k:raw[k].copy() for k in raw.files if k!='metadata_utf8'}
driver=read(MODEL/'SHAPE_DRIVER_READONLY.json');pf=read(ROOT/'experiments/hands_c01_whole_hand_motion_feasibility_r1/RIG_PREFLIGHT.json')
assert sha(I['source_scene']['path'])==I['source_scene']['sha256']
# Reuse frozen model, native FK/LBS and corrective formulas only. The slice
# contains no optimizer or candidate search and its callers here are static.
code=(PREV/'evaluate.py').read_text(encoding='utf-8-sig')
exec(compile(code[code.index('M=read(MODEL/'):code.index('ref_t=REF')],str(PREV/'evaluate.py')+':frozen_model_only','exec'))
rois=read(ROOT/'experiments/hands_c01_whole_hand_motion_feasibility_r1/DIGIT_SKIN_ROI.json')
lo=np.array(P['joint_bounds_deg'])[:,0];hi=np.array(P['joint_bounds_deg'])[:,1]
def basis_of(q):
 basis=np.tile(np.eye(3),(1,len(REST),1,1))
 for j,d in enumerate(DIGITS):
  for k,name in enumerate(NAMES[j]):
   basis[:,BN[name]]=rot(np.radians(q[j,k]),AXES[j][k])
   if k==0:basis[:,BN[name]]=rot(np.radians(q[j,3]),SPREAD[j])@basis[:,BN[name]]
 return basis
def shape_value(basis):
 opp=np.arctan2(basis[0,BN['THUMB_CMC_R'],2,1],basis[0,BN['THUMB_CMC_R'],2,2]);mcp=np.arctan2(basis[0,BN['THUMB_MCP_R'],2,1],basis[0,BN['THUMB_MCP_R'],2,2])
 return float(max(np.clip((-opp-.37)/.06,0,1),np.clip((-opp-.15)/.15,0,1)*np.clip((-mcp-.175)/.175,0,1)))
def group_of(name):
 return next((d for d in DIGITS if name.startswith(d+'_')),'SHARED_WRIST')
groups={d:[i for i,n in enumerate(M['bones']) if group_of(n)==d] for d in DIGITS+['SHARED_WRIST']}
mass=np.column_stack([W[:,groups[d]].sum(1) for d in DIGITS]);shared=W[:,groups['SHARED_WRIST']].sum(1)
crossids=np.flatnonzero((mass>1e-8).sum(1)>1)
shared_digit_ids=np.flatnonzero((mass.max(1)>1e-8)&(shared>1e-8))
crosspairs=[]
for j,d in enumerate(DIGITS):
 for k,e in enumerate(DIGITS[j+1:],start=j+1):
  ids=np.flatnonzero((mass[:,j]>1e-8)&(mass[:,k]>1e-8))
  if len(ids):crosspairs.append(dict(pair=d+'_'+e,vertices=len(ids),vertex_examples=ids[:8],max_combined_weight=float((mass[ids,j]+mass[ids,k]).max())))
markers=[]
for j,r in enumerate(MARK):
 v=r['mesh_vertex'];chain=[];b=BN[r['distal_frame']]
 while b>=0:chain.append(M['bones'][b]);b=int(D['parents'][b])
 markers.append(dict(digit=DIGITS[j],vertex=v,weighted_bones=[dict(bone=n,weight=float(W[v,i])) for i,n in enumerate(M['bones']) if W[v,i]>1e-8],kinematic_ancestor_chain=chain,cross_other_digit_weight=float(mass[v].sum()-mass[v,j]),corrective_rest_delta_mm=float(np.linalg.norm(SH[v])*1000)))
roi_coupling=[]
for j,d in enumerate(DIGITS):
 ids=np.array(rois[d]['vertices']);other=mass[ids].sum(1)-mass[ids,j]
 roi_coupling.append(dict(digit=d,strong_roi_vertices=len(ids),other_digit_influenced_vertices=int((other>1e-8).sum()),other_digit_max_weight=float(other.max()),shared_wrist_influenced_vertices=int((shared[ids]>1e-8).sum()),corrective_influenced_vertices=int((np.linalg.norm(SH[ids],axis=1)>1e-12).sum())))
# Three existing, exactly matched snapshots; a few one-degree coordinate probes.
requests=[(1.4214275,['INDEX','MIDDLE']),(1.7,['INDEX','MIDDLE','RING','THUMB']),(2.0625,['INDEX','THUMB'])]
probes=[];baseline=[]
for t,digits in requests:
 ix=int(np.argmin(abs(S['times']-t)));assert abs(S['times'][ix]-t)<1e-10
 q=S['qdeg'][ix];world=S['rig_world'][ix];basebasis=basis_of(q)
 V,_=skin(basebasis,world[None],np.arange(len(W)));V=V[0]
 err=float(np.max(np.linalg.norm(V-S['vertices'][ix],axis=1))*1000);assert err<.01,err
 row=next(r for r in audit['rows'] if abs(r['time']-t)<1e-10)
 act=[r for r in row['roles'] if r['role']=='ACTIVE'];assert len(act)==1
 active_digit=act[0]['digit'];active_j=DIGITS.index(active_digit);active_pad=MARK[active_j]['mesh_vertex'];active_ids=np.array(rois[active_digit]['vertices'])
 pad_local=np.linalg.inv(world)@np.r_[S['vertices'][ix,active_pad],1]
 baseline.append(dict(time=t,active_digit=active_digit,active_event=act[0]['event'],native_LBS_max_error_mm=err,active_pad_rig_local_m=pad_local[:3],source_contacts=row['contacts'],roles=row['roles'],active_parameters_deg=q[active_j],all_digit_remaining_lower_deg=q-lo,all_digit_remaining_upper_deg=hi-q))
 for d in digits:
  j=DIGITS.index(d);assert j!=active_j
  qnew=q.copy();delta=1. if q[j,0]+1<=hi[j,0] else -1.
  qnew[j,0]+=delta;assert lo[j,0]-.002<=qnew[j,0]<=hi[j,0]+.002
  b=basis_of(qnew);V1,_=skin(b,world[None],np.arange(len(W)));V1=V1[0];shift=np.linalg.norm(V1-V,axis=1)*1000
  probes.append(dict(time=t,changed_digit=d,source_role=next(r['role'] for r in row['roles'] if r['digit']==d),changed_coordinate='first flexion engineering increment only',delta_deg=delta,root_fixed=True,active_digit=active_digit,active_pad_delta_mm=float(shift[active_pad]),active_strong_ROI_max_delta_mm=float(shift[active_ids].max()),full_hand_max_delta_mm=float(shift.max()),full_hand_moved_vertices_gt1e_6mm=int((shift>1e-6).sum()),corrective_activation_before=shape_value(basebasis),corrective_activation_after=shape_value(b),no_collision_or_repair_check=True,not_a_candidate_pose=True))
 translated=world.copy();translated[0,3]+=.0005
 V1,_=skin(basebasis,translated[None],np.arange(len(W)));shift=np.linalg.norm(V1[0]-V,axis=1)*1000
 probes.append(dict(time=t,changed_digit='SHARED_WRIST',changed_coordinate='world X translation',delta_mm=.5,active_digit=active_digit,active_pad_delta_mm=float(shift[active_pad]),full_hand_min_delta_mm=float(shift.min()),full_hand_max_delta_mm=float(shift.max()),no_contact_legality_claim=True,no_collision_or_repair_check=True,not_a_candidate_pose=True))
atomic_json('KINEMATIC_AND_SKIN_DEPENDENCIES.json',dict(marker_support=markers,bone_parent_rows=[dict(bone=n,parent=M['bones'][int(D['parents'][i])] if D['parents'][i]>=0 else None) for i,n in enumerate(M['bones'])],mesh_vertex_count=len(W),cross_digit_weight_vertex_count=len(crossids),cross_digit_pairs=crosspairs,digit_plus_wrist_blended_vertex_count=len(shared_digit_ids),strong_digit_ROI_coupling=roi_coupling,corrective_nonzero_vertex_count=int((np.linalg.norm(SH,axis=1)>1e-12).sum()),corrective_driver_metadata=driver,rig_metadata=dict(wrist=pf['wrist'],root=pf['root'],modifiers=pf['mesh_modifiers']),threshold=1e-8,source_model_is_existing_frozen_native_export=True))
atomic_json('READONLY_FK_DEPENDENCY_PROBES.json',dict(existing_snapshot_count=3,individual_coordinate_probes=8,shared_root_probes=3,baseline=baseline,probes=probes,no_optimization=True,no_actual_Rig_pose_edits=True,no_geometry_repair_attempt=True,no_pose_or_motion_arrays_exported=True))
# Classify EXISTING actual collision/key evidence by the source event roles.
events=[]
for n in I['source']:
 active_rows=[r for r in audit['rows'] if any(c['event']==n['note_id'] for c in r['contacts'])];d=DIGITS[n['finger']-1]
 pair_rows=[r for r in active_rows if any(v for p,v in r['finger_skin_pairs'].items() if d in p.split('_'))]
 key_rows=[r for r in active_rows if any(h['digit']==d for h in r['non_owned_key_hits'])]
 indices=[int(np.argmin(abs(S['times']-r['time']))) for r in active_rows]
 pads=S['vertices'][indices,MARK[n['finger']-1]['mesh_vertex']];dt=np.diff(S['times'][indices]);speed=np.linalg.norm(np.diff(pads,axis=0),axis=1)/dt*1000
 qn=S['qdeg'][indices,n['finger']-1];qvel=abs(np.diff(qn,axis=0)/dt[:,None])
 events.append(dict(event=n['note_id'],finger=n['finger'],active_samples=len(active_rows),contact_gate=next(c for c in audit['source_contacts'] if c['event']==n['note_id']),active_skin_pair_hit_samples=len(pair_rows),active_skin_nonowned_key_hit_samples=len(key_rows),finite_active_pad_speed_peak_mm_s=float(speed.max()),finite_active_joint_coordinate_speed_peak_deg_s=float(qvel.max()),velocity_is_reference_feature_not_safety_limit=True))
rolecounts={};skinrole=[]
for r in audit['rows']:
 if not r['core']:continue
 rolemap={a['digit']:a['role'] for a in r['roles']}
 for pair,count in r['finger_skin_pairs'].items():
  if count:
   a,b=pair.split('_');skinrole.append(dict(time=r['time'],pair=pair,count=count,roles=[rolemap[a],rolemap[b]]))
 for role in ['ACTIVE','RELEASING','PREPARING','IDLE','PALM_OR_SHARED_WEB']:
  hits=[h for h in r['non_owned_key_hits'] if (h['digit']==role if role=='PALM_OR_SHARED_WEB' else rolemap.get(h['digit'])==role)]
  if hits:
   z=rolecounts.setdefault(role,dict(hit_samples=0,max_depth_mm=0.));z['hit_samples']+=1;z['max_depth_mm']=max(z['max_depth_mm'],max(h['depth_mm'] for h in hits))
atomic_json('ROLE_DECOMPOSITION_EVIDENCE.json',dict(events=events,core_role_key_intrusion_summary=rolecounts,existing_skin_collision_role_records=skinrole,all_source_activity_retained_as_information=True,whole_source_not_required_collision_free_for_this_review=True,finite_samples_are_not_full_skin_safety_certificate=True))
for p in [ROOT/'AGENTS.md',Path(I['source_scene']['path']),A2/'STAGE_A_R2_COORDINATED_RIGHT_DESIGN_ONLY.blend',ROOT/'production_spec/right_hand_product_baseline_r2/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R2.blend']:
 READS[str(p)]=sha(p)
protect()
print('MARKERS',markers);print('CROSS_WEIGHT',len(crossids),crosspairs);print('ROI_COUPLING',roi_coupling);print('SOURCE_EVENTS',events)
for r in probes:print('PROBE',r['time'],r['changed_digit'],r['active_pad_delta_mm'],r.get('active_strong_ROI_max_delta_mm'))
