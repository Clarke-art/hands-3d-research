import sys,json,ast,time
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O));sys.path.insert(0,str(O/'deps'))
from rig_model import *
# Use installed stack consistently; frozen FK itself is unmodified.
from scipy.optimize import minimize
import mink,mujoco
from mink.limits import Limit,Constraint
from mink.tasks import Task
from triangle_distance import distances
P=json.loads((O.parent/'hands_c01_g4_e5_natural_motion_bridge_r2/POLICY_LOCK.json').read_text());P.update(task='PIANO_CONTACT_STATE_MOTION_PLANNER_COMPARISON_R1',static_only=True,max_new_numerical_seconds=600,experiment='P2 and P3, one SLSQP and one Mink run each; no restarts',external_adapter='Mink custom Task/Limit with frozen FK and skin; MuJoCo scalar coordinate carrier only, no surrogate anatomy or native collision claims');(O/'POLICY_LOCK.json').write_text(json.dumps(P,indent=2))
KEYDATA=np.load(O/'DISCRETE_KEY_STATES.npz');STEPS=np.r_[[5.]*3,[10.]*3,[10.]*4,.2,.2];H=np.r_[[.001]*10,[.0001]*2]
class Problem:
 def __init__(self,phase):
  self.phase=phase;self.finger=1 if phase=='P2' else 3;self.note=67 if phase=='P2' else 76;self.index=self.note-21;self.angles=KEYDATA['angles'][1 if phase=='P2' else 2];self.time=float(KEYDATA['times'][1 if phase=='P2' else 2]);self.z0=(ZS if phase=='P2' else ZE).copy();self.low=LOW.copy();self.high=HIGH.copy();self.cache={};self.calls=0
  V=skin(state(self.z0));k=c.KEYS[self.index];loc=keylocal(V,k,self.angles[self.index]);s=k['key_top_playable_surface'][0];patch=np.array(META['pad_patches'][self.finger-1]);inside=(loc[patch,0]>=s['xmin'])&(loc[patch,0]<=s['xmax'])&(loc[patch,1]>=s['ymin'])&(loc[patch,1]<=s['ymax']);vi=patch[inside];assert len(vi);self.witness=int(vi[np.argmin(loc[vi,2])]);self.goal=V[self.witness].copy()
  if phase=='P3':
   self.goal=keyworld(np.array([[loc[self.witness,0],loc[self.witness,1],s['z']-.000005]]),k,self.angles[self.index])[0];self.z0[:3]+=(self.goal-V[self.witness])*1000;V=skin(state(self.z0))
  self.desired=self.z0.copy()
  if phase=='P2':self.desired[0]+=3.;self.desired[11]=.15
  rows=[]
  for note,N,d,blo,bhi in prepkey(self.angles,self.note,self.finger):
   if np.any(V.max(0)<blo-.003) or np.any(V.min(0)>bhi+.003):continue
   signed=V@N.T-d;vv=np.flatnonzero((np.max(signed,1)<.003)&np.all(V>=blo-.004,1)&np.all(V<=bhi+.004,1))
   for v in vv:
    plane=int(np.argmax(signed[v]));rows.append((v,N[plane],d[plane],.20 if note==self.note else .10))
  self.vi=np.array([r[0] for r in rows],int);self.N=np.array([r[1] for r in rows]);self.offset=np.array([r[2] for r in rows]);self.allow=np.array([r[3] for r in rows])
  U=unroot(V,state(self.z0));pairs=[]
  for j in range(5):
   for k0 in range(j+1,5):
    ia=np.flatnonzero(LABEL==j);ib=np.flatnonzero(LABEL==k0);A=U[TR[ia]];B=U[TR[ib]];bl=B.min(1);bh=B.max(1)
    for i,ta in enumerate(ia):
     delta=np.maximum(np.maximum(bl-A[i].max(0),A[i].min(0)-bh),0)
     for b in np.flatnonzero(np.sum(delta**2,1)<.003**2):
      tb=int(ib[b])
      if tb not in META['topological_vertex_neighbors'][int(ta)] and not set(TR[ta])&set(TR[tb]):pairs.append((ta,tb))
  self.pairs=np.array(pairs,int).reshape(-1,2)
  if len(pairs):
   ds,wa,wb=distances(U[TR[self.pairs[:,0]]],U[TR[self.pairs[:,1]]]);assert np.all(ds>1e-10);self.axis=(wa-wb)/ds[:,None]
  self.eqn=4 if phase=='P2' else 3
 def evaluate(self,z):
  key=np.array(z).tobytes()
  if key in self.cache:return self.cache[key]
  self.calls+=1;st=state(z);V=skin(st);eq=list((V[self.witness]-self.goal)*1000)
  if self.phase=='P2':eq.append(z[0]-self.desired[0])
  out=list(np.sum(V[self.vi]*self.N,1)*1000-self.offset*1000+self.allow)
  if len(self.pairs):
   U=unroot(V,st);out.extend((np.min(np.einsum('pvi,pi->pv',U[TR[self.pairs[:,0]]],self.axis),1)-np.max(np.einsum('pvi,pi->pv',U[TR[self.pairs[:,1]]],self.axis),1))*1000-.02)
  k=c.KEYS[self.index];s=k['key_top_playable_surface'][0];q=keylocal(V,k,self.angles[self.index])[int(RAW['pad_indices'][self.finger-1])]*1000
  out.extend([q[0]-s['xmin']*1000,s['xmax']*1000-q[0],q[1]-s['ymin']*1000,s['ymax']*1000-q[1],3-abs(q[2]-s['z']*1000)])
  result=(np.array(eq),np.array(out));self.cache[key]=result;return result
 def jac(self,z,kind):
  cols=[]
  for i,h in enumerate(H):
   a=np.array(z);b=np.array(z);a[i]+=h;b[i]-=h;cols.append((self.evaluate(a)[kind]-self.evaluate(b)[kind])/(2*h))
  return np.array(cols).T
 def violations(self,z):
  e,g=self.evaluate(z);return float(np.max(abs(e))),float(max(0,-g.min(),np.max(self.low-z),np.max(z-self.high)))
