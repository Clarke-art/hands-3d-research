import sys,json,time,ast,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O))
from skin_proxy import *
from triangle_distance import distances
from scipy.optimize import minimize
from itertools import combinations
PRE=O.parent/'hands_c01_s1_constrained_solver_feasibility_r1';P=json.loads((O/'ANATOMY_CONSTRAINT_PROPOSAL.json').read_text(encoding='utf-8-sig'))
TR=RAW['triangles'];LABEL=np.array(META['triangle_labels']);D=RAW;rot=c.axisrot
tree=ast.parse((O/'geometry_detector.py').read_text(encoding='utf-8-sig'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['clip','area','keylocal','keyworld','contact_metric','triangle_inside_depth']],type_ignores=[]),'original_geometry_functions','exec'))
tree=ast.parse((O.parent/'hands_skin_collision_static_feasibility_r1/solve_static_skin.py').read_text(encoding='utf-8-sig'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='prepkey'],type_ignores=[]),'original_key_planes','exec'))
ai=int(sys.argv[-1]);assert ai in [1,2];assert not (O/f'B_SOLVE_{ai}.json').exists()
A=json.loads((PRE/'SOLVE_2.json').read_text());astate=np.array(A['state']);angles=np.array(A['key_angles'])
Q0=np.array([r['approved_reference_controls_deg'][0] for r in P['constraints']]);Q1=np.array([r['approved_reference_controls_deg'][1] for r in P['constraints']])
seed=astate.copy();seed[10:]=Q0[1:].ravel()
if ai==2:
 assert json.loads((O/'B_ACTUAL_1.json').read_text())['status']!='REFERENCE_STATIC_GATES_PASS'
 seed[6:]=Q0.ravel();seed[:2]=0.;seed[3:6]=0.;v=skin(seed);seed[0]=(c.KEYS[46]['key_center'][0]-v[int(RAW['pad_indices'][0])][0])*1000
start=time.monotonic();already=json.loads((O/'B_SOLVE_1.json').read_text())['elapsed_seconds'] if ai==2 else 0.;deadline=start+min(140,300-already)
class BudgetStop(Exception):pass
def budget():
 if time.monotonic()>deadline:raise BudgetStop()
def state(x):
 st=astate.copy();st[:2]=x[:2];st[3:6]=x[2:5];st[6:10]=x[5:9];st[10:]=((1-x[9])*Q0[1:]+x[9]*Q1[1:]).ravel()
 return st
x0=np.r_[seed[:2],seed[3:6],seed[6:10],0.]
low=np.r_[np.maximum([-150,-30],astate[:2]-15),[-8,-8,-12],[0,0,0,-35],0.]
high=np.r_[np.minimum([60,35],astate[:2]+15),[8,8,12],[25,25,18,35],1.]
x0=np.clip(x0,low+1e-9,high-1e-9);V0=skin(state(x0))
ids=[np.flatnonzero(LABEL==j) for j in range(5)];neighbors=META['topological_vertex_neighbors'];pool=set()
for j in range(5):
 for k in range(j+1,5):
  AA=V0[TR[ids[j]]];BB=V0[TR[ids[k]]];alo=AA.min(1);ahi=AA.max(1);blo=BB.min(1);bhi=BB.max(1)
  for i,ta in enumerate(ids[j]):
   budget();d=np.maximum(np.maximum(blo-ahi[i],alo[i]-bhi),0)
   for bi in np.flatnonzero(np.sum(d*d,1)<=.005**2):
    tb=int(ids[k][bi])
    if tb in neighbors[int(ta)] or set(TR[ta])&set(TR[tb]):continue
    pool.add((int(ta),tb))
