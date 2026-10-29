from bridge_model import *
rows=json.loads((O/'R2_BASE_ACTUAL.json').read_text(encoding='utf8'));times=set();brackets=[]
for gate in ['all_required_contacts','target_depth','non_target_or_wrong_region_depth','authorized_domain']:
 i=next((i for i,r in enumerate(rows) if not r['gates'][gate]),None)
 if i is not None and i>0:
  a=rows[i-1]['display_time'];b=rows[i]['display_time'];brackets.append(dict(gate=gate,last_previous_time=a,first_failed_sample=b))
  times.update(a+(b-a)*k/8 for k in range(1,8))
save('R2_ADAPTIVE_TIMES.json',sorted(times));save('R2_ADAPTIVE_BRACKETS.json',brackets)
front=json.loads((O/'candidate_front_RESULT.json').read_text(encoding='utf8'));Z=np.array(front['latents']);T=np.array(front['times']);vv=tangents([z for z in Z],T);intervals=[];minmax=[]
tol=np.r_[[.001]*10,[1e-6,1e-6]]
for seg in range(len(T)-1):
 dt=T[seg+1]-T[seg];z0=Z[seg];z1=Z[seg+1];v0=vv[seg];v1=vv[seg+1];coef=np.array([z0,dt*v0,-3*z0-2*dt*v0+3*z1-dt*v1,2*z0+dt*v0-2*z1+dt*v1])
 for j in range(12):
  c=coef[:,j]
  critical=[0.,1.]+[float(r.real) for r in np.polynomial.polynomial.polyroots([c[1],2*c[2],3*c[3]]) if abs(r.imag)<1e-10 and 0<r.real<1]
  values=[float(np.polynomial.polynomial.polyval(x,c)) for x in critical]
  minmax.append(dict(segment=seg,control=j,minimum=min(values),maximum=max(values),tolerance=float(tol[j])))
  for label,bound in [('LOWER',LOW[j]-tol[j]),('UPPER',HIGH[j]+tol[j])]:
   poly=c.copy();poly[0]-=bound;roots=[0.,1.]+[float(r.real) for r in np.polynomial.polynomial.polyroots(poly) if abs(r.imag)<1e-10 and 0<r.real<1];roots=sorted(set(roots))
   for aa,bb in zip(roots,roots[1:]):
    val=np.polynomial.polynomial.polyval((aa+bb)/2,c);bad=val<bound if label=='LOWER' else val>bound
    if bad:intervals.append(dict(segment=seg,control=j,bound_type=label,actual_gate_bound=float(bound),u_interval=[aa,bb],time_interval=[float(T[seg]+aa*dt),float(T[seg]+bb*dt)],proof='Exact cubic latent-control polynomial with numerical root solving; actual gate tolerance preserved'))
save('R2_ANALYTIC_DOMAIN_INTERVALS.json',dict(status='C1_INITIALIZER_HAS_PROVEN_AUTHORIZED_PARAMETER_DOMAIN_VIOLATIONS',intervals=intervals,extrema=minmax,no_human_impossibility_claim=True,scope='Only the unsolved initialized cubic curve, not every possible corridor path'))
p=json.loads((O/'POLICY_LOCK.json').read_text(encoding='utf8'));p.update(no_more_solves=True,primary_optimizer_calls=1,proposed_high_level_candidates=2,second_optimizer_early_stopped=True,STOP='STOP — HUMAN REVIEW');save('POLICY_LOCK.json',p)
print('R2_ADAPTIVE_POINTS',len(times),'analytical_bad_intervals',len(intervals),flush=True)
