from total_angle_pipeline import *
assert not (P/'CANDIDATE_ATTEMPT.json').exists()
p=TotalAnglePipeline();zero=np.zeros(len(p.free));q=p.evaluate(zero,p.times);stored=np.degrees(p.A['L_q']).reshape(-1,20)
cert=p.certify(zero);parity=float(np.max(abs(q-stored)));assert parity<1e-12 and cert['pass_']
# A finite nonzero, non-performance engineering perturbation tests the actual
# 113-knot influence collar, all827 times, and boundary C1 behavior.
probe=.01*(p.upper-p.lower)/2
probe=np.minimum(probe,.5*p.upper);probe=np.maximum(probe,.5*p.lower)
testx=probe.ravel()[p.free];nonzero=p.certify(testx);assert nonzero['pass_']
# Same previously established synthetic counterexample; no planner invocation.
kk=np.array([0.,1.,2.]);ref=np.array([22.,24.7,25.]);cor=np.array([3.,.3,-.3]);tt=np.linspace(0,2,201)
old=PchipInterpolator(kk,ref)(tt)+PchipInterpolator(kk,cor)(tt);new=PchipInterpolator(kk,ref+cor)(tt)
assert old.max()>25+1e-7 and new.max()<=25+1e-7
fake=np.zeros((2,20));fake[1,2]=-.125
reject=rec.inspect_stage('SYNTHETIC_REJECTION',np.array([0.,.25]),fake,p.low,p.high);assert not reject['pass_']
meta=dict(nfev=7,status=1,success=True,message='Synthetic fixture, no optimizer',cost=0.,optimality=0.,max_nfev=10)
rec.record_before_guard(P/'synthetic_recorder_checkpoint.json',meta,[reject],{}, {},origin='ARTIFICIAL_FIXTURE_ONLY')
# Finite ten pose prechecks, same actual degrees and budget as formal solver.
model=o.models('L');patches=read(P/'PAD_PATCHES.json');indices=sorted(set(i for pa in patches for i in pa['vertices']));lookup={v:i for i,v in enumerate(indices)};patchix=[[lookup[v] for v in pa['vertices']] for pa in patches]
times=sorted(set([n['note_on']+.04 for n in p.co.events]+[(n['note_on']+n['note_off'])/2 for n in p.co.events]));fullref=PchipInterpolator(p.knots,p.reference_states,axis=0);tests=[]
for t in times:
    reference=fullref(t)[None,:];goal,weights=region.targets_relative_to_reference(p.co,np.array([t]),reference,p.policy['regions']);outside=p.outside_mask(np.array([t]))[0]
    active=np.flatnonzero(~outside);lo,hi=actual_delta_bounds(reference[0,6:],p.low,p.high,p.budget)
    def state(x):
        delta=np.zeros(20);delta[active]=x;ss=reference.copy();ss[:,6:]=total_angles(reference[:,6:],delta);return ss
    def residual(x):return np.r_[((fk_batch(state(x))[0]-goal)*1000*weights[:,:,None]).ravel(),x*p.policy['joint_correction_prior']]
    fit=least_squares(residual,np.clip(np.zeros(len(active)),lo[active]+1e-8,hi[active]-1e-8),bounds=(lo[active],hi[active]),max_nfev=100,ftol=1e-7,xtol=1e-7,gtol=1e-7)
    st=state(fit.x);delta=st[0,6:]-reference[0,6:];caps=skin_caps_batch(st,model,indices)[0];pads=fk_batch(st)[0][0];contacts=[]
    for i,n in enumerate(p.co.events):
        if n['note_on']<=t<n['note_off']:
            j=n['finger']-1;s=p.co.surfaces[i];xs=caps[patchix[j],0]*1000;a,b=np.quantile(xs,[.05,.95]);edge=min(a-s['xmin']*1000,s['xmax']*1000-b);err=np.linalg.norm(pads[j]-goal[0,j])*1000
            contacts.append(dict(note_id=n['note_id'],finger=j+1,pad_min_edge_mm=float(edge),target_error_mm=float(err),pass_=bool(edge>0 and err<.1*edge)))
    domain=rec.inspect_stage('STATIC_TOTAL_ANGLE',np.array([t]),st[:,6:],p.low,p.high);budgetok=bool(np.all(abs(delta)<=p.budget+1e-7))
    tests.append(dict(time=t,nfev=fit.nfev,success=bool(fit.success),actual_delta_deg=delta.reshape(5,4),contacts=contacts,engineering_domain_pass=domain['pass_'],actual_budget_pass=budgetok))
    print('STATIC_SAME_ACTUAL_BUDGET',t,contacts,flush=True)
staticpass=all(r['engineering_domain_pass'] and r['actual_budget_pass'] and all(c['pass_'] for c in r['contacts']) for r in tests)
result=dict(pass_=staticpass,zero_correction_max_abs_deg=parity,zero_correction_certificate=cert,nonzero_engineering_fixture_certificate=nonzero,old_counterexample_max_excess_deg=float(old.max()-25),new_counterexample_guard_pass=True,illegal_fixture_guard_rejected=True,recorder_checkpoint_before_guard_verified=True,static_actual_budget_tests=tests,static_solves=10,contact_region_unchanged=p.policy['regions']==read(R3/'GENERATION_POLICY.json')['regions'],budget_numbers_unchanged=p.policy['joint_delta_limits_deg']==read(R3/'GENERATION_POLICY.json')['joint_delta_limits_deg'],support_knots=len(p.knots),original_output_samples=len(p.times),free_actual_delta_parameters=len(p.free),mutable_nodes_by_finger=[int(np.sum(p.mutable[:,j*4])) for j in range(5)],windows=p.windows,formal_solves=0,production_candidates=0)
dump('PREGENERATION_VALIDATION.json',result)
if not staticpass:raise RuntimeError('PREGENERATION_FAILED_STOP_ZERO_CANDIDATES')
print('ALL_PREGENERATION_GATES_PASS',len(p.free),'parameters',flush=True)
