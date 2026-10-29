import json as _lock_json
from pathlib import Path as _LockPath
if __name__ == "__main__" and _lock_json.loads((_LockPath(__file__).resolve().parent / "POLICY_LOCK.json").read_text(encoding="utf-8"))["no_more_solves"]:
    raise SystemExit("STOP — HUMAN REVIEW: completed experiment is locked; use a separately authorized run")
import sys,time,json,ctypes,os,hashlib
from pathlib import Path
sys.dont_write_bytecode=True;O=Path(__file__).resolve().parent;sys.path.insert(0,str(O));T=time.monotonic()
import derivative_probe as d
from derivative_probe import np,ca,save
# Explicit cumulative numerical ledger; previous completed phases charged, including imports.
budget_files=['RUN_BUDGET.json','EXTRA_BUDGET.json','PRUNED_BUDGET.json','ORIGINAL_DIRECT_BUDGET.json','STAGE2_BUDGET.json','NEIGHBOR_BUDGET.json','FACE_BUDGET.json']
prior={n:json.loads((O/n).read_text())['charged_seconds'] for n in budget_files};prior['first_derivative_probe_seconds']=9.406;prior['failed_UTF8_start_conservative_seconds']=2.;prior['shell_parser_failed_conservative_seconds']=1.
remaining=600-sum(prior.values());deadline=T+remaining
def guard():
 if time.monotonic()>deadline:raise TimeoutError('600 second cumulative numerical deadline')
class Memory(ctypes.Structure):
 _fields_=[('cb',ctypes.c_ulong),('PageFaultCount',ctypes.c_ulong),('PeakWorkingSetSize',ctypes.c_size_t),('WorkingSetSize',ctypes.c_size_t),('QuotaPeakPagedPoolUsage',ctypes.c_size_t),('QuotaPagedPoolUsage',ctypes.c_size_t),('QuotaPeakNonPagedPoolUsage',ctypes.c_size_t),('QuotaNonPagedPoolUsage',ctypes.c_size_t),('PagefileUsage',ctypes.c_size_t),('PeakPagefileUsage',ctypes.c_size_t)]
def rss():
 m=Memory();m.cb=ctypes.sizeof(m);ctypes.windll.psapi.GetProcessMemoryInfo(ctypes.windll.kernel32.GetCurrentProcess(),ctypes.byref(m),m.cb);return dict(working_set_bytes=m.WorkingSetSize,peak_working_set_bytes=m.PeakWorkingSetSize)
mem0=rss();old=np.load(O/'ORIGINAL_JACOBIAN.npz');new=np.load(O/'PRUNED_JACOBIAN.npz');g=ca.Function.load(str(O/'PRUNED_G.casadi'));oldg=ca.Function.load(str(O/'ORIGINAL_G.casadi'));j=ca.Function.load(str(O/'PRUNED_J.casadi'));x=old['x'];rng=np.arange(len(x));xp=x+0.007*np.sin(rng+1);ja=np.array(j(xp));checks=[]
for h in [1e-2,1e-3,1e-4]:
 cols=[]
 for i in range(len(x)):
  guard();delta=np.eye(len(x))[i]*h;cols.append((np.array(g(xp+delta)).ravel()-np.array(g(xp-delta)).ravel())/(2*h))
 fd=np.array(cols).T;err=abs(fd-ja);checks.append(dict(h=h,max_abs=float(err.max()),relative_frobenius=float(np.linalg.norm(fd-ja)/np.linalg.norm(fd)),missing_nonzeros=int(np.sum((abs(ja)<1e-12)&(abs(fd)>1e-5))),unstable_variables=np.flatnonzero(err.max(0)>1e-3).tolist()))
valuechecks=[]
for xx in [x,xp,new['x']]:
 guard();valuechecks.append(float(abs(np.array(g(xx))-np.array(oldg(xx))).max()))
sign_tests=[]
# Positive root Z must increase face height for zero-angle white key; tilted key gives cos(angle).
rs=json.loads((O/'FACE_SURFACE_VALIDATION.json').read_text())
for case in rs['cases']:sign_tests.append(dict(case=case['id'],d_gap_d_root_z=case['chart']['jacobian'][0][2],expected='positive; moving-key normal projection'))
save('DIRECT_JACOBIAN_VERIFICATION.json',dict(original_vs_pruned_max_abs=float(abs(old['jac']-new['jac']).max()),constraint_value_max_abs=valuechecks,checks=checks,sign_tests=sign_tests,memory_start=mem0,memory_end=rss(),scope='144 Bernstein coefficients, three actual adjacent timestamps. Perturbations used for derivative diagnostics only, never accepted states.'))
# IPOPT adapter smoke: only evaluate derivative at an existing state, zero optimization iterations.
guard();z=ca.MX.sym('z',12);skin=d.F(z)[0];contact=json.loads((O/'runs/recovery_dynamic.json').read_text());ct=contact['contacts'][0];key=d.c.KEYS[ct['midi']-21];a=json.loads((O/'RECOVERY_INPUT.json').read_text())['actual']['key_angles'][ct['midi']-21];pv=ca.DM(key['press_pivot']);p=ca.DM(d.c.axisrot(-a,key['press_axis']))@(skin[:,ct['vertices']]@ca.DM(ct['barycentric'])-pv)+pv;gg=(p[2]-key['key_top_playable_surface'][0]['z'])*1000+.005
solver=ca.nlpsol('derivative_smoke','ipopt',dict(x=z,f=ca.sumsqr(z-ca.DM(contact['latent'])),g=gg),dict(print_time=False,ipopt=dict(max_iter=0,max_wall_time=5,print_level=0,hessian_approximation='limited-memory')));solver(x0=contact['latent'],lbx=d.LOW,ubx=d.HIGH,lbg=-.0005,ubg=.0005);stats=solver.stats();save('SOLVER_INTERFACE_SMOKE.json',dict(return_status=stats['return_status'],n_call_nlp_jac_g=stats.get('n_call_nlp_jac_g'),iterations=stats['iter_count'],scope='Single-state zero-iteration derivative callback only; not a recovery or trajectory candidate'))
prior['final_derivative_verification_seconds']=time.monotonic()-T;save('TOTAL_NUMERICAL_BUDGET.json',dict(phases=prior,total_charged_seconds=sum(prior.values()),limit_seconds=600,under_budget=sum(prior.values())<=600,cumulative_deadline_enforced_for_final_stage=True,policy='No further numerical solves after final verification',includes='model builds, imports, failed starts, repeated diagnostic comparisons, SLSQP and independent Blender replay; sum of process wall times, concurrent overlap conservatively counted twice'))
