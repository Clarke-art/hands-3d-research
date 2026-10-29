from model import *
from persistence import atomic_record,atomic_json,load_record
from scipy.optimize import least_squares
import traceback
assert read(O/'INPUT_GATE.json')['pass_'];P=read(O/'POLICY.json');I=read(O/'INPUT_BINDINGS.json')
assert not (O/'SOURCE_PRECHECK_STARTED.json').exists()
atomic_json('SOURCE_PRECHECK_STARTED.json',dict(batches=1,policy_sha256=sha(O/'POLICY.json'),code_sha256=sha(__file__),model_sha256=sha(O/'model.py')))
SOURCEDIR=ROOT/'experiments/hands_reusable_motion_representation_feasibility_r1'
with np.load(SOURCEDIR/'SOURCE_AUDIT_SAMPLES.npz',allow_pickle=False) as a:S={k:a[k] for k in a.files if k!='metadata_utf8'}
features,_=load_record('SOURCE_FEATURES.npz');event=I['source'][-1];j=event['finger']-1;rows=[];outq=[];outworld=[];outangles=[];sourceverts=[];start=time.perf_counter()
for k,t in enumerate(P['source_witness_times']):
 ix=int(np.argmin(abs(S['times']-t)));q=S['qdeg'][ix];world=S['rig_world'][ix];angles=S['key_angles'][ix];key=KEYS[event['key_index']];pv=np.array(key['press_pivot']);p=rot(-angles[event['key_index']],key['press_axis'])@(S['vertices'][ix,PADIDS[j]]-pv)+pv
 preferred=np.clip(p[:2]*1000,*inset(key));seed,lo,hi,fun,ids=local_fit_inputs(q,world,angles,event,preferred,P);last=seed.copy();lastfun=fun(seed);calls=0
 def bounded_fun(x):
  global last,lastfun,calls
  if time.perf_counter()-start>24:raise TimeoutError('SOURCE_BATCH_24_SECONDS_CAP')
  y=fun(x);assert np.isfinite(y).all();last=x.copy();lastfun=y.copy();calls+=1;return y
 try:
  fit=least_squares(bounded_fun,seed,bounds=(lo,hi),max_nfev=P['source_local_max_nfev'],ftol=1e-6,xtol=1e-6,gtol=1e-6)
  changed=q.copy();changed[j]=fit.x[:4]
  atomic_record('SOURCE_LOCAL_RESULT_'+str(k)+'.npz',dict(x=fit.x,fun=fit.fun,grad=fit.grad,active_mask=fit.active_mask,q=changed,world=world,key_angles=angles,x0=seed),dict(record_type='SOURCE_LOCAL_OPTIMIZER_RESULT_NOT_ANIMATION',time=t,nfev=fit.nfev,njev=fit.njev,success=bool(fit.success),message=fit.message,cost=float(fit.cost),optimality=float(fit.optimality),residual_calls=calls,elapsed_total_seconds=time.perf_counter()-start,other_digits_and_root_frozen=True))
 except BaseException:
  atomic_record('SOURCE_LOCAL_EXCEPTION_'+str(k)+'.npz',dict(x=last,fun=lastfun),dict(record_type='INTERMEDIATE_ONLY',error=traceback.format_exc(),time=t));raise
 V=native(changed,world)[0];_,h,g,_=surface_metrics(V[PADIDS[j]][None],key,angles[event['key_index']]);ds,obstacles=depths(V[ids],angles,event['key_index']);peak=float(max(0,ds.max()));loc=np.unravel_index(ds.argmax(),ds.shape)
 row=dict(time=t,nfev=fit.nfev,success=bool(fit.success),contact_horizontal_mm=float(h[0]*1000),contact_gap_mm=float(g[0]*1000),active_own_skin_wrong_key_max_mm=peak,peak_key=obstacles[loc[0]][0]['note_name'],peak_vertex=int(ids[loc[1]]),contact_pass=bool(h[0]*1000<=.03 and abs(g[0]*1000)<=3),local_geometry_pass=peak<=.5,angular_change_deg=changed[j]-q[j],preferred_xy_change_mm=fit.x[4:]-preferred)
 rows.append(row);outq.append(changed);outworld.append(world);outangles.append(angles);sourceverts.append(S['vertices'][ix]);print('SOURCE_LOCAL',row,flush=True)
atomic_record('SOURCE_LOCAL_STATES.npz',dict(times=P['source_witness_times'],q=outq,world=outworld,key_angles=outangles,source_vertices=sourceverts),dict(record_type='STATIC_NECESSARY_CAPABILITY_PROBES_NOT_SOURCE_REPAIR',local_solver_calls=3))
atomic_json('SOURCE_LOCAL_NUMERIC_SUMMARY.json',dict(rows=rows,local_solver_calls=3,variables_per_call=6,complete_source_motion_repaired=False,elapsed_seconds=time.perf_counter()-start))
protect()
