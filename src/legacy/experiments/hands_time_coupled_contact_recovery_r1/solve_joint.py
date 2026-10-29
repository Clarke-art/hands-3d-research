from coupled_model import *
assert not json.loads((O/'POLICY_LOCK.json').read_text())['no_more_solves']
assert json.loads((O/'DERIVATIVE_GUARD_VALIDATION.json').read_text())['status']=='LOCAL_BRANCH_VERIFIED'
assert not (O/'TIME_COUPLED_SOLVE_RESULTS.json').exists(),'Do not repeat main solve'
beg=time.monotonic();p,data=load_problem();deadline=beg+200
for n in p.nodes:n.deadline=deadline
class Iteration(ca.Callback):
 def __init__(self):
  self.history=[];self.best=None;ca.Callback.__init__(self);self.construct('iteration_capture',{})
 def get_n_in(self):return ca.nlpsol_n_out()
 def get_n_out(self):return 1
 def get_sparsity_in(self,i):
  name=ca.nlpsol_out(i);return ca.Sparsity.dense({'x':p.X.numel(),'f':1,'g':p.G.numel(),'lam_x':p.X.numel(),'lam_g':p.G.numel(),'lam_p':0}[name],1)
 def get_sparsity_out(self,i):return ca.Sparsity.scalar()
 def eval(self,args):
  x=np.array(args[0]).ravel();g=np.array(args[2]).ravel();v=float(np.maximum(np.maximum(p.lo-g,g-p.hi),0).max());self.history.append(dict(iteration=len(self.history),seconds=time.monotonic()-beg,max_scaled_violation=v,objective=float(args[1])));
  if self.best is None or v<self.best[0]:self.best=(v,x.tolist())
  print('JOINT_ITER',len(self.history)-1,round(time.monotonic()-beg,3),v,flush=True)
  save('JOINT_PROGRESS.json',dict(history=self.history,best=self.best))
  return [int(time.monotonic()>deadline)]
cb=Iteration();build=time.monotonic();solver=ca.nlpsol('time_coupled','ipopt',dict(x=p.X,f=p.objective,g=p.G),dict(iteration_callback=cb,print_time=True,ipopt=dict(max_iter=60,max_wall_time=170.,tol=1e-6,constr_viol_tol=1e-6,acceptable_iter=0,hessian_approximation='limited-memory',print_level=5,linear_solver='mumps',bound_push=1e-5,bound_frac=1e-5)))
construction=time.monotonic()-build;solve_start=time.monotonic();sol=solver(x0=p.x0,lbx=p.lbx,ubx=p.ubx,lbg=p.lo,ubg=p.hi);elapsed=time.monotonic()-solve_start;stats=solver.stats();x=np.array(sol['x']).ravel();violation,rows=p.violation(x);nodes=[]
for i,(z,r) in enumerate(zip(x.reshape(-1,12),data['nodes'])):
 w,st=KIN(z);node=dict(id='coupled_'+str(i),display_time=r['time'],contacts=r['contacts'],latent=z.tolist(),state=state(z).tolist(),initial_latent=r['initial_latent'],original_latent=r['original_latent'],key_angles=r['key_angles'],wrist_numeric_m=np.array(w).ravel().tolist(),authority='DESIGN_PROVISIONAL');nodes.append(node);save('runs/'+node['id']+'.json',node)
segments=[]
for a,b in zip(nodes,nodes[1:]):
 dt=b['display_time']-a['display_time'];dv=(np.array(b['wrist_numeric_m'])-a['wrist_numeric_m'])*1000;rate=(np.array(b['latent'])-a['latent'])/dt;qr=(np.array(b['state'][6:])-a['state'][6:])/dt;segments.append(dict(dt=dt,wrist_displacement_mm=float(np.linalg.norm(dv)),wrist_speed_mm_s=float(np.linalg.norm(dv)/dt),latent_rates=rate,mapped_joint_rates=qr,wrist_pass=bool(np.linalg.norm(dv)/dt<=500+1e-5),latent_rates_pass=bool(np.all(abs(rate)<=np.array(p.bounds['latent_velocity'])+1e-5)),mapped_rates_pass=bool(np.all(abs(qr)<=240+1e-5))))
result=dict(authority='DESIGN_PROVISIONAL',candidate_count=1,variables=p.X.numel(),constraints=p.G.numel(),jacobian_nonzeros=p.jfun.sparsity_out(0).nnz(),solver_stats=stats,construction_seconds=construction,solver_wall_seconds=elapsed,total_stage_seconds=time.monotonic()-beg,violation=violation,row_violations=rows,nodes=nodes,segments=segments,node_stats=[n.stats for n in p.nodes],switch_logs=[n.switch_log for n in p.nodes],numeric_gate=violation<1e-5,motion_numeric_pass=all(s['wrist_pass'] and s['latent_rates_pass'] and s['mapped_rates_pass'] for s in segments),actual_geometry='PENDING_INDEPENDENT_BLENDER',history=cb.history,best=cb.best)
save('TIME_COUPLED_SOLVE_RESULTS.json',result);print('SOLVE_FINISHED',stats['return_status'],violation,elapsed,flush=True)
