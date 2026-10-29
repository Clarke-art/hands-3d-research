from stage_common import *
from coordinated_motion import *
import time
assert not (P/'CANDIDATE_ATTEMPT.json').exists(),'ONE NEW DYNAMIC CANDIDATE ONLY'
lock=read(P/'GENERATION_LOCK.json');assert all(sha(P/n)==h for n,h in lock['scripts'].items())
assert sha(P/'GENERATION_POLICY.json')==lock['policy_sha256']
tl=read(P/'PERFORMANCE_TIMELINE.json');assert sha(P/'PERFORMANCE_TIMELINE.json')==lock['timeline_sha256']
pol=read(P/'GENERATION_POLICY.json');co=EventCoordinator(tl['notes'],pol);events=co.events
dump('CANDIDATE_ATTEMPT.json',dict(attempt=1,restarts=0,status='STARTED',motion_candidates=1))
end=np.ceil(tl['presentation_duration_sec']*60)/60
priority=np.unique(np.r_[0,end,[n['note_on']+d for n in events for d in [0,.0175,.035]],
    [n['note_off']+d for n in events for d in [-.045,0,.04,.07]]])
support=list(priority[(priority>=0)&(priority<=end)])
for t in sorted(np.r_[np.arange(0,end,.09),[n['note_on']+d for n in events for d in [-.18,-.075]],
    [n['note_off']+d for n in events for d in [.035,.15]]]):
    if 0<=t<=end and min(abs(np.array(support)-t))>=.004:support.append(float(t))
knots=np.array(sorted(support));K=len(knots);N=len(events);dt=np.diff(knots)
# Event-level adjacent-pair initial poses, only an initialization inside this one
# trajectory solve. All knot roots and digits remain optimization variables.
seedstates=[];seedtimes=[]
for i,n in enumerate(events):
    tasks=[(n['finger']-1,i,0,6.)]
    if i+1<N and events[i+1]['finger']!=n['finger']:
        tasks.append((events[i+1]['finger']-1,i+1,.008,1.8))
    fit=co.static_solve(n['note_on']+.035,tasks)
    seedstates.append(fit.x);seedtimes.append(n['note_on']+.035)
seedstates=np.array(seedstates);seed=np.column_stack([np.interp(knots,seedtimes,seedstates[:,d]) for d in range(26)])
X0=np.r_[seed.ravel(),co.xy_seed.ravel()]
lower=np.r_[np.tile(co.state_low,K),co.xy_low.ravel()];upper=np.r_[np.tile(co.state_high,K),co.xy_high.ravel()]
X0=np.clip(X0,lower+1e-6,upper-1e-6)
taskidx=np.zeros((K,5),int);taskweights=np.zeros((K,5));lifts=np.zeros((K,5));taskrows=[]
for k,t in enumerate(knots):
    tasks=co.tasks(float(t));taskrows.append(tasks)
    for j,i,lift,w in tasks:taskidx[k,j]=i;taskweights[k,j]=w;lifts[k,j]=lift
angles=np.array([co.key_angles(t) for t in knots]);pivots=np.array([co.keys[n['midi_note']]['press_pivot'] for n in events])
tops=np.array([s['z']+.0005 for s in co.surfaces]);tkey=np.array([n['key_index'] for n in events])
taskangles=angles[np.arange(K)[:,None],tkey[taskidx]]
taskrot=rotations(taskangles,[1,0,0]);taskpivot=pivots[taskidx]
boxpivot=np.array([co.keys[m]['press_pivot'] for m in co.boxkeys]);boxangles=angles[:,np.array(co.boxkeys)-21]
boxrot=rotations(-boxangles,[1,0,0])
margin=np.full((K,5,len(co.boxkeys)),.003)
for k,tasks in enumerate(taskrows):
    for j,i,lift,w in tasks:
        if w>1:margin[k,j,np.array(co.boxkeys)==events[i]['midi_note']]=0
lo,hi=co.boxlo,co.boxhi
velweight=np.r_[[pol['velocity_weights'][0],pol['velocity_weights'][1],pol['velocity_weights'][2]],
    [pol['velocity_weights'][3]]*3,[.020]*20]
accweight=np.r_[[pol['acceleration_weights'][0],pol['acceleration_weights'][1],pol['acceleration_weights'][2]],
    [pol['acceleration_weights'][3]]*3,[.00070]*20]
