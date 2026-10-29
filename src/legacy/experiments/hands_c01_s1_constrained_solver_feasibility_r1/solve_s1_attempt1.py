import sys,json,time,ast
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent
sys.path.insert(0,str(O))
from skin_proxy import *
from triangle_distance import distances
from scipy.optimize import minimize
import scipy
OLD=O.parent/'hands_c01_g4_e5_skin_safe_bridge_r1'
P=json.loads((O/'POLICY_LOCK.json').read_text(encoding='utf-8-sig'))
TR=RAW['triangles']; LABEL=np.array(META['triangle_labels']);D=RAW;rot=c.axisrot
tree=ast.parse((O/'geometry_detector.py').read_text(encoding='utf-8-sig'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['clip','area','keylocal','keyworld','contact_metric']],type_ignores=[]),'frozen_contact_functions','exec'))
tree=ast.parse((O.parent/'hands_skin_collision_static_feasibility_r1/solve_static_skin.py').read_text(encoding='utf-8-sig'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='prepkey'],type_ignores=[]),'frozen_key_planes','exec'))
ai=int(sys.argv[-1]);assert ai in [1,2];assert not (O/f'SOLVE_{ai}.json').exists(),'No repeated solve'
prior=json.loads((OLD/f'REPAIR_ATTEMPT_{ai}.json').read_text(encoding='utf-8-sig'))
seed=np.array(prior['state']);angles=np.array(prior['key_angles']);safe=np.array(json.loads((OLD/'REPAIR_ATTEMPT_2.json').read_text(encoding='utf-8-sig'))['state'])
start=time.monotonic();deadline=start+240
if (O/'SOLVE_1.json').exists() and ai==2:deadline=min(deadline,start+600-json.loads((O/'SOLVE_1.json').read_text())['elapsed_seconds'])
class BudgetStop(Exception):pass
def budget():
 if time.monotonic()>deadline:raise BudgetStop()
VS=skin(safe);V0=skin(seed)
# All five digit combinations, original topology exclusions. Safe seed axes also resolve recorded crossings.
ids=[np.flatnonzero(LABEL==j) for j in range(5)]
neighbors=META['topological_vertex_neighbors'];pairset=set()
for j in range(5):
 for k in range(j+1,5):
  for V in [V0,VS]:
   A=V[TR[ids[j]]];B=V[TR[ids[k]]];alo=A.min(1);ahi=A.max(1);blo=B.min(1);bhi=B.max(1)
   for i,ta in enumerate(ids[j]):
    budget();delta=np.maximum(np.maximum(blo-ahi[i],alo[i]-bhi),0)
    near=np.flatnonzero(np.sum(delta*delta,1)<=.001**2)
    for bi in near:
     tb=int(ids[k][bi])
     if tb in neighbors[int(ta)] or set(TR[ta])&set(TR[tb]):continue
     pairset.add((int(ta),tb))
for pair in json.loads((OLD/'S1_REPAIR_1_ACTUAL_VALIDATION.json').read_text())['actual_geometry']['self_skin']:
 pairset.update(tuple(x) for x in pair['triangle_pair_ids'])
pairs=np.array(sorted(pairset),dtype=int)
dist,wa,wb=distances(VS[TR[pairs[:,0]]],VS[TR[pairs[:,1]]])
assert np.all(dist>1e-10),'Need reliable disjoint-seed separation axes'
axis=(wa-wb)/dist[:,None]
gap0=(np.min(np.einsum('pvi,pi->pv',VS[TR[pairs[:,0]]],axis),1)-np.max(np.einsum('pvi,pi->pv',VS[TR[pairs[:,1]]],axis),1))*1000
assert gap0.min()>-1e-7
# Whole triangle supporting-plane inequalities: sufficient condition for depth <= .20 mm on each included key piece.
pieces=prepkey(angles,67,1);kt=[];kn=[];kd=[];km=[];counts={}
TV=V0[TR];tlo=TV.min(1);thi=TV.max(1)
for pi,(note,N,d,lo,hi) in enumerate(pieces):
 budget();idx=np.flatnonzero(np.all(thi>=lo-.005,1)&np.all(tlo<=hi+.005,1))
 if not len(idx):continue
 signed=np.einsum('tvi,ni->tvn',TV[idx],N)-d
 choice=np.argmax(np.min(signed,axis=1),axis=1)
 kt.extend(idx);kn.extend(N[choice]);kd.extend(d[choice]);km.extend([note]*len(idx));counts[str(note)]=counts.get(str(note),0)+len(idx)
