"""One finite local guidance pass; no nonlinear optimizer or trajectory solve."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import sys,time,json
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
sys.path.insert(0,str(ROOT/'audits/minuet_stage_c_r6_whole_phrase_spatial_planning'))
import whole_phrase_model as m
from scipy.spatial import ConvexHull
from scipy.ndimage import gaussian_filter1d
np=m.np
lock=json.loads((P/'STRATEGY_LOCK.json').read_text())
with (P/'ATTEMPT_STARTED.json').open('x') as f:json.dump(dict(started_utc=__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),strategy=lock),f)
start=time.perf_counter();evals=0;batches=0
times=np.r_[np.arange(179)/30,5.95];source=m.source_angles(times)
notes=[n for n in m.TL['notes'] if n['hand']=='R']
def envelope(t,j):
 dist=min([max(n['note_on']-.025-t,t-n['note_off']-.025,0) for n in notes if n['finger']==j+1]+[1])
 u=np.clip(dist/.16,0,1);return u**3*(10+u*(-15+6*u))
env=np.array([[envelope(t,j) for j in range(5)] for t in times]);env[:,[0,4]]=0
roi={d:np.array(m.M['rois'][d]['vertices'])[::3] for d in m.c.DIGITS}
ids=np.unique(np.concatenate(list(roi.values())));idx={d:np.searchsorted(ids,v) for d,v in roi.items()}
keys=[(k,g) for k,g in m.key_components() if k['color'].upper()=='BLACK']
assert len(keys)>0
boxes=[(k,np.min(g['vertices'],axis=0),np.max(g['vertices'],axis=0)) for k,g in keys]
trust=np.array(lock['trust_degrees']);raw=np.zeros_like(source);prev=np.zeros((5,4));logs=[]
def topcost(x):
 x=np.maximum(x,0);return np.mean(np.sort(x,axis=-1)[...,-8:]**2,axis=-1)
for i,t in enumerate(times):
 if time.perf_counter()-start>590:raise RuntimeError('STOP: generation budget reached; no second attempt')
 q0=source[i];current=q0.copy();current[1:4]+=prev[1:4]*.75*env[i,1:4,None]
 engine=m.Skin(np.repeat(t,9),ids)
 def skin(q):
  global evals,batches
  evals+=len(q);batches+=1
  return engine(q)
 for step in lock['steps_degrees']:
  for j in [1,2,3]:
   if env[i,j]<1e-6:continue
   d=m.c.DIGITS[j];lo,hi=m.c.bounds(d);lo=np.degrees(lo);hi=np.degrees(hi)
   lower=np.maximum(lo,q0[j]-trust*env[i,j]);upper=np.minimum(hi,q0[j]+trust*env[i,j])
   for _ in range(4):
    candidates=np.repeat(current[None],9,axis=0)
    for ax in range(4):
     candidates[1+2*ax,j,ax]+=step*env[i,j];candidates[2+2*ax,j,ax]-=step*env[i,j]
    candidates[:,j]=np.clip(candidates[:,j],lower,upper)
    vertices=skin(candidates);points=vertices[:,idx[d]];score=np.zeros(9)
    for other in [m.c.DIGITS[j-1],m.c.DIGITS[j+1]]:
     fixed=vertices[0,idx[other]];hull=ConvexHull(fixed);planes=hull.equations
     depth=-np.max(points@planes[:,:3].T+planes[:,3],axis=-1)*1000
     score+=2*topcost(depth+.5)
    for key,low,high in boxes:
     pivot=np.array(key['press_pivot']);a=engine.angles[0,key['key_index']]
     local=(points-pivot)@m.rot(a,[1,0,0])+pivot
     depth=np.minimum(local-low,high-local).min(-1)*1000
     score+=topcost(depth+.3)
    delta=candidates[:,j]-q0[j]
    score+=.018*np.sum(delta**2,axis=-1)+.008*np.sum((delta-prev[j])**2,axis=-1)
    best=int(np.argmin(score));current=candidates[best]
    if best==0:break
 raw[i]=current-q0;prev=raw[i]
 if i%30==0:print('LOCAL_GUIDANCE',i,len(times),'eval',evals,'sec',round(time.perf_counter()-start,2),flush=True)
smooth=gaussian_filter1d(raw,2,axis=0,mode='nearest')*env[:,:,None]
smooth[:,[0,4]]=0
# A single deterministic temporal filter, not a new motion fit or candidate.
q=source+smooth
for j,d in enumerate(m.c.DIGITS):
 lo,hi=m.c.bounds(d);assert np.min(q[:,j]-np.degrees(lo))>-.0001 and np.min(np.degrees(hi)-q[:,j])>-.0001
np.savez_compressed(P/'LIGHTWEIGHT_TRAJECTORY.npz',times=times,source_qdeg=source,correction_deg=smooth,qdeg=q,envelope=env,raw_correction_deg=raw)
elapsed=time.perf_counter()-start
receipt=dict(motion_generation_time_sec=elapsed,processed_frames=len(times),frame_hz=30,full_duration_sec=5.95,modified_digits=['INDEX','MIDDLE','RING'],engineering_coordinates=12,pose_bones=9,local_fk_evaluations=evals,batched_calls=batches,nonlinear_optimizer_called=False,new_heavy_solver_calls=0,formal_attempts=1,candidate_count=1,per_note_pose_patches=False,trust_degrees=trust.tolist(),max_abs_correction_deg=np.max(abs(smooth),axis=0).tolist(),max_correction_velocity_deg_sec=float(np.max(abs(np.diff(smooth,axis=0)/np.diff(times)[:,None,None]))),strategy_sha256=__import__('hashlib').sha256((P/'STRATEGY_LOCK.json').read_bytes()).hexdigest())
(P/'GENERATION_RECEIPT.json').write_text(json.dumps(receipt,indent=2),encoding='utf8')
assert elapsed<600
print(json.dumps(receipt),flush=True)
