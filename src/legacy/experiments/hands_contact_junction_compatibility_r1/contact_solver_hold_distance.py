import sys,json,ast,time
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O))
from rig_model import *
from triangle_distance import distances
from scipy.optimize import minimize
I=json.loads((O/'EXPERIMENT_INPUT.json').read_text());POL=json.loads((O/'POLICY_LOCK.json').read_text());H=np.r_[[.001]*10,[.0001]*2]
# Generic geometric contact descriptor, independent of note name/event ID.
class ContactProblem:
 def __init__(self,z0,contacts,angles,trust=None):
  self.z0=np.array(z0);self.contacts=contacts;self.angles=np.array(angles);self.trust=trust;self.cache={};self.calls=0;self.pieces=prepkey(self.angles,contacts[0]['midi'],contacts[0]['finger']);self.planes=[np.c_[N,d] for note,N,d,lo,hi in self.pieces];self.pairs=[];self.axes=[]
  U=unroot(skin(state(self.z0)),state(self.z0))
  for j in range(5):
   for k in range(j+1,5):
    ia=np.flatnonzero(LABEL==j);ib=np.flatnonzero(LABEL==k);A=U[TR[ia]];B=U[TR[ib]];bl=B.min(1);bh=B.max(1)
    for ai,ta in enumerate(ia):
     delta=np.maximum(np.maximum(bl-A[ai].max(0),A[ai].min(0)-bh),0)
     for bi in np.flatnonzero(np.sum(delta**2,1)<=.003**2):
      tb=int(ib[bi])
      if tb not in META['topological_vertex_neighbors'][int(ta)] and not set(TR[ta])&set(TR[tb]):self.pairs.append((int(ta),tb))
  self.pairs=np.array(self.pairs,int).reshape(-1,2)
  if len(self.pairs):
   dd,wa,wb=distances(U[TR[self.pairs[:,0]]],U[TR[self.pairs[:,1]]]);assert np.all(dd>1e-10);self.axes=(wa-wb)/dd[:,None]
 def evaluate(self,z):
  key=np.array(z).tobytes()
  if key in self.cache:return self.cache[key]
  self.calls+=1;st=state(z);V=skin(st);eq=[];g=[];names=[]
  for ci,ct in enumerate(self.contacts):
   k=c.KEYS[ct['midi']-21];s=k['key_top_playable_surface'][0];loc=keylocal(V,k,self.angles[ct['midi']-21]);point=np.array(ct['barycentric'])@loc[np.array(ct['vertices'])];pad=loc[int(RAW['pad_indices'][ct['finger']-1])]
   eq.append((point[2]-s['z'])*1000+.005)
   g.extend([(point[0]-s['xmin'])*1000-.001,(s['xmax']-point[0])*1000-.001,(point[1]-s['ymin'])*1000-.001,(s['ymax']-point[1])*1000-.001,(pad[0]-s['xmin'])*1000-.01,(s['xmax']-pad[0])*1000-.01,(pad[1]-s['ymin'])*1000-.01,(s['ymax']-pad[1])*1000-.01,3-abs(pad[2]-s['z'])*1000]);names.extend([f'contact_{ci}_{s}' for s in ['witness_xmin','witness_xmax','witness_ymin','witness_ymax','pad_xmin','pad_xmax','pad_ymin','pad_ymax','pad_height']])
  TV=V[TR];tl=TV.min(1);th=TV.max(1)
  for pi,(note,N,d,lo,hi) in enumerate(self.pieces):
   ti=np.flatnonzero(np.all(th>=lo-1e-8,1)&np.all(tl<=hi+1e-8,1))
   if len(ti):
    sig=np.einsum('tvi,ni->tvn',TV[ti],N)-d;ti=ti[np.all(np.min(sig,axis=1)<=1e-8,axis=1)]
   peak=max([triangle_inside_depth(TV[t],self.planes[pi])[0] for t in ti]+[0.]);g.append(.20-peak);names.append('key_'+str(note)+'_piece_'+str(pi))
  if len(self.pairs):
   U=unroot(V,st);sep=(np.min(np.einsum('pvi,pi->pv',U[TR[self.pairs[:,0]]],self.axes),1)-np.max(np.einsum('pvi,pi->pv',U[TR[self.pairs[:,1]]],self.axes),1))*1000-.02;g.extend(sep);names.extend(['self_pair_'+str(i) for i in range(len(sep))])
  if self.trust is not None:
   V0=skin(state(self.z0))
   for ci,ct in enumerate(self.contacts):
    kk=c.KEYS[ct['midi']-21];aa=self.angles[ct['midi']-21];pp=keylocal(np.array([np.array(ct['barycentric'])@V[np.array(ct['vertices'])]]),kk,aa)[0];p0=keylocal(np.array([np.array(ct['barycentric'])@V0[np.array(ct['vertices'])]]),kk,aa)[0];g.append(3.-float(np.linalg.norm(pp[:2]-p0[:2])*1000));names.append('controlled_tangential_step_'+str(ci))
   g.extend(self.trust-(z-self.z0));g.extend(self.trust+(z-self.z0));names.extend(['trust_hi_'+str(i) for i in range(12)]+['trust_lo_'+str(i) for i in range(12)])
  out=(np.array(eq),np.array(g),names)
  if len(self.cache)>60:self.cache.clear()
  self.cache[key]=out;return out
 def jac(self,z,which,budget):
  cols=[]
  for i,h in enumerate(H):
   budget();a=z.copy();b=z.copy();a[i]+=h;b[i]-=h;cols.append((self.evaluate(a)[which]-self.evaluate(b)[which])/(2*h))
  return np.array(cols).T

