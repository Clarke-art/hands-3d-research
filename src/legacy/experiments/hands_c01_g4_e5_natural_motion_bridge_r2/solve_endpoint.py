import sys,json,time,ast,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O))
from skin_proxy import *
from triangle_distance import distances
from scipy.optimize import minimize
from itertools import combinations
P=json.loads((O/'POLICY_LOCK.json').read_text(encoding='utf-8-sig'));PRE=O.parent/'hands_c01_anatomy_preparation_audit_r1'
REF=json.loads((PRE/'ANATOMY_CONSTRAINT_PROPOSAL.json').read_text(encoding='utf-8-sig'))
Q0=np.array([r['approved_reference_controls_deg'][0] for r in REF['constraints']]);Q1=np.array([r['approved_reference_controls_deg'][1] for r in REF['constraints']])
TR=RAW['triangles'];LABEL=np.array(META['triangle_labels']);D=RAW;rot=c.axisrot
source=(O/'geometry_detector.py').read_text(encoding='utf-8-sig');tree=ast.parse(source)
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['clip','area','keylocal','keyworld','contact_metric','triangle_inside_depth']],type_ignores=[]),'frozen_geometry_functions','exec'))
node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='triangle_inside_depth')
exec(compile(ast.get_source_segment(source,node).replace('def triangle_inside_depth','def signed_triangle_depth').replace('&(x[:,2]>=-1e-8)','').replace('max(float(best[2])*1000,0.)','float(best[2])*1000'),'signed_LP','exec'))
tree=ast.parse((O.parent/'hands_skin_collision_static_feasibility_r1/solve_static_skin.py').read_text(encoding='utf-8-sig'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='prepkey'],type_ignores=[]),'frozen_key_planes','exec'))
ai=int(sys.argv[-1]);assert ai in [1,2];assert not (O/f'ENDPOINT_SOLVE_{ai}.json').exists()
B=json.loads((PRE/'B_SOLVE_2.json').read_text());startstate=np.array(B['state']);angles=np.load(O/'ENDPOINT_KEY_ANGLES.npz')['angles'];target=76;finger=3
if ai==2:assert json.loads((O/'ENDPOINT_ACTUAL_1.json').read_text())['status']!='ENDPOINT_GATES_PASS'
ACTIVE_FLEX=np.array(next(d for d in json.loads((O/'PREFLIGHT_AND_ENDPOINT_DIAGNOSIS.json').read_text())['old_S2']['actual_anatomy']['digits'] if d['digit']=='MIDDLE')['controls_recovered_deg'][:3])
assert np.all(ACTIVE_FLEX<=[32,32,20]) and np.all(ACTIVE_FLEX>=0)
seed=startstate.copy();lam=0.
if ai==2:seed[:6]=np.array(json.loads((O/'PREFLIGHT_AND_ENDPOINT_DIAGNOSIS.json').read_text())['old_S2']['state'])[:6];seed[6:]=Q1.ravel();seed[14:17]=ACTIVE_FLEX;lam=1.
# Initialisation only: retarget approved posture pad to actual depressed E5.
V=skin(seed);ek=c.KEYS[55];surf=ek['key_top_playable_surface'][0];goal=keyworld(np.array([[ek['key_center'][0],.035,surf['z']+.001]]),ek,angles[55])[0]
seed[:3]+=(goal-V[int(RAW['pad_indices'][2])])*1000
loZ=-12.217247311392744
low=np.r_[[-150,-30,loZ],[-8,-8,-12],[0,0,0,-35],0.]
high=np.r_[[60,35,12],[8,8,12],[25,25,18,35],1.]
def state(x):
 st=np.zeros(26);st[:6]=x[:6];st[6:10]=x[6:10];st[10:]=((1-x[10])*Q0[1:]+x[10]*Q1[1:]).ravel()
 if ai==2:st[14:17]=(1-x[11])*st[14:17]+x[11]*ACTIVE_FLEX
 return st
if ai==2:low=np.r_[low,0.];high=np.r_[high,1.]
x0=np.r_[seed[:6],seed[6:10],lam];
if ai==2:x0=np.r_[x0,1.]
x0=np.clip(x0,low+1e-9,high-1e-9)
clockstart=time.monotonic();already=sum(json.loads((O/f'ENDPOINT_SOLVE_{i}.json').read_text())['elapsed_seconds'] for i in [1] if (O/f'ENDPOINT_SOLVE_{i}.json').exists());deadline=clockstart+min(140,600-already)
class BudgetStop(Exception):pass
def budget():
 if time.monotonic()>deadline:raise BudgetStop()
V0=skin(state(x0));ids=[np.flatnonzero(LABEL==j) for j in range(5)];neighbors=META['topological_vertex_neighbors'];pool=set()
for j in range(5):
 for k in range(j+1,5):
  AA=V0[TR[ids[j]]];BB=V0[TR[ids[k]]];al=AA.min(1);ah=AA.max(1);bl=BB.min(1);bh=BB.max(1)
  for i,ta in enumerate(ids[j]):
   budget();delta=np.maximum(np.maximum(bl-ah[i],al[i]-bh),0)
   for bi in np.flatnonzero(np.sum(delta*delta,1)<=.005**2):
    tb=int(ids[k][bi])
    if tb in neighbors[int(ta)] or set(TR[ta])&set(TR[tb]):continue
    pool.add((int(ta),tb))
