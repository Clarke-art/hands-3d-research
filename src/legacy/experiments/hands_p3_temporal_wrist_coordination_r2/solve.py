"""Exactly one formal solve; durable raw result precedes every diagnostic."""
from problem import *
from persistence import atomic_record,atomic_json,save_last,load_record
from scipy.optimize import least_squares
import traceback
assert read(O/'RESULT_PERSISTENCE_GATE.json')['RESULT_PERSISTENCE_GATE']=='PASS'
assert read(O/'INPUT_CONTRACT_GATE.json')['pass_']
lock=read(O/'POLICY_LOCK.json');assert sha(O/'POLICY.json')==lock['policy_sha256']
assert all(sha(O/n)==h for n,h in lock['scripts'].items())
assert not (O/'FORMAL_ATTEMPT_STARTED.json').exists()
pr=Problem();J=pr.sparsity();initial_fun=pr.residual(pr.x0)
atomic_json('FORMAL_ATTEMPT_STARTED.json',dict(attempt=1,restarts=0,policy_sha256=lock['policy_sha256'],script_sha256=sha(__file__),variables=len(pr.x0),control_nodes=pr.K))
atomic_record('FORMAL_INITIAL_STATE.npz',dict(x=pr.x0,fun=initial_fun),dict(record_type='SOLE_FORMAL_INITIAL_STATE',not_final_optimizer_result=True))
protect();started=time.perf_counter();lastx=pr.x0.copy();lastfun=initial_fun.copy();checkpoint=started
def fun(x):
 global lastx,lastfun,checkpoint
 if time.perf_counter()-started>pr.P['solver_internal_seconds']:raise TimeoutError('FIXED_74_SECOND_FORMAL_SOLVER_CAP')
 y=pr.residual(x)
 if not np.isfinite(y).all():raise ValueError('NONFINITE_FORMAL_RESIDUAL')
 lastx=x.copy();lastfun=y.copy();now=time.perf_counter()
 if now-checkpoint>=5:
  save_last('LAST_FINITE_EVALUATION.npz',lastx,lastfun,dict(residual_calls=pr.calls,elapsed_seconds=now-started,may_be_finite_difference_trial=True))
  checkpoint=now;print('FORMAL_PROGRESS',pr.calls,'calls',round(now-started,2),'seconds',flush=True)
 return y
try:
 fit=least_squares(fun,pr.x0,bounds=(pr.low,pr.high),jac_sparsity=J,max_nfev=pr.P['max_nfev'],ftol=1e-6,xtol=1e-6,gtol=1e-6)
 elapsed=time.perf_counter()-started;states,xy=pr.unpack(fit.x);jac=fit.jac.tocsr()
 arrays=dict(x=fit.x,fun=fit.fun,grad=fit.grad,active_mask=fit.active_mask,control_times=pr.T,states=states,source_states=pr.sourceT,contact_xy=xy,lower=pr.low,upper=pr.high,x0=pr.x0,initial_fun=initial_fun,jac_data=jac.data,jac_indices=jac.indices,jac_indptr=jac.indptr)
 metadata=dict(record_type='FINAL_OPTIMIZER_RESULT',schema_version=1,success=bool(fit.success),status=int(fit.status),message=str(fit.message),nfev=int(fit.nfev),njev=int(fit.njev),cost=float(fit.cost),optimality=float(fit.optimality),elapsed_seconds=elapsed,residual_calls=pr.calls,jac_shape=list(jac.shape),policy_sha256=lock['policy_sha256'],not_continuous_performance_pass=True)
 # FIRST operation after assembling the returned result: immutable raw bundle.
 finalhash=atomic_record('FINAL_OPTIMIZER_RESULT.npz',arrays,metadata)
 a,m=load_record('FINAL_OPTIMIZER_RESULT.npz');assert np.array_equal(a['x'],fit.x) and m==metadata
 atomic_json('FORMAL_RESULT_RECEIPT.json',dict(complete_final_result_saved=True,sha256=finalhash,metadata=metadata,roundtrip_pass=True,raw_result_precedes_diagnostics=True))
 print('FINAL_OPTIMIZER_RESULT_DURABLY_SAVED',metadata,flush=True)
except BaseException:
 error=traceback.format_exc()
 atomic_record('EXCEPTION_LAST_FINITE_STATE.npz',dict(x=lastx,fun=lastfun),dict(record_type='EXCEPTION_LAST_FINITE_STATE',not_final_optimizer_result=True,error=error,elapsed_seconds=time.perf_counter()-started,residual_calls=pr.calls))
 atomic_json('FORMAL_EXCEPTION.json',dict(error=error,last_finite_state_saved=True,final_result_exists=(O/'FINAL_OPTIMIZER_RESULT.npz').exists(),optimizer_restart_permitted=False))
 print(error,flush=True)
 raise
finally:protect()
