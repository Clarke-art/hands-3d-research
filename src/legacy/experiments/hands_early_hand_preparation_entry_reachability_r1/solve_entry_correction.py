from guarded_node import *
import coupled_model as cm
cm.DynamicNode=GuardedNode
data=json.loads((O/'ENTRY_SOLVE_INPUT.json').read_text(encoding='utf8'));assert not (O/'ENTRY_CORRECTION_RESULT.json').exists()
beg=time.monotonic();p=cm.CoupledProblem(data['contact_sets'],data['initial_latent'],data['moving_keys'],data['time_grid'],(data['joint_domain']['lower'],data['joint_domain']['upper']),data['motion_bounds']);deadline=beg+230
p.lbx=p.lbx.astype(float);p.ubx=p.ubx.astype(float)
p.lbx[:12]=p.x0[:12];p.ubx[:12]=p.x0[:12]
assert np.all(p.lbx<=p.ubx) and np.max(abs(p.ubx[:12]-p.x0[:12]))==0
for nd in p.nodes:nd.deadline=deadline
interface=p.interface();interface.update(anchors=[dict(node=0,time=data['time_grid'][0],state=data['initial_latent'][0],fixed=True)],anchor_policy='Actual B2 is fixed; all later states including event and E5 endpoint adjustable',derivative_guard='In-solver strict central differences at multiple scales with branch detection and fail closed; corrected continuous face-existence proxy',prototype_only=True);save('TIME_COUPLED_ENTRY_CORRECTION_INTERFACE.json',interface)
class Iteration(ca.Callback):
 def __init__(self):
  self.history=[];self.best=None;ca.Callback.__init__(self);self.construct('entry_iteration',{})
 def get_n_in(self):return ca.nlpsol_n_out()
 def get_n_out(self):return 1
 def get_sparsity_in(self,i):return ca.Sparsity.dense({'x':p.X.numel(),'f':1,'g':p.G.numel(),'lam_x':p.X.numel(),'lam_g':p.G.numel(),'lam_p':0}[ca.nlpsol_out(i)],1)
 def get_sparsity_out(self,i):return ca.Sparsity.scalar()
 def eval(self,args):
  x=np.array(args[0]).ravel();g=np.array(args[2]).ravel();v=float(np.maximum(np.maximum(p.lo-g,g-p.hi),0).max());self.history.append(dict(iteration=len(self.history),seconds=time.monotonic()-beg,violation=v))
  if self.best is None or v<self.best[0]:self.best=(v,x.tolist())
  save('ENTRY_CORRECTION_PROGRESS.json',dict(history=self.history,best=self.best));print('ENTRY_ITER',self.history[-1],flush=True)
  return [int(time.monotonic()>deadline or (v<1e-6 and len(self.history)>1))]
cb=Iteration();chosen=p.x0.copy();status='NOT_STARTED';error=None
try:
 solver=ca.nlpsol('entry','ipopt',dict(x=p.X,f=p.objective,g=p.G),dict(iteration_callback=cb,ipopt=dict(max_iter=35,max_wall_time=205.,tol=1e-6,constr_viol_tol=1e-6,acceptable_iter=0,hessian_approximation='limited-memory',print_level=5,linear_solver='mumps',bound_push=1e-6,bound_frac=1e-6)))
 sol=solver(x0=p.x0,lbx=p.lbx,ubx=p.ubx,lbg=p.lo,ubg=p.hi);chosen=np.array(sol['x']).ravel();status=solver.stats()['return_status']
except Exception as e:
 status='FAIL_CLOSED_SOLVER_EXCEPTION';error=str(e)[-2000:]
 if cb.best is not None:chosen=np.array(cb.best[1])
for nd in p.nodes:nd.deadline=float('inf')
v,viol=p.violation(chosen);out=dict(status=status,error=error,scope='FULL_ENTRY_COLLOCATION_CANDIDATE_ONLY',times=data['time_grid'],latents=chosen.reshape(-1,12).tolist(),fixed_start_error=float(np.max(abs(chosen[:12]-p.x0[:12]))),violation=v,row_violations=viol,history=cb.history,elapsed_seconds=time.monotonic()-beg,guards=[nd.guard_calls for nd in p.nodes],stats=[nd.stats for nd in p.nodes],actual_validation='PENDING',primary_trajectory_candidate_count=1,correction_count=1,convergence_not_assumed=True)
save('ENTRY_CORRECTION_RESULT.json',out);print('ENTRY_DONE',status,v,flush=True)