class MTask(Task):
 def __init__(self,p,hard=False):self.p=p;self.hard=hard;super().__init__(cost=np.ones(p.eqn if hard else 12),gain=1. if hard else .6)
 def compute_error(self,cfg):return self.p.evaluate(cfg.q)[0] if self.hard else (cfg.q-self.p.desired)*np.r_[[1.]*6,[.1]*4,1.,1.]
 def compute_jacobian(self,cfg):return self.p.jac(cfg.q,0) if self.hard else np.diag(np.r_[[1.]*6,[.1]*4,1.,1.])
class MLimit(Limit):
 def __init__(self,p):self.p=p
 def compute_qp_inequalities(self,cfg,dt):
  z=cfg.q;g=self.p.evaluate(z)[1];J=self.p.jac(z,1);I=np.eye(12);return Constraint(G=np.vstack([-J,I,-I,I,-I]),h=np.r_[g,self.p.high-z,z-self.p.low,STEPS,STEPS])
xml='<mujoco><option gravity="0 0 0"/><worldbody>'+''.join(f'<body name="coordinate_{i}"><joint name="q{i}" type="slide" axis="1 0 0" limited="false"/><geom type="sphere" size="0.001" mass="0.001" contype="0" conaffinity="0"/></body>' for i in range(12))+'</worldbody></mujoco>'
(O/'MINK_COORDINATE_CARRIER.xml').write_text(xml)
model=mujoco.MjModel.from_xml_string(xml);assert model.nq==model.nv==12
# Smoke uses same real-rig custom tasks, but is labelled only interface construction.
smoke=Problem('P2');cfg=mink.Configuration(model,q=smoke.z0);qp=mink.build_ik(cfg,[MTask(smoke)],.01,limits=[MLimit(smoke)],constraints=[MTask(smoke,True)]);assert qp.A.shape==(4,12)
(O/'MINK_SMOKE_TEST.json').write_text(json.dumps(dict(status='TOOL_SMOKE_TESTED',nq=model.nq,equality_shape=list(qp.A.shape),inequality_shape=list(qp.G.shape),carrier_not_anatomical_MJ_model=True,FK='unchanged frozen Rig FK and weighted actual skin from rig_model/skin_proxy',native_MuJoCo_collision_not_used=True),indent=2))
allstart=time.monotonic();runs=[]
for phase in ['P2','P3']:
 for method in ['MINK_DAQP']:
  p=Problem(phase);start=time.monotonic();z=p.z0.copy();history=[];niter=0;success=False;reason='ITERATION_LIMIT';deadline=start+90
  def budget():
   if time.monotonic()>deadline or time.monotonic()-allstart>500:raise TimeoutError('Per run90s / combined500s hard stop')
  try:
   if method=='SLSQP':
    def cons(x,kind):budget();return p.evaluate(x)[kind]
    weights=np.r_[[1.]*6,[.1]*4,1.,1.]
    def obj(x):return float(np.sum(((x-p.desired)*weights)**2)/2)
    def cb(x):
     global z,niter
     z=x.copy();niter+=1;history.append(dict(iteration=niter,violation=p.violations(z)));budget()
    fit=minimize(obj,z,jac=lambda x:(x-p.desired)*weights**2,method='SLSQP',bounds=list(zip(p.low,p.high)),constraints=[dict(type='eq',fun=lambda x:cons(x,0),jac=lambda x:p.jac(x,0)),dict(type='ineq',fun=lambda x:cons(x,1),jac=lambda x:p.jac(x,1))],callback=cb,options=dict(maxiter=50,ftol=1e-8));z=fit.x;success=bool(fit.success);reason=str(fit.message);niter=int(fit.nit)
   else:
    cfg=mink.Configuration(model,q=z)
    for it in range(35):
     budget();v=mink.solve_ik(cfg,[MTask(p)],.01,'daqp',limits=[MLimit(p)],constraints=[MTask(p,True)],safety_break=True);cfg.integrate_inplace(v,.01);z=cfg.q.copy();niter=it+1;e,g=p.violations(z);history.append(dict(iteration=niter,equality_mm=e,inequality_mm=g,step_norm=float(np.linalg.norm(v*.01))))
     if e<1e-5 and g<1e-5 and np.max(abs(v*.01))<.002:success=True;reason='LOCAL_FIXED_POINT_AND_CONSTRAINT_TOLERANCE';break
  except Exception as e:reason=type(e).__name__+': '+str(e)
  result=dict(phase=phase,method=method,display_time=p.time,variables=12,equality_constraints=p.eqn,inequality_constraints=len(p.evaluate(z)[1]),bound_constraints=24,initial_latent=p.z0.tolist(),latent=z.tolist(),state=state(z).tolist(),key_angles=p.angles.tolist(),solver_success=success,termination=reason,iterations=niter,elapsed_seconds=time.monotonic()-start,FK_evaluations=p.calls,violations=p.violations(z),witness_vertex=p.witness,witness_goal_world_m=p.goal.tolist(),history=history,actual_Blender_acceptance='PENDING',no_continuous_motion_claim=True)
  runs.append(result);(O/f'{phase}_{method}_SOLVE.json').write_text(json.dumps(result,indent=2));print('DISCRETE_SOLVE',phase,method,result['elapsed_seconds'],success,reason,result['violations'],flush=True)
(O/'MINK_CORRECTED_RUNS.json').write_text(json.dumps(runs,indent=2));print('TOTAL_NEW_NUMERICAL',sum(r['elapsed_seconds'] for r in runs),flush=True)