kt=np.array(kt);kn=np.array(kn);kd=np.array(kd)
staticB=json.loads((ROOT/'audits/piano_hand_static_posture_clearance_refinement_r2/STATIC_REFINEMENT_POLICY_R2.json').read_text(encoding='utf-8-sig'))['joint_increment_bounds_deg']
B=np.array([staticB['THUMB' if j==0 else 'LONG'] for j in range(5)])
low=np.r_[[-150,-30],[-8,-8,-12],B[:,0].ravel()];high=np.r_[[60,35],[8,8,12],B[:,1].ravel()]
x0=np.r_[seed[:2],seed[3:]]
local=np.r_[[1.,1.],[2.,2.,2.],np.full(20,3.)]
low=np.maximum(low,x0-local);high=np.minimum(high,x0+local)
def state(x):return np.r_[x[:2],seed[2],x[2:]]
cache={};calls=0;history=[];best=[np.inf,x0.copy()];iterations=0;jac_calls=0
def evaluate(x):
 global calls
 budget();key=x.tobytes()
 if key in cache:return cache[key]
 calls+=1;V=skin(state(x));ct=contact_metric(V,c.KEYS[46],angles[46],1)
 g=ct['true_pulp_min_signed_gap_mm']
 if g is None:raise RuntimeError('Missing clipped complete-pulp footprint')
 p=keylocal(V,c.KEYS[46],angles[46])[int(RAW['pad_indices'][0])]*1000
 ek=c.KEYS[55];ep=keylocal(V,ek,angles[55])[int(RAW['pad_indices'][2])]*1000
 s=c.KEYS[46]['key_top_playable_surface'][0];e=ek['key_top_playable_surface'][0]
 keygap=np.min(np.einsum('tvi,ti->tv',V[TR[kt]],kn)-kd[:,None],axis=1)*1000+.20
 selfgap=(np.min(np.einsum('pvi,pi->pv',V[TR[pairs[:,0]]],axis),1)-np.max(np.einsum('pvi,pi->pv',V[TR[pairs[:,1]]],axis),1))*1000-.020
 # Contact requires small negative minimum, with positive height on the patch. Independent oracle confirms actual crossing.
 patch=set(META['pad_patches'][0]);pt=[ti for ti in ids[0] if all(int(v) in patch for v in TR[ti])]
 maxgap=float(np.max(keylocal(V[TR[pt].ravel()],c.KEYS[46],angles[46])[:,2]-s['z'])*1000)
 aux=np.array([-g-.005,g+.020,maxgap-.10,p[0]-s['xmin']*1000-.01,s['xmax']*1000-.01-p[0],p[1]-s['ymin']*1000-.01,s['ymax']*1000-.01-p[1],3.-abs(p[2]-s['z']*1000),
 ep[0]-e['xmin']*1000+2,e['xmax']*1000+2-ep[0],ep[1]-e['ymin']*1000+2,e['ymax']*1000+2-ep[1],ep[2]-e['z']*1000-4,20-(ep[2]-e['z']*1000)])
 # Vertex displacement bound makes discarded key-AABB constraints conservative (5mm pool, <=4mm move).
 displacement=np.linalg.norm(V-V0,axis=1)*1000
 out=np.r_[aux,keygap,selfgap,4-displacement]
 v=float(max(-out.min(),0.))
 if v<best[0]:
  best[:]=[v,x.copy()];history.append(dict(evaluation=calls,elapsed_seconds=time.monotonic()-start,max_constraint_violation_mm=v,contact_signed_gap_mm=float(g),minimum_self_axis_gap_mm=float(selfgap.min()+.020),minimum_key_plane_margin_mm=float(keygap.min())))
 if len(cache)>80:cache.clear()
 cache[key]=out
 return out
