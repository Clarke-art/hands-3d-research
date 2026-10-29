import os,sys,time,json,math,subprocess,traceback
from pathlib import Path
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1';sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;P=O.parent/'hands_contact_constrained_trajectory_planning_r1';sys.path.insert(0,str(O));sys.path.insert(0,str(P/'deps'))
T=time.monotonic();DEADLINE=T+540
def check():
 if time.monotonic()>DEADLINE:raise TimeoutError('GLOBAL_NUMERICAL_DEADLINE')
def save(n,x): (O/n).write_text(json.dumps(x,indent=2,default=lambda x:x.tolist() if hasattr(x,'tolist') else str(x)))
import casadi as ca
from rig_model import *
from contact_solver import ContactProblem
from scipy.optimize import minimize
I=json.loads((O/'EXPERIMENT_INPUT.json').read_text());chart=json.loads((P/'ACTIVE_GEOMETRY_CHART.json').read_text());B=json.loads((P/'TRAJECTORY_BENCHMARK_INPUT.json').read_text());F=ca.Function.load(str(P/'FROZEN_SKIN_SYMBOLIC.casadi'))
V0=skin(state(np.array(B['Start']['local']['latent'])))
selfrows=[r for r in chart['self_chart'] if (V0[TR[r['a']]]@r['axis']).min()-(V0[TR[r['b']]]@r['axis']).max()<.0035]
class ContactDerivative:
 """RigState + ContactSet + MovingKeyGeometry + EventTime + JointDomain.
 Frozen material triangle witnesses are local charts, not global contact proof.
 Re-detect full pulp faces and full collisions at acceptance.
 """
 def __init__(self,contacts,angles,event_time,domain):
  self.contacts=contacts;self.angles=angles;self.event_time=event_time;self.domain=domain
  v=ca.MX.sym('vertices',3,len(W));g=[];lo=[];hi=[]
  def add(x,l,h):
   x=ca.vec(x);g.append(x);lo.extend(np.broadcast_to(l,(x.numel(),)));hi.extend(np.broadcast_to(h,(x.numel(),)))
  def loc(points,midi):
   k=c.KEYS[midi-21];pv=ca.DM(k['press_pivot']);return ca.DM(c.axisrot(-angles[midi-21],k['press_axis']))@(points-ca.repmat(pv,1,points.size2()))+ca.repmat(pv,1,points.size2())
  for ct in contacts:
   s=c.KEYS[ct['midi']-21]['key_top_playable_surface'][0];pt=loc(v[:,ct['vertices']]@ca.DM(ct['barycentric']),ct['midi']);pad=loc(v[:,int(RAW['pad_indices'][ct['finger']-1])],ct['midi'])
   add((pt[2]-s['z'])*1000+.005,-.0005,.0005)
   for p,m in [(pt,.001),(pad,.01)]:add(ca.vertcat(p[0]-s['xmin'],s['xmax']-p[0],p[1]-s['ymin'],s['ymax']-p[1])*1000,m,np.inf)
   add((pad[2]-s['z'])*1000,-3,3)
  for r in chart['key_chart']:add((r['offset_key_local']-ca.DM(r['normal_key_local']).T@loc(v[:,r['vertices']],r['midi']))*1000,-np.inf,.20)
  for r in selfrows:
   a=ca.DM(r['axis']);add((ca.mmin(a.T@v[:,TR[r['a']].tolist()])-ca.mmax(a.T@v[:,TR[r['b']].tolist()]))*1000,.02,np.inf)
  gg=ca.vertcat(*g);self.geo=ca.Function('geometry',[v],[gg]);self.geo_j=ca.Function('geometry_j',[v],[ca.jacobian(gg,ca.vec(v))]);self.lo=np.array(lo);self.hi=np.array(hi);z=ca.MX.sym('z',12);vv=F(z)[0]
  self.fun=ca.Function('node',[z],[self.geo(vv)])
  # Chain rule at the node boundary: full skin differentiated only once per state.
  self.skin_j=ca.Function('skin_j',[z],[ca.jacobian(ca.vec(vv),z)],{'ad_weight':0})
  self.old=ca.Function('old_node',[z],[self.geo(F.expand()(z)[0])]);self.old_j=ca.Function('old_j',[z],[ca.jacobian(self.old(z),z)])
  self.cache=None;self.calls={'skin':0,'skin_jacobian':0,'geometry':0,'geometry_jacobian':0,'active_detection':0}
 def value_jac(self,z):
  check();key=np.asarray(z).tobytes()
  if self.cache is not None and self.cache[0]==key:return self.cache[1:]
  v=F(z)[0];j=self.skin_j(z);g=np.array(self.geo(v)).ravel();jac=np.array(ca.mtimes(self.geo_j(v),j));self.calls['skin']+=1;self.calls['skin_jacobian']+=1;self.calls['geometry']+=1;self.calls['geometry_jacobian']+=1
  self.cache=(key,g,jac);return g,jac
 def redetect(self,z):
  self.calls['active_detection']+=1;v=np.array(F(z)[0]).T
  return [contact_metric(v,c.KEYS[ct['midi']-21],self.angles[ct['midi']-21],ct['finger']) for ct in self.contacts]
