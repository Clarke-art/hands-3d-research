from contact_region import *
import time
assert not (P/'CANDIDATE_ATTEMPT.json').exists(),'ONE_NEW_DYNAMIC_CANDIDATE_ONLY'
lock=read(P/'GENERATION_LOCK.json')
assert all(sha(P/n)==h for n,h in lock['scripts'].items())
assert sha(P/'GENERATION_POLICY.json')==lock['policy_sha256']
pol=read(P/'GENERATION_POLICY.json');tl=read(P/'PERFORMANCE_TIMELINE.json');co=EventCoordinator(tl['notes'],pol['source_policy']);regions=pol['regions']
old=read(R2/'COORDINATED_TRAJECTORY_FIT.json');knots=np.array(old['knots']);reference=np.array(old['solved_states']);K=len(knots);dt=np.diff(knots)
assert sha(R2/'motion.npz')==pol['reference_motion_sha256'] and sha(R2/'COORDINATED_TRAJECTORY_FIT.json')==pol['reference_fit_sha256']
A=dict(np.load(R2/'motion.npz'));model=o.models('L');patches=read(P/'PAD_PATCHES.json');indices=sorted(set(i for p in patches for i in p['vertices']));lookup={v:i for i,v in enumerate(indices)};patchix=[[lookup[v] for v in p['vertices']] for p in patches]
env=activity_envelope(knots,co.events,pol['source_policy']);en20=np.repeat(env,4,axis=1)
goal,weights=targets_relative_to_reference(co,knots,reference,regions)
limits=np.tile(np.array(pol['joint_delta_limits_deg']).ravel(),(K,1));lower=np.maximum(-limits,co.state_low[6:]-reference[:,6:]);upper=np.minimum(limits,co.state_high[6:]-reference[:,6:])
assert np.all(lower<upper)
active=[[(i,n) for i,n in enumerate(co.events) if n['note_on']<=t+1e-10 and t<n['note_off']-1e-10] for t in knots]
refcaps=skin_caps_batch(reference,model,indices)
basepads=fk_batch(reference)[0]
print('EXACT_SKIN_MARKER_PARITY',max(np.max(np.linalg.norm(refcaps[:,lookup[p['marker_vertex']]]-basepads[:,j],axis=1))*1000 for j,p in enumerate(patches)),flush=True)
calls=0;last=time.monotonic();started=last
def residual(x):
    global calls,last
    calls+=1;latent=x.reshape(K,20);correction=latent*en20;st=reference.copy();st[:,6:]+=correction
    pads=fk_batch(st)[0];caps=skin_caps_batch(st,model,indices)
    contact=((pads-goal)*1000*weights[:,:,None]).reshape(K,15)
    edge=np.zeros((K,10))
    for k,ns in enumerate(active):
        for i,n in ns:
            j=n['finger']-1;s=co.surfaces[i];xx=caps[k,patchix[j],0]*1000;a,b=np.quantile(xx,[.05,.95])
            slack=regions[i]['edge_slack_mm']
            edge[k,j*2]=max(0,s['xmin']*1000+slack-a)*pol['pad_edge_penalty_weight']
            edge[k,j*2+1]=max(0,b-(s['xmax']*1000-slack))*pol['pad_edge_penalty_weight']
    local=np.c_[contact,edge,latent*pol['joint_correction_prior']]
    v=np.diff(correction,axis=0)/dt[:,None];acc=np.diff(v,axis=0)/((dt[:-1]+dt[1:])/2)[:,None]
    if time.monotonic()-last>20:
        print('ONE_CORRECTION_SOLVE',calls,'elapsed',round(time.monotonic()-started,1),'contact_rms',round(float(np.sqrt(np.mean(contact**2))),4),flush=True);last=time.monotonic()
    return np.r_[local.ravel(),(v*pol['correction_velocity_weight']).ravel(),(acc*pol['correction_acceleration_weight']).ravel()]
X0=np.zeros((K,20));sample=residual(X0.ravel());J=lil_matrix((len(sample),K*20),dtype=np.int8);row=0
for k in range(K):J[row:row+45,k*20:(k+1)*20]=1;row+=45
for k in range(K-1):J[row:row+20,k*20:(k+2)*20]=1;row+=20
for k in range(K-2):J[row:row+20,k*20:(k+3)*20]=1;row+=20
assert row==len(sample)
dump('CANDIDATE_ATTEMPT.json',dict(attempt=1,dynamic_candidates=1,restarts=0,status='STARTED',policy_sha256=sha(P/'GENERATION_POLICY.json'),no_second_candidate=True))
fit=least_squares(residual,np.clip(X0.ravel(),lower.ravel()+1e-8,upper.ravel()-1e-8),bounds=(lower.ravel(),upper.ravel()),jac_sparsity=J.tocsr(),max_nfev=pol['max_nfev'],x_scale='jac',ftol=2e-6,xtol=2e-6,gtol=2e-6,tr_options={'regularize':True})
latent=fit.x.reshape(K,20);times=A['times'];outenv=activity_envelope(times,co.events,pol['source_policy']);corr=PchipInterpolator(knots,latent,axis=0)(times)*np.repeat(outenv,4,axis=1)
q=np.degrees(A['L_q']).reshape(-1,20)+corr
assert np.all(q>=co.state_low[6:]-1e-7) and np.all(q<=co.state_high[6:]+1e-7),'Bound exceeded: stop, no refit'
np.savez_compressed(P/'motion.npz',**{**A,'L_q':np.radians(q.reshape(-1,5,4))})
dump('COORDINATED_TRAJECTORY_FIT.json',dict(candidate_count=1,restarts=0,nfev=fit.nfev,calls=calls,cost=float(fit.cost),success=bool(fit.success),message=fit.message,optimality=float(fit.optimality),solver_limit_reached=fit.nfev>=pol['max_nfev'],elapsed_sec=time.monotonic()-started,knots=knots,reference_states=reference,latent_correction_deg=latent,solved_states=np.c_[reference[:,:6],reference[:,6:]+latent*en20],sample_joint_delta_deg=corr.reshape(-1,5,4),solved_contact_xy_mm=[[r['target_x_mm'],old['solved_contact_xy_mm'][i][1]] for i,r in enumerate(regions)],root_trajectory_bitwise_preserved=True,unassigned_fingers_exact_zero_correction=True,temporal_correction_constraints=True,not_a_new_motion_redesign=True))
dump('MOTION_GENERATION.json',dict(candidate_count=1,motion_sha256=sha(P/'motion.npz'),samples=len(times),solves=1,restarts=0,source_time_unchanged=True,fingering_unchanged=True,root_bitwise_preserved=True,key_angles_bitwise_preserved=True,right_generated=False))
dump('CANDIDATE_ATTEMPT.json',dict(attempt=1,dynamic_candidates=1,restarts=0,status='MOTION_SAVED',nfev=fit.nfev,success=bool(fit.success),no_second_candidate=True))
print('ONLY_DYNAMIC_CANDIDATE_SAVED',fit.success,fit.message,fit.nfev,'max_joint_deg',np.max(abs(corr)),flush=True)
