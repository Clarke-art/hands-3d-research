from motion_core import *
assert not (O/'STATIC_REACH_STATES.npz').exists()
start=time.perf_counter();states=[];times=[];rows=[]
for i,n in enumerate(events):
 t=n['note_on']+.035;tasks=[(n['finger']-1,i,0.,pol['contact_weight'])]
 if i+1<len(events) and events[i+1]['finger']!=n['finger']:tasks.append((events[i+1]['finger']-1,i+1,.009,2.0))
 fit=co.static_solve(t,tasks);pads=fk_batch(fit.x)[0][0];err=float(np.linalg.norm(pads[n['finger']-1]-co.target(i,co.xy_seed,t))*1000)
 states.append(fit.x);times.append(t);rows.append(dict(note=n['note_id'],time=t,success=bool(fit.success),nfev=fit.nfev,active_FK_error_mm=err,root_xyz_m=BASE+fit.x[:3]/1000,extra_root_rotation_deg=fit.x[3:6],q_deg=fit.x[6:].reshape(5,4)))
 print('STATIC_REACH',n['note_id'],round(err,3),flush=True)
np.savez_compressed(O/'STATIC_REACH_STATES.npz',times=times,states=states,contact_xy=co.xy_seed)
dump('STATIC_FK_REACH.json',dict(rows=rows,seconds=time.perf_counter()-start,single_policy=pol,static_only=True))