def bench(name,z,cts,angles,t):
 check();beg=time.monotonic();p=ContactDerivative(cts,angles,t,(LOW,HIGH));build=time.monotonic()-beg
 def timed(fn):
  out=[]
  for _ in range(3):check();tt=time.perf_counter();val=fn();out.append(time.perf_counter()-tt)
  return val,out
 old,ot=timed(lambda:np.array(p.old_j(z)))
 def fresh():p.cache=None;return p.value_jac(z)[1]
 new,nt=timed(fresh);checks=[]
 for h in [1e-2,1e-3,1e-4]:
  steps=np.r_[[h]*10,[h*.1]*2];cols=[]
  for j,hh in enumerate(steps):
   check();d=np.eye(12)[j]*hh;cols.append((np.array(p.fun(z+d)).ravel()-np.array(p.fun(z-d)).ravel())/(2*hh))
  fd=np.array(cols).T;err=abs(fd-new);checks.append(dict(step=steps,max_abs_error=float(err.max()),relative_frobenius=float(np.linalg.norm(fd-new)/max(np.linalg.norm(fd),1e-12)),per_variable_max_abs=err.max(0),missing_nonzeros=int(np.sum((abs(new)<1e-12)&(abs(fd)>1e-5)))))
 memory=__import__('ctypes').windll.kernel32.GetCurrentProcessId() # PID recorded; RSS via Windows query below
 row=dict(id=name,event_time=t,build_seconds=build,old_seconds=ot,new_seconds=nt,speedup=float(np.median(ot)/np.median(nt)),shape=list(new.shape),numeric_nonzeros=int(np.sum(abs(new)>1e-12)),old_structural_nonzeros=p.old_j.sparsity_out(0).nnz(),old_new_max_abs=float(abs(old-new).max()),checks=checks,calls=p.calls,old_method='Original expanded-SX skin automatic differentiation, same local constraint rows; excludes trajectory kinematic rows',new_method='Node-local chain rule MX skin Jacobian times sparse geometry Jacobian',active_contacts=p.redetect(z),pid=memory)
 print('BENCH',name,'speedup',row['speedup'],'error',checks[-1]['max_abs_error'],flush=True);return row,p
