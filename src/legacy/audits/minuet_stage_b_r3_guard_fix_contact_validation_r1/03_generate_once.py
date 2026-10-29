from total_angle_pipeline import *
import time
assert not (P/'CANDIDATE_ATTEMPT.json').exists(),'ONE_FORMAL_DYNAMIC_SOLVE_ATTEMPT_ONLY'
lock=read(P/'GENERATION_LOCK.json');assert all(sha(P/n)==h for n,h in lock['scripts'].items())
assert sha(P/'GENERATION_POLICY.json')==lock['policy_sha256']
assert read(P/'PREGENERATION_VALIDATION.json')['pass_']
p=TotalAnglePipeline();K=len(p.knots);dt=np.diff(p.knots);N=len(p.free)
baseline=read(P/'BASELINE_BIND.json');assert sha(R2/'motion.npz')==baseline['R2_motion_sha256']
model=o.models('L');patches=read(P/'PAD_PATCHES.json');indices=sorted(set(i for pa in patches for i in pa['vertices']));lookup={v:i for i,v in enumerate(indices)};patchix=[[lookup[v] for v in pa['vertices']] for pa in patches]
goal,weights=region.targets_relative_to_reference(p.co,p.knots,p.reference_states,p.policy['regions'])
active=[[(i,n) for i,n in enumerate(p.co.events) if n['note_on']<=t+1e-10 and t<n['note_off']-1e-10] for t in p.knots]
refcheck=p.refcurve(p.check_times);h=dt[:,None];calls=0;last=time.monotonic();started=last
def residual(x):
    global calls,last
    calls+=1;delta=p.expand(x);st=p.reference_states.copy();st[:,6:]=total_angles(p.reference_q,delta)
    pads=fk_batch(st)[0];caps=skin_caps_batch(st,model,indices)
    contact=((pads-goal)*1000*weights[:,:,None]).reshape(K,15);edge=np.zeros((K,10))
    for k,ns in enumerate(active):
        for i,n in ns:
            j=n['finger']-1;s=p.co.surfaces[i];a,b=np.quantile(caps[k,patchix[j],0]*1000,[.05,.95]);slack=p.policy['regions'][i]['edge_slack_mm']
            edge[k,j*2]=max(0,s['xmin']*1000+slack-a)*p.policy['pad_edge_penalty_weight']
            edge[k,j*2+1]=max(0,b-(s['xmax']*1000-slack))*p.policy['pad_edge_penalty_weight']
    local=np.c_[contact,edge,delta*p.policy['joint_correction_prior']]
    v=np.diff(delta,axis=0)/h;acc=np.diff(v,axis=0)/((dt[:-1]+dt[1:])/2)[:,None]
    curve=p.curve(x);outdelta=curve(p.check_times)-refcheck
    budget=np.maximum(abs(outdelta)-p.budget,0)*p.policy['actual_budget_output_penalty_weight']
    # Sufficient convex-hull bound on the actual correction cubic, plus output
    # checks. These are penalties, not clipping; final exact-extrema guard stays.
    dc=curve.c-p.refcurve.c
    controls=np.stack([dc[3],dc[3]+dc[2]*h/3,dc[3]+2*dc[2]*h/3+dc[1]*h*h/3,dc[3]+dc[2]*h+dc[1]*h*h+dc[0]*h*h*h],axis=1)
    controlbudget=np.maximum(abs(controls)-p.budget,0)*p.policy['actual_budget_output_penalty_weight']
    if time.monotonic()-last>20:
        print('ONE_TOTAL_Q_SOLVE',calls,'elapsed',round(time.monotonic()-started,1),'contact_rms',round(float(np.sqrt(np.mean(contact**2))),4),flush=True);last=time.monotonic()
    return np.r_[local.ravel(),(v*p.policy['correction_velocity_weight']).ravel(),(acc*p.policy['correction_acceleration_weight']).ravel(),budget.ravel(),controlbudget.ravel()]
# One deterministic initializer from the finite STATIC probes. Feasible clipping
# here applies to starting parameters, never to final output q.
pre=read(P/'PREGENERATION_VALIDATION.json');sttests=pre['static_actual_budget_tests'];seedtimes=np.r_[0,[s['time'] for s in sttests],p.knots[-1]];seed=np.r_[np.zeros((1,20)),np.array([s['actual_delta_deg'] for s in sttests]).reshape(-1,20),np.zeros((1,20))]
initial=np.column_stack([np.interp(p.knots,seedtimes,seed[:,j]) for j in range(20)])
lo=p.lower.ravel()[p.free];hi=p.upper.ravel()[p.free];X0=np.clip(initial.ravel()[p.free],lo+1e-8,hi-1e-8)
sample=residual(X0);J=lil_matrix((len(sample),N),dtype=np.int8);idx=np.full(K*20,-1);idx[p.free]=np.arange(N);idx=idx.reshape(K,20);row=0
def cols(nodes,dofs=range(20)):
    return [int(idx[k,j]) for k in nodes if 0<=k<K for j in dofs if idx[k,j]>=0]
for k in range(K):J[row:row+45,cols([k])]=1;row+=45
for k in range(K-1):J[row:row+20,cols([k,k+1])]=1;row+=20
for k in range(K-2):J[row:row+20,cols([k,k+1,k+2])]=1;row+=20
for t in p.check_times:
    k=min(K-2,max(0,int(np.searchsorted(p.knots,t,side='right')-1)))
    for j in range(20):J[row,cols(range(k-1,k+3),[j])]=1;row+=1
