from guarded_node import *
from scipy.optimize import minimize
cfg=json.loads((O/'EXPERIMENT_CONFIG.json').read_text(encoding='utf8'));probes=json.loads((O/'HOLD_PROBE_REQUESTS.json').read_text(encoding='utf8'))
assert not (O/'HOLD_CONTINUATION_SOLVES.json').exists(),'No repeated continuation batch'
angles=np.load(O/'PREPARATION_KEY_STATES.npz')['angles'][0]; results=[];beg=time.monotonic();overall=beg+175
for req in probes[:3]:
 z0=np.array(req['latent']);node=GuardedNode(z0,req['contacts'],angles,req['display_time'],(LOW,HIGH));node.deadline=min(time.monotonic()+55,overall);best=[float('inf'),z0.copy()];hist=[];scale=np.r_[[20,10,5],[8,8,12],[15]*4,1,1]
 def val(z):
  v=node.value(z);viol=float(max(abs(v[0]),max(0,-v[1:].min())))
  if viol<best[0]:best[:]=[viol,np.array(z).copy()]
  return v
 def jac(z):return node.checked_jac(z)
 def obj(z):return .001*np.sum(((z-z0)/scale)**2)
 def cb(z):
  v=val(z);hist.append(dict(iteration=len(hist),seconds=time.monotonic()-beg,violation=float(max(abs(v[0]),max(0,-v[1:].min())))));print('HOLD',req['id'],hist[-1],flush=True)
 status={}; val(z0)
 try:
  fit=minimize(obj,z0,method='SLSQP',jac=lambda z:.002*(z-z0)/scale**2,bounds=list(zip(LOW,HIGH)),constraints=[dict(type='eq',fun=lambda z:val(z)[:1],jac=lambda z:jac(z)[:1]),dict(type='ineq',fun=lambda z:val(z)[1:],jac=lambda z:jac(z)[1:])],callback=cb,options=dict(maxiter=30,ftol=1e-8));z=fit.x;status=dict(success=bool(fit.success),message=str(fit.message),nit=int(fit.nit))
 except (TimeoutError,ValueError) as e:z=best[1];status=dict(success=False,message=str(e))
 node.deadline=float('inf');v=val(z);violation=float(max(abs(v[0]),max(0,-v[1:].min())));row=dict(req,id=req['id']+'_corrected',latent=z.tolist(),state=state(z).tolist(),status=status,violation=violation,best_violation=best[0],history=hist,guard_calls=node.guard_calls,stats=node.stats)
 results.append(row);save('HOLD_CONTINUATION_SOLVES.json',results);save('HOLD_CORRECTED_REQUESTS.json',[{k:r[k] for k in ['id','display_time','contacts','latent','state']} for r in results]);print('HOLD_DONE',row['id'],status,violation,flush=True)
 if time.monotonic()>=overall:break