def main():
 phase=time.monotonic();data=np.load(O/'BOUNDARY_KEY_STATES.npz');joint=json.loads((O.parent/'hands_contact_junction_compatibility_r1/runs/junction_2.json').read_text());E=json.loads((O/'ENDPOINT_SOLVE_2.json').read_text());traj=json.loads((P/'LOCAL_CONTROL_TRAJECTORY.json').read_text());actual=json.loads((P/'LOCAL_PATH_ACTUAL_SAMPLES.json').read_text());save('ACTUAL_STRUCTURE.json',{'type':str(type(actual)),'keys':list(actual)[:15] if isinstance(actual,dict) else list(actual[0])})
 rows=[];configs=[('J1',np.array(I['seeds']['P2']['latent']),[I['contacts'][0]],data['angles'][1],2.72),('J2',ZE,[I['contacts'][1]],data['angles'][-1],E['source_time']),('J3',np.array(joint['latent']),I['contacts'],data['angles'][3],I['junction_time'])]
 for args in configs:
  row,p=bench(*args);rows.append(row);save('JACOBIAN_PERFORMANCE_COMPARISON.json',rows)
 # Use exact recorded moving-key states and original failed controls.
 ar=actual.get('results',actual.get('samples',[])) if isinstance(actual,dict) else actual
 print('ACTUAL_ROWS',len(ar),list(ar[0]) if ar else '',flush=True)
 fail=next(r for r in reversed(ar) if r.get('id','').startswith('candidate') and not r.get('all_gates',True))
 sample=next(s for s in traj['samples'] if s['id']==fail['id']);z=np.array(sample['latent']);angles=np.array(fail['key_angles']);save('RECOVERY_INPUT.json',dict(sample=sample,actual=fail))
 row,p=bench('J4_node',z,sample['contacts'],angles,sample['display_time']);rows.append(row);save('JACOBIAN_PERFORMANCE_COMPARISON.json',rows)
 valid=rows[-1]['checks'][-1]['max_abs_error']<1e-3 and rows[-1]['old_new_max_abs']<1e-6 and rows[-1]['checks'][-1]['missing_nonzeros']==0
 save('DERIVATIVE_VALIDATION.json',dict(fixed_material_chart_verified=valid,whole_active_surface_derivative='NON_SMOOTH_OR_UNVERIFIED',rows=rows,scope='Fixed face barycentric chart and frozen collision certificates; actual pulp re-detected separately'))
 if not valid:save('CONTACT_FEASIBILITY_RECOVERY.json',dict(status='FEASIBILITY_RECOVERY_BLOCKED',reason='derivative gate failed'));return
 # One deterministic feasibility solve, initialized exactly at original failed state.
 start=time.monotonic();deadline=min(DEADLINE,start+110);history=[];z0=z.copy();scale=np.r_[[30,20,10],[8,8,12],[15]*4,1,1]
 def ev(z):
  if time.monotonic()>deadline:raise TimeoutError('single recovery budget')
  return p.value_jac(z)
 def g(z):
  a,j=ev(z);return np.r_[(a-p.lo)[np.isfinite(p.lo)],(p.hi-a)[np.isfinite(p.hi)]]
 def jac(z):
  a,j=ev(z);return np.vstack([j[np.isfinite(p.lo)],-j[np.isfinite(p.hi)]])
 def cb(z):history.append(dict(seconds=time.monotonic()-start,violation=max(0,float(-g(z).min()))));print('RECOVERY',len(history),history[-1],flush=True)
 fit=minimize(lambda z:1e-4*np.sum(((z-z0)/scale)**2),z, jac=lambda z:2e-4*(z-z0)/scale**2,bounds=list(zip(LOW,HIGH)),method='SLSQP',constraints=[dict(type='ineq',fun=g,jac=jac)],callback=cb,options=dict(maxiter=50,ftol=1e-10))
 out=dict(id='recovery_1',display_time=sample['display_time'],contacts=sample['contacts'],latent=fit.x.tolist(),state=state(fit.x).tolist(),initial_latent=z0.tolist(),convergence=dict(success=bool(fit.success),message=fit.message,nit=fit.nit),elapsed_seconds=time.monotonic()-start,history=history,constraint_violation=max(0,float(-g(fit.x).min())),active_contact_before=p.redetect(z0),active_contact_after=p.redetect(fit.x),calls=p.calls,authority='DESIGN_PROVISIONAL')
 save('runs/recovery_1.json',out);save('CONTACT_FEASIBILITY_RECOVERY.json',dict(status='NUMERICAL_CANDIDATE_REQUIRES_BLENDER',result=out))
 check()
 with (O/'logs/recovery_actual.log').open('w') as log:subprocess.run([r'D:\blender\blender.exe','-b','-t','4','--python',str(O/'blender_verify.py'),'--',str(O/'runs/recovery_1.json')],stdout=log,stderr=subprocess.STDOUT,timeout=min(80,max(1,DEADLINE-time.monotonic())),check=True)
 ac=json.loads((O/'runs/recovery_1_actual.json').read_text());save('CONTACT_FEASIBILITY_RECOVERY.json',dict(status='CONTACT_FEASIBILITY_RECOVERED' if ac['all_gates'] else 'FEASIBILITY_RECOVERY_BLOCKED',result=out,actual=ac))
if __name__=='__main__':
 try:main()
 except Exception as e:save('EXECUTION_ERROR.json',dict(error=str(e),traceback=traceback.format_exc()));traceback.print_exc()
 finally:save('RUN_BUDGET.json',dict(charged_seconds=time.monotonic()-T,limit_seconds=600,process_deadline_seconds=540,includes='imports, construction, probes, solver, independent Blender',authority='DESIGN_PROVISIONAL'))
