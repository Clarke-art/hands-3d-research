from skin_proxy import *
from scipy.optimize import least_squares
from scipy.spatial import cKDTree
import time,hashlib
POL=json.loads((O/'POLICY_LOCK.json').read_text(encoding='utf-8-sig'));assert json.loads((O/'COLLISION_METHOD_TESTS.json').read_text(encoding='utf-8-sig'))['status']=='VALIDATED_FOR_STATIC_SCREEN';assert json.loads((O/'SKIN_PROXY_PARITY.json').read_text(encoding='utf-8-sig'))['pass_'];assert not (O/'SOLVER_RESULTS.json').exists()
WEIGHTS=dict(true_pulp_contact=15.,pad_inside=12.,pad_height_interval=3.,preferred_pad_xy=.1,full_skin_key_clearance=20.,self_skin_signed_nearest_proxy=8.,joint_prior_deg=.012,root_xy_prior_mm=.012,root_rotation_prior_deg=.04,prepared_middle=1.5,desired_non_target_clearance_mm=.6,numerical_contact_settle_mm=-.005)
(O/'SOLVER_WEIGHT_LOCK.json').write_text(json.dumps(WEIGHTS,indent=2)+'\n',encoding='utf8')
SRC=json.loads((O/'SOURCE_POSES.json').read_text(encoding='utf-8-sig'));SRC={r['label']:r for r in SRC};ANCH=json.loads((ROOT/'audits/piano_hand_static_posture_clearance_refinement_r2/SOLVED_STATIC_POSES_R2.json').read_text(encoding='utf-8-sig'))['poses'];staticB=json.loads((ROOT/'audits/piano_hand_static_posture_clearance_refinement_r2/STATIC_REFINEMENT_POLICY_R2.json').read_text(encoding='utf-8-sig'))['joint_increment_bounds_deg'];B=np.array([staticB['THUMB' if j==0 else 'LONG'] for j in range(5)])
tri=RAW['triangles'];labels=np.array(META['triangle_labels']);triangle_ids=[np.flatnonzero(labels==j) for j in range(5)];fvertex=[np.unique(tri[ids]) for ids in triangle_ids];sampleids=[ids[::5] for ids in fvertex];targetpatch=[np.array(p) for p in META['pad_patches']]
I=POL['source_input'];sourceNotes={n['note_id']:n for n in I['notes']};tests=[('S1','R07',67,1,76,3),('S2','R08',76,3,None,None),('S3','R09',72,1,None,None),('S4','R12',78,4,None,None),('S5','R14',67,1,None,None)]
started=time.monotonic();results=[];budget=POL['max_numerical_wall_seconds']
class StopBudget(Exception):pass

def prepkey(angles,target,finger):
 pieces=[]
 for k in c.KEYS:
  R=c.axisrot(angles[k['key_index']],k['press_axis']);pv=np.array(k['press_pivot'])
  for g in k['geometry']:
   pl=component_planes(g);N=pl[:,:3]@R.T;dd=pl[:,3]-pl[:,:3]@pv+N@pv;vv=(np.array(g['vertices'])-pv)@R.T+pv
   pieces.append((k['midi_note'],N,dd,vv.min(0),vv.max(0)))
 return pieces

def keyPenalty(V,pieces,midi,finger):
 penalty=np.zeros(len(V));lo=V.min(0);hi=V.max(0);patch=targetpatch[finger-1]
 for note,N,d,l,h in pieces:
  if np.any(hi<l-.003) or np.any(lo>h+.003):continue
  distance=np.max(V@N.T-d,axis=1)*1000;margin=np.full(len(V),WEIGHTS['desired_non_target_clearance_mm'])
  if note==midi:margin[patch]=0.
  penalty=np.maximum(penalty,np.maximum(margin-distance,0))
 return penalty