pairs=np.array(sorted(pool),dtype=int).reshape(-1,2);ds,wa,wb=distances(V0[TR[pairs[:,0]]],V0[TR[pairs[:,1]]]);assert np.all(ds>1e-10);axis=(wa-wb)/ds[:,None]
pieces=prepkey(angles,target,finger);planes=[np.c_[N,d] for note,N,d,lo,hi in pieces]
cache={};calls=0;jcalls=0;iters=0;history=[];best=[np.inf,x0.copy()]
def evaluate(x):
 global calls
 budget();key=x.tobytes()
 if key in cache:return cache[key]
 calls+=1;V=skin(state(x));TV=V[TR];tl=TV.min(1);th=TV.max(1);depths=[]
 for pi,(note,N,d,lo,hi) in enumerate(pieces):
  margin=.001 if note!=target else 1e-8
  ti=np.flatnonzero(np.all(th>=lo-margin,1)&np.all(tl<=hi+margin,1))
  if len(ti):
   sig=np.einsum('tvi,ni->tvn',TV[ti],N)-d;ti=ti[np.all(np.min(sig,axis=1)<=margin,axis=1)]
  if note!=target:peak=max([signed_triangle_depth(TV[t],planes[pi])[0] for t in ti]+[-1.]);depths.append(-.05-peak)
  else:peak=max([triangle_inside_depth(TV[t],planes[pi])[0] for t in ti]+[0.]);depths.append(.20-peak)
 ct=contact_metric(V,ek,angles[55],finger);g=ct['true_pulp_min_signed_gap_mm'];g=100. if g is None else g
 p=keylocal(V,ek,angles[55])[int(RAW['pad_indices'][2])]*1000
 gaps=(np.min(np.einsum('pvi,pi->pv',V[TR[pairs[:,0]]],axis),1)-np.max(np.einsum('pvi,pi->pv',V[TR[pairs[:,1]]],axis),1))*1000-.020
 aux=[-g-.005,g+.020,p[0]-surf['xmin']*1000-.01,surf['xmax']*1000-.01-p[0],p[1]-surf['ymin']*1000-.01,surf['ymax']*1000-.01-p[1],3-abs(p[2]-surf['z']*1000)]
 out=np.r_[aux,depths,gaps];viol=float(max(-out.min(),0.))
 if viol<best[0]:
  best[:]=[viol,x.copy()];history.append(dict(call=calls,elapsed_seconds=time.monotonic()-clockstart,max_violation_mm=viol,E5_signed_gap_mm=float(g),root_Z=float(x[2]),lambda_reference=float(x[10]),key_margin_mm=float(min(depths))))
 if len(cache)>50:cache.clear()
 cache[key]=out
 return out
def jac(x):
 global jcalls
 jcalls+=1;h=.001;cols=[]
 for j in range(len(x)):
  a=x.copy();b=x.copy();a[j]+=h;b[j]-=h;cols.append((evaluate(a)-evaluate(b))/(2*h))
 return np.array(cols).T
scale=np.r_[[15,15,10],[5,5,5],[10,10,10,10],1]
if ai==2:scale=np.r_[scale,1.]
def obj(x):return float(.5*np.sum(((x-x0)/scale)**2))
def grad(x):return (x-x0)/scale**2
def cb(x):
 global iters
 iters+=1;budget();print('ENDPOINT_ITERATION',ai,iters,round(time.monotonic()-clockstart,3),float(max(-evaluate(x).min(),0)),flush=True)
initial=evaluate(x0)
try:
 fit=minimize(obj,x0,jac=grad,method='SLSQP',bounds=list(zip(low,high)),constraints=[dict(type='ineq',fun=evaluate,jac=jac)],callback=cb,options=dict(maxiter=60,ftol=1e-7,disp=True))
 chosen=fit.x;conv=dict(success=bool(fit.success),status=int(fit.status),message=str(fit.message),nit=int(fit.nit),nfev=int(fit.nfev),njev=int(fit.njev))
except BudgetStop:chosen=best[1];conv=dict(success=False,status='WALL_BUDGET_STOP',message='140s per attempt / 600s cumulative fixed ceiling, no restart',nit=iters,nfev=None,njev=None)
final=evaluate(chosen) if time.monotonic()<deadline else None
out=dict(attempt=ai,authority='DESIGN_PROVISIONAL',source_time=2.956426,initialization='B2 normal family retargeted to E5' if ai==1 else 'approved R2 normal family retargeted to E5',initial_state=state(x0).tolist(),state=state(chosen).tolist(),x=chosen.tolist(),key_angles=angles.tolist(),lambda_reference=float(chosen[10]),bounds_lower=low.tolist(),bounds_upper=high.tolist(),reference_q_R1=Q0.tolist(),reference_q_R2=Q1.tolist(),convergence=conv,elapsed_seconds=time.monotonic()-clockstart,constraint_evaluations=calls,jacobian_evaluations=jcalls,history=history,initial_violation_mm=float(max(-initial.min(),0)),final_violation_mm=float(max(-final.min(),0)) if final is not None else best[0],self_active_pairs=len(pairs),source_B2_not_optimized=True,natural_family='approved spread + provisional old-S2 coordinated active flexion' if ai==2 else 'conservative approved R1/R2 coupled whole long finger reference; not a general active piano prior',active_flex_alpha=float(chosen[11]) if ai==2 else 0.,active_flex_anchor=ACTIVE_FLEX.tolist(),active_flex_reference_Human='NOT_SEPARATELY_REVIEWED; prior audit found hinge-only flexion, old S2 spread rejected',self_pool_not_global_equivalence=True,no_abnormal_joint_range_expansion=True,not_acceptance=True)
(O/f'ENDPOINT_SOLVE_{ai}.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8')
np.savez_compressed(O/f'ENDPOINT_POOL_{ai}.npz',pairs=pairs,axis=axis)
print('ENDPOINT_FINISHED',ai,out['elapsed_seconds'],conv,out['final_violation_mm'],flush=True)
