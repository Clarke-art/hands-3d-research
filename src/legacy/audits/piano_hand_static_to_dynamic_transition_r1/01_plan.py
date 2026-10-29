from common import *
from scipy.optimize import least_squares
import time
policy=read(P/'TEMPORAL_MOTION_POLICY_R1.json');lock=read(P/'PRE_GENERATION_LOCK_R1.json')
assert sha(P/'TEMPORAL_MOTION_POLICY_R1.json')==lock['policy_sha256']
assert all(sha(P/n)==v for n,v in lock['script_sha256'].items())
assert not (P/'CONTACT_AWARE_MOTION_PLAN_R1.json').exists(),'No second candidate or restart.'
timer=time.monotonic();allctrl={};arrays={};diagnostics={};w=policy['optimization']['weights']
for s,poses in [('L',['L1','L2']),('R',['R2'])]:
 model=models(s);lo=[];hi=[];seed=[]
 for pose in poses:
  j=4 if pose=='L1' else 0 if pose=='L2' else 2;a=qanchor(pose)[j];b=np.radians(SP['joint_increment_bounds_deg']['THUMB' if j==0 else 'LONG']);lower=np.maximum(b[0],a-np.radians(12));upper=np.minimum(b[1],a+np.radians(12))
  if pose=='L1':upper[[0,3]]=b[1,[0,3]]-np.radians(.5)
  if pose=='L2':upper[2]=b[1,2]-np.radians(.5)
  lo.extend(np.tile(lower,3));hi.extend(np.tile(upper,3));seed.extend(np.clip(np.tile(a,3),np.tile(lower,3)+1e-8,np.tile(upper,3)-1e-8))
 lo=np.array(lo);hi=np.array(hi)
 grid=np.arange(round(WINDOWS[s][0]*120),round(WINDOWS[s][1]*120)+1)/120
 exact=[v for n in EVENTS[s] for v in [n['note_on']-.12,n['note_on'],n['note_on']+.035,n['note_off'],n['note_off']+.07,recovery_end(n)]]
 times=np.unique(np.r_[grid,exact]);contact_times=[];colloc=[]
 for n in EVENTS[s]:
  on,off=n['note_on'],n['note_off'];contact_times.extend([on,on+.035,off]+[t for t in grid if on<=t<off+.07]);colloc.extend(on-.12+u*.12 for u in [.25,.5,.75]);colloc.extend([on+.035*u for u in [0,.25,.5,.75,1]]);colloc.extend([off+.07*u for u in [0,.25,.5,.75]]);colloc.extend([off+.07+(recovery_end(n)-off-.07)*u for u in [.25,.5,.75]])
 colloc=np.unique(colloc);contact_times=np.unique(contact_times)
 targets={}
 for pose in poses:
  j=4 if pose=='L1' else 0 if pose=='L2' else 2;targets[pose]=worldpads(s,qanchor(pose))[j]
 band=SP['solver']['planned_key_bands'][s];keyids=[k['key_index'] for k in c.KEYS if band[0]<=k['midi_note']<=band[1]]
 boxes=[]
 for k in keyids:
  for g in c.KEYS[k]['geometry']:
   V=np.array(g['vertices']);boxes.append((k,V.min(0),V.max(0)))
 palm=model['V'][:,1]<.105
 def unpack(x):return {p:x[i*12:(i+1)*12].reshape(3,4) for i,p in enumerate(poses)}
 calls=0;lastnote=time.monotonic()
 def residual(x):
  global calls,lastnote
  calls+=1;ctrl=unpack(x);out=[]
  for t in contact_times:
   q,ka=sample(s,t,ctrl);pp=worldpads(s,q)
   for n in EVENTS[s]:
    if not n['note_on']-1e-9<=t<=n['note_off']+.07+1e-9:continue
    pose='L1' if s=='L' and n['finger']==5 else 'L2' if s=='L' else 'R2';j=n['finger']-1;target=keytransform(n['midi_note'],targets[pose],ka[n['key_index']]);out.extend((pp[j]-target)*1000*w['pad_target_mm'])
  # Whole-sequence temporal residual is part of coefficient generation, not a postfilter.
  qs=np.array([sample(s,t,ctrl)[0] for t in grid]);v=np.diff(np.degrees(qs),axis=0)*120;a=np.diff(v,axis=0)*120
  out.extend((np.maximum(np.abs(v)-850,0)*w['velocity_over_deg_sec']).ravel());out.extend((np.maximum(np.abs(a)-90000,0)*w['acceleration_over_deg_sec2']).ravel())
  for t in colloc:
   q,ka=sample(s,t,ctrl);V=skin(s,q,model);pen=np.zeros(len(V));active=[]
   for n in EVENTS[s]:
    if n['note_on']-1e-9<=t<=n['note_off']+.07+1e-9:
     pose='L1' if s=='L' and n['finger']==5 else 'L2' if s=='L' else 'R2';j=n['finger']-1;target=keytransform(n['midi_note'],targets[pose],ka[n['key_index']]);out.extend((V[c.MARKERS[s][j]['mesh_vertex']]-target)*1000*w['skin_pad_target_mm']);patch=np.linalg.norm(model['V']-model['V'][c.MARKERS[s][j]['mesh_vertex']],axis=1)<.018;active.append((n['key_index'],patch))
   for k,l,h in boxes:
    VV=keytransform(k+21,V,ka[k],True) if ka[k] else V;d=np.abs(VV-(l+h)/2)-(h-l)/2;sdf=np.linalg.norm(np.maximum(d,0),axis=1)+np.minimum(np.max(d,axis=1),0);margin=np.where(palm,.005,.002)
    for own,patch in active:
     if own==k:margin=margin.copy();margin[patch]=0
    pen=np.maximum(pen,margin-sdf)
   out.extend(np.maximum(pen,0)*1000*2)
  for pose in poses:
   j=4 if pose=='L1' else 0 if pose=='L2' else 2;out.extend(((ctrl[pose]-qanchor(pose)[j])*w['joint_anchor_rad']).ravel());out.extend(((np.diff(ctrl[pose],n=2,axis=0))*w['coefficient_curvature_rad']).ravel())
  if time.monotonic()-lastnote>20:print('GLOBAL_COEFFICIENT_SOLVE',s,calls,'elapsed',round(time.monotonic()-timer,1),flush=True);lastnote=time.monotonic()
  return np.array(out)
 fit=least_squares(residual,np.array(seed),bounds=(lo,hi),max_nfev=100,xtol=1e-8,ftol=1e-7,gtol=1e-7)
 assert np.isfinite(fit.x).all();ctrl=unpack(fit.x);allctrl.update(ctrl)
 qs=[];keys=[];pads=[]
 for t in times:
  q,ka=sample(s,t,ctrl);qs.append(q);keys.append(ka);pads.append(worldpads(s,q))
 arrays[s+'_times']=times;arrays[s+'_q']=np.array(qs);arrays[s+'_key_angles']=np.array(keys);arrays[s+'_pads']=np.array(pads)
 diagnostics[s]={'success':bool(fit.success),'nfev':fit.nfev,'status':int(fit.status),'cost':float(fit.cost),'optimality':float(fit.optimality),'message':fit.message,'calls':calls,'one_seed':True,'restarts':0,'per_frame_ik':False,'skin_collocation_count':len(colloc),'time_samples':len(times),'elapsed_sec':time.monotonic()-timer}
 print('ONE_SEQUENCE_SOLVED',s,json.dumps(diagnostics[s]),flush=True)
np.savez_compressed(P/'temporal_motion.npz',**arrays)
dump('CONTACT_AWARE_MOTION_PLAN_R1.json',{'planner':policy['planner'],'policy_sha256':lock['policy_sha256'],'anchor_sha256':lock['anchor_identity_sha256'],'candidate_count':1,'controls_radians':allctrl,'controls_deg':{p:np.degrees(v) for p,v in allctrl.items()},'events':EVENTS,'windows':WINDOWS,'diagnostics':diagnostics,'generated_pose_arrays_sha256':sha(P/'temporal_motion.npz'),'source_events_unchanged':True,'root_constant':True,'anchors_not_reoptimized':True,'postfilter':False,'human_approval':False})
print('SOLE_MOTION_CANDIDATE_GENERATED',flush=True)