def selfPenalty(V):
 triangles=V[tri];centers=triangles.mean(1);normals=np.cross(triangles[:,1]-triangles[:,0],triangles[:,2]-triangles[:,0]);normals/=np.maximum(np.linalg.norm(normals,axis=1,keepdims=True),1e-12);trees=[cKDTree(centers[ids]) for ids in triangle_ids];out=[]
 for j in range(5):
  for k in range(5):
   if j==k:continue
   vids=sampleids[j];dist,index=trees[k].query(V[vids]);tids=triangle_ids[k][index];normal=normals[tids];signed=np.sum((V[vids]-centers[tids])*normal,axis=1)*1000
   shared=np.any(tri[tids]==vids[:,None],axis=1);p=np.where((dist<.008)&~shared,np.maximum(.6-signed,0),0)
   out.extend(p)
 return np.array(out)

def contactResidual(V,midi,finger,angle):
 key=c.KEYS[midi-21];pv=np.array(key['press_pivot']);R=c.axisrot(angle,key['press_axis']);local=(V-pv)@R;local+=pv;pad=local[RAW['pad_indices'][finger-1]];s=key['key_top_playable_surface'];errors=[pad[:2]-np.clip(pad[:2],[q['xmin']+.004,q['ymin']+.002],[q['xmax']-.004,q['ymax']-.002]) for q in s];si=int(np.argmin([e@e for e in errors]));q=s[si]
 patch=targetpatch[finger-1];inside=(local[patch,0]>=q['xmin'])&(local[patch,0]<=q['xmax'])&(local[patch,1]>=q['ymin'])&(local[patch,1]<=q['ymax']);gaps=(local[patch,2]-q['z'])*1000;gap=float(gaps[inside].min()) if inside.any() else (pad[2]-q['z'])*1000;pg=(pad[2]-q['z'])*1000
 preferred=np.array([key['key_center'][0],.027 if key['color']=='WHITE' else .072]);preferred=np.clip(preferred,[q['xmin']+.004,q['ymin']+.002],[q['xmax']-.004,q['ymax']-.002])
 return np.r_[errors[si]*1000*WEIGHTS['pad_inside'],(gap-WEIGHTS['numerical_contact_settle_mm'])*WEIGHTS['true_pulp_contact'],(pg-np.clip(pg,0,3))*WEIGHTS['pad_height_interval'],(pad[:2]-preferred)*1000*WEIGHTS['preferred_pad_xy']]