pairs=np.array(sorted(pool),dtype=int).reshape(-1,2)
ds,wa,wb=distances(V0[TR[pairs[:,0]]],V0[TR[pairs[:,1]]])
assert np.all(ds>1e-10),'No reliable reference-seed axis'
axis=(wa-wb)/ds[:,None];pieces=prepkey(angles,67,1)
# Exact, dynamically filtered triangle-interior maximum for each of all 88-key convex pieces.
fullplanes=[np.c_[N,dd] for note,N,dd,lo,hi in pieces]
cache={};calls=0;jcalls=0;iters=0;history=[];best=[np.inf,x0.copy()];last=np.full(1,-np.inf)
def evaluate(x):
 global calls,last
 budget();key=x.tobytes()
 if key in cache:return cache[key]
 calls+=1;st=state(x);V=skin(st);TV=V[TR];tl=TV.min(1);th=TV.max(1)
 depths=[]
 for pi,(note,N,dd,lo,hi) in enumerate(pieces):
  candidates=np.flatnonzero(np.all(th>=lo-1e-8,1)&np.all(tl<=hi+1e-8,1))
  if len(candidates):
   sig=np.einsum('tvi,ni->tvn',TV[candidates],N)-dd
   candidates=candidates[np.all(np.min(sig,axis=1)<=1e-8,axis=1)]
  peak=max([triangle_inside_depth(TV[ti],fullplanes[pi])[0] for ti in candidates]+[0.])
  depths.append(.20-peak)
 ct=contact_metric(V,c.KEYS[46],angles[46],1);g=ct['true_pulp_min_signed_gap_mm'];g=100. if g is None else g
 s=c.KEYS[46]['key_top_playable_surface'][0];pad=keylocal(V,c.KEYS[46],angles[46])[int(RAW['pad_indices'][0])]*1000
 middle=keylocal(V,c.KEYS[55],angles[55])[int(RAW['pad_indices'][2])]*1000;e=c.KEYS[55]['key_top_playable_surface'][0]
 gap=(np.min(np.einsum('pvi,pi->pv',V[TR[pairs[:,0]]],axis),1)-np.max(np.einsum('pvi,pi->pv',V[TR[pairs[:,1]]],axis),1))*1000-.020
 aux=[-g-.005,g+.020,pad[0]-s['xmin']*1000-.01,s['xmax']*1000-.01-pad[0],pad[1]-s['ymin']*1000-.01,s['ymax']*1000-.01-pad[1],3-abs(pad[2]-s['z']*1000),middle[2]-e['z']*1000-4]
 out=np.r_[aux,depths,gap];vi=float(max(-out.min(),0.))
 if vi<best[0]:
  best[:]=[vi,x.copy()];history.append(dict(call=calls,elapsed_seconds=time.monotonic()-start,max_violation_mm=vi,contact_signed_gap_mm=float(g),key_constraint_min_mm=float(min(depths)),self_axis_min_mm=float(gap.min()+.020) if len(gap) else None,lambda_reference=float(x[9])))
 if len(cache)>45:cache.clear()
 cache[key]=out;last=out
 return out
def jac(x):
 global jcalls
 jcalls+=1;h=.001;columns=[]
 for j in range(len(x)):
  xp=x.copy();xm=x.copy();xp[j]+=h;xm[j]-=h;columns.append((evaluate(xp)-evaluate(xm))/(2*h))
 return np.array(columns).T
scale=np.r_[[10,10],[5,5,5],[10,10,10,10],1]
# Preference only secondary; anatomy family is structural equality.
def obj(x):return float(.5*np.sum(((x-x0)/scale)**2))
def grad(x):return (x-x0)/scale**2
def callback(x):
 global iters
 iters+=1;budget();print('B_ITERATION',ai,iters,round(time.monotonic()-start,3),'violation',float(max(-evaluate(x).min(),0)),flush=True)
initial=evaluate(x0)
try:
 fit=minimize(obj,x0,jac=grad,method='SLSQP',bounds=list(zip(low,high)),constraints=[dict(type='ineq',fun=evaluate,jac=jac)],callback=callback,options=dict(maxiter=60,ftol=1e-7,disp=True))
 chosen=fit.x;conv=dict(success=bool(fit.success),status=int(fit.status),message=str(fit.message),nit=int(fit.nit),nfev=int(fit.nfev),njev=int(fit.njev))
except BudgetStop:
 chosen=best[1];conv=dict(success=False,status='WALL_BUDGET_STOP',message='Precommitted 140s per run / 300s total exceeded; no restart',nit=iters,nfev=None,njev=None)
elapsed=time.monotonic()-start;st=state(chosen);final=evaluate(chosen) if time.monotonic()<deadline else None
result=dict(attempt=ai,authority='DESIGN_PROVISIONAL',test='S1 natural reference family + stage-specific early preparation',state=st.tolist(),key_angles=angles.tolist(),source_time=A['source_time'],original_A_state=astate.tolist(),initial_state=state(x0).tolist(),x=chosen.tolist(),lambda_reference=float(chosen[9]),bounds_lower=low.tolist(),bounds_upper=high.tolist(),elapsed_seconds=time.monotonic()-start,convergence=conv,constraint_evaluations=calls,jacobian_evaluations=jcalls,initial_constraint_violation_mm=float(max(-initial.min(),0)),final_constraint_violation_mm=float(max(-final.min(),0)) if final is not None else best[0],history=history,reference_q_R1=Q0.tolist(),reference_q_R2=Q1.tolist(),root_Z_fixed_mm=float(astate[2]),self_active_pairs=len(pairs),self_candidate_AABB_radius_mm=5.,self_pool_global_equivalence=False,key_all_piece_count=len(pieces),key_exact_dynamic_AABB_filter=True,E5_exact_horizontal_and_upper_height_NOT_required_at_S1=True,Human_naturalness='PENDING',proposal_sha256=hashlib.sha256((O/'ANATOMY_CONSTRAINT_PROPOSAL.json').read_bytes()).hexdigest(),not_acceptance=True)
(O/f'B_SOLVE_{ai}.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
np.savez_compressed(O/f'B_POOL_{ai}.npz',pairs=pairs,axis=axis)
print('B_SOLVE_FINISHED',ai,result['elapsed_seconds'],conv,'violation',result['final_constraint_violation_mm'],flush=True)

