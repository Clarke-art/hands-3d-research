from bridge_model import *
import traceback
pid=sys.argv[-1];plan=next(p for p in json.loads((O/'R2_PLANS.json').read_text(encoding='utf8')) if p['candidate_id']==pid);assert not (O/(pid+'_RESULT.json')).exists(),'No repeated candidate';beg=time.monotonic();deadline=beg+195
Z0=np.array(CTX['known_start']['latent']);ref=np.array(CTX['reference_common']['latent']);raised=ref.copy();raised[11]=0.;ready=plan['reference_time_allocation']['ready'];event=CTX['time_span']['junction'];end=CTX['time_span']['first_full_press'];initial=[]
# Stable material-face bank warm start only; all non-start states are jointly adjustable.
for t in plan['time_grid']:
 if t<=ready:
  f=(t-plan['time_grid'][0])/(ready-plan['time_grid'][0]);z=(1-f)*Z0+f*raised
 elif t<=event:
  f=(t-ready)/(event-ready);z=(1-f)*raised+f*ref
 else:
  f=(t-event)/(end-event);z=ref.copy();V=skin(state(ref));thumb=plan['held_contact']['finger'];k=c.KEYS[plan['held_contact']['midi']-21];radius=max(float(p[1]-k['key_top_playable_surface'][0]['ymin']) for p in V[np.array(META['pad_patches'][thumb-1])]);z[1]-=f*(max(radius,0)+.0005)*1000;z[11]+=f*(1-z[11])
 ct=plan['held_contact'] if t<event else plan['target_contact']
 if t!=plan['time_grid'][0]:z=contact_transport(z,ct,t)
 z=np.clip(z,LOW,HIGH);initial.append(z.tolist())
initial[0]=CTX['known_start']['latent'];save(pid+'_INITIALIZATION.json',dict(method='Existing common material-face bank warm start plus source Action transport; not a fixed state or an accepted path',states=initial,all_non_start_states_adjustable=True,source_common_pose_sha256=__import__('hashlib').sha256(json.dumps(CTX['reference_common'],sort_keys=True).encode()).hexdigest(),preferred_subset_comes_from_high_level=plan['target_subset']))
p=None;result=dict(candidate_id=pid,status='NOT_EXECUTED',solver_called=False,authority='DESIGN_PROVISIONAL — STOP — HUMAN REVIEW',initial=initial,latents=initial,times=plan['time_grid'],history=[],error=None)
class Iteration(ca.Callback):
 def __init__(self,p):
  self.p=p;self.history=[];self.best=None;ca.Callback.__init__(self);self.construct('r2_iteration_'+pid,{})
 def get_n_in(self):return ca.nlpsol_n_out()
 def get_n_out(self):return 1
 def get_sparsity_in(self,i):return ca.Sparsity.dense({'x':self.p.X.numel(),'f':1,'g':self.p.G.numel(),'lam_x':self.p.X.numel(),'lam_g':self.p.G.numel(),'lam_p':0}[ca.nlpsol_out(i)],1)
 def get_sparsity_out(self,i):return ca.Sparsity.scalar()
 def eval(self,args):
  x=np.array(args[0]).ravel();g=np.array(args[2]).ravel();v=float(np.maximum(np.maximum(self.p.lo-g,g-self.p.hi),0).max());self.history.append(dict(iteration=len(self.history),seconds=time.monotonic()-beg,violation=v))
  if self.best is None or v<self.best[0]:self.best=(v,x.tolist())
  save(pid+'_PROGRESS.json',dict(history=self.history,best=self.best));print(pid,'ITER',self.history[-1],flush=True)
  stagnation=len(self.history)>=5 and self.history[-1]['violation']>.999*self.history[-5]['violation']
  return [int(time.monotonic()>deadline or stagnation or (v<1e-6 and len(self.history)>1))]
try:
 p=BridgeProblem(plan,initial)
 for n in p.nodes:n.deadline=deadline
 cb=Iteration(p);result['solver_called']=True;result['interface']=dict(variables=p.X.numel(),constraints=p.G.numel(),jacobian_nonzeros=p.jfun.sparsity_out(0).nnz(),geometric_collocation_times=[r['time'] for r in p.samples],motion_collocation='5 points/segment, exact pruned FK motion AD',curve='C1 cubic Hermite, central secant tangents; only B2 fixed',physical_thresholds_unchanged=True,redundant_clipped_witness_xy_rows_removed=True,remaining_contact_geometry='Actual clipped-face minimum, crossing existence, original pad bounds/height, full key pieces and self separation proxies')
 solver=ca.nlpsol('r2_'+pid,'ipopt',dict(x=p.X,f=p.f,g=p.G),dict(iteration_callback=cb,print_time=True,ipopt=dict(max_iter=24,max_wall_time=max(10.,deadline-time.monotonic()-15),tol=1e-6,constr_viol_tol=1e-6,acceptable_iter=0,hessian_approximation='limited-memory',print_level=5,linear_solver='mumps',bound_push=1e-6,bound_frac=1e-6)))
 sol=solver(x0=p.x0,lbx=p.lbx,ubx=p.ubx,lbg=p.lo,ubg=p.hi);x=np.array(sol['x']).ravel();result['status']=solver.stats()['return_status'];result['latents']=x.reshape(-1,12).tolist();result['history']=cb.history
 for n in p.nodes:n.deadline=float('inf')
 result['violation'],result['row_violations']=p.violation(x)
except Exception as e:
 result['status']='FAIL_CLOSED_INTERFACE_OR_DERIVATIVE';result['error']=str(e)[-3000:];result['traceback']=traceback.format_exc()[-6000:]
 if p is not None:
  for n in p.nodes:n.deadline=float('inf')
  if 'cb' in globals() and cb.best is not None:result['latents']=np.array(cb.best[1]).reshape(-1,12).tolist();result['history']=cb.history
  try:result['violation'],result['row_violations']=p.violation(np.array(result['latents']).ravel())
  except Exception as ee:result['verification_error']=str(ee)
finally:
 result['elapsed_seconds']=time.monotonic()-beg;result['fixed_start_error']=float(np.max(abs(np.array(result['latents'][0])-Z0)))
 if p is not None:result['guards']=[n.guard_calls for n in p.nodes];result['stats']=[n.stats for n in p.nodes];result['corridor_switches']=[n.corridor_switches for n in p.nodes]
 result['actual_Blender_validation']='PENDING';save(pid+'_RESULT.json',result);print(pid,'DONE',result['status'],result.get('violation'),flush=True)