for name,nid,midi,finger,prep,prepf in tests:
 if time.monotonic()-started>=budget:results.append(dict(test=name,status='NOT_FOUND_WITHIN_BUDGET',reason='global budget exhausted',attempts=[]));break
 if name=='S5' and not all(any(a.get('proxy_contact_valid') and a.get('proxy_max_key_intrusion_mm',100)<.25 and a.get('proxy_self_penalty_peak',100)<.2 for a in r.get('attempts',[])) for r in results[:4]):
  results.append(dict(test=name,status='NOT_RUN_CONDITION_NOT_MET',reason='S1-S4 not all provisionally feasible; obey conditional S5 rule',attempts=[]));continue
 sourceLabel=name+'_INITIAL';source=SRC[sourceLabel];angles=np.array(source['angles']);pieces=prepkey(angles,midi,finger);targetTime=source['time'];entry=np.array(source['root_state']);pose='R2' if name in ['S2','S4'] else 'R1';second=np.r_[np.zeros(6),np.array(ANCH[pose]['joint_increments_deg']).ravel()]
 # Retarget only X using actual skin pad/key coordinates; original approved Z is retained.
 pp=skin(second)[RAW['pad_indices'][finger-1]];second[0]=(c.KEYS[midi-21]['key_center'][0]-pp[0])*1000
 attempts=[];testStart=time.monotonic();print('STATIC_TEST_START',name,'elapsed',round(testStart-started,2),flush=True)
 for seedid,seed in [('C01_RECORDED',entry),('APPROVED_'+pose+'_X_RETARGET',second)]:
  if time.monotonic()-testStart>=POL['max_test_seconds'] or time.monotonic()-started>=budget:break
  fixedZ=float(seed[2]);variable=np.r_[seed[:2],seed[3:]];low=np.r_[[-150,-30],[-8,-8,-12],B[:,0].ravel()];high=np.r_[[60,35],[8,8,12],B[:,1].ravel()];variable=np.clip(variable,low+1e-7,high-1e-7);attemptStart=time.monotonic();deadline=min(started+budget,testStart+POL['max_test_seconds'],attemptStart+56.);best=[np.inf,variable.copy()];calls=0
  def state(x):return np.r_[x[:2],fixedZ,x[2:]]
  def residual(x):
   global calls
   calls+=1
   if time.monotonic()>deadline:raise StopBudget()
   st=state(x);V=skin(st);out=[contactResidual(V,midi,finger,angles[midi-21]),keyPenalty(V,pieces,midi,finger)*WEIGHTS['full_skin_key_clearance'],selfPenalty(V)*WEIGHTS['self_skin_signed_nearest_proxy'],(st[6:]-seed[6:])*WEIGHTS['joint_prior_deg'],(st[:2]-seed[:2])*WEIGHTS['root_xy_prior_mm'],st[3:6]*WEIGHTS['root_rotation_prior_deg']]
   if prep is not None:
    k=c.KEYS[prep-21];s=k['key_top_playable_surface'][0];point=V[RAW['pad_indices'][prepf-1]];goal=np.array([k['key_center'][0],.035,s['z']+.012]);out.append((point-goal)*1000*WEIGHTS['prepared_middle'])
   r=np.concatenate(out);cost=float(r@r)
   if cost<best[0]:best[:]=[cost,x.copy()]
   return r
  try:
   fit=least_squares(residual,variable,bounds=(low,high),max_nfev=POL['max_nfev_per_initialization'],ftol=1e-5,xtol=1e-5,gtol=1e-5,x_scale='jac');chosen=fit.x;conv=dict(success=bool(fit.success),nfev=fit.nfev,status=int(fit.status),message=fit.message)
  except StopBudget:chosen=best[1];conv=dict(success=False,nfev=None,status='BUDGET_STOP',message='Fixed per-seed/test/global wall-clock ceiling reached; best evaluated state retained')
  st=state(chosen);V=skin(st);rcontact=contactResidual(V,midi,finger,angles[midi-21]);kp=keyPenalty(V,pieces,midi,finger);sp=selfPenalty(V)
  attempts.append(dict(initialization=seedid,state=st.tolist(),fixed_root_z_delta_mm=fixedZ,source_time=targetTime,key_angles=angles.tolist(),elapsed_seconds=time.monotonic()-attemptStart,residual_calls=calls,convergence=conv,proxy_cost=best[0],proxy_contact_valid=abs(float(rcontact[2]/WEIGHTS['true_pulp_contact']))<.05,proxy_max_key_intrusion_mm=float(max(kp.max()-.6,0)),proxy_self_penalty_peak=float(sp.max()),not_final_acceptance=True))
  print('STATIC_ATTEMPT',name,seedid,round(attempts[-1]['elapsed_seconds'],2),conv['success'],'proxy_self',round(sp.max(),3),flush=True)
  (O/'SOLVER_PROGRESS.json').write_text(json.dumps(dict(completed_tests=results,current_test=name,current_attempts=attempts,total_seconds=time.monotonic()-started),indent=2)+'\n',encoding='utf8')
 results.append(dict(test=name,note_id=nid,midi=midi,finger=finger,prepare=dict(midi=prep,finger=prepf) if prep else None,time=targetTime,attempts=attempts,status='PENDING_ACTUAL_BLENDER_VERIFICATION'))
output=dict(task='PIANO_HAND_SKIN_COLLISION_STATIC_FEASIBILITY_R1',tests=results,total_numerical_wall_seconds=time.monotonic()-started,budget_seconds=600,weights=WEIGHTS,initializations_per_test_max=2,continuous_motion_generated=False,proxy='Reused frozen complete skin + all-key convex planes; sampled oriented skin-triangle proximity for self avoidance; final actual BVH validation mandatory')
(O/'SOLVER_RESULTS.json').write_text(json.dumps(output,indent=2,allow_nan=False)+'\n',encoding='utf8');print('STATIC_SOLVER_FINISHED',output['total_numerical_wall_seconds'],flush=True)