for k in range(K-1):
    for control in range(4):
        for j in range(20):J[row,cols(range(k-1,k+3),[j])]=1;row+=1
assert row==len(sample)
dump('CANDIDATE_ATTEMPT.json',dict(attempt=1,formal_dynamic_attempts=1,status='STARTED',restarts=0,parameters=N,policy_sha256=sha(P/'GENERATION_POLICY.json')))
print('ONLY_FORMAL_SOLVE_START',N,'parameters',len(sample),'residuals',flush=True)
try:
    fit=least_squares(residual,X0,bounds=(lo,hi),jac_sparsity=J.tocsr(),max_nfev=p.policy['max_nfev'],x_scale='jac',ftol=2e-6,xtol=2e-6,gtol=2e-6,tr_options={'regularize':True})
except Exception as exc:
    dump('SOLVER_AND_GUARD_DIAGNOSTICS.json',dict(formal_dynamic_attempts=1,solver_returned=False,exception_type=type(exc).__name__,exception=str(exc),last_residual_calls=calls,guard_not_reached=True,valid_candidate=False,no_second_attempt=True))
    raise
# IMMEDIATE checkpoint, before output interpolation/certification/guard.
meta=dict(nfev=fit.nfev,njev=fit.njev,status=int(fit.status),success=bool(fit.success),message=fit.message,cost=float(fit.cost),optimality=float(fit.optimality),active_mask=fit.active_mask,max_nfev=p.policy['max_nfev'],limit_reached=fit.nfev>=p.policy['max_nfev'],residual_calls=calls,elapsed_sec=time.monotonic()-started)
delta=p.expand(fit.x);supports=total_angles(p.reference_q,delta)
dump('SOLVER_RETURN_CHECKPOINT.json',dict(solver=meta,raw_unknown_actual_delta_deg=fit.x,latent_semantics='identity: actual_delta_deg, no unwindowed/envelope-divided latent',support_knots=p.knots,reference_q_deg=p.reference_q,actual_support_delta_deg=delta,support_total_q_deg=supports,mutable_mask=p.mutable,engineering_low_deg=p.low,engineering_high_deg=p.high,budget_actual_deg=p.budget,source_hashes=baseline))
try:
    qout=p.evaluate(fit.x,p.times);qcheck=p.evaluate(fit.x,p.check_times);certificate=p.certify(fit.x)
    stages=[rec.inspect_stage('RAW_TOTAL_SUPPORT_Q',p.knots,supports,p.low,p.high),rec.inspect_stage('FINAL_INTERPOLATED_827_TOTAL_Q',p.times,qout,p.low,p.high),rec.inspect_stage('EVENT_BOUNDARY_AND_FULL_OUTPUT_Q',p.check_times,qcheck,p.low,p.high),rec.inspect_stage('ACTUAL_OUTPUT_CORRECTION_BUDGET',p.check_times,qcheck-p.refcurve(p.check_times),-p.budget,p.budget)]
    ok=all(s['pass_'] for s in stages) and certificate['pass_']
    payload=dict(solver=meta,formal_dynamic_attempts=1,stages=stages,continuous_polynomial_certificate=certificate,engineering_domain_guarantee=certificate['domain']['pass_'],strict_guard_preserved=True,output_angles_clipped=False,root_optimized=False,valid_output=ok,no_second_attempt=True,output_times=p.times,final_total_q_deg=qout,final_actual_delta_deg=qout-p.refcurve(p.times))
    rec.write_checkpoint(P/'SOLVER_AND_GUARD_DIAGNOSTICS.json',payload)
except Exception as exc:
    dump('OUTPUT_PROCESSING_EXCEPTION.json',dict(exception_type=type(exc).__name__,exception=str(exc),solver_checkpoint_preserved=True,no_second_attempt=True))
    raise
if not ok:
    dump('CANDIDATE_ATTEMPT.json',dict(attempt=1,formal_dynamic_attempts=1,status='FAIL_CLOSED_OUTPUT_GUARD',solver_nfev=fit.nfev,solver_success=bool(fit.success),saved_candidates=0,no_second_attempt=True))
    raise RuntimeError('RECORDED_STRICT_OUTPUT_GUARD_FAILURE_NO_REFIT')
Q=p.A['L_q'].copy();inside=~p.outside_mask(p.times);flat=Q.reshape(-1,20);flat[inside]=np.radians(qout)[inside]
np.savez_compressed(P/'motion.npz',**{**p.A,'L_q':Q})
dump('COORDINATED_TRAJECTORY_FIT.json',dict(knots=p.knots,reference_states=p.reference_states,actual_support_delta_deg=delta,solved_states=np.c_[p.reference_states[:,:6],supports],success=bool(fit.success),nfev=fit.nfev,message=fit.message,candidate_count=1,root_bitwise_preserved=True,no_output_clipping=True))
dump('MOTION_GENERATION.json',dict(candidate_count=1,formal_attempts=1,source_samples=len(p.times),motion_sha256=sha(P/'motion.npz'),root_and_key_arrays_bitwise_preserved=True,source_events_unchanged=True,source_MIDI_sha256=sha(SOURCE)))
dump('CANDIDATE_ATTEMPT.json',dict(attempt=1,formal_dynamic_attempts=1,status='LEGAL_MOTION_SAVED',solver_nfev=fit.nfev,solver_success=bool(fit.success),saved_candidates=1,no_second_attempt=True))
print('ONE_LEGAL_TOTAL_Q_MOTION_SAVED',fit.nfev,fit.success,fit.message,'max_actual_delta_deg',float(np.max(abs(qout-p.refcurve(p.times)))),flush=True)