calls=0;started=time.monotonic();last=started;pernode=15+5*len(co.boxkeys)+10+20+3+3+5
def residual(x):
    global calls,last
    calls+=1;states=x[:K*26].reshape(K,26);xy=x[K*26:].reshape(N,2)
    pads,joints=fk_batch(states)
    point=np.concatenate([xy[taskidx]/1000,tops[taskidx][...,None]],axis=-1)
    targets=np.einsum('kdij,kdj->kdi',taskrot,point-taskpivot)+taskpivot;targets[:,:,2]+=lifts
    contact=((pads-targets)*1000*taskweights[:,:,None]).reshape(K,-1)
    # Actual moving-key frame inverse before the finite key-volume proxy.
    vv=np.einsum('kbij,kdbj->kdbi',boxrot,pads[:,:,None,:]-boxpivot[None,None,:,:])+boxpivot[None,None,:,:]
    dd=np.abs(vv-(lo+hi)/2)-(hi-lo)/2
    sdf=np.linalg.norm(np.maximum(dd,0),axis=-1)+np.minimum(np.max(dd,axis=-1),0)
    collision=(np.maximum(margin-sdf,0)*1000*pol['clearance_weight']).reshape(K,-1)
    jp=joints[:,:,1:,:]
    covers=(jp[:,:,:,None,0]>lo[None,None,None,:,0])&(jp[:,:,:,None,0]<hi[None,None,None,:,0])&(jp[:,:,:,None,1]>lo[None,None,None,:,1])&(jp[:,:,:,None,1]<hi[None,None,None,:,1])
    top=np.max(np.where(covers,hi[None,None,None,:,2],-.010),axis=-1)
    jointclear=(np.maximum(top+.005-jp[:,:,:,2],0)*1000*.5).reshape(K,-1)
    prior=(states[:,6:]-NEUTRAL.ravel())*pol['joint_prior_weight']
    rootprior=(states[:,:3]-co.nominal[:3])*[.015,.035,.06]
    passive=(np.maximum(.005-pads[:,:,2],0)*(taskweights<1)*1000*2)
    pose=np.c_[contact,collision,jointclear,prior,states[:,3:6]*.20,rootprior,passive]
    assert pose.shape==(K,pernode)
    velocity=np.diff(states,axis=0)/dt[:,None]
    acceleration=np.diff(velocity,axis=0)/((dt[:-1]+dt[1:])/2)[:,None]
    out=[pose.ravel(),(velocity*velweight).ravel(),(acceleration*accweight).ravel(),((xy-co.xy_seed)*.12).ravel()]
    for i,n in enumerate(events[:-1]):
        if n['note_id'] in co.repeats:out.append((xy[i+1]-xy[i])*3)
    if time.monotonic()-last>15:
        print('ONE_JOINT_TRAJECTORY_ITERATIONS',calls,'elapsed',round(time.monotonic()-started,1),'contact_rms',round(float(np.sqrt(np.mean(contact**2))),3),flush=True);last=time.monotonic()
    return np.concatenate(out)
sample=residual(X0);J=lil_matrix((len(sample),len(X0)),dtype=np.int8);row=0
for k in range(K):
    cols=list(range(k*26,(k+1)*26))
    for j,i,lift,w in taskrows[k]:cols.extend([K*26+2*i,K*26+2*i+1])
    J[row:row+pernode,cols]=1;row+=pernode
for k in range(K-1):J[row:row+26,k*26:(k+2)*26]=1;row+=26
for k in range(K-2):J[row:row+26,k*26:(k+3)*26]=1;row+=26
J[row:row+2*N,K*26:]=1;row+=2*N
for i,n in enumerate(events[:-1]):
    if n['note_id'] in co.repeats:J[row:row+2,K*26+2*i:K*26+2*i+4]=1;row+=2
assert row==len(sample)
print('SINGLE_BANDED_SOLVE_START',K,'knots',len(X0),'parameters',len(sample),'residuals',flush=True)
fit=least_squares(residual,X0,bounds=(lower,upper),jac_sparsity=J.tocsr(),max_nfev=pol['max_trajectory_nfev'],
    x_scale='jac',ftol=2e-5,xtol=2e-5,gtol=2e-5,tr_options={'regularize':True},verbose=0)
assert np.isfinite(fit.x).all();states=fit.x[:K*26].reshape(K,26);xy=fit.x[K*26:].reshape(N,2)
# C1 shape-preserving interpolation on the jointly solved event support states.
times=np.unique(np.r_[np.arange(0,end+1/240,1/120),knots,
    [n[p]+d for n in events for p in ['note_on','note_off'] for d in [0,.0175,.035,.045,.07]]])
times=times[(times>=0)&(times<=end+1e-9)];traj=PchipInterpolator(knots,states,axis=0)(times)
assert np.all(traj>=co.state_low-1e-7) and np.all(traj<=co.state_high+1e-7)
KA=np.array([co.key_angles(t) for t in times]);Q=np.radians(traj[:,6:].reshape(-1,5,4));RR=extra_rotation(traj[:,3:6])
np.savez_compressed(P/'motion.npz',times=times,R_q=Q,R_delta=traj[:,:3]/1000,R_extra_rot_deg=traj[:,3:6],R_extra_rotation=RR,key_angles=KA)
dump('COORDINATED_TRAJECTORY_FIT.json',dict(candidate_count=1,restarts=0,nfev=fit.nfev,calls=calls,cost=float(fit.cost),
    success=bool(fit.success),message=fit.message,elapsed_sec=time.monotonic()-started,knots=knots,
    solved_states=states,solved_contact_xy_mm=xy,parameters=len(fit.x),
    root_and_all_fingers_are_joint_unknowns=True,moving_contact_locations_are_joint_unknowns=True,
    temporal_velocity_acceleration_constraints=True,not_a_fixed_root_retarget=True,source_event_count=16,
    no_per_note_manual_adjustment=True,policy_sha256=sha(P/'GENERATION_POLICY.json'),module_sha256=sha(P/'coordinated_motion.py')))
dump('MOTION_GENERATION.json',dict(candidate_count=1,motion_sha256=sha(P/'motion.npz'),samples=len(times),source_notes=16,
    source_time_unchanged=True,fingering_unchanged=True,left_generated=False,solves=1,restarts=0,
    sparse_event_support_knots=K,continuous_joint_and_root_curves=True,actions_baked=False))
print('ONE_COORDINATED_MOTION_SAVED',len(times),fit.nfev,fit.success,flush=True)
