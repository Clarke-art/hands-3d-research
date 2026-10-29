from path_model import *
from scipy.optimize import least_squares
from scipy.sparse import csr_matrix
assert read(OUT/'CONTINUOUS_TARGET_GATE.json')['pass_']
assert not (OUT/'PATH_ATTEMPT_STARTED.json').exists()
policy=read(OUT/'SOLVER_POLICY.json');manifest=read(OUT/'ENVELOPE_MANIFEST.json');curve=Curve()
# Whole-window control samples, not three independent poses. Exact ON/OFF,
# follow endpoints and source collision peak join the grid deterministically.
indices=set(range(0,len(BASE['times']),4))|{len(BASE['times'])-1}
special=[n[x] for n in NOTES for x in ['note_on','note_off'] if START<=n[x]<=END]+[SCOPE['old']['note_off']+POL['finger_release_follow_sec'],manifest['witness_time']]
indices|={int(np.argmin(abs(BASE['times']-t))) for t in special}
idx=np.array(sorted(indices));ctx=Context(BASE['times'][idx],manifest);target=curve.targets(ctx,manifest)
started=time.perf_counter();calls=0;last=np.zeros(16);last_save=started;trace=[]
save('PATH_ATTEMPT_STARTED.json',dict(path_scheme_count=1,optimizer_calls=1,variables=16,samples=len(idx),
    numerical_budget_cumulative_seconds=300,policy_sha256=sha(OUT/'SOLVER_POLICY.json'),source_files_sha256={n:sha(OUT/n) for n in ['path_model.py','solve_path.py','runtime.py']},
    root_freedoms=0,no_static_pose_optimization=True))
def residual(x):
    global calls,last,last_save
    if time.perf_counter()-started>policy['solver_wall_seconds']:raise TimeoutError('One path attempt wall limit; no restart')
    calls+=1;last=np.array(x).copy();q=curve.state(x,ctx.t);V=ctx.model(q);gaps,_=ctx.envelope(V)
    point=(V[:,ctx.marker]-target)*1000;weights=np.full((len(ctx.t),5),.15)
    for k,t in enumerate(ctx.t):
        for j in CHANGED:
            state,n=role(float(t),j)
            weights[k,j]=6 if state=='ACTIVE_HOLD' else 4.2 if state=='RELEASING' else 4*smooth((t-n['note_on']+POL['prepare_sec'])/POL['prepare_sec']) if state=='PREPARING' else .15
    contacts=ctx.contacts(V);contact=[]
    for r in contacts:
        contact.extend([max(0,abs(r['gap_mm'])-3)*20,max(0,r['horizontal_mm']-.03)*20])
    keys,_=ctx.key_regression(V)
    delta=q[:,CHANGED]-ctx.source[:,CHANGED];dt=np.diff(ctx.t)[:,None,None]
    speed=np.diff(delta,axis=0)/dt;acc=np.diff(speed,axis=0)/((np.diff(ctx.t[:-1])+np.diff(ctx.t[1:]))[:,None,None]/2)
    lower=np.array([0,0,0,-28]);upper=np.array([75,95,65,28])
    bounds=np.maximum(lower-q[:,CHANGED],0)+np.maximum(q[:,CHANGED]-upper,0)
    values=np.r_[(point[:,CHANGED]*weights[:,CHANGED,None]).ravel(),np.array(contact),
        (np.maximum(.0007-gaps,0)*1000*3).ravel(),(keys*8).ravel(),
        (delta*np.array([.08,.08,.10,.30])).ravel(),(speed*.020).ravel(),(acc*.00070).ravel(),
        (np.maximum(abs(speed)-180,0)*.10).ravel(),(bounds*15).ravel()]
    if time.perf_counter()-last_save>10:
        trace.append(dict(calls=calls,elapsed_seconds=time.perf_counter()-started,cost=float(values@values/2)))
        np.savez_compressed(OUT/'LAST_EVALUATED_DIAGNOSTIC.npz',coefficients=last)
        save('NUMERICAL_TRACE.json',dict(rows=trace,iterate_semantics='Last evaluated residual including finite-difference probes, not an accepted solution'))
        print('CONTINUOUS_PREFLIGHT',calls,round(time.perf_counter()-started,2),flush=True);last_save=time.perf_counter()
    return values
seed=np.zeros(16);initial=residual(seed);trust=np.tile(policy['trust_degrees'],4)
try:
    fit=least_squares(residual,seed,bounds=(-trust,trust),jac_sparsity=csr_matrix(np.ones((len(initial),16),dtype=np.int8)),
        max_nfev=policy['max_nfev'],x_scale='jac',ftol=2e-5,xtol=2e-5,gtol=2e-5,tr_options={'regularize':True})
    x=fit.x;termination=dict(success=bool(fit.success),status=int(fit.status),message=fit.message,nfev=fit.nfev,cost=float(fit.cost),optimality=float(fit.optimality),numerical_termination_only=True)
except TimeoutError as e:
    x=last;termination=dict(success=False,message=str(e),nfev=None,point_semantics='Last evaluated objective, possibly a finite-difference probe; diagnostic only')
core_elapsed=time.perf_counter()-started
np.savez_compressed(OUT/'PATH_PREFLIGHT.npz',coefficients=x,knots=curve.knots,times=BASE['times'],qdeg=curve.state(x,BASE['times']),source_qdeg=BASE['qdeg'])
dense=Context(BASE['times'],manifest);q=curve.state(x,dense.t);V=dense.model(q);gaps,_=dense.envelope(V);contacts=dense.contacts(V);key_excess,key_rows=dense.key_regression(V);cert=curve_certificate(curve,x)
pre_pass=all(r['pass_'] for r in contacts) and not key_rows and cert['domain_pass'] and cert['correction_velocity_pass'] and gaps.min()>=0
save('PATH_PREFLIGHT_RESULT.json',dict(termination=termination,residual_calls=calls,solver_core_seconds=core_elapsed,
    evaluation_samples=len(ctx.t),dense_samples=len(dense.t),certificate=cert,contacts=contacts,key_regressions=key_rows,
    envelope_min_gap_mm=float(gaps.min()*1000),proxy_collision_samples=int((gaps.min(1)<0).sum()),preflight_pass=bool(pre_pass),
    boundary_proxy_gap_mm=(gaps[[0,-1]].min(1)*1000).tolist(),
    candidate_count=0,geometry_status='NUMERICAL_PREFLIGHT_ONLY_ACTUAL_BLENDER_REQUIRED',
    limitations='Dense discrete envelope/key samples; no continuous geometric proof; conservative proxy can reject actual separated skin'))
save('ADAPTIVE_PROBES.json',dict(times=[float((a+b)/2) for a,b,g1,g2 in zip(dense.t[:-1],dense.t[1:],gaps.min(1)[:-1],gaps.min(1)[1:]) if min(g1,g2)<.001],
    reason='One deterministic midpoint pass for close/colliding envelope intervals, no new optimization'))
print('ONE_CONTINUOUS_PATH_PREFLIGHT_FINISHED',termination['message'],'core_seconds',core_elapsed,'machine_preflight',pre_pass,flush=True)
