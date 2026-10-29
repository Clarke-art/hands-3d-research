from coordination import *
import time
assert not (P/'FORMAL_SOLVE_ATTEMPT.json').exists()
check=Context(D['times'][::20]);actual=D['actual_skin'][::20]
err=float(np.linalg.norm(check.original-actual,axis=-1).max()*1000)
dump('NUMERICAL_SKIN_PARITY.json',dict(max_mm=err,samples=len(check.t),method='Original saved quaternions + frozen FK + actual weighted skin, no geometry proxy for black keys'))
assert err<.03,err
times=[0.,.433333333,1.133333333,1.4214275,1.8,2.6,3.4,3.825,4.,4.05,4.683333333,4.916666667,5.933333333]
rows=[];started=time.monotonic()
for t in times:
    context=Context([t]);lo,hi=bounds([t]);fit=least_squares(lambda x:context.residual(x).ravel(),np.zeros(12),bounds=(lo.ravel()+1e-6,hi.ravel()-1e-6),max_nfev=160,ftol=1e-7,xtol=1e-7,gtol=1e-7,diff_step=1e-4)
    delta=fit.x.reshape(1,3,4);V=context.skin(delta);black,sdf=context.black_clearance(V);pair=context.pair_clearance(V);contacts=context.contacts(V)[1]
    row=dict(video_sec=t,music_sec=t-.35,delta_deg=delta[0],actual_degrees=original_degrees([t])[0]+delta[0],success=bool(fit.success),nfev=fit.nfev,cost=float(fit.cost),message=fit.message,max_black_constraint_residual_mm=float(black.max()),max_pair_constraint_residual_mm=float(pair.max()),contacts=contacts)
    rows.append(row);dump('STATIC_PREFLIGHT.json',dict(kind='ONE_FINITE_STATIC_PREFLIGHT_BATCH_NOT_DYNAMIC',root_locked=True,poses=rows,dynamic_candidates=0,formal_solve_attempts=0,elapsed_sec=time.monotonic()-started,complete=len(rows)==len(times)))
    print('STATIC',t,'black',round(float(black.max()),3),'pair',round(float(pair.max()),3),'contact',contacts,'delta',delta.round(2).tolist(),'nfev',fit.nfev,flush=True)
print('FINITE_STATIC_BATCH_FINISHED',flush=True)