# Central finite differences of the vector-valued constraint. Shared V/FK per column, no separate geometry per scalar.
def jacobian(x,h=.001):
 global jac_calls
 jac_calls+=1;cols=[]
 for j in range(len(x)):
  xp=x.copy();xm=x.copy();xp[j]+=h;xm[j]-=h
  cols.append((evaluate(xp)-evaluate(xm))/(2*h))
 return np.array(cols).T
def objective(x):return float(.5*np.sum((x-x0)**2))
def objjac(x):return x-x0
def callback(x):
 global iterations
 iterations+=1;budget()
 print('ITERATION',iterations,'elapsed',round(time.monotonic()-start,3),'violation',float(max(-evaluate(x).min(),0.)),flush=True)
setup=time.monotonic()-start
initial=evaluate(x0)
J1=jacobian(x0);J2=jacobian(x0,.0005)
derivative=dict(central_step_mm_or_deg=.001,half_step=.0005,max_absolute_difference=float(np.max(abs(J1-J2))),relative_frobenius_difference=float(np.linalg.norm(J1-J2)/max(np.linalg.norm(J2),1e-12)),note='Includes active min/max/clip and displacement norm nondifferentiability; diagnostic, not proof of smoothness')
try:
 result=minimize(objective,x0,jac=objjac,method='SLSQP',bounds=list(zip(low,high)),constraints=[dict(type='ineq',fun=evaluate,jac=jacobian)],callback=callback,options=dict(maxiter=60,ftol=1e-8,disp=True))
 chosen=result.x;conv=dict(success=bool(result.success),status=int(result.status),message=str(result.message),nit=int(result.nit),nfev=int(result.nfev),njev=int(result.njev))
except BudgetStop:
 chosen=best[1];conv=dict(success=False,status='WALL_BUDGET_STOP',message='Fixed 240s per-solve / 600s cumulative ceiling; best evaluated violation retained',nit=iterations,nfev=None,njev=None)
elapsed=time.monotonic()-start
# Do not correct state after solver termination.
cache.clear()
final=evaluate(chosen) if elapsed<deadline-start else None
st=state(chosen)
out=dict(attempt=ai,method='SLSQP',authority='DESIGN_PROVISIONAL',initialization=f'PREVIOUS_REPAIR_{ai}',initial_state=seed.tolist(),state=st.tolist(),root_Z_fixed_mm=float(seed[2]),key_angles=angles.tolist(),source_time=prior['source_time'],elapsed_seconds=time.monotonic()-start,setup_seconds=setup,constraint_evaluations=calls,constraint_jacobian_evaluations=jac_calls,convergence=conv,initial_max_violation_mm=float(max(-initial.min(),0.)),final_max_violation_mm=float(max(-final.min(),0.)) if final is not None else best[0],derivative_probe=derivative,history=history,active_self_pairs=len(pairs),key_triangle_plane_constraints=len(kt),key_constraint_counts=counts,inequality_count=len(initial),bounds_lower=low.tolist(),bounds_upper=high.tolist(),local_bound_radius=local.tolist(),self_candidate_AABB_radius_mm=1.,self_pool_global_equivalence=False,actual_blender_acceptance_required=True,scipy_version=scipy.__version__,no_root_z_ablation=True)
(O/f'SOLVE_{ai}.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8')
np.savez_compressed(O/f'CONSTRAINT_POOL_{ai}.npz',self_pairs=pairs,separation_axes=axis,key_triangle_ids=kt,key_normals=kn,key_offsets=kd,key_midi=np.array(km))
print('SOLVE_FINISHED',ai,out['elapsed_seconds'],conv,'violation',out['final_max_violation_mm'],flush=True)