def run_solve(run_id,z0,contacts,display_time,angles,seconds,goal=None,trust=None):
 assert not (O/'runs'/(run_id+'.json')).exists(),'No repeated solve ID'
 clock=time.monotonic();deadline=clock+seconds;p=ContactProblem(z0,contacts,angles,trust);z0=np.clip(np.array(z0),LOW,HIGH);best=[float('inf'),z0.copy()];iterations=0;history=[]
 def budget():
  if time.monotonic()>deadline:raise TimeoutError('Per-experiment fixed wall budget')
 def track(z):
  e,g,n=p.evaluate(z);v=float(max(np.max(abs(e)),max(0,-g.min())))
  if v<best[0]:best[:]=[v,z.copy()]
  return e,g,n,v
 def fun(z,which):budget();return track(z)[which]
 scale=np.r_[[30,20,10],[8,8,12],[15]*4,1,1]
 def objective(z):
  reg=.0001*np.sum(((z-z0)/scale)**2)
  if goal is None:return float(reg)
  V=skin(state(z));pad=V[int(RAW['pad_indices'][goal['finger']-1])];k=c.KEYS[goal['midi']-21];loc=keylocal(np.array([pad]),k,angles[goal['midi']-21])[0];dist=min(np.sum((loc-np.array([np.clip(loc[0],s['xmin'],s['xmax']),np.clip(loc[1],s['ymin'],s['ymax']),s['z']]))**2) for s in k['key_top_playable_surface']);return float(dist*1e6+reg)
 def cb(z):
  nonlocal iterations
  iterations+=1;budget();e,g,n,v=track(z);history.append(dict(iteration=iterations,elapsed=time.monotonic()-clock,violation_mm=v));print(run_id,iterations,round(time.monotonic()-clock,3),round(v,6),flush=True)
 initial=track(z0)[3];conv={}
 try:
  fit=minimize(objective,z0,method='SLSQP',bounds=list(zip(LOW,HIGH)),constraints=[dict(type='eq',fun=lambda z:fun(z,0),jac=lambda z:p.jac(z,0,budget)),dict(type='ineq',fun=lambda z:fun(z,1),jac=lambda z:p.jac(z,1,budget))],callback=cb,options=dict(maxiter=60,ftol=1e-8,eps=.001));chosen=fit.x;conv=dict(success=bool(fit.success),status=int(fit.status),message=str(fit.message),nit=int(fit.nit),nfev=int(fit.nfev),njev=int(fit.njev))
 except TimeoutError as e:chosen=best[1];conv=dict(success=False,status='WALL_BUDGET_STOP',message=str(e),nit=iterations,nfev=None,njev=None)
 e,g,n,v=track(chosen);worst=[dict(name=n[i],margin_mm=float(g[i])) for i in np.argsort(g)[:8]]
 out=dict(id=run_id,display_time=display_time,contacts=contacts,latent=chosen.tolist(),state=state(chosen).tolist(),initial_latent=z0.tolist(),key_angles=np.array(angles).tolist(),convergence=conv,elapsed_seconds=time.monotonic()-clock,budget_seconds=seconds,variables=12,equalities=len(e),inequalities=len(g),bounds=24,FK_evaluations=p.calls,initial_violation_mm=initial,final_violation_mm=v,normal_contact_errors_mm=e.tolist(),worst_inequalities=worst,history=history,objective='feasibility then tiny deviation cost' if goal is None else 'distance of free preparing pad to target playable surface, not hard hover position',trust_box=trust.tolist() if trust is not None else None,goal=goal,scope='NUMERICAL_CANDIDATE_REQUIRES_BLENDER',authority='DESIGN_PROVISIONAL',geometry_method='Full candidate-filtered triangle internal depth per convex key piece; fixed near self-face separating axes; material face normal contact with tangential key-region bounds')
 (O/'runs'/(run_id+'.json')).write_text(json.dumps(out,indent=2)+'\n');print('SOLVE_END',run_id,out['elapsed_seconds'],conv,'violation',v,flush=True);return out
if __name__=='__main__':
 attempt=int(sys.argv[-1]);assert attempt in [1,2];assert json.loads((O/'BOUNDARY_SOURCE_VERIFICATION.json').read_text())['status']=='BOUNDARY_CONTRACT_PASS';data=np.load(O/'BOUNDARY_KEY_STATES.npz');angles=data['angles'][3];seed=I['seeds']['P2']['latent'] if attempt==1 else json.loads((O/'runs/junction_1.json').read_text())['latent'];run_solve('junction_'+str(attempt),seed,I['contacts'],I['junction_time'],angles,100)
