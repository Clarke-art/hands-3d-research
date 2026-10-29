"""The single locked, bounded local correction pass. No retry."""
from repair_model import *
import time,datetime,hashlib
from scipy.spatial import ConvexHull
from scipy.ndimage import gaussian_filter1d
lock=json.loads((P/'STRATEGY_LOCK.json').read_text())
with (P/'ATTEMPT_STARTED.json').open('x') as f:json.dump(dict(started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),strategy_sha256=hashlib.sha256((P/'STRATEGY_LOCK.json').read_bytes()).hexdigest()),f)
start=time.perf_counter();evals=0;batches=0
def budget():
 if time.perf_counter()-start>290:raise RuntimeError('STOP_300_SECOND_BUDGET_NO_RETRY')
times=np.r_[np.arange(358)/60,5.95];times=np.unique(times);source=source_angles(times);notes=[n for n in m.TL['notes'] if n['hand']=='R']
def smooth(u):u=np.clip(u,0,1);return u**3*(10+u*(-15+6*u))
def envelope(t,j):
 window=max([smooth((t-a)/lock['window_fade_sec'])*smooth((b-t)/lock['window_fade_sec']) for a,b in lock['windows']])
 role=1.
 for n in notes:
  if n['finger']!=j+1:continue
  if n['note_on']-.015<=t<=n['note_off']:return 0.
  if t<n['note_on']-.015:role=min(role,smooth((n['note_on']-.015-t)/lock['prepare_ramp_sec']))
  else:role=min(role,smooth((t-n['note_off'])/lock['release_ramp_sec']))
 return role*window
env=np.array([[envelope(t,j) if j in [1,2,3] else 0 for j in range(5)] for t in times])
roi={d:np.array(m.M['rois'][d]['vertices'])[::3] for d in m.c.DIGITS};ids=np.unique(np.concatenate(list(roi.values())));idx={d:np.searchsorted(ids,v) for d,v in roi.items()}
boxes=[(k,np.min(g['vertices'],axis=0),np.max(g['vertices'],axis=0)) for k,g in m.key_components() if k['color'].upper()=='BLACK']
trust=np.array(lock['trust_degrees']);raw=np.zeros_like(source);prev=np.zeros((5,4))
def topcost(depth):return np.mean(np.sort(np.maximum(depth,0),axis=-1)[...,-8:]**2,axis=-1)
for i,t in enumerate(times):
 budget();q0=source[i];current=q0.copy()
 if env[i].max()<1e-8:prev[:]=0;continue
 engine=m.Skin(np.repeat(t,9),ids)
 def skin(q):
  global evals,batches
  evals+=len(q);batches+=1;return engine(q)
 for step in lock['steps_degrees']:
  for sweep in range(lock['coordinate_sweeps_per_step']):
   for j in [1,2,3]:
    budget()
    if env[i,j]<1e-8:continue
    d=m.c.DIGITS[j];lo,hi=m.c.bounds(d);lower=np.maximum(np.degrees(lo),q0[j]-trust*env[i,j]);upper=np.minimum(np.degrees(hi),q0[j]+trust*env[i,j]);candidates=np.repeat(current[None],9,axis=0)
    for ax in range(4):candidates[1+2*ax,j,ax]+=step*env[i,j];candidates[2+2*ax,j,ax]-=step*env[i,j]
    candidates[:,j]=np.clip(candidates[:,j],lower,upper);vertices=skin(candidates);points=vertices[:,idx[d]];score=np.zeros(9)
    for other in [o for o in m.c.DIGITS if o!=d]:
     planes=ConvexHull(vertices[0,idx[other]]).equations;depth=-np.max(points@planes[:,:3].T+planes[:,3],axis=-1)*1000;score+=3*topcost(depth+lock['neighbor_clearance_mm'])
    for key,low,high in boxes:
     pivot=np.array(key['press_pivot']);local=(points-pivot)@m.rot(engine.angles[0,key['key_index']],[1,0,0])+pivot;depth=np.minimum(local-low,high-local).min(-1)*1000;score+=3*topcost(depth+lock['black_clearance_mm'])
    delta=candidates[:,j]-q0[j];score+=lock['style_penalty']*np.sum(delta**2,axis=-1)+lock['temporal_penalty']*np.sum((delta-prev[j])**2,axis=-1)
    current=candidates[int(np.argmin(score))]
 raw[i]=current-q0;prev=raw[i]
 if i%30==0:print('ONE_PASS',i,len(times),'FK',evals,'sec',round(time.perf_counter()-start,2),flush=True)
delta=gaussian_filter1d(raw,lock['smoothing_sigma_frames'],axis=0,mode='nearest')
lower=np.empty_like(delta);upper=np.empty_like(delta)
for j,d in enumerate(m.c.DIGITS):
 lo,hi=m.c.bounds(d);lower[:,j]=np.maximum(np.degrees(lo)-source[:,j],-trust*env[:,j,None]);upper[:,j]=np.minimum(np.degrees(hi)-source[:,j],trust*env[:,j,None])
# Fixed filter/projection is part of this one pass, not another pose solve.
for _ in range(4):
 delta=np.clip(delta,lower,upper)
 for i in range(1,len(times)):
  step=lock['correction_velocity_limit_deg_sec']*(times[i]-times[i-1]);delta[i]=np.clip(delta[i],delta[i-1]-step,delta[i-1]+step)
 for i in range(len(times)-2,-1,-1):
  step=lock['correction_velocity_limit_deg_sec']*(times[i+1]-times[i]);delta[i]=np.clip(delta[i],delta[i+1]-step,delta[i+1]+step)
delta=np.clip(delta,lower,upper);delta[:,[0,4]]=0;delta[env<1e-8]=0
budget();np.savez_compressed(P/'REPAIR_TRAJECTORY.npz',times=times,source_qdeg=source,correction_deg=delta,qdeg=source+delta,envelope=env,raw_correction_deg=raw)
receipt=dict(seconds=time.perf_counter()-start,local_fk_evaluations=evals,batched_calls=batches,IK_optimizer_calls=0,heavy_solver_calls=0,formal_attempts=1,trajectory_count=1,modified_digits=['INDEX','MIDDLE','RING'],max_abs_correction_deg=np.max(abs(delta),axis=0).tolist(),max_added_velocity_deg_sec=float(np.max(abs(np.diff(delta,axis=0)/np.diff(times)[:,None,None]))),source_sha256=lock['source_sha256'],per_note_pose_patches=False)
(P/'GENERATION_RECEIPT.json').write_text(json.dumps(receipt,indent=2),encoding='utf8');print(json.dumps(receipt),flush=True)
