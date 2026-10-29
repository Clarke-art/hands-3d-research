from coupled_model import *
start=time.monotonic();p,data=load_problem();r=json.loads((O/'CORRECTION_SOLVE_RESULTS.json').read_text());x=np.array([n['latent'] for n in r['nodes']]).ravel();t=time.perf_counter();J=np.array(p.jfun(x));seconds=time.perf_counter()-t;direction=np.cos(np.arange(len(x))+.4);checks=[]
for h in [1e-5,1e-6,1e-7]:
 fd=(np.array(p.gfun(x+h*direction)).ravel()-np.array(p.gfun(x-h*direction)).ravel())/(2*h);checks.append(dict(h=h,max_abs=float(abs(fd-J@direction).max()),relative=float(np.linalg.norm(fd-J@direction)/max(np.linalg.norm(fd),1e-12))))
result=dict(status='OBSERVED_COUPLED_BRANCH_VERIFIED' if checks[-1]['max_abs']<1e-3 else 'NONSMOOTH_DERIVATIVE_PARTIAL',full_checked_jacobian_seconds=seconds,guards=[n.last_derivative_guard for n in p.nodes],directional_checks=checks,no_solver_executed=True,actual_solver_derivatives='Historical main/correction used single-step current-geometry FD; this stricter adaptive guard was added and independently validated afterward, not claimed retroactively.',global_smoothness=False,wall_seconds=time.monotonic()-start)
save('ADAPTIVE_DERIVATIVE_FALLBACK_CHECK.json',result);print(result,flush=True)
